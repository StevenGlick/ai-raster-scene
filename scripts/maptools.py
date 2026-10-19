"""Helpers for authoring ai-raster-scene scenes in Python instead of typing map strings by hand.

    from maptools import Grid, scene
    g = Grid(30, 20, fill=',')          # 30 wide, 20 tall, all grass
    g.rect(4, 2, 19, 7, 'H')            # solid building block (inclusive corners)
    g.box(0, 0, 29, 19, 'w')            # hollow perimeter wall
    g.line(11, 8, 11, 18, 'c', width=2) # path
    g.disc(12, 14, 3, 'c')              # round plaza
    g.put(11, 7, 'E')                   # single cell
    s = scene(g, legend={...}, camera={...}, lights=[...], sprites=[...], sky='night')
    s.save('my_scene.json')
"""
import json


class Grid:
    def __init__(self, w, h, fill='.'):
        self.w, self.h = w, h
        self.g = [[fill] * w for _ in range(h)]

    def _ok(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def put(self, x, y, c):
        if self._ok(x, y):
            self.g[y][x] = c
        return self

    def get(self, x, y):
        return self.g[y][x] if self._ok(x, y) else None

    def rect(self, x0, y0, x1, y1, c):
        """Filled rectangle, corners inclusive."""
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                self.put(x, y, c)
        return self

    def box(self, x0, y0, x1, y1, c):
        """Hollow rectangle outline (room walls), corners inclusive."""
        for x in range(x0, x1 + 1):
            self.put(x, y0, c); self.put(x, y1, c)
        for y in range(y0, y1 + 1):
            self.put(x0, y, c); self.put(x1, y, c)
        return self

    def room(self, x0, y0, x1, y1, wall, floor, doors=()):
        """Walled room with interior floor; doors is a list of (x, y) cells to open (or (x, y, char))."""
        self.rect(x0, y0, x1, y1, floor)
        self.box(x0, y0, x1, y1, wall)
        for d in doors:
            self.put(d[0], d[1], d[2] if len(d) > 2 else floor)
        return self

    def line(self, x0, y0, x1, y1, c, width=1):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            for k in range(width):
                if abs(x1 - x0) >= abs(y1 - y0):
                    self.put(x, y + k, c)
                else:
                    self.put(x + k, y, c)
        return self

    def disc(self, cx, cy, r, c):
        for y in range(int(cy - r - 1), int(cy + r + 2)):
            for x in range(int(cx - r - 1), int(cx + r + 2)):
                if (x + 0.5 - cx - 0.5) ** 2 + (y + 0.5 - cy - 0.5) ** 2 <= r * r:
                    self.put(x, y, c)
        return self

    def replace(self, old, new, x0=0, y0=0, x1=None, y1=None):
        x1 = self.w - 1 if x1 is None else x1
        y1 = self.h - 1 if y1 is None else y1
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if self.g[y][x] == old:
                    self.g[y][x] = new
        return self

    def rows(self):
        return [''.join(r) for r in self.g]

    def __str__(self):
        return '\n'.join(self.rows())


class Scene(dict):
    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self, f, indent=1)
        return path


def scene(grid, legend, camera, **kw):
    s = Scene(resolution=[320, 200], scale=3, map=grid.rows(), legend=legend, camera=camera)
    s.update(kw)
    return s

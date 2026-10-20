#!/usr/bin/env python3
"""ai-raster-scene renderer: 90s-style first-person views from a JSON scene file.

A 2.5D grid raycaster in the Wolfenstein/Doom lineage with:
  - textured walls of any height (tall buildings seen over short walls, multi-hit rays)
  - textured floors and ceilings per cell, open-sky cells with a panorama sky
  - billboard sprites with per-pixel depth testing
  - coloured point lights baked into a shadowed lightmap, ambient light, light banding
  - emissive texels (lit windows, lamps, glowing runes), a player flashlight
  - distance fog, 256-colour palette quantisation with ordered (Bayer) dithering

Usage:
  python render.py scene.json -o out.png            # render the camera (or every shot)
  python render.py scene.json -o out.png --map      # also write a top-down layout check
  python render.py scene.json -o out.png --sheet    # tile all shots into one contact sheet
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assets  # noqa: E402
import gui  # noqa: E402
import icons  # noqa: E402
import post  # noqa: E402
import prefabs  # noqa: E402
import buildings  # noqa: E402

T = assets.T


# ------------------------------------------------------------------ cameras

def find_sprite(scene, sid, cam=None):
    """The sprite with this `id`, from the scene (its prefabs included) or the shot's extra_sprites."""
    scene = prefabs.expand(scene)
    for sp in list(scene.get('sprites', [])) + list((cam or {}).get('extra_sprites', [])):
        if sp.get('id') == sid:
            return sp
    return None


# How far the edge of solid ground drops into a void floor before the sky shows beneath it.
VOID_DEPTH = 2.5


def resolve_camera(scene, cam):
    """Fill in `angle` from a camera's `look_at` (a sprite id, [x, y] or [x, y, z]).

    Aiming by hand means working out atan2 in your head, which is easy to get wrong by tens of
    degrees. An [x, y, z] target also sets `pitch` so that height sits mid-frame.
    """
    tgt = cam.get('look_at')
    if tgt is None or 'x' not in cam or 'y' not in cam:
        return cam
    cam = dict(cam)
    if isinstance(tgt, str):
        sp = find_sprite(scene, tgt, cam)
        if sp is None:
            raise KeyError(f"look_at names sprite id {tgt!r}, but no sprite has that id")
        tx, ty, tz = float(sp['x']), float(sp['y']), None
    else:
        tx, ty = float(tgt[0]), float(tgt[1])
        tz = float(tgt[2]) if len(tgt) > 2 else None
    vx, vy = tx - float(cam['x']), ty - float(cam['y'])
    dist = math.hypot(vx, vy)
    if dist < 1e-6:
        return cam
    cam['angle'] = math.degrees(math.atan2(vy, vx)) % 360
    if tz is not None:
        W, H = scene.get('resolution', [320, 200])
        fov = math.radians(float(cam.get('fov', 66)))
        cam['pitch'] = (tz - float(cam.get('height', 0.5))) * (W / 2) / (math.tan(fov / 2) * dist * H)
    return cam


def merge_camera(scene, shot):
    """A shot over the scene camera, with look_at resolved. A shot that sets its own `angle`
    (and no look_at) is aimed by that angle, not by a look_at inherited from the camera."""
    base = dict(scene.get('camera') or {})
    if 'angle' in shot and 'look_at' not in shot:
        base.pop('look_at', None)
    return resolve_camera(scene, {**base, **shot})


def _seg_dist(px, py, x0, y0, x1, y1):
    vx, vy = x1 - x0, y1 - y0
    L = vx * vx + vy * vy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - x0) * vx + (py - y0) * vy) / L))
    return math.hypot(px - (x0 + t * vx), py - (y0 + t * vy))


# ------------------------------------------------------------------ scene loading

class World:
    def __init__(self, scene):
        scene = prefabs.expand(scene)       # prefabs become ordinary cells, sprites, lights and decals
        self.scene = scene
        rows = scene['map']
        self.mh = len(rows)
        self.mw = max(len(r) for r in rows)
        legend = scene['legend']
        default = scene.get('default', {'floor': 'concrete_floor'})
        self.ceil_h = float(scene.get('ceiling_height', 1.0))

        self.height = np.zeros((self.mh, self.mw), np.float32)
        self.wall_tid = np.full((self.mh, self.mw), -1, np.int32)
        self.floor_tid = np.full((self.mh, self.mw), -1, np.int32)
        self.ceil_tid = np.full((self.mh, self.mw), -1, np.int32)
        self.drop = np.zeros((self.mh, self.mw), np.float32)  # how far this floor sits below z=0
        self.reflect = np.zeros((self.mh, self.mw), np.float32)  # how mirror-like each floor is
        self.void = np.zeros((self.mh, self.mw), bool)           # no ground: the sky shows below
        self.glazed = np.zeros((self.mh, self.mw), bool)         # a roof the sun shines through
        self.side_tid = np.full((self.mh, self.mw), -1, np.int32)  # texture of a cell's sunken edge
        self.tex = []
        self.tex_key = []    # the material name each texture id came from
        self.tex_noise = []  # its relative surface-noise multiplier
        self.tex_alpha = []  # see-through mask (or None) per texture id
        self._tidx = {}
        self.see = np.zeros((self.mh, self.mw), bool)  # walls with see-through texels: fences, bars
        inherit = []
        self.stacks = {}  # (y, x) -> texture ids per storey, bottom to top
        self._fringes = {}  # (y, x) -> the fringe spec of a wall cell that has one
        self._facades = {}  # (y, x) -> the facade spec of a wall cell that has one

        for y, row in enumerate(rows):
            row = row.ljust(self.mw)
            for x, ch in enumerate(row):
                spec = legend.get(ch, default)
                if 'wall' in spec:
                    self.height[y, x] = float(spec.get('h', 1.0))
                    stack = spec['wall'] if isinstance(spec['wall'], list) else [spec['wall']]
                    tids = [self.tid(t) for t in stack]
                    self.wall_tid[y, x] = tids[0]
                    if spec.get('side'):
                        self.side_tid[y, x] = self.tid(spec['side'])
                    if len(tids) > 1:
                        self.stacks[(y, x)] = tids
                    if spec.get('fringe'):
                        self._fringes[(y, x)] = spec['fringe']
                    if spec.get('facade'):
                        self._facades[(y, x)] = spec['facade']
                    if any(self.tex_alpha[t] is not None for t in tids):
                        # a fence or grille: the ground (and any roof) carries on underneath it
                        self.see[y, x] = True
                        if spec.get('floor'):
                            self.floor_tid[y, x] = self.tid(spec['floor'])
                        if spec.get('ceil'):
                            self.ceil_tid[y, x] = self.tid(spec['ceil'])
                        inherit.append((y, x, not spec.get('floor'), not spec.get('ceil')))
                    else:
                        self.floor_tid[y, x] = self.tid(spec.get('top', stack[-1]))
                        if spec.get('ceil'):  # an altar or a step under a roof: the roof is above it
                            self.ceil_tid[y, x] = self.tid(spec['ceil'])
                else:
                    floor = spec.get('floor', default.get('floor', 'concrete_floor'))
                    if spec.get('ceil'):
                        self.ceil_tid[y, x] = self.tid(spec['ceil'])
                        self.glazed[y, x] = bool(spec.get('glazed', False))
                    if spec.get('side'):
                        self.side_tid[y, x] = self.tid(spec['side'])
                    if floor == 'void':
                        # no ground at all: the sky carries on below the horizon, and the edge of
                        # the ground beside it drops VOID_DEPTH into it like a cliff
                        self.void[y, x] = True
                        self.drop[y, x] = VOID_DEPTH
                        continue
                    self.floor_tid[y, x] = self.tid(floor)
                    self.drop[y, x] = min(0.9, max(0.0, float(spec.get('drop', 0.0))))
                    self.reflect[y, x] = min(1.0, max(0.0, float(spec.get('reflect', assets.texture_reflect(floor)))))

        self._apply_heights(scene)
        for y, x, want_floor, want_ceil in inherit:
            self._inherit_surfaces(y, x, want_floor, want_ceil, default)
        self._roof_low_blocks()
        # rain-soaked: open ground under the sky darkens and turns mirror-like (roofed and void
        # cells stay dry)
        wet = min(1.0, max(0.0, float(scene.get('wet', 0) or 0)))
        outside = (self.height <= 0) & (self.ceil_tid < 0) & ~self.void
        self.wet = np.where(outside, wet, 0.0).astype(np.float32)
        self.reflect = np.clip(self.reflect + self.wet * 0.35, 0, 1).astype(np.float32)
        # what blocks light and hides what is behind it: see-through cells do neither
        self.solid_h = np.where(self.see, 0.0, self.height).astype(np.float32)

        self.floor_decals, self.ceil_decals, self.wall_decals = [], [], {}
        self.fringe_sprites = self._fringe(scene)
        self.fringe_sprites += self._facade(scene)
        grime = self._expand_scatter(scene)
        # contact shadows go first, so puddles, stains and the author's own decals sit on top
        self._load_decals(scene, self._contact_shadows(scene) + list(scene.get('decals', [])) + grime)

    def _apply_heights(self, scene):
        """`heights`: a digit layer over the map setting each wall cell's height in steps of
        `height_unit` (0.1 by default), so a flight of stairs is one string per row."""
        rows = scene.get('heights')
        if not rows:
            return
        unit = float(scene.get('height_unit', 0.1))
        for y, row in enumerate(rows[:self.mh]):
            for x, ch in enumerate(str(row)[:self.mw]):
                if ch in '123456789' and self.height[y, x] > 0:
                    self.height[y, x] = int(ch) * unit

    def _inherit_surfaces(self, y, x, want_floor, want_ceil, default):
        """A see-through cell borrows the floor (and roof) most common among its open neighbours,
        so a fence across a lawn stands on grass without the legend having to say so."""
        from collections import Counter
        floors, ceils = Counter(), Counter()
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.mh and 0 <= nx < self.mw and self.height[ny, nx] <= 0 and not self.void[ny, nx]:
                floors[int(self.floor_tid[ny, nx])] += 1
                ceils[int(self.ceil_tid[ny, nx])] += 1
        if want_floor:
            self.floor_tid[y, x] = (floors.most_common(1)[0][0] if floors
                                    else self.tid(default.get('floor', 'concrete_floor')))
        if want_ceil and ceils:
            self.ceil_tid[y, x] = ceils.most_common(1)[0][0]

    def _roof_low_blocks(self):
        """A block lower than the ceiling leaves the ceiling above it in view, so give it the roof
        of the room around it - spreading inward across a wide platform - or open sky outdoors."""
        from collections import Counter
        low = (self.height > 0) & (self.height < self.ceil_h - 1e-6) & ~self.see
        need = low & (self.ceil_tid < 0)
        for _ in range(self.mw + self.mh):
            changed = False
            for y, x in zip(*np.nonzero(need)):
                votes = Counter()
                for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    ny, nx = y + dy, x + dx
                    if (0 <= ny < self.mh and 0 <= nx < self.mw and not need[ny, nx]
                            and (self.height[ny, nx] <= 0 or low[ny, nx])):
                        votes[int(self.ceil_tid[ny, nx])] += 1
                if votes:
                    self.ceil_tid[y, x] = votes.most_common(1)[0][0]
                    need[y, x] = False
                    changed = True
            if not changed:
                break

    def base_z(self, x, y):
        """Height of the surface a sprite standing at (x, y) rests on: below z=0 in a sunken
        cell, on top of a block lower than a room wall, otherwise the floor."""
        cx, cy = int(math.floor(x)), int(math.floor(y))
        if not (0 <= cy < self.mh and 0 <= cx < self.mw):
            return 0.0
        h = float(self.height[cy, cx])
        if h > 0:
            return h if h < 0.95 and not self.see[cy, cx] else 0.0
        if self.void[cy, cx]:
            return 0.0   # nothing to stand on: `z` is simply the height (a whale in the sky)
        return -float(self.drop[cy, cx])

    def _load_decals(self, scene, decals):
        """Decals are stamps blended into a surface's albedo: puddles, stains, vines, cracks."""
        defs = scene.get('decal_defs', {})
        for d in decals:
            rgba, em = assets.get_decal(d['tex'], defs)
            if d.get('flip'):
                rgba, em = rgba[:, ::-1], em[:, ::-1]
            dh, dw = rgba.shape[:2]
            e = {'rgba': rgba, 'em': em, 'dw': dw, 'dh': dh,
                 'size': float(d.get('size', 1.0)),
                 'opacity': float(d.get('opacity', 1.0)),
                 'reflect': float(d.get('reflect', assets.DECAL_REFLECT.get(d['tex'], 0.0))),
                 'tint': np.array(d.get('tint', [1, 1, 1]), np.float32)}
            surf = d.get('surface', 'floor')
            if surf in ('floor', 'ceil', 'ceiling'):
                e['x'], e['y'] = float(d['x']), float(d['y'])
                cx, cy = int(math.floor(e['x'])), int(math.floor(e['y']))
                e['drop'] = float(self.drop[cy, cx]) if 0 <= cy < self.mh and 0 <= cx < self.mw else 0.0
                (self.floor_decals if surf == 'floor' else self.ceil_decals).append(e)
            else:
                cx, cy = (int(v) for v in d['cell'])
                e['u'] = float(d.get('u', 0.5))
                e['z'] = float(d.get('z', 0.5))
                self.wall_decals.setdefault((cy, cx, d.get('face', 'south')), []).append(e)

    # ---------------------------------------------------------------- scatter and grime

    def _grime(self, scene):
        """`grime` 0..1 is one dial for how neglected somewhere is.

        It turns up surface variation, multiplies scatter density, and stamps wear decals on
        walls and floors, so a dirty room needs one number rather than three sets of tuning.
        """
        g = scene.get('grime', 0)
        g = float(g.get('amount', 0)) if isinstance(g, dict) else float(g)
        return max(0.0, min(1.0, g))

    def _ground_open(self, x, y):
        """Open ground for fringes and facades: inside the map, and no wall a person could not
        step over (a kerb or a low step still counts as ground)."""
        return (0 <= x < self.mw and 0 <= y < self.mh and self.height[y, x] < 0.5
                and not self.void[y, x])

    def _face_runs(self, cells):
        """Straight runs of wall faces that look onto open ground, from cells {(y, x): spec}:
        each (spec, d, line, a, b) with d the way out ('n', 's', 'w' or 'e'), `line` the row
        (or column) of the walls and a..b the cells along it. Cells whose specs differ make
        separate runs."""
        groups = {}
        for (y, x), spec in cells.items():
            key = json.dumps({'set': spec} if isinstance(spec, str) else spec, sort_keys=True)
            for d, ox, oy in (('n', 0, -1), ('s', 0, 1), ('w', -1, 0), ('e', 1, 0)):
                if self._ground_open(x + ox, y + oy):
                    groups.setdefault((key, d, y if d in 'ns' else x), []).append(x if d in 'ns' else y)
        out = []
        for (key, d, line), poss in sorted(groups.items()):
            poss = sorted(set(poss))
            start = poss[0]
            for p, q in zip(poss, poss[1:] + [None]):
                if q != p + 1:
                    out.append((json.loads(key), d, line, start, p))
                    start = q
        return out

    def _run_ends(self, d, line, a, b, off):
        """Where a layer `off` out from a run of faces starts and ends along it, and what is at
        each end: it wraps round an outside corner, stops short in an inside one, and carries on
        off the edge of the map."""
        o = 1 if d in 'se' else -1
        lo, hi, kinds = float(a), float(b + 1), []
        for end, step in ((a - 1, -1), (b + 1, 1)):
            nx, ny = (end, line) if d in 'ns' else (line, end)
            dx_, dy_ = (end, line + o) if d in 'ns' else (line + o, end)
            if not (0 <= nx < self.mw and 0 <= ny < self.mh):
                adj, kind = 0.0, 'edge'
            elif self._ground_open(nx, ny):
                adj, kind = off, 'convex'
            elif not self._ground_open(dx_, dy_):
                adj, kind = -off, 'concave'
            else:
                adj, kind = 0.0, 'straight'
            if step < 0:
                lo -= adj
            else:
                hi += adj
            kinds.append(kind)
        return lo, hi, kinds[0], kinds[1]

    def _card(self, d, line, lo, hi, off, **fields):
        """A planar sprite lying along a run of faces, `off` out from them, from lo to hi."""
        o = 1 if d in 'se' else -1
        face = line + (1 if o > 0 else 0)
        mid, across = (lo + hi) / 2, face + o * off
        sp = {'x': mid if d in 'ns' else across, 'y': across if d in 'ns' else mid,
              'angle': 0.0 if d in 'ns' else 90.0, 'planes': 1, 'length': hi - lo, 'shadow': False}
        sp.update(fields)
        return sp

    def _cam_spots(self, scene):
        return [(cx, cy) for cx, cy, r in self._keep_clear(scene) if r == 1.0]

    def _fringe(self, scene):
        """Layered foliage cards standing in front of every face of a `fringe` wall that looks
        onto open ground.

        Each straight run of faces gets one long card per layer of its set, back to front: the
        densest just off the wall, the sparsest at the front, spread over `depth` (a cell by
        default). Each layer wraps round outside corners and is trimmed in inside ones, so it
        follows the wall's outline at its own distance, and a card that would pass through a
        camera is left out.
        """
        if not self._fringes:
            return []
        cams = self._cam_spots(scene)
        out = []
        for spec, d, line, a, b in self._face_runs(self._fringes):
            name = spec.get('set')
            if 'cards' in spec:
                cards = list(spec['cards'])
            elif name in assets.FRINGES:
                cards = list(assets.FRINGES[name])
            else:
                raise KeyError(f"unknown fringe set {name!r}. Sets: {', '.join(sorted(assets.FRINGES))}, "
                               f"or give \"cards\" (sprite names, back to front)")
            depth, hk, seed = float(spec.get('depth', 1.0)), float(spec.get('height', 1.0)), int(spec.get('seed', 0))
            for k, card in enumerate(cards):
                off = depth * (k + 0.5) / len(cards)
                lo, hi, _, _ = self._run_ends(d, line, a, b, off)
                if hi - lo < 0.15:
                    continue
                rng = np.random.default_rng([seed, 'nswe'.index(d), line + 1000, a + 1000, k])
                sp = self._card(d, line, lo, hi, off, type=card,
                                scale=float(assets.SPRITE_HEIGHT.get(card, 1.0)) * hk,
                                u0=float(rng.random()), flip=bool(rng.random() < 0.5))
                q = Renderer.plane_quads(sp, np.zeros((1, 1, 4)))[0]
                if any(_seg_dist(cx, cy, *q[:4]) < 0.35 for cx, cy in cams):
                    continue
                out.append(sp)
        return out

    # layers of a facade, back to front: how far out from the wall's face each stands, as a
    # share of the facade's depth (the street line is 1.0)
    FACADE_LAYERS = (('room', 0.45), ('drape', 0.83), ('frame', 0.93), ('glass', 0.93), ('wall', 1.0))

    def _facade(self, scene):
        """Building fronts in layers, for wall cells with a `facade` (see buildings.py).

        Every straight run of faces onto open ground is cut into buildings of `widths` cells,
        each `storeys` units tall, and each building stands its layers - rooms, curtains, frames
        and glass, and the wall with its openings, the street line `depth` out from the walls -
        all spanning the same stretch so its windows line up. A building on an outside corner
        takes its look (colour, height, paint) from the corner, so both its faces match, and a
        building taller than its neighbour shows a side wall above it.
        """
        if not self._facades:
            return []
        out = []
        for spec, d, line, a, b in self._face_runs(self._facades):
            spec = {'style': spec['set']} if 'set' in spec and len(spec) == 1 else dict(spec)
            spec.setdefault('style', spec.pop('set', 'brick'))
            for st in spec['style'] if isinstance(spec['style'], list) else [spec['style']]:
                if st not in buildings.FACADE_STYLES:
                    raise KeyError(f"unknown facade style {st!r}. Styles: {', '.join(buildings.FACADE_STYLES)}")
            depth = float(spec.get('depth', 1.0))
            wmin, wmax = (int(v) for v in spec.get('widths', [3, 6]))
            hmin, hmax = (int(v) for v in spec.get('storeys', [3, 5]))
            seed = int(spec.get('seed', 0))
            lo, hi, kl, kh = self._run_ends(d, line, a, b, depth)
            o = 1 if d in 'se' else -1
            street = line + (1 if o > 0 else 0) + o * depth
            rng = np.random.default_rng([seed, 'nswe'.index(d), line + 1000, a + 1000])
            bounds, pos = [lo], lo
            while hi - pos > wmax:
                pos += int(rng.integers(wmin, wmax + 1))
                bounds.append(pos)
            if hi - pos < wmin and len(bounds) > 1:
                bounds.pop()
            bounds.append(hi)
            spans = list(zip(bounds[:-1], bounds[1:]))
            heights, looks = [], []
            western = any(buildings.FACADE_STYLES[st].get('western')
                          for st in (spec['style'] if isinstance(spec['style'], list) else [spec['style']]))
            names = buildings.street_names(np.random.default_rng([seed, 'nswe'.index(d), line + 1000, a + 1000, 5]),
                                           len(spans)) if western else None
            for i, (s0, s1) in enumerate(spans):
                # a corner building takes its look from the corner, the same from either face
                if (i == 0 and kl == 'convex') or (i == len(spans) - 1 and kh == 'convex'):
                    at = s0 if i == 0 and kl == 'convex' else s1
                    corner = (at, street) if d in 'ns' else (street, at)
                    look = int(round(corner[0] * 4)) * 7919 + int(round(corner[1] * 4)) * 104729 + seed * 31
                else:
                    look = int(rng.integers(1, 2 ** 31))
                storeys = int(np.random.default_rng(look % (2 ** 32)).integers(hmin, hmax + 1))
                heights.append(storeys)
                looks.append(look)
                params = dict(style=spec['style'], w=round(s1 - s0, 3), h=storeys, look=look,
                              seed=int(rng.integers(1, 2 ** 31)), lit=float(spec.get('lit', 0.35)))
                if 'shops' in spec:
                    params['shops'] = float(spec['shops'])
                corner = (i == 0 and kl == 'convex') or (i == len(spans) - 1 and kh == 'convex')
                if names and not corner:                  # a corner building's sign comes from its look, both faces
                    params['name'] = names[i]
                for layer, frac in self.FACADE_LAYERS:
                    fields = dict(type=buildings.layer_name(layer, **params), scale=float(storeys),
                                  flip=d in 'ne')                 # read left to right from the street
                    if layer == 'glass':
                        fields['glass'] = spec.get('glass', True)
                    if layer == 'wall':                   # as thick as the frames are set back in it
                        fields['reveal'] = depth * (1.0 - dict(self.FACADE_LAYERS)['frame']) + 0.004
                    out.append(self._card(d, line, s0, s1, depth * frac, **fields))
                # a village style stands a roof on the wall: a gable end in the wall's own plane, or the
                # slope of thatch or tiles set back behind the eave, so the wall's top hides its foot;
                # each overhangs the ends a little and stands a hair off its neighbour so they never fight
                roof = buildings.roof_of(spec['style'], look, s1 - s0)
                if roof:
                    kind, cover, rh, chim = roof
                    over = 0.0 if kind == 'front' else 0.1
                    off = depth + 0.05 if kind in ('gable', 'front') else depth - min(0.4, depth * 0.45)
                    out.append(self._card(d, line, s0 - over, s1 + over, off + 0.03 * (i % 2),
                                          type=buildings.layer_name('roof', style=spec['style'], look=look, kind=kind,
                                                                    cover=cover, chimney=chim,
                                                                    w=round(s1 - s0 + 2 * over, 3), h=rh,
                                                                    **({'name': params['name']} if 'name' in params else {})),
                                          scale=rh, z=float(storeys), flip=d in 'ne'))
                # a style with blade signs hangs one or two out over the street, square to the front
                look_style = buildings.FACADE_STYLES[buildings.pick_style(spec['style'], look)]
                if look_style.get('blades') and storeys >= 3:
                    brng = np.random.default_rng([look % (2 ** 31), 7])
                    for k in range(int(brng.integers(1, look_style['blades'] + 1))):
                        at = s0 + (s1 - s0) * brng.uniform(0.15, 0.85)
                        out_len, tall = 0.7, float(brng.uniform(1.0, 1.7))
                        z = float(brng.uniform(1.15, max(1.2, storeys - tall - 0.4)))
                        mid = street + o * out_len / 2
                        out.append({'type': buildings.layer_name('blade', style=spec['style'], look=look, seed=k,
                                                                 w=out_len, h=round(tall, 3)),
                                    'x': at if d in 'ns' else mid, 'y': mid if d in 'ns' else at,
                                    'angle': 90.0 if d in 'ns' else 0.0, 'planes': 1, 'length': out_len,
                                    'scale': tall, 'z': z, 'shadow': False, 'flip': d in 'nw'})
                # a western building's covered boardwalk: posts and fascia out at the edge of the walk,
                # as tall as the scene's ceiling, which roofs the walk's cells
                walk = float(spec.get('porch', look_style.get('porch', 0)))
                if walk > 0:
                    out.append(self._card(d, line, s0 + 0.01, s1 - 0.01, depth + walk - 0.05,
                                          type=buildings.layer_name('porch', style=spec['style'], look=look,
                                                                    w=round(s1 - s0 - 0.02, 3), h=round(self.ceil_h, 3)),
                                          scale=self.ceil_h, flip=d in 'ne'))
            # a taller building shows its side wall above a lower neighbour
            for i in range(len(spans) - 1):
                h0, h1 = heights[i], heights[i + 1]
                if h0 == h1:
                    continue
                look = looks[i if h0 > h1 else i + 1]
                at = spans[i][1]
                mid = line + (1 if o > 0 else 0) + o * depth / 2
                out.append({'type': buildings.layer_name('side', style=spec['style'], w=depth, h=abs(h0 - h1),
                                                         look=look),
                            'x': at if d in 'ns' else mid, 'y': mid if d in 'ns' else at,
                            'angle': 90.0 if d in 'ns' else 0.0, 'planes': 1, 'length': depth,
                            'scale': float(abs(h0 - h1)), 'z': float(min(h0, h1)), 'shadow': False})
        return out

    def _open_cells(self, chars=None):
        """Open (non-wall) cells, optionally restricted to a set of legend characters."""
        rows = self.scene['map']
        out = []
        for y in range(self.mh):
            row = rows[y].ljust(self.mw) if y < len(rows) else ' ' * self.mw
            for x in range(self.mw):
                if self.height[y, x] > 0 or self.floor_tid[y, x] < 0:
                    continue
                if chars is None or row[x] in chars:
                    out.append((x, y))
        return out

    def _clear_of_walls(self, x, y, cx, cy, margin):
        """Nudge a point away from any wall face of its cell, so props never clip into walls."""
        if margin <= 0:
            return x, y
        if cx > 0 and self.height[cy, cx - 1] > 0:
            x = max(x, cx + margin)
        if cx < self.mw - 1 and self.height[cy, cx + 1] > 0:
            x = min(x, cx + 1 - margin)
        if cy > 0 and self.height[cy - 1, cx] > 0:
            y = max(y, cy + margin)
        if cy < self.mh - 1 and self.height[cy + 1, cx] > 0:
            y = min(y, cy + 1 - margin)
        return x, y

    def _keep_clear(self, scene):
        """Places scatter must not bury: camera positions and any sprite an overlay anchors to."""
        out = []
        cam = scene.get('camera', {})
        for c in [cam] + list(scene.get('shots', [])):
            cc = {**cam, **c}
            if 'x' in cc and 'y' in cc:
                out.append((float(cc['x']), float(cc['y']), 1.0))
        for sp in scene.get('sprites', []):
            if 'id' in sp:
                out.append((float(sp['x']), float(sp['y']), 1.2))
        return out

    def _sight_lines(self, scene):
        """Camera-to-subject segments that tall scatter must not stand on: each shot's look_at
        target, and every sprite with an `id` that sits inside that shot's view."""
        out = []
        subjects = [sp for sp in scene.get('sprites', []) if 'id' in sp]
        for shot in (scene.get('shots') or [scene.get('camera') or {}]):
            c = merge_camera(scene, shot)
            if 'x' not in c or 'y' not in c:
                continue
            cx, cy = float(c['x']), float(c['y'])
            ang = math.radians(float(c.get('angle', 0)))
            half = math.radians(float(c.get('fov', 66))) / 2 + 0.1
            targets = []
            if isinstance(c.get('look_at'), (list, tuple)):
                targets.append((float(c['look_at'][0]), float(c['look_at'][1])))
            for sp in subjects:
                vx, vy = float(sp['x']) - cx, float(sp['y']) - cy
                off = (math.atan2(vy, vx) - ang + math.pi) % (2 * math.pi) - math.pi
                if 0.3 < math.hypot(vx, vy) < 14 and abs(off) <= half:
                    targets.append((float(sp['x']), float(sp['y'])))
            out += [(cx, cy, tx, ty) for tx, ty in targets]
        return out

    def _contact_shadows(self, scene):
        """A soft dark stamp under every prop and character standing on the floor, so nothing
        looks pasted on. `contact_shadows` sets the strength (0 turns them off); a sprite's own
        `"shadow"` overrides it, `false` for none."""
        strength = scene.get('contact_shadows', 0.55)
        strength = 0.0 if strength is False else 0.55 if strength is True else float(strength)
        defs = scene.get('sprite_defs', {})
        out = []
        for sp in list(scene.get('sprites', [])) + self.scatter_sprites:
            sp = {**assets.sprite_defaults(sp['type'], defs), **sp}
            own = sp.get('shadow')
            s = strength if own is None or own is True else 0.0 if own is False else float(own)
            if s <= 0 or float(sp.get('z', 0)) > 0.05 or sp['type'] in assets.NO_CONTACT_SHADOW:
                continue
            if sp.get('fullbright') or sp.get('blend', 'alpha') != 'alpha' or float(sp.get('opacity', 1)) < 1:
                continue  # ghosts, glows and light sources cast nothing
            cx, cy = int(math.floor(float(sp['x']))), int(math.floor(float(sp['y'])))
            if not (0 <= cy < self.mh and 0 <= cx < self.mw) or self.height[cy, cx] > 0 or self.void[cy, cx]:
                continue  # standing on top of a block, or over a void: no floor to shade
            width = float(sp.get('scale', 1.0)) * assets.sprite_aspect(sp['type'], defs) * float(sp.get('stretch', 1.0))
            out.append({'tex': 'contact_shadow', 'surface': 'floor', 'x': float(sp['x']), 'y': float(sp['y']),
                        # wider than the prop: half the disc hides behind its feet, and the
                        # visible half is foreshortened to a few rows at a grazing angle
                        'size': min(max(width * 1.25 + 0.12, 0.3), 1.8), 'opacity': min(1.0, s)})
        return out

    def _scatter_points(self, cells, count, rng, clump, margin, keep=()):
        """Pick `count` positions over `cells`, weighted by the shared noise field.

        Uniform random scatter reads as machine-made: everything evenly spaced, no bare patches.
        Weighting cell choice by smooth noise gives drifts and clearings for free, and a gaussian
        jitter inside the chosen cell keeps items off the grid lines.
        """
        if not cells or count <= 0:
            return []
        field = noise_field()
        cx = np.array([c[0] for c in cells], np.float64) + 0.5
        cy = np.array([c[1] for c in cells], np.float64) + 0.5
        w = sample_noise(field, cx / SCATTER_PERIOD, cy / SCATTER_PERIOD).astype(np.float64)
        w = np.clip(w, 0.02, 1.0) ** max(0.0, clump) if clump > 0 else np.ones_like(w)
        w /= w.sum()
        picks = rng.choice(len(cells), size=count, p=w)
        out = []
        for i in picks:
            gx, gy = cells[i]
            # gaussian jitter about the cell centre, clipped so it stays in the cell
            jx = float(np.clip(rng.normal(0.5, 0.21), 0.08, 0.92))
            jy = float(np.clip(rng.normal(0.5, 0.21), 0.08, 0.92))
            x, y = self._clear_of_walls(gx + jx, gy + jy, gx, gy, margin)
            if any((x - kx) ** 2 + (y - ky) ** 2 < kr * kr for kx, ky, kr in keep):
                continue  # never pile debris on a camera or in front of a speaking character
            out.append((x, y))
        return out

    def _expand_scatter(self, scene):
        """Turn `scatter` specs (and `grime`) into real sprites and decals, once, at load."""
        self.scatter_sprites = []
        grime = self._grime(scene)
        base_seed = int(scene.get('seed', 0))
        keep = self._keep_clear(scene)
        sight = self._sight_lines(scene)
        specs = list(scene.get('scatter', []))
        if grime > 0 and scene.get('grime_debris', True):
            specs.append({'of': 'wreckage', 'density': 0.05 * grime, 'sizes': ['tiny', 'small'],
                          'seed': 991, '_auto': True})

        for n, spec in enumerate(specs):
            rng = np.random.default_rng(base_seed * 7919 + int(spec.get('seed', n)) * 104729 + 13)
            cells = self._open_cells(spec.get('on'))
            density = float(spec.get('density', 0.35)) * (1.0 + 2.0 * grime)
            count = int(round(density * len(cells)))
            if count <= 0:
                continue
            defs = scene.get('sprite_defs', {})
            items = assets.debris_items(spec.get('of', 'stones'))
            for name in sorted(set(items)):
                try:
                    assets.get_sprite(name, defs)
                except KeyError:
                    raise KeyError(f"scatter 'of' names {name!r}, which is neither a debris set "
                                   f"({', '.join(sorted(assets.DEBRIS_SETS))}) nor a built-in or "
                                   f"sprite_defs sprite") from None
            sizes = spec.get('sizes') or assets.SIZE_WEIGHTS
            if isinstance(sizes, dict):
                names, weights = list(sizes), np.array([float(v) for v in sizes.values()])
            else:
                names, weights = list(sizes), np.ones(len(sizes))
            unknown = [s for s in names if s not in assets.SIZE_CLASSES]
            if unknown:
                raise KeyError(f"scatter 'sizes' has unknown class(es) {unknown}; "
                               f"classes are {', '.join(assets.SIZE_CLASSES)}")
            weights = weights / weights.sum()
            margin = float(spec.get('margin', 0.22))
            pts = self._scatter_points(cells, count, rng, float(spec.get('clump', 1.4)), margin,
                                       keep)
            for (x, y) in pts:
                name = items[int(rng.integers(len(items)))]
                cls = names[int(rng.choice(len(names), p=weights))]
                scale = assets.size_scale(name, cls, defs)
                # A keep-clear radius alone is not enough: a `huge` boulder is over a unit wide,
                # so it can sit outside the radius and still fill the frame. Grow the exclusion
                # by the item's own half-width.
                half = 0.5 * scale * assets.sprite_aspect(name, defs)
                if any((x - kx) ** 2 + (y - ky) ** 2 < (kr + half) ** 2 for kx, ky, kr in keep):
                    continue
                # low clutter between camera and subject reads as ground; anything taller blocks it
                if scale > 0.22 and any(_seg_dist(x, y, *s) < 0.28 + half for s in sight):
                    continue
                sp = {'x': round(float(x), 3), 'y': round(float(y), 3), 'type': name,
                      'scale': round(scale, 4)}
                if rng.random() < 0.5:
                    sp['flip'] = True
                self.scatter_sprites.append(sp)

        return self._grime_decals(scene, grime)

    def _grime_decals(self, scene, grime):
        """Wear stamped on visible wall faces and floors, scaled by `grime`."""
        if grime <= 0 or not scene.get('grime_decals', True):
            return []
        rng = np.random.default_rng(int(scene.get('seed', 0)) * 7919 + 7717)
        out = []
        faces = []
        for y in range(self.mh):
            for x in range(self.mw):
                if self.height[y, x] <= 0 or self.see[y, x]:
                    continue
                for face, (dx, dy) in (('south', (0, 1)), ('north', (0, -1)),
                                       ('east', (1, 0)), ('west', (-1, 0))):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.mw and 0 <= ny < self.mh \
                            and self.height[ny, nx] <= 0 and self.floor_tid[ny, nx] >= 0:
                        faces.append((x, y, face))
        rng.shuffle(faces)
        for (x, y, face) in faces[:int(round(len(faces) * 0.35 * grime))]:
            tex = assets.GRIME_WALL_DECALS[int(rng.integers(len(assets.GRIME_WALL_DECALS)))]
            high = tex in ('leak', 'vines')
            u = float(rng.uniform(0.25, 0.75))
            z = float(rng.uniform(0.6, 0.9) if high else rng.uniform(0.2, 0.7))
            size = round(float(rng.uniform(0.4, 0.9)), 3)
            opacity = float(rng.uniform(0.35, 0.8))
            # a wall decal is clipped to its own face, so one that overhangs the cell edge ends
            # in a hard vertical cut: slide it back inside (draw order unchanged, so seeds hold)
            u = min(max(u, size / 2), 1 - size / 2)
            out.append({'tex': tex, 'surface': 'wall', 'cell': [x, y], 'face': face,
                        'u': u, 'z': round(z, 3), 'size': size, 'opacity': round(opacity, 3)})
        cells = self._open_cells()
        for (x, y) in self._scatter_points(cells, int(round(len(cells) * 0.10 * grime)),
                                           rng, 1.4, 0.3, self._keep_clear(scene)):
            tex = assets.GRIME_FLOOR_DECALS[int(rng.integers(len(assets.GRIME_FLOOR_DECALS)))]
            out.append({'tex': tex, 'surface': 'floor', 'x': round(float(x), 3),
                        'y': round(float(y), 3),
                        'size': round(float(rng.uniform(0.7, 2.0)), 3),
                        'opacity': round(float(rng.uniform(0.3, 0.7)), 3)})
        return out

    def tid(self, spec):
        key = json.dumps(spec, sort_keys=True)
        if key not in self._tidx:
            rgb, em = assets.get_texture(spec)
            self._tidx[key] = len(self.tex)
            self.tex.append((rgb, em))
            self.tex_key.append(assets.texture_key(spec))
            self.tex_noise.append(assets.texture_noise(spec))
            self.tex_alpha.append(assets.get_alpha(spec))
        return self._tidx[key]


# ------------------------------------------------------------------ lighting

def build_lightmap(world, lights, res=8):
    """Returns dynamic light (mh*res, mw*res, 3) from point lights with grid shadows."""
    H, W = world.mh * res, world.mw * res
    lm = np.zeros((H, W, 3), np.float32)
    if not lights:
        return lm, res
    sy, sx = np.mgrid[0:H, 0:W]
    px = (sx.ravel() + 0.5) / res
    py = (sy.ravel() + 0.5) / res
    for L in lights:
        lx, ly = float(L['x']), float(L['y'])
        lz = float(L.get('z', 1.2))
        r = float(L.get('radius', 4.0))
        inten = float(L.get('intensity', 1.0))
        c = np.array(L.get('color', [1.0, 0.85, 0.6]), np.float32)
        dx, dy = lx - px, ly - py
        d = np.sqrt(dx * dx + dy * dy)
        near = d < r
        idx = np.nonzero(near)[0]
        if idx.size == 0:
            continue
        f = np.clip(1 - d[idx] / r, 0, 1) ** 2 * inten
        if L.get('shadows', True):
            block_h = min(lz, 0.95)
            steps = int(min(120, max(8, r * 12)))
            vis = np.ones(idx.size, bool)
            ix, iy = px[idx], py[idx]
            ddx, ddy = dx[idx], dy[idx]
            own_x, own_y = np.floor(ix).astype(int), np.floor(iy).astype(int)
            lcx, lcy = int(math.floor(lx)), int(math.floor(ly))
            for t in np.linspace(0.02, 0.98, steps):
                qx = np.floor(ix + ddx * t).astype(int)
                qy = np.floor(iy + ddy * t).astype(int)
                inb = (qx >= 0) & (qy >= 0) & (qx < world.mw) & (qy < world.mh)
                qxc, qyc = np.clip(qx, 0, world.mw - 1), np.clip(qy, 0, world.mh - 1)
                hb = world.solid_h[qyc, qxc]
                skip = ((qx == own_x) & (qy == own_y)) | ((qx == lcx) & (qy == lcy))
                vis &= ~(inb & (hb >= block_h) & ~skip)
            f = f * vis
        flat = lm.reshape(-1, 3)
        flat[idx] += f[:, None] * c[None, :]
    return lm, res


SUN_DEFAULTS = {
    # colour, intensity, disc colour, disc radius (degrees), halo strength
    'sun': ([1.0, 0.94, 0.82], 0.85, [1.0, 0.96, 0.82], 2.6, 0.6),
    'moon': ([0.55, 0.65, 0.95], 0.4, [0.9, 0.9, 0.84], 2.0, 0.3),
}


def build_sun(world, L, res=4):
    """A directional light (sun or moon) and its shadows.

    Shadows come from one map: for each ground sample, the lowest height that can still see the
    light - the highest (wall height - distance x tan(elevation)) met while marching toward it.
    A point at height z is then lit when z clears that value, so facades are half-lit behind a
    lower building, characters' legs fall into the shadow of a wall, and a wall face turned
    away from the light shadows itself.

    Under a roof the light can only arrive through a gap - a doorway, a see-through window, the
    open side of a porch - so a second map holds the highest height that can still see it: the
    ray toward the light must be below the ceiling where it leaves the last roofed cell. A
    sunbeam therefore comes in low through a window and lands on the floor across the room.
    """
    kind = L.get('type')
    colour, inten, disc_c, disc_r, glow = SUN_DEFAULTS[kind]
    az = math.radians(float(L.get('azimuth', 300)))
    el = math.radians(min(89.0, max(1.0, float(L.get('elevation', 35)))))
    ux, uy, tan_el = math.cos(az), math.sin(az), math.tan(el)
    H, W = world.mh * res, world.mw * res
    sy, sx = np.mgrid[0:H, 0:W]
    px, py = (sx + 0.5) / res, (sy + 0.5) / res
    zlit = np.full((H, W), -1.0, np.float32)
    maxh = float(world.solid_h.max())
    if L.get('shadows', True) and maxh > 0:
        own_x, own_y = np.floor(px).astype(int), np.floor(py).astype(int)
        reach = min(maxh / tan_el, float(world.mw + world.mh))
        for t in np.arange(0.2, reach + 0.25, 0.25):
            qx = np.floor(px + ux * t).astype(int)
            qy = np.floor(py + uy * t).astype(int)
            inb = (qx >= 0) & (qy >= 0) & (qx < world.mw) & (qy < world.mh)
            hb = np.where(inb, world.solid_h[np.clip(qy, 0, world.mh - 1), np.clip(qx, 0, world.mw - 1)], 0)
            cand = np.where((qx == own_x) & (qy == own_y), -1.0, hb - t * tan_el)
            np.maximum(zlit, cand, out=zlit)
    roof = (world.ceil_tid >= 0) & ~world.glazed      # a glazed roof lets the light through
    zroof = np.full((H, W), np.inf, np.float32)
    zsky = np.full((2, H, W), -np.inf, np.float32)     # the band of heights lit down through a skylight
    if roof.any() and L.get('shadows', True):
        last = np.full((H, W), -1.0, np.float32)    # how far toward the light the roof lasts
        t_open = np.full((H, W), np.inf, np.float32)     # where the first stretch of open sky begins...
        t_shut = np.full((H, W), np.inf, np.float32)     # ...and where roof takes over again
        reach = min(world.ceil_h / tan_el + 1.0, float(world.mw + world.mh))
        for t in np.arange(0.0, reach + 0.25, 0.25):
            qx = np.floor(px + ux * t).astype(int)
            qy = np.floor(py + uy * t).astype(int)
            inb = (qx >= 0) & (qy >= 0) & (qx < world.mw) & (qy < world.mh)
            under = inb & roof[np.clip(qy, 0, world.mh - 1), np.clip(qx, 0, world.mw - 1)]
            last = np.where(under, t, last)
            t_shut = np.where(np.isfinite(t_open) & np.isinf(t_shut) & under, t, t_shut)
            t_open = np.where(np.isinf(t_open) & ~under, t, t_open)
        zroof = np.where(last >= 0, world.ceil_h - (last + 0.25) * tan_el, np.inf).astype(np.float32)
        # a ray rising from height z crosses the roof's height (t - z/tan) along the way; if it
        # crosses inside that first open stretch it escapes, whatever roof lies beyond
        zsky[1] = np.where(np.isfinite(t_open), world.ceil_h - t_open * tan_el, -np.inf)
        zsky[0] = np.where(np.isfinite(t_shut), world.ceil_h - (t_shut - 0.25) * tan_el, -np.inf)
    elif roof.any():
        zroof[np.repeat(np.repeat(roof, res, 0), res, 1)] = -np.inf
    rgb = np.array(L.get('color', colour), np.float32) * float(L.get('intensity', inten))
    disc = None
    if L.get('disc', True):
        disc = {'azimuth': math.degrees(az), 'elevation': math.degrees(el),
                'color': L.get('disc_color', disc_c), 'radius': float(L.get('disc_size', disc_r)), 'glow': glow}
    return {'ux': ux, 'uy': uy, 'sin': math.sin(el), 'cos': math.cos(el), 'rgb': rgb, 'zlit': zlit,
            'zroof': zroof, 'zsky': zsky, 'ceil_h': world.ceil_h, 'res': res, 'disc': disc}


def sun_visibility(s_, x, y, z, soft=0.12):
    """0-1: how much of a sun or moon a point (x, y, z) sees, with a soft edge to its shadows
    (`soft` is the height over which a shadow edge fades)."""
    zl, zr, r = s_['zlit'], s_['zroof'], s_['res']
    iy = np.clip((np.asarray(y) * r).astype(int), 0, zl.shape[0] - 1)
    ix = np.clip((np.asarray(x) * r).astype(int), 0, zl.shape[1] - 1)
    z = np.asarray(z)
    with np.errstate(invalid='ignore'):
        roof = np.clip(np.nan_to_num(zr[iy, ix] - z, posinf=9.0, neginf=-9.0) / soft + 0.5, 0, 1)
        if 'zsky' in s_:                              # or down through a skylight
            lo, hi = s_['zsky'][0][iy, ix], s_['zsky'][1][iy, ix]
            band = np.clip(np.nan_to_num(z - lo, posinf=9.0, neginf=9.0) / soft + 0.5, 0, 1) * \
                np.clip(np.nan_to_num(hi - z, posinf=9.0, neginf=-9.0) / soft + 0.5, 0, 1)
            roof = np.maximum(roof, band)
    roof = np.where(z >= s_['ceil_h'], 1.0, roof)    # air above a roof is outdoors
    return np.clip((z - zl[iy, ix]) / soft + 0.5, 0, 1) * roof


def _box4(a):
    """4x4 box average over axes 1 and 2 (rows and columns) of a stack of images, edges clamped."""
    pad = [(0, 0), (2, 1), (2, 1)] + [(0, 0)] * (a.ndim - 3)
    c = np.pad(a, pad, mode='edge').cumsum(axis=1).cumsum(axis=2)
    c = np.pad(c, [(0, 0), (1, 0), (1, 0)] + [(0, 0)] * (a.ndim - 3))
    h, w = a.shape[1], a.shape[2]
    out = c[:, 4:4 + h, 4:4 + w] - c[:, :h, 4:4 + w] - c[:, 4:4 + h, :w] + c[:, :h, :w]
    return (out / 16.0).astype(np.float32)


GLASS_DEFAULTS = {'tint': [0.82, 0.92, 1.0], 'opacity': 0.22, 'blur': 1, 'fog': False}


def glass_spec(g):
    """A sprite's `glass` field filled out: `true` takes the defaults (a light blue tint, a
    little reflection, the half-size blur), a dict overrides any of them."""
    out = dict(GLASS_DEFAULTS)
    if isinstance(g, dict):
        out.update(g)
    out['tint'] = np.array(out['tint'], np.float32)
    out['opacity'] = min(1.0, max(0.0, float(out['opacity'])))
    out['blur'] = max(0, min(3, int(out['blur'])))
    out['fog'] = bool(out['fog'])
    return out


def hole_runs(alpha):
    """For every see-through texel of an image, the run of see-through texels it lies in: its
    left and right ends along the row, and its top and bottom down the column (ends exclusive).
    For a rectangular opening that is the opening, which is how a card with `reveal` finds the
    sides of its windows."""
    clear = alpha < 0.5
    h, w = clear.shape
    xs = np.broadcast_to(np.arange(w), (h, w))
    ys = np.broadcast_to(np.arange(h)[:, None], (h, w))
    left = np.maximum.accumulate(np.where(clear, -1, xs), axis=1) + 1
    right = np.minimum.accumulate(np.where(clear, w, xs)[:, ::-1], axis=1)[:, ::-1]
    top = np.maximum.accumulate(np.where(clear, -1, ys), axis=0) + 1
    bottom = np.minimum.accumulate(np.where(clear, h, ys)[::-1], axis=0)[::-1]
    return left, right, top, bottom


def frost(img, k):
    """The frame shrunk by k - each k x k block averaged - and blown back up without smoothing:
    a blocky blur, the look of a scene through old window glass."""
    H, W = img.shape[:2]
    h, w = H // k, W // k
    out = img.copy()
    if h and w:
        small = img[:h * k, :w * k].reshape(h, k, w, k, -1).mean(axis=(1, 3))
        out[:h * k, :w * k] = np.repeat(np.repeat(small, k, 0), k, 1)
    return out


def sample_lm(lm, res, x, y):
    """Bilinear lightmap lookup for arrays of world coordinates."""
    H, W = lm.shape[:2]
    fx = np.clip(x * res - 0.5, 0, W - 1.001)
    fy = np.clip(y * res - 0.5, 0, H - 1.001)
    x0, y0 = fx.astype(int), fy.astype(int)
    tx, ty = (fx - x0)[..., None], (fy - y0)[..., None]
    a = lm[y0, x0]; b = lm[y0, x0 + 1]; c = lm[y0 + 1, x0]; d = lm[y0 + 1, x0 + 1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def height_falloff(z):
    """Point lights sit near head height; tall walls fade into the dark above them."""
    return 1.0 / (1.0 + 0.7 * np.maximum(0, z - 1.4) ** 1.5)


# ------------------------------------------------------------------ surface variation

_NOISE_FIELD = None
COARSE_PERIOD = 6.3   # world units: varies cell to cell
FINE_PERIOD = 0.43    # sub-cell, so a 1-unit wall gets a few cycles and mottles instead of
                      # streaking vertically; also never lines up with the 1-unit texture tiling
SCATTER_PERIOD = 9.0  # world units a scatter drift spans; wider than the surface octaves
NOISE_TYPICAL = 0.27  # mean |value| of the two-octave blend, measured; divided out so that
                      # `amount` is the typical brightness swing rather than a rare peak
SURFACE_NOISE_DEFAULT = 0.10  # typical brightness swing, before each material scales it by its
                              # assets.TEXTURE_NOISE factor. "surface_noise": 0 disables it


def noise_field(size=256):
    """Tileable 0..1 value noise, built once and shared by every surface."""
    global _NOISE_FIELD
    if _NOISE_FIELD is None:
        n = assets.fbm(size, np.random.default_rng(20250115), base=4, octaves=5)
        lo, hi = np.percentile(n, 2), np.percentile(n, 98)
        _NOISE_FIELD = np.clip((n - lo) / max(hi - lo, 1e-6), 0, 1).astype(np.float32)
    return _NOISE_FIELD


def sample_noise(field, u, v):
    """Wrapping nearest lookup. u and v are counted in field periods, not pixels."""
    n = field.shape[0]
    return field[(v * n).astype(np.int32) % n, (u * n).astype(np.int32) % n]


def soft_swing(x, knee=0.5, limit=0.9):
    """Pass brightness swings below `knee` through unchanged and ease larger ones toward ±`limit`.

    amount x variation is unbounded: a rough material under heavy grime (cobble at grime 1 asks
    for swings near +/-2) would otherwise drive the albedo multiplier below zero and print black
    speckles. tanh keeps the slope continuous at the knee, so there is no visible seam between
    the untouched and the compressed range.
    """
    x = np.asarray(x, np.float32)
    a = np.abs(x)
    over = a > knee
    if not over.any():
        return x
    out = x.copy()
    span = limit - knee
    out[over] = np.sign(x[over]) * (knee + span * np.tanh((a[over] - knee) / span))
    return out


# ------------------------------------------------------------------ renderer

class Renderer:
    def __init__(self, world, scene):
        scene = prefabs.expand(scene)
        self.w = world
        self.s = scene
        self.W, self.H = scene.get('resolution', [320, 200])
        self.ambient = np.array(scene.get('ambient', [0.18, 0.18, 0.22]), np.float32)
        self.levels = int(scene.get('light_levels', 24))
        fog = scene.get('fog')
        self.fog_c = np.array(fog['color'], np.float32) if fog else None
        self.fog_d = float(fog.get('density', 0.1)) if fog else 0.0
        # Any of the volumetric keys moves fog from a per-surface fade to a pass that marches
        # through the air in front of every pixel, so it can lie low, drift in banks, glow round
        # lamps and carry shafts of sun or moonlight.
        self.vol = None
        if fog and any(k in fog for k in FOG_VOLUME_KEYS):
            sh = fog.get('shafts', True)
            self.vol = {'density': float(fog.get('density', 0.02)),
                        'ground': float(fog.get('ground', 0.0)),
                        'height': max(0.05, float(fog.get('height', 0.6))),
                        'noise': float(fog.get('noise', 0.0)),
                        'scale': max(0.2, float(fog.get('scale', 4.0))),
                        'glow': float(fog.get('glow', 1.0)),
                        'shafts': 1.0 if sh is True else 0.0 if sh is False else float(sh),
                        'steps': max(6, int(fog.get('steps', 32))),
                        'distance': float(fog.get('distance', min(48.0, float(scene.get('max_distance', 64))))),
                        'g': min(0.9, max(-0.5, float(fog.get('anisotropy', 0.3))))}
        lights, suns = [], []
        for L in scene.get('lights', []):
            kind = L.get('type', 'point')
            if kind not in ('point', 'sun', 'moon'):
                raise KeyError(f"unknown light type '{kind}'. Types: point (default), sun, moon")
            (lights if kind == 'point' else suns).append(L)
        for sp in scene.get('sprites', []):
            sp = {**assets.sprite_defaults(sp['type'], scene.get('sprite_defs', {})), **sp}
            if sp.get('light'):
                base = world.base_z(float(sp['x']), float(sp['y']))
                L = {'x': sp['x'], 'y': sp['y'], 'z': float(sp.get('z', 0)) + base + 0.2, 'shadows': True}
                L.update(sp['light'] if isinstance(sp['light'], dict) else {})
                lights.append(L)
        self.lm, self.lres = build_lightmap(world, lights, scene.get('lightmap_res', 8))
        self.overbright = float(scene.get('overbright', 1.0))
        self.suns = [build_sun(world, L) for L in suns]
        rf = scene.get('reflections', True)
        rf = ({} if rf is True else {'amount': 0.0} if rf is False
              else rf if isinstance(rf, dict) else {'amount': rf})
        self.reflect_k = float(rf.get('amount', 1.0))
        self.ripple = float(rf.get('ripple', 1.0))
        # a sun or moon light shows itself in the sky (unless it asks not to)
        self.discs = [s_['disc'] for s_ in self.suns if s_['disc']]
        self.sky_objects = list(scene.get('sky_objects') or [])
        self._skies = {}
        self._runs = {}
        sn = scene.get('surface_noise', SURFACE_NOISE_DEFAULT)
        by_texture = {}
        if isinstance(sn, dict):
            self.sn_amount = float(sn.get('amount', SURFACE_NOISE_DEFAULT))
            self.sn_scale = float(sn.get('scale', 1.0))
            by_texture = sn.get('by_texture', {}) or {}
        else:
            self.sn_amount, self.sn_scale = float(sn), 1.0
        self.sn_amount *= 1.0 + 1.5 * world._grime(scene)  # neglect shows on the surfaces too
        # Resolve one absolute amount per texture id: the scene amount scaled by the material's
        # own appetite for variation, unless the scene names that material explicitly.
        self.tex_amount = np.array(
            [float(by_texture[k]) if k in by_texture else self.sn_amount * m
             for k, m in zip(world.tex_key, world.tex_noise)], np.float32)
        self.sn = noise_field() if float(np.abs(self.tex_amount).max(initial=0.0)) > 1e-4 else None

    def surface_variation(self, u, v, key=0.0):
        """Signed ~[-1, 1] variation across one surface, anchored in world space.

        (u, v) are coordinates *on the surface* - (x, y) for floors and ceilings, (along, height)
        for walls - so the pattern sits still as the camera moves and stays continuous along a
        wall instead of breaking at cell edges. `key` separates surfaces that share coordinates
        (floor vs ceiling, the two wall orientations, each wall plane).
        """
        f, s, o = self.sn, self.sn_scale, key * 0.613
        coarse = 2 * sample_noise(f, (u + o) / (COARSE_PERIOD * s), (v + o) / (COARSE_PERIOD * s)) - 1
        fine = 2 * sample_noise(f, (u - o) / (FINE_PERIOD * s), (v - o) / (FINE_PERIOD * s)) - 1
        # Even weighting: leaning on the coarse octave makes a 1-unit-tall wall see mostly a
        # horizontal gradient, which reads as vertical banding once the amplitude is turned up.
        # Dividing by the blend's own typical magnitude makes `amount` mean what it says.
        return np.clip((0.5 * coarse + 0.5 * fine) / NOISE_TYPICAL, -2.6, 2.6)

    # --- shading helpers
    def sun_at(self, x, y, z, lam):
        """Direct light from every sun or moon at points (x, y) of height z. `lam(sun)` gives the
        Lambert factor for the surface's orientation (scalar or per point). Not subject to the
        point lights' height falloff: sunlight reaches the top of a tall facade as well."""
        total = 0.0
        for s_ in self.suns:
            total = total + (sun_visibility(s_, x, y, z) * lam(s_))[..., None] * s_['rgb']
        return total

    @staticmethod
    def lam_up(s_):
        return s_['sin']

    def shade(self, albedo, dyn, z, dist, em, flash, sun=0.0):
        light = self.ambient[None, :] + dyn * height_falloff(z)[..., None] + flash + sun
        light = light * self.overbright
        if self.levels > 0:
            light = np.floor(light * self.levels + 0.5) / self.levels
        out = albedo * light
        if em is not None:
            e = em[..., None]
            out = out * (1 - e) + albedo * e * 1.15
        if self.fog_c is not None and self.vol is None:
            k = (1 - np.exp(-self.fog_d * dist))[..., None]
            out = out * (1 - k) + self.fog_c[None, :] * k
        return out

    def render(self, cam):
        """Render one camera: 3D pass (optionally supersampled), then UI overlays at native res."""
        ss = int(cam.get('supersample', self.s.get('supersample', 1)))
        self._ss = ss
        bw, bh = self.W, self.H
        self.W, self.H = bw * ss, bh * ss
        try:
            img = self._render3d(cam)
            if self.vol is not None:
                img = self._atmosphere(img, self.depth, ss)
        finally:
            self.W, self.H = bw, bh
        if ss > 1:
            img = img.reshape(bh, ss, bw, ss, 3).mean(axis=(1, 3))
            for a in self.anchors.values():
                for k in ('x', 'top', 'w', 'h'):
                    a[k] /= ss
        self.last_report = self._report(cam, img, ss)
        overlays = list(self.s.get('overlays', [])) + list(cam.get('overlays', []))
        effects = post.expand(list(self.s.get('post', [])) + list(cam.get('post', [])))
        if cam.get('scanlines', self.s.get('scanlines')) and not any(e['fx'] in ('scanlines', 'crt') for e in effects):
            effects.append({'fx': 'scanlines'})
        H, W = img.shape[:2]
        ctx = gui.Ctx(Image.new('RGBA', (W, H), (0, 0, 0, 0)), self.s, self.anchors, cam, self.w, self.camera_light(cam))
        img = gui.draw_world_layer(img, overlays, ctx)
        img = post.apply_world(img, effects, self._weather_ctx(cam, ss, bw, bh))
        img = gui.draw_ui_layer(img, overlays, ctx)
        self.last_effects = effects
        return np.clip(img, 0, 1)

    def _report(self, cam, img, ss):
        """Problems with the frame that are easy to miss in a small preview, each with a fix:
        too dark or blown out, a black foreground, a blank where there is no sky, a wall in the
        lens, a camera inside a wall, and a subject (the `look_at` sprite or a bubble's speaker)
        that is hidden, cut off, tiny or unlit. The CLI prints them after each shot."""
        out = []
        lum = img @ np.array([0.299, 0.587, 0.114], np.float32)
        H, W = lum.shape
        mean = float(lum.mean())
        if mean < 0.045:
            out.append(f'the frame is very dark (mean brightness {mean:.2f}): raise "ambient" or add lights in view')
        elif float(lum[int(H * 0.75):].mean()) < 0.02:
            out.append('the bottom of the frame is nearly black: no light reaches the floor near the camera; '
                       'stretch a light over it or raise "ambient"')
        hot = float((lum > 0.97).mean())
        if hot > 0.25:
            out.append(f'{hot:.0%} of the frame is near white: lower the lights or "ambient", '
                       'or drop a bright post preset')
        depth = self.depth
        if not self.s.get('sky'):
            dark = img.repeat(ss, 0).repeat(ss, 1).sum(axis=2) < 1e-4
            blank = float((np.isinf(depth) & dark).mean())
            if blank > 0.02:
                out.append(f'{blank:.0%} of the frame shows nothing: with "sky": null an open cell needs a "ceil", '
                           'and the map needs walls all round where the camera can see')
        close = float((depth < 0.6).mean())
        if close > 0.3:
            out.append(f'something under 0.6 units from the camera fills {close:.0%} of the frame: step back or turn')
        cx, cy = int(math.floor(float(cam['x']))), int(math.floor(float(cam['y'])))
        if not (0 <= cy < self.w.mh and 0 <= cx < self.w.mw):
            out.append(f'the camera ({cam["x"]}, {cam["y"]}) is outside the map')
        elif self.w.solid_h[cy, cx] >= float(cam.get('height', 0.5)):
            out.append(f'the camera ({cam["x"]}, {cam["y"]}) is inside a wall cell')
        subjects = [cam['look_at']] if isinstance(cam.get('look_at'), str) else []
        for ov in list(self.s.get('overlays', [])) + list(cam.get('overlays', [])):
            if isinstance(ov, dict) and ov.get('type') == 'bubble' and ov.get('anchor'):
                subjects.append(ov['anchor'])
        named = {sp.get('id') for sp in list(self.s.get('sprites', [])) + list(cam.get('extra_sprites', []))}
        for sid in dict.fromkeys(subjects):
            st = self.sprite_stats.get(sid)
            if st is None:
                if sid in named:
                    out.append(f'"{sid}" is behind the camera or out of the frame')
                continue
            if st['visible'] <= 0:
                out.append(f'"{sid}" is completely hidden, behind a wall or a nearer sprite: check the map')
                continue
            seen = st['visible'] / max(st['area'], 1e-6)
            if seen < 0.4:
                out.append(f'only {seen:.0%} of "{sid}" is visible: something is in front of it, '
                           'or the frame edge cuts it off')
            if st['height'] / ss < 14:
                out.append(f'"{sid}" is only {st["height"] / ss:.0f} px tall on screen: move closer or narrow the fov')
            if st['brightness'] < 0.06:
                out.append(f'"{sid}" is almost black: give it a light (sprite "light") unless a silhouette is the point')
        return out

    def _weather_ctx(self, cam, ss, bw, bh):
        """What the world-stage post effects need to put weather in the scene: the depth buffer
        and the camera rays at output resolution, the world (walls, roofs) and the fog."""
        ctx = {'seed': int(self.s.get('seed', 0)) + int(cam.get('seed', 0)), 'world': self.w,
               'fog_d': self.fog_d if (self.fog_c is not None and self.vol is None) else 0.0}
        r = getattr(self, 'rays', None)
        if r is not None:
            c0 = np.arange(bw) * ss + ss // 2
            ctx['rays'] = {'px': r['px'], 'py': r['py'], 'rdx': r['rdx'][c0], 'rdy': r['rdy'][c0],
                           'horizon': r['horizon'] / ss, 'proj': r['proj'] / ss, 'camz': r['camz']}
            ctx['depth'] = self.depth.reshape(bh, ss, bw, ss).min(axis=(1, 3))
            if self.vol is not None:
                ctx['fog_t'] = self.fog_t[:2]
        return ctx

    def _atmosphere(self, img, depth, ss):
        """Volumetric fog: march the air in front of every pixel, losing the surface behind it to
        the fog's density and gaining the light the fog scatters toward the eye.

        One ray is marched per output pixel; each supersampled pixel then reads the result at its
        own depth, so fog meets the edge of every wall cleanly. Density is a thin even haze plus
        a ground layer that thins with height and drifts in banks (`noise`); the light it carries
        is its own colour, the point lights (`glow`, read from the shadowed lightmap, so lamps
        get halos and doorways spill light) and every sun or moon it can see (`shafts`, through
        the shadow maps, with forward scattering so beams brighten as you look toward them).
        Behind glass the fog carries on: the glass pass leaves a correction for the air between
        each pane and what is seen through it (see _glass_pass).
        """
        if not self._marched:
            self._march(depth.shape, ss)
        H, W = depth.shape
        Tp, Lp = self._fog_px(np.arange(H)[:, None], np.arange(W)[None, :], depth)
        out = img * Tp[..., None] + Lp
        if self._glass_fix is not None:
            out = out + self._glass_fix
        return out

    def _march(self, shape, ss):
        """The march itself, once a frame: how much of the light from each distance along every
        ray gets through the air, and how much the air adds, kept in self.fog_t."""
        self._marched = True
        v, r = self.vol, self.rays
        H, W = shape
        h, w = H // ss, W // ss
        c0 = np.arange(w) * ss + ss // 2
        rdx, rdy, rlen = r['rdx'][c0], r['rdy'][c0], r['rlen'][c0]
        slope = (r['horizon'] - (np.arange(h) * ss + ss / 2)) / r['proj']        # z gained per unit t
        sx, sl = rdx[None, :], slope[:, None]
        path = np.sqrt(rlen[None, :] ** 2 + sl ** 2)                              # metres per unit t
        n = v['steps']
        t = v['distance'] * (np.arange(n + 1) / n) ** 1.6                         # finer near the eye
        # each ray samples its segments at a dithered point, so a shaft's edge and the steps of a
        # coarse far segment come out as fine grain instead of bands
        bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32)
        jit = (bayer[np.arange(h)[:, None] % 4, np.arange(w)[None, :] % 4] + 0.5) / 16
        tv = np.zeros((n + 1, h, w), np.float32)
        lv = np.zeros((n + 1, h, w, 3), np.float32)
        T = np.ones((h, w), np.float32)
        L = np.zeros((h, w, 3), np.float32)
        tv[0] = 1.0
        fogc = self.fog_c if self.fog_c is not None else np.zeros(3, np.float32)
        field = noise_field() if v['noise'] > 0 else None
        phase = []
        for s_ in self.suns:
            cos = (sx * s_['ux'] * s_['cos'] + rdy[None, :] * s_['uy'] * s_['cos'] + sl * s_['sin']) / path
            g = v['g']
            phase.append(((1 - g * g) / (1 + g * g - 2 * g * cos) ** 1.5).astype(np.float32))
        for k in range(1, n + 1):
            dt = t[k] - t[k - 1]
            tm = t[k - 1] + jit * dt
            x, y = r['px'] + sx * tm, r['py'] + rdy[None, :] * tm
            z = r['camz'] + sl * tm
            z = np.broadcast_to(z, (h, w))
            # optical depth of the segment: the even haze, plus the ground layer integrated along
            # the ray (Simpson's rule on its height profile, which depends only on the row), so
            # it thins smoothly with height instead of in noisy steps
            tau = np.full((h, w), v['density'] * dt, np.float32)
            if v['ground'] > 0:
                zp = [np.maximum(r['camz'] + sl * tt, 0.0) for tt in (t[k - 1], 0.5 * (t[k - 1] + t[k]), t[k])]
                prof = [np.exp(-zz / v['height']) for zz in zp]
                layer = v['ground'] * dt / 6.0 * (prof[0] + 4 * prof[1] + prof[2])
                if field is not None:            # banks about `scale` wide, fading smoothly
                    patch = sample_noise(field, x / (v['scale'] * 4.0), y / (v['scale'] * 4.0))
                    layer = layer * np.exp(v['noise'] * 1.6 * (2 * patch - 1))
                tau = tau + layer
            a = 1 - np.exp(-tau * path)
            light = np.broadcast_to(fogc, (h, w, 3)).astype(np.float32)
            if v['glow'] > 0:
                light = light + v['glow'] * sample_lm(self.lm, self.lres, x, y) * height_falloff(z)[..., None]
            if v['shafts'] > 0:
                for s_, ph in zip(self.suns, phase):
                    # scaled so a beam seen side-on reads as a beam, and the air round a low
                    # sun glows without whiting out the frame
                    light = light + (0.6 * v['shafts'] * sun_visibility(s_, x, y, z, 0.35) * ph)[..., None] * s_['rgb']
            L = L + (T * a)[..., None] * light
            T = T * (1 - a)
            tv[k], lv[k] = T, L
        # neighbouring rays see nearly the same air: averaging each step over the 4x4 tile of the
        # dither pattern removes the pattern but keeps shafts and banks, and each pixel still reads
        # the result at its own depth, so nothing bleeds across a silhouette
        tv, lv = _box4(tv), _box4(lv)
        self.fog_t = (t, tv, lv)        # kept for weather, which sits inside the same fog

    def _fog_px(self, ri, ci, depth):
        """What the air does to the pixels at rows ri and columns ci (index arrays of the
        supersampled frame, broadcast together) seen at `depth`: the share of the light from that
        far that gets through (T) and the light the air in front adds (L). Each pixel reads its
        parent ray's march at its own depth."""
        t, tv, lv = self.fog_t
        ss = self._ss
        n = len(t) - 1
        d = np.minimum(np.nan_to_num(depth, posinf=t[-1]), t[-1])
        k = np.clip(np.searchsorted(t, d), 1, n)
        f = np.clip((d - t[k - 1]) / np.maximum(t[k] - t[k - 1], 1e-6), 0, 1)
        pi, pj = ri // ss, ci // ss
        Tp = tv[k - 1, pi, pj] * (1 - f) + tv[k, pi, pj] * f
        Lp = lv[k - 1, pi, pj] * (1 - f)[..., None] + lv[k, pi, pj] * f[..., None]
        # light scattered toward the eye eases off toward white instead of clipping, so mist
        # lit by a low sun glows rather than whiting out the frame
        knee = 0.55
        Lp = np.where(Lp > knee, knee + (1 - knee) * np.tanh((Lp - knee) / (1 - knee)), Lp)
        return Tp, Lp

    def camera_light(self, cam):
        """Light falling on things held at the camera (viewmodels): ambient + lightmap + flashlight spill."""
        dyn = sample_lm(self.lm, self.lres, np.array([float(cam['x'])]), np.array([float(cam['y'])]))[0]
        light = self.ambient + dyn * 0.6
        if self.suns:  # a held item in sunlight is lit by it
            fx, fy = math.cos(math.radians(float(cam.get('angle', 0)))), math.sin(math.radians(float(cam.get('angle', 0))))
            light = light + np.asarray(self.sun_at(np.array([float(cam['x'])]), np.array([float(cam['y'])]),
                                                   np.array([0.4]), lambda s_: s_['sin'] * 0.5 + s_['cos'] * 0.6 *
                                                   max(0.2, -(fx * s_['ux'] + fy * s_['uy']))))[0]
        if cam.get('flashlight', self.s.get('flashlight')):
            light = light + 0.25
        # a floor keeps held items readable in near-darkness, the cap stops held lamps blowing them out
        return np.clip(light * self.overbright, 0.22, 1.0).astype(np.float32)

    def _blend_plane_decal(self, alb, emv, wx, wy, d, valid, dcl, rk=None):
        """Stamp one floor/ceiling decal into a surface pass's albedo."""
        sw = dcl['size']
        sh = sw * dcl['dh'] / dcl['dw']
        x0, y0 = dcl['x'] - sw / 2, dcl['y'] - sh / 2
        # a plane's distance is constant per row, so only a band of rows can touch the decal. `d`
        # is measured along the view axis, so the decal's centre must be too: its straight-line
        # distance is longer off-axis, which used to clip decals toward the edges of the frame
        rad = 0.5 * math.hypot(sw, sh)
        ctr = (dcl['x'] - self._px) * self._fx + (dcl['y'] - self._py) * self._fy
        band = np.nonzero((d >= ctr - rad) & (d <= ctr + rad))[0]
        if band.size == 0:
            return
        r0, r1 = int(band[0]), int(band[-1]) + 1
        sx, sy = wx[r0:r1], wy[r0:r1]
        m = (sx >= x0) & (sx <= x0 + sw) & (sy >= y0) & (sy <= y0 + sh) & valid[r0:r1]
        if not m.any():
            return
        du = ((sx[m] - x0) / sw * dcl['dw']).astype(int).clip(0, dcl['dw'] - 1)
        dv = ((sy[m] - y0) / sh * dcl['dh']).astype(int).clip(0, dcl['dh'] - 1)
        tex = dcl['rgba'][dv, du]
        a = (tex[:, 3] * dcl['opacity'])[:, None]
        sub = alb[r0:r1]
        sub[m] = sub[m] * (1 - a) + tex[:, :3] * dcl['tint'][None, :] * a
        de = dcl['em'][dv, du]
        if de.any():
            sube = emv[r0:r1]
            sube[m] = np.maximum(sube[m], de * (a[:, 0] > 0.4))
        if rk is not None and dcl['reflect'] > 0:   # a puddle mirrors what stands over it
            subr = rk[r0:r1]
            subr[m] = np.maximum(subr[m], dcl['reflect'] * a[:, 0])

    def _blend_wall_decals(self, alb, e, decals, uf_raw, z):
        """Stamp wall decals into one column's albedo. Returns the (possibly created) emissive array."""
        for dcl in decals:
            halfw = dcl['size'] / 2
            off = uf_raw - dcl['u']
            if abs(off) > halfw:
                continue
            halfh = (dcl['size'] * dcl['dh'] / dcl['dw']) / 2
            m = np.abs(z - dcl['z']) <= halfh
            if not m.any():
                continue
            dui = min(dcl['dw'] - 1, max(0, int((off + halfw) / (2 * halfw) * dcl['dw'])))
            dvi = (((dcl['z'] + halfh) - z[m]) / (2 * halfh) * dcl['dh']).astype(int).clip(0, dcl['dh'] - 1)
            tex = dcl['rgba'][dvi, dui]
            a = (tex[:, 3] * dcl['opacity'])[:, None]
            alb[m] = alb[m] * (1 - a) + tex[:, :3] * dcl['tint'][None, :] * a
            de = dcl['em'][dvi, dui]
            if de.any():
                if e is None:
                    e = np.zeros(len(z), np.float32)
                e[m] = np.maximum(e[m], de * (a[:, 0] > 0.4))
        return e

    def _render3d(self, cam):
        W, H = self.W, self.H
        w = self.w
        self._marched, self._glass_fix = False, None
        px, py = float(cam['x']), float(cam['y'])
        self._px, self._py = px, py
        ang = math.radians(float(cam.get('angle', 0)))
        fov = math.radians(float(cam.get('fov', 66)))
        camz = float(cam.get('height', 0.5))
        horizon = H / 2 + float(cam.get('pitch', 0)) * H
        proj = (W / 2) / math.tan(fov / 2)
        dx, dy = math.cos(ang), math.sin(ang)
        self._fx, self._fy = dx, dy
        pl = math.tan(fov / 2)

        def in_view(dcl):
            """A floor/ceiling decal that could touch the frame: in front, and inside the cone."""
            vx, vy = dcl['x'] - px, dcl['y'] - py
            r = dcl['size'] * max(1.0, dcl['dh'] / dcl['dw'])
            along = vx * dx + vy * dy
            return along > -r and abs(vy * dx - vx * dy) <= max(along, 0) * pl + r + 0.5
        floor_decals = [d_ for d_ in w.floor_decals if in_view(d_)]
        ceil_decals = [d_ for d_ in w.ceil_decals if in_view(d_)]
        plx, ply = -dy * pl, dx * pl
        cx = 2 * (np.arange(W) + 0.5) / W - 1
        rdx = (dx + plx * cx).astype(np.float64)
        rdy = (dy + ply * cx).astype(np.float64)
        rlen = np.sqrt(rdx ** 2 + rdy ** 2)

        img = np.zeros((H, W, 3), np.float32)
        depth = np.full((H, W), np.inf, np.float32)
        refl = np.zeros((H, W), np.float32)          # how mirror-like each floor pixel is
        refl_depth = np.full((H, W), -1.0, np.float32)

        # flashlight cone in screen space
        fl = cam.get('flashlight', self.s.get('flashlight'))
        if fl is True:
            fl = {}
        if fl is not None and fl is not False:
            yy, xx = np.mgrid[0:H, 0:W]
            rr = np.hypot((xx - W / 2) / (W / 2), (yy - horizon) / (W / 2)) / float(fl.get('radius', 0.35))
            cone = np.clip(1 - rr ** 2, 0, 1) ** 1.2 * float(fl.get('intensity', 1.2))
            cone += np.clip(1 - rr / 2.2, 0, 1) * 0.12 * float(fl.get('intensity', 1.2))
            fl_col = np.array(fl.get('color', [1.0, 0.95, 0.8]), np.float32)
            fl_range = float(fl.get('range', 5.0))
        else:
            cone = None

        def flash(rows, cols, dist):
            if cone is None:
                return 0.0
            return (cone[rows, cols] / (1 + (dist / fl_range) ** 2))[..., None] * fl_col[None, :]

        # --- sky
        sky_name = self.s.get('sky', 'night')
        sky_rows = int(max(1, math.ceil(horizon)))
        if sky_name:
            pano_w = int(round(W * 2 * math.pi / fov))
            # a void floor shows sky under the horizon too: stars in space, cloud far below otherwise
            below = max(2, H - sky_rows + 2) if w.void.any() else 0
            key = (pano_w, max(sky_rows, H // 2), round(proj, 3), below)
            if key not in self._skies:  # identical for every shot that shares a lens and pitch
                self._skies[key] = assets.make_sky(sky_name, pano_w, key[1], skyline=self.s.get('skyline'),
                                                   proj=proj, discs=self.discs, objects=self.sky_objects,
                                                   below=below)
            pano = self._skies[key]
            ph = key[1]
            ang_cols = (np.arctan2(rdy, rdx) % (2 * math.pi)) / (2 * math.pi) * pano_w
            ang_cols = ang_cols.astype(int) % pano_w
            rows = np.arange(H) if below else np.arange(min(H, sky_rows + 2))
            pr = np.clip(ph - (horizon - rows) - 1, 0, pano.shape[0] - 1).astype(int)
            img[rows] = pano[pr][:, ang_cols]
            if self.fog_c is not None and self.s.get('fog_sky', True) and self.vol is None:
                k = float(self.s['fog'].get('sky_mix', 0.35))
                img[rows] = img[rows] * (1 - k) + self.fog_c * k
        else:
            img[:] = 0

        # --- floors and ceilings
        # Cells with a "drop" (water, pits) sit below z=0, so the floor is not one plane any
        # more: render one pass per distinct depth, deepest first, letting nearer planes win.
        ys = np.arange(H)
        frows = ys[ys + 0.5 > horizon + 0.5]
        crows = ys[ys + 0.5 < horizon - 0.5]
        drops = sorted({float(v) for v in np.unique(w.drop[~w.void]) if v > 1e-6}, reverse=True)
        drop0 = None
        if drops and frows.size:
            # where the un-sunken plane lands, so a deep pass can fill the submerged bank
            D0 = (camz * proj / (frows + 0.5 - horizon))[:, None] * np.ones((1, W))
            m0x = np.clip(np.floor(px + rdx[None, :] * D0).astype(int), 0, w.mw - 1)
            m0y = np.clip(np.floor(py + rdy[None, :] * D0).astype(int), 0, w.mh - 1)
            drop0 = np.where(w.void[m0y, m0x], 0.0, w.drop[m0y, m0x])

        for kind, dr in [('floor', v) for v in drops] + [('floor', 0.0), ('ceil', 0.0)]:
            if kind == 'floor':
                rows = frows
                if rows.size == 0:
                    continue
                d = (camz + dr) * proj / (rows + 0.5 - horizon)
                z = -dr
                tid_grid = w.floor_tid
            else:
                rows = crows
                if rows.size == 0:
                    continue
                d = (w.ceil_h - camz) * proj / (horizon - rows - 0.5)
                z = w.ceil_h
                tid_grid = w.ceil_tid
            D = d[:, None] * np.ones((1, W))
            wx = px + rdx[None, :] * D
            wy = py + rdy[None, :] * D
            mx, my = np.floor(wx).astype(int), np.floor(wy).astype(int)
            if kind == 'floor':
                # past the map edge the ground carries on as the nearest edge cell - its floor and
                # its drop alike - so an open vista meets its skyline instead of a black band
                mx, my = np.clip(mx, 0, w.mw - 1), np.clip(my, 0, w.mh - 1)
            inb = (mx >= 0) & (my >= 0) & (mx < w.mw) & (my < w.mh)
            tids = np.full(D.shape, -1, np.int32)
            tids[inb] = tid_grid[my[inb], mx[inb]]
            valid = tids >= 0
            lip = None
            if kind == 'floor':
                cdrop = np.zeros(D.shape, np.float32)
                cdrop[inb] = w.drop[my[inb], mx[inb]]
                if dr > 0:
                    # the far bank seen below the waterline: only the deepest pass fills it
                    lip = (valid & (cdrop <= 1e-6) & (drop0 > 1e-6)) if dr == drops[0] \
                        else np.zeros(D.shape, bool)
                    valid = valid & ((np.abs(cdrop - dr) < 1e-6) | lip)
                    if lip.any():   # a bank's sunken edge shows the cell's `side` texture, if it has one
                        st = w.side_tid[my[lip], mx[lip]]
                        tids[lip] = np.where(st >= 0, st, tids[lip])
                else:
                    valid = valid & (cdrop <= 1e-6)
            if not valid.any():
                continue
            u = ((wx * T) % T).astype(int)
            v = ((wy * T) % T).astype(int)
            alb = np.zeros(D.shape + (3,), np.float32)
            em = np.zeros(D.shape, np.float32)
            for t in np.unique(tids[valid]):
                m = tids == t
                rgb, e = w.tex[t]
                alb[m] = rgb[v[m], u[m]]
                if e is not None:
                    em[m] = e[v[m], u[m]]
            if kind == 'floor' and w.wet.any():
                alb *= (1 - 0.3 * w.wet[my, mx])[..., None]       # wet ground is darker
            if self.sn is not None:
                var = self.surface_variation(wx[valid], wy[valid], 0.0 if kind == 'floor' else 3.1)
                alb[valid] *= (1 + soft_swing(self.tex_amount[tids[valid]] * var))[:, None]
            rk = None
            if kind == 'floor' and self.reflect_k > 0:
                rk = np.where(valid, w.reflect[my, mx], 0.0).astype(np.float32)
            for dcl in (floor_decals if kind == 'floor' else ceil_decals):
                if kind == 'floor' and abs(dcl['drop'] - dr) > 1e-6:
                    continue
                self._blend_plane_decal(alb, em, wx, wy, d, valid, dcl, rk)
            if lip is not None and lip.any():
                alb[lip] *= 0.45  # bank below the waterline reads as shadowed, not lit
            dyn = sample_lm(self.lm, self.lres, wx, wy)
            dist = D * rlen[None, :]
            rr, cc = np.meshgrid(rows, np.arange(W), indexing='ij')
            sun = self.sun_at(wx, wy, np.full(D.shape, z), self.lam_up) if kind == 'floor' and self.suns else 0.0
            col = self.shade(alb, dyn, np.full(D.shape, z), dist, em, flash(rr, cc, dist), sun)
            sub = img[rows]
            sub[valid] = col[valid]
            img[rows] = sub
            dsub = depth[rows]
            dsub[valid] = D[valid]
            depth[rows] = dsub
            if rk is not None and rk.any():
                k = valid & (rk > 0)
                rsub, dsub2 = refl[rows], refl_depth[rows]
                rsub[k] = rk[k] * self.reflect_k
                dsub2[k] = dsub[k]
                refl[rows], refl_depth[rows] = rsub, dsub2

        # --- walls: a vectorised DDA over all columns. It collects a face at every rising edge, and
        # the top of every block lower than the eye, so steps, altars and kerbs read as solid.
        mapx = np.full(W, int(math.floor(px)))
        mapy = np.full(W, int(math.floor(py)))
        with np.errstate(divide='ignore'):
            ddx = np.where(rdx == 0, 1e30, np.abs(1 / rdx))
            ddy = np.where(rdy == 0, 1e30, np.abs(1 / rdy))
        stepx = np.where(rdx < 0, -1, 1)
        stepy = np.where(rdy < 0, -1, 1)
        sdx = np.where(rdx < 0, (px - mapx) * ddx, (mapx + 1 - px) * ddx)
        sdy = np.where(rdy < 0, (py - mapy) * ddy, (mapy + 1 - py) * ddy)
        inside = 0 <= mapx[0] < w.mw and 0 <= mapy[0] < w.mh
        cy0, cx0 = (int(mapy[0]), int(mapx[0])) if inside else (0, 0)
        # the height a new wall has to rise above to be seen; see-through cells never raise it
        prev_h = np.full(W, w.solid_h[cy0, cx0] if inside else 0.0, np.float32)
        prev_see = np.full(W, bool(w.see[cy0, cx0]) if inside else False)
        # drop of the cell each ray is leaving: a wall rising out of sunken water starts below z=0
        prev_d = np.full(W, w.drop[cy0, cx0] if inside else 0.0, np.float32)
        prev_void = np.full(W, bool(w.void[cy0, cx0]) if inside else False)
        active = np.ones(W, bool)
        max_dist = float(self.s.get('max_distance', 64))
        hits = []  # ('face' | 'top', nearest distance, column, ...), drawn far to near
        if inside and not w.see[cy0, cx0] and 1e-6 < w.height[cy0, cx0] < camz - 1e-6:
            # standing on a low block: its own top runs from under the camera to its far edge
            exit0 = np.minimum(sdx, sdy)
            hits += [('top', 0.0, c, cx0, cy0, float(w.height[cy0, cx0]), float(exit0[c])) for c in range(W)]
        for _ in range(int(2 * (w.mw + w.mh)) + 4):
            if not active.any():
                break
            xs = sdx < sdy
            dist = np.where(xs, sdx, sdy)            # where each ray enters its next cell...
            mapx = np.where(xs & active, mapx + stepx, mapx)
            mapy = np.where(~xs & active, mapy + stepy, mapy)
            sdx = np.where(xs & active, sdx + ddx, sdx)
            sdy = np.where(~xs & active, sdy + ddy, sdy)
            exitd = np.minimum(sdx, sdy)             # ...and where it leaves it
            inb = (mapx >= 0) & (mapy >= 0) & (mapx < w.mw) & (mapy < w.mh)
            active &= inb & (dist < max_dist)
            cyc, cxc = np.clip(mapy, 0, w.mh - 1), np.clip(mapx, 0, w.mw - 1)
            hgt = np.where(inb, w.height[cyc, cxc], 0)
            see_c = inb & w.see[cyc, cxc]
            # a run of see-through cells shows only the face the ray enters it by, never inner faces
            rise = active & (hgt > prev_h + 1e-6) & (dist > 1e-4) & ~(see_c & prev_see)
            low = active & ~see_c & (hgt > 1e-6) & (hgt < camz - 1e-6)
            for c in np.nonzero(rise)[0]:
                # a wall or fence at the brink stops at the ground; the cliff under it is the bank
                below = 0.0 if prev_void[c] else prev_d[c]
                hits.append(('face', dist[c], c, int(not xs[c]), mapx[c], mapy[c], hgt[c], below,
                             bool(see_c[c])))
            vo = inb & w.void[cyc, cxc]
            # climbing out of a void onto anything solid: the edge of the ground is a cliff
            bank = active & prev_void & ~vo & (dist > 1e-4)
            for c in np.nonzero(bank)[0]:
                lvl = float(w.drop[cyc[c], cxc[c]]) if hgt[c] <= 1e-6 else 0.0
                hits.append(('bank', dist[c], c, int(not xs[c]), mapx[c], mapy[c], lvl))
            for c in np.nonzero(low)[0]:
                hits.append(('top', dist[c], c, mapx[c], mapy[c], hgt[c], exitd[c]))
            top = horizon - (hgt - camz) * proj / np.maximum(dist, 1e-4)
            bot = horizon + camz * proj / np.maximum(dist, 1e-4)
            # a solid wall that fills the whole column hides everything behind it
            active &= ~(rise & ~see_c & (top <= 0) & (bot >= H))
            prev_h = np.where(active & ~see_c, hgt, prev_h)
            prev_see = np.where(active, see_c, prev_see)
            prev_d = np.where(active, np.where(inb, w.drop[cyc, cxc], 0), prev_d)
            prev_void = np.where(active, vo, prev_void)

        # far to near; at the same distance a block's top goes down before its face
        hits.sort(key=lambda h: (-h[1], h[0] == 'face'))
        for hit in hits:
            if hit[0] == 'top':
                # the top of a low block: a patch of floor at the block's height, between where the
                # ray crosses into the cell and where it leaves, with its own per-row depth
                _, din, c, mx, my, hgt, dout = hit
                lift = camz - hgt
                far_row = horizon + lift * proj / max(dout, 1e-4)
                near_row = horizon + lift * proj / din if din > 1e-6 else H + 1
                y0, y1 = max(0, int(math.ceil(far_row - 0.5))), min(H, int(math.ceil(near_row - 0.5)))
                if y1 <= y0:
                    continue
                rows = np.arange(y0, y1)
                dd = lift * proj / (rows + 0.5 - horizon)
                tx, ty = px + rdx[c] * dd, py + rdy[c] * dd
                tid = w.floor_tid[my, mx]
                rgb, em = w.tex[tid]
                tu, tv = ((tx * T) % T).astype(int), ((ty * T) % T).astype(int)
                alb = rgb[tv, tu]
                e = em[tv, tu] if em is not None else None
                if self.sn is not None:
                    var = self.surface_variation(tx, ty, 5.3)
                    alb = alb * (1 + soft_swing(self.tex_amount[tid] * var))[:, None]
                ed = dd * rlen[c]
                zt = np.full(len(rows), hgt)
                sun = self.sun_at(tx, ty, zt, self.lam_up) if self.suns else 0.0
                colr = self.shade(alb, sample_lm(self.lm, self.lres, tx, ty), zt, ed, e,
                                  flash(rows, np.full(len(rows), c), ed), sun)
                img[y0:y1, c] = colr
                depth[y0:y1, c] = dd
                continue
            if hit[0] == 'bank':
                _, dist, c, side, mx, my, lvl = hit
                wallx = py + dist * rdy[c] if side == 0 else px + dist * rdx[c]
                jag = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(wallx * 5.3 + mx * 1.7 + my * 2.9)
                                   * math.cos(wallx * 2.2 - my * 0.7))
                top = horizon + (camz + lvl) * proj / dist
                bot = horizon + (camz + VOID_DEPTH * jag) * proj / dist
                y0, y1 = max(0, int(math.ceil(top - 0.5))), min(H, int(math.ceil(bot - 0.5)))
                tid = w.side_tid[my, mx] if w.side_tid[my, mx] >= 0 else w.floor_tid[my, mx]
                if y1 <= y0 or tid < 0:
                    continue
                rows = np.arange(y0, y1)
                keep = depth[y0:y1, c] > dist
                if not keep.any():
                    continue
                z = (horizon - (rows + 0.5)) * dist / proj + camz
                rgb, em = w.tex[tid]
                u = min(T - 1, int((wallx - math.floor(wallx)) * T))
                v = ((1 - (z % 1.0)) * T).astype(int).clip(0, T - 1)
                alb = rgb[v, u] * (0.85 - 0.55 * np.clip(-z / VOID_DEPTH, 0, 1))[:, None]
                if side == 1:
                    alb = alb * 0.78
                hx = px + rdx[c] * dist - rdx[c] / rlen[c] * 0.04
                hy = py + rdy[c] * dist - rdy[c] / rlen[c] * 0.04
                ed = np.full(len(rows), dist * rlen[c])
                colr = self.shade(alb, np.repeat(sample_lm(self.lm, self.lres, np.array([hx]), np.array([hy])),
                                                 len(rows), 0), z, ed, None,
                                  flash(rows, np.full(len(rows), c), ed), 0.0)
                img[rows[keep], c] = colr[keep]
                depth[rows[keep], c] = dist
                continue
            _, dist, c, side, mx, my, hgt, below, see_hit = hit
            top = horizon - (hgt - camz) * proj / dist
            # a wall standing in sunken water carries on down to the surface instead of
            # stopping at z=0 and leaving the floor pass to guess what fills the gap
            bot = horizon + (camz + below) * proj / dist
            y0, y1 = max(0, int(math.ceil(top - 0.5))), min(H, int(math.ceil(bot - 0.5)))
            if y1 <= y0:
                continue
            if side == 0:
                wallx = py + dist * rdy[c]
            else:
                wallx = px + dist * rdx[c]
            uf_raw = wallx - math.floor(wallx)  # always measured along +x / +y, so decals are predictable
            uf = uf_raw
            if (side == 0 and rdx[c] < 0) or (side == 1 and rdy[c] > 0):
                uf = 1 - uf
            u = min(T - 1, int(uf * T))
            rows = np.arange(y0, y1)
            z = (horizon - (rows + 0.5)) * dist / proj + camz
            v = ((1 - (z % 1.0)) * T).astype(int).clip(0, T - 1)
            stack = w.stacks.get((my, mx))
            solid = None  # rows of a see-through wall that are actually there
            if stack is None:
                tid = w.wall_tid[my, mx]
                rgb, em = w.tex[tid]
                alb = rgb[v, u]
                e = em[v, u] if em is not None else None
                wall_amt = self.tex_amount[tid]
                if see_hit and w.tex_alpha[tid] is not None:
                    solid = w.tex_alpha[tid][v, u] > 0.5
            else:
                storey = np.clip(np.floor(z).astype(int), 0, len(stack) - 1)
                alb = np.zeros((len(rows), 3), np.float32)
                e = np.zeros(len(rows), np.float32)
                if see_hit:
                    solid = np.ones(len(rows), bool)
                for k in np.unique(storey):
                    m = storey == k
                    rgb, em = w.tex[stack[k]]
                    alb[m] = rgb[v[m], u]
                    if em is not None:
                        e[m] = em[v[m], u]
                    if see_hit and w.tex_alpha[stack[k]] is not None:
                        solid[m] = w.tex_alpha[stack[k]][v[m], u] > 0.5
                # a facade can change material per storey, so the amount varies down the column
                wall_amt = self.tex_amount[np.asarray(stack, np.int32)[storey]]
            if below > 1e-6:
                under = (z < -1e-6) & (depth[y0:y1, c] <= dist)
                if under.any():
                    solid = ~under if solid is None else solid & ~under
            if solid is not None and not solid.any():
                continue
            if self.sn is not None:
                # one key per wall plane, so a long wall varies continuously but the
                # two orientations and the far side of a corridor never match
                perp = round(px + rdx[c] * dist) if side == 0 else round(py + rdy[c] * dist)
                var = self.surface_variation(np.full(len(rows), wallx), z, side * 7.0 + perp * 1.31)
                # wall_amt is a scalar for a plain wall, one value per row for a stacked facade
                alb = alb * (1 + soft_swing(wall_amt * var))[:, None]
            if w.wall_decals:
                face = ('east' if rdx[c] < 0 else 'west') if side == 0 else \
                       ('south' if rdy[c] < 0 else 'north')
                dcls = w.wall_decals.get((my, mx, face))
                if dcls:
                    e = self._blend_wall_decals(alb, e, dcls, uf_raw, z)
            if side == 1:
                alb = alb * 0.78
            hx = px + rdx[c] * dist - rdx[c] / rlen[c] * 0.04
            hy = py + rdy[c] * dist - rdy[c] / rlen[c] * 0.04
            dyn = sample_lm(self.lm, self.lres, np.array([hx]), np.array([hy]))
            ed = dist * rlen[c]
            sun = 0.0
            if self.suns:
                nx, ny = (-math.copysign(1, rdx[c]), 0.0) if side == 0 else (0.0, -math.copysign(1, rdy[c]))
                sun = self.sun_at(np.full(len(rows), hx), np.full(len(rows), hy), z,
                                  lambda s_: s_['cos'] * max(0.0, nx * s_['ux'] + ny * s_['uy']))
            colr = self.shade(alb, np.repeat(dyn, len(rows), 0), z, np.full(len(rows), ed), e,
                              flash(rows, np.full(len(rows), c), np.full(len(rows), ed)), sun)
            if solid is None:
                img[y0:y1, c] = colr
                depth[y0:y1, c] = dist
            else:
                # holes in a fence write nothing, so whatever lies behind (and its depth) shows
                img[rows[solid], c] = colr[solid]
                depth[rows[solid], c] = dist

        # --- sprites: opaque pass (writes depth), then translucent/additive far-to-near (no depth writes)
        inv = 1.0 / (plx * dy - dx * ply)
        defs = self.s.get('sprite_defs', {})
        placed = []
        self.anchors = {}
        for sp in (self.s.get('sprites', []) + self.w.scatter_sprites + self.w.fringe_sprites
                   + cam.get('extra_sprites', [])):
            sp = {**assets.sprite_defaults(sp['type'], defs), **sp}
            if sp.get('glass') and int(sp.get('planes', 0)) <= 0:
                sp['planes'] = 1                  # a pane of glass is flat: it stands as a card
            sx, sy = float(sp['x']) - px, float(sp['y']) - py
            tx = inv * (dy * sx - dx * sy)
            ty = inv * (-ply * sx + plx * sy)
            if int(sp.get('planes', 0)) > 0:
                # a card can reach into view with its centre behind the camera
                reach = max(float(sp.get('length', 0.0)), float(sp.get('scale', 1.0)) * 2.0) / 2 + 0.5
                if ty > -reach:
                    placed.append((max(ty, 0.05), tx, sp))
            elif ty > 0.05:
                placed.append((ty, tx, sp))
        translucent = lambda sp: sp.get('blend', 'alpha') != 'alpha' or float(sp.get('opacity', 1)) < 1
        glass = sorted([p for p in placed if p[2].get('glass')], key=lambda s: -s[0])
        placed = [p for p in placed if not p[2].get('glass')]
        opaque = sorted([p for p in placed if not translucent(p[2])], key=lambda s: -s[0])
        trans = sorted([p for p in placed if translucent(p[2])], key=lambda s: -s[0])
        self._named = {}
        rays = (rdx, rdy, rlen)
        for ty, tx, sp in opaque + trans:
            if int(sp.get('planes', 0)) > 0:
                self._draw_planes(img, depth, ty, tx, sp, defs, horizon, proj, camz, flash, translucent(sp), rays)
            else:
                self._draw_sprite(img, depth, ty, tx, sp, defs, horizon, proj, camz, pl, flash, translucent(sp))
        self.sprite_stats = {}
        for sid, n in self._named.items():
            vis, lum = 0.0, 0.0
            if n['box'] is not None:                 # what is left once everything nearer is drawn
                y0_, y1_, x0_, x1_, solid = n['box']   # (glass comes after: a fish in a tank is seen)
                seen = solid & (depth[y0_:y1_, x0_:x1_] >= n['ty'] - 1e-3)
                vis = float(seen.sum())
                if vis:
                    lum = float(img[y0_:y1_, x0_:x1_][seen].mean())
            self.sprite_stats[sid] = {'visible': vis, 'area': n['area'], 'height': n['h'], 'brightness': lum}
        if glass:
            self.rays = {'px': px, 'py': py, 'rdx': rdx, 'rdy': rdy, 'rlen': rlen, 'horizon': horizon,
                         'proj': proj, 'camz': camz}
            self._glass_pass(img, depth, glass, defs, horizon, proj, camz, flash, rays)

        if refl.any():
            img = self._reflect(img, depth, refl, refl_depth)
        self.depth = depth
        self.rays = {'px': px, 'py': py, 'rdx': rdx, 'rdy': rdy, 'rlen': rlen, 'horizon': horizon,
                     'proj': proj, 'camz': camz}
        return np.clip(img, 0, 1)

    def _reflect(self, img, depth, refl, refl_depth):
        """Mirror the frame into reflective floor pixels, column by column.

        A pixel that still shows the reflective floor it was drawn as (nothing nearer covered it)
        mirrors whatever stands just above its run in that column: a wall base, a boat on the
        water, a lamp post's foot, or the horizon for open water. Screen-space, so it can only
        mirror what is on screen - which at a grazing angle across water is nearly everything.
        """
        H, W = depth.shape
        ss = max(1, W // self.W) if self.W else 1
        mask = (refl > 0) & (depth == refl_depth)
        if not mask.any():
            return img
        rows = np.arange(H)[:, None]
        # the last row above each pixel that is not part of its reflective run: the mirror line
        last = np.maximum.accumulate(np.where(mask, -1, rows * np.ones((1, W), int)), axis=0)
        src = 2 * last + 1 - rows
        # a ripple: rows shimmer sideways a pixel or two, more toward the camera
        amp = self.ripple * ss * (0.6 + 1.4 * np.clip((rows - H / 2) / (H / 2), 0, 1))
        cols = np.arange(W)[None, :]
        shift = np.round(amp * np.sin(rows * 0.9 / ss + cols * 0.07 / ss)).astype(int)
        sc = np.clip(cols + shift, 0, W - 1)
        ok = mask & (last >= 0)
        # a short vertical smear: real wet ground and water stretch reflections into streaks
        s0 = np.clip(src, 0, H - 1)
        mirrored = (0.5 * img[s0, sc] + 0.25 * img[np.clip(s0 - 2 * ss, 0, H - 1), sc]
                    + 0.25 * img[np.clip(s0 + 2 * ss, 0, H - 1), sc])
        # stronger at a grazing angle (far away), weaker looking straight down
        k = refl * (0.55 + 0.45 * (1 - np.exp(-np.maximum(refl_depth, 0) / 4.0)))
        # close to the camera the mirrored point is above the top of the frame; what is up there
        # is mostly sky, so those pixels take the top row's colour as a fainter sheen
        k = np.where(src < 0, k * 0.45, k)
        k = np.where(ok, np.clip(k, 0, 1), 0)[..., None]
        # lights glint: anything bright in the reflection comes through harder than the rest
        glint = np.maximum(mirrored - 0.45, 0) * 0.9
        return img * (1 - k) + (mirrored * 0.85 + glint) * k

    def sprite_view(self, sp):
        """'back' when a sprite with a `facing` has its back to the camera (or `view` says so)."""
        v = sp.get('view')
        if v in ('front', 'back'):
            return v
        if 'facing' not in sp:
            return 'front'
        to_cam = math.degrees(math.atan2(self._py - float(sp['y']), self._px - float(sp['x'])))
        off = (to_cam - float(sp['facing']) + 180.0) % 360.0 - 180.0
        return 'back' if abs(off) > 90.0 else 'front'

    def _draw_sprite(self, img, depth, ty, tx, sp, defs, horizon, proj, camz, pl, flash, is_trans):
        W, H = self.W, self.H
        rgba, em = assets.get_sprite(sp['type'], defs, self.sprite_view(sp))
        th, tw = rgba.shape[:2]
        hs = float(sp.get('scale', 1.0))
        # a sprite rests on the surface under it: a boat on sunken water, a candle on an altar
        zb = float(sp.get('z', 0.0)) + self.w.base_z(float(sp['x']), float(sp['y']))
        ph = hs * proj / ty
        pw = ph * tw / th * float(sp.get('stretch', 1.0))
        scx = (tx / ty + 1) * W / 2  # screen centre column
        ytop = horizon - (zb + hs - camz) * proj / ty
        if 'id' in sp:
            self.anchors[sp['id']] = {'x': scx, 'top': ytop, 'w': pw, 'h': ph, 'depth': ty,
                                      'visible': -pw < scx < W + pw and ytop + ph > 0 and ytop < H}
            self._named[sp['id']] = {'ty': ty, 'h': ph, 'area': float((rgba[..., 3] > 0.5).mean()) * pw * ph,
                                     'box': None}
        x0, x1 = int(math.floor(scx - pw / 2)), int(math.ceil(scx + pw / 2))
        y0, y1 = int(math.floor(ytop)), int(math.ceil(ytop + ph))
        cx0, cx1 = max(0, x0), min(W, x1)
        cy0, cy1 = max(0, y0), min(H, y1)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        cols = np.arange(cx0, cx1)
        rows = np.arange(cy0, cy1)
        uu = ((cols + 0.5 - (scx - pw / 2)) / pw * tw).astype(int).clip(0, tw - 1)
        if sp.get('flip'):
            uu = tw - 1 - uu
        vv = ((rows + 0.5 - ytop) / ph * th).astype(int).clip(0, th - 1)
        wob = float(sp.get('wobble', 0))
        if wob:
            # per-texel-row sideways sway, stronger toward the bottom (ghost tails, flames, heat)
            phase = float(sp.get('phase', sp['x'] * 3.1 + sp['y'] * 1.7))
            off = np.round(wob * (vv / th + 0.2) * np.sin(vv * 0.55 + phase)).astype(int)
            U = (uu[None, :] + off[:, None]).clip(0, tw - 1)
            block = rgba[vv[:, None], U]
            emb = em[vv[:, None], U]
        else:
            block = rgba[np.ix_(vv, uu)]
            emb = em[np.ix_(vv, uu)]
        dsub = depth[cy0:cy1, cx0:cx1]
        alpha = block[..., 3] * float(sp.get('opacity', 1.0))
        if not is_trans:
            alpha = (alpha > 0.5).astype(np.float32)
        mask = (alpha > 0.02) & (ty < dsub)
        if 'id' in sp:
            self._named[sp['id']]['box'] = (cy0, cy1, cx0, cx1, alpha > 0.5)
        if not mask.any():
            return
        dyn = sample_lm(self.lm, self.lres, np.array([float(sp['x'])]), np.array([float(sp['y'])]))[0]
        zz = (horizon - (rows + 0.5)) * ty / proj + camz
        Z = np.repeat(zz[:, None], len(cols), 1)
        ed = ty * math.hypot(1, tx / ty * pl)
        rr, cc = np.meshgrid(rows, cols, indexing='ij')
        emm = np.maximum(emb, 1.0 if sp.get('fullbright') else 0.0)
        tint = np.array(sp.get('tint', [1, 1, 1]), np.float32)
        sun = 0.0
        if self.suns:
            fx, fy = self._fx, self._fy
            sun = self.sun_at(np.full(Z.shape, float(sp['x'])), np.full(Z.shape, float(sp['y'])), Z,
                              lambda s_: s_['sin'] * 0.5 + s_['cos'] * 0.6 * max(0.2, -(fx * s_['ux'] + fy * s_['uy'])))
        colr = self.shade(block[..., :3] * tint, np.broadcast_to(dyn, block.shape[:2] + (3,)), Z,
                          np.full(Z.shape, ed), emm, flash(rr, cc, np.full(Z.shape, ed)), sun)
        sub = img[cy0:cy1, cx0:cx1]
        a = (alpha * mask)[..., None]
        if sp.get('blend') == 'additive':
            sub += colr * a
        else:
            sub[:] = sub * (1 - a) + colr * a
        if not is_trans:
            dsub[mask] = ty
        aura = sp.get('aura')
        if aura:
            self._aura(img, depth, alpha * (ty < dsub), cx0, cy0, ty, aura, pw)

    @staticmethod
    def plane_quads(sp, rgba):
        """The vertical quads a planar sprite stands as, each (x0, y0, x1, y1, repeats).

        `planes` 1 is a single card across `angle`; 2 crosses two at right angles; 3 is a star of
        three 60 degrees apart, dividing the ground round the sprite into sixths. Without an
        `angle` each sprite takes one from its position, so a bed of ferns is not all aligned.
        A card with a `length` repeats its image along it, every image-width.
        """
        th, tw = rgba.shape[:2]
        x, y = float(sp['x']), float(sp['y'])
        width = float(sp.get('scale', 1.0)) * tw / th * float(sp.get('stretch', 1.0))
        n = max(1, min(3, int(sp.get('planes', 1))))
        length = float(sp.get('length', width))
        a0 = math.radians(float(sp['angle']) if 'angle' in sp else (x * 137.508 + y * 61.803) % 180.0)
        out = []
        for k in range(n):
            a = a0 + k * math.pi / n
            hx, hy = math.cos(a) * length / 2, math.sin(a) * length / 2
            out.append((x - hx, y - hy, x + hx, y + hy, length / max(width, 1e-6)))
        return out

    def _glass_pass(self, img, depth, glass, defs, horizon, proj, camz, flash, rays):
        """Glass, after all the geometry and sprites, far to near. Each pane shows what is behind
        it - by default through the finished frame shrunk to half size and blown back up without
        smoothing, a cheap blur - tinted, and mixed with the pane's own faint reflection.

        Volumetric fog is laid over the finished frame at the depth of the glass, so it stops at
        the pane - right for a window onto space. A pane with `fog` lets it carry on behind: the
        water of a tank, the mist past a window. For those the frame without glass is fogged at
        its own depth, and each such pane leaves in self._glass_fix the difference between that,
        seen through the pane, and what fogging the pane at its own depth would give."""
        behind = {}
        fogged = None
        if self.vol is not None and any(glass_spec(sp['glass'])['fog'] for _, _, sp in glass):
            self._march(depth.shape, self._ss)
            H, W = depth.shape
            Ts, Ls = self._fog_px(np.arange(H)[:, None], np.arange(W)[None, :], depth)
            fogged = img * Ts[..., None] + Ls
            self._glass_fix = np.zeros_like(img)
        for ty, tx, sp in glass:
            g = glass_spec(sp['glass'])
            if g['blur'] not in behind:            # made once per blur, from the frame without glass
                k = 2 ** g['blur'] * getattr(self, '_ss', 1)
                blur = (lambda a: frost(a, k)) if g['blur'] > 0 else (lambda a: a.copy())
                behind[g['blur']] = (blur(img), None if fogged is None else blur(fogged))
            back, fogback = behind[g['blur']]
            self._draw_planes(img, depth, ty, tx, sp, defs, horizon, proj, camz, flash, False, rays,
                              glass=(g, back, fogback if g['fog'] else None))

    def _draw_planes(self, img, depth, ty, tx, sp, defs, horizon, proj, camz, flash, is_trans, rays, glass=None):
        """A planar sprite: each of its quads is drawn like a thin wall at the sprite stage.

        Every screen column intersects the quad on its own, so the image is foreshortened,
        depth-tested per pixel against everything drawn so far (and the other quads of the same
        cross), and lit by the light map and the sun at its own point along the card.
        """
        W, H = self.W, self.H
        rdx, rdy, rlen = rays
        px, py = self._px, self._py
        rgba, em = assets.get_sprite(sp['type'], defs, self.sprite_view(sp))
        th, tw = rgba.shape[:2]
        zb = float(sp.get('z', 0.0)) + self.w.base_z(float(sp['x']), float(sp['y']))
        hs = float(sp.get('scale', 1.0))
        u0 = float(sp.get('u0', 0.0))
        opacity = float(sp.get('opacity', 1.0))
        tint = np.array(sp.get('tint', [1, 1, 1]), np.float32)
        additive = sp.get('blend') == 'additive'
        named = 'id' in sp
        if named:
            ph = hs * proj / ty
            pw = ph * tw / th
            scx = (tx / ty + 1) * W / 2
            ytop = horizon - (zb + hs - camz) * proj / ty
            self.anchors[sp['id']] = {'x': scx, 'top': ytop, 'w': pw, 'h': ph, 'depth': ty,
                                      'visible': -pw < scx < W + pw and ytop + ph > 0 and ytop < H}
            self._named[sp['id']] = {'ty': ty, 'h': ph, 'area': float((rgba[..., 3] > 0.5).mean()) * pw * ph,
                                     'box': None}
            seen = np.zeros((H, W), bool)
        for x0, y0, x1, y1, rep_ in self.plane_quads(sp, rgba):
            ex, ey = x1 - x0, y1 - y0
            denom = rdx * ey - rdy * ex
            wx0, wy0 = x0 - px, y0 - py
            with np.errstate(divide='ignore', invalid='ignore'):
                t = (wx0 * ey - wy0 * ex) / denom          # depth along each column's ray
                s_ = (wx0 * rdy - wy0 * rdx) / denom       # where along the quad it lands, 0..1
            hit = (np.abs(denom) > 1e-9) & (t > 0.05) & (s_ >= 0) & (s_ <= 1)
            cols = np.nonzero(hit)[0]
            if cols.size == 0:
                continue
            t, s_ = t[cols], s_[cols]
            top = horizon - (zb + hs - camz) * proj / t
            bot = horizon - (zb - camz) * proj / t
            r0, r1 = max(0, int(math.floor(top.min()))), min(H, int(math.ceil(bot.max())))
            if r1 <= r0:
                continue
            rows = np.arange(r0, r1)
            v = (rows[:, None] + 0.5 - top[None, :]) / (bot - top)[None, :]
            inside = (v >= 0) & (v < 1)
            uu = u0 + s_ * rep_
            uu = ((uu - np.floor(uu)) * tw).astype(int).clip(0, tw - 1)
            if sp.get('flip'):
                uu = tw - 1 - uu
            vv = (v * th).astype(int).clip(0, th - 1)
            block = rgba[vv, uu[None, :]]
            alpha = block[..., 3] * opacity
            if not is_trans:
                alpha = (alpha > 0.5).astype(np.float32)
            dsub = depth[r0:r1, cols]
            mask = inside & (alpha > 0.02) & (t[None, :] < dsub)
            rv = None
            if sp.get('reveal') and glass is None and not is_trans:
                rv = self._reveal(sp, rgba, (x0, y0, x1, y1, rep_), rows, cols, t, s_, v, vv, uu,
                                  inside & (block[..., 3] < 0.5) & (t[None, :] < dsub), dsub,
                                  horizon, proj, camz, flash, rays)
            if not mask.any() and rv is None:
                continue
            wx, wy = px + rdx[cols] * t, py + rdy[cols] * t
            dyn = sample_lm(self.lm, self.lres, wx, wy)
            Z = (horizon - (rows[:, None] + 0.5)) * t[None, :] / proj + camz
            ed = np.broadcast_to((t * rlen[cols])[None, :], Z.shape)
            rr, cc = np.meshgrid(rows, cols, indexing='ij')
            emm = np.maximum(em[vv, uu[None, :]], 1.0 if sp.get('fullbright') else 0.0)
            sun = 0.0
            if self.suns:
                n_ = math.hypot(ex, ey) or 1.0
                nx, ny = -ey / n_, ex / n_
                # foliage cards take light on either face: a leaf lets the sun through
                sun = self.sun_at(np.broadcast_to(wx[None, :], Z.shape), np.broadcast_to(wy[None, :], Z.shape), Z,
                                  lambda s2: s2['sin'] * 0.5 + s2['cos'] * 0.6 * max(0.25, abs(nx * s2['ux'] + ny * s2['uy'])))
            colr = self.shade(block[..., :3] * tint, np.broadcast_to(dyn[None, :, :], block.shape[:2] + (3,)), Z,
                              ed, emm, flash(rr, cc, ed), sun)
            a = (alpha * mask)[..., None]
            sub = img[r0:r1, cols]
            if glass is not None:
                # light through the pane, tinted, under the pane's own reflection
                g, back, fogback = glass
                through = back[r0:r1, cols] * g['tint']
                colr = through * (1 - g['opacity']) + colr * g['opacity']
                if self._glass_fix is not None:
                    fix = 0.0
                    if fogback is not None:
                        # the fog behind the pane: what it lets through and adds, less what
                        # fogging the pane at its own depth will make of the view through it
                        Tg, Lg = self._fog_px(np.arange(r0, r1)[:, None], cols[None, :],
                                              np.broadcast_to(t[None, :], (r1 - r0, len(cols))))
                        fix = g['tint'] * (1 - g['opacity']) * (fogback[r0:r1, cols] - Lg
                                                                 - back[r0:r1, cols] * Tg[..., None])
                    self._glass_fix[r0:r1, cols] = self._glass_fix[r0:r1, cols] * (1 - a) + fix * a
            img[r0:r1, cols] = sub + colr * a if additive else sub * (1 - a) + colr * a
            if not is_trans:
                depth[r0:r1, cols] = np.where(mask, t[None, :], dsub)
            if rv is not None:
                ri, ci, rcol, rt = rv
                img[r0 + ri, cols[ci]] = rcol
                depth[r0 + ri, cols[ci]] = rt
            if named:
                seen[r0:r1, cols] |= mask & (alpha > 0.5)
        if named and seen.any():
            ys_, xs_ = np.nonzero(seen)
            y0_, y1_, x0_, x1_ = ys_.min(), ys_.max() + 1, xs_.min(), xs_.max() + 1
            self._named[sp['id']]['box'] = (y0_, y1_, x0_, x1_, seen[y0_:y1_, x0_:x1_])

    def _reveal(self, sp, rgba, quad, rows, cols, t, s_, v, vv, uu, cand, dsub, horizon, proj, camz, flash, rays):
        """The inner sides of a card's openings, for a card with `reveal` (a depth): the card is
        drawn as a slab that thick, so through an opening seen at an angle its far side shows -
        the jamb, the head over it, the sill under it - not whatever stands behind the wall.

        A ray going in through a see-through texel runs on behind the card; if it leaves that
        opening (the run of clear texels it is in, across and down) before it is `reveal` deep,
        it stops on that side. The side takes its colour from the card just past the opening's
        edge, read on round the corner as brickwork turns it, darker the deeper it goes, and its
        light from its own facing: a jamb turned to the sun is lit where the light could come in
        through the opening, and the head and the wall's edges shade the rest. Returns (rows,
        columns, colours, depths) of the pixels it covers, or None.
        """
        ri, ci = np.nonzero(cand)
        if ri.size == 0:
            return None
        x0, y0, x1, y1, rep_ = quad
        rdx, rdy, rlen = rays
        th, tw = rgba.shape[:2]
        hs = float(sp.get('scale', 1.0))
        deep = float(sp['reveal'])
        if id(rgba) not in self._runs or self._runs[id(rgba)][0] is not rgba:
            self._runs[id(rgba)] = (rgba, hole_runs(rgba[..., 3]))
        lft, rgt, top, bot = (r_[vv[ri, ci], uu[ci]] for r_ in self._runs[id(rgba)][1])
        lq = math.hypot(x1 - x0, y1 - y0) or 1.0
        ax, ay = (x1 - x0) / lq, (y1 - y0) / lq           # along the card
        nx, ny = -ay, ax                                   # across it
        c = cols[ci]
        rx, ry = rdx[c], rdy[c]
        k = np.abs(rx * nx + ry * ny)                      # how fast the ray goes in, per unit of t
        flip = -1.0 if sp.get('flip') else 1.0
        tpu = tw * rep_ / lq                               # texels per unit along the card
        du = (rx * ax + ry * ay) * tpu * flip              # texels across, per unit of t
        su = float(sp.get('u0', 0.0)) + s_[ci] * rep_
        uc = (su - np.floor(su)) * tw
        if flip < 0:
            uc = tw - uc
        vc = v[ri, ci] * th
        dv = -(horizon - (rows[ri] + 0.5)) / proj * th / hs   # texels down, per unit of t
        with np.errstate(divide='ignore', invalid='ignore'):
            d_u = np.where(du > 0, (rgt - uc) / du, np.where(du < 0, (lft - uc) / du, np.inf))
            d_v = np.where(dv > 0, (bot - vc) / dv, np.where(dv < 0, (top - vc) / dv, np.inf))
        d = np.maximum(np.minimum(d_u, d_v), 0.0)
        tt = t[ci] + d
        keep = np.nonzero((d * k < deep) & (tt < dsub[ri, ci]))[0]
        if keep.size == 0:
            return None
        ri, ci, c, rx, ry, k, du, dv, d, tt = (a_[keep] for a_ in (ri, ci, c, rx, ry, k, du, dv, d, tt))
        uc, vc, d_u, d_v, lft, rgt, top, bot = (a_[keep] for a_ in (uc, vc, d_u, d_v, lft, rgt, top, bot))
        jamb = d_u <= d_v
        e = d * k                                          # how deep in the side is met
        uh, vh = uc + du * d, vc + dv * d
        fold = np.floor(e * th / hs).astype(int)
        tu = np.where(jamb, np.where(du > 0, rgt + fold, lft - 1 - fold), np.floor(uh).astype(int))
        tv = np.where(jamb, np.floor(vh).astype(int), np.where(dv < 0, top - 1 - fold, bot + fold))
        alb = rgba[tv.clip(0, th - 1), tu.clip(0, tw - 1), :3] * (1 - 0.4 * e / deep)[:, None]
        wx, wy = self._px + rx * tt, self._py + ry * tt
        Z = (horizon - (rows[ri] + 0.5)) * tt / proj + camz
        ed = tt * rlen[c]
        sun = 0.0
        if self.suns:
            go = np.sign(rx * ax + ry * ay)                # the way the ray runs along the card
            cam = -np.sign(rx * nx + ry * ny)              # the side of the card the camera is on

            def lam(s2):
                # a jamb faces back the way the ray came, a sill up, a head down (no sun)
                face = np.where(jamb, s2['cos'] * np.maximum(0.0, -go * (ax * s2['ux'] + ay * s2['uy'])),
                                np.where(dv > 0, s2['sin'], 0.0))
                # follow the light back out to the face of the card: did it come in by this opening?
                out = s2['cos'] * cam * (nx * s2['ux'] + ny * s2['uy'])
                back = e / np.maximum(out, 1e-6)
                uw = uh + s2['cos'] * (ax * s2['ux'] + ay * s2['uy']) * tpu * flip * back
                vw = vh - s2['sin'] * back * th / hs
                return face * ((out > 1e-6) & (uw >= lft) & (uw <= rgt) & (vw >= top) & (vw <= bot))
            sun = self.sun_at(wx, wy, Z, lam)
        col = self.shade(alb, sample_lm(self.lm, self.lres, wx, wy), Z, ed, None, flash(rows[ri], c, ed), sun)
        return ri, ci, col, tt

    def _aura(self, img, depth, alpha, cx0, cy0, ty, aura, pw):
        """Soft additive glow around a sprite's silhouette (ghosts, spirits, magic)."""
        from PIL import ImageFilter
        H, W = img.shape[:2]
        r = max(2, int(float(aura.get('radius', 0.25)) * pw))
        pad = r * 2
        hh, ww = alpha.shape
        canvas = np.zeros((hh + 2 * pad, ww + 2 * pad), np.float32)
        canvas[pad:pad + hh, pad:pad + ww] = alpha
        im = Image.fromarray((canvas * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
        glow = np.asarray(im, np.float32) / 255
        y0, x0 = cy0 - pad, cx0 - pad
        sy0, sx0 = max(0, -y0), max(0, -x0)
        y1, x1 = min(H, y0 + glow.shape[0]), min(W, x0 + glow.shape[1])
        g = glow[sy0:sy0 + (y1 - max(0, y0)), sx0:sx0 + (x1 - max(0, x0))]
        vis = (depth[max(0, y0):y1, max(0, x0):x1] > ty * 0.9)[..., None]
        c = np.array(aura.get('color', [0.6, 0.8, 1.0]), np.float32) * float(aura.get('strength', 0.5))
        img[max(0, y0):y1, max(0, x0):x1] += g[..., None] * c * vis



# ------------------------------------------------------------------ output

def finish(img, scene, effects=(), seed=0):
    """Palette quantise (ordered dither), nearest-neighbour upscale, then display-stage effects."""
    effects = list(effects)
    spec, levels = post.palette_spec(effects, scene)
    arr = post.quantize(img, spec, float(scene.get('dither', 1.0)), levels)
    scale = int(scene.get('scale', 3))
    pim = Image.fromarray(arr, 'RGB')
    out = np.asarray(pim.resize((pim.width * scale, pim.height * scale), Image.NEAREST))
    out = post.apply_display(out, effects, {'scale': scale, 'seed': seed})
    return Image.fromarray(out)


def prepare_shot(scene, cam):
    """Per-shot adjustments: held lights from viewmodels (lantern, torch) and the flashlight item."""
    cam = dict(cam)
    overlays = list(scene.get('overlays', [])) + list(cam.get('overlays', []))
    extra = []
    for ov in overlays:
        if ov.get('type') != 'viewmodel':
            continue
        v = scene.get('viewmodel_defs', {}).get(ov['item']) or icons.VIEWMODELS.get(ov['item'], {})
        if v.get('light') and ov.get('light', True):
            L = {'x': cam['x'], 'y': cam['y'], 'z': 0.55, 'shadows': False, **v['light']}
            if isinstance(ov.get('light'), dict):
                L.update(ov['light'])
            extra.append(L)
        if v.get('flashlight') and 'flashlight' not in cam:
            cam['flashlight'] = True
    if extra:
        ovr = dict(cam.get('overrides', {}))
        ovr['lights'] = list(ovr.get('lights', scene.get('lights', []))) + extra
        cam['overrides'] = ovr
    return cam


def render_shot(scene, i, base=None, report=None):
    """Render shot `i` (0-based) of a scene to a finished PIL image.

    `base` is an optional (World, Renderer) pair for the scene as written; shots without
    `overrides` reuse it, so a many-shot scene builds its lightmap and scatter once.
    """
    shots = scene.get('shots') or [scene['camera']]
    cam = prepare_shot(scene, merge_camera(scene, shots[i]))
    if cam.get('overrides'):
        sc = {**scene, **cam['overrides']}
        rr = Renderer(World(sc), sc)
    else:
        if base is None:
            w = World(scene)
            base = (w, Renderer(w, scene))
        rr = base[1]
    frame = rr.render(cam)
    if report is not None:
        report.extend(rr.last_report)
    return finish(frame, {**scene, **cam.get('overrides', {})}, rr.last_effects, i)


def draw_map(world, scene, cams, path, cell=24):
    """Top-down layout check: walls by height, floors by texture tint, lights, decals, scattered
    props (small olive dots), placed sprites (green squares) and each camera's view cone."""
    scene = world.scene                    # with its prefabs placed
    im = Image.new('RGB', (world.mw * cell, world.mh * cell), (10, 10, 14))
    d = ImageDraw.Draw(im)
    maxh = max(1.0, float(world.height.max()))
    for y in range(world.mh):
        for x in range(world.mw):
            box = [x * cell, y * cell, (x + 1) * cell - 1, (y + 1) * cell - 1]
            if world.height[y, x] > 0:
                g = int(90 + 140 * world.height[y, x] / maxh)
                d.rectangle(box, fill=(g, g // 2 + 20, g // 3 + 10))
            else:
                t = world.floor_tid[y, x]
                c = (world.tex[t][0].mean(axis=(0, 1)) * 140).astype(int) if t >= 0 else (0, 0, 0)
                d.rectangle(box, fill=tuple(int(v) for v in c))
                if world.ceil_tid[y, x] >= 0:
                    d.line([box[0], box[1], box[2], box[3]], fill=(60, 60, 70))
    for L in scene.get('lights', []):
        if L.get('type', 'point') != 'point':
            continue
        lx, ly = L['x'] * cell, L['y'] * cell
        c = tuple(int(min(1, v) * 255) for v in L.get('color', [1, 0.85, 0.6]))
        r = L.get('radius', 4) * cell
        d.ellipse([lx - r, ly - r, lx + r, ly + r], outline=tuple(v // 3 for v in c))
        d.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=c)
    for dcl in world.floor_decals:
        hw, hh = dcl['size'] * cell / 2, dcl['size'] * dcl['dh'] / dcl['dw'] * cell / 2
        dx_, dy_ = dcl['x'] * cell, dcl['y'] * cell
        d.rectangle([dx_ - hw, dy_ - hh, dx_ + hw, dy_ + hh], outline=(150, 118, 84))
    # fringe and scatter first, so the sprites an author placed by hand stay readable on top
    defs = scene.get('sprite_defs', {})

    def planes(sp, colour):
        sp = {**assets.sprite_defaults(sp['type'], defs), **sp}
        if int(sp.get('planes', 0)) <= 0:
            return False
        for x0, y0, x1, y1, _ in Renderer.plane_quads(sp, assets.get_sprite(sp['type'], defs)[0]):
            d.line([x0 * cell, y0 * cell, x1 * cell, y1 * cell], fill=colour)
        return True
    for sp in world.fringe_sprites:
        planes(sp, (64, 110, 60))
    for sp in world.scatter_sprites:
        if not planes(sp, (120, 132, 84)):
            sx, sy = sp['x'] * cell, sp['y'] * cell
            d.rectangle([sx - 1, sy - 1, sx + 1, sy + 1], fill=(120, 132, 84))
    for sp in scene.get('sprites', []):
        planes(sp, (80, 200, 120))
        sx, sy = sp['x'] * cell, sp['y'] * cell
        d.rectangle([sx - 2, sy - 2, sx + 2, sy + 2], fill=(80, 200, 120))
    for i, c in enumerate(cams):
        cx, cy = c['x'] * cell, c['y'] * cell
        a = math.radians(c.get('angle', 0))
        f = math.radians(c.get('fov', 66)) / 2
        L = 5 * cell
        for s in (-1, 1):
            d.line([cx, cy, cx + L * math.cos(a + s * f), cy + L * math.sin(a + s * f)], fill=(120, 160, 255))
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(80, 140, 255))
        d.text((cx + 6, cy - 6), str(i + 1), fill=(255, 255, 255))
    im.save(path)


# Fog keys that switch on the volumetric pass (see Renderer._atmosphere).
FOG_VOLUME_KEYS = ('height', 'ground', 'noise', 'scale', 'glow', 'shafts', 'steps', 'distance', 'anisotropy')

# Every key the renderer reads. Anything else is ignored, which for a hand- or LLM-written file
# almost always means a typo ("ligths", "sprits") that silently drops part of the scene.
SCENE_KEYS = {
    'map', 'legend', 'default', 'camera', 'shots', 'resolution', 'scale', 'ceiling_height', 'sky',
    'ambient', 'lights', 'fog', 'fog_sky', 'sprites', 'sprite_defs', 'flashlight', 'light_levels',
    'scatter', 'grime', 'grime_debris', 'grime_decals', 'surface_noise', 'decals', 'decal_defs',
    'palette', 'auto_levels', 'dither', 'scanlines', 'overbright', 'lightmap_res', 'max_distance',
    'supersample', 'overlays', 'ui', 'post', 'icon_defs', 'viewmodel_defs', 'seed',
    'skyline', 'contact_shadows', 'heights', 'height_unit', 'reflections', 'sky_objects', 'wet',
    'prefabs', 'prefab_defs',
    'title', 'description', 'notes',  # free-form metadata, never read
}
SHOT_KEYS = {'x', 'y', 'angle', 'look_at', 'fov', 'height', 'pitch', 'flashlight', 'overlays', 'overrides',
             'post', 'scanlines', 'seed', 'supersample', 'extra_sprites', 'title', 'description', 'notes'}
CELL_KEYS = {'wall', 'h', 'top', 'floor', 'ceil', 'drop', 'reflect', 'side', 'fringe', 'facade', 'glazed'}
ASSET_EXTS = ('.png', '.ttf', '.otf')


def lint_scene(scene):
    """Warnings for keys the renderer never reads. Keys starting with '_' pass as comments."""
    import difflib
    out = []

    def check(d, known, where):
        if not isinstance(d, dict):
            return
        for k in d:
            if k in known or str(k).startswith('_'):
                continue
            hint = difflib.get_close_matches(str(k), sorted(known), n=1, cutoff=0.7)
            out.append(f"{where}: unknown key {k!r}" + (f" - did you mean {hint[0]!r}?" if hint else ''))

    check(scene, SCENE_KEYS, 'scene')
    check(scene.get('camera'), SHOT_KEYS, 'camera')
    for i, shot in enumerate(scene.get('shots') or []):
        check(shot, SHOT_KEYS, f'shot {i + 1}')
        if isinstance(shot, dict):
            check(shot.get('overrides'), SCENE_KEYS, f'shot {i + 1} overrides')
    for ch, spec in (scene.get('legend') or {}).items():
        check(spec, CELL_KEYS, f'legend {ch!r}')
    for i, pl in enumerate(scene.get('prefabs') or []):
        check(pl, prefabs.PLACEMENT_KEYS, f'prefab {i + 1}')
    return out


def resolve_paths(obj, base):
    """Point relative .png / .ttf paths at the scene file's folder when the file is there.

    Anything not found beside the scene is left untouched, so paths written relative to the
    working directory keep working.
    """
    if isinstance(obj, dict):
        return {k: resolve_paths(v, base) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_paths(v, base) for v in obj]
    if isinstance(obj, str) and obj.lower().endswith(ASSET_EXTS) and not os.path.isabs(obj):
        cand = os.path.join(base, obj)
        if os.path.isfile(cand):
            return cand
    return obj


def load_scene(path):
    """Read a scene file. Always UTF-8: the platform default (cp1252 on Windows) garbles em dashes
    and curly quotes in dialog, and fails outright on some accented capitals."""
    with open(path, encoding='utf-8-sig') as f:
        scene = json.load(f)
    return resolve_paths(scene, os.path.dirname(os.path.abspath(path)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scene')
    ap.add_argument('-o', '--out', default='render.png')
    ap.add_argument('--map', action='store_true', help='also write <out>_map.png top-down view')
    ap.add_argument('--sheet', action='store_true', help='also tile all shots into <out>_sheet.png')
    ap.add_argument('--shot', type=int, help='render only this shot number (1-based)')
    args = ap.parse_args()
    # output paths and warnings go to a pipe in most harnesses; on Windows that pipe is cp1252,
    # which cannot encode every path or key - degrade to escapes rather than crash after rendering
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')

    scene = load_scene(args.scene)
    for warning in lint_scene(scene):
        print(f'warning: {warning}', file=sys.stderr)
    if not scene.get('shots') and not isinstance(scene.get('camera'), dict):
        ap.error('the scene needs a "camera" (or a list of "shots")')
    shots = scene.get('shots') or [scene['camera']]
    if args.shot is not None and not 1 <= args.shot <= len(shots):
        ap.error(f'--shot {args.shot} is out of range: this scene has {len(shots)} shot(s)')
    for i, cam in enumerate(shots):
        c = merge_camera(scene, cam)
        if 'x' not in c or 'y' not in c:
            ap.error(f'shot {i + 1} has no x/y and there is no camera to inherit them from')
    base, ext = os.path.splitext(args.out)
    if not ext:  # PIL picks the format from the extension, and has nothing to go on without one
        ext = '.png'
        args.out = base + ext
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    world = World(scene)
    base_pair = (world, Renderer(world, scene))
    outs = []
    for i in range(len(shots)):
        if args.shot and i + 1 != args.shot:
            continue
        path = args.out if len(shots) == 1 else f"{base}_{i + 1:02d}{ext}"
        notes = []
        img = render_shot(scene, i, base_pair, notes)
        for note in notes:
            print(f'warning: shot {i + 1}: {note}', file=sys.stderr)
        img.save(path)
        outs.append((path, img))
        print(path)
    if args.map:
        mp = base + '_map.png'
        draw_map(world, scene, [merge_camera(scene, c) for c in shots], mp)
        print(mp)
    if args.sheet and len(outs) > 1:
        w, h = outs[0][1].size
        cols = 2
        rows = (len(outs) + 1) // 2
        sheet = Image.new('RGB', (w * cols + 8 * (cols - 1), h * rows + 8 * (rows - 1)), (0, 0, 0))
        for k, (_, im) in enumerate(outs):
            sheet.paste(im, ((k % cols) * (w + 8), (k // cols) * (h + 8)))
        sp = base + '_sheet.png'
        sheet.save(sp)
        print(sp)


if __name__ == '__main__':
    main()

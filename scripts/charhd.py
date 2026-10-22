"""Characters in finer pixels: the text-grid characters drawn at twice the resolution, a little taller.

A character is written as a small text grid (see characters.py) - 16 x 32 for the built-ins. Drawn as it
is, a close shot shows each of its pixels as a big square, much coarser than the walls and props around
it. So before a character becomes a texture its grid goes through a few steps, each keeping its look:

- **taller**: a row of the torso and two of the legs said twice, each where it is most like the row
  under it (so no belt or hem is doubled) - a figure about a tenth taller and slimmer, nearer real
  proportions; its world height grows with it (`stretch`), so a pixel stays the size it was;
- **twice the pixels**: scale2x (EPX) - every pixel into four, a corner taking a neighbour's colour where
  two neighbours agree, which rounds the silhouette and smooths diagonals without a single new colour;
- **a finer face**, where the face uses the usual chars (`s` skin, `S` its shade, `e` dark eyes): each
  eye an upper lid two pixels wide over a one-pixel pupil on the side toward the nose (so it still reads
  as an eye from across a room), a brow of skin shade over it, the nose's shade only at its foot;
- **form shading** from the upper left: across every row each run of the figure darkens toward its
  right edge and lifts a little at its left, and top edges catch the light - in steps, as pixel art is
  shaded.

The back view goes through the same steps (the same rows doubled, so front and back stay the same
size), the face pass aside. Built-in characters are always drawn this way; a scene's own `sprite_defs`
character asks for it with `"hd": true`.
"""
import numpy as np

EXTRA = ((0.40, 0.60, 1), (0.64, 0.92, 2))      # (from, to as shares of the height, rows) said twice


def _diff(a, b):
    return sum(x != y for x, y in zip(a, b))


def _expand(defn, back=False):
    rows = defn['back'] if back else defn['pixels']
    if defn.get('mirror'):                       # half rows, the back's too (see characters.back_rows)
        rows = [r + r[::-1] for r in rows]
    return rows


def picks(rows):
    """The rows said twice: in each band of EXTRA, the ones most like the row under them."""
    h = len(rows)
    out = []
    for lo, hi, n in EXTRA:
        mid = (lo + hi) / 2 * h
        for r in sorted(range(int(lo * h), min(int(hi * h), h - 2)),
                        key=lambda r: (_diff(rows[r], rows[r + 1]), abs(r - mid))):
            if sum(lo * h <= p < hi * h for p in out) >= n:
                break
            if all(abs(r - p) > 1 for p in out):
                out.append(r)
    return sorted(out)


def stretch(defn):
    """How much taller the character is drawn than its grid: (rows + doubled) / rows."""
    rows = _expand(defn)
    return (len(rows) + len(picks(rows))) / len(rows)


def scale2x(rows):
    """EPX: each pixel into four, a corner taking a neighbour's colour where two neighbours agree."""
    h, w = len(rows), len(rows[0])

    def at(y, x):
        return rows[y][x] if 0 <= y < h and 0 <= x < w else '.'
    out = [[None] * (2 * w) for _ in range(2 * h)]
    for y in range(h):
        for x in range(w):
            P, A, B, C, D = at(y, x), at(y - 1, x), at(y, x + 1), at(y, x - 1), at(y + 1, x)
            out[2 * y][2 * x] = A if (C == A and C != D and A != B) else P
            out[2 * y][2 * x + 1] = B if (A == B and A != C and B != D) else P
            out[2 * y + 1][2 * x] = C if (D == C and D != B and C != A) else P
            out[2 * y + 1][2 * x + 1] = D if (B == D and B != A and D != C) else P
    return [''.join(r) for r in out]


def _lum(hexc):
    h = hexc.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.3 * r + 0.59 * g + 0.11 * b


def face(rows, defn):
    """The finer face, on a grid already at 2x - see the module notes. Faces drawn otherwise are left."""
    pal = defn['palette']
    if not ('s' in pal and 'S' in pal and 'e' in pal) or 'e' in defn.get('emissive', '') or _lum(pal['e']) > 0.3:
        return rows
    g = [list(r) for r in rows]
    h, w = len(g), len(g[0])
    eyes = [(y, x) for y in range(0, h - 1, 2) for x in range(0, w - 1, 2)
            if g[y][x] == g[y][x + 1] == g[y + 1][x] == g[y + 1][x + 1] == 'e']
    if not eyes:
        return rows
    cx = sum(x + 1 for _, x in eyes) / len(eyes)
    for y, x in eyes:
        outer = x if x + 1 < cx else x + 1
        g[y + 1][outer] = 's'                       # the lid stays two wide, the pupil one
        if y >= 1 and g[y - 1][x] == 's' and g[y - 1][x + 1] == 's':
            g[y - 1][x] = g[y - 1][x + 1] = 'S'
    ey = max(y for y, _ in eyes)
    for y in range(ey + 2, min(ey + 8, h - 1), 2):
        for x in range(1, w - 1):
            if g[y][x] == 'S' == g[y + 1][x] and 's' in g[y][x - 1:x + 2] and abs(x + 0.5 - cx) < 3:
                g[y][x] = 's'
    return [''.join(r) for r in g]


def shade(rgba):
    """Form shading from the upper left - see the module notes."""
    a = rgba[..., 3] > 0.5
    h, w = a.shape
    f = np.ones((h, w), np.float32)
    for y in range(h):
        x = 0
        while x < w:
            if not a[y, x]:
                x += 1
                continue
            x0 = x
            while x < w and a[y, x]:
                x += 1
            n = x - x0
            if n >= 3:
                u = (np.arange(n) + 0.5) / n
                f[y, x0:x] = 1.0 + 0.07 * (u < 0.22) - 0.12 * (u > 0.62) - 0.08 * (u > 0.82)
    top = a.copy()
    top[1:] &= ~a[:-1]
    f = np.where(top, f + 0.08, f)
    out = rgba.copy()
    out[..., :3] = np.clip(rgba[..., :3] * f[..., None], 0, 1)
    return out


def sprite(defn, back=False):
    """(rgba float H x W x 4, emissive H x W) of a text-grid character in finer pixels."""
    from assets import sprite_from_pixels
    front = _expand(defn)
    twice = set(picks(front))
    rows = _expand(defn, back)
    rows = [r for i, row in enumerate(rows) for r in ([row, row] if i in twice else [row])]
    rows = scale2x(rows)
    if not back:
        rows = face(rows, defn)
    rgba, em = sprite_from_pixels(dict(defn, pixels=rows, mirror=False))
    return shade(rgba), em

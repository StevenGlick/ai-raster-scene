"""Jungle, ruins and beach: textures and props drawn with the pixel-art toolkit.

Everything here is built the way scripts/pixelart.py describes - shapes stamped into a height
field, lit from the upper left, snapped onto hue-shifted ramps - rather than from noise, so a
leaf reads as a leaf and a stone as a stone even when it is small on screen. The three places
share their ramps, so a scene that mixes them still looks like one place.

assets.py merges TEXTURES, SPRITES and the tables below into its own registries.
"""
import numpy as np

from pixelart import Canvas, outline_sprite, ramp, smooth_noise

T = 64


def _rng(name):
    seed = 0
    for ch in name:
        seed = (seed * 131 + ord(ch)) % (2 ** 32)
    return np.random.default_rng(seed)


# ---------------------------------------------------------------- shared ramps

LEAF = ramp('#2f6e34')                    # the jungle's main green
LEAF_SUN = ramp('#6c9c2e')                # young and sunlit leaves
LEAF_SHADE = ramp('#2a665a')              # blue-green leaves in shade
VINE = ramp('#5a5232')
BARK = ramp('#6a5a44', dark=0.25)
TEMPLE = ramp('#8e8c74')                  # grey-green limestone of the jungle temple
TEMPLE_DEEP = ramp('#45433a', light=1.1)
MOSS = ramp('#4e7034')
LICHEN = ramp('#b8b070', dark=0.5)
MARBLE = ramp('#e2d8c2', dark=0.45, light=1.12, warm=0.06)   # sun-bleached ruin stone
MARBLE_SHADE = ramp('#9a9284', dark=0.5)
OCHRE = ramp('#c89a52')
SAND = ramp('#e8d6a8', dark=0.6, light=1.1, warm=0.05)
SAND_WET = ramp('#b49a6e', dark=0.55, light=1.15)
SHELL = ramp('#f2e8dc', dark=0.6, light=1.05)
STRAW = ramp('#c09a52')
BAMBOO = ramp('#b8a35a')
GRASS_DRY = ramp('#c2a456')
GRASS_GREEN = ramp('#7a8a3a')
SOIL = ramp('#5a4632', dark=0.35)
LITTER = [ramp('#8a5a2c'), ramp('#a87a34'), ramp('#6a4a2a')]


def _tile(cv, ramps, dither=0.3, **light):
    return cv.paint(ramps, cv.light(**light), dither=dither)


# ---------------------------------------------------------------- jungle

def _leaf_layers(cv, rng, layers, mats, angles=(25, 155), aspect=(0.42, 0.6), bend=0.1):
    """Leaves in depth order: each layer is (z, count, tone, (shortest, longest))."""
    for z, n, tone, (lo, hi) in layers:
        for _ in range(n):
            x, y = rng.random() * cv.w, rng.random() * cv.h
            ang = np.radians(rng.uniform(*angles))
            L = rng.uniform(lo, hi)
            cv.leaf(x, y, x + np.cos(ang) * L, y + np.sin(ang) * L, L * rng.uniform(*aspect),
                    z=z + rng.random() * 0.3, dome=0.9, bend=rng.uniform(-bend, bend),
                    mat=int(rng.choice(mats)), tone=tone + rng.normal(0, 0.04), rib=0.3)


def tex_jungle_leaves(name):
    """A wall of jungle: broad leaves at three depths, the farthest in shadow, lianas behind."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.2)
    for _ in range(3):
        x0, k, a = rng.random() * T, rng.integers(1, 3), rng.uniform(2, 5)
        pts = [(x0 + a * np.sin(2 * np.pi * k * t / T), t) for t in range(0, T + 1, 4)]
        cv.stroke(pts, 2.4, z=-0.6, dome=0.5, mat=3, tone=-0.05)
    _leaf_layers(cv, rng, [(-0.5, 70, -0.2, (8, 12)), (0.3, 46, -0.05, (10, 15)), (1.1, 20, 0.05, (12, 19))],
                 [0, 0, 0, 1, 2, 2])
    return _tile(cv, [LEAF, LEAF_SUN, LEAF_SHADE, VINE], cavity=0.45, shadow=0.55)


def tex_canopy(name):
    """The underside of the canopy: far leaves glowing with the light through them, the near
    ones and the branches in silhouette, and small bright gaps of sky."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.0, mat=1)
    _leaf_layers(cv, rng, [(0.0, 170, 0.0, (8, 13))], [1], angles=(0, 360), bend=0.15)
    for _ in range(3):                      # branches between the layers
        y0, k, a = rng.random() * T, int(rng.integers(1, 3)), rng.uniform(2, 6)
        pts = [(t, y0 + a * np.sin(2 * np.pi * k * t / T)) for t in range(0, T + 1, 4)]
        cv.stroke(pts, rng.uniform(2.2, 3.4), z=0.5, dome=0.6, mat=2)
    _leaf_layers(cv, rng, [(1.0, 38, 0.0, (9, 14))], [0], angles=(0, 360), bend=0.15)
    shape = cv.light(sun=(0.0, 0.0, 1.0), ambient=0.2, diffuse=0.8, cavity=0.4, shadow=0.0)
    # against the light: what is in front is dark, what the light comes through is bright
    L = np.where(cv.mat == 1, 0.26 + 0.42 * shape, 0.04 + 0.24 * shape)
    rgb = _paint_light(L, LEAF_SUN)
    near = cv.mat != 1
    rgb[near] = _paint_light(L, LEAF)[near]
    rgb[cv.mat == 2] = _paint_light(L, BARK)[cv.mat == 2]
    gap = cv.id == 0
    rgb[gap] = (0.86, 0.92, 0.7)
    em = np.where(cv.mat == 1, 0.12, 0.0).astype(np.float32)
    em[gap] = 0.55
    return rgb, em


def tex_canopy_top(name):
    """The canopy seen from above: sunlit crowns of round leaf clusters, deep shade between."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.0)
    for _ in range(13):
        cx, cy, r = rng.random() * T, rng.random() * T, rng.uniform(10, 16)
        mat = int(rng.choice([0, 0, 1, 2]))
        cv.ellipse(cx, cy, r, r * 0.9, z=-0.2, dome=1.4, rough=0.15, rng=rng, mat=mat, tone=rng.normal(0, 0.04))
        for _ in range(int(r * 2.4)):       # leaves on the crown, pointing outward from its middle
            a, rr = rng.random() * 2 * np.pi, r * np.sqrt(rng.random()) * 0.85
            x, y = cx + np.cos(a) * rr, cy + np.sin(a) * rr
            L = rng.uniform(5, 8)
            cv.leaf(x, y, x + np.cos(a) * L, y + np.sin(a) * L, L * 0.55, z=0.6 + (1 - rr / r), dome=0.6,
                    mat=mat, tone=rng.normal(0.02, 0.04), rib=0.25)
    cv.tone[cv.id == 0] -= 0.4
    return _tile(cv, [LEAF, LEAF_SUN, LEAF_SHADE], sun=(-0.5, -0.6, 1.0), cavity=0.5, shadow=0.55)


def tex_jungle_floor(name):
    """Leaf litter on dark soil, with roots running through it and the odd seedling."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.5, cells=6, rng=rng)
    for _ in range(3):                      # roots
        x0, y0 = rng.random() * T, rng.random() * T
        a = rng.random() * 2 * np.pi
        pts = [(x0, y0)]
        for _ in range(6):
            a += rng.normal(0, 0.5)
            pts.append((pts[-1][0] + np.cos(a) * 7, pts[-1][1] + np.sin(a) * 7))
        cv.stroke(pts, rng.uniform(2.5, 3.6), z=0.3, dome=0.8, taper=(1.0, 0.4), mat=4)
    for i in range(150):                    # fallen leaves, flat, each its own colour
        x, y = rng.random() * T, rng.random() * T
        a = rng.random() * 2 * np.pi
        L = rng.uniform(4, 8)
        cv.leaf(x, y, x + np.cos(a) * L, y + np.sin(a) * L, L * 0.5, z=0.25 + i * 0.002, dome=0.25,
                mat=int(rng.integers(1, 4)), tone=rng.normal(0, 0.06), rib=0.2)
    for _ in range(5):                      # seedlings
        x, y = rng.random() * T, rng.random() * T
        for a in (200, 340):
            r = np.radians(a + rng.normal(0, 15))
            cv.leaf(x, y, x + np.cos(r) * 4, y + np.sin(r) * 4, 2.6, z=0.8, dome=0.4, mat=5)
    return _tile(cv, [SOIL] + LITTER + [BARK, LEAF_SUN], cavity=0.4, shadow=0.4)


def _blocks(cv, rng, rows, widths, mat=0, rough=0.8, chip=3, bevel=2.5, gap=0.6, tone=0.05):
    """Courses of stone blocks across a tile: rows are the course boundaries in pixels."""
    for r in range(len(rows) - 1):
        y0, y1 = rows[r], rows[r + 1]
        start = x = rng.random() * 12
        while x < start + cv.w - 1:
            w = rng.uniform(*widths)
            if x + w > start + cv.w - widths[0] * 0.6:
                w = start + cv.w - x
            cv.box(x + gap, y0 + gap, w - 2 * gap, y1 - y0 - 2 * gap, z=0, top=1.0, bevel=bevel, rough=rough,
                   chip=chip, rng=rng, mat=mat, tone=rng.normal(0, tone))
            x += w


def _moss_in(cv, rng, mat, amount=0.55, low=0.75, cells=5):
    """Moss where the stone is low (joints, chips) and the noise says so."""
    m = (smooth_noise(cv.w, cv.h, cells, rng) > amount) & (cv.z < low)
    cv.mat[m] = mat
    return m


def tex_temple_stone(name):
    """Big jungle-temple blocks: grey-green limestone, chipped, moss in the joints, lichen."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.7, mat=1)
    _blocks(cv, rng, [0, 15, 31, 47, 64], (16, 28))
    cv.noise(0.25, cells=8, rng=rng)
    _moss_in(cv, rng, 2)
    for _ in range(10):                     # lichen
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.8, 1.8), rng.uniform(0.7, 1.4), z=1.05,
                   dome=0.1, mat=3, rough=0.3, rng=rng, mode='max')
    return _tile(cv, [TEMPLE, TEMPLE_DEEP, MOSS, LICHEN], relief=1.2, cavity=0.55)


def _glyph(cv, rng, x, y, s, mat=0):
    """One carved cartouche: a sunken field with numbers, a spiral, an eye, a sun or a fret raised in it."""
    cv.box(x + 1, y + 1, s - 2, s - 2, z=0, top=1.0, bevel=2.0, rough=0.4, chip=1, rng=rng, mat=mat,
           tone=rng.normal(0, 0.04))
    cv.box(x + 4.5, y + 4.5, s - 9, s - 9, z=0, top=0.55, bevel=1.0, mat=mat, mode='carve')
    kind = rng.integers(0, 5)
    cx, cy = x + s / 2, y + s / 2
    if kind == 0:                           # a number: dots over bars
        for i in range(int(rng.integers(1, 3))):
            cv.box(x + 8, cy + 1 + i * 5, s - 16, 3.2, z=0, top=0.6, bevel=1, mat=mat, mode='add')
        n = int(rng.integers(1, 4))
        for i in range(n):
            cv.ellipse(cx + (i - (n - 1) / 2) * 6, cy - 4.5, 2.0, 2.0, dome=0.6, mat=mat, mode='add')
    elif kind == 1:                         # a spiral
        t = np.linspace(0, 3.0 * np.pi, 44)
        r = 1.5 + t / (3.0 * np.pi) * (s / 2 - 8.5)
        cv.stroke(np.stack([cx + r * np.cos(t), cy + r * np.sin(t)], 1), 2.8, dome=0.6, mat=mat, mode='add')
    elif kind == 2:                         # an eye
        cv.ellipse(cx, cy, s / 2 - 8, s / 4 - 1.5, dome=0.6, mat=mat, mode='add')
        cv.ellipse(cx, cy, 2.8, 2.8, dome=0.7, mat=mat, mode='carve')
    elif kind == 3:                         # a sun: a disc with rays
        cv.ellipse(cx, cy, 4.0, 4.0, dome=0.6, mat=mat, mode='add')
        for a in np.arange(8) * np.pi / 4:
            cv.stroke([(cx + np.cos(a) * 6.5, cy + np.sin(a) * 6.5), (cx + np.cos(a) * 9.5, cy + np.sin(a) * 9.5)],
                      2.2, dome=0.5, mat=mat, mode='add')
    else:                                   # a stepped fret
        pts = [(x + 8, y + s - 8.5), (x + 8, cy), (cx, cy), (cx, y + 8.5), (x + s - 8, y + 8.5)]
        cv.stroke(pts, 3.0, dome=0.6, mat=mat, mode='add')


def tex_glyphs(name):
    """Carved glyph panels: cartouches of numbers, spirals, eyes, suns and frets."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.8, mat=1)
    for gy in (0, 32):
        for gx in (0, 32):
            _glyph(cv, rng, gx, gy, 32)
    cv.noise(0.15, cells=8, rng=rng)
    _moss_in(cv, rng, 2, amount=0.5, low=0.0)
    return _tile(cv, [TEMPLE, TEMPLE_DEEP, MOSS], relief=1.5, cavity=0.6, shadow=0.6, reach=4)


def _roots(cv, rng, n, z=1.2, mat=4, width=(3.0, 5.0)):
    """Roots pouring down a surface, branching as they go, each tiling round the edges."""
    for _ in range(n):
        x, y = rng.random() * cv.w, rng.random() * cv.h * 0.3
        a = np.radians(90 + rng.normal(0, 18))
        w = rng.uniform(*width)
        pts = [(x, y)]
        for _ in range(9):
            a += rng.normal(0, 0.35)
            a = np.clip(a, np.radians(35), np.radians(145))
            pts.append((pts[-1][0] + np.cos(a) * 7, pts[-1][1] + np.sin(a) * 7))
        cv.stroke(pts, w, z=z, dome=1.0, taper=(1.0, 0.35), mat=mat, tone=rng.normal(0, 0.04))
        for _ in range(2):                  # side roots
            i = rng.integers(2, len(pts) - 2)
            b = a + rng.choice([-1, 1]) * rng.uniform(0.6, 1.0)
            q = [pts[i]]
            for _ in range(4):
                b += rng.normal(0, 0.3)
                q.append((q[-1][0] + np.cos(b) * 5, q[-1][1] + abs(np.sin(b)) * 5))
            cv.stroke(q, w * 0.5, z=z - 0.1, dome=0.8, taper=(1.0, 0.3), mat=mat, tone=rng.normal(0, 0.04))


def tex_temple_roots(name):
    """Temple blocks with a strangler fig's roots poured over them."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.7, mat=1)
    _blocks(cv, rng, [0, 15, 31, 47, 64], (16, 28))
    cv.noise(0.25, cells=8, rng=rng)
    _moss_in(cv, rng, 2, amount=0.6)
    _roots(cv, rng, 4)
    return _tile(cv, [TEMPLE, TEMPLE_DEEP, MOSS, LICHEN, BARK], relief=1.2, cavity=0.55, shadow=0.6)


def tex_temple_door(name):
    """A shrine doorway: a corbelled opening into the dark, a glyph lintel over it, and a faint
    warm light from something burning inside."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.7, mat=1)
    _blocks(cv, rng, [0, 15, 31, 47, 64], (16, 28))
    cv.noise(0.2, cells=8, rng=rng)
    y, x = np.mgrid[0:T, 0:T] + 0.5
    # the corbel arch: straight jambs, then courses stepping in toward a narrow top
    half = np.where(y > 38, 13.0, 13.0 - np.ceil((38 - y) / 4) * 2.2)
    opening = (np.abs(x - T / 2) < half) & (y > 17) & (half > 2)
    frame = (np.abs(x - T / 2) < half + 3) & (y > 14) & ~opening
    cv.z[frame] = np.maximum(cv.z[frame], 1.15)
    cv.mat[frame] = 0
    for gx in (14, 32):                     # a lintel of two small glyphs
        cv.box(gx, 2, 18, 11, z=0.1, top=1.1, bevel=1.5, mat=0, rng=rng)
        cv.box(gx + 3, 4.5, 12, 6, top=0.4, bevel=0.8, mat=0, mode='carve')
        cv.ellipse(gx + 9, 7.5, 2.2, 2.0, dome=0.4, mat=0, mode='add')
    rgb = _tile(cv, [TEMPLE, TEMPLE_DEEP], relief=1.2, cavity=0.55)
    glow = np.clip((y - 30) / 34, 0, 1) ** 2 * opening
    inside = ramp(['#07060a', '#120c0a', '#2a1a10', '#4a2c14', '#6a3e18'])
    rgb[opening] = _paint_light(glow, inside)[opening]
    em = (glow * 0.35).astype(np.float32)
    return rgb, em


def tex_temple_cornice(name):
    """The top course of a temple tier: a projecting moulding with a shadow under it, so each
    step of a pyramid reads as a step. Use it as the top storey of a wall stack."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.7, mat=1)
    _blocks(cv, rng, [14, 31, 47, 64], (16, 28))
    for x in range(0, T, 16):               # the moulding: one long course of dressed stones
        cv.box(x + 0.5, 0.5, 15, 10, z=0.5, top=1.0, bevel=1.5, rough=0.3, rng=rng, mat=0, tone=rng.normal(0.04, 0.03))
        cv.box(x + 4, 3, 8, 4.5, top=0.3, bevel=0.8, mat=0, mode='carve')
    cv.noise(0.2, cells=8, rng=rng)
    _moss_in(cv, rng, 2, amount=0.6)
    rgb = _tile(cv, [TEMPLE, TEMPLE_DEEP, MOSS], relief=1.2, cavity=0.55)
    rgb[11:14] = TEMPLE_DEEP[0]             # the shadow the moulding throws
    rgb[14:16] *= 0.75
    return rgb


def tex_roof_comb(name):
    """A shrine's roof comb: a stone lattice against the sky, with a stepped crest."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.7, mat=2)
    _blocks(cv, rng, [0, 12, 24, 36, 48, 64], (10, 18), chip=1, bevel=2.0)
    y, x = np.mgrid[0:T, 0:T] + 0.5
    holes = np.zeros((T, T), bool)
    for hx in (3, 24, 45):
        for hy in (14, 39):
            holes |= (x > hx) & (x < hx + 16) & (y > hy) & (y < hy + 19)
    cv.noise(0.2, cells=8, rng=rng)
    _moss_in(cv, rng, 1, amount=0.6)
    rgb = _tile(cv, [TEMPLE, MOSS, TEMPLE_DEEP], relief=1.2, cavity=0.55)
    rim = holes & ~np.roll(holes, 1, axis=0)  # the lintel over each opening throws a shadow
    rgb[np.roll(rim, -1, axis=0) & ~holes] = TEMPLE_DEEP[1]
    crest = (y < 6) & ((x % 16) > 9)        # the stepped crest along the top
    alpha = ~(holes | crest)
    return rgb, None, alpha.astype(np.float32)


def tex_jungle_bark(name):
    """A giant rainforest trunk: fissured grey bark netted over by a strangler fig's roots."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    for _ in range(9):                      # fissures in the bark
        x0, k, a, ph = rng.random() * T, int(rng.integers(1, 3)), rng.uniform(1, 3), rng.random() * 6
        pts = [(x0 + a * np.sin(2 * np.pi * k * t / T + ph), t) for t in range(0, T + 1, 4)]
        cv.stroke(pts, 1.3, dome=0.5, mode='carve')
    roots = []
    for i in range(6):                      # the fig's roots, down the trunk
        x0, k, a, ph = (i + rng.random() * 0.6) * T / 6, int(rng.integers(1, 3)), rng.uniform(2, 5), rng.random() * 6
        pts = [(x0 + a * np.sin(2 * np.pi * k * t / T + ph), t) for t in range(0, T + 1, 4)]
        roots.append(pts)
        cv.stroke(pts, rng.uniform(3.2, 5.0), z=0.5, dome=1.0, mat=1, tone=rng.normal(0, 0.05))
    for _ in range(7):                      # and the bridges where neighbours have grown together
        i = int(rng.integers(0, 6))
        a, b = roots[i], roots[(i + 1) % 6]
        j = int(rng.integers(1, len(a) - 3))
        p, q = a[j], b[j + 2]
        if q[0] < p[0]:
            q = (q[0] + T, q[1])
        cv.stroke([p, q], rng.uniform(2.2, 3.2), z=0.45, dome=0.9, mat=1, tone=rng.normal(-0.03, 0.04))
    moss = (smooth_noise(T, T, 3, rng, cells_y=6) > 0.6) & (cv.z < 1.1)
    cv.mat[moss] = 2
    return _tile(cv, [ramp('#7c766a', dark=0.3), BARK, MOSS], relief=1.2, cavity=0.5, shadow=0.55)


# ---------------------------------------------------------------- ruins

def tex_limestone(name):
    """Sun-bleached ashlar: big cream blocks with weathered edges, rain streaks and orange lichen."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.5, mat=1)
    _blocks(cv, rng, [0, 21, 42, 64], (24, 40), rough=1.1, chip=2, bevel=3.5, gap=0.5, tone=0.04)
    cv.noise(0.14, cells=10, rng=rng, octaves=2)
    for _ in range(9):
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.8, 2.0), rng.uniform(0.6, 1.4), z=1.05,
                   dome=0.1, mat=2, rough=0.4, rng=rng, mode='max')
    streak = (smooth_noise(T, T, 16, rng, cells_y=2) > 0.66) & (cv.mat == 0)
    cv.tone[streak] -= 0.08
    return _tile(cv, [MARBLE, MARBLE_SHADE, OCHRE], sun=(-0.6, -0.7, 0.9), relief=1.1, cavity=0.45, dither=0.2)


def tex_ruin_paving(name):
    """Worn stone slabs, cracked and sunk unevenly, with grass growing up through the joints."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.6, mat=1)
    y0 = 0
    for y1 in (19, 40, 64):
        start = x = rng.random() * 14
        while x < start + T - 1:
            w = rng.uniform(18, 34)
            if x + w > start + T - 12:
                w = start + T - x
            cv.box(x + 0.7, y0 + 0.7, w - 1.4, y1 - y0 - 1.4, z=rng.normal(0, 0.15), top=1.0, bevel=3.0, rough=1.4,
                   chip=2, rng=rng, mat=0, tone=rng.normal(0, 0.06))
            x += w
        y0 = y1
    cv.noise(0.12, cells=10, rng=rng)
    for _ in range(4):                      # cracks
        x, y = rng.random() * T, rng.random() * T
        a = rng.random() * 2 * np.pi
        pts = [(x, y)]
        for _ in range(4):
            a += rng.normal(0, 0.6)
            pts.append((pts[-1][0] + np.cos(a) * 4, pts[-1][1] + np.sin(a) * 4))
        cv.stroke(pts, 1.4, dome=0.6, mode='carve')
    low = np.argwhere(cv.z < 0.1)
    for y, x in low[rng.choice(len(low), 46, replace=False)]:     # grass tufts in the joints
        for _ in range(4):
            a = np.radians(rng.uniform(210, 330))
            L = rng.uniform(2.5, 4.5)
            cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], 1.4, z=1.0, dome=0.4, taper=(1, 0.6),
                      mat=2, tone=rng.normal(0, 0.05))
    return _tile(cv, [MARBLE, MARBLE_SHADE, GRASS_GREEN], sun=(-0.6, -0.7, 0.9), relief=1.1, cavity=0.5, dither=0.2)


def tex_dry_grass(name):
    """Sunburnt grass in thick clumps, a little pale earth between them, the odd poppy."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.3, cells=6, rng=rng)
    for i in range(46):                         # fewer, larger clumps, earth between them
        cx, cy = rng.random() * T, rng.random() * T
        mat = 1 if rng.random() < 0.8 else 2
        tone = rng.normal(0, 0.05)
        for _ in range(13):
            a = np.radians(rng.uniform(215, 325))
            L = rng.uniform(4, 8)
            x0, y0 = cx + rng.normal(0, 1.8), cy + rng.normal(0, 0.8)
            cv.stroke([(x0, y0), (x0 + np.cos(a) * L, y0 + np.sin(a) * L)], 1.4, z=0.3 + i * 0.01, dome=0.5,
                      taper=(1.0, 0.5), mat=mat, tone=tone + rng.normal(0, 0.03))
    for _ in range(3):
        cv.ellipse(rng.random() * T, rng.random() * T, 1.2, 1.1, z=1.3, dome=0.3, mat=3)
    return _tile(cv, [SOIL, GRASS_DRY, GRASS_GREEN, ramp('#d04a30')], sun=(-0.5, -0.8, 0.8), cavity=0.35, dither=0.25)


def _column_shade(x, cx, r):
    """Cylinder light across a column: 0 dark edge .. 1 lit, light from the left."""
    u = np.clip((x - cx) / r, -1, 1)
    nx, nz = u, np.sqrt(1 - u * u)
    return np.clip(0.6 * nz - 0.55 * nx, 0, 1)


def _paint_light(light, rp, dither=0.3):
    """A light map 0..1 snapped onto a ramp with a light ordered dither."""
    from pixelart import BAYER4
    h, w = light.shape
    bay = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    return rp[np.clip(np.round(light * (len(rp) - 1) + (bay - 0.5) * dither), 0, len(rp) - 1).astype(int)]


def _colonnade(name, part):
    """One storey of a Doric colonnade, one column to a cell, see-through between the columns.

    part: 'shaft' (fluted shaft), 'top' (capital, architrave, triglyph frieze and cornice) or
    'broken' (shafts snapped off at different heights). Stack them: shaft, shaft, top."""
    rng = _rng(name)
    r, cx = 13.0, T / 2
    y, x = np.mgrid[0:T, 0:T] + 0.5
    dx = np.abs(x - cx)
    # concave flutes catch the light in stripes across the round of the shaft
    shaft_light = _column_shade(x, cx, r) * (0.8 + 0.2 * np.cos((x - cx) / r * np.pi * 5) ** 2)
    light = np.zeros((T, T), np.float32)
    if part == 'shaft':
        alpha = dx < r
        light = shaft_light
    elif part == 'broken':
        cols = np.clip(x.astype(int), 0, T - 1)
        jag = (16 + 30 * smooth_noise(T, 1, 3, rng)[0] + 5 * (rng.random(T) - 0.5))[cols]
        alpha = (dx < r) & (y > jag)
        light = np.where(y < jag + 2.5, shaft_light * 0.6 + 0.4, shaft_light)    # the break catches the sun
    else:
        shaft = (dx < r) & (y > 44)
        echinus = (y > 36) & (y <= 44) & (dx < r + 6 * (44 - y) / 8)
        abacus = (y > 31) & (y <= 36) & (dx < r + 7)
        beam = y <= 31
        alpha = shaft | echinus | abacus | beam
        light = np.where(shaft, shaft_light, light)
        light = np.where(echinus, 0.25 + 0.6 * _column_shade(x, cx, r + 6), light)
        light = np.where(abacus, np.where(y < 33, 0.95, 0.7), light)
        light = np.where(beam & (y > 20), np.where(y < 22, 0.95, 0.74), light)          # architrave
        frieze = beam & (y > 8) & (y <= 20)
        tri = frieze & ((dx < 6) | (np.abs(dx - T / 2) < 6))      # over each column and between them
        light = np.where(frieze, np.where(tri, 0.58, 0.78), light)
        groove = tri & ((np.abs(dx - 2) < 0.8) | (np.abs(np.abs(dx - T / 2) - 2) < 0.8))
        light = np.where(groove, 0.28, light)
        light = np.where(beam & (y <= 8), np.where(y < 3, 0.98, np.where(y > 6, 0.4, 0.82)), light)  # cornice
    light = np.clip(light + 0.14 * (smooth_noise(T, T, 8, rng) - 0.5), 0, 1)
    rgb = _paint_light(light, MARBLE)
    rgb[alpha & ~np.roll(alpha, -1, axis=1)] = MARBLE[0]       # dark edge on the shadow side
    return rgb, None, alpha.astype(np.float32)


def tex_colonnade(name):
    return _colonnade(name, 'shaft')


def tex_colonnade_top(name):
    return _colonnade(name, 'top')


def tex_colonnade_broken(name):
    return _colonnade(name, 'broken')


# ---------------------------------------------------------------- beach

def tex_beach_sand(name):
    """Pale coral sand: soft wind ripples that wander, bits of shell, a little grain."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0)
    yy, xx = np.mgrid[0:T, 0:T]
    warp = smooth_noise(T, T, 3, rng) * 9 + smooth_noise(T, T, 6, rng) * 3
    ph = (yy + warp) * 2 * np.pi / (T / 6)
    cv.z = (0.5 + 0.5 * np.sin(ph)) ** 1.5 * 0.55 * (0.6 + 0.8 * smooth_noise(T, T, 4, rng))
    cv.noise(0.15, cells=16, rng=rng)
    for _ in range(12):
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.7, 1.4), rng.uniform(0.5, 0.9),
                   angle=rng.random() * 180, z=0.7, dome=0.4, mat=1, tone=rng.normal(0.05, 0.05))
    return _tile(cv, [SAND, SHELL], sun=(-0.4, -0.8, 0.7), relief=1.2, cavity=0.15, shadow=0.25, dither=0.45)


def tex_wet_sand(name):
    """Sand the sea has just left: dark and smooth and shining, with lines of foam left by the
    backwash and the pinholes of things living under it."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0)
    cv.noise(0.12, cells=4, rng=rng)
    cv.tone += 0.12 * (smooth_noise(T, T, 3, rng) - 0.5)
    for _ in range(2):                      # backwash lines: thin wavering foam
        y0, ph = rng.random() * T, rng.random() * 6
        pts = [(t, y0 + 4 * np.sin(2 * np.pi * t / T + ph) + 1.5 * np.sin(2 * np.pi * 3 * t / T)) for t in range(0, T + 1, 2)]
        cv.stroke(pts, 1.3, z=0.15, dome=0.2, mat=1)
    for _ in range(14):
        cv.ellipse(rng.random() * T, rng.random() * T, 0.6, 0.6, dome=0.5, mode='carve')
    return _tile(cv, [SAND_WET, ramp('#e8ecdc', dark=0.7, light=1.05)], sun=(-0.4, -0.8, 0.7), relief=0.8,
                 cavity=0.3, shadow=0.0, dither=0.4)


def tex_shallows(name):
    """Clear turquoise water over sand: the rippled bed seen through it, caustics drawn in light."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    # caustics: bright where two tiled noise fields cross their midline
    a = smooth_noise(T, T, 5, rng)
    b = smooth_noise(T, T, 7, rng)
    net = np.exp(-((a - 0.5) / 0.045) ** 2) + np.exp(-((b - 0.5) / 0.045) ** 2)
    depth = smooth_noise(T, T, 3, rng)
    v = 0.45 + 0.25 * depth + 0.35 * np.clip(net, 0, 1)
    return _paint_light(v, ramp('#3ab8b0', dark=0.45, light=1.4, warm=0.05), 0.5)


def tex_sea(name):
    """Open water: deep blue, the backs of small waves catching the sky, a few whitecaps."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0)
    yy, xx = np.mgrid[0:T, 0:T]
    w1 = np.sin(2 * np.pi * (yy * 4 / T + 0.3 * smooth_noise(T, T, 3, rng)))
    w2 = np.sin(2 * np.pi * (xx * 2 / T + yy * 6 / T + 0.5 * smooth_noise(T, T, 4, rng)))
    cv.z = 0.6 * w1 + 0.35 * w2
    caps = (w1 > 0.86) & (smooth_noise(T, T, 8, rng) > 0.6)
    cv.mat[caps] = 1
    return _tile(cv, [ramp('#1e5a8a', dark=0.4, light=1.5), ramp('#e8f0f0')], sun=(0.0, -1.0, 0.5), relief=1.6,
                 cavity=0.0, shadow=0.0, dither=0.4)


def tex_bamboo(name):
    """Bamboo poles side by side, ringed at their nodes, some greener, some sun-browned, one cord."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.0, mat=3)
    x = 0.0
    while x < T - 2:
        w = rng.uniform(6.5, 9.5)
        if x + w > T - 4:
            w = T - x
        cx = x + w / 2
        mat = int(rng.choice([0, 0, 0, 1, 2]))
        cv.stroke([(cx, -2), (cx, T + 2)], w - 0.9, z=0.0, dome=1.0, mat=mat, tone=rng.normal(0, 0.05))
        for ny in rng.uniform(0, T, 2) + [0, 0]:      # nodes: a ridge with a dark ring under it
            cv.stroke([(cx - w / 2, ny), (cx + w / 2, ny)], 1.8, dome=0.45, mat=mat, mode='add')
            cv.stroke([(cx - w / 2, ny + 1.5), (cx + w / 2, ny + 1.5)], 0.9, dome=0.3, mat=mat, mode='carve')
        x += w
    cy = rng.uniform(10, 54)
    for k in range(2):                      # a lashing cord, two turns
        cv.stroke([(-1, cy + k * 2.2), (T + 1, cy + k * 2.2)], 1.8, z=1.0, dome=0.6, mat=4)
    return _tile(cv, [BAMBOO, ramp('#8a9a4a'), ramp('#a07a4a'), ramp('#2a2418'), ramp('#7a6040')],
                 relief=1.0, cavity=0.3, shadow=0.5)


def tex_thatch(name):
    """Palm thatch: rows of straw, each row overlapping the one below and shading its top."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.0)
    for row, y0 in enumerate(range(-6, T, 8)):
        for i in range(30):
            x = (i + rng.random()) * T / 30
            L = rng.uniform(10, 13)
            a = np.radians(90 + rng.normal(0, 4))
            cv.stroke([(x, y0), (x + np.cos(a) * L, y0 + np.sin(a) * L)], 2.2, z=row * 0.6 + rng.random() * 0.15,
                      dome=0.5, taper=(1.0, 0.6), mat=int(rng.random() < 0.18), tone=rng.normal(0, 0.05))
    return _tile(cv, [STRAW, ramp('#8a7040')], relief=0.7, cavity=0.25, shadow=0.55, reach=4, dither=0.25)


TEXTURES = {
    'jungle_leaves': lambda n: (tex_jungle_leaves(n), None),
    'canopy': tex_canopy,
    'canopy_top': lambda n: (tex_canopy_top(n), None),
    'jungle_floor': lambda n: (tex_jungle_floor(n), None),
    'temple_stone': lambda n: (tex_temple_stone(n), None),
    'glyphs': lambda n: (tex_glyphs(n), None),
    'temple_roots': lambda n: (tex_temple_roots(n), None),
    'jungle_bark': lambda n: (tex_jungle_bark(n), None),
    'temple_door': tex_temple_door,
    'temple_cornice': lambda n: (tex_temple_cornice(n), None),
    'roof_comb': tex_roof_comb,
    'limestone': lambda n: (tex_limestone(n), None),
    'ruin_paving': lambda n: (tex_ruin_paving(n), None),
    'dry_grass': lambda n: (tex_dry_grass(n), None),
    'colonnade': tex_colonnade,
    'colonnade_top': tex_colonnade_top,
    'colonnade_broken': tex_colonnade_broken,
    'beach_sand': lambda n: (tex_beach_sand(n), None),
    'wet_sand': lambda n: (tex_wet_sand(n), None),
    'shallows': lambda n: (tex_shallows(n), None),
    'sea': lambda n: (tex_sea(n), None),
    'bamboo': lambda n: (tex_bamboo(n), None),
    'thatch': lambda n: (tex_thatch(n), None),
}

# ---------------------------------------------------------------- props
# Sprites are drawn on a canvas that does not wrap; z is relief toward the viewer, lit from the
# upper left like the textures, so a prop and the wall behind it agree about where the sun is.

def _prop(cv, ramps, outline=True, em=None, dither=0.3, **light):
    rgba = cv.paint(ramps, cv.light(**light), dither=dither)
    if outline:
        rgba = outline_sprite(rgba)
    e = np.zeros(rgba.shape[:2], np.float32) if em is None else em.astype(np.float32)
    return rgba.astype(np.float32), e


def _arc(p0, angle, length, droop, n=12):
    """Points along a stem that sets off at `angle` (degrees, 0 = right, -90 = up) and bends
    down under its own weight by `droop` (a fraction of its length)."""
    a = np.radians(angle)
    t = np.linspace(0, 1, n)
    return np.stack([p0[0] + np.cos(a) * length * t, p0[1] + np.sin(a) * length * t + droop * length * t * t], 1)


def _frond(cv, pts, leaflet, angle=50, mat=0, z=0.0, tone=0.0, width=1.6, step=2.0, droop=0.35, rib=True,
           rng=None, ragged=0.0):
    """A pinnate frond: a midrib along pts with narrow leaflets down both sides, longest in the
    middle, swept toward the tip and drooping. `ragged` (0..1) drops that share of the leaflets
    and varies the length of the rest, the way wind tatters a palm."""
    pts = np.asarray(pts, np.float32)
    if rib:
        cv.stroke(pts, 1.6, z=z + 0.3, dome=0.4, taper=(1.0, 0.4), mat=mat, tone=tone - 0.08)
    seg = np.diff(pts, axis=0)
    lens = np.hypot(seg[:, 0], seg[:, 1])
    total = lens.sum()
    d = 0.0
    while d < total:
        i = min(np.searchsorted(np.cumsum(lens), d), len(seg) - 1)
        f = (d - (np.cumsum(lens)[i] - lens[i])) / max(lens[i], 1e-6)
        p = pts[i] + seg[i] * f
        heading = np.arctan2(seg[i][1], seg[i][0])
        t = d / total
        L = leaflet * np.sin(np.pi * min(1.0, 0.15 + t)) ** 0.7
        for side in (-1, 1):
            if ragged and rng.random() < ragged * 0.4:
                continue
            L = L * (1 + (rng.uniform(-0.3, 0.2) * ragged if ragged else 0))
            a = heading + side * np.radians(angle)
            q = (p[0] + np.cos(a) * L, p[1] + np.sin(a) * L + droop * L)
            cv.stroke([p, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 - 0.3 * side), q], width, z=z + 0.2 - 0.1 * side,
                      dome=0.5, taper=(1.0, 0.45), mat=mat, tone=tone + 0.04 * side)
        d += step


def _paddle(t):
    """Width along a banana or heliconia blade: a short stalk, then a long paddle rounded at both ends."""
    t = np.asarray(t, np.float32)
    return np.where(t < 0.18, 0.12, np.clip(np.sin(np.pi * np.clip((t - 0.18) / 0.82, 0, 1)), 0, 1) ** 0.45)


def spr_banana_plant():
    """A banana plant: long paddle leaves on stalks, held up and drooping at the tips, torn into
    strips by the wind, with an old leaf hanging dead against the stem."""
    rng = np.random.default_rng(31)
    w, h = 176, 136
    cx, top = 88, 84
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.leaf(cx, top + 2, cx - 6, top + 44, 10, z=-0.4, dome=0.6, rib=0.3, shape=0.8, mat=2)      # the dead leaf
    cv.stroke([(cx, h), (cx, top - 2)], 10, z=0.0, dome=1.0, taper=(1.15, 0.8), mat=1)
    for y in range(top + 4, h - 2, 7):
        cv.stroke([(cx - 4, y), (cx + 4, y - 2)], 1.0, dome=0.3, mat=1, mode='carve')
    leaves = [(-160, 82, 0.55, -0.14), (-20, 82, 0.55, -0.12), (-130, 78, 0.42, -0.02), (-50, 78, 0.42, 0.0),
              (-106, 70, 0.32, 0.06), (-78, 64, 0.25, 0.08)]
    for ang, L, droop, tone in leaves:
        leaf, cut = cv.layer(), cv.layer()
        pts = _arc((cx, top), ang, L, droop, n=16)
        leaf.stroke(pts, 21, z=0.5 + tone * 3, dome=1.0, taper=_paddle, mat=0, tone=tone)
        leaf.stroke(pts[2:], 1.1, dome=0.5, mode='carve')                                 # the midrib
        seg = np.diff(pts, axis=0)
        for _ in range(int(rng.integers(3, 6))):            # tears from the edge in toward the midrib
            i = int(rng.integers(5, 15))
            nx, ny = -seg[i][1], seg[i][0]
            n = np.hypot(nx, ny)
            side = rng.choice([-1, 1])
            nx, ny = nx / n * side, ny / n * side
            p = pts[i]
            cut.stroke([(p[0] + nx * 12, p[1] + ny * 12), (p[0] + nx * 2.2, p[1] + ny * 2.2)], 1.2)
        cv.paste(leaf, cut)
    return _prop(cv, [LEAF_SUN, ramp('#8a9a4a'), ramp('#8a6a3a')], relief=1.1, cavity=0.4, shadow=0.5)


def spr_monstera():
    """Monstera: big glossy heart-shaped leaves, split and holed, on long stalks."""
    rng = np.random.default_rng(7)
    w, h = 72, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    spots = [(14, 40, 11, -0.18), (58, 40, 11, -0.15), (20, 26, 15, -0.1), (50, 24, 15, -0.06), (35, 18, 16, 0.08)]
    for cx, cy, r, tone in spots:
        cv.stroke([(36, 56), ((36 + cx) / 2, cy + 18), (cx, cy + r * 0.4)], 1.8, z=-0.2, dome=0.4, mat=1)
    for k, (cx, cy, r, tone) in enumerate(spots):
        leaf, cut = cv.layer(), cv.layer()
        leaf.ellipse(cx, cy, r, r * 0.82, z=0.2 + 0.3 * k, dome=1.0, mat=0, tone=tone, power=0.7)
        leaf.stroke([(cx, cy + r * 0.6), (cx, cy - r * 0.7)], 1.0, dome=0.3, mode='carve')    # midrib
        cut.ellipse(cx, cy + r * 0.78, r * 0.2, r * 0.24)                                    # the notch at the stalk
        for i in range(5):                  # splits from the edge toward the middle, and a hole in each lobe
            a = np.radians(200 + i * 35 + rng.normal(0, 6))
            cut.stroke([(cx + np.cos(a) * r * 1.05, cy + np.sin(a) * r * 0.9),
                        (cx + np.cos(a) * r * 0.48, cy + np.sin(a) * r * 0.4)], 1.4)
            cut.ellipse(cx + np.cos(a + 0.3) * r * 0.3, cy + np.sin(a + 0.3) * r * 0.26, 1.3, 1.0)
        cv.paste(leaf, cut)
    return _prop(cv, [ramp('#24683a', dark=0.25, light=1.45), ramp('#4a6a2a')], relief=1.0, cavity=0.3)


def spr_tree_fern():
    """A tree fern: a slim scaly trunk under a crown of long arching fronds."""
    w, h = 96, 120
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(48, 120), (47, 80), (49, 44)], 6, z=0.0, dome=1.0, taper=(1.3, 0.9), mat=1)
    for y in range(48, 118, 4):             # the scars of old fronds up the trunk
        cv.stroke([(44, y), (52, y + 1)], 1.2, dome=0.4, mat=1, mode='carve')
    for k, (ang, L, droop) in enumerate([(-150, 46, 0.55), (-30, 46, 0.55), (-115, 40, 0.45), (-65, 40, 0.45),
                                         (-175, 40, 0.7), (-5, 40, 0.7), (-90, 34, 0.35)]):
        pts = _arc((48, 44), ang, L, droop)
        _frond(cv, pts, 7.5, angle=55, mat=0, z=0.3 + 0.15 * k, tone=-0.1 if k < 2 else 0.04)
    return _prop(cv, [LEAF, ramp('#5a4632', dark=0.3)], relief=1.0, cavity=0.4, shadow=0.5)


def spr_heliconia():
    """Heliconia: tall paddle leaves with hanging zigzags of red and gold bracts."""
    rng = np.random.default_rng(12)
    w, h = 56, 72
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x0, ang, L in ((24, -105, 46), (32, -75, 44), (18, -130, 34), (38, -50, 34)):
        a = np.radians(ang)
        cv.stroke([(28, 72), (x0, 40)], 2.0, z=0.0, dome=0.5, mat=0, tone=-0.1)
        cv.leaf(x0, 40, x0 + np.cos(a) * L * 0.6, 40 + np.sin(a) * L * 0.6, 9, z=0.3, dome=0.9, rib=0.5,
                shape=0.6, base=0.45, mat=0, tone=rng.normal(0, 0.05))
    for bx, by in ((24, 42), (34, 38)):     # the bract chains: alternate left and right, hanging down
        cv.stroke([(bx, by - 4), (bx, by + 22)], 1.2, z=1.0, dome=0.3, mat=0)
        for i in range(6):
            side = 1 if i % 2 else -1
            y = by + i * 3.6
            cv.leaf(bx, y, bx + side * 6, y - 3, 3.4, z=1.4 + 0.05 * i, dome=0.8, rib=0.2, shape=0.8, base=0.3,
                    mat=1 if i % 3 else 2)
    return _prop(cv, [LEAF, ramp('#d0302a'), ramp('#e8b030')], relief=1.0, cavity=0.35, shadow=0.45)


def spr_bromeliad():
    """A bromeliad: a rosette of stiff strap leaves flushed red toward a small red heart."""
    w, h = 44, 26
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k, ang in enumerate([-172, -8, -152, -28, -132, -48, -112, -68, -90]):
        a = np.radians(ang)
        L = 19 if k < 4 else 15 if k < 8 else 11
        cv.leaf(22, 24, 22 + np.cos(a) * L, 24 + np.sin(a) * L * 0.8, 4.6, z=0.12 * k, dome=0.8, rib=0.4,
                shape=0.9, base=0.35, mat=0 if k < 4 else 1)
    cv.ellipse(22, 20, 2.4, 1.8, z=1.4, dome=0.6, mat=2)
    return _prop(cv, [ramp('#4a7a3a'), ramp('#6a6a3a'), ramp('#c02838')], relief=1.0, cavity=0.3, shadow=0.4)


def spr_liana():
    """Lianas hanging from the canopy: long woody strands with a few leaves, the top cut by the frame."""
    rng = np.random.default_rng(5)
    w, h = 40, 128
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x0 in (8, 19, 31):
        sway = rng.uniform(2, 5)
        pts = [(x0 + sway * np.sin(t / 20 + x0), t) for t in range(0, int(rng.uniform(96, 126)), 6)]
        cv.stroke(pts, 2.2, z=0.0, dome=0.6, taper=(1.0, 0.7), mat=1)
        for (px, py) in pts[2::3]:
            side = rng.choice([-1, 1])
            cv.leaf(px, py, px + side * 6, py + 5, 4.2, z=0.5, dome=0.7, rib=0.3, mat=0, tone=rng.normal(0, 0.05))
    return _prop(cv, [LEAF, VINE], relief=1.0, cavity=0.3, shadow=0.4)


def spr_fern():
    """A clump of ferns: fronds arching out of a crown at the ground, the old ones lower and darker."""
    rng = np.random.default_rng(71)
    w, h = 72, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k, (ang, L, droop) in enumerate([(-165, 36, 0.75), (-15, 36, 0.75), (-140, 34, 0.6), (-40, 34, 0.6),
                                         (-118, 30, 0.5), (-62, 30, 0.5), (-96, 26, 0.4), (-84, 24, 0.4)]):
        pts = _arc((36, 38), ang + rng.normal(0, 4), L, droop, n=12)
        _frond(cv, pts, 4.6, angle=62, mat=0, z=0.3 + 0.15 * k, tone=-0.12 if k < 2 else rng.normal(0.02, 0.03),
               width=1.4, step=2.3, droop=0.5)
    return _prop(cv, [ramp('#3a7a36')], relief=1.0, cavity=0.4, shadow=0.45)


def _crown(cv, rng, cx, cy, rx, ry, clusters, size=(9, 14), leaf=6.0, z=1.0, tone=0.0):
    """A rounded mass of leaf clusters, lit from above: the top of a rainforest tree. Clusters
    are `size` pixels across and kept inside the rx x ry oval."""
    for _ in range(clusters):
        a = rng.uniform(0, 2 * np.pi)
        r = rng.uniform(0, 1) ** 0.6
        cl = rng.uniform(*size)
        x, y = cx + np.cos(a) * (rx - cl) * r, cy + np.sin(a) * (ry - cl * 0.8) * r
        up = (cy - y) / ry                  # +1 at the top of the crown, -1 underneath
        cv.ellipse(x, y, cl, cl * 0.8, z=z + 0.6 * (1 - r), dome=1.4, rough=0.2, rng=rng, mat=0,
                   tone=tone + 0.08 * up - 0.04 + rng.normal(0, 0.03))
        for _ in range(int(cl * 1.3)):
            b, rr = rng.uniform(0, 2 * np.pi), cl * np.sqrt(rng.random()) * 0.8
            px, py = x + np.cos(b) * rr, y + np.sin(b) * rr * 0.8
            cv.leaf(px, py, px + np.cos(b) * leaf, py + np.sin(b) * leaf * 0.8, leaf * 0.55,
                    z=z + 0.8 + 0.6 * (1 - r) + 0.4 * (1 - rr / cl), dome=0.5, mat=0,
                    tone=tone + 0.08 * up - 0.04 + rng.normal(0, 0.04), rib=0.2)


def spr_kapok():
    """An emergent giant: a grey trunk on flaring buttress roots, its great rounded crown
    standing clear above the rest of the canopy."""
    rng = np.random.default_rng(44)
    w, h = 224, 272
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    for dx, spread, top in ((-1, 44, 188), (1, 46, 184), (-1, 20, 208), (1, 18, 212)):      # buttress roots
        cv.polygon([(cx + dx * 5, top), (cx + dx * spread, h), (cx + dx * (spread - 12), h), (cx, top + 40)],
                   z=0.0 if spread > 30 else 0.3, top=0.8, bevel=3, mat=1, tone=-0.06 if spread > 30 else 0.02)
    cv.stroke([(cx, h), (cx, 180), (cx - 2, 130), (cx, 100)], 16, z=0.4, dome=1.2, taper=(1.3, 0.8), mat=1)
    for side, y, reach in ((-1, 114, 46), (1, 108, 50)):
        cv.stroke([(cx, y), (cx + side * reach * 0.6, y - 16), (cx + side * reach, y - 24)], 7, z=0.6, dome=0.9,
                  taper=(1, 0.5), mat=1)
    _crown(cv, rng, cx, 64, 108, 60, 90, size=(11, 17), leaf=6.5, z=1.0)
    return _prop(cv, [LEAF, ramp('#8c8676', dark=0.3, light=1.2)], relief=1.0, cavity=0.45, shadow=0.55, reach=8)


def spr_canopy_crown():
    """The top of one tree in the canopy: set it on a jungle wall so the canopy edge is a row of
    rounded crowns against the sky, not a hedge."""
    rng = np.random.default_rng(46)
    w, h = 112, 72
    cv = Canvas(w, h, wrap=False, ground=-9)
    _crown(cv, rng, 56, 40, 54, 32, 36, size=(8, 13), leaf=5.5, z=0.5)
    return _prop(cv, [LEAF, LEAF_SUN], relief=1.0, cavity=0.45, shadow=0.55, reach=6)


def _weather(cv, rng, moss_mat, amount=0.58, low=None, lichen_mat=None, n_lichen=8):
    """Age a carved stone: pitting, moss in the hollows (and wherever `low` says), lichen spots."""
    cv.noise(0.18, cells=10, rng=rng)
    solid = cv.id > 0
    m = (smooth_noise(cv.w, cv.h, 6, rng, wrap=False) > amount) & solid
    if low is not None:
        m &= cv.z < low
    cv.mat[m] = moss_mat
    if lichen_mat is not None:
        ys, xs = np.nonzero(solid)
        for i in rng.choice(len(ys), n_lichen, replace=False):
            cv.ellipse(xs[i], ys[i], rng.uniform(0.8, 1.6), rng.uniform(0.6, 1.2), z=cv.z[ys[i], xs[i]] + 0.05,
                       dome=0.1, mat=lichen_mat, rough=0.3, rng=rng)


def spr_stone_head():
    """A colossal carved head in a banded helmet, sunk to the chin in the forest floor: heavy
    lidded eyes, a broad nose, full lips, moss on its crown."""
    rng = np.random.default_rng(3)
    w, h = 88, 80
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(44, 36, 41, 36, z=0.0, dome=2.0, mat=0, power=0.6)                  # the helmet
    for x in (4, 71):                                                                # ear flaps
        cv.box(x, 40, 13, 36, z=0.8, top=0.7, bevel=2.5, rough=0.4, rng=rng, mat=0)
    cv.box(7, 27, 74, 9, z=1.6, top=0.8, bevel=2.0, rough=0.3, rng=rng, mat=0)       # the band
    for x in range(12, 78, 8):
        cv.box(x, 29.5, 4, 4, top=0.35, bevel=0.8, mat=0, mode='carve')
    cv.ellipse(44, 58, 28, 23, z=1.6, dome=1.2, mat=0, power=0.8)                    # the face
    cv.stroke([(22, 43), (40, 42)], 3.2, dome=0.7, mat=0, mode='add')               # brows
    cv.stroke([(48, 42), (66, 43)], 3.2, dome=0.7, mat=0, mode='add')
    for ex in (31, 57):
        cv.leaf(ex - 8, 49, ex + 8, 49, 5.2, dome=1.4, rib=0.0, base=0.5, shape=0.8, mode='carve')   # deep eyes
        cv.stroke([(ex - 8, 46.4), (ex + 8, 46.4)], 2.0, dome=0.6, mat=0, mode='add')                 # lids
    cv.ellipse(44, 58.5, 10, 7.5, dome=1.3, mat=0, mode='add', power=0.6)          # the nose
    for nx in (38.5, 49.5):
        cv.ellipse(nx, 62, 2.2, 1.6, dome=1.0, mode='carve')
    cv.ellipse(44, 68.5, 13, 3.6, dome=1.0, mat=0, mode='add')                      # lips
    cv.ellipse(44, 73.5, 12, 3.8, dome=1.0, mat=0, mode='add')
    cv.stroke([(31, 71), (57, 71)], 1.4, dome=1.0, mode='carve')
    cv.noise(0.14, cells=10, rng=rng)
    solid = cv.id > 0
    yy = np.arange(h)[:, None]
    crown = solid & (yy < 27 + 6 * smooth_noise(w, h, 4, rng, wrap=False)) & (smooth_noise(w, h, 5, rng, wrap=False) > 0.35)
    flaps = solid & ((np.arange(w)[None, :] < 16) | (np.arange(w)[None, :] > 72)) & (yy > 56) & \
        (smooth_noise(w, h, 4, rng, wrap=False) > 0.5)
    cv.mat[crown | flaps] = 1
    for _ in range(9):
        y, x = rng.integers(8, 76), rng.integers(10, 78)
        if solid[y, x]:
            cv.ellipse(x, y, rng.uniform(0.8, 1.5), rng.uniform(0.6, 1.1), z=cv.z[y, x] + 0.05, dome=0.1, mat=2)
    return _prop(cv, [TEMPLE, MOSS, LICHEN], relief=1.4, cavity=0.6, shadow=0.6, dither=0.15)


def spr_stela():
    """A carved stela: a tall slab with a mask in a frame above two columns of glyphs."""
    rng = np.random.default_rng(9)
    w, h = 44, 108
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(4, 108), (4, 12), (10, 3), (34, 3), (40, 12), (40, 108)], z=0.0, top=1.4, bevel=3.0, mat=0)
    cv.polygon([(8, 100), (8, 14), (12, 8), (32, 8), (36, 14), (36, 100)], top=0.35, bevel=1.0, mat=0, mode='carve')
    # the mask: brow, two ringed eyes, a fanged mouth
    cv.box(11, 16, 22, 4, top=0.5, bevel=1, mat=0, mode='add')
    for ex in (16, 28):
        cv.ellipse(ex, 25, 4.2, 4.2, dome=0.6, mat=0, mode='add')
        cv.ellipse(ex, 25, 1.8, 1.8, dome=0.5, mode='carve')
    cv.box(13, 33, 18, 5, top=0.5, bevel=1, mat=0, mode='add')
    for fx in (16, 21, 26):
        cv.box(fx, 37, 2.5, 3, top=0.4, bevel=0.6, mat=0, mode='add')
    for row in range(5):                    # glyph columns
        for col in range(2):
            gx, gy = 9.5 + col * 13, 46 + row * 11
            cv.box(gx, gy, 11.5, 9.5, top=0.45, bevel=1, mat=0, mode='add')
            cv.box(gx + 2, gy + 2, 7.5, 5.5, top=0.25, bevel=0.6, mat=0, mode='carve')
            if rng.random() < 0.5:
                cv.ellipse(gx + 5.7, gy + 4.7, 1.5, 1.5, dome=0.4, mat=0, mode='add')
            else:
                cv.box(gx + 3, gy + 4, 5.5, 1.6, top=0.4, bevel=0.5, mat=0, mode='add')
    _weather(cv, rng, 1, amount=0.68, low=1.0, lichen_mat=2, n_lichen=6)
    foot = (np.arange(h)[:, None] > 88) & (cv.id > 0) & (smooth_noise(w, h, 4, rng, wrap=False) > 0.35)
    cv.mat[foot] = 1
    return _prop(cv, [TEMPLE, MOSS, LICHEN], relief=1.4, cavity=0.6, shadow=0.55, dither=0.15)


# ---------------------------------------------------------------- ruins props

TERRACOTTA = ramp('#b8603a', dark=0.35)
CYPRESS = ramp('#2a4a32', dark=0.3, light=1.5)
OLIVE = ramp('#8a9a6a', dark=0.4, light=1.3)


def _column(cv, rng, cx, top, foot, r, broken=None):
    """A fluted Doric column on a plinth, from `top` (the abacus) down to `foot`: the shaft
    narrows a little as it rises. With `broken` (a row) it is snapped off there."""
    shaft, cut = cv.layer(), cv.layer()
    shaft.box(cx - r - 6, foot - 9, 2 * r + 12, 9, z=0.0, top=1.0, bevel=2.0, rough=0.5, rng=rng, mat=0)
    shaft.stroke([(cx, foot - 8), (cx, top + 14)], 2 * r, z=0.2, dome=1.2, taper=(1.0, 0.84), mat=0)
    for i in (-2, -1, 0, 1, 2):             # flutes, following the taper
        shaft.stroke([(cx + i * r * 0.36, foot - 9), (cx + i * r * 0.30, top + 15)], 1.5, dome=0.35, mode='carve')
    shaft.stroke([(cx - r, top + 16), (cx + r, top + 16)], 1.2, dome=0.4, mode='carve')        # the necking
    shaft.polygon([(cx - r * 0.86, top + 15), (cx + r * 0.86, top + 15), (cx + r + 5, top + 7),
                   (cx - r - 5, top + 7)], z=0.4, top=1.0, bevel=2.5, mat=0)                  # echinus
    shaft.box(cx - r - 6, top, 2 * r + 12, 7.5, z=0.5, top=1.0, bevel=1.5, rough=0.4, rng=rng, mat=0)  # abacus
    if broken is not None:
        xs = np.arange(cv.w)
        jag = broken + 8 * (smooth_noise(cv.w, 1, 4, rng, wrap=False)[0] - 0.5) + 3 * (rng.random(cv.w) - 0.5)
        yy = np.arange(cv.h)[:, None]
        cut.id[yy < jag[None, :]] = 1
        rim = (yy >= jag[None, :]) & (yy < jag[None, :] + 2.5)
        shaft.tone[rim] += 0.12              # the fresh break is paler than the weathered shaft
    for _ in range(3):                      # a few bites knocked out of the edges
        y = rng.uniform(top + 20, foot - 12)
        side = rng.choice([-1, 1])
        cut.ellipse(cx + side * (r + 1), y, rng.uniform(2, 3.5), rng.uniform(2, 4))
    cv.paste(shaft, cut)


def _ruin_finish(cv, rng, lichen=6, stains=True):
    cv.noise(0.15, cells=10, rng=rng)
    solid = cv.id > 0
    if stains:                              # rain streaks running down from the top
        streak = smooth_noise(cv.w, cv.h, max(2, cv.w // 5), rng, wrap=False, cells_y=2) > 0.62
        cv.tone[streak & solid] -= 0.07
    ys, xs = np.nonzero(solid)
    for i in rng.choice(len(ys), min(lichen, len(ys)), replace=False):
        cv.ellipse(xs[i], ys[i], rng.uniform(0.8, 1.6), rng.uniform(0.6, 1.2), z=cv.z[ys[i], xs[i]] + 0.05,
                   dome=0.1, mat=1, rough=0.3, rng=rng)


def spr_column():
    """A Doric column of weathered marble: fluted shaft, cushion capital, square abacus, plinth."""
    rng = np.random.default_rng(2)
    cv = Canvas(44, 140, wrap=False, ground=-9)
    _column(cv, rng, 22, 2, 140, 12)
    _ruin_finish(cv, rng)
    return _prop(cv, [MARBLE, OCHRE], relief=1.2, cavity=0.45, shadow=0.5, dither=0.2)


def spr_broken_column():
    """A column snapped off partway up, its break still pale against the weathered shaft."""
    rng = np.random.default_rng(6)
    cv = Canvas(44, 140, wrap=False, ground=-9)
    _column(cv, rng, 22, 2, 140, 12, broken=58)
    _ruin_finish(cv, rng)
    return _prop(cv, [MARBLE, OCHRE], relief=1.2, cavity=0.45, shadow=0.5, dither=0.2)


def spr_column_drum():
    """A fallen column drum on its side: its fluted end toward you, the round of it going back."""
    rng = np.random.default_rng(8)
    w, h = 72, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(22, 26), (60, 22)], 34, z=0.0, dome=1.2, taper=(1.0, 0.96), mat=0, tone=-0.1)   # the body
    for k in range(-4, 5):                  # flutes running back along it
        dy = k * 3.5
        cv.stroke([(26, 26 + dy), (60, 22 + dy * 0.96)], 1.1, z=0, dome=0.55, mode='carve')
    end, cut = cv.layer(), cv.layer()
    end.ellipse(20, 26, 14, 17, z=1.6, dome=0.5, mat=0, power=0.9, tone=0.1)                   # the end face, lit
    for k in range(20):                     # flutes scallop the rim
        a = 2 * np.pi * k / 20
        cut.ellipse(20 + np.cos(a) * 14.5, 26 + np.sin(a) * 17.5, 1.7, 2.0)
    end.ellipse(20, 26, 3, 3.5, dome=0.5, mode='carve')                                        # the dowel hole
    a = np.linspace(0, 2 * np.pi, 48)
    end.stroke(list(zip(20 + np.cos(a) * 11.5, 26 + np.sin(a) * 14)), 0.9, z=0, dome=0.3, mode='carve')  # a worn ring
    cv.paste(end, cut)
    rim = np.zeros(cv.id.shape, bool)       # the body darkens where the face stands proud of it
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    d = ((xx - 20) / 15.5) ** 2 + ((yy - 26) / 18.5) ** 2
    rim[(d >= 1.0) & (d < 1.5) & (xx > 20)] = True
    cv.tone[rim & (cv.id > 0)] -= 0.12
    _ruin_finish(cv, rng, lichen=5)
    return _prop(cv, [MARBLE, OCHRE], relief=1.2, cavity=0.45, shadow=0.5, dither=0.2)


def spr_marble_head():
    """A colossal marble head, broken off at the neck: curled hair, a straight nose, blank eyes."""
    rng = np.random.default_rng(13)
    w, h = 68, 80
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(34, 44, 24, 31, z=0.0, dome=1.8, mat=0, power=0.7)                  # the head
    cv.polygon([(20, 66), (48, 66), (50, 80), (18, 80)], z=0.0, top=1.2, bevel=3, mat=0)   # the neck stump
    for _ in range(46):                     # curls over the crown and the temples
        a = rng.uniform(np.pi * 0.95, np.pi * 2.05)
        r = rng.uniform(0.7, 1.0)
        x, y = 34 + np.cos(a) * 24 * r, 40 + np.sin(a) * 30 * r
        cv.ellipse(x, y, 3.2, 2.8, z=1.4, dome=0.7, mat=0, tone=rng.normal(0, 0.03))
    cv.ellipse(34, 50, 17, 20, z=1.6, dome=0.8, mat=0, power=0.8)                   # the face
    cv.stroke([(21, 40), (32, 39)], 2.6, dome=0.6, mat=0, mode='add')               # brows
    cv.stroke([(36, 39), (47, 40)], 2.6, dome=0.6, mat=0, mode='add')
    for ex in (27, 41):
        cv.leaf(ex - 5, 44, ex + 5, 44, 3.6, dome=0.9, rib=0.0, base=0.5, shape=0.8, mode='carve')
        cv.ellipse(ex, 44, 1.0, 1.0, dome=0.5, mode='carve')                         # drilled pupils
    cv.polygon([(32, 41), (36, 41), (38.5, 55), (29.5, 55)], top=0.9, bevel=1.5, mat=0, mode='add')   # the nose
    cv.stroke([(28, 60), (40, 60)], 1.2, dome=0.7, mode='carve')                     # the mouth
    cv.ellipse(34, 62, 5, 2.2, dome=0.5, mat=0, mode='add')
    cv.ellipse(34.5, 53.5, 3.2, 2.6, dome=0.7, mode='carve')    # the tip of the nose, long gone:
    yy, xx = np.mgrid[0:h, 0:w]                                  # a raw, paler break where it was
    cv.tone[(xx - 34.5) ** 2 / 10 + (yy - 53.5) ** 2 / 7 < 1] += 0.1
    _ruin_finish(cv, rng, lichen=5)
    return _prop(cv, [MARBLE, OCHRE], relief=1.3, cavity=0.5, shadow=0.5, dither=0.2)


def spr_amphora():
    """A terracotta amphora: a tall body on a pointed foot, two handles, a black painted band."""
    rng = np.random.default_rng(4)
    w, h = 30, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    for side in (-1, 1):                    # handles behind the neck
        cv.stroke([(15 + side * 4, 9), (15 + side * 10, 10), (15 + side * 10, 17), (15 + side * 7, 21)], 2.4,
                  z=0.0, dome=0.6, mat=0, tone=-0.05)
    cv.ellipse(15, 31, 11.5, 17, z=0.4, dome=1.4, mat=0, power=0.6)                # the body
    cv.stroke([(15, 46), (15, 54)], 4.2, z=0.4, dome=0.8, taper=(1.0, 0.6), mat=0)  # the foot
    cv.stroke([(15, 18), (15, 6)], 7, z=0.6, dome=1.0, mat=0)                       # the neck
    cv.box(10, 3, 10, 3.5, z=1.0, top=0.6, bevel=1, mat=0)                          # the rim
    band = (np.arange(h)[:, None] > 24) & (np.arange(h)[:, None] < 31) & (cv.id > 0)
    cv.mat[band] = 1
    _ruin_finish(cv, rng, lichen=0, stains=False)
    return _prop(cv, [TERRACOTTA, ramp('#2a1e18', light=1.6)], relief=1.0, cavity=0.3, shadow=0.4, dither=0.2)


def spr_cypress():
    """A Mediterranean cypress: a tall dark flame of a tree, close-leaved, on a short trunk."""
    rng = np.random.default_rng(21)
    w, h = 40, 160
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(20, 160), (20, 140)], 4, z=0.0, dome=0.8, mat=1)
    for i in range(240):                    # leaf sprays packed into a flame outline
        t = rng.random()                    # 0 at the foot of the crown, 1 at the tip
        y = 146 - t * 142
        half = 15 * np.sin(np.pi * min(1.0, 0.1 + t * 0.95)) ** 0.8 * (1 - t) ** 0.35
        x = 20 + rng.uniform(-1, 1) * half
        depth = 1 - abs(x - 20) / max(half, 1)
        cv.ellipse(x, y, rng.uniform(2.5, 4), rng.uniform(3, 5), z=depth * 1.5 + i * 0.001, dome=0.6, mat=0,
                   tone=rng.normal(0, 0.04))
    return _prop(cv, [CYPRESS, BARK], relief=1.0, cavity=0.5, shadow=0.5)


def spr_olive_tree():
    """An old olive: a twisted, split grey trunk and an airy silver-green crown with light through it."""
    rng = np.random.default_rng(17)
    w, h = 128, 112
    cv = Canvas(w, h, wrap=False, ground=-9)
    for dx, bend in ((-5, -10), (4, 9), (0, 2)):            # the trunk: strands twisting round each other
        cv.stroke([(64 + dx, 112), (64 + dx + bend * 0.4, 96), (64 + dx - bend * 0.3, 80), (64 + dx + bend, 62)],
                  7, z=0.3, dome=1.0, taper=(1.3, 0.8), mat=1, tone=rng.normal(0, 0.05))
    for side, reach in ((-1, 44), (1, 46), (-1, 24), (1, 22)):
        cv.stroke([(64, 64), (64 + side * reach * 0.5, 50), (64 + side * reach, 44)], 4, z=0.5, dome=0.8,
                  taper=(1.0, 0.4), mat=1)
    for _ in range(34):                     # the crown: loose clusters of narrow silvery leaves
        a = rng.uniform(np.pi * 1.05, np.pi * 1.95)
        r = rng.uniform(0.3, 1.0)
        cx, cy = 64 + np.cos(a) * 56 * r, 50 + np.sin(a) * 36 * r
        for _ in range(16):
            b = rng.uniform(0, 2 * np.pi)
            x, y = cx + rng.normal(0, 4.5), cy + rng.normal(0, 3.5)
            cv.leaf(x, y, x + np.cos(b) * 5, y + np.sin(b) * 3, 1.8, z=1.0 + (1 - r), dome=0.4, rib=0.0, mat=0,
                    tone=rng.normal(0.02, 0.05) + (0.06 if np.sin(b) < 0 else -0.04))
    return _prop(cv, [OLIVE, ramp('#6a6458', dark=0.3)], relief=1.0, cavity=0.35, shadow=0.45)


def spr_poppies():
    """A clump of red poppies among dry grass."""
    rng = np.random.default_rng(29)
    w, h = 44, 28
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(14):
        x = rng.uniform(4, 40)
        a = np.radians(rng.uniform(250, 290))
        L = rng.uniform(10, 18)
        cv.stroke([(x, 28), (x + np.cos(a) * L, 28 + np.sin(a) * L)], 1.2, z=0.0, dome=0.3, mat=0)
    for _ in range(7):
        x, y = rng.uniform(6, 38), rng.uniform(5, 16)
        cv.stroke([(x, y), (x + rng.normal(0, 1.5), 28)], 1.0, z=0.2, dome=0.3, mat=2)
        cv.ellipse(x, y, rng.uniform(2.6, 3.4), rng.uniform(2.0, 2.6), z=1.0, dome=0.8, mat=1, power=0.7)
        cv.ellipse(x, y - 0.3, 0.9, 0.8, z=1.9, dome=0.2, mat=3)
    return _prop(cv, [GRASS_DRY, ramp('#d8302a'), GRASS_GREEN, ramp('#2a1a20')], relief=1.0, cavity=0.3, shadow=0.4)


# ---------------------------------------------------------------- beach props

PALM_LEAF = ramp('#4a8a32', dark=0.28, light=1.4)
PALM_TRUNK = ramp('#8a7a5e', dark=0.3)
DRIFT = ramp('#b8b0a0', dark=0.4, light=1.15)
CANVAS_RED = ramp('#c04a3a')
CANVAS_CREAM = ramp('#e8dcc0', dark=0.5, light=1.08)


def spr_palm(lean=0.0, part='all'):
    """A coconut palm: a ringed trunk curving up out of the sand, long fronds arching out of the
    crown with their leaflets hanging in a curtain, coconuts bunched under them. `lean` tips the
    tree over to one side, the way palms lean out over a beach. `part` 'trunk' or 'crown' draws
    only that, in the same frame, so the two stack into one tree (see the palm_3d prefab)."""
    rng = np.random.default_rng(55 + int(lean * 10))
    w, h = 200, 208
    cx0 = 100 - 40 * lean
    base = (cx0, h)
    top = (cx0 + 70 * lean + 4, 66 + 20 * lean)
    mid = ((base[0] + top[0]) / 2 - 12 + 6 * lean, (base[1] + top[1]) / 2 + 10 * lean)
    t = np.linspace(0, 1, 24)[:, None]
    trunk = (1 - t) ** 2 * np.array(base) + 2 * (1 - t) * t * np.array(mid) + t ** 2 * np.array(top)
    cv = Canvas(w, h, wrap=False, ground=-9)
    if part != 'crown':
        cv.stroke(trunk, 10, z=0.0, dome=1.0, taper=(1.3, 0.8), mat=1)
        for i in range(1, 23):              # the rings left by old fronds
            p, q = trunk[i], trunk[i + 1]
            nx, ny = -(q[1] - p[1]), q[0] - p[0]
            n = np.hypot(nx, ny)
            nx, ny = nx / n * 6.5, ny / n * 6.5
            cv.stroke([(p[0] - nx, p[1] - ny), (p[0] + nx, p[1] + ny)], 1.0, dome=0.35, mode='carve')
    if part == 'trunk':
        return _prop(cv, [PALM_LEAF, PALM_TRUNK, ramp('#6a5a2a')], relief=1.0, cavity=0.35, shadow=0.45)
    cx, cy = top
    fronds = [(-172, 80, 0.62, -0.12), (-8, 80, 0.62, -0.1), (-150, 76, 0.45, 0.0), (-30, 76, 0.45, 0.0),
              (-195, 64, 0.9, -0.16), (15, 64, 0.9, -0.14), (-122, 64, 0.32, 0.05), (-58, 64, 0.32, 0.05),
              (-92, 50, 0.25, 0.08)]
    for k, (ang, L, droop, tone) in enumerate(fronds):
        pts = _arc((cx, cy), ang + rng.normal(0, 3), L, droop + rng.normal(0, 0.04), n=16)
        _frond(cv, pts, 15, angle=70, mat=0, z=0.5 + 0.1 * k, tone=tone, width=1.5, step=2.4, droop=1.1, rng=rng,
               ragged=0.7)
    for dx, dy in ((-5, 5), (3, 6), (-1, 9), (6, 3)):                   # coconuts
        cv.ellipse(cx + dx, cy + dy, 3.8, 3.6, z=1.8, dome=0.8, mat=2, tone=rng.normal(0, 0.05))
    return _prop(cv, [PALM_LEAF, PALM_TRUNK, ramp('#6a5a2a')], relief=1.0, cavity=0.35, shadow=0.45)


def spr_palm_lean():
    return spr_palm(lean=1.0)


def spr_coconuts():
    """A few fallen coconuts, one still green."""
    w, h = 32, 14
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, y, r, mat in ((8, 8, 5, 0), (18, 9, 4.6, 0), (25, 9, 4.2, 1)):
        cv.ellipse(x, y, r, r * 0.9, z=0.0, dome=1.0, mat=mat)
        cv.stroke([(x - r * 0.6, y - 1), (x + r * 0.5, y + 1)], 0.8, dome=0.3, mode='carve')
    return _prop(cv, [ramp('#6a4a2a'), ramp('#7a8a3a')], relief=1.0, cavity=0.3, shadow=0.4)


def spr_canoe():
    """An outrigger canoe drawn up on the sand: a dark hull, booms out to a slim float, a paddle."""
    w, h = 136, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(18, 10), (118, 10)], 3.2, z=-0.2, dome=0.6, mat=2)                 # the float, behind
    for x in (44, 92):                      # booms
        cv.stroke([(x, 22), (x - 2, 9)], 2.4, z=0.6, dome=0.6, mat=1)
    cv.polygon([(4, 16), (16, 20), (120, 20), (132, 15), (126, 28), (12, 28)], z=0.2, top=1.2, bevel=3, mat=0)
    cv.stroke([(10, 18), (126, 18)], 1.6, z=1.0, dome=0.4, mat=1)                  # the gunwale
    cv.stroke([(70, 13), (104, 25)], 1.6, z=1.5, dome=0.5, mat=1)                  # a paddle laid across
    cv.ellipse(106, 26, 3.4, 2.0, z=1.5, dome=0.5, angle=20, mat=1)
    return _prop(cv, [ramp('#5a3a22'), ramp('#a07a4a'), ramp('#8a6a44')], relief=1.0, cavity=0.35, shadow=0.45)


def spr_tiki_torch():
    """A bamboo torch: a pole, a woven cup and a burning flame."""
    w, h = 18, 104
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(9, 104), (9, 22)], 4.2, z=0.0, dome=1.0, mat=0)
    for y in (40, 66, 90):
        cv.stroke([(6.5, y), (11.5, y)], 1.2, dome=0.4, mat=0, mode='add')
    cv.polygon([(3, 12), (15, 12), (13, 24), (5, 24)], z=0.4, top=1.0, bevel=1.5, mat=1)
    for y in (15, 19):
        cv.stroke([(4, y), (14, y)], 1.0, dome=0.3, mode='carve')
    flame = cv.layer()
    flame.leaf(9, 13, 8, 0, 9, z=1.0, dome=0.6, rib=0.0, base=0.3, shape=0.8, mat=2)
    flame.leaf(9, 13, 10, 4, 5, z=1.4, dome=0.4, rib=0.0, base=0.3, shape=0.8, mat=3)
    cv.paste(flame)
    rgba, em = _prop(cv, [BAMBOO, STRAW, ramp('#f08a20', dark=0.6, light=1.2), ramp('#ffe070', dark=0.8, light=1.1)],
                     relief=1.0, cavity=0.3, shadow=0.3)
    em[:14][rgba[:14, :, 3] > 0.5] = 1.0
    return rgba, em


def spr_hammock():
    """A striped hammock slung between two weathered posts."""
    w, h = 128, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (6, 122):
        cv.stroke([(x, 64), (x, 6)], 5, z=0.0, dome=1.0, mat=2)
    xs = np.linspace(14, 114, 40)
    sag = 30 * np.sin(np.pi * (xs - 14) / 100) ** 0.9
    for side in (0, 1):                     # cords out to the posts
        x0, x1 = (6, 18) if side == 0 else (122, 110)
        cv.stroke([(x0, 12), (x1, 22)], 1.0, z=0.2, dome=0.3, mat=3)
        cv.stroke([(x0, 12), (x1, 30)], 1.0, z=0.2, dome=0.3, mat=3)
    for i, (x, sy) in enumerate(zip(xs, sag)):
        stripe = int((x - 14) // 9) % 2
        cv.stroke([(x, 20 + sy), (x, 30 + sy * 0.95)], 3.4, z=0.6, dome=0.6, mat=stripe)
    return _prop(cv, [CANVAS_RED, CANVAS_CREAM, DRIFT, ramp('#b09a6a')], relief=1.0, cavity=0.35, shadow=0.45)


def spr_driftwood():
    """A bleached branch thrown up by the sea, its roots still clawing at the air."""
    rng = np.random.default_rng(37)
    w, h = 76, 26
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(6, 20), (30, 17), (58, 19), (70, 16)], 6, z=0.0, dome=1.0, taper=(1.3, 0.6), mat=0)
    for a in (-130, -100, -160, 160):       # the root end
        r = np.radians(a)
        cv.stroke([(8, 19), (8 + np.cos(r) * 10, 19 + np.sin(r) * 9)], 2.0, z=0.4, dome=0.6, taper=(1, 0.4), mat=0)
    cv.stroke([(40, 18), (48, 8), (52, 5)], 2.2, z=0.5, dome=0.6, taper=(1, 0.4), mat=0)
    for x in range(14, 66, 7):
        cv.stroke([(x, 15), (x + 5, 21)], 0.9, dome=0.3, mode='carve')
    return _prop(cv, [DRIFT], relief=1.0, cavity=0.35, shadow=0.4)


def spr_surf(glow=False):
    """The lip of a spent wave: a low line of foam, solid along its foot and lacy along its crest.
    Set a row of them along a waterline: being sprites they stay visible from a standing eye
    height, where a foam decal on the ground would be seen edge-on; the solid foot keeps them
    a clean line when they are only two or three pixels tall. The glowing kind is the surf on a
    night of bioluminescence."""
    rng = np.random.default_rng(91 if glow else 90)
    w, h = 96, 10
    y = np.arange(h)[:, None] + 0.5
    crest = 2 + 3 * smooth_noise(w, 1, 9, rng, wrap=False)[0] + 1.5 * smooth_noise(w, 1, 23, rng, wrap=False)[0]
    foot = y > h - 4
    lace = (y > crest[None, :]) & (smooth_noise(w, h, 14, rng, wrap=False) > 0.34)
    xs = np.arange(w)[None, :]
    ends = np.minimum(xs, w - 1 - xs) > np.where(foot, 1, 5)
    a = ((foot | lace) & ends).astype(np.float32)
    light = np.clip(1.1 - (y - crest[None, :]) / h, 0.55, 1.0)
    rp = ramp('#5ae8f0', dark=0.55, light=1.3) if glow else ramp('#e8f0ec', dark=0.65, light=1.08)
    rgb = _paint_light(np.broadcast_to(light, (h, w)), rp, 0.4)
    rgba = np.concatenate([rgb, a[..., None]], -1).astype(np.float32)
    em = (a * 0.9).astype(np.float32) if glow else np.zeros((h, w), np.float32)
    return rgba, em


# ---------------------------------------------------------------- decals

def _foam(glow=False):
    """A band of lacy surf foam, soft at its edges, for laying along a shoreline."""
    rng = np.random.default_rng(61 if glow else 60)
    w, h = 64, 32
    y = np.arange(h)[:, None]
    band = np.exp(-((y - 16) / 9.0) ** 2)
    lace = smooth_noise(w, h, 6, rng, wrap=False)
    holes = smooth_noise(w, h, 14, rng, wrap=False)
    a = np.clip((lace * band - 0.12) * 3.5, 0, 1) * (holes < 0.68)
    a *= np.clip(1 - np.abs(np.arange(w)[None, :] - w / 2) / (w / 2), 0, 1) ** 0.3
    a = np.round(a * 3) / 3                 # a few steps of opacity, not a smooth gradient
    c = np.array([0.55, 0.95, 1.0] if glow else [0.95, 0.97, 0.94], np.float32)
    rgb = np.broadcast_to(c, (h, w, 3)) * (0.82 + 0.18 * holes[..., None])
    rgba = np.concatenate([rgb, (a * 0.9)[..., None]], -1).astype(np.float32)
    em = (a * 0.9).astype(np.float32) if glow else np.zeros((h, w), np.float32)
    return rgba, em


def dec_starfish():
    """An orange starfish on the sand."""
    w = h = 24
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(5):
        a = np.radians(-90 + 72 * k + 8)
        cv.stroke([(12, 12), (12 + np.cos(a) * 10, 12 + np.sin(a) * 10)], 4.6, z=0.0, dome=0.8, taper=(1.0, 0.35), mat=0)
    cv.ellipse(12, 12, 3.6, 3.6, z=0.6, dome=0.5, mat=0)
    rgba = cv.paint([ramp('#e07a3a')], cv.light(relief=1.0, cavity=0.3, shadow=0.4), dither=0.25)
    return outline_sprite(rgba).astype(np.float32), np.zeros((h, w), np.float32)


def dec_shells():
    """Shells washed up together: a scallop, a little spiral, chips of white."""
    rng = np.random.default_rng(64)
    w, h = 32, 24
    cv = Canvas(w, h, wrap=False, ground=-9)
    for i in range(7):                      # the scallop's ribs, fanning out
        a = np.radians(-150 + i * 20)
        cv.stroke([(10, 16), (10 + np.cos(a) * 8, 16 + np.sin(a) * 8)], 2.6, z=0.2, dome=0.7, mat=0)
    t = np.linspace(0, 3.4 * np.pi, 30)
    r = 0.6 + t / (3.4 * np.pi) * 4.2
    cv.stroke(np.stack([23 + r * np.cos(t), 13 + r * np.sin(t) * 0.8], 1), 2.0, z=0.3, dome=0.6, mat=1)
    for _ in range(5):
        cv.ellipse(rng.uniform(4, 28), rng.uniform(17, 22), 1.0, 0.7, z=0.2, dome=0.4, mat=0)
    rgba = cv.paint([SHELL, ramp('#d8a080')], cv.light(relief=1.0, cavity=0.3, shadow=0.4), dither=0.25)
    return outline_sprite(rgba).astype(np.float32), np.zeros((h, w), np.float32)


def dec_lily_pads():
    """Lily pads on still water, notched, rimmed with light, one opening flower."""
    rng = np.random.default_rng(66)
    w = h = 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    for (x, y, r) in ((14, 16, 9), (32, 12, 7), (30, 31, 10), (13, 35, 6.5), (41, 25, 5)):
        pad, cut = cv.layer(), cv.layer()
        pad.ellipse(x, y, r, r * 0.9, z=0.0, dome=0.3, mat=0, tone=rng.normal(0, 0.05), power=0.9)
        a = rng.uniform(0, 2 * np.pi)
        cut.polygon([(x, y), (x + np.cos(a - 0.25) * r * 1.2, y + np.sin(a - 0.25) * r * 1.2),
                     (x + np.cos(a + 0.25) * r * 1.2, y + np.sin(a + 0.25) * r * 1.2)], bevel=0.5)
        cv.paste(pad, cut)
    for k in range(6):                      # the flower
        a = np.radians(k * 60 + 15)
        cv.leaf(30, 30, 30 + np.cos(a) * 5, 30 + np.sin(a) * 5, 3.2, z=0.8, dome=0.6, rib=0.0, mat=1)
    cv.ellipse(30, 30, 1.4, 1.4, z=1.3, dome=0.3, mat=2)
    rgba = cv.paint([ramp('#3a7a3a'), ramp('#f0a0c0', dark=0.55, light=1.1), ramp('#f0d040')],
                    cv.light(relief=1.0, cavity=0.3, shadow=0.4), dither=0.25)
    return outline_sprite(rgba).astype(np.float32), np.zeros((h, w), np.float32)


def dec_seaweed():
    """A tangle of dark weed left on the sand by the tide."""
    rng = np.random.default_rng(68)
    w, h = 44, 22
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(9):
        x, y = rng.uniform(6, 38), rng.uniform(6, 16)
        a = rng.uniform(0, 2 * np.pi)
        pts = [(x, y)]
        for _ in range(4):
            a += rng.normal(0, 0.7)
            pts.append((pts[-1][0] + np.cos(a) * 4, pts[-1][1] + np.sin(a) * 2.5))
        cv.stroke(pts, rng.uniform(1.4, 2.4), z=rng.random(), dome=0.5, mat=int(rng.random() < 0.3))
    rgba = cv.paint([ramp('#3a4a22'), ramp('#6a5a2a')], cv.light(relief=1.0, cavity=0.3, shadow=0.4), dither=0.25)
    return rgba.astype(np.float32), np.zeros((h, w), np.float32)


# ---------------------------------------------------------------- ground cover
# Reworks of the original grass and rocks, drawn the same way as everything above.

def _tuft(seed, ramps, blades=32, w=44, h=30):
    """A tuft of grass: thin blades springing from one root and arching over, the outer ones
    lower and in shadow. No outline: on blades this thin it would only thicken them."""
    rng = np.random.default_rng(seed)
    cv = Canvas(w, h, wrap=False, ground=-9)
    for i in range(blades):
        a = np.radians(rng.uniform(-158, -22))
        L = rng.uniform(0.5, 1.0) * (h - 2) * (1 - 0.3 * abs(np.cos(a)))
        x0 = w / 2 + rng.normal(0, 2.5)
        lean = np.cos(a)
        tip = (x0 + lean * L * 1.15, h - 1 + np.sin(a) * L * 0.85 + abs(lean) * L * 0.35)
        mid = (x0 + lean * L * 0.55, h - 1 + np.sin(a) * L * 0.62)
        cv.stroke([(x0, h - 1), mid, tip], rng.uniform(1.6, 2.0), z=0.3 * np.sin(-a) + i * 0.01, dome=0.6,
                  taper=(1.0, 0.75), mat=int(rng.integers(0, len(ramps))),
                  tone=rng.normal(0, 0.05) - 0.14 * abs(lean))
    rgba = cv.paint(ramps, cv.light(relief=1.0, cavity=0.3, shadow=0.4), dither=0.25)
    return rgba.astype(np.float32), np.zeros((h, w), np.float32)


def spr_grass_tuft():
    """A tuft of green grass."""
    return _tuft(81, [ramp('#5a7a34'), ramp('#7a8a3a')])


def spr_dry_tuft():
    """A tuft of sunburnt grass: the summer hillside, the ruin, the dune."""
    return _tuft(83, [GRASS_DRY, ramp('#a8904e')])


def spr_rocks():
    """A few stones half sunk in the ground: lit tops, shadowed undersides, a crack or two."""
    rng = np.random.default_rng(85)
    w, h = 64, 22
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, y, rx, ry in ((14, 15, 11, 7), (34, 14, 13, 8.5), (52, 17, 8, 5), (25, 18, 6, 4)):
        stone = cv.layer()
        stone.ellipse(x, y, rx, ry, z=0.0, dome=1.6, rough=0.1, rng=rng, mat=0, tone=rng.normal(0, 0.05), power=0.6)
        if rx > 10:
            a = rng.uniform(0, np.pi)
            stone.stroke([(x - np.cos(a) * rx * 0.5, y - np.sin(a) * ry * 0.4), (x, y), (x + rx * 0.3, y + ry * 0.5)],
                         1.0, dome=0.5, mode='carve')
        cv.paste(stone)
    m = (smooth_noise(w, h, 8, rng, wrap=False) > 0.8) & (cv.id > 0)
    cv.mat[m] = 1
    return _prop(cv, [ramp('#666258', dark=0.28, light=1.2), LICHEN], relief=1.2, cavity=0.45, shadow=0.5)


# ---------------------------------------------------------------- fringe cards
# Long see-through strips with plants stamped into them, for the layered edge of a jungle: a
# `fringe` wall stands a few of these in front of each face, sparse at the front and dense at
# the back, so the edge of the forest has depth as the camera moves. Each card is 8 units long
# at 64 pixels a unit, the textures' own density, and tiles end to end.

CARD_PX = 64
CARD_W = 8 * CARD_PX


def _stamp(card, rgba, x, bottom, height, flip=False):
    """Paste a sprite into a card: centred on column x, its foot on row `bottom`, `height` units
    tall, wrapping round the card's ends so the card still tiles."""
    from PIL import Image
    th, tw = rgba.shape[:2]
    h = max(1, int(round(height * CARD_PX)))
    w = max(1, int(round(tw * h / th)))
    im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').resize((w, h), Image.NEAREST)
    src = np.asarray(im, np.float32) / 255
    if flip:
        src = src[:, ::-1]
    H, W = card.shape[:2]
    top = int(round(bottom)) - h
    left = int(round(x - w / 2))
    for shift in (-W, 0, W):
        x0, x1 = max(0, left + shift), min(W, left + shift + w)
        y0, y1 = max(0, top), min(H, top + h)
        if x1 <= x0 or y1 <= y0:
            continue
        sub = src[y0 - top:y1 - top, x0 - left - shift:x1 - left - shift]
        a = sub[..., 3:4]
        dst = card[y0:y1, x0:x1]
        dst[..., :3] = sub[..., :3] * a + dst[..., :3] * (1 - a)
        dst[..., 3:4] = a + dst[..., 3:4] * (1 - a)


def _card_trunk(height, width, rng):
    """A rainforest trunk for a card: grey bark, a fissure or two, forking into its crown."""
    h, w = max(8, int(height * CARD_PX)), max(4, int(width * CARD_PX))
    cv = Canvas(w * 3, h, wrap=False, ground=-9)
    cx, lean = w * 1.5, rng.uniform(-0.15, 0.15) * w
    cv.stroke([(cx, h), (cx + lean * 0.5, h * 0.5), (cx + lean, 0)], w, z=0.0, dome=1.0, taper=(1.25, 0.75), mat=0)
    for side in (-1, 1):                     # the fork where it meets the crown
        cv.stroke([(cx + lean, h * 0.22), (cx + lean + side * w * 1.1, 0)], w * 0.45, z=0.3, dome=0.8,
                  taper=(1.0, 0.6), mat=0)
    for _ in range(2):
        fx = cx + rng.uniform(-0.25, 0.25) * w
        cv.stroke([(fx, h), (fx + lean * 0.5, h * 0.4)], 1.0, dome=0.4, mode='carve')
    rgba = cv.paint([ramp('#7a7266', dark=0.3)], cv.light(relief=1.0, cavity=0.4, shadow=0.4), dither=0.25)
    return rgba


def _jungle_card(layer):
    """One layer of the jungle's edge, 1 (front) to 4 (back): bushes alone, then a few trees with
    bushes in front of them, then more trees, then a dense wall of trees, crowns and bushes."""
    from assets import get_sprite                # assets imports this module, so not at the top
    rng = np.random.default_rng(300 + layer)
    height = {1: 1.4, 2: 3.4, 3: 4.0, 4: 4.6}[layer]
    H = int(height * CARD_PX)
    card = np.zeros((H, CARD_W, 4), np.float32)
    trees = {1: 0, 2: 3, 3: 6, 4: 9}[layer]
    crowns = {1: 0, 2: 0, 3: 3, 4: 9}[layer]
    bushes = {1: 9, 2: 8, 3: 10, 4: 14}[layer]
    stamps = []
    for _ in range(crowns):                     # tall trees: a trunk up into a mass of leaves, furthest back
        x = rng.uniform(0, CARD_W)
        size = rng.uniform(1.2, 1.9)
        foot = rng.uniform(1.4, height - size * 0.55)          # where the crown's lower edge sits
        stamps.append((x, H, _card_trunk(foot + size * 0.25, rng.uniform(0.16, 0.26), rng), foot + size * 0.25))
        stamps.append((x, H - foot * CARD_PX + size * 0.3 * CARD_PX, 'canopy_crown', size))
    for _ in range(trees):
        kind = rng.choice(['tree_fern', 'banana_plant', 'palm', 'tree_fern', 'banana_plant', 'heliconia'])
        tall = {'tree_fern': (2.0, 2.9), 'banana_plant': (1.5, 2.2), 'palm': (2.8, min(3.8, height - 0.2)),
                'heliconia': (1.0, 1.4)}[kind]
        stamps.append((rng.uniform(0, CARD_W), H, kind, rng.uniform(*tall)))
    for _ in range(bushes):
        kind = rng.choice(['fern', 'fern', 'monstera', 'bromeliad', 'monstera', 'fern'])
        tall = {'fern': (0.45, 0.75), 'monstera': (0.6, 1.0), 'bromeliad': (0.22, 0.32)}[kind]
        stamps.append((rng.uniform(0, CARD_W), H, kind, rng.uniform(*tall)))
    def rank(st):                               # back to front: trunks, their crowns, trees tall first, bushes
        kind = st[2]
        return (0 if not isinstance(kind, str) else 1 if kind == 'canopy_crown' else 2, -st[3])
    for x, bottom, kind, tall in sorted(stamps, key=rank):
        rgba = kind if not isinstance(kind, str) else get_sprite(kind)[0]
        _stamp(card, rgba, x, bottom, tall, flip=bool(rng.random() < 0.5))
    shade = {1: 1.0, 2: 0.94, 3: 0.84, 4: 0.72}[layer]     # deeper into the forest, deeper in shade
    card[..., :3] *= shade
    card[..., 3] = (card[..., 3] > 0.5).astype(np.float32)
    return card, np.zeros(card.shape[:2], np.float32)


# ---------------------------------------------------------------- glass

def glass_image(w, h, rng=None, tone=(0.24, 0.3, 0.36)):
    """What a pane reflects, for the glass pass to lay over what is behind it: a cool grey-blue
    with a soft diagonal streak of sky across it. Solid alpha: the whole pane is glass."""
    rng = rng or np.random.default_rng(0)
    y, x = np.mgrid[0:h, 0:w] + 0.5
    base = np.array(tone, np.float32)
    diag = (x + y * 0.6) / max(w, 1)
    streak = np.exp(-((diag - rng.uniform(0.3, 0.7)) / 0.12) ** 2) * 0.55
    streak += np.exp(-((diag - rng.uniform(0.75, 1.0)) / 0.04) ** 2) * 0.35
    rgb = np.clip(base[None, None, :] * (1 + 1.6 * streak[..., None]), 0, 1)
    return np.concatenate([rgb, np.ones((h, w, 1), np.float32)], -1).astype(np.float32)


def spr_glass_pane():
    """A plain pane of glass, a unit square: give a sprite `"glass": true` and it shows what is
    behind it, tinted and softly blurred (see the glass pass)."""
    return glass_image(64, 64, np.random.default_rng(3)), np.zeros((64, 64), np.float32)


# ---------------------------------------------------------------- animals
# Small enough on screen that hand-placed pixels beat any shape: these are text grids, in the
# same format as the characters (scripts/characters.py), drawn at the cast's pixel size.

ANIMALS = {
    'jaguar': {
        'height': 0.34,
        'palette': {'k': '#24160c', 'o': '#d8963a', 'O': '#f0bc5a', 'd': '#a0662a', 's': '#3a2210',
                    'w': '#f0e4c8', 'e': '#d8f050', 'n': '#5a3028'},
        'emissive': 'e',
        'pixels': [
            '...kk........kk...',
            '..kdok......kodk..',
            '..kookkkkkkkkook..',
            '..koooOOOOOOoook..',
            '..kosooOssOoosok..',
            '..kooeeooooeeook..',
            '..kdooownnwooodk..',
            '..kdoowwkkwwoodk..',
            '...kdowwwwwwodk...',
            '..kddowwwwwwoddk..',
            '.kdoosowwwwosoodk.',
            '.kdosoowwwwoosodk.',
            'kdoosookwwkoosoodk',
            'kdosoookddkooosodk',
            'kdoosookddkoosoodk',
            'kddooookddkooooddk',
            '.kddoowwkkwwooddk.',
            '..kkkkkkkkkkkkkk..',
        ],
    },
    'macaw': {
        'height': 0.3,
        'palette': {'k': '#1a1410', 'r': '#d02a1e', 'R': '#f05a3a', 'y': '#f0c030', 'b': '#2a5ad0',
                    'B': '#5a9af0', 'w': '#f0ece0', 'g': '#e8e0c0', 't': '#6a4a2a', 'T': '#3a2414'},
        'pixels': [
            '.....kkk....',
            '....krRRk...',
            '...krRRrrk..',
            '...krwwkgk..',
            '...krwwwggk.',
            '...krrrkkgk.',
            '..krRrrrkk..',
            '..krRrrrk...',
            '.krrRrrrk...',
            '.kryyrrrk...',
            '.kyyyrrrk...',
            '.kbyyyrrk...',
            '.kbbyyrk....',
            '.kbbbbrk....',
            'TTkkbbbkTTTT',
            'tttkkkkttttt',
            '..kbbk......',
            '..kbBk......',
            '..kbBk......',
            '...kbk......',
            '...kbk......',
            '...kBk......',
            '....k.......',
        ],
    },
    'goat': {
        'height': 0.34,
        'palette': {'k': '#2a2420', 'w': '#ece6da', 'W': '#b8b0a2', 'g': '#8a7462', 'h': '#9a8a70',
                    'H': '#5a4a3a', 'e': '#c89a2a', 'p': '#c09a90'},
        'pixels': [
            '..kk..................',
            '.khHk.................',
            '.khHHk................',
            'kwwkHk................',
            'kwekwHk...............',
            'kwwwwwk...............',
            '.kwwwwwkkkkkkkkkkkkk..',
            '.kpwwwwwwwwwwwwwwwwwk.',
            '..kWwwwwwwwggggwwwwwwk',
            '..kWWwwwwwggggggwwwwk.',
            '...kWkwwwwwggggwwwwwk.',
            '...kWkWwwwwwwwwwwwwWk.',
            '....k.kWWWWWWWWWWWWk..',
            '......kWk.kWk.kWk.kWk.',
            '......kwk.kwk.kwk.kwk.',
            '......kwk.kwk.kwk.kwk.',
            '......kWk.kWk.kWk.kWk.',
            '......kkk.kkk.kkk.kkk.',
        ],
    },
    'crab': {
        'height': 0.08,
        'palette': {'k': '#2a0e0a', 'r': '#d0402a', 'R': '#f07a4a', 'e': '#1a1a1a', 'w': '#f0e0d0'},
        'pixels': [
            '.kk.......kk.',
            'krRk.....kRrk',
            'krrk.k.k.krrk',
            '.kk.kwkwk.kk.',
            '..krRRRRrrk..',
            '.krRrrrrrrrk.',
            'k.krrrrrrrk.k',
            '.k.kkkkkkk.k.',
            'k.k.......k.k',
        ],
    },
    'seagull': {
        'height': 0.14,
        'palette': {'k': '#1a1a1e', 'w': '#f2f2ec', 'g': '#9aa4ac', 'G': '#c4ccd2', 'y': '#e8b020'},
        'pixels': [
            'kk..................kk',
            '.kgk..............kgk.',
            '..gggk..........kggg..',
            '...Gggkk......kkggG...',
            '....GGgggk..kgggGG....',
            '......wwwwkkwwww......',
            '........kwwwwk........',
            '.........kyyk.........',
            '..........kk..........',
        ],
    },
}


def _animal(name):
    from assets import sprite_from_pixels      # assets imports this module, so not at the top
    return sprite_from_pixels(ANIMALS[name])


# how mirror-like each floor is, and how much of the scene's surface_noise it takes: these are
# crisp pixel art, so they take less mottling than the noise-built textures do
TEXTURE_REFLECT = {'shallows': 0.3, 'sea': 0.45, 'wet_sand': 0.28}
TEXTURE_NOISE = {n: 0.6 for n in TEXTURES}
TEXTURE_NOISE.update({'shallows': 0.3, 'sea': 0.3, 'canopy': 0.4, 'colonnade': 0.5, 'colonnade_top': 0.5,
                      'colonnade_broken': 0.5})

SPRITES = {
    'banana_plant': spr_banana_plant, 'monstera': spr_monstera, 'tree_fern': spr_tree_fern,
    'heliconia': spr_heliconia, 'bromeliad': spr_bromeliad, 'liana': spr_liana, 'kapok': spr_kapok,
    'canopy_crown': spr_canopy_crown, 'fern': spr_fern,
    'stone_head': spr_stone_head, 'stela': spr_stela,
    'column': spr_column, 'broken_column': spr_broken_column, 'column_drum': spr_column_drum,
    'marble_head': spr_marble_head, 'amphora': spr_amphora, 'cypress': spr_cypress, 'olive_tree': spr_olive_tree,
    'poppies': spr_poppies,
    'palm': spr_palm, 'palm_lean': spr_palm_lean, 'coconuts': spr_coconuts, 'canoe': spr_canoe,
    'palm_trunk': lambda: spr_palm(part='trunk'), 'palm_crown': lambda: spr_palm(part='crown'),
    'tiki_torch': spr_tiki_torch, 'hammock': spr_hammock, 'driftwood': spr_driftwood,
    'grass_tuft': spr_grass_tuft, 'dry_tuft': spr_dry_tuft, 'rocks': spr_rocks,
    'surf': spr_surf, 'surf_glow': lambda: spr_surf(glow=True), 'glass_pane': spr_glass_pane,
}
SPRITES.update({n: (lambda n=n: _animal(n)) for n in ANIMALS})
SPRITES.update({f'jungle_card_{k}': (lambda k=k: _jungle_card(k)) for k in (1, 2, 3, 4)})
SPRITE_HEIGHT = {
    'banana_plant': 1.7, 'monstera': 0.75, 'tree_fern': 2.4, 'heliconia': 1.1, 'bromeliad': 0.22,
    'canopy_crown': 1.2, 'fern': 0.42,
    'liana': 2.4, 'kapok': 7.5, 'stone_head': 1.5, 'stela': 2.1,
    'column': 1.0, 'broken_column': 1.0, 'column_drum': 0.42, 'marble_head': 1.1, 'amphora': 0.36,
    'cypress': 4.0, 'olive_tree': 2.2, 'poppies': 0.24,
    'palm': 3.2, 'palm_lean': 3.0, 'palm_trunk': 3.2, 'palm_crown': 3.2, 'coconuts': 0.1, 'canoe': 0.3, 'tiki_torch': 0.75, 'hammock': 0.55,
    'driftwood': 0.2, 'grass_tuft': 0.4, 'dry_tuft': 0.36, 'rocks': 0.22, 'surf': 0.1, 'surf_glow': 0.1, 'glass_pane': 1.0,
}
SPRITE_HEIGHT.update({n: d['height'] for n, d in ANIMALS.items()})
SPRITE_HEIGHT.update({'jungle_card_1': 1.4, 'jungle_card_2': 3.4, 'jungle_card_3': 4.0, 'jungle_card_4': 4.6})
PROP_DEFAULTS = {
    'tiki_torch': {'aura': {'color': [1.0, 0.62, 0.25], 'strength': 0.5, 'radius': 0.25}},
}
# plants stand as crossed planes rather than billboards: a star of three (sixths) for round
# clumps, a cross of two for flatter ones, so they have body as the camera moves round them
PROP_DEFAULTS.update({n: {'planes': 3} for n in ('fern', 'bromeliad', 'grass_tuft', 'dry_tuft', 'banana_plant',
                                                  'tree_fern')})
PROP_DEFAULTS.update({n: {'planes': 2} for n in ('monstera', 'heliconia', 'poppies')})
PROP_DEFAULTS['glass_pane'] = {'glass': True, 'planes': 1, 'shadow': False}
NO_CONTACT_SHADOW = {'liana', 'seagull', 'tiki_torch', 'canopy_crown', 'surf', 'surf_glow', 'palm_crown'}
DEBRIS_SETS = {
    'jungle': ['fern', 'fern', 'fern', 'monstera', 'bromeliad', 'bromeliad', 'heliconia', 'mushrooms'],
    'beach': ['coconuts', 'driftwood', 'rocks', 'rocks', 'crab', 'dry_tuft'],
    'ruins': ['column_drum', 'rubble', 'rocks', 'rocks', 'poppies', 'dry_tuft', 'dry_tuft', 'amphora'],
}
# fringe sets: cards back to front, for a wall's `fringe`
FRINGES = {'jungle': ['jungle_card_4', 'jungle_card_3', 'jungle_card_2', 'jungle_card_1']}
DECALS = {
    'foam': lambda: _foam(), 'foam_glow': lambda: _foam(glow=True), 'starfish': dec_starfish,
    'shells': dec_shells, 'lily_pads': dec_lily_pads, 'seaweed': dec_seaweed,
}

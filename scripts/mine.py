"""The mine: a frontier gold mine, drawn with the pixel-art toolkit (scripts/pixelart.py) - its rock,
brown and faceted, with veins of milky quartz, and the gold in them glinting where a lamp catches
it; a pick and a shovel leaning together, a crate of dynamite, a heap of ore.

The timber sets that hold the roof up are `column` and `beam` objects of wood; the track and the
cars on it are objects too (`rails`, `ore_cart` in objects.py).
"""
import numpy as np

from basics import _facets
from biomes import T, _prop, _rng
from pixelart import Canvas, ramp
from pixelfont import PixelFont

ROCK = [ramp('#6e5c48', dark=0.32, light=1.32), ramp('#62564a', dark=0.32, light=1.34),
        ramp('#56483c', dark=0.32, light=1.36)]
CREVICE = ramp('#241c18', dark=0.6, light=1.8)
QUARTZ = ramp('#d6d0c2', dark=0.45, light=1.16)
GOLD = ramp('#e2b444', dark=0.42, light=1.32, warm=0.1)
TIMBER = ramp('#7a6248', dark=0.32, light=1.4)
IRON = ramp('#4a4a4e', dark=0.45, light=1.7)
HICKORY = ramp('#a88456', dark=0.35, light=1.3)
DYNAMITE = ramp('#b8382c', dark=0.4, light=1.3)
FUSE = ramp('#d8c8a0', dark=0.5, light=1.1)
ORE = ramp('#7a6650', dark=0.35, light=1.35)
_FONT = PixelFont()


def _vein(cv, rng, gold):
    """A vein of quartz running across the rock in a gentle wave (it joins up tile to tile, so along a
    wall it is one long seam), a hand wide, and in it - if `gold` - flecks and a thread of gold."""
    y, ph = rng.uniform(24, 40), rng.uniform(0, 6)
    pts = [(x, y + 3.5 * np.sin(x / T * 2 * np.pi + ph) + rng.normal(0, 0.6)) for x in range(-8, T + 9, 8)]
    cv.stroke(pts, 3.6, z=0.7, dome=0.6, mat=4)
    cv.stroke([(x, yy + rng.normal(0, 0.6)) for x, yy in pts], 1.6, z=0.9, dome=0.4, mat=4, tone=0.06)
    flecks = []
    if gold:
        for _ in range(26):
            k = rng.integers(1, len(pts) - 1)
            t = rng.random()
            x = pts[k][0] + 8 * t
            yy = pts[k][1] + (pts[k + 1][1] - pts[k][1]) * t + rng.normal(0, 1.2)
            r = rng.uniform(0.6, 1.4)
            cv.ellipse(x, yy, r, r * 0.8, z=1.2, dome=0.8, mat=5)
            flecks.append((x, yy, r))
        cv.stroke([(x, yy + rng.normal(0, 0.4)) for x, yy in pts[2:6]], 0.9, z=1.1, dome=0.5, mat=5)
    return flecks


def tex_mine_rock(name, vein=False, gold=False):
    """A mine's rock: brown broken masses split by dark cracks, marked by the drills and picks.
    `mine_rock_vein` has a seam of milky quartz running across it; `mine_rock_gold` gold in the
    seam, glinting (it glows a little, so a lamp seems to catch it)."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.6, mat=3)
    _facets(cv, rng, 5, 5, 0.6, 3.0, 0.06)
    for _ in range(14):                                        # the marks of the drills and picks
        x, y = rng.random() * T, rng.random() * T
        cv.stroke([(x, y), (x + rng.uniform(-2, 2), y + rng.uniform(3, 6))], 0.7, dome=0.4, mode='carve')
    cv.noise(0.2, cells=10, rng=rng, octaves=3)
    flecks = _vein(cv, rng, gold) if vein or gold else []
    light = cv.light(relief=1.2, cavity=0.5, shadow=0.55, ambient=0.2, diffuse=0.52)
    rgb = cv.paint(ROCK + [CREVICE, QUARTZ, GOLD], light, dither=0.3)
    em = None
    if gold:
        em = np.zeros((T, T), np.float32)
        em[cv.mat == 5] = 0.25
        for x, y, r in flecks[::3]:                            # a few catch the light hard
            yi, xi = int(y) % T, int(x) % T
            em[yi, xi] = 0.9
            rgb[yi, xi] = np.minimum(1.0, rgb[yi, xi] * 1.5 + 0.2)
    return np.clip(rgb, 0, 1), em


def spr_pick_shovel():
    """A pick and a shovel leaning together against a wall, their handles worn pale."""
    w, h = 30, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(9, h - 1), (17, 6)], 1.5, z=0.6, dome=0.7, mat=0)                  # the shovel's handle
    cv.stroke([(16, 5), (19, 3)], 1.0, z=0.6, dome=0.5, mat=0)
    cv.polygon([(4, h - 13), (13, h - 15), (12, h - 1), (6, h - 1)], z=0.8, top=0.8, bevel=0.8, mat=1)   # blade
    cv.stroke([(22, h - 1), (14, 9)], 1.5, z=1.0, dome=0.7, mat=0)                 # the pick's handle
    cv.stroke([(5, 12), (13, 7), (24, 9), (28, 15)], 1.6, z=1.2, dome=0.6, taper=(0.5, 1.0), mat=1)   # its head
    return _prop(cv, [HICKORY, IRON], relief=1.0, cavity=0.4, shadow=0.45)


def spr_dynamite_crate():
    """A crate of dynamite, its lid off: DYNAMITE stencilled on its side, red sticks with their fuses
    standing in it."""
    w, h = 54, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(10):                                                             # the sticks
        x = 6 + k * 4.4
        cv.box(x, 4, 3.6, 12, z=1.0, top=0.8, bevel=1.0, mat=1, tone=float(np.sin(k) * 0.04))
        cv.stroke([(x + 1.8, 4), (x + 1.8 + np.sin(k * 2) * 2, 0.5)], 0.6, z=1.2, dome=0.3, mat=2)
    cv.box(2, 12, 50, 21, z=0.8, top=0.9, bevel=1.2, mat=0)                         # the crate
    for y in (14, 24):
        cv.box(2, y, 50, 1.2, z=0.9, top=1.0, bevel=0.3, mat=0, tone=-0.1)
    rgba = _prop(cv, [TIMBER, DYNAMITE, FUSE], relief=1.0, cavity=0.4, shadow=0.45)
    m = np.asarray(_FONT.render_mask('DYNAMITE')) > 0
    mh, mw = m.shape
    x0 = max(0, (w - mw) // 2)
    sub = m[:, :min(mw, w - x0)]
    region = rgba[0][16:16 + mh, x0:x0 + sub.shape[1]]
    region[..., :3][sub] = (0.12, 0.08, 0.06)
    return rgba


def spr_ore_heap():
    """A heap of broken ore: rock in lumps, a vein's white quartz in some, a glint of gold - for the
    floor of a stope, or heaped in an ore cart."""
    rng = np.random.default_rng(193)
    w, h = 44, 20
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(60):
        x = rng.uniform(4, w - 4)
        top = h - 2 - (1 - abs(x - w / 2) / (w / 2)) * 13
        r = rng.uniform(1.6, 3.4)
        cv.ellipse(x, rng.uniform(top + r * 0.6, h - 2), r, r * 0.8, z=1.0 + rng.random(), dome=1.0, rough=0.3, rng=rng,
                   mat=int(rng.choice([0, 0, 0, 1, 2], p=[0.3, 0.3, 0.2, 0.15, 0.05])))
    return _prop(cv, [ORE, QUARTZ, GOLD], relief=1.0, cavity=0.45, shadow=0.45)


TEXTURES = {'mine_rock': lambda n: tex_mine_rock(n), 'mine_rock_vein': lambda n: tex_mine_rock(n, vein=True),
            'mine_rock_gold': lambda n: tex_mine_rock(n, gold=True)}
TEXTURE_NOISE = {'mine_rock': 1.4, 'mine_rock_vein': 1.4, 'mine_rock_gold': 1.4}
SPRITES = {'pick_shovel': spr_pick_shovel, 'dynamite_crate': spr_dynamite_crate, 'ore_heap': spr_ore_heap}
SPRITE_HEIGHT = {'pick_shovel': 0.46, 'dynamite_crate': 0.2, 'ore_heap': 0.16}

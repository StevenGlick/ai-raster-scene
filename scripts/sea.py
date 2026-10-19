"""Under the sea, drawn with the pixel-art toolkit (scripts/pixelart.py): the floor of a kelp
forest, the kelp itself standing up toward the light, a shoal of fish, bubbles rising, and what
a wreck leaves on the bottom - an anchor and a broken mast.

As in the other toolkit modules, every shape is stamped into a height field, lit from the upper
left and snapped onto hue-shifted ramps; every texture tiles.
"""
import numpy as np

from biomes import CARD_PX, CARD_W, T, _prop, _rng, _stamp, _tile
from pixelart import Canvas, ramp, smooth_noise

SEABED = ramp('#a89a72', dark=0.36, light=1.2, cool=0.12)
CAUSTIC = ramp('#e6f0d8', dark=0.6, light=1.05)
KELP = ramp('#7a6a2a', dark=0.3, light=1.35, warm=0.12)
KELP_DARK = ramp('#4e4a22', dark=0.32, light=1.4)
FLOAT = ramp('#9a8a3a', dark=0.35, light=1.3)
FISH = ramp('#9ab0b8', dark=0.35, light=1.3, cool=0.2)
FISH_BACK = ramp('#3e5a6a', dark=0.4, light=1.4)
BUBBLE = ramp('#d8f0f4', dark=0.6, light=1.05)
RUST = ramp('#6a4a36', dark=0.35, light=1.4)
GROWTH = ramp('#5a6a3a', dark=0.35)
WRECK_WOOD = ramp('#4a4034', dark=0.3, light=1.4)
ROPE = ramp('#8a7a5a', dark=0.4)


# ---------------------------------------------------------------- textures

def tex_seabed(name):
    """The floor of a kelp forest seen through clear water: pale sand in gentle ripples, a scatter
    of shell and pebble, and over it the net of light the waves above focus onto the bottom."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    xs = np.arange(T)[None, :]
    ys = np.arange(T)[:, None]
    phase = 2 * np.pi * (3 * ys + 2 * xs) / T + 3.0 * smooth_noise(T, T, 3, rng)
    cv.z += (0.25 * np.sin(phase)).astype(np.float32)
    cv.noise(0.1, cells=12, rng=rng)
    for _ in range(14):
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.6, 1.4), rng.uniform(0.5, 1.0), z=0.4,
                   dome=0.6, mat=0, tone=rng.normal(-0.06, 0.06))
    n = 11                                                   # caustics: the edges of Voronoi cells, bright
    sx, sy = rng.random(n) * T, rng.random(n) * T
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    dx = np.abs(xx[..., None] - sx)
    dy = np.abs(yy[..., None] - sy)
    d = np.sort(np.hypot(np.minimum(dx, T - dx), np.minimum(dy, T - dy)), axis=-1)
    edge = d[..., 1] - d[..., 0]
    fade = np.clip(smooth_noise(T, T, 4, rng) * 1.6 - 0.3, 0, 1)
    cv.tone += (0.22 * np.exp(-edge / 1.1) * fade).astype(np.float32)
    return _tile(cv, [SEABED], dither=0.3, relief=1.2, cavity=0.3, shadow=0.3)


def tex_water_surface(name):
    """The surface of the sea seen from below: bright, rippled, its waves gathering the light into
    a net of brighter lines - for the ceiling of an underwater scene. It glows (emissive), since
    the light is coming through it; leave cells of it open and the sun comes down in beams."""
    rng = _rng(name)
    swell = smooth_noise(T, T, 3, rng) * 0.6 + smooth_noise(T, T, 6, rng) * 0.4
    n = 9
    sx, sy = rng.random(n) * T, rng.random(n) * T
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    dx = np.abs(xx[..., None] - sx)
    dy = np.abs(yy[..., None] - sy)
    d = np.sort(np.hypot(np.minimum(dx, T - dx), np.minimum(dy, T - dy)), axis=-1)
    net = np.exp(-(d[..., 1] - d[..., 0]) / 1.6)
    v = np.clip(0.35 + 0.35 * swell + 0.45 * net, 0, 1)
    pal = np.asarray(ramp('#4a9aa8', dark=0.35, light=1.6, cool=0.1), np.float32)
    bay = np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0, (T // 4, T // 4))
    idx = np.clip(np.round(v * (len(pal) - 1) + (bay - 0.5) * 0.5), 0, len(pal) - 1).astype(int)
    return pal[idx], (0.45 + 0.5 * v).astype(np.float32)


# ---------------------------------------------------------------- props

def spr_kelp():
    """A stalk of giant kelp: a stipe swaying up from its holdfast toward the light, long golden
    blades streaming off it, each from a small gas float, and a tangle of blades at the top."""
    rng = np.random.default_rng(201)
    w, h = 80, 252
    cv = Canvas(w, h, wrap=False, ground=-9)
    ph = rng.uniform(0, 2 * np.pi)
    stem = [(40 + 6 * np.sin(t * 2.6 + ph) * t, h - t * (h - 8)) for t in np.linspace(0, 1, 26)]
    for k in range(5):                                       # the holdfast
        a = np.radians(200 + k * 35)
        cv.stroke([(40, h - 3), (40 + np.cos(a) * 9, h - 3 - np.sin(a) * 3 + 3)], 2.0, z=0.0, dome=0.6, mat=1)
    cv.stroke(stem, 2.2, z=0.3, dome=0.7, taper=(1.2, 0.7), mat=1)
    for i in range(3, 25):                                   # floats and blades
        x, y = stem[i]
        side = 1 if i % 2 else -1
        cv.ellipse(x + side * 2.5, y, 1.8, 2.2, z=0.9, dome=0.9, mat=2)
        if rng.random() < 0.3:
            continue
        L = rng.uniform(18, 34)
        rise = rng.uniform(-0.15, 0.6)                       # blades stream out, some up, some drooping
        amp, freq = rng.uniform(1.5, 4.0), rng.uniform(3, 6)
        pts = []
        for t in np.linspace(0, 1, 9):
            pts.append((x + side * (2.5 + L * t * rng.uniform(0.8, 1.0)), y - L * t * rise + amp * np.sin(t * freq + i)))
        cv.stroke(pts, rng.uniform(2.4, 3.6), z=1.0 + rng.random() * 0.4, dome=0.5,
                  taper=lambda u: 0.45 + 0.8 * np.sin(np.pi * np.minimum(1.0, u * 1.05)), mat=0, tone=rng.normal(0, 0.06))
        cv.stroke(pts, 0.5, z=1.6, dome=0.1, mat=1)          # the blade's midrib
    for k in range(7):                                       # the canopy at the top
        a = np.radians(rng.uniform(200, 340))
        x, y = stem[-1]
        L = rng.uniform(10, 18)
        cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L * 0.4)], 3.0, z=1.6, dome=0.5,
                  taper=lambda u: 0.4 + np.sin(np.pi * u), mat=0, tone=0.05)
    return _prop(cv, [KELP, KELP_DARK, FLOAT], relief=1.0, cavity=0.35, shadow=0.4)


def spr_fish_school():
    """A shoal of small silvery fish turning together: thirty-odd bodies all headed one way, dark
    backs and bright bellies, thicker toward the middle of the shoal. Float it with `z`."""
    rng = np.random.default_rng(203)
    w, h = 112, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(34):
        x, y = rng.normal(56, 22), rng.normal(28, 9)
        if not (6 <= x < w - 8 and 4 <= y < h - 4):
            continue
        s = rng.uniform(0.75, 1.15)
        z = rng.random()
        cv.ellipse(x, y, 4.2 * s, 1.5 * s, z=z, dome=0.8, mat=0, tone=rng.normal(0, 0.05))
        cv.polygon([(x - 3.6 * s, y), (x - 6.6 * s, y - 2.0 * s), (x - 6.6 * s, y + 2.0 * s)], z=z, top=0.3, bevel=0.6,
                   mat=1)                                     # the tail
        cv.stroke([(x - 3 * s, y - 0.8 * s), (x + 3.4 * s, y - 0.8 * s)], 0.8 * s, z=z + 0.6, dome=0.2, mat=1)   # the back
    return _prop(cv, [FISH, FISH_BACK], relief=1.0, cavity=0.3, shadow=0.35)


def spr_bubbles():
    """A column of bubbles rising, small at the bottom and swelling as they go up, each a bright
    ring round clear water. Float it from a diver's helmet or a vent; it is drawn light-only."""
    rng = np.random.default_rng(205)
    w, h = 24, 80
    rgba = np.zeros((h, w, 4), np.float32)
    col = np.array(BUBBLE[-2], np.float32)
    y = h - 3.0
    while y > 4:
        r = 0.8 + (h - y) / h * 3.2 * rng.uniform(0.6, 1.1)
        x = 12 + rng.normal(0, 1.6) + np.sin(y * 0.2) * 2
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
        d = np.hypot(xx - x, yy - y)
        ring = (d < r) & (d > r - 1.1)
        glint = (np.hypot(xx - (x - r * 0.4), yy - (y - r * 0.4)) < max(0.6, r * 0.3))
        rgba[ring | glint, :3] = col
        rgba[ring, 3] = 0.85
        rgba[glint, 3] = 1.0
        y -= r * 2 + rng.uniform(1.5, 5)
    return rgba, np.zeros((h, w), np.float32)


def spr_anchor():
    """An old iron anchor standing where it fell, one fluke in the sand: the shank and its stock,
    the ring at the top, the curved arms ending in spade-shaped flukes, all rusted and grown over."""
    rng = np.random.default_rng(207)
    w, h = 44, 56
    cx = 22
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(cx, 10), (cx, h - 8)], 3.2, z=0.4, dome=0.8, mat=0)                      # the shank
    cv.stroke([(cx - 13, 12), (cx + 13, 12)], 2.4, z=1.0, dome=0.8, mat=0)              # the stock
    a = np.linspace(0, 2 * np.pi, 24)
    cv.stroke(list(zip(cx + np.cos(a) * 4, 5 + np.sin(a) * 4)), 1.6, z=0.6, dome=0.6, mat=0)   # the ring
    t = np.linspace(-1, 1, 15)
    cv.stroke(list(zip(cx + t * 16, h - 5 - 10 * t * t)), 3.0, z=0.8, dome=0.8, mat=0)                 # the arms
    for side in (-1, 1):                                                                # the flukes
        fx = cx + side * 16
        cv.polygon([(fx - side * 1, h - 13), (fx + side * 1, h - 22), (fx + side * 6, h - 12)], z=1.2, top=0.8,
                   bevel=1.5, mat=0)
    growth = (smooth_noise(w, h, 5, rng, wrap=False) > 0.62) & (cv.id > 0)
    cv.mat[growth] = 1
    return _prop(cv, [RUST, GROWTH], relief=1.0, cavity=0.4, shadow=0.45)


def spr_wreck_mast():
    """The broken mast of a wreck, leaning: a heavy spar snapped off near the top, a yard hanging
    askew from it, torn rigging trailing, the whole of it furred with weed."""
    rng = np.random.default_rng(209)
    w, h = 72, 196
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(30, h), (38, 20)], 5.0, z=0.4, dome=1.0, taper=(1.1, 0.85), mat=0)       # the mast
    cv.polygon([(35.5, 22), (39, 13), (40.5, 21)], z=0.6, top=0.8, bevel=1.0, mat=0)      # snapped off
    cv.stroke([(10, 58), (66, 44)], 3.0, z=1.0, dome=0.8, mat=0)                          # the yard, askew
    for x0, y0, x1, y1 in ((12, 58, 4, 120), (64, 45, 70, 110), (36, 50, 14, 150), (37, 40, 60, 140)):
        cv.stroke([(x0, y0), ((x0 + x1) / 2 + rng.normal(0, 3), (y0 + y1) / 2), (x1, y1)], 0.8, z=1.4, dome=0.3,
                  mat=2)                                                                  # torn rigging
    for _ in range(40):                                                                   # weed
        x = 30 + (38 - 30) * (1 - rng.random()) + rng.normal(0, 2)
        y = rng.uniform(25, h - 5)
        cv.stroke([(x, y), (x + rng.normal(0, 1.5), y - rng.uniform(3, 8))], 1.0, z=1.6, dome=0.3, taper=(1, 0.3),
                  mat=1)
    return _prop(cv, [WRECK_WOOD, GROWTH, ROPE], relief=1.0, cavity=0.4, shadow=0.45)


def _kelp_card(layer):
    """One layer of a kelp forest's edge, 1 (front) to 2 (back): a few stalks, then a dense stand."""
    from assets import get_sprite
    rng = np.random.default_rng(700 + layer)
    height = {1: 5.0, 2: 5.8}[layer]
    H = int(height * CARD_PX)
    card = np.zeros((H, CARD_W, 4), np.float32)
    k = {1: 4, 2: 9}[layer]
    stamps = []
    off = rng.uniform(0, CARD_W)
    for i in range(k):
        x = (off + (i + rng.uniform(0.15, 0.85)) * CARD_W / k) % CARD_W
        stamps.append((x, rng.uniform(3.6, height - 0.1)))
    for x, tl in sorted(stamps, key=lambda s: -s[1]):
        _stamp(card, get_sprite('kelp')[0], x, H, tl, flip=bool(rng.random() < 0.5))
    card[..., :3] *= {1: 0.95, 2: 0.78}[layer]
    card[..., 3] = (card[..., 3] > 0.5).astype(np.float32)
    return card, np.zeros(card.shape[:2], np.float32)


TEXTURES = {'seabed': lambda n: (tex_seabed(n), None), 'water_surface': tex_water_surface}
TEXTURE_NOISE = {'seabed': 1.2, 'water_surface': 0.3}
SPRITES = {'kelp': spr_kelp, 'fish_school': spr_fish_school, 'bubbles': spr_bubbles, 'anchor': spr_anchor,
           'wreck_mast': spr_wreck_mast}
SPRITES.update({f'kelp_card_{k}': (lambda k=k: _kelp_card(k)) for k in (1, 2)})
SPRITE_HEIGHT = {'kelp': 5.0, 'fish_school': 0.9, 'bubbles': 1.2, 'anchor': 0.75, 'wreck_mast': 3.6,
                 'kelp_card_1': 5.0, 'kelp_card_2': 5.8}
PROP_DEFAULTS = {'bubbles': {'blend': 'additive', 'shadow': False}, 'fish_school': {'shadow': False}}
NO_CONTACT_SHADOW = {'fish_school', 'bubbles'}
FRINGES = {'kelp': ['kelp_card_2', 'kelp_card_1']}
DEBRIS_SETS = {'seabed': ['rocks', 'rocks', 'rocks', 'crab', 'boulder']}

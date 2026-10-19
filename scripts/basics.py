"""Everyday materials and props redrawn with the pixel-art toolkit (scripts/pixelart.py): grass,
a clipped hedge, dirt, gravel, wood panelling and water; a barrel, a broken one, a crate and a
fountain. These are the oldest things in the set - the first versions were noise and flat shapes
- and they turn up in a great many scenes.

As in the other toolkit modules, shapes are stamped into a height field, lit from the upper left
and snapped onto hue-shifted ramps; every texture tiles without a seam.
"""
import numpy as np

from biomes import T, _leaf_layers, _prop, _rng, _tile
from dream import _lathe
from pixelart import Canvas, ramp, smooth_noise

GRASS = [ramp('#3e6a2a', dark=0.3), ramp('#5a8a32'), ramp('#9aa848', dark=0.45, light=1.2)]
HEDGE = [ramp('#2e5a2a', dark=0.3), ramp('#3e6e30'), ramp('#24482a', dark=0.3)]
SOIL = ramp('#5a4632', dark=0.35)
CLOD = ramp('#6e563c', dark=0.35)
PEBBLE = [ramp('#8a8478', dark=0.35), ramp('#9a8a70', dark=0.35), ramp('#6e6a64', dark=0.35)]
WOOD = ramp('#6a4428', dark=0.3)
WOOD_DARK = ramp('#4a2e1a', dark=0.3)
PANEL = ramp('#553620', dark=0.3)
WATER = ramp('#163a44', dark=0.35, light=1.45, warm=0.02, cool=0.12)
IRON = ramp('#4a4a4e', dark=0.4, light=1.6)
STONE_F = ramp('#a8a294', dark=0.4, light=1.2)


# ---------------------------------------------------------------- textures

def tex_grass(name):
    """A lawn seen from standing height: blades in clumps, dark at the roots and bright at the tips,
    a few yellow-green tufts, the odd daisy."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.4, mat=0)
    dense = smooth_noise(T, T, 4, rng)
    for i in range(900):
        x, y = rng.random() * T, rng.random() * T
        if rng.random() > 0.35 + 0.65 * dense[int(y) % T, int(x) % T]:
            continue
        a = np.radians(rng.uniform(-115, -65))                # mostly upright, leaning a little
        L = rng.uniform(2.5, 5.0)
        tip = 2 if rng.random() < 0.18 else 1
        cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], 1.1, z=0.1 + i * 0.0006, dome=0.5,
                  taper=(1.0, 0.4), mat=tip if rng.random() < 0.6 else 0, tone=rng.normal(0, 0.05))
    rgb = _tile(cv, GRASS, cavity=0.45, shadow=0.4, ambient=0.26, diffuse=0.62)
    for _ in range(4):                                        # daisies
        x, y = int(rng.random() * T), int(rng.random() * T)
        rgb[y % T, x % T] = (0.95, 0.95, 0.9)
        rgb[(y + 1) % T, x % T] = (0.92, 0.82, 0.3)
    return rgb


def tex_hedge(name):
    """A clipped hedge: small leaves packed tight in three depths, the face kept nearly flat by the
    shears, darker hollows where it has grown thin."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.0, mat=2)
    _leaf_layers(cv, rng, [(-0.4, 150, -0.18, (3, 5)), (0.2, 110, -0.06, (3, 5)), (0.7, 70, 0.04, (3, 5.5))],
                 [0, 0, 1, 1], angles=(0, 360), aspect=(0.5, 0.7), bend=0.1)
    thin = smooth_noise(T, T, 3, rng)
    cv.tone -= np.where(thin < 0.3, 0.12, 0.0).astype(np.float32)
    return _tile(cv, HEDGE, cavity=0.5, shadow=0.5)


def tex_dirt(name):
    """Bare earth: soil broken into clods, a scatter of pebbles, darker damp patches and the odd
    root or twig."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.35, cells=6, rng=rng, octaves=3)
    for _ in range(46):                                       # clods
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(1.5, 4), rng.uniform(1.2, 3), z=0.1, dome=0.6,
                   rough=0.4, rng=rng, mat=1, tone=rng.normal(0, 0.06))
    for _ in range(26):                                       # pebbles
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.8, 1.8), rng.uniform(0.7, 1.4), z=0.4, dome=0.9,
                   rough=0.2, rng=rng, mat=2, tone=rng.normal(0, 0.08))
    for _ in range(2):                                        # a root
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, np.pi)
        cv.stroke([(x, y), (x + np.cos(a) * 8, y + np.sin(a) * 8 + 2), (x + np.cos(a) * 15, y + np.sin(a) * 15)],
                  1.2, z=0.3, dome=0.5, mat=3)
    damp = smooth_noise(T, T, 3, rng)
    cv.tone -= (np.clip(damp - 0.55, 0, 1) * 0.5).astype(np.float32)
    return _tile(cv, [SOIL, CLOD, PEBBLE[0], WOOD_DARK], cavity=0.45, shadow=0.4)


def tex_gravel(name):
    """Gravel: rounded pebbles packed together, each lit on top with a shadow under it, in a few
    stone colours."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.6, mat=2)
    for i in range(260):
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(1.4, 3.0), rng.uniform(1.1, 2.4),
                   z=rng.uniform(0, 0.3), dome=1.0, angle=rng.uniform(0, 180), rough=0.15, rng=rng,
                   mat=int(rng.integers(0, 3)), tone=rng.normal(0, 0.06), mode='max')
    return _tile(cv, PEBBLE, cavity=0.5, shadow=0.45)


def tex_wood_panel(name):
    """Wood panelling: stiles and rails framing two raised, bevelled panels per unit, all of one
    wood, so the panels show by the light on their bevels; a groove round each panel, the grain
    running up the stiles and panels and along the rails."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    for x in (0, 32):
        cv.box(x + 5, 6, 22, 52, z=-0.1, top=1.8, bevel=4.0, mat=0, tone=0.03 + rng.normal(0, 0.02))
        cv.stroke([(x + 4.6, 5.6), (x + 27.4, 5.6), (x + 27.4, 58.4), (x + 4.6, 58.4), (x + 4.6, 5.6)], 0.8,
                  dome=0.35, mode='carve')
    for _ in range(46):                                        # grain up the stiles and panels
        x, y = rng.random() * T, rng.uniform(6, 50)
        cv.stroke([(x, y), (x + rng.normal(0, 0.3), y + rng.uniform(6, 16))], 0.55, dome=0.18, mode='carve')
    for y0 in (1, 59):                                         # and along the rails
        for _ in range(5):
            x, y = rng.random() * T, y0 + rng.uniform(0.5, 3.5)
            cv.stroke([(x, y), (x + rng.uniform(8, 18), y + rng.normal(0, 0.2))], 0.55, dome=0.18, mode='carve')
    cv.stroke([(0, 0.5), (T, 0.5)], 0.9, dome=0.35, mode='carve')   # the joint with the course above
    rail = (np.arange(T)[:, None] < 6) | (np.arange(T)[:, None] > 58)   # figure in the wood: streaks with the grain
    streak = np.where(rail, smooth_noise(T, T, 2, rng, cells_y=16), smooth_noise(T, T, 16, rng, cells_y=2))
    cv.tone += (0.3 * (streak - 0.5)).astype(np.float32)
    return _tile(cv, [PANEL], dither=0.25, relief=1.6, cavity=0.4, shadow=0.35, ambient=0.25, diffuse=0.6)


def tex_water(name):
    """Still water: a deep teal in slow swells of lighter and darker, and a broken net of light
    where the ripples gather it - the cells of a Voronoi pattern, brightest along their edges,
    fading in and out."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    swell = smooth_noise(T, T, 3, rng) * 0.7 + smooth_noise(T, T, 7, rng) * 0.3
    cv.tone += (0.32 * (swell - 0.5)).astype(np.float32)
    n = 12                                                     # the caustic net
    sx, sy = rng.random(n) * T, rng.random(n) * T
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    dx = np.abs(xx[..., None] - sx)
    dy = np.abs(yy[..., None] - sy)
    d = np.sort(np.hypot(np.minimum(dx, T - dx), np.minimum(dy, T - dy)), axis=-1)
    edge = d[..., 1] - d[..., 0]
    fade = np.clip(smooth_noise(T, T, 4, rng) * 1.8 - 0.4, 0, 1)
    cv.tone += (0.2 * np.exp(-edge / 1.8) * fade).astype(np.float32)
    return _tile(cv, [WATER], dither=0.4, cavity=0.0, shadow=0.0, ambient=0.12, diffuse=0.45)


# ---------------------------------------------------------------- props

def spr_barrel():
    """A wooden barrel: staves bulging at the middle, three iron hoops round it, the lid showing at
    the top, lit on the left."""
    w, h = 32, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    _lathe(cv, 16, [(3, 11.5), (12, 14), (22, 15), (32, 14), (43, 11.5)], z=0.0, dome=1.3, mat=0)
    for x in (8, 12.5, 16.5, 20.5, 25):                        # the joints between staves
        cv.stroke([(x, 4), (16 + (x - 16) * 1.12, 22), (x, 42)], 0.7, dome=0.3, mode='carve')
    for y, half in ((8, 13.2), (22, 15.1), (36, 13.5)):        # hoops
        _lathe(cv, 16, [(y, half + 0.3), (y + 2.5, half + 0.4)], z=0.2, dome=1.35, mat=1)
    cv.ellipse(16, 3.2, 11, 2.4, z=1.2, dome=0.3, mat=2)       # the lid
    return _prop(cv, [WOOD, IRON, WOOD_DARK], relief=1.0, cavity=0.35, shadow=0.45, ambient=0.3, diffuse=0.65)


def spr_broken_barrel():
    """A barrel burst open: the bottom half still hooped, its front staves splintered off at
    different heights so the dark inside shows through, the back staves standing taller, a loose
    stave leaning on it, another fallen, and a hoop lying on the ground."""
    rng = np.random.default_rng(101)
    w, h = 48, 44
    cx, rim, rx = 21, 17, 13.8
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, top in ((cx - 10, 10), (cx - 5, 4), (cx, 7), (cx + 5, 2), (cx + 10, 9)):   # the back staves
        peak = x + rng.uniform(-1.2, 1.2)
        cv.polygon([(x - 2.6, rim + 3), (x - 2.6, top + 3), (peak, top), (x + 2.6, top + rng.uniform(1, 4)),
                    (x + 2.6, rim + 3)], top=0.25, bevel=1.0, mat=1, tone=rng.normal(0, 0.04))
    cv.ellipse(cx, rim, rx, 4.2, z=0.05, dome=0.0, mat=2)      # the dark inside
    cv.box(cx - rx, rim, 2 * rx, 13, z=0.05, top=0.0, bevel=1, mat=2)
    body = cv.layer()                                          # the front, built on its own and broken
    _lathe(body, cx, [(rim - 1, 14.4), (29, 15.6), (43, 12.6)], z=0.6, dome=1.3, mat=0)
    for x in (cx - 10, cx - 5, cx, cx + 5, cx + 10):           # joints between the staves
        body.stroke([(x, rim), (cx + (x - cx) * 1.08, 30), (cx + (x - cx) * 0.9, 42)], 0.7, dome=0.3, mode='carve')
    _lathe(body, cx, [(31, 15.4), (33.5, 15.5)], z=0.8, dome=1.35, mat=3)   # hoops
    _lathe(body, cx, [(38.5, 14.2), (41, 13.6)], z=0.8, dome=1.35, mat=3)
    cut = np.zeros((h, w), bool)
    for k, a in enumerate(np.arange(cx - 15, cx + 15, 5.0)):   # each front stave broken off at its own height
        drop, peak, spike = rng.uniform(0, 9), rng.uniform(0.2, 0.8), rng.uniform(2, 5)
        if k in (2, 4):
            drop = rng.uniform(0, 2)
        for x in range(int(np.floor(a)), int(np.ceil(a + 5))):
            if not 0 <= x < w:
                continue
            u = (x + 0.5 - cx) / rx
            arc = rim + 4.2 * np.sqrt(max(0.0, 1 - u * u))     # the near half of the opening
            t = (x + 0.5 - a) / 5
            cut[:int(round(max(arc, arc + drop + spike * abs(t - peak) * 2 - spike * 0.5))), x] = True
    cv.paste(body, cut=cut)
    cv.stroke([(3, 42), (8.5, 22)], 3.6, z=1.4, dome=0.9, taper=(1.0, 0.8), mat=0, tone=0.03)        # a stave leaning on it
    cv.stroke([(34, 40.5), (40, 39.0), (47, 39.8)], 3.2, z=1.0, dome=0.8, taper=(0.8, 1.0), mat=0, tone=-0.03)   # one fallen
    a = np.linspace(0, 2 * np.pi, 30)                          # a hoop on the ground
    cv.stroke(list(zip(40 + np.cos(a) * 6, 41.6 + np.sin(a) * 1.8)), 1.2, z=1.6, dome=0.4, mat=3)
    return _prop(cv, [WOOD, WOOD_DARK, ramp('#22160e', dark=0.6, light=1.3), IRON], relief=1.0, cavity=0.4,
                 shadow=0.45)


def spr_crate():
    """A wooden crate: planks behind a frame of battens and a diagonal brace, nails at the corners,
    a stencilled arrow, lit on the left."""
    w, h = 40, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(4):                                         # the planks
        cv.box(2, 2 + k * 9, 36, 8.6, z=0.0, top=0.8, bevel=1.2, mat=0, tone=(k % 2) * 0.04 - 0.02)
    for x0, y0, x1, y1 in ((2, 2, 38, 2), (2, 38, 38, 38), (2, 2, 2, 38), (38, 2, 38, 38)):   # the frame
        cv.stroke([(x0, y0), (x1, y1)], 4.2, z=0.8, dome=0.7, mat=1)
    cv.stroke([(5, 35), (35, 5)], 3.6, z=0.6, dome=0.6, mat=1)      # the brace
    for x, y in ((4, 4), (36, 4), (4, 36), (36, 36)):          # nails
        cv.ellipse(x, y, 0.8, 0.8, z=1.7, dome=0.3, mat=2)
    for k in range(2):                                         # a stencilled arrow, pointing up
        x = 13 + k * 12
        cv.stroke([(x, 30), (x, 21)], 1.2, z=0.85, dome=0.1, mat=3)
        cv.stroke([(x - 2.5, 24), (x, 20.5), (x + 2.5, 24)], 1.2, z=0.86, dome=0.1, mat=3)
    return _prop(cv, [ramp('#8a6440', dark=0.3), WOOD_DARK, IRON, ramp('#2e2a26', dark=0.6, light=1.6)],
                 relief=1.0, cavity=0.35, shadow=0.45, ambient=0.3, diffuse=0.65)


def spr_fountain():
    """A stone fountain: a broad round basin with a moulded rim and water in it, a fluted pedestal
    carrying a bowl, water spilling from the bowl in arcs and falling as drops."""
    rng = np.random.default_rng(103)
    w, h = 80, 72
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    _lathe(cv, cx, [(50, 36), (54, 38), (66, 36), (72, 34)], z=0.0, dome=1.2, mat=0)        # the basin
    _lathe(cv, cx, [(48, 37), (52, 38.5)], z=0.6, dome=1.0, mat=0, tone=0.05)              # its rim
    cv.ellipse(cx, 50.5, 33, 2.2, z=1.6, dome=0.2, mat=1)                                  # the water
    _lathe(cv, cx, [(20, 4), (24, 5), (46, 6), (50, 8)], z=0.8, dome=1.2, mat=0)           # the pedestal
    for x in (cx - 3, cx, cx + 3):
        cv.stroke([(x, 26), (x, 46)], 0.6, dome=0.3, mode='carve')
    _lathe(cv, cx, [(12, 15), (16, 14), (20, 6)], z=1.2, dome=1.2, mat=0)                  # the bowl
    cv.ellipse(cx, 12, 14, 1.6, z=2.5, dome=0.2, mat=1)
    for side in (-1, 1):                                       # water spilling over in arcs
        t = np.linspace(0, 1, 12)
        cv.stroke(list(zip(cx + side * (14 + 10 * t), 13 + 36 * t * t)), 1.2, z=2.6, dome=0.3, mat=2)
    cv.stroke([(cx, 2), (cx, 11)], 1.4, z=2.8, dome=0.3, mat=2)                             # a jet
    for _ in range(12):                                        # drops
        x, y = cx + rng.uniform(-30, 30), rng.uniform(16, 48)
        if abs(x - cx) > 8:
            cv.ellipse(x, y, 0.6, 0.9, z=2.6, dome=0.2, mat=2)
    return _prop(cv, [STONE_F, WATER, ramp('#bfe8f0', dark=0.6, light=1.05)], relief=1.0, cavity=0.4, shadow=0.45)


TEXTURES = {
    'grass': lambda n: (tex_grass(n), None),
    'hedge': lambda n: (tex_hedge(n), None),
    'dirt': lambda n: (tex_dirt(n), None),
    'gravel': lambda n: (tex_gravel(n), None),
    'wood_panel': lambda n: (tex_wood_panel(n), None),
    'water': lambda n: (tex_water(n), None),
}
SPRITES = {'barrel': spr_barrel, 'broken_barrel': spr_broken_barrel, 'crate': spr_crate, 'fountain': spr_fountain}

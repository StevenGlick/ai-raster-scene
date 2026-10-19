"""A base on the Moon, drawn with the pixel-art toolkit (scripts/pixelart.py): grey regolith pocked
with craters, the tracks a rover leaves in it, a greenhouse dome lit from inside, a six-wheeled
rover, a solar array and a habitat module.

As in the other toolkit modules, every shape is stamped into a height field, lit from the upper
left and snapped onto hue-shifted ramps; the regolith tiles.
"""
import numpy as np

from biomes import T, _prop, _rng, _tile
from dream import _lathe
from pixelart import Canvas, ramp, smooth_noise

REGOLITH = ramp('#8a8884', dark=0.3, light=1.35, warm=0.0, cool=0.05)
GLASS_PANE = ramp('#5a7a8a', dark=0.4, light=1.5, cool=0.15)
STRUT = ramp('#c8ccd0', dark=0.45, light=1.12)
PLANT = ramp('#5aa84a', dark=0.4, light=1.3)
GROWLIGHT = ramp('#e8b0ff', dark=0.6, light=1.1)
WHITE_HULL = ramp('#d8d8d4', dark=0.4, light=1.1)
FOIL = ramp('#c8a040', dark=0.35, light=1.35, warm=0.12)
CELL = ramp('#2a3a6a', dark=0.4, light=1.8, cool=0.2)
TYRE = ramp('#5a5a58', dark=0.45, light=1.5)
WINDOW = ramp('#ffd890', dark=0.6, light=1.1)


def tex_regolith(name):
    """The Moon's surface: grey dust, craters of every size - a raised rim lit on the side toward the
    sun, a dark bowl - small rocks thrown out of them, and the dust's own fine grain."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.35, cells=8, rng=rng, octaves=3)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    for k in range(8):
        cx, cy = rng.random() * T, rng.random() * T
        r = float(rng.uniform(1.5, 6.0) if k < 6 else rng.uniform(9, 13))
        dx = (xx - cx + T / 2) % T - T / 2
        dy = (yy - cy + T / 2) % T - T / 2
        d = np.hypot(dx, dy) / r
        bowl = np.where(d < 1, -0.9 * (1 - d * d), 0.0)
        rim = 0.5 * np.exp(-((d - 1.0) / 0.18) ** 2)
        cv.z += ((bowl + rim) * min(1.0, r / 6)).astype(np.float32)
    for _ in range(30):                                          # thrown-out rocks
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.6, 1.4), rng.uniform(0.5, 1.0), z=0.4, dome=0.8,
                   rough=0.3, rng=rng, mat=0, tone=rng.normal(-0.04, 0.05))
    return _tile(cv, [REGOLITH], dither=0.3, relief=1.2, cavity=0.3, shadow=0.5, sun=(-0.7, -0.5, 0.45))


def dec_rover_tracks():
    """Two rover tracks running straight across the dust: chevron treads pressed in, darker than
    the dust round them."""
    w, h = 64, 128
    rgba = np.zeros((h, w, 4), np.float32)
    for x0 in (10, 44):
        for y in range(0, h, 4):
            for k in range(10):
                x = x0 + k
                yy = y + abs(k - 4.5) * 0.6
                yi = int(yy) % h
                rgba[yi, x, :3] = (0.22, 0.22, 0.22)
                rgba[yi, x, 3] = 0.55
        rgba[:, x0:x0 + 10, 3] = np.maximum(rgba[:, x0:x0 + 10, 3], 0.22)
    return rgba, np.zeros((h, w), np.float32)


def spr_dome():
    """A greenhouse dome: a geodesic frame of white struts over glass, the inside lit pink-white by
    grow lights over rows of green, an airlock door at its foot. It glows."""
    w, h = 128, 72
    cx = 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    R = 60
    d = np.hypot((xx - cx) / R, (yy - (h - 2)) / (h - 4))
    shell = (d < 1) & (yy < h - 1)
    cv.z[shell] = (np.sqrt(np.clip(1 - d[shell] ** 2, 0, 1)) * 2.0).astype(np.float32)
    cv.mat[shell] = 0
    cv.id[shell] = 1
    cv.n = 1
    for k in range(5):                                           # rows of plants inside, behind the glass
        y = h - 6 - k * 8
        for x in range(int(cx - R * 0.9), int(cx + R * 0.9), 5):
            if d[min(h - 1, max(0, y)), min(w - 1, max(0, x))] < 0.85:
                cv.ellipse(x + (k % 2) * 2.5, y, 2.6, 2.2, z=0.3, dome=0.8, mat=2)
    for k in range(3):                                           # grow lights
        y = 14 + k * 9
        cv.stroke([(cx - 30 + k * 6, y), (cx + 30 - k * 6, y)], 1.2, z=0.5, dome=0.3, mat=3)
    for a in np.linspace(0.12, np.pi - 0.12, 9):                 # meridian struts
        pts = [(cx + np.cos(a) * R * np.sin(t), (h - 2) - (h - 4) * np.cos(t) * 0 - (h - 4) * np.sin(t) * np.sin(a) * 0
                - (h - 4) * (1 - np.cos(t)) * 0) for t in [0]]
        t = np.linspace(0, np.pi / 2, 12)
        pts = list(zip(cx + np.cos(a) * R * np.cos(t), (h - 2) - (h - 4) * np.sin(t) * 1.0))
        pts = [(cx + (px - cx) , py) for px, py in pts]
        cv.stroke(pts, 1.0, z=2.4, dome=0.4, mat=1)
    for k in range(1, 5):                                        # rings
        f = k / 5
        yk = (h - 2) - (h - 4) * f
        half = R * np.sqrt(max(0.0, 1 - f * f))
        a = np.linspace(-1, 1, 30)
        cv.stroke(list(zip(cx + a * half, yk + 0 * a)), 1.0, z=2.4, dome=0.4, mat=1)
    cv.box(cx - 7, h - 16, 14, 15, z=2.6, top=0.6, bevel=1.2, mat=4)            # the airlock
    cv.box(cx - 4, h - 13, 8, 12, z=3.0, top=0.3, bevel=0.8, mat=5)
    em = (((cv.mat == 2) | (cv.mat == 3)) & (cv.id > 0)) * 0.9 + ((cv.mat == 0) & (cv.id > 0)) * 0.35
    return _prop(cv, [GLASS_PANE, STRUT, PLANT, GROWLIGHT, WHITE_HULL, WINDOW], relief=1.0, cavity=0.3, shadow=0.35,
                 em=em)


def spr_rover():
    """A six-wheeled lunar rover: a white chassis on wire-mesh wheels, an open cab with two seats, a
    dish antenna on a mast, a gold-foiled equipment box at the back."""
    w, h = 96, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (16, 48, 80):                                       # the wheels
        a = np.linspace(0, 2 * np.pi, 30)
        cv.stroke(list(zip(x + np.cos(a) * 8, h - 9 + np.sin(a) * 8)), 3.0, z=1.2, dome=0.7, mat=3)
        for k in range(6):
            b = k * np.pi / 3
            cv.stroke([(x, h - 9), (x + np.cos(b) * 7, h - 9 + np.sin(b) * 7)], 0.7, z=1.0, dome=0.3, mat=3)
        cv.ellipse(x, h - 9, 2.0, 2.0, z=1.6, dome=0.7, mat=0)
    cv.box(4, 22, 88, 10, z=0.6, top=1.0, bevel=1.5, mat=0)                         # the chassis
    for x in (16, 48, 80):                                       # fenders
        cv.stroke([(x - 11, 24), (x - 6, 20), (x + 6, 20), (x + 11, 24)], 1.6, z=1.6, dome=0.5, mat=0)
    cv.box(70, 10, 20, 12, z=0.9, top=1.0, bevel=1.5, mat=1)                         # the equipment box
    for sx in (30, 46):                                          # seats
        cv.box(sx, 12, 10, 10, z=1.0, top=0.6, bevel=1.0, mat=2)
        cv.box(sx, 4, 3, 10, z=1.2, top=0.6, bevel=0.8, mat=2)
    cv.stroke([(60, 22), (60, 2)], 1.0, z=1.4, dome=0.4, mat=0)                    # the mast
    cv.ellipse(60, 4, 7, 2.4, z=1.8, dome=0.6, angle=-25, mat=0, tone=0.05)        # the dish
    cv.stroke([(20, 22), (26, 10), (30, 10)], 1.0, z=1.4, dome=0.4, mat=3)          # the hand controller
    return _prop(cv, [WHITE_HULL, FOIL, ramp('#4a5a7a', dark=0.4, light=1.4), TYRE], relief=1.0, cavity=0.35,
                 shadow=0.45)


def spr_solar_array():
    """A solar array on a mast: a wide panel of dark-blue cells in a silver frame, tilted toward the
    sun, a pivot and a cable running down."""
    w, h = 96, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(48, h), (48, 26)], 2.6, z=0.0, dome=0.7, mat=1)
    cv.polygon([(4, 6), (92, 2), (90, 30), (6, 34)], z=0.8, top=0.5, bevel=1.0, mat=1)
    for i in range(12):                                          # the cells
        for j in range(3):
            x0 = 7 + i * 7.0
            y0 = 6 - i * 0.33 + j * 8.6 + 0.6
            cv.polygon([(x0, y0), (x0 + 6, y0 - 0.3), (x0 + 6, y0 + 7.4), (x0, y0 + 7.7)], z=1.0, top=0.3, bevel=0.5,
                       mat=0, tone=(i + j) % 2 * 0.04)
    cv.ellipse(48, 26, 3, 3, z=1.4, dome=0.7, mat=1)
    cv.stroke([(48, 30), (56, 44), (60, h)], 0.8, z=0.4, dome=0.3, mat=2)
    return _prop(cv, [CELL, STRUT, ramp('#2a2a2c', dark=0.5, light=1.6)], relief=1.0, cavity=0.3, shadow=0.4)


def spr_hab_module():
    """A habitat module lying on its side on low legs: a white cylinder with ribs, a round hatch at the
    end and a row of lit portholes, a radiator fin on its back."""
    w, h = 128, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (24, 104):                                          # legs
        cv.stroke([(x, 40), (x - 6, h)], 2.0, z=0.0, dome=0.6, mat=0)
        cv.stroke([(x, 40), (x + 6, h)], 2.0, z=0.0, dome=0.6, mat=0)
    cv.box(8, 14, 112, 30, z=0.4, top=2.4, bevel=13, mat=0)                       # the cylinder
    for x in range(20, 116, 16):
        cv.stroke([(x, 15), (x, 43)], 0.9, dome=0.4, mode='carve')                   # its ribs
    for x in range(28, 104, 16):
        cv.ellipse(x, 26, 3.0, 3.0, z=2.8, dome=0.3, mat=1)                         # portholes
    cv.ellipse(10, 29, 5.5, 12, z=2.6, dome=0.6, mat=0, tone=0.05)                  # the end hatch
    cv.ellipse(10, 29, 3.5, 7, z=3.0, dome=0.3, mat=2)
    cv.polygon([(40, 14), (88, 14), (84, 4), (44, 4)], z=0.2, top=0.4, bevel=0.8, mat=3)   # a radiator fin
    for x in range(46, 84, 4):
        cv.stroke([(x, 5), (x, 13)], 0.5, dome=0.2, mode='carve')
    em = ((cv.mat == 1) & (cv.id > 0)) * 1.0
    return _prop(cv, [WHITE_HULL, WINDOW, ramp('#8a9098', dark=0.4, light=1.3), STRUT], relief=1.0, cavity=0.35,
                 shadow=0.45, em=em)


TEXTURES = {'regolith': lambda n: (tex_regolith(n), None)}
TEXTURE_NOISE = {'regolith': 1.6}
DECALS = {'rover_tracks': dec_rover_tracks}
SPRITES = {'dome': spr_dome, 'rover': spr_rover, 'solar_array': spr_solar_array, 'hab_module': spr_hab_module}
SPRITE_HEIGHT = {'dome': 2.6, 'rover': 0.8, 'solar_array': 1.4, 'hab_module': 1.3}
PROP_DEFAULTS = {'dome': {'aura': {'color': [0.9, 0.7, 1.0], 'strength': 0.3, 'radius': 0.25}}}

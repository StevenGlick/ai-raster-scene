"""Sci-fi hardware drawn with the pixel-art toolkit (scripts/pixelart.py): a hangar's deck plates,
cable conduits, walls of screens, landing-pad markings, a shuttle, cargo containers, a power
loader, a warning beacon, a reactor core, a robot arm and cables hanging from the ceiling - for
hangars, labs and engine rooms.

As in biomes.py and forest.py, every shape is stamped into a height field, lit from the upper
left and snapped onto ramps; lights, screens and engines also write an emissive mask, so they
glow in the dark.
"""
import numpy as np

from biomes import T, _prop, _rng, _tile
from pixelart import Canvas, ramp, smooth_noise

STEEL = ramp('#8e949c', dark=0.3, light=1.25, warm=0.05, cool=0.1)
GUNMETAL = ramp('#4e5660', dark=0.35)
DECK = ramp('#5c6168', dark=0.35, light=1.2)
PAINT_YELLOW = ramp('#d8a832', dark=0.4)
PAINT_ORANGE = ramp('#c8642a', dark=0.35)
PAINT_WHITE = ramp('#d6dad6', dark=0.45, light=1.08)
RUBBER = ramp('#2c2e32', dark=0.6, light=1.7)
GLASS = ramp('#4ab4d0', dark=0.35, light=1.35)
GLOW_CYAN = ramp('#58e0f0', dark=0.5, light=1.3)
GLOW_AMBER = ramp('#ffb040', dark=0.5, light=1.2)
GLOW_RED = ramp('#ff4a3a', dark=0.5, light=1.2)
CABLES = [ramp('#2a2c30', dark=0.6, light=1.8), ramp('#a03a2a'), ramp('#2a5aa0'), ramp('#c8a030')]


# ---------------------------------------------------------------- textures

def tex_hangar_floor(name):
    """A hangar deck: heavy plates bolted down, four to a unit, worn bright where boots and loaders
    run, a tie-down ring set into each crossing of the seams, scuffs and oil stains."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.6, mat=1)
    for j in range(2):
        for i in range(2):
            x, y = i * 32 + 0.5, j * 32 + 0.5
            cv.box(x, y, 31, 31, z=0.0, top=1.0, bevel=2.0, mat=0, tone=rng.normal(0, 0.04))
            for bx, by in ((4, 4), (27, 4), (4, 27), (27, 27)):          # bolts in the corners
                cv.ellipse(x + bx, y + by, 1.3, 1.3, z=1.0, dome=0.5, mat=1)
            for _ in range(5):                                          # diamond tread
                tx, ty = x + rng.uniform(8, 24), y + rng.uniform(8, 24)
                cv.stroke([(tx - 1.5, ty + 1.5), (tx + 1.5, ty - 1.5)], 1.0, dome=0.3, mode='add')
    a = np.linspace(0, 2 * np.pi, 24)
    cv.stroke(list(zip(T / 2 + np.cos(a) * 3.2, T / 2 + np.sin(a) * 3.2)), 1.2, z=0.8, dome=0.6, mat=2)   # tie-down ring
    cv.noise(0.08, cells=10, rng=rng)
    wear = smooth_noise(T, T, 3, rng)
    cv.tone += (wear - 0.5) * 0.18                                      # paths of wear
    yy, xx = np.mgrid[0:T, 0:T] + 0.5
    for _ in range(2):                                                  # oil stains
        ox, oy, r = rng.random() * T, rng.random() * T, rng.uniform(4, 7)
        dx, dy = np.abs(xx - ox), np.abs(yy - oy)
        d = np.hypot(np.minimum(dx, T - dx), np.minimum(dy, T - dy) * 1.3)
        cv.tone -= 0.14 * np.clip(1 - d / r, 0, 1) ** 0.5
    return _tile(cv, [DECK, GUNMETAL, STEEL], cavity=0.5, shadow=0.4)


def tex_conduit(name):
    """A wall of cable runs: bundles of black, red, blue and yellow cable and two pipes going up
    the wall, held in steel clamps, a junction box with lit status lights."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.0, mat=1)
    x = 2.0
    while x < T - 3:
        if rng.random() < 0.25:                                         # a pipe
            wd = rng.uniform(7, 9)
            cv.stroke([(x + wd / 2, -4), (x + wd / 2, T + 4)], wd, z=0.0, dome=1.2, mat=0)
        else:                                                           # a bundle of cables
            wd = rng.uniform(2.6, 4.2)
            cv.stroke([(x + wd / 2, -4), (x + wd / 2, T + 4)], wd, z=0.2, dome=0.9,
                      mat=2 + int(rng.integers(0, 4)), tone=rng.normal(0, 0.05))
        x += wd + rng.uniform(0.3, 1.2)
    for y in (12, 44):                                                  # clamps across them
        cv.box(0, y, T, 3.5, z=1.2, top=0.6, bevel=1.0, mat=0)
        for bx in range(4, T, 16):
            cv.ellipse(bx, y + 1.75, 1.0, 1.0, z=1.8, dome=0.3, mat=1)
    cv.box(36, 22, 18, 14, z=1.4, top=0.8, bevel=1.5, mat=0, tone=-0.04)   # a junction box
    for k, m in enumerate((6, 7, 6)):
        cv.ellipse(40 + k * 5, 26, 1.2, 1.2, z=2.3, dome=0.3, mat=m)
    cv.stroke([(39, 31), (51, 31)], 1.0, dome=0.3, mode='carve')
    rgb = cv.paint([STEEL, GUNMETAL] + CABLES + [GLOW_AMBER, ramp('#5aff7a', dark=0.5)], cv.light(cavity=0.5, shadow=0.5),
                   dither=0.3)
    em = np.isin(cv.mat, (6, 7)).astype(np.float32) * 0.9
    return rgb, em


def tex_screen_wall(name):
    """A wall of monitors, four to a unit in heavy bezels, each showing something different - a
    trace, columns of readouts, a radar sweep, a wireframe - in cyan, green or amber."""
    rng = _rng(name)
    rgb = np.zeros((T, T, 3), np.float32)
    em = np.zeros((T, T), np.float32)
    cv = Canvas(T, ground=0.0, mat=0)
    for j in range(2):
        for i in range(2):
            cv.box(i * 32 + 1, j * 32 + 1, 30, 30, z=0.0, top=1.0, bevel=2.5, mat=0, tone=rng.normal(0, 0.03))
    base = cv.paint([GUNMETAL], cv.light(cavity=0.4, shadow=0.4), dither=0.25)
    rgb[:] = base
    tints = [np.array(c, np.float32) for c in ((0.35, 0.95, 1.0), (0.45, 1.0, 0.5), (1.0, 0.72, 0.3))]
    yy, xx = np.mgrid[0:24, 0:24]
    for j in range(2):
        for i in range(2):
            x0, y0 = i * 32 + 4, j * 32 + 4
            c = tints[int(rng.integers(len(tints)))]
            scr = np.full((24, 24), 0.12, np.float32)
            kind = (i + 2 * j + int(rng.integers(4))) % 4
            if kind == 0:                                               # a trace
                ys = (12 + 7 * np.sin(np.arange(24) / 3.0 + rng.uniform(0, 6)) * np.cos(np.arange(24) / 7.0)).astype(int)
                scr[np.clip(ys, 1, 22), np.arange(24)] = 1.0
                scr[::6, :] = np.maximum(scr[::6, :], 0.3)
            elif kind == 1:                                             # readouts
                for r in range(3, 22, 3):
                    n = int(rng.integers(6, 20))
                    scr[r, 2:2 + n] = rng.choice([0.55, 0.9], n)
            elif kind == 2:                                             # radar
                d = np.hypot(xx - 12, yy - 12)
                scr[(np.abs(d - 10) < 0.6) | (np.abs(d - 6) < 0.5)] = 0.6
                ang = np.arctan2(yy - 12, xx - 12)
                scr[(d < 10) & (np.abs(((ang - 0.6) + np.pi) % (2 * np.pi) - np.pi) < 0.35)] = 0.85
                scr[int(rng.integers(5, 19)), int(rng.integers(5, 19))] = 1.0
            else:                                                       # a wireframe
                for k in range(0, 24, 4):
                    scr[k, :] = np.maximum(scr[k, :], 0.45)
                    scr[:, k] = np.maximum(scr[:, k], 0.45)
                scr[6:18, 6] = scr[6:18, 17] = scr[6, 6:18] = scr[17, 6:18] = 1.0
            scr[1::2, :] *= 0.8                                         # scanlines
            rgb[y0:y0 + 24, x0:x0 + 24] = scr[..., None] * c[None, None, :] + 0.03
            em[y0:y0 + 24, x0:x0 + 24] = 0.6 + 0.4 * scr
    return np.clip(rgb, 0, 1), em


# ---------------------------------------------------------------- decals

def dec_pad_marking():
    """A landing pad painted on a deck: a broad ring with an H in it and hazard marks round it."""
    s = 128
    yy, xx = np.mgrid[0:s, 0:s] + 0.5
    d = np.hypot(xx - s / 2, yy - s / 2)
    a = ((d > 50) & (d < 58)).astype(np.float32)
    ang = (np.degrees(np.arctan2(yy - s / 2, xx - s / 2)) + 360) % 360
    a = np.maximum(a, ((d > 60) & (d < 63) & ((ang // 15) % 2 == 0)).astype(np.float32))
    h = ((np.abs(xx - s / 2 + 14) < 4) | (np.abs(xx - s / 2 - 14) < 4)) & (np.abs(yy - s / 2) < 24)
    h |= (np.abs(yy - s / 2) < 3.5) & (np.abs(xx - s / 2) < 15)
    a = np.maximum(a, h.astype(np.float32))
    wear = smooth_noise(s, s, 8, np.random.default_rng(5), wrap=False)
    a *= np.clip(0.55 + wear, 0, 1) > 0.6
    rgba = np.zeros((s, s, 4), np.float32)
    rgba[..., :3] = (0.86, 0.68, 0.22)
    rgba[..., 3] = a * 0.85
    return rgba, np.zeros((s, s), np.float32)


def dec_hazard_stripe():
    """A band of yellow and black diagonal stripes, worn, for the edge of a pad or a loading bay."""
    w, h = 128, 24
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    band = ((xx + yy) // 12) % 2 == 0
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = np.where(band[..., None], (0.86, 0.68, 0.18), (0.08, 0.08, 0.09))
    wear = smooth_noise(w, h, 10, np.random.default_rng(6), wrap=False, cells_y=2)
    rgba[..., 3] = np.where(wear > 0.28, 0.9, 0.0)
    return rgba, np.zeros((h, w), np.float32)


# ---------------------------------------------------------------- props

def spr_shuttle():
    """A short-hop shuttle parked on its pad, nose on: a broad wedge of a hull in white and orange,
    the cockpit glass lit from inside, two engine pods glowing, landing legs on pads."""
    rng = np.random.default_rng(71)
    w, h = 176, 104
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    for side in (-1, 1):                                                # landing legs
        cv.stroke([(cx + side * 34, 66), (cx + side * 46, 92), (cx + side * 48, h - 6)], 5, z=0.0, dome=0.8,
                  taper=(1.0, 0.8), mat=1)
        cv.box(cx + side * 48 - 9, h - 7, 18, 6, z=0.2, top=0.6, bevel=1.2, mat=1)
        cv.stroke([(cx + side * 30, 70), (cx + side * 44, 88)], 2.5, z=0.3, dome=0.6, mat=3)   # a strut
    cv.stroke([(cx, 70), (cx, h - 8)], 5, z=0.0, dome=0.8, mat=1)
    cv.box(cx - 8, h - 9, 16, 6, z=0.2, top=0.6, bevel=1.2, mat=1)
    for side in (-1, 1):                                                # engine pods on stub wings
        cv.polygon([(cx + side * 30, 44), (cx + side * 74, 50), (cx + side * 74, 60), (cx + side * 30, 64)],
                   z=0.6, top=1.0, bevel=2.5, mat=0)
        cv.ellipse(cx + side * 70, 58, 14, 13, z=0.8, dome=1.6, mat=2)
        cv.ellipse(cx + side * 70, 58, 7.5, 7, z=2.2, dome=0.4, mat=5)                      # the glow
        cv.ellipse(cx + side * 70, 58, 9.5, 9, dome=0.4, mode='carve')
    cv.polygon([(cx - 36, 70), (cx + 36, 70), (cx + 42, 46), (cx + 26, 22), (cx - 26, 22), (cx - 42, 46)],
               z=1.0, top=1.6, bevel=7, mat=0)                         # the hull
    cv.polygon([(cx - 36, 70), (cx + 36, 70), (cx + 39, 58), (cx - 39, 58)], z=2.2, top=0.4, bevel=2, mat=3)  # orange band
    cv.polygon([(cx - 20, 44), (cx + 20, 44), (cx + 15, 28), (cx - 15, 28)], z=2.6, top=0.5, bevel=2, mat=4)   # cockpit
    cv.stroke([(cx, 28), (cx, 44)], 1.6, z=3.1, dome=0.3, mat=1)
    for y in (50, 63):                                                  # panel lines
        cv.stroke([(cx - 38, y), (cx + 38, y)], 0.8, dome=0.3, mode='carve')
    for x in (-24, 24):
        cv.stroke([(cx + x, 46), (cx + x * 1.1, 58)], 0.8, dome=0.3, mode='carve')
    for x in (-30, -26, -22, 22, 26, 30):                               # vents in the orange band
        cv.stroke([(cx + x, 62), (cx + x, 67)], 1.2, dome=0.4, mode='carve')
    hull = (cv.mat == 0) & (cv.id > 0)                                  # the underside in its own shadow
    cv.tone += np.where(hull, -0.12 * np.clip((np.arange(h)[:, None] - 40) / 30.0, 0, 1), 0).astype(np.float32)
    for side in (-1, 1):
        cv.ellipse(cx + side * 38, 50, 1.8, 1.8, z=3.0, dome=0.3, mat=6 if side < 0 else 7)  # nav lights
    em = (np.isin(cv.mat, (5,)) * 1.0 + np.isin(cv.mat, (4,)) * 0.45 + np.isin(cv.mat, (6, 7)) * 1.0) * (cv.id > 0)
    return _prop(cv, [PAINT_WHITE, GUNMETAL, STEEL, PAINT_ORANGE, GLASS, GLOW_CYAN, GLOW_RED,
                      ramp('#5aff7a', dark=0.5)], em=em, relief=1.0, cavity=0.45, shadow=0.5)


def spr_cargo_container():
    """A shipping container side on: corrugated steel in faded orange, corner castings, a door
    seam at one end, a stencilled band and rust working out of the ribs."""
    rng = np.random.default_rng(73)
    w, h = 120, 52
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(2, 4, w - 4, h - 6, z=0.0, top=1.2, bevel=2.0, mat=0)
    for x in range(8, w - 8, 5):                                        # the corrugation
        cv.stroke([(x, 8), (x, h - 6)], 2.2, dome=0.6, mode='add')
    for x0, y0 in ((2, 4), (w - 10, 4), (2, h - 10), (w - 10, h - 10)):  # corner castings
        cv.box(x0, y0, 8, 8, z=1.4, top=0.6, bevel=1.2, mat=1)
    cv.stroke([(w - 26, 8), (w - 26, h - 6)], 1.0, dome=0.4, mode='carve')
    for x in (w - 22, w - 16):
        cv.stroke([(x, 9), (x, h - 7)], 1.5, z=1.6, dome=0.5, mat=1)   # door rods
    cv.box(14, 14, 56, 7, z=1.4, top=0.2, bevel=0.6, mat=2)            # the stencilled band
    rust = (smooth_noise(w, h, 26, rng, wrap=False, cells_y=2) > 0.7) & (cv.mat == 0) & (cv.id > 0)   # streaks down the ribs
    cv.mat[rust] = 3
    return _prop(cv, [PAINT_ORANGE, GUNMETAL, PAINT_WHITE, ramp('#7a3a1e', dark=0.4)], relief=1.0, cavity=0.5,
                 shadow=0.5)


def spr_power_loader():
    """An industrial power loader: a roll cage round the driver's seat, two hydraulic arms ending in
    heavy forks, short legs on broad feet, hazard yellow and black, a work light lit."""
    rng = np.random.default_rng(75)
    w, h = 104, 112
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    for side in (-1, 1):                                                # legs and feet
        cv.stroke([(cx + side * 12, 70), (cx + side * 16, 88), (cx + side * 14, h - 10)], 7, z=0.2, dome=1.0,
                  mat=1)
        cv.box(cx + side * 14 - 11, h - 11, 22, 10, z=0.3, top=1.0, bevel=2.0, mat=0)
        cv.stroke([(cx + side * 9, 74), (cx + side * 13, 98)], 2.6, z=0.8, dome=0.6, mat=2)  # a piston
    cv.box(cx - 22, 56, 44, 18, z=0.6, top=1.4, bevel=3, mat=0)        # the hip block
    for side in (-1, 1):                                                # arms and forks
        sh = (cx + side * 22, 34)
        el = (cx + side * 40, 52)
        wr = (cx + side * 38, 72)
        cv.stroke([sh, el], 8, z=0.8, dome=1.0, mat=0)
        cv.stroke([el, wr], 7, z=1.0, dome=1.0, mat=1)
        cv.stroke([(sh[0], sh[1] + 4), (el[0] - side * 2, el[1] + 2)], 2.4, z=1.4, dome=0.5, mat=2)
        for k in (-1, 1):
            cv.stroke([wr, (wr[0] + side * 4 + k * 4, wr[1] + 16)], 3.2, z=1.2, dome=0.8, taper=(1, 0.6), mat=1)
    for x0, y0, x1, y1 in ((cx - 18, 18, cx - 18, 58), (cx + 18, 18, cx + 18, 58), (cx - 18, 18, cx + 18, 18),
                           (cx - 18, 18, cx - 10, 10), (cx + 18, 18, cx + 10, 10), (cx - 10, 10, cx + 10, 10)):
        cv.stroke([(x0, y0), (x1, y1)], 2.6, z=1.6, dome=0.7, mat=1)   # the roll cage
    cv.box(cx - 12, 36, 24, 20, z=0.9, top=0.8, bevel=2, mat=3)        # the seat
    cv.ellipse(cx, 12, 3, 2.2, z=2.4, dome=0.4, mat=4)                 # the work light
    stripes = (cv.mat == 0) & (((np.arange(w)[None, :] + np.arange(h)[:, None]) // 5) % 2 == 0)
    cv.mat[stripes & (np.arange(h)[:, None] > 56) & (np.arange(h)[:, None] < 74)] = 5
    em = (cv.mat == 4) * (cv.id > 0) * 1.0
    return _prop(cv, [PAINT_YELLOW, GUNMETAL, STEEL, RUBBER, GLOW_AMBER, RUBBER], em=em, relief=1.0, cavity=0.5,
                 shadow=0.5)


def spr_beacon():
    """A warning beacon: an amber dome on a squat base, lit, inside a little wire cage."""
    w, h = 24, 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(3, h - 8, 18, 8, z=0.0, top=1.0, bevel=2, mat=0)
    cv.ellipse(12, h - 9, 7.5, 12, z=0.4, dome=1.2, mat=1)
    for x in (6, 12, 18):
        cv.stroke([(x, h - 8), (12 + (x - 12) * 0.4, 2)], 1.0, z=1.8, dome=0.3, mat=0)
    cv.ellipse(10, h - 14, 2, 3, z=1.7, dome=0.3, mat=2)               # the hot spot
    em = np.isin(cv.mat, (1, 2)) * (cv.id > 0) * 1.0
    return _prop(cv, [GUNMETAL, GLOW_AMBER, ramp('#fff0c0', dark=0.6, light=1.05)], em=em, relief=1.0, cavity=0.3,
                 shadow=0.3)


def spr_reactor_core():
    """A reactor core: a tall column of light behind armoured glass, held in heavy steel collars,
    coolant pipes running into its foot."""
    w, h = 72, 136
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(cx, 16), (cx, h - 18)], 34, z=0.4, dome=1.0, mat=1)    # the glass column
    cv.stroke([(cx - 2, 18), (cx - 2, h - 20)], 10, z=1.3, dome=0.3, mat=2)   # the bright heart
    for y in (8, 44, 84, h - 18):                                       # collars
        cv.box(cx - 22, y, 44, 10, z=1.6, top=1.0, bevel=2.5, mat=0)
        for bx in (-16, -6, 4, 14):
            cv.ellipse(cx + bx + 1, y + 5, 1.3, 1.3, z=2.6, dome=0.3, mat=3)
    for side in (-1, 1):                                                # coolant pipes
        cv.stroke([(cx + side * 34, h), (cx + side * 32, h - 12), (cx + side * 20, h - 14)], 6, z=1.2, dome=1.0,
                  mat=3)
    em = (cv.mat == 1) * (cv.id > 0) * 0.75 + (cv.mat == 2) * (cv.id > 0) * 1.0
    return _prop(cv, [STEEL, GLOW_CYAN, ramp('#e0ffff', dark=0.6, light=1.02), GUNMETAL], em=em, relief=1.0,
                 cavity=0.4, shadow=0.45)


def spr_robot_arm():
    """An industrial robot arm on a turntable base: three segments in factory orange with black
    joints, a welding head at the end with a spark of light."""
    w, h = 104, 104
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(30, h - 16, 40, 16, z=0.0, top=1.2, bevel=3, mat=1)        # base
    cv.ellipse(50, h - 18, 14, 6, z=0.8, dome=0.6, mat=1)
    joints = [(50, h - 24), (40, 46), (74, 22), (88, 40)]
    for (x0, y0), (x1, y1), wd in zip(joints, joints[1:], (13, 10, 7)):
        cv.stroke([(x0, y0), (x1, y1)], wd, z=0.6, dome=1.2, taper=(1.0, 0.85), mat=0)
    for (x, y), r in zip(joints[:3], (9, 7.5, 6)):
        cv.ellipse(x, y, r, r, z=1.6, dome=0.8, mat=1)
        cv.ellipse(x, y, r * 0.35, r * 0.35, z=2.5, dome=0.3, mat=2)
    cv.stroke([(88, 40), (90, 52)], 3.0, z=1.6, dome=0.6, mat=1)       # the welding head
    cv.ellipse(90, 54, 2.6, 2.6, z=2.4, dome=0.4, mat=3)
    em = (cv.mat == 3) * (cv.id > 0) * 1.0
    return _prop(cv, [PAINT_ORANGE, GUNMETAL, STEEL, ramp('#d8f0ff', dark=0.6, light=1.05)], em=em, relief=1.0,
                 cavity=0.45, shadow=0.5)


def spr_cables_hang():
    """Cables hanging from the ceiling in slack loops, a few ends dangling: set `z` near the
    ceiling."""
    rng = np.random.default_rng(79)
    w, h = 64, 96
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(6):
        x0, x1 = rng.uniform(4, 60), rng.uniform(4, 60)
        sag = rng.uniform(30, 80)
        t = np.linspace(0, 1, 16)
        pts = list(zip(x0 + (x1 - x0) * t, 2 + sag * 4 * t * (1 - t)))
        cv.stroke(pts, rng.uniform(1.6, 2.6), z=0.2 + k * 0.1, dome=0.8, mat=int(rng.integers(0, 4)))
    for _ in range(3):                                                  # dangling ends
        x = rng.uniform(8, 56)
        cv.stroke([(x, 0), (x + rng.normal(0, 2), rng.uniform(50, 92))], 1.8, z=0.9, dome=0.8,
                  mat=int(rng.integers(0, 4)))
    return _prop(cv, CABLES, relief=1.0, cavity=0.3, shadow=0.4)


TEXTURES = {
    'hangar_floor': lambda n: (tex_hangar_floor(n), None),
    'conduit': tex_conduit,
    'screen_wall': tex_screen_wall,
}
TEXTURE_NOISE = {'hangar_floor': 1.2, 'conduit': 0.6, 'screen_wall': 0.3}
SPRITES = {'shuttle': spr_shuttle, 'cargo_container': spr_cargo_container, 'power_loader': spr_power_loader,
           'beacon': spr_beacon, 'reactor_core': spr_reactor_core, 'robot_arm': spr_robot_arm,
           'cables_hang': spr_cables_hang}
SPRITE_HEIGHT = {'shuttle': 2.2, 'cargo_container': 1.2, 'power_loader': 2.0, 'beacon': 0.3, 'reactor_core': 2.8,
                 'robot_arm': 1.8, 'cables_hang': 1.4}
PROP_DEFAULTS = {
    'beacon': {'aura': {'color': [1.0, 0.62, 0.2], 'strength': 0.6, 'radius': 0.3}},
    'reactor_core': {'aura': {'color': [0.35, 0.9, 1.0], 'strength': 0.45, 'radius': 0.25}},
}
NO_CONTACT_SHADOW = {'cables_hang'}
DECALS = {'pad_marking': dec_pad_marking, 'hazard_stripe': dec_hazard_stripe}

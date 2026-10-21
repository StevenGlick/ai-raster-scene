"""The public aquarium, drawn with the pixel-art toolkit (scripts/pixelart.py): the animals of the
big ocean tank - a whale shark, a manta ray, a blacktip reef shark, a green turtle - the small
bright fish of a reef (clownfish, an emperor angelfish, a blue tang, a shoal of anthias), the
reef itself (brain coral, staghorn, a sea fan, a bubble-tip anemone, tube sponges and a rock
grown over with all of them), jellyfish for a jelly tank, a lit plaque for the visitors, and the
textures of the tanks: rockwork, open water for the back of a big tank, the view up through a
tunnel's roof, and a jelly tank's glowing blue backdrop.

The fish face right (`flip` turns them round) and are lit from above, as fish are in water: dark
backs, pale bellies. Float them with `z`; they cast no shadows of their own.
"""
import numpy as np

from biomes import T, _prop, _rng, _tile
from pixelart import Canvas, dither, outline_sprite, ramp, smooth_noise

TOP = (-0.25, -0.9, 0.6)              # light from above, a little from the left

WHALE = ramp('#3a5466', dark=0.3, light=1.45, cool=0.2)
SPOT = ramp('#c4d2d4', dark=0.55, light=1.1)
BELLY = ramp('#d6dad4', dark=0.45, light=1.1)
SHARK = ramp('#6c6c64', dark=0.3, light=1.45, cool=0.12)
INK = ramp('#1e1e24', dark=0.6, light=1.9)
MANTA = ramp('#2c3036', dark=0.45, light=1.7)
MANTA_BELLY = ramp('#d2d0c8', dark=0.42, light=1.12)
SHELL = ramp('#6e5428', dark=0.3, light=1.5, warm=0.2)
SCUTE = ramp('#a07a36', dark=0.32, light=1.4, warm=0.16)
SKIN = ramp('#6a7258', dark=0.3, light=1.4)
SKIN_PALE = ramp('#b4b496', dark=0.45, light=1.15)
CLOWN = ramp('#ec6a18', dark=0.35, light=1.25)
WHITE = ramp('#f2eee6', dark=0.6, light=1.05)
TANG = ramp('#2a58d0', dark=0.3, light=1.4)
YELLOW = ramp('#f2c626', dark=0.42, light=1.15)
EMPEROR = ramp('#2a46b0', dark=0.3, light=1.4)
ANTHIAS = ramp('#f0784c', dark=0.38, light=1.25)
PURPLE = ramp('#8a52c8', dark=0.35, light=1.3)
BRAIN = ramp('#b49a56', dark=0.32, light=1.3, warm=0.1)
BRAIN_VALLEY = ramp('#5e6a3a', dark=0.35, light=1.3)
STAG = ramp('#b89a68', dark=0.32, light=1.3, warm=0.12)
STAG_TIP = ramp('#d8c8e8', dark=0.5, light=1.08)
FAN = ramp('#9a3a7c', dark=0.32, light=1.4)
ANEMONE = ramp('#e09878', dark=0.4, light=1.2, warm=0.1)
ANEMONE_TIP = ramp('#e0507a', dark=0.4, light=1.25)
ANEMONE_FOOT = ramp('#a03a4a', dark=0.35, light=1.3)
SPONGE = ramp('#8a4a9e', dark=0.3, light=1.35)
SPONGE_IN = ramp('#3a2244', dark=0.5, light=1.4)
LIVE_ROCK = ramp('#7e6e5c', dark=0.3, light=1.35, warm=0.1)
CORALLINE = ramp('#b06a86', dark=0.35, light=1.3)
ALGAE = ramp('#5a7444', dark=0.35, light=1.35)
NETTLE = ramp('#e8a03c', dark=0.38, light=1.2, warm=0.1)
NETTLE_DARK = ramp('#8a3a24', dark=0.4, light=1.5)
FRILL = ramp('#f0dcc0', dark=0.55, light=1.05)
STEEL = ramp('#3a3e44', dark=0.45, light=1.6)
PANEL = ramp('#1e5a8a', dark=0.4, light=1.6, cool=0.1)


def _side(cv, prof, mat=0, z=0.0, dome=1.4, tone=0.0, shade=0.16):
    """A body seen side-on - a fish, a shark: `prof` is (column, top, bottom) triples along its
    length; every column is filled from top to bottom and domed like a cylinder, as one shape,
    `shade` lighter along its back and darker under its belly so it reads as round.
    Returns the column range and the top and bottom of every column, for laying on markings."""
    x0, x1 = int(prof[0][0]), int(np.ceil(prof[-1][0]))
    xs = np.arange(x0, x1)
    px = [p[0] for p in prof]
    top = np.interp(xs + 0.5, px, [p[1] for p in prof])
    bot = np.interp(xs + 0.5, px, [p[2] for p in prof])
    ys = np.arange(int(np.floor(top.min())) - 1, int(np.ceil(bot.max())) + 2)
    mid, half = (top + bot) / 2, np.maximum((bot - top) / 2, 1e-3)
    V = (ys[:, None] + 0.5 - mid[None, :]) / half[None, :]
    mask = (np.abs(V) < 1) & (half[None, :] > 0.4)
    hgt = z + dome * np.sqrt(np.clip(1 - V * V, 0, 1)) * np.minimum(1.0, half[None, :] / 6.0) ** 0.5
    cv.put(ys, xs, mask, hgt, mat=mat, tone=tone - shade * np.clip(V, -1, 1) - shade * 0.5 * V * V)
    return xs, top, bot


def _band(cv, xs, top, bot, lo, hi, ids, mat):
    """Repaint the part of a body between fractions lo and hi of its depth (0 its back, 1 its
    belly) with another material: a pale belly, a dark back."""
    yy = np.arange(cv.h)[:, None] + 0.5
    full = np.zeros((cv.h, cv.w), bool)
    f = (yy - top[None, :]) / np.maximum(bot - top, 1e-3)[None, :]
    sel = (f >= lo) & (f <= hi)
    c0 = max(0, xs[0])
    c1 = min(cv.w, xs[-1] + 1)
    full[:, c0:c1] = sel[:, c0 - xs[0]:c1 - xs[0]]
    m = full & np.isin(cv.id, ids)
    cv.mat[m] = mat
    return m


def _dots(cv, rng, where, spacing, radius, mat, jitter=0.35, tone=0.0):
    """A staggered grid of round spots over the pixels in `where`, in another material."""
    yy, xx = np.mgrid[0:cv.h, 0:cv.w].astype(np.float32) + 0.5
    spots = np.zeros((cv.h, cv.w), bool)
    sx, sy = spacing
    for j, y in enumerate(np.arange(0, cv.h + sy, sy)):
        for x in np.arange((j % 2) * sx / 2, cv.w + sx, sx):
            cx, cy = x + rng.normal(0, jitter * sx), y + rng.normal(0, jitter * sy)
            r = radius * rng.uniform(0.7, 1.15)
            spots |= (xx - cx) ** 2 + (yy - cy) ** 2 < r * r
    m = spots & where
    cv.mat[m] = mat
    cv.tone[m] += tone
    return m


# ---------------------------------------------------------------- the big tank

def spr_whale_shark():
    """A whale shark gliding: the broad flat head with its wide mouth at the very front, ridges
    running down the flanks, a tall first dorsal, long pectorals and the crescent tail; the dark
    blue-grey back covered in pale spots, the belly white. A young one, about 3.4 units long."""
    rng = np.random.default_rng(301)
    w, h = 240, 96
    cv = Canvas(w, h, wrap=False, ground=-9)
    ids = []
    for pts, z in (([(70, 37), (63, 29), (67, 28), (84, 35)], 0.2),                        # second dorsal
                   ([(150, 28), (137, 7), (143, 4), (180, 27)], 0.2),                      # first dorsal
                   ([(40, 40), (27, 24), (8, 3), (3, 6), (14, 28), (21, 44), (11, 66), (16, 69), (38, 49)], 0.2),
                   ([(96, 56), (86, 66), (90, 67), (106, 58)], 0.2),                       # pelvic
                   ([(66, 50), (58, 57), (62, 58), (76, 51)], 0.2)):                       # anal
        cv.polygon(pts, z=z, top=0.6, bevel=2.0, mat=0, tone=-0.04)
        ids.append(cv.n)
    xs, top, bot = _side(cv, [(32, 41.5, 46.5), (50, 39.5, 48.5), (80, 34, 54), (120, 28.5, 59), (160, 25.5, 62),
                              (192, 26.5, 62), (216, 29.5, 60), (229, 34, 57), (236, 40, 54), (238, 46, 51)],
                         z=0.4, dome=2.4, shade=0.3)
    body = cv.n
    ids.append(body)
    for k, (y0, y1) in enumerate(((33, 42.5), (40, 45.5), (47.5, 47))):                    # the ridges
        cv.stroke([(206, y0), (140, (y0 + y1) / 2 - 1), (60, y1)], 1.6, z=0, dome=0.35, mode='add')
    for k in range(5):                                                                     # gill slits
        x = 196 - k * 4
        cv.stroke([(x + 1, 37), (x, 46), (x + 1, 56)], 1.0, z=0, dome=0.45, mode='carve')
    cv.polygon([(198, 58), (182, 74), (154, 90), (149, 87), (168, 70), (174, 59)], z=1.5, top=0.7, bevel=2.5,
               mat=0, tone=0.02)                                                           # the near pectoral
    ids.append(cv.n)
    _band(cv, xs, top, bot, 0.7, 1.01, [body], 2)                                          # white belly
    back = np.isin(cv.id, ids) & (cv.mat == 0)
    yy = np.arange(h)[:, None]
    _dots(cv, rng, back & (yy < 60), (6.5, 5.0), 1.25, 1)                                  # the spots
    for x in range(126, 206, 10):                                                          # broken pale bars
        m = np.zeros((h, w), bool)                                                         # on the front of
        m[:, x:x + 1] = True                                                               # the body
        m &= back & (yy < 54) & (yy > 28) & ((yy + x // 10) % 5 < 3)
        cv.mat[m & (rng.random((h, w)) < 0.7)] = 1
    cv.stroke([(238, 49), (229, 50.5), (217, 51.5)], 1.6, z=0.6, dome=0.2, mat=3)          # the mouth
    cv.ellipse(213.5, 44.5, 1.3, 1.2, z=1.6, dome=0.3, mat=3)                              # the eye
    return _prop(cv, [WHALE, SPOT, BELLY, INK], relief=1.0, cavity=0.35, shadow=0.35, sun=TOP)


def spr_manta_ray():
    """A manta ray seen from below as it glides over: wings spread wide and pointed, the curled
    horns of its cephalic fins either side of the mouth, five pairs of gill slits on the white
    belly, a few dark blotches, a dark margin round the wings and a thin tail."""
    rng = np.random.default_rng(303)
    w, h = 200, 100
    cx = 100
    cv = Canvas(w, h, wrap=False, ground=-9)
    right = [(106, 30), (128, 31), (152, 36), (174, 45), (196, 60), (184, 61), (164, 62), (142, 64), (124, 70),
             (110, 78), (104, 82)]
    outline = [(cx - (x - cx), y) for x, y in reversed(right)] + right
    cv.polygon(outline, z=0.0, top=0.5, bevel=3.0, mat=0)                                  # the dark upper side
    inset = []
    for x, y in outline:                                                                   # the belly inside it
        dx, dy = x - cx, y - 52
        k = 0.93 if abs(dx) < 70 else 0.9
        inset.append((cx + dx * k, 52 + dy * k + (2.0 if y < 40 else -1.0)))
    cv.polygon(inset, z=0.05, top=0.55, bevel=4.0, mat=1)
    belly = cv.n
    cv.ellipse(cx, 52, 22, 26, z=0, dome=1.1, mode='add')                                  # the body
    for side in (-1, 1):
        cv.stroke([(cx + side * 7, 33), (cx + side * 11, 24), (cx + side * 9, 15), (cx + side * 5, 13)], 5.2, z=0.8,
                  dome=0.8, taper=(1.0, 0.55), mat=0, tone=0.1)                            # cephalic fins
        for k in range(5):                                                                 # gill slits
            y = 42 + k * 4.6
            cv.stroke([(cx + side * 10, y), (cx + side * 15, y + 1.2)], 1.0, z=0, dome=0.4, mode='carve')
    cv.ellipse(cx, 33, 7.5, 2.0, z=0.4, dome=0.2, mat=2)                                   # the mouth
    cv.stroke([(cx, 82), (cx + 1, 92), (cx - 1, 99)], 1.6, z=0.2, dome=0.4, taper=(1.0, 0.4), mat=0)   # tail
    for side in (-1, 1):                                                                   # pelvic fins
        cv.ellipse(cx + side * 5, 80, 4.0, 3.0, z=0.3, dome=0.5, mat=0)
    on = cv.id == belly
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    cv.tone[on] -= (0.3 * (np.abs(xx - cx) / 96.0) ** 1.6 + 0.08 * np.clip((yy - 60) / 20, 0, 1))[on]
    for _ in range(7):                                                                     # blotches
        bx, by = cx + rng.normal(0, 14), rng.uniform(56, 72)
        m = on & (((xx - bx) / rng.uniform(1.5, 3.0)) ** 2 + ((yy - by) / rng.uniform(1.2, 2.2)) ** 2 < 1)
        cv.mat[m] = 2
    return _prop(cv, [MANTA, MANTA_BELLY, INK], relief=1.0, cavity=0.3, shadow=0.3, sun=(-0.3, -0.6, 0.8))


def spr_reef_shark():
    """A blacktip reef shark cruising: a sleek bronze-grey body, the pointed snout, five gill slits,
    a white belly, and the black tips on its dorsal, pectoral and tail that give it its name."""
    w, h = 140, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    fins = []
    for pts in ([(86, 23), (77, 6), (81, 4.5), (101, 22)],                                  # first dorsal
                [(46, 28), (41, 22), (43.5, 21.5), (53, 27)],
                [(30, 30), (18, 17), (5, 3), (2, 5.5), (11, 21), (16, 32), (9, 44), (12.5, 45.5), (29, 35)],
                [(64, 38), (57, 45), (61, 45.5), (71, 39)],
                [(46, 34), (41, 40), (44.5, 40.5), (53, 35)]):
        cv.polygon(pts, z=0.2, top=0.5, bevel=1.5, mat=0, tone=-0.03)
        fins.append(cv.n)
    xs, top, bot = _side(cv, [(26, 30, 33.5), (40, 28.5, 35.5), (60, 25, 39), (85, 21.5, 41.5), (105, 21, 41),
                              (120, 23, 38.5), (130, 26, 36), (136, 29, 33.5), (139, 31, 32.5)], z=0.4, dome=2.0,
                         shade=0.26)
    body = cv.n
    for k in range(5):
        x = 112 - k * 3
        cv.stroke([(x + 0.5, 26.5), (x, 35)], 0.9, z=0, dome=0.4, mode='carve')
    cv.polygon([(110, 38), (98, 50), (91, 54), (93, 49), (100, 39)], z=1.4, top=0.6, bevel=1.5, mat=0)   # pectoral
    fins.append(cv.n)
    _band(cv, xs, top, bot, 0.62, 1.01, [body], 1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    fin = np.isin(cv.id, fins)
    tips = fin & (((yy < 11) & (xx > 70)) | (yy < 9) | (yy > 40) & (xx < 20) | (yy > 49) & (xx > 88))
    cv.mat[tips] = 2
    cv.stroke([(133, 34), (124, 35.5)], 0.9, z=0.6, dome=0.2, mat=2)                        # the mouth
    cv.ellipse(124.5, 28.0, 1.1, 1.0, z=1.6, dome=0.3, mat=2)                              # the eye
    return _prop(cv, [SHARK, BELLY, INK], relief=1.0, cavity=0.3, shadow=0.35, sun=TOP)


def spr_sea_turtle():
    """A green turtle swimming, seen from a little above: the domed shell in amber and brown scutes
    with a rim of small plates, the head reaching forward, the long front flippers sweeping back
    like wings (the far one darker) and the small rear ones trailing."""
    rng = np.random.default_rng(307)
    w, h = 124, 76
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.leaf(76, 26, 50, 3, 13, z=0.0, dome=0.6, rib=0.0, bend=-0.12, shape=0.8, base=0.3, mat=2, tone=-0.14)   # far flipper
    cv.leaf(34, 30, 18, 20, 8, z=0.0, dome=0.5, rib=0.0, shape=0.8, mat=2, tone=-0.12)    # far rear flipper
    cv.ellipse(58, 36, 34, 19, z=0.4, dome=1.8, mat=0)                                     # the shell
    shell = cv.n
    for k in range(18):                                                                    # marginal plates
        a = np.radians(200 + k * 11)
        cv.ellipse(58 + np.cos(a) * 31, 37 + np.sin(a) * 17, 4.0, 3.2, z=1.0, dome=0.5, mat=0,
                   tone=rng.normal(-0.02, 0.04), angle=np.degrees(a))
    for k in range(5):                                                                     # vertebral scutes
        cv.ellipse(36 + k * 11, 30 - 3 * np.sin(np.pi * k / 4), 6.0, 5.0, z=1.9 + 0.3 * np.sin(np.pi * k / 4),
                   dome=0.5, rough=0.15, rng=rng, mat=1, tone=rng.normal(0, 0.05))
    for k in range(4):                                                                     # costal scutes
        cv.ellipse(41 + k * 12, 41 - 2 * np.sin(np.pi * (k + 0.5) / 4), 6.5, 6.0, z=1.6, dome=0.5, rough=0.15,
                   rng=rng, mat=1, tone=rng.normal(-0.03, 0.05))
    cv.ellipse(91, 38, 9, 6.5, z=1.0, dome=1.0, mat=2)                                     # the neck
    cv.ellipse(104, 35, 10, 7.5, z=1.4, dome=1.2, mat=2)                                   # the head
    for x, y in ((100, 31), (106, 30), (103, 37), (109, 35), (97, 37)):                     # head scales
        cv.ellipse(x, y, 2.4, 1.9, z=2.4, dome=0.3, mat=3, tone=-0.05)
    cv.ellipse(108.5, 33.5, 1.7, 1.6, z=2.8, dome=0.0, mat=4)                              # the eye
    cv.stroke([(113.5, 37), (108, 39.5)], 0.9, z=2.5, dome=0.1, mat=4)                     # the beak
    cv.leaf(80, 46, 38, 70, 15, z=2.0, dome=0.7, rib=0.1, bend=0.15, shape=0.8, base=0.3, mat=2)   # near flipper
    near = cv.n
    cv.leaf(30, 46, 12, 58, 9, z=1.6, dome=0.6, rib=0.0, shape=0.8, mat=2)                 # near rear flipper
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    flip = np.isin(cv.id, [near, cv.n])
    _dots(cv, rng, flip, (5.0, 4.0), 1.1, 3, tone=-0.05)                                   # scaled skin
    del shell
    return _prop(cv, [SHELL, SCUTE, SKIN, SKIN_PALE, INK], relief=1.0, cavity=0.4, shadow=0.4, sun=TOP)


# ---------------------------------------------------------------- the reef's fish

def spr_clownfish():
    """A pair of clownfish: orange, with three white bands edged in black and black-edged fins.
    Tiny - about a hand long; set them in an `anemone`, or close to the glass."""
    w, h = 54, 24
    cv = Canvas(w, h, wrap=False, ground=-9)
    for ox, oy, s in ((2, 1, 1.0), (32, 8, 0.72)):
        def P(x, y):
            return ox + x * s, oy + y * s
        cv.polygon([P(4, 9), P(0, 4), P(0, 14)], z=0.0, top=0.5, bevel=1, mat=0)          # tail
        cv.ellipse(*P(16, 6), 8 * s, 3.4 * s, z=0.0, dome=0.6, mat=0)                       # dorsal fin
        cv.ellipse(*P(15, 9), 11 * s, 5.4 * s, z=0.4, dome=1.2, mat=0)                      # the body
        body = cv.n
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
        mine = (np.abs(xx - (ox + 15 * s)) < 13 * s) & (np.abs(yy - (oy + 8 * s)) < 8 * s) & (cv.id > 0)
        for bx, bw in ((21.0, 2.4), (14.0, 2.6), (5.5, 1.6)):
            x0 = ox + bx * s
            edge = mine & (np.abs(xx - x0) < (bw / 2 + 1.0) * s)
            cv.mat[edge] = 2
            cv.mat[mine & (np.abs(xx - x0) < bw / 2 * s)] = 1
        rim = mine & (cv.id != body) & ((np.abs(yy - (oy + 2.5 * s)) < 1.0 * s) | (xx < ox + 1.6 * s))
        cv.mat[rim] = 2
        cv.ellipse(*P(23, 7.5), 1.4 * s, 1.4 * s, z=1.8, dome=0.2, mat=2)                   # the eye
    return _prop(cv, [CLOWN, WHITE, INK], relief=1.0, cavity=0.3, shadow=0.3, sun=TOP)


def spr_angelfish():
    """An emperor angelfish: a tall oval body in close diagonal stripes of yellow and blue, a
    black mask through the eye edged in pale blue, a dark patch behind the head, a blue face and
    a bright yellow tail."""
    w, h = 42, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(10, 17), (2, 9), (4, 17), (2, 25)], z=0.0, top=0.5, bevel=1, mat=1)      # the tail
    cv.ellipse(15, 9.5, 9, 4.2, z=0.1, dome=0.5, angle=-18, mat=0)                         # dorsal fin
    cv.ellipse(15, 24.5, 9, 4.2, z=0.1, dome=0.5, angle=18, mat=2, tone=-0.1)             # anal fin
    _side(cv, [(9, 13, 21), (13, 8.5, 25.5), (20, 6.5, 27.5), (27, 7.5, 26.5), (32, 10, 23.5), (36, 13.5, 20.5),
               (38, 16, 18.5)], z=0.4, dome=1.4, shade=0.1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    on = (cv.id > 0) & (cv.mat == 0)
    stripe = (np.floor(yy) + np.floor(xx / 2)) % 3 == 0
    cv.mat[on & stripe & (xx < 28)] = 1
    lean = xx + 0.12 * (yy - 17)
    cv.mat[on & (lean >= 28)] = 2                                                          # the blue face
    cv.mat[on & (np.abs(lean - 29.5) < 2.9) & (yy > 7) & (yy < 26)] = 3                    # pale edge
    cv.mat[on & (np.abs(lean - 29.5) < 1.8) & (yy > 7.5) & (yy < 25.5)] = 4                # the mask
    cv.mat[on & (((xx - 25) / 2.2) ** 2 + ((yy - 18) / 6.5) ** 2 < 1)] = 4                 # shoulder patch
    cv.tone[on & (((xx - 25) / 2.2) ** 2 + ((yy - 18) / 6.5) ** 2 < 1)] += 0.25
    cv.ellipse(30.0, 14.0, 1.5, 1.5, z=2.0, dome=0.0, mat=3)                               # the eye
    cv.ellipse(30.0, 14.0, 0.8, 0.8, z=2.2, dome=0.0, mat=4)
    return _prop(cv, [EMPEROR, YELLOW, TANG, SPOT, INK], dither=0.0, relief=1.0, cavity=0.3, shadow=0.3, sun=TOP)


def spr_blue_tang():
    """A blue tang: an oval of royal blue with the black 'palette' loop along its side, black-edged
    fins top and bottom, a yellow tail and a yellow touch on the pectoral fin."""
    w, h = 40, 26
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(9, 13), (2, 6), (5, 13), (2, 20)], z=0.0, top=0.5, bevel=1, mat=1)        # the tail
    cv.ellipse(21, 13, 14, 9.5, z=0.1, dome=0.6, mat=2)                                    # fins, edged black
    cv.ellipse(22, 13, 13, 7.5, z=0.4, dome=1.3, mat=0)                                    # the body
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    on = cv.id == cv.n
    t = np.clip((xx - 10) / 20, 0, 1)
    upper = 9.0 + 1.5 * np.sin(t * np.pi)
    lower = 14.5 - 2.0 * np.sin(t * np.pi * 0.9)
    loop = on & (np.abs(yy - upper) < 1.6) & (xx > 10) & (xx < 31)
    loop |= on & (np.abs(yy - lower) < 1.2) & (xx > 12) & (xx < 25)
    loop |= on & (np.abs(xx - 11.5) < 1.6) & (yy > upper - 1) & (yy < lower + 1)
    cv.mat[loop] = 2
    cv.ellipse(22, 16.5, 3.5, 1.6, z=1.8, dome=0.3, mat=1, angle=20)                       # pectoral
    cv.ellipse(30.5, 10.5, 1.3, 1.3, z=1.9, dome=0.2, mat=2)                               # the eye
    return _prop(cv, [TANG, YELLOW, INK], relief=1.0, cavity=0.3, shadow=0.3, sun=TOP)


def spr_reef_shoal():
    """A shoal of anthias over the reef: three dozen small fish in orange-pink, a few purple and
    gold among them, all turning one way. Float it with `z` over coral."""
    rng = np.random.default_rng(311)
    w, h = 124, 62
    cv = Canvas(w, h, wrap=False, ground=-9)
    placed = []
    tries = 0
    while len(placed) < 36 and tries < 2000:
        tries += 1
        x, y = rng.normal(62, 25), rng.normal(31, 11)
        if not (8 <= x < w - 7 and 4 <= y < h - 4):
            continue
        if any(abs(x - px) < 11 and abs(y - py) < 4.5 for px, py in placed):
            continue
        placed.append((x, y))
    for x, y in sorted(placed, key=lambda p: p[1]):
        s = rng.uniform(0.8, 1.1)
        z = rng.random()
        m = int(rng.choice([0, 0, 0, 0, 0, 0, 1, 2]))
        cv.polygon([(x - 3.2 * s, y), (x - 6.4 * s, y - 2.2 * s), (x - 5.2 * s, y), (x - 6.4 * s, y + 2.2 * s)], z=z,
                   top=0.3, bevel=0.6, mat=m)
        cv.ellipse(x, y, 4.3 * s, 1.9 * s, z=z, dome=0.8, mat=m, tone=rng.normal(0, 0.05))
        cv.stroke([(x - 2.5 * s, y - 1.6 * s), (x + 2 * s, y - 2.1 * s)], 1.0 * s, z=z + 0.4, dome=0.2, mat=m,
                  tone=0.1)                                                                # the dorsal fin
        cv.put(np.array([int(y - 0.4)]), np.array([int(x + 2.4 * s)]), np.ones((1, 1), bool), z + 1.2, mat=3)
    return _prop(cv, [ANTHIAS, PURPLE, YELLOW, INK], relief=1.0, cavity=0.3, shadow=0.3, sun=TOP)


# ---------------------------------------------------------------- the reef

def spr_brain_coral():
    """A boulder of brain coral: a low dome covered in meandering ridges and grooves, ochre on the
    ridges and green-brown in the valleys, as round and furrowed as its name."""
    rng = np.random.default_rng(313)
    w, h = 72, 42
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(36, 44, 33, 38, z=0.0, dome=5.0, rough=0.04, rng=rng, mat=0)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    on = cv.id > 0
    cv.tone[on] += (0.12 - 0.22 * ((xx - 31) ** 2 / 33.0 ** 2) - 0.3 * (yy / h) ** 1.5)[on]   # lit on its crown
    n = smooth_noise(w, h, 4, rng, wrap=False) * 0.65 + smooth_noise(w, h, 8, rng, wrap=False) * 0.35
    groove = (np.abs((n * 15.0) % 1.0 - 0.5) < 0.17) & on
    cv.z[groove] -= 0.55
    cv.mat[groove] = 1
    return _prop(cv, [BRAIN, BRAIN_VALLEY], relief=1.2, cavity=0.5, shadow=0.4, sun=TOP)


def _branch(cv, rng, x, y, ang, length, width, depth, mat, tip, z=0.0):
    """One branch of a coral, forking `depth` times more; returns nothing, draws everything."""
    pts = [(x, y)]
    for t in (0.35, 0.7, 1.0):
        a = np.radians(ang + rng.normal(0, 8))
        pts.append((x + np.cos(a) * length * t, y + np.sin(a) * length * t))
    cv.stroke(pts, width, z=z, dome=0.8, taper=(1.0, 0.8 if depth else 0.6), mat=mat, tone=rng.normal(0, 0.04))
    ex, ey = pts[-1]
    if depth <= 0:
        cv.ellipse(ex, ey, width * 0.45, width * 0.45, z=z + 0.6, dome=0.4, mat=tip)
        return
    for d in (-1, 1) if rng.random() < 0.8 else (rng.choice([-1, 1]),):
        _branch(cv, rng, ex, ey, ang + d * rng.uniform(18, 34), length * rng.uniform(0.6, 0.8), width * 0.8,
                depth - 1, mat, tip, z + 0.2)


def spr_staghorn_coral():
    """A thicket of staghorn coral: golden-brown branches forking up and out like antlers, each tip
    pale and lilac where it is still growing."""
    rng = np.random.default_rng(317)
    w, h = 104, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(11):
        x0 = 26 + k * 5.2 + rng.normal(0, 1.5)
        a = -90 + (x0 - 52) * 0.8 + rng.normal(0, 8)
        _branch(cv, rng, x0, 63, a, rng.uniform(13, 20), 3.2, 2, 0, 1, z=rng.random() * 0.5)
    return _prop(cv, [STAG, STAG_TIP], relief=1.0, cavity=0.35, shadow=0.45, sun=TOP)


def spr_sea_fan():
    """A sea fan (a gorgonian): a flat lace of purple held up across the current from a short
    trunk - a few thicker branches fanning out, and between them a fine net of little cells."""
    rng = np.random.default_rng(319)
    w, h = 76, 78
    cx, cy = 38, 70
    cv = Canvas(w, h, wrap=False, ground=-9)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    th = np.arctan2(yy - cy, xx - cx)
    rim = 1 + 0.08 * (smooth_noise(w, h, 4, rng, wrap=False) - 0.5)
    fan = (((xx - cx) / 36) ** 2 + ((yy - cy) / 66) ** 2 < rim ** 2) & (yy < cy + 1) & (np.abs(th + np.pi / 2) < 1.45)
    n = 320                                                                                # the net: edges of
    sx, sy = rng.uniform(1, w - 1, n), rng.uniform(2, cy + 2, n)                           # little cells
    d = np.sort(np.hypot(xx[..., None] - sx, yy[..., None] - sy), axis=-1)
    net = fan & (d[..., 1] - d[..., 0] < 0.55)
    cv.put(np.arange(h), np.arange(w), net, np.full((h, w), 0.2, np.float32), mat=0, tone=-0.1)
    cv.stroke([(cx, h), (cx, cy - 2)], 3.4, z=0.6, dome=0.8, taper=(1.2, 0.9), mat=0)    # the trunk
    for a in np.radians([-162, -136, -112, -90, -68, -44, -18]):                           # the branches
        pts = [(cx, cy - 2)]
        L = 30 + 34 * np.sin(-a) ** 3
        for t in (0.3, 0.6, 0.85):
            pts.append((cx + np.cos(a) * L * t + rng.normal(0, 1.2), cy - 2 + np.sin(a) * L * t * 1.1))
        cv.stroke(pts, 2.0, z=0.6, dome=0.6, taper=(1.0, 0.5), mat=0, tone=0.06)
        ex, ey = pts[2]
        for d_ in (-1, 1):
            b = a + d_ * np.radians(rng.uniform(14, 24))
            cv.stroke([(ex, ey), (ex + np.cos(b) * L * 0.3, ey + np.sin(b) * L * 0.33)], 1.3, z=0.5, dome=0.5,
                      taper=(1.0, 0.6), mat=0, tone=0.04)
    cv.id[~(fan | ((yy > cy - 3) & (np.abs(xx - cx) < 3)))] = 0                         # trimmed to the fan
    return _prop(cv, [FAN], relief=0.8, cavity=0.2, shadow=0.3, sun=TOP)


def spr_anemone():
    """A bubble-tip anemone with its pair of clownfish: a red foot, a crown of soft tentacles in
    salmon pink each swollen to a bulb with a magenta tip, and the two fish nestled in among them."""
    rng = np.random.default_rng(321)
    w, h = 96, 66
    ramps = [ANEMONE, ANEMONE_TIP, ANEMONE_FOOT]
    lit = dict(relief=1.0, cavity=0.35, shadow=0.45, sun=TOP)

    def tentacles(cv, n, front):
        for k in range(n):
            x0 = 48 + rng.uniform(-20, 20)
            y0 = 61 - rng.uniform(0, 4) + (2 if front else 0)
            lean = (x0 - 48) / 20
            L = rng.uniform(20, 32) * (1 - 0.25 * abs(lean)) * (0.6 if front else 1.0)
            a = np.radians(-90 + lean * 55 + rng.normal(0, 14))
            bend = rng.normal(0, 3)
            pts = [(x0 + np.cos(a) * L * t + bend * np.sin(t * 3), y0 + np.sin(a) * L * t) for t in np.linspace(0, 1, 5)]
            z = rng.random() * 0.6
            cv.stroke(pts, 3.0, z=z, dome=0.9, taper=(0.7, 1.0), mat=0, tone=rng.normal(0, 0.06) - (0 if front else 0.1))
            ex, ey = pts[-1]
            cv.ellipse(ex, ey, 1.9, 2.3, z=z + 0.6, dome=0.7, mat=1)

    back = Canvas(w, h, wrap=False, ground=-9)
    back.ellipse(48, 63, 17, 3.5, z=0.0, dome=0.9, mat=2)                                 # the foot
    tentacles(back, 54, False)
    front = Canvas(w, h, wrap=False, ground=-9)
    tentacles(front, 16, True)
    rgba = back.paint(ramps, back.light(**lit), dither=0.3)
    fish = spr_clownfish()[0]
    from PIL import Image
    im = Image.fromarray((np.clip(fish, 0, 1) * 255).astype(np.uint8), 'RGBA')
    im = im.resize((int(fish.shape[1] * 0.8), int(fish.shape[0] * 0.8)), Image.NEAREST)
    fish = np.asarray(im, np.float32) / 255
    for layer, (fy, fx) in ((fish, (30, 27)),):
        lh, lw = layer.shape[:2]
        a = layer[..., 3:4]
        rgba[fy:fy + lh, fx:fx + lw, :3] = layer[..., :3] * a + rgba[fy:fy + lh, fx:fx + lw, :3] * (1 - a)
        rgba[fy:fy + lh, fx:fx + lw, 3:4] = np.maximum(rgba[fy:fy + lh, fx:fx + lw, 3:4], a)
    top = front.paint(ramps, front.light(**lit), dither=0.3)
    a = top[..., 3:4]
    rgba[..., :3] = top[..., :3] * a + rgba[..., :3] * (1 - a)
    rgba[..., 3:4] = np.maximum(rgba[..., 3:4], a)
    rgba = outline_sprite(rgba)
    return rgba.astype(np.float32), np.zeros((h, w), np.float32)


def spr_tube_sponge():
    """A cluster of tube sponges: violet tubes standing up from a shared base, each widening a
    little to an open dark mouth at the top."""
    rng = np.random.default_rng(323)
    w, h = 58, 60
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, top, r, z in ((24, 4, 6.0, 0.0), (40, 12, 5.5, 0.3), (12, 18, 5.0, 0.5), (50, 28, 4.2, 0.9),
                         (31, 24, 4.6, 1.2)):
        ys = np.arange(int(top), h - 1)
        hw = r * (0.8 + 0.2 * (1 - (ys - top) / (h - top))) + 0.35 * np.sin(ys * 0.45 + x)
        cx = x + 0.1 * (ys - h) * (x - 30) / 12
        X = np.arange(w)[None, :] + 0.5
        U = (X - cx[:, None]) / hw[:, None]
        mask = np.abs(U) < 1
        cv.put(ys, np.arange(w), mask, z + 1.6 * np.sqrt(np.clip(1 - U * U, 0, 1)), mat=0,
               tone=rng.normal(0, 0.05) - 0.12 * (U * U))
        rx = hw[0]
        cv.ellipse(cx[0], top + 0.5, rx, rx * 0.42, z=z + 2.2, dome=0.3, mat=0, tone=0.16)   # the lip
        cv.ellipse(cx[0], top + 0.7, rx - 1.6, rx * 0.42 - 1.0, z=z + 1.2, dome=0.0, mat=1)  # the mouth
    return _prop(cv, [SPONGE, SPONGE_IN], relief=1.0, cavity=0.4, shadow=0.45, sun=TOP)


def spr_reef_rock():
    """Live rock: a mound of reef rock grown over with everything - crusts of pink coralline, tufts
    of algae, a small brain coral, a staghorn thicket, a sea fan and a tube sponge - the piece
    to build a reef out of, in a tank or on the sea floor."""
    rng = np.random.default_rng(327)
    w, h = 140, 84
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(16):                                                                    # the rock
        x = rng.uniform(18, 122)
        top = 84 - 44 * np.sin(np.pi * (x - 6) / 128) ** 0.8
        cv.ellipse(x, rng.uniform(top + 12, 80), rng.uniform(12, 20), rng.uniform(10, 16), z=rng.random() * 0.5,
                   dome=1.6, rough=0.25, rng=rng, mat=0, tone=rng.normal(0, 0.06))
    rock = cv.id > 0
    crust = rock & (smooth_noise(w, h, 7, rng, wrap=False) > 0.6)
    cv.mat[crust] = 1
    weed = rock & (smooth_noise(w, h, 9, rng, wrap=False) > 0.66) & ~crust
    cv.mat[weed] = 2
    for _ in range(30):                                                                    # pits and holes
        cv.ellipse(rng.uniform(10, 130), rng.uniform(40, 82), rng.uniform(1, 2.5), rng.uniform(1, 2), z=0.6,
                   dome=0.5, mode='carve')
    rgba = cv.paint([LIVE_ROCK, CORALLINE, ALGAE], cv.light(relief=1.0, cavity=0.5, shadow=0.45, sun=TOP),
                    dither=0.3)
    rgba[..., 3] = rock.astype(np.float32)

    def put(sprite, x, bottom, height):
        src = sprite[0]
        sh, sw = src.shape[:2]
        k = height / sh
        from PIL import Image
        im = Image.fromarray((np.clip(src, 0, 1) * 255).astype(np.uint8), 'RGBA')
        im = im.resize((max(1, int(sw * k)), max(1, int(sh * k))), Image.NEAREST)
        s = np.asarray(im, np.float32) / 255
        y0, x0 = int(bottom - s.shape[0]), int(x - s.shape[1] / 2)
        ys, xs = slice(max(0, y0), min(h, y0 + s.shape[0])), slice(max(0, x0), min(w, x0 + s.shape[1]))
        s = s[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
        a = s[..., 3:4]
        rgba[ys, xs, :3] = s[..., :3] * a + rgba[ys, xs, :3] * (1 - a)
        rgba[ys, xs, 3:4] = np.maximum(rgba[ys, xs, 3:4], a)

    put(spr_sea_fan(), 98, 48, 44)
    put(spr_staghorn_coral(), 42, 46, 30)
    put(spr_tube_sponge(), 118, 62, 28)
    put(spr_brain_coral(), 70, 44, 18)
    put(spr_brain_coral(), 24, 64, 12)
    rgba = outline_sprite(rgba)
    return rgba.astype(np.float32), np.zeros((h, w), np.float32)


# ---------------------------------------------------------------- the jelly tank

def spr_sea_nettle():
    """A sea nettle: a golden bell striped with rust from its crown to its scalloped rim, long
    fine maroon tentacles and four pale frilled arms twisting down below - half see-through, for
    a jelly tank lit blue from behind."""
    rng = np.random.default_rng(331)
    w, h = 44, 120
    cx, cy, rx, ry = 22, 19, 17, 15
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    rim_y = cy + 2 + 1.4 * np.sin((xx - cx) * 1.3)
    bell = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1) & (yy <= rim_y)
    th = np.arctan2(xx - cx, cy - yy + 4)
    stripe = (np.abs((th * 16 / np.pi) % 2 - 1) < 0.35) & bell
    shade = np.clip(1.15 - 0.5 * ((xx - cx + 5) / rx) ** 2 - 0.35 * (yy - cy + ry) / (2 * ry), 0.35, 1.2)
    col = np.array(NETTLE[3], np.float32)
    dark = np.array(NETTLE_DARK[2], np.float32)
    rgba[bell, :3] = (col[None, :] * shade[bell][:, None])
    rgba[stripe, :3] = dark * shade[stripe][:, None]
    rgba[bell, 3] = 0.9
    em[bell] = 0.5
    for k in range(12):                                                                    # tentacles
        x0 = cx - rx + 2 + k * (2 * rx - 4) / 11
        ph = rng.uniform(0, 6)
        for y in range(int(rim_y[0, int(x0)]), h - 1):
            t = (y - cy) / (h - cy)
            x = int(round(x0 + np.sin(y / 9.0 + ph) * 3.5 * t + (x0 - cx) * 0.5 * t))
            if 0 <= x < w:
                rgba[y, x, :3] = np.array(NETTLE_DARK[3], np.float32)
                rgba[y, x, 3] = 0.6
                em[y, x] = 0.1
    for k in range(4):                                                                     # oral arms
        x0 = cx + (k - 1.5) * 2.5
        for y in range(int(cy + 2), int(cy + 64)):
            t = (y - cy) / 64
            x = x0 + np.sin(y / 6.0 + k * 1.6) * (1.5 + 3 * t) + (k - 1.5) * 3 * t
            wd = 1.3 + 0.9 * np.sin(y * 1.1 + k) * (1 - t)
            for dx in range(-2, 3):
                xi = int(round(x)) + dx
                if abs(dx) <= wd and 0 <= xi < w:
                    edge = abs(dx) >= wd - 0.8
                    rgba[y, xi, :3] = np.array(FRILL[4 if edge else 2], np.float32)
                    rgba[y, xi, 3] = 0.7 if edge else 0.55
                    em[y, xi] = 0.15
    return rgba, em


def spr_moon_jelly():
    """A moon jelly: a wide, clear saucer of a bell with the four lilac crescents of its gonads
    showing through in a ring, a fringe of short tentacles and four short arms. Glowing and
    see-through (additive by default)."""
    w, h = 52, 34
    cx, cy, rx, ry = 26, 10, 23, 8.5
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    disc = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    edge = disc & (((xx - cx) / (rx - 1.5)) ** 2 + ((yy - cy) / (ry - 1.2)) ** 2 > 1)
    rgba[disc, :3] = (0.28, 0.36, 0.5)
    rgba[edge, :3] = (0.7, 0.78, 0.92)
    d = np.hypot((xx - cx) / 11.0, (yy - cy - 0.5) / 4.6)
    ang = np.degrees(np.arctan2((yy - cy - 0.5) * 2.4, xx - cx)) % 90
    ring = disc & (d < 1) & (d > 0.55) & (ang > 12) & (ang < 78)
    rgba[ring, :3] = (0.92, 0.6, 0.95)
    rgba[disc, 3] = 1.0
    em[disc] = 0.8
    for x in range(int(cx - rx + 2), int(cx + rx - 1), 2):                                  # fringe
        y0 = int(cy + ry * np.sqrt(max(0.0, 1 - ((x + 0.5 - cx) / rx) ** 2)))
        for y in range(y0, min(h, y0 + 3)):
            rgba[y, x, :3] = (0.55, 0.62, 0.8)
            rgba[y, x, 3] = 1.0
            em[y, x] = 0.6
    for k in range(4):                                                                     # short arms
        x0 = cx + (k - 1.5) * 4
        for y in range(int(cy + 4), int(cy + 22)):
            x = int(x0 + np.sin(y / 3.0 + k) * 1.5)
            rgba[y, x, :3] = (0.75, 0.62, 0.9)
            rgba[y, x, 3] = 1.0
            em[y, x] = 0.7
    return rgba, em


# ---------------------------------------------------------------- the visitors' side

def spr_info_plaque():
    """An aquarium's information plaque on its post: a slanted panel lit from behind, showing a
    fish's outline and lines of text too small to read, glowing blue in the dark of the hall."""
    w, h = 44, 52
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(19, 22, 6, 30, z=0.0, top=0.8, bevel=2.0, mat=0)                                # the post
    cv.box(12, 48, 20, 4, z=0.0, top=0.6, bevel=1.5, mat=0)                                # its foot
    cv.polygon([(2, 6), (42, 2), (42, 24), (2, 26)], z=0.6, top=0.8, bevel=2.0, mat=0)     # the frame
    cv.polygon([(5, 8), (39, 5), (39, 21), (5, 23)], z=1.0, top=0.2, bevel=0.5, mat=1)     # the lit panel
    panel = cv.id == cv.n
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    fish = (((xx - 13) / 5.5) ** 2 + ((yy - 13.5) / 3.0) ** 2 < 1) | \
        ((xx > 5.5) & (xx < 9) & (np.abs(yy - 13.5) < (9 - xx) * 0.9))
    lines = (xx > 21) & (xx < 37) & (np.isin(np.floor(yy), (9, 12, 15, 18))) & ((xx < 33) | (yy < 17))
    cv.mat[panel & (fish | lines)] = 2
    em = np.where(panel, 0.75, 0.0) + np.where(panel & (fish | lines), 0.25, 0.0)
    return _prop(cv, [STEEL, PANEL, ramp('#a8e0f0', dark=0.7, light=1.05)], relief=1.0, cavity=0.3, shadow=0.3,
                 em=em)


# ---------------------------------------------------------------- textures

def tex_reef_wall(name):
    """The rockwork at the back of a reef tank: lumps of live rock in shadow and light, patches of
    pink coralline, small coral heads, tufts of green algae and clusters of bright polyps, dark
    crevices between - a wall of reef that tiles."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.0)
    for _ in range(18):                                                                    # rock lumps
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(6, 11), rng.uniform(5, 8), z=rng.random() * 0.6,
                   dome=1.5, rough=0.3, rng=rng, mat=0, tone=rng.normal(-0.02, 0.07))
    crust = smooth_noise(T, T, 9, rng) > 0.66
    cv.mat[crust & (cv.id > 0)] = 1
    for _ in range(9):                                                                     # coral heads
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(2.0, 3.6), rng.uniform(1.6, 2.8), z=1.9,
                   dome=0.8, mat=int(rng.choice([3, 3, 4])), tone=rng.normal(0, 0.06))
    for _ in range(12):                                                                    # algae tufts
        x, y = rng.random() * T, rng.random() * T
        for k in range(4):
            a = np.radians(-90 + rng.normal(0, 30))
            L = rng.uniform(2.0, 4.0)
            cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], 1.1, z=2.0, dome=0.3, taper=(1, 0.5), mat=2)
    for _ in range(6):                                                                     # polyp clusters
        x, y = rng.random() * T, rng.random() * T
        m = int(rng.choice([2, 4, 5]))
        for k in range(7):
            cv.ellipse(x + rng.normal(0, 2.2), y + rng.normal(0, 1.6), 0.9, 0.9, z=2.3, dome=0.4, mat=m, tone=0.12)
    cv.noise(0.25, cells=10, rng=rng)
    return _tile(cv, [LIVE_ROCK, CORALLINE, ALGAE, BRAIN, PURPLE, ANTHIAS], dither=0.3, relief=1.1, cavity=0.55,
                 shadow=0.5, ambient=0.3, diffuse=0.65, sun=TOP)


def tex_tunnel_roof(name):
    """The view up through the roof of a walk-through tunnel: deep blue water with the bright,
    rippled surface far above and its net of light, and a seam of the acrylic arch at the edge of
    every tile. It glows - the light is coming down through it."""
    rng = _rng(name)
    swell = smooth_noise(T, T, 3, rng) * 0.6 + smooth_noise(T, T, 5, rng) * 0.4
    n = 7
    sx, sy = rng.random(n) * T, rng.random(n) * T
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    dx = np.abs(xx[..., None] - sx)
    dy = np.abs(yy[..., None] - sy)
    d = np.sort(np.hypot(np.minimum(dx, T - dx), np.minimum(dy, T - dy)), axis=-1)
    net = np.exp(-(d[..., 1] - d[..., 0]) / 2.0)
    v = np.clip(0.15 + 0.3 * swell + 0.35 * net, 0, 1)
    seam = (yy < 2) | (yy >= T - 1)
    v = np.where(seam, 0.04, v)
    pal = np.asarray(ramp('#1e5a8e', dark=0.3, light=1.7, cool=0.1), np.float32)
    bay = np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0, (T // 4, T // 4))
    idx = np.clip(np.round(v * (len(pal) - 1) + (bay - 0.5) * 0.6), 0, len(pal) - 1).astype(int)
    rgb = pal[idx]
    rgb[seam] = np.array([0.06, 0.09, 0.12], np.float32)
    em = np.where(seam, 0.05, 0.35 + 0.55 * v).astype(np.float32)
    return rgb, em


def tex_jelly_backdrop(name):
    """The back wall of a jelly tank: an even, glowing deep blue with the faintest mottling, so
    whatever drifts in front of it stands out as a silhouette of light."""
    rng = _rng(name)
    v = 0.5 + 0.16 * (smooth_noise(T, T, 2, rng) - 0.5) + 0.06 * (smooth_noise(T, T, 5, rng) - 0.5)
    pal = np.asarray(ramp('#1a46a0', dark=0.6, light=1.2, cool=0.1), np.float32)
    bay = np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0, (T // 4, T // 4))
    idx = np.clip(np.round(v * (len(pal) - 1) + (bay - 0.5) * 0.5), 0, len(pal) - 1).astype(int)
    return pal[idx], np.full((T, T), 0.8, np.float32)


WATER = ramp('#1c5a7e', n=8, dark=0.28, light=1.75, cool=0.1, warm=0.04)


def _open_water(name, z0):
    """A storey (z0 to z0 + 1) of open water: blue, deep toward the floor and paler toward the light
    coming down from the surface, soft shafts in it. It glows a little, being lit from above."""
    rng = _rng(name)
    z = z0 + 1 - (np.arange(T)[:, None] + 0.5) / T                         # height of each row
    up = np.clip(z / 2.0, 0, 1)
    shafts = (smooth_noise(T, T, 5, rng, cells_y=1) * 0.6 + smooth_noise(T, T, 9, rng, cells_y=1) * 0.4) - 0.5
    v = np.clip(0.1 + 0.8 * up ** 1.2 + 0.16 * shafts * up ** 2 + 0.05 * (smooth_noise(T, T, 4, rng) - 0.5), 0, 1)
    return dither(v, WATER, 0.7), (0.5 + 0.5 * v).astype(np.float32)


def tex_open_water(name):
    """The open water at the back of a big tank, as aquariums paint it so the tank seems to go on:
    the upper storey of a wall two high, paler toward the surface. Stack it over `deep_water`."""
    return _open_water(name, 1.0)


def tex_deep_water(name):
    """The lower storey of `open_water`: the same blue going deep toward the floor."""
    return _open_water(name, 0.0)


def tex_tank_window(name):
    """A viewing window into a tank (see-through): a deep frame of dark painted steel with
    rounded corners round an opening from just above the floor to near the top of the storey.
    Stand a `glass_pane` just behind it for the water; stack plain wall above it."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0)
    cv.noise(0.12, cells=8, rng=rng)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    x0, x1, y0, y1, r = 5, 59, 7, 57, 7
    d = np.hypot(xx - np.clip(xx, x0 + r, x1 - r), yy - np.clip(yy, y0 + r, y1 - r)) - r
    edge = np.maximum(d, np.maximum(np.maximum(x0 - xx, xx - x1), np.maximum(y0 - yy, yy - y1)))
    rim = (edge > 0) & (edge < 3.5)
    cv.z += np.where(rim, 0.9 - 0.25 * edge, 0.0).astype(np.float32)
    cv.mat[rim] = 1
    for y in (2, 61):                                                                      # bolt heads
        for x in range(6, 60, 9):
            cv.ellipse(x, y, 1.0, 1.0, z=0.6, dome=0.4, mat=1)
    rgb = _tile(cv, [ramp('#2a2e34', dark=0.5, light=1.4), STEEL], dither=0.3, relief=1.0, cavity=0.4, shadow=0.4)
    return rgb, None, (edge > 0).astype(np.float32)


TEXTURES = {'reef_wall': lambda n: (tex_reef_wall(n), None), 'tunnel_roof': tex_tunnel_roof,
            'jelly_backdrop': tex_jelly_backdrop, 'tank_window': tex_tank_window, 'open_water': tex_open_water,
            'deep_water': tex_deep_water}
TEXTURE_NOISE = {'reef_wall': 0.8, 'tunnel_roof': 0.2, 'jelly_backdrop': 0.1, 'tank_window': 0.3, 'open_water': 0.05,
                 'deep_water': 0.05}
SPRITES = {'whale_shark': spr_whale_shark, 'manta_ray': spr_manta_ray, 'reef_shark': spr_reef_shark,
           'sea_turtle': spr_sea_turtle, 'clownfish': spr_clownfish, 'angelfish': spr_angelfish,
           'blue_tang': spr_blue_tang, 'reef_shoal': spr_reef_shoal, 'brain_coral': spr_brain_coral,
           'staghorn_coral': spr_staghorn_coral, 'sea_fan': spr_sea_fan, 'anemone': spr_anemone,
           'tube_sponge': spr_tube_sponge, 'reef_rock': spr_reef_rock, 'sea_nettle': spr_sea_nettle,
           'moon_jelly': spr_moon_jelly, 'info_plaque': spr_info_plaque}
SPRITE_HEIGHT = {'whale_shark': 1.36, 'manta_ray': 0.9, 'reef_shark': 0.25, 'sea_turtle': 0.3, 'clownfish': 0.07,
                 'angelfish': 0.13, 'blue_tang': 0.08, 'reef_shoal': 0.5, 'brain_coral': 0.3, 'staghorn_coral': 0.42,
                 'sea_fan': 0.62, 'anemone': 0.26, 'tube_sponge': 0.36, 'reef_rock': 0.6, 'sea_nettle': 0.45,
                 'moon_jelly': 0.12, 'info_plaque': 0.42}
_SWIMMERS = ('whale_shark', 'manta_ray', 'reef_shark', 'sea_turtle', 'clownfish', 'angelfish', 'blue_tang',
             'reef_shoal', 'sea_nettle', 'moon_jelly')
PROP_DEFAULTS = {k: {'shadow': False} for k in _SWIMMERS}
PROP_DEFAULTS['moon_jelly'] = {'blend': 'additive', 'shadow': False}
NO_CONTACT_SHADOW = set(_SWIMMERS)

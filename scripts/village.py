"""The countryside, drawn with the pixel-art toolkit (scripts/pixelart.py): the things at the edge
of a field and along a village lane - a scarecrow, pumpkins, hay bales and the crows that are not
afraid of the scarecrow - and on a village street: a well, a hand cart, a market stall and the
sign of the inn.

As in the other toolkit modules, every shape is stamped into a height field, lit from the upper
left and snapped onto hue-shifted ramps.
"""
import numpy as np

from biomes import _prop
from dream import _lathe
from pixelart import Canvas, ramp

STRAW = ramp('#c8a85a', dark=0.4, light=1.18)
BURLAP = ramp('#a88a60', dark=0.4)
COAT = ramp('#4e5a3a', dark=0.35)
PATCH = ramp('#8a4a36', dark=0.35)
HAT = ramp('#6a5a40', dark=0.35)
POST = ramp('#6e5238', dark=0.3)
STITCH = ramp('#2a2420', dark=0.6, light=1.6)
PUMPKIN = ramp('#d0782a', dark=0.3, light=1.25, warm=0.15)
STEM = ramp('#6a6a34', dark=0.35)
LEAF = ramp('#4e6e2c', dark=0.3)
TWINE = ramp('#7a5a34', dark=0.4)
CARVED = ramp('#ffc24a', dark=0.78, light=1.2, warm=0.05)
CROW = ramp('#22242c', dark=0.45, light=1.75, warm=0.0, cool=0.35)
BEAK = ramp('#4a4a4e', dark=0.5, light=1.6)
FIELDSTONE = ramp('#8e8a80', dark=0.35, light=1.2)
OAK = ramp('#5a4632', dark=0.3)
SHINGLE = ramp('#6a5444', dark=0.35)
IRON = ramp('#3a3a3e', dark=0.45, light=1.7)
CANVAS_RED = ramp('#a8382c', dark=0.35, light=1.25)
CANVAS_WHITE = ramp('#e2dccb', dark=0.5, light=1.06)
APPLE = ramp('#b8382a', dark=0.35, light=1.3)
CABBAGE = ramp('#6a9a4a', dark=0.35, light=1.25)
BREAD = ramp('#c08a48', dark=0.35, light=1.2)
SIGN_RED = ramp('#7a2422', dark=0.35, light=1.3)
GILT = ramp('#d8b048', dark=0.45, light=1.2)


def _crow(cv, x, y, s=1.0, z=2.0, facing=1, mats=(0, 1)):
    """A crow standing at (x, y) - its feet - `s` times life size on the canvas, facing right (1)
    or left (-1): a glossy black body, the head up, a heavy beak, the tail angled down. `mats` are
    the materials for its feathers and its beak and legs."""
    f = facing
    body, bill = mats
    cv.ellipse(x - f * 0.5 * s, y - 4.2 * s, 4.2 * s, 2.8 * s, z=z, dome=1.0, angle=f * 18, mat=body)       # body
    cv.polygon([(x - f * 3.0 * s, y - 4.6 * s), (x - f * 8.2 * s, y - 2.0 * s), (x - f * 7.4 * s, y - 0.8 * s),
                (x - f * 2.6 * s, y - 3.0 * s)], z=z + 0.2, top=0.6, bevel=1, mat=body, tone=-0.05)         # tail
    cv.ellipse(x + f * 3.0 * s, y - 7.4 * s, 2.0 * s, 1.9 * s, z=z + 0.4, dome=1.0, mat=body)              # head
    cv.polygon([(x + f * 4.4 * s, y - 8.0 * s), (x + f * 7.6 * s, y - 7.2 * s), (x + f * 4.4 * s, y - 6.4 * s)],
               z=z + 0.6, top=0.5, bevel=0.6, mat=bill)                                                    # beak
    cv.stroke([(x + f * 0.2 * s, y - 4.0 * s), (x - f * 2.6 * s, y - 5.4 * s)], 1.0 * s, z=z + 1.1, dome=0.3,
              mat=body, tone=0.08)                                                                       # the wing's edge
    for dx in (-0.6, 0.7):                                                                             # legs
        cv.stroke([(x + dx * s, y - 1.8 * s), (x + dx * s + f * 0.3, y)], 0.7, z=z - 0.2, dome=0.2, mat=bill)


def spr_scarecrow():
    """A scarecrow in a field: a post and crossbar, a sack head tied at the neck with a stitched
    face, a battered hat, an old coat patched at the elbow and hung on the bar with its arms out,
    straw sticking out of the cuffs, the collar and the hem - and a crow on one arm."""
    rng = np.random.default_rng(141)
    w, h = 64, 92
    cx = 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(cx, h), (cx, 22)], 3.4, z=0.0, dome=0.8, taper=(1.15, 0.9), mat=4)                     # post
    cv.stroke([(cx - 25, 36), (cx + 24, 35)], 2.8, z=0.2, dome=0.8, mat=4)                             # crossbar
    for k in range(12):                                                                               # straw below the hem
        x = cx + rng.uniform(-9, 9)
        cv.stroke([(x, 62), (x + rng.normal(0, 1.2), 62 + rng.uniform(4, 9))], 0.9, z=0.8, dome=0.3, taper=(1, 0.4),
                  mat=0, tone=rng.normal(0, 0.06))
    for side in (-1, 1):                                                                              # the sleeves, along the bar
        cv.polygon([(cx + side * 6, 31), (cx + side * 21, 32.5), (cx + side * 22, 40.5), (cx + side * 9, 41)],
                   z=1.0, top=0.9, bevel=2.2, mat=1, tone=-0.03)
        for k in range(8):                                                                            # straw at the cuff
            a = np.radians(90 - side * 90 + rng.uniform(-50, 50))
            L = rng.uniform(4, 8)
            x0, y0 = cx + side * 21, 36.5 + rng.uniform(-2.5, 2.5)
            cv.stroke([(x0, y0), (x0 + side * abs(np.cos(a)) * L, y0 + np.sin(a) * L * 0.8)], 0.9, z=1.8, dome=0.3,
                      taper=(1, 0.45), mat=0, tone=rng.normal(0.02, 0.06))
    hem = [(cx + 11, 64)] + [(cx + 11 - k * 2.2, 64 + (3 if k % 2 else -1) + rng.uniform(-1, 1)) for k in range(1, 10)] \
        + [(cx - 11, 64)]
    cv.polygon([(cx - 9, 30), (cx + 9, 30), (cx + 12, 45), (cx + 11, 64)] + hem[1:-1] + [(cx - 11, 64), (cx - 12, 45)],
               z=1.2, top=1.0, bevel=3.0, mat=1)                                                       # the coat
    cv.stroke([(cx, 31), (cx + 0.5, 62)], 0.8, dome=0.3, mode='carve')                                  # its front edge
    for y in (40, 47, 54):
        cv.ellipse(cx + 2.2, y, 0.9, 0.9, z=2.4, dome=0.4, mat=5)                                        # buttons
    cv.box(cx - 9, 48, 6, 6, z=1.9, top=0.4, bevel=1, mat=2, tone=0.02)                                 # patches
    cv.box(cx + 13, 34, 5, 5, z=1.9, top=0.4, bevel=1, mat=2, tone=-0.03)
    for px, py in ((cx - 9, 48), (cx + 13, 34)):
        for k in range(3):
            cv.stroke([(px + 1 + k * 2, py - 0.4), (px + 1 + k * 2, py + 0.6)], 0.5, z=2.5, dome=0.1, mat=5)
    for k in range(9):                                                                                # straw at the collar
        a = np.radians(rng.uniform(200, 340))
        cv.stroke([(cx + rng.uniform(-3, 3), 30), (cx + np.cos(a) * 5, 30 + np.sin(a) * 2.5)], 0.9, z=2.2, dome=0.3,
                  taper=(1, 0.5), mat=0, tone=rng.normal(0.03, 0.05))
    cv.ellipse(cx, 22, 7.6, 8.2, z=2.0, dome=1.2, rough=0.08, rng=rng, mat=3)                            # the sack head
    cv.stroke([(cx - 5, 29.2), (cx + 5, 29.4)], 1.4, z=3.2, dome=0.4, mat=4)                             # tied with twine
    for ex in (-3, 3):                                                                                # eyes: stitched crosses
        cv.stroke([(cx + ex - 1.3, 19.2), (cx + ex + 1.3, 21.6)], 0.8, z=3.4, dome=0.1, mat=5)
        cv.stroke([(cx + ex - 1.3, 21.6), (cx + ex + 1.3, 19.2)], 0.8, z=3.4, dome=0.1, mat=5)
    cv.stroke([(cx - 3.5, 25.2), (cx, 26.0), (cx + 3.5, 25.0)], 0.7, z=3.4, dome=0.1, mat=5)              # the mouth
    for k in range(5):
        x = cx - 3 + k * 1.5
        cv.stroke([(x, 24.4), (x, 26.6)], 0.5, z=3.5, dome=0.1, mat=5)
    cv.ellipse(cx, 15.5, 12.5, 2.6, z=3.6, dome=0.5, mat=6, angle=-4)                                  # the hat's brim
    cv.polygon([(cx - 7, 15.5), (cx - 5.5, 6.5), (cx - 1, 4.8), (cx + 4, 6.2), (cx + 6.5, 15.2)], z=3.8, top=1.2,
               bevel=2.0, mat=6)
    cv.stroke([(cx - 6.6, 13.2), (cx + 6.4, 12.8)], 1.3, z=5.2, dome=0.3, mat=2, tone=-0.08)            # a band
    cv.stroke([(cx - 1, 5.2), (cx + 0.5, 9)], 0.8, dome=0.3, mode='carve')                              # the dent
    _crow(cv, cx + 19, 33.6, s=0.95, z=3.0, facing=-1, mats=(7, 8))
    return _prop(cv, [STRAW, COAT, PATCH, BURLAP, POST, STITCH, HAT, CROW, BEAK], relief=1.0, cavity=0.4,
                 shadow=0.45)


def _pumpkin(cv, rng, cx, cy):
    """The gourd: deep ribs, the outer ones first, a woody stem, a curl of vine and a leaf."""
    for dx, rx in ((-9.5, 5.0), (9.5, 5.0), (-5.5, 6.0), (5.5, 6.0), (0, 6.6)):      # ribs, the outer ones first
        cv.ellipse(cx + dx, cy, rx, 8.6 - abs(dx) * 0.12, z=0.3 - abs(dx) * 0.02, dome=1.6, mat=0,
                   tone=-abs(dx) * 0.006 + rng.normal(0, 0.02))
    cv.stroke([(cx, 7.5), (cx + 1, 4.5), (cx + 3, 2)], 2.2, z=2.2, dome=0.7, taper=(1.2, 0.7), mat=1)  # stem
    a = np.linspace(0, 1.6 * np.pi, 14)
    cv.stroke(list(zip(cx + 5 + np.cos(a) * (1 + a * 0.4), 5 + np.sin(a) * (1 + a * 0.3))), 0.6, z=2.3, dome=0.2,
              mat=1)                                                                      # a curl of vine
    cv.leaf(cx - 2, 7, cx - 9, 3, 4.2, z=2.0, dome=0.5, mat=2, rib=0.3)


def spr_pumpkin():
    """A pumpkin: a squat orange gourd of deep ribs, a woody stem and a curl of vine with a leaf."""
    cv = Canvas(32, 24, wrap=False, ground=-9)
    _pumpkin(cv, np.random.default_rng(143), 16, 14.5)
    return _prop(cv, [PUMPKIN, STEM, LEAF], relief=1.0, cavity=0.5, shadow=0.45)


def spr_jack_o_lantern():
    """A pumpkin carved into a face and lit from inside: three-cornered eyes, a nose, a grin with
    two teeth left in it, all burning yellow-orange (emissive), the rind darker round them."""
    cv = Canvas(32, 24, wrap=False, ground=-9)
    cx = 16
    _pumpkin(cv, np.random.default_rng(147), cx, 14.5)
    cut = [[(cx - 7.5, 12.8), (cx - 2.5, 12.8), (cx - 4.6, 8.8)],                   # eyes
           [(cx + 2.5, 12.8), (cx + 7.5, 12.8), (cx + 4.6, 8.8)],
           [(cx - 1.2, 15.6), (cx + 1.2, 15.6), (cx, 13.6)],                         # nose
           [(cx - 8.5, 16.6), (cx - 6, 18.0), (cx - 4, 17.2), (cx - 3.2, 19.4), (cx - 1, 18.2), (cx + 1, 18.2),
            (cx + 3.2, 19.4), (cx + 4, 17.2), (cx + 6, 18.0), (cx + 8.5, 16.6), (cx + 6.5, 21.2), (cx + 3.4, 20.0),
            (cx + 3.4, 21.6), (cx + 1.4, 21.6), (cx, 20.4), (cx - 1.4, 21.6), (cx - 3.4, 21.6), (cx - 3.4, 20.0),
            (cx - 6.5, 21.2)]]                                                       # the grin
    for pts in cut:
        cv.polygon(pts, z=-0.4, top=0.3, bevel=0.8, mat=3)
    glow = (cv.mat == 3) & (cv.id > 0)
    cv.tone += np.where(glow, 0.4, np.where(cv.mat == 0, -0.14, 0.0)).astype(np.float32)   # bright cuts, a darker rind
    return _prop(cv, [PUMPKIN, STEM, LEAF, CARVED], relief=1.0, cavity=0.5, shadow=0.45, em=glow * 1.0)


def spr_hay_bale():
    """A square bale of straw: a block packed with stalks running along it, two bands of twine
    round it, loose ends bristling at the cut faces."""
    rng = np.random.default_rng(145)
    w, h = 44, 28
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(3, 5, 38, 22, z=0.0, top=1.6, bevel=3.5, rough=0.8, rng=rng, mat=0)
    for _ in range(90):                                                       # stalks along the bale
        x, y = rng.uniform(3, 40), rng.uniform(6, 26)
        cv.stroke([(x, y), (x + rng.uniform(3, 7), y + rng.normal(0, 0.4))], 0.7, dome=0.3,
                  mode='carve' if rng.random() < 0.5 else 'add', mat=0)
    for x in (13, 30):                                                        # twine
        cv.stroke([(x, 4.5), (x + 0.4, 27)], 1.2, z=1.75, dome=0.4, mat=1)
    for _ in range(26):                                                       # loose ends
        side = rng.choice([0, 1, 2])
        if side == 2:
            x, y, a = rng.uniform(5, 39), 5.5, np.radians(rng.uniform(-150, -30))
        else:
            x, y = (3.5, rng.uniform(7, 25)) if side == 0 else (40.5, rng.uniform(7, 25))
            a = np.radians(180 + rng.uniform(-30, 30)) if side == 0 else np.radians(rng.uniform(-30, 30))
        L = rng.uniform(1.5, 3.5)
        cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], 0.8, z=1.2, dome=0.3, taper=(1, 0.5), mat=0,
                  tone=rng.normal(0.04, 0.05))
    return _prop(cv, [STRAW, TWINE], relief=1.0, cavity=0.45, shadow=0.45)


def spr_crow():
    """A crow on the ground: glossy black with a blue sheen where the light catches it, the head
    up and a heavy beak - for fields, fences and gallows."""
    w, h = 22, 14
    cv = Canvas(w, h, wrap=False, ground=-9)
    _crow(cv, 11, 13.6, s=1.15, z=0.0)
    return _prop(cv, [CROW, BEAK], relief=1.0, cavity=0.35, shadow=0.4)


def spr_well():
    """A village well: a round wall of fieldstones with a coping of flat stones, two oak posts
    carrying a little shingled roof, a windlass with its crank and the rope going down, and a
    bucket standing on the rim."""
    rng = np.random.default_rng(151)
    w, h = 56, 72
    cx = 28
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (cx - 17, cx + 17):                                                    # the posts
        cv.stroke([(x, h - 12), (x, 14)], 3.4, z=0.0, dome=0.8, mat=1)
    cv.stroke([(cx - 17, 30), (cx + 17, 30)], 2.6, z=0.3, dome=0.8, mat=1)          # the windlass
    cv.stroke([(cx + 17, 30), (cx + 22, 30), (cx + 22, 36)], 1.6, z=0.5, dome=0.6, mat=3)    # its crank
    cv.stroke([(cx + 2, 31), (cx + 2, h - 22)], 0.8, z=0.4, dome=0.3, mat=4)        # the rope
    cv.polygon([(cx - 25, 20), (cx, 4), (cx + 25, 20), (cx + 22, 22), (cx, 8), (cx - 22, 22)], z=1.2, top=0.8,
               bevel=1.5, mat=2)                                                    # the roof's bargeboards
    cv.polygon([(cx - 22, 20), (cx, 6), (cx + 22, 20)], z=0.9, top=0.6, bevel=2, mat=2, tone=-0.06)
    for k in range(4):                                                              # shingle courses
        y = 9 + k * 3.2
        cv.stroke([(cx - 4 - k * 4.8, y + 0.5), (cx + 4 + k * 4.8, y + 0.5)], 0.6, dome=0.3, mode='carve')
    _lathe(cv, cx, [(h - 22, 21), (h - 12, 22), (h - 1, 21.5)], z=0.8, dome=1.2, mat=0)    # the stone wall
    for row, y in enumerate(range(h - 21, h - 1, 5)):                               # its stones
        off = (row % 2) * 4
        for x in range(cx - 22 + off, cx + 22, 8):
            cv.stroke([(x, y), (x, y + 4)], 0.7, dome=0.3, mode='carve')
        cv.stroke([(cx - 21, y + 4.6), (cx + 21, y + 4.6)], 0.7, dome=0.3, mode='carve')
    _lathe(cv, cx, [(h - 25, 22.5), (h - 21, 23)], z=1.5, dome=1.0, mat=0, tone=0.06)    # the coping
    cv.ellipse(cx, h - 24.5, 19, 2.2, z=1.6, dome=0.0, mat=5)                         # the dark inside
    _lathe(cv, cx - 14, [(h - 33, 4.0), (h - 27, 3.4)], z=2.6, dome=1.2, mat=1, tone=0.05)   # a bucket on the rim
    cv.stroke([(cx - 18, h - 33), (cx - 14, h - 37), (cx - 10, h - 33)], 0.7, z=3.0, dome=0.3, mat=3)
    for _ in range(14):                                                             # moss in the joints
        x, y = cx + rng.uniform(-20, 20), rng.uniform(h - 20, h - 2)
        cv.ellipse(x, y, rng.uniform(0.8, 1.6), 0.8, z=2.2, dome=0.2, mat=6)
    return _prop(cv, [FIELDSTONE, OAK, SHINGLE, IRON, TWINE, ramp('#141210', dark=0.7, light=1.5), LEAF],
                 relief=1.0, cavity=0.45, shadow=0.45)


def spr_cart():
    """A hand cart: a bed of oak planks with low sides on a big spoked wheel, its shafts resting
    on the ground, loaded with sacks."""
    rng = np.random.default_rng(153)
    w, h = 80, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(4, h - 2), (26, 21)], 2.4, z=0.0, dome=0.8, mat=0, tone=-0.04)      # the shafts
    cv.stroke([(8, h - 1), (28, 23)], 2.4, z=0.1, dome=0.8, mat=0, tone=-0.08)
    cv.box(22, 18, 54, 10, z=0.3, top=1.0, bevel=1.5, mat=0)                        # the bed
    for x in range(26, 76, 7):
        cv.stroke([(x, 18.5), (x, 27.5)], 0.6, dome=0.3, mode='carve')
    cv.box(22, 11, 54, 3, z=0.4, top=0.8, bevel=1, mat=0, tone=0.04)                # the side rail
    for x in (24, 49, 74):
        cv.stroke([(x, 11), (x, 28)], 2.2, z=0.6, dome=0.7, mat=0, tone=-0.03)      # stakes
    for x, y in ((34, 12), (44, 10), (55, 12), (64, 11)):                           # sacks
        cv.ellipse(x, y, 7, 6, z=1.2, dome=1.2, rough=0.12, rng=rng, mat=2, tone=rng.normal(0, 0.04))
        cv.stroke([(x - 2, y - 5.5), (x + 2, y - 5.5)], 1.2, z=2.6, dome=0.4, mat=4)
    a = np.linspace(0, 2 * np.pi, 40)                                               # the wheel
    wx, wy, r = 50, h - 13, 12
    cv.stroke(list(zip(wx + np.cos(a) * r, wy + np.sin(a) * r)), 2.6, z=1.6, dome=0.7, mat=0, tone=-0.05)
    for k in range(8):
        b = k * np.pi / 4
        cv.stroke([(wx, wy), (wx + np.cos(b) * (r - 1), wy + np.sin(b) * (r - 1))], 1.3, z=1.5, dome=0.5, mat=0)
    cv.ellipse(wx, wy, 2.6, 2.6, z=2.2, dome=0.8, mat=3)                            # the hub
    cv.stroke(list(zip(wx + np.cos(a) * (r + 0.8), wy + np.sin(a) * (r + 0.8))), 0.8, z=2.0, dome=0.3, mat=3)
    return _prop(cv, [OAK, OAK, BURLAP, IRON, TWINE], relief=1.0, cavity=0.4, shadow=0.45)


def spr_market_stall():
    """A market stall: a trestle table under a striped awning on two poles with a scalloped
    valance, heaped with apples, cabbages and loaves, crates stacked underneath."""
    rng = np.random.default_rng(155)
    w, h = 88, 80
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (8, 80):                                                               # the poles
        cv.stroke([(x, h), (x, 12)], 2.6, z=0.0, dome=0.8, mat=0)
    for x0 in (14, 46):                                                             # crates under the table
        cv.box(x0, h - 16, 26, 15, z=0.2, top=0.8, bevel=1.2, mat=0, tone=-0.08)
        cv.stroke([(x0 + 1, h - 9), (x0 + 25, h - 9)], 0.6, dome=0.3, mode='carve')
    cv.box(6, 46, 76, 5, z=0.6, top=0.8, bevel=1.0, mat=0, tone=0.04)               # the table top
    for x in (10, 76):
        cv.stroke([(x, 51), (x + 4, h - 1)], 1.8, z=0.5, dome=0.6, mat=0)           # trestle legs
    for _ in range(46):                                                             # the goods
        x = rng.uniform(10, 78)
        kind = 0 if x < 34 else 1 if x < 56 else 2
        if kind == 0:
            cv.ellipse(x, rng.uniform(41, 45), 2.3, 2.1, z=1.2 + rng.random(), dome=1.0, mat=3)
        elif kind == 1:
            cv.ellipse(x, rng.uniform(40, 44), 3.6, 3.2, z=1.2 + rng.random(), dome=1.2, rough=0.2, rng=rng, mat=4)
        else:
            cv.ellipse(x, rng.uniform(41, 44), 4.2, 2.2, z=1.2 + rng.random(), dome=1.0, angle=rng.uniform(-20, 20),
                       mat=5)
    for k in range(8):                                                              # the awning, striped
        x0 = 4 + k * 10
        cv.polygon([(x0, 14), (x0 + 10, 14), (x0 + 10.5, 26), (x0 + 0.5, 26)], z=2.0, top=0.6, bevel=1.0,
                   mat=1 if k % 2 == 0 else 2)
        for j in range(2):                                                          # the valance, scalloped
            sx = x0 + 2.5 + j * 5
            cv.ellipse(sx, 27, 2.6, 2.6, z=2.0, dome=0.5, mat=1 if k % 2 == 0 else 2)
    cv.stroke([(4, 14), (84, 14)], 1.4, z=2.6, dome=0.4, mat=0)
    return _prop(cv, [OAK, CANVAS_RED, CANVAS_WHITE, APPLE, CABBAGE, BREAD], relief=1.0, cavity=0.4, shadow=0.45)


def spr_inn_sign():
    """An inn's sign: an iron bracket with a scroll under it, standing out from the wall at the
    left, and hanging from it on two rings a board painted deep red with a gilt border and a
    gilt crown. Stand it out from a front as a card (`planes` 1, square to the wall) so it reads
    from up and down the street."""
    w, h = 56, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(0, 4), (54, 4)], 2.4, z=0.0, dome=0.7, mat=2)                       # the bracket
    t = np.linspace(0, 1, 24)
    a = np.pi + t * 1.6 * np.pi
    cv.stroke(list(zip(10 + np.cos(a) * (9 - 6 * t), 14 + np.sin(a) * (9 - 6 * t))), 1.4, z=0.1, dome=0.5,
              mat=2)                                                                 # its scroll
    cv.stroke([(2, 23), (20, 5)], 1.6, z=0.1, dome=0.5, mat=2)
    for x in (24, 48):
        cv.stroke([(x, 5), (x, 11)], 1.0, z=0.4, dome=0.4, mat=2)                   # rings
    cv.box(18, 11, 36, 34, z=0.6, top=1.0, bevel=2.0, mat=1)                        # the board's gilt edge
    cv.box(21, 14, 30, 28, z=0.9, top=0.6, bevel=1.5, mat=0)                        # the red field
    cv.polygon([(26, 34), (26, 24), (29.5, 28), (32, 21), (36, 27), (40, 21), (42.5, 28), (46, 24), (46, 34)],
               z=1.6, top=0.6, bevel=1.0, mat=1)                                    # the crown
    cv.box(26, 34, 20, 3, z=1.6, top=0.5, bevel=0.8, mat=1, tone=-0.05)
    for x in (32, 36, 40):
        cv.ellipse(x, 21, 1.3, 1.3, z=2.0, dome=0.5, mat=1)
    return _prop(cv, [SIGN_RED, GILT, IRON], relief=1.0, cavity=0.4, shadow=0.45)


SPRITES = {'scarecrow': spr_scarecrow, 'pumpkin': spr_pumpkin, 'jack_o_lantern': spr_jack_o_lantern,
           'hay_bale': spr_hay_bale, 'crow': spr_crow, 'well': spr_well, 'cart': spr_cart,
           'market_stall': spr_market_stall, 'inn_sign': spr_inn_sign}
SPRITE_HEIGHT = {'scarecrow': 1.9, 'pumpkin': 0.32, 'jack_o_lantern': 0.34, 'hay_bale': 0.5, 'crow': 0.2,
                 'well': 1.7, 'cart': 0.75, 'market_stall': 1.9, 'inn_sign': 0.75}
PROP_DEFAULTS = {'jack_o_lantern': {'aura': {'color': [1.0, 0.62, 0.22], 'strength': 0.55, 'radius': 0.3}}}

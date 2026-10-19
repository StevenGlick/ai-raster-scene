"""The countryside, drawn with the pixel-art toolkit (scripts/pixelart.py): the things at the edge
of a field and along a village lane - a scarecrow, pumpkins, hay bales and the crows that are not
afraid of the scarecrow.

As in the other toolkit modules, every shape is stamped into a height field, lit from the upper
left and snapped onto hue-shifted ramps.
"""
import numpy as np

from biomes import _prop
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


SPRITES = {'scarecrow': spr_scarecrow, 'pumpkin': spr_pumpkin, 'jack_o_lantern': spr_jack_o_lantern,
           'hay_bale': spr_hay_bale, 'crow': spr_crow}
SPRITE_HEIGHT = {'scarecrow': 1.9, 'pumpkin': 0.32, 'jack_o_lantern': 0.34, 'hay_bale': 0.5, 'crow': 0.2}
PROP_DEFAULTS = {'jack_o_lantern': {'aura': {'color': [1.0, 0.62, 0.22], 'strength': 0.55, 'radius': 0.3}}}

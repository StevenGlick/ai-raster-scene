"""Up on the roofs of the neon city, drawn with the pixel-art toolkit (scripts/pixelart.py): a wooden
water tower on its steel legs, a rooftop air-conditioning unit, a giant sign on a scaffold lit in
glowing pseudo-letters, an elevated train on its beam to sling between the towers as a card,
and a black cat to sit on a ledge.

A roof is the top of a tall block: stand the camera on it with `height` (its `h` plus the eye's
0.5) and give roof props a `z` of the roof's height.
"""
import numpy as np

from biomes import _prop
from buildings import NEON, _glyph_mask
from pixelart import Canvas, outline_sprite, ramp

TANK_WOOD = ramp('#6a4a32', dark=0.32, light=1.35, warm=0.12)
STEEL = ramp('#5a6068', dark=0.4, light=1.45, cool=0.12)
RUSTED = ramp('#7a4a32', dark=0.35, light=1.35)
TARPAPER = ramp('#2e2c30', dark=0.5, light=1.7)
UNIT = ramp('#a8aca8', dark=0.4, light=1.2)
CONCRETE = ramp('#6a6a68', dark=0.35, light=1.35)
TRAIN = ramp('#c8ccd0', dark=0.38, light=1.18, cool=0.1)
STRIPE = ramp('#d83a5a', dark=0.4, light=1.3)
CAT = ramp('#1c1a22', dark=0.65, light=2.6, cool=0.25)


def spr_water_tower():
    """A wooden water tower on a roof: a barrel of vertical staves bound with iron hoops under a
    conical cap, on a frame of steel legs with cross bracing, a ladder up its side."""
    w, h = 72, 120
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x0, x1 in ((14, 10), (58, 62), (28, 26), (44, 46)):                                # legs
        cv.stroke([(x0, 66), (x1, h - 1)], 2.6, z=0.3, dome=0.6, mat=1)
    for y0, y1 in ((72, 100), (100, 72)):                                                  # bracing
        cv.stroke([(13, y0), (59, y1)], 1.2, z=0.5, dome=0.3, mat=1)
    cv.stroke([(12, 86), (60, 86)], 1.4, z=0.6, dome=0.3, mat=1)
    cv.box(8, 62, 56, 5, z=0.8, top=0.6, bevel=1.0, mat=1)                                 # the platform
    xs = np.arange(10, 62)                                                                 # the barrel
    for x in range(10, 62, 4):
        cv.box(x, 22, 4, 41, z=1.2 + 0.9 * np.sin(np.pi * (x - 8) / 56), top=0.5, bevel=0.8, mat=0,
               tone=0.04 * np.sin(x * 1.7))
    for y in (27, 37, 47, 57):                                                             # hoops
        cv.stroke([(9, y), (63, y)], 1.4, z=2.4, dome=0.4, mat=2)
    cv.polygon([(6, 23), (36, 4), (66, 23)], z=1.6, top=1.0, bevel=3.0, mat=0, tone=-0.05)  # the cap
    cv.ellipse(36, 4, 2.0, 2.0, z=2.2, dome=0.5, mat=1)
    for y in range(24, h - 2, 5):                                                          # ladder
        cv.stroke([(64, y), (68, y)], 0.8, z=2.6, dome=0.2, mat=1)
    for x in (64, 68):
        cv.stroke([(x, 24), (x, h - 1)], 0.9, z=2.6, dome=0.2, mat=1)
    del xs
    return _prop(cv, [TANK_WOOD, STEEL, RUSTED], relief=1.0, cavity=0.4, shadow=0.45)


def spr_ac_unit():
    """A rooftop air-conditioning unit: a pale steel box on rails, louvres down its side, a round
    fan grille on its face, a pipe running off it."""
    w, h = 56, 36
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(2, 32, 52, 4, z=0.2, top=0.4, bevel=0.8, mat=1)                                 # rails
    cv.box(4, 4, 48, 28, z=0.6, top=1.0, bevel=2.0, mat=0)                                 # the box
    for y in range(8, 30, 3):
        cv.stroke([(6, y), (20, y)], 0.8, z=0, dome=0.3, mode='carve')                     # louvres
    cv.ellipse(36, 18, 11, 11, z=1.0, dome=0.4, mat=1)                                     # the grille
    for k in range(-9, 10, 3):
        cv.stroke([(36 + k, 8), (36 + k, 28)], 0.6, z=1.4, dome=0.1, mat=2)
    cv.ellipse(36, 18, 2.6, 2.6, z=1.8, dome=0.5, mat=2)
    cv.stroke([(52, 26), (55, 26), (55, 35)], 2.0, z=0.8, dome=0.6, mat=2)                  # the pipe
    return _prop(cv, [UNIT, STEEL, ramp('#3a3c40', dark=0.5, light=1.6)], relief=1.0, cavity=0.4, shadow=0.4)


def spr_rooftop_sign():
    """A giant sign on a roof: three tall panels lettered top to bottom in glowing pseudo-letters,
    edged in neon tube, held up on a scaffold of steel lattice with a catwalk at its foot - the
    kind that lights a whole block from above."""
    rng = np.random.default_rng(601)
    w, h = 120, 160
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (8, 40, 72, 104):                                                             # the scaffold
        cv.stroke([(x, h - 1), (x, 70)], 2.0, z=0.4, dome=0.5, mat=0)
    for y in range(h - 1, 70, -18):
        for x0 in (8, 40, 72):
            cv.stroke([(x0, y), (x0 + 32, y - 18)], 0.9, z=0.5, dome=0.2, mat=0)
            cv.stroke([(x0, y - 18), (x0 + 32, y)], 0.9, z=0.5, dome=0.2, mat=0)
    cv.box(2, 128, 116, 4, z=0.8, top=0.5, bevel=1.0, mat=0)                               # the catwalk
    for x in range(4, 116, 6):
        cv.stroke([(x, 120), (x, 128)], 0.7, z=0.9, dome=0.2, mat=0)
    cv.stroke([(2, 120), (118, 120)], 0.9, z=0.9, dome=0.2, mat=0)
    panels = [(4, 4, 38, 110), (42, 14, 78, 118), (82, 2, 116, 108)]
    for x0, y0, x1, y1 in panels:
        cv.box(x0, y0, x1 - x0, y1 - y0, z=1.2, top=0.5, bevel=1.5, mat=1)
    rgba = cv.paint([STEEL, TARPAPER], cv.light(relief=1.0, cavity=0.3, shadow=0.3), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    for k, (x0, y0, x1, y1) in enumerate(panels):
        c = np.array(NEON[(k * 2) % len(NEON)], np.float32)
        x0, y0, x1, y1 = x0 + 2, y0 + 2, x1 - 2, y1 - 2
        edge = np.zeros((y1 - y0, x1 - x0), bool)
        edge[[0, -1], :] = True
        edge[:, [0, -1]] = True
        letters = np.zeros_like(edge)
        letters[3:-3, 3:-3] = _glyph_mask(y1 - y0 - 6, x1 - x0 - 6, rng, True)
        fat = letters | np.roll(letters, 1, 1)                                             # bold strokes
        sub = rgba[y0:y1, x0:x1]
        sub[..., :3] = np.where((edge | fat)[..., None], np.clip(c * 0.7 + 0.35, 0, 1), c * 0.1 + 0.03)
        em[y0:y1, x0:x1] = np.where(edge | fat, 1.0, 0.25)
    return rgba.astype(np.float32), em


def spr_sky_train():
    """An elevated train on its beam, for a card slung between towers (`planes` 1, a `length`, an
    `angle`): three cars in pale steel with a red stripe and every window lit, on a concrete beam
    held up on slim pillars that run down out of the bottom of the card. It repeats along its
    length; stand it on the street with its `scale` the height of the line."""
    w, h = 256, 160
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (40, 168):                                                                    # pillars
        cv.box(x - 5, 40, 10, h - 40, z=0.4, top=0.8, bevel=2.0, mat=3)
        cv.polygon([(x - 14, 40), (x + 14, 40), (x + 5, 52), (x - 5, 52)], z=0.6, top=0.8, bevel=1.5, mat=3)
    cv.box(-2, 32, w + 4, 9, z=0.8, top=0.8, bevel=1.5, mat=3)                             # the beam
    for x0 in (4, 88, 172):                                                                # the cars
        cv.box(x0, 8, 80, 24, z=1.4, top=1.2, bevel=3.0, mat=0)
        cv.box(x0, 24, 80, 3, z=2.0, top=0.3, bevel=0.6, mat=1)
    rgba = cv.paint([TRAIN, STRIPE, STEEL, CONCRETE], cv.light(relief=1.0, cavity=0.3, shadow=0.35), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    for x0 in (4, 88, 172):                                                                # lit windows
        for x in range(x0 + 6, x0 + 74, 9):
            rgba[12:20, x:x + 6, :3] = (1.0, 0.9, 0.65)
            em[12:20, x:x + 6] = 1.0
            rgba[12, x:x + 6, :3] = (0.75, 0.65, 0.45)
    return rgba.astype(np.float32), em


def spr_black_cat():
    """A black cat sitting with its back to you, looking out over the city: ears up, the curve of
    its back, its tail laid round its feet, one green eye catching the light as it turns its
    head. Small - set it on a ledge."""
    w, h = 32, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(5, 37), (8, 39), (20, 39), (27, 37), (29, 33)], 3.0, z=0.2, dome=0.8, taper=(0.8, 1.0), mat=0)  # tail
    cv.ellipse(15, 28, 10, 11, z=0.6, dome=2.0, mat=0)                                     # the body
    cv.ellipse(16, 13, 7.5, 6.5, z=1.6, dome=1.6, mat=0)                                   # the head
    cv.polygon([(9.5, 10), (10, 2), (14.5, 7.5)], z=2.0, top=0.8, bevel=1.0, mat=0)        # ears
    cv.polygon([(17.5, 7.5), (22, 2), (23, 10)], z=2.0, top=0.8, bevel=1.0, mat=0)
    rgba = cv.paint([CAT], cv.light(relief=1.2, cavity=0.3, shadow=0.3, sun=(0.5, -0.6, 0.6)), dither=0.3)
    rgba = outline_sprite(rgba, darken=0.6)
    em = np.zeros((h, w), np.float32)
    rgba[12:14, 22:24, :3] = (0.55, 1.0, 0.35)                                             # one eye
    em[12:14, 22:24] = 1.0
    for x, y in ((10, 3), (21, 3)):                                                        # ear tips catch
        rgba[y, x, :3] = rgba[y, x, :3] + 0.15                                             # the city's light
    return rgba.astype(np.float32), em


SPRITES = {'water_tower': spr_water_tower, 'ac_unit': spr_ac_unit, 'rooftop_sign': spr_rooftop_sign,
           'sky_train': spr_sky_train, 'black_cat': spr_black_cat}
SPRITE_HEIGHT = {'water_tower': 1.5, 'ac_unit': 0.32, 'rooftop_sign': 2.6, 'sky_train': 2.5, 'black_cat': 0.13}
PROP_DEFAULTS = {'sky_train': {'planes': 1, 'shadow': False},
                 'rooftop_sign': {'aura': {'color': [1.0, 0.35, 0.7], 'strength': 0.3, 'radius': 0.25}}}
NO_CONTACT_SHADOW = {'sky_train'}

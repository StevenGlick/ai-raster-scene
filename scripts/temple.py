"""Inside the jungle temple, drawn with the pixel-art toolkit (scripts/pixelart.py): a golden idol - a
squat jaguar crouched on a carved pedestal, jade in its eyes - and a spill of treasure, gold coins and a
jade mask among them, for the floor of a sanctum.

The temple's walls, pillars and altar are the jungle kit's stone (`temple_stone`, `glyphs`,
`temple_roots`) and `column` and `beam` objects of `stone`.
"""
import numpy as np

from biomes import _prop
from pixelart import Canvas, ramp

GOLD = ramp('#d8a838', dark=0.38, light=1.45, warm=0.12)
JADE = ramp('#3a9a6a', dark=0.4, light=1.4)
CARVED = ramp('#8a8a72', dark=0.35, light=1.3)


def spr_golden_idol():
    """A golden idol: a squat jaguar crouched on a carved stone pedestal, its head up, jade in its eyes
    and on its collar, worn bright where hands have touched it. It glints: give it a light, or a sunbeam."""
    w, h = 40, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(6, 34, 28, 22, z=0.6, top=0.9, bevel=1.4, mat=2)                        # the pedestal
    for y in (38, 46):
        cv.box(6, y, 28, 2, z=0.7, top=1.0, bevel=0.4, mat=2, tone=-0.12)         # its carved bands
    for x in (10, 18, 26):
        cv.box(x, 41, 4, 4, z=0.75, top=0.8, bevel=0.6, mat=2, tone=0.05)        # glyphs
    cv.box(4, 32, 32, 3, z=0.9, top=1.0, bevel=0.6, mat=2, tone=0.06)              # its top
    cv.ellipse(20, 26, 12, 7, z=1.2, dome=1.0, mat=0)                              # the crouched body
    cv.ellipse(12, 30, 4, 3, z=1.4, dome=0.9, mat=0)                               # forepaws
    cv.ellipse(28, 30, 4, 3, z=1.4, dome=0.9, mat=0)
    cv.ellipse(20, 14, 8, 7.5, z=1.6, dome=1.0, mat=0)                             # the head
    for x in (14, 26):
        cv.ellipse(x, 8, 2.4, 2.4, z=1.7, dome=0.8, mat=0)                         # ears
    cv.ellipse(20, 18, 4, 2.6, z=1.9, dome=0.8, mat=0, tone=0.05)                 # the muzzle
    for x in (16.5, 23.5):
        cv.ellipse(x, 13, 1.6, 1.2, z=2.0, dome=0.5, mat=1)                         # jade eyes
    cv.stroke([(12, 22), (20, 24), (28, 22)], 1.2, z=1.8, dome=0.5, mat=1)          # the jade collar
    cv.stroke([(32, 28), (36, 22), (35, 16)], 1.6, z=1.3, dome=0.8, mat=0)          # the tail curled up
    return _prop(cv, [GOLD, JADE, CARVED], relief=1.2, cavity=0.4, shadow=0.45,
                 em=np.zeros((h, w), np.float32))


def spr_treasure():
    """A spill of treasure on a temple floor: gold coins in heaps and scattered, a jade mask, a golden
    cup on its side."""
    rng = np.random.default_rng(211)
    w, h = 52, 20
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(70):                                                           # coins
        x = rng.normal(26, 10)
        top = h - 2 - max(0.0, 7 - abs(x - 22) * 0.5)
        if not (2 < x < w - 2):
            continue
        cv.ellipse(x, rng.uniform(top, h - 2), 1.8, 0.9, z=1.0 + rng.random() * 0.6, dome=0.4, mat=0,
                   tone=float(rng.normal(0, 0.06)))
    cv.ellipse(38, h - 7, 5, 4.2, z=1.4, dome=0.9, mat=1)                          # the jade mask
    for x in (36.5, 39.5):
        cv.ellipse(x, h - 8, 1.0, 0.7, z=1.8, dome=0.2, mat=1, tone=-0.35)
    cv.box(8, h - 7, 7, 4, z=1.2, top=0.9, bevel=1.0, mat=0, tone=0.05)              # the cup on its side
    cv.ellipse(8, h - 5, 1.8, 2.2, z=1.4, dome=0.6, mat=0, tone=-0.2)
    return _prop(cv, [GOLD, JADE], relief=1.0, cavity=0.4, shadow=0.45)


SPRITES = {'golden_idol': spr_golden_idol, 'treasure': spr_treasure}
SPRITE_HEIGHT = {'golden_idol': 0.38, 'treasure': 0.1}

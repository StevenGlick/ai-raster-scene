"""The north: a round shield of painted boards, to hang along a longship's sides or a hall's walls, drawn
with the pixel-art toolkit (scripts/pixelart.py). The longship itself is an object (`longship` in
objects.py).
"""
import numpy as np

from biomes import _prop
from pixelart import Canvas, ramp

BOARD_RED = ramp('#9a3426', dark=0.38, light=1.3)
BOARD_PALE = ramp('#c8b88a', dark=0.45, light=1.15)
IRON = ramp('#55545a', dark=0.45, light=1.7)
RIM = ramp('#5a4632', dark=0.35, light=1.4)


def spr_round_shield():
    """A round shield of boards, painted in quarters red and pale, an iron boss in the middle and a
    rawhide rim - seen face on. Stand it as a card (`planes` 1) along a ship's side or a wall."""
    w = h = 32
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(16, 16, 15.2, 15.2, z=0.6, dome=0.3, mat=3)                      # the rim
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.arctan2(yy - 16, xx - 16)
    quarter = ((a // (np.pi / 2)).astype(int)) % 2
    cv.ellipse(16, 16, 13.6, 13.6, z=0.8, dome=0.25, mat=0)                     # the board face
    face = cv.mat == 0
    cv.mat[face & (quarter == 1)] = 1
    for k in range(-12, 13, 4):                                                 # the boards' seams
        cv.stroke([(16 + k, 3), (16 + k, 29)], 0.5, dome=0.2, mode='carve')
    cv.ellipse(16, 16, 4.2, 4.2, z=1.6, dome=1.2, mat=2)                        # the boss
    return _prop(cv, [BOARD_RED, BOARD_PALE, IRON, RIM], relief=1.0, cavity=0.4, shadow=0.45)


SPRITES = {'round_shield': spr_round_shield}
SPRITE_HEIGHT = {'round_shield': 0.32}
PROP_DEFAULTS = {'round_shield': {'planes': 1}}
NO_CONTACT_SHADOW = {'round_shield'}

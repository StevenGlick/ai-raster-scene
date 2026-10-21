"""The glasshouse: a Victorian palm house's walls of glass between white cast-iron frames, and its floor of
encaustic tiles, drawn with the pixel-art toolkit (scripts/pixelart.py). The roof of glass is the
`gable_roof` object with `"cover": "glass"`; the columns and ribs are `column`s and `beam`s of
`iron_white`.
"""
import numpy as np

from biomes import T, _rng
from pixelart import Canvas, ramp

IRON_WHITE = ramp('#e2e0d6', dark=0.45, light=1.12)
TERRACOTTA = ramp('#a8583a', dark=0.4, light=1.3)
CREAM = ramp('#d8ccae', dark=0.45, light=1.12)
TILE_BLACK = ramp('#2e2a2c', dark=0.6, light=2.0)
TILE_BLUE = ramp('#3a5a7a', dark=0.45, light=1.4)


def tex_glasshouse(name):
    """A glasshouse wall: white cast-iron uprights and transoms, a kick panel of iron at the foot, and
    between them open panes (see-through) - stack it for every storey."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.box(0, 0, T, T, z=0.6, top=1.0, bevel=0, mat=0)
    rgb = cv.paint([IRON_WHITE], cv.light(relief=0.8), dither=0.25)
    alpha = np.ones((T, T), np.float32)
    for x0 in range(0, T, 16):                                   # four lights across, two down
        for y0 in (2, 33):
            alpha[y0 + 2:y0 + 29, x0 + 2:x0 + 14] = 0.0
    alpha[56:, :] = 1.0                                           # the kick panel along the foot
    rgb[56:] *= 0.86
    rgb[:2] *= 1.06
    noise = rng.random((T, T)) < 0.02                             # a fleck of rust here and there
    rgb[noise & (alpha > 0)] = (0.55, 0.36, 0.24)
    return np.clip(rgb, 0, 1), None, alpha


def tex_encaustic(name):
    """Encaustic tiles: a pattern of terracotta, cream, black and blue - an eight-pointed star in each
    square, borders of black between them."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    for j in range(4):
        for i in range(4):
            x0, y0 = i * 16, j * 16
            cv.box(x0, y0, 16, 16, z=0.3, top=1.0, bevel=0.6, mat=1, tone=float(rng.normal(0, 0.02)))
            cv.polygon([(x0 + 8, y0 + 1), (x0 + 15, y0 + 8), (x0 + 8, y0 + 15), (x0 + 1, y0 + 8)], z=0.4, top=1.0,
                       bevel=0.4, mat=0)
            cv.box(x0 + 5, y0 + 5, 6, 6, z=0.45, top=1.0, bevel=0.4, mat=3 if (i + j) % 2 else 2)
    for k in range(0, T + 1, 16):
        cv.stroke([(k, 0), (k, T)], 0.5, dome=0.2, mode='carve')
        cv.stroke([(0, k), (T, k)], 0.5, dome=0.2, mode='carve')
    rgb = cv.paint([TERRACOTTA, CREAM, TILE_BLACK, TILE_BLUE], cv.light(relief=0.6, cavity=0.3, shadow=0.2), dither=0.2)
    return np.clip(rgb, 0, 1), None


TEXTURES = {'glasshouse': tex_glasshouse, 'encaustic': tex_encaustic}
TEXTURE_NOISE = {'glasshouse': 0.2, 'encaustic': 0.4}
TEXTURE_REFLECT = {'encaustic': 0.12}

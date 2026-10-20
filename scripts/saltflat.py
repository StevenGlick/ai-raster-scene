"""The salt flat: a dry lake bed of salt cracked into plates, and - after rain - the same crust under a
film of water that mirrors the whole sky out to the horizon, so ground and sky become one.

`salt_flat` is the dry crust: pale plates, each a shade of its own, edged by the raised white rims the
salt pushes up as it dries. `salt_water` is that crust under a few centimetres of still water: darker,
the plates faint below - give it `reflect` 0.9 and `"reflections": {"ripple": 0, "smear": 0}` for a
mirror. `salt_brick` is blocks cut from the crust, for a salt house. The prop: `salt_mound`, a cone of
raked salt left to dry in rows.
"""
import numpy as np

from biomes import T, _prop, _rng
from pixelart import Canvas, ramp, smooth_noise

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16

CRUST = ramp(['#9d9aa2', '#b8b4b8', '#cfcbcb', '#e2dedb', '#efece8', '#fbfaf6'])
UNDER = ramp(['#4f5a66', '#5f6b77', '#707c87', '#828d97', '#98a2aa', '#b2bac0'])
BRICK = ramp(['#8e8578', '#a89e8e', '#c0b6a5', '#d4cbbb', '#e4dccd', '#f0eadf'])


def _dither(v, pal, amount=0.6):
    bay = np.tile(BAYER, (v.shape[0] // 4 + 1, v.shape[1] // 4 + 1))[:v.shape[0], :v.shape[1]]
    idx = np.clip(np.round(v * (len(pal) - 1) + (bay - 0.5) * amount), 0, len(pal) - 1).astype(int)
    return pal[idx].astype(np.float32)


def _plates(rng, n=10):
    """Tileable cells of a crust: for every texel the plate it belongs to and how near it is to the
    plate's edge (the gap between its nearest and second-nearest centre), wrapping at the tile edge."""
    pts = []
    while len(pts) < n:                                 # spread out, so no two plates crowd into a smear
        p = rng.uniform(0, T, 2)
        if all(np.hypot(*np.minimum(np.abs(p - q), T - np.abs(p - q))) > 13 for q in pts):
            pts.append(p)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    best = np.full((T, T), 1e9, np.float32)
    second = np.full((T, T), 1e9, np.float32)
    owner = np.zeros((T, T), int)
    for k, (py, px) in enumerate(pts):
        dy = np.abs(yy - py)
        dx = np.abs(xx - px)
        d = np.hypot(np.minimum(dy, T - dy), np.minimum(dx, T - dx))
        closer = d < best
        second = np.where(closer, best, np.minimum(second, d))
        owner = np.where(closer, k, owner)
        best = np.where(closer, d, best)
    return owner, second - best


def tex_salt_flat(name):
    """The dry crust: pale plates, each its own shade, edged by raised white rims."""
    rng = _rng(name)
    owner, gap = _plates(rng)
    tone = rng.uniform(-0.08, 0.08, owner.max() + 1)[owner]
    grain = smooth_noise(T, T, 16, rng) - 0.5
    rim = np.clip(1.6 - gap, 0, 1)                      # the ridge along each edge
    lee = np.clip(3.2 - gap, 0, 1) * (1 - rim)          # a faint shadow at its foot
    v = 0.62 + tone + 0.12 * grain - 0.16 * lee + 0.38 * rim
    return _dither(np.clip(v, 0, 1), CRUST, 0.55)


def tex_salt_water(name):
    """The crust under a film of still water: darker, the plates and their rims faint beneath it."""
    rng = _rng(name)
    owner, gap = _plates(rng)
    tone = rng.uniform(-0.06, 0.06, owner.max() + 1)[owner]
    rim = np.clip(1.6 - gap, 0, 1)
    v = 0.48 + tone + 0.06 * (smooth_noise(T, T, 8, rng) - 0.5) + 0.22 * rim
    return _dither(np.clip(v, 0, 1), UNDER, 0.45)


def tex_salt_brick(name):
    """Blocks cut from the salt crust and laid in courses: rough cream faces, the cut layers showing
    as faint bands, deep joints between."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    row = yy // 16
    shift = (row % 2) * 16
    col = (xx + shift) // 32
    block = row * 4 + col
    tone = rng.uniform(-0.07, 0.07, 64)[block % 64]
    bands = 0.05 * np.sin((yy + block * 3) * 1.3)
    rough = 0.12 * (smooth_noise(T, T, 12, rng) - 0.5)
    joint = (yy % 16 < 2) | ((xx + shift) % 32 < 2)
    edge = ((yy % 16 == 2) | ((xx + shift) % 32 == 2)) & ~joint
    v = 0.66 + tone + bands + rough + 0.1 * edge
    v = np.where(joint, 0.12, v)
    return _dither(np.clip(v, 0, 1), BRICK, 0.5)


def spr_salt_mound():
    """A cone of raked salt, its slopes ribbed where the rake dragged it up, left to dry in the sun."""
    w, h = 26, 16
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(1, 15.5), (11, 1.5), (15, 1.5), (25, 15.5)], z=1.0, top=0.6, bevel=7.0, mat=0)
    rng = np.random.default_rng(7)
    for k in range(6):                                  # rake marks running down the slopes
        x0 = 6 + k * 3 + rng.uniform(-0.5, 0.5)
        cv.stroke([(13 + (x0 - 13) * 0.25, 3), (x0, 15)], 0.5, z=0, dome=0.3, mode='carve')
    return _prop(cv, [ramp(['#8a8790', '#a9a6ad', '#c6c3c6', '#dedbd8', '#efede9', '#ffffff'])],
                 relief=1.2, cavity=0.25, shadow=0.35)


TEXTURES = {'salt_flat': lambda n: (tex_salt_flat(n), None), 'salt_water': lambda n: (tex_salt_water(n), None),
            'salt_brick': lambda n: (tex_salt_brick(n), None)}
TEXTURE_NOISE = {'salt_flat': 0.3, 'salt_water': 0.2, 'salt_brick': 0.6}
SPRITES = {'salt_mound': spr_salt_mound}
SPRITE_HEIGHT = {'salt_mound': 0.32}
PROP_DEFAULTS = {}
NO_CONTACT_SHADOW = set()

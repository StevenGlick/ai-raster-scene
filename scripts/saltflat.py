"""The salt flat: a dry lake bed of salt cracked into plates, and - after rain - the same crust under a
film of water that mirrors the whole sky out to the horizon, so ground and sky become one.

`salt_flat` is the dry crust: pale plates, each a shade of its own, edged by the raised white rims the
salt pushes up as it dries. `salt_water` is that crust under a few centimetres of still water: darker,
the plates faint below - give it `reflect` 0.9 and `"reflections": {"ripple": 0, "smear": 0}` for a
mirror. `salt_brick` is blocks cut from the crust, for a salt house. The props are salt raked up to
dry, in four sizes, all round-topped and damp at the foot: `salt_mound` (the raked mound, set out in
rows), `salt_heap` (two slumped together, long and low), `salt_pile` (a small rough shovelful) and
`salt_clods` (a few lumps left lying).
"""
import numpy as np

from biomes import T, _rng
from pixelart import Canvas, outline_sprite, ramp, smooth_noise

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


SALT = ramp(['#8a91a0', '#a6adba', '#c0c5ce', '#d7dadf', '#e9eaea', '#f6f6f3', '#ffffff'])
WET = np.array([0.78, 0.83, 0.9], np.float32)           # brine darkening the foot of a pile


def _heap(cv, cx, base, R, H, p=2.0, q=0.6, rough=0.0, rng=None):
    """A rounded heap seen from the side: its outline rises as H * (1 - |u|^p)^q across a half-width R
    (p above 2 is broad-shouldered, below 1.5 peaked; q under 1 rounds the top), and its relief is that
    of a solid of revolution, so it shades like a heap and not a flat cut-out. `rough` lumps the outline."""
    ys = np.arange(int(np.floor(base - H - 2)), int(np.ceil(base)) + 1)
    xs = np.arange(int(np.floor(cx - R - 2)), int(np.ceil(cx + R)) + 2)
    X, Y = np.meshgrid(xs + 0.5, ys + 0.5)
    u = (X - cx) / R
    top = H * np.clip(1 - np.abs(u) ** p, 0, 1) ** q
    if rough:
        a = rng.uniform(0, 2 * np.pi, 3)
        top = top * (1 + rough * (0.5 * np.sin(u * 7 + a[0]) + 0.3 * np.sin(u * 13 + a[1]) + 0.2 * np.sin(u * 23 + a[2])))
    v = base - Y                                                # height above the foot, in pixels
    mask = (v >= 0) & (v < top)
    r = R * np.clip(1 - (np.clip(v, 0, H) / H) ** (1 / q), 0, 1) ** (1 / p)    # its radius at that height
    cv.put(ys, xs, mask, np.sqrt(np.clip(r * r - (X - cx) ** 2, 0, None)), mode='max')


def _lumps(cv, rng, n, x0, x1, y0, y1, rx=(1.0, 2.0), ry=(0.8, 1.5), dome=0.6):
    """Lumps of salt raised on the slopes of what is drawn."""
    for _ in range(n):
        cv.ellipse(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(*rx), rng.uniform(*ry), dome=dome,
                   mode='add')


def _salt(cv, rng, wet, seed):
    """Light the salt from the upper left - white where the sun is on it, a pale grey-blue in its shade
    (salt is never dark) - edge it softly so it stands off a crust as white as itself, then darken the
    foot of each column a ragged little way up, where the brine has wicked in."""
    cv.noise(0.8, cells=6, rng=rng)
    light = cv.light(sun=(-0.75, -0.6, 0.55), ambient=0.4, diffuse=0.68, relief=1.6, cavity=0.4, shadow=0.25)
    rgba = outline_sprite(cv.paint([SALT], light, dither=0.3, outline=0).astype(np.float32), darken=0.8)
    h, w = rgba.shape[:2]
    n = smooth_noise(w, 1, 9, np.random.default_rng(seed), False)[0]
    line = wet[0] + (wet[1] - wet[0]) * (n - n.min()) / max(n.max() - n.min(), 1e-6)
    rows = np.arange(h, dtype=np.float32)
    for c in range(w):
        solid = np.nonzero(rgba[:, c, 3] > 0)[0]
        if len(solid):
            k = np.clip((rows - (solid.max() - line[c])) / max(line[c], 0.5), 0, 1) ** 0.7 * (rgba[:, c, 3] > 0)
            rgba[:, c, :3] *= 1 - k[:, None] * (1 - WET)
    return rgba, np.zeros((h, w), np.float32)


def spr_salt_mound():
    """A mound of salt raked up out of the brine to dry: round-topped, lumpy, damp at its foot."""
    rng = np.random.default_rng(11)
    cv = Canvas(30, 19, wrap=False, ground=-9)
    _heap(cv, 15.0, 18.6, 14.0, 16.0, p=2.1, q=0.62, rough=0.05, rng=rng)
    _lumps(cv, rng, 9, 5, 25, 6, 17, (1.2, 2.2), (0.9, 1.6))
    return _salt(cv, rng, (1.5, 3.0), 3)


def spr_salt_heap():
    """A long low heap of salt, two mounds slumped together, the smaller leaning on the larger."""
    rng = np.random.default_rng(12)
    cv = Canvas(38, 14, wrap=False, ground=-9)
    _heap(cv, 14.0, 13.6, 13.0, 11.0, p=2.3, q=0.6, rough=0.06, rng=rng)
    _heap(cv, 26.0, 13.6, 10.5, 7.6, p=2.4, q=0.6, rough=0.08, rng=rng)
    _lumps(cv, rng, 8, 4, 34, 6, 13, dome=0.5)
    return _salt(cv, rng, (1.2, 2.4), 4)


def spr_salt_pile():
    """A small rough pile of salt, a shovelful tipped out: rounded, chunky, a clod rolled off its side."""
    rng = np.random.default_rng(13)
    cv = Canvas(22, 12, wrap=False, ground=-9)
    _heap(cv, 10.0, 11.6, 9.0, 9.4, p=2.1, q=0.6, rough=0.14, rng=rng)
    _lumps(cv, rng, 6, 3, 17, 4, 11, (1.0, 1.8), (0.9, 1.4), dome=0.7)
    cv.ellipse(18.6, 10.4, 2.0, 1.5, mode='max')                 # the clod
    return _salt(cv, rng, (1.0, 2.0), 5)


def spr_salt_clods():
    """A few clods of salt left lying where a mound was raked up: rounded lumps of different sizes."""
    rng = np.random.default_rng(14)
    cv = Canvas(28, 9, wrap=False, ground=-9)
    for x, rx, ry in ((5.0, 3.6, 3.4), (12.0, 2.2, 2.0), (17.5, 3.0, 2.8), (23.6, 1.7, 1.6)):
        cv.ellipse(x, 8.8 - ry * 0.9, rx, ry, dome=1.2, rough=0.12, rng=rng, mode='max')
    return _salt(cv, rng, (0.8, 1.6), 6)


TEXTURES = {'salt_flat': lambda n: (tex_salt_flat(n), None), 'salt_water': lambda n: (tex_salt_water(n), None),
            'salt_brick': lambda n: (tex_salt_brick(n), None)}
TEXTURE_NOISE = {'salt_flat': 0.3, 'salt_water': 0.2, 'salt_brick': 0.6}
SPRITES = {'salt_mound': spr_salt_mound, 'salt_heap': spr_salt_heap, 'salt_pile': spr_salt_pile,
           'salt_clods': spr_salt_clods}
SPRITE_HEIGHT = {'salt_mound': 0.22, 'salt_heap': 0.15, 'salt_pile': 0.12, 'salt_clods': 0.08}
PROP_DEFAULTS = {}
NO_CONTACT_SHADOW = set()

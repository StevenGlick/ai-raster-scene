"""Sky islands: meadows adrift in the sky over a sea of cloud, waterfalls pouring off their edges and
turning to mist on the way down, roots trailing from their undersides, plank bridges between them.

Textures: `meadow` (grass sprinkled with tiny flowers, for an island's top) and `island_rock` (rock in
layers with roots running through it, for the `side` of an island: give the cell a deep `cliff` and the
rock drops away under it). Cards (`planes` 1 - lay them along an edge with `angle` and `length`):
`waterfall` (a sheet of falling water, white at its lip and turning to mist toward its foot: hang it
off an edge with `z` at minus its `scale`), `island_roots` (roots and vines dangling under an edge:
`z` about -2) and `rope_rail` (posts and two sagging ropes, along the sides of a bridge). And a
billboard, `island_keel`: rock tapering to a ragged point, to hang under an island from the foot of its
cliff so it reads as a floating mountain from every side.
"""
import numpy as np

from biomes import T, _prop, _rng
from pixelart import Canvas, ramp, smooth_noise

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16
GRASS = ramp(['#24461f', '#2f5a26', '#3d722d', '#4f8a35', '#66a343', '#86bc58'])
ROCK = ramp(['#4a4450', '#605862', '#786e70', '#908480', '#a89c94', '#c2b6aa'])
WATER = ramp(['#4f7896', '#6f98b6', '#94b8d2', '#bcd6e8', '#e2eff7', '#ffffff'])
ROOT = ramp(['#2e2016', '#45301f', '#5e432b', '#7a5a3b'])


def _dither(v, pal, amount=0.6):
    bay = np.tile(BAYER, (v.shape[0] // 4 + 1, v.shape[1] // 4 + 1))[:v.shape[0], :v.shape[1]]
    idx = np.clip(np.round(v * (len(pal) - 1) + (bay - 0.5) * amount), 0, len(pal) - 1).astype(int)
    return pal[idx].astype(np.float32)


def tex_meadow(name):
    """A meadow: grass in tufts with the light on their tips, and tiny flowers - white, yellow, pink."""
    rng = _rng(name)
    v = 0.45 + 0.25 * (smooth_noise(T, T, 6, rng) - 0.5) + 0.2 * (smooth_noise(T, T, 20, rng) - 0.5)
    blades = rng.random((T, T)) < 0.18
    v = np.where(blades, v + 0.22, v)
    v = np.where(np.roll(blades, 1, 0) & ~blades, v - 0.15, v)    # a shadow under each tip
    rgb = _dither(np.clip(v, 0, 1), GRASS, 0.6)
    for colour, n in (([0.96, 0.95, 0.88], 14), ([1.0, 0.86, 0.3], 10), ([0.95, 0.55, 0.7], 8), ([0.7, 0.62, 0.95], 5)):
        for _ in range(n):
            y, x = rng.integers(0, T, 2)
            rgb[y, x] = colour
            rgb[(y + 1) % T, x] = rgb[(y + 1) % T, x] * 0.6                  # its stem's shade under it
    return rgb


def tex_island_rock(name):
    """The underside of a sky island: rock laid down in bands of grey and brown, cracked, with roots
    working down through it."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    wave = 3.0 * np.sin(xx * 2 * np.pi / T + rng.uniform(0, 6)) + 2.0 * np.sin(xx * 4 * np.pi / T)
    band = ((yy + wave) / 9.0).astype(int)
    tone = rng.uniform(-0.18, 0.18, 32)[band % 32]
    v = 0.5 + tone + 0.18 * (smooth_noise(T, T, 10, rng) - 0.5)
    seam = ((yy + wave) % 9.0) < 1.0
    v = np.where(seam, v - 0.28, v)
    rgb = _dither(np.clip(v, 0, 1), ROCK, 0.6)
    for _ in range(5):                                   # roots threading down through it
        x = float(rng.integers(0, T))
        y0 = int(rng.integers(0, T))
        for k in range(int(rng.integers(10, 28))):
            x += rng.uniform(-0.7, 0.7)
            yi, xi = (y0 + k) % T, int(round(x)) % T
            rgb[yi, xi] = ROOT[2]
            rgb[yi, (xi + 1) % T] = ROOT[0]
    return rgb


def spr_waterfall():
    """A sheet of falling water: a white lip where it pours over, streaks running down, and toward the
    foot it breaks into mist and fades away. Uniform across, so a card of any `length` is seamless."""
    w, h = 32, 128
    rng = np.random.default_rng(31)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = yy / (h - 1)
    streak = smooth_noise(w, h, 8, rng, cells_y=3) * 0.6 + smooth_noise(w, h, 16, rng, cells_y=5) * 0.4
    v = 0.45 + 0.5 * (streak - 0.5) + 0.25 * t                  # paler as it breaks up
    v = np.where(yy < 3, 0.98, v)                                 # the lip
    rgb = _dither(np.clip(v, 0, 1), WATER, 0.7)
    mist = np.clip((t - 0.55) / 0.45, 0, 1)
    rgb = rgb * (1 - mist[..., None] * 0.6) + np.array([0.94, 0.97, 1.0], np.float32) * mist[..., None] * 0.6
    a = np.clip(0.92 - 0.25 * (streak < 0.35) * t, 0, 1) * (1 - mist ** 1.3)
    rgba = np.concatenate([rgb, a[..., None]], -1).astype(np.float32)
    return rgba, np.zeros((h, w), np.float32)


def spr_island_roots():
    """Roots and vines hanging from under an island's edge, long and short, a few with leaves."""
    w, h = 64, 48
    rng = np.random.default_rng(5)
    rgba = np.zeros((h, w, 4), np.float32)
    leaf = np.array([0.27, 0.48, 0.2], np.float32)
    for k in range(13):
        x = (k + rng.uniform(0.1, 0.9)) * w / 13
        n = int(rng.integers(12, h))
        vine = rng.random() < 0.35
        for y in range(n):
            x += rng.uniform(-0.45, 0.45)
            xi = int(round(x)) % w
            col = ROOT[1 + (y < n * 0.6)] if not vine else np.array([0.2, 0.36, 0.16], np.float32)
            rgba[y, xi] = list(col) + [1.0]
            if y < n * 0.4 and not vine:                           # thicker near the top
                rgba[y, (xi + 1) % w] = list(ROOT[0]) + [1.0]
            if vine and y % 4 == 2:
                rgba[y, (xi + (1 if (y // 4) % 2 else -1)) % w] = list(leaf) + [1.0]
    return rgba, np.zeros((h, w), np.float32)


def spr_island_keel():
    """The underside of a sky island: rock tapering to a ragged point, banded, roots trailing from it,
    lit from above. A billboard: hang it under an island (top at the foot of its cliff) and it looks
    solid from every side."""
    w, h = 72, 64
    rng = np.random.default_rng(23)
    cv = Canvas(w, h, wrap=False, ground=-9)
    pts = [(0.5, 0.5)]
    for k in range(1, 12):                                    # the ragged left flank down to the point
        t = k / 12
        pts.append((0.5 + 31 * t + rng.uniform(-2.5, 2.5), 0.5 + 58 * t ** 1.3 + rng.uniform(-1.5, 1.5)))
    pts.append((36, 63))
    for k in range(11, 0, -1):                                # and back up the right flank
        t = k / 12
        pts.append((71.5 - 31 * t + rng.uniform(-2.5, 2.5), 0.5 + 58 * t ** 1.3 + rng.uniform(-1.5, 1.5)))
    pts.append((71.5, 0.5))
    cv.polygon(pts, z=2.0, top=0.5, bevel=9.0, mat=0)
    for k in range(9):                                        # crags standing out of it
        cx, cy = rng.uniform(12, 60), rng.uniform(4, 34)
        cv.ellipse(cx, cy, rng.uniform(3, 6), rng.uniform(2, 4), z=2.6, dome=0.8, mat=0)
    rgba, em = _prop(cv, [ROCK], relief=1.3, cavity=0.35, shadow=0.45, outline=False)
    rgba[..., :3] *= 0.62 * (1 - 0.42 * (np.arange(h) / h) ** 1.2)[:, None, None]   # in its own shade, as the cliff is
    yy = np.arange(h)[:, None]
    bands = (np.sin(yy * 0.9 + np.sin(np.arange(w)[None, :] * 0.15) * 2.0) > 0.85) & (rgba[..., 3] > 0.5)
    rgba[..., :3] = np.where(bands[..., None], rgba[..., :3] * 0.78, rgba[..., :3])
    for k in range(10):                                       # roots trailing from its flanks
        x = rng.uniform(6, 66)
        top = int(np.argmax(rgba[:, int(x), 3] > 0.5)) if (rgba[:, int(x), 3] > 0.5).any() else 0
        bottom = int(h - 1 - np.argmax(rgba[::-1, int(x), 3] > 0.5))
        for y in range(bottom, min(h, bottom + int(rng.integers(4, 12)))):
            x += rng.uniform(-0.4, 0.4)
            rgba[y, int(x) % w] = list(ROOT[1]) + [1.0]
    return rgba, em


def spr_rope_rail():
    """A bridge's railing: a post at every unit and two ropes sagging between them."""
    w, h = 32, 14
    rgba = np.zeros((h, w, 4), np.float32)
    wood = np.array([0.36, 0.25, 0.15], np.float32)
    rope = np.array([0.62, 0.5, 0.33], np.float32)
    rgba[:, 0:2] = list(wood) + [1.0]
    rgba[:, 1] = list(wood * 0.7) + [1.0]
    for x in range(2, w):
        sag = np.sin(np.pi * (x - 1) / (w - 1))
        for y0 in (1.5, 7.0):
            y = int(round(y0 + 2.2 * sag))
            rgba[y, x] = list(rope) + [1.0]
            if y + 1 < h:
                rgba[y + 1, x] = list(rope * 0.6) + [1.0]
    return rgba, np.zeros((h, w), np.float32)


TEXTURES = {'meadow': lambda n: (tex_meadow(n), None), 'island_rock': lambda n: (tex_island_rock(n), None)}
TEXTURE_NOISE = {'meadow': 0.6, 'island_rock': 0.7}
SPRITES = {'waterfall': spr_waterfall, 'island_roots': spr_island_roots, 'island_keel': spr_island_keel,
           'rope_rail': spr_rope_rail}
SPRITE_HEIGHT = {'waterfall': 6.0, 'island_roots': 2.0, 'island_keel': 6.0, 'rope_rail': 0.42}
PROP_DEFAULTS = {'waterfall': {'planes': 1, 'shadow': False}, 'island_keel': {'shadow': False},
                 'island_roots': {'planes': 1, 'shadow': False},
                 'rope_rail': {'planes': 1, 'shadow': False}}
NO_CONTACT_SHADOW = {'waterfall', 'island_roots', 'island_keel', 'rope_rail'}

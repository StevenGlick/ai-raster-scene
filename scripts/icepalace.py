"""The ice palace: a palace of ice on a frozen lake, under the aurora.

The `aurora` sky (drawn here for assets.make_sky): a clear night with curtains of green light hanging
across it, bright along their lower hems, rayed upward and fading through violet into the dark; they
glow, so a light bloom takes them up and a frozen lake doubles them. Textures: `ice_block` (blocks of
blue ice with frosted faces and bright edges), `frost_wall` (ice covered in fern-like frost),
`ice_floor` (polished ice over dark water, cracked; it reflects). Props: `ice_spire` (a tower's
crystal spire: stand it on a tower top with `z`), `ice_throne` (a throne cut from the ice), `icicles`
(a card of icicles to hang under eaves, `z` at the eave less its height), `ice_shards` (crystals of ice
breaking through the snow).
"""
import math

import numpy as np

from biomes import T, _prop, _rng
from pixelart import Canvas, ramp, smooth_noise

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16
ICE = ramp(['#1d3550', '#2c5476', '#46789c', '#6c9cbc', '#9cc2da', '#d2e8f4', '#f6fcff'])


def _dither(v, pal, amount=0.6):
    bay = np.tile(BAYER, (v.shape[0] // 4 + 1, v.shape[1] // 4 + 1))[:v.shape[0], :v.shape[1]]
    idx = np.clip(np.round(v * (len(pal) - 1) + (bay - 0.5) * amount), 0, len(pal) - 1).astype(int)
    return pal[idx].astype(np.float32)


def draw_aurora(sky, rng, hrow, proj):
    """Paint curtains of the aurora into a sky panorama (h x w x 3, horizon at row `hrow`), seamless
    round 360 degrees: three curtains, each a wavering hem of bright green with rays climbing from it,
    fading through violet into the dark."""
    h, w = sky.shape[:2]
    x = np.arange(w, dtype=np.float32) / w * 2 * math.pi          # angle round the panorama
    rows = np.arange(h, dtype=np.float32)[:, None]
    light = np.zeros((h, w, 3), np.float32)
    # each curtain's brightest arc is set over an azimuth: the strongest due north (270), so a view
    # toward the north always has the aurora over it
    for k, (el, amp, height, power, peak, n1) in enumerate(((14, 5, 22, 1.0, 270, 2), (24, 7, 26, 0.75, 305, 3),
                                                             (34, 6, 18, 0.5, 235, 2))):
        p = rng.uniform(0, 2 * math.pi, 4)
        p[2] = math.pi / 2 - n1 * math.radians(peak)
        n2 = int(rng.integers(5, 8))
        el_x = el + amp * np.sin(n1 * x + p[0]) + 0.4 * amp * np.sin(n2 * x + p[1])     # the hem's elevation
        hem = hrow - proj * np.tan(np.radians(el_x))                                  # its panorama row
        tall = proj * (np.tan(np.radians(el_x + height)) - np.tan(np.radians(el_x)))    # how high its rays go
        # patchy: arcs here and there with the dark between them, not a wall of light all round
        strength = power * np.clip(0.1 + 1.0 * np.sin(n1 * x + p[2]) + 0.35 * np.sin(5 * x + p[1]), 0, 1) ** 1.3
        rays = 0.55 + 0.45 * np.sin(x * (60 + 20 * k) + 3 * np.sin(x * 7 + p[3]))     # vertical streaks
        up = (hem[None, :] - rows) / np.maximum(tall[None, :], 1.0)                   # 0 at the hem, 1 at the top
        below = (rows - hem[None, :]) / 3.0
        body = np.where(up >= 0, np.exp(-3.2 * up) * (up <= 1.4), np.exp(-below * below))
        a = body * (strength * rays)[None, :]
        green = np.array([0.35, 1.0, 0.55], np.float32)
        violet = np.array([0.55, 0.3, 0.85], np.float32)
        mix = np.clip(up, 0, 1)[..., None]
        light += a[..., None] * (green * (1 - mix) + violet * mix)
    return sky + light * 1.25


def tex_ice_block(name):
    """Big blocks of blue ice: frosted faces paler at their edges, deep blue in the joints, a crack
    or two, a gleam."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    row = yy // 32
    shift = (row % 2) * 24
    col = (xx + shift) // 48
    tone = rng.uniform(-0.08, 0.08, 16)[(row * 3 + col) % 16]
    lx = ((xx + shift) % 48).astype(np.float32)
    ly = (yy % 32).astype(np.float32)
    edge = np.minimum(np.minimum(lx, 47 - lx), np.minimum(ly, 31 - ly))
    v = 0.5 + tone + 0.18 * (smooth_noise(T, T, 8, rng) - 0.5) + 0.25 * np.exp(-edge / 2.5)
    joint = edge < 1.0
    v = np.where(joint, 0.08, v)
    crack = np.zeros((T, T), bool)
    for _ in range(3):
        x, y = rng.uniform(0, T, 2)
        a = rng.uniform(0, math.pi)
        for t in range(22):
            x += math.cos(a) + rng.uniform(-0.4, 0.4)
            y += math.sin(a) + rng.uniform(-0.4, 0.4)
            crack[int(y) % T, int(x) % T] = True
    v = np.where(crack & ~joint, v + 0.28, v)
    return _dither(np.clip(v, 0, 1), ICE, 0.6)


def tex_frost_wall(name):
    """A wall of ice grown over with frost: feathery fern-like crystals branching across it."""
    rng = _rng(name)
    v = 0.35 + 0.15 * (smooth_noise(T, T, 6, rng) - 0.5)
    m = np.zeros((T, T), np.float32)
    for _ in range(7):
        x, y = rng.uniform(0, T, 2)
        a = rng.uniform(0, 2 * math.pi)
        for t in range(30):
            x += math.cos(a) * 1.1
            y += math.sin(a) * 1.1
            m[int(y) % T, int(x) % T] = 1.0
            if t % 3 == 0:                                     # feathers off the stem, both sides
                for side in (1, -1):
                    b = a + side * 0.9
                    for s in range(1, 5 - t // 10):
                        m[int(y + math.sin(b) * s) % T, int(x + math.cos(b) * s) % T] = 0.8
            a += rng.uniform(-0.12, 0.12)
    v = v + 0.5 * m
    return _dither(np.clip(v, 0, 1), ICE, 0.5)


def tex_ice_floor(name):
    """Polished ice over dark water: deep blue-black, white cracks running through it, bubbles."""
    rng = _rng(name)
    v = 0.18 + 0.12 * (smooth_noise(T, T, 5, rng) - 0.5)
    for _ in range(4):
        x, y = rng.uniform(0, T, 2)
        a = rng.uniform(0, math.pi)
        for t in range(40):
            x += math.cos(a)
            y += math.sin(a)
            a += rng.uniform(-0.3, 0.3)
            v[int(y) % T, int(x) % T] = 0.75
    bubbles = rng.random((T, T)) < 0.01
    v = np.where(bubbles, 0.6, v)
    return _dither(np.clip(v, 0, 1), ICE, 0.5)


def spr_ice_spire():
    """A tower's spire of ice: a tall faceted crystal, pale at its lit edge, blue in its shade."""
    w, h = 18, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(1.5, 63.5), (9, 0.5), (16.5, 63.5)], z=2.0, top=0.4, bevel=3.0, mat=0)
    cv.polygon([(6, 63.5), (9, 18), (12, 63.5)], z=2.6, top=0.5, bevel=1.5, mat=0)
    return _prop(cv, [ICE], relief=1.4, cavity=0.3, shadow=0.35)


def spr_ice_throne():
    """A throne cut from a block of ice: a high pointed back, arms, a step."""
    w, h = 30, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(5, 39), (5, 12), (15, 1), (25, 12), (25, 39)], z=1.5, top=0.8, bevel=2.5, mat=0)
    cv.box(2, 24, 6, 15, z=2.0, top=1.0, bevel=1.5, mat=0)
    cv.box(22, 24, 6, 15, z=2.0, top=1.0, bevel=1.5, mat=0)
    cv.box(6, 27, 18, 6, z=2.4, top=1.0, bevel=1.5, mat=0)
    cv.box(1, 35, 28, 4.5, z=1.0, top=1.0, bevel=1.0, mat=0)
    return _prop(cv, [ICE], relief=1.2, cavity=0.35, shadow=0.35)


def spr_icicles():
    """A row of icicles hanging from an eave, long and short. A card: hang it under a ledge."""
    w, h = 32, 20
    rng = np.random.default_rng(3)
    rgba = np.zeros((h, w, 4), np.float32)
    for x in range(0, w, 2):
        n = int(rng.integers(4, h))
        for y in range(n):
            wide = 1 if y < n * 0.5 else 0
            c = ICE[5] if (x % 4 == 0) else ICE[4]
            rgba[y, x] = list(c) + [1.0]
            if wide and x + 1 < w:
                rgba[y, x + 1] = list(ICE[3]) + [1.0]
    rgba[0, :] = list(ICE[6]) + [1.0]
    return rgba, np.zeros((h, w), np.float32)


def spr_ice_shards():
    """Shards of ice breaking up through the snow, leaning every way."""
    w, h = 28, 22
    rng = np.random.default_rng(9)
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(6):
        x = 3 + k * 4.2 + rng.uniform(-1, 1)
        top = rng.uniform(1, 12)
        lean = rng.uniform(-3, 3)
        cv.polygon([(x - 2.2, 21.5), (x + lean, top), (x + 2.2, 21.5)], z=1.5 + k * 0.1, top=0.4, bevel=1.6, mat=0)
    return _prop(cv, [ICE], relief=1.3, cavity=0.3, shadow=0.35)


TEXTURES = {'ice_block': lambda n: (tex_ice_block(n), None), 'frost_wall': lambda n: (tex_frost_wall(n), None),
            'ice_floor': lambda n: (tex_ice_floor(n), None)}
TEXTURE_NOISE = {'ice_block': 0.4, 'frost_wall': 0.3, 'ice_floor': 0.2}
TEXTURE_REFLECT = {'ice_floor': 0.6}
SPRITES = {'ice_spire': spr_ice_spire, 'ice_throne': spr_ice_throne, 'icicles': spr_icicles, 'ice_shards': spr_ice_shards}
SPRITE_HEIGHT = {'ice_spire': 2.4, 'ice_throne': 1.1, 'icicles': 0.4, 'ice_shards': 0.5}
PROP_DEFAULTS = {'icicles': {'planes': 1, 'shadow': False}}
NO_CONTACT_SHADOW = {'icicles', 'ice_spire'}

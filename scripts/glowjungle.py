"""The glowing jungle: the rainforest at night with light inside its plants - leaves edged and ribbed in
cold light, flowers burning pink, pods glowing on their stalks, moss and fungus aglow on the floor and
plankton swirling in the pools.

Props, each the jungle's own plant at night (its colours sunk to deep blue-green, its brightest parts
glowing, a scatter of glowing specks over it): `glow_monstera`, `glow_fern`, `glow_tree_fern`,
`glow_heliconia` (pink), `glow_bromeliad` (violet), `glow_liana` (hanging); and `glow_pods`, a curling
stalk hung with glowing seed pods. The fringe `glow_jungle` is the jungle's wall of plants at night.
Textures: `glow_leaves` (a wall of rainforest at night, specked with light), `lumen_floor` (dark leaf
litter with glowing moss and fungus) and `glow_water` (black water with plankton glowing in swirls;
it reflects). They all glow: pair them with coloured lights and a light bloom.
"""
import numpy as np

import biomes
from biomes import T, _prop, _rng
from pixelart import Canvas, ramp, smooth_noise

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16
NIGHT = np.array([0.05, 0.11, 0.13], np.float32)          # the jungle's own green, sunk into the night


def _smooth(a, b, x):
    t = np.clip((x - a) / max(1e-6, b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _glow(rgba, em, glow, flowers=None, rim=0.9, edge=0.86, speckle=0.03, seed=0):
    """A plant at night with light in it: its own colours sunk to deep blue-green, keeping their
    shading; the edge of every leaf and frond traced in `glow`, its brightest highlights glowing as
    veins, its flowers (the warm reds and pinks of the plant) burning in `flowers`, and a scatter of
    glowing specks over the rest."""
    rgba = rgba.copy()
    a = rgba[..., 3] > 0.5
    col = rgba[..., :3]
    lum = col @ np.array([0.299, 0.587, 0.114], np.float32)
    lo, hi = (np.percentile(lum[a], 5), np.percentile(lum[a], 98)) if a.any() else (0.0, 1.0)
    t = np.clip((lum - lo) / (hi - lo + 1e-6), 0, 1)
    pad = np.pad(a, 1)
    inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
    g = np.maximum(_smooth(edge, edge + 0.12, t), (a & ~inner) * rim)
    rng = np.random.default_rng(seed)
    g = np.maximum(g, ((rng.random(a.shape) < speckle) & a) * 0.9)
    tint = np.broadcast_to(np.asarray(glow, np.float32), col.shape).copy()
    if flowers is not None:
        warm = a & (col[..., 0] > col[..., 1] * 1.3) & (col[..., 0] > 0.3)
        g = np.where(warm, np.maximum(g, 0.55 + 0.45 * t), g)
        tint[warm] = flowers
    shade = (0.3 + 0.7 * t)[..., None] * NIGHT
    rgb = shade * (1 - g[..., None]) + tint * g[..., None]
    rgba[..., :3] = np.where(a[..., None], rgb, rgba[..., :3])
    return rgba.astype(np.float32), np.where(a, np.maximum(em, g), 0.0).astype(np.float32)


def _variant(base, glow, **kw):
    def make():
        rgba, em = biomes.SPRITES[base]()
        return _glow(rgba, em, glow, seed=len(base) * 7, **kw)
    return make


def spr_glow_pods():
    """A stalk curling up out of the dark, hung with seed pods that glow from inside."""
    w, h = 24, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    pts = [(12 + 3.5 * np.sin(t * 2.6), 39 - 36 * t) for t in np.linspace(0, 1, 9)]
    cv.stroke(pts, 1.4, z=0.8, dome=0.6, mat=0)
    pods = []
    for k, t in enumerate((0.3, 0.45, 0.58, 0.7, 0.82, 0.93)):
        x, y = 12 + 3.5 * np.sin(t * 2.6), 39 - 36 * t
        side = 1 if k % 2 else -1
        cx, cy = x + side * 4.0, y + 1.5
        cv.stroke([(x, y), (cx, cy - 1.5)], 0.6, z=0.6, dome=0.4, mat=0)
        r = 2.6 - k * 0.22
        cv.ellipse(cx, cy, r * 0.8, r, z=1.4, dome=1.0, mat=1)
        pods.append((cx, cy, r))
    rgba, em = _prop(cv, [ramp(['#081614', '#0e2420', '#16332c', '#204438']),
                          ramp(['#1c5a6a', '#2f8fa0', '#5fd0d8', '#a8f4ef', '#e8fffb'])],
                     relief=1.0, cavity=0.3, shadow=0.3)
    m = (cv.mat == 1) & (rgba[..., 3] > 0.5)
    return rgba, np.where(m, np.maximum(em, 0.85), em).astype(np.float32)


def _dither(v, pal, amount=0.6):
    bay = np.tile(BAYER, (v.shape[0] // 4 + 1, v.shape[1] // 4 + 1))[:v.shape[0], :v.shape[1]]
    idx = np.clip(np.round(v * (len(pal) - 1) + (bay - 0.5) * amount), 0, len(pal) - 1).astype(int)
    return pal[idx].astype(np.float32)


def tex_glow_leaves(name):
    """A wall of rainforest at night: the leaves dark blue-green, ribs and tips of them glowing."""
    rgb = biomes.TEXTURES['jungle_leaves']('jungle_leaves')
    rgb = rgb[0] if isinstance(rgb, tuple) else rgb
    rgba = np.concatenate([rgb, np.ones(rgb.shape[:2] + (1,), np.float32)], -1)
    out, em = _glow(rgba, np.zeros(rgb.shape[:2], np.float32), [0.35, 0.95, 0.85], rim=0.0, edge=0.82,
                    speckle=0.03, seed=11)
    return out[..., :3], em * 0.9


def tex_lumen_floor(name):
    """The jungle floor at night: dark leaf litter, glowing moss in patches and fungus in specks."""
    rng = _rng(name)
    litter = smooth_noise(T, T, 16, rng) * 0.6 + smooth_noise(T, T, 5, rng) * 0.4
    rgb = _dither(np.clip(0.3 + 0.5 * (litter - 0.5), 0, 1),
                  ramp(['#06100e', '#0b1a16', '#11251f', '#183128', '#203e32']), 0.6)
    moss = _smooth(0.66, 0.8, smooth_noise(T, T, 9, rng)) * (rng.random((T, T)) < 0.35)
    specks = rng.random((T, T)) < 0.012
    em = np.clip(moss * 0.3 + specks * 0.95, 0, 1).astype(np.float32)
    glow = np.where(specks[..., None], np.array([0.75, 0.6, 1.0], np.float32), np.array([0.3, 0.95, 0.7], np.float32))
    rgb = rgb * (1 - em[..., None]) + glow * em[..., None]
    return rgb.astype(np.float32), em


def tex_glow_water(name):
    """Black water with plankton glowing blue in slow swirling streams."""
    rng = _rng(name)
    flow = smooth_noise(T, T, 3, rng) * 0.6 + smooth_noise(T, T, 7, rng) * 0.4
    streams = np.exp(-(((flow * 5.0) % 1.0) - 0.5) ** 2 / 0.006)
    dots = (rng.random((T, T)) < 0.05) * streams
    em = np.clip(streams * 0.35 + dots * 0.9, 0, 1).astype(np.float32)
    base = np.array([0.01, 0.025, 0.04], np.float32)
    glow = np.array([0.3, 0.75, 1.0], np.float32)
    rgb = base * (1 - em[..., None]) + glow * em[..., None]
    return rgb.astype(np.float32), em


BASES = {'glow_monstera': ('monstera', [0.35, 1.0, 0.85], None), 'glow_fern': ('fern', [0.4, 1.0, 0.95], None),
         'glow_tree_fern': ('tree_fern', [0.45, 0.9, 1.0], None),
         'glow_heliconia': ('heliconia', [0.4, 1.0, 0.8], [1.0, 0.38, 0.8]),
         'glow_bromeliad': ('bromeliad', [0.7, 0.55, 1.0], [1.0, 0.35, 0.9]),
         'glow_liana': ('liana', [0.4, 0.85, 1.0], None)}
CARDS = {'glow_jungle_card_%d' % k: ('jungle_card_%d' % k, [0.35, 0.95, 0.8], None) for k in range(1, 5)}
SPRITES = {name: _variant(base, glow, flowers=fl) for name, (base, glow, fl) in BASES.items()}
SPRITES.update({name: _variant(base, glow, rim=0.4, edge=0.9, speckle=0.02) for name, (base, glow, _) in CARDS.items()})
SPRITES['glow_pods'] = spr_glow_pods
SPRITE_HEIGHT = {name: biomes.SPRITE_HEIGHT[v[0]] for name, v in list(BASES.items()) + list(CARDS.items())}
SPRITE_HEIGHT['glow_pods'] = 1.1
PROP_DEFAULTS = {name: dict(biomes.PROP_DEFAULTS[v[0]]) for name, v in
                 list(BASES.items()) + list(CARDS.items()) if v[0] in biomes.PROP_DEFAULTS}
NO_CONTACT_SHADOW = set(CARDS)
TEXTURES = {'glow_leaves': lambda n: tex_glow_leaves(n), 'lumen_floor': tex_lumen_floor, 'glow_water': tex_glow_water}
TEXTURE_NOISE = {'glow_leaves': 0.3, 'lumen_floor': 0.4, 'glow_water': 0.0}
TEXTURE_REFLECT = {'glow_water': 0.55}
FRINGES = {'glow_jungle': ['glow_jungle_card_4', 'glow_jungle_card_3', 'glow_jungle_card_2', 'glow_jungle_card_1']}

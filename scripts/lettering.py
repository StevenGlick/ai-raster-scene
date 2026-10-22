"""Lettering: text made into pixel art - a painted board over a shop, neon tubes in a window, a brass plaque by a
door, letters cut in stone, chalk on a board, gilt on glass - and the words on a page (titles, captions).

Built on the pixel font (scripts/pixelfont.py): every letter drawn at a whole-number `scale`, so its pixels stay
square, and with `smooth` drawn at half that and its steps rounded off by scale2x, for big display lettering.
Several lines are split on newlines and centred.

    m = mask('THE BLUE LANTERN', scale=2)                          # True where the ink is
    rgba, em = sign('THE BLUE LANTERN', 'neon', color='#40e0ff')   # a texture: colour and alpha, emission
"""
import numpy as np

from pixelart import BAYER4, rgb, smooth_noise
from pixelfont import PixelFont

_FONT = PixelFont()
STYLES = ('painted', 'neon', 'plaque', 'carved', 'chalk', 'gilt', 'ink', 'poster')


def _scale2x(m):
    """A boolean mask twice the size, its diagonal steps rounded (EPX)."""
    p = np.pad(m, 1)
    A, B, C, D, P = p[:-2, 1:-1], p[1:-1, 2:], p[1:-1, :-2], p[2:, 1:-1], m
    out = np.zeros((m.shape[0] * 2, m.shape[1] * 2), bool)
    out[0::2, 0::2] = np.where((C == A) & (C != D) & (A != B), A, P)
    out[0::2, 1::2] = np.where((A == B) & (A != C) & (B != D), B, P)
    out[1::2, 0::2] = np.where((D == C) & (D != B) & (C != A), C, P)
    out[1::2, 1::2] = np.where((B == D) & (B != A) & (D != C), D, P)
    return out


def mask(text, scale=1, smooth=False, gap=3):
    """Text as a boolean mask (True where the ink is): the pixel font at `scale`, or with `smooth` at half that
    rounded off by scale2x; lines (split on newlines) `gap` pixels of the font apart, each centred, the empty
    rows round it trimmed."""
    scale = max(1, int(scale))
    rows = []
    for line in str(text).split('\n'):
        if smooth and scale >= 2:                                   # (an odd scale rounds down to even)
            m = _scale2x(np.asarray(_FONT.render_mask(line, scale // 2)) > 127)
        else:
            m = np.asarray(_FONT.render_mask(line, scale)) > 127
        rows.append(m)
    W = max(m.shape[1] for m in rows)
    g = gap * scale
    out = np.zeros((sum(m.shape[0] for m in rows) + g * (len(rows) - 1), W), bool)
    y = 0
    for m in rows:
        x = (W - m.shape[1]) // 2
        out[y:y + m.shape[0], x:x + m.shape[1]] = m
        y += m.shape[0] + g
    ys = np.nonzero(out.any(1))[0]
    return out[ys[0]:ys[-1] + 1] if len(ys) else out


def _grow(m, n=1):
    """A mask grown by n pixels all round (the eight neighbours)."""
    for _ in range(n):
        p = np.pad(m, 1)
        m = m | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:] | p[:-2, :-2] | p[:-2, 2:] | p[2:, :-2] | p[2:, 2:]
    return m


def _shift(m, dy, dx):
    """A mask moved by (dy, dx) pixels, what falls off the edge lost."""
    out = np.zeros_like(m)
    H, W = m.shape
    out[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = m[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)]
    return out


def _col(c, default):
    return rgb(c) if isinstance(c, str) else np.asarray(c if c is not None else rgb(default), np.float32)


def _plate(H, W, ground, seed, grain=0.0, rough=0.06, bevel=2):
    """A plate or a board of the colour `ground`, H x W: mottled (and with `grain`, streaked along its length), a
    bevel catching the light along its top and left edges and in shade along its bottom and right."""
    rng = np.random.default_rng(seed)
    v = 1.0 + rough * (smooth_noise(W, H, max(2, W // 8), rng, wrap=False) - 0.5) * 2
    if grain:
        streak = smooth_noise(W, H, max(2, W // 16), rng, wrap=False, cells_y=max(2, H // 2))   # along it
        v = v + grain * (streak - 0.5)
    yy, xx = np.mgrid[0:H, 0:W]
    edge = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy))
    lit = ((yy < bevel) | (xx < bevel)) & (edge < bevel)
    dark = ((yy >= H - bevel) | (xx >= W - bevel)) & (edge < bevel)
    v = v + 0.18 * lit - 0.22 * dark
    return np.clip(ground[None, None, :] * v[..., None], 0, 1)


def sign(text, style='painted', color=None, ground=None, scale=2, smooth=False, pad=None, seed=1, backing=True):
    """Lettering as a texture (rgba, emission), H x W, its letters `scale` pixels to a font pixel:

    - `painted`: a board of `ground` (default dark brown) with a bevelled edge and the grain of its wood, the
      letters in `color` (default cream) with a shadow under them, flaking here and there;
    - `neon`: the letters as glowing tubes of `color` (default pink), a halo round them, on a dark backing board
      (`backing` false: on nothing);
    - `plaque`: a brass plate, the letters engraved in it, a screw at each corner;
    - `carved`: letters cut into stone (`ground`, default grey), dark in the cut, the light on its lower edge;
    - `chalk`: chalk letters on a blackboard in a wooden frame;
    - `gilt`: letters in gold leaf, light along their tops and a dark line round them, on `ground` or on nothing;
    - `ink`: plain letters of `color` (default near black) on nothing - for a poster, a wall, a page;
    - `poster`: the ink letters on a sheet of paper.
    """
    if style not in STYLES:
        raise KeyError(f"unknown lettering style {style!r} - the styles are {', '.join(STYLES)}")
    rng = np.random.default_rng(seed)
    m = mask(text, scale, smooth)
    s = max(1, scale)
    pad = (3 * s + 2 if style in ('painted', 'plaque', 'carved', 'chalk', 'poster') else 2 * s + 1) if pad is None else int(pad)
    h, w = m.shape
    H, W = h + 2 * pad, w + 2 * pad
    ink = np.zeros((H, W), bool)
    ink[pad:pad + h, pad:pad + w] = m
    rgba = np.zeros((H, W, 4), np.float32)
    em = np.zeros((H, W), np.float32)
    bay = BAYER4[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4]
    if style == 'painted':
        g, c = _col(ground, '#3a2a1e'), _col(color, '#ecdcb0')
        rgba[..., :3] = _plate(H, W, g, seed, grain=0.12, bevel=max(2, s))
        yy, xx = np.mgrid[0:H, 0:W]
        e = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy))
        trim = (e >= max(2, s)) & (e < max(2, s) + max(1, s // 2))              # a painted line inside the edge
        rgba[trim, :3] = c * 0.8
        sh = _shift(ink, max(1, s // 2), max(1, s // 2)) & ~ink
        rgba[sh, :3] *= 0.45
        flake = (smooth_noise(W, H, max(2, W // 6), rng, wrap=False) > 0.78) & (rng.random((H, W)) < 0.35)
        rgba[ink, :3] = c * (0.92 + 0.12 * (bay[ink] - 0.5))[:, None]
        rgba[ink & flake, :3] = g * 1.15
        rgba[..., 3] = 1.0
    elif style == 'neon':
        c = _col(color, '#ff4fa0')
        halo = _grow(ink, max(1, s // 2 + 1)) & ~ink
        if backing:
            rgba[..., :3] = _plate(H, W, _col(ground, '#16141c'), seed, rough=0.05, bevel=1)
            rgba[..., 3] = 1.0
        rgba[halo, :3] = c * 0.62 + (rgba[halo, :3] * 0.3 if backing else 0)
        rgba[halo, 3] = 1.0 if backing else 0.7
        em[halo] = 0.55
        rgba[ink, :3] = np.clip(c * 0.65 + 0.4, 0, 1)
        rgba[ink, 3] = 1.0
        em[ink] = 1.0
    elif style == 'plaque':
        g = _col(ground, '#b08a3c')
        rgba[..., :3] = _plate(H, W, g, seed, rough=0.08, bevel=max(2, s))
        cut, lip = ink, _shift(ink, 1, 1) & ~ink
        rgba[cut, :3] = g * 0.32
        rgba[lip, :3] = np.clip(g * 1.35, 0, 1)
        for y, x in ((2, 2), (2, W - 3), (H - 3, 2), (H - 3, W - 3)):                     # the screws
            rgba[y - 1:y + 1, x - 1:x + 1, :3] = g * 0.55
        rgba[..., 3] = 1.0
    elif style == 'carved':
        g = _col(ground, '#9a968c')
        rgba[..., :3] = _plate(H, W, g, seed, rough=0.12, bevel=1)
        rgba[ink, :3] = g * 0.38                                                        # in the cut's shade
        lit = ink & ~_shift(ink, -max(1, s // 2), -max(1, s // 2))                       # its lower walls in light
        rgba[lit, :3] = g * 0.75
        rgba[..., 3] = 1.0
    elif style == 'chalk':
        board = _col(ground, '#1e2a24')
        rgba[..., :3] = _plate(H, W, board, seed, rough=0.1, bevel=1)
        yy, xx = np.mgrid[0:H, 0:W]
        e = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy))
        rgba[e < max(2, s), :3] = rgb('#6a4a30')                                         # its frame
        dust = rng.random((H, W)) < 0.22
        rgba[ink & ~dust, :3] = _col(color, '#e6e6dc')
        rgba[ink & dust, :3] = board * 1.6
        rgba[..., 3] = 1.0
    elif style == 'gilt':
        c = _col(color, '#d8b048')
        line = _grow(ink, 1) & ~ink
        if ground is not None:
            rgba[..., :3] = _plate(H, W, _col(ground, '#1a1a1e'), seed, rough=0.05, bevel=1)
            rgba[..., 3] = 1.0
        top = ink & ~_shift(ink, 1, 0)
        rgba[line, :3] = c * 0.3
        rgba[line, 3] = 1.0
        rgba[ink, :3] = c
        rgba[top, :3] = np.clip(c * 1.35, 0, 1)
        rgba[ink, 3] = 1.0
    else:                                                                               # ink, poster
        c = _col(color, '#1e1a16')
        if style == 'poster':
            rgba[..., :3] = _plate(H, W, _col(ground, '#d8c8a0'), seed, rough=0.1, bevel=0)
            rgba[..., 3] = 1.0
        rgba[ink, :3] = c
        rgba[ink, 3] = 1.0
    return rgba, em


def sprite(defn):
    """A scene's own sprite of lettering (a `sprite_defs` entry with `text`): `style`, `color`, `ground`, `scale`
    (default 2), `smooth`, `backing` as for sign()."""
    return sign(defn['text'], defn.get('style', 'painted'), defn.get('color'), defn.get('ground'),
                int(defn.get('scale', 2)), bool(defn.get('smooth', False)), defn.get('pad'), int(defn.get('seed', 1)),
                defn.get('backing', True))

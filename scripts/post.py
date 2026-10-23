"""Post-processing: colour grading, lens and weather effects, retro palettes, and display emulation.

Effects are listed in a scene's (or shot's) "post" array, applied in order within their stage:
  world    float image at native resolution, before the GUI is drawn (grade, bloom, rain, vignette...)
  palette  the quantisation step (one per frame; the last "palette" entry wins)
  display  uint8 image after the nearest-neighbour upscale, after the GUI (crt, vhs, chromatic, scanlines)

An entry is either a preset/effect name ("crt") or a dict {"fx": "bloom", "strength": 0.8}.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import weather
from pixelfont import PixelFont

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - 0.47

PALETTES = {
    'gameboy': ['#0f380f', '#306230', '#8bac0f', '#c4d82a'],
    'cga': ['#000000', '#55ffff', '#ff55ff', '#ffffff'],
    'cga_warm': ['#000000', '#55ff55', '#ff5555', '#ffff55'],
    'ega': ['#000000', '#0000aa', '#00aa00', '#00aaaa', '#aa0000', '#aa00aa', '#aa5500', '#aaaaaa',
            '#555555', '#5555ff', '#55ff55', '#55ffff', '#ff5555', '#ff55ff', '#ffff55', '#ffffff'],
    'amber': ['#0a0500', '#2a1400', '#552b00', '#804000', '#aa5a00', '#d47800', '#ffa000', '#ffc850'],
    'phosphor': ['#020a04', '#06260e', '#0c4a1a', '#147028', '#1f9a38', '#33c84e', '#5cf070', '#b4ffb8'],
    'sepia': ['#140c06', '#33220f', '#55391c', '#77532c', '#9a7044', '#bb8f62', '#d8b488', '#f2dcb4'],
    'mono': ['#000000', '#ffffff'],
    'bone': ['#0b0b10', '#25252e', '#45434a', '#6a6460', '#948a7a', '#c0b49a', '#e8dcc0'],
}
RAMPS = {'gameboy', 'amber', 'phosphor', 'sepia', 'mono', 'bone'}  # mapped by luminance

PRESETS = {
    'crt': [{'fx': 'crt'}],
    'crt_amber': [{'fx': 'palette', 'name': 'amber'}, {'fx': 'crt'}],
    'crt_green': [{'fx': 'palette', 'name': 'phosphor'}, {'fx': 'crt'}],
    'vhs': [{'fx': 'grade', 'saturation': 0.8, 'contrast': 1.05, 'lift': [0.03, 0.02, 0.04]}, {'fx': 'vhs'}],
    'gameboy': [{'fx': 'grade', 'contrast': 1.25}, {'fx': 'pixelate', 'factor': 2}, {'fx': 'palette', 'name': 'gameboy'}],
    'cga': [{'fx': 'grade', 'contrast': 1.2}, {'fx': 'palette', 'name': 'cga'}],
    'ega': [{'fx': 'grade', 'saturation': 1.3, 'contrast': 1.1}, {'fx': 'palette', 'name': 'ega'}],
    'nightvision': [{'fx': 'grade', 'contrast': 1.35, 'brightness': 0.1, 'gamma': 0.8}, {'fx': 'bloom', 'strength': 0.7},
                    {'fx': 'grain', 'amount': 0.06}, {'fx': 'vignette', 'strength': 0.85, 'radius': 0.62},
                    {'fx': 'palette', 'name': 'phosphor'}],
    'cinematic': [{'fx': 'grade', 'contrast': 1.12, 'saturation': 0.9, 'tint': [1.03, 1.0, 0.96]},
                  {'fx': 'bloom', 'strength': 0.45}, {'fx': 'vignette', 'strength': 0.4}, {'fx': 'letterbox'}],
    'horror': [{'fx': 'grade', 'saturation': 0.5, 'contrast': 1.18, 'tint': [1.0, 0.97, 0.88]},
               {'fx': 'grain', 'amount': 0.035}, {'fx': 'vignette', 'strength': 0.6}],
    'old_photo': [{'fx': 'grade', 'contrast': 1.1}, {'fx': 'grain', 'amount': 0.04},
                  {'fx': 'vignette', 'strength': 0.6}, {'fx': 'palette', 'name': 'sepia'}],
    'dream': [{'fx': 'grade', 'lift': [0.08, 0.05, 0.12], 'saturation': 1.2, 'exposure': 1.15}, {'fx': 'bloom', 'strength': 1.5, 'threshold': 0.3, 'radius': 10},
              {'fx': 'chromatic', 'offset': 2}],
    'bloodmoon': [{'fx': 'grade', 'tint': [1.25, 0.75, 0.7], 'saturation': 0.8, 'contrast': 1.1}, {'fx': 'vignette', 'strength': 0.6, 'color': [0.15, 0, 0]}],
    'storm': [{'fx': 'rain'}, {'fx': 'grade', 'saturation': 0.75, 'tint': [0.9, 0.97, 1.08]}],
    'blizzard': [{'fx': 'snow', 'count': 500}, {'fx': 'grade', 'lift': [0.05, 0.06, 0.08], 'saturation': 0.7}],
    'downpour': [{'fx': 'rain', 'density': 2.2, 'length': 9, 'opacity': 0.42, 'angle': 16},
                 {'fx': 'splashes', 'density': 1.4},
                 {'fx': 'grade', 'saturation': 0.7, 'brightness': -0.02, 'tint': [0.9, 0.96, 1.06]}],
    'autumn': [{'fx': 'leaves'}, {'fx': 'grade', 'tint': [1.08, 0.98, 0.86], 'saturation': 1.1}],
    'sandstorm': [{'fx': 'dust', 'density': 1.6}, {'fx': 'grade', 'tint': [1.12, 0.98, 0.8], 'saturation': 0.7}],
    'ashfall': [{'fx': 'ash'}, {'fx': 'embers', 'count': 50},
                {'fx': 'grade', 'tint': [1.1, 0.9, 0.82], 'saturation': 0.55}],
    'hurt': [{'fx': 'hurt'}],
}

WORLD = {'grade', 'bloom', 'vignette', 'grain', 'rain', 'snow', 'lightning', 'letterbox', 'hurt', 'fade',
         'splashes', 'embers', 'fireflies', 'spores', 'ash', 'leaves', 'dust',
         'pixelate', 'posterize', 'gradient_map', 'dof', 'streaks', 'flare', 'speed'}
LENS = {'dof'}      # run first, on the bare frame: a held item drawn after them stays sharp
DISPLAY = {'crt', 'vhs', 'chromatic', 'scanlines'}


def expand(entries):
    out = []
    for e in entries or []:
        if isinstance(e, str):
            if e in PRESETS:
                out += [dict(x) for x in PRESETS[e]]
            else:
                out.append({'fx': e})
        elif 'preset' in e:
            if e['preset'] not in PRESETS:
                raise KeyError(f"unknown post preset '{e['preset']}'. Presets: {sorted(PRESETS)}")
            out += [dict(x) for x in PRESETS[e['preset']]]
        elif 'fx' not in e:
            raise KeyError(f"post entry {e} needs an 'fx' (effect name) or 'preset' key")
        else:
            out.append(dict(e))
    for e in out:
        if e['fx'] not in WORLD | DISPLAY | {'palette'}:
            raise KeyError(f"unknown post effect '{e['fx']}'. Effects: {sorted(WORLD | DISPLAY | {'palette'})}; "
                           f"presets: {sorted(PRESETS)}")
    return out


def _rgb(c):
    if isinstance(c, str):
        c = c.lstrip('#')
        return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
    return np.array(c, np.float32)


def _blur(img, r):
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


def _lum(img):
    return img[..., 0] * 0.299 + img[..., 1] * 0.587 + img[..., 2] * 0.114


def _box(a, w, axis):
    """A box blur `w` wide (odd) along one axis, edges clamped, in float."""
    h = w // 2
    pad = [(0, 0)] * a.ndim
    pad[axis] = (h + 1, h)
    c = np.cumsum(np.pad(a, pad, mode='edge'), axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(w, w + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / w).astype(np.float32)


def _fblur(img, r):
    """A Gaussian blur of radius (sigma) `r` that stays in float: three box blurs each way, which is
    as smooth to the eye and keeps the faint ends of a glow from banding in 8 bits."""
    if r < 0.35:
        return np.asarray(img, np.float32).copy()
    w = max(1, int(round(np.sqrt(4 * r * r + 1))) | 1)
    out = np.asarray(img, np.float32)
    for axis in (0, 1):
        for _ in range(3):
            out = _box(out, w, axis)
    return out


# ------------------------------------------------------------------ world stage

def fx_grade(img, p, ctx):
    img = img * float(p.get('exposure', 1.0)) + float(p.get('brightness', 0.0))
    if 'tint' in p:
        img = img * _rgb(p['tint'])
    if 'lift' in p:
        img = img + _rgb(p['lift']) * (1 - img)
    c = float(p.get('contrast', 1.0))
    img = (img - 0.5) * c + 0.5
    s = float(p.get('saturation', 1.0))
    if s != 1.0:
        l = _lum(img)[..., None]
        img = l + (img - l) * s
    g = float(p.get('gamma', 1.0))
    img = np.clip(img, 0, 1) ** g
    return img


def fx_bloom(img, p, ctx):
    """Glow round bright things. `source` "image" (the default) blooms whatever is bright in the
    frame above `threshold`; "light" blooms only what gives off light - neon, lit windows, screens,
    flames, lamps, a sun or moon disc, and their reflections in wet ground (the renderer's emission
    buffer) - so a white wall stays a white wall and the glow can go much stronger. `spread` (0-1)
    sends that share of the glow into a wide halo round the tight core; with it, or with "light",
    the glow is blurred in float in three widths."""
    source = p.get('source', 'image')
    if source == 'image' and 'spread' not in p:
        thr = float(p.get('threshold', 0.65))
        bright = np.clip(img - thr, 0, 1) / max(1e-3, 1 - thr)
        glow = _blur(bright, float(p.get('radius', 6)))
        return img + glow * float(p.get('strength', 0.6)) * _rgb(p.get('color', [1, 1, 1]))
    if source == 'light':
        em = ctx.get('emission')
        bright = np.maximum((em if em is not None else np.zeros_like(img)) - float(p.get('threshold', 0.0)), 0)
    else:
        thr = float(p.get('threshold', 0.65))
        bright = np.clip(img - thr, 0, 1) / max(1e-3, 1 - thr)
    r = float(p.get('radius', 4))
    spread = float(p.get('spread', 0.45))
    glow = _fblur(bright, r) * (1 - spread) + (_fblur(bright, r * 3) * 0.6 + _fblur(bright, r * 8) * 0.4) * spread
    return img + glow * float(p.get('strength', 0.8)) * _rgb(p.get('color', [1, 1, 1]))


def fx_dof(img, p, ctx):
    """Depth of field: the frame sharp at the `focus` distance and softening away from it, nearer
    and farther, as through a lens wide open. `focus` is a distance, a sprite's id, or left out to
    focus where the shot's `look_at` is (else on the middle of the frame); `blur` is the widest blur
    in pixels, reached at the horizon and at half the focus distance; `range` (0-1) widens the band
    that stays sharp. Each pixel takes the blur its distance asks for; the background is gathered
    only from pixels at or beyond the focus, so a sharp subject never smears into it, and a soft
    foreground spreads over whatever is behind its edges."""
    depth = ctx.get('depth')
    if depth is None:
        return img
    d = np.maximum(np.nan_to_num(depth, nan=1e4, posinf=1e4), 1e-3)
    f = p.get('focus')
    if isinstance(f, str):
        a = (ctx.get('anchors') or {}).get(f)
        f = a.get('depth') if a else None
    if f is None:
        f = ctx.get('focus')
    if f is None:
        H, W = d.shape
        f = float(np.median(d[H * 2 // 5:H * 3 // 5, W * 2 // 5:W * 3 // 5]))
    f = max(float(f), 0.05)
    maxb = max(0.0, float(p.get('blur', 2.5)))
    band = min(0.95, max(0.0, float(p.get('range', 0.1))))
    if maxb < 0.35:
        return img
    c = np.abs(1.0 / f - 1.0 / d) * f                     # 0 in focus, 1 at the horizon and at f/2
    coc = maxb * np.clip((c - band) / (1 - band), 0, 1)
    far = d >= f
    n = 4
    step = maxb / n
    wf = far.astype(np.float32)[..., None]
    lev_far, lev_near = [img], [img]
    for k in range(1, n + 1):
        r = step * k
        num, den = _fblur(img * wf, r), _fblur(wf, r)
        lev_far.append(np.where(den > 1e-3, num / np.maximum(den, 1e-3), img))
        lev_near.append(_fblur(img, r))
    x = np.clip(coc / step, 0, n)
    k0 = np.minimum(x.astype(int), n - 1)
    t = (x - k0)[..., None]
    lf, ln = np.stack(lev_far), np.stack(lev_near)
    rows, cols = np.indices(d.shape)
    pick = np.where(far[..., None], lf[k0, rows, cols] * (1 - t) + lf[k0 + 1, rows, cols] * t,
                    ln[k0, rows, cols] * (1 - t) + ln[k0 + 1, rows, cols] * t)
    near = (~far) & (coc > 0.5)
    if near.any():                                          # a soft foreground spreads past its edges
        rn = float(np.mean(coc[near]))
        m = near.astype(np.float32)[..., None]
        cover = _fblur(m, rn)
        layer = _fblur(img * m, rn) / np.maximum(cover, 1e-3)
        a_ = np.clip(cover * 1.6, 0, 1) * (1 - m)
        pick = pick * (1 - a_) + layer * a_
    return pick.astype(img.dtype)          # what stayed sharp keeps the frame's own values, exactly


def _lights(img, p, ctx):
    """What gives off light in the frame: the renderer's emission (the default `source`, "light"),
    or with "image" whatever is brighter than `threshold`."""
    em = ctx.get('emission')
    if p.get('source', 'light') == 'light' and em is not None:
        return np.maximum(em - float(p.get('threshold', 0.0)), 0)
    thr = float(p.get('threshold', 0.75))
    return np.clip(img - thr, 0, 1) / max(1e-3, 1 - thr)


def _peaks(src, count, gap, floor, compact):
    """The brightest compact lights in `src` (H x W x 3): up to `count` of them, at least `gap`
    pixels apart, each as (row, column, brightness, colour). A light is compact when it stands out
    from the light round it by at least `compact` of its own brightness - a lamp, a flame, the
    hottest letters of a sign - so a glowing sky or the even run of a long tube is passed over."""
    lum = _lum(src)
    near = _fblur(lum, 1.0)                  # ranked by the light round each pixel: lamps over lines
    score = np.where(near - _fblur(lum, 5.0) >= compact * near, near, 0.0)
    H, W = lum.shape
    out = []
    for _ in range(count):
        y, x = divmod(int(np.argmax(score)), W)
        v = float(score[y, x])                   # how much light it gives: a small one streaks faintly
        if v < floor:
            break
        out.append((float(y), float(x), v, src[y, x] / max(1e-6, float(src[y, x].max()))))
        score[max(0, y - gap):y + gap + 1, max(0, x - gap):x + gap + 1] = 0
    return out


def _suns(ctx, p):
    """The sun or moon discs that show in the frame, as light sources (row, column, brightness,
    colour) - brightness is how much of the disc shows, less for the moon."""
    if not p.get('sun', True):
        return []
    return [(s_['y'], s_['x'], s_['visible'] * s_['power'], np.asarray(s_['color'], np.float32))
            for s_ in ctx.get('suns') or [] if s_['visible'] > 0.02]


def _splat(layer, ys, xs, w, c):
    """Add w * c at the float positions (ys, xs) of `layer`, shared out over the nearest pixels."""
    H, W = layer.shape[:2]
    y0, x0 = np.floor(ys).astype(int), np.floor(xs).astype(int)
    fy, fx = ys - y0, xs - x0
    for oy, ox, k in ((0, 0, (1 - fy) * (1 - fx)), (0, 1, (1 - fy) * fx), (1, 0, fy * (1 - fx)), (1, 1, fy * fx)):
        yy, xx = y0 + oy, x0 + ox
        ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W) & (k > 0)
        np.add.at(layer, (yy[ok], xx[ok]), (w * k)[ok][:, None] * c[None, :])


def fx_streaks(img, p, ctx):
    """Light drawn out in thin lines from the brightest lights, as through a star filter or an
    anamorphic lens. `points` 4 makes a cross (the default), 6 or 8 a star, 2 one horizontal line -
    the anamorphic look, best long (`length` 40 or more) and blue (`color` [0.6, 0.8, 1.3]);
    `angle` turns the star; `length` (pixels) is how far a line runs before it fades to a third.
    Only the brightest compact lights streak - up to `count` (24) of them, a lamp, a flame, a
    sign's hottest letters - and a sun or moon in the frame (unless `sun` is false), longest of
    all; `white` (0.4) pales the lines from the light's own colour toward white."""
    H, W = img.shape[:2]
    src = _lights(img, p, ctx)
    peaks = _peaks(src, int(p.get('count', 24)), int(p.get('gap', 4)), float(p.get('min', 0.05)),
                   float(p.get('compact', 0.35)))
    suns = _suns(ctx, p)
    if not peaks and not suns:
        return img
    length = max(1.0, float(p.get('length', 12)))
    pts = max(2, int(p.get('points', 4)))
    lines = max(1, pts // 2)
    a0 = math.radians(float(p.get('angle', 0)))
    white = float(p.get('white', 0.4))
    layer = np.zeros((H, W, 3), np.float32)
    for (y, x, v, c), reach0 in [(q, length) for q in peaks] + [(q, length * 2.5) for q in suns]:
        c = np.asarray(c, np.float32) * (1 - white) + white
        for j in range(lines):
            a = a0 + math.pi * j / lines
            reach = reach0 * (0.55 if pts >= 8 and j % 2 else 1.0)   # a star filter's short diagonals
            k = np.arange(1, int(3 * reach) + 1, dtype=np.float32)
            w = v * np.exp(-k / reach)
            for sgn in (1.0, -1.0):
                _splat(layer, y - sgn * math.sin(a) * k, x + sgn * math.cos(a) * k, w, c)
    return img + layer * float(p.get('strength', 0.6)) * _rgb(p.get('color', [1, 1, 1]))


# a lens flare's ghosts: (place on the line from the light through the middle of the frame - 1 is
# the middle, 2 the far side; radius as a share of the frame's height; colour; brightness; shape)
FLARE_GHOSTS = [(0.3, 0.022, [1.0, 0.85, 0.55], 0.5, 'disc'), (0.58, 0.05, [0.55, 1.0, 0.65], 0.26, 'hex'),
                (0.86, 0.012, [1.0, 1.0, 0.8], 0.55, 'disc'), (1.2, 0.02, [0.75, 0.6, 1.0], 0.45, 'disc'),
                (1.45, 0.085, [0.5, 0.8, 1.0], 0.18, 'hex'), (1.72, 0.04, [1.0, 0.6, 0.45], 0.3, 'ring'),
                (2.05, 0.13, [0.6, 0.55, 1.0], 0.13, 'hex')]


def fx_flare(img, p, ctx):
    """A lens flare: a string of faint coloured ghosts - discs, a ring, the six-sided shape of the
    aperture - running from a bright light through the middle of the frame and out the other side,
    and a pale ring round the light. The light is the sun or moon when its disc shows in the frame
    (the default `source`, "sun"; none when it is behind a wall or a tree or out of the frame, and
    weaker as less of it shows); with "light", the brightest compact light in view - a lamp, a
    headlight - or the `sources` brightest. `strength` 0.6; `ghosts` how many of the seven to draw;
    `halo` (0.25) the ring's strength."""
    H, W = img.shape[:2]
    if p.get('source', 'sun') == 'sun':
        srcs = _suns(ctx, {})
    else:
        srcs = [(y, x, min(1.0, v * 1.5), c) for y, x, v, c in
                _peaks(_lights(img, p, ctx), int(p.get('sources', 1)), max(4, H // 10), 0.05, 0.35)]
    if not srcs:
        return img
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ghosts = FLARE_GHOSTS[:max(0, int(p.get('ghosts', len(FLARE_GHOSTS))))]
    out = img.copy()
    for sy, sx, v, tint in srcs:
        k = float(p.get('strength', 0.6)) * min(1.0, v)
        tint = np.asarray(tint, np.float32) * 0.4 + 0.6        # the ghosts take a little of its colour
        cx, cy = (W - 1) / 2, (H - 1) / 2
        # with the light near the middle the ghosts pile up on it, where its own glare hides them
        kg = k * (0.25 + 0.75 * min(1.0, math.hypot(sx - cx, sy - cy) / (0.3 * H)))
        for t, rad, col, a, shape in ghosts:
            gx, gy = sx + (cx - sx) * t, sy + (cy - sy) * t
            rr = max(1.0, rad * H)
            ux, uy = (xx - gx) / rr, (yy - gy) / rr
            if shape == 'hex':
                d = np.maximum(np.abs(uy), np.abs(ux) * 0.866 + np.abs(uy) * 0.5)
                g = np.clip((1.0 - d) * 5, 0, 1) * (0.5 + 0.5 * np.clip(d, 0, 1) ** 3)
            elif shape == 'ring':
                g = np.exp(-((np.hypot(ux, uy) - 1.0) * 5) ** 2)
            else:
                g = np.clip(1.0 - np.hypot(ux, uy), 0, 1) ** 0.7
            out = out + (g * a * kg)[..., None] * (_rgb(col) * tint)
        halo = float(p.get('halo', 0.25))
        if halo > 0:
            d = np.hypot(xx - sx, yy - sy) / (H * 0.22)
            ring = np.exp(-((d - 1.0) * 7) ** 2) * halo * k * 0.5
            out = out + ring[..., None] * (_rgb([1.0, 0.9, 0.75]) * tint)
    return out


def fx_vignette(img, p, ctx):
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) / math.sqrt(2)
    rad = float(p.get('radius', 0.7))
    k = np.clip((r - rad * 0.55) / (1 - rad * 0.55), 0, 1) ** 1.6 * float(p.get('strength', 0.5))
    col = _rgb(p.get('color', [0, 0, 0]))
    return img * (1 - k[..., None]) + col * k[..., None]


def fx_speed(img, p, ctx):
    """Speed: the frame streaked outward from the point it rushes toward - a road's vanishing point, or `x`, `y`
    (0-1 across and down the frame) - more toward its edges, its middle (`clear`, 0.3) and a road shot's own
    vehicle left sharp: an arcade racer's sense of speed. `strength` 0.4 how far the streaks reach, `samples` 10."""
    H, W = img.shape[:2]
    cx, cy = W / 2, H / 2
    rays = ctx.get('rays') or {}
    if 'horizon' in rays:                      # a road shot: the horizon, and the column the road runs toward
        cy = float(rays['horizon'])
        rdx = np.asarray(rays.get('rdx', []), np.float64)
        rdy = np.asarray(rays.get('rdy', [0.0]), np.float64)
        if len(rdx) == W and np.allclose(rdy, 1.0) and rdx.min() < 0 < rdx.max():    # a road's rays: rdx is
            cx = float(np.interp(0.0, rdx, np.arange(W) + 0.5))                     # zero where it runs to
    cx = float(p['x']) * W if 'x' in p else cx
    cy = float(p['y']) * H if 'y' in p else cy
    reach = float(p.get('strength', 0.4)) * 0.16
    n = max(2, int(p.get('samples', 10)))
    clear = float(p.get('clear', 0.3))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) + 0.5
    dx, dy = xx - cx, yy - cy
    k = np.clip((np.hypot(dx / (W / 2), dy / (H / 2)) - clear) / max(1e-6, 1.2 - clear), 0, 1) ** 1.3
    v = (ctx.get('anchors') or {}).get('_vehicle')
    if v:                                      # your own car is moving with you: it stays sharp
        k[(xx >= v['x'] - v['w'] / 2 - 1) & (xx < v['x'] + v['w'] / 2 + 1) & (yy >= v['top'] - 1) &
          (yy < v['top'] + v['h'] + 1)] = 0.0
    acc = img.astype(np.float32).copy()
    for i in range(1, n):
        f = 1 - reach * k * i / (n - 1)
        acc += img[np.clip(cy + dy * f, 0, H - 1).astype(int), np.clip(cx + dx * f, 0, W - 1).astype(int)]
    return acc / n


def fx_grain(img, p, ctx):
    rng = np.random.default_rng(ctx['seed'] + 1)
    a = float(p.get('amount', 0.06))
    if p.get('color'):
        n = rng.normal(0, a, img.shape)
    else:
        n = rng.normal(0, a, img.shape[:2])[..., None]
    return img + n


def fx_rain(img, p, ctx):
    if ctx.get('rays') is not None:            # a 3D frame: rain falls in the world, behind things
        return weather.rain(img, p, ctx)
    H, W = img.shape[:2]
    rng = np.random.default_rng(ctx['seed'] + 2)
    n = int(float(p.get('density', 1.0)) * W * H / 160)
    ln = float(p.get('length', 7))
    ang = math.radians(float(p.get('angle', 12)))
    lay = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y = rng.random() * (W + 40) - 20, rng.random() * (H + 20) - 20
        l = ln * (0.5 + rng.random())
        d.line([(x, y), (x + math.sin(ang) * l, y + math.cos(ang) * l)], fill=int(120 + rng.random() * 135))
    a = np.asarray(lay, np.float32)[..., None] / 255 * float(p.get('opacity', 0.35))
    col = _rgb(p.get('color', [0.75, 0.8, 0.9]))
    return img * (1 - a) + col * a


def fx_snow(img, p, ctx):
    if ctx.get('rays') is not None:
        return weather.snow(img, p, ctx)
    H, W = img.shape[:2]
    rng = np.random.default_rng(ctx['seed'] + 3)
    lay = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(lay)
    for _ in range(int(p.get('count', 260))):
        x, y = int(rng.random() * W), int(rng.random() * H)
        s = 1 if rng.random() < 0.75 else 2
        d.rectangle([x, y, x + s - 1, y + s - 1], fill=int(150 + rng.random() * 105))
    a = np.asarray(lay, np.float32)[..., None] / 255 * float(p.get('opacity', 0.85))
    return img * (1 - a) + _rgb(p.get('color', [0.95, 0.97, 1.0])) * a


def fx_splashes(img, p, ctx):
    return weather.splashes(img, p, ctx)


def fx_embers(img, p, ctx):
    return weather.embers(img, p, ctx)


def fx_fireflies(img, p, ctx):
    return weather.fireflies(img, p, ctx)


def fx_spores(img, p, ctx):
    return weather.spores(img, p, ctx)


def fx_ash(img, p, ctx):
    return weather.ash(img, p, ctx)


def fx_leaves(img, p, ctx):
    return weather.leaves(img, p, ctx)


def fx_dust(img, p, ctx):
    return weather.dust(img, p, ctx)


def fx_lightning(img, p, ctx):
    H, W = img.shape[:2]
    amt = float(p.get('amount', 0.45))
    out = img + amt * _rgb(p.get('color', [0.75, 0.8, 1.0])) * (0.4 + _lum(img)[..., None])
    if p.get('bolt', True):
        rng = np.random.default_rng(ctx['seed'] + 4)
        lay = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(lay)
        x = float(p.get('x', 0.3 + rng.random() * 0.4)) * W
        y, pts = 0.0, []
        end = float(p.get('y_end', 0.42)) * H
        while y < end:
            pts.append((x, y))
            y += 4 + rng.random() * 8
            x += (rng.random() - 0.5) * 14
        d.line(pts, fill=255, width=1)
        a = _blur(np.asarray(lay, np.float32)[..., None].repeat(3, 2) / 255, 2) * 1.5
        out = out + a * 0.8 + (np.asarray(lay, np.float32)[..., None] / 255)
    return out


def fx_letterbox(img, p, ctx):
    H = img.shape[0]
    h = int(H * float(p.get('height', 0.11)))
    img = img.copy()
    img[:h] = _rgb(p.get('color', [0, 0, 0]))
    img[H - h:] = _rgb(p.get('color', [0, 0, 0]))
    return img


def fx_hurt(img, p, ctx):
    return fx_vignette(img, {'strength': p.get('strength', 0.75), 'radius': p.get('radius', 0.55),
                             'color': p.get('color', [0.55, 0.0, 0.0])}, ctx)


def fx_fade(img, p, ctx):
    a = float(p.get('amount', 0.5))
    return img * (1 - a) + _rgb(p.get('color', [0, 0, 0])) * a


def fx_pixelate(img, p, ctx):
    f = int(p.get('factor', 2))
    if f <= 1:
        return img
    H, W = img.shape[:2]
    h, w = H // f, W // f
    small = img[:h * f, :w * f].reshape(h, f, w, f, 3).mean(axis=(1, 3))
    out = img.copy()
    out[:h * f, :w * f] = small.repeat(f, 0).repeat(f, 1)
    return out


def fx_posterize(img, p, ctx):
    n = max(1, int(p.get('levels', 6)) - 1)  # 2 levels is the floor: black and white
    return np.round(np.clip(img, 0, 1) * n) / n


def fx_gradient_map(img, p, ctx):
    cols = np.array([_rgb(c) for c in p.get('colors', ['#0a0a1e', '#7a2a4a', '#f0c070'])])
    l = np.clip(_lum(img), 0, 1) * (len(cols) - 1)
    i = np.clip(np.floor(l).astype(int), 0, len(cols) - 2)
    t = (l - i)[..., None]
    mapped = cols[i] * (1 - t) + cols[i + 1] * t
    a = float(p.get('amount', 1.0))
    return img * (1 - a) + mapped * a


WORLD_FX = {k: globals()['fx_' + k] for k in WORLD}


def apply_world(img, effects, ctx):
    for e in effects:
        if e['fx'] in WORLD_FX:
            img = WORLD_FX[e['fx']](img, e, ctx)
    return np.clip(img, 0, 1)


# ------------------------------------------------------------------ palette stage

def quantize(img, spec, dither=1.0, levels=True, ref=None):
    """img float HxWx3 -> uint8 HxWx3. spec: int (adaptive), name, list of hex colours, or 0/None.
    `ref` is the frame as it would be without a lens effect (depth of field): the colours are
    chosen from it, so a subject left sharp keeps exactly the colours it has in a shot without
    the lens, instead of losing palette entries to the shades of a blurred background."""
    H, W = img.shape[:2]
    bay = np.tile(BAYER4, (H // 4 + 1, W // 4 + 1))[:H, :W]
    if not spec:
        return (np.clip(img, 0, 1) * 255).astype(np.uint8)
    if isinstance(spec, (int, float)):
        arr = img * 255 + bay[..., None] * 18 * dither
        a8 = np.clip(arr, 0, 255).astype(np.uint8)
        pim = Image.fromarray(a8, 'RGB')
        if ref is None:
            pim = pim.quantize(colors=int(spec), method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            return np.asarray(pim.convert('RGB'))
        r8 = np.clip(ref * 255 + bay[..., None] * 18 * dither, 0, 255).astype(np.uint8)
        rq = Image.fromarray(r8, 'RGB').quantize(colors=int(spec), method=Image.Quantize.MEDIANCUT,
                                                 dither=Image.Dither.NONE)
        out = np.array(pim.quantize(palette=rq, dither=Image.Dither.NONE).convert('RGB'))
        same = (a8 == r8).all(-1)            # what the lens left alone comes out as it would without it
        out[same] = np.asarray(rq.convert('RGB'))[same]
        return out
    name = spec if isinstance(spec, str) else None
    cols = np.array([_rgb(c) for c in (PALETTES[spec] if name else spec)], np.float32)
    if levels:
        # few-colour palettes need the full tonal range or dark scenes collapse into one shade
        l = _lum(img if ref is None else ref)
        lo, hi = np.percentile(l, 2), np.percentile(l, 99)
        gain = min(3.0, 1.0 / max(1e-3, hi - lo))
        img = np.clip((img - lo) * gain, 0, 1)
    if name in RAMPS:
        n = len(cols)
        l = np.clip(_lum(img), 0, 1) * (n - 1) + bay * dither * 0.9
        idx = np.clip(np.round(l), 0, n - 1).astype(int)
        return (cols[idx] * 255).astype(np.uint8)
    spread = 0.9 / max(1.0, len(cols) ** (1 / 3))
    a = np.clip(img + bay[..., None] * spread * dither, 0, 1)
    d = ((a[:, :, None, :] - cols[None, None, :, :]) ** 2).sum(-1)
    return (cols[d.argmin(-1)] * 255).astype(np.uint8)


def palette_spec(effects, scene):
    spec, levels = scene.get('palette', 256), scene.get('auto_levels', True)
    for e in effects:
        if e['fx'] == 'palette':
            spec = e.get('name', e.get('colors', spec))
            levels = e.get('auto_levels', levels)
    return spec, levels


# ------------------------------------------------------------------ display stage (uint8, upscaled)

def dx_scanlines(arr, p, ctx):
    s = ctx['scale']
    a = arr.astype(np.float32)
    a[s - 1::s] *= 1 - float(p.get('strength', 0.28))
    return a


def dx_chromatic(arr, p, ctx):
    o = int(p.get('offset', 2))
    if o <= 0:
        return arr.astype(np.float32)
    a = arr.astype(np.float32).copy()
    a[:, o:, 0] = arr[:, :-o, 0]
    a[:, :-o, 2] = arr[:, o:, 2]
    return a


def dx_crt(arr, p, ctx):
    s = ctx['scale']
    H, W = arr.shape[:2]
    a = arr.astype(np.float32)
    # soft glow so bright pixels bleed like phosphor
    glow = np.asarray(Image.fromarray(arr).filter(ImageFilter.GaussianBlur(s * 0.9)), np.float32)
    a = a * 0.82 + glow * float(p.get('glow', 0.35))
    # scanlines and aperture-grille mask
    a[s - 1::s] *= 1 - float(p.get('scanline', 0.3))
    m = float(p.get('mask', 0.18))
    for ch in range(3):
        a[:, (np.arange(W) % 3) != ch, ch] *= 1 - m
    a *= 1 + m * 0.6
    # barrel curvature
    k = float(p.get('curvature', 0.07))
    if k > 0:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        nx, ny = xx / W * 2 - 1, yy / H * 2 - 1
        r2 = nx * nx + ny * ny
        sx, sy = nx * (1 + k * r2), ny * (1 + k * r2)
        inside = (np.abs(sx) <= 1) & (np.abs(sy) <= 1)
        px = np.clip(((sx + 1) / 2 * W).astype(int), 0, W - 1)
        py = np.clip(((sy + 1) / 2 * H).astype(int), 0, H - 1)
        a = a[py, px] * inside[..., None]
        # rounded corner falloff
        edge = np.clip(1 - np.maximum(np.abs(sx), np.abs(sy)), 0, 1)
        a *= np.clip(edge * 40, 0, 1)[..., None]
    v = float(p.get('vignette', 0.3))
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    a *= (1 - v * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None]
    return a


def dx_vhs(arr, p, ctx):
    s = ctx['scale']
    H, W = arr.shape[:2]
    rng = np.random.default_rng(ctx['seed'] + 7)
    a = arr.astype(np.float32)
    # chroma bleed: keep luma sharp, smear colour sideways
    l = _lum(a / 255)[..., None] * 255
    chroma = a - l
    k = int(p.get('bleed', 4)) * s
    if k > 1:
        ker = np.ones(k) / k
        chroma = np.apply_along_axis(lambda r: np.convolve(r, ker, mode='same'), 1, chroma)
    a = l + chroma
    a[:, :, 0] = np.roll(a[:, :, 0], s, axis=1)
    # line jitter and a tracking band
    jit = (rng.random(H // s + 1) < 0.08) * rng.integers(-2, 3, H // s + 1) * s
    for i, j in enumerate(jit):
        if j:
            a[i * s:(i + 1) * s] = np.roll(a[i * s:(i + 1) * s], j, axis=1)
    band = int(float(p.get('tracking', 0.85)) * H)
    bh = 6 * s
    seg = a[band:band + bh]
    a[band:band + bh] = np.roll(seg, 8 * s, axis=1) * 0.8 + rng.random(seg.shape[:2])[..., None] * 90
    a += rng.normal(0, 7, a.shape[:2])[..., None]
    # on-screen display text
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    f = PixelFont()
    for text, (x, y) in ((p.get('label', 'PLAY'), (14, 12)), (p.get('timestamp', 'OCT 19 1994  23:47'), (14, None))):
        if not text:
            continue
        mask = f.render_mask(text).resize((f.getlength(text) * s, 9 * s), Image.NEAREST)
        yy = y * s if y is not None else H - 22 * s
        d.bitmap((x * s + s, yy + s), mask, fill=(0, 0, 0))
        d.bitmap((x * s, yy), mask, fill=(235, 235, 235))
    if p.get('label', 'PLAY') == 'PLAY':
        x0 = 14 * s + f.getlength('PLAY') * s + 4 * s
        d.polygon([(x0, 13 * s), (x0, 20 * s), (x0 + 5 * s, 16 * s)], fill=(235, 235, 235))
    return np.asarray(img, np.float32)


DISPLAY_FX = {'crt': dx_crt, 'vhs': dx_vhs, 'chromatic': dx_chromatic, 'scanlines': dx_scanlines}


def apply_display(arr, effects, ctx):
    for e in effects:
        if e['fx'] in DISPLAY_FX:
            arr = np.clip(DISPLAY_FX[e['fx']](arr, e, ctx), 0, 255).astype(np.uint8)
    return arr

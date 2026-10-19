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
    'hurt': [{'fx': 'hurt'}],
}

WORLD = {'grade', 'bloom', 'vignette', 'grain', 'rain', 'snow', 'lightning', 'letterbox', 'hurt', 'fade',
         'pixelate', 'posterize', 'gradient_map'}
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
    thr = float(p.get('threshold', 0.65))
    bright = np.clip(img - thr, 0, 1) / max(1e-3, 1 - thr)
    glow = _blur(bright, float(p.get('radius', 6)))
    return img + glow * float(p.get('strength', 0.6)) * _rgb(p.get('color', [1, 1, 1]))


def fx_vignette(img, p, ctx):
    H, W = img.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) / math.sqrt(2)
    rad = float(p.get('radius', 0.7))
    k = np.clip((r - rad * 0.55) / (1 - rad * 0.55), 0, 1) ** 1.6 * float(p.get('strength', 0.5))
    col = _rgb(p.get('color', [0, 0, 0]))
    return img * (1 - k[..., None]) + col * k[..., None]


def fx_grain(img, p, ctx):
    rng = np.random.default_rng(ctx['seed'] + 1)
    a = float(p.get('amount', 0.06))
    if p.get('color'):
        n = rng.normal(0, a, img.shape)
    else:
        n = rng.normal(0, a, img.shape[:2])[..., None]
    return img + n


def fx_rain(img, p, ctx):
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

def quantize(img, spec, dither=1.0, levels=True):
    """img float HxWx3 -> uint8 HxWx3. spec: int (adaptive), name, list of hex colours, or 0/None."""
    H, W = img.shape[:2]
    bay = np.tile(BAYER4, (H // 4 + 1, W // 4 + 1))[:H, :W]
    if not spec:
        return (np.clip(img, 0, 1) * 255).astype(np.uint8)
    if isinstance(spec, (int, float)):
        arr = img * 255 + bay[..., None] * 18 * dither
        pim = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')
        pim = pim.quantize(colors=int(spec), method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        return np.asarray(pim.convert('RGB'))
    name = spec if isinstance(spec, str) else None
    cols = np.array([_rgb(c) for c in (PALETTES[spec] if name else spec)], np.float32)
    if levels:
        # few-colour palettes need the full tonal range or dark scenes collapse into one shade
        l = _lum(img)
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

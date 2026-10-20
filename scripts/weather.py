"""Weather for the ai-raster-scene renderer: rain, snow, splashes, embers, ash, leaves,
fireflies, dust and spores, as particles placed in the world in front of the camera.

Every particle has a real position and depth, so it is hidden behind anything nearer, shrinks
and fades with distance, fades into fog like everything else, never sits inside a wall, and the
outdoor kinds (rain, snow, leaves, splashes, dust) never fall under a roof. Handed a frame
without its 3D context (post-processing on its own), the particles spread over the screen.

Each effect is a post effect (`"post": [{"fx": "rain", ...}]`); see references/scene_format.md.
"""
import math

import numpy as np
from PIL import Image, ImageDraw


def _rgb(c, default):
    c = default if c is None else c
    if isinstance(c, str):
        c = c.lstrip('#')
        return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
    return np.array(c, np.float32)


def place(ctx, rng, n, zmin, zmax, near=0.6, far=22.0, outdoors=True):
    """`n` candidate particles spread evenly by distance through the view (so the near ones, big
    enough to read, are as common as the far ones that make the haze of a downpour); returns the
    survivors as screen x, screen y, depth t, height z and a 0-1 fade.

    A particle is dropped if something nearer covers its pixel, if it would be inside a wall, or
    (`outdoors`) if it is under a roof.
    """
    H, W = ctx['shape']
    u = rng.random(n)
    t = near + u * (far - near)
    sx = rng.random(n) * W
    z = zmin + rng.random(n) * (zmax - zmin)
    r = ctx.get('rays')
    if r is None:                                  # no 3D frame: spread them over the screen
        sy = rng.random(n) * H
        return sx, sy, t, z, np.clip(3.0 / t, 0.35, 1.0)
    sy = r['horizon'] - (z - r['camz']) * r['proj'] / t
    keep = (sy >= 0) & (sy < H)
    col = np.clip(sx.astype(int), 0, W - 1)
    row = np.clip(sy.astype(int), 0, H - 1)
    keep &= t < ctx['depth'][row, col]
    world = ctx['world']
    wx = r['px'] + r['rdx'][col] * t
    wy = r['py'] + r['rdy'][col] * t
    cx, cy = np.floor(wx).astype(int), np.floor(wy).astype(int)
    inb = (cx >= 0) & (cy >= 0) & (cx < world.mw) & (cy < world.mh)
    cxc, cyc = np.clip(cx, 0, world.mw - 1), np.clip(cy, 0, world.mh - 1)
    keep &= ~(inb & (world.solid_h[cyc, cxc] > z))
    if outdoors:
        keep &= ~(inb & (world.ceil_tid[cyc, cxc] >= 0) & (z < world.ceil_h))
    sx, sy, t, z = sx[keep], sy[keep], t[keep], z[keep]
    fade = np.clip(3.0 / t, 0.35, 1.0) * through_fog(ctx, sy, sx, t)
    return sx, sy, t, z, fade


def through_fog(ctx, sy, sx, t):
    """How much of a particle at depth t survives the scene's fog on its way to the eye."""
    vol = ctx.get('fog_t')
    if vol is not None:                            # the volumetric pass's own transmittance
        tt, tv = vol
        H, W = ctx['shape']
        row = np.clip(sy.astype(int), 0, min(H, tv.shape[1]) - 1)
        col = np.clip(sx.astype(int), 0, min(W, tv.shape[2]) - 1)
        k = np.clip(np.searchsorted(tt, t), 1, len(tt) - 1)
        f = np.clip((t - tt[k - 1]) / np.maximum(tt[k] - tt[k - 1], 1e-6), 0, 1)
        return tv[k - 1, row, col] * (1 - f) + tv[k, row, col] * f
    return np.exp(-float(ctx.get('fog_d', 0.0)) * t)


def _proj(ctx):
    r = ctx.get('rays')
    return float(r['proj']) if r is not None else ctx['shape'][1] * 0.75


def _composite(img, layer, mode='over'):
    """Blend an RGBA uint8 layer into the float frame: 'over' covers, 'add' glows."""
    a = np.asarray(layer, np.float32) / 255
    if mode == 'add':
        return img + a[..., :3] * a[..., 3:4]
    return img * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]


def _box(x, y, s, extra_w=0):
    """An s-pixel square at (x, y) in whole pixels (PIL rounds float corners unevenly)."""
    x0, y0, n = int(x), int(y), max(1, int(round(s)))
    return [x0, y0, x0 + n - 1 + extra_w, y0 + n - 1]


def _rgba(c, alpha):
    return tuple(int(v * 255) for v in np.clip(c, 0, 1)) + (int(max(0, min(1, alpha)) * 255),)


# ------------------------------------------------------------------ the effects

def rain(img, p, ctx):
    """Streaks of falling rain. `density` 1, `length` 7 (pixels for a drop about two units
    away; near drops are longer), `angle` 12 (degrees of slant from the wind), `opacity` 0.35."""
    H, W = img.shape[:2]
    ctx = dict(ctx, shape=(H, W))
    rng = np.random.default_rng(ctx['seed'] + 2)
    proj = _proj(ctx)
    sx, sy, t, z, fade = place(ctx, rng, int(2400 * float(p.get('density', 1.0))), 0.0, 3.2, 0.6, 18.0)
    ln = float(p.get('length', 7)) * 2.0 / t * (proj / 246.0)        # pixels at this depth
    slant = math.tan(math.radians(float(p.get('angle', 12))))
    col = _rgb(p.get('color'), [0.75, 0.8, 0.9])
    op = float(p.get('opacity', 0.35))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, l, f, wdt in zip(sx, sy, ln, fade, (t < 1.6).astype(int) + 1):
        d.line([(x, y), (x + slant * l, y + l)], fill=_rgba(col, op * f * (0.6 + 0.4 * rng.random())), width=int(wdt))
    return _composite(img, layer)


def snow(img, p, ctx):
    """Falling snow. `count` 260 (about as many flakes as the screen-space version showed),
    `size` 1 (flake size at two units), `wind` 0 (-1 to 1, drift), `opacity` 0.85."""
    H, W = img.shape[:2]
    ctx = dict(ctx, shape=(H, W))
    rng = np.random.default_rng(ctx['seed'] + 3)
    proj = _proj(ctx)
    sx, sy, t, z, fade = place(ctx, rng, int(float(p.get('count', 260)) * 4.5), 0.0, 3.2, 0.6, 16.0)
    size = float(p.get('size', 1.0)) * 0.05 * proj / t
    col = _rgb(p.get('color'), [0.95, 0.97, 1.0])
    op = float(p.get('opacity', 0.85))
    drift = float(p.get('wind', 0.0))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, s, f in zip(sx, sy, size, fade):
        s = max(1.0, min(4.0, s))
        a = op * f * (0.55 + 0.45 * rng.random())
        if drift and s >= 2:                         # big near flakes streak a little in the wind
            d.line([(x, y), (x - drift * s * 1.5, y - s * 0.8)], fill=_rgba(col, a * 0.5), width=1)
        d.rectangle(_box(x, y, s), fill=_rgba(col, a))
    return _composite(img, layer)


def splashes(img, p, ctx):
    """Rain hitting the ground: little crowns on open floors, bigger near the camera.
    `density` 1, `color`, `opacity` 0.5. Needs the 3D frame (nothing to land on otherwise)."""
    r = ctx.get('rays')
    if r is None:
        return img
    H, W = img.shape[:2]
    rng = np.random.default_rng(ctx['seed'] + 5)
    n = int(170 * float(p.get('density', 1.0)))
    sx = rng.random(n) * W
    sy = r['horizon'] + 1 + rng.random(n) * max(1.0, H - r['horizon'] - 1)
    col, row = np.clip(sx.astype(int), 0, W - 1), np.clip(sy.astype(int), 0, H - 1)
    t = r['camz'] * r['proj'] / np.maximum(sy - r['horizon'], 1e-3)       # where the floor would be
    hit = np.abs(ctx['depth'][row, col] - t) < 0.06 * t                    # and it is the floor
    world = ctx['world']
    wx, wy = r['px'] + r['rdx'][col] * t, r['py'] + r['rdy'][col] * t
    cx = np.clip(np.floor(wx).astype(int), 0, world.mw - 1)
    cy = np.clip(np.floor(wy).astype(int), 0, world.mh - 1)
    hit &= (world.ceil_tid[cy, cx] < 0) & ~world.void[cy, cx] & (t < 18)
    c = _rgb(p.get('color'), [0.8, 0.85, 0.92])
    op = float(p.get('opacity', 0.3))
    fade = np.clip(3.0 / t, 0.3, 1.0) * through_fog(dict(ctx, shape=(H, W)), sy, sx, t)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, tt, f in zip(sx[hit], sy[hit], t[hit], fade[hit]):
        s = max(0.5, min(2.5, 0.035 * r['proj'] / tt))
        a = _rgba(c, op * f)
        if s < 1:                                    # far off, a splash is a fleck
            d.point([(int(x), int(y))], fill=_rgba(c, op * f * 0.7))
            continue
        d.line([(x - s, y), (x + s, y)], fill=a, width=1)
        if s >= 1.8:                                 # close by, a crown: two drops thrown up
            d.point([(x - s * 0.6, y - s * 0.8), (x + s * 0.6, y - s * 0.8)], fill=a)
    return _composite(img, layer)


def _glow_dots(img, ctx, rng, n, zmin, zmax, near, far, colours, size, glow, outdoors, rise=0.0):
    """Shared by embers, fireflies and spores: bright cores with a soft additive halo. They give
    off light: they are added to the frame's emission too, for a light bloom later in the list."""
    H, W = img.shape[:2]
    shared, ctx = ctx, dict(ctx, shape=(H, W))
    proj = _proj(ctx)
    sx, sy, t, z, fade = place(ctx, rng, n, zmin, zmax, near, far, outdoors)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, tt, f in zip(sx, sy, t, fade):
        c = colours[int(rng.integers(len(colours)))]
        s = max(1.0, min(3.0, size * 0.03 * proj / tt))
        if glow > 0:                                 # a soft cross of light round the core
            h = max(1, int(round(s)))
            for dx, dy in ((-h, 0), (h, 0), (0, -h), (0, h)):
                d.rectangle(_box(x + dx, y + dy, s), fill=_rgba(c, min(1.0, 0.35 * glow) * f))
        if rise:                                     # a short trail below a rising spark
            d.line([(x, y), (x + rng.normal() * 0.6, y + rise * s * 2.5)], fill=_rgba(c, 0.45 * f), width=1)
        d.rectangle(_box(x, y, s), fill=_rgba(c, 0.95 * f))
    if shared.get('emission') is not None:
        shared['emission'] = _composite(shared['emission'], layer, 'add')
    return _composite(img, layer, 'add')


def embers(img, p, ctx):
    """Glowing sparks drifting up: fires, burning towns, forges. `count` 80, `color`."""
    rng = np.random.default_rng(ctx['seed'] + 7)
    base = _rgb(p.get('color'), [1.0, 0.55, 0.18])
    cols = [base, np.clip(base * [1.0, 1.4, 1.6], 0, 1), base * 0.8]
    return _glow_dots(img, ctx, rng, int(float(p.get('count', 80)) * 3), 0.0, 2.6, 0.8, 14.0, cols,
                      float(p.get('size', 1.0)), float(p.get('glow', 1.0)), False, rise=1.0)


def fireflies(img, p, ctx):
    """Little lights drifting low over the ground: summer nights, gardens, bogs. `count` 40."""
    rng = np.random.default_rng(ctx['seed'] + 11)
    base = _rgb(p.get('color'), [0.85, 1.0, 0.45])
    return _glow_dots(img, ctx, rng, int(float(p.get('count', 40)) * 3), 0.1, 1.4, 1.2, 12.0, [base, base * 0.85],
                      float(p.get('size', 1.0)), float(p.get('glow', 1.5)), False)


def spores(img, p, ctx):
    """Glowing motes hanging in the air: alien forests, dreams, magic. `count` 70, `colors`."""
    rng = np.random.default_rng(ctx['seed'] + 13)
    cols = [_rgb(c, None) for c in p.get('colors', [[0.5, 1.0, 0.95], [1.0, 0.55, 0.9], [0.9, 0.9, 1.0]])]
    return _glow_dots(img, ctx, rng, int(float(p.get('count', 70)) * 3), 0.1, 2.6, 1.0, 14.0, cols,
                      float(p.get('size', 1.0)), float(p.get('glow', 1.2)), False)


def ash(img, p, ctx):
    """Ash drifting down: grey flakes, some pale, some dark. `count` 300, `wind` 0.2."""
    H, W = img.shape[:2]
    ctx = dict(ctx, shape=(H, W))
    rng = np.random.default_rng(ctx['seed'] + 17)
    proj = _proj(ctx)
    sx, sy, t, z, fade = place(ctx, rng, int(float(p.get('count', 300)) * 4), 0.0, 3.0)
    tones = [np.array(v, np.float32) for v in ([0.75, 0.72, 0.7], [0.45, 0.43, 0.42], [0.25, 0.24, 0.24])]
    drift = float(p.get('wind', 0.2))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, tt, f in zip(sx, sy, t, fade):
        s = max(1.0, min(3.0, 0.04 * proj / tt))
        c = tones[int(rng.integers(3))]
        d.rectangle(_box(x, y, s, int(drift > 0.3)), fill=_rgba(c, 0.8 * f))
    return _composite(img, layer)


def leaves(img, p, ctx):
    """Autumn leaves falling and tumbling. `count` 120, `wind` 0.4, `colors`."""
    H, W = img.shape[:2]
    ctx = dict(ctx, shape=(H, W))
    rng = np.random.default_rng(ctx['seed'] + 19)
    proj = _proj(ctx)
    sx, sy, t, z, fade = place(ctx, rng, int(float(p.get('count', 120)) * 4), 0.0, 3.0, 0.6, 16.0)
    cols = [_rgb(c, None) for c in p.get('colors', [[0.85, 0.42, 0.12], [0.72, 0.2, 0.1], [0.9, 0.7, 0.2],
                                                    [0.5, 0.32, 0.14]])]
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, tt, f in zip(sx, sy, t, fade):
        s = max(1.0, min(4.0, 0.09 * proj / tt))
        c = cols[int(rng.integers(len(cols)))]
        a = rng.random() * math.pi
        dx, dy = math.cos(a) * s, math.sin(a) * s * 0.45      # a leaf seen at an angle
        d.polygon([(x - dx, y - dy), (x - dy * 0.4, y + dx * 0.4), (x + dx, y + dy), (x + dy * 0.4, y - dx * 0.4)],
                  fill=_rgba(c, 0.95 * f))
    return _composite(img, layer)


def dust(img, p, ctx):
    """Wind-driven dust or sand: long faint streaks low over the ground and a tint in the air.
    `density` 1, `wind` 1 (-1 blows left), `color`, `haze` 0.12."""
    H, W = img.shape[:2]
    ctx = dict(ctx, shape=(H, W))
    rng = np.random.default_rng(ctx['seed'] + 23)
    proj = _proj(ctx)
    c = _rgb(p.get('color'), [0.78, 0.62, 0.42])
    haze = float(p.get('haze', 0.12))
    img = img * (1 - haze) + c * haze
    sx, sy, t, z, fade = place(ctx, rng, int(1600 * float(p.get('density', 1.0))), 0.0, 2.2)
    wind = float(p.get('wind', 1.0))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x, y, tt, f in zip(sx, sy, t, fade):
        ln = min(40.0, 0.5 * proj / tt) * (0.5 + rng.random())
        d.line([(x, y), (x + wind * ln, y + abs(wind) * ln * 0.08)], fill=_rgba(c * 1.1, 0.4 * f), width=1)
    return _composite(img, layer)


EFFECTS = {'rain': rain, 'snow': snow, 'splashes': splashes, 'embers': embers, 'fireflies': fireflies,
           'spores': spores, 'ash': ash, 'leaves': leaves, 'dust': dust}

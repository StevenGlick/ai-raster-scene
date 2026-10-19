"""Procedural 90s-style texture, sprite and sky library for the ai-raster-scene renderer.

Every texture is a float32 array (64, 64, 3) in 0..1, tileable.
Some textures carry an emissive mask (64, 64) in 0..1: those texels ignore scene lighting
(lit windows, glowing runes). Sprites are (H, W, 4) RGBA arrays plus an emissive mask.
Everything is deterministic: the same name always produces the same pixels.
"""
import numpy as np
from PIL import Image, ImageDraw

T = 64  # texture size


def _rng(name):
    seed = 0
    for ch in name:
        seed = (seed * 131 + ord(ch)) % (2**32)
    return np.random.default_rng(seed)


def vnoise(size, cells, rng):
    """Tileable smooth value noise in 0..1."""
    g = rng.random((cells, cells))
    x = np.arange(size) * cells / size
    x0 = np.floor(x).astype(int) % cells
    x1 = (x0 + 1) % cells
    f = x - np.floor(x)
    f = f * f * (3 - 2 * f)
    a = g[np.ix_(x0, x0)]
    b = g[np.ix_(x0, x1)]
    c = g[np.ix_(x1, x0)]
    d = g[np.ix_(x1, x1)]
    fy = f[:, None]
    fx = f[None, :]
    top = a * (1 - fx) + b * fx
    bot = c * (1 - fx) + d * fx
    return top * (1 - fy) + bot * fy


def fbm(size, rng, base=4, octaves=4):
    out = np.zeros((size, size))
    amp, tot = 1.0, 0.0
    cells = base
    for _ in range(octaves):
        out += vnoise(size, min(cells, size), rng) * amp
        tot += amp
        amp *= 0.5
        cells *= 2
    return out / tot


def col(hexstr):
    hexstr = hexstr.lstrip('#')
    return np.array([int(hexstr[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)


def shade(base, n, amt=0.25):
    """Apply a noise field n (0..1) to a base colour."""
    return np.clip(base[None, None, :] * (1 - amt + 2 * amt * n[..., None]), 0, 1)


def grain(img, rng, amt=0.06):
    return np.clip(img * (1 - amt + 2 * amt * rng.random(img.shape[:2])[..., None]), 0, 1)


# ---------------------------------------------------------------- wall textures

def tex_brick(name, mortar='#5a5048', c1='#7a3a2c', c2='#5e2c22', bw=16, bh=8):
    rng = _rng(name)
    img = np.zeros((T, T, 3))
    n = fbm(T, rng, 8, 3)
    m = col(mortar)
    for row in range(T // bh):
        off = (bw // 2) * (row % 2)
        for bx in range(-1, T // bw + 1):
            x0 = bx * bw + off
            c = col(c1) * (1 - rng.random() * 0.5) + col(c2) * rng.random() * 0.5
            for y in range(row * bh, row * bh + bh):
                for x in range(x0, x0 + bw):
                    img[y, x % T] = c
        img[row * bh, :] = m
    for row in range(T // bh):
        off = (bw // 2) * (row % 2)
        for bx in range(T // bw + 1):
            img[row * bh:row * bh + bh, (bx * bw + off) % T] = m
    return grain(img * (0.8 + 0.4 * n[..., None]), rng, 0.08)


def tex_stone(name, c='#8a8578', mortar='#4a4740'):
    rng = _rng(name)
    img = np.zeros((T, T, 3))
    base = col(c)
    n = fbm(T, rng, 8, 4)
    rows = [0, 20, 36, 52, 64]
    for i in range(len(rows) - 1):
        y0, y1 = rows[i], rows[i + 1]
        x = (i * 13) % 24
        widths = [22, 30, 26, 18, 28]
        k = 0
        while x < T + 32:
            w = widths[(k + i) % len(widths)]
            v = 0.8 + rng.random() * 0.35
            for xx in range(x, x + w):
                img[y0:y1, xx % T] = base * v
            img[y0:y1, x % T] = col(mortar)
            x += w
            k += 1
        img[y0, :] = col(mortar)
    img = img * (0.75 + 0.5 * n[..., None])
    return grain(np.clip(img, 0, 1), rng, 0.08)


def tex_plaster(name, c='#c9bb98', grime='#6b5a40', grime_amt=0.5):
    rng = _rng(name)
    n = fbm(T, rng, 4, 5)
    img = shade(col(c), n, 0.12)
    # water stains running down from the top
    streak = vnoise(T, 16, rng)[0:1, :].repeat(T, 0)
    fade = np.linspace(1, 0.2, T)[:, None]
    stain = np.clip((streak - 0.55) * 3, 0, 1) * fade * grime_amt
    img = img * (1 - stain[..., None]) + col(grime) * stain[..., None]
    # dirty baseboard band
    img[-6:] = img[-6:] * 0.55
    return grain(img, rng, 0.05)


def tex_hospital(name):
    """Pale green wainscot tiles below, stained cream plaster above (1930s ward)."""
    rng = _rng(name)
    top = tex_plaster(name + 'p', '#d8d0b4', '#7a6a48', 0.6)
    img = top.copy()
    n = fbm(T, rng, 8, 3)
    tile = col('#7fa58f')
    for y in range(36, T):
        for x in range(T):
            g = (x % 8 == 0) or ((y - 36) % 8 == 0)
            img[y, x] = col('#4c5c50') if g else tile * (0.85 + 0.3 * n[y, x])
    img[34:37] = col('#3e4a40')
    return grain(img, rng, 0.04)


def tex_tile(name, c='#d8d8cc', grout='#7a7a70', size=8):
    rng = _rng(name)
    n = fbm(T, rng, 8, 3)
    img = np.zeros((T, T, 3))
    for y in range(T):
        for x in range(T):
            if x % size == 0 or y % size == 0:
                img[y, x] = col(grout)
            else:
                img[y, x] = col(c) * (0.85 + 0.3 * n[y, x])
    return grain(img, rng, 0.04)


def tex_wood_panel(name, c='#5a3a22'):
    rng = _rng(name)
    img = np.zeros((T, T, 3))
    base = col(c)
    for x in range(T):
        stripe = 0.85 + 0.25 * np.sin(x * 0.9 + rng.random() * 0.2)
        img[:, x] = base * stripe
    g = vnoise(T, 32, rng)
    img *= (0.8 + 0.4 * g[..., None])
    for x in (0, 16, 32, 48):
        img[:, x] = img[:, x] * 0.45
    img[0:3] *= 0.6
    img[28:31] = img[28:31] * 0.6 + col('#8a6a3a') * 0.3
    img[-4:] *= 0.5
    return grain(np.clip(img, 0, 1), rng, 0.05)


def tex_planks(name, c='#6e5034', horizontal=True):
    rng = _rng(name)
    img = np.zeros((T, T, 3))
    base = col(c)
    grainf = vnoise(T, 64, rng)
    for p in range(8):
        v = 0.75 + rng.random() * 0.4
        img[p * 8:(p + 1) * 8, :] = base * v
        img[p * 8, :] = base * 0.35
        seam = int(rng.random() * T)
        img[p * 8:(p + 1) * 8, seam] = base * 0.35
    img *= (0.85 + 0.3 * grainf.T[..., None] if horizontal else 1)
    if not horizontal:
        img = img.transpose(1, 0, 2)
    return grain(np.clip(img, 0, 1), rng, 0.06)


def tex_concrete(name, c='#8a8a84'):
    rng = _rng(name)
    n = fbm(T, rng, 4, 5)
    img = shade(col(c), n, 0.2)
    img[::32, :] *= 0.6  # pour lines
    spots = rng.random((T, T)) > 0.985
    img[spots] *= 0.5
    return grain(img, rng, 0.08)


def tex_rock(name, c='#5a544c'):
    rng = _rng(name)
    n = fbm(T, rng, 4, 5)
    ridges = np.abs(vnoise(T, 8, rng) - 0.5) * 2
    v = 0.55 + 0.6 * n - 0.25 * (ridges < 0.12)
    img = col(c)[None, None, :] * v[..., None]
    # drill marks from blasting
    for x in (10, 41):
        img[:, x] *= 0.7
    return grain(np.clip(img, 0, 1), rng, 0.1)


def tex_metal_door(name, c='#4a4e52'):
    rng = _rng(name)
    n = fbm(T, rng, 8, 3)
    img = shade(col(c), n, 0.15)
    img[0:3] *= 0.5; img[-3:] *= 0.5; img[:, 0:3] *= 0.5; img[:, -3:] *= 0.5
    for y in (8, 32, 56):
        for x in (8, 56):
            img[y - 1:y + 2, x - 1:x + 2] = col('#7a7e82')
    img[30:34, 6:58] *= 0.6  # crossbar
    img[40:46, 26:38] = col('#2a2c2e')  # lock plate
    img[42:45, 31:33] = col('#8a7a50')
    rust = np.clip((fbm(T, rng, 4, 4) - 0.6) * 4, 0, 1)
    img = img * (1 - rust[..., None]) + col('#6a3a22') * rust[..., None]
    return grain(img, rng, 0.06)


def tex_corrugated(name, c='#6a6a62'):
    rng = _rng(name)
    img = np.zeros((T, T, 3))
    for x in range(T):
        img[:, x] = col(c) * (0.7 + 0.35 * np.sin(x * np.pi / 4))
    rust = np.clip((fbm(T, rng, 4, 4) - 0.55) * 3, 0, 1)
    img = img * (1 - rust[..., None]) + col('#7a4528') * rust[..., None]
    img[:, :] *= np.linspace(0.85, 1.0, T)[:, None, None]
    return grain(np.clip(img, 0, 1), rng, 0.05)


def tex_hedge(name):
    rng = _rng(name)
    n = fbm(T, rng, 16, 3)
    leaves = rng.random((T, T))
    img = col('#2c4a26')[None, None, :] * (0.5 + 0.8 * n[..., None])
    img[leaves > 0.8] = col('#4a6e36')
    img[leaves < 0.1] = col('#16241a')
    return img


def tex_window(name, wall='#8a8578', lit=True, frame='#3a3028', glass_on='#f0c860', glass_off='#1c2228', style='stone'):
    """A facade texture: wall material with a 4-pane window. Returns (rgb, emissive)."""
    base = tex_stone(name + 'w', wall) if style == 'stone' else tex_plaster(name + 'w', wall, '#5a4a38', 0.4)
    img = base.copy()
    em = np.zeros((T, T))
    x0, x1, y0, y1 = 16, 48, 10, 50
    img[y0 - 2:y1 + 2, x0 - 2:x1 + 2] = col(frame)
    rng = _rng(name)
    for (a, b, c, d) in [(x0, 31, y0, 29), (33, x1, y0, 29), (x0, 31, 31, y1), (33, x1, 31, y1)]:
        if lit:
            g = np.clip(col(glass_on) * (0.8 + 0.3 * rng.random()), 0, 1)
            img[c:d, a:b] = g
            em[c:d, a:b] = 1.0
        else:
            img[c:d, a:b] = col(glass_off)
            img[c:c + 3, a:a + 3] = col('#4a5a68')  # moon glint
    img[y1 + 2:y1 + 5, x0 - 4:x1 + 4] = col('#a09a8a')  # sill
    return img, em


def tex_bookshelf(name):
    rng = _rng(name)
    img = tex_wood_panel(name + 'b', '#3e2818')
    palette = ['#6a2a22', '#2a3a5a', '#3a4a2a', '#5a4a2a', '#4a2a3a', '#1e1e1e', '#7a6a4a']
    for shelf in range(4):
        y0 = shelf * 16 + 3
        x = 2
        while x < 62:
            w = int(2 + rng.random() * 4)
            h = int(9 + rng.random() * 4)
            c = col(palette[int(rng.random() * len(palette))]) * (0.7 + 0.4 * rng.random())
            img[y0 + 13 - h:y0 + 13, x:min(x + w, 62)] = c
            img[y0 + 13 - h + 2, x:min(x + w, 62)] = col('#b09a5a') * 0.7
            x += w + (1 if rng.random() > 0.8 else 0)
        img[y0 + 13:y0 + 16, :] = col('#2a1a10')
    return img


def tex_wallpaper(name, c='#4a2a2a', pattern='#6a4030'):
    rng = _rng(name)
    img = tex_plaster(name + 'wp', c, '#2a1a1a', 0.4)
    for y in range(T):
        for x in range(T):
            dx = (x % 16) - 8
            dy = (y % 16) - 8
            if abs(abs(dx) + abs(dy) - 5) < 1 or (abs(dx) < 1 and abs(dy) < 1):
                img[y, x] = col(pattern)
    img[-10:] = tex_wood_panel(name + 'wb', '#3a2416')[-10:]
    return grain(img, rng, 0.04)


def tex_curtain(name, c='#6a1a1a'):
    rng = _rng(name)
    img = np.zeros((T, T, 3))
    for x in range(T):
        img[:, x] = col(c) * (0.55 + 0.45 * (0.5 + 0.5 * np.sin(x * np.pi / 8)))
    img *= np.linspace(1.0, 0.75, T)[:, None, None]
    return grain(img, rng, 0.04)


def tex_runes(name, base='rock'):
    """Rock wall with a glowing red cult sigil. Returns (rgb, emissive)."""
    img = tex_rock(name + 'r')
    em = np.zeros((T, T))
    im = Image.new('L', (T * 4, T * 4), 0)
    d = ImageDraw.Draw(im)
    cx, cy, r = 128, 120, 70
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=255, width=8)
    d.polygon([(cx, cy - 58), (cx + 50, cy + 32), (cx - 50, cy + 32)], outline=255, width=7)
    d.line([(cx, cy - 92), (cx, cy + 96)], fill=255, width=7)
    d.line([(cx - 30, cy + 70), (cx + 30, cy + 70)], fill=255, width=6)
    m = np.asarray(im.resize((T, T), Image.BILINEAR)) / 255.0
    m = np.clip(m * 1.8, 0, 1)
    img = img * (1 - m[..., None]) + col('#c0281e')[None, None, :] * m[..., None]
    em = m
    return img, em


# ---------------------------------------------------------------- floor/ceiling textures

def tex_checker(name, a='#d8d4c8', b='#2a2a2a', size=16):
    rng = _rng(name)
    img = np.zeros((T, T, 3))
    for y in range(T):
        for x in range(T):
            img[y, x] = col(a) if ((x // size) + (y // size)) % 2 == 0 else col(b)
    n = fbm(T, rng, 4, 4)
    return grain(img * (0.8 + 0.3 * n[..., None]), rng, 0.04)


def tex_linoleum(name, c='#8a8a6e'):
    rng = _rng(name)
    n = fbm(T, rng, 8, 4)
    img = np.zeros((T, T, 3))
    for y in range(T):
        for x in range(T):
            img[y, x] = col(c) * (0.85 + 0.25 * n[y, x])
            if x % 32 == 0 or y % 32 == 0:
                img[y, x] *= 0.6
    flecks = rng.random((T, T)) > 0.96
    img[flecks] *= 1.25
    return grain(np.clip(img, 0, 1), rng, 0.03)


def tex_grass(name):
    rng = _rng(name)
    n = fbm(T, rng, 8, 4)
    blades = rng.random((T, T))
    img = col('#2e4a24')[None, None, :] * (0.55 + 0.7 * n[..., None])
    img[blades > 0.85] = col('#4a6a32')
    img[blades < 0.06] = col('#1a2a16')
    return img


def tex_gravel(name, c='#8a8070'):
    rng = _rng(name)
    n = fbm(T, rng, 16, 3)
    img = col(c)[None, None, :] * (0.6 + 0.6 * n[..., None])
    s = rng.random((T, T))
    img[s > 0.9] = col('#b0a890')
    img[s < 0.08] = col('#4a4438')
    return img


def tex_cobble(name, c='#6a665e'):
    rng = _rng(name)
    img = np.zeros((T, T, 3))
    n = fbm(T, rng, 8, 3)
    pts = rng.random((22, 2)) * T
    yy, xx = np.mgrid[0:T, 0:T]
    best = np.full((T, T), 1e9)
    second = np.full((T, T), 1e9)
    idx = np.zeros((T, T), int)
    for i, (py, px) in enumerate(pts):
        for oy in (-T, 0, T):
            for ox in (-T, 0, T):
                d = np.hypot(yy - py - oy, xx - px - ox)
                upd = d < best
                second = np.where(upd, best, np.minimum(second, d))
                idx = np.where(upd, i, idx)
                best = np.where(upd, d, best)
    edge = (second - best) < 1.6
    shades = 0.7 + rng.random(len(pts)) * 0.45
    img = col(c)[None, None, :] * shades[idx][..., None] * (0.85 + 0.3 * n[..., None])
    img[edge] = col('#2a2824')
    return np.clip(img, 0, 1)


def tex_water(name):
    rng = _rng(name)
    n = fbm(T, rng, 4, 4)
    img = col('#0e2a32')[None, None, :] * (0.7 + 0.6 * n[..., None])
    for y in range(T):
        off = int(4 * np.sin(y * 0.4))
        for x in range(0, T, 16):
            if (y + x // 16 * 5) % 11 == 0:
                img[y, (x + off) % T:(x + off) % T + 6] = col('#2a5a66')
    return img


def tex_carpet(name, c='#6a1e22', border='#b08a3a'):
    rng = _rng(name)
    img = shade(col(c), fbm(T, rng, 16, 2), 0.15)
    for y in range(T):
        for x in range(T):
            dx, dy = abs(x - 32), abs(y - 32)
            if dx + dy == 20 or dx + dy == 21 or (dx + dy) == 8:
                img[y, x] = col(border)
    return grain(img, rng, 0.08)


def tex_sand(name):
    rng = _rng(name)
    n = fbm(T, rng, 4, 5)
    return grain(col('#c2b088')[None, None, :] * (0.8 + 0.3 * n[..., None]), rng, 0.1)


def tex_marble(name, c='#d8d4cc'):
    rng = _rng(name)
    n = fbm(T, rng, 4, 5)
    veins = np.abs(np.sin((np.arange(T)[None, :] + n * 40) * 0.25))
    img = col(c)[None, None, :] * (0.85 + 0.15 * veins[..., None])
    img[veins < 0.08] = col('#8a8478')
    img[0, :] *= 0.6; img[:, 0] *= 0.6
    img[32, :] *= 0.6; img[:, 32] *= 0.6
    return img


def tex_beams(name):
    img = tex_plaster(name + 'c', '#b0a488', '#5a4a38', 0.2)
    wood = tex_planks(name + 'bm', '#4a3220')
    img[0:14] = wood[0:14]
    img[32:46] = wood[32:46]
    return img


def tex_acoustic(name):
    rng = _rng(name)
    img = tex_tile(name + 'a', '#b8b4a4', '#6a6858', 32)
    holes = (np.add.outer(np.arange(T), np.arange(T)) % 4 == 0) & (np.arange(T)[:, None] % 4 == 0)
    img[holes] *= 0.7
    stain = np.clip((fbm(T, rng, 4, 4) - 0.6) * 3, 0, 1)
    return img * (1 - 0.4 * stain[..., None])


# ------------------------------------------------- woodland, weather and industrial

def tex_bark(name, c='#4a3a2a', deep='#241c14', hi='#6e5a42'):
    """Vertical ridged bark: tree trunks, timber palisades."""
    rng = _rng(name)
    n = fbm(T, rng, 8, 4)
    xx = np.arange(T)[None, :] + 5 * fbm(T, _rng(name + 'w'), 3, 2)
    v = 0.5 + 0.5 * np.sin(xx * (2 * np.pi * 7 / T))
    img = col(c)[None, None, :] * (0.6 + 0.6 * v[..., None]) * (0.8 + 0.4 * n[..., None])
    img = np.where((v < 0.16)[..., None], col(deep)[None, None, :] * (0.7 + 0.5 * n[..., None]), img)
    img = np.where((v > 0.92)[..., None], col(hi)[None, None, :] * (0.8 + 0.3 * n[..., None]), img)
    img[rng.random((T, T)) > 0.995] = col(deep)
    return grain(np.clip(img, 0, 1), rng, 0.04)


def tex_foliage(name, c='#1e3a22', hi='#365a2e', deep='#0c1a10'):
    """Dense leaf mass: tree canopies, thickets, overgrown walls."""
    rng = _rng(name)
    n = fbm(T, rng, 12, 4)
    blob = fbm(T, _rng(name + 'b'), 5, 3)
    img = col(c)[None, None, :] * (0.5 + 0.9 * n[..., None]) * (0.6 + 0.7 * blob[..., None])
    s = rng.random((T, T))
    img[s > 0.84] = col(hi)[None, :] * (0.8 + 0.4 * blob[s > 0.84])[:, None]
    img[s < 0.12] = col(deep)
    return np.clip(img, 0, 1)


def tex_moss_stone(name):
    """Stone block wall swallowed by moss patches."""
    rng = _rng(name)
    img = tex_stone(name + 's', '#6e6a60', '#3a3832')
    m = np.clip((fbm(T, rng, 5, 4) - 0.46) * 3.2, 0, 1)
    moss = col('#2e4a2a')[None, None, :] * (0.55 + 0.8 * fbm(T, _rng(name + 'm'), 14, 3)[..., None])
    return np.clip(img * (1 - m[..., None]) + moss * m[..., None], 0, 1)


def tex_ivy(name):
    """Brick under climbing ivy."""
    rng = _rng(name)
    img = tex_brick(name + 'b')
    v = np.clip((fbm(T, rng, 4, 4) - 0.40) * 2.6, 0, 1)
    ivy = col('#24401f')[None, None, :] * (0.5 + 0.9 * fbm(T, _rng(name + 'l'), 16, 3)[..., None])
    ivy[rng.random((T, T)) > 0.87] = col('#3e6a30')
    return np.clip(img * (1 - v[..., None]) + ivy * v[..., None], 0, 1)


def tex_logs(name, c='#6a5134', chink='#3a3028'):
    """Horizontally stacked logs: cabins, lodges, palisade huts."""
    rng = _rng(name)
    n = fbm(T, rng, 10, 4)
    lh = 16
    y = np.arange(T)[:, None]
    t = (y % lh) / lh
    curve = np.sin(np.clip((t - 0.12) / 0.88, 0, 1) * np.pi)
    img = col(c)[None, None, :] * (0.4 + 0.8 * curve[..., None]) * (0.85 + 0.3 * n[..., None])
    img = np.where(((y % lh) < 2)[..., None], col(chink)[None, None, :] * (0.7 + 0.5 * n[..., None]), img)
    img[rng.random((T, T)) > 0.99] = col('#4a3826')
    return grain(np.clip(img, 0, 1), rng, 0.035)


def tex_shingle(name, c='#4a4a4e', edge='#22222a'):
    """Overlapping roof shingles; also reads as a low roofline or a wall top."""
    rng = _rng(name)
    n = fbm(T, rng, 12, 3)
    yy, xx = np.mgrid[0:T, 0:T]
    sw, sh = 16, 8
    off = ((yy // sh) % 2) * (sw // 2)
    u = ((xx + off) % sw) / sw
    v = (yy % sh) / sh
    tone = 0.72 + 0.32 * (((yy // sh) * 7 + ((xx + off) // sw) * 13) % 5) / 4
    img = col(c)[None, None, :] * tone[..., None] * (0.85 + 0.3 * n[..., None]) * (0.62 + 0.62 * v)[..., None]
    img[v > 0.84] *= 0.4
    img[v < 0.14] = np.clip(col(c) * 1.45, 0, 1) * tone[v < 0.14][:, None]
    img[(u < 0.09) | (u > 0.94)] = col(edge)
    return grain(np.clip(img, 0, 1), rng, 0.04)


def tex_rust(name, c='#6a4a32'):
    """Rusted iron sheet with panel seams and bolts."""
    rng = _rng(name)
    n = fbm(T, rng, 6, 4)
    img = col(c)[None, None, :] * (0.55 + 0.8 * n[..., None])
    patch = np.clip((fbm(T, _rng(name + 'p'), 10, 3) - 0.5) * 3, 0, 1)
    img = img * (1 - patch[..., None]) + col('#8a4a22')[None, None, :] * patch[..., None]
    dark = np.clip((0.42 - fbm(T, _rng(name + 'd'), 4, 3)) * 4, 0, 1)
    img *= (1 - 0.55 * dark[..., None])
    yy, xx = np.mgrid[0:T, 0:T]
    img[(xx % 32 == 0) | (yy % 32 == 0)] *= 0.55
    img[np.hypot((xx % 32) - 4, (yy % 32) - 4) < 2.2] = col('#9a9088')
    return grain(np.clip(img, 0, 1), rng, 0.05)


def tex_pipes(name):
    """A bank of vertical pipes on concrete: plant rooms, bunkers, sewers."""
    rng = _rng(name)
    img = tex_concrete(name + 'b', '#4a4a46')
    yy, xx = np.mgrid[0:T, 0:T]
    for cx, r, pc in ((10, 6, '#6a6e72'), (30, 8, '#4a5a4a'), (50, 5, '#7a5a3a')):
        dist = np.abs(xx - cx)
        m = dist <= r
        lit = np.clip(1 - ((dist - r * 0.35) / r) ** 2, 0, 1)
        img[m] = col(pc)[None, :] * (0.4 + 0.8 * lit[m])[:, None]
        band = m & ((yy % 24) < 3)
        img[band] = col(pc)[None, :] * (0.5 + 0.4 * lit[band])[:, None]
    return grain(np.clip(img, 0, 1), rng, 0.03)


def tex_panel(name, c='#8a9098', seam='#4a5056'):
    """Clean riveted steel panelling: labs, bunkers, ships, sci-fi interiors."""
    rng = _rng(name)
    n = fbm(T, rng, 14, 3)
    img = col(c)[None, None, :] * (0.86 + 0.24 * n[..., None])
    yy, xx = np.mgrid[0:T, 0:T]
    img[((xx % 32) < 2) | ((yy % 16) < 1)] = col(seam)
    img[np.hypot((xx % 32) - 6, (yy % 16) - 8) < 1.6] = np.clip(col(c) * 1.3, 0, 1)
    img *= np.linspace(1.05, 0.88, T)[:, None, None]
    return grain(np.clip(img, 0, 1), rng, 0.02)


def tex_needles(name, c='#3a2e1e'):
    """Pine-needle forest floor with patches of undergrowth."""
    rng = _rng(name)
    n = fbm(T, rng, 7, 4)
    img = col(c)[None, None, :] * (0.6 + 0.8 * n[..., None])
    s = rng.random((T, T))
    img[s > 0.88] = col('#5a4628')
    img[s < 0.1] = col('#1e1812')
    img[rng.random((T, T)) > 0.985] = col('#6a5a34')
    g = np.clip((fbm(T, _rng(name + 'g'), 4, 3) - 0.6) * 4, 0, 1)
    img = img * (1 - g[..., None]) + col('#2c4424')[None, None, :] * g[..., None]
    return np.clip(img, 0, 1)


def tex_moss(name, c='#2a4424'):
    """Soft moss ground with stone showing through."""
    rng = _rng(name)
    n = fbm(T, rng, 16, 4)
    img = col(c)[None, None, :] * (0.5 + 0.9 * n[..., None])
    s = rng.random((T, T))
    img[s > 0.9] = col('#4a6e34')
    img[s < 0.08] = col('#16261a')
    stone = np.clip((fbm(T, _rng(name + 's'), 4, 3) - 0.64) * 5, 0, 1)
    img = img * (1 - stone[..., None]) + col('#6a665e')[None, None, :] * stone[..., None]
    return np.clip(img, 0, 1)


def tex_mud(name, c='#4a3a28'):
    """Churned mud with standing water."""
    rng = _rng(name)
    n = fbm(T, rng, 6, 4)
    img = col(c)[None, None, :] * (0.6 + 0.75 * n[..., None])
    pud = np.clip((fbm(T, _rng(name + 'p'), 4, 3) - 0.52) * 4, 0, 1)
    wet = col('#2a3236')[None, None, :] * (0.8 + 0.5 * n[..., None])
    img = img * (1 - pud[..., None]) + wet * pud[..., None]
    img[rng.random((T, T)) > 0.99] = col('#2a2018')
    return grain(np.clip(img, 0, 1), rng, 0.04)


def tex_snow(name, c='#d8dee8'):
    """Fresh snow with blue shadow drifts."""
    rng = _rng(name)
    n = fbm(T, rng, 5, 4)
    img = col(c)[None, None, :] * (0.82 + 0.25 * n[..., None])
    sh = np.clip((0.45 - fbm(T, _rng(name + 's'), 8, 3)) * 3, 0, 1)
    img = img * (1 - 0.3 * sh[..., None]) + col('#9aa8c0')[None, None, :] * 0.3 * sh[..., None]
    img[rng.random((T, T)) > 0.985] = col('#ffffff')
    return np.clip(img, 0, 1)


def tex_asphalt(name, c='#3a3a3c'):
    """Cracked road surface."""
    rng = _rng(name)
    n = fbm(T, rng, 16, 4)
    img = col(c)[None, None, :] * (0.7 + 0.6 * n[..., None])
    g = rng.random((T, T))
    img[g > 0.93] = col('#5a5a5c')
    img[g < 0.05] = col('#1e1e20')
    img[np.abs(fbm(T, _rng(name + 'c'), 3, 4) - 0.5) < 0.016] = col('#18181a')
    return grain(np.clip(img, 0, 1), rng, 0.03)


def tex_grate(name, c='#5a5e60'):
    """Metal walkway grating over darkness."""
    rng = _rng(name)
    n = fbm(T, rng, 12, 3)
    yy, xx = np.mgrid[0:T, 0:T]
    bar = ((xx % 8) < 3) | ((yy % 16) < 3)
    img = np.where(bar[..., None], col(c)[None, None, :] * (0.7 + 0.5 * n[..., None]),
                   col('#14161a')[None, None, :] * np.ones((T, T, 1)))
    img[bar & ((xx % 8) == 2)] *= 0.65
    return grain(np.clip(img, 0, 1), rng, 0.04)


# ------------------------------------------------- see-through (masked) wall textures
# These return (rgb, emissive, alpha): alpha 1 is solid, 0 is a hole the renderer looks through.
# Each is designed for a 1-unit tile; low fences keep their parts in the lower rows, so they read
# correctly on a short wall (a wall shows the bottom of its texture first).


def _iron(rng, a, c):
    """Shade a mask as dark iron: noise, a highlight down each member, the odd rust fleck."""
    n = fbm(T, rng, 10, 3)
    img = col(c)[None, None, :] * (0.8 + 0.35 * n[..., None])
    img[(rng.random((T, T)) > 0.95) & (a > 0)] = col('#6a4028')
    return img


def tex_bars(name, c='#3c3c44'):
    """Jail bars: four thick uprights per unit between a top and a bottom rail."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    a = (((xx % 16) < 5) | (yy < 5) | (yy > 58)).astype(np.float32)
    img = _iron(rng, a, c)
    round_ = 0.7 + 0.55 * np.clip(1 - np.abs((xx % 16) - 1.5) / 3.0, 0, 1)   # lit edge, dark edge
    img = img * np.where((xx % 16) < 5, round_, 1.0)[..., None]
    return np.clip(img, 0, 1), None, a


def tex_fence_iron(name, c='#26262c'):
    """Wrought-iron railings with spear tips, about 0.9 high."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    cx = (xx % 8) - 3.5
    upright = (np.abs(cx) <= 1.0) & (yy >= 8)
    spear = (yy >= 2) & (yy < 9) & (np.abs(cx) <= np.minimum(yy - 2, 9 - yy) * 0.55)
    rails = ((yy >= 12) & (yy <= 13)) | ((yy >= 55) & (yy <= 57))
    a = (upright | spear | rails).astype(np.float32)
    img = _iron(rng, a, c)
    img[spear] *= 1.25
    return np.clip(img, 0, 1), None, a


def tex_chainlink(name, c='#8e949a'):
    """Chain-link mesh between steel posts, with a top rail."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    mesh = (((xx + yy) % 8) < 2) | (((xx - yy) % 8) < 2)
    post = (xx < 3) | (xx > 60)
    a = (mesh | post | (yy < 3)).astype(np.float32)
    n = fbm(T, rng, 12, 3)
    img = col(c)[None, None, :] * (0.75 + 0.4 * n[..., None])
    img[post] = col('#5a5e62') * (0.85 + 0.3 * n[post])[:, None]
    return np.clip(img, 0, 1), None, a


def tex_railing(name, c='#5a4028'):
    """A waist-high timber railing, about 0.37 high: jetties, walkways, balconies."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    posts = (((xx % 32) < 4) & (yy >= 40))
    top = (yy >= 40) & (yy < 44)
    mid = (yy >= 51) & (yy < 54)
    a = (posts | top | mid).astype(np.float32)
    wood = tex_planks(name + 'w', c)
    img = wood * (0.9 + 0.2 * rng.random((T, T)))[..., None]
    img[top] *= 1.15
    return np.clip(img, 0, 1), None, a


def tex_picket(name, c='#d8d4c8'):
    """A white picket fence, about 0.45 high, pointed boards on two rails."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    cx = (xx % 8) - 3.5
    board = (np.abs(cx) <= 2.5) & (yy >= 40) & (yy <= 61)
    point = (yy >= 35) & (yy < 40) & (np.abs(cx) <= (yy - 35) * 0.6)
    rails = ((yy >= 44) & (yy <= 46)) | ((yy >= 55) & (yy <= 57))
    a = (board | point | rails).astype(np.float32)
    n = fbm(T, rng, 10, 3)
    img = col(c)[None, None, :] * (0.82 + 0.25 * n[..., None])
    dirt = np.clip((yy - 44) / 20.0, 0, 1)[..., None] * 0.25   # grime splashed up from the ground
    img = img * (1 - dirt)
    img[rails] *= 0.8
    return np.clip(img, 0, 1), None, a


def tex_portcullis(name, c='#30302e'):
    """An iron portcullis grid with spiked feet. Stack it under stone for a castle gate."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    vert = ((xx % 16) >= 6) & ((xx % 16) < 10)
    horiz = ((yy % 16) >= 6) & ((yy % 16) < 10) & (yy < 54)
    spike = vert & (yy >= 54) & (np.abs((xx % 16) - 7.5) <= (63 - yy) * 0.25)
    a = ((vert & (yy < 54)) | horiz | spike).astype(np.float32)
    img = _iron(rng, a, c)
    rivet = vert & horiz & (((xx % 16) == 7) | ((xx % 16) == 8)) & (((yy % 16) == 7) | ((yy % 16) == 8))
    img[rivet] = col('#7a7670')
    return np.clip(img, 0, 1), None, a


def tex_window_broken(name, wall='#7a766c'):
    """A stone wall with a smashed window: frame and a few shards left, the rest open."""
    rng = _rng(name)
    img = tex_stone(name + 's', wall, '#3e3a34')
    a = np.ones((T, T), np.float32)
    x0, x1, y0, y1 = 16, 48, 10, 50
    img[y0 - 2:y1 + 2, x0 - 2:x1 + 2] = col('#3a2c20')                   # frame
    pane = np.zeros((T, T), bool)
    pane[y0:y1, x0:x1] = True
    pane[y0:y1, 31:33] = False                                          # mullion
    pane[29:31, x0:x1] = False                                          # transom
    shards = fbm(T, _rng(name + 'g'), 6, 3) < 0.36                      # what is left of the glass
    hole = pane & ~shards
    a[hole] = 0
    img[pane & shards] = col('#28343c') * 1.2
    return np.clip(img, 0, 1), None, a


def tex_lattice(name, c='#5a4630'):
    """A diagonal timber lattice in a frame: trellises, screens, confessionals."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    strips = (((xx + yy) % 16) < 3) | (((xx - yy) % 16) < 3)
    frame = (xx < 3) | (xx > 60) | (yy < 3) | (yy > 60)
    a = (strips | frame).astype(np.float32)
    wood = tex_planks(name + 'w', c, False)
    img = wood * (0.85 + 0.3 * rng.random((T, T)))[..., None]
    img[frame] *= 0.8
    return np.clip(img, 0, 1), None, a


# ------------------------------------------------- castle, chapel, cave, sewer and winter textures

def tex_castle(name, c='#77736a', mortar='#34312c'):
    """Big rough-cut ashlar blocks: keeps, dungeons, city walls."""
    rng = _rng(name)
    n = fbm(T, rng, 8, 4)
    yy, xx = np.mgrid[0:T, 0:T]
    bh, bw = 16, 32
    row = yy // bh
    off = (row % 2) * (bw // 2)
    bx, by = (xx + off) % bw, yy % bh
    block = ((xx + off) // bw) + row * 7
    tone = 0.78 + 0.32 * ((block * 37 + 11) % 9) / 8.0
    img = col(c)[None, None, :] * tone[..., None] * (0.82 + 0.3 * n[..., None])
    img[(by < 2) | (bx < 2)] *= 1.12               # chiselled edges catch the light...
    img[(by > bh - 3) | (bx > bw - 3)] *= 0.72     # ...and the far edges fall into shadow
    img[(by == 0) | (bx == 0)] = col(mortar)
    img[rng.random((T, T)) > 0.985] *= 0.6
    return grain(np.clip(img, 0, 1), rng, 0.04)


def tex_flagstone(name, c='#6e6a62', grout='#2e2c28'):
    """Large worn paving slabs in staggered rows: castle halls, chapels, courtyards."""
    rng = _rng(name)
    n = fbm(T, rng, 10, 4)
    yy, xx = np.mgrid[0:T, 0:T]
    row = yy // 32
    off = (row % 2) * 16
    bx, by = (xx + off) % 32, yy % 32
    slab = ((xx + off) // 32) % 2 + row * 3
    tone = 0.8 + 0.3 * ((slab * 53 + 7) % 5) / 4.0
    img = col(c)[None, None, :] * tone[..., None] * (0.8 + 0.35 * n[..., None])
    wear = np.clip((fbm(T, _rng(name + 'w'), 4, 3) - 0.55) * 3, 0, 1)
    img = img * (1 - 0.25 * wear[..., None])
    img[(bx < 2) | (by < 2)] = col(grout)
    crack = np.abs(fbm(T, _rng(name + 'c'), 3, 4) - 0.5) < 0.012
    img[crack] *= 0.55
    return grain(np.clip(img, 0, 1), rng, 0.04)


def tex_stained_glass(name, wall='#8a857c'):
    """A pointed-arch window of leaded jewel-coloured glass in a stone wall. Emissive panes."""
    rng = _rng(name)
    img = tex_stone(name + 's', wall, '#4a4740')
    em = np.zeros((T, T), np.float32)
    yy, xx = np.mgrid[0:T, 0:T]
    cx = 31.5
    lower = (np.abs(xx - cx) <= 11) & (yy >= 22) & (yy <= 58)
    arch = (yy < 22) & (yy >= 3) & ((xx - (cx - 11)) ** 2 + (yy - 22) ** 2 <= 22 ** 2) \
        & ((xx - (cx + 11)) ** 2 + (yy - 22) ** 2 <= 22 ** 2)
    win = lower | arch
    grow = np.zeros_like(win)
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            grow |= np.roll(np.roll(win, dy, 0), dx, 1)
    img[grow & ~win] = col('#3a3630')                       # stone surround
    jewels = [col(h) for h in ('#c02030', '#2050c0', '#e0b030', '#30a050', '#8030a0', '#e06020')]
    cell = ((xx + yy) // 8) * 5 + ((xx - yy) // 8) * 3
    pane = np.stack([jewels[int(k) % len(jewels)] for k in cell.ravel()]).reshape(T, T, 3)
    lead = (((xx + yy) % 8) == 0) | (((xx - yy) % 8) == 0) | (np.abs(xx - cx) < 0.6)
    glass = win & ~lead
    shimmer = (0.8 + 0.4 * rng.random((T, T)))[..., None]
    img[glass] = (pane * shimmer)[glass]
    img[win & lead] = col('#1a1814')
    em[glass] = 1.0
    return np.clip(img, 0, 1), em


def tex_ice(name, c='#b6d0dc'):
    """Frozen water: pale, glassy, cracked. Reflective by default."""
    rng = _rng(name)
    n = fbm(T, rng, 5, 4)
    img = col(c)[None, None, :] * (0.78 + 0.3 * n[..., None])
    deep = np.clip((0.45 - fbm(T, _rng(name + 'd'), 6, 3)) * 3, 0, 1)
    img = img * (1 - 0.35 * deep[..., None]) + col('#4a7088')[None, None, :] * 0.35 * deep[..., None]
    crack = np.abs(fbm(T, _rng(name + 'c'), 3, 4) - 0.5) < 0.014
    img[crack] = col('#eef6fa')
    img[rng.random((T, T)) > 0.993] = col('#ffffff')       # trapped bubbles
    return np.clip(img, 0, 1)


def tex_snow_rock(name):
    """Rock with snow lying on its ledges: mountainsides, cliffs, winter walls."""
    rng = _rng(name)
    img = tex_rock(name + 'r', '#5a5650')
    yy = np.mgrid[0:T, 0:T][0]
    lie = np.clip((fbm(T, rng, 6, 4) - 0.5 + (1 - yy / T) * 0.35) * 4, 0, 1)
    snow = col('#dce4ee')[None, None, :] * (0.85 + 0.2 * fbm(T, _rng(name + 's'), 12, 3)[..., None])
    return np.clip(img * (1 - lie[..., None]) + snow * lie[..., None], 0, 1)


def tex_slime_brick(name):
    """Dark sewer brick, wet, with green slime creeping up from the waterline."""
    rng = _rng(name)
    img = tex_brick(name + 'b', '#2e2a26', '#4a3a30', '#3a2c24')
    yy = np.mgrid[0:T, 0:T][0]
    slime = np.clip((fbm(T, rng, 8, 4) - 0.75 + (yy / T) * 0.7) * 3, 0, 1)
    green = col('#3a5a28')[None, None, :] * (0.7 + 0.5 * fbm(T, _rng(name + 'g'), 14, 3)[..., None])
    img = img * (1 - slime[..., None]) + green * slime[..., None]
    wet = np.clip((fbm(T, _rng(name + 'w'), 6, 3) - 0.55) * 4, 0, 1)
    return np.clip(img * (1 - 0.3 * wet[..., None]), 0, 1)


def tex_door_wood(name, c='#5a3c22'):
    """A heavy plank door with iron straps and studs."""
    rng = _rng(name)
    img = tex_planks(name + 'p', c, False)
    yy, xx = np.mgrid[0:T, 0:T]
    straps = ((yy >= 10) & (yy < 15)) | ((yy >= 46) & (yy < 51))
    img[straps] = col('#2e2c2a') * (0.8 + 0.4 * rng.random((T, T)))[straps][:, None]
    studs = straps & ((xx % 8) == 4) & (((yy - 12) % 36 == 0) | ((yy - 48) % 36 == 0))
    img[studs] = col('#8a8478')
    ring = np.abs(np.hypot(xx - 44, yy - 32) - 4) < 1.0
    img[ring] = col('#6a645c')
    img[:, :2] *= 0.6
    img[:, -2:] *= 0.6
    return np.clip(img, 0, 1)


# ---------------------------------------------------------------- registry

def _plain(fn, *a, **k):
    return lambda name: (fn(name, *a, **k), None)


def _em(fn, *a, **k):
    return lambda name: fn(name, *a, **k)


def _masked(fn, *a, **k):
    """A texture with see-through texels: fn returns (rgb, emissive, alpha)."""
    return lambda name: fn(name, *a, **k)


TEXTURES = {
    # walls
    'brick': _plain(tex_brick),
    'brick_dark': _plain(tex_brick, '#3a3430', '#4a2a24', '#2e1e1a'),
    'brick_yellow': _plain(tex_brick, '#6a6050', '#a08a5a', '#7a6640'),
    'stone': _plain(tex_stone),
    'stone_dark': _plain(tex_stone, '#5a5650', '#2e2c28'),
    'stone_pale': _plain(tex_stone, '#b0a890', '#6a6250'),
    'plaster': _plain(tex_plaster),
    'plaster_white': _plain(tex_plaster, '#d8d4c4', '#6a6050', 0.45),
    'hospital_wall': _plain(tex_hospital),
    'tile_white': _plain(tex_tile),
    'tile_green': _plain(tex_tile, '#6a9a80', '#3a5a48'),
    'wood_panel': _plain(tex_wood_panel),
    'planks': _plain(tex_planks),
    'boards': _plain(tex_planks, '#5a4430', False),
    'concrete': _plain(tex_concrete),
    'rock': _plain(tex_rock),
    'rock_wet': _plain(tex_rock, '#3e4446'),
    'iron_door': _plain(tex_metal_door),
    'corrugated': _plain(tex_corrugated),
    'hedge': _plain(tex_hedge),
    'bookshelf': _plain(tex_bookshelf),
    'wallpaper': _plain(tex_wallpaper),
    'wallpaper_green': _plain(tex_wallpaper, '#26402e', '#4a6a40'),
    'curtain': _plain(tex_curtain),
    'curtain_black': _plain(tex_curtain, '#1a1418'),
    'window_lit': _em(tex_window),
    'window_dark': _em(tex_window, lit=False),
    'window_lit_plaster': _em(tex_window, '#c9bb98', style='plaster'),
    'window_dark_plaster': _em(tex_window, '#c9bb98', lit=False, style='plaster'),
    'window_teal': _em(tex_window, '#7a7a74', glass_on='#8ad0c4'),
    'runes': _em(tex_runes),
    'bark': _plain(tex_bark),
    'bark_pine': _plain(tex_bark, '#5a3a28', '#2e1a12', '#8a5a38'),
    'foliage': _plain(tex_foliage),
    'foliage_autumn': _plain(tex_foliage, '#4a3418', '#6e5a24', '#281c0e'),
    'moss_stone': _plain(tex_moss_stone),
    'ivy': _plain(tex_ivy),
    'logs': _plain(tex_logs),
    'shingle': _plain(tex_shingle),
    'rust': _plain(tex_rust),
    'pipes': _plain(tex_pipes),
    'panel': _plain(tex_panel),
    'panel_green': _plain(tex_panel, '#6a7a6e', '#36443a'),
    # floors / ceilings
    'checker': _plain(tex_checker),
    'linoleum': _plain(tex_linoleum),
    'tile_floor': _plain(tex_tile, '#b8b4a8', '#5a5850', 16),
    'grass': _plain(tex_grass),
    'gravel': _plain(tex_gravel),
    'cobble': _plain(tex_cobble),
    'dirt': _plain(tex_gravel, '#5a4a36'),
    'water': _plain(tex_water),
    'carpet': _plain(tex_carpet),
    'carpet_green': _plain(tex_carpet, '#1e3a2a', '#9a8a4a'),
    'sand': _plain(tex_sand),
    'marble': _plain(tex_marble),
    'marble_dark': _plain(tex_marble, '#4a4844'),
    'wood_floor': _plain(tex_planks, '#5a3e26'),
    'concrete_floor': _plain(tex_concrete, '#6e6e68'),
    'rock_floor': _plain(tex_rock, '#4a4440'),
    'beams': _plain(tex_beams),
    'acoustic': _plain(tex_acoustic),
    'ceiling_plaster': _plain(tex_plaster, '#a8a08a', '#4a4030', 0.3),
    'pine_needles': _plain(tex_needles),
    'moss': _plain(tex_moss),
    'mud': _plain(tex_mud),
    'snow': _plain(tex_snow),
    'asphalt': _plain(tex_asphalt),
    'grate': _plain(tex_grate),
    # see-through: the renderer looks past their holes (fences, bars, railings, broken glass)
    'castle': _plain(tex_castle),
    'flagstone': _plain(tex_flagstone),
    'stained_glass': _em(tex_stained_glass),
    'ice': _plain(tex_ice),
    'snow_rock': _plain(tex_snow_rock),
    'slime_brick': _plain(tex_slime_brick),
    'door_wood': _plain(tex_door_wood),
    'bars': _masked(tex_bars),
    'fence_iron': _masked(tex_fence_iron),
    'chainlink': _masked(tex_chainlink),
    'railing': _masked(tex_railing),
    'picket': _masked(tex_picket),
    'portcullis': _masked(tex_portcullis),
    'window_broken': _masked(tex_window_broken),
    'lattice': _masked(tex_lattice),
}

_cache = {}
_alpha = {}


def get_texture(spec):
    """spec: a name from TEXTURES, a path to a PNG, or {"base": name, "tint": [r,g,b], "brightness": f}."""
    key = str(spec)
    if key in _cache:
        return _cache[key]
    em = alpha = None
    if isinstance(spec, dict):
        rgb, em = get_texture(spec['base'])
        alpha = get_alpha(spec['base'])
        rgb = rgb.copy()
        if 'tint' in spec:
            rgb = rgb * np.array(spec['tint'], dtype=np.float32)[None, None, :]
        rgb = np.clip(rgb * spec.get('brightness', 1.0), 0, 1)
    elif isinstance(spec, str) and spec.lower().endswith('.png'):
        rgba = np.asarray(Image.open(spec).convert('RGBA').resize((T, T), Image.NEAREST), np.float32) / 255
        rgb = rgba[..., :3]
        if (rgba[..., 3] < 0.5).any():   # a PNG with transparent pixels is a see-through wall
            alpha = (rgba[..., 3] >= 0.5).astype(np.float32)
    else:
        if spec not in TEXTURES:
            raise KeyError(f"unknown texture '{spec}'. Known: {', '.join(sorted(TEXTURES))}")
        res = TEXTURES[spec](spec)
        rgb, em = res[0], res[1]
        alpha = res[2] if len(res) > 2 else None
    out = (np.clip(rgb, 0, 1).astype(np.float32), None if em is None else em.astype(np.float32))
    _cache[key] = out
    _alpha[key] = alpha
    return out


def get_alpha(spec):
    """See-through mask for a texture (64x64, 1 = solid, 0 = hole), or None if it is solid."""
    get_texture(spec)
    return _alpha.get(str(spec))


# ---------------------------------------------------------------- sprites
# Drawn at 4x then reduced for a chunky pixel look. Return (rgba float HxWx4, emissive HxW).

def _canvas(w, h):
    im = Image.new('RGBA', (w * 4, h * 4), (0, 0, 0, 0))
    em = Image.new('L', (w * 4, h * 4), 0)
    return im, ImageDraw.Draw(im), em, ImageDraw.Draw(em)


def _finish(im, em, w, h):
    rgba = np.asarray(im.resize((w, h), Image.NEAREST), dtype=np.float32) / 255
    e = np.asarray(em.resize((w, h), Image.NEAREST), dtype=np.float32) / 255
    rgba[..., 3] = (rgba[..., 3] > 0.5).astype(np.float32)
    return rgba, e


def spr_lamp_post():
    w, h = 16, 64
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([7 * S, 14 * S, 9 * S - 1, 62 * S], fill='#24221e')
    d.rectangle([5 * S, 58 * S, 11 * S - 1, 64 * S], fill='#1c1a18')
    d.rectangle([4 * S, 3 * S, 12 * S - 1, 12 * S], fill='#f2d27a')
    de.rectangle([4 * S, 3 * S, 12 * S - 1, 12 * S], fill=255)
    d.polygon([(3 * S, 3 * S), (8 * S, 0), (13 * S, 3 * S)], fill='#1c1a18')
    d.rectangle([3 * S, 12 * S, 13 * S, 14 * S], fill='#1c1a18')
    d.line([(8 * S, 3 * S), (8 * S, 12 * S)], fill='#3a3020', width=S)
    return _finish(im, em, w, h)


def spr_statue():
    w, h = 24, 64
    im, d, em, de = _canvas(w, h)
    S = 4
    stone, dark = '#8a857c', '#5a5650'
    d.rectangle([2 * S, 46 * S, 22 * S, 64 * S], fill='#6a6660')
    d.rectangle([1 * S, 44 * S, 23 * S, 47 * S], fill='#77736c')
    d.polygon([(12 * S, 8 * S), (6 * S, 16 * S), (5 * S, 44 * S), (19 * S, 44 * S), (18 * S, 16 * S)], fill=stone)
    d.ellipse([8 * S, 1 * S, 16 * S, 10 * S], fill=stone)
    d.polygon([(7 * S, 4 * S), (12 * S, 0), (17 * S, 4 * S), (16 * S, 12 * S), (8 * S, 12 * S)], fill=dark)  # hood
    d.ellipse([10 * S, 5 * S, 14 * S, 10 * S], fill='#2a2826')  # shadowed face
    d.line([(12 * S, 20 * S), (12 * S, 43 * S)], fill=dark, width=S)
    d.line([(9 * S, 22 * S), (9 * S, 43 * S)], fill=dark, width=S // 2)
    d.polygon([(8 * S, 20 * S), (16 * S, 20 * S), (14 * S, 28 * S), (10 * S, 28 * S)], fill=dark)  # hands clasped
    return _finish(im, em, w, h)


def spr_flowers():
    w, h = 32, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(4)
    d.ellipse([0, 4 * S, 32 * S, 24 * S], fill='#1e3a22')
    d.ellipse([3 * S, 2 * S, 20 * S, 16 * S], fill='#264a2a')
    d.ellipse([14 * S, 3 * S, 30 * S, 17 * S], fill='#22422a')
    for _ in range(26):
        x, y = rng.random() * 28 + 2, rng.random() * 12 + 2
        d.ellipse([x * S, y * S, (x + 2) * S, (y + 2) * S], fill='#c4302a')
        d.point([((x + 1) * S, (y + 1) * S)], fill='#ffd060')
    return _finish(im, em, w, h)


def spr_palm():
    w, h = 48, 96
    im, d, em, de = _canvas(w, h)
    S = 4
    for i in range(70):
        y = 96 - i
        x = 24 + 4 * np.sin(i / 25)
        d.rectangle([(x - 2) * S, y * S, (x + 2) * S, (y + 1) * S], fill='#5a4632' if (i // 4) % 2 else '#4a3a28')
    cx, cy = 24 + 4 * np.sin(70 / 25), 26
    for ang in np.linspace(0, 2 * np.pi, 9)[:-1]:
        ex, ey = cx + 22 * np.cos(ang), cy + 10 * np.sin(ang) + 10 * abs(np.cos(ang))
        d.line([(cx * S, cy * S), (ex * S, ey * S)], fill='#26442a', width=3 * S)
        for t in np.linspace(0.3, 1, 6):
            px, py = cx + (ex - cx) * t, cy + (ey - cy) * t
            d.line([(px * S, py * S), ((px + 2) * S, (py + 4) * S)], fill='#1e3a22', width=S)
    return _finish(im, em, w, h)


def spr_tree():
    w, h = 64, 96
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(28 * S, 96 * S), (30 * S, 50 * S), (34 * S, 50 * S), (37 * S, 96 * S)], fill='#3a2c20')
    d.line([(32 * S, 60 * S), (18 * S, 44 * S)], fill='#3a2c20', width=2 * S)
    d.line([(32 * S, 58 * S), (46 * S, 42 * S)], fill='#3a2c20', width=2 * S)
    rng = np.random.default_rng(9)
    for _ in range(40):
        x, y, r = rng.random() * 44 + 10, rng.random() * 40 + 6, rng.random() * 6 + 6
        c = ['#1e3424', '#24402a', '#2c4a2e', '#18281c'][int(rng.random() * 4)]
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    return _finish(im, em, w, h)


def spr_barrel():
    w, h = 20, 28
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([2 * S, 1 * S, 18 * S, 28 * S], fill='#5a3a22')
    for x in range(2, 18, 3):
        d.line([(x * S, 1 * S), (x * S, 28 * S)], fill='#3a2614', width=S // 2)
    for y in (4, 14, 24):
        d.rectangle([2 * S, y * S, 18 * S, (y + 2) * S], fill='#2a2a2a')
    d.ellipse([2 * S, 0, 18 * S, 3 * S], fill='#4a3018')
    return _finish(im, em, w, h)


def spr_crate():
    w, h = 24, 24
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([0, 0, 24 * S, 24 * S], fill='#7a5a36')
    d.rectangle([0, 0, 24 * S - 1, 24 * S - 1], outline='#3a2814', width=2 * S)
    d.line([(2 * S, 2 * S), (22 * S, 22 * S)], fill='#4a3420', width=2 * S)
    for y in (8, 16):
        d.line([(0, y * S), (24 * S, y * S)], fill='#5a4026', width=S // 2)
    d.text((6 * S, 9 * S), 'TNT', fill='#2a1a10')
    return _finish(im, em, w, h)


def spr_lantern():
    w, h = 12, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    d.line([(6 * S, 0), (6 * S, 4 * S)], fill='#2a2620', width=S)
    d.rectangle([2 * S, 4 * S, 10 * S, 6 * S], fill='#2a2620')
    d.rectangle([3 * S, 6 * S, 9 * S, 16 * S], fill='#f0b45a')
    de.rectangle([3 * S, 6 * S, 9 * S, 16 * S], fill=255)
    d.line([(6 * S, 6 * S), (6 * S, 16 * S)], fill='#5a4020', width=S // 2)
    d.rectangle([2 * S, 16 * S, 10 * S, 19 * S], fill='#2a2620')
    return _finish(im, em, w, h)


def spr_candles():
    w, h = 24, 16
    im, d, em, de = _canvas(w, h)
    S = 4
    for x, hh in [(3, 7), (8, 10), (13, 5), (17, 9), (21, 6)]:
        d.rectangle([(x - 1.5) * S, (16 - hh) * S, (x + 1.5) * S, 16 * S], fill='#d8ccb0')
        d.rectangle([(x - 1.5) * S, (16 - hh) * S, (x + 1.5) * S, (17 - hh) * S], fill='#f0e8d0')
        flame = [(x - 1.2) * S, (16 - hh - 4) * S, (x + 1.2) * S, (16 - hh) * S]
        d.ellipse(flame, fill='#ffcc60')
        de.ellipse(flame, fill=255)
    return _finish(im, em, w, h)


def spr_bed():
    w, h = 40, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([2 * S, 6 * S, 38 * S, 12 * S], fill='#c8c4b4')
    d.rectangle([2 * S, 4 * S, 12 * S, 8 * S], fill='#e0dccc')
    for x in (1, 39):
        d.rectangle([(x - 1) * S, 0, (x + 1) * S, 20 * S], fill='#5a5e60')
    d.rectangle([0, 12 * S, 40 * S, 14 * S], fill='#4a4e50')
    for x in (4, 36):
        d.rectangle([(x - 1) * S, 14 * S, (x + 1) * S, 20 * S], fill='#3a3e40')
    d.line([(0, 2 * S), (40 * S, 2 * S)], fill='#5a5e60', width=S)
    return _finish(im, em, w, h)


def spr_wheelchair():
    w, h = 20, 24
    im, d, em, de = _canvas(w, h)
    S = 4
    d.ellipse([1 * S, 10 * S, 19 * S, 24 * S], outline='#3a3a3a', width=S)
    d.rectangle([4 * S, 2 * S, 16 * S, 14 * S], fill='#4a3a2a')
    d.rectangle([4 * S, 2 * S, 16 * S, 4 * S], fill='#2a2a2a')
    d.line([(10 * S, 10 * S), (10 * S, 24 * S)], fill='#3a3a3a', width=S // 2)
    return _finish(im, em, w, h)


def spr_bench():
    w, h = 40, 16
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([0, 0, 40 * S, 3 * S], fill='#5a3e26')
    d.rectangle([0, 6 * S, 40 * S, 9 * S], fill='#6a4a2e')
    for x in (3, 37):
        d.rectangle([(x - 1) * S, 0, (x + 1) * S, 16 * S], fill='#1e1e1e')
    return _finish(im, em, w, h)


def spr_column():
    w, h = 16, 64
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([3 * S, 4 * S, 13 * S, 60 * S], fill='#b0aa9a')
    for x in (5, 8, 11):
        d.line([(x * S, 5 * S), (x * S, 59 * S)], fill='#8a8476', width=S)
    d.rectangle([0, 0, 16 * S, 4 * S], fill='#c0baa8')
    d.rectangle([0, 60 * S, 16 * S, 64 * S], fill='#9a9484')
    return _finish(im, em, w, h)


def spr_rowboat():
    w, h = 48, 16
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(0, 4 * S), (48 * S, 4 * S), (42 * S, 14 * S), (6 * S, 14 * S)], fill='#5a4030')
    d.rectangle([0, 3 * S, 48 * S, 5 * S], fill='#6e5038')
    for y in (8, 11):
        d.line([(4 * S, y * S), (44 * S, y * S)], fill='#4a3424', width=S // 2)
    d.line([(36 * S, 4 * S), (36 * S, 0)], fill='#3a2c22', width=S)
    return _finish(im, em, w, h)


def spr_fern():
    w, h = 24, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    for ang in np.linspace(-1.2, 1.2, 9):
        ex, ey = 12 + 11 * np.sin(ang), 20 - 18 * np.cos(ang)
        d.line([(12 * S, 20 * S), (ex * S, ey * S)], fill='#2a4a2a', width=2 * S)
        d.line([(12 * S, 20 * S), ((ex + 12) / 2 * S, (ey + 20) / 2 * S)], fill='#3a5e32', width=S)
    return _finish(im, em, w, h)


def spr_fountain():
    w, h = 48, 40
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([0, 26 * S, 48 * S, 40 * S], fill='#8a857c')
    d.rectangle([0, 26 * S, 48 * S, 28 * S], fill='#a8a294')
    d.rectangle([20 * S, 8 * S, 28 * S, 26 * S], fill='#7a766e')
    d.ellipse([12 * S, 4 * S, 36 * S, 12 * S], fill='#8a857c')
    d.rectangle([22 * S, 0, 26 * S, 6 * S], fill='#7a766e')
    return _finish(im, em, w, h)


def spr_pine():
    w, h = 48, 112
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([21 * S, 84 * S, 27 * S, 112 * S], fill='#3a2a1c')
    tones = ['#16301c', '#1e3c22', '#264828']
    for i in range(7):
        half = 23 - 16 * (i / 6.0)
        base = 96 - 13 * i
        d.polygon([((24 - half) * S, base * S), ((24 + half) * S, base * S), (24 * S, (base - 26) * S)],
                  fill=tones[i % 3])
    d.polygon([(19 * S, 20 * S), (29 * S, 20 * S), (24 * S, 0)], fill='#2c5230')
    return _finish(im, em, w, h)


def spr_dead_tree():
    w, h = 64, 104
    im, d, em, de = _canvas(w, h)
    S = 4
    bark = '#3a3028'
    d.polygon([(27 * S, 104 * S), (30 * S, 40 * S), (35 * S, 40 * S), (38 * S, 104 * S)], fill=bark)
    for (x0, y0, x1, y1, wd) in ((32, 56, 12, 32, 5), (32, 50, 52, 26, 5), (32, 40, 24, 10, 4),
                                 (32, 42, 44, 12, 4), (20, 40, 10, 22, 3), (44, 36, 56, 18, 3)):
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=bark, width=wd * S)
    for (x0, y0, x1, y1) in ((12, 32, 6, 20), (52, 26, 58, 14), (24, 10, 18, 2), (44, 12, 50, 4),
                             (16, 26, 10, 14), (48, 20, 54, 8)):
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill='#2a241e', width=2 * S)
    d.ellipse([24 * S, 98 * S, 42 * S, 104 * S], fill='#2a241e')
    return _finish(im, em, w, h)


def spr_stump():
    w, h = 24, 16
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([3 * S, 4 * S, 21 * S, 16 * S], fill='#4a3826')
    for x in range(4, 21, 4):
        d.line([(x * S, 6 * S), (x * S, 16 * S)], fill='#3a2a1c', width=S // 2)
    d.ellipse([3 * S, 0, 21 * S, 8 * S], fill='#8a6a44')
    d.ellipse([7 * S, 2 * S, 17 * S, 6 * S], fill='#6e5234')
    d.ellipse([10 * S, 3 * S, 14 * S, 5 * S], fill='#543e26')
    return _finish(im, em, w, h)


def spr_log():
    w, h = 48, 14
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([2 * S, 2 * S, 46 * S, 13 * S], fill='#4a3826')
    d.rectangle([2 * S, 2 * S, 46 * S, 5 * S], fill='#5e4830')
    for x in range(4, 46, 5):
        d.line([(x * S, 3 * S), ((x + 2) * S, 12 * S)], fill='#3a2a1c', width=S // 2)
    d.ellipse([0, S, 6 * S, 13 * S], fill='#8a6a44')
    d.ellipse([2 * S, 4 * S, 5 * S, 10 * S], fill='#6e5234')
    d.ellipse([42 * S, S, 48 * S, 13 * S], fill='#7a5c3a')
    return _finish(im, em, w, h)


def spr_bush():
    w, h = 32, 24
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([14 * S, 16 * S, 18 * S, 24 * S], fill='#3a2c20')
    rng = np.random.default_rng(5)
    tones = ['#1e3a22', '#264a28', '#2e5a30', '#14281a']
    for _ in range(34):
        x, y, r = rng.random() * 24 + 4, rng.random() * 15 + 5, rng.random() * 5 + 4
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=tones[int(rng.random() * 4)])
    return _finish(im, em, w, h)


def spr_mushrooms():
    w, h = 20, 14
    im, d, em, de = _canvas(w, h)
    S = 4
    for (x, y, r, cap) in ((5, 9, 4, '#8a3a32'), (12, 7, 5, '#a04a3a'), (16, 11, 3, '#7a3028')):
        d.rectangle([(x - 1) * S, y * S, (x + 1) * S, 14 * S], fill='#d8cdb4')
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r // 2) * S], fill=cap)
        d.ellipse([(x - r + 1) * S, (y - r + 1) * S, (x - r + 3) * S, (y - r + 3) * S], fill='#e0d0c0')
    return _finish(im, em, w, h)


def spr_boulder():
    w, h = 32, 24
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(2 * S, 24 * S), (4 * S, 10 * S), (12 * S, 3 * S), (22 * S, 4 * S), (30 * S, 14 * S),
               (30 * S, 24 * S)], fill='#6a665e')
    d.polygon([(4 * S, 12 * S), (12 * S, 4 * S), (20 * S, 5 * S), (14 * S, 14 * S)], fill='#8a857c')
    d.polygon([(16 * S, 16 * S), (28 * S, 15 * S), (30 * S, 24 * S), (14 * S, 24 * S)], fill='#4a4740')
    rng = np.random.default_rng(11)
    for _ in range(10):
        x, y = rng.random() * 22 + 5, rng.random() * 8 + 4
        d.ellipse([x * S, y * S, (x + 3) * S, (y + 2) * S], fill='#2e4a2a')
    return _finish(im, em, w, h)


def spr_signpost():
    w, h = 32, 48
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([14 * S, 8 * S, 18 * S, 48 * S], fill='#4a3826')
    d.rectangle([2 * S, 10 * S, 28 * S, 20 * S], fill='#6e5636')
    d.polygon([(28 * S, 10 * S), (32 * S, 15 * S), (28 * S, 20 * S)], fill='#6e5636')
    d.rectangle([2 * S, 10 * S, 28 * S - 1, 20 * S - 1], outline='#3a2a1c', width=S)
    for y in (13, 16):
        d.line([(6 * S, y * S), (24 * S, y * S)], fill='#2a2018', width=S // 2)
    return _finish(im, em, w, h)


def spr_campfire():
    w, h = 32, 28
    im, d, em, de = _canvas(w, h)
    S = 4
    d.ellipse([3 * S, 21 * S, 29 * S, 27 * S], fill='#4a4440')
    d.ellipse([6 * S, 22 * S, 26 * S, 26 * S], fill='#2e2a28')
    d.line([(6 * S, 24 * S), (26 * S, 18 * S)], fill='#4a3826', width=3 * S)
    d.line([(6 * S, 18 * S), (26 * S, 24 * S)], fill='#3a2c1e', width=3 * S)
    d.ellipse([10 * S, 19 * S, 22 * S, 24 * S], fill='#c04010')
    de.ellipse([10 * S, 19 * S, 22 * S, 24 * S], fill=200)
    d.polygon([(16 * S, 2 * S), (23 * S, 21 * S), (9 * S, 21 * S)], fill='#ff8a20')
    de.polygon([(16 * S, 2 * S), (23 * S, 21 * S), (9 * S, 21 * S)], fill=255)
    d.polygon([(16 * S, 8 * S), (20 * S, 21 * S), (12 * S, 21 * S)], fill='#ffe070')
    de.polygon([(16 * S, 8 * S), (20 * S, 21 * S), (12 * S, 21 * S)], fill=255)
    return _finish(im, em, w, h)


def spr_locker():
    w, h = 24, 56
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([2 * S, 2 * S, 22 * S, 56 * S], fill='#4a5a5e')
    d.rectangle([2 * S, 2 * S, 22 * S - 1, 56 * S - 1], outline='#2a3438', width=S)
    d.line([(12 * S, 2 * S), (12 * S, 56 * S)], fill='#2a3438', width=S)
    for x in (7, 17):
        d.rectangle([(x - 3) * S, 8 * S, (x + 3) * S, 13 * S], fill='#2e3a3e')
        for k in range(3):
            d.line([((x - 3) * S, (9 + k * 1.5) * S), ((x + 3) * S, (9 + k * 1.5) * S)],
                   fill='#5a6a6e', width=S // 2)
        d.rectangle([(x + 2) * S, 28 * S, (x + 3) * S, 33 * S], fill='#b0a060')
    d.rectangle([2 * S, 52 * S, 22 * S, 56 * S], fill='#2e3a3e')
    return _finish(im, em, w, h)


def spr_console():
    w, h = 32, 44
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([3 * S, 14 * S, 29 * S, 44 * S], fill='#4a4e52')
    d.rectangle([3 * S, 14 * S, 29 * S - 1, 44 * S - 1], outline='#2a2e32', width=S)
    d.rectangle([5 * S, 2 * S, 27 * S, 18 * S], fill='#2a2e30')
    d.rectangle([7 * S, 4 * S, 25 * S, 15 * S], fill='#2aff8a')
    de.rectangle([7 * S, 4 * S, 25 * S, 15 * S], fill=190)
    for y in range(5, 15, 2):
        d.line([(8 * S, y * S), ((10 + (y * 7) % 14) * S, y * S)], fill='#0a2a18', width=S // 2)
    for i, c in enumerate(('#d04030', '#d0b030', '#30c060')):
        d.rectangle([(7 + i * 5) * S, 22 * S, (10 + i * 5) * S, 25 * S], fill=c)
        de.rectangle([(7 + i * 5) * S, 22 * S, (10 + i * 5) * S, 25 * S], fill=160)
    d.rectangle([6 * S, 30 * S, 26 * S, 38 * S], fill='#3a3e42')
    for y in (32, 35):
        for x in range(7, 25, 3):
            d.rectangle([x * S, y * S, (x + 2) * S, (y + 2) * S], fill='#6a7074')
    return _finish(im, em, w, h)


def spr_buoy():
    w, h = 20, 32
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([8 * S, 2 * S, 12 * S, 18 * S], fill='#6a6a66')
    d.ellipse([2 * S, 14 * S, 18 * S, 32 * S], fill='#a03028')
    d.ellipse([2 * S, 14 * S, 18 * S, 22 * S], fill='#c04038')
    d.rectangle([4 * S, 23 * S, 16 * S, 26 * S], fill='#d8d4c0')
    d.ellipse([7 * S, 0, 13 * S, 5 * S], fill='#ffd060')
    de.ellipse([7 * S, 0, 13 * S, 5 * S], fill=255)
    return _finish(im, em, w, h)


def spr_gravestone():
    w, h = 24, 32
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([2 * S, 28 * S, 22 * S, 32 * S], fill='#6a665e')
    d.rectangle([4 * S, 8 * S, 20 * S, 30 * S], fill='#8a857c')
    d.ellipse([4 * S, 2 * S, 20 * S, 16 * S], fill='#8a857c')
    d.rectangle([7 * S, 11 * S, 17 * S, 26 * S], fill='#726e66')
    for y in range(13, 25, 3):
        d.line([(9 * S, y * S), (15 * S, y * S)], fill='#5a5650', width=S // 2)
    rng = np.random.default_rng(31)
    for _ in range(8):
        x, y = rng.random() * 14 + 5, rng.random() * 16 + 8
        d.ellipse([x * S, y * S, (x + 2) * S, (y + 2) * S], fill='#4a5a3a')
    return _finish(im, em, w, h)


def spr_sconce():
    """Wall bracket with a live flame. Mount it with z around 0.7."""
    w, h = 16, 24
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([6 * S, 14 * S, 10 * S, 24 * S], fill='#3a3028')
    d.rectangle([4 * S, 12 * S, 12 * S, 15 * S], fill='#4a4038')
    d.polygon([(5 * S, 12 * S), (11 * S, 12 * S), (10 * S, 8 * S), (6 * S, 8 * S)], fill='#2e2822')
    d.polygon([(8 * S, 0), (12 * S, 11 * S), (4 * S, 11 * S)], fill='#ff8a20')
    de.polygon([(8 * S, 0), (12 * S, 11 * S), (4 * S, 11 * S)], fill=255)
    d.polygon([(8 * S, 4 * S), (10 * S, 11 * S), (6 * S, 11 * S)], fill='#ffe887')
    de.polygon([(8 * S, 4 * S), (10 * S, 11 * S), (6 * S, 11 * S)], fill=255)
    return _finish(im, em, w, h)


def spr_ceiling_lamp():
    """Hangs from above: give it z near the ceiling height."""
    w, h = 20, 24
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([9 * S, 0, 11 * S, 9 * S], fill='#2a2620')
    d.polygon([(2 * S, 16 * S), (18 * S, 16 * S), (14 * S, 9 * S), (6 * S, 9 * S)], fill='#4a4640')
    d.polygon([(4 * S, 15 * S), (16 * S, 15 * S), (13 * S, 10 * S), (7 * S, 10 * S)], fill='#6a665e')
    d.ellipse([7 * S, 14 * S, 13 * S, 20 * S], fill='#ffe070')
    de.ellipse([7 * S, 14 * S, 13 * S, 20 * S], fill=255)
    return _finish(im, em, w, h)


def spr_chandelier():
    w, h = 40, 28
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([19 * S, 0, 21 * S, 8 * S], fill='#2a2620')
    d.ellipse([8 * S, 7 * S, 32 * S, 13 * S], outline='#6a5a32', width=2 * S)
    d.rectangle([14 * S, 10 * S, 26 * S, 12 * S], fill='#6a5a32')
    for x in (10, 17, 23, 30):
        d.rectangle([(x - 1) * S, 10 * S, (x + 1) * S, 16 * S], fill='#5a4a28')
        d.rectangle([(x - 1.4) * S, 16 * S, (x + 1.4) * S, 22 * S], fill='#e8e0c8')
        d.ellipse([(x - 1.6) * S, 21 * S, (x + 1.6) * S, 27 * S], fill='#ffd060')
        de.ellipse([(x - 1.6) * S, 21 * S, (x + 1.6) * S, 27 * S], fill=255)
    return _finish(im, em, w, h)


def spr_brazier():
    w, h = 28, 44
    im, d, em, de = _canvas(w, h)
    S = 4
    for x in (6, 14, 22):
        d.line([(14 * S, 26 * S), (x * S, 44 * S)], fill='#2e2a26', width=2 * S)
    d.rectangle([4 * S, 40 * S, 24 * S, 44 * S], fill='#24201c')
    d.polygon([(4 * S, 20 * S), (24 * S, 20 * S), (21 * S, 30 * S), (7 * S, 30 * S)], fill='#4a4440')
    d.polygon([(6 * S, 22 * S), (22 * S, 22 * S), (20 * S, 28 * S), (8 * S, 28 * S)], fill='#2a2622')
    d.ellipse([7 * S, 17 * S, 21 * S, 24 * S], fill='#c03c10')
    de.ellipse([7 * S, 17 * S, 21 * S, 24 * S], fill=210)
    d.polygon([(14 * S, 0), (21 * S, 21 * S), (7 * S, 21 * S)], fill='#ff8a20')
    de.polygon([(14 * S, 0), (21 * S, 21 * S), (7 * S, 21 * S)], fill=255)
    d.polygon([(14 * S, 6 * S), (18 * S, 21 * S), (10 * S, 21 * S)], fill='#ffe887')
    de.polygon([(14 * S, 6 * S), (18 * S, 21 * S), (10 * S, 21 * S)], fill=255)
    return _finish(im, em, w, h)


def spr_painting():
    """Framed picture for a wall: mount with z around 0.6."""
    w, h = 28, 22
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([0, 0, 28 * S, 22 * S], fill='#5a4424')
    d.rectangle([2 * S, 2 * S, 26 * S, 20 * S], fill='#7a6034')
    d.rectangle([4 * S, 4 * S, 24 * S, 18 * S], fill='#2a3038')
    d.polygon([(4 * S, 18 * S), (11 * S, 8 * S), (17 * S, 18 * S)], fill='#3e4a42')
    d.polygon([(12 * S, 18 * S), (19 * S, 10 * S), (24 * S, 18 * S)], fill='#4a5648')
    d.ellipse([18 * S, 5 * S, 22 * S, 9 * S], fill='#c8b888')
    d.rectangle([4 * S, 15 * S, 24 * S, 18 * S], fill='#2e3a30')
    return _finish(im, em, w, h)


def spr_banner():
    """Tall hanging cloth: mount high on a wall with z around 0.5."""
    w, h = 20, 40
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([2 * S, 0, 18 * S, 3 * S], fill='#4a4038')
    d.polygon([(3 * S, 2 * S), (17 * S, 2 * S), (17 * S, 34 * S), (10 * S, 40 * S), (3 * S, 34 * S)],
              fill='#6a1a20')
    d.polygon([(5 * S, 4 * S), (15 * S, 4 * S), (15 * S, 33 * S), (10 * S, 37 * S), (5 * S, 33 * S)],
              fill='#8a2228')
    d.ellipse([7 * S, 10 * S, 13 * S, 16 * S], outline='#c8a040', width=S)
    d.polygon([(10 * S, 19 * S), (13 * S, 27 * S), (7 * S, 27 * S)], fill='#c8a040')
    return _finish(im, em, w, h)


def spr_wall_clock():
    w, h = 16, 16
    im, d, em, de = _canvas(w, h)
    S = 4
    d.ellipse([0, 0, 15 * S, 15 * S], fill='#3a2e22')
    d.ellipse([2 * S, 2 * S, 13 * S, 13 * S], fill='#d8d0b8')
    for a in range(0, 360, 30):
        r = np.radians(a)
        d.line([((7.5 + 4.4 * np.sin(r)) * S, (7.5 - 4.4 * np.cos(r)) * S),
                ((7.5 + 5.2 * np.sin(r)) * S, (7.5 - 5.2 * np.cos(r)) * S)], fill='#4a4038', width=S // 2)
    d.line([(7.5 * S, 7.5 * S), (7.5 * S, 4 * S)], fill='#2a2620', width=S)
    d.line([(7.5 * S, 7.5 * S), (10.5 * S, 9 * S)], fill='#2a2620', width=S)
    return _finish(im, em, w, h)


def spr_pipe_valve():
    w, h = 20, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([8 * S, 10 * S, 12 * S, 20 * S], fill='#5a5e62')
    d.rectangle([5 * S, 7 * S, 15 * S, 11 * S], fill='#4a4e52')
    d.ellipse([2 * S, 2 * S, 18 * S, 12 * S], outline='#8a3a28', width=2 * S)
    d.line([(2 * S, 7 * S), (18 * S, 7 * S)], fill='#8a3a28', width=2 * S)
    d.line([(10 * S, 2 * S), (10 * S, 12 * S)], fill='#8a3a28', width=2 * S)
    d.ellipse([8 * S, 5 * S, 12 * S, 9 * S], fill='#6a6e72')
    return _finish(im, em, w, h)


def spr_rubble():
    w, h = 32, 14
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(41)
    for _ in range(26):
        x, y = rng.random() * 28 + 2, rng.random() * 8 + 5
        s = rng.random() * 3.5 + 1.5
        c = ['#6a665e', '#8a857c', '#4a4740', '#5a5048'][int(rng.random() * 4)]
        d.polygon([(x * S, (y + s) * S), ((x + s) * S, y * S), ((x + s * 2) * S, (y + s) * S)], fill=c)
    d.rectangle([3 * S, 11 * S, 29 * S, 14 * S], fill='#3a3830')
    return _finish(im, em, w, h)


def spr_bones():
    w, h = 28, 12
    im, d, em, de = _canvas(w, h)
    S = 4
    bone = '#d8d0b8'
    for (x0, y0, x1, y1) in ((4, 8, 14, 6), (8, 10, 20, 9), (14, 5, 23, 7)):
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=bone, width=2 * S)
        for (bx, by) in ((x0, y0), (x1, y1)):
            d.ellipse([(bx - 1.4) * S, (by - 1.4) * S, (bx + 1.4) * S, (by + 1.4) * S], fill=bone)
    d.ellipse([18 * S, 2 * S, 26 * S, 10 * S], fill=bone)
    d.ellipse([20 * S, 5 * S, 22 * S, 8 * S], fill='#2a2620')
    d.ellipse([23 * S, 5 * S, 25 * S, 8 * S], fill='#2a2620')
    return _finish(im, em, w, h)


def spr_sack():
    w, h = 20, 22
    im, d, em, de = _canvas(w, h)
    S = 4
    d.ellipse([1 * S, 6 * S, 19 * S, 22 * S], fill='#8a7a52')
    d.ellipse([3 * S, 8 * S, 13 * S, 19 * S], fill='#a89668')
    d.polygon([(7 * S, 8 * S), (13 * S, 8 * S), (12 * S, 1 * S), (8 * S, 1 * S)], fill='#8a7a52')
    d.rectangle([7 * S, 3 * S, 13 * S, 5 * S], fill='#4a3e28')
    return _finish(im, em, w, h)


def spr_bucket():
    w, h = 16, 16
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(2 * S, 4 * S), (14 * S, 4 * S), (12 * S, 16 * S), (4 * S, 16 * S)], fill='#5a5e62')
    d.polygon([(3 * S, 5 * S), (8 * S, 5 * S), (7 * S, 15 * S), (4 * S, 15 * S)], fill='#6e7276')
    d.ellipse([2 * S, 2 * S, 14 * S, 6 * S], fill='#3a3e42')
    d.ellipse([4 * S, 3 * S, 12 * S, 5 * S], fill='#1a1e22')
    d.arc([3 * S, 0, 13 * S, 8 * S], 180, 360, fill='#3a3e42', width=S)
    return _finish(im, em, w, h)


def spr_broken_barrel():
    w, h = 22, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(2 * S, 20 * S), (3 * S, 6 * S), (9 * S, 2 * S), (12 * S, 9 * S), (16 * S, 4 * S),
               (19 * S, 20 * S)], fill='#5a3a22')
    d.polygon([(4 * S, 19 * S), (5 * S, 8 * S), (9 * S, 5 * S), (11 * S, 10 * S)], fill='#6e4a2a')
    for y in (12, 17):
        d.rectangle([2 * S, y * S, 19 * S, (y + 1.6) * S], fill='#2a2a2a')
    d.polygon([(13 * S, 20 * S), (20 * S, 14 * S), (22 * S, 20 * S)], fill='#3a2614')
    return _finish(im, em, w, h)


def spr_grass_tuft():
    w, h = 20, 14
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(47)
    for _ in range(16):
        x = rng.random() * 16 + 2
        ln = rng.random() * 8 + 5
        lean = (rng.random() - 0.5) * 5
        c = ['#39442c', '#4a5a38', '#272e1f'][int(rng.random() * 3)]
        d.line([(x * S, 14 * S), ((x + lean) * S, (14 - ln) * S)], fill=c, width=S)
    return _finish(im, em, w, h)


def spr_reeds():
    w, h = 24, 34
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(53)
    for _ in range(13):
        x = rng.random() * 18 + 3
        ln = rng.random() * 16 + 15
        lean = (rng.random() - 0.5) * 7
        c = ['#4a5a28', '#5e7034', '#38461e'][int(rng.random() * 3)]
        tipx = x + lean
        d.line([(x * S, 34 * S), (tipx * S, (34 - ln) * S)], fill=c, width=S)
        if rng.random() > 0.5:
            d.rectangle([(tipx - 0.8) * S, (34 - ln) * S, (tipx + 0.8) * S, (38 - ln) * S],
                        fill='#6a5230')
    return _finish(im, em, w, h)


def spr_ivy_hang():
    """Trailing growth to hang off a ledge or wall top; place with z."""
    w, h = 28, 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(59)
    for x0 in (4, 11, 18, 24):
        ln = rng.random() * 14 + 14
        x = x0
        for y in range(int(ln)):
            x += (rng.random() - 0.5) * 0.8
            d.rectangle([x * S, y * S, (x + 1) * S, (y + 1.6) * S], fill='#20401e')
            if y % 3 == 1:
                s = 1.6 + rng.random() * 1.4
                sx = x + (1.2 if y % 6 == 1 else -s)
                d.ellipse([sx * S, (y - 0.5) * S, (sx + s) * S, (y + 1.5) * S], fill='#2e5a2a')
    return _finish(im, em, w, h)


def spr_rocks():
    w, h = 24, 10
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(61)
    for _ in range(9):
        x, y = rng.random() * 20 + 2, rng.random() * 4 + 4
        s = rng.random() * 2.6 + 1.6
        c = ['#6a665e', '#8a857c', '#4a4740'][int(rng.random() * 3)]
        d.ellipse([(x - s) * S, (y - s * 0.7) * S, (x + s) * S, (y + s * 0.7) * S], fill=c)
    return _finish(im, em, w, h)


def spr_throne():
    w, h = 28, 52
    im, d, em, de = _canvas(w, h)
    S = 4
    gold, wood, dark, red = '#c8a040', '#5a3a22', '#3a2414', '#8a1e26'
    d.polygon([(6 * S, 34 * S), (6 * S, 6 * S), (14 * S, 0), (22 * S, 6 * S), (22 * S, 34 * S)], fill=wood)
    d.polygon([(8 * S, 32 * S), (8 * S, 8 * S), (14 * S, 3 * S), (20 * S, 8 * S), (20 * S, 32 * S)], fill=red)
    d.line([(14 * S, 0), (14 * S, 3 * S)], fill=gold, width=S)
    d.ellipse([12 * S, 10 * S, 16 * S, 14 * S], fill=gold)
    d.rectangle([2 * S, 30 * S, 26 * S, 36 * S], fill=wood)            # arms and seat
    d.rectangle([2 * S, 30 * S, 6 * S, 32 * S], fill=gold)
    d.rectangle([22 * S, 30 * S, 26 * S, 32 * S], fill=gold)
    d.rectangle([7 * S, 34 * S, 21 * S, 38 * S], fill=red)
    for x in (3, 22):
        d.rectangle([x * S, 36 * S, (x + 3) * S, 52 * S], fill=dark)
    d.rectangle([6 * S, 38 * S, 22 * S, 48 * S], fill=wood)
    d.line([(6 * S, 38 * S), (22 * S, 38 * S)], fill=gold, width=S)
    return _finish(im, em, w, h)


def spr_armor():
    """A suit of armour on its stand, halberd in hand."""
    w, h = 24, 56
    im, d, em, de = _canvas(w, h)
    S = 4
    st, dk, hi = '#9aa0a8', '#5a606a', '#d4dae0'
    d.line([(20 * S, 0), (20 * S, 54 * S)], fill='#4a3420', width=S)       # halberd shaft
    d.polygon([(20 * S, 0), (24 * S, 5 * S), (20 * S, 10 * S)], fill=hi)
    d.ellipse([7 * S, 2 * S, 15 * S, 11 * S], fill=st)                     # helm
    d.rectangle([8 * S, 6 * S, 14 * S, 7 * S], fill='#0a0a0c')
    d.rectangle([3 * S, 12 * S, 19 * S, 16 * S], fill=dk)                  # pauldrons
    d.polygon([(6 * S, 14 * S), (16 * S, 14 * S), (15 * S, 28 * S), (7 * S, 28 * S)], fill=st)
    d.line([(11 * S, 15 * S), (11 * S, 27 * S)], fill=hi, width=S)
    for x in (3, 16):
        d.rectangle([x * S, 16 * S, (x + 3) * S, 28 * S], fill=st)         # arms
    d.rectangle([7 * S, 28 * S, 15 * S, 33 * S], fill=dk)
    for x in (7, 12):
        d.rectangle([x * S, 33 * S, (x + 3) * S, 50 * S], fill=st)         # legs
        d.line([(x * S + S, 34 * S), (x * S + S, 49 * S)], fill=hi, width=S // 2)
    d.rectangle([4 * S, 50 * S, 18 * S, 56 * S], fill='#4a3a2a')           # stand
    return _finish(im, em, w, h)


def spr_chains():
    """Two chains hanging from above, one ending in a shackle. Hang it with z near the ceiling."""
    w, h = 16, 44
    im, d, em, de = _canvas(w, h)
    S = 4
    for x, ln in ((4, 37), (11, 29)):
        for y in range(0, ln, 4):
            if (y // 4) % 2:   # links alternate face-on (a ring) and edge-on (a bar)
                d.ellipse([(x - 2) * S, y * S, (x + 2) * S, (y + 4) * S], outline='#6a6a72', width=S)
            else:
                d.rectangle([(x - 1) * S, y * S, (x + 1) * S, (y + 4) * S], fill='#7a7a82')
    d.ellipse([1 * S, 36 * S, 8 * S, 43 * S], outline='#5a5a62', width=S + S // 2)
    return _finish(im, em, w, h)


def spr_chest():
    w, h = 24, 18
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([1 * S, 7 * S, 23 * S, 18 * S], fill='#6a4428')
    d.chord([1 * S, 0, 23 * S, 12 * S], 180, 360, fill='#7a5030')
    for x in (4, 18):
        d.rectangle([x * S, 1 * S, (x + 2) * S, 18 * S], fill='#3a3a3e')
    d.line([(1 * S, 7 * S), (23 * S, 7 * S)], fill='#3a3a3e', width=S)
    d.rectangle([10 * S, 6 * S, 14 * S, 11 * S], fill='#c8a040')
    d.rectangle([11 * S, 8 * S, 13 * S, 10 * S], fill='#2a2014')
    return _finish(im, em, w, h)


def spr_table():
    w, h = 40, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([0, 4 * S, 40 * S, 8 * S], fill='#6a4a2c')
    d.rectangle([0, 4 * S, 40 * S, 5 * S], fill='#8a6a44')
    for x in (2, 35):
        d.rectangle([x * S, 8 * S, (x + 3) * S, 20 * S], fill='#4a3220')
    d.rectangle([5 * S, 8 * S, 35 * S, 10 * S], fill='#4a3220')
    return _finish(im, em, w, h)


def spr_pew():
    """A long church bench with a back, seen from the aisle."""
    w, h = 52, 24
    im, d, em, de = _canvas(w, h)
    S = 4
    wood, dark = '#5a3a22', '#3a2414'
    d.rectangle([0, 0, 52 * S, 12 * S], fill=wood)              # backrest
    d.rectangle([0, 0, 52 * S, 2 * S], fill='#7a5432')
    d.rectangle([0, 12 * S, 52 * S, 15 * S], fill=dark)          # seat edge
    for x in (0, 49):
        d.rectangle([x * S, 0, (x + 3) * S, 24 * S], fill=dark)  # end boards
    d.rectangle([3 * S, 15 * S, 49 * S, 18 * S], fill=wood)
    return _finish(im, em, w, h)


def spr_stalagmite():
    w, h = 18, 44
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(2 * S, 44 * S), (8 * S, 0), (11 * S, 6 * S), (16 * S, 44 * S)], fill='#5a5248')
    d.polygon([(5 * S, 44 * S), (8 * S, 4 * S), (9 * S, 44 * S)], fill='#7a7064')
    for y in range(8, 42, 6):
        d.line([(4 * S, y * S), (14 * S, (y + 2) * S)], fill='#4a443c', width=S // 2)
    return _finish(im, em, w, h)


def spr_crystal():
    """A cluster of glowing crystals: give it a light of its own to cast the glow."""
    w, h = 22, 26
    im, d, em, de = _canvas(w, h)
    S = 4
    for (x0, x1, top, c) in ((3, 8, 10, '#5ac8e8'), (8, 14, 0, '#8ae0ff'), (13, 19, 7, '#6ab0f0'), (6, 10, 14, '#a8f0ff')):
        poly = [(x0 * S, 26 * S), ((x0 + x1) / 2 * S, top * S), (x1 * S, 26 * S)]
        d.polygon(poly, fill=c)
        de.polygon(poly, fill=230)
    d.rectangle([1 * S, 23 * S, 21 * S, 26 * S], fill='#3a3440')
    return _finish(im, em, w, h)


def spr_glowshroom():
    w, h = 22, 14
    im, d, em, de = _canvas(w, h)
    S = 4
    for (x, y, r) in ((5, 7, 4), (12, 5, 5), (18, 9, 3)):
        d.rectangle([(x - 1) * S, y * S, (x + 1) * S, 14 * S], fill='#c8d8c0')
        cap = [(x - r) * S, (y - r) * S, (x + r) * S, (y + r // 2) * S]
        d.ellipse(cap, fill='#4af0c8')
        de.ellipse(cap, fill=255)
    return _finish(im, em, w, h)


def spr_snowy_pine():
    w, h = 48, 112
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([21 * S, 84 * S, 27 * S, 112 * S], fill='#3a2a1c')
    for i in range(7):
        half = 23 - 16 * (i / 6.0)
        base = 96 - 13 * i
        d.polygon([((24 - half) * S, base * S), ((24 + half) * S, base * S), (24 * S, (base - 26) * S)],
                  fill=('#16301c', '#1e3c22', '#264828')[i % 3])
        # snow along each tier's upper slopes
        d.polygon([((24 - half * 0.75) * S, (base - 6) * S), (24 * S, (base - 26) * S),
                   ((24 + half * 0.75) * S, (base - 6) * S), (24 * S, (base - 12) * S)], fill='#dce6ee')
    d.polygon([(19 * S, 20 * S), (29 * S, 20 * S), (24 * S, 0)], fill='#e8eef4')
    return _finish(im, em, w, h)


def spr_snowman():
    w, h = 22, 34
    im, d, em, de = _canvas(w, h)
    S = 4
    snow = '#e6ecf2'
    d.ellipse([1 * S, 16 * S, 21 * S, 34 * S], fill=snow)
    d.ellipse([4 * S, 7 * S, 18 * S, 20 * S], fill=snow)
    d.ellipse([6 * S, 0, 16 * S, 10 * S], fill=snow)
    d.rectangle([5 * S, 9 * S, 17 * S, 11 * S], fill='#a02828')      # scarf
    d.rectangle([14 * S, 10 * S, 16 * S, 16 * S], fill='#a02828')
    for (x, y) in ((9, 4), (13, 4), (11, 13), (11, 16), (11, 19)):
        d.rectangle([x * S, y * S, (x + 1) * S, (y + 1) * S], fill='#1a1a1a')
    d.polygon([(11 * S, 5 * S), (11 * S, 7 * S), (15 * S, 6 * S)], fill='#e07020')
    return _finish(im, em, w, h)


def spr_grave_cross():
    w, h = 16, 30
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([6 * S, 0, 10 * S, 30 * S], fill='#5a4a38')
    d.rectangle([1 * S, 7 * S, 15 * S, 11 * S], fill='#5a4a38')
    d.rectangle([7 * S, 1 * S, 8 * S, 28 * S], fill='#6e5c46')
    d.rectangle([3 * S, 26 * S, 13 * S, 30 * S], fill='#3a3028')
    return _finish(im, em, w, h)


def spr_ladder():
    """Iron rungs up a wall. Place it a little off the wall face."""
    w, h = 16, 64
    im, d, em, de = _canvas(w, h)
    S = 4
    for x in (2, 12):
        d.rectangle([x * S, 0, (x + 2) * S, 64 * S], fill='#4a4e52')
    for y in range(3, 64, 6):
        d.rectangle([2 * S, y * S, 14 * S, (y + 1) * S], fill='#6a6e72')
    return _finish(im, em, w, h)


def spr_lectern():
    w, h = 20, 30
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(1 * S, 6 * S), (19 * S, 2 * S), (19 * S, 9 * S), (1 * S, 11 * S)], fill='#5a3a22')
    d.polygon([(3 * S, 5 * S), (10 * S, 4 * S), (10 * S, 8 * S), (3 * S, 9 * S)], fill='#e8e0c8')   # open book
    d.polygon([(10 * S, 4 * S), (17 * S, 3 * S), (17 * S, 7 * S), (10 * S, 8 * S)], fill='#d8d0b8')
    d.rectangle([8 * S, 10 * S, 12 * S, 27 * S], fill='#4a3020')
    d.rectangle([4 * S, 27 * S, 16 * S, 30 * S], fill='#3a2414')
    return _finish(im, em, w, h)


SPRITES = {
    'lamp_post': spr_lamp_post, 'statue': spr_statue, 'flowers': spr_flowers, 'palm': spr_palm,
    'tree': spr_tree, 'barrel': spr_barrel, 'crate': spr_crate, 'lantern': spr_lantern,
    'candles': spr_candles, 'bed': spr_bed, 'wheelchair': spr_wheelchair, 'bench': spr_bench,
    'column': spr_column, 'rowboat': spr_rowboat, 'fern': spr_fern, 'fountain': spr_fountain,
    'pine': spr_pine, 'dead_tree': spr_dead_tree, 'stump': spr_stump, 'log': spr_log,
    'bush': spr_bush, 'mushrooms': spr_mushrooms, 'boulder': spr_boulder, 'signpost': spr_signpost,
    'campfire': spr_campfire, 'locker': spr_locker, 'console': spr_console, 'buoy': spr_buoy,
    'gravestone': spr_gravestone,
    'sconce': spr_sconce, 'ceiling_lamp': spr_ceiling_lamp, 'chandelier': spr_chandelier,
    'brazier': spr_brazier, 'painting': spr_painting, 'banner': spr_banner,
    'wall_clock': spr_wall_clock, 'pipe_valve': spr_pipe_valve, 'rubble': spr_rubble,
    'bones': spr_bones, 'sack': spr_sack, 'bucket': spr_bucket, 'broken_barrel': spr_broken_barrel,
    'grass_tuft': spr_grass_tuft, 'reeds': spr_reeds, 'ivy_hang': spr_ivy_hang, 'rocks': spr_rocks,
    'throne': spr_throne, 'armor': spr_armor, 'chains': spr_chains, 'chest': spr_chest,
    'table': spr_table, 'pew': spr_pew, 'stalagmite': spr_stalagmite, 'crystal': spr_crystal,
    'glowshroom': spr_glowshroom, 'snowy_pine': spr_snowy_pine, 'snowman': spr_snowman,
    'grave_cross': spr_grave_cross, 'ladder': spr_ladder, 'lectern': spr_lectern,
}

# default world size (height in map units) for each sprite
SPRITE_HEIGHT = {
    'lamp_post': 1.6, 'statue': 1.5, 'flowers': 0.35, 'palm': 3.0, 'tree': 2.6, 'barrel': 0.45,
    'crate': 0.4, 'lantern': 0.3, 'candles': 0.2, 'bed': 0.4, 'wheelchair': 0.45, 'bench': 0.35,
    'column': 1.0, 'rowboat': 0.3, 'fern': 0.4, 'fountain': 0.9,
    'pine': 3.4, 'dead_tree': 2.9, 'stump': 0.3, 'log': 0.28, 'bush': 0.5, 'mushrooms': 0.12,
    'boulder': 0.55, 'signpost': 1.3, 'campfire': 0.4, 'locker': 1.0, 'console': 0.85, 'buoy': 0.5,
    'gravestone': 0.6,
    'sconce': 0.32, 'ceiling_lamp': 0.3, 'chandelier': 0.45, 'brazier': 0.85,
    'painting': 0.45, 'banner': 0.95, 'wall_clock': 0.28, 'pipe_valve': 0.32, 'rubble': 0.34,
    'bones': 0.22, 'sack': 0.42, 'bucket': 0.32, 'broken_barrel': 0.46, 'grass_tuft': 0.40,
    'reeds': 0.8, 'ivy_hang': 0.8, 'rocks': 0.22,
    'throne': 0.95, 'armor': 0.66, 'chains': 0.6, 'chest': 0.3, 'table': 0.36, 'pew': 0.42,
    'stalagmite': 0.8, 'crystal': 0.36, 'glowshroom': 0.16, 'snowy_pine': 3.4, 'snowman': 0.62,
    'grave_cross': 0.55, 'ladder': 1.0, 'lectern': 0.5,
}

# ---------------------------------------------------------------- debris and scatter

# Size classes multiply a prop's default height. Real ground litter is mostly small with the
# occasional big piece, so the default weighting leans heavily toward the lower classes.
# Classes are centred on each prop's default height, which is already tuned to read at 320x200.
# The spread stays modest on purpose: `scale` is a *height*, so a wide prop like `log` (48x14)
# grows sideways much faster than it grows tall, and a big multiplier turns debris into scenery.
# The low end has to stay visible too - `rocks` defaults to 0.22, so 0.3x of that is invisible.
SIZE_CLASSES = {'tiny': 0.6, 'small': 0.8, 'medium': 1.0, 'large': 1.3, 'huge': 1.7}
SIZE_WEIGHTS = {'tiny': 5, 'small': 4, 'medium': 2.5, 'large': 1, 'huge': 0.3}

# Named sets for `scatter`. Repeats are how a set is weighted: 'stones' is mostly loose rock
# with the odd boulder, not an even mix.
DEBRIS_SETS = {
    'stones': ['rocks', 'rocks', 'rocks', 'boulder'],
    'rubble': ['rubble', 'rubble', 'rocks', 'broken_barrel'],
    'forest': ['rocks', 'rocks', 'log', 'stump', 'mushrooms', 'grass_tuft', 'grass_tuft',
               'fern', 'bush'],
    'undergrowth': ['grass_tuft', 'grass_tuft', 'grass_tuft', 'fern', 'bush', 'mushrooms'],
    'shore': ['rocks', 'rocks', 'rocks', 'boulder', 'reeds', 'bones'],
    'litter': ['sack', 'bucket', 'crate', 'barrel', 'broken_barrel', 'bones'],
    'wreckage': ['rubble', 'rubble', 'broken_barrel', 'rocks', 'bones', 'sack', 'bucket'],
    'cave': ['rocks', 'rocks', 'rocks', 'stalagmite', 'glowshroom', 'crystal', 'bones'],
}

# What `grime` stamps on surfaces when it is turned up.
GRIME_WALL_DECALS = ['stain', 'stain_rust', 'splatter_dark', 'leak', 'crack', 'moss_patch']
GRIME_FLOOR_DECALS = ['stain', 'stain_rust', 'splatter_dark', 'crack', 'puddle_dark', 'scorch']


def debris_items(spec):
    """Resolve a scatter `of` field to a list of sprite names (repeats act as weights)."""
    if isinstance(spec, str):
        if spec in DEBRIS_SETS:
            return list(DEBRIS_SETS[spec])
        return [spec]
    out = []
    for item in spec:
        out.extend(debris_items(item))
    return out


def sprite_aspect(name, defs=None):
    """Width / height of a prop, so callers can work out its world footprint from its scale."""
    rgba, _ = get_sprite(name, defs)
    h, w = rgba.shape[:2]
    return w / max(h, 1)


def size_scale(name, size_class, defs=None):
    """Absolute world height for a prop drawn at one of the named size classes.

    A scene's own sprite_defs carry their `height`, so scattered custom debris keeps the size
    its author gave it rather than falling back to one world unit.
    """
    base = sprite_defaults(name, defs).get('scale', SPRITE_HEIGHT.get(name, 1.0))
    return base * SIZE_CLASSES.get(size_class, 1.0)


_scache = {}


def _hex_rgba(h):
    h = h.lstrip('#')
    v = [int(h[i:i + 2], 16) / 255 for i in range(0, len(h), 2)]
    return v + [1.0] * (4 - len(v))


def sprite_from_pixels(defn):
    """Text-grid pixel art -> (rgba float HxWx4, emissive HxW). See characters.py for the format."""
    rows = defn['pixels']
    if defn.get('mirror'):
        rows = [r + r[::-1] for r in rows]
    w = max(len(r) for r in rows)
    h = len(rows)
    pal = {k: _hex_rgba(v) for k, v in defn['palette'].items()}
    glow = set(defn.get('emissive', ''))
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in '. ':
                continue
            if ch not in pal:
                raise KeyError(f"pixel char '{ch}' (row {y}) missing from palette")
            rgba[y, x] = pal[ch]
            if ch in glow:
                em[y, x] = 1.0
    return rgba, em


def sprite_defaults(spec, defs=None):
    """Default placement fields (height, opacity, aura...) for a sprite name."""
    from characters import CHARACTERS
    d = (defs or {}).get(spec) or CHARACTERS.get(spec) if isinstance(spec, str) else None
    out = {}
    if d:
        if 'height' in d:
            out['scale'] = d['height']
        out.update(d.get('defaults', {}))
    elif isinstance(spec, str) and spec in SPRITE_HEIGHT:
        out['scale'] = SPRITE_HEIGHT[spec]
    return out


def get_sprite(spec, defs=None):
    """spec: built-in prop name, character name, a name defined in the scene's sprite_defs, or a PNG path."""
    from characters import CHARACTERS
    defs = defs or {}
    if spec in defs:
        key = 'def:' + json_key(defs[spec])
        if key not in _scache:
            _scache[key] = sprite_from_pixels(defs[spec])
        return _scache[key]
    if spec in _scache:
        return _scache[spec]
    if spec in CHARACTERS:
        out = sprite_from_pixels(CHARACTERS[spec])
    elif spec.lower().endswith('.png'):
        im = Image.open(spec).convert('RGBA')
        rgba = np.asarray(im, dtype=np.float32) / 255
        out = (rgba, np.zeros(rgba.shape[:2], np.float32))
    else:
        if spec not in SPRITES:
            known = sorted(SPRITES) + sorted(CHARACTERS)
            raise KeyError(f"unknown sprite '{spec}'. Known: {', '.join(known)}")
        out = SPRITES[spec]()
    _scache[spec] = out
    return out


def json_key(obj):
    import json
    return json.dumps(obj, sort_keys=True)


# ---------------------------------------------------------------- per-material variation

# How much surface_noise each material wants, relative to the scene's amount. One global figure
# does not suit every surface: flat man-made materials show mottling almost immediately, while
# rough natural ones (cobble, gravel, rust) swallow a lot before they stop looking like stone.
# The scene's `surface_noise` amount is multiplied by these, so at the 0.10 default a plaster
# wall varies by ~7% and a cobbled street by ~30%.
TEXTURE_NOISE = {
    # flat and man-made: show variation soonest, so damp it down
    'checker': 0.5, 'marble': 0.5, 'marble_dark': 0.5, 'curtain': 0.5, 'curtain_black': 0.5,
    'tile_white': 0.6, 'tile_green': 0.6, 'tile_floor': 0.6, 'linoleum': 0.6,
    'panel': 0.6, 'panel_green': 0.6, 'iron_door': 0.6,
    'plaster': 0.7, 'plaster_white': 0.7, 'hospital_wall': 0.7, 'ceiling_plaster': 0.7,
    'acoustic': 0.7, 'snow': 0.8, 'water': 0.8,
    # emissive or light-carrying: keep these clean, mottled light reads as a fault
    'runes': 0.3, 'window_lit': 0.4, 'window_lit_plaster': 0.4, 'window_teal': 0.4,
    'window_dark': 0.6, 'window_dark_plaster': 0.6,
    # worked materials: about as much as the scene asks for
    'wallpaper': 0.8, 'wallpaper_green': 0.8, 'bookshelf': 0.8,
    'wood_panel': 0.9, 'corrugated': 0.9, 'carpet': 0.9, 'carpet_green': 0.9,
    'planks': 1.0, 'boards': 1.0, 'wood_floor': 1.0, 'beams': 1.0,
    'concrete': 1.1, 'concrete_floor': 1.1, 'logs': 1.1,
    'brick': 1.2, 'brick_dark': 1.2, 'brick_yellow': 1.2, 'shingle': 1.2, 'grate': 1.2,
    'pipes': 1.4,
    # rough and natural: these take a lot before they stop reading as the material
    'hedge': 1.6, 'foliage': 1.6, 'foliage_autumn': 1.6,
    'bark': 1.8, 'bark_pine': 1.8, 'ivy': 1.8,
    'stone': 2.0, 'stone_dark': 2.0, 'stone_pale': 2.0, 'sand': 2.0, 'grass': 2.0,
    'rock': 2.2, 'rock_wet': 2.2, 'rock_floor': 2.2, 'pine_needles': 2.2, 'moss': 2.2,
    'dirt': 2.4, 'mud': 2.4, 'asphalt': 2.4, 'moss_stone': 2.4,
    'gravel': 2.6, 'rust': 2.6,
    'cobble': 3.0,
    # see-through: only their solid parts are drawn, so the factor applies to the metal or wood
    'chainlink': 0.6, 'fence_iron': 0.8, 'picket': 0.8, 'bars': 1.0, 'railing': 1.0,
    'lattice': 1.0, 'portcullis': 1.2, 'window_broken': 1.4,
    'castle': 2.0, 'flagstone': 2.2, 'stained_glass': 0.3, 'ice': 0.8, 'snow_rock': 1.8,
    'slime_brick': 1.4, 'door_wood': 1.0,
}


# How mirror-like a floor is by default. Any floor cell can set its own "reflect" (wet asphalt,
# polished marble); puddle decals carry their own (DECAL_REFLECT).
TEXTURE_REFLECT = {'water': 0.5, 'ice': 0.38}
DECAL_REFLECT = {'puddle': 0.35, 'puddle_shine': 0.55, 'puddle_dark': 0.25}


def texture_reflect(spec):
    """Default reflectivity of a floor texture (0 = matte)."""
    return float(TEXTURE_REFLECT.get(texture_key(spec), 0.0))


def texture_key(spec):
    """The name a texture spec is keyed by: a built-in name, a PNG path, or a variant's base."""
    if isinstance(spec, dict):
        return spec.get('base') or spec.get('path') or ''
    return spec if isinstance(spec, str) else ''


def texture_noise(spec):
    """Relative surface-noise multiplier for a texture spec. Unknown materials get 1.0."""
    return float(TEXTURE_NOISE.get(texture_key(spec), 1.0))


# ---------------------------------------------------------------- decals
# Stamps blended into a surface's albedo at render time: puddles, stains, vines, cracks.
# Unlike sprites these keep soft alpha, so they can fade into the surface underneath.


def col_hex(h, a=255):
    """'#rrggbb' + 0-255 alpha -> an RGBA tuple for PIL."""
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(a))


def _finish_soft(im, em, w, h):
    """Like _finish, but keeps the alpha gradient instead of thresholding it to 1 bit."""
    rgba = np.asarray(im.resize((w, h), Image.NEAREST), dtype=np.float32) / 255
    e = np.asarray(em.resize((w, h), Image.NEAREST), dtype=np.float32) / 255
    return rgba, e


def dec_puddle(c='#1a2630', rim='#4a5a60', a=190):
    """Nested rings, so a big puddle fades into the floor instead of cutting a hard hole in it."""
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(3)
    blobs = [(rng.random() * 9 + 11.5, rng.random() * 7 + 12.5,
              rng.random() * 4.5 + 5.5, rng.random() * 3 + 3.5) for _ in range(6)]
    for k in range(6):
        shrink = 1.0 - k * 0.14
        al = int(a * (0.22 + 0.78 * k / 5))
        for (cx, cy, ex, ey) in blobs:
            d.ellipse([(cx - ex * shrink) * S, (cy - ey * shrink) * S,
                       (cx + ex * shrink) * S, (cy + ey * shrink) * S], fill=col_hex(c, al))
    d.ellipse([11 * S, 13 * S, 19 * S, 16 * S], fill=col_hex(rim, int(a * 0.45)))
    return _finish_soft(im, em, w, h)


def dec_stain(c='#2e2418', a=150):
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(11)
    for i in range(14):
        r = rng.random() * 7 + 3
        cx, cy = rng.random() * 16 + 8, rng.random() * 16 + 8
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
                  fill=col_hex(c, int(a * (0.4 + 0.6 * rng.random()))))
    return _finish_soft(im, em, w, h)


def dec_splatter(c='#5a1012', a=225):
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(7)
    d.ellipse([11 * S, 12 * S, 21 * S, 20 * S], fill=col_hex(c, a))
    for _ in range(26):
        ang = rng.random() * 6.283
        dist = rng.random() * 13 + 3
        r = rng.random() * 2.2 + 0.6
        cx, cy = 16 + dist * np.cos(ang), 16 + dist * np.sin(ang)
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=col_hex(c, a))
    return _finish_soft(im, em, w, h)


def dec_vines(c='#1e3a1e', leaf='#2e5a2a', a=255):
    """Hangs from the top edge: put it high on a wall."""
    w, h = 32, 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(5)
    for x0 in (4, 9, 15, 21, 27):
        ln = rng.random() * 12 + 14
        x = x0
        for y in range(0, int(ln)):
            x += (rng.random() - 0.5) * 0.9
            d.rectangle([x * S, y * S, (x + 1) * S, (y + 1.6) * S], fill=col_hex(c, a))
            if y % 4 == 2:
                s = 1.6 + rng.random()
                sx = x + (1.4 if y % 8 == 2 else -s)
                d.ellipse([sx * S, (y - 0.4) * S, (sx + s) * S, (y + 1.4) * S], fill=col_hex(leaf, a))
    return _finish_soft(im, em, w, h)


def dec_moss_patch(c='#2c4a26', hi='#3e6a30', a=205):
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(13)
    for _ in range(40):
        r = rng.random() * 4.5 + 1.5
        cx, cy = rng.random() * 20 + 6, rng.random() * 20 + 6
        fill = hi if rng.random() > 0.65 else c
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
                  fill=col_hex(fill, int(a * (0.5 + 0.5 * rng.random()))))
    return _finish_soft(im, em, w, h)


def dec_crack(c='#15120f', a=230):
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(17)

    def branch(x, y, ang, ln, wd):
        for _ in range(int(ln)):
            nx, ny = x + np.cos(ang), y + np.sin(ang)
            d.line([(x * S, y * S), (nx * S, ny * S)], fill=col_hex(c, a), width=max(1, int(wd * S)))
            x, y = nx, ny
            ang += (rng.random() - 0.5) * 0.7
        return x, y, ang

    x, y, ang = branch(3, 7, 0.35, 18, 1.1)
    branch(x, y, ang - 0.8, 11, 0.85)
    branch(x, y, ang + 0.7, 9, 0.75)
    branch(12, 11, 1.3, 11, 0.75)
    branch(20, 4, 2.1, 9, 0.75)
    return _finish_soft(im, em, w, h)


def dec_scorch(c='#0e0c0b', a=215):
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(23)
    for i in range(10):
        r = 11 - i * 0.8
        d.ellipse([(16 - r) * S, (16 - r * 0.85) * S, (16 + r) * S, (16 + r * 0.85) * S],
                  fill=col_hex(c, int(a * (0.25 + 0.075 * i))))
    for _ in range(18):
        ang = rng.random() * 6.283
        dist = rng.random() * 5 + 10
        r = rng.random() * 2 + 0.8
        cx, cy = 16 + dist * np.cos(ang), 16 + dist * np.sin(ang) * 0.85
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=col_hex(c, 120))
    return _finish_soft(im, em, w, h)


def dec_leak(c='#2a3a3e', a=165):
    """Vertical drip streaks: water damage running down a wall."""
    w, h = 32, 32
    im, d, em, de = _canvas(w, h)
    S = 4
    rng = np.random.default_rng(29)
    for x0 in (6, 11, 16, 20, 25):
        ln = rng.random() * 14 + 14
        wd = rng.random() * 1.6 + 0.8
        for y in range(int(ln)):
            fade = int(a * (1 - y / (ln * 1.25)))
            d.rectangle([x0 * S, y * S, (x0 + wd) * S, (y + 1.2) * S], fill=col_hex(c, max(0, fade)))
        d.ellipse([(x0 - 0.6) * S, (ln - 1) * S, (x0 + wd + 0.6) * S, (ln + 1.6) * S],
                  fill=col_hex(c, int(a * 0.55)))
    return _finish_soft(im, em, w, h)


def dec_cobweb(c='#c8c8c0', a=120):
    """Corner web: sits in the top-left of its footprint, flip it for the other corner."""
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    for k in range(9):
        t = k / 8
        d.line([(0, t * 31 * S), (t * 31 * S, 0)], fill=col_hex(c, a), width=max(1, S // 2))
    for r in (9, 16, 23, 29):
        d.arc([-r * S, -r * S, r * S, r * S], 0, 90, fill=col_hex(c, a), width=max(1, S // 2))
    return _finish_soft(im, em, w, h)


def dec_rune_mark(c='#c02018', glow='#ff4030'):
    """Emissive sigil: glows regardless of scene lighting."""
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    box = [5 * S, 5 * S, 27 * S, 27 * S]
    d.ellipse(box, outline=col_hex(c, 255), width=2 * S)
    de.ellipse(box, outline=255, width=2 * S)
    pts = [(16, 6), (26, 22), (6, 22)]
    poly = [(x * S, y * S) for x, y in pts]
    d.line(poly + [poly[0]], fill=col_hex(glow, 255), width=2 * S)
    de.line(poly + [poly[0]], fill=255, width=2 * S)
    d.line([(16 * S, 6 * S), (16 * S, 22 * S)], fill=col_hex(glow, 255), width=S)
    de.line([(16 * S, 6 * S), (16 * S, 22 * S)], fill=255, width=S)
    return _finish_soft(im, em, w, h)


def dec_contact_shadow(c='#0a0806'):
    """Soft round shadow for the foot of a prop or character. A smooth falloff on purpose: the
    palette's ordered dither turns it into a properly 90s stippled shadow."""
    n = 32
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.hypot((xx + 0.5 - n / 2) / (n / 2), (yy + 0.5 - n / 2) / (n / 2))
    rgba = np.zeros((n, n, 4), np.float32)
    rgba[..., :3] = col(c)
    rgba[..., 3] = np.clip(1 - r * r, 0, 1) ** 1.3
    return rgba, np.zeros((n, n), np.float32)


def dec_drain(c='#3a3e40', bar='#6a6e70'):
    w = h = 32
    im, d, em, de = _canvas(w, h)
    S = 4
    d.ellipse([6 * S, 6 * S, 26 * S, 26 * S], fill=col_hex('#101214', 235))
    d.ellipse([6 * S, 6 * S, 26 * S, 26 * S], outline=col_hex(bar, 255), width=2 * S)
    for y in range(9, 24, 4):
        d.rectangle([8 * S, y * S, 24 * S, (y + 2) * S], fill=col_hex(c, 255))
    return _finish_soft(im, em, w, h)


DECALS = {
    'puddle': dec_puddle,
    'puddle_dark': lambda: dec_puddle('#0c1216', '#2a3a40', 215),
    'puddle_shine': lambda: dec_puddle('#6a7a88', '#c6d2de', 150),
    'stain': dec_stain,
    'stain_rust': lambda: dec_stain('#6a3a18', 150),
    'splatter': dec_splatter,
    'splatter_dark': lambda: dec_splatter('#24100f', 235),
    'vines': dec_vines,
    'moss_patch': dec_moss_patch,
    'crack': dec_crack,
    'scorch': dec_scorch,
    'leak': dec_leak,
    'cobweb': dec_cobweb,
    'rune_mark': dec_rune_mark,
    'drain': dec_drain,
    'contact_shadow': lambda: dec_contact_shadow(),
}

# Props that never get an automatic contact shadow: light sources whose base glows (a dark blob
# under a fire reads as a hole), and things that hang or mount on walls.
NO_CONTACT_SHADOW = {'campfire', 'brazier', 'candles', 'lantern', 'ceiling_lamp', 'chandelier',
                     'sconce', 'ivy_hang', 'painting', 'banner', 'wall_clock', 'pipe_valve',
                     'chains', 'ladder', 'crystal', 'glowshroom'}

_dcache = {}


def get_decal(spec, defs=None):
    """spec: a built-in decal name, a name in the scene's decal_defs, or a PNG path (RGBA)."""
    defs = defs or {}
    if spec in defs:
        key = 'def:' + json_key(defs[spec])
        if key not in _dcache:
            _dcache[key] = sprite_from_pixels(defs[spec])
        return _dcache[key]
    if spec in _dcache:
        return _dcache[spec]
    if isinstance(spec, str) and spec.lower().endswith('.png'):
        im = Image.open(spec).convert('RGBA')
        rgba = np.asarray(im, dtype=np.float32) / 255
        out = (rgba, np.zeros(rgba.shape[:2], np.float32))
    else:
        if spec not in DECALS:
            raise KeyError(f"unknown decal '{spec}'. Known: {', '.join(sorted(DECALS))}")
        out = DECALS[spec]()
    _dcache[spec] = out
    return out


# ---------------------------------------------------------------- skies

SKYLINES = ('mountains', 'hills', 'treeline', 'city')


def _harmonics(w, rng, terms, ridged=False):
    """A 1-D profile over 360 degrees built from whole-number harmonics, so it wraps seamlessly."""
    az = np.arange(w) / w * 2 * np.pi
    out = np.zeros(w)
    for k, amp in terms:
        s = np.sin(k * az + rng.random() * 2 * np.pi)
        out += amp * ((1 - np.abs(s)) if ridged else 0.5 + 0.5 * s)
    return out / sum(a for _, a in terms)


def _wrapdist(w, centre):
    x = np.arange(w)
    d = np.abs(x - centre)
    return np.minimum(d, w - d)


def _silhouette(sky, elev_deg, proj, colour, rng, texture=0.08):
    """Paint a ground silhouette whose top edge is `elev_deg` (per column) above the horizon."""
    h, w = sky.shape[:2]
    top = h - 1 - proj * np.tan(np.radians(np.clip(elev_deg, 0, 60)))
    mask = np.arange(h)[:, None] >= top[None, :]
    shade = 1 - texture + texture * 2 * rng.random((h, w))
    sky[mask] = (colour[None, None, :] * shade[..., None])[mask]
    return mask


def draw_skyline(sky, spec, proj, seed=0):
    """Paint distant silhouettes into a sky panorama, back to front.

    spec: a name from SKYLINES, a dict {"type", "height", "color", "seed", "lights"}, or a list of
    those (first = farthest). Heights are in degrees above the horizon, so the skyline keeps its
    proportions at any resolution or field of view.
    """
    specs = spec if isinstance(spec, list) else [spec]
    hor = sky[-1].mean(axis=0)  # the sky's own horizon colour, for atmospheric perspective

    def tone(depth, ink=(0.03, 0.035, 0.05)):
        return hor * (1 - depth) + np.array(ink, np.float32) * depth

    for i, s in enumerate(specs):
        s = {'type': s} if isinstance(s, str) else dict(s)
        kind = s.get('type')
        if kind not in SKYLINES:
            raise KeyError(f"unknown skyline '{kind}'. Skylines: {', '.join(SKYLINES)}")
        rng = np.random.default_rng(int(s.get('seed', seed)) * 31 + i * 7 + 11)
        k = float(s.get('height', 1.0))
        w = sky.shape[1]
        custom = np.array(s['color'], np.float32) if 'color' in s else None
        if kind == 'mountains':
            far = 2.0 + 6.5 * _harmonics(w, rng, [(2, 1), (3, .8), (5, .6), (8, .45), (13, .3), (21, .2), (34, .12)], True)
            _silhouette(sky, far * k, proj, custom if custom is not None else tone(0.42), rng)
            near = 0.8 + 3.2 * _harmonics(w, rng, [(3, 1), (5, .7), (9, .5), (15, .3), (27, .15)], True)
            _silhouette(sky, near * k, proj, custom * 0.7 if custom is not None else tone(0.68), rng)
        elif kind == 'hills':
            back = 1.0 + 3.4 * _harmonics(w, rng, [(5, 1), (8, .7), (13, .45), (21, .25)])
            _silhouette(sky, back * k, proj, custom if custom is not None else tone(0.5), rng)
            front = 0.4 + 2.2 * _harmonics(w, rng, [(7, 1), (11, .6), (17, .35), (29, .2)])
            _silhouette(sky, front * k, proj, custom * 0.75 if custom is not None else tone(0.72), rng)
        elif kind == 'treeline':
            px_deg = w / 360.0
            base = 1.4 + 1.2 * _harmonics(w, rng, [(9, 1), (17, .6), (31, .3)])
            elev = base.copy()
            for _ in range(int(360 * 1.6)):          # overlapping conifers, ~1.6 per degree
                cx = rng.random() * w
                th, half = 1.0 + 2.4 * rng.random(), (0.45 + 0.5 * rng.random()) * px_deg
                d = _wrapdist(w, cx)
                top = base[int(cx) % w] + th
                elev = np.maximum(elev, np.where(d < half, top - (top - base) * (d / half), 0))
            ink = (0.02, 0.045, 0.03)
            _silhouette(sky, elev * k, proj, custom if custom is not None else tone(0.86, ink), rng, 0.05)
        elif kind == 'city':
            px_deg = w / 360.0
            h = sky.shape[0]
            elev = np.zeros(w)
            x = 0.0
            spans = []
            while x < w:
                bw = (1.2 + 3.0 * rng.random()) * px_deg
                bh = (1.5 + 5.0 * rng.random() ** 1.7 + (4.0 if rng.random() < 0.08 else 0)) * k
                x1 = min(w, x + bw)
                elev[int(x):int(x1)] = bh
                spans.append((int(x), int(x1), bh))
                x = x1 + (0 if rng.random() < 0.75 else rng.random() * 2 * px_deg)
            ink = (0.04, 0.04, 0.06)
            body = custom if custom is not None else tone(0.8, ink)
            mask = _silhouette(sky, elev, proj, body, rng, 0.04)
            # lit windows: a sparse grid on each block, warm with the odd cold office light
            lit = float(s.get('lights', 0.22))
            yy = np.arange(h)
            for x0, x1, bh in spans:
                top = h - 1 - proj * np.tan(np.radians(bh))
                for wx in range(x0 + 1, x1 - 1, max(2, int(0.45 * px_deg))):
                    for wy in yy[(yy > top + 2) & (yy < h - 2)][::max(2, int(0.55 * px_deg))]:
                        if rng.random() < lit and mask[wy, wx]:
                            sky[wy, wx] = col('#f0c860') if rng.random() < 0.8 else col('#a8d0f0')
    return sky


def draw_disc(sky, az_deg, el_deg, proj, colour, radius_deg=2.2, glow=0.35):
    """A sun or moon at an azimuth/elevation, with a soft additive halo. Wraps around 360."""
    h, w = sky.shape[:2]
    cx = (az_deg % 360) / 360.0 * w
    cy = h - 1 - proj * np.tan(np.radians(el_deg))
    r = max(2.0, proj * np.tan(np.radians(radius_deg)))
    dx = _wrapdist(w, cx)[None, :]
    dy = (np.arange(h) - cy)[:, None]
    d = np.sqrt(dx * dx + dy * dy)
    c = np.asarray(colour, np.float32)
    halo = np.clip(1 - d / (r * 4.5), 0, 1) ** 2 * glow
    sky += halo[..., None] * c[None, None, :]
    disc = d <= r
    sky[disc] = c * (0.92 + 0.08 * np.clip(1 - d[disc] / r, 0, 1))[:, None]
    return sky


def make_sky(preset, w, h, seed=3, skyline=None, proj=None, discs=()):
    """Panorama (h, w, 3) covering 360 degrees. h is the height above the horizon line.

    `skyline` adds distant silhouettes (see draw_skyline). `discs` are suns and moons placed by
    directional lights; when any are given, the preset's own decorative moon is left out.
    """
    rng = np.random.default_rng(seed)
    presets = {
        'night': ('#05070e', '#1b2232', '#26304a'),
        'dusk': ('#1f2333', '#4a3550', '#a0605a'),
        'storm': ('#141820', '#262c38', '#3a4250'),
        'day': ('#4a7ab0', '#8ab4d8', '#c8dce8'),
        'overcast': ('#5a6068', '#7a8088', '#9aa0a4'),
        'blood': ('#120608', '#3a0e10', '#7a2018'),
    }
    top, mid, hor = [col(c) for c in presets[preset]]
    t = np.linspace(0, 1, h)[:, None]
    g = np.where(t < 0.6, top * (1 - t / 0.6) + mid * (t / 0.6), mid * (1 - (t - 0.6) / 0.4) + hor * ((t - 0.6) / 0.4))
    sky = np.repeat(g[:, None, :], w, axis=1).reshape(h, w, 3)
    # clouds: horizontal-stretched noise bands
    cn = np.zeros((h, w))
    for cells, amp in ((6, 1.0), (12, 0.5), (24, 0.25)):
        base = rng.random((max(2, cells // 3), cells))
        im = Image.fromarray((base * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        cn += np.asarray(im) / 255 * amp
    cn /= 1.75
    cover = {'night': 0.62, 'dusk': 0.55, 'storm': 0.42, 'day': 0.6, 'overcast': 0.3, 'blood': 0.55}[preset]
    mask = np.clip((cn - cover) * 4, 0, 1) * (t < 0.85)
    ccol = {'night': '#2a3245', 'dusk': '#5a3a4a', 'storm': '#1c2028', 'day': '#e8eef4', 'overcast': '#6a7078', 'blood': '#2a0a0c'}[preset]
    sky = sky * (1 - mask[..., None] * 0.85) + col(ccol) * mask[..., None] * 0.85
    if preset in ('night', 'storm', 'blood', 'dusk'):
        stars = (rng.random((h, w)) > 0.997) & (t[:, 0][:, None] < 0.6) & (mask < 0.2)
        sky[stars] = col('#c8c8d0') * (0.5 if preset != 'night' else 1)
    if preset in ('night', 'blood') and not discs:
        mx, my, r = int(w * 0.62), int(h * 0.28), max(4, h // 14)
        yy, xx = np.mgrid[0:h, 0:w]
        m = (yy - my) ** 2 + (xx - mx) ** 2 < r * r
        sky[m] = col('#e6e0c8') if preset == 'night' else col('#d04a30')
    proj = proj or w / (2 * np.pi)
    for d in discs:
        draw_disc(sky, d['azimuth'], d['elevation'], proj, d['color'], d.get('radius', 2.2), d.get('glow', 0.35))
    if skyline:
        draw_skyline(sky, skyline, proj, seed)
    return np.clip(sky, 0, 1).astype(np.float32)


def catalog(path):
    """Contact sheet of every texture and sprite with its name, for picking materials."""
    names = sorted(TEXTURES)
    cols = 8
    cw, ch = 96, 110
    rows_t = (len(names) + cols - 1) // cols
    from characters import CHARACTERS
    snames = sorted(SPRITES) + sorted(CHARACTERS)
    rows_s = (len(snames) + cols - 1) // cols
    dnames = sorted(DECALS)
    rows_d = (len(dnames) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cw, (rows_t + rows_s + rows_d) * ch + 30), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        rgb, _ = get_texture(n)
        a = get_alpha(n)
        if a is not None:   # see-through: show the holes against a checkerboard
            chk = np.where(((np.arange(T)[:, None] // 8 + np.arange(T)[None, :] // 8) % 2)[..., None] == 0, 0.35, 0.55)
            rgb = rgb * a[..., None] + chk * (1 - a[..., None])
        tile = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).resize((88, 88), Image.NEAREST)
        x, y = (i % cols) * cw + 4, (i // cols) * ch + 4
        sheet.paste(tile, (x, y))
        d.text((x, y + 90), n[:15], fill=(220, 220, 220))
    oy = rows_t * ch + 20
    for i, n in enumerate(snames):
        rgba, _ = get_sprite(n)
        hgt, wid = rgba.shape[:2]
        k = min(88 / hgt, 88 / wid)
        im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').resize((max(1, int(wid * k)), max(1, int(hgt * k))), Image.NEAREST)
        x, y = (i % cols) * cw + 4, oy + (i // cols) * ch + 4
        bg = Image.new('RGB', (88, 88), (60, 60, 70))
        bg.paste(im, ((88 - im.width) // 2, 88 - im.height), im)
        sheet.paste(bg, (x, y))
        d.text((x, y + 90), n, fill=(220, 220, 220))
    # decals, shown over a mid grey so their alpha reads
    oy = (rows_t + rows_s) * ch + 30
    for i, n in enumerate(dnames):
        rgba, _ = get_decal(n)
        im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').resize((88, 88), Image.NEAREST)
        x, y = (i % cols) * cw + 4, oy + (i // cols) * ch + 4
        bg = Image.new('RGB', (88, 88), (118, 112, 104))
        bg.paste(im, (0, 0), im)
        sheet.paste(bg, (x, y))
        d.text((x, y + 90), n[:15], fill=(220, 220, 220))
    # icons and held items
    import icons
    inames = [n for n in icons.ICONS]
    vnames = list(icons.VIEWMODELS)
    rows_i = (len(inames) + cols * 2 - 1) // (cols * 2)
    extra = rows_i * 60 + 130 + 20
    big = Image.new('RGB', (sheet.width, sheet.height + extra), (20, 20, 24))
    big.paste(sheet, (0, 0))
    d = ImageDraw.Draw(big)
    oy = sheet.height + 10
    for i, n in enumerate(inames):
        rgba, _ = icons.get_icon(n)
        im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        x, y = (i % (cols * 2)) * 48 + 8, oy + (i // (cols * 2)) * 60
        big.paste(im, (x + (32 - im.width) // 2, y), im)
        d.text((x - 2, y + 36), n[:8], fill=(200, 200, 200))
    oy += rows_i * 60 + 10
    for i, n in enumerate(vnames):
        rgba, _, _ = icons.get_viewmodel(n)
        im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')
        x = i * (sheet.width // len(vnames)) + 8
        bg = Image.new('RGB', (sheet.width // len(vnames) - 12, 110), (60, 60, 70))
        bg.paste(im, ((bg.width - im.width) // 2, 110 - im.height), im)
        big.paste(bg, (x, oy))
        d.text((x, oy + 112), n, fill=(220, 220, 220))
    big.save(path)


if __name__ == '__main__':
    import sys
    catalog(sys.argv[1] if len(sys.argv) > 1 else 'catalog.png')

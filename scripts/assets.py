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


# ------------------------------------------------- sci-fi, alien, dream and study materials

def tex_hull(name, c='#8a929c', strip=None):
    """Starship interior plating: panels between trim bands, rivets, a recessed band at eye
    height. With `strip` (a colour) that band is a glowing light strip (emissive), so a corridor
    of it draws lines of light to the vanishing point."""
    rng = _rng(name)
    n = fbm(T, rng, 12, 3)
    yy, xx = np.mgrid[0:T, 0:T]
    panel = (xx // 32) + (yy // 32) * 2
    tone = 0.9 + 0.12 * ((panel * 37 + 5) % 4) / 3.0
    img = col(c)[None, None, :] * tone[..., None] * (0.9 + 0.18 * n[..., None])
    img *= np.linspace(1.06, 0.86, T)[:, None, None]
    trim = col(c) * 0.42
    img[yy < 3] = trim
    img[yy >= 60] = trim * 0.8
    img[(yy >= 28) & (yy < 36)] = col(c) * 0.55
    img[(xx % 32) < 1] *= 0.55
    img[(yy == 3) | (yy == 36)] *= 1.25
    img[(yy == 27) | (yy == 59)] *= 0.7
    rivet = (np.hypot((xx % 32) - 4, (yy % 32) - 7) < 1.3) | (np.hypot((xx % 32) - 28, (yy % 32) - 7) < 1.3)
    img[rivet & ((yy < 28) | (yy >= 36)) & (yy >= 3) & (yy < 60)] = np.clip(col(c) * 1.25, 0, 1)
    em = None
    if strip:
        em = np.zeros((T, T), np.float32)
        band = (yy >= 30) & (yy < 34)
        img[band] = col(strip)
        em[band] = 1.0
        img[(yy == 29) | (yy == 34)] = np.clip(col(strip) * 0.45 + col(c) * 0.3, 0, 1)
    return grain(np.clip(img, 0, 1), rng, 0.02), em


def tex_tech_panel(name, c='#3a424c'):
    """Dark instrument panels: readouts with lines of glowing text and rows of indicator lights
    (emissive). Bridges, labs, control rooms."""
    rng = _rng(name)
    n = fbm(T, rng, 10, 3)
    yy, xx = np.mgrid[0:T, 0:T]
    img = col(c)[None, None, :] * (0.85 + 0.25 * n[..., None])
    em = np.zeros((T, T), np.float32)
    img[((xx % 32) < 1) | ((yy % 32) < 1)] *= 0.5
    for x0, y0 in ((4, 5), (36, 5), (4, 37), (36, 37)):
        img[y0:y0 + 10, x0:x0 + 24] = col('#0c1418')
        for r in range(y0 + 2, y0 + 9, 3):
            ln = int(rng.integers(8, 22))
            img[r, x0 + 2:x0 + 2 + ln] = col('#5ae0c8')
            em[r, x0 + 2:x0 + 2 + ln] = 1.0
        for k in range(4):
            cc = ('#ff4a3a', '#ffc040', '#4aff7a', '#4ac0ff')[int(rng.integers(0, 4))]
            img[y0 + 14:y0 + 16, x0 + 2 + k * 6:x0 + 4 + k * 6] = col(cc)
            em[y0 + 14:y0 + 16, x0 + 2 + k * 6:x0 + 4 + k * 6] = 1.0
        img[y0 + 19:y0 + 21, x0:x0 + 24] = col(c) * 0.6
    return np.clip(img, 0, 1), em


def tex_server(name):
    """Racks of computers: rows of units with blinking status lights (emissive)."""
    rng = _rng(name)
    xx = np.mgrid[0:T, 0:T][1]
    img = col('#22262c')[None, None, :] * (0.85 + 0.25 * fbm(T, rng, 12, 2)[..., None])
    em = np.zeros((T, T), np.float32)
    img[(xx % 32) < 2] = col('#3a3e46')
    for y in range(2, T - 4, 5):
        for x0 in (3, 35):
            img[y:y + 4, x0:x0 + 27] = col('#2e333a')
            img[y + 3, x0:x0 + 27] *= 0.6
            img[y + 1:y + 3, x0 + 19:x0 + 26] = col('#14181c')
            for _ in range(int(rng.integers(1, 5))):
                x = x0 + int(rng.integers(1, 17))
                cc = ('#4aff7a', '#4aff7a', '#ffc040', '#4ac0ff', '#ff4a3a')[int(rng.integers(0, 5))]
                img[y + 1, x] = col(cc)
                em[y + 1, x] = 1.0
    return np.clip(img, 0, 1), em


def tex_blast_door(name, c='#6a7078'):
    """A heavy sliding blast door: two leaves meeting in a toothed seam, hazard chevrons top and
    bottom, a red status light (emissive)."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    img = col(c)[None, None, :] * (0.85 + 0.25 * fbm(T, rng, 10, 3)[..., None])
    img[:, :3] = col(c) * 0.45
    img[:, -3:] = col(c) * 0.45
    for y in (16, 31, 46):
        img[y:y + 2, 5:59] = col(c) * 0.6
        img[y + 2, 5:59] = np.clip(col(c) * 1.25, 0, 1)
    bands = (yy >= 53) | (yy < 6)
    img[bands] = col('#1a1a1a')
    img[bands & (((xx + yy) // 5) % 2 == 0)] = col('#e0b030')
    seam = np.abs(xx - 31.5 - np.where((yy // 6) % 2 == 0, 1.5, -1.5)) < 1.2
    img[seam] = col('#121416')
    em = np.zeros((T, T), np.float32)
    light = np.hypot(xx - 31.5, yy - 10) < 2.2
    img[light] = col('#ff4030')
    em[light] = 1.0
    return np.clip(img, 0, 1), em


def tex_hazard(name):
    """Worn yellow-and-black hazard stripes: loading bays, airlocks, the edge of a drop."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    stripe = (((xx + yy) // 8) % 2 == 0)[..., None]
    img = np.where(stripe, col('#d8a828')[None, None, :], col('#1c1c1e')[None, None, :]).astype(np.float64)
    wear = np.clip((fbm(T, rng, 8, 4) - 0.55) * 4, 0, 1)
    img = img * (1 - 0.45 * wear[..., None]) + col('#6a6458')[None, None, :] * 0.45 * wear[..., None]
    return grain(np.clip(img, 0, 1), rng, 0.05)


def tex_deck(name, c='#4a4e54'):
    """Starship deck plating: big plates with a raised tread and corner bolts."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    img = col(c)[None, None, :] * (0.85 + 0.25 * fbm(T, rng, 10, 3)[..., None])
    tread = (((xx + (yy // 4 % 2) * 4) % 8) < 3) & (yy % 4 == 1)
    img[tread] *= 1.3
    img[((xx % 32) < 1) | ((yy % 32) < 1)] = col('#1e2024')
    img[np.hypot((xx % 32) - 3.5, (yy % 32) - 3.5) < 1.2] = col('#8a8e94')
    return grain(np.clip(img, 0, 1), rng, 0.03)


def tex_grid_floor(name, c='#0a0e18', line='#3ac8ff'):
    """A black floor ruled with glowing grid lines (emissive): holodecks, cyberspace, dreams.
    Glossy, so it reflects a little by default."""
    yy, xx = np.mgrid[0:T, 0:T]
    img = np.zeros((T, T, 3)) + col(c)[None, None, :]
    em = np.zeros((T, T), np.float32)
    major = ((xx % 32) < 1) | ((yy % 32) < 1)
    minor = (((xx % 8) < 1) | ((yy % 8) < 1)) & ~major
    img[minor] = col(line) * 0.3
    em[minor] = 0.35
    img[major] = col(line)
    em[major] = 1.0
    return img, em


def tex_viewport(name, c='#7a828c'):
    """An observation window (see-through): a slim hull frame round an opening from just above
    the floor to just under the top, with struts at the tile edges, so a row of them reads as one
    glass wall. Stack two for a window two storeys tall."""
    rgb, _ = tex_hull(name + 'h', c)
    rgb = rgb.copy()
    yy, xx = np.mgrid[0:T, 0:T]
    opening = (yy >= 6) & (yy < 56) & (xx >= 3) & (xx < 61)
    rim = ~opening & (yy >= 4) & (yy < 58) & (xx >= 1) & (xx < 63)
    rgb[rim] = col(c) * 0.4
    return np.clip(rgb, 0, 1), None, (~opening).astype(np.float32)


def tex_hex(name, c='#2a4a50', edge='#6a9a98'):
    """Hexagonal panelling: alien architecture, shield walls, hives of the tidier kind."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    cx = np.array([i * 16 + (j % 2) * 8 for j in range(4) for i in range(4)], float)
    cy = np.array([j * 16 for j in range(4) for i in range(4)], float)
    dx = np.abs(xx[..., None] - cx[None, None, :])
    dy = np.abs(yy[..., None] - cy[None, None, :])
    d = np.hypot(np.minimum(dx, T - dx), np.minimum(dy, T - dy))
    near = np.sort(d, axis=2)
    cell = np.argmin(d, axis=2)
    tone = 0.8 + 0.3 * ((cell * 29 + 3) % 5) / 4
    img = col(c)[None, None, :] * tone[..., None] * (0.85 + 0.25 * fbm(T, rng, 8, 3)[..., None])
    img[(near[..., 1] - near[..., 0]) < 1.6] = col(edge)
    return grain(np.clip(img, 0, 1), rng, 0.03)


def tex_alien_rock(name, c='#3a2a4a', vein='#4af0d0'):
    """Dark violet rock split by glowing veins (emissive): alien worlds, otherworldly caves."""
    img = tex_rock(name + 'r', c)
    v1 = np.abs(fbm(T, _rng(name + 'v'), 3, 4) - 0.5)
    v2 = np.abs(fbm(T, _rng(name + 'w'), 5, 3) - 0.5)
    line = (v1 < 0.018) | (v2 < 0.012)
    glow = (v1 < 0.05) & ~line
    img[glow] = img[glow] * 0.6 + col(vein) * 0.25
    img[line] = col(vein)
    em = np.zeros((T, T), np.float32)
    em[line] = 1.0
    return np.clip(img, 0, 1), em


def tex_alien_ground(name, c='#6a4a6e'):
    """Violet dust drifting over teal grit, with crystal flecks that catch the light."""
    rng = _rng(name)
    n = fbm(T, rng, 6, 4)
    img = col(c)[None, None, :] * (0.65 + 0.6 * n[..., None])
    drift = np.clip((fbm(T, _rng(name + 'd'), 4, 3) - 0.5) * 3, 0, 1)
    img = img * (1 - 0.4 * drift[..., None]) + col('#3a6a72')[None, None, :] * 0.4 * drift[..., None]
    s = rng.random((T, T))
    img[s > 0.985] = col('#c8f0ff')
    img[s < 0.04] *= 0.6
    return grain(np.clip(img, 0, 1), rng, 0.04)


def tex_organic(name, c='#7a2a3a'):
    """A living wall: ridged flesh with dark veins and wet highlights. Hives, infested ships."""
    rng = _rng(name)
    yy = np.mgrid[0:T, 0:T][0]
    n = fbm(T, rng, 6, 4)
    ridge = 0.5 + 0.5 * np.sin((yy + n * 18) * 2 * np.pi / 16)
    img = col(c)[None, None, :] * (0.55 + 0.6 * ridge[..., None]) * (0.85 + 0.3 * n[..., None])
    img[np.abs(fbm(T, _rng(name + 'v'), 4, 4) - 0.5) < 0.02] = col('#3a0c18')
    hi = (ridge > 0.92) & (rng.random((T, T)) > 0.6)
    img[hi] = np.clip(img[hi] * 1.5 + 0.1, 0, 1)
    img[rng.random((T, T)) > 0.992] = col('#1a0408')
    return np.clip(img, 0, 1)


def tex_sky_wall(name):
    """A wall painted as blue sky with white clouds: a door in it opens onto more sky."""
    rng = _rng(name)
    img = col('#6a9ede')[None, None, :] * (0.94 + 0.1 * fbm(T, rng, 4, 3)[..., None])
    cl = np.clip((fbm(T, _rng(name + 'c'), 4, 5) - 0.5) * 3.5, 0, 1)
    shade = np.clip(fbm(T, _rng(name + 's'), 6, 3) - 0.3, 0, 1)
    cloud = col('#f8fbff')[None, None, :] * (1 - 0.35 * shade[..., None])
    return np.clip(img * (1 - cl[..., None]) + cloud * cl[..., None], 0, 1)


def tex_cloud_floor(name, c='#f4f0f8'):
    """Ground made of cloud: soft billows with lavender hollows, to walk on in a dream."""
    n = fbm(T, _rng(name), 4, 5)
    m = fbm(T, _rng(name + 'm'), 8, 3)
    billow = np.clip((n - 0.35) * 2.2, 0, 1)
    img = col('#c8b8e0')[None, None, :] * (1 - billow[..., None]) + col(c)[None, None, :] * billow[..., None]
    return np.clip(img * (0.92 + 0.12 * m[..., None]), 0, 1)


def tex_obsidian(name, c='#16141c'):
    """Polished black stone slabs with a violet sheen. Reflective by default: mirror floors."""
    rng = _rng(name)
    img = col(c)[None, None, :] * (0.8 + 0.5 * fbm(T, rng, 5, 4)[..., None])
    streak = np.clip((fbm(T, _rng(name + 's'), 3, 4) - 0.55) * 3, 0, 1)
    img = img + col('#3a2a5a')[None, None, :] * streak[..., None] * 0.6
    yy, xx = np.mgrid[0:T, 0:T]
    img[((xx % 32) < 1) | ((yy % 32) < 1)] *= 0.6
    return np.clip(img, 0, 1)


def tex_fireplace(name):
    """A stone hearth under a wooden mantel with a log fire burning in it (emissive)."""
    rng = _rng(name)
    img = tex_stone(name + 's', '#8a7a6a', '#4a4038')
    em = np.zeros((T, T), np.float32)
    yy, xx = np.mgrid[0:T, 0:T]
    mantel = (yy >= 20) & (yy < 26)
    img[mantel] = (col('#5a3a22')[None, None, :] * (0.85 + 0.3 * rng.random((T, T)))[..., None])[mantel]
    img[yy == 25] = col('#3a2414')
    mouth = ((yy >= 34) & (yy < 62) & (np.abs(xx - 31.5) <= 17)) | \
            ((yy >= 30) & (yy < 34) & (np.abs(xx - 31.5) <= 17 - (34 - yy) * 1.5))
    img[mouth] = col('#140c0a')
    tall = 8 + 16 * fbm(T, _rng(name + 'f'), 8, 3)[20]
    flame = mouth & (yy >= 56 - tall[None, :]) & (yy < 56) & (np.abs(xx - 31.5) <= 13)
    heat = np.clip((56 - yy) / np.maximum(tall[None, :], 1), 0, 1)[..., None]
    fc = col('#fff0a0')[None, None, :] * (1 - heat) + col('#ff6020')[None, None, :] * heat
    img[flame] = fc[flame]
    em[flame] = 1.0
    logs = mouth & (yy >= 56) & (yy < 61) & (np.abs(xx - 31.5) <= 14)
    img[logs] = col('#3a2416')
    ember = logs & (rng.random((T, T)) > 0.75)
    img[ember] = col('#ff7030')
    em[ember] = 0.9
    return np.clip(img, 0, 1), em


def tex_star_chart(name, c='#141c34'):
    """Old star charts on deep blue paper, ruled in gold: constellations and an astrolabe ring.
    The stars faintly glow (emissive)."""
    rng = _rng(name)
    img = col(c)[None, None, :] * (0.8 + 0.35 * fbm(T, rng, 8, 3)[..., None])
    yy, xx = np.mgrid[0:T, 0:T]
    em = np.zeros((T, T), np.float32)
    gold = col('#c8a048')
    r = np.hypot(xx - 31.5, yy - 31.5)
    img[(np.abs(r - 25) < 0.7) | (np.abs(r - 14) < 0.5)] = gold * 0.75
    pts = rng.random((9, 2)) * 48 + 8
    lines = Image.new('L', (T, T), 0)
    ld = ImageDraw.Draw(lines)
    for a, b in ((0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (6, 7), (7, 8)):
        ld.line([tuple(pts[a]), tuple(pts[b])], fill=255, width=1)
    img[np.asarray(lines) > 0] = gold
    faint = rng.random((T, T)) > 0.985
    img[faint] = col('#d8d8f0') * 0.8
    em[faint] = 0.6
    for (x, y) in pts:
        img[int(y), int(x)] = col('#fff4c8')
        em[int(y), int(x)] = 1.0
    img[:, :1] = col('#3a2a1a')
    return np.clip(img, 0, 1), em


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
    'mud': _plain(tex_mud),
    'snow': _plain(tex_snow),
    'asphalt': _plain(tex_asphalt),
    'grate': _plain(tex_grate),
    'castle': _plain(tex_castle),
    'flagstone': _plain(tex_flagstone),
    'stained_glass': _em(tex_stained_glass),
    'ice': _plain(tex_ice),
    'snow_rock': _plain(tex_snow_rock),
    'slime_brick': _plain(tex_slime_brick),
    'door_wood': _plain(tex_door_wood),
    # sci-fi
    'hull': _em(tex_hull),
    'hull_lit': _em(tex_hull, strip='#7ae8ff'),
    'hull_red': _em(tex_hull, '#6a6e76', '#ff3a2a'),
    'hull_dark': _em(tex_hull, '#4a5058'),
    'tech_panel': _em(tex_tech_panel),
    'server': _em(tex_server),
    'blast_door': _em(tex_blast_door),
    'hazard': _plain(tex_hazard),
    'deck': _plain(tex_deck),
    'grid_floor': _em(tex_grid_floor),
    'hex_panel': _plain(tex_hex),
    # alien and dream
    'alien_rock': _em(tex_alien_rock),
    'alien_ground': _plain(tex_alien_ground),
    'organic': _plain(tex_organic),
    'sky_wall': _plain(tex_sky_wall),
    'cloud_floor': _plain(tex_cloud_floor),
    'obsidian': _plain(tex_obsidian),
    # the study
    'fireplace': _em(tex_fireplace),
    'star_chart': _em(tex_star_chart),
    # see-through: the renderer looks past their holes (fences, bars, railings, broken glass)
    'bars': _masked(tex_bars),
    'fence_iron': _masked(tex_fence_iron),
    'chainlink': _masked(tex_chainlink),
    'railing': _masked(tex_railing),
    'picket': _masked(tex_picket),
    'portcullis': _masked(tex_portcullis),
    'window_broken': _masked(tex_window_broken),
    'lattice': _masked(tex_lattice),
    'viewport': _masked(tex_viewport),
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


def spr_mushrooms():
    w, h = 20, 14
    im, d, em, de = _canvas(w, h)
    S = 4
    for (x, y, r, cap) in ((5, 9, 4, '#8a3a32'), (12, 7, 5, '#a04a3a'), (16, 11, 3, '#7a3028')):
        d.rectangle([(x - 1) * S, y * S, (x + 1) * S, 14 * S], fill='#d8cdb4')
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r // 2) * S], fill=cap)
        d.ellipse([(x - r + 1) * S, (y - r + 1) * S, (x - r + 3) * S, (y - r + 3) * S], fill='#e0d0c0')
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


# ---- sci-fi


def spr_stasis_pod():
    """An upright cryo pod: frosted glass lit from inside (emissive), a sleeper's shape."""
    w, h = 24, 56
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rounded_rectangle([1 * S, 2 * S, 23 * S, 50 * S], radius=10 * S, fill='#4a525c')
    d.rounded_rectangle([1 * S, 2 * S, 23 * S, 50 * S], radius=10 * S, outline='#2a3036', width=S)
    glass = [4 * S, 6 * S, 20 * S, 46 * S]
    d.rounded_rectangle(glass, radius=7 * S, fill='#9ae8f0')
    de.rounded_rectangle(glass, radius=7 * S, fill=170)
    d.ellipse([10 * S, 11 * S, 14 * S, 15 * S], fill='#5a9aaa')
    d.rounded_rectangle([9 * S, 16 * S, 15 * S, 38 * S], radius=2 * S, fill='#5a9aaa')
    de.ellipse([10 * S, 11 * S, 14 * S, 15 * S], fill=120)
    de.rounded_rectangle([9 * S, 16 * S, 15 * S, 38 * S], radius=2 * S, fill=120)
    for x in (6, 18):
        d.line([(x * S, 9 * S), (x * S, 43 * S)], fill='#d8f8ff', width=S // 2)
    d.rectangle([0, 48 * S, 24 * S, 56 * S], fill='#2e343c')
    for i, c in enumerate(('#4aff7a', '#ffc040', '#4ac0ff')):
        box = [(5 + i * 5) * S, 51 * S, (7 + i * 5) * S, 53 * S]
        d.rectangle(box, fill=c)
        de.rectangle(box, fill=255)
    return _finish(im, em, w, h)


def spr_hologram():
    """A wireframe world turning over its emitter, in glowing cyan (emissive)."""
    w, h = 26, 40
    im, d, em, de = _canvas(w, h)
    S = 4
    cyan, dim = '#6af0ff', '#3ab0c8'
    for draw, a, b in ((d, cyan, dim), (de, 255, 190)):
        draw.ellipse([3 * S, 1 * S, 23 * S, 21 * S], outline=a, width=S)
        for k in (4, 8):
            draw.ellipse([(13 - k) * S, 1 * S, (13 + k) * S, 21 * S], outline=b, width=S // 2)
        for y in (6, 11, 16):
            half = float(np.sqrt(max(0.0, 100 - (y - 11) ** 2)))
            draw.line([((13 - half) * S, y * S), ((13 + half) * S, y * S)], fill=b, width=S // 2)
        for x in (8, 13, 18):
            draw.line([(x * S, 22 * S), (13 * S, 33 * S)], fill=b, width=S // 2)
    d.ellipse([6 * S, 32 * S, 20 * S, 37 * S], fill='#3a4048')
    d.ellipse([9 * S, 32 * S, 17 * S, 34 * S], fill=cyan)
    de.ellipse([9 * S, 32 * S, 17 * S, 34 * S], fill=255)
    d.rectangle([8 * S, 35 * S, 18 * S, 40 * S], fill='#2a2e34')
    return _finish(im, em, w, h)


def spr_sci_crate():
    """A ribbed metal cargo crate with hazard corners and a lit label (emissive)."""
    w, h = 24, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([0, 2 * S, 24 * S, 20 * S], fill='#5a6068')
    d.rectangle([0, 0, 24 * S, 3 * S], fill='#7a8088')
    d.rectangle([2 * S, 5 * S, 22 * S, 18 * S], outline='#3a3e44', width=S)
    for x0 in (0, 20):
        for k in range(3):
            d.polygon([((x0 + k * 2) * S, 20 * S), ((x0 + k * 2 + 1) * S, 20 * S),
                       ((x0 + k * 2 + 4) * S, 16 * S), ((x0 + k * 2 + 3) * S, 16 * S)], fill='#e0b030')
    d.rectangle([9 * S, 8 * S, 15 * S, 11 * S], fill='#6af0ff')
    de.rectangle([9 * S, 8 * S, 15 * S, 11 * S], fill=210)
    return _finish(im, em, w, h)


def spr_drone():
    """A hovering drone with one glowing eye (emissive). Float it with z (0.6-1.2)."""
    w, h = 22, 14
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([0, 5 * S, 22 * S, 7 * S], fill='#2a2e34')
    d.rectangle([0, 3 * S, 5 * S, 4 * S], fill='#8a9098')
    d.rectangle([17 * S, 3 * S, 22 * S, 4 * S], fill='#8a9098')
    d.ellipse([5 * S, 1 * S, 17 * S, 13 * S], fill='#3a3e46')
    d.ellipse([7 * S, 2 * S, 15 * S, 7 * S], fill='#5a606a')
    d.ellipse([9 * S, 6 * S, 13 * S, 10 * S], fill='#ff4030')
    de.ellipse([9 * S, 6 * S, 13 * S, 10 * S], fill=255)
    return _finish(im, em, w, h)


def spr_lander():
    """A small landing craft on splayed legs, cockpit and engines lit (emissive)."""
    w, h = 64, 44
    im, d, em, de = _canvas(w, h)
    S = 4
    hull, dark = '#c8ccd2', '#6a6e76'
    for x0, x1 in ((14, 6), (50, 58), (32, 32)):
        d.line([(x0 * S, 28 * S), (x1 * S, 41 * S)], fill=dark, width=2 * S)
        d.rectangle([(x1 - 3) * S, 41 * S, (x1 + 3) * S, 44 * S], fill='#4a4e56')
    d.ellipse([22 * S, 28 * S, 42 * S, 33 * S], fill='#ffb060')
    de.ellipse([22 * S, 28 * S, 42 * S, 33 * S], fill=200)
    d.polygon([(10 * S, 30 * S), (54 * S, 30 * S), (60 * S, 20 * S), (48 * S, 6 * S), (16 * S, 6 * S),
               (4 * S, 20 * S)], fill=hull)
    d.polygon([(16 * S, 6 * S), (48 * S, 6 * S), (44 * S, 1 * S), (20 * S, 1 * S)], fill='#a8acb4')
    d.polygon([(4 * S, 20 * S), (60 * S, 20 * S), (54 * S, 30 * S), (10 * S, 30 * S)], fill='#a8acb4')
    d.rectangle([4 * S, 19 * S, 60 * S, 21 * S], fill=dark)
    cockpit = [(24 * S, 8 * S), (40 * S, 8 * S), (43 * S, 15 * S), (21 * S, 15 * S)]
    d.polygon(cockpit, fill='#7ae0ff')
    de.polygon(cockpit, fill=190)
    d.line([(32 * S, 8 * S), (32 * S, 15 * S)], fill=dark, width=S)
    d.rectangle([12 * S, 10 * S, 17 * S, 13 * S], fill='#e07a2a')
    for x, c in ((6, '#ff3020'), (57, '#30ff60')):
        d.rectangle([x * S, 18 * S, (x + 2) * S, 20 * S], fill=c)
        de.rectangle([x * S, 18 * S, (x + 2) * S, 20 * S], fill=255)
    return _finish(im, em, w, h)


def spr_antenna():
    """A lattice mast with a dish and a red warning light on top (emissive)."""
    w, h = 20, 64
    im, d, em, de = _canvas(w, h)
    S = 4
    d.line([(7 * S, 63 * S), (9 * S, 8 * S)], fill='#8a8e96', width=S)
    d.line([(13 * S, 63 * S), (11 * S, 8 * S)], fill='#8a8e96', width=S)
    for y in range(12, 62, 6):
        d.line([(8 * S, y * S), (12 * S, (y + 6) * S)], fill='#6a6e76', width=S // 2)
        d.line([(12 * S, y * S), (8 * S, (y + 6) * S)], fill='#6a6e76', width=S // 2)
    d.ellipse([0, 10 * S, 11 * S, 22 * S], fill='#c8ccd2')
    d.ellipse([2 * S, 12 * S, 9 * S, 20 * S], fill='#9aa0a8')
    d.line([(5 * S, 16 * S), (10 * S, 14 * S)], fill='#4a4e56', width=S // 2)
    d.ellipse([8 * S, 1 * S, 12 * S, 5 * S], fill='#ff3020')
    de.ellipse([8 * S, 1 * S, 12 * S, 5 * S], fill=255)
    d.line([(10 * S, 5 * S), (10 * S, 9 * S)], fill='#8a8e96', width=S // 2)
    d.rectangle([4 * S, 61 * S, 16 * S, 64 * S], fill='#4a4e56')
    return _finish(im, em, w, h)


# ---- alien


def spr_alien_plant():
    """A tall alien stalk hung with glowing seed pods (emissive). Pair it with a light."""
    w, h = 22, 44
    im, d, em, de = _canvas(w, h)
    S = 4
    pts = [(11, 44), (10, 35), (12, 26), (10, 17), (12, 8), (11, 3)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill='#2e5a4c', width=2 * S)
    for (x, y, dx) in ((10, 34, -7), (12, 26, 7), (10, 18, -6)):
        d.polygon([(x * S, y * S), ((x + dx) * S, (y - 4) * S), ((x + dx * 0.6) * S, (y + 1) * S)], fill='#2a7a62')
    for (x, y, r) in ((4, 29, 3), (18, 21, 3), (5, 13, 2.5), (14, 5, 3), (17, 36, 2)):
        box = [(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S]
        d.ellipse(box, fill='#ff6ad8')
        de.ellipse(box, fill=230)
        d.ellipse([(x - r / 2) * S, (y - r / 2) * S, x * S, y * S], fill='#ffd0f4')
    return _finish(im, em, w, h)


def spr_monolith():
    """A tall black slab, perfectly smooth. It was here before anyone."""
    w, h = 16, 56
    im, d, em, de = _canvas(w, h)
    S = 4
    d.rectangle([1 * S, 0, 15 * S, 56 * S], fill='#0a0a0e')
    d.rectangle([1 * S, 0, 2 * S, 56 * S], fill='#2a2a36')
    d.rectangle([1 * S, 0, 15 * S, 1 * S], fill='#2a2a36')
    return _finish(im, em, w, h)


def spr_orb():
    """A floating sphere of light (emissive, with its own glow). Hang it in the air with z."""
    w = h = 14
    im, d, em, de = _canvas(w, h)
    S = 4
    for r, c, e in ((7, '#a888ff', 170), (5, '#d8c8ff', 230), (3, '#ffffff', 255)):
        box = [(7 - r) * S, (7 - r) * S, (7 + r) * S, (7 + r) * S]
        d.ellipse(box, fill=c)
        de.ellipse(box, fill=e)
    return _finish(im, em, w, h)


def spr_alien_egg():
    """A leathery egg with a glowing slit (emissive). Something inside is nearly ready."""
    w, h = 16, 20
    im, d, em, de = _canvas(w, h)
    S = 4
    d.ellipse([1 * S, 2 * S, 15 * S, 20 * S], fill='#5a4a3a')
    d.ellipse([3 * S, 4 * S, 10 * S, 13 * S], fill='#76664e')
    for (x0, y0, x1, y1) in ((4, 8, 6, 18), (11, 6, 12, 17), (8, 12, 9, 19)):
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill='#3a2a20', width=S // 2)
    slit = [(8 * S, 2 * S), (10 * S, 5 * S), (8 * S, 8 * S), (6 * S, 5 * S)]
    d.polygon(slit, fill='#a0ff60')
    de.polygon(slit, fill=220)
    return _finish(im, em, w, h)


def spr_floating_rock():
    """A chunk of earth adrift in the air: grass on top, roots trailing below. Set z."""
    w, h = 40, 44
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(2 * S, 8 * S), (38 * S, 8 * S), (31 * S, 22 * S), (24 * S, 33 * S), (20 * S, 42 * S),
               (15 * S, 32 * S), (8 * S, 21 * S)], fill='#6a5a4a')
    d.polygon([(20 * S, 8 * S), (38 * S, 8 * S), (31 * S, 22 * S), (24 * S, 33 * S), (20 * S, 42 * S)], fill='#4e4236')
    for (x, y) in ((12, 20), (26, 18), (19, 28)):
        d.ellipse([(x - 2) * S, (y - 1) * S, (x + 2) * S, (y + 1) * S], fill='#8a7a64')
    for (x0, y0, x1, y1) in ((14, 30, 12, 38), (25, 30, 28, 37), (20, 40, 21, 44)):
        d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill='#3a2e22', width=S // 2)
    d.ellipse([1 * S, 3 * S, 39 * S, 13 * S], fill='#3e7a32')
    d.ellipse([3 * S, 3 * S, 37 * S, 10 * S], fill='#5a9a44')
    return _finish(im, em, w, h)


# ---- dream


def spr_door_frame():
    """A door standing on its own in the open, swung ajar. Through it: whatever is behind."""
    w, h = 30, 48
    im, d, em, de = _canvas(w, h)
    S = 4
    paint, shadow = '#ece4d4', '#b8ae9c'
    d.rectangle([8 * S, 0, 28 * S, 4 * S], fill=paint)
    d.rectangle([8 * S, 0, 11 * S, 46 * S], fill=paint)
    d.rectangle([25 * S, 0, 28 * S, 46 * S], fill=paint)
    d.rectangle([10 * S, 4 * S, 11 * S, 46 * S], fill=shadow)
    d.rectangle([8 * S, 45 * S, 28 * S, 48 * S], fill='#8a7a64')
    leaf = [(8 * S, 4 * S), (1 * S, 7 * S), (1 * S, 46 * S), (8 * S, 45 * S)]
    d.polygon(leaf, fill='#4a6a8a')
    d.line([(4 * S, 9 * S), (4 * S, 42 * S)], fill='#3a5470', width=S // 2)
    d.ellipse([2 * S, 25 * S, 4 * S, 27 * S], fill='#c8a040')
    return _finish(im, em, w, h)


def spr_sky_whale():
    """A whale swimming through the sky with stars along its back. Float it high with z."""
    w, h = 64, 28
    im, d, em, de = _canvas(w, h)
    S = 4
    body, dark, belly = '#3a4a7a', '#2a3660', '#a8b8d8'
    d.polygon([(47 * S, 13 * S), (56 * S, 15 * S), (63 * S, 5 * S), (60 * S, 15 * S), (64 * S, 25 * S),
               (56 * S, 18 * S)], fill=dark)
    d.ellipse([6 * S, 4 * S, 52 * S, 24 * S], fill=body)
    d.ellipse([0, 6 * S, 24 * S, 24 * S], fill=body)
    d.chord([2 * S, 10 * S, 48 * S, 26 * S], 0, 180, fill=belly)
    for x in range(8, 40, 4):
        d.line([(x * S, 20 * S), ((x + 3) * S, 22 * S)], fill='#8898b8', width=S // 2)
    d.polygon([(22 * S, 18 * S), (31 * S, 18 * S), (24 * S, 27 * S)], fill=dark)
    d.ellipse([7 * S, 13 * S, 9 * S, 15 * S], fill='#e8e8f0')
    for (x, y) in ((16, 7), (22, 5), (29, 6), (35, 7), (41, 9), (26, 9)):
        d.rectangle([x * S, y * S, (x + 1) * S, (y + 1) * S], fill='#fff4c8')
        de.rectangle([x * S, y * S, (x + 1) * S, (y + 1) * S], fill=255)
    return _finish(im, em, w, h)


def spr_koi():
    """A koi swimming through the air. Float it with z; flip it to turn it round."""
    w, h = 26, 12
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(19 * S, 6 * S), (26 * S, 1 * S), (24 * S, 6 * S), (26 * S, 11 * S)], fill='#f2a050')
    d.ellipse([2 * S, 2 * S, 21 * S, 10 * S], fill='#f08a3a')
    d.ellipse([7 * S, 2 * S, 13 * S, 6 * S], fill='#f4f0e8')
    d.ellipse([13 * S, 5 * S, 18 * S, 9 * S], fill='#f4f0e8')
    d.polygon([(9 * S, 9 * S), (13 * S, 9 * S), (10 * S, 12 * S)], fill='#f2a050')
    d.ellipse([4 * S, 4 * S, 6 * S, 6 * S], fill='#1a1a1a')
    return _finish(im, em, w, h)


def spr_pocket_watch():
    """A great pocket watch hanging in the air on its chain. Float it with z."""
    w, h = 28, 36
    im, d, em, de = _canvas(w, h)
    S = 4
    for y in range(0, 6, 2):
        d.ellipse([12 * S, y * S, 16 * S, (y + 3) * S], outline='#c8a040', width=S // 2)
    d.rectangle([12 * S, 5 * S, 16 * S, 8 * S], fill='#b08a34')
    d.ellipse([1 * S, 7 * S, 27 * S, 33 * S], fill='#c8a040')
    d.ellipse([3 * S, 9 * S, 25 * S, 31 * S], fill='#f4eedc')
    for k in range(12):
        a = k * np.pi / 6
        x, y = 14 + 9.5 * np.sin(a), 20 - 9.5 * np.cos(a)
        d.rectangle([(x - 0.5) * S, (y - 0.5) * S, (x + 0.5) * S, (y + 0.5) * S], fill='#3a3028')
    d.line([(14 * S, 20 * S), (9 * S, 16 * S)], fill='#2a2420', width=S)
    d.line([(14 * S, 20 * S), (19 * S, 14 * S)], fill='#2a2420', width=S // 2)
    return _finish(im, em, w, h)


def _chess(w, h, crown):
    im, d, em, de = _canvas(w, h)
    S = 4
    c, s, hi = '#e8e4dc', '#bcb6aa', '#fbf8f2'
    cx = w / 2
    d.rounded_rectangle([1 * S, (h - 5) * S, (w - 1) * S, h * S], radius=S, fill=c)
    d.rectangle([3 * S, (h - 8) * S, (w - 3) * S, (h - 5) * S], fill=s)
    top = 12 if crown else 11
    d.polygon([((cx - 4) * S, (h - 8) * S), ((cx + 4) * S, (h - 8) * S), ((cx + 2) * S, top * S),
               ((cx - 2) * S, top * S)], fill=c)
    d.polygon([((cx + 1) * S, (h - 8) * S), ((cx + 4) * S, (h - 8) * S), ((cx + 2) * S, top * S),
               ((cx + 1) * S, top * S)], fill=s)
    d.rectangle([(cx - 4) * S, (top - 1) * S, (cx + 4) * S, (top + 1) * S], fill=s)
    if crown:
        d.polygon([((cx - 4) * S, (top - 1) * S), ((cx + 4) * S, (top - 1) * S), ((cx + 5) * S, 6 * S),
                   ((cx - 5) * S, 6 * S)], fill=c)
        d.rectangle([(cx - 1) * S, 0, (cx + 1) * S, 6 * S], fill=c)
        d.rectangle([(cx - 3) * S, 2 * S, (cx + 3) * S, 4 * S], fill=c)
    else:
        d.ellipse([(cx - 5) * S, 1 * S, (cx + 5) * S, (top + 0.5) * S], fill=c)
        d.ellipse([(cx - 3) * S, 2 * S, (cx - 1) * S, 5 * S], fill=hi)
    return _finish(im, em, w, h)


def spr_chess_pawn():
    """A giant marble pawn. Tint it dark for the other side."""
    return _chess(18, 30, False)


def spr_chess_king():
    """A giant marble king, crowned and crossed. Tint it dark for the other side."""
    return _chess(18, 48, True)


def spr_balloon():
    """A striped hot-air balloon drifting overhead. Float it high with z."""
    w, h = 30, 46
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(5 * S, 22 * S), (25 * S, 22 * S), (19 * S, 34 * S), (11 * S, 34 * S)], fill='#d84a3a')
    for (x0, x1), c in (((1, 29), '#d84a3a'), ((7, 23), '#f0c860'), ((12, 18), '#d84a3a')):
        d.ellipse([x0 * S, 0, x1 * S, 30 * S], fill=c)
    d.polygon([(11 * S, 22 * S), (19 * S, 22 * S), (17 * S, 34 * S), (13 * S, 34 * S)], fill='#f0c860')
    for x0, x1 in ((11, 12), (19, 18)):
        d.line([(x0 * S, 34 * S), (x1 * S, 40 * S)], fill='#4a3a2a', width=S // 2)
    d.rectangle([11 * S, 40 * S, 19 * S, 46 * S], fill='#7a5a32')
    d.rectangle([11 * S, 40 * S, 19 * S, 41 * S], fill='#5a3e20')
    return _finish(im, em, w, h)


# ---- the study


def spr_telescope():
    """A brass refracting telescope on a wooden tripod, pointed at the sky."""
    w, h = 32, 40
    im, d, em, de = _canvas(w, h)
    S = 4
    for x1 in (7, 19, 31):
        d.line([(19 * S, 18 * S), (x1 * S, 40 * S)], fill='#5a3a22', width=S + S // 2)
    d.line([(6 * S, 4 * S), (25 * S, 18 * S)], fill='#b08a3c', width=4 * S)
    d.line([(7 * S, 3 * S), (25 * S, 16 * S)], fill='#e0c070', width=S)
    d.ellipse([2 * S, 0, 9 * S, 7 * S], fill='#7a5a22')
    d.ellipse([3 * S, 1 * S, 8 * S, 6 * S], fill='#2a3a4a')
    d.line([(25 * S, 18 * S), (28 * S, 21 * S)], fill='#3a2a1a', width=2 * S)
    d.ellipse([16 * S, 13 * S, 22 * S, 19 * S], fill='#5a3a22')
    return _finish(im, em, w, h)


def spr_globe():
    """A globe on a turned wooden stand inside its brass meridian."""
    w, h = 20, 28
    im, d, em, de = _canvas(w, h)
    S = 4
    d.ellipse([2 * S, 1 * S, 18 * S, 17 * S], fill='#3a6a8a')
    for (x0, y0, x1, y1) in ((5, 4, 10, 9), (11, 8, 15, 14), (6, 11, 9, 15)):
        d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill='#c8b070')
    d.ellipse([4 * S, 3 * S, 9 * S, 7 * S], outline='#6a9aba', width=S // 2)
    d.arc([0, 0, 20 * S, 18 * S], 100, 260, fill='#c8a040', width=S)
    d.rectangle([9 * S, 18 * S, 11 * S, 23 * S], fill='#5a3a22')
    d.ellipse([4 * S, 22 * S, 16 * S, 28 * S], fill='#4a3020')
    return _finish(im, em, w, h)


def spr_armchair():
    """A deep wingback reading chair in oxblood leather."""
    w, h = 28, 26
    im, d, em, de = _canvas(w, h)
    S = 4
    leather, dark, hi = '#6a2a26', '#4a1a18', '#8a3e36'
    d.rounded_rectangle([4 * S, 0, 24 * S, 19 * S], radius=3 * S, fill=leather)
    for x0 in (1, 21):
        d.rounded_rectangle([x0 * S, 3 * S, (x0 + 6) * S, 21 * S], radius=2 * S, fill=dark)
    d.rectangle([5 * S, 15 * S, 23 * S, 20 * S], fill=hi)
    for x in (9, 14, 19):
        for y in (5, 10):
            d.rectangle([x * S, y * S, (x + 1) * S, (y + 1) * S], fill=dark)
    for x0 in (2, 24):
        d.rectangle([x0 * S, 21 * S, (x0 + 2) * S, 26 * S], fill='#2a1a10')
    return _finish(im, em, w, h)


def spr_book_stack():
    """A tottering pile of books."""
    w, h = 20, 18
    im, d, em, de = _canvas(w, h)
    S = 4
    rows = ((1, 18, 14, 18, '#7a2a2a'), (3, 17, 10, 14, '#2a4a6a'), (2, 15, 7, 10, '#3a5a32'),
            (5, 19, 3, 7, '#8a6a2a'), (4, 14, 0, 3, '#5a2a4a'))
    for (x0, x1, y0, y1, c) in rows:
        d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=c)
        d.rectangle([x0 * S, y0 * S, x1 * S, (y0 + 1) * S], fill='#e8dcc0')
        d.line([((x0 + 2) * S, y0 * S), ((x0 + 2) * S, y1 * S)], fill='#c8a040', width=S // 2)
    return _finish(im, em, w, h)


def spr_open_book():
    """An open book with softly glowing pages (emissive). Float a few with z for magic."""
    w, h = 22, 12
    im, d, em, de = _canvas(w, h)
    S = 4
    d.polygon([(0, 4 * S), (11 * S, 6 * S), (22 * S, 4 * S), (22 * S, 11 * S), (11 * S, 12 * S),
               (0, 11 * S)], fill='#6a2a22')
    for x0, x1 in ((1, 11), (11, 21)):
        page = [(x0 * S, (2 if x0 == 1 else 4) * S), (x1 * S, (4 if x0 == 1 else 2) * S),
                (x1 * S, 10 * S), (x0 * S, 10 * S)]
        d.polygon(page, fill='#fff4dc')
        de.polygon(page, fill=120)
    for y in (5, 7):
        d.line([(2 * S, y * S), (9 * S, (y + 1) * S)], fill='#8a7a62', width=S // 2)
        d.line([(13 * S, (y + 1) * S), (20 * S, y * S)], fill='#8a7a62', width=S // 2)
    return _finish(im, em, w, h)


def spr_writing_desk():
    """A writing desk with papers, an inkwell and quill, and a lit candle (emissive)."""
    w, h = 44, 30
    im, d, em, de = _canvas(w, h)
    S = 4
    wood, dark = '#6a4428', '#4a2e1a'
    d.rectangle([0, 12 * S, 44 * S, 16 * S], fill=wood)
    d.rectangle([0, 12 * S, 44 * S, 13 * S], fill='#8a6040')
    d.rectangle([2 * S, 16 * S, 14 * S, 27 * S], fill=dark)
    for y in (18, 22):
        d.rectangle([4 * S, y * S, 12 * S, (y + 3) * S], fill=wood)
        d.rectangle([7 * S, (y + 1) * S, 9 * S, (y + 2) * S], fill='#c8a040')
    for x in (2, 40):
        d.rectangle([x * S, 16 * S, (x + 2) * S, 30 * S], fill=dark)
    d.polygon([(16 * S, 12 * S), (28 * S, 12 * S), (27 * S, 10 * S), (17 * S, 10 * S)], fill='#f0e6d0')
    d.rectangle([31 * S, 9 * S, 35 * S, 12 * S], fill='#1a1a2a')
    d.line([(33 * S, 9 * S), (37 * S, 1 * S)], fill='#f4f0e8', width=S)
    d.rectangle([6 * S, 6 * S, 8 * S, 12 * S], fill='#efe6d0')
    d.ellipse([5 * S, 2 * S, 9 * S, 7 * S], fill='#ffd060')
    de.ellipse([5 * S, 2 * S, 9 * S, 7 * S], fill=255)
    return _finish(im, em, w, h)


def spr_orrery():
    """A brass orrery: planets on their arms round a glowing sun (emissive)."""
    w, h = 32, 34
    im, d, em, de = _canvas(w, h)
    S = 4
    brass = '#b08a3c'
    d.line([(16 * S, 14 * S), (16 * S, 30 * S)], fill=brass, width=S)
    d.ellipse([8 * S, 29 * S, 24 * S, 34 * S], fill='#4a3020')
    d.ellipse([1 * S, 6 * S, 31 * S, 18 * S], outline=brass, width=S // 2)
    d.ellipse([6 * S, 8 * S, 26 * S, 16 * S], outline=brass, width=S // 2)
    for (x, y, r, c) in ((2, 11, 2, '#c8784a'), (25, 9, 1.5, '#6a9ac8'), (29, 15, 2.5, '#d8b880'),
                         (8, 15, 1.5, '#a8a8a0')):
        d.line([(16 * S, 12 * S), (x * S, y * S)], fill=brass, width=S // 2)
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    d.ellipse([13 * S, 9 * S, 19 * S, 15 * S], fill='#ffd060')
    de.ellipse([13 * S, 9 * S, 19 * S, 15 * S], fill=255)
    return _finish(im, em, w, h)


SPRITES = {
    'lamp_post': spr_lamp_post, 'statue': spr_statue, 'flowers': spr_flowers,
    'barrel': spr_barrel, 'crate': spr_crate, 'lantern': spr_lantern,
    'candles': spr_candles, 'bed': spr_bed, 'wheelchair': spr_wheelchair, 'bench': spr_bench,
    'rowboat': spr_rowboat, 'fountain': spr_fountain,
    'mushrooms': spr_mushrooms, 'signpost': spr_signpost,
    'campfire': spr_campfire, 'locker': spr_locker, 'console': spr_console, 'buoy': spr_buoy,
    'gravestone': spr_gravestone,
    'sconce': spr_sconce, 'ceiling_lamp': spr_ceiling_lamp, 'chandelier': spr_chandelier,
    'brazier': spr_brazier, 'painting': spr_painting, 'banner': spr_banner,
    'wall_clock': spr_wall_clock, 'pipe_valve': spr_pipe_valve, 'rubble': spr_rubble,
    'bones': spr_bones, 'sack': spr_sack, 'bucket': spr_bucket, 'broken_barrel': spr_broken_barrel,
    'reeds': spr_reeds, 'ivy_hang': spr_ivy_hang,
    'throne': spr_throne, 'armor': spr_armor, 'chains': spr_chains, 'chest': spr_chest,
    'table': spr_table, 'pew': spr_pew, 'stalagmite': spr_stalagmite, 'crystal': spr_crystal,
    'glowshroom': spr_glowshroom, 'snowy_pine': spr_snowy_pine, 'snowman': spr_snowman,
    'grave_cross': spr_grave_cross, 'ladder': spr_ladder, 'lectern': spr_lectern,
    'stasis_pod': spr_stasis_pod, 'hologram': spr_hologram, 'sci_crate': spr_sci_crate,
    'drone': spr_drone, 'lander': spr_lander, 'antenna': spr_antenna,
    'alien_plant': spr_alien_plant, 'monolith': spr_monolith, 'orb': spr_orb, 'alien_egg': spr_alien_egg,
    'floating_rock': spr_floating_rock,
    'door_frame': spr_door_frame, 'sky_whale': spr_sky_whale, 'koi': spr_koi,
    'pocket_watch': spr_pocket_watch, 'chess_pawn': spr_chess_pawn, 'chess_king': spr_chess_king,
    'balloon': spr_balloon,
    'telescope': spr_telescope, 'globe': spr_globe, 'armchair': spr_armchair,
    'book_stack': spr_book_stack, 'open_book': spr_open_book, 'writing_desk': spr_writing_desk,
    'orrery': spr_orrery,
}

# default world size (height in map units) for each sprite
SPRITE_HEIGHT = {
    'lamp_post': 1.6, 'statue': 1.5, 'flowers': 0.35, 'tree': 2.6, 'barrel': 0.45,
    'crate': 0.4, 'lantern': 0.3, 'candles': 0.2, 'bed': 0.4, 'wheelchair': 0.45, 'bench': 0.35,
    'rowboat': 0.3, 'fountain': 0.9,
    'pine': 3.4, 'dead_tree': 2.9, 'stump': 0.3, 'log': 0.28, 'bush': 0.5, 'mushrooms': 0.12,
    'boulder': 0.55, 'signpost': 1.3, 'campfire': 0.4, 'locker': 1.0, 'console': 0.85, 'buoy': 0.5,
    'gravestone': 0.6,
    'sconce': 0.32, 'ceiling_lamp': 0.3, 'chandelier': 0.45, 'brazier': 0.85,
    'painting': 0.45, 'banner': 0.95, 'wall_clock': 0.28, 'pipe_valve': 0.32, 'rubble': 0.34,
    'bones': 0.22, 'sack': 0.42, 'bucket': 0.32, 'broken_barrel': 0.46,
    'reeds': 0.8, 'ivy_hang': 0.8,
    'throne': 0.95, 'armor': 0.66, 'chains': 0.6, 'chest': 0.3, 'table': 0.36, 'pew': 0.42,
    'stalagmite': 0.8, 'crystal': 0.36, 'glowshroom': 0.16, 'snowy_pine': 3.4, 'snowman': 0.62,
    'grave_cross': 0.55, 'ladder': 1.0, 'lectern': 0.5,
    'stasis_pod': 1.0, 'hologram': 0.55, 'sci_crate': 0.35, 'drone': 0.22, 'lander': 1.6,
    'antenna': 2.4, 'alien_plant': 1.1, 'monolith': 2.2, 'orb': 0.2, 'alien_egg': 0.35,
    'floating_rock': 1.6, 'door_frame': 1.1, 'sky_whale': 2.0, 'koi': 0.35, 'pocket_watch': 0.8,
    'chess_pawn': 0.9, 'chess_king': 1.5, 'balloon': 2.6, 'telescope': 0.8, 'globe': 0.45,
    'armchair': 0.6, 'book_stack': 0.22, 'open_book': 0.12, 'writing_desk': 0.55, 'orrery': 0.6,
}

# Placement fields a built-in prop carries unless the scene overrides them, like a character's
# `defaults`: things that glow bring their own soft aura.
PROP_DEFAULTS = {
    'orb': {'aura': {'color': [0.72, 0.6, 1.0], 'strength': 0.6, 'radius': 0.3}},
    'hologram': {'aura': {'color': [0.4, 0.9, 1.0], 'strength': 0.35, 'radius': 0.18}},
    # low plants stand as crossed planes (see biomes.py for the jungle's)
    'bush': {'planes': 3}, 'reeds': {'planes': 3}, 'flowers': {'planes': 2},
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
    'alien': ['rocks', 'rocks', 'crystal', 'glowshroom', 'alien_plant', 'alien_egg'],
    'derelict': ['rubble', 'rubble', 'sci_crate', 'bones', 'rocks', 'alien_egg'],
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
        out.update(PROP_DEFAULTS.get(spec, {}))
    return out


def get_sprite(spec, defs=None, view='front'):
    """spec: built-in prop name, character name, a name defined in the scene's sprite_defs, or a PNG path.

    `view` 'back' gives the character from behind when its definition has a `back` grid (every
    built-in character does); anything without one looks the same from both sides.
    """
    from characters import CHARACTERS
    defs = defs or {}
    if view == 'back':
        d = defs.get(spec) if spec in defs else CHARACTERS.get(spec)
        if d and d.get('back'):
            key = 'back:' + (json_key(d) if spec in defs else spec)
            if key not in _scache:
                _scache[key] = sprite_from_pixels(dict(d, pixels=d['back']))
            return _scache[key]
    if spec in defs:
        key = 'def:' + json_key(defs[spec])
        if key not in _scache:
            _scache[key] = sprite_from_pixels(defs[spec])
        return _scache[key]
    if spec in _scache:
        return _scache[spec]
    if isinstance(spec, str) and spec.startswith('facade:'):
        import buildings                  # one layer of one building's front (see buildings.py)
        _scache[spec] = buildings.layer_image(spec)
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
    'hull': 0.6, 'hull_lit': 0.5, 'hull_red': 0.6, 'hull_dark': 0.6, 'tech_panel': 0.5, 'server': 0.4,
    'blast_door': 0.7, 'hazard': 1.2, 'deck': 1.0, 'grid_floor': 0.2, 'hex_panel': 0.8,
    'alien_rock': 1.8, 'alien_ground': 2.0, 'organic': 1.6, 'sky_wall': 0.3, 'cloud_floor': 0.5,
    'obsidian': 0.6, 'fireplace': 0.6, 'star_chart': 0.4, 'viewport': 0.6,
}


# How mirror-like a floor is by default. Any floor cell can set its own "reflect" (wet asphalt,
# polished marble); puddle decals carry their own (DECAL_REFLECT).
TEXTURE_REFLECT = {'water': 0.5, 'ice': 0.38, 'obsidian': 0.45, 'grid_floor': 0.3}
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
                     'chains', 'ladder', 'crystal', 'glowshroom', 'hologram', 'drone', 'orb',
                     'floating_rock', 'sky_whale', 'koi', 'pocket_watch', 'balloon', 'open_book'}

# ---------------------------------------------------------------- jungle, ruins and beach
# Drawn with the pixel-art toolkit (scripts/pixelart.py) in scripts/biomes.py, which adds its
# textures, props, scatter sets and decals to the tables here.
import biomes  # noqa: E402

TEXTURES.update(biomes.TEXTURES)
TEXTURE_REFLECT.update(biomes.TEXTURE_REFLECT)
TEXTURE_NOISE.update(biomes.TEXTURE_NOISE)
SPRITES.update(biomes.SPRITES)
SPRITE_HEIGHT.update(biomes.SPRITE_HEIGHT)
PROP_DEFAULTS.update(biomes.PROP_DEFAULTS)
NO_CONTACT_SHADOW |= biomes.NO_CONTACT_SHADOW
DEBRIS_SETS.update(biomes.DEBRIS_SETS)
DECALS.update(biomes.DECALS)
FRINGES = dict(biomes.FRINGES)

# ---------------------------------------------------------------- the temperate forest
# Spruce, oak, birch, bushes, the forest floor, bark and leaf walls, and the `forest` fringe,
# drawn with the same toolkit in scripts/forest.py; they replace the first, flat versions.
import forest  # noqa: E402

TEXTURES.update(forest.TEXTURES)
SPRITES.update(forest.SPRITES)
SPRITE_HEIGHT.update(forest.SPRITE_HEIGHT)
FRINGES.update(forest.FRINGES)

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

SKYLINES = ('mountains', 'hills', 'treeline', 'city', 'islands', 'jungle')


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


def _silhouette(sky, elev_deg, proj, colour, rng, texture=0.08, gaps=False):
    """Paint a ground silhouette whose top edge is `elev_deg` (per column) above the horizon.
    With `gaps`, columns at zero stay open sky right down to the horizon (islands at sea)."""
    h, w = sky.shape[:2]
    top = h - 1 - proj * np.tan(np.radians(np.clip(elev_deg, 0, 60)))
    mask = np.arange(h)[:, None] >= top[None, :]
    if gaps:
        mask &= (np.asarray(elev_deg) > 0)[None, :]
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
        elif kind == 'islands':
            # a few low islands far out at sea, the bigger ones crowned with a palm or two
            px_deg = w / 360.0
            elev = np.zeros(w)
            for _ in range(int(s.get('count', 7))):
                cx = rng.random() * w
                half = (1.5 + 4.5 * rng.random()) * px_deg
                top = (0.5 + 1.6 * rng.random()) * k
                d = _wrapdist(w, cx)
                elev = np.maximum(elev, top * np.clip(1 - (d / half) ** 2, 0, 1) ** 0.6)
                for _ in range(int(rng.integers(1, 4)) if top > 0.8 * k else 0):
                    px = cx + (rng.random() - 0.5) * half
                    ph = top + (0.5 + 0.6 * rng.random()) * k
                    dd = _wrapdist(w, px)
                    elev = np.maximum(elev, np.where(dd < 0.1 * px_deg, ph, 0))                     # trunk
                    elev = np.maximum(elev, np.where(dd < 0.55 * px_deg, ph - dd / px_deg * 0.6 * k, 0))   # crown
            _silhouette(sky, elev, proj, custom if custom is not None else tone(0.45), rng, 0.04, gaps=True)
        elif kind == 'jungle':
            # rolling rainforest: round crowns packed shoulder to shoulder, the odd emergent giant
            px_deg = w / 360.0
            for depth, layer in ((0.5, 0.0), (0.8, 0.6)):
                base = 1.2 + 1.4 * layer + 1.4 * _harmonics(w, rng, [(5, 1), (9, .6), (17, .3)])
                elev = base.copy()
                for _ in range(int(360 * 0.8)):
                    cx = rng.random() * w
                    half = (0.5 + 1.3 * rng.random()) * px_deg * (1.8 if rng.random() < 0.05 else 1)
                    top = base[int(cx) % w] + (0.5 + 1.2 * rng.random() ** 2) * (2.2 if half > 2 * px_deg else 1)
                    hc = half / px_deg * 0.5
                    d = _wrapdist(w, cx)
                    crown = top - hc * (1 - np.sqrt(np.clip(1 - (d / half) ** 2, 0, 1)))
                    elev = np.maximum(elev, np.where(d < half, crown, 0))
                ink = (0.03, 0.06, 0.04)
                _silhouette(sky, elev * k, proj, custom * (1 - 0.3 * layer) if custom is not None else tone(depth, ink),
                            rng, 0.05)
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


def draw_disc(sky, az_deg, el_deg, proj, colour, radius_deg=2.2, glow=0.35, hrow=None):
    """A sun or moon at an azimuth/elevation, with a soft additive halo. Wraps around 360.
    `hrow` is the panorama row of the horizon (the last row, unless the sky continues below)."""
    h, w = sky.shape[:2]
    hrow = h - 1 if hrow is None else hrow
    cx = (az_deg % 360) / 360.0 * w
    cy = hrow - proj * np.tan(np.radians(el_deg))
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


# ---------------------------------------------------------------- sky objects
# Planets, moons and stranger things painted into the sky panorama. Like the skyline they are
# placed in degrees (azimuth on the camera compass, elevation above the horizon, size as an
# angular radius), so they keep their size and place at any resolution or field of view.

SKY_OBJECTS = ('planet', 'ringed', 'moon', 'sun', 'eye')


def _sky_object_frame(sky, o, proj, hrow, default_size):
    """Pixel offsets of the whole panorama from an object's centre, in units of its radius."""
    h, w = sky.shape[:2]
    cx = (float(o.get('azimuth', 0)) % 360) / 360.0 * w
    cy = hrow - proj * np.tan(np.radians(float(o.get('elevation', 20))))
    r = max(2.0, proj * np.tan(np.radians(float(o.get('size', default_size)))))
    xs = np.arange(w)
    dx = ((xs - cx + w / 2) % w) - w / 2          # signed, wrapping round 360
    dy = np.arange(h) - cy
    return dx[None, :] / r, dy[:, None] / r, r


def _lambert(nx, ny, o):
    """Light on a sphere's face: `lit_from` is the screen direction the light comes from, in
    degrees (0 right, 90 below, 180 left, 270 above), `phase` how far round the side it is."""
    a = np.radians(float(o.get('lit_from', 210)))
    side = float(o.get('phase', 0.75))               # 0 = lit face-on, 1 = lit from the side
    lx, ly, lz = np.cos(a) * side, np.sin(a) * side, 1.0 - side * 0.85
    n = np.sqrt(lx * lx + ly * ly + lz * lz)
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    return np.clip((nx * lx + ny * ly + nz * lz) / n, 0, 1), nz


def draw_sky_object(sky, o, proj, hrow, seed=0):
    """Paint one entry of a scene's `sky_objects` into the panorama."""
    kind = o.get('type', 'planet')
    if kind not in SKY_OBJECTS:
        raise KeyError(f"unknown sky object '{kind}'. Sky objects: {', '.join(SKY_OBJECTS)}")
    rng = np.random.default_rng(int(o.get('seed', seed)) * 97 + 13)
    defaults = {'planet': ('#c87a4a', '#e8b07a', 9), 'ringed': ('#d8b880', '#a8784a', 7),
                'moon': ('#c8c4b8', '#8a867c', 3.5), 'sun': ('#fff0c0', '#ffb060', 3),
                'eye': ('#5a9a6a', '#f2ece0', 8)}[kind]
    c1 = np.array(o['color'] if 'color' in o else col(defaults[0]), np.float32)
    c2 = np.array(o['color2'] if 'color2' in o else col(defaults[1]), np.float32)
    nx, ny, r = _sky_object_frame(sky, o, proj, hrow, defaults[2])
    d2 = nx * nx + ny * ny
    inside = d2 <= 1
    glow = float(o.get('glow', {'sun': 0.9, 'eye': 0.15}.get(kind, 0.25)))
    if glow > 0:   # a haze of the object's own colour round it (atmosphere, corona)
        halo = np.clip(1 - np.sqrt(d2) / (3.2 if kind == 'sun' else 1.6), 0, 1) ** 2 * glow
        sky += halo[..., None] * (c2 if kind == 'sun' else c1)[None, None, :]

    if kind == 'sun':
        core = np.clip(1 - d2, 0, 1) ** 0.25
        sky[inside] = (c1[None, :] * (0.85 + 0.15 * core[inside][:, None]))
        return sky

    if kind == 'eye':
        # an almond of white with an iris that follows the viewer: the stuff of bad dreams
        lid = np.abs(ny) <= 0.62 * np.clip(1 - nx * nx, 0, 1) ** 0.75
        white = lid & (np.abs(nx) <= 1)
        veins = (np.abs(np.sin(nx * 23 + ny * 7) * np.cos(ny * 19)) > 0.985) & white
        sky[white] = c2 * (0.88 + 0.12 * np.clip(1 - d2, 0, 1))[white][:, None]
        sky[veins] = np.array([0.75, 0.25, 0.25], np.float32)
        ir = np.sqrt(nx * nx + ny * ny)
        iris = white & (ir <= 0.42)
        rings = 0.75 + 0.25 * np.sin(np.arctan2(ny, nx) * 24)
        sky[iris] = c1 * (0.6 + 0.5 * (1 - ir[iris] / 0.42))[:, None] * rings[iris][:, None]
        sky[white & (ir <= 0.17)] = np.array([0.03, 0.02, 0.03], np.float32)
        sky[white & (np.hypot(nx + 0.08, ny + 0.08) <= 0.05)] = np.array([1, 1, 1], np.float32)
        rim = (~lid) & (np.abs(ny) <= 0.62 * np.clip(1 - nx * nx, 0, 1) ** 0.75 + 0.07) & (np.abs(nx) <= 1.02)
        sky[rim] = np.array([0.1, 0.06, 0.07], np.float32)
        return sky

    shade, nz = _lambert(nx, ny, o)
    if kind == 'moon':
        tone = np.ones_like(d2)
        for _ in range(int(o.get('craters', 14))):
            ccx, ccy, cr = rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), rng.uniform(0.06, 0.24)
            m = (nx - ccx) ** 2 + (ny - ccy) ** 2 <= cr * cr
            tone[m] *= 0.78
        surface = c1[None, None, :] * tone[..., None]
        mare = np.clip(np.sin(nx * 4.1 + 1.3) * np.cos(ny * 3.3) - 0.35, 0, 1)
        surface = surface * (1 - mare[..., None] * 0.3) + c2[None, None, :] * mare[..., None] * 0.3
    else:
        # banded gas giant: latitude bands warped by a little turbulence
        warp = np.sin(nx * 5 + ny * 2.0 + rng.random() * 6) * 0.08
        band = 0.5 + 0.5 * np.sin((ny + warp) * float(o.get('bands', 9)) + rng.random() * 6)
        surface = c1[None, None, :] * (1 - band[..., None] * 0.55) + c2[None, None, :] * band[..., None] * 0.55
        if kind == 'planet' and o.get('storm', True):
            st = ((nx - 0.25) / 0.22) ** 2 + ((ny - 0.3) / 0.11) ** 2 <= 1
            surface[st] = surface[st] * 0.55 + np.array([0.75, 0.3, 0.2], np.float32) * 0.45
    lit = surface * (0.06 + 0.94 * shade[..., None])
    rim = np.clip(1 - nz, 0, 1) ** 3 * 0.35            # atmosphere brightening the limb
    lit = lit + (c1 * 0.6)[None, None, :] * (rim * np.clip(shade * 1.5, 0, 1))[..., None]

    if kind == 'ringed':
        tilt = float(o.get('tilt', 0.24))
        rot = np.radians(float(o.get('angle', -14)))
        rx = nx * np.cos(rot) + ny * np.sin(rot)
        ry = -nx * np.sin(rot) + ny * np.cos(rot)
        rho = np.sqrt(rx * rx + (ry / tilt) ** 2)
        ring = (rho >= 1.35) & (rho <= 2.35)
        dens = (0.55 + 0.45 * np.sin(rho * 31)) * np.where((rho > 1.8) & (rho < 1.88), 0.1, 1.0)
        ring_c = c2[None, None, :] * (0.7 + 0.3 * dens[..., None])
        a = (dens * 0.85)[..., None]
        back = ring & (ry < 0)
        sky[back] = (sky * (1 - a) + ring_c * a)[back]
        sky[inside] = lit[inside]
        front = ring & (ry >= 0)
        sky[front] = (sky * (1 - a) + ring_c * a)[front]
        return sky
    sky[inside] = lit[inside]
    return sky


# ---------------------------------------------------------------- sky presets

# top, middle and horizon colours of each preset's gradient
SKY_PRESETS = {
    'night': ('#05070e', '#1b2232', '#26304a'),
    'dusk': ('#1f2333', '#4a3550', '#a0605a'),
    'storm': ('#141820', '#262c38', '#3a4250'),
    'day': ('#4a7ab0', '#8ab4d8', '#c8dce8'),
    'overcast': ('#5a6068', '#7a8088', '#9aa0a4'),
    'blood': ('#120608', '#3a0e10', '#7a2018'),
    'space': ('#010104', '#020208', '#05050e'),
    'alien': ('#06262a', '#1c6458', '#d0b868'),
    'dream': ('#6a86d6', '#d6a2cc', '#ffdcae'),
    'sunset': ('#2a2c5a', '#c8607a', '#ffb860'),
    'golden': ('#3a6aa8', '#a0bcd2', '#f2d8a0'),
}
_CLOUD_COVER = {'night': 0.62, 'dusk': 0.55, 'storm': 0.42, 'day': 0.6, 'overcast': 0.3, 'blood': 0.55,
                'alien': 0.5, 'dream': 0.5, 'sunset': 0.56, 'golden': 0.64}
_CLOUD_COLOUR = {'night': '#2a3245', 'dusk': '#5a3a4a', 'storm': '#1c2028', 'day': '#e8eef4',
                 'overcast': '#6a7078', 'blood': '#2a0a0c', 'alien': '#7a3a6a', 'dream': '#fff2f6',
                 'sunset': '#e8806a', 'golden': '#fff0d8'}
# the sea of cloud seen from above, under a void floor: sunlit tops, shadowed hollows
_CLOUD_SEA = {'night': ('#4a5672', '#121828'), 'dusk': ('#d89880', '#3a2c48'),
              'storm': ('#3e4652', '#141820'), 'day': ('#f2f5fa', '#9aaccc'),
              'overcast': ('#a0a6ae', '#5a6068'), 'blood': ('#7a2a1e', '#1e0608'),
              'alien': ('#9ae0c0', '#2a3a5a'), 'dream': ('#fff6fa', '#c0a0d8'),
              'sunset': ('#ffc890', '#5a3a6a'), 'golden': ('#fff0d8', '#a89aa8')}


def _wrapnoise(w, h, cx, cy, rng):
    """Smooth value noise over the panorama that wraps seamlessly round 360 degrees:
    a cy x cx grid of random values, interpolated with periodic indices across the width."""
    g = rng.random((cy, cx))
    u = np.arange(w) * cx / w
    i0 = np.floor(u).astype(int) % cx
    i1 = (i0 + 1) % cx
    fu = u - np.floor(u)
    fu = fu * fu * (3 - 2 * fu)
    v = np.linspace(0, cy - 1, h)
    j0 = np.floor(v).astype(int).clip(0, cy - 1)
    j1 = np.minimum(j0 + 1, cy - 1)
    fv = v - np.floor(v)
    fv = (fv * fv * (3 - 2 * fv))[:, None]
    top = g[j0][:, i0] * (1 - fu) + g[j0][:, i1] * fu
    bot = g[j1][:, i0] * (1 - fu) + g[j1][:, i1] * fu
    return (top * (1 - fv) + bot * fv).astype(np.float32)


def _stars(sky, rng, density, bright=1.0, rows=None):
    """Scatter stars of varied brightness and colour, a few of them big."""
    h, w = sky.shape[:2]
    rows = slice(None) if rows is None else rows
    sub = sky[rows]
    m = rng.random(sub.shape[:2]) < density
    k = int(m.sum())
    level = (0.35 + 0.65 * rng.random(k) ** 2.2) * bright
    tint = np.array([[1, 1, 1], [0.75, 0.85, 1.0], [1.0, 0.9, 0.75], [1.0, 0.8, 0.8]], np.float32)
    sub[m] = np.maximum(sub[m], tint[rng.integers(0, 4, k)] * level[:, None])
    big = np.argwhere(m)[level > 0.85 * bright]
    for (y, x) in big[:max(1, k // 40)]:
        for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            yy, xx = y + dy, (x + dx) % w
            if 0 <= yy < sub.shape[0]:
                sub[yy, xx] = np.maximum(sub[yy, xx], sub[y, x] * 0.55)
    sky[rows] = sub


def _space(w, h, below, proj, rng):
    """Deep space all the way round: a starfield, coloured nebula and the band of a galaxy,
    continuing under the horizon so a viewport or a void floor shows stars below as well."""
    rows = h + below
    hrow = h - 1
    sky = np.zeros((rows, w, 3), np.float32) + col('#020208')[None, None, :]
    yy = np.arange(rows)[:, None]
    az = np.arange(w)[None, :] / w * 2 * np.pi
    band_el = 18 * np.sin(az + rng.random() * 6.28) + 6 * np.sin(2 * az + rng.random() * 6.28)
    band_row = hrow - proj * np.tan(np.radians(band_el))
    near = np.exp(-((yy - band_row) / (proj * 0.12)) ** 2)
    n1 = _wrapnoise(w, rows, 18, 6, rng)
    n2 = _wrapnoise(w, rows, 40, 12, rng)
    dust = np.clip(near * (0.6 * n1 + 0.4 * n2) * 1.4 - 0.25, 0, 1)
    sky += dust[..., None] * col('#4a3a6a')[None, None, :] * 0.55
    sky += (near * n2 * 0.25)[..., None] * col('#8a7a9a')[None, None, :] * 0.4
    neb = np.clip((_wrapnoise(w, rows, 7, 3, rng) - 0.62) * 3.0, 0, 1) * np.clip(n2 * 1.4, 0, 1)
    sky += neb[..., None] * col('#2a6a8a')[None, None, :] * 0.5
    neb2 = np.clip((_wrapnoise(w, rows, 5, 2, rng) - 0.66) * 3.0, 0, 1) * n1
    sky += neb2[..., None] * col('#8a2a5a')[None, None, :] * 0.45
    _stars(sky, rng, 0.006)
    m = rng.random((rows, w)) < 0.02 * near
    sky[m] = np.maximum(sky[m], 0.55)
    return np.clip(sky, 0, 1)


def _cloud_sea(w, below, proj, preset, horizon_colour, rng):
    """What lies under a void floor: a deck of cloud far below, seen from above, melting into
    the horizon haze. Each row looks down at a steeper angle and so at nearer cloud."""
    lit, shadow = (col(c) for c in _CLOUD_SEA[preset])
    k = np.arange(1, below + 1, dtype=np.float64)[:, None]
    az = (np.arange(w) / w * 2 * np.pi)[None, :]
    down = k / proj                                   # tan of the angle below the horizon
    dist = 1.0 / down
    N = 128
    tex, fine = fbm(N, rng, 4, 5), fbm(N, rng, 8, 4)
    X, Y = dist * np.cos(az) * 12.0, dist * np.sin(az) * 12.0
    n = (0.7 * tex[Y.astype(np.int64) % N, X.astype(np.int64) % N]
         + 0.3 * fine[(Y * 2.3).astype(np.int64) % N, (X * 2.3).astype(np.int64) % N])
    billow = np.clip((n - 0.42) * 3.2, 0, 1) ** 0.7
    sea = shadow[None, None, :] * (1 - billow[..., None]) + lit[None, None, :] * billow[..., None]
    haze = np.exp(-down / 0.07)[..., None]
    return (sea * (1 - haze) + horizon_colour[None, None, :] * haze).astype(np.float32)


def make_sky(preset, w, h, seed=3, skyline=None, proj=None, discs=(), objects=(), below=0):
    """Panorama covering 360 degrees: h rows above the horizon line, plus `below` rows under it
    for scenes with void floors (stars in space, otherwise a sea of cloud far beneath).

    `skyline` adds distant silhouettes (see draw_skyline). `discs` are suns and moons placed by
    directional lights and `objects` the scene's `sky_objects`; when either is given, the
    preset's own decorative moon is left out.
    """
    if preset not in SKY_PRESETS:
        raise KeyError(f"unknown sky '{preset}'. Skies: {', '.join(SKY_PRESETS)}, or null for none")
    rng = np.random.default_rng(seed)
    proj = proj or w / (2 * np.pi)
    if preset == 'space':
        sky = _space(w, h, below, proj, rng)
    else:
        top, mid, hor = [col(c) for c in SKY_PRESETS[preset]]
        t = np.linspace(0, 1, h)[:, None]
        g = np.where(t < 0.6, top * (1 - t / 0.6) + mid * (t / 0.6), mid * (1 - (t - 0.6) / 0.4) + hor * ((t - 0.6) / 0.4))
        sky = np.repeat(g[:, None, :], w, axis=1).reshape(h, w, 3)
        # clouds: horizontal-stretched noise bands
        cn = np.zeros((h, w))
        for cells, amp in ((6, 1.0), (12, 0.5), (24, 0.25)):
            cn += _wrapnoise(w, h, cells, max(2, cells // 3), rng) * amp   # seamless at 0/360
        cn /= 1.75
        mask = np.clip((cn - _CLOUD_COVER[preset]) * 4, 0, 1) * (t < 0.85)
        sky = sky * (1 - mask[..., None] * 0.85) + col(_CLOUD_COLOUR[preset]) * mask[..., None] * 0.85
        if preset in ('night', 'storm', 'blood', 'dusk', 'alien'):
            stars = (rng.random((h, w)) > 0.997) & (t[:, 0][:, None] < 0.6) & (mask < 0.2)
            sky[stars] = col('#c8c8d0') * (0.5 if preset != 'night' else 1)
        if preset in ('night', 'blood') and not discs and not objects:
            mx, my, r = int(w * 0.62), int(h * 0.28), max(4, h // 14)
            yy, xx = np.mgrid[0:h, 0:w]
            m = (yy - my) ** 2 + (xx - mx) ** 2 < r * r
            sky[m] = col('#e6e0c8') if preset == 'night' else col('#d04a30')
        if below:
            sky = np.concatenate([sky, _cloud_sea(w, below, proj, preset, hor, rng)], axis=0)
    sky = sky.astype(np.float32)
    for i, o in enumerate(objects):
        draw_sky_object(sky, o, proj, h - 1, seed + i)
    for d in discs:
        draw_disc(sky, d['azimuth'], d['elevation'], proj, d['color'], d.get('radius', 2.2),
                  d.get('glow', 0.35), h - 1)
    if skyline:
        draw_skyline(sky[:h], skyline, proj, seed)
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

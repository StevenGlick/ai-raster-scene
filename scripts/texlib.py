"""The small drawing helpers the original textures, props, decals and skies are made with: a seeded
generator per name, tileable value noise and fBm, hex colours, noise shading and grain. T is the
texture size (64)."""
import numpy as np

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

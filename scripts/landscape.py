"""Landscape scale: the world as a giant sees it. A map cell is about 100 m, so the camera's eye at 0.5 stands
some fifty metres up, a kaiju is the size a person is in a room, a ten-storey building comes to its knee and a
car is a speck. The engine is the same; what changes is what the textures and props are drawn as. Buildings are
`tower` objects (scripts/objects.py); the ground is drawn here.

`city_street` is a city block's ground with half a street along each edge, so a field of them is a street grid:
asphalt with a dashed centre line, kerbs and pavements, street trees, the block's own paving inside, where its
towers stand. `harbor_water` is open water seen from high up: dark, small waves catching the light.
"""
import numpy as np

from pixelart import Canvas, dither, outline_sprite, ramp, smooth_noise
from texlib import T, _rng, col

ROAD, KERB, PAVE = 6, 8, 64 - 8          # texels from a cell's edge: the half street, the pavement, the block


def _edge_dist():
    """For every texel of a cell, how far it is in from the nearest edge, and which way that edge runs."""
    yy, xx = np.mgrid[0:T, 0:T]
    dy, dx = np.minimum(yy, T - 1 - yy), np.minimum(xx, T - 1 - xx)
    return np.minimum(dy, dx), dy <= dx, yy, xx


def _street(name, lit):
    """A city block's ground at landscape scale: half a street along each edge (meeting the next block's half,
    the centre line dashed along the cell's top and left edges), crossings at the corners, a pale pavement with
    street trees, and the block's own paving inside. `lit`: its street lamps burn along the pavements, sodium
    orange, and cars' lights move down the roads, white coming and red going."""
    rng = _rng(name)
    d, across, yy, xx = _edge_dist()
    img = np.empty((T, T, 3), np.float32)
    road = d < ROAD
    img[:] = col('#a29e94')
    img[:] *= (0.92 + 0.12 * smooth_noise(T, T, 8, rng))[..., None]
    img[road] = col('#3c3d40') * (0.9 + 0.2 * rng.random((T, T, 1)))[road]
    img[(d >= ROAD) & (d < KERB)] = col('#b6b2a8')
    img[d == ROAD] = col('#cfcbc0')                              # the kerb
    ex, ey = np.minimum(xx, T - 1 - xx), np.minimum(yy, T - 1 - yy)
    corner = (ey < KERB) & (ex < KERB)
    dash = ((yy == 0) & (xx % 6 < 3)) | ((xx == 0) & (yy % 6 < 3))
    img[dash & ~corner] = col('#d8c880')                          # the centre line
    zebra = ~corner & road & (((ex >= KERB) & (ex < KERB + 3) & (xx % 2 == 0) & ~across)
                              | ((ey >= KERB) & (ey < KERB + 3) & (yy % 2 == 0) & across))
    img[zebra] = col('#c8c6c0')                                   # crossings at the corners
    trees = (d == KERB - 1) & (((xx + yy) % 7) == 0) & ~corner
    img[trees] = col('#2e4a28')
    if not lit:
        return np.clip(img, 0, 1), None
    em = np.zeros((T, T), np.float32)
    lamps = (d == KERB - 1) & ~trees & ~corner & (np.where(across, xx, yy) % 4 == 2)
    img[lamps] = col('#ffb848')
    cars = road & (d >= 1) & (d <= ROAD - 2) & ~corner & (rng.random((T, T)) < 0.035)
    img[cars] = np.where(rng.random((T, T, 1)) < 0.5, col('#fff2d0'), col('#ff3a24'))[cars]
    em[lamps | cars] = 1.0
    return np.clip(img, 0, 1), em


def tex_quay(name):
    """A quay's concrete apron from high up: big pale slabs with dark joints, tyre marks and stains, a yellow
    line painted along it and the dots of the mooring bollards."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    img = np.empty((T, T, 3), np.float32)
    img[:] = col('#aaa69c') * (0.9 + 0.14 * smooth_noise(T, T, 6, rng))[..., None]
    img[(yy % 16 == 0) | (xx % 16 == 0)] *= 0.78                  # the joints between slabs
    stain = smooth_noise(T, T, 10, rng) > 0.72
    img[stain] *= 0.82
    img[(yy == 40) & (xx % 8 < 5)] = col('#d8b840')
    img[(yy == 4) & (xx % 12 == 6)] = col('#2a2a2c')               # bollards
    return np.clip(img, 0, 1)


def tex_container_yard(name):
    """A container port's yard from high up: asphalt, and blocks of shipping containers in rows - each its own
    colour, rust red, blue, green, grey, white, orange - their tops catching the light, a line of shadow under each
    row, lanes between the blocks for the straddle carriers."""
    rng = _rng(name)
    img = np.empty((T, T, 3), np.float32)
    img[:] = col('#4c4c4e') * (0.9 + 0.15 * rng.random((T, T, 1)))
    cols = [col(c) for c in ('#8a3a28', '#2e5a8a', '#3a6a3a', '#8a8a86', '#c8c4b8', '#c8642a', '#6a2a2a', '#2a4a6a')]
    for y0 in (3, 35):                                             # two blocks, six rows each
        for r in range(6):
            y = y0 + r * 4
            for x in range(1, 63, 9):
                c = cols[int(rng.integers(0, len(cols)))] * rng.uniform(0.85, 1.1)
                img[y, x:x + 8] = c * 1.18                         # its top, in the light
                img[y + 1, x:x + 8] = c
                img[y + 2, x:x + 8] *= 0.6                         # the shadow under the row
    return np.clip(img, 0, 1)


def tex_city_park(name):
    """A city park from high up: lawns of two greens, paths of pale gravel crossing it, and clumps of tree
    crowns - each a dark round with a lit side."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    img = np.empty((T, T, 3), np.float32)
    img[:] = col('#4a6a34') * (0.9 + 0.2 * smooth_noise(T, T, 8, rng))[..., None]
    img[(np.abs(yy - xx) < 1.5) | (np.abs(yy + xx - T) < 1.5) | (yy == 32)] = col('#b8ae94')   # the paths
    for _ in range(26):                                           # tree crowns
        cy, cx, r = rng.uniform(0, T), rng.uniform(0, T), rng.uniform(1.6, 3.2)
        dy = np.minimum(np.abs(yy - cy), T - np.abs(yy - cy))
        dx = np.minimum(np.abs(xx - cx), T - np.abs(xx - cx))
        crown = dy ** 2 + dx ** 2 < r * r
        img[crown] = col('#2c4a22')
        img[crown & (((yy - cy) % T) > T / 2) & (((xx - cx) % T) > T / 2)] = col('#4e7234')   # its lit side
    return np.clip(img, 0, 1)


CROPS = {'wheat': ('#b8a262', 0.1), 'plough': ('#6e5238', 0.14), 'pasture': ('#5e7c3a', 0.0),
         'rapeseed': ('#bcae46', 0.06), 'young': ('#7a9646', 0.12), 'stubble': ('#a8946a', 0.08),
         'meadow': ('#6a8a42', 0.0)}


def tex_farmland(name):
    """Farmland from high up: a patchwork of fields - wheat, ploughed earth, pasture, rapeseed, young green crops,
    stubble - each with its rows running its own way, between hedgerows with a tree here and there in them. The
    fields lie across the cell's edges (the texture wraps), so a run of cells is not a grid of squares; the six
    layouts (`farmland`, `farmland_b` ... `farmland_f`) mixed at random read as one countryside."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    img = np.empty((T, T, 3), np.float32)
    ox, oy = int(rng.integers(0, T)), int(rng.integers(0, T))     # the layout slid, so its lines fall anywhere
    sx, sy = (xx + ox) % T, (yy + oy) % T
    xs = [0, int(rng.integers(14, 28)), int(rng.integers(34, 50)), T]
    hedge = np.zeros((T, T), bool)
    names = list(CROPS)
    for i in range(3):
        x0, x1 = xs[i], xs[i + 1]
        ys = sorted({0, T, *(int(v) for v in rng.integers(12, 52, int(rng.integers(0, 3))))})
        for j in range(len(ys) - 1):
            y0, y1 = ys[j], ys[j + 1]
            c, rows = CROPS[names[int(rng.integers(0, len(names)))]]
            field = (sy >= y0) & (sy < y1) & (sx >= x0) & (sx < x1)
            along = sx if rng.random() < 0.5 else sy
            v = (1.0 + rows * np.where(along % 3 == 0, -1.0, 0.4) + 0.08 * (rng.random((T, T)) - 0.5)
                 + rng.uniform(-0.06, 0.06))
            img[field] = (col(c) * v[..., None])[field]
            hedge |= field & ((sy == y0) | (sx == x0))
    img[hedge] = col('#3a4e26')
    trees = hedge & (rng.random((T, T)) < 0.12)
    for y, x in zip(*np.nonzero(trees)):                          # a tree in the hedge: a dark crown, its lit side
        img[y:y + 2, x:x + 2] = col('#2a3c1c')
        img[y, x] = col('#4a6a2c')
    return np.clip(img, 0, 1)


def tex_road(name, ew=True, ns=False):
    """A country road at landscape scale across a cell of farmland: two lanes of asphalt, a dashed white line down
    the middle and pale lines at its edges, grass verges and a hedgerow either side with trees in it, the fields
    beyond. `road_ew` runs across the cell (east-west), `road_ns` down it, `road_x` is a crossroads; their ends
    meet the next cell's, so a row of them is one road."""
    rng = _rng(name)
    img = tex_farmland(name)
    yy, xx = np.mgrid[0:T, 0:T]
    c = T // 2
    roads = [d for d, on in ((yy, ew), (xx, ns)) if on]       # the distance across each road is from its middle
    hedge = np.zeros((T, T), bool)
    for across in roads:
        off = np.abs(across - c)
        hedge |= off == 6
        img[(off >= 4) & (off <= 5)] = col('#6a8a42') * (0.92 + 0.12 * rng.random((T, T, 1)))[(off >= 4) & (off <= 5)]
    for across in roads:                                       # every road's verges cleared before its tarmac
        along = xx if across is yy else yy
        off = np.abs(across - c)
        img[off <= 3] = col('#4a4a4c') * (0.9 + 0.16 * rng.random((T, T, 1)))[off <= 3]
        img[off == 3] = col('#a8a8a0')                         # the edge lines
        img[(across == c) & (along % 6 < 3)] = col('#e8e6dc')  # the dashes down the middle
    for across in roads:                                       # no hedge across another road
        hedge &= np.abs(across - c) > 3
    img[hedge] = col('#3a4e26')
    for y, x in zip(*np.nonzero(hedge & (rng.random((T, T)) < 0.16))):
        img[y:y + 2, x:x + 2] = col('#2a3c1c')                 # a tree in the hedge
        img[y, x] = col('#4a6a2c')
    return np.clip(img, 0, 1)


def _voronoi(n, rng, size=T):
    """The two nearest of n points scattered over a wrapping cell, for every texel: (F1, F2, nearest's index)."""
    pts = rng.random((n, 2)) * size
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    best = np.full((2, size, size), 1e9, np.float32)
    idx = np.zeros((size, size), int)
    for k, (py, px) in enumerate(pts):
        dy = np.abs(yy - py)
        dx = np.abs(xx - px)
        d = np.hypot(np.minimum(dy, size - dy), np.minimum(dx, size - dx))
        closer = d < best[0]
        best[1] = np.where(closer, best[0], np.minimum(best[1], d))
        idx = np.where(closer, k, idx)
        best[0] = np.where(closer, d, best[0])
    return best[0], best[1], idx


LAVA_GLOW = ramp(['#5a1206', '#9a2a08', '#d8540e', '#ff8a1e', '#ffc048', '#fff0a8'])
BASALT = ramp(['#141214', '#1e1b1c', '#2a2626', '#383232', '#4a4340', '#625a54'])


def tex_lava_field(name):
    """Old lava from high up: black crust broken into plates, ropy and rough, and in patches - where it is still
    moving underneath - the cracks between the plates glowing orange (they glow)."""
    rng = _rng(name)
    f1, f2, idx = _voronoi(26, rng)
    rope = smooth_noise(T, T, 16, rng) * 0.5 + smooth_noise(T, T, 5, rng) * 0.5
    v = 0.28 + 0.3 * rope + 0.12 * (rng.random(26)[idx] - 0.5) - 0.18 * np.exp(-f1 / 6.0)
    img = dither(np.clip(v, 0, 1), BASALT, 0.5)
    crack = (f2 - f1) < 1.1
    live = smooth_noise(T, T, 3, rng) > 0.55                                 # where it still moves underneath
    hot = crack & live
    heat = np.clip(0.55 + 0.45 * (smooth_noise(T, T, 9, rng) - 0.3), 0, 1)
    img[hot] = dither(heat, LAVA_GLOW, 0.4)[hot]
    img[crack & ~live] = BASALT[0]
    em = np.where(hot, 1.0, 0.0).astype(np.float32)
    return np.clip(img, 0, 1), em


def tex_lava_flow(name):
    """A river of lava from high up: plates of dark crust riding on it, the glowing melt between them wide and
    bright, yellow-white where it runs hottest (it all glows)."""
    rng = _rng(name)
    f1, f2, idx = _voronoi(30, rng)
    gap = f2 - f1
    heat = np.clip(1.0 - gap / 3.2, 0, 1) * 0.8 + 0.25 * smooth_noise(T, T, 6, rng)
    img = dither(np.clip(heat, 0, 1), LAVA_GLOW, 0.5)
    crust = gap > 2.2 + 1.5 * rng.random(30)[idx]                             # plates of crust riding on it
    cv = 0.2 + 0.25 * smooth_noise(T, T, 12, rng)
    img[crust] = dither(np.clip(cv, 0, 1), ramp(['#1a0c0a', '#2a120c', '#3e1a10', '#5a2614', '#7a3418', '#9a4a20']),
                        0.5)[crust]
    em = np.where(crust, 0.55, 1.0).astype(np.float32)
    return np.clip(img, 0, 1), em


def tex_black_sand(name):
    """A beach of black volcanic sand from high up: dark grey-black, wind ripples faint across it, darker where
    the sea has wet it, a scatter of pale pebbles and drift."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    v = (0.36 + 0.14 * smooth_noise(T, T, 6, rng) + 0.05 * np.sin((xx * 0.7 + yy * 0.25) * 0.9)
         - 0.12 * (smooth_noise(T, T, 3, rng) > 0.6))
    img = dither(np.clip(v, 0, 1), ramp(['#141416', '#1e1e20', '#2a2a2c', '#38383a', '#4a4a4a', '#626058']), 0.5)
    for y, x in zip(*np.nonzero(rng.random((T, T)) < 0.012)):
        img[y, x] = col('#8a8478')
    return np.clip(img, 0, 1)


def tex_desert_floor(name):
    """Desert from high up: red-brown sand and gravel in broad patches, darker where desert pavement lies, pale
    braided washes where the rain runs off, and the dots of scrub - sage and creosote - scattered over it; it
    wraps, so a plain of it runs on without a seam. Three layouts (`desert_floor`, `_b`, `_c`) to mix at random."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    v = 0.46 + 0.16 * smooth_noise(T, T, 4, rng) + 0.08 * smooth_noise(T, T, 12, rng) - 0.1 * (
        smooth_noise(T, T, 6, rng) > 0.62)
    wash = np.abs(smooth_noise(T, T, 3, rng) - 0.5) < 0.018                 # a braided wash, pale
    wash |= np.abs(smooth_noise(T, T, 5, rng) - 0.5) < 0.011
    v = np.where(wash, 0.82, v)
    img = dither(np.clip(v, 0, 1), ramp(['#5a2e1c', '#7a4026', '#9a5632', '#b46e42', '#c88a5a', '#dcb084']), 0.5)
    scrub = (rng.random((T, T)) < 0.035) & ~wash
    img[scrub] = col('#5a5e3a')
    img[np.roll(scrub, 1, 0) & ~scrub & ~wash] *= 0.82                      # each bush's shadow
    return np.clip(img, 0, 1)


def tex_desert_road(name, ew=True):
    """A desert highway at landscape scale: two lanes of sun-faded asphalt, a dashed yellow line, pale sandy
    shoulders, the desert either side; `desert_road` runs down the cell (north-south), `desert_road_ew` across."""
    rng = _rng(name)
    img = tex_desert_floor(name)
    yy, xx = np.mgrid[0:T, 0:T]
    across, along = (yy, xx) if ew else (xx, yy)
    off = np.abs(across - T // 2)
    img[(off >= 4) & (off <= 5)] = col('#d4b08a')
    img[off <= 3] = col('#4e4a48') * (0.9 + 0.16 * rng.random((T, T, 1)))[off <= 3]
    img[off == 3] = col('#b0aca4')
    img[(across == T // 2) & (along % 8 < 4)] = col('#e0b840')
    return np.clip(img, 0, 1)


def tex_snow_fields(name):
    """Farmland under snow from high up: the fields white, each a shade of its own and the ploughed ones showing
    their furrows faintly through, the hedgerows dark lines across it with their trees standing out of the snow."""
    base = tex_farmland(name)
    lum = base.mean(-1)
    rng = _rng(name + '/snow')
    hedge = lum < 0.25
    drift = smooth_noise(T, T, 5, rng)                                # the snow lies unevenly, in drifts
    img = col('#e4ecf4') * (0.88 + 0.08 * (lum[..., None] - 0.4) + 0.1 * drift[..., None]) * (
        0.97 + 0.05 * rng.random((T, T, 1)))
    img[hedge] = (img * 0.84 + col('#5a6466') * 0.16)[hedge]          # hedges buried, a faint line
    img[hedge & (lum < 0.16)] = col('#2e3836')                       # the trees in them, standing out
    return np.clip(img, 0, 1)


def tex_snow_forest(name):
    """Pines under snow from high up: dark crowns close together, each white on its lit side and its top, blue
    shadow between them."""
    base = tex_pine_canopy(name)
    lum = base.mean(-1)
    img = base * 0.75 + col('#22303a') * 0.1
    snow = lum > np.percentile(lum, 55)
    img[snow] = col('#dce6f0') * (0.85 + 0.5 * (lum[snow, None] - lum[snow].mean()))
    return np.clip(img, 0, 1)


def tex_frozen_lake(name):
    """A frozen lake from high up: grey-blue ice, white drifts of snow blown across it in streaks, cracks running long and straight. Three layouts
    (`frozen_lake`, `_b`, `_c`) to mix, so a lake of it does not repeat."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    v = 0.56 + 0.1 * smooth_noise(T, T, 5, rng)
    drift = smooth_noise(T, T, 8, rng, cells_y=2) > 0.6                 # streaks blown along it
    v = np.where(drift, 0.8, v)
    img = dither(np.clip(v, 0, 1), ramp(['#2a3a48', '#3e5262', '#5a7282', '#7a94a4', '#a8bccc', '#e0eaf2']), 0.5)
    for _ in range(3):                                                    # cracks, long and straight
        x0, y0, a = rng.uniform(0, T), rng.uniform(0, T), rng.uniform(0, np.pi)
        t = np.arange(-26, 26)
        cx, cy = (x0 + t * np.cos(a)).astype(int) % T, (y0 + t * np.sin(a)).astype(int) % T
        img[cy, cx] = col('#3e5060')
    return np.clip(img, 0, 1)


def tex_ocean(name):
    """Deep tropical sea from high up: a saturated blue, a long swell in it, short whitecaps here and there."""
    rng = _rng(name)
    swell = smooth_noise(T, T, 5, rng)
    v = 0.4 + 0.22 * swell + 0.08 * smooth_noise(T, T, 14, rng)
    cap = (rng.random((T, T)) < 0.006) & (swell > 0.55)              # a whitecap, small and rare
    v = np.where(cap, 0.9, v)
    return dither(np.clip(v, 0, 1), ramp(['#0a2a5a', '#103a74', '#18508e', '#2468a6', '#3a86be', '#cfe6f4']), 0.5)


def tex_lagoon(name):
    """A lagoon from high up: clear turquoise over pale sand, ripples of light on the bottom, a darker patch of
    weed or a coral head here and there; it reflects a little."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    v = 0.56 + 0.16 * smooth_noise(T, T, 4, rng) + 0.06 * np.sin((xx + yy * 0.6) * 0.6 + smooth_noise(T, T, 3, rng) * 6)
    img = dither(np.clip(v, 0, 1), ramp(['#0e6a7a', '#168a96', '#22a8aa', '#3cc4bc', '#6ad8cc', '#b4ece0']), 0.5)
    heads = smooth_noise(T, T, 9, rng) > 0.72
    img[heads] = col('#3a6a5e')
    return np.clip(img, 0, 1)


def tex_reef_flat(name):
    """A reef from high up, under a little water: heads and spurs of coral - brown, olive, a purple one - packed
    together with channels of pale sand and turquoise between them."""
    rng = _rng(name)
    f1, f2, idx = _voronoi(22, rng)
    img = tex_lagoon(name + '/water')
    coral = (f2 - f1) > 1.6 + 2.2 * smooth_noise(T, T, 6, rng)
    tones = [col(c) for c in ('#6a5a3a', '#5a6a3a', '#7a5a4a', '#5a4a6a', '#8a7a4a')]
    pick = rng.integers(0, len(tones), 22)[idx]
    shade = (0.75 + 0.3 * smooth_noise(T, T, 16, rng))[..., None]
    for k, c in enumerate(tones):
        sel = coral & (pick == k)
        img[sel] = (c * shade)[sel]
    return np.clip(img, 0, 1)


def tex_white_sand(name):
    """A beach of white coral sand from high up: bright, faintly rippled, wetter and darker in patches, a line of
    wrack here and there."""
    rng = _rng(name)
    v = 0.72 + 0.12 * smooth_noise(T, T, 6, rng) - 0.1 * (smooth_noise(T, T, 3, rng) > 0.66)
    img = dither(np.clip(v, 0, 1), ramp(['#a89a7a', '#c4b896', '#d8ceb0', '#e8e0c8', '#f2ecdc', '#fcf8f0']), 0.5)
    img[rng.random((T, T)) < 0.01] = col('#8a7a5a')
    return np.clip(img, 0, 1)


def tex_palm_canopy(name):
    """Coconut palms from high up: each crown a star of fronds, bright green on its lit side, pale sand and
    shadow showing between them."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    img = tex_white_sand(name + '/sand') * 0.82
    for _ in range(42):
        cx, cy = rng.uniform(0, T), rng.uniform(0, T)
        r = rng.uniform(4, 7)
        dx = (xx - cx + T / 2) % T - T / 2
        dy = (yy - cy + T / 2) % T - T / 2
        d = np.hypot(dx, dy)
        a = np.arctan2(dy, dx)
        fronds = int(rng.integers(6, 9))
        star = d < r * (0.45 + 0.55 * np.abs(np.cos(a * fronds / 2 + rng.uniform(0, 3))) ** 0.6)
        img[star & (d < r)] = col('#2e5a1e')
        lit = star & (d < r) & ((dx * -0.6 + dy * -0.8) > 0)
        img[lit] = col('#5a8a2e')
        img[(d < 1.2)] = col('#6a5a2a')                                  # the crown's heart
    return np.clip(img, 0, 1)


def _canopy(name, rmin, rmax, n, greens, light):
    """Woodland from high up: crowns packed close, each a round of its own green, lit on its upper left and in
    shade on the lower right, the gaps between them dark - wrapping, so the wood runs on from cell to cell."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    img = np.empty((T, T, 3), np.float32)
    img[:] = col('#141c10')
    for _ in range(n):
        cy, cx, r = rng.uniform(0, T), rng.uniform(0, T), rng.uniform(rmin, rmax)
        dy = (yy - cy + T / 2) % T - T / 2
        dx = (xx - cx + T / 2) % T - T / 2
        d = np.hypot(dy, dx) / r
        crown = d < 1
        g = col(greens[int(rng.integers(0, len(greens)))]) * rng.uniform(0.85, 1.12)
        lit = np.clip(0.75 - (dx + dy) / (2.2 * r) * light, 0.45, 1.25)
        img[crown] = (g * lit[..., None])[crown]
    return np.clip(img, 0, 1)


def tex_forest_canopy(name):
    """Broadleaf woodland from high up: big rounded crowns of many greens, packed close."""
    return _canopy(name, 2.4, 4.4, 150, ['#3e5a26', '#4a6a2c', '#56762e', '#3a5222', '#5e7a34'], 0.9)


def tex_pine_canopy(name):
    """Pine forest from high up: small dark crowns, blue-green, close as bristles."""
    return _canopy(name, 1.5, 2.4, 330, ['#1e3424', '#24402c', '#2a4a30', '#1a2e20'], 1.1)


def tex_pasture(name):
    """Pasture and meadow from high up: green in broad patches of lighter and darker grass, the stripes of the
    last mowing faint across it, a lone tree or two."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    v = 0.9 + 0.14 * smooth_noise(T, T, 5, rng) + 0.04 * np.where((xx // 4) % 2 == 0, 1.0, -1.0)
    img = col('#5e7e3a')[None, None, :] * v[..., None]
    for _ in range(2):
        y, x = int(rng.integers(2, T - 3)), int(rng.integers(2, T - 3))
        img[y:y + 3, x:x + 3] = col('#2e4220')
        img[y, x:x + 2] = col('#4a6a2c')
    return np.clip(img, 0, 1)


def tex_river_water(name):
    """A river from high up: green-grey water, lighter than the sea, the current drawn out in long streaks."""
    rng = _rng(name)
    v = 0.45 + 0.2 * smooth_noise(T, T, 4, rng, cells_y=12) + 0.12 * smooth_noise(T, T, 2, rng, cells_y=24)
    glint = (rng.random((T, T)) < 0.03)
    v = np.where(glint, 0.9, v)
    return dither(np.clip(v, 0, 1), ramp(['#2a4450', '#365866', '#446c78', '#56828a', '#6e9aa0', '#b4ccd0']), 0.5)


def tex_harbor_water(name):
    """Open water from high up: dark blue-grey, a slow swell in it and small waves catching the light, short
    and many, lying the same way."""
    rng = _rng(name)
    swell = smooth_noise(T, T, 6, rng)
    v = 0.38 + 0.22 * swell + 0.1 * smooth_noise(T, T, 16, rng)
    crest = (rng.random((T, T)) < 0.05) & (swell > 0.45)
    crest |= np.roll(crest, 1, 1)                                 # each a short dash
    v = np.where(crest, 0.95, v)
    return dither(np.clip(v, 0, 1), ramp(['#141c24', '#1c2832', '#26343e', '#33434c', '#4a5c64', '#8a9ca0']), 0.5)


SKIN = ramp('#3e4440', dark=0.3, light=1.55, cool=0.2)
BELLY = ramp('#8a8070', dark=0.38, light=1.3, warm=0.12)
PLATE = ramp('#c8cec8', dark=0.35, light=1.15, cool=0.15)
GLOW = ramp(['#1a4a6a', '#2a7ab0', '#4ab4e8', '#8ee0ff', '#c8f4ff', '#f0ffff'])
EYE = ramp(['#6a2a08', '#a8480c', '#e07a18', '#ffb030', '#ffe080', '#fff8d0'])
IVORY = ramp('#d8d0b8', dark=0.45, light=1.12)
MOUTH = ramp('#3a1418', dark=0.5, light=1.6)
FOAM = ramp('#c8d4d8', dark=0.55, light=1.12, cool=0.1)
WADE = 92                               # the row the sea comes up to on a wading kaiju (its sprite is 126 tall)


def _along(pts, step):
    """Points every `step` along a polyline, with the unit direction there and how far along it is (0-1)."""
    pts = np.asarray(pts, np.float32)
    seg = np.diff(pts, axis=0)
    lens = np.hypot(seg[:, 0], seg[:, 1])
    ends = np.cumsum(lens)
    out = []
    for d in np.arange(0.0, ends[-1], step):
        i = min(int(np.searchsorted(ends, d, side='right')), len(seg) - 1)
        f = (d - (ends[i] - lens[i])) / max(lens[i], 1e-6)
        out.append((pts[i] + seg[i] * f, seg[i] / max(lens[i], 1e-6), d / ends[-1]))
    return out


def _crest(cv, spine, peak, rng, z, side=0.0, mat=2, step=6.0, mode='over'):
    """A crest of jagged plates along a spine (from the head down the tail): each a separate shard of several
    points standing out from the back, swept toward the tail, big and small by turns - small at the head, tallest
    (`peak`) over the shoulders and the middle of the back, dwindling down the tail; `side` shifts the row out
    from the back."""
    for i, ((x, y), (ux, uy), t) in enumerate(_along(spine, step)):
        nx, ny = uy, -ux                                         # out from the back
        s = peak * (0.3 + 0.7 * np.sin(np.pi * min(1.0, t * 1.6)) if t < 0.62 else 0.36 * (1.12 - t) / 0.5)
        s = max(2.2, s * rng.uniform(0.85, 1.1) * (1.0 if i % 2 == 0 else 0.68))
        x, y = x + nx * side, y + ny * side

        def at(out, back):                                       # a point `out` from the back, `back` toward the tail
            return (x + nx * out * s + ux * back * s, y + ny * out * s + uy * back * s)
        pts = [at(-0.15, -0.3), at(0.45, -0.26), at(0.52, -0.12), at(0.72, -0.1), at(0.66, 0.02), at(1.0, 0.24),
               at(0.6, 0.22), at(0.62, 0.38), at(0.32, 0.3), at(-0.15, 0.3)]
        pts = [(px + rng.uniform(-0.35, 0.35), py + rng.uniform(-0.35, 0.35)) for px, py in pts]
        cv.polygon(pts, z=z, top=0.5, bevel=1.4, mat=mat, tone=float(rng.uniform(-0.06, 0.06)), mode=mode)


def _back_edge(cv, rows, cols):
    """The kaiju's back traced from what is drawn so far: the right-hand edge of its body row by row (`rows`, from
    the head down to the hips), then the top edge of its tail column by column (`cols`) - a few texels in."""
    body = (cv.id > 0) & (cv.mat == 0)
    pts = []
    for y in rows:
        xs = np.nonzero(body[y, :86])[0]
        if len(xs):
            pts.append((float(xs.max()) - 2.0, float(y)))
    for x in cols:
        ys = np.nonzero(body[70:, x])[0]
        if len(ys):
            pts.append((float(x), float(ys.min()) + 70 + 2.0))
    return pts


def _kaiju(roar, wade=False):
    """The kaiju, three-quarters on, facing left: upright on legs like pillars set under its hips - the near one's
    haunch swelling out of the body, the belly whole in front of it - a heavy tail sweeping out behind it, small
    clawed arms held forward, a thick neck and a heavy, blunt head; charcoal skin pebbled over, a pale ridged
    belly, and two rows of jagged plates standing up along its back and tail. Roaring (`roar`), its head is thrown
    back and its jaws gape on two rows of teeth, the lower one hinged at the cheek into the neck; its plates glow a
    cold blue, and its throat, deep in the mouth. Wading (`wade`), the sea is up to its thighs: it stops in a ring
    of surf where the water meets it."""
    rng = np.random.default_rng(61)
    w, h = 124, 126
    cv = Canvas(w, h, wrap=False, ground=-9)
    hx, hy, tilt = (38, 17, -22) if roar else (38, 24, -6)
    cv.stroke([(68, 80), (84, 95), (98, 105), (110, 113), (121, 121)], 25, z=0.6, dome=1.0, taper=(1.0, 0.14), mat=0,
              tone=-0.05)                                        # the tail
    cv.stroke([(62, 48), (58, 56), (53, 62)], 6.5, z=0.62, dome=0.8, taper=(1.0, 0.7), mat=0, tone=-0.14)   # far arm
    cv.stroke([(72, 84), (75, 102), (76, 119)], 16, z=0.62, dome=1.0, taper=(1.0, 0.8), mat=0, tone=-0.1)   # far leg
    cv.ellipse(76, 120.5, 8.5, 3.8, z=0.64, dome=0.6, mat=0, tone=-0.1)
    for dx in (-6, -2.5):                                           # its claws, in the far leg's shade
        cv.stroke([(76 + dx, 121.5), (72.5 + dx, 124.3)], 1.4, z=0.8, dome=0.3, mat=4, tone=-0.16)
    cv.ellipse(57, 64, 23, 29, z=0.7, dome=1.4, angle=-10, mat=0)   # the body
    cv.ellipse(54, 44, 17, 13, z=0.85, dome=1.0, mat=0)             # the shoulders
    cv.stroke([(57, 42), (52, 33), (hx + 7, hy + 4)], 18, z=1.0, dome=1.0, taper=(1.0, 0.78), mat=0)   # the neck
    cv.ellipse(hx, hy, 12, 9, z=1.4, dome=1.1, angle=tilt, mat=0)                                        # the head
    back = _back_edge(cv, range(hy - 2, 86, 3), range(88, 122, 3))
    _crest(cv, back, 14, np.random.default_rng(62), z=0.0, side=2.5, step=8.5, mode='max')  # the far row
    _crest(cv, back, 20, rng, z=0.1, side=0.0, step=8.0, mode='max')                         # the near row, tallest
    cv.ellipse(51, 70, 8.5, 20, z=1.3, dome=0.8, angle=-8, mat=1)   # the belly
    for y in np.arange(54, 89, 3.6):                                # its ridges, each across the belly's width
        half = 8.5 * np.sqrt(max(0.0, 1 - ((y + 0.75 - 70) / 20) ** 2)) - 1.2
        if half > 1.5:
            cv.stroke([(51 - half, y), (51 + half, y + 1.5)], 1.0, z=2.2, dome=0.1, mat=1, tone=-0.2, mode='max')
    cv.ellipse(61, 88, 13.5, 15, z=1.0, dome=1.1, angle=-15, mat=0, mode='max')   # the near thigh, out of the hip
    cv.stroke([(59, 94), (57, 106), (55.5, 118)], 17, z=1.05, dome=1.1, taper=(1.0, 0.85), mat=0, mode='max')
    cv.ellipse(55.5, 104, 6.5, 5, z=1.75, dome=0.45, mat=0, mode='max', tone=0.03)  # the knee, a little forward
    cv.ellipse(52.5, 120.5, 11, 4.3, z=1.1, dome=0.6, mat=0)
    for dx in (-7, -3, 1):                                          # its claws
        cv.stroke([(53 + dx, 121.5), (49 + dx, 124.5)], 1.5, z=1.3, dome=0.3, mat=4)
    ca, sa = np.cos(np.radians(tilt)), np.sin(np.radians(tilt))
    sx, sy = hx - 11 * ca, hy - 11 * sa                                                                 # the snout
    cv.ellipse(sx, sy, 9, 5.4, z=1.6, dome=0.8, angle=tilt - 6, mat=0)
    cv.stroke([(hx - 4 * ca + 1.5 * sa, hy - 7), (hx + 6, hy - 7.5 - 2 * sa)], 2.6, z=2.0, dome=0.5, mat=0,
              tone=0.08)                                                                                # the brow
    if roar:                                                       # the jaws gape
        jx, jy = sx + 2.5, sy + 12
        cv.ellipse(jx, jy, 9.5, 3.4, z=1.45, dome=0.7, angle=22, mat=0)                                 # lower jaw
        cv.ellipse(hx + 2, hy + 13, 6, 7, z=1.45, dome=0.8, mat=0)                                   # the hinge
        cv.polygon([(sx - 7, sy + 3), (sx + 6, sy + 2.5), (jx + 5, jy - 1.5), (jx - 7, jy - 4)], z=1.5, top=0.2,
                   bevel=0.6, mat=7)                                                                    # the mouth
        cv.ellipse(sx + 5.5, sy + 5.2, 2.3, 1.6, z=1.52, dome=0.2, mat=3, tone=-0.15)                    # the throat
        for k in range(6):
            cv.polygon([(sx - 6.5 + k * 2.2, sy + 2.6), (sx - 5.3 + k * 2.2, sy + 2.6), (sx - 5.9 + k * 2.2, sy + 4.4)],
                       z=1.7, top=0.1, bevel=0.2, mat=4)                                                # upper teeth
            cv.polygon([(jx - 7.5 + k * 2.2, jy - 3.6 + k * 0.85), (jx - 6.3 + k * 2.2, jy - 3.6 + k * 0.85),
                        (jx - 6.9 + k * 2.2, jy - 5.4 + k * 0.85)], z=1.7, top=0.1, bevel=0.2, mat=4)   # lower
    else:
        cv.stroke([(sx - 7, sy + 3.2), (sx + 3, sy + 3.6), (hx + 2, hy + 5)], 1.0, z=1.9, dome=0.1, mat=0,
                  tone=-0.32)                                                                          # its mouth
        cv.ellipse(sx - 6.5, sy - 1.4, 0.8, 0.6, z=2.0, dome=0.1, mat=0, tone=-0.3)                    # a nostril
    cv.ellipse(hx - 2, hy - 3.4, 1.5, 1.0, z=2.1, dome=0.3, mat=5)                                       # the eye
    cv.stroke([(47, 48), (39, 56), (31, 60)], 8.0, z=1.6, dome=0.9, taper=(1.0, 0.72), mat=0)            # near arm
    for dy in (-1.8, 0.4, 2.6):
        cv.stroke([(31, 60 + dy), (26.5, 62.5 + dy)], 1.3, z=1.8, dome=0.3, mat=4)
    for _ in range(440):                                              # pebbled hide
        x, y = rng.uniform(18, 122), rng.uniform(4, 124)
        iy, ix = int(y), int(x)
        if cv.mat[iy, ix] == 0 and cv.id[iy, ix] > 0:
            cv.ellipse(x, y, 0.8, 0.8, z=float(cv.z[iy, ix]) + 0.04, dome=0.22, mat=0,
                       tone=float(rng.uniform(-0.12, 0.05)), mode='max')
    em = np.zeros((h, w), np.float32)
    if roar:
        em[(cv.mat == 2) & (cv.id > 0)] = 0.8
        em[(cv.mat == 3) & (cv.id > 0)] = 1.0
        cv.mat[cv.mat == 2] = 6                                       # the plates take the glow's colours
    em[(cv.mat == 5) & (cv.id > 0)] = 0.9
    if wade:                                                         # the sea at its thighs, and its surf
        cv.id[WADE:] = 0
        body = np.nonzero((cv.id[WADE - 4:WADE] > 0).any(0))[0]
        x0, x1 = float(body.min()) - 6, float(body.max()) + 6
        for x in np.arange(x0, x1, 2.2):                             # the surf round it, broken and thin
            if rng.random() < 0.22:
                continue
            cv.ellipse(x + rng.uniform(-1, 1), WADE + rng.uniform(-0.8, 0.4), rng.uniform(1.6, 3.4),
                       rng.uniform(0.6, 1.2), z=3.0, dome=0.6, mat=8, tone=float(rng.uniform(-0.08, 0.06)))
        for _ in range(26):                                           # spray thrown up
            x = rng.uniform(x0 + 4, x1 - 4)
            cv.ellipse(x, WADE - rng.uniform(3, 10), rng.uniform(0.5, 1.2), rng.uniform(0.5, 1.2), z=3.2,
                       dome=0.3, mat=8, tone=float(rng.uniform(-0.04, 0.08)))
    rgba = cv.paint([SKIN, BELLY, PLATE, GLOW, IVORY, EYE, GLOW, MOUTH, FOAM],
                    cv.light(relief=1.1, cavity=0.4, shadow=0.45), dither=0.3)
    rgba = outline_sprite(rgba).astype(np.float32)
    if wade:                                                         # it stands on the water at its surf line
        return rgba[:WADE + 2], em[:WADE + 2]
    return rgba, em


FLAME = [ramp(['#4a0e06', '#7a1a08', '#b8300c', '#e8500e', '#ff7a1a', '#ffb040']),
         ramp(['#a83a08', '#d85a0c', '#ff8418', '#ffa830', '#ffcc50', '#ffe890']),
         ramp(['#ffb030', '#ffcc50', '#ffe080', '#fff0b0', '#fff8d8', '#ffffff'])]
SMOKE = ramp(['#141210', '#221e1a', '#322c26', '#443c34', '#5a5046', '#6e6458'])
OLIVE = ramp('#4a5236', dark=0.4, light=1.4)
STEEL = ramp('#6a6e74', dark=0.4, light=1.5, cool=0.15)


def spr_blaze():
    """A building ablaze, seen from a giant's height: a mass of flame tongues of red, orange and a white-yellow
    heart rising from embers, every one glowing (additive)."""
    rng = np.random.default_rng(71)
    w, h = 48, 56
    cv = Canvas(w, h, wrap=False)
    for mat, n, hmin, hmax, wid in ((0, 9, 26, 50, 9), (1, 7, 18, 38, 7), (2, 5, 10, 24, 5)):
        for _ in range(n):
            x = rng.uniform(8, 40)
            top = h - rng.uniform(hmin, hmax)
            cv.leaf(x + rng.uniform(-2, 2), h - 2, x + rng.uniform(-5, 5), top, wid * rng.uniform(0.8, 1.2),
                    z=mat, dome=0.6, rib=0.0, base=0.3, shape=1.4, mat=mat)
    rgba = cv.paint(FLAME, cv.light(relief=0.4), dither=0.3, outline=0)
    em = np.where(cv.id > 0, (0.7, 0.9, 1.0)[0] + 0.15 * cv.mat, 0.0).astype(np.float32)
    return rgba.astype(np.float32), np.clip(em, 0, 1)


def spr_smoke_plume():
    """A column of smoke from a burning city, a hundred metres and more: billows heaped on billows, rising and
    widening and leaning with the wind, dark brown-grey with paler tops where the sky lights them, lit orange at
    its foot by the fire under it."""
    rng = np.random.default_rng(73)
    w, h = 64, 140
    cv = Canvas(w, h, wrap=False)
    puffs = []
    for k in range(90):
        t = rng.random() ** 0.85                                  # from the foot up, more of them high up
        width = 4 + 20 * t ** 0.8
        x = 16 + 30 * t ** 1.7 + rng.normal(0, width * 0.38)
        y = h - 6 - (h - 24) * t + rng.normal(0, 2.5)
        r = rng.uniform(0.35, 0.6) * width
        puffs.append((rng.random(), x, y, r, t))
    for z, x, y, r, t in sorted(puffs):                           # far ones first, so the near heap over them
        cv.ellipse(x, y, r, r * rng.uniform(0.75, 0.95), z=z * 2, dome=1.0, rough=0.25, rng=rng,
                   mat=1 if t < 0.1 else 0, tone=float(-0.12 + 0.18 * t + rng.uniform(-0.04, 0.04)))
    rgba = cv.paint([SMOKE, FLAME[0]], cv.light(sun=(-0.4, -0.85, 0.55), relief=1.2, ambient=0.45, cavity=0.3),
                    dither=0.4, outline=0)
    em = np.where((cv.mat == 1) & (cv.id > 0), 0.5, 0.0).astype(np.float32)
    return rgba.astype(np.float32), em


def spr_ash_plume():
    """A volcano's column of ash, a kilometre and more: billows boiling up from the crater, dense and dark,
    rising nearly straight and spreading out at the top into a flattened head the wind drags aside; lit orange
    from below by the fire in the crater (it glows there)."""
    rng = np.random.default_rng(91)
    w, h = 120, 190
    cv = Canvas(w, h, wrap=False)
    puffs = []
    for k in range(170):
        t = rng.random() ** 0.8                                   # from the foot up
        width = 8 + 16 * t if t < 0.72 else 20 + 120 * (t - 0.72)  # a column, then the head spreading out
        x = 46 + 10 * t + 22 * max(0.0, t - 0.7) / 0.3 + rng.normal(0, width * 0.32)
        y = h - 6 - (h - 30) * t + rng.normal(0, 3.0)
        r = rng.uniform(0.32, 0.55) * min(width, 40)
        puffs.append((rng.random(), x, y, r, t))
    for z, x, y, r, t in sorted(puffs):
        cv.ellipse(x, y, r, r * rng.uniform(0.7, 0.92), z=z * 2, dome=1.0, rough=0.28, rng=rng,
                   mat=1 if t < 0.22 else 0, tone=float(-0.16 + 0.14 * t + rng.uniform(-0.05, 0.05)))
    ash = ramp(['#0e0c0c', '#1a1716', '#262220', '#34302c', '#46403a', '#5a524a'])
    glow = ramp(['#3a0e06', '#6a1c08', '#a8360c', '#e05e16', '#ff8a2a', '#ffb850'])
    rgba = cv.paint([ash, glow], cv.light(sun=(-0.3, 0.6, 0.6), relief=1.2, ambient=0.42, cavity=0.3),
                    dither=0.4, outline=0)
    em = np.where((cv.mat == 1) & (cv.id > 0), 0.6, 0.0).astype(np.float32)
    return rgba.astype(np.float32), em


HULL = ramp('#2a3644', dark=0.35, light=1.5, cool=0.15)
RED_HULL = ramp('#7a2a22', dark=0.4, light=1.35)
WHITE = ramp('#d8dcdc', dark=0.45, light=1.12)
BOX = [ramp(c, dark=0.4, light=1.35) for c in ('#a8402c', '#2c5a8a', '#3a7a4a', '#b8a03a', '#7a7e84', '#c86a2a')]


def spr_cargo_ship():
    """A container ship, side on, bow to the left, two hundred metres of it: a long dark hull over a red boot-top
    at the waterline, its deck stacked with containers of every colour in bays, the white superstructure and
    bridge at the stern under its funnel; its lights lit."""
    rng = np.random.default_rng(83)
    w, h = 160, 38
    oy = 8                                                          # headroom for the funnel
    cv = Canvas(w, h, wrap=False)
    hull = [(2, 18 + oy), (8, 22 + oy), (150, 22 + oy), (158, 15 + oy), (156, 13 + oy), (4, 13 + oy)]
    cv.polygon(hull, z=0.4, top=0.6, bevel=1.2, mat=0)
    cv.polygon([(7, 21 + oy), (8, 23.5 + oy), (150, 23.5 + oy), (152, 21 + oy)], z=0.45, top=0.3, bevel=0.6, mat=1)   # the boot-top
    for bay in range(16):                                           # containers, bay by bay
        x0 = 14 + bay * 7.8
        if x0 > 124:
            break
        for tier in range(int(rng.integers(2, 5))):
            cv.box(x0, 12 + oy - tier * 2.6, 7.2, 2.5, z=0.8 + tier * 0.05, top=0.2, bevel=0.5,
                   mat=3 + int(rng.integers(0, len(BOX))), tone=float(rng.uniform(-0.06, 0.06)))
    cv.box(130, 2 + oy, 16, 11, z=0.9, top=0.3, bevel=0.8, mat=2)      # the superstructure
    cv.box(127, 1 + oy, 22, 2.4, z=1.0, top=0.2, bevel=0.5, mat=2)     # its bridge wings
    cv.box(141, -3 + oy, 5, 6, z=1.0, top=0.3, bevel=0.6, mat=1)       # the funnel
    for x in range(132, 145, 3):                                  # the bridge's windows
        cv.box(x, 3.4 + oy, 1.6, 1.0, z=1.2, top=0.05, bevel=0.2, mat=0, tone=-0.3)
    rgba = cv.paint([HULL, RED_HULL, WHITE] + BOX, cv.light(relief=1.0, cavity=0.3), dither=0.3)
    return outline_sprite(rgba).astype(np.float32), np.zeros(rgba.shape[:2], np.float32)


def spr_ferry():
    """A car ferry, side on, bow to the left: a white hull and two decks of windows, a blue band along it, a
    squat funnel; its windows lit."""
    w, h = 72, 28
    oy = 8
    cv = Canvas(w, h, wrap=False)
    cv.polygon([(2, 12 + oy), (6, 16 + oy), (66, 16 + oy), (70, 10 + oy), (69, 8 + oy), (3, 8 + oy)], z=0.4, top=0.6, bevel=1.0, mat=1)
    cv.box(6, 15 + oy, 60, 1.6, z=0.5, top=0.2, bevel=0.4, mat=0)                       # the band along the hull
    cv.box(12, 3 + oy, 46, 5, z=0.8, top=0.3, bevel=0.6, mat=1)                        # its decks
    cv.box(20, -1 + oy, 26, 4, z=0.9, top=0.3, bevel=0.6, mat=1)
    cv.box(36, -5 + oy, 5, 4.5, z=1.0, top=0.3, bevel=0.5, mat=0)                      # the funnel
    for x in range(14, 56, 3):
        cv.box(x, 4.5 + oy, 1.6, 1.2, z=1.1, top=0.05, bevel=0.2, mat=2)
    for x in range(22, 44, 3):
        cv.box(x, 0.4 + oy, 1.6, 1.2, z=1.1, top=0.05, bevel=0.2, mat=2)
    rgba = cv.paint([ramp('#2a5a9a', dark=0.4, light=1.35), WHITE, ramp('#e8d8a0', dark=0.5, light=1.1)],
                    cv.light(relief=1.0, cavity=0.3), dither=0.3)
    em = np.where((cv.mat == 2) & (cv.id > 0), 0.6, 0.0).astype(np.float32)
    return outline_sprite(rgba).astype(np.float32), em


def spr_sailboat():
    """A yacht under sail, side on, heeling a little: a white hull, a tall mainsail and a jib, white against the
    water."""
    w, h = 24, 36
    cv = Canvas(w, h, wrap=False)
    cv.polygon([(3, 29), (5, 32), (19, 32), (22, 28.5)], z=0.4, top=0.5, bevel=0.6, mat=1)
    cv.stroke([(12.5, 29), (13.5, 2)], 0.9, z=0.6, dome=0.2, mat=0)                 # the mast
    cv.polygon([(13.6, 3), (21, 27.5), (13.8, 27.5)], z=0.7, top=0.3, bevel=0.6, mat=1)   # the mainsail
    cv.polygon([(12.6, 5), (12.6, 27.5), (4.5, 27.5)], z=0.65, top=0.3, bevel=0.6, mat=1, tone=-0.06)  # the jib
    rgba = cv.paint([ramp('#6a6a70', dark=0.4, light=1.3), WHITE], cv.light(relief=1.0, cavity=0.3), dither=0.3)
    return outline_sprite(rgba).astype(np.float32), np.zeros(rgba.shape[:2], np.float32)


MOTH_WING = ramp('#c8742a', dark=0.35, light=1.3, warm=0.15)
MOTH_BAND = ramp('#5a3418', dark=0.4, light=1.3)
MOTH_SPOT = ramp(['#1a2a5a', '#2a4a8a', '#4a7ac0', '#8ab8f0', '#c8e4ff', '#f4fbff'])
MOTH_FUR = ramp('#a8946a', dark=0.4, light=1.25)
MOTH_EDGE = ramp(['#4a6a8a', '#6a9ac0', '#9acaf0', '#c8e8ff', '#e8f6ff', '#ffffff'])


def spr_giant_moth():
    """A giant moth, seen from in front and a little below as it flies at you: four wings spread - broad
    forewings with a pale band and an eye-spot each, smaller rounded hindwings - their edges glowing a cold
    blue-white; a furry body, feathery antennae, eyes that glow."""
    rng = np.random.default_rng(7)
    w, h = 160, 96
    cv = Canvas(w, h, wrap=False)
    cx = w / 2
    for side in (-1, 1):
        def m(pts, grow=0.0):
            cxp, cyp = 30.0, 40.0                                # grown about the wing's middle, for the rim
            return [(cx + side * (x + (x - cxp) * grow), y + (y - cyp) * grow) for x, y in pts]
        hind = [(4, 44), (20, 50), (44, 62), (56, 78), (48, 90), (30, 88), (12, 72), (4, 58)]
        fore = [(4, 40), (18, 22), (40, 8), (66, 2), (78, 6), (76, 18), (66, 34), (52, 46), (30, 52), (8, 50)]
        cv.polygon(m(hind, 0.05), z=0.45, top=0.3, bevel=0.6, mat=4)                       # a rim of light
        cv.polygon(m(hind), z=0.5, top=0.6, bevel=2.0, mat=0, tone=-0.08)                    # the hindwing
        cv.polygon(m(fore, 0.04), z=0.75, top=0.3, bevel=0.6, mat=4)
        cv.polygon(m(fore), z=0.8, top=0.7, bevel=2.4, mat=0)                                # the forewing
        for (x0, y0), (x1, y1) in (((6, 40), (60, 6)), ((6, 42), (74, 14)), ((6, 44), (62, 36)), ((6, 46), (40, 50)),
                                   ((6, 48), (28, 70)), ((6, 50), (46, 84)), ((6, 52), (52, 74))):
            cv.stroke(m([(x0, y0), (x1, y1)]), 1.0, dome=0.5, mode='carve')                     # its veins, pressed in
        cv.polygon(m([(22, 30), (46, 14), (70, 8), (72, 12), (50, 22), (28, 36)]), z=1.2, top=0.2, bevel=1.0,
                   mat=0, tone=0.25)                                                          # a pale band
        cv.polygon(m([(10, 44), (30, 44), (48, 40), (60, 32), (62, 36), (48, 46), (28, 50), (10, 48)]), z=1.15,
                   top=0.2, bevel=1.0, mat=1, tone=-0.1)                                      # a dark band
        for (sx, sy, r) in ((44, 30, 8.0), (34, 72, 5.5)):                                   # eye-spots, ringed
            cv.ellipse(cx + side * sx, sy, r, r * 0.88, z=1.3, dome=0.4, mat=1, tone=-0.2)
            cv.ellipse(cx + side * sx, sy, r * 0.72, r * 0.64, z=1.35, dome=0.4, mat=0, tone=0.35)
            cv.ellipse(cx + side * sx, sy, r * 0.46, r * 0.42, z=1.45, dome=0.5, mat=2)
        cv.stroke(m([(3, 18), (10, 8), (20, 2)]), 1.6, z=1.6, dome=0.4, mat=3)                # an antenna
        for k in range(6):
            x, y = 3 + k * 3, 18 - k * 3
            cv.stroke(m([(x, y), (x + 3, y + 1.5)]), 0.8, z=1.6, dome=0.2, mat=3)              # its feathers
    cv.ellipse(cx, 62, 6, 20, z=1.5, dome=1.1, mat=3, tone=-0.05)                             # the abdomen
    for y in range(46, 82, 4):
        cv.stroke([(cx - 5, y), (cx + 5, y)], 1.0, z=2.3, dome=0.1, mat=3, tone=-0.25, mode='max')   # its rings
    cv.ellipse(cx, 36, 9, 11, z=1.8, dome=1.1, rough=0.22, rng=rng, mat=3, tone=0.08)         # the furry thorax
    cv.ellipse(cx, 22, 7, 6, z=1.9, dome=1.0, rough=0.12, rng=rng, mat=3)                     # the head
    for side in (-1, 1):
        cv.ellipse(cx + side * 4.5, 21, 2.6, 2.4, z=2.3, dome=0.4, mat=2, tone=0.3)           # the eyes
    rgba = cv.paint([MOTH_WING, MOTH_BAND, MOTH_SPOT, MOTH_FUR, MOTH_EDGE], cv.light(relief=1.1, cavity=0.3), dither=0.3)
    em = np.zeros((h, w), np.float32)
    em[(cv.mat == 2) & (cv.id > 0)] = 0.8
    em[(cv.mat == 4) & (cv.id > 0)] = 1.0
    return outline_sprite(rgba).astype(np.float32), em


def _tanks(firing):
    """A column of four tanks, side on, facing left, olive drab on dark tracks, their guns raised toward something
    tall; `firing`: a flash at every muzzle."""
    w, h = 76, 14
    cv = Canvas(w, h, wrap=False)
    for k in range(4):
        x = 4 + k * 18
        cv.box(x, h - 4, 15, 3, z=0.4, top=0.4, bevel=0.8, mat=1)                  # tracks
        cv.box(x + 1, h - 7, 13, 3.5, z=0.7, top=0.5, bevel=0.8, mat=0)          # hull
        cv.ellipse(x + 7, h - 8, 4, 2.2, z=1.0, dome=0.6, mat=0)                  # turret
        cv.stroke([(x + 5, h - 8.5), (x - 2, h - 12.5)], 1.0, z=1.1, dome=0.2, mat=0)   # the gun, raised
        if firing:
            cv.ellipse(x - 3, h - 13, 2.2, 1.4, z=1.3, dome=0.3, mat=2)
    rgba = cv.paint([OLIVE, ramp('#26262a', dark=0.5, light=1.6), FLAME[2]], cv.light(relief=0.8), dither=0.2)
    em = ((cv.mat == 2) & (cv.id > 0)).astype(np.float32)
    return outline_sprite(rgba).astype(np.float32), em


def spr_tanks():
    return _tanks(False)


def spr_tanks_firing():
    return _tanks(True)


def spr_helicopter():
    """An army helicopter, side on, nose to the left: an olive body, a tail boom to its rotor, skids, the blur of
    its main rotor over it and a lamp burning at its nose."""
    w, h = 44, 16
    cv = Canvas(w, h, wrap=False)
    cv.stroke([(18, 9), (40, 7)], 2.0, z=0.6, dome=0.4, taper=(1.0, 0.6), mat=0)          # tail boom
    cv.ellipse(40, 6, 2.2, 2.2, z=0.7, dome=0.3, mat=1)                                     # tail rotor
    cv.ellipse(14, 9, 9, 4.2, z=1.0, dome=1.0, mat=0)                                       # body
    cv.ellipse(9, 8, 3.6, 2.4, z=1.3, dome=0.6, mat=2)                                      # canopy
    cv.stroke([(6, 14), (22, 14)], 0.9, z=0.8, dome=0.1, mat=1)                             # skids
    cv.stroke([(1, 3.5), (30, 3.0)], 1.0, z=1.2, dome=0.1, mat=1)                           # rotor blur
    cv.ellipse(5.5, 10, 1.0, 0.9, z=1.5, dome=0.2, mat=3)                                   # the lamp
    rgba = cv.paint([OLIVE, ramp('#3a3a3e', dark=0.5, light=1.6), ramp('#6a8090', light=1.6), FLAME[2]],
                    cv.light(relief=0.8), dither=0.2)
    em = ((cv.mat == 3) & (cv.id > 0)).astype(np.float32)
    return outline_sprite(rgba).astype(np.float32), em


def spr_jet():
    """A fighter jet, side on, nose to the left: a grey fuselage, swept wing and tail fin, the canopy, and its
    afterburner glowing at the tail."""
    w, h = 44, 14
    cv = Canvas(w, h, wrap=False)
    cv.polygon([(30, 7), (38, 1), (41, 1), (38, 7)], z=0.6, top=0.3, bevel=0.6, mat=0)     # the fin
    cv.stroke([(3, 8), (16, 7), (38, 7.5)], 3.6, z=1.0, dome=0.9, taper=(0.5, 1.0), mat=0)  # fuselage
    cv.polygon([(16, 8), (30, 8), (34, 12), (26, 12)], z=1.1, top=0.3, bevel=0.6, mat=0)   # the wing
    cv.ellipse(12, 5.8, 3.4, 1.4, z=1.4, dome=0.5, mat=1)                                   # canopy
    cv.ellipse(41.5, 7.5, 2.0, 1.4, z=1.3, dome=0.3, mat=2)                                 # afterburner
    rgba = cv.paint([STEEL, ramp('#405060', light=1.7), FLAME[1]], cv.light(relief=0.8), dither=0.2)
    em = ((cv.mat == 2) & (cv.id > 0)).astype(np.float32)
    return outline_sprite(rgba).astype(np.float32), em


def spr_pylon():
    """An electricity pylon at landscape scale - fifty metres of steel lattice, about a kaiju's waist: legs
    splayed at its foot, drawing in to a waist, three crossarms with insulators hanging from their tips, braced
    all the way up in diagonals; see-through between its members."""
    w, h = 48, 120
    img = np.zeros((h, w, 4), np.float32)
    steel = np.array([0.42, 0.44, 0.46], np.float32)

    def line(x0, y0, x1, y1, c=steel):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 2
        for t in np.linspace(0, 1, n):
            x, y = int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))
            if 0 <= x < w and 0 <= y < h:
                img[y, x, :3] = c * (0.85 + 0.3 * (1 - y / h))
                img[y, x, 3] = 1.0
    cx = w / 2 - 0.5
    half = lambda y: 2.5 + 14.5 * ((y - 18) / (h - 19)) ** 1.6 if y > 18 else 2.5  # noqa: E731
    ys = list(range(18, h, 9)) + [h - 1]
    for y0, y1 in zip(ys, ys[1:]):                                # the legs and the bracing between them
        for sgn in (-1, 1):
            line(cx + sgn * half(y0), y0, cx + sgn * half(y1), y1)
        line(cx - half(y0), y0, cx + half(y1), y1)
        line(cx + half(y0), y0, cx - half(y1), y1)
        line(cx - half(y1), y1, cx + half(y1), y1)
    line(cx - 2.5, 0, cx - 2.5, 18)
    line(cx + 2.5, 0, cx + 2.5, 18)
    for y, reach in ((6, 15), (14, 19), (22, 14)):                # the crossarms, insulators hanging
        line(cx - reach, y, cx + reach, y)
        line(cx - reach, y, cx - 2.5, y - 4)
        line(cx + reach, y, cx + 2.5, y - 4)
        for sgn in (-1, 1):
            line(cx + sgn * reach, y + 1, cx + sgn * reach, y + 4, np.array([0.7, 0.74, 0.7], np.float32))
    return img, np.zeros((h, w), np.float32)


def spr_kaiju():
    return _kaiju(False)


def spr_kaiju_roar():
    return _kaiju(True)


def spr_kaiju_wading():
    return _kaiju(True, wade=True)


TEXTURES = {'city_street': lambda n: _street(n, False), 'city_street_lit': lambda n: _street(n, True),
            'harbor_water': lambda n: (tex_harbor_water(n), None), 'quay': lambda n: (tex_quay(n), None),
            'container_yard': lambda n: (tex_container_yard(n), None), 'city_park': lambda n: (tex_city_park(n), None),
            'farmland': lambda n: (tex_farmland(n), None), 'farmland_b': lambda n: (tex_farmland(n), None),
            'farmland_c': lambda n: (tex_farmland(n), None), 'farmland_d': lambda n: (tex_farmland(n), None),
            'farmland_e': lambda n: (tex_farmland(n), None), 'farmland_f': lambda n: (tex_farmland(n), None),
            'forest_canopy': lambda n: (tex_forest_canopy(n), None),
            'pine_canopy': lambda n: (tex_pine_canopy(n), None), 'river_water': lambda n: (tex_river_water(n), None),
            'pasture': lambda n: (tex_pasture(n), None), 'road_ew': lambda n: (tex_road(n), None),
            'road_ns': lambda n: (tex_road(n, False, True), None), 'road_x': lambda n: (tex_road(n, True, True), None),
            'lava_field': tex_lava_field, 'lava_flow': tex_lava_flow, 'black_sand': lambda n: (tex_black_sand(n), None),
            'desert_floor': lambda n: (tex_desert_floor(n), None), 'desert_floor_b': lambda n: (tex_desert_floor(n), None),
            'desert_floor_c': lambda n: (tex_desert_floor(n), None), 'desert_road': lambda n: (tex_desert_road(n, False), None),
            'desert_road_ew': lambda n: (tex_desert_road(n), None), 'snow_fields': lambda n: (tex_snow_fields(n), None),
            'snow_fields_b': lambda n: (tex_snow_fields(n), None), 'snow_forest': lambda n: (tex_snow_forest(n), None),
            'frozen_lake': lambda n: (tex_frozen_lake(n), None), 'frozen_lake_b': lambda n: (tex_frozen_lake(n), None),
            'frozen_lake_c': lambda n: (tex_frozen_lake(n), None), 'ocean': lambda n: (tex_ocean(n), None),
            'lagoon': lambda n: (tex_lagoon(n), None), 'reef_flat': lambda n: (tex_reef_flat(n), None),
            'white_sand': lambda n: (tex_white_sand(n), None), 'palm_canopy': lambda n: (tex_palm_canopy(n), None)}
TEXTURE_NOISE = {'city_street': 0.15, 'city_street_lit': 0.15, 'harbor_water': 0.1, 'quay': 0.2, 'container_yard': 0.1,
                 'city_park': 1.0, 'farmland': 1.0, 'farmland_b': 1.0, 'farmland_c': 1.0, 'farmland_d': 1.0,
                 'farmland_e': 1.0, 'farmland_f': 1.0, 'pasture': 1.0, 'forest_canopy': 1.0, 'pine_canopy': 1.0,
                 'river_water': 1.0, 'road_ew': 0.6, 'road_ns': 0.6, 'road_x': 0.6, 'lava_field': 0.5,
                 'lava_flow': 0.0, 'black_sand': 0.6, 'desert_floor': 0.8, 'desert_floor_b': 0.8,
                 'desert_floor_c': 0.8, 'desert_road': 0.5, 'desert_road_ew': 0.5, 'snow_fields': 0.4,
                 'snow_fields_b': 0.4, 'snow_forest': 0.8, 'frozen_lake': 0.4, 'frozen_lake_b': 0.4,
                 'frozen_lake_c': 0.4, 'ocean': 0.6, 'lagoon': 0.3, 'reef_flat': 0.5, 'white_sand': 0.5,
                 'palm_canopy': 0.8}                 # the country mottled in full, as soil and weather lie across it
TEXTURE_REFLECT = {'harbor_water': 0.35, 'river_water': 0.5, 'frozen_lake': 0.18, 'frozen_lake_b': 0.18,
                   'frozen_lake_c': 0.18, 'ocean': 0.12, 'lagoon': 0.1}
SPRITES = {'kaiju': spr_kaiju, 'kaiju_roar': spr_kaiju_roar, 'kaiju_wading': spr_kaiju_wading, 'blaze': spr_blaze,
           'smoke_plume': spr_smoke_plume,
           'tanks': spr_tanks, 'tanks_firing': spr_tanks_firing, 'helicopter': spr_helicopter, 'jet': spr_jet,
           'pylon': spr_pylon, 'ash_plume': spr_ash_plume, 'cargo_ship': spr_cargo_ship, 'ferry': spr_ferry,
           'sailboat': spr_sailboat, 'giant_moth': spr_giant_moth}
SPRITE_HEIGHT = {'kaiju': 0.62, 'kaiju_roar': 0.62, 'kaiju_wading': round(0.62 * (WADE + 2) / 126, 3), 'blaze': 0.24,
                 'smoke_plume': 1.2,
                 'tanks': 0.045,
                 'tanks_firing': 0.045, 'helicopter': 0.05, 'jet': 0.045, 'pylon': 0.55, 'ash_plume': 9.0,
                 'cargo_ship': 0.5, 'ferry': 0.28, 'sailboat': 0.16, 'giant_moth': 0.72}
PROP_DEFAULTS = {'blaze': {'blend': 'additive', 'shadow': False}, 'smoke_plume': {'opacity': 0.85, 'shadow': False},
                 'helicopter': {'shadow': False}, 'jet': {'shadow': False}, 'pylon': {'planes': 2},
                 'ash_plume': {'opacity': 0.92, 'shadow': False}, 'giant_moth': {'shadow': False}}
NO_CONTACT_SHADOW = {'blaze', 'smoke_plume', 'helicopter', 'jet', 'ash_plume', 'giant_moth'}

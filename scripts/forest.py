"""The temperate forest, drawn with the pixel-art toolkit (scripts/pixelart.py): spruce, oak and
birch, bushes, the forest floor, bark and leaves for walls, and the `forest` fringe - long cards
of trees standing in front of a forest's edge, sparse at the front and dense at the back - and the
same wood in autumn and in winter, and a deer.

Like the jungle (biomes.py), every shape is stamped into a height field, lit from the upper left
and snapped onto hue-shifted ramps, so the trees read as pixel art rather than noise.
"""
import numpy as np

from biomes import CARD_PX, CARD_W, T, _crown, _leaf_layers, _prop, _rng, _stamp, _tile
from pixelart import Canvas, ramp, smooth_noise

NEEDLE = ramp('#2e5a3a', dark=0.26, light=1.3, warm=0.08)       # spruce: a dark blue-green
NEEDLE_DRY = ramp('#5e4630', dark=0.35, light=1.15)              # fallen needles, a dull rust brown
OAK_LEAF = ramp('#4e7a30')
OAK_SHADE = ramp('#2e5432', dark=0.3)
BIRCH_LEAF = ramp('#8eaa3e', dark=0.35, light=1.25)
AUTUMN = [ramp('#b8622a'), ramp('#c89a34'), ramp('#8a3a22'), ramp('#3a2a1e', dark=0.4)]
BIRCH_GOLD = ramp('#d2a83a', dark=0.35, light=1.22, warm=0.1)
WINTER_BARK = ramp('#4e4640', dark=0.3, light=1.4)
DEER_COAT = ramp('#8a6444', dark=0.32, light=1.3)
DEER_PALE = ramp('#d8ccb8', dark=0.5, light=1.06)
ANTLER = ramp('#c8b898', dark=0.4, light=1.12)
PINE_BARK = ramp('#6e4a34', dark=0.25)
OAK_BARK = ramp('#665a4c', dark=0.25)
BIRCH_BARK = ramp('#e6e2d4', dark=0.45, light=1.06, warm=0.04)
BIRCH_MARK = ramp('#2a2622', dark=0.6, light=1.6)
FOREST_SOIL = ramp('#4a3a2a', dark=0.35)
FOREST_MOSS = ramp('#4e6e2c', dark=0.3)
STONE = ramp('#7a786e', dark=0.35)
SNOW = ramp('#e2eaf2', dark=0.5, light=1.07, warm=0.0, cool=0.25)


def _along(pts, t):
    """The point a fraction t of the way along a polyline."""
    pts = np.asarray(pts, np.float32)
    seg = np.diff(pts, axis=0)
    lens = np.hypot(seg[:, 0], seg[:, 1])
    cum = np.concatenate([[0.0], np.cumsum(lens)])
    d = t * cum[-1]
    i = int(min(max(np.searchsorted(cum, d, side='right') - 1, 0), len(seg) - 1))
    return pts[i] + seg[i] * ((d - cum[i]) / max(lens[i], 1e-6))


# ---------------------------------------------------------------- trees

def _turn(cv, rng, leaf, mats, weights, cells=4, mix=0.4):
    """Turn a crown for autumn: its leaves (material `leaf`) take the materials in `mats` in
    patches, by a smooth noise field, so sides of the tree turn together the way a real one does
    - not a speckle of every colour - but with each leaf cluster nudged by a chance of its own
    (`mix`), so the patches run into each other cluster by cluster instead of along a line."""
    own = rng.random(cv.n + 1)[cv.id]
    zone = smooth_noise(cv.w, cv.h, cells, rng, wrap=False) * (1 - mix) + own * mix
    leaves = (cv.mat == leaf) & (cv.id > 0)
    if not leaves.any():
        return
    q = np.quantile(zone[leaves], np.cumsum(weights)[:-1] / float(sum(weights)))
    cv.mat = np.where(leaves, np.asarray(mats)[np.searchsorted(q, zone)], cv.mat).astype(np.int32)


def _spruce(snow=False, v=0):
    """The spruce, bare or under snow (see spr_pine and spr_snowy_pine); variant v another spruce - its
    tiers hung and spread another way, fuller or leaner."""
    rng = np.random.default_rng(31 + 41 * v)
    srng = np.random.default_rng(37 + 41 * v)   # the snow's own stream, so the bare tree never changes
    full = (1.0, 0.88, 0.96, 0.92)[v % 4]      # no wider than the first: its canvas holds that one
    w, h = 72, 168
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(cx, h), (cx, 4)], 6, z=0.0, dome=1.0, taper=(1.3, 0.25), mat=1)
    top, foot, n = 3, h - 26, 12
    for i in reversed(range(n)):            # the lowest tier first: each tier hangs over the one below
        t = i / (n - 1)                     # 0 at the tip, 1 at the lowest tier
        hem = top + 8 + (foot - top - 8) * t ** 0.92 + rng.uniform(-1.5, 1.5)
        half = (3.5 + 30 * t ** 0.8) * rng.uniform(0.9, 1.08) * full
        skew = rng.uniform(-0.1, 0.1)       # no two tiers quite alike, nor their two sides
        tall = 9 + 12 * t
        z = 1.0 + 0.6 * (1 - t)
        drop = 2 + 4 * t                    # the tips droop below the middle of the hem
        teeth = max(2, int(half / 3.2))
        pts = [(cx, hem - tall)]
        for k in range(teeth * 2 + 1):      # the hem, right tip to left tip, ragged
            f = k / (teeth * 2)
            edge = abs(1 - 2 * f)           # 1 at the tips, 0 under the trunk
            dy = rng.uniform(1.5, 3.5) if k % 2 == 0 else -rng.uniform(0.5, 2.0)
            pts.append((cx + half * (1 + skew) - 2 * half * f, hem + drop * edge ** 2 + dy))
        cv.polygon(pts, z=z, top=1.0, bevel=3, mat=0, tone=0.04 * (1 - t) - 0.03)
        for _ in range(int(half * 3)):      # needle sprays on the skirt, swept down and out
            side = 1 if rng.random() < 0.5 else -1
            r = rng.uniform(0.15, 1.0)
            x = cx + side * half * r
            y = hem - rng.uniform(0, tall * (1 - r)) + rng.uniform(-0.5, 1.5)
            a = np.radians(90 - side * rng.uniform(20, 55))
            L = rng.uniform(3, 6)
            cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], 1.4, z=z + 0.9, dome=0.5,
                      taper=(1.0, 0.5), mat=0, tone=rng.normal(0.02, 0.04))
        if snow:
            _snow_tier(cv, srng, cx, hem, half, tall, skew, drop, z + 1.4, t)
    if not snow:
        return _prop(cv, [NEEDLE, PINE_BARK], relief=1.0, cavity=0.5, shadow=0.55, reach=6)
    cv.ellipse(cx - 0.3, top + 5, 1.2, 1.8, z=3.4, dome=0.8, mat=2)      # a cap on the leader
    return _prop(cv, [NEEDLE, PINE_BARK, SNOW], relief=1.0, cavity=0.5, shadow=0.55, reach=6)


def _snow_tier(cv, rng, cx, hem, half, tall, skew, drop, z, t):
    """Snow lying on one tier of a spruce: clumps along both shoulders, thickest a little way out
    from the trunk where the boughs are flattest, thinning to nothing before the drooping tips,
    and a soft drift across the middle where the tier above does not cover it."""
    k = float(np.clip(half / 14.0, 0.35, 1.0))     # small tiers near the top carry small clumps
    for side in (-1, 1):
        reach = half * (1 + skew * side)
        for f in np.linspace(0.18, rng.uniform(0.72, 0.9), 4 + int(6 * t)):
            x = cx + side * reach * f
            y = hem - tall + (tall + drop * f * f) * f - 1.2
            fat = np.sin(np.pi * min(1.0, f * 1.15)) ** 0.7
            cv.ellipse(x + rng.normal(0, 0.6), y + rng.normal(0, 0.4), (1.6 + 2.6 * fat * rng.uniform(0.8, 1.2)) * k,
                       (0.9 + 1.2 * fat) * max(k, 0.6), z=z, dome=0.7, rough=0.25, rng=rng, mat=2,
                       tone=0.03 * side * -1)
        for _ in range(int(2 + 3 * t)):     # crumbs fallen onto the hem below the shoulder
            f = rng.uniform(0.3, 0.8)
            cv.ellipse(cx + side * reach * f, hem - 1 + rng.uniform(-1, 1.5), rng.uniform(0.8, 1.6),
                       rng.uniform(0.6, 1.0), z=z, dome=0.5, mat=2, tone=-0.04)


def spr_pine():
    """A spruce: a straight trunk under tier on tier of drooping boughs. Each tier is a skirt of
    needles with a ragged hem hanging over the tier below; lit from the upper left, so every
    tier has a bright shoulder and a dark underside, and the heart of the tree is in shadow."""
    return _spruce()


def spr_snowy_pine():
    """The spruce after a snowfall: snow lying in clumps along every tier's shoulders, thickest
    near the trunk and gone before the drooping tips, crumbs of it on the hems, and a cap on the
    leader. Dark needles show between the tiers, so it still reads as a spruce at a distance."""
    return _spruce(snow=True)


def _oak(autumn=False, v=0):
    """The oak, green or turned (see spr_tree and spr_tree_autumn); variant v another oak - its crown's
    lobes set another way."""
    rng = np.random.default_rng(23 + 41 * v)
    jig = np.random.default_rng(900 + v).uniform(-5, 5, (8, 2)) if v else np.zeros((8, 2))
    w, h = 136, 128
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    for dx, spread in ((-1, 14), (1, 15), (-1, 7), (1, 8)):                # the root flare
        cv.polygon([(cx + dx * 4, h - 20), (cx + dx * spread, h), (cx + dx * (spread - 7), h), (cx, h - 8)],
                   z=0.2, top=0.7, bevel=2, mat=1, tone=-0.05)
    cv.stroke([(cx, h), (cx - 2, h - 26), (cx + 1, h - 50)], 12, z=0.4, dome=1.2, taper=(1.25, 0.9), mat=1)
    for _ in range(6):                      # furrows up the trunk
        fx = cx + rng.uniform(-4.5, 4.5)
        cv.stroke([(fx, h), (fx + rng.normal(0, 1), h - 24), (fx + rng.normal(0, 1.5), h - 46)], 1.0, dome=0.5,
                  mode='carve')
    limbs = [((cx + 1, h - 48), (cx - 22, h - 70), (cx - 40, h - 84), 6),
             ((cx + 1, h - 50), (cx + 20, h - 74), (cx + 40, h - 86), 6),
             ((cx, h - 52), (cx - 6, h - 80), (cx - 2, h - 100), 5),
             ((cx - 10, h - 64), (cx - 30, h - 96), (cx - 26, h - 106), 3.5),
             ((cx + 12, h - 66), (cx + 30, h - 98), (cx + 24, h - 108), 3.5)]
    for p0, p1, p2, wd in limbs:
        cv.stroke([p0, p1, p2], wd, z=0.6, dome=1.0, taper=(1.0, 0.45), mat=1)
    # the crown in separate lobes, so the outline is lumpy and the limbs show between them
    for (lx, ly, rx, ry, k), (jx, jy) in zip(((cx - 40, 58, 26, 19, 11), (cx + 42, 56, 26, 19, 11),
                                              (cx - 22, 34, 29, 23, 13), (cx + 22, 30, 29, 23, 13), (cx, 15, 25, 15, 9),
                                              (cx - 3, 52, 28, 18, 10), (cx + 54, 40, 14, 13, 5),
                                              (cx - 55, 44, 13, 12, 5)), jig):
        lx = float(np.clip(lx + jx, rx * 0.5 + 2, w - rx * 0.5 - 2))
        _crown(cv, rng, lx, max(ly + jy, ry * 0.7), rx, ry, k, size=(7, 11), leaf=4.0, z=1.0)
    leaves = (cv.mat == 0) & (cv.id > 0)    # lit from above: the top of the crown bright, its underside dark
    cv.tone += np.where(leaves, 0.1 - 0.24 * np.clip(np.arange(h)[:, None] / 80.0, 0, 1), 0).astype(np.float32)
    if not autumn:
        return _prop(cv, [OAK_LEAF, ramp('#5a4e40', dark=0.25)], relief=1.0, cavity=0.45, shadow=0.55, reach=7)
    _turn(cv, np.random.default_rng(231 + 41 * v), 0, [0, 2, 3], [0.45, 0.35, 0.2], cells=5)
    return _prop(cv, [AUTUMN[0], ramp('#5a4e40', dark=0.25), AUTUMN[1], AUTUMN[2]], relief=1.0, cavity=0.45,
                 shadow=0.55, reach=7)


def spr_tree():
    """An oak: a short, heavy trunk on a flared foot, limbs spreading into a broad crown of leaf
    clusters in lobes, lit from above, with gaps where the limbs show through."""
    return _oak()


def spr_tree_autumn():
    """The oak in autumn: the same tree with its crown turned in patches of orange, gold and rust,
    a side going first, the way a real one turns."""
    return _oak(autumn=True)


def _birch(autumn=False, v=0):
    """The birch, green or turned (see spr_birch and spr_birch_autumn); variant v another birch - its
    second stem leaning the other way or nearer upright, the crown hung another way."""
    rng = np.random.default_rng(37 + 41 * v)
    w, h = 72, 160
    cv = Canvas(w, h, wrap=False, ground=-9)
    lean = (1.0, -1.0, 0.55)[v % 3]
    stems = [([(34, h), (33, h - 60), (36, 34), (34, 12)], 5.0),
             ([(35, h), (35 + 6 * lean, h - 50), (35 + 13 * lean, h - 96), (35 + 17 * lean, 44)], 3.4)]
    for pts, wd in stems:
        cv.stroke(pts, wd, z=0.4, dome=1.0, taper=(1.15, 0.35), mat=1)
    for pts, wd in stems:                   # the black marks across the white bark
        for _ in range(int(wd * 4)):
            t = rng.uniform(0.02, 0.9)
            x, y = _along(pts, t)
            half = wd / 2 * (1.15 - 0.8 * t)
            cv.stroke([(x - half * 0.9, y), (x + half * rng.uniform(0.1, 0.8), y + rng.uniform(-0.3, 0.6))],
                      rng.uniform(0.9, 1.6), z=1.25, dome=0.2, mat=2)
    for x0, y0, x1, y1 in ((34, 70, 18, 52), (34, 58, 50, 40), (35, 44, 22, 26),
                           (35 + 13 * lean, 92, 35 + 25 * lean, 74), (36, 30, 46, 16)):
        cv.stroke([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 3), (x1, y1)], 1.4, z=0.7, dome=0.6, taper=(1, 0.4), mat=2)
    for _ in range(30):                     # the crown: clumps of small leaves hanging off drooping twigs
        a = rng.uniform(0, 2 * np.pi)
        r = rng.random() ** 0.7
        x, y = 36 + 4 * lean + np.cos(a) * 26 * r, 62 + np.sin(a) * 46 * r
        up = 0.08 if np.sin(a) < 0 else -0.06
        cv.stroke([(x - 2, y - 7), (x, y), (x + 1, y + 5)], 0.8, z=0.8, dome=0.3, mat=2)
        for _ in range(16):
            px, py = x + rng.normal(0, 3.6), y + rng.normal(0, 4.0) + 1.5
            b = np.radians(rng.uniform(55, 125))
            cv.leaf(px, py, px + np.cos(b) * 3.6, py + np.sin(b) * 3.6, 2.4, z=1.2 + (1 - r) * 0.5 + rng.random() * 0.2,
                    dome=0.5, rib=0.0, mat=0, tone=up + rng.normal(0, 0.05))
    if not autumn:
        return _prop(cv, [BIRCH_LEAF, BIRCH_BARK, BIRCH_MARK], relief=1.0, cavity=0.35, shadow=0.45)
    _turn(cv, np.random.default_rng(371 + 41 * v), 0, [0, 3], [0.8, 0.2])
    return _prop(cv, [BIRCH_GOLD, BIRCH_BARK, BIRCH_MARK, AUTUMN[0]], relief=1.0, cavity=0.35, shadow=0.45)


def spr_birch():
    """A birch: a slender white trunk banded with black, a second stem leaning off it, and an
    airy, drooping crown of small bright leaves with the sky showing through."""
    return _birch()


def spr_birch_autumn():
    """The birch in autumn: its small leaves gone to gold, a few patches already orange."""
    return _birch(autumn=True)


def _bush(autumn=False, v=0):
    """The shrub, green or turned (see spr_bush and spr_bush_autumn); variant v another shape of it -
    lower and wider, taller and rounder, lopsided."""
    rng = np.random.default_rng(13 + 29 * v)
    w, h = 64, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    cx, cy, rx, ry, n = ((32, 24, 30, 19, 18), (32, 27, 31, 16, 17), (32, 22, 26, 21, 18), (29, 25, 28, 18, 17))[v % 4]
    for k in range(6):
        a = np.radians(-150 + k * 24)
        cv.stroke([(32, h), (32 + np.cos(a) * 18, h + np.sin(a) * 18)], 1.6, z=0.2, dome=0.6, taper=(1, 0.5), mat=1)
    _crown(cv, rng, cx, cy, rx, ry, n, size=(6, 9), leaf=3.6, z=0.8)
    if not autumn:
        return _prop(cv, [OAK_LEAF, OAK_BARK], relief=1.0, cavity=0.45, shadow=0.5)
    _turn(cv, np.random.default_rng(131 + 29 * v), 0, [0, 2], [0.6, 0.4], cells=3)
    return _prop(cv, [AUTUMN[2], OAK_BARK, AUTUMN[0]], relief=1.0, cavity=0.45, shadow=0.5)


def _mushrooms(v=0):
    """A cluster of toadstools on the forest floor: domed caps on pale stems, the biggest at the back,
    the gills in shadow under each cap, white flecks on the red ones; variant v another cluster - more
    or fewer of them, leaning another way, red or brown."""
    rng = np.random.default_rng(141 + 19 * v)
    w, h = 40, 28
    cv = Canvas(w, h, wrap=False, ground=-9)
    n = (3, 4, 2, 5)[v % 4]
    red = v % 4 != 2
    sizes = [r * rng.uniform(0.85, 1.1) for r in (7.0, 5.0, 4.4, 3.4, 3.0)[:n]]
    side = 1 if rng.random() < 0.5 else -1
    xs = [20 + side * d + rng.uniform(-1.2, 1.2) for d in (0, -8.5, 8, -14, 13.5)[:n]]
    for i, (x, r) in enumerate(zip(xs, sizes)):                        # back (biggest) to front
        top = h - 1 - r * rng.uniform(1.3, 1.9)
        lean = rng.uniform(-1.5, 1.5)
        cv.stroke([(x, h - 1), (x + lean, top + r * 0.3)], max(1.6, r * 0.42), z=0.4 + 0.3 * i, dome=0.7, mat=1,
                  tone=rng.normal(0, 0.03))
        cv.ellipse(x + lean, top, r, r * 0.62, z=1.2 + 0.3 * i, dome=1.5, mat=0, tone=rng.normal(0, 0.05))
        cv.ellipse(x + lean, top + r * 0.42, r * 0.86, r * 0.22, z=0.9 + 0.3 * i, dome=0.3, mat=2)
        if red:
            for _ in range(int(r // 1.6)):                             # white flecks on the cap
                a = rng.uniform(np.pi * 1.1, np.pi * 1.9)
                d = rng.uniform(0.2, 0.75)
                cv.ellipse(x + lean + np.cos(a) * r * d, top + np.sin(a) * r * 0.55 * d + 0.5, 0.7, 0.55,
                           z=1.3 + 0.3 * i + 0.4, dome=0.2, mat=3)
    caps = [ramp('#a43a2c', dark=0.4, light=1.25), ramp('#8a5634', dark=0.4, light=1.25)]
    return _prop(cv, [caps[0] if red else caps[1], ramp('#ddd2ba', dark=0.45, light=1.1),
                      ramp('#9a8a70', dark=0.5, light=1.0), ramp('#f2ece0', dark=0.6, light=1.05)],
                 relief=1.0, cavity=0.4, shadow=0.45)


def spr_mushrooms():
    """A cluster of toadstools: domed caps on pale stems, gills in shadow, white flecks on the red."""
    return _mushrooms(0)


def spr_bush():
    """A rounded shrub: twigs fanning out of the ground under a mound of small leaf clusters,
    bright on top and dark underneath."""
    return _bush()


def spr_bush_autumn():
    """The shrub in autumn: gone to rust red and orange, the colour of a hedge-bank in October."""
    return _bush(autumn=True)


CUT_WOOD = ramp('#c49a64', dark=0.4, light=1.15)
DEAD_WOOD = ramp('#7e766a', dark=0.28, light=1.25)
LICHEN = ramp('#b8b070', dark=0.5)


def _rings(cv, cx, cy, rx, ry, n):
    """Growth rings carved into a cut face."""
    for k in range(1, n + 1):
        f = k / (n + 1)
        a = np.linspace(0, 2 * np.pi, 40)
        cv.stroke(list(zip(cx + np.cos(a) * rx * f, cy + np.sin(a) * ry * f)), 0.7, dome=0.25, mode='carve')


def _boulder(snow=False, v=0):
    """The boulder, mossy or under snow (see spr_boulder and spr_boulder_snow); variant v another
    boulder - its lesser lobe on the other side, taller, flatter."""
    rng = np.random.default_rng(61 + 37 * v)
    w, h = 48, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    (bx, by, brx, bry), (lx, ly, lrx, lry) = (((24, 25, 19, 15), (12, 19, 8, 7)), ((24, 25, 19, 14), (35, 18, 8, 7.5)),
                                              ((24, 23, 17, 17), (13, 27, 8, 6)), ((24, 27, 20, 12), (35, 23, 8.5, 6.5)))[v % 4]
    cv.ellipse(bx, by, brx, bry, z=0.0, dome=2.4, rough=0.14, rng=rng, mat=0, power=0.6)
    cv.ellipse(lx, ly, lrx, lry, z=0.5, dome=1.4, rough=0.2, rng=rng, mat=0, tone=0.04, mode='max')
    t = rng.uniform(-3, 3)
    cv.stroke([(28 + t, 11 + abs(t)), (26 + t, 18), (29 + t, 27)], 1.3, dome=0.8, mode='carve')
    cv.stroke([(9, 23), (16, 26)] if v % 2 == 0 else [(32, 24), (39, 27)], 1.0, dome=0.5, mode='carve')
    cv.noise(0.15, cells=8, rng=rng)
    solid = cv.id > 0
    moss = (smooth_noise(w, h, 5, rng, wrap=False) > 0.48) & solid & (np.arange(h)[:, None] < h * 0.48)
    if snow:
        return _snowcap(cv, rng, solid)
    cv.mat[moss] = 1
    cv.z[moss] += 0.2
    ys, xs = np.nonzero(solid & ~moss)
    for i in rng.choice(len(ys), 6, replace=False):
        cv.ellipse(xs[i], ys[i], rng.uniform(0.8, 1.5), rng.uniform(0.6, 1.1), z=cv.z[ys[i], xs[i]] + 0.05, dome=0.1,
                   mat=2, rough=0.3, rng=rng)
    return _prop(cv, [STONE, FOREST_MOSS, LICHEN], relief=1.1, cavity=0.5, shadow=0.5)


def _snowcap(cv, rng, solid):
    """Snow over the top of a rock: in each column, a layer from the top of the rock down, deep
    where the top is flat and thin where it falls away steeply, with a soft lumpy lower edge."""
    h, w = solid.shape
    rows = np.arange(h)[:, None]
    has = solid.any(0)
    top = np.where(has, solid.argmax(0), h).astype(np.float32)
    slope = np.abs(np.gradient(np.where(has, top, np.nan)))
    slope = np.nan_to_num(slope, nan=9.0)
    lump = smooth_noise(w, 1, 7, rng, wrap=False)[0]
    depth = np.clip(6.5 - 1.6 * slope, 0.0, 7.0) * (0.75 + 0.5 * lump)
    cap = solid & (rows < top[None, :] + depth[None, :])
    cv.mat[cap] = 3
    cv.z[cap] += 0.45
    cv.tone[cap] = 0.0
    return _prop(cv, [STONE, FOREST_MOSS, LICHEN, SNOW], relief=1.1, cavity=0.5, shadow=0.5)


def spr_boulder():
    """A boulder settled into the ground: a rounded mass with a lesser lobe and a crack or two,
    lit from the upper left, moss over its top and a few spots of lichen."""
    return _boulder()


def spr_boulder_snow():
    """The boulder under snow: a cushion of it over the top, deep where the rock is flat and thin
    down the steep sides, the grey rock showing below - for a winter shore instead of moss."""
    return _boulder(snow=True)


def spr_stump():
    """A sawn stump: a pale cut face ringed with growth rings, furrowed bark down its sides, roots
    spreading into the ground and a cushion of moss on one shoulder."""
    rng = np.random.default_rng(63)
    w, h = 40, 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    for dx, L in ((-1, 12), (1, 13), (-1, 7), (1, 6)):                     # the roots
        cv.stroke([(20 + dx * 6, h - 8), (20 + dx * (6 + L * 0.6), h - 3), (20 + dx * (6 + L), h)], 4, z=0.2,
                  dome=0.8, taper=(1.0, 0.4), mat=0)
    cv.box(8, 9, 24, h - 11, z=0.5, top=1.4, bevel=6, mat=0)
    for _ in range(6):                                                     # furrows in the bark
        x = rng.uniform(10, 30)
        cv.stroke([(x, 12), (x + rng.normal(0, 0.6), h - 3)], 0.9, dome=0.5, mode='carve')
    cv.ellipse(20, 9.5, 12, 5, z=2.4, dome=0.25, mat=1, tone=0.04)
    _rings(cv, 20, 9.5, 12, 5, 3)
    cv.ellipse(28, 13, 4, 3, z=2.2, dome=0.6, rough=0.3, rng=rng, mat=2)    # moss
    return _prop(cv, [OAK_BARK, CUT_WOOD, FOREST_MOSS], relief=1.0, cavity=0.45, shadow=0.45)


def spr_log():
    """A fallen trunk lying across the ground: bark in long ridges, the stub of a branch, moss along
    its top and the pale, ringed end where it broke off."""
    rng = np.random.default_rng(65)
    w, h = 88, 22
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(6, 13), (44, 12), (80, 13)], 15, z=0.0, dome=1.4, taper=(1.0, 0.92), mat=0)
    for _ in range(10):                                                    # ridges along the bark
        y, x0 = rng.uniform(7, 19), rng.uniform(4, 50)
        cv.stroke([(x0, y), (x0 + rng.uniform(14, 30), y + rng.normal(0, 0.6))], 0.9, dome=0.5, mode='carve')
    cv.stroke([(32, 7), (28, 1)], 4, z=1.3, dome=0.8, taper=(1.0, 0.6), mat=0)   # a branch stub
    cv.ellipse(81, 13, 4.2, 7.2, z=1.6, dome=0.3, mat=1)
    _rings(cv, 81, 13, 4.2, 7.2, 2)
    moss = (smooth_noise(w, h, 7, rng, wrap=False) > 0.5) & (cv.mat == 0) & (cv.id > 0) & (np.arange(h)[:, None] < 10)
    cv.mat[moss] = 2
    cv.z[moss] += 0.15
    return _prop(cv, [OAK_BARK, CUT_WOOD, FOREST_MOSS], relief=1.0, cavity=0.45, shadow=0.45)


def spr_dead_tree():
    """A dead tree: a split trunk on a gnarled foot, bare limbs forking into twigs, the bark gone
    grey and peeling in strips."""
    rng = np.random.default_rng(67)
    w, h = 128, 128
    cv = Canvas(w, h, wrap=False, ground=-9)

    def limb(x, y, ang, length, width, depth):
        pts = [(x, y)]
        for _ in range(4):
            ang += rng.normal(0, 0.16)
            x, y = x + np.cos(ang) * length / 4, y + np.sin(ang) * length / 4
            pts.append((x, y))
        cv.stroke(pts, width, z=0.4 + 0.15 * (4 - depth), dome=0.9, taper=(1.0, 0.6), mat=0)
        if depth > 1 and width > 1.0:
            for side in (-1, 1):
                if rng.random() < 0.85:
                    limb(x, y, ang + side * rng.uniform(0.35, 0.75), length * rng.uniform(0.55, 0.75), width * 0.6,
                         depth - 1)
    cx = w / 2
    for dx in (-1, 1):                                                     # the gnarled foot
        cv.stroke([(cx + dx * 3, h - 14), (cx + dx * 10, h - 3), (cx + dx * 14, h)], 4, z=0.2, dome=0.8,
                  taper=(1.0, 0.5), mat=0)
    cv.stroke([(cx, h), (cx - 1, h - 40), (cx - 3, h - 62)], 9, z=0.3, dome=1.1, taper=(1.25, 0.8), mat=0)
    limb(cx - 3, h - 62, -np.pi / 2 - 0.25, 31, 6.0, 4)
    limb(cx - 2, h - 56, -np.pi / 2 + 0.6, 26, 4.5, 3)
    limb(cx - 1, h - 44, -np.pi / 2 - 0.9, 21, 3.6, 3)
    for _ in range(7):                                                     # peeling strips of bark
        x = cx + rng.uniform(-3.5, 3.5)
        y = rng.uniform(h - 56, h - 6)
        cv.stroke([(x, y), (x + rng.normal(0, 0.5), y + rng.uniform(6, 14))], 0.9, dome=0.5, mode='carve')
    return _prop(cv, [DEAD_WOOD], relief=1.0, cavity=0.4, shadow=0.45)


# ---------------------------------------------------------------- textures

def tex_foliage(name, autumn=False):
    """A wall of forest: small leaves at three depths over a dark tangle of twigs, the deepest in
    shadow - the thicket behind a forest's edge. `autumn` turns it orange, gold and red."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.4, mat=3)      # the dark tangle at the back shows in the gaps
    for _ in range(5):                      # twigs in the dark behind the leaves
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, 2 * np.pi)
        cv.stroke([(x, y), (x + np.cos(a) * 14, y + np.sin(a) * 14)], 1.6, z=-0.9, dome=0.4, mat=3)
    layers = [(-0.6, 110, -0.26, (4, 7)), (0.2, 72, -0.12, (5, 8)), (1.0, 38, 0.0, (5, 9))]
    _leaf_layers(cv, rng, layers, [0, 1, 1, 2], angles=(0, 360), aspect=(0.45, 0.62), bend=0.15)
    ramps = AUTUMN if autumn else [OAK_LEAF, OAK_SHADE, NEEDLE, ramp('#2a2a20', dark=0.5)]
    return _tile(cv, ramps, cavity=0.5, shadow=0.6)


def _plates(cv, rng, rows, cols, fissure=1.4, bevel=2.6, stretch=1.0):
    """Fill a tiling canvas with a mosaic of irregular plates - every pixel belongs to its nearest
    seed point, and a fissure runs wherever two plates meet - each plate domed, tilted a little
    and given a tone of its own: pine bark, crazed mud, cracked paving."""
    n = rows * cols
    sx = (np.arange(n) % cols + rng.uniform(0.15, 0.85, n) + (np.arange(n) // cols % 2) * 0.5) * cv.w / cols
    sy = (np.arange(n) // cols + rng.uniform(0.15, 0.85, n)) * cv.h / rows
    yy, xx = np.mgrid[0:cv.h, 0:cv.w].astype(np.float32) + 0.5
    dx = np.abs(xx[..., None] - sx % cv.w)
    dy = np.abs(yy[..., None] - sy % cv.h)
    d = np.hypot(np.minimum(dx, cv.w - dx) * stretch, np.minimum(dy, cv.h - dy))   # stretch > 1: taller than wide
    order = np.argsort(d, axis=-1)
    d1 = np.take_along_axis(d, order[..., :1], -1)[..., 0]
    d2 = np.take_along_axis(d, order[..., 1:2], -1)[..., 0]
    edge = d2 - d1                          # 0 on the line where two plates meet
    near = order[..., 0]
    tilt = rng.normal(0, 0.03, (n, 2))
    inside = edge > fissure
    prof = np.clip((edge - fissure) / bevel, 0, 1) ** 0.6
    ox = (xx - sx[near] + cv.w / 2) % cv.w - cv.w / 2        # offsets from the plate's seed, round the wrap
    oy = (yy - sy[near] + cv.h / 2) % cv.h - cv.h / 2
    cv.z = np.where(inside, prof + tilt[near, 0] * ox + tilt[near, 1] * oy, cv.z).astype(np.float32)
    cv.id = np.where(inside, near + 1 + cv.n, cv.id).astype(np.int32)
    cv.mat = np.where(inside, 0, cv.mat).astype(np.int32)
    cv.tone = np.where(inside, rng.normal(0, 0.06, n)[near], cv.tone).astype(np.float32)
    cv.n += n


def tex_forest_deep(name, autumn=False, snow=False):
    """The inside of a wood seen from its edge: trunks at every depth in the dark, the farthest
    thinnest and darkest, low boughs and the odd clump of leaves catching a little light. Meant
    for the wall behind a `forest` fringe, so wherever the cards thin out it reads as more wood."""
    rng = _rng(name)
    cv = Canvas(T, ground=-2.0, mat=2)
    for depth in range(4):                  # back to front: more, thinner and darker trunks behind
        for _ in range((5, 4, 3, 2)[depth]):
            x = rng.random() * T
            wd = (2.0, 3.0, 4.2, 6.0)[depth] * rng.uniform(0.8, 1.2)
            ph, amp = rng.uniform(0, 2 * np.pi), rng.uniform(0.3, 1.0)     # a sway that repeats with the tile
            cv.stroke([(x + amp * np.sin(2 * np.pi * y / T + ph), y) for y in range(-4, T + 5, 4)], wd,
                      z=-1.6 + depth * 0.5, dome=0.6 + depth * 0.2, mat=1, tone=-0.42 + depth * 0.12)
            if rng.random() < 0.5:          # a bough off it
                y = rng.uniform(4, T - 4)
                side = 1 if rng.random() < 0.5 else -1
                cv.stroke([(x, y), (x + side * rng.uniform(6, 12), y - rng.uniform(2, 6))], wd * 0.35,
                          z=-1.5 + depth * 0.5, dome=0.4, mat=1, tone=-0.42 + depth * 0.12)
    for _ in range(14):                     # leaves hanging in front, catching a little light
        x, y = rng.random() * T, rng.random() * T
        for _ in range(9):
            px, py = x + rng.normal(0, 3), y + rng.normal(0, 2.4)
            a = np.radians(rng.uniform(0, 360))
            cv.leaf(px, py, px + np.cos(a) * 4.5, py + np.sin(a) * 4.5, 2.8, z=0.6 + rng.random() * 0.3, dome=0.5,
                    mat=0, tone=rng.normal(-0.2, 0.05), rib=0.2)
    leaf = ramp('#5c3218', dark=0.3) if autumn else OAK_SHADE      # `autumn`: the hanging leaves turned
    if snow:                                                       # `snow`: snow lying on the boughs instead
        leaf = ramp('#b8c4d4', dark=0.45, light=1.12, cool=0.2)
    return _tile(cv, [leaf, ramp('#3a3228', dark=0.4), ramp('#141a14', dark=0.6, light=1.4)],
                 cavity=0.4, shadow=0.5)


def tex_leaves_fallen(name):
    """The floor of a wood in autumn: fallen leaves lying thick and flat over dark earth, each its
    own colour - orange, gold, rust, the brown of last week's - a few still green, and grass blades
    poking through where they lie thin."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.4, cells=6, rng=rng)
    thin = smooth_noise(T, T, 3, rng)
    for i in range(240):
        x, y = rng.random() * T, rng.random() * T
        if thin[int(y) % T, int(x) % T] < 0.3 and rng.random() < 0.6:
            continue                        # thin patches: earth and grass show
        a = rng.random() * 2 * np.pi
        L = rng.uniform(3.5, 6.5)
        cv.leaf(x, y, x + np.cos(a) * L, y + np.sin(a) * L, L * rng.uniform(0.5, 0.75), z=0.2 + i * 0.002,
                dome=0.25, bend=rng.uniform(-0.2, 0.2), mat=int(rng.choice([1, 1, 2, 2, 3, 4, 4, 5])),
                tone=rng.normal(0, 0.06), rib=0.25)
    for _ in range(60):                     # grass through the thin places
        x, y = rng.random() * T, rng.random() * T
        if thin[int(y) % T, int(x) % T] > 0.42:
            continue
        a = np.radians(rng.uniform(-120, -60))
        cv.stroke([(x, y), (x + np.cos(a) * 3.5, y + np.sin(a) * 3.5)], 1.0, z=0.8, dome=0.4, taper=(1, 0.4), mat=6)
    return _tile(cv, [FOREST_SOIL, AUTUMN[0], AUTUMN[1], AUTUMN[2], AUTUMN[3], ramp('#8a7a3a', dark=0.35),
                      ramp('#4e6e2c', dark=0.3)], cavity=0.45, shadow=0.45, ambient=0.3, diffuse=0.65)


def tex_bark(name, pine=False):
    """Bark for trunks built as walls: an oak's long grey ridges, wavy and broken now and then,
    with deep furrows between them - or (`pine`) a pine's red-brown scales, irregular plates in
    loose rows split by dark fissures."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.9, mat=1)      # the furrows and fissures, deep and dark
    if pine:
        _plates(cv, rng, rows=6, cols=4, stretch=1.5)
        for _ in range(40):                 # flaking: thin ridges across the plates
            x, y = rng.random() * T, rng.random() * T
            cv.stroke([(x, y), (x + rng.uniform(3, 7), y + rng.normal(0, 0.6))], 0.9, dome=0.35, mode='carve')
    else:
        cols = 7
        for c in range(cols):
            x = c * T / cols + rng.uniform(-1, 1)
            y = start = rng.uniform(0, T)
            while y < start + T:
                L = rng.uniform(14, 30)
                ph = rng.uniform(0, 2 * np.pi)
                pts = [(x + 1.3 * np.sin((y + k) / 7 + ph) + rng.normal(0, 0.3), y + k) for k in np.linspace(0, L, 7)]
                cv.stroke(pts, rng.uniform(4.5, 7.0), z=0.0, dome=1.0, mat=0, tone=rng.normal(0, 0.05))
                y += L + rng.uniform(1.0, 3.0)
    cv.noise(0.12, cells=12, rng=rng)
    return _tile(cv, [PINE_BARK if pine else OAK_BARK, ramp('#2a1c14', dark=0.5)], cavity=0.65, shadow=0.5)


def tex_needles(name):
    """The floor of a conifer wood: a deep litter of fallen needles over dark soil, criss-crossed,
    mostly rust brown and a few still green, with the odd cone and twig."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.4, cells=5, rng=rng)
    for i in range(520):
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, np.pi)
        L = rng.uniform(3, 6)
        cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], 1.0, z=0.3 + i * 0.0012, dome=0.4,
                  mat=2 if rng.random() < 0.12 else 1, tone=rng.normal(0, 0.06))
    for _ in range(3):                      # cones
        x, y = rng.random() * T, rng.random() * T
        cv.ellipse(x, y, 2.0, 3.4, z=1.6, dome=1.0, angle=rng.uniform(0, 180), mat=3)
    for _ in range(3):                      # twigs
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, np.pi)
        cv.stroke([(x, y), (x + np.cos(a) * 6, y + np.sin(a) * 6 + 1), (x + np.cos(a) * 12, y + np.sin(a) * 12)],
                  1.4, z=1.3, dome=0.6, mat=4)
    return _tile(cv, [FOREST_SOIL, NEEDLE_DRY, NEEDLE, ramp('#6a4a2e'), OAK_BARK], cavity=0.35, shadow=0.35)


def tex_moss(name):
    """A bed of moss: soft cushions crowded together, lit on top with dark seams between them,
    and here and there a stone showing through."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.6, mat=1)
    for _ in range(5):
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(3, 6), rng.uniform(2.5, 4), z=-0.4, dome=0.7,
                   rough=0.2, rng=rng, mat=1, tone=rng.normal(0, 0.04))
    for _ in range(110):
        x, y, r = rng.random() * T, rng.random() * T, rng.uniform(3, 6.5)
        cv.ellipse(x, y, r, r * 0.8, z=0.1 + rng.random() * 0.3, dome=0.8, rough=0.3, rng=rng, mat=0,
                   tone=rng.normal(0, 0.06))
        for _ in range(int(r * 2)):          # the fine bobbles of the moss
            cv.ellipse(x + rng.normal(0, r * 0.5), y + rng.normal(0, r * 0.4), 0.9, 0.9, dome=0.3, mode='add')
    return _tile(cv, [FOREST_MOSS, STONE], cavity=0.55, shadow=0.45)


# ---------------------------------------------------------------- the forest's edge

def _bare(cv, rng, x, y, ang, length, width, depth, snow, z=0.4):
    """A bare limb and its branches, forking down to twigs; with `snow`, a line of it lies along
    the top of every limb that is not too steep to hold it."""
    pts = [(x, y)]
    for _ in range(4):
        ang += rng.normal(0, 0.14)
        x, y = x + np.cos(ang) * length / 4, y + np.sin(ang) * length / 4
        pts.append((x, y))
    cv.stroke(pts, width, z=z, dome=0.9, taper=(1.0, 0.65), mat=0)
    if snow and width > 1.3:
        flat = abs(np.cos(ang))                                    # how level the limb lies
        if flat > 0.35:
            top = [(px, py - width * 0.42) for px, py in pts]
            cv.stroke(top, max(1.0, width * 0.55 * flat), z=z + 0.6, dome=0.5, taper=(1.0, 0.5), mat=2)
    if depth > 0:
        for side in (-1, 1):
            if rng.random() < 0.9:
                _bare(cv, rng, x, y, ang + side * rng.uniform(0.3, 0.7), length * rng.uniform(0.6, 0.78),
                      width * 0.62, depth - 1, snow, z + 0.05)
    elif width > 0.5:                                              # twigs at the ends
        for _ in range(3):
            a = ang + rng.normal(0, 0.6)
            cv.stroke([(x, y), (x + np.cos(a) * 4, y + np.sin(a) * 4)], 0.6, z=z, dome=0.2, mat=0)


def spr_tree_winter():
    """An oak in winter: the broad, spreading frame of trunk and limbs bare against the sky, forking
    down to a haze of twigs, snow lying along the top of every limb level enough to hold it."""
    rng = np.random.default_rng(29)
    w, h = 136, 128
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    for dx, spread in ((-1, 14), (1, 15)):                                 # the root flare
        cv.polygon([(cx + dx * 4, h - 20), (cx + dx * spread, h), (cx + dx * (spread - 7), h), (cx, h - 8)],
                   z=0.2, top=0.7, bevel=2, mat=0, tone=-0.05)
    cv.stroke([(cx, h), (cx - 2, h - 26), (cx + 1, h - 46)], 12, z=0.4, dome=1.2, taper=(1.25, 0.85), mat=0)
    for ang, length, wd, depth in ((-np.pi / 2 - 0.85, 34, 6.0, 4), (-np.pi / 2 + 0.8, 36, 6.0, 4),
                                   (-np.pi / 2 - 0.15, 30, 5.0, 4), (-np.pi / 2 + 0.35, 26, 4.0, 3),
                                   (-np.pi / 2 - 1.3, 26, 3.6, 3), (-np.pi / 2 + 1.3, 28, 3.6, 3)):
        _bare(cv, rng, cx + rng.normal(0, 1.5), h - 46, ang, length, wd, depth, True)
    cv.ellipse(cx - 3, h - 46, 5, 1.6, z=1.6, dome=0.4, mat=2)              # snow in the crotch
    for _ in range(5):                                                       # furrows up the trunk
        fx = cx + rng.uniform(-4.5, 4.5)
        cv.stroke([(fx, h), (fx + rng.normal(0, 1), h - 24), (fx + rng.normal(0, 1.5), h - 44)], 1.0, dome=0.5,
                  mode='carve')
    return _prop(cv, [WINTER_BARK, WINTER_BARK, ramp('#e8eef4', dark=0.55, light=1.06, cool=0.25)], relief=1.0,
                 cavity=0.4, shadow=0.45)


def spr_birch_winter():
    """A birch in winter: the white trunk banded with black, a second stem off it, and a fine
    purplish haze of drooping twigs, snow on the few level limbs."""
    rng = np.random.default_rng(39)
    w, h = 72, 160
    cv = Canvas(w, h, wrap=False, ground=-9)
    stems = [([(34, h), (33, h - 60), (36, 34), (34, 12)], 5.0), ([(35, h), (41, h - 50), (48, h - 96), (52, 44)], 3.4)]
    for pts, wd in stems:
        cv.stroke(pts, wd, z=0.4, dome=1.0, taper=(1.15, 0.35), mat=1)
    for pts, wd in stems:                                                  # the black marks
        for _ in range(int(wd * 4)):
            t = rng.uniform(0.02, 0.9)
            x, y = _along(pts, t)
            half = wd / 2 * (1.15 - 0.8 * t)
            cv.stroke([(x - half * 0.9, y), (x + half * rng.uniform(0.1, 0.8), y + rng.uniform(-0.3, 0.6))],
                      rng.uniform(0.9, 1.6), z=1.25, dome=0.2, mat=2)
    for _ in range(16):                                                     # branches reaching out and up,
        t = rng.uniform(0.2, 0.92)                                          # fine twigs weeping from them
        pts, wd = stems[int(rng.random() < 0.35)]
        x, y = _along(pts, t)
        side = 1 if rng.random() < 0.5 else -1
        L = rng.uniform(10, 24) * (1.1 - 0.5 * t)
        ex, ey = x + side * L, y - L * rng.uniform(0.25, 0.6)
        cv.stroke([(x, y), ((x + ex) / 2, (y + ey) / 2 - 1), (ex, ey)], 1.1, z=0.7, dome=0.4, taper=(1.0, 0.4), mat=0)
        if rng.random() < 0.5:                                              # snow along it
            cv.stroke([(x + side * 1, y - 1.2), (ex, ey - 1.0)], 0.9, z=1.3, dome=0.4, taper=(1.0, 0.4), mat=3)
        for k in range(5):                                                  # the weeping twigs
            f = (k + 1) / 6
            tx, ty = x + (ex - x) * f, y + (ey - y) * f
            Lt = rng.uniform(5, 11)
            cv.stroke([(tx, ty), (tx + side * 1.5, ty + Lt * 0.5), (tx + side * 1, ty + Lt)], 0.4, z=0.5, dome=0.1,
                      mat=0, tone=rng.normal(0.04, 0.05))
    rgba, em = _prop(cv, [ramp('#6a5660', dark=0.35, light=1.3), BIRCH_BARK, BIRCH_MARK,
                          ramp('#e8eef4', dark=0.55, light=1.06, cool=0.25)], outline=False, relief=1.0, cavity=0.35,
                     shadow=0.4)
    return rgba, em


def spr_bush_snow():
    """A bush under snow: a rounded cushion of it, blue in its hollows, with dark twigs poking out
    of the sides and the top."""
    rng = np.random.default_rng(17)
    w, h = 64, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, y, rx, ry in ((32, 30, 20, 9), (19, 32, 10, 7), (46, 32, 11, 7), (30, 25, 11, 6), (40, 27, 8, 5)):
        cv.ellipse(x, y, rx, ry, z=0.8, dome=1.2, rough=0.22, rng=rng, mat=0, mode='max')
    for _ in range(26):                                                      # twigs poking up through the snow
        a = np.radians(rng.uniform(-160, -20))
        x = 32 + rng.normal(0, 11)
        y = 27 + rng.normal(0, 3)
        L = rng.uniform(7, 15)
        cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], 0.8, z=2.4, dome=0.3, taper=(1, 0.4), mat=1)
    return _prop(cv, [ramp('#e2e9f0', dark=0.55, light=1.06, cool=0.28), WINTER_BARK], relief=1.0, cavity=0.35,
                 shadow=0.45)


def spr_deer():
    """A deer standing alert, side on, facing left: a russet coat, pale belly and throat, slim legs,
    the head up with big ears and a branching rack of antlers, a white flag of a tail."""
    w, h = 64, 60
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x0, x1, tn in ((22, 21, -0.06), (27, 28, 0.0), (42, 41, -0.06), (47, 48, 0.0)):   # legs, far ones darker
        cv.stroke([(x0, 38), (x0 + 0.5, 50), (x1, h - 1)], 1.8, z=0.0 if tn else 0.4, dome=0.5, taper=(1.3, 0.8),
                  mat=0, tone=tn)
    cv.ellipse(35, 34, 15, 7.5, z=0.6, dome=1.1, mat=0)                       # the body
    cv.ellipse(35, 38.5, 11, 3.0, z=1.3, dome=0.5, mat=1)                     # pale belly
    cv.polygon([(49, 30), (54, 28), (53, 33)], z=1.0, top=0.4, bevel=0.8, mat=1)   # the tail, flagged
    cv.stroke([(24, 32), (19, 22), (17, 15)], 5.5, z=1.0, dome=0.9, taper=(1.3, 0.9), mat=0)   # the neck
    cv.stroke([(21, 29), (17, 20)], 2.2, z=1.6, dome=0.4, mat=1)              # the pale throat
    cv.ellipse(15, 14, 4.2, 3.4, z=1.4, dome=1.0, angle=-15, mat=0)          # head
    cv.ellipse(10, 16, 3.0, 2.0, z=1.5, dome=0.8, mat=0, tone=-0.03)         # muzzle
    cv.ellipse(8, 16.5, 1.0, 0.9, z=2.0, dome=0.3, mat=3)                    # nose
    cv.ellipse(14, 13.4, 0.8, 0.8, z=2.0, dome=0.3, mat=3)                   # eye
    cv.leaf(18, 11, 23, 7.5, 2.6, z=1.2, dome=0.6, mat=0, rib=0.3)           # ears
    cv.leaf(17, 11, 15, 6, 2.4, z=1.0, dome=0.6, mat=0, tone=-0.05, rib=0.3)
    for side, sx in ((1, 18), (-1, 15)):                                      # antlers
        base = (sx, 10)
        beam = [base, (sx + side * 3, 4), (sx + side * 1, -1 + 2), (sx + side * 5, 0 + 1)]
        cv.stroke(beam, 1.3, z=2.2 if side > 0 else 1.6, dome=0.5, taper=(1.0, 0.6), mat=2)
        for k, (px, py) in enumerate(((sx + side * 2, 6), (sx + side * 2.5, 3))):
            cv.stroke([(px, py), (px - side * 2.5, py - 3)], 0.9, z=2.2 if side > 0 else 1.6, dome=0.4, mat=2)
    return _prop(cv, [DEER_COAT, DEER_PALE, ANTLER, ramp('#1a1412', dark=0.6, light=1.5)], relief=1.0, cavity=0.35,
                 shadow=0.45)


WINTER_PLAN = {1: {'bush_snow': 8, 'dry_tuft': 4},
               2: {'snowy_pine': 3, 'birch_winter': 2, 'bush_snow': 6},
               3: {'snowy_pine': 6, 'tree_winter': 2, 'birch_winter': 2, 'bush_snow': 5},
               4: {'snowy_pine': 16, 'tree_winter': 3, 'bush_snow': 10}}


AUTUMN_PLAN = {1: {'fern': 5, 'grass_tuft': 5, 'bush_autumn': 7},
               2: {'pine': 1, 'birch_autumn': 3, 'bush_autumn': 7, 'fern': 3},
               3: {'pine': 3, 'tree_autumn': 3, 'birch_autumn': 3, 'bush_autumn': 6},
               4: {'pine': 8, 'tree_autumn': 9, 'birch_autumn': 3, 'bush_autumn': 12}}


def _forest_card(layer, autumn=False, winter=False):
    """One layer of a forest's edge, 1 (front) to 4 (back): ferns, grass and bushes; then young
    trees behind them; then more and taller trees; then a dense wall of spruce and oak. `autumn`:
    a mixed wood in October - oak, birch and bush turned, the spruce among them still green."""
    from assets import get_sprite, variant_pick  # assets imports this module, so not at the top
    rng = np.random.default_rng((800 if winter else 500 if autumn else 400) + layer)
    pick = np.random.default_rng((800 if winter else 500 if autumn else 400) + layer + 70)   # which drawing
    height = {1: 1.2, 2: 3.0, 3: 4.0, 4: 4.8}[layer]
    H = int(height * CARD_PX)
    card = np.zeros((H, CARD_W, 4), np.float32)
    plan = {1: {'fern': 6, 'grass_tuft': 6, 'bush': 6},
            2: {'pine': 2, 'birch': 2, 'bush': 7, 'fern': 4},
            3: {'pine': 5, 'tree': 2, 'birch': 2, 'bush': 6},
            4: {'pine': 17, 'tree': 3, 'bush': 12}}[layer]
    if autumn:
        plan = AUTUMN_PLAN[layer]
    if winter:
        plan = WINTER_PLAN[layer]
    tall = {'pine': (2.2, 4.6), 'tree': (2.4, 3.4), 'birch': (2.4, 3.6), 'bush': (0.4, 0.7), 'fern': (0.35, 0.6),
            'grass_tuft': (0.3, 0.45)}
    tall.update({k + '_autumn': tall[k] for k in ('tree', 'birch', 'bush')})
    tall.update({'snowy_pine': tall['pine'], 'tree_winter': tall['tree'], 'birch_winter': tall['birch'],
                 'bush_snow': (0.35, 0.6), 'dry_tuft': (0.25, 0.4)})
    stamps = []
    for kind, k in plan.items():            # spread evenly along the card, each nudged at random
        lo, hi = tall[kind]
        off = rng.uniform(0, CARD_W)
        for i in range(k):
            x = (off + (i + rng.uniform(0.15, 0.85)) * CARD_W / k) % CARD_W
            stamps.append((x, kind, rng.uniform(lo, min(hi, height - 0.15))))
    for x, kind, tl in sorted(stamps, key=lambda s: -s[2]):          # the tallest first, at the back
        _stamp(card, get_sprite(variant_pick(kind, pick))[0], x, H, tl, flip=bool(rng.random() < 0.5))
    shade = {1: 1.0, 2: 0.92, 3: 0.82, 4: 0.7}[layer]     # deeper into the wood, deeper in shade
    if winter:
        shade = {1: 1.0, 2: 0.95, 3: 0.88, 4: 0.8}[layer]  # snow keeps the light deeper in
    card[..., :3] *= shade
    card[..., 3] = (card[..., 3] > 0.5).astype(np.float32)
    return card, np.zeros(card.shape[:2], np.float32)


TEXTURES = {
    'foliage': lambda n: (tex_foliage(n), None),
    'foliage_autumn': lambda n: (tex_foliage(n, autumn=True), None),
    'forest_deep': lambda n: (tex_forest_deep(n), None),
    'forest_deep_autumn': lambda n: (tex_forest_deep(n, autumn=True), None),
    'forest_deep_snow': lambda n: (tex_forest_deep(n, snow=True), None),
    'leaves_fallen': lambda n: (tex_leaves_fallen(n), None),
    'bark': lambda n: (tex_bark(n), None),
    'bark_pine': lambda n: (tex_bark(n, pine=True), None),
    'pine_needles': lambda n: (tex_needles(n), None),
    'moss': lambda n: (tex_moss(n), None),
}
# how strongly the world-space surface noise varies each texture (see assets.TEXTURE_NOISE)
TEXTURE_NOISE = {'forest_deep': 1.6, 'forest_deep_autumn': 1.6, 'forest_deep_snow': 1.4, 'leaves_fallen': 2.2}
# props drawn a few ways, one picked per placement (assets.variant_name): name -> (count, draw(k))
VARIANTS = {'pine': (4, lambda v: _spruce(v=v)), 'snowy_pine': (4, lambda v: _spruce(snow=True, v=v)),
            'tree': (3, lambda v: _oak(v=v)), 'tree_autumn': (3, lambda v: _oak(autumn=True, v=v)),
            'birch': (3, lambda v: _birch(v=v)), 'birch_autumn': (3, lambda v: _birch(autumn=True, v=v)),
            'mushrooms': (4, _mushrooms), 'bush': (4, lambda v: _bush(v=v)), 'bush_autumn': (4, lambda v: _bush(autumn=True, v=v)),
            'boulder': (4, lambda v: _boulder(v=v)), 'boulder_snow': (4, lambda v: _boulder(snow=True, v=v))}
SPRITES = {'mushrooms': spr_mushrooms, 'pine': spr_pine, 'tree': spr_tree, 'birch': spr_birch, 'bush': spr_bush, 'boulder': spr_boulder,
           'stump': spr_stump, 'log': spr_log, 'dead_tree': spr_dead_tree, 'snowy_pine': spr_snowy_pine,
           'boulder_snow': spr_boulder_snow, 'tree_autumn': spr_tree_autumn, 'birch_autumn': spr_birch_autumn,
           'bush_autumn': spr_bush_autumn, 'tree_winter': spr_tree_winter, 'birch_winter': spr_birch_winter,
           'bush_snow': spr_bush_snow, 'deer': spr_deer}
SPRITES.update({f'forest_card_{k}': (lambda k=k: _forest_card(k)) for k in (1, 2, 3, 4)})
SPRITES.update({f'autumn_card_{k}': (lambda k=k: _forest_card(k, autumn=True)) for k in (1, 2, 3, 4)})
SPRITES.update({f'winter_card_{k}': (lambda k=k: _forest_card(k, winter=True)) for k in (1, 2, 3, 4)})
SPRITE_HEIGHT = {'pine': 3.4, 'tree': 2.6, 'birch': 3.0, 'bush': 0.5, 'snowy_pine': 3.4, 'boulder_snow': 0.55,
                 'forest_card_1': 1.2, 'forest_card_2': 3.0, 'forest_card_3': 4.0, 'forest_card_4': 4.8,
                 'tree_autumn': 2.6, 'birch_autumn': 3.0, 'bush_autumn': 0.5,
                 'autumn_card_1': 1.2, 'autumn_card_2': 3.0, 'autumn_card_3': 4.0, 'autumn_card_4': 4.8,
                 'tree_winter': 2.6, 'birch_winter': 3.0, 'bush_snow': 0.45, 'deer': 0.62,
                 'winter_card_1': 1.2, 'winter_card_2': 3.0, 'winter_card_3': 4.0, 'winter_card_4': 4.8}
# fringe sets: cards back to front, for a wall's `fringe`
FRINGES = {'forest': ['forest_card_4', 'forest_card_3', 'forest_card_2', 'forest_card_1'],
           'forest_autumn': ['autumn_card_4', 'autumn_card_3', 'autumn_card_2', 'autumn_card_1'],
           'forest_snow': ['winter_card_4', 'winter_card_3', 'winter_card_2', 'winter_card_1']}

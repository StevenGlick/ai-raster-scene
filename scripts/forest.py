"""The temperate forest, drawn with the pixel-art toolkit (scripts/pixelart.py): spruce, oak and
birch, bushes, the forest floor, bark and leaves for walls, and the `forest` fringe - long cards
of trees standing in front of a forest's edge, sparse at the front and dense at the back.

Like the jungle (biomes.py), every shape is stamped into a height field, lit from the upper left
and snapped onto hue-shifted ramps, so the trees read as pixel art rather than noise.
"""
import numpy as np

from biomes import CARD_PX, CARD_W, T, _crown, _leaf_layers, _prop, _rng, _stamp, _tile
from pixelart import Canvas, ramp

NEEDLE = ramp('#2e5a3a', dark=0.26, light=1.3, warm=0.08)       # spruce: a dark blue-green
NEEDLE_DRY = ramp('#5e4630', dark=0.35, light=1.15)              # fallen needles, a dull rust brown
OAK_LEAF = ramp('#4e7a30')
OAK_SHADE = ramp('#2e5432', dark=0.3)
BIRCH_LEAF = ramp('#8eaa3e', dark=0.35, light=1.25)
AUTUMN = [ramp('#b8622a'), ramp('#c89a34'), ramp('#8a3a22'), ramp('#3a2a1e', dark=0.4)]
PINE_BARK = ramp('#6e4a34', dark=0.25)
OAK_BARK = ramp('#665a4c', dark=0.25)
BIRCH_BARK = ramp('#e6e2d4', dark=0.45, light=1.06, warm=0.04)
BIRCH_MARK = ramp('#2a2622', dark=0.6, light=1.6)
FOREST_SOIL = ramp('#4a3a2a', dark=0.35)
FOREST_MOSS = ramp('#4e6e2c', dark=0.3)
STONE = ramp('#7a786e', dark=0.35)


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

def spr_pine():
    """A spruce: a straight trunk under tier on tier of drooping boughs. Each tier is a skirt of
    needles with a ragged hem hanging over the tier below; lit from the upper left, so every
    tier has a bright shoulder and a dark underside, and the heart of the tree is in shadow."""
    rng = np.random.default_rng(31)
    w, h = 72, 168
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(cx, h), (cx, 4)], 6, z=0.0, dome=1.0, taper=(1.3, 0.25), mat=1)
    top, foot, n = 3, h - 26, 12
    for i in reversed(range(n)):            # the lowest tier first: each tier hangs over the one below
        t = i / (n - 1)                     # 0 at the tip, 1 at the lowest tier
        hem = top + 8 + (foot - top - 8) * t ** 0.92 + rng.uniform(-1.5, 1.5)
        half = (3.5 + 30 * t ** 0.8) * rng.uniform(0.9, 1.08)
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
    return _prop(cv, [NEEDLE, PINE_BARK], relief=1.0, cavity=0.5, shadow=0.55, reach=6)


def spr_tree():
    """An oak: a short, heavy trunk on a flared foot, limbs spreading into a broad crown of leaf
    clusters in lobes, lit from above, with gaps where the limbs show through."""
    rng = np.random.default_rng(23)
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
    for lx, ly, rx, ry, k in ((cx - 40, 58, 26, 19, 11), (cx + 42, 56, 26, 19, 11), (cx - 22, 34, 29, 23, 13),
                              (cx + 22, 30, 29, 23, 13), (cx, 15, 25, 15, 9), (cx - 3, 52, 28, 18, 10),
                              (cx + 54, 40, 14, 13, 5), (cx - 55, 44, 13, 12, 5)):
        _crown(cv, rng, lx, ly, rx, ry, k, size=(7, 11), leaf=4.0, z=1.0)
    leaves = (cv.mat == 0) & (cv.id > 0)    # lit from above: the top of the crown bright, its underside dark
    cv.tone += np.where(leaves, 0.1 - 0.24 * np.clip(np.arange(h)[:, None] / 80.0, 0, 1), 0).astype(np.float32)
    return _prop(cv, [OAK_LEAF, ramp('#5a4e40', dark=0.25)], relief=1.0, cavity=0.45, shadow=0.55, reach=7)


def spr_birch():
    """A birch: a slender white trunk banded with black, a second stem leaning off it, and an
    airy, drooping crown of small bright leaves with the sky showing through."""
    rng = np.random.default_rng(37)
    w, h = 72, 160
    cv = Canvas(w, h, wrap=False, ground=-9)
    stems = [([(34, h), (33, h - 60), (36, 34), (34, 12)], 5.0), ([(35, h), (41, h - 50), (48, h - 96), (52, 44)], 3.4)]
    for pts, wd in stems:
        cv.stroke(pts, wd, z=0.4, dome=1.0, taper=(1.15, 0.35), mat=1)
    for pts, wd in stems:                   # the black marks across the white bark
        for _ in range(int(wd * 4)):
            t = rng.uniform(0.02, 0.9)
            x, y = _along(pts, t)
            half = wd / 2 * (1.15 - 0.8 * t)
            cv.stroke([(x - half * 0.9, y), (x + half * rng.uniform(0.1, 0.8), y + rng.uniform(-0.3, 0.6))],
                      rng.uniform(0.9, 1.6), z=1.25, dome=0.2, mat=2)
    for x0, y0, x1, y1 in ((34, 70, 18, 52), (34, 58, 50, 40), (35, 44, 22, 26), (48, 92, 60, 74), (36, 30, 46, 16)):
        cv.stroke([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 3), (x1, y1)], 1.4, z=0.7, dome=0.6, taper=(1, 0.4), mat=2)
    for _ in range(30):                     # the crown: clumps of small leaves hanging off drooping twigs
        a = rng.uniform(0, 2 * np.pi)
        r = rng.random() ** 0.7
        x, y = 40 + np.cos(a) * 26 * r, 62 + np.sin(a) * 46 * r
        up = 0.08 if np.sin(a) < 0 else -0.06
        cv.stroke([(x - 2, y - 7), (x, y), (x + 1, y + 5)], 0.8, z=0.8, dome=0.3, mat=2)
        for _ in range(16):
            px, py = x + rng.normal(0, 3.6), y + rng.normal(0, 4.0) + 1.5
            b = np.radians(rng.uniform(55, 125))
            cv.leaf(px, py, px + np.cos(b) * 3.6, py + np.sin(b) * 3.6, 2.4, z=1.2 + (1 - r) * 0.5 + rng.random() * 0.2,
                    dome=0.5, rib=0.0, mat=0, tone=up + rng.normal(0, 0.05))
    return _prop(cv, [BIRCH_LEAF, BIRCH_BARK, BIRCH_MARK], relief=1.0, cavity=0.35, shadow=0.45)


def spr_bush():
    """A rounded shrub: twigs fanning out of the ground under a mound of small leaf clusters,
    bright on top and dark underneath."""
    rng = np.random.default_rng(13)
    w, h = 64, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(6):
        a = np.radians(-150 + k * 24)
        cv.stroke([(32, h), (32 + np.cos(a) * 18, h + np.sin(a) * 18)], 1.6, z=0.2, dome=0.6, taper=(1, 0.5), mat=1)
    _crown(cv, rng, 32, 24, 30, 19, 18, size=(6, 9), leaf=3.6, z=0.8)
    return _prop(cv, [OAK_LEAF, OAK_BARK], relief=1.0, cavity=0.45, shadow=0.5)


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

def _forest_card(layer):
    """One layer of a forest's edge, 1 (front) to 4 (back): ferns, grass and bushes; then young
    trees behind them; then more and taller trees; then a dense wall of spruce and oak."""
    from assets import get_sprite                # assets imports this module, so not at the top
    rng = np.random.default_rng(400 + layer)
    height = {1: 1.2, 2: 3.0, 3: 4.0, 4: 4.8}[layer]
    H = int(height * CARD_PX)
    card = np.zeros((H, CARD_W, 4), np.float32)
    plan = {1: {'fern': 6, 'grass_tuft': 6, 'bush': 6},
            2: {'pine': 2, 'birch': 2, 'bush': 7, 'fern': 4},
            3: {'pine': 5, 'tree': 2, 'birch': 2, 'bush': 6},
            4: {'pine': 17, 'tree': 3, 'bush': 12}}[layer]
    tall = {'pine': (2.2, 4.6), 'tree': (2.4, 3.4), 'birch': (2.4, 3.6), 'bush': (0.4, 0.7), 'fern': (0.35, 0.6),
            'grass_tuft': (0.3, 0.45)}
    stamps = []
    for kind, k in plan.items():            # spread evenly along the card, each nudged at random
        lo, hi = tall[kind]
        off = rng.uniform(0, CARD_W)
        for i in range(k):
            x = (off + (i + rng.uniform(0.15, 0.85)) * CARD_W / k) % CARD_W
            stamps.append((x, kind, rng.uniform(lo, min(hi, height - 0.15))))
    for x, kind, tl in sorted(stamps, key=lambda s: -s[2]):          # the tallest first, at the back
        _stamp(card, get_sprite(kind)[0], x, H, tl, flip=bool(rng.random() < 0.5))
    shade = {1: 1.0, 2: 0.92, 3: 0.82, 4: 0.7}[layer]     # deeper into the wood, deeper in shade
    card[..., :3] *= shade
    card[..., 3] = (card[..., 3] > 0.5).astype(np.float32)
    return card, np.zeros(card.shape[:2], np.float32)


TEXTURES = {
    'foliage': lambda n: (tex_foliage(n), None),
    'foliage_autumn': lambda n: (tex_foliage(n, autumn=True), None),
    'bark': lambda n: (tex_bark(n), None),
    'bark_pine': lambda n: (tex_bark(n, pine=True), None),
    'pine_needles': lambda n: (tex_needles(n), None),
    'moss': lambda n: (tex_moss(n), None),
}
SPRITES = {'pine': spr_pine, 'tree': spr_tree, 'birch': spr_birch, 'bush': spr_bush}
SPRITES.update({f'forest_card_{k}': (lambda k=k: _forest_card(k)) for k in (1, 2, 3, 4)})
SPRITE_HEIGHT = {'pine': 3.4, 'tree': 2.6, 'birch': 3.0, 'bush': 0.5,
                 'forest_card_1': 1.2, 'forest_card_2': 3.0, 'forest_card_3': 4.0, 'forest_card_4': 4.8}
# fringe sets: cards back to front, for a wall's `fringe`
FRINGES = {'forest': ['forest_card_4', 'forest_card_3', 'forest_card_2', 'forest_card_1']}

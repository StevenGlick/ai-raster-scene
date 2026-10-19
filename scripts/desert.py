"""The desert, drawn with the pixel-art toolkit (scripts/pixelart.py): a red-rock canyon - walls of
layered sandstone, the swirled rock of a slot canyon, the dry wash on its floor, the stone rooms
of an old cliff dwelling with their T-shaped doors - and the things that live in it: saguaro and
prickly pear, tumbleweed, a bleached skull, a painted pot.

As in the other toolkit modules, every shape is stamped into a height field, lit from the upper
left and snapped onto hue-shifted ramps; every texture tiles.
"""
import numpy as np

from biomes import T, _blocks, _prop, _rng, _tile
from dream import _lathe
from pixelart import Canvas, ramp, smooth_noise

RED_ROCK = ramp('#a8482c', dark=0.32, light=1.25, warm=0.14)
ORANGE_ROCK = ramp('#c4743e', dark=0.32, light=1.22, warm=0.12)
CREAM_ROCK = ramp('#d8b88a', dark=0.36, light=1.14)
BROWN_ROCK = ramp('#7a3e2a', dark=0.3, light=1.3)
PURPLE_ROCK = ramp('#7a4448', dark=0.3, light=1.3)
SAND = ramp('#d0a878', dark=0.36, light=1.16)
PEBBLES = [ramp('#8a6a52', dark=0.35), ramp('#b08a68', dark=0.35), ramp('#6e5a4e', dark=0.35)]
MUD = ramp('#9a7a5a', dark=0.35)
CACTUS = ramp('#4e7a46', dark=0.3, light=1.28, cool=0.2)
SPINE = ramp('#e6dcb8', dark=0.6, light=1.05)
BLOOM = ramp('#f0ecd8', dark=0.6, light=1.05)
FRUIT = ramp('#a03050', dark=0.35, light=1.25)
DRY = ramp('#a8865a', dark=0.4, light=1.18)
BONE = ramp('#e8e0cc', dark=0.45, light=1.06)
POT_WHITE = ramp('#e4dccb', dark=0.5, light=1.05)
POT_BLACK = ramp('#2a2622', dark=0.6, light=1.6)


# ---------------------------------------------------------------- textures

def _strata(cv, rng, mats, wave=None):
    """Fill a tiling canvas with beds of rock, top to bottom: each bed its own material and
    thickness, the hard ones standing out as ledges (their tops proud, their faces sloping back
    under them), the soft ones recessed. `wave` (amplitude, cycles) bends the beds into the swirls
    of a slot canyon."""
    y, k = 0, 0
    bounds = []
    while y < cv.h:
        hgt = int(rng.integers(4, 13))
        bounds.append((y, min(cv.h, y + hgt), int(rng.choice(mats)), rng.random() < 0.4, rng.normal(0, 0.05)))
        y += hgt
    xs = np.arange(cv.w)
    if wave:
        amp, cycles = wave
        ph = rng.uniform(0, 2 * np.pi)
        shift = amp * np.sin(2 * np.pi * cycles * xs / cv.w + ph) + amp * 0.4 * np.sin(2 * np.pi * (cycles + 1) * xs / cv.w)
    else:
        shift = np.zeros(cv.w)
    yy = (np.arange(cv.h)[:, None] - shift[None, :]) % cv.h
    for k, (y0, y1, m, hard, tone) in enumerate(bounds):
        inside = (yy >= y0) & (yy < y1)
        t = (yy - y0) / max(1.0, y1 - y0 - 1.0)
        prof = np.where(hard, 0.9 - 0.7 * t, 0.25 + 0.15 * np.sin(np.pi * t))
        cv.z = np.where(inside, prof, cv.z).astype(np.float32)
        cv.mat = np.where(inside, m, cv.mat).astype(np.int32)
        cv.tone = np.where(inside, tone, cv.tone).astype(np.float32)
        cv.id = np.where(inside, k + 1, cv.id).astype(np.int32)
    cv.n = len(bounds)
    return bounds


def tex_sandstone(name, pale=False):
    """A canyon wall of layered sandstone: beds of red, orange and cream, the hard ones standing
    out as ledges over the soft ones, cross-bedding scored through the thicker beds, a few joints
    cracking down through them, and desert varnish streaking dark down from the ledges. `pale`:
    the cream cap rock near the rim."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    mats = [2, 2, 2, 1, 0] if pale else [0, 0, 1, 1, 2, 3]
    bounds = _strata(cv, rng, mats, wave=(1.3, 1))
    cv.noise(0.3, cells=8, rng=rng, octaves=3)
    cv.tone += (0.16 * (smooth_noise(T, T, 5, rng, cells_y=12) - 0.5)).astype(np.float32)    # each bed mottled along
    for y0, y1, m, hard, _ in bounds:                     # cross-bedding: fine slanting lines in a thick bed
        if y1 - y0 >= 8 and not hard:
            for _ in range(4):
                x = rng.random() * T
                cv.stroke([(x, y0 + 1), (x + rng.uniform(5, 10), y1 - 1)], 0.6, dome=0.2, mode='carve')
    for _ in range(3):                                     # joints
        x, y = rng.random() * T, rng.random() * T
        L = rng.uniform(12, 30)
        cv.stroke([(x, y), (x + rng.normal(0, 1.2), y + L / 2), (x + rng.normal(0, 1.5), y + L)], 0.9, dome=0.5,
                  mode='carve')
    for y0, y1, m, hard, _ in bounds:                     # desert varnish: dark streaks hanging under the ledges
        if not hard:
            continue
        for _ in range(int(rng.integers(1, 4))):
            x, L, wd = rng.random() * T, rng.uniform(5, 18), rng.uniform(1.5, 3.5)
            ys = np.arange(int(y1), int(y1 + L)) % T
            xs = np.arange(int(x - wd), int(x + wd) + 1) % T
            fade = np.linspace(0.32, 0.04, len(ys))[:, None] * (1 - np.abs(np.arange(len(xs)) - wd) / (wd + 1))[None, :]
            cv.tone[np.ix_(ys, xs)] -= fade.astype(np.float32)
    return _tile(cv, [RED_ROCK, ORANGE_ROCK, CREAM_ROCK, BROWN_ROCK], cavity=0.45, shadow=0.5)


def tex_slot_rock(name):
    """The wall of a slot canyon: sandstone carved smooth by floods, its beds swept into flowing
    curves of orange, red and violet, polished so the light slides along them."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    _strata(cv, rng, [0, 0, 1, 1, 2, 3], wave=(7.0, 1))
    cv.noise(0.12, cells=6, rng=rng, octaves=2)
    cv.z *= 0.6
    return _tile(cv, [ORANGE_ROCK, RED_ROCK, CREAM_ROCK, PURPLE_ROCK], dither=0.4, cavity=0.3, shadow=0.35)


def tex_desert_wash(name):
    """The floor of a dry wash: pale sand rippled by the wind, a scatter of pebbles washed down
    from the walls, and here and there a patch of dried mud crazed into plates."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    xs = np.arange(T)[None, :]
    ys = np.arange(T)[:, None]
    ripple = np.sin(2 * np.pi * (2 * xs + ys) / T + 4.0 * smooth_noise(T, T, 3, rng))
    cv.z += (0.1 * ripple).astype(np.float32)
    cv.noise(0.2, cells=10, rng=rng)
    mud = smooth_noise(T, T, 3, rng) > 0.68                # crazed mud
    cv.mat[mud] = 4
    cv.tone[mud] += 0.04
    for _ in range(12):
        x, y = rng.random() * T, rng.random() * T
        if mud[int(y) % T, int(x) % T]:
            a = rng.uniform(0, np.pi)
            cv.stroke([(x, y), (x + np.cos(a) * 5, y + np.sin(a) * 5)], 0.7, dome=0.4, mode='carve')
    for _ in range(40):                                    # pebbles
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.7, 1.8), rng.uniform(0.6, 1.4), z=0.3,
                   dome=0.8, rough=0.2, rng=rng, mat=int(rng.integers(1, 4)), tone=rng.normal(0, 0.06))
    return _tile(cv, [SAND] + PEBBLES + [MUD], dither=0.25, cavity=0.4, shadow=0.4)


def tex_pueblo_stone(name):
    """The wall of a cliff dwelling: thin slabs of sandstone laid in courses, chinked with small
    stones, in a thick mud mortar the colour of the canyon."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.5, mat=1)
    rows = [0]
    while rows[-1] < T:
        rows.append(min(T, rows[-1] + int(rng.integers(5, 9))))
    _blocks(cv, rng, rows, (9, 22), rough=0.9, chip=2, bevel=1.6, gap=0.9, tone=0.06)
    for _ in range(18):                                    # chinking stones in the joints
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.8, 1.5), rng.uniform(0.6, 1.0), z=0.2,
                   dome=0.6, mat=0, tone=rng.normal(-0.04, 0.05), mode='max')
    cv.noise(0.12, cells=10, rng=rng)
    return _tile(cv, [ORANGE_ROCK, MUD], cavity=0.5, shadow=0.45)


def tex_pueblo_door(name):
    """A doorway in a cliff dwelling's wall: the T-shaped opening of the old builders, dark inside,
    framed in the same coursed stone, with a lintel of a few poles over its head."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.5, mat=1)
    rows = [0]
    while rows[-1] < T:
        rows.append(min(T, rows[-1] + int(rng.integers(5, 9))))
    _blocks(cv, rng, rows, (9, 22), rough=0.9, chip=2, bevel=1.6, gap=0.9, tone=0.06)
    cv.noise(0.12, cells=10, rng=rng)
    hole = np.zeros((T, T), bool)
    hole[20:56, 24:40] = True                              # the narrow lower part
    hole[12:30, 18:46] = True                              # the wide upper part: the T
    cv.z[hole] = -2.0
    cv.mat[hole] = 2
    cv.id[hole] = 0
    for k in range(4):                                     # poles over the head
        cv.stroke([(16, 10.5 - k * 0.1), (48, 10.5 + k * 0.1)], 1.3, z=0.6, dome=0.7, mat=3, tone=-0.05 * k)
    return _tile(cv, [ORANGE_ROCK, MUD, ramp('#1a1210', dark=0.7, light=1.4), ramp('#8a6a4a', dark=0.3)],
                 cavity=0.5, shadow=0.5)


# ---------------------------------------------------------------- props

def _ribbed(cv, pts, width, z, tone=0.0):
    """A cactus stem along pts: a rounded column with ribs running its length and spines along
    the ribs."""
    cv.stroke(pts, width, z=z, dome=1.4, taper=(1.0, 0.92), mat=0, tone=tone)
    pts = np.asarray(pts, np.float32)
    for f in (-0.32, 0.0, 0.32):
        off = []
        for i, (x, y) in enumerate(pts):
            j = min(i + 1, len(pts) - 1)
            k = max(i - 1, 0)
            dx, dy = pts[j] - pts[k]
            n = np.hypot(dx, dy) or 1.0
            off.append((x - dy / n * f * width, y + dx / n * f * width))
        cv.stroke(off, 0.6, dome=0.3, mode='carve')


def spr_saguaro():
    """A saguaro: a ribbed green column, two arms bending out and up, a rounded crown with a few
    white blossoms on it, spines catching the light along the ribs."""
    rng = np.random.default_rng(171)
    w, h = 64, 150
    cx = 32
    cv = Canvas(w, h, wrap=False, ground=-9)
    _ribbed(cv, [(cx - 18, 82), (cx - 18, 60), (cx - 17, 36)], 9, z=0.3, tone=-0.02)        # the left arm
    _ribbed(cv, [(cx - 6, 92), (cx - 15, 92), (cx - 18, 84)], 9, z=0.3, tone=-0.02)
    _ribbed(cv, [(cx + 18, 70), (cx + 19, 50), (cx + 18, 44)], 8, z=0.3)                    # the right arm
    _ribbed(cv, [(cx + 6, 78), (cx + 14, 78), (cx + 18, 72)], 8, z=0.3)
    _ribbed(cv, [(cx, h), (cx, 60), (cx, 12)], 15, z=0.6)                                    # the trunk
    cv.ellipse(cx, 13, 7.0, 6.0, z=1.6, dome=1.0, mat=0)
    for _ in range(70):                                                                       # spines
        x, y = cx + rng.uniform(-7, 7), rng.uniform(12, h - 4)
        cv.ellipse(x, y, 0.5, 0.5, z=2.4, dome=0.2, mat=1)
    for x, y in ((cx - 3, 8), (cx + 2, 7), (cx + 5, 10)):                                     # blossoms
        cv.ellipse(x, y, 1.8, 1.5, z=2.8, dome=0.6, mat=2)
    return _prop(cv, [CACTUS, SPINE, BLOOM], relief=1.0, cavity=0.4, shadow=0.45)


def spr_prickly_pear():
    """A prickly pear: flat oval pads growing out of one another, dotted with spines, a few
    ripe magenta fruits along the top edges."""
    rng = np.random.default_rng(173)
    w, h = 56, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    pads = [(28, 34, 9, 10, 0), (17, 26, 8, 9.5, -25), (39, 26, 8, 9, 22), (24, 15, 7, 8.5, -10),
            (35, 13, 6.5, 8, 18), (12, 14, 6, 7.5, -38)]
    for i, (x, y, rx, ry, a) in enumerate(pads):
        cv.ellipse(x, y, rx, ry, z=0.2 + i * 0.25, dome=0.7, angle=a, mat=0, tone=rng.normal(0, 0.04))
        for _ in range(9):
            t = rng.uniform(0, 2 * np.pi)
            r = rng.uniform(0.2, 0.8)
            cv.ellipse(x + np.cos(t) * rx * r, y + np.sin(t) * ry * r, 0.5, 0.5, z=0.9 + i * 0.25, dome=0.2, mat=1)
    for x, y in ((24, 6.5), (27.5, 6.0), (33, 4.6), (12, 6.4), (40, 17.5)):
        cv.ellipse(x, y, 1.8, 2.2, z=2.6, dome=0.8, mat=2)
    return _prop(cv, [CACTUS, SPINE, FRUIT], relief=1.0, cavity=0.4, shadow=0.45)


def spr_tumbleweed():
    """A tumbleweed: a loose ball of dry, wiry stems, tangled every way, the light coming through."""
    rng = np.random.default_rng(175)
    w, h = 40, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(46):
        a = rng.uniform(0, 2 * np.pi)
        r0 = rng.uniform(2, 14)
        pts = [(20 + np.cos(a) * r0, 18 + np.sin(a) * r0 * 0.85)]
        for _ in range(3):
            a += rng.normal(0, 0.9)
            x, y = pts[-1]
            nx, ny = x + np.cos(a) * 5, y + np.sin(a) * 5
            if (nx - 20) ** 2 + ((ny - 18) / 0.85) ** 2 > 16 ** 2:
                break
            pts.append((nx, ny))
        if len(pts) > 1:
            cv.stroke(pts, 0.8, z=rng.uniform(0, 1.5), dome=0.3, mat=0, tone=rng.normal(0, 0.06))
    return _prop(cv, [DRY], relief=1.0, cavity=0.3, shadow=0.35)


def spr_cow_skull():
    """A cow's skull bleached by the sun: the long face, dark sockets and nose holes, horns
    curving out and up."""
    w, h = 44, 26
    cv = Canvas(w, h, wrap=False, ground=-9)
    for side in (-1, 1):                                                       # the horns
        t = np.linspace(0, 1, 12)
        cv.stroke(list(zip(22 + side * (6 + 15 * t), 9 - 7 * t ** 2 + 2 * t)), 2.6, z=0.4, dome=0.8, taper=(1.2, 0.3),
                  mat=0, tone=0.02)
    cv.polygon([(14, 8), (30, 8), (28, 18), (25, 25), (19, 25), (16, 18)], z=0.8, top=1.2, bevel=3, mat=0)
    for side in (-1, 1):
        cv.ellipse(22 + side * 4.6, 12.5, 2.2, 2.0, z=0.2, dome=0.0, mat=1)    # sockets
        cv.ellipse(22 + side * 1.4, 22.5, 0.9, 1.3, z=0.4, dome=0.0, mat=1)    # nose
    cv.stroke([(22, 9), (22, 18)], 0.6, dome=0.3, mode='carve')
    return _prop(cv, [BONE, ramp('#2a2420', dark=0.6, light=1.5)], relief=1.0, cavity=0.4, shadow=0.45)


def spr_clay_pot():
    """A pot of the old canyon people: a round white body painted in black with stepped bands and
    zigzags, a short neck."""
    w, h = 28, 30
    cx = 14
    cv = Canvas(w, h, wrap=False, ground=-9)
    _lathe(cv, cx, [(4, 6.5), (7, 6.0), (12, 11.5), (20, 12.5), (27, 9.0), (29, 6.0)], z=0.0, dome=1.3, mat=0)
    _lathe(cv, cx, [(3, 7.0), (5, 7.0)], z=0.6, dome=1.0, mat=0, tone=0.04)
    for y in (9, 22):
        cv.stroke([(cx - 12, y), (cx + 12, y)], 1.2, z=1.6, dome=0.1, mat=1)
    for k in range(7):                                                         # a zigzag band
        x0 = cx - 11 + k * 3.3
        cv.stroke([(x0, 18.5), (x0 + 1.65, 12.5), (x0 + 3.3, 18.5)], 0.9, z=1.6, dome=0.1, mat=1)
    paint = (cv.mat == 1)
    inside = np.abs(np.arange(w)[None, :] + 0.5 - cx) < np.interp(np.arange(h), [4, 7, 12, 20, 27, 29],
                                                                  [6.5, 6.0, 11.5, 12.5, 9.0, 6.0])[:, None] - 0.5
    cv.id[paint & ~inside] = 0
    return _prop(cv, [POT_WHITE, POT_BLACK], relief=1.0, cavity=0.35, shadow=0.45)


TEXTURES = {
    'sandstone': lambda n: (tex_sandstone(n), None),
    'sandstone_pale': lambda n: (tex_sandstone(n, pale=True), None),
    'slot_rock': lambda n: (tex_slot_rock(n), None),
    'desert_wash': lambda n: (tex_desert_wash(n), None),
    'pueblo_stone': lambda n: (tex_pueblo_stone(n), None),
    'pueblo_door': lambda n: (tex_pueblo_door(n), None),
}
TEXTURE_NOISE = {'sandstone': 1.4, 'sandstone_pale': 1.4, 'slot_rock': 0.6, 'desert_wash': 1.6, 'pueblo_stone': 1.2,
                 'pueblo_door': 0.8}
SPRITES = {'saguaro': spr_saguaro, 'prickly_pear': spr_prickly_pear, 'tumbleweed': spr_tumbleweed,
           'cow_skull': spr_cow_skull, 'clay_pot': spr_clay_pot}
SPRITE_HEIGHT = {'saguaro': 3.2, 'prickly_pear': 0.6, 'tumbleweed': 0.45, 'cow_skull': 0.2, 'clay_pot': 0.34}
DEBRIS_SETS = {'desert': ['rocks', 'rocks', 'rocks', 'prickly_pear', 'tumbleweed', 'cow_skull', 'dry_tuft']}

"""Everyday materials and props redrawn with the pixel-art toolkit (scripts/pixelart.py): grass,
a clipped hedge, dirt, gravel, wood panelling, water, slates, cobbles, ceiling beams, raw rock (dry,
wet, a floor of it, under snow), ice, sand, plaster and ivy on brick, velvet curtains, acoustic
ceiling tiles, corrugated iron, dark marble, and the rock and dust of an alien world; a barrel,
a broken one, a crate, a fountain, a rowboat, a bench, flowers, a statue, an iron bed, a
wheelchair, a table, a chest, glowing mushrooms, a buoy and an alien egg. These are the oldest
things in the set - the first versions were noise and flat shapes - and they turn up in a great
many scenes.

As in the other toolkit modules, shapes are stamped into a height field, lit from the upper left
and snapped onto hue-shifted ramps; every texture tiles without a seam.
"""
import numpy as np

from biomes import T, _blocks, _leaf_layers, _prop, _rng, _tile
from dream import _lathe
from forest import _plates
from pixelart import Canvas, ramp, smooth_noise

GRASS = [ramp('#3e6a2a', dark=0.3), ramp('#5a8a32'), ramp('#9aa848', dark=0.45, light=1.2)]
HEDGE = [ramp('#2e5a2a', dark=0.3), ramp('#3e6e30'), ramp('#24482a', dark=0.3)]
SOIL = ramp('#5a4632', dark=0.35)
CLOD = ramp('#6e563c', dark=0.35)
PEBBLE = [ramp('#8a8478', dark=0.35), ramp('#9a8a70', dark=0.35), ramp('#6e6a64', dark=0.35)]
WOOD = ramp('#6a4428', dark=0.3)
WOOD_DARK = ramp('#4a2e1a', dark=0.3)
PANEL = ramp('#553620', dark=0.3)
WATER = ramp('#163a44', dark=0.35, light=1.45, warm=0.02, cool=0.12)
IRON = ramp('#4a4a4e', dark=0.4, light=1.6)
STONE_F = ramp('#a8a294', dark=0.4, light=1.2)
SLATE = [ramp('#4a4e58', dark=0.35, light=1.35, cool=0.2), ramp('#5a5a62', dark=0.35, light=1.3),
         ramp('#3e4450', dark=0.35, light=1.4)]
SETT = [ramp('#7a766c', dark=0.35, light=1.25), ramp('#8a7e6c', dark=0.35, light=1.22),
        ramp('#62646a', dark=0.35, light=1.3)]
JOINT = ramp('#2e2a26', dark=0.5, light=1.5)
MOSS_J = ramp('#4e6230', dark=0.35)
BEAM = ramp('#5a3e28', dark=0.3, light=1.3)
LIME = ramp('#d6cdb4', dark=0.45, light=1.1)
HULL_PAINT = ramp('#4e7a78', dark=0.35, light=1.25)
OAR = ramp('#a8865a', dark=0.35, light=1.2)
CAST_IRON = ramp('#2e3034', dark=0.5, light=1.9)
SLAT = ramp('#8a5e3a', dark=0.32)
FLOWER = [ramp('#c8303a', dark=0.4, light=1.25), ramp('#e8c040', dark=0.4, light=1.15),
          ramp('#e8e0d8', dark=0.5, light=1.05), ramp('#d070a0', dark=0.4, light=1.2)]
STEMS = ramp('#3e6a2e', dark=0.3)
MARBLE_W = ramp('#c8c2b4', dark=0.4, light=1.15)
LICHEN_S = ramp('#8a8a5a', dark=0.4)
BED_IRON = ramp('#6a7076', dark=0.4, light=1.5, cool=0.1)
SHEET = ramp('#e2ded2', dark=0.5, light=1.06)
BLANKET = ramp('#7a8070', dark=0.35, light=1.25)
CHROME = ramp('#9aa0a6', dark=0.35, light=1.45, cool=0.1)
LEATHER = ramp('#4a3a30', dark=0.35, light=1.4)
TYRE = ramp('#2a2a2c', dark=0.6, light=1.8)
TABLE_WOOD = ramp('#6a4a2c', dark=0.3, light=1.3)
CHEST_WOOD = ramp('#7a5030', dark=0.3, light=1.3)
BRASS = ramp('#c8a040', dark=0.4, light=1.2)
SHROOM = ramp('#3ad8b8', dark=0.45, light=1.25, cool=0.15)
SHROOM_STEM = ramp('#c8d8c0', dark=0.45, light=1.1)
BUOY_RED = ramp('#b03a2e', dark=0.32, light=1.3)
BUOY_WHITE = ramp('#dedad0', dark=0.5, light=1.06)
LAMP = ramp('#ffd060', dark=0.7, light=1.1)
EGG = ramp('#6a5640', dark=0.32, light=1.5)
EGG_VEIN = ramp('#6a9a3a', dark=0.45, light=1.3)
EGG_GLOW = ramp('#a8ff6a', dark=0.7, light=1.1)


# ---------------------------------------------------------------- textures

def tex_grass(name):
    """A lawn seen from standing height: blades in clumps, dark at the roots and bright at the tips,
    a few yellow-green tufts, the odd daisy."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.4, mat=0)
    dense = smooth_noise(T, T, 4, rng)
    for i in range(900):
        x, y = rng.random() * T, rng.random() * T
        if rng.random() > 0.35 + 0.65 * dense[int(y) % T, int(x) % T]:
            continue
        a = np.radians(rng.uniform(-115, -65))                # mostly upright, leaning a little
        L = rng.uniform(2.5, 5.0)
        tip = 2 if rng.random() < 0.18 else 1
        cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], 1.1, z=0.1 + i * 0.0006, dome=0.5,
                  taper=(1.0, 0.4), mat=tip if rng.random() < 0.6 else 0, tone=rng.normal(0, 0.05))
    rgb = _tile(cv, GRASS, cavity=0.45, shadow=0.4, ambient=0.26, diffuse=0.62)
    for _ in range(4):                                        # daisies
        x, y = int(rng.random() * T), int(rng.random() * T)
        rgb[y % T, x % T] = (0.95, 0.95, 0.9)
        rgb[(y + 1) % T, x % T] = (0.92, 0.82, 0.3)
    return rgb


def tex_hedge(name):
    """A clipped hedge: small leaves packed tight in three depths, the face kept nearly flat by the
    shears, darker hollows where it has grown thin."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.0, mat=2)
    _leaf_layers(cv, rng, [(-0.4, 150, -0.18, (3, 5)), (0.2, 110, -0.06, (3, 5)), (0.7, 70, 0.04, (3, 5.5))],
                 [0, 0, 1, 1], angles=(0, 360), aspect=(0.5, 0.7), bend=0.1)
    thin = smooth_noise(T, T, 3, rng)
    cv.tone -= np.where(thin < 0.3, 0.12, 0.0).astype(np.float32)
    return _tile(cv, HEDGE, cavity=0.5, shadow=0.5)


def tex_dirt(name):
    """Bare earth: soil broken into clods, a scatter of pebbles, darker damp patches and the odd
    root or twig."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.35, cells=6, rng=rng, octaves=3)
    for _ in range(46):                                       # clods
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(1.5, 4), rng.uniform(1.2, 3), z=0.1, dome=0.6,
                   rough=0.4, rng=rng, mat=1, tone=rng.normal(0, 0.06))
    for _ in range(26):                                       # pebbles
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(0.8, 1.8), rng.uniform(0.7, 1.4), z=0.4, dome=0.9,
                   rough=0.2, rng=rng, mat=2, tone=rng.normal(0, 0.08))
    for _ in range(2):                                        # a root
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, np.pi)
        cv.stroke([(x, y), (x + np.cos(a) * 8, y + np.sin(a) * 8 + 2), (x + np.cos(a) * 15, y + np.sin(a) * 15)],
                  1.2, z=0.3, dome=0.5, mat=3)
    damp = smooth_noise(T, T, 3, rng)
    cv.tone -= (np.clip(damp - 0.55, 0, 1) * 0.5).astype(np.float32)
    return _tile(cv, [SOIL, CLOD, PEBBLE[0], WOOD_DARK], cavity=0.45, shadow=0.4)


def tex_gravel(name):
    """Gravel: rounded pebbles packed together, each lit on top with a shadow under it, in a few
    stone colours."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.6, mat=2)
    for i in range(260):
        cv.ellipse(rng.random() * T, rng.random() * T, rng.uniform(1.4, 3.0), rng.uniform(1.1, 2.4),
                   z=rng.uniform(0, 0.3), dome=1.0, angle=rng.uniform(0, 180), rough=0.15, rng=rng,
                   mat=int(rng.integers(0, 3)), tone=rng.normal(0, 0.06), mode='max')
    return _tile(cv, PEBBLE, cavity=0.5, shadow=0.45)


def tex_wood_panel(name):
    """Wood panelling: stiles and rails framing two raised, bevelled panels per unit, all of one
    wood, so the panels show by the light on their bevels; a groove round each panel, the grain
    running up the stiles and panels and along the rails."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    for x in (0, 32):
        cv.box(x + 5, 6, 22, 52, z=-0.1, top=1.8, bevel=4.0, mat=0, tone=0.03 + rng.normal(0, 0.02))
        cv.stroke([(x + 4.6, 5.6), (x + 27.4, 5.6), (x + 27.4, 58.4), (x + 4.6, 58.4), (x + 4.6, 5.6)], 0.8,
                  dome=0.35, mode='carve')
    for _ in range(46):                                        # grain up the stiles and panels
        x, y = rng.random() * T, rng.uniform(6, 50)
        cv.stroke([(x, y), (x + rng.normal(0, 0.3), y + rng.uniform(6, 16))], 0.55, dome=0.18, mode='carve')
    for y0 in (1, 59):                                         # and along the rails
        for _ in range(5):
            x, y = rng.random() * T, y0 + rng.uniform(0.5, 3.5)
            cv.stroke([(x, y), (x + rng.uniform(8, 18), y + rng.normal(0, 0.2))], 0.55, dome=0.18, mode='carve')
    cv.stroke([(0, 0.5), (T, 0.5)], 0.9, dome=0.35, mode='carve')   # the joint with the course above
    rail = (np.arange(T)[:, None] < 6) | (np.arange(T)[:, None] > 58)   # figure in the wood: streaks with the grain
    streak = np.where(rail, smooth_noise(T, T, 2, rng, cells_y=16), smooth_noise(T, T, 16, rng, cells_y=2))
    cv.tone += (0.3 * (streak - 0.5)).astype(np.float32)
    return _tile(cv, [PANEL], dither=0.25, relief=1.6, cavity=0.4, shadow=0.35, ambient=0.25, diffuse=0.6)


def tex_water(name):
    """Still water: a deep teal in slow swells of lighter and darker, and a broken net of light
    where the ripples gather it - the cells of a Voronoi pattern, brightest along their edges,
    fading in and out."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    swell = smooth_noise(T, T, 3, rng) * 0.7 + smooth_noise(T, T, 7, rng) * 0.3
    cv.tone += (0.32 * (swell - 0.5)).astype(np.float32)
    n = 12                                                     # the caustic net
    sx, sy = rng.random(n) * T, rng.random(n) * T
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    dx = np.abs(xx[..., None] - sx)
    dy = np.abs(yy[..., None] - sy)
    d = np.sort(np.hypot(np.minimum(dx, T - dx), np.minimum(dy, T - dy)), axis=-1)
    edge = d[..., 1] - d[..., 0]
    fade = np.clip(smooth_noise(T, T, 4, rng) * 1.8 - 0.4, 0, 1)
    cv.tone += (0.2 * np.exp(-edge / 1.8) * fade).astype(np.float32)
    return _tile(cv, [WATER], dither=0.4, cavity=0.0, shadow=0.0, ambient=0.12, diffuse=0.45)


def tex_shingle(name):
    """A roof of slates seen from above: courses of staggered tabs, each tipped up toward its foot
    where it laps over the course below, so every course throws a shadow along the next; the odd
    tab a shade off, a chipped corner, a little moss in the joints."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.4, mat=3)
    for r in range(8):
        y0 = r * 8
        for c in range(8):
            x0 = c * 8 + (r % 2) * 4 + rng.uniform(-0.4, 0.4)
            ys, xs = np.arange(y0, y0 + 8), np.arange(int(x0), int(x0) + 8)
            X, Y = np.meshgrid(xs + 0.5 - x0, ys + 0.5 - y0)
            mask = (X > 0.6) & (X < 7.5) & (Y < 7.6)
            if rng.random() < 0.25:                                  # a chipped corner
                cx_, cy_ = (1.0 if rng.random() < 0.5 else 7.0), 7.0
                mask &= (X - cx_) ** 2 + (Y - cy_) ** 2 > 2.2
            cv.put(ys, xs, mask, 0.2 + 0.85 * (Y / 8.0), mat=int(rng.choice([0, 0, 0, 1, 2])),
                   tone=rng.normal(0, 0.05))
    cv.noise(0.08, cells=12, rng=rng)
    moss = (cv.mat == 3) & (smooth_noise(T, T, 5, rng) > 0.62)
    cv.mat[moss] = 4
    return _tile(cv, SLATE + [JOINT, MOSS_J], cavity=0.45, shadow=0.55, ambient=0.26, diffuse=0.6)


def tex_cobble(name):
    """Cobbles: rounded stones of grey and brown set close in a mosaic of every size, dark grit and
    a little moss in the joints - enough stones in a tile that its repeat does not show."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.8, mat=3)
    _plates(cv, rng, rows=6, cols=6, fissure=1.5, bevel=2.4)
    own = rng.integers(0, 3, cv.n + 1)
    stones = cv.id > 0
    cv.mat[stones] = own[cv.id[stones]]
    cv.noise(0.12, cells=10, rng=rng)
    moss = ~stones & (smooth_noise(T, T, 4, rng) > 0.6)
    cv.mat[moss] = 4
    return _tile(cv, SETT + [JOINT, MOSS_J], cavity=0.5, shadow=0.5, ambient=0.26, diffuse=0.62)


def tex_beams(name):
    """A beamed ceiling seen from below: two heavy oak beams to a unit standing proud of the
    limewashed plaster between them, so each has a lit edge and a shadowed one and throws a soft
    shadow onto the plaster; grain, a check or two along the beams."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=1)
    cv.noise(0.2, cells=6, rng=rng)
    for y0 in (2, 34):
        ys = np.arange(y0, y0 + 15)                                  # the beam, bevelled along its edges only
        edge = np.minimum(ys + 0.5 - y0, y0 + 15 - ys - 0.5)
        cv.z[y0:y0 + 15] = (0.3 + 1.6 * np.clip(edge / 2.5, 0, 1) ** 0.6)[:, None].astype(np.float32)
        cv.mat[y0:y0 + 15] = 0
        cv.id[y0:y0 + 15] = y0 + 1
        cv.tone[y0:y0 + 15] = rng.normal(0, 0.03)
        for _ in range(9):                                           # grain along the beam
            x, y = rng.random() * T, y0 + rng.uniform(2.5, 12.5)
            cv.stroke([(x, y), (x + rng.uniform(8, 20), y + rng.normal(0, 0.3))], 0.55, dome=0.2, mode='carve')
        x = rng.random() * T                                         # a check (a long crack)
        cv.stroke([(x, y0 + 7), (x + rng.uniform(14, 24), y0 + 7.5)], 0.9, dome=0.5, mode='carve')
        cv.tone[y0:y0 + 2] += 0.12                                   # the lit edge
        cv.tone[y0 + 11:y0 + 15] -= np.linspace(0.12, 0.28, 4)[:, None].astype(np.float32)   # the side in shadow
        cv.tone[y0 + 15:y0 + 21] -= np.linspace(0.22, 0.02, 6)[:, None].astype(np.float32)   # its shadow on the plaster
    return _tile(cv, [BEAM, LIME], cavity=0.45, shadow=0.55, ambient=0.26, diffuse=0.6)


# ---------------------------------------------------------------- rock, ice, sand, plaster, ivy

ROCK = {'rock': [ramp('#6a645a', dark=0.32, light=1.3), ramp('#5e5a54', dark=0.32, light=1.32),
                 ramp('#74695a', dark=0.32, light=1.28)],
        'rock_wet': [ramp('#46504e', dark=0.3, light=1.6, cool=0.2), ramp('#3e4648', dark=0.3, light=1.65, cool=0.2),
                     ramp('#4a4e4a', dark=0.3, light=1.6)],
        'rock_floor': [ramp('#5e564c', dark=0.32, light=1.3), ramp('#544e48', dark=0.32, light=1.32),
                       ramp('#665a4a', dark=0.32, light=1.28)]}
CREVICE = ramp('#1e1c1a', dark=0.6, light=1.6)
SNOW = ramp('#dfe7ef', dark=0.55, light=1.07, warm=0.0, cool=0.22)


def _facets(cv, rng, rows, cols, fissure, bevel, tilt):
    """A mosaic of rock masses: every pixel belongs to its nearest seed; each mass domed, tilted
    hard one way or another so it catches the light as a facet, with a crevice between masses."""
    n = rows * cols
    sx = (np.arange(n) % cols + rng.uniform(0.1, 0.9, n) + (np.arange(n) // cols % 2) * 0.5) * cv.w / cols
    sy = (np.arange(n) // cols + rng.uniform(0.1, 0.9, n)) * cv.h / rows
    yy, xx = np.mgrid[0:cv.h, 0:cv.w].astype(np.float32) + 0.5
    dx = np.abs(xx[..., None] - sx % cv.w)
    dy = np.abs(yy[..., None] - sy % cv.h)
    d = np.hypot(np.minimum(dx, cv.w - dx), np.minimum(dy, cv.h - dy))
    order = np.argsort(d, axis=-1)
    d1 = np.take_along_axis(d, order[..., :1], -1)[..., 0]
    d2 = np.take_along_axis(d, order[..., 1:2], -1)[..., 0]
    warp = smooth_noise(cv.w, cv.h, 6, rng)                  # crevices wander, widen and narrow,
    edge = d2 - d1 + 3.0 * (warp - 0.5)                      # and close up here and there
    near = order[..., 0]
    tl = rng.normal(0, tilt, (n, 2))
    ox = (xx - sx[near] + cv.w / 2) % cv.w - cv.w / 2
    oy = (yy - sy[near] + cv.h / 2) % cv.h - cv.h / 2
    width = fissure * (0.3 + 1.4 * smooth_noise(cv.w, cv.h, 4, rng))
    inside = edge > width
    prof = np.clip((edge - width) / bevel, 0, 1) ** 0.55
    cv.z = np.where(inside, prof * 1.4 + tl[near, 0] * ox + tl[near, 1] * oy, cv.z).astype(np.float32)
    cv.id = np.where(inside, near + 1 + cv.n, cv.id).astype(np.int32)
    cv.mat = np.where(inside, rng.integers(0, 3, n)[near], cv.mat).astype(np.int32)
    cv.tone = np.where(inside, rng.normal(0, 0.05, n)[near], cv.tone).astype(np.float32)
    cv.n += n
    return near, inside


def tex_rock(name, kind='rock'):
    """Raw rock: masses of every size split by deep, dark crevices, each a facet tilted to the
    light, scored with finer cracks and grained. `rock_wet` is darker and blue-grey with glints
    of water on the faces that catch the light; `rock_floor` flatter and browner, grit in the
    cracks."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.6, mat=3)
    floor = kind == 'rock_floor'
    _facets(cv, rng, 4 if floor else 3, 4 if floor else 3, 1.1, 5.0 if not floor else 3.5, 0.045 if not floor else 0.025)
    for _ in range(9):                                       # finer cracks across the masses
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, 2 * np.pi)
        pts = [(x, y)]
        for _ in range(3):
            a += rng.normal(0, 0.5)
            pts.append((pts[-1][0] + np.cos(a) * 5, pts[-1][1] + np.sin(a) * 5))
        cv.stroke(pts, 0.8, dome=0.5, mode='carve')
    cv.noise(0.22, cells=10, rng=rng, octaves=3)
    if floor:
        for _ in range(30):                                  # grit in the cracks
            x, y = rng.random() * T, rng.random() * T
            if cv.mat[int(y) % T, int(x) % T] == 3:
                cv.ellipse(x, y, 0.8, 0.7, z=-0.9, dome=0.4, mat=int(rng.integers(0, 3)))
    light = cv.light(relief=1.2, cavity=0.5, shadow=0.55, ambient=0.2, diffuse=0.52)
    if kind == 'rock_wet':                                   # glints of water where the light catches
        glint = (light > np.percentile(light, 90)) & (rng.random((T, T)) < 0.35) & (cv.mat != 3)
        cv.tone[glint] += 0.3
    return cv.paint(ROCK[kind] + [CREVICE], light, dither=0.3)


def tex_snow_rock(name):
    """Rock under snow: the same faceted masses, snow lying on the top of every one - thick on the
    flatter tops, thin down the faces - and filling the crevices, the rock dark between."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.6, mat=3)
    _facets(cv, rng, 3, 3, 1.1, 5.0, 0.04)
    cv.noise(0.2, cells=10, rng=rng, octaves=2)
    run = np.zeros((T, T), np.float32)                       # how far below its mass's top each pixel is
    ids = cv.id
    for y in range(1, 2 * T):                                # twice round, so the wrap is right
        yy = y % T
        same = (ids[yy] == ids[(yy - 1) % T]) & (ids[yy] > 0)
        run[yy] = np.where(same, run[(yy - 1) % T] + 1, 0)
    lump = smooth_noise(T, T, 8, rng)
    snow = (run < 3 + 6 * lump) & (ids > 0)
    snow |= (ids == 0) & (lump > 0.45)                        # drifts in the crevices
    cv.mat[snow] = 4
    cv.z[snow] += 0.35
    cv.tone[snow] = 0.0
    ramps = ROCK['rock'] + [CREVICE, SNOW]
    return _tile(cv, ramps, relief=1.1, cavity=0.45, shadow=0.5)


def tex_snow(name):
    """Fresh snow: soft drifts sculpted by the wind, their lee sides in blue shadow, faint ripples
    along them, and a glitter of ice crystals catching the light."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    drift = smooth_noise(T, T, 3, rng) * 0.7 + smooth_noise(T, T, 6, rng) * 0.3
    cv.z += (5.0 * drift).astype(np.float32)
    xs = np.arange(T)[None, :]
    ys = np.arange(T)[:, None]
    cv.z += (0.25 * np.sin(2 * np.pi * (5 * ys + 2 * xs) / T + 3 * drift)).astype(np.float32)
    light = cv.light(sun=(-0.6, -0.5, 0.6), relief=1.6, cavity=0.3, shadow=0.45, ambient=0.42, diffuse=0.55)
    rgb = cv.paint([ramp('#d0dae8', dark=0.62, light=1.1, warm=0.04, cool=0.3)], light, dither=0.35)
    glint = rng.random((T, T)) < 0.012 * np.clip(light * 1.6 - 0.4, 0, 1)
    rgb[glint] = (1.0, 1.0, 1.0)
    return rgb


def tex_ice(name):
    """A frozen lake from above: clear blue ice with depth in it - darker where it is thick and
    black - long straight fractures with white edges branching at sharp angles, air bubbles
    trapped in strings, and frost dusted over it."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    deep = smooth_noise(T, T, 3, rng) * 0.6 + smooth_noise(T, T, 7, rng) * 0.4
    cv.tone += (0.16 * (deep - 0.5)).astype(np.float32)
    frac = np.zeros((T, T), bool)
    for _ in range(4):                                       # fractures: straight runs, a branch off each
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, np.pi)
        for seg in range(3):
            L = rng.uniform(10, 26)
            nx, ny = x + np.cos(a) * L, y + np.sin(a) * L
            n = int(L * 2)
            xs = np.round(np.linspace(x, nx, n)).astype(int) % T
            ys = np.round(np.linspace(y, ny, n)).astype(int) % T
            frac[ys, xs] = True
            if rng.random() < 0.6:                           # a branch
                b = a + rng.choice([-1, 1]) * rng.uniform(0.6, 1.1)
                bl = rng.uniform(5, 12)
                m = int(bl * 2)
                bx = np.round(np.linspace(nx, nx + np.cos(b) * bl, m)).astype(int) % T
                by = np.round(np.linspace(ny, ny + np.sin(b) * bl, m)).astype(int) % T
                frac[by, bx] = True
            x, y = nx, ny
            a += rng.normal(0, 0.35)
    cv.mat[frac] = 1
    halo = np.zeros_like(frac)
    for dy, dx in ((0, 1), (1, 0)):
        halo |= np.roll(frac, (dy, dx), (0, 1))
    cv.tone[halo & ~frac] -= 0.12                            # the dark side of each crack
    for _ in range(5):                                       # strings of bubbles
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, 2 * np.pi)
        for k in range(rng.integers(4, 9)):
            px, py = x + np.cos(a) * k * 1.8 + rng.normal(0, 0.4), y + np.sin(a) * k * 1.8 + rng.normal(0, 0.4)
            cv.mat[int(py) % T, int(px) % T] = 1
    frost = rng.random((T, T)) < 0.04 * smooth_noise(T, T, 5, rng)
    cv.tone[frost] += 0.15
    return _tile(cv, [ramp('#8ab4c8', dark=0.35, light=1.3, cool=0.25), ramp('#eef6fa', dark=0.7, light=1.04)],
                 dither=0.35, cavity=0.0, shadow=0.0, ambient=0.34, diffuse=0.62)


def tex_sand(name):
    """Sand: ripples drawn by the wind, each with a lit face and a shaded lee, wandering a little,
    a shell fragment or two and a few dark grains."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    xs = np.arange(T)[None, :]
    ys = np.arange(T)[:, None]
    warp = smooth_noise(T, T, 3, rng)
    phase = 2 * np.pi * (4 * ys + 1 * xs) / T + 3.0 * warp
    cv.z += (0.35 * np.sin(phase) + 0.12 * np.sin(2 * phase)).astype(np.float32)
    cv.noise(0.08, cells=16, rng=rng)
    for _ in range(4):                                       # shell fragments
        x, y = rng.random() * T, rng.random() * T
        cv.ellipse(x, y, rng.uniform(0.8, 1.4), rng.uniform(0.6, 1.0), z=0.6, dome=0.5, angle=rng.uniform(0, 180),
                   mat=1)
    dark = rng.random((T, T)) < 0.015
    cv.mat[dark] = 2
    return _tile(cv, [ramp('#c4aa7c', dark=0.38, light=1.16), ramp('#ece2d0', dark=0.6, light=1.05),
                      ramp('#6e5e4a', dark=0.4)], dither=0.3, relief=1.4, cavity=0.2, shadow=0.3,
                 ambient=0.34, diffuse=0.62)


def tex_plaster(name, base='#c9bb98', stain='#6b5a40', amount=0.5):
    """Old plaster: a smooth render, mottled where it was patched, a hairline crack or two, a few
    faint water stains run down from wherever the water got in - not in stripes, and no band,
    so a wall stacked storey on storey has no seams."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.26, cells=5, rng=rng, octaves=3)
    patch = smooth_noise(T, T, 4, rng)
    cv.tone += (0.12 * (patch - 0.5)).astype(np.float32)
    for _ in range(int(rng.integers(1, 3))):                 # hairline cracks
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, 2 * np.pi)
        pts = [(x, y)]
        for _ in range(4):
            a += rng.normal(0, 0.6)
            pts.append((pts[-1][0] + np.cos(a) * 4, pts[-1][1] + np.sin(a) * 4))
        cv.stroke(pts, 0.55, dome=0.35, mode='carve')
    for _ in range(int(rng.integers(1, 4))):                 # water stains, faint, irregular
        x, y = rng.random() * T, rng.random() * T
        L, wd = rng.uniform(14, 34), rng.uniform(1.0, 2.2)
        yy = (np.arange(int(y), int(y + L)) % T)
        for k, row in enumerate(yy):
            sx = x + 1.2 * np.sin(k * 0.25)
            cols = np.arange(int(sx - wd), int(sx + wd) + 1) % T
            cv.tone[row, cols] -= amount * 0.12 * min(1.0, k / 4.0) * (1 - k / L)
    return _tile(cv, [ramp(base, dark=0.42, light=1.12)], dither=0.2, relief=0.8, cavity=0.3, shadow=0.2,
                 ambient=0.32, diffuse=0.7)


def tex_ivy(name):
    """A brick wall overgrown with ivy: brick in red courses, and over it the ivy - woody stems
    climbing and branching, clusters of dark three-pointed leaves, the newest a brighter green."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.6, mat=1)
    _blocks(cv, rng, list(range(0, T + 1, 8)), (14, 18), rough=0.3, chip=1, bevel=1.2, gap=0.8, tone=0.06)
    for _ in range(3):                                       # stems
        x, y = rng.random() * T, T + 2
        pts = [(x, y)]
        for _ in range(9):
            pts.append((pts[-1][0] + rng.normal(0, 3), pts[-1][1] - rng.uniform(5, 9)))
        cv.stroke(pts, 1.2, z=0.9, dome=0.5, mat=2)
    cover = smooth_noise(T, T, 3, rng)
    for _ in range(170):                                     # leaves
        x, y = rng.random() * T, rng.random() * T
        if cover[int(y) % T, int(x) % T] < 0.42:
            continue
        a = np.radians(rng.uniform(200, 340))
        L = rng.uniform(3.5, 5.5)
        m = 3 if rng.random() < 0.8 else 4
        cv.leaf(x, y, x + np.cos(a) * L, y + np.sin(a) * L, L * 0.85, z=1.2 + rng.random() * 0.5, dome=0.6,
                shape=0.5, base=0.5, mat=m, tone=rng.normal(0, 0.05), rib=0.35)
    return _tile(cv, [ramp('#8a3e2c', dark=0.32), ramp('#5a5048', dark=0.4), ramp('#5a4a34', dark=0.35),
                      ramp('#2e5a2a', dark=0.3, light=1.3), ramp('#5a8a34', dark=0.3)], cavity=0.45, shadow=0.55)


def tex_curtain(name, base='#6a1a1e'):
    """Heavy velvet curtains: folds of every width hanging straight down, each a rounded column
    lit on its left with a sheen along its crest, deep shadow where two folds meet."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.2, mat=0)
    x = 0.0
    while x < T:                                                     # folds of varying width, tiling across
        wd = float(rng.uniform(9, 17))
        if x + wd > T - 6:
            wd = T - x
        xs = np.arange(int(np.floor(x)), int(np.ceil(x + wd)))
        u = (xs + 0.5 - x) / wd
        prof = np.sqrt(np.clip(1 - (2 * u - 1) ** 2, 0, 1)) * rng.uniform(0.8, 1.2)
        cv.z[:, xs % T] = np.maximum(cv.z[:, xs % T], (prof[None, :] * 1.6 - 0.2).astype(np.float32))
        cv.tone[:, xs % T] = rng.normal(0, 0.04)
        x += wd
    sway = smooth_noise(T, T, 2, rng, cells_y=2)                     # a little sway in the folds' light
    cv.tone += (0.06 * (sway - 0.5)).astype(np.float32)
    return _tile(cv, [ramp(base, dark=0.3, light=1.5, warm=0.1)], dither=0.3, relief=1.8, cavity=0.45, shadow=0.5,
                 ambient=0.18, diffuse=0.55)


def tex_acoustic(name):
    """Acoustic ceiling tiles, four to a unit: each a shallow bevelled square in a grid of thin
    metal runners, the face pitted with fissures and pin-holes, a tea-coloured water stain or two."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.4, mat=1)
    for j in range(2):
        for i in range(2):
            cv.box(i * 32 + 1, j * 32 + 1, 30, 30, z=0.0, top=0.6, bevel=2.2, mat=0, tone=rng.normal(0, 0.025))
    pits = rng.random((T, T)) < 0.09
    cv.z[pits & (cv.mat == 0)] -= 0.25
    for _ in range(40):                                              # fissures
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, np.pi)
        cv.stroke([(x, y), (x + np.cos(a) * 2.5, y + np.sin(a) * 2.5)], 0.5, dome=0.2, mode='carve')
    for _ in range(int(rng.integers(1, 3))):                         # water stains, a ring and a pale middle
        x, y, r = rng.random() * T, rng.random() * T, rng.uniform(4, 9)
        yy, xx = np.mgrid[0:T, 0:T]
        d = np.hypot((xx - x + T / 2) % T - T / 2, (yy - y + T / 2) % T - T / 2)
        cv.tone -= (0.1 * np.exp(-((d - r) / 1.2) ** 2) + 0.03 * (d < r)).astype(np.float32)
    return _tile(cv, [ramp('#bcb8a8', dark=0.45, light=1.1), ramp('#7a7a74', dark=0.4, light=1.3)], dither=0.25,
                 cavity=0.35, shadow=0.35)


def tex_corrugated(name):
    """Corrugated iron: galvanised sheets in rounded ribs, two sheets to a unit lapped at the seam,
    nail heads in rows along the purlins, rust breaking out round the nails and running down in
    streaks, a sheet here and there gone rustier than its neighbour."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    xs = np.arange(T)
    rib = 0.6 * np.sin(2 * np.pi * xs / 6.4)                         # ten ribs a sheet
    cv.z[:] = rib[None, :].astype(np.float32)
    for x0 in (0, 32):                                               # the lap where one sheet lies on the next
        cv.z[:, (x0 + np.arange(2)) % T] += 0.5
        cv.z[:, (x0 + 2) % T] -= 0.5
    rust_sheet = [rng.random() < 0.5, rng.random() < 0.5]
    for y in (6, 38):                                                # nail rows on the purlins
        for x in np.arange(3.2, T, 6.4):
            cv.ellipse(x, y, 0.8, 0.8, z=0.9, dome=0.3, mat=2)
            if rng.random() < 0.6:                                   # a rust streak running down from it
                L = rng.uniform(6, 20)
                cv.tone[int(y):int(y + L), int(x) % T] -= 0.12
                cv.mat[int(y) + 1:int(y + L * 0.6), int(x) % T] = 1
    blotch = (smooth_noise(T, T, 9, rng) > 0.74) & (rng.random((T, T)) < 0.7)
    for k in range(2):
        if rust_sheet[k]:
            blotch[:, k * 32:(k + 1) * 32] |= (smooth_noise(T, T, 12, rng)[:, k * 32:(k + 1) * 32] > 0.7)
    cv.mat[blotch & (cv.mat == 0)] = 1
    cv.tone += (0.1 * (smooth_noise(T, T, 3, rng) - 0.5)).astype(np.float32)          # the zinc dulled unevenly
    return _tile(cv, [ramp('#7a7c78', dark=0.35, light=1.3, cool=0.08), ramp('#7a4a30', dark=0.35, light=1.25),
                      ramp('#4a4a48', dark=0.45, light=1.5)], dither=0.3, relief=1.5, cavity=0.3, shadow=0.35,
                 ambient=0.2, diffuse=0.55)


def tex_marble_dark(name):
    """Dark polished marble in square slabs: grey-black stone with long, soft, continuous veins of
    white and grey drifting across it, a fine joint between the slabs."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.3, mat=1)
    for j in range(2):
        for i in range(2):
            cv.box(i * 32 + 0.5, j * 32 + 0.5, 31, 31, z=0.0, top=0.3, bevel=1.0, mat=0)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    warp = smooth_noise(T, T, 3, rng) * 0.6 + smooth_noise(T, T, 6, rng) * 0.4
    for k, (fx, fy, wd, strength) in enumerate(((1, 1, 0.012, 0.5), (2, -1, 0.008, 0.32), (1, 2, 0.006, 0.22))):
        phase = 2 * np.pi * (fx * xx + fy * yy) / T + 7.0 * warp + rng.uniform(0, 2 * np.pi)
        vein = np.exp(-(np.sin(phase / 2) ** 2) / wd)                 # thin where the sine crosses zero
        cv.tone += (strength * vein).astype(np.float32)
    cv.tone += (0.06 * (smooth_noise(T, T, 4, rng) - 0.5)).astype(np.float32)
    return _tile(cv, [ramp('#3a3836', dark=0.5, light=2.4, cool=0.05), ramp('#1e1c1a', dark=0.5, light=1.6)],
                 dither=0.3, relief=0.6, cavity=0.2, shadow=0.2, ambient=0.22, diffuse=0.45)


def tex_alien_rock(name):
    """The rock of an alien world: dark violet masses, each a facet tilted to the light, and in the
    crevices between them a teal light welling up from inside (emissive), brightest in the cracks
    and spilling a little onto the faces either side."""
    rng = _rng(name)
    cv = Canvas(T, ground=-1.6, mat=3)
    _facets(cv, rng, 3, 3, 1.2, 5.0, 0.04)
    cv.noise(0.2, cells=10, rng=rng, octaves=2)
    crack = (cv.mat == 3)
    halo = np.zeros_like(crack)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)):
        halo |= np.roll(crack, (dy, dx), (0, 1))
    halo &= ~crack
    cv.mat[halo] = 4
    light = cv.light(relief=1.2, cavity=0.4, shadow=0.5, ambient=0.25, diffuse=0.55)
    rgb = cv.paint([ramp('#4a3a5e', dark=0.3, light=1.45), ramp('#3e3252', dark=0.3, light=1.5),
                    ramp('#52405a', dark=0.3, light=1.45), ramp('#5af0d8', dark=0.75, light=1.1),
                    ramp('#3a7a80', dark=0.5, light=1.4)], light, dither=0.3)
    em = np.where(crack, 1.0, np.where(halo, 0.4, 0.0)).astype(np.float32)
    return rgb, em


def tex_alien_ground(name):
    """The dust of an alien world: violet drifts over teal grit, and shards of crystal - pink, cyan,
    white - of every size, each with a bright facet and a shadow."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    drift = smooth_noise(T, T, 4, rng)
    cv.z += (1.2 * drift).astype(np.float32)
    grit = drift + 0.25 * (rng.random((T, T)) - 0.5) < 0.3               # teal grit where the dust is thin,
    cv.mat[grit] = 1                                                     # its edge broken up grain by grain
    cv.tone += (0.12 * (smooth_noise(T, T, 9, rng) - 0.5)).astype(np.float32)
    cv.noise(0.15, cells=12, rng=rng)
    for _ in range(26):                                                  # crystal shards
        x, y = rng.random() * T, rng.random() * T
        L = rng.uniform(1.2, 3.6)
        a = np.radians(rng.uniform(-150, -30))
        m = int(rng.choice([2, 2, 3, 4]))
        cv.polygon([(x - L * 0.3, y), (x + np.cos(a) * L, y + np.sin(a) * L), (x + L * 0.3, y)], z=1.4, top=0.8,
                   bevel=0.6, mat=m)
    return _tile(cv, [ramp('#6a4a6e', dark=0.35, light=1.35), ramp('#3a6a72', dark=0.35, light=1.4),
                      ramp('#e88ad0', dark=0.5, light=1.2), ramp('#8ae8f0', dark=0.5, light=1.15),
                      ramp('#e8f0f8', dark=0.6, light=1.05)], dither=0.3, cavity=0.35, shadow=0.45,
                 ambient=0.32, diffuse=0.62)


def tex_menhir(name, top=False):
    """The face of a standing stone, one weathered surface: broad swells and hollows, runnels worn
    down it by the rain, two or three long cracks, rosettes of pale lichen, moss gathered at its
    foot - or (`top`) the upper courses, greyer and more lichened, without the moss."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    swell = smooth_noise(T, T, 2, rng) * 0.6 + smooth_noise(T, T, 4, rng) * 0.4
    cv.z += (2.4 * swell).astype(np.float32)
    cv.noise(0.3, cells=12, rng=rng, octaves=3)                        # pitting
    for _ in range(9):                                                   # runnels down the face
        x = rng.random() * T
        pts = [(x, -2)]
        for _ in range(6):
            pts.append((pts[-1][0] + rng.normal(0, 1.0), pts[-1][1] + rng.uniform(8, 14)))
        cv.stroke(pts, rng.uniform(1.0, 2.2), dome=0.5, mode='carve')
    for _ in range(2):                                                   # long cracks
        x, y = rng.random() * T, rng.random() * T
        a = np.radians(rng.uniform(60, 120))
        pts = [(x, y)]
        for _ in range(5):
            a += rng.normal(0, 0.3)
            pts.append((pts[-1][0] + np.cos(a) * 6, pts[-1][1] + np.sin(a) * 6))
        cv.stroke(pts, 0.9, dome=0.8, mode='carve')
    for _ in range(26 if top else 14):                                   # lichen rosettes
        x, y = rng.random() * T, rng.random() * T
        r = rng.uniform(1.2, 3.2)
        m = 1 if rng.random() < 0.6 else 2
        for _ in range(6):
            cv.ellipse(x + rng.normal(0, r * 0.4), y + rng.normal(0, r * 0.4), r * 0.45, r * 0.4, z=0.0, dome=0.2,
                       mode='add', mat=m, tone=rng.normal(0, 0.04))
            cv.mat[int(y) % T, int(x) % T] = m
    lich = np.zeros((T, T), bool)
    for _ in range(26 if top else 14):
        x, y, r = rng.random() * T, rng.random() * T, rng.uniform(1.2, 3.0)
        yy, xx = np.mgrid[0:T, 0:T]
        d = np.hypot((xx - x + T / 2) % T - T / 2, (yy - y + T / 2) % T - T / 2)
        lich |= d < r * (0.7 + 0.3 * rng.random((T, T)))
    cv.mat[lich] = np.where(rng.random(int(lich.sum())) < 0.6, 1, 2)
    if not top:                                                          # moss at the foot
        foot = (np.arange(T)[:, None] > T - 14 + 6 * smooth_noise(T, 1, 5, rng)[0][None, :])
        cv.mat[foot & (rng.random((T, T)) < 0.75)] = 3
    cv.tone += (0.08 * (smooth_noise(T, T, 3, rng) - 0.5)).astype(np.float32)
    return _tile(cv, [ramp('#8a8a84', dark=0.32, light=1.3), ramp('#b8b48a', dark=0.45, light=1.12),
                      ramp('#9aa49a', dark=0.45, light=1.15), ramp('#4e6a34', dark=0.35, light=1.25)],
                 relief=1.0, cavity=0.4, shadow=0.4, ambient=0.3, diffuse=0.62)


def spr_stone_cap():
    """The weathered top of a standing stone: a slanted, chipped crown of grey stone with lichen on
    it, high on one side, the corners knocked off - to set on a wall block one cell wide (`z` a
    little under the block's height; `flip` half of them) so the stones' outline against the sky
    is not a row of flat-topped boxes."""
    rng = np.random.default_rng(191)
    w, h = 64, 28
    cv = Canvas(w, h, wrap=False, ground=-9)
    xs = np.arange(w) + 0.5
    u = xs / w
    rise = 0.25 + 0.75 * u                                              # a slanted top, high on one side,
    shoulder = np.clip(np.minimum(u, 1 - u) / 0.12, 0, 1) ** 0.5         # the corners knocked off,
    top = h - (h - 3) * rise * shoulder
    top += 4.0 * (smooth_noise(w, 1, 9, rng, wrap=False)[0] - 0.5)      # and chipped along its edge
    top = np.minimum(top, h - 1)
    yy = np.arange(h)[:, None] + 0.5
    body = yy >= top[None, :]
    cv.put(np.arange(h), np.arange(w), body, (1.0 * shoulder)[None, :].repeat(h, 0), mat=0)
    cv.noise(0.25, cells=8, rng=rng)
    for _ in range(9):                                                   # lichen
        x, y = rng.uniform(8, w - 8), rng.uniform(h * 0.35, h - 2)
        if body[int(y), int(x)]:
            cv.ellipse(x, y, rng.uniform(1.2, 2.6), rng.uniform(1.0, 2.0), z=1.6, dome=0.2, mode='max', mat=1)
    return _prop(cv, [ramp('#8a8a84', dark=0.32, light=1.3), ramp('#b8b48a', dark=0.45, light=1.12)], outline=False,
                 relief=1.0, cavity=0.35, shadow=0.35, ambient=0.3, diffuse=0.62)


def spr_jaguar():
    """A jaguar prowling, side on, facing left: a long, low, heavy body, the shoulders working, a
    broad head with round ears, the tail curving down and up at the tip; a golden coat in black
    rosettes, spots on the head and legs, a pale belly. Its eyes catch the light (emissive)."""
    rng = np.random.default_rng(181)
    w, h = 72, 32
    cv = Canvas(w, h, wrap=False, ground=-9)
    t = np.linspace(0, 1, 14)                                            # the tail
    cv.stroke(list(zip(56 + 14 * t, 13 + 10 * t - 8 * t ** 4)), 2.6, z=0.0, dome=0.8, taper=(1.0, 0.7), mat=0)
    for x0, x1, tn in ((20, 19, -0.08), (50, 52, -0.08)):                # the far legs
        cv.stroke([(x0, 16), (x0 + 1, 24), (x1, h - 1)], 3.0, z=0.2, dome=0.7, taper=(1.3, 0.8), mat=0, tone=tn)
    cv.ellipse(38, 15, 20, 7.5, z=0.6, dome=1.2, mat=0)                  # the body
    cv.ellipse(23, 13, 8.5, 7.5, z=0.9, dome=1.2, mat=0)                 # the shoulders
    cv.ellipse(53, 14, 7.5, 6.5, z=0.8, dome=1.1, mat=0)                 # the haunch
    cv.ellipse(36, 20.5, 14, 2.6, z=1.3, dome=0.4, mat=1)                # the pale belly
    for x0, x1 in ((26, 24), (55, 57)):                                  # the near legs, one stepping forward
        cv.stroke([(x0, 17), (x0 - 2, 24), (x1, h - 1.5)], 3.4, z=1.4, dome=0.8, taper=(1.3, 0.85), mat=0)
        cv.ellipse(x1 - 0.8, h - 1.4, 2.4, 1.3, z=1.6, dome=0.5, mat=0)   # paws
    cv.ellipse(10, 11, 7.0, 5.6, z=1.4, dome=1.1, mat=0)                 # the head
    cv.ellipse(5, 13.5, 3.6, 2.6, z=1.6, dome=0.8, mat=1)                # the muzzle
    cv.ellipse(2.6, 12.4, 1.0, 0.8, z=2.0, dome=0.3, mat=3)              # nose
    cv.ellipse(12.5, 6.4, 2.0, 2.0, z=1.5, dome=0.6, mat=0)              # ear
    cv.ellipse(7.8, 9.6, 1.1, 0.8, z=2.2, dome=0.2, mat=2)               # the eye
    coat = (cv.mat == 0) & (cv.id > 0)
    ys, xs = np.nonzero(coat[7:21, 15:62])
    placed = []
    for i in rng.permutation(len(ys)):                                   # rosettes spread over the coat, apart
        x, y = xs[i] + 15.5, ys[i] + 7.5
        if any((x - px) ** 2 + (y - py) ** 2 < 4.2 ** 2 for px, py in placed):
            continue
        placed.append((x, y))
        r = rng.uniform(1.2, 1.7)
        for b in np.linspace(0, 2 * np.pi, 7)[:-1] + rng.uniform(0, 1):
            if rng.random() < 0.85:                                      # a broken ring of dark spots
                cv.ellipse(x + np.cos(b) * r, y + np.sin(b) * r * 0.85, 0.5, 0.5, z=2.0, dome=0.1, mat=3)
        cv.ellipse(x, y, 0.7, 0.6, z=1.9, dome=0.1, mat=0, tone=-0.08)   # the darker gold inside
    for _ in range(14):                                                  # spots on the head and legs
        x, y = (rng.uniform(5, 14), rng.uniform(7, 13)) if rng.random() < 0.5 else (rng.uniform(22, 58), rng.uniform(21, 29))
        cv.ellipse(x, y, 0.5, 0.5, z=2.0, dome=0.1, mat=3)
    em = ((cv.mat == 2) & (cv.id > 0)) * 1.0
    return _prop(cv, [ramp('#d0943a', dark=0.32, light=1.25, warm=0.12), ramp('#ecdcb8', dark=0.45, light=1.06),
                      ramp('#d8f050', dark=0.6, light=1.1), ramp('#24160c', dark=0.6, light=1.6)], relief=1.0,
                 cavity=0.35, shadow=0.45, em=em)


# ---------------------------------------------------------------- props

def spr_barrel():
    """A wooden barrel: staves bulging at the middle, three iron hoops round it, the lid showing at
    the top, lit on the left."""
    w, h = 32, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    _lathe(cv, 16, [(3, 11.5), (12, 14), (22, 15), (32, 14), (43, 11.5)], z=0.0, dome=1.3, mat=0)
    for x in (8, 12.5, 16.5, 20.5, 25):                        # the joints between staves
        cv.stroke([(x, 4), (16 + (x - 16) * 1.12, 22), (x, 42)], 0.7, dome=0.3, mode='carve')
    for y, half in ((8, 13.2), (22, 15.1), (36, 13.5)):        # hoops
        _lathe(cv, 16, [(y, half + 0.3), (y + 2.5, half + 0.4)], z=0.2, dome=1.35, mat=1)
    cv.ellipse(16, 3.2, 11, 2.4, z=1.2, dome=0.3, mat=2)       # the lid
    return _prop(cv, [WOOD, IRON, WOOD_DARK], relief=1.0, cavity=0.35, shadow=0.45, ambient=0.3, diffuse=0.65)


def spr_broken_barrel():
    """A barrel burst open: the bottom half still hooped, its front staves splintered off at
    different heights so the dark inside shows through, the back staves standing taller, a loose
    stave leaning on it, another fallen, and a hoop lying on the ground."""
    rng = np.random.default_rng(101)
    w, h = 48, 44
    cx, rim, rx = 21, 17, 13.8
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, top in ((cx - 10, 10), (cx - 5, 4), (cx, 7), (cx + 5, 2), (cx + 10, 9)):   # the back staves
        peak = x + rng.uniform(-1.2, 1.2)
        cv.polygon([(x - 2.6, rim + 3), (x - 2.6, top + 3), (peak, top), (x + 2.6, top + rng.uniform(1, 4)),
                    (x + 2.6, rim + 3)], top=0.25, bevel=1.0, mat=1, tone=rng.normal(0, 0.04))
    cv.ellipse(cx, rim, rx, 4.2, z=0.05, dome=0.0, mat=2)      # the dark inside
    cv.box(cx - rx, rim, 2 * rx, 13, z=0.05, top=0.0, bevel=1, mat=2)
    body = cv.layer()                                          # the front, built on its own and broken
    _lathe(body, cx, [(rim - 1, 14.4), (29, 15.6), (43, 12.6)], z=0.6, dome=1.3, mat=0)
    for x in (cx - 10, cx - 5, cx, cx + 5, cx + 10):           # joints between the staves
        body.stroke([(x, rim), (cx + (x - cx) * 1.08, 30), (cx + (x - cx) * 0.9, 42)], 0.7, dome=0.3, mode='carve')
    _lathe(body, cx, [(31, 15.4), (33.5, 15.5)], z=0.8, dome=1.35, mat=3)   # hoops
    _lathe(body, cx, [(38.5, 14.2), (41, 13.6)], z=0.8, dome=1.35, mat=3)
    cut = np.zeros((h, w), bool)
    for k, a in enumerate(np.arange(cx - 15, cx + 15, 5.0)):   # each front stave broken off at its own height
        drop, peak, spike = rng.uniform(0, 9), rng.uniform(0.2, 0.8), rng.uniform(2, 5)
        if k in (2, 4):
            drop = rng.uniform(0, 2)
        for x in range(int(np.floor(a)), int(np.ceil(a + 5))):
            if not 0 <= x < w:
                continue
            u = (x + 0.5 - cx) / rx
            arc = rim + 4.2 * np.sqrt(max(0.0, 1 - u * u))     # the near half of the opening
            t = (x + 0.5 - a) / 5
            cut[:int(round(max(arc, arc + drop + spike * abs(t - peak) * 2 - spike * 0.5))), x] = True
    cv.paste(body, cut=cut)
    cv.stroke([(3, 42), (8.5, 22)], 3.6, z=1.4, dome=0.9, taper=(1.0, 0.8), mat=0, tone=0.03)        # a stave leaning on it
    cv.stroke([(34, 40.5), (40, 39.0), (47, 39.8)], 3.2, z=1.0, dome=0.8, taper=(0.8, 1.0), mat=0, tone=-0.03)   # one fallen
    a = np.linspace(0, 2 * np.pi, 30)                          # a hoop on the ground
    cv.stroke(list(zip(40 + np.cos(a) * 6, 41.6 + np.sin(a) * 1.8)), 1.2, z=1.6, dome=0.4, mat=3)
    return _prop(cv, [WOOD, WOOD_DARK, ramp('#22160e', dark=0.6, light=1.3), IRON], relief=1.0, cavity=0.4,
                 shadow=0.45)


def spr_crate():
    """A wooden crate: planks behind a frame of battens and a diagonal brace, nails at the corners,
    a stencilled arrow, lit on the left."""
    w, h = 40, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k in range(4):                                         # the planks
        cv.box(2, 2 + k * 9, 36, 8.6, z=0.0, top=0.8, bevel=1.2, mat=0, tone=(k % 2) * 0.04 - 0.02)
    for x0, y0, x1, y1 in ((2, 2, 38, 2), (2, 38, 38, 38), (2, 2, 2, 38), (38, 2, 38, 38)):   # the frame
        cv.stroke([(x0, y0), (x1, y1)], 4.2, z=0.8, dome=0.7, mat=1)
    cv.stroke([(5, 35), (35, 5)], 3.6, z=0.6, dome=0.6, mat=1)      # the brace
    for x, y in ((4, 4), (36, 4), (4, 36), (36, 36)):          # nails
        cv.ellipse(x, y, 0.8, 0.8, z=1.7, dome=0.3, mat=2)
    for k in range(2):                                         # a stencilled arrow, pointing up
        x = 13 + k * 12
        cv.stroke([(x, 30), (x, 21)], 1.2, z=0.85, dome=0.1, mat=3)
        cv.stroke([(x - 2.5, 24), (x, 20.5), (x + 2.5, 24)], 1.2, z=0.86, dome=0.1, mat=3)
    return _prop(cv, [ramp('#8a6440', dark=0.3), WOOD_DARK, IRON, ramp('#2e2a26', dark=0.6, light=1.6)],
                 relief=1.0, cavity=0.35, shadow=0.45, ambient=0.3, diffuse=0.65)


def spr_fountain():
    """A stone fountain: a broad round basin with a moulded rim and water in it, a fluted pedestal
    carrying a bowl, water spilling from the bowl in arcs and falling as drops."""
    rng = np.random.default_rng(103)
    w, h = 80, 72
    cx = w / 2
    cv = Canvas(w, h, wrap=False, ground=-9)
    _lathe(cv, cx, [(50, 36), (54, 38), (66, 36), (72, 34)], z=0.0, dome=1.2, mat=0)        # the basin
    _lathe(cv, cx, [(48, 37), (52, 38.5)], z=0.6, dome=1.0, mat=0, tone=0.05)              # its rim
    cv.ellipse(cx, 50.5, 33, 2.2, z=1.6, dome=0.2, mat=1)                                  # the water
    _lathe(cv, cx, [(20, 4), (24, 5), (46, 6), (50, 8)], z=0.8, dome=1.2, mat=0)           # the pedestal
    for x in (cx - 3, cx, cx + 3):
        cv.stroke([(x, 26), (x, 46)], 0.6, dome=0.3, mode='carve')
    _lathe(cv, cx, [(12, 15), (16, 14), (20, 6)], z=1.2, dome=1.2, mat=0)                  # the bowl
    cv.ellipse(cx, 12, 14, 1.6, z=2.5, dome=0.2, mat=1)
    for side in (-1, 1):                                       # water spilling over in arcs
        t = np.linspace(0, 1, 12)
        cv.stroke(list(zip(cx + side * (14 + 10 * t), 13 + 36 * t * t)), 1.2, z=2.6, dome=0.3, mat=2)
    cv.stroke([(cx, 2), (cx, 11)], 1.4, z=2.8, dome=0.3, mat=2)                             # a jet
    for _ in range(12):                                        # drops
        x, y = cx + rng.uniform(-30, 30), rng.uniform(16, 48)
        if abs(x - cx) > 8:
            cv.ellipse(x, y, 0.6, 0.9, z=2.6, dome=0.2, mat=2)
    return _prop(cv, [STONE_F, WATER, ramp('#bfe8f0', dark=0.6, light=1.05)], relief=1.0, cavity=0.4, shadow=0.45)


def spr_rowboat():
    """A wooden rowboat drawn up or afloat: a clinker hull of overlapping strakes, the top one
    painted a faded teal, a lighter gunwale, the bow rising, an oar laid along it with its blade
    over the stern."""
    w, h = 88, 26
    cv = Canvas(w, h, wrap=False, ground=-9)
    xs = np.arange(w) + 0.5
    top = 6.0 + 0.0016 * (xs - 50) ** 2 - np.clip((14 - xs) / 14, 0, 1) * 4.5       # sheer: the bow rises
    keel = np.where(xs < 16, 9 + (xs / 16) * 13, 22.5 - np.clip((xs - 78) / 9, 0, 1) * 7)
    keel = np.minimum(keel, 23.5)
    yy = np.arange(h)[:, None] + 0.5
    hull = (yy >= top[None, :]) & (yy <= keel[None, :]) & (xs[None, :] > 1.5) & (xs[None, :] < 86)
    t = np.clip((yy - top[None, :]) / np.maximum(keel - top, 1)[None, :], 0, 1)
    cv.put(np.arange(h), np.arange(w), hull, 1.0 - 0.4 * t, mat=0)
    for k in (0.3, 0.55, 0.78):                                       # the strakes' lapped edges
        line = top + (keel - top) * k
        pts = [(x, line[int(x)]) for x in range(3, 85, 4)]
        cv.stroke(pts, 0.8, dome=0.4, mode='carve')
    painted = hull & (t < 0.3)
    cv.mat[painted] = 1
    rim = hull & (yy < top[None, :] + 1.6)
    cv.mat[rim] = 2
    cv.z[rim] += 0.3
    cv.stroke([(18, top[18] - 1.2), (70, top[70] - 2.6), (84, top[84] - 3.4)], 1.4, z=1.6, dome=0.6, mat=2)   # the oar
    cv.polygon([(80, top[80] - 4.8), (88, top[84] - 6.2), (88, top[84] - 1.6), (80, top[80] - 2.0)], z=1.6,
               top=0.5, bevel=1.0, mat=2)
    return _prop(cv, [WOOD, HULL_PAINT, OAR], relief=1.0, cavity=0.4, shadow=0.45, ambient=0.3, diffuse=0.65)


def spr_bench():
    """A park bench: three slats in the backrest and two in the seat, held in cast-iron ends with
    a scrolled armrest and curving legs."""
    w, h = 60, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for y in (3, 9, 15):                                              # the backrest
        cv.box(6, y, 48, 4.6, z=0.0, top=0.8, bevel=1.0, mat=0, tone=0.02)
    for y, tn in ((23, 0.04), (27.5, -0.04)):                         # the seat
        cv.box(5, y, 50, 4.0, z=0.4, top=0.8, bevel=1.0, mat=0, tone=tn)
    for side in (-1, 1):                                              # the iron ends
        x = 30 + side * 25
        cv.stroke([(x - side * 1, 2), (x, 22), (x - side * 2, 31), (x + side * 1, h)], 2.2, z=1.2, dome=0.6, mat=1)
        cv.stroke([(x - side * 2, 31), (x - side * 6, h)], 1.8, z=1.1, dome=0.6, mat=1)
        a = np.linspace(0, 1.7 * np.pi, 16)
        cv.stroke(list(zip(x + side * (2.5 + np.cos(a) * 2.6), 20 + np.sin(a) * 2.6)), 1.3, z=1.4, dome=0.5,
                  mat=1)                                               # the scrolled armrest
        cv.stroke([(x - side * 1, 18), (x + side * 3, 17.5)], 1.6, z=1.4, dome=0.5, mat=1)
    return _prop(cv, [SLAT, CAST_IRON], relief=1.0, cavity=0.4, shadow=0.45, ambient=0.3, diffuse=0.65)


def spr_flowers():
    """A clump of flowers: leaves and stems, and blooms of four kinds - red, yellow, white, pink -
    each five petals round a dark eye, at different heights."""
    rng = np.random.default_rng(161)
    w, h = 44, 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(26):                                               # leaves
        x = rng.uniform(4, 40)
        a = np.radians(rng.uniform(-150, -30))
        L = rng.uniform(5, 9)
        cv.leaf(x, h, x + np.cos(a) * L, h + np.sin(a) * L, L * 0.45, z=rng.random() * 0.4, dome=0.6, mat=4,
                tone=rng.normal(0, 0.05), rib=0.3)
    for k in range(13):                                               # stems and blooms
        x = rng.uniform(5, 39)
        top = rng.uniform(4, 16)
        cv.stroke([(x, h - 2), (x + rng.normal(0, 1.2), top)], 0.7, z=0.6, dome=0.3, mat=4)
        m = int(rng.integers(0, 4))
        r = rng.uniform(1.6, 2.4)
        for p in range(5):
            b = p * 2 * np.pi / 5 + rng.uniform(0, 1)
            cv.ellipse(x + np.cos(b) * r, top + np.sin(b) * r * 0.8, r * 0.75, r * 0.6, z=1.4 + k * 0.02, dome=0.6,
                       angle=np.degrees(b), mat=m)
        cv.ellipse(x, top, 0.9, 0.8, z=1.9 + k * 0.02, dome=0.5, mat=5)
    return _prop(cv, FLOWER + [STEMS, ramp('#3a2a1a', dark=0.5, light=1.6)], relief=1.0, cavity=0.35, shadow=0.4)


def spr_statue():
    """A statue on a plinth: a draped woman in weathered marble, her weight on one leg, one arm
    raised with a wreath, the other gathering her robe; long folds in the drapery catching the
    light; the moulded plinth stained and touched with lichen."""
    rng = np.random.default_rng(163)
    w, h = 48, 104
    cx = 24
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(8, 80, 32, 24, z=0.0, top=1.0, bevel=2.0, mat=0, tone=-0.04)                 # the plinth
    cv.box(5, 76, 38, 5, z=0.8, top=0.8, bevel=1.5, mat=0, tone=0.04)                   # its cornice
    cv.box(6, 98, 36, 6, z=0.6, top=0.8, bevel=1.5, mat=0)                              # its foot
    cv.polygon([(cx - 9, 76), (cx - 8, 40), (cx - 5, 24), (cx + 5, 24), (cx + 8, 40), (cx + 11, 76)], z=0.8,
               top=1.6, bevel=5, mat=0)                                                  # the robed body
    for x0, x1 in ((cx - 6, cx - 7), (cx - 3, cx - 3.5), (cx, cx + 0.5), (cx + 3, cx + 5), (cx + 6, cx + 9)):
        cv.stroke([(x0, 34), (x0 + (x1 - x0) * 0.5, 55), (x1, 75)], 0.8, dome=0.5, mode='carve')   # folds
    cv.stroke([(cx - 8, 44), (cx + 7, 36)], 1.6, z=2.3, dome=0.7, mat=0, tone=0.05)        # the robe's sash
    cv.ellipse(cx + 0.5, 15, 4.2, 5.0, z=2.4, dome=1.2, mat=0, tone=0.06)                 # head
    cv.ellipse(cx + 2.5, 11.5, 2.6, 2.4, z=2.6, dome=0.8, mat=0)                          # hair, gathered up
    cv.stroke([(cx, 20), (cx, 24)], 2.6, z=2.2, dome=0.8, mat=0)                           # neck
    cv.stroke([(cx + 5, 26), (cx + 10, 16), (cx + 12, 5)], 2.4, z=2.6, dome=0.8, taper=(1.1, 0.8), mat=0)   # raised arm
    a = np.linspace(0, 2 * np.pi, 20)
    cv.stroke(list(zip(cx + 12.5 + np.cos(a) * 3.4, 3.4 + np.sin(a) * 2.2)), 1.2, z=3.0, dome=0.5, mat=0,
              tone=0.03)                                                                   # the wreath
    cv.stroke([(cx - 5, 26), (cx - 9, 38), (cx - 8, 46)], 2.4, z=2.5, dome=0.8, taper=(1.1, 0.9), mat=0)   # the other
    for x in (cx - 4, cx + 6):
        cv.ellipse(x, 76.5, 2.6, 1.4, z=2.0, dome=0.6, mat=0)                             # feet
    stain = smooth_noise(w, h, 4, rng, wrap=False, cells_y=8) > 0.66
    cv.tone[stain & (cv.mat == 0)] -= 0.08
    lichen = (smooth_noise(w, h, 6, rng, wrap=False) > 0.7) & (np.arange(h)[:, None] > 78) & (cv.id > 0)
    cv.mat[lichen] = 1
    return _prop(cv, [MARBLE_W, LICHEN_S], relief=1.1, cavity=0.45, shadow=0.5, ambient=0.28, diffuse=0.62)


def spr_bed():
    """An iron bedstead: head and foot rails of tubing with uprights, a mattress made up in white
    sheets, a pillow at the head and a grey blanket turned back over the foot of it."""
    w, h = 80, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (3, 76):                                                          # the posts
        cv.stroke([(x, 2 if x == 3 else 10), (x, h)], 2.6, z=0.6, dome=0.8, mat=0)
    for x0, top in ((3, 2), (76, 10)):                                          # head and foot rails
        x1 = x0 + 0.0
        cv.stroke([(x0 - 0.2, top + 1), (x0 + 0.2, top + 1)], 2.6, z=0.8, dome=0.8, mat=0)
    cv.stroke([(3, 4), (3, 4)], 3.2, z=1.0, dome=0.8, mat=0)
    cv.box(4, 18, 72, 8, z=0.4, top=1.0, bevel=2.5, mat=1)                       # the mattress, made up
    cv.box(44, 15, 32, 11, z=0.8, top=1.2, bevel=3.0, mat=2)                     # the blanket over the foot
    cv.stroke([(44, 16), (44, 25)], 1.0, dome=0.5, mode='carve')                 # its turned-back edge
    cv.stroke([(48, 15.5), (75, 15.5)], 1.2, z=2.0, dome=0.4, mat=2, tone=0.06)
    cv.ellipse(15, 15, 9, 4.2, z=1.2, dome=1.2, mat=1, tone=0.04)                 # the pillow
    cv.stroke([(4, 27), (76, 27)], 2.0, z=0.6, dome=0.6, mat=0)                   # the side rail
    for x in (8, 72):                                                          # legs and castors
        cv.stroke([(x, 27), (x, h - 3)], 2.0, z=0.4, dome=0.6, mat=0)
        cv.ellipse(x, h - 2, 2.0, 1.8, z=0.4, dome=0.6, mat=3)
    for x in range(8, 20, 3):                                                   # the headboard's uprights
        cv.stroke([(x - 4, 4), (x - 4, 18)], 0.9, z=0.5, dome=0.5, mat=0)
    return _prop(cv, [BED_IRON, SHEET, BLANKET, TYRE], relief=1.0, cavity=0.35, shadow=0.45)


def spr_wheelchair():
    """An old wheelchair, side on: a big spoked rear wheel with its push rim, a small caster in
    front, a leather seat and back on a steel frame, armrest, push handles and a footrest."""
    w, h = 40, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(9, 4), (11, 26), (12, 30)], 1.6, z=0.3, dome=0.6, mat=0)            # the back post and handle
    cv.stroke([(6, 4), (10, 4)], 2.0, z=0.4, dome=0.6, mat=2)
    cv.polygon([(10.5, 7), (14, 7), (15, 26), (12, 26)], z=0.6, top=0.8, bevel=1.2, mat=1)   # the back
    cv.polygon([(12, 24), (30, 23), (30, 27), (12, 28)], z=0.7, top=0.8, bevel=1.2, mat=1)   # the seat
    cv.stroke([(12, 18), (28, 18), (29, 23)], 1.3, z=1.6, dome=0.5, mat=0)           # the armrest
    cv.stroke([(28, 27), (33, 40), (37, 40)], 1.3, z=0.6, dome=0.5, mat=0)           # the footrest
    cv.stroke([(28, 27), (31, h - 6)], 1.2, z=0.4, dome=0.5, mat=0)
    a = np.linspace(0, 2 * np.pi, 40)                                           # the big wheel
    wx, wy, R = 16, 31, 15
    cv.stroke(list(zip(wx + np.cos(a) * R, wy + np.sin(a) * R)), 2.4, z=1.2, dome=0.8, mat=3)
    cv.stroke(list(zip(wx + np.cos(a) * (R - 2.6), wy + np.sin(a) * (R - 2.6))), 0.8, z=1.6, dome=0.5, mat=0)
    for k in range(12):
        b = k * np.pi / 6
        cv.stroke([(wx, wy), (wx + np.cos(b) * (R - 1.5), wy + np.sin(b) * (R - 1.5))], 0.5, z=1.1, dome=0.3, mat=0)
    cv.ellipse(wx, wy, 1.8, 1.8, z=1.8, dome=0.6, mat=0)
    cv.stroke(list(zip(32 + np.cos(a) * 3.2, h - 4 + np.sin(a) * 3.2)), 1.4, z=0.8, dome=0.6, mat=3)   # caster
    return _prop(cv, [CHROME, LEATHER, TYRE, TYRE], relief=1.0, cavity=0.3, shadow=0.4)


def spr_table():
    """A heavy wooden table: a thick top with a lit edge and grain along it, an apron under it,
    turned legs at the corners, the far pair a shade darker."""
    rng = np.random.default_rng(171)
    w, h = 80, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, tn in ((10, -0.1), (68, -0.1)):                                       # the far legs
        _lathe(cv, x, [(12, 2.2), (20, 2.8), (24, 2.0), (34, 2.4), (39, 2.0)], z=0.0, dome=1.0, mat=0, tone=tn)
    cv.box(3, 12, 74, 6, z=0.3, top=0.8, bevel=1.2, mat=0, tone=-0.05)              # the apron
    for x in (6, 74):                                                          # the near legs, turned
        _lathe(cv, x, [(12, 2.6), (19, 3.4), (23, 2.3), (27, 3.0), (34, 2.6), (40, 2.2)], z=0.6, dome=1.2, mat=0)
    cv.box(0, 6, 80, 7, z=0.9, top=1.0, bevel=1.5, mat=0, tone=0.04)                # the top
    for _ in range(12):
        x, y = rng.uniform(0, 70), rng.uniform(7, 12)
        cv.stroke([(x, y), (x + rng.uniform(8, 20), y + rng.normal(0, 0.2))], 0.5, dome=0.2, mode='carve')
    return _prop(cv, [TABLE_WOOD], relief=1.0, cavity=0.4, shadow=0.45, ambient=0.32, diffuse=0.66)


def spr_chest():
    """A chest of oak planks under a rounded lid, bound with iron straps studded with rivets,
    iron corners, and a brass lock plate with its keyhole at the front."""
    w, h = 48, 36
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(2, 14, 44, 21, z=0.0, top=1.0, bevel=2.0, mat=0)                        # the body
    for y in (20, 26, 31):
        cv.stroke([(3, y), (45, y)], 0.7, dome=0.4, mode='carve')                  # plank seams
    t = np.linspace(-1, 1, 25)                                                  # the rounded lid
    lid = [(24 + 22 * u, 14 - 11 * np.sqrt(max(0.0, 1 - u * u))) for u in t]
    cv.polygon(lid + [(46, 14), (2, 14)], z=0.4, top=1.2, bevel=3.0, mat=0, tone=0.05)
    cv.stroke([(2, 14), (46, 14)], 1.6, z=1.6, dome=0.5, mat=1)                     # the lid's iron edge
    for x in (9, 39):                                                          # straps over the lid and down
        cv.stroke([(x, 3 + 4 * (1 - abs(x - 24) / 22)), (x, 14), (x, 34)], 2.6, z=1.5, dome=0.6, mat=1)
        for y in (8, 17, 24, 31):
            cv.ellipse(x, y, 0.8, 0.8, z=2.6, dome=0.4, mat=1, tone=0.1)
    for x0 in (2, 42):                                                          # iron corners
        cv.box(x0, 30, 4, 5, z=1.4, top=0.4, bevel=0.8, mat=1)
    cv.box(20.5, 12, 7, 9, z=1.6, top=0.6, bevel=1.0, mat=2)                       # the lock plate
    cv.ellipse(24, 15.5, 1.0, 1.0, z=2.0, dome=0.0, mat=3)
    cv.stroke([(24, 16), (24, 18.2)], 0.7, z=2.0, dome=0.0, mat=3)
    return _prop(cv, [CHEST_WOOD, ramp('#3e3e44', dark=0.45, light=1.7), BRASS, ramp('#140e0a', dark=0.7, light=1.4)],
                 relief=1.0, cavity=0.4, shadow=0.45)


def spr_glowshroom():
    """A clump of glowing mushrooms: pale stems under domed caps that shade from a bright rim to a
    deeper heart, freckled with paler spots, the gills dark underneath. The caps glow."""
    rng = np.random.default_rng(173)
    w, h = 44, 28
    cv = Canvas(w, h, wrap=False, ground=-9)
    caps = [(10, 14, 7.5, 4.6), (24, 10, 9.5, 5.6), (36, 18, 5.5, 3.6), (31, 22, 3.6, 2.4)]
    for x, y, rx, ry in caps:                                                   # stems first
        cv.stroke([(x, h), (x + rng.normal(0, 0.6), y)], rx * 0.36, z=0.2, dome=0.8, taper=(1.2, 0.9), mat=1)
    for x, y, rx, ry in caps:
        cv.ellipse(x, y + ry * 0.5, rx * 0.9, 1.2, z=0.9, dome=0.3, mat=2)           # the gills
        cv.ellipse(x, y, rx, ry, z=1.0, dome=1.4, mat=0)
        for _ in range(int(rx)):                                                 # spots
            a, r = rng.uniform(np.pi, 2 * np.pi), rng.uniform(0.2, 0.75)
            cv.ellipse(x + np.cos(a) * rx * r, y + np.sin(a) * ry * r, 0.9, 0.7, z=2.4, dome=0.2, mat=3)
    glow = ((cv.mat == 0) | (cv.mat == 3)) & (cv.id > 0)
    return _prop(cv, [SHROOM, SHROOM_STEM, ramp('#1e4a44', dark=0.5, light=1.5), ramp('#c8fff0', dark=0.7, light=1.04)],
                 relief=1.0, cavity=0.3, shadow=0.35, em=glow * 0.85)


def spr_buoy():
    """A channel buoy riding the water: a red can with a white band, a lattice cage on top of it
    carrying its lamp (lit), a ring of ripples where it sits in the water."""
    w, h = 40, 64
    cx = 20
    cv = Canvas(w, h, wrap=False, ground=-9)
    for side in (-1, 1):                                                         # the cage
        cv.stroke([(cx + side * 7, 34), (cx + side * 3, 9)], 1.3, z=0.4, dome=0.6, mat=2)
    for y in (16, 24):
        cv.stroke([(cx - 6 + (24 - y) * 0.12, y), (cx + 6 - (24 - y) * 0.12, y)], 1.0, z=0.4, dome=0.5, mat=2)
    cv.box(cx - 5, 7, 10, 3, z=0.6, top=0.6, bevel=0.8, mat=2)                     # the lamp's platform
    cv.ellipse(cx, 4, 3.0, 3.4, z=1.0, dome=1.0, mat=3)                             # the lamp
    _lathe(cv, cx, [(32, 11), (36, 13), (52, 13), (58, 12)], z=0.8, dome=1.3, mat=0)   # the can
    _lathe(cv, cx, [(41, 13.2), (46, 13.2)], z=1.0, dome=1.3, mat=1)               # its white band
    a = np.linspace(0, 2 * np.pi, 30)                                           # ripples at the waterline
    cv.stroke(list(zip(cx + np.cos(a) * 17, 59 + np.sin(a) * 2.6)), 0.8, z=0.2, dome=0.2, mat=4)
    em = (cv.mat == 3) & (cv.id > 0)
    return _prop(cv, [BUOY_RED, BUOY_WHITE, ramp('#5a5e60', dark=0.4, light=1.5), LAMP,
                      ramp('#9ac0c8', dark=0.5, light=1.2)], relief=1.0, cavity=0.35, shadow=0.4, em=em * 1.0)


def spr_alien_egg():
    """A leathery alien egg standing on end: mottled and veined, a wet sheen on its upper side, and
    at its crown the slit of its four lips parting on a green glow. Something is nearly ready."""
    rng = np.random.default_rng(175)
    w, h = 32, 40
    cx = 16
    cv = Canvas(w, h, wrap=False, ground=-9)
    _lathe(cv, cx, [(4, 6), (8, 11), (18, 14), (30, 13.5), (37, 10), (40, 6)], z=0.0, dome=1.6, mat=0)
    for _ in range(9):                                                          # veins
        x, y = cx + rng.normal(0, 6), rng.uniform(10, 36)
        pts = [(x, y)]
        for _ in range(4):
            pts.append((pts[-1][0] + rng.normal(0, 2), pts[-1][1] + rng.uniform(-4, 1)))
        cv.stroke(pts, 0.8, z=1.7, dome=0.5, taper=(1.0, 0.4), mat=1)
    mott = smooth_noise(w, h, 4, rng, wrap=False) > 0.6
    cv.tone[mott & (cv.mat == 0)] -= 0.08
    for k in range(4):                                                          # the four lips at the crown
        a = k * np.pi / 2 + np.pi / 4
        cv.stroke([(cx, 7), (cx + np.cos(a) * 4.5, 7 + np.sin(a) * 2.6)], 1.0, z=1.9, dome=0.4, mat=1)
    cv.ellipse(cx, 7.5, 3.6, 2.4, z=1.8, dome=0.3, mat=2)                            # the glow between them
    light = cv.light(relief=1.0, cavity=0.35, shadow=0.45)
    sheen = (light > np.percentile(light[cv.id > 0], 92)) & (cv.mat == 0)          # wet highlights
    cv.tone[sheen] += 0.3
    em = ((cv.mat == 2) & (cv.id > 0)) * 1.0 + ((cv.mat == 1) & (cv.id > 0)) * 0.4   # the veins glow faintly
    return _prop(cv, [EGG, EGG_VEIN, EGG_GLOW], relief=1.0, cavity=0.35, shadow=0.45, em=em)


TEXTURES = {
    'grass': lambda n: (tex_grass(n), None),
    'hedge': lambda n: (tex_hedge(n), None),
    'dirt': lambda n: (tex_dirt(n), None),
    'gravel': lambda n: (tex_gravel(n), None),
    'wood_panel': lambda n: (tex_wood_panel(n), None),
    'water': lambda n: (tex_water(n), None),
    'shingle': lambda n: (tex_shingle(n), None),
    'cobble': lambda n: (tex_cobble(n), None),
    'beams': lambda n: (tex_beams(n), None),
    'rock': lambda n: (tex_rock(n), None),
    'rock_wet': lambda n: (tex_rock(n, 'rock_wet'), None),
    'rock_floor': lambda n: (tex_rock(n, 'rock_floor'), None),
    'snow_rock': lambda n: (tex_snow_rock(n), None),
    'ice': lambda n: (tex_ice(n), None),
    'snow': lambda n: (tex_snow(n), None),
    'sand': lambda n: (tex_sand(n), None),
    'plaster': lambda n: (tex_plaster(n), None),
    'plaster_white': lambda n: (tex_plaster(n, '#d8d4c4', '#6a6050', 0.45), None),
    'ivy': lambda n: (tex_ivy(n), None),
    'curtain': lambda n: (tex_curtain(n), None),
    'curtain_black': lambda n: (tex_curtain(n, '#24181c'), None),
    'acoustic': lambda n: (tex_acoustic(n), None),
    'ceiling_plaster': lambda n: (tex_plaster(n, '#a8a08a', '#4a4030', 0.3), None),
    'corrugated': lambda n: (tex_corrugated(n), None),
    'marble_dark': lambda n: (tex_marble_dark(n), None),
    'alien_rock': tex_alien_rock,
    'menhir': lambda n: (tex_menhir(n), None),
    'menhir_top': lambda n: (tex_menhir(n, top=True), None),
    'alien_ground': lambda n: (tex_alien_ground(n), None),
}
SPRITES = {'barrel': spr_barrel, 'broken_barrel': spr_broken_barrel, 'crate': spr_crate, 'fountain': spr_fountain,
           'rowboat': spr_rowboat, 'bench': spr_bench, 'flowers': spr_flowers, 'statue': spr_statue,
           'bed': spr_bed, 'wheelchair': spr_wheelchair, 'table': spr_table, 'chest': spr_chest,
           'glowshroom': spr_glowshroom, 'buoy': spr_buoy, 'alien_egg': spr_alien_egg, 'jaguar': spr_jaguar,
           'stone_cap': spr_stone_cap}
SPRITE_HEIGHT = {'stone_cap': 0.44}

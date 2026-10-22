"""Objects: things bigger than a prop, built in 3D out of flat panels - a food stand, a car, rock.

A sprite is a picture that always turns to face the camera: right for a person or a lamp, but it
makes anything big a cardboard cut-out with one view. An object is built the way Build-engine maps
built counters and cars out of flat "wall" and "floor" sprites: flat panels standing, lying and
sloped at any angle, textured with pixel art that is see-through wherever the thing is not - a car's
side is its outline, open above the hood - boxes of them, and among them, for the small things that
read best as pictures (bowls on a counter, a lantern), ordinary billboard sprites. The panels are
drawn in true perspective, depth-tested per pixel and lit like walls (Renderer._draw_panel), so
from any side you see the sides you should; billboards that stay small never give the trick away.

A scene places objects by name, position and turn:

    "objects": [{"type": "car", "x": 12.5, "y": 20.5, "angle": 90, "paint": "#8a2a2a"}]

Before anything else reads the scene, `expand` (called by prefabs.expand) turns every placement into
panels (the scene's `panels`, read only by the renderer), sprites, lights and contact shadows. An
object is laid out in its own units from its origin on the ground: x forward, y to its right, z up.
At angle 0 it faces east (+x), at 90 south - the camera's compass. OBJECTS lists the built-ins.

Rock - a `rock_wall` along the foot of a wall, a `boulder` - has its faces cut from one solid
block of stone (pixelart.cells3), so the stone runs on round a corner and each face takes the
light by the way it faces; see "rock" below.
"""
import functools
import json
import math

import numpy as np

from aquarium import ALGAE, CORALLINE, LIVE_ROCK
from pixelart import BAYER4, Canvas, cells3, noise3, ramp, rgb, table

TEXELS = 64                 # texels per world unit, as on the walls
PLACEMENT_KEYS = {'type', 'x', 'y', 'z', 'angle', 'scale', 'paint', 'lights', 'title', 'notes',
                  'rock', 'length', 'height', 'depth', 'pieces', 'trim', 'size', 'seed', 'plants', 'back', 'lining',
                  'count', 'spread', 'color', 'refract', 'glow', 'base', 'material', 'sides', 'radius', 'top', 'capital',
                  'sink', 'broken', 'width', 'flutes', 'doric', 'fill', 'rise', 'overhang', 'walls', 'inset',
                  'cover', 'chimney', 'plaster', 'gauge', 'ore', 'roots', 'piece', 'side', 'heel', 'ends', 'sail',
                  'band', 'lit', 'casts', 'teeth', 'spokes'}


# ------------------------------------------------------------------ parts

def quad(tex, tl, tr, bl, **kw):
    """A flat panel: its texture's top left, top right and bottom left corners, as seen from the
    side it reads from. `tex` is (rgba, emission). `translucent` draws it like glass - its texture's
    alpha as it is, over what is behind, writing no depth - and `opacity` scales that alpha; `back`
    dims its far side (the inside of a box) and `cull` hides it."""
    return dict(kw, part='panel', tex=tex, tl=tl, tr=tr, bl=bl)


def box(lo, hi, faces, **kw):
    """The panels of a box from corner `lo` to corner `hi`, one texture per named face - front
    (+x), back, right (+y), left, top, bottom - each read from outside; a face not named is open."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    corners = {
        'front': ((x1, y1, z1), (x1, y0, z1), (x1, y1, z0)),
        'back': ((x0, y0, z1), (x0, y1, z1), (x0, y0, z0)),
        'right': ((x0, y1, z1), (x1, y1, z1), (x0, y1, z0)),
        'left': ((x1, y0, z1), (x0, y0, z1), (x1, y0, z0)),
        'top': ((x1, y0, z1), (x1, y1, z1), (x0, y0, z1)),
        'bottom': ((x1, y1, z0), (x1, y0, z0), (x0, y1, z0)),
    }
    return [quad(tex, *corners[f], **kw) for f, tex in faces.items() if tex is not None]


def sprite(type_, dx, dy, z=0.0, **kw):
    return dict(kw, part='sprite', type=type_, dx=dx, dy=dy, z=z)


def light(dx, dy, z, radius, color, intensity=1.0):
    return {'part': 'light', 'dx': dx, 'dy': dy, 'z': z, 'radius': radius, 'color': list(color),
            'intensity': intensity}


def shadow(dx, dy, size, opacity=0.6):
    """A soft dark stamp on the ground under the object, as props get."""
    return {'part': 'shadow', 'dx': dx, 'dy': dy, 'size': size, 'opacity': opacity}


# ------------------------------------------------------------------ placing

def expand(scene):
    """The scene with every object placement turned into panels, sprites, lights and shadows. A
    scene without objects comes back as it is - the same object."""
    if not scene.get('objects'):
        return scene
    out = dict(scene)
    for key in ('sprites', 'lights', 'decals', 'panels'):
        out[key] = list(scene.get(key) or [])
    for pl in [q for p in scene['objects'] for q in (_lining(scene, p) if p.get('lining') else [p])]:
        if pl['type'] not in OBJECTS:
            raise KeyError(f"unknown object {pl['type']!r} - the built-ins are {', '.join(sorted(OBJECTS))}")
        X, Y, Z = float(pl['x']), float(pl['y']), float(pl.get('z', 0.0))
        a = math.radians(float(pl.get('angle', 0.0)))
        k = float(pl.get('scale', 1.0))
        ca, sa = math.cos(a), math.sin(a)

        def world(p):
            x, y, z = p
            return np.array([X + (x * ca - y * sa) * k, Y + (x * sa + y * ca) * k, Z + z * k])

        for part in _parts(pl):
            kind = part['part']
            if kind == 'panel':
                tl, tr, bl = world(part['tl']), world(part['tr']), world(part['bl'])
                pn = {key: val for key, val in part.items() if key not in ('part', 'tex', 'tl', 'tr', 'bl')}
                pn.update(o=tl, u=tr - tl, v=bl - tl, rgba=part['tex'][0], em=part['tex'][1], at=(X, Y, Z))
                if pl.get('fill'):
                    pn['fill'] = float(pl['fill'])
                if pl.get('casts'):
                    pn['casts'] = True
                if 'refract' in pn:
                    pn['refract'] = float(pn['refract']) * k
                out['panels'].append(pn)
            elif kind == 'sprite':
                p = world((part['dx'], part['dy'], part['z']))
                sp = {key: val for key, val in part.items() if key not in ('part', 'dx', 'dy', 'z')}
                sp.update(x=float(p[0]), y=float(p[1]), z=float(p[2]))
                if 'scale' in sp:
                    sp['scale'] = float(sp['scale']) * k
                out['sprites'].append(sp)
            elif kind == 'light':
                p = world((part['dx'], part['dy'], part['z']))
                out['lights'].append({'x': float(p[0]), 'y': float(p[1]), 'z': float(p[2]), 'radius': part['radius'] * k,
                                      'color': part['color'], 'intensity': part['intensity']})
            elif kind == 'shadow':
                p = world((part['dx'], part['dy'], 0.0))
                out['decals'].append({'tex': 'contact_shadow', 'surface': 'floor', 'x': float(p[0]), 'y': float(p[1]),
                                      'size': part['size'] * k, 'opacity': part['opacity']})
    out.pop('objects')
    return out


def _lining(scene, pl):
    """A rock wall placed with `lining` (map characters): one rock wall along every straight run of
    those cells' faces that look onto open ground (as fringes find them: ground with no wall a person
    could not step over), facing out from it - none where a shot's camera stands within its reach."""
    rows, legend = scene['map'], scene.get('legend', {})
    default = scene.get('default', {'floor': 'concrete_floor'})
    H, W = len(rows), max(len(r) for r in rows)
    grid = [r.ljust(W) for r in rows]

    def ground(x, y):
        if not (0 <= x < W and 0 <= y < H):
            return False
        spec = legend.get(grid[y][x], default)
        return ('wall' not in spec or float(spec.get('h', 1.0)) < 0.5) and not spec.get('void')
    faces = {}
    for y in range(H):
        for x in range(W):
            if grid[y][x] in pl['lining']:
                for d, ox, oy in (('n', 0, -1), ('s', 0, 1), ('w', -1, 0), ('e', 1, 0)):
                    if ground(x + ox, y + oy):
                        faces.setdefault((d, y if d in 'ns' else x), []).append(x if d in 'ns' else y)
    cams = [(float(c['x']), float(c['y'])) for c in [scene.get('camera') or {}] + list(scene.get('shots') or [])
            if 'x' in c and 'y' in c]
    reach = float(pl.get('depth', 0.7)) + 0.4
    out = []
    for (d, line), poss in sorted(faces.items()):
        poss = sorted(poss)
        a = poss[0]
        for p, q in zip(poss, poss[1:] + [None]):
            if q == p + 1:
                continue
            mid, L = (a + p + 1) / 2, p - a + 1
            x, y, ang = {'s': (mid, line + 1, 90), 'n': (mid, line, 270), 'e': (line + 1, mid, 0), 'w': (line, mid, 180)}[d]
            c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            if not any(abs((cy - y) * c - (cx - x) * s) < L / 2 + 0.3 and -0.2 < (cx - x) * c + (cy - y) * s < reach
                       for cx, cy in cams):
                run = {k: v for k, v in pl.items() if k != 'lining'}
                out.append(dict(run, x=x, y=y, angle=ang, length=L,
                                seed=int(pl.get('seed', 1)) * 7919 + 'nswe'.index(d) * 1009 + line * 131 + a))
            a = q
    return out


_BUILT = {}


def _parts(pl):
    """An object's parts, built once per placement and kept a while: cutting rock takes a moment,
    and the world and the renderer each expand a scene, and again for a shot with overrides."""
    key = json.dumps(pl, sort_keys=True, default=str)
    if key not in _BUILT:
        if len(_BUILT) >= 64:
            _BUILT.pop(next(iter(_BUILT)))
        _BUILT[key] = OBJECTS[pl['type']](pl)
    return _BUILT[key]


# ------------------------------------------------------------------ textures

def _texels(length):
    return max(2, int(round(length * TEXELS)))


def solid(w, h, base, rough=0.04, seed=0):
    """A plain painted panel, w x h texels, faintly mottled."""
    rng = np.random.default_rng(seed)
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.5, top=1.0, bevel=0.0)
    cv.noise(rough, cells=6, rng=rng)
    rgba = cv.paint([ramp(base)], cv.light(relief=0.4), dither=0.25, outline=0)
    return rgba.astype(np.float32), np.zeros((h, w), np.float32)


# ------------------------------------------------------------------ the noodle stand

LACQUER = ramp('#7a2a22', dark=0.35, light=1.35, warm=0.12)
WOOD_DARK = ramp('#4a3020', dark=0.35, light=1.3)
WOOD_PALE = ramp('#b08a5a', dark=0.45, light=1.25)
AWN_RED = ramp('#b8322c', dark=0.4, light=1.3)
AWN_CREAM = ramp('#e6dcc2', dark=0.5, light=1.12)
INDIGO = ramp('#283052', dark=0.4, light=1.4, cool=0.1)
CLOTH_WHITE = ramp('#e2ded2', dark=0.55, light=1.1)
SIGN_BOARD = ramp('#1c161c', dark=0.5, light=1.7)
CROCKERY = ramp('#d8d4c8', dark=0.45, light=1.15)
GLASS_DARK = ramp('#2a4a3a', dark=0.4, light=1.6)
NEON_PINK = (1.0, 0.36, 0.62)


def _finish(cv, ramps, em=None, relief=0.8, cavity=0.3, shadow=0.3, outline=1):
    rgba = cv.paint(ramps, cv.light(relief=relief, cavity=cavity, shadow=shadow), dither=0.25, outline=outline)
    return rgba.astype(np.float32), (np.zeros(rgba.shape[:2], np.float32) if em is None else em.astype(np.float32))


@functools.lru_cache(maxsize=None)
def _boards(w, h, seed, rails=True):
    """Lacquered boards standing side by side, a rail along the top and a kick rail at the foot."""
    rng = np.random.default_rng(seed)
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.2, top=1.0, bevel=0, mat=1)
    x = 0
    while x < w:
        bw = int(rng.integers(5, 8))
        cv.box(x, 0, bw - 1, h, z=0.6, top=1.0, bevel=0.6, mat=0, tone=float(rng.normal(0, 0.04)))
        x += bw
    if rails:
        cv.box(0, 0, w, 2, z=0.9, top=1.0, bevel=0.4, mat=1, tone=0.06)
        cv.box(0, h - 3, w, 3, z=0.9, top=1.0, bevel=0.4, mat=1, tone=-0.08)
    return _finish(cv, [LACQUER, WOOD_DARK])


@functools.lru_cache(maxsize=None)
def _counter_top(w, h):
    """The pale wooden counter, its planks running its length, worn paler where bowls go."""
    rng = np.random.default_rng(5)
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.2, top=1.0, bevel=0, mat=1)
    y = 0
    while y < h:
        ph = int(rng.integers(6, 9))
        cv.box(0, y, w, ph - 1, z=0.6, top=1.0, bevel=0.5, mat=0, tone=float(rng.normal(0, 0.035)))
        y += ph
    for _ in range(w // 6):                                        # grain
        gy, gx = rng.integers(0, h), rng.integers(0, w - 8)
        cv.stroke([(gx, gy), (gx + rng.integers(4, 9), gy)], 0.6, z=0.0, dome=0.2, mode='carve')
    return _finish(cv, [WOOD_PALE, WOOD_DARK], relief=0.5)


@functools.lru_cache(maxsize=None)
def _counter_back(w, h):
    """The cook's side of the counter: open shelves in the dark, bowls stacked, bottles."""
    rng = np.random.default_rng(9)
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.0, top=1.0, bevel=0, mat=1, tone=-0.25)
    for y in (h // 2 - 1, h - 3):                                  # the shelves
        cv.box(0, y, w, 2, z=0.8, top=1.0, bevel=0.4, mat=0)
    for x in range(3, w - 4, int(rng.integers(9, 12))):            # stacks of bowls, bottles
        if rng.random() < 0.6:
            for k in range(int(rng.integers(2, 4))):
                cv.ellipse(x + 2, h // 2 - 2 - k * 1.6, 2.6, 1.0, z=1.2 + k * 0.1, dome=0.5, mat=2)
        else:
            cv.stroke([(x + 1, h // 2 - 2), (x + 1, h // 2 - 6)], 1.4, z=1.2, dome=0.6, mat=3)
        if rng.random() < 0.7:
            cv.ellipse(x + 4, h - 4, 2.4, 1.0, z=1.2, dome=0.5, mat=2)
    for x in (0, w - 2):
        cv.box(x, 0, 2, h, z=0.9, top=1.0, bevel=0.3, mat=0)
    return _finish(cv, [LACQUER, WOOD_DARK, CROCKERY, GLASS_DARK], shadow=0.5)


def _stripes(w, h, stripe):
    """Awning canvas in red and cream stripes running down the texture, faintly domed."""
    cv = Canvas(w, h, wrap=False)
    for k, x in enumerate(range(0, w, stripe)):
        cv.box(x, 0, min(stripe, w - x), h, z=0.5, top=0.7, bevel=1.2, mat=k % 2)
    return cv


@functools.lru_cache(maxsize=None)
def _awning(w, h, stripe):
    cv = _stripes(w, h, stripe)
    cv.box(0, 0, w, 2, z=0.8, top=1.0, bevel=0.3, mode='over', mat=0, tone=-0.05)   # the bent front edge
    return _finish(cv, [AWN_RED, AWN_CREAM], relief=0.6)


@functools.lru_cache(maxsize=None)
def _valance(w, h, stripe):
    """The awning's hanging edge, its stripes in step with the awning's, cut in scallops."""
    cv = _stripes(w, h, stripe)
    rgba, em = _finish(cv, [AWN_RED, AWN_CREAM], relief=0.6)
    xx = np.arange(w) + 0.5
    ph = (xx % stripe) / stripe
    edge = (h - 2.2) + 2.2 * np.sin(np.pi * ph)                   # each stripe ends in a tongue
    rows = np.arange(h)[:, None] + 0.5
    rgba = rgba.copy()
    rgba[..., 3] *= (rows < edge[None, :])
    return rgba, em


@functools.lru_cache(maxsize=None)
def _noren(w, h, strips=5):
    """Split curtains of indigo cloth, a white crest on the middle one, hanging from the awning."""
    rng = np.random.default_rng(13)
    cv = Canvas(w, h, wrap=False)
    sw = w / strips
    for k in range(strips):
        x0 = int(round(k * sw))
        x1 = int(round((k + 1) * sw)) - 1
        cv.box(x0, 0, x1 - x0, h, z=0.6, top=0.8, bevel=1.0, mat=0, tone=float(rng.normal(0, 0.03)))
    cx, cy = w / 2, h * 0.52
    cv.ellipse(cx, cy, h * 0.3, h * 0.3, z=0.9, dome=0.2, mat=1)
    cv.ellipse(cx, cy, h * 0.17, h * 0.17, z=1.0, dome=0.2, mat=0)
    for k in (1, 3):                                               # brushed marks on two more
        x = (k + 0.5) * sw
        cv.stroke([(x - 1, h * 0.25), (x + 1, h * 0.75)], 1.1, z=0.9, dome=0.2, mat=1)
    rgba, em = _finish(cv, [INDIGO, CLOTH_WHITE], relief=0.5)
    rgba = rgba.copy()
    hem = h - 1 - (np.arange(w) % max(1, int(sw)) == 0)            # the corners of each strip ride up
    rgba[h - 1, hem < h - 1, 3] = 0.0
    return rgba, em


@functools.lru_cache(maxsize=None)
def _sign(w, h, seed=81):
    """A lit sign board: pink neon pseudo-letters on black, glowing."""
    rng = np.random.default_rng(seed)
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.6, top=0.8, bevel=0.8, mat=0)
    rgba, _ = _finish(cv, [SIGN_BOARD], relief=0.4)
    em = np.zeros((h, w), np.float32)
    n = max(3, w // 9)
    for k in range(n):
        x = 3 + k * (w - 6) / n
        for _ in range(3):
            a, b = rng.uniform(0, (w - 6) / n - 2, 2)
            if rng.random() < 0.5:
                pts = [(x + a, 2.5), (x + b, h - 2.5)]
            else:
                pts = [(x, 2.5 + a * (h - 5) / ((w - 6) / n)), (x + (w - 6) / n - 2, 2.5 + b * (h - 5) / ((w - 6) / n))]
            for t in np.linspace(0, 1, 16):
                px = int(round(pts[0][0] + (pts[1][0] - pts[0][0]) * t))
                py = int(round(pts[0][1] + (pts[1][1] - pts[0][1]) * t))
                if 0 <= px < w and 0 <= py < h:
                    rgba[py, px, :3] = NEON_PINK
                    em[py, px] = 1.0
    return rgba, em


def noodle_stand(pl):
    """A street-food stand for noodles: a counter of lacquered boards under a sloping striped
    awning on four posts, split indigo curtains hanging from its front edge, a lit sign on the
    roof, red lanterns at the front corners, shelves on the cook's side. Built from panels; the
    lanterns, bottles and steam are billboards. Faces +x: the customers stand there."""
    T = _texels
    d0, d1, half = -0.18, 0.16, 0.6                                  # the counter: back, front, half width
    top = 0.34
    parts = box((d0, -half, 0.0), (d1, half, top),
                {'front': _boards(T(2 * half), T(top), 1), 'back': _counter_back(T(2 * half), T(top)),
                 'right': _boards(T(d1 - d0), T(top), 2), 'left': _boards(T(d1 - d0), T(top), 3)})
    slab = (d0 - 0.02, -half - 0.02, top), (d1 + 0.1, half + 0.02, top + 0.03)       # the counter top, overhanging
    edge = _solid_cached(T(2 * half + 0.04), 2, '#5a3a24')
    parts += box(*slab, {'top': _counter_top(T(2 * half + 0.04), T(slab[1][0] - slab[0][0])),
                         'front': edge, 'back': edge, 'right': _solid_cached(T(slab[1][0] - slab[0][0]), 2, '#5a3a24'),
                         'left': _solid_cached(T(slab[1][0] - slab[0][0]), 2, '#5a3a24'), 'bottom': edge})
    xf, xb, zf, zb = 0.44, -0.22, 0.86, 1.02                          # the awning's front and back edges
    for x, z in ((d1 - 0.02, zf + (zb - zf) * (xf - d1 + 0.02) / (xf - xb)), (d0 + 0.02, zb - 0.01)):
        for y in (-half + 0.03, half - 0.03):                         # the posts
            parts += box((x - 0.018, y - 0.018, top + 0.03), (x + 0.018, y + 0.018, z),
                         {f: _solid_cached(3, T(z - top), '#3a2618') for f in ('front', 'back', 'right', 'left')})
    aw = half + 0.08
    stripe = 7
    parts.append(quad(_awning(T(2 * aw), T(math.hypot(xf - xb, zb - zf)), stripe),
                      (xf, -aw, zf), (xf, aw, zf), (xb, -aw, zb), back=0.85))                 # the awning
    vh = 0.1
    val = _valance(T(2 * aw), T(vh), stripe)                         # read from the front: flipped to
    parts.append(quad((val[0][:, ::-1], val[1][:, ::-1]), (xf, aw, zf), (xf, -aw, zf), (xf, aw, zf - vh),
                      back=0.85))                                     # keep step with the awning's stripes
    for y, sgn in ((aw, 1), (-aw, -1)):                              # its sides, along the slope
        tl, tr = ((xb, y, zb), (xf, y, zf)) if sgn > 0 else ((xf, y, zf), (xb, y, zb))
        parts.append(quad(_valance(T(math.hypot(xf - xb, zb - zf)), T(vh), stripe), tl, tr,
                          (tl[0], tl[1], tl[2] - vh), back=0.85))
    nh = 0.2
    parts.append(quad(_noren(T(2 * half), T(nh)), (xf - 0.03, half, zf - 0.02), (xf - 0.03, -half, zf - 0.02),
                      (xf - 0.03, half, zf - 0.02 - nh), back=0.7))                          # the curtains
    sx0, sx1, sz0, sz1 = -0.17, -0.11, 1.012, 1.17                    # the sign on the roof
    face = _sign(T(0.8), T(sz1 - sz0))
    parts += box((sx0, -0.4, sz0), (sx1, 0.4, sz1), {'front': face, 'back': face, 'top': _solid_cached(T(0.8), 4, '#1c161c'),
                                                     'right': _solid_cached(4, T(sz1 - sz0), '#1c161c'),
                                                     'left': _solid_cached(4, T(sz1 - sz0), '#1c161c')})
    lit = pl.get('lights', True)
    for y in (-half + 0.02, half - 0.02):                             # lanterns at the front corners
        parts.append(sprite('red_lantern', xf - 0.02, y, zf - 0.2))
        if lit:
            parts.append(light(xf + 0.05, y, zf - 0.14, 1.4, (1.0, 0.42, 0.28), 0.6))
    if lit:                                                           # a warm pool under the awning
        parts.append(light(0.12, 0.0, 0.74, 3.2, (1.0, 0.72, 0.45), 1.2))
    ct = top + 0.03                                                   # on the counter: bowls served
    parts += [sprite('noodle_bowl', d1 + 0.03, -0.36, ct), sprite('condiments', d1 + 0.01, -0.08, ct),
              sprite('noodle_bowl', d1 + 0.04, 0.38, ct)]
    parts += [sprite('stock_pot', d0 + 0.07, -0.3, ct), sprite('steam', d0 + 0.07, -0.3, ct + 0.09, scale=0.5),
              sprite('bowl_stack', d0 + 0.08, 0.14, ct), sprite('bottles', d0 + 0.06, 0.42, ct, scale=0.12)]
    for y in (-0.38, 0.0, 0.38):                                       # stools for the customers
        parts.append(sprite('bar_stool', d1 + 0.3, y, 0.0, scale=0.22))
    parts.append(shadow(0.0, 0.0, 1.5, 0.55))
    return parts


@functools.lru_cache(maxsize=None)
def _solid_cached(w, h, base):
    return solid(w, h, base)


# ------------------------------------------------------------------ the car

CHROME = ramp('#9aa0a8', dark=0.4, light=1.5, cool=0.1)
TRIM = ramp('#222428', dark=0.6, light=1.9)
RUBBER = ramp('#1e1e22', dark=0.6, light=1.9)
UPHOLSTERY = ramp('#3a3036', dark=0.5, light=1.6)
AMBER = ramp('#e89a2a', dark=0.5, light=1.15)
TAIL_RED = ramp('#b8201a', dark=0.45, light=1.3)
LAMP = ramp('#e8e6d8', dark=0.55, light=1.1)
PLATE = ramp('#d8d4c0', dark=0.5, light=1.1)
GLASS_TINT = np.array([0.16, 0.2, 0.26], np.float32)

# the car in its own units: x along it (forward +), z up. Its half length and half width; the
# body's underside, the belt (where hood, trunk and window sills are: the body 60%, the glass 40%)
# and the roof; the windscreen's foot and head and the rear window's, along x; the B pillar; the
# wheels' x, their radius, the tyres' inner and outer y and the radius of the arches cut for them.
CAR = dict(L=0.8, W=0.3, z0=0.078, belt=0.313, roof=0.47, wind=(0.29, 0.155), rear=(-0.43, -0.325),
           bpillar=-0.05, wheels=(0.52, -0.52), r=0.105, tyre=(0.192, 0.262), arch=0.116)


def _poly(w, h, pts):
    """A mask of the polygon `pts` (texel coordinates) on a w x h grid."""
    from PIL import Image, ImageDraw
    im = Image.new('L', (w, h), 0)
    ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    return np.asarray(im) > 127


def _side_geometry(w, h):
    """Where things are on the car's side texture (column 0 at the back, row 0 at the roof):
    a function from x, z to texel, and the masks of the cabin, its windows and the wheel arches."""
    c = CAR
    cx = lambda x: (x + c['L']) / (2 * c['L']) * w                      # noqa: E731
    rz = lambda z: (c['roof'] - z) / (c['roof'] - c['z0']) * h           # noqa: E731
    belt = rz(c['belt'])
    (wf, wt), (rb, rt) = c['wind'], c['rear']
    cabin = _poly(w, h, [(cx(rb), belt), (cx(rt), 0), (cx(wt), 0), (cx(wf), belt)])
    slope_a = (cx(wf) - cx(wt)) / belt
    slope_c = (cx(rt) - cx(rb)) / belt
    bpil = cx(c['bpillar'])
    top, sill = 1.5, belt - 1.2
    front = _poly(w, h, [(bpil + 1.2, top), (cx(wt) + slope_a * top - 2.0, top),
                         (cx(wt) + slope_a * sill - 2.0, sill), (bpil + 1.2, sill)])
    back = _poly(w, h, [(cx(rt) - slope_c * top + 3.2, top), (bpil - 1.2, top), (bpil - 1.2, sill),
                        (cx(rt) - slope_c * sill + 3.2, sill)])
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    arches = np.zeros((h, w), bool)
    for xw in c['wheels']:
        arches |= np.hypot(xx - cx(xw), (yy - rz(c['r'])) * (w / (2 * c['L'])) / (h / (c['roof'] - c['z0']))) \
            < c['arch'] * w / (2 * c['L'])
    return cx, rz, cabin, front | back, arches


@functools.lru_cache(maxsize=None)
def _car_side(paint, lit):
    """The car's right side, front to the right: the body with its doors, handles, trim and the
    wheel arches cut out, and above the belt the cabin's pillars, its windows left open for the
    glass behind them; see-through over the hood and the trunk."""
    w, h = _texels(2 * CAR['L']), _texels(CAR['roof'] - CAR['z0'])
    cx, rz, cabin, windows, arches = _side_geometry(w, h)
    belt = int(round(rz(CAR['belt'])))
    cv = Canvas(w, h, wrap=False)
    cv.box(0, belt, w, h - belt, z=0.6, top=1.0, bevel=1.2, mat=0)                       # the body
    cv.put(np.arange(h), np.arange(w), cabin & ~windows, 0.7, mat=0)                      # the pillars
    z0, zb, bp = CAR['z0'], CAR['belt'], CAR['bpillar']
    trim = int(round(rz(z0 + 0.4 * (zb - z0))))
    cv.box(0, trim, w, 1, z=0.75, top=0.6, bevel=0.3, mat=1)                              # a rubbing strip
    cv.box(0, h - 2, w, 2, z=0.5, top=0.6, bevel=0.3, mat=1)                              # the sill below
    for x in (CAR['wind'][0] - 0.025, bp, CAR['rear'][0] + 0.09):                         # door seams
        cv.stroke([(cx(x), belt + 0.5), (cx(x), h - 2.5)], 0.6, z=0, dome=0.3, mode='carve')
    for x in (bp + 0.075, CAR['rear'][0] + 0.13):                                        # handles, at each
                                                                                          # door's back edge
        cv.box(cx(x) - 1.5, rz(zb - 0.035), 3, 1, z=0.9, top=0.6, bevel=0.2, mat=2)
    for c0, c1 in ((0, 2), (w - 2, w)):                                                   # bumper ends
        cv.box(c0, rz(z0 + 0.13), c1 - c0, rz(z0 + 0.03) - rz(z0 + 0.13), z=0.8, top=0.8, bevel=0.3, mat=1)
    cv.box(w - 4, rz(zb - 0.075), 2, 1, z=0.9, top=0.5, bevel=0.2, mat=3)                 # side markers
    cv.box(2, rz(zb - 0.075), 2, 1, z=0.9, top=0.5, bevel=0.2, mat=4)
    rgba, em = _finish(cv, [ramp(paint, dark=0.35, light=1.45), TRIM, CHROME, AMBER, TAIL_RED], relief=0.7)
    rgba = rgba.copy()
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    lip = np.zeros((h, w), bool)
    for xw in CAR['wheels']:                                                              # the arches' dark lips
        d = np.hypot(xx - cx(xw), yy - rz(CAR['r']))
        lip |= (d < CAR['arch'] * w / (2 * CAR['L']) + 1.0) & (yy > belt)
    rgba[lip & ~arches, :3] *= 0.45
    rgba[..., 3] *= ~arches
    rgba[:belt][~cabin[:belt], 3] = 0.0                                                 # open above hood and trunk
    rgba[windows, 3] = 0.0
    corner = (xx > w - 1.6) & (yy < belt + 1.6) | (xx < 1.6) & (yy < belt + 1.6)      # rounded ends
    rgba[corner & (yy > belt - 0.5) & (yy < belt + 1), 3] = 0.0
    return rgba, em


@functools.lru_cache(maxsize=None)
def _car_end(paint, front, lit):
    """The car's nose or tail below the belt - headlamps, grille, bumper and plate, or the tail
    lamps - and see-through above, where the windscreen and the rear window stand back."""
    w, h = _texels(2 * CAR['W']), _texels(CAR['roof'] - CAR['z0'])
    rz = lambda z: (CAR['roof'] - z) / (CAR['roof'] - CAR['z0']) * h     # noqa: E731
    belt = int(round(rz(CAR['belt'])))
    cv = Canvas(w, h, wrap=False)
    z0, zb = CAR['z0'], CAR['belt']
    cv.box(0, belt, w, h - belt, z=0.6, top=1.0, bevel=1.2, mat=0)
    cv.box(0, rz(z0 + 0.075), w, rz(z0 + 0.01) - rz(z0 + 0.075), z=0.9, top=0.8, bevel=0.5, mat=1)   # the bumper
    cv.box(w / 2 - 4, rz(z0 + 0.067), 8, 3, z=1.0, top=0.6, bevel=0.3, mat=2)                     # the plate
    em = np.zeros((h, w), np.float32)
    lamp_top, lamp_foot = zb - 0.015, zb - (0.08 if front else 0.09)
    if front:
        cv.box(9, rz(zb - 0.025), w - 18, rz(zb - 0.11) - rz(zb - 0.025), z=0.4, top=0.6, bevel=0.4, mat=1)  # grille
        for k in range(3):
            cv.box(10, rz(zb - 0.035) + k * 2, w - 20, 1, z=0.7, top=0.5, bevel=0.2, mat=3)
        lamps = [(2, 8), (w - 8, w - 2)]
        for c0, c1 in lamps:
            cv.box(c0, rz(lamp_top), c1 - c0, rz(lamp_foot) - rz(lamp_top), z=1.0, top=1.2, bevel=1.0, mat=4)
        ramps = [ramp(paint, dark=0.35, light=1.45), TRIM, PLATE, CHROME, LAMP]
    else:
        cv.stroke([(1, belt + 1.5), (w - 1, belt + 1.5)], 0.6, z=0, dome=0.3, mode='carve')  # the trunk lid
        lamps = [(1, 8), (w - 8, w - 1)]
        for c0, c1 in lamps:
            cv.box(c0, rz(lamp_top), c1 - c0, rz(lamp_foot) - rz(lamp_top), z=1.0, top=1.0, bevel=0.8, mat=4)
        ramps = [ramp(paint, dark=0.35, light=1.45), TRIM, PLATE, CHROME, TAIL_RED]
    rgba, _ = _finish(cv, ramps, relief=0.7)
    rgba = rgba.copy()
    if lit or not front:                                                                   # the lamps glow
        for c0, c1 in lamps:
            em[int(rz(lamp_top)):int(rz(lamp_foot)), c0:c1] = 0.9 if lit else 0.35
    rgba[:belt, :, 3] = 0.0
    return rgba, em


@functools.lru_cache(maxsize=None)
def _car_top(paint, w, h, creases=False, seam=None):
    """Hood, trunk lid or roof: paint catching the light, the hood's two creases, a seam."""
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.6, top=1.0, bevel=1.4, mat=0)
    if creases:
        for c in (w * 0.28, w * 0.72):
            cv.stroke([(c, 1), (c, h - 1)], 0.6, z=0.75, dome=0.6, mat=0, tone=0.08)
    if seam is not None:
        cv.stroke([(1, seam), (w - 1, seam)], 0.6, z=0, dome=0.3, mode='carve')
    return _finish(cv, [ramp(paint, dark=0.35, light=1.5)], relief=0.6)


@functools.lru_cache(maxsize=None)
def _glass(w, h, mask_key=None):
    """Dark glass, a pale streak of reflection across it and a rubber seal round its edge; see-
    through (alpha under 1) everywhere but the seal. `mask_key` cuts it to the side windows."""
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    rgba = np.zeros((h, w, 4), np.float32)
    streak = np.abs((xx / w) * 1.4 - (yy / h) - 0.25) < 0.12
    rgba[..., :3] = GLASS_TINT + streak[..., None] * 0.22
    rgba[..., 3] = 0.62 + streak * 0.1
    if mask_key is None:
        seal = (xx < 1) | (xx > w - 1) | (yy < 1) | (yy > h - 1)
        rgba[seal, :3] = (0.05, 0.05, 0.06)
        rgba[seal, 3] = 1.0
    else:
        _, _, _, windows, _ = _side_geometry(*mask_key)
        x0 = int(np.floor(mask_key[0] * (CAR['rear'][0] + CAR['L']) / (2 * CAR['L'])))
        win = windows[:, x0:x0 + w][:h]
        rgba[..., 3] *= win
    return rgba, np.zeros((h, w), np.float32)


@functools.lru_cache(maxsize=None)
def _seat(w, h):
    """Upholstery: a cushion or a seat back, its seams stitched."""
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.6, top=1.4, bevel=1.5, mat=0)
    for c in range(3, w - 2, 4):
        cv.stroke([(c, 1), (c, h - 1)], 0.5, z=0, dome=0.3, mode='carve')
    return _finish(cv, [UPHOLSTERY], relief=0.8)


@functools.lru_cache(maxsize=None)
def _steering(n):
    """A steering wheel, face on: a dark rim and three spokes, see-through between."""
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    r = np.hypot(xx - n / 2, yy - n / 2)
    rim = (r < n / 2) & (r > n / 2 - 1.3)
    spokes = (r < n / 2 - 1) & (((np.abs(yy - n / 2) < 0.7) & True) | ((np.abs(xx - n / 2) < 0.7) & (yy > n / 2)))
    hub = r < 1.6
    rgba = np.zeros((n, n, 4), np.float32)
    on = rim | spokes | hub
    rgba[on, :3] = (0.09, 0.09, 0.1)
    rgba[rim & (yy < n / 2), :3] = (0.16, 0.16, 0.18)
    rgba[on, 3] = 1.0
    return rgba, np.zeros((n, n), np.float32)


@functools.lru_cache(maxsize=None)
def _wheel_face(n, inner=False):
    """A wheel side on: the tyre's black sidewall, the rim and the hubcap - or just dark rubber
    for its inner face. See-through outside the disc."""
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    r = np.hypot(xx - n / 2, yy - n / 2) / (n / 2)
    rgba = np.zeros((n, n, 4), np.float32)
    disc = r < 1.0
    rgba[disc, :3] = (0.08, 0.08, 0.09)
    if not inner:
        rim = r < 0.62
        rgba[rim, :3] = (0.55, 0.57, 0.6)
        rgba[(r < 0.62) & (r > 0.5), :3] = (0.3, 0.31, 0.33)
        rgba[r < 0.24, :3] = (0.72, 0.74, 0.76)
        lit = disc & (yy < n / 2) & (xx < n / 2) & (r > 0.7)
        rgba[lit, :3] = (0.16, 0.16, 0.17)
    rgba[disc, 3] = 1.0
    return rgba, np.zeros((n, n), np.float32)


@functools.lru_cache(maxsize=None)
def _well(n):
    """The dark of a wheel well, behind the tyre: a disc."""
    yy, xx = np.mgrid[0:n, 0:n] + 0.5
    rgba = np.zeros((n, n, 4), np.float32)
    disc = np.hypot(xx - n / 2, yy - n / 2) < n / 2
    rgba[disc, :3] = (0.035, 0.035, 0.04)
    rgba[disc, 3] = 1.0
    return rgba, np.zeros((n, n), np.float32)


@functools.lru_cache(maxsize=None)
def _floor_pan(w, h):
    """The car's underside, dark, holed where the wheels come through it (columns across the car,
    rows from its nose back): what is seen through a wheel arch past the tyre, not the street."""
    c = CAR
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    x = c['L'] - yy / h * 2 * c['L']
    y = -c['W'] + xx / w * 2 * c['W']
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = 0.045
    rgba[..., 3] = 1.0
    for xw in c['wheels']:
        hole = (np.abs(x - xw) < c['arch'] + 0.01) & (np.abs(y) > c['tyre'][0] - 0.015)
        rgba[hole, 3] = 0.0
    return rgba, np.zeros((h, w), np.float32)


@functools.lru_cache(maxsize=None)
def _under(w, h, edge=0.3):
    """The shadow under a thing: dark, see-through, fading out over `edge` of the way to its rim."""
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    d = np.minimum(np.minimum(xx, w - xx) / (w * edge / 2), np.minimum(yy, h - yy) / (h * edge / 2))
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., 3] = 0.88 * np.clip(d, 0, 1) ** 1.5
    return rgba, np.zeros((h, w), np.float32)


@functools.lru_cache(maxsize=None)
def _tread(w, h):
    yy, xx = np.mgrid[0:h, 0:w]
    rgba = np.ones((h, w, 4), np.float32)
    rgba[..., :3] = np.where(((xx + yy) % 3 == 0)[..., None], 0.05, 0.11)
    return rgba, np.zeros((h, w), np.float32)


def car(pl):
    """A saloon car, parked: built the way the user laid it out - the overall box, its sides the
    car's outline (open above the hood and the trunk, the windows open for glass), the hood and
    the trunk lid flat across it half way up, the roof on top, glass windows you can see the
    seats and the steering wheel through, and four wheels set in under the body. `paint` is its
    colour; `lights` true turns its headlamps on (with light), else only the tail lamps glow."""
    c = CAR
    paint = str(pl.get('paint', '#7a2a26'))
    lit = bool(pl.get('lights', False))
    L, W, z0, belt, roof = c['L'], c['W'], c['z0'], c['belt'], c['roof']
    (wf, wt), (rb, rt) = c['wind'], c['rear']
    side = _car_side(paint, lit)
    parts = box((-L, -W, z0), (L, W, roof),
                {'right': side, 'left': (side[0][:, ::-1], side[1][:, ::-1]),
                 'front': _car_end(paint, True, lit), 'back': _car_end(paint, False, lit)}, back=0.4)
    tw = _texels(2 * W)
    parts.append(quad(_car_top(paint, tw, _texels(L - wf), creases=True), (L, -W, belt), (L, W, belt), (wf, -W, belt)))   # hood
    parts.append(quad(_car_top(paint, tw, _texels(rb + L), seam=_texels(rb + L) - 2), (rb, -W, belt), (rb, W, belt),
                      (-L, -W, belt)))                                                                                    # trunk
    parts.append(quad(_car_top(paint, tw, _texels(wt - rt)), (wt, -W, roof), (wt, W, roof), (rt, -W, roof)))         # roof
    gw = 0.004                                                                                                  # glass just inside
    parts.append(quad(_glass(tw, _texels(math.hypot(wf - wt, roof - belt))), (wt, W - gw, roof), (wt, -W + gw, roof),
                      (wf, W - gw, belt), translucent=True))                                                     # windscreen
    parts.append(quad(_glass(tw, _texels(math.hypot(rt - rb, roof - belt))), (rt, -W + gw, roof), (rt, W - gw, roof),
                      (rb, -W + gw, belt), translucent=True))                                                    # rear window
    sw, sh = _texels(2 * L), _texels(roof - z0)
    gw_cols = int(round(sw * (wf - rb) / (2 * L)))
    belt_row = int(round((roof - belt) / (roof - z0) * sh))
    win = _glass(gw_cols, belt_row, (sw, sh))
    parts.append(quad(win, (rb, W - gw, roof), (wf, W - gw, roof), (rb, W - gw, belt), translucent=True))
    parts.append(quad((win[0][:, ::-1], win[1]), (wf, -W + gw, roof), (rb, -W + gw, roof), (wf, -W + gw, belt),
                      translucent=True))
    # inside: the floor, the dashboard, the seats and the wheel
    zf, bp = z0 + 0.085, c['bpillar']
    zs = zf + 0.065                                                                           # seat cushions
    parts.append(quad(_solid_cached(tw, _texels(wf - rb), '#1e1a1c'), (wf, -W, zf), (wf, W, zf), (rb, -W, zf)))
    parts += box((wf - 0.07, -W + 0.01, belt - 0.06), (wf, W - 0.01, belt + 0.01),
                 {'top': _solid_cached(tw, 5, '#26222a'), 'back': _solid_cached(tw, 5, '#1e1a20')})
    for y in (-0.14, 0.14):                                                                   # the front seats
        parts += box((bp + 0.08, y - 0.09, zf), (bp + 0.22, y + 0.09, zs), {'top': _seat(12, 9), 'front': _seat(12, 4)})
        parts.append(quad(_seat(12, 13), (bp + 0.045, y + 0.085, belt + 0.11), (bp + 0.045, y - 0.085, belt + 0.11),
                          (bp + 0.085, y + 0.085, zs)))
    parts += box((rb + 0.08, -W + 0.03, zf), (rb + 0.22, W - 0.03, zs), {'top': _seat(36, 9), 'front': _seat(36, 4)})
    parts.append(quad(_seat(36, 13), (rb + 0.05, W - 0.03, belt + 0.1), (rb + 0.05, -W + 0.03, belt + 0.1),
                      (rb + 0.085, W - 0.03, zs)))
    parts.append(quad(_steering(7), (wf - 0.115, -0.19, belt + 0.045), (wf - 0.115, -0.09, belt + 0.045),
                      (wf - 0.085, -0.19, belt - 0.04)))                                       # the wheel
    # the wheels, set in from the sides: a face, a dark inner face, and the tread in eight flats
    r, (yi, yo) = c['r'], c['tyre']
    n = _texels(2 * r)
    for xw in c['wheels']:
        for s in (1, -1):
            out_y, in_y = s * yo, s * yi
            if s > 0:
                parts.append(quad(_wheel_face(n), (xw - r, out_y, 2 * r), (xw + r, out_y, 2 * r), (xw - r, out_y, 0.0)))
                parts.append(quad(_wheel_face(n, True), (xw + r, in_y, 2 * r), (xw - r, in_y, 2 * r), (xw + r, in_y, 0.0)))
            else:
                parts.append(quad(_wheel_face(n), (xw + r, out_y, 2 * r), (xw - r, out_y, 2 * r), (xw + r, out_y, 0.0)))
                parts.append(quad(_wheel_face(n, True), (xw - r, in_y, 2 * r), (xw + r, in_y, 2 * r), (xw - r, in_y, 0.0)))
            R, wy = c['arch'] + 0.025, s * (yi - 0.006)               # the wheel well behind it
            ends = (xw - R, xw + R) if s > 0 else (xw + R, xw - R)
            parts.append(quad(_well(_texels(2 * R)), (ends[0], wy, r + R), (ends[1], wy, r + R), (ends[0], wy, r - R)))
            hi, lo = max(out_y, in_y), min(out_y, in_y)
            for k in range(8):
                a0, a1 = math.radians(k * 45 + 22.5), math.radians(k * 45 + 67.5)
                p0 = (xw + r * math.cos(a0), r + r * math.sin(a0))
                p1 = (xw + r * math.cos(a1), r + r * math.sin(a1))
                parts.append(quad(_tread(5, 5), (p0[0], hi, p0[1]), (p1[0], hi, p1[1]), (p0[0], lo, p0[1])))
    if lit:                                                           # the headlamps' pools on the road
        for y in (-W + 0.08, W - 0.08):
            parts.append(light(L + 0.3, y, belt - 0.05, 2.6, (1.0, 0.92, 0.75), 0.9))
    zp = z0 + 0.002                                                   # its floor pan
    parts.append(quad(_floor_pan(tw, _texels(2 * L)), (L, -W, zp), (L, W, zp), (-L, -W, zp)))
    u, v = L + 0.08, W + 0.07                                         # the dark under it, soft-edged
    parts.append(quad(_under(40, 16), (u, -v, 0.004), (u, v, 0.004), (-u, -v, 0.004), translucent=True))
    return parts


# ------------------------------------------------------------------ rock

# What each kind of rock is made of: ramps for the stone, for a crust on it (lichen, coralline)
# and for weed (moss, algae, snow) where it faces up; the size of its masses and of the chips on
# them (x, y, z in units - flat cells lie in beds, as sandstone's do); the light painted on it -
# a direction in the world, from the south-west and above (nearly straight down, through water),
# the same for every rock in a scene however it is turned - and how dark and how bright that takes it; how much of it is crusted, weedy and pitted, and how
# nearly level a face must be for the weed to settle (`up`); which materials glow and how much;
# and what grows on top: (prop, lowest, highest), heights in units.
SNOW = ramp(['#8e9ab2', '#a8b4ca', '#c2ccdc', '#d8e0ea', '#eaeff5', '#f8fafc'])
CAVE = ramp('#4a4652', dark=0.3, light=1.5, cool=0.12)
ROCKS = {
    'stone': dict(ramps=[ramp('#6e6a64', dark=0.3, light=1.45), ramp('#7a7866', dark=0.35, light=1.3),
                         ramp('#4e6a32', dark=0.35, light=1.35)],
                  mass=(0.9, 0.9, 0.7), chip=(0.24, 0.24, 0.2), key=(-0.4, 0.45, 0.8), shade=(0.3, 0.62),
                  crust=0.68, weed=0.62, pores=0.0,
                  plants=[('fern', 0.22, 0.34), ('grass_tuft', 0.16, 0.26)]),
    'reef': dict(ramps=[LIVE_ROCK, CORALLINE, ALGAE], mass=(0.8, 0.8, 0.55), chip=(0.2, 0.2, 0.16),
                 key=(-0.25, 0.3, 0.92), shade=(0.17, 0.7), crust=0.62, weed=0.66, pores=0.45,
                 plants=[('sea_fan', 0.32, 0.52), ('staghorn_coral', 0.24, 0.38), ('tube_sponge', 0.22, 0.36),
                         ('anemone', 0.16, 0.24), ('brain_coral', 0.14, 0.22)]),
    'sandstone': dict(ramps=[ramp('#b0704a', dark=0.35, light=1.35, warm=0.1), ramp('#c89a6a', dark=0.4, light=1.25),
                             ramp('#6a6a3a', dark=0.35, light=1.3)],
                      mass=(1.2, 1.2, 0.22), chip=(0.4, 0.4, 0.07), key=(-0.4, 0.45, 0.8), shade=(0.3, 0.62),
                      crust=0.62, weed=0.8, pores=0.0, plants=[('dry_tuft', 0.14, 0.22)]),
    'canyon': dict(ramps=[ramp('#b8683e', dark=0.38, light=1.4, warm=0.1), ramp('#e6c696', dark=0.45, light=1.18),
                          ramp('#6a6a3a', dark=0.35, light=1.3)],
                   mass=(1.4, 1.4, 0.3), chip=(0.45, 0.45, 0.09), key=(-0.22, 0.26, 0.94), shade=(0.46, 0.52),
                   crust=0.9, weed=0.85, pores=0.0, strata=(1.4, 0.4), varnish=0.16, plants=[('dry_tuft', 0.14, 0.22)]),
    'marble': dict(ramps=[ramp('#d6ccb6', dark=0.36, light=1.24, warm=0.08), ramp('#d4b688', dark=0.52, light=1.2),
                          ramp('#8c9a68', dark=0.38, light=1.3)],
                   mass=(2.4, 2.4, 1.4), chip=(0.3, 0.3, 0.2), key=(-0.4, 0.45, 0.8), shade=(0.46, 0.5),
                   crust=0.8, weed=0.74, up=0.6, pores=0.0, courses=0.5, cracks=0.1, plants=[('dry_tuft', 0.14, 0.22)]),
    'island': dict(ramps=[ramp(['#4a4450', '#605862', '#786e70', '#908480', '#a89c94', '#c2b6aa']),
                          ramp('#6a5a48', dark=0.4, light=1.3), ramp('#4e6a3a', dark=0.4, light=1.3)],
                   mass=(2.6, 2.6, 1.2), chip=(0.5, 0.5, 0.3), key=(-0.3, 0.35, 0.88), shade=(0.36, 0.6),
                   crust=0.82, weed=0.8, up=0.7, pores=0.0, strata=(0.9, 0.18), density=0.5,
                   plants=[('grass_tuft', 0.16, 0.26), ('fern', 0.2, 0.3)]),
    'ashlar': dict(ramps=[ramp('#aaa189', dark=0.32, light=1.4), ramp('#8f8c6e', dark=0.35, light=1.3),
                          ramp('#56683a', dark=0.35, light=1.35)],
                   mass=(2.0, 2.0, 1.2), chip=(0.3, 0.3, 0.2), key=(-0.4, 0.45, 0.8), shade=(0.36, 0.56),
                   crust=0.74, weed=0.66, up=0.5, pores=0.0, courses=0.42,
                   plants=[('fern', 0.22, 0.34), ('grass_tuft', 0.16, 0.26)]),
    'snow': dict(ramps=[ramp('#686c76', dark=0.3, light=1.45, cool=0.16), ramp('#7c7a6c', dark=0.35, light=1.3), SNOW],
                 mass=(0.9, 0.9, 0.7), chip=(0.24, 0.24, 0.2), key=(-0.4, 0.45, 0.8), shade=(0.3, 0.62),
                 crust=0.7, weed=0.3, up=0.42, pores=0.0, plants=[]),
    'cave': dict(ramps=[CAVE, ramp('#8e877a', dark=0.4, light=1.25), ramp('#3c5236', dark=0.35, light=1.35)],
                 mass=(0.8, 0.8, 0.6), chip=(0.18, 0.18, 0.15), key=(-0.3, 0.35, 0.88), shade=(0.22, 0.62),
                 crust=0.64, weed=0.72, pores=0.35, plants=[('glowshroom', 0.12, 0.2), ('mushrooms', 0.1, 0.16)]),
    'lumen': dict(ramps=[CAVE, ramp('#8e877a', dark=0.4, light=1.25), ramp('#36c8a6', dark=0.45, light=1.3)],
                  mass=(0.8, 0.8, 0.6), chip=(0.18, 0.18, 0.15), key=(-0.3, 0.35, 0.88), shade=(0.2, 0.6),
                  crust=0.66, weed=0.58, up=0.5, pores=0.35, glow={2: 0.75},
                  plants=[('glow_fern', 0.3, 0.46), ('glowshroom', 0.14, 0.22), ('glow_bromeliad', 0.2, 0.3)]),
    'menhir': dict(ramps=[ramp('#8a8a84', dark=0.32, light=1.3), ramp('#b8b48a', dark=0.45, light=1.12),
                          ramp('#4e6a34', dark=0.35, light=1.25)],
                   mass=(1.4, 1.4, 1.0), chip=(0.2, 0.2, 0.18), key=(-0.4, 0.45, 0.8), shade=(0.3, 0.62),
                   crust=0.62, weed=0.55, up=0.5, pores=0.0, cracks=0.25, varnish=0.06,
                   plants=[('grass_tuft', 0.18, 0.28), ('fern', 0.2, 0.3)]),
    'basalt': dict(ramps=[ramp('#4a4644', dark=0.32, light=1.6), ramp('#5e544a', dark=0.35, light=1.4),
                          ramp('#7a7464', dark=0.4, light=1.3)],
                   mass=(2.0, 2.0, 2.0), chip=(0.12, 0.12, 0.1), key=(-0.4, 0.45, 0.8), shade=(0.3, 0.6),
                   crust=0.7, weed=0.2, up=0.7, pores=0.0, cracks=0.2, courses=0.42, staggered=True,
                   plants=[('grass_tuft', 0.14, 0.22)]),
    'salt': dict(ramps=[ramp('#ebe6dc', dark=0.55, light=1.08), ramp('#d6ccbc', dark=0.55, light=1.08),
                        ramp('#f4f0ea', dark=0.55, light=1.06)],
                 mass=(0.3, 0.3, 0.3), chip=(0.05, 0.05, 0.05), key=(-0.4, 0.45, 0.8), shade=(0.6, 0.42),
                 crust=0.72, weed=0.7, up=0.75, pores=0.1, cracks=0.0, plants=[]),
}
ROCK_FOOT = 0.02            # rock runs this far below the ground, so no seam shows at its foot


def _turned(key, pl):
    """A light direction in the world as an object placed by `pl` sees it in its own frame (x forward,
    y to its right), so what is painted on it agrees with everything else in the scene."""
    a = math.radians(float(pl.get('angle', 0.0)))
    x, y, z = key
    return (x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a), z)


def _rock_kind(pl):
    """The kind of rock a placement asks for (`rock`, default stone), its light turned to the placement."""
    rk = ROCKS[pl.get('rock', 'stone')]
    return dict(rk, key=_turned(rk['key'], pl))


def _dome(gap, e1, e2, cell, k, amp):
    """The slope (per unit) of a low dome over each cell of `cells3`: `amp` high inside (one height,
    or one per point), falling smoothly to nothing over the last `k` (in boxes) before its edge."""
    x = np.clip(gap / k, 0, 1)
    return (amp * 6 * x * (1 - x) / k)[:, None] * (e2 - e1) / cell


def _stone(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """The texture (rgba, emission) of a panel of rock - its corner o, columns along u, rows along v,
    w x h texels, solid where `alpha` - cut from one solid block of the rock `rk` (see _rock_kind; its
    light in the object's frame): masses of stone, each a
    little domed and a shade of its own, some of the joins between them cracked; chips on them,
    some pitted; crusts in patches and weed where the stone faces up; all lit in 3D by the rock's
    light, so a face takes it by the way it faces. `rim` (per texel, how many texels below the top
    edge) rounds the stone over toward that edge, so it catches the light there; `tone` lightens or
    darkens the whole panel; `tilt` (per texel) bends its normal along u - the hollow of a flute."""
    key = np.asarray(rk['key'], np.float32)
    key /= np.linalg.norm(key)
    at = np.nonzero(alpha.reshape(-1))[0]                           # only the texels that are there
    ys, xs = at // w, at % w
    P = o + ((xs + 0.5) / w)[:, None] * u + ((ys + 0.5) / h)[:, None] * v
    nrm = np.cross(u, v)
    nrm = (nrm / np.linalg.norm(nrm)).astype(np.float32)
    mass, chip = np.asarray(rk['mass'], np.float32), np.asarray(rk['chip'], np.float32)
    F1, F2, e1, e2, id1, id2 = cells3(P, mass, seed)
    f1, f2, c1, c2, cid, _ = cells3(P, chip, seed + 1)
    gap = F2 - F1                                                   # 0 where two masses meet
    grad = _dome(gap, e1, e2, mass, 0.35, 0.06) + _dome(f2 - f1, c1, c2, chip, 0.3, 0.035 * table(2, cid) ** 2)
    grad -= (grad @ nrm)[:, None] * nrm                             # its slope across the face
    N = nrm - grad
    if rim is not None:
        N[:, 2] += 2.0 * (1 - np.clip(rim.reshape(-1)[at] / 6.0, 0, 1)) ** 2
    if tilt is not None:
        N += tilt.reshape(-1)[at][:, None] * (u / np.linalg.norm(u)).astype(np.float32)[None, :]
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    lit = np.clip(N @ key, 0, 1)
    crack = (gap < 0.04) & (table(4, np.minimum(id1, id2) * 31 + np.maximum(id1, id2)) < rk.get('cracks', 0.45))
    pits = (f1 < 0.12) & (table(3, cid) < rk['pores'])
    val = rk['shade'][0] + rk['shade'][1] * lit + tone + (table(5, id1) - 0.5) * 0.12 - 0.22 * crack - 0.3 * pits
    val -= 0.2 * (1 - np.clip(P[:, 2] / 0.3, 0, 1)) ** 2            # darker at the foot
    mat = np.zeros(len(P), int)
    mat[(noise3(P, 0.16, seed + 2) > rk['crust']) & (table(4, id1) < 0.5)] = 1
    if 'strata' in rk:                                              # beds of pale stone, by height, wandering a little
        period, pale = rk['strata']
        wob = 0.22 * (noise3(P, 1.8, seed + 7) - 0.5)
        bed = (P[:, 2] / period + wob) % 1.0
        mat[bed < pale] = 1
        val = val + 0.07 * np.cos(2 * np.pi * (P[:, 2] / (period * 0.31) + wob))   # thinner bands of tone
    if rk.get('courses'):                                           # dressed stone in courses: a joint between
        k = P[:, 2] / rk['courses'] + rk.get('course_phase', 0.0)  # each, every course its own shade
        course = np.floor(k).astype(np.int64)
        joint = (k - course < 0.035) | (k - course > 0.985)
        val = val + (table(5, course * 7919 + seed) - 0.5) * 0.1 - 0.16 * joint
        crack = crack | joint
    if rk.get('varnish'):                                           # desert varnish: dark streaks run down the face
        streak = noise3(P / np.array([0.1, 0.1, 2.2], np.float32), 1.0, seed + 8)
        val = val - rk['varnish'] * np.clip((streak - 0.52) / 0.25, 0, 1) * np.clip(P[:, 2] / 2.5, 0, 1)
    up = np.nonzero(N[:, 2] > rk.get('up', 0.6))[0]                 # weed in tufts, where it faces up
    if up.size:
        mat[up[noise3(P[up], 0.12, seed + 3) > rk['weed']]] = 2
    bay = BAYER4[ys % 4, xs % 4]
    rgb = np.zeros((h * w, 3), np.float32)
    em = np.zeros(h * w, np.float32)
    for m, rp in enumerate(rk['ramps']):
        sel = mat == m
        idx = np.clip(np.round(val[sel] * (len(rp) - 1) + (bay[sel] - 0.5) * 0.35), 0, len(rp) - 1).astype(int)
        idx = np.where((crack | pits)[sel], np.maximum(idx - 1, 0), idx)    # cracks and pits a step darker
        rgb[at[sel]] = np.asarray(rp, np.float32)[idx]
        em[at[sel]] = rk.get('glow', {}).get(m, 0.0)
    rgba = np.concatenate([rgb.reshape(h, w, 3), alpha.reshape(h, w, 1).astype(np.float32)], -1)
    return rgba, em.reshape(h, w)


# Timber, for posts and piles: weathered wood grey-brown, the grain running up it, and where it
# stands in water (below `wet`) dark and grown green. Painted by _wood, lit like rock.
WOODS = {
    'wood': dict(ramps=[ramp('#8f7a62', dark=0.4, light=1.45, warm=0.08), ramp('#46523c', dark=0.4, light=1.35)],
                 key=(-0.4, 0.45, 0.8), shade=(0.38, 0.52), grain=(0.025, 0.025, 0.4), wet=0.1),
}


def _wood(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """The texture of a panel of timber, as _stone is of rock: grain running up it in long streaks
    with a few dark checks along it, cut from one solid block so the grain carries round a corner, lit
    by the way the face faces; below `wet` it is dark and grown over, with a ragged line where the
    water reaches. With `boards` (a width) it is laid in boards along the grain, a dark seam between
    each and each its own tone, the seams lining up from one panel to the next."""
    key = np.asarray(rk['key'], np.float32)
    key /= np.linalg.norm(key)
    at = np.nonzero(alpha.reshape(-1))[0]
    ys, xs = at // w, at % w
    P = o + ((xs + 0.5) / w)[:, None] * u + ((ys + 0.5) / h)[:, None] * v
    nrm = np.cross(u, v)
    lit = float(np.clip((nrm / np.linalg.norm(nrm)) @ key, 0, 1))
    G = P / np.asarray(rk['grain'], np.float32)                      # long along the grain, fine across it
    grain = noise3(G, 1.0, seed) * 0.65 + noise3(G * 2.3, 1.0, seed + 1) * 0.35
    check = (np.abs(noise3(G * np.array([0.6, 0.6, 0.25]), 1.0, seed + 2) - 0.5) < 0.035)   # splits along it
    val = rk['shade'][0] + rk['shade'][1] * lit + tone + 0.34 * (grain - 0.5) - 0.22 * check
    if rk.get('boards'):                                             # across the boards: the finest grain
        span = np.abs(u) + np.abs(v)                                 # of the ways the panel runs
        ax = min((i for i in range(3) if span[i] > 0.05 * span.max()), key=lambda i: rk['grain'][i])
        c = P[:, ax] / rk['boards']
        k = np.floor(c).astype(np.int64)
        val = val + (table(5, k * 7919 + 11) - 0.5) * 0.14 - 0.26 * ((c - k) < 1.2 / (TEXELS * rk['boards']))
    wet = P[:, 2] < rk['wet'] + 0.03 * (noise3(P, 0.08, seed + 3) - 0.5)
    mat = wet.astype(int)
    bay = BAYER4[ys % 4, xs % 4]
    rgb = np.zeros((h * w, 3), np.float32)
    for m, rp in enumerate(rk['ramps']):
        sel = mat == m
        idx = np.clip(np.round(val[sel] * (len(rp) - 1) + (bay[sel] - 0.5) * 0.35), 0, len(rp) - 1).astype(int)
        rgb[at[sel]] = np.asarray(rp, np.float32)[idx]
    rgba = np.concatenate([rgb.reshape(h, w, 3), alpha.reshape(h, w, 1).astype(np.float32)], -1)
    return rgba, np.zeros((h, w), np.float32)


def _grown(m):
    """A mask grown by a texel all round, so panels that meet leave no gap between them."""
    p = np.pad(m, 1)
    return m | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]


def _inset(m):
    """A mask drawn in by a texel all round: a top that must not show past the faces round it."""
    return ~_grown(~m)


def _rock(rk, seed, tl, tr, bl, alpha=None, rim=None, tone=0.0, tilt=None):
    """A panel of rock, its corners as `quad` takes them; `alpha(w, h)` and `rim(w, h)` give its mask
    and how far below its top edge each texel is, for a texture w x h. None if nothing is solid."""
    tl, tr, bl = (np.asarray(p, float) for p in (tl, tr, bl))
    u, v = tr - tl, bl - tl
    dens = rk.get('density', 1.0)                                    # texels per unit, as a share of a wall's
    w, h = _texels(np.linalg.norm(u) * dens), _texels(np.linalg.norm(v) * dens)
    a = np.ones((h, w), bool) if alpha is None else alpha(w, h)
    if not a.any():
        return None
    paint = rk.get('paint', _stone)
    if tilt is not None:
        tex = paint(rk, seed, tl, u, v, w, h, a, None if rim is None else rim(w, h), tone, tilt=tilt(w, h))
    else:
        tex = paint(rk, seed, tl, u, v, w, h, a, None if rim is None else rim(w, h), tone)
    return quad(tex, tuple(tl), tuple(tr), tuple(bl))


def _rock_tri(rk, seed, A, B, C, out):
    """A triangle of rock, turned to read from the side `out` points to."""
    A, B, C = (np.asarray(p, float) for p in (A, B, C))
    if np.cross(B - A, C - A) @ out < 0:
        B, C = C, B
    return _rock(rk, seed, A, B, C, alpha=lambda w, h: _grown(_poly(w, h, [(0, 0), (w, 0), (0, h)])))


def _span(v):
    """(low, high) from a pair, or one number for both."""
    return (float(v), float(v)) if isinstance(v, (int, float)) else (float(v[0]), float(v[1]))


def _wave(rng, S):
    """A long smooth wavy edge along S units of rock: its height 0..1 at a distance s along it - a
    slow swell, a shorter one and a ripple, at random phases, drawn down toward both ends."""
    waves = [(amp, rng.uniform(lo, hi), rng.uniform(0, 2 * np.pi))
             for amp, lo, hi in ((0.26, 1.1, 2.0), (0.16, 0.45, 0.8), (0.06, 0.18, 0.3))]

    def at(s):
        y = 0.55 + sum(a * np.sin(2 * np.pi * s / lam + ph) for a, lam, ph in waves)
        k = np.clip(np.minimum(s, S - s) / 0.35, 0, 1)
        return np.clip(y * (0.35 + 0.65 * k * k * (3 - 2 * k)), 0.06, 1.0)
    return at


def _outline(rng, ya, yb, reach):
    """One piece of a rock wall in plan, from the wall at y = ya out and back to it at y = yb (ya > yb:
    left to right as seen from in front, +x): a rounded mass of a few broad faces at gentle angles to
    one another - full or flat, leaning one way or the other - its points jostled a little, and now
    and then one pushed out into a spike or pulled in to a notch."""
    wd = ya - yb
    n = max(3, int(round(wd / rng.uniform(0.5, 0.75))))              # its faces, each half a unit or more
    t = (np.arange(1, n) + rng.uniform(-0.25, 0.25, n - 1)) / n      # where its points are, across it
    t = np.sort(np.clip(t ** rng.uniform(0.75, 1.3), 0.06, 0.94))     # the bulge leaning one way
    x = reach * np.sin(np.pi * t) ** rng.uniform(0.45, 0.8) * rng.uniform(0.86, 1.08, n - 1)
    odd = rng.random(n - 1) < 0.12                                    # a few spikes and notches
    x = np.where(odd, x * rng.choice([0.6, 1.35], n - 1), x)
    return [(0.0, ya)] + [(float(a), float(ya - b * wd)) for a, b in zip(x, t)] + [(0.0, yb)]


def _piece(rk, seed, pts, h, trim, wave, tone, back):
    """The panels of one piece of a rock wall standing along `pts`, `h` high: its faces, the trim of
    faces over them cut along `wave`, its flat top, and with `back` its back against the wall."""
    parts = []
    s0 = 0.0
    for a, b in zip(pts, pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])

        def below(w, hh, top, span, s0=s0, ln=ln):        # texels below the wave, down a panel from `top`
            edge = trim * (1 - wave(s0 + (np.arange(w) + 0.5) / w * ln))
            return ((np.arange(hh)[:, None] + 0.5) / hh * span + top - edge[None, :]) * TEXELS

        parts.append(_rock(rk, seed, (a[0], a[1], h + trim), (b[0], b[1], h + trim), (a[0], a[1], h), tone=tone,
                           alpha=lambda w, hh, f=below: f(w, hh, 0.0, trim) >= -0.5,
                           rim=lambda w, hh, f=below: f(w, hh, 0.0, trim)))                     # the trim
        parts.append(_rock(rk, seed, (a[0], a[1], h), (b[0], b[1], h), (a[0], a[1], -ROCK_FOOT), tone=tone,
                           rim=lambda w, hh, f=below: f(w, hh, trim, h + ROCK_FOOT)))           # the face
        s0 += ln
    P = np.asarray(pts, float)
    (x0, y0), (x1, y1) = P.min(0), P.max(0)
    shape = lambda w, hh: _inset(_poly(w, hh, [((q[1] - y0) / (y1 - y0) * w, (x1 - q[0]) / (x1 - x0) * hh)  # noqa: E731
                                               for q in P]))
    parts.append(_rock(rk, seed, (x1, y0, h), (x1, y1, h), (x0, y0, h), alpha=shape, tone=tone))        # its top
    if back:
        parts.append(_rock(rk, seed, (0.0, y0, h), (0.0, y1, h), (0.0, y0, -ROCK_FOOT), tone=tone))
    return [p for p in parts if p]


def rock_wall(pl):
    """Rockwork along the foot of a wall, as the user laid it out: pieces side by side and overlapping,
    each in plan a rounded mass of broad faces jutting from the wall, each its own height, a trim of
    faces along its top cut by one long smooth wavy edge, so no top is straight and level; a flat top
    on each, and plants growing on them. The wall's foot runs along y, centred on the origin, `length` long,
    and the rock juts out toward +x up to `depth`. `height` is how tall a piece is (lowest, highest),
    `pieces` how wide (narrowest, widest), `trim` the trim's height as a share of its piece's, `rock`
    the kind of rock; `plants` false leaves the tops bare, and `back` true closes each piece's back,
    for rock standing free of a wall."""
    rk = _rock_kind(pl)
    L = float(pl.get('length', 4.0))
    hlo, hhi = _span(pl.get('height', [0.5, 1.4]))
    reach = float(pl.get('depth', 0.7))
    wlo, whi = _span(pl.get('pieces', [1.4, 2.8]))
    trim_k = float(pl.get('trim', 0.28))
    seed = int(pl.get('seed', 1))
    rng = np.random.default_rng(seed)
    parts, y, last = [], L / 2, None
    while True:
        wd = rng.uniform(wlo, whi)
        yb = y - wd
        if yb + L / 2 < wlo * 0.5:                                     # too little left for another
            yb = -L / 2
        h = rng.uniform(hlo, hhi)
        if last is not None and hhi > hlo and abs(h - last) < 0.22 * (hhi - hlo):
            h = hlo + (hhi - hlo) * (((h - hlo) / (hhi - hlo) + 0.5) % 1.0)   # not the height of the last
        last = h
        pts = _outline(rng, y, yb, reach * rng.uniform(0.7, 1.0))
        S = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))
        wave, trim = _wave(rng, S), trim_k * h
        parts += _piece(rk, seed, pts, h, trim, wave, rng.uniform(-0.06, 0.06), bool(pl.get('back', False)))
        s = 0.0
        for p, q in zip(pts, pts[1:]):
            parts.append(shadow((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, 0.55, 0.35))   # shade at its foot
            if pl.get('plants', True) and rk['plants'] and p[0] > 0.45 * reach and rng.random() < 0.5:
                name, lo, hi = rk['plants'][rng.integers(len(rk['plants']))]           # on the rim, at the wave
                parts.append(sprite(name, p[0] * rng.uniform(0.55, 0.8), p[1] + rng.uniform(-0.08, 0.08),
                                    h + 0.8 * trim * float(wave(s)), scale=rng.uniform(lo, hi), shadow=False,
                                    flip=bool(rng.random() < 0.5)))
            s += math.hypot(q[0] - p[0], q[1] - p[1])
        if yb <= -L / 2:
            break
        y = yb + wd * rng.uniform(0.15, 0.35)                          # the next overlaps it
    return parts


def boulder(pl):
    """A boulder: a low-poly mass of rock, every face a triangle - an irregular polygon at its foot,
    bulging a little, drawing in toward its shoulders, up to a peak off its centre. `size` is how wide
    it is, `height` how tall, `rock` the kind of rock and `plants` how many things grow on top."""
    rk = _rock_kind(pl)
    seed = int(pl.get('seed', 1))
    rng = np.random.default_rng(seed)
    R = float(pl.get('size', 0.8)) / 2
    H = float(pl.get('height', R * 1.1))
    N = int(rng.integers(6, 9))
    ang = (np.arange(N) + rng.uniform(-0.3, 0.3, N)) * 2 * np.pi / N
    r0 = R * rng.uniform(0.72, 1.0, N)
    off = rng.uniform(-0.18, 0.18, 2) * R
    rings = [(r0 * rng.uniform(0.94, 1.0, N), np.full(N, -ROCK_FOOT), np.zeros(2)),           # its foot
             (r0 * rng.uniform(0.98, 1.08, N), H * rng.uniform(0.26, 0.42, N), off * 0.3),      # its belly
             (r0 * rng.uniform(0.55, 0.78, N), H * rng.uniform(0.66, 0.86, N), off)]            # its shoulders
    rings = [np.stack([r * np.cos(ang) + c[0], r * np.sin(ang) + c[1], z], 1) for r, z, c in rings]
    peak = np.array([off[0] * 1.3, off[1] * 1.3, H])
    mid = np.array([0.0, 0.0, H * 0.4])
    parts = []
    for lo, hi in zip(rings, rings[1:]):
        for i in range(N):
            j = (i + 1) % N
            A, B, C, D = lo[i], lo[j], hi[j], hi[i]
            tris = ((A, B, C), (A, C, D)) if rng.random() < 0.5 else ((A, B, D), (B, C, D))
            parts += [_rock_tri(rk, seed, *t, (A + B + C + D) / 4 - mid) for t in tris]
    for i in range(N):
        A, B = rings[-1][i], rings[-1][(i + 1) % N]
        parts.append(_rock_tri(rk, seed, A, B, peak, (A + B + peak) / 3 - mid))
    parts = [p for p in parts if p]
    parts.append(shadow(0.0, 0.0, 2.6 * R, 0.5))
    n = int(pl.get('plants', 0)) if rk['plants'] else 0
    for k in range(n):                                                 # what grows on its top
        name, lo, hi = rk['plants'][rng.integers(len(rk['plants']))]
        a, r = rng.uniform(0, 2 * np.pi), (0.15 + 0.35 * k / n) * R
        parts.append(sprite(name, peak[0] + r * np.cos(a), peak[1] + r * np.sin(a), H * (0.95 - 0.5 * r / R),
                            scale=rng.uniform(lo, hi), shadow=False, flip=bool(rng.random() < 0.5)))
    return parts


def keel(pl):
    """The rock under a floating island, hanging from it: an irregular ring `size` across at its top
    (set the placement's `z` at the foot of the island's `cliff`), drawing in by uneven steps - each
    corner jutting or drawn in on its own - to a ragged point `depth` below (default 0.8 of its size),
    off its centre, with two or three crags hanging from its flanks; every face a triangle of rock, lit
    from above, so its underside is in its own shade. `rock` defaults to `island` (grey and brown in
    beds); `roots` (default true) trails roots from its top."""
    rk = _rock_kind(dict(pl, rock=pl.get('rock', 'island')))
    seed = int(pl.get('seed', 1))
    rng = np.random.default_rng(seed)
    R = float(pl.get('size', 4.0)) / 2
    D = float(pl.get('depth', R * 1.6))
    tip = rng.uniform(-0.2, 0.2, 2) * R

    def cone(c, r0, z0, depth, n, steps, k0):
        """A hanging cone of rock from a ring of radius r0 round c at z0, by `steps` (share of r0, share
        of depth down, how far it leans to the tip), to a point."""
        ang = (np.arange(n) + rng.uniform(-0.3, 0.3, n)) * 2 * np.pi / n
        rings = []
        for k, (share, down, lean) in enumerate(steps):
            r = r0 * share * (rng.uniform(0.8, 1.06, n) if k else rng.uniform(0.97, 1.0, n))
            z = z0 - depth * (down + (rng.uniform(-0.04, 0.04, n) if k else np.zeros(n)))
            rings.append(np.stack([c[0] + r * np.cos(ang) + tip[0] * lean, c[1] + r * np.sin(ang) + tip[1] * lean, z], 1))
        point = np.array([c[0] + tip[0], c[1] + tip[1], z0 - depth])
        out = []
        for k, (hi, lo) in enumerate(zip(rings, rings[1:])):
            mid = np.array([c[0] + tip[0] * 0.5, c[1] + tip[1] * 0.5, (lo[:, 2].mean() + hi[:, 2].mean()) / 2])
            for i in range(n):
                j = (i + 1) % n
                A, B, C, E = hi[i], hi[j], lo[j], lo[i]
                tris = ((A, B, C), (A, C, E)) if rng.random() < 0.5 else ((A, B, E), (B, C, E))
                out += [_rock_tri(rk, seed + k0 + k, *t, (A + B + C + E) / 4 - mid) for t in tris]
        for i in range(n):
            A, B = rings[-1][i], rings[-1][(i + 1) % n]
            out.append(_rock_tri(rk, seed + k0 + 9, A, B, point,
                                 (A + B + point) / 3 - np.array([c[0] + tip[0], c[1] + tip[1], z0 - depth * 0.8])))
        return out, rings

    parts, rings = cone((0.0, 0.0), R, 0.0, D, int(rng.integers(10, 14)),
                        ((1.0, 0.0, 0.0), (0.9, 0.14, 0.1), (0.76, 0.3, 0.28), (0.58, 0.48, 0.5),
                         (0.4, 0.66, 0.7), (0.22, 0.84, 0.88)), 0)
    for s_ in range(int(rng.integers(2, 4))):                         # crags hanging from its flanks
        ring = rings[int(rng.integers(1, 4))]
        p = ring[int(rng.integers(len(ring)))] * np.array([0.82, 0.82, 1.0])
        more, _ = cone(p[:2], R * rng.uniform(0.16, 0.26), p[2], D * rng.uniform(0.3, 0.5), 6,
                       ((1.0, 0.0, 0.0), (0.7, 0.4, 0.2)), 20 + s_)
        parts += more
    parts = [q for q in parts if q]
    if pl.get('roots', True):                                         # roots trailing from its top
        for i in range(0, len(rings[1]), 2):
            x, y, z = rings[1][i]
            parts.append(sprite('island_roots', x * 0.95, y * 0.95, z - D * 0.15, scale=R * rng.uniform(0.35, 0.5),
                                shadow=False, flip=bool(rng.random() < 0.5)))
    return parts


def heap(pl):
    """A heap of something loose - salt raked up to dry, sand, spoil: an irregular cone `size` across at
    its foot (default 0.5) and `height` tall (default 0.6 of its size), lumpy, drawing in by uneven steps
    to a blunt top a little off its centre; every face a triangle of `rock` (default `salt`: white grains,
    pitted)."""
    rk = _rock_kind(dict(pl, rock=pl.get('rock', 'salt')))
    seed = int(pl.get('seed', 1))
    rng = np.random.default_rng(seed)
    R = float(pl.get('size', 0.5)) / 2
    H = float(pl.get('height', R * 1.2))
    N = int(rng.integers(8, 11))
    ang = (np.arange(N) + rng.uniform(-0.25, 0.25, N)) * 2 * np.pi / N
    tip = rng.uniform(-0.12, 0.12, 2) * R
    levels = [(np.full(N, -ROCK_FOOT), rng.uniform(0.9, 1.0, N)),
              (H * (0.36 + rng.uniform(-0.03, 0.03, N)), 0.68 * rng.uniform(0.95, 1.04, N)),
              (H * (0.72 + rng.uniform(-0.03, 0.03, N)), 0.34 * rng.uniform(0.92, 1.06, N))]
    rings = [np.stack([R * k * np.cos(ang) + tip[0] * z / H, R * k * np.sin(ang) + tip[1] * z / H, z], 1)
             for z, k in levels]
    peak = np.array([tip[0], tip[1], H])
    mid = np.array([tip[0] * 0.3, tip[1] * 0.3, H * 0.3])
    parts = []
    for lo, hi in zip(rings, rings[1:]):
        for i in range(N):
            j = (i + 1) % N
            A, B, C, D = lo[i], lo[j], hi[j], hi[i]
            tris = ((A, B, C), (A, C, D)) if rng.random() < 0.5 else ((A, B, D), (B, C, D))
            parts += [_rock_tri(rk, seed, *t, (A + B + C + D) / 4 - mid) for t in tris]
    for i in range(N):
        A, B = rings[-1][i], rings[-1][(i + 1) % N]
        parts.append(_rock_tri(rk, seed, A, B, peak, (A + B + peak) / 3 - mid))
    parts = [p for p in parts if p]
    parts.append(shadow(0.0, 0.0, 2.4 * R, 0.45))
    return parts


def standing_stone(pl):
    """A standing stone: a rough slab of rock set on end, `size` across (default 1.0), `depth` through
    (default 0.45 of its size) and `height` tall (default 2.0) - an irregular outline at its foot, its
    broad faces nearly flat, swelling a little and drawing in by uneven steps as it rises, leaning a
    few degrees, to a weathered top that slopes down from one shoulder with the corners knocked off.
    Every face a triangle of rock (`rock`, default `menhir`: grey, lichened, moss where it faces up).
    Its broad faces look along x: turn them with `angle` (into a circle, say). Low and wide it is a slab
    lying, its top near flat - an altar stone. `plants` sets tufts round its foot."""
    rk = _rock_kind(dict(pl, rock=pl.get('rock', 'menhir')))
    seed = int(pl.get('seed', 1))
    rng = np.random.default_rng(seed)
    W = float(pl.get('size', 1.0))
    T = float(pl.get('depth', W * 0.45))
    H = float(pl.get('height', 2.0))
    N = int(rng.integers(8, 11))
    ang = (np.arange(N) + rng.uniform(-0.25, 0.25, N)) * 2 * np.pi / N
    c, sn = np.cos(ang), np.sin(ang)
    foot = np.stack([T / 2 * np.sign(c) * np.abs(c) ** 0.6,                     # squarer than an ellipse,
                     W / 2 * np.sign(sn) * np.abs(sn) ** 0.6], 1) * rng.uniform(0.9, 1.0, N)[:, None]   # so its faces are broad
    lean = rng.uniform(-0.05, 0.05, 2) * np.array([1.0, 0.6])
    t = (foot[:, 1] / (W / 2) + 1) / 2                                         # 0..1 across its width
    t = 1 - t if rng.random() < 0.5 else t
    slope = 0.2 * min(1.0, H / W)                                              # how far its top falls across it
    levels = [(np.full(N, -ROCK_FOOT), np.ones(N)),                                                    # its foot
              (H * (0.4 + rng.uniform(-0.04, 0.04, N)), rng.uniform(1.0, 1.07, N)),                       # its belly
              (H * (0.9 - 1.3 * slope + slope * t + rng.uniform(-0.03, 0.03, N)), rng.uniform(0.8, 0.9, N)),  # shoulders
              (np.minimum(H * (1 - slope + slope * t + rng.uniform(-0.015, 0.015, N)), H), rng.uniform(0.5, 0.62, N))]
    rings = [np.stack([foot[:, 0] * k + lean[0] * z, foot[:, 1] * k + lean[1] * z, z], 1) for z, k in levels]
    parts = []
    for k, (lo, hi) in enumerate(zip(rings, rings[1:])):
        for i in range(N):
            j = (i + 1) % N
            A, B, C, D = lo[i], lo[j], hi[j], hi[i]
            m = (A + B + C + D) / 4
            out = m - np.array([lean[0] * m[2], lean[1] * m[2], m[2]]) + np.array([0.0, 0.0, 0.15 * (k == 2)])
            tris = ((A, B, C), (A, C, D)) if rng.random() < 0.5 else ((A, B, D), (B, C, D))
            parts += [_rock_tri(rk, seed, *q, out) for q in tris]
    crown = rings[-1]
    top = np.array([crown[:, 0].mean(), crown[:, 1].mean(), crown[:, 2].mean() + 0.02 * H])
    for i in range(N):                                                          # and its top
        parts.append(_rock_tri(rk, seed, crown[i], crown[(i + 1) % N], top, np.array([0.0, 0.0, 1.0])))
    parts = [p for p in parts if p]
    parts.append(shadow(0.0, 0.0, 1.3 * W, 0.5))
    n = int(pl.get('plants', 0)) if rk['plants'] else 0
    for k in range(n):                                                          # tufts round its foot
        name, lo, hi = rk['plants'][rng.integers(len(rk['plants']))]
        x, y = foot[int(rng.integers(N))] * rng.uniform(1.04, 1.16)
        parts.append(sprite(name, x, y, 0.0, scale=rng.uniform(lo, hi), shadow=False, flip=bool(rng.random() < 0.5)))
    return parts


# ------------------------------------------------------------------ columns and posts

def _material(pl):
    """What a column is made of - a kind of rock (`material` names it, cut from solid stone as rock is),
    `wood`, or painted cast `iron` (`iron_white`, `iron_green`) - with its light turned to the placement,
    as for rock."""
    name = pl.get('material', 'stone')
    if name in WOODS:
        return dict(WOODS[name], paint=_wood, key=_turned(WOODS[name]['key'], pl))
    if name in IRONS:
        return dict(IRONS[name], paint=_painted, key=_turned(IRONS[name]['key'], pl))
    return _rock_kind({'rock': name, 'angle': pl.get('angle', 0.0)})


def _painted(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """Painted metal - cast iron in a glasshouse: smooth, lit by the way it faces (with `tilt`, round), a
    sheen toward the light, the paint chipped to rust here and there."""
    key = np.asarray(rk['key'], np.float32)
    key /= np.linalg.norm(key)
    at = np.nonzero(alpha.reshape(-1))[0]
    ys, xs = at // w, at % w
    P = o + ((xs + 0.5) / w)[:, None] * u + ((ys + 0.5) / h)[:, None] * v
    nrm = np.cross(u, v)
    N = np.repeat((nrm / np.linalg.norm(nrm)).astype(np.float32)[None, :], len(at), 0)
    if tilt is not None:
        N += tilt.reshape(-1)[at][:, None] * (u / np.linalg.norm(u)).astype(np.float32)[None, :]
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    lit = np.clip(N @ key, 0, 1)
    val = rk['shade'][0] + rk['shade'][1] * lit + 0.2 * np.clip((lit - 0.85) / 0.15, 0, 1) + tone
    mat = (noise3(P, 0.06, seed) > rk.get('rust', 0.86)).astype(int)
    bay = BAYER4[ys % 4, xs % 4]
    rgb = np.zeros((h * w, 3), np.float32)
    for m, rp in enumerate(rk['ramps']):
        sel = mat == m
        idx = np.clip(np.round(val[sel] * (len(rp) - 1) + (bay[sel] - 0.5) * 0.3), 0, len(rp) - 1).astype(int)
        rgb[at[sel]] = np.asarray(rp, np.float32)[idx]
    rgba = np.concatenate([rgb.reshape(h, w, 3), alpha.reshape(h, w, 1).astype(np.float32)], -1)
    return rgba, np.zeros((h, w), np.float32)


# Painted cast iron, for a glasshouse's columns, ribs and glazing bars. Painted by _painted.
IRONS = {
    'iron_white': dict(ramps=[ramp('#e2e0d6', dark=0.45, light=1.12), ramp('#8a5a3a', dark=0.4, light=1.3)],
                       key=(-0.4, 0.45, 0.8), shade=(0.42, 0.5)),
    'iron_green': dict(ramps=[ramp('#3a5a48', dark=0.4, light=1.5), ramp('#7a4a32', dark=0.4, light=1.3)],
                       key=(-0.4, 0.45, 0.8), shade=(0.38, 0.55)),
    'lime_white': dict(ramps=[ramp('#e6e2d6', dark=0.42, light=1.1), ramp('#a8a08a', dark=0.4, light=1.2)],
                       key=(-0.4, 0.45, 0.8), shade=(0.4, 0.52), rust=0.8),
    'lime_red': dict(ramps=[ramp('#a8382c', dark=0.38, light=1.3), ramp('#8a6a5a', dark=0.4, light=1.2)],
                     key=(-0.4, 0.45, 0.8), shade=(0.38, 0.55), rust=0.84),
    'lacquer_black': dict(ramps=[ramp('#2a2628', dark=0.6, light=2.2), ramp('#4a3a32', dark=0.5, light=1.6)],
                          key=(-0.4, 0.45, 0.8), shade=(0.3, 0.6), rust=0.9),
    'brass': dict(ramps=[ramp('#b08a3c', dark=0.4, light=1.55, warm=0.06), ramp('#4f8a6e', dark=0.4, light=1.3)],
                  key=(-0.4, 0.45, 0.8), shade=(0.34, 0.62), rust=0.8),
}


def _ring(n, r, z, phase):
    return [np.array([r * math.cos(phase + 2 * math.pi * k / n), r * math.sin(phase + 2 * math.pi * k / n), z])
            for k in range(n)]


def _prism_faces(mat, seed, n, r0, r1, z0, z1, phase, tone=0.0, flute=0.0, block=False):
    """The sides of an n-sided prism from radius r0 at z0 to r1 at z1 (a frustum when they differ, narrowing
    or widening): every face a panel cut to its trapezoid, read from outside. `flute` hollows each face
    into a flute - its normal bends across it, so it takes the light on one side and shadow on the other.
    `block` cuts every face from the same block of stone (one stone round), not each from its own."""
    parts = []
    bottom, top = _ring(n, r0, z0, phase), _ring(n, r1, z1, phase)
    wide = r1 > r0                                                   # the panel is laid on the wider edge
    cut = (1 - min(r0, r1) / max(r0, r1)) / 2                        # how far the narrower edge is drawn in
    for k in range(n):
        B0, B1 = bottom[k], bottom[(k + 1) % n]
        T0, T1 = top[k], top[(k + 1) % n]
        if np.cross(B1 - B0, np.array([0.0, 0.0, -1.0])) @ (B0 + B1) < 0:   # read from outside
            B0, B1, T0, T1 = B1, B0, T1, T0
        drop = (B0 + B1) / 2 - (T0 + T1) / 2

        def edges(w, h):
            """Each texel's place across the panel, and how far in the face's edge is at its height."""
            t = (np.arange(h)[:, None] + 0.5) / h                       # 0 at the top, 1 at the foot
            return (np.arange(w)[None, :] + 0.5) / w, cut * (t if wide else 1 - t)

        def shape(w, h):
            s, c = edges(w, h)
            return (s >= c - 0.5 / w) & (s <= 1 - c + 0.5 / w)

        def span(w, h):                                              # 0..1 across the face itself
            s, c = edges(w, h)
            return np.clip((s - c) / (1 - 2 * c), 0, 1)
        tilt = (lambda w, h: flute * (1 - 2 * span(w, h))) if flute else None
        tl, tr = (T0, T1) if wide else (B0 - drop, B1 - drop)
        p = _rock(mat, seed + (0 if block else k), tl, tr, tl + drop, alpha=shape, tone=tone, tilt=tilt)
        if p:
            parts.append(p)
    return parts


def _disc(mat, seed, n, r, z, phase, below=False):
    """A flat n-sided cap at height z, read from above (or, with `below`, from below)."""
    x0, x1, y0, y1 = -r, r, -r, r
    pts = [(p[1], p[0]) for p in _ring(n, r, z, phase)]

    def shape(w, h):
        return _poly(w, h, [((y - y0) / (y1 - y0) * w, (x1 - x) / (x1 - x0) * h) for y, x in pts])
    if below:
        return _rock(mat, seed, (x1, y1, z), (x1, y0, z), (x0, y1, z), alpha=lambda w, h: shape(w, h)[:, ::-1])
    return _rock(mat, seed, (x1, y0, z), (x1, y1, z), (x0, y0, z), alpha=shape)


def _broken_top(mat, seed, n, r0, r1, z0, H, phase, depth, flute=0.0, block=False):
    """The sides of an n-sided shaft (radius r0 at z0 to r1 at H) broken off ragged: each corner stops
    at its own height, up to `depth` below H, every face cut slanting between its two corners, and the
    break itself a fan of rough triangles in to a point a little below the top. Each face is a panel in
    the face's own plane, laid as _prism_faces lays them, solid in every texel the face reaches into - so
    the faces overlap at their edges by a sliver of a texel, never leaving a crack the sky shows through.
    `flute` and `block` as for _prism_faces."""
    rng = np.random.default_rng(seed + 400)
    tops = H - rng.uniform(0, depth, n)
    rad = lambda z: r0 + (r1 - r0) * (z - z0) / max(H - z0, 1e-6)     # noqa: E731
    ang = [phase + 2 * math.pi * k / n for k in range(n)]
    at = lambda a, z: np.array([rad(z) * math.cos(a), rad(z) * math.sin(a), z])     # noqa: E731
    ring = [at(a, t) for a, t in zip(ang, tops)]
    parts = []
    for k in range(n):
        a, b, za, zb = ang[k], ang[(k + 1) % n], tops[k], tops[(k + 1) % n]
        if np.cross(at(b, z0) - at(a, z0), np.array([0.0, 0.0, -1.0])) @ (at(a, z0) + at(b, z0)) < 0:
            a, b, za, zb = b, a, zb, za                                # read from outside
        hi = max(za, zb)
        B0, B1, T0, T1 = at(a, z0), at(b, z0), at(a, hi), at(b, hi)
        wide = rad(hi) > r0                                            # laid on its wider edge
        cut = (1 - min(r0, rad(hi)) / max(r0, rad(hi))) / 2           # how far the narrower edge is drawn in
        drop = (B0 + B1) / 2 - (T0 + T1) / 2
        tl, tr = (T0, T1) if wide else (B0 - drop, B1 - drop)
        ta, tb = (hi - za) / (hi - z0), (hi - zb) / (hi - z0)          # how far down each edge the break is
        sa, sb = cut * (ta if wide else 1 - ta), 1 - cut * (tb if wide else 1 - tb)
        slope = (tb - ta) / max(sb - sa, 1e-9)

        def shape(w, h, cut=cut, wide=wide, ta=ta, sa=sa, slope=slope):
            s0, s1 = np.arange(w)[None, :] / w, (np.arange(w)[None, :] + 1) / w     # each texel's sides,
            t0, t1 = np.arange(h)[:, None] / h, (np.arange(h)[:, None] + 1) / h     # its top and its foot
            c = cut * (t0 if wide else 1 - t1)                        # the face's edge where widest across it
            under = t1 >= ta + slope * ((s0 if slope > 0 else s1) - sa)              # any of it under the break
            return (s1 >= c) & (s0 <= 1 - c) & under

        def tilt(w, h, cut=cut, wide=wide):                           # the hollow of a flute, across the face
            s, t = (np.arange(w)[None, :] + 0.5) / w, (np.arange(h)[:, None] + 0.5) / h
            c = cut * (t if wide else 1 - t)
            return flute * (1 - 2 * np.clip((s - c) / (1 - 2 * c), 0, 1))
        p = _rock(mat, seed + (0 if block else k), tl, tr, tl + drop, alpha=shape, tilt=tilt if flute else None)
        if p:
            parts.append(p)
    peak = np.array([0.0, 0.0, float(tops.mean()) - 0.04])
    for k in range(n):
        A, B = ring[k], ring[(k + 1) % n]
        parts.append(_rock_tri(mat, seed + 450 + k, A, B, peak, (A + B) / 2 * np.array([1, 1, 0]) + np.array([0, 0, 1.5])))
    return parts


def column(pl):
    """A column or a post: a prism of `sides` faces (8 by default) `height` tall and `radius` across its
    corners at the foot, narrowing to `top` times that at its head; `material` a kind of rock (cut from
    the solid stone, as rock is), `ashlar` (pale dressed stone laid in drums) or `wood` (the grain
    running up it, wet and dark at the foot where it stands in water). `base` and `capital` (heights)
    add a wider block under it and over it, `broken` (a depth) breaks it off ragged instead of a head,
    `sink` sets its foot that far into the ground, and `seed` varies its stone or grain. `flutes` (a
    number) makes it that many-sided with every face hollowed into a flute, all cut from one stone round
    (a drum is one stone), and `"doric": true` gives it the Doric order: no base, a capital of a cushion
    (the echinus) under a square slab (the abacus)."""
    mat = _material(pl)
    seed = int(pl.get('seed', 1))
    if mat.get('staggered'):                                           # its joints at heights of its own
        mat = dict(mat, course_phase=(seed * 0.618034) % 1.0)
    flutes = int(pl.get('flutes', 0))
    n = flutes or int(pl.get('sides', 8))
    hollow = 1.4 if flutes else 0.0
    r = float(pl.get('radius', 0.12))
    top = r * float(pl.get('top', 1.0))
    H = float(pl.get('height', 1.0))
    z0 = -float(pl.get('sink', 0.02))
    hb, hc = float(pl.get('base', 0.0)), float(pl.get('capital', 0.0))
    phase = math.pi / n
    parts = []
    if hb:                                                             # a plinth under it
        parts += _prism_faces(mat, seed + 50, n, r * 1.3, r * 1.3, z0, hb, phase, tone=0.03)
        parts.append(_disc(mat, seed + 60, n, r * 1.3, hb, phase))
    if pl.get('broken'):                                               # broken off: no head
        return [p for p in parts + _broken_top(mat, seed, n, r, top, max(z0, hb - 0.01) if hb else z0, H, phase,
                                                float(pl['broken']), flute=hollow, block=bool(flutes)) if p]
    parts += _prism_faces(mat, seed, n, r, top, max(z0, hb - 0.01) if hb else z0, H - hc, phase, flute=hollow,
                          block=bool(flutes))
    if hc and pl.get('doric'):                                         # a cushion under a square slab
        za = H - hc * 0.42
        parts += _prism_faces(mat, seed + 70, 16, top, top * 1.42, H - hc, za, math.pi / 16, tone=0.02, block=True)
        sq = top * 1.5 * math.sqrt(2)
        parts += _prism_faces(mat, seed + 75, 4, sq, sq, za, H, math.pi / 4, tone=0.03, block=True)
        parts.append(_disc(mat, seed + 80, 4, sq, za, math.pi / 4, below=True))
        parts.append(_disc(mat, seed + 90, 4, sq, H, math.pi / 4))
    elif hc:                                                           # a capital over it
        parts += _prism_faces(mat, seed + 70, n, top * 1.35, top * 1.35, H - hc, H, phase, tone=0.03)
        parts.append(_disc(mat, seed + 80, n, top * 1.35, H - hc, phase, below=True))
        parts.append(_disc(mat, seed + 90, n, top * 1.35, H, phase))
    else:
        parts.append(_disc(mat, seed + 90, n, top, H, phase))
    return [p for p in parts if p]


def beam(pl):
    """A beam: a squared timber (or a stone lintel) lying level, `length` long along the way it faces,
    `width` across and `depth` deep, its underside at the placement's `z` - a wall plate along a row of
    pillars, a lintel, a rail. `material` as for a column; timber's grain runs along it."""
    mat = _material(pl)
    if 'grain' in mat:
        g = mat['grain']
        mat = dict(mat, grain=(g[2], g[0], g[1]))                       # along the beam, not up it
    seed = int(pl.get('seed', 1))
    L, w, d = float(pl.get('length', 2.0)) / 2, float(pl.get('width', 0.2)) / 2, float(pl.get('depth', 0.2))
    x0, x1, y0, y1, z0, z1 = -L, L, -w, w, 0.0, d
    faces = {'front': ((x1, y1, z1), (x1, y0, z1), (x1, y1, z0)), 'back': ((x0, y0, z1), (x0, y1, z1), (x0, y0, z0)),
             'right': ((x0, y1, z1), (x1, y1, z1), (x0, y1, z0)), 'left': ((x1, y0, z1), (x0, y0, z1), (x1, y0, z0)),
             'top': ((x1, y0, z1), (x1, y1, z1), (x0, y0, z1)), 'bottom': ((x1, y1, z0), (x1, y0, z0), (x0, y1, z0))}
    parts = [_rock(mat, seed + k, *c) for k, c in enumerate(faces.values())]
    return [p for p in parts if p]


# ------------------------------------------------------------------ timber work: troughs and roofs

def _timber(pl, grain, width):
    """Timber in boards (or the placement's `material`, wood by default): the grain along `grain`, a
    board every `width`."""
    mat = _material(dict(pl, material=pl.get('material', 'wood')))
    if mat.get('paint') is _wood:
        mat = dict(mat, grain=grain, boards=width, wet=-1e9)       # never wet: it may stand anywhere
    return mat


def _still_water(w, h, seed):
    """Still water seen from above, w x h texels: near black-green, the sky's sheen lying on it in
    soft streaks."""
    ys, xs = np.mgrid[0:h, 0:w]
    pts = np.stack([xs.ravel() / TEXELS, ys.ravel() / TEXELS * 3.0, np.zeros(w * h)], 1)
    val = (0.25 + 0.5 * noise3(pts, 0.6, seed)).reshape(h, w)
    rp = np.asarray(ramp('#2a4642', dark=0.45, light=1.7, warm=0.0), np.float32)
    idx = np.clip(np.round(val * (len(rp) - 1) + (BAYER4[ys % 4, xs % 4] - 0.5) * 0.4), 0, len(rp) - 1).astype(int)
    return np.concatenate([rp[idx], np.ones((h, w, 1), np.float32)], -1), np.zeros((h, w), np.float32)


def trough(pl):
    """A horse trough: an open box of weathered boards on the ground, `length` long the way it faces,
    `width` across and `height` tall, still water in it a hand below the rim."""
    mat = _timber(pl, (0.4, 0.4, 0.025), 0.15)
    seed = int(pl.get('seed', 1))
    L, w, H = float(pl.get('length', 1.6)) / 2, float(pl.get('width', 0.5)) / 2, float(pl.get('height', 0.45))
    rim = 0.05
    x0, x1, y0, y1 = -L, L, -w, w
    sides = (((x1, y1, H), (x1, y0, H), (x1, y1, 0.0)), ((x0, y0, H), (x0, y1, H), (x0, y0, 0.0)),
             ((x0, y1, H), (x1, y1, H), (x0, y1, 0.0)), ((x1, y0, H), (x0, y0, H), (x1, y0, 0.0)))
    parts = [_rock(mat, seed + k, *c) for k, c in enumerate(sides)]      # inside, their backs
    for k, (a0, a1, b0, b1) in enumerate(((x1 - rim, x1, y0, y1), (x0, x0 + rim, y0, y1),
                                          (x0, x1, y1 - rim, y1), (x0, x1, y0, y0 + rim))):
        parts.append(_rock(mat, seed + 10 + k, (a1, b0, H), (a1, b1, H), (a0, b0, H)))     # the rim
    z = H - 0.1
    parts.append(quad(_still_water(_texels(2 * (w - rim)), _texels(2 * (L - rim)), seed),
                      (x1 - rim, y0 + rim, z), (x1 - rim, y1 - rim, z), (x0 + rim, y0 + rim, z)))
    parts.append(shadow(0.0, 0.0, 2 * L + 0.4, 0.45))
    return [p for p in parts if p]


ROOF_LAMPS = 0.25    # how much of the lamps below it a roof's top takes (they are mapped on the floor)


def shed_roof(pl):
    """A shed roof of boards - over a porch or a boardwalk, a lean-to, an awning: `length` along it,
    reaching `depth` out the way it faces, its front edge at the placement's `z` and its back edge
    `rise` higher, so it slopes down to the front; the boards run down the slope."""
    mat = _timber(pl, (0.4, 0.025, 0.4), 0.14)
    seed = int(pl.get('seed', 1))
    L, D, r = float(pl.get('length', 2.0)) / 2, float(pl.get('depth', 1.0)) / 2, float(pl.get('rise', 0.3))
    t = 0.04                                                          # as thick as a board
    top = _rock(mat, seed, (D, -L, t), (D, L, t), (-D, -L, r + t))
    top['dyn'] = ROOF_LAMPS                                           # the lamps under it light its underside
    parts = [top,                                                                       # the top
             _rock(mat, seed + 1, (D, L, 0.0), (D, -L, 0.0), (-D, L, r), tone=-0.06),  # the underside
             _rock(mat, seed + 2, (D, L, t), (D, -L, t), (D, L, 0.0))]                  # its front edge
    return [p for p in parts if p]


def gable_roof(pl):
    """A gabled roof: the ridge `length` long the way it faces, `width` across, the eaves at the
    placement's `z` and the ridge `rise` above them; `cover` is `boards` (the default), `thatch`, `tile`,
    `slate`, `snow` (a roof under snow) or `glass` (panes between white iron glazing bars, drawn as glass:
    the sky shows through it and the sun comes in under it). It overhangs by `overhang` - a number, or [at the eaves, at the ends]; its gable ends are
    closed with upright boards, and under it stand `walls` that tall (0 for none) - the body of a
    building on a lower block, or a shed on the ground - set `inset` in from the roof's ends and
    eaves: a number (from the front end only) or [front, back, left, right]. `chimney` stands one on
    the ridge, that far along it from the back (0..1) - or a list of such places, one for each;
    `plaster` (a colour) makes the walls and gable ends plaster of that colour instead of boards, and
    `ends` (a kind of rock: `ashlar`, `stone`, ...) makes them stone."""
    cover = pl.get('cover', 'boards')
    roof = (_timber(pl, (0.025, 0.4, 0.4), 0.14) if cover == 'boards'
            else dict(ROOFS[cover], key=_turned(ROOFS[cover]['key'], pl)))
    ends = (dict(ROOFS['glass'], key=_turned(ROOFS['glass']['key'], pl)) if pl.get('ends') == 'glass'
            else _rock_kind(dict(pl, rock=pl['ends'])) if pl.get('ends')
            else dict(PLASTER, ramps=[ramp(pl['plaster'], dark=0.4, light=1.3)], key=_turned(PLASTER['key'], pl))
            if pl.get('plaster') else _timber(pl, (0.025, 0.025, 0.4), 0.16))
    seed = int(pl.get('seed', 1))
    L, W, r = float(pl.get('length', 3.0)) / 2, float(pl.get('width', 2.0)) / 2, float(pl.get('rise', 0.8))
    o = pl.get('overhang', 0.12)
    o, oe = (float(o), float(o)) if isinstance(o, (int, float)) else (float(o[0]), float(o[1]))
    drop = o * r / W                                                  # the eaves come down past the walls
    parts = [_rock(roof, seed, (-L - oe, 0.0, r), (L + oe, 0.0, r), (-L - oe, W + o, -drop)),
             _rock(roof, seed + 1, (L + oe, 0.0, r), (-L - oe, 0.0, r), (L + oe, -W - o, -drop))]
    for p in parts:                                                   # up out of the lamps' reach
        p['dyn'] = ROOF_LAMPS
        if cover == 'glass':
            p['translucent'] = True
    for k, x in enumerate((L, -L)):
        parts.append(_rock_tri(ends, seed + 2 + k, (x, -W, 0.0), (x, W, 0.0), (x, 0.0, r), (x, 0.0, 0.0)))
        if pl.get('ends') == 'glass' and parts[-1]:
            parts[-1]['translucent'] = True
    h, ins = float(pl.get('walls', 0.0)), pl.get('inset', 0.0)
    ins = (float(ins), 0.0, 0.0, 0.0) if isinstance(ins, (int, float)) else tuple(float(v) for v in ins)
    f, b, lf, rt = L - ins[0], -L + ins[1], -W + ins[2], W - ins[3]
    if h > 0:                                                         # the walls under it, read from outside
        for k, c in enumerate((((f, rt, 0.0), (f, lf, 0.0), (f, rt, -h)), ((b, lf, 0.0), (b, rt, 0.0), (b, lf, -h)),
                               ((b, rt, 0.0), (f, rt, 0.0), (b, rt, -h)), ((f, lf, 0.0), (b, lf, 0.0), (f, lf, -h)))):
            parts.append(_rock(ends, seed + 4 + k, *c))
    chims = pl.get('chimney')
    for place in ([] if chims is None else chims if isinstance(chims, (list, tuple)) else [chims]):
        x = -L + 2 * L * float(place)                                 # a chimney of brick through the ridge,
        big = max(1.0, r / 0.9) ** 0.5                                # stouter on a bigger roof
        c0 = c1 = 0.13 * big
        ztop = r + 0.36 * big
        brick = ROOFS['chimney']
        for k, c in enumerate((((x + c0, c1, ztop), (x + c0, -c1, ztop), (x + c0, c1, r * 0.4)),
                               ((x - c0, -c1, ztop), (x - c0, c1, ztop), (x - c0, -c1, r * 0.4)),
                               ((x - c0, c1, ztop), (x + c0, c1, ztop), (x - c0, c1, r * 0.4)),
                               ((x + c0, -c1, ztop), (x - c0, -c1, ztop), (x + c0, -c1, r * 0.4)))):
            parts.append(_rock(dict(brick, key=_turned(brick['key'], pl)), seed + 9 + k, *c))
        parts += box((x - c0 - 0.025, -c1 - 0.025, ztop), (x + c0 + 0.025, c1 + 0.025, ztop + 0.05),
                     {f_: _solid_cached(_texels(2 * c0 + 0.05), 4, '#4e3a32') for f_ in ('front', 'back', 'right', 'left')}
                     | {'top': _solid_cached(_texels(2 * c0 + 0.05), _texels(2 * c1 + 0.05), '#3a2a24')})
    return [p for p in parts if p]


def _thatch(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """Thatch on a roof's slope (a panel whose v runs down the slope): reed ends in streaks of gold and
    weathered brown running down it, laid in courses, each course's foot a dark line of shadow,
    greyer and greener toward the ridge."""
    key = np.asarray(rk['key'], np.float32)
    key /= np.linalg.norm(key)
    at = np.nonzero(alpha.reshape(-1))[0]
    ys, xs = at // w, at % w
    nrm = np.cross(u, v)
    lit = float(np.clip((nrm / np.linalg.norm(nrm)) @ key, 0, 1))
    a = (xs + 0.5) / w * np.linalg.norm(u)                            # along the ridge, units
    d = (ys + 0.5) / h * np.linalg.norm(v)                            # down the slope from the ridge
    P = np.stack([a / 0.05, d / 0.3, np.zeros_like(a)], 1)
    streak = noise3(P, 1.0, seed) * 0.6 + noise3(P * 2.1, 1.0, seed + 1) * 0.4
    course = d / 0.22 + 0.25 * noise3(np.stack([a / 0.6, d, np.zeros_like(a)], 1), 1.0, seed + 2)
    foot = (course - np.floor(course)) > 0.88                        # the shadow under each course
    val = rk['shade'][0] + rk['shade'][1] * lit + tone + 0.5 * (streak - 0.5) - 0.1 * foot - 0.12 * d / (d.max() + 1e-6)
    patch_ = noise3(np.stack([a, d, np.zeros_like(a)], 1), 0.25, seed + 3)
    mat = ((patch_ > 0.86) | (d < 0.05 + 0.05 * noise3(np.stack([a / 0.3, d, d], 1), 1.0, seed + 4))).astype(int)
    bay = BAYER4[ys % 4, xs % 4]
    rgb = np.zeros((h * w, 3), np.float32)
    for m, rp in enumerate(rk['ramps']):
        sel = mat == m
        idx = np.clip(np.round(val[sel] * (len(rp) - 1) + (bay[sel] - 0.5) * 0.35), 0, len(rp) - 1).astype(int)
        rgb[at[sel]] = np.asarray(rp, np.float32)[idx]
    rgba = np.concatenate([rgb.reshape(h, w, 3), alpha.reshape(h, w, 1).astype(np.float32)], -1)
    return rgba, np.zeros((h, w), np.float32)


def _tiles(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """Clay tiles on a roof's slope (a panel whose v runs down it): in courses, each tile its own
    shade of terracotta, the joints staggered course to course, each course's foot overlapping the
    next in a line of shadow, lichen on a few. Also bricks for a chimney, when `bricks`."""
    key = np.asarray(rk['key'], np.float32)
    key /= np.linalg.norm(key)
    at = np.nonzero(alpha.reshape(-1))[0]
    ys, xs = at // w, at % w
    nrm = np.cross(u, v)
    lit = float(np.clip((nrm / np.linalg.norm(nrm)) @ key, 0, 1))
    a = (xs + 0.5) / w * np.linalg.norm(u)
    d = (ys + 0.5) / h * np.linalg.norm(v)
    ch, cw = rk['course']
    row = np.floor(d / ch).astype(np.int64)
    col = np.floor(a / cw + 0.5 * (row % 2)).astype(np.int64)
    fd, fa = d / ch - row, a / cw + 0.5 * (row % 2) - col
    seam = (fd > 1 - 1.5 / (TEXELS * ch)) | (fa < 1.0 / (TEXELS * cw))
    val = (rk['shade'][0] + rk['shade'][1] * lit + tone + (table(5, row * 7919 + col * 31 + seed) - 0.5) * 0.18
           + 0.08 * (0.5 - fd) - 0.28 * seam)
    mat = ((table(4, row * 104729 + col * 13 + seed) < rk.get('lichen', 0.0)) & (fd > 0.3)).astype(int)
    bay = BAYER4[ys % 4, xs % 4]
    rgb = np.zeros((h * w, 3), np.float32)
    for m, rp in enumerate(rk['ramps']):
        sel = mat == m
        idx = np.clip(np.round(val[sel] * (len(rp) - 1) + (bay[sel] - 0.5) * 0.35), 0, len(rp) - 1).astype(int)
        rgb[at[sel]] = np.asarray(rp, np.float32)[idx]
    rgba = np.concatenate([rgb.reshape(h, w, 3), alpha.reshape(h, w, 1).astype(np.float32)], -1)
    return rgba, np.zeros((h, w), np.float32)


def _plaster(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """Limewash or ochre plaster on a wall, lit like rock: mottled a little, darker toward its foot."""
    key = np.asarray(rk['key'], np.float32)
    key /= np.linalg.norm(key)
    at = np.nonzero(alpha.reshape(-1))[0]
    ys, xs = at // w, at % w
    P = o + ((xs + 0.5) / w)[:, None] * u + ((ys + 0.5) / h)[:, None] * v
    nrm = np.cross(u, v)
    lit = float(np.clip((nrm / np.linalg.norm(nrm)) @ key, 0, 1))
    val = (rk['shade'][0] + rk['shade'][1] * lit + tone + 0.16 * (noise3(P, 0.35, seed) - 0.5)
           + 0.08 * (noise3(P, 0.08, seed + 1) - 0.5) - 0.06 * ((ys + 0.5) / h))
    rp = np.asarray(rk['ramps'][0], np.float32)
    idx = np.clip(np.round(val * (len(rp) - 1) + (BAYER4[ys % 4, xs % 4] - 0.5) * 0.35), 0, len(rp) - 1).astype(int)
    rgb = np.zeros((h * w, 3), np.float32)
    rgb[at] = rp[idx]
    rgba = np.concatenate([rgb.reshape(h, w, 3), alpha.reshape(h, w, 1).astype(np.float32)], -1)
    return rgba, np.zeros((h, w), np.float32)


PLASTER = dict(paint=_plaster, key=(-0.4, 0.45, 0.8), shade=(0.4, 0.5))

def _snow_roof(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """A roof under snow (a panel whose v runs down the slope): snow lying deep in soft drifts, blue in
    its hollows, thinner at the ridge where the shingles' dark edges show through, and at the eave a
    rounded lip of it over a dark line of board."""
    key = np.asarray(rk['key'], np.float32)
    key /= np.linalg.norm(key)
    at = np.nonzero(alpha.reshape(-1))[0]
    ys, xs = at // w, at % w
    nrm = np.cross(u, v)
    lit = float(np.clip((nrm / np.linalg.norm(nrm)) @ key, 0, 1))
    a = (xs + 0.5) / w * np.linalg.norm(u)
    d = (ys + 0.5) / h * np.linalg.norm(v)
    P = np.stack([a, d, np.zeros_like(a)], 1)
    drift = noise3(P / np.array([1.2, 0.5, 1.0], np.float32), 1.0, seed) * 0.6 + noise3(P, 0.25, seed + 1) * 0.4
    val = rk['shade'][0] + rk['shade'][1] * lit + tone + 0.3 * (drift - 0.5)
    depth_ = d.max() - d                                             # how far above the eave
    val = val + 0.08 * np.clip(1 - depth_ / 0.12, 0, 1)            # the lip catches the light
    thin = (d < 0.25 * (0.6 + noise3(P / np.array([0.5, 1.0, 1.0], np.float32), 1.0, seed + 2)))
    shingle = thin & (((d / 0.09) % 1.0) > 0.78)                     # their edges, showing at the ridge
    mat = (shingle | (depth_ < 0.025)).astype(int)                  # the board under the lip
    bay = BAYER4[ys % 4, xs % 4]
    rgb = np.zeros((h * w, 3), np.float32)
    for m, rp in enumerate(rk['ramps']):
        sel = mat == m
        idx = np.clip(np.round(val[sel] * (len(rp) - 1) + (bay[sel] - 0.5) * 0.35), 0, len(rp) - 1).astype(int)
        rgb[at[sel]] = np.asarray(rp, np.float32)[idx]
    rgba = np.concatenate([rgb.reshape(h, w, 3), alpha.reshape(h, w, 1).astype(np.float32)], -1)
    return rgba, np.zeros((h, w), np.float32)


def _glass_roof(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """Glazing: panes of glass, faintly green and catching the sky, between white iron glazing bars
    running down the slope and a few across - painted with each texel's own opacity, to be drawn as glass."""
    at = np.nonzero(alpha.reshape(-1))[0]
    ys, xs = at // w, at % w
    a = (xs + 0.5) / w * np.linalg.norm(u)
    d = (ys + 0.5) / h * np.linalg.norm(v)
    bar = ((a % rk['bars'][0]) < 0.035) | ((d % rk['bars'][1]) < 0.03)
    rgb = np.zeros((h * w, 3), np.float32)
    op = np.zeros(h * w, np.float32)
    bar_c = np.asarray(rk['ramps'][0], np.float32)
    rgb[at] = np.where(bar[:, None], bar_c[-2], rk['glass'])
    op[at] = np.where(bar, 1.0, rk['opacity'] + 0.06 * noise3(np.stack([a, d, np.zeros_like(a)], 1), 0.6, seed))
    rgba = np.concatenate([rgb.reshape(h, w, 3), (op * alpha.reshape(-1)).reshape(h, w, 1)], -1)
    return rgba, np.zeros((h, w), np.float32)


# Roof covers, painted by _thatch, _tiles, _snow_roof and _glass_roof and lit like rock; `chimney` is brick in courses.
ROOFS = {
    'thatch': dict(paint=_thatch, ramps=[ramp('#a88a52', dark=0.38, light=1.4, warm=0.1), ramp('#7e7a5a', dark=0.4, light=1.3)],
                   key=(-0.4, 0.45, 0.8), shade=(0.36, 0.5)),
    'tile': dict(paint=_tiles, ramps=[ramp('#9a5038', dark=0.36, light=1.35, warm=0.08), ramp('#8a8a5a', dark=0.4, light=1.3)],
                 key=(-0.4, 0.45, 0.8), shade=(0.36, 0.5), course=(0.1, 0.13), lichen=0.06),
    'snow': dict(paint=_snow_roof, ramps=[SNOW, ramp('#3e3630', dark=0.5, light=1.6)], key=(-0.4, 0.45, 0.8),
                 shade=(0.44, 0.5)),
    'glass': dict(paint=_glass_roof, ramps=[ramp('#e2e0d6', dark=0.45, light=1.12)], key=(-0.4, 0.45, 0.8),
                  shade=(0.44, 0.5), glass=np.array([0.78, 0.9, 0.86], np.float32), opacity=0.16, bars=(0.36, 0.9)),
    'slate': dict(paint=_tiles, ramps=[ramp('#4a4e5a', dark=0.45, light=1.55, cool=0.2), ramp('#5e6a4c', dark=0.4, light=1.3)],
                  key=(-0.4, 0.45, 0.8), shade=(0.34, 0.52), course=(0.075, 0.15), lichen=0.05),
    'chimney': dict(paint=_tiles, ramps=[ramp('#8a4a36', dark=0.36, light=1.3)], key=(-0.4, 0.45, 0.8),
                    shade=(0.38, 0.5), course=(0.06, 0.12)),
}


def market_stand(pl):
    """A market stand: a trestle table of boards, 1.5 long, a striped skirt hanging from its front,
    under a striped awning on four poles that slopes down to the front, a scalloped valance round it;
    goods heaped on the table - apples, cabbages, loaves - and crates by it, as billboards. Faces +x:
    the customers stand there."""
    seed = int(pl.get('seed', 1))
    wood = _timber(pl, (0.025, 0.4, 0.025), 0.12)                    # boards along the table
    post = _timber(pl, (0.025, 0.025, 0.4), 0.5)
    d0, d1, half, top = -0.28, 0.24, 0.75, 0.42                      # the table: back, front, half length
    parts = [_rock(wood, seed, (d1, -half, top), (d1, half, top), (d0, -half, top)),           # its top
             _rock(wood, seed + 1, (d1, half, top), (d1, -half, top), (d1, half, top - 0.05)),   # its edge
             _rock(wood, seed + 2, (d0, -half, top), (d0, half, top), (d0, -half, top - 0.05))]
    for y in (-half + 0.12, half - 0.12):                           # trestles: a pair of legs at each end
        for x in (d0 + 0.05, d1 - 0.05):
            parts += [p for p in (_rock(post, seed + 5, (x + 0.02, y + 0.02, top - 0.05), (x + 0.02, y - 0.02, top - 0.05),
                                        (x + 0.02, y + 0.02, 0.0)),
                                  _rock(post, seed + 6, (x - 0.02, y - 0.02, top - 0.05), (x - 0.02, y + 0.02, top - 0.05),
                                        (x - 0.02, y - 0.02, 0.0)),
                                  _rock(post, seed + 7, (x - 0.02, y + 0.02, top - 0.05), (x + 0.02, y + 0.02, top - 0.05),
                                        (x - 0.02, y + 0.02, 0.0)),
                                  _rock(post, seed + 8, (x + 0.02, y - 0.02, top - 0.05), (x - 0.02, y - 0.02, top - 0.05),
                                        (x + 0.02, y - 0.02, 0.0)))]
    xf, xb, zf, zb = 0.52, -0.46, 1.22, 1.46                          # the awning's front and back edges
    for x, z in ((xf - 0.04, zf + (zb - zf) * 0.04 / (xf - xb)), (xb + 0.04, zb - (zb - zf) * 0.04 / (xf - xb))):
        for y in (-half - 0.04, half + 0.04):                         # the poles
            parts += box((x - 0.022, y - 0.022, 0.0), (x + 0.022, y + 0.022, z),
                         {f: _solid_cached(3, _texels(z), '#4a3828') for f in ('front', 'back', 'right', 'left')})
    aw, stripe, vh = half + 0.12, 7, 0.12
    T = _texels
    parts.append(quad(_awning(T(2 * aw), T(math.hypot(xf - xb, zb - zf)), stripe),
                      (xf, -aw, zf), (xf, aw, zf), (xb, -aw, zb), back=0.85))
    val = _valance(T(2 * aw), T(vh), stripe)
    parts.append(quad((val[0][:, ::-1], val[1][:, ::-1]), (xf, aw, zf), (xf, -aw, zf), (xf, aw, zf - vh), back=0.85))
    for y, sgn in ((aw, 1), (-aw, -1)):                              # its sides, along the slope
        tl, tr = ((xb, y, zb), (xf, y, zf)) if sgn > 0 else ((xf, y, zf), (xb, y, zb))
        parts.append(quad(_valance(T(math.hypot(xf - xb, zb - zf)), T(vh), stripe), tl, tr,
                          (tl[0], tl[1], tl[2] - vh), back=0.85))
    skirt = _valance(T(2 * half), T(top - 0.12), stripe)             # its skirt, in step with the awning
    parts.append(quad((skirt[0][:, ::-1], skirt[1][:, ::-1]), (d1 + 0.01, half, top - 0.04),
                      (d1 + 0.01, -half, top - 0.04), (d1 + 0.01, half, 0.08), back=0.8))
    ct = top + 0.005                                                  # the goods on the table
    for y, kind in ((-0.48, 'apples'), (0.0, 'cabbages'), (0.48, 'loaves')):
        parts.append(sprite(f'goods_{kind}', 0.04, y, ct))
    parts += [sprite('crate', d1 + 0.12, -0.42, 0.0, scale=0.3), sprite('crate', d1 + 0.1, 0.36, 0.0, scale=0.28),
              sprite('sack', d0 - 0.12, 0.62, 0.0, scale=0.3)]
    parts.append(shadow(0.0, 0.0, 1.8, 0.5))
    return [p for p in parts if p]


MAHOGANY = ramp('#5a2e1e', dark=0.3, light=1.5)
BAR_BRASS = ramp('#c8a048', dark=0.35, light=1.6, warm=0.1)


@functools.lru_cache(maxsize=None)
def _bar_front(w, h):
    """A saloon bar's front: raised panels of dark mahogany between pilasters, a moulding along the
    top and a dark kick rail at the foot."""
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.3, top=1.0, bevel=0, mat=0, tone=-0.08)
    step = 30
    for x in range(0, w, step):
        cv.box(x, 2, 4, h - 6, z=0.9, top=1.0, bevel=0.6, mat=0, tone=0.05)          # a pilaster
        cv.box(x + 7, 6, step - 10, h - 14, z=0.7, top=0.8, bevel=1.8, mat=0)         # a raised panel
    cv.box(0, 0, w, 3, z=1.0, top=1.0, bevel=0.5, mat=0, tone=0.1)                    # the moulding
    cv.box(0, h - 4, w, 4, z=0.8, top=1.0, bevel=0.4, mat=0, tone=-0.2)               # the kick rail
    return _finish(cv, [MAHOGANY], relief=0.9)


def saloon_bar(pl):
    """A saloon's bar: a counter of dark mahogany `length` long (default 3) across the way it faces,
    0.38 tall - raised panels between pilasters on its front, a polished top overhanging the drinkers'
    side, the bartender's shelves behind - with a brass foot rail on brackets along its foot and
    bottles standing on it. Faces +x: the drinkers stand there."""
    T = _texels
    half = float(pl.get('length', 3.0)) / 2
    d0, d1, top = -0.15, 0.15, 0.38
    parts = box((d0, -half, 0.0), (d1, half, top),
                {'front': _bar_front(T(2 * half), T(top)), 'back': _counter_back(T(2 * half), T(top)),
                 'right': _bar_front(T(d1 - d0), T(top)), 'left': _bar_front(T(d1 - d0), T(top))})
    slab = (d0 - 0.02, -half - 0.03, top), (d1 + 0.05, half + 0.03, top + 0.025)
    gloss = _solid_cached(T(2 * half + 0.06), T(slab[1][0] - slab[0][0]), '#7a3a22')
    edge = _solid_cached(T(2 * half + 0.06), 2, '#4a2416')
    side = _solid_cached(T(slab[1][0] - slab[0][0]), 2, '#4a2416')
    parts += box(*slab, {'top': gloss, 'front': edge, 'back': edge, 'right': side, 'left': side, 'bottom': edge})
    rail = _solid_cached(T(2 * half), 3, '#c8a048')
    end = _solid_cached(3, 3, '#c8a048')
    parts += box((d1 + 0.06, -half + 0.02, 0.05), (d1 + 0.09, half - 0.02, 0.08),        # the foot rail
                 {'front': rail, 'back': rail, 'top': rail, 'bottom': rail, 'right': end, 'left': end})
    k = max(2, int(round(2 * half / 0.6)))
    for i in range(k + 1):                                            # its brackets
        y = -half + 0.05 + (2 * half - 0.1) * i / k
        parts += box((d1, y - 0.01, 0.06), (d1 + 0.07, y + 0.01, 0.075),
                     {f: _solid_cached(4, 2, '#a8803a') for f in ('top', 'right', 'left')})
    ct = top + 0.026
    for i, y in enumerate(np.linspace(-half + 0.3, half - 0.3, max(2, int(half)))):
        parts.append(sprite('bottles', d0 + 0.07, float(y), ct, scale=0.1, flip=bool(i % 2)))
    parts.append(shadow(0.0, 0.0, 2 * half + 0.4, 0.4))
    return [p for p in parts if p]


IRON_RUST = ramp('#5a4436', dark=0.4, light=1.5)
IRON_DARK = ramp('#3e3c3e', dark=0.45, light=1.7)


@functools.lru_cache(maxsize=None)
def _iron_side(w, h):
    """A riveted plate of iron gone to rust: a row of rivets along its top and foot, streaks of rust
    running down from them."""
    rng = np.random.default_rng(w * 31 + h)
    cv = Canvas(w, h, wrap=False)
    cv.box(0, 0, w, h, z=0.5, top=1.0, bevel=0, mat=0)
    cv.noise(0.1, cells=4, rng=rng)
    for y in (2, h - 3):
        for x in range(3, w - 2, 6):
            cv.ellipse(x, y, 1.0, 1.0, z=1.0, dome=0.8, mat=1)                      # rivets
    for _ in range(max(2, w // 10)):                                               # rust run down
        x = rng.uniform(2, w - 2)
        cv.stroke([(x, 3), (x + rng.normal(0, 0.6), rng.uniform(h * 0.4, h - 3))], 0.9, z=0.55, dome=0.2, mat=1,
                  tone=-0.05)
    cv.box(0, 0, w, 2, z=1.1, top=1.0, bevel=0.4, mat=1, tone=0.06)               # the rolled lip
    return _finish(cv, [IRON_RUST, IRON_DARK], relief=0.8)


def rails(pl):
    """A narrow track of the kind a mine runs: two iron rails `length` long the way it faces, `gauge`
    apart (default 0.24), on wooden sleepers every 0.22, laid on the ground - the rails' tops worn
    bright."""
    half = float(pl.get('length', 4.0)) / 2
    g = float(pl.get('gauge', 0.24)) / 2
    parts = []
    n = max(1, int(round(2 * half / 0.22)))
    for k in range(n):                                                # the sleepers, across the track
        x = -half + (k + 0.5) * 2 * half / n
        tex = _solid_cached(_texels(2 * g + 0.16), 5, ('#5e4a38', '#54422f', '#665240')[k % 3])
        edge = _solid_cached(_texels(2 * g + 0.16), 2, '#3a2e24')
        parts += box((x - 0.035, -g - 0.08, 0.0), (x + 0.035, g + 0.08, 0.03),
                     {'top': tex, 'front': edge, 'back': edge})
    for y in (-g, g):                                                 # the rails
        top = _solid_cached(_texels(2 * half), 2, '#9a9a9e')
        side = _solid_cached(_texels(2 * half), 2, '#4a3c34')
        parts += box((-half, y - 0.012, 0.03), (half, y + 0.012, 0.06), {'top': top, 'right': side, 'left': side})
    return [p for p in parts if p]


def ore_cart(pl):
    """An ore cart: a riveted iron tub on a low frame and four small wheels set to the rails, its
    length the way it faces; ore heaped in it (`"ore": false` leaves it empty)."""
    T = _texels
    L, w, z0, z1 = 0.24, 0.16, 0.1, 0.34
    side_l, side_w = _iron_side(T(2 * L), T(z1 - z0)), _iron_side(T(2 * w), T(z1 - z0))
    parts = box((-L, -w, z0), (L, w, z1), {'right': side_l, 'left': side_l, 'front': side_w, 'back': side_w,
                                           'bottom': _solid_cached(T(2 * w), T(2 * L), '#2e2a28')})
    parts += box((-L + 0.03, -w + 0.02, z1 - 0.12), (L - 0.03, w - 0.02, z1 - 0.12),
                 {'top': _solid_cached(T(2 * w - 0.04), T(2 * L - 0.06), '#3a3230')})     # its floor inside
    frame = _solid_cached(T(2 * L), 3, '#2a2626')
    parts += box((-L + 0.02, -w + 0.03, 0.06), (L - 0.02, w - 0.03, z0), {f: frame for f in ('front', 'back', 'right', 'left')})
    for x in (-L + 0.07, L - 0.07):                                   # the wheels, on the rails
        for y in (-0.13, 0.13):
            parts += box((x - 0.045, y - 0.012, 0.015), (x + 0.045, y + 0.012, 0.105),
                         {f: _solid_cached(4, 4, '#262222') for f in ('front', 'back', 'right', 'left', 'top')})
    if pl.get('ore', True):
        parts.append(sprite('ore_heap', 0.0, 0.0, z1 - 0.08, scale=0.14))
    parts.append(shadow(0.0, 0.0, 0.7, 0.45))
    return [p for p in parts if p]


# ------------------------------------------------------------------ a ship's hull

def ship_hull(pl):
    """A wooden ship's hull, open (no deck): `length` long the way it faces (the bow), `width` across at
    its widest, `depth` from the keel to the gunwale - a square stern, the sides curving out from the keel
    to their widest a little aft of the middle and in to a pointed bow whose stem sweeps up, the gunwale
    rising toward both ends; planked in boards along its length, ribs inside. `heel` lists it over (degrees,
    toward its starboard side, +y), `broken` (0-1) staves in that much of its starboard side, the ribs
    showing; sink it into a sea floor with a negative `z`."""
    wood = _timber(dict(pl, material=pl.get('material', 'wood')), (0.4, 0.025, 0.025), 0.12)
    rib = _timber(dict(pl, material=pl.get('material', 'wood')), (0.025, 0.025, 0.4), 0.5)
    seed = int(pl.get('seed', 1))
    rng = np.random.default_rng(seed)
    L, B, D = float(pl.get('length', 5.0)), float(pl.get('width', 1.6)), float(pl.get('depth', 1.0))
    heel = math.radians(float(pl.get('heel', 0.0)))
    broken = float(pl.get('broken', 0.0))
    n, m = 14, 5                                                      # stations along it, points up each side
    ch, sh = math.cos(heel), math.sin(heel)

    def at(t, j, side):
        """The hull's surface at station t (0 stern, 1 bow), j of m up from the keel, side +1 or -1."""
        w = B / 2 * ((0.8 + 0.2 * math.sin(math.pi / 2 * t / 0.42)) if t <= 0.42
                     else max(0.0, math.cos(math.pi / 2 * (t - 0.42) / 0.58)) ** 0.75)
        kz = 0.45 * D * max(0.0, (t - 0.8) / 0.2) ** 2                 # the stem sweeps up
        hz = D * (1 + 0.16 * (2 * t - 1) ** 2)                         # the gunwale's sheer
        th = math.pi / 2 * j / m
        y, z = side * w * math.sin(th), kz + (hz - kz) * (1 - math.cos(th))
        x = (t - 0.5) * L
        return np.array([x, y * ch - z * sh, y * sh + z * ch])

    ts = [k / (n - 1) for k in range(n)]
    hole = (0.38, 0.38 + 0.42 * broken)                               # where the starboard side is stove in
    parts = []
    for side in (1, -1):
        for i in range(n - 1):
            for j in range(m):
                if side > 0 and hole[0] <= ts[i] < hole[1] and j >= 1 and rng.random() < 0.85:
                    continue                                          # stove in
                A, Bq, C, E = at(ts[i], j, side), at(ts[i + 1], j, side), at(ts[i + 1], j + 1, side), at(ts[i], j + 1, side)
                mid = np.array([(A[0] + Bq[0]) / 2, 0.0, D * 0.9])
                mid = np.array([mid[0], -mid[2] * sh, mid[2] * ch])
                out = (A + Bq + C + E) / 4 - mid
                parts += [_rock_tri(wood, seed + i, A, Bq, C, out), _rock_tri(wood, seed + i, A, C, E, out)]
    for i in range(1, n - 1, 2):                                      # ribs inside, every other station
        for j in range(m):
            for side in (1, -1):
                A, C = at(ts[i], j, side), at(ts[i], j + 1, side)
                dx = np.array([0.04, 0.0, 0.0])
                inward = -(A + C) / 2 + np.array([(A[0] + C[0]) / 2, -D * 0.9 * sh, D * 0.9 * ch])
                step = 0.035 * inward / max(np.linalg.norm(inward), 1e-6)     # just inside the planks
                A, C = A + step, C + step
                parts.append(_rock_tri(rib, seed + 50, A - dx, A + dx, C + dx, inward))
                parts.append(_rock_tri(rib, seed + 50, A - dx, C + dx, C - dx, inward))
    keel = at(0.0, 0, 1)                                              # the transom, closing the stern
    for side in (1, -1):
        for j in range(1, m):
            A, C = at(0.0, j, side), at(0.0, j + 1, side)
            parts.append(_rock_tri(wood, seed + 70, keel, A, C, np.array([-1.0, 0.0, 0.0])))
    for side in (1, -1):                                              # a rail along the gunwale
        for i in range(n - 1):
            A, Bq = at(ts[i], m, side), at(ts[i + 1], m, side)
            if side > 0 and hole[0] <= ts[i] < hole[1]:
                continue
            up = np.array([0.0, -0.06 * sh, 0.06 * ch])
            parts.append(_rock(wood, seed + 80, A + up, Bq + up, A))
    parts = [p for p in parts if p]
    parts.append(shadow(0.0, 0.0, L * 0.9, 0.5))
    return parts


def _moved(parts, dx=0.0, dy=0.0, dz=0.0):
    """Parts built about the origin, moved: panels by their corners, sprites, lights and shadows by
    their places."""
    out = []
    for p in parts:
        p = dict(p)
        if p['part'] == 'panel':
            for k in ('tl', 'tr', 'bl'):
                x, y, z = p[k]
                p[k] = (x + dx, y + dy, z + dz)
        else:
            p['dx'], p['dy'] = p['dx'] + dx, p['dy'] + dy
            if 'z' in p:
                p['z'] = p['z'] + dz
        out.append(p)
    return out


SAIL_RED = ramp('#a8382c', dark=0.38, light=1.3)
SAIL_CREAM = ramp('#d8ccae', dark=0.45, light=1.12)


@functools.lru_cache(maxsize=None)
def _sail(w, h, stripe):
    """A square sail of wool in broad red and cream stripes, bellied a little - its middle lighter."""
    cv = Canvas(w, h, wrap=False)
    for k, x in enumerate(range(0, w, stripe)):
        cv.box(x, 0, min(stripe, w - x), h, z=0.5, top=0.7, bevel=1.0, mat=k % 2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cv.tone += (0.12 * np.exp(-(((xx - w / 2) / (w * 0.45)) ** 2 + ((yy - h * 0.45) / (h * 0.5)) ** 2))).astype(np.float32)
    rgba, em = _finish(cv, [SAIL_RED, SAIL_CREAM], relief=0.5)
    rgba = rgba.copy()
    rgba[0:2, :, :3] *= 0.6                                          # the head lashed to the yard
    return rgba, em


def longship(pl):
    """A longship: a long open hull of overlapping boards, its stem and stern curling up high, a mast
    amidships with a yard across it and a square sail in red and cream stripes (`"sail": false` furls
    it), round shields along both sides at the gunwale; `length` long the way it faces (default 7),
    `heel` lists it as for a hull, drawn up on a beach."""
    L = float(pl.get('length', 7.0))
    B, D = L * 0.2, L * 0.13
    hull = dict(pl, length=L, width=B, depth=D, broken=0)
    parts = ship_hull(hull)
    heel = math.radians(float(pl.get('heel', 0.0)))
    ch, sh = math.cos(heel), math.sin(heel)

    def tilt(x, y, z):                                                # heeled as the hull is
        return (x, y * ch - z * sh, y * sh + z * ch)
    seed = int(pl.get('seed', 1))
    wood = _timber(dict(pl, material='wood'), (0.025, 0.025, 0.4), 0.5)
    for end, sgn in ((L / 2, 1), (-L / 2, -1)):                       # stem and stern posts, curling up and over
        pts = [(end - sgn * 0.12, 0.0, D * 1.0), (end + sgn * 0.05, 0.0, D * 1.35), (end + sgn * 0.12, 0.0, D * 1.7),
               (end + sgn * 0.08, 0.0, D * 2.05), (end - sgn * 0.08, 0.0, D * 2.25), (end - sgn * 0.22, 0.0, D * 2.15)]
        for k, (p, q) in enumerate(zip(pts, pts[1:])):
            a, b = np.array(tilt(*p)), np.array(tilt(*q))
            for w_ in (-0.04, 0.04):
                off = np.array(tilt(0.0, w_, 0.0))
                parts.append(_rock_tri(wood, seed + 90 + k, a + off, b + off, b - off, off))
                parts.append(_rock_tri(wood, seed + 90 + k, a + off, b - off, a - off, off))
    H = L * 0.62                                                     # the mast, the yard, the sail
    mast = column({'material': 'wood', 'sides': 6, 'radius': L * 0.012, 'top': 0.8, 'height': H, 'sink': 0.0,
                   'seed': seed + 100, 'angle': pl.get('angle', 0.0)})
    parts += _moved(mast, *tilt(-L * 0.02, 0.0, D * 0.2))
    yz, yl = D * 0.2 + H * 0.88, B * 2.4
    if pl.get('sail', True):
        top, foot = yz, yz - H * 0.62
        a, b = tilt(-L * 0.02 + 0.05, -yl / 2, top), tilt(-L * 0.02 + 0.05, yl / 2, top)
        c = tilt(-L * 0.02 + 0.05, -yl / 2, foot)
        tex = _sail(_texels(yl), _texels(top - foot), max(6, _texels(yl) // 7))
        parts.append(quad(tex, a, b, c, back=0.75))
        parts.append(quad((tex[0][:, ::-1], tex[1][:, ::-1]), b, a, tilt(-L * 0.02 + 0.05, yl / 2, foot), back=0.75))
    yard = beam({'material': 'wood', 'length': yl + 0.2, 'width': 0.06, 'depth': 0.06, 'seed': seed + 101})
    for p in yard:                                                    # turned across the ship
        q = dict(p)
        for k in ('tl', 'tr', 'bl'):
            x, y, z = p[k]
            q[k] = tilt(-L * 0.02 - y, x, z + yz)
        parts.append(q)
    n = int(L * 1.6)
    for side in (1, -1):                                              # shields along the gunwale, each side
        for k in range(n):
            t = 0.22 + 0.56 * (k + 0.5) / n
            x = (t - 0.5) * L
            w = B / 2 * (0.8 + 0.2 * math.sin(math.pi / 2 * t / 0.42) if t <= 0.42
                         else max(0.0, math.cos(math.pi / 2 * (t - 0.42) / 0.58)) ** 0.75)
            gz = D * (1 + 0.16 * (2 * t - 1) ** 2)
            sx, sy, sz = tilt(x, side * (w + 0.03), gz - 0.12)
            parts.append(sprite('round_shield', sx, sy, sz, planes=1, angle=float(pl.get('angle', 0.0)),
                                length=0.32, scale=0.32, shadow=False, flip=bool(k % 2)))
    return parts


def lighthouse(pl):
    """A lighthouse: a round tower of whitewashed masonry `height` tall (default 8) and `radius` at its foot
    (default 0.9), tapering to 0.7 of that, a red `band` round it (`false` for none) - smoothly shaded round
    - a gallery round its head with an iron rail, a lantern room of glass with the lamp in it (`lit`, by
    default true: it glows and lights the night round it) and a domed iron cap with a ball on top."""
    seed = int(pl.get('seed', 1))
    H, R = float(pl.get('height', 8.0)), float(pl.get('radius', 0.9))
    white = _material(dict(pl, material='lime_white'))
    red = _material(dict(pl, material='lime_red'))
    iron = _material(dict(pl, material='iron_green'))
    n = 18
    smooth = -math.tan(math.pi / n)
    rad = lambda z: R * (1 - 0.3 * z / H)                             # noqa: E731
    cuts = [0.0, H * 0.58, H * 0.7, H] if pl.get('band', True) else [0.0, H]
    parts = []
    for k, (z0, z1) in enumerate(zip(cuts, cuts[1:])):                 # the tower, white and a red band
        mat = red if (len(cuts) > 2 and k == 1) else white
        parts += _prism_faces(mat, seed + k, n, rad(z0), rad(z1), z0 - (0.02 if k == 0 else 0.0), z1, 0.0,
                              flute=smooth, block=True)
    rg = rad(H) + 0.28                                                 # the gallery: a deck on corbels, a rail
    parts += _prism_faces(white, seed + 10, n, rad(H) - 0.02, rg, H - 0.24, H, 0.0, flute=smooth, block=True)
    parts.append(_disc(iron, seed + 11, n, rg, H, 0.0))
    parts += _prism_faces(iron, seed + 12, n, rg - 0.01, rg - 0.01, H + 0.26, H + 0.32, 0.0, block=True)
    for k in range(n):                                                 # the rail's posts
        a = 2 * math.pi * k / n
        x, y = (rg - 0.02) * math.cos(a), (rg - 0.02) * math.sin(a)
        parts += box((x - 0.015, y - 0.015, H), (x + 0.015, y + 0.015, H + 0.3),
                     {f: _solid_cached(2, 18, '#2e4236') for f in ('front', 'back', 'right', 'left')})
    rl, zl, hl = rad(H) * 0.72, H, 1.0                                 # the lantern room
    glass = dict(ROOFS['glass'], bars=(rl * 2 * math.sin(math.pi / 10) / 2, 0.34), opacity=0.12)
    for k in range(10):
        a0, a1 = 2 * math.pi * k / 10, 2 * math.pi * (k + 1) / 10
        A = np.array([rl * math.cos(a0), rl * math.sin(a0), zl + hl])
        B = np.array([rl * math.cos(a1), rl * math.sin(a1), zl + hl])
        if np.cross(B - A, np.array([0.0, 0.0, -1.0])) @ (A + B) < 0:
            A, B = B, A
        p = _rock(glass, seed + 20 + k, A, B, A - np.array([0.0, 0.0, hl]))
        if p:
            p['translucent'] = True
            parts.append(p)
    parts += _prism_faces(iron, seed + 30, 10, rl, rl * 1.05, zl + hl, zl + hl + 0.08, 0.0, block=True)
    dome = [(1.05, 0.0), (0.98, 0.18), (0.78, 0.4), (0.45, 0.58), (0.14, 0.66), (0.0, 0.68)]
    for k, ((r0, z0), (r1, z1)) in enumerate(zip(dome, dome[1:])):     # the dome, and the ball on it
        parts += _prism_faces(iron, seed + 40 + k, 12, max(rl * r0, 1e-3), max(rl * r1, 1e-3), zl + hl + 0.08 + z0 * rl,
                              zl + hl + 0.08 + z1 * rl, 0.0, flute=-math.tan(math.pi / 12), block=True)
    zb = zl + hl + 0.08 + 0.68 * rl
    parts += _prism_faces(iron, seed + 50, 8, 0.06, 0.06, zb, zb + 0.12, 0.0, block=True)
    parts.append(_disc(iron, seed + 51, 8, 0.06, zb + 0.12, 0.0))
    if pl.get('lit', True):                                            # the lamp in the lantern room
        parts.append(sprite('orb', 0.0, 0.0, zl + 0.05, scale=hl * 0.9, shadow=False))
        parts.append(light(0.0, 0.0, zl + 0.5, 9.0, (1.0, 0.86, 0.6), 1.6))
    parts.append(shadow(0.0, 0.0, 2.6 * R, 0.5))
    return [p for p in parts if p]


def stone_lantern(pl):
    """A stone lantern for a garden: a hexagonal foot, a round shaft, a platform, a firebox of four posts
    with the flame showing between them (`lit`, default true: it glows and gives a little light), a wide
    six-sided roof sweeping out, a ball finial; `height` tall (default 1.1), of `material` (default
    `stone`) - the moss grows on its tops."""
    mat = _material(dict(pl, material=pl.get('material', 'stone')))
    seed = int(pl.get('seed', 1))
    H = float(pl.get('height', 1.1))
    u = H / 1.1
    ph = math.pi / 6
    parts = []
    parts += _prism_faces(mat, seed, 6, 0.2 * u, 0.17 * u, 0.0, 0.1 * u, ph, block=True)                    # the foot
    parts.append(_disc(mat, seed + 1, 6, 0.17 * u, 0.1 * u, ph))
    parts += _prism_faces(mat, seed + 2, 12, 0.07 * u, 0.06 * u, 0.1 * u, 0.5 * u, 0.0, flute=-math.tan(math.pi / 12),
                          block=True)                                                                           # the shaft
    parts += _prism_faces(mat, seed + 3, 6, 0.08 * u, 0.2 * u, 0.5 * u, 0.58 * u, ph, block=True)             # the platform
    parts.append(_disc(mat, seed + 4, 6, 0.2 * u, 0.58 * u, ph))
    for k in range(4):                                                # the firebox's posts
        a = math.pi / 4 + k * math.pi / 2
        x, y = 0.11 * u * math.cos(a), 0.11 * u * math.sin(a)
        parts += box((x - 0.025 * u, y - 0.025 * u, 0.58 * u), (x + 0.025 * u, y + 0.025 * u, 0.8 * u),
                     {f: _solid_cached(3, 14, '#7a7a6e') for f in ('front', 'back', 'right', 'left')})
    parts += _prism_faces(mat, seed + 5, 6, 0.3 * u, 0.12 * u, 0.8 * u, 0.92 * u, ph, block=True, tone=-0.02)  # the roof
    parts.append(_disc(mat, seed + 6, 6, 0.3 * u, 0.8 * u, ph, below=True))
    parts += _prism_faces(mat, seed + 7, 6, 0.12 * u, 0.03 * u, 0.92 * u, 0.98 * u, ph, block=True)
    parts += _prism_faces(mat, seed + 8, 8, 0.045 * u, 0.045 * u, 0.98 * u, 1.04 * u, 0.0, block=True)        # the finial
    parts += _prism_faces(mat, seed + 9, 8, 0.045 * u, 0.0, 1.04 * u, H, 0.0, block=True)
    if pl.get('lit', True):                                           # the flame in the firebox
        parts.append(sprite('candles', 0.0, 0.0, 0.58 * u, scale=0.16 * u, shadow=False))
        parts.append(light(0.0, 0.0, 0.7 * u, 2.2 * u, (1.0, 0.7, 0.38), 0.9))
    parts.append(shadow(0.0, 0.0, 0.6 * u, 0.5))
    return [p for p in parts if p]


def gear(pl):
    """A gear: a toothed wheel `size` across (default 2.0) and `depth` thick (default a tenth of its size),
    standing on its rim (lift it with `z`), its axle along x - turn it with `angle` to face where it
    should, flat to a wall say. `teeth` round it (default 24) and `spokes` (default 6) - both even, so
    its two faces agree; a rim, the spokes and a boss at the hub each a shade of their own; of
    `material`, default `brass` (gone green with verdigris in patches)."""
    mat = _material(dict(pl, material=pl.get('material', 'brass')))
    seed = int(pl.get('seed', 1))
    R = float(pl.get('size', 2.0)) / 2
    D = float(pl.get('depth', R * 0.2))
    n = max(2, int(pl.get('teeth', 24)) // 2 * 2)
    m = max(2, int(pl.get('spokes', 6)) // 2 * 2)
    root, rim, hub, sw = R * 0.86, R * 0.7, R * 0.24, R * 0.13

    def region(part):
        def mask(w, h):
            ys, xs = np.mgrid[0:h, 0:w]
            u, v = (xs + 0.5) / w * 2 - 1, 1 - (ys + 0.5) / h * 2
            r, th = np.hypot(u, v) * R, np.arctan2(v, u)
            d = np.abs((th / (2 * np.pi) * n) % 1.0 - 0.5)               # from the middle of a tooth's pitch
            edge = np.where(d < 0.16, R, np.where(d > 0.3, root, root + (R - root) * (0.3 - d) / 0.14))
            if part == 'rim':
                return (r <= edge) & (r >= rim)
            if part == 'boss':
                return r < hub * 0.62
            off = ((th / (2 * np.pi) * m + 0.5) % 1.0 - 0.5) * 2 * np.pi / m
            spoke = np.abs(r * np.sin(off)) < sw / 2
            return (r < rim) & (r >= hub * 0.62) & ((r < hub) | spoke)
        return mask

    parts = []
    for x, sgn in ((D / 2, 1), (-D / 2, -1)):                          # its two faces
        tl, tr, bl = (x, sgn * R, 2 * R), (x, -sgn * R, 2 * R), (x, sgn * R, 0.0)
        for part, tone in (('rim', 0.04), ('web', -0.1), ('boss', 0.1)):
            parts.append(_rock(mat, seed, tl, tr, bl, alpha=region(part), tone=tone))
    p = 2 * np.pi / n                                                  # the sides of its teeth, all round
    th = np.concatenate([[(k + 0.5) * p - 0.3 * p, (k + 0.5) * p - 0.16 * p, (k + 0.5) * p + 0.16 * p,
                          (k + 0.5) * p + 0.3 * p] for k in range(n)])
    rr = np.tile([root, R, R, root], n)
    ring = np.stack([rr * np.cos(th), R + rr * np.sin(th)], 1)
    for i in range(len(ring)):
        (y0, z0), (y1, z1) = ring[i], ring[(i + 1) % len(ring)]
        A, B, C = np.array([D / 2, y0, z0]), np.array([D / 2, y1, z1]), np.array([-D / 2, y0, z0])
        out = np.array([0.0, (y0 + y1) / 2, (z0 + z1) / 2 - R])
        if np.cross(B - A, C - A) @ out < 0:
            A, B, C = np.array([-D / 2, y0, z0]), np.array([-D / 2, y1, z1]), np.array([D / 2, y0, z0])
        parts.append(_rock(mat, seed + 1, A, B, C))
    return [q for q in parts if q]


# ------------------------------------------------------------------ chess pieces

def _polished(rk, seed, o, u, v, w, h, alpha, rim=None, tone=0.0, tilt=None):
    """Polished stone - a chess piece's marble: smooth, lit by the way each texel faces (with `tilt`, the
    faces of a turned piece shade round it smoothly), a sheen where it faces the light, and veins
    wandering through it."""
    key = np.asarray(rk['key'], np.float32)
    key /= np.linalg.norm(key)
    at = np.nonzero(alpha.reshape(-1))[0]
    ys, xs = at // w, at % w
    P = o + ((xs + 0.5) / w)[:, None] * u + ((ys + 0.5) / h)[:, None] * v
    nrm = np.cross(u, v)
    N = np.repeat((nrm / np.linalg.norm(nrm)).astype(np.float32)[None, :], len(at), 0)
    if tilt is not None:
        N += tilt.reshape(-1)[at][:, None] * (u / np.linalg.norm(u)).astype(np.float32)[None, :]
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    lit = np.clip(N @ key, 0, 1)
    sheen = np.clip((lit - 0.8) / 0.2, 0, 1) ** 2
    wander = noise3(P, 0.5, seed + 1) * 0.6
    vein = np.abs(noise3(P + wander[:, None], rk['vein'], seed) - 0.5)
    val = rk['shade'][0] + rk['shade'][1] * lit + 0.3 * sheen + tone - 0.1 * (vein < 0.05)
    mat = (vein < 0.02).astype(int)
    bay = BAYER4[ys % 4, xs % 4]
    rgb = np.zeros((h * w, 3), np.float32)
    for m, rp in enumerate(rk['ramps']):
        sel = mat == m
        idx = np.clip(np.round(val[sel] * (len(rp) - 1) + (bay[sel] - 0.5) * 0.3), 0, len(rp) - 1).astype(int)
        rgb[at[sel]] = np.asarray(rp, np.float32)[idx]
    rgba = np.concatenate([rgb.reshape(h, w, 3), alpha.reshape(h, w, 1).astype(np.float32)], -1)
    return rgba, np.zeros((h, w), np.float32)


CHESS = {
    'white': dict(paint=_polished, ramps=[ramp('#e6ded2', dark=0.46, light=1.12, warm=0.06),
                                          ramp('#9a92a0', dark=0.5, light=1.2)],
                  key=(-0.4, 0.45, 0.8), shade=(0.4, 0.5), vein=0.9),
    'black': dict(paint=_polished, ramps=[ramp('#3a3442', dark=0.5, light=1.9, cool=0.2),
                                          ramp('#7a6a8a', dark=0.5, light=1.5)],
                  key=(-0.4, 0.45, 0.8), shade=(0.3, 0.6), vein=0.9),
}
_BASE = [(0.26, 0.0), (0.26, 0.05), (0.225, 0.07), (0.225, 0.1), (0.17, 0.13)]
# each piece's profile, turned: (radius, height) as shares of its height, foot to head
CHESS_PROFILES = {
    'pawn': _BASE + [(0.1, 0.22), (0.075, 0.47), (0.15, 0.51), (0.15, 0.535), (0.07, 0.56), (0.12, 0.6),
                     (0.155, 0.65), (0.17, 0.71), (0.162, 0.77), (0.14, 0.83), (0.1, 0.89), (0.05, 0.93), (0.0, 0.95)],
    'rook': _BASE + [(0.13, 0.25), (0.12, 0.62), (0.17, 0.69), (0.19, 0.73), (0.19, 0.9)],
    'bishop': _BASE + [(0.09, 0.3), (0.07, 0.5), (0.14, 0.54), (0.14, 0.565), (0.06, 0.59), (0.1, 0.63),
                       (0.135, 0.71), (0.12, 0.8), (0.08, 0.87), (0.035, 0.91), (0.05, 0.94), (0.045, 0.97), (0.0, 1.0)],
    'queen': _BASE + [(0.1, 0.3), (0.075, 0.6), (0.15, 0.645), (0.15, 0.67), (0.08, 0.695), (0.1, 0.75),
                      (0.165, 0.84), (0.165, 0.855)],
    'king': _BASE + [(0.1, 0.3), (0.08, 0.58), (0.16, 0.63), (0.16, 0.655), (0.09, 0.68), (0.11, 0.74),
                     (0.155, 0.82), (0.155, 0.84), (0.07, 0.86)],
    'knight': _BASE + [(0.15, 0.2), (0.14, 0.42)],
}
# the knight's head, side on, facing +x: (forward, height) as shares of its height
KNIGHT_HEAD = [(-0.13, 0.4), (-0.16, 0.6), (-0.12, 0.78), (-0.05, 0.9), (-0.01, 1.0), (0.03, 0.93), (0.1, 0.88),
               (0.19, 0.75), (0.24, 0.66), (0.21, 0.6), (0.1, 0.62), (0.04, 0.56), (0.11, 0.4)]


def _lathe(mat, seed, prof, H, n=16, phase=0.0):
    """A turned piece: every pair of points in its profile a frustum of n faces, smoothly shaded round."""
    parts = []
    smooth = -math.tan(math.pi / n)                                   # a convex `flute`: round, not faceted
    for k, ((r0, z0), (r1, z1)) in enumerate(zip(prof, prof[1:])):
        parts += _prism_faces(mat, seed, n, max(r0 * H, 1e-3 * H), max(r1 * H, 1e-3 * H), z0 * H, z1 * H, phase,
                              flute=smooth, block=True)
    r, z = prof[-1]
    if r > 0:                                                         # a flat head
        parts.append(_disc(mat, seed + 1, n, r * H, z * H, phase))
    return parts


def _slab(mat, seed, x0, x1, y0, y1, z0, z1):
    """A small block of the piece's stone, its five faces that show."""
    faces = (((x1, y1, z1), (x1, y0, z1), (x1, y1, z0)), ((x0, y0, z1), (x0, y1, z1), (x0, y0, z0)),
             ((x0, y1, z1), (x1, y1, z1), (x0, y1, z0)), ((x1, y0, z1), (x0, y0, z1), (x1, y0, z0)),
             ((x1, y0, z1), (x1, y1, z1), (x0, y0, z1)))
    return [_rock(mat, seed + k, *c) for k, c in enumerate(faces)]


def chess_piece(pl):
    """A chess piece in 3D, turned in polished marble - `piece` a `pawn`, `rook`, `bishop`, `knight`,
    `queen` or `king`, `side` `white` or `black`, `height` tall (default 1): a stepped foot, a stem, a
    collar; the pawn's ball, the rook's battlements, the bishop's mitre, the queen's coronet of points,
    the king's crown and cross; the knight's head carved side on and cut thick, facing the way it faces.
    Smoothly shaded round, a sheen where it faces the light, veins in the stone."""
    kind = pl.get('piece', 'pawn')
    mat = dict(CHESS[pl.get('side', 'white')])
    mat['key'] = _turned(mat['key'], pl)
    seed = int(pl.get('seed', 1))
    H = float(pl.get('height', 1.0))
    parts = _lathe(mat, seed, CHESS_PROFILES[kind], H)
    if kind == 'rook':                                                # battlements round its head
        for k in range(5):
            a0, a1 = 2 * math.pi * k / 5, 2 * math.pi * (k + 0.55) / 5
            for a in np.linspace(a0, a1, 3)[:-1]:
                b = a + (a1 - a0) / 2
                p0, p1 = np.array([math.cos(a), math.sin(a)]), np.array([math.cos(b), math.sin(b)])
                o0, o1, i0, i1 = p0 * 0.19 * H, p1 * 0.19 * H, p0 * 0.11 * H, p1 * 0.11 * H
                zt, zb = H, 0.9 * H
                parts += [_rock(mat, seed + 3, (*o0, zt), (*o1, zt), (*o0, zb)), _rock(mat, seed + 4, (*i1, zt), (*i0, zt), (*i1, zb)),
                          _rock(mat, seed + 5, (*i0, zt), (*i1, zt), (*o0, zt))]
            for a in (a0, a1):                                        # the merlon's ends
                p = np.array([math.cos(a), math.sin(a)])
                parts.append(_rock(mat, seed + 6, (*(p * 0.11 * H), H), (*(p * 0.19 * H), H), (*(p * 0.11 * H), 0.9 * H)))
    elif kind in ('queen', 'king'):                                   # a coronet of points round its head
        r, z0 = CHESS_PROFILES[kind][-1 if kind == 'queen' else -2]
        pts = 9 if kind == 'queen' else 6
        for k in range(pts):
            a, da = 2 * math.pi * k / pts, math.pi / pts
            A = np.array([r * math.cos(a - da) * H, r * math.sin(a - da) * H, z0 * H])
            B = np.array([r * math.cos(a + da) * H, r * math.sin(a + da) * H, z0 * H])
            C = np.array([(r + 0.015) * math.cos(a) * H, (r + 0.015) * math.sin(a) * H, (z0 + 0.075) * H])
            parts.append(_rock_tri(mat, seed + 7, A, B, C, np.array([math.cos(a), math.sin(a), 0.2])))
        if kind == 'queen':                                           # her ball
            parts += _lathe(mat, seed + 8, [(0.0, 0.87), (0.05, 0.9), (0.055, 0.94), (0.0, 0.98)], H, n=10)
        else:                                                         # his cross
            w, t = 0.02 * H, 0.025 * H
            parts += _slab(mat, seed + 9, -t, t, -w, w, 0.86 * H, H)
            parts += _slab(mat, seed + 10, -t, t, -0.065 * H, 0.065 * H, 0.92 * H, 0.955 * H)
    elif kind == 'knight':                                            # the head, cut thick from a slab
        t = 0.085 * H
        pts = [(x * H, z * H) for x, z in KNIGHT_HEAD]
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        z0, z1 = min(p[1] for p in pts), max(p[1] for p in pts)

        def mask(w, h, flip=False):
            poly = [((x - x0) / (x1 - x0) * w, (z1 - z) / (z1 - z0) * h) for x, z in pts]
            if flip:
                poly = [(w - px, py) for px, py in poly]
            return _grown(_poly(w, h, poly))
        parts.append(_rock(mat, seed + 11, (x0, t, z1), (x1, t, z1), (x0, t, z0), alpha=mask))     # read from +y
        parts.append(_rock(mat, seed + 12, (x1, -t, z1), (x0, -t, z1), (x1, -t, z0),                 # and from -y
                           alpha=lambda w, h: mask(w, h, True)))
        cx, cz = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        for k, (p, q) in enumerate(zip(pts, pts[1:] + pts[:1])):     # its edges, round the outline
            out = np.array([(p[0] + q[0]) / 2 - cx, 0.0, (p[1] + q[1]) / 2 - cz])
            A, B = np.array([p[0], -t, p[1]]), np.array([q[0], -t, q[1]])
            nrm = np.cross(B - A, np.array([0.0, 2 * t, 0.0]))
            if nrm @ out < 0:
                A, B = B, A
            parts.append(_rock(mat, seed + 13 + k, A, B, A + np.array([0.0, 2 * t, 0.0])))
        for side_ in (-1, 1):                                         # its eyes, a nick in each cheek
            parts.append(_rock(dict(mat, shade=(0.05, 0.1)), seed + 40, (0.085 * H, side_ * (t + 0.002), 0.79 * H),
                               (0.115 * H, side_ * (t + 0.002), 0.79 * H), (0.085 * H, side_ * (t + 0.002), 0.765 * H)))
    parts = [p for p in parts if p]
    parts.append(shadow(0.0, 0.0, 0.7 * H, 0.45))
    return parts


# ------------------------------------------------------------------ crystals

CRYSTAL_HUES = {'cyan': '#5adcf2', 'violet': '#a47af6', 'rose': '#f27cba', 'green': '#62eaa4', 'amber': '#f2b24e',
                'ice': '#bfe4ff', 'white': '#eef2ff'}
CRYSTAL_KEY = np.array([0.35, 0.3, 0.88]) / np.linalg.norm([0.35, 0.3, 0.88])


def _facet(w, h, hue, lit, clear, seed, tip=False):
    """The texture of one facet of a crystal, w x h texels (rows from its tip end toward its base):
    its colour from the crystal's ramp, brighter the more the facet is turned to the light, toward
    the tip and along its edges; its alpha - how much of the facet itself shows over what is seen
    through it - `clear` across the middle, clouding toward the base as real crystals do, solid
    at the edges, with a few streaks of inclusion down it; and a glow."""
    rng = np.random.default_rng(seed)
    shape = _grown(_poly(w, h, [(0, 0), (w, 0), (0, h)])) if tip else np.ones((h, w), bool)
    p = np.pad(shape, 1)                                         # nothing past the texture's border
    edge = shape & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    yy, xx = np.mgrid[0:h, 0:w]
    along = (yy + 0.5) / h                                       # 0 at the tip end, 1 at the base
    streaks = np.zeros((h, w), bool)
    for _ in range(rng.integers(0, 3)):                          # inclusions, along the crystal
        c = rng.integers(0, w)
        streaks |= (xx == c) & (along > rng.uniform(0.1, 0.5)) & (along < rng.uniform(0.6, 1.0))
    v = 0.3 + 0.5 * lit + 0.18 * (1 - along) * (not tip) + 0.25 * tip + 0.35 * edge + 0.12 * streaks
    a = clear + (0.5 - clear) * np.clip((along - 0.65) / 0.35, 0, 1) ** 1.5 * (not tip) + 0.6 * edge + 0.15 * streaks
    pal = ramp(hue, n=7, dark=0.35, light=1.6, cool=0.12, warm=0.06)
    idx = np.clip(np.round(np.clip(v, 0, 1) * (len(pal) - 1) + (BAYER4[yy % 4, xx % 4] - 0.5) * 0.5), 0, len(pal) - 1)
    rgba = np.concatenate([pal[idx.astype(int)], (np.clip(a, 0.06, 0.95) * shape)[..., None]], -1).astype(np.float32)
    return rgba, (np.clip(v, 0, 1) * shape).astype(np.float32)


def _prism(hue, base, axis, length, r, spin, seed, refract, glow, key=CRYSTAL_KEY):
    """One crystal: a hexagonal prism `length` long from `base` along `axis`, `r` across its corners,
    ending in a six-sided point - every face a panel of its own, each with its own clarity and its
    own bend of the light through it."""
    rng = np.random.default_rng(seed)
    axis = axis / np.linalg.norm(axis)
    e1 = np.cross(axis, [0.0, 0.0, 1.0] if abs(axis[2]) < 0.9 else [1.0, 0.0, 0.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    ring = [r * (math.cos(spin + k * math.pi / 3) * e1 + math.sin(spin + k * math.pi / 3) * e2) for k in range(6)]
    tip = r * rng.uniform(1.3, 1.9)
    foot, shoulder, apex = base, base + axis * (length - tip), base + axis * length
    filt = 0.4 + 0.6 * rgb(hue) / rgb(hue).max()                 # the light through it takes its colour
    parts = []
    for k in range(6):
        p, q = ring[k], ring[(k + 1) % 6]
        out = (p + q) / 2
        for tri, corners in ((False, (shoulder + p, shoulder + q, foot + p)), (True, (shoulder + p, shoulder + q, apex))):
            A, B, C = (np.asarray(c, float) for c in corners)
            facing = out + (axis * r if tri else 0)
            if np.cross(B - A, C - A) @ facing < 0:              # read from outside
                A, B, C = B, A, (C if tri else foot + q)
            u, v = B - A, C - A
            w, h = _texels(np.linalg.norm(u)), _texels(np.linalg.norm(v))
            nrm = np.cross(u, v)
            lit = max(0.0, float(nrm @ key) / max(np.linalg.norm(nrm), 1e-9))
            rgba, v_ = _facet(w, h, hue, lit, rng.uniform(0.05, 0.3), int(rng.integers(1 << 30)), tri)
            parts.append(quad((rgba, glow * (0.35 + 0.65 * v_)), tuple(A), tuple(B), tuple(C), back=0.8,
                              refract=refract * rng.uniform(0.6, 1.5), filter=[float(c) for c in filt],
                              disperse=0.25))
    return parts


def crystal_cluster(pl):
    """A cluster of crystals growing from a bed of rock: `count` hexagonal prisms with pointed tips,
    the tallest `size` high and near upright, the rest smaller and leaning out, `spread` across.
    Each facet is a panel that bends the light through it its own way - a facet shows a shifted
    piece of what lies behind, its neighbours other pieces, the colours parting a little at their
    edges - tinted, milky toward the base, bright along the edges and glowing. `color` is a name
    (cyan, violet, rose, green, amber, ice, white) or `#rrggbb`; `refract` how far the light bends
    (units, default 0.16); `glow` how much the crystals glow; `lights` false leaves out the light
    they give; `rock` the bed's kind of rock, `base` false leaves it out."""
    rng = np.random.default_rng(int(pl.get('seed', 1)))
    size = float(pl.get('size', 0.9))
    n = int(pl.get('count', 5))
    spread = float(pl.get('spread', 0.3 * size))
    hue = CRYSTAL_HUES.get(pl.get('color', 'cyan'), pl.get('color', 'cyan'))
    refract, glow = float(pl.get('refract', 0.16)), float(pl.get('glow', 0.6))
    parts = []
    for k in range(n):
        length = size * (1.0 if k == 0 else rng.uniform(0.35, 0.8))
        if k == 0:
            at, lean = np.zeros(2), rng.uniform(0, 8)
        else:
            a = rng.uniform(0, 2 * math.pi)
            at, lean = spread * rng.uniform(0.4, 1.0) * np.array([math.cos(a), math.sin(a)]), rng.uniform(14, 38)
        out = math.atan2(at[1], at[0]) + rng.uniform(-0.4, 0.4) if k else rng.uniform(0, 2 * math.pi)
        tilt = math.radians(lean)
        axis = np.array([math.sin(tilt) * math.cos(out), math.sin(tilt) * math.sin(out), math.cos(tilt)])
        base = np.array([at[0], at[1], -0.06 * size])           # set in the rock
        parts += _prism(hue, base, axis, length, length * rng.uniform(0.1, 0.15), rng.uniform(0, math.pi),
                        int(rng.integers(1 << 30)), refract, glow, np.array(_turned(CRYSTAL_KEY, pl)))
    if pl.get('base', True):
        parts += boulder({'size': 2.6 * spread + 0.25 * size, 'height': 0.14 * size, 'rock': pl.get('rock', 'cave'),
                          'angle': pl.get('angle', 0.0),
                          'seed': int(pl.get('seed', 1)) + 500})
    if pl.get('lights', True):
        parts.append(light(0.0, 0.0, 0.5 * size, 2.0 + 3.0 * size, [float(c) for c in rgb(hue) / rgb(hue).max()], 1.8))
    return parts


OBJECTS = {'noodle_stand': noodle_stand, 'car': car, 'rock_wall': rock_wall, 'boulder': boulder, 'column': column,
           'beam': beam, 'crystal_cluster': crystal_cluster, 'trough': trough, 'shed_roof': shed_roof,
           'gable_roof': gable_roof, 'market_stand': market_stand, 'saloon_bar': saloon_bar, 'rails': rails,
           'ore_cart': ore_cart, 'keel': keel, 'chess_piece': chess_piece, 'ship_hull': ship_hull,
           'longship': longship, 'lighthouse': lighthouse, 'stone_lantern': stone_lantern,
           'standing_stone': standing_stone, 'gear': gear, 'heap': heap}

"""Objects: things bigger than a prop, built in 3D out of flat panels - a food stand, a car.

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
"""
import functools
import math

import numpy as np

from pixelart import Canvas, ramp

TEXELS = 64                 # texels per world unit, as on the walls
PLACEMENT_KEYS = {'type', 'x', 'y', 'z', 'angle', 'scale', 'paint', 'lights', 'title', 'notes'}


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
    for pl in scene['objects']:
        if pl['type'] not in OBJECTS:
            raise KeyError(f"unknown object {pl['type']!r} - the built-ins are {', '.join(sorted(OBJECTS))}")
        X, Y, Z = float(pl['x']), float(pl['y']), float(pl.get('z', 0.0))
        a = math.radians(float(pl.get('angle', 0.0)))
        k = float(pl.get('scale', 1.0))
        ca, sa = math.cos(a), math.sin(a)

        def world(p):
            x, y, z = p
            return np.array([X + (x * ca - y * sa) * k, Y + (x * sa + y * ca) * k, Z + z * k])

        for part in OBJECTS[pl['type']](pl):
            kind = part['part']
            if kind == 'panel':
                tl, tr, bl = world(part['tl']), world(part['tr']), world(part['bl'])
                pn = {key: val for key, val in part.items() if key not in ('part', 'tex', 'tl', 'tr', 'bl')}
                pn.update(o=tl, u=tr - tl, v=bl - tl, rgba=part['tex'][0], em=part['tex'][1], at=(X, Y, Z))
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


OBJECTS = {'noodle_stand': noodle_stand, 'car': car}

"""Road scenes: the road of an arcade racer - a scene with a `road` instead of a `map`.

A road is a long run of short segments, each bending a little and rising or falling a little from the last (its
`sections`). Every segment ahead of the camera is projected onto the screen and the rows between its near and far
edges are filled, from the camera outward: a segment is drawn only above the ones nearer it, so a crest hides the
road beyond until it comes back into view lower down. The road's surface, its lines and rumble strips and the
ground either side are textures, lit by the scene's ambient, its sun or moon and the lamps along it; every few
segments the ground and the road shift a shade, the bands that read as speed. Props stand along it - `roadside`
rows, or `sprites` placed by `at` (how far along) and `x` (how far across) - scaled by distance and clipped by the
crests in front of them, and a shot's `vehicle` rides ahead of its camera. Overhead, the scene's sky.

The frame comes out as the raycaster's does - colour, depth and light - so the post effects, the weather, the GUI
and the palette finish it the same way (render.finish_world).
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import assets
import prefabs
import world as WD

# the keys a road and a roadside row take (render.lint_scene checks them; a road camera's are in render.SHOT_KEYS)
ROAD_KEYS = {'sections', 'width', 'surface', 'lanes', 'lines', 'edges', 'centre', 'rumble', 'shoulder', 'ground',
             'stripe', 'bands', 'segment', 'distance', 'edge', 'roofs', 'walls', 'ceiling', 'below', 'wet',
             'ripple'}
WALL_KEYS = {'side', 'offset', 'height', 'texture', 'from', 'to', 'z', 'tile', 'light', 'ragged', 'seed', 'blocks',
             'gaps'}
CEILING_KEYS = {'from', 'to', 'height', 'texture', 'tile', 'light'}
BELOW_KEYS = {'depth', 'texture', 'tile', 'haze'}
ROADSIDE_KEYS = {'type', 'every', 'density', 'side', 'offset', 'scale', 'jitter', 'from', 'to', 'flip', 'z', 'tint',
                 'light', 'seed', 'variant', 'view', 'opacity', 'blend', 'fullbright', 'shadow', 'clear'}
SCATTER_KEYS = {'of', 'density', 'side', 'offset', 'from', 'to', 'sizes', 'clump', 'scale', 'seed', 'clear', 'tint'}
DECAL_KEYS = {'tex', 'at', 'x', 'size', 'angle', 'opacity', 'tint', 'flip', 'density', 'every', 'side', 'offset',
              'from', 'to', 'seed', 'clump', 'reflect'}
# named sets of marks for a row of `decals`, as `scatter` has its sets of props (repeats are weights)
DECAL_SETS = {
    'wear': ['crack', 'crack', 'road_patch', 'oil_stain', 'stain'],             # an old road
    'ruin': ['pothole', 'pothole', 'crack', 'crack', 'puddle', 'road_patch'],    # a road gone to ruin
    'city': ['oil_stain', 'oil_stain', 'manhole', 'crack', 'stain', 'road_patch'],
    'trail': ['pebbles', 'pebbles', 'stain', 'leaf_litter'],                    # a dirt path
    'fall': ['leaf_litter', 'leaf_litter', 'leaf_litter', 'pebbles'],
    'drifts': ['sand_drift', 'sand_drift', 'pebbles', 'crack'],                 # a desert road
}
# marks that lie along the road (a row of them is not turned at random)
ALONG = {'tyre_marks', 'lane_arrow', 'zebra_crossing', 'road_patch', 'rover_tracks', 'hazard_stripe', 'manhole'}
NEAR = 0.15                         # nothing nearer the camera than this is drawn
ADDITIVE = ('additive', 'add')     # a sprite's `blend` that adds its light (the docs name the first)
TEX = 64                            # texels to a unit, as on the raycaster's walls and floors


def _col(c, default=(1.0, 1.0, 1.0)):
    if c is None:
        return np.array(default, np.float32)
    if isinstance(c, str):
        c = c.lstrip('#')
        return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
    return np.array(c[:3], np.float32)


def _hash01(a, b, seed=0):
    """A stable pseudo-random 0-1 per integer pair (arrays), for ragged edges and stray tufts."""
    h = (a.astype(np.int64) * 73856093) ^ (b.astype(np.int64) * 19349663) ^ (seed * 83492791)
    return ((h * 2654435761) % 4294967296).astype(np.float64) / 4294967296.0


class Road:
    """The road as segments: per segment its curve (how much it bends) and its height at each end.

    `sections` are [length, curve, rise] or {"length", "curve", "rise"}: `length` in units, `curve` how hard it
    bends (-1 to 1 is gentle to sharp, negative to the left), eased in over its first quarter and out over its
    last, and `rise` how far it climbs (or falls, negative) over the whole section, eased at both ends."""

    def __init__(self, spec):
        self.seg = float(spec.get('segment', 1.0))
        curve, ys = [], [0.0]
        for s in spec.get('sections') or [[400, 0, 0]]:
            n, c, rise = (s + [0, 0])[:3] if isinstance(s, list) else (s.get('length', 50), s.get('curve', 0),
                                                                        s.get('rise', 0))
            n = max(1, int(round(float(n) / self.seg)))
            y0 = ys[-1]
            for k in range(n):
                t = (k + 0.5) / n
                ease = min(1.0, t / 0.25, (1 - t) / 0.25)
                curve.append(float(c) * 0.035 * self.seg * (0.5 - 0.5 * math.cos(math.pi * ease)))
                ys.append(y0 + float(rise) * (0.5 - 0.5 * math.cos(math.pi * (k + 1) / n)))
        self.curve = np.array(curve, np.float64)
        self.y = np.array(ys, np.float64)
        self.n = len(curve)
        self.length = self.n * self.seg

    def height(self, at):
        """The road's height at `at` units along it."""
        f = np.clip(np.asarray(at, np.float64) / self.seg, 0, self.n - 1e-6)
        i = f.astype(int)
        return self.y[i] + (self.y[i + 1] - self.y[i]) * (f - i)


class OpenWorld:
    """Stands in for a grid World where the GUI and the weather want one: open ground, no walls and no roofs."""
    mw = mh = 1
    ceil_h = 1e9
    solid_h = np.zeros((1, 1), np.float32)
    ceil_tid = np.full((1, 1), -1, np.int32)
    void = np.zeros((1, 1), bool)


def _side_spec(g):
    """A side's ground as bands out from the road's edge: [(outer edge or inf, texture spec, tint)], or None for
    void - no ground at all, the sky carrying on below."""
    if g == 'void':
        return None
    if isinstance(g, str) or (isinstance(g, dict) and 'base' in g):
        g = [{'texture': g}]
    elif isinstance(g, dict):
        g = [g]
    out, edge = [], 0.0
    for b in g:
        edge = edge + float(b['width']) if 'width' in b else math.inf
        tex = b.get('texture', 'grass')
        name = tex.get('base') if isinstance(tex, dict) else tex
        own = assets.TEXTURE_REFLECT.get(name, 0.0)             # water mirrors by its nature, under a roof too
        out.append((edge, tex, _col(b.get('tint')), float(b.get('reflect', own)), own, float(b.get('tile', 1.0))))
        if math.isinf(edge):
            break
    if not math.isinf(out[-1][0]):
        out.append((math.inf,) + out[-1][1:])
    return out


class RoadRenderer:
    """The road scene's renderer: `render(cam)` gives a finished frame, as render.Renderer does."""

    def __init__(self, scene):
        scene = prefabs.expand(scene)               # its `time` of day: the sky, the sun or moon, the air
        self.s = scene
        spec = scene['road']
        self.road = Road(spec)
        self.w = OpenWorld()
        self.anchors = {}
        self.palette_ref = None
        self.last_effects = []
        self.last_report = []
        self.defs = scene.get('sprite_defs', {})
        self.half = float(spec.get('width', 4.0)) / 2
        rum = spec.get('rumble', {'width': 0.3})
        self.rumble = None if rum is False else {
            'width': float(rum.get('width', 0.3)),
            'colors': [_col(c) for c in rum.get('colors', ['#ececec', '#c83024'])]}
        sh = spec.get('shoulder', False)
        self.shoulder = None if not sh else {'width': float(sh.get('width', 0.5)),
                                             'tex': assets.get_texture(sh.get('texture', 'gravel'))[0]}
        self.lanes = int(spec.get('lanes', 2))
        self.lines = None if spec.get('lines', '#eeeeee') is False else _col(spec.get('lines', '#eeeeee'))
        self.edges = None if not spec.get('edges') else _col(spec['edges'])
        self.centre = None if not spec.get('centre') else _col(spec['centre'])
        self.stripe = max(1, int(spec.get('stripe', 3)))
        self.bands = float(spec.get('bands', 0.08))
        self.draw = max(10, int(float(spec.get('distance', 260)) / self.road.seg))
        e = spec.get('edge') or {}
        self.ragged = float(e.get('ragged', 0.0))        # how far the edge wanders, in units
        self.blend = float(e.get('blend', 0.0))          # how wide a band the road and the ground mix in
        self.surface, self.surface_em = assets.get_texture(spec.get('surface', 'asphalt'))[:2]   # a lane of light glows
        surf = spec.get('surface', 'asphalt')
        surf = surf.get('base') if isinstance(surf, dict) else surf
        self.surface_alpha = assets.get_alpha(surf)            # a see-through road: a coaster's rails and ties
        # how mirror-like the road is: water mirrors by its own nature, a road by how `wet` it is
        self.wet = float(spec.get('wet', assets.TEXTURE_REFLECT.get(surf, 0.0)))
        self.dry = assets.TEXTURE_REFLECT.get(surf, 0.0)        # under a roof the rain does not reach
        self.ripple = float(spec.get('ripple', 1.0))
        g = spec.get('ground', 'grass')
        sides = g if isinstance(g, dict) and ('left' in g or 'right' in g) else {'left': g, 'right': g}
        self.sides = {k: _side_spec(sides.get(k, 'grass')) for k in ('left', 'right')}
        for bands in self.sides.values():
            for b in bands or []:
                if b[1] != 'void':
                    assets.get_texture(b[1])
        self.ambient = _col(scene.get('ambient'), (0.55, 0.55, 0.6))
        self.suns = [L for L in scene.get('lights', []) if L.get('type') in ('sun', 'moon')]
        fog = scene.get('fog') or {}
        self.fog_c = _col(fog.get('color'), (0.6, 0.65, 0.75)) if fog else None
        self.fog_d = float(fog.get('density', 0.0)) if fog else 0.0
        self.roofs = [(float(r[0]), float(r[1]), float(r[2]) if len(r) > 2 else 0.2)
                      for r in spec.get('roofs', [])]
        self.walls = []
        for n, wl in enumerate(spec.get('walls') or []):
            tex = wl.get('texture', 'concrete')
            texs = tex if isinstance(tex, list) else [tex]          # a street: each building its own facade
            tex = texs[0]
            tile = wl.get('tile', 1.0)
            self.walls.append({'sides': {'both': (-1, 1), 'left': (-1,), 'right': (1,)}[wl.get('side', 'both')],
                               'offset': float(wl.get('offset', 0.5)), 'height': float(wl.get('height', 1.0)),
                               'z': float(wl.get('z', 0.0)),
                               'tile': (float(tile[0]), float(tile[1])) if isinstance(tile, list) else
                                       (float(tile), float(tile)),
                               'ragged': float(wl.get('ragged', 0.0)), 'seed': int(wl.get('seed', n)),
                               'blocks': float(wl.get('blocks', 0.0)), 'gaps': float(wl.get('gaps', 0.0)),
                               'texs': [(assets.get_texture(t), assets.get_alpha(t.get('base') if isinstance(t, dict)
                                                                                 else t)) for t in texs],
                               'from': float(wl.get('from', 0.0)), 'to': float(wl.get('to', 1e9)),
                               'tex': assets.get_texture(tex), 'alpha': assets.get_alpha(tex.get('base') if
                                                                                         isinstance(tex, dict) else tex),
                               'light': float(wl.get('light', 1.0))})
        ceil = spec.get('ceiling') or []
        self.ceilings = []
        for c in [ceil] if isinstance(ceil, dict) else ceil:
            self.ceilings.append({'from': float(c.get('from', 0.0)), 'to': float(c.get('to', 1e9)),
                                  'height': float(c.get('height', 2.5)), 'tile': float(c.get('tile', 1.0)),
                                  'tex': assets.get_texture(c.get('texture', 'concrete'))})
            self.roofs.append((self.ceilings[-1]['from'], self.ceilings[-1]['to'], float(c.get('light', 0.2))))
        b = spec.get('below')
        self.below = None if not b else {'depth': float(b.get('depth', 30.0)), 'tile': float(b.get('tile', 1.0)),
                                         'bands': _side_spec(b.get('texture', 'grass')),
                                         'haze': float(b.get('haze', 1.0))}
        cs = scene.get('contact_shadows', 0.55)
        self.shadow = 0.0 if cs is False else 0.55 if cs is True else float(cs)
        self._skies = {}
        self.items = self._place(scene)
        self.lamps = self._lamps(scene)
        self.decals = self._decals(scene)

    # ------------------------------------------------------------------ what stands along the road

    def _place(self, scene):
        """Every prop along the road as {type, at, x, z, scale, ...}: the `roadside` rows laid out (the same every
        render) and the scene's own `sprites`."""
        out = []
        L = self.road.length
        # a scattered row leaves the few units in front of every shot's camera clear (`clear`, default 3): a tree
        # right at the lens is a smear of magnified pixels, not a tree
        cams = [float(c.get('at', 0.0)) for c in [scene.get('camera') or {}] + list(scene.get('shots') or [])]
        for k, row in enumerate(scene.get('roadside', [])):
            rng = np.random.default_rng(int(row.get('seed', k)))
            types = row['type'] if isinstance(row['type'], list) else [row['type']]
            sides = {'both': (-1, 1), 'left': (-1,), 'right': (1,), 'middle': (0,)}[row.get('side', 'both')]
            a0, a1 = float(row.get('from', 1.0)), min(L, float(row.get('to', L)))
            off = row.get('offset', 1.0)
            o0, o1 = (off, off) if not isinstance(off, list) else off
            sc = row.get('scale')
            jit = float(row.get('jitter', 0.0))
            for side in sides:
                if 'density' in row:            # scattered: so many to a unit of road, anywhere in the band
                    n = int(rng.poisson(float(row['density']) * (a1 - a0)))
                    ats = np.sort(rng.uniform(a0, a1, n))
                    clear = float(row.get('clear', 3.0))
                    ats = np.array([a for a in ats if not any(c - 0.5 <= a <= c + clear for c in cams)])
                else:
                    ats = np.arange(a0, a1, float(row.get('every', 5.0)))
                for at in ats:
                    t = types[int(rng.integers(len(types)))]
                    edge = self.half + (self.rumble['width'] if self.rumble else 0.0)
                    if side == 0:                   # down the middle: `offset` is from the road's centre line
                        x = float(rng.uniform(o0, o1))
                    else:                           # (`jitter` moves it along the road; `offset` sets how far out)
                        x = side * (edge + float(rng.uniform(o0, o1)))
                    it = {k2: v for k2, v in row.items() if k2 not in ('type', 'every', 'density', 'side', 'offset',
                                                                       'jitter', 'from', 'to', 'scale', 'seed')}
                    it.update(type=t, at=float(at + rng.uniform(-jit, jit)), x=x)
                    if isinstance(sc, list):
                        it['scale'] = float(rng.uniform(sc[0], sc[1]))
                    elif sc is not None:
                        it['scale'] = float(sc)
                    if isinstance(row.get('z'), list):     # floating at heights between the two
                        it['z'] = float(rng.uniform(row['z'][0], row['z'][1]))
                    if row.get('flip') and side > 0:
                        it['flip'] = True
                    elif 'flip' in it:
                        it.pop('flip')
                    out.append(it)
        out += self._scatter(scene, cams)
        for sp in scene.get('sprites', []):
            out.append(dict(sp, at=float(sp.get('at', 0.0)), x=float(sp.get('x', 0.0))))
        for it in out:
            it['type'] = assets.variant_name({**it, 'x': it['at'], 'y': it['x']}, scene)
            d = assets.sprite_defaults(it['type'], self.defs)
            for k2, v in d.items():
                it.setdefault(k2, v)
        return out

    def _band(self, spec, sgn, default):
        """A row's band across the road: (from, to) in x - out from the edge for a side, from the centre line for
        the road itself (sgn 0)."""
        off = spec.get('offset', default)
        o0, o1 = (float(off), float(off)) if not isinstance(off, list) else (float(off[0]), float(off[1]))
        return min(o0, o1), max(o0, o1)

    def _spread(self, rng, n, a0, a1, o0, o1, sgn, edge, clump):
        """`n` spots in a band - along from a0 to a1, out (or across) from o0 to o1 - drawn from a pool weighted
        by the scatter noise field, so they gather in drifts and leave clearings (`clump` 0 for none). Returns
        their (at, x), x from the centre line."""
        pool = max(4 * n, 32)
        ca, co = rng.uniform(a0, a1, pool), rng.uniform(o0, o1, pool)
        xs = co if sgn == 0 else sgn * (edge + co)
        if clump > 0:
            w = WD.sample_noise(WD.noise_field(), ca / WD.SCATTER_PERIOD, xs / WD.SCATTER_PERIOD).astype(np.float64)
            w = np.clip(w, 0.02, 1.0) ** clump
        else:
            w = np.ones(pool)
        picks = np.sort(rng.choice(pool, size=min(n, pool), replace=False, p=w / w.sum()))
        return ca[picks], xs[picks]

    def _scatter(self, scene, cams):
        """`scatter` along the road, as on a map: what - a named set, a prop or a list (`of`) - so many to a square
        unit (`density`) in a band beside the road or on it (`side`, `offset`, `from`, `to`), in size classes
        (`sizes`), weighted by a noise field so they gather in drifts and leave clearings (`clump`). The same every
        render; the few units in front of each camera are left `clear` (default 1.5)."""
        out = []
        L = self.road.length
        edge = self.half + (self.rumble['width'] if self.rumble else 0.0)
        for n, spec in enumerate(scene.get('scatter') or []):
            rng = np.random.default_rng(int(scene.get('seed', 0)) * 7919 + int(spec.get('seed', n)) * 104729 + 29)
            items = assets.debris_items(spec.get('of', 'verge'))
            for name in sorted(set(items)):
                try:
                    assets.get_sprite(name, self.defs)
                except KeyError:
                    raise KeyError(f"scatter 'of' names {name!r}, which is neither a scatter set "
                                   f"({', '.join(sorted(assets.DEBRIS_SETS))}) nor a prop") from None
            sizes = spec.get('sizes') or assets.SIZE_WEIGHTS
            names = list(sizes)
            bad = [c for c in names if c not in assets.SIZE_CLASSES]
            if bad:
                raise KeyError(f"scatter 'sizes' has unknown class(es) {bad}; classes are "
                               f"{', '.join(assets.SIZE_CLASSES)}")
            wts = np.array([float(sizes[c]) for c in names] if isinstance(sizes, dict) else [1.0] * len(names))
            wts = wts / wts.sum()
            a0, a1 = float(spec.get('from', 1.0)), min(L, float(spec.get('to', L)))
            sides = {'both': (-1, 1), 'left': (-1,), 'right': (1,), 'road': (0,)}[spec.get('side', 'both')]
            clear = float(spec.get('clear', 1.5))
            for sgn in sides:
                o0, o1 = self._band(spec, sgn, [-self.half, self.half] if sgn == 0 else [0.0, 2.5])
                count = int(round(float(spec.get('density', 0.4)) * max(0.0, a1 - a0) * max(o1 - o0, 0.2)))
                if count <= 0:
                    continue
                for at, x in zip(*self._spread(rng, count, a0, a1, o0, o1, sgn, edge, float(spec.get('clump', 1.4)))):
                    name = items[int(rng.integers(len(items)))]
                    cls = names[int(rng.choice(len(names), p=wts))]
                    flip = bool(rng.random() < 0.5)
                    if any(c - 0.5 <= at <= c + clear for c in cams):
                        continue
                    it = {'type': name, 'at': float(at), 'x': float(x),
                          'scale': assets.size_scale(name, cls, self.defs) * float(spec.get('scale', 1.0))}
                    if flip:
                        it['flip'] = True
                    if spec.get('tint') is not None:
                        it['tint'] = spec['tint']
                    out.append(it)
        return out

    def _decals(self, scene):
        """The marks lying on the road and the ground (`decals`): placed ones by `at` and `x`, and rows of them -
        `density` so many to a square unit, or one `every` so many units - on the road (`side` 'road', the
        default) or the ground beside it, weighted by the scatter's noise so they gather. `tex` a decal, a set
        (DECAL_SETS) or a list; `size` its width across (or [min, max]), its length along the image's; `angle` in
        degrees (a row's are turned at random, but marks that lie along the road stay with it); `opacity`, `tint`,
        `flip`."""
        out = []
        L = self.road.length
        edge = self.half + (self.rumble['width'] if self.rumble else 0.0)
        ddefs = scene.get('decal_defs')

        def one(tex, at, x, size, angle, spec, flip):
            rgba, _ = assets.get_decal(tex, ddefs)
            th = math.radians(angle)
            out.append({'tex': tex, 'at': float(at), 'x': float(x), 'w': size, 'h': size * rgba.shape[0] / rgba.shape[1],
                        'c': math.cos(th), 's': math.sin(th), 'opacity': float(spec.get('opacity', 1.0)),
                        'tint': _col(spec.get('tint')), 'flip': flip,
                        'reflect': float(spec.get('reflect', assets.DECAL_REFLECT.get(tex, 0.0)))})

        for n, spec in enumerate(scene.get('decals') or []):
            texs = spec.get('tex', 'crack')
            texs = [t2 for t in ([texs] if isinstance(texs, str) else texs) for t2 in DECAL_SETS.get(t, [t])]
            for t in set(texs):
                assets.get_decal(t, ddefs)
            sz = spec.get('size', 1.0)
            if 'density' not in spec and 'every' not in spec:          # one, placed
                one(texs[0], spec.get('at', 0.0), spec.get('x', 0.0), float(sz if not isinstance(sz, list) else sz[0]),
                    float(spec.get('angle', 0.0)), spec, bool(spec.get('flip', False)))
                continue
            rng = np.random.default_rng(int(scene.get('seed', 0)) * 7919 + int(spec.get('seed', n)) * 104729 + 61)
            a0, a1 = float(spec.get('from', 0.0)), min(L, float(spec.get('to', L)))
            sides = {'both': (-1, 1), 'left': (-1,), 'right': (1,), 'road': (0,)}[spec.get('side', 'road')]
            for sgn in sides:
                o0, o1 = self._band(spec, sgn, [-self.half, self.half] if sgn == 0 else [0.0, 2.0])
                if 'every' in spec:
                    ats = np.arange(a0, a1, float(spec['every']))
                    xs = rng.uniform(o0, o1, len(ats))
                    xs = xs if sgn == 0 else sgn * (edge + xs)
                else:
                    count = int(round(float(spec['density']) * max(0.0, a1 - a0) * max(o1 - o0, 0.2)))
                    if count <= 0:
                        continue
                    ats, xs = self._spread(rng, count, a0, a1, o0, o1, sgn, edge, float(spec.get('clump', 1.0)))
                for at, x in zip(ats, xs):
                    t = texs[int(rng.integers(len(texs)))]
                    size = float(rng.uniform(sz[0], sz[1])) if isinstance(sz, list) else float(sz)
                    spin = float(rng.uniform(0, 360))
                    flip = bool(rng.random() < 0.5)
                    angle = float(spec['angle']) if 'angle' in spec else (spin if t not in ALONG else 0.0)
                    one(t, at, x, size, angle, spec, flip if t not in ALONG else bool(spec.get('flip', False)))
        out.sort(key=lambda d: d['at'])
        return out

    def _lamps(self, scene):
        """The point lights along the road: the scene's own (placed by `at` and `x`) and one for every prop that
        carries a `light` (a roadside row's, or the prop's own)."""
        out = []
        for L in scene.get('lights', []):
            if L.get('type') in ('sun', 'moon'):
                continue
            out.append({'at': float(L.get('at', 0.0)), 'x': float(L.get('x', 0.0)), 'z': float(L.get('z', 1.0)),
                        'r': float(L.get('radius', 3.0)), 'c': _col(L.get('color'), (1, 0.85, 0.6)) *
                        float(L.get('intensity', 1.0))})
        for it in self.items:
            L = it.get('light')
            if isinstance(L, dict):
                out.append({'at': it['at'] + float(L.get('at', 0.0)), 'x': it['x'] + float(L.get('x', 0.0)) * (
                            -1 if it['x'] > 0 else 1), 'z': float(L.get('z', 1.0)), 'r': float(L.get('radius', 3.0)),
                            'c': _col(L.get('color'), (1, 0.85, 0.6)) * float(L.get('intensity', 1.0))})
        return out

    def _headlights(self, cam, at, camx):
        """A shot's vehicle with `headlights` (a colour, or true for white): two pools of light on the road ahead
        of it; and the `light` it carries (a lantern at a boat's bow), placed from the vehicle."""
        v = cam.get('vehicle') or {}
        hl = v.get('headlights')
        ahead = at + float(v.get('ahead', 2.4))
        vx = camx + float(v.get('x', 0.0))
        out = []
        if hl:
            c = _col(None if hl is True else hl, (1.0, 0.95, 0.82)) * float(v.get('beam', 1.0))
            out += [{'at': ahead + 3.0, 'x': vx + side * 0.5, 'z': 0.35, 'r': 4.5, 'c': c} for side in (-1, 1)]
        L = v.get('light')
        if isinstance(L, dict):
            out.append({'at': ahead + float(L.get('at', 0.0)), 'x': vx + float(L.get('x', 0.0)),
                        'z': float(L.get('z', 0.5)), 'r': float(L.get('radius', 3.0)),
                        'c': _col(L.get('color'), (1, 0.85, 0.6)) * float(L.get('intensity', 1.0))})
        return out

    def _vehicle_marks(self, cam, at, camx):
        """A shot's vehicle's `wake` (true, or {"size", "opacity"}): foam spread on the water behind it."""
        v = cam.get('vehicle') or {}
        wk = v.get('wake')
        if not wk:
            return []
        wk = wk if isinstance(wk, dict) else {}
        size = float(wk.get('size', 1.2))
        rgba, _ = assets.get_decal('wake')
        length = size * rgba.shape[0] / rgba.shape[1]
        return [{'tex': 'wake', 'at': at + float(v.get('ahead', 2.4)) - length / 2 + 0.05,
                 'x': camx + float(v.get('x', 0.0)), 'w': size, 'h': length, 'c': 1.0, 's': 0.0,
                 'opacity': float(wk.get('opacity', 0.9)), 'tint': _col(None), 'flip': False, 'reflect': 0.0}]

    # ------------------------------------------------------------------ the frame

    def render(self, cam):
        """Render one camera: the road at `supersample` times the size, brought down, then finished by the post
        effects and the GUI (render.finish_world)."""
        import render as R
        self.anchors = {}                         # this shot's, as the raycaster's are: none left from the last
        ss = int(cam.get('supersample', self.s.get('supersample', 1)))
        res = self.s.get('resolution', [320, 200])
        bw, bh = int(res[0]), int(res[1])
        W, H = bw * ss, bh * ss
        roll = math.radians(float(cam.get('roll', 0.0)))
        if roll:                       # a bigger frame, turned and cut down, so the corners never show its edge
            c, sn = abs(math.cos(roll)), abs(math.sin(roll))
            px, py = int(math.ceil((W * c + H * sn - W) / 2)) + 2, int(math.ceil((W * sn + H * c - H) / 2)) + 2
            self._pad, self._hold_vehicle = (px, py, W, H), True
            img, emis, depth = self._frame(cam, W + 2 * px, H + 2 * py)
            img, emis, depth = (self._turn(a, math.degrees(roll), px, py, W, H, k) for a, k in
                                ((img, Image.BILINEAR), (emis, Image.BILINEAR), (depth, Image.NEAREST)))
            for a in self.anchors.values():
                a['x'] -= px
                a['top'] -= py
            self._pad, self._hold_vehicle = (0, 0, W, H), False
            fov, focal, horizon, mid, at, camy, camx = self._view(cam, W, H)
            self._mid, self._horizon = mid, horizon
            if cam.get('vehicle'):                     # your car stays level while the world leans
                P = self._segments(at, focal, horizon, mid, camy, camx, H)
                self._props(img, emis, depth, P, cam, at, camy, camx, focal, horizon, mid, W, H, only='vehicle')
        else:
            self._pad = (0, 0, W, H)
            img, emis, depth = self._frame(cam, W, H)
        self.depth = depth
        if ss > 1:
            img = img.reshape(bh, ss, bw, ss, 3).mean(axis=(1, 3))
            emis = emis.reshape(bh, ss, bw, ss, 3).mean(axis=(1, 3))
            for a in self.anchors.values():
                for k in ('x', 'top', 'w', 'h'):
                    a[k] /= ss
        self._emis_out = emis
        self._ss, self._bw, self._bh = ss, bw, bh
        self.last_report = self._report(cam, img)
        return R.finish_world(self, cam, img, ss)

    @staticmethod
    def _turn(a, deg, px, py, W, H, resample):
        """A buffer turned by `deg` (positive: the picture clockwise) about its middle, cut to W x H."""
        a = np.where(np.isinf(a), 1e9, a) if a.ndim == 2 else a
        chans = [a] if a.ndim == 2 else [a[..., k] for k in range(a.shape[2])]
        out = [np.asarray(Image.fromarray(ch.astype(np.float32), 'F').rotate(-deg, resample=resample))[py:py + H,
                                                                                                       px:px + W]
               for ch in chans]
        if a.ndim == 2:
            return np.where(out[0] >= 1e8, np.inf, out[0]).astype(np.float32)
        return np.stack(out, -1).astype(np.float32)

    def _view(self, cam, W, H):
        """The camera's lens and where it stands: focal length (pixels), the horizon's row, the column the road's
        line straight ahead falls on, the base segment and the camera's height and offset. A rolled frame is drawn
        bigger than the picture (`_pad`); the lens is the picture's."""
        px, py, Wo, Ho = getattr(self, '_pad', (0, 0, W, H))
        fov = math.radians(float(cam.get('fov', 64)))
        focal = (Wo / 2) / math.tan(fov / 2)
        horizon = py + Ho / 2 + float(cam.get('pitch', 0.0)) * Ho
        mid = px + Wo / 2 - math.tan(math.radians(float(cam.get('yaw', 0.0)))) * focal
        at = float(np.clip(float(cam.get('at', 0.0)), 0, self.road.length - self.road.seg * 2))
        camy = float(self.road.height(at)) + float(cam.get('height', 1.0))
        return fov, focal, horizon, mid, at, camy, float(cam.get('x', 0.0))

    def _segments(self, at, focal, horizon, mid, camy, camx, H):
        """Every segment ahead projected: near and far edges (column of the road's middle, row, scale, distance),
        which rows it fills, and the clip row each lies under (the lowest row the segments nearer it reach up to:
        a prop standing on it is hidden below there)."""
        rd, seg = self.road, self.road.seg
        base = int(at // seg)
        frac = at / seg - base
        idx = np.arange(base, min(rd.n, base + self.draw))
        cur = rd.curve[idx]
        dx = -rd.curve[base] * frac + np.concatenate([[0.0], np.cumsum(cur[:-1])])
        xn = np.concatenate([[0.0], np.cumsum(dx[:-1])])         # the road's middle at each near edge, sideways
        xf = xn + dx
        z1 = idx * seg - at
        z2 = z1 + seg
        y1, y2 = rd.y[idx], rd.y[idx + 1]
        out = {'idx': idx, 'z1': z1, 'z2': z2, 'xn': xn, 'xf': xf, 'y1': y1, 'y2': y2}
        zc1 = np.maximum(z1, NEAR)
        # the near edge of the camera's own segment lies behind it: start it at NEAR, where the road then is
        yc1 = np.where(z1 < NEAR, y1 + (y2 - y1) * (NEAR - z1) / seg, y1)
        xc1 = np.where(z1 < NEAR, xn + dx * (NEAR - z1) / seg, xn)
        s1, s2 = focal / zc1, focal / z2
        out.update(zc1=zc1, xc1=xc1, yc1=yc1, s1=s1, s2=s2,
                   X1=mid + s1 * (xc1 - camx), X2=mid + s2 * (xf - camx),
                   Y1=horizon - s1 * (yc1 - camy), Y2=horizon - s2 * (y2 - camy))
        clip = np.empty(len(idx))
        drawn = np.zeros(len(idx), bool)
        maxy = float(H)
        for k in range(len(idx)):
            clip[k] = maxy
            if z2[k] <= NEAR or out['Y2'][k] >= out['Y1'][k] or out['Y2'][k] >= maxy:
                continue
            drawn[k] = True
            maxy = min(maxy, out['Y2'][k])
        out['clip'], out['drawn'] = clip, drawn
        return out

    def _frame(self, cam, W, H):
        """The 3D pass: sky, road and ground, the props; colour, light (emission) and depth at W x H."""
        fov, focal, horizon, mid, at, camy, camx = self._view(cam, W, H)
        P = self._segments(at, focal, horizon, mid, camy, camx, H)
        img = np.zeros((H, W, 3), np.float32)
        emis = np.zeros((H, W, 3), np.float32)
        depth = np.full((H, W), np.inf, np.float32)
        void = any(b is None or b[-1][1] == 'void' for b in self.sides.values())     # a side ends in nothing
        self._sky(img, emis, cam, W, H, focal, horizon, mid, below=void)
        self._sky_img, self._sky_emis = img.copy(), emis.copy()          # what the water mirrors
        self._refl = np.zeros((H, W), np.float32)                         # how mirror-like each pixel's ground is
        self._ripple_k = max(1.0, W / 320.0)
        if not void:                           # beyond the farthest segment, the land lost in the haze
            far = np.arange(H) + 0.5 >= horizon
            haze = self.fog_c if self.fog_c is not None else self._ground_colour_far()
            img[far] = haze
        self.frame_lamps = self.lamps + self._headlights(cam, at, camx)
        self._frame_decals = self.decals + self._vehicle_marks(cam, at, camx)
        self._horizon_now = horizon
        if self.below:
            self._below(img, depth, P, at, camy, camx, focal, horizon, mid, W, H)
        self._ground(img, emis, depth, P, at, camx, focal, mid, W, H)
        self._gdepth = depth.copy()
        for c in self.ceilings:
            self._ceiling(img, emis, depth, P, c, at, camy, camx, focal, horizon, mid, W, H)
        for wl in self.walls:
            self._wall(img, emis, depth, P, wl, at, camy, camx, focal, horizon, mid, W, H)
        self._props(img, emis, depth, P, cam, at, camy, camx, focal, horizon, mid, W, H)
        self._focal, self._horizon, self._mid, self._camy = focal, horizon, mid, camy
        return img, emis, depth

    def _light_wall(self, sgn):
        """The light on a wall along one side of the road (sgn -1 left, 1 right), facing across it: the ambient,
        and the sun or moon by how squarely it faces the wall (the road runs along azimuth 270)."""
        L = self.ambient.copy()
        for s in self.suns:
            el = math.radians(float(s.get('elevation', 30)))
            d = math.radians(float(s.get('azimuth', 270)) - 270)
            kind = s['type']
            c = _col(s.get('color'), (1, 0.94, 0.82) if kind == 'sun' else (0.55, 0.65, 0.95))
            face = -sgn * math.sin(d) * math.cos(el)              # the wall's normal points back across the road
            L = L + c * float(s.get('intensity', 0.85 if kind == 'sun' else 0.4)) * max(0.0, face) * 1.15
        return L

    def _roof_k(self, along):
        """How much of the sky's light reaches each place along the road (1 in the open, less under a roof)."""
        k = np.ones(np.shape(along), np.float32)
        for a0, a1, f in self.roofs:
            k = np.where((along >= a0) & (along < a1), k * f, k)
        return k

    def _wall(self, img, emis, depth, P, wl, at, camy, camx, focal, horizon, mid, W, H):
        """A wall along the road: on each segment a strip standing `offset` out from the road's edge, `height`
        tall from `z` over the road (its top wandering by `ragged`) - a guard rail, a fence, a cliff, a row of
        buildings. Each strip is filled column by column, each column projected from its own distance (1/z runs
        straight across the screen); textured from its foot up by how far along and how high (`tile` units to
        the texture, or [along, up]), lit by the sun on its face, the lamps near it and its own glow, fogged, and
        drawn where it is nearer than what is there (a see-through texture leaves its holes)."""
        tex, em = wl['tex']
        alpha = wl['alpha']
        tu_k, tv_k = TEX / wl['tile'][0], TEX / wl['tile'][1]
        seg = self.road.seg
        field = WD.noise_field() if wl['ragged'] else None
        k_far = np.nonzero(P['z2'] > NEAR)[0]
        for sgn in wl['sides']:
            xo = sgn * (self.half + wl['offset'])
            flat = self._light_wall(sgn) * wl['light']
            for k in k_far[::-1]:
                a0 = P['idx'][k] * seg
                if a0 + seg <= wl['from'] or a0 >= wl['to']:
                    continue
                zn, zf = P['zc1'][k], P['z2'][k]
                Xn = mid + focal / zn * (P['xc1'][k] + xo - camx)
                Xf = mid + focal / zf * (P['xf'][k] + xo - camx)
                c0, c1 = max(0, int(math.ceil(min(Xn, Xf) - 0.5))), min(W, int(math.ceil(max(Xn, Xf) - 0.5)))
                if c1 <= c0:
                    continue
                t = np.clip((np.arange(c0, c1) + 0.5 - Xn) / (Xf - Xn), 0, 1) if abs(Xf - Xn) > 1e-6 \
                    else np.zeros(c1 - c0)
                z = 1 / ((1 - t) / zn + t / zf)
                along = at + z
                base = P['yc1'][k] + (P['y2'][k] - P['yc1'][k]) * (z - zn) / max(zf - zn, 1e-9) + wl['z']
                h = np.full(c1 - c0, wl['height'])
                face = np.zeros(c1 - c0, int)
                u0 = np.zeros(c1 - c0)
                if wl['blocks'] > 0:                  # buildings: each block its own height, facade and start
                    bi = np.floor(along / wl['blocks'])
                    rnd = _hash01(bi, np.full_like(bi, sgn), wl['seed'])
                    h = np.maximum(0.0, h + wl['ragged'] * (2 * rnd - 1))
                    face = (_hash01(bi, np.full_like(bi, sgn), wl['seed'] + 7) * len(wl['texs'])).astype(int)
                    u0 = bi * wl['blocks']
                    if wl['gaps'] > 0:                # an alley: the block left out
                        h = np.where(_hash01(bi, np.full_like(bi, sgn), wl['seed'] + 13) < wl['gaps'], 0.0, h)
                elif field is not None:               # the top wanders, the same at a place every render
                    h = np.maximum(0.0, h + wl['ragged'] * (2 * WD.sample_noise(
                        field, along / max(36.0, 12 * wl['ragged']),
                        np.full_like(along, 0.13 + 0.29 * wl['seed'] + 0.5 * (sgn > 0))) - 1))
                ybot = horizon - focal / z * (base - camy)
                ytop = horizon - focal / z * (base + h - camy)
                r0, r1 = max(0, int(math.floor(ytop.min()))), min(H, int(math.ceil(ybot.max())))
                if r1 <= r0:
                    continue
                hy = (camy + (horizon - (np.arange(r0, r1)[:, None] + 0.5)) * (z / focal)[None, :]) - base[None, :]
                in_a = (along >= wl['from']) & (along < wl['to'])
                m = (hy >= 0) & (hy < h[None, :]) & in_a[None, :] & (depth[r0:r1, c0:c1] > z[None, :])
                if not m.any():
                    continue
                ri, ci = np.nonzero(m)
                tu = ((along[ci] - u0[ci]) * tu_k).astype(int) % TEX
                tv = (TEX - 1 - (hy[ri, ci] * tv_k).astype(int)) % TEX
                fc = face[ci]
                if len(wl['texs']) > 1:               # the street's facades, each building its own
                    rgb = np.zeros((len(ri), 3), np.float32)
                    gl = np.zeros(len(ri), np.float32)
                    keep = np.ones(len(ri), bool)
                    for f, ((tx, ex), al) in enumerate(wl['texs']):
                        q = fc == f
                        if not q.any():
                            continue
                        rgb[q] = tx[tv[q], tu[q]]
                        if ex is not None:
                            gl[q] = ex[tv[q], tu[q]]
                        if al is not None:
                            keep[q] = al[tv[q], tu[q]] > 0.5
                    ri, ci, tu, tv, rgb, gl = ri[keep], ci[keep], tu[keep], tv[keep], rgb[keep], gl[keep]
                    if not len(ri):
                        continue
                    ems = gl
                else:
                    if alpha is not None:
                        keep = alpha[tv, tu] > 0.5
                        ri, ci, tu, tv = ri[keep], ci[keep], tu[keep], tv[keep]
                        if not len(ri):
                            continue
                    rgb = tex[tv, tu]
                    ems = None if em is None else em[tv, tu]
                zc = z[ci]
                L = flat[None, :] * self._roof_k(along[ci])[:, None]
                for lamp in self.frame_lamps:
                    if abs(lamp['at'] - (a0 + seg / 2)) > lamp['r'] + seg:
                        continue
                    d = np.sqrt((along[ci] - lamp['at']) ** 2 + (xo - lamp['x']) ** 2 +
                                (wl['z'] + hy[ri, ci] - lamp['z']) ** 2)
                    L = L + (np.clip(1 - d / lamp['r'], 0, 1) ** 2)[:, None] * lamp['c']
                col = rgb * L
                glow = np.zeros_like(col)
                if ems is not None:
                    glow = ems[:, None] * rgb * 1.6
                    col = col + glow
                if self.fog_c is not None and self.fog_d > 0:
                    fg = np.exp(-self.fog_d * zc)[:, None]
                    col = col * fg + self.fog_c * (1 - fg)
                    glow = glow * fg
                img[r0 + ri, c0 + ci] = col
                emis[r0 + ri, c0 + ci] = glow
                depth[r0 + ri, c0 + ci] = zc
                if self._refl[:, c0:c1].any():
                    self._reflect_wall(img, emis, depth, wl, flat, z, along, base, h, ybot, ytop, u0, face, c0, c1,
                                       camy, horizon, focal, H)

    def _reflect_wall(self, img, emis, depth, wl, flat, z, along, base, h, ybot, ytop, u0, face, c0, c1, camy,
                      horizon, focal, H):
        """A wall's mirror image on the water at its foot: each column turned upside down under it, as tall as the
        wall stands, darkened a little, blended by how mirror-like the water is - where the water still shows."""
        r0 = max(0, int(math.floor(ybot.min())))
        r1 = min(H, int(math.ceil((2 * ybot - ytop).max())))
        if r1 <= r0:
            return
        ys = np.arange(r0, r1)[:, None] + 0.5
        src = 2 * ybot[None, :] - ys                                     # the row it mirrors
        hy = (camy + (horizon - src) * (z / focal)[None, :]) - base[None, :]
        k = self._refl[r0:r1, c0:c1]
        m = (hy >= 0) & (hy < h[None, :]) & (k > 0) & ((self._gdepth[r0:r1, c0:c1] == depth[r0:r1, c0:c1]))
        if not m.any():
            return
        ri, ci = np.nonzero(m)
        tu = ((along[ci] - u0[ci]) * TEX / wl['tile'][0]).astype(int) % TEX
        tv = (TEX - 1 - (hy[ri, ci] * TEX / wl['tile'][1]).astype(int)) % TEX
        (tex, em), al = wl['texs'][0] if len(wl['texs']) == 1 else (wl['tex'], wl['alpha'])
        if len(wl['texs']) > 1:
            rgb = np.zeros((len(ri), 3), np.float32)
            gl = np.zeros(len(ri), np.float32)
            for f, ((tx, ex), _) in enumerate(wl['texs']):
                q = face[ci] == f
                rgb[q] = tx[tv[q], tu[q]]
                if ex is not None:
                    gl[q] = ex[tv[q], tu[q]]
        else:
            if al is not None:
                keep = al[tv, tu] > 0.5
                ri, ci, tu, tv = ri[keep], ci[keep], tu[keep], tv[keep]
            rgb = tex[tv, tu]
            gl = None if em is None else em[tv, tu]
        L = flat[None, :] * self._roof_k(along[ci])[:, None]
        col = rgb * L * 0.8
        glow = np.zeros_like(col) if gl is None else gl[:, None] * rgb * 1.6 * 0.8
        col = col + glow
        if self.fog_c is not None and self.fog_d > 0:
            fg = np.exp(-self.fog_d * z[ci])[:, None]
            col = col * fg + self.fog_c * (1 - fg)
            glow = glow * fg
        w = k[ri, ci][:, None]
        rows, cols = r0 + ri, c0 + ci
        img[rows, cols] = img[rows, cols] * (1 - w) + col * w
        emis[rows, cols] = emis[rows, cols] * (1 - w) + glow * w

    def _ceiling(self, img, emis, depth, P, c, at, camy, camx, focal, horizon, mid, W, H):
        """A ceiling over a stretch of road, `height` over it and following its rises: filled as the road is,
        from the camera outward - a nearer segment's ceiling hides the rows a farther one's would take - lit only by
        what light gets under it and the lamps, fogged."""
        tex, em = c['tex']
        top = -1.0                                   # the lowest row the nearer ceiling reaches down to
        rows, ks = [], []
        for k in range(len(P['idx'])):
            if P['z2'][k] <= NEAR:
                continue
            a0 = P['idx'][k] * self.road.seg
            if a0 + self.road.seg <= c['from'] or a0 >= c['to']:
                continue
            Yn = horizon - P['s1'][k] * (P['yc1'][k] + c['height'] - camy)
            Yf = horizon - P['s2'][k] * (P['y2'][k] + c['height'] - camy)
            if Yf <= Yn:                             # a ceiling below the eye is not seen from under it
                continue
            r0, r1 = max(0, int(math.ceil(max(Yn, top) - 0.5))), min(H, int(math.ceil(Yf - 0.5)))
            if r1 > r0:
                rows.append(np.arange(r0, r1))
                ks.append(np.full(r1 - r0, k))
            top = max(top, Yf)
        if not rows:
            return
        rows, ks = np.concatenate(rows), np.concatenate(ks)
        Yn = horizon - P['s1'][ks] * (P['yc1'][ks] + c['height'] - camy)
        Yf = horizon - P['s2'][ks] * (P['y2'][ks] + c['height'] - camy)
        t = np.clip((rows + 0.5 - Yn) / np.maximum(Yf - Yn, 1e-6), 0, 1)       # 0 at the near edge, 1 at the far
        z = 1 / (1 / P['zc1'][ks] + (1 / P['z2'][ks] - 1 / P['zc1'][ks]) * t)
        tau = (z - P['zc1'][ks]) / np.maximum(P['z2'][ks] - P['zc1'][ks], 1e-9)
        xw = P['xc1'][ks] + (P['xf'][ks] - P['xc1'][ks]) * tau
        along = at + z
        X = camx + (np.arange(W)[None, :] + 0.5 - mid) * (z / focal)[:, None] - xw[:, None]
        tu = (X * TEX / c['tile']).astype(int) % TEX
        tv = np.repeat(((along * TEX / c['tile']).astype(int) % TEX)[:, None], W, 1)
        rgb = tex[tv, tu]
        L = np.broadcast_to((self._light_flat() * self._roof_k(along)[:, None])[:, None, :], rgb.shape).copy()
        for lamp in self.frame_lamps:
            near = np.abs(along - lamp['at']) < lamp['r']
            if not near.any():
                continue
            rr = np.nonzero(near)[0]
            d = np.sqrt((along[rr, None] - lamp['at']) ** 2 + (X[rr] - lamp['x']) ** 2 + (c['height'] - lamp['z']) ** 2)
            L[rr] += (np.clip(1 - d / lamp['r'], 0, 1) ** 2)[..., None] * lamp['c']
        col = rgb * L
        glow = np.zeros_like(col) if em is None else em[tv, tu][..., None] * rgb * 1.6
        col = col + glow
        if self.fog_c is not None and self.fog_d > 0:
            fg = np.exp(-self.fog_d * z)[:, None, None]
            col = col * fg + self.fog_c * (1 - fg)
            glow = glow * fg
        m = depth[rows] > z[:, None]
        ri, ci = np.nonzero(m)
        img[rows[ri], ci] = col[ri, ci]
        emis[rows[ri], ci] = glow[ri, ci]
        depth[rows[ri], ci] = z[ri]

    def _below(self, img, depth, P, at, camy, camx, focal, horizon, mid, W, H):
        """The land far below a road with a drop beside it (`below`): a flat plane `depth` under the road's
        start, seen past its edge on a `void` side - a valley floor - lit as open ground, fogged by its distance."""
        b = self.below
        r0 = int(math.floor(horizon + 0.5))
        if r0 >= H:
            return
        rows = np.arange(max(0, r0), H)
        dy = rows + 0.5 - horizon
        z = focal * (camy + b['depth']) / np.maximum(dy, 1e-3)
        ok = z < 6000
        rows, z = rows[ok], z[ok]
        # the plane bends with the road, as the ground does: the road's middle at each distance
        zs = np.concatenate([P['zc1'][:1], P['z2']])
        xs = np.concatenate([P['xc1'][:1], P['xf']])
        xw = np.interp(z, zs, xs)
        X = camx + (np.arange(W)[None, :] + 0.5 - mid) * (z / focal)[:, None] - xw[:, None]
        along = at + z
        tu = (X * TEX / b['tile']).astype(int) % TEX
        tv = np.repeat(((along * TEX / b['tile']).astype(int) % TEX)[:, None], W, 1)
        past = np.abs(X) - self.half                 # out from the road's edge: the valley in bands along it
        col = np.zeros(X.shape + (3,), np.float32)
        lo = 0.0
        for hi, spec, tint, *_ in b['bands']:
            m = (past < hi) & (past >= lo) if lo > 0 else past < hi
            if m.any():
                col[m] = assets.get_texture(spec)[0][tv[m], tu[m]] * tint
            lo = hi
        col = col * self._light_flat()
        if self.fog_c is not None and self.fog_d > 0:           # `haze` thins the air down there (or thickens it)
            fg = np.exp(-self.fog_d * b['haze'] * z)[:, None, None]
            col = col * fg + self.fog_c * (1 - fg)
        m = np.isinf(depth[rows])
        ri, ci = np.nonzero(m)
        img[rows[ri], ci] = col[ri, ci]
        depth[rows[ri], ci] = z[ri]

    def _ground_colour_far(self):
        bands = self.sides['left'] or self.sides['right']
        tex = assets.get_texture(bands[-1][1])[0]
        return tex.reshape(-1, 3).mean(0) * bands[-1][2] * self._light_flat()

    def _light_flat(self):
        """The light on open ground: the ambient and the sun or moon, by how high it stands."""
        L = self.ambient.copy()
        for s in self.suns:
            el = math.radians(float(s.get('elevation', 30)))
            kind = s['type']
            c = _col(s.get('color'), (1, 0.94, 0.82) if kind == 'sun' else (0.55, 0.65, 0.95))
            L = L + c * float(s.get('intensity', 0.85 if kind == 'sun' else 0.4)) * max(0.0, math.sin(el))
        return L

    def _sky(self, img, emis, cam, W, H, focal, horizon, mid, below=False):
        """The scene's sky panorama behind everything, turned with the camera's `yaw` (the road runs north, along
        azimuth 270), its sun or moon placed by the lights."""
        name = self.s.get('sky', 'day')
        if not name:
            return
        rows = int(max(1, math.ceil(horizon)))
        pano_w = int(round(W * 2 * math.pi / (2 * math.atan(W / 2 / focal))))
        extra = max(2, H - rows + 2) if below else 0
        key = (pano_w, max(rows, H // 2), round(focal, 3), extra)
        if key not in self._skies:
            discs = []
            for s in self.suns:
                if s.get('disc', True):
                    sun = s['type'] == 'sun'
                    discs.append({'azimuth': float(s.get('azimuth', 270)), 'elevation': float(s.get('elevation', 20)),
                                  'color': s.get('disc_color', [1.0, 0.92, 0.7] if sun else [0.92, 0.94, 1.0]),
                                  'radius': float(s.get('disc_size', 2.6 if sun else 2.0)),
                                  'glow': 0.5 if sun else 0.35, 'style': s.get('disc_style')})
            self._skies[key] = assets.make_sky(name, pano_w, key[1], skyline=self.s.get('skyline'), proj=focal,
                                               discs=discs, objects=list(self.s.get('sky_objects') or []),
                                               below=extra)
        pano = self._skies[key]
        ph = key[1]
        view = math.radians(270 + float(cam.get('yaw', 0.0)))
        ang = (view + np.arctan((np.arange(W) + 0.5 - mid) / focal)) % (2 * math.pi)
        cols = (ang / (2 * math.pi) * pano_w).astype(int) % pano_w
        rr = np.arange(H) if below else np.arange(min(H, rows + 2))
        pr = np.clip(ph - (horizon - rr) - 1, 0, pano.shape[0] - 1).astype(int)
        img[rr] = pano[pr][:, cols]
        emis[rr] = np.maximum(img[rr] - 0.9, 0) * 6.0
        if self.fog_c is not None:
            k = float((self.s.get('fog') or {}).get('sky_mix', 0.35))
            img[rr] = img[rr] * (1 - k) + self.fog_c * k

    def _ground(self, img, emis, depth, P, at, camx, focal, mid, W, H):
        """The road and the ground beside it, row by row: every row belongs to the one segment that reaches it,
        and every pixel in it to a spot on the road (`along`, `x` across) - its texture, its markings, its band
        and the light on it."""
        rd = self.road
        rows, ks = [], []
        for k in np.nonzero(P['drawn'])[0]:
            r0 = max(0, int(math.ceil(P['Y2'][k] - 0.5)))
            r1 = min(H, int(math.ceil(min(P['Y1'][k], P['clip'][k]) - 0.5)))
            if r1 > r0:
                rows.append(np.arange(r0, r1))
                ks.append(np.full(r1 - r0, k))
        if not rows:
            return
        rows, ks = np.concatenate(rows), np.concatenate(ks)
        t = np.clip((rows + 0.5 - P['Y2'][ks]) / np.maximum(P['Y1'][ks] - P['Y2'][ks], 1e-6), 0, 1)
        iz = 1 / P['z2'][ks] + (1 / P['zc1'][ks] - 1 / P['z2'][ks]) * t      # 1/z runs straight down the screen
        z = 1 / iz
        tau = (z - P['z2'][ks]) / np.minimum(P['zc1'][ks] - P['z2'][ks], -1e-9)  # 0 at the far edge, 1 at the near
        xw = P['xf'][ks] + (P['xc1'][ks] - P['xf'][ks]) * tau                    # the road's middle, sideways
        along = at + z
        xs = np.arange(W) + 0.5
        X = camx + (xs[None, :] - mid) * (z / focal)[:, None] - xw[:, None]       # every pixel's place across
        A = np.repeat(along[:, None], W, 1)
        ax = np.abs(X)
        band = ((np.floor(along / (rd.seg * self.stripe)).astype(int)) % 2 == 0)[:, None]
        half = self.half
        if self.ragged:                         # a path's edge wanders, and the ground creeps onto it in tufts
            wob = (np.sin(A * 1.7 + np.sign(X) * 2.1) * 0.5 + np.sin(A * 0.53 + np.sign(X)) * 0.5) * self.ragged
            half = half + wob
        edge_in = ax - half                     # how far past the road's edge (negative: on the road)
        if self.blend:
            n = _hash01(np.floor(X * 8), np.floor(A * 8), 7)
            edge_in = edge_in + (n - 0.5) * self.blend
        out = np.zeros(ax.shape + (3,), np.float32)
        lightk = np.zeros(ax.shape + (3,), np.float32)
        refl = np.zeros(ax.shape, np.float32)
        tv = (A * TEX).astype(int) % TEX
        tu = (X * TEX).astype(int) % TEX
        on = edge_in < 0
        lift = np.broadcast_to(np.where(band, 1 + self.bands / 2, 1 - self.bands / 2), X.shape)
        out[on] = self.surface[tv[on], tu[on]] * lift[on][:, None]
        if self.surface_em is not None:
            lightk[on] = self.surface_em[tv[on], tu[on]][:, None] * self.surface[tv[on], tu[on]] * 1.6
        roofed = np.zeros(len(along), bool)
        for a0, a1, _ in self.roofs:
            roofed |= (along >= a0) & (along < a1)
        refl[on] = np.where(np.broadcast_to(roofed[:, None], on.shape), self.dry, self.wet)[on]
        holes = on & (self.surface_alpha[tv, tu] < 0.5) if self.surface_alpha is not None else None
        # the markings: dashed lane lines on the light bands, solid edge and centre lines
        if self.lines is not None and self.lanes > 1:
            for j in range(1, self.lanes):
                lx = -self.half + 2 * self.half * j / self.lanes
                if self.centre is not None and abs(lx) < 1e-6:
                    continue
                m = on & (np.abs(X - lx) < 0.07) & band
                out[m] = self.lines
        if self.centre is not None:
            m = on & (np.abs(np.abs(X) - 0.09) < 0.045)
            out[m] = self.centre
        if self.edges is not None:
            m = on & (np.abs(ax - (half - 0.25)) < 0.06)
            out[m] = self.edges
        past = edge_in
        if self.rumble:
            w = self.rumble['width']
            m = (past >= 0) & (past < w)
            c0, c1 = self.rumble['colors']
            out[m] = np.where(np.broadcast_to(band, m.shape)[m][:, None], c0, c1)
            past = past - w
            on_r = m
        else:
            on_r = np.zeros_like(on)
        rest = (past >= 0) & ~on & ~on_r
        if self.shoulder:
            w = self.shoulder['width']
            m = rest & (past < w)
            out[m] = self.shoulder['tex'][tv[m], tu[m]]
            past = past - w
            rest = rest & ~m
        shade = np.where(band, 1 + self.bands, 1 - self.bands)
        void = np.zeros(ax.shape, bool)
        for side, sgn in (('left', -1), ('right', 1)):
            bands = self.sides[side]
            m = rest & ((X < 0) if sgn < 0 else (X >= 0))
            if bands is None:
                void |= m
                continue
            lo = 0.0
            for hi, spec, tint, rk, own, tile in bands:
                b = m & (past >= lo) & (past < hi)
                if b.any() and spec == 'void':                         # the ground ends: nothing beyond
                    void |= b
                elif b.any():
                    tex = assets.get_texture(spec)[0]
                    em = assets.get_texture(spec)[1]
                    bv, bu = (tv[b], tu[b]) if tile == 1.0 else (      # a band's own `tile`: a big pattern
                        (A[b] * TEX / tile).astype(int) % TEX, (X[b] * TEX / tile).astype(int) % TEX)
                    out[b] = tex[bv, bu] * tint * np.broadcast_to(shade, b.shape)[b][:, None]
                    refl[b] = np.where(np.broadcast_to(roofed[:, None], b.shape), own, rk)[b]
                    if em is not None:
                        lightk[b] = em[bv, bu][:, None] * tex[bv, bu] * 1.6
                lo = hi
        if holes is not None:                     # through a see-through road, whatever lies beyond it
            void |= holes
        self._stamp(out, lightk, A, X, along, ~void, refl)
        # the light on it: ambient and sun alike over open ground, and the lamps along the road
        L = np.broadcast_to(self._light_flat(), out.shape).copy()
        for a0, a1, k in self.roofs:              # under a roof the sky's light is gone; the lamps still reach
            m = (along >= a0) & (along < a1)
            L[m] *= k
        for lamp in self.frame_lamps:
            near = np.abs(along - lamp['at']) < lamp['r']
            if not near.any():
                continue
            rr = np.nonzero(near)[0]
            d2 = (A[rr] - lamp['at']) ** 2 + (X[rr] - lamp['x']) ** 2 + lamp['z'] ** 2
            f = np.clip(1 - np.sqrt(d2) / lamp['r'], 0, 1) ** 2
            L[rr] += f[..., None] * lamp['c']
        col = out * L + lightk
        emis_g = lightk.copy()
        if refl.any():                       # water and wet road mirror the sky about the horizon, rippling
            col, emis_g = self._mirror_sky(col, emis_g, refl, rows, A, X)
        if self.fog_c is not None and self.fog_d > 0:
            fog = np.exp(-self.fog_d * z)[:, None, None]
            col = col * fog + self.fog_c * (1 - fog)
            emis_g = emis_g * fog
        keep = ~void
        rr_, cc_ = np.nonzero(keep)
        img[rows[rr_], cc_] = col[rr_, cc_]
        emis[rows[rr_], cc_] = emis_g[rr_, cc_]
        depth[rows[rr_], cc_] = z[rr_]
        self._refl[rows[rr_], cc_] = refl[rr_, cc_]

    def _ripple(self, rows, A, X):
        """How far sideways (pixels) the mirror image shifts at each place: a few small waves across the water."""
        return np.round(self.ripple * self._ripple_k * (np.sin(A * 3.1 + X * 0.7) * 0.9 +
                                                        np.sin(A * 7.3 - X * 1.9 + 1.3) * 0.6)).astype(int)

    def _mirror_sky(self, col, emis_g, refl, rows, A, X):
        """The sky's mirror image on the reflective pixels: each takes the sky's colour at the row as far above the
        horizon as it lies below it (and the sky's light, so the sun glints on the sea)."""
        H, W = self._sky_img.shape[:2]
        m = refl > 0
        ri, ci = np.nonzero(m)
        mr = np.clip(np.round(2 * self._horizon_now - (rows[ri] + 0.5)).astype(int), 0, H - 1)
        mc = np.clip(ci + self._ripple(rows[ri], A[ri, ci], X[ri, ci]), 0, W - 1)
        k = refl[ri, ci][:, None]
        roof = self._roof_k(A[ri, ci])[:, None]          # under a roof the sky is not there to be mirrored
        col[ri, ci] = col[ri, ci] * (1 - k) + self._sky_img[mr, mc] * k * roof
        emis_g[ri, ci] = emis_g[ri, ci] + self._sky_emis[mr, mc] * k * roof
        return col, emis_g

    def _stamp(self, out, lightk, A, X, along, keep, refl=None):
        """The decals, lying flat on the road and the ground: each pixel's place (along, across) inside one picks
        its texel, blended over the surface by the decal's alpha."""
        decals = getattr(self, '_frame_decals', self.decals)
        if not decals:
            return
        lo, hi = float(along.min()), float(along.max())
        ddefs = self.s.get('decal_defs')
        for d in decals:
            r = 0.5 * math.hypot(d['w'], d['h'])
            if d['at'] + r < lo or d['at'] - r > hi:
                continue
            rr = np.nonzero(np.abs(along - d['at']) < r)[0]
            if not len(rr):
                continue
            dx = X[rr] - d['x']
            da = A[rr] - d['at']
            u = (dx * d['c'] + da * d['s']) / d['w'] + 0.5
            v = 0.5 - (da * d['c'] - dx * d['s']) / d['h']
            m = (u >= 0) & (u < 1) & (v >= 0) & (v < 1) & keep[rr]
            if not m.any():
                continue
            rgba, em = assets.get_decal(d['tex'], ddefs)
            hh, ww = rgba.shape[:2]
            ri, ci = np.nonzero(m)
            tu = (u[ri, ci] * ww).astype(int).clip(0, ww - 1)
            if d['flip']:
                tu = ww - 1 - tu
            tv = (v[ri, ci] * hh).astype(int).clip(0, hh - 1)
            px = rgba[tv, tu]
            a = px[:, 3:4] * d['opacity']
            rows = rr[ri]
            rgb = px[:, :3] * d['tint']
            out[rows, ci] = out[rows, ci] * (1 - a) + rgb * a
            if refl is not None and d['reflect'] > 0:          # a puddle mirrors where it lies
                refl[rows, ci] = np.maximum(refl[rows, ci], d['reflect'] * a[:, 0])
            if em is not None and em.max() > 0:                  # a glowing mark (a rune) lights itself
                lightk[rows, ci] += em[tv, tu][:, None] * rgb * a * 1.6

    def _props(self, img, emis, depth, P, cam, at, camy, camx, focal, horizon, mid, W, H, only=None):
        """Everything standing along the road, far to near: each scaled by its distance, standing on the road's
        height there, lit by the ambient, the sun and the lamps near it, fogged, and cut off below the clip row of
        its segment so a crest in front of it hides its foot. `only` 'vehicle' draws just the shot's vehicle; under
        a roll it is left out of the first pass (`_hold_vehicle`) and drawn so, level, after the frame is turned."""
        seg = self.road.seg
        base = int(P['idx'][0])
        items = [] if only == 'vehicle' else list(self.items)
        v = cam.get('vehicle')
        if v and (only == 'vehicle' or not getattr(self, '_hold_vehicle', False)):
            it = dict(assets.sprite_defaults(v['type'], self.defs))
            it.update(v)
            it.update(at=at + float(v.get('ahead', 2.4)), x=camx + float(v.get('x', 0.0)), _vehicle=True)
            it['type'] = assets.variant_name({**it, 'x': it['at'], 'y': it['x']}, self.s)
            items.append(it)
        for sp in cam.get('extra_sprites', []) if only is None else []:
            items.append(dict(sp, at=float(sp.get('at', 0.0)), x=float(sp.get('x', 0.0))))
        flat = self._light_flat()
        refl_on = only is None and bool(self._refl.any()) if hasattr(self, '_refl') else False
        drawn = []
        for it in items:
            z = it['at'] - at
            if z < NEAR or z > self.draw * seg:
                continue
            k = int(it['at'] // seg) - base
            if not 0 <= k < len(P['idx']):
                continue
            f = it['at'] / seg - int(it['at'] // seg)
            xr = P['xn'][k] + (P['xf'][k] - P['xn'][k]) * f
            yr = P['y1'][k] + (P['y2'][k] - P['y1'][k]) * f
            drawn.append((z, k, xr, yr, it))
        drawn.sort(key=lambda d: -d[0])
        for z, k, xr, yr, it in drawn:
            spec = it['type']
            rgba, em = assets.get_sprite(spec, self.defs, view=it.get('view', 'front'))
            rgba = np.asarray(rgba, np.float32)
            em = np.asarray(em, np.float32)
            s = focal / z
            hpx = s * float(it.get('scale', 1.0))
            if hpx < 1.0:
                continue
            wpx = hpx * rgba.shape[1] / rgba.shape[0]
            cx = mid + s * (xr + it['x'] - camx)
            bot = horizon - s * (yr + float(it.get('z', 0.0)) - camy)
            top, left = bot - hpx, cx - wpx / 2
            clip = H if it.get('_vehicle') else P['clip'][k]
            r0, r1 = max(0, int(math.floor(top))), min(H, int(math.ceil(min(bot, clip))))
            c0, c1 = max(0, int(math.floor(left))), min(W, int(math.ceil(left + wpx)))
            if it.get('_vehicle'):                 # where the shot's own vehicle is, for `speed` to leave sharp
                self.anchors['_vehicle'] = {'x': cx, 'top': top, 'w': wpx, 'h': hpx, 'depth': z, 'visible': True}
            if it.get('id'):
                self.anchors[it['id']] = {'x': cx, 'top': top, 'w': wpx, 'h': hpx, 'depth': z,
                                          'visible': -wpx < cx < W + wpx and top + hpx > 0 and top < H}
            if r1 <= r0 or c1 <= c0:
                continue
            self._contact_shadow(img, depth, it, z, s, cx, bot, clip, camy - yr, rgba.shape, W, H)
            vv = ((np.arange(r0, r1) + 0.5 - top) / hpx * rgba.shape[0]).astype(int).clip(0, rgba.shape[0] - 1)
            uu = ((np.arange(c0, c1) + 0.5 - left) / wpx * rgba.shape[1]).astype(int).clip(0, rgba.shape[1] - 1)
            if it.get('flip'):
                uu = rgba.shape[1] - 1 - uu
            sub = rgba[vv][:, uu]
            e = em[vv][:, uu]
            if e.ndim == 2:
                e = e[..., None]
            a = sub[..., 3] > 0.5
            near_d = depth[r0:r1, c0:c1] > z
            a &= near_d
            if not a.any():
                continue
            L = flat.copy()
            for a0, a1, kk in self.roofs:
                if a0 <= it['at'] < a1:
                    L = L * kk
            for lamp in self.frame_lamps:
                d = math.sqrt((it['at'] - lamp['at']) ** 2 + (it['x'] - lamp['x']) ** 2 +
                              (float(it.get('scale', 1.0)) * 0.5 - lamp['z']) ** 2)
                if d < lamp['r']:
                    L = L + lamp['c'] * (1 - d / lamp['r']) ** 2
            tint = _col(it.get('tint'))
            full = bool(it.get('fullbright'))
            light = full or it.get('blend', 'alpha') in ADDITIVE    # a prop that is all light takes its tint
            rgb = sub[..., :3] * (tint if light else np.where(e > 0, 1.0, tint))   # else a tint skips its lamps
            lit = rgb if full else rgb * L
            colour = np.where(e > 0, np.maximum(lit, rgb * np.clip(e, 0, 1)), lit)
            glow = rgb * np.clip(e, 0, 1) if not full else rgb
            if self.fog_c is not None and self.fog_d > 0 and not it.get('_vehicle'):
                fg = math.exp(-self.fog_d * z)
                colour = colour * fg + self.fog_c * (1 - fg)
                glow = glow * fg
            op = float(it.get('opacity', 1.0))
            blend = it.get('blend', 'alpha')
            if refl_on:
                self._reflect_prop(img, emis, depth, rgba, em, tint, L, full, op, blend, z, top, bot, left, hpx, wpx,
                                   bool(it.get('flip')), H, W)
            reg = img[r0:r1, c0:c1]
            if blend in ADDITIVE:
                reg[a] = reg[a] + colour[a] * op
            else:
                reg[a] = reg[a] * (1 - op) + colour[a] * op
            ereg = emis[r0:r1, c0:c1]
            if blend in ADDITIVE:
                ereg[a] = ereg[a] + glow[a] * op
            else:                               # an opaque prop hides the light behind it as it hides the rest
                ereg[a] = ereg[a] * (1 - op) + glow[a] * op
            if blend not in ADDITIVE and op >= 0.99:
                depth[r0:r1, c0:c1][a] = z

    def _reflect_prop(self, img, emis, depth, rgba, em, tint, L, full, op, blend, z, top, bot, left, hpx, wpx, flip,
                      H, W):
        """A prop's mirror image on the water (or the wet road) in front of it: its picture turned upside down under
        its foot, as tall as it stands, rippling, darkened a little and blended by how mirror-like each pixel's
        ground is - only where that ground still shows (nothing nearer stands over it)."""
        r0, r1 = max(0, int(math.ceil(bot - 0.5))), min(H, int(math.ceil(bot + hpx - 0.5)))
        c0, c1 = max(0, int(math.floor(left))), min(W, int(math.ceil(left + wpx)))
        if r1 <= r0 or c1 <= c0:
            return
        k = self._refl[r0:r1, c0:c1]
        if not k.any():
            return
        hh, ww = rgba.shape[:2]
        ys = np.arange(r0, r1) + 0.5
        vv = (((2 * bot - ys) - top) / hpx * hh).astype(int).clip(0, hh - 1)
        shift = np.round(self.ripple * self._ripple_k * np.sin(ys * 0.9 + z * 3.0) * 1.2).astype(int)
        cols = np.arange(c0, c1)[None, :] - shift[:, None]
        uu = ((cols + 0.5 - left) / wpx * ww).astype(int).clip(0, ww - 1)
        if flip:
            uu = ww - 1 - uu
        sub = rgba[vv[:, None], uu]
        e = em[vv[:, None], uu]
        if e.ndim == 2:
            e = e[..., None]
        a = (sub[..., 3] > 0.5) & (k > 0)
        a &= (self._gdepth[r0:r1, c0:c1] == depth[r0:r1, c0:c1])    # the water still shows there
        if not a.any():
            return
        rgb = sub[..., :3] * (tint if full or blend in ADDITIVE else np.where(e > 0, 1.0, tint))
        lit = rgb if full else rgb * L
        colour = np.where(e > 0, np.maximum(lit, rgb * np.clip(e, 0, 1)), lit) * 0.82
        glow = (rgb * np.clip(e, 0, 1) if not full else rgb) * 0.82
        if self.fog_c is not None and self.fog_d > 0:
            fg = math.exp(-self.fog_d * z)
            colour = colour * fg + self.fog_c * (1 - fg)
            glow = glow * fg
        w = (k * op)[..., None] * a[..., None]
        reg = img[r0:r1, c0:c1]
        ereg = emis[r0:r1, c0:c1]
        if blend in ADDITIVE:
            reg += colour * w
            ereg += glow * w
        else:
            reg[:] = reg * (1 - w) + colour * w
            ereg[:] = ereg * (1 - w) + glow * w

    def _contact_shadow(self, img, depth, it, z, s, cx, bot, clip, rise, shape, W, H):
        """A soft dark disc on the ground under a prop's foot, as the raycaster's contact shadow: as wide as the
        prop and a little more, foreshortened by the camera's height over the ground there (`rise`)."""
        own = it.get('shadow')
        k = self.shadow if own is None or own is True else 0.0 if own is False else float(own)
        if (k <= 0 or float(it.get('z', 0.0)) > 0.05 or it['type'].split('~')[0] in assets.NO_CONTACT_SHADOW
                or it.get('fullbright') or it.get('blend', 'alpha') != 'alpha' or float(it.get('opacity', 1)) < 1):
            return
        width = float(it.get('scale', 1.0)) * shape[1] / shape[0]
        R = min(max(width * 0.62 + 0.06, 0.15), 0.9)                # the disc's radius, in units
        rx = s * R
        ry = max(0.8, rx * max(rise, 0.05) / z)
        r0, r1 = max(0, int(bot - ry)), min(H, int(math.ceil(min(bot + ry, clip))))
        c0, c1 = max(0, int(cx - rx)), min(W, int(math.ceil(cx + rx)))
        if r1 <= r0 or c1 <= c0:
            return
        yy, xx = np.mgrid[r0:r1, c0:c1].astype(np.float32) + 0.5
        d2 = ((xx - cx) / rx) ** 2 + ((yy - bot) / ry) ** 2
        f = np.clip(1 - d2, 0, 1) ** 1.5
        dz = depth[r0:r1, c0:c1]
        on = np.abs(dz - z) < R * 1.6 + 0.2                          # the ground round its foot, nothing else
        img[r0:r1, c0:c1] *= (1 - k * 0.75 * f * on)[..., None]

    # ------------------------------------------------------------------ what the finishing passes need

    def camera_light(self, cam):
        """The light on things held at the camera (viewmodels): the ambient and the sun."""
        return np.clip(self._light_flat(), 0.22, 1.0).astype(np.float32)

    def _weather_ctx(self, cam, ss, bw, bh):
        """What the world-stage post effects need: the depth buffer and the camera's rays at output resolution,
        an open world under the sky (rain falls everywhere), the fog, the light buffer, the suns in view."""
        ctx = {'seed': int(self.s.get('seed', 0)) + int(cam.get('seed', 0)), 'world': self.w,
               'fog_d': self.fog_d if self.fog_c is not None else 0.0, 'anchors': self.anchors, 'focus': None}
        dz = self.depth.reshape(bh, ss, bw, ss).min(axis=(1, 3)) if ss > 1 else self.depth
        cols = (np.arange(bw) + 0.5) * ss
        ctx['rays'] = {'px': 0.5, 'py': 0.5, 'rdx': (cols - self._mid) / self._focal, 'rdy': np.ones(bw),
                       'horizon': self._horizon / ss, 'proj': self._focal / ss,
                       'camz': float(cam.get('height', 1.0))}
        ctx['depth'] = dz
        ctx['emission'] = self._emis_out
        ctx['suns'] = self._suns_in_view(cam, dz, ss)
        return ctx

    def _suns_in_view(self, cam, depth, ss):
        """Each sun or moon disc in the frame (output pixels), for the flare and the streaks."""
        out = []
        H, W = depth.shape
        proj, horizon, mid = self._focal / ss, self._horizon / ss, self._mid / ss
        view = 270 + float(cam.get('yaw', 0.0))
        for s in self.suns:
            if not s.get('disc', True):
                continue
            delta = math.radians((float(s.get('azimuth', 270)) - view + 180) % 360 - 180)
            if abs(delta) >= math.radians(80):
                continue
            x = mid + proj * math.tan(delta) - 0.5
            y = horizon - proj * math.tan(math.radians(float(s.get('elevation', 20)))) - 0.5
            r = max(1.0, proj * math.tan(math.radians(float(s.get('disc_size', 2.6)))))
            n = int(math.ceil(r))
            gy, gx = np.mgrid[-n:n + 1, -n:n + 1]
            inside = gx * gx + gy * gy <= r * r
            py, px = np.round(y + gy[inside]).astype(int), np.round(x + gx[inside]).astype(int)
            on = (py >= 0) & (py < H) & (px >= 0) & (px < W)
            seen = np.isinf(depth[py[on], px[on]]).sum() / max(1, inside.sum())
            if seen > 0:
                out.append({'x': x, 'y': y, 'r': r, 'color': s.get('disc_color', [1.0, 0.92, 0.7]),
                            'visible': float(seen), 'power': 1.0 if s['type'] == 'sun' else 0.4})
        return out

    def _report(self, cam, img):
        """Problems with the frame worth a warning: too dark, blown out, a camera past the road's end."""
        out = []
        lum = img @ np.array([0.299, 0.587, 0.114], np.float32)
        if float(lum.mean()) < 0.045:
            out.append(f'the frame is very dark (mean brightness {float(lum.mean()):.2f}): raise "ambient" '
                       'or add lights')
        if float((lum > 0.97).mean()) > 0.25:
            out.append('a quarter of the frame is near white: lower the sun, the lights or "ambient"')
        if float(cam.get('at', 0.0)) > self.road.length - self.road.seg * 2:
            out.append(f'the camera is at {cam.get("at")}, past the road\'s end ({self.road.length:g}): '
                       'lengthen the sections')
        return out


# ------------------------------------------------------------------ the layout check

def draw_map(scene, cams, path, scale=4):
    """The road seen from above, for checking a layout (render.py --map): its line bending as its curves bend it
    (a top view of what the camera sees as it drives), the props along it as dots, the cameras as arrows."""
    road = Road(scene['road'])
    heading = -math.pi / 2 + np.concatenate([[0.0], np.cumsum(road.curve * 1.6)])
    pts = np.stack([np.concatenate([[0.0], np.cumsum(np.cos(heading[:-1]))]),
                    np.concatenate([[0.0], np.cumsum(np.sin(heading[:-1]))])], 1) * road.seg
    lo, hi = pts.min(0) - 12, pts.max(0) + 12
    size = ((hi - lo) * scale).astype(int) + 1
    im = Image.new('RGB', (int(size[0]), int(size[1])), (24, 26, 30))
    d = ImageDraw.Draw(im)

    def to(p):
        return (float((p[0] - lo[0]) * scale), float((p[1] - lo[1]) * scale))

    half = float(scene['road'].get('width', 4.0)) / 2
    d.line([to(p) for p in pts[::2]], fill=(120, 120, 128), width=max(1, int(half * 2 * scale)))
    d.line([to(p) for p in pts[::2]], fill=(220, 220, 90), width=1)

    def place(at, x):
        i = int(np.clip(at / road.seg, 0, road.n - 1))
        h = heading[i]
        return pts[i] + np.array([-math.sin(h), math.cos(h)]) * x

    rr = RoadRenderer(scene)
    for wl in rr.walls:                                 # the walls along it, as lines
        for sgn in wl['sides']:
            ii = [i for i in range(0, road.n, 2) if wl['from'] <= i * road.seg < wl['to']]
            if len(ii) > 1:
                d.line([to(place(i * road.seg, sgn * (half + wl['offset']))) for i in ii], fill=(170, 150, 120), width=2)
    for it in rr.items:
        p = to(place(it['at'], it['x']))
        d.ellipse([p[0] - 1.5, p[1] - 1.5, p[0] + 1.5, p[1] + 1.5], fill=(90, 170, 90))
    for k, c in enumerate(cams):
        a = float(c.get('at', 0.0))
        p = place(a, float(c.get('x', 0.0)))
        i = int(np.clip(a / road.seg, 0, road.n - 1))
        h = heading[i] + math.radians(float(c.get('yaw', 0.0)))
        q = p + np.array([math.cos(h), math.sin(h)]) * 5
        d.line([to(p), to(q)], fill=(255, 120, 80), width=2)
        d.text((to(p)[0] + 4, to(p)[1] - 4), str(k + 1), fill=(255, 255, 255))
    im.save(path)

"""Prefabs: named groups of things, placed together with one line of a scene.

A prefab is a small scene of its own laid out round an origin - sprites (billboards or crossed
planes), point lights, decals, scatter, other prefabs, and even a patch of map with its own
legend - and a scene places it by name, position and turn:

    "prefabs": [{"type": "campsite", "x": 12.5, "y": 20.5, "angle": 30, "seed": 2}]

Before anything else reads the scene, `expand` turns every placement into ordinary sprites,
lights, decals, scatter and map cells, so a placed prefab lights, occludes and scatters exactly
like parts placed by hand. The built-ins are in PREFABS below; a scene defines its own under
"prefab_defs" in the same form.

Inside a prefab, a part's `dx`, `dy` are world units from its origin before it turns: at angle 0
+dx points east (+x), at 90 south, the camera's compass. A prefab with a `map` lays its `anchor`
cell (the middle one by default) on the cell holding the origin, puts the origin at that cell's
centre, and turns in quarter turns so its walls stay on the grid. Map characters its own legend
defines are given fresh characters, so they cannot clash with the scene's; any other character
is written as it is and means whatever the scene's legend says. A space leaves the cell alone.

Parts can vary: `jitter` moves a part by up to that much, `chance` keeps it only that often, a
[low, high] pair for `scale`, `z` or `angle` picks a value in between, and "flip": "random"
mirrors half of them. A prefab-level `scale` pair varies the whole group. The placement's
`seed` picks the variation, so the same seed gives the same group.
"""
import math
import random

import daylight
import objects

MAX_DEPTH = 6
PLACEMENT_KEYS = {'type', 'x', 'y', 'dx', 'dy', 'angle', 'scale', 'seed', 'id', 'title', 'notes'}
FACES = {'east': 0, 'south': 90, 'west': 180, 'north': 270}

# ------------------------------------------------------------------ the built-in prefabs

PREFABS = {
    'campsite': {
        'description': 'a fire in a ring of stones, logs to sit on, its own warm light',
        'sprites': [
            {'type': 'campfire'},
            {'type': 'log', 'dx': 0.95, 'dy': 0.25, 'flip': True},
            {'type': 'log', 'dx': -0.9, 'dy': 0.4},
            {'type': 'stump', 'dx': 0.35, 'dy': -0.95, 'chance': 0.7},
            {'type': 'rocks', 'dx': -0.45, 'dy': -0.55, 'scale': [0.14, 0.2], 'flip': 'random'},
            {'type': 'grass_tuft', 'dx': 1.3, 'dy': -0.7, 'jitter': 0.3, 'chance': 0.8, 'scale': [0.3, 0.45]},
            {'type': 'grass_tuft', 'dx': -1.2, 'dy': -0.3, 'jitter': 0.3, 'chance': 0.8, 'scale': [0.3, 0.45]},
        ],
        'lights': [{'dx': 0, 'dy': 0, 'z': 0.35, 'radius': 4.5, 'color': [1.0, 0.62, 0.3], 'intensity': 1.4}],
        'decals': [{'tex': 'scorch', 'dx': 0, 'dy': 0, 'size': 1.1}],
    },
    'palm_grove': {
        'description': 'three palms, one leaning out, coconuts and dry grass at their feet',
        'scale': [0.9, 1.1],
        'sprites': [
            {'type': 'palm', 'scale': [3.0, 3.6], 'flip': 'random'},
            {'type': 'palm_lean', 'dx': 1.3, 'dy': 0.7, 'scale': [2.8, 3.3], 'flip': 'random'},
            {'type': 'palm', 'dx': -1.1, 'dy': 1.1, 'scale': [2.5, 3.1], 'flip': 'random', 'chance': 0.8},
            {'type': 'coconuts', 'dx': 0.4, 'dy': 0.6, 'flip': 'random'},
            {'type': 'dry_tuft', 'dx': -0.5, 'dy': -0.6, 'jitter': 0.4},
            {'type': 'dry_tuft', 'dx': 0.9, 'dy': -0.4, 'jitter': 0.4, 'chance': 0.7},
        ],
    },
    'palm_3d': {
        'description': 'a palm with a crown of crossed planes over a billboard trunk: the crown has body from any side',
        'scale': [0.9, 1.15],
        'sprites': [
            {'type': 'palm_trunk', 'scale': 3.2},
            {'type': 'palm_crown', 'scale': 3.2, 'planes': 3, 'angle': [0, 60]},
        ],
    },
    'jungle_clump': {
        'description': 'a banana plant over monstera, ferns, bromeliads and the odd heliconia',
        'sprites': [
            {'type': 'banana_plant', 'scale': [1.4, 1.9], 'flip': 'random'},
            {'type': 'monstera', 'dx': 0.75, 'dy': 0.3, 'flip': 'random'},
            {'type': 'fern', 'dx': -0.65, 'dy': 0.4, 'jitter': 0.15},
            {'type': 'fern', 'dx': 0.25, 'dy': 0.85, 'jitter': 0.15, 'scale': [0.35, 0.5]},
            {'type': 'bromeliad', 'dx': -0.3, 'dy': -0.55, 'jitter': 0.1},
            {'type': 'heliconia', 'dx': 0.9, 'dy': -0.45, 'chance': 0.6, 'flip': 'random'},
        ],
    },
    'jungle_bush': {
        'description': 'a star of monstera with a billboard fern and heliconia in front: planes and billboards mixed',
        'sprites': [
            {'type': 'monstera', 'planes': 3, 'scale': [0.8, 1.05]},
            {'type': 'fern', 'planes': 0, 'dx': 0.35, 'dy': 0.35, 'scale': [0.4, 0.55]},
            {'type': 'heliconia', 'planes': 0, 'dx': -0.3, 'dy': 0.25, 'scale': [0.9, 1.2], 'chance': 0.7},
        ],
    },
    'fern_bed': {
        'description': 'a spread of ferns with mushrooms in the shade under them',
        'sprites': [
            {'type': 'fern', 'jitter': 0.2, 'scale': [0.4, 0.6]},
            {'type': 'fern', 'dx': 0.8, 'dy': 0.2, 'jitter': 0.25, 'scale': [0.35, 0.55]},
            {'type': 'fern', 'dx': -0.7, 'dy': 0.3, 'jitter': 0.25, 'scale': [0.35, 0.55]},
            {'type': 'fern', 'dx': 0.2, 'dy': -0.7, 'jitter': 0.25, 'scale': [0.3, 0.5]},
            {'type': 'fern', 'dx': -0.3, 'dy': 0.8, 'jitter': 0.25, 'scale': [0.3, 0.5], 'chance': 0.7},
            {'type': 'mushrooms', 'dx': 0.4, 'dy': 0.5, 'jitter': 0.2, 'chance': 0.6},
        ],
    },
    'ruined_columns': {
        'description': 'a standing Doric column and a broken one, fluted marble in 3D, fallen drums, rubble and dry grass',
        'objects': [
            {'type': 'column', 'material': 'marble', 'flutes': 20, 'doric': True, 'top': 0.8, 'radius': 0.24,
             'height': [2.6, 3.0], 'capital': 0.3, 'fill': 1.0},
            {'type': 'column', 'dx': 1.4, 'dy': 0.2, 'material': 'marble', 'flutes': 20, 'top': 0.8, 'radius': 0.24,
             'height': [1.4, 2.2], 'broken': [0.2, 0.3], 'fill': 1.0},
        ],
        'sprites': [
            {'type': 'column_drum', 'dx': 0.6, 'dy': 1.2, 'flip': 'random'},
            {'type': 'column_drum', 'dx': -0.9, 'dy': 0.9, 'flip': 'random', 'chance': 0.6},
            {'type': 'rubble', 'dx': 1.0, 'dy': 1.0, 'jitter': 0.2},
            {'type': 'dry_tuft', 'dx': -0.5, 'dy': 0.4, 'jitter': 0.3},
            {'type': 'dry_tuft', 'dx': 1.8, 'dy': 0.7, 'jitter': 0.3, 'chance': 0.7},
            {'type': 'poppies', 'dx': 0.2, 'dy': 0.8, 'jitter': 0.3, 'chance': 0.6},
        ],
    },
    'altar_fire': {
        'description': 'a low stone altar with a brazier burning on it',
        'map': ['A'],
        'legend': {'A': {'wall': 'limestone', 'h': 0.5, 'top': 'limestone'}},
        'sprites': [{'type': 'brazier', 'scale': 0.55}],
        'lights': [{'dx': 0, 'dy': 0, 'z': 1.1, 'radius': 4.5, 'color': [1.0, 0.62, 0.3], 'intensity': 1.4}],
    },
    'beach_hut': {
        'description': 'a bamboo hut with thatched eaves, a lit lattice window, its door (east at angle 0) between two torches',
        'map': ['hhhhh',
                'hiiih',
                'hiiid',
                'hiiih',
                'hhlhh'],
        'legend': {
            'h': {'wall': ['bamboo', 'thatch'], 'h': 1.5, 'top': 'thatch'},
            'l': {'wall': ['lattice', 'thatch'], 'h': 1.5, 'top': 'thatch', 'floor': 'boards', 'ceil': 'thatch'},
            'i': {'floor': 'boards', 'ceil': 'thatch'},
            'd': {'floor': 'boards', 'ceil': 'thatch'},
        },
        'sprites': [{'type': 'tiki_torch', 'dx': 3.0, 'dy': -0.8}, {'type': 'tiki_torch', 'dx': 3.0, 'dy': 0.8}],
        'lights': [{'dx': 0, 'dy': 0, 'z': 0.7, 'radius': 3.0, 'color': [1.0, 0.7, 0.4], 'intensity': 1.2},
                   {'dx': 3.0, 'dy': 0, 'z': 0.9, 'radius': 2.6, 'color': [1.0, 0.6, 0.3], 'intensity': 0.9}],
    },
    'tiki_torches': {
        'description': 'a pair of tiki torches either side of a way through, with their light',
        'sprites': [{'type': 'tiki_torch', 'dy': -0.9}, {'type': 'tiki_torch', 'dy': 0.9}],
        'lights': [{'dx': 0, 'dy': 0, 'z': 0.9, 'radius': 2.8, 'color': [1.0, 0.6, 0.3], 'intensity': 1.0}],
    },
    'street_lamp': {
        'description': 'a lamp post, its light, and a wet shine on the ground under it',
        'sprites': [{'type': 'lamp_post'}],
        'lights': [{'dx': 0, 'dy': 0, 'z': 1.45, 'radius': 4.6, 'color': [1.0, 0.86, 0.6], 'intensity': 1.45}],
        'decals': [{'tex': 'puddle_shine', 'dx': 0.3, 'dy': 0.5, 'size': 1.4, 'chance': 0.6}],
    },
    'graves': {
        'description': 'a few graves gone to grass, one leaning cross',
        'sprites': [
            {'type': 'gravestone', 'flip': 'random'},
            {'type': 'gravestone', 'dx': 1.1, 'dy': 0.1, 'jitter': 0.1, 'flip': 'random'},
            {'type': 'grave_cross', 'dx': -1.0, 'dy': 0.15, 'jitter': 0.1, 'flip': 'random'},
            {'type': 'grass_tuft', 'dx': 0.5, 'dy': 0.4, 'jitter': 0.3},
            {'type': 'grass_tuft', 'dx': -0.5, 'dy': 0.45, 'jitter': 0.3, 'chance': 0.7},
        ],
    },
    'shrine': {
        'description': 'a carved stela with candles burning at its foot',
        'sprites': [{'type': 'stela'}, {'type': 'candles', 'dx': 0.0, 'dy': 0.45}],
        'lights': [{'dx': 0, 'dy': 0.5, 'z': 0.3, 'radius': 2.4, 'color': [1.0, 0.7, 0.35], 'intensity': 1.0}],
    },
}


# ------------------------------------------------------------------ expansion

def _rot(dx, dy, a):
    c, s = math.cos(a), math.sin(a)
    return dx * c - dy * s, dx * s + dy * c


def _pick(v, rng):
    """A fixed value, or a random one from a [low, high] pair."""
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
        return rng.uniform(float(v[0]), float(v[1]))
    return v


def _fresh(state):
    """A map character nothing in the scene uses yet."""
    while True:
        ch = chr(state['next'])
        state['next'] += 1
        if ch not in state['used'] and not ch.isspace():
            state['used'].add(ch)
            return ch


def expand(scene, keep=()):
    """The scene with every prefab placement turned into its parts, its `time` of day into its sky,
    its sun or moon and its air (daylight.apply: the keys named in `keep` stay as they are), and
    every object into its panels (objects.expand) - in that order, so the hour reaches the lamps a
    prefab brings and the objects' lit windows and night marks. A scene with none of them comes
    back as it is - the same object - and an expanded one is never expanded twice."""
    return objects.expand(daylight.apply(_expand(scene), keep))


def _expand(scene):
    if not scene.get('prefabs'):
        return scene
    defs = {**PREFABS, **(scene.get('prefab_defs') or {})}
    out = dict(scene)
    out['map'] = [list(r) for r in scene['map']]
    out['legend'] = dict(scene.get('legend') or {})
    for key in ('sprites', 'lights', 'decals', 'scatter', 'objects'):
        out[key] = list(scene.get(key) or [])
    state = {'used': set(''.join(scene['map'])) | set(out['legend']), 'next': 0x100}
    for n, pl in enumerate(scene['prefabs']):
        _place(out, defs, pl, None, 0, state, n)
    out['map'] = [''.join(r) for r in out['map']]
    out.pop('prefabs')
    out.pop('prefab_defs', None)
    if not out['objects']:
        out.pop('objects')
    return out


def _place(out, defs, pl, parent, depth, state, n):
    """Lay one placement into `out`. `parent` is (x, y, angle, scale) of the prefab it sits in."""
    if depth > MAX_DEPTH:
        raise ValueError('prefabs nested more than %d deep - does one place itself?' % MAX_DEPTH)
    name = pl.get('type')
    if name not in defs:
        raise KeyError(f"unknown prefab {name!r}. Prefabs: {', '.join(sorted(defs))}")
    pf = defs[name]
    seed = pl.get('seed', n)
    rng = random.Random(f'{name}/{seed}/{depth}/{n}')
    if parent is None:
        x, y, a, sc = float(pl['x']), float(pl['y']), 0.0, 1.0
    else:
        ox, oy, a, sc = parent
        rx, ry = _rot(float(pl.get('dx', 0)) * sc, float(pl.get('dy', 0)) * sc, a)
        x, y = ox + rx, oy + ry
    a += math.radians(float(_pick(pl.get('angle', 0), rng)))
    sc *= float(_pick(pl.get('scale', 1.0), rng)) * float(_pick(pf.get('scale', 1.0), rng))
    remap, cell0, k = {}, None, 0
    if pf.get('map'):
        k = round(math.degrees(a) / 90.0) % 4      # a patch of map only turns in quarter turns,
        a = math.radians(90 * k)
        sc = 1.0                                     # and never scales: its parts stay on its cells
        cell0 = _stamp(out, pf, x, y, k, remap, state)
        x, y = cell0[0] + 0.5, cell0[1] + 0.5
    deg = math.degrees(a)
    pre = pl.get('id')

    def where(part):
        dx, dy = float(part.get('dx', 0)), float(part.get('dy', 0))
        j = float(part.get('jitter', 0))
        if j:
            dx, dy = dx + rng.uniform(-j, j), dy + rng.uniform(-j, j)
        rx, ry = _rot(dx * sc, dy * sc, a)
        return round(x + rx, 4), round(y + ry, 4)

    def keep(part):
        return 'chance' not in part or rng.random() < float(part['chance'])

    for part in pf.get('sprites', []):
        if not keep(part):
            continue
        sp = {key: v for key, v in part.items() if key not in ('dx', 'dy', 'jitter', 'chance')}
        sp['x'], sp['y'] = where(part)
        if 'scale' in part:
            sp['scale'] = round(float(_pick(part['scale'], rng)) * sc, 4)
        elif sc != 1.0:
            import assets                               # only for the default heights
            base = assets.sprite_defaults(part['type'], out.get('sprite_defs', {})).get('scale', 1.0)
            sp['scale'] = round(float(base) * sc, 4)
        if 'z' in part:
            sp['z'] = round(float(_pick(part['z'], rng)) * sc, 4)
        if part.get('flip') == 'random':
            sp['flip'] = rng.random() < 0.5
        if 'angle' in part:
            sp['angle'] = round((float(_pick(part['angle'], rng)) + deg) % 360, 2)
        if 'facing' in part:
            sp['facing'] = round((float(part['facing']) + deg) % 360, 2)
        if 'id' in part and pre:
            sp['id'] = f"{pre}.{part['id']}"
        out['sprites'].append(sp)
    for part in pf.get('lights', []):
        if not keep(part):
            continue
        if part.get('type', 'point') != 'point':
            raise ValueError(f'prefab {name!r}: only point lights belong in a prefab; put the sun in the scene')
        L = {key: v for key, v in part.items() if key not in ('dx', 'dy', 'jitter', 'chance')}
        L['x'], L['y'] = where(part)
        if 'radius' in L:
            L['radius'] = float(L['radius']) * sc
        out['lights'].append(L)
    for part in pf.get('decals', []):
        if not keep(part):
            continue
        dcl = {key: v for key, v in part.items() if key not in ('dx', 'dy', 'jitter', 'chance')}
        if dcl.get('surface', 'floor') == 'wall':
            if cell0 is None or 'cell' not in part:
                raise ValueError(f'prefab {name!r}: a wall decal needs the prefab to have a map, and a `cell` in it')
            dcl['cell'], dcl['face'], dcl['u'] = _wall_spot(pf, part, cell0, k)
        else:
            dcl['x'], dcl['y'] = where(part)
            dcl['size'] = float(part.get('size', 1.0)) * sc
        out['decals'].append(dcl)
    for part in pf.get('objects', []):                 # things built in 3D (objects.py), turned with it
        if not keep(part):
            continue
        ob = {key: v for key, v in part.items() if key not in ('dx', 'dy', 'jitter', 'chance')}
        ob['x'], ob['y'] = where(part)
        ob['angle'] = round((float(_pick(part.get('angle', 0), rng)) + deg) % 360, 2)
        for key in ('height', 'broken'):
            if key in part:
                ob[key] = round(float(_pick(part[key], rng)), 4)
        ob.setdefault('seed', rng.randrange(1 << 16))
        if sc != 1.0:
            ob['scale'] = round(float(part.get('scale', 1.0)) * sc, 4)
        out['objects'].append(ob)
    for part in pf.get('scatter', []):
        sct = dict(part)
        on = sct.get('on')
        if on is not None:
            sct['on'] = ''.join(remap.get(ch, ch) for ch in (on if isinstance(on, str) else ''.join(on)))
        sct['seed'] = int(sct.get('seed', 0)) + 1000 * (len(out['scatter']) + 1)
        out['scatter'].append(sct)
    for i, child in enumerate(pf.get('prefabs', [])):
        if keep(child):
            _place(out, defs, child, (x, y, a, sc), depth + 1, state, n * 100 + i)


def _stamp(out, pf, x, y, k, remap, state):
    """Write a prefab's map into the scene's, turned k quarter turns about its anchor cell, which
    lands on the cell holding (x, y). Returns that cell."""
    rows = pf['map']
    aw, ah = max(len(r) for r in rows), len(rows)
    ai, aj = pf.get('anchor', [aw // 2, ah // 2])
    cx, cy = int(math.floor(x)), int(math.floor(y))
    for ch, spec in (pf.get('legend') or {}).items():
        new = _fresh(state)
        remap[ch] = new
        out['legend'][new] = spec
    grid = out['map']
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == ' ':
                continue
            di, dj = _turn(i - ai, j - aj, k)
            X, Y = cx + di, cy + dj
            if 0 <= Y < len(grid):
                if X >= len(grid[Y]):
                    grid[Y].extend(' ' * (X + 1 - len(grid[Y])))
                if X >= 0:
                    grid[Y][X] = remap.get(ch, ch)
    return cx, cy


def _turn(di, dj, k):
    for _ in range(k):
        di, dj = -dj, di
    return di, dj


def _wall_spot(pf, part, cell0, k):
    """Where a wall decal of a prefab lands once its map is turned: cell, face and u."""
    rows = pf['map']
    aw, ah = max(len(r) for r in rows), len(rows)
    ai, aj = pf.get('anchor', [aw // 2, ah // 2])
    i, j = part['cell']
    di, dj = _turn(i - ai, j - aj, k)
    face = (FACES[part.get('face', 'south')] + 90 * k) % 360
    # u runs along +x on north and south faces and along +y on east and west ones; a turn can
    # reverse that direction, and then u counts from the other end
    along = (1, 0) if part.get('face', 'south') in ('north', 'south') else (0, 1)
    ax, ay = _turn(along[0], along[1], k)
    u = float(part.get('u', 0.5))
    if ax < 0 or ay < 0:
        u = 1.0 - u
    name = {v: n for n, v in FACES.items()}[face]
    return [cell0[0] + di, cell0[1] + dj], name, u

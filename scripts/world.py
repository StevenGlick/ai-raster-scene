"""The world a scene describes, as the renderer reads it: the map's characters turned into cells (walls
and their storeys, floors, ceilings, heights, drops and voids, doors, glass, facades), the prefabs
stamped into it, scattered props and fringes placed, decals laid, textures indexed - and the cameras
aimed (look_at). render.py draws a World; it re-exports everything here, so render.World still works.
"""
import json
import math

import numpy as np

import assets
import buildings
import prefabs

# ------------------------------------------------------------------ cameras

def find_sprite(scene, sid, cam=None):
    """The sprite with this `id`, from the scene (its prefabs included) or the shot's extra_sprites -
    or the wireframe with it."""
    scene = prefabs.expand(scene)
    cam = cam or {}
    for sp in (list(scene.get('sprites', [])) + list(cam.get('extra_sprites', []))
               + list(scene.get('wireframes', [])) + list(cam.get('extra_wireframes', []))):
        if sp.get('id') == sid:
            return sp
    return None


# How far the edge of solid ground drops into a void floor before the sky shows beneath it.
VOID_DEPTH = 2.5


def resolve_camera(scene, cam):
    """Fill in `angle` from a camera's `look_at` (a sprite id, [x, y] or [x, y, z]).

    Aiming by hand means working out atan2 in your head, which is easy to get wrong by tens of
    degrees. An [x, y, z] target also sets `pitch` so that height sits mid-frame.
    """
    tgt = cam.get('look_at')
    if tgt is None or 'x' not in cam or 'y' not in cam:
        return cam
    cam = dict(cam)
    if isinstance(tgt, str):
        sp = find_sprite(scene, tgt, cam)
        if sp is None:
            raise KeyError(f"look_at names sprite id {tgt!r}, but no sprite has that id")
        tx, ty, tz = float(sp['x']), float(sp['y']), None
    else:
        tx, ty = float(tgt[0]), float(tgt[1])
        tz = float(tgt[2]) if len(tgt) > 2 else None
    vx, vy = tx - float(cam['x']), ty - float(cam['y'])
    dist = math.hypot(vx, vy)
    if dist < 1e-6:
        return cam
    cam['angle'] = math.degrees(math.atan2(vy, vx)) % 360
    if tz is not None:
        W, H = scene.get('resolution', [320, 200])
        fov = math.radians(float(cam.get('fov', 66)))
        cam['pitch'] = (tz - float(cam.get('height', 0.5))) * (W / 2) / (math.tan(fov / 2) * dist * H)
    return cam


def merge_camera(scene, shot):
    """A shot over the scene camera, with look_at resolved. A shot that sets its own `angle`
    (and no look_at) is aimed by that angle, not by a look_at inherited from the camera."""
    base = dict(scene.get('camera') or {})
    if 'angle' in shot and 'look_at' not in shot:
        base.pop('look_at', None)
    return resolve_camera(scene, {**base, **shot})


def _seg_dist(px, py, x0, y0, x1, y1):
    vx, vy = x1 - x0, y1 - y0
    L = vx * vx + vy * vy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - x0) * vx + (py - y0) * vy) / L))
    return math.hypot(px - (x0 + t * vx), py - (y0 + t * vy))


# ------------------------------------------------------------------ scene loading

class World:
    def __init__(self, scene):
        scene = prefabs.expand(scene)       # prefabs become ordinary cells, sprites, lights and decals
        self.scene = scene
        rows = scene['map']
        self.mh = len(rows)
        self.mw = max(len(r) for r in rows)
        legend = scene['legend']
        default = scene.get('default', {'floor': 'concrete_floor'})
        self.ceil_h = float(scene.get('ceiling_height', 1.0))

        self.height = np.zeros((self.mh, self.mw), np.float32)
        self.wall_tid = np.full((self.mh, self.mw), -1, np.int32)
        self.floor_tid = np.full((self.mh, self.mw), -1, np.int32)
        self.ceil_tid = np.full((self.mh, self.mw), -1, np.int32)
        self.drop = np.zeros((self.mh, self.mw), np.float32)  # how far this floor sits below z=0
        self.reflect = np.zeros((self.mh, self.mw), np.float32)  # how mirror-like each floor is
        self.void = np.zeros((self.mh, self.mw), bool)           # no ground: the sky shows below
        self.glazed = np.zeros((self.mh, self.mw), bool)         # a roof the sun shines through
        self.side_tid = np.full((self.mh, self.mw), -1, np.int32)  # texture of a cell's sunken edge
        self.cliff = np.full((self.mh, self.mw), VOID_DEPTH, np.float32)  # how deep its edge drops into a void
        self.tex = []
        self.tex_key = []    # the material name each texture id came from
        self.tex_noise = []  # its relative surface-noise multiplier
        self.tex_alpha = []  # see-through mask (or None) per texture id
        self._tidx = {}
        self.see = np.zeros((self.mh, self.mw), bool)  # walls with see-through texels: fences, bars
        inherit = []
        self.stacks = {}  # (y, x) -> texture ids per storey, bottom to top
        self._fringes = {}  # (y, x) -> the fringe spec of a wall cell that has one
        self._facades = {}  # (y, x) -> the facade spec of a wall cell that has one

        for y, row in enumerate(rows):
            row = row.ljust(self.mw)
            for x, ch in enumerate(row):
                spec = legend.get(ch, default)
                if 'cliff' in spec:
                    self.cliff[y, x] = max(0.05, float(spec['cliff']))
                if 'wall' in spec:
                    self.height[y, x] = float(spec.get('h', 1.0))
                    stack = spec['wall'] if isinstance(spec['wall'], list) else [spec['wall']]
                    tids = [self.tid(t) for t in stack]
                    self.wall_tid[y, x] = tids[0]
                    if spec.get('side'):
                        self.side_tid[y, x] = self.tid(spec['side'])
                    if len(tids) > 1:
                        self.stacks[(y, x)] = tids
                    if spec.get('fringe'):
                        self._fringes[(y, x)] = spec['fringe']
                    if spec.get('facade'):
                        self._facades[(y, x)] = spec['facade']
                    if any(self.tex_alpha[t] is not None for t in tids):
                        # a fence or grille: the ground (and any roof) carries on underneath it
                        self.see[y, x] = True
                        if spec.get('floor'):
                            self.floor_tid[y, x] = self.tid(spec['floor'])
                        if spec.get('ceil'):
                            self.ceil_tid[y, x] = self.tid(spec['ceil'])
                        inherit.append((y, x, not spec.get('floor'), not spec.get('ceil')))
                    else:
                        self.floor_tid[y, x] = self.tid(spec.get('top', stack[-1]))
                        if spec.get('ceil'):  # an altar or a step under a roof: the roof is above it
                            self.ceil_tid[y, x] = self.tid(spec['ceil'])
                else:
                    floor = spec.get('floor', default.get('floor', 'concrete_floor'))
                    if spec.get('ceil'):
                        self.ceil_tid[y, x] = self.tid(spec['ceil'])
                        self.glazed[y, x] = bool(spec.get('glazed', False))
                    if spec.get('side'):
                        self.side_tid[y, x] = self.tid(spec['side'])
                    if floor == 'void':
                        # no ground at all: the sky carries on below the horizon, and the edge of
                        # the ground beside it drops VOID_DEPTH into it like a cliff
                        self.void[y, x] = True
                        self.drop[y, x] = VOID_DEPTH
                        continue
                    self.floor_tid[y, x] = self.tid(floor)
                    self.drop[y, x] = min(0.9, max(0.0, float(spec.get('drop', 0.0))))
                    self.reflect[y, x] = min(1.0, max(0.0, float(spec.get('reflect', assets.texture_reflect(floor)))))

        self._apply_heights(scene)
        for y, x, want_floor, want_ceil in inherit:
            self._inherit_surfaces(y, x, want_floor, want_ceil, default)
        self._roof_low_blocks()
        # rain-soaked: open ground under the sky darkens and turns mirror-like (roofed and void
        # cells stay dry)
        wet = min(1.0, max(0.0, float(scene.get('wet', 0) or 0)))
        outside = (self.height <= 0) & (self.ceil_tid < 0) & ~self.void
        self.wet = np.where(outside, wet, 0.0).astype(np.float32)
        self.reflect = np.clip(self.reflect + self.wet * 0.35, 0, 1).astype(np.float32)
        # what blocks light and hides what is behind it: see-through cells do neither
        self.solid_h = np.where(self.see, 0.0, self.height).astype(np.float32)

        self.floor_decals, self.ceil_decals, self.wall_decals = [], [], {}
        self.fringe_sprites = self._fringe(scene)
        self.fringe_sprites += self._facade(scene)
        grime = self._expand_scatter(scene)
        # contact shadows go first, so puddles, stains and the author's own decals sit on top
        self._load_decals(scene, self._contact_shadows(scene) + list(scene.get('decals', [])) + grime)

    def _apply_heights(self, scene):
        """`heights`: a digit layer over the map setting each wall cell's height in steps of
        `height_unit` (0.1 by default), so a flight of stairs is one string per row."""
        rows = scene.get('heights')
        if not rows:
            return
        unit = float(scene.get('height_unit', 0.1))
        for y, row in enumerate(rows[:self.mh]):
            for x, ch in enumerate(str(row)[:self.mw]):
                if ch in '123456789' and self.height[y, x] > 0:
                    self.height[y, x] = int(ch) * unit

    def _inherit_surfaces(self, y, x, want_floor, want_ceil, default):
        """A see-through cell borrows the floor (and roof) most common among its open neighbours,
        so a fence across a lawn stands on grass without the legend having to say so."""
        from collections import Counter
        floors, ceils = Counter(), Counter()
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.mh and 0 <= nx < self.mw and self.height[ny, nx] <= 0 and not self.void[ny, nx]:
                floors[int(self.floor_tid[ny, nx])] += 1
                ceils[int(self.ceil_tid[ny, nx])] += 1
        if want_floor:
            self.floor_tid[y, x] = (floors.most_common(1)[0][0] if floors
                                    else self.tid(default.get('floor', 'concrete_floor')))
        if want_ceil and ceils:
            self.ceil_tid[y, x] = ceils.most_common(1)[0][0]

    def _roof_low_blocks(self):
        """A block lower than the ceiling leaves the ceiling above it in view, so give it the roof
        of the room around it - spreading inward across a wide platform - or open sky outdoors."""
        from collections import Counter
        low = (self.height > 0) & (self.height < self.ceil_h - 1e-6) & ~self.see
        need = low & (self.ceil_tid < 0)
        for _ in range(self.mw + self.mh):
            changed = False
            for y, x in zip(*np.nonzero(need)):
                votes = Counter()
                for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    ny, nx = y + dy, x + dx
                    if (0 <= ny < self.mh and 0 <= nx < self.mw and not need[ny, nx]
                            and (self.height[ny, nx] <= 0 or low[ny, nx])):
                        votes[int(self.ceil_tid[ny, nx])] += 1
                if votes:
                    self.ceil_tid[y, x] = votes.most_common(1)[0][0]
                    need[y, x] = False
                    changed = True
            if not changed:
                break

    def base_z(self, x, y):
        """Height of the surface a sprite standing at (x, y) rests on: below z=0 in a sunken
        cell, on top of a block lower than a room wall, otherwise the floor."""
        cx, cy = int(math.floor(x)), int(math.floor(y))
        if not (0 <= cy < self.mh and 0 <= cx < self.mw):
            return 0.0
        h = float(self.height[cy, cx])
        if h > 0:
            return h if h < 0.95 and not self.see[cy, cx] else 0.0
        if self.void[cy, cx]:
            return 0.0   # nothing to stand on: `z` is simply the height (a whale in the sky)
        return -float(self.drop[cy, cx])

    def _load_decals(self, scene, decals):
        """Decals are stamps blended into a surface's albedo: puddles, stains, vines, cracks."""
        defs = scene.get('decal_defs', {})
        for d in decals:
            rgba, em = assets.get_decal(d['tex'], defs)
            if d.get('flip'):
                rgba, em = rgba[:, ::-1], em[:, ::-1]
            dh, dw = rgba.shape[:2]
            e = {'rgba': rgba, 'em': em, 'dw': dw, 'dh': dh,
                 'size': float(d.get('size', 1.0)),
                 'opacity': float(d.get('opacity', 1.0)),
                 'reflect': float(d.get('reflect', assets.DECAL_REFLECT.get(d['tex'], 0.0))),
                 'tint': np.array(d.get('tint', [1, 1, 1]), np.float32)}
            surf = d.get('surface', 'floor')
            if surf in ('floor', 'ceil', 'ceiling'):
                e['x'], e['y'] = float(d['x']), float(d['y'])
                cx, cy = int(math.floor(e['x'])), int(math.floor(e['y']))
                e['drop'] = float(self.drop[cy, cx]) if 0 <= cy < self.mh and 0 <= cx < self.mw else 0.0
                (self.floor_decals if surf == 'floor' else self.ceil_decals).append(e)
            else:
                cx, cy = (int(v) for v in d['cell'])
                e['u'] = float(d.get('u', 0.5))
                e['z'] = float(d.get('z', 0.5))
                self.wall_decals.setdefault((cy, cx, d.get('face', 'south')), []).append(e)

    # ---------------------------------------------------------------- scatter and grime

    def _grime(self, scene):
        """`grime` 0..1 is one dial for how neglected somewhere is.

        It turns up surface variation, multiplies scatter density, and stamps wear decals on
        walls and floors, so a dirty room needs one number rather than three sets of tuning.
        """
        g = scene.get('grime', 0)
        g = float(g.get('amount', 0)) if isinstance(g, dict) else float(g)
        return max(0.0, min(1.0, g))

    def _ground_open(self, x, y):
        """Open ground for fringes and facades: inside the map, and no wall a person could not
        step over (a kerb or a low step still counts as ground)."""
        return (0 <= x < self.mw and 0 <= y < self.mh and self.height[y, x] < 0.5
                and not self.void[y, x])

    def _face_runs(self, cells):
        """Straight runs of wall faces that look onto open ground, from cells {(y, x): spec}:
        each (spec, d, line, a, b) with d the way out ('n', 's', 'w' or 'e'), `line` the row
        (or column) of the walls and a..b the cells along it. Cells whose specs differ make
        separate runs."""
        groups = {}
        for (y, x), spec in cells.items():
            key = json.dumps({'set': spec} if isinstance(spec, str) else spec, sort_keys=True)
            for d, ox, oy in (('n', 0, -1), ('s', 0, 1), ('w', -1, 0), ('e', 1, 0)):
                if self._ground_open(x + ox, y + oy):
                    groups.setdefault((key, d, y if d in 'ns' else x), []).append(x if d in 'ns' else y)
        out = []
        for (key, d, line), poss in sorted(groups.items()):
            poss = sorted(set(poss))
            start = poss[0]
            for p, q in zip(poss, poss[1:] + [None]):
                if q != p + 1:
                    out.append((json.loads(key), d, line, start, p))
                    start = q
        return out

    def _run_ends(self, d, line, a, b, off):
        """Where a layer `off` out from a run of faces starts and ends along it, and what is at
        each end: it wraps round an outside corner, stops short in an inside one, and carries on
        off the edge of the map."""
        o = 1 if d in 'se' else -1
        lo, hi, kinds = float(a), float(b + 1), []
        for end, step in ((a - 1, -1), (b + 1, 1)):
            nx, ny = (end, line) if d in 'ns' else (line, end)
            dx_, dy_ = (end, line + o) if d in 'ns' else (line + o, end)
            if not (0 <= nx < self.mw and 0 <= ny < self.mh):
                adj, kind = 0.0, 'edge'
            elif self._ground_open(nx, ny):
                adj, kind = off, 'convex'
            elif not self._ground_open(dx_, dy_):
                adj, kind = -off, 'concave'
            else:
                adj, kind = 0.0, 'straight'
            if step < 0:
                lo -= adj
            else:
                hi += adj
            kinds.append(kind)
        return lo, hi, kinds[0], kinds[1]

    def _card(self, d, line, lo, hi, off, **fields):
        """A planar sprite lying along a run of faces, `off` out from them, from lo to hi."""
        o = 1 if d in 'se' else -1
        face = line + (1 if o > 0 else 0)
        mid, across = (lo + hi) / 2, face + o * off
        sp = {'x': mid if d in 'ns' else across, 'y': across if d in 'ns' else mid,
              'angle': 0.0 if d in 'ns' else 90.0, 'planes': 1, 'length': hi - lo, 'shadow': False}
        sp.update(fields)
        return sp

    def _cam_spots(self, scene):
        return [(cx, cy) for cx, cy, r in self._keep_clear(scene) if r == 1.0]

    def _fringe(self, scene):
        """Layered foliage cards standing in front of every face of a `fringe` wall that looks
        onto open ground.

        Each straight run of faces gets one long card per layer of its set, back to front: the
        densest just off the wall, the sparsest at the front, spread over `depth` (a cell by
        default). Each layer wraps round outside corners and is trimmed in inside ones, so it
        follows the wall's outline at its own distance, and a card that would pass through a
        camera is left out.
        """
        if not self._fringes:
            return []
        cams = self._cam_spots(scene)
        out = []
        for spec, d, line, a, b in self._face_runs(self._fringes):
            name = spec.get('set')
            if 'cards' in spec:
                cards = list(spec['cards'])
            elif name in assets.FRINGES:
                cards = list(assets.FRINGES[name])
            else:
                raise KeyError(f"unknown fringe set {name!r}. Sets: {', '.join(sorted(assets.FRINGES))}, "
                               f"or give \"cards\" (sprite names, back to front)")
            depth, hk, seed = float(spec.get('depth', 1.0)), float(spec.get('height', 1.0)), int(spec.get('seed', 0))
            for k, card in enumerate(cards):
                off = depth * (k + 0.5) / len(cards)
                lo, hi, _, _ = self._run_ends(d, line, a, b, off)
                if hi - lo < 0.15:
                    continue
                rng = np.random.default_rng([seed, 'nswe'.index(d), line + 1000, a + 1000, k])
                sp = self._card(d, line, lo, hi, off, type=card,
                                scale=float(assets.SPRITE_HEIGHT.get(card, 1.0)) * hk,
                                u0=float(rng.random()), flip=bool(rng.random() < 0.5))
                q = plane_quads(sp, np.zeros((1, 1, 4)))[0]
                if any(_seg_dist(cx, cy, *q[:4]) < 0.35 for cx, cy in cams):
                    continue
                out.append(sp)
        return out

    # layers of a facade, back to front: how far out from the wall's face each stands, as a
    # share of the facade's depth (the street line is 1.0)
    FACADE_LAYERS = (('room', 0.45), ('drape', 0.83), ('frame', 0.93), ('glass', 0.93), ('wall', 1.0))

    def _facade(self, scene):
        """Building fronts in layers, for wall cells with a `facade` (see buildings.py).

        Every straight run of faces onto open ground is cut into buildings of `widths` cells,
        each `storeys` units tall, and each building stands its layers - rooms, curtains, frames
        and glass, and the wall with its openings, the street line `depth` out from the walls -
        all spanning the same stretch so its windows line up. A building on an outside corner
        takes its look (colour, height, paint) from the corner, so both its faces match, and a
        building taller than its neighbour shows a side wall above it.
        """
        if not self._facades:
            return []
        out = []
        for spec, d, line, a, b in self._face_runs(self._facades):
            spec = {'style': spec['set']} if 'set' in spec and len(spec) == 1 else dict(spec)
            spec.setdefault('style', spec.pop('set', 'brick'))
            for st in spec['style'] if isinstance(spec['style'], list) else [spec['style']]:
                if st not in buildings.FACADE_STYLES:
                    raise KeyError(f"unknown facade style {st!r}. Styles: {', '.join(buildings.FACADE_STYLES)}")
            depth = float(spec.get('depth', 1.0))
            wmin, wmax = (int(v) for v in spec.get('widths', [3, 6]))
            hmin, hmax = (int(v) for v in spec.get('storeys', [3, 5]))
            seed = int(spec.get('seed', 0))
            lo, hi, kl, kh = self._run_ends(d, line, a, b, depth)
            o = 1 if d in 'se' else -1
            street = line + (1 if o > 0 else 0) + o * depth
            rng = np.random.default_rng([seed, 'nswe'.index(d), line + 1000, a + 1000])
            bounds, pos = [lo], lo
            while hi - pos > wmax:
                pos += int(rng.integers(wmin, wmax + 1))
                bounds.append(pos)
            if hi - pos < wmin and len(bounds) > 1:
                bounds.pop()
            bounds.append(hi)
            spans = list(zip(bounds[:-1], bounds[1:]))
            heights, looks = [], []
            western = any(buildings.FACADE_STYLES[st].get('western')
                          for st in (spec['style'] if isinstance(spec['style'], list) else [spec['style']]))
            names = buildings.street_names(np.random.default_rng([seed, 'nswe'.index(d), line + 1000, a + 1000, 5]),
                                           len(spans)) if western else None
            for i, (s0, s1) in enumerate(spans):
                # a corner building takes its look from the corner, the same from either face
                if (i == 0 and kl == 'convex') or (i == len(spans) - 1 and kh == 'convex'):
                    at = s0 if i == 0 and kl == 'convex' else s1
                    corner = (at, street) if d in 'ns' else (street, at)
                    look = int(round(corner[0] * 4)) * 7919 + int(round(corner[1] * 4)) * 104729 + seed * 31
                else:
                    look = int(rng.integers(1, 2 ** 31))
                storeys = int(np.random.default_rng(look % (2 ** 32)).integers(hmin, hmax + 1))
                heights.append(storeys)
                looks.append(look)
                params = dict(style=spec['style'], w=round(s1 - s0, 3), h=storeys, look=look,
                              seed=int(rng.integers(1, 2 ** 31)), lit=float(spec.get('lit', 0.35)))
                if 'shops' in spec:
                    params['shops'] = float(spec['shops'])
                corner = (i == 0 and kl == 'convex') or (i == len(spans) - 1 and kh == 'convex')
                if names and not corner:                  # a corner building's sign comes from its look, both faces
                    params['name'] = names[i]
                for layer, frac in self.FACADE_LAYERS:
                    fields = dict(type=buildings.layer_name(layer, **params), scale=float(storeys),
                                  flip=d in 'ne')                 # read left to right from the street
                    if layer == 'glass':
                        fields['glass'] = spec.get('glass', True)
                    if layer == 'wall':                   # as thick as the frames are set back in it
                        fields['reveal'] = depth * (1.0 - dict(self.FACADE_LAYERS)['frame']) + 0.004
                    out.append(self._card(d, line, s0, s1, depth * frac, **fields))
                # a village style stands a roof on the wall: a gable end in the wall's own plane, or the
                # slope of thatch or tiles set back behind the eave, so the wall's top hides its foot;
                # each overhangs the ends a little and stands a hair off its neighbour so they never fight
                roof = buildings.roof_of(spec['style'], look, s1 - s0)
                if roof:
                    kind, cover, rh, chim = roof
                    over = 0.0 if kind == 'front' else 0.1
                    off = depth + 0.05 if kind in ('gable', 'front') else depth - min(0.4, depth * 0.45)
                    out.append(self._card(d, line, s0 - over, s1 + over, off + 0.03 * (i % 2),
                                          type=buildings.layer_name('roof', style=spec['style'], look=look, kind=kind,
                                                                    cover=cover, chimney=chim,
                                                                    w=round(s1 - s0 + 2 * over, 3), h=rh,
                                                                    **({'name': params['name']} if 'name' in params else {})),
                                          scale=rh, z=float(storeys), flip=d in 'ne'))
                # a style with blade signs hangs one or two out over the street, square to the front
                look_style = buildings.FACADE_STYLES[buildings.pick_style(spec['style'], look)]
                if look_style.get('blades') and storeys >= 3:
                    brng = np.random.default_rng([look % (2 ** 31), 7])
                    for k in range(int(brng.integers(1, look_style['blades'] + 1))):
                        at = s0 + (s1 - s0) * brng.uniform(0.15, 0.85)
                        out_len, tall = 0.7, float(brng.uniform(1.0, 1.7))
                        z = float(brng.uniform(1.15, max(1.2, storeys - tall - 0.4)))
                        mid = street + o * out_len / 2
                        out.append({'type': buildings.layer_name('blade', style=spec['style'], look=look, seed=k,
                                                                 w=out_len, h=round(tall, 3)),
                                    'x': at if d in 'ns' else mid, 'y': mid if d in 'ns' else at,
                                    'angle': 90.0 if d in 'ns' else 0.0, 'planes': 1, 'length': out_len,
                                    'scale': tall, 'z': z, 'shadow': False, 'flip': d in 'nw'})
                # a western building's covered boardwalk: posts and fascia out at the edge of the walk,
                # as tall as the scene's ceiling, which roofs the walk's cells
                walk = float(spec.get('porch', look_style.get('porch', 0)))
                if walk > 0:
                    out.append(self._card(d, line, s0 + 0.01, s1 - 0.01, depth + walk - 0.05,
                                          type=buildings.layer_name('porch', style=spec['style'], look=look,
                                                                    w=round(s1 - s0 - 0.02, 3), h=round(self.ceil_h, 3)),
                                          scale=self.ceil_h, flip=d in 'ne'))
            # a taller building shows its side wall above a lower neighbour
            for i in range(len(spans) - 1):
                h0, h1 = heights[i], heights[i + 1]
                if h0 == h1:
                    continue
                look = looks[i if h0 > h1 else i + 1]
                at = spans[i][1]
                mid = line + (1 if o > 0 else 0) + o * depth / 2
                out.append({'type': buildings.layer_name('side', style=spec['style'], w=depth, h=abs(h0 - h1),
                                                         look=look),
                            'x': at if d in 'ns' else mid, 'y': mid if d in 'ns' else at,
                            'angle': 90.0 if d in 'ns' else 0.0, 'planes': 1, 'length': depth,
                            'scale': float(abs(h0 - h1)), 'z': float(min(h0, h1)), 'shadow': False})
        return out

    def _open_cells(self, chars=None):
        """Open (non-wall) cells, optionally restricted to a set of legend characters."""
        rows = self.scene['map']
        out = []
        for y in range(self.mh):
            row = rows[y].ljust(self.mw) if y < len(rows) else ' ' * self.mw
            for x in range(self.mw):
                if self.height[y, x] > 0 or self.floor_tid[y, x] < 0:
                    continue
                if chars is None or row[x] in chars:
                    out.append((x, y))
        return out

    def _clear_of_walls(self, x, y, cx, cy, margin):
        """Nudge a point away from any wall face of its cell, so props never clip into walls."""
        if margin <= 0:
            return x, y
        if cx > 0 and self.height[cy, cx - 1] > 0:
            x = max(x, cx + margin)
        if cx < self.mw - 1 and self.height[cy, cx + 1] > 0:
            x = min(x, cx + 1 - margin)
        if cy > 0 and self.height[cy - 1, cx] > 0:
            y = max(y, cy + margin)
        if cy < self.mh - 1 and self.height[cy + 1, cx] > 0:
            y = min(y, cy + 1 - margin)
        return x, y

    def _keep_clear(self, scene):
        """Places scatter must not bury: camera positions and any sprite an overlay anchors to."""
        out = []
        cam = scene.get('camera', {})
        for c in [cam] + list(scene.get('shots', [])):
            cc = {**cam, **c}
            if 'x' in cc and 'y' in cc:
                out.append((float(cc['x']), float(cc['y']), 1.0))
        for sp in scene.get('sprites', []):
            if 'id' in sp:
                out.append((float(sp['x']), float(sp['y']), 1.2))
        return out

    def _sight_lines(self, scene):
        """Camera-to-subject segments that tall scatter must not stand on: each shot's look_at
        target, and every sprite with an `id` that sits inside that shot's view."""
        out = []
        subjects = [sp for sp in scene.get('sprites', []) if 'id' in sp]
        for shot in (scene.get('shots') or [scene.get('camera') or {}]):
            c = merge_camera(scene, shot)
            if 'x' not in c or 'y' not in c:
                continue
            cx, cy = float(c['x']), float(c['y'])
            ang = math.radians(float(c.get('angle', 0)))
            half = math.radians(float(c.get('fov', 66))) / 2 + 0.1
            targets = []
            if isinstance(c.get('look_at'), (list, tuple)):
                targets.append((float(c['look_at'][0]), float(c['look_at'][1])))
            for sp in subjects:
                vx, vy = float(sp['x']) - cx, float(sp['y']) - cy
                off = (math.atan2(vy, vx) - ang + math.pi) % (2 * math.pi) - math.pi
                if 0.3 < math.hypot(vx, vy) < 14 and abs(off) <= half:
                    targets.append((float(sp['x']), float(sp['y'])))
            out += [(cx, cy, tx, ty) for tx, ty in targets]
        return out

    def _contact_shadows(self, scene):
        """A soft dark stamp under every prop and character standing on the floor, so nothing
        looks pasted on. `contact_shadows` sets the strength (0 turns them off); a sprite's own
        `"shadow"` overrides it, `false` for none."""
        strength = scene.get('contact_shadows', 0.55)
        strength = 0.0 if strength is False else 0.55 if strength is True else float(strength)
        defs = scene.get('sprite_defs', {})
        out = []
        for sp in list(scene.get('sprites', [])) + self.scatter_sprites:
            sp = {**assets.sprite_defaults(sp['type'], defs), **sp}
            own = sp.get('shadow')
            s = strength if own is None or own is True else 0.0 if own is False else float(own)
            if s <= 0 or float(sp.get('z', 0)) > 0.05 or sp['type'] in assets.NO_CONTACT_SHADOW:
                continue
            if sp.get('fullbright') or sp.get('blend', 'alpha') != 'alpha' or float(sp.get('opacity', 1)) < 1:
                continue  # ghosts, glows and light sources cast nothing
            cx, cy = int(math.floor(float(sp['x']))), int(math.floor(float(sp['y'])))
            if not (0 <= cy < self.mh and 0 <= cx < self.mw) or self.height[cy, cx] > 0 or self.void[cy, cx]:
                continue  # standing on top of a block, or over a void: no floor to shade
            width = float(sp.get('scale', 1.0)) * assets.sprite_aspect(sp['type'], defs) * float(sp.get('stretch', 1.0))
            out.append({'tex': 'contact_shadow', 'surface': 'floor', 'x': float(sp['x']), 'y': float(sp['y']),
                        # wider than the prop: half the disc hides behind its feet, and the
                        # visible half is foreshortened to a few rows at a grazing angle
                        'size': min(max(width * 1.25 + 0.12, 0.3), 1.8), 'opacity': min(1.0, s)})
        return out

    def _scatter_points(self, cells, count, rng, clump, margin, keep=()):
        """Pick `count` positions over `cells`, weighted by the shared noise field.

        Uniform random scatter reads as machine-made: everything evenly spaced, no bare patches.
        Weighting cell choice by smooth noise gives drifts and clearings for free, and a gaussian
        jitter inside the chosen cell keeps items off the grid lines.
        """
        if not cells or count <= 0:
            return []
        field = noise_field()
        cx = np.array([c[0] for c in cells], np.float64) + 0.5
        cy = np.array([c[1] for c in cells], np.float64) + 0.5
        w = sample_noise(field, cx / SCATTER_PERIOD, cy / SCATTER_PERIOD).astype(np.float64)
        w = np.clip(w, 0.02, 1.0) ** max(0.0, clump) if clump > 0 else np.ones_like(w)
        w /= w.sum()
        picks = rng.choice(len(cells), size=count, p=w)
        out = []
        for i in picks:
            gx, gy = cells[i]
            # gaussian jitter about the cell centre, clipped so it stays in the cell
            jx = float(np.clip(rng.normal(0.5, 0.21), 0.08, 0.92))
            jy = float(np.clip(rng.normal(0.5, 0.21), 0.08, 0.92))
            x, y = self._clear_of_walls(gx + jx, gy + jy, gx, gy, margin)
            if any((x - kx) ** 2 + (y - ky) ** 2 < kr * kr for kx, ky, kr in keep):
                continue  # never pile debris on a camera or in front of a speaking character
            out.append((x, y))
        return out

    def _expand_scatter(self, scene):
        """Turn `scatter` specs (and `grime`) into real sprites and decals, once, at load."""
        self.scatter_sprites = []
        grime = self._grime(scene)
        base_seed = int(scene.get('seed', 0))
        keep = self._keep_clear(scene)
        sight = self._sight_lines(scene)
        specs = list(scene.get('scatter', []))
        if grime > 0 and scene.get('grime_debris', True):
            specs.append({'of': 'wreckage', 'density': 0.05 * grime, 'sizes': ['tiny', 'small'],
                          'seed': 991, '_auto': True})

        for n, spec in enumerate(specs):
            rng = np.random.default_rng(base_seed * 7919 + int(spec.get('seed', n)) * 104729 + 13)
            cells = self._open_cells(spec.get('on'))
            density = float(spec.get('density', 0.35)) * (1.0 + 2.0 * grime)
            count = int(round(density * len(cells)))
            if count <= 0:
                continue
            defs = scene.get('sprite_defs', {})
            items = assets.debris_items(spec.get('of', 'stones'))
            for name in sorted(set(items)):
                try:
                    assets.get_sprite(name, defs)
                except KeyError:
                    raise KeyError(f"scatter 'of' names {name!r}, which is neither a debris set "
                                   f"({', '.join(sorted(assets.DEBRIS_SETS))}) nor a built-in or "
                                   f"sprite_defs sprite") from None
            sizes = spec.get('sizes') or assets.SIZE_WEIGHTS
            if isinstance(sizes, dict):
                names, weights = list(sizes), np.array([float(v) for v in sizes.values()])
            else:
                names, weights = list(sizes), np.ones(len(sizes))
            unknown = [s for s in names if s not in assets.SIZE_CLASSES]
            if unknown:
                raise KeyError(f"scatter 'sizes' has unknown class(es) {unknown}; "
                               f"classes are {', '.join(assets.SIZE_CLASSES)}")
            weights = weights / weights.sum()
            margin = float(spec.get('margin', 0.22))
            pts = self._scatter_points(cells, count, rng, float(spec.get('clump', 1.4)), margin,
                                       keep)
            for (x, y) in pts:
                name = items[int(rng.integers(len(items)))]
                cls = names[int(rng.choice(len(names), p=weights))]
                scale = assets.size_scale(name, cls, defs)
                # A keep-clear radius alone is not enough: a `huge` boulder is over a unit wide,
                # so it can sit outside the radius and still fill the frame. Grow the exclusion
                # by the item's own half-width.
                half = 0.5 * scale * assets.sprite_aspect(name, defs)
                if any((x - kx) ** 2 + (y - ky) ** 2 < (kr + half) ** 2 for kx, ky, kr in keep):
                    continue
                # low clutter between camera and subject reads as ground; anything taller blocks it
                if scale > 0.22 and any(_seg_dist(x, y, *s) < 0.28 + half for s in sight):
                    continue
                sp = {'x': round(float(x), 3), 'y': round(float(y), 3), 'type': name,
                      'scale': round(scale, 4)}
                if rng.random() < 0.5:
                    sp['flip'] = True
                self.scatter_sprites.append(sp)

        return self._grime_decals(scene, grime)

    def _grime_decals(self, scene, grime):
        """Wear stamped on visible wall faces and floors, scaled by `grime`."""
        if grime <= 0 or not scene.get('grime_decals', True):
            return []
        rng = np.random.default_rng(int(scene.get('seed', 0)) * 7919 + 7717)
        out = []
        faces = []
        for y in range(self.mh):
            for x in range(self.mw):
                if self.height[y, x] <= 0 or self.see[y, x]:
                    continue
                for face, (dx, dy) in (('south', (0, 1)), ('north', (0, -1)),
                                       ('east', (1, 0)), ('west', (-1, 0))):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.mw and 0 <= ny < self.mh \
                            and self.height[ny, nx] <= 0 and self.floor_tid[ny, nx] >= 0:
                        faces.append((x, y, face))
        rng.shuffle(faces)
        for (x, y, face) in faces[:int(round(len(faces) * 0.35 * grime))]:
            tex = assets.GRIME_WALL_DECALS[int(rng.integers(len(assets.GRIME_WALL_DECALS)))]
            high = tex in ('leak', 'vines')
            u = float(rng.uniform(0.25, 0.75))
            z = float(rng.uniform(0.6, 0.9) if high else rng.uniform(0.2, 0.7))
            size = round(float(rng.uniform(0.4, 0.9)), 3)
            opacity = float(rng.uniform(0.35, 0.8))
            # a wall decal is clipped to its own face, so one that overhangs the cell edge ends
            # in a hard vertical cut: slide it back inside (draw order unchanged, so seeds hold)
            u = min(max(u, size / 2), 1 - size / 2)
            out.append({'tex': tex, 'surface': 'wall', 'cell': [x, y], 'face': face,
                        'u': u, 'z': round(z, 3), 'size': size, 'opacity': round(opacity, 3)})
        cells = self._open_cells()
        for (x, y) in self._scatter_points(cells, int(round(len(cells) * 0.10 * grime)),
                                           rng, 1.4, 0.3, self._keep_clear(scene)):
            tex = assets.GRIME_FLOOR_DECALS[int(rng.integers(len(assets.GRIME_FLOOR_DECALS)))]
            out.append({'tex': tex, 'surface': 'floor', 'x': round(float(x), 3),
                        'y': round(float(y), 3),
                        'size': round(float(rng.uniform(0.7, 2.0)), 3),
                        'opacity': round(float(rng.uniform(0.3, 0.7)), 3)})
        return out

    def tid(self, spec):
        key = json.dumps(spec, sort_keys=True)
        if key not in self._tidx:
            rgb, em = assets.get_texture(spec)
            self._tidx[key] = len(self.tex)
            self.tex.append((rgb, em))
            self.tex_key.append(assets.texture_key(spec))
            self.tex_noise.append(assets.texture_noise(spec))
            self.tex_alpha.append(assets.get_alpha(spec))
        return self._tidx[key]


# ------------------------------------------------------------------ planar sprites

def plane_quads(sp, rgba):
    """The vertical quads a planar sprite stands as, each (x0, y0, x1, y1, repeats).

    `planes` 1 is a single card across `angle`; 2 crosses two at right angles; 3 is a star of
    three 60 degrees apart, dividing the ground round the sprite into sixths. Without an
    `angle` each sprite takes one from its position, so a bed of ferns is not all aligned.
    A card with a `length` repeats its image along it, every image-width.
    """
    th, tw = rgba.shape[:2]
    x, y = float(sp['x']), float(sp['y'])
    width = float(sp.get('scale', 1.0)) * tw / th * float(sp.get('stretch', 1.0))
    n = max(1, min(3, int(sp.get('planes', 1))))
    length = float(sp.get('length', width))
    a0 = math.radians(float(sp['angle']) if 'angle' in sp else (x * 137.508 + y * 61.803) % 180.0)
    out = []
    for k in range(n):
        a = a0 + k * math.pi / n
        hx, hy = math.cos(a) * length / 2, math.sin(a) * length / 2
        out.append((x - hx, y - hy, x + hx, y + hy, length / max(width, 1e-6)))
    return out


# ------------------------------------------------------------------ the noise field

_NOISE_FIELD = None
SCATTER_PERIOD = 9.0  # world units a scatter drift spans; wider than the surface octaves


def noise_field(size=256):
    """Tileable 0..1 value noise, built once and shared by every surface."""
    global _NOISE_FIELD
    if _NOISE_FIELD is None:
        n = assets.fbm(size, np.random.default_rng(20250115), base=4, octaves=5)
        lo, hi = np.percentile(n, 2), np.percentile(n, 98)
        _NOISE_FIELD = np.clip((n - lo) / max(hi - lo, 1e-6), 0, 1).astype(np.float32)
    return _NOISE_FIELD


def sample_noise(field, u, v):
    """Wrapping nearest lookup. u and v are counted in field periods, not pixels."""
    n = field.shape[0]
    return field[(v * n).astype(np.int32) % n, (u * n).astype(np.int32) % n]

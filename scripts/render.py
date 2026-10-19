#!/usr/bin/env python3
"""ai-raster-scene renderer: 90s-style first-person views from a JSON scene file.

A 2.5D grid raycaster in the Wolfenstein/Doom lineage with:
  - textured walls of any height (tall buildings seen over short walls, multi-hit rays)
  - textured floors and ceilings per cell, open-sky cells with a panorama sky
  - billboard sprites with per-pixel depth testing
  - coloured point lights baked into a shadowed lightmap, ambient light, light banding
  - emissive texels (lit windows, lamps, glowing runes), a player flashlight
  - distance fog, 256-colour palette quantisation with ordered (Bayer) dithering

Usage:
  python render.py scene.json -o out.png            # render the camera (or every shot)
  python render.py scene.json -o out.png --map      # also write a top-down layout check
  python render.py scene.json -o out.png --sheet    # tile all shots into one contact sheet
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assets  # noqa: E402
import gui  # noqa: E402
import icons  # noqa: E402
import post  # noqa: E402

T = assets.T


# ------------------------------------------------------------------ scene loading

class World:
    def __init__(self, scene):
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
        self.tex = []
        self.tex_key = []    # the material name each texture id came from
        self.tex_noise = []  # its relative surface-noise multiplier
        self._tidx = {}
        self.stacks = {}  # (y, x) -> texture ids per storey, bottom to top

        for y, row in enumerate(rows):
            row = row.ljust(self.mw)
            for x, ch in enumerate(row):
                spec = legend.get(ch, default)
                if 'wall' in spec:
                    self.height[y, x] = float(spec.get('h', 1.0))
                    stack = spec['wall'] if isinstance(spec['wall'], list) else [spec['wall']]
                    tids = [self.tid(t) for t in stack]
                    self.wall_tid[y, x] = tids[0]
                    if len(tids) > 1:
                        self.stacks[(y, x)] = tids
                    self.floor_tid[y, x] = self.tid(spec.get('top', stack[-1]))
                else:
                    self.floor_tid[y, x] = self.tid(spec.get('floor', default.get('floor', 'concrete_floor')))
                    if spec.get('ceil'):
                        self.ceil_tid[y, x] = self.tid(spec['ceil'])
                    self.drop[y, x] = min(0.9, max(0.0, float(spec.get('drop', 0.0))))

        self.floor_decals, self.ceil_decals, self.wall_decals = [], [], {}
        self._load_decals(scene, list(scene.get('decals', [])) + self._expand_scatter(scene))

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
                if self.height[y, x] <= 0:
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
        return self._tidx[key]


# ------------------------------------------------------------------ lighting

def build_lightmap(world, lights, res=8):
    """Returns dynamic light (mh*res, mw*res, 3) from point lights with grid shadows."""
    H, W = world.mh * res, world.mw * res
    lm = np.zeros((H, W, 3), np.float32)
    if not lights:
        return lm, res
    sy, sx = np.mgrid[0:H, 0:W]
    px = (sx.ravel() + 0.5) / res
    py = (sy.ravel() + 0.5) / res
    for L in lights:
        lx, ly = float(L['x']), float(L['y'])
        lz = float(L.get('z', 1.2))
        r = float(L.get('radius', 4.0))
        inten = float(L.get('intensity', 1.0))
        c = np.array(L.get('color', [1.0, 0.85, 0.6]), np.float32)
        dx, dy = lx - px, ly - py
        d = np.sqrt(dx * dx + dy * dy)
        near = d < r
        idx = np.nonzero(near)[0]
        if idx.size == 0:
            continue
        f = np.clip(1 - d[idx] / r, 0, 1) ** 2 * inten
        if L.get('shadows', True):
            block_h = min(lz, 0.95)
            steps = int(min(120, max(8, r * 12)))
            vis = np.ones(idx.size, bool)
            ix, iy = px[idx], py[idx]
            ddx, ddy = dx[idx], dy[idx]
            own_x, own_y = np.floor(ix).astype(int), np.floor(iy).astype(int)
            lcx, lcy = int(math.floor(lx)), int(math.floor(ly))
            for t in np.linspace(0.02, 0.98, steps):
                qx = np.floor(ix + ddx * t).astype(int)
                qy = np.floor(iy + ddy * t).astype(int)
                inb = (qx >= 0) & (qy >= 0) & (qx < world.mw) & (qy < world.mh)
                qxc, qyc = np.clip(qx, 0, world.mw - 1), np.clip(qy, 0, world.mh - 1)
                hb = world.height[qyc, qxc]
                skip = ((qx == own_x) & (qy == own_y)) | ((qx == lcx) & (qy == lcy))
                vis &= ~(inb & (hb >= block_h) & ~skip)
            f = f * vis
        flat = lm.reshape(-1, 3)
        flat[idx] += f[:, None] * c[None, :]
    return lm, res


def sample_lm(lm, res, x, y):
    """Bilinear lightmap lookup for arrays of world coordinates."""
    H, W = lm.shape[:2]
    fx = np.clip(x * res - 0.5, 0, W - 1.001)
    fy = np.clip(y * res - 0.5, 0, H - 1.001)
    x0, y0 = fx.astype(int), fy.astype(int)
    tx, ty = (fx - x0)[..., None], (fy - y0)[..., None]
    a = lm[y0, x0]; b = lm[y0, x0 + 1]; c = lm[y0 + 1, x0]; d = lm[y0 + 1, x0 + 1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def height_falloff(z):
    """Point lights sit near head height; tall walls fade into the dark above them."""
    return 1.0 / (1.0 + 0.7 * np.maximum(0, z - 1.4) ** 1.5)


# ------------------------------------------------------------------ surface variation

_NOISE_FIELD = None
COARSE_PERIOD = 6.3   # world units: varies cell to cell
FINE_PERIOD = 0.43    # sub-cell, so a 1-unit wall gets a few cycles and mottles instead of
                      # streaking vertically; also never lines up with the 1-unit texture tiling
SCATTER_PERIOD = 9.0  # world units a scatter drift spans; wider than the surface octaves
NOISE_TYPICAL = 0.27  # mean |value| of the two-octave blend, measured; divided out so that
                      # `amount` is the typical brightness swing rather than a rare peak
SURFACE_NOISE_DEFAULT = 0.10  # typical brightness swing, before each material scales it by its
                              # assets.TEXTURE_NOISE factor. "surface_noise": 0 disables it


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


def soft_swing(x, knee=0.5, limit=0.9):
    """Pass brightness swings below `knee` through unchanged and ease larger ones toward ±`limit`.

    amount x variation is unbounded: a rough material under heavy grime (cobble at grime 1 asks
    for swings near +/-2) would otherwise drive the albedo multiplier below zero and print black
    speckles. tanh keeps the slope continuous at the knee, so there is no visible seam between
    the untouched and the compressed range.
    """
    x = np.asarray(x, np.float32)
    a = np.abs(x)
    over = a > knee
    if not over.any():
        return x
    out = x.copy()
    span = limit - knee
    out[over] = np.sign(x[over]) * (knee + span * np.tanh((a[over] - knee) / span))
    return out


# ------------------------------------------------------------------ renderer

class Renderer:
    def __init__(self, world, scene):
        self.w = world
        self.s = scene
        self.W, self.H = scene.get('resolution', [320, 200])
        self.ambient = np.array(scene.get('ambient', [0.18, 0.18, 0.22]), np.float32)
        self.levels = int(scene.get('light_levels', 24))
        fog = scene.get('fog')
        self.fog_c = np.array(fog['color'], np.float32) if fog else None
        self.fog_d = float(fog.get('density', 0.1)) if fog else 0.0
        lights = list(scene.get('lights', []))
        for sp in scene.get('sprites', []):
            sp = {**assets.sprite_defaults(sp['type'], scene.get('sprite_defs', {})), **sp}
            if sp.get('light'):
                L = {'x': sp['x'], 'y': sp['y'], 'z': float(sp.get('z', 0)) + 0.2, 'shadows': True}
                L.update(sp['light'] if isinstance(sp['light'], dict) else {})
                lights.append(L)
        self.lm, self.lres = build_lightmap(world, lights, scene.get('lightmap_res', 8))
        self.overbright = float(scene.get('overbright', 1.0))
        sn = scene.get('surface_noise', SURFACE_NOISE_DEFAULT)
        by_texture = {}
        if isinstance(sn, dict):
            self.sn_amount = float(sn.get('amount', SURFACE_NOISE_DEFAULT))
            self.sn_scale = float(sn.get('scale', 1.0))
            by_texture = sn.get('by_texture', {}) or {}
        else:
            self.sn_amount, self.sn_scale = float(sn), 1.0
        self.sn_amount *= 1.0 + 1.5 * world._grime(scene)  # neglect shows on the surfaces too
        # Resolve one absolute amount per texture id: the scene amount scaled by the material's
        # own appetite for variation, unless the scene names that material explicitly.
        self.tex_amount = np.array(
            [float(by_texture[k]) if k in by_texture else self.sn_amount * m
             for k, m in zip(world.tex_key, world.tex_noise)], np.float32)
        self.sn = noise_field() if float(np.abs(self.tex_amount).max(initial=0.0)) > 1e-4 else None

    def surface_variation(self, u, v, key=0.0):
        """Signed ~[-1, 1] variation across one surface, anchored in world space.

        (u, v) are coordinates *on the surface* - (x, y) for floors and ceilings, (along, height)
        for walls - so the pattern sits still as the camera moves and stays continuous along a
        wall instead of breaking at cell edges. `key` separates surfaces that share coordinates
        (floor vs ceiling, the two wall orientations, each wall plane).
        """
        f, s, o = self.sn, self.sn_scale, key * 0.613
        coarse = 2 * sample_noise(f, (u + o) / (COARSE_PERIOD * s), (v + o) / (COARSE_PERIOD * s)) - 1
        fine = 2 * sample_noise(f, (u - o) / (FINE_PERIOD * s), (v - o) / (FINE_PERIOD * s)) - 1
        # Even weighting: leaning on the coarse octave makes a 1-unit-tall wall see mostly a
        # horizontal gradient, which reads as vertical banding once the amplitude is turned up.
        # Dividing by the blend's own typical magnitude makes `amount` mean what it says.
        return np.clip((0.5 * coarse + 0.5 * fine) / NOISE_TYPICAL, -2.6, 2.6)

    # --- shading helpers
    def shade(self, albedo, dyn, z, dist, em, flash):
        light = self.ambient[None, :] + dyn * height_falloff(z)[..., None] + flash
        light = light * self.overbright
        if self.levels > 0:
            light = np.floor(light * self.levels + 0.5) / self.levels
        out = albedo * light
        if em is not None:
            e = em[..., None]
            out = out * (1 - e) + albedo * e * 1.15
        if self.fog_c is not None:
            k = (1 - np.exp(-self.fog_d * dist))[..., None]
            out = out * (1 - k) + self.fog_c[None, :] * k
        return out

    def render(self, cam):
        """Render one camera: 3D pass (optionally supersampled), then UI overlays at native res."""
        ss = int(cam.get('supersample', self.s.get('supersample', 1)))
        bw, bh = self.W, self.H
        self.W, self.H = bw * ss, bh * ss
        try:
            img = self._render3d(cam)
        finally:
            self.W, self.H = bw, bh
        if ss > 1:
            img = img.reshape(bh, ss, bw, ss, 3).mean(axis=(1, 3))
            for a in self.anchors.values():
                for k in ('x', 'top', 'w', 'h'):
                    a[k] /= ss
        overlays = list(self.s.get('overlays', [])) + list(cam.get('overlays', []))
        effects = post.expand(list(self.s.get('post', [])) + list(cam.get('post', [])))
        if cam.get('scanlines', self.s.get('scanlines')) and not any(e['fx'] in ('scanlines', 'crt') for e in effects):
            effects.append({'fx': 'scanlines'})
        H, W = img.shape[:2]
        ctx = gui.Ctx(Image.new('RGBA', (W, H), (0, 0, 0, 0)), self.s, self.anchors, cam, self.w, self.camera_light(cam))
        img = gui.draw_world_layer(img, overlays, ctx)
        img = post.apply_world(img, effects, {'seed': int(self.s.get('seed', 0)) + int(cam.get('seed', 0))})
        img = gui.draw_ui_layer(img, overlays, ctx)
        self.last_effects = effects
        return np.clip(img, 0, 1)

    def camera_light(self, cam):
        """Light falling on things held at the camera (viewmodels): ambient + lightmap + flashlight spill."""
        dyn = sample_lm(self.lm, self.lres, np.array([float(cam['x'])]), np.array([float(cam['y'])]))[0]
        light = self.ambient + dyn * 0.6
        if cam.get('flashlight', self.s.get('flashlight')):
            light = light + 0.25
        # a floor keeps held items readable in near-darkness, the cap stops held lamps blowing them out
        return np.clip(light * self.overbright, 0.22, 1.0).astype(np.float32)

    def _blend_plane_decal(self, alb, emv, wx, wy, d, valid, dcl):
        """Stamp one floor/ceiling decal into a surface pass's albedo."""
        sw = dcl['size']
        sh = sw * dcl['dh'] / dcl['dw']
        x0, y0 = dcl['x'] - sw / 2, dcl['y'] - sh / 2
        # a plane's distance is constant per row, so only a band of rows can touch the decal
        rad = 0.5 * math.hypot(sw, sh)
        ctr = math.hypot(dcl['x'] - self._px, dcl['y'] - self._py)
        band = np.nonzero((d >= ctr - rad) & (d <= ctr + rad))[0]
        if band.size == 0:
            return
        r0, r1 = int(band[0]), int(band[-1]) + 1
        sx, sy = wx[r0:r1], wy[r0:r1]
        m = (sx >= x0) & (sx <= x0 + sw) & (sy >= y0) & (sy <= y0 + sh) & valid[r0:r1]
        if not m.any():
            return
        du = ((sx[m] - x0) / sw * dcl['dw']).astype(int).clip(0, dcl['dw'] - 1)
        dv = ((sy[m] - y0) / sh * dcl['dh']).astype(int).clip(0, dcl['dh'] - 1)
        tex = dcl['rgba'][dv, du]
        a = (tex[:, 3] * dcl['opacity'])[:, None]
        sub = alb[r0:r1]
        sub[m] = sub[m] * (1 - a) + tex[:, :3] * dcl['tint'][None, :] * a
        de = dcl['em'][dv, du]
        if de.any():
            sube = emv[r0:r1]
            sube[m] = np.maximum(sube[m], de * (a[:, 0] > 0.4))

    def _blend_wall_decals(self, alb, e, decals, uf_raw, z):
        """Stamp wall decals into one column's albedo. Returns the (possibly created) emissive array."""
        for dcl in decals:
            halfw = dcl['size'] / 2
            off = uf_raw - dcl['u']
            if abs(off) > halfw:
                continue
            halfh = (dcl['size'] * dcl['dh'] / dcl['dw']) / 2
            m = np.abs(z - dcl['z']) <= halfh
            if not m.any():
                continue
            dui = min(dcl['dw'] - 1, max(0, int((off + halfw) / (2 * halfw) * dcl['dw'])))
            dvi = (((dcl['z'] + halfh) - z[m]) / (2 * halfh) * dcl['dh']).astype(int).clip(0, dcl['dh'] - 1)
            tex = dcl['rgba'][dvi, dui]
            a = (tex[:, 3] * dcl['opacity'])[:, None]
            alb[m] = alb[m] * (1 - a) + tex[:, :3] * dcl['tint'][None, :] * a
            de = dcl['em'][dvi, dui]
            if de.any():
                if e is None:
                    e = np.zeros(len(z), np.float32)
                e[m] = np.maximum(e[m], de * (a[:, 0] > 0.4))
        return e

    def _render3d(self, cam):
        W, H = self.W, self.H
        w = self.w
        px, py = float(cam['x']), float(cam['y'])
        self._px, self._py = px, py
        ang = math.radians(float(cam.get('angle', 0)))
        fov = math.radians(float(cam.get('fov', 66)))
        camz = float(cam.get('height', 0.5))
        horizon = H / 2 + float(cam.get('pitch', 0)) * H
        proj = (W / 2) / math.tan(fov / 2)
        dx, dy = math.cos(ang), math.sin(ang)
        pl = math.tan(fov / 2)
        plx, ply = -dy * pl, dx * pl
        cx = 2 * (np.arange(W) + 0.5) / W - 1
        rdx = (dx + plx * cx).astype(np.float64)
        rdy = (dy + ply * cx).astype(np.float64)
        rlen = np.sqrt(rdx ** 2 + rdy ** 2)

        img = np.zeros((H, W, 3), np.float32)
        depth = np.full((H, W), np.inf, np.float32)

        # flashlight cone in screen space
        fl = cam.get('flashlight', self.s.get('flashlight'))
        if fl is True:
            fl = {}
        if fl is not None and fl is not False:
            yy, xx = np.mgrid[0:H, 0:W]
            rr = np.hypot((xx - W / 2) / (W / 2), (yy - horizon) / (W / 2)) / float(fl.get('radius', 0.35))
            cone = np.clip(1 - rr ** 2, 0, 1) ** 1.2 * float(fl.get('intensity', 1.2))
            cone += np.clip(1 - rr / 2.2, 0, 1) * 0.12 * float(fl.get('intensity', 1.2))
            fl_col = np.array(fl.get('color', [1.0, 0.95, 0.8]), np.float32)
            fl_range = float(fl.get('range', 5.0))
        else:
            cone = None

        def flash(rows, cols, dist):
            if cone is None:
                return 0.0
            return (cone[rows, cols] / (1 + (dist / fl_range) ** 2))[..., None] * fl_col[None, :]

        # --- sky
        sky_name = self.s.get('sky', 'night')
        sky_rows = int(max(1, math.ceil(horizon)))
        if sky_name:
            pano_w = int(round(W * 2 * math.pi / fov))
            pano = assets.make_sky(sky_name, pano_w, max(sky_rows, H // 2))
            ph = pano.shape[0]
            ang_cols = (np.arctan2(rdy, rdx) % (2 * math.pi)) / (2 * math.pi) * pano_w
            ang_cols = ang_cols.astype(int) % pano_w
            rows = np.arange(min(H, sky_rows + 2))
            pr = np.clip(ph - (horizon - rows) - 1, 0, ph - 1).astype(int)
            img[rows] = pano[pr][:, ang_cols]
            if self.fog_c is not None and self.s.get('fog_sky', True):
                k = float(self.s['fog'].get('sky_mix', 0.35))
                img[rows] = img[rows] * (1 - k) + self.fog_c * k
        else:
            img[:] = 0

        # --- floors and ceilings
        # Cells with a "drop" (water, pits) sit below z=0, so the floor is not one plane any
        # more: render one pass per distinct depth, deepest first, letting nearer planes win.
        ys = np.arange(H)
        frows = ys[ys + 0.5 > horizon + 0.5]
        crows = ys[ys + 0.5 < horizon - 0.5]
        drops = sorted({float(v) for v in np.unique(w.drop) if v > 1e-6}, reverse=True)
        drop0 = None
        if drops and frows.size:
            # where the un-sunken plane lands, so a deep pass can fill the submerged bank
            D0 = (camz * proj / (frows + 0.5 - horizon))[:, None] * np.ones((1, W))
            m0x = np.floor(px + rdx[None, :] * D0).astype(int)
            m0y = np.floor(py + rdy[None, :] * D0).astype(int)
            ok0 = (m0x >= 0) & (m0y >= 0) & (m0x < w.mw) & (m0y < w.mh)
            drop0 = np.zeros(D0.shape, np.float32)
            drop0[ok0] = w.drop[m0y[ok0], m0x[ok0]]

        for kind, dr in [('floor', v) for v in drops] + [('floor', 0.0), ('ceil', 0.0)]:
            if kind == 'floor':
                rows = frows
                if rows.size == 0:
                    continue
                d = (camz + dr) * proj / (rows + 0.5 - horizon)
                z = -dr
                tid_grid = w.floor_tid
            else:
                rows = crows
                if rows.size == 0:
                    continue
                d = (w.ceil_h - camz) * proj / (horizon - rows - 0.5)
                z = w.ceil_h
                tid_grid = w.ceil_tid
            D = d[:, None] * np.ones((1, W))
            wx = px + rdx[None, :] * D
            wy = py + rdy[None, :] * D
            mx, my = np.floor(wx).astype(int), np.floor(wy).astype(int)
            inb = (mx >= 0) & (my >= 0) & (mx < w.mw) & (my < w.mh)
            tids = np.full(D.shape, -1, np.int32)
            tids[inb] = tid_grid[my[inb], mx[inb]]
            valid = tids >= 0
            lip = None
            if kind == 'floor':
                cdrop = np.zeros(D.shape, np.float32)
                cdrop[inb] = w.drop[my[inb], mx[inb]]
                if dr > 0:
                    # the far bank seen below the waterline: only the deepest pass fills it
                    lip = (valid & (cdrop <= 1e-6) & (drop0 > 1e-6)) if dr == drops[0] \
                        else np.zeros(D.shape, bool)
                    valid = valid & ((np.abs(cdrop - dr) < 1e-6) | lip)
                else:
                    valid = valid & (cdrop <= 1e-6)
            if not valid.any():
                continue
            u = ((wx * T) % T).astype(int)
            v = ((wy * T) % T).astype(int)
            alb = np.zeros(D.shape + (3,), np.float32)
            em = np.zeros(D.shape, np.float32)
            for t in np.unique(tids[valid]):
                m = tids == t
                rgb, e = w.tex[t]
                alb[m] = rgb[v[m], u[m]]
                if e is not None:
                    em[m] = e[v[m], u[m]]
            if self.sn is not None:
                var = self.surface_variation(wx[valid], wy[valid], 0.0 if kind == 'floor' else 3.1)
                alb[valid] *= (1 + soft_swing(self.tex_amount[tids[valid]] * var))[:, None]
            for dcl in (w.floor_decals if kind == 'floor' else w.ceil_decals):
                if kind == 'floor' and abs(dcl['drop'] - dr) > 1e-6:
                    continue
                self._blend_plane_decal(alb, em, wx, wy, d, valid, dcl)
            if lip is not None and lip.any():
                alb[lip] *= 0.45  # bank below the waterline reads as shadowed, not lit
            dyn = sample_lm(self.lm, self.lres, wx, wy)
            dist = D * rlen[None, :]
            rr, cc = np.meshgrid(rows, np.arange(W), indexing='ij')
            col = self.shade(alb, dyn, np.full(D.shape, z), dist, em, flash(rr, cc, dist))
            sub = img[rows]
            sub[valid] = col[valid]
            img[rows] = sub
            dsub = depth[rows]
            dsub[valid] = D[valid]
            depth[rows] = dsub

        # --- walls: vectorised DDA over all columns, collecting every rising edge
        mapx = np.full(W, int(math.floor(px)))
        mapy = np.full(W, int(math.floor(py)))
        with np.errstate(divide='ignore'):
            ddx = np.where(rdx == 0, 1e30, np.abs(1 / rdx))
            ddy = np.where(rdy == 0, 1e30, np.abs(1 / rdy))
        stepx = np.where(rdx < 0, -1, 1)
        stepy = np.where(rdy < 0, -1, 1)
        sdx = np.where(rdx < 0, (px - mapx) * ddx, (mapx + 1 - px) * ddx)
        sdy = np.where(rdy < 0, (py - mapy) * ddy, (mapy + 1 - py) * ddy)
        inside = 0 <= mapx[0] < w.mw and 0 <= mapy[0] < w.mh
        prev_h = np.full(W, w.height[mapy[0], mapx[0]] if inside else 0.0, np.float32)
        # drop of the cell each ray is leaving: a wall rising out of sunken water starts below z=0
        prev_d = np.full(W, w.drop[mapy[0], mapx[0]] if inside else 0.0, np.float32)
        active = np.ones(W, bool)
        max_dist = float(self.s.get('max_distance', 64))
        hits = []
        for _ in range(int(2 * (w.mw + w.mh)) + 4):
            if not active.any():
                break
            xs = sdx < sdy
            dist = np.where(xs, sdx, sdy)
            mapx = np.where(xs & active, mapx + stepx, mapx)
            mapy = np.where(~xs & active, mapy + stepy, mapy)
            sdx = np.where(xs & active, sdx + ddx, sdx)
            sdy = np.where(~xs & active, sdy + ddy, sdy)
            inb = (mapx >= 0) & (mapy >= 0) & (mapx < w.mw) & (mapy < w.mh)
            active &= inb & (dist < max_dist)
            cyc, cxc = np.clip(mapy, 0, w.mh - 1), np.clip(mapx, 0, w.mw - 1)
            hgt = np.where(inb, w.height[cyc, cxc], 0)
            rise = active & (hgt > prev_h + 1e-6) & (dist > 1e-4)
            for c in np.nonzero(rise)[0]:
                hits.append((dist[c], c, int(not xs[c]), mapx[c], mapy[c], hgt[c], prev_d[c]))
            top = horizon - (hgt - camz) * proj / np.maximum(dist, 1e-4)
            bot = horizon + camz * proj / np.maximum(dist, 1e-4)
            active &= ~(rise & (top <= 0) & (bot >= H))
            prev_h = np.where(active, hgt, prev_h)
            prev_d = np.where(active, np.where(inb, w.drop[cyc, cxc], 0), prev_d)

        hits.sort(key=lambda h: -h[0])
        for dist, c, side, mx, my, hgt, below in hits:
            top = horizon - (hgt - camz) * proj / dist
            # a wall standing in sunken water carries on down to the surface instead of
            # stopping at z=0 and leaving the floor pass to guess what fills the gap
            bot = horizon + (camz + below) * proj / dist
            y0, y1 = max(0, int(math.ceil(top - 0.5))), min(H, int(math.ceil(bot - 0.5)))
            if y1 <= y0:
                continue
            if side == 0:
                wallx = py + dist * rdy[c]
            else:
                wallx = px + dist * rdx[c]
            uf_raw = wallx - math.floor(wallx)  # always measured along +x / +y, so decals are predictable
            uf = uf_raw
            if (side == 0 and rdx[c] < 0) or (side == 1 and rdy[c] > 0):
                uf = 1 - uf
            u = min(T - 1, int(uf * T))
            rows = np.arange(y0, y1)
            z = (horizon - (rows + 0.5)) * dist / proj + camz
            v = ((1 - (z % 1.0)) * T).astype(int).clip(0, T - 1)
            stack = w.stacks.get((my, mx))
            if stack is None:
                rgb, em = w.tex[w.wall_tid[my, mx]]
                alb = rgb[v, u]
                e = em[v, u] if em is not None else None
                wall_amt = self.tex_amount[w.wall_tid[my, mx]]
            else:
                storey = np.clip(np.floor(z).astype(int), 0, len(stack) - 1)
                alb = np.zeros((len(rows), 3), np.float32)
                e = np.zeros(len(rows), np.float32)
                for k in np.unique(storey):
                    m = storey == k
                    rgb, em = w.tex[stack[k]]
                    alb[m] = rgb[v[m], u]
                    if em is not None:
                        e[m] = em[v[m], u]
                # a facade can change material per storey, so the amount varies down the column
                wall_amt = self.tex_amount[np.asarray(stack, np.int32)[storey]]
            if self.sn is not None:
                # one key per wall plane, so a long wall varies continuously but the
                # two orientations and the far side of a corridor never match
                perp = round(px + rdx[c] * dist) if side == 0 else round(py + rdy[c] * dist)
                var = self.surface_variation(np.full(len(rows), wallx), z, side * 7.0 + perp * 1.31)
                # wall_amt is a scalar for a plain wall, one value per row for a stacked facade
                alb = alb * (1 + soft_swing(wall_amt * var))[:, None]
            if w.wall_decals:
                face = ('east' if rdx[c] < 0 else 'west') if side == 0 else \
                       ('south' if rdy[c] < 0 else 'north')
                dcls = w.wall_decals.get((my, mx, face))
                if dcls:
                    e = self._blend_wall_decals(alb, e, dcls, uf_raw, z)
            if side == 1:
                alb = alb * 0.78
            hx = px + rdx[c] * dist - rdx[c] / rlen[c] * 0.04
            hy = py + rdy[c] * dist - rdy[c] / rlen[c] * 0.04
            dyn = sample_lm(self.lm, self.lres, np.array([hx]), np.array([hy]))
            ed = dist * rlen[c]
            colr = self.shade(alb, np.repeat(dyn, len(rows), 0), z, np.full(len(rows), ed), e,
                              flash(rows, np.full(len(rows), c), np.full(len(rows), ed)))
            img[y0:y1, c] = colr
            depth[y0:y1, c] = dist

        # --- sprites: opaque pass (writes depth), then translucent/additive far-to-near (no depth writes)
        inv = 1.0 / (plx * dy - dx * ply)
        defs = self.s.get('sprite_defs', {})
        placed = []
        self.anchors = {}
        for sp in (self.s.get('sprites', []) + self.w.scatter_sprites
                   + cam.get('extra_sprites', [])):
            sp = {**assets.sprite_defaults(sp['type'], defs), **sp}
            sx, sy = float(sp['x']) - px, float(sp['y']) - py
            tx = inv * (dy * sx - dx * sy)
            ty = inv * (-ply * sx + plx * sy)
            if ty > 0.05:
                placed.append((ty, tx, sp))
        translucent = lambda sp: sp.get('blend', 'alpha') != 'alpha' or float(sp.get('opacity', 1)) < 1
        opaque = sorted([p for p in placed if not translucent(p[2])], key=lambda s: -s[0])
        trans = sorted([p for p in placed if translucent(p[2])], key=lambda s: -s[0])
        for ty, tx, sp in opaque + trans:
            self._draw_sprite(img, depth, ty, tx, sp, defs, horizon, proj, camz, pl, flash, translucent(sp))

        return np.clip(img, 0, 1)

    def _draw_sprite(self, img, depth, ty, tx, sp, defs, horizon, proj, camz, pl, flash, is_trans):
        W, H = self.W, self.H
        rgba, em = assets.get_sprite(sp['type'], defs)
        th, tw = rgba.shape[:2]
        hs = float(sp.get('scale', 1.0))
        # a sprite standing in a sunken cell rests on that lower surface (a boat sits on the water)
        cx, cy = int(math.floor(float(sp['x']))), int(math.floor(float(sp['y'])))
        sink = float(self.w.drop[cy, cx]) if 0 <= cy < self.w.mh and 0 <= cx < self.w.mw else 0.0
        zb = float(sp.get('z', 0.0)) - sink
        ph = hs * proj / ty
        pw = ph * tw / th * float(sp.get('stretch', 1.0))
        scx = (tx / ty + 1) * W / 2  # screen centre column
        ytop = horizon - (zb + hs - camz) * proj / ty
        if 'id' in sp:
            self.anchors[sp['id']] = {'x': scx, 'top': ytop, 'w': pw, 'h': ph, 'depth': ty,
                                      'visible': -pw < scx < W + pw and ytop + ph > 0 and ytop < H}
        x0, x1 = int(math.floor(scx - pw / 2)), int(math.ceil(scx + pw / 2))
        y0, y1 = int(math.floor(ytop)), int(math.ceil(ytop + ph))
        cx0, cx1 = max(0, x0), min(W, x1)
        cy0, cy1 = max(0, y0), min(H, y1)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        cols = np.arange(cx0, cx1)
        rows = np.arange(cy0, cy1)
        uu = ((cols + 0.5 - (scx - pw / 2)) / pw * tw).astype(int).clip(0, tw - 1)
        if sp.get('flip'):
            uu = tw - 1 - uu
        vv = ((rows + 0.5 - ytop) / ph * th).astype(int).clip(0, th - 1)
        wob = float(sp.get('wobble', 0))
        if wob:
            # per-texel-row sideways sway, stronger toward the bottom (ghost tails, flames, heat)
            phase = float(sp.get('phase', sp['x'] * 3.1 + sp['y'] * 1.7))
            off = np.round(wob * (vv / th + 0.2) * np.sin(vv * 0.55 + phase)).astype(int)
            U = (uu[None, :] + off[:, None]).clip(0, tw - 1)
            block = rgba[vv[:, None], U]
            emb = em[vv[:, None], U]
        else:
            block = rgba[np.ix_(vv, uu)]
            emb = em[np.ix_(vv, uu)]
        dsub = depth[cy0:cy1, cx0:cx1]
        alpha = block[..., 3] * float(sp.get('opacity', 1.0))
        if not is_trans:
            alpha = (alpha > 0.5).astype(np.float32)
        mask = (alpha > 0.02) & (ty < dsub)
        if not mask.any():
            return
        dyn = sample_lm(self.lm, self.lres, np.array([float(sp['x'])]), np.array([float(sp['y'])]))[0]
        zz = (horizon - (rows + 0.5)) * ty / proj + camz
        Z = np.repeat(zz[:, None], len(cols), 1)
        ed = ty * math.hypot(1, tx / ty * pl)
        rr, cc = np.meshgrid(rows, cols, indexing='ij')
        emm = np.maximum(emb, 1.0 if sp.get('fullbright') else 0.0)
        tint = np.array(sp.get('tint', [1, 1, 1]), np.float32)
        colr = self.shade(block[..., :3] * tint, np.broadcast_to(dyn, block.shape[:2] + (3,)), Z,
                          np.full(Z.shape, ed), emm, flash(rr, cc, np.full(Z.shape, ed)))
        sub = img[cy0:cy1, cx0:cx1]
        a = (alpha * mask)[..., None]
        if sp.get('blend') == 'additive':
            sub += colr * a
        else:
            sub[:] = sub * (1 - a) + colr * a
        if not is_trans:
            dsub[mask] = ty
        aura = sp.get('aura')
        if aura:
            self._aura(img, depth, alpha * (ty < dsub), cx0, cy0, ty, aura, pw)

    def _aura(self, img, depth, alpha, cx0, cy0, ty, aura, pw):
        """Soft additive glow around a sprite's silhouette (ghosts, spirits, magic)."""
        from PIL import ImageFilter
        H, W = img.shape[:2]
        r = max(2, int(float(aura.get('radius', 0.25)) * pw))
        pad = r * 2
        hh, ww = alpha.shape
        canvas = np.zeros((hh + 2 * pad, ww + 2 * pad), np.float32)
        canvas[pad:pad + hh, pad:pad + ww] = alpha
        im = Image.fromarray((canvas * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
        glow = np.asarray(im, np.float32) / 255
        y0, x0 = cy0 - pad, cx0 - pad
        sy0, sx0 = max(0, -y0), max(0, -x0)
        y1, x1 = min(H, y0 + glow.shape[0]), min(W, x0 + glow.shape[1])
        g = glow[sy0:sy0 + (y1 - max(0, y0)), sx0:sx0 + (x1 - max(0, x0))]
        vis = (depth[max(0, y0):y1, max(0, x0):x1] > ty * 0.9)[..., None]
        c = np.array(aura.get('color', [0.6, 0.8, 1.0]), np.float32) * float(aura.get('strength', 0.5))
        img[max(0, y0):y1, max(0, x0):x1] += g[..., None] * c * vis



# ------------------------------------------------------------------ output

def finish(img, scene, effects=(), seed=0):
    """Palette quantise (ordered dither), nearest-neighbour upscale, then display-stage effects."""
    effects = list(effects)
    spec, levels = post.palette_spec(effects, scene)
    arr = post.quantize(img, spec, float(scene.get('dither', 1.0)), levels)
    scale = int(scene.get('scale', 3))
    pim = Image.fromarray(arr, 'RGB')
    out = np.asarray(pim.resize((pim.width * scale, pim.height * scale), Image.NEAREST))
    out = post.apply_display(out, effects, {'scale': scale, 'seed': seed})
    return Image.fromarray(out)


def prepare_shot(scene, cam):
    """Per-shot adjustments: held lights from viewmodels (lantern, torch) and the flashlight item."""
    cam = dict(cam)
    overlays = list(scene.get('overlays', [])) + list(cam.get('overlays', []))
    extra = []
    for ov in overlays:
        if ov.get('type') != 'viewmodel':
            continue
        v = scene.get('viewmodel_defs', {}).get(ov['item']) or icons.VIEWMODELS.get(ov['item'], {})
        if v.get('light') and ov.get('light', True):
            L = {'x': cam['x'], 'y': cam['y'], 'z': 0.55, 'shadows': False, **v['light']}
            if isinstance(ov.get('light'), dict):
                L.update(ov['light'])
            extra.append(L)
        if v.get('flashlight') and 'flashlight' not in cam:
            cam['flashlight'] = True
    if extra:
        ovr = dict(cam.get('overrides', {}))
        ovr['lights'] = list(ovr.get('lights', scene.get('lights', []))) + extra
        cam['overrides'] = ovr
    return cam


def render_shot(scene, i, base=None):
    """Render shot `i` (0-based) of a scene to a finished PIL image.

    `base` is an optional (World, Renderer) pair for the scene as written; shots without
    `overrides` reuse it, so a many-shot scene builds its lightmap and scatter once.
    """
    shots = scene.get('shots') or [scene['camera']]
    cam = prepare_shot(scene, {**scene.get('camera', {}), **shots[i]})
    if cam.get('overrides'):
        sc = {**scene, **cam['overrides']}
        rr = Renderer(World(sc), sc)
    else:
        if base is None:
            w = World(scene)
            base = (w, Renderer(w, scene))
        rr = base[1]
    frame = rr.render(cam)
    return finish(frame, {**scene, **cam.get('overrides', {})}, rr.last_effects, i)


def draw_map(world, scene, cams, path, cell=24):
    """Top-down layout check: walls by height, floors by texture tint, lights, decals, scattered
    props (small olive dots), placed sprites (green squares) and each camera's view cone."""
    im = Image.new('RGB', (world.mw * cell, world.mh * cell), (10, 10, 14))
    d = ImageDraw.Draw(im)
    maxh = max(1.0, float(world.height.max()))
    for y in range(world.mh):
        for x in range(world.mw):
            box = [x * cell, y * cell, (x + 1) * cell - 1, (y + 1) * cell - 1]
            if world.height[y, x] > 0:
                g = int(90 + 140 * world.height[y, x] / maxh)
                d.rectangle(box, fill=(g, g // 2 + 20, g // 3 + 10))
            else:
                t = world.floor_tid[y, x]
                c = (world.tex[t][0].mean(axis=(0, 1)) * 140).astype(int) if t >= 0 else (0, 0, 0)
                d.rectangle(box, fill=tuple(int(v) for v in c))
                if world.ceil_tid[y, x] >= 0:
                    d.line([box[0], box[1], box[2], box[3]], fill=(60, 60, 70))
    for L in scene.get('lights', []):
        lx, ly = L['x'] * cell, L['y'] * cell
        c = tuple(int(min(1, v) * 255) for v in L.get('color', [1, 0.85, 0.6]))
        r = L.get('radius', 4) * cell
        d.ellipse([lx - r, ly - r, lx + r, ly + r], outline=tuple(v // 3 for v in c))
        d.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=c)
    for dcl in world.floor_decals:
        hw, hh = dcl['size'] * cell / 2, dcl['size'] * dcl['dh'] / dcl['dw'] * cell / 2
        dx_, dy_ = dcl['x'] * cell, dcl['y'] * cell
        d.rectangle([dx_ - hw, dy_ - hh, dx_ + hw, dy_ + hh], outline=(150, 118, 84))
    # scatter first, so the sprites an author placed by hand stay readable on top of it
    for sp in world.scatter_sprites:
        sx, sy = sp['x'] * cell, sp['y'] * cell
        d.rectangle([sx - 1, sy - 1, sx + 1, sy + 1], fill=(120, 132, 84))
    for sp in scene.get('sprites', []):
        sx, sy = sp['x'] * cell, sp['y'] * cell
        d.rectangle([sx - 2, sy - 2, sx + 2, sy + 2], fill=(80, 200, 120))
    for i, c in enumerate(cams):
        cx, cy = c['x'] * cell, c['y'] * cell
        a = math.radians(c.get('angle', 0))
        f = math.radians(c.get('fov', 66)) / 2
        L = 5 * cell
        for s in (-1, 1):
            d.line([cx, cy, cx + L * math.cos(a + s * f), cy + L * math.sin(a + s * f)], fill=(120, 160, 255))
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(80, 140, 255))
        d.text((cx + 6, cy - 6), str(i + 1), fill=(255, 255, 255))
    im.save(path)


# Every key the renderer reads. Anything else is ignored, which for a hand- or LLM-written file
# almost always means a typo ("ligths", "sprits") that silently drops part of the scene.
SCENE_KEYS = {
    'map', 'legend', 'default', 'camera', 'shots', 'resolution', 'scale', 'ceiling_height', 'sky',
    'ambient', 'lights', 'fog', 'fog_sky', 'sprites', 'sprite_defs', 'flashlight', 'light_levels',
    'scatter', 'grime', 'grime_debris', 'grime_decals', 'surface_noise', 'decals', 'decal_defs',
    'palette', 'auto_levels', 'dither', 'scanlines', 'overbright', 'lightmap_res', 'max_distance',
    'supersample', 'overlays', 'ui', 'post', 'icon_defs', 'viewmodel_defs', 'seed',
    'title', 'description', 'notes',  # free-form metadata, never read
}
SHOT_KEYS = {'x', 'y', 'angle', 'fov', 'height', 'pitch', 'flashlight', 'overlays', 'overrides',
             'post', 'scanlines', 'seed', 'supersample', 'extra_sprites', 'title', 'description', 'notes'}
CELL_KEYS = {'wall', 'h', 'top', 'floor', 'ceil', 'drop'}
ASSET_EXTS = ('.png', '.ttf', '.otf')


def lint_scene(scene):
    """Warnings for keys the renderer never reads. Keys starting with '_' pass as comments."""
    import difflib
    out = []

    def check(d, known, where):
        if not isinstance(d, dict):
            return
        for k in d:
            if k in known or str(k).startswith('_'):
                continue
            hint = difflib.get_close_matches(str(k), sorted(known), n=1, cutoff=0.7)
            out.append(f"{where}: unknown key {k!r}" + (f" - did you mean {hint[0]!r}?" if hint else ''))

    check(scene, SCENE_KEYS, 'scene')
    check(scene.get('camera'), SHOT_KEYS, 'camera')
    for i, shot in enumerate(scene.get('shots') or []):
        check(shot, SHOT_KEYS, f'shot {i + 1}')
        if isinstance(shot, dict):
            check(shot.get('overrides'), SCENE_KEYS, f'shot {i + 1} overrides')
    for ch, spec in (scene.get('legend') or {}).items():
        check(spec, CELL_KEYS, f'legend {ch!r}')
    return out


def resolve_paths(obj, base):
    """Point relative .png / .ttf paths at the scene file's folder when the file is there.

    Anything not found beside the scene is left untouched, so paths written relative to the
    working directory keep working.
    """
    if isinstance(obj, dict):
        return {k: resolve_paths(v, base) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_paths(v, base) for v in obj]
    if isinstance(obj, str) and obj.lower().endswith(ASSET_EXTS) and not os.path.isabs(obj):
        cand = os.path.join(base, obj)
        if os.path.isfile(cand):
            return cand
    return obj


def load_scene(path):
    """Read a scene file. Always UTF-8: the platform default (cp1252 on Windows) garbles em dashes
    and curly quotes in dialog, and fails outright on some accented capitals."""
    with open(path, encoding='utf-8-sig') as f:
        scene = json.load(f)
    return resolve_paths(scene, os.path.dirname(os.path.abspath(path)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scene')
    ap.add_argument('-o', '--out', default='render.png')
    ap.add_argument('--map', action='store_true', help='also write <out>_map.png top-down view')
    ap.add_argument('--sheet', action='store_true', help='also tile all shots into <out>_sheet.png')
    ap.add_argument('--shot', type=int, help='render only this shot number (1-based)')
    args = ap.parse_args()
    # output paths and warnings go to a pipe in most harnesses; on Windows that pipe is cp1252,
    # which cannot encode every path or key - degrade to escapes rather than crash after rendering
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='backslashreplace')

    scene = load_scene(args.scene)
    for warning in lint_scene(scene):
        print(f'warning: {warning}', file=sys.stderr)
    if not scene.get('shots') and not isinstance(scene.get('camera'), dict):
        ap.error('the scene needs a "camera" (or a list of "shots")')
    shots = scene.get('shots') or [scene['camera']]
    if args.shot is not None and not 1 <= args.shot <= len(shots):
        ap.error(f'--shot {args.shot} is out of range: this scene has {len(shots)} shot(s)')
    for i, cam in enumerate(shots):
        c = {**scene.get('camera', {}), **cam}
        if 'x' not in c or 'y' not in c:
            ap.error(f'shot {i + 1} has no x/y and there is no camera to inherit them from')
    base, ext = os.path.splitext(args.out)
    if not ext:  # PIL picks the format from the extension, and has nothing to go on without one
        ext = '.png'
        args.out = base + ext
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    world = World(scene)
    base_pair = (world, Renderer(world, scene))
    outs = []
    for i in range(len(shots)):
        if args.shot and i + 1 != args.shot:
            continue
        path = args.out if len(shots) == 1 else f"{base}_{i + 1:02d}{ext}"
        img = render_shot(scene, i, base_pair)
        img.save(path)
        outs.append((path, img))
        print(path)
    if args.map:
        mp = base + '_map.png'
        draw_map(world, scene, [{**scene.get('camera', {}), **c} for c in shots], mp)
        print(mp)
    if args.sheet and len(outs) > 1:
        w, h = outs[0][1].size
        cols = 2
        rows = (len(outs) + 1) // 2
        sheet = Image.new('RGB', (w * cols + 8 * (cols - 1), h * rows + 8 * (rows - 1)), (0, 0, 0))
        for k, (_, im) in enumerate(outs):
            sheet.paste(im, ((k % cols) * (w + 8), (k // cols) * (h + 8)))
        sp = base + '_sheet.png'
        sheet.save(sp)
        print(sp)


if __name__ == '__main__':
    main()

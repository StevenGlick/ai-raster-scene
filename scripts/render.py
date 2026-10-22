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
import types

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assets  # noqa: E402
import gui  # noqa: E402
import icons  # noqa: E402
import post  # noqa: E402
import prefabs  # noqa: E402
import buildings  # noqa: E402
import daylight  # noqa: E402
import wires  # noqa: E402
from world import (GLASS_TEXTURES, SCATTER_PERIOD, VOID_DEPTH, World, find_sprite, merge_camera,  # noqa: E402,F401
                   noise_field, plane_quads, resolve_camera, sample_noise)

T = assets.T


# ------------------------------------------------------------------ lighting

def build_lightmap(world, lights, res=8):
    """Dynamic light from point lights with grid shadows, `res` texels to a unit. Returns
    (lm, res, lift, top):
      lm    (mh*res, mw*res, 3) the light, for the ground, the walls and what stands on the ground;
      lift  (mh*res, mw*res, 1) how far above the default the lights reaching each spot hang (their
            luminance-weighted mean of z - 1.2), so their light fades above them rather than above
            the floor - None when no light is lifted, which leaves the falloff as it always was;
      top   the light on the tops of tall blocks - roofs - and on what stands there: a lamp above a
            roof shines over whatever the line from a spot up to it passes above, so it lights the
            roof round it and not only its own cell (lm itself where no roof is lit differently)."""
    H, W = world.mh * res, world.mw * res
    lm = np.zeros((H, W, 3), np.float32)
    if not lights:
        return lm, res, None, lm
    sy, sx = np.mgrid[0:H, 0:W]
    px = (sx.ravel() + 0.5) / res
    py = (sy.ravel() + 0.5) / res
    num = np.zeros(H * W, np.float64)
    den = np.zeros(H * W, np.float64)
    top = np.zeros((H, W, 3), np.float32)
    lifted = differs = False
    for L in lights:
        lx, ly = float(L['x']), float(L['y'])
        lz = float(L.get('z', LIGHT_Z))
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
        ft = f
        if L.get('shadows', True):
            block_h = min(lz, 0.95)
            steps = int(min(120, max(8, r * 12)))
            vis = np.ones(idx.size, bool)
            ix, iy = px[idx], py[idx]
            ddx, ddy = dx[idx], dy[idx]
            own_x, own_y = np.floor(ix).astype(int), np.floor(iy).astype(int)
            lcx, lcy = int(math.floor(lx)), int(math.floor(ly))
            zr = world.solid_h[np.clip(own_y, 0, world.mh - 1), np.clip(own_x, 0, world.mw - 1)]
            roof = (zr >= 0.95) & (zr < lz)             # spots on a roof, with the lamp above them
            vis_top = vis.copy() if roof.any() else None
            for t in np.linspace(0.02, 0.98, steps):
                qx = np.floor(ix + ddx * t).astype(int)
                qy = np.floor(iy + ddy * t).astype(int)
                inb = (qx >= 0) & (qy >= 0) & (qx < world.mw) & (qy < world.mh)
                qxc, qyc = np.clip(qx, 0, world.mw - 1), np.clip(qy, 0, world.mh - 1)
                hb = world.solid_h[qyc, qxc]
                skip = ((qx == own_x) & (qy == own_y)) | ((qx == lcx) & (qy == lcy))
                block = inb & (hb >= block_h) & ~skip
                vis &= ~block
                if vis_top is not None:                 # the line to the lamp passes over it
                    vis_top &= ~(block & ~(roof & (hb <= zr + (lz - zr) * t)))
            if vis_top is not None:
                ft = f * vis_top
                differs = differs or bool((vis_top != vis).any())
            f = f * vis
            if vis_top is None:
                ft = f
        flat = lm.reshape(-1, 3)
        flat[idx] += f[:, None] * c[None, :]
        top.reshape(-1, 3)[idx] += ft[:, None] * c[None, :]
        wgt = ft * float(c[0] * 0.299 + c[1] * 0.587 + c[2] * 0.114)
        den[idx] += wgt
        if lz > LIGHT_Z:
            num[idx] += wgt * (lz - LIGHT_Z)
            lifted = True
    lift = None
    if lifted:
        lift = np.where(den > 1e-9, num / np.maximum(den, 1e-9), 0.0).astype(np.float32).reshape(H, W, 1)
    return lm, res, lift, (top if differs else lm)


SUN_DEFAULTS = {
    # colour, intensity, disc colour, disc radius (degrees), halo strength
    'sun': ([1.0, 0.94, 0.82], 0.85, [1.0, 0.96, 0.82], 2.6, 0.6),
    'moon': ([0.55, 0.65, 0.95], 0.4, [0.9, 0.9, 0.84], 2.0, 0.3),
}


def _occluders(world, res):
    """What objects that cast the sun's shadow (`"casts": true`) stand in its way: over each ground
    sample (res per unit) the height of the highest of their panels there, and which object that is
    (-1 for none) - so an object never shadows itself, only the ground and everything else. None if
    no object casts."""
    pns = [p for p in list(world.scene.get('panels') or []) + list(world.panels) if p.get('casts')]
    if not pns:
        return None
    H, W = world.mh * res, world.mw * res
    occ = np.zeros((H, W), np.float32)
    oid = np.full((H, W), -1, np.int32)
    ids = {}
    for pn in pns:
        k = ids.setdefault(tuple(np.round(np.asarray(pn['at'], float), 4)), len(ids))
        a = np.asarray(pn['rgba'])[..., 3] > 0.5
        h, w = a.shape
        o, u, v = (np.asarray(pn[q], float) for q in ('o', 'u', 'v'))
        ns = max(2, int(math.ceil(np.linalg.norm(u[:2]) * res * 2)) + 1)    # finer than the samples, so
        nt = max(2, int(math.ceil(np.linalg.norm(v[:2]) * res * 2)) + 1)    # none it covers is missed
        S, T = np.meshgrid((np.arange(ns) + 0.5) / ns, (np.arange(nt) + 0.5) / nt)
        keep = a[np.minimum((T * h).astype(int), h - 1), np.minimum((S * w).astype(int), w - 1)]
        P = o + S[keep][:, None] * u + T[keep][:, None] * v
        ix, iy = np.floor(P[:, 0] * res).astype(int), np.floor(P[:, 1] * res).astype(int)
        ok = (ix >= 0) & (iy >= 0) & (ix < W) & (iy < H)
        np.maximum.at(occ, (iy[ok], ix[ok]), P[ok, 2].astype(np.float32))
        oid[iy[ok], ix[ok]] = k
    return occ, oid


def build_sun(world, L, res=4):
    """A directional light (sun or moon) and its shadows.

    Shadows come from one map: for each ground sample, the lowest height that can still see the
    light - the highest (wall height - distance x tan(elevation)) met while marching toward it.
    A point at height z is then lit when z clears that value, so facades are half-lit behind a
    lower building, characters' legs fall into the shadow of a wall, and a wall face turned
    away from the light shadows itself.

    Under a roof the light can only arrive through a gap - a doorway, a see-through window, the
    open side of a porch - so a second map holds the highest height that can still see it: the
    ray toward the light must be below the ceiling where it leaves the last roofed cell. A
    sunbeam therefore comes in low through a window and lands on the floor across the room. A
    solid wall that rises to meet the roof is roofed over for this, so no light slips in along the
    join; a wall with a storey of coloured glass stands in neither march - its panes let the light
    through coloured and its lead and stone stop it (sun_tint).

    Objects that cast (`"casts": true`) stand in the same march at a finer grain, by the highest of
    their panels over each sample, so a standing stone throws its own shape of shadow.
    """
    kind = L.get('type')
    colour, inten, disc_c, disc_r, glow = SUN_DEFAULTS[kind]
    az = math.radians(float(L.get('azimuth', 300)))
    el = math.radians(min(89.0, max(1.0, float(L.get('elevation', 35)))))
    ux, uy, tan_el = math.cos(az), math.sin(az), math.tan(el)
    H, W = world.mh * res, world.mw * res
    sy, sx = np.mgrid[0:H, 0:W]
    px, py = (sx + 0.5) / res, (sy + 0.5) / res
    zlit = np.full((H, W), -1.0, np.float32)
    occ = _occluders(world, res) if L.get('shadows', True) else None
    glass = getattr(world, 'glass', None)
    solid = world.solid_h if glass is None or not glass.any() else np.where(glass, 0.0, world.solid_h)
    maxh = max(float(solid.max()), float(occ[0].max()) if occ is not None else 0.0)
    if L.get('shadows', True) and maxh > 0:
        own_x, own_y = np.floor(px).astype(int), np.floor(py).astype(int)
        reach = min(maxh / tan_el, float(world.mw + world.mh))
        for t in np.arange(0.2, reach + 0.25, 0.25):
            qx = np.floor(px + ux * t).astype(int)
            qy = np.floor(py + uy * t).astype(int)
            inb = (qx >= 0) & (qy >= 0) & (qx < world.mw) & (qy < world.mh)
            hb = np.where(inb, solid[np.clip(qy, 0, world.mh - 1), np.clip(qx, 0, world.mw - 1)], 0)
            cand = np.where((qx == own_x) & (qy == own_y), -1.0, hb - t * tan_el)
            if occ is not None:                       # and the objects that cast, but never on themselves
                fx = np.floor((px + ux * t) * res).astype(int)
                fy = np.floor((py + uy * t) * res).astype(int)
                fin = (fx >= 0) & (fy >= 0) & (fx < W) & (fy < H)
                fx, fy = np.clip(fx, 0, W - 1), np.clip(fy, 0, H - 1)
                ho = np.where(fin & (occ[1][fy, fx] != occ[1]), occ[0][fy, fx], 0.0)
                cand = np.maximum(cand, np.where(ho > 0, ho - t * tan_el, -1.0))
            np.maximum(zlit, cand, out=zlit)
    roof = (world.ceil_tid >= 0) & ~world.glazed      # a glazed roof lets the light through
    zroof = np.full((H, W), np.inf, np.float32)
    zsky = np.full((2, H, W), -np.inf, np.float32)     # the band of heights lit down through a skylight
    if roof.any() and L.get('shadows', True):
        # a solid wall that rises to meet the roof leaves no gap at its top: light from under the roof must clear
        # its far side as well (else a sheet of it slips in where the wall's shadow and the roof's meet)
        beside = np.zeros_like(roof)                    # (corners too: a ray can cross one diagonally)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                beside[max(dy, 0):roof.shape[0] + min(dy, 0), max(dx, 0):roof.shape[1] + min(dx, 0)] |= \
                    roof[max(-dy, 0):roof.shape[0] + min(-dy, 0), max(-dx, 0):roof.shape[1] + min(-dx, 0)]
        sealed = beside & ~roof & (solid >= world.ceil_h - 1e-6)
        own = np.floor(py).astype(int) * world.mw + np.floor(px).astype(int)
        last = np.full((H, W), -1.0, np.float32)    # how far toward the light the roof lasts
        t_open = np.full((H, W), np.inf, np.float32)     # where the first stretch of open sky begins...
        t_shut = np.full((H, W), np.inf, np.float32)     # ...and where roof takes over again
        reach = min(world.ceil_h / tan_el + 1.0, float(world.mw + world.mh))
        for t in np.arange(0.0, reach + 0.25, 0.25):
            qx = np.floor(px + ux * t).astype(int)
            qy = np.floor(py + uy * t).astype(int)
            inb = (qx >= 0) & (qy >= 0) & (qx < world.mw) & (qy < world.mh)
            cq = np.clip(qy, 0, world.mh - 1), np.clip(qx, 0, world.mw - 1)
            under = inb & roof[cq]
            shut = under | (inb & sealed[cq] & (qy * world.mw + qx != own))      # (a wall's own face is not sealed)
            last = np.where(shut, t, last)
            t_shut = np.where(np.isfinite(t_open) & np.isinf(t_shut) & under, t, t_shut)
            t_open = np.where(np.isinf(t_open) & ~shut, t, t_open)
        zroof = np.where(last >= 0, world.ceil_h - (last + 0.25) * tan_el, np.inf).astype(np.float32)
        # a ray rising from height z crosses the roof's height (t - z/tan) along the way; if it
        # crosses inside that first open stretch it escapes, whatever roof lies beyond
        zsky[1] = np.where(np.isfinite(t_open), world.ceil_h - t_open * tan_el, -np.inf)
        zsky[0] = np.where(np.isfinite(t_shut), world.ceil_h - (t_shut - 0.25) * tan_el, -np.inf)
    elif roof.any():
        zroof[np.repeat(np.repeat(roof, res, 0), res, 1)] = -np.inf
    panes = _glass_cells(world, ux, uy) if glass is not None and glass.any() and L.get('shadows', True) else None
    rgb = np.array(L.get('color', colour), np.float32) * float(L.get('intensity', inten))
    disc = None
    if L.get('disc', True):
        disc = {'azimuth': math.degrees(az), 'elevation': math.degrees(el),
                'color': L.get('disc_color', disc_c), 'radius': float(L.get('disc_size', disc_r)), 'glow': glow,
                'style': L.get('disc_style')}
    return {'ux': ux, 'uy': uy, 'sin': math.sin(el), 'cos': math.cos(el), 'rgb': rgb, 'zlit': zlit,
            'zroof': zroof, 'zsky': zsky, 'ceil_h': world.ceil_h, 'res': res, 'disc': disc, 'kind': kind,
            'glass': panes, 'roof': roof, 'tan': tan_el}


def _glass_cells(world, ux, uy):
    """The walls of coloured glass (World.glass) as sun_tint reads them for a light from (ux, uy): each cell, its
    height, whether it rises to the roof, each storey's panes - each pane's hue, bright, where the texture glows;
    None for a storey of stone - and whether the faces the light comes in by lie inside the wall, against another
    cell of glass (the light took its colour at the first)."""
    cells, panes = [], {}
    for cy, cx in zip(*np.nonzero(world.glass)):
        tiers = []
        for tid in world.stacks.get((cy, cx), [world.wall_tid[cy, cx]]):
            if world.tex_key[tid] not in GLASS_TEXTURES:
                tiers.append(None)
                continue
            if tid not in panes:
                rgb_, em_ = world.tex[tid]
                pane = em_ > 0.5 if em_ is not None else np.zeros(rgb_.shape[:2], bool)
                hue = rgb_ / np.maximum(rgb_.max(-1, keepdims=True), 1e-3)
                panes[tid] = np.where(pane[..., None], hue * 0.95, 0.0).astype(np.float32)
            tiers.append(panes[tid])
        ox, oy = cx - (1 if ux > 0 else -1), cy - (1 if uy > 0 else -1)
        cells.append({'x': int(cx), 'y': int(cy), 'h': float(world.height[cy, cx]), 'tiers': tiers,
                      'roofed': float(world.height[cy, cx]) >= world.ceil_h - 1e-6,
                      'inner': (0 <= ox < world.mw and bool(world.glass[cy, ox]),
                                0 <= oy < world.mh and bool(world.glass[oy, cx]))})
    return cells


def sun_tint(s_, x, y, z):
    """The colour a sun's or moon's light has at points (x, y, z) from the coloured glass it came in through - 1.0
    where it came through none. Wherever the ray from a point toward the light enters a wall of glass beyond the
    point - at the height it has climbed to there, at its place along the face it crosses - a pane lets it on in the
    pane's colour and the lead and the stone round the panes stop it, as a wall of stone does; over the wall's top
    it passes untouched, unless the wall rises to the roof and the point is indoors, under a roof of its own."""
    cells = s_.get('glass')
    if not cells:
        return 1.0
    x, y, z = np.broadcast_arrays(np.asarray(x, np.float64), np.asarray(y, np.float64), np.asarray(z, np.float64))
    shape = x.shape
    x, y, z = x.reshape(-1), y.reshape(-1), z.reshape(-1)
    ux = s_['ux'] if abs(s_['ux']) > 1e-9 else 1e-9
    uy = s_['uy'] if abs(s_['uy']) > 1e-9 else 1e-9
    tint = None
    for c in cells:
        tx = (c['x'] + (0 if ux > 0 else 1) - x) / ux          # where the ray crosses into the cell's span in x,
        ty = (c['y'] + (0 if uy > 0 else 1) - y) / uy          # and in y: it is in the cell between the later of
        t_in = np.maximum(tx, ty)                              # those and the earlier of the crossings out
        hit = (t_in > 1e-6) & (t_in < np.minimum(tx + 1.0 / abs(ux), ty + 1.0 / abs(uy)))
        if not hit.any():
            continue
        sel = np.nonzero(hit)
        tc, xface = t_in[sel], tx[sel] >= ty[sel]
        zc = z[sel] + tc * s_['tan']
        along = np.where(xface, (y[sel] + uy * tc) % 1.0, (x[sel] + ux * tc) % 1.0)
        along = np.where(np.where(xface, ux < 0, uy > 0), 1 - along, along)      # as the wall pass reads it
        col = np.zeros(zc.shape + (3,), np.float32)
        over = zc >= c['h']
        col[over] = 1.0
        if c['roofed'] and over.any():                         # from indoors it went through the roof to get there
            xo, yo, zo = x[sel][over], y[sel][over], z[sel][over]
            roof = s_['roof']
            iy = np.clip(np.floor(yo).astype(int), 0, roof.shape[0] - 1)
            ix = np.clip(np.floor(xo).astype(int), 0, roof.shape[1] - 1)
            col[over] = (~(roof[iy, ix] & (zo < s_['ceil_h'] - 1e-6)))[:, None]
        k = np.clip(np.floor(zc).astype(int), 0, len(c['tiers']) - 1)
        for kk in np.unique(k[~over]):
            light = c['tiers'][kk]
            if light is None:
                continue                                       # a storey of stone
            s2 = ~over & (k == kk)
            n = light.shape[0]
            v = ((1 - zc[s2] % 1.0) * n).astype(int).clip(0, n - 1)
            col[s2] = light[v, (along[s2] * n).astype(int).clip(0, n - 1)]
        col[np.where(xface, c['inner'][0], c['inner'][1])] = 1.0
        if tint is None:
            tint = np.ones(x.shape + (3,), np.float32)
        tint[sel] *= col
    return 1.0 if tint is None else tint.reshape(shape + (3,))


def sun_visibility(s_, x, y, z, soft=0.12):
    """0-1: how much of a sun or moon a point (x, y, z) sees, with a soft edge to its shadows
    (`soft` is the height over which a shadow edge fades)."""
    zl, zr, r = s_['zlit'], s_['zroof'], s_['res']
    iy = np.clip((np.asarray(y) * r).astype(int), 0, zl.shape[0] - 1)
    ix = np.clip((np.asarray(x) * r).astype(int), 0, zl.shape[1] - 1)
    z = np.asarray(z)
    with np.errstate(invalid='ignore'):
        roof = np.clip(np.nan_to_num(zr[iy, ix] - z, posinf=9.0, neginf=-9.0) / soft + 0.5, 0, 1)
        if 'zsky' in s_:                              # or down through a skylight
            lo, hi = s_['zsky'][0][iy, ix], s_['zsky'][1][iy, ix]
            band = np.clip(np.nan_to_num(z - lo, posinf=9.0, neginf=9.0) / soft + 0.5, 0, 1) * \
                np.clip(np.nan_to_num(hi - z, posinf=9.0, neginf=-9.0) / soft + 0.5, 0, 1)
            roof = np.maximum(roof, band)
    roof = np.where(z >= s_['ceil_h'], 1.0, roof)    # air above a roof is outdoors
    return np.clip((z - zl[iy, ix]) / soft + 0.5, 0, 1) * roof


def _box4(a):
    """4x4 box average over axes 1 and 2 (rows and columns) of a stack of images, edges clamped."""
    pad = [(0, 0), (2, 1), (2, 1)] + [(0, 0)] * (a.ndim - 3)
    c = np.pad(a, pad, mode='edge').cumsum(axis=1).cumsum(axis=2)
    c = np.pad(c, [(0, 0), (1, 0), (1, 0)] + [(0, 0)] * (a.ndim - 3))
    h, w = a.shape[1], a.shape[2]
    out = c[:, 4:4 + h, 4:4 + w] - c[:, :h, 4:4 + w] - c[:, 4:4 + h, :w] + c[:, :h, :w]
    return (out / 16.0).astype(np.float32)


GLASS_DEFAULTS = {'tint': [0.82, 0.92, 1.0], 'opacity': 0.22, 'blur': 1, 'fog': False}


def glass_spec(g):
    """A sprite's `glass` field filled out: `true` takes the defaults (a light blue tint, a
    little reflection, the half-size blur), a dict overrides any of them."""
    out = dict(GLASS_DEFAULTS)
    if isinstance(g, dict):
        out.update(g)
    out['tint'] = np.array(out['tint'], np.float32)
    out['opacity'] = min(1.0, max(0.0, float(out['opacity'])))
    out['blur'] = max(0, min(3, int(out['blur'])))
    out['fog'] = bool(out['fog'])
    return out


def hole_runs(alpha):
    """For every see-through texel of an image, the run of see-through texels it lies in: its
    left and right ends along the row, and its top and bottom down the column (ends exclusive).
    For a rectangular opening that is the opening, which is how a card with `reveal` finds the
    sides of its windows."""
    clear = alpha < 0.5
    h, w = clear.shape
    xs = np.broadcast_to(np.arange(w), (h, w))
    ys = np.broadcast_to(np.arange(h)[:, None], (h, w))
    left = np.maximum.accumulate(np.where(clear, -1, xs), axis=1) + 1
    right = np.minimum.accumulate(np.where(clear, w, xs)[:, ::-1], axis=1)[:, ::-1]
    top = np.maximum.accumulate(np.where(clear, -1, ys), axis=0) + 1
    bottom = np.minimum.accumulate(np.where(clear, h, ys)[::-1], axis=0)[::-1]
    return left, right, top, bottom


def frost(img, k):
    """The frame shrunk by k - each k x k block averaged - and blown back up without smoothing:
    a blocky blur, the look of a scene through old window glass."""
    H, W = img.shape[:2]
    h, w = H // k, W // k
    out = img.copy()
    if h and w:
        small = img[:h * k, :w * k].reshape(h, k, w, k, -1).mean(axis=(1, 3))
        out[:h * k, :w * k] = np.repeat(np.repeat(small, k, 0), k, 1)
    return out


def sample_lm(lm, res, x, y):
    """Bilinear lightmap lookup for arrays of world coordinates."""
    H, W = lm.shape[:2]
    fx = np.clip(x * res - 0.5, 0, W - 1.001)
    fy = np.clip(y * res - 0.5, 0, H - 1.001)
    x0, y0 = fx.astype(int), fy.astype(int)
    tx, ty = (fx - x0)[..., None], (fy - y0)[..., None]
    a = lm[y0, x0]; b = lm[y0, x0 + 1]; c = lm[y0 + 1, x0]; d = lm[y0 + 1, x0 + 1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


LIGHT_Z = 1.2       # a point light's default height, which height_falloff is drawn for


def height_falloff(z):
    """Point lights sit near head height; tall walls fade into the dark above them. `z` is
    measured as if the light hung at LIGHT_Z: a higher light lifts it (Renderer.fade_z)."""
    return 1.0 / (1.0 + 0.7 * np.maximum(0, z - 1.4) ** 1.5)


# ------------------------------------------------------------------ surface variation

COARSE_PERIOD = 6.3   # world units: varies cell to cell
FINE_PERIOD = 0.43    # sub-cell, so a 1-unit wall gets a few cycles and mottles instead of
                      # streaking vertically; also never lines up with the 1-unit texture tiling
NOISE_TYPICAL = 0.27  # mean |value| of the two-octave blend, measured; divided out so that
                      # `amount` is the typical brightness swing rather than a rare peak
SURFACE_NOISE_DEFAULT = 0.10  # typical brightness swing, before each material scales it by its
                              # assets.TEXTURE_NOISE factor. "surface_noise": 0 disables it


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


# ------------------------------------------------------------------ pictures within pictures

PORTAL_REACH = 8.0      # how far behind a portal's exit the camera on its far side may stand
_SCREENS = {}           # a screen's picture, by what it shows: a shot is rendered once however often it is shown
_SCREEN_DEPTH = [0]     # how deep in screens-within-screens the render is: one level shows, the next is snow


def _snow(h, w, seed=7):
    """A screen with nothing to show: grey snow."""
    rng = np.random.default_rng(seed)
    return np.repeat((rng.random((h, w, 1)) * 0.7 + 0.15).astype(np.float32), 3, 2)


def screen_picture(spec, scene):
    """The picture a screen shows (h x w x 3, 0..1): a shot of another scene file (`scene`, its `shot` counted
    from 1) or of the scene it is in, or the view of a `camera` of its own, at the scene's resolution or the
    spec's `resolution` - rendered with its own post effects and overlays, palette and all."""
    key = json.dumps([spec.get('scene') or scene.get('title'), spec.get('shot', 1), spec.get('camera'),
                      spec.get('resolution')], sort_keys=True, default=str)
    if key not in _SCREENS:
        if _SCREEN_DEPTH[0] >= 1 or spec.get('snow'):
            W, H = spec.get('resolution') or scene.get('resolution', [320, 200])
            _SCREENS[key] = _snow(int(H), int(W))
        else:
            _SCREEN_DEPTH[0] += 1
            try:
                sc = load_scene(spec['scene']) if spec.get('scene') else scene
                if spec.get('resolution'):
                    sc = dict(sc, resolution=[int(v) for v in spec['resolution']])
                shots = [spec['camera']] if spec.get('camera') else sc.get('shots') or [sc['camera']]
                i = 0 if spec.get('camera') else max(0, min(len(shots), int(spec.get('shot', 1))) - 1)
                cam = prepare_shot(sc, merge_camera(sc, shots[i]))
                sc2 = shot_scene(sc, cam, shots[i])
                rr = Renderer(World(sc2), sc2)
                frame = rr.render(cam)
                pal, levels = post.palette_spec(rr.last_effects, sc2)
                arr = post.quantize(frame, pal, float(sc2.get('dither', 1.0)), levels, rr.palette_ref)
                _SCREENS[key] = arr.astype(np.float32) / 255.0
            finally:
                _SCREEN_DEPTH[0] -= 1
    return _SCREENS[key]


def screen_texture(pn, scene):
    """A panel with a `screen` (see objects.screen) as it shows its picture: the picture laid into its texture
    - over the whole of it, or the `rect` (rows and columns) of a screen set in a bezel - the texture grown so
    the picture keeps its pixels, lit by `glow`, with `crt` scanlines and rounded corners."""
    spec = pn['screen']
    pic = screen_picture(spec, scene)
    rgba, em = np.asarray(pn['rgba'], np.float32), np.asarray(pn['em'], np.float32)
    th, tw = rgba.shape[:2]
    y0, y1, x0, x1 = spec.get('rect') or (0, th, 0, tw)
    k = max(1, int(math.ceil(pic.shape[1] / max(x1 - x0, 1))))         # the texture grown to hold it
    rgba = np.repeat(np.repeat(rgba, k, 0), k, 1).copy()
    em = np.repeat(np.repeat(em, k, 0), k, 1).copy()
    h, w = (y1 - y0) * k, (x1 - x0) * k
    im = Image.fromarray((np.clip(pic, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.NEAREST)
    p = np.asarray(im, np.float32) / 255.0
    if spec.get('crt'):                                                # scanlines, the tube's dark corners
        p[1::2] *= 0.72
        yy, xx = np.mgrid[0:h, 0:w]
        r = np.hypot((xx + 0.5) / w * 2 - 1, (yy + 0.5) / h * 2 - 1)
        p *= np.clip(1.25 - 0.45 * r ** 2, 0, 1)[..., None]
    rgba[y0 * k:y1 * k, x0 * k:x1 * k, :3] = p
    rgba[y0 * k:y1 * k, x0 * k:x1 * k, 3] = 1.0
    em[y0 * k:y1 * k, x0 * k:x1 * k] = float(spec.get('glow', 0.9))
    return rgba, em


# ------------------------------------------------------------------ renderer

class Renderer:
    def __init__(self, world, scene):
        raw = scene
        scene = prefabs.expand(scene)
        if any(pn.get('screen') is not None for pn in scene.get('panels', [])):
            scene = dict(scene, panels=[dict(pn) for pn in scene['panels']])     # its own, to lay pictures into
        self.w = world
        self.s = scene
        # a portal shows the view from its far side (rendered before each frame, see _portal_views); a screen
        # a picture of another shot, rendered once
        self._portal_frames, self._portal_depth, self._portal_rr = {}, 0, {}
        for pn in scene.get('panels', []):
            if pn.get('screen') is not None:
                pn['rgba'], pn['em'] = screen_texture(pn, raw)
        self.W, self.H = scene.get('resolution', [320, 200])
        self.ambient = np.array(scene.get('ambient', [0.18, 0.18, 0.22]), np.float32)
        self.levels = int(scene.get('light_levels', 24))
        fog = scene.get('fog')
        self.fog_c = np.array(fog['color'], np.float32) if fog else None
        self.fog_d = float(fog.get('density', 0.1)) if fog else 0.0
        # Any of the volumetric keys moves fog from a per-surface fade to a pass that marches
        # through the air in front of every pixel, so it can lie low, drift in banks, glow round
        # lamps and carry shafts of sun or moonlight.
        self.vol = None
        if fog and any(k in fog for k in FOG_VOLUME_KEYS):
            sh = fog.get('shafts', True)
            self.vol = {'density': float(fog.get('density', 0.02)),
                        'ground': float(fog.get('ground', 0.0)),
                        'height': max(0.05, float(fog.get('height', 0.6))),
                        'noise': float(fog.get('noise', 0.0)),
                        'scale': max(0.2, float(fog.get('scale', 4.0))),
                        'glow': float(fog.get('glow', 1.0)),
                        'shafts': 1.0 if sh is True else 0.0 if sh is False else float(sh),
                        'steps': max(6, int(fog.get('steps', 32))),
                        'distance': float(fog.get('distance', min(48.0, float(scene.get('max_distance', 64))))),
                        'g': min(0.9, max(-0.5, float(fog.get('anisotropy', 0.3))))}
        lights, suns = [], []
        for L in scene.get('lights', []):
            kind = L.get('type', 'point')
            if kind not in ('point', 'sun', 'moon'):
                raise KeyError(f"unknown light type '{kind}'. Types: point (default), sun, moon")
            (lights if kind == 'point' else suns).append(L)
        for sp in scene.get('sprites', []):
            sp = {**assets.sprite_defaults(sp['type'], scene.get('sprite_defs', {})), **sp}
            if sp.get('light'):
                base = world.base_z(float(sp['x']), float(sp['y']))
                L = {'x': sp['x'], 'y': sp['y'], 'z': float(sp.get('z', 0)) + base + 0.2, 'shadows': True}
                L.update(sp['light'] if isinstance(sp['light'], dict) else {})
                lights.append(L)
        self.lm, self.lres, self.lift, self.lm_top = build_lightmap(world, lights, scene.get('lightmap_res', 8))
        self.overbright = float(scene.get('overbright', 1.0))
        self.suns = [build_sun(world, L) for L in suns]
        rf = scene.get('reflections', True)
        rf = ({} if rf is True else {'amount': 0.0} if rf is False
              else rf if isinstance(rf, dict) else {'amount': rf})
        self.reflect_k = float(rf.get('amount', 1.0))
        self.ripple = float(rf.get('ripple', 1.0))
        self.smear = float(rf.get('smear', 1.0))     # the vertical streak; 0 is a still mirror
        # a sun or moon light shows itself in the sky (unless it asks not to)
        self.discs = [s_['disc'] for s_ in self.suns if s_['disc']]
        self.sky_objects = list(scene.get('sky_objects') or [])
        self._skies = {}
        self._runs = {}
        self.palette_ref = None     # the last frame without its lens effects, for the palette
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
    def sun_at(self, x, y, z, lam):
        """Direct light from every sun or moon at points (x, y) of height z. `lam(sun)` gives the
        Lambert factor for the surface's orientation (scalar or per point). Not subject to the
        point lights' height falloff: sunlight reaches the top of a tall facade as well."""
        total = 0.0
        for s_ in self.suns:
            total = total + (sun_visibility(s_, x, y, z) * lam(s_))[..., None] * s_['rgb'] * sun_tint(s_, x, y, z)
        return total

    @staticmethod
    def lam_up(s_):
        return s_['sin']

    def _lm_at(self, x, y, z):
        """The lightmap for something at (x, y) standing at height z: the roofs' own on top of a
        tall block (lit by a lamp up there over the rest of the roof), else the ground's."""
        if self.lm_top is not self.lm:
            cx, cy = int(math.floor(x)), int(math.floor(y))
            if 0 <= cy < self.w.mh and 0 <= cx < self.w.mw:
                h = float(self.w.solid_h[cy, cx])
                if h >= 0.95 and z >= h - 0.05:
                    return self.lm_top
        return self.lm

    def fade_z(self, x, y, z):
        """Height z at points (x, y) as the point lights' height falloff should see it: less the
        lift of the lights that reach there, so a lamp hung high over a street, or set on a roof,
        lights the walls round it at its own height and fades above itself, not above the floor."""
        if self.lift is None:
            return z
        return z - sample_lm(self.lift, self.lres, x, y)[..., 0]

    def shade(self, albedo, dyn, z, dist, em, flash, sun=0.0):
        light = self.ambient[None, :] + dyn * height_falloff(z)[..., None] + flash + sun
        light = light * self.overbright
        if self.levels > 0:
            light = np.floor(light * self.levels + 0.5) / self.levels
        out = albedo * light
        glow = None
        if em is not None:
            e = em[..., None]
            glow = albedo * e * 1.15
            out = out * (1 - e) + glow
        if self.fog_c is not None and self.vol is None:
            k = (1 - np.exp(-self.fog_d * dist))[..., None]
            out = out * (1 - k) + self.fog_c[None, :] * k
            if glow is not None:
                glow = glow * (1 - k)
        self._glow = glow           # the emitted part, for the emission buffer (bloom, glare)
        return out

    def render(self, cam):
        """Render one camera: 3D pass (optionally supersampled), then UI overlays at native res."""
        ss = int(cam.get('supersample', self.s.get('supersample', 1)))
        self._ss = ss
        bw, bh = self.W, self.H
        self.W, self.H = bw * ss, bh * ss
        try:
            img = self._render3d(cam)
            if self.vol is not None:
                img = self._atmosphere(img, self.depth, ss)
        finally:
            self.W, self.H = bw, bh
        self._emis_out = self._emis
        if ss > 1:
            img = img.reshape(bh, ss, bw, ss, 3).mean(axis=(1, 3))
            self._emis_out = self._emis.reshape(bh, ss, bw, ss, 3).mean(axis=(1, 3))
            for a in self.anchors.values():
                for k in ('x', 'top', 'w', 'h'):
                    a[k] /= ss
        self.last_report = self._report(cam, img, ss)
        overlays = list(self.s.get('overlays', [])) + list(cam.get('overlays', []))
        effects = post.expand(list(self.s.get('post', [])) + list(cam.get('post', [])))
        if cam.get('scanlines', self.s.get('scanlines')) and not any(e['fx'] in ('scanlines', 'crt') for e in effects):
            effects.append({'fx': 'scanlines'})
        H, W = img.shape[:2]
        ctx = gui.Ctx(Image.new('RGBA', (W, H), (0, 0, 0, 0)), self.s, self.anchors, cam, self.w, self.camera_light(cam))
        wctx = self._weather_ctx(cam, ss, bw, bh)
        lens = [e for e in effects if e['fx'] in post.LENS]
        rest = [e for e in effects if e['fx'] not in post.LENS]
        sharp = post.apply_world(img, [], wctx) if lens else None
        img = post.apply_world(img, lens, wctx)
        ctx.emission = wctx.get('emission')                 # a held lantern adds its flame to it
        img = gui.draw_world_layer(img, overlays, ctx)
        img = post.apply_world(img, rest, dict(wctx, emission=ctx.emission))   # (a copy: embers add to it)
        img = gui.draw_ui_layer(img, overlays, ctx)
        # with a lens effect the frame is finished a second time without it, for the palette to be
        # chosen from (post.quantize): a subject kept sharp keeps the colours it has without the lens
        self.palette_ref = None
        if sharp is not None:
            ctx.emission = wctx.get('emission')
            sharp = gui.draw_world_layer(sharp, overlays, ctx)
            sharp = post.apply_world(sharp, rest, dict(wctx, emission=ctx.emission))
            self.palette_ref = np.clip(gui.overlay_ui(sharp, ctx), 0, 1)
        self.last_effects = effects
        return np.clip(img, 0, 1)

    def _report(self, cam, img, ss):
        """Problems with the frame that are easy to miss in a small preview, each with a fix:
        too dark or blown out, a black foreground, a blank where there is no sky, a wall in the
        lens, a camera inside a wall, and a subject (the `look_at` sprite or a bubble's speaker)
        that is hidden, cut off, tiny or unlit. The CLI prints them after each shot."""
        out = []
        lum = img @ np.array([0.299, 0.587, 0.114], np.float32)
        H, W = lum.shape
        mean = float(lum.mean())
        if mean < 0.045:
            out.append(f'the frame is very dark (mean brightness {mean:.2f}): raise "ambient" or add lights in view')
        elif float(lum[int(H * 0.75):].mean()) < 0.02:
            out.append('the bottom of the frame is nearly black: no light reaches the floor near the camera; '
                       'stretch a light over it or raise "ambient"')
        hot = float((lum > 0.97).mean())
        if hot > 0.25:
            out.append(f'{hot:.0%} of the frame is near white: lower the lights or "ambient", '
                       'or drop a bright post preset')
        depth = self.depth
        if not self.s.get('sky'):
            dark = img.repeat(ss, 0).repeat(ss, 1).sum(axis=2) < 1e-4
            blank = float((np.isinf(depth) & dark).mean())
            if blank > 0.02:
                out.append(f'{blank:.0%} of the frame shows nothing: with "sky": null an open cell needs a "ceil", '
                           'and the map needs walls all round where the camera can see')
        close = float((depth < 0.6).mean())
        if close > 0.3:
            out.append(f'something under 0.6 units from the camera fills {close:.0%} of the frame: step back or turn')
        cx, cy = int(math.floor(float(cam['x']))), int(math.floor(float(cam['y'])))
        if not (0 <= cy < self.w.mh and 0 <= cx < self.w.mw):
            out.append(f'the camera ({cam["x"]}, {cam["y"]}) is outside the map')
        elif self.w.solid_h[cy, cx] >= float(cam.get('height', 0.5)):
            out.append(f'the camera ({cam["x"]}, {cam["y"]}) is inside a wall cell')
        subjects = [cam['look_at']] if isinstance(cam.get('look_at'), str) else []
        for ov in list(self.s.get('overlays', [])) + list(cam.get('overlays', [])):
            if isinstance(ov, dict) and ov.get('type') == 'bubble' and ov.get('anchor'):
                subjects.append(ov['anchor'])
        named = {sp.get('id') for sp in list(self.s.get('sprites', [])) + list(cam.get('extra_sprites', []))}
        for sid in dict.fromkeys(subjects):
            st = self.sprite_stats.get(sid)
            if st is None:
                if sid in named:
                    out.append(f'"{sid}" is behind the camera or out of the frame')
                continue
            if st['visible'] <= 0:
                out.append(f'"{sid}" is completely hidden, behind a wall or a nearer sprite: check the map')
                continue
            seen = st['visible'] / max(st['area'], 1e-6)
            if seen < 0.4:
                out.append(f'only {seen:.0%} of "{sid}" is visible: something is in front of it, '
                           'or the frame edge cuts it off')
            if st['height'] / ss < 14:
                out.append(f'"{sid}" is only {st["height"] / ss:.0f} px tall on screen: move closer or narrow the fov')
            if st['brightness'] < 0.06:
                out.append(f'"{sid}" is almost black: give it a light (sprite "light") unless a silhouette is the point')
        return out

    def _weather_ctx(self, cam, ss, bw, bh):
        """What the world-stage post effects need to put weather in the scene: the depth buffer
        and the camera rays at output resolution, the world (walls, roofs) and the fog."""
        ctx = {'seed': int(self.s.get('seed', 0)) + int(cam.get('seed', 0)), 'world': self.w,
               'fog_d': self.fog_d if (self.fog_c is not None and self.vol is None) else 0.0}
        r = getattr(self, 'rays', None)
        if r is not None:
            c0 = np.arange(bw) * ss + ss // 2
            ctx['rays'] = {'px': r['px'], 'py': r['py'], 'rdx': r['rdx'][c0], 'rdy': r['rdy'][c0],
                           'horizon': r['horizon'] / ss, 'proj': r['proj'] / ss, 'camz': r['camz']}
            ctx['depth'] = self.depth.reshape(bh, ss, bw, ss).min(axis=(1, 3))
            if self.vol is not None:
                ctx['fog_t'] = self.fog_t[:2]
            ctx['suns'] = self._suns_in_view(ctx['rays'], ctx['depth'])
        if getattr(self, '_emis_out', None) is not None:
            ctx['emission'] = self._emis_out
        ctx['anchors'] = self.anchors
        ctx['focus'] = self._focus_distance(cam)
        return ctx

    def _suns_in_view(self, rays, depth):
        """Each sun or moon disc that falls in the frame: where (output pixels), its colour, how
        much of it shows (0-1: none behind a wall or a tree or past the edge of the frame) and its
        power (the moon's is weaker) - for the lens effects, a flare or a star of streaks."""
        out = []
        H, W = depth.shape
        ang = math.atan2(self._fy, self._fx)
        for s_ in self.suns:
            d = s_['disc']
            if not d:
                continue
            delta = (math.radians(d['azimuth']) - ang + math.pi) % (2 * math.pi) - math.pi
            if abs(delta) >= math.radians(80):
                continue
            x = W / 2 + rays['proj'] * math.tan(delta) - 0.5
            y = rays['horizon'] - rays['proj'] * math.tan(math.radians(d['elevation'])) - 0.5
            r = max(1.0, rays['proj'] * math.tan(math.radians(d['radius'])))
            n = int(math.ceil(r))
            gy, gx = np.mgrid[-n:n + 1, -n:n + 1]
            inside = gx * gx + gy * gy <= r * r
            py, px = np.round(y + gy[inside]).astype(int), np.round(x + gx[inside]).astype(int)
            on = (py >= 0) & (py < H) & (px >= 0) & (px < W)
            seen = np.isinf(depth[py[on], px[on]]).sum() / max(1, inside.sum())
            if seen > 0:
                out.append({'x': x, 'y': y, 'r': r, 'color': d['color'], 'visible': float(seen),
                            'power': 1.0 if s_['kind'] == 'sun' else 0.4})
        return out

    def _focus_distance(self, cam):
        """How far ahead (along the view) the shot is looking: its `look_at` - a sprite or a point -
        measured the way the depth buffer measures, or None when it looks nowhere in particular."""
        look = cam.get('look_at')
        if isinstance(look, str):
            sp = find_sprite(self.s, look, cam)
            look = None if sp is None else [sp['x'], sp['y']]
        if not isinstance(look, (list, tuple)) or len(look) < 2:
            return None
        d = (float(look[0]) - self._px) * self._fx + (float(look[1]) - self._py) * self._fy
        return d if d > 0.05 else None

    def _atmosphere(self, img, depth, ss):
        """Volumetric fog: march the air in front of every pixel, losing the surface behind it to
        the fog's density and gaining the light the fog scatters toward the eye.

        One ray is marched per output pixel; each supersampled pixel then reads the result at its
        own depth, so fog meets the edge of every wall cleanly. Density is a thin even haze plus
        a ground layer that thins with height and drifts in banks (`noise`); the light it carries
        is its own colour, the point lights (`glow`, read from the shadowed lightmap, so lamps
        get halos and doorways spill light) and every sun or moon it can see (`shafts`, through
        the shadow maps, with forward scattering so beams brighten as you look toward them).
        Behind glass the fog carries on: the glass pass leaves a correction for the air between
        each pane and what is seen through it (see _glass_pass).
        """
        if not self._marched:
            self._march(depth, ss)
        H, W = depth.shape
        Tp, Lp = self._fog_px(np.arange(H)[:, None], np.arange(W)[None, :], depth)
        out = img * Tp[..., None] + Lp
        if self._glass_fix is not None:
            out = out + self._glass_fix
        self._emis = self._emis * Tp[..., None]
        return out

    def _march(self, depth, ss):
        """The march itself, once a frame: how much of the light from each distance along every
        ray gets through the air, and how much the air adds, kept in self.fog_t."""
        self._marched = True
        v, r = self.vol, self.rays
        H, W = depth.shape
        h, w = H // ss, W // ss
        # no ray takes its light from past the farthest thing its pixel shows: the stretch that holds a wall or a
        # ceiling is sampled in front of it, not in the sunlit air beyond (over the roof, behind the wall)
        reach = np.nan_to_num(depth[:h * ss, :w * ss].reshape(h, ss, w, ss).max(axis=(1, 3)), nan=np.inf, posinf=np.inf)
        c0 = np.arange(w) * ss + ss // 2
        rdx, rdy, rlen = r['rdx'][c0], r['rdy'][c0], r['rlen'][c0]
        slope = (r['horizon'] - (np.arange(h) * ss + ss / 2)) / r['proj']        # z gained per unit t
        sx, sl = rdx[None, :], slope[:, None]
        path = np.sqrt(rlen[None, :] ** 2 + sl ** 2)                              # metres per unit t
        n = v['steps']
        t = v['distance'] * (np.arange(n + 1) / n) ** 1.6                         # finer near the eye
        # each ray samples its segments at a dithered point, so a shaft's edge and the steps of a
        # coarse far segment come out as fine grain instead of bands
        bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32)
        jit = (bayer[np.arange(h)[:, None] % 4, np.arange(w)[None, :] % 4] + 0.5) / 16
        tv = np.zeros((n + 1, h, w), np.float32)
        lv = np.zeros((n + 1, h, w, 3), np.float32)
        live = np.ones((n + 1, h, w), np.float32)         # 1 where the ray still has air at the start of the step
        T = np.ones((h, w), np.float32)
        L = np.zeros((h, w, 3), np.float32)
        tv[0] = 1.0
        fogc = self.fog_c if self.fog_c is not None else np.zeros(3, np.float32)
        field = noise_field() if v['noise'] > 0 else None
        phase = []
        for s_ in self.suns:
            cos = (sx * s_['ux'] * s_['cos'] + rdy[None, :] * s_['uy'] * s_['cos'] + sl * s_['sin']) / path
            g = v['g']
            phase.append(((1 - g * g) / (1 + g * g - 2 * g * cos) ** 1.5).astype(np.float32))
        for k in range(1, n + 1):
            dt = t[k] - t[k - 1]
            tm = t[k - 1] + jit * np.clip(np.minimum(t[k], reach) - t[k - 1], 0.0, dt)
            x, y = r['px'] + sx * tm, r['py'] + rdy[None, :] * tm
            z = r['camz'] + sl * tm
            z = np.broadcast_to(z, (h, w))
            # optical depth of the segment: the even haze, plus the ground layer integrated along
            # the ray (Simpson's rule on its height profile, which depends only on the row), so
            # it thins smoothly with height instead of in noisy steps
            tau = np.full((h, w), v['density'] * dt, np.float32)
            if v['ground'] > 0:
                zp = [np.maximum(r['camz'] + sl * tt, 0.0) for tt in (t[k - 1], 0.5 * (t[k - 1] + t[k]), t[k])]
                prof = [np.exp(-zz / v['height']) for zz in zp]
                layer = v['ground'] * dt / 6.0 * (prof[0] + 4 * prof[1] + prof[2])
                if field is not None:            # banks about `scale` wide, fading smoothly
                    patch = sample_noise(field, x / (v['scale'] * 4.0), y / (v['scale'] * 4.0))
                    layer = layer * np.exp(v['noise'] * 1.6 * (2 * patch - 1))
                tau = tau + layer
            a = 1 - np.exp(-tau * path)
            light = np.broadcast_to(fogc, (h, w, 3)).astype(np.float32)
            if v['glow'] > 0:
                hf = height_falloff(self.fade_z(x, y, z))[..., None]
                light = light + v['glow'] * sample_lm(self.lm, self.lres, x, y) * hf
            if v['shafts'] > 0:
                for s_, ph in zip(self.suns, phase):
                    # scaled so a beam seen side-on reads as a beam, and the air round a low
                    # sun glows without whiting out the frame
                    light = light + ((0.6 * v['shafts'] * sun_visibility(s_, x, y, z, 0.35) * ph)[..., None] * s_['rgb']
                                     * sun_tint(s_, x, y, z))
            L = L + (T * a)[..., None] * light
            T = T * (1 - a)
            tv[k], lv[k], live[k] = T, L, t[k - 1] < reach
        # neighbouring rays see nearly the same air: averaging each step over the 4x4 tile of the
        # dither pattern removes the pattern but keeps shafts and banks, and each pixel still reads
        # the result at its own depth, so nothing bleeds across a silhouette - nor from past the wall
        # a neighbour stops at: each step is averaged over the rays that still have air there
        n_live = _box4(live)
        some = n_live > 1e-6
        tv = np.where(some, _box4(tv * live) / np.maximum(n_live, 1e-6), tv)
        lv = np.where(some[..., None], _box4(lv * live[..., None]) / np.maximum(n_live, 1e-6)[..., None], lv)
        self.fog_t = (t, tv, lv)        # kept for weather, which sits inside the same fog

    def _fog_px(self, ri, ci, depth):
        """What the air does to the pixels at rows ri and columns ci (index arrays of the
        supersampled frame, broadcast together) seen at `depth`: the share of the light from that
        far that gets through (T) and the light the air in front adds (L). Each pixel reads its
        parent ray's march at its own depth."""
        t, tv, lv = self.fog_t
        ss = self._ss
        n = len(t) - 1
        d = np.minimum(np.nan_to_num(depth, posinf=t[-1]), t[-1])
        k = np.clip(np.searchsorted(t, d), 1, n)
        f = np.clip((d - t[k - 1]) / np.maximum(t[k] - t[k - 1], 1e-6), 0, 1)
        pi, pj = ri // ss, ci // ss
        Tp = tv[k - 1, pi, pj] * (1 - f) + tv[k, pi, pj] * f
        Lp = lv[k - 1, pi, pj] * (1 - f)[..., None] + lv[k, pi, pj] * f[..., None]
        # light scattered toward the eye eases off toward white instead of clipping, so mist
        # lit by a low sun glows rather than whiting out the frame
        knee = 0.55
        Lp = np.where(Lp > knee, knee + (1 - knee) * np.tanh((Lp - knee) / (1 - knee)), Lp)
        return Tp, Lp

    def camera_light(self, cam):
        """Light falling on things held at the camera (viewmodels): ambient + lightmap + flashlight spill."""
        lm = self._lm_at(float(cam['x']), float(cam['y']), float(cam.get('height', 0.5)) - 0.5)
        dyn = sample_lm(lm, self.lres, np.array([float(cam['x'])]), np.array([float(cam['y'])]))[0]
        light = self.ambient + dyn * 0.6
        if self.suns:  # a held item in sunlight is lit by it
            fx, fy = math.cos(math.radians(float(cam.get('angle', 0)))), math.sin(math.radians(float(cam.get('angle', 0))))
            light = light + np.asarray(self.sun_at(np.array([float(cam['x'])]), np.array([float(cam['y'])]),
                                                   np.array([0.4]), lambda s_: s_['sin'] * 0.5 + s_['cos'] * 0.6 *
                                                   max(0.2, -(fx * s_['ux'] + fy * s_['uy']))))[0]
        if cam.get('flashlight', self.s.get('flashlight')):
            light = light + 0.25
        # a floor keeps held items readable in near-darkness, the cap stops held lamps blowing them out
        return np.clip(light * self.overbright, 0.22, 1.0).astype(np.float32)

    def _blend_plane_decal(self, alb, emv, wx, wy, d, valid, dcl, rk=None):
        """Stamp one floor/ceiling decal into a surface pass's albedo."""
        sw = dcl['size']
        sh = sw * dcl['dh'] / dcl['dw']
        x0, y0 = dcl['x'] - sw / 2, dcl['y'] - sh / 2
        # a plane's distance is constant per row, so only a band of rows can touch the decal. `d`
        # is measured along the view axis, so the decal's centre must be too: its straight-line
        # distance is longer off-axis, which used to clip decals toward the edges of the frame
        rad = 0.5 * math.hypot(sw, sh)
        ctr = (dcl['x'] - self._px) * self._fx + (dcl['y'] - self._py) * self._fy
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
        if rk is not None and dcl['reflect'] > 0:   # a puddle mirrors what stands over it
            subr = rk[r0:r1]
            subr[m] = np.maximum(subr[m], dcl['reflect'] * a[:, 0])

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

    def _raw(self, cam, W, H):
        """The 3D frame of `cam` at W x H (the frame's own supersampled size), its air included: the colour
        and the emission, before any post effect - what a portal shows of the place it opens on."""
        bw, bh = self.W, self.H
        self.W, self.H = W, H
        try:
            img = self._render3d(cam)
            if self.vol is not None:
                img = self._atmosphere(img, self.depth, self._ss)
        finally:
            self.W, self.H = bw, bh
        return img, self._emis.copy()

    def _through(self, pn, cam):
        """The camera on a portal's far side: standing where this shot's camera would stand, and looking the
        way it would look, if the portal's opening were its exit - so the view through it lines up from here.
        A portal with a `view` looks out from that camera instead, whatever the shot (a window onto one view)."""
        spec = pn['portal']
        keep = {k: cam[k] for k in ('fov', 'pitch') if k in cam}
        if spec.get('view'):
            v = dict(spec['view'])
            sc = self._portal_scene(spec)
            return resolve_camera(sc, {**keep, 'x': v.pop('x'), 'y': v.pop('y'), **v})
        o, u, v = (np.asarray(pn[k], float) for k in ('o', 'u', 'v'))
        foot = o + u / 2 + v                                 # the middle of its foot
        n = np.cross(u, v)                                   # toward the side it is seen from
        f = -n[:2] / max(np.linalg.norm(n[:2]), 1e-9)        # the way into it
        r = np.array([-f[1], f[0]])
        to = spec['to']
        a = math.radians(float(to.get('angle', 0.0)))
        fd, rd = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
        rel = np.array([float(cam['x']), float(cam['y'])]) - foot[:2]
        p = np.array([float(to['x']), float(to['y'])]) + (rel @ f) * fd + (rel @ r) * rd
        back = -(rel @ f) - PORTAL_REACH
        if back > 0:                         # seen from far off, the far side's camera comes no further back
            p = p + back * fd                # than `reach` (it would stand in a wall): a small portal, no matter
        turn = math.degrees(a - math.atan2(f[1], f[0]))
        return {**keep, 'x': float(p[0]), 'y': float(p[1]), 'angle': (float(cam.get('angle', 0.0)) + turn) % 360,
                'height': float(cam.get('height', 0.5)) - float(foot[2]) + float(to.get('z', 0.0))}

    def _portal_scene(self, spec):
        """The scene a portal opens on: its own `scene` file, or this one."""
        return load_scene(spec['scene']) if spec.get('scene') else self.s

    def _portal_views(self, cam):
        """What each portal in sight shows - {its spec's id: (colour, emission)} at the frame's size - rendered
        from its far side's camera, in its own scene or this one. Inside a portal's view, portals are not
        opened again: they show their own texture."""
        frames = {}
        portals = [pn for pn in self.s.get('panels', []) if pn.get('portal') is not None]
        if self._portal_depth or not portals:
            return frames
        ang = math.radians(float(cam.get('angle', 0.0)))
        fwd = np.array([math.cos(ang), math.sin(ang)])
        half = math.radians(float(cam.get('fov', 66))) / 2 + 0.2
        for pn in portals:
            lift = self.w.base_z(float(pn['at'][0]), float(pn['at'][1])) if 'at' in pn else 0.0
            pn = dict(pn, o=np.asarray(pn['o'], float) + np.array([0.0, 0.0, lift]))
            corners = pn['o'] + np.array([[0, 0], [1, 0], [0, 1], [1, 1]], float) @ np.stack([pn['u'], pn['v']])
            rel = corners[:, :2] - np.array([float(cam['x']), float(cam['y'])])
            ahead = rel @ fwd
            if (ahead < 0.05).all():
                continue                                     # behind the camera
            off = np.arctan2(rel @ np.array([-fwd[1], fwd[0]]), np.maximum(ahead, 1e-3))
            if (ahead > 0.05).all() and ((off > half).all() or (off < -half).all()):
                continue                                     # out of the frame to one side
            spec = pn['portal']
            if spec.get('scene'):
                path = os.path.abspath(spec['scene'])
                if path not in self._portal_rr:
                    sc = load_scene(path)
                    self._portal_rr[path] = Renderer(World(sc), sc)
                rr = self._portal_rr[path]
            else:
                rr = self
            dcam = self._through(pn, cam)
            rr._portal_depth, rr._ss = self._portal_depth + 1, self._ss
            try:
                frames[id(spec)] = rr._raw(dcam, self.W, self.H)
            finally:
                rr._portal_depth = self._portal_depth if rr is self else 0
        return frames

    def _render3d(self, cam):
        """One frame of the world seen from `cam`: the sky, floors and ceilings, walls, then what stands
        in the world - sprites, cards, wireframes, glass - each pass drawing into the frame's colour,
        depth and emission buffers; then the reflections. Returns the colour, 0..1."""
        self._portal_frames = {}
        self._portal_frames = self._portal_views(cam)
        f = self._frame(cam)
        self._sky_pass(f)
        self._floor_pass(f)
        self._wall_pass(f)
        self._sprite_pass(f)
        img, depth, refl, refl_depth = f.img, f.depth, f.refl, f.refl_depth
        px, py, rdx, rdy, rlen, horizon, proj, camz = f.px, f.py, f.rdx, f.rdy, f.rlen, f.horizon, f.proj, f.camz
        if refl.any():
            sky = self._sky_layer or (None, None)
            img = self._reflect(img, depth, refl, refl_depth, sky[0])
            self._emis = self._reflect(self._emis, depth, refl, refl_depth, sky[1])
        self.depth = depth
        self.rays = {'px': px, 'py': py, 'rdx': rdx, 'rdy': rdy, 'rlen': rlen, 'horizon': horizon,
                     'proj': proj, 'camz': camz}
        return np.clip(img, 0, 1)

    def _frame(self, cam):
        """The frame's camera and rays, its buffers - colour, depth, emission, how mirror-like each floor
        pixel is and at what depth - and the flashlight: what every pass draws with and into."""
        W, H = self.W, self.H
        w = self.w
        self._marched, self._glass_fix = False, None
        self._sky_layer = None
        px, py = float(cam['x']), float(cam['y'])
        self._px, self._py = px, py
        ang = math.radians(float(cam.get('angle', 0)))
        fov = math.radians(float(cam.get('fov', 66)))
        camz = float(cam.get('height', 0.5))
        horizon = H / 2 + float(cam.get('pitch', 0)) * H
        self._horizon = horizon
        proj = (W / 2) / math.tan(fov / 2)
        self._proj = proj
        dx, dy = math.cos(ang), math.sin(ang)
        self._fx, self._fy = dx, dy
        pl = math.tan(fov / 2)

        def in_view(dcl):
            """A floor/ceiling decal that could touch the frame: in front, and inside the cone."""
            vx, vy = dcl['x'] - px, dcl['y'] - py
            r = dcl['size'] * max(1.0, dcl['dh'] / dcl['dw'])
            along = vx * dx + vy * dy
            return along > -r and abs(vy * dx - vx * dy) <= max(along, 0) * pl + r + 0.5
        floor_decals = [d_ for d_ in w.floor_decals if in_view(d_)]
        ceil_decals = [d_ for d_ in w.ceil_decals if in_view(d_)]
        plx, ply = -dy * pl, dx * pl
        cx = 2 * (np.arange(W) + 0.5) / W - 1
        rdx = (dx + plx * cx).astype(np.float64)
        rdy = (dy + ply * cx).astype(np.float64)
        rlen = np.sqrt(rdx ** 2 + rdy ** 2)

        img = np.zeros((H, W, 3), np.float32)
        depth = np.full((H, W), np.inf, np.float32)
        # what each pixel gives off as light (lit windows, neon, flames, the sun), beside what it shows:
        # every surface that is drawn writes its emitted part here, so bloom can glow from light
        # sources only (see post.fx_bloom's `source`)
        emis = np.zeros((H, W, 3), np.float32)
        self._emis = emis
        refl = np.zeros((H, W), np.float32)          # how mirror-like each floor pixel is
        refl_depth = np.full((H, W), -1.0, np.float32)

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
        return types.SimpleNamespace(
            W=W, H=H, w=w, cam=cam, px=px, py=py, fov=fov, camz=camz, horizon=horizon, proj=proj, dx=dx, dy=dy,
            pl=pl, plx=plx, ply=ply, rdx=rdx, rdy=rdy, rlen=rlen, floor_decals=floor_decals,
            ceil_decals=ceil_decals, img=img, depth=depth, emis=emis, refl=refl, refl_depth=refl_depth,
            flash=flash)

    def _sky_pass(self, f):
        """The sky behind everything: the panorama for the scene's sky (black when there is none)."""
        W, H, w, img, emis, fov, horizon, proj = f.W, f.H, f.w, f.img, f.emis, f.fov, f.horizon, f.proj
        rdx, rdy = f.rdx, f.rdy
        # --- sky
        sky_name = self.s.get('sky', 'night')
        sky_rows = int(max(1, math.ceil(horizon)))
        if sky_name:
            pano_w = int(round(W * 2 * math.pi / fov))
            # a void floor shows sky under the horizon too: stars in space, cloud far below otherwise
            below = max(2, H - sky_rows + 2) if w.void.any() else 0
            key = (pano_w, max(sky_rows, H // 2), round(proj, 3), below)
            if key not in self._skies:  # identical for every shot that shares a lens and pitch
                self._skies[key] = assets.make_sky(sky_name, pano_w, key[1], skyline=self.s.get('skyline'),
                                                   proj=proj, discs=self.discs, objects=self.sky_objects,
                                                   below=below)
            pano = self._skies[key]
            ph = key[1]
            ang_cols = (np.arctan2(rdy, rdx) % (2 * math.pi)) / (2 * math.pi) * pano_w
            ang_cols = ang_cols.astype(int) % pano_w
            rows = np.arange(H) if below else np.arange(min(H, sky_rows + 2))
            pr = np.clip(ph - (horizon - rows) - 1, 0, pano.shape[0] - 1).astype(int)
            img[rows] = pano[pr][:, ang_cols]
            emis[rows] = np.maximum(img[rows] - 0.9, 0) * 6.0       # a sun or moon disc glows
            if self.fog_c is not None and self.s.get('fog_sky', True) and self.vol is None:
                k = float(self.s['fog'].get('sky_mix', 0.35))
                img[rows] = img[rows] * (1 - k) + self.fog_c * k
                emis[rows] = emis[rows] * (1 - k)
            if self.smear < 1.0:                # a still mirror shows the sky behind what floats over it
                self._sky_layer = (img.copy(), emis.copy())
        else:
            img[:] = 0

    def _floor_pass(self, f):
        """Floors and ceilings, cast row by row, deepest plane first where cells sink below z=0."""
        W, H, w, img, depth, emis, refl = f.W, f.H, f.w, f.img, f.depth, f.emis, f.refl
        refl_depth, camz, horizon, proj, px, py = f.refl_depth, f.camz, f.horizon, f.proj, f.px, f.py
        rdx, rdy, rlen, flash, floor_decals = f.rdx, f.rdy, f.rlen, f.flash, f.floor_decals
        ceil_decals = f.ceil_decals
        # --- floors and ceilings
        # Cells with a "drop" (water, pits) sit below z=0, so the floor is not one plane any
        # more: render one pass per distinct depth, deepest first, letting nearer planes win.
        ys = np.arange(H)
        frows = ys[ys + 0.5 > horizon + 0.5]
        crows = ys[ys + 0.5 < horizon - 0.5]
        drops = sorted({float(v) for v in np.unique(w.drop[~w.void]) if v > 1e-6}, reverse=True)
        drop0 = None
        if drops and frows.size:
            # where the un-sunken plane lands, so a deep pass can fill the submerged bank
            D0 = (camz * proj / (frows + 0.5 - horizon))[:, None] * np.ones((1, W))
            m0x = np.clip(np.floor(px + rdx[None, :] * D0).astype(int), 0, w.mw - 1)
            m0y = np.clip(np.floor(py + rdy[None, :] * D0).astype(int), 0, w.mh - 1)
            drop0 = np.where(w.void[m0y, m0x], 0.0, w.drop[m0y, m0x])

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
            if kind == 'floor':
                # past the map edge the ground carries on as the nearest edge cell - its floor and
                # its drop alike - so an open vista meets its skyline instead of a black band
                mx, my = np.clip(mx, 0, w.mw - 1), np.clip(my, 0, w.mh - 1)
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
                    if lip.any():   # a bank's sunken edge shows the cell's `side` texture, if it has one
                        st = w.side_tid[my[lip], mx[lip]]
                        tids[lip] = np.where(st >= 0, st, tids[lip])
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
            if kind == 'floor' and w.wet.any():
                alb *= (1 - 0.3 * w.wet[my, mx])[..., None]       # wet ground is darker
            if self.sn is not None:
                var = self.surface_variation(wx[valid], wy[valid], 0.0 if kind == 'floor' else 3.1)
                alb[valid] *= (1 + soft_swing(self.tex_amount[tids[valid]] * var))[:, None]
            rk = None
            if kind == 'floor' and self.reflect_k > 0:
                rk = np.where(valid, w.reflect[my, mx], 0.0).astype(np.float32)
            for dcl in (floor_decals if kind == 'floor' else ceil_decals):
                if kind == 'floor' and abs(dcl['drop'] - dr) > 1e-6:
                    continue
                self._blend_plane_decal(alb, em, wx, wy, d, valid, dcl, rk)
            if lip is not None and lip.any():
                alb[lip] *= 0.45  # bank below the waterline reads as shadowed, not lit
            dyn = sample_lm(self.lm, self.lres, wx, wy)
            dist = D * rlen[None, :]
            rr, cc = np.meshgrid(rows, np.arange(W), indexing='ij')
            sun = self.sun_at(wx, wy, np.full(D.shape, z), self.lam_up) if kind == 'floor' and self.suns else 0.0
            col = self.shade(alb, dyn, self.fade_z(wx, wy, np.full(D.shape, z)), dist, em, flash(rr, cc, dist), sun)
            sub = img[rows]
            sub[valid] = col[valid]
            img[rows] = sub
            gsub = emis[rows]
            gsub[valid] = self._glow[valid] if self._glow is not None else 0.0
            emis[rows] = gsub
            dsub = depth[rows]
            dsub[valid] = D[valid]
            depth[rows] = dsub
            if rk is not None and rk.any():
                k = valid & (rk > 0)
                rsub, dsub2 = refl[rows], refl_depth[rows]
                rsub[k] = rk[k] * self.reflect_k
                dsub2[k] = dsub[k]
                refl[rows], refl_depth[rows] = rsub, dsub2

        self._plane_depth = depth if self.smear >= 1.0 else depth.copy()   # what the floor pass left

    def _wall_pass(self, f):
        """Walls, block tops and the faces of raised and sunken ground, column by column."""
        W, H, w, img, depth, emis, camz = f.W, f.H, f.w, f.img, f.depth, f.emis, f.camz
        horizon, proj, px, py, rdx, rdy, rlen = f.horizon, f.proj, f.px, f.py, f.rdx, f.rdy, f.rlen
        flash = f.flash
        # --- walls: a vectorised DDA over all columns. It collects a face at every rising edge, and
        # the top of every block lower than the eye, so steps, altars and kerbs read as solid.
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
        cy0, cx0 = (int(mapy[0]), int(mapx[0])) if inside else (0, 0)
        # the height a new wall has to rise above to be seen; see-through cells never raise it
        prev_h = np.full(W, w.solid_h[cy0, cx0] if inside else 0.0, np.float32)
        prev_see = np.full(W, bool(w.see[cy0, cx0]) if inside else False)
        # drop of the cell each ray is leaving: a wall rising out of sunken water starts below z=0
        prev_d = np.full(W, w.drop[cy0, cx0] if inside else 0.0, np.float32)
        prev_void = np.full(W, bool(w.void[cy0, cx0]) if inside else False)
        active = np.ones(W, bool)
        max_dist = float(self.s.get('max_distance', 64))
        hits = []  # ('face' | 'top', nearest distance, column, ...), drawn far to near
        if inside and not w.see[cy0, cx0] and 1e-6 < w.height[cy0, cx0] < camz - 1e-6:
            # standing on a low block: its own top runs from under the camera to its far edge
            exit0 = np.minimum(sdx, sdy)
            hits += [('top', 0.0, c, cx0, cy0, float(w.height[cy0, cx0]), float(exit0[c])) for c in range(W)]
        for _ in range(int(2 * (w.mw + w.mh)) + 4):
            if not active.any():
                break
            xs = sdx < sdy
            dist = np.where(xs, sdx, sdy)            # where each ray enters its next cell...
            mapx = np.where(xs & active, mapx + stepx, mapx)
            mapy = np.where(~xs & active, mapy + stepy, mapy)
            sdx = np.where(xs & active, sdx + ddx, sdx)
            sdy = np.where(~xs & active, sdy + ddy, sdy)
            exitd = np.minimum(sdx, sdy)             # ...and where it leaves it
            inb = (mapx >= 0) & (mapy >= 0) & (mapx < w.mw) & (mapy < w.mh)
            active &= inb & (dist < max_dist)
            cyc, cxc = np.clip(mapy, 0, w.mh - 1), np.clip(mapx, 0, w.mw - 1)
            hgt = np.where(inb, w.height[cyc, cxc], 0)
            see_c = inb & w.see[cyc, cxc]
            # a run of see-through cells shows only the face the ray enters it by, never inner faces
            rise = active & (hgt > prev_h + 1e-6) & (dist > 1e-4) & ~(see_c & prev_see)
            low = active & ~see_c & (hgt > 1e-6) & (hgt < camz - 1e-6)
            for c in np.nonzero(rise)[0]:
                # a wall or fence at the brink stops at the ground; the cliff under it is the bank
                below = 0.0 if prev_void[c] else prev_d[c]
                hits.append(('face', dist[c], c, int(not xs[c]), mapx[c], mapy[c], hgt[c], below,
                             bool(see_c[c])))
            vo = inb & w.void[cyc, cxc]
            # climbing out of a void onto anything solid: the edge of the ground is a cliff
            bank = active & prev_void & ~vo & (dist > 1e-4)
            for c in np.nonzero(bank)[0]:
                lvl = float(w.drop[cyc[c], cxc[c]]) if hgt[c] <= 1e-6 else 0.0
                hits.append(('bank', dist[c], c, int(not xs[c]), mapx[c], mapy[c], lvl))
            for c in np.nonzero(low)[0]:
                hits.append(('top', dist[c], c, mapx[c], mapy[c], hgt[c], exitd[c]))
            top = horizon - (hgt - camz) * proj / np.maximum(dist, 1e-4)
            bot = horizon + camz * proj / np.maximum(dist, 1e-4)
            # a solid wall that fills the whole column hides everything behind it
            active &= ~(rise & ~see_c & (top <= 0) & (bot >= H))
            prev_h = np.where(active & ~see_c, hgt, prev_h)
            prev_see = np.where(active, see_c, prev_see)
            prev_d = np.where(active, np.where(inb, w.drop[cyc, cxc], 0), prev_d)
            prev_void = np.where(active, vo, prev_void)

        # far to near; at the same distance a block's top goes down before its face
        hits.sort(key=lambda h: (-h[1], h[0] == 'face'))
        for hit in hits:
            if hit[0] == 'top':
                # the top of a low block: a patch of floor at the block's height, between where the
                # ray crosses into the cell and where it leaves, with its own per-row depth
                _, din, c, mx, my, hgt, dout = hit
                lift = camz - hgt
                far_row = horizon + lift * proj / max(dout, 1e-4)
                near_row = horizon + lift * proj / din if din > 1e-6 else H + 1
                y0, y1 = max(0, int(math.ceil(far_row - 0.5))), min(H, int(math.ceil(near_row - 0.5)))
                if y1 <= y0:
                    continue
                rows = np.arange(y0, y1)
                dd = lift * proj / (rows + 0.5 - horizon)
                tx, ty = px + rdx[c] * dd, py + rdy[c] * dd
                tid = w.floor_tid[my, mx]
                rgb, em = w.tex[tid]
                tu, tv = ((tx * T) % T).astype(int), ((ty * T) % T).astype(int)
                alb = rgb[tv, tu]
                e = em[tv, tu] if em is not None else None
                if self.sn is not None:
                    var = self.surface_variation(tx, ty, 5.3)
                    alb = alb * (1 + soft_swing(self.tex_amount[tid] * var))[:, None]
                ed = dd * rlen[c]
                zt = np.full(len(rows), hgt)
                sun = self.sun_at(tx, ty, zt, self.lam_up) if self.suns else 0.0
                colr = self.shade(alb, sample_lm(self.lm_top, self.lres, tx, ty), self.fade_z(tx, ty, zt), ed, e,
                                  flash(rows, np.full(len(rows), c), ed), sun)
                img[y0:y1, c] = colr
                emis[y0:y1, c] = self._glow if self._glow is not None else 0.0
                depth[y0:y1, c] = dd
                continue
            if hit[0] == 'bank':
                _, dist, c, side, mx, my, lvl = hit
                wallx = py + dist * rdy[c] if side == 0 else px + dist * rdx[c]
                jag = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(wallx * 5.3 + mx * 1.7 + my * 2.9)
                                   * math.cos(wallx * 2.2 - my * 0.7))
                top = horizon + (camz + lvl) * proj / dist
                deep = float(w.cliff[my, mx])
                bot = horizon + (camz + deep * jag) * proj / dist
                y0, y1 = max(0, int(math.ceil(top - 0.5))), min(H, int(math.ceil(bot - 0.5)))
                tid = w.side_tid[my, mx] if w.side_tid[my, mx] >= 0 else w.floor_tid[my, mx]
                if y1 <= y0 or tid < 0:
                    continue
                rows = np.arange(y0, y1)
                keep = depth[y0:y1, c] > dist
                if not keep.any():
                    continue
                z = (horizon - (rows + 0.5)) * dist / proj + camz
                rgb, em = w.tex[tid]
                u = min(T - 1, int((wallx - math.floor(wallx)) * T))
                v = ((1 - (z % 1.0)) * T).astype(int).clip(0, T - 1)
                alb = rgb[v, u] * (0.85 - 0.55 * np.clip(-z / deep, 0, 1))[:, None]
                if side == 1:
                    alb = alb * 0.78
                hx = px + rdx[c] * dist - rdx[c] / rlen[c] * 0.04
                hy = py + rdy[c] * dist - rdy[c] / rlen[c] * 0.04
                ed = np.full(len(rows), dist * rlen[c])
                colr = self.shade(alb, np.repeat(sample_lm(self.lm, self.lres, np.array([hx]), np.array([hy])),
                                                 len(rows), 0),
                                  self.fade_z(np.array([hx]), np.array([hy]), z), ed, None,
                                  flash(rows, np.full(len(rows), c), ed), 0.0)
                img[rows[keep], c] = colr[keep]
                emis[rows[keep], c] = 0.0
                depth[rows[keep], c] = dist
                continue
            _, dist, c, side, mx, my, hgt, below, see_hit = hit
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
            solid = None  # rows of a see-through wall that are actually there
            if stack is None:
                tid = w.wall_tid[my, mx]
                rgb, em = w.tex[tid]
                alb = rgb[v, u]
                e = em[v, u] if em is not None else None
                wall_amt = self.tex_amount[tid]
                if see_hit and w.tex_alpha[tid] is not None:
                    solid = w.tex_alpha[tid][v, u] > 0.5
            else:
                storey = np.clip(np.floor(z).astype(int), 0, len(stack) - 1)
                alb = np.zeros((len(rows), 3), np.float32)
                e = np.zeros(len(rows), np.float32)
                if see_hit:
                    solid = np.ones(len(rows), bool)
                for k in np.unique(storey):
                    m = storey == k
                    rgb, em = w.tex[stack[k]]
                    alb[m] = rgb[v[m], u]
                    if em is not None:
                        e[m] = em[v[m], u]
                    if see_hit and w.tex_alpha[stack[k]] is not None:
                        solid[m] = w.tex_alpha[stack[k]][v[m], u] > 0.5
                # a facade can change material per storey, so the amount varies down the column
                wall_amt = self.tex_amount[np.asarray(stack, np.int32)[storey]]
            if below > 1e-6:
                under = (z < -1e-6) & (depth[y0:y1, c] <= dist)
                if under.any():
                    solid = ~under if solid is None else solid & ~under
            if solid is not None and not solid.any():
                continue
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
            sun = 0.0
            if self.suns:
                nx, ny = (-math.copysign(1, rdx[c]), 0.0) if side == 0 else (0.0, -math.copysign(1, rdy[c]))
                sun = self.sun_at(np.full(len(rows), hx), np.full(len(rows), hy), z,
                                  lambda s_: s_['cos'] * max(0.0, nx * s_['ux'] + ny * s_['uy']))
            colr = self.shade(alb, np.repeat(dyn, len(rows), 0), self.fade_z(np.array([hx]), np.array([hy]), z),
                              np.full(len(rows), ed), e,
                              flash(rows, np.full(len(rows), c), np.full(len(rows), ed)), sun)
            gl = self._glow
            if solid is None:
                img[y0:y1, c] = colr
                emis[y0:y1, c] = gl if gl is not None else 0.0
                depth[y0:y1, c] = dist
            else:
                # holes in a fence write nothing, so whatever lies behind (and its depth) shows
                img[rows[solid], c] = colr[solid]
                emis[rows[solid], c] = gl[solid] if gl is not None else 0.0
                depth[rows[solid], c] = dist

    def _sprite_pass(self, f):
        """What stands in the world: sprites and cards (opaque, then translucent far to near), the
        wireframes between them, how much of each named sprite is seen, then glass."""
        cam, img, depth, camz, horizon, proj = f.cam, f.img, f.depth, f.camz, f.horizon, f.proj
        px, py, dx, dy, pl, plx, ply, rdx = f.px, f.py, f.dx, f.dy, f.pl, f.plx, f.ply, f.rdx
        rdy, rlen, flash = f.rdy, f.rlen, f.flash
        # --- sprites: opaque pass (writes depth), then translucent/additive far-to-near (no depth writes)
        inv = 1.0 / (plx * dy - dx * ply)
        defs = self.s.get('sprite_defs', {})
        placed = []
        self.anchors = {}
        for sp in (self.s.get('sprites', []) + self.w.scatter_sprites + self.w.fringe_sprites
                   + cam.get('extra_sprites', [])):
            sp = {**assets.sprite_defaults(sp['type'], defs), **sp}
            sp['type'] = assets.variant_name(sp, self.s)     # one of the prop's drawings, by where it stands
            if sp.get('glass') and int(sp.get('planes', 0)) <= 0:
                sp['planes'] = 1                  # a pane of glass is flat: it stands as a card
            sx, sy = float(sp['x']) - px, float(sp['y']) - py
            tx = inv * (dy * sx - dx * sy)
            ty = inv * (-ply * sx + plx * sy)
            if int(sp.get('planes', 0)) > 0:
                # a card can reach into view with its centre behind the camera
                reach = max(float(sp.get('length', 0.0)), float(sp.get('scale', 1.0)) * 2.0) / 2 + 0.5
                if ty > -reach:
                    placed.append((max(ty, 0.05), tx, sp))
            elif ty > 0.05:
                placed.append((ty, tx, sp))
        H, W = depth.shape
        for pn in self.s.get('panels', []) + self.w.panels:   # the flat parts of objects (objects.py)
            lift = self.w.base_z(float(pn['at'][0]), float(pn['at'][1])) if 'at' in pn else 0.0
            if lift:                                   # an object stands on the floor under it
                pn = dict(pn, o=pn['o'] + np.array([0.0, 0.0, lift]))
            corners = pn['o'] + np.array([[0, 0], [1, 0], [0, 1], [1, 1]], float) @ np.stack([pn['u'], pn['v']])
            sx, sy = corners[:, 0] - px, corners[:, 1] - py
            cty = inv * (-ply * sx + plx * sy)
            if (cty < 0.05).all():
                continue
            if (cty < 0.05).any():                     # it reaches behind the camera: look everywhere
                box = (0, H, 0, W)
            else:
                scx = (inv * (dy * sx - dx * sy) / cty + 1) * W / 2
                scy = horizon - (corners[:, 2] - camz) * proj / cty
                box = (max(0, int(math.floor(scy.min()))), min(H, int(math.ceil(scy.max())) + 1),
                       max(0, int(math.floor(scx.min()))), min(W, int(math.ceil(scx.max())) + 1))
                if box[1] <= box[0] or box[3] <= box[2]:
                    continue
            placed.append((max(float(cty.mean()), 0.05), 0.0,
                           {'_panel': pn, '_box': box, 'blend': pn.get('blend', 'alpha'),
                            'opacity': pn.get('opacity', 1.0), '_trans': bool(pn.get('translucent')),
                            '_bends': pn.get('refract') is not None}))
        # glass and the like: drawn over what is behind them, far to near, without writing depth
        translucent = lambda sp: (sp.get('blend', 'alpha') != 'alpha' or float(sp.get('opacity', 1)) < 1
                                  or sp.get('_trans', False))
        # panes of glass and crystals' facets look through to what is drawn before them: they go last
        seen_through = lambda sp: sp.get('glass') or sp.get('_bends')
        glass = sorted([p for p in placed if seen_through(p[2])], key=lambda s: -s[0])
        placed = [p for p in placed if not seen_through(p[2])]
        opaque = sorted([p for p in placed if not translucent(p[2])], key=lambda s: -s[0])
        trans = sorted([p for p in placed if translucent(p[2])], key=lambda s: -s[0])
        self._named = {}
        rays = (rdx, rdy, rlen)
        wired = list(self.s.get('wireframes', [])) + list(cam.get('extra_wireframes', []))
        for k, (ty, tx, sp) in enumerate(opaque + trans):
            if k == len(opaque) and wired:
                self._wire_pass(img, depth, wired, px, py, dx, dy, camz, horizon, proj, rlen)
            if '_panel' in sp:
                self._draw_panel(img, depth, sp['_panel'], sp['_box'], (px, py, camz), horizon, proj, flash,
                                 rays, translucent(sp))
            elif int(sp.get('planes', 0)) > 0:
                self._draw_planes(img, depth, ty, tx, sp, defs, horizon, proj, camz, flash, translucent(sp), rays)
            else:
                self._draw_sprite(img, depth, ty, tx, sp, defs, horizon, proj, camz, pl, flash, translucent(sp))
        if wired and not trans:
            self._wire_pass(img, depth, wired, px, py, dx, dy, camz, horizon, proj, rlen)
        self.sprite_stats = {}
        for sid, n in self._named.items():
            vis, lum = 0.0, 0.0
            if n['box'] is not None:                 # what is left once everything nearer is drawn
                y0_, y1_, x0_, x1_, solid = n['box']   # (glass comes after: a fish in a tank is seen)
                seen = solid & (depth[y0_:y1_, x0_:x1_] >= n['ty'] - 1e-3)
                vis = float(seen.sum())
                if vis:
                    lum = float(img[y0_:y1_, x0_:x1_][seen].mean())
            self.sprite_stats[sid] = {'visible': vis, 'area': n['area'], 'height': n['h'], 'brightness': lum}
        if glass:
            self.rays = {'px': px, 'py': py, 'rdx': rdx, 'rdy': rdy, 'rlen': rlen, 'horizon': horizon,
                         'proj': proj, 'camz': camz}
            self._glass_pass(img, depth, glass, defs, horizon, proj, camz, flash, rays)

    def _wire_pass(self, img, depth, wired, px, py, dx, dy, camz, horizon, proj, rlen):
        """The scene's wireframes (scripts/wires.py), drawn after the opaque sprites so that what is
        nearer hides them, and before the translucent ones, glass and reflections."""
        view = wires.View(px, py, dx, dy, camz, horizon, proj, self.W, self.H, rlen)
        wires.draw(img, depth, self._emis, view, wired, ss=self._ss,
                   fog_c=self.fog_c if self.vol is None else None, fog_d=self.fog_d, anchors=self.anchors)

    def _reflect(self, img, depth, refl, refl_depth, sky=None):
        """Mirror the frame into reflective floor pixels, column by column.

        A pixel that still shows the reflective floor it was drawn as (nothing nearer covered it)
        mirrors whatever stands just above its run in that column: a wall base, a boat on the
        water, a lamp post's foot, or the horizon for open water. Screen-space, so it can only
        mirror what is on screen - which at a grazing angle across water is nearly everything.
        A still mirror (`smear` under 1) is exact instead: see _still_mirror; `sky` is the frame's
        sky before anything was drawn over it, for the sky it mirrors from behind a floating thing.
        """
        H, W = depth.shape
        ss = max(1, W // self.W) if self.W else 1
        mask = (refl > 0) & (depth == refl_depth)
        if not mask.any():
            return img
        rows = np.arange(H)[:, None]
        # the last row above each pixel that is not part of its reflective run: the mirror line
        last = np.maximum.accumulate(np.where(mask, -1, rows * np.ones((1, W), int)), axis=0)
        src = 2 * last + 1 - rows
        behind = None
        if self.smear < 1.0:
            src, behind = self._still_mirror(depth, mask, refl_depth)
            if sky is None:
                behind = None
        # a ripple: rows shimmer sideways a pixel or two, more toward the camera
        amp = self.ripple * ss * (0.6 + 1.4 * np.clip((rows - H / 2) / (H / 2), 0, 1))
        cols = np.arange(W)[None, :]
        shift = np.round(amp * np.sin(rows * 0.9 / ss + cols * 0.07 / ss)).astype(int)
        sc = np.clip(cols + shift, 0, W - 1)
        ok = mask & (last >= 0)
        # a short vertical smear: real wet ground and water stretch reflections into streaks
        s0 = np.clip(src, 0, H - 1)
        if self.smear == 1.0:
            mirrored = (0.5 * img[s0, sc] + 0.25 * img[np.clip(s0 - 2 * ss, 0, H - 1), sc]
                        + 0.25 * img[np.clip(s0 + 2 * ss, 0, H - 1), sc])
        else:
            sm = min(2.0, max(0.0, self.smear)) * 0.25

            def at(r_):
                v = img[r_, sc]
                return v if behind is None else np.where(behind[..., None], sky[r_, sc], v)
            mirrored = ((1 - 2 * sm) * at(s0) + sm * at(np.clip(s0 - 2 * ss, 0, H - 1))
                        + sm * at(np.clip(s0 + 2 * ss, 0, H - 1)))
        # stronger at a grazing angle (far away), weaker looking straight down
        k = refl * (0.55 + 0.45 * (1 - np.exp(-np.maximum(refl_depth, 0) / 4.0)))
        # close to the camera the mirrored point is above the top of the frame; what is up there
        # is mostly sky, so those pixels take the top row's colour as a fainter sheen
        k = np.where(src < 0, k * 0.45, k)
        k = np.where(ok, np.clip(k, 0, 1), 0)[..., None]
        # lights glint: anything bright in the reflection comes through harder than the rest
        glint = np.maximum(mirrored - 0.45, 0) * 0.9
        return img * (1 - k) + (mirrored * 0.85 + glint) * k

    def _still_mirror(self, depth, mask, refl_depth):
        """The row each pixel of a still mirror shows. A mirror shows every point at its own depth as
        far below the water as it stands above it, so each thing is mirrored about its own foot - a
        figure wading, a mound on a dry bank past the water, a palace across the ice - and where
        nothing stands, the sky about the horizon. Each thing on screen is cast down into the water
        and the nearest kept; like the rest, it can only mirror what is on screen. Also returns where
        the sky so mirrored is hidden on screen by something standing in front of it (a whale over the
        flat): there the sky behind it is wanted."""
        if getattr(self, '_still_for', None) is depth:            # the emission pass reuses it
            return self._still_src
        H, W = depth.shape
        rows = np.arange(H)[:, None]
        src = np.repeat(np.round(2 * self._horizon - 1 - rows).astype(int), W, axis=1)
        hit = np.zeros((H, W), bool)
        # how high the eye stands over the water, from where the water is seen (it may lie sunken)
        lift = ((rows + 0.5 - self._horizon) * refl_depth / self._proj)[mask]
        if lift.size:
            lift = float(np.median(lift))
            ground = np.isfinite(depth) & (depth == self._plane_depth) & (rows + 0.5 > self._horizon)
            sy, sx = np.nonzero(np.isfinite(depth) & ~mask & ~ground)    # bare ground mirrors nothing
            d = depth[sy, sx]
            ty = np.floor(2 * (self._horizon + lift * self._proj / d) - sy - 0.5).astype(int)
            ok = (ty >= 0) & (ty < H)
            sy, sx, d, ty = sy[ok], sx[ok], d[ok], ty[ok]
            ok = mask[ty, sx] & (d >= refl_depth[ty, sx] * 0.999)    # only what stands past that water
            sy, sx, d, ty = sy[ok], sx[ok], d[ok], ty[ok]
            key = ty * W + sx
            order = np.lexsort((d, key))                             # by water pixel, the nearest first
            first = np.ones(len(order), bool)
            first[1:] = key[order][1:] != key[order][:-1]
            pick = order[first]
            src[ty[pick], sx[pick]] = sy[pick]
            hit[ty[pick], sx[pick]] = True
            # something sloping away in depth (a ceiling, a block's top) stretches as it is cast down,
            # leaving gaps a row or two high: they take the row between their neighbours'
            for gap in (1, 2):
                up, dn = np.zeros_like(hit), np.zeros_like(hit)
                up[gap:], dn[:-gap] = hit[:-gap], hit[gap:]
                su, sd = np.zeros_like(src), np.zeros_like(src)
                su[gap:], sd[:-gap] = src[:-gap], src[gap:]
                fill = mask & ~hit & up & dn & (np.abs(su - sd) <= 2 * gap + 2)
                src = np.where(fill, (su + sd) // 2, src)
                hit |= fill
        behind = mask & ~hit & np.isfinite(depth[np.clip(src, 0, H - 1), np.arange(W)[None, :]])
        self._still_for, self._still_src = depth, (src, behind)
        return src, behind

    def sprite_view(self, sp):
        """'back' when a sprite with a `facing` has its back to the camera (or `view` says so)."""
        v = sp.get('view')
        if v in ('front', 'back'):
            return v
        if 'facing' not in sp:
            return 'front'
        to_cam = math.degrees(math.atan2(self._py - float(sp['y']), self._px - float(sp['x'])))
        off = (to_cam - float(sp['facing']) + 180.0) % 360.0 - 180.0
        return 'back' if abs(off) > 90.0 else 'front'

    def _draw_sprite(self, img, depth, ty, tx, sp, defs, horizon, proj, camz, pl, flash, is_trans):
        W, H = self.W, self.H
        rgba, em = assets.get_sprite(sp['type'], defs, self.sprite_view(sp))
        th, tw = rgba.shape[:2]
        hs = float(sp.get('scale', 1.0))
        # a sprite rests on the surface under it: a boat on sunken water, a candle on an altar
        zb = float(sp.get('z', 0.0)) + self.w.base_z(float(sp['x']), float(sp['y']))
        ph = hs * proj / ty
        pw = ph * tw / th * float(sp.get('stretch', 1.0))
        scx = (tx / ty + 1) * W / 2  # screen centre column
        ytop = horizon - (zb + hs - camz) * proj / ty
        if 'id' in sp:
            self.anchors[sp['id']] = {'x': scx, 'top': ytop, 'w': pw, 'h': ph, 'depth': ty,
                                      'visible': -pw < scx < W + pw and ytop + ph > 0 and ytop < H}
            self._named[sp['id']] = {'ty': ty, 'h': ph, 'area': float((rgba[..., 3] > 0.5).mean()) * pw * ph,
                                     'box': None}
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
        if 'id' in sp:
            self._named[sp['id']]['box'] = (cy0, cy1, cx0, cx1, alpha > 0.5)
        if not mask.any():
            return
        dyn = sample_lm(self._lm_at(float(sp['x']), float(sp['y']), zb), self.lres,
                        np.array([float(sp['x'])]), np.array([float(sp['y'])]))[0]
        zz = (horizon - (rows + 0.5)) * ty / proj + camz
        Z = np.repeat(zz[:, None], len(cols), 1)
        ed = ty * math.hypot(1, tx / ty * pl)
        rr, cc = np.meshgrid(rows, cols, indexing='ij')
        emm = np.maximum(emb, 1.0 if sp.get('fullbright') else 0.0)
        tint = np.array(sp.get('tint', [1, 1, 1]), np.float32)
        sun = 0.0
        if self.suns:
            fx, fy = self._fx, self._fy
            sun = self.sun_at(np.full(Z.shape, float(sp['x'])), np.full(Z.shape, float(sp['y'])), Z,
                              lambda s_: s_['sin'] * 0.5 + s_['cos'] * 0.6 * max(0.2, -(fx * s_['ux'] + fy * s_['uy'])))
        colr = self.shade(block[..., :3] * tint, np.broadcast_to(dyn, block.shape[:2] + (3,)),
                          self.fade_z(np.array([float(sp['x'])]), np.array([float(sp['y'])]), Z),
                          np.full(Z.shape, ed), emm, flash(rr, cc, np.full(Z.shape, ed)), sun)
        sub = img[cy0:cy1, cx0:cx1]
        a = (alpha * mask)[..., None]
        gsub = self._emis[cy0:cy1, cx0:cx1]
        gl = self._glow if self._glow is not None else 0.0
        if sp.get('blend') == 'additive':
            sub += colr * a
            gsub += gl * a
        else:
            sub[:] = sub * (1 - a) + colr * a
            gsub[:] = gsub * (1 - a) + gl * a
        if not is_trans:
            dsub[mask] = ty
        aura = sp.get('aura')
        if aura:
            self._aura(img, depth, alpha * (ty < dsub), cx0, cy0, ty, aura, pw)

    plane_quads = staticmethod(plane_quads)

    def _glass_pass(self, img, depth, glass, defs, horizon, proj, camz, flash, rays):
        """Glass, after all the geometry and sprites, far to near. Each pane shows what is behind
        it - by default through the finished frame shrunk to half size and blown back up without
        smoothing, a cheap blur - tinted, and mixed with the pane's own faint reflection.

        Volumetric fog is laid over the finished frame at the depth of the glass, so it stops at
        the pane - right for a window onto space. A pane with `fog` lets it carry on behind: the
        water of a tank, the mist past a window. For those the frame without glass is fogged at
        its own depth, and each such pane leaves in self._glass_fix the difference between that,
        seen through the pane, and what fogging the pane at its own depth would give."""
        behind = {}
        fogged = None
        if self.vol is not None and any(glass_spec(sp['glass'])['fog'] for _, _, sp in glass if sp.get('glass')):
            self._march(depth, self._ss)
            H, W = depth.shape
            Ts, Ls = self._fog_px(np.arange(H)[:, None], np.arange(W)[None, :], depth)
            fogged = img * Ts[..., None] + Ls
            self._glass_fix = np.zeros_like(img)
        for ty, tx, sp in glass:
            if '_panel' in sp:                      # a crystal's facet: it bends what is behind it
                self._draw_panel(img, depth, sp['_panel'], sp['_box'], (self._px, self._py, camz), horizon, proj,
                                 flash, rays, False)
                behind.clear()                      # a pane nearer than it sees it
                continue
            g = glass_spec(sp['glass'])
            if g['blur'] not in behind:            # made once per blur, from the frame without glass
                k = 2 ** g['blur'] * getattr(self, '_ss', 1)
                blur = (lambda a: frost(a, k)) if g['blur'] > 0 else (lambda a: a.copy())
                behind[g['blur']] = (blur(img), None if fogged is None else blur(fogged))
            back, fogback = behind[g['blur']]
            self._draw_planes(img, depth, ty, tx, sp, defs, horizon, proj, camz, flash, False, rays,
                              glass=(g, back, fogback if g['fog'] else None))

    def _draw_planes(self, img, depth, ty, tx, sp, defs, horizon, proj, camz, flash, is_trans, rays, glass=None):
        """A planar sprite: each of its quads is drawn like a thin wall at the sprite stage.

        Every screen column intersects the quad on its own, so the image is foreshortened,
        depth-tested per pixel against everything drawn so far (and the other quads of the same
        cross), and lit by the light map and the sun at its own point along the card.
        """
        W, H = self.W, self.H
        rdx, rdy, rlen = rays
        px, py = self._px, self._py
        rgba, em = assets.get_sprite(sp['type'], defs, self.sprite_view(sp))
        th, tw = rgba.shape[:2]
        zb = float(sp.get('z', 0.0)) + self.w.base_z(float(sp['x']), float(sp['y']))
        hs = float(sp.get('scale', 1.0))
        u0 = float(sp.get('u0', 0.0))
        opacity = float(sp.get('opacity', 1.0))
        tint = np.array(sp.get('tint', [1, 1, 1]), np.float32)
        additive = sp.get('blend') == 'additive'
        named = 'id' in sp
        if named:
            ph = hs * proj / ty
            pw = ph * tw / th
            scx = (tx / ty + 1) * W / 2
            ytop = horizon - (zb + hs - camz) * proj / ty
            self.anchors[sp['id']] = {'x': scx, 'top': ytop, 'w': pw, 'h': ph, 'depth': ty,
                                      'visible': -pw < scx < W + pw and ytop + ph > 0 and ytop < H}
            self._named[sp['id']] = {'ty': ty, 'h': ph, 'area': float((rgba[..., 3] > 0.5).mean()) * pw * ph,
                                     'box': None}
            seen = np.zeros((H, W), bool)
        for x0, y0, x1, y1, rep_ in self.plane_quads(sp, rgba):
            ex, ey = x1 - x0, y1 - y0
            denom = rdx * ey - rdy * ex
            wx0, wy0 = x0 - px, y0 - py
            with np.errstate(divide='ignore', invalid='ignore'):
                t = (wx0 * ey - wy0 * ex) / denom          # depth along each column's ray
                s_ = (wx0 * rdy - wy0 * rdx) / denom       # where along the quad it lands, 0..1
            hit = (np.abs(denom) > 1e-9) & (t > 0.05) & (s_ >= 0) & (s_ <= 1)
            cols = np.nonzero(hit)[0]
            if cols.size == 0:
                continue
            t, s_ = t[cols], s_[cols]
            top = horizon - (zb + hs - camz) * proj / t
            bot = horizon - (zb - camz) * proj / t
            r0, r1 = max(0, int(math.floor(top.min()))), min(H, int(math.ceil(bot.max())))
            if r1 <= r0:
                continue
            rows = np.arange(r0, r1)
            v = (rows[:, None] + 0.5 - top[None, :]) / (bot - top)[None, :]
            inside = (v >= 0) & (v < 1)
            uu = u0 + s_ * rep_
            uu = ((uu - np.floor(uu)) * tw).astype(int).clip(0, tw - 1)
            if sp.get('flip'):
                uu = tw - 1 - uu
            vv = (v * th).astype(int).clip(0, th - 1)
            block = rgba[vv, uu[None, :]]
            alpha = block[..., 3] * opacity
            if sp.get('edge_fade'):             # seen almost edge on, it fades out rather than squeeze
                side = np.abs(denom[cols]) / (np.hypot(rdx[cols], rdy[cols]) * math.hypot(ex, ey))   # its
                alpha = alpha * np.clip((side - 0.15) / 0.2, 0, 1)[None, :]                         # picture
            if not is_trans:
                alpha = (alpha > 0.5).astype(np.float32)
            dsub = depth[r0:r1, cols]
            mask = inside & (alpha > 0.02) & (t[None, :] < dsub)
            rv = None
            if sp.get('reveal') and glass is None and not is_trans:
                rv = self._reveal(sp, rgba, (x0, y0, x1, y1, rep_), rows, cols, t, s_, v, vv, uu,
                                  inside & (block[..., 3] < 0.5) & (t[None, :] < dsub), dsub,
                                  horizon, proj, camz, flash, rays)
            if not mask.any() and rv is None:
                continue
            wx, wy = px + rdx[cols] * t, py + rdy[cols] * t
            dyn = sample_lm(self._lm_at(float(sp['x']), float(sp['y']), zb), self.lres, wx, wy)
            Z = (horizon - (rows[:, None] + 0.5)) * t[None, :] / proj + camz
            ed = np.broadcast_to((t * rlen[cols])[None, :], Z.shape)
            rr, cc = np.meshgrid(rows, cols, indexing='ij')
            emm = np.maximum(em[vv, uu[None, :]], 1.0 if sp.get('fullbright') else 0.0)
            sun = 0.0
            if self.suns:
                n_ = math.hypot(ex, ey) or 1.0
                nx, ny = -ey / n_, ex / n_
                # foliage cards take light on either face: a leaf lets the sun through
                sun = self.sun_at(np.broadcast_to(wx[None, :], Z.shape), np.broadcast_to(wy[None, :], Z.shape), Z,
                                  lambda s2: s2['sin'] * 0.5 + s2['cos'] * 0.6 * max(0.25, abs(nx * s2['ux'] + ny * s2['uy'])))
            colr = self.shade(block[..., :3] * tint, np.broadcast_to(dyn[None, :, :], block.shape[:2] + (3,)),
                              self.fade_z(wx, wy, Z),
                              ed, emm, flash(rr, cc, ed), sun)
            a = (alpha * mask)[..., None]
            sub = img[r0:r1, cols]
            if glass is not None:
                # light through the pane, tinted, under the pane's own reflection
                g, back, fogback = glass
                through = back[r0:r1, cols] * g['tint']
                colr = through * (1 - g['opacity']) + colr * g['opacity']
                if self._glass_fix is not None:
                    fix = 0.0
                    if fogback is not None:
                        # the fog behind the pane: what it lets through and adds, less what
                        # fogging the pane at its own depth will make of the view through it
                        Tg, Lg = self._fog_px(np.arange(r0, r1)[:, None], cols[None, :],
                                              np.broadcast_to(t[None, :], (r1 - r0, len(cols))))
                        fix = g['tint'] * (1 - g['opacity']) * (fogback[r0:r1, cols] - Lg
                                                                 - back[r0:r1, cols] * Tg[..., None])
                    self._glass_fix[r0:r1, cols] = self._glass_fix[r0:r1, cols] * (1 - a) + fix * a
            img[r0:r1, cols] = sub + colr * a if additive else sub * (1 - a) + colr * a
            gsub = self._emis[r0:r1, cols]
            if glass is not None:      # light from behind comes through the pane, tinted
                gl = gsub * glass[0]['tint'] * (1 - glass[0]['opacity'])
            else:
                gl = self._glow if self._glow is not None else 0.0
            self._emis[r0:r1, cols] = gsub + gl * a if additive else gsub * (1 - a) + gl * a
            if not is_trans:
                depth[r0:r1, cols] = np.where(mask, t[None, :], dsub)
            if rv is not None:
                ri, ci, rcol, rt = rv
                img[r0 + ri, cols[ci]] = rcol
                self._emis[r0 + ri, cols[ci]] = 0.0
                depth[r0 + ri, cols[ci]] = rt
            if named:
                seen[r0:r1, cols] |= mask & (alpha > 0.5)
        if named and seen.any():
            ys_, xs_ = np.nonzero(seen)
            y0_, y1_, x0_, x1_ = ys_.min(), ys_.max() + 1, xs_.min(), xs_.max() + 1
            self._named[sp['id']]['box'] = (y0_, y1_, x0_, x1_, seen[y0_:y1_, x0_:x1_])

    def _draw_panel(self, img, depth, pn, box, cam3, horizon, proj, flash, rays, is_trans):
        """One flat panel of an object (scripts/objects.py) at any angle - standing, lying or
        sloped - over the rows and columns of `box`.

        The panel is a parallelogram: its texture's top left corner at `o`, its columns running
        along `u` and its rows along `v`. Each pixel's ray meets the panel's plane on its own, so
        the panel is drawn in true perspective and depth-tested per pixel against everything drawn
        so far, the object's other panels included. It is lit as a wall is: by the light map on the
        side it is seen from, the sun or moon by the way that side faces, a face turned along y
        darker than one turned along x, the underside of a thing darker still. Seen from behind,
        its texture shows mirrored at `back` of its brightness - the inside of a box. A panel with
        `refract` is a crystal's facet, drawn with the glass: see _bend.
        """
        rdx, rdy, rlen = rays
        r0, r1, c0, c1 = box
        o, u, v = pn['o'], pn['u'], pn['v']
        rgba, em = pn['rgba'], pn['em']
        th, tw = rgba.shape[:2]
        cam3 = np.asarray(cam3, float)
        nf = np.cross(u, v)                                  # toward the side the texture reads from
                                                             # (x east, y south, z up)
        nn = float(nf @ nf)
        if nn < 1e-12:
            return
        front = float((cam3 - o) @ nf) > 0
        if not front and pn.get('cull'):
            return
        rows, cols = np.arange(r0, r1), np.arange(c0, c1)
        k = ((horizon - (rows + 0.5)) / proj)[:, None]       # height the ray climbs per unit of depth
        Rx, Ry = rdx[cols][None, :], rdy[cols][None, :]
        den = Rx * nf[0] + Ry * nf[1] + k * nf[2]
        with np.errstate(divide='ignore', invalid='ignore'):
            t = float((o - cam3) @ nf) / den                  # depth along each pixel's ray
            hx, hy, hz = cam3[0] + t * Rx, cam3[1] + t * Ry, cam3[2] + t * k
            d0, d1, d2 = hx - o[0], hy - o[1], hz - o[2]
            nv_, nu_ = np.cross(v, nf), np.cross(nf, u)       # where along u and along v, 0..1
            s = (d0 * nv_[0] + d1 * nv_[1] + d2 * nv_[2]) / nn
            w = (d0 * nu_[0] + d1 * nu_[1] + d2 * nu_[2]) / nn
            inside = np.isfinite(t) & (t > 0.05) & (s >= 0) & (s < 1) & (w >= 0) & (w < 1)
        if not inside.any():
            return
        uu = (np.where(inside, s, 0.0) * tw).astype(int).clip(0, tw - 1)
        vv = (np.where(inside, w, 0.0) * th).astype(int).clip(0, th - 1)
        t = np.where(inside, t, np.inf)
        block = rgba[vv, uu]
        alpha = block[..., 3] * float(pn.get('opacity', 1.0))
        bends = pn.get('refract') is not None             # a crystal's facet: alpha is how much of it shows
        if not is_trans and not bends:
            alpha = (alpha > 0.5).astype(np.float32)
        dsub = depth[r0:r1, c0:c1]
        mask = inside & (alpha > 0.02) & (t < dsub)
        if not mask.any():
            return
        n = nf / math.sqrt(nn) * (1 if front else -1)         # the normal of the side seen
        flat = n[0] ** 2 + n[1] ** 2
        side = 0.78 + 0.22 * n[0] ** 2 / flat if flat > 1e-9 else 1.0
        fac = side * flat + (1.0 if n[2] >= 0 else 0.62) * n[2] ** 2
        if not front:
            fac *= float(pn.get('back', 0.6))
        hx, hy, hz = (np.where(inside, q, 0.0) for q in (hx, hy, hz))
        ed = np.where(inside, t * rlen[cols][None, :], 0.0)
        ax, ay, az = pn.get('at', o)
        dyn = sample_lm(self._lm_at(float(ax), float(ay), float(az)), self.lres, hx + n[0] * 0.04, hy + n[1] * 0.04)
        if pn.get('dyn') is not None:       # the lamps' light is mapped on the floor: a roof's slope over
            dyn = dyn * float(pn['dyn'])    # them takes little of it
        sun = 0.0
        if self.suns:
            sun = self.sun_at(hx, hy, hz, lambda s2: s2['sin'] * max(0.0, n[2])
                              + s2['cos'] * max(0.0, n[0] * s2['ux'] + n[1] * s2['uy']))
        if pn.get('fill'):                  # light from the sky and the ground on what the sun misses,
            sun = sun + float(pn['fill']) * float(np.mean(self.ambient))   # as much more as the ambient times this
        rr, cc = np.meshgrid(rows, cols, indexing='ij')
        emm = np.maximum(em[vv, uu], 1.0 if pn.get('fullbright') else 0.0)
        tint = np.array(pn.get('tint', [1, 1, 1]), np.float32)
        colr = self.shade(block[..., :3] * (fac * tint), dyn, self.fade_z(hx, hy, hz), ed, emm,
                          flash(rr, cc, ed), sun)
        seen = self._portal_frames.get(id(pn['portal'])) if pn.get('portal') is not None else None
        if seen is not None:                 # a portal: the view from its far side, through this scene's air
            colr, glow = seen[0][r0:r1, c0:c1], seen[1][r0:r1, c0:c1]
            if self.fog_c is not None and self.vol is None:
                k = (1 - np.exp(-self.fog_d * ed))[..., None]
                colr, glow = colr * (1 - k) + self.fog_c[None, None, :] * k, glow * (1 - k)
            self._glow = glow
        if bends:
            self._bend(img, depth, pn, n, box, t, mask, alpha, colr, cam3, proj)
            return
        a = (alpha * mask)[..., None]
        sub = img[r0:r1, c0:c1]
        additive = pn.get('blend') == 'additive'
        img[r0:r1, c0:c1] = sub + colr * a if additive else sub * (1 - a) + colr * a
        gsub = self._emis[r0:r1, c0:c1]
        gl = self._glow if self._glow is not None else 0.0
        self._emis[r0:r1, c0:c1] = gsub + gl * a if additive else gsub * (1 - a) + gl * a
        if not is_trans:
            depth[r0:r1, c0:c1] = np.where(mask, t, dsub)

    def _bend(self, img, depth, pn, n, box, t, mask, alpha, colr, cam3, proj):
        """A crystal's facet - a panel with `refract` - drawn over what is behind it, bent.

        The whole facet takes one shift: `refract` units at the facet, along the way it is turned
        across the line of sight (a facet turned left shows what lies to the right, as a lens does),
        so it shows one coherent piece of the frame drawn so far, displaced, and its neighbours show
        other pieces - a cut stone. Drawn far to near, a crystal behind it shows through it too. What
        it lets through is tinted by `filter` and split into its colours by `disperse` (red bent a
        little further, blue a little less), and the facet's own lit surface lies over that by its
        texture's alpha - so each facet is as clear or as milky as its texture makes it. A shift that
        would land on something nearer than the facet looks straight through instead."""
        r0, r1, c0, c1 = box
        H, W = depth.shape
        rows, cols = np.arange(r0, r1)[:, None], np.arange(c0, c1)[None, :]
        mid = np.asarray(pn['o'], float) + 0.5 * (np.asarray(pn['u'], float) + np.asarray(pn['v'], float))
        sight = mid - np.asarray(cam3, float)
        sight /= max(np.linalg.norm(sight), 1e-9)
        tilt = n - (n @ sight) * sight                         # its turn across the line of sight
        k = float(pn['refract']) * proj / max(float(np.median(t[mask])), 0.05)
        sx, sy = -k * (tilt[0] * -self._fy + tilt[1] * self._fx), k * tilt[2]   # rows run down the frame
        disp = float(pn.get('disperse', 0.0))
        direct, glowing = img[r0:r1, c0:c1], self._emis[r0:r1, c0:c1]
        seen, glow = np.empty_like(direct), np.empty_like(direct)
        for ch, f in enumerate((1 + disp, 1.0, 1 - disp)):
            rr = np.clip(rows + int(round(sy * f)), 0, H - 1)
            cc = np.clip(cols + int(round(sx * f)), 0, W - 1)
            ok = depth[rr, cc] > t                             # only what is behind the facet
            seen[..., ch] = np.where(ok, img[rr, cc, ch], direct[..., ch])
            glow[..., ch] = np.where(ok, self._emis[rr, cc, ch], glowing[..., ch])
        filt = np.asarray(pn.get('filter', [1.0, 1.0, 1.0]), np.float32)
        a, m = (alpha * mask)[..., None], mask[..., None]
        own = self._glow if self._glow is not None else 0.0
        img[r0:r1, c0:c1] = np.where(m, seen * filt * (1 - a) + colr * a, direct)
        self._emis[r0:r1, c0:c1] = np.where(m, glow * filt * (1 - a) + own * a, glowing)
        depth[r0:r1, c0:c1] = np.where(mask, t, depth[r0:r1, c0:c1])

    def _reveal(self, sp, rgba, quad, rows, cols, t, s_, v, vv, uu, cand, dsub, horizon, proj, camz, flash, rays):
        """The inner sides of a card's openings, for a card with `reveal` (a depth): the card is
        drawn as a slab that thick, so through an opening seen at an angle its far side shows -
        the jamb, the head over it, the sill under it - not whatever stands behind the wall.

        A ray going in through a see-through texel runs on behind the card; if it leaves that
        opening (the run of clear texels it is in, across and down) before it is `reveal` deep,
        it stops on that side. The side takes its colour from the card just past the opening's
        edge, read on round the corner as brickwork turns it, darker the deeper it goes, and its
        light from its own facing: a jamb turned to the sun is lit where the light could come in
        through the opening, and the head and the wall's edges shade the rest. Returns (rows,
        columns, colours, depths) of the pixels it covers, or None.
        """
        ri, ci = np.nonzero(cand)
        if ri.size == 0:
            return None
        x0, y0, x1, y1, rep_ = quad
        rdx, rdy, rlen = rays
        th, tw = rgba.shape[:2]
        hs = float(sp.get('scale', 1.0))
        deep = float(sp['reveal'])
        if id(rgba) not in self._runs or self._runs[id(rgba)][0] is not rgba:
            self._runs[id(rgba)] = (rgba, hole_runs(rgba[..., 3]))
        lft, rgt, top, bot = (r_[vv[ri, ci], uu[ci]] for r_ in self._runs[id(rgba)][1])
        lq = math.hypot(x1 - x0, y1 - y0) or 1.0
        ax, ay = (x1 - x0) / lq, (y1 - y0) / lq           # along the card
        nx, ny = -ay, ax                                   # across it
        c = cols[ci]
        rx, ry = rdx[c], rdy[c]
        k = np.abs(rx * nx + ry * ny)                      # how fast the ray goes in, per unit of t
        flip = -1.0 if sp.get('flip') else 1.0
        tpu = tw * rep_ / lq                               # texels per unit along the card
        du = (rx * ax + ry * ay) * tpu * flip              # texels across, per unit of t
        su = float(sp.get('u0', 0.0)) + s_[ci] * rep_
        uc = (su - np.floor(su)) * tw
        if flip < 0:
            uc = tw - uc
        vc = v[ri, ci] * th
        dv = -(horizon - (rows[ri] + 0.5)) / proj * th / hs   # texels down, per unit of t
        with np.errstate(divide='ignore', invalid='ignore'):
            d_u = np.where(du > 0, (rgt - uc) / du, np.where(du < 0, (lft - uc) / du, np.inf))
            d_v = np.where(dv > 0, (bot - vc) / dv, np.where(dv < 0, (top - vc) / dv, np.inf))
        d = np.maximum(np.minimum(d_u, d_v), 0.0)
        tt = t[ci] + d
        keep = np.nonzero((d * k < deep) & (tt < dsub[ri, ci]))[0]
        if keep.size == 0:
            return None
        ri, ci, c, rx, ry, k, du, dv, d, tt = (a_[keep] for a_ in (ri, ci, c, rx, ry, k, du, dv, d, tt))
        uc, vc, d_u, d_v, lft, rgt, top, bot = (a_[keep] for a_ in (uc, vc, d_u, d_v, lft, rgt, top, bot))
        jamb = d_u <= d_v
        e = d * k                                          # how deep in the side is met
        uh, vh = uc + du * d, vc + dv * d
        fold = np.floor(e * th / hs).astype(int)
        tu = np.where(jamb, np.where(du > 0, rgt + fold, lft - 1 - fold), np.floor(uh).astype(int))
        tv = np.where(jamb, np.floor(vh).astype(int), np.where(dv < 0, top - 1 - fold, bot + fold))
        alb = rgba[tv.clip(0, th - 1), tu.clip(0, tw - 1), :3] * (1 - 0.4 * e / deep)[:, None]
        wx, wy = self._px + rx * tt, self._py + ry * tt
        Z = (horizon - (rows[ri] + 0.5)) * tt / proj + camz
        ed = tt * rlen[c]
        sun = 0.0
        if self.suns:
            go = np.sign(rx * ax + ry * ay)                # the way the ray runs along the card
            cam = -np.sign(rx * nx + ry * ny)              # the side of the card the camera is on

            def lam(s2):
                # a jamb faces back the way the ray came, a sill up, a head down (no sun)
                face = np.where(jamb, s2['cos'] * np.maximum(0.0, -go * (ax * s2['ux'] + ay * s2['uy'])),
                                np.where(dv > 0, s2['sin'], 0.0))
                # follow the light back out to the face of the card: did it come in by this opening?
                out = s2['cos'] * cam * (nx * s2['ux'] + ny * s2['uy'])
                back = e / np.maximum(out, 1e-6)
                uw = uh + s2['cos'] * (ax * s2['ux'] + ay * s2['uy']) * tpu * flip * back
                vw = vh - s2['sin'] * back * th / hs
                return face * ((out > 1e-6) & (uw >= lft) & (uw <= rgt) & (vw >= top) & (vw <= bot))
            sun = self.sun_at(wx, wy, Z, lam)
        col = self.shade(alb, sample_lm(self.lm, self.lres, wx, wy), self.fade_z(wx, wy, Z), ed, None,
                         flash(rows[ri], c, ed), sun)
        return ri, ci, col, tt

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
        self._emis[max(0, y0):y1, max(0, x0):x1] += g[..., None] * c * vis



# ------------------------------------------------------------------ output

def finish(img, scene, effects=(), seed=0, ref=None):
    """Palette quantise (ordered dither), nearest-neighbour upscale, then display-stage effects.
    `ref` is the frame without its lens effects, which the palette is chosen from (Renderer.palette_ref)."""
    effects = list(effects)
    spec, levels = post.palette_spec(effects, scene)
    arr = post.quantize(img, spec, float(scene.get('dither', 1.0)), levels, ref)
    scale = int(scene.get('scale', 3))
    pim = Image.fromarray(arr, 'RGB')
    out = np.asarray(pim.resize((pim.width * scale, pim.height * scale), Image.NEAREST))
    out = post.apply_display(out, effects, {'scale': scale, 'seed': seed})
    return Image.fromarray(out)


def prepare_shot(scene, cam):
    """Per-shot adjustments: held lights from viewmodels (lantern, torch) and the flashlight item; a shot's
    `time` of day goes into its overrides."""
    cam = dict(cam)
    if 'time' in cam:
        cam['overrides'] = {**cam.get('overrides', {}), 'time': cam.pop('time')}
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
        if ov.get('fire') and v.get('fire_light'):        # a shot lights the room for an instant
            a = math.radians(float(cam.get('angle', 0)))
            extra.append({'x': cam['x'] + 0.4 * math.cos(a), 'y': cam['y'] + 0.4 * math.sin(a), 'z': 0.5,
                          'shadows': False, **v['fire_light']})
    if extra:
        ovr = dict(cam.get('overrides', {}))
        ovr['lights'] = list(ovr.get('lights', scene.get('lights', []))) + extra
        cam['overrides'] = ovr
    return cam


def render_shot(scene, i, base=None, report=None):
    """Render shot `i` (0-based) of a scene to a finished PIL image.

    `base` is an optional (World, Renderer) pair for the scene as written; shots without
    `overrides` reuse it, so a many-shot scene builds its lightmap and scatter once.
    """
    shots = scene.get('shots') or [scene['camera']]
    cam = prepare_shot(scene, merge_camera(scene, shots[i]))
    if cam.get('overrides'):
        sc = shot_scene(scene, cam, shots[i])
        rr = Renderer(World(sc), sc)
    else:
        if base is None:
            w = World(scene)
            base = (w, Renderer(w, scene))
        rr = base[1]
    frame = rr.render(cam)
    if report is not None:
        report.extend(rr.last_report)
    return finish(frame, {**scene, **cam.get('overrides', {})}, rr.last_effects, i, rr.palette_ref)


def shot_scene(scene, cam, shot):
    """The scene as a shot sees it: the shot's `overrides` laid over it and the whole expanded - its prefabs,
    objects and time of day (prefabs.expand) - the keys the shot itself overrides beside a `time` staying as the
    shot gives them."""
    return prefabs.expand({**scene, **cam.get('overrides', {})}, keep=set(shot.get('overrides') or {}) - {'time'})


def save_png(im, path):
    """Save an image as PNG: as an 8-bit palette image when it has 256 colours or fewer - every frame
    the palette pass finished does - which keeps every pixel exactly and takes about half the bytes
    of RGB; otherwise (a display effect after the palette, a downscaled sheet) as RGB."""
    rgb = im.convert('RGB')
    colours = rgb.getcolors(256)
    if colours is None:
        rgb.save(path, optimize=True)
        return
    pal = np.array([c for _, c in colours], np.int32)
    a = np.asarray(rgb).astype(np.int32)
    keys = (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]
    pk = (pal[:, 0] << 16) | (pal[:, 1] << 8) | pal[:, 2]
    order = np.argsort(pk)
    out = Image.fromarray(order[np.searchsorted(pk[order], keys)].astype(np.uint8), 'P')
    out.putpalette(pal.astype(np.uint8).ravel().tolist())
    out.save(path, optimize=True)


def draw_map(world, scene, cams, path, cell=24):
    """Top-down layout check: walls by height, floors by texture tint, lights, decals, scattered
    props (small olive dots), placed sprites (green squares) and each camera's view cone."""
    scene = world.scene                    # with its prefabs placed
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
        if L.get('type', 'point') != 'point':
            continue
        lx, ly = L['x'] * cell, L['y'] * cell
        c = tuple(int(min(1, v) * 255) for v in L.get('color', [1, 0.85, 0.6]))
        r = L.get('radius', 4) * cell
        d.ellipse([lx - r, ly - r, lx + r, ly + r], outline=tuple(v // 3 for v in c))
        d.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=c)
    for dcl in world.floor_decals:
        hw, hh = dcl['size'] * cell / 2, dcl['size'] * dcl['dh'] / dcl['dw'] * cell / 2
        dx_, dy_ = dcl['x'] * cell, dcl['y'] * cell
        d.rectangle([dx_ - hw, dy_ - hh, dx_ + hw, dy_ + hh], outline=(150, 118, 84))
    # fringe and scatter first, so the sprites an author placed by hand stay readable on top
    defs = scene.get('sprite_defs', {})

    def planes(sp, colour):
        sp = {**assets.sprite_defaults(sp['type'], defs), **sp}
        if int(sp.get('planes', 0)) <= 0:
            return False
        for x0, y0, x1, y1, _ in Renderer.plane_quads(sp, assets.get_sprite(sp['type'], defs)[0]):
            d.line([x0 * cell, y0 * cell, x1 * cell, y1 * cell], fill=colour)
        return True
    for sp in world.fringe_sprites:
        planes(sp, (64, 110, 60))
    for sp in world.scatter_sprites:
        if not planes(sp, (120, 132, 84)):
            sx, sy = sp['x'] * cell, sp['y'] * cell
            d.rectangle([sx - 1, sy - 1, sx + 1, sy + 1], fill=(120, 132, 84))
    for sp in scene.get('sprites', []):
        planes(sp, (80, 200, 120))
        sx, sy = sp['x'] * cell, sp['y'] * cell
        d.rectangle([sx - 2, sy - 2, sx + 2, sy + 2], fill=(80, 200, 120))
    for spec in scene.get('wireframes', []):
        v, e, _ = wires.build(spec)
        col = tuple(int(min(1, x) * 255) for x in spec.get('color', wires.DEFAULT_COLOR))
        for a, b in e:
            d.line([v[a, 0] * cell, v[a, 1] * cell, v[b, 0] * cell, v[b, 1] * cell], fill=col)
    for i, c in enumerate(cams):
        cx, cy = c['x'] * cell, c['y'] * cell
        a = math.radians(c.get('angle', 0))
        f = math.radians(c.get('fov', 66)) / 2
        L = 5 * cell
        for s in (-1, 1):
            d.line([cx, cy, cx + L * math.cos(a + s * f), cy + L * math.sin(a + s * f)], fill=(120, 160, 255))
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(80, 140, 255))
        d.text((cx + 6, cy - 6), str(i + 1), fill=(255, 255, 255))
    save_png(im, path)


# Fog keys that switch on the volumetric pass (see Renderer._atmosphere).
FOG_VOLUME_KEYS = ('height', 'ground', 'noise', 'scale', 'glow', 'shafts', 'steps', 'distance', 'anisotropy')

# Every key the renderer reads. Anything else is ignored, which for a hand- or LLM-written file
# almost always means a typo ("ligths", "sprits") that silently drops part of the scene.
SCENE_KEYS = {
    'map', 'legend', 'default', 'camera', 'shots', 'resolution', 'scale', 'ceiling_height', 'sky',
    'ambient', 'lights', 'fog', 'fog_sky', 'sprites', 'sprite_defs', 'flashlight', 'light_levels',
    'scatter', 'grime', 'grime_debris', 'grime_decals', 'surface_noise', 'decals', 'decal_defs',
    'palette', 'auto_levels', 'dither', 'scanlines', 'overbright', 'lightmap_res', 'max_distance',
    'supersample', 'overlays', 'ui', 'post', 'icon_defs', 'viewmodel_defs', 'seed',
    'skyline', 'contact_shadows', 'heights', 'height_unit', 'reflections', 'sky_objects', 'wet',
    'prefabs', 'prefab_defs', 'wireframes', 'objects', 'time',
    'title', 'description', 'notes',  # free-form metadata, never read
}
SHOT_KEYS = {'x', 'y', 'angle', 'look_at', 'fov', 'height', 'pitch', 'flashlight', 'overlays', 'overrides',
             'post', 'scanlines', 'seed', 'supersample', 'extra_sprites', 'extra_wireframes', 'time', 'title',
             'description', 'notes'}
CELL_KEYS = {'wall', 'h', 'top', 'floor', 'ceil', 'drop', 'reflect', 'side', 'fringe', 'facade', 'glazed', 'cliff'}
ASSET_EXTS = ('.png', '.ttf', '.otf', '.json')     # a .json: another scene, that a portal or a screen shows


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
    check(scene.get('time'), daylight.SPEC_KEYS, 'time')
    check(scene.get('camera'), SHOT_KEYS, 'camera')
    for i, shot in enumerate(scene.get('shots') or []):
        check(shot, SHOT_KEYS, f'shot {i + 1}')
        if isinstance(shot, dict):
            check(shot.get('overrides'), SCENE_KEYS, f'shot {i + 1} overrides')
            for t in (shot.get('time'), (shot.get('overrides') or {}).get('time')):
                check(t, daylight.SPEC_KEYS, f'shot {i + 1} time')
    for ch, spec in (scene.get('legend') or {}).items():
        check(spec, CELL_KEYS, f'legend {ch!r}')
    for i, pl in enumerate(scene.get('prefabs') or []):
        check(pl, prefabs.PLACEMENT_KEYS, f'prefab {i + 1}')
    for i, pl in enumerate(scene.get('objects') or []):
        check(pl, prefabs.objects.PLACEMENT_KEYS, f'object {i + 1}')
    for i, wf in enumerate(scene.get('wireframes') or []):
        check(wf, wires.SPEC_KEYS, f'wireframe {i + 1}')
    for i, shot in enumerate(scene.get('shots') or []):
        for j, wf in enumerate((shot.get('extra_wireframes') or []) if isinstance(shot, dict) else []):
            check(wf, wires.SPEC_KEYS, f'shot {i + 1} wireframe {j + 1}')
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
        c = merge_camera(scene, cam)
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
        notes = []
        img = render_shot(scene, i, base_pair, notes)
        for note in notes:
            print(f'warning: shot {i + 1}: {note}', file=sys.stderr)
        save_png(img, path)
        outs.append((path, img))
        print(path)
    if args.map:
        mp = base + '_map.png'
        draw_map(world, scene, [merge_camera(scene, c) for c in shots], mp)
        print(mp)
    if args.sheet and len(outs) > 1:
        w, h = outs[0][1].size
        cols = 2
        rows = (len(outs) + 1) // 2
        sheet = Image.new('RGB', (w * cols + 8 * (cols - 1), h * rows + 8 * (rows - 1)), (0, 0, 0))
        for k, (_, im) in enumerate(outs):
            sheet.paste(im, ((k % cols) * (w + 8), (k // cols) * (h + 8)))
        sp = base + '_sheet.png'
        save_png(sheet, sp)
        print(sp)


if __name__ == '__main__':
    main()

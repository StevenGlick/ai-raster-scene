"""Small 3D models rendered straight to pixel art.

A model is rounded primitives - spheres, ellipsoids, round cones (a capsule tapering from one radius to
another: a finger bone, a haft), cylinders and boxes - combined as signed distance fields: parts in one
blend group melt smoothly into each other (fingers growing out of a hand), groups meet with a hard edge.
It is ray-marched from the eye through each pixel of a canvas, lit from one direction with soft ambient
occlusion and a rim of light at the silhouette, and painted onto colour ramps with ordered dithering;
a dark line is drawn wherever a part passes in front of another, and an outline round the whole - so it
reads as the rest of the pixel art does, but with true perspective and true occlusion. It suits things
whose shape must hold from a particular angle, which stamping 2D shapes cannot promise: a hand round a
gun seen from the shooter's eye (held.py).

Camera space: the eye at the origin, x to the right, y down, z forward; units are metres. A canvas is a
window onto a 320x200 screen with a horizontal field of view `fov`.
"""
import math

import numpy as np

from pixelart import outline_sprite

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16
SCREEN = (320, 200)


def _v(x):
    return np.asarray(x, np.float64)


def _dot(a, b):
    return np.sum(a * b, axis=-1)


def _len(a):
    return np.sqrt(np.sum(a * a, axis=-1))


def unit(v):
    v = _v(v)
    return v / np.linalg.norm(v)


# ------------------------------------------------------------------ shapes (signed distances, p is (N, 3))

def sd_sphere(p, c, r):
    return _len(p - _v(c)) - r


def sd_ellipsoid(p, c, r, rot=None):
    """An ellipsoid with radii r, along the rows of `rot` if given (an orthonormal 3x3)."""
    q = p - _v(c)
    if rot is not None:
        q = q @ np.asarray(rot).T
    q = q / _v(r)
    k0 = _len(q)
    k1 = _len(q / _v(r))
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def sd_round_cone(p, a, b, r1, r2):
    """A capsule from a (radius r1) to b (radius r2)."""
    a, b = _v(a), _v(b)
    ba = b - a
    l2 = float(ba @ ba)
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pa = p - a
    y = pa @ ba
    z = y - l2
    w = pa * l2 - np.outer(y, ba)
    x2 = _dot(w, w)
    y2 = y * y * l2
    z2 = z * z * l2
    k = math.copysign(1.0, rr) * rr * rr * x2 if rr != 0 else np.zeros_like(x2)
    d1 = np.sqrt(x2 + z2) * il2 - r2
    d2 = np.sqrt(x2 + y2) * il2 - r1
    d3 = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d1, np.where(np.sign(y) * a2 * y2 < k, d2, d3))


def sd_cylinder(p, a, b, r, round_=0.0):
    """A capped cylinder from a to b, its edges rounded by `round_`."""
    a, b = _v(a), _v(b)
    r = r - round_
    ba = b - a
    pa = p - a
    baba = float(ba @ ba)
    paba = pa @ ba
    x = _len(pa * baba - np.outer(paba, ba)) - r * baba
    y = np.abs(paba - baba * 0.5) - baba * 0.5
    x2 = x * x
    y2 = y * y * baba
    inside = np.maximum(x, y) < 0
    d = np.where(inside, -np.minimum(x2, y2), np.where(x > 0, x2, 0) + np.where(y > 0, y2, 0))
    return np.sign(d) * np.sqrt(np.abs(d)) / baba - round_


def sd_box(p, c, half, rot=None, round_=0.0):
    """A box centred at c with half-sizes `half` along the rows of `rot`, its edges rounded by `round_`."""
    q = p - _v(c)
    if rot is not None:
        q = q @ np.asarray(rot).T
    q = np.abs(q) - (_v(half) - round_)
    return _len(np.maximum(q, 0)) + np.minimum(np.max(q, axis=-1), 0) - round_


# ------------------------------------------------------------------ frames

def frame(fwd, up_hint=(0, -1, 0)):
    """An orthonormal frame (right, up, forward) with `forward` along fwd, in camera space."""
    f = unit(fwd)
    r = np.cross(f, _v(up_hint))
    if np.linalg.norm(r) < 1e-6:
        r = np.cross(f, _v((0, 0, 1)))
    r /= np.linalg.norm(r)
    return np.stack([r, np.cross(r, f), f])


class Frame:
    """Coordinates local to an object: x to its right, y up, z forward, from `origin` facing `fwd`."""

    def __init__(self, origin, fwd, up_hint=(0, -1, 0)):
        self.o = _v(origin)
        self.r, self.u, self.f = frame(fwd, up_hint)

    def P(self, x, y, z):
        return self.o + self.r * x + self.u * y + self.f * z

    def D(self, x, y, z):
        return unit(self.r * x + self.u * y + self.f * z)

    def rot(self, x_axis, y_axis):
        """Rows for an oriented box or ellipsoid whose local x and y are these (local) directions."""
        a = self.D(*x_axis)
        b = self.D(*y_axis)
        b = unit(b - a * (a @ b))
        return np.stack([a, b, np.cross(a, b)])


def screen_point(sx, sy, depth, fov=70.0, screen=SCREEN):
    """The camera-space point `depth` metres ahead that lands on screen pixel (sx, sy)."""
    sw, sh = screen
    t = math.tan(math.radians(fov) / 2)
    return np.array([(sx - sw / 2) / (sw / 2) * t * depth, (sy - sh / 2) / (sw / 2) * t * depth, depth])


# ------------------------------------------------------------------ the model

def _smin(a, b, k):
    """A smooth union of two distances, melting over a width k."""
    h = np.clip(0.5 + 0.5 * (a - b) / k, 0, 1)
    return a * (1 - h) + b * h - k * h * (1 - h)


class Model:
    """Parts, each with a material; the parts of one blend group melt together (`group(name, k)`, k the
    width of the blend in metres), and groups union with a hard edge - or melt into another group as a
    whole (`into`), so fingers can stay apart from each other and still grow out of the hand."""

    def __init__(self):
        self.parts = []
        self.blend = {}
        self.into = {}

    def add(self, fn, *args, mat=0, group=None, **kw):
        self.parts.append((fn, args, kw, mat, group))
        return self

    def group(self, name, k, into=None, k_into=0.0):
        self.blend[name] = k
        if into is not None:
            self.into[name] = (into, k_into)

    def field(self, p):
        """Distance to the model and the material of the nearest part, for points p (N, 3)."""
        groups = {}
        best_d = np.full(len(p), 1e9)
        best_m = np.zeros(len(p), int)
        for i, (fn, args, kw, mat, g) in enumerate(self.parts):
            d = fn(p, *args, **kw)
            best_m = np.where(d < best_d, mat, best_m)
            best_d = np.minimum(best_d, d)
            key = g if g is not None else ('part', i)
            if key in groups:
                k = self.blend.get(g, 0.0)
                groups[key] = _smin(d, groups[key], k) if k > 0 else np.minimum(groups[key], d)
            else:
                groups[key] = d
        for g, (parent, k) in self.into.items():          # whole groups melting into another
            if g in groups and parent in groups:
                d = groups.pop(g)
                groups[parent] = _smin(d, groups[parent], k) if k > 0 else np.minimum(groups[parent], d)
        return np.min(np.stack(list(groups.values())), axis=0), best_m


# ------------------------------------------------------------------ rendering

def rays(w, h, ox, oy, fov=70.0, screen=SCREEN):
    """Unit ray directions (h*w, 3) through the pixel centres of a w x h canvas whose top left is at
    (ox, oy) on the screen."""
    sw, sh = screen
    t = math.tan(math.radians(fov) / 2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    sx, sy = ox + xx + 0.5, oy + yy + 0.5
    d = np.stack([(sx - sw / 2) / (sw / 2) * t, (sy - sh / 2) / (sw / 2) * t, np.ones_like(sx)], -1).reshape(-1, 3)
    return d / _len(d)[:, None]


def look_rays(eye, target, w, h, fov=40.0):
    """Origins and directions through a w x h canvas for a camera at `eye` looking at `target` - for
    seeing a model from the side while building it."""
    R = frame(_v(target) - _v(eye))
    t = math.tan(math.radians(fov) / 2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    u = ((xx + 0.5) / w * 2 - 1) * t
    v = ((yy + 0.5) / w * 2 - h / w) * t
    d = (u[..., None] * R[0] - v[..., None] * R[1] + R[2]).reshape(-1, 3)
    return np.repeat(_v(eye)[None, :], len(d), 0), d / _len(d)[:, None]


def render(model, w, h, ramps, origin=(0, 0), fov=70.0, camera=None, light=(-0.4, -0.75, -0.5), glow=(),
           dither=0.35, outline=0.5, crease=0.025, crease_dark=0.55, ambient=0.2, diffuse=0.78, rim=0.18,
           ao=0.6, steps=96, tmax=3.0):
    """Ray-march `model` through a w x h canvas at `origin` on the screen (or along `camera`, a pair of
    origins and directions from look_rays). Each material m is painted on ramps[m]; those in `glow` emit.
    `light` points toward the light (camera space). Returns RGBA (h, w, 4) and an emission mask (h, w)."""
    if camera is None:
        d = rays(w, h, origin[0], origin[1], fov)
        o = np.zeros_like(d)
    else:
        o, d = camera
    n = len(d)
    t = np.full(n, 0.05)
    hit = np.zeros(n, bool)
    alive = np.ones(n, bool)
    for _ in range(steps):
        idx = np.nonzero(alive)[0]
        if not len(idx):
            break
        dist, _ = model.field(o[idx] + d[idx] * t[idx, None])
        t[idx] += dist * 0.9
        got = dist < 0.0004
        hit[idx[got]] = True
        alive[idx[got]] = False
        alive[idx[t[idx] > tmax]] = False
    out = np.zeros((h * w, 4), np.float32)
    em = np.zeros(h * w, np.float32)
    hi = np.nonzero(hit)[0]
    if len(hi):
        p = o[hi] + d[hi] * t[hi, None]
        _, mat = model.field(p)
        e = 0.0006
        grad = [model.field(p + s)[0] - model.field(p - s)[0] for s in ((e, 0, 0), (0, e, 0), (0, 0, e))]
        nrm = np.stack(grad, -1)
        nrm /= np.maximum(_len(nrm), 1e-9)[:, None]
        lam = np.clip(nrm @ unit(light), 0, 1)
        edge = (1 - np.clip(_dot(nrm, -d[hi]), 0, 1)) ** 2.5
        occ = np.zeros(len(hi))
        for k, s in enumerate((0.004, 0.009, 0.016)):             # ambient occlusion, from the field
            occ += (s - model.field(p + nrm * s)[0]) / s * (0.5 ** k)
        v = np.clip((ambient + diffuse * lam) * np.clip(1 - ao * occ / 1.75, 0.35, 1) + rim * edge, 0, 1)
        yy, xx = np.divmod(hi, w)
        bay = BAYER[yy % 4, xx % 4]
        for m, ramp in enumerate(ramps):
            sel = mat == m
            if ramp is None or not sel.any():
                continue
            ramp = np.asarray(ramp, np.float32)
            k = np.clip(np.round(v[sel] * (len(ramp) - 1) + (bay[sel] - 0.5) * dither), 0, len(ramp) - 1).astype(int)
            out[hi[sel], :3] = ramp[k]
            if m in glow:
                em[hi[sel]] = 1.0
        out[hi, 3] = 1.0
        if crease:                                     # a dark line where a part passes in front of another
            Z = np.full(h * w, np.inf)
            Z[hi] = t[hi]
            Z = Z.reshape(h, w)
            pad = np.pad(Z, 1, constant_values=np.inf)
            near = np.minimum.reduce([pad[:-2, 1:-1], pad[2:, 1:-1], pad[1:-1, :-2], pad[1:-1, 2:]])
            with np.errstate(invalid='ignore'):
                behind = np.isfinite(Z) & (Z - near > crease * Z)
            out.reshape(h, w, 4)[behind, :3] *= crease_dark
    rgba = out.reshape(h, w, 4)
    if outline:
        rgba = outline_sprite(rgba, darken=outline)
    return rgba.astype(np.float32), em.reshape(h, w)

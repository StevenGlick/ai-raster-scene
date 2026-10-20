"""Wireframes: low-poly meshes drawn as lines of light through the camera, in true 3D.

A scene's `wireframes` (and a shot's `extra_wireframes`) are meshes - a built-in shape by name, or
the scene's own vertices and faces - placed in the world like sprites. Every edge is projected
through the shot's camera and drawn one pixel wide, hidden behind anything nearer and seen in
front of anything farther, so a cube is a cube from every side and a ring of them reads as solid
3D. They give off light (bloom with `"source": "light"` glows round them) and stand in reflective
floors. A `solid` mesh fills its faces (black unless `fill` says otherwise), so it hides what is
behind it - its own far edges included: black shapes edged in light, the look of 80s vector
arcade games.

A mesh is (vertices, edges, faces): vertices about one unit across with the base at z = 0 and the
middle at x = y = 0; faces as lists of vertex indices; edges as index pairs (the faces' sides
when not given). The renderer calls draw(); MESHES lists the built-in shapes.
"""
import math

import numpy as np

NEAR = 0.05          # nearest distance a line is drawn at
GOLD = (1 + 5 ** 0.5) / 2


# ------------------------------------------------------------------ building meshes

def _edges_of(faces):
    seen, out = set(), []
    for f in faces:
        for a, b in zip(f, f[1:] + f[:1]):
            k = (min(a, b), max(a, b))
            if k not in seen:
                seen.add(k)
                out.append(k)
    return out


def _mesh(verts, faces=(), edges=None):
    v = np.asarray(verts, np.float64).reshape(-1, 3)
    faces = [list(map(int, f)) for f in faces]
    e = _edges_of(faces) if edges is None else [(int(a), int(b)) for a, b in edges]
    return v, np.asarray(e, int).reshape(-1, 2), faces


def _join(*parts):
    """Several meshes as one (their vertex indices renumbered)."""
    vs, es, fs, n = [], [], [], 0
    for v, e, f in parts:
        vs.append(v)
        es.append(e + n)
        fs += [[i + n for i in face] for face in f]
        n += len(v)
    return np.concatenate(vs), np.concatenate(es), fs


def _ring(n, r, z, phase=0.0, cx=0.0, cy=0.0):
    return [(cx + r * math.cos(phase + 2 * math.pi * k / n), cy + r * math.sin(phase + 2 * math.pi * k / n), z)
            for k in range(n)]


def _box(x0, x1, y0, y1, z0, z1):
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    return _mesh(v, [[0, 2, 3, 1], [4, 5, 7, 6], [0, 1, 5, 4], [1, 3, 7, 5], [3, 2, 6, 7], [2, 0, 4, 6]])


def _prism(n, r0, r1, z0, z1, phase=0.0):
    """An n-sided prism (r0 = r1), frustum, or cone (r1 = 0) from z0 up to z1."""
    if r1 <= 0:
        v = _ring(n, r0, z0, phase) + [(0.0, 0.0, z1)]
        return _mesh(v, [list(range(n))[::-1]] + [[k, (k + 1) % n, n] for k in range(n)])
    v = _ring(n, r0, z0, phase) + _ring(n, r1, z1, phase)
    faces = [list(range(n))[::-1], list(range(n, 2 * n))]
    faces += [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    return _mesh(v, faces)


def _polyline(points, closed=False):
    pts = [tuple(p) for p in points]
    e = [(k, k + 1) for k in range(len(pts) - 1)] + ([(len(pts) - 1, 0)] if closed else [])
    return _mesh(pts, (), e)


def _hull_faces(v):
    """The faces of a convex solid given its vertices: every plane through three of them with all
    the rest on one side, its vertices in order round it. For the small polyhedra only."""
    n = len(v)
    faces, seen = [], set()
    c = v.mean(0)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                nrm = np.cross(v[j] - v[i], v[k] - v[i])
                if np.linalg.norm(nrm) < 1e-9:
                    continue
                nrm /= np.linalg.norm(nrm)
                d = (v - v[i]) @ nrm
                if (d > 1e-6).any() and (d < -1e-6).any():
                    continue
                on = tuple(sorted(np.nonzero(np.abs(d) <= 1e-6)[0]))
                if on in seen:
                    continue
                seen.add(on)
                if (v[i] - c) @ nrm < 0:
                    nrm = -nrm
                m = v[list(on)].mean(0)
                a = v[on[0]] - m
                a /= np.linalg.norm(a)
                b = np.cross(nrm, a)
                ang = [math.atan2((v[q] - m) @ b, (v[q] - m) @ a) for q in on]
                faces.append([on[q] for q in np.argsort(ang)])
    return faces


def _solid(v):
    v = np.asarray(v, np.float64)
    return _mesh(v, _hull_faces(v))


def _sit(v):
    """Rest a solid on z = 0 and scale it to one unit across its widest."""
    v = np.asarray(v, np.float64)
    v = v - v.mean(0)
    v = v / max(1e-9, float(np.ptp(v, axis=0).max()))
    v[:, 2] -= v[:, 2].min()
    return v


def m_cube(p):
    return _box(-0.5, 0.5, -0.5, 0.5, 0.0, 1.0)


def m_pyramid(p):
    return _mesh([(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0), (0, 0, 1)],
                 [[3, 2, 1, 0], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]])


def m_tetrahedron(p):
    return _solid(_sit(_ring(3, 1.0, 0.0, math.pi / 2) + [(0, 0, math.sqrt(2.0))]))


def m_octahedron(p):
    return _solid(_sit([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]))


def m_icosahedron(p):
    g = GOLD
    v = [(0, s1, s2 * g) for s1 in (-1, 1) for s2 in (-1, 1)] + [(s1, s2 * g, 0) for s1 in (-1, 1) for s2 in (-1, 1)] \
        + [(s2 * g, 0, s1) for s1 in (-1, 1) for s2 in (-1, 1)]
    return _solid(_sit(v))


def m_dodecahedron(p):
    g, h = GOLD, 1 / GOLD
    v = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    v += [(0, s1 * h, s2 * g) for s1 in (-1, 1) for s2 in (-1, 1)]
    v += [(s1 * h, s2 * g, 0) for s1 in (-1, 1) for s2 in (-1, 1)]
    v += [(s2 * g, 0, s1 * h) for s1 in (-1, 1) for s2 in (-1, 1)]
    return _solid(_sit(v))


def m_prism(p):
    """`sides` (6) round, one unit tall."""
    return _prism(max(3, int(p.get('sides', 6))), 0.5, 0.5, 0.0, 1.0)


def m_cylinder(p):
    return _prism(max(3, int(p.get('sides', 16))), 0.5, 0.5, 0.0, 1.0)


def m_cone(p):
    return _prism(max(3, int(p.get('sides', 12))), 0.5, 0.0, 0.0, 1.0)


def m_sphere(p):
    """`segments` (12) round and `rings` (8) from pole to pole: a globe of lines."""
    n, m = max(3, int(p.get('segments', 12))), max(2, int(p.get('rings', 8)))
    v = [(0, 0, 0.0)]
    for i in range(1, m):
        a = math.pi * i / m
        v += _ring(n, 0.5 * math.sin(a), 0.5 - 0.5 * math.cos(a))
    v.append((0, 0, 1.0))
    top = len(v) - 1
    faces = [[0, 1 + (k + 1) % n, 1 + k] for k in range(n)]
    for i in range(m - 2):
        b = 1 + i * n
        faces += [[b + k, b + (k + 1) % n, b + n + (k + 1) % n, b + n + k] for k in range(n)]
    b = 1 + (m - 2) * n
    faces += [[b + k, b + (k + 1) % n, top] for k in range(n)]
    return _mesh(v, faces)


def m_torus(p):
    """A ring lying flat: `segments` (16) round it, `sides` (8) round its tube, `thickness` (0.15)."""
    n, m = max(3, int(p.get('segments', 16))), max(3, int(p.get('sides', 8)))
    r = float(p.get('thickness', 0.15))
    R = 0.5 - r
    v = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            v.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r + r * math.sin(b)))
    faces = [[i * m + j, i * m + (j + 1) % m, ((i + 1) % n) * m + (j + 1) % m, ((i + 1) % n) * m + j]
             for i in range(n) for j in range(m)]
    return _mesh(v, faces)


def m_grid(p):
    """A flat lattice of `cells` (8) by `cells` lines on the ground."""
    n = max(1, int(p.get('cells', 8)))
    v = [(-0.5 + i / n, -0.5 + j / n, 0.0) for j in range(n + 1) for i in range(n + 1)]
    faces = [[j * (n + 1) + i, j * (n + 1) + i + 1, (j + 1) * (n + 1) + i + 1, (j + 1) * (n + 1) + i]
             for j in range(n) for i in range(n)]
    return _mesh(v, faces)


def m_terrain(p):
    """Low-poly mountains: a field `cells` (14) square, each cell cut into two triangles, raised
    into `peaks` (3) ridged summits one unit high at most - placed by `seed` - and falling to the
    ground at the edges."""
    n = max(2, int(p.get('cells', 14)))
    rng = np.random.default_rng(int(p.get('seed', 1)))
    xs = np.linspace(-0.5, 0.5, n + 1)
    X, Y = np.meshgrid(xs, xs)
    Z = np.zeros_like(X)
    for _ in range(max(1, int(p.get('peaks', 3)))):
        cx, cy = rng.uniform(-0.25, 0.25, 2)
        h, w = rng.uniform(0.55, 1.0), rng.uniform(0.14, 0.26)
        d = np.hypot(X - cx, Y - cy) / w
        Z = np.maximum(Z, h * np.clip(1 - d, 0, 1) ** 1.2)
    Z += rng.uniform(-0.04, 0.04, Z.shape) * (Z > 0.05)
    edge = np.clip(np.minimum(0.5 - np.abs(X), 0.5 - np.abs(Y)) / 0.12, 0, 1)
    Z = np.clip(Z * edge, 0, None)
    Z /= max(1e-9, Z.max())
    v = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    idx = lambda i, j: j * (n + 1) + i    # noqa: E731
    faces = []
    for j in range(n):
        for i in range(n):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            faces += [[a, b, c], [a, c, d]] if (i + j) % 2 == 0 else [[a, b, d], [b, c, d]]
    # only the ground that rises: a flat skirt of lines would pile up into a glare along the foot
    return _mesh(v, [f for f in faces if v[f, 2].max() > 0.02])


def m_racer(p):
    """A low-poly racer one unit long, nose toward +x: a wedge of a body, a canopy, a fin, and a
    wheel on each side of each axle."""
    v = [(0.5, 0.0, 0.07),                                        # 0 the nose
         (0.22, -0.15, 0.04), (0.22, 0.15, 0.04),                  # 1, 2 front shoulders, low
         (0.18, -0.12, 0.14), (0.18, 0.12, 0.14),                  # 3, 4 front shoulders, high
         (-0.5, -0.18, 0.05), (-0.5, 0.18, 0.05),                  # 5, 6 tail, low
         (-0.5, -0.16, 0.19), (-0.5, 0.16, 0.19),                  # 7, 8 tail, high
         (0.05, 0.0, 0.25), (-0.25, -0.08, 0.24), (-0.25, 0.08, 0.24),  # 9-11 the canopy
         (-0.42, 0.0, 0.19), (-0.5, 0.0, 0.36)]                     # 12, 13 the fin
    faces = [[0, 2, 1], [0, 1, 3], [0, 4, 2], [0, 3, 4], [1, 2, 6, 5], [1, 5, 7, 3], [2, 4, 8, 6],
             [5, 6, 8, 7], [3, 9, 4], [3, 10, 9], [4, 9, 11], [3, 7, 10], [4, 11, 8], [10, 11, 9],
             [7, 8, 11, 10]]
    parts = [_mesh(v, faces), _mesh([v[12], v[13], (-0.44, 0.0, 0.19)], [[0, 1, 2]])]
    for x in (0.26, -0.33):                                         # the wheels, rings on the sides
        for y in (-0.19, 0.19):
            ring = [(x + 0.075 * math.cos(a), y, 0.075 + 0.075 * math.sin(a))
                    for a in np.linspace(0, 2 * math.pi, 9)[:-1]]
            parts.append(_polyline(ring, closed=True))
    return _join(*parts)


def m_palm(p):
    """A palm in lines: a leaning trunk ringed at every joint and a crown of drooping fronds."""
    parts = []
    trunk = [(0.12 * (k / 6) ** 2, 0.0, k / 6 * 0.95) for k in range(7)]
    parts.append(_polyline(trunk))
    for x, y, z in trunk[:-1]:
        parts.append(_polyline(_ring(6, 0.035, z, cx=x, cy=y), closed=True))
    top = np.array(trunk[-1])
    for k in range(7):
        a = 2 * math.pi * k / 7 + 0.3
        pts = [top + np.array([math.cos(a) * 0.48 * s, math.sin(a) * 0.48 * s,
                               0.12 * math.sin(math.pi * s * 0.8) - 0.25 * s * s])   # up, then drooping
               for s in np.linspace(0, 1, 6)]
        parts.append(_polyline(pts))
    return _join(*parts)


def m_tree(p):
    """A low-poly pine: a trunk and three cones stacked, smaller to the top."""
    parts = [_prism(5, 0.06, 0.06, 0.0, 0.2)]
    for z0, r, h in ((0.15, 0.36, 0.4), (0.4, 0.28, 0.35), (0.62, 0.2, 0.38)):
        parts.append(_prism(7, r, 0.0, z0, z0 + h))
    return _join(*parts)


def m_tower(p):
    """A stepped spire: three blocks, each narrower, and a point on top - one unit tall."""
    parts = [_box(-0.5, 0.5, -0.5, 0.5, 0.0, 0.32), _box(-0.36, 0.36, -0.36, 0.36, 0.32, 0.58),
             _box(-0.22, 0.22, -0.22, 0.22, 0.58, 0.8)]
    parts.append(_mesh([(-0.22, -0.22, 0.8), (0.22, -0.22, 0.8), (0.22, 0.22, 0.8), (-0.22, 0.22, 0.8), (0, 0, 1.0)],
                       [[3, 2, 1, 0], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]))
    return _join(*parts)


def m_gate(p):
    """A gateway: two square pillars and a lintel across them, one unit wide and tall."""
    return _join(_box(-0.5, -0.36, -0.07, 0.07, 0.0, 0.86), _box(0.36, 0.5, -0.07, 0.07, 0.0, 0.86),
                 _box(-0.56, 0.56, -0.09, 0.09, 0.86, 1.0))


def m_crystal(p):
    """A long six-sided crystal, pointed at both ends."""
    v = _ring(6, 0.22, 0.5) + [(0, 0, 0.0), (0, 0, 1.0)]
    faces = [[k, (k + 1) % 6, 6] for k in range(6)] + [[(k + 1) % 6, k, 7] for k in range(6)]
    return _mesh(v, faces)


MESHES = {'cube': m_cube, 'pyramid': m_pyramid, 'tetrahedron': m_tetrahedron, 'octahedron': m_octahedron,
          'icosahedron': m_icosahedron, 'dodecahedron': m_dodecahedron, 'prism': m_prism, 'cylinder': m_cylinder,
          'cone': m_cone, 'sphere': m_sphere, 'torus': m_torus, 'grid': m_grid, 'terrain': m_terrain,
          'racer': m_racer, 'palm': m_palm, 'tree': m_tree, 'tower': m_tower, 'gate': m_gate, 'crystal': m_crystal}

DEFAULT_COLOR = [0.3, 1.0, 1.0]
MESH_PARAMS = ('sides', 'segments', 'rings', 'thickness', 'cells', 'seed', 'peaks')
# every key a `wireframes` entry may have (the linter warns about any other)
SPEC_KEYS = {'mesh', 'x', 'y', 'z', 'size', 'scale', 'angle', 'tilt', 'roll', 'color', 'gradient', 'intensity',
             'glow', 'solid', 'fill', 'blend', 'width', 'id', 'title', 'description', 'notes'} | set(MESH_PARAMS)
_CACHE = {}


def _rotation(yaw, tilt, roll):
    a, b, c = (math.radians(float(x)) for x in (yaw, tilt, roll))
    rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    ry = np.array([[math.cos(b), 0, math.sin(b)], [0, 1, 0], [-math.sin(b), 0, math.cos(b)]])
    rx = np.array([[1, 0, 0], [0, math.cos(c), -math.sin(c)], [0, math.sin(c), math.cos(c)]])
    return rz @ ry @ rx


def build(spec):
    """The world-space vertices, edges and faces of one `wireframes` entry: the mesh scaled by
    `size` (and `scale` [x, y, z]), turned by `angle` (about the vertical), `tilt` and `roll` round
    its own middle, and set down with its base at (`x`, `y`, `z`)."""
    m = spec.get('mesh', 'cube')
    if isinstance(m, dict):
        v, e, f = _mesh(m.get('vertices', []), m.get('faces', ()), m.get('edges'))
    else:
        if m not in MESHES:
            raise KeyError(f"unknown wireframe mesh '{m}'. Meshes: {', '.join(MESHES)}, "
                           f"or a dict of vertices, faces and edges")
        key = (m,) + tuple(repr(spec.get(k)) for k in MESH_PARAMS)
        if key not in _CACHE:
            _CACHE[key] = MESHES[m](spec)
        v, e, f = _CACHE[key]
    v = v * (np.asarray(spec.get('scale', [1, 1, 1]), np.float64) * float(spec.get('size', 1.0)))
    if len(v):
        mid = (v.min(0) + v.max(0)) / 2
        v = (v - mid) @ _rotation(spec.get('angle', 0), spec.get('tilt', 0), spec.get('roll', 0)).T + mid
    v = v + np.array([float(spec.get('x', 0)), float(spec.get('y', 0)), float(spec.get('z', 0))])
    return v, e, f


# ------------------------------------------------------------------ drawing

class View:
    """What draw() needs of the camera: position, facing, height, the frame and its projection."""

    def __init__(self, px, py, dx, dy, camz, horizon, proj, W, H, rlen):
        self.px, self.py, self.dx, self.dy, self.camz = px, py, dx, dy, camz
        self.horizon, self.proj, self.W, self.H, self.rlen = horizon, proj, W, H, rlen

    def camera(self, v):
        """World points (N, 3) to camera space: (sideways, ahead, height)."""
        sx, sy = v[:, 0] - self.px, v[:, 1] - self.py
        return np.stack([self.dx * sy - self.dy * sx, self.dx * sx + self.dy * sy, v[:, 2]], 1)

    def screen(self, c):
        """Camera-space points to (column, row) on the frame, continuous."""
        return (self.W / 2 + self.proj * c[:, 0] / c[:, 1],
                self.horizon - (c[:, 2] - self.camz) * self.proj / c[:, 1])


def _clip_near(a, b):
    """Edges a -> b in camera space with any part behind the near plane cut off."""
    ta, tb = a[:, 1], b[:, 1]
    keep = (ta > NEAR) | (tb > NEAR)
    a, b = a[keep], b[keep]
    ta, tb = a[:, 1:2], b[:, 1:2]
    d = np.where(np.abs(tb - ta) < 1e-12, 1e-12, tb - ta)
    a2 = np.where(ta < NEAR, a + (b - a) * np.clip((NEAR - ta) / d, 0, 1), a)
    b2 = np.where(tb < NEAR, b + (a - b) * np.clip((NEAR - tb) / -d, 0, 1), b)
    return a2, b2, keep


def _clip_frame(u0, v0, u1, v1, W, H, pad=2.0):
    """Liang-Barsky: the part of each screen segment inside the frame, as start and end fractions."""
    s0, s1 = np.zeros_like(u0), np.ones_like(u0)
    du, dv = u1 - u0, v1 - v0
    for p, q in ((-du, u0 + pad), (du, W + pad - u0), (-dv, v0 + pad), (dv, H + pad - v0)):
        with np.errstate(divide='ignore', invalid='ignore'):
            r = q / p
        par = np.abs(p) < 1e-12
        s0 = np.where(~par & (p < 0), np.maximum(s0, r), s0)
        s1 = np.where(~par & (p > 0), np.minimum(s1, r), s1)
        s1 = np.where(par & (q < 0), -1.0, s1)                  # parallel to an edge and outside it
    return s0, s1


def _colours(spec, z, zlo, zhi):
    """Each sample's colour: the mesh's `color`, or its `gradient` [low, high] by height."""
    if 'gradient' in spec:
        lo, hi = (np.asarray(c, np.float32) for c in spec['gradient'])
        t = np.clip((z - zlo) / max(1e-6, zhi - zlo), 0, 1)[:, None]
        return lo * (1 - t) + hi * t
    return np.broadcast_to(np.asarray(spec.get('color', DEFAULT_COLOR), np.float32), (len(z), 3))


def _lines(img, depth, emis, view, spec, v, e, ss, fog, bias):
    if not len(e):
        return
    c = view.camera(v)
    a, b, keep = _clip_near(c[e[:, 0]], c[e[:, 1]])
    if not len(a):
        return
    W, H = view.W, view.H
    (ua, va), (ub, vb) = view.screen(a), view.screen(b)
    s0, s1 = _clip_frame(ua, va, ub, vb, W, H)
    ok = s1 > s0
    if not ok.any():
        return
    ia, ib = 1 / a[:, 1], 1 / b[:, 1]            # 1/distance runs straight across the screen
    za, zb = a[:, 2] * ia, b[:, 2] * ib
    lerp = lambda p, q, s: p + (q - p) * s     # noqa: E731
    u0, u1 = lerp(ua, ub, s0)[ok], lerp(ua, ub, s1)[ok]
    v0, v1 = lerp(va, vb, s0)[ok], lerp(va, vb, s1)[ok]
    i0, i1 = lerp(ia, ib, s0)[ok], lerp(ia, ib, s1)[ok]
    q0, q1 = lerp(za, zb, s0)[ok], lerp(za, zb, s1)[ok]
    n = (np.ceil(np.maximum(np.abs(u1 - u0), np.abs(v1 - v0))) + 1).astype(int)
    idx = np.repeat(np.arange(len(n)), n)
    start = np.repeat(np.cumsum(n) - n, n)
    s = (np.arange(len(idx)) - start) / np.maximum(np.repeat(n, n) - 1, 1)
    u, vv = lerp(u0[idx], u1[idx], s), lerp(v0[idx], v1[idx], s)
    inv = lerp(i0[idx], i1[idx], s)
    t = 1 / np.maximum(inv, 1e-9)
    z = lerp(q0[idx], q1[idx], s) * t
    w = max(1, int(round(float(spec.get('width', 1)) * ss)))
    off = np.arange(w) - (w - 1) / 2.0
    cols = np.floor(u[:, None] + off[None, :] * 1.0).astype(int)
    rows = np.floor(vv[:, None] + off[None, :] * 1.0).astype(int)
    cols = np.repeat(cols, w, axis=1)
    rows = np.tile(rows, (1, w))
    tt = np.repeat(t, w * w)
    zz = np.repeat(z, w * w)
    cols, rows = cols.ravel(), rows.ravel()
    inb = (cols >= 0) & (cols < W) & (rows >= 0) & (rows < H)
    cols, rows, tt, zz = cols[inb], rows[inb], tt[inb], zz[inb]
    lin = rows * W + cols
    order = np.lexsort((tt, lin))                # each pixel once: its nearest sample
    lin, tt, zz, cols = lin[order], tt[order], zz[order], cols[order]
    first = np.ones(len(lin), bool)
    first[1:] = lin[1:] != lin[:-1]
    lin, tt, zz, cols = lin[first], tt[first], zz[first], cols[first]
    seen = tt * (1 - bias) < depth.ravel()[lin]
    lin, tt, zz, cols = lin[seen], tt[seen], zz[seen], cols[seen]
    if not len(lin):
        return
    col = _colours(spec, zz, float(v[:, 2].min()), float(v[:, 2].max())) * float(spec.get('intensity', 1.0))
    if fog is not None:                          # fading into the scene's haze with distance
        col = col * np.exp(-fog * tt * view.rlen[cols])[:, None]
    flat, eflat = img.reshape(-1, 3), emis.reshape(-1, 3)
    if spec.get('blend', 'add') == 'add':
        flat[lin] += col
    else:
        flat[lin] = col
    eflat[lin] += col * float(spec.get('glow', 1.0))
    depth.flat[lin] = tt


def _clip_poly(c):
    """A face's camera-space corners with the part behind the near plane cut away."""
    out = []
    for k in range(len(c)):
        p, q = c[k], c[(k + 1) % len(c)]
        pin, qin = p[1] > NEAR, q[1] > NEAR
        if pin:
            out.append(p)
        if pin != qin:
            out.append(p + (q - p) * ((NEAR - p[1]) / (q[1] - p[1])))
    return np.array(out)


def _fill(img, depth, emis, view, spec, v, faces, fog_c, fog):
    """Fill a solid mesh's faces with flat `fill` colour, writing depth: it hides what is behind."""
    fill = np.asarray(spec.get('fill', [0.0, 0.0, 0.0]), np.float32)
    c = view.camera(v)
    W, H = view.W, view.H
    for f in faces:
        poly = _clip_poly(c[f])
        if len(poly) < 3:
            continue
        us, vs = view.screen(poly)
        inv = 1 / poly[:, 1]
        for k in range(1, len(poly) - 1):
            tri = [0, k, k + 1]
            x0, x1 = max(0, int(math.floor(us[tri].min()))), min(W, int(math.ceil(us[tri].max())) + 1)
            y0, y1 = max(0, int(math.floor(vs[tri].min()))), min(H, int(math.ceil(vs[tri].max())) + 1)
            if x1 <= x0 or y1 <= y0:
                continue
            gy, gx = np.mgrid[y0:y1, x0:x1].astype(np.float64)
            gx += 0.5
            gy += 0.5
            (ax, bx, cx_), (ay, by, cy_) = us[tri], vs[tri]
            area = (bx - ax) * (cy_ - ay) - (cx_ - ax) * (by - ay)
            if abs(area) < 1e-9:
                continue
            w0 = ((bx - gx) * (cy_ - gy) - (cx_ - gx) * (by - gy)) / area
            w1 = ((cx_ - gx) * (ay - gy) - (ax - gx) * (cy_ - gy)) / area
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            it = w0 * inv[tri[0]] + w1 * inv[tri[1]] + w2 * inv[tri[2]]
            t = 1 / np.maximum(it, 1e-9)
            sub = depth[y0:y1, x0:x1]
            m = inside & (t < sub)
            if not m.any():
                continue
            col = fill
            if fog is not None:
                k_ = (1 - np.exp(-fog * t[m] * view.rlen[x0:x1][None, :].repeat(y1 - y0, 0)[m]))[:, None]
                col = fill * (1 - k_) + fog_c * k_
            img[y0:y1, x0:x1][m] = col
            emis[y0:y1, x0:x1][m] = 0.0
            sub[m] = t[m]


def draw(img, depth, emis, view, items, ss=1, fog_c=None, fog_d=0.0, anchors=None):
    """Draw every wireframe in `items` into the frame (img, depth and the emission buffer, all at
    the frame's resolution): solid meshes' faces first, then each mesh's edges as lines one
    `width` (native pixels) wide that add their light, hidden behind anything nearer. `fog_d` with
    `fog_c` fades them into a plain fog with distance (a volumetric fog does that itself later).
    A mesh with an `id` gets an anchor (its outline on screen), so a shot can `look_at` it."""
    fog = float(fog_d) if fog_c is not None and fog_d > 0 else None
    built = []
    for spec in items:
        v, e, f = build(spec)
        if not len(v):
            continue
        c = view.camera(v)
        built.append((float(np.median(c[:, 1])), spec, v, e, f))
    for _, spec, v, e, f in sorted(built, key=lambda b: -b[0]):      # far to near
        solid = bool(spec.get('solid', False)) and f
        if solid:
            _fill(img, depth, emis, view, spec, v, f, fog_c, fog)
        _lines(img, depth, emis, view, spec, v, e, ss, fog, 0.03 if solid else 0.0)
        if anchors is not None and spec.get('id'):
            c = view.camera(v)
            front = c[c[:, 1] > NEAR]
            if len(front):
                us, vs = view.screen(front)
                anchors[spec['id']] = {'x': float((us.min() + us.max()) / 2), 'top': float(vs.min()),
                                       'w': float(us.max() - us.min()), 'h': float(vs.max() - vs.min()),
                                       'depth': float(np.median(front[:, 1])),
                                       'visible': bool(us.max() > 0 and us.min() < view.W and vs.max() > 0
                                                       and vs.min() < view.H)}

"""The skies: procedural panoramas for the sky presets (make_sky), seamless round 360 degrees - a
gradient, clouds, stars, the aurora (icepalace.draw_aurora), a sea of cloud or space below a void floor -
with distant skylines, suns and moons (draw_disc) and sky objects (planets, a clock, an eye) painted in.
"""
import math

import numpy as np

from texlib import col, fbm, shade  # noqa: F401

# ---------------------------------------------------------------- skies

SKYLINES = ('mountains', 'hills', 'treeline', 'city', 'islands', 'jungle')


def _harmonics(w, rng, terms, ridged=False):
    """A 1-D profile over 360 degrees built from whole-number harmonics, so it wraps seamlessly."""
    az = np.arange(w) / w * 2 * np.pi
    out = np.zeros(w)
    for k, amp in terms:
        s = np.sin(k * az + rng.random() * 2 * np.pi)
        out += amp * ((1 - np.abs(s)) if ridged else 0.5 + 0.5 * s)
    return out / sum(a for _, a in terms)


def _wrapdist(w, centre):
    x = np.arange(w)
    d = np.abs(x - centre)
    return np.minimum(d, w - d)


def _silhouette(sky, elev_deg, proj, colour, rng, texture=0.08, gaps=False):
    """Paint a ground silhouette whose top edge is `elev_deg` (per column) above the horizon.
    With `gaps`, columns at zero stay open sky right down to the horizon (islands at sea)."""
    h, w = sky.shape[:2]
    top = h - 1 - proj * np.tan(np.radians(np.clip(elev_deg, 0, 60)))
    mask = np.arange(h)[:, None] >= top[None, :]
    if gaps:
        mask &= (np.asarray(elev_deg) > 0)[None, :]
    shade = 1 - texture + texture * 2 * rng.random((h, w))
    sky[mask] = (colour[None, None, :] * shade[..., None])[mask]
    return mask


def draw_skyline(sky, spec, proj, seed=0):
    """Paint distant silhouettes into a sky panorama, back to front.

    spec: a name from SKYLINES, a dict {"type", "height", "color", "seed", "lights"}, or a list of
    those (first = farthest). Heights are in degrees above the horizon, so the skyline keeps its
    proportions at any resolution or field of view.
    """
    specs = spec if isinstance(spec, list) else [spec]
    hor = sky[-1].mean(axis=0)  # the sky's own horizon colour, for atmospheric perspective

    def tone(depth, ink=(0.03, 0.035, 0.05)):
        return hor * (1 - depth) + np.array(ink, np.float32) * depth

    for i, s in enumerate(specs):
        s = {'type': s} if isinstance(s, str) else dict(s)
        kind = s.get('type')
        if kind not in SKYLINES:
            raise KeyError(f"unknown skyline '{kind}'. Skylines: {', '.join(SKYLINES)}")
        rng = np.random.default_rng(int(s.get('seed', seed)) * 31 + i * 7 + 11)
        k = float(s.get('height', 1.0))
        w = sky.shape[1]
        custom = np.array(s['color'], np.float32) if 'color' in s else None
        if kind == 'mountains':
            far = 2.0 + 6.5 * _harmonics(w, rng, [(2, 1), (3, .8), (5, .6), (8, .45), (13, .3), (21, .2), (34, .12)], True)
            _silhouette(sky, far * k, proj, custom if custom is not None else tone(0.42), rng)
            near = 0.8 + 3.2 * _harmonics(w, rng, [(3, 1), (5, .7), (9, .5), (15, .3), (27, .15)], True)
            _silhouette(sky, near * k, proj, custom * 0.7 if custom is not None else tone(0.68), rng)
        elif kind == 'hills':
            back = 1.0 + 3.4 * _harmonics(w, rng, [(5, 1), (8, .7), (13, .45), (21, .25)])
            _silhouette(sky, back * k, proj, custom if custom is not None else tone(0.5), rng)
            front = 0.4 + 2.2 * _harmonics(w, rng, [(7, 1), (11, .6), (17, .35), (29, .2)])
            _silhouette(sky, front * k, proj, custom * 0.75 if custom is not None else tone(0.72), rng)
        elif kind == 'treeline':
            px_deg = w / 360.0
            base = 1.4 + 1.2 * _harmonics(w, rng, [(9, 1), (17, .6), (31, .3)])
            elev = base.copy()
            for _ in range(int(360 * 1.6)):          # overlapping conifers, ~1.6 per degree
                cx = rng.random() * w
                th, half = 1.0 + 2.4 * rng.random(), (0.45 + 0.5 * rng.random()) * px_deg
                d = _wrapdist(w, cx)
                top = base[int(cx) % w] + th
                elev = np.maximum(elev, np.where(d < half, top - (top - base) * (d / half), 0))
            ink = (0.02, 0.045, 0.03)
            _silhouette(sky, elev * k, proj, custom if custom is not None else tone(0.86, ink), rng, 0.05)
        elif kind == 'islands':
            # a few low islands far out at sea, the bigger ones crowned with a palm or two
            px_deg = w / 360.0
            elev = np.zeros(w)
            for _ in range(int(s.get('count', 7))):
                cx = rng.random() * w
                half = (1.5 + 4.5 * rng.random()) * px_deg
                top = (0.5 + 1.6 * rng.random()) * k
                d = _wrapdist(w, cx)
                elev = np.maximum(elev, top * np.clip(1 - (d / half) ** 2, 0, 1) ** 0.6)
                for _ in range(int(rng.integers(1, 4)) if top > 0.8 * k else 0):
                    px = cx + (rng.random() - 0.5) * half
                    ph = top + (0.5 + 0.6 * rng.random()) * k
                    dd = _wrapdist(w, px)
                    elev = np.maximum(elev, np.where(dd < 0.1 * px_deg, ph, 0))                     # trunk
                    elev = np.maximum(elev, np.where(dd < 0.55 * px_deg, ph - dd / px_deg * 0.6 * k, 0))   # crown
            _silhouette(sky, elev, proj, custom if custom is not None else tone(0.45), rng, 0.04, gaps=True)
        elif kind == 'jungle':
            # rolling rainforest: round crowns packed shoulder to shoulder, the odd emergent giant
            px_deg = w / 360.0
            for depth, layer in ((0.5, 0.0), (0.8, 0.6)):
                base = 1.2 + 1.4 * layer + 1.4 * _harmonics(w, rng, [(5, 1), (9, .6), (17, .3)])
                elev = base.copy()
                for _ in range(int(360 * 0.8)):
                    cx = rng.random() * w
                    half = (0.5 + 1.3 * rng.random()) * px_deg * (1.8 if rng.random() < 0.05 else 1)
                    top = base[int(cx) % w] + (0.5 + 1.2 * rng.random() ** 2) * (2.2 if half > 2 * px_deg else 1)
                    hc = half / px_deg * 0.5
                    d = _wrapdist(w, cx)
                    crown = top - hc * (1 - np.sqrt(np.clip(1 - (d / half) ** 2, 0, 1)))
                    elev = np.maximum(elev, np.where(d < half, crown, 0))
                ink = (0.03, 0.06, 0.04)
                _silhouette(sky, elev * k, proj, custom * (1 - 0.3 * layer) if custom is not None else tone(depth, ink),
                            rng, 0.05)
        elif kind == 'city':
            px_deg = w / 360.0
            h = sky.shape[0]
            elev = np.zeros(w)
            x = 0.0
            spans = []
            while x < w:
                bw = (1.2 + 3.0 * rng.random()) * px_deg
                bh = (1.5 + 5.0 * rng.random() ** 1.7 + (4.0 if rng.random() < 0.08 else 0)) * k
                x1 = min(w, x + bw)
                elev[int(x):int(x1)] = bh
                spans.append((int(x), int(x1), bh))
                x = x1 + (0 if rng.random() < 0.75 else rng.random() * 2 * px_deg)
            ink = (0.04, 0.04, 0.06)
            body = custom if custom is not None else tone(0.8, ink)
            mask = _silhouette(sky, elev, proj, body, rng, 0.04)
            # lit windows: a sparse grid on each block, warm with the odd cold office light
            lit = float(s.get('lights', 0.22))
            yy = np.arange(h)
            for x0, x1, bh in spans:
                top = h - 1 - proj * np.tan(np.radians(bh))
                for wx in range(x0 + 1, x1 - 1, max(2, int(0.45 * px_deg))):
                    for wy in yy[(yy > top + 2) & (yy < h - 2)][::max(2, int(0.55 * px_deg))]:
                        if rng.random() < lit and mask[wy, wx]:
                            sky[wy, wx] = col('#f0c860') if rng.random() < 0.8 else col('#a8d0f0')
    return sky


def draw_disc(sky, az_deg, el_deg, proj, colour, radius_deg=2.2, glow=0.35, hrow=None, style=None):
    """A sun or moon at an azimuth/elevation, with a soft additive halo. Wraps around 360.
    `hrow` is the panorama row of the horizon (the last row, unless the sky continues below).
    `style` "stripes" draws a synthwave sun: yellow at the top through orange to pink, its lower
    half cut by gaps that widen toward the bottom (`colour` then tints only its halo)."""
    h, w = sky.shape[:2]
    hrow = h - 1 if hrow is None else hrow
    cx = (az_deg % 360) / 360.0 * w
    cy = hrow - proj * np.tan(np.radians(el_deg))
    r = max(2.0, proj * np.tan(np.radians(radius_deg)))
    dx = _wrapdist(w, cx)[None, :]
    dy = (np.arange(h) - cy)[:, None]
    d = np.sqrt(dx * dx + dy * dy)
    c = np.asarray(colour, np.float32)
    halo = np.clip(1 - d / (r * 4.5), 0, 1) ** 2 * glow
    sky += halo[..., None] * c[None, None, :]
    disc = d <= r
    if style == 'stripes':
        rows = np.arange(h, dtype=np.float32)
        rel = np.clip((rows - (cy - r)) / (2 * r), 0, 1)
        top, mid, bot = (np.array(x, np.float32) for x in ([1.0, 0.95, 0.45], [1.0, 0.55, 0.28], [1.0, 0.2, 0.62]))
        up = (rel < 0.5)[:, None]
        grad = np.where(up, top + (mid - top) * (rel / 0.5)[:, None], mid + (bot - mid) * ((rel - 0.5) / 0.5)[:, None])
        period = max(3.0, r * 0.2)
        f = np.clip((rel - 0.42) / 0.58, 0, 1)
        cut = (rel > 0.42) & (((rows - cy) % period) / period < 0.14 + 0.46 * f)
        disc = disc & ~cut[:, None]
        sky[disc] = np.broadcast_to(grad[:, None, :], sky.shape)[disc]
        return sky
    sky[disc] = c * (0.92 + 0.08 * np.clip(1 - d[disc] / r, 0, 1))[:, None]
    return sky


# ---------------------------------------------------------------- sky objects
# Planets, moons and stranger things painted into the sky panorama. Like the skyline they are
# placed in degrees (azimuth on the camera compass, elevation above the horizon, size as an
# angular radius), so they keep their size and place at any resolution or field of view.

SKY_OBJECTS = ('planet', 'ringed', 'moon', 'sun', 'eye', 'clock', 'earth')


def _sky_object_frame(sky, o, proj, hrow, default_size):
    """Pixel offsets of the whole panorama from an object's centre, in units of its radius."""
    h, w = sky.shape[:2]
    cx = (float(o.get('azimuth', 0)) % 360) / 360.0 * w
    cy = hrow - proj * np.tan(np.radians(float(o.get('elevation', 20))))
    r = max(2.0, proj * np.tan(np.radians(float(o.get('size', default_size)))))
    xs = np.arange(w)
    dx = ((xs - cx + w / 2) % w) - w / 2          # signed, wrapping round 360
    dy = np.arange(h) - cy
    return dx[None, :] / r, dy[:, None] / r, r


def _lambert(nx, ny, o):
    """Light on a sphere's face: `lit_from` is the screen direction the light comes from, in
    degrees (0 right, 90 below, 180 left, 270 above), `phase` how far round the side it is."""
    a = np.radians(float(o.get('lit_from', 210)))
    side = float(o.get('phase', 0.75))               # 0 = lit face-on, 1 = lit from the side
    lx, ly, lz = np.cos(a) * side, np.sin(a) * side, 1.0 - side * 0.85
    n = np.sqrt(lx * lx + ly * ly + lz * lz)
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    return np.clip((nx * lx + ny * ly + nz * lz) / n, 0, 1), nz


def draw_sky_object(sky, o, proj, hrow, seed=0):
    """Paint one entry of a scene's `sky_objects` into the panorama."""
    kind = o.get('type', 'planet')
    if kind not in SKY_OBJECTS:
        raise KeyError(f"unknown sky object '{kind}'. Sky objects: {', '.join(SKY_OBJECTS)}")
    rng = np.random.default_rng(int(o.get('seed', seed)) * 97 + 13)
    defaults = {'planet': ('#c87a4a', '#e8b07a', 9), 'ringed': ('#d8b880', '#a8784a', 7),
                'moon': ('#c8c4b8', '#8a867c', 3.5), 'sun': ('#fff0c0', '#ffb060', 3),
                'eye': ('#5a9a6a', '#f2ece0', 8), 'clock': ('#f2e8d0', '#3a2e26', 7),
                'earth': ('#2e62a8', '#5e8a48', 6)}[kind]
    c1 = np.array(o['color'] if 'color' in o else col(defaults[0]), np.float32)
    c2 = np.array(o['color2'] if 'color2' in o else col(defaults[1]), np.float32)
    nx, ny, r = _sky_object_frame(sky, o, proj, hrow, defaults[2])
    d2 = nx * nx + ny * ny
    inside = d2 <= 1
    glow = float(o.get('glow', {'sun': 0.9, 'eye': 0.15, 'earth': 0.4}.get(kind, 0.25)))
    if glow > 0:   # a haze of the object's own colour round it (atmosphere, corona)
        halo = np.clip(1 - np.sqrt(d2) / (3.2 if kind == 'sun' else 1.6), 0, 1) ** 2 * glow
        sky += halo[..., None] * (c2 if kind == 'sun' else c1)[None, None, :]

    if kind == 'sun':
        core = np.clip(1 - d2, 0, 1) ** 0.25
        sky[inside] = (c1[None, :] * (0.85 + 0.15 * core[inside][:, None]))
        return sky

    if kind == 'clock':
        # a clock face hung in the sky, its hands stopped at `time`, the bottom of it running like
        # wax (`melt`, 0 for a whole face)
        t = float(o.get('time', 10.15))
        melt = float(o.get('melt', 0.45))
        span = np.clip(1 - nx * nx, 0, 1)
        drip = melt * (0.3 + 0.7 * np.clip(np.sin(nx * 6.3 + 1.1) * 0.5 + 0.5, 0, 1) ** 3) * span
        face = inside | ((ny > 0) & (np.abs(nx) <= 1) & (ny <= np.sqrt(span) + drip))
        rr = np.sqrt(d2)
        ang = np.arctan2(ny, nx)
        sky[face] = (c1[None, :] * (0.82 + 0.18 * np.clip(1 - d2, 0, 1))[face][:, None])
        sky[inside & (rr >= 0.88)] = c2
        for k in range(12):                         # the ticks
            a = k * np.pi / 6 - np.pi / 2
            tick = inside & (rr > 0.66) & (rr < (0.84 if k % 3 else 0.86)) & (np.cos(ang - a) > 0) & \
                (np.abs(np.sin(ang - a)) * rr < (0.05 if k % 3 == 0 else 0.03))
            sky[tick] = c2
        for frac, length, half in (((t % 12) / 12.0, 0.5, 0.055), (t % 1.0, 0.76, 0.035)):
            a = frac * 2 * np.pi - np.pi / 2
            along = nx * np.cos(a) + ny * np.sin(a)
            across = -nx * np.sin(a) + ny * np.cos(a)
            sky[face & (along >= -0.1) & (along <= length) & (np.abs(across) <= half)] = c2
        sky[rr <= 0.06] = c2
        return sky

    if kind == 'eye':
        # an almond of white with an iris that follows the viewer: the stuff of bad dreams
        lid = np.abs(ny) <= 0.62 * np.clip(1 - nx * nx, 0, 1) ** 0.75
        white = lid & (np.abs(nx) <= 1)
        veins = (np.abs(np.sin(nx * 23 + ny * 7) * np.cos(ny * 19)) > 0.985) & white
        sky[white] = c2 * (0.88 + 0.12 * np.clip(1 - d2, 0, 1))[white][:, None]
        sky[veins] = np.array([0.75, 0.25, 0.25], np.float32)
        ir = np.sqrt(nx * nx + ny * ny)
        iris = white & (ir <= 0.42)
        rings = 0.75 + 0.25 * np.sin(np.arctan2(ny, nx) * 24)
        sky[iris] = c1 * (0.6 + 0.5 * (1 - ir[iris] / 0.42))[:, None] * rings[iris][:, None]
        sky[white & (ir <= 0.17)] = np.array([0.03, 0.02, 0.03], np.float32)
        sky[white & (np.hypot(nx + 0.08, ny + 0.08) <= 0.05)] = np.array([1, 1, 1], np.float32)
        rim = (~lid) & (np.abs(ny) <= 0.62 * np.clip(1 - nx * nx, 0, 1) ** 0.75 + 0.07) & (np.abs(nx) <= 1.02)
        sky[rim] = np.array([0.1, 0.06, 0.07], np.float32)
        return sky

    shade, nz = _lambert(nx, ny, o)
    if kind == 'earth':
        # a blue world: continents of green and desert gold over the ocean, white swirls of cloud,
        # ice at the poles, the whole of it lit on one side with a thin blue limb
        shp = np.broadcast(nx, ny).shape
        nzb = np.broadcast_to(np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1)), shp)
        lon = np.arctan2(np.broadcast_to(nx, shp), np.maximum(nzb, 1e-3))          # -pi/2 .. pi/2 across the face
        lat = np.broadcast_to(ny, shp)
        N = 128
        ui = np.clip(((lon / np.pi + 0.5) * (N - 1)).astype(int), 0, N - 1)
        vi = np.clip(((lat * 0.5 + 0.5) * (N - 1)).astype(int), 0, N - 1)
        land = fbm(N, rng, 3, 4)[vi, ui]
        cloud = fbm(N, rng, 6, 4)[vi, ui]
        is_land = land > 0.54
        desert = is_land & (np.abs(lat) < 0.42) & (land < 0.62)
        surface = np.empty(shp + (3,), np.float32)
        surface[:] = c1 * (0.85 + 0.15 * np.clip(nzb, 0, 1))[..., None]
        surface[is_land] = c2
        surface[desert] = np.array([0.72, 0.6, 0.4], np.float32)
        surface[cloud > 0.6] = np.array([0.95, 0.96, 0.98], np.float32)
        thin = (cloud > 0.55) & (cloud <= 0.6)
        surface[thin] = surface[thin] * 0.45 + 0.52
        surface[np.broadcast_to(np.abs(ny) > 0.86, shp)] = np.array([0.93, 0.95, 0.98], np.float32)
    elif kind == 'moon':
        tone = np.ones_like(d2)
        for _ in range(int(o.get('craters', 14))):
            ccx, ccy, cr = rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), rng.uniform(0.06, 0.24)
            m = (nx - ccx) ** 2 + (ny - ccy) ** 2 <= cr * cr
            tone[m] *= 0.78
        surface = c1[None, None, :] * tone[..., None]
        mare = np.clip(np.sin(nx * 4.1 + 1.3) * np.cos(ny * 3.3) - 0.35, 0, 1)
        surface = surface * (1 - mare[..., None] * 0.3) + c2[None, None, :] * mare[..., None] * 0.3
    else:
        # banded gas giant: latitude bands warped by a little turbulence
        warp = np.sin(nx * 5 + ny * 2.0 + rng.random() * 6) * 0.08
        band = 0.5 + 0.5 * np.sin((ny + warp) * float(o.get('bands', 9)) + rng.random() * 6)
        surface = c1[None, None, :] * (1 - band[..., None] * 0.55) + c2[None, None, :] * band[..., None] * 0.55
        if kind == 'planet' and o.get('storm', True):
            st = ((nx - 0.25) / 0.22) ** 2 + ((ny - 0.3) / 0.11) ** 2 <= 1
            surface[st] = surface[st] * 0.55 + np.array([0.75, 0.3, 0.2], np.float32) * 0.45
    lit = surface * (0.06 + 0.94 * shade[..., None])
    rim = np.clip(1 - nz, 0, 1) ** 3 * 0.35            # atmosphere brightening the limb
    lit = lit + (c1 * 0.6)[None, None, :] * (rim * np.clip(shade * 1.5, 0, 1))[..., None]

    if kind == 'ringed':
        tilt = float(o.get('tilt', 0.24))
        rot = np.radians(float(o.get('angle', -14)))
        rx = nx * np.cos(rot) + ny * np.sin(rot)
        ry = -nx * np.sin(rot) + ny * np.cos(rot)
        rho = np.sqrt(rx * rx + (ry / tilt) ** 2)
        ring = (rho >= 1.35) & (rho <= 2.35)
        dens = (0.55 + 0.45 * np.sin(rho * 31)) * np.where((rho > 1.8) & (rho < 1.88), 0.1, 1.0)
        ring_c = c2[None, None, :] * (0.7 + 0.3 * dens[..., None])
        a = (dens * 0.85)[..., None]
        back = ring & (ry < 0)
        sky[back] = (sky * (1 - a) + ring_c * a)[back]
        sky[inside] = lit[inside]
        front = ring & (ry >= 0)
        sky[front] = (sky * (1 - a) + ring_c * a)[front]
        return sky
    sky[inside] = lit[inside]
    return sky


# ---------------------------------------------------------------- sky presets

# top, middle and horizon colours of each preset's gradient
SKY_PRESETS = {
    'night': ('#05070e', '#1b2232', '#26304a'),
    'dusk': ('#1f2333', '#4a3550', '#a0605a'),
    'storm': ('#141820', '#262c38', '#3a4250'),
    'day': ('#4a7ab0', '#8ab4d8', '#c8dce8'),
    'overcast': ('#5a6068', '#7a8088', '#9aa0a4'),
    'blood': ('#120608', '#3a0e10', '#7a2018'),
    'space': ('#010104', '#020208', '#05050e'),
    'alien': ('#06262a', '#1c6458', '#d0b868'),
    'dream': ('#6a86d6', '#d6a2cc', '#ffdcae'),
    'sunset': ('#2a2c5a', '#c8607a', '#ffb860'),
    'golden': ('#3a6aa8', '#a0bcd2', '#f2d8a0'),
    'vector': ('#020108', '#0c0522', '#3c1046'),       # black to violet, a magenta glow at the horizon
    'aurora': ('#02040c', '#07152a', '#103046'),       # a clear arctic night: the aurora is drawn over it
}
_CLOUD_COVER = {'night': 0.62, 'dusk': 0.55, 'storm': 0.42, 'day': 0.6, 'overcast': 0.3, 'blood': 0.55,
                'alien': 0.5, 'dream': 0.5, 'sunset': 0.56, 'golden': 0.64, 'vector': 9.0, 'aurora': 9.0}
_CLOUD_COLOUR = {'night': '#2a3245', 'dusk': '#5a3a4a', 'storm': '#1c2028', 'day': '#e8eef4',
                 'overcast': '#6a7078', 'blood': '#2a0a0c', 'alien': '#7a3a6a', 'dream': '#fff2f6',
                 'sunset': '#e8806a', 'golden': '#fff0d8', 'vector': '#100820', 'aurora': '#0c1a2a'}
# the sea of cloud seen from above, under a void floor: sunlit tops, shadowed hollows
_CLOUD_SEA = {'night': ('#4a5672', '#121828'), 'dusk': ('#d89880', '#3a2c48'),
              'storm': ('#3e4652', '#141820'), 'day': ('#f2f5fa', '#9aaccc'),
              'overcast': ('#a0a6ae', '#5a6068'), 'blood': ('#7a2a1e', '#1e0608'),
              'alien': ('#9ae0c0', '#2a3a5a'), 'dream': ('#fff6fa', '#c0a0d8'),
              'sunset': ('#ffc890', '#5a3a6a'), 'golden': ('#fff0d8', '#a89aa8'),
              'vector': ('#3a1a5a', '#0a0418'), 'aurora': ('#2a4a5a', '#081420')}


def _wrapnoise(w, h, cx, cy, rng):
    """Smooth value noise over the panorama that wraps seamlessly round 360 degrees:
    a cy x cx grid of random values, interpolated with periodic indices across the width."""
    g = rng.random((cy, cx))
    u = np.arange(w) * cx / w
    i0 = np.floor(u).astype(int) % cx
    i1 = (i0 + 1) % cx
    fu = u - np.floor(u)
    fu = fu * fu * (3 - 2 * fu)
    v = np.linspace(0, cy - 1, h)
    j0 = np.floor(v).astype(int).clip(0, cy - 1)
    j1 = np.minimum(j0 + 1, cy - 1)
    fv = v - np.floor(v)
    fv = (fv * fv * (3 - 2 * fv))[:, None]
    top = g[j0][:, i0] * (1 - fu) + g[j0][:, i1] * fu
    bot = g[j1][:, i0] * (1 - fu) + g[j1][:, i1] * fu
    return (top * (1 - fv) + bot * fv).astype(np.float32)


def _stars(sky, rng, density, bright=1.0, rows=None):
    """Scatter stars of varied brightness and colour, a few of them big."""
    h, w = sky.shape[:2]
    rows = slice(None) if rows is None else rows
    sub = sky[rows]
    m = rng.random(sub.shape[:2]) < density
    k = int(m.sum())
    level = (0.35 + 0.65 * rng.random(k) ** 2.2) * bright
    tint = np.array([[1, 1, 1], [0.75, 0.85, 1.0], [1.0, 0.9, 0.75], [1.0, 0.8, 0.8]], np.float32)
    sub[m] = np.maximum(sub[m], tint[rng.integers(0, 4, k)] * level[:, None])
    big = np.argwhere(m)[level > 0.85 * bright]
    for (y, x) in big[:max(1, k // 40)]:
        for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            yy, xx = y + dy, (x + dx) % w
            if 0 <= yy < sub.shape[0]:
                sub[yy, xx] = np.maximum(sub[yy, xx], sub[y, x] * 0.55)
    sky[rows] = sub


def _space(w, h, below, proj, rng):
    """Deep space all the way round: a starfield, coloured nebula and the band of a galaxy,
    continuing under the horizon so a viewport or a void floor shows stars below as well."""
    rows = h + below
    hrow = h - 1
    sky = np.zeros((rows, w, 3), np.float32) + col('#020208')[None, None, :]
    yy = np.arange(rows)[:, None]
    az = np.arange(w)[None, :] / w * 2 * np.pi
    band_el = 18 * np.sin(az + rng.random() * 6.28) + 6 * np.sin(2 * az + rng.random() * 6.28)
    band_row = hrow - proj * np.tan(np.radians(band_el))
    near = np.exp(-((yy - band_row) / (proj * 0.12)) ** 2)
    n1 = _wrapnoise(w, rows, 18, 6, rng)
    n2 = _wrapnoise(w, rows, 40, 12, rng)
    dust = np.clip(near * (0.6 * n1 + 0.4 * n2) * 1.4 - 0.25, 0, 1)
    sky += dust[..., None] * col('#4a3a6a')[None, None, :] * 0.55
    sky += (near * n2 * 0.25)[..., None] * col('#8a7a9a')[None, None, :] * 0.4
    neb = np.clip((_wrapnoise(w, rows, 7, 3, rng) - 0.62) * 3.0, 0, 1) * np.clip(n2 * 1.4, 0, 1)
    sky += neb[..., None] * col('#2a6a8a')[None, None, :] * 0.5
    neb2 = np.clip((_wrapnoise(w, rows, 5, 2, rng) - 0.66) * 3.0, 0, 1) * n1
    sky += neb2[..., None] * col('#8a2a5a')[None, None, :] * 0.45
    _stars(sky, rng, 0.006)
    m = rng.random((rows, w)) < 0.02 * near
    sky[m] = np.maximum(sky[m], 0.55)
    return np.clip(sky, 0, 1)


def _cloud_sea(w, below, proj, preset, horizon_colour, rng):
    """What lies under a void floor: a deck of cloud far below, seen from above, melting into
    the horizon haze. Each row looks down at a steeper angle and so at nearer cloud."""
    lit, shadow = (col(c) for c in _CLOUD_SEA[preset])
    k = np.arange(1, below + 1, dtype=np.float64)[:, None]
    az = (np.arange(w) / w * 2 * np.pi)[None, :]
    down = k / proj                                   # tan of the angle below the horizon
    dist = 1.0 / down
    N = 128
    tex, fine = fbm(N, rng, 4, 5), fbm(N, rng, 8, 4)
    X, Y = dist * np.cos(az) * 12.0, dist * np.sin(az) * 12.0
    n = (0.7 * tex[Y.astype(np.int64) % N, X.astype(np.int64) % N]
         + 0.3 * fine[(Y * 2.3).astype(np.int64) % N, (X * 2.3).astype(np.int64) % N])
    billow = np.clip((n - 0.42) * 3.2, 0, 1) ** 0.7
    sea = shadow[None, None, :] * (1 - billow[..., None]) + lit[None, None, :] * billow[..., None]
    haze = np.exp(-down / 0.07)[..., None]
    return (sea * (1 - haze) + horizon_colour[None, None, :] * haze).astype(np.float32)


def make_sky(preset, w, h, seed=3, skyline=None, proj=None, discs=(), objects=(), below=0):
    """Panorama covering 360 degrees: h rows above the horizon line, plus `below` rows under it
    for scenes with void floors (stars in space, otherwise a sea of cloud far beneath).

    `skyline` adds distant silhouettes (see draw_skyline). `discs` are suns and moons placed by
    directional lights and `objects` the scene's `sky_objects`; when either is given, the
    preset's own decorative moon is left out.
    """
    if preset not in SKY_PRESETS:
        raise KeyError(f"unknown sky '{preset}'. Skies: {', '.join(SKY_PRESETS)}, or null for none")
    rng = np.random.default_rng(seed)
    proj = proj or w / (2 * np.pi)
    if preset == 'space':
        sky = _space(w, h, below, proj, rng)
    else:
        top, mid, hor = [col(c) for c in SKY_PRESETS[preset]]
        t = np.linspace(0, 1, h)[:, None]
        g = np.where(t < 0.6, top * (1 - t / 0.6) + mid * (t / 0.6), mid * (1 - (t - 0.6) / 0.4) + hor * ((t - 0.6) / 0.4))
        sky = np.repeat(g[:, None, :], w, axis=1).reshape(h, w, 3)
        # clouds: horizontal-stretched noise bands
        cn = np.zeros((h, w))
        for cells, amp in ((6, 1.0), (12, 0.5), (24, 0.25)):
            cn += _wrapnoise(w, h, cells, max(2, cells // 3), rng) * amp   # seamless at 0/360
        cn /= 1.75
        mask = np.clip((cn - _CLOUD_COVER[preset]) * 4, 0, 1) * (t < 0.85)
        sky = sky * (1 - mask[..., None] * 0.85) + col(_CLOUD_COLOUR[preset]) * mask[..., None] * 0.85
        if preset in ('night', 'storm', 'blood', 'dusk', 'alien', 'vector', 'aurora'):
            stars = (rng.random((h, w)) > 0.997) & (t[:, 0][:, None] < 0.6) & (mask < 0.2)
            sky[stars] = col('#c8c8d0') * (0.5 if preset != 'night' else 1)
        if preset in ('night', 'blood') and not discs and not objects:
            mx, my, r = int(w * 0.62), int(h * 0.28), max(4, h // 14)
            yy, xx = np.mgrid[0:h, 0:w]
            m = (yy - my) ** 2 + (xx - mx) ** 2 < r * r
            sky[m] = col('#e6e0c8') if preset == 'night' else col('#d04a30')
        if preset == 'aurora':                    # curtains of light over the stars (icepalace.py)
            import icepalace
            sky = icepalace.draw_aurora(sky, rng, h - 1, proj)
        if below:
            sky = np.concatenate([sky, _cloud_sea(w, below, proj, preset, hor, rng)], axis=0)
    sky = sky.astype(np.float32)
    for i, o in enumerate(objects):
        draw_sky_object(sky, o, proj, h - 1, seed + i)
    for d in discs:
        draw_disc(sky, d['azimuth'], d['elevation'], proj, d['color'], d.get('radius', 2.2),
                  d.get('glow', 0.35), h - 1, d.get('style'))
    if skyline:
        draw_skyline(sky[:h], skyline, proj, seed)
    return np.clip(sky, 0, 1).astype(np.float32)

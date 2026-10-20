"""Drawing pixel art in code: colour ramps, lit shapes, selective outlines and seamless tiling.

Noise on its own makes mush: every pixel a slightly different colour, no shapes, no light. A
pixel artist builds a surface out of a few deliberate things instead, and this module lets a
texture or a sprite do the same:

1. Shapes - stones, leaves, planks, blades of grass, vines - are stamped one after another into
   a height field, each pixel remembering which shape it belongs to, its material and a tone.
2. One light lights that height field: the slope of each shape shades it, taller shapes cast
   short shadows onto what lies below them, and the crevices between shapes darken.
3. The light is snapped onto a ramp - a handful of colours from shadow to highlight, with the
   shadows shifted toward blue and the highlights toward yellow, the way an artist picks them -
   with an ordered dither only where two bands of the ramp meet.
4. Each shape gets a dark edge on its shadow side where it overlaps something lower (a
   "selective outline"), so shapes stay readable when the texture is small on screen.

On a tiling canvas every stamp wraps round the edges, so the result tiles without seams.

    cv = Canvas(64)
    for x, y in spots:
        cv.leaf(x, y, x + 6, y + 14, width=7, z=1.0, tone=rng.normal(0, 0.05))
    rgb = cv.paint([ramp('#3a7a32')])

Sprites use the same canvas with `wrap=False`; `paint` then also returns an alpha mask.
"""
import colorsys

import numpy as np
from PIL import Image, ImageDraw

BAYER4 = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) + 0.5) / 16


def rgb(hexstr):
    h = hexstr.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def _toward(h, target, amt):
    """Move hue h toward target (both 0..1 round the colour wheel) by the fraction amt."""
    d = ((target - h + 0.5) % 1.0) - 0.5
    return (h + d * amt) % 1.0


def ramp(base, n=6, dark=0.3, light=1.35, warm=0.12, cool=0.16, sat=0.3):
    """n colours from deep shadow to highlight around `base`, hue-shifted like a painter's ramp.

    Shadows slide toward blue-violet and gain a little saturation; highlights slide toward
    yellow and lose some. `dark` and `light` scale the base brightness at the two ends, so the
    base colour itself sits about two thirds of the way up. A list of hex colours is returned
    as it is, for hand-picked ramps.
    """
    if isinstance(base, (list, tuple)):
        return np.array([rgb(c) for c in base], np.float32)
    r, g, b = rgb(base)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    out = []
    for i in range(n):
        t = i / (n - 1)
        k = 2 * t - 1
        f = dark + (light - dark) * t
        vv = v * f
        if k < 0:
            hh, ss = _toward(h, 0.70, cool * -k), min(1.0, s * (1 + sat * -k))
        else:
            hh, ss = _toward(h, 0.14, warm * k), s * (1 - sat * k)
        if vv > 1.0:                       # out of brightness: keep climbing by losing colour
            ss *= max(0.0, 1 - (vv - 1.0) * 1.5)
            vv = 1.0
        out.append(colorsys.hsv_to_rgb(hh, ss, vv))
    return np.array(out, np.float32)


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16


def dither(v, pal, amount=0.6):
    """Values in 0..1 (an array h x w) as colours of the ramp `pal` (n x 3), ordered-dithered across
    the steps between them: `amount` 0 bands hard, 1 spreads the pattern over a whole step. For the
    flat, banded pixel-art look of the newer kits' textures."""
    bay = np.tile(BAYER, (v.shape[0] // 4 + 1, v.shape[1] // 4 + 1))[:v.shape[0], :v.shape[1]]
    idx = np.clip(np.round(v * (len(pal) - 1) + (bay - 0.5) * amount), 0, len(pal) - 1).astype(int)
    return pal[idx].astype(np.float32)


def smooth_noise(w, h, cells, rng, wrap=True, cells_y=None):
    """Value noise 0..1 that tiles when `wrap`: `cells` across the width, and down the height
    either as many as keep the cells square or `cells_y` (fewer for vertical streaks)."""
    cy = int(cells_y) if cells_y else max(1, round(cells * h / w))
    g = rng.random((cy + 1, cells + 1))
    if wrap:
        g[-1, :], g[:, -1] = g[0, :], g[:, 0]
    x = np.arange(w) * cells / w
    y = np.arange(h) * cy / h
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = g[np.ix_(y0, x0)], g[np.ix_(y0, x0 + 1)]
    c, d = g[np.ix_(y0 + 1, x0)], g[np.ix_(y0 + 1, x0 + 1)]
    fx, fy = fx[None, :], fy[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


class Canvas:
    """Height, shape id, material and tone per pixel, built up by stamping shapes in order.

    Stamps take a `mode`: 'over' (the default) paints the shape on top of whatever is there,
    like a painter working back to front; 'max' keeps whichever surface is higher; 'add' and
    'carve' raise or cut the height inside the shape without changing what it belongs to -
    bumps, cracks, grooves and chisel marks.
    """

    def __init__(self, w, h=None, wrap=True, ground=0.0, mat=0):
        self.w, self.h = int(w), int(h or w)
        self.wrap = wrap
        self.z = np.full((self.h, self.w), ground, np.float32)
        self.id = np.zeros((self.h, self.w), np.int32)
        self.mat = np.full((self.h, self.w), mat, np.int32)
        self.tone = np.zeros((self.h, self.w), np.float32)
        self.n = 0

    # -------------------------------------------------------------- stamping

    def _grid(self, x0, y0, x1, y1):
        """Pixel coordinates covering a box, as (ys, xs) index vectors and pixel-centre offsets."""
        xs = np.arange(int(np.floor(x0)), int(np.ceil(x1)) + 1)
        ys = np.arange(int(np.floor(y0)), int(np.ceil(y1)) + 1)
        return ys, xs

    def put(self, ys, xs, mask, height, mat=0, tone=0.0, mode='over'):
        """Write one shape: mask and height are (len(ys), len(xs)) arrays over the box."""
        height = np.broadcast_to(np.asarray(height, np.float32), mask.shape)
        tone = np.broadcast_to(np.asarray(tone, np.float32), mask.shape)
        if self.wrap:
            ys, xs = ys % self.h, xs % self.w
            keep_y, keep_x = np.ones(len(ys), bool), np.ones(len(xs), bool)
        else:
            keep_y, keep_x = (ys >= 0) & (ys < self.h), (xs >= 0) & (xs < self.w)
        mask, height, tone = (a[keep_y][:, keep_x] for a in (mask, height, tone))
        Y, X = np.meshgrid(ys[keep_y], xs[keep_x], indexing='ij')
        if mode in ('add', 'carve'):
            sign = 1 if mode == 'add' else -1
            self.z[Y[mask], X[mask]] += sign * height[mask]
            return
        if mode == 'max':
            mask = mask & (height > self.z[Y, X])
        self.n += 1
        self.z[Y[mask], X[mask]] = height[mask]
        self.id[Y[mask], X[mask]] = self.n
        self.mat[Y[mask], X[mask]] = mat
        self.tone[Y[mask], X[mask]] = tone[mask]

    def ellipse(self, cx, cy, rx, ry, z=0.0, dome=1.0, angle=0.0, rough=0.0, rng=None, power=0.5, **kw):
        """An oval mound: pebbles, stones, berries, blobs of moss. `rough` wobbles the outline."""
        r = max(rx, ry) * (1 + rough) + 1
        ys, xs = self._grid(cx - r, cy - r, cx + r, cy + r)
        X, Y = np.meshgrid(xs + 0.5 - cx, ys + 0.5 - cy)
        if angle:
            ca, sa = np.cos(np.radians(angle)), np.sin(np.radians(angle))
            X, Y = X * ca + Y * sa, -X * sa + Y * ca
        d = np.sqrt((X / rx) ** 2 + (Y / ry) ** 2)
        if rough:
            rng = rng or np.random.default_rng()
            th = np.arctan2(Y, X)
            k, ph = rng.integers(3, 7), rng.random(3) * 2 * np.pi
            wob = (np.sin(th * k + ph[0]) * 0.6 + np.sin(th * (k + 2) + ph[1]) * 0.4)
            d = d * (1 + rough * wob)
        mask = d < 1
        self.put(ys, xs, mask, z + dome * np.clip(1 - d * d, 0, 1) ** power, **kw)

    def box(self, x, y, w, h, z=0.0, top=1.0, bevel=2.0, rough=0.0, rng=None, chip=0.0, **kw):
        """A bevelled block: stones in a wall, planks, tiles, bricks.

        `rough` wobbles the edges; `chip` knocks pieces out of the corners and edges."""
        ys, xs = self._grid(x - 1, y - 1, x + w + 1, y + h + 1)
        X, Y = np.meshgrid(xs + 0.5, ys + 0.5)
        e = np.minimum(np.minimum(X - x, x + w - X), np.minimum(Y - y, y + h - Y))
        if rough or chip:
            rng = rng or np.random.default_rng()
            n = smooth_noise(len(xs), len(ys), max(2, int(len(xs) / 3)), rng, wrap=False)
            e = e - rough * (n - 0.5) * 2
            for _ in range(int(chip)):
                # a bite out of a random point on the outline
                if rng.random() < 0.5:
                    cx, cy = x + rng.random() * w, y + h * rng.integers(0, 2)
                else:
                    cx, cy = x + w * rng.integers(0, 2), y + rng.random() * h
                rr = 1.0 + rng.random() * 1.6
                e = np.where((X - cx) ** 2 + (Y - cy) ** 2 < rr * rr, -1, e)
        mask = e > 0
        prof = np.clip(e / max(bevel, 1e-3), 0, 1) ** 0.6
        self.put(ys, xs, mask, z + top * prof, **kw)

    def leaf(self, x0, y0, x1, y1, width, z=0.0, dome=1.0, rib=0.35, bend=0.0, shape=0.7, base=0.25, **kw):
        """A pointed leaf from its stalk end (x0, y0) to its tip (x1, y1).

        `bend` curls it sideways (a fraction of its length), `rib` presses a crease down the
        middle, `shape` < 1 makes it fuller, > 1 more slender, and `base` how far along it is
        widest (0.5 is an even oval)."""
        L = max(np.hypot(x1 - x0, y1 - y0), 1e-3)
        ax, ay = (x1 - x0) / L, (y1 - y0) / L
        pad = width + abs(bend) * L + 1
        ys, xs = self._grid(min(x0, x1) - pad, min(y0, y1) - pad, max(x0, x1) + pad, max(y0, y1) + pad)
        X, Y = np.meshgrid(xs + 0.5 - x0, ys + 0.5 - y0)
        u = (X * ax + Y * ay) / L
        v = -X * ay + Y * ax
        v = v - bend * L * 4 * u * (1 - u)
        uc = np.clip(u, 0, 1)
        # widest at `base`, pointed at the tip, rounded toward the stalk
        prof_u = np.where(uc < base, np.sin(np.pi / 2 * np.minimum(uc / base, 1)) ** 0.6,
                          np.cos(np.pi / 2 * np.clip((uc - base) / (1 - base), 0, 1)))
        half = width / 2 * np.clip(prof_u, 0, 1) ** shape
        inside = (u >= 0) & (u <= 1) & (np.abs(v) < half)
        across = np.where(half > 0, np.abs(v) / np.maximum(half, 1e-3), 1)
        hgt = dome * np.sqrt(np.clip(1 - across ** 2, 0, 1)) * (0.6 + 0.4 * prof_u)
        hgt = hgt - rib * dome * np.exp(-(v / 0.7) ** 2) * (u < 0.92)
        self.put(ys, xs, inside, z + hgt, **kw)

    def stroke(self, pts, width, z=0.0, dome=1.0, taper=(1.0, 1.0), **kw):
        """A thick line through pts with rounded ends: stems, blades, roots, vines, cracks.

        `width` tapers linearly from taper[0] at the first point to taper[1] at the last, or
        follows `taper(t)` for t from 0 to 1 along the line when taper is a function - a blade
        that is narrow at both ends, say. With mode='carve' it cuts a groove instead."""
        pts = np.asarray(pts, np.float32)
        seg = np.diff(pts, axis=0)
        lens = np.hypot(seg[:, 0], seg[:, 1])
        total = max(lens.sum(), 1e-3)
        widest = max(taper(t) for t in np.linspace(0, 1, 21)) if callable(taper) else max(taper)
        pad = width * widest / 2 + 1
        ys, xs = self._grid(pts[:, 0].min() - pad, pts[:, 1].min() - pad, pts[:, 0].max() + pad, pts[:, 1].max() + pad)
        X, Y = np.meshgrid(xs + 0.5, ys + 0.5)
        best = np.full(X.shape, np.inf, np.float32)
        best_t = np.zeros(X.shape, np.float32)
        acc = 0.0
        for (px, py), (dx, dy), ln in zip(pts[:-1], seg, lens):
            if ln < 1e-6:
                continue
            t = np.clip(((X - px) * dx + (Y - py) * dy) / (ln * ln), 0, 1)
            d = np.hypot(X - (px + t * dx), Y - (py + t * dy))
            closer = d < best
            best = np.where(closer, d, best)
            best_t = np.where(closer, (acc + t * ln) / total, best_t)
            acc += ln
        if callable(taper):
            half = width / 2 * np.asarray(taper(best_t), np.float32)
        else:
            half = width / 2 * (taper[0] + (taper[1] - taper[0]) * best_t)
        mask = best < half
        hgt = dome * np.sqrt(np.clip(1 - (best / np.maximum(half, 1e-3)) ** 2, 0, 1))
        self.put(ys, xs, mask, z + hgt if kw.get('mode') not in ('add', 'carve') else hgt, **kw)

    def polygon(self, pts, z=0.0, top=1.0, bevel=2.0, **kw):
        """A flat-topped, bevel-edged polygon: shards, slabs, planks at an angle, roof tiles."""
        pts = np.asarray(pts, np.float32)
        x0, y0 = pts.min(0) - 1
        x1, y1 = pts.max(0) + 1
        ys, xs = self._grid(x0, y0, x1, y1)
        im = Image.new('L', (len(xs) * 4, len(ys) * 4), 0)
        ImageDraw.Draw(im).polygon([((px - xs[0]) * 4, (py - ys[0]) * 4) for px, py in pts], fill=255)
        mask = np.asarray(im.resize((len(xs), len(ys)), Image.BOX), np.float32) / 255 > 0.5
        # bevel from a cheap distance to the edge: count how many erosions each pixel survives
        dist = np.zeros(mask.shape, np.float32)
        cur = mask.copy()
        for _ in range(int(np.ceil(bevel)) + 1):
            dist += cur
            pad = np.pad(cur, 1)
            cur = cur & pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
        prof = np.clip(dist / max(bevel, 1e-3), 0, 1) ** 0.6
        self.put(ys, xs, mask, z + top * prof, **kw)

    def layer(self):
        """A blank canvas the same size, for building one piece - a leaf with holes in it, a
        cracked stone - on its own before pasting it over everything drawn so far."""
        return Canvas(self.w, self.h, wrap=self.wrap)

    def paste(self, other, cut=None):
        """Paint another canvas's shapes over this one, keeping their height, material and tone.
        `cut` (a boolean mask, or a canvas whose shapes mark it) punches holes in what is pasted,
        so they show whatever was drawn here before."""
        m = other.id > 0
        if cut is not None:
            m &= ~(cut.id > 0 if isinstance(cut, Canvas) else cut)
        self.z[m] = other.z[m]
        self.id[m] = other.id[m] + self.n
        self.mat[m] = other.mat[m]
        self.tone[m] = other.tone[m]
        self.n += other.n

    def noise(self, amount, cells=8, rng=None, octaves=2):
        """Add gentle relief everywhere (or carve, with a negative amount): grain, wear, pitting."""
        rng = rng or np.random.default_rng()
        n = np.zeros((self.h, self.w), np.float32)
        amp = 1.0
        for o in range(octaves):
            n += amp * (smooth_noise(self.w, self.h, cells * 2 ** o, rng, self.wrap) - 0.5)
            amp *= 0.5
        self.z += amount * n

    # -------------------------------------------------------------- light and paint

    def _shift(self, a, dy, dx):
        """a moved by (dy, dx) pixels: rolled round on a tile, edge-clamped on a sprite."""
        if self.wrap:
            return np.roll(a, (dy, dx), axis=(0, 1))
        h, w = a.shape
        yi = np.clip(np.arange(h) - dy, 0, h - 1)
        xi = np.clip(np.arange(w) - dx, 0, w - 1)
        return a[np.ix_(yi, xi)]

    def light(self, sun=(-0.55, -0.75, 0.75), ambient=0.38, diffuse=0.75, relief=1.0,
              cavity=0.5, shadow=0.45, reach=6, softness=0.8):
        """Light 0..1 per pixel off the height field.

        `sun` is (x, y, up) with y pointing down the image, so the default is light from the
        upper left. `relief` exaggerates slopes, `cavity` darkens pixels sitting below their
        neighbours, and `shadow` darkens what taller shapes within `reach` pixels shade from
        the light.
        """
        z = self.z
        gx = (self._shift(z, 0, -1) - self._shift(z, 0, 1)) / 2
        gy = (self._shift(z, -1, 0) - self._shift(z, 1, 0)) / 2
        gx, gy = np.clip(gx * relief, -2.5, 2.5), np.clip(gy * relief, -2.5, 2.5)
        n = np.stack([-gx, -gy, np.ones_like(z)], -1)
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        lv = np.asarray(sun, np.float32)
        lv /= np.linalg.norm(lv)
        lam = np.clip(n @ lv, 0, 1)
        # crevices: below the average of the 5x5 neighbourhood
        avg = sum(self._shift(z, dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)) / 25
        cav = np.clip((avg - z) * 1.5, 0, 1)
        # cast shadows: walk toward the light; anything rising above the ray shades this pixel
        flat = np.hypot(lv[0], lv[1])
        rise = lv[2] / max(flat, 1e-3)
        occ = np.zeros_like(z)
        for s in range(1, reach + 1 if flat > 1e-3 else 1):     # light from straight above casts none
            dx, dy = int(round(lv[0] / flat * s)), int(round(lv[1] / flat * s))
            above = self._shift(z, -dy, -dx) - z - rise * s      # the height s pixels toward the light
            occ = np.maximum(occ, above)
        sh = np.clip(occ / softness, 0, 1)
        return np.clip(ambient + diffuse * lam * (1 - shadow * sh) - cavity * cav, 0, 1)

    def paint(self, ramps, light=None, dither=0.35, outline=1, tone_noise=0.0, rng=None, alpha=None):
        """Colours from the ramps: each pixel's light, plus its shape's tone, picks a step.

        `ramps` is a list of ramps indexed by material. `outline` darkens by that many steps
        the edge of every shape that overlaps something lower, on the side away from the
        light (down and right). `tone_noise` adds a soft wash that bends the bands organically.
        On a sprite canvas (wrap=False) the result is RGBA, opaque wherever a shape was drawn
        (or where `alpha` says).
        """
        L = self.light() if light is None else light
        v = np.clip(L + self.tone, 0, 1)
        if tone_noise:
            rng = rng or np.random.default_rng(7)
            v = np.clip(v + tone_noise * (smooth_noise(self.w, self.h, 6, rng, self.wrap) - 0.5), 0, 1)
        out = np.zeros((self.h, self.w, 3), np.float32)
        bay = np.tile(BAYER4, (self.h // 4 + 1, self.w // 4 + 1))[:self.h, :self.w]
        for m, rp in enumerate(ramps):
            sel = self.mat == m
            if not sel.any():
                continue
            rp = np.asarray(rp, np.float32)
            k = len(rp)
            f = v * (k - 1) + (bay - 0.5) * dither
            idx = np.clip(np.round(f), 0, k - 1).astype(int)
            if outline:
                edge = np.zeros_like(sel)
                for dy, dx in ((0, -1), (-1, 0)):        # neighbour to the right, neighbour below
                    other = self._shift(self.id, dy, dx)
                    lower = self._shift(self.z, dy, dx) < self.z - 0.15
                    edge |= (other != self.id) & lower
                idx = np.where(edge, np.maximum(idx - outline, 0), idx)
            out[sel] = rp[idx[sel]]
        if self.wrap and alpha is None:
            return out
        a = (self.id > 0) if alpha is None else alpha
        return np.concatenate([out, a[..., None].astype(np.float32)], -1)


def outline_sprite(rgba, color=None, darken=0.38):
    """A one-pixel line round a sprite's silhouette, outside it, so it reads at a distance.

    With no `color` the line takes the colour of the pixels it borders, darkened - a coloured
    outline, softer than black, the way pixel artists usually draw them."""
    a = rgba[..., 3] > 0.5
    pad = np.pad(a, 1)
    near = [pad[:-2, 1:-1], pad[2:, 1:-1], pad[1:-1, :-2], pad[1:-1, 2:]]
    ring = (near[0] | near[1] | near[2] | near[3]) & ~a
    out = rgba.copy()
    if color is not None:
        out[ring] = list(color) + [1.0]
        return out
    cp = np.pad(rgba[..., :3], ((1, 1), (1, 1), (0, 0)))
    shifted = [cp[:-2, 1:-1], cp[2:, 1:-1], cp[1:-1, :-2], cp[1:-1, 2:]]
    acc = sum(c * m[..., None] for c, m in zip(shifted, near))
    cnt = sum(m.astype(np.float32) for m in near)
    out[ring, :3] = (acc / np.maximum(cnt, 1)[..., None] * darken)[ring]
    out[ring, 3] = 1.0
    return out

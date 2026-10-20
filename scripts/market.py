"""The night market, drawn with the pixel-art toolkit (scripts/pixelart.py): a street-food cart with
its wok over the flame, a fruit stall and a stall of glowing gadgets under their tarps, red paper
lanterns and a string of them to hang across a lane, a parked scooter, a folding table and
plastic stools, a utility pole hung with cables, a standing neon sign, a clear umbrella with a
lit shaft, and a crowd to fill the far end of a street.

Signs carry the same glowing pseudo-letters as the `neon` facades (buildings._neon_sign), so a
market reads as writing in no real script. Lit parts glow: give the stalls a warm light of
their own and they light the wet street round them.
"""
import numpy as np

from biomes import _prop
from buildings import NEON, _neon_sign
from pixelart import Canvas, outline_sprite, ramp, smooth_noise

STEEL = ramp('#7a8288', dark=0.35, light=1.4, cool=0.1)
STAINLESS = ramp('#b4bcc0', dark=0.45, light=1.2)
PAINT_TEAL = ramp('#3a8a86', dark=0.32, light=1.4)
RUST = ramp('#8a4a2a', dark=0.35, light=1.3)
TYRE = ramp('#26262a', dark=0.6, light=1.8)
IRON = ramp('#2e2c2c', dark=0.55, light=1.7)
FLAME = ramp('#ffb03a', dark=0.7, light=1.15)
BULB = ramp('#fff0b0', dark=0.75, light=1.05)
WHITE = ramp('#ece8e0', dark=0.6, light=1.05)
WOOD = ramp('#7a5a3a', dark=0.32, light=1.35)
TARP_GREEN = ramp('#2e7a5a', dark=0.32, light=1.4)
TARP_BLUE = ramp('#2a52a0', dark=0.32, light=1.4)
CLOTH = ramp('#2a2430', dark=0.5, light=1.6)
ORANGE = ramp('#ec8a1c', dark=0.4, light=1.2)
APPLE = ramp('#c42e26', dark=0.4, light=1.3)
LIME = ramp('#6aaa32', dark=0.4, light=1.25)
GRAPE = ramp('#6a3a8e', dark=0.38, light=1.35)
BANANA = ramp('#ecc83a', dark=0.45, light=1.15)
LANTERN = ramp('#c8261a', dark=0.45, light=1.25)
GOLD = ramp('#e8b43a', dark=0.45, light=1.2)
PLASTIC_RED = ramp('#d0342a', dark=0.4, light=1.3)
PLASTIC_BLUE = ramp('#2a6ad0', dark=0.4, light=1.3)
SCOOTER = ramp('#8ad0c0', dark=0.35, light=1.25)
SEAT = ramp('#3a2a26', dark=0.5, light=1.6)
CONCRETE = ramp('#8a8a84', dark=0.32, light=1.3)
CABLE = ramp('#1c1c20', dark=0.6, light=2.0)
COAT = ramp('#1e2028', dark=0.6, light=1.9)
CANOPY = ramp('#b8d8e8', dark=0.55, light=1.1)


def _glow(rgba, em, x, y, color, r=1.6, halo=1.0):
    """A small light on a painted sprite: a bright core and a softer ring round it, both glowing."""
    h, w = rgba.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    d = np.hypot(xx - x, yy - y)
    c = np.array(color, np.float32)
    core = d < r
    ring = (d >= r) & (d < r + halo) & (rgba[..., 3] < 0.5)
    rgba[core, :3] = np.clip(c * 0.6 + 0.45, 0, 1)
    rgba[core, 3] = 1.0
    em[core] = 1.0
    rgba[ring, :3] = c * 0.8
    rgba[ring, 3] = 1.0
    em[ring] = np.maximum(em[ring], 0.6)


def _sag(x0, x1, y0, sag, n=24):
    """Points along a line hanging from (x0, y0) to (x1, y0), sagging `sag` in the middle."""
    t = np.linspace(0, 1, n)
    return list(zip(x0 + (x1 - x0) * t, y0 + sag * 4 * t * (1 - t)))


def _tarp(cv, x0, x1, y0, sag, depth, mat):
    """A tarp roof seen from the front: a band sagging between two poles, its hem scalloped where
    the cloth hangs between the ties."""
    xs = np.arange(int(x0), int(x1))
    t = (xs + 0.5 - x0) / (x1 - x0)
    top = y0 + sag * 4 * t * (1 - t) - 2
    bot = top + depth + 1.6 * np.abs(np.sin(t * np.pi * 5))
    ys = np.arange(int(top.min()) - 1, int(bot.max()) + 2)
    V = (ys[:, None] + 0.5 - top[None, :]) / (bot - top)[None, :]
    mask = (V >= 0) & (V <= 1)
    cv.put(ys, xs, mask, 1.4 + 0.6 * np.sin(np.pi * np.clip(V, 0, 1)) - 0.25 * np.abs(np.sin(t * np.pi * 5))[None, :],
           mat=mat, tone=0.08 - 0.22 * V)
    return top, bot


# ---------------------------------------------------------------- stalls

def spr_food_cart():
    """A street-food cart: a teal cabinet on two wheels, a steel counter with a wok over a roaring
    burner, tall stock pots and a stack of bowls, a tin roof on posts, and under it a glowing menu
    board and three bare bulbs. Give it a warm light; set `steam` over the pots."""
    rng = np.random.default_rng(401)
    w, h = 104, 108
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (9, 95):                                                                      # posts
        cv.stroke([(x, h - 18), (x, 14)], 2.4, z=0.3, dome=0.6, mat=0)
    cv.polygon([(0, 16), (104, 9), (104, 17), (0, 24)], z=0.8, top=0.6, bevel=1.5, mat=2)    # tin roof
    for k in range(0, 104, 5):
        cv.stroke([(k, 16.5 - k * 0.067), (k, 23.5 - k * 0.067)], 1.0, z=0, dome=0.3, mode='carve')
    cv.box(6, 58, 92, 34, z=0.4, top=0.9, bevel=2.0, mat=1)                                # the cabinet
    for x in (30, 54, 78):
        cv.stroke([(x, 61), (x, 89)], 1.0, z=0, dome=0.4, mode='carve')                    # its doors
    cv.box(6, 63, 92, 3, z=1.2, top=0.3, bevel=0.8, mat=1, tone=-0.12)                     # a trim band
    cv.box(2, 54, 100, 6, z=1.4, top=0.6, bevel=1.2, mat=3)                                # steel counter
    for cx in (24, 82):                                                                    # wheels
        cv.ellipse(cx, 96, 9, 9, z=1.6, dome=1.2, mat=4)
        cv.ellipse(cx, 96, 3.6, 3.6, z=2.5, dome=0.5, mat=3)
    cv.ellipse(30, 50, 12, 4.2, z=1.8, dome=0.8, mat=5)                                    # the wok
    cv.stroke([(18, 47), (8, 44)], 1.6, z=2.0, dome=0.3, mat=5)                            # its handle
    for x, top, r in ((58, 34, 7.0), (74, 38, 6.0)):                                       # stock pots
        cv.box(x - r, top, 2 * r, 54 - top, z=1.6, top=1.2, bevel=2.5, mat=3)
        cv.ellipse(x, top, r + 0.6, 1.8, z=2.6, dome=0.4, mat=3, tone=0.1)
    for k in range(5):                                                                     # a stack of bowls
        cv.ellipse(91, 52 - k * 2.2, 5.0, 1.6, z=2.0 + k * 0.2, dome=0.5, mat=6)
    cv.box(20, 27, 64, 14, z=1.0, top=0.4, bevel=1.0, mat=4)                               # the menu board
    ramps = [STEEL, PAINT_TEAL, RUST, STAINLESS, TYRE, IRON, WHITE]
    rgba = cv.paint(ramps, cv.light(relief=1.0, cavity=0.4, shadow=0.45), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    _neon_sign(rgba[..., :3], em, (21, 28, 83, 40), NEON[1], rng, False)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    flame = (np.abs(yy - 54.5) < 1.6) & (np.abs(xx - 30) < 9) & (rng.random((h, w)) < 0.85)
    rgba[flame, :3] = np.array(FLAME[4], np.float32)
    rgba[flame, 3] = 1.0
    em[flame] = 1.0
    for x in (14, 50, 88):                                                                 # bulbs on flex
        for y in range(19, 44):
            rgba[y, x, :3] = (0.08, 0.08, 0.09)
            rgba[y, x, 3] = 1.0
        _glow(rgba, em, x + 0.5, 46, (1.0, 0.86, 0.55), r=2.2)
    return rgba.astype(np.float32), em


def _fruit(cv, rng, x0, x1, y, kind):
    """A heap of fruit along a crate's top: oranges, apples, limes, grapes or bananas."""
    mats = {'orange': 2, 'apple': 3, 'lime': 4, 'grape': 5, 'banana': 6}
    m = mats[kind]
    for row in range(3):
        for x in np.arange(x0 + 2 + row * 1.6, x1 - 2, 4.2 if kind != 'grape' else 2.6):
            yy = y - 2 - row * 2.6 - 1.2 * np.sin(np.pi * (x - x0) / (x1 - x0))
            if kind == 'banana':
                cv.stroke([(x - 3, yy - 1), (x, yy + 1), (x + 3, yy - 1.5)], 2.2, z=1.6 + row * 0.4, dome=0.7, mat=m,
                          tone=rng.normal(0, 0.05))
            elif kind == 'grape':
                cv.ellipse(x + rng.normal(0, 0.4), yy, 1.3, 1.3, z=1.6 + row * 0.4, dome=0.7, mat=m,
                           tone=rng.normal(0, 0.06))
            else:
                r = 2.0 if kind != 'lime' else 1.8
                cv.ellipse(x + rng.normal(0, 0.3), yy, r, r * 0.95, z=1.6 + row * 0.4, dome=0.9, mat=m,
                           tone=rng.normal(0, 0.05))


def spr_fruit_stall():
    """A fruit stall: crates stepped up in three tiers, heaped with oranges, apples, limes, grapes
    and bananas, little price cards stuck in them, under a green tarp hung with a bare bulb and a
    string of coloured lights."""
    rng = np.random.default_rng(403)
    w, h = 104, 100
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (5, 99):
        cv.stroke([(x, h - 2), (x, 12)], 2.0, z=0.2, dome=0.5, mat=0)
    tiers = ((h - 46, 0.6, 12), (h - 30, 1.2, 14), (h - 14, 1.8, 13))              # back to front
    kinds = ['orange', 'apple', 'lime', 'banana', 'grape']
    k = 0
    for y, z, ch in tiers:
        for x0 in range(8, 96, 22):
            cv.box(x0, y, 21, ch, z=z, top=0.8, bevel=1.5, mat=1, tone=rng.normal(0, 0.05) - 0.06 * (y < h - 40))
            cv.stroke([(x0 + 1, y + ch // 2), (x0 + 20, y + ch // 2)], 0.8, z=0, dome=0.3, mode='carve')
            _fruit(cv, rng, x0, x0 + 21, y, kinds[k % len(kinds)])
            k += 1
    _tarp(cv, 0, 104, 12, 5, 9, 7)
    ramps = [STEEL, WOOD, ORANGE, APPLE, LIME, GRAPE, BANANA, TARP_GREEN]
    rgba = cv.paint(ramps, cv.light(relief=1.0, cavity=0.4, shadow=0.45), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    for x0, y0 in ((14, h - 22), (40, h - 38), (64, h - 22), (86, h - 54), (30, h - 54)):  # price cards
        y0 = int(y0 + rng.integers(-2, 2))
        rgba[y0:y0 + 4, x0:x0 + 6, :3] = (0.92, 0.9, 0.84)
        rgba[y0 + 1, x0 + 1:x0 + 5, :3] = (0.15, 0.12, 0.12)
        rgba[y0:y0 + 4, x0:x0 + 6, 3] = 1.0
    for y in range(22, 34):
        rgba[y, 52, :3] = (0.08, 0.08, 0.09)
        rgba[y, 52, 3] = 1.0
    _glow(rgba, em, 52.5, 36, (1.0, 0.88, 0.6), r=2.4)
    for i, x in enumerate(range(6, 100, 7)):                                               # coloured lights
        y = 21 + 5 * 4 * (x / 104) * (1 - x / 104) + 1.6 * abs(np.sin(x / 104 * np.pi * 5))
        _glow(rgba, em, x + 0.5, y + 1.5, NEON[i % len(NEON)], r=0.9, halo=0.7)
    return rgba.astype(np.float32), em


def spr_gadget_stall():
    """A stall of gadgets under a blue tarp: a table in dark cloth laid with glowing screens and
    boxed odds and ends, a pegboard behind hung with cables, headphones and cases, a neon sign
    along the tarp's edge."""
    rng = np.random.default_rng(405)
    w, h = 104, 100
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (5, 99):
        cv.stroke([(x, h - 2), (x, 12)], 2.0, z=0.2, dome=0.5, mat=0)
    cv.box(12, 30, 80, 36, z=0.2, top=0.3, bevel=1.0, mat=3)                               # the pegboard
    for y in range(33, 64, 4):
        for x in range(15, 90, 4):
            cv.ellipse(x, y, 0.6, 0.6, z=0.2, dome=0.3, mode='carve')
    for k in range(12):                                                                    # things hung on it
        x, y = 16 + k * 6.4 + rng.normal(0, 0.8), rng.uniform(34, 44)
        if k % 3 == 0:                                                                     # a coil of cable
            a = np.linspace(0, 2 * np.pi, 16)
            cv.stroke(list(zip(x + 2.6 * np.cos(a), y + 5 + 4 * np.sin(a))), 1.0, z=1.0, dome=0.3, mat=4)
        elif k % 3 == 1:                                                                   # headphones
            a = np.linspace(np.pi, 2 * np.pi, 10)
            cv.stroke(list(zip(x + 3 * np.cos(a), y + 4 + 3 * np.sin(a))), 1.0, z=1.0, dome=0.3, mat=4)
            for sx in (-3, 3):
                cv.ellipse(x + sx, y + 5, 1.4, 2.0, z=1.2, dome=0.5, mat=4)
        else:                                                                              # a boxed thing
            cv.box(x - 2.5, y, 5, 7, z=1.0, top=0.5, bevel=0.8, mat=5 + k % 2)
    cv.box(4, h - 34, 96, 32, z=0.6, top=0.6, bevel=1.5, mat=2)                            # the table
    for k in range(7):                                                                     # the cloth's folds
        cv.stroke([(10 + k * 14, h - 30), (12 + k * 14, h - 3)], 1.2, z=0, dome=0.4, mode='carve')
    _tarp(cv, 0, 104, 12, 5, 9, 7)
    ramps = [STEEL, WOOD, CLOTH, ramp('#4a4844', dark=0.4, light=1.4), CABLE, PLASTIC_RED, PLASTIC_BLUE, TARP_BLUE]
    rgba = cv.paint(ramps, cv.light(relief=1.0, cavity=0.4, shadow=0.45), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    for k in range(9):                                                                     # glowing screens
        x0 = int(8 + k * 10 + rng.integers(0, 3))
        y0 = h - 40 + int(rng.integers(0, 3))
        sw, sh = int(rng.integers(5, 8)), int(rng.integers(6, 9))
        c = np.array(NEON[k % len(NEON)], np.float32)
        rgba[y0:y0 + sh, x0:x0 + sw, :3] = (0.05, 0.05, 0.06)
        rgba[y0 + 1:y0 + sh - 1, x0 + 1:x0 + sw - 1, :3] = c * 0.75 + 0.15
        if k % 2:
            rgba[y0 + 2:y0 + sh - 2:2, x0 + 1:x0 + sw - 1, :3] = c * 0.35
        rgba[y0:y0 + sh, x0:x0 + sw, 3] = 1.0
        em[y0 + 1:y0 + sh - 1, x0 + 1:x0 + sw - 1] = 0.9
    _neon_sign(rgba[..., :3], em, (24, 13, 80, 22), NEON[3], rng, False)
    return rgba.astype(np.float32), em


# ---------------------------------------------------------------- lanterns, signs, light

def spr_red_lantern():
    """A red paper lantern: ribbed paper glowing from the candle inside, black bands top and
    bottom, a gold tassel, and a pseudo-letter painted on its side. Hang it with `z`."""
    w, h = 30, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(15, 21, 13, 14, z=0.0, dome=2.4, mat=0)
    body = cv.id == cv.n
    for y in range(9, 34, 3):
        cv.stroke([(2, y), (28, y)], 0.8, z=0, dome=0.35, mode='carve')
    cv.box(8, 4, 14, 4, z=2.0, top=0.6, bevel=1.0, mat=1)
    cv.box(8, 34, 14, 4, z=2.0, top=0.6, bevel=1.0, mat=1)
    cv.stroke([(15, 1), (15, 4)], 1.2, z=2.2, dome=0.3, mat=1)
    cv.stroke([(15, 38), (15, 43)], 2.0, z=2.0, dome=0.4, taper=(0.6, 1.2), mat=2)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    letter = body & (((np.abs(xx - 15) < 0.8) & (np.abs(yy - 21) < 7)) | ((np.abs(yy - 17) < 0.8) & (np.abs(xx - 15) < 5))
                     | ((np.abs(yy - 24) < 0.8) & (xx > 11) & (xx < 20)) | ((np.abs(xx - 11.5) < 0.8) & (yy > 21) & (yy < 27)))
    cv.mat[letter] = 1
    em = np.where(body & ~letter, 0.7, 0.0) + np.where(letter, 0.15, 0.0)
    return _prop(cv, [LANTERN, IRON, GOLD], relief=1.0, cavity=0.3, shadow=0.3, sun=(-0.2, -0.3, 0.9), em=em)


def spr_lantern_span():
    """A rope slung across a lane hung with big red paper lanterns, glowing: a long card to hang
    at `z` 2-3 across a street (`planes` 1, an `angle` across it), like `wires_span`."""
    lantern, lem = spr_red_lantern()
    lh, lw = lantern.shape[:2]
    w, h = 256, 56
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    pts = _sag(0, w, 3, 12, n=200)
    for x, y in pts:
        xi, yi = int(x), int(y)
        if 0 <= xi < w:
            rgba[yi:yi + 2, xi, :3] = (0.1, 0.09, 0.08)
            rgba[yi:yi + 2, xi, 3] = 1.0
    for k, x in enumerate(range(18, w - 10, 32)):
        t = x / w
        y = int(3 + 12 * 4 * t * (1 - t)) + 1
        s = 0.62 if k % 2 else 0.74
        from PIL import Image
        im = Image.fromarray((np.clip(lantern, 0, 1) * 255).astype(np.uint8), 'RGBA')
        sw, sh = int(lw * s), int(lh * s)
        src = np.asarray(im.resize((sw, sh), Image.NEAREST), np.float32) / 255
        e = np.asarray(Image.fromarray((lem * 255).astype(np.uint8)).resize((sw, sh), Image.NEAREST), np.float32) / 255
        x0 = x - sw // 2
        ys, xs = slice(y, min(h, y + sh)), slice(max(0, x0), min(w, x0 + sw))
        sub = src[:ys.stop - y, xs.start - x0:xs.stop - x0]
        a = sub[..., 3:4]
        rgba[ys, xs, :3] = sub[..., :3] * a + rgba[ys, xs, :3] * (1 - a)
        rgba[ys, xs, 3:4] = np.maximum(rgba[ys, xs, 3:4], a)
        em[ys, xs] = np.maximum(em[ys, xs], e[:ys.stop - y, xs.start - x0:xs.stop - x0] * (a[..., 0] > 0.5))
    return rgba, em


def spr_neon_sign():
    """A standing neon sign: a tall lightbox on a steel post, edged in tube and lettered top to
    bottom in glowing pseudo-letters - for the mouth of an alley or the end of a market row."""
    rng = np.random.default_rng(409)
    w, h = 28, 112
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(11, 70, 6, 40, z=0.4, top=0.8, bevel=1.5, mat=0)                                # the post
    cv.box(6, h - 4, 16, 4, z=0.6, top=0.5, bevel=1.0, mat=0)
    cv.box(2, 2, 24, 70, z=0.8, top=0.6, bevel=1.5, mat=1)                                 # the box
    rgba = cv.paint([STEEL, IRON], cv.light(relief=1.0, cavity=0.3, shadow=0.4), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    _neon_sign(rgba[..., :3], em, (4, 4, 24, 70), NEON[0], rng, True)
    return rgba.astype(np.float32), em


def spr_umbrella():
    """A clear umbrella of the rainy city, its shaft lit along its length: a dome of pale plastic
    beaded with rain, the ribs showing through, a glowing tube from the tip down to the handle.
    Stand it at a person's place, `z` about 0.35, so the handle meets their hand."""
    w, h = 56, 52
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    cx, cy, rx, ry = 28, 20, 26, 16
    dome = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1) & (yy <= cy + 2 + 1.2 * np.abs(np.sin((xx - cx) * 0.5)))
    rgba[dome, :3] = np.array(CANOPY[3], np.float32) * (0.7 + 0.3 * (1 - (yy[dome] - 4) / 20))[:, None]
    rgba[dome, 3] = 0.45
    edge = dome & ~((((xx - cx) / (rx - 1.5)) ** 2 + ((yy - cy) / (ry - 1.5)) ** 2 <= 1) & (yy <= cy + 0.5))
    rgba[edge, :3] = (0.85, 0.95, 1.0)
    rgba[edge, 3] = 0.9
    for k in range(-3, 4):                                                                 # ribs
        a = k * 0.42
        for t in np.linspace(0, 1, 40):
            x = cx + np.sin(a) * rx * t
            y = cy - ry + 0.5 + (ry + 1.5) * (1 - np.cos(a * 0.9)) * t + ry * t * t * np.cos(a) * 0.95
            xi, yi = int(x), int(min(y, cy + 2))
            if 0 <= xi < w and 0 <= yi < h and dome[yi, xi]:
                rgba[yi, xi, :3] = (0.7, 0.8, 0.88)
                rgba[yi, xi, 3] = 0.85
    rng = np.random.default_rng(411)
    drops = dome & (rng.random((h, w)) < 0.06)                                             # raindrops
    rgba[drops, :3] = (0.95, 1.0, 1.0)
    rgba[drops, 3] = 1.0
    for y in range(3, h - 4):                                                              # the lit shaft
        rgba[y, cx - 1:cx + 1, :3] = (0.55, 1.0, 0.95)
        rgba[y, cx - 1:cx + 1, 3] = 1.0
        em[y, cx - 1:cx + 1] = 1.0
    a = np.linspace(0, np.pi, 10)                                                          # the handle
    for x, y in zip(cx - 3 + 3 * np.cos(a), h - 4 + 3 * np.sin(a)):
        rgba[int(y), int(x), :3] = (0.12, 0.12, 0.14)
        rgba[int(y), int(x), 3] = 1.0
    em[dome & ~edge] = np.maximum(em[dome & ~edge], 0.12)
    return rgba, em


# ---------------------------------------------------------------- street furniture

def spr_scooter():
    """A parked scooter in mint paint: rounded body panels, a dark seat, the front shield with its
    headlight lit, a chrome mirror, small fat wheels, standing on its kickstand."""
    w, h = 76, 52
    cv = Canvas(w, h, wrap=False, ground=-9)
    for cx in (14, 62):                                                                    # wheels
        cv.ellipse(cx, 42, 9, 9, z=0.0, dome=1.2, mat=2)
        cv.ellipse(cx, 42, 4, 4, z=1.0, dome=0.5, mat=3)
    cv.ellipse(22, 30, 18, 11, z=0.8, dome=2.0, mat=0)                                     # the rear body
    cv.polygon([(34, 36), (50, 36), (58, 14), (52, 12), (44, 32), (34, 32)], z=1.0, top=0.8, bevel=2.0, mat=0)
    cv.ellipse(60, 32, 8, 7, z=1.2, dome=1.4, mat=0)                                       # front mudguard
    cv.ellipse(24, 18.5, 14, 4.2, z=2.6, dome=0.8, mat=1)                                  # the seat
    cv.stroke([(52, 12), (56, 4), (66, 4)], 1.6, z=2.0, dome=0.4, mat=3)                   # bars and stem
    cv.stroke([(56, 4), (50, 3)], 1.4, z=2.0, dome=0.4, mat=1)                             # a grip
    cv.ellipse(66, 1.6, 2.0, 1.4, z=2.2, dome=0.4, mat=3)                                  # the mirror
    cv.stroke([(30, 40), (26, 50)], 1.4, z=1.2, dome=0.3, mat=3)                           # kickstand
    rgba = cv.paint([SCOOTER, SEAT, TYRE, STAINLESS], cv.light(relief=1.0, cavity=0.4, shadow=0.4), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    _glow(rgba, em, 59.5, 13.5, (1.0, 0.95, 0.8), r=2.2, halo=0.8)                        # headlight
    _glow(rgba, em, 4.5, 27.5, (1.0, 0.2, 0.15), r=1.4, halo=0.6)                          # tail light
    return rgba.astype(np.float32), em


def spr_stools_table():
    """Street-food seating: a low folding table with two bowls and chopsticks on it, a red and a
    blue plastic stool pulled up to it."""
    w, h = 72, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, m in ((10, 1), (62, 2)):                                                        # stools
        cv.polygon([(x - 7, 18), (x + 7, 18), (x + 5, 33), (x - 5, 33)], z=0.6, top=0.8, bevel=1.5, mat=m)
        cv.ellipse(x, 18, 8, 2.4, z=1.4, dome=0.5, mat=m, tone=0.1)
        cv.ellipse(x, 27, 2.0, 2.4, z=1.2, dome=-0.6, mat=m, tone=-0.3)
    for x in (24, 48):                                                                     # table legs
        cv.stroke([(x, 12), (x + 1, 33)], 1.4, z=0.8, dome=0.4, mat=0)
    cv.box(16, 9, 40, 4, z=1.6, top=0.6, bevel=1.0, mat=3)                                 # the top
    for x in (27, 43):                                                                     # bowls
        cv.ellipse(x, 7.5, 5.0, 2.6, z=2.2, dome=0.8, mat=4)
        cv.ellipse(x, 6.4, 3.8, 0.9, z=2.8, dome=0.1, mat=5)
    cv.stroke([(31, 5), (38, 2)], 0.7, z=3.0, dome=0.1, mat=0)                             # chopsticks
    return _prop(cv, [WOOD, PLASTIC_RED, PLASTIC_BLUE, STAINLESS, WHITE, ORANGE], relief=1.0, cavity=0.35,
                 shadow=0.4)


def spr_power_pole():
    """A concrete utility pole of the old city: a crossarm of insulators, a transformer drum, a
    street lamp on an arm, and cables looping down from it every which way."""
    rng = np.random.default_rng(413)
    w, h = 72, 220
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(36, h), (36, 6)], 5.0, z=0.4, dome=1.0, taper=(1.15, 0.8), mat=0)          # the pole
    cv.box(12, 18, 48, 4, z=1.2, top=0.6, bevel=1.0, mat=1)                                # crossarm
    for x in (15, 26, 46, 57):
        cv.ellipse(x, 16, 1.6, 2.2, z=1.6, dome=0.6, mat=2)                                # insulators
    cv.box(38, 40, 14, 20, z=1.4, top=1.2, bevel=2.0, mat=1)                               # transformer
    for y in (43, 49, 55):
        cv.stroke([(38, y), (52, y)], 0.7, z=0, dome=0.3, mode='carve')
    cv.stroke([(34, 78), (16, 72), (8, 74)], 1.6, z=1.4, dome=0.4, mat=1)                  # lamp arm
    cv.polygon([(2, 73), (14, 73), (12, 77), (4, 77)], z=1.6, top=0.6, bevel=1.0, mat=1)   # lamp head
    for k in range(9):                                                                     # cable loops
        x0 = rng.choice([15, 26, 46, 57])
        y0 = 18
        side = -1 if x0 < 36 else 1
        x1 = x0 + side * rng.uniform(6, 22)
        sag = rng.uniform(8, 40)
        pts = [(x0 + (x1 - x0) * t, y0 + sag * np.sin(np.pi * t) + 30 * t * t * (k % 3 == 0)) for t in np.linspace(0, 1, 16)]
        cv.stroke(pts, 1.0, z=2.0, dome=0.2, mat=3)
    for k in range(4):                                                                     # coils on the pole
        y = 100 + k * 14
        a = np.linspace(0, 2 * np.pi, 14)
        cv.stroke(list(zip(36 + 5 * np.cos(a), y + 2 * np.sin(a))), 1.0, z=2.2, dome=0.2, mat=3)
    for k in range(5):                                                                     # posted bills
        y = int(rng.uniform(110, 180))
        cv.box(33, y, 6, 8, z=1.6, top=0.2, bevel=0.5, mat=4, tone=rng.normal(0, 0.1))
    rgba = cv.paint([CONCRETE, STEEL, WHITE, CABLE, WHITE], cv.light(relief=1.0, cavity=0.35, shadow=0.4), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    lamp = (yy > 77) & (yy < 79.5) & (xx > 4) & (xx < 12)
    rgba[lamp, :3] = (1.0, 0.85, 0.55)
    rgba[lamp, 3] = 1.0
    em[lamp] = 1.0
    return rgba.astype(np.float32), em


def spr_crowd():
    """A crowd of people in the rain, seen at a distance: a dozen figures in dark coats at
    different depths, some under umbrellas (one or two lit), a hood, a bag - to fill the far end
    of a street or a market without placing everyone. Mostly silhouette; their edges catch the
    light."""
    rng = np.random.default_rng(415)
    w, h = 176, 70
    cv = Canvas(w, h, wrap=False, ground=-9)
    figs = sorted([(rng.uniform(8, w - 8), rng.uniform(0.82, 1.0), rng.random()) for _ in range(13)], key=lambda f: f[1])
    for x, s, r in figs:
        top = h - 58 * s
        z = s * 3
        cv.stroke([(x - 2.6 * s, h - 1), (x - 1.6 * s, h - 22 * s)], 3.2 * s, z=z, dome=0.6, mat=0)     # legs
        cv.stroke([(x + 2.6 * s, h - 1), (x + 1.6 * s, h - 22 * s)], 3.2 * s, z=z, dome=0.6, mat=0)
        cv.polygon([(x - 8 * s, h - 20 * s), (x + 8 * s, h - 20 * s), (x + 6.5 * s, top + 13 * s), (x - 6.5 * s, top + 13 * s)],
                   z=z, top=1.0, bevel=2.0, mat=0, tone=rng.normal(0, 0.06))               # the coat
        cv.ellipse(x, top + 7 * s, 5 * s, 6 * s, z=z + 0.3, dome=1.0, mat=1 if r > 0.25 else 0)        # head / hood
        if r > 0.55:                                                                       # an umbrella
            a = np.linspace(np.pi, 2 * np.pi, 20)
            cv.polygon([(x + 15 * s * np.cos(t), top + 2 * s + 9 * s * np.sin(t)) for t in a], z=z + 0.6, top=0.8,
                       bevel=1.0, mat=2 if r < 0.85 else 3)
            cv.stroke([(x, top + 2 * s), (x + 1, top + 18 * s)], 0.9, z=z + 0.6, dome=0.1, mat=0)
        elif r < 0.15:                                                                     # a bag
            cv.box(x + 6 * s, h - 32 * s, 5 * s, 7 * s, z=z + 0.4, top=0.5, bevel=1.0, mat=4)
    ramps = [COAT, ramp('#4a3a36', dark=0.5, light=1.6), ramp('#2a2a3e', dark=0.5, light=1.7), CANOPY,
             ramp('#6a3a3a', dark=0.45, light=1.5)]
    rgba = cv.paint(ramps, cv.light(relief=1.0, cavity=0.3, shadow=0.3), dither=0.3)
    em = np.zeros((h, w), np.float32)
    lit = (cv.mat == 3) & (cv.id > 0)
    rgba[lit, :3] = np.array(CANOPY[4], np.float32)
    rgba[lit, 3] = 0.7
    em[lit] = 0.6
    rgba = outline_sprite(rgba)
    return rgba.astype(np.float32), em


SPRITES = {'food_cart': spr_food_cart, 'fruit_stall': spr_fruit_stall, 'gadget_stall': spr_gadget_stall,
           'red_lantern': spr_red_lantern, 'lantern_span': spr_lantern_span, 'neon_sign': spr_neon_sign,
           'umbrella': spr_umbrella, 'scooter': spr_scooter, 'stools_table': spr_stools_table,
           'power_pole': spr_power_pole, 'crowd': spr_crowd}
SPRITE_HEIGHT = {'food_cart': 1.0, 'fruit_stall': 0.95, 'gadget_stall': 0.95, 'red_lantern': 0.16,
                 'lantern_span': 0.6, 'neon_sign': 1.5, 'umbrella': 0.42, 'scooter': 0.42, 'stools_table': 0.26,
                 'power_pole': 3.4, 'crowd': 0.66}
PROP_DEFAULTS = {'red_lantern': {'shadow': False}, 'lantern_span': {'planes': 1, 'shadow': False},
                 'umbrella': {'shadow': False},
                 'neon_sign': {'aura': {'color': [1.0, 0.3, 0.7], 'strength': 0.35, 'radius': 0.2}}}
NO_CONTACT_SHADOW = {'red_lantern', 'lantern_span', 'umbrella'}

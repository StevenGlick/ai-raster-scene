"""Dream things drawn with the pixel-art toolkit (scripts/pixelart.py): a chess set in marble, a
clock gone soft and draped over a ledge, an hourglass, a stone arch and a flight of stairs to
stand where they lead nowhere (or to hang in the air), a paper boat, and a floor of chequered
marble - for impossible places.

As in biomes.py and forest.py, every shape is stamped into a height field, lit from the upper
left and snapped onto ramps. Turned pieces - the chess men, the hourglass - are drawn with
`_lathe`, which fills a profile row by row and domes it like a cylinder.
"""
import numpy as np

from biomes import T, _prop, _rng, _tile
from pixelart import Canvas, ramp

MARBLE_W = ramp('#ece8de', dark=0.45, light=1.08, warm=0.05, cool=0.12)
MARBLE_B = ramp('#3e3a46', dark=0.45, light=1.7)
GILT = ramp('#d8b04a', dark=0.35)
FACE = ramp('#f2ead6', dark=0.5, light=1.05)
INK = ramp('#2a2420', dark=0.6, light=1.8)
STONE_D = ramp('#cfc6b4', dark=0.4, light=1.15)
GLASS_D = ramp('#a8d8e8', dark=0.5, light=1.15)
SAND_D = ramp('#e0b860', dark=0.45)
WOOD_D = ramp('#6a4a32', dark=0.35)
PAPER = ramp('#f4f0e6', dark=0.5, light=1.05)


def _lathe(cv, cx, profile, mat=0, z=0.0, dome=1.4, tone=0.0):
    """A turned shape - a chess man, a bulb of glass, a baluster: `profile` is (row, half-width)
    pairs down its height; every row is filled that wide and domed like a cylinder, as one shape."""
    y0, y1 = int(profile[0][0]), int(profile[-1][0])
    ys = np.arange(y0, y1)
    hw = np.interp(ys + 0.5, [p[0] for p in profile], [p[1] for p in profile])
    wmax = float(hw.max())
    xs = np.arange(int(np.floor(cx - wmax)) - 1, int(np.ceil(cx + wmax)) + 2)
    U = (xs[None, :] + 0.5 - cx) / np.maximum(hw[:, None], 1e-3)
    mask = (np.abs(U) < 1) & (hw[:, None] > 0.4)
    cv.put(ys, xs, mask, z + dome * np.sqrt(np.clip(1 - U * U, 0, 1)), mat=mat, tone=tone)


def _erase(cv, x0, y0, x1, y1):
    """Cut a hole right through a sprite canvas: the battlements of a rook, a window."""
    cv.id[int(y0):int(y1), int(x0):int(x1)] = 0
    cv.z[int(y0):int(y1), int(x0):int(x1)] = -9


def _veins(cv, rng, n, box):
    """Faint veins in marble: thin wandering grooves, so the stone is not plastic."""
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        pts = [(x, y)]
        for _ in range(4):
            x, y = x + rng.normal(0, 3), y + rng.uniform(2, 5)
            pts.append((x, y))
        cv.stroke(pts, 0.7, dome=0.25, mode='carve')


# ---------------------------------------------------------------- the chess set

def _base(cv, cx, h, wide):
    """The foot every piece stands on: a broad plinth, a bead and a collar."""
    _lathe(cv, cx, [(h - 9, wide - 3), (h - 7, wide), (h, wide)], dome=1.2)
    _lathe(cv, cx, [(h - 12, wide - 4), (h - 9, wide - 2)], z=0.2, dome=1.2)


def spr_chess_pawn():
    """A giant marble pawn: a broad foot, a collar and a round head. Tint it dark for the other side."""
    rng = np.random.default_rng(91)
    w, h = 40, 60
    cv = Canvas(w, h, wrap=False, ground=-9)
    _base(cv, 20, h, 16)
    _lathe(cv, 20, [(22, 8), (26, 10), (30, 7), (40, 9), (48, 13)], z=0.1, dome=1.3)
    cv.ellipse(20, 15, 9.5, 9.5, z=0.3, dome=1.6, mat=0)
    _veins(cv, rng, 3, (8, 10, 32, 56))
    return _prop(cv, [MARBLE_W], relief=1.0, cavity=0.35, shadow=0.45)


def spr_chess_rook():
    """A giant marble rook: a tower on a broad foot, its top flared and cut into battlements."""
    rng = np.random.default_rng(92)
    w, h = 44, 72
    cv = Canvas(w, h, wrap=False, ground=-9)
    _base(cv, 22, h, 17)
    _lathe(cv, 22, [(12, 14), (18, 14), (22, 11), (52, 12), (60, 15)], z=0.1, dome=1.3)
    for x in (14.0, 22.0, 30.0):                                      # gaps between the battlements
        _erase(cv, x - 1.5, 10, x + 1.5, 16)
    _veins(cv, rng, 4, (9, 12, 35, 68))
    return _prop(cv, [MARBLE_W], relief=1.0, cavity=0.4, shadow=0.45)


def spr_chess_bishop():
    """A giant marble bishop: a slender stem and a mitre with its slit, a bead on top."""
    rng = np.random.default_rng(93)
    w, h = 40, 84
    cv = Canvas(w, h, wrap=False, ground=-9)
    _base(cv, 20, h, 16)
    _lathe(cv, 20, [(30, 7), (34, 10), (37, 6), (62, 8), (72, 13)], z=0.1, dome=1.3)
    _lathe(cv, 20, [(9, 2), (14, 8), (22, 10), (30, 6)], z=0.3, dome=1.6)
    cv.stroke([(15, 14), (24, 22)], 1.2, dome=0.6, mode='carve')
    cv.ellipse(20, 6, 3, 3, z=0.5, dome=1.0, mat=0)
    _veins(cv, rng, 4, (8, 10, 32, 80))
    return _prop(cv, [MARBLE_W], relief=1.0, cavity=0.35, shadow=0.45)


def spr_chess_knight():
    """A giant marble knight: a horse's head and neck on a turned foot, the mane cut in ridges."""
    rng = np.random.default_rng(94)
    w, h = 48, 76
    cv = Canvas(w, h, wrap=False, ground=-9)
    _base(cv, 24, h, 17)
    _lathe(cv, 24, [(50, 12), (56, 14), (64, 15)], z=0.1, dome=1.2)
    head = [(14, 54), (12, 40), (14, 26), (18, 14), (24, 6), (30, 4), (34, 10), (42, 20), (44, 28), (40, 31),
            (32, 26), (30, 32), (36, 44), (36, 54)]
    cv.polygon(head, z=0.3, top=1.6, bevel=4, mat=0)
    for k in range(5):                                                # ridges of the mane
        y = 12 + k * 7
        cv.stroke([(14 + k * 0.4, y), (18 + k * 0.4, y + 4)], 1.0, dome=0.5, mode='carve')
    cv.ellipse(31, 13, 1.5, 1.2, dome=0.6, mode='carve')              # the eye
    cv.stroke([(41, 26), (43, 28)], 1.0, dome=0.4, mode='carve')      # the nostril
    cv.polygon([(26, 6), (28, 0), (31, 5)], z=0.6, top=0.8, bevel=1.5, mat=0)   # the ear
    _veins(cv, rng, 4, (12, 10, 36, 70))
    return _prop(cv, [MARBLE_W], relief=1.0, cavity=0.4, shadow=0.45)


def spr_chess_queen():
    """A giant marble queen: a tall stem, a flared crown ringed with beads, an orb on top."""
    rng = np.random.default_rng(95)
    w, h = 44, 92
    cv = Canvas(w, h, wrap=False, ground=-9)
    _base(cv, 22, h, 17)
    _lathe(cv, 22, [(26, 8), (30, 11), (33, 7), (68, 9), (80, 14)], z=0.1, dome=1.3)
    _lathe(cv, 22, [(10, 13), (16, 11), (26, 7)], z=0.3, dome=1.4)
    for k in range(7):                                                # the beads of the coronet
        x = 22 + (k - 3) * 4
        cv.ellipse(x, 9 - (3 - abs(k - 3)) * 0.6, 2.0, 2.0, z=1.2, dome=0.8, mat=0)
    cv.ellipse(22, 4, 3.4, 3.4, z=1.0, dome=1.2, mat=0)
    _veins(cv, rng, 5, (9, 12, 35, 88))
    return _prop(cv, [MARBLE_W], relief=1.0, cavity=0.35, shadow=0.45)


def spr_chess_king():
    """A giant marble king: the tallest piece, a crown and a cross on top. Tint it dark for the
    other side."""
    rng = np.random.default_rng(96)
    w, h = 44, 100
    cv = Canvas(w, h, wrap=False, ground=-9)
    _base(cv, 22, h, 17)
    _lathe(cv, 22, [(30, 8), (34, 12), (37, 8), (76, 10), (88, 15)], z=0.1, dome=1.3)
    _lathe(cv, 22, [(14, 12), (20, 13), (30, 8)], z=0.3, dome=1.4)
    cv.box(20, 2, 4, 13, z=0.8, top=0.8, bevel=1.2, mat=0)           # the cross
    cv.box(16, 5, 12, 4, z=0.9, top=0.8, bevel=1.2, mat=0)
    _veins(cv, rng, 5, (9, 14, 35, 96))
    return _prop(cv, [MARBLE_W], relief=1.0, cavity=0.35, shadow=0.45)


# ---------------------------------------------------------------- other dream things

def _clock_face(size, rng, hands=(10.2, 0.68)):
    """A clock face as RGBA: cream enamel in a gilt rim, twelve ticks, two hands."""
    cv = Canvas(size, size, wrap=False, ground=-9)
    c = size / 2
    r = size / 2 - 2
    cv.ellipse(c, c, r, r, z=0.0, dome=0.9, mat=1, power=0.4)        # the rim
    cv.ellipse(c, c, r - 3.5, r - 3.5, z=0.6, dome=0.3, mat=0)        # the enamel
    for k in range(12):
        a = k * np.pi / 6 - np.pi / 2
        cv.stroke([(c + np.cos(a) * (r - 6), c + np.sin(a) * (r - 6)), (c + np.cos(a) * (r - 9), c + np.sin(a) * (r - 9))],
                  1.6 if k % 3 == 0 else 1.0, z=0.95, dome=0.2, mat=2)
    hour, minute = hands
    for frac, length, wd in ((hour / 12.0, 0.45, 2.0), (minute, 0.7, 1.3)):
        a = frac * 2 * np.pi - np.pi / 2
        cv.stroke([(c, c), (c + np.cos(a) * r * length, c + np.sin(a) * r * length)], wd, z=1.1, dome=0.3,
                  taper=(1.0, 0.5), mat=2)
    cv.ellipse(c, c, 2, 2, z=1.3, dome=0.4, mat=1)
    return cv.paint([FACE, GILT, INK], cv.light(relief=1.0, cavity=0.3, shadow=0.35), dither=0.25)


def spr_melting_clock():
    """A clock gone soft, draped over a ledge: the top of its face lies flat on the ledge, the rest
    slumps over the edge and runs, longest in the middle, its ticks and hands bent with it. Set it on
    a block with its fold at the block's front edge."""
    rng = np.random.default_rng(97)
    face = _clock_face(48, rng)
    w, h = 56, 72
    fold = 20                                         # the row where it bends over the edge
    out = np.zeros((h, w, 4), np.float32)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    cx = w / 2
    sx = (xs - cx) / 1.08 + 24                        # a little wider than the face: it has spread
    stretch = 1.0 + 1.6 * np.exp(-((xs - cx) / 12.0) ** 2) + 0.4 * np.exp(-((xs - cx - 9) / 5.0) ** 2)
    top = ys < fold
    sy = np.where(top, (ys - 2) * 1.0, (fold - 2) + (ys - fold) / stretch)
    narrow = np.where(top, 1.0, 1.0 + (ys - fold) / h * 0.9)    # it narrows as it drips
    sx = (sx - 24) * narrow + 24
    inb = (sx >= 0) & (sx < 48) & (sy >= 0) & (sy < 48)
    sxi, syi = np.clip(sx.astype(int), 0, 47), np.clip(sy.astype(int), 0, 47)
    out[inb] = face[syi[inb], sxi[inb]]
    out[..., 3] = np.where(inb, out[..., 3], 0)
    shade = np.clip(1 - np.abs(ys - fold) / 3.0, 0, 1) * 0.35         # the crease along the edge
    out[..., :3] *= (1 - shade)[..., None]
    out[fold + 1:, :, :3] *= 0.86                                      # the hanging part faces away from the light
    out[..., 3] = (out[..., 3] > 0.5).astype(np.float32)
    return out, np.zeros((h, w), np.float32)


def spr_hourglass():
    """An hourglass in a turned wooden frame: two glass bulbs, the sand running from the top one
    into a heap in the bottom one, a gleam on the glass."""
    w, h = 40, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (6, 34):                                                 # the posts
        cv.stroke([(x, 6), (x, h - 6)], 2.6, z=0.6, dome=0.9, mat=2)
    _lathe(cv, 20, [(8, 3), (12, 13), (24, 12), (31, 2.2), (33, 2.2), (40, 12), (52, 13), (56, 3)], z=0.0, dome=0.8)
    _lathe(cv, 20, [(20, 7), (25, 10), (31, 1.8)], z=0.5, dome=0.4, mat=1)       # sand left in the top
    cv.stroke([(20, 31), (20, 52)], 0.9, z=0.7, dome=0.2, mat=1)                # the stream
    _lathe(cv, 20, [(45, 1), (51, 9), (55, 12)], z=0.5, dome=0.5, mat=1)        # the heap
    cv.stroke([(14, 13), (13, 22)], 1.0, z=1.0, dome=0.2, mat=0, tone=0.25)      # a gleam
    for y in (2, h - 8):                                              # the end plates
        cv.box(2, y, 36, 6, z=0.9, top=1.0, bevel=2, mat=2)
    return _prop(cv, [GLASS_D, SAND_D, WOOD_D], relief=1.0, cavity=0.3, shadow=0.4)


def spr_stone_arch():
    """A stone archway standing on its own: two piers of coursed stone and a round arch of
    voussoirs with a keystone, open in the middle - to stand where it leads nowhere, or to float."""
    rng = np.random.default_rng(98)
    w, h = 104, 112
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x0 in (6, 76):                                                # the piers, course by course
        y = h
        while y > 46:
            hh = rng.uniform(9, 13)
            cv.box(x0 + rng.uniform(-0.6, 0.6), y - hh, 22, hh - 0.8, z=0.0, top=1.2, bevel=2.2, rough=0.4, rng=rng,
                   mat=0, tone=rng.normal(0, 0.04))
            y -= hh
    cx, cy, r0, r1 = 52, 48, 26, 46
    n = 11
    for k in range(n):                                                # the voussoirs
        a0, a1 = np.pi + k * np.pi / n + 0.012, np.pi + (k + 1) * np.pi / n - 0.012
        big = k == n // 2
        ro = r1 + (5 if big else 0)
        pts = [(cx + np.cos(a0) * r0, cy + np.sin(a0) * r0), (cx + np.cos(a0) * ro, cy + np.sin(a0) * ro),
               (cx + np.cos(a1) * ro, cy + np.sin(a1) * ro), (cx + np.cos(a1) * r0, cy + np.sin(a1) * r0)]
        cv.polygon(pts, z=0.2 + (0.3 if big else 0), top=1.2, bevel=2.2, mat=0, tone=rng.normal(0, 0.04))
    return _prop(cv, [STONE_D], relief=1.0, cavity=0.45, shadow=0.5)


def spr_stair_float():
    """A flight of stone stairs going up into nothing, broken off at both ends, a few stones falling
    away beneath it: for the air (set `z`), or rising from the ground to nowhere."""
    rng = np.random.default_rng(99)
    w, h = 104, 100
    cv = Canvas(w, h, wrap=False, ground=-9)
    n = 8
    pts = [(4, h - 18)]
    for k in range(n):                                                # the soffit under the flight
        pts.append((4 + (k + 1) * 12, h - 18 - (k + 1) * 10))
    pts += [(4 + n * 12, h - 18 - n * 10 + 12), (16, h - 6), (4, h - 8)]
    cv.polygon(pts, z=0.0, top=1.0, bevel=3, mat=0, tone=-0.08)
    for k in range(n):                                                # the treads and risers
        x, y = 4 + k * 12, h - 18 - (k + 1) * 10
        cv.box(x, y, 13, 10, z=0.6, top=1.0, bevel=2, rough=0.3, rng=rng, mat=0, tone=0.05 - k * 0.005)
    for _ in range(5):                                                # falling stones
        x, y = rng.uniform(20, 80), rng.uniform(h - 30, h - 4)
        cv.ellipse(x, y, rng.uniform(1.5, 3), rng.uniform(1.2, 2.4), z=0.4, dome=0.8, rough=0.3, rng=rng, mat=0)
    return _prop(cv, [STONE_D], relief=1.0, cavity=0.45, shadow=0.5)


def spr_paper_boat():
    """A folded paper boat: a hull of folded planes, a peak in the middle, its creases catching the
    light."""
    w, h = 48, 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(4, 17), (44, 17), (37, 28), (11, 28)], z=0.0, top=0.8, bevel=1.5, mat=0, tone=-0.04)
    cv.polygon([(24, 2), (36, 17), (12, 17)], z=0.3, top=1.0, bevel=1.5, mat=0)
    cv.polygon([(24, 2), (30, 17), (24, 17)], z=0.5, top=0.6, bevel=1.0, mat=0, tone=-0.08)
    cv.stroke([(4, 17), (44, 17)], 0.8, dome=0.3, mode='carve')
    return _prop(cv, [PAPER], relief=1.0, cavity=0.3, shadow=0.4)


def spr_jellyfish():
    """A jellyfish drifting through the air: a bell of soft light frilled at its rim, ribbons of
    oral arms and long trailing tentacles - see-through and glowing (additive by default), so float
    it with `z` over something dark."""
    w, h = 48, 104
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    cx, cy, rx, ry = 24, 24, 19, 17
    wave = 1.6 * np.sin(xx / 2.2)
    bell = (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1) & (yy <= cy + 3 + wave)
    inner = (((xx - cx) / (rx - 4)) ** 2 + ((yy - cy + 2) / (ry - 5)) ** 2 <= 1) & bell
    rim = bell & (yy > cy - 1 + wave)
    rgb = np.zeros((h, w, 3), np.float32)
    rgb[bell] = (0.3, 0.55, 1.0)
    rgb[inner] = (0.5, 0.8, 1.0)
    rgb[rim] = (0.9, 0.55, 1.0)
    glowing = bell.copy()
    tent = np.zeros((h, w), bool)
    for k in range(7):                                                # tentacles
        x0 = cx - rx + 4 + k * (2 * rx - 8) / 6
        for y in range(int(cy + 3), h - 2):
            t = (y - cy) / (h - cy)
            x = int(round(x0 + np.sin(y / 7.0 + k) * 3 * t + (k - 3) * t * 2))
            if 0 <= x < w and (y + k) % 9 != 0:
                tent[y, x] = True
    for k in (-1, 1):                                                 # two frilled oral arms
        for y in range(int(cy), int(cy + 46)):
            t = (y - cy) / 46
            x = cx + k * (2 + 3 * np.sin(y / 4.0)) * (1 - t * 0.4)
            for dx in range(-1, 2):
                if 0 <= int(x) + dx < w:
                    tent[y, int(x) + dx] = True
    rgb[tent & ~bell] = (0.75, 0.45, 1.0)
    glowing |= tent
    rgb *= np.where(((yy.astype(int) // 1) % 3 == 0)[..., None] & glowing[..., None], 0.75, 1.0)
    a = glowing.astype(np.float32)
    return np.concatenate([rgb, a[..., None]], -1).astype(np.float32), a * 1.0


def spr_sky_lantern():
    """A paper sky lantern drifting up, lit from inside: a tapering shade of warm paper, the flame
    showing through at its open foot, a wire ring round it."""
    w, h = 26, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    _lathe(cv, 13, [(2, 10.5), (12, 10), (24, 8.5), (30, 7)], z=0.0, dome=1.0, mat=0)
    for y in (9, 17, 25):                                             # the ribs of the shade
        cv.stroke([(4, y), (22, y)], 0.8, dome=0.3, mode='carve')
    cv.stroke([(6, 30), (20, 30)], 1.2, z=1.2, dome=0.4, mat=1)       # the wire ring
    cv.ellipse(13, 28, 2.2, 3.0, z=1.4, dome=0.5, mat=2)              # the flame
    em = (cv.mat == 0) * (cv.id > 0) * 0.75 + (cv.mat == 2) * (cv.id > 0) * 1.0
    return _prop(cv, [ramp('#ffb05a', dark=0.55, light=1.2), INK, ramp('#fff4c0', dark=0.7, light=1.02)], em=em,
                 relief=1.0, cavity=0.2, shadow=0.2)


def spr_book_fly():
    """A book flying like a bird: open, its covers raised as wings, its pages fanned out between
    them and fluttering."""
    w, h = 52, 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(26, 22), (3, 6), (6, 2), (26, 16)], z=0.0, top=0.8, bevel=1.2, mat=1)      # left cover
    cv.polygon([(26, 22), (49, 8), (47, 3), (26, 16)], z=0.0, top=0.8, bevel=1.2, mat=1)    # right cover
    for k in range(7):                                                # the fanned pages
        a = np.radians(200 + k * 20)
        L = 18 + 3 * np.sin(k * 1.7)
        cv.stroke([(26, 19), (26 + np.cos(a) * L, 19 + np.sin(a) * L * 0.7)], 2.2, z=0.5 + k * 0.05, dome=0.4,
                  taper=(0.6, 1.0), mat=0)
    cv.stroke([(26, 15), (26, 24)], 2.0, z=1.0, dome=0.6, mat=1)      # the spine
    return _prop(cv, [PAPER, ramp('#7a2e2a', dark=0.35)], relief=1.0, cavity=0.3, shadow=0.35)


# ---------------------------------------------------------------- textures

def tex_tall_window(name, top=False):
    """A tall gothic window in pale stone: two lancets parted by a mullion, leaded across every
    quarter unit and open to the air between the leads. Stack it two or three storeys high and end
    it with `tall_window_top`, where the lancets close in pointed arches under a small rose."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    for row in range(4):                                              # ashlar behind everything
        off = 8 if row % 2 else 0
        for col in range(-1, 5):
            cv.box(col * 16 + off + 0.5, row * 16 + 0.5, 15, 15, z=0.0, top=1.0, bevel=2.0, mat=0,
                   tone=rng.normal(0, 0.04))
    yy, xx = np.mgrid[0:T, 0:T] + 0.5
    hole = np.zeros((T, T), bool)
    for xc in (22, 42):                                               # the two lancets
        half = 7.0
        if top:
            # a pointed arch: two arcs meeting at the apex, springing at row 34
            spring, apex = 34.0, 12.0
            r = ((spring - apex) ** 2 + half ** 2) / (2 * half)
            left = (xx - (xc + half - r)) ** 2 + (yy - spring) ** 2 <= r * r
            right = (xx - (xc - half + r)) ** 2 + (yy - spring) ** 2 <= r * r
            arch = (yy < spring) & left & right & (np.abs(xx - xc) < half) & (yy > apex)
            hole |= arch | ((yy >= spring) & (np.abs(xx - xc) < half))
        else:
            hole |= np.abs(xx - xc) < half
    if top:                                                           # the rose between the arches
        d = np.hypot(xx - 32, yy - 8)
        hole |= (d < 4.5) & ~((np.abs(xx - 32) < 0.8) | (np.abs(yy - 8) < 0.8))
    leads = hole & ((yy.astype(int) % 16) < 1)
    edge = np.zeros_like(hole)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        edge |= np.roll(hole, (dy, dx), (0, 1)) & ~hole
    cv.tone[edge] += 0.15                                            # the chamfer round the opening, catching light
    rgb = cv.paint([STONE_D], cv.light(relief=1.0, cavity=0.4, shadow=0.35), dither=0.25)
    rgb[leads] = (0.16, 0.16, 0.18)
    alpha = np.where(hole & ~leads, 0.0, 1.0).astype(np.float32)
    return rgb, None, alpha


def tex_door_hall(name):
    """A door in a papered wall, as in a hotel corridor: a pale painted door of four raised panels in
    a moulded frame, a brass knob and a brass number plate, the wallpaper striped either side.
    Tint it for doors of other colours; tile a ceiling with it and the doors go overhead."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    for x in range(0, T, 8):                                             # striped wallpaper
        cv.stroke([(x + 0.5, 0), (x + 0.5, T)], 1.4, dome=0.2, mode='carve')
    cv.noise(0.1, cells=8, rng=rng)
    cv.box(13, 4, 38, 60, z=0.3, top=1.2, bevel=2.0, mat=1)              # the frame (architrave)
    cv.box(17, 8, 30, 56, z=0.6, top=0.6, bevel=1.0, mat=2)              # the door
    for px, py, pw, ph in ((20, 11, 11, 19), (33, 11, 11, 19), (20, 34, 11, 26), (33, 34, 11, 26)):
        cv.box(px, py, pw, ph, z=0.9, top=0.8, bevel=2.0, mat=2, tone=0.03)   # raised panels
    cv.ellipse(43, 37, 1.6, 1.6, z=1.8, dome=0.8, mat=3)                 # the knob
    cv.box(29, 5.5, 6, 2.4, z=1.6, top=0.3, bevel=0.6, mat=3)            # the number plate
    cv.tone[62:, :] -= 0.15                                              # the skirting's shadow
    return _tile(cv, [ramp('#b8a88a', dark=0.45, light=1.12), ramp('#e0dccc', dark=0.5, light=1.06),
                      ramp('#e8e2d2', dark=0.5, light=1.05), ramp('#d8b048', dark=0.45, light=1.2)],
                 cavity=0.4, shadow=0.4)


def tex_checker_marble(name):
    """Chequered marble, black and white squares two to a side per unit, each square veined,
    polished, with fine joints between them."""
    rng = _rng(name)
    cv = Canvas(T, ground=-0.4, mat=0)
    for j in range(2):
        for i in range(2):
            m = (i + j) % 2
            cv.box(i * 32 + 0.4, j * 32 + 0.4, 31.2, 31.2, z=0.0, top=0.5, bevel=0.8, mat=m, tone=rng.normal(0, 0.02))
            for _ in range(2):
                x, y = i * 32 + rng.uniform(2, 30), j * 32 + rng.uniform(2, 30)
                pts = [(x, y)]
                for _ in range(5):
                    x, y = x + rng.uniform(2, 6), y + rng.normal(0, 3)
                    pts.append((x, y))
                cv.stroke(pts, 0.8, dome=0.2, mode='carve')
    return _tile(cv, [MARBLE_W, MARBLE_B], dither=0.12, cavity=0.3, shadow=0.2)


TEXTURES = {'checker_marble': lambda n: (tex_checker_marble(n), None), 'door_hall': lambda n: (tex_door_hall(n), None),
            'tall_window': lambda n: tex_tall_window(n), 'tall_window_top': lambda n: tex_tall_window(n, top=True)}
TEXTURE_REFLECT = {'checker_marble': 0.35}
TEXTURE_NOISE = {'checker_marble': 0.3, 'tall_window': 0.5, 'tall_window_top': 0.5, 'door_hall': 0.4}
SPRITES = {
    'chess_pawn': spr_chess_pawn, 'chess_rook': spr_chess_rook, 'chess_bishop': spr_chess_bishop,
    'chess_knight': spr_chess_knight, 'chess_queen': spr_chess_queen, 'chess_king': spr_chess_king,
    'melting_clock': spr_melting_clock, 'hourglass': spr_hourglass, 'stone_arch': spr_stone_arch,
    'stair_float': spr_stair_float, 'paper_boat': spr_paper_boat, 'jellyfish': spr_jellyfish,
    'sky_lantern': spr_sky_lantern, 'book_fly': spr_book_fly,
}
SPRITE_HEIGHT = {'chess_pawn': 0.9, 'chess_rook': 1.1, 'chess_bishop': 1.3, 'chess_knight': 1.2, 'chess_queen': 1.45,
                 'chess_king': 1.55, 'melting_clock': 0.6, 'hourglass': 0.6, 'stone_arch': 2.4, 'stair_float': 2.0,
                 'paper_boat': 0.3, 'jellyfish': 0.9, 'sky_lantern': 0.34, 'book_fly': 0.3}
PROP_DEFAULTS = {
    'jellyfish': {'blend': 'additive', 'opacity': 0.9, 'shadow': False},
    'sky_lantern': {'aura': {'color': [1.0, 0.66, 0.3], 'strength': 0.5, 'radius': 0.3}, 'shadow': False},
    'book_fly': {'shadow': False},
}
NO_CONTACT_SHADOW = {'melting_clock', 'jellyfish', 'sky_lantern', 'book_fly'}

"""The highway: what a road scene (road.py) needs that nothing else drew - cars seen from behind, as you follow them
down a road (a red convertible with two in it for your own, a compact, a sedan, a box truck), their tail lights
glowing; a chevron sign before a bend, a billboard on its legs, a checkpoint banner over the road on two poles, a
traffic cone; a road tunnel's rings and its portal. Drawn with the pixel-art toolkit (scripts/pixelart.py).
"""
import numpy as np
from PIL import Image, ImageDraw

from biomes import _prop
from pixelart import Canvas, ramp
from texlib import T, _rng, col, fbm, vnoise

RED = ramp('#c41e2a', dark=0.32, light=1.5, warm=0.1)
TAIL = ramp(['#5a0c0c', '#9a160e', '#e0301a', '#ff6436', '#ff9c68', '#ffd2b4'])      # a lamp's red, lit
PLATE = ramp('#d8d6cc', dark=0.5, light=1.3)
TYRE = ramp('#1c1c20', dark=0.6, light=2.2)
TRIM = ramp('#2c2c34', dark=0.5, light=1.9)
HAIR_D = ramp('#3e2618', dark=0.4, light=1.6)
HAIR_B = ramp('#e2b862', dark=0.45, light=1.35, warm=0.08)
CHROME = ramp('#9ea4ae', dark=0.4, light=1.7, cool=0.1)
BLUE = ramp('#2c5a9a', dark=0.35, light=1.5, cool=0.1)
WHITE = ramp('#d4d4cc', dark=0.45, light=1.3)
GLASS = ramp('#3a4a5a', dark=0.4, light=1.8, cool=0.15)
BOX = ramp('#d8d2c0', dark=0.45, light=1.25)
YELLOW = ramp('#f0c020', dark=0.4, light=1.3, warm=0.06)
POST = ramp('#7a7a80', dark=0.4, light=1.5)
ORANGE = ramp('#f06a1a', dark=0.4, light=1.35, warm=0.06)


def _tail_em(cv, mats):
    """The emission mask: the shapes of these materials glow."""
    return (np.isin(cv.mat, mats) & (cv.id > 0)).astype(np.float32)


def spr_sports_car():
    """A red convertible seen from behind, as you drive it: the top down, two in it - the driver dark-haired, the
    passenger's fair hair blown back - wide fenders over fat tyres, the rear deck catching the light, the tail
    lights glowing across its back either side of the plate, twin exhausts under the bumper."""
    w, h = 64, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (3, 49):                                              # the tyres, under the fenders
        cv.box(x, 25, 12, 14, z=0.6, top=0.5, bevel=2.2, mat=3)
    cv.polygon([(14, 2.4), (50, 2.4), (52, 9), (12, 9)], z=0.8, top=0.2, bevel=0.6, mat=8)   # the windscreen beyond
    cv.box(13.5, 1.6, 37, 1.6, z=0.9, top=0.4, bevel=0.5, mat=4)                 # its frame
    cv.stroke([(14.2, 2.4), (11.5, 11)], 1.3, z=0.9, dome=0.5, mat=4)
    cv.stroke([(49.8, 2.4), (52.5, 11)], 1.3, z=0.9, dome=0.5, mat=4)
    for x in (5.5, 58.5):                                          # the mirrors, out at its sides
        cv.ellipse(x, 10.5, 3.0, 1.9, z=1.4, dome=0.7, mat=0)
    cv.box(16, 4, 12, 10, z=1.0, top=0.5, bevel=1.6, mat=4)                      # the seats' backs
    cv.box(36, 4, 12, 10, z=1.0, top=0.5, bevel=1.6, mat=4)
    cv.ellipse(22, 5.5, 4.2, 4.8, z=1.9, dome=0.9, mat=5)                        # the driver
    cv.ellipse(42, 6, 4.4, 4.6, z=1.9, dome=0.9, mat=6)                          # the passenger, her hair blowing
    cv.stroke([(44, 4), (50, 6.5), (54, 9)], 3.0, z=1.7, dome=0.6, taper=(1.0, 0.3), mat=6)
    cv.polygon([(6, 12), (58, 12), (61, 21), (3, 21)], z=1.2, top=0.9, bevel=2.4, mat=0, tone=0.08)   # the deck
    for x in (9.5, 54.5):                                          # the fenders, swelling over the tyres
        cv.ellipse(x, 21, 7, 6.5, z=1.35, dome=0.55, mat=0)
    cv.box(4, 19, 56, 12, z=1.3, top=0.45, bevel=2.6, mat=0, tone=-0.04)        # its back
    cv.box(7, 21, 15, 4, z=1.7, top=0.2, bevel=0.6, mat=1)                       # the tail lights
    cv.box(42, 21, 15, 4, z=1.7, top=0.2, bevel=0.6, mat=1)
    cv.box(23, 21, 18, 5, z=1.55, top=0.2, bevel=0.6, mat=4)                     # the panel between them
    cv.box(26.5, 22, 11, 3.6, z=1.75, top=0.15, bevel=0.4, mat=2)                # the plate
    cv.box(5, 28.5, 54, 4, z=1.5, top=0.4, bevel=1.2, mat=4)                     # the bumper
    for x in (17, 47):                                             # twin exhausts
        cv.ellipse(x, 33, 1.8, 1.3, z=1.6, dome=0.4, mat=7)
    return _prop(cv, [RED, TAIL, PLATE, TYRE, TRIM, HAIR_D, HAIR_B, CHROME, GLASS], em=_tail_em(cv, [1]),
                 relief=1.0, cavity=0.45, shadow=0.45)


# the traffic's paint: each car drawn a few ways (assets.VARIANTS), one picked by where it stands
COMPACT_PAINT = [ramp('#2c5a9a', dark=0.35, light=1.5, cool=0.1), ramp('#b8282a', dark=0.35, light=1.5),
                 ramp('#3a7a4a', dark=0.35, light=1.5), ramp('#e2d8c2', dark=0.45, light=1.25, warm=0.04)]
SEDAN_PAINT = [ramp('#d4d4cc', dark=0.45, light=1.3), ramp('#5a5e66', dark=0.4, light=1.8),
               ramp('#22242a', dark=0.5, light=2.6), ramp('#6e2026', dark=0.35, light=1.6)]


def spr_car_compact():
    return _car_compact(0)


def _car_compact(k):
    """A small rounded car seen from behind, in blue (red, green or cream: `variant` 1 to 3): its roof and rear
    window, round tail lights, a chrome bumper."""
    w, h = 44, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (2, 33):
        cv.box(x, 27, 9, 12, z=0.6, top=0.5, bevel=2.0, mat=3)
    cv.ellipse(22, 14, 17, 12, z=1.0, dome=0.8, mat=0)                           # the roof
    cv.ellipse(22, 13, 11, 6.5, z=1.6, dome=0.3, mat=4)                          # the rear window
    cv.box(3, 18, 38, 14, z=1.3, top=0.6, bevel=3.0, mat=0, tone=0.02)           # its back
    for x in (7, 37):
        cv.ellipse(x, 23, 3, 3, z=1.8, dome=0.4, mat=1)                          # round tail lights
    cv.box(15, 23, 14, 4, z=1.6, top=0.1, bevel=0.4, mat=2)                      # the plate
    cv.box(3, 29, 38, 3.4, z=1.7, top=0.5, bevel=1.0, mat=5)                     # the bumper
    return _prop(cv, [COMPACT_PAINT[k], TAIL, PLATE, TYRE, GLASS, CHROME], em=_tail_em(cv, [1]),
                 relief=1.0, cavity=0.45, shadow=0.45)


def spr_car_sedan():
    return _car_sedan(0)


def _car_sedan(k):
    """A boxy sedan seen from behind, pale (grey, black or maroon: `variant` 1 to 3): a roof over a raked rear
    window, a trunk lid, wide tail lights."""
    w, h = 52, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (3, 40):
        cv.box(x, 31, 9, 12, z=0.6, top=0.5, bevel=2.0, mat=3)
    cv.polygon([(10, 4), (42, 4), (46, 15), (6, 15)], z=1.0, top=0.8, bevel=1.4, mat=0)       # the roof
    cv.polygon([(11, 6), (41, 6), (44, 15), (8, 15)], z=1.3, top=0.3, bevel=0.8, mat=4)       # the rear window
    cv.box(3, 15, 46, 6, z=1.4, top=0.9, bevel=1.6, mat=0, tone=0.06)            # the trunk lid
    cv.box(3, 20, 46, 13, z=1.3, top=0.5, bevel=2.2, mat=0)                      # its back
    cv.box(5, 22, 11, 4.5, z=1.7, top=0.2, bevel=0.5, mat=1)
    cv.box(36, 22, 11, 4.5, z=1.7, top=0.2, bevel=0.5, mat=1)
    cv.box(19.5, 23.5, 13, 4, z=1.6, top=0.1, bevel=0.4, mat=2)
    cv.box(3, 31, 46, 3.6, z=1.6, top=0.4, bevel=1.0, mat=5)
    return _prop(cv, [SEDAN_PAINT[k], TAIL, PLATE, TYRE, GLASS, TRIM], em=_tail_em(cv, [1]),
                 relief=1.0, cavity=0.45, shadow=0.45)


def spr_box_truck():
    """A delivery truck seen from behind: a tall box with a roll-up door, small tail lights low down, dual wheels,
    a bumper of black steel."""
    w, h = 48, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (2, 37):
        cv.box(x, 52, 9, 11, z=0.6, top=0.5, bevel=1.8, mat=3)
    cv.box(2, 2, 44, 50, z=1.0, top=0.4, bevel=1.4, mat=0)                       # the box
    for y in range(8, 48, 6):                                      # the door's slats
        cv.stroke([(6, y), (42, y)], 0.7, dome=0.3, mode='carve')
    cv.box(21, 44, 6, 3, z=1.3, top=0.2, bevel=0.4, mat=4)                       # its handle
    cv.box(3, 49, 42, 4, z=1.4, top=0.3, bevel=0.8, mat=4)                       # the sill
    cv.box(4, 53, 6, 3, z=1.6, top=0.1, bevel=0.4, mat=1)
    cv.box(38, 53, 6, 3, z=1.6, top=0.1, bevel=0.4, mat=1)
    cv.box(18, 53, 12, 3.6, z=1.6, top=0.1, bevel=0.4, mat=2)
    cv.box(1, 57, 46, 3, z=1.5, top=0.3, bevel=0.8, mat=4)
    return _prop(cv, [BOX, TAIL, PLATE, TYRE, TRIM], em=_tail_em(cv, [1]), relief=1.0, cavity=0.45, shadow=0.45)


def spr_curve_sign():
    """A sign before a bend: chevrons in black on a yellow board, pointing left (`flip` it for a bend to the right),
    on two grey posts."""
    w, h = 40, 36
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (9, 29):
        cv.box(x, 14, 2.4, 22, z=0.6, top=0.5, bevel=0.6, mat=2)
    cv.box(1, 1, 38, 16, z=1.0, top=0.4, bevel=1.0, mat=0)
    for k in range(3):                                             # the chevrons
        x = 8 + k * 10
        cv.stroke([(x + 5, 3.5), (x, 9), (x + 5, 14.5)], 2.6, z=1.3, dome=0.2, mat=1)
    return _prop(cv, [YELLOW, TRIM, POST], relief=0.9, cavity=0.4, shadow=0.4)


def spr_billboard():
    return _billboard(0)


def _billboard(k):
    """A billboard on two legs, a frame round it and a catwalk under it, its ad in flat bands of colour: a sunset
    over the sea and a palm (`variant` 1: a cold drink, its bubbles rising; 2: an airliner climbing through
    clouds)."""
    w, h = 72, 52
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    board = (xx >= 2) & (xx < 70) & (yy >= 2) & (yy < 34)
    if k:
        _ad(rgba, k, board, yy, xx)
        return _billboard_frame(rgba, board, yy, xx)
    t = (yy - 2) / 32
    bands = np.array([[0.22, 0.16, 0.38], [0.62, 0.22, 0.42], [0.95, 0.42, 0.32], [0.99, 0.7, 0.36]], np.float32)
    k = np.clip((t * 4).astype(int), 0, 3)
    rgba[board, :3] = bands[k[board]]
    sun = board & (np.hypot(xx - 46, yy - 22) < 9) & (yy < 24)
    rgba[sun, :3] = [1.0, 0.86, 0.5]
    sea = board & (yy >= 24)
    rgba[sea, :3] = np.array([0.16, 0.3, 0.5], np.float32) + 0.08 * ((yy[sea] + xx[sea] // 3) % 3 == 0)[:, None]
    palm = Image.new('L', (w, h), 0)                                # a palm in silhouette against it
    d = ImageDraw.Draw(palm)
    d.line([(20, 31), (18, 22), (15, 11)], fill=255, width=2)
    for ex, ey in ((5, 12), (7, 6), (15, 4), (24, 6), (27, 12), (22, 15), (9, 16)):
        d.line([(15, 11), ((15 + ex) / 2, min(11, ey) - 1.5), (ex, ey)], fill=255, width=2)
    rgba[board & (np.asarray(palm) > 0), :3] = [0.12, 0.08, 0.12]
    return _billboard_frame(rgba, board, yy, xx)


def _ad(rgba, k, board, yy, xx):
    """A billboard's other ads, painted on its board."""
    if k == 1:                                                     # a cold drink on red, bubbles rising
        rgba[board, :3] = np.where(((yy[board] - 2) / 32 < 0.5)[:, None], [0.84, 0.12, 0.12], [0.72, 0.08, 0.1])
        glass = board & (np.abs(xx - 22) < 7 - (yy - 8) * 0.06) & (yy >= 8) & (yy < 31)
        rgba[glass, :3] = [0.36, 0.16, 0.08]
        rgba[glass & (yy < 11), :3] = [0.96, 0.92, 0.84]                         # the head on it
        rgba[glass & (np.abs(xx - 17.5) < 1), :3] = [0.6, 0.34, 0.2]              # light down its side
        rng = np.random.default_rng(6)
        for _ in range(14):
            cx, cy, r = rng.uniform(30, 66), rng.uniform(5, 31), rng.uniform(0.8, 2.2)
            ring = board & (np.abs(np.hypot(xx - cx, yy - cy) - r) < 0.6)
            rgba[ring, :3] = [0.98, 0.9, 0.86]
        band = board & (yy >= 25) & (yy < 30) & (xx >= 34) & (xx < 66)
        rgba[band, :3] = [0.98, 0.86, 0.3]
    else:                                                          # an airliner climbing through clouds
        t = (yy - 2) / 32
        rgba[board, :3] = (np.array([0.28, 0.52, 0.86]) * (1 - t[board, None]) +
                           np.array([0.62, 0.8, 0.96]) * t[board, None])
        for cx, cy, r in ((14, 26, 9), (24, 29, 8), (54, 12, 7), (62, 14, 6), (46, 30, 10)):
            cloud = board & (np.hypot((xx - cx) / 1.6, yy - cy) < r * 0.6)
            rgba[cloud, :3] = [0.96, 0.97, 1.0]
        plane = Image.new('L', (72, 52), 0)                        # an airliner side on, nose up, climbing
        d = ImageDraw.Draw(plane)
        d.ellipse([18, 15, 58, 21], fill=255)                                  # the fuselage
        d.polygon([(55, 16), (62, 18), (55, 20)], fill=255)                    # its nose
        d.polygon([(20, 16), (14, 8), (19, 8), (27, 16)], fill=255)            # the tail fin
        d.polygon([(34, 18), (44, 18), (30, 27), (25, 27)], fill=255)          # the near wing, swept back
        d.polygon([(16, 17), (22, 17), (17, 21), (13, 21)], fill=255)          # the tailplane
        m = np.asarray(plane.rotate(16, resample=Image.NEAREST, center=(38, 18))) > 0
        rgba[board & m, :3] = [0.95, 0.95, 0.97]
        stripe = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).rotate(0)) > 0
        band = Image.new('L', (72, 52), 0)
        ImageDraw.Draw(band).rectangle([18, 18, 58, 19], fill=255)
        bm = np.asarray(band.rotate(16, resample=Image.NEAREST, center=(38, 18))) > 0
        rgba[board & bm & stripe, :3] = [0.82, 0.14, 0.16]                    # a red line along it


def _billboard_frame(rgba, board, yy, xx):
    """The billboard round its board: the frame, the catwalk under it, its two legs."""
    h, w = rgba.shape[:2]
    rgba[board, 3] = 1.0
    frame = ((xx >= 0) & (xx < 72) & (yy >= 0) & (yy < 36)) & ~board
    rgba[frame, :3] = [0.82, 0.82, 0.8]
    rgba[frame, 3] = 1.0
    walk = (xx >= 0) & (xx < 72) & (yy >= 36) & (yy < 38)
    rgba[walk, :3] = [0.35, 0.35, 0.38]
    rgba[walk, 3] = 1.0
    for x0 in (12, 56):                                            # its legs
        leg = (xx >= x0) & (xx < x0 + 4) & (yy >= 36)
        rgba[leg, :3] = [0.42, 0.42, 0.45] * (1 - 0.25 * (xx[leg] >= x0 + 2))[:, None]
        rgba[leg, 3] = 1.0
    return rgba, np.zeros((h, w), np.float32)


def spr_checkpoint():
    """A checkpoint over the road: a banner chequered black and white with CHECKPOINT on a white band across its
    middle, slung between two red-and-white poles. Stand it at `x` 0 and scale it to the road: it is 2.6 tall
    and about twice as wide."""
    import lettering
    w, h = 132, 64
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    for x0 in (2, 124):                                            # the poles, banded
        pole = (xx >= x0) & (xx < x0 + 6)
        band = ((yy // 6) % 2 == 0)
        rgba[pole, :3] = np.where(band[pole][:, None], [0.86, 0.14, 0.12], [0.92, 0.92, 0.9])
        rgba[pole, :3] *= (1 - 0.3 * (xx[pole] >= x0 + 4))[:, None]
        rgba[pole, 3] = 1.0
    ban = (xx >= 8) & (xx < 124) & (yy >= 4) & (yy < 26)
    chq = ((xx // 4 + yy // 4) % 2 == 0)
    rgba[ban, :3] = np.where(chq[ban][:, None], 0.08, 0.92)
    rgba[ban, 3] = 1.0
    plate = (xx >= 22) & (xx < 110) & (yy >= 9) & (yy < 21)
    rgba[plate, :3] = [0.96, 0.95, 0.9]
    word, _ = lettering.sign('CHECKPOINT', 'painted', '#c0181c', None, 1, False, 0, 1, False)
    th, tw = word.shape[:2]
    y0, x0 = 15 - th // 2, 66 - tw // 2
    ink = word[..., 3] > 0.5
    rgba[y0:y0 + th, x0:x0 + tw][ink] = np.concatenate([word[..., :3], np.ones((th, tw, 1), np.float32)], -1)[ink]
    return rgba, np.zeros((h, w), np.float32)


def spr_traffic_cone():
    """A traffic cone: orange, two white bands, on a black square foot."""
    w, h = 14, 18
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(1, 15, 12, 3, z=0.4, top=0.5, bevel=0.6, mat=2)
    for k, (y0, y1) in enumerate(((1, 5), (5, 7.5), (7.5, 10.5), (10.5, 13), (13, 15.5))):
        def half(y):                                               # the cone widens toward its foot
            return 1.2 + (y - 1) * 0.3
        cv.polygon([(7 - half(y0), y0), (7 + half(y0), y0), (7 + half(y1), y1), (7 - half(y1), y1)],
                   z=1.0 + 0.02 * k, top=1.0, bevel=1.6, mat=k % 2)
    return _prop(cv, [ORANGE, WHITE, TRIM], relief=1.0, cavity=0.4, shadow=0.4)


def _tunnel_card(w, h, open_w, wall_top, crown, margin_top=0):
    """A card with a tunnel's opening cut in it, at the bottom middle: straight walls `open_w` px apart up to
    `wall_top` px from the card's foot, then an arch to its crown `crown` px up. Returns the yy, xx grids and the
    masks: the opening, and a band round its edge (the tunnel's lining, seen edge on)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    up = h - yy                                                   # height above the card's foot, px
    cx, a = w / 2, open_w / 2
    rise = crown - wall_top
    inside = (np.abs(xx - cx) < a) & ((up < wall_top) | (((xx - cx) / a) ** 2 + ((up - wall_top) / rise) ** 2 < 1))
    grow = 1.12
    lining = (np.abs(xx - cx) < a * grow) & ((up < wall_top) | (((xx - cx) / (a * grow)) ** 2 +
                                                                 ((up - wall_top) / (rise * grow + 2)) ** 2 < 1))
    return yy, xx, up, inside, lining & ~inside


def spr_tunnel_ring():
    """One ring of a road tunnel, end on: pale tiles round the opening (the lining, edge on) in a band of dark
    concrete, a lamp at the crown. Set them across the road every 1.2 or so, down the `middle` - each frames the next
    and the linings join into the tunnel, its lamps into a line down its roof; a `tunnel_portal` at its mouth."""
    w, h = 320, 96                                                 # wide: the hill's mass round the tube
    yy, xx, up, inside, lining = _tunnel_card(w, h, 128, 52, 80)
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    tile = (((xx // 6) + (yy // 6)) % 2 == 0)
    rgba[..., :3] = [0.18, 0.18, 0.2]
    rgba[lining, :3] = np.where(tile[lining][:, None], [0.74, 0.74, 0.7], [0.66, 0.66, 0.63])
    edge = lining & (np.abs(up - 4) < 3)                           # a kerb along the foot of the walls
    rgba[edge, :3] = [0.5, 0.5, 0.52]
    lamp = (np.abs(xx - w / 2) < 8) & (up > 80 - 1) & (up < 80 + 4)
    rgba[lamp, :3] = [1.0, 0.78, 0.42]
    em[lamp] = 1.0
    rgba[..., 3] = (~inside).astype(np.float32)
    return rgba, em


def spr_brick_ring():
    """One ring of a brick barrel vault, end on - a canal tunnel's: an arched opening, the vault's brick seen edge on
    round it in a band, dark brick beyond, moss and wet streaks down it. A row of them down the `middle` every unit
    makes the vault; at its own size the opening is 2.6 wide and its crown 2.2 over its foot (the water)."""
    w, h = 300, 150
    yy, xx, up, inside, lining = _tunnel_card(w, h, 120, 46, 100)
    rgba = np.zeros((h, w, 4), np.float32)
    rng = np.random.default_rng(12)
    course = (yy // 5).astype(int)
    joint = ((yy % 5) == 0) | (((xx + (course % 2) * 6) % 12) == 0)             # brick courses
    rgba[..., :3] = [0.2, 0.13, 0.1]
    rgba[joint, :3] = [0.12, 0.1, 0.09]
    tone = 0.85 + 0.3 * rng.random((h // 5 + 1, w // 12 + 2))
    k = tone[course, ((xx + (course % 2) * 6) // 12).astype(int)]
    rgba[lining, :3] = (np.array([0.5, 0.3, 0.22]) * k[lining][:, None])           # the vault's face, edge on
    rgba[lining & joint, :3] = [0.26, 0.22, 0.18]
    moss = _noise(h, w, 9, 14) > 0.6
    rgba[moss & ~inside, :3] = rgba[moss & ~inside, :3] * 0.6 + np.array([0.16, 0.26, 0.1]) * 0.4
    wet = (_noise(h, w, 3, 15) > 0.7) & (yy > 100)
    rgba[wet & ~inside, :3] *= 0.7
    rgba[..., 3] = (~inside).astype(np.float32)
    return rgba, np.zeros((h, w), np.float32)


def spr_tunnel_portal():
    """A road tunnel's mouth: a face of concrete round the opening, a darker band over it, set into a grassy
    hillside that rises over it and runs off to both sides (wider than the rings, which it hides). Stand it at the
    tunnel's mouth: at their own sizes its opening and a `tunnel_ring`'s are the same, so give both the same factor
    if you scale them."""
    w, h = 420, 154
    yy, xx, up, inside, lining = _tunnel_card(w, h, 128, 52, 80)
    rgba = np.zeros((h, w, 4), np.float32)
    rng = np.random.default_rng(5)
    hill = up < 112 + 36 * np.cos((xx - w / 2) / w * np.pi) - 8 * np.abs(np.sin(xx * 0.07)) - 30 * (
        np.abs(xx - w / 2) / (w / 2)) ** 3                                                        # the hillside
    face = (np.abs(xx - w / 2) < 92) & (up < 100)
    grass = rng.random((h, w)) * 0.12
    rgba[hill, :3] = (np.array([0.24, 0.34, 0.16]) + grass[hill][:, None] * np.array([1, 1.2, 0.6]))
    rgba[face, :3] = [0.56, 0.55, 0.52]
    rgba[face & (((yy // 10) + (xx // 22)) % 2 == 0), :3] = [0.52, 0.51, 0.48]               # its panels
    band = face & (up > 86) & (up < 100)
    rgba[band, :3] = [0.36, 0.36, 0.38]
    rgba[lining, :3] = [0.42, 0.42, 0.44]
    rgba[..., 3] = ((hill | face) & ~inside).astype(np.float32)
    return rgba, np.zeros((h, w), np.float32)


BAG = ramp('#17181b', dark=0.55, light=3.4, cool=0.12)          # black plastic, with a shine to it
RUBBER = ramp('#202022', dark=0.55, light=2.0)
PAPER = ramp('#d8d4c4', dark=0.55, light=1.2)
CAN = ramp('#b8282a', dark=0.4, light=1.6)
BOTTLE = ramp('#3a6a3a', dark=0.4, light=1.9, cool=0.08)


def spr_trash_bag():
    """A black rubbish bag, knotted at its neck and slumped where it was left: a lump of something inside, a crease
    or two, a shine on the plastic."""
    w, h = 26, 18
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(13, 12, 11.5, 5.8, z=1.0, dome=0.8, mat=0)                        # the body, slumped
    cv.ellipse(8.5, 9.5, 6, 4.8, z=1.3, dome=0.8, mat=0)                         # lumps of what is in it
    cv.ellipse(17, 9, 5.5, 4.4, z=1.25, dome=0.8, mat=0)
    cv.polygon([(11.5, 3.2), (14.5, 3.2), (14.8, 6), (11.2, 6)], z=1.4, top=0.5, bevel=0.6, mat=0)   # the neck
    cv.stroke([(13, 3.4), (9.5, 1.8), (8, 2.6)], 1.3, z=1.5, dome=0.5, taper=(1.0, 0.5), mat=0)      # its ears
    cv.stroke([(13, 3.4), (16.5, 1.6), (18, 2.4)], 1.3, z=1.5, dome=0.5, taper=(1.0, 0.5), mat=0)
    for pts in ([(5, 12), (8.5, 15)], [(15, 11), (18, 15)], [(12.5, 9), (12, 12)]):
        cv.stroke(pts, 0.7, dome=0.3, mode='carve')
    return _prop(cv, [BAG], relief=1.3, cavity=0.55, shadow=0.5)


def spr_old_tyre():
    """An old tyre dumped by the road, propped on its edge: worn tread round its rim, the hole through it."""
    w, h = 20, 20
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(10, 10, 9, 9, z=1.0, dome=0.7, mat=0)
    for k in range(16):                                            # the tread's blocks
        a = k * np.pi / 8
        cv.stroke([(10 + 7.6 * np.cos(a), 10 + 7.6 * np.sin(a)), (10 + 9.2 * np.cos(a), 10 + 9.2 * np.sin(a))],
                  0.8, dome=0.3, mode='carve')
    rgba, em = _prop(cv, [RUBBER], relief=1.2, cavity=0.55, shadow=0.45)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    r = np.hypot(xx - 10, yy - 10)
    rgba[r < 4.2, 3] = 0.0                                          # the hole
    rim = (r >= 4.2) & (r < 5.0)
    rgba[rim, :3] *= 0.55
    return rgba, em


def spr_trash():
    """Litter: a crumpled sheet of paper, a red can and a green bottle on their sides - a few pixels of colour
    in the grass at the side of a road."""
    w, h = 18, 8
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(4.5, 4.8, 3.6, 2.8, z=1.0, dome=0.8, rough=0.5, rng=np.random.default_rng(3), mat=0)   # the paper
    cv.box(8.5, 4, 3.6, 3, z=1.0, top=0.6, bevel=1.0, mat=1)                                         # the can
    cv.box(12, 4.4, 5.2, 2.6, z=1.0, top=0.7, bevel=1.1, mat=2)                                      # the bottle
    cv.box(16.6, 5.1, 1.4, 1.2, z=1.0, top=0.6, bevel=0.4, mat=2)
    return _prop(cv, [PAPER, CAN, BOTTLE], relief=1.0, cavity=0.4, shadow=0.4)


# ------------------------------------------------------------------ road furniture

AMBER = ramp('#f0a020', dark=0.5, light=1.4, warm=0.05)
STEEL = ramp('#8a9098', dark=0.4, light=1.6, cool=0.08)
SIGN_GREEN = (0.06, 0.38, 0.2)


def spr_reflector_post():
    """A marker post at the side of a road: white, a black band near its top with an amber reflector set in it,
    which catches the headlights - one every few units along a country road's verge."""
    w, h = 6, 22
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(1, 1, 4, 21, z=1.0, top=0.6, bevel=0.8, mat=0)
    cv.box(1, 3, 4, 4.5, z=1.05, top=0.6, bevel=0.5, mat=1)                      # the black band
    cv.box(2, 4, 2, 2.5, z=1.2, top=0.3, bevel=0.2, mat=2)                       # the reflector
    rgba, _ = _prop(cv, [WHITE, TRIM, AMBER], relief=0.8, cavity=0.3, shadow=0.35)
    return rgba, _tail_em(cv, [2]) * 0.55


def spr_highway_lamp():
    """A highway's street lamp: a tall steel pole, its arm curving out over the road to a long lamp head whose
    underside glows. The arm reaches right: `flip` the row so those on the right reach back over the road. Give the
    row a `light` hung out under the head (`x` about 1.2, `z` 3.4)."""
    w, h = 36, 72
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(3, 10, 3.6, 62, z=1.0, top=0.5, bevel=1.0, mat=0)                       # the pole
    cv.box(2, 66, 5.6, 6, z=1.1, top=0.5, bevel=1.0, mat=0)                        # its foot
    cv.stroke([(4.8, 12), (6.5, 6), (12, 3.2), (22, 3.4)], 1.8, z=1.2, dome=0.5, mat=0)   # the arm
    cv.box(20, 2, 14, 4.2, z=1.3, top=0.6, bevel=1.2, mat=0)                       # the head
    cv.box(21, 5, 12, 1.6, z=1.4, top=0.2, bevel=0.3, mat=1)                       # its lamp, underneath
    rgba, _ = _prop(cv, [STEEL, ramp('#ffc070', dark=0.7, light=1.2, warm=0.1)], relief=0.9, cavity=0.35,
                    shadow=0.4)
    return rgba, _tail_em(cv, [1])


def _road_sign(text_lines, arrow, w, h):
    """A motorway sign: green, a white border, white lettering, an arrow."""
    import lettering
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = SIGN_GREEN
    rgba[..., 3] = 1.0
    rgba[:2, :, :3] = rgba[-2:, :, :3] = rgba[:, :2, :3] = rgba[:, -2:, :3] = 0.92
    rgba[:2, :, :3] = rgba[:2, :, :3]
    y = 5
    for t in text_lines:
        m = lettering.mask(t, 1, False)
        mh, mw = m.shape
        x = 5
        rgba[y:y + mh, x:x + mw][m] = [0.95, 0.95, 0.93, 1.0]
        y += mh + 3
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ax, ay = w - 11, h - 8                                             # the arrow, pointing ahead (or ahead right)
    if arrow == 'up':
        head = (yy >= ay - 9) & (yy < ay - 3) & (np.abs(xx - ax) <= (yy - (ay - 9)) * 0.9)
        shaft = (np.abs(xx - ax) < 1.5) & (yy >= ay - 4) & (yy < ay + 4)
    else:
        u, v = (xx - ax + yy - ay) / 1.414, (xx - ax - (yy - ay)) / 1.414
        head = (v >= 2) & (v < 8) & (np.abs(u) <= (8 - v) * 0.9)
        shaft = (np.abs(u) < 1.5) & (v > -6) & (v < 3)
    rgba[head | shaft, :3] = 0.95
    return rgba


def spr_sign_gantry():
    """A gantry over a motorway: a steel truss on two lattice legs, two green signs hung from it - the city ahead,
    the airport off to the right - white lettering, arrows. Stand it at `x` 0, scaled to the road: it is 3.2 tall
    and spans about seven units, its legs outside a three-lane road."""
    w, h = 160, 72
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    for x0 in (2, 151):                                                # the legs, lattice
        leg = (xx >= x0) & (xx < x0 + 7) & (yy >= 6)
        web = leg & (((xx - x0 + yy) % 8 < 2) | ((x0 + 6 - xx + yy) % 8 < 2) | (xx == x0) | (xx == x0 + 6))
        rgba[web, :3] = [0.55, 0.57, 0.6]
        rgba[web, 3] = 1.0
    truss = (yy >= 6) & (yy < 15) & (xx >= 2) & (xx < 158)
    tw = truss & ((yy == 6) | (yy == 14) | ((xx + yy) % 9 < 2) | ((xx - yy) % 9 < 2))
    rgba[tw, :3] = [0.58, 0.6, 0.63]
    rgba[tw, 3] = 1.0
    for (x0, lines, arrow) in ((18, ['CITY', 'CENTRE'], 'up'), (86, ['AIRPORT', 'EXIT 12'], 'right')):
        sign = _road_sign(lines, arrow, 56, 32)
        rgba[15:47, x0:x0 + 56] = sign
    return rgba, np.zeros((h, w), np.float32)


def spr_speed_sign():
    """A speed limit sign: a white disc in a red ring, 80 in black, on a grey post."""
    import lettering
    w, h = 20, 36
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    r = np.hypot(xx - 10, yy - 10)
    post = (np.abs(xx - 10) < 1.3) & (yy > 18)
    rgba[post, :3] = [0.55, 0.56, 0.58]
    rgba[post & (xx > 10), :3] = [0.4, 0.41, 0.43]
    rgba[r < 9.5, :3] = [0.85, 0.12, 0.1]
    rgba[r < 7.2, :3] = [0.95, 0.95, 0.93]
    rgba[(r < 9.5) | post, 3] = 1.0
    m = lettering.mask('80', 1, False)
    mh, mw = m.shape
    y0, x0 = 10 - mh // 2, 10 - mw // 2
    rgba[y0:y0 + mh, x0:x0 + mw][m, :3] = 0.08
    return rgba, np.zeros((h, w), np.float32)


def _traffic_light(k):
    w, h = 12, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(4.6, 20, 2.8, 20, z=1.0, top=0.5, bevel=0.8, mat=0)                     # the pole
    cv.box(1.5, 1, 9, 21, z=1.3, top=0.6, bevel=1.4, mat=1)                        # the housing
    for i, y in enumerate((5.5, 11, 16.5)):
        cv.box(3.6, y - 1, 4.8, 2.0, z=1.6, top=0.4, bevel=0.5, mat=1)             # the hoods
        cv.ellipse(6, y + 1.6, 2.3, 2.3, z=1.5, dome=0.4, mat=2 + i)
    lit = [ramp('#ff3020', dark=0.7, light=1.3), ramp('#ffb020', dark=0.7, light=1.3),
           ramp('#30ff80', dark=0.7, light=1.3)]
    dim = [ramp('#3a0e0c', dark=0.6, light=1.4), ramp('#3a2a0a', dark=0.6, light=1.4),
           ramp('#0c3018', dark=0.6, light=1.4)]
    lamps = [lit[i] if i == k else dim[i] for i in range(3)]
    rgba, _ = _prop(cv, [STEEL, ramp('#202224', dark=0.5, light=2.2)] + lamps, relief=0.9, cavity=0.35, shadow=0.4)
    return rgba, _tail_em(cv, [2 + k])


def spr_traffic_light():
    """A traffic light on its pole: three lamps under their hoods, one lit - red (drawn three ways: `variant` 0 red,
    1 amber, 2 green)."""
    return _traffic_light(0)


def spr_tyre_stack():
    """A stack of old tyres, every other one with a band of white paint round it - a crash barrier at the side of
    a race track."""
    w, h = 16, 18
    cv = Canvas(w, h, wrap=False, ground=-9)
    for i, y in enumerate((13.2, 9.0, 4.8, 0.6)):
        cv.ellipse(8, y + 2.1, 7.4, 2.3, z=1.0 + 0.03 * i, dome=0.9, mat=0)        # a tyre, side on: its tread
        if i % 2 == 0:
            cv.box(1.4, y + 1.2, 13.2, 1.8, z=1.4 + 0.03 * i, top=0.3, bevel=0.5, mat=1)
        for x in (3.5, 6.5, 9.5, 12.5):                                          # the tread's blocks
            cv.stroke([(x, y + 0.6), (x, y + 3.6)], 0.5, dome=0.3, mode='carve')
    return _prop(cv, [RUBBER, WHITE], relief=1.1, cavity=0.5, shadow=0.45)


def spr_road_barrier():
    """A road-works barrier: a plank striped red and white on two legs, an amber lamp on top, lit."""
    w, h = 28, 18
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    plank = (yy >= 6) & (yy < 11) & (xx >= 1) & (xx < 27)
    rgba[plank, :3] = np.where((((xx + yy) // 4) % 2 == 0)[plank][:, None], [0.85, 0.14, 0.1], [0.94, 0.94, 0.92])
    rgba[plank & (yy == 10), :3] *= 0.75
    for x0 in (4, 22):
        leg = (xx >= x0) & (xx < x0 + 2) & (yy >= 11)
        rgba[leg, :3] = [0.3, 0.3, 0.32]
        rgba[plank | leg, 3] = 1.0
    lamp = (np.hypot(xx - 6.5, yy - 3.5) < 2.6)
    rgba[lamp, :3] = [1.0, 0.7, 0.2]
    rgba[lamp, 3] = 1.0
    em = lamp.astype(np.float32)
    return rgba, em


def spr_start_lights():
    """The start lights over a race track: a black panel of five columns of red lamps, all lit, slung between two
    poles. Stand it at `x` 0 over the start line: 3 tall, twice as wide."""
    w, h = 96, 48
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    for x0 in (2, 90):
        pole = (xx >= x0) & (xx < x0 + 4)
        rgba[pole, :3] = [0.5, 0.52, 0.55]
        rgba[pole & (xx >= x0 + 2.5), :3] = [0.36, 0.37, 0.4]
        rgba[pole, 3] = 1.0
    panel = (xx >= 14) & (xx < 82) & (yy >= 4) & (yy < 24)
    rgba[panel, :3] = [0.06, 0.06, 0.07]
    rgba[panel, 3] = 1.0
    bar = (yy >= 8) & (yy < 11) & (((xx >= 6) & (xx < 14)) | ((xx >= 82) & (xx < 90)))
    rgba[bar, :3] = [0.45, 0.46, 0.5]
    rgba[bar, 3] = 1.0
    for i in range(5):
        for y in (10, 18):
            lamp = np.hypot(xx - (23 + i * 12.5), yy - y) < 3.6
            rgba[lamp, :3] = [1.0, 0.16, 0.1]
            em[lamp] = 1.0
    return rgba, em


def dec_start_line():
    """A start line across a race track: a band of black and white squares, two rows deep. Lay it at `x` 0 with a
    `size` of the road's width."""
    h, w = 12, 96
    yy, xx = _grid(h, w)
    chq = ((xx // 6).astype(int) + (yy // 6).astype(int)) % 2 == 0
    rgb = np.where(chq[..., None], 0.92, 0.06).astype(np.float32) * np.ones(3, np.float32)
    return _decal(rgb, np.full((h, w), 0.95, np.float32))


# ------------------------------------------------------------------ marks on the road (decals)

def _noise(h, w, cell, seed):
    """Smooth value noise, 0-1, h x w, its blobs about `cell` px across."""
    rng = np.random.default_rng(seed)
    g = rng.random((h // cell + 3, w // cell + 3)).astype(np.float32)
    big = np.asarray(Image.fromarray(g, 'F').resize((g.shape[1] * cell, g.shape[0] * cell), Image.BICUBIC))
    return np.clip(big[cell:cell + h, cell:cell + w], 0, 1)


def _decal(rgb, a, em=None):
    h, w = a.shape
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = rgb
    rgba[..., 3] = np.clip(a, 0, 1)
    return rgba, np.zeros((h, w), np.float32) if em is None else em.astype(np.float32)


def _grid(h, w):
    return np.mgrid[0:h, 0:w].astype(np.float32) + 0.5


def dec_oil_stain():
    """Oil dripped where cars stand: a dark blotch soaked into the road, darkest at its heart, a faint blue sheen
    at its rim."""
    h = w = 32
    yy, xx = _grid(h, w)
    r = np.hypot((xx - 16) / 1.3, yy - 16) / 11 + (_noise(h, w, 6, 41) - 0.5) * 0.55
    a = np.clip((1 - r) * 2.0, 0, 1) * (0.55 + 0.3 * _noise(h, w, 3, 42))
    rim = np.clip(1 - np.abs(r - 0.82) / 0.1, 0, 1)
    rgb = np.array([0.045, 0.045, 0.05], np.float32) + rim[..., None] * np.array([0.04, 0.05, 0.11], np.float32)
    return _decal(rgb, a)


def dec_tyre_marks():
    """Skid marks: two streaks of rubber laid down the road where a car braked hard, wavering a little, heaviest
    in the middle and fading at both ends. A `size` of 1 is a car's track across, and four units long."""
    h, w = 128, 32
    yy, xx = _grid(h, w)
    t = yy / h
    sway = np.sin(t * 4.0 + 0.6) * 1.6 + np.sin(t * 11.0) * 0.4
    a = np.zeros((h, w), np.float32)
    for cx in (7.5, 24.5):
        a = np.maximum(a, np.clip(2.4 - np.abs(xx - cx - sway), 0, 1))
    fade = np.clip(np.minimum(t, 1 - t) * 4.5, 0, 1)
    return _decal(np.array([0.035, 0.035, 0.04], np.float32), a * fade * (0.5 + 0.5 * _noise(h, w, 3, 8)) * 0.8)


def dec_road_patch():
    """A patch in the road: a square of newer, darker asphalt where it was dug up, its seams sealed with tar."""
    h, w = 36, 52
    yy, xx = _grid(h, w)
    n = _noise(h, w, 4, 12)
    inside = (xx > 2.2 + n * 1.5) & (xx < w - 2.2 - n * 1.5) & (yy > 2.2 + n) & (yy < h - 2.2 - n)
    seam = ~inside & (xx > 0.6 + n) & (xx < w - 0.6 - n) & (yy > 0.6) & (yy < h - 0.6)
    rgb = np.zeros((h, w, 3), np.float32) + [0.15, 0.15, 0.16]
    rgb[np.random.default_rng(13).random((h, w)) < 0.12] = [0.24, 0.24, 0.25]
    rgb[seam] = [0.05, 0.05, 0.055]
    return _decal(rgb, (inside | seam).astype(np.float32) * 0.92)


def dec_pothole():
    """A pothole: the road broken through to the dark under it, a rim of crumbled asphalt round it, a crack or
    two running out from it."""
    h = w = 32
    yy, xx = _grid(h, w)
    n = _noise(h, w, 4, 23)
    r = np.hypot((xx - 16) / 1.35, yy - 16) / 8.5 + (n - 0.5) * 0.5
    hole, rim = r < 0.72, (r >= 0.72) & (r < 1.0)
    rgb = np.zeros((h, w, 3), np.float32) + [0.07, 0.065, 0.06]
    rgb[hole] *= (0.55 + 0.6 * np.clip((yy[hole] - 10) / 14, 0, 1))[:, None]      # its far wall in shadow
    rgb[rim] = (np.array([0.3, 0.29, 0.28]) * (0.75 + 0.5 * n[rim])[:, None])
    crack = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(crack)
    for pts in (((27, 15), (30, 12), (31.5, 7)), ((5, 18), (2, 21), (1, 26)), ((15, 27), (13, 31))):
        d.line(pts, fill=255, width=1)
    ck = (np.asarray(crack) > 0) & ~hole & ~rim
    rgb[ck] = [0.05, 0.045, 0.04]
    return _decal(rgb, hole * 0.95 + rim * 0.85 * (n > 0.3) + ck * 0.8)


def dec_leaf_litter():
    """Fallen leaves in autumn colours, lying thick in the middle and thinning out round it."""
    h = w = 48
    S = 4
    im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(31)
    cols = [(170, 72, 28), (196, 112, 34), (214, 160, 52), (140, 58, 30), (122, 92, 40), (188, 84, 40)]
    for _ in range(95):
        r, th = rng.random() ** 0.7 * 21, rng.random() * 2 * np.pi
        cx, cy = 24 + np.cos(th) * r, 24 + np.sin(th) * r * 0.9
        ln, ang = rng.uniform(2.0, 3.6), rng.random() * np.pi
        t = np.linspace(0, 2 * np.pi, 9)[:-1]
        px, py = np.cos(t) * ln, np.sin(t) * ln * 0.5
        pts = [((cx + px[k] * np.cos(ang) - py[k] * np.sin(ang)) * S,
                (cy + px[k] * np.sin(ang) + py[k] * np.cos(ang)) * S) for k in range(8)]
        c = cols[int(rng.integers(len(cols)))]
        k = rng.uniform(0.8, 1.1)
        d.polygon(pts, fill=(int(c[0] * k), int(c[1] * k), int(c[2] * k), 255))
    rgba = np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255
    rgba[..., :3] /= np.maximum(rgba[..., 3:4], 1e-3)
    rgba[..., 3] = np.clip(rgba[..., 3] * 1.4, 0, 1)
    return rgba, np.zeros((h, w), np.float32)


def dec_manhole():
    """A manhole cover: a disc of cast iron set in the road, a ring round it, a raised grid across it."""
    h = w = 24
    yy, xx = _grid(h, w)
    r = np.hypot(xx - 12, yy - 12)
    disc, ring = r < 10.5, (r >= 9.2) & (r < 10.5)
    xi, yi = xx.astype(int), yy.astype(int)
    grid = disc & ~ring & (((xi + yi) % 4 == 0) | ((xi - yi) % 4 == 0))
    rgb = np.zeros((h, w, 3), np.float32) + [0.2, 0.19, 0.18]
    rgb[ring] = [0.12, 0.115, 0.11]
    rgb[grid] = [0.3, 0.29, 0.27]
    return _decal(rgb, disc.astype(np.float32))


def dec_lane_arrow():
    """An arrow painted on a lane, pointing straight on, worn by the traffic over it. It lies along the road: a
    `size` of 0.45 makes it 1.8 units long."""
    h, w = 64, 16
    yy, xx = _grid(h, w)
    shaft = (np.abs(xx - 8) < 2.1) & (yy > 22) & (yy < 62)
    head = (yy >= 2) & (yy < 24) & (np.abs(xx - 8) < (yy - 2) * 0.34)
    a = (shaft | head) * (0.5 + 0.42 * _noise(h, w, 3, 61))
    return _decal(np.array([0.9, 0.9, 0.86], np.float32), a)


def dec_zebra_crossing():
    """A zebra crossing: broad white bars side by side across the road, worn grey where the wheels run. Lay it at
    `x` 0 with a `size` of the road's width."""
    h, w = 24, 96
    yy, xx = _grid(h, w)
    bars = ((xx - 1) % 10) < 5.6
    wheels = 0.75 + 0.25 * np.cos(xx / w * 2 * np.pi * 4)          # where the tyres run, the paint is worn
    a = bars * (0.45 + 0.4 * _noise(h, w, 3, 71)) * wheels
    return _decal(np.array([0.9, 0.9, 0.87], np.float32), a)


def dec_sand_drift():
    """Sand blown over the road: a pale drift with ripples in it, thinning out to stray grains at its edges."""
    h, w = 32, 64
    yy, xx = _grid(h, w)
    r = np.hypot((xx - 32) / 30, (yy - 16) / 13) + (_noise(h, w, 8, 51) - 0.5) * 0.6
    a = np.clip((1 - r) * 2.5, 0, 1)
    grains = (np.random.default_rng(53).random((h, w)) < 0.18) & (r < 1.3)
    ripple = np.sin(xx * 0.85 + _noise(h, w, 6, 52) * 6) > 0.55
    rgb = np.zeros((h, w, 3), np.float32) + [0.84, 0.74, 0.54]
    rgb[ripple] *= 0.9
    return _decal(rgb, np.maximum(a * 0.9, grains * 0.7))


def dec_pebbles():
    """Gravel spilled over a path: small stones in greys and browns, each with a lit side and a shadow."""
    h, w = 32, 48
    yy, xx = _grid(h, w)
    rng = np.random.default_rng(81)
    rgb = np.zeros((h, w, 3), np.float32)
    a = np.zeros((h, w), np.float32)
    cols = np.array([[0.52, 0.5, 0.47], [0.42, 0.38, 0.33], [0.6, 0.57, 0.52], [0.36, 0.34, 0.32]], np.float32)
    for _ in range(70):
        r, th = rng.random() ** 0.6 * 20, rng.random() * 2 * np.pi
        cx, cy = 24 + np.cos(th) * r * 1.1, 16 + np.sin(th) * r * 0.65
        rs = rng.uniform(0.7, 1.7)
        d = np.hypot(xx - cx, (yy - cy) * 1.25) / rs
        m = d < 1
        lit = np.clip(1.15 - 0.35 * ((xx - cx + rs * 0.4) ** 2 + (yy - cy + rs * 0.4) ** 2) / rs ** 2, 0.6, 1.2)
        rgb[m] = cols[int(rng.integers(len(cols)))] * lit[m][:, None]
        a[m] = 1.0
    return _decal(rgb, a)


# ------------------------------------------------------------------ walls along a road (textures, 64 px)

def tex_guard_rail(name):
    """A steel guard rail, for a wall along a road: a galvanised W-beam - two ridges catching the light, a groove
    between - bolted to a thin post, nothing else (see-through). Its post is at the tile's middle and its beam
    along the top third: `"tile": [1, 0.3]` on a wall 0.3 high puts a post every unit."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.zeros((T, T, 3), np.float32)
    beam = (yy >= 8) & (yy < 27)
    post = (xx >= 30) & (xx < 34) & (yy >= 27)
    prof = np.array([0.42, 0.55, 0.74, 0.86, 0.8, 0.7, 0.58, 0.44, 0.36, 0.48, 0.66, 0.84, 0.8, 0.7, 0.58, 0.46,
                     0.4, 0.34, 0.3], np.float32)                     # the W, top to bottom: ridge, groove, ridge
    rgb[beam] = (prof[yy[beam] - 8][:, None] * np.array([0.9, 0.93, 0.97], np.float32) *
                 (0.94 + 0.1 * rng.random(beam.sum()))[:, None])
    rgb[post] = np.where((xx[post] == 30)[:, None], [0.56, 0.58, 0.6], [0.34, 0.35, 0.37])
    bolts = ((xx == 31) | (xx == 32)) & ((yy == 12) | (yy == 21))
    rgb[bolts] = [0.2, 0.2, 0.21]
    refl = (xx >= 30) & (xx < 34) & (yy >= 15) & (yy < 18)           # a reflector on the post's bolt plate
    rgb[refl] = [0.95, 0.62, 0.16]
    return np.clip(rgb, 0, 1), None, (beam | post).astype(np.float32)


def tex_jersey_barrier(name):
    """A concrete safety barrier, for a wall along a road or down its middle: the narrow top catching the light,
    the upright face, the sloped foot, dirt splashed up from the road; a joint at each block's end
    (`"tile": [1.3, 0.27]` on a wall 0.27 high)."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    shade = np.select([yy < 7, yy < 40, yy < 56], [1.12, 0.9, 1.0], 0.72)
    base = col('#a8a49a') * (0.86 + 0.2 * fbm(T, rng, 6, 3))[..., None]
    rgb = base * shade[..., None]
    rgb *= (1 - 0.3 * np.clip((yy - 44) / 20, 0, 1) * (0.6 + 0.4 * vnoise(T, 10, rng)))[..., None]   # road dirt
    rgb[(yy >= 6) & (yy < 8)] *= 0.8
    rgb[(yy >= 39) & (yy < 41)] *= 0.86
    rgb[(xx < 1.5) | (xx >= 63)] *= 0.55                                   # the joint
    return np.clip(rgb, 0, 1), None


def _voronoi(rng, n, sx=1.0, sy=1.0):
    """Tileable cells over the texture: per pixel the distance to the nearest of n points and to the next (for
    cracks), and the nearest one's index. `sx`, `sy` stretch them."""
    pts = rng.random((n, 2)) * T
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    best = np.full((T, T), 1e9, np.float32)
    second = np.full((T, T), 1e9, np.float32)
    idx = np.zeros((T, T), np.int32)
    for i, (px, py) in enumerate(pts):
        for ox in (-T, 0, T):
            for oy in (-T, 0, T):
                d = np.hypot((xx - px - ox) / sx, (yy - py - oy) / sy)
                closer = d < best
                second = np.where(closer, best, np.minimum(second, d))
                idx = np.where(closer, i, idx)
                best = np.where(closer, d, best)
    return best, second, idx


def tex_cliff_face(name):
    """A face of grey granite, for a mountain's cliffs along a road: tall blocks split along their joints, each
    leaning its own way to the light, dark cracks between, streaks where water runs down, lichen in patches.
    Tile it 3 or 4 units."""
    rng = _rng(name)
    n = 8
    best, second, idx = _voronoi(rng, n, sx=0.42, sy=2.4)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    cx = np.array([np.median(xx[idx == i]) if (idx == i).any() else 0 for i in range(n)], np.float32)
    dx = (xx - cx[idx] + T / 2) % T - T / 2                                          # across its own block
    lean = (rng.random(n) * 2 - 1)[idx]                                             # each block faces its own way
    tone = (rng.random(n) * 0.24 - 0.1)[idx] + lean * dx * 0.012
    rgb = col('#7c7a74') * (0.86 + tone + 0.16 * fbm(T, rng, 8, 4))[..., None]
    rgb *= (1 - 0.55 * np.clip(1 - (second - best) / 1.1, 0, 1))[..., None]          # the joints
    ledge = (np.abs((yy + 9 * vnoise(T, 3, rng)) % 32 - 20) < 0.8) & (vnoise(T, 6, rng) > 0.45)
    rgb[ledge] *= 0.72                                                                # sheets split across it
    streak = (vnoise(T, 16, rng) > 0.62) * np.clip(1 - yy / 64, 0.2, 1)               # water stains down it
    rgb *= (1 - 0.22 * streak * (vnoise(T, 4, rng) > 0.4))[..., None]
    lichen = fbm(T, rng, 5, 3) > 0.8
    rgb[lichen] = rgb[lichen] * 0.75 + col('#a8aa80') * 0.25
    return np.clip(rgb, 0, 1), None


def tex_power_lines(name):
    """Power lines for a wall along a road at the poles' crossarms: three wires sagging between the poles, nothing
    else (see-through). Each wire sags over the width of the tile, so give the wall `"tile": [d, 1]` and stand the
    poles every d units from 0 (`"every": d, "from": 0`)."""
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    sag = 7 * (1 - ((xx + 0.5) / 32 - 1) ** 2)
    a = np.zeros((T, T), np.float32)
    for y0 in (5, 18, 31):
        a = np.maximum(a, (np.abs(yy - (y0 + sag)) < 0.9).astype(np.float32))
    rgb = np.zeros((T, T, 3), np.float32) + [0.07, 0.07, 0.08]
    return rgb, None, a


TEXTURES = {'guard_rail': lambda n: tex_guard_rail(n), 'jersey_barrier': lambda n: tex_jersey_barrier(n),
            'cliff_face': lambda n: tex_cliff_face(n), 'power_lines': lambda n: tex_power_lines(n)}
TEXTURE_NOISE = {'guard_rail': 0.3, 'jersey_barrier': 1.0, 'cliff_face': 1.0, 'power_lines': 0.0}

# ------------------------------------------------------------------ off the road

OLIVE = ramp('#6a6a3a', dark=0.35, light=1.5, warm=0.05)
MUD = ramp('#7a5a3a', dark=0.4, light=1.3, warm=0.06)
RALLY = ramp('#e8e4dc', dark=0.45, light=1.25)
RALLY_BLUE = ramp('#1e48a8', dark=0.35, light=1.6, cool=0.08)
LEATHER = ramp('#2a2a30', dark=0.5, light=2.2)
HELMET = ramp('#d8301e', dark=0.35, light=1.6, warm=0.05)
DUST = (0.72, 0.6, 0.46)


def spr_jeep():
    """An open-top four-by-four seen from behind, as you follow it down a dirt track: olive paint, a roll bar over
    the two in it, a spare wheel on the tailgate, small square tail lights, fat tyres, mud thrown up its back."""
    w, h = 56, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (2, 42):                                              # the tyres, chunky
        cv.box(x, 30, 12, 17, z=0.6, top=0.6, bevel=2.4, mat=3)
        for y in range(32, 46, 3):
            cv.stroke([(x + 1, y), (x + 11, y)], 0.6, dome=0.3, mode='carve')
    cv.ellipse(19, 7, 4.2, 4.6, z=1.6, dome=0.9, mat=5)                          # the driver's head
    cv.ellipse(37, 7.5, 4.0, 4.4, z=1.6, dome=0.9, mat=5)                        # the passenger's,
    cv.ellipse(37, 5.2, 6.2, 1.6, z=1.9, dome=0.5, mat=6)                        # under a bush hat
    cv.ellipse(37, 4.0, 3.6, 2.4, z=2.0, dome=0.8, mat=6)
    cv.box(8, 3, 3, 16, z=1.5, top=0.5, bevel=0.8, mat=4)                        # the roll bar
    cv.box(45, 3, 3, 16, z=1.5, top=0.5, bevel=0.8, mat=4)
    cv.box(8, 2, 40, 3, z=1.6, top=0.5, bevel=0.8, mat=4)
    cv.box(3, 16, 50, 18, z=1.2, top=0.6, bevel=2.0, mat=0)                      # the tub
    cv.box(5, 16, 46, 2.5, z=1.4, top=0.5, bevel=0.8, mat=0, tone=0.08)          # its rim
    cv.ellipse(28, 26, 8.5, 8.5, z=1.9, dome=0.7, mat=3)                         # the spare wheel
    cv.ellipse(28, 26, 3.4, 3.4, z=2.0, dome=0.3, mat=7)
    cv.box(5, 21, 6, 4, z=1.5, top=0.2, bevel=0.4, mat=1)                        # the tail lights
    cv.box(45, 21, 6, 4, z=1.5, top=0.2, bevel=0.4, mat=1)
    cv.box(2, 33, 52, 4, z=1.4, top=0.4, bevel=1.0, mat=4)                       # the bumper
    rng = np.random.default_rng(7)
    for _ in range(26):                                            # mud up its back
        x, y = rng.uniform(4, 52), rng.uniform(27, 35)
        cv.ellipse(x, y, rng.uniform(0.8, 2.2), rng.uniform(0.6, 1.4), z=1.55, dome=0.3, mat=2)
    return _prop(cv, [OLIVE, TAIL, MUD, TYRE, TRIM, HAIR_D, ramp('#9a8a5a', dark=0.4, light=1.4), CHROME],
                 em=_tail_em(cv, [1]), relief=1.0, cavity=0.45, shadow=0.45)


def spr_rally_car():
    """A rally car seen from behind, flat out on the dirt: a white hatchback in a blue livery, a wing on its roof,
    mud flaps, a bank of lights, its tail lights glowing, mud sprayed up its back."""
    w, h = 52, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (3, 39):
        cv.box(x, 30, 10, 13, z=0.6, top=0.5, bevel=2.0, mat=3)
    cv.polygon([(11, 6), (41, 6), (45, 17), (7, 17)], z=1.0, top=0.8, bevel=1.4, mat=0)        # the roof
    cv.polygon([(12, 8), (40, 8), (43, 17), (9, 17)], z=1.3, top=0.3, bevel=0.8, mat=4)        # the rear window
    cv.box(6, 2, 40, 3, z=1.5, top=0.6, bevel=0.8, mat=5)                        # the wing
    cv.box(9, 4, 3, 4, z=1.4, top=0.5, bevel=0.5, mat=5)
    cv.box(40, 4, 3, 4, z=1.4, top=0.5, bevel=0.5, mat=5)
    cv.box(3, 17, 46, 15, z=1.3, top=0.5, bevel=2.2, mat=0)                      # its back
    cv.box(3, 23, 46, 3, z=1.45, top=0.3, bevel=0.6, mat=5)                      # the livery's stripe
    cv.box(5, 19, 10, 4, z=1.6, top=0.2, bevel=0.5, mat=1)
    cv.box(37, 19, 10, 4, z=1.6, top=0.2, bevel=0.5, mat=1)
    cv.box(19.5, 26.5, 13, 4, z=1.6, top=0.1, bevel=0.4, mat=2)
    for x in (4, 41):                                              # mud flaps
        cv.box(x, 34, 7, 7, z=1.2, top=0.3, bevel=0.5, mat=6)
    rng = np.random.default_rng(9)
    for _ in range(30):
        x, y = rng.uniform(3, 49), rng.uniform(26, 37)
        cv.ellipse(x, y, rng.uniform(0.8, 2.0), rng.uniform(0.6, 1.3), z=1.7, dome=0.3, mat=7)
    return _prop(cv, [RALLY, TAIL, PLATE, TYRE, GLASS, RALLY_BLUE, TRIM, MUD], em=_tail_em(cv, [1]),
                 relief=1.0, cavity=0.45, shadow=0.45)


def spr_dirt_bike():
    """A dirt bike and its rider seen from behind, standing on the pegs: a red helmet, a dark jacket, the knobbly
    rear tyre, the tail light under the seat."""
    w, h = 24, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(9, 27, 6, 16, z=0.8, top=0.6, bevel=2.0, mat=3)                       # the rear tyre
    for y in range(29, 42, 3):
        cv.stroke([(9.5, y), (14.5, y)], 0.6, dome=0.3, mode='carve')
    cv.box(8, 24, 8, 4, z=1.2, top=0.5, bevel=1.0, mat=4)                        # the mudguard
    cv.box(10, 25, 4, 2, z=1.5, top=0.2, bevel=0.3, mat=1)                       # the tail light
    cv.stroke([(5, 33), (2, 34)], 1.6, z=1.0, dome=0.5, mat=4)                   # the pegs, the boots on them
    cv.stroke([(19, 33), (22, 34)], 1.6, z=1.0, dome=0.5, mat=4)
    cv.stroke([(6, 22), (5, 32)], 3.0, z=1.3, dome=0.8, mat=5)                   # the legs
    cv.stroke([(18, 22), (19, 32)], 3.0, z=1.3, dome=0.8, mat=5)
    cv.ellipse(12, 15, 7.5, 8.5, z=1.6, dome=0.8, mat=5)                         # the back, crouched
    cv.stroke([(5, 12), (1, 15)], 2.2, z=1.5, dome=0.7, mat=5)                   # arms out to the bars
    cv.stroke([(19, 12), (23, 15)], 2.2, z=1.5, dome=0.7, mat=5)
    cv.ellipse(12, 5, 4.6, 4.8, z=2.0, dome=0.9, mat=6)                          # the helmet
    return _prop(cv, [OLIVE, TAIL, PLATE, TYRE, TRIM, LEATHER, HELMET], em=_tail_em(cv, [1]),
                 relief=1.0, cavity=0.45, shadow=0.45)


def spr_dust_cloud():
    """Dust thrown up behind a car on a dirt road: a low cloud of puffs, billowing out and up, lit on top and
    dusky underneath. Give it an `opacity` of 0.6 to 0.85 and set it a little behind the car."""
    w, h = 64, 32
    cv = Canvas(w, h, wrap=False, ground=-9)
    rng = np.random.default_rng(21)
    for _ in range(22):                                            # puffs: big and low in the middle, smaller out
        cx = rng.uniform(8, 56)
        spread = abs(cx - 32) / 32
        cy = rng.uniform(16, 27) - (1 - spread) * 6
        r = rng.uniform(4.5, 8.5) * (1.1 - spread * 0.5)
        cv.ellipse(cx, cy, r, r * 0.8, z=1.0 + rng.uniform(0, 0.6), dome=0.9, mat=0)
    return _prop(cv, [ramp('#c4aa86', dark=0.5, light=1.25, warm=0.04)], outline=False, relief=1.2, cavity=0.3,
                 shadow=0.3)


# ------------------------------------------------------------------ on the water

HULL_W = ramp('#e8e6e0', dark=0.45, light=1.25)
HULL_R = ramp('#b02a24', dark=0.35, light=1.5)
NARROW = ramp('#24503a', dark=0.35, light=1.6)            # a narrowboat's green
NARROW_R = ramp('#9a2a1e', dark=0.35, light=1.5)
WOOD = ramp('#7a5434', dark=0.4, light=1.5, warm=0.06)
BRASS = ramp('#c8a040', dark=0.4, light=1.6, warm=0.08)


def spr_speedboat():
    """A speedboat seen from behind, as you follow it over the water: a white hull with a red stripe, the
    outboard motor on its transom, the driver in it, the water churned white at its stern. Set it a little into
    the water (`z` -0.05); the wake on the water behind it is a decal (`wake`)."""
    w, h = 52, 36
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(26, 9, 4.2, 4.6, z=1.6, dome=0.9, mat=4)                          # the driver's head
    cv.box(18, 10, 16, 8, z=1.3, top=0.6, bevel=1.4, mat=5)                      # his shoulders, a windscreen
    cv.polygon([(4, 14), (48, 14), (45, 28), (7, 28)], z=1.2, top=0.7, bevel=2.2, mat=0)       # the transom
    cv.box(5, 20, 42, 2.4, z=1.35, top=0.3, bevel=0.5, mat=1)                    # the stripe
    cv.box(21, 15, 10, 13, z=1.6, top=0.7, bevel=1.6, mat=2)                     # the outboard
    cv.box(23.5, 27, 5, 6, z=1.5, top=0.5, bevel=1.0, mat=2)                     # its leg, into the water
    rng = np.random.default_rng(4)
    for _ in range(40):                                            # white water at the stern
        x, y = rng.uniform(4, 48), rng.uniform(29, 35)
        cv.ellipse(x, y, rng.uniform(0.8, 2.4), rng.uniform(0.6, 1.4), z=1.0, dome=0.4, mat=3)
    return _prop(cv, [HULL_W, HULL_R, TRIM, ramp('#f2f6f8', dark=0.6, light=1.1), HAIR_D, GLASS],
                 relief=1.0, cavity=0.4, shadow=0.4)


def spr_narrowboat():
    """A narrowboat seen from its stern, going ahead of you down a canal: green paint and red trim, the brass of
    its tiller, the steerer standing at it in a cap, the chimney of its stove beyond him smoking."""
    w, h = 40, 52
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(29, 2, 3, 12, z=0.9, top=0.6, bevel=0.8, mat=4)                       # the chimney
    cv.ellipse(30.5, 2, 2.6, 1.4, z=1.0, dome=0.5, mat=4)
    cv.box(6, 12, 28, 18, z=1.0, top=0.6, bevel=1.6, mat=0)                      # the cabin's end
    cv.box(15, 15, 10, 13, z=1.15, top=0.3, bevel=0.8, mat=1)                    # its doors
    cv.ellipse(20, 15, 3.6, 3.9, z=1.7, dome=0.9, mat=5)                         # the steerer's head
    cv.box(15, 18, 10, 12, z=1.6, top=0.6, bevel=1.6, mat=6)                     # his coat
    cv.stroke([(20, 26), (32, 22)], 1.4, z=1.9, dome=0.5, mat=3)                 # the tiller
    cv.polygon([(3, 30), (37, 30), (34, 44), (6, 44)], z=1.2, top=0.7, bevel=2.0, mat=0)       # the counter
    cv.box(4, 31, 32, 2.2, z=1.4, top=0.3, bevel=0.4, mat=1)                     # its red band
    cv.box(18, 42, 4, 8, z=1.3, top=0.5, bevel=0.8, mat=2)                       # the rudder
    return _prop(cv, [NARROW, NARROW_R, WOOD, BRASS, TRIM, HAIR_D, ramp('#3a3226', dark=0.4, light=1.8)],
                 relief=1.0, cavity=0.4, shadow=0.4)


def spr_boat_bow():
    """The bow of your own boat, from inside it: its two gunwales running forward to the stem, the boards of its
    floor between, a lantern on a post at the bow, lit. A shot's `vehicle` for a boat ride: `"ahead": 0.9`,
    `"z": -0.12`, with a `light` for the lantern."""
    w, h = 64, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(2, 39), (62, 39), (35, 8), (29, 8)], z=0.6, top=0.4, bevel=2.0, mat=0)        # the floor, boards
    for x in (12, 22, 32, 42, 52):
        cv.stroke([(x, 39), (32, 9)], 0.5, dome=0.3, mode='carve')
    cv.stroke([(1, 39), (29, 7.5)], 3.2, z=1.4, dome=0.7, taper=(1.0, 0.5), mat=1)              # the gunwales
    cv.stroke([(63, 39), (35, 7.5)], 3.2, z=1.4, dome=0.7, taper=(1.0, 0.5), mat=1)
    cv.box(30.6, 2, 2.8, 8, z=1.6, top=0.5, bevel=0.6, mat=1)                   # the lantern's post
    cv.box(29, 0, 6, 4, z=1.9, top=0.5, bevel=0.8, mat=2)                        # the lantern
    cv.box(30, 1, 4, 2.4, z=2.0, top=0.2, bevel=0.3, mat=3)                      # its flame
    rgba, _ = _prop(cv, [WOOD, ramp('#5a3c22', dark=0.4, light=1.6), BRASS, ramp('#ffd080', dark=0.8, light=1.1)],
                    relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [3])


def dec_wake():
    """A boat's wake on the water behind it: a V of white foam spreading back from the stern, churned white water
    down its middle, breaking up as it spreads. Lay it behind the boat (`at` about its length back), `size` about
    three times the boat's width."""
    h, w = 96, 64
    yy, xx = _grid(h, w)
    t = yy / h                                                     # 0 at the stern, 1 far behind it
    spread = 4 + t * 26
    n = _noise(h, w, 4, 33)
    arms = np.clip(1.6 - np.abs(np.abs(xx - 32) - spread) / (1.2 + t * 2.4), 0, 1)
    churn = np.clip(1 - np.abs(xx - 32) / (3 + t * 9), 0, 1) * (1 - t) ** 0.6
    a = np.maximum(arms * (0.55 + 0.5 * n) * (1 - t) ** 0.4, churn * (0.6 + 0.4 * n))
    a = np.where(a > 0.25, a, 0)
    rgb = np.zeros((h, w, 3), np.float32) + [0.92, 0.95, 0.96]
    return _decal(rgb, np.clip(a * 1.1, 0, 1))


# ------------------------------------------------------------------ the neon city (wall textures)

LIT = [(1.0, 0.78, 0.5), (0.62, 0.8, 1.0), (1.0, 0.42, 0.78), (0.4, 1.0, 0.92), (1.0, 0.9, 0.7)]


def tex_tower_windows(name):
    """A tower's face at night, for a wall of buildings along a road: dark panels, a grid of windows four across
    and four up to a tile, some lit - warm, cool, a few in neon pink and cyan - most dark, a blind half down in
    one or two. Its lit windows glow."""
    rng = _rng(name)
    rgb = np.zeros((T, T, 3), np.float32) + [0.1, 0.11, 0.14]
    rgb *= (0.85 + 0.3 * fbm(T, rng, 8, 2))[..., None]
    em = np.zeros((T, T), np.float32)
    yy, xx = np.mgrid[0:T, 0:T]
    rgb[(yy % 16) == 15] *= 0.6                                         # the floors' lines
    for gy in range(4):
        for gx in range(4):
            y0, x0 = gy * 16 + 3, gx * 16 + 3
            win = (yy >= y0) & (yy < y0 + 10) & (xx >= x0) & (xx < x0 + 10)
            if rng.random() < 0.55:
                c = np.array(LIT[int(rng.choice(5, p=[0.36, 0.3, 0.12, 0.1, 0.12]))], np.float32)
                k = rng.uniform(0.55, 1.0)
                rgb[win] = c * k * (0.85 + 0.2 * rng.random((10, 10)))[(yy[win] - y0), (xx[win] - x0)][:, None]
                em[win] = k
                if rng.random() < 0.25:                                 # a blind half down
                    blind = win & (yy < y0 + int(rng.integers(3, 7))) & ((yy - y0) % 2 == 0)
                    rgb[blind] *= 0.45
                    em[blind] *= 0.3
            else:
                rgb[win] = [0.05, 0.06, 0.09]
                rgb[win & (xx - x0 + yy - y0 < 4)] = [0.16, 0.18, 0.24]   # the sky caught in the glass
    return np.clip(rgb, 0, 1), em


def tex_shopfront(name, glow=(1.0, 0.25, 0.7)):
    """A shop at the foot of a building in the neon city, for a wall along a street: its window lit warm with
    shelves in it, a shutter rolled half down, over it a sign board outlined in a neon tube (`glow`) with glyphs
    on it, a scrap of concrete above. One shop to a tile; its window, its sign and its tube glow."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    g = np.array(glow, np.float32)
    rgb = np.zeros((T, T, 3), np.float32) + [0.16, 0.16, 0.18]
    rgb *= (0.8 + 0.35 * fbm(T, rng, 6, 3))[..., None]
    em = np.zeros((T, T), np.float32)
    sign = (yy >= 8) & (yy < 22) & (xx >= 3) & (xx < 61)
    rgb[sign] = g * 0.22
    tube = sign & ((yy == 8) | (yy == 21) | (xx == 3) | (xx == 60))
    rgb[tube] = np.minimum(g * 1.3, 1.0)
    em[tube] = 1.0
    for k in range(5):                                                  # glyphs on the board
        x0 = 8 + k * 10 + int(rng.integers(0, 3))
        stroke = sign & (np.abs(xx - x0 - 2) < 1) & (yy >= 11) & (yy < 19)
        stroke |= sign & (yy == 11 + int(rng.integers(0, 6))) & (xx >= x0) & (xx < x0 + 5)
        stroke |= sign & (np.abs((xx - x0) - (yy - 11) * 0.6) < 0.8) & (yy >= 11) & (yy < 19) & (rng.random() < 0.5)
        rgb[stroke] = [1.0, 0.95, 0.85]
        em[stroke] = 0.9
    win = (yy >= 28) & (yy < 60) & (xx >= 6) & (xx < 58)
    rgb[win] = np.array([1.0, 0.78, 0.52], np.float32) * (0.45 + 0.3 * fbm(T, rng, 4, 2)[win])[:, None]
    em[win] = 0.5
    shelves = win & ((yy - 28) % 8 == 7)
    rgb[shelves] *= 0.5
    goods = win & ((yy - 28) % 8 < 7) & ((yy - 28) % 8 > 3) & (rng.random((T, T)) < 0.45)
    rgb[goods] = np.array(LIT, np.float32)[rng.integers(0, 5, goods.sum())] * 0.8
    shutter = win & (yy < 28 + int(rng.integers(6, 14)))
    rgb[shutter] = [0.42, 0.43, 0.46]
    rgb[shutter & ((yy % 2) == 0)] *= 0.7
    em[shutter] = 0.0
    frame = ((yy >= 26) & (yy < 28) & (xx >= 4) & (xx < 60)) | (((xx == 4) | (xx == 5) | (xx == 58) | (xx == 59))
                                                             & (yy >= 26) & (yy < 62))
    rgb[frame] = [0.08, 0.08, 0.09]
    return np.clip(rgb, 0, 1), em


# ------------------------------------------------------------------ the neon city (vehicles)

NIGHT_BODY = ramp('#2a2c3a', dark=0.4, light=2.4, cool=0.12)
NEON_C = ramp('#40f0ff', dark=0.7, light=1.15)
NEON_P = ramp('#ff40c0', dark=0.7, light=1.15)
TAXI = ramp('#f0c020', dark=0.4, light=1.3, warm=0.06)


def spr_hover_car():
    """A hover car seen from behind, as you race it through the neon city: a low dark wedge of a body edged in
    cyan light, a red light bar across its tail, twin jets glowing blue, and under it, where wheels would be, the
    glow it floats on. Stand it a little off the road (`z` 0.06)."""
    w, h = 60, 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(30, 22.5, 26, 4.5, z=0.4, dome=0.4, mat=4)                        # the glow under it
    cv.polygon([(14, 3), (46, 3), (54, 12), (6, 12)], z=1.0, top=0.8, bevel=1.6, mat=0)        # the canopy
    cv.polygon([(16, 4.5), (44, 4.5), (50, 11.5), (10, 11.5)], z=1.3, top=0.3, bevel=0.8, mat=5)  # its glass
    cv.polygon([(3, 11), (57, 11), (55, 21), (5, 21)], z=1.2, top=0.6, bevel=2.2, mat=0)       # the body
    cv.box(6, 13, 48, 2.2, z=1.5, top=0.2, bevel=0.4, mat=1)                     # the tail's light bar
    cv.box(3, 11, 54, 1.2, z=1.45, top=0.2, bevel=0.3, mat=2)                    # its cyan edge
    for x in (14, 46):                                             # the jets
        cv.ellipse(x, 18, 4.2, 2.6, z=1.6, dome=0.5, mat=3)
    return _prop(cv, [NIGHT_BODY, TAIL, NEON_C, ramp('#60a0ff', dark=0.7, light=1.2), ramp('#40d0ff', dark=0.8,
                                                                                         light=1.1), GLASS],
                 em=_tail_em(cv, [1, 2, 3, 4]), relief=1.0, cavity=0.4, shadow=0.4)


def spr_neon_bike():
    """A motorbike of the neon city and its rider, seen from behind: a long low bike lined in pink light, the rider
    crouched over it in a dark jacket and a white helmet, a red bar of tail light."""
    w, h = 28, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(10, 25, 8, 14, z=0.8, top=0.6, bevel=2.2, mat=3)                      # the back wheel, fat
    cv.box(6, 21, 16, 7, z=1.2, top=0.6, bevel=1.8, mat=0)                       # the tail
    cv.box(7, 22, 14, 1.6, z=1.5, top=0.2, bevel=0.3, mat=1)                     # its light bar
    cv.stroke([(6, 27), (6, 21)], 0.8, z=1.4, dome=0.4, mat=2)                   # pink lines down its flanks
    cv.stroke([(22, 27), (22, 21)], 0.8, z=1.4, dome=0.4, mat=2)
    cv.ellipse(14, 15, 8.5, 7.5, z=1.6, dome=0.8, mat=4)                         # the rider, crouched
    cv.stroke([(6, 12), (2, 15)], 2.2, z=1.5, dome=0.7, mat=4)
    cv.stroke([(22, 12), (26, 15)], 2.2, z=1.5, dome=0.7, mat=4)
    cv.ellipse(14, 6.5, 4.6, 4.8, z=2.0, dome=0.9, mat=5)                        # the helmet
    cv.box(10.5, 6, 7, 1.6, z=2.3, top=0.2, bevel=0.3, mat=2)                    # its band of light
    return _prop(cv, [NIGHT_BODY, TAIL, NEON_P, TYRE, LEATHER, WHITE], em=_tail_em(cv, [1, 2]),
                 relief=1.0, cavity=0.45, shadow=0.45)


def spr_taxi():
    """A city taxi seen from behind: yellow, a chequered band along its flank, the TAXI sign on its roof lit, its
    tail lights glowing."""
    import lettering
    w, h = 52, 46
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (3, 40):
        cv.box(x, 33, 9, 12, z=0.6, top=0.5, bevel=2.0, mat=3)
    cv.box(18, 2, 16, 6, z=1.6, top=0.6, bevel=0.8, mat=5)                       # the roof sign
    cv.polygon([(10, 8), (42, 8), (46, 18), (6, 18)], z=1.0, top=0.8, bevel=1.4, mat=0)        # the roof
    cv.polygon([(11, 10), (41, 10), (44, 18), (8, 18)], z=1.3, top=0.3, bevel=0.8, mat=4)      # the rear window
    cv.box(3, 18, 46, 16, z=1.3, top=0.5, bevel=2.2, mat=0)                      # its back
    cv.box(5, 21, 10, 4.5, z=1.7, top=0.2, bevel=0.5, mat=1)
    cv.box(37, 21, 10, 4.5, z=1.7, top=0.2, bevel=0.5, mat=1)
    cv.box(19.5, 25.5, 13, 4, z=1.6, top=0.1, bevel=0.4, mat=2)
    cv.box(3, 33, 46, 3.6, z=1.6, top=0.4, bevel=1.0, mat=6)
    rgba, _ = _prop(cv, [TAXI, TAIL, PLATE, TYRE, GLASS, ramp('#fff4c0', dark=0.8, light=1.1), TRIM],
                    relief=1.0, cavity=0.45, shadow=0.45)
    em = _tail_em(cv, [1, 5])
    word = lettering.mask('TAXI', 1, False)
    mh, mw = word.shape
    y0, x0 = 5 - mh // 2, 26 - mw // 2
    rgba[y0:y0 + mh, x0:x0 + mw][word, :3] = [0.15, 0.12, 0.05]
    chq = np.zeros(rgba.shape[:2], bool)                           # the chequered band
    yy, xx = np.mgrid[0:h, 0:w]
    chq = (yy >= 28) & (yy < 31) & (xx >= 4) & (xx < 48) & (((xx // 2) + (yy // 2)) % 2 == 0)
    rgba[chq & (rgba[..., 3] > 0.5), :3] = [0.1, 0.1, 0.1]
    return rgba, em


# ------------------------------------------------------------------ the fairground

COASTER_RED = ramp('#d02a2a', dark=0.35, light=1.5, warm=0.05)
SHIRT_B = ramp('#3a68c0', dark=0.4, light=1.5)
SHIRT_Y = ramp('#e8c040', dark=0.4, light=1.3)
SKIN = ramp('#d8a07a', dark=0.45, light=1.25, warm=0.05)


def tex_coaster_track(name):
    """A roller coaster's track, for a road scene's `surface`: two steel rails half a unit either side of the middle,
    the ties across between them every quarter unit, and nothing else - the ground far below shows through it.
    Give the road a `width` of about 1.4."""
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.zeros((T, T, 3), np.float32)
    rail = (np.abs(xx - 31.5) < 3.2)                       # at the tile's middle: x = +-0.5 from the road's
    ties = ((yy % 16) < 4)                                 # every quarter unit
    rgb[ties] = [0.36, 0.26, 0.18]
    rgb[ties & ((yy % 16) == 0)] = [0.48, 0.36, 0.24]
    rgb[rail] = [0.62, 0.64, 0.68]
    rgb[rail & (np.abs(xx - 31.5) < 1.2)] = [0.86, 0.88, 0.9]          # its top, catching the light
    return rgb, None, (rail | ties).astype(np.float32)


def spr_coaster_car():
    """The front car of a roller coaster seen from behind, from the seat behind it: red, its lap bar down, two
    riders with their arms thrown up."""
    w, h = 56, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x0, mat in ((17, 4), (39, 5)):                                 # the riders' arms, up
        cv.stroke([(x0 - 8, 22), (x0 - 12, 10), (x0 - 13, 2)], 2.6, z=1.4, dome=0.7, taper=(1.0, 0.7), mat=6)
        cv.stroke([(x0 + 8, 22), (x0 + 12, 10), (x0 + 13, 2)], 2.6, z=1.4, dome=0.7, taper=(1.0, 0.7), mat=6)
        cv.ellipse(x0 - 13, 2.5, 2.0, 2.0, z=1.6, dome=0.8, mat=6)
        cv.ellipse(x0 + 13, 2.5, 2.0, 2.0, z=1.6, dome=0.8, mat=6)
        cv.ellipse(x0, 25, 8, 6.5, z=1.3, dome=0.8, mat=mat)                     # their backs
        cv.ellipse(x0, 15.5, 4.4, 4.8, z=1.6, dome=0.9, mat=7 if x0 == 17 else 8)  # their heads
    cv.box(3, 27, 50, 14, z=1.2, top=0.6, bevel=2.4, mat=0)                      # the car's back
    cv.box(5, 27, 46, 2.4, z=1.4, top=0.4, bevel=0.6, mat=1)                     # its rim
    cv.box(3, 37, 50, 3, z=1.5, top=0.3, bevel=0.6, mat=2)                       # a stripe
    for x in (6, 44):
        cv.box(x, 40, 6, 6, z=1.0, top=0.5, bevel=1.2, mat=3)                    # wheels on the rails
    return _prop(cv, [COASTER_RED, TRIM, ramp('#f0d040', dark=0.4, light=1.3), CHROME, SHIRT_B, SHIRT_Y, SKIN,
                      HAIR_D, HAIR_B], relief=1.0, cavity=0.45, shadow=0.45)


def tex_coaster_frame(name):
    """The steel frame under a roller coaster's track, for walls standing down from it to the ground: uprights,
    cross braces and girders, white, open between (see-through)."""
    yy, xx = np.mgrid[0:T, 0:T]
    up = (xx % 32) < 3
    girder = (yy % 32) < 3
    brace = (np.abs(((xx % 32) - (yy % 32))) < 1.6) | (np.abs(((xx % 32) + (yy % 32)) - 32) < 1.6)
    a = up | girder | brace
    rgb = np.zeros((T, T, 3), np.float32) + [0.86, 0.86, 0.84]
    rgb[up & ((xx % 32) == 2)] = [0.6, 0.6, 0.62]
    rgb[brace & ~up & ~girder] *= 0.9
    return rgb, None, a.astype(np.float32)


# ------------------------------------------------------------------ the mine

TIMBER = ramp('#6a4a2c', dark=0.4, light=1.5, warm=0.06)
IRON = ramp('#4a4644', dark=0.45, light=1.9)


def tex_rail_track(name):
    """A railway's track for a road scene's `surface`: two steel rails half a unit either side of the middle on
    wooden sleepers every quarter unit, bedded in grey ballast. Give the road a `width` of about 1.4; a mine's
    tracks, a railway's."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    n = fbm(T, rng, 16, 3)
    rgb = np.zeros((T, T, 3), np.float32) + [0.4, 0.38, 0.36]
    rgb *= (0.7 + 0.5 * n)[..., None]                                   # the ballast, stones in it
    stones = rng.random((T, T)) < 0.25
    rgb[stones] *= rng.uniform(0.7, 1.25, stones.sum())[:, None]
    ties = (yy % 16) < 5                                              # the sleepers, right across
    rgb[ties] = (np.array([0.34, 0.24, 0.16]) * (0.8 + 0.35 * fbm(T, rng, 8, 2)[ties])[:, None])
    rgb[ties & ((yy % 16) == 0)] *= 1.25
    rail = np.abs(xx - 31.5) < 3.0                                   # at the tile's middle: x = +-0.5 from the road's
    rgb[rail] = [0.42, 0.42, 0.44]
    rgb[np.abs(xx - 31.5) < 1.0] = [0.78, 0.78, 0.8]                # its worn top, bright
    return np.clip(rgb, 0, 1), None


def spr_mine_frame():
    """A mine's timber set, end on: two posts and a cap across them, a lamp hung from its middle, lit. A row of them
    down the `middle` every 2 or so shores up a tunnel; at its own size the opening is 1.7 wide and 1.9 high."""
    w, h = 72, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (4, 61):                                               # the posts
        cv.box(x, 6, 7, 58, z=1.0, top=0.6, bevel=1.6, mat=0, rough=0.3, rng=np.random.default_rng(x))
    cv.box(1, 1, 70, 8, z=1.2, top=0.6, bevel=1.8, mat=0, rough=0.3, rng=np.random.default_rng(3))   # the cap
    for x in (4, 61):
        cv.stroke([(x + 3.5, 8.5), (x + 3.5 + (8 if x < 30 else -8), 1.5)], 2.4, z=1.15, dome=0.6, mat=0)  # braces
    cv.stroke([(36, 9), (36, 14)], 0.7, z=1.3, dome=0.4, mat=1)       # the lamp's wire
    cv.box(33, 14, 6, 6, z=1.5, top=0.5, bevel=1.0, mat=1)            # its cage
    cv.box(34.5, 15.5, 3, 3, z=1.6, top=0.3, bevel=0.4, mat=2)        # the flame
    rgba, _ = _prop(cv, [TIMBER, IRON, ramp('#ffc060', dark=0.8, light=1.1)], relief=1.1, cavity=0.5, shadow=0.45)
    return rgba, _tail_em(cv, [2])


def spr_mine_cart():
    """The mine cart ahead of you, riding the rails: a riveted iron tub heaped with ore, gold glinting in it, on
    small wheels."""
    w, h = 44, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    rng = np.random.default_rng(13)
    for _ in range(22):                                             # the ore, heaped over its rim
        cv.ellipse(rng.uniform(8, 36), rng.uniform(4, 12), rng.uniform(2.0, 4.4), rng.uniform(1.6, 3.2),
                   z=1.0 + rng.uniform(0, 0.5), dome=0.8, mat=2 if rng.random() < 0.2 else 1)
    cv.polygon([(3, 9), (41, 9), (38, 27), (6, 27)], z=1.2, top=0.7, bevel=1.8, mat=0)        # the tub
    for x in range(7, 40, 6):                                       # its rivets
        cv.ellipse(x, 11, 0.8, 0.8, z=1.5, dome=0.6, mat=0)
    cv.box(3, 9, 38, 2.2, z=1.4, top=0.5, bevel=0.6, mat=0, tone=0.1)            # its rim
    for x in (7, 31):
        cv.ellipse(x + 3, 29.5, 4.2, 4.2, z=0.9, dome=0.7, mat=3)                # wheels on the rails
    return _prop(cv, [IRON, ramp('#5a524a', dark=0.4, light=1.6), ramp('#e8c040', dark=0.5, light=1.4, warm=0.1),
                      TYRE], relief=1.1, cavity=0.5, shadow=0.45)


# ------------------------------------------------------------------ in space

HULL = ramp('#8a9098', dark=0.35, light=1.6, cool=0.1)
HULL_D = ramp('#4a4e58', dark=0.4, light=1.9, cool=0.1)
JET = ramp('#ffa040', dark=0.8, light=1.15, warm=0.1)


def spr_starfighter():
    """A small starfighter seen from behind, as you fly it: a grey hull swept back into two wings angled down, a
    canopy over the pilot, red lights at the wingtips and twin engines glowing at its tail."""
    w, h = 64, 32
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(30, 12), (34, 12), (62, 22), (60, 25), (34, 19), (30, 19), (4, 25), (2, 22)], z=1.0, top=0.7,
               bevel=1.6, mat=0)                                                # the wings, angled down
    cv.box(58, 21, 5, 3, z=1.3, top=0.4, bevel=0.6, mat=3)                       # the wingtips' lights
    cv.box(1, 21, 5, 3, z=1.3, top=0.4, bevel=0.6, mat=3)
    cv.ellipse(32, 15, 9, 8, z=1.4, dome=0.8, mat=0)                             # the hull
    cv.ellipse(32, 9.5, 4.5, 4, z=1.8, dome=0.8, mat=4)                          # the canopy
    cv.polygon([(29, 2), (35, 2), (34, 9), (30, 9)], z=1.2, top=0.6, bevel=0.8, mat=1)   # the fin
    for x in (26, 38):                                              # the engines
        cv.ellipse(x, 19, 4.4, 4.0, z=1.6, dome=0.6, mat=1)
        cv.ellipse(x, 19.5, 2.8, 2.4, z=1.8, dome=0.4, mat=2)
    rgba, _ = _prop(cv, [HULL, HULL_D, JET, ramp('#ff3020', dark=0.8, light=1.2), GLASS], relief=1.0, cavity=0.4,
                    shadow=0.4)
    return rgba, _tail_em(cv, [2, 3])


# ------------------------------------------------------------------ the race track

LIVERY = [ramp('#c81e1e', dark=0.35, light=1.5), ramp('#1e5ac8', dark=0.35, light=1.6, cool=0.06),
          ramp('#f0f0ea', dark=0.45, light=1.2), ramp('#f0a020', dark=0.4, light=1.35, warm=0.05)]


def spr_race_car():
    return _race_car(0)


def _race_car(k):
    """An open-wheel race car seen from behind, on the grid: a wide rear wing on its pylon, the fat rear tyres
    either side of the gearbox, the rain light under the wing, the driver's helmet over the cockpit - in red (blue,
    white or orange: `variant` 1 to 3)."""
    w, h = 60, 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (1, 45):                                               # the rear tyres, fat
        cv.box(x, 11, 14, 18, z=0.8, top=0.6, bevel=2.6, mat=3)
        cv.stroke([(x + 2, 13), (x + 2, 27)], 0.6, dome=0.3, mode='carve')
    cv.box(18, 13, 24, 13, z=1.1, top=0.6, bevel=2.2, mat=0)                     # the body, the gearbox
    cv.box(28.5, 4, 3, 10, z=1.4, top=0.5, bevel=0.6, mat=1)                     # the wing's pylon
    cv.ellipse(30, 10.5, 4.4, 4.6, z=1.7, dome=0.9, mat=4)                       # the helmet, before it
    cv.box(26.5, 10, 7, 1.6, z=1.9, top=0.3, bevel=0.4, mat=5)                   # its visor
    cv.box(13, 2, 34, 4.5, z=1.6, top=0.6, bevel=1.0, mat=0)                     # the rear wing
    cv.box(12, 1, 3, 9, z=1.7, top=0.5, bevel=0.6, mat=1)                        # its end plates
    cv.box(45, 1, 3, 9, z=1.7, top=0.5, bevel=0.6, mat=1)
    cv.box(28, 21, 4, 3, z=1.5, top=0.3, bevel=0.5, mat=2)                       # the rain light
    cv.box(19, 25, 22, 3, z=1.0, top=0.4, bevel=0.6, mat=1)                      # the diffuser
    return _prop(cv, [LIVERY[k], TRIM, TAIL, TYRE, WHITE, GLASS], em=_tail_em(cv, [2]), relief=1.0,
                 cavity=0.45, shadow=0.45)


def tex_grandstand(name):
    """A grandstand full of people, for a wall along a race track: tiers of concrete steps rising, a crowd on every
    one - heads and shirts of every colour - a flag waved here and there. One tile is the whole stand: give the
    wall `"tile": [2, h]` for a stand h high."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.zeros((T, T, 3), np.float32) + [0.5, 0.5, 0.52]
    step = (yy % 8) < 2
    rgb[step] = [0.62, 0.62, 0.64]
    shirts = np.array([[0.85, 0.2, 0.2], [0.2, 0.4, 0.85], [0.95, 0.85, 0.3], [0.9, 0.9, 0.9], [0.2, 0.6, 0.3],
                       [0.95, 0.5, 0.15], [0.15, 0.15, 0.18]], np.float32)
    heads = np.array([[0.85, 0.65, 0.5], [0.6, 0.42, 0.3], [0.35, 0.24, 0.16], [0.9, 0.8, 0.6]], np.float32)
    for row in range(8):
        y0 = row * 8 + 2
        x = rng.uniform(0, 2)
        while x < T:
            if rng.random() < 0.9:
                xi = int(x)
                rgb[y0 + 2:y0 + 6, xi:xi + 2] = shirts[int(rng.integers(len(shirts)))]
                rgb[y0:y0 + 2, xi:xi + 2] = heads[int(rng.integers(len(heads)))]
            x += rng.uniform(2.4, 3.4)
    for _ in range(3):                                              # flags waved
        fx, fy = int(rng.integers(2, 58)), int(rng.integers(0, 48))
        rgb[fy:fy + 4, fx:fx + 6] = shirts[int(rng.integers(len(shirts)))]
        rgb[fy:fy + 8, fx:fx + 1] = [0.3, 0.3, 0.3]
    return np.clip(rgb, 0, 1), None


DEBRIS_SETS = {                       # for a road scene's `scatter`: what lies along a verge
    'verge': ['grass_tuft', 'grass_tuft', 'grass_tuft', 'dry_tuft', 'flowers', 'rocks', 'bush'],
    'alpine': ['rocks', 'rocks', 'rocks', 'boulder', 'grass_tuft', 'grass_tuft', 'flowers'],
    'street': ['trash_bag', 'trash_bag', 'trash', 'trash', 'old_tyre', 'traffic_cone'],
}
DECALS = {'oil_stain': dec_oil_stain, 'tyre_marks': dec_tyre_marks, 'road_patch': dec_road_patch,
          'pothole': dec_pothole, 'leaf_litter': dec_leaf_litter, 'manhole': dec_manhole,
          'lane_arrow': dec_lane_arrow, 'zebra_crossing': dec_zebra_crossing, 'sand_drift': dec_sand_drift,
          'pebbles': dec_pebbles, 'start_line': dec_start_line, 'wake': dec_wake}
TEXTURES.update({'tower_windows': lambda n: tex_tower_windows(n), 'tower_windows_b': lambda n: tex_tower_windows(n),
                 'shopfront': lambda n: tex_shopfront(n),
                 'shopfront_b': lambda n: tex_shopfront(n, (0.25, 0.95, 1.0)),
                 'shopfront_c': lambda n: tex_shopfront(n, (1.0, 0.7, 0.2)),
                 'coaster_track': lambda n: tex_coaster_track(n), 'coaster_frame': lambda n: tex_coaster_frame(n),
                 'rail_track': lambda n: tex_rail_track(n), 'grandstand': lambda n: tex_grandstand(n)})
TEXTURE_NOISE.update({'tower_windows': 0.4, 'tower_windows_b': 0.4, 'shopfront': 0.4, 'shopfront_b': 0.4,
                      'shopfront_c': 0.4, 'coaster_track': 0.2, 'coaster_frame': 0.2, 'rail_track': 0.6,
                      'grandstand': 0.3})
VARIANTS = {'traffic_light': (3, _traffic_light), 'car_compact': (4, _car_compact), 'car_sedan': (4, _car_sedan),
            'billboard': (3, _billboard), 'race_car': (4, _race_car)}

SPRITES = {'sports_car': spr_sports_car, 'car_compact': spr_car_compact, 'car_sedan': spr_car_sedan,
           'box_truck': spr_box_truck, 'curve_sign': spr_curve_sign, 'billboard': spr_billboard,
           'checkpoint': spr_checkpoint, 'traffic_cone': spr_traffic_cone, 'tunnel_ring': spr_tunnel_ring,
           'tunnel_portal': spr_tunnel_portal, 'trash_bag': spr_trash_bag, 'old_tyre': spr_old_tyre,
           'trash': spr_trash, 'reflector_post': spr_reflector_post, 'highway_lamp': spr_highway_lamp,
           'sign_gantry': spr_sign_gantry, 'speed_sign': spr_speed_sign, 'traffic_light': spr_traffic_light,
           'tyre_stack': spr_tyre_stack, 'road_barrier': spr_road_barrier, 'start_lights': spr_start_lights,
           'jeep': spr_jeep, 'rally_car': spr_rally_car, 'dirt_bike': spr_dirt_bike, 'dust_cloud': spr_dust_cloud,
           'speedboat': spr_speedboat, 'narrowboat': spr_narrowboat, 'boat_bow': spr_boat_bow,
           'hover_car': spr_hover_car, 'neon_bike': spr_neon_bike, 'taxi': spr_taxi, 'brick_ring': spr_brick_ring,
           'coaster_car': spr_coaster_car, 'mine_frame': spr_mine_frame, 'mine_cart': spr_mine_cart,
           'starfighter': spr_starfighter, 'race_car': spr_race_car}
SPRITE_HEIGHT = {'sports_car': 0.42, 'car_compact': 0.44, 'car_sedan': 0.48, 'box_truck': 1.05, 'curve_sign': 0.95,
                 'billboard': 2.6, 'checkpoint': 2.6, 'traffic_cone': 0.24, 'tunnel_ring': 3.6,
                 'tunnel_portal': 5.775, 'trash_bag': 0.16, 'old_tyre': 0.22, 'trash': 0.05,
                 'reflector_post': 0.34, 'highway_lamp': 3.6, 'sign_gantry': 3.2, 'speed_sign': 0.95,
                 'traffic_light': 1.5, 'tyre_stack': 0.32, 'road_barrier': 0.36, 'start_lights': 3.0,
                 'jeep': 0.62, 'rally_car': 0.48, 'dirt_bike': 0.55, 'dust_cloud': 0.62, 'speedboat': 0.44,
                 'narrowboat': 0.9, 'boat_bow': 0.42, 'hover_car': 0.36, 'neon_bike': 0.52, 'taxi': 0.5, 'brick_ring': 3.25, 'coaster_car': 0.55,
                 'mine_frame': 2.2, 'mine_cart': 0.38, 'starfighter': 0.4, 'race_car': 0.3}
PROP_DEFAULTS = {'checkpoint': {'shadow': False}, 'billboard': {'shadow': False}, 'tunnel_ring': {'shadow': False},
                 'tunnel_portal': {'shadow': False}, 'sign_gantry': {'shadow': False},
                 'start_lights': {'shadow': False}, 'dust_cloud': {'shadow': False, 'opacity': 0.75},
                 'speedboat': {'shadow': False}, 'narrowboat': {'shadow': False}, 'boat_bow': {'shadow': False},
                 'brick_ring': {'shadow': False}, 'mine_frame': {'shadow': False}, 'starfighter': {'shadow': False}}

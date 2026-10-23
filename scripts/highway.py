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


def spr_car_oncoming():
    return _car_oncoming(0)


def _car_oncoming(k):
    """A car coming the other way, seen from the front: the windscreen with the driver dim behind it, the bonnet,
    a grille between two headlights, lit - white, glowing - the bumper, a plate. In the sedan's paints (`variant`
    0 to 3); at night its lights carry a `light` of their own if you give it one."""
    w, h = 52, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (3, 40):
        cv.box(x, 31, 9, 12, z=0.6, top=0.5, bevel=2.0, mat=3)                    # the front tyres
    cv.polygon([(10, 4), (42, 4), (46, 16), (6, 16)], z=1.0, top=0.8, bevel=1.4, mat=0)       # the roof's edge
    cv.polygon([(11, 6), (41, 6), (44, 16), (8, 16)], z=1.3, top=0.3, bevel=0.8, mat=4)       # the windscreen
    cv.ellipse(18, 12, 3.2, 3.4, z=1.15, dome=0.8, mat=6)                        # the driver, dim behind it
    cv.box(3, 16, 46, 6, z=1.4, top=0.9, bevel=1.6, mat=0, tone=0.06)            # the bonnet
    cv.box(3, 21, 46, 12, z=1.3, top=0.5, bevel=2.2, mat=0)                      # its front
    cv.box(18, 24, 16, 5, z=1.5, top=0.3, bevel=0.6, mat=5)                      # the grille
    for x in (5, 36):
        cv.box(x, 23, 11, 5, z=1.7, top=0.3, bevel=0.8, mat=1)                   # the headlights, lit
    cv.box(3, 31, 46, 3.6, z=1.6, top=0.4, bevel=1.0, mat=5)                     # the bumper
    cv.box(20, 30, 12, 3.2, z=1.7, top=0.1, bevel=0.4, mat=2)                    # the plate
    return _prop(cv, [SEDAN_PAINT[k], ramp('#fffbe8', dark=0.85, light=1.05), PLATE, TYRE, GLASS, TRIM,
                      ramp('#2a2a30', dark=0.5, light=1.8)], em=_tail_em(cv, [1]), relief=1.0, cavity=0.45,
                 shadow=0.45)


def spr_box_truck():
    """A delivery truck seen from behind: a tall box with a roll-up door - a red band across it and a round badge on
    it - a marker light at each top corner, small tail lights low down, dual wheels, a step bumper of black steel."""
    w, h = 48, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (2, 37):
        cv.box(x, 52, 9, 11, z=0.6, top=0.5, bevel=1.8, mat=3)
    cv.box(2, 2, 44, 50, z=1.0, top=0.4, bevel=1.4, mat=0)                       # the box
    cv.box(2, 30, 44, 5, z=1.05, top=0.4, bevel=0.6, mat=5)                      # a band of red across it
    for y in range(8, 48, 6):                                      # the door's slats
        cv.stroke([(6, y), (42, y)], 0.7, dome=0.3, mode='carve')
    cv.ellipse(24, 18, 6, 6, z=1.1, dome=0.3, mat=5)                             # a round badge
    cv.ellipse(24, 18, 3.6, 3.6, z=1.15, dome=0.3, mat=0)
    cv.stroke([(4, 4), (4, 49)], 1.2, z=1.2, dome=0.5, mat=4)                    # the door's runners
    cv.stroke([(44, 4), (44, 49)], 1.2, z=1.2, dome=0.5, mat=4)
    for x in (3, 42):                                              # marker lights at its top corners
        cv.box(x, 2, 3, 2, z=1.3, top=0.2, bevel=0.3, mat=6)
    cv.box(21, 44, 6, 3, z=1.3, top=0.2, bevel=0.4, mat=4)                       # its handle
    cv.box(3, 49, 42, 4, z=1.4, top=0.3, bevel=0.8, mat=4)                       # the sill
    cv.box(4, 53, 6, 3, z=1.6, top=0.1, bevel=0.4, mat=1)
    cv.box(38, 53, 6, 3, z=1.6, top=0.1, bevel=0.4, mat=1)
    cv.box(18, 53, 12, 3.6, z=1.6, top=0.1, bevel=0.4, mat=2)
    cv.box(1, 57, 46, 3, z=1.5, top=0.3, bevel=0.8, mat=4)
    cv.box(14, 60, 20, 2.4, z=1.4, top=0.3, bevel=0.5, mat=4)                    # the step
    return _prop(cv, [BOX, TAIL, PLATE, TYRE, TRIM, ramp('#b02a24', dark=0.35, light=1.5), AMBER],
                 em=_tail_em(cv, [1, 6]), relief=1.0, cavity=0.45, shadow=0.45)


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
    ridge = 112 + 36 * np.cos((xx - w / 2) / w * np.pi) - 8 * np.abs(np.sin(xx * 0.07)) - 30 * (
        np.abs(xx - w / 2) / (w / 2)) ** 3
    hill = up < ridge                                                                             # the hillside
    face = (np.abs(xx - w / 2) < 92) & (up < 100)
    grass = rng.random((h, w)) * 0.12
    n = _noise(h, w, 9, 6)
    rgba[hill, :3] = (np.array([0.24, 0.34, 0.16]) * (0.75 + 0.5 * n[hill])[:, None] +
                      grass[hill][:, None] * np.array([1, 1.2, 0.6]))                              # patchy grass
    rgba[hill & (up > ridge - 3), :3] *= 1.25                                                     # its lit crest
    for _ in range(26):                                             # bushes and trees along the ridge and its slopes
        cx = rng.uniform(4, w - 4)
        cy = h - (112 + 36 * np.cos((cx - w / 2) / w * np.pi) - 30 * (abs(cx - w / 2) / (w / 2)) ** 3) + \
            rng.uniform(-2, 30)
        r = rng.uniform(4, 9)
        bush = (np.hypot(xx - cx, (yy - cy) * 1.2) < r)
        rgba[bush, :3] = np.array([0.16, 0.26, 0.12]) * (0.8 + 0.4 * n[bush])[:, None]
        rgba[bush & (yy < cy - r * 0.3), :3] *= 1.3
        hill = hill | bush
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


# ------------------------------------------------------------------ the roadside at night

def spr_motel_sign():
    """A motel's sign by the highway: MOTEL in pink neon on an arrow-shaped board pointing in, a star at its tip,
    VACANCY lit in green on a panel under it, the whole on a tall pole. Its tubes glow."""
    import lettering
    w, h = 64, 112
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    pole = (np.abs(xx - 40) < 2.2) & (yy > 40)
    rgba[pole, :3] = [0.5, 0.52, 0.55]
    rgba[pole & (xx > 40), :3] = [0.36, 0.37, 0.4]
    board = (yy >= 8) & (yy < 30) & (xx >= 10 - (yy - 8) * 0.0) & (xx < 58)
    tip = (xx >= 2) & (xx < 12) & (np.abs(yy - 19) < (xx - 2) * 1.1)                  # the arrow's point
    arrow = board | tip
    rgba[arrow, :3] = [0.14, 0.08, 0.16]
    edge = arrow & ~(((yy >= 10) & (yy < 28) & (xx >= 12) & (xx < 56)) |
                     ((xx >= 4.5) & (xx < 12) & (np.abs(yy - 19) < (xx - 4.5) * 1.1 - 1)))
    rgba[edge, :3] = [1.0, 0.4, 0.75]
    em[edge] = 1.0
    word = lettering.mask('MOTEL', 1, False)
    mh, mw = word.shape
    y0, x0 = 19 - mh // 2, 35 - mw // 2
    rgba[y0:y0 + mh, x0:x0 + mw][word, :3] = [1.0, 0.55, 0.85]
    em[y0:y0 + mh, x0:x0 + mw][word] = 1.0
    star = (np.abs(xx - 52) + np.abs(yy - 4) * 1.4 < 4) & (yy < 8)
    rgba[star, :3] = [1.0, 0.9, 0.4]
    em[star] = 1.0
    panel = (yy >= 32) & (yy < 42) & (xx >= 20) & (xx < 60)
    rgba[panel, :3] = [0.1, 0.1, 0.12]
    vac = lettering.mask('VACANCY', 1, False)
    vh, vw = vac.shape
    vy, vx = 37 - vh // 2, 40 - vw // 2
    rgba[vy:vy + vh, vx:vx + vw][vac, :3] = [0.4, 1.0, 0.5]
    em[vy:vy + vh, vx:vx + vw][vac] = 1.0
    rgba[..., 3] = (arrow | star | panel | pole).astype(np.float32)
    return rgba, em


def spr_gas_station():
    """A gas station by the road, seen across its forecourt: a flat canopy on two pillars, lit white underneath, two
    pumps under it, a little shop behind with its window lit, the price board on a pole."""
    w, h = 120, 60
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    shop = (xx >= 64) & (xx < 112) & (yy >= 26) & (yy < 60)
    rgba[shop, :3] = [0.62, 0.6, 0.56]
    win = (xx >= 70) & (xx < 104) & (yy >= 36) & (yy < 52)
    rgba[win, :3] = [1.0, 0.92, 0.7]
    em[win] = 0.8
    roof = (xx >= 62) & (xx < 114) & (yy >= 24) & (yy < 27)
    rgba[roof, :3] = [0.3, 0.3, 0.32]
    canopy = (xx >= 4) & (xx < 76) & (yy >= 14) & (yy < 21)
    rgba[canopy, :3] = [0.92, 0.92, 0.9]
    band = canopy & (yy >= 16) & (yy < 19)
    rgba[band, :3] = [0.85, 0.15, 0.12]
    under = (xx >= 6) & (xx < 74) & (yy >= 21) & (yy < 23)
    rgba[under, :3] = [1.0, 1.0, 0.95]
    em[under] = 1.0
    for x0 in (14, 62):                                            # the pillars
        p = (xx >= x0) & (xx < x0 + 4) & (yy >= 21)
        rgba[p, :3] = [0.82, 0.82, 0.8]
    for x0 in (26, 44):                                            # the pumps
        pump = (xx >= x0) & (xx < x0 + 7) & (yy >= 42) & (yy < 60)
        rgba[pump, :3] = [0.8, 0.2, 0.16]
        face = (xx >= x0 + 1.5) & (xx < x0 + 5.5) & (yy >= 45) & (yy < 50)
        rgba[face, :3] = [0.9, 0.95, 1.0]
        em[face] = 0.6
    post = (xx >= 113) & (xx < 116) & (yy >= 6)
    rgba[post, :3] = [0.45, 0.45, 0.48]
    sign = (xx >= 104) & (xx < 120) & (yy >= 2) & (yy < 14)
    rgba[sign, :3] = [0.1, 0.1, 0.12]
    digits = sign & ((((xx - 106) % 4) < 2.5) & (((yy - 4) % 4) < 2.5)) & (xx >= 106) & (xx < 118) & (yy >= 4) & (yy < 12)
    rgba[digits, :3] = [1.0, 0.6, 0.2]
    em[digits] = 1.0
    rgba[..., 3] = (shop | roof | canopy | under | post | sign |
                    np.any([(xx >= x0) & (xx < x0 + 4) & (yy >= 21) for x0 in (14, 62)], axis=0) |
                    np.any([(xx >= x0) & (xx < x0 + 7) & (yy >= 42) for x0 in (26, 44)], axis=0)).astype(np.float32)
    return rgba, em


# ------------------------------------------------------------------ a suspension bridge

BRIDGE_RED = ramp('#b8462c', dark=0.35, light=1.45, warm=0.06)


def spr_bridge_tower():
    """A suspension bridge's tower spanning the road: two tall legs in red paint, stepping in as they rise, joined by
    portal beams, a recess down each face. Stand it at `x` 0 over the road; at its own size it is 10 tall and its
    legs stand 7 apart - a row of them every span, with `suspension_cables` walls between."""
    w, h = 96, 120
    cv = Canvas(w, h, wrap=False, ground=-9)
    for side in (-1, 1):
        x0 = 48 + side * 38
        for k, (y0, y1, half) in enumerate(((60, 120, 7.0), (24, 60, 6.0), (0, 24, 5.0))):   # stepping in
            cv.box(x0 - half, y0, 2 * half, y1 - y0, z=1.0 + 0.05 * k, top=0.6, bevel=1.4, mat=0)
            cv.stroke([(x0, y0 + 2), (x0, y1 - 2)], 1.2, dome=0.3, mode='carve')         # the recess
    for y0, hh in ((6, 6), (40, 6), (80, 5)):                       # the portal beams
        cv.box(14, y0, 68, hh, z=0.9, top=0.6, bevel=1.4, mat=0)
        cv.stroke([(18, y0 + hh - 1.2), (78, y0 + hh - 1.2)], 0.6, dome=0.3, mode='carve')
    cv.box(8, 0, 10, 3, z=1.2, top=0.5, bevel=0.8, mat=1)          # the cable saddles on top
    cv.box(78, 0, 10, 3, z=1.2, top=0.5, bevel=0.8, mat=1)
    cv.box(10.5, 1, 2, 1.4, z=1.3, top=0.3, bevel=0.3, mat=2)       # an aircraft light on each
    cv.box(83.5, 1, 2, 1.4, z=1.3, top=0.3, bevel=0.3, mat=2)
    rgba, _ = _prop(cv, [BRIDGE_RED, TRIM, ramp('#ff3020', dark=0.8, light=1.2)], relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [2])


def tex_suspension_cables(name):
    """A suspension bridge's cables, for a wall along its deck: the main cable sagging over the width of the tile
    from its top at both ends, the suspenders hanging from it to the deck every few texels, see-through between.
    Give the wall the towers' spacing and height: `"tile": [span, height]`, the towers every span from 0."""
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    u = (xx + 0.5) / T
    main = 1.5 + 54 * (1 - (2 * u - 1) ** 2)                       # the cable's row, sagging to near the deck
    cable = np.abs(yy - main) < 1.3
    hangers = ((xx.astype(int) % 4) == 0) & (yy > main)
    rgb = np.zeros((T, T, 3), np.float32) + [0.7, 0.28, 0.17]
    rgb[hangers] = [0.5, 0.22, 0.16]
    return rgb, None, (cable | hangers).astype(np.float32)


# ------------------------------------------------------------------ the dark road

def spr_dark_castle():
    """A dark castle on a crag, far off at a road's end: black towers and spires against the sky, a curtain wall
    between them, a few windows lit red, the crag dropping away under it. A great billboard for the horizon: stand
    it at the road's end at a `scale` of 40 or so."""
    w, h = 160, 120
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    rng = np.random.default_rng(66)
    n = _noise(h, w, 7, 67)
    crag = yy > 74 + 22 * np.abs((xx - 80) / 80) ** 1.6 + (n - 0.5) * 10        # the crag under it
    keep = np.zeros((h, w), bool)
    towers = [(80, 10, 9), (52, 28, 7), (108, 24, 7), (30, 44, 6), (130, 42, 6), (66, 34, 5), (94, 30, 5)]
    for cx, top, half in towers:                                    # each tower and its spire
        body = (np.abs(xx - cx) < half) & (yy > top + half * 2.2) & (yy < 82)
        spire = (yy >= top) & (yy <= top + half * 2.2) & (np.abs(xx - cx) < (yy - top) / 2.2)
        keep |= body | spire
        for k in range(int(rng.integers(1, 4))):                    # a lit window or two
            wy = int(top + half * 2.2 + 6 + k * 9)
            if wy < 78:
                win = (np.abs(xx - cx) < 1.2) & (yy >= wy) & (yy < wy + 3)
                rgba[win, :3] = [1.0, 0.3, 0.12]
                em[win] = 1.0
                keep |= win
    wall = (xx > 26) & (xx < 134) & (yy > 60) & (yy < 84)          # the curtain wall
    crenel = wall & (yy < 63) & ((xx.astype(int) // 3) % 2 == 0)
    keep |= wall & ~crenel
    shade = np.array([0.08, 0.06, 0.09], np.float32)
    rgba[keep & (em == 0), :3] = shade * (0.8 + 0.4 * n[keep & (em == 0)])[:, None]
    rgba[crag, :3] = np.array([0.12, 0.08, 0.08]) * (0.7 + 0.6 * n[crag])[:, None]
    rgba[..., 3] = (keep | crag).astype(np.float32)
    return rgba, em


# ------------------------------------------------------------------ the canal at night

LACQUER = ramp('#1a1a22', dark=0.5, light=3.0, cool=0.1)
NAVY = ramp('#24325e', dark=0.45, light=1.6, cool=0.06)
STRAW = ramp('#e2c272', dark=0.45, light=1.3, warm=0.06)
STONE_W = ramp('#dedad0', dark=0.45, light=1.25)
CANAL_BRICK = ramp('#9a5a3e', dark=0.4, light=1.4, warm=0.06)
POLE_C = [ramp('#c42a2a', dark=0.4, light=1.4), ramp('#2a4ac4', dark=0.4, light=1.5, cool=0.08),
          ramp('#2a8a4a', dark=0.4, light=1.5)]


def tex_canal_house(name, plaster=(0.78, 0.58, 0.38)):
    """An old house's face over a canal at night, for a wall of houses along the water: plaster (`plaster`)
    worn through to the brick in patches, a pale string course at each floor, four windows across and two floors
    up to a tile, each with a stone sill and green shutters - a few lit warm behind their curtains, most dark,
    some shuttered. Its lit windows glow."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    p = np.array(plaster, np.float32)
    rgb = p * (0.8 + 0.32 * fbm(T, rng, 6, 3))[..., None]
    worn = fbm(T, rng, 5, 2) > 0.64                                     # the plaster worn through to brick
    course = ((yy // 3) % 2) * 3
    bk = np.array([0.5, 0.27, 0.2], np.float32) * (0.8 + 0.3 * (((xx + course) // 6) % 2))[..., None]
    bk[(yy % 3) == 2] *= 0.6
    rgb[worn] = bk[worn]
    rgb[(yy % 32) >= 30] = p * 1.12                                     # the string course at each floor
    rgb[(yy % 32) == 29] *= 0.55                                        # its shadow
    em = np.zeros((T, T), np.float32)
    shutter = np.array([0.18, 0.34, 0.24], np.float32)
    for gy in range(2):
        for gx in range(4):
            y0, x0 = gy * 32 + 9, gx * 16 + 5
            win = (yy >= y0) & (yy < y0 + 15) & (xx >= x0) & (xx < x0 + 6)
            win &= ~((yy < y0 + 2) & ((xx == x0) | (xx == x0 + 5)))          # its round top
            sill = (yy >= y0 + 15) & (yy < y0 + 17) & (xx >= x0 - 1) & (xx < x0 + 7)
            rgb[sill] = [0.88, 0.86, 0.8]
            rgb[(yy == y0 + 17) & (xx >= x0 - 1) & (xx < x0 + 7)] *= 0.5
            roll = rng.random()
            if roll < 0.32:                                                     # lit, a curtain half drawn
                c = np.array([1.0, 0.74, 0.4], np.float32) * rng.uniform(0.75, 1.0)
                rgb[win] = c
                em[win] = 0.9
                cur = win & (xx >= x0 + (4 if rng.random() < 0.5 else 0)) & (xx < x0 + (6 if rng.random() < 0.5 else 2))
                rgb[cur] = c * [0.85, 0.5, 0.35]
                em[cur] = 0.5
                rgb[win & (xx == x0 + 3)] *= 0.55                                 # the mullion
                em[win & (xx == x0 + 3)] *= 0.5
            else:
                rgb[win] = [0.05, 0.06, 0.09]
                rgb[win & (yy < y0 + 5) & (xx < x0 + 2)] = [0.2, 0.22, 0.3]     # the sky caught in the glass
            if roll > 0.82:                                                     # shuttered
                rgb[win] = shutter * (0.8 + 0.4 * ((yy[win] - y0) % 2))[:, None]
                em[win] = 0.0
            else:                                                               # the shutters open, either side
                for sx in (x0 - 3, x0 + 6):
                    sh = (yy >= y0) & (yy < y0 + 15) & (xx >= sx) & (xx < sx + 3)
                    rgb[sh] = shutter * (0.75 + 0.35 * ((yy[sh] - y0) % 2))[:, None]
    return np.clip(rgb, 0, 1), em


def tex_canal_footing(name):
    """The foot of a house where it stands in a canal: courses of pale stone, the waterline's band of green-black
    weed at the bottom and wet streaks running up from it."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.array([0.74, 0.72, 0.66], np.float32) * (0.78 + 0.3 * fbm(T, rng, 6, 3))[..., None]
    rgb[(yy % 16) == 15] *= 0.5                                          # the courses
    rgb[((xx + (yy // 16) * 11) % 24 == 0)] *= 0.55                      # the joints
    weed = yy > 40 + 6 * vnoise(T, 8, rng)
    rgb[weed] = np.array([0.1, 0.16, 0.1], np.float32) * (0.7 + 0.6 * fbm(T, rng, 8, 2)[weed])[:, None]
    streak = (yy > 20) & (vnoise(T, 16, rng) > 0.62) & ~weed
    rgb[streak] *= 0.62
    return np.clip(rgb, 0, 1), None


def _mooring_pole(k):
    w, h = 8, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(2.4, 6, 3.2, 58, z=1.0, top=0.5, bevel=1.4, mat=0)                       # the pole
    for y in range(8, 56, 7):                                                      # its spiral stripes
        cv.stroke([(2.2, y + 3.5), (5.8, y)], 2.2, z=1.25, dome=0.4, mat=1)
    cv.ellipse(4, 5, 2.6, 2.2, z=1.4, dome=0.8, mat=2)                              # the gilt knob
    cv.box(2.0, 56, 4.0, 8, z=1.1, top=0.5, bevel=1.0, mat=3)                       # wet and weedy at the water
    return _prop(cv, [STONE_W, POLE_C[k], BRASS, ramp('#2a3a26', dark=0.5, light=1.6)], relief=1.0, cavity=0.4,
                 shadow=0.4)


def spr_mooring_pole():
    """A mooring pole standing in a canal, striped round like a barber's pole with a gilt knob on top, weed where it
    meets the water (three ways: `variant` 0 red, 1 blue, 2 green). Stand them in twos and threes off the houses."""
    return _mooring_pole(0)


def spr_canal_bridge():
    """A bridge humped over a canal, seen from the water: one arch of brick ringed in pale stone, its parapet
    capped in the same stone and rising to the middle, the arch's opening open (you go under it). Stand it across
    the canal with `"x": 0`, wide enough to reach both banks."""
    w, h = 112, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    xs = np.arange(w) + 0.5
    top = 12 - 8 * np.sin(np.clip(xs / w, 0, 1) * np.pi)                           # the deck humps to the middle
    pts = [(0, 40)] + [(x, top[i]) for i, x in enumerate(xs[::4])] + [(w, top[-1]), (w, 40)]
    cv.polygon(pts, z=1.0, top=0.4, bevel=0.6, mat=0)                               # the brick body
    for y in range(4, 40, 3):                                                      # its courses
        cv.stroke([(0, y), (w, y)], 0.5, mode='carve', z=0.2)
    cv.stroke([(x, top[i * 4] + 1.2) for i, x in enumerate(xs[::4])], 2.6, z=1.4, dome=0.5, mat=1)   # the coping
    cx, span, rise = 56, 34, 25                                                     # the arch
    t = np.linspace(0, np.pi, 40)
    ring = [(cx - np.cos(a) * (span + 2.5), 40 - np.sin(a) * (rise + 2.5)) for a in t]
    cv.stroke(ring, 4.0, z=1.3, dome=0.4, mat=1)                                    # its ring of stone
    for a in t[2:-2:3]:                                                            # the voussoirs' joints
        r0, r1 = (span + 0.6, rise + 0.6), (span + 4.4, rise + 4.4)
        cv.stroke([(cx - np.cos(a) * r0[0], 40 - np.sin(a) * r0[1]), (cx - np.cos(a) * r1[0], 40 - np.sin(a) * r1[1])],
                  0.6, mode='carve', z=0.3)
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    hole = ((xx - cx) / span) ** 2 + ((yy - 40) / rise) ** 2 < 1.0
    cv.id[hole] = 0                                                                 # the opening, open
    rgba, em = _prop(cv, [CANAL_BRICK, STONE_W], relief=1.0, cavity=0.5, shadow=0.4)
    yi, xi = np.mgrid[0:h, 0:w]
    brick = (cv.mat == 0) & (cv.id > 0)
    shift = (yi // 3) % 2 * 3
    mortar = ((yi % 3) == 2) | (((xi + shift) % 6) == 0)
    each = np.sin(((yi // 3) * 37 + (xi + shift) // 6) * 12.9898) * 43758.5453 % 1.0      # each brick its own
    rgba[brick, :3] *= np.where(mortar, 0.62, 0.84 + 0.26 * each)[brick][:, None]
    return rgba, em


LAUNDRY = [ramp('#e8e6e0', dark=0.45, light=1.2), ramp('#6a9ad0', dark=0.4, light=1.4, cool=0.06),
           ramp('#c84a3a', dark=0.4, light=1.4), ramp('#e8c040', dark=0.4, light=1.3, warm=0.05),
           ramp('#5aa070', dark=0.4, light=1.4), ramp('#d890b0', dark=0.4, light=1.3)]


def spr_washing_line():
    """A line of washing slung across a canal or a lane between the houses: sheets, shirts, trousers, towels and
    socks pegged along a sagging line. A long card to hang across the way at `z` 2 or so (`side` middle)."""
    w, h = 192, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    rng = np.random.default_rng(71)

    def sag(x):
        return 2 + 40 * (x / w) * (1 - x / w)
    x, k = 8.0, 0
    paint = rng.permutation(len(LAUNDRY))
    while x < w - 16:
        kind = rng.choice(['sheet', 'shirt', 'trousers', 'towel', 'socks'], p=[0.22, 0.32, 0.2, 0.16, 0.1])
        m = 1 + int(paint[k % len(paint)])                                  # the colours taken in turn
        k += 1
        y = sag(x) + 0.5
        if kind == 'sheet':
            ww, hh = 20, 17 + rng.uniform(-2, 2)
            cv.polygon([(x, y), (x + ww, sag(x + ww) + 0.5), (x + ww - 1, y + hh + 1), (x + ww / 2, y + hh - 1),
                        (x + 1, y + hh + 1)], z=1.0, top=0.5, bevel=1.4, mat=m)
        elif kind == 'shirt':
            ww = 14
            cv.polygon([(x, y), (x + ww, y), (x + ww, y + 5), (x + ww - 3, y + 4), (x + ww - 3, y + 13),
                        (x + 3, y + 13), (x + 3, y + 4), (x, y + 5)], z=1.0, top=0.6, bevel=1.2, mat=m)
        elif kind == 'trousers':
            ww = 10
            cv.polygon([(x, y), (x + ww, y), (x + ww, y + 17), (x + 6, y + 17), (x + 5, y + 6), (x + 4, y + 17),
                        (x, y + 17)], z=1.0, top=0.6, bevel=1.0, mat=m)
        elif kind == 'towel':
            ww = 11
            cv.box(x, y, ww, 13, z=1.0, top=0.5, bevel=1.0, mat=m)
            cv.box(x, y + 10, ww, 1.2, z=1.05, top=0.2, bevel=0.2, mat=1 + (m % len(LAUNDRY)))
        else:
            ww = 9
            for sx in (x, x + 5):
                cv.polygon([(sx, y), (sx + 3, y), (sx + 3, y + 6), (sx + 4.5, y + 7.5), (sx + 1, y + 7.5)], z=1.0,
                           top=0.5, bevel=0.6, mat=m)
        x += ww + float(rng.uniform(2, 6))
    cv.stroke([(t, sag(t)) for t in np.linspace(0, w, 48)], 1.0, z=2.0, dome=0.3, mat=0)      # the line
    return _prop(cv, [ramp('#3a3530', dark=0.5, light=1.6)] + LAUNDRY, relief=1.0, cavity=0.4, shadow=0.4)


def spr_gondola():
    """A gondola seen from behind, going ahead of you down a canal: its black lacquered hull and the stern rising
    to a curl, the gondolier standing on the stern in a striped shirt and a straw hat, leaning on his long oar."""
    w, h = 40, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(6, 52), (34, 52), (30, 62), (10, 62)], z=1.0, top=0.6, bevel=2.0, mat=0)        # the hull
    cv.stroke([(20, 54), (20, 44), (21.5, 38), (19, 35)], 3.2, z=1.3, dome=0.6, taper=(1.0, 0.6), mat=0)  # the stern
    cv.box(9, 50, 22, 3, z=1.2, top=0.3, bevel=0.6, mat=6)                        # the gilt rail
    cv.box(15, 34, 4.2, 16, z=1.5, top=0.6, bevel=1.0, mat=3)                     # his legs, black
    cv.box(21, 34, 4.2, 16, z=1.5, top=0.6, bevel=1.0, mat=3)
    cv.box(14, 18, 12, 17, z=1.8, top=0.7, bevel=2.0, mat=1)                      # his shirt
    for y in (20.5, 24, 27.5, 31):                                                 # its navy stripes
        cv.box(14, y, 12, 1.6, z=1.85, top=0.3, bevel=0.2, mat=2)
    cv.ellipse(20, 14, 3.4, 3.6, z=2.0, dome=0.9, mat=4)                           # his head
    cv.ellipse(20, 11, 7.0, 1.5, z=2.2, dome=0.3, mat=5)                           # the hat's brim
    cv.box(16.2, 7, 7.6, 4.4, z=2.3, top=0.5, bevel=0.8, mat=5)                    # its crown
    cv.box(16.2, 9.6, 7.6, 1.4, z=2.35, top=0.2, bevel=0.2, mat=2)                 # the ribbon
    cv.stroke([(26, 20), (31, 25)], 2.6, z=1.9, dome=0.6, mat=1)                   # his arms, on the oar
    cv.stroke([(14, 22), (24, 27)], 2.6, z=2.0, dome=0.6, mat=1)
    cv.stroke([(22, 6), (38, 63)], 1.6, z=2.1, dome=0.5, mat=7)                    # the oar, down into the water
    return _prop(cv, [LACQUER, WHITE, NAVY, ramp('#1e1e24', dark=0.5, light=2.0), SKIN, STRAW, BRASS, WOOD],
                 relief=1.0, cavity=0.4, shadow=0.4)


# ------------------------------------------------------------------ the ski run

JACKET = ramp('#d83a2a', dark=0.4, light=1.4)
SKI_PANTS = ramp('#22283a', dark=0.45, light=1.9, cool=0.08)
SKI_HELMET = ramp('#e8e8ec', dark=0.45, light=1.2)
GATE_C = [ramp('#d82a22', dark=0.4, light=1.4), ramp('#2a52d8', dark=0.4, light=1.5, cool=0.08)]
NET = np.array([1.0, 0.45, 0.08], np.float32)
LIFT = ramp('#8a8e96', dark=0.4, light=1.6, cool=0.06)


def tex_piste(name):
    """Groomed snow on a ski run: the corduroy a groomer leaves, ridges running down the slope (along a road),
    blue-white in their troughs, the seam between two passes, a glint of ice here and there."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.array([0.9, 0.93, 0.98], np.float32) * (0.9 + 0.12 * fbm(T, rng, 4, 3))[..., None]
    rgb *= np.array([1.0, 0.98, 0.95, 0.9, 0.88, 0.92, 0.96, 0.99], np.float32)[xx % 8][..., None]   # the ridges
    rgb[(xx % 8) == 4] *= [0.9, 0.94, 1.0]                                          # blue in the troughs
    rgb[(xx == 0) | (xx == 63)] *= 0.86                                             # the seam
    glint = rng.random((T, T)) < 0.008
    rgb[glint] = [1.0, 1.0, 1.0]
    return np.clip(rgb, 0, 1), None


def tex_ski_fence(name):
    """The orange safety net along a ski run, for a wall at the piste's edge: a diamond mesh of orange cord
    stretched between posts, its top edge banded, see-through between the cords. One post to a tile."""
    yy, xx = np.mgrid[0:T, 0:T]
    mesh = (((xx + yy) % 8) == 0) | (((xx - yy) % 8) == 0)
    band = (yy < 4) | ((yy >= 56) & (yy < 58))
    post = xx < 2
    rgb = np.zeros((T, T, 3), np.float32) + NET * (0.85 + 0.15 * (yy < 32))[..., None]
    rgb[band] = NET * 1.05
    rgb[post] = [0.25, 0.3, 0.4]
    alpha = (mesh | band | post).astype(np.float32)
    alpha[yy >= 58] = 0.0                                                           # a gap to the snow
    alpha[post] = 1.0
    return np.clip(rgb, 0, 1), None, alpha


def tex_chairlift(name):
    """A chairlift's cable and its chairs, for a wall high over a ski run (`z` up near the towers' arms): the
    cable along the top, one chair to a tile hanging from it, two skiers riding in most, their skis dangling;
    see-through between. Give it `"tile": [4, 1.6]` - a chair every four units."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.zeros((T, T, 3), np.float32) + [0.2, 0.2, 0.22]
    a = np.zeros((T, T), np.float32)
    a[(yy >= 2) & (yy < 4)] = 1.0                                                   # the cable
    cx = 32
    hang = (np.abs(xx - cx) < 1) & (yy >= 4) & (yy < 44)
    seat = (yy >= 44) & (yy < 47) & (np.abs(xx - cx) < 7)
    back = (yy >= 32) & (yy < 46) & (np.abs(xx - (cx + 6)) < 1)
    foot = (yy >= 54) & (yy < 56) & (np.abs(xx - cx) < 6)
    bar = (yy >= 36) & (yy < 38) & (np.abs(xx - cx) < 7)
    for m in (hang, seat, back, foot, bar):
        a[m] = 1.0
    rgb[seat | back] = [0.25, 0.32, 0.5]
    if rng.random() < 0.85:                                                         # two riding
        for k, (dx, c) in enumerate(((-4, [0.85, 0.25, 0.2]), (2, [0.2, 0.5, 0.8]))):
            body = (yy >= 34) & (yy < 45) & (np.abs(xx - cx - dx) < 2.5)
            head = ((xx - cx - dx) ** 2 + (yy - 31) ** 2) < 7
            legs = (yy >= 45) & (yy < 54) & (np.abs(xx - cx - dx + 2 - (yy - 45) * 0.15) < 1.5)
            ski = (np.abs((yy - 54) - (xx - cx - dx + 6) * 0.25) < 0.8) & (np.abs(xx - cx - dx) < 7)
            rgb[body] = c
            rgb[head] = [0.9, 0.9, 0.92] if k else [0.15, 0.15, 0.18]
            rgb[legs] = [0.15, 0.17, 0.22]
            rgb[ski] = [0.9, 0.6, 0.1]
            for m in (body, head, legs, ski):
                a[m] = 1.0
    return np.clip(rgb, 0, 1), None, a


def _slalom_gate(k):
    w, h = 24, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (2, 20):
        cv.box(x, 2, 2.4, 38, z=1.0, top=0.5, bevel=0.8, mat=0)                    # the poles
        cv.ellipse(x + 1.2, 2, 1.6, 1.2, z=1.2, dome=0.6, mat=0)
    cv.polygon([(3, 5), (21, 5), (21, 21), (3, 21)], z=0.9, top=0.4, bevel=0.6, mat=1)    # the panel
    cv.box(3, 11.5, 18, 2.6, z=0.95, top=0.2, bevel=0.2, mat=2)                     # its white stripe
    return _prop(cv, [GATE_C[k], GATE_C[k], WHITE], relief=1.0, cavity=0.3, shadow=0.4)


def spr_slalom_gate():
    """A slalom gate on a ski run: a panel stretched between two poles stuck in the snow, a white stripe across
    it (two ways: `variant` 0 red, 1 blue - set them down the course turn and turn about)."""
    return _slalom_gate(0)


def spr_skier():
    """A skier seen from behind, going down a run ahead of you: crouched over the skis in a red jacket and dark
    salopettes, a white helmet with the goggles' strap round it, the poles tucked back under the arms."""
    w, h = 30, 46
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(7, 25), (1.5, 45)], 1.0, z=1.0, dome=0.3, mat=4)                     # the poles, back to the snow
    cv.stroke([(23, 25), (28.5, 45)], 1.0, z=1.0, dome=0.3, mat=4)
    cv.box(8, 42, 5, 4, z=1.1, top=0.3, bevel=0.4, mat=5)                           # the skis' tails
    cv.box(17, 42, 5, 4, z=1.1, top=0.3, bevel=0.4, mat=5)
    cv.box(8.5, 36, 4.5, 7, z=1.3, top=0.5, bevel=0.8, mat=3)                       # the boots
    cv.box(17, 36, 4.5, 7, z=1.3, top=0.5, bevel=0.8, mat=3)
    cv.polygon([(7, 25), (23, 25), (22, 37), (17, 37), (15, 30), (13, 37), (8, 37)], z=1.5, top=0.6, bevel=1.4,
               mat=1)                                                               # the salopettes, knees bent
    cv.polygon([(5, 13), (25, 13), (24, 27), (6, 27)], z=1.8, top=0.7, bevel=2.2, mat=0)   # the jacket
    cv.stroke([(6, 15), (5, 24)], 3.0, z=1.9, dome=0.6, mat=0)                       # the arms
    cv.stroke([(24, 15), (25, 24)], 3.0, z=1.9, dome=0.6, mat=0)
    cv.ellipse(15, 9, 5.0, 5.2, z=2.2, dome=0.9, mat=2)                              # the helmet
    cv.box(10, 9, 10, 1.6, z=2.3, top=0.2, bevel=0.2, mat=6)                        # the goggles' strap
    return _prop(cv, [JACKET, SKI_PANTS, SKI_HELMET, TRIM, CHROME, ramp('#e8a020', dark=0.4, light=1.3),
                      ramp('#30c0e0', dark=0.4, light=1.3)], relief=1.0, cavity=0.4, shadow=0.4)


def spr_ski_tips():
    """Your own skis, from the skier's eye: the two skis running ahead from your boots and curling up at their
    tips, a stripe down each. A shot's `vehicle` for a ski run: `"ahead": 0.9`, `"z": -0.3` or so."""
    w, h = 64, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for s in (-1, 1):
        x0 = 32 + s * 16
        tip = 32 + s * 10
        cv.polygon([(x0 - 6, 40), (x0 + 6, 40), (tip + 3, 7), (tip - 3, 7)], z=1.0, top=0.4,
                   bevel=1.0, mat=0)                                                # the ski
        cv.stroke([(x0, 40), (tip, 8)], 1.4, z=1.15, dome=0.3, mat=1)               # its stripe
        cv.ellipse(tip, 6.5, 3.4, 2.6, z=1.5, dome=0.5, mat=0)                       # the tip, curled up
        cv.stroke([(tip - 2.2, 5.6), (tip + 2.2, 5.6)], 0.8, z=1.7, dome=0.3, mat=2)   # its edge catching the light
        cv.box(x0 - 7, 31, 14, 9, z=1.6, top=0.6, bevel=1.6, mat=3)                 # the boot's toe
        cv.box(x0 - 7, 34, 14, 1.4, z=1.7, top=0.2, bevel=0.2, mat=4)               # a buckle
    return _prop(cv, [ramp('#1e2028', dark=0.5, light=2.4), ramp('#f07a1a', dark=0.4, light=1.3),
                      ramp('#e8e8ee', dark=0.5, light=1.2), ramp('#3a3e48', dark=0.45, light=1.8), CHROME],
                 relief=1.0, cavity=0.4, shadow=0.4)


def spr_lift_tower():
    """A chairlift's tower: a steel column on a footing, at its head a crossarm with the wheels the cables ride on
    either end. Stand them along a ski run under a pair of `chairlift` walls, its arms reaching both."""
    w, h = 44, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(18, 58, 8, 6, z=0.9, top=0.5, bevel=1.0, mat=1)                          # the footing
    cv.polygon([(19, 60), (25, 60), (24, 6), (20, 6)], z=1.2, top=0.6, bevel=1.4, mat=0)   # the column
    cv.box(1, 4, 42, 3.4, z=1.4, top=0.5, bevel=0.8, mat=0)                         # the crossarm
    for x in (2, 36):
        cv.box(x, 6.5, 6, 2.6, z=1.5, top=0.4, bevel=0.6, mat=2)                    # the wheel trains
        for wx in (x + 1, x + 4):
            cv.ellipse(wx + 0.5, 9.4, 1.3, 1.3, z=1.6, dome=0.6, mat=2)
    cv.stroke([(22, 7), (14, 14)], 1.0, z=1.3, dome=0.3, mat=0)                      # a brace or two
    cv.stroke([(22, 7), (30, 14)], 1.0, z=1.3, dome=0.3, mat=0)
    return _prop(cv, [LIFT, ramp('#9a968c', dark=0.45, light=1.4), TRIM], relief=1.0, cavity=0.4, shadow=0.4)


# ------------------------------------------------------------------ the sky lane and the Moon

def tex_city_night(name):
    """A city at night seen from far above, for the land `below` a road in the sky: a grid of avenues lit sodium
    orange with cars' lights along them, narrower streets between, the dark roofs of the blocks pricked with lit
    windows and here and there a sign in pink or cyan; a park or two. Its lights glow."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.zeros((T, T, 3), np.float32) + [0.05, 0.05, 0.08]
    rgb *= (0.7 + 0.6 * fbm(T, rng, 8, 2))[..., None]
    em = np.zeros((T, T), np.float32)
    park = (vnoise(T, 4, rng) > 0.72) & ((xx % 16) > 2) & ((yy % 16) > 2)
    rgb[park] = [0.04, 0.08, 0.05]
    lit = (rng.random((T, T)) < 0.06) & ~park & ((xx % 16) > 2) & ((yy % 16) > 2)
    rgb[lit] = np.array(LIT, np.float32)[rng.integers(0, 5, lit.sum())] * rng.uniform(0.5, 1.0, (lit.sum(), 1))
    em[lit] = 0.8
    street = ((xx % 8) == 0) | ((yy % 8) == 0)
    rgb[street & ~park] = [0.42, 0.26, 0.1]
    em[street & ~park] = 0.45
    avenue = ((xx % 16) < 2) | ((yy % 16) < 2)
    rgb[avenue] = [0.95, 0.6, 0.22]
    em[avenue] = 0.9
    cars = avenue & (rng.random((T, T)) < 0.18)
    rgb[cars] = np.where((rng.random(cars.sum()) < 0.5)[:, None], [1.0, 0.95, 0.85], [1.0, 0.18, 0.12])
    em[cars] = 1.0
    signs = (rng.random((T, T)) < 0.004) & ~avenue
    for y, x in np.argwhere(signs):
        c = [1.0, 0.3, 0.75] if rng.random() < 0.5 else [0.3, 0.95, 1.0]
        rgb[y:y + 2, x:x + 3] = c
        em[y:y + 2, x:x + 3] = 1.0
    return np.clip(rgb, 0, 1), em


def tex_light_lane(name):
    """A lane of light for flying traffic, for a road's `surface` in the sky: lines of cyan light a unit apart down
    its length and chevrons in magenta between them pointing the way, see-through between, so the city shows far
    below. A road surface tiles a unit to a texture, so a lane 2 wide has a line at each edge and one down its
    middle, a chevron either side. All of it glows."""
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.zeros((T, T, 3), np.float32) + [0.3, 0.95, 1.0]
    line = (xx < 2) | (xx > 61)
    v = (yy % 32).astype(np.float32)
    off = np.abs(xx - 31.5)
    chev = (np.abs(off * 0.8 - (v - 6)) < 1.3) & (off > 3) & (off < 18)
    rgb[chev] = [1.0, 0.3, 0.8]
    a = (line | chev).astype(np.float32)
    return rgb, a.copy(), a


def dec_crater():
    """A crater in the Moon's dust: a bowl, its wall toward the sun lit and the other in shadow, a raised rim, the
    ejecta thrown out round it in a paler blanket fading into the dust. Stamp it a few units across beside a road."""
    h = w = 48
    yy, xx = _grid(h, w)
    n = _noise(h, w, 6, 31)
    r = np.hypot(xx - 24, yy - 24) / 14.0 + (n - 0.5) * 0.12
    bowl, rim, blanket = r < 0.86, (r >= 0.86) & (r < 1.06), (r >= 1.06) & (r < 1.7)
    rgb = np.zeros((h, w, 3), np.float32) + [0.5, 0.5, 0.5]
    lit = np.clip((xx - 24) / 14.0, -1, 1)                                          # the sun from the left: the far
    rgb[bowl] = (np.array([0.4, 0.4, 0.41]) * (0.18 + 0.95 * ((lit[bowl] + 1) / 2) ** 1.5)[:, None])   # wall lit
    rgb[rim] = np.array([0.66, 0.66, 0.66]) * (0.85 + 0.3 * n[rim])[:, None]
    rgb[blanket] = np.array([0.6, 0.6, 0.6]) * (0.85 + 0.3 * n[blanket])[:, None]
    alpha = bowl * 0.95 + rim * 0.9 + blanket * np.clip((1.7 - r) / 0.64, 0, 1) * 0.55
    return _decal(rgb, alpha)


MOON_SUIT = ramp('#e2e2e0', dark=0.45, light=1.2)
FOIL_G = ramp('#d8a840', dark=0.4, light=1.4, warm=0.08)


def spr_moon_buggy():
    """A moon buggy seen from behind, driving on ahead of you: two astronauts side by side in white suits, the
    life-support packs on their backs and their helmets' gold visors catching the light at the sides, on a
    skeletal chassis between wire-mesh wheels under their fenders; the dish antenna on its mast at the front like
    an open umbrella, a gold-foiled box at the back."""
    w, h = 60, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(9, 4), (11, 30)], 1.0, z=0.9, dome=0.4, mat=4)                      # the dish's mast, front left
    cv.ellipse(8, 4, 8.0, 2.8, z=1.0, dome=0.45, angle=-8, mat=5)                   # the dish, open
    for a in np.linspace(-1, 1, 5):                                                 # its ribs
        cv.stroke([(8, 2.4), (8 + a * 7.5, 5.0 - abs(a) * 1.2)], 0.5, z=1.15, dome=0.3, mat=4)
    for x in (5, 55):                                                                # the rear wheels
        cv.box(x - 4.5, 30, 9, 18, z=1.2, top=0.6, bevel=1.6, mat=3)
        for y in range(32, 47, 3):
            cv.box(x - 4.5, y, 9, 0.8, z=1.3, top=0.2, bevel=0.2, mat=4)
        cv.stroke([(x - 5.5, 31), (x - 3, 27.5), (x + 3, 27.5), (x + 5.5, 31)], 1.5, z=1.5, dome=0.4, mat=1)
    cv.box(8, 32, 44, 5, z=1.0, top=0.6, bevel=1.0, mat=4)                           # the chassis
    cv.box(21, 35, 18, 8, z=1.1, top=0.6, bevel=1.0, mat=5)                          # the gold box
    for k, x in enumerate((19, 41)):                                                 # the astronauts
        cv.box(x - 9, 19, 18, 15, z=1.5, top=0.7, bevel=2.6, mat=0)                  # the suit's back, shoulders
        cv.stroke([(x - 8.5, 21), (x - 9.5, 31)], 3.2, z=1.6, dome=0.7, mat=0)        # the arms
        cv.stroke([(x + 8.5, 21), (x + 9.5, 31)], 3.2, z=1.6, dome=0.7, mat=0)
        if k == 0:
            cv.stroke([(x - 8.5, 23), (x - 9.3, 30)], 1.2, z=1.75, dome=0.3, mat=6)   # the commander's red stripes
            cv.stroke([(x + 8.5, 23), (x + 9.3, 30)], 1.2, z=1.75, dome=0.3, mat=6)
        cv.box(x - 6, 16, 12, 16, z=2.0, top=0.6, bevel=1.6, mat=1)                  # the pack
        cv.box(x - 6, 22.5, 12, 1.0, z=2.05, top=0.2, bevel=0.2, mat=4)              # its seam
        cv.stroke([(x - 4.5, 16.2), (x + 4.5, 16.2)], 1.6, z=2.1, dome=0.4, mat=4)    # the helmet's neck ring
        cv.ellipse(x, 10.5, 5.6, 5.4, z=2.4, dome=0.95, mat=0)                       # the helmet
        cv.stroke([(x - 5.2, 9), (x - 5.4, 13)], 1.2, z=2.45, dome=0.3, mat=5)        # the visor, gold at its edge
        cv.stroke([(x + 5.2, 9), (x + 5.4, 13)], 1.2, z=2.45, dome=0.3, mat=5)
    return _prop(cv, [MOON_SUIT, ramp('#c8c8c4', dark=0.45, light=1.3), CHROME, TYRE, TRIM, FOIL_G,
                      ramp('#c82a22', dark=0.4, light=1.4)], relief=1.0, cavity=0.4, shadow=0.45)


# ------------------------------------------------------------------ the footplate

LOCO = ramp('#1e4a30', dark=0.4, light=2.0, cool=0.04)
POLE_W = ramp('#6a5038', dark=0.4, light=1.5, warm=0.05)


def spr_loco_boiler():
    """The view from a steam engine's footplate: the boiler running away ahead of you in green paint, brass bands
    round it, the handrails along its sides, the dome on its back and the chimney at its far end over the
    smokebox. A shot's `vehicle` for a train: set `steam` over the chimney, and more drifting back."""
    w, h = 64, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(32, 50), (32, 16)], 44, z=7.0, dome=1.0, taper=(1.0, 0.32), mat=0)       # the boiler, round
    body = cv.id > 0
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    half = 22 - 15 * np.clip((50 - yy) / 34, 0, 1)                                   # the boiler's half-width
    u = (xx - 32) / half
    cv.tone[body] = (0.34 * np.sqrt(np.clip(1 - ((u + 0.25) / 1.1) ** 2, 0, 1)) - 0.2)[body]   # round: lit on top
    for t in (0.18, 0.5, 0.78):                                                       # brass bands, nearer apart
        y = 48 - 34 * t ** 0.8                                                         # as they go away
        cv.mat[body & (np.abs(yy - y - 0.0006 * (xx - 32) ** 2 * (1 - t)) < 0.4 + 0.4 * (1 - t))] = 1
    for sgn in (-1, 1):                                                                # the handrails
        rail = body & (np.abs((xx - 32) * sgn - (6.4 + (yy - 15) * 0.44)) < 0.6)
        cv.mat[rail] = 1
        cv.z[rail] += 0.8
    cv.ellipse(32, 25, 4.6, 3.4, z=7.6, dome=0.9, mat=1)                              # the dome
    cv.box(25.5, 11, 13, 5, z=4.0, top=0.6, bevel=1.4, mat=2)                         # the smokebox's top
    cv.box(29.5, 3, 5, 9, z=5.0, top=0.7, bevel=1.0, mat=2)                           # the chimney
    cv.ellipse(32, 3.2, 3.6, 1.4, z=5.4, dome=0.6, mat=2)                             # its cap
    cv.box(0, 42, 9, 6, z=2.0, top=0.4, bevel=0.8, mat=2)                             # the cab's spectacle plate
    cv.box(55, 42, 9, 6, z=2.0, top=0.4, bevel=0.8, mat=2)
    return _prop(cv, [LOCO, BRASS, ramp('#1c1c20', dark=0.5, light=2.2)], relief=1.0, cavity=0.4, shadow=0.4)


def spr_telegraph_pole():
    """A telegraph pole of the railway age: a weathered wooden pole, three crossarms near its top, each with its
    row of glass insulators. Stand them along a line every span with a `power_lines` wall at the arms."""
    w, h = 24, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(10.4, 2, 3.2, 62, z=1.0, top=0.6, bevel=1.4, mat=0)                        # the pole
    for y in (6, 11, 16):                                                            # the crossarms
        cv.box(1, y, 22, 2.2, z=1.3, top=0.5, bevel=0.6, mat=0)
        for x in (2.5, 7, 17, 21.5):                                                  # their insulators
            cv.ellipse(x, y - 1.0, 1.1, 1.3, z=1.6, dome=0.8, mat=1)
    return _prop(cv, [POLE_W, ramp('#9ac8b8', dark=0.5, light=1.4, cool=0.08)], relief=1.0, cavity=0.4, shadow=0.4)


# ------------------------------------------------------------------ the bulb fields

SAIL = ramp('#d8d0c0', dark=0.45, light=1.25)
THATCH = ramp('#6a5a46', dark=0.4, light=1.6, warm=0.04)
MILL_BRICK = ramp('#8a4632', dark=0.4, light=1.4, warm=0.06)
BIKE = ramp('#2a3a5a', dark=0.4, light=1.8, cool=0.06)
WICKER = ramp('#b0844a', dark=0.4, light=1.4, warm=0.06)
SKIN_B = ramp('#e0aa84', dark=0.45, light=1.3, warm=0.05)
TULIP_C = [ramp('#e0242a', dark=0.4, light=1.4), ramp('#f4c81a', dark=0.4, light=1.3, warm=0.05)]


def tex_tulip_field(name, petal=(0.88, 0.12, 0.14)):
    """A field of tulips in flower, for the ground beside a road through the bulb fields: rows of blooms in one
    colour (`petal`) four to a tile running along the road, their leaves and the dark soil between the rows. Seen
    down the road the rows close up into a band of colour to the horizon."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    p = np.array(petal, np.float32)
    rgb = np.array([0.22, 0.16, 0.1], np.float32) * (0.8 + 0.4 * fbm(T, rng, 8, 2))[..., None]     # the soil
    lane = xx % 16
    leaf = (lane >= 2) & (lane < 14)
    rgb[leaf] = np.array([0.2, 0.42, 0.16], np.float32) * (0.75 + 0.5 * fbm(T, rng, 16, 2)[leaf])[:, None]
    heads = (lane >= 3) & (lane < 13) & (vnoise(T, 32, rng) + 0.35 * rng.random((T, T)) > 0.62)
    shade = 0.75 + 0.45 * fbm(T, rng, 32, 2)
    rgb[heads] = p * shade[heads][:, None]
    top = heads & (rng.random((T, T)) < 0.2)
    rgb[top] = np.minimum(p * 1.35 + 0.12, 1.0)                                        # light on the petals
    return np.clip(rgb, 0, 1), None


def spr_windmill():
    """A windmill of the low country: a brick base, the tapering thatched body with a stage round it, the cap and
    four lattice sails set in an X. A landmark for the flat fields: stand it out in them, 4 tall at its own size."""
    w, h = 72, 100
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(19, 100), (53, 100), (51, 84), (21, 84)], z=1.0, top=0.6, bevel=1.6, mat=2)       # the base
    cv.box(33, 90, 6, 10, z=1.2, top=0.5, bevel=0.8, mat=4)                         # its door
    cv.polygon([(22, 85), (50, 85), (42, 36), (30, 36)], z=1.2, top=0.8, bevel=4.0, mat=1)         # the body
    for y in (52, 64, 76):                                                          # the thatch's courses
        cv.stroke([(24 + (85 - y) * 0.16, y), (48 - (85 - y) * 0.16, y)], 0.6, mode='carve', z=0.3)
    cv.box(31.6, 58, 3.4, 5, z=1.4, top=0.5, bevel=0.5, mat=4)                      # a window
    cv.box(10, 70, 52, 2.6, z=1.6, top=0.4, bevel=0.6, mat=3)                       # the stage
    for x in range(11, 62, 5):
        cv.box(x, 66, 0.9, 4, z=1.6, top=0.3, bevel=0.2, mat=3)                     # its rail's posts
    cv.box(10, 65.6, 52, 1.0, z=1.65, top=0.3, bevel=0.2, mat=3)                    # the rail
    cv.ellipse(36, 34, 9, 6.5, z=1.6, dome=0.9, mat=1)                              # the cap
    for ang in (38, 128, 218, 308):                                                 # the sails
        a = np.radians(ang)
        tip = (36 + np.cos(a) * 34, 34 + np.sin(a) * 34)
        cv.stroke([(36, 34), tip], 1.2, z=2.0, dome=0.4, mat=3)                    # the stock
        side = np.array([np.cos(a + np.pi / 2), np.sin(a + np.pi / 2)]) * 4.5
        start = np.array([36 + np.cos(a) * 8, 34 + np.sin(a) * 8])
        end = np.array(tip)
        cv.stroke([tuple(start + side), tuple(end + side)], 0.8, z=1.95, dome=0.3, mat=0)   # the lattice's edge
        for k in np.linspace(0, 1, 7):                                              # its bars
            p0 = start + (end - start) * k
            cv.stroke([tuple(p0), tuple(p0 + side)], 0.7, z=1.9, dome=0.3, mat=0)
    cv.ellipse(36, 34, 2.2, 2.2, z=2.2, dome=0.8, mat=4)                            # the hub
    return _prop(cv, [SAIL, THATCH, MILL_BRICK, ramp('#e8e4da', dark=0.45, light=1.2), TRIM], relief=1.0,
                 cavity=0.4, shadow=0.4)


def spr_cyclist():
    """Someone cycling ahead of you on an upright bike, seen from behind: a coat and a scarf, the back wheel under
    them and its mudguard, one knee up on the pedal."""
    w, h = 24, 44
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(10.6, 30, 2.8, 14, z=1.0, top=0.6, bevel=1.0, mat=3)                     # the back wheel, edge on
    cv.box(10.2, 28, 3.6, 3, z=1.1, top=0.5, bevel=0.6, mat=4)                      # the mudguard and its light
    cv.box(7, 26, 10, 2.2, z=1.2, top=0.4, bevel=0.6, mat=3)                        # the carrier
    cv.stroke([(9, 22), (8, 32), (9, 36)], 2.6, z=1.4, dome=0.7, mat=1)              # the legs, one up
    cv.stroke([(15, 22), (16, 28)], 2.6, z=1.4, dome=0.7, mat=1)
    cv.polygon([(6, 10), (18, 10), (19, 24), (5, 24)], z=1.7, top=0.7, bevel=2.0, mat=0)   # the coat
    cv.box(8, 8.5, 8, 2.6, z=1.9, top=0.4, bevel=0.8, mat=5)                        # the scarf
    cv.ellipse(12, 5.5, 3.4, 3.8, z=2.0, dome=0.9, mat=2)                           # the head
    return _prop(cv, [ramp('#3a6a8a', dark=0.4, light=1.5), ramp('#2a2a32', dark=0.45, light=1.9), HAIR_D, TRIM,
                      ramp('#e0302a', dark=0.5, light=1.3), ramp('#e8b020', dark=0.4, light=1.3)],
                 relief=1.0, cavity=0.4, shadow=0.4)


def spr_bike_bars():
    """Your own bicycle from the saddle: the swept-back handlebars, your hands on the grips (the backs of them, a
    thumb over each), a bell, and a wicker basket on the front with tulips in it. A shot's `vehicle` for a ride:
    `"ahead": 0.8`, `"z"` up near the eye."""
    w, h = 64, 34
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(20, 22), (44, 22), (42, 34), (22, 34)], z=1.0, top=0.6, bevel=1.6, mat=3)        # the basket
    for x in range(22, 43, 3):
        cv.stroke([(x, 23), (x + 0.4, 33)], 0.5, mode='carve', z=0.3)
    for k in range(7):                                                              # tulips in it
        x = 24 + k * 2.6 + (k % 2)
        cv.stroke([(x, 22), (x + (k - 3) * 0.6, 14 + (k % 3))], 0.7, z=1.3, dome=0.3, mat=4)     # stems
        cv.ellipse(x + (k - 3) * 0.6, 13 + (k % 3), 1.6, 2.0, z=1.6, dome=0.9, mat=5 + k % 2)   # heads
    cv.stroke([(4, 20), (14, 16), (32, 15), (50, 16), (60, 20)], 2.2, z=2.0, dome=0.6, mat=0)   # the bars
    cv.stroke([(32, 15), (32, 24)], 2.6, z=1.8, dome=0.6, mat=0)                    # the stem
    cv.ellipse(39, 13.5, 2.0, 1.6, z=2.4, dome=0.9, mat=7)                          # the bell
    for s in (-1, 1):                                                               # the hands on the grips
        x = 32 + s * 24
        cv.ellipse(x, 20.5, 5.4, 4.0, z=2.6, dome=0.9, mat=2)
        cv.stroke([(x - s * 4, 18.5), (x - s * 7.5, 17.5)], 2.0, z=2.8, dome=0.8, mat=2)         # the thumb
    return _prop(cv, [BIKE, BIKE, SKIN_B, WICKER, ramp('#3a7a2a', dark=0.4, light=1.5), TULIP_C[0], TULIP_C[1],
                      CHROME], relief=1.0, cavity=0.4, shadow=0.4)


# ------------------------------------------------------------------ the runway at night

AIRLINER = ramp('#c8ccd4', dark=0.4, light=1.5, cool=0.06)


def spr_runway_light():
    """A runway's edge light: a squat glass lens on a short stalk, lit - tint it (white for the runway's edges,
    blue for a taxiway, green at the threshold, red at its end). A row every unit or two down each edge."""
    w, h = 8, 8
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    lens = ((xx - 4) / 3.2) ** 2 + ((yy - 3.2) / 2.4) ** 2 < 1
    stalk = (np.abs(xx - 4) < 1) & (yy > 4.5)
    rgba[stalk] = [0.3, 0.3, 0.32, 1.0]
    rgba[lens] = [1.0, 1.0, 1.0, 1.0]
    em[lens] = 1.0
    return rgba, em


def spr_control_tower():
    """An airport's control tower at night: a tall concrete shaft, the cab at its top glazed all round and lit
    green-white, a red beacon on the roof, a few lit windows down the shaft."""
    w, h = 36, 100
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(13, 100), (23, 100), (22, 26), (14, 26)], z=1.0, top=0.6, bevel=2.0, mat=0)      # the shaft
    cv.polygon([(6, 16), (30, 16), (27, 26), (9, 26)], z=1.3, top=0.6, bevel=1.4, mat=1)        # the cab's glass
    cv.box(4, 12, 28, 4, z=1.5, top=0.6, bevel=1.0, mat=0)                          # its roof
    cv.box(8, 26, 20, 3, z=1.4, top=0.5, bevel=0.8, mat=0)                          # its floor
    cv.box(16.5, 6, 3, 6, z=1.6, top=0.5, bevel=0.6, mat=0)                         # the mast
    cv.ellipse(18, 5, 2.0, 2.0, z=1.8, dome=0.8, mat=2)                             # the beacon
    for y in (40, 56, 72):
        cv.box(16.6, y, 2.8, 3, z=1.1, top=0.3, bevel=0.3, mat=3)                   # a lit window or two
    for x in range(10, 28, 4):                                                      # the cab's mullions
        cv.stroke([(x, 16.5), (x + (x - 18) * 0.12, 25.5)], 0.6, z=1.4, dome=0.3, mat=0)
    rgba, _ = _prop(cv, [ramp('#5a5a62', dark=0.4, light=1.6), ramp('#a8f0c8', dark=0.7, light=1.2),
                         ramp('#ff3020', dark=0.7, light=1.2), ramp('#ffd890', dark=0.7, light=1.1)],
                    relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [1, 2, 3])


def spr_airliner():
    """An airliner seen from behind as it lifts off the runway ahead of you at night: the fuselage's round tail end,
    the fin rising over it, the wings swept back to their tips with the red and green lights, the engines under
    them, the white strobe and the tail's light lit."""
    w, h = 128, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(62, 4), (66, 4), (68, 30), (60, 30)], z=1.2, top=0.6, bevel=1.4, mat=0)          # the fin
    cv.polygon([(4, 34), (58, 30), (70, 30), (124, 34), (124, 36), (70, 38), (58, 38), (4, 36)], z=1.0,
               top=0.5, bevel=1.0, mat=0)                                            # the wings
    cv.polygon([(46, 26), (82, 26), (82, 29), (46, 29)], z=1.3, top=0.5, bevel=0.8, mat=0)        # the tailplane
    cv.ellipse(64, 34, 7.5, 7.5, z=1.6, dome=0.9, mat=0)                            # the fuselage, end on
    for x in (40, 88):                                                              # the engines
        cv.ellipse(x, 41, 5.0, 4.6, z=1.4, dome=0.8, mat=1)
        cv.ellipse(x, 41, 3.0, 2.8, z=1.5, dome=0.4, mat=2)
    cv.ellipse(4, 35, 1.8, 1.8, z=1.8, dome=0.8, mat=3)                             # the port light, red
    cv.ellipse(124, 35, 1.8, 1.8, z=1.8, dome=0.8, mat=4)                           # starboard, green
    cv.ellipse(64, 4, 1.6, 1.6, z=1.8, dome=0.8, mat=5)                             # the fin's light
    cv.ellipse(64, 27.5, 1.4, 1.4, z=1.9, dome=0.8, mat=5)                          # the tail cone's light
    rgba, _ = _prop(cv, [AIRLINER, ramp('#8a8e98', dark=0.4, light=1.6), ramp('#2a2a32', dark=0.5, light=1.6),
                         ramp('#ff3020', dark=0.7, light=1.2), ramp('#30ff70', dark=0.7, light=1.2),
                         ramp('#ffffff', dark=0.8, light=1.0)], relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [3, 4, 5])


def spr_cockpit():
    """The cockpit of your own aircraft, from the left seat: the glareshield across the bottom of the view with the
    instruments glowing under it, the windscreen's frame and its pillars round the view, the yoke's horns. A shot's
    `vehicle`: `"ahead": 0.9`, `"z"` so the frame's top is out of the view."""
    w, h = 96, 72
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(0, 56), (96, 56), (96, 72), (0, 72)], z=1.0, top=0.5, bevel=1.0, mat=0)          # the panel
    cv.polygon([(0, 51), (96, 51), (96, 57), (0, 57)], z=1.6, top=0.5, bevel=1.2, mat=1)          # the glareshield
    for x0 in (8, 26, 54, 72):                                                      # the screens, glowing
        cv.box(x0, 59, 15, 9, z=1.2, top=0.3, bevel=0.6, mat=2)
        cv.box(x0 + 2, 61, 11, 1.2, z=1.3, top=0.2, bevel=0.2, mat=3)
        cv.box(x0 + 2, 64, 7, 1.2, z=1.3, top=0.2, bevel=0.2, mat=3)
    cv.polygon([(0, 0), (10, 0), (15, 51), (0, 51)], z=1.4, top=0.5, bevel=1.4, mat=0)            # the pillars
    cv.polygon([(96, 0), (86, 0), (81, 51), (96, 51)], z=1.4, top=0.5, bevel=1.4, mat=0)
    cv.polygon([(0, 0), (96, 0), (96, 5), (0, 5)], z=1.4, top=0.5, bevel=1.0, mat=0)              # the frame's top
    cv.stroke([(30, 72), (30, 66), (24, 64)], 2.4, z=2.0, dome=0.6, mat=0)          # the yoke's horns
    cv.stroke([(30, 66), (36, 64)], 2.4, z=2.0, dome=0.6, mat=0)
    rgba, _ = _prop(cv, [ramp('#22242a', dark=0.5, light=2.0), ramp('#18181c', dark=0.5, light=2.0),
                         ramp('#0a2a3a', dark=0.6, light=1.3), ramp('#60f0a0', dark=0.7, light=1.1)],
                    relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [2, 3]) * 0.5


# ------------------------------------------------------------------ the bayou and the dunes

BOARDS = ramp('#6a5e4e', dark=0.4, light=1.6, warm=0.03)
TIN = ramp('#8a5a3a', dark=0.4, light=1.6, warm=0.06)
CAMEL = ramp('#c89a62', dark=0.4, light=1.35, warm=0.06)
RUG = [ramp('#a8282a', dark=0.4, light=1.4), ramp('#2a3a8a', dark=0.4, light=1.5), ramp('#e0b040', dark=0.4, light=1.3)]
ROBE = ramp('#e8e2d4', dark=0.45, light=1.2)
SANDSTONE = ramp('#d8b07a', dark=0.4, light=1.3, warm=0.06)


def spr_stilt_shack():
    """A shack on stilts over the bayou: weathered boards under a rusted tin roof, a porch out front on its posts,
    a window lit warm and a lantern by the door - the two of them glow. A landmark on a swamp's water."""
    w, h = 64, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (8, 20, 34, 48, 58):                                                   # the stilts
        cv.box(x, 38, 2.4, 18, z=0.8, top=0.5, bevel=0.6, mat=0)
    cv.box(4, 36, 58, 3, z=1.0, top=0.5, bevel=0.6, mat=0)                          # the porch's deck
    cv.box(12, 14, 44, 23, z=1.2, top=0.6, bevel=1.4, mat=0)                        # the cabin
    for y in range(16, 36, 3):                                                      # its boards
        cv.stroke([(12, y), (56, y)], 0.5, mode='carve', z=0.3)
    cv.polygon([(6, 16), (58, 16), (52, 4), (12, 4)], z=1.6, top=0.5, bevel=1.0, mat=1)            # the tin roof
    for x in range(10, 58, 3):
        cv.stroke([(x, 15.5), (x * 0.86 + 4.5, 4.5)], 0.5, mode='carve', z=0.25)
    cv.box(18, 20, 9, 16, z=1.3, top=0.5, bevel=0.8, mat=2)                         # the door
    cv.box(36, 21, 11, 8, z=1.3, top=0.4, bevel=0.6, mat=3)                         # the window, lit
    cv.box(41, 21, 1, 8, z=1.4, top=0.2, bevel=0.2, mat=2)
    cv.box(29.5, 21, 3, 4, z=1.5, top=0.4, bevel=0.4, mat=3)                        # the lantern
    cv.stroke([(4, 30), (4, 36)], 0.8, z=1.1, dome=0.3, mat=0)                      # the porch rail
    cv.stroke([(4, 30), (12, 30)], 0.8, z=1.1, dome=0.3, mat=0)
    rgba, _ = _prop(cv, [BOARDS, TIN, ramp('#3a2e24', dark=0.45, light=1.6), ramp('#ffc870', dark=0.8, light=1.1)],
                    relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [3])


def spr_camel():
    """A camel walking ahead in a caravan, seen from behind: its long legs and tail, the hump under a saddle
    blanket in red and blue, a rider in a pale robe and a headcloth, the neck and head reaching on beyond."""
    w, h = 36, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(24, 22), (27, 12), (26, 6)], 3.6, z=0.8, dome=0.7, mat=0)           # the neck, off to one side
    cv.ellipse(26.5, 5, 3.4, 3.0, z=0.9, dome=0.8, mat=0)                           # its head, beyond
    for x in (14.5, 21.5):                                                          # the far legs, between
        cv.stroke([(x, 38), (x, 55)], 2.2, z=0.9, dome=0.6, mat=0)
    for x in (9.5, 26.5):                                                           # the hind legs
        cv.stroke([(x, 34), (x - 0.8 * (1 if x < 18 else -1), 45), (x, 56)], 3.6, z=1.1, dome=0.7,
                  taper=(1.0, 0.7), mat=0)
    cv.ellipse(18, 33, 11.5, 8.0, z=1.3, dome=0.9, mat=0)                           # the haunches, from behind
    cv.stroke([(18, 36), (18.5, 45)], 1.2, z=1.6, dome=0.4, mat=0)                  # the tail
    cv.polygon([(8, 20), (28, 20), (30, 31), (6, 31)], z=1.6, top=0.5, bevel=1.4, mat=1)          # the blanket
    cv.box(6.4, 27, 23, 2.0, z=1.7, top=0.3, bevel=0.3, mat=2)                      # its stripe
    cv.polygon([(12, 9), (24, 9), (25, 22), (11, 22)], z=1.9, top=0.6, bevel=2.0, mat=3)          # the rider's robe
    cv.ellipse(18, 6.5, 3.4, 3.6, z=2.1, dome=0.9, mat=3)                           # the headcloth
    cv.box(14.8, 5.2, 6.4, 1.2, z=2.2, top=0.2, bevel=0.2, mat=4)                   # its band
    return _prop(cv, [CAMEL, RUG[0], RUG[1], ROBE, TRIM], relief=1.0, cavity=0.4, shadow=0.4)


def spr_camel_head():
    """Your own camel from the saddle: its long neck reaching away from you over the sand, the head at the end of
    it with the ears up, the halter's rope back to your hands, a corner of the saddle blanket. A shot's `vehicle`
    for a caravan: `"ahead": 1.0`, `"z"` up near the eye."""
    w, h = 48, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(0, 40), (12, 36), (36, 36), (48, 40), (48, 48), (0, 48)], z=1.0, top=0.5, bevel=1.4, mat=1)  # the blanket
    cv.box(0, 42, 48, 2.2, z=1.1, top=0.3, bevel=0.3, mat=2)                        # its stripe
    cv.stroke([(24, 42), (25, 28), (23, 15)], 12.0, z=1.6, dome=0.9, taper=(1.0, 0.55), mat=0)     # the neck
    cv.ellipse(23, 10, 6.0, 6.6, z=1.9, dome=0.9, mat=0)                            # the head, from behind
    for sgn in (-1, 1):
        cv.ellipse(23 + sgn * 4.6, 4.2, 1.5, 2.4, z=2.0, dome=0.7, mat=0)           # the ears
    cv.stroke([(21, 12), (14, 30), (10, 40)], 0.7, z=2.2, dome=0.3, mat=3)          # the halter rope
    cv.stroke([(25, 12), (32, 30), (36, 40)], 0.7, z=2.2, dome=0.3, mat=3)
    return _prop(cv, [CAMEL, RUG[0], RUG[2], ramp('#3a2a1e', dark=0.45, light=1.6)], relief=1.0, cavity=0.4,
                 shadow=0.4)


def spr_pyramid():
    """A great pyramid far off across the desert: its faces of pale stone, the sunlit one and the shaded one, the
    courses showing, the top a little broken. A billboard for the horizon, 20 tall at its own size."""
    w, h = 96, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(0, 56), (48, 3), (96, 56)], z=1.0, top=0.5, bevel=0.6, mat=0)
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    body = cv.id > 0
    cv.tone[body & (xx > 48 + (yy - 3) * 0.12)] = -0.3                                  # the face in shade
    for y in range(6, 56, 3):                                                       # the courses
        cv.z[body & (np.abs(yy - y) < 0.5)] -= 0.3
    return _prop(cv, [SANDSTONE], relief=1.0, cavity=0.4, shadow=0.4)


# ------------------------------------------------------------------ the candy road

CANE_RED = ramp('#e01e3a', dark=0.4, light=1.4)
ICING = ramp('#fff6f8', dark=0.5, light=1.1)
GINGER = ramp('#b8682e', dark=0.4, light=1.4, warm=0.06)
GUM_C = [ramp('#ff4a8a', dark=0.45, light=1.3), ramp('#4ad0ff', dark=0.45, light=1.3, cool=0.05),
         ramp('#a8f040', dark=0.45, light=1.3), ramp('#ffb020', dark=0.45, light=1.3, warm=0.05)]


def tex_peppermint(name):
    """A road of peppermint candy: broad stripes of red and white running slantwise across it, glossy, a little
    melted at their edges, a glint of sugar here and there."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    band = ((xx + yy) // 16) % 2 == 0
    wob = (fbm(T, rng, 8, 2) - 0.5) * 6
    band = (((xx + yy + wob) // 16) % 2).astype(int) == 0
    rgb = np.where(band[..., None], np.array([0.88, 0.12, 0.2], np.float32), np.array([0.97, 0.94, 0.94], np.float32))
    rgb = rgb * (0.9 + 0.14 * fbm(T, rng, 4, 3))[..., None]
    glint = rng.random((T, T)) < 0.01
    rgb[glint] = [1.0, 1.0, 1.0]
    return np.clip(rgb, 0, 1), None


def tex_frosting(name):
    """Pink frosting spread thick, for the ground of a candy land: soft swirls of icing and sprinkles of every
    colour scattered over it."""
    rng = _rng(name)
    rgb = np.array([0.98, 0.7, 0.8], np.float32) * (0.86 + 0.2 * fbm(T, rng, 6, 3))[..., None]
    swirl = np.abs(np.sin(fbm(T, rng, 3, 2) * 18)) < 0.12
    rgb[swirl] *= 0.88
    colours = np.array([[1.0, 0.95, 0.3], [0.3, 0.8, 1.0], [0.4, 0.95, 0.4], [1.0, 1.0, 1.0], [0.6, 0.3, 0.9]],
                       np.float32)
    for y, x in np.argwhere(rng.random((T, T)) < 0.03):
        c = colours[rng.integers(0, len(colours))]
        if rng.random() < 0.5:
            rgb[y, x:x + 2] = c
        else:
            rgb[y:y + 2, x] = c
    return np.clip(rgb, 0, 1), None


def spr_candy_cane():
    """A candy cane as tall as a lamp post, striped red and white round its stem, its crook bent over the road. Set
    them in rows along a candy road."""
    w, h = 24, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    pts = [(8, 64), (8, 14)] + [(12 + 5.5 * np.cos(a), 14 - 5.5 * np.sin(a)) for a in np.linspace(np.pi, 0, 10)][1:] \
        + [(17.5, 20)]
    cv.stroke(pts, 5.2, z=1.2, dome=0.9, mat=0)                                     # the cane, white
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    cane = cv.id > 0
    cv.mat[cane & ((((yy + xx * 0.8) // 4) % 2) == 0)] = 1                          # its red stripes, slantwise
    return _prop(cv, [ICING, CANE_RED], relief=1.0, cavity=0.3, shadow=0.4)


def spr_lollipop():
    """A lollipop tree: a great swirled disc of candy in pink and white on a white stick, standing in the frosting."""
    w, h = 40, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(18.6, 30, 2.8, 34, z=1.0, top=0.6, bevel=1.0, mat=0)                     # the stick
    cv.ellipse(20, 18, 16, 16, z=1.5, dome=0.6, mat=1)                              # the disc
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    r = np.hypot(xx - 20, yy - 18)
    th = np.arctan2(yy - 18, xx - 20)
    disc = (cv.id > 0) & (r < 16.5)
    cv.mat[disc & ((((r * 0.55 + th * 1.6 / np.pi * 2) % 2) < 1))] = 2              # the swirl
    return _prop(cv, [ICING, ramp('#ff5aa8', dark=0.45, light=1.3), ICING], relief=1.0, cavity=0.3, shadow=0.4)


def _gumdrop(k):
    w, h = 24, 20
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(12, 15, 11, 14, z=1.4, dome=0.8, mat=0)                              # the drop, sugared
    rgba, em = _prop(cv, [GUM_C[k]], relief=1.0, cavity=0.3, shadow=0.4)
    rng = np.random.default_rng(80 + k)
    sugar = (rng.random(rgba.shape[:2]) < 0.12) & (rgba[..., 3] > 0)
    rgba[sugar, :3] = np.minimum(rgba[sugar, :3] * 1.3 + 0.15, 1.0)
    return rgba, em


def spr_gumdrop():
    """A gumdrop the size of a hill, sugared all over: pink, or `variant` 1 blue, 2 green, 3 orange."""
    return _gumdrop(0)


def spr_gingerbread_house():
    """A gingerbread house: walls of gingerbread piped with white icing, a roof thick with icing like snow and sweets
    along its eaves, a candy-cane door frame, its windows lit warm."""
    w, h = 64, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(10, 26, 44, 30, z=1.0, top=0.6, bevel=1.6, mat=0)                        # the walls
    cv.polygon([(4, 28), (60, 28), (32, 4)], z=1.4, top=0.6, bevel=1.6, mat=1)       # the roof, iced
    for x in range(8, 58, 6):                                                       # sweets along the eaves
        cv.ellipse(x, 28.5, 2.0, 2.0, z=1.7, dome=0.9, mat=3 + (x // 6) % 3)
    cv.box(27, 38, 10, 18, z=1.2, top=0.5, bevel=1.0, mat=2)                        # the door frame
    cv.box(29, 40, 6, 16, z=1.25, top=0.5, bevel=0.8, mat=0)                        # the door
    for x0 in (14, 42):                                                             # the windows, lit
        cv.box(x0, 34, 8, 8, z=1.2, top=0.4, bevel=0.6, mat=6)
        cv.box(x0 - 1, 33, 10, 1.2, z=1.3, top=0.2, bevel=0.2, mat=1)              # icing over them
        cv.box(x0 - 1, 42, 10, 1.2, z=1.3, top=0.2, bevel=0.2, mat=1)
    for y in (48, 52):                                                              # piped icing on the walls
        cv.stroke([(11, y), (26, y)], 0.8, z=1.2, dome=0.4, mat=1)
        cv.stroke([(38, y), (53, y)], 0.8, z=1.2, dome=0.4, mat=1)
    rgba, _ = _prop(cv, [GINGER, ICING, CANE_RED, GUM_C[0], GUM_C[1], GUM_C[2], ramp('#ffd080', dark=0.8, light=1.1)],
                    relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [6])


# ------------------------------------------------------------------ the ghost train

BONE = ramp('#e8e2cc', dark=0.4, light=1.25)
RIDE_CAR = ramp('#4a1a5a', dark=0.4, light=1.9)


def spr_skeleton():
    """A skeleton leaping out at a ghost train's riders: its skull grinning, the ribs, the arms flung up and the
    bony fingers spread, one leg kicked up - pale bone that a green light makes glow."""
    w, h = 32, 52
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(16, 7, 5.0, 5.4, z=2.0, dome=0.9, mat=0)                             # the skull
    cv.box(13, 11, 6, 3, z=1.9, top=0.5, bevel=0.6, mat=0)                          # the jaw
    for x in (13.8, 18.2):                                                          # the eye sockets
        cv.ellipse(x, 6.6, 1.5, 1.6, z=2.1, dome=0.2, mat=1)
    cv.box(13.6, 11.6, 4.8, 0.8, z=2.0, top=0.2, bevel=0.1, mat=1)                  # the teeth's line
    cv.stroke([(16, 14), (16, 32)], 1.6, z=1.6, dome=0.5, mat=0)                    # the spine
    for k, y in enumerate(range(17, 28, 3)):                                        # the ribs
        half = 6.0 - k * 0.6
        cv.stroke([(16 - half, y + 1.5), (16, y), (16 + half, y + 1.5)], 1.0, z=1.8, dome=0.5, mat=0)
    cv.stroke([(12, 32), (20, 32)], 2.0, z=1.7, dome=0.5, mat=0)                    # the pelvis
    for s in (-1, 1):                                                               # the arms, flung up
        cv.stroke([(16 + s * 6, 16), (16 + s * 11, 10), (16 + s * 13, 2)], 1.4, z=1.9, dome=0.5, mat=0)
        for f in (-1.4, 0, 1.4):                                                    # the fingers, spread
            cv.stroke([(16 + s * 13, 2.5), (16 + s * 13 + f, 0)], 0.6, z=2.0, dome=0.3, mat=0)
    cv.stroke([(13, 33), (11, 42), (12, 51)], 1.6, z=1.6, dome=0.5, mat=0)          # a leg standing
    cv.stroke([(19, 33), (25, 39), (28, 35)], 1.6, z=1.6, dome=0.5, mat=0)          # a leg kicked up
    return _prop(cv, [BONE, ramp('#1a1418', dark=0.6, light=1.4)], relief=1.0, cavity=0.4, shadow=0.4)


def spr_ghost_car():
    """The front of your own car on a ghost train, from its seat: a dark purple cowl with a grinning skull on its
    nose, its eyes lit red, and the padded lap bar across in front of you. A shot's `vehicle` for a dark ride."""
    w, h = 64, 36
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(2, 36), (62, 36), (54, 10), (10, 10)], z=1.0, top=0.6, bevel=3.0, mat=0)          # the cowl
    cv.ellipse(32, 14, 8.0, 7.4, z=1.8, dome=0.9, mat=1)                            # the skull on its nose
    cv.box(27.5, 19, 9, 4, z=1.7, top=0.5, bevel=0.6, mat=1)                        # its jaw
    for x in (28.6, 35.4):
        cv.ellipse(x, 13.6, 2.0, 2.2, z=1.95, dome=0.4, mat=2)                      # its eyes, lit
    cv.box(28.5, 20.6, 7, 0.8, z=1.8, top=0.2, bevel=0.1, mat=3)                    # its teeth's line
    cv.stroke([(4, 30), (14, 26), (50, 26), (60, 30)], 3.6, z=2.4, dome=0.8, mat=4)  # the lap bar
    rgba, _ = _prop(cv, [RIDE_CAR, BONE, ramp('#ff2010', dark=0.8, light=1.2), ramp('#1a1418', dark=0.6, light=1.4),
                         ramp('#2a2a30', dark=0.5, light=1.9)], relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [2])


# ------------------------------------------------------------------ the blossom road

BLOSSOM = ramp('#f4a8c4', dark=0.5, light=1.25)
BARK_C = ramp('#4a3436', dark=0.4, light=1.7)
VERMILION = ramp('#d8401e', dark=0.4, light=1.4, warm=0.06)
PEAK_SNOW = ramp('#eef2f8', dark=0.55, light=1.1, cool=0.04)


def spr_cherry_tree():
    """A cherry tree in full bloom: a dark trunk forking into spreading limbs, the crown a cloud of pink blossom, a
    few petals drifting down under it. Line a road with them in spring."""
    w, h = 80, 72
    cv = Canvas(w, h, wrap=False, ground=-9)
    rng = np.random.default_rng(91)
    cv.stroke([(40, 72), (39, 52), (36, 40)], 5.0, z=1.0, dome=0.8, taper=(1.0, 0.7), mat=1)       # the trunk
    for pts in (((38, 46), (24, 34), (12, 28)), ((40, 44), (54, 32), (68, 28)), ((37, 42), (34, 26), (30, 16)),
                ((40, 44), (46, 24), (52, 14))):
        cv.stroke(pts, 2.4, z=1.1, dome=0.7, taper=(1.0, 0.5), mat=1)              # the limbs
    for _ in range(46):                                                             # the blossom, in clouds
        cx, cy = rng.normal(40, 15), rng.normal(26, 8)
        cv.ellipse(cx, cy, rng.uniform(4, 8), rng.uniform(3, 6), z=1.6 + rng.random() * 0.6, dome=0.8, mat=0,
                   rough=0.3, rng=rng)
    rgba, em = _prop(cv, [BLOSSOM, BARK_C], relief=1.0, cavity=0.4, shadow=0.45)
    for _ in range(14):                                                             # petals drifting down
        y, x = int(rng.uniform(42, 70)), int(rng.uniform(12, 68))
        if rgba[y, x, 3] == 0:
            rgba[y, x] = [1.0, 0.78, 0.86, 1.0]
    return rgba, em


def spr_torii():
    """A shrine gate standing over a road: two vermilion pillars on black feet, the lower beam through them, the top
    beam over it curving up at its ends and capped in black, a plaque between the two. Stand it at `x` 0 across the
    road; 3.6 tall at its own size."""
    w, h = 96, 72
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (18, 70):
        cv.box(x, 14, 8, 58, z=1.0, top=0.6, bevel=2.0, mat=0)                     # the pillars
        cv.box(x - 1, 64, 10, 8, z=1.1, top=0.5, bevel=1.0, mat=1)                  # their black feet
    cv.box(10, 22, 76, 5, z=1.3, top=0.5, bevel=1.0, mat=0)                         # the lower beam
    xs = np.linspace(0, 96, 25)
    curve = [(x, 9 - 5 * ((x - 48) / 48) ** 4) for x in xs]
    cv.stroke(curve, 5.0, z=1.5, dome=0.6, mat=0)                                   # the top beam, curving up
    cv.stroke([(x, y - 3.2) for x, y in curve], 2.4, z=1.7, dome=0.5, mat=1)        # its black cap
    cv.box(44, 11, 8, 11, z=1.6, top=0.5, bevel=0.8, mat=1)                         # the plaque
    cv.box(45.5, 12.5, 5, 8, z=1.7, top=0.3, bevel=0.4, mat=2)
    return _prop(cv, [VERMILION, ramp('#1e1a1c', dark=0.5, light=2.0), ramp('#d8b040', dark=0.4, light=1.3)],
                 relief=1.0, cavity=0.4, shadow=0.4)


def spr_snow_peak():
    """A lone volcano far off, its cone rising alone from the plain, snow down its upper slopes in streaks, the rest
    blue with distance. A billboard for the horizon, 18 tall at its own size."""
    w, h = 128, 48
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(0, 48), (50, 4), (78, 4), (128, 48)], z=1.0, top=0.4, bevel=0.6, mat=0)
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    body = cv.id > 0
    n = _noise(h, w, 4, 95)
    snowline = 18 + 7 * np.sin(xx * 0.45) * (n - 0.3) + 6 * n
    cv.mat[body & (yy < snowline)] = 1                                              # the snow, in streaks
    cv.tone[body & (xx > 64 + (yy - 4) * 0.1)] = -0.18                               # the far side in shade
    return _prop(cv, [ramp('#6a82a8', dark=0.5, light=1.3, cool=0.08), PEAK_SNOW], relief=1.0, cavity=0.3, shadow=0.4)


# ------------------------------------------------------------------ the storm chase

BARN_RED = ramp('#a8281e', dark=0.4, light=1.4, warm=0.04)
PICKUP = ramp('#d8d4c8', dark=0.4, light=1.3)


def tex_wheat_field(name):
    """A field of ripe wheat, for the ground beside a road across the plains: gold ears packed close in rows along
    the road, darker between them, a few stalks bent over by the wind."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    rgb = np.array([0.82, 0.66, 0.3], np.float32) * (0.78 + 0.36 * fbm(T, rng, 8, 3))[..., None]
    rgb[(xx % 8) < 2] *= 0.68                                                       # between the rows
    ears = rng.random((T, T)) < 0.22
    rgb[ears] = np.minimum(rgb[ears] * 1.22 + 0.04, 1.0)
    flat = vnoise(T, 6, rng) > 0.74                                                 # bent over by the wind
    rgb[flat] *= [1.08, 1.04, 0.92]
    return np.clip(rgb, 0, 1), None


def spr_tornado():
    """A tornado on the plains: the funnel dropping out of the cloud base, wide at the top and twisting down to a
    rope where it touches the ground, debris whirling round its foot in a dark skirt. A billboard far out in the
    fields, 30 tall at its own size."""
    w, h = 64, 96
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    n = _noise(h, w, 6, 71)
    t = yy / h
    centre = 32 + 6 * np.sin(t * 5.0) * t                                           # it snakes as it comes down
    half = 4.5 + 24 * (1 - t) ** 2.2
    body = np.abs(xx - centre) < half * (0.85 + 0.3 * n)
    band = np.sin((yy * 0.9 - (xx - centre) * 1.6 / (half + 1) * 3)) * 0.5 + 0.5        # the twist's bands
    shade = 0.55 + 0.25 * band + 0.25 * (xx < centre)                               # lit on the left
    rgba[body, :3] = (np.array([0.42, 0.44, 0.48]) * shade[body][:, None] * (0.85 + 0.3 * n[body])[:, None])
    rgba[body, 3] = np.clip(0.7 + 0.3 * (1 - t[body]), 0, 1)
    base = (yy < 14 + 6 * n) & (np.abs(xx - 32) < 31 * (0.75 + 0.35 * n))          # the cloud base it drops from
    a = np.clip((31 - np.abs(xx - 32)) / 14, 0, 1) * np.clip((14 + 6 * n - yy) / 6, 0, 1)
    rgba[base, :3] = np.array([0.3, 0.32, 0.36]) * (0.8 + 0.4 * n[base])[:, None]
    rgba[base, 3] = np.maximum(rgba[base, 3], a[base])
    skirt = (yy > h - 26) & (np.abs(xx - centre) < (yy - (h - 26)) * 1.1 + 5) & (n > 0.22)
    rgba[skirt, :3] = np.array([0.36, 0.32, 0.28]) * (0.8 + 0.4 * n[skirt])[:, None]  # dust and debris whirling
    rgba[skirt, 3] = np.maximum(rgba[skirt, 3], 0.55 + 0.35 * np.clip((yy[skirt] - (h - 26)) / 26, 0, 1))
    return rgba, np.zeros((h, w), np.float32)


def spr_barn():
    """A red barn on the plains: the gambrel roof's two pitches, white trim, the big doors crossed with white
    braces, a hay door up in the gable, and a tin grain silo beside it with its domed cap."""
    w, h = 80, 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(60, 8, 14, 48, z=1.0, top=0.6, bevel=3.0, mat=2)                         # the silo
    cv.ellipse(67, 8, 7.4, 4.4, z=1.3, dome=0.9, mat=2)                             # its cap
    for y in range(14, 56, 5):
        cv.stroke([(60, y), (74, y)], 0.5, mode='carve', z=0.3)
    cv.polygon([(4, 56), (56, 56), (56, 26), (46, 14), (30, 6), (14, 14), (4, 26)], z=1.2, top=0.6, bevel=1.6,
               mat=0)                                                               # the barn
    cv.stroke([(3, 26), (14, 14), (30, 5.5), (46, 14), (57, 26)], 1.6, z=1.6, dome=0.5, mat=1)   # the roof's trim
    cv.box(18, 34, 24, 22, z=1.3, top=0.5, bevel=1.0, mat=1)                        # the doors' frame
    cv.box(19.5, 35.5, 21, 20.5, z=1.35, top=0.5, bevel=0.8, mat=0)
    cv.stroke([(19.5, 35.5), (40.5, 56)], 1.2, z=1.5, dome=0.4, mat=1)              # the braces
    cv.stroke([(40.5, 35.5), (19.5, 56)], 1.2, z=1.5, dome=0.4, mat=1)
    cv.box(25, 17, 10, 9, z=1.3, top=0.5, bevel=0.8, mat=3)                         # the hay door
    return _prop(cv, [BARN_RED, WHITE, CHROME, ramp('#3a2a20', dark=0.45, light=1.6)], relief=1.0, cavity=0.4,
                 shadow=0.4)


def spr_pickup_truck():
    """A storm chasers' pickup seen from behind, racing ahead of you: a pale truck, its tailgate and bumper, the
    bed with gear strapped in it, a mast of weather instruments on the cab's roof, the tail lights lit."""
    w, h = 48, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(22.6, 0, 1.6, 12, z=1.3, top=0.4, bevel=0.4, mat=3)                      # the instrument mast
    cv.box(17, 1, 12, 1.4, z=1.4, top=0.3, bevel=0.3, mat=3)
    cv.ellipse(18, 1.6, 1.8, 1.2, z=1.5, dome=0.7, mat=3)                           # the cups of the anemometer
    cv.ellipse(28, 1.6, 1.8, 1.2, z=1.5, dome=0.7, mat=3)
    cv.box(10, 10, 28, 9, z=1.0, top=0.6, bevel=1.6, mat=0)                         # the cab
    cv.box(12, 11.5, 24, 6, z=1.1, top=0.3, bevel=0.6, mat=4)                       # its back window
    cv.box(3, 19, 42, 15, z=1.2, top=0.6, bevel=1.6, mat=0)                         # the bed and tailgate
    cv.box(6, 17, 36, 4, z=1.3, top=0.5, bevel=0.8, mat=5)                          # gear strapped in the bed
    for x in (3.5, 40.5):                                                           # the tail lights
        cv.box(x, 21, 4, 7, z=1.4, top=0.4, bevel=0.6, mat=1)
    cv.box(2, 33, 44, 3, z=1.3, top=0.5, bevel=0.8, mat=3)                          # the bumper
    cv.box(19, 26, 10, 4, z=1.35, top=0.3, bevel=0.4, mat=2)                        # the plate
    for x in (4, 36):
        cv.box(x, 33, 8, 7, z=0.8, top=0.6, bevel=1.4, mat=6)                       # the tyres
    return _prop(cv, [PICKUP, TAIL, PLATE, CHROME, GLASS, ramp('#3a5a3a', dark=0.4, light=1.5), TYRE],
                 em=_tail_em(cv, [1]), relief=1.0, cavity=0.4, shadow=0.45)


# ------------------------------------------------------------------ the kelp run

SUB_ORANGE = ramp('#f07a1a', dark=0.4, light=1.35, warm=0.06)


def spr_mini_sub():
    """A little research submarine seen from behind as it noses on ahead of you through the water: an orange hull,
    its glass dome over the pilot, a ducted propeller at the stern, a thruster either side, its lamps lit forward
    and a red light at its tail."""
    w, h = 48, 36
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(24, 18, 15, 12, z=1.2, dome=0.9, mat=0)                              # the hull, end on
    cv.ellipse(24, 8, 8, 6, z=1.6, dome=0.9, mat=1)                                 # the dome
    cv.ellipse(24, 7, 3.0, 3.2, z=1.9, dome=0.8, mat=4)                             # the pilot's head in it
    for x in (6, 42):                                                               # the side thrusters
        cv.ellipse(x, 22, 5.0, 4.0, z=1.3, dome=0.8, mat=2)
        cv.ellipse(x, 22, 2.6, 2.0, z=1.4, dome=0.3, mat=3)
    cv.ellipse(24, 22, 7.0, 6.6, z=1.6, dome=0.5, mat=2)                            # the propeller's duct
    cv.ellipse(24, 22, 4.6, 4.4, z=1.65, dome=0.2, mat=3)
    for a in (0, 2.1, 4.2):                                                         # the blades
        cv.stroke([(24, 22), (24 + np.cos(a) * 4.2, 22 + np.sin(a) * 4.2)], 1.2, z=1.7, dome=0.4, mat=2)
    cv.box(22.5, 28.5, 3, 2.4, z=1.8, top=0.4, bevel=0.4, mat=5)                    # the tail light
    cv.box(14, 30, 20, 3, z=1.1, top=0.5, bevel=0.8, mat=2)                         # the skids
    rgba, _ = _prop(cv, [SUB_ORANGE, GLASS, CHROME, TRIM, HAIR_D, TAIL], relief=1.0, cavity=0.4, shadow=0.45)
    return rgba, _tail_em(cv, [5])


def spr_light_shaft():
    """A shaft of sunlight slanting down through the water from the surface, brightest at the top and fading as
    it goes down, soft at its edges. Drawn `additive` - set them standing about a sea floor, tall."""
    w, h = 24, 96
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    lean = (yy / h) * 6                                                             # it slants a little
    d = np.abs(xx - 12 + lean - 3) / (5 + yy / h * 4)
    a = np.clip(1 - d, 0, 1) ** 1.5 * (1 - yy / h) ** 1.2
    rgba[..., :3] = [0.75, 0.95, 1.0]
    rgba[..., 3] = a
    return rgba, a * 0.6


def spr_porthole():
    """The rim of your own submarine's viewport, from inside: a thick brass ring round the view, bolted, the
    hull's dark steel at the corners outside it. A shot's `vehicle`, close and big, so the ring frames the view."""
    w, h = 96, 64
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w] + 0.5
    r = np.hypot((xx - 48) / 47, (yy - 32) / 31)
    hull = r > 1.0
    ring = (r > 0.86) & (r <= 1.0)
    rgba[hull, :3] = [0.1, 0.11, 0.13]
    rgba[hull, 3] = 1.0
    ang = np.arctan2(yy - 32, xx - 48)
    lit = 0.6 + 0.4 * np.cos(ang + 2.2)                                             # the light on the ring
    rgba[ring, :3] = np.array([0.66, 0.5, 0.24])[None, :] * lit[ring][:, None]
    rgba[ring, 3] = 1.0
    rgba[ring & (np.abs(r - 0.93) < 0.012)] = [0.36, 0.27, 0.13, 1.0]                # its groove
    for k in range(12):                                                             # its bolts
        a = k * np.pi / 6
        bx, by = 48 + np.cos(a) * 47 * 0.93, 32 + np.sin(a) * 31 * 0.93
        bolt = (xx - bx) ** 2 + (yy - by) ** 2 < 2.2
        rgba[bolt, :3] = [0.9, 0.78, 0.5]
    return rgba, np.zeros((h, w), np.float32)


# ------------------------------------------------------------------ the sled run

HUSKY = ramp('#8a8c94', dark=0.4, light=1.7, cool=0.04)
HUSKY_W = ramp('#ecebe6', dark=0.5, light=1.15)
HARNESS = ramp('#d8302a', dark=0.4, light=1.4)
LOGS = ramp('#7a5434', dark=0.4, light=1.5, warm=0.05)


def spr_dog_team():
    """A team of sled dogs running away from you up the trail: three pairs of huskies in red harness on the
    gangline, each in its own coat - grey, black, brown - white legs, tails curled up, the lead pair farthest and
    smallest. Stand it a few units ahead of the camera for the team you drive."""
    w, h = 48, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(24, 40), (24, 6)], 0.8, z=0.9, dome=0.3, mat=2)                     # the gangline
    for k, (y, s) in enumerate(((10, 0.55), (21, 0.75), (33, 1.0))):               # pairs, far to near
        for side in (-1, 1):
            x = 24 + side * 7.5 * s
            coat = (0, 3, 4, 0, 3, 4)[k * 2 + (side > 0)]                            # each dog its own coat
            for lx in (-2.6, 2.6):                                                  # the legs, running
                cv.stroke([(x + lx * s, y + 2 * s), (x + lx * s * 1.3, y + 7 * s)], 1.4 * s, z=1.0, dome=0.5,
                          mat=1)
            cv.ellipse(x, y, 4.6 * s, 3.6 * s, z=1.3, dome=0.9, mat=coat)           # the back, from behind
            cv.ellipse(x, y - 3.4 * s, 2.4 * s, 2.0 * s, z=1.4, dome=0.9, mat=coat)  # the head beyond
            for e in (-1, 1):
                cv.ellipse(x + e * 1.4 * s, y - 5.0 * s, 0.7 * s, 1.1 * s, z=1.45, dome=0.6, mat=coat)   # ears
            cv.stroke([(x, y - 0.5 * s), (x + side * 1.5 * s, y - 2.6 * s)], 1.6 * s, z=1.5, dome=0.7,
                      mat=1)                                                        # the tail, curled up
            cv.stroke([(x - 3.6 * s, y + 0.4 * s), (x + 3.6 * s, y + 0.4 * s)], 0.9 * s, z=1.45, dome=0.3,
                      mat=2)                                                        # the harness
            cv.stroke([(x, y + 0.4 * s), (24, y + 2.2 * s)], 0.6, z=1.2, dome=0.3, mat=2)   # its tug line
    return _prop(cv, [HUSKY, HUSKY_W, HARNESS, ramp('#2a2a30', dark=0.5, light=2.0),
                      ramp('#9a6a3e', dark=0.4, light=1.5, warm=0.05)], relief=1.0, cavity=0.4, shadow=0.45)


def spr_log_cabin():
    """A log cabin in the snow: walls of round logs with their ends crossing at the corners, a roof deep in snow,
    a stone chimney smoking, its windows lit warm."""
    w, h = 64, 52
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(46, 6, 7, 22, z=1.0, top=0.6, bevel=1.0, mat=3)                          # the chimney
    cv.box(8, 26, 48, 26, z=1.0, top=0.6, bevel=1.2, mat=0)                         # the walls
    for y in range(27, 52, 3):                                                      # the logs, round
        cv.stroke([(6, y + 1), (58, y + 1)], 2.6, z=1.2, dome=0.8, mat=0)
    cv.polygon([(2, 28), (62, 28), (50, 12), (14, 12)], z=1.6, top=0.6, bevel=1.4, mat=1)          # the roof, snowed
    cv.box(28, 36, 9, 16, z=1.3, top=0.5, bevel=0.8, mat=4)                         # the door
    for x0 in (13, 42):
        cv.box(x0, 34, 9, 8, z=1.3, top=0.4, bevel=0.6, mat=5)                      # the windows, lit
    rgba, _ = _prop(cv, [LOGS, ramp('#eef2f6', dark=0.55, light=1.1), ramp('#7a7a80', dark=0.4, light=1.5),
                         ramp('#8a8a90', dark=0.4, light=1.5), ramp('#3a2a1e', dark=0.45, light=1.6),
                         ramp('#ffc870', dark=0.8, light=1.1)], relief=1.0, cavity=0.4, shadow=0.4)
    return rgba, _tail_em(cv, [5])


DEBRIS_SETS = {                       # for a road scene's `scatter`: what lies along a verge
    'verge': ['grass_tuft', 'grass_tuft', 'grass_tuft', 'dry_tuft', 'flowers', 'rocks', 'bush'],
    'alpine': ['rocks', 'rocks', 'rocks', 'boulder', 'grass_tuft', 'grass_tuft', 'flowers'],
    'street': ['trash_bag', 'trash_bag', 'trash', 'trash', 'old_tyre', 'traffic_cone'],
}
DECALS = {'oil_stain': dec_oil_stain, 'tyre_marks': dec_tyre_marks, 'road_patch': dec_road_patch,
          'pothole': dec_pothole, 'leaf_litter': dec_leaf_litter, 'manhole': dec_manhole,
          'lane_arrow': dec_lane_arrow, 'zebra_crossing': dec_zebra_crossing, 'sand_drift': dec_sand_drift,
          'pebbles': dec_pebbles, 'start_line': dec_start_line, 'wake': dec_wake, 'crater': dec_crater}
TEXTURES.update({'tower_windows': lambda n: tex_tower_windows(n), 'tower_windows_b': lambda n: tex_tower_windows(n),
                 'shopfront': lambda n: tex_shopfront(n),
                 'shopfront_b': lambda n: tex_shopfront(n, (0.25, 0.95, 1.0)),
                 'shopfront_c': lambda n: tex_shopfront(n, (1.0, 0.7, 0.2)),
                 'coaster_track': lambda n: tex_coaster_track(n), 'coaster_frame': lambda n: tex_coaster_frame(n),
                 'rail_track': lambda n: tex_rail_track(n), 'grandstand': lambda n: tex_grandstand(n),
                 'suspension_cables': lambda n: tex_suspension_cables(n),
                 'canal_house': lambda n: tex_canal_house(n),
                 'canal_house_b': lambda n: tex_canal_house(n, (0.74, 0.44, 0.4)),
                 'canal_house_c': lambda n: tex_canal_house(n, (0.84, 0.78, 0.64)),
                 'canal_footing': lambda n: tex_canal_footing(n), 'piste': lambda n: tex_piste(n),
                 'ski_fence': lambda n: tex_ski_fence(n), 'chairlift': lambda n: tex_chairlift(n),
                 'city_night': lambda n: tex_city_night(n), 'light_lane': lambda n: tex_light_lane(n),
                 'tulip_field': lambda n: tex_tulip_field(n),
                 'tulip_field_b': lambda n: tex_tulip_field(n, (0.96, 0.8, 0.12)),
                 'tulip_field_c': lambda n: tex_tulip_field(n, (0.96, 0.46, 0.7)),
                 'tulip_field_d': lambda n: tex_tulip_field(n, (0.56, 0.24, 0.7)),
                 'peppermint': lambda n: tex_peppermint(n), 'frosting': lambda n: tex_frosting(n),
                 'wheat_field': lambda n: tex_wheat_field(n)})
TEXTURE_NOISE.update({'tower_windows': 0.4, 'tower_windows_b': 0.4, 'shopfront': 0.4, 'shopfront_b': 0.4,
                      'shopfront_c': 0.4, 'coaster_track': 0.2, 'coaster_frame': 0.2, 'rail_track': 0.6,
                      'grandstand': 0.3, 'suspension_cables': 0.0, 'canal_house': 0.3, 'canal_house_b': 0.3,
                      'canal_house_c': 0.3, 'canal_footing': 0.4, 'piste': 0.15, 'ski_fence': 0.0, 'chairlift': 0.0,
                      'city_night': 0.0, 'light_lane': 0.0, 'tulip_field': 0.2, 'tulip_field_b': 0.2,
                      'tulip_field_c': 0.2, 'tulip_field_d': 0.2, 'peppermint': 0.1, 'frosting': 0.2,
                      'wheat_field': 0.3})
VARIANTS = {'traffic_light': (3, _traffic_light), 'car_compact': (4, _car_compact), 'car_sedan': (4, _car_sedan),
            'billboard': (3, _billboard), 'race_car': (4, _race_car), 'car_oncoming': (4, _car_oncoming),
            'mooring_pole': (3, _mooring_pole), 'slalom_gate': (2, _slalom_gate), 'gumdrop': (4, _gumdrop)}

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
           'starfighter': spr_starfighter, 'race_car': spr_race_car, 'car_oncoming': spr_car_oncoming,
           'motel_sign': spr_motel_sign, 'gas_station': spr_gas_station, 'bridge_tower': spr_bridge_tower,
           'dark_castle': spr_dark_castle, 'mooring_pole': spr_mooring_pole, 'canal_bridge': spr_canal_bridge,
           'gondola': spr_gondola, 'washing_line': spr_washing_line, 'slalom_gate': spr_slalom_gate,
           'skier': spr_skier, 'ski_tips': spr_ski_tips, 'lift_tower': spr_lift_tower, 'moon_buggy': spr_moon_buggy,
           'loco_boiler': spr_loco_boiler, 'telegraph_pole': spr_telegraph_pole, 'windmill': spr_windmill,
           'cyclist': spr_cyclist, 'bike_bars': spr_bike_bars, 'runway_light': spr_runway_light,
           'control_tower': spr_control_tower, 'airliner': spr_airliner, 'cockpit': spr_cockpit,
           'stilt_shack': spr_stilt_shack, 'camel': spr_camel, 'camel_head': spr_camel_head, 'pyramid': spr_pyramid,
           'candy_cane': spr_candy_cane, 'lollipop': spr_lollipop, 'gumdrop': spr_gumdrop,
           'gingerbread_house': spr_gingerbread_house, 'skeleton': spr_skeleton, 'ghost_car': spr_ghost_car,
           'cherry_tree': spr_cherry_tree, 'torii': spr_torii, 'snow_peak': spr_snow_peak, 'tornado': spr_tornado,
           'barn': spr_barn, 'pickup_truck': spr_pickup_truck, 'mini_sub': spr_mini_sub,
           'light_shaft': spr_light_shaft, 'porthole': spr_porthole, 'dog_team': spr_dog_team,
           'log_cabin': spr_log_cabin}
SPRITE_HEIGHT = {'sports_car': 0.42, 'car_compact': 0.44, 'car_sedan': 0.48, 'box_truck': 1.05, 'curve_sign': 0.95,
                 'billboard': 2.6, 'checkpoint': 2.6, 'traffic_cone': 0.24, 'tunnel_ring': 3.6,
                 'tunnel_portal': 5.775, 'trash_bag': 0.16, 'old_tyre': 0.22, 'trash': 0.05,
                 'reflector_post': 0.34, 'highway_lamp': 3.6, 'sign_gantry': 3.2, 'speed_sign': 0.95,
                 'traffic_light': 1.5, 'tyre_stack': 0.32, 'road_barrier': 0.36, 'start_lights': 3.0,
                 'jeep': 0.62, 'rally_car': 0.48, 'dirt_bike': 0.55, 'dust_cloud': 0.62, 'speedboat': 0.44,
                 'narrowboat': 0.9, 'boat_bow': 0.42, 'hover_car': 0.36, 'neon_bike': 0.52, 'taxi': 0.5, 'brick_ring': 3.25, 'coaster_car': 0.55,
                 'mine_frame': 2.2, 'mine_cart': 0.38, 'starfighter': 0.4, 'race_car': 0.3, 'car_oncoming': 0.48,
                 'motel_sign': 4.2, 'gas_station': 2.6, 'bridge_tower': 10.0, 'dark_castle': 30.0,
                 'mooring_pole': 1.3, 'canal_bridge': 1.45, 'gondola': 0.85, 'washing_line': 0.6,
                 'slalom_gate': 0.62, 'skier': 0.5, 'ski_tips': 0.4, 'lift_tower': 3.0, 'moon_buggy': 0.55,
                 'loco_boiler': 0.6, 'telegraph_pole': 2.9, 'windmill': 4.0, 'cyclist': 0.6, 'bike_bars': 0.3,
                 'runway_light': 0.08, 'control_tower': 8.0, 'airliner': 2.6, 'cockpit': 0.84,
                 'stilt_shack': 2.2, 'camel': 0.8, 'camel_head': 0.5, 'pyramid': 20.0,
                 'candy_cane': 1.8, 'lollipop': 2.4, 'gumdrop': 0.8, 'gingerbread_house': 2.0, 'skeleton': 0.75,
                 'ghost_car': 0.4, 'cherry_tree': 3.2, 'torii': 3.6, 'snow_peak': 18.0,
                 'tornado': 30.0, 'barn': 2.4, 'pickup_truck': 0.62, 'mini_sub': 0.5, 'light_shaft': 8.0,
                 'porthole': 1.0, 'dog_team': 0.4, 'log_cabin': 1.8}
PROP_DEFAULTS = {'checkpoint': {'shadow': False}, 'billboard': {'shadow': False}, 'tunnel_ring': {'shadow': False},
                 'tunnel_portal': {'shadow': False}, 'sign_gantry': {'shadow': False},
                 'start_lights': {'shadow': False}, 'dust_cloud': {'shadow': False, 'opacity': 0.75},
                 'speedboat': {'shadow': False}, 'narrowboat': {'shadow': False}, 'boat_bow': {'shadow': False},
                 'brick_ring': {'shadow': False}, 'mine_frame': {'shadow': False}, 'starfighter': {'shadow': False},
                 'motel_sign': {'shadow': False}, 'gas_station': {'shadow': False}, 'bridge_tower': {'shadow': False},
                 'dark_castle': {'shadow': False}, 'canal_bridge': {'shadow': False}, 'gondola': {'shadow': False},
                 'mooring_pole': {'shadow': False}, 'washing_line': {'shadow': False, 'planes': 1},
                 'ski_tips': {'shadow': False}, 'lift_tower': {'shadow': False}, 'moon_buggy': {'shadow': False},
                 'loco_boiler': {'shadow': False}, 'windmill': {'shadow': False}, 'bike_bars': {'shadow': False},
                 'runway_light': {'shadow': False, 'fullbright': True}, 'control_tower': {'shadow': False},
                 'airliner': {'shadow': False}, 'cockpit': {'shadow': False}, 'stilt_shack': {'shadow': False},
                 'camel_head': {'shadow': False}, 'pyramid': {'shadow': False},
                 'gingerbread_house': {'shadow': False}, 'ghost_car': {'shadow': False},
                 'torii': {'shadow': False}, 'snow_peak': {'shadow': False}, 'tornado': {'shadow': False},
                 'barn': {'shadow': False}, 'mini_sub': {'shadow': False},
                 'light_shaft': {'shadow': False, 'blend': 'additive'}, 'porthole': {'shadow': False},
                 'dog_team': {'shadow': False}, 'log_cabin': {'shadow': False}}

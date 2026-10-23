"""The highway: what a road scene (road.py) needs that nothing else drew - cars seen from behind, as you follow them
down a road (a red convertible with two in it for your own, a compact, a sedan, a box truck), their tail lights
glowing; a chevron sign before a bend, a billboard on its legs, a checkpoint banner over the road on two poles, a
traffic cone; a road tunnel's rings and its portal. Drawn with the pixel-art toolkit (scripts/pixelart.py).
"""
import numpy as np
from PIL import Image, ImageDraw

from biomes import _prop
from pixelart import Canvas, ramp

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
    return _prop(cv, [RED, TAIL, PLATE, TYRE, TRIM, HAIR_D, HAIR_B, CHROME], em=_tail_em(cv, [1]),
                 relief=1.0, cavity=0.45, shadow=0.45)


def spr_car_compact():
    """A small rounded car seen from behind, in blue: its roof and rear window, round tail lights, a chrome
    bumper."""
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
    return _prop(cv, [BLUE, TAIL, PLATE, TYRE, GLASS, CHROME], em=_tail_em(cv, [1]),
                 relief=1.0, cavity=0.45, shadow=0.45)


def spr_car_sedan():
    """A boxy sedan seen from behind, pale: a roof over a raked rear window, a trunk lid, wide tail lights."""
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
    return _prop(cv, [WHITE, TAIL, PLATE, TYRE, GLASS, TRIM], em=_tail_em(cv, [1]),
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
    """A billboard on two legs: a sunset over the sea and a palm in flat bands of colour, a frame round it, a
    catwalk under it."""
    w, h = 72, 52
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    board = (xx >= 2) & (xx < 70) & (yy >= 2) & (yy < 34)
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


SPRITES = {'sports_car': spr_sports_car, 'car_compact': spr_car_compact, 'car_sedan': spr_car_sedan,
           'box_truck': spr_box_truck, 'curve_sign': spr_curve_sign, 'billboard': spr_billboard,
           'checkpoint': spr_checkpoint, 'traffic_cone': spr_traffic_cone, 'tunnel_ring': spr_tunnel_ring,
           'tunnel_portal': spr_tunnel_portal}
SPRITE_HEIGHT = {'sports_car': 0.42, 'car_compact': 0.44, 'car_sedan': 0.48, 'box_truck': 1.05, 'curve_sign': 0.95,
                 'billboard': 2.6, 'checkpoint': 2.6, 'traffic_cone': 0.24, 'tunnel_ring': 3.6,
                 'tunnel_portal': 5.775}
PROP_DEFAULTS = {'checkpoint': {'shadow': False}, 'billboard': {'shadow': False}, 'tunnel_ring': {'shadow': False},
                 'tunnel_portal': {'shadow': False}}

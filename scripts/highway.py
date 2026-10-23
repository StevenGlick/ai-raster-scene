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

DEBRIS_SETS = {                       # for a road scene's `scatter`: what lies along a verge
    'verge': ['grass_tuft', 'grass_tuft', 'grass_tuft', 'dry_tuft', 'flowers', 'rocks', 'bush'],
    'alpine': ['rocks', 'rocks', 'rocks', 'boulder', 'grass_tuft', 'grass_tuft', 'flowers'],
    'street': ['trash_bag', 'trash_bag', 'trash', 'trash', 'old_tyre', 'traffic_cone'],
}
DECALS = {'oil_stain': dec_oil_stain, 'tyre_marks': dec_tyre_marks, 'road_patch': dec_road_patch,
          'pothole': dec_pothole, 'leaf_litter': dec_leaf_litter, 'manhole': dec_manhole,
          'lane_arrow': dec_lane_arrow, 'zebra_crossing': dec_zebra_crossing, 'sand_drift': dec_sand_drift,
          'pebbles': dec_pebbles, 'start_line': dec_start_line}
VARIANTS = {'traffic_light': (3, _traffic_light)}

SPRITES = {'sports_car': spr_sports_car, 'car_compact': spr_car_compact, 'car_sedan': spr_car_sedan,
           'box_truck': spr_box_truck, 'curve_sign': spr_curve_sign, 'billboard': spr_billboard,
           'checkpoint': spr_checkpoint, 'traffic_cone': spr_traffic_cone, 'tunnel_ring': spr_tunnel_ring,
           'tunnel_portal': spr_tunnel_portal, 'trash_bag': spr_trash_bag, 'old_tyre': spr_old_tyre,
           'trash': spr_trash, 'reflector_post': spr_reflector_post, 'highway_lamp': spr_highway_lamp,
           'sign_gantry': spr_sign_gantry, 'speed_sign': spr_speed_sign, 'traffic_light': spr_traffic_light,
           'tyre_stack': spr_tyre_stack, 'road_barrier': spr_road_barrier, 'start_lights': spr_start_lights}
SPRITE_HEIGHT = {'sports_car': 0.42, 'car_compact': 0.44, 'car_sedan': 0.48, 'box_truck': 1.05, 'curve_sign': 0.95,
                 'billboard': 2.6, 'checkpoint': 2.6, 'traffic_cone': 0.24, 'tunnel_ring': 3.6,
                 'tunnel_portal': 5.775, 'trash_bag': 0.16, 'old_tyre': 0.22, 'trash': 0.05,
                 'reflector_post': 0.34, 'highway_lamp': 3.6, 'sign_gantry': 3.2, 'speed_sign': 0.95,
                 'traffic_light': 1.5, 'tyre_stack': 0.32, 'road_barrier': 0.36, 'start_lights': 3.0}
PROP_DEFAULTS = {'checkpoint': {'shadow': False}, 'billboard': {'shadow': False}, 'tunnel_ring': {'shadow': False},
                 'tunnel_portal': {'shadow': False}, 'sign_gantry': {'shadow': False},
                 'start_lights': {'shadow': False}}

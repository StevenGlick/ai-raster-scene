"""The first-person held items, drawn with the pixel-art toolkit: a hand that is a hand - four fingers
wrapped round the handle, each its own rounded segment, light on the knuckles, a thumb laid over -
coming out of a shaded coat sleeve with a shirt cuff, round the item. Same canvases and anchors as the flat versions in icons.py.
"""
import math

import numpy as np

from pixelart import Canvas, outline_sprite, ramp

COAT = ramp('#2a2a32', dark=0.5, light=1.4, cool=0.1)
CUFF = ramp('#8a8070', dark=0.4, light=1.45)
SKIN = ramp('#c88a62', dark=0.42, light=1.32, warm=0.12)
METAL = ramp('#7e848c', dark=0.38, light=1.6, cool=0.1)
GUNMETAL = ramp('#4a4e56', dark=0.42, light=1.65, cool=0.1)
IRON = ramp('#46464e', dark=0.45, light=1.7, cool=0.08)
WOOD = ramp('#7a5030', dark=0.38, light=1.45, warm=0.12)
REDBAR = ramp('#a8302a', dark=0.36, light=1.45)
CLOTH = ramp('#4a3a2a', dark=0.4, light=1.4)
GLASS = ramp('#ffc860', dark=0.75, light=1.25, warm=0.1)
LENS = ramp('#fff0c0', dark=0.8, light=1.15)
LIGHT = dict(sun=(-0.3, -0.85, 0.65), relief=1.15, cavity=0.45, shadow=0.4)


def _fist(cv, cx, cy, span, reach, along, mat, right=True, thumb=None, z=1.2):
    """A hand closed round a handle that runs `along` (degrees, toward the business end): the back of
    the hand behind, on the knuckle side, and four fingers wrapped across the handle in front of it -
    each its own rounded segment, the index longest - `span` long down the handle and `reach` across it;
    a right hand's knuckles are on the right of the handle. `thumb` (x, y, length, width, angle) lays a
    thumb over the top."""
    a = math.radians(along)
    ux, uy = math.cos(a), math.sin(a)                      # down the handle, toward its business end
    vx, vy = -uy, ux                                        # across it
    side = 1 if right else -1                               # where the knuckles are
    bx, by = cx + vx * side * reach * 0.3 - ux * span * 0.1, cy + vy * side * reach * 0.3 - uy * span * 0.1
    cv.ellipse(bx, by, span * 0.62, reach * 0.55, z=z, dome=1.3, angle=along, mat=mat, tone=-0.05)   # the hand
    n = 4
    pitch = span / n
    for k in range(n):                                       # index (k = 0) nearest the business end
        t = (n - 1) / 2 - k
        px, py = cx + ux * t * pitch, cy + uy * t * pitch
        tip = reach * (0.5 - 0.06 * k)                       # each finger a little shorter than the last
        knuckle = (px + vx * side * reach * 0.5, py + vy * side * reach * 0.5)
        end = (px - vx * side * tip, py - vy * side * tip)
        cv.stroke([knuckle, end], pitch * 0.98, z=z + 0.5, dome=1.0, taper=(1.0, 0.85), mat=mat)
        cv.ellipse(knuckle[0], knuckle[1], pitch * 0.55, pitch * 0.5, z=0, dome=0.35, mode='add')   # its knuckle
    if thumb:
        tx, ty, length, width, ta = thumb
        cv.stroke([(tx - math.cos(math.radians(ta)) * length / 2, ty - math.sin(math.radians(ta)) * length / 2),
                   (tx + math.cos(math.radians(ta)) * length / 2, ty + math.sin(math.radians(ta)) * length / 2)],
                  width, z=z + 1.1, dome=1.0, taper=(1.0, 0.8), mat=mat, tone=0.04)


def _sleeve(cv, pts, cuff):
    """The coat sleeve the hand comes out of, and the cuff of the shirt under it at the wrist."""
    cv.polygon(pts, z=0.3, top=1.3, bevel=3.0, mat=0)
    cv.polygon(cuff, z=0.9, top=0.8, bevel=1.2, mat=1)


def _finish(cv, ramps, glow_mats=(), glow=1.0):
    rgba = cv.paint(ramps, cv.light(**LIGHT), dither=0.2)
    rgba = outline_sprite(rgba, darken=0.5)
    em = np.zeros(rgba.shape[:2], np.float32)
    for m in glow_mats:
        sel = (cv.mat == m) & (cv.id > 0)
        em[sel] = glow
    return rgba.astype(np.float32), em


def vm_revolver(fire=False):
    """A revolver held up in the right hand: the cylinder and its chambers, the barrel running up to the
    muzzle, the wooden grip in a fist with the thumb along the frame, the coat sleeve and cuff."""
    cv = Canvas(84, 78, wrap=False, ground=-9)
    _sleeve(cv, [(52, 78), (84, 78), (84, 46), (64, 40)], [(55, 66), (64, 50), (70, 54), (61, 71)])
    cv.polygon([(38, 50), (52, 47), (50, 35), (41, 36)], z=0.9, top=1.0, bevel=1.5, mat=3)          # the grip
    _fist(cv, 47.0, 63.0, 24.0, 24.0, -98, 4, right=True, thumb=(39.0, 50.0, 13.0, 5.0, -78))
    cv.box(37, 27, 16, 11, z=1.0, top=0.9, bevel=1.5, mat=2)                                        # the frame
    cv.ellipse(45.0, 26.0, 8.4, 8.0, z=1.8, dome=1.2, mat=2)                                        # the cylinder
    for k in range(6):                                                                              # its chambers
        a = math.radians(-90 + 60 * k)
        cv.ellipse(45.0 + math.cos(a) * 4.6, 26.0 + math.sin(a) * 4.4, 1.5, 1.4, z=0, dome=0.8, mode='carve')
    cv.stroke([(45.0, 21.0), (45.0, 4.5)], 7.0, z=1.6, dome=1.1, taper=(1.0, 0.85), mat=2)          # the barrel
    cv.stroke([(45.0, 20.0), (45.0, 5.0)], 1.0, z=2.2, dome=0.3, mat=2, tone=0.15)                  # its top rib
    cv.ellipse(45.0, 4.0, 4.0, 3.0, z=2.0, dome=0.8, mat=5)                                         # the muzzle
    cv.ellipse(45.0, 3.8, 2.0, 1.5, z=1.6, dome=0.0, mat=5, tone=-0.6)                              # the bore
    return _finish(cv, [COAT, CUFF, GUNMETAL, WOOD, SKIN, IRON])


def vm_lantern(fire=False):
    """An oil lantern held up in the left hand by the ring under its base: the glass lit from inside,
    its iron frame and cap, the hand closed round the ring, the coat sleeve and cuff."""
    cv = Canvas(60, 96, wrap=False, ground=-9)
    _sleeve(cv, [(0, 96), (24, 96), (30, 72), (10, 62), (0, 66)], [(6, 70), (26, 66), (28, 73), (9, 77)])
    cv.stroke([(23, 42), (23, 57)], 2.2, z=1.0, dome=0.6, mat=2)                                    # the stem
    cv.ellipse(23, 44, 9, 2.2, z=1.2, dome=0.6, mat=2)                                              # the ring
    _fist(cv, 23.0, 64.0, 17.0, 23.0, -90, 4, right=False, thumb=(31.0, 57.0, 10.0, 4.4, -20))
    cv.polygon([(11, 15), (35, 15), (30, 8), (16, 8)], z=1.4, top=1.0, bevel=1.5, mat=2)            # the cap
    cv.box(21, 3, 4, 5, z=1.6, top=0.6, bevel=0.8, mat=2)                                           # its knob
    cv.box(13, 15, 20, 22, z=0.6, top=0.6, bevel=0.5, mat=5)                                        # the glass
    for x in (13.5, 23.0, 32.5):                                                                    # the frame
        cv.stroke([(x, 15), (x, 37)], 1.6, z=1.4, dome=0.6, mat=2)
    cv.box(11, 37, 24, 5, z=1.4, top=1.0, bevel=1.2, mat=2)                                         # the base
    rgba, em = _finish(cv, [COAT, CUFF, IRON, IRON, SKIN, GLASS], glow_mats=(5,))
    yy, xx = np.mgrid[0:96, 0:60].astype(np.float32)
    flame = (((xx - 23) / 3.2) ** 2 + ((yy - 27) / 6.5) ** 2) < 1                                   # the flame
    rgba[flame, :3] = (1.0, 0.97, 0.78)
    em[flame] = 1.0
    return rgba, em


def vm_flashlight(fire=False):
    """A torch (an electric one) in the right fist: the ribbed barrel, the flared head, the lit lens,
    the coat sleeve and cuff."""
    cv = Canvas(70, 80, wrap=False, ground=-9)
    _sleeve(cv, [(40, 80), (70, 80), (70, 50), (52, 46)], [(44, 70), (55, 57), (61, 62), (50, 74)])
    cv.stroke([(41, 80), (37.5, 45)], 12.0, z=1.0, dome=1.4, mat=2)                                 # the barrel
    for y in range(50, 79, 3):                                                                      # its ribs
        cv.stroke([(32, y), (46, y - 0.4)], 0.7, z=0, dome=0.3, mode='carve')
    cv.polygon([(27, 34), (46, 34), (43.5, 47), (30, 47)], z=1.6, top=1.2, bevel=1.5, mat=3)        # the head
    cv.ellipse(36.5, 33.0, 10.5, 7.0, z=2.0, dome=0.6, mat=3)                                       # its rim
    cv.ellipse(36.5, 33.0, 7.5, 4.8, z=2.2, dome=0.4, mat=5)                                        # the lens
    _fist(cv, 42.5, 67.0, 22.0, 24.0, -96, 4, right=True, thumb=(41.0, 57.5, 12.0, 4.6, -12))
    return _finish(cv, [COAT, CUFF, IRON, METAL, SKIN, LENS], glow_mats=(5,))


def vm_axe(fire=False):
    """A felling axe held at the end of its haft in the right fist: the steel head with a bright edge,
    the iron socket, the coat sleeve and cuff."""
    cv = Canvas(90, 96, wrap=False, ground=-9)
    _sleeve(cv, [(60, 96), (90, 96), (90, 64), (70, 60)], [(62, 86), (70, 70), (78, 74), (70, 90)])
    cv.stroke([(64, 94), (34, 18)], 6.0, z=1.0, dome=1.0, mat=3)                                    # the haft
    cv.stroke([(62, 90), (35, 22)], 1.2, z=1.6, dome=0.3, mat=3, tone=0.15)                         # its grain
    cv.polygon([(28, 10), (14, 2), (5, 22), (18, 30), (36, 26)], z=1.2, top=1.0, bevel=2.0, mat=2)  # the head
    cv.stroke([(14, 3), (5.5, 21)], 1.6, z=2.0, dome=0.3, mat=2, tone=0.3)                          # the edge
    cv.box(29, 12, 11, 14, z=1.6, top=1.0, bevel=1.5, mat=5)                                        # the socket
    _fist(cv, 59.0, 80.0, 24.0, 23.0, -112, 4, right=True, thumb=(52.0, 69.0, 11.0, 4.6, -40))
    return _finish(cv, [COAT, CUFF, METAL, WOOD, SKIN, IRON])


def vm_crowbar(fire=False):
    """A crowbar in the right fist, its hooked claw up and out: red paint worn to steel at the edges,
    the coat sleeve and cuff."""
    cv = Canvas(80, 92, wrap=False, ground=-9)
    _sleeve(cv, [(52, 92), (80, 92), (80, 62), (62, 58)], [(52, 82), (61, 66), (69, 70), (61, 86)])
    cv.stroke([(57, 91), (30, 14)], 5.0, z=1.0, dome=0.7, mat=2)                                    # the bar
    cv.stroke([(30, 14), (26, 6), (16, 6), (14, 12)], 4.6, z=1.0, dome=0.7, mat=2)                  # the claw
    cv.stroke([(15.0, 11.5), (13.5, 13.5)], 3.0, z=1.0, dome=0.6, mat=5)                            # its worn tip
    _fist(cv, 53.0, 77.0, 24.0, 22.0, -110, 4, right=True, thumb=(46.0, 66.5, 11.0, 4.4, -38))
    return _finish(cv, [COAT, CUFF, REDBAR, WOOD, SKIN, METAL])


def vm_torch(fire=False):
    """A burning torch held up in the left fist: a wooden haft, a head of pitch-soaked rags, the flame
    in tongues of orange, yellow and white (it glows), the coat sleeve and cuff."""
    cv = Canvas(56, 96, wrap=False, ground=-9)
    _sleeve(cv, [(0, 96), (26, 96), (32, 74), (10, 64), (0, 68)], [(6, 72), (27, 69), (29, 76), (8, 80)])
    cv.stroke([(22, 72), (28, 22)], 6.0, z=1.0, dome=1.0, mat=3)                                    # the haft
    cv.stroke([(23, 68), (28, 26)], 1.2, z=1.6, dome=0.3, mat=3, tone=0.12)
    cv.polygon([(19, 28), (36, 28), (35, 17), (21, 17)], z=1.6, top=1.2, bevel=1.5, mat=5)          # the rags
    for y in (20, 23.5, 27):
        cv.stroke([(20, y), (36, y - 1.2)], 0.8, z=0, dome=0.4, mode='carve')
    _fist(cv, 23.5, 69.0, 18.0, 23.0, -83, 4, right=False, thumb=(31.0, 61.5, 10.0, 4.4, -25))
    rgba, em = _finish(cv, [COAT, CUFF, IRON, WOOD, SKIN, CLOTH])
    yy, xx = np.mgrid[0:96, 0:56].astype(np.float32) + 0.5
    for (cx, cy, rx, ry, c) in ((28.5, 11.0, 9.5, 12.0, (1.0, 0.54, 0.12)), (29.0, 13.0, 6.0, 8.5, (1.0, 0.8, 0.3)),
                                (29.0, 15.0, 3.2, 5.0, (1.0, 0.97, 0.8))):
        th = np.arctan2(yy - cy, xx - cx)
        wob = 1 + 0.18 * np.sin(th * 5 + cx) * (yy < cy)
        m = (((xx - cx) / rx) ** 2 + ((yy - cy) / (ry * wob)) ** 2) < 1
        m &= ~((yy > cy + ry * 0.55))                                                             # flat at the rags
        rgba[m, :3] = c
        rgba[m, 3] = 1.0
        em[m] = 1.0
    return rgba, em


HELD = {'revolver': vm_revolver, 'lantern': vm_lantern, 'flashlight': vm_flashlight, 'axe': vm_axe,
        'crowbar': vm_crowbar, 'torch': vm_torch}

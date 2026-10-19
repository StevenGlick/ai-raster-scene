"""The haunted house, drawn with the pixel-art toolkit (scripts/pixelart.py): cobwebs for the
corners, a standing candelabra, a family portrait whose eyes are not quite still, a grandfather
clock, a balustrade for a landing, and the bats that live in the roof.

As in the other toolkit modules, every shape is stamped into a height field, lit from the upper
left and snapped onto hue-shifted ramps.
"""
import numpy as np

from biomes import _prop
from dream import _lathe
from pixelart import Canvas, ramp

BRASS = ramp('#b08a3a', dark=0.35, light=1.3, warm=0.1)
WAX = ramp('#e8dcc0', dark=0.5, light=1.06)
FLAME = ramp('#ffc850', dark=0.7, light=1.1)
GILT = ramp('#b8923e', dark=0.35, light=1.3, warm=0.08)
CANVAS_DARK = ramp('#2e2620', dark=0.5, light=1.6)
SKIN = ramp('#c8b49a', dark=0.4, light=1.15)
COAT = ramp('#1e1c22', dark=0.5, light=1.8)
MAHOGANY = ramp('#5a2e1e', dark=0.3, light=1.35)
DIAL = ramp('#e2d8c0', dark=0.5, light=1.06)
BAT = ramp('#1a1618', dark=0.6, light=1.8)


def spr_cobweb():
    """A cobweb strung across a corner: threads radiating from the corner at the top left, rings of
    spiral between them sagging a little, a broken strand hanging down. Stand it across a corner
    as a card (`planes` 1, `angle` 45 or 135) with `z` near the ceiling."""
    rng = np.random.default_rng(221)
    w, h = 64, 64
    rgba = np.zeros((h, w, 4), np.float32)
    silk = np.array((0.86, 0.86, 0.84), np.float32)

    def line(x0, y0, x1, y1, a):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 1.5) + 1
        for t in np.linspace(0, 1, n):
            x, y = int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))
            if 0 <= x < w and 0 <= y < h:
                rgba[y, x, :3] = silk
                rgba[y, x, 3] = max(rgba[y, x, 3], a)
    angles = np.radians(np.linspace(2, 88, 8) + rng.normal(0, 3, 8))
    R = 62
    for a in angles:                                                 # the radial threads
        line(0, 0, np.cos(a) * R, np.sin(a) * R, 0.75)
    for r in np.arange(8, R, 6.5):                                   # the spiral, sagging between threads
        for a0, a1 in zip(angles[:-1], angles[1:]):
            if rng.random() < 0.12:                                  # a gap where it has broken
                continue
            x0, y0 = np.cos(a0) * r, np.sin(a0) * r
            x1, y1 = np.cos(a1) * r, np.sin(a1) * r
            mx, my = (x0 + x1) / 2 + 0.8, (y0 + y1) / 2 + 1.2
            line(x0, y0, mx, my, 0.55)
            line(mx, my, x1, y1, 0.55)
    line(30, 24, 33, 52, 0.5)                                        # a broken strand hanging down
    return rgba, np.zeros((h, w), np.float32)


def spr_candelabra():
    """A tall standing candelabra in tarnished brass: a turned stem on a tripod foot, five arms
    curving up to their cups, a candle burning in each, wax run down their sides."""
    w, h = 40, 72
    cx = 20
    cv = Canvas(w, h, wrap=False, ground=-9)
    for dx in (-9, 9):                                                # the tripod foot
        cv.stroke([(cx, h - 8), (cx + dx * 0.6, h - 3), (cx + dx, h)], 2.0, z=0.2, dome=0.8, taper=(1, 0.6), mat=0)
    _lathe(cv, cx, [(22, 1.6), (30, 2.4), (34, 1.6), (44, 2.2), (52, 1.6), (60, 2.6), (h - 6, 3.4), (h - 3, 2.0)],
           z=0.4, dome=1.2, mat=0)                                   # the turned stem
    arms = [(-15, 14), (-8, 10), (0, 7), (8, 10), (15, 14)]
    for dx, top in arms:
        if dx:
            t = np.linspace(0, 1, 10)
            pts = list(zip(cx + dx * t, 24 - (24 - top - 4) * t ** 0.5 + 6 * t * (1 - t)))
            cv.stroke(pts, 1.5, z=0.6, dome=0.7, mat=0)
        cv.ellipse(cx + dx, top + 4, 3.0, 1.4, z=1.0, dome=0.6, mat=0)      # the cup
        cv.box(cx + dx - 1.4, top - 4, 2.8, 8, z=1.2, top=0.8, bevel=0.8, mat=1)   # the candle
        cv.stroke([(cx + dx + 1.2, top - 3), (cx + dx + 1.4, top + 1)], 0.8, z=1.6, dome=0.3, mat=1, tone=0.05)
        cv.ellipse(cx + dx, top - 6.5, 1.3, 2.4, z=1.6, dome=0.4, mat=2)    # the flame
    em = (cv.mat == 2) & (cv.id > 0)
    return _prop(cv, [BRASS, WAX, FLAME], relief=1.0, cavity=0.35, shadow=0.4, em=em * 1.0)


def spr_portrait():
    """A family portrait in an oval gilt frame: a pale, unsmiling face over a black coat and a
    white collar against a brown-black ground. The eyes catch a little light that is not there.
    Hang it a little off a wall with `z`."""
    w, h = 40, 52
    cx = 20
    cv = Canvas(w, h, wrap=False, ground=-9)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    d = np.hypot((xx - cx) / 18.5, (yy - 26) / 24.5)
    frame = (d < 1.0) & (d > 0.8)
    inside = d <= 0.8
    cv.z[frame] = (1.2 - np.abs(d[frame] - 0.9) * 8).astype(np.float32)
    cv.mat[frame] = 0
    cv.id[frame] = 1
    for k in range(18):                                               # the frame's carved beads
        a = k * 2 * np.pi / 18
        cv.ellipse(cx + np.cos(a) * 16.6, 26 + np.sin(a) * 22.1, 1.3, 1.3, z=1.4, dome=0.6, mat=0)
    cv.z[inside] = -0.4
    cv.mat[inside] = 1
    cv.id[inside] = 2
    cv.n = 2
    cv.polygon([(cx - 11, 46), (cx - 9, 34), (cx - 3, 31), (cx + 3, 31), (cx + 9, 34), (cx + 11, 46)], z=-0.2,
               top=0.6, bevel=2.0, mat=3)                                # the coat
    cv.polygon([(cx - 3, 31), (cx + 3, 31), (cx + 1.5, 36), (cx - 1.5, 36)], z=0.2, top=0.3, bevel=0.6, mat=2)   # collar
    cv.ellipse(cx, 22, 5.6, 7.4, z=0.0, dome=0.9, mat=2)                # the face
    cv.ellipse(cx, 15.5, 6.2, 3.4, z=0.2, dome=0.8, mat=3)              # dark hair
    for ex in (cx - 2.3, cx + 2.3):
        cv.ellipse(ex, 21.5, 0.9, 0.7, z=0.6, dome=0.2, mat=4)          # the eyes
    cv.stroke([(cx - 2, 26.5), (cx + 2, 26.5)], 0.6, z=0.6, dome=0.1, mat=3)   # a thin mouth
    em = ((cv.mat == 4) & (cv.id > 0)) * 0.55
    return _prop(cv, [GILT, CANVAS_DARK, SKIN, COAT, ramp('#e8d8b0', dark=0.6, light=1.1)], relief=1.0, cavity=0.35,
                 shadow=0.4, em=em)


def spr_grandfather_clock():
    """A grandfather clock in mahogany: a hood with a broken pediment and a brass finial over the
    painted dial (its hands near midnight), a long trunk with a glass door on the brass pendulum,
    and a plinth."""
    w, h = 28, 96
    cx = 14
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(3, h - 14, 22, 14, z=0.0, top=1.0, bevel=1.5, mat=0)                    # the plinth
    cv.box(5, 30, 18, h - 44, z=0.0, top=1.0, bevel=1.5, mat=0, tone=-0.03)         # the trunk
    cv.box(8, 36, 12, 34, z=0.8, top=0.3, bevel=1.0, mat=3)                         # its glass door
    cv.stroke([(cx, 37), (cx, 62)], 0.7, z=1.0, dome=0.3, mat=1)                    # the pendulum rod
    cv.ellipse(cx, 63, 3.2, 3.2, z=1.2, dome=0.8, mat=1)                            # its bob
    cv.box(3, 8, 22, 24, z=0.2, top=1.0, bevel=1.5, mat=0, tone=0.03)               # the hood
    cv.ellipse(cx, 19, 8.0, 8.0, z=0.8, dome=0.3, mat=2)                            # the dial
    for k in range(12):
        a = k * np.pi / 6
        cv.ellipse(cx + np.cos(a) * 6.4, 19 + np.sin(a) * 6.4, 0.5, 0.5, z=1.2, dome=0.1, mat=4)
    cv.stroke([(cx, 19), (cx - 0.4, 13.2)], 0.8, z=1.3, dome=0.1, mat=4)            # the hands, near midnight
    cv.stroke([(cx, 19), (cx - 1.2, 15.0)], 1.0, z=1.3, dome=0.1, mat=4)
    for side in (-1, 1):                                                             # the broken pediment
        cv.polygon([(cx + side * 11, 8), (cx + side * 3, 2), (cx + side * 3, 5), (cx + side * 9, 9)], z=0.6, top=0.6,
                   bevel=1.0, mat=0)
    cv.ellipse(cx, 2.6, 1.6, 2.4, z=1.0, dome=0.8, mat=1)                           # the finial
    return _prop(cv, [MAHOGANY, BRASS, DIAL, ramp('#2a3438', dark=0.5, light=1.6), ramp('#1a1614', dark=0.6, light=1.5)],
                 relief=1.0, cavity=0.4, shadow=0.45)


def spr_balustrade():
    """A length of balustrade for the edge of a landing or a gallery: turned balusters between a
    handrail and a base rail, in dark wood. Stand it as a card along the edge with `z` at the
    landing's height."""
    w, h = 192, 32                                                   # three units long at its own height
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in range(4, w, 8):
        _lathe(cv, x, [(6, 1.4), (10, 2.4), (14, 1.2), (20, 2.0), (26, 1.4), (28, 1.6)], z=0.0, dome=1.0, mat=0)
    for x in (2, 94, 189):                                                          # newel posts
        cv.box(x - 2.5, 0, 5, 32, z=0.8, top=0.8, bevel=1.0, mat=0, tone=-0.04)
    cv.box(0, 1, w, 5, z=0.6, top=1.0, bevel=1.2, mat=0, tone=0.04)                # the handrail
    cv.box(0, 27, w, 5, z=0.4, top=0.8, bevel=1.0, mat=0, tone=-0.03)              # the base rail
    return _prop(cv, [ramp('#8a5a3a', dark=0.3, light=1.35)], relief=1.0, cavity=0.4, shadow=0.45)


def spr_bats():
    """Bats flying out of the eaves: half a dozen black silhouettes, wings spread or beating, at
    different distances. Float it with `z` against the moon."""
    rng = np.random.default_rng(223)
    w, h = 72, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(7):
        x, y = rng.uniform(8, w - 8), rng.uniform(6, h - 6)
        s = rng.uniform(0.6, 1.2)
        up = rng.random() < 0.5
        cv.ellipse(x, y, 1.4 * s, 2.0 * s, z=0.4, dome=0.5, mat=0)
        for side in (-1, 1):
            tip = (x + side * 7 * s, y + (-3.5 if up else 1.5) * s)
            mid = (x + side * 3.5 * s, y + (-2.0 if up else -0.5) * s)
            cv.polygon([(x, y - 0.5 * s), mid, tip, (x + side * 5 * s, y + 1.5 * s), (x + side * 2.5 * s, y + 1.0 * s),
                        (x, y + 1.0 * s)], z=0.3, top=0.3, bevel=0.5, mat=0)
        cv.ellipse(x - 0.8 * s, y - 2.2 * s, 0.6 * s, 0.9 * s, z=0.5, dome=0.3, mat=0)   # ears
        cv.ellipse(x + 0.8 * s, y - 2.2 * s, 0.6 * s, 0.9 * s, z=0.5, dome=0.3, mat=0)
    return _prop(cv, [BAT], outline=False, relief=1.0, cavity=0.2, shadow=0.2)


SPRITES = {'cobweb': spr_cobweb, 'candelabra': spr_candelabra, 'portrait': spr_portrait,
           'grandfather_clock': spr_grandfather_clock, 'balustrade': spr_balustrade, 'bats': spr_bats}
SPRITE_HEIGHT = {'cobweb': 0.9, 'candelabra': 1.2, 'portrait': 0.75, 'grandfather_clock': 1.6, 'balustrade': 0.5,
                 'bats': 0.6}
PROP_DEFAULTS = {'candelabra': {'aura': {'color': [1.0, 0.72, 0.38], 'strength': 0.5, 'radius': 0.3}},
                 'cobweb': {'shadow': False}, 'bats': {'shadow': False}}
NO_CONTACT_SHADOW = {'cobweb', 'portrait', 'bats'}

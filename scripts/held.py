"""The first-person held items, modelled in 3D and rendered to pixel art (sculpt.py) from the player's
eye, so each is seen as its holder sees it. Things you point - the revolver, the flashlight - run away
from the hand into the view; tools - the axe, the crowbar, the torch - are held like a hammer, the haft
across the fist and leaning back over the shoulder; the lantern hangs from the hand by its handle.
Every hand is what its owner sees of it: the back of the hand, facing out, and the thumb over the
handle - the fingers are round the far side, out of sight - and it runs back into a coat sleeve with a
shirt cuff, off the edge of the screen.

Each item is staged by where its parts should land on the 320x200 screen (where icons.viewmodel_origin
puts its canvas). They take half a second or so to render, so each is drawn once and kept.
"""
import functools
import math

import numpy as np

import sculpt as S
from icons import viewmodel_origin
from pixelart import ramp

COAT = ramp('#2a2a32', dark=0.5, light=1.45, cool=0.1)
CUFF = ramp('#8a8070', dark=0.45, light=1.4)
SKIN = ramp('#c88a62', dark=0.42, light=1.3, warm=0.12)
GUNMETAL = ramp('#4a4e56', dark=0.42, light=1.65, cool=0.1)
METAL = ramp('#8a9098', dark=0.38, light=1.55, cool=0.1)
IRON = ramp('#46464e', dark=0.45, light=1.7, cool=0.08)
WOOD = ramp('#7a5030', dark=0.38, light=1.45, warm=0.12)
REDBAR = ramp('#a8302a', dark=0.38, light=1.45)
CLOTH = ramp('#4a3a2a', dark=0.4, light=1.4)
GLASS = ramp('#ffc860', dark=0.8, light=1.2, warm=0.1)
M_COAT, M_CUFF, M_SKIN = 0, 1, 2          # every item's first three materials: the sleeve, cuff and hand
FOV = 70.0


def _kept(draw):
    """Draw an item once; hand out copies."""
    memo = functools.lru_cache(maxsize=None)(lambda fire: draw())

    @functools.wraps(draw)
    def get(fire=False):
        rgba, em = memo(bool(fire))
        return rgba.copy(), em.copy()
    return get


def _render(m, w, h, anchor, ramps, glow=()):
    return S.render(m, w, h, ramps, origin=viewmodel_origin(320, 200, w, h, anchor), fov=FOV, glow=glow)


def _staged(hand_px, head_px, hand_depth, head_depth):
    """The hand's point, the unit vector to the item's head, the distance and the head's point, from
    where they should land on the screen."""
    hnd = S.screen_point(*hand_px, hand_depth, FOV)
    hd = S.screen_point(*head_px, head_depth, FOV)
    return hnd, S.unit(hd - hnd), float(np.linalg.norm(hd - hnd)), hd


def _arm(m, wrist, elbow, cuff_at=0.12):
    """The forearm from the wrist back to the elbow, in a coat sleeve with the shirt cuff showing."""
    wrist, elbow = np.asarray(wrist, float), np.asarray(elbow, float)
    m.add(S.sd_round_cone, wrist, elbow, 0.024, 0.036, mat=M_SKIN, group='hand')
    toward = S.unit(elbow - wrist)
    c0 = wrist + (elbow - wrist) * cuff_at
    m.add(S.sd_round_cone, c0, elbow, 0.031, 0.052, mat=M_COAT, group='sleeve')
    m.add(S.sd_cylinder, c0 - toward * 0.004, c0 + toward * 0.007, 0.032, round_=0.002, mat=M_CUFF, group='cuff')


def _hand(m, c, axis, away, wrist, elbow, right=True, hr=0.015, span=0.075):
    """A hand closed round a handle of radius hr through c, running toward `axis` (the item's head), as
    its owner sees it: the back of the hand facing out (right for a right hand) and the thumb wrapped
    over the near side of the handle at the top of the fist. The fingers are round the far side - the
    side toward `away` - out of sight, so they are one rounded mass there, not fingers. The forearm runs
    from `wrist` back to `elbow`."""
    m.group('hand', 0.005)
    skin = dict(mat=M_SKIN, group='hand')
    a = S.unit(axis)
    c = np.asarray(c, float)
    away = np.asarray(away, float)
    f = S.unit(away - (away @ a) * a)                     # the far side
    o = S.unit(np.cross(f, a)) * (1 if right else -1)     # out: the back of the hand
    R = hr + 0.008

    def at(phi, rad, s):
        """A point round the handle: phi 0 at the back of the hand, 90 the far side, -90 the near."""
        ph = math.radians(phi)
        return c + a * s + (math.cos(ph) * o + math.sin(ph) * f) * rad

    rot = np.stack([a, f, o])
    m.add(S.sd_ellipsoid, at(10, R * 0.8, -0.006), (span / 2, 0.028, 0.0145), rot, **skin)          # back of the hand
    m.add(S.sd_ellipsoid, at(115, R * 0.55, -0.004), (span / 2 - 0.004, 0.02, 0.016), rot, **skin)   # the fingers, far
    m.add(S.sd_ellipsoid, at(-75, R * 0.6, -0.016), (0.026, 0.014, 0.017), rot, **skin)             # heel of the palm
    thumb = [at(-25, R + 0.005, span / 2 - 0.016), at(-82, R + 0.004, span / 2 - 0.004),
             at(-140, R + 0.001, span / 2 - 0.006)]
    m.add(S.sd_round_cone, thumb[0], thumb[1], 0.0135, 0.0112, **skin)                               # the thumb
    m.add(S.sd_round_cone, thumb[1], thumb[2], 0.0112, 0.0092, **skin)
    _arm(m, wrist, elbow)


def _hammer_grip(m, c, a, right=True, hr=0.015):
    """A tool held like a hammer: the haft across the fist, the forearm running forward under it at
    right angles, the wrist on the near side just below the thumb, the elbow off the bottom of the
    screen."""
    into = np.array([0.0, 0.15, 1.0])                     # the far side: into the scene
    f = S.unit(into - (into @ a) * a)
    elbow = S.screen_point(160 + (150 if right else -150), 330, 0.26, FOV)
    _hand(m, c, a, into, c - f * 0.045 - a * 0.022, elbow, right=right, hr=hr)


def _flame(rgba, em, p, ox, oy, height):
    """Tongues of flame standing on camera-space point p - orange, yellow and white, glowing - painted
    over the canvas (whose top left is at (ox, oy) on the screen)."""
    h, w = em.shape
    t = math.tan(math.radians(FOV) / 2)
    sx = 160 + p[0] / p[2] / t * 160 - ox
    sy = 100 + p[1] / p[2] / t * 160 - oy
    size = height / p[2] / t * 160
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    for rx, ry, colour in ((0.42, 1.0, (1.0, 0.54, 0.12)), (0.28, 0.72, (1.0, 0.8, 0.3)), (0.15, 0.42, (1.0, 0.97, 0.8))):
        cy = sy - size * ry * 0.5
        wob = 1 + 0.2 * np.sin(np.arctan2(yy - cy, xx - sx) * 5 + sx) * (yy < cy)
        tongue = (((xx - sx) / (size * rx)) ** 2 + ((yy - cy) / (size * ry * 0.5 * wob)) ** 2 < 1) & (yy < sy + size * 0.1)
        rgba[tongue, :3] = colour
        rgba[tongue, 3] = 1.0
        em[tongue] = 1.0
    return rgba, em


@_kept
def vm_revolver():
    """A revolver in the right hand, seen from behind: the barrel running away toward the middle of the
    view, the hammer and the top strap nearest; the back of the hand on the right of the grip and the
    thumb low along the left of it."""
    w, h = 141, 112
    m = S.Model()
    o = S.screen_point(266, 150, 0.31, FOV)
    G = S.Frame(o, np.array([-1.7, 0.35, 6.0]) - o)
    level = G.rot((1, 0, 0), (0, 1, 0))
    gun = dict(mat=3, group='gun')
    m.group('gun', 0.0015)
    m.add(S.sd_cylinder, G.P(0, 0, 0.044), G.P(0, 0, 0.150), 0.0075, round_=0.001, **gun)               # barrel
    m.add(S.sd_cylinder, G.P(0, -0.0105, 0.050), G.P(0, -0.0105, 0.146), 0.005, round_=0.001, **gun)    # its lug
    m.add(S.sd_box, G.P(0, 0.0092, 0.143), (0.0013, 0.0035, 0.004), level, **gun)                       # front sight
    m.add(S.sd_cylinder, G.P(0, -0.0115, 0.003), G.P(0, -0.0115, 0.042), 0.0185, round_=0.003, **gun)  # cylinder
    m.add(S.sd_box, G.P(0, 0.0105, 0.022), (0.006, 0.0025, 0.024), level, round_=0.001, **gun)         # top strap
    m.add(S.sd_box, G.P(0, -0.012, 0.045), (0.008, 0.012, 0.003), level, round_=0.001, **gun)
    m.add(S.sd_box, G.P(0, -0.008, -0.004), (0.0105, 0.017, 0.006), level, round_=0.002, **gun)        # recoil shield
    m.add(S.sd_round_cone, G.P(0, 0.004, -0.008), G.P(0, 0.013, -0.021), 0.0036, 0.003, **gun)        # hammer
    m.add(S.sd_box, G.P(0, -0.03, 0.012), (0.0075, 0.009, 0.02), level, round_=0.002, **gun)
    guard = [G.P(0, -0.037, 0.031), G.P(0, -0.051, 0.027), G.P(0, -0.056, 0.012), G.P(0, -0.048, -0.003)]
    for p0, p1 in zip(guard, guard[1:]):
        m.add(S.sd_round_cone, p0, p1, 0.0022, 0.0022, **gun)                                           # trigger guard
    m.add(S.sd_round_cone, G.P(0, -0.035, 0.015), G.P(0, -0.047, 0.018), 0.0018, 0.0016, **gun)      # trigger
    gd = S.unit((0.0, -0.95, -0.33))                                   # down the grip, raked back
    gc = np.array([0.0, -0.03, -0.008]) + gd * 0.040
    m.add(S.sd_box, G.P(*gc), (0.0135, 0.044, 0.0155), G.rot((1, 0, 0), tuple(gd)), round_=0.009, mat=4, group='grip')

    m.group('hand', 0.0035)
    hand = dict(mat=M_SKIN, group='hand')
    x = np.array([1.0, 0, 0])
    n = -np.cross(x, gd)                                               # toward the grip's front strap
    grip_rot = np.stack([G.D(*x), G.D(*gd), G.D(*n)])

    def gp(xx, dd, nn):
        return G.P(*(gc + x * xx + gd * dd + n * nn))

    def around(theta, s, grow=0.0):
        th = math.radians(theta)
        return gp(math.cos(th) * (0.0215 + grow), s, math.sin(th) * (0.0235 + grow))

    index = [around(-35, -0.043, 0.004), G.P(0.0105, -0.034, 0.004), G.P(0.0075, -0.040, 0.015), G.P(0.001, -0.043, 0.017)]
    for p0, p1, ra, rb in zip(index, index[1:], (0.0092, 0.0085, 0.0076), (0.0085, 0.0076, 0.0066)):
        m.add(S.sd_round_cone, p0, p1, ra, rb, **hand)                                                 # on the trigger
    m.add(S.sd_ellipsoid, gp(0.023, -0.006, -0.004), (0.011, 0.041, 0.031), grip_rot, **hand)          # back of the hand
    m.add(S.sd_ellipsoid, gp(0.002, -0.014, -0.02), (0.02, 0.034, 0.014), grip_rot, **hand)            # palm on the strap
    t0, t1, t2 = gp(-0.008, -0.03, -0.018), G.P(-0.0135, -0.027, -0.008), G.P(-0.014, -0.033, 0.004)
    m.add(S.sd_round_cone, t0, t1, 0.0128, 0.0112, **hand)                                             # the thumb
    m.add(S.sd_round_cone, t1, t2, 0.0112, 0.0098, **hand)
    _arm(m, gp(0.004, 0.02, -0.03), S.screen_point(400, 360, 0.22, FOV), cuff_at=0.1)
    return _render(m, w, h, 'right', [COAT, CUFF, SKIN, GUNMETAL, WOOD])


@_kept
def vm_flashlight():
    """An electric torch pointed up into the scene from the right fist, the forearm running on behind
    it; the back of the hand faces out and the thumb lies over the top."""
    w, h = 141, 110
    m = S.Model()
    c, a, length, head = _staged((282, 190), (238, 112), 0.40, 0.52)
    m.add(S.sd_cylinder, c - a * 0.08, c + a * (length - 0.035), 0.0155, round_=0.003, mat=3)          # barrel
    m.add(S.sd_round_cone, c + a * (length - 0.035), c + a * (length - 0.004), 0.016, 0.022, mat=4)  # head
    m.add(S.sd_cylinder, c + a * (length - 0.006), c + a * length, 0.0222, round_=0.002, mat=4)     # rim
    down = np.array([0.0, 1.0, 0.0])                                   # the fingers cup underneath
    f = S.unit(down - (down @ a) * a)
    _hand(m, c, a, down, c - a * 0.06 - f * 0.01, S.screen_point(400, 330, 0.32, FOV), right=True)
    return _render(m, w, h, 'right', [COAT, CUFF, SKIN, IRON, METAL])


@_kept
def vm_axe():
    """A felling axe held up in the right fist like a hammer, the haft leaning back over the shoulder,
    the blade toward the middle of the view."""
    w, h = 141, 150
    m = S.Model()
    c, a, length, head = _staged((240, 180), (290, 76), 0.50, 0.45)
    m.add(S.sd_round_cone, c - a * 0.07, c + a * (length + 0.02), 0.0135, 0.0125, mat=3)              # the haft
    F = S.Frame(head, a, up_hint=(0, 0, 1))
    m.add(S.sd_box, F.P(0.045, 0, 0), (0.05, 0.008, 0.032), F.rot((1, 0, 0), (0, 1, 0)), round_=0.003, mat=4)  # head
    m.add(S.sd_cylinder, F.P(0, 0, -0.03), F.P(0, 0, 0.03), 0.018, round_=0.003, mat=4)              # the eye
    _hammer_grip(m, c, a, right=True)
    return _render(m, w, h, 'right', [COAT, CUFF, SKIN, WOOD, IRON])


@_kept
def vm_crowbar():
    """A crowbar held up in the right fist like a hammer, leaning back, its claw hooked over at the top."""
    w, h = 141, 150
    m = S.Model()
    c, a, length, head = _staged((242, 180), (288, 80), 0.50, 0.45)
    m.add(S.sd_round_cone, c - a * 0.07, head, 0.0095, 0.0095, mat=3)                                   # the bar
    F = S.Frame(head, a, up_hint=(0, 0, 1))
    claw = [F.P(0, 0, 0), F.P(0.012, 0, 0.03), F.P(0.04, 0, 0.044), F.P(0.07, 0, 0.034), F.P(0.086, 0, 0.022)]
    for p0, p1 in zip(claw, claw[1:]):
        m.add(S.sd_round_cone, p0, p1, 0.0095, 0.0088, mat=3)
    _hammer_grip(m, c, a, right=True, hr=0.0095)
    return _render(m, w, h, 'right', [COAT, CUFF, SKIN, REDBAR])


@_kept
def vm_torch():
    """A burning torch held up in the left fist like a hammer, leaning back and out: a wooden haft, rags
    soaked in pitch, the flame."""
    w, h = 115, 150
    m = S.Model()
    c, a, length, head = _staged((80, 180), (38, 90), 0.50, 0.45)
    m.add(S.sd_round_cone, c - a * 0.06, c + a * (length - 0.04), 0.0135, 0.016, mat=3)               # the haft
    m.add(S.sd_round_cone, c + a * (length - 0.05), c + a * (length + 0.01), 0.022, 0.02, mat=4)      # the rags
    _hammer_grip(m, c, a, right=False)
    rgba, em = _render(m, w, h, 'left', [COAT, CUFF, SKIN, WOOD, CLOTH])
    return _flame(rgba, em, c + a * (length + 0.01), *viewmodel_origin(320, 200, w, h, 'left'), 0.075)


@_kept
def vm_lantern():
    """An oil lantern hanging by its handle from the left hand - the back of the hand on top - the flame
    in its glass."""
    w, h = 115, 150
    m = S.Model()
    grip = S.screen_point(56, 104, 0.47, FOV)
    body = grip + np.array([0.0, 0.118, 0.0])                                                            # it hangs below
    m.add(S.sd_cylinder, body + (0, -0.052, 0), body + (0, 0.043, 0), 0.029, round_=0.004, mat=6)       # the glass
    for ang in range(45, 405, 90):                                                                       # its frame
        off = np.array([math.cos(math.radians(ang)) * 0.031, 0, math.sin(math.radians(ang)) * 0.031])
        m.add(S.sd_round_cone, body + off + (0, -0.052, 0), body + off + (0, 0.043, 0), 0.0028, 0.0028, mat=3)
    m.add(S.sd_round_cone, body + (0, -0.07, 0), body + (0, -0.052, 0), 0.013, 0.035, mat=3)              # the cap
    m.add(S.sd_cylinder, body + (0, 0.043, 0), body + (0, 0.058, 0), 0.035, round_=0.003, mat=3)         # the base
    bail = [body + (-0.032, -0.055, 0), grip + (-0.026, 0.011, 0), grip + (0.026, 0.011, 0), body + (0.032, -0.055, 0)]
    for p0, p1 in zip(bail, bail[1:]):
        m.add(S.sd_round_cone, p0, p1, 0.0028, 0.0028, mat=3)
    m.add(S.sd_cylinder, grip + (-0.034, 0, 0), grip + (0.034, 0, 0), 0.0085, round_=0.003, mat=4)       # wooden handle
    _hand(m, grip, (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), grip - np.array([0.06, 0.0, 0.02]),
          S.screen_point(-150, 150, 0.34, FOV), right=False, hr=0.0085, span=0.07)
    rgba, em = _render(m, w, h, 'left', [COAT, CUFF, SKIN, IRON, WOOD, IRON, GLASS], glow=(6,))
    return _flame(rgba, em, body + (0, 0.012, 0), *viewmodel_origin(320, 200, w, h, 'left'), 0.03)


HELD = {'revolver': vm_revolver, 'lantern': vm_lantern, 'flashlight': vm_flashlight, 'axe': vm_axe,
        'crowbar': vm_crowbar, 'torch': vm_torch}

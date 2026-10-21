"""The first-person held items, modelled in 3D and rendered to pixel art (sculpt.py) from the player's
eye, so each is seen as its holder sees it. Things you point - the revolver, the flashlight - run away
from the hand into the view; tools - the axe, the crowbar, the torch - are held like a hammer, the haft
across the fist and leaning back over the shoulder; the lantern hangs from the hand by its handle.
Every hand is what its owner sees of it - a fist built bone by bone round the handle (_fist): the back
of the hand facing out, the thumb across the near side, the fingertips coming round from the far side
- and it runs back into a coat sleeve with a shirt cuff, off the edge of the screen.

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


#          across the knuckles, radius, the lengths of the three bones (metres)
FINGERS = ((0.0265, 0.0096, 0.044, 0.025, 0.019),            # index
           (0.0075, 0.0099, 0.048, 0.028, 0.020),            # middle
           (-0.0110, 0.0093, 0.045, 0.026, 0.019),           # ring
           (-0.0275, 0.0083, 0.036, 0.020, 0.017))           # little


def _round(th, length, rad):
    """The angle (degrees) reached going `length` on round a circle of radius rad from angle th - in
    straight bones, so their joints sit on the circle."""
    return th + math.degrees(2 * math.asin(min(length / (2 * rad), 0.999)))


def _facing(a, roll, base=(1.0, 0.0, 0.0)):
    """Which way the back of a hand faces: `base` made square to the handle a, then turned `roll`
    degrees round it toward the eye."""
    b = np.asarray(base, float)
    b = S.unit(b - (b @ a) * a)
    t = np.array([0.0, 0.0, -1.0])
    t = S.unit(t - (t @ a) * a - (t @ b) * b)
    return math.cos(math.radians(roll)) * b + math.sin(math.radians(roll)) * t


def _fist(m, c, axis, out, right=True, r=0.015, beta=15.0, curl=0.85, thumb=(-48.0, 0.0, -0.004)):
    """A hand closed round a handle of radius r through c, the handle running toward `axis` out of the
    thumb's end of the fist and the back of the hand facing `out`; returns the wrist.

    In the handle's frame - x the way the back of the hand faces, y to the front of the fist where the
    knuckles are, z along the handle - each finger runs from its knuckle round the front and the far
    side, bone by bone at its true length, its tip coming back round toward the eye (`curl` is how far
    its last two bones go round: less leaves only the fingertips showing past the handle's edge); the
    thumb lies across the near side at the head end of the fist, its last joint running on past the edge.
    `thumb` is where its root sits round the handle (degrees from the back of the hand), how far its
    last joint bends round, and how far its tip climbs toward the head. A thin handle lies in the
    hollow of the fist against the palm, the thumb over the curled fingers rather than hugging it. The
    palm is the four bones behind the knuckles melted together, slanting back to the wrist by the
    grip's obliquity beta (a handle crosses the palm from the heel to the base of the index finger).
    The fingers and thumb stay apart from each other, and melt into the palm."""
    m.group('hand', 0.011)
    m.group('digits', 0.0015, into='hand', k_into=0.004)
    palm, digit = dict(mat=M_SKIN, group='hand'), dict(mat=M_SKIN, group='digits')
    a = S.unit(axis)
    c = np.asarray(c, float)
    x = S.unit(out - (out @ a) * a)
    y = np.cross(a, x) if right else np.cross(x, a)
    frame = np.stack([x, y, a])

    def P(p):
        return c + p @ frame

    b = math.radians(beta)
    hx, hy, hz = np.eye(3)[0], np.array([0.0, math.cos(b), math.sin(b)]), np.array([0.0, -math.sin(b), math.cos(b)])
    hand_rot = np.stack([x, hy @ frame, hz @ frame])
    W0 = max(r + 0.0096, 0.0205)                                         # the hollow the fingers close round
    gap = W0 - 0.0096 - r
    hole = np.array([-gap * 0.75, -gap * 0.55])
    K0 = np.array([r + 0.0115, hole[1] + W0 * 0.8, 0.004])               # the middle of the knuckles
    knuckles = []
    for zk, rf, lp, lm, ld in FINGERS:
        k = K0 + hz * zk
        knuckles.append(k)
        W = W0 + (rf - 0.0096) * 0.5 + 0.0012
        rel = k[:2] - hole
        d = float(np.linalg.norm(rel))
        meet = math.degrees(math.atan2(rel[1], rel[0]) + math.acos(min(W / d, 0.999)))     # where it meets the hollow
        th1 = _round(meet, max(lp - math.sqrt(max(d * d - W * W, 0.0)), 0.0), W)
        th2 = _round(th1, lm * curl, W)
        th3 = min(_round(th2, ld * 0.72 * curl, W), 262.0)

        def on(th, rad):
            t = math.radians(th)
            return P(np.array([hole[0] + math.cos(t) * rad, hole[1] + math.sin(t) * rad, k[2]]))

        j = [P(k), on(th1, W + 0.0015), on(th2, W + 0.001), on(th3, W - 0.0005)]
        for j0, j1, r0, r1 in zip(j, j[1:], (1.02, 0.94, 0.86), (0.94, 0.86, 0.76)):
            m.add(S.sd_round_cone, j0, j1, rf * r0, rf * r1, **digit)
    wrist = K0 - hy * 0.083 - hz * 0.004 + hx * 0.001
    for (zk, *_), k in zip(FINGERS, knuckles):                          # the bones behind the knuckles
        m.add(S.sd_round_cone, P(k + hx * 0.0015), P(wrist + hz * zk * 0.55 + hx * 0.001), 0.0105, 0.0095, **palm)
    m.add(S.sd_ellipsoid, P((K0 + wrist) / 2 - hx * 0.006), (0.012, 0.042, 0.034), hand_rot, **palm)       # the palm
    m.add(S.sd_ellipsoid, P(wrist + hy * 0.03 - hx * 0.01 - hz * 0.02), (0.014, 0.026, 0.016), hand_rot, **palm)  # its heel

    Wt = max(r + 0.0134, 0.027)                                           # the thumb, round the near side
    zt = K0[2] + FINGERS[0][0] * math.cos(b) + 0.016
    root = wrist + hy * 0.012 + hz * 0.030 - hx * 0.004
    t0 = math.radians(thumb[0])
    t1 = t0 - math.radians(_round(0.0, 0.031, Wt))
    j1 = np.array([math.cos(t0) * (Wt + 0.004), math.sin(t0) * (Wt + 0.004), zt - 0.006])
    j2 = np.array([math.cos(t1) * (Wt + 0.001), math.sin(t1) * (Wt + 0.001), zt])
    d1 = S.unit(j2[:2] - j1[:2])
    q = math.radians(-thumb[1])                                           # the last joint
    j3 = j2 + np.array([(d1[0] * math.cos(q) - d1[1] * math.sin(q)) * 0.019,
                        (d1[0] * math.sin(q) + d1[1] * math.cos(q)) * 0.019, thumb[2]])
    m.add(S.sd_round_cone, P(root), P(j1), 0.0135, 0.0128, **palm)
    m.add(S.sd_ellipsoid, P(root * 0.55 + j1 * 0.45 - hx * 0.004), (0.013, 0.018, 0.016), hand_rot, **palm)  # its ball
    m.add(S.sd_round_cone, P(j1), P(j2), 0.0128, 0.0118, **digit)
    m.add(S.sd_round_cone, P(j2), P(j3), 0.0118, 0.0102, **digit)
    return P(wrist - hy * 0.006)


def _turned(F, spin):
    """An item head's frame F turned `spin` degrees in the hand, round the haft: its x (across the view)
    toward its y (away from the eye)."""
    s = math.radians(spin)
    F.r, F.u = math.cos(s) * F.r + math.sin(s) * F.u, math.cos(s) * F.u - math.sin(s) * F.r
    return F


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
    """An electric torch pointed up into the scene from the right fist, the forearm running off to the
    bottom right: the back of the hand up and out, the thumb across the top of the barrel, the
    fingertips curled round under it on the left."""
    w, h = 141, 110
    m = S.Model()
    c, a, length, head = _staged((282, 190), (238, 112), 0.40, 0.52)
    m.add(S.sd_cylinder, c - a * 0.08, c + a * (length - 0.035), 0.0155, round_=0.003, mat=3)          # barrel
    m.add(S.sd_round_cone, c + a * (length - 0.035), c + a * (length - 0.004), 0.016, 0.022, mat=4)  # head
    m.add(S.sd_cylinder, c + a * (length - 0.006), c + a * length, 0.0222, round_=0.002, mat=4)     # rim
    wrist = _fist(m, c, a, _facing(a, 0, base=(1.0, -0.4, 0.0)), r=0.0155, beta=30.0,             # aslant in the palm
                  thumb=(-34.0, 38.0, 0.004))                          # the thumb's tip curled down round the barrel
    _arm(m, wrist, S.screen_point(400, 330, 0.32, FOV))
    return _render(m, w, h, 'right', [COAT, CUFF, SKIN, IRON, METAL])


@_kept
def vm_axe():
    """A felling axe held up in the right fist like a hammer, the haft leaning back over the shoulder,
    the blade turned in the hand to point away from the eye; the thumb over the haft, the back of the
    hand outward, the wrist straight below and only the fingertips showing round the haft."""
    w, h = 141, 150
    m = S.Model()
    c, a, length, head = _staged((240, 180), (290, 76), 0.50, 0.45)
    m.add(S.sd_round_cone, c - a * 0.07, c + a * (length + 0.02), 0.0135, 0.0125, mat=3)              # the haft
    F = _turned(S.Frame(head, a, up_hint=(0, 0, 1)), 70)
    m.add(S.sd_box, F.P(0.045, 0, 0), (0.05, 0.008, 0.032), F.rot((1, 0, 0), (0, 1, 0)), round_=0.003, mat=4)  # head
    m.add(S.sd_cylinder, F.P(0, 0, -0.03), F.P(0, 0, 0.03), 0.018, round_=0.003, mat=4)              # the eye
    _arm(m, _fist(m, c, a, _facing(a, 22), r=0.0135, curl=0.45), S.screen_point(390, 330, 0.30, FOV))
    return _render(m, w, h, 'right', [COAT, CUFF, SKIN, WOOD, IRON])


@_kept
def vm_crowbar():
    """A crowbar held up in the right fist like a hammer, leaning back, its claw hooked over at the top
    and turned in the hand to hook away from the eye."""
    w, h = 141, 150
    m = S.Model()
    c, a, length, head = _staged((242, 180), (288, 80), 0.50, 0.45)
    m.add(S.sd_round_cone, c - a * 0.07, head, 0.0095, 0.0095, mat=3)                                   # the bar
    F = _turned(S.Frame(head, a, up_hint=(0, 0, 1)), 70)
    claw = [F.P(0, 0, 0), F.P(0.012, 0, 0.03), F.P(0.04, 0, 0.044), F.P(0.07, 0, 0.034), F.P(0.086, 0, 0.022)]
    for p0, p1 in zip(claw, claw[1:]):
        m.add(S.sd_round_cone, p0, p1, 0.0095, 0.0088, mat=3)
    _arm(m, _fist(m, c, a, _facing(a, 22), r=0.0095, curl=0.45), S.screen_point(390, 330, 0.30, FOV))
    return _render(m, w, h, 'right', [COAT, CUFF, SKIN, REDBAR])


@_kept
def vm_torch():
    """A burning torch held up in the left fist like a hammer, leaning back and out: a wooden haft, slim
    where the hand closes tight round it, rags soaked in pitch, the flame."""
    w, h = 115, 150
    m = S.Model()
    c, a, length, head = _staged((80, 180), (38, 90), 0.50, 0.45)
    m.add(S.sd_round_cone, c - a * 0.06, c + a * (length - 0.04), 0.0105, 0.0135, mat=3)              # the haft
    m.add(S.sd_round_cone, c + a * (length - 0.05), c + a * (length + 0.01), 0.022, 0.02, mat=4)      # the rags
    wrist = _fist(m, c, a, _facing(a, 22, base=(-1.0, 0.0, 0.0)), right=False, r=0.0105, curl=0.45)
    _arm(m, wrist, S.screen_point(-70, 330, 0.30, FOV))
    rgba, em = _render(m, w, h, 'left', [COAT, CUFF, SKIN, WOOD, CLOTH])
    return _flame(rgba, em, c + a * (length + 0.01), *viewmodel_origin(320, 200, w, h, 'left'), 0.075)


@_kept
def vm_lantern():
    """An oil lantern hanging by its bail from the left fist - the back of the hand on top and held up,
    not drooping, the fingers curled under the handle, the forearm reaching in from the left - the
    flame in its glass."""
    w, h = 115, 150
    m = S.Model()
    grip = S.screen_point(56, 94, 0.47, FOV)
    a = S.unit((1.0, 0.0, -0.3))                                       # the handle, square to the forearm
    body = grip + np.array([0.0, 0.142, 0.0])                                                            # it hangs below
    m.add(S.sd_cylinder, body + (0, -0.052, 0), body + (0, 0.043, 0), 0.029, round_=0.004, mat=6)       # the glass
    for ang in range(45, 405, 90):                                                                       # its frame
        off = np.array([math.cos(math.radians(ang)) * 0.031, 0, math.sin(math.radians(ang)) * 0.031])
        m.add(S.sd_round_cone, body + off + (0, -0.052, 0), body + off + (0, 0.043, 0), 0.0028, 0.0028, mat=3)
    m.add(S.sd_round_cone, body + (0, -0.07, 0), body + (0, -0.052, 0), 0.013, 0.035, mat=3)              # the cap
    m.add(S.sd_cylinder, body + (0, 0.043, 0), body + (0, 0.058, 0), 0.035, round_=0.003, mat=3)         # the base
    ends = (grip - a * 0.047, grip + a * 0.047)
    bail = [body + (-0.032, -0.055, 0), ends[0] + (0, 0.011, 0) - a * 0.004, ends[1] + (0, 0.011, 0) + a * 0.004,
            body + (0.032, -0.055, 0)]
    for p0, p1 in zip(bail, bail[1:]):
        m.add(S.sd_round_cone, p0, p1, 0.0028, 0.0028, mat=3)
    m.add(S.sd_cylinder, ends[0], ends[1], 0.0085, round_=0.003, mat=4)                                  # wooden handle
    wrist = _fist(m, grip, a, _facing(a, 35, base=(0.0, -1.0, 0.0)), right=False, r=0.0085, beta=10.0)
    _arm(m, wrist, S.screen_point(-120, 300, 0.26, FOV))
    rgba, em = _render(m, w, h, 'left', [COAT, CUFF, SKIN, IRON, WOOD, IRON, GLASS], glow=(6,))
    return _flame(rgba, em, body + (0, 0.012, 0), *viewmodel_origin(320, 200, w, h, 'left'), 0.03)


HELD = {'revolver': vm_revolver, 'lantern': vm_lantern, 'flashlight': vm_flashlight, 'axe': vm_axe,
        'crowbar': vm_crowbar, 'torch': vm_torch}

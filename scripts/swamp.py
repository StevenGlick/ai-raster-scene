"""The swamp, drawn with the pixel-art toolkit (scripts/pixelart.py): black water skinned with
duckweed, peat and sphagnum, the murk between the trunks for a swamp's edge - and bald cypresses
hung with Spanish moss, their knees standing out of the water, cattails, a heron, an alligator
watching from the surface, and fireflies.

As in the other toolkit modules, every shape is stamped into a height field, lit from the upper
left and snapped onto hue-shifted ramps; every texture tiles.
"""
import numpy as np

from biomes import CARD_PX, CARD_W, T, _prop, _rng, _stamp, _tile
from pixelart import Canvas, ramp, smooth_noise

BLACKWATER = ramp('#2a3324', dark=0.4, light=1.5, warm=0.04, cool=0.1)
DUCKWEED = ramp('#5e7a2e', dark=0.4, light=1.25)
PEAT = ramp('#3a3024', dark=0.4)
SPHAGNUM = [ramp('#8aa448', dark=0.35, light=1.2), ramp('#9a4a3a', dark=0.35)]
CYPRESS_BARK = ramp('#6a5a4a', dark=0.28, light=1.3)
CYPRESS_LEAF = ramp('#5a7034', dark=0.3, light=1.25)
MOSS_GREY = ramp('#76806a', dark=0.4, light=1.18, cool=0.1)
CATTAIL = ramp('#6a7a38', dark=0.35)
CATTAIL_HEAD = ramp('#6a4a2c', dark=0.35)
HERON = ramp('#9aa0a4', dark=0.35, light=1.25)
HERON_DARK = ramp('#3a3e44', dark=0.5, light=1.6)
BEAK_YELLOW = ramp('#c8a040', dark=0.4)
GATOR = ramp('#3e4430', dark=0.4, light=1.5)
EYE = ramp('#d8b040', dark=0.5, light=1.2)
FIREFLY = ramp('#d8f070', dark=0.7, light=1.1)


# ---------------------------------------------------------------- textures

def tex_swamp_water(name):
    """Swamp water: black-brown and still, a skin of duckweed drifting across it in patches, a few
    leaves floating."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.tone += (0.16 * (smooth_noise(T, T, 3, rng) - 0.5)).astype(np.float32)
    skin = smooth_noise(T, T, 5, rng) * 0.7 + smooth_noise(T, T, 9, rng) * 0.3
    speck = rng.random((T, T)) < np.clip((skin - 0.56) * 3.0, 0, 0.7)
    cv.mat[speck] = 1                                          # duckweed
    cv.z[speck] += 0.25
    cv.tone[speck] += rng.normal(0, 0.06, int(speck.sum())).astype(np.float32)
    for _ in range(5):                                         # floating leaves
        x, y = rng.random() * T, rng.random() * T
        a = rng.uniform(0, np.pi)
        cv.leaf(x, y, x + np.cos(a) * 4, y + np.sin(a) * 4, 2.4, z=0.4, dome=0.3, mat=2, rib=0.2)
    return _tile(cv, [BLACKWATER, DUCKWEED, ramp('#6a5a30', dark=0.35)], dither=0.3, cavity=0.2, shadow=0.25,
                 ambient=0.22, diffuse=0.5)


def tex_bog(name):
    """Swamp ground: black peat, cushions of sphagnum in green and rust, standing puddles between."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.noise(0.4, cells=6, rng=rng, octaves=3)
    for _ in range(36):                                        # sphagnum cushions
        x, y = rng.random() * T, rng.random() * T
        m = 1 if rng.random() < 0.7 else 2
        for _ in range(8):
            cv.ellipse(x + rng.normal(0, 2.2), y + rng.normal(0, 1.8), rng.uniform(0.8, 1.6), rng.uniform(0.7, 1.3),
                       z=0.5, dome=0.7, mat=m, tone=rng.normal(0, 0.05))
    wet = smooth_noise(T, T, 4, rng) > 0.66                    # puddles
    cv.mat[wet] = 3
    cv.z[wet] = -0.3
    cv.tone[wet] = 0.0
    return _tile(cv, [PEAT] + SPHAGNUM + [BLACKWATER], cavity=0.45, shadow=0.45)


def tex_swamp_deep(name):
    """The inside of a swamp seen from its edge: grey trunks at every depth standing in the murk,
    flared at the foot, curtains of Spanish moss hanging between them catching a little light."""
    rng = _rng(name)
    cv = Canvas(T, ground=-2.0, mat=2)
    for depth in range(4):
        for _ in range((5, 4, 3, 2)[depth]):
            x = rng.random() * T
            wd = (2.0, 3.0, 4.0, 5.5)[depth] * rng.uniform(0.8, 1.2)
            ph, amp = rng.uniform(0, 2 * np.pi), rng.uniform(0.2, 0.7)
            cv.stroke([(x + amp * np.sin(2 * np.pi * y / T + ph), y) for y in range(-4, T + 5, 4)], wd,
                      z=-1.6 + depth * 0.5, dome=0.6 + depth * 0.2, mat=0, tone=-0.4 + depth * 0.12)
    for _ in range(16):                                        # moss curtains
        x, y = rng.random() * T, rng.random() * T
        for _ in range(7):
            sx = x + rng.normal(0, 2.5)
            L = rng.uniform(6, 16)
            cv.stroke([(sx, y), (sx + rng.normal(0, 0.8), y + L / 2), (sx + rng.normal(0, 1.2), y + L)], 0.8,
                      z=0.6 + rng.random() * 0.3, dome=0.3, taper=(1, 0.3), mat=1, tone=rng.normal(-0.12, 0.06))
    return _tile(cv, [CYPRESS_BARK, MOSS_GREY, ramp('#141a16', dark=0.6, light=1.4)], cavity=0.4, shadow=0.5,
                 ambient=0.3, diffuse=0.6)


# ---------------------------------------------------------------- props

def _moss(cv, rng, x, y, n, length, z, mat=2):
    """Spanish moss hanging from a point: grey-green strands, wavy, the longest in the middle."""
    for k in range(n):
        sx = x + rng.normal(0, 1.6)
        L = length * rng.uniform(0.5, 1.0) * (1 - abs(sx - x) / 8)
        if L < 2:
            continue
        pts = [(sx, y)]
        for t in np.linspace(0.25, 1, 4):
            pts.append((sx + np.sin(t * 5 + k) * 1.2, y + L * t))
        cv.stroke(pts, rng.uniform(0.7, 1.1), z=z + rng.random() * 0.3, dome=0.3, taper=(1.0, 0.35), mat=mat,
                  tone=rng.normal(0, 0.06))


def spr_bald_cypress():
    """A bald cypress standing in the water: a trunk flared and fluted into buttresses at its foot,
    branches spreading high up under flat sprays of feathery leaves, and Spanish moss hanging from
    every branch in grey-green curtains. A few knees stand out of the water round it."""
    rng = np.random.default_rng(181)
    w, h = 112, 196
    cx = 56
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(cx - 6, h - 46), (cx + 6, h - 46), (cx + 22, h), (cx - 22, h)], z=0.0, top=1.2, bevel=6, mat=0)
    for x in (cx - 13, cx - 6, cx + 1, cx + 8, cx + 15):        # fluting down the buttresses
        cv.stroke([(cx + (x - cx) * 0.35, h - 44), (x, h - 1)], 1.0, dome=0.5, mode='carve')
    cv.stroke([(cx, h - 40), (cx - 1, 90), (cx + 1, 30)], 10, z=0.4, dome=1.0, taper=(1.0, 0.45), mat=0)
    for kx in (cx - 30, cx - 26, cx + 27, cx + 33, cx - 38):     # knees
        kh = rng.uniform(5, 10)
        cv.polygon([(kx - 3, h), (kx - 1, h - kh), (kx + 1.5, h - kh + 1), (kx + 3, h)], z=0.2, top=0.8, bevel=1.5,
                   mat=0, tone=-0.05)
    limbs = [((cx, 100), (cx - 30, 86), (cx - 48, 84)), ((cx, 92), (cx + 28, 78), (cx + 50, 80)),
             ((cx, 70), (cx - 22, 56), (cx - 40, 52)), ((cx + 1, 62), (cx + 22, 48), (cx + 42, 46)),
             ((cx + 1, 40), (cx - 14, 30), (cx - 28, 26)), ((cx + 1, 36), (cx + 14, 24), (cx + 26, 22))]
    for p0, p1, p2 in limbs:
        cv.stroke([p0, p1, p2], 3.2, z=0.8, dome=0.8, taper=(1.0, 0.4), mat=0)
    for p0, p1, p2 in limbs:                                    # flat sprays of leaves along each limb
        for _ in range(16):
            t = rng.uniform(0.3, 1.0)
            x = p1[0] + (p2[0] - p1[0]) * t + rng.normal(0, 4)
            y = p1[1] + (p2[1] - p1[1]) * t + rng.normal(-3, 2.5)
            for _ in range(5):
                a = np.radians(rng.uniform(150, 390))
                L = rng.uniform(3, 6)
                cv.stroke([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L * 0.5)], 1.2, z=1.6 + rng.random() * 0.4,
                          dome=0.4, taper=(1, 0.4), mat=1, tone=rng.normal(0.02, 0.05))
    for p0, p1, p2 in limbs:                                    # moss from every limb
        for t in (0.35, 0.65, 0.95):
            x = p0[0] + (p2[0] - p0[0]) * t
            y = p0[1] + (p2[1] - p0[1]) * t
            _moss(cv, rng, x, y + 1, 9, rng.uniform(14, 30), z=2.4)
    leaves = (cv.mat == 1) & (cv.id > 0)
    cv.tone += np.where(leaves, 0.08 - 0.2 * np.clip(np.arange(h)[:, None] / 110.0, 0, 1), 0).astype(np.float32)
    return _prop(cv, [CYPRESS_BARK, CYPRESS_LEAF, MOSS_GREY], relief=1.0, cavity=0.45, shadow=0.5, reach=7)


def spr_spanish_moss():
    """A curtain of Spanish moss hanging from a stub of branch: to hang from a limb, an eave or the
    top of a swamp's edge with `z`."""
    rng = np.random.default_rng(183)
    w, h = 44, 72
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(0, 4), (22, 6), (44, 3)], 2.6, z=0.0, dome=0.8, mat=0)
    for x in (8, 15, 22, 29, 36):
        _moss(cv, rng, x, 6, 8, rng.uniform(40, 64), z=0.6, mat=1)
    return _prop(cv, [CYPRESS_BARK, MOSS_GREY], relief=1.0, cavity=0.35, shadow=0.4)


def spr_cypress_knees():
    """Cypress knees: knobbly cones of root standing up out of the water round a bald cypress."""
    rng = np.random.default_rng(185)
    w, h = 48, 22
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x, kh in ((8, 12), (17, 19), (25, 10), (33, 16), (41, 8)):
        kh *= rng.uniform(0.85, 1.1)
        cv.polygon([(x - 4, h), (x - 1.5, h - kh), (x + 1, h - kh + 1.5), (x + 4, h)], z=0.0, top=1.0, bevel=2.0,
                   mat=0, tone=rng.normal(0, 0.05))
        cv.ellipse(x - 0.2, h - kh + 1, 1.6, 1.4, z=1.0, dome=0.6, mat=0, tone=0.05)
    return _prop(cv, [CYPRESS_BARK], relief=1.0, cavity=0.4, shadow=0.45)


def spr_cattails():
    """Cattails at the water's edge: long blades and stems, the brown velvet heads on top."""
    rng = np.random.default_rng(187)
    w, h = 36, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(14):                                         # blades
        x = rng.uniform(6, 30)
        L = rng.uniform(26, 50)
        lean = rng.normal(0, 5)
        cv.stroke([(x, h), (x + lean * 0.5, h - L * 0.6), (x + lean, h - L)], 1.5, z=rng.random(), dome=0.4,
                  taper=(1.0, 0.25), mat=0, tone=rng.normal(0, 0.05))
    for _ in range(5):                                          # stems and heads
        x = rng.uniform(9, 27)
        top = rng.uniform(4, 14)
        cv.stroke([(x, h), (x + rng.normal(0, 1), top + 9)], 0.9, z=1.2, dome=0.3, mat=0)
        cv.ellipse(x, top + 5, 1.8, 4.5, z=1.6, dome=0.9, mat=1)
        cv.stroke([(x, top + 0.5), (x, top - 3)], 0.6, z=1.6, dome=0.2, mat=0)
    return _prop(cv, [CATTAIL, CATTAIL_HEAD], relief=1.0, cavity=0.35, shadow=0.4)


def spr_heron():
    """A grey heron standing in the shallows: long legs, the neck drawn back in an S, a dagger of a
    beak, the black crest and the dark flight feathers folded along its back."""
    w, h = 44, 60
    cv = Canvas(w, h, wrap=False, ground=-9)
    for x in (19, 23):
        cv.stroke([(x, h), (x + 0.5, 34)], 1.1, z=0.0, dome=0.3, mat=2)                 # legs
    cv.ellipse(22, 28, 9, 6.5, z=0.6, dome=1.0, angle=-20, mat=0)                       # body
    cv.polygon([(14, 26), (30, 24), (36, 34), (22, 33)], z=1.0, top=0.6, bevel=1.5, mat=1, tone=-0.05)  # folded wing
    t = np.linspace(0, 1, 10)
    cv.stroke(list(zip(16 - 6 * np.sin(t * np.pi * 1.1), 24 - 14 * t)), 2.6, z=1.2, dome=0.8, taper=(1.3, 0.8),
              mat=0, tone=0.05)                                                          # the S of the neck
    cv.ellipse(13.5, 9.5, 3.0, 2.4, z=1.6, dome=0.9, mat=0, tone=0.08)                  # head
    cv.polygon([(14, 8.6), (3, 10.5), (14, 11.0)], z=2.0, top=0.5, bevel=0.6, mat=2)    # beak
    cv.stroke([(15, 8.5), (21, 6.5)], 0.9, z=2.1, dome=0.2, mat=1)                       # crest
    cv.ellipse(12.4, 9.0, 0.6, 0.6, z=2.3, dome=0.2, mat=1)                              # eye
    return _prop(cv, [HERON, HERON_DARK, BEAK_YELLOW], relief=1.0, cavity=0.35, shadow=0.45)


def spr_alligator():
    """An alligator lying in the water with only its back showing: the long snout with the nostrils
    raised on its tip, the eyes standing up behind it - pale gold, catching any light - and a row
    of ridged scutes down its back. Stand it in a sunken water cell."""
    rng = np.random.default_rng(189)
    w, h = 96, 18
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(30, h - 1, 26, 4.5, z=0.0, dome=0.7, mat=0)                               # the head and snout
    cv.ellipse(8, h - 2.5, 3.0, 2.2, z=0.6, dome=0.8, mat=0)                              # nostrils
    for x in (36, 44):
        cv.ellipse(x, h - 6, 3.4, 3.0, z=0.8, dome=1.0, mat=0)                            # eye bumps
        cv.ellipse(x - 0.6, h - 6.6, 1.4, 1.1, z=1.4, dome=0.4, mat=1)                    # the eyes
    for k in range(9):                                                                   # the back, in scutes
        x = 58 + k * 4.2
        cv.ellipse(x, h - 1, 2.6, 2.8 + rng.uniform(-0.5, 0.5), z=0.3, dome=0.9, mat=0, tone=rng.normal(0, 0.05))
    em = ((cv.mat == 1) & (cv.id > 0)).astype(np.float32) * 0.6
    return _prop(cv, [GATOR, EYE], relief=1.0, cavity=0.4, shadow=0.4, em=em)


def spr_fireflies():
    """Fireflies over the water at night: a loose swarm of tiny lights, some brighter than others.
    Glowing and additive; float it with `z`."""
    rng = np.random.default_rng(191)
    w, h = 64, 64
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    col = np.array(FIREFLY[-2], np.float32)
    for _ in range(26):
        x, y = rng.normal(32, 13), rng.normal(32, 12)
        if not (2 <= x < w - 2 and 2 <= y < h - 2):
            continue
        b = rng.uniform(0.5, 1.0)
        x, y = int(x), int(y)
        rgba[y, x, :3] = col * b
        rgba[y, x, 3] = 1.0
        em[y, x] = 1.0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):                                 # a soft halo
            rgba[y + dy, x + dx, :3] = np.maximum(rgba[y + dy, x + dx, :3], col * b * 0.4)
            rgba[y + dy, x + dx, 3] = 1.0
            em[y + dy, x + dx] = max(em[y + dy, x + dx], 0.4)
    return rgba, em


SWAMP_CARDS = {1: 1.4, 2: 3.0, 3: 3.9, 4: 4.6}       # each layer's height


def _swamp_card(layer):
    """One layer of a swamp's edge, 1 (front) to 4 (back): cattails, knees and reeds at the water's
    edge; then a few young cypresses among cattails; then a looser stand of cypresses hung with moss;
    then a dense stand of tall ones, darker as they go back."""
    from assets import get_sprite
    rng = np.random.default_rng(600 + layer)
    height = SWAMP_CARDS[layer]
    H = int(height * CARD_PX)
    card = np.zeros((H, CARD_W, 4), np.float32)
    plan = {1: {'cattails': 9, 'cypress_knees': 5, 'reeds': 4},
            2: {'bald_cypress': 2, 'cattails': 6, 'cypress_knees': 3},
            3: {'bald_cypress': 5, 'cattails': 4, 'cypress_knees': 2},
            4: {'bald_cypress': 12, 'cattails': 4}}[layer]
    tall = {'bald_cypress': {2: (1.6, 2.8), 3: (2.2, 3.7)}.get(layer, (3.0, 4.4)), 'cattails': (0.7, 1.1),
            'cypress_knees': (0.25, 0.4), 'reeds': (0.5, 0.8)}
    stamps = []
    for kind, k in plan.items():
        lo, hi = tall[kind]
        off = rng.uniform(0, CARD_W)
        for i in range(k):
            x = (off + (i + rng.uniform(0.15, 0.85)) * CARD_W / k) % CARD_W
            stamps.append((x, kind, rng.uniform(lo, min(hi, height - 0.15))))
    for x, kind, tl in sorted(stamps, key=lambda s: -s[2]):
        _stamp(card, get_sprite(kind)[0], x, H, tl, flip=bool(rng.random() < 0.5))
    card[..., :3] *= {1: 1.0, 2: 0.9, 3: 0.8, 4: 0.7}[layer]
    card[..., 3] = (card[..., 3] > 0.5).astype(np.float32)
    return card, np.zeros(card.shape[:2], np.float32)


TEXTURES = {
    'swamp_water': lambda n: (tex_swamp_water(n), None),
    'bog': lambda n: (tex_bog(n), None),
    'swamp_deep': lambda n: (tex_swamp_deep(n), None),
}
TEXTURE_NOISE = {'swamp_water': 0.6, 'bog': 2.2, 'swamp_deep': 1.6}
TEXTURE_REFLECT = {'swamp_water': 0.42}
SPRITES = {'bald_cypress': spr_bald_cypress, 'spanish_moss': spr_spanish_moss, 'cypress_knees': spr_cypress_knees,
           'cattails': spr_cattails, 'heron': spr_heron, 'alligator': spr_alligator, 'fireflies': spr_fireflies}
SPRITES.update({f'swamp_card_{k}': (lambda k=k: _swamp_card(k)) for k in SWAMP_CARDS})
SPRITE_HEIGHT = {'bald_cypress': 4.2, 'spanish_moss': 1.4, 'cypress_knees': 0.3, 'cattails': 1.0, 'heron': 0.95,
                 'alligator': 0.2, 'fireflies': 1.2, **{f'swamp_card_{k}': h for k, h in SWAMP_CARDS.items()}}
PROP_DEFAULTS = {'fireflies': {'blend': 'additive', 'shadow': False}}
NO_CONTACT_SHADOW = {'spanish_moss', 'fireflies', 'alligator'}
FRINGES = {'swamp': ['swamp_card_4', 'swamp_card_3', 'swamp_card_2', 'swamp_card_1']}
DEBRIS_SETS = {'swamp': ['cattails', 'cattails', 'reeds', 'cypress_knees', 'rocks']}

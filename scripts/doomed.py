"""Doomed: an homage to the first-person shooters of 1993 - their stone status bar along the bottom of
the screen, the face in the middle of it that gets bloodier as health runs down, the gun held out in
the middle of the view, and the slime pits, hex floors and green tech walls of their first level.

Everything here is drawn fresh in code (the pixel-art toolkit, scripts/pixelart.py, and small
hand-made bitmap fonts): no artwork from any game is used. The status bar is a GUI widget
(`statusbar` in scripts/gui.py), the guns are viewmodels (`pistol`, `shotgun` in scripts/icons.py),
and the level's textures and props merge into the asset tables like any other module.
"""
import numpy as np

from biomes import T, _prop, _rng, _tile
from pixelart import Canvas, dither, outline_sprite, ramp, smooth_noise

# ---------------------------------------------------------------- bitmap fonts

BIG = {   # 6x8, drawn at twice the size: chunky red numbers
    '0': ['.####.', '##..##', '##.###', '###.##', '##..##', '##..##', '##..##', '.####.'],
    '1': ['..##..', '.###..', '####..', '..##..', '..##..', '..##..', '..##..', '######'],
    '2': ['.####.', '##..##', '....##', '...##.', '..##..', '.##...', '##....', '######'],
    '3': ['#####.', '....##', '....##', '.####.', '....##', '....##', '##..##', '.####.'],
    '4': ['...##.', '..###.', '.####.', '##.##.', '######', '...##.', '...##.', '...##.'],
    '5': ['######', '##....', '##....', '#####.', '....##', '....##', '##..##', '.####.'],
    '6': ['..###.', '.##...', '##....', '#####.', '##..##', '##..##', '##..##', '.####.'],
    '7': ['######', '....##', '...##.', '...##.', '..##..', '..##..', '..##..', '..##..'],
    '8': ['.####.', '##..##', '##..##', '.####.', '##..##', '##..##', '##..##', '.####.'],
    '9': ['.####.', '##..##', '##..##', '##..##', '.#####', '....##', '...##.', '.###..'],
    '%': ['##..#', '##.##', '..##.', '.##..', '##.##', '#..##', '.....', '.....'],
    '-': ['......', '......', '......', '######', '######', '......', '......', '......'],
}
SMALL = {  # 3x5: the ammo table, the arms grid and the labels
    '0': ['###', '#.#', '#.#', '#.#', '###'], '1': ['.#.', '##.', '.#.', '.#.', '###'],
    '2': ['###', '..#', '###', '#..', '###'], '3': ['###', '..#', '.##', '..#', '###'],
    '4': ['#.#', '#.#', '###', '..#', '..#'], '5': ['###', '#..', '###', '..#', '###'],
    '6': ['###', '#..', '###', '#.#', '###'], '7': ['###', '..#', '.#.', '.#.', '.#.'],
    '8': ['###', '#.#', '###', '#.#', '###'], '9': ['###', '#.#', '###', '..#', '###'],
    '/': ['..#', '..#', '.#.', '#..', '#..'],
    'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'B': ['##.', '#.#', '##.', '#.#', '##.'],
    'C': ['###', '#..', '#..', '#..', '###'], 'E': ['###', '#..', '##.', '#..', '###'],
    'H': ['#.#', '#.#', '###', '#.#', '#.#'], 'K': ['#.#', '#.#', '##.', '#.#', '#.#'],
    'L': ['#..', '#..', '#..', '#..', '###'], 'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'],
    'O': ['###', '#.#', '#.#', '#.#', '###'], 'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['###', '#..', '###', '..#', '###'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'], ' ': ['.', '.', '.', '.', '.'],
}


def _glyph(table, ch):
    rows = table.get(ch, table.get(' ', ['.']))
    return np.array([[c == '#' for c in r] for r in rows], bool)


def _text_mask(table, s, gap=1):
    gl = [_glyph(table, c) for c in s]
    h = max(g.shape[0] for g in gl)
    w = sum(g.shape[1] for g in gl) + gap * (len(gl) - 1)
    m = np.zeros((h, max(1, w)), bool)
    x = 0
    for g in gl:
        m[:g.shape[0], x:x + g.shape[1]] = g
        x += g.shape[1] + gap
    return m


def _stamp(rgb, mask, x, y, colors, shadow=(0.08, 0.02, 0.02)):
    """Paint a mask at (x, y): `colors` is one colour or one per row (a gradient), with a one-pixel
    shadow down and to the right."""
    h, w = mask.shape
    H, W = rgb.shape[:2]
    cols = np.asarray(colors, np.float32)
    if cols.ndim == 1:
        cols = np.repeat(cols[None, :], h, 0)
    for dy, dx, c in ((1, 1, None), (0, 0, 'ink')):
        for r in range(h):
            yy = y + r + dy
            if not 0 <= yy < H:
                continue
            for q in np.nonzero(mask[r])[0]:
                xx = x + q + dx
                if 0 <= xx < W:
                    rgb[yy, xx] = shadow if c is None else cols[r]


# ---------------------------------------------------------------- the face

SKIN = ramp('#b8794c', dark=0.32, light=1.3, warm=0.12)
HAIR = ramp('#4a3018', dark=0.4, light=1.5)
DARK = ramp('#24160e', dark=0.6, light=1.8)
EYE = ramp('#e2dccc', dark=0.6, light=1.05)
LIP = ramp('#8a4434', dark=0.4, light=1.3)
BLOOD = ramp('#a01810', dark=0.4, light=1.25)


def face(health=100, expression=None, look=0):
    """A gruff face for the middle of the status bar, 24x30: cropped hair, heavy brows, a broken nose.
    It takes damage as `health` falls - a cut over the eye, then blood running from it, a black
    eye and a split lip, then blood everywhere - and has a few `expression`s: calm, grin (teeth
    showing, brows down), ouch (mouth open, eyes wide) and dead. `look` -1/1 turns the eyes."""
    rng = np.random.default_rng(77)
    expression = expression or ('dead' if health <= 0 else 'calm')
    w, h = 24, 30
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(8, 23, 8, 7, z=0.3, top=0.6, bevel=1.5, mat=0, tone=-0.12)                     # the neck
    cv.ellipse(2.8, 15.5, 1.7, 2.8, z=0.4, dome=0.8, mat=0, tone=-0.05)                    # ears
    cv.ellipse(21.2, 15.5, 1.7, 2.8, z=0.4, dome=0.8, mat=0, tone=-0.08)
    cv.ellipse(12, 15, 9.2, 11.6, z=0.6, dome=2.6, mat=0)                                  # the head
    cv.polygon([(2.6, 12.5), (2.8, 6), (6, 2.2), (12, 1.0), (18, 2.2), (21.2, 6), (21.4, 12.5), (19.5, 9.2),
                (16, 7.4), (12, 7.9), (8, 7.4), (4.5, 9.2)], z=2.6, top=0.8, bevel=1.5, mat=1)  # cropped hair
    for x in range(4, 21, 2):                                                              # its texture
        cv.stroke([(x, 2.5 + abs(x - 12) * 0.25), (x + 0.5, 6.5)], 0.6, z=0, dome=0.3, mode='carve')
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    jaw = (cv.mat == 0) & (yy > 18) & (cv.id > 0)
    cv.tone[jaw & (rng.random((h, w)) < 0.45)] -= 0.12                                     # stubble
    cv.tone[(cv.mat == 0) & (np.abs(xx - 12) > 6.5) & (yy > 12) & (yy < 24)] -= 0.08       # cheeks turn away
    brow_y = 10.2 if expression != 'grin' else 10.6
    tilt = 0.9 if expression == 'grin' else (-0.6 if expression == 'ouch' else 0.0)
    cv.stroke([(6.0, brow_y - tilt), (10.4, brow_y + tilt * 0.6)], 1.6, z=3.0, dome=0.4, mat=2)   # brows
    cv.stroke([(13.6, brow_y + tilt * 0.6), (18.0, brow_y - tilt)], 1.6, z=3.0, dome=0.4, mat=2)
    eye_h = 1.25 if expression == 'ouch' else 0.85
    if expression != 'dead':
        for ex in (8.2, 15.8):                                                             # eyes
            cv.ellipse(ex, 12.8, 1.7, eye_h, z=2.2, dome=0.2, mat=3)
            cv.put(np.array([12, 13]) if expression == 'ouch' else np.array([12]),
                   np.array([int(ex + look * 0.9)]), np.ones((2 if expression == 'ouch' else 1, 1), bool), 3.0, mat=2)
    else:
        for ex in (8.2, 15.8):
            cv.stroke([(ex - 1.6, 12.9), (ex + 1.6, 12.9)], 0.8, z=2.6, dome=0.1, mat=2)
    cv.stroke([(12, 11.5), (11.6, 15.5), (12.6, 17.2)], 2.6, z=1.2, dome=1.0, mode='add')   # the nose, broken
    for nx in (10.9, 13.3):
        cv.ellipse(nx, 17.6, 0.7, 0.5, z=0, dome=0.5, mode='carve')
    if expression == 'grin':                                                               # the mouth
        cv.stroke([(8.0, 20.6), (12, 21.6), (16.0, 20.6)], 2.4, z=2.4, dome=0.3, mat=2)
        cv.stroke([(8.8, 20.6), (12, 21.3), (15.2, 20.6)], 1.1, z=2.8, dome=0.1, mat=3)
    elif expression == 'ouch':
        cv.ellipse(12, 21.6, 2.4, 2.0, z=2.4, dome=0.2, mat=2)
    else:
        cv.stroke([(9.0, 21.2), (12, 21.5), (15.0, 21.0)], 1.2, z=2.4, dome=0.2, mat=4)
    blood = np.zeros((h, w), bool)
    if health < 80:                                                                        # a cut over the eye
        blood |= (np.abs(xx - 16.5) < 1.0) & (np.abs(yy - 9.3) < 0.6)
    if health < 60:                                                                        # blood runs from it
        run = 16.8 + 0.3 * (yy - 9)
        blood |= (np.abs(xx - run) < 0.55) & (yy > 9) & (yy < 18)
        blood |= (np.abs(xx - 12.3) < 0.9) & (yy > 17.6) & (yy < 20.5)                     # and the nose
    if health < 40:
        shiner = ((xx - 15.8) / 2.4) ** 2 + ((yy - 13.0) / 1.9) ** 2 < 1                   # a black eye
        cv.tone[shiner & (cv.mat == 0)] -= 0.22
        blood |= (np.abs(xx - 9.4) < 0.7) & (yy > 21) & (yy < 23.5)                        # a split lip
        blood |= (((xx - 5.5) / 2.0) ** 2 + ((yy - 7.6) / 1.4) ** 2 < 1)                    # the scalp
    if health < 20:
        splash = smooth_noise(w, h, 4, rng, wrap=False) > 0.55
        blood |= splash & (cv.mat == 0) & (yy > 6) & (yy < 23)
    cv.mat[blood & (cv.id > 0)] = 5
    rgba = cv.paint([SKIN, HAIR, DARK, EYE, LIP, BLOOD], cv.light(relief=1.2, cavity=0.4, shadow=0.35), dither=0.25)
    return outline_sprite(rgba, darken=0.5)


# ---------------------------------------------------------------- the status bar

STONE = np.array([0.46, 0.45, 0.43], np.float32)
RED = [np.array(c, np.float32) for c in ((1.0, 0.42, 0.28), (0.98, 0.26, 0.16), (0.86, 0.14, 0.08), (0.72, 0.09, 0.05),
                                          (0.58, 0.06, 0.04))]
YELLOW = np.array([0.98, 0.82, 0.24], np.float32)
GREY_TXT = np.array([0.74, 0.72, 0.68], np.float32)
KEY_COLORS = {'blue': (0.3, 0.45, 1.0), 'yellow': (1.0, 0.85, 0.2), 'red': (0.95, 0.2, 0.15)}


def _stone(w, h, seed=5):
    """A slab of grey stone: mottled, flecked, cut by a few dark cracks."""
    rng = np.random.default_rng(seed)
    v = 1.0 + 0.16 * (smooth_noise(w, h, max(2, w // 26), rng, wrap=False) - 0.5) \
        + 0.1 * (smooth_noise(w, h, max(2, w // 7), rng, wrap=False) - 0.5) + 0.07 * (rng.random((h, w)) - 0.5)
    for _ in range(max(2, w // 40)):                                                        # cracks
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        for _ in range(int(rng.integers(6, 18))):
            if 0 <= int(y) < h and 0 <= int(x) < w:
                v[int(y), int(x)] *= 0.62
            x += rng.choice([-1, 0, 1, 1])
            y += rng.choice([-1, 0, 1])
    return (STONE[None, None, :] * v[..., None]).clip(0, 1)


def _inset(rgb, x0, y0, x1, y1, depth=0.72):
    """A recessed panel: darker inside, a shadowed top and left edge, a lit bottom and right edge."""
    rgb[y0:y1, x0:x1] *= depth
    rgb[y0, x0:x1] *= 0.45
    rgb[y0:y1, x0] *= 0.45
    rgb[y1 - 1, x0:x1] = np.minimum(rgb[y1 - 1, x0:x1] * 1.5 + 0.05, 1)
    rgb[y0:y1, x1 - 1] = np.minimum(rgb[y0:y1, x1 - 1] * 1.5 + 0.05, 1)


def _big_number(rgb, s, x_right, y, scale=2):
    """Big red digits ending at x_right, a gradient from bright to dark down each glyph."""
    m = _text_mask(BIG, s, gap=1)
    if scale != 1:
        m = np.repeat(np.repeat(m, scale, 0), scale, 1)
    rows = m.shape[0]
    grad = [RED[min(len(RED) - 1, int(r / rows * len(RED)))] for r in range(rows)]
    _stamp(rgb, m, x_right - m.shape[1], y, grad, shadow=(0.12, 0.02, 0.02))
    return m.shape[1]


def _small(rgb, s, x, y, color, right=False):
    m = _text_mask(SMALL, s, gap=1)
    x = x - m.shape[1] if right else x
    shade = [np.asarray(color, np.float32) * f for f in (1.08, 1.0, 0.92, 0.82, 0.72)]
    _stamp(rgb, m, x, y, [np.clip(c, 0, 1) for c in shade], shadow=(0.06, 0.05, 0.05))
    return m.shape[1]


def statusbar(width, height, p):
    """The whole status bar as an RGB image `width` x `height` (drawn on a 320 x 32 plan and
    stretched to the screen's width): ammo, health, arms, the face, armour, keys and the ammo
    table. `p` is the widget's entry - see gui.w_statusbar."""
    W, H = 320, 32
    rgb = _stone(W, H, int(p.get('seed', 5)))
    rgb[0, :] = np.minimum(rgb[0, :] * 1.4, 1)                                              # the top lip
    rgb[1, :] *= 0.55
    for x0, x1 in ((2, 46), (48, 104), (106, 142), (144, 176), (178, 236), (238, 248), (250, 318)):
        _inset(rgb, x0, 3, x1, 31)
    ammo = p.get('ammo', 50)
    health = int(p.get('health', 100))
    armor = int(p.get('armor', 0))
    if ammo is not None and ammo != '':
        _big_number(rgb, str(ammo), 43, 5)
    _big_number(rgb, '%d%%' % health, 102, 5)
    _big_number(rgb, '%d%%' % armor, 234, 5)
    for label, x0, x1 in (('AMMO', 2, 46), ('HEALTH', 48, 104), ('ARMS', 106, 142), ('ARMOR', 178, 236)):
        lw = _text_mask(SMALL, label).shape[1]
        _small(rgb, label, x0 + (x1 - x0 - lw) // 2, 24, GREY_TXT)
    owned = set(int(a) for a in p.get('arms', [2]))
    for k, n in enumerate(range(2, 8)):                                                     # the arms grid
        x, y = 113 + (k % 3) * 9, 6 + (k // 3) * 8
        _small(rgb, str(n), x, y, YELLOW if n in owned else GREY_TXT * 0.62)
    rgb[4:30, 145:175] = rgb[4:30, 145:175] * 0.4                                           # the face's box
    keys = p.get('keys', [])
    for k, key in enumerate(('blue', 'yellow', 'red')):
        if key in keys:
            c = np.array(KEY_COLORS[key], np.float32)
            y = 6 + k * 8
            rgb[y:y + 5, 240:246] = c * 0.8
            rgb[y, 240:246] = np.minimum(c * 1.2, 1)
            rgb[y + 4, 240:246] = c * 0.45
    table = p.get('ammo_table', [[50, 200], [0, 50], [0, 50], [0, 300]])
    for k, label in enumerate(('BULL', 'SHEL', 'RCKT', 'CELL')):
        y = 6 + k * 6
        _small(rgb, label, 253, y, GREY_TXT)
        cur, mx = (table[k] + [0, 0])[:2] if k < len(table) else (0, 0)
        _small(rgb, str(int(cur)), 293, y, YELLOW, right=True)
        _small(rgb, '/', 295, y, GREY_TXT)
        _small(rgb, str(int(mx)), 316, y, YELLOW, right=True)
    expression = p.get('face')
    if expression == 'auto':
        expression = None
    fc = face(health, expression, int(p.get('look', 0)))
    fa = fc[..., 3:4]
    region = rgb[2:32, 148:172]
    region[:] = region * (1 - fa) + fc[..., :3] * fa
    rgb = np.clip(rgb, 0, 1)
    if (width, height) != (W, H):
        from PIL import Image
        im = Image.fromarray((rgb * 255).astype(np.uint8)).resize((width, height), Image.NEAREST)
        rgb = np.asarray(im, np.float32) / 255
    return rgb


# ---------------------------------------------------------------- the guns (first-person viewmodels)

GUNMETAL = ramp('#3e4046', dark=0.45, light=1.6, cool=0.1)
SLEEVE = ramp('#4a5236', dark=0.4, light=1.4)
GRIP = ramp('#2a2420', dark=0.5, light=1.6)
WOODEN = ramp('#6a4024', dark=0.35, light=1.45, warm=0.12)


def _flash(rgba, em, cx, cy, size):
    """A muzzle flash: a ragged star of yellow-white fire with orange tips, glowing."""
    h, w = em.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    th = np.arctan2(yy - cy, xx - cx)
    r = np.hypot(xx - cx, yy - cy)
    reach = size * (0.55 + 0.45 * np.abs(np.cos(th * 3.5)) ** 3)
    m = r < reach
    core = r < reach * 0.5
    rgba[m, :3] = (1.0, 0.62, 0.18)
    rgba[core, :3] = (1.0, 0.95, 0.7)
    rgba[m, 3] = 1.0
    em[m] = 1.0


def vm_pistol(fire=False):
    """A pistol held out in the middle of the view from below: a fist round the grip, the slide seen
    from behind with its rear sight, the top of it running away to the front sight. `fire` adds a
    flash at the muzzle."""
    w, h = 56, 66
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(15, 66), (41, 66), (37, 50), (19, 50)], z=0.2, top=1.4, bevel=3.0, mat=0)   # the sleeve
    cv.box(23, 33, 10, 12, z=0.8, top=0.8, bevel=1.5, mat=2)                                # the grip
    cv.polygon([(20, 30), (36, 30), (32.5, 8), (23.5, 8)], z=1.2, top=1.0, bevel=1.5, mat=1, tone=0.12)  # slide
    cv.box(20, 21, 16, 12, z=1.6, top=0.8, bevel=1.5, mat=1)                                # its back face
    for x in range(22, 35, 2):                                                             # serrations
        cv.stroke([(x, 23.5), (x, 31)], 0.6, z=0, dome=0.3, mode='carve')
    for x0 in (20.5, 33.5):                                                                # rear sight
        cv.box(x0, 18, 2, 3.5, z=2.0, top=0.5, bevel=0.6, mat=1, tone=-0.1)
    cv.box(27.3, 5.5, 1.4, 3, z=1.8, top=0.4, bevel=0.5, mat=1, tone=0.1)                   # front sight
    cv.ellipse(28, 43.5, 11.5, 7.5, z=2.0, dome=1.6, mat=3)                                 # the fist
    for y in (41.5, 44.5, 47.5):                                                           # fingers
        cv.stroke([(18, y), (38, y + 0.6)], 0.8, z=0, dome=0.4, mode='carve')
    cv.ellipse(36.0, 38.5, 3.4, 2.5, z=2.6, dome=0.8, mat=3, tone=0.06)                     # the thumb
    rgba = cv.paint([SLEEVE, GUNMETAL, GRIP, SKIN], cv.light(sun=(-0.25, -0.8, 0.7), relief=1.1, cavity=0.4,
                                                               shadow=0.4), dither=0.2)
    rgba = outline_sprite(rgba, darken=0.5)
    em = np.zeros((h, w), np.float32)
    if fire:
        _flash(rgba, em, 28, 3.5, 7.5)
    return rgba.astype(np.float32), em


def vm_shotgun(fire=False):
    """A pump shotgun in the middle of the view: the receiver at the bottom, the barrel running away up
    to its bead sight, the wooden pump round the magazine tube under it, a hand on the pump.
    `fire` adds a flash at the muzzle."""
    w, h = 84, 78
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(30, 78), (54, 78), (52, 50), (32, 50)], z=0.4, top=1.2, bevel=2.5, mat=1)     # the receiver
    cv.stroke([(42, 52), (42, 6)], 9.0, z=1.0, dome=1.4, taper=(1.0, 0.55), mat=1)            # the barrel
    cv.stroke([(42, 50), (42, 9)], 1.2, z=2.0, dome=0.3, taper=(1.0, 0.5), mat=1, tone=0.18)  # its rib
    cv.polygon([(30, 46), (54, 46), (50.5, 23), (33.5, 23)], z=1.8, top=1.4, bevel=2.5, mat=2, tone=-0.06)  # pump
    for y in range(26, 43, 3):                                                             # its grooves
        cv.stroke([(33, y), (51, y)], 0.7, z=0, dome=0.3, mode='carve')
    cv.ellipse(42, 4.5, 1.4, 1.4, z=2.2, dome=0.5, mat=1, tone=0.3)                          # bead sight
    cv.ellipse(30, 36, 6, 8.5, z=2.6, dome=1.4, mat=3)                                       # the hand on the pump
    for y in (31, 34.5, 38, 41.5):
        cv.stroke([(25, y), (35, y + 0.8)], 0.7, z=0, dome=0.4, mode='carve')
    cv.polygon([(0, 78), (22, 78), (30, 44), (16, 46)], z=0.4, top=1.2, bevel=2.5, mat=0)     # its sleeve
    rgba = cv.paint([SLEEVE, GUNMETAL, WOODEN, SKIN], cv.light(sun=(-0.25, -0.8, 0.7), relief=1.1, cavity=0.4,
                                                                shadow=0.4), dither=0.2)
    rgba = outline_sprite(rgba, darken=0.5)
    em = np.zeros((h, w), np.float32)
    if fire:
        _flash(rgba, em, 42, 4.0, 9.5)
    return rgba.astype(np.float32), em


# ---------------------------------------------------------------- the level: textures

SLIME = ramp('#38a02a', dark=0.32, light=1.6, cool=0.0)
HEX_BROWN = ramp('#7a5434', dark=0.34, light=1.32, warm=0.12)
GREEN_PANEL = ramp('#4e6634', dark=0.32, light=1.38)
TRIM_BROWN = ramp('#6e4c2c', dark=0.32, light=1.4, warm=0.12)
CEIL_GREY = ramp('#6e685c', dark=0.38, light=1.3)
EDGE_BROWN = ramp('#5e4a34', dark=0.34, light=1.35)


def tex_nukage(name):
    """Toxic slime: a bright green sludge in slow swirls, paler veins running through it and darker
    clots. It glows - sink it with `drop` and it lights the room green from below."""
    rng = _rng(name)
    swirl = smooth_noise(T, T, 3, rng) * 0.55 + smooth_noise(T, T, 7, rng) * 0.45
    veins = np.exp(-(((swirl * 6.0) % 1.0) - 0.5) ** 2 / 0.012)
    clots = smooth_noise(T, T, 9, rng) > 0.7
    v = np.clip(0.42 + 0.35 * (swirl - 0.5) + 0.42 * veins - 0.25 * clots, 0, 1)
    return dither(v, SLIME, 0.6), (0.5 + 0.45 * v).astype(np.float32)


def tex_hex_floor(name):
    """A floor of brown hexagonal tiles, each a slightly different shade and worn at its edges, dark
    grout between them."""
    rng = _rng(name)
    cx = np.array([16 * i + 8 * (j % 2) for j in range(4) for i in range(4)], np.float32) + 8
    cy = np.array([16 * j for j in range(4) for i in range(4)], np.float32) + 8
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    dx = np.abs(xx[..., None] - cx)
    dy = np.abs(yy[..., None] - cy) * 1.15
    d = np.hypot(np.minimum(dx, T - dx), np.minimum(dy, T * 1.15 - dy))
    order = np.argsort(d, axis=-1)
    d1 = np.take_along_axis(d, order[..., :1], -1)[..., 0]
    d2 = np.take_along_axis(d, order[..., 1:2], -1)[..., 0]
    edge = d2 - d1
    tone = rng.normal(0, 0.06, len(cx))[order[..., 0]]
    wear = 0.08 * (smooth_noise(T, T, 8, rng) - 0.5)
    v = 0.56 + tone + wear + 0.1 * np.clip((edge - 1.0) / 6.0, 0, 1)
    v = np.where(edge < 1.1, 0.12, v)
    return dither(np.clip(v, 0, 1), HEX_BROWN, 0.5)


def _green_panel(rng):
    """Green metal plating in vertical strakes of different shades, darker toward the floor."""
    cols = np.cumsum(rng.integers(2, 6, 40))
    shade = np.zeros(T, np.float32)
    k = 0
    for x in range(T):
        while k < len(cols) - 1 and x >= cols[k]:
            k += 1
        shade[x] = 0.08 * np.sin(k * 2.4) + rng.normal(0, 0.015)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    v = 0.52 + shade[None, :] + 0.08 * (smooth_noise(T, T, 6, rng) - 0.5)
    for x in range(0, T, 32):                                                              # panel seams
        v[:, x] = 0.18
        v[:, (x + 1) % T] = 0.66
    for _ in range(10):                                                                    # streaks of grime
        x = int(rng.integers(0, T))
        y0 = int(rng.integers(0, T))
        n = int(rng.integers(8, 30))
        for y in range(y0, y0 + n):
            v[y % T, x] -= 0.12 * (1 - (y - y0) / n)
    return v


def tex_green_tech(name):
    """Tech walls in green plating: vertical strakes of different shades, panel seams, streaks of
    grime running down."""
    rng = _rng(name)
    return dither(np.clip(_green_panel(rng), 0, 1), GREEN_PANEL, 0.5)


def tex_green_trim(name):
    """The green plating under a band of brown metal at the top of each storey, a row of pale teeth
    along the band - stack it storey on storey for walls banded like a 1993 tech base."""
    rng = _rng(name)
    v = np.clip(_green_panel(rng), 0, 1)
    rgb = dither(v, GREEN_PANEL, 0.5)
    yy, xx = np.mgrid[0:16, 0:T].astype(np.float32) + 0.5
    band = np.full((16, T), 0.5, np.float32)
    band[0:2] = 0.82
    band[14:16] = 0.2
    tooth = ((xx % 8) - 4)
    teeth = (yy > 4) & (yy < 12) & (np.abs(tooth) < (12 - yy) * 0.55)
    band[teeth] = 0.78
    band[(yy > 4) & (yy < 12) & (np.abs(tooth) >= (12 - yy) * 0.55) & (np.abs(tooth) < (12 - yy) * 0.55 + 1)] = 0.3
    rgb[:16] = dither(np.clip(band + 0.04 * (rng.random((16, T)) - 0.5), 0, 1), TRIM_BROWN, 0.4)
    return rgb


def tex_green_window(name):
    """The trimmed green wall with a window cut through it (see-through): a deep dark frame round an
    opening onto whatever is outside."""
    rgb = tex_green_trim(name + 't').copy()
    yy, xx = np.mgrid[0:T, 0:T]
    opening = (yy >= 22) & (yy < 58) & (xx >= 3) & (xx < 61)
    rim = ~opening & (yy >= 19) & (yy < 61) & (xx >= 1) & (xx < 63)
    rgb[rim] = rgb[rim] * 0.4
    rgb[(yy == 58) & (xx >= 3) & (xx < 61)] = np.array(GREEN_PANEL[4], np.float32)
    return rgb, None, (~opening).astype(np.float32)


def tex_tech_ceiling(name):
    """Ceiling tiles in a grid: grey-brown squares, each a shade of its own, dark lines between."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    tile = (yy // 16) * 4 + (xx // 16)
    tone = rng.normal(0, 0.05, 16)[tile]
    v = 0.55 + tone + 0.06 * (smooth_noise(T, T, 8, rng) - 0.5)
    v = np.where((yy % 16 == 0) | (xx % 16 == 0), 0.2, v)
    v = np.where((yy % 16 == 1) | (xx % 16 == 1), v + 0.12, v)
    return dither(np.clip(v, 0, 1), CEIL_GREY, 0.5)


def tex_slime_edge(name):
    """The edge of a walkway down into the slime: brown metal plates, stained green toward the
    bottom where the sludge laps at them."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    v = 0.5 + 0.06 * (smooth_noise(T, T, 8, rng) - 0.5) + 0.03 * (rng.random((T, T)) - 0.5)
    v = np.where(xx % 32 == 0, 0.2, v)
    rgb = dither(np.clip(v, 0, 1), EDGE_BROWN, 0.5)
    stain = (yy / T) ** 2 * (0.7 + 0.3 * smooth_noise(T, T, 6, rng))
    rgb = rgb * (1 - stain[..., None] * 0.6) + np.array([0.25, 0.6, 0.15], np.float32) * stain[..., None] * 0.6
    return np.clip(rgb, 0, 1)


# ---------------------------------------------------------------- the level: props

DRUM = ramp('#4a5246', dark=0.38, light=1.5)
OOZE = ramp('#5ad83a', dark=0.45, light=1.25)
OLIVE = ramp('#5a6440', dark=0.35, light=1.4)
GORE = ramp('#7a1410', dark=0.4, light=1.4)
WHITE_BOX = ramp('#d8d8d0', dark=0.5, light=1.1)
BRASS = ramp('#c09a3a', dark=0.4, light=1.25)


def spr_toxic_barrel():
    """A steel drum of toxic waste: ribbed and dented, green sludge brimming over the rim and running
    down its sides, glowing."""
    rng = np.random.default_rng(611)
    w, h = 30, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(3, 6, 24, 33, z=0.4, top=2.2, bevel=7.0, mat=0)                                  # the drum
    for y in (14, 27):
        cv.stroke([(3, y), (27, y)], 1.6, z=0.6, dome=0.5, mode='add')                       # ribs
    cv.ellipse(15, 6.5, 12, 3.6, z=2.6, dome=0.6, mat=1, tone=0.15)                          # brimming over
    for x in (6, 10.5, 19, 24):                                                            # running down
        L = rng.uniform(5, 14)
        cv.stroke([(x, 7), (x + rng.normal(0, 0.6), 7 + L)], rng.uniform(1.4, 2.4), z=2.4, dome=0.5,
                  taper=(1.2, 0.6), mat=1)
    cv.ellipse(10, 33, 1.6, 2.2, z=2.0, dome=0.4, mode='carve')                              # a dent
    rgba = cv.paint([DRUM, OOZE], cv.light(relief=1.0, cavity=0.35, shadow=0.4), dither=0.25)
    rgba = outline_sprite(rgba)
    em = np.where((cv.mat == 1) & (cv.id > 0), 0.85, 0.0).astype(np.float32)
    return rgba.astype(np.float32), em


def spr_corpse():
    """A fallen soldier lying on his side in a pool of his own blood: boots, olive fatigues, an arm
    flung out, the helmet rolled off."""
    rng = np.random.default_rng(613)
    w, h = 56, 18
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(28, 15.5, 26, 2.6, z=0.0, dome=0.3, rough=0.25, rng=rng, mat=2)              # the pool
    cv.stroke([(8, 12), (20, 12.5)], 4.4, z=0.6, dome=0.8, mat=0, tone=-0.06)               # legs
    cv.ellipse(6, 12.5, 2.6, 2.2, z=0.8, dome=0.6, mat=3)                                   # boots
    cv.ellipse(30, 11.5, 11, 4.4, z=0.8, dome=1.2, mat=0)                                   # the torso
    cv.stroke([(32, 9), (40, 5), (45, 8)], 2.4, z=1.2, dome=0.6, mat=0)                      # an arm flung out
    cv.ellipse(46, 8.8, 1.8, 1.6, z=1.4, dome=0.5, mat=1)                                   # the hand
    cv.ellipse(43, 12.5, 3.6, 3.2, z=1.0, dome=0.8, mat=1)                                  # the head
    cv.ellipse(51, 13.5, 3.4, 2.4, z=0.8, dome=0.8, mat=0, tone=0.1)                        # the helmet
    for _ in range(9):                                                                     # wounds
        cv.ellipse(rng.uniform(24, 38), rng.uniform(9, 14), 1.0, 0.8, z=2.0, dome=0.2, mat=2)
    return _prop(cv, [OLIVE, SKIN, GORE, DARK], relief=1.0, cavity=0.4, shadow=0.4)


def spr_medkit():
    """A white medical kit with a red cross on its lid."""
    w, h = 22, 14
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(1, 2, 20, 12, z=0.4, top=1.0, bevel=2.0, mat=0)
    cv.box(8.5, 4, 5, 8, z=1.4, top=0.3, bevel=0.6, mat=1)
    cv.box(6, 6.5, 10, 3, z=1.4, top=0.3, bevel=0.6, mat=1)
    cv.box(8, 0.5, 6, 2.5, z=0.8, top=0.4, bevel=0.6, mat=2)                                 # the handle
    return _prop(cv, [WHITE_BOX, BLOOD, GUNMETAL], relief=1.0, cavity=0.3, shadow=0.3)


def spr_ammo_clip():
    """A magazine of pistol rounds, the brass of the top round showing."""
    w, h = 12, 14
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(2, 3), (9, 3), (10, 13), (3, 13)], z=0.4, top=0.9, bevel=1.2, mat=0)
    cv.ellipse(5.8, 2.6, 3.0, 1.4, z=1.2, dome=0.6, mat=1)
    cv.stroke([(4, 7), (8, 7.3)], 0.6, z=0, dome=0.3, mode='carve')
    return _prop(cv, [GUNMETAL, BRASS], relief=1.0, cavity=0.3, shadow=0.3)


def spr_armor_vest():
    """A combat vest laid on the floor: green plates over the chest, straps at the shoulders."""
    w, h = 26, 22
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(4, 4), (9, 2), (13, 5), (17, 2), (22, 4), (23, 20), (3, 20)], z=0.4, top=1.2, bevel=2.5, mat=0)
    cv.box(6, 7, 6, 9, z=1.4, top=0.5, bevel=1.0, mat=0, tone=0.08)
    cv.box(14, 7, 6, 9, z=1.4, top=0.5, bevel=1.0, mat=0, tone=0.08)
    cv.stroke([(4, 13), (22, 13)], 1.2, z=1.6, dome=0.4, mat=1)
    return _prop(cv, [ramp('#3e8a3a', dark=0.35, light=1.35), DARK], relief=1.0, cavity=0.35, shadow=0.35)


def spr_fireball():
    """A ball of fire hurled across a room: a white-hot core in orange flame with a ragged tail behind
    it. Glowing (additive); float it with `z`."""
    rng = np.random.default_rng(617)
    w, h = 40, 26
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    cx, cy = 28, 13
    n = smooth_noise(w, h, 5, rng, wrap=False)
    tail = (xx < cx) & (np.abs(yy - cy - 1.5 * np.sin(xx * 0.4)) < (xx / cx) * 6 * (0.6 + 0.6 * n))
    r = np.hypot(xx - cx, yy - cy) * (0.9 + 0.3 * n)
    for m, col in ((tail, (0.9, 0.3, 0.08)), (r < 9, (1.0, 0.45, 0.1)), (r < 6, (1.0, 0.75, 0.3)), (r < 3.2, (1.0, 0.97, 0.8))):
        rgba[m, :3] = col
        rgba[m, 3] = 1.0
        em[m] = 1.0
    return rgba, em


def dec_toxic_sign():
    """A warning sign for a wall: a yellow triangle edged in black with a skull in it, the word TOXIC
    below."""
    w, h = 40, 40
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    tri = (yy > 3) & (yy < 30) & (np.abs(xx - 20) < (yy - 3) * 0.74)
    inner = (yy > 7) & (yy < 27.5) & (np.abs(xx - 20) < (yy - 7) * 0.74 - 1.0)
    rgba[tri] = (0.1, 0.08, 0.06, 1.0)
    rgba[inner] = (0.96, 0.78, 0.18, 1.0)
    skull = (((xx - 20) / 4.2) ** 2 + ((yy - 17) / 3.8) ** 2 < 1) | ((np.abs(xx - 20) < 2.6) & (yy > 19) & (yy < 23))
    rgba[skull & inner] = (0.1, 0.08, 0.06, 1.0)
    for ex in (18.3, 21.7):
        rgba[(np.hypot(xx - ex, yy - 16.6) < 1.1) & inner] = (0.96, 0.78, 0.18, 1.0)
    plate = (yy > 31) & (yy < 39) & (xx > 4) & (xx < 36)
    rgba[plate] = (0.1, 0.08, 0.06, 1.0)
    word = _text_mask(SMALL, 'TOXIC')
    if word.shape[1] > 28:
        word = word[:, :28]
    wy, wx = 32 + (7 - word.shape[0]) // 2, 20 - word.shape[1] // 2
    sub = rgba[wy:wy + word.shape[0], wx:wx + word.shape[1]]
    sub[word] = (0.96, 0.78, 0.18, 1.0)
    return rgba, np.zeros((h, w), np.float32)


TEXTURES = {'nukage': tex_nukage, 'hex_floor': lambda n: (tex_hex_floor(n), None),
            'green_tech': lambda n: (tex_green_tech(n), None), 'green_trim': lambda n: (tex_green_trim(n), None),
            'green_window': tex_green_window, 'tech_ceiling': lambda n: (tex_tech_ceiling(n), None),
            'slime_edge': lambda n: (tex_slime_edge(n), None)}
TEXTURE_NOISE = {'nukage': 0.2, 'hex_floor': 0.8, 'green_tech': 0.8, 'green_trim': 0.8, 'green_window': 0.6,
                 'tech_ceiling': 0.6, 'slime_edge': 0.6}
SPRITES = {'toxic_barrel': spr_toxic_barrel, 'corpse': spr_corpse, 'medkit': spr_medkit, 'ammo_clip': spr_ammo_clip,
           'armor_vest': spr_armor_vest, 'fireball': spr_fireball}
SPRITE_HEIGHT = {'toxic_barrel': 0.4, 'corpse': 0.13, 'medkit': 0.1, 'ammo_clip': 0.07, 'armor_vest': 0.12,
                 'fireball': 0.22}
PROP_DEFAULTS = {'fireball': {'blend': 'additive', 'shadow': False},
                 'toxic_barrel': {'aura': {'color': [0.4, 1.0, 0.3], 'strength': 0.25, 'radius': 0.15}}}
NO_CONTACT_SHADOW = {'fireball'}
DECALS = {'toxic_sign': dec_toxic_sign}

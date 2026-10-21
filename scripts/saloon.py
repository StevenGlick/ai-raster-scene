"""The saloon: a frontier saloon's inside, drawn with the pixel-art toolkit (scripts/pixelart.py) -
flocked red wallpaper over a wainscot of dark boards, the back bar's carved shelves of bottles round
a mirror, a window of dusty panes, a pressed-tin ceiling; an upright piano, a card table mid-game,
a bentwood chair, a brass spittoon; and a wanted poster to paste on a wall.

The bar itself is an object (`saloon_bar` in objects.py): a long counter in 3D with its brass rail.
"""
import numpy as np

from biomes import T, _prop, _rng
from pixelart import Canvas, ramp, smooth_noise
from pixelfont import PixelFont

MAHOGANY = ramp('#5a2e1e', dark=0.3, light=1.5)
PAPER_RED = ramp('#7a2a26', dark=0.4, light=1.35)
PAPER_GOLD = ramp('#a8864a', dark=0.4, light=1.3)
BRASS = ramp('#c8a048', dark=0.35, light=1.5, warm=0.1)
BAIZE = ramp('#2e6a3a', dark=0.35, light=1.35)
IVORY = ramp('#e8e0c8', dark=0.5, light=1.1)
EBONY = ramp('#2a2224', dark=0.6, light=2.2)
TIN = ramp('#8a8474', dark=0.4, light=1.45)
MIRROR = ramp('#7a8a8e', dark=0.35, light=1.5, cool=0.2)
BOTTLE_GREEN = ramp('#2e5a32', dark=0.4, light=1.6)
BOTTLE_AMBER = ramp('#9a5a24', dark=0.4, light=1.5)
CHIP_RED = ramp('#b8302a', dark=0.4, light=1.3)
CHIP_BLUE = ramp('#2e4a9a', dark=0.4, light=1.3)
PAPER = ramp('#d8c8a0', dark=0.45, light=1.12)
INK = ramp('#2a2018', dark=0.6, light=2.0)
_FONT = PixelFont()


def _damask(cv, rng, y0, y1):
    """Flocked wallpaper between rows y0 and y1: a gold diamond trellis with a sprig in each lozenge."""
    for j in range(y0 // 16, (y1 + 15) // 16 + 1):
        for i in range(-1, T // 16 + 1):
            cx, cy = i * 16 + (8 if j % 2 else 0), j * 16
            if not (y0 - 4 <= cy <= y1 + 4):
                continue
            cv.polygon([(cx, cy - 6), (cx + 4, cy), (cx, cy + 6), (cx - 4, cy)], z=0.35, top=0.8, bevel=0.8, mat=2,
                       tone=float(rng.normal(-0.05, 0.03)))
            cv.ellipse(cx, cy, 1.4, 1.4, z=0.45, dome=0.5, mat=2, tone=0.05)


def tex_saloon_wainscot(name):
    """A saloon's wall to head height: a wainscot of dark raised panels to a chair rail (0.45 up),
    flocked red wallpaper above it. Stack `saloon_paper` over it."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.2, mat=1)
    cv.noise(0.05, cells=8, rng=rng)
    _damask(cv, rng, 0, T - 32)
    wy = T - 29
    cv.box(0, wy, T, 29, z=0.4, top=1.0, bevel=0, mat=0, tone=-0.06)
    for x in range(0, T, 16):                                       # the raised panels
        cv.box(x + 2, wy + 5, 12, 19, z=0.75, top=0.8, bevel=1.6, mat=0, tone=float(rng.normal(0, 0.03)))
    cv.box(0, wy, T, 3, z=1.0, top=1.0, bevel=0.6, mat=0, tone=0.1)    # the chair rail
    cv.box(0, T - 3, T, 3, z=0.9, top=1.0, bevel=0.4, mat=0, tone=-0.12)   # the skirting
    rgb = cv.paint([MAHOGANY, PAPER_RED, PAPER_GOLD], cv.light(relief=1.0, cavity=0.4, shadow=0.35), dither=0.25)
    return np.clip(rgb, 0, 1), None


def tex_saloon_paper(name):
    """Flocked red wallpaper, a dark cornice along its top - the wall over `saloon_wainscot`."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.2, mat=1)
    cv.noise(0.05, cells=8, rng=rng)
    _damask(cv, rng, 8, T)
    cv.box(0, 0, T, 5, z=1.0, top=1.0, bevel=0.8, mat=0, tone=0.04)      # the cornice
    cv.box(0, 5, T, 2, z=0.7, top=1.0, bevel=0.4, mat=2, tone=-0.1)
    rgb = cv.paint([MAHOGANY, PAPER_RED, PAPER_GOLD], cv.light(relief=1.0, cavity=0.4, shadow=0.35), dither=0.25)
    return np.clip(rgb, 0, 1), None


def _bottles(cv, rng, shelf, x0, x1, tall=(14, 22)):
    """A row of bottles standing on a shelf at row `shelf`, between x0 and x1."""
    x = x0 + rng.uniform(0, 2)
    while x < x1 - 4:
        bw, bh = rng.uniform(3.0, 4.6), rng.uniform(*tall)
        mat = int(rng.choice([3, 4, 4, 5]))
        cx = x + bw / 2
        cv.box(cx - bw / 2, shelf - bh * 0.6, bw, bh * 0.6, z=1.0, top=0.6, bevel=1.0, mat=mat,
               tone=float(rng.normal(0, 0.05)))
        cv.box(cx - 0.8, shelf - bh, 1.6, bh * 0.42, z=1.0, top=0.6, bevel=0.4, mat=mat)
        x += bw + rng.uniform(0.6, 1.8)


def tex_saloon_backbar(name):
    """The back bar to head height: a cabinet of dark panels with a shelf on it, and shelves of
    bottles - green, amber, clear - over it, in carved uprights. Stack `saloon_backbar_top` over it."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.box(0, 0, T, T, z=0.1, top=1.0, bevel=0, mat=0, tone=-0.3)           # the dark back
    for x in (0, 32):
        cv.box(x + 3, T - 24, 26, 20, z=0.6, top=0.8, bevel=1.6, mat=0)        # cabinet doors
    cv.box(0, T - 28, T, 4, z=1.0, top=1.0, bevel=0.6, mat=0, tone=0.08)      # the shelf on the cabinet
    _bottles(cv, rng, T - 30, 0, T)
    _bottles(cv, rng, 14, 0, T, tall=(8, 13))                               # short ones, under the top
    cv.box(0, 14, T, 3, z=0.9, top=1.0, bevel=0.5, mat=0, tone=0.04)          # a shelf
    for x in (0, T - 3):
        cv.box(x, 0, 3, T - 28, z=1.1, top=1.0, bevel=0.6, mat=0, tone=0.06)  # uprights
    rgb = cv.paint([MAHOGANY, MIRROR, BRASS, BOTTLE_GREEN, BOTTLE_AMBER, MIRROR],
                   cv.light(relief=1.0, cavity=0.45, shadow=0.4), dither=0.25)
    return np.clip(rgb, 0, 1), None


def tex_saloon_backbar_top(name):
    """The back bar's top: a tall mirror in a carved frame, misted at its edges, a lamp's glint in it,
    under an arched cresting."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.box(0, 0, T, T, z=0.2, top=1.0, bevel=0, mat=0, tone=-0.1)
    cv.box(5, 10, T - 10, T - 12, z=0.9, top=1.0, bevel=1.4, mat=0, tone=0.06)  # the frame
    cv.box(8, 13, T - 16, T - 18, z=0.3, top=1.0, bevel=0.4, mat=1)          # the glass
    cv.noise(0.03, cells=6, rng=rng)
    cv.polygon([(2, 9), (T // 2, 1), (T - 2, 9)], z=1.0, top=0.7, bevel=1.4, mat=0, tone=0.04)   # the cresting
    cv.ellipse(T // 2, 5, 2.5, 2.5, z=1.3, dome=0.7, mat=2)
    rgb = cv.paint([MAHOGANY, MIRROR, BRASS], cv.light(relief=1.0, cavity=0.4, shadow=0.35), dither=0.25)
    yy, xx = np.mgrid[0:T, 0:T]
    glass = (xx >= 9) & (xx < T - 9) & (yy >= 14) & (yy < T - 6)
    streak = glass & (np.abs((xx - 18) - (yy - 14) * 0.6) < 2.2)               # a glint across it
    rgb[streak] = np.minimum(1.0, rgb[streak] * 1.35 + 0.08)
    return np.clip(rgb, 0, 1), None


def tex_saloon_window(name):
    """A sash window of small dusty panes in a dark frame, the panes left open, so the sun comes
    through it (a see-through wall: stack it as a storey)."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.0, mat=0)
    cv.box(0, 0, T, T, z=0.6, top=1.0, bevel=0, mat=0)
    rgb = cv.paint([MAHOGANY], cv.light(relief=0.8), dither=0.25)
    alpha = np.ones((T, T), np.float32)
    for j in range(3):
        for i in range(2):
            x0, y0 = 8 + i * 25, 6 + j * 18
            alpha[y0:y0 + 15, x0:x0 + 22] = 0.0                              # the panes
    rgb[:4] *= 1.15
    return np.clip(rgb, 0, 1), None, alpha


def tex_tin_ceiling(name):
    """A pressed-tin ceiling, painted cream gone yellow with smoke: square panels each pressed with a
    rosette and a bead round its edge."""
    rng = _rng(name)
    cv = Canvas(T, ground=0.3, mat=0)
    for j in range(2):
        for i in range(2):
            x0, y0 = i * 32, j * 32
            cv.box(x0 + 2, y0 + 2, 28, 28, z=0.6, top=0.7, bevel=2.0, mat=0)
            cv.ellipse(x0 + 16, y0 + 16, 7, 7, z=0.9, dome=1.0, mat=0)
            for a in range(8):
                t = a * np.pi / 4
                cv.ellipse(x0 + 16 + 10 * np.cos(t), y0 + 16 + 10 * np.sin(t), 1.6, 1.6, z=0.8, dome=0.6, mat=0)
    cv.noise(0.05, cells=4, rng=rng)
    rgb = cv.paint([TIN], cv.light(relief=1.2, cavity=0.4, shadow=0.3), dither=0.25)
    return np.clip(rgb * np.array([1.06, 1.0, 0.86]), 0, 1), None


def spr_piano():
    """An upright piano: a dark case with carved legs, its fall open on the keys, candle sconces of
    brass on its front, a sheet of music on its stand."""
    w, h = 64, 52
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(4, 4, 56, 30, z=0.6, top=1.0, bevel=1.6, mat=0)                  # the upper case
    cv.box(8, 8, 48, 22, z=0.8, top=0.7, bevel=1.4, mat=0, tone=0.05)       # its panel
    cv.box(2, 2, 60, 4, z=1.0, top=1.0, bevel=0.8, mat=0, tone=0.08)        # the lid
    cv.box(2, 32, 60, 6, z=1.2, top=1.0, bevel=0.6, mat=0, tone=0.03)       # the key bed
    cv.box(4, 33, 56, 3, z=1.5, top=1.0, bevel=0.3, mat=1)                   # white keys
    for x in range(6, 58, 4):
        if (x // 4) % 7 not in (2, 6):
            cv.box(x + 2, 33, 1.5, 2, z=1.7, top=1.0, bevel=0.2, mat=2)       # black keys
    cv.box(8, 38, 48, 8, z=0.7, top=0.9, bevel=1.0, mat=0, tone=-0.05)     # the lower case
    for x in (8, 54):
        cv.stroke([(x, 38), (x, h - 1)], 2.6, z=1.0, dome=0.8, mat=0)        # legs
    cv.box(24, 12, 16, 12, z=1.2, top=0.8, bevel=0.6, mat=3)                 # the music
    for x in (12, 52):
        cv.stroke([(x, 22), (x, 16)], 1.2, z=1.4, dome=0.5, mat=4)            # sconces
        cv.ellipse(x, 15, 1.4, 1.4, z=1.6, dome=0.6, mat=3)
    return _prop(cv, [MAHOGANY, IVORY, EBONY, PAPER, BRASS], relief=1.0, cavity=0.4, shadow=0.45)


def spr_card_table():
    """A round card table mid-game, seen a little from above: green baize, a spread of cards, stacks
    of red, white and blue chips, a bottle and two glasses, on a turned pedestal."""
    rng = np.random.default_rng(171)
    w, h = 56, 36
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(28, 16), (28, h - 4)], 4.0, z=0.4, dome=0.8, mat=0)          # the pedestal
    cv.ellipse(28, h - 3, 10, 2.4, z=0.5, dome=0.5, mat=0)                    # its foot
    cv.ellipse(28, 13, 26, 8.5, z=0.8, dome=0.3, mat=0)                      # the rim
    cv.ellipse(28, 12.5, 23.5, 7, z=1.0, dome=0.2, mat=1)                    # the baize
    for k in range(7):                                                       # cards
        cx, cy = rng.uniform(12, 44), rng.uniform(9, 15)
        cv.polygon([(cx - 2.2, cy - 1.2), (cx + 2.2, cy - 1.6), (cx + 2.4, cy + 1.2), (cx - 2.0, cy + 1.6)],
                   z=1.15, top=1.0, bevel=0.2, mat=2, tone=float(rng.normal(0.03, 0.02)))
    for x, y, m in ((14, 11, 3), (17, 13, 2), (39, 10, 4), (41, 13, 3)):     # chip stacks
        for k in range(int(rng.integers(2, 5))):
            cv.ellipse(x, y - k * 0.9, 1.8, 0.9, z=1.3 + k * 0.1, dome=0.4, mat=m)
    cv.box(31, 1, 3, 9, z=1.6, top=0.6, bevel=0.6, mat=5)                    # a bottle
    cv.box(32, -2, 1.2, 3.5, z=1.6, top=0.6, bevel=0.2, mat=5)
    for x in (22, 36):
        cv.box(x, 8, 2.4, 3, z=1.5, top=0.9, bevel=0.3, mat=6)               # glasses
    return _prop(cv, [MAHOGANY, BAIZE, IVORY, CHIP_RED, CHIP_BLUE, BOTTLE_AMBER, MIRROR],
                 relief=1.0, cavity=0.4, shadow=0.45)


def spr_saloon_chair():
    """A bentwood chair seen side on: the hooped back, the round seat, splayed legs."""
    w, h = 26, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.stroke([(6, 22), (5, 12), (6, 4), (10, 2), (13, 5), (13, 21)], 1.5, z=0.7, dome=0.7, mat=0)   # the hoop
    cv.ellipse(13, 22, 10, 2.4, z=0.9, dome=0.6, mat=0, tone=0.04)          # the seat
    for x0, x1 in ((5, 3), (21, 23), (9, 8), (17, 18)):
        cv.stroke([(x0, 23), (x1, h - 1)], 1.3, z=0.6, dome=0.6, mat=0)      # legs
    cv.ellipse(13, 32, 7, 1.0, z=0.5, dome=0.3, mat=0, tone=-0.06)          # the ring between them
    return _prop(cv, [MAHOGANY], relief=1.0, cavity=0.4, shadow=0.45)


def spr_spittoon():
    """A brass spittoon: a squat bellied pot with a wide funnel mouth."""
    w, h = 18, 14
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(9, 9, 7.5, 4.5, z=0.6, dome=1.0, mat=0)
    cv.ellipse(9, 4, 6.0, 1.8, z=1.0, dome=0.4, mat=0, tone=0.08)
    cv.ellipse(9, 4, 3.6, 1.0, z=0.8, dome=0.2, mat=0, tone=-0.3)
    return _prop(cv, [BRASS], relief=1.0, cavity=0.4, shadow=0.45)


def dec_wanted_poster():
    """A wanted poster to paste on a wall: yellowed paper, WANTED over a sketched face, a reward."""
    w, h = 42, 48
    rgba = np.zeros((h, w, 4), np.float32)
    rng = np.random.default_rng(181)
    paper = np.array([0.84, 0.76, 0.58], np.float32)
    rgba[1:h - 1, 1:w - 1, :3] = paper * (0.92 + 0.12 * smooth_noise(w - 2, h - 2, 4, rng, wrap=False)[..., None])
    rgba[1:h - 1, 1:w - 1, 3] = 1.0
    rgba[h - 6:h - 1, w - 7:w - 1, 3] = 0.0                                # a torn corner
    ink = np.array([0.18, 0.12, 0.08], np.float32)
    for text, y in (('WANTED', 3), ('$500', h - 11)):
        m = np.asarray(_FONT.render_mask(text))
        mh, mw = m.shape[:2]
        x = (w - mw) // 2
        if x >= 0:
            sub = m[:min(mh, h - y), :min(mw, w - x)] > 0
            rgba[y:y + sub.shape[0], x:x + sub.shape[1], :3][sub] = ink
    yy, xx = np.mgrid[0:h, 0:w]
    face = ((xx - 21) / 7.0) ** 2 + ((yy - 24) / 9.0) ** 2
    rgba[(face > 0.75) & (face < 1.0), :3] = ink * 1.4                    # the face sketched
    for ex in (17, 23):
        rgba[22:24, ex:ex + 2, :3] = ink
    rgba[28, 17:25, :3] = ink * 1.2                                        # a mustache
    rgba[17:19, 13:30, :3] = ink                                           # a hat brim
    rgba[13:17, 16:27, :3] = ink * 1.1                                     # its crown
    return rgba, np.zeros((h, w), np.float32)


TEXTURES = {'saloon_wainscot': tex_saloon_wainscot, 'saloon_paper': tex_saloon_paper,
            'saloon_backbar': tex_saloon_backbar, 'saloon_backbar_top': tex_saloon_backbar_top,
            'saloon_window': tex_saloon_window, 'tin_ceiling': tex_tin_ceiling}
TEXTURE_NOISE = {'saloon_wainscot': 0.3, 'saloon_paper': 0.3, 'saloon_backbar': 0.2, 'saloon_backbar_top': 0.2,
                 'saloon_window': 0.3, 'tin_ceiling': 0.3}
SPRITES = {'piano': spr_piano, 'card_table': spr_card_table, 'saloon_chair': spr_saloon_chair,
           'spittoon': spr_spittoon}
SPRITE_HEIGHT = {'piano': 0.46, 'card_table': 0.3, 'saloon_chair': 0.32, 'spittoon': 0.09}
DECALS = {'wanted_poster': dec_wanted_poster}

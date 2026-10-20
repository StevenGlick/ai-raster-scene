"""The neon bar, drawn with the pixel-art toolkit (scripts/pixelart.py): an arcade cabinet with a game
on its screen, a bar counter's front to stand as a card, chrome bar stools, a booth, a jukebox
with its bubble tubes, neon art for the walls (a cocktail glass, a fish), a cluster of bottles
for the counter, and the back bar's lit shelves as a wall texture.

Screens, tubes and shelves glow: give each a coloured light of its own and the haze of a
volumetric fog (`glow`) carries their colour through the room.
"""
import numpy as np

from biomes import T, _prop, _rng
from buildings import NEON, _glyph_mask
from pixelart import Canvas, outline_sprite, ramp, smooth_noise

CAB = ramp('#2a2440', dark=0.5, light=1.6)
CAB_ART = ramp('#c03a8a', dark=0.35, light=1.3)
CHROME = ramp('#b8c0c8', dark=0.4, light=1.25, cool=0.15)
VINYL = ramp('#b8283a', dark=0.4, light=1.35)
VINYL_TEAL = ramp('#1e8a8a', dark=0.4, light=1.4)
WOOD = ramp('#4a3226', dark=0.35, light=1.4)
BLACK = ramp('#18161c', dark=0.6, light=2.0)
FORMICA = ramp('#d8d0c0', dark=0.5, light=1.12)
GLASS_GREEN = ramp('#2e6a3a', dark=0.4, light=1.5)
GLASS_AMBER = ramp('#a0602a', dark=0.4, light=1.4)
GLASS_CLEAR = ramp('#a8c0c4', dark=0.5, light=1.2)
JUKE = ramp('#c89a4a', dark=0.4, light=1.3, warm=0.15)


def _tube(rgba, em, mask, color):
    """Neon tube along a one-pixel mask: the tube white-hot in its core colour, a glow either side."""
    c = np.array(color, np.float32)
    halo = mask.copy()
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        halo |= np.roll(mask, (dy, dx), (0, 1))
    ring = halo & ~mask & (rgba[..., 3] < 0.5)
    rgba[ring, :3] = c * 0.55
    rgba[ring, 3] = 0.7
    em[ring] = 0.6
    rgba[mask, :3] = np.clip(c * 0.7 + 0.35, 0, 1)
    rgba[mask, 3] = 1.0
    em[mask] = 1.0


def _line(mask, pts):
    """One-pixel lines through pts into a boolean mask."""
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        xs = np.clip(np.round(np.linspace(x0, x1, n)).astype(int), 0, mask.shape[1] - 1)
        ys = np.clip(np.round(np.linspace(y0, y1, n)).astype(int), 0, mask.shape[0] - 1)
        mask[ys, xs] = True


def _game_screen(h, w, rng):
    """A frame of an arcade shooter: a starfield, rows of invaders, a ship, a shot going up, the
    score along the top - in the bright flat colours of a CRT."""
    img = np.zeros((h, w, 3), np.float32)
    img[:] = (0.02, 0.02, 0.06)
    stars = rng.random((h, w)) < 0.03
    img[stars] = (0.5, 0.5, 0.7)
    inv = [[0, 1, 0, 1, 0], [1, 1, 1, 1, 1], [1, 0, 1, 0, 1]]
    cols = [(1.0, 0.3, 0.6), (0.3, 1.0, 0.5), (0.4, 0.7, 1.0)]
    for r in range(3):
        for c in range(4):
            x0, y0 = 3 + c * 7, 6 + r * 5
            for yy, row in enumerate(inv):
                for xx, v in enumerate(row):
                    if v and y0 + yy < h and x0 + xx < w:
                        img[y0 + yy, x0 + xx] = cols[r]
    sx = w // 2 + int(rng.integers(-4, 4))
    for yy, xx in ((h - 3, sx), (h - 4, sx), (h - 3, sx - 1), (h - 3, sx + 1), (h - 2, sx - 2), (h - 2, sx + 2),
                   (h - 2, sx - 1), (h - 2, sx), (h - 2, sx + 1)):
        img[yy, xx] = (1.0, 0.95, 0.4)
    for yy in range(h - 12, h - 7):
        img[yy, sx] = (1.0, 1.0, 1.0)
    img[1, 2:12:2] = (1.0, 1.0, 1.0)
    img[1, w - 10:w - 2:2] = (1.0, 0.8, 0.3)
    return img


def spr_arcade_cabinet():
    """An upright arcade cabinet: a dark body with neon side art, a marquee lit along the top in
    glowing pseudo-letters, a shooter on its screen in the bezel, a control panel with a joystick
    and buttons, a coin door below."""
    rng = np.random.default_rng(501)
    w, h = 44, 104
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(4, 14), (40, 14), (40, 52), (44, 60), (44, 104), (2, 104), (2, 60), (4, 52)], z=0.4, top=0.8,
               bevel=2.0, mat=0)                                                           # the body
    cv.box(4, 2, 36, 13, z=0.9, top=0.6, bevel=1.5, mat=0)                                 # marquee box
    cv.box(7, 18, 30, 30, z=0.6, top=0.3, bevel=2.5, mat=2)                                # screen bezel
    cv.polygon([(2, 56), (44, 56), (44, 64), (2, 64)], z=1.4, top=0.7, bevel=1.5, mat=1)    # control panel
    cv.stroke([(14, 58), (14, 52)], 1.4, z=2.0, dome=0.4, mat=3)                           # joystick
    cv.ellipse(14, 51, 2.2, 2.2, z=2.4, dome=0.8, mat=4)
    for k, x in enumerate((24, 30, 36)):
        cv.ellipse(x, 59, 1.8, 1.4, z=2.0, dome=0.6, mat=4 + k % 2)
    cv.box(14, 74, 16, 14, z=0.8, top=0.4, bevel=1.0, mat=2)                               # coin door
    for x in (19, 24):
        cv.box(x, 77, 3, 5, z=1.0, top=0.2, bevel=0.5, mat=5)
    rgba = cv.paint([CAB, CAB_ART, BLACK, CHROME, VINYL, VINYL_TEAL],
                    cv.light(relief=1.0, cavity=0.35, shadow=0.4), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    rgba[22:44, 10:34, :3] = _game_screen(22, 24, rng)                                     # the screen
    em[22:44, 10:34] = 0.95
    scan = np.arange(22, 44) % 2 == 0
    rgba[22:44, 10:34, :3][scan] *= 0.75
    glyph = _glyph_mask(7, 30, rng, False)                                                 # the marquee
    c = np.array(NEON[0], np.float32)
    sub = rgba[5:12, 7:37, :3]
    sub[:] = c * 0.25 + 0.05
    sub[glyph] = np.clip(c * 0.7 + 0.35, 0, 1)
    em[5:12, 7:37] = np.where(glyph, 1.0, 0.55)
    side = np.zeros((h, w), bool)                                                          # side art stripes
    _line(side, [(4, 66), (12, 98)])
    _line(side, [(40, 66), (32, 98)])
    _tube(rgba, em, side & (rgba[..., 3] > 0.5), NEON[2])
    return rgba.astype(np.float32), em


def spr_bar_counter():
    """The front of a bar counter, to stand as a card along the bar (`planes` 1, a `length`): dark
    wood panelling under a steel rail and the lip of the top, a strip of magenta light along the
    foot. It repeats along its length."""
    w, h = 64, 28
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(-2, 3, w + 4, 22, z=0.4, top=0.6, bevel=1.0, mat=0)                             # the panelling
    for x in range(0, w, 16):
        cv.box(x + 2, 6, 12, 16, z=0.9, top=0.4, bevel=1.5, mat=0, tone=0.05)              # raised panels
    cv.box(-2, 0, w + 4, 4, z=1.6, top=0.6, bevel=1.0, mat=1)                              # the top's lip
    cv.stroke([(-2, 8), (w + 2, 8)], 1.4, z=2.2, dome=0.5, mat=2)                          # the rail
    rgba = cv.paint([WOOD, BLACK, CHROME], cv.light(relief=1.0, cavity=0.35, shadow=0.35), dither=0.3)
    em = np.zeros((h, w), np.float32)
    rgba[25:28, :, :3] = np.array([1.0, 0.35, 0.75], np.float32)
    rgba[25:28, :, 3] = 1.0
    em[25:28] = 1.0
    rgba[24, :, :3] = rgba[24, :, :3] * 0.4 + np.array([1.0, 0.35, 0.75], np.float32) * 0.5
    return rgba.astype(np.float32), em


def spr_bar_stool():
    """A chrome bar stool: a round seat in red vinyl on a pole, a foot ring, a weighted base."""
    w, h = 24, 40
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(12, 38, 9, 2.4, z=0.0, dome=0.6, mat=1)                                     # base
    cv.stroke([(12, 37), (12, 9)], 2.2, z=0.6, dome=0.8, mat=1)                            # pole
    cv.ellipse(12, 24, 7, 1.6, z=1.2, dome=0.4, mat=1)                                     # foot ring
    cv.ellipse(12, 7, 10, 4.0, z=1.6, dome=1.4, mat=0)                                     # the seat
    cv.box(3, 7, 18, 4, z=1.2, top=0.6, bevel=1.0, mat=0, tone=-0.12)
    return _prop(cv, [VINYL, CHROME], relief=1.0, cavity=0.35, shadow=0.4)


def spr_booth():
    """A diner booth seen from the aisle: a high-backed bench buttoned in teal vinyl, a formica
    table on a chrome leg in front of it, a lamp glowing on the table."""
    w, h = 72, 52
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(2, 2, 68, 34, z=0.2, top=1.0, bevel=3.0, mat=0)                                 # the back
    for y in (10, 22):
        for x in range(10, 66, 12):
            cv.ellipse(x + (6 if y == 22 else 0), y, 1.0, 1.0, z=0.8, dome=0.4, mode='carve')   # buttons
    cv.box(0, 34, 72, 8, z=0.8, top=1.0, bevel=2.0, mat=0, tone=0.06)                      # the seat
    cv.box(2, 42, 68, 10, z=0.6, top=0.5, bevel=1.0, mat=3)                                # its base
    cv.stroke([(36, 38), (36, 52)], 2.6, z=1.6, dome=0.6, mat=2)                           # table leg
    cv.box(8, 30, 56, 5, z=2.0, top=0.6, bevel=1.2, mat=1)                                 # the table
    cv.box(31, 22, 6, 8, z=2.4, top=0.8, bevel=1.5, mat=2)                                 # a lamp
    rgba = cv.paint([VINYL_TEAL, FORMICA, CHROME, BLACK], cv.light(relief=1.0, cavity=0.35, shadow=0.4), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    rgba[19:23, 30:38, :3] = (1.0, 0.85, 0.55)
    rgba[19:23, 30:38, 3] = 1.0
    em[19:23, 30:38] = 1.0
    return rgba.astype(np.float32), em


def spr_jukebox():
    """A jukebox: a rounded top glowing in bands of colour, bubble tubes up both sides, a window
    onto the records, a grille below - lit up from inside."""
    w, h = 44, 64
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(3, 22, 38, 42, z=0.4, top=0.9, bevel=2.0, mat=0)                                # the body
    cv.ellipse(22, 22, 19, 19, z=0.4, dome=1.4, mat=0)                                     # the arch
    cv.box(10, 30, 24, 12, z=1.2, top=0.3, bevel=1.0, mat=1)                               # record window
    cv.box(10, 46, 24, 14, z=1.0, top=0.4, bevel=1.0, mat=2)                               # the grille
    for y in range(48, 60, 3):
        cv.stroke([(11, y), (33, y)], 0.8, z=0, dome=0.3, mode='carve')
    rgba = cv.paint([JUKE, BLACK, CHROME], cv.light(relief=1.0, cavity=0.35, shadow=0.4), dither=0.3)
    rgba = outline_sprite(rgba)
    em = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    d = np.hypot(xx - 22, yy - 22)
    arch = (d < 17) & (d > 11) & (yy < 23)
    band = ((d - 11) // 2).astype(int) % 3
    for k, c in enumerate(((1.0, 0.35, 0.3), (1.0, 0.8, 0.3), (0.4, 0.8, 1.0))):
        m = arch & (band == k)
        rgba[m, :3] = c
        em[m] = 1.0
    for x in (6, 37):                                                                      # bubble tubes
        for y in range(24, 62):
            on = (y * 7 + x) % 5 == 0
            rgba[y, x:x + 2, :3] = (1.0, 0.95, 0.8) if on else (1.0, 0.45, 0.25)
            em[y, x:x + 2] = 1.0
    rec = (np.abs(xx - 22) < 9) & (yy > 31) & (yy < 41)
    rgba[rec & ((xx.astype(int) % 4) == 0), :3] = (0.1, 0.1, 0.12)
    rgba[rec & ((xx.astype(int) % 4) != 0), :3] = (0.75, 0.6, 0.35)
    em[rec] = 0.5
    return rgba.astype(np.float32), em


def _neon_art(w, h, paths, color, filled=None, fill_color=None):
    """Neon art for a wall: the given polylines drawn as glowing tube on nothing (additive)."""
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    mask = np.zeros((h, w), bool)
    for pts in paths:
        _line(mask, pts)
    if filled is not None:
        c = np.array(fill_color, np.float32)
        rgba[filled & ~mask, :3] = c * 0.55
        rgba[filled & ~mask, 3] = 1.0
        em[filled & ~mask] = 0.8
    _tube(rgba, em, mask, color)
    return rgba, em


def spr_neon_cocktail():
    """A neon sign of a cocktail glass: the rim, the cone, the stem and foot in pink tube, an olive
    on a stick in green. Glowing and additive: hang it on a wall with `z`."""
    w, h = 40, 48
    glass = [(4, 6), (36, 6), (20, 26), (4, 6)]
    stem = [(20, 26), (20, 40)]
    foot = [(12, 42), (28, 42)]
    stick = [(14, 2), (24, 14)]
    rgba, em = _neon_art(w, h, [glass, stem, foot], NEON[0])
    r2, e2 = _neon_art(w, h, [stick], NEON[2])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    olive = np.hypot(xx - 24.5, yy - 14.5) < 2.4
    m = r2[..., 3] > 0
    rgba[m] = r2[m]
    em[m] = np.maximum(em[m], e2[m])
    rgba[olive, :3] = (0.5, 1.0, 0.45)
    rgba[olive, 3] = 1.0
    em[olive] = 1.0
    return rgba, em


def spr_neon_fish():
    """A neon sign of a fish: the outline of its body and tail in cyan tube, an eye, a few scales
    and bubbles rising. Glowing and additive: hang it on a wall with `z`."""
    w, h = 56, 36
    t = np.linspace(0, 2 * np.pi, 40)
    body = list(zip(28 + 16 * np.cos(t), 18 + 9 * np.sin(t)))
    tail = [(12, 18), (3, 9), (3, 27), (12, 18)]
    scales = [list(zip(30 + k * 5 + 2.5 * np.cos(a), 18 + 4 * np.sin(a))) for k in range(-2, 2)
              for a in [np.linspace(-1.2, 1.2, 8)]]
    rgba, em = _neon_art(w, h, [body, tail] + scales, NEON[1])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    eye = np.hypot(xx - 38.5, yy - 15.5) < 1.6
    rgba[eye, :3] = (1.0, 1.0, 1.0)
    rgba[eye, 3] = 1.0
    em[eye] = 1.0
    for bx, by, r in ((48, 7, 1.6), (51, 2.5, 1.2)):
        ring = (np.abs(np.hypot(xx - bx, yy - by) - r) < 0.6)
        rgba[ring, :3] = np.array(NEON[1], np.float32) * 0.8 + 0.2
        rgba[ring, 3] = 1.0
        em[ring] = 1.0
    return rgba, em


def spr_bottles():
    """A cluster of bottles for a bar top or a shelf: green, amber and clear glass at different
    heights, one with a lit label, catching the light down their shoulders."""
    rng = np.random.default_rng(509)
    w, h = 40, 32
    cv = Canvas(w, h, wrap=False, ground=-9)
    for k, (x, top, r, m) in enumerate(((6, 6, 3.4, 0), (13, 2, 3.0, 1), (20, 9, 3.6, 2), (27, 4, 3.2, 0),
                                       (34, 10, 3.0, 1))):
        neck = top + 7
        cv.box(x - r, neck, 2 * r, h - neck, z=0.6 + k * 0.1, top=1.2, bevel=r, mat=m)          # the body
        cv.polygon([(x - r, neck + 1), (x + r, neck + 1), (x + 1.1, top + 3), (x - 1.1, top + 3)], z=0.7 + k * 0.1,
                   top=1.0, bevel=1.2, mat=m)                                              # the shoulder
        cv.box(x - 1.1, top, 2.2, 4, z=0.8 + k * 0.1, top=0.6, bevel=0.6, mat=m)            # the neck
        cv.box(x - r + 0.6, neck + 6, 2 * r - 1.2, 6, z=1.0 + k * 0.1, top=0.2, bevel=0.4, mat=3)   # label
    rgba = cv.paint([GLASS_GREEN, GLASS_AMBER, GLASS_CLEAR, FORMICA], cv.light(relief=1.2, cavity=0.3, shadow=0.3),
                    dither=0.3)
    rgba = outline_sprite(rgba)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    for x, top in ((6, 6), (20, 9), (34, 10)):                                             # glints
        m = (np.abs(xx - (x - 1.5)) < 0.6) & (yy > top + 9) & (yy < h - 3)
        rgba[m & (rgba[..., 3] > 0.5), :3] = np.minimum(1.0, rgba[m & (rgba[..., 3] > 0.5), :3] + 0.35)
    del rng
    return rgba.astype(np.float32), np.zeros((h, w), np.float32)


def tex_bar_shelves(name):
    """The back bar: two glass shelves of bottles in a mirrored recess, lit from below by a strip of
    light along each shelf so every bottle glows at its foot - green, amber, clear, a blue one, a
    red one. It glows; tile it along the wall behind a bar."""
    rng = _rng(name)
    rgb = np.zeros((T, T, 3), np.float32)
    em = np.zeros((T, T), np.float32)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32) + 0.5
    rgb[:] = (0.06, 0.05, 0.08) + 0.04 * smooth_noise(T, T, 4, rng)[..., None]             # mirror behind
    pal = [(0.2, 0.55, 0.3), (0.7, 0.42, 0.18), (0.65, 0.75, 0.78), (0.25, 0.4, 0.9), (0.8, 0.2, 0.25),
           (0.85, 0.75, 0.3)]
    for shelf in (30, 62):                                                                 # two shelves
        rgb[shelf - 1:shelf + 1, :] = (0.55, 0.6, 0.65)
        rgb[shelf + 1, :] = (1.0, 0.4, 0.8)
        em[shelf + 1, :] = 1.0
        x = rng.uniform(0, 3)
        while x < T - 3:
            bw = rng.uniform(3.0, 5.0)
            bh = rng.uniform(14, 24)
            c = np.array(pal[int(rng.integers(len(pal)))], np.float32)
            body = (np.abs(xx - x - bw / 2) < bw / 2) & (yy < shelf - 1) & (yy > shelf - 1 - bh * 0.62)
            neck = (np.abs(xx - x - bw / 2) < 0.9) & (yy <= shelf - 1 - bh * 0.62) & (yy > shelf - 1 - bh)
            m = body | neck
            glow = np.clip(1.0 - (shelf - 1 - yy) / (bh * 0.8), 0.15, 1.0)                 # lit from below
            rgb[m] = c[None, :] * (0.35 + 0.9 * glow[m])[:, None]
            em[m] = np.maximum(em[m], 0.65 * glow[m])
            edge = m & (np.abs(xx - x - 0.8) < 0.6)
            rgb[edge] = np.minimum(1.0, rgb[edge] + 0.3)
            x += bw + rng.uniform(0.8, 2.2)
    return np.clip(rgb, 0, 1), em


TEXTURES = {'bar_shelves': tex_bar_shelves}
TEXTURE_NOISE = {'bar_shelves': 0.2}
SPRITES = {'arcade_cabinet': spr_arcade_cabinet, 'bar_counter': spr_bar_counter, 'bar_stool': spr_bar_stool,
           'booth': spr_booth, 'jukebox': spr_jukebox, 'neon_cocktail': spr_neon_cocktail,
           'neon_fish': spr_neon_fish, 'bottles': spr_bottles}
SPRITE_HEIGHT = {'arcade_cabinet': 0.68, 'bar_counter': 0.35, 'bar_stool': 0.27, 'booth': 0.5, 'jukebox': 0.56,
                 'neon_cocktail': 0.4, 'neon_fish': 0.32, 'bottles': 0.12}
PROP_DEFAULTS = {'bar_counter': {'planes': 1, 'shadow': False},
                 'neon_cocktail': {'blend': 'additive', 'shadow': False},
                 'neon_fish': {'blend': 'additive', 'shadow': False},
                 'arcade_cabinet': {'aura': {'color': [0.6, 0.5, 1.0], 'strength': 0.25, 'radius': 0.15}},
                 'jukebox': {'aura': {'color': [1.0, 0.6, 0.3], 'strength': 0.3, 'radius': 0.18}}}
NO_CONTACT_SHADOW = {'neon_cocktail', 'neon_fish', 'bar_counter'}

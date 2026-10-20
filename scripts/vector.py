"""Vector World: a world drawn in lines of light on black - the look of 80s vector arcade games and
of films set inside a computer.

The textures are black ruled with lines of white light, so a cell's `tint` colours them (cyan,
magenta, orange): `vector_grid` (a wall of squares), `vector_floor` (the grid running away to the
horizon - make it reflect), `vector_frame` (each cell outlined, so a block reads as a box of
light), `vector_circuit` (traces and pads), `vector_windows` (a tower of window outlines, a few
lit), `vector_bands` (bands of light stacked up a wall) and `vector_data` (dashes of light running
down in columns). The props: `vector_runner` (a figure in a black suit traced with light),
`light_trail` (a ribbon of light, a card: give it a `length` and an `angle`), `light_beam` (a
column of light rising from the floor) and `glint` (a point of light - a headlight, a beacon - to
hang at a height with `z`). Tint any of them. The shapes - cubes, pyramids, polyhedra, mountains,
racers - are wireframes (scripts/wires.py); the sky is `vector`, with a sun given
`"disc_style": "stripes"`.
"""
import numpy as np

from biomes import T, _rng

INK = np.array([0.012, 0.012, 0.022], np.float32)       # the black everything is made of
LIGHT = np.array([0.92, 0.97, 1.0], np.float32)         # the lines: white, for a tint to colour


def _lit(line, halo=None, dim=None):
    """Black with lines of light: `line` (0-1) at full brightness, `dim` (0-1) fainter lines, and
    `halo` a faint glow beside them."""
    m = np.clip(np.asarray(line, np.float32), 0, 1)
    if dim is not None:
        m = np.maximum(m, np.clip(np.asarray(dim, np.float32), 0, 1) * 0.45)
    if halo is not None:
        m = np.maximum(m, np.clip(np.asarray(halo, np.float32), 0, 1) * 0.22)
    rgb = INK[None, None, :] * (1 - m[..., None]) + LIGHT[None, None, :] * m[..., None]
    return rgb.astype(np.float32), m.astype(np.float32)


def _ruled(coord, period, half=1):
    """Lines centred on every multiple of `period` texels, `half` texels to each side, so where two
    tiles meet the line is whole and the outer edges of a wall get half of one; and the texels just
    beside the lines, for a halo."""
    r = coord % period
    line = (r < half) | (r >= period - half)
    halo = (r == half) | (r == period - half - 1)
    return line, halo


def tex_vector_grid(name):
    """A wall of squares: black, ruled in lines of light, two squares to a unit each way."""
    yy, xx = np.mgrid[0:T, 0:T]
    lx, hx = _ruled(xx, 32)
    ly, hy = _ruled(yy, 32)
    return _lit(lx | ly, hx | hy)


def tex_vector_floor(name):
    """The grid underfoot: a line of light at every unit, running away to the horizon."""
    yy, xx = np.mgrid[0:T, 0:T]
    lx, hx = _ruled(xx, 64, 1)
    ly, hy = _ruled(yy, 64, 1)
    return _lit(lx | ly, hx | hy)


def tex_vector_frame(name):
    """Black with a line of light round the edge of each cell, so a block reads as a box of light."""
    yy, xx = np.mgrid[0:T, 0:T]
    lx, hx = _ruled(xx, 64, 2)
    ly, hy = _ruled(yy, 64, 2)
    return _lit(lx | ly, hx | hy)


def tex_vector_circuit(name):
    """Traces of light running at right angles across black, each ending in a square pad or a ring."""
    rng = _rng(name)
    m = np.zeros((T, T), np.float32)
    for _ in range(9):
        x, y = (rng.integers(1, 15, 2) * 4)
        d = rng.integers(4)
        for _ in range(rng.integers(3, 7)):
            n = int(rng.integers(2, 6)) * 4
            dx, dy = ((1, 0), (0, 1), (-1, 0), (0, -1))[d]
            for _ in range(n):
                if 1 <= x < T - 1 and 1 <= y < T - 1:
                    m[y, x] = 1.0
                    m[y + (dx != 0), x + (dy != 0)] = 1.0
                x, y = x + dx, y + dy
            d = (d + (1 if rng.random() < 0.5 else 3)) % 4
        if 3 <= x < T - 3 and 3 <= y < T - 3:
            if rng.random() < 0.5:
                m[y - 2:y + 2, x - 2:x + 2] = 1.0
            else:
                yy, xx = np.mgrid[0:T, 0:T]
                r = np.hypot(yy - y, xx - x)
                m[(r >= 1.5) & (r < 2.6)] = 1.0
    yy, xx = np.mgrid[0:T, 0:T]
    edge, _ = _ruled(yy, 64, 1)
    halo = np.zeros_like(m)
    for oy, ox in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        halo = np.maximum(halo, np.roll(np.roll(m, oy, 0), ox, 1))
    return _lit(m, halo, edge)


def tex_vector_windows(name):
    """The face of a tower: four rows of four window outlines to a unit, a few of them lit."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    cx, cy = xx % 16, yy % 16
    box = ((cx >= 3) & (cx <= 12) & (cy >= 3) & (cy <= 12))
    rim = box & ((cx == 3) | (cx == 12) | (cy == 3) | (cy == 12))
    lit = rng.random((4, 4)) < 0.28
    fill = box & lit[yy // 16, xx // 16]
    return _lit(rim, None, fill)


def tex_vector_bands(name):
    """Bands of light stacked up a wall: a bold one at every storey and thin ones between."""
    yy, _ = np.mgrid[0:T, 0:T]
    bold, halo = _ruled(yy, 64, 2)
    thin = (yy % 16 == 8)
    return _lit(bold, halo, thin)


def tex_vector_data(name):
    """Dashes of light running down in columns, like data streaming past, brighter at their heads."""
    rng = _rng(name)
    m = np.zeros((T, T), np.float32)
    for col in range(2, T, 6):
        y = int(rng.integers(T))
        for _ in range(3):
            n = int(rng.integers(4, 14))
            ys = (y + np.arange(n)) % T
            m[ys, col] = np.maximum(m[ys, col], np.linspace(0.25, 1.0, n))
            m[ys, col + 1] = np.maximum(m[ys, col + 1], np.linspace(0.25, 1.0, n) * 0.6)
            y = (y + n + int(rng.integers(3, 12))) % T
    return _lit(m)


# ------------------------------------------------------------------ props

RUNNER = [                     # K suit, G its sheen, L a line of light, . clear
    "......KKKK......",
    ".....KGGGGK.....",
    "....KGKKKKGK....",
    "....KKKKKKKK....",
    "....LLLLLLLL....",
    "....KKKKKKKK....",
    ".....KKKKKK.....",
    "......KKKK......",
    "......KLLK......",
    "...KKKKKKKKKK...",
    "..KLLKKKKKKLLK..",
    "..KLKKKKKKKKLK..",
    "..KLKKKLLKKKLK..",
    "..KLKKLKKLKKLK..",
    "..KLKKKLLKKKLK..",
    "..KLKKKKKKKKLK..",
    "..KLKKKKKKKKLK..",
    "..KLKLLLLLLKLK..",
    "..KLKKKKKKKKLK..",
    "..LLKKKKKKKKLL..",
    "..LL.KKKKKK.LL..",
    ".....KKKKKK.....",
    "....KLKK.KKLK...",
    "....KLKK.KKLK...",
    "....KLKK.KKLK...",
    "....KLLK.KLLK...",
    "....KLKK.KKLK...",
    "....KLKK.KKLK...",
    "....KLKK.KKLK...",
    "....KLKK.KKLK...",
    "...LLLLK.KLLLL..",
    "...KKKKK.KKKKK..",
]


def spr_vector_runner():
    """A figure in a black suit traced with light: a visor across the helmet, a collar, seams down
    the arms and legs, a diamond on the chest, a belt, knee pads, glowing hands and the rims of the
    boots."""
    h, w = len(RUNNER), len(RUNNER[0])
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    cols = {'K': INK * 2.0, 'G': np.array([0.1, 0.1, 0.14], np.float32), 'L': LIGHT}
    for y, row in enumerate(RUNNER):
        for x, ch in enumerate(row):
            if ch in cols:
                rgba[y, x, :3] = cols[ch]
                rgba[y, x, 3] = 1.0
                em[y, x] = 1.0 if ch == 'L' else 0.0
    return rgba, em


def spr_light_trail():
    """A ribbon of light, uniform along its length: brightest at its top edge and fading down to
    the floor. A card - give it a `length` and an `angle` - drawn additively."""
    h, w = 16, 32
    prof = np.concatenate([[1.0, 1.0, 0.75], np.linspace(0.55, 0.18, h - 3)]).astype(np.float32)
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = LIGHT
    rgba[..., 3] = prof[:, None]
    return rgba, np.repeat(prof[:, None], w, 1)


def spr_light_beam():
    """A column of light rising from the floor, bright at its foot and core, fading upward."""
    h, w = 64, 16
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    core = np.exp(-((xx - (w - 1) / 2) / 2.2) ** 2)
    rise = 0.25 + 0.75 * (yy / (h - 1)) ** 1.5
    a = np.clip(core * rise, 0, 1)
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = LIGHT
    rgba[..., 3] = a
    return rgba, a


def spr_glint():
    """A point of light: a white-hot core in a soft halo - a headlight, a beacon, a star."""
    n = 9
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) - (n - 1) / 2
    d = np.hypot(yy, xx)
    a = np.clip(np.where(d <= 1.0, 1.0, 0.6 * np.exp(-(d - 1.0) / 1.2)), 0, 1)
    rgba = np.zeros((n, n, 4), np.float32)
    rgba[..., :3] = LIGHT
    rgba[..., 3] = a
    return rgba, a


TEXTURES = {'vector_grid': tex_vector_grid, 'vector_floor': tex_vector_floor, 'vector_frame': tex_vector_frame,
            'vector_circuit': tex_vector_circuit, 'vector_windows': tex_vector_windows,
            'vector_bands': tex_vector_bands, 'vector_data': tex_vector_data}
TEXTURE_NOISE = {k: 0.0 for k in TEXTURES}
SPRITES = {'vector_runner': spr_vector_runner, 'light_trail': spr_light_trail, 'light_beam': spr_light_beam,
           'glint': spr_glint}
SPRITE_HEIGHT = {'vector_runner': 0.6, 'light_trail': 0.22, 'light_beam': 3.0, 'glint': 0.09}
PROP_DEFAULTS = {'vector_runner': {'tint': [0.35, 1.0, 1.0]},
                 'light_trail': {'blend': 'additive', 'planes': 1, 'shadow': False, 'tint': [0.35, 1.0, 1.0]},
                 'light_beam': {'blend': 'additive', 'shadow': False, 'tint': [0.35, 1.0, 1.0]},
                 'glint': {'blend': 'additive', 'shadow': False}}
NO_CONTACT_SHADOW = {'light_trail', 'light_beam', 'glint'}

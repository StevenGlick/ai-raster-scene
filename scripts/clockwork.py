"""The clockwork city: brass and copper, gears the height of houses turning in the walls, clock faces on
every tower, pipes and steam, gaslight in a brown smog.

Textures: `brass_plate` (riveted brass panels, worn bright at their edges), `copper_pipes` (a wall run
with copper pipes, elbows and valves, green where they weep), `clock_face` (a clock dial on a dark
ground, one to a cell: stack it on a tower). Cards (`planes` 1 - stand them against a wall with
`angle` square to it): `brass_gear` (a great toothed wheel with spokes and a hub; `scale` sets its
size) and `great_clock` (a big dial in a brass ring, roman hours, the hands at ten to ten). An orrery
is wireframes: rings (`torus` meshes) tilted round a `sphere`, in brass.
"""
import math

import numpy as np

from biomes import T, _prop, _rng
from pixelart import Canvas, dither, ramp, smooth_noise

BRASS = ramp(['#3a2610', '#5c3e18', '#7e5a22', '#a37a2c', '#c79c3e', '#e6c264', '#fbe7a0'])
COPPER = ramp(['#3a1c10', '#5e2e18', '#874424', '#ad5e34', '#cf7f4c', '#eba574'])
PATINA = np.array([0.36, 0.62, 0.52], np.float32)


def tex_brass_plate(name):
    """Riveted brass panels, darker in their middles, worn bright at their edges, rivets round them."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T]
    lx, ly = xx % 32, yy % 32
    edge = np.minimum(np.minimum(lx, 31 - lx), np.minimum(ly, 31 - ly)).astype(np.float32)
    tone = rng.uniform(-0.06, 0.06, 4)[(yy // 32) * 2 + xx // 32]
    v = 0.42 + tone + 0.12 * (smooth_noise(T, T, 6, rng) - 0.5) + 0.22 * np.exp(-edge / 3.0)
    v = np.where(edge < 1, 0.1, v)
    rivet = ((lx - 3) % 6 == 0) & ((ly < 4) & (ly >= 2) | (ly > 27) & (ly <= 29)) | \
            ((ly - 3) % 6 == 0) & ((lx < 4) & (lx >= 2) | (lx > 27) & (lx <= 29))
    v = np.where(rivet, 0.95, v)
    return dither(np.clip(v, 0, 1), BRASS, 0.55)


def tex_copper_pipes(name):
    """A wall run with copper pipes: three upright, two across, an elbow, a valve wheel, green
    weeping where they join; dark iron behind them."""
    rng = _rng(name)
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    v = np.full((T, T), 0.12, np.float32) + 0.05 * (smooth_noise(T, T, 8, rng) - 0.5)
    pipe = np.zeros((T, T), bool)
    for cx, r in ((10, 4.5), (31, 6.0), (52, 3.5)):
        d = np.abs(xx - cx) / r
        on = d < 1
        v = np.where(on, 0.35 + 0.55 * np.sqrt(np.clip(1 - d * d, 0, 1)) - 0.1 * d, v)
        pipe |= on
    for cy, r in ((20, 3.5), (46, 5.0)):
        d = np.abs(yy - cy) / r
        on = (d < 1) & (xx > 6) & (xx < 58)
        v = np.where(on, 0.35 + 0.55 * np.sqrt(np.clip(1 - d * d, 0, 1)) - 0.1 * d, v)
        pipe |= on
    flange = ((np.abs(yy - 20) < 6) & (np.abs(xx - 31) < 8)) & ~((np.abs(yy - 20) < 4.5) & (np.abs(xx - 31) < 6.5))
    v = np.where(flange, 0.75, v)
    rgb = dither(np.clip(v, 0, 1), COPPER, 0.5)
    weep = pipe & (smooth_noise(T, T, 10, rng) > 0.72)
    rgb[weep] = rgb[weep] * 0.4 + PATINA * 0.6
    r = np.hypot(yy - 46, xx - 18)                            # a valve wheel on the lower pipe
    wheel = (np.abs(r - 5) < 1) | ((r < 5) & ((np.abs(yy - 46) < 0.8) | (np.abs(xx - 18) < 0.8)))
    rgb[wheel] = np.array([0.55, 0.12, 0.1], np.float32)
    return rgb


def tex_clock_face(name):
    """A clock dial on a dark ground: an ivory face in a brass ring, twelve hour marks, two hands."""
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    dx, dy = xx - 31.5, yy - 31.5
    r = np.hypot(dx, dy)
    a = np.arctan2(dy, dx)
    rgb = np.full((T, T, 3), 0.1, np.float32) * np.array([1.0, 0.85, 0.7], np.float32)
    face = r < 26
    rgb[face] = [0.86, 0.82, 0.7]
    ring = (r >= 26) & (r < 30)
    rgb[ring] = BRASS[4] * (0.8 + 0.2 * np.sin(a[ring] * 2))[:, None]
    marks = face & (r > 20) & (np.abs(((a / (2 * math.pi) * 12) % 1) - 0.5) > 0.42)
    rgb[marks] = [0.15, 0.12, 0.1]
    for ang, length, width in ((-math.pi / 2 - 2 * math.pi / 12 * 2, 14, 1.4), (-math.pi / 2 + 2 * math.pi / 12 * 2, 20, 0.9)):
        along = dx * math.cos(ang) + dy * math.sin(ang)
        across = np.abs(-dx * math.sin(ang) + dy * math.cos(ang))
        hand = (along > -2) & (along < length) & (across < width)
        rgb[hand] = [0.1, 0.08, 0.08]
    rgb[r < 2.5] = BRASS[5]
    return rgb


def spr_brass_gear():
    """A great brass gear: teeth all round, six spokes, a hub, light catching its upper edge."""
    n = 64
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    dx, dy = xx - 31.5, yy - 31.5
    r = np.hypot(dx, dy)
    a = np.arctan2(dy, dx)
    teeth = 28.5 + 2.8 * (np.cos(a * 16) > 0.1)
    rim = (r < teeth) & (r >= 21)
    spokes = (r < 21) & (r >= 7) & (np.abs(np.sin(a * 3)) < 7.0 / np.maximum(r, 1))
    hub = r < 7
    solid = rim | spokes | hub
    light = 0.55 + 0.35 * (-dy / np.maximum(r, 1)) * 0.6 - 0.15 * (r / 32)
    v = np.where(hub & (r < 3), 0.2, light + 0.15 * (rim & (r > teeth - 2.5)))
    rgb = dither(np.clip(v, 0, 1), BRASS, 0.55)
    edge = solid & ~(np.roll(solid, 1, 0) & np.roll(solid, -1, 0) & np.roll(solid, 1, 1) & np.roll(solid, -1, 1))
    rgb[edge] = rgb[edge] * 0.55
    rgba = np.concatenate([rgb, solid[..., None].astype(np.float32)], -1)
    return rgba.astype(np.float32), np.zeros((n, n), np.float32)


def spr_great_clock():
    """A tower's great clock: a big ivory dial in a heavy brass ring, roman hour marks, the hands at
    ten to ten."""
    rgb = tex_clock_face('great_clock')
    yy, xx = np.mgrid[0:T, 0:T].astype(np.float32)
    r = np.hypot(xx - 31.5, yy - 31.5)
    a = (r < 30.5).astype(np.float32)
    return np.concatenate([rgb, a[..., None]], -1).astype(np.float32), np.zeros((T, T), np.float32)


TEXTURES = {'brass_plate': lambda n: (tex_brass_plate(n), None), 'copper_pipes': lambda n: (tex_copper_pipes(n), None),
            'clock_face': lambda n: (tex_clock_face(n), None)}
TEXTURE_NOISE = {'brass_plate': 0.4, 'copper_pipes': 0.3, 'clock_face': 0.1}
SPRITES = {'brass_gear': spr_brass_gear, 'great_clock': spr_great_clock}
SPRITE_HEIGHT = {'brass_gear': 2.0, 'great_clock': 1.6}
PROP_DEFAULTS = {'brass_gear': {'planes': 1, 'shadow': False}, 'great_clock': {'planes': 1, 'shadow': False}}
NO_CONTACT_SHADOW = {'brass_gear', 'great_clock'}

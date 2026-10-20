"""Vector World: a world drawn in lines of light on black - the look of 80s vector arcade games and of
films set inside a computer. A city of towers ruled in neon stands on a grid that runs to the
horizon, racers trail ribbons of light down its avenue, a giant black core hangs over a plaza in a
ring of light beams, wire palms flank the gate into the city, and a striped sun sets between
wireframe mountains. A beacon on a pylon out on the plain throws a lens flare.

Shows the Vector World kit (scripts/vector.py): black textures ruled in white light that a cell's
`tint` colours - `vector_grid` (a wall of squares), `vector_floor` (the grid underfoot, made to
reflect), `vector_windows`, `vector_bands`, `vector_data`, `vector_circuit`, `vector_frame` - the
`vector_runner`, `light_trail`s, `light_beam`s and `glint`s; and `wireframes` (scripts/wires.py):
low-poly meshes projected in true 3D - `terrain` mountains, `pyramid`s, a `dodecahedron`, `crystal`s,
`racer`s, `palm`s, a `gate` - some `solid` (black faces that hide what is behind them). The sky is
`vector`, with a sun of `"disc_style": "stripes"`; the light is all bloom, the anamorphic streaks of the
racers' headlights, and flares from the sun and the beacon.
Run:  python vector_world.py  -> writes vector_world.json
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

CYAN, PINK, ORANGE = [0.3, 1.0, 1.0], [1.0, 0.3, 0.8], [1.0, 0.55, 0.15]
VIOLET, GREEN, WHITE = [0.62, 0.4, 1.0], [0.4, 1.0, 0.5], [0.9, 0.95, 1.0]
W, H = 60, 72
g = Grid(W, H, fill='.')
# the city: two rows of towers either side of an avenue (x 26-33) running north into the sunset
blocks = [  # x0, y0, x1, y1, legend
    (18, 6, 25, 15, 'A'), (20, 8, 24, 13, 'a'),             # west, the tower of windows on its podium
    (20, 18, 25, 27, 'B'),                                   # west, the grid tower
    (17, 30, 25, 39, 'C'), (19, 32, 23, 36, 'c'),            # west, bands
    (34, 6, 41, 15, 'D'),                                    # east, data
    (34, 18, 39, 27, 'E'), (35, 20, 38, 25, 'e'),            # east, the tallest: windows, with a beacon
    (34, 30, 42, 39, 'F'),                                   # east, circuits
]
for x0, y0, x1, y1, c in blocks:
    g.rect(x0, y0, x1, y1, c)
for y in range(46, 59):                                     # the plaza round the core: circuits underfoot
    for x in range(23, 38):
        if math.hypot(x + 0.5 - 30.5, y + 0.5 - 52.5) < 6.8:
            g.put(x, y, 'p')


def tower(tex, colour, storeys, top=None):
    return {'wall': [{'base': tex, 'tint': colour}] * storeys, 'h': float(storeys),
            'top': {'base': top or 'vector_frame', 'tint': colour}}


legend = {
    '.': {'floor': {'base': 'vector_floor', 'tint': [0.42, 0.22, 0.85]}, 'reflect': 0.4},
    'p': {'floor': {'base': 'vector_circuit', 'tint': [0.25, 0.75, 0.9]}, 'reflect': 0.4},
    'A': tower('vector_frame', CYAN, 3), 'a': tower('vector_windows', CYAN, 11),
    'B': tower('vector_grid', PINK, 7),
    'C': tower('vector_frame', ORANGE, 2), 'c': tower('vector_bands', ORANGE, 6),
    'D': tower('vector_data', GREEN, 8),
    'E': tower('vector_frame', VIOLET, 4), 'e': tower('vector_windows', VIOLET, 13),
    'F': {'wall': [{'base': 'vector_circuit', 'tint': CYAN}, {'base': 'vector_frame', 'tint': CYAN}] * 2 +
          [{'base': 'vector_circuit', 'tint': CYAN}], 'h': 5.0, 'top': {'base': 'vector_frame', 'tint': CYAN}},
}


def racer(x, y, heading, colour, trail=7.0, size=1.3):
    """A racer heading `heading` degrees with its headlights lit and a ribbon of light behind it."""
    a = math.radians(heading)
    fx, fy, sx, sy = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    nose, tail = (x + fx * 0.5 * size, y + fy * 0.5 * size), (x - fx * 0.5 * size, y - fy * 0.5 * size)
    mesh = {'mesh': 'racer', 'x': x, 'y': y, 'size': size, 'angle': heading, 'solid': True, 'color': colour}
    sprites = [{'x': nose[0] + fx * 0.06 * size + sx * k * 0.1 * size,       # just ahead of the nose
                'y': nose[1] + fy * 0.06 * size + sy * k * 0.1 * size, 'type': 'glint',
                'z': 0.05 * size, 'scale': 0.14, 'tint': [1.0, 1.0, 0.92]} for k in (-1, 1)]
    sprites.append({'x': tail[0] - fx * trail / 2, 'y': tail[1] - fy * trail / 2, 'type': 'light_trail',
                    'angle': heading, 'length': trail, 'tint': colour})
    return mesh, sprites


r1, s1 = racer(28.7, 32.0, 90, CYAN, trail=10.0, size=1.5)
r2, s2 = racer(30.8, 36.8, 90, ORANGE, trail=8.0, size=1.5)
r3, s3 = racer(30.6, 24.0, 90, PINK, trail=9.0, size=1.5)
beams = [(30.5 + 6.3 * math.cos(math.radians(a)), 52.5 + 6.3 * math.sin(math.radians(a))) for a in range(0, 360, 45)]
wireframes = [
    # the mountains on the horizon, the sun going down between them
    {'mesh': 'terrain', 'x': 12.0, 'y': -26.0, 'size': 44, 'scale': [1, 0.4, 0.3], 'solid': True, 'seed': 4,
     'gradient': [VIOLET, CYAN]},
    {'mesh': 'terrain', 'x': 50.0, 'y': -30.0, 'size': 50, 'scale': [1, 0.4, 0.32], 'solid': True, 'seed': 9,
     'gradient': [VIOLET, PINK]},
    {'mesh': 'terrain', 'x': -20.0, 'y': 20.0, 'size': 40, 'scale': [0.4, 1, 0.3], 'solid': True, 'seed': 12,
     'gradient': [VIOLET, CYAN]},
    {'mesh': 'terrain', 'x': 82.0, 'y': 30.0, 'size': 44, 'scale': [0.4, 1, 0.28], 'solid': True, 'seed': 6,
     'gradient': [VIOLET, PINK]},
    # the core over the plaza, a crystal turning above it
    {'id': 'core', 'mesh': 'dodecahedron', 'x': 30.5, 'y': 52.5, 'z': 2.2, 'size': 4.2, 'angle': 18, 'tilt': 24,
     'solid': True, 'color': WHITE, 'intensity': 1.1},
    {'mesh': 'crystal', 'x': 30.5, 'y': 52.5, 'z': 7.4, 'size': 1.6, 'tilt': 12, 'solid': True, 'color': CYAN},
    # the gate into the city, a wire spire on the tallest tower
    {'mesh': 'gate', 'x': 30.0, 'y': 42.0, 'scale': [8.4, 3.0, 4.6], 'solid': True, 'color': PINK},
    {'mesh': 'tower', 'x': 36.5, 'y': 22.5, 'z': 13.0, 'size': 2.4, 'scale': [1, 1, 1.6], 'solid': True,
     'color': VIOLET},
    {'id': 'pylon', 'mesh': 'tower', 'x': 56.0, 'y': 28.0, 'size': 3.0, 'scale': [1, 1, 2.4], 'solid': True,
     'color': ORANGE},                                  # a beacon out on the plain
    # pyramids out on the plain
    {'mesh': 'pyramid', 'x': 14.0, 'y': 50.0, 'size': 5.0, 'angle': 12, 'solid': True, 'color': ORANGE},
    {'mesh': 'pyramid', 'x': 47.0, 'y': 47.0, 'size': 6.5, 'angle': 40, 'solid': True, 'color': PINK},
    {'mesh': 'pyramid', 'x': 8.0, 'y': 36.0, 'size': 3.2, 'angle': 30, 'solid': True, 'color': CYAN},
    {'mesh': 'pyramid', 'x': 52.0, 'y': 60.0, 'size': 3.6, 'angle': 5, 'solid': True, 'color': ORANGE},
    {'mesh': 'octahedron', 'x': 46.0, 'y': 56.0, 'z': 1.2, 'size': 1.4, 'angle': 30, 'solid': True, 'color': CYAN},
    {'mesh': 'icosahedron', 'x': 15.0, 'y': 58.0, 'z': 0.9, 'size': 1.6, 'angle': 10, 'tilt': 20, 'solid': True,
     'color': PINK},
    r1, r2, r3,
] + [{'mesh': 'palm', 'x': x, 'y': y, 'size': 3.2, 'angle': (x * 37 + y * 11) % 360, 'color': PINK}
     for x, y in ((24.6, 43.6), (35.4, 43.6), (21.8, 46.2), (38.2, 46.2))]      # palms flank the gate
sprites = ([{'x': x, 'y': y, 'type': 'light_beam', 'scale': 5.0, 'tint': CYAN if k % 2 else PINK}
            for k, (x, y) in enumerate(beams)]
           + [{'id': 'runner', 'x': 26.4, 'y': 63.0, 'type': 'vector_runner'},
              {'id': 'rival', 'x': 32.8, 'y': 44.6, 'type': 'vector_runner', 'tint': ORANGE},
              {'x': 36.5, 'y': 22.5, 'type': 'glint', 'z': 17.1, 'scale': 0.3, 'tint': [1.0, 0.85, 1.0]},
              {'x': 56.0, 'y': 28.0, 'type': 'glint', 'z': 7.3, 'scale': 0.4, 'tint': [1.0, 0.92, 0.8]}]
           + s1 + s2 + s3)
lights = ([{'x': x, 'y': y, 'z': 0.5, 'radius': 3.0, 'color': CYAN if k % 2 else PINK, 'intensity': 0.8}
           for k, (x, y) in enumerate(beams)]
          + [{'type': 'sun', 'azimuth': 268, 'elevation': 9, 'intensity': 0.25, 'disc_style': 'stripes',
              'disc_size': 8, 'disc_color': [1.0, 0.3, 0.6]}])
NEON = {'fx': 'bloom', 'source': 'light', 'strength': 2.2, 'radius': 2.5, 'spread': 0.6}

s = scene(
    g,
    title='Vector World - a city of light on the grid',
    legend=legend,
    sky='vector',
    ambient=[0.04, 0.03, 0.06],
    fog={'color': [0.2, 0.05, 0.26], 'density': 0.016},
    max_distance=96,
    lights=lights,
    sprites=sprites,
    wireframes=wireframes,
    surface_noise=0,
    camera={'x': 30.5, 'y': 71.0, 'look_at': [30.5, 30.0, 4.0], 'fov': 70},
    shots=[
        {'x': 43.0, 'y': 70.0, 'height': 0.6, 'look_at': [31.0, 36.0, 4.5], 'fov': 70,
         'post': [dict(NEON, strength=1.6), {'fx': 'streaks', 'points': 6, 'angle': 15, 'count': 0},
                  {'fx': 'flare'}],
         'overlays': [{'type': 'caption', 'text': 'Vector World', 'at': 'top', 'box': True}]},
        {'x': 30.0, 'y': 39.5, 'height': 0.25, 'look_at': [30.0, 20.0, 0.5], 'fov': 70,
         'post': [NEON, {'fx': 'streaks', 'points': 2, 'length': 60, 'strength': 0.9, 'count': 6, 'gap': 10,
                         'color': [0.55, 0.75, 1.3]}]},
        {'x': 45.0, 'y': 41.0, 'height': 0.5, 'look_at': [52.0, 28.0, 2.0], 'fov': 72,
         'post': [NEON, {'fx': 'flare', 'source': 'light', 'strength': 1.6}]},
        {'x': 20.0, 'y': 57.5, 'height': 0.5, 'look_at': [30.5, 52.5, 3.4], 'fov': 66, 'post': [NEON]},
        {'x': 28.4, 'y': 64.4, 'height': 0.45, 'look_at': 'runner', 'fov': 46,
         'post': [{'fx': 'dof', 'blur': 2.5}, NEON]},
    ],
    contact_shadows=0.0,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vector_world.json')))

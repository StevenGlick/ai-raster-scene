"""Alien world: a landing site under a teal sky, a gas giant on the horizon, a monolith waiting.

Shows the `alien` sky with `sky_objects` (a ringed gas giant and two moons), an alien sun casting
long shadows, a purple mountain skyline, glowing `alien_rock` outcrops, a reflective pool, the
`alien` scatter set, and a raised plateau with steps (`heights`) carrying a monolith.
Run:  python alien_world.py  -> writes alien_world.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(40, 40, fill='.')
for (x, y, r, c) in ((5, 12, 2.6, 'R'), (31, 9, 3.2, 'R'), (6, 25, 2.2, 'r'), (31, 27, 2.6, 'R'),
                     (27, 34, 1.6, 'r'), (3, 34, 2.2, 'R'), (36, 18, 2.2, 'r'), (21, 4, 2.4, 'r')):
    g.disc(x, y, r, c)                                # outcrops of veined rock
g.disc(22, 20, 3.4, '~')                              # a glowing pool
g.rect(11, 9, 15, 13, 'P')                            # the plateau...
g.rect(12, 14, 14, 14, 'S')                           # ...and its step

heights = [list('.' * 40) for _ in range(40)]
for y in range(9, 14):
    for x in range(11, 16):
        heights[y][x] = '4'                           # plateau 0.4
for x in range(12, 15):
    heights[14][x] = '2'                              # step 0.2

s = scene(
    g,
    title='Alien world - the landing site',
    heights=[''.join(r) for r in heights],
    legend={
        '.': {'floor': 'alien_ground'},
        'R': {'wall': 'alien_rock', 'h': 2.2, 'top': 'alien_ground'},
        'r': {'wall': 'alien_rock', 'h': 1.1, 'top': 'alien_ground'},
        '~': {'floor': {'base': 'water', 'tint': [0.45, 1.1, 1.0]}, 'drop': 0.1, 'reflect': 0.6},
        'P': {'wall': 'alien_rock', 'top': 'hex_panel'},
        'S': {'wall': 'alien_rock', 'top': 'hex_panel'},
    },
    sky='alien',
    skyline={'type': 'mountains', 'color': [0.3, 0.22, 0.38], 'height': 1.15},
    sky_objects=[
        {'type': 'ringed', 'azimuth': 280, 'elevation': 11, 'size': 17, 'color': [0.5, 0.74, 0.86],
         'color2': [0.92, 0.86, 0.72], 'lit_from': 200, 'phase': 0.55, 'tilt': 0.3, 'angle': 16},
        {'type': 'moon', 'azimuth': 248, 'elevation': 31, 'size': 2.6, 'color': [0.86, 0.72, 0.76], 'lit_from': 180},
        {'type': 'moon', 'azimuth': 318, 'elevation': 38, 'size': 1.5, 'lit_from': 180},
    ],
    ambient=[0.24, 0.22, 0.28],
    fog={'color': [0.45, 0.58, 0.5], 'density': 0.02, 'sky_mix': 0.2},
    lights=[
        {'type': 'sun', 'azimuth': 135, 'elevation': 18, 'color': [0.92, 1.0, 0.86], 'intensity': 0.75},
        {'x': 22.0, 'y': 20.0, 'z': 0.3, 'radius': 5.0, 'color': [0.3, 1.0, 0.85], 'intensity': 0.9},
        {'x': 13.5, 'y': 12.6, 'z': 1.6, 'radius': 4.0, 'color': [0.7, 0.5, 1.0], 'intensity': 0.7},
        {'x': 13.5, 'y': 30.2, 'z': 0.3, 'radius': 3.6, 'color': [1.0, 0.75, 0.45], 'intensity': 0.9},
    ],
    sprites=[
        {'x': 13.5, 'y': 29.0, 'type': 'lander'},
        {'id': 'explorer', 'x': 13.0, 'y': 30.8, 'type': 'astronaut'},
        {'x': 18.4, 'y': 30.8, 'type': 'antenna', 'scale': 1.3},
        {'x': 13.5, 'y': 11.0, 'type': 'monolith'},
        {'id': 'native', 'x': 15.2, 'y': 12.3, 'type': 'alien'},
        {'x': 19.4, 'y': 18.4, 'type': 'alien_plant'}, {'x': 25.8, 'y': 21.0, 'type': 'alien_plant', 'scale': 1.2},
        {'x': 24.4, 'y': 17.4, 'type': 'alien_plant', 'scale': 0.8, 'flip': True},
        {'x': 20.0, 'y': 23.4, 'type': 'crystal', 'scale': 0.5}, {'x': 18.8, 'y': 21.2, 'type': 'crystal'},
    ],
    scatter=[{'of': 'alien', 'on': '.', 'density': 0.16, 'clump': 1.4, 'sizes': ['small', 'medium', 'large'],
              'seed': 6}],
    camera={'x': 11.0, 'y': 34.0, 'look_at': [15.0, 20.0, 0.8], 'fov': 72},
    shots=[
        {'x': 11.0, 'y': 34.0, 'look_at': [15.0, 20.0, 0.8], 'fov': 72,
         'overlays': [{'type': 'caption', 'text': 'Landing site, day one', 'at': 'top', 'box': True}]},
        {'x': 24.0, 'y': 26.5, 'look_at': [21.0, 14.0, 0.45], 'fov': 72},
        {'x': 13.5, 'y': 19.0, 'look_at': [13.5, 11.0, 1.0], 'fov': 64,
         'overlays': [{'type': 'bubble', 'anchor': 'native', 'text': 'You are not the first to land here.'}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alien_world.json')))

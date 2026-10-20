"""Kelp forest: the sea floor under a forest of giant kelp, sunbeams coming down through the water,
a shoal of fish turning, and the wreck of a ship with a diver in a brass helmet working round it.

Shows the sea kit - a `seabed` floor (rippled sand under a net of caustic light), `kelp` stalks
five units tall and a `kelp` fringe round the edges, rock outcrops, `fish_school`s, the `diver`
with `bubbles` rising from his helmet, an `anchor`, a `wreck_mast` and a hull of low blocks - and
how to make water of the air: a dense teal fog that swallows the sky, a high sun whose light
comes down between the kelp (`shafts`), and a teal `grade` over everything. The last shot is a night dive by
the diver's flashlight, jellyfish glowing in the dark.
Run:  python kelp_forest.py  -> writes kelp_forest.json next to this file.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402


def kelp_forest():
    g = Grid(36, 40, fill='K')                     # the reef all round, kelp standing in front of it
    g.disc(18, 21, 14, 's')
    g.rect(6, 8, 30, 38, 's')
    for x, y, r, c in ((9, 14, 1, 'r'), (27, 12, 1, 'q'), (25, 30, 1, 'r'), (10, 31, 1, 'q'), (14, 9, 0, 'r')):
        g.disc(x, y, r, c)                         # rock outcrops
    hull = [(16, 15), (17, 14), (18, 14), (19, 14), (20, 15), (21, 16), (21, 17), (21, 19), (20, 20), (16, 20),
            (15, 19), (15, 17), (15, 16)]           # the wreck's hull, broken open on the near side
    for x, y in hull:
        g.put(x, y, 'H')
    for x in range(16, 21):
        for y in range(15, 20):
            if g.get(x, y) == 's':
                g.put(x, y, 'd')                   # its deck, low and broken
    g.put(18, 20, 's'); g.put(19, 20, 's')          # a hole in the hull where we look in
    rng = np.random.default_rng(3)
    kelp = []
    for _ in range(60):                            # the forest: stalks everywhere but the clearing round the wreck
        x, y = rng.uniform(7, 30), rng.uniform(8, 37)
        if (x - 18) ** 2 + (y - 18) ** 2 < 30 or (abs(x - 18) < 2.2 and y > 30):
            continue
        if g.get(int(x), int(y)) != 's':
            continue
        kelp.append({'x': round(x, 2), 'y': round(y, 2), 'type': 'kelp', 'scale': round(rng.uniform(4.0, 5.6), 2),
                     'flip': bool(rng.random() < 0.5)})
    sprites = kelp + [
        {'x': 18.5, 'y': 17.5, 'type': 'wreck_mast', 'z': 0.6},
        {'x': 13.6, 'y': 21.4, 'type': 'anchor', 'flip': True},
        {'x': 19.4, 'y': 21.2, 'type': 'chest'},
        {'id': 'diver', 'x': 17.2, 'y': 21.8, 'type': 'diver', 'facing': 300},
        {'x': 17.25, 'y': 21.75, 'type': 'bubbles', 'z': 0.62, 'scale': 1.6},
        {'x': 22.0, 'y': 24.0, 'type': 'fish_school', 'z': 1.6, 'scale': 1.0},
        {'x': 13.0, 'y': 16.0, 'type': 'fish_school', 'z': 2.6, 'scale': 1.3, 'flip': True},
        {'x': 24.0, 'y': 14.0, 'type': 'fish_school', 'z': 3.2, 'scale': 0.8},
        {'x': 20.6, 'y': 26.2, 'type': 'crab'}, {'x': 15.0, 'y': 25.0, 'type': 'rocks'},
    ]
    decals = [{'tex': t, 'surface': 'floor', 'x': x, 'y': y, 'size': s_}
              for t, x, y, s_ in (('starfish', 16.4, 23.6, 0.6), ('shells', 21.4, 22.8, 0.8), ('seaweed', 14.6, 22.6, 1.2),
                                  ('starfish', 22.4, 27.4, 0.5), ('seaweed', 20.0, 29.0, 1.4))]
    night = [{'x': x, 'y': y, 'type': 'jellyfish', 'z': z, 'scale': 0.9} for x, y, z in ((15.4, 20.0, 1.6),
                                                                                         (19.6, 18.6, 2.2), (14.2, 17.0, 1.2),
                                                                                         (21.0, 21.6, 1.0))]
    return scene(
        g,
        legend={
            'K': {'wall': 'rock_wet', 'h': 0.8, 'top': 'seabed', 'fringe': 'kelp'},
            's': {'floor': 'seabed'},
            'r': {'wall': 'rock', 'h': 1.2, 'top': 'rock_floor'},
            'q': {'wall': 'rock', 'h': 0.7, 'top': 'rock_floor'},
            'H': {'wall': 'planks', 'h': 1.1, 'top': 'planks'},
            'd': {'wall': 'planks', 'h': 0.45, 'top': 'boards'},
        },
        title='Kelp forest - the floor of the sea, a wreck and a diver',
        sky='day',
        ambient=[0.08, 0.2, 0.22],
        fog={'color': [0.0, 0.15, 0.19], 'density': 0.05, 'shafts': 0.9, 'anisotropy': 0.35},
        lights=[{'type': 'sun', 'azimuth': 105, 'elevation': 66, 'intensity': 1.15}],
        post=[{'fx': 'grade', 'tint': [0.74, 0.98, 1.05], 'saturation': 1.1}, {'fx': 'vignette', 'strength': 0.4}],
        sprites=sprites,
        decals=decals,
        scatter=[{'of': 'seabed', 'on': 's', 'density': 0.15, 'sizes': {'tiny': 3, 'small': 2}, 'seed': 4}],
        camera={'x': 18.2, 'y': 36.5, 'angle': 270, 'fov': 68, 'height': 0.7},
        shots=[
            {'x': 18.4, 'y': 31.5, 'angle': 268, 'height': 0.8,
             'overlays': [{'type': 'caption', 'text': 'Forty feet down', 'at': 'top', 'box': True}]},
            {'x': 16.0, 'y': 26.4, 'look_at': [17.6, 19.0, 1.0], 'fov': 64, 'height': 0.9},
            {'x': 23.0, 'y': 28.0, 'look_at': [13.0, 16.0, 2.2], 'fov': 70, 'height': 1.2},
            {'x': 16.6, 'y': 24.6, 'look_at': [17.6, 19.0, 1.0], 'fov': 64, 'height': 0.9, 'flashlight': True,
             'extra_sprites': night,
             'overrides': {'sky': 'night', 'ambient': [0.05, 0.09, 0.12],
                           'lights': [{'x': j['x'], 'y': j['y'], 'z': j['z'], 'radius': 3.0, 'color': [0.55, 0.85, 1.0],
                                       'intensity': 1.1} for j in night],            # the jellyfish light the water
                           'fog': {'color': [0.0, 0.05, 0.08], 'density': 0.03, 'glow': 1.0}}},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(kelp_forest().save(os.path.join(HERE, 'kelp_forest.json')))

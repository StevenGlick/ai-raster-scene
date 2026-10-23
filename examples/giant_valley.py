"""A mountain valley at landscape scale - the world as a giant sees it, a map cell about 100 m and the camera's eye
fifty metres up: a river winding down a valley floor of `farmland` and `pasture`, a `village` by the water with its
church and an old stone `bridge`, a hamlet further up, woods of `forest_canopy` and `pine_canopy` on the flanks with tiny trees standing
at their edges (a `scatter` with a `scale`), and `mountain`s - ranges either side and a great peak at the valley's
head, snow on their tops. Dawn: mist lies along the valley floor and the first sun catches the peaks.
Run:  python giant_valley.py  -> writes giant_valley.json next to this file.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 56, 52


def river_x(y):
    """Where the river runs at row y: down the middle of the valley, winding."""
    return 28 + 4.5 * math.sin(y / 7.0) + 1.5 * math.sin(y / 3.1)


def giant_valley():
    rng = random.Random(11)
    g = Grid(W, H, fill='w')
    for y in range(H):
        rx = river_x(y)
        for x in range(W):
            d = abs(x + 0.5 - rx)
            if d < 1.3:
                ch = 'r'                                # the river
            elif d < 2.8:
                ch = 'm'                                # water meadows
            elif d < 8.0 + 2 * math.sin(y / 5.0) + rng.random():
                ch = rng.choice('abcdef')               # the valley floor's fields, six layouts at random
            elif d < 14.0 + rng.random():
                ch = 'w'                                # broadleaf woods on the lower flanks
            else:
                ch = 'p'                                # pines higher up
            g.put(x, y, ch)
    mountains = []
    for y in range(4, H - 6, 5):                        # a range either side
        for side in (-1, 1):
            x = river_x(y) + side * rng.uniform(22, 26)
            mountains.append({'type': 'mountain', 'x': round(x, 2), 'y': y + rng.uniform(-1, 1), 'angle': 90,
                              'size': round(rng.uniform(12, 16), 2), 'length': round(rng.uniform(16, 24), 2),
                              'height': round(rng.uniform(5.5, 9.5), 2), 'seed': rng.randrange(1000)})
    mountains.append({'type': 'mountain', 'x': 28.0, 'y': -6.0, 'size': 30, 'length': 40, 'height': 16, 'seed': 77,
                      'ridges': 6})
    bridge = {'type': 'bridge', 'style': 'stone', 'x': round(river_x(34.0), 2), 'y': 34.0, 'length': 5.2, 'span': 0.85,
              'seed': 4}                                          # the village's old bridge over the river
    villages = [{'type': 'village', 'x': river_x(34) + 2.6, 'y': 34.0, 'size': 3.2, 'count': 26, 'seed': 3},
                {'type': 'village', 'x': river_x(16) - 2.4, 'y': 16.0, 'size': 1.6, 'count': 9, 'seed': 8,
                 'church': False}]
    return scene(
        g,
        title='The giant valley - mountains, woods and a village at landscape scale',
        legend={
            'r': {'floor': 'river_water'},
            'm': {'floor': 'pasture'},
            'a': {'floor': 'farmland'}, 'b': {'floor': 'farmland_b'}, 'c': {'floor': 'farmland_c'},
            'd': {'floor': 'farmland_d'}, 'e': {'floor': 'farmland_e'}, 'f': {'floor': 'farmland_f'},
            'w': {'floor': 'forest_canopy'},
            'p': {'floor': 'pine_canopy'},
        },
        sky='day',
        skyline='mountains',
        ambient=[0.42, 0.42, 0.46],
        lights=[{'type': 'sun', 'azimuth': 200, 'elevation': 30, 'intensity': 1.2}],
        fog={'color': [0.72, 0.76, 0.84], 'density': 0.008, 'ground': 0.22, 'height': 0.1, 'noise': 0.7,
             'scale': 3.0, 'shafts': 0.5},
        objects=mountains + villages + [bridge],
        scatter=[{'of': ['pine', 'pine', 'tree'], 'on': 'w', 'density': 3.0, 'scale': 0.09, 'seed': 5},
                 {'of': 'pine', 'on': 'p', 'density': 3.0, 'scale': 0.09, 'seed': 6}],
        time='dawn',
        camera={'x': 27.0, 'y': 50.0, 'look_at': [28.0, 20.0, 2.5], 'fov': 66, 'height': 0.6},
        shots=[
            {'x': 27.0, 'y': 50.0, 'look_at': [28.0, 20.0, 2.5], 'fov': 66, 'height': 0.6},
            {'x': 27.2, 'y': 36.6, 'look_at': [24.6, 34.0, 0.02], 'fov': 60, 'height': 0.22},
            {'x': 28.0, 'y': 51.5, 'look_at': [28.0, 24.0, 0.0], 'fov': 70, 'height': 4.0},
            {'x': 27.0, 'y': 50.0, 'look_at': [28.0, 20.0, 2.5], 'fov': 66, 'height': 0.6, 'time': 'afternoon'},
        ],
        max_distance=80,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(giant_valley().save(os.path.join(HERE, 'giant_valley.json')))

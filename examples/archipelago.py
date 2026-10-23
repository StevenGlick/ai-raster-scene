"""The archipelago: tropical islands in a blue sea, at landscape scale.

A map cell is about 100 m. Deep `ocean`, and three islands in it: a high one, its jungle hill a `mountain` of
`tropical` rock, a village of thatch (`"roof": "thatch"`) on its shore; a smaller one beside it; and a low atoll,
a ring of `white_sand` and `palm_canopy` round a `lagoon`. Every island is fringed with white sand and palms and
ringed with reef (`reef_flat`) in turquoise shallows, `sailboat`s at anchor in them. The afternoon, from a boat,
from the air, and golden hour.
Run:  python archipelago.py  -> writes archipelago.json next to this file.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 60, 52
ISLANDS = [(22.0, 22.0, 6.5, 'high'), (40.0, 15.0, 3.6, 'high'), (43.0, 36.0, 4.2, 'atoll')]   # x, y, radius, kind


def archipelago():
    rng = random.Random(71)
    g = Grid(W, H, fill='~')
    for y in range(H):
        for x in range(W):
            for cx, cy, r, kind in ISLANDS:
                a = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
                rr = r * (1 + 0.14 * math.sin(a * 3 + cx) + 0.08 * math.sin(a * 5 + cy))
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if d < rr + 2.6:
                    ch = 'r' if d > rr + 1.1 else 'l' if d > rr else 's' if d > rr - 1.0 else 'p'
                    if kind == 'atoll' and d < rr - 1.6:
                        ch = 'l'                                          # the atoll's lagoon
                    if g.get(x, y) in ('~', 'r', 'l') or ch in ('s', 'p'):
                        g.put(x, y, ch)
    hills = [{'type': 'mountain', 'x': 21.4, 'y': 21.2, 'size': 8.5, 'length': 10, 'height': 2.4, 'rock': 'tropical',
              'snowline': 0, 'seed': 5, 'ridges': 5},
             {'type': 'mountain', 'x': 40.2, 'y': 14.6, 'size': 4.6, 'height': 1.3, 'rock': 'tropical',
              'snowline': 0, 'seed': 9}]
    village = {'type': 'village', 'x': 17.5, 'y': 27.4, 'size': 1.8, 'count': 9, 'roof': 'thatch', 'church': False,
               'seed': 4, 'angle': 20}
    boats = [{'x': 15.6, 'y': 29.6, 'type': 'sailboat'}, {'x': 19.6, 'y': 30.6, 'type': 'sailboat', 'flip': True},
             {'x': 43.2, 'y': 36.4, 'type': 'sailboat'}, {'x': 33.0, 'y': 26.0, 'type': 'ferry', 'flip': True}]
    return scene(
        g,
        title='The archipelago - tropical islands in a blue sea, at landscape scale',
        legend={
            '~': {'floor': 'ocean'},
            'r': {'floor': 'reef_flat'},
            'l': {'floor': 'lagoon'},
            's': {'floor': 'white_sand'},
            'p': {'floor': 'palm_canopy'},
        },
        sky='day',
        skyline='islands',
        ambient=[0.48, 0.48, 0.52],
        lights=[{'type': 'sun', 'azimuth': 120, 'elevation': 45, 'intensity': 1.3}],
        fog={'color': [0.78, 0.86, 0.94], 'density': 0.006},
        objects=hills + [village],
        sprites=boats,
        scatter=[{'of': 'palm', 'on': 'p', 'density': 1.2, 'scale': 0.07, 'seed': 2}],
        time='afternoon',
        camera={'x': 13.0, 'y': 36.0, 'look_at': [22.0, 22.0, 1.0], 'fov': 60, 'height': 0.06},
        shots=[
            {'x': 13.0, 'y': 36.0, 'look_at': [22.0, 22.0, 1.0], 'fov': 60, 'height': 0.06},
            {'x': 30.0, 'y': 50.0, 'look_at': [30.0, 24.0, 0.0], 'fov': 64, 'height': 3.2},
            {'x': 44.5, 'y': 40.4, 'look_at': [42.0, 31.0, 0.1], 'fov': 64, 'height': 0.3},
            {'x': 13.0, 'y': 36.0, 'look_at': [22.0, 22.0, 1.0], 'fov': 60, 'height': 0.06, 'time': 'golden'},
        ],
        max_distance=70,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(archipelago().save(os.path.join(HERE, 'archipelago.json')))

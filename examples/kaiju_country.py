"""The kaiju in the country: an afternoon at landscape scale, something enormous walking in across the fields.

A map cell is about 100 m. The plain is a patchwork of `farmland` with woods in it (`forest_canopy`, small trees
along their edges), crossed by country roads (`road_ew`, `road_ns`, a crossroads `road_x`) with a market town at
the crossing - its blocks of low buildings on `city_street` and a `village` of cottages and a church beside it.
A line of electricity `pylon`s marches across the fields, `cable` slung from arm to arm; beyond it the `kaiju`
walks in from the hills (rounded `mountain`s), `jet`s passing over it, `helicopter`s at its shoulder, `tanks`
drawn up across the road, a field burning where it has been.
Run:  python kaiju_country.py  -> writes kaiju_country.json next to this file.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 48, 40
KAIJU = (21.5, 19.3)
ROAD_Y, ROAD_X = 26, 14                    # the roads' rows and columns; they cross at the town
P0, P1 = (3.5, 30.5), (45.5, 8.5)          # the pylon line's ends
ARMS = [(0.495, 0.07), (0.458, 0.09), (0.43, 0.066)]    # each arm's height and reach, from the pylon sprite


def pylons():
    """The pylons along the line, turned square to it, and their cables from arm tip to arm tip."""
    dx, dy = P1[0] - P0[0], P1[1] - P0[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    n = int(L / 4.4)
    at = [(P0[0] + ux * L * k / n, P0[1] + uy * L * k / n) for k in range(n + 1)]
    sprites = [{'x': round(x, 3), 'y': round(y, 3), 'type': 'pylon', 'angle': round(math.degrees(math.atan2(dy, dx)), 1)}
               for x, y in at]
    cables = []
    for (ax, ay), (bx, by) in zip(at, at[1:]):
        for z, off in ARMS:
            for side in (-1, 1):
                ox, oy = nx * off * side, ny * off * side
                cables.append({'type': 'cable', 'x': round(ax + ox, 4), 'y': round(ay + oy, 4), 'z': z,
                               'to': [round(bx + ox, 4), round(by + oy, 4), z], 'sag': 0.09, 'width': 0.006})
    return sprites, cables


def kaiju_country():
    rng = random.Random(23)
    g = Grid(W, H, fill='a')
    for y in range(H):
        for x in range(W):
            g.put(x, y, rng.choice('abcdef'))
    for cx, cy, r in ((8, 8, 3.2), (38, 30, 3.6), (19, 35, 2.4), (41, 16, 2.6), (5, 20, 2.0)):   # woods
        for y in range(H):
            for x in range(W):
                if math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 1.2) < r + rng.random() * 0.8:
                    g.put(x, y, 'w')
    g.rect(0, ROAD_Y, W - 1, ROAD_Y, '-')
    g.rect(ROAD_X, 0, ROAD_X, H - 1, '|')
    g.put(ROAD_X, ROAD_Y, '+')
    g.rect(ROAD_X + 1, ROAD_Y - 3, ROAD_X + 3, ROAD_Y - 1, 's')        # the town's streets, north-east of the crossing
    town = [{'type': 'city_block', 'x': x + 0.5, 'y': y + 0.5, 'height': [0.03, 0.1], 'count': rng.choice((2, 3)),
             'style': ['brick', 'apartment', 'office'], 'seed': rng.randrange(1 << 16)}
            for x in range(ROAD_X + 1, ROAD_X + 4) for y in range(ROAD_Y - 3, ROAD_Y)]
    mountains = []
    for k in range(9):                                                  # hills to the north
        mountains.append({'type': 'mountain', 'x': -4 + k * 7 + rng.uniform(-1.5, 1.5), 'y': -7 + rng.uniform(-2, 2),
                          'size': round(rng.uniform(13, 19), 2), 'length': round(rng.uniform(15, 24), 2),
                          'height': round(rng.uniform(3.5, 6.5), 2), 'snowline': 0, 'seed': rng.randrange(1000)})
    pyl, cables = pylons()
    sprites = [{'id': 'kaiju', 'x': KAIJU[0], 'y': KAIJU[1], 'type': 'kaiju'},
               {'x': 19.6, 'y': 17.9, 'type': 'jet', 'z': 1.0}, {'x': 20.9, 'y': 18.3, 'type': 'jet', 'z': 1.1},
               {'x': 19.2, 'y': 20.7, 'type': 'helicopter', 'z': 0.42}, {'x': 24.0, 'y': 18.8, 'type': 'helicopter',
                                                                          'z': 0.5, 'flip': True},
               {'x': 19.4, 'y': ROAD_Y + 0.35, 'type': 'tanks_firing', 'flip': True},
               {'x': 22.2, 'y': ROAD_Y + 0.35, 'type': 'tanks_firing'},
               {'x': 24.2, 'y': 18.4, 'type': 'blaze', 'scale': 0.6}, {'x': 24.3, 'y': 18.3, 'type': 'smoke_plume'},
               {'x': 25.8, 'y': 17.2, 'type': 'blaze', 'scale': 0.4}] + pyl
    return scene(
        g,
        title='The kaiju in the country - an afternoon at landscape scale',
        legend={
            'a': {'floor': 'farmland'}, 'b': {'floor': 'farmland_b'}, 'c': {'floor': 'farmland_c'},
            'd': {'floor': 'farmland_d'}, 'e': {'floor': 'farmland_e'}, 'f': {'floor': 'farmland_f'},
            'w': {'floor': 'forest_canopy'},
            '-': {'floor': 'road_ew'}, '|': {'floor': 'road_ns'}, '+': {'floor': 'road_x'},
            's': {'floor': 'city_street'},
        },
        sky='day',
        skyline='hills',
        ambient=[0.44, 0.44, 0.48],
        lights=[{'type': 'sun', 'azimuth': 140, 'elevation': 34, 'intensity': 1.25},
                {'x': 24.2, 'y': 18.4, 'z': 0.1, 'radius': 1.2, 'color': [1.0, 0.55, 0.22], 'intensity': 0.8}],
        fog={'color': [0.74, 0.78, 0.84], 'density': 0.012},
        sprites=sprites,
        objects=town + [{'type': 'village', 'x': ROAD_X - 2.6, 'y': ROAD_Y + 2.8, 'size': 2.6, 'count': 18, 'seed': 5}]
        + mountains + cables,
        scatter=[{'of': ['tree', 'tree', 'pine'], 'on': 'w', 'density': 2.5, 'scale': 0.09, 'seed': 4}],
        time='afternoon',
        camera={'x': 18.4, 'y': 24.1, 'look_at': [21.5, 19.3, 0.34], 'fov': 44, 'height': 0.11},
        shots=[
            {'x': 18.4, 'y': 24.1, 'look_at': [21.5, 19.3, 0.34], 'fov': 44, 'height': 0.11},
            {'x': 19.7, 'y': 21.2, 'look_at': [21.5, 19.3, 0.38], 'fov': 58, 'height': 0.45},
            {'x': 19.6, 'y': 22.4, 'look_at': [21.2, 19.9, 0.42], 'fov': 70, 'height': 0.03},
            {'x': 10.0, 'y': 25.0, 'look_at': [21.0, 20.6, 0.25], 'fov': 19, 'height': 0.1, 'time': 'golden'},
        ],
        max_distance=70,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(kaiju_country().save(os.path.join(HERE, 'kaiju_country.json')))

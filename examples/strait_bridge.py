"""The strait bridge: a suspension bridge across a sea strait at landscape scale, ships passing under it.

A map cell is about 100 m. Two green shores face each other across two kilometres of sea (`harbor_water`): a
town on the northern one where the bridge comes ashore, its quay along the water, woods and pasture and rounded
hills behind (`mountain`s with no snow); on the southern one woods and a `lighthouse` on its point, scaled down.
The `bridge` - a suspension bridge, its towers two hundred metres tall, its main cables slung over them - spans
the strait, and under it a `cargo_ship`, a `ferry` and `sailboat`s go by. Golden hour, and the same at dusk
with the bridge `lit` - and one night the `kaiju_wading` comes up the strait to it.
Run:  python strait_bridge.py  -> writes strait_bridge.json next to this file.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 60, 46
BX = 30.0                                  # the bridge's line, north to south


def north_coast(x):
    return 12.5 + 1.6 * math.sin(x / 5.0) + 0.9 * math.sin(x / 2.3)


def south_coast(x):
    return 32.5 + 1.8 * math.sin(x / 4.0 + 1.0) + 0.8 * math.sin(x / 1.9)


def strait_bridge():
    rng = random.Random(61)
    g = Grid(W, H, fill='~')
    for y in range(H):
        for x in range(W):
            n, s_ = north_coast(x + 0.5), south_coast(x + 0.5)
            if y + 0.5 < n or y + 0.5 > s_:
                shore = min(abs(y + 0.5 - n), abs(y + 0.5 - s_))
                woods = math.sin(x / 3.1 + 1.3) + math.sin(y / 2.7) + 0.6 * math.sin((x + y) / 1.7) > -0.2
                g.put(x, y, 'k' if shore < 0.8 else 'w' if woods else 'm')       # woods and fields in patches
    for x in range(int(BX) - 3, int(BX) + 4):                         # the town where the bridge comes ashore
        for y in range(int(north_coast(x + 0.5)) - 4, int(north_coast(x + 0.5)) - 1):
            g.put(x, y, 's')
        g.put(x, int(north_coast(x + 0.5)) - 1, 'q')
    town = [{'type': 'city_block', 'x': x + 0.5, 'y': y + 0.5, 'height': [0.03, 0.12], 'count': 2, 'lit': 0.5,
             'style': ['brick', 'apartment', 'office'], 'seed': rng.randrange(1 << 16)}
            for y in range(H) for x in range(W) if g.get(x, y) == 's']
    ny, sy = north_coast(BX) - 1.5, south_coast(BX) + 1.5
    span = sy - ny
    bridge = {'type': 'bridge', 'x': BX, 'y': (ny + sy) / 2, 'angle': 90, 'length': round(span, 2), 'deck': 0.55,
              'height': 1.9, 'lit': True}
    hills = [{'type': 'mountain', 'x': 6 + k * 9 + rng.uniform(-2, 2), 'y': 2 + rng.uniform(-2, 2), 'size': 9,
              'length': 13, 'height': round(rng.uniform(1.8, 3.0), 2), 'snowline': 0, 'seed': rng.randrange(1000)}
             for k in range(7)]
    hills += [{'type': 'mountain', 'x': 4 + k * 12 + rng.uniform(-2, 2), 'y': 43 + rng.uniform(-1, 1), 'size': 8,
               'length': 12, 'height': round(rng.uniform(1.4, 2.4), 2), 'snowline': 0, 'seed': rng.randrange(1000)}
              for k in range(5)]
    point = (42.0, south_coast(42.0) + 0.6)
    lighthouse = {'type': 'lighthouse', 'x': point[0], 'y': point[1], 'scale': 0.04}
    sprites = [{'x': 25.5, 'y': 24.5, 'type': 'cargo_ship', 'flip': True},
               {'x': 36.0, 'y': 17.0, 'type': 'ferry'},
               {'x': 23.0, 'y': 27.2, 'type': 'sailboat'}, {'x': 45.0, 'y': 25.0, 'type': 'sailboat', 'flip': True},
               {'x': 17.0, 'y': 22.0, 'type': 'sailboat'}]
    monster = [{'id': 'kaiju', 'x': 30.75, 'y': 21.0, 'type': 'kaiju_wading', 'facing': 90},
               {'x': 31.9, 'y': 20.2, 'type': 'helicopter', 'z': 0.62, 'flip': True},
               {'x': 29.0, 'y': 20.6, 'type': 'helicopter', 'z': 0.7},
               {'x': 22.0, 'y': 19.5, 'type': 'cargo_ship', 'flip': True}]
    night = {'time': 'night', 'sprites': monster,
             'lights': [{'type': 'moon', 'azimuth': 300, 'elevation': 26, 'intensity': 0.3},
                        {'x': 31.6, 'y': 21.0, 'z': 0.3, 'radius': 1.0, 'color': [0.45, 0.85, 1.0], 'intensity': 0.5}],
             'fog': {'color': [0.1, 0.1, 0.14], 'density': 0.02, 'glow': 0.7}}
    return scene(
        g,
        title='The strait bridge - a suspension bridge over a sea strait, at landscape scale',
        legend={
            '~': {'floor': 'harbor_water'},
            'k': {'floor': 'black_sand'},
            'w': {'floor': 'forest_canopy'},
            'm': {'floor': 'pasture'},
            's': {'floor': 'city_street_lit'},
            'q': {'floor': 'quay'},
        },
        sky='day',
        skyline='hills',
        ambient=[0.44, 0.44, 0.48],
        lights=[{'type': 'sun', 'azimuth': 180, 'elevation': 30, 'intensity': 1.25}],
        fog={'color': [0.76, 0.78, 0.84], 'density': 0.01},
        objects=[bridge, lighthouse] + town + hills,
        sprites=sprites,
        scatter=[{'of': ['tree', 'pine'], 'on': 'w', 'density': 1.5, 'scale': 0.09, 'seed': 3}],
        time='golden',
        camera={'x': 20.0, 'y': 29.5, 'look_at': [30.0, 22.0, 1.0], 'fov': 62, 'height': 0.06},
        shots=[
            {'x': 20.0, 'y': 29.5, 'look_at': [30.0, 22.0, 1.0], 'fov': 62, 'height': 0.06},
            {'x': 33.6, 'y': 14.7, 'look_at': [30.0, 26.0, 0.8], 'fov': 62, 'height': 0.08},
            {'x': 42.0, 'y': 36.0, 'look_at': [30.0, 22.0, 0.2], 'fov': 62, 'height': 2.0},
            {'x': 20.0, 'y': 29.5, 'look_at': [30.0, 22.0, 1.0], 'fov': 62, 'height': 0.06, 'time': 'dusk',
             'post': [{'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.2, 'spread': 0.5}]},
            {'x': 32.9, 'y': 23.5, 'look_at': [30.6, 20.8, 0.42], 'fov': 60, 'height': 0.12, 'overrides': night,
             'post': [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.5}]},
        ],
        max_distance=70,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(strait_bridge().save(os.path.join(HERE, 'strait_bridge.json')))

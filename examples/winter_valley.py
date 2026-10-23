"""The winter valley: a frozen lake, a village with its lamps lit and snow on its roofs, under the aurora - at
landscape scale.

A map cell is about 100 m. The valley floor is fields under snow (`snow_fields`), its flanks pines under snow
(`snow_forest`, little `snowy_pine`s along their edges); in the middle a `frozen_lake`, a `village` on its north
shore - `"snow": true` lays its roofs under snow and `lit` puts lamps in its windows - and a hamlet up the
valley; `mountain`s all round, white nearly to their feet (a low `snowline`). The sky is the `aurora`, its great
curtain in the north, so every shot looks north up the valley. The last shot is the morning after.
Run:  python winter_valley.py  -> writes winter_valley.json next to this file.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 56, 56
LAKE = (28.0, 31.0, 8.0, 5.5)              # its middle and radii


def winter_valley():
    rng = random.Random(53)
    g = Grid(W, H, fill='p')
    for y in range(H):
        for x in range(W):
            d = abs(x + 0.5 - 28 - 2.5 * math.sin(y / 9.0))
            if d < 12 + 2 * math.sin(y / 6.0) + rng.random():
                g.put(x, y, rng.choice('ab'))                            # the valley floor's fields
            lx, ly, rx, ry = LAKE
            a = math.atan2(y + 0.5 - ly, x + 0.5 - lx)
            if math.hypot((x + 0.5 - lx) / rx, (y + 0.5 - ly) / ry) < 1 + 0.12 * math.sin(a * 3 + 0.7):
                g.put(x, y, rng.choice('ijk'))
    mountains = []
    for y in range(-2, H - 10, 6):                                        # ranges either side
        for side in (-1, 1):
            mountains.append({'type': 'mountain', 'x': round(28 + side * rng.uniform(21, 25), 2),
                              'y': y + rng.uniform(-1.5, 1.5), 'angle': 90, 'size': round(rng.uniform(12, 16), 2),
                              'length': round(rng.uniform(15, 22), 2), 'height': round(rng.uniform(5, 8), 2),
                              'snowline': 0.02, 'seed': rng.randrange(1000)})
    mountains.append({'type': 'mountain', 'x': 26.0, 'y': -9.0, 'size': 26, 'length': 36, 'height': 13, 'seed': 12,
                      'ridges': 5, 'snowline': 0.02})
    villages = [{'type': 'village', 'x': 28.0, 'y': 23.2, 'size': 2.8, 'count': 22, 'seed': 6, 'snow': True, 'lit': 0.55},
                {'type': 'village', 'x': 38.5, 'y': 13.5, 'size': 1.2, 'count': 6, 'seed': 2, 'snow': True, 'lit': 0.5,
                 'church': False}]
    glow = [{'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.2, 'spread': 0.5}]
    lamps = [{'x': 28.0 + dx, 'y': 23.2 + dy, 'z': 0.05, 'radius': 0.7, 'color': [1.0, 0.72, 0.4], 'intensity': 0.7,
              'night': True} for dx, dy in ((-0.9, 0.1), (0.0, -0.2), (0.9, 0.2), (0.3, 0.6))]
    return scene(
        g,
        title='The winter valley - a frozen lake and a lit village under the aurora, at landscape scale',
        legend={
            'a': {'floor': 'snow_fields'}, 'b': {'floor': 'snow_fields_b'},
            'p': {'floor': 'snow_forest'},
            'i': {'floor': 'frozen_lake'}, 'j': {'floor': 'frozen_lake_b'}, 'k': {'floor': 'frozen_lake_c'},
        },
        sky='aurora',
        ambient=[0.14, 0.16, 0.22],
        lights=[{'type': 'moon', 'azimuth': 210, 'elevation': 22, 'intensity': 0.34, 'disc': False}] + lamps,
        fog={'color': [0.1, 0.13, 0.18], 'density': 0.01},
        objects=mountains + villages,
        scatter=[{'of': 'snowy_pine', 'on': 'p', 'density': 2.5, 'scale': 0.09, 'seed': 7}],
        camera={'x': 28.0, 'y': 47.0, 'look_at': [28.0, 22.0, 2.4], 'fov': 66, 'height': 0.5},
        shots=[
            {'x': 28.0, 'y': 36.5, 'look_at': [28.0, 20.0, 1.6], 'fov': 64, 'height': 0.3, 'post': glow},
            {'x': 28.3, 'y': 26.4, 'look_at': [28.0, 22.6, 0.3], 'fov': 58, 'height': 0.03, 'post': glow},
            {'x': 27.4, 'y': 24.4, 'look_at': [27.0, 10.0, 2.5], 'fov': 70, 'height': 0.05, 'post': glow},
            {'x': 28.0, 'y': 47.0, 'look_at': [28.0, 22.0, 2.4], 'fov': 66, 'height': 0.5,
             'overrides': {'time': 'morning', 'sky': 'day', 'ambient': [0.5, 0.52, 0.58],
                           'fog': {'color': [0.78, 0.82, 0.88], 'density': 0.01}}},
        ],
        max_distance=80,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(winter_valley().save(os.path.join(HERE, 'winter_valley.json')))

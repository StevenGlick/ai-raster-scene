"""The mesa desert: buttes and mesas standing out of a red plain, at landscape scale, from golden hour to night.

A map cell is about 100 m. The plain is `desert_floor` (three layouts, mixed), a highway (`desert_road`) running
straight across it toward the monuments - `mountain`s of `sandstone` and `canyon` rock with a `cliff`: a slope
of talus up to sheer walls and a flat top, buttes standing alone, spires, long mesas - each casting its shadow
across the plain in the low sun (`casts`). A lone ranch by the road (a `village` of four, no church). Shots: down
the road at golden hour, from the air, the monuments against the sunset, and the road again by moonlight.
Run:  python mesa_desert.py  -> writes mesa_desert.json next to this file.
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 60, 56
ROAD = 30
# x, y, size, length, height, cliff, angle, rock: the monuments
MONUMENTS = [(18.0, 14.0, 9.0, 20.0, 3.6, 0.6, 20, 'sandstone'), (25.0, 19.5, 4.5, 6.0, 4.2, 0.72, 70, 'sandstone'),
             (37.5, 18.0, 4.5, 5.5, 4.0, 0.7, 110, 'sandstone'), (33.2, 26.0, 1.6, 1.6, 3.2, 0.85, 0, 'sandstone'),
             (47.0, 10.0, 10.0, 22.0, 3.2, 0.55, -10, 'canyon'), (10.0, 28.0, 5.0, 7.0, 3.4, 0.65, 40, 'canyon'),
             (30.0, -4.0, 12.0, 40.0, 3.0, 0.5, 0, 'sandstone'), (43.0, 30.0, 1.4, 1.4, 2.6, 0.85, 0, 'sandstone'),
             (44.6, 31.2, 1.2, 1.2, 2.2, 0.85, 0, 'sandstone'), (52.0, 24.0, 6.0, 9.0, 2.8, 0.6, 60, 'canyon')]


def mesa_desert():
    rng = random.Random(41)
    g = Grid(W, H, fill='a')
    for y in range(H):
        for x in range(W):
            g.put(x, y, rng.choice('abc'))
    g.rect(ROAD, 0, ROAD, H - 1, 'r')
    monuments = [{'type': 'mountain', 'x': x, 'y': y, 'size': s, 'length': L, 'height': h, 'cliff': c, 'angle': a,
                  'rock': rock, 'snowline': 0, 'ridges': rng.choice((2, 3, 4)), 'seed': rng.randrange(1000),
                  'casts': True} for x, y, s, L, h, c, a, rock in MONUMENTS]
    ranch = {'type': 'village', 'x': ROAD + 2.4, 'y': 41.0, 'size': 0.7, 'count': 4, 'church': False, 'seed': 9}
    return scene(
        g,
        title='The mesa desert - buttes and mesas on a red plain, at landscape scale',
        legend={
            'a': {'floor': 'desert_floor'}, 'b': {'floor': 'desert_floor_b'}, 'c': {'floor': 'desert_floor_c'},
            'r': {'floor': 'desert_road'},
        },
        sky='day',
        skyline='mountains',
        ambient=[0.46, 0.42, 0.42],
        lights=[{'type': 'sun', 'azimuth': 180, 'elevation': 30, 'intensity': 1.3}],
        fog={'color': [0.8, 0.7, 0.62], 'density': 0.006},
        objects=monuments + [ranch],
        time='golden',
        camera={'x': ROAD + 0.5, 'y': 50.0, 'look_at': [ROAD + 0.5, 20.0, 1.8], 'fov': 60, 'height': 0.04},
        shots=[
            {'x': ROAD + 0.5, 'y': 50.0, 'look_at': [ROAD + 0.5, 20.0, 1.8], 'fov': 60, 'height': 0.04},
            {'x': 44.0, 'y': 44.0, 'look_at': [28.0, 18.0, 1.0], 'fov': 62, 'height': 3.5},
            {'x': 40.0, 'y': 23.0, 'look_at': [18.0, 18.0, 1.6], 'fov': 66, 'height': 0.2, 'time': 'sunset'},
            {'x': ROAD + 0.5, 'y': 50.0, 'look_at': [ROAD + 0.5, 20.0, 1.8], 'fov': 60, 'height': 0.04,
             'time': 'night'},
        ],
        max_distance=80,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(mesa_desert().save(os.path.join(HERE, 'mesa_desert.json')))

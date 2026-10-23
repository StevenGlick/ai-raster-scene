"""The sky road: a road scene (road.py) with no ground under it - a road of marble laid across a sea of cloud, arches
over it, islands adrift beside it, a sky whale going the same way, and a dreamer walking it.

The road's `ground` is `void` on both sides, so the sky carries on below it: the `dream` sky's sea of cloud far
beneath. Gilded kerbs (the `rumble` strip in gold) edge the marble; columns stand along its edges every 8 (an
`offset` back onto the road) and stone arches stand over it every 18 (a row down the `middle`). Floating islands
(`floating_rock`) drift off both sides at heights between two (`z` as a range), a `sky_whale` swims alongside, and
balloons hang in the distance. The sun is low ahead; the dreamer walks toward it.
Run:  python sky_road.py  -> writes sky_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.0, 'radius': 2.4, 'spread': 0.6}]


def sky_road():
    road = {
        'sections': [[12, 0, 0], [40, 0.4, 1.4], [40, -0.5, -0.8], [50, 0.3, 2.0], [120, -0.15, 0.0]],
        'width': 2.6, 'surface': 'marble', 'lines': False,
        'rumble': {'width': 0.22, 'colors': ['#f0d070', '#c89a38']},
        'ground': 'void', 'bands': 0.05, 'distance': 220,
    }
    roadside = [
        {'type': 'column', 'every': 8, 'offset': -0.12, 'scale': 2.2, 'from': 5, 'flip': True},
        {'type': 'stone_arch', 'side': 'middle', 'every': 18, 'offset': 0.0, 'scale': 3.4, 'from': 14},
        {'type': 'floating_rock', 'density': 0.06, 'offset': [5.0, 30.0], 'z': [-3.0, 5.0], 'scale': [2.0, 6.0],
         'seed': 3},
        {'type': 'balloon', 'density': 0.02, 'offset': [8.0, 40.0], 'z': [2.0, 9.0], 'scale': [1.4, 2.6], 'seed': 4},
    ]
    decals = [{'tex': 'crack', 'density': 0.03, 'size': [0.4, 0.8], 'opacity': 0.5, 'seed': 1}]   # old marble
    sprites = [
        {'type': 'dreamer', 'at': 7.0, 'x': 0.1, 'view': 'back', 'id': 'dreamer'},
        {'type': 'sky_whale', 'at': 42.0, 'x': -16.0, 'z': 6.0, 'scale': 7.0},
    ]
    return road_scene(
        road,
        title='The sky road - a road of marble across a sea of cloud',
        sky='dream',
        lights=[{'type': 'sun', 'azimuth': 268, 'elevation': 7, 'intensity': 0.7, 'color': [1.0, 0.86, 0.7],
                 'disc_size': 4}],
        ambient=[0.62, 0.58, 0.68],
        fog={'color': [0.9, 0.8, 0.86], 'density': 0.008, 'sky_mix': 0.1},
        roadside=roadside,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 64, 'pitch': 0.02},
        shots=[
            {'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 64, 'pitch': 0.02, 'post': LOOK},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(sky_road().save(os.path.join(HERE, 'sky_road.json')))

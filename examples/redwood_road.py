"""The redwood road: a road scene (road.py) through a forest of giant redwoods on a misty morning - the road winding
between trunks wider than the car, their tops lost overhead, shafts of sunlight slanting down through the haze,
ferns thick on the forest floor.

A two-lane road (`asphalt`, a yellow centre line) through `pine_needles` verges and `moss` beyond; `redwood_trunk`s
in rows either side (a few right at the road's edge, more back in the wood), ferns and undergrowth between them;
the canopy closes over it all (a high `ceiling` of `canopy`, lit); `light_shaft`s (additive) slant down through a
green-gold `fog`. Your convertible from behind.
Run:  python redwood_road.py  -> writes redwood_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.4}]


def redwood_road():
    road = {
        'sections': [[34, 0, 0.1], [40, -0.25, 0.2], [40, 0.3, -0.2], [300, -0.1, 0]],
        'width': 2.2, 'lanes': 2, 'surface': 'asphalt', 'lines': '#d8c040', 'rumble': False, 'bands': 0.02,
        'ground': [{'width': 0.5, 'texture': 'pine_needles'}, {'texture': 'moss'}],
        'ceiling': {'height': 16, 'texture': 'canopy', 'tile': 6.0, 'light': 0.7},
        'distance': 160,
    }
    roadside = [
        {'type': 'redwood_trunk', 'every': 10, 'offset': [1.0, 1.8], 'scale': [20, 26], 'from': 10, 'jitter': 3,
         'seed': 1},
        {'type': 'redwood_trunk', 'density': 0.1, 'offset': [3.0, 16.0], 'scale': [20, 30], 'from': 8, 'seed': 2},
        {'type': ['fern', 'fern', 'tree_fern', 'bush'], 'density': 1.0, 'offset': [0.4, 6.0], 'scale': [0.4, 0.9],
         'seed': 3},
    ]
    scatter = [{'of': 'undergrowth', 'density': 1.4, 'offset': [0.0, 5.0], 'seed': 4}]
    sprites = [
        {'type': 'light_shaft', 'at': 9, 'x': -1.6, 'scale': 12, 'opacity': 0.5},
        {'type': 'light_shaft', 'at': 15, 'x': 1.2, 'scale': 14, 'opacity': 0.45},
        {'type': 'light_shaft', 'at': 24, 'x': -0.4, 'scale': 14, 'opacity': 0.4},
        {'type': 'deer', 'at': 13, 'x': 1.5},
    ]
    return road_scene(
        road,
        title='The redwood road - winding through giant redwoods on a misty morning, sunlight slanting down',
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 300, 'elevation': 50, 'intensity': 0.6, 'color': [1.0, 0.92, 0.75]}],
        ambient=[0.5, 0.52, 0.46],
        fog={'color': [0.66, 0.7, 0.56], 'density': 0.035},
        roadside=roadside,
        scatter=scatter,
        sprites=sprites,
        camera={'at': 2.0, 'x': -0.4, 'height': 0.75, 'fov': 64, 'pitch': 0.12},
        shots=[{'at': 2.0, 'x': -0.4, 'height': 0.75, 'fov': 64, 'pitch': 0.12, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(redwood_road().save(os.path.join(HERE, 'redwood_road.json')))

"""The torii path: a road scene (road.py) on a mountain shrine's path - walking up a stone path through a tunnel of
red shrine gates set one behind another, the forest dark either side, late sun striking through the gaps, lanterns
lit at the gates' feet.

The path is `flagstone` with `moss` at its edges, the forest floor `moss` beyond; the gates are `torii` set close
in a row over the path (`side` middle, `every` 0.9), so they make a tunnel of red; small lanterns at their feet glow
(`red_lantern`, a few with a warm `light`); tall pines and cedars crowd the slope either side; a `golden` sky low in
the west, its light slanting in. On foot.
Run:  python torii_path.py  -> writes torii_path.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.2}]
WARM = [1.0, 0.7, 0.4]


def torii_path():
    road = {
        'sections': [[12, 0, 0.3], [30, 0.15, 0.5], [30, -0.2, 0.4], [200, 0.05, 0.2]],
        'width': 1.4, 'surface': 'flagstone', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': [{'width': 0.3, 'texture': 'moss_stone'}, {'texture': 'moss'}],
        'distance': 120,
    }
    roadside = [
        {'type': 'torii', 'side': 'middle', 'every': 0.9, 'offset': 0.0, 'from': 2.5, 'scale': 2.2},
        {'type': 'red_lantern', 'every': 3.6, 'offset': 0.12, 'from': 3, 'z': 0.0, 'scale': 0.3, 'seed': 1,
         'light': {'color': WARM, 'radius': 1.4, 'intensity': 0.6, 'z': 0.2}},
        {'type': ['pine', 'pine', 'tree'], 'density': 0.4, 'offset': [0.8, 8.0], 'scale': [2.6, 4.2], 'seed': 2},
        {'type': ['fern', 'bush'], 'density': 0.8, 'offset': [0.3, 3.0], 'scale': [0.3, 0.6], 'seed': 3},
    ]
    return road_scene(
        road,
        title='The torii path - walking up a mountain shrine path through a tunnel of red gates, lanterns lit',
        sky='golden',
        lights=[{'type': 'sun', 'azimuth': 250, 'elevation': 10, 'intensity': 0.9, 'color': [1.0, 0.8, 0.56]}],
        ambient=[0.46, 0.44, 0.42],
        fog={'color': [0.7, 0.6, 0.5], 'density': 0.02},
        roadside=roadside,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.12},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.12, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(torii_path().save(os.path.join(HERE, 'torii_path.json')))

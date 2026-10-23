"""The aurora lake: a road scene (road.py) on a frozen lake at night - riding a snowmobile across the ice under the
aurora, the lights doubled in the polished ice, two more snowmobiles' tail lights ahead, snowy pines and lit cabins
along the shore.

The lake is the road and the ground (`ice`, polished enough to mirror the sky - `wet` 0.6 on the way, `reflect` on
the ground's band - then `snow` at the shore); `snowy_pine`s crowding the shore, `log_cabin`s with their windows lit
and a warm `light`; two `snowmobile`s ahead, their tail lights glowing; the `aurora` sky. Your own snowmobile's cowl,
windscreen and bars before you (`snowmobile_bars`).
Run:  python aurora_lake.py  -> writes aurora_lake.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.9, 'radius': 2.4}]
WARM = [1.0, 0.72, 0.4]
ICE = {'base': 'ice', 'tint': [0.7, 0.8, 0.95]}


def aurora_lake():
    road = {
        'sections': [[20, 0, 0], [60, 0.1, 0], [300, -0.04, 0]],
        'width': 6.0, 'surface': ICE, 'lines': False, 'rumble': False, 'bands': 0.0, 'wet': 0.6,
        'ground': [{'width': 10.0, 'texture': ICE, 'reflect': 0.6}, {'texture': 'snow'}],
        'distance': 300,
    }
    roadside = [
        {'type': 'snowy_pine', 'density': 0.3, 'offset': [11.0, 30.0], 'scale': [2.0, 3.4], 'seed': 1},
        {'type': 'log_cabin', 'every': 40, 'offset': [11.0, 14.0], 'from': 20, 'scale': [1.6, 2.0], 'seed': 2,
         'light': {'color': WARM, 'radius': 4.0, 'intensity': 0.9, 'z': 0.8}},
    ]
    sprites = [
        {'type': 'snowmobile', 'at': 7, 'x': -0.8},
        {'type': 'snowmobile', 'at': 12, 'x': 1.2},
    ]
    return road_scene(
        road,
        title='The aurora lake - a snowmobile across a frozen lake under the aurora, the lights doubled in the ice',
        sky='aurora',
        ambient=[0.26, 0.32, 0.4],
        fog={'color': [0.12, 0.2, 0.26], 'density': 0.006},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'snowmobile_bars', 'ahead': 0.7, 'z': 0.33, 'scale': 0.24,
                            'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(aurora_lake().save(os.path.join(HERE, 'aurora_lake.json')))

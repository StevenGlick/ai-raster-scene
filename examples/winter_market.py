"""The winter market: a road scene (road.py) in the medieval town on a winter night - walking up the high street
in the snow, the half-timbered houses' windows lit, market stalls glowing along both sides, people out among them,
the town's great fir dressed with lights in the square ahead, the castle lit on its hill.

The market ride's street at night: `cobble` under `snow` drifts, the houses `timber_house_night` (their windows
lit) in `blocks`; the stalls (`market_stall`, `fruit_stall`) with warm `light`s, `lamp_post`s; the townspeople
(`villager`, `child`, `farmer`, `monk`); the `christmas_tree` in the square (its lights glow); the `castle_hill` far
off, tinted to the night; snow falling, a `night` sky.
Run:  python winter_market.py  -> writes winter_market.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.4, 'spread': 0.5}, 'snow']
WALK = 0.7
WARM = [1.0, 0.72, 0.4]
SNOWY = {'base': 'snow', 'tint': [0.82, 0.86, 1.0]}


def winter_market():
    road = {
        'sections': [[16, 0, 0], [30, 0.12, 0.25], [30, -0.1, 0.1], [200, 0.0, 0.0]],
        'width': 2.4, 'surface': {'base': 'cobble', 'tint': [0.9, 0.92, 1.0]}, 'lines': False, 'rumble': False,
        'bands': 0.0,
        'ground': [{'width': WALK, 'texture': SNOWY}, {'texture': SNOWY}],
        'walls': [{'side': 'both', 'offset': WALK, 'height': 2.6, 'tile': [2.0, 2.6], 'blocks': 2.0, 'seed': 3,
                   'texture': ['timber_house_night', 'timber_house_night_b', 'timber_house_night_c']}],
        'distance': 120,
    }
    roadside = [
        {'type': ['market_stall', 'fruit_stall'], 'every': 5.5, 'offset': [0.05, 0.25], 'from': 8, 'to': 40,
         'flip': True, 'seed': 1, 'light': {'color': WARM, 'radius': 2.4, 'intensity': 1.0, 'z': 1.0}},
        {'type': 'lamp_post', 'every': 7, 'offset': 0.1, 'from': 4, 'seed': 2,
         'light': {'color': WARM, 'radius': 3.0, 'intensity': 0.9, 'z': 1.5}},
    ]
    decals = [{'tex': 'sand_drift', 'density': 0.3, 'size': [0.8, 1.6], 'side': 'road', 'tint': [1.4, 1.5, 1.7],
               'seed': 1}]
    sprites = [
        {'type': 'villager', 'at': 5.5, 'x': -1.1},
        {'type': 'child', 'at': 6.3, 'x': -0.6},
        {'type': 'farmer', 'at': 9, 'x': 1.0, 'flip': True},
        {'type': 'monk', 'at': 12, 'x': 0.3, 'view': 'back'},
        {'type': 'villager', 'at': 15, 'x': -0.8, 'flip': True},
        {'type': 'christmas_tree', 'at': 28, 'x': 0.0, 'scale': 3.2,
         'light': {'color': WARM, 'radius': 4.0, 'intensity': 1.0, 'z': 1.5}},
        {'type': 'castle_hill', 'at': 70, 'x': 0.0, 'scale': 21, 'tint': [0.55, 0.6, 0.8]},
    ]
    return road_scene(
        road,
        title='The winter market - the medieval town\'s high street on a snowy night, stalls lit, the great fir aglow',
        sky='night',
        ambient=[0.26, 0.28, 0.4],
        fog={'color': [0.2, 0.22, 0.34], 'density': 0.02},
        roadside=roadside,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 64, 'pitch': 0.12},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 64, 'pitch': 0.12, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(winter_market().save(os.path.join(HERE, 'winter_market.json')))

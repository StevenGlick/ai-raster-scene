"""The underworld river: a road scene (road.py) on the water - a ferry ride down a dark river through a cavern,
robed statues holding fire along its banks, pale wisps over the water, a great gate ahead.

The river is the road (black-green `water`, a slow `ripple`); either bank a strip of bone-strewn rock, then the
cavern's walls (`walls` of dark `stone` with a `ragged` top) under a `ceiling` of rock far overhead (a roof: no
sky). Robed statues stand along the banks, a brazier at each one's feet with its fire; wisps hang over the water
(`orb`s, tinted green, `additive`) and the water mirrors them all. A stone gate spans the river ahead, braziers on
either side; you ride in the ferry, its bow and lantern before you.
Run:  python underworld_river.py  -> writes underworld_river.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.5, 'radius': 2.4, 'spread': 0.5}]
FIRE = [1.0, 0.55, 0.25]
WISP = {'type': 'orb', 'blend': 'additive', 'fullbright': True, 'tint': [0.5, 1.0, 0.7]}
RIVER = {'base': 'water', 'tint': [0.4, 0.55, 0.5]}


def underworld_river():
    road = {
        'sections': [[12, 0, 0], [40, -0.3, 0], [40, 0.35, 0], [200, -0.1, 0]],
        'width': 3.0, 'surface': RIVER, 'lines': False, 'rumble': False, 'bands': 0.0, 'ripple': 0.4,
        'ground': [{'width': 1.2, 'texture': {'base': 'rock_floor', 'tint': [0.5, 0.48, 0.5]}},
                   {'texture': 'rock_floor'}],
        'walls': [{'side': 'both', 'offset': 1.2, 'height': 5.0, 'texture': 'stone_dark', 'tile': 1.6, 'ragged': 1.2,
                   'seed': 1}],
        'ceiling': {'height': 7.0, 'texture': 'rock', 'tile': 2.5, 'light': 0.35},
        'distance': 140,
    }
    roadside = [
        {'type': 'robed_statue', 'every': 8, 'offset': 0.5, 'from': 4, 'scale': 1.8, 'tint': [0.6, 0.6, 0.65]},
        {'type': 'brazier', 'every': 8, 'offset': 0.15, 'from': 4.6, 'scale': 0.5,
         'light': {'color': FIRE, 'radius': 3.2, 'intensity': 1.3, 'z': 0.6, 'x': 0.3}},
        dict(WISP, side='middle', density=0.25, offset=[-1.3, 1.3], z=[0.5, 1.8], scale=[0.08, 0.14], seed=5),
    ]
    scatter = [{'of': ['bones', 'bones', 'rocks'], 'density': 0.5, 'offset': [0.0, 1.2], 'sizes': ['small', 'medium'],
                'seed': 1}]
    sprites = [
        {'type': 'stone_arch', 'at': 26, 'x': 0.0, 'scale': 5.2, 'tint': [0.6, 0.58, 0.62]},
        {'type': 'brazier', 'at': 25.5, 'x': -2.3, 'scale': 0.8,
         'light': {'color': FIRE, 'radius': 4.0, 'intensity': 1.5, 'z': 0.8}},
        {'type': 'brazier', 'at': 25.5, 'x': 2.3, 'scale': 0.8,
         'light': {'color': FIRE, 'radius': 4.0, 'intensity': 1.5, 'z': 0.8}},
    ]
    return road_scene(
        road,
        title='The underworld river - a ferry down a dark river through a cavern, statues holding fire on its banks',
        sky='night',
        ambient=[0.34, 0.36, 0.42],
        fog={'color': [0.05, 0.08, 0.07], 'density': 0.03},
        roadside=roadside,
        scatter=scatter,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.08},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.08, 'post': LOOK,
                'vehicle': {'type': 'boat_bow', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5,
                            'light': {'color': [1.0, 0.8, 0.5], 'radius': 2.4, 'intensity': 1.0, 'z': 0.5,
                                      'at': 0.1}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(underworld_river().save(os.path.join(HERE, 'underworld_river.json')))

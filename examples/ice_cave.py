"""The ice cave: a road scene (road.py) under a glacier - paddling a boat down a meltwater river through a cave of
blue ice, the daylight glowing through its roof, icicles hanging from it, spires of ice along the banks.

The river is the road (`water` tinted glacier blue, a slow `ripple`); its banks `ice_floor`; the cave's walls are
`ice_block` and `frost_wall` (`walls` in `blocks` with a `ragged` top) under a low `ceiling` of `ice` that lets the
daylight through (its `light` 1.0, so the cave glows blue); `icicles` hang in curtains along the walls' tops,
`ice_spire`s and `ice_shards` stand on the banks; the water mirrors it all. Your own boat's bow and its lantern.
Run:  python ice_cave.py  -> writes ice_cave.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.8, 'radius': 2.2}]


def ice_cave():
    road = {
        'sections': [[10, 0, 0], [24, 0.35, -0.2], [24, -0.4, 0.1], [200, 0.15, 0]],
        'width': 2.0, 'surface': {'base': 'water', 'tint': [0.55, 0.8, 0.95]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'ripple': 0.3,
        'ground': [{'width': 0.8, 'texture': 'ice_floor'}, {'texture': 'ice'}],
        'walls': [{'side': 'both', 'offset': 0.8, 'height': 2.6, 'ragged': 0.6,
                   'texture': ['ice_block', 'frost_wall', 'ice_block'], 'tile': [1.6, 1.3], 'blocks': 2.5, 'seed': 2}],
        'ceiling': {'height': 2.6, 'texture': 'ice', 'tile': 2.0, 'light': 1.0},
        'distance': 120,
    }
    roadside = [
        {'type': 'icicles', 'side': 'both', 'every': 1.6, 'offset': 0.7, 'z': 1.85, 'scale': 0.75},
        {'type': ['ice_spire', 'ice_shards', 'ice_shards'], 'density': 0.5, 'offset': [0.1, 0.7],
         'scale': [0.3, 0.9], 'seed': 3},
    ]
    return road_scene(
        road,
        title='The ice cave - paddling down a meltwater river through a cave of blue ice, icicles hanging overhead',
        sky='day',
        ambient=[0.66, 0.8, 0.94],
        fog={'color': [0.62, 0.82, 0.96], 'density': 0.025},
        roadside=roadside,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 62, 'pitch': 0.06},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 62, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'boat_bow', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5,
                            'light': {'color': [1.0, 0.8, 0.5], 'radius': 2.0, 'intensity': 0.8, 'z': 0.5,
                                      'at': 0.1}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(ice_cave().save(os.path.join(HERE, 'ice_cave.json')))

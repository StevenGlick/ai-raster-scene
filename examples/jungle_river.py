"""The jungle river: a road scene (road.py) on the water - by canoe up a river through the jungle, its banks a wall
of green mirrored in the still water, mist over it.

The road is the river (`water` tinted green-brown, a gentle `ripple`); either bank a strip of mud and reeds, then
the jungle - a `wall` of `jungle_leaves` with a `ragged` top, and in front of it kapoks, palms, tree ferns and
banana plants standing over the water, ferns and heliconias at its edge (`roadside` rows) - all of it reflected.
Another canoe goes ahead, a heron stands in the shallows, an alligator lies at the bank, macaws cross overhead, a
stone head watches from the bank. Your own canoe's bow (`boat_bow`) in front of you.
Run:  python jungle_river.py  -> writes jungle_river.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.0}]
RIVER = {'base': 'water', 'tint': [0.75, 0.9, 0.62]}


def jungle_river():
    road = {
        'sections': [[12, 0, 0], [40, -0.4, 0], [40, 0.45, 0], [40, -0.3, 0], [300, 0.2, 0]],
        'width': 3.4, 'surface': RIVER, 'lines': False, 'rumble': False, 'bands': 0.0, 'ripple': 0.5,
        'ground': [{'width': 0.8, 'texture': RIVER, 'reflect': 0.45},
                   {'width': 0.6, 'texture': 'mud'}, {'texture': 'jungle_floor'}],
        'walls': [{'side': 'both', 'offset': 3.4, 'height': 6.0, 'texture': 'jungle_leaves', 'tile': 2.0,
                   'ragged': 2.5, 'seed': 1}],
        'distance': 220,
    }
    roadside = [
        {'type': 'kapok', 'density': 0.06, 'offset': [1.6, 3.2], 'scale': [6.0, 8.0], 'seed': 1},
        {'type': ['palm', 'tree_fern', 'banana_plant', 'palm'], 'density': 0.5, 'offset': [1.0, 3.2],
         'scale': [1.6, 3.2], 'seed': 2},
        {'type': ['fern', 'heliconia', 'monstera', 'reeds', 'reeds'], 'density': 1.4, 'offset': [0.6, 1.6],
         'scale': [0.5, 1.0], 'seed': 3},
    ]
    sprites = [
        {'type': 'canoe', 'at': 11, 'x': 0.4, 'z': -0.04, 'scale': 0.9},
        {'type': 'heron', 'at': 8, 'x': 2.15, 'scale': 0.8},
        {'type': 'alligator', 'at': 14, 'x': -2.4, 'scale': 1.2},
        {'type': 'stone_head', 'at': 19, 'x': -2.8, 'scale': 1.4},
        {'type': 'macaw', 'at': 9, 'x': -1.0, 'z': 3.4, 'scale': 0.8},
        {'type': 'macaw', 'at': 10.5, 'x': 0.4, 'z': 3.8, 'scale': 0.7, 'flip': True},
    ]
    return road_scene(
        road,
        title='The jungle river - by canoe up a river through the jungle, its banks mirrored in the water',
        sky='day',
        skyline='jungle',
        lights=[{'type': 'sun', 'azimuth': 250, 'elevation': 55, 'intensity': 0.7, 'disc': False}],
        ambient=[0.46, 0.52, 0.44],
        fog={'color': [0.66, 0.74, 0.62], 'density': 0.03},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': -0.2, 'height': 0.5, 'fov': 62, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': -0.2, 'height': 0.5, 'fov': 62, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'boat_bow', 'ahead': 1.2, 'z': -0.1, 'scale': 0.48}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(jungle_river().save(os.path.join(HERE, 'jungle_river.json')))

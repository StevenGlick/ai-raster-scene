"""The rope bridge: a road scene (road.py) - a bridge of planks and rope slung between floating islands, nothing
under it but sky, a stone gate on the island at its far end.

The road is the bridge's planks, sagging in the middle and rising to the far side (`sections` that fall and rise);
its rails are `walls` of `railing` on both sides; the ground is `void`, so the sky - the `dream` sky's sea of
cloud - carries on below. Floating islands drift off to both sides at every height, a stone gate stands where the
bridge lands, birds wheel below. Someone crossing ahead.
Run:  python rope_bridge.py  -> writes rope_bridge.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.8, 'radius': 2.2}]


def rope_bridge():
    road = {
        'sections': [[4, 0, 0], [22, 0, -1.4], [22, 0, 1.6], [200, 0.1, 0.4]],
        'width': 1.1, 'surface': 'planks', 'lines': False, 'rumble': False, 'bands': 0.05,
        'ground': 'void',
        'walls': [{'side': 'both', 'offset': 0.04, 'height': 0.55, 'texture': 'railing', 'tile': [1.1, 0.55]}],
        'distance': 200,
    }
    roadside = [
        {'type': 'floating_rock', 'density': 0.06, 'offset': [4.0, 30.0], 'z': [-8.0, 6.0], 'scale': [2.0, 7.0],
         'seed': 3},
    ]
    sprites = [
        {'type': 'floating_rock', 'at': 52, 'x': 0.0, 'z': -7.0, 'scale': 14},       # the island it lands on
        {'type': 'stone_arch', 'at': 49, 'x': 0.0, 'scale': 2.6},
        {'type': 'explorer', 'at': 8, 'x': 0.05, 'view': 'back'},
        {'type': 'crow', 'at': 14, 'x': -4.6, 'z': -1.0, 'scale': 0.8},
        {'type': 'crow', 'at': 19, 'x': 4.4, 'z': -1.4, 'scale': 0.7, 'flip': True},
    ]
    return road_scene(
        road,
        title='The rope bridge - a bridge of planks and rope between floating islands, the sky beneath it',
        sky='dream',
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 12, 'intensity': 0.7, 'color': [1.0, 0.88, 0.72]}],
        ambient=[0.62, 0.58, 0.66],
        fog={'color': [0.88, 0.82, 0.88], 'density': 0.01, 'sky_mix': 0.1},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 64, 'pitch': 0.0},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 64, 'pitch': 0.0, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(rope_bridge().save(os.path.join(HERE, 'rope_bridge.json')))

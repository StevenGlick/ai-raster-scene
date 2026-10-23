"""The ghost ship: a road scene (road.py) on a haunted sea - rowing out of a cove at midnight toward a ship that
should not be there, pale and half see-through under the moon, its stern windows burning green, mist on the black
water, the cove's rocks dark either side.

The sea is the road and the ground (`sea`, almost still, mirroring the moon); rocks close either side
(`cliff_face` walls, ragged, low, opening out ahead); the `galleon` tinted ghost green, half see-through
(`opacity`) and lit from within (`fullbright`), a green `light` of its own, another farther off in the mist;
floating lights on the water (`orb`); a big moon, a cold `fog`. Your rowboat's bow and its lantern.
Run:  python ghost_ship.py  -> writes ghost_ship.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.9, 'radius': 2.4}]
GHOST = [0.6, 1.0, 0.8]


def ghost_ship():
    road = {
        'sections': [[300, 0.02, 0]],
        'width': 4.0, 'surface': 'sea', 'lines': False, 'rumble': False, 'bands': 0.0, 'ripple': 0.2,
        'ground': 'sea',
        'walls': [{'side': 'both', 'offset': 1.0, 'height': 5, 'texture': 'cliff_face', 'tile': 3.5, 'ragged': 3,
                   'to': 14, 'seed': 3}],
        'distance': 260,
    }
    roadside = [{'type': 'orb', 'side': 'middle', 'density': 0.1, 'offset': [-6.0, 6.0], 'z': [0.1, 0.5],
                 'scale': [0.1, 0.18], 'from': 4, 'seed': 1}]
    sprites = [
        {'type': 'galleon', 'at': 21, 'x': 0.8, 'z': -0.3, 'scale': 6.5, 'tint': GHOST, 'opacity': 0.6,
         'fullbright': True, 'light': {'color': GHOST, 'radius': 7.0, 'intensity': 1.0, 'z': 1.5}},
        {'type': 'galleon', 'at': 60, 'x': -9, 'z': -0.3, 'scale': 4.5, 'tint': GHOST, 'opacity': 0.35,
         'flip': True},
    ]
    return road_scene(
        road,
        title='The ghost ship - rowing out of a cove at midnight toward a ship that should not be there',
        sky='night',
        sky_objects=[{'type': 'moon', 'azimuth': 278, 'elevation': 16, 'size': 3.0}],
        ambient=[0.16, 0.2, 0.28],
        fog={'color': [0.14, 0.22, 0.24], 'density': 0.03},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.08},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.08, 'post': LOOK,
                'vehicle': {'type': 'boat_bow', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5,
                            'light': {'color': [1.0, 0.76, 0.45], 'radius': 2.0, 'intensity': 0.8, 'z': 0.5,
                                      'at': 0.1}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(ghost_ship().save(os.path.join(HERE, 'ghost_ship.json')))

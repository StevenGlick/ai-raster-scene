"""The midnight ride: a road scene (road.py) on a haunted night - riding a horse down a muddy lane through a dead wood
under a full moon, gravestones leaning in the grass, ghost lights drifting between the trees, a pale figure waiting
by the lane, the dark castle at its end, your lantern the only warm light.

A `mud` lane between verges of fallen leaves and `dry_grass`; `dead_tree`s crowding both sides, gravestones and
crosses among them; `orb`s - violet will-o'-wisps - at every height, a few with a `light`; the `ghost`
standing by the lane; crows on the branches; the `dark_castle` at the lane's end; a big moon in a `night` sky and a
cold blue `fog`. Your horse's neck and ears before you (`horse_neck`), a lantern's warm `light` carried with it.
Run:  python midnight_ride.py  -> writes midnight_ride.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 1.0, 'radius': 2.4}]
WISP = [0.72, 0.6, 1.0]                          # the will-o'-wisps' own violet


def midnight_ride():
    road = {
        'sections': [[16, 0, 0], [40, -0.2, 0.2], [40, 0.25, -0.1], [200, -0.05, 0]],
        'width': 1.4, 'surface': 'mud', 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.25, 'blend': 0.8},
        'ground': [{'width': 0.6, 'texture': 'leaves_fallen'}, {'texture': 'dry_grass'}],
        'distance': 160,
    }
    roadside = [
        {'type': 'dead_tree', 'density': 0.35, 'offset': [0.5, 9.0], 'scale': [2.2, 3.6], 'from': 3, 'seed': 1},
        {'type': ['gravestone', 'grave_cross', 'gravestone'], 'density': 0.6, 'offset': [0.3, 3.0],
         'scale': [0.45, 0.65], 'from': 3, 'seed': 2},
        {'type': 'orb', 'density': 0.2, 'offset': [0.5, 8.0], 'z': [0.3, 1.6], 'scale': [0.12, 0.22],
         'seed': 3},
        {'type': 'orb', 'every': 7, 'offset': [0.8, 2.0], 'z': [0.5, 1.2], 'scale': 0.2, 'from': 5,
         'seed': 4, 'light': {'color': WISP, 'radius': 2.2, 'intensity': 0.7, 'z': 0.8}},
    ]
    sprites = [
        {'type': 'ghost', 'at': 8.5, 'x': 1.15, 'flip': True},
        {'type': 'crow', 'at': 8, 'x': -1.6, 'z': 1.6, 'scale': 0.22},
        {'type': 'crow', 'at': 14, 'x': 2.4, 'z': 2.2, 'scale': 0.22, 'flip': True},
        {'type': 'dark_castle', 'at': 120, 'x': 4, 'scale': 30},
    ]
    return road_scene(
        road,
        title='The midnight ride - riding a haunted lane through a dead wood under the full moon, ghost lights in '
              'the trees',
        sky='night',
        sky_objects=[{'type': 'moon', 'azimuth': 262, 'elevation': 14, 'size': 3.2}],
        ambient=[0.2, 0.24, 0.34],
        fog={'color': [0.16, 0.2, 0.3], 'density': 0.035},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'horse_neck', 'ahead': 0.7, 'z': 0.5, 'scale': 0.26,
                            'light': {'color': [1.0, 0.72, 0.4], 'radius': 2.4, 'intensity': 0.9, 'z': 0.6,
                                      'at': -0.3}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(midnight_ride().save(os.path.join(HERE, 'midnight_ride.json')))

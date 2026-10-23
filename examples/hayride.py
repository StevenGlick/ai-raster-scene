"""The hayride: a road scene (road.py) on a farm in autumn - riding on the back of a hay wagon down a farm lane at
dusk, the tractor towing you, pumpkins thick in the fields, scarecrows, jack-o'-lanterns lit along the lane, the
red barn ahead, the trees turned.

The lane is the road (`dirt`), grass verges, then the pumpkin field either side (`farmland` tinted, `pumpkin`s
scattered thick), a scarecrow or two, crows; jack-o'-lanterns along the verges with their glow; autumn trees and a
`barn`. The `tractor` tows you on ahead; you ride the `hay_wagon` (the shot's vehicle). A `sunset` sky, warm haze.
Run:  python hayride.py  -> writes hayride.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.2, 'spread': 0.5}]


def hayride():
    road = {
        'sections': [[12, 0, 0], [30, 0.15, 0.4], [30, -0.2, -0.3], [200, 0.05, 0.2]],
        'width': 1.4, 'surface': {'base': 'dirt', 'tint': [0.8, 0.66, 0.5]}, 'lines': False, 'rumble': False,
        'bands': 0.02, 'edge': {'ragged': 0.2, 'blend': 0.4},
        'ground': [{'width': 0.8, 'texture': 'grass'}, {'texture': {'base': 'farmland_d', 'tint': [0.7, 0.62, 0.45]}}],
        'distance': 250,
    }
    roadside = [
        {'type': 'pumpkin', 'density': 2.2, 'offset': [0.9, 10.0], 'scale': [0.2, 0.32], 'seed': 1},
        {'type': 'jack_o_lantern', 'side': 'both', 'every': 4, 'offset': 0.3, 'from': 4, 'scale': 0.22,
         'light': {'color': [1.0, 0.55, 0.2], 'radius': 1.2, 'intensity': 0.9, 'z': 0.2}},
        {'type': ['tree_autumn', 'birch_autumn'], 'density': 0.06, 'offset': [8.0, 30.0], 'scale': [2.4, 3.4],
         'seed': 2},
        {'type': 'scarecrow', 'side': 'both', 'every': 23, 'offset': 4.0, 'from': 9, 'scale': 1.0},
    ]
    sprites = [
        {'type': 'tractor', 'at': 5.0, 'x': 0.0},
        {'type': 'barn', 'at': 40, 'x': 6.0, 'scale': 3.0},
        {'type': 'crow', 'at': 12, 'x': -2.0, 'z': 2.0, 'scale': 0.4},
        {'type': 'crow', 'at': 15, 'x': -1.2, 'z': 2.6, 'scale': 0.35, 'flip': True},
    ]
    return road_scene(
        road,
        title='The hayride - on the back of a hay wagon down a farm lane at dusk, pumpkins in the fields',
        sky='sunset',
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 6, 'intensity': 0.8, 'color': [1.0, 0.7, 0.45]}],
        ambient=[0.52, 0.44, 0.44],
        fog={'color': [0.86, 0.62, 0.5], 'density': 0.006, 'sky_mix': 0.3},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.68, 'fov': 62, 'pitch': 0.12},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.68, 'fov': 62, 'pitch': 0.12, 'post': LOOK,
                'vehicle': {'type': 'hay_wagon', 'ahead': 0.8, 'z': 0.12, 'scale': 0.45}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(hayride().save(os.path.join(HERE, 'hayride.json')))

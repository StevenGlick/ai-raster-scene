"""The night canal: a road scene (road.py) on the water - down a canal between old houses at night by boat, their
windows lit here and there and all of it doubled in the water, a gondola ahead, bridges humped over the canal.

The canal is the road (dark `water`, a slow `ripple`); on the left a stone quay along it, on the right the houses
rise straight from the water. The houses are `walls` in `blocks` - each house its own height and face
(`canal_house`, `_b`, `_c`: plaster worn to the brick, green shutters, a few windows lit) - standing on a
`canal_footing` of stone gone green at the waterline. Striped `mooring_pole`s stand off the doors, rowboats tied
up, lamps on the quay and on the walls; two `canal_bridge`s span the canal; a `gondola` goes ahead with its lamp.
The moon is up over the roofs; the water mirrors the windows, the lamps and the moon.
Run:  python night_canal.py  -> writes night_canal.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.4, 'spread': 0.5}]
LAMP = [1.0, 0.72, 0.42]
QUAY = 1.1                                   # the quay's width, on the left
HOUSES = ['canal_house', 'canal_house_b', 'canal_house_c', 'canal_house']


def night_canal():
    road = {
        'sections': [[12, 0, 0], [30, 0.16, 0], [30, -0.2, 0], [200, 0.08, 0]],
        'width': 2.6, 'surface': {'base': 'water', 'tint': [0.42, 0.48, 0.6]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'ripple': 0.35,
        'ground': {'left': [{'width': QUAY, 'texture': 'flagstone'}, {'texture': 'cobble'}], 'right': 'water'},
        'walls': [
            {'side': 'right', 'offset': 0.0, 'height': 0.32, 'texture': 'canal_footing', 'tile': [1.2, 0.32]},
            {'side': 'right', 'offset': 0.0, 'z': 0.32, 'height': 3.2, 'ragged': 1.0, 'texture': HOUSES,
             'tile': [1.6, 1.6], 'blocks': 1.6, 'seed': 2},
            {'side': 'left', 'offset': QUAY, 'height': 3.4, 'ragged': 1.0, 'texture': HOUSES[::-1],
             'tile': [1.6, 1.6], 'blocks': 1.6, 'seed': 3},
        ],
        'distance': 140,
    }
    roadside = [
        {'type': 'lamp_post', 'side': 'left', 'every': 7, 'offset': 0.2, 'from': 3, 'scale': 0.8,
         'light': {'color': LAMP, 'radius': 2.8, 'intensity': 1.2, 'z': 1.2, 'x': 0.1}},
        {'type': 'wall_lamp', 'side': 'right', 'every': 9, 'offset': 0.05, 'from': 6, 'z': 1.3, 'flip': True,
         'light': {'color': LAMP, 'radius': 2.6, 'intensity': 1.1, 'z': 1.4, 'x': 0.25}},
        {'type': 'mooring_pole', 'side': 'right', 'every': 5.5, 'offset': -0.35, 'from': 4, 'seed': 1},
        {'type': 'mooring_pole', 'side': 'right', 'every': 5.5, 'offset': -0.55, 'from': 4.3, 'seed': 2},
    ]
    sprites = [
        {'type': 'gondola', 'at': 6.0, 'x': 0.3,
         'light': {'color': LAMP, 'radius': 1.8, 'intensity': 0.8, 'z': 0.7}},
        {'type': 'canal_bridge', 'at': 14, 'x': -0.55, 'scale': 1.05},
        {'type': 'canal_bridge', 'at': 38, 'x': -0.55, 'scale': 1.05},
        {'type': 'washing_line', 'at': 12, 'x': -0.4, 'z': 2.4, 'scale': 1.4},
        {'type': 'washing_line', 'at': 27, 'x': -0.5, 'z': 2.6, 'scale': 1.4, 'flip': True},
    ]
    return road_scene(
        road,
        title='The night canal - by boat down a canal between old houses at night, a gondola ahead, bridges over it',
        sky='night',
        sky_objects=[{'type': 'moon', 'azimuth': 266, 'elevation': 19, 'size': 2.8}],
        lights=[{'type': 'moon', 'azimuth': 266, 'elevation': 30, 'intensity': 0.35, 'disc': False}],
        ambient=[0.3, 0.32, 0.44],
        fog={'color': [0.1, 0.12, 0.2], 'density': 0.018},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 62, 'pitch': 0.06},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 62, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'boat_bow', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5,
                            'light': {'color': LAMP, 'radius': 2.4, 'intensity': 1.0, 'z': 0.5, 'at': 0.1}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(night_canal().save(os.path.join(HERE, 'night_canal.json')))

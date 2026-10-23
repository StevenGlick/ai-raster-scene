"""The drowned city: a road scene (road.py) on the water - by boat down a flooded avenue of an abandoned city at
sunset, the towers either side gone back to nature, ivy climbing out of the water, driftwood floating, birds
wheeling, the sun going down at the end of the avenue.

The avenue is the road, under still water (`water`, a slow `ripple`); the towers stand out of it either side as
`walls` in `blocks` - `ruined_tower`, `_b`, each its own height, some fallen (`gaps`), their tops broken
(`ragged`) - doubled in the water. Driftwood, barrels and logs float by; a lamp post stands drowned to its lamp;
crows wheel; your own boat's bow and its lantern. The `sunset` sky, a warm haze.
Run:  python drowned_city.py  -> writes drowned_city.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.2}]
TOWERS = ['ruined_tower', 'ruined_tower_b', 'ruined_tower']


def drowned_city():
    road = {
        'sections': [[20, 0, 0], [40, 0.08, 0], [300, -0.05, 0]],
        'width': 3.4, 'surface': {'base': 'water', 'tint': [0.6, 0.62, 0.6]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'ripple': 0.3,
        'ground': {'base': 'water', 'tint': [0.6, 0.62, 0.6]},
        'walls': [
            {'side': 'both', 'offset': 0.6, 'height': 12, 'ragged': 5, 'texture': TOWERS, 'tile': [3.0, 3.0],
             'blocks': 4.0, 'gaps': 0.25, 'seed': 3},
            {'side': 'both', 'offset': 9, 'height': 22, 'ragged': 9, 'texture': TOWERS[::-1], 'tile': [4.0, 4.0],
             'blocks': 6.0, 'gaps': 0.3, 'seed': 4},
        ],
        'distance': 300,
    }
    roadside = [
        {'type': ['driftwood', 'log', 'barrel', 'driftwood'], 'density': 0.25, 'offset': [-1.6, 0.4], 'z': -0.08,
         'scale': [0.3, 0.5], 'seed': 1},
        {'type': 'lamp_post', 'side': 'left', 'every': 11, 'offset': -0.3, 'from': 5, 'z': -0.7, 'scale': 0.9},
    ]
    sprites = [
        {'type': 'crow', 'at': 14, 'x': -1.0, 'z': 3.0, 'scale': 0.5},
        {'type': 'crow', 'at': 18, 'x': 1.5, 'z': 4.2, 'scale': 0.45, 'flip': True},
        {'type': 'crow', 'at': 22, 'x': 0.2, 'z': 5.0, 'scale': 0.4},
    ]
    return road_scene(
        road,
        title='The drowned city - by boat down a flooded avenue of an abandoned city at sunset, the towers overgrown',
        sky='sunset',
        sky_objects=[{'type': 'sun', 'azimuth': 270, 'elevation': 5, 'size': 3.0}],
        lights=[{'type': 'sun', 'azimuth': 270, 'elevation': 7, 'intensity': 0.8, 'color': [1.0, 0.72, 0.48],
                 'disc': False}],
        ambient=[0.52, 0.46, 0.46],
        fog={'color': [0.86, 0.6, 0.48], 'density': 0.008, 'sky_mix': 0.3},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.12},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.12, 'post': LOOK,
                'vehicle': {'type': 'boat_bow', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(drowned_city().save(os.path.join(HERE, 'drowned_city.json')))

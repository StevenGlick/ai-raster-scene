"""The lantern river: a road scene (road.py) on a festival night - drifting down a wide river among hundreds of
floating lanterns, sky lanterns rising from the banks into the stars, cherry trees along the water, a shrine gate
standing in the river ahead, the moon over the hills, every light doubled in the water.

The river is the road (`water` tinted night blue, a slow `ripple`), grass banks; `floating_lantern`s scattered on
the water (`side` middle across its width, `z` 0, a few with a `light`), `sky_lantern`s rising over it and the
banks at every height (`z` spread), `cherry_tree`s along both banks, the `torii` in the water ahead; dark hills as a
`mountains` skyline, the moon. Your own boat's bow and its lantern.
Run:  python lantern_river.py  -> writes lantern_river.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

WARM = [1.0, 0.72, 0.4]
LOOK = [{'fx': 'bloom', 'strength': 1.0, 'radius': 2.4}]


def lantern_river():
    road = {
        'sections': [[20, 0, 0], [60, 0.12, 0], [300, -0.06, 0]],
        'width': 6.0, 'surface': {'base': 'water', 'tint': [0.36, 0.42, 0.62]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'ripple': 0.3,
        'ground': [{'width': 0.5, 'texture': 'mud'}, {'texture': 'grass'}],
        'distance': 200,
    }
    roadside = [
        {'type': 'floating_lantern', 'side': 'middle', 'density': 3.0, 'offset': [-2.9, 2.9], 'from': 2.5,
         'scale': [0.2, 0.3], 'seed': 1},
        {'type': 'floating_lantern', 'side': 'middle', 'every': 3.0, 'offset': [-2.4, 2.4], 'from': 3,
         'scale': 0.22, 'seed': 2, 'light': {'color': WARM, 'radius': 1.6, 'intensity': 0.8, 'z': 0.2}},
        {'type': 'sky_lantern', 'side': 'middle', 'density': 1.2, 'offset': [-3.0, 3.0], 'z': [0.8, 10.0],
         'scale': [0.35, 0.6], 'seed': 3},
        {'type': 'sky_lantern', 'density': 0.8, 'offset': [0.0, 12.0], 'z': [0.5, 14.0], 'scale': [0.35, 0.6],
         'seed': 4},
        {'type': 'cherry_tree', 'density': 0.16, 'offset': [0.4, 5.0], 'scale': [2.6, 3.4], 'seed': 5},
    ]
    sprites = [
        {'type': 'torii', 'at': 26, 'x': 0.0, 'scale': 3.2,
         'light': {'color': WARM, 'radius': 4.0, 'intensity': 0.8, 'z': 0.6, 'at': -1.0}},
    ]
    return road_scene(
        road,
        title='The lantern river - drifting among floating lanterns on a festival night, sky lanterns rising into '
              'the stars',
        sky='night',
        skyline={'type': 'mountains', 'height': 1.0, 'color': [0.08, 0.09, 0.14]},
        sky_objects=[{'type': 'moon', 'azimuth': 285, 'elevation': 22, 'size': 1.6}],
        ambient=[0.2, 0.2, 0.3],
        fog={'color': [0.12, 0.12, 0.22], 'density': 0.02},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.08},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.08, 'post': LOOK,
                'vehicle': {'type': 'boat_bow', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5,
                            'light': {'color': WARM, 'radius': 2.0, 'intensity': 0.9, 'z': 0.5, 'at': 0.1}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(lantern_river().save(os.path.join(HERE, 'lantern_river.json')))

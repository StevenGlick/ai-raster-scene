"""The mountain pass: a road scene (road.py) - a road cut into the side of a mountain, climbing through its bends
with the valley far below.

On the left the mountain rises sheer from the road (a `cliff_face` wall with a `ragged` top), marker posts and
stones along its foot. On the right a steel `guard_rail` and then nothing - the ground there is `void`, and far
below lies the valley (`below`, in bands along it: woods, a river, pasture, pine forest - the landscape textures, seen
from the air at their own scale), its far side a wall of rock 240 units off with a
`ragged` ridge, hazy with the distance. A goat on the verge, a car ahead, a sign before the bend. The second shot stops at the
rail and looks out over the valley.
Run:  python mountain_pass.py  -> writes mountain_pass.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.0}]


def mountain_pass():
    road = {
        'sections': [[12, 0, 0], [40, 0.75, 2.4], [34, -0.85, 1.8], [40, 0.65, 2.6], [36, -0.7, 1.6],
                     [60, 0.4, 2.0], [900, -0.2, 0.0]],
        'width': 3.0, 'lanes': 2, 'surface': 'asphalt', 'edges': '#e4e4e4', 'rumble': False,
        'ground': {'left': [{'width': 0.7, 'texture': 'gravel'}, {'texture': 'rock_floor'}], 'right': 'void'},
        'below': {'depth': 70, 'tile': 33, 'haze': 0.5,                        # the valley floor, in bands
                  'texture': [{'width': 60, 'texture': 'forest_canopy'}, {'width': 8, 'texture': 'river_water'},
                              {'width': 50, 'texture': 'pasture'}, {'texture': 'pine_canopy'}]},
        'walls': [
            {'side': 'left', 'offset': 0.7, 'height': 9, 'texture': 'cliff_face', 'tile': 3.5, 'ragged': 3},
            {'side': 'right', 'offset': 0.2, 'height': 0.3, 'texture': 'guard_rail', 'tile': [1, 0.3]},
            {'side': 'right', 'offset': 240, 'z': -70, 'height': 150, 'texture': 'cliff_face', 'tile': 30,
             'ragged': 40, 'seed': 6},                                      # the valley's far side
        ],
        'bands': 0.04, 'distance': 900,
    }
    roadside = [{'type': 'reflector_post', 'side': 'left', 'every': 4, 'offset': 0.25, 'from': 3}]
    scatter = [{'of': 'alpine', 'side': 'left', 'density': 1.2, 'offset': [0.05, 0.65], 'sizes': ['tiny', 'small'],
                'seed': 1}]
    decals = [{'tex': 'wear', 'density': 0.03, 'size': [0.5, 0.9], 'seed': 1}]
    sprites = [
        {'type': 'goat', 'at': 13, 'x': -1.95},
        {'type': 'car_sedan', 'at': 22, 'x': 0.75, 'tint': [0.55, 0.75, 1.0]},
        {'type': 'curve_sign', 'at': 9, 'x': 1.95, 'flip': True},
        {'type': 'speed_sign', 'at': 5.5, 'x': 1.95},
    ]
    return road_scene(
        road,
        title='The mountain pass - a road cut into the side of a mountain, the valley far below',
        sky='day',
        skyline='mountains',
        lights=[{'type': 'sun', 'azimuth': 300, 'elevation': 38, 'intensity': 0.8}],
        ambient=[0.58, 0.6, 0.66],
        fog={'color': [0.74, 0.8, 0.9], 'density': 0.0012},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.08},
        shots=[
            {'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.08, 'post': LOOK,
             'vehicle': {'type': 'sports_car', 'ahead': 2.6}},
            {'at': 30.0, 'x': 1.0, 'height': 0.7, 'fov': 62, 'pitch': -0.05, 'yaw': 14, 'post': LOOK},  # the view
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(mountain_pass().save(os.path.join(HERE, 'mountain_pass.json')))

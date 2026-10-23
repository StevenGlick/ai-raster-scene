"""The storm coast: a road scene (road.py) - driving a cliff road along the coast at night in a storm, the
lighthouse on the headland ahead sweeping its beam out over the sea, rain driving across the headlights, lightning
over the water.

The road runs along the cliff's edge: on the left the rock rises (`cliff_face` walls with a `ragged` top), on the
right a guard rail and then nothing - the ground is `void` and far `below` the sea, its surf breaking white. The
`lighthouse_tower` stands on its headland ahead and to the right, its `lighthouse_beam` swinging out over the
water; reflector posts mark the bends; the `storm` sky, `rain`, a fork of `lightning` far out. Your car with its
headlights on, the wet road shining.
Run:  python storm_coast.py  -> writes storm_coast.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.4, 'spread': 0.5},
        {'fx': 'rain', 'density': 1.2, 'length': 8, 'opacity': 0.3, 'angle': 14, 'color': [0.75, 0.8, 0.9]},
        {'fx': 'lightning', 'amount': 0.12, 'x': 0.85, 'y_end': 0.36}]


def storm_coast():
    road = {
        'sections': [[12, 0, 0], [40, 0.45, 0.8], [40, -0.35, -0.6], [300, 0.15, 0.2]],
        'width': 2.2, 'lanes': 2, 'surface': 'asphalt', 'lines': '#d8d8d8', 'edges': '#d8d8d8', 'rumble': False,
        'wet': 0.32, 'ripple': 0.5, 'bands': 0.03,
        'ground': {'left': [{'width': 0.5, 'texture': 'gravel'}, {'texture': 'rock_floor'}], 'right': 'void'},
        'below': {'depth': 24, 'tile': 6, 'haze': 0.4, 'texture': 'sea'},
        'walls': [{'side': 'left', 'offset': 0.5, 'height': 7, 'texture': 'cliff_face', 'tile': 3.5, 'ragged': 2.5},
                  {'side': 'right', 'offset': 0.2, 'height': 0.3, 'texture': 'guard_rail', 'tile': [1, 0.3]}],
        'distance': 300,
    }
    roadside = [{'type': 'reflector_post', 'side': 'left', 'every': 4, 'offset': 0.25, 'from': 3}]
    sprites = [
        {'type': 'lighthouse_tower', 'at': 34, 'x': 12, 'z': -6, 'scale': 10,
         'light': {'color': [1.0, 0.95, 0.8], 'radius': 8.0, 'intensity': 0.8, 'z': 3}},
        {'type': 'lighthouse_beam', 'at': 34, 'x': -2.2, 'z': -0.5, 'scale': 7.0, 'flip': True},
    ]
    return road_scene(
        road,
        title='The storm coast - a cliff road at night in a storm, the lighthouse sweeping its beam over the sea',
        sky='storm',
        ambient=[0.2, 0.22, 0.28],
        fog={'color': [0.12, 0.14, 0.18], 'density': 0.01},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.55, 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[{'at': 2.0, 'x': 0.55, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(storm_coast().save(os.path.join(HERE, 'storm_coast.json')))

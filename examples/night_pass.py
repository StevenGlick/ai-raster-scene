"""The night pass: a road scene (road.py) racing a mountain road at night - hugging the cliff through the bends, a
rival's tail lights ahead, the whole city spread out in lights far below the drop beside you, the stars over it.

The mountain pass's road with the night on it: the cliff (`cliff_face`) on the left, a guard rail on the right and
the drop beyond it (`void`); far `below` lies the city at night (`city_night`, its avenues lit). Reflector posts and
curve signs pick up the headlights; a rival car ahead (`car_compact`, its tail lights glowing); your convertible
with its `headlights` on; the `night` sky.
Run:  python night_pass.py  -> writes night_pass.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.2}]


def night_pass():
    road = {
        'sections': [[12, 0, 0], [40, 0.6, 1.2], [34, -0.75, 1.0], [40, 0.55, 1.4], [900, -0.2, 0.0]],
        'width': 3.0, 'lanes': 2, 'surface': 'asphalt', 'edges': '#e4e4e4', 'rumble': False,
        'ground': {'left': [{'width': 0.7, 'texture': 'gravel'}, {'texture': 'rock_floor'}], 'right': 'void'},
        'below': {'depth': 60, 'tile': 18, 'haze': 0.35, 'texture': 'city_night'},
        'walls': [
            {'side': 'left', 'offset': 0.7, 'height': 9, 'texture': 'cliff_face', 'tile': 3.5, 'ragged': 3},
            {'side': 'right', 'offset': 0.2, 'height': 0.3, 'texture': 'guard_rail', 'tile': [1, 0.3]},
        ],
        'bands': 0.04, 'distance': 900,
    }
    roadside = [{'type': 'reflector_post', 'side': 'left', 'every': 4, 'offset': 0.25, 'from': 3}]
    sprites = [
        {'type': 'car_compact', 'variant': 0, 'at': 9.5, 'x': 0.65},
        {'type': 'curve_sign', 'at': 9, 'x': 1.95, 'flip': True},
    ]
    return road_scene(
        road,
        title='The night pass - racing a mountain road at night, a rival ahead, the city in lights far below',
        sky='night',
        ambient=[0.2, 0.22, 0.32],
        fog={'color': [0.1, 0.1, 0.18], 'density': 0.0015},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.06},
        shots=[{'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(night_pass().save(os.path.join(HERE, 'night_pass.json')))

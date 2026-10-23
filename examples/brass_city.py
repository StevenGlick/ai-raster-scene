"""The brass city: a road scene (road.py) in the clockwork city at sundown - walking its high street behind a tram,
buildings of brass and copper either side with gears turning in their walls and steam venting from their pipes,
gaslamps lit, a great clock on a front, airships overhead, all in a brown smog.

A `cobble` street with `flagstone` pavements; the buildings are `brass_plate` and `copper_pipes` walls in `blocks`
of their own heights, a storey of `clock_face` on some; `brass_gear`s turning on the walls (`z` up the fronts),
`steam` from the pipes, `lamp_post`s with warm `light`s; the `great_clock` on a front;
`airship`s overhead; the `tram` tinted brass ahead; a `sunset` sky behind a brown smog. On foot.
Run:  python brass_city.py  -> writes brass_city.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.8, 'radius': 2.2}]
WALK = 0.8
GAS = [1.0, 0.72, 0.4]


def brass_city():
    road = {
        'sections': [[20, 0, 0], [40, 0.12, 0.2], [200, -0.04, 0]],
        'width': 2.6, 'surface': 'cobble', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': [{'width': WALK, 'texture': 'flagstone'}, {'texture': 'cobble'}],
        'walls': [
            {'side': 'both', 'offset': WALK, 'height': 3.4, 'ragged': 1.6, 'blocks': 2.6, 'seed': 4,
             'texture': ['brass_plate', 'copper_pipes', 'brass_plate', 'clock_face'], 'tile': [1.6, 1.6]},
            {'side': 'both', 'offset': WALK + 6, 'height': 9, 'ragged': 4, 'blocks': 4, 'seed': 5,
             'texture': ['copper_pipes', 'brass_plate'], 'tile': [2.4, 2.4]},
        ],
        'distance': 140,
    }
    roadside = [
        {'type': 'brass_gear', 'every': 5, 'offset': WALK - 0.05, 'z': [0.8, 2.2], 'scale': [0.9, 1.6],
         'from': 4, 'seed': 1},
        {'type': 'steam', 'every': 7, 'offset': WALK - 0.2, 'z': [2.6, 3.4], 'scale': [1.0, 1.6], 'opacity': 0.4,
         'from': 6, 'seed': 2},
        {'type': 'lamp_post', 'every': 6, 'offset': 0.15, 'from': 3, 'seed': 3,
         'light': {'color': GAS, 'radius': 3.0, 'intensity': 0.9, 'z': 1.5}},
    ]
    sprites = [
        {'type': 'tram', 'at': 7, 'x': 0.5, 'tint': [1.0, 0.82, 0.5]},
        {'type': 'great_clock', 'at': 15, 'x': 1.95, 'z': 2.0, 'scale': 1.3, 'flip': True},     # on a front
        {'type': 'airship', 'variant': 0, 'at': 28, 'x': -3.0, 'z': 8.0, 'scale': 3.0},
        {'type': 'airship', 'variant': 1, 'at': 50, 'x': 6.0, 'z': 12.0, 'scale': 3.6, 'flip': True},
    ]
    return road_scene(
        road,
        title="The brass city - the clockwork city's high street at sundown, gears turning in the walls, airships "
              "overhead",
        sky='sunset',
        ambient=[0.36, 0.3, 0.26],
        fog={'color': [0.46, 0.34, 0.24], 'density': 0.02},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': -0.6, 'height': 0.55, 'fov': 64, 'pitch': 0.14},
        shots=[{'at': 1.0, 'x': -0.6, 'height': 0.55, 'fov': 64, 'pitch': 0.14, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(brass_city().save(os.path.join(HERE, 'brass_city.json')))

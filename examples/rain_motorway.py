"""The rain motorway: a road scene (road.py) - a dual carriageway at dusk in the rain, oncoming headlights across
the barrier, tail lights ahead, the wet road mirroring all of it.

The road is both carriageways in one: two lanes each way (`lanes` 4), split by a `jersey_barrier` down the middle
(a `wall` at offset back over the road), the far two lanes carrying the oncoming traffic - `car_oncoming`s with
their headlights lit and a light of their own on the road - and ours the tail lights. The road is `wet`, the
`rain` falls with `splashes`, sodium `highway_lamp`s on the barrier, a `sign_gantry` over our side, the city's
skyline in the dusk.
Run:  python rain_motorway.py  -> writes rain_motorway.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.4, 'spread': 0.5},
        {'fx': 'rain', 'density': 1.2, 'length': 9, 'opacity': 0.3, 'angle': 8}, {'fx': 'splashes'}]
SODIUM = [1.0, 0.62, 0.3]
HEAD = [1.0, 0.95, 0.85]
W = 6.0
LANE = W / 4


def lane(k):
    return -W / 2 + (k + 0.5) * LANE


def rain_motorway():
    road = {
        'sections': [[16, 0, 0], [60, 0.22, 0.6], [60, -0.18, -0.4], [300, 0.1, 0]],
        'width': W, 'lanes': 4, 'surface': 'asphalt', 'edges': '#d8d8d4', 'rumble': False, 'wet': 0.3,
        'ripple': 0.4,
        'ground': [{'width': 0.6, 'texture': 'concrete', 'reflect': 0.15}, {'texture': 'grass'}],
        'walls': [{'side': 'left', 'offset': -W / 2 - 0.12, 'height': 0.27, 'texture': 'jersey_barrier',
                   'tile': [1.3, 0.27]}],                                   # the barrier down the middle
        'bands': 0.03, 'distance': 260,
    }
    roadside = [
        {'type': 'highway_lamp', 'side': 'middle', 'every': 12, 'offset': -0.2, 'from': 4,
         'light': {'color': SODIUM, 'radius': 6.0, 'intensity': 1.2, 'z': 3.4, 'x': 1.2}},
        {'type': 'tree', 'side': 'right', 'density': 0.2, 'offset': [1.5, 8.0], 'scale': [2.4, 3.2], 'seed': 1,
         'tint': [0.55, 0.58, 0.66]},
    ]
    oncoming = [{'type': 'car_oncoming', 'at': a, 'x': lane(k), 'variant': v,
                 'light': {'color': HEAD, 'radius': 4.0, 'intensity': 0.9, 'z': 0.4, 'at': -2.0}}
                for a, k, v in ((9, 0, 2), (14, 1, 1), (24, 0, 0), (38, 1, 3))]
    ours = [{'type': 'car_sedan', 'at': 13, 'x': lane(3), 'variant': 1},
            {'type': 'car_compact', 'at': 22, 'x': lane(2), 'variant': 0},
            {'type': 'box_truck', 'at': 34, 'x': lane(3)}]
    sprites = oncoming + ours + [{'type': 'sign_gantry', 'at': 28, 'x': W / 4, 'scale': 2.6}]
    return road_scene(
        road,
        title='The rain motorway - a dual carriageway at dusk in the rain, oncoming headlights across the barrier',
        sky='dusk',
        skyline='city',
        ambient=[0.3, 0.3, 0.38],
        fog={'color': [0.3, 0.3, 0.38], 'density': 0.012},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': lane(2), 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[{'at': 2.0, 'x': lane(2), 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(rain_motorway().save(os.path.join(HERE, 'rain_motorway.json')))

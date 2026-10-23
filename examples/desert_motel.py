"""The desert motel: a road scene (road.py) - the desert highway at night, a motel's neon sign and a gas station lit
by the road, nothing else for miles.

The highway runs on into the dark under the stars. On the left a `motel_sign` - MOTEL in pink neon on an arrow,
VACANCY in green - and the motel's row of rooms behind it, a `wall` of lit windows; on the right a `gas_station`, its
canopy lit white over the pumps, a car at them. Their lights pool on the road (pink, white, warm), power poles and
their wires run along it, saguaros stand black against the sky. Your car's headlights.
Run:  python desert_motel.py  -> writes desert_motel.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.4, 'spread': 0.5}]
PINK, WHITE, WARM = [1.0, 0.4, 0.75], [0.9, 0.95, 1.0], [1.0, 0.78, 0.5]
DIRT = {'base': 'desert_wash', 'tint': [0.9, 0.86, 0.8]}


def desert_motel():
    road = {
        'sections': [[30, 0, 0], [60, 0, 1.2], [60, 0.05, -1.4], [600, 0, 0.6]],
        'width': 3.0, 'lanes': 2, 'surface': 'asphalt', 'lines': '#e8c040', 'edges': '#d8d8d4', 'rumble': False,
        'shoulder': {'width': 0.4, 'texture': 'gravel'},
        'ground': [{'width': 4, 'texture': DIRT}, {'texture': 'sand'}],
        'walls': [
            {'side': 'left', 'offset': 6.5, 'height': 1.1, 'texture': 'window_lit_plaster', 'tile': [1.4, 1.1],
             'from': 16, 'to': 34},                                     # the motel's rooms
            {'side': 'left', 'offset': 6.4, 'z': 1.1, 'height': 0.25, 'texture': 'concrete', 'tile': 1.0,
             'from': 16, 'to': 34},
            {'side': 'right', 'offset': 0.9, 'z': 3.0, 'height': 0.6, 'texture': 'power_lines', 'tile': [10, 0.6]},
        ],
        'bands': 0.03, 'distance': 500,
    }
    roadside = [
        {'type': 'power_pole', 'side': 'right', 'every': 10, 'from': 0, 'offset': 0.9, 'scale': 3.5},
        {'type': 'saguaro', 'density': 0.05, 'offset': [3.0, 16.0], 'scale': [1.6, 2.6], 'tint': [0.12, 0.12, 0.18],
         'seed': 1},
    ]
    sprites = [
        {'type': 'motel_sign', 'at': 12, 'x': -3.0, 'scale': 4.2},
        {'type': 'gas_station', 'at': 24, 'x': 5.6, 'scale': 2.6},
        {'type': 'car_sedan', 'at': 22.5, 'x': 4.0, 'variant': 3},
    ]
    lights = [
        {'at': 12, 'x': -2.6, 'z': 3.2, 'radius': 6.0, 'color': PINK, 'intensity': 1.4},
        {'at': 23, 'x': 4.4, 'z': 2.2, 'radius': 5.5, 'color': WHITE, 'intensity': 1.5},
        {'at': 25, 'x': -6.0, 'z': 1.0, 'radius': 4.0, 'color': WARM, 'intensity': 1.0},
    ]
    return road_scene(
        road,
        title='The desert motel - the highway at night, a motel\'s neon sign and a gas station by the road',
        sky='night',
        skyline='hills',
        sky_objects=[{'type': 'moon', 'azimuth': 300, 'elevation': 22, 'size': 2.4}],
        ambient=[0.16, 0.16, 0.24],
        fog={'color': [0.08, 0.08, 0.14], 'density': 0.006},
        lights=lights,
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.75, 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[{'at': 2.0, 'x': 0.75, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(desert_motel().save(os.path.join(HERE, 'desert_motel.json')))

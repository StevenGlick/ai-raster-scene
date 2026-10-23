"""The neon race: a road scene (road.py) - racing a hover car through a cyberpunk city at night, the street wet
with rain, every sign and window in it mirrored on the road.

The street is `walls` cut into buildings (`blocks`): shops at street level, each its own `shopfront` (a list: pink,
cyan, amber signs), towers over them each its own height with their windows lit at random (`tower_windows`), alleys
between some (`gaps`), and taller towers far behind for the skyline. The road is `wet`: it mirrors the sky, the
signs, the cars and the neon; cyan lane lines, magenta edges. Pink and cyan lights along the shopfronts pool on
it; holographic ads hang over it, a sky train crosses it on a bridge, drones, other racers ahead - hover cars and
a bike. Your car is the shot's `vehicle`, floating a little off the road; a racer's HUD over it. The second shot
leans into the bend.
Run:  python neon_race.py  -> writes neon_race.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

PINK, CYAN, AMBER = [1.0, 0.3, 0.75], [0.3, 0.95, 1.0], [1.0, 0.7, 0.25]
NEON = [{'fx': 'bloom', 'source': 'light', 'strength': 2.2, 'radius': 2.4, 'spread': 0.6}]
LANE = 4.4 / 3
HUD = [{'type': 'counter', 'value': '2/3', 'label': 'LAP', 'at': 'top-left', 'margin': 16, 'scale': 1,
        'color': [64, 240, 255]},
       {'type': 'counter', 'value': '01:42.7', 'label': 'TIME', 'at': 'top', 'margin': 16, 'color': [255, 72, 192]},
       {'type': 'counter', 'value': '412 km/h', 'at': 'bottom-right', 'scale': 1, 'color': [64, 240, 255]}]


def neon_race():
    road = {
        'sections': [[16, 0, 0], [50, 0.4, 0.4], [40, -0.5, -0.4], [60, 0.3, 0.6], [300, -0.2, 0.0]],
        'width': 4.4, 'lanes': 3, 'surface': 'asphalt', 'lines': '#40e8ff', 'edges': '#ff40c0', 'rumble': False,
        'wet': 0.26, 'ripple': 0.6,
        'ground': [{'width': 1.6, 'texture': 'concrete_floor'}, {'texture': 'asphalt'}],
        'walls': [
            {'side': 'both', 'offset': 1.6, 'height': 1.4, 'texture': ['shopfront', 'shopfront_b', 'shopfront_c'],
             'tile': [2.2, 1.4], 'blocks': 2.2, 'seed': 1},                         # the shops
            {'side': 'both', 'offset': 1.75, 'z': 1.4, 'height': 13, 'ragged': 7,
             'texture': ['tower_windows', 'tower_windows_b'], 'tile': [1.4, 1.4], 'blocks': 4.4, 'gaps': 0.12,
             'seed': 2},                                                            # the towers over them
            {'side': 'both', 'offset': 14, 'height': 46, 'ragged': 18, 'texture': ['tower_windows_b', 'tower_windows'],
             'tile': [3.2, 3.2], 'blocks': 9, 'seed': 3},                           # the skyline behind
        ],
        'bands': 0.03, 'distance': 260,
    }
    lights = [{'at': a, 'x': (-1 if k % 2 else 1) * 3.4, 'z': 1.2, 'radius': 4.2,
               'color': PINK if k % 3 == 0 else CYAN if k % 3 == 1 else AMBER, 'intensity': 1.3}
              for k, a in enumerate(range(4, 200, 6))]
    roadside = [
        {'type': ['neon_sign', 'holo_ad', 'neon_fish', 'neon_cocktail'], 'every': 9, 'offset': [0.2, 0.6],
         'z': [2.0, 4.5], 'scale': [0.8, 1.4], 'flip': True, 'seed': 1},          # signs out over the street
        {'type': 'drone', 'side': 'middle', 'density': 0.05, 'offset': [-3, 3], 'z': [3.0, 6.0], 'scale': 0.5,
         'seed': 2},
    ]
    sprites = [
        {'type': 'sky_train', 'at': 34, 'x': 0.0, 'z': 6.5, 'scale': 2.4},       # on its bridge over the street
        {'type': 'hover_car', 'at': 12, 'x': -LANE, 'z': 0.06, 'tint': [1.0, 0.6, 1.0]},
        {'type': 'neon_bike', 'at': 18, 'x': LANE * 0.9},
        {'type': 'hover_car', 'at': 26, 'x': 0.2, 'z': 0.06, 'tint': [1.0, 0.85, 0.5]},
        {'type': 'hover_car', 'at': 44, 'x': LANE, 'z': 0.06},
    ]
    return road_scene(
        road,
        title='The neon race - a hover car through a cyberpunk city at night, the street wet with rain',
        sky='night',
        skyline='city',
        ambient=[0.16, 0.13, 0.24],
        fog={'color': [0.22, 0.1, 0.28], 'density': 0.012},
        lights=lights,
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.7, 'fov': 66, 'pitch': 0.08},
        shots=[
            {'at': 2.0, 'x': 0.0, 'height': 0.7, 'fov': 66, 'pitch': 0.08, 'post': NEON, 'overlays': HUD,
             'vehicle': {'type': 'hover_car', 'ahead': 2.5, 'z': 0.06, 'headlights': [0.7, 0.95, 1.0]}},
            {'at': 22.0, 'x': 0.0, 'height': 0.7, 'fov': 66, 'pitch': 0.06, 'roll': 7, 'yaw': 4,
             'post': NEON + [{'fx': 'speed', 'strength': 0.32}],
             'vehicle': {'type': 'hover_car', 'ahead': 2.5, 'z': 0.06, 'headlights': [0.7, 0.95, 1.0]}},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(neon_race().save(os.path.join(HERE, 'neon_race.json')))

"""The sky lane: a road scene (road.py) in the neon city's air - racing a lane of light hung high between the
towers at night, flying cars ahead, the city's grid glowing far below.

The lane is the road: a `light_lane` surface, only its edges, a dashed middle and chevrons lit, see-through between;
the ground `void` either side, and far `below` the city at night (`city_night`: avenues lit sodium orange, cars'
lights along them, roofs pricked with lit windows) in a violet haze. The towers stand either side in `blocks` -
`tower_windows` from far below to far above, gaps between - with signs hung out from them; hover cars fly the
lane ahead and the lanes above, your own car before you. The `speed` effect streaks the towers past.
Run:  python sky_lane.py  -> writes sky_lane.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

PINK, CYAN, AMBER = [1.0, 0.3, 0.75], [0.3, 0.95, 1.0], [1.0, 0.7, 0.25]
LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.8, 'radius': 2.4, 'spread': 0.6},
        {'fx': 'speed', 'strength': 0.35}]


def sky_lane():
    road = {
        'sections': [[12, 0, 0], [50, 0.3, 1.5], [50, -0.35, -1.0], [300, 0.15, 0.5]],
        'width': 2.0, 'surface': 'light_lane', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': 'void',
        'below': {'depth': 20, 'texture': 'city_night', 'tile': 10, 'haze': 0.3},
        'walls': [
            {'side': 'both', 'offset': 4.5, 'z': -20, 'height': 34, 'ragged': 12,
             'texture': ['tower_windows', 'tower_windows_b'], 'tile': [1.6, 1.6], 'blocks': 2.5, 'gaps': 0.45,
             'seed': 3},
            {'side': 'both', 'offset': 14, 'z': -20, 'height': 50, 'ragged': 20,
             'texture': ['tower_windows_b', 'tower_windows'], 'tile': [3.0, 3.0], 'blocks': 7.0, 'gaps': 0.2,
             'seed': 4},
        ],
        'distance': 260,
    }
    roadside = [
        {'type': ['neon_sign', 'hologram', 'neon_fish', 'neon_cocktail'], 'every': 9, 'offset': [4.1, 4.4],
         'z': [0.5, 4.0], 'scale': [1.0, 1.8], 'flip': True, 'seed': 1},
    ]
    sprites = [
        {'type': 'hover_car', 'at': 9, 'x': -0.4, 'z': 0.15, 'tint': [1.0, 0.7, 1.0]},
        {'type': 'hover_car', 'at': 17, 'x': 0.5, 'z': 0.2},
        {'type': 'hover_car', 'at': 14, 'x': -1.5, 'z': 3.5, 'tint': [1.0, 0.9, 0.6]},
        {'type': 'hover_car', 'at': 26, 'x': 1.2, 'z': 5.0},
        {'type': 'hover_car', 'at': 38, 'x': -0.8, 'z': -4.0, 'tint': [0.7, 1.0, 0.8]},
    ]
    return road_scene(
        road,
        title='The sky lane - racing a lane of light high between the towers at night, the city glowing far below',
        sky='night',
        skyline='city',
        ambient=[0.18, 0.15, 0.26],
        fog={'color': [0.2, 0.1, 0.3], 'density': 0.012},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 66, 'pitch': -0.18},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 66, 'pitch': -0.18, 'post': LOOK,
                'vehicle': {'type': 'hover_car', 'ahead': 2.2, 'z': 0.12, 'scale': 0.36, 'tint': [0.6, 0.9, 1.0]}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(sky_lane().save(os.path.join(HERE, 'sky_lane.json')))

"""The neon avenue: a road scene (road.py) - walking down an avenue of the neon city in the rain, the street and the
pavements wet, the traffic of the road beside you and of the air over it.

You walk the left-hand pavement (the camera `x` out past the kerb): shops beside you and across the street, cut
into buildings (`blocks`, each its own `shopfront`), towers over them lit window by window, signs hung out over
the pavement, strings of red lanterns and cables slung across the street. The road and the pavements are wet -
`wet` on the road, `reflect` on the pavement's band - and mirror it all. People out in the rain, a noodle stall,
steam rising from the street, a zebra crossing with its lights; a taxi in the traffic, and hover cars flying in
lanes over it. Rain falls through it all (`rain` with `splashes`).
Run:  python neon_avenue.py  -> writes neon_avenue.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

PINK, CYAN, AMBER, WHITE = [1.0, 0.3, 0.75], [0.3, 0.95, 1.0], [1.0, 0.7, 0.25], [0.8, 0.9, 1.0]
WALK = 2.4                                      # the pavements' width
LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 2.0, 'radius': 2.4, 'spread': 0.6},
        {'fx': 'rain', 'density': 1.3, 'length': 8, 'opacity': 0.3, 'angle': 10, 'color': [0.75, 0.8, 1.0]},
        {'fx': 'splashes'}]


def neon_avenue():
    road = {
        'sections': [[20, 0, 0], [60, 0.18, 0.2], [60, -0.22, 0.0], [300, 0.1, 0.0]],
        'width': 3.0, 'lanes': 2, 'surface': 'asphalt', 'lines': '#e8e8e8', 'edges': '#d8c040', 'rumble': False,
        'wet': 0.3, 'ripple': 0.5,
        'ground': [{'width': WALK, 'texture': 'concrete_floor', 'reflect': 0.18}, {'texture': 'concrete'}],
        'walls': [
            {'side': 'both', 'offset': WALK, 'height': 1.5, 'texture': ['shopfront', 'shopfront_b', 'shopfront_c'],
             'tile': [2.0, 1.5], 'blocks': 2.0, 'seed': 4},
            {'side': 'both', 'offset': WALK + 0.15, 'z': 1.5, 'height': 12, 'ragged': 6,
             'texture': ['tower_windows', 'tower_windows_b'], 'tile': [1.4, 1.4], 'blocks': 4.0, 'gaps': 0.1,
             'seed': 5},
            {'side': 'both', 'offset': 16, 'height': 44, 'ragged': 16, 'texture': ['tower_windows_b', 'tower_windows'],
             'tile': [3.2, 3.2], 'blocks': 9, 'seed': 6},
        ],
        'bands': 0.02, 'distance': 220,
    }
    lights = [{'at': a, 'x': (-1 if k % 2 else 1) * (1.5 + WALK - 0.4), 'z': 1.3, 'radius': 3.6,
               'color': [PINK, CYAN, AMBER][k % 3], 'intensity': 1.2} for k, a in enumerate(range(3, 160, 5))]
    roadside = [
        {'type': ['neon_sign', 'neon_fish', 'neon_cocktail', 'hologram'], 'every': 7, 'offset': [WALK - 0.5, WALK - 0.2],
         'z': [1.7, 3.2], 'scale': [0.7, 1.2], 'flip': True, 'seed': 1},           # signs hung out over the pavements
        {'type': 'lantern_span', 'side': 'middle', 'every': 13, 'offset': 0.0, 'from': 10, 'z': 3.2, 'scale': 4.6},
        {'type': 'wires_span', 'side': 'middle', 'every': 17, 'offset': 0.0, 'from': 11, 'z': 3.8, 'scale': 7.5},
        {'type': 'highway_lamp', 'side': 'right', 'every': 14, 'offset': -0.15, 'from': 9, 'flip': True,
         'light': {'color': WHITE, 'radius': 5.0, 'intensity': 0.9, 'z': 3.4, 'x': 1.0}},
    ]
    scatter = [{'of': 'crowd', 'side': 'both', 'density': 0.07, 'offset': [0.3, WALK - 0.3], 'sizes': ['medium'],
                'clump': 0.2, 'seed': 2, 'clear': 5}]                               # people out in the rain
    decals = [
        {'tex': 'city', 'density': 0.05, 'size': [0.5, 1.0], 'seed': 1},
        {'tex': 'zebra_crossing', 'at': 15, 'x': 0, 'size': 3.0},
        {'tex': 'puddle_shine', 'density': 0.06, 'side': 'both', 'offset': [0.2, WALK], 'size': [0.4, 0.9],
         'seed': 3},
    ]
    sprites = [
        {'type': 'traffic_light', 'at': 14.2, 'x': -1.8, 'variant': 0},
        {'type': 'traffic_light', 'at': 14.2, 'x': 1.8, 'variant': 0, 'flip': True},
        {'type': 'noodle_stall', 'at': 7.5, 'x': -1.5 - WALK + 0.55, 'scale': 1.2,
         'light': {'color': AMBER, 'radius': 2.4, 'intensity': 1.0, 'z': 1.0}},
        {'type': 'steam', 'at': 10, 'x': 0.4, 'scale': 1.4, 'opacity': 0.35},
        {'type': 'steam', 'at': 24, 'x': -0.7, 'scale': 1.6, 'opacity': 0.35},
        {'type': 'taxi', 'at': 11, 'x': 0.75},
        {'type': 'hover_car', 'at': 20, 'x': -0.8, 'z': 4.5, 'tint': [1.0, 0.7, 1.0]},     # the traffic of the air
        {'type': 'hover_car', 'at': 31, 'x': 0.9, 'z': 5.6},
        {'type': 'hover_car', 'at': 44, 'x': -0.6, 'z': 6.4, 'tint': [1.0, 0.9, 0.6]},
    ]
    return road_scene(
        road,
        title='The neon avenue - walking an avenue of the neon city in the rain, traffic on the road and in the air',
        sky='night',
        skyline='city',
        ambient=[0.17, 0.15, 0.25],
        fog={'color': [0.2, 0.15, 0.3], 'density': 0.02},
        lights=lights,
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': -2.55, 'height': 0.55, 'fov': 64, 'pitch': 0.12, 'yaw': 3},
        shots=[{'at': 2.0, 'x': -2.55, 'height': 0.55, 'fov': 64, 'pitch': 0.12, 'yaw': 3, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(neon_avenue().save(os.path.join(HERE, 'neon_avenue.json')))

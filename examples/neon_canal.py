"""The neon canal: a road scene (road.py) in the neon city's flooded quarter - by water taxi down a canal between its
towers at night in the rain, the shops at the water's edge lit, signs hung out over the water, lanterns strung
across, the traffic of the air overhead, and all of it doubled in the black water.

The canal is the road (`water` tinted violet, a slow `ripple`), a narrow ledge of wet concrete either side; the
buildings are the neon avenue's - `shopfront`s in `blocks` at the water's edge, `tower_windows` over them, taller
towers behind - and coloured lamps along both sides light the water. Signs (`neon_sign`, `neon_fish`,
`neon_cocktail`, `hologram`) hang out over it, `lantern_span`s and `wires_span`s cross it, a `holo_ad` glows on a
tower, another taxi ahead (`speedboat`), `hover_car`s overhead. Your own `water_taxi`'s bow before you; `rain`.
Run:  python neon_canal.py  -> writes neon_canal.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

PINK, CYAN, AMBER, WHITE = [1.0, 0.3, 0.75], [0.3, 0.95, 1.0], [1.0, 0.7, 0.25], [0.8, 0.9, 1.0]
LEDGE = 0.5                                      # the wet concrete either side of the water
LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 2.0, 'radius': 2.4, 'spread': 0.6},
        {'fx': 'rain', 'density': 1.2, 'length': 8, 'opacity': 0.3, 'angle': 10, 'color': [0.75, 0.8, 1.0]}]


def neon_canal():
    road = {
        'sections': [[16, 0, 0], [50, 0.2, 0], [60, -0.25, 0], [300, 0.1, 0]],
        'width': 3.2, 'surface': {'base': 'water', 'tint': [0.5, 0.48, 0.8]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'ripple': 0.5,
        'ground': [{'width': LEDGE, 'texture': 'concrete_floor', 'reflect': 0.18}, {'texture': 'concrete'}],
        'walls': [
            {'side': 'both', 'offset': LEDGE, 'height': 1.5, 'texture': ['shopfront', 'shopfront_b', 'shopfront_c'],
             'tile': [2.0, 1.5], 'blocks': 2.0, 'seed': 4},
            {'side': 'both', 'offset': LEDGE + 0.15, 'z': 1.5, 'height': 12, 'ragged': 6,
             'texture': ['tower_windows', 'tower_windows_b'], 'tile': [1.4, 1.4], 'blocks': 4.0, 'gaps': 0.1,
             'seed': 5},
            {'side': 'both', 'offset': 14, 'height': 44, 'ragged': 16, 'texture': ['tower_windows_b', 'tower_windows'],
             'tile': [3.2, 3.2], 'blocks': 9, 'seed': 6},
        ],
        'distance': 220,
    }
    lights = [{'at': a, 'x': (-1 if k % 2 else 1) * (1.6 + LEDGE - 0.3), 'z': 1.2, 'radius': 3.4,
               'color': [PINK, CYAN, AMBER][k % 3], 'intensity': 1.2} for k, a in enumerate(range(3, 160, 5))]
    roadside = [
        {'type': ['neon_sign', 'neon_fish', 'neon_cocktail', 'hologram'], 'every': 6, 'offset': [LEDGE - 0.4, LEDGE - 0.1],
         'z': [1.7, 3.2], 'scale': [0.7, 1.2], 'flip': True, 'seed': 1},           # signs hung out over the water
        {'type': 'lantern_span', 'side': 'middle', 'every': 12, 'offset': 0.0, 'from': 15, 'z': 3.0, 'scale': 3.4},
        {'type': 'wires_span', 'side': 'middle', 'every': 17, 'offset': 0.0, 'from': 11, 'z': 3.8, 'scale': 7.5},
    ]
    sprites = [
        {'type': 'speedboat', 'at': 9, 'x': 0.55, 'light': {'color': [1.0, 0.9, 0.7], 'radius': 2.0, 'intensity': 0.8,
                                                              'z': 0.5}},
        {'type': 'holo_ad', 'at': 28, 'x': -2.3, 'z': 3.2, 'scale': 2.4},
        {'type': 'hover_car', 'at': 18, 'x': -0.6, 'z': 4.2, 'tint': [1.0, 0.7, 1.0]},     # the traffic of the air
        {'type': 'hover_car', 'at': 30, 'x': 0.8, 'z': 5.4},
        {'type': 'hover_car', 'at': 44, 'x': -0.5, 'z': 6.2, 'tint': [1.0, 0.9, 0.6]},
    ]
    return road_scene(
        road,
        title='The neon canal - by water taxi down a canal of the neon city at night, in the rain, its lights in '
              'the water',
        sky='night',
        skyline='city',
        ambient=[0.17, 0.15, 0.25],
        fog={'color': [0.2, 0.15, 0.3], 'density': 0.02},
        lights=lights,
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.06},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'water_taxi', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5,
                            'light': {'color': [0.9, 0.95, 1.0], 'radius': 2.4, 'intensity': 0.8, 'z': 0.4,
                                      'at': 0.1}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(neon_canal().save(os.path.join(HERE, 'neon_canal.json')))

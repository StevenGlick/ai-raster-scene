"""The reef dive: a road scene (road.py) on a coral reef in the shallows - swimming along the reef behind your
dive buddy, corals crowding the sand either side, the reef wall rising on the left, a manta ray gliding over, a
whale shark passing, sunlight rippling down from the surface.

No road but the sand (`reef_flat` for the floor and the way, its edges ragged); the reef wall rises along the left
(`reef_wall`, ragged); the surface is a `ceiling` of `water_surface` close overhead, bright; corals crowd both sides
(`brain_coral`, `staghorn_coral`, `anemone`), clownfish by an anemone, angelfish and a `fish_school`, a
`sea_turtle`, the `manta_ray` and the `whale_shark` overhead, `light_shaft`s; the `diver` ahead with `bubbles`
rising. A turquoise `fog`, marine snow.
Run:  python reef_dive.py  -> writes reef_dive.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.8, 'radius': 2.4},
        {'fx': 'snow', 'color': [0.8, 0.94, 0.94], 'count': 90, 'opacity': 0.35}]        # marine snow
REEF = {'base': 'reef_flat', 'tint': [1.05, 1.0, 0.95]}


def reef_dive():
    road = {
        'sections': [[16, 0, 0], [30, -0.15, 0.3], [30, 0.2, -0.2], [200, 0.05, 0.1]],
        'width': 1.8, 'surface': REEF, 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.4, 'blend': 1.0},
        'ground': REEF,
        'walls': [{'side': 'left', 'offset': 2.5, 'height': 5, 'texture': 'reef_wall', 'tile': 2.5, 'ragged': 2,
                   'seed': 2}],
        'ceiling': {'height': 6.5, 'texture': 'water_surface', 'tile': 4.0, 'light': 1.0},
        'distance': 300,
    }
    roadside = [
        {'type': ['brain_coral', 'staghorn_coral', 'anemone', 'staghorn_coral'], 'density': 1.4,
         'offset': [0.1, 5.0], 'scale': [0.4, 0.9], 'from': 2.5, 'seed': 1},
        {'type': 'light_shaft', 'side': 'middle', 'density': 0.12, 'offset': [-3.0, 3.0], 'scale': [5.0, 6.5],
         'seed': 3},
    ]
    sprites = [
        {'type': 'diver', 'at': 4.5, 'x': 0.1, 'z': 0.7, 'view': 'back'},
        {'type': 'bubbles', 'at': 4.4, 'x': 0.15, 'z': 1.5, 'scale': 0.8},
        {'type': 'manta_ray', 'at': 10, 'x': -0.8, 'z': 3.2, 'scale': 1.2},
        {'type': 'whale_shark', 'at': 22, 'x': 2.6, 'z': 2.2, 'scale': 1.6, 'flip': True},
        {'type': 'sea_turtle', 'at': 7, 'x': 1.4, 'z': 1.2},
        {'type': 'fish_school', 'at': 6, 'x': -1.2, 'z': 1.6},
        {'type': 'clownfish', 'at': 3.4, 'x': -0.9, 'z': 0.3},
        {'type': 'angelfish', 'at': 5.5, 'x': 1.0, 'z': 0.6},
    ]
    return road_scene(
        road,
        title='The reef dive - swimming along a coral reef behind your buddy, a manta overhead, a whale shark passing',
        sky='storm',
        ambient=[0.45, 0.66, 0.7],
        fog={'color': [0.1, 0.5, 0.6], 'density': 0.045, 'sky_mix': 1.0},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 1.0, 'fov': 64, 'pitch': 0.02},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 1.0, 'fov': 64, 'pitch': 0.02, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(reef_dive().save(os.path.join(HERE, 'reef_dive.json')))

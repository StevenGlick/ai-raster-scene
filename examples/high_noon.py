"""High noon: a road scene (road.py) on foot - standing in the main street of a frontier town at noon, the false
fronts of its buildings either side, a gunslinger waiting in the middle of the street, horses at the rails,
tumbleweeds blowing through, the water tower at the end of town and the mesas beyond.

The street is the road (dust: `desert_wash` tinted); a boardwalk either side (`planks`), then the buildings as
`walls` in `blocks` - `western_front`, `_b`, `_c`, each its own height. A `cowboy` stands square in the street
ahead; `horse`s stand at the rails, `tumbleweed`s roll, a `water_trough` and a `wagon_wheel` by the walks, the
`water_tower` closes the street; the `mountains` skyline in red rock. A high, hard sun and heat in the air.
Run:  python high_noon.py  -> writes high_noon.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]
WALK = 0.7


def high_noon():
    road = {
        'sections': [[60, 0, 0], [200, 0.02, 0.3]],
        'width': 3.0, 'surface': {'base': 'desert_wash', 'tint': [0.88, 0.76, 0.62]}, 'lines': False,
        'rumble': False, 'bands': 0.0, 'edge': {'ragged': 0.15, 'blend': 0.3},
        'ground': [{'width': WALK, 'texture': 'planks'}, {'texture': 'desert_wash'}],
        'walls': [{'side': 'both', 'offset': WALK, 'from': 1, 'to': 40, 'height': 2.2, 'ragged': 0.5,
                   'texture': ['western_front', 'western_front_b', 'western_front_c'], 'tile': [2.0, 2.2],
                   'blocks': 2.0, 'seed': 3}],
        'distance': 200,
    }
    roadside = [
        {'type': 'horse', 'side': 'both', 'every': 7, 'offset': -0.1, 'from': 4, 'seed': 2},
        {'type': 'tumbleweed', 'density': 0.06, 'offset': [-1.4, 0.4], 'scale': [0.3, 0.45], 'seed': 4},
    ]
    sprites = [
        {'type': 'cowboy', 'at': 5.5, 'x': 0.15, 'view': 'front'},
        {'type': 'water_trough', 'at': 6, 'x': -2.1},
        {'type': 'wagon_wheel', 'at': 11, 'x': 2.15},
        {'type': 'water_tower', 'at': 44, 'x': 1.2, 'scale': 3.2},
    ]
    return road_scene(
        road,
        title='High noon - standing in the main street of a frontier town at noon, a gunslinger waiting in the street',
        sky='day',
        skyline={'type': 'mountains', 'height': 1.2, 'color': [0.72, 0.42, 0.3]},
        lights=[{'type': 'sun', 'azimuth': 200, 'elevation': 62, 'intensity': 1.0, 'color': [1.0, 0.95, 0.85]}],
        ambient=[0.62, 0.56, 0.5],
        fog={'color': [0.92, 0.82, 0.66], 'density': 0.006, 'sky_mix': 0.3},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': -0.2, 'height': 0.5, 'fov': 60, 'pitch': 0.08},
        shots=[{'at': 1.0, 'x': -0.2, 'height': 0.5, 'fov': 60, 'pitch': 0.08, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(high_noon().save(os.path.join(HERE, 'high_noon.json')))

"""The hill street: a road scene (road.py) in a city by the sea - at the top of a steep street of painted
townhouses, a cable tram going down ahead, the street running on out across the bay toward the great bridge in the
fog.

The street drops away in its `sections` (5 down in 20, then gentler), the cable's slot down its middle (`centre`);
a pavement either side, then the townhouses as `walls` in `blocks` - `townhouse`, `_b`, `_c`, in lavender, mint and
cream - until the street reaches the shore, where they end and the bay (`harbor_water`) opens either side. The
`tram` goes on down ahead, cars parked at the kerb, street lamps; the `bridge_tower`s stand out of the fog beyond.
Run:  python hill_street.py  -> writes hill_street.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]
SHORE = 34


def hill_street():
    road = {
        'sections': [[6, 0, 0.2], [20, 0, -5.5], [12, 0, -1.6], [300, 0, 0]],
        'width': 2.2, 'lanes': 2, 'surface': 'asphalt', 'lines': False, 'centre': '#2a2a2c', 'rumble': False,
        'bands': 0.02,
        'ground': [{'width': 0.8, 'texture': 'concrete_floor'}, {'texture': 'harbor_water'}],
        'walls': [{'side': 'both', 'offset': 0.8, 'to': SHORE, 'height': 2.2, 'ragged': 0.6,
                   'texture': ['townhouse', 'townhouse_b', 'townhouse_c'], 'tile': [1.6, 1.6], 'blocks': 1.6,
                   'seed': 2}],
        'distance': 300,
    }
    roadside = [
        {'type': 'lamp_post', 'side': 'both', 'every': 6, 'offset': 0.15, 'from': 3, 'to': SHORE, 'scale': 0.9},
        {'type': ['car_compact', 'car_sedan'], 'side': 'both', 'every': 4.5, 'offset': -0.25, 'from': 7.5, 'to': SHORE - 2,
         'seed': 3},
    ]
    sprites = [
        {'type': 'tram', 'at': 10.5, 'x': -0.35},
        {'type': 'bridge_tower', 'at': 120, 'x': 0.0, 'z': -2, 'scale': 16},
        {'type': 'bridge_tower', 'at': 175, 'x': 0.0, 'z': -2, 'scale': 16},
    ]
    return road_scene(
        road,
        title='The hill street - at the top of a steep street of painted houses, a tram going down, the bridge in the fog',
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 300, 'elevation': 35, 'intensity': 0.75}],
        ambient=[0.62, 0.64, 0.7],
        fog={'color': [0.86, 0.88, 0.92], 'density': 0.01, 'sky_mix': 0.4},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 4.5, 'x': 0.55, 'height': 0.55, 'fov': 62, 'pitch': -0.04},
        shots=[{'at': 4.5, 'x': 0.55, 'height': 0.55, 'fov': 62, 'pitch': -0.04, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(hill_street().save(os.path.join(HERE, 'hill_street.json')))

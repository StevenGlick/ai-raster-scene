"""The lavender ride: a road scene (road.py) on a summer afternoon in the south - riding a scooter down a lane
between fields of lavender in flower, rows of purple to the hills, a line of dark cypresses along the lane, olive
trees, the light going golden.

A narrow lane (`asphalt` pale with sun, no lines) with dry verges; the fields are `lavender_field` (rows running
along the lane, closing into purple bands to the horizon); `cypress`es in a line beside it, `olive_tree`s scattered
out in the fields; low blue `hills` far off, a `golden` sky. Your scooter's handlebars and mirrors before you
(`scooter_bars`, the shot's vehicle).
Run:  python lavender_ride.py  -> writes lavender_ride.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.2}]


def lavender_ride():
    road = {
        'sections': [[20, 0, 0], [50, 0.1, 0.2], [50, -0.15, -0.2], [300, 0.05, 0]],
        'width': 1.6, 'surface': {'base': 'asphalt', 'tint': [1.7, 1.6, 1.45]}, 'lines': False, 'rumble': False,
        'bands': 0.0,
        'ground': [{'width': 0.4, 'texture': 'dry_grass'}, {'texture': 'lavender_field'}],
        'distance': 300,
    }
    roadside = [
        {'type': 'cypress', 'side': 'right', 'every': 5, 'offset': 0.5, 'from': 4, 'scale': [3.2, 4.2], 'seed': 1},
        {'type': 'olive_tree', 'density': 0.03, 'offset': [3.0, 30.0], 'scale': [1.2, 1.8], 'seed': 2},
    ]
    return road_scene(
        road,
        title='The lavender ride - a scooter down a lane between fields of lavender in flower, cypresses, golden light',
        sky='golden',
        skyline={'type': 'hills', 'height': 0.8, 'color': [0.5, 0.56, 0.72]},
        lights=[{'type': 'sun', 'azimuth': 235, 'elevation': 20, 'intensity': 0.9, 'color': [1.0, 0.88, 0.7]}],
        ambient=[0.62, 0.6, 0.6],
        fog={'color': [0.86, 0.8, 0.78], 'density': 0.004, 'sky_mix': 0.3},
        roadside=roadside,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'scooter_bars', 'ahead': 0.7, 'z': 0.33, 'scale': 0.24}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(lavender_ride().save(os.path.join(HERE, 'lavender_ride.json')))

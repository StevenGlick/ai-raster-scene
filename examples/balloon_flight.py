"""The balloon flight: a road scene (road.py) in the air - drifting in a hot-air balloon over the desert at dawn,
other balloons floating at every height around you, the plain and its mesas far below, the sun just up.

The balloon's way is the road, too narrow to see; the ground is `void` and far `below` lies the desert
(`desert_floor` at landscape scale); the mesas stand round it as a red `mountains` skyline. Balloons hang at every
height and distance (`balloon`, scattered by density with `z` spread), a few near; the sun low over the horizon in
a `dawn` sky. Your own basket's rim and the burner's frame before you (`basket_rim`, the shot's vehicle).
Run:  python balloon_flight.py  -> writes balloon_flight.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.2}]


def balloon_flight():
    road = {
        'sections': [[400, 0.02, 0]],
        'width': 0.002, 'surface': 'asphalt', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': 'void',
        'below': {'depth': 26, 'tile': 18, 'haze': 0.5, 'texture': 'desert_floor'},
        'distance': 400,
    }
    roadside = [
        {'type': 'balloon', 'density': 0.04, 'offset': [2.0, 40.0], 'z': [-12.0, 8.0], 'scale': [1.4, 2.2],
         'seed': 3},
    ]
    sprites = [
        {'type': 'balloon', 'at': 9, 'x': 3.0, 'z': -1.0, 'scale': 2.4},
        {'type': 'balloon', 'at': 14, 'x': -4.5, 'z': 1.5, 'scale': 2.4, 'flip': True},
        {'type': 'balloon', 'at': 22, 'x': 1.0, 'z': -6.0, 'scale': 2.2},
    ]
    return road_scene(
        road,
        title='The balloon flight - drifting over the desert at dawn, balloons at every height, the mesas far below',
        sky='dawn',
        skyline={'type': 'mountains', 'height': 0.9, 'color': [0.62, 0.4, 0.36]},
        sky_objects=[{'type': 'sun', 'azimuth': 262, 'elevation': 3, 'size': 3.0}],
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 8, 'intensity': 0.9, 'color': [1.0, 0.8, 0.6],
                 'disc': False}],
        ambient=[0.6, 0.54, 0.56],
        fog={'color': [0.92, 0.76, 0.66], 'density': 0.003, 'sky_mix': 0.3},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': -0.08},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': -0.08, 'post': LOOK,
                'vehicle': {'type': 'basket_rim', 'ahead': 0.6, 'z': 0.3, 'scale': 0.4}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(balloon_flight().save(os.path.join(HERE, 'balloon_flight.json')))

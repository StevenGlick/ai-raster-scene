"""The canal boat: a road scene (road.py) on the water - by boat down a canal tunnel under an old town, lanterns
along its walls, daylight at its far end.

The road is the canal (`surface` `water`); the vault over it is `brick_ring`s set down its middle a little under
a unit apart, each framing the next, under a `roof` (the sky's light gone). Lamps on the walls, a light at each;
the water mirrors them, the vault and the boats (props are reflected about their feet; under a roof the water
mirrors no sky). A narrowboat goes ahead of you; the shot's `vehicle` is the bow of your own boat with its lantern lit (a `light` it carries). Beyond the
tunnel's mouth the canal runs on between low walls into the morning.
Run:  python canal_boat.py  -> writes canal_boat.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 2.4, 'spread': 0.5}]
END = 44                                     # where the tunnel comes out into the daylight
LAMP = [1.0, 0.72, 0.4]


def canal_boat():
    road = {
        'sections': [[14, 0, 0], [30, 0.12, 0], [30, -0.15, 0], [200, 0.1, 0]],
        'width': 2.2, 'surface': 'water', 'lines': False, 'rumble': False, 'bands': 0.0, 'ripple': 0.6,
        'ground': 'water',
        'walls': [{'side': 'both', 'offset': 0.1, 'height': 0.9, 'texture': 'brick', 'tile': 1.0, 'from': END}],
        'roofs': [[0, END, 0.25]],
        'distance': 160,
    }
    roadside = [
        {'type': 'brick_ring', 'side': 'middle', 'every': 0.9, 'offset': 0.0, 'from': 0.5, 'to': END},
        {'type': 'wall_lamp', 'side': 'left', 'every': 8, 'offset': 0.12, 'from': 4, 'to': END, 'z': 1.2,
         'light': {'color': LAMP, 'radius': 3.2, 'intensity': 1.3, 'z': 1.4, 'x': 0.3}},
        {'type': 'wall_lamp', 'side': 'right', 'every': 8, 'offset': 0.12, 'from': 8, 'to': END, 'z': 1.2,
         'flip': True, 'light': {'color': LAMP, 'radius': 3.2, 'intensity': 1.3, 'z': 1.4, 'x': 0.3}},
    ]
    sprites = [
        {'type': 'narrowboat', 'at': 12.0, 'x': 0.05, 'z': -0.08,
         'light': {'color': LAMP, 'radius': 2.2, 'intensity': 0.9, 'z': 0.9, 'at': 0.3}},   # its cabin lit
    ]
    return road_scene(
        road,
        title='The canal boat - by boat through a brick tunnel under an old town, lamps along its walls',
        sky='dawn',
        lights=[{'type': 'sun', 'azimuth': 268, 'elevation': 10, 'intensity': 0.7, 'color': [1.0, 0.86, 0.66]}],
        ambient=[0.42, 0.42, 0.46],
        fog={'color': [0.2, 0.22, 0.2], 'density': 0.02},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.06},
        shots=[
            {'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.06, 'post': LOOK,
             'vehicle': {'type': 'boat_bow', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5,
                         'light': {'color': LAMP, 'radius': 2.6, 'intensity': 1.2, 'z': 0.5, 'at': 0.1}}},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(canal_boat().save(os.path.join(HERE, 'canal_boat.json')))

"""The suspension bridge: a road scene (road.py) - driving across a great suspension bridge at dawn, its red towers
standing over the road every span, the cables sagging between them, the bay far below, the city ahead.

The deck is the road (four lanes); either side nothing - the ground `void` - and far `below` the bay (`harbor_water`
with `ocean` beyond). The towers are `bridge_tower`s down the `middle` every 40 from 0, and the cables `walls` of
`suspension_cables` along both edges, tiled one span long so the main cable sags from tower to tower; a rail along
the deck's edges, lamps on the rail. Cars on it, the city's skyline ahead, a low sun.
Run:  python suspension_bridge.py  -> writes suspension_bridge.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.8, 'radius': 2.2}]
SPAN, TOWER = 40, 10.0
W = 5.6
LANE = W / 4


def suspension_bridge():
    road = {
        'sections': [[300, 0, 0]],
        'width': W, 'lanes': 4, 'surface': 'asphalt', 'edges': '#e0e0dc', 'rumble': False,
        'ground': 'void',
        'below': {'depth': 22, 'tile': 33, 'haze': 0.6, 'texture': [{'width': 200, 'texture': 'harbor_water'},
                                                                   {'texture': 'ocean'}]},
        'walls': [
            {'side': 'both', 'offset': 0.25, 'height': 0.3, 'texture': 'guard_rail', 'tile': [1, 0.3]},
            {'side': 'both', 'offset': 0.35, 'height': TOWER, 'texture': 'suspension_cables', 'tile': [SPAN, TOWER]},
        ],
        'bands': 0.03, 'distance': 300,
    }
    roadside = [
        {'type': 'bridge_tower', 'side': 'middle', 'every': SPAN, 'from': 0, 'offset': 0.0, 'scale': TOWER},
        {'type': 'highway_lamp', 'every': 10, 'offset': 0.1, 'from': 5, 'flip': True, 'scale': 2.4},
    ]
    sprites = [
        {'type': 'car_sedan', 'at': 12, 'x': -LANE / 2 - LANE, 'variant': 0},
        {'type': 'box_truck', 'at': 20, 'x': LANE / 2},
        {'type': 'car_compact', 'at': 30, 'x': -LANE / 2, 'variant': 1},
    ]
    return road_scene(
        road,
        title='The suspension bridge - across a great suspension bridge at dawn, the bay far below',
        sky='dawn',
        skyline='city',
        lights=[{'type': 'sun', 'azimuth': 285, 'elevation': 7, 'intensity': 0.75, 'color': [1.0, 0.84, 0.66]}],
        ambient=[0.56, 0.54, 0.58],
        fog={'color': [0.86, 0.78, 0.76], 'density': 0.003},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': LANE / 2, 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[{'at': 2.0, 'x': LANE / 2, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(suspension_bridge().save(os.path.join(HERE, 'suspension_bridge.json')))

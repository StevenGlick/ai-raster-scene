"""The candy road: a road scene (road.py) - racing a road of peppermint through a land of sweets, candy canes along
it, lollipop trees, gumdrop hills, a chocolate river, a gingerbread house with its windows lit.

The road is `peppermint` (red and white stripes slantwise) with rumble strips of white and pink; the ground is
`frosting` (pink icing and sprinkles), a river of chocolate along the right (`mud` tinted, its band's `reflect`
0.15 so it shines a little); `candy_cane`s every few units either side with their crooks over the road,
`lollipop` trees and `gumdrop`s of every size and colour by density, gingerbread houses; the `dream` sky. Your car
in pink.
Run:  python candy_road.py  -> writes candy_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.0}]
FROSTING = 'frosting'
CHOCOLATE = {'base': 'mud', 'tint': [0.72, 0.38, 0.2]}


def candy_road():
    road = {
        'sections': [[10, 0, 0], [30, 0.4, 1.0], [30, -0.5, -0.8], [40, 0.3, 1.2], [300, -0.1, 0]],
        'width': 2.6, 'surface': 'peppermint', 'lines': False,
        'rumble': {'width': 0.25, 'colors': ['#ffffff', '#ff5aa8']}, 'bands': 0.0,
        'ground': {'left': FROSTING,
                   'right': [{'width': 1.2, 'texture': FROSTING}, {'width': 2.2, 'texture': CHOCOLATE, 'reflect': 0.15},
                             {'texture': FROSTING}]},
        'distance': 240,
    }
    roadside = [
        {'type': 'candy_cane', 'side': 'left', 'every': 5, 'offset': 0.35, 'from': 3},
        {'type': 'candy_cane', 'side': 'right', 'every': 5, 'offset': 0.35, 'from': 5.5, 'flip': True},
        {'type': 'lollipop', 'density': 0.12, 'offset': [1.4, 12.0], 'scale': [1.8, 3.2], 'seed': 1},
        {'type': 'gumdrop', 'density': 0.1, 'offset': [3.6, 30.0], 'scale': [0.6, 4.0], 'seed': 2},
    ]
    sprites = [
        {'type': 'gingerbread_house', 'at': 13, 'x': -4.2, 'scale': 2.2,
         'light': {'color': [1.0, 0.8, 0.5], 'radius': 2.5, 'intensity': 0.6, 'z': 0.8}},
        {'type': 'gingerbread_house', 'at': 46, 'x': 9.0, 'scale': 2.4, 'flip': True},
    ]
    return road_scene(
        road,
        title='The candy road - racing a road of peppermint through a land of sweets, lollipop trees and gumdrop hills',
        sky='dream',
        skyline={'type': 'hills', 'height': 1.2, 'color': [0.96, 0.7, 0.86]},
        lights=[{'type': 'sun', 'azimuth': 250, 'elevation': 30, 'intensity': 0.8, 'color': [1.0, 0.95, 0.9]}],
        ambient=[0.66, 0.62, 0.7],
        fog={'color': [0.98, 0.86, 0.92], 'density': 0.005, 'sky_mix': 0.2},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.08},
        shots=[{'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.08, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'tint': [1.0, 0.62, 0.9]}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(candy_road().save(os.path.join(HERE, 'candy_road.json')))

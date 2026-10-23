"""The market ride: a road scene (road.py) in a medieval town - riding a horse up the high street on market day, the
half-timbered houses leaning over it, stalls along both sides and the town's people at them, banners out, the
castle on its hill at the street's end.

The street is `cobble`, a strip of `flagstone` either side; the houses are `timber_house` walls in three plasters
(`blocks` one tile wide and one tall, so each is its own house and the gables make the skyline). Stalls
(`market_stall`, `fruit_stall`), `banner`s hung from the houses, barrels, sacks and hay; the people are characters
(`villager`, `farmer`, `shopkeeper`, `monk`, `child`, `knight`); a cart ahead; the `castle_hill` at the end. Your
horse's neck and ears before you (`horse_neck`, the shot's vehicle).
Run:  python market_ride.py  -> writes market_ride.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.4, 'radius': 2.0}]
WALK = 0.7                                       # the flagstones either side


def market_ride():
    road = {
        'sections': [[16, 0, 0], [30, 0.12, 0.25], [30, -0.1, 0.1], [200, 0.0, 0.0]],
        'width': 2.4, 'surface': 'cobble', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': [{'width': WALK, 'texture': 'flagstone'}, {'texture': 'cobble'}],
        'walls': [{'side': 'both', 'offset': WALK, 'height': 2.6, 'tile': [2.0, 2.6], 'blocks': 2.0, 'seed': 3,
                   'texture': ['timber_house', 'timber_house_b', 'timber_house_c']}],
        'distance': 120,
    }
    roadside = [
        {'type': ['market_stall', 'fruit_stall'], 'every': 5.5, 'offset': [0.05, 0.25], 'from': 9, 'to': 40,
         'flip': True, 'seed': 1},
        {'type': 'banner', 'every': 6, 'offset': WALK - 0.05, 'z': 1.4, 'from': 6, 'flip': True, 'seed': 2},
        {'type': ['barrel', 'sack', 'hay_bale', 'crate'], 'density': 0.5, 'offset': [0.0, WALK - 0.1],
         'scale': [0.2, 0.32], 'from': 3, 'seed': 4},
    ]
    sprites = [
        {'type': 'villager', 'at': 5.5, 'x': -1.2},
        {'type': 'farmer', 'at': 7.5, 'x': 1.1, 'flip': True},
        {'type': 'shopkeeper', 'at': 11.5, 'x': -1.0},
        {'type': 'monk', 'at': 13, 'x': 0.35, 'view': 'back'},
        {'type': 'child', 'at': 6.4, 'x': -0.7},
        {'type': 'knight', 'at': 17, 'x': -0.3, 'view': 'back'},
        {'type': 'villager', 'at': 15, 'x': 0.9, 'flip': True},
        {'type': 'cart', 'at': 24, 'x': 0.5},
        {'type': 'well', 'at': 30, 'x': -1.1},
        {'type': 'castle_hill', 'at': 70, 'x': 0.0, 'scale': 21},
    ]
    return road_scene(
        road,
        title="The market ride - riding up a medieval town's high street on market day toward the castle on its hill",
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 300, 'elevation': 40, 'intensity': 0.9, 'color': [1.0, 0.95, 0.85]}],
        ambient=[0.62, 0.62, 0.66],
        fog={'color': [0.78, 0.84, 0.92], 'density': 0.003},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'horse_neck', 'ahead': 0.7, 'z': 0.5, 'scale': 0.26}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(market_ride().save(os.path.join(HERE, 'market_ride.json')))

"""The tulip ride: a road scene (road.py) - cycling a red cycle path through the bulb fields in spring, bands of
tulips in flower running away to the horizon either side, windmills standing out in them, a big sky.

The path is the road (red asphalt); either side a strip of grass, a ditch of still water mirroring
the sky, then the fields in bands along the road - `tulip_field` in red, `_b` yellow, `_c` pink, `_d` purple -
whose rows close up into stripes of colour to the horizon; a line of trees far out. Windmills stand in the fields;
reeds along the ditches; two people cycling ahead; your own handlebars, your hands on them and tulips in the
basket (`bike_bars`, the shot's vehicle).
Run:  python tulip_ride.py  -> writes tulip_ride.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]


def fields(order):
    bands = [{'width': 0.35, 'texture': 'grass'}, {'width': 0.7, 'texture': 'water'}, {'width': 0.35, 'texture': 'grass'}]
    for t in order:
        bands.append({'width': 2.6, 'texture': t})
    return bands + [{'texture': 'pasture'}]


def tulip_ride():
    road = {
        'sections': [[20, 0, 0], [60, 0.08, 0], [60, -0.1, 0], [400, 0.04, 0]],
        'width': 1.2, 'surface': {'base': 'asphalt', 'tint': [0.85, 0.42, 0.36]}, 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': {'left': fields(['tulip_field', 'tulip_field_b', 'tulip_field_c', 'tulip_field_d', 'tulip_field_b',
                                   'tulip_field']),
                   'right': fields(['tulip_field_c', 'tulip_field', 'tulip_field_b', 'tulip_field_d', 'tulip_field_c',
                                    'tulip_field_b'])},
        'distance': 400,
    }
    roadside = [
        {'type': 'reeds', 'density': 0.8, 'offset': [0.3, 1.1], 'scale': [0.3, 0.5], 'seed': 1},
        {'type': 'tree', 'side': 'both', 'every': 2.2, 'offset': 18.5, 'scale': [2.2, 2.8], 'seed': 2},
    ]
    sprites = [
        {'type': 'windmill', 'at': 28, 'x': -11, 'scale': 4.5},
        {'type': 'windmill', 'at': 52, 'x': 15, 'scale': 5.0, 'flip': True},
        {'type': 'windmill', 'at': 17, 'x': 7.5, 'scale': 4.2},
        {'type': 'windmill', 'at': 120, 'x': -24, 'scale': 5.0},
        {'type': 'cyclist', 'at': 6.5, 'x': 0.2},
        {'type': 'cyclist', 'at': 14, 'x': -0.25, 'tint': [1.2, 0.8, 0.8]},
    ]
    return road_scene(
        road,
        title='The tulip ride - cycling a red path through the bulb fields in spring, windmills in the tulips',
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 232, 'elevation': 34, 'intensity': 0.9, 'color': [1.0, 0.96, 0.88]}],
        ambient=[0.62, 0.64, 0.7],
        fog={'color': [0.78, 0.84, 0.92], 'density': 0.004, 'sky_mix': 0.2},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 64, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'bike_bars', 'ahead': 0.8, 'z': 0.17, 'scale': 0.3}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(tulip_ride().save(os.path.join(HERE, 'tulip_ride.json')))

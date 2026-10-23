"""The viaduct train: a road scene (road.py) - on the footplate of a steam engine crossing a long stone viaduct
high over a valley in the late afternoon.

The road is the line (`rail_track`) between the viaduct's parapets, low `walls` of `stone`; either side nothing -
the ground is `void` - and far `below` the valley's woods, its river and its pastures. Steam from the engine drifts
back past the cab (`steam`, translucent, rising from the chimney); the engine's boiler runs away ahead of you
(`loco_boiler`, the shot's vehicle); telegraph poles with their wires along the line; a low sun.
Run:  python viaduct_train.py  -> writes viaduct_train.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.0}]


def viaduct_train():
    road = {
        'sections': [[20, 0, 0], [40, 0.35, 0], [300, 0.1, 0.5]],
        'width': 1.4, 'surface': 'rail_track', 'lines': False, 'rumble': False, 'bands': 0.02,
        'ground': {'left': 'void', 'right': 'void'},
        'below': {'depth': 34, 'tile': 33, 'haze': 0.6,
                  'texture': [{'width': 30, 'texture': 'forest_canopy'}, {'width': 8, 'texture': 'river_water'},
                              {'width': 60, 'texture': 'pasture'}, {'texture': 'forest_canopy'}]},
        'walls': [
            {'side': 'both', 'offset': 0.15, 'height': 0.42, 'texture': 'stone', 'tile': 0.8},   # the parapets
            {'side': 'right', 'offset': 0.6, 'z': 2.35, 'height': 0.5, 'texture': 'power_lines', 'tile': [9, 0.5]},
        ],
        'distance': 300,
    }
    roadside = [
        {'type': 'telegraph_pole', 'side': 'right', 'every': 9, 'from': 0, 'offset': 0.6},
    ]
    sprites = [
        {'type': 'steam', 'at': 2.62, 'x': 0.0, 'z': 0.86, 'scale': 0.55, 'opacity': 0.75},   # from the chimney
        {'type': 'steam', 'at': 2.3, 'x': -0.12, 'z': 1.1, 'scale': 0.9, 'opacity': 0.55},    # and drifting back
        {'type': 'steam', 'at': 1.95, 'x': -0.35, 'z': 1.35, 'scale': 1.4, 'opacity': 0.4},
    ]
    return road_scene(
        road,
        title='The viaduct train - at the front of a train crossing a long stone viaduct high over a valley',
        sky='golden',
        skyline='mountains',
        lights=[{'type': 'sun', 'azimuth': 240, 'elevation': 14, 'intensity': 0.8, 'color': [1.0, 0.86, 0.66]}],
        ambient=[0.6, 0.56, 0.54],
        fog={'color': [0.86, 0.8, 0.72], 'density': 0.0025},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.9, 'fov': 64, 'pitch': -0.02},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.9, 'fov': 64, 'pitch': -0.02, 'post': LOOK,
                'vehicle': {'type': 'loco_boiler', 'ahead': 1.6, 'z': 0.3, 'scale': 0.62}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(viaduct_train().save(os.path.join(HERE, 'viaduct_train.json')))

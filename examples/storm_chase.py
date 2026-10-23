"""The storm chase: a road scene (road.py) - chasing a tornado down a straight road across the plains, the funnel
dropping out of the storm in the fields ahead, lightning, wheat to the horizon, a red barn, the chasers' pickup.

Two lanes of asphalt dead straight over gentle swells, a yellow centre line, a gravel shoulder; either side grass
and then `wheat_field` to the horizon. Telegraph poles carry the wires along the right (`power_lines` at their
arms). The `tornado` stands out in the fields ahead and left, a red `barn` and its silo on the right; under the
`storm` sky a last low sun breaks in from the west, gold on the wheat; `lightning` forks down. You drive the
chasers' `pickup_truck` (the shot's vehicle), its instruments on the roof.
Run:  python storm_chase.py  -> writes storm_chase.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'lightning', 'amount': 0.18, 'x': 0.78, 'y_end': 0.38},
        {'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]


def storm_chase():
    road = {
        'sections': [[20, 0, 0], [60, 0.0, 0.6], [60, 0.0, -0.4], [400, 0.0, 0.2]],
        'width': 2.2, 'lanes': 2, 'surface': 'asphalt', 'lines': False, 'centre': '#e8c040', 'rumble': False,
        'shoulder': {'width': 0.4, 'texture': 'gravel'}, 'bands': 0.03,
        'ground': [{'width': 1.0, 'texture': 'grass'}, {'texture': 'wheat_field', 'tile': 1.5}],
        'walls': [{'side': 'right', 'offset': 1.6, 'z': 2.35, 'height': 0.5, 'texture': 'power_lines',
                   'tile': [9, 0.5]}],
        'distance': 400,
    }
    roadside = [
        {'type': 'telegraph_pole', 'side': 'right', 'every': 9, 'from': 0, 'offset': 1.6},
        {'type': 'hay_bale', 'side': 'left', 'density': 0.03, 'offset': [2.0, 14.0], 'scale': [0.4, 0.5], 'seed': 1},
    ]
    sprites = [
        {'type': 'tornado', 'at': 110, 'x': -26, 'scale': 46},
        {'type': 'barn', 'at': 30, 'x': 9, 'scale': 2.6},
    ]
    return road_scene(
        road,
        title='The storm chase - chasing a tornado down a straight road across the plains, lightning, wheat, a red barn',
        sky='storm',
        lights=[{'type': 'sun', 'azimuth': 228, 'elevation': 7, 'intensity': 0.7, 'color': [1.0, 0.78, 0.5]}],
        ambient=[0.42, 0.46, 0.44],
        fog={'color': [0.4, 0.44, 0.42], 'density': 0.004},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': -0.55, 'height': 0.72, 'fov': 64, 'pitch': 0.08},
        shots=[{'at': 2.0, 'x': -0.55, 'height': 0.72, 'fov': 64, 'pitch': 0.08, 'post': LOOK,
                'vehicle': {'type': 'pickup_truck', 'ahead': 2.6}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(storm_chase().save(os.path.join(HERE, 'storm_chase.json')))

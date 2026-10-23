"""The close encounter: a road scene (road.py) - pulled up on a desert road at night, a flying saucer hovering low
over the road ahead, its beam letting down onto the asphalt and a cow rising up it, a farm by the road.

Two lanes of old asphalt across the desert at night (`desert_wash` either side), telegraph poles and their wires,
saguaros; a `barn` and a few cows in their field to the right. The `flying_saucer` hangs over the road with its
lights lit and a green light of its own on everything under it; the `tractor_beam` comes down from it onto the
road, a `cow` floating up inside it. Your convertible with its headlights on (the shot's vehicle).
Run:  python close_encounter.py  -> writes close_encounter.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.4, 'spread': 0.6}]
BEAM = [0.6, 1.0, 0.75]


def close_encounter():
    road = {
        'sections': [[20, 0, 0], [40, 0.05, 0.4], [300, -0.03, 0.2]],
        'width': 2.2, 'lanes': 2, 'surface': 'asphalt', 'lines': False, 'centre': '#d8b040', 'rumble': False,
        'bands': 0.03,
        'ground': [{'width': 0.4, 'texture': 'gravel'}, {'texture': 'desert_wash'}],
        'walls': [{'side': 'left', 'offset': 1.4, 'z': 2.35, 'height': 0.5, 'texture': 'power_lines',
                   'tile': [9, 0.5]}],
        'distance': 300,
    }
    roadside = [
        {'type': 'telegraph_pole', 'side': 'left', 'every': 9, 'from': 0, 'offset': 1.4},
        {'type': 'saguaro', 'density': 0.04, 'offset': [2.0, 20.0], 'scale': [1.6, 2.6], 'seed': 1},
    ]
    sprites = [
        {'type': 'flying_saucer', 'at': 13, 'x': 0.2, 'z': 4.2, 'scale': 1.8,
         'light': {'color': BEAM, 'radius': 6.0, 'intensity': 1.6, 'z': 1.0}},
        {'type': 'tractor_beam', 'at': 13, 'x': 0.2, 'scale': 4.75},
        {'type': 'cow', 'at': 13, 'x': 0.2, 'z': 1.6, 'scale': 0.5, 'tint': [0.85, 1.0, 0.9]},
        {'type': 'barn', 'at': 24, 'x': 8.5, 'scale': 2.4},
        {'type': 'cow', 'at': 17, 'x': 4.5, 'scale': 0.45},
        {'type': 'cow', 'at': 19, 'x': 6.0, 'scale': 0.45, 'flip': True},
    ]
    return road_scene(
        road,
        title='The close encounter - pulled up on a desert road at night, a flying saucer over the road, a cow rising',
        sky='night',
        lights=[{'type': 'moon', 'azimuth': 300, 'elevation': 25, 'intensity': 0.3, 'disc': False}],
        ambient=[0.24, 0.26, 0.34],
        fog={'color': [0.1, 0.12, 0.18], 'density': 0.006},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': -0.55, 'height': 0.75, 'fov': 64, 'pitch': 0.16},
        shots=[{'at': 2.0, 'x': -0.55, 'height': 0.75, 'fov': 64, 'pitch': 0.16, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(close_encounter().save(os.path.join(HERE, 'close_encounter.json')))

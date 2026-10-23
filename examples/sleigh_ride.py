"""The sleigh ride: a road scene (road.py) on a winter night - riding a horse-drawn sleigh down the lane of a snowy
village, log cabins either side with their windows lit, firs strung with lights, lamps along the way, snow falling.

The lane is the road (`snow`, packed), deep snow either side; `log_cabin`s stand along both sides with their
windows lit and a warm light at each, `christmas_tree`s between them with their lights, `lamp_post`s, snowy pines
behind; the moon up, snow falling. Your sleigh's red dash and lamp and the horse before you, its harness hung with
bells (`sleigh_horse`, the shot's vehicle).
Run:  python sleigh_ride.py  -> writes sleigh_ride.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.4, 'spread': 0.5}, 'snow']
WARM = [1.0, 0.75, 0.45]
SNOW = {'base': 'snow', 'tint': [0.82, 0.86, 1.0]}


def sleigh_ride():
    road = {
        'sections': [[12, 0, 0], [30, 0.2, 0.3], [30, -0.25, -0.2], [200, 0.1, 0.1]],
        'width': 1.6, 'surface': SNOW, 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.2, 'blend': 0.5},
        'ground': SNOW,
        'distance': 200,
    }
    roadside = [
        {'type': 'log_cabin', 'side': 'both', 'every': 6, 'offset': 1.6, 'from': 4, 'scale': 1.9, 'seed': 1,
         'light': {'color': WARM, 'radius': 2.6, 'intensity': 1.1, 'z': 0.7}},
        {'type': 'christmas_tree', 'side': 'both', 'every': 6, 'offset': 0.7, 'from': 7, 'scale': 1.2,
         'light': {'color': [1.0, 0.8, 0.5], 'radius': 1.4, 'intensity': 0.7, 'z': 0.8}},
        {'type': 'lamp_post', 'side': 'left', 'every': 8, 'offset': 0.3, 'from': 5, 'scale': 0.9,
         'light': {'color': WARM, 'radius': 2.4, 'intensity': 1.0, 'z': 1.2}},
        {'type': 'snowy_pine', 'density': 0.4, 'offset': [5.0, 20.0], 'scale': [1.8, 3.0], 'seed': 2},
    ]
    return road_scene(
        road,
        title='The sleigh ride - by horse-drawn sleigh down the lane of a snowy village at night, windows lit',
        sky='night',
        sky_objects=[{'type': 'moon', 'azimuth': 278, 'elevation': 15, 'size': 2.6}],
        lights=[{'type': 'moon', 'azimuth': 280, 'elevation': 30, 'intensity': 0.35, 'disc': False}],
        ambient=[0.34, 0.38, 0.5],
        fog={'color': [0.16, 0.2, 0.3], 'density': 0.012},
        roadside=roadside,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 62, 'pitch': 0.08},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 62, 'pitch': 0.08, 'post': LOOK,
                'vehicle': {'type': 'sleigh_horse', 'ahead': 1.2, 'z': 0.14, 'scale': 0.6,
                            'light': {'color': WARM, 'radius': 1.6, 'intensity': 0.8, 'z': 0.5, 'at': -0.2}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(sleigh_ride().save(os.path.join(HERE, 'sleigh_ride.json')))

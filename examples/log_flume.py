"""The log flume: a road scene (road.py) at the fair - riding a log boat down a flume through a pine wood, at the lip
of the big drop, the wooden channel plunging away to the pool and its splash far below.

The flume is the road: running `water` between the channel's wooden sides (`walls` of `planks`, low), the
`sections` running level to the lip and then dropping steeply away down the hill to the pool; pines either side, a
fence, the fair's big wheel over the trees; your log's nose and its grab bar before you (`log_boat`, the shot's
vehicle), the camera pitched down the drop.
Run:  python log_flume.py  -> writes log_flume.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]


def log_flume():
    road = {
        'sections': [[3.2, 0, 0], [3, 0, -1.6], [10, 0.1, -7], [6, -0.2, -0.4], [200, 0.1, 0]],
        'width': 0.9, 'surface': {'base': 'water', 'tint': [0.7, 0.85, 0.9]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'ripple': 0.8,
        'ground': [{'width': 0.6, 'texture': 'pine_needles'}, {'texture': 'grass'}],
        'walls': [{'side': 'both', 'offset': 0.0, 'height': 0.35, 'texture': {'base': 'planks', 'tint': [0.8, 0.6, 0.45]},
                   'tile': [1.0, 0.35]}],
        'distance': 200,
    }
    roadside = [
        {'type': 'pine', 'density': 0.9, 'offset': [0.8, 10.0], 'scale': [1.8, 3.0], 'seed': 1},
    ]
    sprites = [
        {'type': 'surf', 'at': 22.5, 'x': 0.0, 'z': 0.0, 'scale': 1.2},
        {'type': 'ferris_wheel', 'at': 60, 'x': 14, 'z': -8, 'scale': 12},
    ]
    return road_scene(
        road,
        title='The log flume - at the lip of the big drop in a log boat, the flume plunging away to the pool below',
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 240, 'elevation': 40, 'intensity': 0.9}],
        ambient=[0.6, 0.62, 0.68],
        fog={'color': [0.78, 0.84, 0.92], 'density': 0.004, 'sky_mix': 0.2},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.6, 'x': 0.0, 'height': 0.45, 'fov': 66, 'pitch': -0.4},
        shots=[{'at': 2.6, 'x': 0.0, 'height': 0.45, 'fov': 66, 'pitch': -0.4, 'post': LOOK,
                'vehicle': {'type': 'log_boat', 'ahead': 0.7, 'z': -0.02, 'scale': 0.3}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(log_flume().save(os.path.join(HERE, 'log_flume.json')))

"""The cattle drive: a road scene (road.py) on the open range at sunset - riding with the herd across the prairie,
the cattle strung out ahead raising dust, cowboys riding alongside, the buttes red on the horizon.

No road but the trail the herd has beaten (`dirt`, ragged, blending into the grass); `dry_grass` to the horizon;
the `cow`s, tinted brown, scattered along and over the trail (a `roadside` row on the trail itself, `side` middle,
and more out on both sides), dust (`dust_cloud`, half see-through) rising behind them; `cowboy`s on `horse`s out
to the sides; a `mountains` skyline of red buttes, a `sunset` sky. Your horse's neck and ears before you
(`horse_neck`).
Run:  python cattle_drive.py  -> writes cattle_drive.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.2}]
RANGE = [0.86, 0.6, 0.42]                        # range cattle, brown and white


def cattle_drive():
    road = {
        'sections': [[20, 0, 0], [60, 0.08, 0.2], [300, -0.05, 0]],
        'width': 3.0, 'surface': 'dirt', 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.6, 'blend': 1.0},
        'ground': 'dry_grass',
        'distance': 300,
    }
    roadside = [
        {'type': 'cow', 'side': 'middle', 'density': 1.0, 'offset': [-1.4, 1.4], 'from': 3.5, 'to': 60,
         'scale': [0.5, 0.58], 'flip': True, 'tint': RANGE, 'seed': 1},
        {'type': 'cow', 'density': 0.4, 'offset': [0.0, 4.0], 'from': 4, 'to': 50, 'scale': [0.5, 0.58],
         'tint': RANGE, 'seed': 2},
        {'type': 'dust_cloud', 'side': 'middle', 'every': 6, 'offset': [-1.0, 1.0], 'from': 9, 'to': 60,
         'scale': [1.4, 2.2], 'opacity': 0.45, 'seed': 3},
    ]
    sprites = [
        {'type': 'horse', 'at': 9, 'x': -3.0},
        {'type': 'cowboy', 'at': 9, 'x': -3.0, 'z': 0.3, 'scale': 0.6},
        {'type': 'horse', 'at': 16, 'x': 3.6, 'flip': True},
        {'type': 'cowboy', 'at': 16, 'x': 3.6, 'z': 0.3, 'scale': 0.6, 'flip': True},
    ]
    return road_scene(
        road,
        title='The cattle drive - riding with the herd across the prairie at sunset, cowboys alongside, buttes red',
        sky='sunset',
        skyline={'type': 'mountains', 'height': 1.0, 'color': [0.62, 0.32, 0.26]},
        sky_objects=[{'type': 'sun', 'azimuth': 262, 'elevation': 4, 'size': 2.8}],
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 8, 'intensity': 0.9, 'color': [1.0, 0.72, 0.5],
                 'disc': False}],
        ambient=[0.6, 0.5, 0.48],
        fog={'color': [0.9, 0.66, 0.5], 'density': 0.006, 'sky_mix': 0.3},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'horse_neck', 'ahead': 0.7, 'z': 0.5, 'scale': 0.26}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(cattle_drive().save(os.path.join(HERE, 'cattle_drive.json')))

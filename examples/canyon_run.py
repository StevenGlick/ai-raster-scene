"""The canyon run: a road scene (road.py) - off the road, a dirt track through a red rock canyon, following a
rally car's dust.

The track is `dirt` with a `ragged` edge and two ruts worn down it (`tyre_marks` laid along it), bumping over the
canyon floor's rises, a shallow river beside it under the far wall, mirroring it. The canyon is `walls`: banded red rock either side with `ragged` rims, and higher, paler
walls behind them; boulders fallen at their feet and the desert's stones and scrub between (`scatter`). The sun
stands to the left, so the right-hand wall is in light and the left in shade. A rally car ahead throws up a
cloud of dust; you follow it in an open-top jeep. The second shot leans into a bend.
Run:  python canyon_run.py  -> writes canyon_run.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.0}]
WASH = {'base': 'desert_wash', 'tint': [1.05, 0.9, 0.8]}


def canyon_run():
    road = {
        'sections': [[10, 0, 0], [30, -0.6, 0.8], [26, 0.8, -0.6], [34, -0.5, 1.0], [30, 0.7, -0.2], [40, -0.4, -0.8],
                     [300, 0.3, 0.0]],
        'width': 2.2, 'surface': {'base': 'dirt', 'tint': [1.12, 0.86, 0.7]}, 'lines': False, 'rumble': False,
        'edge': {'ragged': 0.3, 'blend': 0.5},
        'ground': {'left': WASH, 'right': [{'width': 0.9, 'texture': WASH},              # a river under the far wall
                                           {'width': 2.3, 'texture': {'base': 'shallows', 'tint': [0.62, 0.78, 0.72]},
                                            'reflect': 0.45},
                                           {'texture': WASH}]},
        'walls': [
            {'side': 'left', 'offset': 3.0, 'height': 16, 'texture': 'slot_rock', 'tile': 6, 'ragged': 4, 'seed': 1},
            {'side': 'right', 'offset': 4.2, 'height': 13, 'texture': 'sandstone', 'tile': 5, 'ragged': 5, 'seed': 2},
            {'side': 'both', 'offset': 15, 'height': 34, 'texture': 'sandstone_pale', 'tile': 10, 'ragged': 9,
             'seed': 3},
        ],
        'bands': 0.04, 'distance': 260,
    }
    scatter = [
        {'of': ['rocks', 'boulder', 'rocks', 'boulder'], 'side': 'left', 'density': 0.9, 'offset': [2.0, 3.0],
         'sizes': ['medium', 'large', 'huge'], 'seed': 1},                  # fallen at the walls' feet
        {'of': ['rocks', 'boulder', 'rocks', 'boulder'], 'side': 'right', 'density': 0.9, 'offset': [3.0, 4.2],
         'sizes': ['medium', 'large', 'huge'], 'seed': 2},
        {'of': 'desert', 'side': 'left', 'density': 0.35, 'offset': [0.2, 3.0], 'seed': 3},
        {'of': 'desert', 'side': 'right', 'density': 0.35, 'offset': [0.1, 0.8], 'seed': 4},
    ]
    decals = [
        {'tex': 'tyre_marks', 'every': 3.6, 'offset': [-0.1, 0.1], 'size': 0.6, 'opacity': 0.55, 'seed': 1},
        {'tex': 'drifts', 'density': 0.05, 'size': [0.5, 1.0], 'seed': 2},
    ]
    sprites = [
        {'type': 'rally_car', 'at': 11, 'x': 0.6},
        {'type': 'dust_cloud', 'at': 10.4, 'x': 0.2, 'scale': 0.55, 'opacity': 0.7},     # its dust, low behind it
        {'type': 'dust_cloud', 'at': 9.9, 'x': 1.0, 'scale': 0.42, 'opacity': 0.55, 'flip': True},
        {'type': 'cow_skull', 'at': 7, 'x': -1.6},
    ]
    return road_scene(
        road,
        title='The canyon run - off the road through a red rock canyon, after a rally car\'s dust',
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 228, 'elevation': 48, 'intensity': 0.85}],
        ambient=[0.6, 0.52, 0.48],
        fog={'color': [0.86, 0.72, 0.58], 'density': 0.006},
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.1},
        shots=[
            {'at': 2.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.1, 'post': LOOK,
             'vehicle': {'type': 'jeep', 'ahead': 2.9}},
            {'at': 31.0, 'x': 0.1, 'height': 0.8, 'fov': 64, 'pitch': 0.08, 'roll': -7, 'yaw': -5, 'post': LOOK,
             'vehicle': {'type': 'jeep', 'ahead': 2.9}},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(canyon_run().save(os.path.join(HERE, 'canyon_run.json')))

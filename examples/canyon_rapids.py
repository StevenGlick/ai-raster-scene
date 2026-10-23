"""The canyon rapids: a road scene (road.py) by raft down white water - the river dropping through a red rock canyon,
foam over the rocks, boulders splitting the current, the walls rising sheer either side, a strip of blue sky above.

The river is the road (`river_water`, rough with `ripple`, hardly mirroring - `wet` 0.1), falling away in steps
(its sections drop); `foam` decals thick over it for the white water, `boulder`s in the stream (`side` middle) and
along its gravel banks; the canyon walls are the canyon run's (`slot_rock` and `sandstone`, ragged, and paler rock
behind). Your raft from its back seat, the two in front paddling (`raft_bow`, the shot's vehicle).
Run:  python canyon_rapids.py  -> writes canyon_rapids.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]


def canyon_rapids():
    road = {
        'sections': [[8, 0, -0.2], [30, 0.3, -0.5], [30, -0.35, -0.4], [200, 0.1, -0.1]],
        'width': 2.6, 'surface': {'base': 'river_water', 'tint': [0.8, 1.0, 1.0]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'ripple': 0.8, 'wet': 0.1,
        'ground': [{'width': 0.4, 'texture': 'gravel'}, {'texture': 'sand'}],
        'walls': [
            {'side': 'left', 'offset': 1.2, 'height': 16, 'texture': 'slot_rock', 'tile': 6, 'ragged': 4, 'seed': 1},
            {'side': 'right', 'offset': 1.6, 'height': 14, 'texture': 'sandstone', 'tile': 5, 'ragged': 5, 'seed': 2},
            {'side': 'both', 'offset': 10, 'height': 34, 'texture': 'sandstone_pale', 'tile': 10, 'ragged': 9,
             'seed': 3},
        ],
        'distance': 160,
    }
    roadside = [
        {'type': 'boulder', 'side': 'middle', 'density': 0.15, 'offset': [-1.1, 1.1], 'scale': [0.25, 0.55],
         'from': 4, 'seed': 1},
        {'type': 'boulder', 'density': 0.4, 'offset': [0.0, 1.0], 'scale': [0.3, 0.8], 'seed': 2},
    ]
    decals = [
        {'tex': 'foam', 'density': 2.6, 'size': [0.6, 1.6], 'side': 'road', 'seed': 1},
        {'tex': 'foam', 'density': 1.0, 'size': [1.2, 2.4], 'side': 'road', 'seed': 2},
    ]
    return road_scene(
        road,
        title='The canyon rapids - by raft down white water through a red rock canyon, foam over the rocks',
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 300, 'elevation': 55, 'intensity': 0.9}],
        ambient=[0.6, 0.56, 0.54],
        fog={'color': [0.86, 0.74, 0.62], 'density': 0.006},
        roadside=roadside,
        decals=decals,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 64, 'pitch': -0.02},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 64, 'pitch': -0.02, 'post': LOOK,
                'vehicle': {'type': 'raft_bow', 'ahead': 1.0, 'z': 0.12, 'scale': 0.28}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(canyon_rapids().save(os.path.join(HERE, 'canyon_rapids.json')))

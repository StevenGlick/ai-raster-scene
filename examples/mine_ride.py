"""The mine ride: a road scene (road.py) - riding a runaway mine cart down the rails through a gold mine, its
timber sets flashing past, lamps on them, gold in the rock.

The road is the track (`rail_track`: rails and sleepers in ballast); the tunnel is `walls` of rock with veins of
gold either side and a `ceiling` of rock, shored up by `mine_frame` timber sets down its `middle` every 2.2, a lamp
hung from each and a light with it. The `sections` run downhill and twist - a mine coaster - and crystals glow in
the rock here and there. You ride in a cart behind another, its ore heaped with gold.
Run:  python mine_ride.py  -> writes mine_ride.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 2.2, 'spread': 0.5}]
LAMP = [1.0, 0.72, 0.38]


def mine_ride():
    road = {
        'sections': [[10, 0, 0], [24, 0.6, -1.5], [20, -0.8, -2.0], [24, 0.7, -1.0], [20, -0.5, 0.6],
                     [200, 0.3, -1.0]],
        'width': 1.4, 'surface': 'rail_track', 'lines': False, 'rumble': False, 'bands': 0.02,
        'ground': [{'width': 0.25, 'texture': 'gravel'}, {'texture': 'rock_floor'}],
        'walls': [{'side': 'both', 'offset': 0.5, 'height': 3.0, 'texture': ['mine_rock', 'mine_rock_vein',
                                                                           'mine_rock_gold'],
                   'tile': 1.5, 'blocks': 3.0, 'seed': 1}],
        'ceiling': {'height': 2.6, 'texture': 'mine_rock', 'tile': 1.5, 'light': 0.3},
        'distance': 140,
    }
    roadside = [
        {'type': 'mine_frame', 'side': 'middle', 'every': 2.2, 'offset': 0.0, 'from': 1.0, 'scale': 2.6,
         'light': {'color': LAMP, 'radius': 3.2, 'intensity': 1.6, 'z': 1.8, 'x': 0.0}},
        {'type': 'crystal', 'density': 0.05, 'offset': [0.1, 0.4], 'scale': [0.3, 0.6], 'seed': 2,
         'light': {'color': [0.4, 0.8, 1.0], 'radius': 1.4, 'intensity': 0.7, 'z': 0.3}},
    ]
    scatter = [{'of': ['rocks', 'rocks', 'ore_heap'], 'density': 0.6, 'offset': [0.0, 0.45], 'sizes': ['tiny', 'small'],
                'seed': 3}]
    sprites = [{'type': 'pick_shovel', 'at': 19.5, 'x': -1.05}]
    return road_scene(
        road,
        title='The mine ride - a runaway mine cart down the rails through a gold mine',
        sky='night',
        ambient=[0.3, 0.26, 0.22],
        fog={'color': [0.1, 0.07, 0.05], 'density': 0.035},
        roadside=roadside,
        scatter=scatter,
        sprites=sprites,
        camera={'at': 15.0, 'x': 0.0, 'height': 0.6, 'fov': 66, 'pitch': 0.04},
        shots=[{'at': 15.0, 'x': 0.0, 'height': 0.6, 'fov': 66, 'pitch': 0.04, 'roll': 6, 'post': LOOK,
                'vehicle': {'type': 'mine_cart', 'ahead': 1.6, 'scale': 0.42}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(mine_ride().save(os.path.join(HERE, 'mine_ride.json')))

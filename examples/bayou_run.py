"""The bayou run: a road scene (road.py) on the water - poling a skiff down a bayou at dusk, bald cypresses hung
with moss closing in on both sides and doubled in the black water, fireflies, a shack on stilts with its window
lit.

The channel is the road (`swamp_water`, still); its banks `bog` and then the swamp's own water, the cypresses
standing in it by density hung with moss, their knees round their feet, the swamp's cards behind
(`swamp_card`s as a wall of trees far out). Cattails along the banks, a heron in the shallows, an alligator's back
in the channel, fireflies over the water; the `stilt_shack` round the bend with its window and lantern lit; your
skiff's bow and its lantern (`boat_bow`).
Run:  python bayou_run.py  -> writes bayou_run.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 2.2, 'spread': 0.5}]
LAMP = [1.0, 0.72, 0.4]


def bayou_run():
    road = {
        'sections': [[10, 0, 0], [30, 0.25, 0], [30, -0.3, 0], [200, 0.1, 0]],
        'width': 2.4, 'surface': 'swamp_water', 'lines': False, 'rumble': False, 'bands': 0.0, 'ripple': 0.3,
        'ground': [{'width': 0.5, 'texture': 'bog'}, {'texture': 'swamp_water'}],
        'distance': 160,
    }
    roadside = [
        {'type': 'bald_cypress', 'density': 0.5, 'offset': [0.6, 10.0], 'scale': [3.4, 4.8], 'seed': 1},
        {'type': 'cypress_knees', 'density': 0.8, 'offset': [0.2, 4.0], 'seed': 3},
        {'type': 'swamp_card_3', 'side': 'both', 'every': 4.0, 'offset': 12, 'scale': 4.0, 'seed': 4},
        {'type': 'fireflies', 'side': 'middle', 'density': 0.25, 'offset': [-1.4, 1.4], 'z': [0.3, 1.0], 'seed': 5},
    ]
    scatter = [{'of': 'swamp', 'density': 0.8, 'offset': [0.0, 1.2], 'seed': 2}]
    sprites = [
        {'type': 'stilt_shack', 'at': 15, 'x': 3.1, 'scale': 2.2,
         'light': {'color': LAMP, 'radius': 3.0, 'intensity': 1.1, 'z': 1.0}},
        {'type': 'heron', 'at': 9, 'x': -1.6, 'scale': 0.8},
        {'type': 'alligator', 'at': 12, 'x': 0.4, 'z': -0.05},
    ]
    return road_scene(
        road,
        title='The bayou run - poling a skiff down a bayou at dusk, cypresses hung with moss, a shack with its window lit',
        sky='dusk',
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 4, 'intensity': 0.5, 'color': [1.0, 0.6, 0.4]}],
        ambient=[0.36, 0.34, 0.4],
        fog={'color': [0.32, 0.28, 0.3], 'density': 0.03},
        roadside=roadside,
        scatter=scatter,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 62, 'pitch': 0.06},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 62, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'boat_bow', 'ahead': 1.25, 'z': -0.1, 'scale': 0.5,
                            'light': {'color': LAMP, 'radius': 2.4, 'intensity': 1.0, 'z': 0.5, 'at': 0.1}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(bayou_run().save(os.path.join(HERE, 'bayou_run.json')))

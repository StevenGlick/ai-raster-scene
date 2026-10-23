"""The kelp run: a road scene (road.py) under the sea - gliding a submarine low through a kelp forest, following a
little research sub, shafts of sunlight slanting down through the fronds, fish, a turtle, a shark, a wreck's mast.

There is no road but the sea floor (`seabed` for the road and the ground, its edge blended away); the water's
surface is a `ceiling` of `water_surface` far overhead, glowing, and the murk a close teal fog. `kelp` stands by
density either side, `light_shaft`s slant down (additive); the `seabed` scatter. The `mini_sub` noses on ahead
with its lamps, bubbles rising; a school of fish, a turtle, a reef shark; an anchor and a wreck's mast. Marine snow
drifting (the `snow` effect, faint and pale); your own viewport's brass rim round it all (`porthole`, the vehicle).
The road is drawn far (`distance` 300) under a dark sky: where the ceiling and the floor stop, a sliver of sky shows.
Run:  python kelp_run.py  -> writes kelp_run.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.4, 'spread': 0.5},
        {'fx': 'snow', 'color': [0.72, 0.86, 0.86], 'count': 110, 'opacity': 0.4}]        # marine snow
SEABED = {'base': 'seabed', 'tint': [0.8, 0.9, 0.9]}


def kelp_run():
    road = {
        'sections': [[10, 0, 0], [30, 0.2, 0.6], [30, -0.25, -0.4], [200, 0.1, 0.2]],
        'width': 2.0, 'surface': SEABED, 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.4, 'blend': 1.0},
        'ground': SEABED,
        'ceiling': {'height': 9.0, 'texture': 'water_surface', 'tile': 4.0, 'light': 0.7},
        'distance': 300,
    }
    roadside = [
        {'type': 'kelp', 'density': 0.9, 'offset': [0.3, 14.0], 'scale': [3.6, 6.0], 'seed': 1},
        {'type': 'light_shaft', 'side': 'middle', 'density': 0.1, 'offset': [-4.0, 4.0], 'scale': [7.0, 9.0],
         'seed': 3},
    ]
    scatter = [{'of': 'seabed', 'density': 0.5, 'offset': [0.0, 6.0], 'seed': 2}]
    sprites = [
        {'type': 'mini_sub', 'at': 6.0, 'x': 0.25, 'z': 0.7,
         'light': {'color': [1.0, 0.95, 0.8], 'radius': 2.6, 'intensity': 0.9, 'z': 0.7, 'at': 1.0}},
        {'type': 'bubbles', 'at': 5.6, 'x': 0.25, 'z': 1.0, 'scale': 0.8},
        {'type': 'fish_school', 'at': 4.5, 'x': -0.9, 'z': 1.1},
        {'type': 'sea_turtle', 'at': 7.5, 'x': 1.3, 'z': 1.5},
        {'type': 'reef_shark', 'at': 11, 'x': -0.7, 'z': 1.9},
        {'type': 'anchor', 'at': 10, 'x': -1.4},
        {'type': 'wreck_mast', 'at': 26, 'x': 3.2, 'scale': 4.0},
    ]
    return road_scene(
        road,
        title='The kelp run - gliding a submarine through a kelp forest, sunlight slanting down, a little sub ahead',
        sky='storm',
        ambient=[0.3, 0.5, 0.55],
        fog={'color': [0.05, 0.26, 0.32], 'density': 0.06},
        roadside=roadside,
        scatter=scatter,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.06},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'porthole', 'ahead': 0.8, 'z': 0.4, 'scale': 0.78}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(kelp_run().save(os.path.join(HERE, 'kelp_run.json')))

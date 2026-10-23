"""The dark road: a road scene (road.py) - an old paved road across a land of lava under a blood-red sky, a knight
walking it toward the dark castle on its crag at the road's end, braziers burning along the way.

The road is old paving with a ragged edge; either side black ash, then fields of lava - its crust cracked and
glowing (`lava_field`, emissive; the band's `tile` 8, so the cracks are big) - with dead trees standing black
against the sky, broken columns, robed statues and bones by the road, braziers every few units with their fire's light on the stones. A knight walks ahead (`view`
back); at the far end the `dark_castle` on its crag, an ash plume behind it. The `blood` sky, ash and embers
falling (`ashfall`).
Run:  python dark_road.py  -> writes dark_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = ['ashfall', {'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 2.2, 'spread': 0.5}]
FIRE = [1.0, 0.55, 0.22]


def dark_road():
    road = {
        'sections': [[14, 0, 0], [40, 0.25, 0.6], [40, -0.3, 1.0], [300, 0.08, 1.4]],
        'width': 2.2, 'surface': {'base': 'ruin_paving', 'tint': [0.7, 0.62, 0.6]}, 'lines': False, 'rumble': False,
        'edge': {'ragged': 0.15, 'blend': 0.35},
        'ground': [{'width': 2.5, 'texture': 'black_sand'}, {'texture': 'lava_field', 'tile': 8}],
        'bands': 0.03, 'distance': 260,
    }
    roadside = [
        {'type': 'brazier', 'every': 9, 'offset': 0.4, 'from': 4, 'scale': 0.6,
         'light': {'color': FIRE, 'radius': 3.4, 'intensity': 1.3, 'z': 0.6, 'x': 0.4}},
        {'type': 'dead_tree', 'density': 0.12, 'offset': [1.5, 12.0], 'scale': [2.2, 3.4],
         'tint': [0.12, 0.08, 0.08], 'seed': 1},
        {'type': ['broken_column', 'robed_statue', 'broken_column', 'stela'], 'density': 0.05, 'offset': [0.6, 3.0],
         'scale': [0.8, 1.6], 'tint': [0.55, 0.45, 0.45], 'seed': 2},
    ]
    scatter = [{'of': ['bones', 'rocks', 'rocks'], 'density': 0.3, 'offset': [0.0, 2.5], 'seed': 1}]
    decals = [{'tex': 'ruin', 'density': 0.06, 'size': [0.4, 0.9], 'seed': 1}]
    sprites = [
        {'type': 'knight', 'at': 7.0, 'x': 0.1, 'view': 'back'},
        {'type': 'dark_castle', 'at': 120, 'x': 4.0, 'z': -2.0, 'scale': 34},
        {'type': 'ash_plume', 'at': 160, 'x': 30, 'scale': 40, 'tint': [0.4, 0.3, 0.3]},
    ]
    return road_scene(
        road,
        title='The dark road - an old road across a land of lava toward the dark castle, a knight walking it',
        sky='blood',
        ambient=[0.42, 0.24, 0.22],
        fog={'color': [0.32, 0.1, 0.08], 'density': 0.004},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.04, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(dark_road().save(os.path.join(HERE, 'dark_road.json')))

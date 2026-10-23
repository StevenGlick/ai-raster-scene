"""The forest path: a road scene (road.py) that is not a road - a dirt path winding through a wood of spruce, oak
and birch on a misty morning, someone walking it ahead of you.

The path is a `road` with no lines and no rumble strip, its surface `dirt`, its edge `ragged` (it wanders) and
`blend`ed into the grass; the ground out from it a verge of grass, then the forest floor. The wood is `roadside`
rows scattered by `density` rather than set out `every` so far: trees well back, bushes and ferns at the path's
edge, now and then a stump. A deer stands off the path; a villager walks it ahead, seen from behind (`view` back).
The sun is low through the trees ahead and the morning's haze (`fog`) closes the far end of it.
Run:  python forest_path.py  -> writes forest_path.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 0.9, 'radius': 2.4, 'spread': 0.6},
        {'fx': 'grade', 'lift': [0.02, 0.025, 0.02]}]


def forest_path():
    road = {
        'sections': [[8, 0, 0], [30, 0.5, 0.4], [26, -0.7, -0.3], [34, 0.45, 0.8], [40, -0.35, -0.5], [120, 0.2, 0.0]],
        'width': 1.5, 'surface': 'dirt', 'lines': False, 'rumble': False,
        'edge': {'ragged': 0.16, 'blend': 0.35},
        'ground': [{'width': 0.9, 'texture': 'grass'}, {'width': 2.5, 'texture': 'moss'},
                   {'texture': 'pine_needles'}],
        'bands': 0.04, 'distance': 160,
    }
    roadside = [
        {'type': ['pine', 'pine', 'tree', 'birch'], 'density': 1.1, 'offset': [1.2, 7.0], 'scale': [2.6, 4.4],
         'clear': 0.5, 'seed': 3},
        {'type': ['pine', 'tree', 'pine'], 'density': 0.9, 'offset': [7.0, 16.0], 'scale': [3.0, 4.8], 'seed': 4},
        {'type': ['bush', 'fern', 'fern', 'grass_tuft'], 'density': 1.4, 'offset': [0.0, 2.0], 'scale': [0.3, 0.6],
         'seed': 5},
        {'type': ['stump', 'rocks', 'mushrooms'], 'density': 0.12, 'offset': [0.3, 3.0], 'seed': 6},
    ]
    sprites = [
        {'type': 'villager', 'at': 9.0, 'x': 0.15, 'view': 'back', 'id': 'walker'},
        {'type': 'deer', 'at': 21.0, 'x': -2.6},
    ]
    return road_scene(
        road,
        title='The forest path - a dirt path through a wood on a misty morning',
        sky='dawn',
        skyline='treeline',
        lights=[{'type': 'sun', 'azimuth': 274, 'elevation': 9, 'intensity': 0.7, 'color': [1.0, 0.86, 0.62]}],
        ambient=[0.5, 0.52, 0.48],
        fog={'color': [0.78, 0.8, 0.74], 'density': 0.035},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': -0.1, 'height': 0.52, 'fov': 62, 'pitch': 0.04},
        shots=[
            {'at': 1.0, 'x': -0.1, 'height': 0.52, 'fov': 62, 'pitch': 0.04, 'post': LOOK},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(forest_path().save(os.path.join(HERE, 'forest_path.json')))

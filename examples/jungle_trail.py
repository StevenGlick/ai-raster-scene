"""The jungle trail: a road scene (road.py) - a muddy trail into the jungle, an explorer going on ahead of you
toward a ruined gateway.

The trail is a `road` of `mud`, `ragged` and `blend`ed into the jungle floor, no lines, no rumble strip. Kapoks
tower over it and palms, banana plants and tree ferns crowd it (`roadside` rows by `density`), monstera, ferns and
heliconias at its edges. Ahead a stone arch stands over the trail, a great stone head beside it, and the explorer
walks toward it, seen from behind. Humid air (a green `fog`) closes the far end; the sun is high.
Run:  python jungle_trail.py  -> writes jungle_trail.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 0.8, 'radius': 2.4, 'spread': 0.6},
        {'fx': 'grade', 'saturation': 1.1, 'lift': [0.01, 0.02, 0.0]}]


def jungle_trail():
    road = {
        'sections': [[10, 0, 0], [26, -0.55, 0.5], [30, 0.6, 0.6], [30, -0.4, -0.3], [120, 0.25, 0.4]],
        'width': 1.7, 'surface': 'mud', 'lines': False, 'rumble': False,
        'edge': {'ragged': 0.22, 'blend': 0.45},
        'ground': 'jungle_floor', 'bands': 0.05, 'distance': 140,
    }
    roadside = [
        {'type': 'kapok', 'density': 0.12, 'offset': [2.5, 9.0], 'scale': [6.0, 8.0], 'from': 9, 'seed': 1},
        {'type': ['palm', 'tree_fern', 'banana_plant', 'tree_fern'], 'density': 1.0, 'offset': [0.8, 7.0],
         'scale': [1.6, 3.2], 'seed': 2},
        {'type': ['palm', 'kapok', 'tree_fern'], 'density': 0.6, 'offset': [7.0, 15.0], 'scale': [3.0, 6.0], 'seed': 3},
        {'type': ['monstera', 'fern', 'heliconia', 'fern', 'monstera'], 'density': 1.8, 'offset': [0.0, 2.2],
         'scale': [0.4, 1.0], 'seed': 4},
    ]
    sprites = [
        {'type': 'explorer', 'at': 8.0, 'x': 0.1, 'view': 'back', 'id': 'explorer'},
        {'type': 'stone_arch', 'at': 17.0, 'x': 0.0, 'scale': 3.2},
        {'type': 'stone_head', 'at': 15.5, 'x': -2.0},
    ]
    return road_scene(
        road,
        title='The jungle trail - a muddy trail toward a ruined gateway',
        sky='day',
        skyline='jungle',
        lights=[{'type': 'sun', 'azimuth': 250, 'elevation': 55, 'intensity': 0.75, 'disc': False}],
        ambient=[0.42, 0.48, 0.4],
        fog={'color': [0.55, 0.66, 0.5], 'density': 0.03},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.52, 'fov': 62, 'pitch': 0.02},
        shots=[
            {'at': 1.0, 'x': 0.0, 'height': 0.52, 'fov': 62, 'pitch': 0.02, 'post': LOOK},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(jungle_trail().save(os.path.join(HERE, 'jungle_trail.json')))

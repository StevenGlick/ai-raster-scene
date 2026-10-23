"""The volcano road: a road scene (road.py) - racing a rally car down a jungle road at night under an erupting
volcano, fire fountaining from its crater, rivers of lava down its flanks, the ash cloud lit red from below, lava
crossing the fields by the road.

A dirt road through the jungle at night; either side `jungle_floor` and then, out in the fields, the lava come
down from the mountain (`lava_flow`, glowing, its band's `tile` 4); palms and jungle trees black against the glow.
The `erupting_volcano` fills the far end of the road with an `ash_plume` over it and a red light on everything,
`fireball`s arcing through the sky; a rally car ahead, your jeep after it.
Run:  python volcano_road.py  -> writes volcano_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.6, 'spread': 0.6}, 'ashfall']
FIRE = [1.0, 0.45, 0.2]


def volcano_road():
    road = {
        'sections': [[12, 0, 0], [40, 0.2, 0.6], [40, -0.25, -0.4], [300, 0.05, 0.4]],
        'width': 1.8, 'surface': {'base': 'dirt', 'tint': [0.7, 0.55, 0.45]}, 'lines': False, 'rumble': False,
        'bands': 0.02, 'edge': {'ragged': 0.25, 'blend': 0.4},
        'ground': {'left': [{'width': 4.0, 'texture': 'jungle_floor'}, {'width': 6, 'texture': 'lava_flow', 'tile': 4},
                            {'texture': 'jungle_floor'}],
                   'right': [{'width': 7.0, 'texture': 'jungle_floor'}, {'width': 5, 'texture': 'lava_flow', 'tile': 4},
                             {'texture': 'jungle_floor'}]},
        'distance': 300,
    }
    roadside = [
        {'type': ['palm', 'kapok', 'palm'], 'density': 0.25, 'offset': [0.8, 3.6], 'scale': [2.4, 3.6],
         'tint': [0.35, 0.3, 0.3], 'seed': 1},
        {'type': 'palm', 'density': 0.05, 'offset': [10.0, 30.0], 'scale': [2.6, 3.4], 'tint': [0.3, 0.25, 0.25],
         'seed': 2},
    ]
    sprites = [
        {'type': 'erupting_volcano', 'at': 150, 'x': -8, 'z': -3, 'scale': 56,
         'light': {'color': FIRE, 'radius': 60, 'intensity': 1.2, 'z': 30}},
        {'type': 'ash_plume', 'at': 170, 'x': -10, 'z': 44, 'scale': 50, 'tint': [0.5, 0.32, 0.3]},
        {'type': 'fireball', 'at': 90, 'x': -26, 'z': 22, 'scale': 2.0},
        {'type': 'fireball', 'at': 80, 'x': 12, 'z': 16, 'scale': 1.6},
        {'type': 'fireball', 'at': 110, 'x': 4, 'z': 30, 'scale': 2.4},
        {'type': 'rally_car', 'at': 9.0, 'x': 0.5},
    ]
    return road_scene(
        road,
        title='The volcano road - racing down a jungle road at night under an erupting volcano, lava in the fields',
        sky='blood',
        ambient=[0.3, 0.2, 0.2],
        fog={'color': [0.3, 0.12, 0.1], 'density': 0.006},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.16},
        shots=[{'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.16, 'post': LOOK,
                'vehicle': {'type': 'jeep', 'ahead': 2.6, 'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(volcano_road().save(os.path.join(HERE, 'volcano_road.json')))

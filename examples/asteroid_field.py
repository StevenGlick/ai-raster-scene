"""The asteroid field: a road scene (road.py) in deep space - flying a starfighter through an asteroid field,
rocks tumbling at every height and distance, two wingmen ahead, a ringed planet huge beyond them, the sun hard on
one side of everything.

The course is the road, too narrow to see; the ground is `void` both sides and the `space` sky runs on below the
horizon. `asteroid`s (three colours and shapes by `variant`) fill the space round the course at every `z`, a few
big ones placed near; two `starfighter`s ahead as wingmen; a `ringed` planet in the sky; a hard sun from the side
and almost no ambient light, so the rocks' far sides go black. Your own starfighter from behind.
Run:  python asteroid_field.py  -> writes asteroid_field.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.8, 'radius': 2.2}]


def asteroid_field():
    road = {
        'sections': [[400, 0.04, 0.02]],
        'width': 0.002, 'surface': 'asphalt', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': 'void',
        'distance': 400,
    }
    roadside = [
        {'type': 'asteroid', 'side': 'middle', 'density': 0.25, 'offset': [-12.0, 12.0], 'z': [-10.0, 10.0],
         'scale': [0.6, 3.0], 'from': 8, 'seed': 1},
        {'type': 'asteroid', 'density': 0.2, 'offset': [2.0, 40.0], 'z': [-20.0, 20.0], 'scale': [1.0, 6.0],
         'seed': 2},
    ]
    sprites = [
        {'type': 'asteroid', 'variant': 1, 'at': 9, 'x': -4.5, 'z': 1.5, 'scale': 3.2},
        {'type': 'asteroid', 'variant': 2, 'at': 14, 'x': 5.0, 'z': -1.0, 'scale': 4.0, 'flip': True},
        {'type': 'asteroid', 'variant': 0, 'at': 6, 'x': 2.4, 'z': 2.2, 'scale': 1.1},
        {'type': 'starfighter', 'at': 8, 'x': -2.0, 'z': 1.0, 'scale': 0.4},
        {'type': 'starfighter', 'at': 10, 'x': 2.2, 'z': 0.5, 'scale': 0.4},
    ]
    return road_scene(
        road,
        title='The asteroid field - flying a starfighter through tumbling rocks, wingmen ahead, a ringed planet',
        sky='space',
        sky_objects=[{'type': 'ringed', 'azimuth': 262, 'elevation': 6, 'size': 16, 'color': [0.76, 0.6, 0.5]}],
        lights=[{'type': 'sun', 'azimuth': 330, 'elevation': 20, 'intensity': 1.1, 'color': [1.0, 0.96, 0.9],
                 'disc': False}],
        ambient=[0.16, 0.16, 0.2],
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.9, 'fov': 66, 'pitch': 0.04},
        shots=[{'at': 2.0, 'x': 0.0, 'height': 0.9, 'fov': 66, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'starfighter', 'ahead': 2.2, 'z': 0.35, 'scale': 0.4}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(asteroid_field().save(os.path.join(HERE, 'asteroid_field.json')))

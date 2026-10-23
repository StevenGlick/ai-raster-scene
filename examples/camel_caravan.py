"""The camel caravan: a road scene (road.py) - riding a camel in a caravan over the dunes at sunset, the camels
strung out ahead, the pyramids on the horizon, the sun going down.

There is no road but the caravan's track: `sand` for the track and the ground, its edges ragged and blended, the
`sections` rising and falling over the swells; the dunes beyond are the `hills` skyline in the sand's colour (walls
with a `ragged` top came out as jagged rock). The camels walk on ahead in a line, each with its rider, and you ride
a little to one side of it; two pyramids on the horizon; your own camel's neck and head before you (`camel_head`, the shot's vehicle). The `sunset` sky.
Run:  python camel_caravan.py  -> writes camel_caravan.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.2}]
SAND = {'base': 'sand', 'tint': [1.0, 0.88, 0.7]}


def camel_caravan():
    road = {
        'sections': [[8, 0, 0.3], [30, 0.12, 1.6], [30, -0.15, -1.8], [40, 0.1, 1.2], [300, -0.05, -0.5]],
        'width': 1.0, 'surface': SAND, 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.4, 'blend': 0.8},
        'ground': SAND,
        'distance': 300,
    }
    camels = [{'type': 'camel', 'at': a, 'x': x} for a, x in ((4.0, 0.05), (7.2, -0.08), (10.5, 0.06), (13.6, -0.04),
                                                             (16.8, 0.05))]
    sprites = camels + [
        {'type': 'pyramid', 'at': 160, 'x': -28, 'scale': 26},
        {'type': 'pyramid', 'at': 190, 'x': 6, 'scale': 18},
    ]
    return road_scene(
        road,
        title='The camel caravan - riding in a caravan over the dunes at sunset, the pyramids on the horizon',
        sky='sunset',
        skyline={'type': 'hills', 'height': 1.4, 'color': [0.62, 0.38, 0.26]},
        sky_objects=[{'type': 'sun', 'azimuth': 274, 'elevation': 5, 'size': 3.2}],
        lights=[{'type': 'sun', 'azimuth': 274, 'elevation': 6, 'intensity': 0.9, 'color': [1.0, 0.72, 0.46],
                 'disc': False}],
        ambient=[0.56, 0.44, 0.44],
        fog={'color': [0.9, 0.62, 0.5], 'density': 0.004, 'sky_mix': 0.3},
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.45, 'height': 0.85, 'fov': 62, 'pitch': 0.02},
        shots=[{'at': 1.0, 'x': 0.45, 'height': 0.85, 'fov': 62, 'pitch': 0.02, 'post': LOOK,
                'vehicle': {'type': 'camel_head', 'ahead': 1.0, 'z': 0.38, 'scale': 0.34}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(camel_caravan().save(os.path.join(HERE, 'camel_caravan.json')))

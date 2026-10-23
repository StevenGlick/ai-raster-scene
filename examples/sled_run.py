"""The sled run: a road scene (road.py) in the north - driving a dog sled down a trail through snowy pines at dusk,
the aurora overhead, a log cabin's windows lit ahead.

The trail is the road (`snow`, packed into runners' ruts, its edge blended into the drifts); deep `snow` either
side, `snowy_pine`s by density, the `snow` scatter; a `log_cabin` by the trail with its windows lit and a warm
light, its chimney's smoke. The `aurora` sky. You ride the sled's runners, its team of huskies running on ahead of you (`dog_team`).
Run:  python sled_run.py  -> writes sled_run.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.2, 'spread': 0.5}]
SNOW = {'base': 'snow', 'tint': [0.86, 0.9, 1.0]}


def sled_run():
    road = {
        'sections': [[10, 0, 0], [30, 0.3, -0.6], [30, -0.35, 0.4], [200, 0.15, -0.3]],
        'width': 1.0, 'surface': SNOW, 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.2, 'blend': 0.6},
        'ground': SNOW,
        'distance': 200,
    }
    roadside = [
        {'type': 'snowy_pine', 'density': 1.2, 'offset': [0.6, 14.0], 'scale': [1.6, 3.2], 'seed': 1},
    ]
    scatter = [{'of': 'snow', 'density': 0.4, 'offset': [0.2, 4.0], 'seed': 2}]
    decals = [{'tex': 'tyre_marks', 'density': 0.3, 'size': [0.6, 1.0], 'seed': 1}]                 # the runners' ruts
    sprites = [
        {'type': 'log_cabin', 'at': 16, 'x': 2.6, 'scale': 1.8,
         'light': {'color': [1.0, 0.75, 0.45], 'radius': 3.0, 'intensity': 1.0, 'z': 0.8, 'x': -0.5}},
        {'type': 'steam', 'at': 16.2, 'x': 3.0, 'z': 1.9, 'scale': 1.2, 'opacity': 0.4},
        {'type': 'dog_team', 'at': 2.7, 'x': 0.0, 'scale': 0.55},
    ]
    return road_scene(
        road,
        title='The sled run - driving a dog sled down a trail through snowy pines under the aurora, a cabin lit ahead',
        sky='aurora',
        lights=[{'type': 'moon', 'azimuth': 250, 'elevation': 20, 'intensity': 0.35, 'disc': False}],
        ambient=[0.36, 0.42, 0.52],
        fog={'color': [0.12, 0.2, 0.26], 'density': 0.012},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 62, 'pitch': 0.08},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 62, 'pitch': 0.08, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(sled_run().save(os.path.join(HERE, 'sled_run.json')))

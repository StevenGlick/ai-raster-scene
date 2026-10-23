"""The ski run: a road scene (road.py) on skis - down a groomed run on a bright day, slalom gates down the course,
a skier ahead, the chairlift going up beside it, the peaks all round.

The run is the road: `piste` (groomed corduroy) falling away in steep `sections` that bend, the deep snow either
side beyond the orange safety net (`walls` of `ski_fence`, see-through). Snowy pines stand by density; the
chairlift runs up the right-hand side - two `chairlift` walls high on the `lift_tower`s, riders on the chairs.
Red and blue `slalom_gate`s turn and turn about down the course, a `skier` or two ahead; your own `ski_tips` before
you (a shot's `vehicle`), the camera pitched down the slope; the `mountains` skyline in pale blue, a little haze.
Run:  python ski_run.py  -> writes ski_run.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]


def ski_run():
    road = {
        'sections': [[4, 0, -1.2], [26, 0.3, -9], [24, -0.35, -8], [30, 0.25, -10], [40, -0.1, -6], [60, 0, -1], [300, 0.05, 30]],
        'width': 4.0, 'surface': {'base': 'piste', 'tint': [0.9, 0.94, 1.0]}, 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.2, 'blend': 0.5},
        'ground': [{'width': 1.6, 'texture': 'snow'}, {'texture': 'snow_forest', 'tile': 3}],
        'walls': [
            {'side': 'both', 'offset': 0.3, 'height': 0.45, 'texture': 'ski_fence', 'tile': [1.2, 0.45]},
            {'side': 'right', 'offset': 4.0, 'z': 1.45, 'height': 1.6, 'texture': 'chairlift', 'tile': [4, 1.6]},
            {'side': 'right', 'offset': 5.5, 'z': 1.45, 'height': 1.6, 'texture': 'chairlift', 'tile': [4.6, 1.6]},
        ],
        'distance': 400,
    }
    roadside = [
        {'type': 'snowy_pine', 'density': 1.6, 'offset': [0.9, 5.0], 'scale': [1.2, 2.4], 'seed': 1},
        {'type': ['snowy_pine', 'pine'], 'density': 0.9, 'offset': [5.0, 14.0], 'scale': [1.8, 3.0], 'seed': 3},
        {'type': 'lift_tower', 'side': 'right', 'every': 12, 'offset': 4.75, 'from': 6},
    ]
    scatter = [{'of': 'snow', 'density': 0.4, 'offset': [0.6, 6.0], 'seed': 2}]
    gates = [{'type': 'slalom_gate', 'at': 5 + 6 * i, 'x': 0.9 if i % 2 else -0.9, 'variant': i % 2}
             for i in range(14)]
    sprites = gates + [
        {'type': 'skier', 'at': 7.5, 'x': 0.35},
        {'type': 'skier', 'at': 22, 'x': -0.6, 'tint': [0.5, 0.7, 1.2]},
    ]
    return road_scene(
        road,
        title='The ski run - down a groomed run on a bright day, slalom gates, a skier ahead, the chairlift beside it',
        sky='day',
        skyline={'type': 'mountains', 'height': 1.6, 'color': [0.78, 0.84, 0.94]},
        lights=[{'type': 'sun', 'azimuth': 238, 'elevation': 32, 'intensity': 0.9, 'color': [1.0, 0.97, 0.92]}],
        ambient=[0.66, 0.7, 0.8],
        fog={'color': [0.86, 0.9, 0.98], 'density': 0.004, 'sky_mix': 0.2},
        roadside=roadside,
        scatter=scatter,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 66, 'pitch': -0.25},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 66, 'pitch': -0.25, 'post': LOOK,
                'vehicle': {'type': 'ski_tips', 'ahead': 0.85, 'z': 0.3, 'scale': 0.24}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(ski_run().save(os.path.join(HERE, 'ski_run.json')))

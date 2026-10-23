"""The grand prix: a road scene (road.py) - on the grid at the start of a race, the five red lights lit over the
track, the field ahead of you, the grandstands full.

A wide track of asphalt, its kerbs striped red and white (`rumble`), a white line along each edge, the `start_line`
painted across it and the grid boxes ahead; behind the kerbs a strip of grass, then a `jersey_barrier` wall
topped by catch fencing (`chainlink`) on the left, tyre stacks on the right, and `grandstand`s rising behind both
(walls of the crowd, tier on tier). The `start_lights` hang over the track; the field waits on the grid in two
columns - `race_car`s in four liveries - and you are on the back row in your own (the shot's `vehicle`). The
second shot is from the side of the track, the lights and the field down the straight.
Run:  python grand_prix.py  -> writes grand_prix.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.0, 'spread': 0.4}]
W = 5.0


def grand_prix():
    road = {
        'sections': [[60, 0, 0], [60, 0.3, 0.6], [300, -0.2, 0]],
        'width': W, 'lanes': 1, 'lines': False, 'edges': '#ececec', 'surface': 'asphalt',
        'rumble': {'width': 0.4, 'colors': ['#ececec', '#d02a24']}, 'stripe': 1,
        'ground': [{'width': 1.2, 'texture': 'grass'}, {'texture': 'concrete'}],
        'walls': [
            {'side': 'left', 'offset': 1.3, 'height': 0.3, 'texture': 'jersey_barrier', 'tile': [1.3, 0.3]},
            {'side': 'left', 'offset': 1.32, 'z': 0.3, 'height': 1.0, 'texture': 'chainlink', 'tile': 1.0},
            {'side': 'both', 'offset': 3.0, 'height': 3.0, 'texture': 'grandstand', 'tile': [2.0, 3.0],
             'to': 90},
            {'side': 'both', 'offset': 3.2, 'z': 3.0, 'height': 0.5, 'texture': 'corrugated', 'tile': 1.0,
             'to': 90},                                                     # the stands' roof edge
        ],
        'bands': 0.04, 'distance': 260,
    }
    roadside = [
        {'type': 'tyre_stack', 'side': 'right', 'every': 0.55, 'offset': 1.0, 'from': 2},
        {'type': 'banner', 'side': 'both', 'every': 12, 'offset': 2.6, 'from': 6, 'scale': 1.4},
    ]
    grid = []
    for k in range(6):                                              # two columns, staggered
        x = -0.9 if k % 2 == 0 else 0.9
        grid.append({'type': 'race_car', 'at': 6.0 + k * 2.2 + (0 if k % 2 == 0 else 1.1), 'x': x,
                     'variant': [0, 1, 3, 2, 1, 0][k]})
    decals = [{'tex': 'start_line', 'at': 19.6, 'x': 0, 'size': W},
              {'tex': 'tyre_marks', 'every': 2.2, 'from': 4, 'to': 20, 'offset': [-0.95, -0.85], 'size': 0.6,
               'opacity': 0.5, 'seed': 1},
              {'tex': 'tyre_marks', 'every': 2.2, 'from': 5, 'to': 21, 'offset': [0.85, 0.95], 'size': 0.6,
               'opacity': 0.5, 'seed': 2}]
    sprites = grid + [{'type': 'start_lights', 'at': 20.5, 'x': 0, 'scale': 3.4}]
    return road_scene(
        road,
        title='The grand prix - on the grid, the five red lights lit, the grandstands full',
        sky='day',
        skyline='hills',
        lights=[{'type': 'sun', 'azimuth': 240, 'elevation': 45, 'intensity': 0.85}],
        ambient=[0.62, 0.62, 0.66],
        fog={'color': [0.78, 0.82, 0.9], 'density': 0.003},
        roadside=roadside,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.9, 'height': 0.55, 'fov': 62, 'pitch': 0.1},
        shots=[
            {'at': 1.0, 'x': 0.9, 'height': 0.55, 'fov': 62, 'pitch': 0.1, 'post': LOOK,
             'vehicle': {'type': 'race_car', 'ahead': 2.2, 'variant': 1}},
            {'at': 4.0, 'x': -3.6, 'height': 1.6, 'fov': 52, 'pitch': 0.0, 'yaw': 14, 'post': LOOK},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(grand_prix().save(os.path.join(HERE, 'grand_prix.json')))

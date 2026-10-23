"""The coast road: a road scene (road.py) - the arcade racer's road along a coast at sunset, driven from behind
the wheel of a red convertible.

The road is `sections` of bends and rises; three lanes with a rumble strip red and white either side. Palms stand
along it (`roadside` rows), with billboards on the land side and the beach and the sea on the other (`ground` in
bands out from the road's edge). Cars seen from behind are on the road ahead (`sprites` placed by `at` and `x`),
a chevron sign stands before the first bend, and a checkpoint banner hangs across the road on the crest. The sun
is low over the road ahead; the shot's `vehicle` is your car, a racer's time, score and speed over it (`counter`s).
The second shot leans into the bend (`roll`), your car level under the tilted world as an arcade racer draws it.
Run:  python coast_road.py  -> writes coast_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LANE = 4.2 / 3                             # three lanes across a road 4.2 wide
GLOW = [{'fx': 'bloom', 'source': 'light', 'strength': 1.0, 'radius': 2.0, 'spread': 0.5}]
HUD = [{'type': 'counter', 'value': '58', 'label': 'TIME', 'at': 'top', 'margin': 16,      # an arcade racer's
        'color': [255, 220, 76]},
       {'type': 'counter', 'value': '1086420', 'label': 'SCORE', 'at': 'top-left', 'margin': 16, 'scale': 1},
       {'type': 'counter', 'value': '293 km/h', 'at': 'bottom-right', 'scale': 1, 'color': [255, 128, 76]}]


def coast_road():
    road = {
        'sections': [[14, 0, 0], [60, -0.55, 1.2], [50, 0.7, -1.4], [70, -0.45, 2.4], [110, 0.3, -1.0],
                     [120, 0, 0]],
        'width': 4.2, 'lanes': 3, 'surface': 'asphalt',
        'rumble': {'width': 0.32, 'colors': ['#ececec', '#c83024']},
        'ground': {'left': 'beach_sand', 'right': [{'width': 5, 'texture': 'beach_sand'},
                                                   {'width': 1.5, 'texture': 'wet_sand'}, {'texture': 'ocean'}]},
    }
    roadside = [
        {'type': ['palm', 'palm_lean'], 'every': 7, 'offset': 1.0, 'scale': [3.0, 3.8], 'flip': True},
        {'type': 'billboard', 'every': 45, 'side': 'left', 'offset': 3.5, 'from': 25, 'scale': 2.6},
    ]
    scatter = [                                     # the beach's flotsam, and tufts of dune grass by the road
        {'of': 'beach', 'side': 'left', 'density': 0.22, 'offset': [0.4, 6.0], 'seed': 1},
        {'of': 'beach', 'side': 'right', 'density': 0.12, 'offset': [1.0, 5.0], 'seed': 2},
        {'of': ['dry_tuft', 'dry_tuft', 'grass_tuft'], 'density': 0.7, 'offset': [0.0, 1.4], 'seed': 3},
    ]
    decals = [                                      # sand blown over the kerbs, a worn road, a skid into the bend
        {'tex': 'sand_drift', 'density': 0.05, 'offset': [-2.1, -1.2], 'size': [0.8, 1.6], 'seed': 1},
        {'tex': 'sand_drift', 'density': 0.05, 'offset': [1.2, 2.1], 'size': [0.8, 1.6], 'seed': 2},
        {'tex': 'wear', 'density': 0.03, 'size': [0.5, 1.0], 'opacity': 0.8, 'seed': 3},
        {'tex': 'tyre_marks', 'at': 9.5, 'x': 0.5, 'size': 0.55, 'opacity': 0.8},
    ]
    sprites = [
        {'type': 'car_compact', 'at': 15, 'x': -LANE},
        {'type': 'car_sedan', 'at': 31, 'x': LANE},
        {'type': 'box_truck', 'at': 46, 'x': 0.0},
        {'type': 'car_compact', 'at': 70, 'x': LANE, 'tint': [1.2, 0.85, 0.5]},
        {'type': 'curve_sign', 'at': 12, 'x': 3.4},
        {'type': 'checkpoint', 'at': 24, 'x': 0.0, 'scale': 2.9},
    ]
    return road_scene(
        road,
        title='The coast road - an arcade racer\'s road along the sea at sunset',
        sky='sunset',
        skyline='islands',
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 6, 'intensity': 0.6, 'color': [1.0, 0.76, 0.5],
                 'disc_size': 6}],
        ambient=[0.74, 0.66, 0.64],
        fog={'color': [0.92, 0.66, 0.5], 'density': 0.0035},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[
            {'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'post': GLOW,
             'vehicle': {'type': 'sports_car', 'ahead': 2.6}, 'overlays': HUD},
            {'at': 18.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'yaw': -4, 'roll': -6, 'post': GLOW,
             'vehicle': {'type': 'sports_car', 'ahead': 2.6}},          # under the checkpoint, leaning into the bend
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(coast_road().save(os.path.join(HERE, 'coast_road.json')))

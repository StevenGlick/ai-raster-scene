"""The autumn lane road: a road scene (road.py) - a narrow country lane between high hedges in autumn, leaves on
it, a little car pottering along ahead (`autumn_lane` is another lane, walked, in the raycaster).

The lane is one track of old asphalt, its edges ragged and grass creeping onto them; along both
sides the hedges are `walls` of `hedge` with a `ragged` top, and over them the trees of the hedgerow - oaks and
birches turned for the fall - stand by density. Leaves lie on the lane (`decals`: `leaf_litter`, the `fall` set),
fallen leaves and tufts gather along the hedges' feet (`scatter`). A low sun through the trees ahead, a light haze.
Run:  python autumn_lane_road.py  -> writes autumn_lane_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.0}]


def autumn_lane_road():
    road = {
        'sections': [[10, 0, 0], [24, 0.6, 0.6], [24, -0.7, -0.3], [30, 0.5, 0.8], [200, -0.3, 0]],
        'width': 1.8, 'surface': {'base': 'asphalt', 'tint': [0.95, 0.92, 0.88]}, 'lines': False, 'rumble': False,
        'edge': {'ragged': 0.1, 'blend': 0.25},
        'ground': [{'width': 0.35, 'texture': 'dry_grass'}, {'texture': 'leaves_fallen'}],
        'walls': [{'side': 'both', 'offset': 0.35, 'height': 1.5, 'texture': 'hedge', 'tile': 1.2, 'ragged': 0.25,
                   'seed': 1}],
        'bands': 0.03, 'distance': 160,
    }
    roadside = [
        {'type': ['tree_autumn', 'tree_autumn', 'birch_autumn'], 'density': 0.35, 'offset': [0.7, 2.2],
         'scale': [2.8, 3.8], 'clear': 1.0, 'seed': 1},
    ]
    scatter = [{'of': ['grass_tuft', 'dry_tuft', 'mushrooms'], 'density': 1.4, 'offset': [0.0, 0.35],
                'sizes': ['tiny', 'small'], 'seed': 1}]
    decals = [{'tex': 'fall', 'density': 0.5, 'size': [0.3, 0.7], 'seed': 1},
              {'tex': 'leaf_litter', 'side': 'both', 'density': 0.8, 'offset': [0.0, 0.35], 'size': [0.3, 0.5],
               'seed': 2}]
    sprites = [{'type': 'car_compact', 'at': 12, 'x': 0.0, 'variant': 3}]
    return road_scene(
        road,
        title='The autumn lane - a narrow country lane between high hedges in autumn, leaves on it',
        sky='golden',
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 10, 'intensity': 0.8, 'color': [1.0, 0.82, 0.58]}],
        ambient=[0.56, 0.5, 0.44],
        fog={'color': [0.86, 0.74, 0.58], 'density': 0.02},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.62, 'fov': 62, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.62, 'fov': 62, 'pitch': 0.04, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(autumn_lane_road().save(os.path.join(HERE, 'autumn_lane_road.json')))

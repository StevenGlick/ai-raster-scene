"""The pilgrims' path: a road scene (road.py) on foot - walking a stony path high in the mountains, strings of prayer
flags across it lifting in the wind, white stupas beside it, a monk walking on ahead, the snow peaks all round.

The path is the road (`gravel`, its edges ragged into the turf); thin turf either side (`dry_grass`), then scree
(`rock_floor`) with patches of `snow`. `prayer_flags` are strung across the path every few units and a `stupa`
stands by it now and then; stones and boulders scatter the slopes; a `monk` walks ahead; `snow_peak`s stand round
the valley, the `mountains` skyline behind them, the high sky deep blue.
Run:  python pilgrim_path.py  -> writes pilgrim_path.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]


def pilgrim_path():
    road = {
        'sections': [[10, 0, 0.3], [30, 0.25, 1.6], [30, -0.3, 1.2], [200, 0.1, 2.0]],
        'width': 1.2, 'surface': {'base': 'gravel', 'tint': [0.85, 0.8, 0.74]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'edge': {'ragged': 0.2, 'blend': 0.4},
        'ground': [{'width': 2.0, 'texture': {'base': 'dry_grass', 'tint': [0.66, 0.64, 0.5]}},
                   {'width': 6.0, 'texture': 'rock_floor'}, {'texture': 'snow'}],
        'distance': 300,
    }
    roadside = [
        {'type': 'prayer_flags', 'side': 'middle', 'every': 6, 'offset': 0.0, 'from': 3, 'z': 1.4, 'scale': 0.6},
        {'type': 'stupa', 'side': 'left', 'every': 18, 'offset': 1.0, 'from': 9, 'scale': 1.6},
        {'type': ['rocks', 'boulder', 'rocks'], 'density': 0.3, 'offset': [0.3, 8.0], 'scale': [0.2, 0.8],
         'seed': 2},
    ]
    sprites = [
        {'type': 'monk', 'at': 6.5, 'x': 0.15, 'view': 'back'},
        {'type': 'snow_peak', 'at': 240, 'x': -80, 'z': -2, 'scale': 48},
        {'type': 'snow_peak', 'at': 300, 'x': 20, 'z': -2, 'scale': 62},
        {'type': 'snow_peak', 'at': 220, 'x': 110, 'z': -2, 'scale': 44},
    ]
    return road_scene(
        road,
        title="The pilgrims' path - walking a mountain path under prayer flags, white stupas, the snow peaks all round",
        sky='day',
        skyline={'type': 'mountains', 'height': 1.6, 'color': [0.62, 0.68, 0.82]},
        lights=[{'type': 'sun', 'azimuth': 230, 'elevation': 40, 'intensity': 1.0, 'color': [1.0, 0.98, 0.94]}],
        ambient=[0.62, 0.66, 0.76],
        fog={'color': [0.78, 0.84, 0.94], 'density': 0.002, 'sky_mix': 0.2},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': -0.1, 'height': 0.55, 'fov': 62, 'pitch': 0.08},
        shots=[{'at': 1.0, 'x': -0.1, 'height': 0.55, 'fov': 62, 'pitch': 0.08, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(pilgrim_path().save(os.path.join(HERE, 'pilgrim_path.json')))

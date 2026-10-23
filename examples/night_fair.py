"""The night fair: a road scene (road.py) on foot - walking the midway of a travelling fair at night, stalls lit
along both sides under strings of lanterns, the big wheel turning ahead, a carousel glowing, the crowd out.

The midway is the road (trampled `dirt`), grass worn thin either side. Stalls stand along it (`market_stall`,
`food_cart`, `fruit_stall`, `gadget_stall` - each with a warm light), `lantern_span`s strung across overhead with
their lights, balloons; the `ferris_wheel` rises ahead to the right with its bulbs lit, the `carousel` glows to the
left; the crowd gathers along the stalls (`crowd` scatter). A night sky.
Run:  python night_fair.py  -> writes night_fair.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.4, 'spread': 0.6}]
WARM = [1.0, 0.75, 0.42]


def night_fair():
    road = {
        'sections': [[12, 0, 0], [40, 0.08, 0.2], [200, -0.05, 0]],
        'width': 2.6, 'surface': {'base': 'dirt', 'tint': [0.8, 0.7, 0.6]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'edge': {'ragged': 0.3, 'blend': 0.6},
        'ground': [{'width': 2.5, 'texture': {'base': 'grass', 'tint': [0.8, 0.85, 0.7]}}, {'texture': 'grass'}],
        'distance': 160,
    }
    stall = {'side': 'both', 'every': 3.2, 'offset': 0.5, 'from': 2.5, 'seed': 3,
             'light': {'color': WARM, 'radius': 2.4, 'intensity': 1.0, 'z': 1.0}}
    roadside = [
        dict(stall, type=['market_stall', 'food_cart', 'fruit_stall', 'gadget_stall']),
        {'type': 'lantern_span', 'side': 'middle', 'every': 14, 'offset': 0.0, 'from': 9, 'z': 3.0, 'scale': 4.2,
         'light': {'color': [1.0, 0.5, 0.35], 'radius': 3.0, 'intensity': 0.8, 'z': 2.3}},
        {'type': 'balloon', 'side': 'both', 'density': 0.15, 'offset': [0.2, 1.5], 'z': [1.4, 2.6],
         'scale': [0.25, 0.35], 'seed': 4},
    ]
    scatter = [{'of': 'crowd', 'side': 'both', 'density': 0.25, 'offset': [-0.6, 0.3], 'sizes': ['medium'],
                'clump': 0.3, 'seed': 2, 'clear': 4}]
    sprites = [
        {'type': 'ferris_wheel', 'at': 28, 'x': 5.5, 'scale': 9,
         'light': {'color': WARM, 'radius': 6.0, 'intensity': 1.0, 'z': 4.0}},
        {'type': 'carousel', 'at': 14, 'x': -4.6, 'scale': 2.4,
         'light': {'color': WARM, 'radius': 4.0, 'intensity': 1.2, 'z': 1.2}},
    ]
    return road_scene(
        road,
        title='The night fair - walking the midway at night, stalls lit under strings of lanterns, the big wheel ahead',
        sky='night',
        ambient=[0.22, 0.2, 0.28],
        fog={'color': [0.12, 0.1, 0.16], 'density': 0.012},
        roadside=roadside,
        scatter=scatter,
        sprites=sprites,
        camera={'at': 1.0, 'x': -0.3, 'height': 0.55, 'fov': 64, 'pitch': 0.14},
        shots=[{'at': 1.0, 'x': -0.3, 'height': 0.55, 'fov': 64, 'pitch': 0.14, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(night_fair().save(os.path.join(HERE, 'night_fair.json')))

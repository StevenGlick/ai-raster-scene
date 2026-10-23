"""The high seas: a road scene (road.py) on the water - from the bow of a sailing ship running before the wind
across a tropical sea at golden hour, a galleon ahead, a stone fort on its rock off the port bow, islands on
the horizon.

The sea is the road and the ground (`sea`, rippling, mirroring the low sun); the `islands` skyline far off; the
`galleon` sails on ahead with its stern windows lit and a light of its own; the `sea_fort` stands on its rock to
the left, a palm or two on a sandbar to the right; gulls. Your own ship's bow, its rail, bowsprit and jib round the
view (`bowsprit`, the shot's vehicle).
Run:  python high_seas.py  -> writes high_seas.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.2}]


def high_seas():
    road = {
        'sections': [[20, 0, 0], [60, 0.06, 0], [400, -0.04, 0]],
        'width': 3.0, 'surface': 'sea', 'lines': False, 'rumble': False, 'bands': 0.0, 'ripple': 0.8,
        'ground': 'sea',
        'distance': 400,
    }
    sprites = [
        {'type': 'galleon', 'at': 24, 'x': -1.5, 'z': -0.25,
         'light': {'color': [1.0, 0.75, 0.45], 'radius': 2.5, 'intensity': 0.7, 'z': 1.2}},
        {'type': 'sea_fort', 'at': 70, 'x': -24, 'z': -0.4, 'scale': 5.0},
        {'type': 'palm', 'at': 46, 'x': 9, 'scale': 2.6},
        {'type': 'palm', 'at': 47, 'x': 10.2, 'scale': 2.2, 'flip': True},
        {'type': 'seagull', 'at': 9, 'x': 1.4, 'z': 1.8, 'scale': 0.3},
        {'type': 'seagull', 'at': 11, 'x': 0.6, 'z': 2.2, 'scale': 0.25, 'flip': True},
    ]
    return road_scene(
        road,
        title='The high seas - from the bow of a sailing ship at golden hour, a galleon ahead, a fort on its rock',
        sky='golden',
        skyline={'type': 'islands', 'height': 1.0},
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 9, 'intensity': 0.85, 'color': [1.0, 0.82, 0.58]}],
        ambient=[0.58, 0.56, 0.56],
        fog={'color': [0.92, 0.82, 0.68], 'density': 0.003, 'sky_mix': 0.3},
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.9, 'fov': 64, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.9, 'fov': 64, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'bowsprit', 'ahead': 1.2, 'z': 0.34, 'scale': 0.75}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(high_seas().save(os.path.join(HERE, 'high_seas.json')))

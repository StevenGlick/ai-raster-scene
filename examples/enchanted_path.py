"""The enchanted path: a road scene (road.py) for a fairy tale - a cobbled path at night through a wood that glows,
under two moons, a witch walking it ahead of you.

The path is a `road` of `cobble` with no lines and no rumble strip, its edge `blend`ed into a verge of glowing moss
(`lumen_floor`), then dark moss. The wood is `roadside` rows by `density`: glowing ferns, bromeliads, monsteras and
crystals at the path's edge, tree ferns and heliconias lit from inside behind them, dark spruces at the back, giant
mushrooms that glow and light the path (a `light` on each), and wisps (`orb`s, added light) drifting over it at
heights between two (`z` as a range). The sky is the night with a big moon and a small one (`sky_objects`); a
cold `fog`, fireflies in the post.
Run:  python enchanted_path.py  -> writes enchanted_path.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

TEAL = [0.35, 1.0, 0.8]
LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.5, 'radius': 2.6, 'spread': 0.6},
        {'fx': 'fireflies', 'count': 16, 'size': 0.6},
        {'fx': 'grade', 'saturation': 1.1}]


def enchanted_path():
    road = {
        'sections': [[8, 0, 0], [30, 0.45, 0.5], [30, -0.6, -0.4], [40, 0.35, 0.9], [100, -0.2, 0.0]],
        'width': 1.6, 'surface': 'cobble', 'lines': False, 'rumble': False,
        'edge': {'ragged': 0.1, 'blend': 0.35},
        'ground': [{'width': 0.9, 'texture': 'lumen_floor'}, {'texture': 'moss'}],
        'bands': 0.03, 'distance': 140,
    }
    roadside = [
        {'type': ['glow_fern', 'glow_bromeliad', 'glow_fern', 'crystal', 'glow_monstera'], 'density': 1.6,
         'offset': [0.0, 2.2], 'scale': [0.3, 0.9], 'seed': 1},
        {'type': ['glow_tree_fern', 'glow_heliconia', 'glow_tree_fern'], 'density': 0.7, 'offset': [1.2, 7.0],
         'scale': [1.6, 3.2], 'seed': 2},
        {'type': ['pine', 'dead_tree', 'pine'], 'density': 0.9, 'offset': [5.0, 14.0], 'scale': [3.0, 5.0],
         'tint': [0.28, 0.32, 0.5], 'seed': 3},
        {'type': 'glowshroom', 'every': 8, 'offset': [0.5, 1.6], 'scale': [0.7, 1.2], 'jitter': 2.0, 'from': 5,
         'light': {'color': TEAL, 'radius': 2.4, 'intensity': 0.8, 'z': 0.5, 'x': 0.4}, 'seed': 4},
        {'type': 'orb', 'side': 'middle', 'density': 0.35, 'offset': [-3.0, 3.0], 'z': [0.4, 1.1],
         'scale': [0.08, 0.14], 'blend': 'additive', 'tint': [0.6, 1.0, 0.85], 'seed': 5},
    ]
    scatter = [{'of': ['mushrooms', 'mushrooms', 'glowshroom', 'glow_fern'], 'density': 0.5, 'offset': [0.0, 1.2],
                'sizes': ['tiny', 'small'], 'seed': 1}]
    decals = [                                      # moss between the cobbles, and now and then a rune, glowing
        {'tex': 'moss_patch', 'density': 0.2, 'size': [0.3, 0.6], 'seed': 1},
        {'tex': 'rune_mark', 'every': 11, 'from': 4, 'offset': [-0.4, 0.4], 'size': 0.4, 'opacity': 0.8,
         'tint': [0.3, 1.0, 0.85], 'seed': 2},
    ]
    sprites = [{'type': 'witch', 'at': 7.5, 'x': 0.1, 'view': 'back', 'id': 'witch',
                'light': {'color': [1.0, 0.78, 0.5], 'radius': 2.2, 'intensity': 0.7, 'z': 0.7}}]   # her lantern
    return road_scene(
        road,
        title='The enchanted path - a cobbled path through a glowing wood under two moons',
        sky='night',
        sky_objects=[{'type': 'moon', 'azimuth': 262, 'elevation': 13, 'size': 5.0, 'color': [0.86, 0.9, 1.0]},
                     {'type': 'moon', 'azimuth': 281, 'elevation': 19, 'size': 2.0, 'color': [1.0, 0.82, 0.7],
                      'phase': 0.4}],
        lights=[{'type': 'moon', 'azimuth': 262, 'elevation': 20, 'intensity': 0.3, 'disc': False}],
        ambient=[0.12, 0.13, 0.22],
        fog={'color': [0.06, 0.09, 0.18], 'density': 0.045},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 62, 'pitch': 0.03},
        shots=[
            {'at': 1.0, 'x': 0.0, 'height': 0.5, 'fov': 62, 'pitch': 0.03, 'post': LOOK},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(enchanted_path().save(os.path.join(HERE, 'enchanted_path.json')))

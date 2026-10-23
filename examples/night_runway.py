"""The night runway: a road scene (road.py) - from the cockpit, lined up on a runway at nightfall, its edge lights
running away in two rows to the horizon, the airliner ahead just lifting off, the tower lit beside the field.

The runway is the road: wide grey concrete, a dashed centre line, white edges, the threshold's bars at your feet
(`zebra_crossing`); `runway_light`s every 1.5 down both edges (white), down the middle (small) and along the
taxiway out to the right (blue), red across the far end. The airliner lifts off ahead, its lights lit; the
`control_tower` and the terminal's lit windows (a low wall of `tower_windows`) off to the right; the city's
glow on the horizon under the last of the dusk. Your own cockpit around the view (`cockpit`, the shot's
vehicle).
Run:  python night_runway.py  -> writes night_runway.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.2, 'spread': 0.5}]
WHITE_L, BLUE_L, RED_L = [1.0, 0.95, 0.85], [0.35, 0.55, 1.0], [1.0, 0.2, 0.15]


def night_runway():
    road = {
        'sections': [[600, 0, 0]],
        'width': 6.0, 'lanes': 2, 'surface': {'base': 'concrete', 'tint': [0.55, 0.56, 0.6]}, 'lines': '#d8d8d8',
        'edges': '#d8d8d8', 'rumble': False, 'bands': 0.0, 'stripe': 4,
        'ground': {'base': 'grass', 'tint': [0.5, 0.6, 0.5]},
        'walls': [{'side': 'right', 'offset': 26, 'from': 30, 'to': 150, 'height': 1.4,
                   'texture': 'tower_windows', 'tile': [1.4, 1.4]}],                  # the terminal
        'distance': 600,
    }
    edge = {'type': 'runway_light', 'side': 'both', 'every': 1.5, 'offset': 0.2, 'tint': WHITE_L}
    roadside = [
        edge,
        dict(edge, side='middle', offset=0.0, every=1.0, scale=0.035, from_=0),
        {'type': 'runway_light', 'side': 'right', 'every': 2.0, 'offset': 6.0, 'tint': BLUE_L},
    ]
    roadside[1]['from'] = roadside[1].pop('from_')
    ends = [{'type': 'runway_light', 'at': 300, 'x': x, 'tint': RED_L} for x in range(-3, 4)]
    sprites = ends + [
        {'type': 'airliner', 'at': 26, 'x': 0.0, 'z': 1.0, 'scale': 2.6,
         'light': {'color': [1.0, 0.95, 0.85], 'radius': 4.0, 'intensity': 0.8, 'z': 0.0}},
        {'type': 'control_tower', 'at': 55, 'x': 16, 'scale': 8},
    ]
    decals = [{'tex': 'zebra_crossing', 'at': 3.0, 'x': 0, 'size': 6.0}]
    return road_scene(
        road,
        title='The night runway - from the cockpit on a runway at nightfall, its lights to the horizon, an airliner lifting off',
        sky='dusk',
        skyline={'type': 'city', 'height': 0.6},
        ambient=[0.32, 0.3, 0.38],
        fog={'color': [0.3, 0.24, 0.32], 'density': 0.005},
        roadside=roadside,
        sprites=sprites,
        decals=decals,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.9, 'fov': 64, 'pitch': 0.02},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.9, 'fov': 64, 'pitch': 0.02, 'post': LOOK,
                'vehicle': {'type': 'cockpit', 'ahead': 0.9, 'z': 0.36, 'scale': 1.04}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(night_runway().save(os.path.join(HERE, 'night_runway.json')))

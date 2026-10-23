"""The ghost train: a road scene (road.py) - riding a ghost train through its haunted house, the track twisting
through dark rooms of old wallpaper, portraits and candelabras, a skeleton leaping out, a ghost drifting over the
rails, bats overhead.

The track is the road (`rail_track`, narrow) on a floor of dark boards; the rooms are `walls` of `wallpaper` and
`wallpaper_green` in `blocks`, one room after another, under a low `ceiling` of panelling - indoors all the way, so
only the ride's own lights show: candelabras burning, jack-o'-lanterns grinning, a sickly green light on the
skeleton and the ghost. Portraits hang on the walls, cobwebs in the corners, a grandfather clock; your car's front
with its skull and the lap bar (`ghost_car`, the shot's vehicle).
Run:  python ghost_train.py  -> writes ghost_train.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.5, 'radius': 2.2, 'spread': 0.5}]
CANDLE, GHOUL = [1.0, 0.66, 0.34], [0.4, 1.0, 0.5]


def ghost_train():
    road = {
        'sections': [[4, 0, 0], [10, 0.9, 0], [8, -1.1, 0.3], [12, 0.8, -0.3], [100, -0.4, 0]],
        'width': 1.0, 'surface': 'rail_track', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': {'base': 'planks', 'tint': [0.45, 0.38, 0.36]},
        'walls': [{'side': 'both', 'offset': 0.9, 'height': 2.2, 'texture': ['wallpaper', 'wallpaper_green'],
                   'tile': [1.4, 1.4], 'blocks': 3.0, 'seed': 2}],
        'ceiling': {'height': 2.2, 'texture': 'wood_panel', 'tile': 1.5, 'light': 0.0},
        'distance': 60,
    }
    roadside = [
        {'type': 'portrait', 'side': 'both', 'every': 4.5, 'offset': 0.85, 'z': 0.9, 'from': 2.5},
        {'type': 'candelabra', 'side': 'both', 'every': 6, 'offset': 0.6, 'from': 4, 'scale': 0.7,
         'light': {'color': CANDLE, 'radius': 2.2, 'intensity': 1.1, 'z': 0.9, 'x': 0.3}},
        {'type': 'cobweb', 'side': 'both', 'every': 3.5, 'offset': 0.85, 'z': 1.4, 'from': 2, 'scale': 0.7},
        {'type': 'jack_o_lantern', 'side': 'both', 'every': 7, 'offset': 0.4, 'from': 6.5, 'scale': 0.35,
         'light': {'color': [1.0, 0.55, 0.2], 'radius': 1.4, 'intensity': 0.9, 'z': 0.2}},
    ]
    sprites = [
        {'type': 'skeleton', 'at': 5.0, 'x': 0.55, 'z': 0.15, 'scale': 0.75,
         'light': {'color': GHOUL, 'radius': 1.8, 'intensity': 1.2, 'z': 0.6, 'x': -0.2}},
        {'type': 'ghost', 'at': 9.5, 'x': -0.2, 'z': 0.35, 'opacity': 0.75,
         'light': {'color': GHOUL, 'radius': 2.0, 'intensity': 0.8, 'z': 0.8}},
        {'type': 'bats', 'at': 7, 'x': 0.2, 'z': 1.5, 'scale': 0.5},
        {'type': 'grandfather_clock', 'at': 13, 'x': -0.75},
    ]
    return road_scene(
        road,
        title='The ghost train - riding a ghost train through its haunted house, a skeleton leaping out, a ghost ahead',
        sky='night',
        ambient=[0.16, 0.12, 0.2],
        fog={'color': [0.04, 0.02, 0.06], 'density': 0.08},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 66, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 66, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'ghost_car', 'ahead': 0.9, 'z': 0.1, 'scale': 0.32,
                            'light': {'color': [0.8, 0.55, 1.0], 'radius': 1.3, 'intensity': 0.9, 'z': 0.5, 'at': -0.3}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(ghost_train().save(os.path.join(HERE, 'ghost_train.json')))

"""The metro ride: a road scene (road.py) underground - from the driver's cab of a metro train running out of its
tunnel into the next station, the platforms lit white either side and people waiting on them, a signal by the
track.

The track is the road (`rail_track`) in a tunnel: `walls` of `tunnel_cables` either side under a low `ceiling` of
`concrete` (indoors, only the lamps' light); at the station the walls are `metro_tiles` set back behind the
platforms' faces (a low wall of `concrete`), lamps hang from its ceiling and the crowd waits on the platform. Wall
lamps along the tunnel, a `signal_light`, your own cab round the view (`metro_cab`, the shot's vehicle) - the
camera at the station's mouth: from deeper in the tunnel its walls hide the platforms.
Run:  python metro_ride.py  -> writes metro_ride.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 2.2, 'spread': 0.5}]
LAMP = [1.0, 0.9, 0.75]
ST0, ST1 = 11, 23                                  # the station, along the line


def metro_ride():
    road = {
        'sections': [[5, 0, 0], [8, 0.3, 0], [200, 0, 0]],
        'width': 1.4, 'surface': 'rail_track', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': {'base': 'concrete', 'tint': [0.5, 0.5, 0.5]},
        'walls': [
            {'side': 'both', 'offset': 0.3, 'height': 2.0, 'texture': 'tunnel_cables', 'tile': [2.0, 2.0], 'to': ST0},
            {'side': 'both', 'offset': 0.3, 'height': 2.0, 'texture': 'tunnel_cables', 'tile': [2.0, 2.0], 'from': ST1},
            {'side': 'both', 'offset': 0.2, 'height': 0.42, 'texture': 'concrete', 'tile': 1.0, 'from': ST0,
             'to': ST1},                                                          # the platforms' faces
            {'side': 'both', 'offset': 2.4, 'height': 2.2, 'texture': 'metro_tiles', 'tile': [1.6, 1.6],
             'from': ST0, 'to': ST1},                                             # the station's walls
        ],
        'ceiling': {'height': 2.2, 'texture': {'base': 'concrete', 'tint': [0.6, 0.6, 0.6]}, 'tile': 2.0,
                    'light': 0.0},
        'distance': 120,
    }
    roadside = [
        {'type': 'wall_lamp', 'side': 'both', 'every': 3.5, 'offset': 0.28, 'z': 1.4, 'to': ST0,
         'light': {'color': LAMP, 'radius': 2.8, 'intensity': 1.3, 'z': 1.4, 'x': 0.2}},
        {'type': 'ceiling_lamp', 'side': 'both', 'every': 2.5, 'offset': 1.0, 'z': 1.6, 'from': ST0, 'to': ST1,
         'light': {'color': [0.95, 0.97, 1.0], 'radius': 3.6, 'intensity': 1.6, 'z': 1.6}},
        {'type': 'crowd', 'side': 'both', 'density': 0.4, 'offset': [0.5, 2.0], 'z': 0.42, 'from': ST0 + 1,
         'to': ST1 - 1, 'scale': [0.55, 0.65], 'seed': 2},
    ]
    sprites = [{'type': 'signal_light', 'at': 14, 'x': -1.0, 'z': 1.0, 'variant': 1}]
    return road_scene(
        road,
        title='The metro ride - from the cab of a metro train through its tunnel, the next station lit ahead',
        sky='night',
        ambient=[0.26, 0.26, 0.28],
        fog={'color': [0.05, 0.05, 0.06], 'density': 0.012},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 9.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.04},
        shots=[{'at': 9.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.04, 'post': LOOK,
                'vehicle': {'type': 'metro_cab', 'ahead': 0.6, 'z': 0.5, 'scale': 0.5, 'headlights': True,
                            'light': {'color': [0.7, 0.8, 1.0], 'radius': 1.2, 'intensity': 0.6, 'z': 0.6, 'at': -0.3}}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(metro_ride().save(os.path.join(HERE, 'metro_ride.json')))

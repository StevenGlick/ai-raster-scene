"""The fjord voyage: a road scene (road.py) by longship up a fjord on a misty morning - the dragon prow ahead of you,
shields along the rails, sheer cliffs rising either side with waterfalls pouring down them, pines on the ledges,
snow on the peaks, gulls over the still dark water.

The fjord is the road (`water` tinted cold, a slow `ripple`), a narrow strip of `rock_wet` at the cliffs' feet; the
cliffs are `cliff_face` walls, ragged and very tall, close either side, more behind; `island_falls` down them,
`snowy_pine`s and `pine`s on the ledges (`z` spread up the cliffs); a `mountains` skyline in snow; mist (`fog`). Your
longship's deck and prow before you (`longship_bow`, the shot's vehicle).
Run:  python fjord_voyage.py  -> writes fjord_voyage.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.2}]


def fjord_voyage():
    road = {
        'sections': [[20, 0, 0], [60, 0.15, 0], [60, -0.2, 0], [300, 0.06, 0]],
        'width': 9.0, 'surface': {'base': 'water', 'tint': [0.6, 0.72, 0.8]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'ripple': 0.3,
        'ground': [{'width': 0.5, 'texture': 'rock_wet'}, {'texture': 'rock'}],
        'walls': [
            {'side': 'both', 'offset': 1.0, 'height': 26, 'texture': 'cliff_face', 'tile': 6, 'ragged': 10, 'seed': 1},
            {'side': 'both', 'offset': 16, 'height': 60, 'texture': 'cliff_face', 'tile': 12, 'ragged': 20, 'seed': 2},
        ],
        'distance': 260,
    }
    roadside = [
        {'type': ['snowy_pine', 'pine', 'pine'], 'density': 0.25, 'offset': [0.7, 0.95], 'z': [2.0, 20.0],
         'scale': [1.2, 2.4], 'seed': 1},
    ]
    sprites = [
        {'type': 'island_falls', 'at': 18, 'x': -5.4, 'scale': 22},                  # falls down the cliffs
        {'type': 'island_falls', 'at': 32, 'x': 5.4, 'scale': 24},
        {'type': 'island_falls', 'at': 56, 'x': -5.4, 'scale': 24},
        {'type': 'seagull', 'at': 9, 'x': -1.0, 'z': 2.0, 'scale': 0.3},
        {'type': 'seagull', 'at': 12, 'x': 1.5, 'z': 2.6, 'scale': 0.28, 'flip': True},
    ]
    return road_scene(
        road,
        title='The fjord voyage - by longship up a fjord on a misty morning, waterfalls pouring down the cliffs',
        sky='dawn',
        skyline={'type': 'mountains', 'height': 1.6, 'color': [0.84, 0.86, 0.9]},
        lights=[{'type': 'sun', 'azimuth': 268, 'elevation': 14, 'intensity': 0.8, 'color': [1.0, 0.84, 0.66]}],
        ambient=[0.6, 0.64, 0.7],
        fog={'color': [0.9, 0.82, 0.76], 'density': 0.018},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.7, 'fov': 64, 'pitch': 0.1},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.7, 'fov': 64, 'pitch': 0.1, 'post': LOOK,
                'vehicle': {'type': 'longship_bow', 'ahead': 0.8, 'z': 0.38, 'scale': 0.28}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(fjord_voyage().save(os.path.join(HERE, 'fjord_voyage.json')))

"""The roller coaster: a road scene (road.py) - riding a roller coaster, at the top of the lift hill with the big
drop falling away below you, the park far down beneath the track.

The road is the track: `coaster_track` is rails and ties and nothing else (a see-through surface), so the sky and
the park show through it; `ground` `void` either side, and far `below` the park's lawns and paths, then fields. The
`sections` are the ride - out of the station, up the lift hill (a long steep `rise`), over the crest and down the
drop, round a banked curve at its foot and over a camel back - and the steel frame under the track is `walls` of
`coaster_frame` standing from it down into the ground (the land below hides what is under it). You ride in the
second car, the front car ahead of you, its riders' arms up. The second shot is in the curve at the drop's foot.
Run:  python roller_coaster.py  -> writes roller_coaster.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.0}]
CAR = {'type': 'coaster_car', 'ahead': 1.25, 'scale': 0.5}
FRONT = {'type': 'coaster_car', 'ahead': 1.7, 'scale': 0.44}


def roller_coaster():
    road = {
        'sections': [[8, 0, 0], [30, 0, 22], [4, 0, 0.4], [20, 0.15, -22], [22, 0.9, 1.0], [16, -0.7, 7],
                     [14, 0.2, -6], [160, 0.4, 0]],
        'width': 1.4, 'surface': 'coaster_track', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': 'void',
        'below': {'depth': 2.5, 'tile': 33, 'haze': 0.6,
                  'texture': [{'width': 24, 'texture': 'city_park'}, {'width': 30, 'texture': 'pasture'},
                              {'texture': 'farmland'}]},
        'walls': [{'side': 'both', 'offset': -0.12, 'z': -60, 'height': 59.9, 'texture': 'coaster_frame',
                   'tile': [3.0, 3.0], 'from': 8}],                         # the frame, down into the ground
        'ceiling': {'height': 2.2, 'texture': 'planks', 'tile': 1.0, 'to': 7, 'light': 0.5},   # the station's roof
        'distance': 200,
    }
    return road_scene(
        road,
        title='The roller coaster - at the top of the lift hill, the big drop falling away below',
        sky='day',
        skyline='hills',
        lights=[{'type': 'sun', 'azimuth': 250, 'elevation': 40, 'intensity': 0.85}],
        ambient=[0.6, 0.62, 0.68],
        fog={'color': [0.72, 0.8, 0.9], 'density': 0.004},
        camera={'at': 41.8, 'x': 0.0, 'height': 0.75, 'fov': 66, 'pitch': -0.55},
        shots=[
            {'at': 41.8, 'x': 0.0, 'height': 0.75, 'fov': 66, 'pitch': -0.55, 'post': LOOK, 'vehicle': FRONT},
            {'at': 66.0, 'x': 0.0, 'height': 0.75, 'fov': 66, 'pitch': 0.0, 'roll': 14, 'yaw': 6, 'post': LOOK,
             'vehicle': CAR},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(roller_coaster().save(os.path.join(HERE, 'roller_coaster.json')))

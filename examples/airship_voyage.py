"""The airship voyage: a road scene (road.py) in the air - at the bow of an airship at sunrise over a sea of cloud,
islands of rock floating at every height with waterfalls pouring off them, other airships under way, gulls.

The airship's course is the road, too narrow to see; the ground is `void` and the clouds lie `below` (`cloud_floor`).
`floating_rock` islands hang at every height and distance (a roadside row with `z` spread, and a few placed),
`island_falls` pouring off the edge of the nearer ones; airships (`airship`, in its three colours by `variant`)
under way round you; `seagull`s; the sun just up in a `dawn` sky. Your own deck's bow before you (`airship_deck`,
the shot's vehicle).
Run:  python airship_voyage.py  -> writes airship_voyage.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.2}]


def airship_voyage():
    road = {
        'sections': [[400, 0.02, 0]],
        'width': 0.002, 'surface': 'asphalt', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': 'void',
        'below': {'depth': 16, 'tile': 8, 'haze': 0.4, 'texture': 'cloud_floor'},
        'distance': 400,
    }
    roadside = [
        {'type': 'floating_rock', 'density': 0.05, 'offset': [6.0, 60.0], 'z': [-10.0, 10.0], 'scale': [3.0, 10.0],
         'seed': 3},
    ]
    sprites = [
        {'type': 'floating_rock', 'at': 34, 'x': -12, 'z': -6.0, 'scale': 14},     # an island, its fall pouring
        {'type': 'island_falls', 'at': 33.0, 'x': -7.0, 'z': -12.0, 'scale': 17.6},  # off its edge
        {'type': 'floating_rock', 'at': 60, 'x': 16, 'z': 1.0, 'scale': 18},
        {'type': 'island_falls', 'at': 59.0, 'x': 10.0, 'z': -10.0, 'scale': 25.8},
        {'type': 'airship', 'variant': 1, 'at': 18, 'x': 6.5, 'z': 1.2, 'scale': 2.8},
        {'type': 'airship', 'variant': 0, 'at': 45, 'x': -6.0, 'z': 4.5, 'scale': 3.2, 'flip': True},
        {'type': 'airship', 'variant': 2, 'at': 90, 'x': 4.0, 'z': -3.0, 'scale': 3.2},
        {'type': 'seagull', 'at': 8, 'x': -1.6, 'z': 1.0, 'scale': 0.3},
        {'type': 'seagull', 'at': 10, 'x': 1.8, 'z': 1.5, 'scale': 0.3, 'flip': True},
    ]
    return road_scene(
        road,
        title='The airship voyage - at the bow of an airship at sunrise over a sea of cloud, islands floating by',
        sky='dawn',
        sky_objects=[{'type': 'sun', 'azimuth': 262, 'elevation': 6, 'size': 3.0}],
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 10, 'intensity': 0.9, 'color': [1.0, 0.84, 0.64],
                 'disc': False}],
        ambient=[0.62, 0.58, 0.62],
        fog={'color': [0.94, 0.82, 0.76], 'density': 0.004, 'sky_mix': 0.3},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': -0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': -0.04, 'post': LOOK,
                'vehicle': {'type': 'airship_deck', 'ahead': 0.7, 'z': 0.32, 'scale': 0.24}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(airship_voyage().save(os.path.join(HERE, 'airship_voyage.json')))

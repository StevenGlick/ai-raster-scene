"""The salt mirror: a road scene (road.py) on a salt flat after the rain - driving out across a thin sheet of water
over the salt at sunset, the whole sky doubled in it to the horizon, the mountains standing on their reflections,
another truck far out ahead, a figure standing on the mirror.

There is no road but your tracks: the surface and the ground are the same `salt_flat`, the ground's band mirroring
almost all of the sky (`reflect` 0.85, the surface's `wet` the same), tyre marks down the middle; the mountains are a
`mountains` skyline, the sun low in a `sunset` sky. A `pickup_truck` far out ahead, the `explorer` standing on the
water, both doubled; your jeep from behind.
Run:  python salt_mirror.py  -> writes salt_mirror.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.2}]


def salt_mirror():
    road = {
        'sections': [[400, 0.0, 0]],
        'width': 1.6, 'surface': 'salt_flat', 'lines': False, 'rumble': False, 'bands': 0.0, 'wet': 0.85,
        'ground': [{'texture': 'salt_flat', 'reflect': 0.85}],
        'distance': 400,
    }
    decals = [{'tex': 'tyre_marks', 'density': 0.25, 'size': [1.0, 1.4], 'side': 'road', 'seed': 1}]
    sprites = [
        {'type': 'pickup_truck', 'at': 26, 'x': 1.4, 'scale': 0.5},
        {'type': 'explorer', 'at': 9, 'x': -2.2},
    ]
    return road_scene(
        road,
        title='The salt mirror - driving out over a salt flat after rain at sunset, the whole sky doubled in it',
        sky='sunset',
        skyline={'type': 'mountains', 'height': 1.1, 'color': [0.42, 0.3, 0.42]},
        sky_objects=[{'type': 'sun', 'azimuth': 270, 'elevation': 3, 'size': 3.0}],
        lights=[{'type': 'sun', 'azimuth': 270, 'elevation': 6, 'intensity': 0.8, 'color': [1.0, 0.72, 0.5],
                 'disc': False}],
        ambient=[0.6, 0.5, 0.56],
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.06},
        shots=[{'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'jeep', 'ahead': 2.6}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(salt_mirror().save(os.path.join(HERE, 'salt_mirror.json')))

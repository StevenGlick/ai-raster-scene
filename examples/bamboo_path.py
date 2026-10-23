"""The bamboo path: a road scene (road.py) in a bamboo grove - walking a path between walls of tall green stalks
that close overhead, the light coming down green through the leaves, a samurai walking ahead of you.

A `gravel` path between low fences of dry `bamboo` poles (walls along both edges); `bamboo_stalks` crowding both
sides in rows, the nearest at the fences, more behind (`scale` 8-11), so the grove closes over the path; a high
`ceiling` of `jungle_leaves`, lit, for the canopy; `light_shaft`s slanting down; a green-gold `fog`; the `samurai`
walking away up the path. On foot.
Run:  python bamboo_path.py  -> writes bamboo_path.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.4}]


def bamboo_path():
    road = {
        'sections': [[24, 0, 0.1], [30, -0.2, 0.2], [30, 0.25, 0.1], [200, -0.05, 0]],
        'width': 1.4, 'surface': 'gravel', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': [{'width': 0.3, 'texture': 'moss'}, {'texture': 'leaves_fallen'}],
        'walls': [{'side': 'both', 'offset': 0.1, 'height': 0.45, 'texture': 'bamboo', 'tile': [1.2, 0.45]}],
        'ceiling': {'height': 9, 'texture': 'jungle_leaves', 'tile': 3.0, 'light': 0.7},
        'distance': 120,
    }
    roadside = [
        {'type': 'bamboo_stalks', 'density': 1.4, 'offset': [0.35, 1.2], 'scale': [8, 11], 'from': 3.5, 'seed': 1},
        {'type': 'bamboo_stalks', 'density': 1.2, 'offset': [1.2, 6.0], 'scale': [8, 11], 'seed': 2},
    ]
    sprites = [
        {'type': 'samurai', 'at': 5.5, 'x': -0.05, 'view': 'back'},
        {'type': 'light_shaft', 'at': 7, 'x': -0.4, 'scale': 8, 'opacity': 0.5},
        {'type': 'light_shaft', 'at': 12, 'x': 0.4, 'scale': 8, 'opacity': 0.45},
    ]
    return road_scene(
        road,
        title='The bamboo path - walking a path through a bamboo grove, the light coming down green, a samurai ahead',
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 290, 'elevation': 50, 'intensity': 0.6, 'color': [1.0, 0.96, 0.82]}],
        ambient=[0.52, 0.58, 0.46],
        fog={'color': [0.62, 0.72, 0.5], 'density': 0.04},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.12},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.12, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(bamboo_path().save(os.path.join(HERE, 'bamboo_path.json')))

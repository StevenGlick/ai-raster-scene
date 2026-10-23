"""The safari drive: a road scene (road.py) - following a jeep down a red dirt track across the savanna at sunset,
acacias spread flat against the sky, giraffes browsing, elephants on the move, zebras grazing.

The track is red dirt (`dirt` tinted), its edges ragged into the grass; the grass is `dry_grass`, gold in the low
sun, the `hills` skyline far off. `acacia`s stand far apart by density; a giraffe browses by one, two elephants
walk across the plain, zebras graze in a knot; the `jeep` goes on ahead with its passengers. The sun going down
huge and orange over the plain.
Run:  python safari_drive.py  -> writes safari_drive.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.2}]


def safari_drive():
    road = {
        'sections': [[16, 0, 0], [40, 0.15, 0.4], [40, -0.2, -0.3], [300, 0.05, 0.1]],
        'width': 1.4, 'surface': {'base': 'dirt', 'tint': [1.0, 0.62, 0.42]}, 'lines': False, 'rumble': False,
        'bands': 0.0, 'edge': {'ragged': 0.3, 'blend': 0.5},
        'ground': {'base': 'dry_grass', 'tint': [1.05, 0.9, 0.62]},
        'distance': 300,
    }
    roadside = [
        {'type': 'acacia', 'density': 0.03, 'offset': [3.0, 40.0], 'scale': [2.0, 3.0], 'seed': 1},
    ]
    scatter = [{'of': ['dry_tuft', 'dry_tuft', 'rocks'], 'density': 0.6, 'offset': [0.0, 4.0], 'seed': 2}]
    sprites = [
        {'type': 'jeep', 'at': 6.5, 'x': 0.0},
        {'type': 'acacia', 'at': 12, 'x': -5.5, 'scale': 2.8},
        {'type': 'giraffe', 'at': 11.5, 'x': -4.0, 'scale': 2.0},
        {'type': 'giraffe', 'at': 15, 'x': -6.5, 'scale': 1.8, 'flip': True},
        {'type': 'elephant', 'at': 17, 'x': 5.2, 'scale': 1.2, 'flip': True},
        {'type': 'elephant', 'at': 18.5, 'x': 7.0, 'scale': 0.8, 'flip': True},
        {'type': 'zebra', 'at': 12, 'x': 4.0},
        {'type': 'zebra', 'at': 12.8, 'x': 5.0, 'flip': True},
        {'type': 'zebra', 'at': 13.5, 'x': 4.4},
    ]
    return road_scene(
        road,
        title='The safari drive - down a red track across the savanna at sunset, giraffes, elephants, zebras',
        sky='sunset',
        skyline={'type': 'hills', 'height': 0.8, 'color': [0.5, 0.32, 0.34]},
        sky_objects=[{'type': 'sun', 'azimuth': 266, 'elevation': 4, 'size': 4.0}],
        lights=[{'type': 'sun', 'azimuth': 266, 'elevation': 7, 'intensity': 0.9, 'color': [1.0, 0.7, 0.42],
                 'disc': False}],
        ambient=[0.56, 0.46, 0.44],
        fog={'color': [0.9, 0.6, 0.45], 'density': 0.004, 'sky_mix': 0.3},
        roadside=roadside,
        scatter=scatter,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.65, 'fov': 62, 'pitch': 0.04},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.65, 'fov': 62, 'pitch': 0.04, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(safari_drive().save(os.path.join(HERE, 'safari_drive.json')))

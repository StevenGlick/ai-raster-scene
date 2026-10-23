"""The blossom road: a road scene (road.py) - walking a country road in spring through an avenue of cherry trees in
full bloom, petals falling, a shrine gate standing over the road, a lone snow-capped peak beyond.

A narrow road of old asphalt; on the left flooded paddies (a band of `water`) that mirror the trees and the
mountain, on the right grass and then fields. `cherry_tree`s every few units either side make an avenue; the
`torii` stands over the road ahead; the `snow_peak` on the horizon; petals drift down (the `snow` effect in pink).
An early morning, the `dawn` sky.
Run:  python blossom_road.py  -> writes blossom_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0},
        {'fx': 'snow', 'color': [1.0, 0.78, 0.86], 'count': 170, 'opacity': 0.8}]          # petals falling


def blossom_road():
    road = {
        'sections': [[16, 0, 0], [40, 0.12, 0.4], [40, -0.15, -0.3], [400, 0.05, 0]],
        'width': 1.8, 'surface': {'base': 'asphalt', 'tint': [0.82, 0.8, 0.8]}, 'lines': False, 'rumble': False,
        'bands': 0.02, 'edge': {'ragged': 0.08, 'blend': 0.2},
        'ground': {'left': [{'width': 0.5, 'texture': 'grass'}, {'width': 10, 'texture': 'water'},
                            {'texture': 'pasture'}],
                   'right': [{'width': 1.2, 'texture': 'grass'}, {'texture': 'pasture'}]},
        'distance': 400,
    }
    roadside = [
        {'type': 'cherry_tree', 'side': 'both', 'every': 4.4, 'offset': 0.9, 'scale': [2.0, 2.5], 'seed': 1},
        {'type': ['grass_tuft', 'flowers'], 'side': 'right', 'density': 0.8, 'offset': [0.1, 1.2], 'scale': [0.2, 0.35],
         'seed': 2},
    ]
    sprites = [
        {'type': 'torii', 'at': 11, 'x': 0.0, 'scale': 3.0},
        {'type': 'snow_peak', 'at': 220, 'x': 0, 'scale': 46},
    ]
    return road_scene(
        road,
        title='The blossom road - walking a country road through cherry trees in bloom, a shrine gate, a snowy peak beyond',
        sky='dawn',
        lights=[{'type': 'sun', 'azimuth': 300, 'elevation': 14, 'intensity': 0.8, 'color': [1.0, 0.9, 0.8]}],
        ambient=[0.66, 0.62, 0.66],
        fog={'color': [0.9, 0.84, 0.88], 'density': 0.002, 'sky_mix': 0.25},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.2, 'height': 0.55, 'fov': 62, 'pitch': 0.06},
        shots=[{'at': 1.0, 'x': 0.2, 'height': 0.55, 'fov': 62, 'pitch': 0.06, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(blossom_road().save(os.path.join(HERE, 'blossom_road.json')))

"""The desert highway: a road scene (road.py) - a two-lane highway straight across the desert at noon, over long
rolling dips, buttes standing off in the haze, riding it on a motorbike.

The highway is faded asphalt, a dashed yellow line down its middle, white edges, a gravel shoulder, then pale dirt
and sand. Its `sections` are long and nearly straight but rise and fall, so each crest hides the road beyond until
it shows again further down. The buttes are `walls` far out on both sides, cut into `blocks` - each its own height
- with `gaps` between them (most of the blocks left out), banded `sandstone`. Saguaros by density, the `desert`
scatter, a line of power poles with their wires sagging between them (`power_lines`), a billboard, a truck
ahead. You ride a `dirt_bike`. The second shot stands on a crest with a long lens, the road rising and falling
away ahead.
Run:  python desert_highway.py  -> writes desert_highway.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]
DIRT = {'base': 'desert_wash', 'tint': [1.0, 0.94, 0.86]}


def desert_highway():
    road = {
        'sections': [[30, 0, 0], [60, 0, 3.0], [50, 0.05, -3.4], [70, 0, 3.8], [60, -0.05, -3.2], [600, 0, 1.0]],
        'width': 3.0, 'lanes': 2, 'surface': {'base': 'asphalt', 'tint': [1.1, 1.06, 1.0]}, 'lines': '#e8c040',
        'edges': '#e0e0dc', 'rumble': False, 'shoulder': {'width': 0.4, 'texture': 'gravel'},
        'ground': [{'width': 4, 'texture': DIRT}, {'texture': 'sand'}],
        'walls': [
            {'side': 'right', 'offset': 70, 'z': -2, 'height': 16, 'ragged': 9, 'texture': 'sandstone', 'tile': 8,
             'blocks': 26, 'gaps': 0.55, 'seed': 1},
            {'side': 'left', 'offset': 110, 'z': -2, 'height': 22, 'ragged': 10, 'texture': 'sandstone', 'tile': 9,
             'blocks': 34, 'gaps': 0.6, 'seed': 2},
            {'side': 'right', 'offset': 0.9, 'z': 3.0, 'height': 0.6, 'texture': 'power_lines', 'tile': [10, 0.6]},
        ],
        'bands': 0.05, 'distance': 600,
    }
    roadside = [
        {'type': 'saguaro', 'density': 0.06, 'offset': [2.0, 14.0], 'scale': [1.6, 2.6], 'seed': 1},
        {'type': 'power_pole', 'side': 'right', 'every': 10, 'from': 0, 'offset': 0.9, 'scale': 3.5},
        {'type': 'billboard', 'side': 'left', 'every': 120, 'from': 40, 'offset': 4.0, 'scale': 2.6, 'variant': 1},
    ]
    scatter = [{'of': 'desert', 'density': 0.2, 'offset': [0.2, 6.0], 'seed': 1}]
    decals = [{'tex': 'drifts', 'density': 0.03, 'size': [0.6, 1.2], 'seed': 1},
              {'tex': 'wear', 'density': 0.02, 'size': [0.5, 1.0], 'seed': 2}]
    sprites = [
        {'type': 'box_truck', 'at': 26, 'x': 0.75},
        {'type': 'speed_sign', 'at': 8, 'x': 2.3},
    ]
    return road_scene(
        road,
        title='The desert highway - straight across the desert at noon, over the dips, buttes in the haze',
        sky='day',
        lights=[{'type': 'sun', 'azimuth': 240, 'elevation': 62, 'intensity': 0.9}],
        ambient=[0.66, 0.6, 0.56],
        fog={'color': [0.92, 0.86, 0.76], 'density': 0.0035},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.7, 'fov': 62, 'pitch': 0.06},
        shots=[
            {'at': 2.0, 'x': 0.0, 'height': 0.7, 'fov': 62, 'pitch': 0.06, 'post': LOOK,
             'vehicle': {'type': 'dirt_bike', 'ahead': 2.4, 'x': 0.75}},
            {'at': 87.0, 'x': 0.4, 'height': 1.0, 'fov': 46, 'pitch': 0.03, 'post': LOOK},   # from a crest
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(desert_highway().save(os.path.join(HERE, 'desert_highway.json')))

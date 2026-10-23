"""The overgrown highway: a road scene (road.py) years after everyone left - walking down a motorway gone back to
the wild in the golden light, weeds up through every crack, rusted cars where they were left, deer grazing on the
asphalt, a broken overpass ahead, the dead city on the horizon.

The surface is `asphalt` faded pale, its lines a dull `lines` colour; the decals do the years - `crack`s
everywhere, `pothole`s, `moss_patch`es and `leaf_litter`; the `overgrown` scatter set puts weeds up through the road
(`side` road) and `undergrowth` fills the verges; the guard rails are `guard_rail` tinted rust. Trees and bushes
crowd in from both sides; `wrecked_car`s (in three faded paints) stand where they stopped, `deer` on the road, the
`broken_overpass` across it ahead; a `city` skyline, unlit, far off in the haze.
Run:  python overgrown_highway.py  -> writes overgrown_highway.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]
ASPHALT = {'base': 'asphalt', 'tint': [1.6, 1.55, 1.42]}
RUSTY_RAIL = {'base': 'guard_rail', 'tint': [0.95, 0.66, 0.48]}


def overgrown_highway():
    road = {
        'sections': [[30, 0, 0], [40, 0.05, 0.15], [200, -0.04, 0]],
        'width': 2.4, 'surface': ASPHALT, 'lanes': 2, 'lines': '#a8a48c', 'rumble': False, 'bands': 0.0,
        'ground': [{'width': 0.4, 'texture': 'dry_grass'}, {'texture': 'grass'}],
        'walls': [{'side': 'both', 'offset': 0.25, 'height': 0.3, 'texture': RUSTY_RAIL, 'tile': [1, 0.3]}],
        'distance': 220,
    }
    roadside = [
        {'type': ['tree', 'birch', 'tree'], 'density': 0.18, 'offset': [1.6, 10.0], 'scale': [2.0, 3.6], 'seed': 4},
        {'type': 'bush', 'density': 0.6, 'offset': [0.3, 3.0], 'scale': [0.4, 0.9], 'seed': 5},
    ]
    scatter = [
        {'of': 'overgrown', 'density': 2.2, 'side': 'road', 'offset': [-1.2, 1.2], 'clump': 0.8, 'scale': 0.7,
         'clear': 1.6, 'seed': 1},
        {'of': 'undergrowth', 'density': 1.2, 'offset': [0.0, 4.0], 'seed': 2},
    ]
    decals = [
        {'tex': 'crack', 'density': 0.6, 'size': [0.6, 1.2], 'side': 'road', 'seed': 1},
        {'tex': 'pothole', 'density': 0.08, 'size': [0.3, 0.6], 'side': 'road', 'seed': 2},
        {'tex': 'moss_patch', 'density': 0.25, 'size': [0.4, 0.9], 'side': 'road', 'seed': 3},
        {'tex': 'vines', 'density': 0.15, 'size': [0.8, 1.4], 'side': 'road', 'seed': 4},
    ]
    sprites = [
        {'type': 'wrecked_car', 'variant': 0, 'at': 4.5, 'x': -0.55},
        {'type': 'wrecked_car', 'variant': 2, 'at': 8.0, 'x': 0.6, 'flip': True},
        {'type': 'wrecked_car', 'variant': 1, 'at': 14, 'x': -0.25},
        {'type': 'wrecked_car', 'variant': 0, 'at': 20, 'x': 0.7},
        {'type': 'deer', 'at': 6.5, 'x': 0.1},
        {'type': 'deer', 'at': 6.8, 'x': -0.22, 'flip': True, 'scale': 0.42},
        {'type': 'birch', 'at': 12, 'x': -1.05, 'scale': 2.2},
        {'type': 'broken_overpass', 'at': 26, 'x': 0.0, 'scale': 4.0},
        {'type': 'billboard', 'variant': 1, 'at': 30, 'x': -4.0, 'tint': [0.62, 0.6, 0.58]},
    ]
    return road_scene(
        road,
        title='The overgrown highway - a motorway gone back to the wild, rusted cars, deer on the road, a broken '
              'overpass',
        sky='golden',
        skyline=[{'type': 'city', 'height': 1.0, 'color': [0.46, 0.48, 0.5], 'lights': 0}],
        lights=[{'type': 'sun', 'azimuth': 300, 'elevation': 14, 'intensity': 0.9, 'color': [1.0, 0.86, 0.66]}],
        ambient=[0.62, 0.62, 0.58],
        fog={'color': [0.84, 0.8, 0.66], 'density': 0.012, 'sky_mix': 0.3},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.0},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.55, 'fov': 62, 'pitch': 0.0, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(overgrown_highway().save(os.path.join(HERE, 'overgrown_highway.json')))

"""The winter road: a road scene (road.py) - a mountain road at night after snow, the banks the plough left along
it, snowy pines, your headlights on the falling snow, a car's tail lights ahead.

The road is asphalt with snow blown over it in drifts (`decals`, the sand drift tinted white) and worn down to the
tarmac in two tracks; along both edges the plough's banks are low `walls` of `snow` with a `ragged` top, and beyond
them the snow lies deep, `snowy_pine`s by density, marker posts every few units. The moon over the peaks
(`mountains`), blue night, your `headlights` pooling on the road and the snow falling through them (`snow`).
Run:  python winter_road.py  -> writes winter_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.2, 'spread': 0.5},
        {'fx': 'snow', 'density': 1.2}]
SNOWY = {'base': 'sand_drift'}


def winter_road():
    road = {
        'sections': [[14, 0, 0], [40, 0.45, 1.2], [36, -0.6, 0.8], [50, 0.35, -0.6], [300, -0.2, 0.4]],
        'width': 2.8, 'lanes': 2, 'surface': 'asphalt', 'lines': '#d8d8d0', 'rumble': False,
        'ground': 'snow',
        'walls': [{'side': 'both', 'offset': 0.15, 'height': 0.32, 'texture': 'snow', 'tile': 1.0, 'ragged': 0.12,
                   'seed': 1}],                                             # the plough's banks
        'bands': 0.03, 'distance': 220,
    }
    roadside = [
        {'type': 'snowy_pine', 'density': 0.9, 'offset': [1.0, 12.0], 'scale': [2.4, 4.0], 'clear': 1.0, 'seed': 1},
        {'type': 'reflector_post', 'every': 5, 'offset': 0.0, 'from': 3},
    ]
    scatter = [{'of': ['boulder_snow', 'bush_snow'], 'density': 0.06, 'offset': [0.5, 5.0], 'seed': 2}]
    decals = [
        {'tex': 'sand_drift', 'density': 0.12, 'size': [0.8, 1.6], 'tint': [1.15, 1.25, 1.45], 'seed': 1},
        {'tex': 'sand_drift', 'density': 0.2, 'offset': [-1.4, -0.9], 'size': [0.6, 1.2], 'tint': [1.15, 1.25, 1.45],
         'seed': 2},
        {'tex': 'sand_drift', 'density': 0.2, 'offset': [0.9, 1.4], 'size': [0.6, 1.2], 'tint': [1.15, 1.25, 1.45],
         'seed': 3},
    ]
    sprites = [{'type': 'car_sedan', 'at': 19, 'x': 0.7, 'tint': [0.5, 0.52, 0.6]}]
    return road_scene(
        road,
        title='The winter road - a mountain road at night after snow, headlights on the falling snow',
        sky='night',
        skyline='mountains',
        sky_objects=[{'type': 'moon', 'azimuth': 258, 'elevation': 16, 'size': 3.0}],
        lights=[{'type': 'moon', 'azimuth': 258, 'elevation': 30, 'intensity': 0.5, 'disc': False}],
        ambient=[0.22, 0.26, 0.38],
        fog={'color': [0.16, 0.2, 0.3], 'density': 0.02},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': -0.65, 'height': 0.7, 'fov': 64, 'pitch': 0.08},
        shots=[{'at': 2.0, 'x': -0.65, 'height': 0.7, 'fov': 64, 'pitch': 0.08, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True, 'beam': 1.3}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(winter_road().save(os.path.join(HERE, 'winter_road.json')))

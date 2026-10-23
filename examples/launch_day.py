"""Launch day: a road scene (road.py) on the coast at dusk - driving the causeway across the lagoon toward the
launch site, the rocket floodlit white on its pad far ahead, cars pulled over and people out on the shoulder to
watch, the rocket and the sky doubled in the still water.

A straight causeway (`asphalt`, white lines) across the water (`ground` bands: a grass shoulder, then `water`
tinted to the dusk, which mirrors); reeds and a few palms along it. The `rocket_pad` stands on the water at the
road's end, `fullbright` - the floodlights - with its tower's lights; cars pulled over on the shoulder
(`car_sedan`, `car_compact`) and people by them (`crowd`). Your convertible from behind, its lights on.
Run:  python launch_day.py  -> writes launch_day.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.7, 'radius': 2.2}]


def launch_day():
    road = {
        'sections': [[30, 0, 0], [60, 0.05, 0], [300, -0.02, 0]],
        'width': 2.4, 'lanes': 2, 'surface': 'asphalt', 'lines': '#e8e8e8', 'rumble': False, 'bands': 0.02,
        'ground': [{'width': 0.6, 'texture': 'grass'}, {'texture': {'base': 'water', 'tint': [0.62, 0.52, 0.62]}}],
        'distance': 260,
    }
    roadside = [
        {'type': 'reeds', 'density': 0.5, 'offset': [0.2, 1.0], 'scale': [0.3, 0.5], 'seed': 1},
        {'type': ['palm', 'palm_lean'], 'density': 0.04, 'offset': [0.3, 0.6], 'scale': [1.8, 2.4], 'seed': 2},
    ]
    sprites = [
        {'type': 'rocket_pad', 'at': 150, 'x': 6.0, 'scale': 34, 'fullbright': True},
        {'type': 'car_sedan', 'at': 9, 'x': 1.65, 'variant': 1},
        {'type': 'car_compact', 'at': 15, 'x': 1.7, 'variant': 3},
        {'type': 'car_sedan', 'at': 24, 'x': 1.7, 'variant': 2},
        {'type': 'crowd', 'at': 10.5, 'x': 1.9, 'scale': 0.6},
        {'type': 'crowd', 'at': 11.2, 'x': 2.2, 'scale': 0.6, 'flip': True},
        {'type': 'crowd', 'at': 16.6, 'x': 2.0, 'scale': 0.6},
        {'type': 'crowd', 'at': 26, 'x': 2.1, 'scale': 0.6},
    ]
    return road_scene(
        road,
        title='Launch day - driving the causeway at dusk toward the rocket floodlit on its pad, people out to watch',
        sky='dusk',
        lights=[{'type': 'sun', 'azimuth': 250, 'elevation': 2, 'intensity': 0.5, 'color': [1.0, 0.7, 0.5],
                 'disc': False}],
        ambient=[0.42, 0.38, 0.48],
        fog={'color': [0.5, 0.42, 0.5], 'density': 0.004, 'sky_mix': 0.25},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': -0.55, 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[{'at': 2.0, 'x': -0.55, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(launch_day().save(os.path.join(HERE, 'launch_day.json')))

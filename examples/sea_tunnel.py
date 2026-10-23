"""The sea tunnel: a road scene (road.py) - a road through a glass tube laid on the sea floor, sharks, rays and a
turtle gliding past outside, the light coming down blue from far above.

The tube's sides are `walls` of glass (`viewport`: open between a frame at its foot and its head and a rib every
two units) and its roof a `ceiling` of the deep water seen from below (`tunnel_roof`, lit by the surface far up),
lamps along it; outside, the sea floor - sand, rocks, coral - runs off into blue water (the `fog` thick and blue,
the sky all fog). Fish swim beyond the glass at every height: a shark, a manta, a turtle, a school, jellies, a
whale shark far off. You drive it, headlights on.
Run:  python sea_tunnel.py  -> writes sea_tunnel.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.4, 'spread': 0.5}]
SEA = [0.06, 0.24, 0.36]


def sea_tunnel():
    road = {
        'sections': [[20, 0, 0], [60, 0.2, -0.6], [60, -0.25, 0.4], [300, 0.1, 0]],
        'width': 3.0, 'lanes': 2, 'surface': 'asphalt', 'lines': '#e0e0e0', 'edges': '#e0c040', 'rumble': False,
        'ground': [{'width': 0.5, 'texture': 'concrete'}, {'texture': 'seabed'}],
        'walls': [{'side': 'both', 'offset': 0.45, 'height': 2.6, 'texture': 'viewport', 'tile': [2.0, 2.6]}],
        'ceiling': {'height': 2.6, 'texture': 'tunnel_roof', 'tile': 2.0, 'light': 0.5},
        'distance': 200,
    }
    lights = [{'at': a, 'x': 0.0, 'z': 2.5, 'radius': 3.4, 'color': [0.85, 0.95, 1.0], 'intensity': 0.9}
              for a in range(3, 160, 6)]
    roadside = [
        {'type': ['reef_rock', 'brain_coral', 'sea_fan', 'staghorn_coral', 'rocks'], 'density': 0.25,
         'offset': [1.2, 9.0], 'scale': [0.5, 1.4], 'seed': 1},
        {'type': 'kelp', 'density': 0.12, 'offset': [2.0, 10.0], 'scale': [1.6, 2.8], 'seed': 2},
    ]
    sprites = [
        {'type': 'reef_shark', 'at': 9, 'x': -3.6, 'z': 1.2, 'scale': 1.0},
        {'type': 'manta_ray', 'at': 14, 'x': 3.8, 'z': 2.4, 'scale': 1.6},
        {'type': 'sea_turtle', 'at': 7, 'x': 2.8, 'z': 0.6, 'scale': 0.7, 'flip': True},
        {'type': 'fish_school', 'at': 18, 'x': -4.5, 'z': 2.0, 'scale': 1.6},
        {'type': 'moon_jelly', 'at': 11, 'x': 3.0, 'z': 3.2, 'scale': 0.5},
        {'type': 'moon_jelly', 'at': 12.5, 'x': 3.6, 'z': 3.8, 'scale': 0.4},
        {'type': 'whale_shark', 'at': 40, 'x': -12, 'z': 4.5, 'scale': 6.0},
        {'type': 'car_compact', 'at': 16, 'x': -0.75, 'variant': 2},
    ]
    return road_scene(
        road,
        title='The sea tunnel - a road through a glass tube on the sea floor, sharks and rays outside',
        sky='night',
        ambient=[0.42, 0.56, 0.62],
        fog={'color': SEA, 'density': 0.06, 'sky_mix': 1.0},
        lights=lights,
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.75, 'height': 0.7, 'fov': 66, 'pitch': 0.08},
        shots=[{'at': 2.0, 'x': 0.75, 'height': 0.7, 'fov': 66, 'pitch': 0.08, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(sea_tunnel().save(os.path.join(HERE, 'sea_tunnel.json')))

"""The volcano island: a night at landscape scale, a volcano erupting over a harbour town.

A map cell is about 100 m. The island rises out of dark sea (`harbor_water`) ringed with `black_sand`, wooded
low down (`forest_canopy`), old lava on its western side (`lava_field`, still glowing in its cracks); in the
middle the volcano - a `mountain` of `volcanic` rock with a `crater`, lava fountaining over its rim (`blaze`)
and running down its flanks (`lava`, aimed the way the cameras look), a river of it (`lava_flow`) going on from
its foot to the sea, where it steams. Its `ash_plume` towers over it, lit from below. A harbour town on the
south-east shore keeps its lights on; a boat off the lava delta watches the river meet the sea.
Run:  python volcano_island.py  -> writes volcano_island.json next to this file.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 52, 46
CX, CY, R = 26.0, 19.0, 13.0               # the island
PEAK = (26.0, 17.5)                        # the volcano
RIM = 7.7                                  # the crater rim's height (0.86 of its 9)
GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.5, 'radius': 2.8, 'spread': 0.55}


def river(t):
    """The lava river from the volcano's foot (t=0) to the sea (t=1)."""
    return 17.6 - 4.8 * t + 0.6 * math.sin(t * 5.0), 22.6 + 3.2 * t


def volcano_island():
    rng = random.Random(31)
    g = Grid(W, H, fill='~')
    for y in range(H):
        for x in range(W):
            a = math.atan2(y + 0.5 - CY, x + 0.5 - CX)
            edge = R + 1.4 * math.sin(a * 3 + 1.0) + 0.9 * math.sin(a * 7 + 2.0)
            d = math.hypot(x + 0.5 - CX, (y + 0.5 - CY) * 1.1)
            if d < edge - 1.3:
                west = math.cos(a) < -0.25
                g.put(x, y, 'l' if west and d > 6 and rng.random() < 0.85 else 'w')
            elif d < edge:
                g.put(x, y, 'k')                                         # the black beach
    for k in range(40):                                                 # the lava river to the sea
        x, y = river(k / 39)
        for dx in (0, 1):
            if g.get(int(x) + dx, int(y)) != '~':
                g.put(int(x) + dx, int(y), 'L')
    g.rect(32, 29, 35, 30, 's')                                          # the harbour town
    g.rect(32, 31, 35, 31, 'q')
    town = [{'type': 'city_block', 'x': x + 0.5, 'y': y + 0.5, 'height': [0.03, 0.14], 'count': 2, 'lit': 0.5,
             'style': ['brick', 'apartment', 'office'], 'seed': rng.randrange(1 << 16)} for x in range(32, 36)
            for y in range(29, 31)]
    sx, sy = river(1.0)
    rim = [(PEAK[0] + 1.3 * math.cos(a), PEAK[1] + 1.3 * math.sin(a) * 0.9) for a in (0.6, 1.9, 2.8, 4.4, 5.4)]
    sprites = ([{'x': PEAK[0] + 0.3, 'y': PEAK[1] - 0.2, 'z': RIM - 0.3, 'type': 'ash_plume', 'tint': [1.5, 1.25, 1.15]}]
               + [{'x': round(x, 2), 'y': round(y, 2), 'z': RIM - 0.5, 'type': 'blaze', 'scale': round(rng.uniform(2.2, 3.4), 2)}
                  for x, y in rim]                                       # lava fountaining over the rim
               + [{'x': 36.6, 'y': 33.6, 'type': 'ferry', 'flip': True}, {'x': 31.2, 'y': 34.4, 'type': 'sailboat'},
                  {'x': sx - 0.4, 'y': sy + 0.5, 'type': 'smoke_plume', 'scale': 1.4, 'tint': [1.6, 1.6, 1.7]},
                  {'x': sx + 0.3, 'y': sy + 0.8, 'type': 'smoke_plume', 'scale': 1.0, 'tint': [1.7, 1.7, 1.8]}])
    lights = [{'type': 'moon', 'azimuth': 320, 'elevation': 24, 'intensity': 0.22, 'disc_size': 1.4},
              {'x': PEAK[0], 'y': PEAK[1], 'z': RIM + 0.6, 'radius': 11, 'color': [1.0, 0.42, 0.14], 'intensity': 1.7},
              {'x': PEAK[0], 'y': PEAK[1], 'z': RIM + 3.5, 'radius': 6, 'color': [1.0, 0.5, 0.2], 'intensity': 0.9},
              {'x': PEAK[0] + 0.6, 'y': PEAK[1] - 0.3, 'z': RIM + 7.0, 'radius': 7, 'color': [0.9, 0.45, 0.22],
               'intensity': 0.8}]                                       # the ash column lit from inside
    lights += [{'x': round(river(t)[0], 2), 'y': round(river(t)[1], 2), 'z': 0.15, 'radius': 2.2,
                'color': [1.0, 0.46, 0.16], 'intensity': 1.0} for t in (0.1, 0.5, 0.9)]
    volcano = {'type': 'mountain', 'x': PEAK[0], 'y': PEAK[1], 'size': 21, 'height': 9, 'rock': 'volcanic',
               'snowline': 0, 'crater': 0.06, 'lava': [80, 112, 150], 'seed': 4, 'casts': False}
    return scene(
        g,
        title='The volcano island - an eruption at night, at landscape scale',
        legend={
            '~': {'floor': 'harbor_water'},
            'k': {'floor': 'black_sand'},
            'w': {'floor': 'forest_canopy'},
            'l': {'floor': 'lava_field'},
            'L': {'floor': 'lava_flow'},
            's': {'floor': 'city_street_lit'},
            'q': {'floor': 'quay'},
        },
        sky='night',
        ambient=[0.12, 0.11, 0.15],
        lights=lights,
        fog={'color': [0.12, 0.08, 0.08], 'density': 0.018, 'glow': 0.9},
        objects=[volcano] + town,
        sprites=sprites,
        camera={'x': 26.0, 'y': 42.0, 'look_at': [26.0, 18.0, 4.6], 'fov': 62, 'height': 0.15},
        shots=[
            {'x': 26.0, 'y': 42.0, 'look_at': [26.0, 18.0, 4.6], 'fov': 62, 'height': 0.15, 'post': [GLOW]},
            {'x': 35.5, 'y': 33.5, 'look_at': [26.5, 18.0, 5.0], 'fov': 64, 'height': 0.08, 'post': [GLOW]},
            {'x': 6.0, 'y': 33.0, 'look_at': [18.0, 22.0, 1.6], 'fov': 62, 'height': 3.0, 'post': [GLOW]},
            {'x': 9.5, 'y': 31.5, 'look_at': [14.0, 23.5, 1.5], 'fov': 64, 'height': 0.06, 'post': [GLOW]},
        ],
        max_distance=70,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(volcano_island().save(os.path.join(HERE, 'volcano_island.json')))

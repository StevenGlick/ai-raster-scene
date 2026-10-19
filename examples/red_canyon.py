"""Red canyon: a dry wash between walls of layered sandstone, the ruins of a cliff dwelling, and a
slot canyon where the sun comes down in a single beam.

Shows the desert kit - `sandstone` walls stacked with bands of `sandstone_pale`, a `desert_wash`
floor dressed with the `desert` scatter set, saguaro and prickly pear, the coursed stone and
T-shaped doors of a cliff dwelling (`pueblo_stone`, `pueblo_door`) with ladders and painted pots -
and a slot canyon of `slot_rock`: its cells roofed at `ceiling_height` with a few left open, so
that a high sun comes down through the gaps in beams of dust (shot overrides give it a sun and a
fog of its own). The last shot is the same wash at sunset.
Run:  python red_canyon.py  -> writes red_canyon.json next to this file.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

ROCK = ['sandstone', 'sandstone', 'sandstone_pale', 'sandstone', 'sandstone', 'sandstone_pale', 'sandstone']
SUN = {'type': 'sun', 'azimuth': 205, 'elevation': 48, 'intensity': 1.05}


def red_canyon():
    g = Grid(36, 58, fill='R')                     # rock everywhere; the canyon is carved out of it
    g.rect(13, 40, 25, 57, 'w')                    # the wash, south
    g.rect(10, 22, 24, 40, 'w')                    # wider in the middle, where the ruins are
    g.rect(15, 18, 22, 22, 'w')                    # narrowing north
    g.rect(14, 2, 24, 17, 'Z')                     # the slot canyon's walls
    g.rect(18, 12, 19, 18, 'S')                    # the slot: two cells wide, winding, roofed
    g.rect(17, 7, 18, 12, 'S')
    g.rect(18, 2, 19, 7, 'S')
    for x, y in ((18, 15), (17, 9), (19, 4)):
        g.put(x, y, 'o')                           # gaps in its roof
    g.rect(10, 24, 12, 35, 'p')                    # the cliff dwelling: a row of rooms against the west wall
    g.rect(10, 27, 11, 31, 'P')                    # a second storey
    for x, y in ((12, 25), (12, 29), (12, 33)):
        g.put(x, y, 'D')                           # T-shaped doors
    g.put(10, 33, 'T')                             # a tower at the back
    for x, y in ((12, 24), (12, 27), (11, 34), (12, 35), (12, 32)):
        g.put(x, y, 'r')                           # walls fallen to stubs
    rng = np.random.default_rng(12)                # ragged walls: alcoves cut in, buttresses standing out
    keep = {(x, y) for x in range(17, 23) for y in range(46, 58)}           # the first shot's foreground
    for y in range(20, 57):
        for x in range(1, 35):
            if g.get(x, y) != 'w' or (x, y) in keep or (x <= 14 and 22 <= y <= 36):
                continue
            walls = [(dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if g.get(x + dx, y + dy) == 'R']
            if walls and rng.random() < 0.18:
                g.put(x, y, 'R')
            elif walls and rng.random() < 0.3:
                dx, dy = walls[0]
                g.put(x + dx, y + dy, 'w')
    for y in range(58):                            # a ragged rim: the rock stands at different heights
        for x in range(36):
            if g.get(x, y) == 'R':
                v = np.sin(x * 0.9 + y * 0.37) + np.sin(y * 0.61 - x * 0.23) + rng.normal(0, 0.4)
                g.put(x, y, 'U' if v < -0.8 else 'Q' if v > 0.8 else 'R')
    sprites = [
        # the wash: saguaros, prickly pear, a tumbleweed, a skull
        {'x': 15.6, 'y': 51.0, 'type': 'saguaro'}, {'x': 23.4, 'y': 47.0, 'type': 'saguaro', 'flip': True},
        {'x': 14.4, 'y': 41.6, 'type': 'saguaro', 'scale': 2.6}, {'x': 23.0, 'y': 36.2, 'type': 'saguaro', 'scale': 3.6},
        {'x': 20.6, 'y': 24.6, 'type': 'saguaro', 'scale': 2.4, 'flip': True},
        {'x': 14.6, 'y': 54.2, 'type': 'prickly_pear'}, {'x': 24.2, 'y': 52.0, 'type': 'prickly_pear', 'flip': True},
        {'x': 17.2, 'y': 44.6, 'type': 'prickly_pear'}, {'x': 23.6, 'y': 30.6, 'type': 'prickly_pear'},
        {'x': 19.6, 'y': 49.2, 'type': 'tumbleweed'}, {'x': 21.8, 'y': 41.0, 'type': 'tumbleweed', 'flip': True},
        {'x': 18.0, 'y': 52.4, 'type': 'cow_skull'},
        {'id': 'cowboy', 'x': 20.4, 'y': 51.2, 'type': 'cowboy', 'facing': 100},
        # the ruins: ladders up to the roofs, pots by the doors, a raven on the tower
        {'x': 13.45, 'y': 27.6, 'type': 'ladder', 'scale': 1.8}, {'x': 12.45, 'y': 30.9, 'type': 'ladder', 'scale': 1.5},
        {'x': 13.4, 'y': 25.8, 'type': 'clay_pot'}, {'x': 13.5, 'y': 26.4, 'type': 'clay_pot', 'scale': 0.26},
        {'x': 13.4, 'y': 34.0, 'type': 'clay_pot', 'flip': True}, {'x': 14.2, 'y': 29.4, 'type': 'rocks'},
        {'x': 10.5, 'y': 33.5, 'type': 'crow'},
        # the slot: someone standing in the beam
        {'id': 'explorer', 'x': 18.5, 'y': 13.5, 'type': 'explorer', 'facing': 270},
    ]
    slot_lights = [{'type': 'sun', 'azimuth': 92, 'elevation': 70, 'intensity': 2.0}]
    sunset_lights = [{'type': 'sun', 'azimuth': 178, 'elevation': 7, 'intensity': 1.0}]
    return scene(
        g,
        legend={
            'R': {'wall': ROCK, 'h': 6.5, 'top': 'desert_wash'},
            'Q': {'wall': ROCK, 'h': 7.4, 'top': 'desert_wash'},
            'U': {'wall': ROCK, 'h': 5.6, 'top': 'desert_wash'},
            'Z': {'wall': 'slot_rock', 'h': 6.5, 'top': 'desert_wash'},
            'w': {'floor': 'desert_wash'},
            'S': {'floor': 'desert_wash', 'ceil': 'slot_rock'},
            'o': {'floor': 'desert_wash'},
            'p': {'wall': 'pueblo_stone', 'h': 1.2, 'top': 'pueblo_stone'},
            'P': {'wall': 'pueblo_stone', 'h': 2.3, 'top': 'pueblo_stone'},
            'D': {'wall': ['pueblo_door', 'pueblo_stone'], 'h': 1.2, 'top': 'pueblo_stone'},
            'T': {'wall': 'pueblo_stone', 'h': 2.8, 'top': 'pueblo_stone'},
            'r': {'wall': 'pueblo_stone', 'h': 0.55, 'top': 'pueblo_stone'},
        },
        title='Red canyon - a dry wash, a cliff dwelling and a slot canyon',
        sky='day',
        ceiling_height=5.6,
        ambient=[0.4, 0.36, 0.34],
        fog={'color': [0.78, 0.66, 0.56], 'density': 0.008},
        lights=[SUN],
        sprites=sprites,
        scatter=[{'of': 'desert', 'on': 'w', 'density': 0.25, 'sizes': {'tiny': 4, 'small': 3, 'medium': 1}, 'seed': 6}],
        camera={'x': 19.5, 'y': 56.4, 'angle': 270, 'fov': 66, 'height': 0.5},
        shots=[
            {'x': 19.5, 'y': 56.4, 'angle': 268,
             'overlays': [{'type': 'caption', 'text': 'Red canyon', 'at': 'top', 'box': True}]},
            {'x': 18.6, 'y': 33.6, 'look_at': [12.0, 29.0, 1.0], 'fov': 66},
            {'x': 18.6, 'y': 17.8, 'angle': 268, 'fov': 62,
             'overrides': {'lights': slot_lights, 'ambient': [0.34, 0.18, 0.1],
                           'fog': {'color': [0.3, 0.17, 0.09], 'density': 0.035, 'shafts': 9.0}}},
            {'x': 16.0, 'y': 50.0, 'look_at': [22.0, 38.0, 2.0], 'fov': 68,
             'overrides': {'sky': 'sunset', 'lights': sunset_lights, 'ambient': [0.34, 0.24, 0.26],
                           'fog': {'color': [0.6, 0.36, 0.3], 'density': 0.01}}},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(red_canyon().save(os.path.join(HERE, 'red_canyon.json')))

"""Moon base: a colony on the Moon - greenhouse domes glowing on the grey plain, habitat modules,
solar arrays turned to a low sun, a rover in its tracks, astronauts, and the Earth hanging in a
black sky.

Shows the Moon kit - `regolith` underfoot with `rover_tracks` decals, `dome` (a greenhouse lit
from inside; it glows), `hab_module`, `solar_array`, `rover` - with the `lander` on its pad, a
crater rim of `rock` round the plain at several heights, the `space` sky with an `earth` in
`sky_objects`, and the light of airless ground: a low, hard sun, long black shadows, no haze at
all. The last shot is the lunar night, the base lit by its windows and the earthlight.
Run:  python moon_base.py  -> writes moon_base.json next to this file.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

EARTH = {'type': 'earth', 'azimuth': 268, 'elevation': 17, 'size': 7, 'lit_from': 200, 'phase': 0.55}


def moon_base():
    g = Grid(44, 44, fill='g')                     # the plain
    rng = np.random.default_rng(4)
    for y in range(44):                            # a crater rim round it, ragged
        for x in range(44):
            edge = min(x, y, 43 - x, 43 - y)
            if edge <= 1 or (edge == 2 and rng.random() < 0.5):
                v = np.sin(x * 0.7 + y * 0.31) + np.sin(y * 0.53 - x * 0.2) + rng.normal(0, 0.4)
                g.put(x, y, 'U' if v < -0.6 else 'Q' if v > 0.7 else 'R')
    for x, y in ((12, 14), (30, 12), (8, 30), (33, 31), (20, 9)):
        g.put(x, y, 'r')                           # boulders on the plain
    sprites = [
        # the base: three domes, habitat modules between them, a row of solar arrays
        {'x': 19.0, 'y': 18.0, 'type': 'dome', 'scale': 3.2},
        {'x': 26.0, 'y': 20.5, 'type': 'dome', 'scale': 2.4},
        {'x': 14.0, 'y': 21.5, 'type': 'dome', 'scale': 2.0},
        {'x': 22.6, 'y': 23.2, 'type': 'hab_module'}, {'x': 17.0, 'y': 24.6, 'type': 'hab_module', 'flip': True},
        *[{'x': 30.0 + k * 2.3, 'y': 26.0 + k * 0.4, 'type': 'solar_array'} for k in range(4)],
        {'x': 11.0, 'y': 17.0, 'type': 'antenna'},
        {'x': 24.4, 'y': 26.2, 'type': 'sci_crate'}, {'x': 25.2, 'y': 26.6, 'type': 'sci_crate', 'scale': 0.3},
        # the pad and its lander; the rover and the crew
        {'x': 9.5, 'y': 26.5, 'type': 'lander'},
        {'id': 'rover', 'x': 21.0, 'y': 30.5, 'type': 'rover'},
        {'id': 'walker', 'x': 19.4, 'y': 31.4, 'type': 'astronaut', 'facing': 270},
        {'x': 23.4, 'y': 29.4, 'type': 'astronaut', 'facing': 200},
    ]
    decals = [{'tex': 'pad_marking', 'surface': 'floor', 'x': 9.5, 'y': 26.5, 'size': 3.2},
              {'tex': 'rover_tracks', 'surface': 'floor', 'x': 21.0, 'y': 33.5, 'size': 3.0},
              {'tex': 'rover_tracks', 'surface': 'floor', 'x': 21.0, 'y': 36.5, 'size': 3.0}]
    night_lights = [{'x': x, 'y': y, 'z': 0.6, 'radius': r, 'color': c, 'intensity': i}
                    for x, y, r, c, i in ((19.0, 18.8, 6.0, [0.9, 0.7, 1.0], 1.2), (26.0, 21.2, 4.5, [0.9, 0.7, 1.0], 1.0),
                                          (22.6, 23.6, 3.5, [1.0, 0.8, 0.5], 1.0), (17.0, 25.0, 3.5, [1.0, 0.8, 0.5], 1.0))]
    return scene(
        g,
        legend={
            'g': {'floor': 'regolith'},
            'R': {'wall': 'rock', 'h': 1.4, 'top': 'regolith'},
            'Q': {'wall': 'rock', 'h': 2.2, 'top': 'regolith'},
            'U': {'wall': 'rock', 'h': 0.8, 'top': 'regolith'},
            'r': {'wall': 'rock', 'h': 0.5, 'top': 'regolith'},
        },
        title='Moon base - a colony on the grey plain, the Earth overhead',
        sky='space',
        sky_objects=[EARTH],
        ambient=[0.07, 0.07, 0.09],
        lights=[{'type': 'sun', 'azimuth': 200, 'elevation': 9, 'intensity': 1.35, 'color': [1.0, 0.98, 0.95]}],
        sprites=sprites,
        decals=decals,
        scatter=[{'of': 'rocks', 'on': 'g', 'density': 0.12, 'sizes': {'tiny': 4, 'small': 2}, 'seed': 3}],
        camera={'x': 21.5, 'y': 39.0, 'angle': 270, 'fov': 66, 'height': 0.5},
        shots=[
            {'x': 21.5, 'y': 39.0, 'angle': 268,
             'overlays': [{'type': 'caption', 'text': 'Mare Serenitatis, day 412', 'at': 'bottom', 'box': True}]},
            {'x': 18.0, 'y': 34.6, 'look_at': 'rover', 'fov': 60},
            {'x': 21.5, 'y': 39.0, 'angle': 268,
             'overrides': {'lights': [{'type': 'moon', 'azimuth': 268, 'elevation': 17, 'intensity': 0.35}] + night_lights,
                           'ambient': [0.05, 0.06, 0.09]}},
            {'x': 20.0, 'y': 33.8, 'look_at': [18.6, 22.0, 2.2], 'fov': 62, 'height': 0.45},
        ],
        contact_shadows=0.6,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(moon_base().save(os.path.join(HERE, 'moon_base.json')))

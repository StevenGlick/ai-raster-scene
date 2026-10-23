"""The storm island: an island town on a stormy night at landscape scale - one of the three concept drawings this
project began from, made into a scene.

A map cell is about 100 m; the camera is on a ferry's deck in the harbour, 400 m out. Out of a dark sea
(`harbor_water`) rises a steep hill with a house on its flat top and a spire beside it (a `mountain` cut flat with
`top`), and behind the harbour a plateau (a `mountain` drawn out with `length`, its sides sheer with `cliff`)
carrying an institution, a factory with two chimneys smoking and a power station, lights along its edge (a
`warning_light` from `sprite_defs`). Down at the shore stand tenements (`tower`s) on a strip of sand, a row of
cottages (a `village` with no church), warehouses and a crane; a pier on piles (`beam`s on `column`s) runs out to a
`lighthouse` on its rock, its beam (a `searchlight`) sweeping the water, a red rowboat tied up by it. A storm comes
in (`storm_cloud`s) and lightning strikes the power station: a cold light there, and the fog's `glow` makes a halo
of it.
Run:  python storm_island.py  -> writes storm_island.json next to this file.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 52, 46
HILL_TOP = (25.53, 22.42, 2.52)            # the middle of the hill's flat top, and its height
PLATEAU = 1.45                             # the plateau's height; its top runs x 28.8-31.35, y 21.55-22.5
LIGHT = (28.97, 28.93)                     # the lighthouse
WARM = [1.0, 0.75, 0.45]
AMBER = [1.0, 0.55, 0.2]
STORM = [{'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 2.4, 'spread': 0.5},
         {'fx': 'grade', 'saturation': 0.85, 'contrast': 1.12, 'tint': [0.92, 0.97, 1.08]},
         {'fx': 'lightning', 'x': 0.665, 'amount': 0.08, 'y_end': 0.39}]


def land(x, y):
    """Whether the cell at x, y is the island: a rough oval, its south shore near y 27.5."""
    dx, dy = (x + 0.5 - 28.5) / 9.5, (y + 0.5 - 22.0) / 6.0
    return dx * dx + dy * dy + 0.08 * math.sin(x * 1.3) + 0.06 * math.sin(y * 1.7 + x) < 1.0


def storm_island():
    g = Grid(W, H, fill='~')
    for y in range(H):
        for x in range(W):
            if land(x, y):
                g.put(x, y, 'w')
    for y in range(H):                             # a rim of shingle where the land meets the sea
        for x in range(W):
            sea = [g.get(x + dx, y + dy) == '~' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if g.get(x, y) == 'w' and any(sea):
                g.put(x, y, 's')
    g.rect(26, 27, 27, 27, 'b')                    # the sand under the tenements
    g.rect(27, 26, 28, 26, 'c')                    # the cottages' lane
    g.put(28, 27, 'q')                             # the quay
    hx, hy, hz = HILL_TOP
    objects = [
        {'type': 'mountain', 'x': 25.6, 'y': 22.6, 'size': 2.6, 'height': 3.0, 'top': 0.84, 'ridges': 0,
         'rock': 'basalt', 'snowline': 0, 'seed': 2},
        {'type': 'mountain', 'x': 29.8, 'y': 22.0, 'size': 3.2, 'length': 9.0, 'height': PLATEAU, 'cliff': 0.6,
         'ridges': 0, 'rock': 'basalt', 'snowline': 0, 'seed': 8},
        # the house on the hill, and its spire
        {'type': 'tower', 'x': hx - 0.03, 'y': hy, 'z': hz, 'width': 0.32, 'depth': 0.24, 'height': 0.17,
         'style': 'brick', 'lit': 0.7, 'seed': 3},
        {'type': 'gable_roof', 'x': hx - 0.03, 'y': hy, 'z': hz + 0.17, 'length': 0.36, 'width': 0.28, 'rise': 0.12,
         'cover': 'slate', 'walls': 0},
        {'type': 'column', 'x': hx + 0.16, 'y': hy + 0.02, 'z': hz, 'sides': 4, 'radius': 0.045, 'height': 0.52,
         'top': 0.08, 'material': 'stone'},
        # on the plateau: the institution and its wing, the factory and its chimneys, the power station
        {'type': 'tower', 'x': 29.25, 'y': 22.0, 'z': PLATEAU, 'width': 0.7, 'depth': 0.38, 'height': 0.42,
         'style': 'brick', 'lit': 0.35, 'seed': 11},
        {'type': 'tower', 'x': 29.85, 'y': 22.05, 'z': PLATEAU, 'width': 0.36, 'depth': 0.32, 'height': 0.2,
         'style': 'brick', 'lit': 0.2, 'seed': 12},
        {'type': 'tower', 'x': 30.45, 'y': 21.9, 'z': PLATEAU, 'width': 0.55, 'depth': 0.36, 'height': 0.13,
         'style': 'dark', 'lit': 0.08, 'seed': 13},
        {'type': 'column', 'x': 30.3, 'y': 21.75, 'z': PLATEAU, 'radius': 0.04, 'top': 0.8, 'height': 0.6,
         'material': 'stone'},
        {'type': 'column', 'x': 30.62, 'y': 21.8, 'z': PLATEAU, 'radius': 0.04, 'top': 0.8, 'height': 0.55,
         'material': 'stone'},
        {'type': 'tower', 'x': 31.1, 'y': 22.0, 'z': PLATEAU, 'width': 0.4, 'depth': 0.36, 'height': 0.48,
         'style': 'dark', 'lit': 0.22, 'seed': 14},
        # the shore: tenements, cottages, warehouses and a crane
        {'type': 'tower', 'x': 26.4, 'y': 27.1, 'width': 0.34, 'depth': 0.28, 'height': 0.44, 'style': 'apartment',
         'lit': 0.25, 'seed': 21},
        {'type': 'tower', 'x': 26.85, 'y': 26.9, 'width': 0.34, 'depth': 0.28, 'height': 0.58, 'style': 'brick',
         'lit': 0.25, 'seed': 22},
        {'type': 'tower', 'x': 27.3, 'y': 27.15, 'width': 0.3, 'depth': 0.26, 'height': 0.38, 'style': 'apartment',
         'lit': 0.25, 'seed': 23},
        {'type': 'village', 'x': 27.95, 'y': 26.9, 'size': 0.75, 'count': 4, 'church': False, 'lit': 0.5, 'seed': 6,
         'scale': 2.0},
        {'type': 'tower', 'x': 30.0, 'y': 26.9, 'width': 0.6, 'depth': 0.32, 'height': 0.11, 'style': 'dark',
         'lit': 0.05, 'seed': 31},
        {'type': 'tower', 'x': 30.75, 'y': 26.7, 'width': 0.5, 'depth': 0.32, 'height': 0.09, 'style': 'dark',
         'lit': 0.05, 'seed': 32},
        {'type': 'column', 'x': 31.25, 'y': 26.9, 'sides': 4, 'radius': 0.016, 'height': 0.5, 'material': 'stone'},
        {'type': 'beam', 'x': 31.05, 'y': 26.9, 'z': 0.47, 'angle': 0, 'length': 0.7, 'width': 0.02, 'depth': 0.02,
         'material': 'stone'},
        # the lighthouse on its rock, and its beam
        {'type': 'lighthouse', 'x': LIGHT[0], 'y': LIGHT[1], 'z': 0.05, 'scale': 0.036},
        {'type': 'boulder', 'x': LIGHT[0], 'y': LIGHT[1], 'size': 0.4, 'height': 0.08, 'rock': 'basalt'},
        {'type': 'searchlight', 'x': LIGHT[0], 'y': LIGHT[1], 'z': 0.31, 'angle': 340, 'elevation': 1.5, 'length': 8,
         'width': 0.1, 'color': [0.92, 0.86, 0.66]},
    ]
    x0, y0, x1, y1 = 28.4, 27.95, LIGHT[0] - 0.08, LIGHT[1] - 0.14          # the pier, from the quay to the rock
    L, ang = math.hypot(x1 - x0, y1 - y0), math.degrees(math.atan2(y1 - y0, x1 - x0))
    objects.append({'type': 'beam', 'x': round((x0 + x1) / 2, 2), 'y': round((y0 + y1) / 2, 2), 'z': 0.03,
                    'angle': round(ang, 1), 'length': round(L, 2), 'width': 0.04, 'depth': 0.01, 'material': 'wood'})
    for k in range(6):
        t = k / 5
        objects.append({'type': 'column', 'x': round(x0 + t * (x1 - x0), 2), 'y': round(y0 + t * (y1 - y0), 2),
                        'z': -0.05, 'radius': 0.006, 'height': 0.08, 'sides': 6, 'material': 'wood'})
    red = [(29.0, 22.3), (30.15, 22.36), (31.2, 22.28)]
    sprites = ([{'x': x, 'y': y, 'z': PLATEAU + 0.04, 'type': 'warning_light'} for x, y in red]
               + [{'x': 31.1, 'y': 22.0, 'z': PLATEAU + 0.49, 'type': 'warning_light'},
                  {'x': 30.3, 'y': 21.75, 'z': PLATEAU + 0.6, 'type': 'smoke_plume', 'scale': 0.8},
                  {'x': 30.62, 'y': 21.8, 'z': PLATEAU + 0.55, 'type': 'smoke_plume', 'scale': 0.7},
                  {'x': 28.2, 'y': 29.75, 'type': 'rowboat', 'scale': 0.06, 'tint': [1.4, 0.6, 0.5]}]  # by the pier
               + [{'x': x, 'y': y, 'z': z, 'type': 'storm_cloud', 'scale': k}      # the storm coming in
                  for x, y, z, k in ((19.0, 3.0, 5.6, 5.5), (37.5, 1.5, 6.8, 6.5), (28.5, 5.0, 4.4, 4.2),
                                     (45.0, 6.0, 4.0, 4.0), (11.0, 7.0, 3.6, 3.8), (27.0, 0.5, 11.5, 8.0),
                                     (12.0, 1.0, 10.0, 7.0), (43.0, 0.5, 10.5, 7.5))])
    lights = ([{'x': x, 'y': y, 'z': PLATEAU + 0.1, 'radius': 0.5, 'color': AMBER, 'intensity': 0.5} for x, y in red]
              + [{'x': LIGHT[0], 'y': LIGHT[1], 'z': 0.31, 'radius': 1.6, 'color': [1.0, 0.9, 0.7], 'intensity': 0.9},
                 {'x': 27.9, 'y': 27.4, 'z': 0.2, 'radius': 1.2, 'color': WARM, 'intensity': 0.3},
                 {'x': 26.85, 'y': 27.4, 'z': 0.2, 'radius': 1.0, 'color': WARM, 'intensity': 0.25},
                 {'type': 'moon', 'azimuth': 70, 'elevation': 28, 'intensity': 0.18, 'disc': False},  # behind cloud
                 {'x': 31.2, 'y': 21.8, 'z': 2.6, 'radius': 3.2, 'color': [0.75, 0.82, 1.0], 'intensity': 1.0}])
    return scene(
        g,
        title='The storm island - an island town on a stormy night, at landscape scale',
        legend={
            '~': {'floor': 'harbor_water'},
            'w': {'floor': {'base': 'pasture', 'tint': [0.45, 0.5, 0.55]}},
            's': {'floor': {'base': 'shingle', 'tint': [0.7, 0.7, 0.75]}},
            'b': {'floor': {'base': 'white_sand', 'tint': [0.62, 0.6, 0.62]}},
            'c': {'floor': 'cobble'},
            'q': {'floor': 'quay'},
        },
        sky='storm',
        ambient=[0.16, 0.16, 0.21],
        lights=lights,
        fog={'color': [0.06, 0.07, 0.1], 'density': 0.008, 'glow': 0.6},
        reflections={'amount': 0.6, 'ripple': 1.8, 'smear': 1.5},       # a choppy sea
        objects=objects,
        sprites=sprites,
        sprite_defs={'warning_light': {'height': 0.1, 'palette': {'r': '#ffa040', 'd': '#7a3a10'}, 'emissive': 'r',
                                       'pixels': ['.r.', 'rrr', '.d.']}},
        camera={'x': 28.6, 'y': 31.5, 'angle': 267, 'fov': 64, 'height': 0.1},
        shots=[
            {'x': 28.6, 'y': 31.5, 'angle': 267, 'fov': 64, 'height': 0.1, 'pitch': 0.15, 'post': STORM},
            {'x': 28.92, 'y': 29.2, 'look_at': [25.9, 23.4, 1.3], 'fov': 62, 'height': 0.3, 'post': STORM},  # from the light
        ],
        max_distance=60,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(storm_island().save(os.path.join(HERE, 'storm_island.json')))

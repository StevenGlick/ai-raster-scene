"""Misty moor: a stone circle at dawn, mist lying in the hollows, the low sun cutting through.

Shows volumetric fog (a ground layer that thins with height and drifts in banks), shafts of
sunlight between the stones, long dawn shadows, and a character seen from behind (`facing`).
Run:  python misty_moor.py  -> writes misty_moor.json
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(44, 44, fill=',')
cx, cy = 22, 17
for k in range(11):                                   # a ring of standing stones...
    a = k * 2 * math.pi / 11 + 0.2
    g.put(int(round(cx + 6.2 * math.cos(a))), int(round(cy + 6.2 * math.sin(a))), 'S')
g.put(cx, cy, 'A')                                    # ...round a low altar stone
for (x, y) in ((8, 30), (33, 31), (36, 9), (6, 8)):
    g.put(x, y, 'S')                                  # a few strays out on the moor
heights = [list('.' * 44) for _ in range(44)]
heights[cy][cx] = '4'

s = scene(
    g,
    title='Misty moor - the stone circle at dawn',
    heights=[''.join(r) for r in heights],
    legend={
        ',': {'floor': 'grass'},
        'S': {'wall': 'moss_stone', 'h': 1.9},
        'A': {'wall': 'stone_dark', 'top': 'moss_stone'},
    },
    sky='dusk',
    skyline={'type': 'hills', 'height': 0.8},
    ambient=[0.3, 0.28, 0.32],
    lights=[{'type': 'sun', 'azimuth': 280, 'elevation': 6, 'color': [1.0, 0.78, 0.55], 'intensity': 0.8,
             'disc_size': 3.2}],
    fog={'color': [0.58, 0.55, 0.62], 'density': 0.01, 'ground': 0.4, 'height': 0.3, 'noise': 0.6, 'scale': 3.0,
         'shafts': 0.8},
    sprites=[
        {'id': 'wanderer', 'x': 22.3, 'y': 27.0, 'type': 'knight', 'facing': 280},
        {'x': 12.0, 'y': 25.0, 'type': 'dead_tree', 'scale': 2.4}, {'x': 31.0, 'y': 24.0, 'type': 'dead_tree', 'flip': True},
    ],
    scatter=[{'of': 'stones', 'on': ',', 'density': 0.12, 'sizes': ['tiny', 'small', 'medium'], 'seed': 3},
             {'of': ['grass_tuft', 'grass_tuft', 'fern'], 'on': ',', 'density': 0.35, 'clump': 1.4,
              'sizes': ['small', 'medium'], 'seed': 8}],
    camera={'x': 21.8, 'y': 31.0, 'look_at': [22.0, 6.0, 0.7], 'fov': 70},
    shots=[
        {'x': 21.8, 'y': 31.0, 'look_at': [22.0, 6.0, 0.7], 'fov': 70,
         'overlays': [{'type': 'caption', 'text': 'The stones at first light', 'at': 'top', 'box': True}]},
        {'x': 24.5, 'y': 20.5, 'look_at': [20.0, 4.0, 0.9], 'fov': 72},
        {'x': 31.0, 'y': 36.0, 'look_at': [20.0, 15.0, 0.4], 'fov': 66},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'misty_moor.json')))

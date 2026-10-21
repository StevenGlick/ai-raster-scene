"""Misty moor: a stone circle at dawn, mist lying in the hollows, the low sun cutting through.

Shows volumetric fog (a ground layer that thins with height and drifts in banks), shafts of
sunlight between the stones (`standing_stone` objects in 3D - rough slabs of different heights, leaning a
little, their tops sloping, broad faces turned into the circle; the altar a slab lying), long dawn
shadows, and a character seen from behind (`facing`).
Mossy `boulder`s lie out on the moor and in the grass at the foot of every shot.
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
stones = []
for k, (x, y) in enumerate([(x, y) for y in range(44) for x in range(44) if g.get(x, y) == 'S']):
    ring = math.hypot(x - cx, y - cy) < 8             # broad faces turned into the circle; the strays any way
    face = math.degrees(math.atan2(cy - y, cx - x)) if ring else 37.0 * k
    stones.append({'type': 'standing_stone', 'x': x + 0.5, 'y': y + 0.5, 'angle': round(face, 1),
                   'height': int('6789'[(k * 7 + x) % 4]) * 0.25,     # each stone its own height, 1.5 to 2.25
                   'size': 0.95 + 0.1 * (k % 3), 'seed': 80 + k, 'plants': 2, 'casts': True})
stones.append({'type': 'standing_stone', 'x': cx + 0.5, 'y': cy + 0.5, 'angle': 15, 'height': 0.45, 'size': 1.7,
               'depth': 0.9, 'seed': 99, 'casts': True})   # the altar, a slab lying

s = scene(
    g,
    title='Misty moor - the stone circle at dawn',
    legend={
        ',': {'floor': 'grass'},
        'S': {'floor': 'grass'},                      # where the stones stand (objects, below)
        'A': {'floor': 'grass'},
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
    objects=stones + [{'type': 'boulder', 'x': x, 'y': y, 'angle': a, 'size': s_, 'height': h_, 'seed': 60 + k, 'plants': n}
             for k, (x, y, a, s_, h_, n) in enumerate((
                 (20.5, 28.0, 20, 0.9, 0.5, 2), (23.5, 27.7, 200, 0.7, 0.38, 1),      # before the first shot
                 (23.0, 18.6, 120, 0.65, 0.36, 1),                                  # before the second, in the ring
                 (29.0, 33.4, 300, 1.2, 0.65, 2), (27.2, 31.0, 80, 0.6, 0.32, 0),   # before the third
                 (12.6, 20.8, 40, 1.0, 0.55, 1), (33.4, 22.6, 160, 1.3, 0.7, 2), (16.6, 9.4, 250, 0.9, 0.5, 1),
                 (28.2, 8.2, 10, 1.1, 0.6, 1), (9.6, 13.8, 300, 0.8, 0.45, 0), (36.0, 28.0, 90, 1.0, 0.55, 1),
                 (14.6, 31.8, 200, 0.9, 0.5, 1),
                 # and smaller ones where the scatter's boulders lay
                 (40.58, 19.8, 0, 0.92, 0.68, 0), (27.24, 20.66, 137, 0.92, 0.68, 0),
                 (24.32, 12.56, 274, 0.92, 0.68, 0), (9.47, 12.24, 51, 0.92, 0.68, 0),
                 (26.53, 29.63, 188, 0.92, 0.68, 0), (23.41, 24.7, 325, 0.92, 0.68, 0),
                 (43.4, 24.42, 102, 0.92, 0.68, 0), (25.29, 11.92, 239, 0.92, 0.68, 0),
                 (29.3, 19.58, 16, 0.92, 0.68, 0), (40.84, 31.44, 153, 0.92, 0.68, 0),
                 (17.35, 25.27, 290, 0.92, 0.68, 0), (39.35, 39.66, 67, 0.92, 0.68, 0)))],
    scatter=[{'of': 'rocks', 'on': ',', 'density': 0.12, 'sizes': ['tiny', 'small', 'medium'], 'seed': 3},
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

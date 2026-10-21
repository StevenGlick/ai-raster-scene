"""Basalt coast: a causeway of basalt columns at sunset - thousands of hexagons packed tight, stepping
down from the foot of a cliff into the sea, a stack or two standing high, organ pipes of basalt up the
cliff behind, the low sun throwing their shadows across the tops, surf where they meet the sea.

Shows `column` objects in a hexagonal grid (`sides` 6, `radius` across the corners) of `basalt` (dark
rock with its joints across each column at heights of its own), each `"casts": true` so the low sun's
shadow of one falls on the next; heights from a smooth slope plus a little noise, a few stacks; the
cliff a wall lined with `rock_wall` of basalt; the sea `deep_water` sunk and reflecting.
Run:  python basalt_coast.py  -> writes basalt_coast.json next to this file.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

R = 0.34                                           # a column's radius, across its corners
D = 2 * R * math.cos(math.pi / 6) + 0.05           # centre to centre: face to face, a dark joint between


def wave(x, y, k):
    """A smooth bump field: a few long sines at fixed phases, -1..1."""
    return (np.sin(x * 0.7 + 1.3 + k) * np.cos(y * 0.55 - 0.4 * k) + 0.6 * np.sin(x * 1.6 - y * 1.1 + 2.0 * k)) / 1.6


def basalt_coast():
    g = Grid(40, 46, fill='w')                     # the sea
    g.rect(0, 20, 39, 33, 'g')                     # the shingle under the cliff
    g.rect(0, 34, 39, 45, 'C')                     # the cliff
    rng = np.random.default_rng(7)
    objects = [{'type': 'rock_wall', 'x': 0, 'y': 0, 'lining': 'C', 'rock': 'basalt', 'depth': 0.9,
                'height': [4.4, 5.6], 'trim': 0.1, 'pieces': [1.2, 2.6], 'seed': 4}]
    stacks = [(16.9, 25.2, 0.8, 0.9), (22.8, 24.6, 0.7, 0.6)]      # (x, y, reach, rise)
    tops = {}
    for j in range(int(26 / (D * 0.866))):         # the causeway, out from the cliff's foot into the sea
        y = 33.4 - j * D * 0.866
        half = 3.6 - 1.6 * (33.4 - y) / 22 + 0.5 * wave(y, 0.0, 2.0)
        for i in range(-12, 13):
            x = 20.0 + i * D + (D / 2 if j % 2 else 0.0)
            if abs(x - 20.0 - 0.6 * math.sin(y * 0.3)) > half or rng.random() < 0.04:
                continue
            t = np.clip((33.4 - y) / 19.0, 0, 1)
            h = 1.5 * (1 - t) ** 1.3 - 0.12 + 0.22 * wave(x, y, 0.0) + rng.choice([-0.14, -0.06, 0.0, 0.08, 0.16])
            for sx, sy, reach, rise in stacks:
                d = math.hypot(x - sx, y - sy)
                if d < reach:
                    h += rise * (1 - d / reach) ** 0.4
            h = round(max(h, -0.12), 2)
            tops[(round(x, 2), round(y, 2))] = h
            objects.append({'type': 'column', 'x': round(x, 2), 'y': round(y, 2), 'z': -0.3, 'sides': 6, 'radius': R,
                            'height': round(h + 0.3, 2), 'material': 'basalt', 'casts': True, 'fill': 0.5,
                            'seed': int(rng.integers(1000))})
    for j in range(2):                             # organ pipes up the cliff, behind the causeway
        y = 34.3 - j * D * 0.866
        for i in range(-22, 23):
            x = 20.0 + i * D + (D / 2 if j % 2 else 0.0)
            if abs(x - 20.0) > 9.0 + 2.0 * wave(x, 0.0, 1.0):
                continue
            h = 4.6 - 1.4 * abs(x - 20.0) / 9.0 + 0.9 * wave(x * 1.7, y, 3.0) + rng.uniform(-0.35, 0.35) - 0.6 * j
            objects.append({'type': 'column', 'x': round(x, 2), 'y': round(y, 2), 'z': -0.3, 'sides': 6, 'radius': R,
                            'height': round(h + 0.3, 2), 'material': 'basalt', 'casts': True,
                            'seed': int(rng.integers(1000))})
    stand = min(tops, key=lambda p: math.hypot(p[0] - 20.4, p[1] - 17.2))
    sprites = [
        {'id': 'explorer', 'x': stand[0], 'y': stand[1], 'z': tops[stand], 'type': 'explorer', 'facing': 250},
        {'x': 17.0, 'y': 12.0, 'type': 'seagull', 'z': 3.0}, {'x': 23.5, 'y': 9.0, 'type': 'seagull', 'z': 4.2, 'flip': True},
        {'x': 26.0, 'y': 16.0, 'type': 'seagull', 'z': 2.2},
    ]
    for x in np.arange(0.4, 40.0, 0.55):           # spent waves on the shingle, and round the causeway's end
        if abs(x - 20.0) < 4.2:
            continue
        sprites.append({'x': round(float(x), 2), 'y': round(19.8 - rng.uniform(0, 0.4), 2), 'type': 'surf',
                        'scale': round(rng.uniform(0.09, 0.13), 3), 'flip': bool(rng.random() < 0.5)})
    return scene(
        g,
        legend={
            'w': {'floor': 'sea', 'drop': 0.2, 'reflect': 0.45},
            'g': {'floor': 'gravel'},
            'C': {'wall': 'rock', 'h': 4.4, 'top': 'grass'},
        },
        title='Basalt coast - the causeway at sunset',
        sky='sunset',
        skyline={'type': 'islands', 'count': 3},
        ambient=[0.34, 0.32, 0.38],
        lights=[{'type': 'sun', 'azimuth': 205, 'elevation': 16, 'color': [1.0, 0.72, 0.5], 'intensity': 1.05,
                 'disc_size': 3.0}],
        fog={'color': [0.74, 0.6, 0.56], 'density': 0.008, 'shafts': 0.5},
        sprites=sprites,
        objects=objects,
        camera={'x': 20.0, 'y': 31.0, 'height': 1.8, 'look_at': [18.4, 14.0, -0.4], 'fov': 70},
        shots=[
            {'x': 20.0, 'y': 31.0, 'height': 1.8, 'look_at': [18.4, 14.0, -0.4], 'fov': 70,
             'overlays': [{'type': 'caption', 'text': 'The causeway at sunset', 'at': 'top', 'box': True}]},
            {'x': 20.6, 'y': 13.4, 'height': 0.55, 'look_at': [19.6, 30.0, 1.4], 'fov': 70},
            {'x': 21.4, 'y': 21.6, 'height': 2.6, 'look_at': [20.2, 18.4, -0.2], 'fov': 64},
        ],
        contact_shadows=0.4,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(basalt_coast().save(os.path.join(HERE, 'basalt_coast.json')))

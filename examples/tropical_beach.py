"""Tropical beach: a lagoon at sunset, a pier, a hut on the sand, the jungle behind.

Shows the beach textures and props: sand, wet sand and clear turquoise shallows over deeper
blue water that mirrors the sky, palms leaning out over the beach, a bamboo hut with thatched
eaves and torches, a palm grove and a campsite (all prefabs), surf along the waterline, and the
same beach at noon and after dark, when the surf glows.
Run:  python tropical_beach.py  -> writes tropical_beach.json
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 50, 46
rnd = random.Random(21)
g = Grid(W, H, fill=',')                              # dry sand


def shore(y):
    """The waterline: the first column of sand in row y."""
    return int(round(16 + 3.5 * math.sin(y * 0.16 + 0.6)))


for y in range(H):
    xs = shore(y)
    for x in range(xs):
        g.put(x, y, '~' if x < xs - 7 else 's')       # deep water, then the shallows
    g.put(xs, y, 'w')                                 # the wet band the waves keep reaching
for x in range(4, shore(22) + 1):                     # the pier, out into the lagoon
    g.put(x, 22, 'J').put(x, 23, 'J')
for y in range(H):                                    # the jungle behind the beach
    edge = int(40 + 2.5 * math.sin(y * 0.35) + 1.5 * math.sin(y * 0.9))
    for x in range(edge, W):
        g.put(x, y, 'F')
for y in range(0, 6):                                 # a rocky point at the north end
    for x in range(shore(y) - 2, shore(y) + 7 - y):
        if rnd.random() < 0.85:
            g.put(x, y, 'R')

legend = {
    ',': {'floor': 'beach_sand'},
    'w': {'floor': 'wet_sand'},
    's': {'floor': 'shallows'},
    '~': {'floor': 'sea'},
    'J': {'wall': 'boards', 'h': 0.16, 'top': 'boards'},
    'F': {'wall': 'jungle_leaves', 'h': 2.8, 'top': 'canopy_top'},
    'R': {'wall': {'base': 'limestone', 'tint': [0.5, 0.47, 0.44]}, 'h': 0.9, 'top': {'base': 'limestone', 'tint': [0.5, 0.47, 0.44]}},
}

sprites = [
    {'id': 'castaway', 'x': 13.5, 'y': 27.8, 'type': 'castaway', 'facing': 180},
    {'x': 14.6, 'y': 32.9, 'type': 'palm_lean', 'scale': 3.4},
    {'x': 21.5, 'y': 34.6, 'type': 'canoe', 'scale': 0.32},
    {'x': 24.0, 'y': 25.4, 'type': 'hammock'},
    {'x': 20.5, 'y': 24.6, 'type': 'palm_lean', 'scale': 3.4},
    {'x': 22.0, 'y': 36.6, 'type': 'palm_lean', 'flip': True},
    {'x': 25.2, 'y': 23.6, 'type': 'palm'}, {'x': 24.4, 'y': 27.4, 'type': 'palm', 'scale': 3.6, 'flip': True},
    {'x': 27.0, 'y': 9.0, 'type': 'palm', 'flip': True}, {'x': 30.0, 'y': 31.0, 'type': 'palm', 'scale': 3.5},
    {'x': 36.5, 'y': 37.0, 'type': 'palm', 'flip': True},
    {'x': 23.5, 'y': 6.5, 'type': 'palm_lean', 'scale': 3.2}, {'x': 33.0, 'y': 41.5, 'type': 'palm_lean'},
    {'x': 26.0, 'y': 18.8, 'type': 'coconuts'}, {'x': 23.2, 'y': 31.8, 'type': 'coconuts'},
    {'x': 20.4, 'y': 33.0, 'type': 'crab'}, {'x': 23.0, 'y': 12.2, 'type': 'crab', 'flip': True},
    {'x': 22.8, 'y': 39.0, 'type': 'driftwood'},
    {'x': 9.0, 'y': 30.0, 'z': 2.4, 'type': 'seagull'}, {'x': 6.0, 'y': 26.5, 'z': 3.1, 'type': 'seagull', 'flip': True},
    {'x': 11.5, 'y': 19.0, 'z': 2.0, 'type': 'seagull', 'scale': 0.12},
]
def surf(kind):
    """A line of spent waves along the waterline, staggered so it never looks ruled."""
    out = []
    for i in range(H * 2):
        y = i / 2 + rnd.random() * 0.4
        out.append({'x': round(shore(int(y)) - 0.15 - rnd.random() * 0.5, 2), 'y': round(y, 2),
                    'type': kind, 'scale': round(rnd.uniform(0.09, 0.13), 3), 'flip': rnd.random() < 0.5})
    return out


sprites += surf('surf')
# the hut (its door to the sea), torches by the hammock, a grove and a crowned palm behind
prefabs = [{'type': 'beach_hut', 'x': 31.5, 'y': 14.5, 'angle': 180},
           {'type': 'tiki_torches', 'x': 22.6, 'y': 23.0},
           {'type': 'palm_grove', 'x': 35.5, 'y': 21.5, 'seed': 4},
           {'type': 'palm_3d', 'x': 34.4, 'y': 10.2, 'seed': 2}]
decals = [{'tex': 'starfish', 'surface': 'floor', 'x': 20.3, 'y': 31.7, 'size': 0.45},
          {'tex': 'shells', 'surface': 'floor', 'x': 21.4, 'y': 28.2, 'size': 0.5},
          {'tex': 'seaweed', 'surface': 'floor', 'x': shore(36) + 0.8, 'y': 36.2, 'size': 0.9},
          {'tex': 'shells', 'surface': 'floor', 'x': shore(16) + 1.2, 'y': 16.5, 'size': 0.45}]
for y in range(0, H, 2):                              # foam where each wave runs out
    decals.append({'tex': 'foam', 'surface': 'floor', 'x': shore(y) + 0.3, 'y': y + 1.0, 'size': 2.2})

s = scene(
    g,
    title='Tropical beach - the lagoon at sunset',
    ceiling_height=1.0,
    legend=legend,
    sky='sunset',
    skyline={'type': 'islands', 'count': 7},
    ambient=[0.36, 0.3, 0.34],
    lights=[{'type': 'sun', 'azimuth': 186, 'elevation': 4, 'color': [1.0, 0.7, 0.45], 'intensity': 0.95,
             'disc_size': 3.4}],
    fog={'color': [0.78, 0.52, 0.5], 'density': 0.003},
    sprites=sprites,
    prefabs=prefabs,
    decals=decals,
    scatter=[{'of': 'beach', 'on': ',', 'density': 0.05, 'sizes': ['tiny', 'small'], 'seed': 2},
             {'of': ['dry_tuft', 'dry_tuft', 'fern'], 'on': ',', 'density': 0.07, 'clump': 2.0,
              'sizes': ['small', 'medium'], 'seed': 6}],
    camera={'x': 17.6, 'y': 30.4, 'height': 0.75, 'look_at': [-14.0, 27.5, 1.0], 'fov': 70},
    shots=[
        {'x': 17.6, 'y': 30.4, 'height': 0.75, 'look_at': [-14.0, 27.5, 1.0], 'fov': 70,
         'overlays': [{'type': 'caption', 'text': 'The lagoon at sunset', 'at': 'top', 'box': True}]},
        {'x': 5.5, 'y': 23.0, 'height': 0.68, 'look_at': [30.0, 15.5, 1.0], 'fov': 70},
        {'x': 20.0, 'y': 34.5, 'height': 0.4, 'look_at': [18.0, 20.0, 0.9], 'fov': 74,
         'overrides': {'sky': 'day', 'ambient': [0.42, 0.42, 0.46],
                       'lights': [{'type': 'sun', 'azimuth': 150, 'elevation': 58, 'intensity': 0.8}],
                       'fog': {'color': [0.7, 0.82, 0.9], 'density': 0.004}}},
        {'x': 24.0, 'y': 40.5, 'look_at': [14.0, 23.2, 0.6], 'fov': 80,
         'overrides': {'sky': 'night', 'ambient': [0.08, 0.09, 0.14],
                       'lights': [{'type': 'moon', 'azimuth': 200, 'elevation': 18, 'intensity': 0.5, 'disc_size': 2.6}],
                       'prefabs': prefabs + [{'type': 'campsite', 'x': 24.5, 'y': 36.0, 'seed': 1}],
                       'decals': [{'tex': 'foam_glow', 'surface': 'floor', 'x': shore(y) + 0.3, 'y': y + 1.0, 'size': 2.4}
                                  for y in range(0, H, 2)],
                       'fog': {'color': [0.06, 0.08, 0.14], 'density': 0.012, 'glow': 0.7}},
         'extra_sprites': [{'x': 23.4, 'y': 35.3, 'type': 'castaway', 'facing': 20}] + surf('surf_glow')},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tropical_beach.json')))

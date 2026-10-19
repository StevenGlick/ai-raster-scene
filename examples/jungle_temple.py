"""Jungle temple: a stepped pyramid swallowed by the rainforest, reached by a path under the canopy.

Shows the jungle textures, plants and animals, a `fringe` of layered foliage cards in front of
every face of the jungle (bushes at the front, a dense wall of trees at the back), plants as
crossed planes, prefabs, sunlight falling in shafts through holes in a leaf ceiling, ground
mist, a pyramid built from the heights layer and wall stacks (a cornice on the top storey of
every tier), giant trees standing clear of a rolling canopy, and a view from the top of the
pyramid out over it all.
Run:  python jungle_temple.py  -> writes jungle_temple.json
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 56, 62
g = Grid(W, H, fill='J')                              # jungle everywhere...
g.disc(27, 15, 17.6, ',')                             # ...but the clearing round the temple
g.rect(19, 21, 35, 31, 'p')                           # the plaza in front of it
g.rect(24, 23, 30, 28, '~')                           # a long still pool that mirrors the pyramid
# the path in from the south under the canopy, with a few holes for the sun: five cells wide,
# so with the fringe a cell deep down each side, three stay clear underfoot
PATH = [(28, 61), (27, 54), (25, 48), (25, 42), (27, 37), (27, 31)]
for (x0, y0), (x1, y1) in zip(PATH, PATH[1:]):
    n = 2 * max(abs(x1 - x0), abs(y1 - y0))
    for i in range(n + 1):
        g.disc(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), 2.6, 'c')
for x, y in ((27, 56), (25, 50), (25, 44), (27, 38)):
    g.put(x, y, 'o').put(x + 1, y, 'o')
for x, y in ((23, 46), (29, 51), (22, 40), (30, 41), (25, 58), (31, 57)):
    g.put(x, y, 'T')                                  # giant trunks beside the path

# the pyramid: four tiers a unit high and two cells deep, stairs up the south face, a shrine on top
X0, Y0, X1, Y1 = 18, 2, 36, 19
TIER = 'ABEF'
heights = [['.'] * W for _ in range(H)]
for y in range(Y0, Y1 + 1):
    for x in range(X0, X1 + 1):
        tier = min(min(x - X0, X1 - x, y - Y0, Y1 - y) // 2, 3)
        roots = x >= X1 - 1 and 6 <= y <= 15 or y <= Y0 + 1 and 22 <= x <= 26
        g.put(x, y, 'X' if roots else TIER[tier])
        heights[y][x] = str(2 * (tier + 1))
for k in range(8):                                    # stairs: half a unit a step
    for x in (26, 27, 28):
        g.put(x, Y1 - k, 'S')
        heights[Y1 - k][x] = str(k + 1)
for x in (24, 25, 29, 30):
    g.put(x, Y1, 'G').put(x, Y1 - 1, 'G')             # glyph panels flanking the foot of the stairs
for x in range(24, 31):
    for y in (9, 10, 11):
        g.put(x, y, 'R')                              # the shrine
        heights[y][x] = '.'
g.put(27, 11, 'D')                                    # its doorway, facing the stairs
for x in range(25, 30):
    g.put(x, 9, 'C')                                  # the roof comb along its back

# the canopy rolls: jungle walls from 2.5 to 4 units in small steps, in broad swells
CANOPY = 'JKLMNO'
for y in range(H):
    for x in range(W):
        if g.get(x, y) == 'J':
            swell = math.sin(x * 0.31 + 1.3) + math.sin(y * 0.27 + 0.4) + 0.6 * math.sin((x + y) * 0.53)
            g.put(x, y, CANOPY[min(5, max(0, int((swell + 1.8) * 1.6)))])

# tree crowns along the top of the canopy, thick near the clearing, so its edge is a line of
# rounded crowns against the sky and the view from the pyramid is a sea of them
rnd = random.Random(5)
crowns = []
for y in range(H):
    for x in range(W):
        c = g.get(x, y)
        near = math.hypot(x - 27, y - 15) < 21 or x > 36 and abs(y - 15) < 16
        if c in CANOPY and rnd.random() < (0.42 if near else 0.1):
            crowns.append({'x': round(x + rnd.random(), 2), 'y': round(y + rnd.random(), 2),
                           'z': round(2.05 + 0.3 * CANOPY.index(c), 2), 'type': 'canopy_crown',
                           'scale': round(rnd.uniform(1.0, 1.7), 2), 'flip': rnd.random() < 0.5})

stone = ['temple_stone'] * 4
paving = {'base': 'ruin_paving', 'tint': [0.8, 0.88, 0.78]}
s = scene(
    g,
    title='Jungle temple - the pyramid in the rainforest',
    height_unit=0.5,
    heights=[''.join(r) for r in heights],
    ceiling_height=2.5,
    legend={
        **{c: {'wall': 'jungle_leaves', 'h': 2.5 + 0.3 * i, 'top': 'canopy_top', 'fringe': 'jungle'}
           for i, c in enumerate(CANOPY)},
        'T': {'wall': 'jungle_bark', 'h': 3.4, 'top': 'canopy_top'},
        ',': {'floor': 'jungle_floor'},
        'c': {'floor': 'jungle_floor', 'ceil': 'canopy'},
        'o': {'floor': 'jungle_floor'},
        'p': {'floor': paving},
        '~': {'floor': {'base': 'shallows', 'tint': [0.42, 0.6, 0.5]}, 'drop': 0.14, 'reflect': 0.75},
        'A': {'wall': ['temple_cornice'], 'top': 'temple_stone'},
        'B': {'wall': stone[:1] + ['temple_cornice'], 'top': 'temple_stone'},
        'E': {'wall': stone[:2] + ['temple_cornice'], 'top': 'temple_stone'},
        'F': {'wall': stone[:3] + ['temple_cornice'], 'top': paving},
        'X': {'wall': 'temple_roots', 'top': 'temple_stone'},
        'S': {'wall': 'temple_stone', 'top': 'temple_stone'},
        'G': {'wall': 'glyphs', 'top': 'temple_stone'},
        'R': {'wall': stone + ['glyphs', 'temple_cornice'], 'h': 6.0, 'top': 'temple_stone'},
        'D': {'wall': stone + ['temple_door', 'temple_cornice'], 'h': 6.0, 'top': 'temple_stone'},
        'C': {'wall': stone + ['glyphs', 'temple_cornice', 'roof_comb'], 'h': 7.0, 'top': 'temple_stone'},
    },
    sky='day',
    skyline=[{'type': 'mountains', 'height': 0.8}, {'type': 'jungle', 'height': 1.0}],
    ambient=[0.3, 0.33, 0.27],
    lights=[{'type': 'sun', 'azimuth': 120, 'elevation': 50, 'color': [1.0, 0.92, 0.74], 'intensity': 1.0},
            {'x': 27.5, 'y': 12.3, 'z': 4.4, 'radius': 2.2, 'color': [1.0, 0.6, 0.3], 'intensity': 0.8}],
    fog={'color': [0.66, 0.74, 0.66], 'density': 0.008, 'ground': 0.22, 'height': 0.3, 'noise': 0.5, 'scale': 3.5,
         'shafts': 1.6, 'glow': 0.3},
    sprites=[
        {'id': 'explorer', 'x': 25.6, 'y': 47.5, 'type': 'explorer', 'facing': 270},
        {'x': 20.6, 'y': 21.8, 'type': 'stone_head'},
        {'x': 34.4, 'y': 21.8, 'type': 'stone_head', 'flip': True},
        {'x': 24.5, 'y': 30.3, 'type': 'stela'},
        {'x': 30.5, 'y': 30.3, 'type': 'stela', 'flip': True},
        {'id': 'macaw', 'x': 30.62, 'y': 30.25, 'z': 2.08, 'type': 'macaw', 'flip': True},
        {'id': 'jaguar', 'x': 27.5, 'y': 19.45, 'z': 0.5, 'type': 'jaguar', 'scale': 0.42},
        {'x': 15.0, 'y': 4.0, 'type': 'kapok'}, {'x': 41.5, 'y': 6.0, 'type': 'kapok', 'flip': True},
        {'x': 9.0, 'y': 22.0, 'type': 'kapok', 'scale': 6.4}, {'x': 46.0, 'y': 25.0, 'type': 'kapok', 'scale': 6.8},
        {'x': 12.0, 'y': 40.0, 'type': 'kapok', 'scale': 7.0}, {'x': 44.0, 'y': 44.0, 'type': 'kapok', 'flip': True},
        {'x': 17.6, 'y': 21.5, 'type': 'liana'}, {'x': 38.4, 'y': 20.0, 'type': 'liana', 'flip': True},
        {'x': 13.2, 'y': 12.0, 'type': 'liana', 'scale': 2.8}, {'x': 41.6, 'y': 14.0, 'type': 'liana', 'scale': 2.8},
        {'x': 23.9, 'y': 44.5, 'type': 'liana', 'scale': 2.2}, {'x': 29.1, 'y': 39.5, 'type': 'liana', 'scale': 2.2},
        {'x': 18.2, 'y': 26.0, 'type': 'banana_plant'}, {'x': 37.0, 'y': 27.5, 'type': 'banana_plant', 'flip': True},
        {'x': 16.0, 'y': 17.0, 'type': 'tree_fern'}, {'x': 39.6, 'y': 11.5, 'type': 'tree_fern', 'flip': True},
        {'x': 19.4, 'y': 29.5, 'type': 'heliconia'}, {'x': 36.0, 'y': 30.8, 'type': 'heliconia', 'flip': True},
        {'x': 23.2, 'y': 51.0, 'type': 'monstera'}, {'x': 29.8, 'y': 45.5, 'type': 'monstera', 'flip': True},
    ] + crowns,
    decals=[
        {'tex': 'lily_pads', 'surface': 'floor', 'x': 24.9, 'y': 27.4, 'size': 1.4},
        {'tex': 'lily_pads', 'surface': 'floor', 'x': 29.4, 'y': 24.2, 'size': 1.2},
        {'tex': 'lily_pads', 'surface': 'floor', 'x': 25.2, 'y': 23.8, 'size': 1.0},
        {'tex': 'vines', 'surface': 'wall', 'cell': [24, 19], 'face': 'south', 'u': 0.5, 'z': 0.9, 'size': 1.0},
        {'tex': 'vines', 'surface': 'wall', 'cell': [33, 17], 'face': 'south', 'u': 0.4, 'z': 1.9, 'size': 1.1},
        {'tex': 'moss_patch', 'surface': 'wall', 'cell': [21, 17], 'face': 'south', 'u': 0.5, 'z': 1.4, 'size': 1.0},
    ],
    scatter=[{'of': 'jungle', 'on': ',', 'density': 0.32, 'clump': 1.5, 'sizes': ['small', 'medium', 'large'], 'seed': 4},
             {'of': ['fern', 'fern', 'bromeliad', 'mushrooms'], 'on': 'co', 'density': 0.3, 'clump': 1.2,
              'sizes': ['tiny', 'small', 'medium'], 'seed': 7}],
    camera={'x': 26.5, 'y': 53.5, 'look_at': [26.0, 30.0, 1.0], 'fov': 70},
    shots=[
        {'x': 26.5, 'y': 53.5, 'look_at': [26.0, 30.0, 1.0], 'fov': 70},
        {'x': 27.5, 'y': 30.2, 'look_at': [27.5, 9.0, 2.6], 'fov': 80,
         'overlays': [{'type': 'caption', 'text': 'The temple of the jaguar', 'at': 'top', 'box': True}]},
        {'x': 27.5, 'y': 22.2, 'height': 0.72, 'look_at': [27.5, 11.0, 3.8], 'fov': 64},
        {'x': 28.4, 'y': 13.6, 'height': 4.5, 'look_at': [62.0, 19.0, 3.4], 'fov': 72,
         'extra_sprites': [{'x': 30.55, 'y': 13.9, 'z': 4.0, 'type': 'explorer', 'facing': 10}]},
    ],
    prefabs=[{'type': 'jungle_clump', 'x': 20.0, 'y': 31.5, 'seed': 1}, {'type': 'jungle_clump', 'x': 35.2, 'y': 31.6, 'seed': 2},
             {'type': 'jungle_clump', 'x': 13.5, 'y': 19.0, 'seed': 3}, {'type': 'jungle_clump', 'x': 41.0, 'y': 17.5, 'seed': 4},
             {'type': 'fern_bed', 'x': 24.0, 'y': 34.6, 'seed': 5}, {'type': 'fern_bed', 'x': 31.0, 'y': 34.8, 'seed': 6},
             {'type': 'shrine', 'x': 33.2, 'y': 21.8, 'angle': 0}],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jungle_temple.json')))

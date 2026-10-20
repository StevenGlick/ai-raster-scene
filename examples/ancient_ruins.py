"""Ancient ruins: a Doric temple on a headland above the sea, at golden hour and by moonlight.

Shows the ruin textures and props: a see-through colonnade built as wall stacks (shaft, shaft,
capital and entablature), columns snapped off and fallen, a collapsing cella, free-standing
columns along a sacred way and in fallen groups (prefabs), cypresses and olives, the low sun throwing the colonnade's shadow in
stripes, and shafts of light between the columns.
Run:  python ancient_ruins.py  -> writes ancient_ruins.json
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.5}  # the lights glow

W, H = 50, 44
rnd = random.Random(11)
g = Grid(W, H, fill=',')                              # dry grass over the headland
heights = [['.'] * W for _ in range(H)]
for y in range(H):                                    # the sea to the west, past a rocky edge
    coast = int(7 + 2.2 * math.sin(y * 0.33) + 1.2 * math.sin(y * 0.81 + 1.0))
    for x in range(coast):
        g.put(x, y, '~')
    for x in (coast, coast + 1):
        if rnd.random() < 0.8:
            g.put(x, y, 'K')
            heights[y][x] = str(rnd.choice([2, 3, 3, 4, 5]))

# the temple: a stepped base, a colonnade round the edge, the cella inside; the entrance faces east
TX0, TY0, TX1, TY1 = 20, 16, 33, 23
for ring, h in ((2, '1'), (1, '2')):
    for y in range(TY0 - ring, TY1 + ring + 1):
        for x in range(TX0 - ring, TX1 + ring + 1):
            g.put(x, y, 'B')
            heights[y][x] = h
for y in range(TY0, TY1 + 1):
    for x in range(TX0, TX1 + 1):
        g.put(x, y, 'B')
        heights[y][x] = '3'
for y in range(TY0, TY1 + 1):
    for x in range(TX0, TX1 + 1):
        if x in (TX0, TX1) or y in (TY0, TY1):
            r = rnd.random()
            # most columns stand; on the sea side more have fallen
            fallen = 0.32 if x < 26 else 0.12
            g.put(x, y, 'P' if r > fallen else ('b' if r > fallen * 0.45 else 'B'))
            heights[y][x] = '.' if g.get(x, y) != 'B' else '3'
for y in range(TY0 + 2, TY1 - 1):
    for x in range(TX0 + 3, TX1 - 2):
        if x in (TX0 + 3, TX1 - 3) or y in (TY0 + 2, TY1 - 2):
            g.put(x, y, 'L' if x > TX0 + 5 else 'l')  # the cella; its west end has half fallen
            heights[y][x] = '.'
for y in (19, 20):
    g.put(TX1 - 3, y, 'B')                            # its doorway, toward the sunrise
    heights[y][TX1 - 3] = '3'

# the sacred way, east from the temple steps to an altar
for x in range(TX1 + 3, W):
    for y in (19, 20):
        g.put(x, y, 'p')
g.put(40, 19, 'A').put(40, 20, 'A')
heights[19][40] = heights[20][40] = '5'

legend = {
    ',': {'floor': 'dry_grass'},
    'p': {'floor': 'ruin_paving'},
    '~': {'floor': 'sea', 'drop': 0.25},
    'K': {'wall': {'base': 'limestone', 'tint': [0.82, 0.8, 0.76]}, 'top': 'limestone'},
    'B': {'wall': 'limestone', 'top': 'ruin_paving'},
    'A': {'wall': 'limestone', 'top': 'limestone'},
    'P': {'wall': ['colonnade', 'colonnade', 'colonnade_top'], 'h': 3.0, 'floor': 'ruin_paving'},
    'b': {'wall': ['colonnade', 'colonnade_broken'], 'h': 2.0, 'floor': 'ruin_paving'},
    'L': {'wall': 'limestone', 'h': 2.6, 'top': 'limestone'},
    'l': {'wall': 'limestone', 'h': 1.2, 'top': 'limestone'},
}

sprites = [
    {'id': 'hoplite', 'x': 34.6, 'y': 21.4, 'type': 'hoplite', 'facing': 0},
    {'id': 'head', 'x': 37.0, 'y': 27.6, 'type': 'marble_head'},
    {'id': 'goat', 'x': 34.4, 'y': 29.2, 'type': 'goat', 'flip': True},
    {'x': 31.0, 'y': 27.5, 'type': 'goat'},
    {'x': 40.5, 'y': 19.95, 'z': 0.5, 'type': 'brazier', 'scale': 0.55},
]
for x, broken in ((37.5, False), (43.5, True), (46.5, False)):          # columns along the sacred way
    for y in (18.2, 21.8):
        sprites.append({'x': x, 'y': y, 'type': 'broken_column' if broken or rnd.random() < 0.3 else 'column',
                        'scale': 3.0, 'flip': rnd.random() < 0.5})
for x, y in ((24.5, 26.6), (27.0, 27.4), (19.0, 25.5), (31.5, 13.0), (23.0, 12.6), (36.6, 24.8)):
    sprites.append({'x': x, 'y': y, 'type': 'column_drum', 'flip': rnd.random() < 0.5})
for x, y, sc in ((17.0, 11.0, 4.2), (21.0, 9.5, 3.6), (28.0, 10.0, 4.4), (34.5, 11.5, 3.8), (38.0, 14.5, 4.0),
                 (14.5, 27.0, 3.4), (44.0, 13.0, 4.2), (44.5, 26.0, 3.6)):
    sprites.append({'x': x, 'y': y, 'type': 'cypress', 'scale': sc})
for x, y in ((30.0, 33.0), (37.0, 35.5), (24.0, 36.0), (43.0, 33.0), (16.0, 33.5)):
    sprites.append({'x': x, 'y': y, 'type': 'olive_tree', 'flip': rnd.random() < 0.5})
for x, y in ((36.2, 28.4), (38.1, 28.0), (35.4, 26.6), (33.2, 27.8)):
    sprites.append({'x': x, 'y': y, 'type': 'poppies'})

s = scene(
    g,
    title='Ancient ruins - the temple on the headland',
    heights=[''.join(r) for r in heights],
    legend=legend,
    sky='golden',
    skyline={'type': 'islands', 'count': 6},
    ambient=[0.34, 0.31, 0.32],
    lights=[{'type': 'sun', 'azimuth': 172, 'elevation': 9, 'color': [1.0, 0.8, 0.56], 'intensity': 1.05,
             'disc_size': 3.0}],
    fog={'color': [0.66, 0.56, 0.46], 'density': 0.005, 'shafts': 0.9, 'ground': 0.1, 'height': 0.3},
    sprites=sprites,
    scatter=[{'of': 'ruins', 'on': ',', 'density': 0.1, 'sizes': ['tiny', 'small', 'medium'], 'seed': 3},
             {'of': ['dry_tuft', 'dry_tuft', 'poppies', 'rocks'], 'on': ',', 'density': 0.22, 'clump': 1.5,
              'sizes': ['small', 'medium'], 'seed': 9}],
    camera={'x': 48.9, 'y': 20.0, 'look_at': [26.0, 19.8, 1.5], 'fov': 64},
    shots=[
        {'x': 48.9, 'y': 20.0, 'look_at': [26.0, 19.8, 1.5], 'fov': 64,
         'overlays': [{'type': 'caption', 'text': 'The temple on the headland', 'at': 'top', 'box': True}]},
        {'x': 28.6, 'y': 19.5, 'height': 0.8, 'look_at': [12.0, 20.2, 1.3], 'fov': 74},
        {'x': 39.8, 'y': 30.6, 'height': 0.36, 'look_at': [35.6, 25.6, 0.7], 'fov': 70},
        {'x': 47.5, 'y': 21.0, 'look_at': [27.0, 19.5, 2.0], 'fov': 66, 'post': [GLOW],
         'overrides': {
             'sky': 'night', 'ambient': [0.1, 0.11, 0.16],
             'lights': [{'type': 'moon', 'azimuth': 205, 'elevation': 24, 'intensity': 0.55, 'disc_size': 2.4},
                        {'x': 40.5, 'y': 19.95, 'z': 1.1, 'radius': 4.5, 'color': [1.0, 0.62, 0.3], 'intensity': 1.4},
                        {'x': 34.6, 'y': 21.4, 'z': 0.9, 'radius': 3.0, 'color': [1.0, 0.62, 0.3], 'intensity': 0.6}],
             'fog': {'color': [0.12, 0.14, 0.2], 'density': 0.01, 'shafts': 1.0, 'glow': 0.6}}},
    ],
    prefabs=[{'type': 'ruined_columns', 'x': 42.2, 'y': 28.0, 'angle': 20, 'seed': 1},
             {'type': 'ruined_columns', 'x': 26.0, 'y': 31.5, 'angle': 170, 'seed': 2}],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ancient_ruins.json')))

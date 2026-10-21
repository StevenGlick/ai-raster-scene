"""Ancient ruins: a Doric temple on a headland above the sea, at golden hour and by moonlight.

Shows the ruin textures and props and columns built in 3D: round the temple a peristyle of fluted
Doric columns of marble standing on the stylobate (`column` objects with `flutes` and `"doric": true`,
laid in drums), stone architraves and cornices (`beam`s) still lying across the runs that stand, others
snapped off (`broken`) or fallen to drums; a collapsing cella; more columns along the sacred way and in
fallen groups; cypresses and olives; the low sun throwing the colonnade's shadow in stripes (the
columns and architraves `"casts": true`), and shafts of light between the columns.
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
ring = {}                                             # the peristyle: what stands on each cell of the ring
for y in range(TY0, TY1 + 1):
    for x in range(TX0, TX1 + 1):
        if x in (TX0, TX1) or y in (TY0, TY1):
            r = rnd.random()
            # most columns stand; on the sea side more have fallen
            fallen = 0.32 if x < 26 else 0.12
            ring[(x, y)] = 'P' if r > fallen else ('b' if r > fallen * 0.45 else 'B')
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

MARBLE = {'material': 'marble', 'flutes': 20, 'top': 0.8, 'fill': 1.0,       # the sky and the ground light the shadow,
          'casts': True}                                                       # and each throws its own
columns = []                                          # the peristyle's columns on the stylobate
for k, ((x, y), what) in enumerate(sorted(ring.items())):
    if what == 'P':
        columns.append(dict(MARBLE, type='column', x=x + 0.5, y=y + 0.5, radius=0.2, height=2.3, doric=True,
                            capital=0.26, seed=k))
    elif what == 'b':                                 # snapped off at its own height
        columns.append(dict(MARBLE, type='column', x=x + 0.5, y=y + 0.5, radius=0.2, height=0.9 + 0.8 * (k * 37 % 10) / 10,
                            broken=0.22, seed=k))


def runs(cells):
    """Straight runs of three or more standing columns, as (first, last) cells."""
    out, cur = [], []
    for c in cells + [None]:
        if c is not None and ring.get(c) == 'P':
            cur.append(c)
        else:
            if len(cur) >= 3:
                out.append((cur[0], cur[-1]))
            cur = []
    return out


for side in ([(x, TY0) for x in range(TX0, TX1 + 1)], [(x, TY1) for x in range(TX0, TX1 + 1)],
             [(TX0, y) for y in range(TY0, TY1 + 1)], [(TX1, y) for y in range(TY0, TY1 + 1)]):
    for (x0, y0), (x1, y1) in runs(side):             # the entablature still lying across them
        along_x = y0 == y1
        n = (x1 - x0 if along_x else y1 - y0) + 1
        cx, cy = (x0 + x1) / 2 + 0.5, (y0 + y1) / 2 + 0.5
        for z, w, d in ((2.3, 0.46, 0.3), (2.6, 0.6, 0.12)):           # architrave, then cornice
            columns.append({'type': 'beam', 'x': cx, 'y': cy, 'z': z, 'angle': 0 if along_x else 90,
                            'length': n - 1 + 0.62, 'width': w, 'depth': d, 'material': 'marble', 'fill': 1.0,
                            'casts': True, 'seed': x0 * 7 + y0})

legend = {
    ',': {'floor': 'dry_grass'},
    'p': {'floor': 'ruin_paving'},
    '~': {'floor': 'sea', 'drop': 0.25},
    'K': {'wall': {'base': 'limestone', 'tint': [0.82, 0.8, 0.76]}, 'top': 'limestone'},
    'B': {'wall': 'limestone', 'top': 'ruin_paving'},
    'A': {'wall': 'limestone', 'top': 'limestone'},
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
        snapped = broken or rnd.random() < 0.3
        rnd.random()                                  # the flip the billboard took, so later draws stay as they were
        columns.append(dict(MARBLE, type='column', x=x, y=y, radius=0.27, height=2.3 if snapped else 3.0,
                            doric=not snapped, capital=0.34, broken=0.26 if snapped else 0, seed=int(x * 10 + y)))
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
    objects=columns,
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
        # the fallen group in the sun, from the west; turned by angle and pitch, not look_at, and stood where
        # no scatter is, so it keeps nothing clear and the other shots' scatter stays as it was
        {'x': 38.4, 'y': 32.4, 'angle': 315.0, 'pitch': 0.198, 'fov': 60},
    ],
    prefabs=[{'type': 'ruined_columns', 'x': 42.2, 'y': 28.0, 'angle': 20, 'seed': 1},
             {'type': 'ruined_columns', 'x': 26.0, 'y': 31.5, 'angle': 170, 'seed': 2}],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ancient_ruins.json')))

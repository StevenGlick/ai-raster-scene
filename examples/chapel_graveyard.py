"""Chapel and graveyard under the moon: an iron-fenced churchyard, and the nave inside.

Shows moonlight with cast shadows (a `moon` light, its disc in the sky), a treeline skyline,
see-through iron fencing, stained glass, and an altar raised on stepped blocks via `heights`.
Run:  python chapel_graveyard.py  -> writes chapel_graveyard.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.5}  # the lights glow

g = Grid(34, 36, fill=',')                            # grass everywhere outside
g.box(2, 12, 31, 34, 'f')                             # the churchyard's iron fence...
g.rect(15, 34, 18, 34, ',')                           # ...with the gate open
g.line(16, 13, 16, 35, 'p', width=2)                  # path from the gate to the chapel door
g.room(9, 1, 24, 12, 'S', '.')                        # the chapel
for y in (3, 6, 9):
    g.put(9, y, 'G'); g.put(24, y, 'G')               # stained glass down both sides
for x in (11, 13, 20, 22):
    g.put(x, 12, 'G')                                 # and across the front, glowing out at the yard
for x in (15, 16, 17, 18):
    g.put(x, 1, 'G')                                  # the great window behind the altar
g.put(16, 12, 'o'); g.put(17, 12, 'o')                # the open doorway
g.rect(16, 3, 17, 11, 'r')                            # carpet down the nave
g.rect(12, 2, 21, 3, 'D')                             # the sanctuary dais...
g.rect(13, 4, 20, 4, 'E')                             # ...its step
g.put(16, 2, 'A'); g.put(17, 2, 'A')                  # the altar on top

heights = [list('.' * 34) for _ in range(36)]
for y in (2, 3):
    for x in range(12, 22):
        if (x, y) not in ((16, 2), (17, 2)):          # leave the altar cells out: they keep h 0.62
            heights[y][x] = '3'                       # dais 0.3
for x in range(13, 21):
    heights[4][x] = '1'                               # step 0.1 (the altar keeps its own h)

pews = [{'x': x, 'y': y, 'type': 'pew', 'scale': 0.42, 'stretch': 2.2}
        for y in (5.6, 7.2, 8.8, 10.4) for x in (14.4, 19.1)]
graves = []
for row, y in enumerate((16.5, 20.5, 24.5, 28.5)):
    for col, x in enumerate((5.5, 8.5, 11.5, 21.5, 24.5, 27.5)):
        kind = 'grave_cross' if (row * 3 + col) % 3 == 0 else 'gravestone'
        graves.append({'x': x + (0.3 if row % 2 else 0), 'y': y, 'type': kind, 'flip': (row + col) % 2 == 0})

s = scene(
    g,
    title='Chapel and graveyard under the moon',
    heights=[''.join(r) for r in heights],
    legend={
        ',': {'floor': 'grass'},
        'p': {'floor': 'gravel'},
        'f': {'wall': 'fence_iron', 'h': 1.0},
        'S': {'wall': 'stone_pale', 'h': 3.2, 'top': 'shingle'},
        'G': {'wall': ['stone_pale', 'stained_glass', 'stone_pale'], 'h': 3.2, 'top': 'shingle'},
        '.': {'floor': 'flagstone', 'ceil': 'beams'},
        'o': {'floor': 'flagstone', 'ceil': 'beams'},
        'r': {'floor': 'carpet', 'ceil': 'beams'},
        'D': {'wall': 'marble', 'top': 'flagstone'},
        'E': {'wall': 'marble', 'top': 'flagstone'},
        'A': {'wall': 'marble', 'h': 0.62, 'top': 'carpet'},
    },
    ceiling_height=2.4,
    sky='night',
    skyline='treeline',
    ambient=[0.13, 0.14, 0.2],
    fog={'color': [0.14, 0.16, 0.22], 'density': 0.03, 'sky_mix': 0.3},
    lights=[
        {'type': 'moon', 'azimuth': 258, 'elevation': 14, 'intensity': 0.85},
        {'x': 16.5, 'y': 34.6, 'z': 1.0, 'radius': 5.0, 'color': [1.0, 0.72, 0.4], 'intensity': 1.1},
        {'x': 16.5, 'y': 13.4, 'z': 1.0, 'radius': 5.0, 'color': [1.0, 0.75, 0.45], 'intensity': 1.0},
        {'x': 16.5, 'y': 2.6, 'z': 0.9, 'radius': 6.5, 'color': [1.0, 0.7, 0.38], 'intensity': 1.5},
        {'x': 16.5, 'y': 8.0, 'z': 1.6, 'radius': 7.0, 'color': [0.95, 0.8, 0.6], 'intensity': 0.7},
        {'x': 10.5, 'y': 6.0, 'z': 1.5, 'radius': 4.0, 'color': [0.5, 0.45, 1.0], 'intensity': 0.5},
        {'x': 22.5, 'y': 6.0, 'z': 1.5, 'radius': 4.0, 'color': [1.0, 0.45, 0.4], 'intensity': 0.5},
        {'x': 24.5, 'y': 24.5, 'z': 0.4, 'radius': 2.5, 'color': [1.0, 0.7, 0.4], 'intensity': 0.9},
        {'x': 11.3, 'y': 25.1, 'z': 0.4, 'radius': 2.8, 'color': [1.0, 0.7, 0.4], 'intensity': 1.0},
        {'x': 8.6, 'y': 21.1, 'z': 0.4, 'radius': 2.6, 'color': [1.0, 0.7, 0.4], 'intensity': 0.9},
        {'x': 14.2, 'y': 28.9, 'z': 0.4, 'radius': 2.4, 'color': [1.0, 0.7, 0.4], 'intensity': 0.8},
    ],
    sprites=pews + graves + [
        {'x': 16.0, 'y': 2.5, 'type': 'candles'}, {'x': 17.0, 'y': 2.5, 'type': 'candles'},
        {'x': 19.5, 'y': 3.4, 'type': 'lectern'},
        {'x': 13.0, 'y': 3.0, 'type': 'candles'}, {'x': 20.0, 'y': 3.0, 'type': 'candles'},
        {'x': 15.6, 'y': 34.6, 'type': 'lantern', 'z': 0.75}, {'x': 18.4, 'y': 13.4, 'type': 'lantern', 'z': 0.8},
        {'x': 24.5, 'y': 24.9, 'type': 'candles'}, {'x': 11.3, 'y': 25.1, 'type': 'candles'},
        {'x': 8.6, 'y': 21.1, 'type': 'candles'}, {'x': 14.2, 'y': 28.9, 'type': 'candles'},
        {'x': 4.5, 'y': 31.0, 'type': 'dead_tree'}, {'x': 29.5, 'y': 18.0, 'type': 'dead_tree', 'flip': True},
        {'x': 6.0, 'y': 14.2, 'type': 'dead_tree', 'scale': 2.2},
        {'id': 'ghost', 'x': 22.8, 'y': 22.4, 'type': 'ghost'},
    ],
    scatter=[{'of': 'undergrowth', 'on': ',', 'density': 0.35, 'clump': 1.5, 'sizes': ['tiny', 'small', 'medium'],
              'seed': 4},
             {'of': 'stones', 'on': ',p', 'density': 0.25, 'sizes': ['tiny', 'small'], 'seed': 5}],
    # its roof: steep slate down the nave, its gable over the door in pale stone
    objects=[{'type': 'gable_roof', 'x': 17.0, 'y': 7.0, 'z': 3.2, 'angle': 90, 'length': 12.0, 'width': 16.0,
              'rise': 5.2, 'cover': 'slate', 'ends': 'ashlar', 'overhang': [0.3, 0.15], 'seed': 7}],
    camera={'x': 16.5, 'y': 34.0, 'look_at': [16.5, 6.0, 1.6], 'fov': 72},
    shots=[
        {'x': 13.2, 'y': 31.2, 'look_at': [16.8, 12.0, 1.5], 'fov': 74, 'post': [GLOW],
         'overlays': [{'type': 'caption', 'text': 'The old churchyard', 'at': 'top', 'box': True}]},
        {'x': 19.0, 'y': 27.0, 'look_at': 'ghost', 'fov': 64, 'post': [GLOW]},
        {'x': 16.5, 'y': 11.4, 'look_at': [16.5, 2.4, 0.75], 'fov': 74, 'post': [GLOW]},
        {'x': 14.2, 'y': 7.4, 'look_at': [16.6, 2.4, 0.62], 'fov': 64, 'post': [GLOW],
         'overlays': [{'type': 'dialog', 'portrait': 'spiritualist', 'name': 'Voice in the nave',
                       'text': 'Light one candle for each name on the stones. Not one more.'}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chapel_graveyard.json')))

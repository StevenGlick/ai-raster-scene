"""Example of authoring a scene with maptools: the mansion's hidden occult library.
Run: python mansion_library.py  -> writes mansion_library.json next to this file."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(18, 16, fill='#')
g.room(1, 1, 16, 14, '#', '.')
# bookshelves line the long walls, broken by curtained windows
for x in range(2, 16):
    g.put(x, 1, 'B'); g.put(x, 14, 'B')
for y in range(2, 14):
    g.put(1, y, 'B'); g.put(16, y, 'B')
for y in (4, 10):
    g.put(16, y, 'W')
g.put(1, 7, 'C'); g.put(1, 8, 'C')           # curtained alcove west
g.rect(6, 5, 11, 10, 'r')                     # ritual rug in the middle
g.put(8, 1, 'S'); g.put(9, 1, 'S')            # sigil behind the reading desk
for (x, y) in ((4, 4), (13, 4), (4, 11), (13, 11)):
    g.put(x, y, 'P')                          # stone pillars

s = scene(
    g,
    legend={
        '#': {'wall': 'stone_dark', 'h': 1.4},
        'B': {'wall': ['bookshelf', 'wallpaper'], 'h': 1.4},
        'W': {'wall': ['wallpaper', 'window_dark'], 'h': 1.4},
        'C': {'wall': 'curtain', 'h': 1.4},
        'S': {'wall': ['runes', 'wallpaper'], 'h': 1.4},
        'P': {'wall': 'marble', 'h': 1.4},
        '.': {'floor': 'wood_floor', 'ceil': 'beams'},
        'r': {'floor': 'carpet', 'ceil': 'beams'},
    },
    camera={'x': 8.5, 'y': 12.8, 'angle': 270, 'fov': 72, 'height': 0.55},
    title='Mansion library built with maptools',
    ceiling_height=1.4,
    sky=None,
    ambient=[0.08, 0.07, 0.075],
    lights=[
        {'x': 8.0, 'y': 2.6, 'z': 0.6, 'radius': 5.0, 'color': [1.0, 0.75, 0.4], 'intensity': 1.4},
        {'x': 9.0, 'y': 7.5, 'z': 0.6, 'radius': 4.0, 'color': [1.0, 0.2, 0.1], 'intensity': 0.9},
        {'x': 15.3, 'y': 4.0, 'z': 1.0, 'radius': 3.0, 'color': [0.5, 0.6, 0.9], 'intensity': 0.6},
        {'x': 15.3, 'y': 10.0, 'z': 1.0, 'radius': 3.0, 'color': [0.5, 0.6, 0.9], 'intensity': 0.6},
        {'x': 3.0, 'y': 12.5, 'z': 0.6, 'radius': 3.5, 'color': [1.0, 0.75, 0.4], 'intensity': 0.9},
        {'x': 2.6, 'y': 5.0, 'z': 0.9, 'radius': 4.0, 'color': [1.0, 0.75, 0.4], 'intensity': 1.1},
        {'x': 14.4, 'y': 7.5, 'z': 0.9, 'radius': 4.0, 'color': [1.0, 0.75, 0.4], 'intensity': 1.0},
        {'x': 2.6, 'y': 10.0, 'z': 0.9, 'radius': 4.0, 'color': [1.0, 0.75, 0.4], 'intensity': 1.0},
    ],
    fog={'color': [0.02, 0.015, 0.015], 'density': 0.045},
    sprites=[
        {'x': 7.6, 'y': 2.4, 'type': 'candles'}, {'x': 9.4, 'y': 2.4, 'type': 'candles'},
        {'x': 8.5, 'y': 7.5, 'type': 'candles', 'scale': 0.25}, {'x': 7.2, 'y': 6.4, 'type': 'candles'},
        {'x': 9.8, 'y': 8.6, 'type': 'candles'}, {'x': 7.0, 'y': 8.8, 'type': 'candles'},
        {'x': 3.0, 'y': 12.6, 'type': 'candles'},
        {'x': 13.0, 'y': 7.5, 'type': 'statue', 'scale': 1.3},
        {'x': 2.3, 'y': 5.0, 'type': 'lantern', 'z': 0.75}, {'x': 14.7, 'y': 7.5, 'type': 'lantern', 'z': 0.75},
        {'x': 2.3, 'y': 10.0, 'type': 'lantern', 'z': 0.75},
        {'x': 3.2, 'y': 2.6, 'type': 'crate'}, {'x': 14.2, 'y': 12.8, 'type': 'barrel'},
    ],
    shots=[
        {'x': 6.0, 'y': 10.6, 'angle': 290, 'pitch': -0.04},
        {'x': 2.7, 'y': 7.5, 'angle': 345},
    ],
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mansion_library.json')))

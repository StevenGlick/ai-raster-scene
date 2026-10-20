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
        '#': {'wall': 'stone_dark', 'h': 2.0},
        'B': {'wall': ['bookshelf', 'bookshelf'], 'h': 2.0},
        'W': {'wall': ['wallpaper', 'window_dark'], 'h': 2.0},
        'C': {'wall': 'curtain', 'h': 2.0},
        'S': {'wall': ['runes', 'wallpaper'], 'h': 2.0},
        'P': {'wall': 'marble', 'h': 2.0},
        '.': {'floor': 'wood_floor', 'ceil': 'wood_panel'},
        'r': {'floor': 'carpet', 'ceil': 'wood_panel'},
    },
    camera={'x': 8.5, 'y': 12.8, 'angle': 270, 'fov': 72, 'height': 0.55},
    title='Mansion library built with maptools',
    ceiling_height=2.0,
    sky=None,
    ambient=[0.16, 0.13, 0.12],
    lights=[
        {'x': 8.0, 'y': 2.6, 'z': 0.6, 'radius': 5.0, 'color': [1.0, 0.75, 0.4], 'intensity': 1.4},
        {'x': 9.0, 'y': 7.5, 'z': 0.6, 'radius': 4.0, 'color': [1.0, 0.2, 0.1], 'intensity': 0.9},
        {'x': 15.3, 'y': 4.0, 'z': 1.0, 'radius': 3.0, 'color': [0.5, 0.6, 0.9], 'intensity': 0.6},
        {'x': 15.3, 'y': 10.0, 'z': 1.0, 'radius': 3.0, 'color': [0.5, 0.6, 0.9], 'intensity': 0.6},
        {'x': 3.0, 'y': 12.5, 'z': 0.6, 'radius': 3.5, 'color': [1.0, 0.75, 0.4], 'intensity': 0.9},
        {'x': 2.6, 'y': 5.0, 'z': 0.9, 'radius': 4.0, 'color': [1.0, 0.75, 0.4], 'intensity': 1.1},
        {'x': 14.4, 'y': 7.5, 'z': 0.9, 'radius': 4.0, 'color': [1.0, 0.75, 0.4], 'intensity': 1.0},
        {'x': 2.6, 'y': 10.0, 'z': 0.9, 'radius': 4.0, 'color': [1.0, 0.75, 0.4], 'intensity': 1.0},
        {'x': 6.6, 'y': 6.0, 'z': 1.1, 'radius': 5.0, 'color': [1.0, 0.72, 0.4], 'intensity': 1.3},   # the candelabras
        {'x': 10.4, 'y': 6.0, 'z': 1.1, 'radius': 5.0, 'color': [1.0, 0.72, 0.4], 'intensity': 1.3},
        {'x': 8.5, 'y': 3.2, 'z': 0.9, 'radius': 3.0, 'color': [1.0, 0.75, 0.42], 'intensity': 1.0},  # the desk's candle
    ],
    fog={'color': [0.02, 0.015, 0.015], 'density': 0.045},
    sprites=[
        {'x': 7.6, 'y': 2.4, 'type': 'candles'}, {'x': 9.4, 'y': 2.4, 'type': 'candles'},
        {'x': 8.5, 'y': 7.5, 'type': 'candles', 'scale': 0.25},
        {'x': 3.0, 'y': 12.6, 'type': 'candles'},
        # the reading corner by the sigil: a desk, a chair, a globe, a telescope at the window
        {'x': 8.5, 'y': 3.0, 'type': 'writing_desk'}, {'x': 8.5, 'y': 4.0, 'type': 'armchair', 'flip': True},
        {'x': 11.6, 'y': 3.0, 'type': 'globe'}, {'x': 15.0, 'y': 5.6, 'type': 'telescope', 'flip': True},
        {'x': 5.2, 'y': 2.8, 'type': 'grandfather_clock'},
        {'x': 6.6, 'y': 6.0, 'type': 'candelabra'}, {'x': 10.4, 'y': 6.0, 'type': 'candelabra'},
        {'x': 4.6, 'y': 9.0, 'type': 'book_stack'}, {'x': 12.0, 'y': 11.2, 'type': 'book_stack', 'flip': True},
        {'x': 8.5, 'y': 7.5, 'type': 'open_book', 'z': 0.9}, {'x': 7.6, 'y': 8.4, 'type': 'book_fly', 'z': 1.3},
        {'x': 9.6, 'y': 6.8, 'type': 'book_fly', 'z': 1.5, 'flip': True},
        {'id': 'reader', 'x': 9.2, 'y': 4.4, 'type': 'spiritualist', 'facing': 270},
        {'x': 2.25, 'y': 7.5, 'type': 'portrait', 'z': 1.3, 'planes': 1, 'angle': 90, 'length': 0.6},
        {'x': 1.3, 'y': 1.3, 'type': 'cobweb', 'z': 1.4, 'planes': 1, 'angle': 135, 'length': 1.0},
        {'x': 15.7, 'y': 1.3, 'type': 'cobweb', 'z': 1.4, 'planes': 1, 'angle': 45, 'length': 1.0, 'flip': True},
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

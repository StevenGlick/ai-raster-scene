"""Rain alley: a downpour at night, wet street, lamps haloed in the drizzle-thick air.

Shows depth-aware rain and splashes (the `downpour` preset), `wet` ground mirroring the lamps
and windows, volumetric fog with `glow` (every lamp gets a halo), lightning, and a figure
walking away from the camera (`facing`).
Run:  python rain_alley.py  -> writes rain_alley.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(20, 44, fill='B')
g.rect(8, 2, 11, 41, '.')                             # the alley
g.rect(4, 18, 7, 21, '.')                             # a side court
for y in range(3, 41, 4):
    g.put(7, y, 'b' if y % 8 else 'N')                # facades with their lit windows
    g.put(12, y + 2, 'b' if (y + 2) % 8 else 'N')
lamps = [(8.4, 36.0), (11.6, 28.0), (8.4, 20.0), (11.6, 12.0), (8.4, 5.0)]

s = scene(
    g,
    title='Rain alley - a downpour at night',
    legend={
        'B': {'wall': ['brick_dark', 'window_dark', 'window_lit', 'window_dark', 'window_lit'], 'h': 5.0},
        'b': {'wall': ['brick_dark', 'window_lit', 'window_dark', 'window_lit', 'window_dark'], 'h': 5.0},
        'N': {'wall': ['brick_dark', 'window_teal', 'window_lit', 'window_teal', 'window_dark'], 'h': 5.0},
        '.': {'floor': 'cobble'},
    },
    sky='storm',
    ambient=[0.07, 0.075, 0.09],
    wet=0.7,
    fog={'color': [0.06, 0.07, 0.09], 'density': 0.035, 'ground': 0.05, 'height': 0.8, 'glow': 1.3},
    lights=[{'x': x + (0.45 if x < 10 else -0.45), 'y': y, 'z': 1.5, 'radius': 4.5, 'color': [1.0, 0.82, 0.52],
             'intensity': 1.3} for x, y in lamps] + [
        {'x': 5.5, 'y': 19.5, 'z': 1.2, 'radius': 3.5, 'color': [0.45, 0.9, 1.0], 'intensity': 0.9},
    ],
    sprites=[{'x': x, 'y': y, 'type': 'lamp_post'} for x, y in lamps] + [
        {'id': 'officer', 'x': 9.7, 'y': 25.0, 'type': 'guard', 'facing': 270},
        {'x': 10.9, 'y': 31.0, 'type': 'barrel'}, {'x': 8.6, 'y': 15.0, 'type': 'crate'},
        {'x': 10.8, 'y': 15.4, 'type': 'sack'},
    ],
    decals=[{'tex': 'puddle_shine', 'surface': 'floor', 'x': 9.6, 'y': y, 'size': 1.6} for y in (33.0, 23.0, 9.0)],
    scatter=[{'of': 'litter', 'on': '.', 'density': 0.08, 'sizes': ['tiny', 'small'], 'seed': 6}],
    camera={'x': 9.8, 'y': 40.2, 'look_at': [9.8, 2.0, 0.8], 'fov': 66},
    shots=[
        {'x': 9.8, 'y': 40.2, 'look_at': [9.8, 2.0, 0.8], 'fov': 66, 'post': ['downpour'],
         'overlays': [{'type': 'caption', 'text': 'Third night of rain', 'at': 'top', 'box': True}]},
        {'x': 10.6, 'y': 31.4, 'look_at': [8.6, 21.0, 1.1], 'fov': 64, 'post': ['downpour']},
        {'x': 9.4, 'y': 29.0, 'look_at': [9.8, 4.0, 2.6], 'fov': 72, 'post': ['storm', {'fx': 'lightning', 'x': 0.62}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rain_alley.json')))

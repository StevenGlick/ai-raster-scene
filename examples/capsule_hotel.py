"""Capsule hotel: a corridor between two walls of sleeping berths in the small hours, a sleepwalker coming
down it with her candle, a vending machine humming at the end.

Shows the `capsules` and `capsules_lit` walls (scripts/bar.py: berths four to a unit, each with a
glowing number plate, lamp-lit bedding, a blind drawn with light behind it, a screen's glow or
dark), alternated cell by cell and storey by storey so the pattern does not march; a corridor
one cell wide under a low ceiling, cool strip lights, a white floor that mirrors the berths, a
`ladder` up to the top row, the `dreamer` and the `hacker`; and at the corridor's end a `vending_machine`
object, in 3D: its window of drinks let into its front, lit, behind clear plastic.
Run:  python capsule_hotel.py  -> writes capsule_hotel.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 7, 19
g = Grid(W, H, fill='#')
g.rect(3, 1, 3, 17, 'c')                             # the corridor
for y in range(1, 18):
    for x in (2, 4):
        g.put(x, y, 'A' if (y + x) % 2 else 'B')     # the berths, two patterns alternating

COOL = [0.82, 0.9, 1.0]
s = scene(
    g,
    title='Capsule hotel - the corridor at four in the morning',
    legend={
        '#': {'wall': 'concrete', 'h': 1.0},
        'A': {'wall': 'capsules', 'h': 1.0},
        'B': {'wall': 'capsules_lit', 'h': 1.0},
        'c': {'floor': 'tile_white', 'ceil': 'panel', 'reflect': 0.3},
    },
    ceiling_height=1.0,
    sky=None,
    ambient=[0.08, 0.09, 0.11],
    fog={'color': [0.04, 0.05, 0.07], 'density': 0.03, 'glow': 0.7},
    lights=[{'x': 3.5, 'y': y, 'z': 0.95, 'radius': 1.6, 'color': COOL, 'intensity': 0.7} for y in range(2, 18, 3)]
    + [{'x': 3.5, 'y': 1.5, 'z': 0.5, 'radius': 1.6, 'color': [0.8, 0.95, 1.0], 'intensity': 1.0},       # vending
       {'x': 3.55, 'y': 9.4, 'z': 0.45, 'radius': 0.9, 'color': [1.0, 0.75, 0.4], 'intensity': 0.9}],    # the candle
    objects=[{'type': 'vending_machine', 'x': 3.5, 'y': 1.15, 'angle': 90, 'lights': False}],   # its light is above
    sprites=[
        {'id': 'hacker', 'x': 3.75, 'y': 2.2, 'type': 'hacker', 'facing': 270},
        {'id': 'dreamer', 'x': 3.5, 'y': 9.4, 'type': 'dreamer', 'facing': 90},
        {'x': 2.25, 'y': 12.5, 'type': 'ladder', 'scale': 0.95},
        {'x': 4.75, 'y': 6.5, 'type': 'ladder', 'scale': 0.95, 'flip': True},
    ],
    camera={'x': 3.5, 'y': 17.6, 'look_at': [3.5, 2.0, 0.48], 'fov': 64},
    shots=[
        {'x': 3.5, 'y': 17.6, 'look_at': [3.5, 2.0, 0.48], 'fov': 64,
         'post': [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.55}],
         'overlays': [{'type': 'caption', 'text': 'Capsule hotel, 4 a.m.', 'at': 'top', 'box': True}]},
        {'x': 3.75, 'y': 12.6, 'look_at': [2.6, 10.6, 0.55], 'fov': 66,
         'post': [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.55}]},
        {'x': 3.45, 'y': 11.4, 'look_at': 'dreamer', 'fov': 56, 'height': 0.42,
         'post': [{'fx': 'dof', 'blur': 2.0}, {'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.55}]},
        {'x': 3.3, 'y': 4.4, 'look_at': 'hacker', 'fov': 60,
         'post': [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.55}],
         'overlays': [{'type': 'bubble', 'anchor': 'hacker', 'name': 'Hacker',
                       'text': 'Machine only takes old coins. Nobody has old coins.'}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'capsule_hotel.json')))

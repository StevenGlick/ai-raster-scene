"""Neon rooftop: the roof of a tower at the end of a neon street, five storeys over it - the canyon of
signs going away below, an elevated train crossing it, holograms over the street, towers all round.

Shows how to stand on a roof - the camera in a block 5 tall with `height` 5.5, roof props given
`z` 5 - and the rooftop kit (scripts/rooftop.py): a `water_tower`, `ac_unit`s, a `rooftop_sign`
on its scaffold, the `sky_train` slung across the street as a card on its pillars, and a
`black_cat` on the parapet beside the `runner`. The street below is the `neon` facade style
between blocks a storey taller, so the fronts' tops meet window walls rather than sky; towers
of plain window walls stand behind them, and a `holo_ad` koi turns over the street.
Run:  python neon_rooftop.py  -> writes neon_rooftop.json
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 40, 46
g = Grid(W, H, fill='s')                             # the streets
g.rect(10, 4, 16, 33, 'L')                           # the neon blocks either side of the canyon
g.rect(22, 4, 28, 33, 'R')
g.rect(10, 18, 16, 19, 's')                          # a cross street the train runs over
g.rect(22, 18, 28, 19, 's')
g.rect(14, 34, 24, 41, 'P')                          # the tower we stand on
g.rect(14, 34, 24, 34, 'p')                          # its parapet
g.rect(14, 34, 14, 41, 'p')
g.rect(24, 34, 24, 41, 'p')
rng = np.random.default_rng(31)
legend = {
    's': {'floor': 'asphalt'},
    'L': {'wall': ['brick_dark', 'window_dark', 'window_lit', 'window_dark', 'window_lit', 'window_dark',
                   'window_dark', 'window_lit', 'window_dark'], 'h': 9.0, 'top': 'concrete_floor',
          'facade': {'style': 'neon', 'storeys': [4, 8], 'widths': [2, 4], 'lit': 0.6, 'shops': 0.85, 'seed': 41}},
    'R': {'wall': ['brick_dark', 'window_lit', 'window_dark', 'window_dark', 'window_lit', 'window_dark',
                   'window_lit', 'window_dark', 'window_dark'], 'h': 9.0, 'top': 'concrete_floor',
          'facade': {'style': 'neon', 'storeys': [4, 8], 'widths': [2, 4], 'lit': 0.6, 'shops': 0.85, 'seed': 43}},
    'P': {'wall': ['brick_dark', 'window_dark', 'window_lit', 'window_dark', 'window_dark'], 'h': 5.0,
          'top': 'concrete_floor'},
    'p': {'wall': ['brick_dark', 'window_dark', 'window_lit', 'window_dark', 'window_dark', 'concrete'], 'h': 5.15,
          'top': 'concrete'},
}
towers = 'ABCDEFGHIJ'                                # towers of lit windows behind the street blocks
for k, (x0, y0, x1, y1) in enumerate(((1, 2, 7, 12), (1, 15, 7, 25), (1, 28, 7, 40), (31, 2, 38, 13),
                                      (31, 16, 38, 26), (31, 29, 38, 41), (10, 0, 28, 1), (8, 43, 13, 45),
                                      (26, 43, 33, 45), (17, 0, 21, 1))):
    c = towers[k]
    hgt = float(rng.choice([10.0, 12.0, 14.0, 11.0, 13.0]))
    legend[c] = {'wall': ['brick_dark'] + ['window_lit' if rng.random() < 0.45 else 'window_dark'
                                          for _ in range(int(hgt))], 'h': hgt, 'top': 'concrete_floor'}
    g.rect(x0, y0, x1, y1, c)

PINK, CYAN, GOLD, VIOLET = [1.0, 0.3, 0.7], [0.3, 0.9, 1.0], [1.0, 0.75, 0.3], [0.7, 0.45, 1.0]
glows = [(17.2, 31.0, PINK), (21.8, 28.0, CYAN), (17.2, 24.0, VIOLET), (21.8, 21.0, PINK), (17.2, 15.0, CYAN),
         (21.8, 12.0, GOLD), (17.2, 8.0, PINK), (21.8, 6.0, VIOLET)]
lights = [{'x': x, 'y': y, 'z': 2.6, 'radius': 4.5, 'color': c, 'intensity': 1.2} for x, y, c in glows]
lights += [{'x': 19.0, 'y': 18.5, 'z': 4.0, 'radius': 4.0, 'color': [1.0, 0.9, 0.7], 'intensity': 0.6},   # the train
           {'x': 17.6, 'y': 38.4, 'z': 5.6, 'radius': 3.5, 'color': [1.0, 0.75, 0.45], 'intensity': 0.7},       # roof lamp
           {'x': 19.0, 'y': 33.7, 'z': 5.0, 'radius': 2.2, 'color': CYAN, 'intensity': 1.0},                   # the street's
           {'x': 18.4, 'y': 33.7, 'z': 4.8, 'radius': 1.8, 'color': PINK, 'intensity': 0.8}]                    # glow, rising
lights += [
           {'x': 23.2, 'y': 36.2, 'z': 5.8, 'radius': 4.0, 'color': PINK, 'intensity': 1.0},              # the sign
           {'x': 19.0, 'y': 12.0, 'z': 6.0, 'radius': 6.0, 'color': CYAN, 'intensity': 0.8}]              # the holo
sprites = [
    {'x': 19.0, 'y': 18.5, 'type': 'sky_train', 'angle': 0, 'length': 30.0, 'scale': 4.6},
    {'x': 19.0, 'y': 12.0, 'type': 'holo_ad', 'z': 5.2, 'scale': 3.0},
    {'x': 19.4, 'y': 27.0, 'type': 'holo_ad', 'z': 3.0, 'scale': 1.6, 'flip': True},
    {'x': 16.8, 'y': 37.0, 'type': 'water_tower', 'z': 5.0},
    {'x': 22.6, 'y': 39.4, 'type': 'ac_unit', 'z': 5.0}, {'x': 21.4, 'y': 40.4, 'type': 'ac_unit', 'z': 5.0, 'flip': True},
    {'x': 17.2, 'y': 40.6, 'type': 'antenna', 'z': 5.0},
    {'x': 23.0, 'y': 36.4, 'type': 'rooftop_sign', 'z': 5.0},
    {'id': 'runner', 'x': 18.7, 'y': 34.22, 'type': 'runner', 'z': 5.15, 'facing': 268, 'tint': [2.2, 2.1, 2.5]},
    {'id': 'cat', 'x': 19.45, 'y': 34.12, 'type': 'black_cat', 'z': 5.15},
] + [{'x': 19.0, 'y': y, 'type': t, 'angle': 0, 'length': 6.0, 'z': z, 'scale': sc}
     for y, z, t, sc in ((31.0, 3.4, 'lantern_span', 0.6), (25.0, 4.2, 'wires_span', 0.75), (22.0, 3.0, 'lantern_span', 0.6),
                         (13.0, 3.6, 'wires_span', 0.75), (9.0, 3.2, 'lantern_span', 0.6))] + [
    {'x': 17.6, 'y': 29.0, 'type': 'crowd', 'scale': 0.66}, {'x': 20.4, 'y': 24.5, 'type': 'crowd', 'flip': True},
    {'x': 18.6, 'y': 15.0, 'type': 'crowd'}, {'x': 17.8, 'y': 31.5, 'type': 'food_cart'},
    {'x': 20.8, 'y': 30.2, 'type': 'scooter'},
]

s = scene(
    g,
    title='Neon rooftop - over the street, the train going by',
    legend=legend,
    sky='night',
    skyline='city',
    ambient=[0.13, 0.11, 0.16],
    wet=0.7,
    fog={'color': [0.07, 0.05, 0.1], 'density': 0.02, 'glow': 1.1},
    lights=lights,
    sprites=sprites,
    camera={'x': 19.3, 'y': 35.6, 'height': 6.25, 'look_at': [19.0, 17.0, 2.2], 'fov': 72},
    shots=[
        {'x': 19.3, 'y': 35.6, 'height': 6.25, 'look_at': [19.0, 17.0, 2.2], 'fov': 72,
         'post': [{'fx': 'bloom', 'threshold': 0.55, 'strength': 0.7, 'radius': 6}],
         'overlays': [{'type': 'caption', 'text': 'Five storeys over the lower city', 'at': 'top', 'box': True}]},
        {'x': 18.4, 'y': 34.1, 'height': 5.75, 'look_at': [19.0, 27.5, 0.0], 'fov': 74,
         'post': [{'fx': 'bloom', 'threshold': 0.55, 'strength': 0.7, 'radius': 6}]},
        {'x': 19.6, 'y': 23.4, 'height': 0.45, 'look_at': [19.0, 18.5, 4.2], 'fov': 74,
         'post': [{'fx': 'bloom', 'threshold': 0.55, 'strength': 0.7, 'radius': 6}]},
        {'x': 19.75, 'y': 34.9, 'height': 5.42, 'look_at': [19.45, 30.0, 4.6], 'fov': 56,
         'post': [{'fx': 'bloom', 'threshold': 0.55, 'strength': 0.7, 'radius': 6}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'neon_rooftop.json')))

"""Neon street: a narrow street in the lower city at night, in the rain, under the signs.

Shows the `neon` facade style - dark concrete blocks hung with glowing signs, blade signs
standing out over the street on cards of their own, shutters half down over the shops, rooms lit
pink, blue and green - with the street props from scifi.py: `wires_span` slung across overhead
with paper lanterns, a `holo_ad` koi turning in the air (additive), a `noodle_stall` with its
cook, `vending_machine`s, `steam` rising from the drains, and the `runner`. Coloured point lights
under the signs throw their colour on the wet street, which mirrors it all.
Run:  python neon_street.py  -> writes neon_street.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 30, 44
g = Grid(W, H, fill='N')
g.rect(10, 6, 10, H - 1, 'f')                         # the fronts' cell, west side
g.rect(11, 6, 12, H - 1, 's')                         # pavement
g.rect(13, 6, 16, H - 1, '~')                         # the road
g.rect(17, 6, 18, H - 1, 's')
g.rect(19, 6, 19, H - 1, 'f')
g.rect(10, 5, 19, 5, 'f')                             # the block closing the far end has a front too

PINK, CYAN, GOLD, VIOLET = [1.0, 0.3, 0.7], [0.3, 0.9, 1.0], [1.0, 0.75, 0.3], [0.7, 0.45, 1.0]
glows = [(11.2, 40.0, PINK), (18.8, 35.0, CYAN), (11.2, 30.0, VIOLET), (18.8, 25.0, PINK), (11.2, 20.0, CYAN),
         (18.8, 15.0, GOLD), (11.2, 10.0, PINK), (18.8, 8.0, CYAN)]
RAIN = [{'fx': 'rain', 'density': 0.7, 'length': 8, 'opacity': 0.26, 'angle': 10}, {'fx': 'splashes', 'density': 0.6},
        {'fx': 'bloom', 'threshold': 0.55, 'strength': 0.7, 'radius': 6},
        {'fx': 'grade', 'saturation': 1.1, 'tint': [1.02, 0.95, 1.06]}]

s = scene(
    g,
    title='Neon street - the lower city at night, in the rain',
    legend={
        'N': {'wall': 'brick_dark', 'h': 3.0,
              'facade': {'style': 'neon', 'storeys': [3, 6], 'widths': [2, 4], 'lit': 0.6, 'shops': 0.9, 'seed': 11}},
        'f': {'floor': 'tile_floor'},
        's': {'floor': 'flagstone'},
        '~': {'floor': 'asphalt', 'drop': 0.05},
    },
    sky='night',
    skyline='city',
    ambient=[0.12, 0.11, 0.15],
    wet=0.85,
    fog={'color': [0.06, 0.05, 0.09], 'density': 0.018, 'glow': 1.2},
    lights=[{'x': x, 'y': y, 'z': 2.2, 'radius': 4.5, 'color': c, 'intensity': 1.3} for x, y, c in glows] + [
        {'x': 17.6, 'y': 22.0, 'z': 1.8, 'radius': 4.0, 'color': [1.0, 0.62, 0.32], 'intensity': 0.9},   # the stall
        {'x': 11.6, 'y': 26.8, 'z': 0.8, 'radius': 2.5, 'color': [0.75, 0.9, 1.0], 'intensity': 0.9},   # a vending machine
        {'x': 15.0, 'y': 20.0, 'z': 2.8, 'radius': 6.0, 'color': CYAN, 'intensity': 0.9},               # the hologram
    ],
    sprites=[
        {'x': 17.9, 'y': 22.0, 'type': 'noodle_stall'},
        {'id': 'cook', 'x': 18.3, 'y': 21.4, 'type': 'shopkeeper', 'facing': 270},
        {'x': 17.4, 'y': 21.4, 'type': 'steam', 'z': 0.9, 'scale': 0.8},
        {'x': 11.4, 'y': 26.8, 'type': 'vending_machine'}, {'x': 11.4, 'y': 27.7, 'type': 'vending_machine', 'flip': True},
        {'x': 18.6, 'y': 33.0, 'type': 'vending_machine'},
        {'x': 15.0, 'y': 20.0, 'type': 'holo_ad', 'z': 1.9, 'scale': 2.4},
        {'x': 13.6, 'y': 30.0, 'type': 'steam', 'scale': 1.3}, {'x': 16.2, 'y': 17.0, 'type': 'steam', 'scale': 1.5},
        {'id': 'runner', 'x': 12.0, 'y': 31.5, 'type': 'runner', 'facing': 90},
        {'x': 17.8, 'y': 27.0, 'type': 'android', 'facing': 270},
        {'x': 11.8, 'y': 16.0, 'type': 'cultist', 'facing': 0},
        {'x': 12.2, 'y': 37.6, 'type': 'barrel'}, {'x': 18.0, 'y': 39.4, 'type': 'sci_crate'},
        {'x': 18.4, 'y': 39.8, 'type': 'sci_crate', 'scale': 0.28},
    ] + [{'x': 15.0, 'y': y, 'type': 'wires_span', 'angle': 0, 'length': 10.0, 'z': z, 'scale': 0.75}
         for y, z in ((38.0, 3.0), (31.5, 3.4), (25.0, 2.9), (18.5, 3.3), (11.0, 3.1))],
    decals=[{'tex': 'puddle_shine', 'surface': 'floor', 'x': x, 'y': y, 'size': 1.6}
            for x, y in ((14.2, 36.0), (15.8, 28.0), (14.0, 21.0), (15.6, 14.0), (14.6, 9.0))] +
           [{'tex': 'drain', 'surface': 'floor', 'x': x, 'y': y, 'size': 0.8} for x, y in ((13.6, 30.0), (16.2, 17.0))],
    scatter=[{'of': 'litter', 'on': 's', 'density': 0.06, 'sizes': ['tiny', 'small'], 'seed': 4}],
    camera={'x': 15.0, 'y': 43.2, 'look_at': [15.0, 6.0, 1.7], 'fov': 64},
    shots=[
        {'x': 15.0, 'y': 43.2, 'look_at': [15.0, 6.0, 1.7], 'fov': 64, 'post': RAIN,
         'overlays': [{'type': 'caption', 'text': 'Lower city, after midnight', 'at': 'top', 'box': True}]},
        {'x': 13.4, 'y': 25.6, 'look_at': [18.4, 21.6, 1.0], 'fov': 66, 'post': RAIN},
        {'x': 12.4, 'y': 36.0, 'look_at': [16.0, 24.0, 3.2], 'fov': 74, 'post': RAIN},
        {'x': 13.2, 'y': 34.6, 'look_at': 'runner', 'fov': 58, 'post': RAIN,
         'overlays': [{'type': 'bubble', 'anchor': 'runner', 'name': 'Runner',
                       'text': 'Not here. Walk with me, and keep your eyes on the signs.'}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'neon_street.json')))

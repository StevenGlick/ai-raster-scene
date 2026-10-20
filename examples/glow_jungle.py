"""The glowing jungle: a clearing in the rainforest at night where everything that grows has light in
it - ferns and monsteras edged in cold blue-green, heliconias burning pink, pods glowing on curling
stalks, moss aglow on the floor - round a black pool where plankton swirls in streams of light. An old
stone head watches from the water's edge; spores drift, fireflies hang over the water, and the moon
looks in through a gap in the canopy.

Shows the glowing-jungle kit (scripts/glowjungle.py): the `glow_jungle` fringe on walls of
`glow_leaves`, a `lumen_floor` and a sunken pool of `glow_water`; `glow_monstera`, `glow_fern`,
`glow_tree_fern`, `glow_heliconia`, `glow_bromeliad`, `glow_liana` and `glow_pods`, with the
`glowshroom`s, a dark `kapok` and the `stone_head`. Coloured lights sit low in the plants so their glow
lands on the ground, a ground mist takes it up, and a light bloom does the rest.
Run:  python glow_jungle.py  -> writes glow_jungle.json
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 44, 44
g = Grid(W, H, fill='J')                              # jungle everywhere...
g.disc(22, 22, 14.5, '.')                             # ...but a clearing
g.disc(22, 19, 5.2, '~')                              # and a black pool in it
g.disc(9, 30, 3.5, '.')                               # a path opening west
for x in range(3, 9):
    for y in range(28, 33):
        g.put(x, y, '.')

CYAN, PINK, VIOLET, GREEN = [0.35, 1.0, 0.9], [1.0, 0.4, 0.8], [0.7, 0.5, 1.0], [0.4, 1.0, 0.55]
DARK = [0.22, 0.3, 0.34]                              # the night on what does not glow
legend = {
    'J': {'wall': 'glow_leaves', 'h': 3.2, 'top': {'base': 'canopy_top', 'tint': DARK}, 'fringe': 'glow_jungle'},
    '.': {'floor': 'lumen_floor'},
    '~': {'floor': 'glow_water', 'drop': 0.1, 'side': 'lumen_floor', 'reflect': 0.55},
}
sprites = [
    {'id': 'head', 'x': 25.6, 'y': 13.6, 'type': 'stone_head', 'scale': 1.6, 'tint': [0.45, 0.6, 0.62]},
    {'x': 11.0, 'y': 12.0, 'type': 'kapok', 'scale': 6.4, 'tint': DARK},
    {'x': 34.0, 'y': 30.5, 'type': 'kapok', 'scale': 6.8, 'tint': DARK, 'flip': True},
    {'id': 'jaguar', 'x': 31.5, 'y': 22.4, 'type': 'jaguar', 'tint': [0.4, 0.5, 0.55], 'facing': 200},
    {'id': 'explorer', 'x': 17.0, 'y': 30.5, 'type': 'explorer', 'tint': [0.55, 0.65, 0.7], 'facing': 300},
]
plants = [('glow_monstera', 15.5, 23.5), ('glow_heliconia', 17.0, 25.5), ('glow_fern', 19.5, 26.0),
          ('glow_bromeliad', 28.0, 25.0), ('glow_monstera', 29.5, 24.0), ('glow_tree_fern', 30.5, 15.0),
          ('glow_heliconia', 27.5, 12.6), ('glow_fern', 16.0, 15.5), ('glow_tree_fern', 14.5, 18.0),
          ('glow_bromeliad', 21.0, 27.0), ('glow_fern', 24.5, 26.2), ('glow_heliconia', 32.5, 19.0),
          ('glow_monstera', 12.5, 27.5), ('glow_fern', 33.0, 26.5), ('glow_bromeliad', 13.0, 21.5),
          ('glow_heliconia', 22.5, 9.5), ('glow_tree_fern', 19.0, 10.0), ('glow_fern', 26.5, 28.5),
          ('glowshroom', 18.2, 27.2), ('glowshroom', 29.0, 26.4), ('glowshroom', 31.4, 13.6),
          ('glowshroom', 14.2, 24.6), ('glow_monstera', 19.4, 29.2), ('glow_fern', 24.6, 29.6),
          ('glow_heliconia', 25.6, 28.8), ('glow_bromeliad', 33.4, 23.6), ('glow_fern', 30.6, 21.0)]
sprites += [{'x': x, 'y': y, 'type': t, 'flip': (k % 2) == 1} for k, (t, x, y) in enumerate(plants)]
sprites += [{'x': x, 'y': y, 'type': 'glow_pods', 'scale': s, 'flip': k % 2 == 1} for k, (x, y, s) in enumerate(
    ((18.4, 24.4, 1.1), (19.1, 24.8, 0.8), (27.0, 26.6, 1.2), (31.6, 17.0, 1.0), (13.8, 16.6, 0.9),
     (23.8, 11.2, 1.3), (10.5, 29.2, 1.0), (8.0, 31.5, 0.8)))]
sprites += [{'x': x, 'y': y, 'type': 'glow_liana', 'scale': s, 'z': z} for x, y, s, z in
            ((12.2, 13.0, 3.0, 1.2), (33.0, 29.5, 3.2, 1.4), (25.0, 33.5, 2.6, 1.6), (17.0, 8.5, 2.8, 1.4))]
lights = [{'x': x, 'y': y, 'z': 0.4, 'radius': r, 'color': c, 'intensity': i} for x, y, r, c, i in
          ((16.5, 24.5, 3.2, CYAN, 0.9), (28.5, 25.0, 3.4, VIOLET, 0.8), (30.0, 14.5, 3.0, CYAN, 0.8),
           (27.6, 12.8, 2.6, PINK, 0.7), (32.4, 19.4, 2.6, PINK, 0.7), (21.6, 26.6, 2.6, GREEN, 0.6),
           (14.0, 18.0, 3.0, CYAN, 0.7), (22.0, 19.0, 5.0, [0.3, 0.7, 1.0], 0.5), (9.0, 30.0, 3.0, CYAN, 0.6),
           (25.3, 14.7, 3.4, CYAN, 2.2), (31.2, 21.4, 2.2, CYAN, 0.8), (22.0, 29.0, 3.0, GREEN, 0.6))]
lights.append({'type': 'moon', 'azimuth': 250, 'elevation': 40, 'intensity': 0.25})
GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.8, 'radius': 2.5, 'spread': 0.55}
AIR = [{'fx': 'spores', 'count': 6, 'glow': 0.6, 'colors': [[0.5, 1.0, 0.9], [0.8, 0.6, 1.0]]},
       {'fx': 'fireflies', 'count': 6, 'glow': 0.8, 'color': [0.6, 1.0, 0.7]}, GLOW]

s = scene(
    g,
    title='The glowing jungle - a clearing at night',
    legend=legend,
    sky='night',
    ambient=[0.04, 0.06, 0.08],
    lights=lights,
    fog={'color': [0.02, 0.05, 0.06], 'density': 0.01, 'ground': 0.12, 'height': 0.3, 'noise': 0.5, 'glow': 0.6},
    sprites=sprites,
    camera={'x': 22.0, 'y': 32.5, 'look_at': [22.0, 15.0, 0.8], 'fov': 70},
    shots=[
        {'x': 22.4, 'y': 26.2, 'height': 0.6, 'look_at': [22.5, 13.0, 0.5], 'fov': 74, 'post': AIR,
         'overlays': [{'type': 'caption', 'text': 'The glowing jungle', 'at': 'top', 'box': True}]},
        {'x': 20.6, 'y': 21.0, 'height': 0.3, 'look_at': 'head', 'fov': 60, 'post': AIR},
        {'x': 19.6, 'y': 28.0, 'height': 0.35, 'look_at': [17.0, 24.6, 0.35], 'fov': 50,
         'post': [{'fx': 'dof', 'blur': 2.2}] + AIR},
        {'x': 3.6, 'y': 30.4, 'height': 0.45, 'look_at': [20.0, 28.0, 0.6], 'fov': 70, 'post': AIR},
    ],
    contact_shadows=0.3,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'glow_jungle.json')))

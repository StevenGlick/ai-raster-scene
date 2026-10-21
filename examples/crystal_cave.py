"""Crystal cave: a great cavern under the hill, a glowing lake in it and a crystal grown taller than
a man on the island in the middle, clusters of crystals round its walls, plants that give their own
light along the shore.

Shows `crystal_cluster` objects - every facet of every crystal bends the light through it its own
way, so each shows its own shifted piece of the cave behind, the colours parting at the edges - with
the lights they give; the walls lined with `rock_wall`s of `cave` rock, and of `lumen` rock (glowing
moss) along the lake; `boulder`s with mushrooms on them; the glowing jungle's plants (`glow_fern`,
`glow_bromeliad`, `glow_pods`, `glowshroom`, a `glow_liana` hanging from the roof) on `lumen_floor`;
a lake of `glow_water` that mirrors it all; a ground mist that takes the glow. A survey robot at the
mouth of the passage, and something large wading in the lake. Run:  python crystal_cave.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.6, 'radius': 2.5, 'spread': 0.55}  # the lights glow
AIR = [{'fx': 'spores', 'count': 6, 'glow': 0.6, 'colors': [[0.5, 1.0, 0.9], [0.8, 0.6, 1.0]]}, GLOW]

g = Grid(40, 34, fill='#')
g.disc(20, 29, 3.4, '.')                              # the chamber at the foot of the way in
g.rect(18, 21, 22, 30, '.')                           # the passage north
g.disc(20, 13, 10.5, '.')                             # the great cavern
g.disc(9.5, 12, 4.5, '.')                             # a grotto west
g.disc(30.5, 8.5, 4.0, '.')                           # and one east
g.disc(20, 12, 7.4, ',')                              # glowing moss round the lake
g.disc(20, 12, 6.2, '~')                              # the lake
g.disc(20, 10.4, 1.7, 'i')                            # the island, where the great crystal grows
for cx, cy in ((12, 5), (20, 1), (29, 4), (32, 14), (10, 18), (5, 10)):   # stretches of wall whose rock glows
    for y in range(cy - 5, cy + 6):
        for x in range(cx - 5, cx + 6):
            if (x - cx) ** 2 + (y - cy) ** 2 < 18 and g.get(x, y) == '#':
                g.put(x, y, '%')
cyan, violet, rose, green = [0.4, 0.9, 1.0], [0.7, 0.5, 1.0], [1.0, 0.45, 0.75], [0.45, 1.0, 0.65]

clusters = [  # (x, y, colour, size, count, seed)
    (20.0, 10.4, 'cyan', 2.4, 7, 1), (20.0, 3.4, 'violet', 1.6, 6, 2), (14.6, 6.6, 'cyan', 1.2, 5, 3),
    (26.8, 5.0, 'rose', 1.3, 5, 4), (7.0, 11.0, 'violet', 1.4, 6, 5), (9.6, 15.6, 'cyan', 0.8, 4, 6),
    (32.4, 7.6, 'green', 1.2, 5, 7), (29.2, 12.4, 'cyan', 0.7, 4, 8), (16.4, 21.4, 'violet', 0.8, 4, 9),
    (23.8, 20.8, 'cyan', 0.9, 5, 10), (14.2, 16.6, 'rose', 0.5, 4, 11), (25.8, 16.0, 'violet', 0.9, 5, 12),
]
objects = [{'type': 'crystal_cluster', 'x': x, 'y': y, 'color': c, 'size': s, 'count': n, 'seed': k}
           for x, y, c, s, n, k in clusters]
objects += [{'type': 'rock_wall', 'lining': '#', 'rock': 'cave', 'depth': 0.8, 'height': [0.7, 1.9],
             'pieces': [1.2, 2.4], 'seed': 2},
            {'type': 'rock_wall', 'lining': '%', 'rock': 'lumen', 'depth': 0.8, 'height': [0.6, 1.5],
             'pieces': [1.2, 2.4], 'seed': 3}]
objects += [{'type': 'boulder', 'x': x, 'y': y, 'angle': a, 'size': s_, 'height': h_, 'rock': 'cave', 'seed': 20 + k,
             'plants': 2} for k, (x, y, a, s_, h_) in enumerate(((17.0, 24.4, 30, 0.9, 0.5), (24.2, 23.6, 200, 0.7, 0.4),
                                                                (11.6, 10.0, 90, 1.0, 0.55), (28.4, 10.0, 160, 0.8, 0.45)))]

plants = [('glow_fern', 13.6, 13.2), ('glow_bromeliad', 14.0, 10.6), ('glowshroom', 13.8, 14.2), ('glow_fern', 26.2, 9.0),
          ('glow_bromeliad', 26.6, 13.4), ('glowshroom', 25.4, 8.0), ('glow_fern', 17.4, 18.6), ('glow_bromeliad', 22.8, 18.8),
          ('glowshroom', 20.6, 19.4), ('glow_fern', 16.0, 6.6), ('glow_fern', 24.4, 6.4), ('glowshroom', 18.2, 5.6),
          ('glow_bromeliad', 19.2, 9.4), ('glowshroom', 21.2, 11.4), ('glow_fern', 8.4, 13.6), ('glowshroom', 31.0, 10.2),
          ('glow_fern', 21.6, 25.6), ('glowshroom', 18.6, 27.2)]
sprites = [{'x': x, 'y': y, 'type': t, 'flip': k % 2 == 1} for k, (t, x, y) in enumerate(plants)]
sprites += [{'x': x, 'y': y, 'type': 'glow_pods', 'scale': s, 'flip': k % 2 == 1} for k, (x, y, s) in enumerate(
    ((14.8, 12.2, 0.9), (25.6, 11.8, 1.0), (16.2, 17.6, 0.8), (10.4, 9.6, 0.9)))]
sprites += [
    {'id': 'robot', 'x': 17.4, 'y': 20.2, 'type': 'robot', 'facing': 300},
    {'id': 'beast', 'x': 21.6, 'y': 13.8, 'type': 'creature', 'scale': 1.3,  # wading, before the great crystal
     'light': {'radius': 2.8, 'color': [1.0, 0.35, 0.25], 'intensity': 1.0, 'z': 0.5}},
]
lights = [{'x': x, 'y': y, 'z': 0.35, 'radius': r, 'color': c, 'intensity': i} for x, y, r, c, i in
          ((14.0, 12.4, 3.0, cyan, 0.7), (26.0, 11.0, 3.0, green, 0.6), (20.0, 19.0, 3.0, cyan, 0.6),
           (20.0, 6.4, 3.0, violet, 0.5), (8.6, 13.2, 2.6, cyan, 0.6), (21.0, 26.0, 3.0, green, 0.5))]

s = scene(
    g,
    title='Crystal cave - a glowing lake under the hill, ringed with crystals',
    legend={
        '#': {'wall': 'rock_wet', 'h': 2.8},
        '%': {'wall': 'rock_wet', 'h': 2.8},
        '.': {'floor': 'rock_floor', 'ceil': 'rock'},
        ',': {'floor': 'lumen_floor', 'ceil': 'rock'},
        'i': {'floor': 'lumen_floor', 'ceil': 'rock'},
        '~': {'floor': 'glow_water', 'drop': 0.2, 'side': 'rock_floor', 'reflect': 0.6, 'ceil': 'rock'},
    },
    ceiling_height=2.8,
    sky=None,
    ambient=[0.08, 0.085, 0.11],
    fog={'color': [0.02, 0.03, 0.05], 'density': 0.01, 'ground': 0.08, 'height': 0.3, 'noise': 0.5, 'glow': 0.5},
    lights=lights,
    objects=objects,
    sprites=sprites,
    scatter=[{'of': 'cave', 'on': '.', 'density': 0.3, 'clump': 1.6, 'sizes': ['tiny', 'small'], 'seed': 3}],
    camera={'x': 18.6, 'y': 19.6, 'look_at': [20.0, 10.4, 1.0], 'fov': 74, 'height': 0.45},
    shots=[
        {'x': 18.6, 'y': 19.6, 'look_at': [20.0, 10.4, 1.0], 'fov': 74, 'height': 0.45, 'post': AIR,
         'overlays': [{'type': 'caption', 'text': 'The lake under the hill', 'at': 'top', 'box': True}]},
        {'x': 19.4, 'y': 23.2, 'look_at': 'robot', 'fov': 60, 'post': [GLOW],
         'overlays': [{'type': 'bubble', 'anchor': 'robot', 'name': 'Survey unit',
                       'text': 'Mineral glow detected. Life signs: one. Large.'}]},
        {'x': 23.6, 'y': 18.6, 'look_at': 'beast', 'fov': 46, 'post': [GLOW, {'fx': 'vignette', 'strength': 0.6}]},
        {'x': 27.2, 'y': 18.0, 'look_at': [25.6, 15.6, 0.45], 'fov': 54, 'height': 0.4, 'post': AIR},
        {'x': 21.8, 'y': 13.4, 'look_at': [20.0, 10.4, 1.0], 'fov': 62, 'height': 0.45, 'post': AIR},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crystal_cave.json')))

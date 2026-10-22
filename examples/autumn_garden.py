"""Autumn garden: a Japanese garden in autumn - a red gate on the gravel path, stone lanterns, maples turned
scarlet and gold, a pond with a plank bridge and boulders of mossy stone, and a tea house under a roof of
grey tiles; by day, and at dusk with the lanterns lit.

Shows a gate of painted wood in 3D (two `column`s of `lime_red`, a tie beam and a top beam of
`lacquer_black`), `stone_lantern` objects (lit: their flames glow at dusk), a tea house of white walls under
a `gable_roof` of `slate` with deep eaves, a plank bridge with red rails (`beam`s), `boulder`s of `stone`
by the water, a pond of still `water` that mirrors it all, `tree_autumn` and `bush_autumn` maples, and the
wood round the garden in its autumn fringe, wandering.
Run:  python autumn_garden.py  -> writes autumn_garden.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

LAMP = [1.0, 0.7, 0.38]


def autumn_garden():
    g = Grid(32, 36, fill='F')                     # the wood all round
    g.rect(4, 4, 27, 33, ',')                      # the garden: moss and grass
    g.rect(14, 5, 20, 8, 'H')                      # the tea house
    g.put(17, 8, 'D')                              # its door, looking down the garden
    g.rect(13, 9, 21, 9, 'v')                      # its veranda
    g.rect(16, 10, 18, 33, 'p')                    # the gravel path, up from the gate to the tea house
    g.disc(17, 17, 4.6, '~')                       # the pond across it
    g.rect(17, 12, 17, 22, 'J')                    # and the plank bridge over the pond
    objects = [
        # the gate on the path
        {'type': 'column', 'x': 15.8, 'y': 27.0, 'material': 'lime_red', 'sides': 12, 'radius': 0.12, 'top': 0.85,
         'height': 2.8, 'sink': 0.0, 'seed': 1},
        {'type': 'column', 'x': 19.2, 'y': 27.0, 'material': 'lime_red', 'sides': 12, 'radius': 0.12, 'top': 0.85,
         'height': 2.8, 'sink': 0.0, 'seed': 2},
        {'type': 'beam', 'x': 17.5, 'y': 27.0, 'z': 2.3, 'angle': 0, 'length': 4.0, 'width': 0.12, 'depth': 0.14,
         'material': 'lime_red', 'seed': 3},
        {'type': 'beam', 'x': 17.5, 'y': 27.0, 'z': 2.8, 'angle': 0, 'length': 4.8, 'width': 0.22, 'depth': 0.18,
         'material': 'lacquer_black', 'seed': 4},
        # the tea house's roof: grey tiles, deep eaves
        {'type': 'gable_roof', 'x': 17.5, 'y': 7.0, 'z': 1.3, 'angle': 0, 'length': 7.0, 'width': 4.0, 'rise': 1.4,
         'cover': 'slate', 'overhang': [0.7, 0.5], 'plaster': '#e8e2d2', 'seed': 5},
        # the bridge's rails
        *[{'type': 'beam', 'x': x, 'y': 17.5, 'z': 0.55, 'angle': 90, 'length': 11.0, 'width': 0.07, 'depth': 0.07,
           'material': 'lime_red', 'seed': 6 + k} for k, x in enumerate((16.95, 18.05))],
        *[{'type': 'column', 'x': x, 'y': y, 'material': 'lime_red', 'sides': 4, 'radius': 0.05, 'height': 0.6,
           'sink': 0.0, 'seed': 10 + k} for k, (x, y) in enumerate((x, y) for y in (12.2, 15.0, 17.5, 20.0, 22.8)
                                                                  for x in (16.95, 18.05))],
        # boulders of mossy stone by the water
        *[{'type': 'boulder', 'x': x, 'y': y, 'size': s_, 'height': h, 'rock': 'stone', 'angle': a, 'plants': 2,
           'seed': 30 + k} for k, (x, y, s_, h, a) in enumerate(((13.0, 14.0, 1.1, 0.6, 30), (21.6, 20.8, 0.9, 0.5, 120),
                                                                 (12.6, 20.6, 0.7, 0.4, 200), (20.8, 13.2, 0.6, 0.36, 300)))],
        # stone lanterns along the path and by the pond
        *[{'type': 'stone_lantern', 'x': x, 'y': y, 'height': h, 'seed': 40 + k}
          for k, (x, y, h) in enumerate(((15.2, 26.0, 1.1), (19.8, 24.6, 1.0), (14.4, 21.8, 0.9), (22.6, 15.4, 1.2),
                                         (15.4, 10.2, 1.0)))],
    ]
    sprites = [
        # the maples, scarlet and gold, and a few pines among them
        *[{'x': x, 'y': y, 'type': 'tree_autumn', 'scale': s_, 'flip': k % 2 == 1}
          for k, (x, y, s_) in enumerate(((8.0, 12.0, 3.4), (25.0, 10.0, 3.0), (9.4, 24.0, 3.2), (25.6, 26.0, 3.6),
                                          (11.0, 30.0, 2.8), (23.6, 31.0, 2.6), (6.6, 18.0, 2.6),
                                          (13.0, 24.2, 3.0), (25.6, 21.0, 3.2), (12.0, 12.4, 3.0), (23.0, 11.2, 2.8)))],
        *[{'x': x, 'y': y, 'type': 'pine', 'scale': s_} for x, y, s_ in ((6.0, 7.0, 3.6), (27.0, 18.0, 3.8))],
        *[{'x': x, 'y': y, 'type': 'bush_autumn', 'flip': k % 2 == 1}
          for k, (x, y) in enumerate(((12.0, 26.0), (21.6, 27.4), (11.6, 9.6), (23.4, 9.2), (9.0, 15.4), (24.6, 22.4),
                                      (13.8, 21.6), (20.6, 13.4), (20.4, 22.0)))],
        # people: a figure on the bridge, the host at the tea house door
        {'id': 'walker', 'x': 17.5, 'y': 16.2, 'type': 'samurai', 'facing': 270},
        {'id': 'host', 'x': 17.5, 'y': 9.4, 'type': 'monk', 'facing': 90},
    ]
    decals = [{'tex': 'lily_pads', 'surface': 'floor', 'x': x, 'y': y, 'size': s_}
              for x, y, s_ in ((15.0, 15.4, 1.2), (19.6, 19.6, 1.0), (14.2, 19.0, 0.9))]
    lantern_lights = [{'x': x, 'y': y, 'z': 0.7, 'radius': 3.0, 'color': LAMP, 'intensity': 1.6}
                      for x, y in ((15.2, 26.0), (19.8, 24.6), (14.4, 21.8), (22.6, 15.4), (15.4, 10.2))]
    sun = {'type': 'sun', 'azimuth': 230, 'elevation': 22, 'color': [1.0, 0.86, 0.66], 'intensity': 1.0}
    return scene(
        g,
        legend={
            'F': {'wall': 'forest_deep_autumn', 'h': 2.4, 'fringe': {'set': 'forest_autumn', 'depth': 1.2, 'wander': 0.3}},
            ',': {'floor': 'grass'},
            '~': {'floor': 'water', 'drop': 0.14, 'reflect': 0.62},
            'J': {'wall': 'boards', 'h': 0.2, 'top': 'boards'},
            'H': {'wall': {'base': 'plaster_white', 'tint': [0.96, 0.94, 0.88]}, 'h': 1.3, 'top': 'boards'},
            'D': {'wall': ['door_wood'], 'h': 1.3, 'top': 'boards'},
            'v': {'wall': 'boards', 'h': 0.15, 'top': 'boards'},
            'p': {'floor': 'gravel'},
        },
        title='Autumn garden - the gate, the lanterns and the tea house',
        sky='golden',
        ambient=[0.36, 0.33, 0.32],
        fog={'color': [0.86, 0.72, 0.6], 'density': 0.01, 'sky_mix': 0.2},
        lights=[sun],
        sprites=sprites,
        objects=objects,
        decals=decals,
        scatter=[{'of': 'autumn', 'on': ',', 'density': 0.12, 'sizes': ['tiny', 'small'], 'seed': 4}],
        camera={'x': 17.5, 'y': 33.2, 'look_at': [17.5, 12.0, 1.5], 'fov': 62},
        shots=[
            {'x': 17.5, 'y': 33.2, 'look_at': [17.5, 12.0, 1.5], 'fov': 62,
             'overlays': [{'type': 'caption', 'text': 'The garden in autumn', 'at': 'top', 'box': True}]},
            {'x': 23.6, 'y': 25.0, 'look_at': [15.0, 12.0, 1.0], 'fov': 64},
            {'x': 17.5, 'y': 30.6, 'look_at': [17.5, 12.0, 1.3], 'fov': 64,   # up the path at dusk, the lanterns lit
             'overrides': {'sky': 'dusk', 'ambient': [0.2, 0.17, 0.22],
                           'lights': [dict(sun, elevation=3, intensity=0.35, color=[1.0, 0.55, 0.4])] + lantern_lights
                           + [{'x': 17.5, 'y': 9.6, 'z': 0.9, 'radius': 3.4, 'color': LAMP, 'intensity': 1.4}],
                           'fog': {'color': [0.2, 0.16, 0.24], 'density': 0.018, 'glow': 0.9}},
             'post': [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.5}]},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(autumn_garden().save(os.path.join(HERE, 'autumn_garden.json')))

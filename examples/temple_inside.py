"""Inside the jungle temple: a narrow passage of carved glyphs running into the pyramid, and at its heart
a sanctum where a golden idol sits on its altar in a single shaft of sun through the broken roof, roots
and lianas coming down with the light, the floor flooded and mirroring it.

Shows the jungle kit's stone indoors (`glyphs`, `temple_stone`, `temple_roots`, `ruin_paving`), the
temple kit (scripts/temple.py: a `golden_idol`, `treasure`), pillars and the altar built in 3D
(`column`s and a `beam` of `stone`, moss on their tops), a roof hole letting the sun in through
volumetric fog, `brazier`s, `stela`s, `liana`s, and the `explorer`.
Run:  python temple_inside.py  -> writes temple_inside.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

FIRE = [1.0, 0.58, 0.26]


def temple_inside():
    g = Grid(13, 23, fill='X')                     # the pyramid's stone
    g.rect(3, 3, 9, 8, '.')                        # the sanctum
    g.put(6, 4, 'O')                               # the broken roof over the altar
    g.rect(3, 7, 9, 8, 'w')                        # its floor flooded at the front
    g.rect(5, 2, 7, 2, 'R')                        # roots through the wall behind the altar
    g.rect(6, 9, 6, 19, 'p')                       # the passage in, one cell wide
    for y in range(9, 20):
        if y % 2:
            g.put(5, y, 'G').put(7, y, 'G')        # carved glyphs down it
    g.rect(4, 20, 8, 22, 'j')                      # the jungle at the door
    g.rect(3, 20, 3, 22, 'L').rect(9, 20, 9, 22, 'L')
    objects = [{'type': 'column', 'x': x, 'y': y, 'material': 'stone', 'sides': 4, 'radius': 0.24, 'height': 1.4,
                'base': 0.12, 'capital': 0.14, 'sink': 0.0, 'seed': k}
               for k, (x, y) in enumerate(((4.4, 4.4), (8.6, 4.4), (4.4, 6.6), (8.6, 6.6)))]
    objects.append({'type': 'beam', 'x': 6.5, 'y': 4.6, 'z': 0.0, 'angle': 0, 'length': 1.0, 'width': 0.66,
                    'depth': 0.36, 'material': 'stone', 'seed': 9})             # the altar
    sprites = [
        {'id': 'idol', 'x': 6.5, 'y': 4.6, 'z': 0.36, 'type': 'golden_idol'},
        {'x': 6.0, 'y': 5.15, 'type': 'treasure'}, {'x': 7.1, 'y': 4.2, 'type': 'treasure', 'flip': True},
        {'x': 5.3, 'y': 3.4, 'type': 'stela', 'scale': 1.0}, {'x': 7.7, 'y': 3.4, 'type': 'stela', 'flip': True, 'scale': 1.0},
        {'x': 6.15, 'y': 4.1, 'type': 'liana', 'scale': 1.2}, {'x': 6.95, 'y': 4.05, 'type': 'liana', 'scale': 1.05, 'flip': True},
        {'x': 3.6, 'y': 3.5, 'type': 'fern'}, {'x': 9.3, 'y': 3.6, 'type': 'fern', 'flip': True},
        {'x': 4.0, 'y': 8.6, 'type': 'brazier'}, {'x': 9.0, 'y': 8.6, 'type': 'brazier'},
        {'x': 3.5, 'y': 6.0, 'type': 'bones'}, {'x': 9.4, 'y': 5.2, 'type': 'clay_pot'},
        {'x': 6.3, 'y': 15.0, 'type': 'bones', 'flip': True}, {'x': 6.7, 'y': 17.5, 'type': 'clay_pot'},
        {'id': 'explorer', 'x': 6.5, 'y': 11.2, 'type': 'explorer', 'facing': 270},
    ]
    decals = [{'tex': 'cobweb', 'surface': 'wall', 'cell': [x, y], 'face': f, 'u': 0.5, 'z': 1.1, 'size': 0.6}
              for x, y, f in ((2, 4, 'east'), (10, 6, 'west'), (5, 13, 'east'))] + [
              {'tex': 'moss_patch', 'surface': 'floor', 'x': x, 'y': y, 'size': 1.2} for x, y in ((4.0, 3.6), (8.8, 3.8))]
    lights = [{'x': 4.0, 'y': 8.6, 'z': 0.5, 'radius': 3.6, 'color': FIRE, 'intensity': 1.6},
              {'x': 9.0, 'y': 8.6, 'z': 0.5, 'radius': 3.6, 'color': FIRE, 'intensity': 1.6},
              {'x': 6.5, 'y': 4.6, 'z': 0.75, 'radius': 1.4, 'color': [1.0, 0.8, 0.4], 'intensity': 0.9},   # its gleam
              {'x': 6.5, 'y': 12.5, 'z': 0.9, 'radius': 2.4, 'color': FIRE, 'intensity': 0.7},             # a torch
              {'type': 'sun', 'azimuth': 270, 'elevation': 72, 'color': [1.0, 0.95, 0.78], 'intensity': 2.2,
               'disc': False}]
    return scene(
        g,
        legend={
            'X': {'wall': 'temple_stone', 'h': 1.4},
            'G': {'wall': 'glyphs', 'h': 1.4},
            'R': {'wall': 'temple_roots', 'h': 1.4},
            'L': {'wall': 'jungle_leaves', 'h': 2.6},
            '.': {'floor': 'ruin_paving', 'ceil': 'temple_stone'},
            'O': {'floor': 'ruin_paving'},
            'w': {'floor': {'base': 'water', 'tint': [0.5, 0.6, 0.5]}, 'drop': 0.05, 'reflect': 0.6, 'ceil': 'temple_stone'},
            'p': {'floor': 'ruin_paving', 'ceil': 'temple_stone'},
            'j': {'floor': 'jungle_floor'},
        },
        title='Inside the temple - the idol in its shaft of sun',
        sky='day',
        ceiling_height=1.4,
        ambient=[0.13, 0.13, 0.1],
        fog={'color': [0.26, 0.25, 0.18], 'density': 0.06, 'glow': 0.6, 'shafts': 4.5},
        lights=lights,
        sprites=sprites,
        decals=decals,
        objects=objects,
        camera={'x': 6.5, 'y': 14.6, 'angle': 270, 'fov': 60},
        shots=[
            {'x': 6.5, 'y': 14.6, 'angle': 270, 'fov': 60,
             'overlays': [{'type': 'caption', 'text': 'Into the temple', 'at': 'top', 'box': True}]},
            {'x': 6.5, 'y': 8.7, 'look_at': [6.5, 4.6, 0.55], 'fov': 66,
             'overlays': [{'type': 'caption', 'text': 'The idol of the jaguar', 'at': 'top', 'box': True}]},
            {'x': 6.9, 'y': 6.6, 'look_at': [6.6, 4.6, 0.5], 'fov': 56,
             'extra_sprites': [{'id': 'reacher', 'x': 7.4, 'y': 4.75, 'type': 'explorer', 'facing': 180}],
             'overlays': [{'type': 'bubble', 'anchor': 'reacher', 'name': 'The Explorer',
                           'text': 'Steady... nobody breathe.'}]},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(temple_inside().save(os.path.join(HERE, 'temple_inside.json')))

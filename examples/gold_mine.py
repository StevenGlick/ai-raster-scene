"""Gold mine: a frontier mine's tunnel, timbered every few paces, rails running down it into the dark,
lanterns hung on the timbers; a stope off it where a prospector works a vein of gold by lamplight;
and the portal in the hillside at dusk, the rails coming out to an ore cart.

Shows the mine kit (scripts/mine.py) and objects built in 3D: the timber sets are `column`s and
`beam`s of `wood` (square posts, a cap across), the track is a `rails` object and the cars are
`ore_cart`s; the rock is `mine_rock`, with a vein of quartz wandering across it, and the stope's
face `mine_rock_gold`, the gold in the vein glinting. A `pick_shovel`, a `dynamite_crate`, `ore_heap`s.
Outside, the hill's face is lined with `canyon` rock.
Run:  python gold_mine.py  -> writes gold_mine.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

WARM = [1.0, 0.64, 0.3]
SETS = [2.6 + 1.3 * k for k in range(13)]          # where the timber sets stand along the tunnel


def gold_mine():
    g = Grid(13, 27, fill='H')                     # the hill
    g.rect(4, 0, 12, 18, 'R')                      # the rock round the workings
    g.put(4, 19, 'R').put(7, 19, 'R')              # the portal cut in it
    for x, y in ((4, 5), (7, 13), (4, 15), (4, 9)):
        g.put(x, y, 'V')                           # a seam of quartz showing here and there
    g.rect(5, 2, 6, 19, '.')                       # the tunnel, two cells wide, out to the portal
    g.rect(7, 6, 10, 10, 'S')                      # the stope off it
    g.rect(11, 6, 11, 10, 'G')                     # the face of the stope: the vein of gold
    g.rect(0, 20, 12, 26, 'D')                     # the desert outside
    objects = []
    for k, y in enumerate(SETS):                   # the timber sets: two posts and a cap
        for x in (5.08, 6.92):
            objects.append({'type': 'column', 'x': x, 'y': y, 'material': 'wood', 'sides': 4, 'radius': 0.075,
                            'height': 0.97, 'sink': 0.0, 'seed': 3 * k + (x > 6)})
        objects.append({'type': 'beam', 'x': 6.0, 'y': y, 'z': 0.88, 'angle': 0, 'length': 1.96, 'width': 0.1,
                        'depth': 0.09, 'material': 'wood', 'seed': 7 * k})
    for x in (4.98, 7.02):                         # the portal's heavier set
        objects.append({'type': 'column', 'x': x, 'y': 19.85, 'material': 'wood', 'sides': 4, 'radius': 0.1,
                        'height': 1.1, 'sink': 0.0, 'seed': 41 + (x > 6)})
    objects.append({'type': 'beam', 'x': 6.0, 'y': 19.85, 'z': 0.98, 'angle': 0, 'length': 2.4, 'width': 0.14,
                    'depth': 0.12, 'material': 'wood', 'seed': 43})
    objects += [{'type': 'rails', 'x': 6.0, 'y': 13.3, 'angle': 90, 'length': 22.6},
                {'type': 'ore_cart', 'x': 6.0, 'y': 11.4, 'angle': 90},
                {'type': 'ore_cart', 'x': 6.0, 'y': 21.6, 'angle': 90, 'ore': True},
                # the hillside in beds of red and pale stone, and closed over the portal by a mass of it
                {'type': 'rock_wall', 'x': 0, 'y': 0, 'lining': 'H', 'rock': 'canyon', 'depth': 0.8,
                 'height': [2.7, 3.5], 'trim': 0.05, 'pieces': [2.0, 3.4], 'seed': 6},
                {'type': 'rock_wall', 'x': 6.0, 'y': 19.05, 'z': 0.98, 'angle': 90, 'length': 4.2, 'depth': 0.5,
                 'height': [1.9, 2.1], 'trim': 0.04, 'pieces': [1.2, 1.6], 'rock': 'canyon', 'back': True,
                 'plants': False, 'seed': 9}]
    sprites = [
        {'x': 5.18, 'y': y, 'z': 0.6, 'type': 'lantern', 'scale': 0.2} for y in SETS[1::3]
    ] + [
        # the stope: the prospector at the face, his lamp on a post, the ore he has broken
        {'id': 'prospector', 'x': 10.35, 'y': 8.3, 'type': 'cowboy', 'facing': 0, 'tint': [0.82, 0.76, 0.66]},
        {'x': 10.6, 'y': 7.2, 'type': 'lantern', 'z': 0.55, 'scale': 0.2},
        {'x': 9.6, 'y': 9.4, 'type': 'ore_heap', 'scale': 0.16}, {'x': 10.7, 'y': 9.3, 'type': 'ore_heap', 'scale': 0.12},
        {'x': 7.4, 'y': 6.3, 'type': 'pick_shovel'}, {'x': 8.2, 'y': 9.7, 'type': 'dynamite_crate'},
        {'x': 7.6, 'y': 9.5, 'type': 'sack', 'scale': 0.3},
        # outside: barrels by the portal, the desert
        {'x': 4.4, 'y': 20.5, 'type': 'barrel'}, {'x': 7.7, 'y': 20.7, 'type': 'crate'},
        {'x': 2.0, 'y': 24.0, 'type': 'saguaro', 'scale': 2.6}, {'x': 10.5, 'y': 25.0, 'type': 'prickly_pear'},
    ]
    lights = ([{'x': 5.3, 'y': y, 'z': 0.62, 'radius': 2.6, 'color': WARM, 'intensity': 1.1} for y in SETS[1::3]]
              + [{'x': 10.5, 'y': 7.3, 'z': 0.6, 'radius': 2.6, 'color': WARM, 'intensity': 1.3}])
    return scene(
        g,
        legend={
            'H': {'wall': ['sandstone', 'sandstone_pale', 'sandstone'], 'h': 3.0, 'top': 'desert_wash'},
            'V': {'wall': 'mine_rock_vein', 'h': 1.0, 'top': 'desert_wash'},
            'R': {'wall': 'mine_rock', 'h': 1.0, 'top': 'desert_wash'},            # as tall as the roof inside
            'G': {'wall': 'mine_rock_gold', 'h': 1.0, 'top': 'desert_wash'},
            '.': {'floor': 'rock_floor', 'ceil': 'boards'},
            'S': {'floor': 'rock_floor', 'ceil': 'mine_rock'},
            'D': {'floor': 'desert_wash'},
        },
        title='Gold mine - the tunnel, the vein, the portal at dusk',
        sky='sunset',
        ceiling_height=1.0,
        ambient=[0.05, 0.045, 0.04],
        fog={'color': [0.14, 0.11, 0.08], 'density': 0.05, 'glow': 0.7},
        lights=lights,
        sprites=sprites,
        objects=objects,
        scatter=[{'of': 'desert', 'on': 'D', 'density': 0.15, 'sizes': {'tiny': 4, 'small': 2}, 'seed': 3}],
        camera={'x': 6.0, 'y': 18.6, 'angle': 270, 'fov': 62},
        shots=[
            {'x': 6.0, 'y': 18.6, 'angle': 270, 'fov': 62, 'pitch': 0.02,
             'overlays': [{'type': 'caption', 'text': 'Into the mine', 'at': 'top', 'box': True}]},
            {'x': 7.6, 'y': 9.6, 'look_at': [10.9, 7.6, 0.45], 'fov': 60,
             'overlays': [{'type': 'bubble', 'anchor': 'prospector', 'name': 'The Prospector',
                           'text': 'Color! Look at her shine, partner.'}]},
            {'x': 6.9, 'y': 25.4, 'look_at': [6.0, 19.0, 0.9], 'fov': 64,
             'overrides': {'ambient': [0.3, 0.22, 0.24],
                           'lights': [{'type': 'sun', 'azimuth': 200, 'elevation': 8, 'intensity': 0.8}] + lights,
                           'fog': {'color': [0.6, 0.4, 0.34], 'density': 0.01}}},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(gold_mine().save(os.path.join(HERE, 'gold_mine.json')))

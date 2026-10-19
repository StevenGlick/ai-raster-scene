"""Authoring an exterior with maptools: a forest path, a bend and a clearing.
Run: python woodland_night.py  -> writes woodland_night.json next to this file.

The thicket is a solid fill of foliage wall cells; the path is carved out of it with
rect(), and bark trunks are dropped into the wall where the camera can see them.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402


def woodland():
    g = Grid(36, 32, fill='F')                     # dense thicket everywhere
    g.rect(15, 19, 20, 31, ',')                    # south leg of the clearing floor
    g.rect(9, 15, 20, 20, ',')                     # the bend
    g.rect(9, 4, 14, 16, ',')                      # north leg
    g.rect(14, 8, 23, 13, ',')                     # spur east toward the clearing
    g.disc(26, 10, 5, ',')                         # the clearing
    g.rect(16, 20, 18, 31, 'p')                    # dirt track, south leg
    g.rect(10, 16, 18, 19, 'p')                    # dirt track, the bend
    g.rect(10, 4, 12, 16, 'p')                     # dirt track, north leg
    g.rect(14, 10, 22, 11, 'p')                    # dirt track, spur
    # bark trunks standing in the thicket wall where the path can see them
    for (x, y) in ((14, 22), (21, 24), (14, 27), (21, 18), (8, 12), (15, 14),
                   (8, 6), (22, 8), (23, 14), (31, 9), (21, 29), (13, 3)):
        g.put(x, y, 'B')
    return scene(
        g,
        legend={
            'F': {'wall': 'foliage', 'h': 3.2},
            'B': {'wall': 'bark', 'h': 3.6, 'top': 'foliage'},
            ',': {'floor': 'pine_needles'},
            'p': {'floor': 'mud'},
        },
        title='Woodland at night - a lantern on the forest path',
        ceiling_height=1.0,
        sky='night',
        ambient=[0.13, 0.14, 0.20],
        fog={'color': [0.03, 0.035, 0.055], 'density': 0.035, 'sky_mix': 0.35},
        lights=[
            {'x': 26.5, 'y': 10.5, 'z': 0.35, 'radius': 9.0, 'color': [1.0, 0.62, 0.28], 'intensity': 2.2},
            {'x': 16.0, 'y': 18.4, 'z': 0.5, 'radius': 5.5, 'color': [1.0, 0.72, 0.38], 'intensity': 1.4},
            {'x': 11.0, 'y': 6.5, 'z': 1.4, 'radius': 7.0, 'color': [0.5, 0.62, 0.92], 'intensity': 0.9},
            {'x': 17.5, 'y': 24.0, 'z': 1.4, 'radius': 7.0, 'color': [0.45, 0.56, 0.88], 'intensity': 0.7},
            {'x': 17.0, 'y': 29.5, 'z': 1.4, 'radius': 6.0, 'color': [0.45, 0.56, 0.88], 'intensity': 0.6},
            {'x': 12.0, 'y': 12.0, 'z': 1.4, 'radius': 6.5, 'color': [0.48, 0.58, 0.90], 'intensity': 0.65},
            {'x': 19.5, 'y': 11.0, 'z': 1.4, 'radius': 6.0, 'color': [0.5, 0.60, 0.88], 'intensity': 0.5},
        ],
        sprites=[
            {'x': 14.4, 'y': 26.5, 'type': 'pine'}, {'x': 20.6, 'y': 28.5, 'type': 'pine'},
            {'x': 14.5, 'y': 21.0, 'type': 'pine'}, {'x': 20.5, 'y': 22.0, 'type': 'pine', 'flip': True},
            {'x': 9.6, 'y': 9.5, 'type': 'pine'}, {'x': 13.4, 'y': 6.0, 'type': 'pine', 'flip': True},
            {'x': 22.5, 'y': 12.6, 'type': 'pine'}, {'x': 15.5, 'y': 9.0, 'type': 'pine', 'flip': True},
            {'x': 23.0, 'y': 7.0, 'type': 'dead_tree'}, {'x': 29.5, 'y': 12.5, 'type': 'dead_tree', 'flip': True},
            {'x': 16.0, 'y': 18.4, 'type': 'stump'}, {'x': 19.4, 'y': 25.6, 'type': 'log'},
            {'x': 15.3, 'y': 29.0, 'type': 'bush'}, {'x': 19.7, 'y': 20.6, 'type': 'bush'},
            {'x': 9.6, 'y': 13.5, 'type': 'bush'}, {'x': 13.5, 'y': 12.0, 'type': 'fern'},
            {'x': 18.6, 'y': 23.2, 'type': 'mushrooms'}, {'x': 11.4, 'y': 10.5, 'type': 'mushrooms'},
            {'x': 10.4, 'y': 18.6, 'type': 'boulder'}, {'x': 22.6, 'y': 10.4, 'type': 'boulder'},
            {'x': 16.0, 'y': 18.4, 'type': 'lantern', 'z': 0.3},
            {'x': 26.5, 'y': 10.5, 'type': 'campfire', 'scale': 0.8},
            {'id': 'watcher', 'x': 27.6, 'y': 12.2, 'type': 'cultist',
             'light': {'radius': 2.6, 'color': [1.0, 0.68, 0.35], 'intensity': 0.9, 'z': 0.45}},
            {'x': 24.6, 'y': 8.4, 'type': 'crate'},
            # undergrowth and forest-floor litter
            {'x': 15.4, 'y': 24.0, 'type': 'grass_tuft'}, {'x': 19.6, 'y': 27.0, 'type': 'grass_tuft'},
            {'x': 15.6, 'y': 29.6, 'type': 'grass_tuft'}, {'x': 10.4, 'y': 8.0, 'type': 'grass_tuft'},
            {'x': 20.4, 'y': 11.4, 'type': 'grass_tuft'}, {'x': 12.6, 'y': 19.4, 'type': 'grass_tuft'},
            {'x': 19.5, 'y': 22.4, 'type': 'rocks'}, {'x': 16.4, 'y': 26.2, 'type': 'rocks'},
            {'x': 11.6, 'y': 11.0, 'type': 'rocks'}, {'x': 24.0, 'y': 12.8, 'type': 'rocks'},
            {'x': 15.5, 'y': 20.2, 'type': 'rubble'}, {'x': 28.4, 'y': 8.6, 'type': 'bones'},
            {'x': 25.4, 'y': 7.6, 'type': 'broken_barrel'}, {'x': 23.8, 'y': 9.2, 'type': 'sack'},
            {'x': 14.6, 'y': 28.2, 'type': 'ivy_hang', 'z': 1.9},
            # litter around the fire, inside the clearing shot's cone
            {'x': 25.6, 'y': 11.9, 'type': 'rocks'}, {'x': 24.9, 'y': 12.3, 'type': 'grass_tuft'},
            {'x': 28.4, 'y': 11.4, 'type': 'grass_tuft'}, {'x': 27.2, 'y': 12.6, 'type': 'bones'},
            {'x': 29.0, 'y': 10.6, 'type': 'rubble'},
        ],
        decals=[
            {'tex': 'puddle', 'surface': 'floor', 'x': 17.2, 'y': 27.4, 'size': 1.8},
            {'tex': 'puddle_dark', 'surface': 'floor', 'x': 16.6, 'y': 22.6, 'size': 1.5},
            {'tex': 'puddle', 'surface': 'floor', 'x': 11.4, 'y': 8.6, 'size': 1.4},
            {'tex': 'moss_patch', 'surface': 'floor', 'x': 19.4, 'y': 24.6, 'size': 1.6, 'opacity': 0.75},
            {'tex': 'moss_patch', 'surface': 'floor', 'x': 15.2, 'y': 17.4, 'size': 1.4, 'opacity': 0.75},
            {'tex': 'stain', 'surface': 'floor', 'x': 26.5, 'y': 12.4, 'size': 1.6, 'opacity': 0.7},
            {'tex': 'vines', 'surface': 'wall', 'cell': [14, 27], 'face': 'east', 'u': 0.5, 'z': 2.3, 'size': 1.1},
            {'tex': 'moss_patch', 'surface': 'wall', 'cell': [21, 24], 'face': 'west', 'u': 0.5, 'z': 0.9, 'size': 1.0},
            {'tex': 'vines', 'surface': 'wall', 'cell': [21, 18], 'face': 'west', 'u': 0.5, 'z': 2.4, 'size': 1.0},
        ],
        scatter=[
            {'of': 'forest', 'on': ',', 'density': 0.5, 'clump': 1.3, 'seed': 1},
            {'of': 'stones', 'on': ',p', 'density': 1.1, 'clump': 1.1,
             'sizes': {'tiny': 6, 'small': 4, 'medium': 2, 'large': 0.6}, 'seed': 2},
            {'of': 'undergrowth', 'on': ',', 'density': 0.5, 'clump': 1.6, 'seed': 3},
        ],
        camera={'x': 17.5, 'y': 30.4, 'angle': 270, 'fov': 68, 'height': 0.5},
        shots=[
            {'x': 17.5, 'y': 30.4, 'angle': 270,
             'overlays': [{'type': 'viewmodel', 'item': 'lantern'},
                          {'type': 'caption', 'text': 'The old forest road', 'at': 'top', 'box': True}]},
            {'x': 23.0, 'y': 13.6, 'angle': 331, 'fov': 70,
             'overlays': [{'type': 'bubble', 'anchor': 'watcher', 'name': 'The Watcher',
                           'text': 'Sit. The fire does not care who you are.'}]},
            {'x': 18.2, 'y': 19.8, 'angle': 209, 'fov': 70, 'post': ['horror']},
            {'x': 19.5, 'y': 11.0, 'look_at': [27.0, 9.0, 0.6], 'fov': 74, 'flashlight': True},
        ],
        supersample=2,
    )

HERE = os.path.dirname(os.path.abspath(__file__))
print(woodland().save(os.path.join(HERE, 'woodland_night.json')))

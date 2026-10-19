"""Derelict ship: emergency lighting, a med bay of stasis pods, and a hive grown into the hull.

Shows red light-strip walls (`hull_red`), living `organic` walls, floors and ceilings taking over
the ship, stasis pods, alien eggs scattered with the `derelict` and custom scatter, and the same
corridor as horror-game and found-footage frames.
Run:  python derelict_ship.py  -> writes derelict_ship.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(22, 29, fill='#')
g.rect(3, 1, 17, 11, 'O')                             # the hive's living walls...
g.disc(10, 6, 5, 'h')                                 # ...round the chamber they have made
g.rect(9, 11, 10, 26, 'c')                            # the main corridor
for y in range(11, 27):
    for x in (8, 11):
        g.put(x, y, 'O' if y < 15 or (x == 8 and y in (19, 23)) else 'R')   # growth creeping south
g.rect(12, 15, 18, 22, 'm')                           # the med bay
g.put(11, 18, 'c')
g.put(11, 19, 'c')                                    # its doorway
for x in (13, 14, 16):
    g.put(x, 14, 'O')
g.rect(9, 27, 10, 27, 'B')                            # the sealed door behind you

red = [1.0, 0.16, 0.1]
s = scene(
    g,
    title='Derelict ship - something got aboard',
    legend={
        '#': {'wall': 'hull_dark', 'h': 1.4},
        'R': {'wall': 'hull_red', 'h': 1.4},
        'O': {'wall': 'organic', 'h': 1.4},
        'B': {'wall': 'blast_door', 'h': 1.4},
        'c': {'floor': 'deck', 'ceil': 'grate'},
        'm': {'floor': 'tile_floor', 'ceil': 'panel'},
        'h': {'floor': 'organic', 'ceil': 'organic'},
    },
    ceiling_height=1.4,
    sky=None,
    ambient=[0.045, 0.04, 0.045],
    fog={'color': [0.05, 0.0, 0.01], 'density': 0.06},
    lights=[{'x': 9.5, 'y': y, 'z': 1.2, 'radius': 3.4, 'color': red, 'intensity': 1.1} for y in (25.0, 21.0, 17.0, 13.0)] + [
        {'x': 17.6, 'y': 16.2, 'z': 0.7, 'radius': 3.2, 'color': [0.5, 0.95, 1.0], 'intensity': 1.0},
        {'x': 13.5, 'y': 20.5, 'z': 1.2, 'radius': 4.0, 'color': [0.85, 0.9, 1.0], 'intensity': 0.8},
        {'x': 15.5, 'y': 15.6, 'z': 1.2, 'radius': 4.0, 'color': red, 'intensity': 0.9},
        {'x': 17.6, 'y': 21.0, 'z': 0.7, 'radius': 3.2, 'color': [0.5, 0.95, 1.0], 'intensity': 1.0},
        {'x': 10.0, 'y': 5.0, 'z': 1.0, 'radius': 5.5, 'color': [0.4, 1.0, 0.5], 'intensity': 1.0},
        {'x': 6.0, 'y': 7.5, 'z': 0.4, 'radius': 3.0, 'color': [0.6, 1.0, 0.3], 'intensity': 0.8},
    ],
    sprites=[
        {'id': 'it', 'x': 10.0, 'y': 4.4, 'type': 'alien', 'scale': 0.8,
         'light': {'radius': 2.2, 'color': [0.5, 1.0, 0.8], 'intensity': 0.7, 'z': 0.6}},
        {'x': 18.3, 'y': 16.0, 'type': 'stasis_pod'},
        {'x': 18.3, 'y': 17.7, 'type': 'stasis_pod', 'tint': [0.35, 0.3, 0.32]},
        {'x': 18.3, 'y': 19.4, 'type': 'stasis_pod', 'tint': [0.35, 0.3, 0.32]},
        {'x': 18.3, 'y': 21.1, 'type': 'stasis_pod'},
        {'x': 15.6, 'y': 17.2, 'type': 'alien_egg'}, {'x': 16.2, 'y': 16.6, 'type': 'alien_egg', 'scale': 0.28},
        {'x': 13.2, 'y': 15.6, 'type': 'sci_crate'},
        {'x': 9.2, 'y': 22.4, 'type': 'sci_crate', 'scale': 0.3}, {'x': 10.3, 'y': 15.8, 'type': 'alien_egg', 'scale': 0.3},
    ],
    scatter=[{'of': 'derelict', 'on': 'c', 'density': 0.3, 'sizes': ['tiny', 'small'], 'seed': 4},
             {'of': 'alien_egg', 'on': 'h', 'density': 0.7, 'clump': 1.5, 'sizes': ['small', 'medium', 'large'],
              'seed': 9}],
    grime=0.4,
    camera={'x': 9.5, 'y': 26.4, 'look_at': [9.6, 3.0, 0.4], 'fov': 66},
    shots=[
        {'x': 9.5, 'y': 26.4, 'look_at': [9.6, 3.0, 0.4], 'fov': 66, 'post': ['horror'],
         'overlays': [{'type': 'viewmodel', 'item': 'flashlight'},
                      {'type': 'caption', 'text': 'Deck 4 - emergency power', 'at': 'top', 'box': True}]},
        {'x': 12.8, 'y': 21.6, 'look_at': [18.3, 18.0, 0.55], 'fov': 70, 'flashlight': True},
        {'x': 10.0, 'y': 12.4, 'look_at': 'it', 'fov': 58, 'flashlight': True, 'post': ['vhs']},
    ],
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'derelict_ship.json')))

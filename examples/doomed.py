"""Doomed: an homage to the first level of the 1993 shooter that named a genre - the slime pit, a walkway
zigzagging across a room flooded with glowing toxic sludge, seen down the barrel of a pistol with the
stone status bar along the bottom of the screen.

Shows the doomed kit (scripts/doomed.py): `nukage` slime sunk with `drop` between ledges of
`hex_floor`, a walkway snaking across it, walls of `green_trim` plating stacked storey on storey with
a `green_window` onto the rock outside, a `tech_ceiling`, `slime_edge` banks, `toxic_barrel`s, a
`corpse`, pickups (`ammo_clip`, `medkit`, `armor_vest`), a `fireball`, `toxic_sign` decals - and the
GUI: the `statusbar` widget, the `message` line and the `pistol` and `shotgun` viewmodels, in the
`doomed` theme. The soldiers are the `soldier` tinted sick green; light falls off into the dark with
distance, in bands, as it did then (`light_levels` 16 and a black fog).
Run:  python doomed.py  -> writes doomed.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 22, 21
g = Grid(W, H, fill='G')
room = ['=============',                             # the far ledge
        '~P~~~~~~~~~~~',
        '~P~~~~~~~~~~~',
        '~PPPPPPPP~~~~',                             # the walkway snakes across the slime
        '~~~~~~~~P~~~~',
        '~~~~~~~~P~~~~',
        '~~~~PPPPP~~~~',
        '~~~~P~~~~~~~~',
        '~~~~P~~~~~~~~',
        '=============']                             # the near ledge
for j, row in enumerate(room):
    for i, c in enumerate(row):
        g.put(3 + i, 2 + j, {'=': 'f', 'P': 'f', '~': '~'}[c])
for y in (5, 6, 7):
    g.put(16, y, 'w')                                # the window in the east wall
g.rect(17, 2, 19, 11, 'o')                           # outside: a strip of rock under the sky
g.rect(20, 0, 21, 20, 'R')
g.rect(8, 12, 9, 12, 'f')                            # the doorway, and the corridor back to the start
g.rect(8, 13, 9, 17, 'c')
g.rect(5, 18, 12, 19, 'c')

OOZE = [0.42, 1.0, 0.3]
WARM = [1.0, 0.92, 0.78]
ZOMBIE = [0.78, 0.92, 0.66]
lights = ([{'x': x, 'y': y, 'z': 0.15, 'radius': 3.2, 'color': OOZE, 'intensity': 0.7}
           for x, y in ((4, 7.5), (6, 3.6), (10, 4), (14, 4.5), (5.5, 9.5), (10, 10), (14, 9), (9.5, 6.5))]
          + [{'x': x, 'y': y, 'z': 2.0, 'radius': 6.5, 'color': WARM, 'intensity': 0.9}
             for x, y in ((5, 3), (13, 3), (5, 10.5), (13, 10.5), (9, 6.5))]
          + [{'x': 8.5, 'y': 15.0, 'z': 1.4, 'radius': 3.0, 'color': WARM, 'intensity': 0.7},
             {'x': 8.5, 'y': 18.8, 'z': 1.4, 'radius': 4.0, 'color': WARM, 'intensity': 0.8}])
sprites = [
    {'x': 3.6, 'y': 2.5, 'type': 'toxic_barrel'}, {'x': 15.4, 'y': 2.5, 'type': 'toxic_barrel'},
    {'x': 15.4, 'y': 11.5, 'type': 'toxic_barrel'}, {'x': 3.6, 'y': 11.4, 'type': 'toxic_barrel'},
    {'x': 10.6, 'y': 5.5, 'type': 'toxic_barrel'},
    {'id': 'zombie', 'x': 10.9, 'y': 7.7, 'type': 'soldier', 'facing': 140, 'tint': ZOMBIE},
    {'id': 'zombie2', 'x': 8.6, 'y': 2.6, 'type': 'soldier', 'facing': 90, 'tint': ZOMBIE},
    {'x': 4.5, 'y': 5.4, 'type': 'soldier', 'facing': 60, 'tint': ZOMBIE},
    {'x': 9.4, 'y': 8.5, 'type': 'corpse'}, {'x': 5.6, 'y': 11.6, 'type': 'corpse', 'flip': True},
    {'x': 10.8, 'y': 8.4, 'type': 'ammo_clip'}, {'x': 12.0, 'y': 2.5, 'type': 'armor_vest'},
    {'x': 4.4, 'y': 3.6, 'type': 'medkit'},
]
decals = [{'tex': 'toxic_sign', 'surface': 'wall', 'cell': [x, 1], 'face': 'south', 'u': 0.5, 'z': 1.25, 'size': 0.5}
          for x in (6, 13)] + [
    {'tex': 'splatter', 'surface': 'floor', 'x': 9.5, 'y': 8.6, 'size': 1.0, 'opacity': 0.8},
    {'tex': 'splatter', 'surface': 'floor', 'x': 5.4, 'y': 11.7, 'size': 0.9, 'opacity': 0.8}]
BAR = {'type': 'statusbar', 'ammo': 26, 'health': 100, 'armor': 0, 'arms': [2], 'ammo_table': [[26, 200], [0, 50], [0, 50], [0, 300]]}
VIEW = -0.08         # the horizon in the middle of the view above the status bar

s = scene(
    g,
    title='Doomed - the slime pit',
    legend={
        'G': {'wall': ['green_trim', 'green_trim', 'green_trim'], 'h': 2.2},
        'R': {'wall': 'rock', 'h': 3.0},
        'w': {'wall': ['green_window', 'green_trim', 'green_trim'], 'h': 2.2},
        'f': {'floor': 'hex_floor', 'ceil': 'tech_ceiling'},
        '~': {'floor': 'nukage', 'ceil': 'tech_ceiling', 'drop': 0.14, 'side': 'slime_edge'},
        'c': {'floor': 'hex_floor', 'ceil': 'tech_ceiling'},
        'o': {'floor': 'rock_floor'},
    },
    ceiling_height=2.2,
    sky='overcast',
    ambient=[0.3, 0.31, 0.27],
    light_levels=16,
    fog={'color': [0.01, 0.01, 0.01], 'density': 0.04},
    lights=[{'type': 'sun', 'azimuth': 200, 'elevation': 50, 'intensity': 0.9}] + lights,
    sprites=sprites,
    decals=decals,
    ui={'theme': 'doomed'},
    camera={'x': 8.5, 'y': 11.7, 'look_at': [8.5, 4.0], 'pitch': VIEW, 'fov': 80},
    shots=[
        {'x': 8.5, 'y': 11.7, 'look_at': [8.5, 4.0], 'pitch': VIEW, 'fov': 80,
         'overlays': [{'type': 'viewmodel', 'item': 'pistol'}, dict(BAR),
                      {'type': 'message', 'text': 'Picked up a clip.'}]},
        {'x': 3.4, 'y': 11.6, 'height': 1.9, 'look_at': [10.0, 5.0, 0.0], 'fov': 80},
        {'x': 7.5, 'y': 10.2, 'look_at': [12.2, 8.5], 'pitch': VIEW, 'fov': 76,
         'extra_sprites': [{'x': 9.9, 'y': 9.9, 'type': 'fireball', 'z': 0.42, 'flip': True}],
         'overlays': [{'type': 'viewmodel', 'item': 'shotgun', 'fire': True},
                      dict(BAR, ammo=8, health=28, armor=75, arms=[2, 3], keys=['blue'],
                           ammo_table=[[51, 200], [8, 50], [0, 50], [0, 300]], face='ouch'),
                      {'type': 'message', 'text': 'You got the shotgun!'}]},
        {'x': 12.6, 'y': 10.6, 'look_at': [16.5, 6.0], 'pitch': VIEW, 'fov': 76,
         'overlays': [{'type': 'viewmodel', 'item': 'pistol'},
                      dict(BAR, ammo=25, health=64, armor=84, arms=[2, 3],
                           ammo_table=[[25, 200], [12, 50], [0, 50], [0, 300]])]},
    ],
    contact_shadows=0.4,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doomed.json')))

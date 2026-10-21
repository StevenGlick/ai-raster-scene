"""Saloon: inside the frontier town's saloon at noon - the sun slanting through the front windows into
dusty air - and again after midnight, when the piano plays itself.

Shows the saloon kit (scripts/saloon.py): `saloon_wainscot` under `saloon_paper` (flocked red
wallpaper over dark panels), the back bar (`saloon_backbar` under `saloon_backbar_top`: shelves of
bottles round a tall mirror), front windows of open panes (`saloon_window`) letting the sun in, a
`tin_ceiling`; the bar itself a `saloon_bar` object in 3D (mahogany panels, a polished top, a brass
foot rail); `card_table`s mid-game among `saloon_chair`s, a `piano`, `spittoon`s, `wanted_poster`
decals, a `chandelier`; and the same room at night through shot overrides, its lamps lit and a ghost
at the keys.
Run:  python saloon.py  -> writes saloon.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

WARM = [1.0, 0.66, 0.34]
LAMPS = [{'x': 4.5, 'y': 3.5, 'z': 1.25, 'radius': 4.5, 'color': WARM, 'intensity': 1.2},       # the chandelier
         {'x': 8.6, 'y': 2.5, 'z': 0.9, 'radius': 2.6, 'color': WARM, 'intensity': 1.0},        # wall lamps
         {'x': 8.6, 'y': 5.0, 'z': 0.9, 'radius': 2.6, 'color': WARM, 'intensity': 1.0},
         {'x': 1.4, 'y': 3.5, 'z': 1.0, 'radius': 2.6, 'color': WARM, 'intensity': 0.9}]        # over the bar


def saloon():
    g = Grid(10, 12, fill='W')
    g.rect(1, 1, 8, 6, '.')                        # the room
    g.rect(0, 1, 0, 6, 'K')                        # the back bar along the west wall
    for x in (2, 3, 6, 7):
        g.put(x, 7, 'N')                           # the front windows
    g.rect(4, 7, 5, 7, 'd')                        # the doorway
    g.rect(0, 8, 9, 11, 's')                       # the bright street outside it
    # the day's people: the bartender behind the bar, a cowboy at it, two at cards (by night it is empty)
    day = [{'id': 'bartender', 'x': 1.3, 'y': 3.1, 'type': 'shopkeeper', 'facing': 0},
           {'id': 'cowboy', 'x': 2.25, 'y': 4.3, 'type': 'cowboy', 'facing': 160},
           {'id': 'gambler', 'x': 4.45, 'y': 2.55, 'type': 'cowboy', 'facing': 90, 'tint': [0.78, 0.8, 0.9]},
           {'id': 'player', 'x': 5.1, 'y': 3.15, 'type': 'cowboy', 'facing': 200, 'tint': [1.0, 0.82, 0.72]}]
    sprites = [
        {'x': 2.1, 'y': 2.4, 'type': 'spittoon'}, {'x': 2.1, 'y': 5.0, 'type': 'spittoon'},   # along the rail
        # the card game, and two empty tables
        {'x': 4.5, 'y': 3.0, 'type': 'card_table'},
        {'x': 3.85, 'y': 3.1, 'type': 'saloon_chair', 'flip': True}, {'x': 4.6, 'y': 3.6, 'type': 'saloon_chair'},
        {'x': 6.6, 'y': 4.6, 'type': 'card_table'},
        {'x': 5.95, 'y': 4.7, 'type': 'saloon_chair', 'flip': True}, {'x': 7.25, 'y': 4.6, 'type': 'saloon_chair'},
        {'x': 3.7, 'y': 5.4, 'type': 'card_table'},
        {'x': 3.05, 'y': 5.5, 'type': 'saloon_chair', 'flip': True}, {'x': 4.3, 'y': 5.3, 'type': 'saloon_chair'},
        # the piano against the north wall, its stool
        {'x': 6.8, 'y': 1.22, 'type': 'piano', 'planes': 1, 'angle': 0, 'length': 0.58},
        {'x': 6.8, 'y': 1.7, 'type': 'saloon_chair', 'scale': 0.22},
        # lamps: the chandelier, wall lamps; a steer's skull on the wall
        {'x': 4.5, 'y': 3.5, 'z': 1.12, 'type': 'chandelier', 'scale': 0.38},
        {'x': 8.75, 'y': 2.5, 'z': 0.72, 'type': 'sconce', 'scale': 0.24},
        {'x': 8.75, 'y': 5.0, 'z': 0.72, 'type': 'sconce', 'scale': 0.24},
        {'x': 3.0, 'y': 1.12, 'z': 1.05, 'type': 'cow_skull', 'scale': 0.24},
        # outside in the bright street
        {'x': 6.6, 'y': 8.5, 'type': 'barrel'}, {'x': 3.4, 'y': 8.7, 'type': 'tumbleweed', 'scale': 0.3},
    ]
    decals = [{'tex': 'wanted_poster', 'surface': 'wall', 'cell': [9, y], 'face': 'west', 'u': 0.5, 'z': 0.75,
               'size': 0.3} for y in (3, 4)] + [
              {'tex': 'wanted_poster', 'surface': 'wall', 'cell': [5, 0], 'face': 'south', 'u': 0.4, 'z': 0.72,
               'size': 0.28}]
    night = {'sky': 'night', 'ambient': [0.06, 0.06, 0.09], 'lights': LAMPS + [
                 {'x': 6.8, 'y': 1.6, 'z': 0.6, 'radius': 1.8, 'color': [0.6, 0.85, 1.0], 'intensity': 0.9},
                 {'x': 6.55, 'y': 1.35, 'z': 0.5, 'radius': 1.3, 'color': WARM, 'intensity': 0.9}],   # a candle
             'fog': {'color': [0.12, 0.08, 0.06], 'density': 0.03, 'glow': 0.9}}
    return scene(
        g,
        legend={
            'W': {'wall': ['saloon_wainscot', 'saloon_paper'], 'h': 1.6},
            'K': {'wall': ['saloon_backbar', 'saloon_backbar_top'], 'h': 1.6},
            'N': {'wall': ['saloon_window', 'saloon_paper'], 'h': 1.6},
            '.': {'floor': 'wood_floor', 'ceil': 'tin_ceiling'},
            'd': {'floor': 'wood_floor', 'ceil': 'tin_ceiling'},
            's': {'floor': 'desert_wash'},
        },
        title='Saloon - the sun through dusty air, and the piano after midnight',
        sky='day',
        ceiling_height=1.6,
        ambient=[0.3, 0.26, 0.21],
        fog={'color': [0.38, 0.31, 0.24], 'density': 0.024, 'glow': 0.4, 'shafts': 3.0},
        lights=[{'type': 'sun', 'azimuth': 90, 'elevation': 22, 'color': [1.0, 0.9, 0.7], 'intensity': 2.0,
                 'disc': False}] + [dict(lamp, intensity=lamp['intensity'] * 0.5) for lamp in LAMPS],
        sprites=sprites,
        decals=decals,
        objects=[{'type': 'saloon_bar', 'x': 1.75, 'y': 3.5, 'angle': 0, 'length': 3.4}],
        camera={'x': 8.2, 'y': 2.2, 'look_at': [1.8, 5.4, 0.55], 'fov': 70},
        shots=[
            {'x': 8.2, 'y': 2.2, 'look_at': [1.8, 5.4, 0.55], 'fov': 70, 'extra_sprites': day,
             'overlays': [{'type': 'caption', 'text': 'High noon in the saloon', 'at': 'top', 'box': True}]},
            {'x': 5.7, 'y': 4.7, 'look_at': [4.5, 2.9, 0.4], 'fov': 56, 'extra_sprites': day,
             'overlays': [{'type': 'bubble', 'anchor': 'gambler', 'name': 'The Gambler',
                           'text': 'Read em and weep, friend. Three ladies.'}]},
            {'x': 5.3, 'y': 4.4, 'look_at': [6.8, 1.3, 0.42], 'fov': 54,
             'extra_sprites': [{'id': 'ghost', 'x': 6.8, 'y': 1.68, 'type': 'ghost', 'facing': 270}],
             'overrides': night,
             'overlays': [{'type': 'caption', 'text': 'After midnight the piano plays itself', 'at': 'top', 'box': True}],
             'post': [{'fx': 'bloom', 'threshold': 0.6, 'strength': 0.6, 'radius': 5}]},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(saloon().save(os.path.join(HERE, 'saloon.json')))

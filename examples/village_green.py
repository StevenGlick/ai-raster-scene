"""Village green: a cobbled street of timber-framed houses opening onto a green with a well.

Shows the `timber` facade style - limewashed and ochre plaster between dark oak timbers, leaded
casements, plank doors, and over the street a gable end or a roof of thatch or tiles, some with a
chimney - and the village props: a market stall at the top of the street, the inn's sign standing
out over it as a card, a hand cart, the well on the green; and the same street by night through
shot overrides, its windows and the inn's lanterns lit.
Run:  python village_green.py  -> writes village_green.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

SUN = {'type': 'sun', 'azimuth': 205, 'elevation': 24, 'intensity': 1.0}
WARM = [1.0, 0.66, 0.34]
INN_LIGHTS = [{'x': 19.6, 'y': y, 'z': 1.0, 'radius': 3.2, 'color': WARM, 'intensity': 1.3} for y in (29.4, 31.6)]


def village_green():
    g = Grid(34, 46, fill='V')                     # houses everywhere; the street and the green cut out
    g.rect(13, 18, 20, 45, 'f')                    # the street, its fronts' cells either side
    g.rect(14, 18, 19, 45, 'c')                    # the cobbles
    g.rect(6, 4, 27, 18, 'f')                      # the green and the fronts round it
    g.rect(7, 5, 26, 17, 'g')                      # the grass
    g.rect(14, 17, 19, 18, 'c')                    # where the street meets the green
    sprites = [
        # a market stall on the street and its keeper
        {'x': 15.5, 'y': 33.6, 'type': 'market_stall'},
        {'id': 'keeper', 'x': 16.5, 'y': 34.5, 'type': 'shopkeeper', 'facing': 45},
        {'x': 14.5, 'y': 34.6, 'type': 'crate'}, {'x': 14.6, 'y': 32.2, 'type': 'barrel'},
        # the inn on the east side: its sign out over the street, barrels and lanterns by the door
        {'x': 19.55, 'y': 30.5, 'type': 'inn_sign', 'planes': 1, 'angle': 0, 'length': 0.9, 'z': 1.25},
        {'x': 19.6, 'y': 29.4, 'type': 'lantern', 'z': 0.85}, {'x': 19.6, 'y': 31.6, 'type': 'lantern', 'z': 0.85},
        {'x': 19.5, 'y': 28.4, 'type': 'barrel'}, {'x': 19.55, 'y': 33.0, 'type': 'barrel', 'flip': True},
        {'x': 19.5, 'y': 33.6, 'type': 'crate'},
        {'id': 'knight', 'x': 18.7, 'y': 27.6, 'type': 'knight', 'facing': 180},
        # along the street
        {'x': 14.6, 'y': 26.4, 'type': 'cart'},
        {'x': 14.3, 'y': 25.4, 'type': 'flowers'}, {'x': 14.3, 'y': 41.0, 'type': 'flowers'},
        {'x': 19.7, 'y': 38.4, 'type': 'flowers'}, {'x': 19.7, 'y': 23.2, 'type': 'flowers'},
        {'x': 14.4, 'y': 38.6, 'type': 'bench'},
        # the green: the well, an oak and a birch, a child, crows
        {'x': 16.5, 'y': 10.5, 'type': 'well'},
        {'x': 14.0, 'y': 5.6, 'type': 'tree', 'scale': 3.2}, {'x': 23.6, 'y': 7.6, 'type': 'birch'},
        {'id': 'child', 'x': 14.6, 'y': 12.4, 'type': 'child', 'facing': 45},
        {'x': 20.5, 'y': 12.0, 'type': 'crow'}, {'x': 21.4, 'y': 11.4, 'type': 'crow', 'flip': True},
        {'x': 9.0, 'y': 14.0, 'type': 'cart', 'flip': True},
    ]
    return scene(
        g,
        legend={
            'V': {'wall': 'plaster', 'h': 1.0,
                  'facade': {'style': 'timber', 'storeys': [1, 2], 'widths': [2, 3], 'lit': 0.4, 'shops': 0.3,
                             'seed': 5}},
            'f': {'floor': 'cobble'},
            'c': {'floor': 'cobble'},
            'g': {'floor': 'grass'},
        },
        title='Village green - a street of timber-framed houses and the green at its end',
        sky='day',
        ambient=[0.42, 0.42, 0.46],
        fog={'color': [0.72, 0.74, 0.8], 'density': 0.009},
        lights=[SUN],
        sprites=sprites,
        scatter=[{'of': 'grass_tuft', 'on': 'g', 'density': 0.12, 'sizes': {'tiny': 3, 'small': 1}, 'seed': 2}],
        camera={'x': 17.0, 'y': 44.5, 'angle': 270, 'fov': 68, 'height': 0.5},
        shots=[
            {'x': 17.0, 'y': 40.5, 'angle': 270, 'fov': 64,
             'overlays': [{'type': 'caption', 'text': 'Market day', 'at': 'top', 'box': True}]},
            {'x': 19.2, 'y': 37.2, 'look_at': [15.7, 33.6, 0.9], 'fov': 58,
             'overlays': [{'type': 'bubble', 'anchor': 'keeper', 'name': 'The Stallholder', 'offset': 60, 'width': 120,
                           'text': "Apples from the hill orchard! Three a penny, and the bread's still warm."}]},
            {'x': 14.2, 'y': 15.0, 'look_at': [16.6, 10.2, 0.95], 'fov': 62},
            {'x': 15.4, 'y': 23.6, 'look_at': [19.4, 30.6, 1.0], 'fov': 66,
             'overlays': [{'type': 'caption', 'text': 'After closing', 'at': 'top', 'box': True}],
             'overrides': {'sky': 'night', 'ambient': [0.1, 0.11, 0.17],
                           'lights': [{'type': 'moon', 'azimuth': 300, 'elevation': 30, 'intensity': 0.4}]
                           + INN_LIGHTS,
                           'fog': {'color': [0.05, 0.06, 0.1], 'density': 0.02, 'glow': 0.8}}},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(village_green().save(os.path.join(HERE, 'village_green.json')))

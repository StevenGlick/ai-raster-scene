"""Village green: a cobbled street of timber-framed houses opening onto a green with a well.

Shows the `timber` facade style - limewashed and ochre plaster between dark oak timbers, leaded
casements, plank doors, and every house's roof built in 3D: a gabled roof running back behind a
gable end, or a roof of thatch or tiles along the street, some with a chimney, on plastered walls
up from the block - and the village in 3D objects: two market stands on the street (trestle tables
of boards under striped awnings, red and blue, trays heaped with apples, cabbages, loaves and
potatoes, crates by them), crates and barrels by the inn's door, the well on the green (a round
wall of fieldstones, posts carrying a little roof, the windlass and its rope); the inn's sign
standing out over the street as a card, a hand cart; and the same street by night through shot
overrides, its windows and the inn's lanterns lit.
Run:  python village_green.py  -> writes village_green.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.5}  # the lights glow

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
        # the market stand's keeper, out in front of it calling his wares
        {'id': 'keeper', 'x': 16.5, 'y': 34.5, 'type': 'shopkeeper', 'facing': 45},
        # the inn on the east side: its sign out over the street, barrels and lanterns by the door
        {'x': 19.55, 'y': 30.5, 'type': 'inn_sign', 'planes': 1, 'angle': 0, 'length': 0.9, 'z': 1.25},
        {'x': 19.6, 'y': 29.4, 'type': 'lantern', 'z': 0.85}, {'x': 19.6, 'y': 31.6, 'type': 'lantern', 'z': 0.85},
        {'id': 'knight', 'x': 18.7, 'y': 27.6, 'type': 'knight', 'facing': 180},
        # along the street
        {'x': 14.6, 'y': 26.4, 'type': 'cart'},
        {'x': 14.3, 'y': 25.4, 'type': 'flowers'}, {'x': 14.3, 'y': 41.0, 'type': 'flowers'},
        {'x': 19.7, 'y': 38.4, 'type': 'flowers'}, {'x': 19.7, 'y': 23.2, 'type': 'flowers'},
        {'x': 14.4, 'y': 38.6, 'type': 'bench'},
        # the green: an oak and a birch, a child, crows (the well is an object)
        {'x': 14.0, 'y': 5.6, 'type': 'tree', 'scale': 3.2}, {'x': 23.6, 'y': 7.6, 'type': 'birch'},
        {'id': 'child', 'x': 14.6, 'y': 12.4, 'type': 'child', 'facing': 45},
        {'x': 18.8, 'y': 11.4, 'type': 'villager', 'facing': 120},
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
        objects=[{'type': 'market_stand', 'x': 15.5, 'y': 33.6, 'angle': 44, 'scale': 0.8},   # facing up the street
                 {'type': 'market_stand', 'x': 19.25, 'y': 35.1, 'angle': 180, 'scale': 0.8, 'paint': '#2e5a9a',
                  'goods': ['potatoes', 'apples', 'cabbages'], 'seed': 4},              # and across, down it
                 {'type': 'well', 'x': 16.5, 'y': 10.5, 'scale': 1.5}]
        + [{'type': 'crate', 'x': x, 'y': y, 'angle': a, 'size': 0.34, 'seed': k, **extra}
           for k, (x, y, a, extra) in enumerate(((14.5, 34.6, 12, {'goods': 'cabbages'}), (19.5, 33.45, 85, {}),
                                                (19.45, 33.85, 80, {'goods': 'apples'})))]
        + [{'type': 'barrel', 'x': x, 'y': y, 'seed': k} for k, (x, y) in enumerate(((14.6, 32.2), (19.5, 28.4),
                                                                                    (19.55, 33.05)))],
        scatter=[{'of': 'grass_tuft', 'on': 'g', 'density': 0.12, 'sizes': {'tiny': 3, 'small': 1}, 'seed': 2}],
        camera={'x': 17.0, 'y': 44.5, 'angle': 270, 'fov': 68, 'height': 0.5},
        shots=[
            {'x': 17.0, 'y': 40.5, 'angle': 270, 'fov': 64,
             'overlays': [{'type': 'caption', 'text': 'Market day', 'at': 'top', 'box': True}]},
            {'x': 18.4, 'y': 37.6, 'look_at': [15.7, 33.6, 0.9], 'fov': 58,
             'overlays': [{'type': 'bubble', 'anchor': 'keeper', 'name': 'The Stallholder', 'offset': 60, 'width': 120,
                           'text': "Apples from the hill orchard! Three a penny, and the bread's still warm."}]},
            {'x': 14.3, 'y': 14.3, 'look_at': [16.5, 10.4, 0.66], 'fov': 64},
            {'x': 15.4, 'y': 23.6, 'look_at': [19.4, 30.6, 1.0], 'fov': 66, 'post': [GLOW],
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

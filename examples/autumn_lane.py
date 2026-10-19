"""Autumn lane: a country lane through a wood in October, a field behind a dry-stone wall.

Shows the `forest_autumn` fringe - oak, birch and bush turned orange, gold and rust, the spruce
among them still green - in front of `forest_deep_autumn` walls; a floor of `leaves_fallen` on
the verges, with the `autumn` scatter set; a stubble field with hay bales, pumpkins, a scarecrow and crows behind a wall; a low
sun off to the side, so the shadows of the trees lie across the lane in shafts of golden haze;
and the gateway at dusk through shot overrides, jack-o'-lanterns lit on the gateposts and along
the wall (`extra_sprites`).
Run:  python autumn_lane.py  -> writes autumn_lane.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

SUN = {'type': 'sun', 'azimuth': 268, 'elevation': 7, 'intensity': 1.0}
LANTERNS = [(17.5, 17.5), (17.5, 20.5), (18.35, 21.6), (18.3, 16.3), (16.2, 19.6)]


def autumn_lane():
    g = Grid(40, 48, fill='F')                     # the wood everywhere; the lane, verges and field cut out
    g.rect(18, 2, 23, 47, ',')                     # the lane and its verges, straight up the map
    g.rect(4, 8, 16, 28, 'h')                      # the field, west of the lane halfway up
    g.rect(17, 8, 17, 28, 'w')                     # a dry-stone wall between the field and the lane
    g.put(17, 18, 'h'); g.put(17, 19, 'h')         # the gateway, its gate long gone
    g.rect(19, 2, 21, 47, 'p')                     # the lane itself
    sprites = [
        # trees standing free on the verges, in front of the layered edges
        {'x': 22.9, 'y': 44.0, 'type': 'tree_autumn', 'scale': 3.1},
        {'x': 18.3, 'y': 41.2, 'type': 'birch_autumn', 'flip': True},
        {'x': 23.2, 'y': 38.6, 'type': 'birch_autumn'},
        {'x': 18.4, 'y': 35.0, 'type': 'tree_autumn', 'flip': True},
        {'x': 23.3, 'y': 32.4, 'type': 'pine', 'flip': True},
        {'x': 23.0, 'y': 26.0, 'type': 'tree_autumn', 'scale': 3.3},
        {'x': 23.2, 'y': 19.0, 'type': 'birch_autumn', 'flip': True},
        {'x': 23.1, 'y': 12.2, 'type': 'tree_autumn'},
        {'x': 18.3, 'y': 6.0, 'type': 'birch_autumn'},
        {'x': 18.2, 'y': 30.2, 'type': 'bush_autumn'}, {'x': 22.7, 'y': 35.8, 'type': 'bush_autumn', 'flip': True},
        {'x': 18.4, 'y': 25.0, 'type': 'bush_autumn', 'flip': True}, {'x': 22.6, 'y': 22.4, 'type': 'fern'},
        {'x': 22.5, 'y': 41.6, 'type': 'mushrooms'}, {'x': 18.6, 'y': 44.8, 'type': 'fern'},
        # the field: an old oak in its corner, the scarecrow, bales, pumpkins, crows
        {'x': 6.4, 'y': 25.4, 'type': 'tree_autumn', 'scale': 3.8},
        {'id': 'scarecrow', 'x': 10.6, 'y': 17.2, 'type': 'scarecrow'},
        {'x': 8.6, 'y': 22.6, 'type': 'hay_bale'}, {'x': 9.8, 'y': 23.1, 'type': 'hay_bale', 'flip': True},
        {'x': 9.2, 'y': 22.8, 'type': 'hay_bale', 'z': 0.48}, {'x': 6.0, 'y': 15.4, 'type': 'hay_bale'},
        {'x': 13.0, 'y': 22.6, 'type': 'pumpkin'}, {'x': 14.2, 'y': 21.4, 'type': 'pumpkin', 'scale': 0.26},
        {'x': 12.2, 'y': 20.8, 'type': 'pumpkin', 'flip': True}, {'x': 14.8, 'y': 23.6, 'type': 'pumpkin', 'scale': 0.4},
        {'x': 13.6, 'y': 25.0, 'type': 'pumpkin', 'scale': 0.29}, {'x': 11.4, 'y': 24.4, 'type': 'pumpkin'},
        {'x': 15.2, 'y': 13.6, 'type': 'pumpkin', 'scale': 0.36}, {'x': 14.0, 'y': 12.4, 'type': 'pumpkin'},
        {'x': 11.9, 'y': 18.6, 'type': 'crow'}, {'x': 9.2, 'y': 20.6, 'type': 'crow', 'flip': True},
        {'x': 17.5, 'y': 23.4, 'type': 'crow'}, {'x': 17.5, 'y': 26.2, 'type': 'crow', 'flip': True},
        # someone walking home up the lane, away from us
        {'id': 'walker', 'x': 20.5, 'y': 41.0, 'type': 'child', 'facing': 270},
    ]
    dusk_sprites = [{'x': x, 'y': y, 'type': 'jack_o_lantern'} for x, y in LANTERNS]   # those on the wall stand on it
    dusk_sprites.append({'x': 17.6, 'y': 19.0, 'type': 'witch', 'facing': 30})            # someone in the gateway
    dusk_lights = [{'x': x + 0.4, 'y': y, 'z': 0.85 if x == 17.5 else 0.25, 'radius': 2.6,
                    'color': [1.0, 0.58, 0.22], 'intensity': 1.2} for x, y in LANTERNS]
    return scene(
        g,
        legend={
            'F': {'wall': 'forest_deep_autumn', 'h': 2.4, 'fringe': 'forest_autumn'},
            ',': {'floor': 'leaves_fallen'},
            'p': {'floor': 'dirt'},
            'h': {'floor': 'dry_grass'},
            'w': {'wall': 'moss_stone', 'h': 0.6, 'top': 'moss'},
        },
        title='Autumn lane - a lane through the wood in October',
        sky='golden',
        ambient=[0.3, 0.27, 0.27],
        fog={'color': [0.34, 0.27, 0.2], 'density': 0.006, 'ground': 0.12, 'height': 0.5, 'noise': 0.6,
             'shafts': 0.7, 'anisotropy': 0.2},
        lights=[SUN],
        sprites=sprites,
        scatter=[{'of': 'autumn', 'on': ',', 'density': 0.3, 'clump': 1.4, 'seed': 3}],
        camera={'x': 20.0, 'y': 46.6, 'angle': 270, 'fov': 66, 'height': 0.5},
        shots=[
            {'x': 20.0, 'y': 46.6, 'angle': 270, 'post': [{'fx': 'leaves', 'count': 70}],
             'overlays': [{'type': 'caption', 'text': 'The long way home', 'at': 'top', 'box': True}]},
            {'x': 12.4, 'y': 15.2, 'look_at': [6.8, 25.0, 1.4], 'fov': 64, 'height': 0.6},
            {'x': 21.4, 'y': 23.6, 'look_at': [17.6, 18.4, 0.55], 'fov': 62, 'height': 0.6,
             'extra_sprites': dusk_sprites, 'post': [{'fx': 'bloom', 'threshold': 0.5, 'strength': 0.8, 'radius': 5},
                                                     {'fx': 'vignette', 'strength': 0.45}],
             'overlays': [{'type': 'caption', 'text': "All Hallows' Eve", 'at': 'top', 'box': True}],
             'overrides': {'sky': 'dusk', 'ambient': [0.14, 0.13, 0.2],
                           'lights': [dict(SUN, elevation=2, intensity=0.3)] + dusk_lights,
                           'fog': {'color': [0.16, 0.13, 0.2], 'density': 0.035, 'ground': 0.3, 'height': 0.4,
                                   'noise': 0.6, 'glow': 0.6}}},
            {'x': 20.1, 'y': 38.3, 'look_at': 'walker', 'fov': 60, 'post': [{'fx': 'leaves', 'count': 50}],
             'overlays': [{'type': 'bubble', 'anchor': 'walker', 'text': 'Can we go the long way? Just this once?'}]},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(autumn_lane().save(os.path.join(HERE, 'autumn_lane.json')))

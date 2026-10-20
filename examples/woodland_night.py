"""Woodland at night: a forest road with a bend, running to a clearing where a fire burns.

Shows the `forest` fringe - every edge of the wood is layered cards of spruce, oak, birch and
undergrowth in front of a low `forest_deep` wall (trunks receding into the dark), so the treeline against the sky is tree tops -
trees standing free along the road, a moon whose light keeps its shadows in volumetric fog
(beams across the road, halos round the fire and the lantern), and the same wood at dawn
through shot overrides: a low sun through a gap in the trees, mist lying in the clearing.
Run:  python woodland_night.py  -> writes woodland_night.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.5}  # the lights glow

FIRE = {'x': 26.5, 'y': 10.5, 'z': 0.5, 'radius': 9.0, 'color': [1.0, 0.62, 0.28], 'intensity': 2.2}
LANTERN = {'x': 16.0, 'y': 18.4, 'z': 0.5, 'radius': 5.5, 'color': [1.0, 0.72, 0.38], 'intensity': 1.4}


def woodland():
    g = Grid(36, 32, fill='F')                     # the wood everywhere; the road and clearing are carved out
    g.rect(14, 19, 21, 31, ',')                    # the south leg: the fringe takes a cell on each side
    g.rect(8, 14, 21, 21, ',')                     # the bend
    g.rect(8, 3, 15, 16, ',')                      # the north leg
    g.rect(14, 7, 24, 14, ',')                     # the spur east to the clearing
    g.disc(26, 10, 6, ',')                         # the clearing
    g.rect(31, 9, 35, 10, ',')                     # a deer path east, where the morning sun comes in
    g.rect(16, 20, 18, 31, 'p')                    # the dirt track, south leg
    g.rect(10, 16, 18, 19, 'p')                    # the bend
    g.rect(10, 3, 12, 16, 'p')                     # the north leg
    g.rect(14, 10, 22, 11, 'p')                    # the spur
    g.disc(26, 10, 2, 'c')                         # swept round the fire: no scatter there
    return scene(
        g,
        legend={
            'F': {'wall': 'forest_deep', 'h': 2.4, 'fringe': 'forest'},
            ',': {'floor': 'pine_needles'},
            'c': {'floor': 'pine_needles'},
            'p': {'floor': 'mud'},
        },
        title='Woodland at night - a lantern on the forest road',
        sky='night',
        ambient=[0.1, 0.11, 0.17],
        fog={'color': [0.04, 0.05, 0.08], 'density': 0.012, 'ground': 0.18, 'height': 0.45, 'noise': 0.5,
             'glow': 0.45, 'shafts': 0.6},
        lights=[{'type': 'moon', 'azimuth': 285, 'elevation': 26, 'intensity': 0.45}, FIRE, LANTERN],
        sprites=[
            # trees standing free along the road, in front of the layered edge
            {'x': 14.9, 'y': 26.5, 'type': 'pine'}, {'x': 20.4, 'y': 28.2, 'type': 'pine', 'flip': True},
            {'x': 14.8, 'y': 21.4, 'type': 'tree'}, {'x': 20.6, 'y': 23.0, 'type': 'birch'},
            {'x': 8.9, 'y': 9.5, 'type': 'pine'}, {'x': 14.7, 'y': 5.0, 'type': 'birch', 'flip': True},
            {'x': 22.6, 'y': 13.6, 'type': 'pine'}, {'x': 15.4, 'y': 8.2, 'type': 'tree', 'flip': True},
            {'x': 22.6, 'y': 6.0, 'type': 'dead_tree'}, {'x': 30.0, 'y': 14.0, 'type': 'dead_tree', 'flip': True},
            {'x': 29.6, 'y': 5.6, 'type': 'birch'}, {'x': 8.8, 'y': 20.4, 'type': 'pine', 'flip': True},
            # the road: a lantern on a stump at the bend, a fallen log
            {'x': 16.0, 'y': 18.4, 'type': 'stump'}, {'x': 16.0, 'y': 18.4, 'type': 'lantern', 'z': 0.3},
            {'x': 19.6, 'y': 25.6, 'type': 'log'},
            {'x': 15.3, 'y': 29.0, 'type': 'bush'}, {'x': 19.9, 'y': 20.6, 'type': 'bush'},
            {'x': 9.5, 'y': 13.5, 'type': 'bush'}, {'x': 13.6, 'y': 12.0, 'type': 'fern'},
            {'x': 18.6, 'y': 23.2, 'type': 'mushrooms'}, {'x': 11.4, 'y': 10.5, 'type': 'mushrooms'},
            {'x': 10.4, 'y': 18.6, 'type': 'boulder'}, {'x': 23.4, 'y': 10.0, 'type': 'boulder'},
            # the clearing: the fire, the one who keeps it, his camp
            {'x': 26.5, 'y': 10.5, 'type': 'campfire', 'scale': 0.8},
            {'id': 'watcher', 'x': 27.6, 'y': 12.2, 'type': 'cultist',
             'light': {'radius': 2.6, 'color': [1.0, 0.68, 0.35], 'intensity': 0.9, 'z': 0.45}},
            {'x': 24.6, 'y': 8.4, 'type': 'crate'}, {'x': 23.8, 'y': 9.2, 'type': 'sack'},
            {'x': 25.4, 'y': 7.6, 'type': 'broken_barrel'}, {'x': 28.4, 'y': 8.6, 'type': 'bones'},
            {'x': 25.6, 'y': 11.9, 'type': 'rocks'}, {'x': 24.9, 'y': 12.3, 'type': 'grass_tuft'},
            {'x': 28.4, 'y': 11.4, 'type': 'grass_tuft'}, {'x': 27.2, 'y': 12.6, 'type': 'bones'},
            {'x': 29.0, 'y': 10.6, 'type': 'rubble'},
            # and far up the north road, something standing in the moonlight
            {'x': 11.2, 'y': 7.6, 'type': 'ghost', 'facing': 90},
        ],
        decals=[
            {'tex': 'puddle', 'surface': 'floor', 'x': 17.2, 'y': 27.4, 'size': 1.8},
            {'tex': 'puddle_dark', 'surface': 'floor', 'x': 16.6, 'y': 22.6, 'size': 1.5},
            {'tex': 'puddle', 'surface': 'floor', 'x': 11.4, 'y': 8.6, 'size': 1.4},
            {'tex': 'moss_patch', 'surface': 'floor', 'x': 19.6, 'y': 24.6, 'size': 1.6, 'opacity': 0.75},
            {'tex': 'moss_patch', 'surface': 'floor', 'x': 15.2, 'y': 17.4, 'size': 1.4, 'opacity': 0.75},
            {'tex': 'stain', 'surface': 'floor', 'x': 26.5, 'y': 12.4, 'size': 1.6, 'opacity': 0.7},
        ],
        scatter=[
            {'of': 'forest', 'on': ',', 'density': 0.45, 'clump': 1.3, 'seed': 1},
            {'of': 'rocks', 'on': 'p', 'density': 0.7, 'clump': 1.1,
             'sizes': {'tiny': 6, 'small': 3}, 'seed': 2},
            {'of': 'undergrowth', 'on': ',', 'density': 0.55, 'clump': 1.6, 'seed': 3},
        ],
        camera={'x': 17.5, 'y': 30.4, 'angle': 270, 'fov': 68, 'height': 0.5},
        shots=[
            {'x': 17.5, 'y': 30.4, 'angle': 270, 'post': [GLOW],
             'overlays': [{'type': 'viewmodel', 'item': 'lantern'},
                          {'type': 'caption', 'text': 'The old forest road', 'at': 'top', 'box': True}]},
            {'x': 23.0, 'y': 13.6, 'angle': 331, 'fov': 70, 'post': [GLOW],
             'overlays': [{'type': 'bubble', 'anchor': 'watcher', 'name': 'The Watcher',
                           'text': 'Sit. The fire does not care who you are.'}]},
            {'x': 18.2, 'y': 19.8, 'angle': 209, 'fov': 70, 'post': ['horror']},
            {'x': 19.5, 'y': 11.0, 'look_at': [27.0, 9.0, 0.6], 'fov': 74, 'flashlight': True},
            {'x': 21.0, 'y': 10.6, 'look_at': [34.0, 6.6, 1.4], 'fov': 72,
             'overlays': [{'type': 'caption', 'text': 'First light', 'at': 'top', 'box': True}],
             'overrides': {
                 'sky': 'golden', 'ambient': [0.34, 0.33, 0.36],
                 'lights': [{'type': 'sun', 'azimuth': 4, 'elevation': 10, 'intensity': 0.85},
                            dict(FIRE, intensity=0.8, radius=4.0)],
                 'fog': {'color': [0.66, 0.6, 0.54], 'density': 0.008, 'ground': 0.3, 'height': 0.45,
                         'noise': 0.6, 'shafts': 0.9, 'anisotropy': 0.35}}},
            {'x': 11.0, 'y': 14.6, 'look_at': [11.2, 3.0, 1.2], 'fov': 70, 'post': [GLOW]},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(woodland().save(os.path.join(HERE, 'woodland_night.json')))

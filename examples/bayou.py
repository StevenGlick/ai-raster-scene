"""Bayou: black water under bald cypresses hung with Spanish moss, a shack on its island with a
lamp in the window, a rowboat at the landing - at dusk, and again at night with the fireflies out.

Shows the swamp kit - `swamp_deep` walls behind a `swamp` fringe, `swamp_water` sunk a little with
`drop` (it mirrors, and duckweed drifts on it), `bog` banks, bald cypresses standing in the water
with their knees round them, cattails, lily pads, a heron, an alligator lying with only its eyes
and back showing, and `fireflies` (additive, glowing) - and the same water at night through shot
overrides, the shack's window and lantern doubled in it.
Run:  python bayou.py  -> writes bayou.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

WARM = [1.0, 0.64, 0.3]
LAMPS = [{'x': 16.6, 'y': 10.0, 'z': 1.0, 'radius': 5.0, 'color': WARM, 'intensity': 1.5},       # the window
         {'x': 19.6, 'y': 10.6, 'z': 1.1, 'radius': 4.0, 'color': WARM, 'intensity': 1.2}]       # the porch lantern


def bayou():
    g = Grid(34, 32, fill='Y')                     # the swamp all round; the water is cut out of it
    g.disc(17, 16, 10, '~')
    g.rect(7, 12, 27, 30, '~')
    g.disc(16, 8, 4, 'b')                          # the shack's island
    g.rect(14, 6, 18, 8, 'H')                      # the shack, two rooms wide
    g.put(16, 8, 'W'); g.put(15, 8, 'D')            # its window and door, looking south over the water
    g.rect(14, 9, 19, 10, 'p')                     # the porch
    g.rect(19, 11, 19, 13, 'p')                    # the landing stage
    for x, y, r in ((8, 18, 1), (26, 16, 1), (25, 26, 1)):
        g.disc(x, y, r, 'b')                       # hummocks
    sprites = [
        # cypresses standing in the water, framing the shack, their knees round them
        {'x': 14.2, 'y': 16.6, 'type': 'bald_cypress', 'scale': 4.6, 'flip': True}, {'x': 20.8, 'y': 16.2, 'type': 'bald_cypress', 'scale': 4.4},
        {'x': 12.0, 'y': 11.6, 'type': 'bald_cypress', 'scale': 3.6}, {'x': 23.2, 'y': 10.8, 'type': 'bald_cypress', 'scale': 3.8},
        {'x': 11.0, 'y': 24.5, 'type': 'bald_cypress', 'scale': 5.0, 'flip': True},
        {'x': 25.0, 'y': 22.0, 'type': 'bald_cypress', 'scale': 4.8},
        {'x': 14.9, 'y': 17.2, 'type': 'cypress_knees'}, {'x': 20.0, 'y': 16.8, 'type': 'cypress_knees', 'flip': True},
        {'x': 12.6, 'y': 12.3, 'type': 'cypress_knees', 'scale': 0.24}, {'x': 18.8, 'y': 19.0, 'type': 'cypress_knees', 'scale': 0.22},
        # the hummocks and the island's edge: cattails, a heron
        {'x': 8.4, 'y': 18.6, 'type': 'cattails'}, {'x': 7.8, 'y': 17.6, 'type': 'cattails', 'flip': True},
        {'x': 26.2, 'y': 16.6, 'type': 'cattails'}, {'x': 12.8, 'y': 10.8, 'type': 'cattails'},
        {'x': 20.8, 'y': 9.4, 'type': 'cattails', 'flip': True},
        {'id': 'heron', 'x': 25.0, 'y': 25.8, 'type': 'heron', 'flip': True},
        # the shack: a lantern on the porch, a rowboat at the landing, moss off the eaves, a barrel
        {'x': 19.6, 'y': 10.6, 'type': 'lantern', 'z': 0.85},
        {'x': 20.3, 'y': 12.8, 'type': 'rowboat', 'angle': 90},
        {'x': 15.5, 'y': 9.08, 'type': 'spanish_moss', 'z': 1.0, 'scale': 0.9, 'planes': 1, 'angle': 0, 'length': 1.2},
        {'x': 14.4, 'y': 9.6, 'type': 'barrel'},
        # the water: an alligator watching, near
        {'id': 'gator', 'x': 18.2, 'y': 23.5, 'type': 'alligator'},
    ]
    decals = [{'tex': 'lily_pads', 'surface': 'floor', 'x': x, 'y': y, 'size': s_}
              for x, y, s_ in ((15.6, 22.4, 1.6), (20.4, 20.0, 1.4), (13.8, 14.6, 1.6), (21.6, 15.6, 1.2),
                               (17.0, 26.4, 1.3), (11.0, 21.6, 1.4))]
    night = [{'x': x, 'y': y, 'type': 'fireflies', 'z': z} for x, y, z in ((14.6, 13.0, 0.4), (20.4, 14.4, 0.6),
                                                                              (16.8, 18.6, 0.3), (11.4, 14.4, 0.8))]
    night_over = {'sky': 'night', 'ambient': [0.08, 0.1, 0.12],
                  'lights': [{'type': 'moon', 'azimuth': 250, 'elevation': 24, 'intensity': 0.35}] + LAMPS,
                  'fog': {'color': [0.04, 0.06, 0.06], 'density': 0.012, 'ground': 0.2, 'height': 0.4,
                          'noise': 0.6, 'glow': 0.9}}
    return scene(
        g,
        legend={
            'Y': {'wall': 'swamp_deep', 'h': 2.6, 'fringe': 'swamp'},
            '~': {'floor': 'swamp_water', 'drop': 0.12, 'side': 'bog'},
            'b': {'floor': 'bog'},
            'H': {'wall': 'boards', 'h': 1.7, 'top': 'shingle'},
            'W': {'wall': [{'base': 'window_lit_plaster', 'tint': [0.62, 0.48, 0.34]}, 'boards'], 'h': 1.7, 'top': 'shingle'},
            'D': {'wall': ['door_wood', 'boards'], 'h': 1.7, 'top': 'shingle'},
            'p': {'wall': 'boards', 'h': 0.22, 'top': 'planks'},
        },
        title='Bayou - a shack on the black water, under the moss',
        sky='sunset',
        ambient=[0.3, 0.27, 0.26],
        fog={'color': [0.46, 0.38, 0.3], 'density': 0.008, 'ground': 0.12, 'height': 0.4, 'noise': 0.5},
        lights=[{'type': 'sun', 'azimuth': 262, 'elevation': 6, 'intensity': 0.75}] + LAMPS,
        sprites=sprites,
        decals=decals,
        camera={'x': 17.4, 'y': 21.6, 'angle': 268, 'fov': 66, 'height': 0.5},
        shots=[
            {'x': 17.4, 'y': 21.6, 'angle': 268,
             'overlays': [{'type': 'caption', 'text': 'The bayou at sundown', 'at': 'top', 'box': True}]},
            {'x': 17.4, 'y': 21.6, 'angle': 268, 'extra_sprites': night, 'overrides': night_over,
             'post': [{'fx': 'bloom', 'threshold': 0.55, 'strength': 0.6, 'radius': 5}]},
            {'x': 18.5, 'y': 26.6, 'look_at': 'gator', 'fov': 40, 'height': 0.22, 'extra_sprites': night,
             'overrides': night_over},
            {'x': 21.0, 'y': 28.6, 'look_at': 'heron', 'fov': 54, 'height': 0.6,
             'overrides': {'sky': 'golden', 'ambient': [0.36, 0.36, 0.38],
                           'lights': [{'type': 'sun', 'azimuth': 20, 'elevation': 10, 'intensity': 0.8}],
                           'fog': {'color': [0.66, 0.66, 0.6], 'density': 0.009, 'ground': 0.2, 'height': 0.5,
                                   'noise': 0.7}}},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(bayou().save(os.path.join(HERE, 'bayou.json')))

"""The window onto the garden: a dark room, its window broken, a moonlit garden beyond - one of the three concept
drawings this project began from, made into a scene.

The room's north wall has a gap two cells wide with a low sill across its foot (a wall cell `h` 0.25), and a
`broken_casement` card stands just inside it (`planes` 1, `scale` 1.5 - three wide, so its plaster lies over the
wall either side): its middle bar snapped, the glass gone but for shards in its corners. `tattered_curtain`s hang
either side; the glass lies on the floor (`glass_shards`), where the moonlight comes in through the gap. Outside, a
gravel path runs to a `robed_statue` on its pedestal between `rose_bush`es, a `lamp_post` lit beside it, `cypress`es
dark against the sky; a house on the left has one window lit, a tower on the right a cold light high up, and the
full moon is over them all. The second shot stands in the garden under the statue, the moon raised for it with the
shot's `overrides`.
Run:  python window_garden.py  -> writes window_garden.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 17, 20
WARM = [1.0, 0.72, 0.4]
ROOM = [0.5, 0.5, 0.56]                    # the room's plaster, in the dark
HOUSE = [0.42, 0.46, 0.6]                  # the house's plaster, blue in the moonlight
MOON = [0.55, 0.65, 0.9]
NIGHT = [{'fx': 'grade', 'tint': [1.0, 1.0, 1.04], 'lift': [0.0, 0.006, 0.02], 'saturation': 1.1},
         {'fx': 'bloom', 'source': 'light', 'strength': 1.0, 'radius': 2.0, 'spread': 0.5}]


def window_garden():
    g = Grid(W, H, fill='g')
    g.rect(0, 0, W - 1, 1, 'F')                    # the trees at the garden's end
    g.rect(2, 5, 5, 9, 'L')                        # the house on the left,
    g.put(5, 7, 'l')                               # one window lit
    g.rect(12, 2, 13, 4, 'T')                      # the tower on the right
    g.rect(7, 9, 8, 13, 'p')                       # the path from the window to the statue,
    g.rect(7, 7, 10, 8, 'p')                       # and round its pedestal
    g.rect(5, 14, 10, 19, 'B')                     # the room
    g.rect(6, 15, 9, 18, 'r')
    g.rect(7, 14, 8, 14, 'S')                      # the window's gap, its sill
    sprites = [
        {'x': 8.0, 'y': 15.02, 'type': 'broken_casement', 'angle': 0, 'scale': 1.5, 'tint': [0.82, 0.82, 0.85]},
        {'x': 7.06, 'y': 15.07, 'type': 'tattered_curtain', 'angle': 0},
        {'x': 8.97, 'y': 15.07, 'type': 'tattered_curtain', 'angle': 0, 'flip': True, 'scale': 1.38},
        {'x': 9.0, 'y': 8.0, 'type': 'robed_statue', 'scale': 1.7},
        {'x': 6.7, 'y': 10.3, 'type': 'lamp_post', 'scale': 1.3},
        {'x': 6.4, 'y': 11.5, 'type': 'rose_bush', 'scale': 0.5},
        {'x': 7.3, 'y': 11.2, 'type': 'rose_bush', 'scale': 0.42},
        {'x': 9.7, 'y': 11.3, 'type': 'rose_bush', 'scale': 0.48},
        {'x': 10.5, 'y': 10.7, 'type': 'rose_bush', 'scale': 0.44},
        {'x': 11.6, 'y': 9.6, 'type': 'rose_bush', 'scale': 0.46},
        {'x': 5.9, 'y': 10.6, 'type': 'bush', 'scale': 0.6},
        {'x': 11.0, 'y': 11.8, 'type': 'bush', 'scale': 0.55},
        {'x': 7.2, 'y': 6.2, 'type': 'cypress', 'scale': 2.3},
        {'x': 10.7, 'y': 6.6, 'type': 'cypress', 'scale': 2.0},
        {'x': 13.9, 'y': 7.4, 'type': 'cypress', 'scale': 2.6},
        {'x': 4.0, 'y': 3.2, 'type': 'cypress', 'scale': 2.4},
    ]
    lights = [
        {'type': 'moon', 'azimuth': 278, 'elevation': 14, 'intensity': 0.5},
        {'x': 6.75, 'y': 10.3, 'z': 1.2, 'radius': 2.6, 'color': WARM, 'intensity': 0.9},    # the lamp post
        {'x': 9.0, 'y': 8.9, 'z': 1.6, 'radius': 2.8, 'color': MOON, 'intensity': 0.9},      # moonlight on the statue
        {'x': 8.0, 'y': 15.7, 'z': 0.3, 'radius': 1.6, 'color': MOON, 'intensity': 1.0},     # and in at the window
        {'x': 11.8, 'y': 3.4, 'z': 3.5, 'radius': 1.4, 'color': [0.45, 0.9, 0.85], 'intensity': 0.5},  # the tower's
    ]
    risen = [dict(lights[0], elevation=24)] + lights[1:]             # the moon higher, for the shot in the garden
    decals = [{'tex': 'glass_shards', 'surface': 'floor', 'x': 7.6, 'y': 15.28, 'size': 0.5},
              {'tex': 'glass_shards', 'surface': 'floor', 'x': 8.5, 'y': 15.36, 'size': 0.42, 'flip': True},
              {'tex': 'glass_shards', 'surface': 'floor', 'x': 8.0, 'y': 15.55, 'size': 0.3}]
    return scene(
        g,
        title='The window onto the garden - a dark room, its window broken, a moonlit garden beyond',
        legend={
            'g': {'floor': {'base': 'grass', 'tint': [0.6, 0.7, 0.7]}},
            'p': {'floor': {'base': 'gravel', 'tint': [0.85, 0.85, 0.9]}},
            'F': {'wall': 'foliage', 'h': 2.4, 'fringe': 'forest'},
            'L': {'wall': [{'base': t, 'tint': HOUSE} for t in ('plaster', 'window_dark_plaster', 'window_dark_plaster',
                                                                'window_dark_plaster')], 'h': 3.6, 'top': 'concrete'},
            'l': {'wall': [{'base': 'plaster', 'tint': HOUSE}, {'base': 'window_dark_plaster', 'tint': HOUSE},
                           {'base': 'window_lit_plaster', 'tint': [0.95, 0.75, 0.5]},
                           {'base': 'window_dark_plaster', 'tint': HOUSE}], 'h': 3.6, 'top': 'concrete'},
            'T': {'wall': ['stone_dark', 'stone_dark', 'stone_dark', 'window_teal', 'stone_dark'], 'h': 4.6,
                  'top': 'stone_dark'},
            'B': {'wall': {'base': 'plaster', 'tint': ROOM}, 'h': 1.5},
            'S': {'wall': {'base': 'plaster', 'tint': ROOM}, 'h': 0.25, 'top': {'base': 'boards', 'tint': ROOM},
                  'ceil': {'base': 'ceiling_plaster', 'tint': ROOM}},
            'r': {'floor': {'base': 'wood_floor', 'tint': [0.62, 0.56, 0.56]},
                  'ceil': {'base': 'ceiling_plaster', 'tint': ROOM}},
        },
        ceiling_height=1.5,
        sky='night',
        ambient=[0.1, 0.11, 0.17],
        lights=lights,
        fog={'color': [0.04, 0.05, 0.09], 'density': 0.03},
        sprites=sprites,
        decals=decals,
        camera={'x': 8.0, 'y': 17.1, 'angle': 270, 'fov': 64, 'height': 0.62},
        shots=[
            {'x': 8.0, 'y': 17.1, 'angle': 270, 'fov': 64, 'height': 0.62, 'pitch': -0.04, 'post': NIGHT},
            {'x': 8.6, 'y': 12.4, 'look_at': [9.0, 8.0, 1.35], 'fov': 56, 'height': 0.4, 'post': NIGHT,
             'overrides': {'lights': risen}},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(window_garden().save(os.path.join(HERE, 'window_garden.json')))

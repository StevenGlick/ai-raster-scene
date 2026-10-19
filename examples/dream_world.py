"""Dream world: islands adrift in a pastel sky, with a sea of cloud far below.

Shows void floors (the sky carries on under the horizon, and each island's edge drops away as a
cliff with its own `side` texture), the `dream` sky with a moon and an eye in `sky_objects`, a wall
painted with sky and a door in it, a staircase to nowhere (`heights` with a 0.3 `height_unit`), a
mirror lake (`reflect` 0.9), and things floating in the air at absolute `z` over the void.
Run:  python dream_world.py  -> writes dream_world.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(40, 40, fill=' ')                            # nothing: open sky in every direction
g.disc(12, 30, 6.5, 'c')                              # the chequered island
g.disc(24, 18, 4.6, 'g')                              # the island of the stair
g.disc(5, 15, 3.6, 'm')                               # the mirror lake
g.disc(31, 31, 2.6, 'g')                              # an islet with a tree
g.rect(9, 25, 12, 25, 'W')                            # a wall of painted sky...
g.put(10, 25, 'D')                                    # ...with a door in it
heights = [list('.' * 40) for _ in range(40)]
for i in range(9):
    g.put(20 + i, 18, 'S')                            # nine steps climbing east, up to nothing
    heights[18][20 + i] = str(i + 1)

glow = [{'fx': 'bloom', 'strength': 0.45, 'threshold': 0.8, 'radius': 8},
        {'fx': 'vignette', 'strength': 0.25, 'color': [0.35, 0.25, 0.45]}]
s = scene(
    g,
    title='Dream world - the islands in the sky',
    heights=[''.join(r) for r in heights],
    height_unit=0.3,
    legend={
        ' ': {'floor': 'void'},
        'c': {'floor': 'checker', 'side': 'marble'},
        'g': {'floor': 'grass', 'side': 'stone_pale'},
        'm': {'floor': 'obsidian', 'reflect': 0.9, 'side': 'marble'},
        'W': {'wall': 'sky_wall', 'h': 2.2},
        'D': {'wall': ['door_wood', 'sky_wall'], 'h': 2.2},
        'S': {'wall': 'marble', 'top': 'marble', 'side': 'stone_pale'},
    },
    sky='dream',
    sky_objects=[
        {'type': 'moon', 'azimuth': 262, 'elevation': 20, 'size': 6, 'color': [0.98, 0.9, 0.93],
         'color2': [0.85, 0.75, 0.85], 'lit_from': 230, 'phase': 0.35},
        {'type': 'eye', 'azimuth': 322, 'elevation': 15, 'size': 6.5, 'color': [0.42, 0.6, 0.9]},
    ],
    ambient=[0.46, 0.42, 0.5],
    lights=[
        {'type': 'sun', 'azimuth': 150, 'elevation': 28, 'color': [1.0, 0.9, 0.86], 'intensity': 0.55, 'disc': False},
    ],
    sprites=[
        {'x': 14.6, 'y': 31.6, 'type': 'door_frame'},
        {'id': 'dreamer', 'x': 12.6, 'y': 28.2, 'type': 'dreamer',
         'light': {'radius': 2.0, 'color': [1.0, 0.8, 0.5], 'intensity': 0.5}},
        {'x': 8.4, 'y': 31.6, 'type': 'chess_pawn'}, {'x': 15.6, 'y': 33.4, 'type': 'chess_pawn', 'tint': [0.22, 0.2, 0.24]},
        {'x': 16.6, 'y': 29.4, 'type': 'chess_king', 'tint': [0.22, 0.2, 0.24]},
        {'x': 7.4, 'y': 28.8, 'type': 'chess_king'},
        {'x': 31.4, 'y': 30.8, 'type': 'tree', 'scale': 2.2},
        {'x': 28.0, 'y': 6.0, 'type': 'sky_whale', 'z': 3.4, 'scale': 3.2},
        {'x': 5.6, 'y': 14.6, 'type': 'koi', 'z': 0.9}, {'x': 4.2, 'y': 16.4, 'type': 'koi', 'z': 1.3, 'flip': True},
        {'x': 6.6, 'y': 16.2, 'type': 'koi', 'z': 0.55, 'scale': 0.3},
        {'x': 19.5, 'y': 23.0, 'type': 'orb', 'z': 1.0}, {'x': 22.0, 'y': 26.5, 'type': 'orb', 'z': 1.6},
        {'x': 8.0, 'y': 22.0, 'type': 'orb', 'z': 1.3}, {'x': 27.0, 'y': 12.0, 'type': 'orb', 'z': 2.0},
        {'x': 33.0, 'y': 21.0, 'type': 'floating_rock', 'z': 0.8, 'scale': 1.4},
        {'x': 6.0, 'y': 6.0, 'type': 'floating_rock', 'z': 2.2, 'scale': 2.2},
        {'x': 36.0, 'y': 10.0, 'type': 'floating_rock', 'z': 0.2, 'scale': 1.0},
        {'x': 31.0, 'y': 26.0, 'type': 'pocket_watch', 'z': 1.3},
        {'x': 4.0, 'y': 22.0, 'type': 'balloon', 'z': 2.4, 'scale': 2.4},
    ],
    camera={'x': 12.4, 'y': 34.6, 'look_at': [10.6, 25.0, 0.9], 'fov': 74},
    shots=[
        {'x': 12.4, 'y': 34.6, 'look_at': [10.6, 25.0, 0.9], 'fov': 74, 'post': glow},
        {'x': 16.0, 'y': 25.6, 'look_at': [24.5, 18.0, 1.0], 'fov': 64, 'post': glow,
         'overlays': [{'type': 'caption', 'text': 'Every stair goes somewhere. Not this one.', 'at': 'bottom', 'box': True}]},
        {'x': 5.0, 'y': 18.0, 'look_at': [5.0, 10.0, 0.7], 'fov': 72, 'post': glow},
    ],
    contact_shadows=0.45,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dream_world.json')))

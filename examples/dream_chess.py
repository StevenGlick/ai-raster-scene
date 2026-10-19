"""The chequered plain: a dream of a chess game nobody finished, on marble floating in the sky.

Shows the dream things from scripts/dream.py: a marble chess set (`chess_pawn` to `chess_king`,
tinted dark for the other side) standing giant on a plain of `checker_marble` that mirrors them;
a `clock` in `sky_objects`, melting; a `melting_clock` slumped over a plinth and an `hourglass`
on another; `stone_arch`es and a `stair_float` hanging in the air at `z`; a lone door at the top
of a stair that climbs out of the floor; a square hole in the plain with the sky showing through
underneath (void floor cells); and `paper_boat`s sailing on the polish as if it were water.
Run:  python dream_chess.py  -> writes dream_chess.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W = H = 44
g = Grid(W, H, fill=' ')                              # open sky all round
g.disc(22, 22, 17.5, 'c')                             # the plain of chequered marble
g.rect(23, 23, 28, 28, 'h')                           # a hole in it, with the sky underneath: its rim
g.rect(24, 24, 27, 27, ' ')                           # drops away in walls painted with sky
g.rect(14, 12, 18, 12, 'W')                           # a wall standing on its own...
g.put(16, 12, 'D')                                    # ...with a door in it
heights = [list('.' * W) for _ in range(H)]
for i in range(6):                                    # a stair out of the floor, up to a landing
    g.put(30, 20 - i, 'S')
    heights[20 - i][30] = str(i + 1)
g.put(30, 14, 'S')
heights[14][30] = '6'
for x, y, h in ((18, 26, '2'), (22, 29, '2')):        # two plinths
    g.put(x, y, 'P')
    heights[y][x] = h

DARK = [0.24, 0.22, 0.28]
white = [('chess_king', 20.5, 17.5), ('chess_queen', 23.0, 18.2), ('chess_knight', 17.8, 21.0),
         ('chess_bishop', 25.6, 21.5), ('chess_rook', 13.6, 18.8), ('chess_pawn', 21.2, 21.8),
         ('chess_pawn', 15.6, 23.6), ('chess_pawn', 26.8, 17.0)]
black = [('chess_king', 29.0, 31.4), ('chess_rook', 29.8, 27.6), ('chess_knight', 23.4, 25.0),
         ('chess_bishop', 15.8, 29.4), ('chess_pawn', 20.0, 31.4), ('chess_pawn', 27.6, 23.4),
         ('chess_queen', 12.6, 26.2)]
glow = [{'fx': 'bloom', 'strength': 0.4, 'threshold': 0.8, 'radius': 8},
        {'fx': 'vignette', 'strength': 0.25, 'color': [0.35, 0.25, 0.45]}]

s = scene(
    g,
    title='The chequered plain - a dream of an unfinished game',
    heights=[''.join(r) for r in heights],
    height_unit=0.3,
    legend={
        ' ': {'floor': 'void'},
        'c': {'floor': 'checker_marble', 'side': 'marble', 'reflect': 0.22},
        'h': {'floor': 'checker_marble', 'side': 'sky_wall', 'reflect': 0.22},
        'W': {'wall': 'sky_wall', 'h': 2.4},
        'D': {'wall': ['door_wood', 'sky_wall'], 'h': 2.4},
        'S': {'wall': 'marble', 'top': 'marble', 'side': 'marble', 'floor': 'checker_marble'},
        'P': {'wall': 'marble', 'top': 'marble', 'floor': 'checker_marble'},
    },
    sky='dream',
    sky_objects=[
        {'type': 'clock', 'azimuth': 268, 'elevation': 16, 'size': 9, 'time': 10.15, 'melt': 0.5},
        {'type': 'moon', 'azimuth': 210, 'elevation': 26, 'size': 3.5, 'color': [0.98, 0.9, 0.93],
         'color2': [0.85, 0.75, 0.85], 'lit_from': 230, 'phase': 0.35},
    ],
    ambient=[0.5, 0.46, 0.54],
    lights=[{'type': 'sun', 'azimuth': 140, 'elevation': 30, 'color': [1.0, 0.9, 0.86], 'intensity': 0.55,
             'disc': False}],
    fog={'color': [0.86, 0.76, 0.86], 'density': 0.012, 'sky_mix': 0.0},
    sprites=[{'x': x, 'y': y, 'type': t, 'scale': 2.0 * {'chess_pawn': 0.9, 'chess_rook': 1.1, 'chess_bishop': 1.3,
                                                         'chess_knight': 1.2, 'chess_queen': 1.45,
                                                         'chess_king': 1.55}[t]} for t, x, y in white] +
            [{'x': x, 'y': y, 'type': t, 'tint': DARK, 'flip': True,
              'scale': 2.0 * {'chess_pawn': 0.9, 'chess_rook': 1.1, 'chess_bishop': 1.3, 'chess_knight': 1.2,
                              'chess_queen': 1.45, 'chess_king': 1.55}[t]} for t, x, y in black] + [
        {'x': 30.5, 'y': 14.5, 'type': 'door_frame', 'z': 1.8},       # on the landing (a block this tall is not stood on by itself)
        {'x': 18.5, 'y': 27.03, 'type': 'melting_clock', 'z': 0.17},   # just off the plinth's face, fold on its edge
        {'x': 22.5, 'y': 29.5, 'type': 'hourglass'},
        {'x': 16.0, 'y': 13.0, 'type': 'stone_arch', 'z': 2.8, 'scale': 2.6},
        {'x': 27.5, 'y': 19.5, 'type': 'stone_arch', 'z': 1.7, 'scale': 1.8, 'flip': True},
        {'x': 11.5, 'y': 19.0, 'type': 'stair_float', 'z': 2.0, 'scale': 3.0},
        {'x': 24.4, 'y': 34.4, 'type': 'paper_boat'}, {'x': 27.0, 'y': 33.2, 'type': 'paper_boat', 'flip': True},
        {'x': 9.6, 'y': 24.0, 'type': 'paper_boat', 'scale': 0.24},
        {'id': 'dreamer', 'x': 21.8, 'y': 35.2, 'type': 'dreamer', 'facing': 270,
         'light': {'radius': 2.0, 'color': [1.0, 0.8, 0.5], 'intensity': 0.5}},
        {'x': 17.0, 'y': 10.0, 'type': 'koi', 'z': 2.2}, {'x': 16.2, 'y': 9.4, 'type': 'koi', 'z': 2.5, 'flip': True},
    ],
    camera={'x': 21.0, 'y': 38.6, 'look_at': [21.0, 18.0, 1.6], 'fov': 70},
    shots=[
        {'x': 21.0, 'y': 38.6, 'look_at': [21.0, 18.0, 1.6], 'fov': 70, 'post': glow,
         'overlays': [{'type': 'caption', 'text': 'Nobody remembers whose move it is', 'at': 'top', 'box': True}]},
        {'x': 34.6, 'y': 23.2, 'look_at': [30.5, 14.5, 2.4], 'fov': 70, 'post': glow},
        {'x': 25.6, 'y': 31.4, 'height': 2.4, 'look_at': [25.8, 25.6, -0.6], 'fov': 70, 'post': glow},
        {'x': 18.0, 'y': 28.7, 'look_at': [18.6, 27.0, 0.42], 'fov': 58, 'post': glow},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dream_chess.json')))

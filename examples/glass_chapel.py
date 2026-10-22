"""The glass chapel: mid-morning, the sun in the south-east, and the nave full of coloured light - through tall
lancets down the south wall, laying their colours across the floor and the pews and hanging them in the dusty
air, under a rose window over the altar. The north wall's lancets glow with the sky behind them, but no sun
comes through them.

Shows coloured glass the sun comes in through: `lancet_window` and `rose_window` (and `stained_glass`) are wall
textures whose panes the light passes, taking each pane's colour - the window's pattern on the floor where its
light falls, and coloured shafts in the volumetric fog (`shafts`) - while their lead and stone tracery stop it.
Walls are a cell thick, so the light comes in where the sun stands well in front of a window; round to its side,
the stone either side cuts it off, as a deep window's jambs do. A nave of pale stone under a timbered roof, rows
of oak `pew`s either side of the aisle, an altar on a dais with `candles`, and the `monk` standing in the light.
Run:  python glass_chapel.py  -> writes glass_chapel.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402


def glass_chapel():
    g = Grid(26, 13, fill=',')
    g.room(3, 2, 22, 10, '#', '.')                  # the nave, running east to the altar
    for x in range(5, 21, 3):
        g.put(x, 10, 'L')                           # tall lancets down the south wall, the sun behind them...
        g.put(x, 2, 'L')                            # ...and the north wall, lit by the sky alone
    g.put(22, 4, 'L')
    g.put(22, 8, 'L')                               # and either side of the altar...
    g.put(22, 6, 'R')                               # ...under the rose window
    g.rect(19, 4, 21, 8, 'D')                       # the dais
    g.put(21, 6, 'A')                               # the altar
    heights = [list('.' * 26) for _ in range(13)]
    for y in range(4, 9):
        for x in range(19, 22):
            heights[y][x] = '2'
    heights[6][21] = '4'
    g.put(3, 6, '.')                                # the west door, open
    pews = [{'type': 'pew', 'x': x, 'y': y, 'angle': 0, 'length': 2.4, 'seed': k, 'fill': 0.4}
            for k, x in enumerate([8.4 + 0.6 * i for i in range(10)]) for y in (4.6, 8.4)]
    return scene(
        g,
        title='The glass chapel - morning through the windows',
        heights=[''.join(r) for r in heights],
        height_unit=0.15,
        legend={
            ',': {'floor': 'grass'},
            '#': {'wall': 'stone_pale', 'h': 3.0},
            'L': {'wall': ['stone_pale', 'lancet_window', 'lancet_window'], 'h': 3.0},
            'R': {'wall': ['stone_pale', 'stone_pale', 'rose_window'], 'h': 3.0},
            '.': {'floor': 'flagstone', 'ceil': 'wood_panel'},
            'D': {'wall': 'marble', 'top': 'flagstone', 'ceil': 'wood_panel'},
            'A': {'wall': 'marble', 'top': 'marble', 'ceil': 'wood_panel'},
        },
        ceiling_height=3.0,
        sky='day',
        ambient=[0.25, 0.245, 0.28],
        lights=[{'type': 'sun', 'azimuth': 75, 'elevation': 25, 'color': [1.0, 0.92, 0.78], 'intensity': 2.2,
                 'disc': False},
                {'x': 20.6, 'y': 6.5, 'z': 0.9, 'radius': 2.4, 'color': [1.0, 0.7, 0.4], 'intensity': 0.7}],
        fog={'color': [0.16, 0.15, 0.15], 'density': 0.02, 'glow': 0.4, 'shafts': 8},
        objects=pews,
        sprites=[
            {'id': 'monk', 'x': 16.75, 'y': 7.0, 'type': 'monk', 'facing': 234},
            {'x': 21.5, 'y': 6.2, 'type': 'candles'}, {'x': 21.5, 'y': 6.8, 'type': 'candles'},
        ],
        camera={'x': 5.6, 'y': 6.5, 'look_at': [19.0, 7.0, 0.8], 'fov': 66, 'height': 0.56},
        shots=[
            {'x': 5.6, 'y': 6.5, 'look_at': [19.0, 7.0, 0.8], 'fov': 66, 'height': 0.56,
             'overlays': [{'type': 'caption', 'text': 'Matins', 'at': 'top', 'box': True}]},
            {'x': 12.4, 'y': 3.3, 'look_at': [14.0, 10.0, 1.0], 'fov': 70, 'height': 0.55},
            {'x': 15.0, 'y': 4.6, 'look_at': 'monk', 'fov': 60, 'height': 0.45},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(glass_chapel().save(os.path.join(HERE, 'glass_chapel.json')))

"""Cathedral ruin: sunbeams through broken windows and a fallen roof, dust hanging in the light.

Shows sunlight entering roofed rooms through openings (see-through `window_broken` storeys and
a collapsed stretch of roof), shafts of light in volumetric fog, and a figure seen from behind
standing in the light. The nave stands on two rows of octagonal piers of dressed stone laid in
drums (`column` objects of `ashlar`, with plinths and capitals) carrying timber wall plates (`beam`)
under the roof; where the roof fell in, its pier is broken off and its plate lies on the floor.
Run:  python cathedral_ruin.py  -> writes cathedral_ruin.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(26, 36, fill=',')
g.room(6, 2, 19, 33, '#', '.')                       # the nave
for y in range(5, 31, 3):
    g.put(19, y, 'W')                                 # broken windows down the east wall...
    g.put(6, y, 'w')                                  # ...and blind arches down the west
g.rect(13, 14, 17, 18, 'o')                           # where the roof fell in
g.rect(11, 3, 14, 4, 'D')                             # the sanctuary dais
g.put(12, 3, 'A')
g.put(13, 3, 'A')                                     # the altar
heights = [list('.' * 26) for _ in range(36)]
for y in (3, 4):
    for x in range(11, 15):
        heights[y][x] = '3'
heights[3][12] = heights[3][13] = '6'
g.put(12, 33, '.')
g.put(13, 33, '.')                                    # the great door, open

s = scene(
    g,
    title='Cathedral ruin - light through the broken windows',
    heights=[''.join(r) for r in heights],
    legend={
        ',': {'floor': 'grass'},
        '#': {'wall': 'stone_pale', 'h': 4.0},
        'W': {'wall': ['stone_pale', 'stone_pale', 'window_broken', 'stone_pale'], 'h': 4.0},
        'w': {'wall': ['stone_pale', 'stone_pale', 'stone_dark', 'stone_pale'], 'h': 4.0},
        '.': {'floor': 'flagstone', 'ceil': 'beams'},
        'o': {'floor': 'flagstone'},
        'D': {'wall': 'marble', 'top': 'flagstone', 'ceil': 'beams'},
        'A': {'wall': 'marble', 'top': 'marble', 'ceil': 'beams'},
    },
    ceiling_height=4.0,
    sky='day',
    ambient=[0.2, 0.18, 0.16],
    lights=[{'type': 'sun', 'azimuth': 0, 'elevation': 36, 'color': [1.0, 0.9, 0.72], 'intensity': 1.2, 'disc': False}],
    fog={'color': [0.12, 0.11, 0.09], 'density': 0.06, 'glow': 0.6, 'shafts': 2.4},
    sprites=[{'x': x, 'y': y, 'type': 'pew', 'scale': 0.42, 'stretch': 2.0, 'tint': [0.8, 0.75, 0.7]}
             for y in (24.0, 26.0, 28.0) for x in (11.3, 14.7)] + [
        {'id': 'pilgrim', 'x': 11.3, 'y': 16.6, 'type': 'spiritualist', 'facing': 270},
        {'x': 12.2, 'y': 3.5, 'type': 'candles'}, {'x': 13.6, 'y': 3.5, 'type': 'candles'},
        {'x': 16.2, 'y': 8.5, 'type': 'ivy_hang', 'z': 2.9}, {'x': 9.8, 'y': 23.5, 'type': 'ivy_hang', 'z': 2.9, 'flip': True},
        # the fallen roof: rafters still spanning the hole, ivy hanging from its edges, and under it
        # the column drums and rubble that came down, grass growing in the light
        *[{'x': 15.0, 'y': y, 'type': 'log', 'planes': 1, 'angle': 0, 'length': 5.6, 'scale': 0.3, 'z': 3.68,
           'shadow': False, 'tint': [0.55, 0.45, 0.38]} for y in (15.1, 16.9)],
        {'x': 14.2, 'y': 16.0, 'type': 'log', 'planes': 1, 'angle': 90, 'length': 3.4, 'scale': 0.26, 'z': 3.72,
         'shadow': False, 'tint': [0.5, 0.42, 0.36]},
        *[{'x': x, 'y': y, 'type': 'ivy_hang', 'z': 3.0, 'scale': 1.0, 'flip': k % 2 == 1}
          for k, (x, y) in enumerate(((13.4, 14.1), (16.4, 14.1), (17.9, 16.0), (14.6, 18.9), (13.1, 17.5)))],
        {'x': 14.4, 'y': 16.4, 'type': 'column_drum'}, {'x': 15.4, 'y': 14.8, 'type': 'column_drum', 'flip': True},
        {'x': 13.6, 'y': 15.0, 'type': 'rubble', 'scale': 0.5}, {'x': 17.0, 'y': 17.8, 'type': 'rubble', 'scale': 0.4},
    ],
    objects=(
        # the arcades: two rows of piers between the windows, 3.2 in from each wall, carrying the roof
        [{'type': 'column', 'x': x, 'y': float(y), 'material': 'ashlar', 'radius': 0.26, 'height': 3.7, 'base': 0.32,
          'capital': 0.28, 'seed': 10 * k + i} for k, x in enumerate((9.8, 16.2)) for i, y in enumerate(range(7, 29, 3))
         if (x, y) != (16.2, 16)]
        + [{'type': 'column', 'x': 16.2, 'y': 16.0, 'material': 'ashlar', 'radius': 0.26, 'height': 1.5, 'base': 0.32,
            'broken': 0.5, 'seed': 77}]                                  # the one that fell with the roof
        # timber wall plates along the tops of the piers, under the roof beams; the east one broken
        # where the roof fell, a length of it down on the floor
        + [{'type': 'beam', 'x': x, 'y': (y0 + y1) / 2, 'z': 3.7, 'angle': 90, 'length': y1 - y0, 'width': 0.3,
            'depth': 0.3, 'material': 'wood', 'seed': k} for k, (x, y0, y1) in enumerate(
               ((9.8, 6.5, 28.5), (16.2, 6.5, 13.5), (16.2, 18.6, 28.5)))]
        + [{'type': 'beam', 'x': 15.0, 'y': 16.6, 'angle': 62, 'length': 3.4, 'width': 0.3, 'depth': 0.3,
            'material': 'wood', 'seed': 9}]),
    scatter=[{'of': 'rubble', 'on': '.o', 'density': 0.18, 'sizes': ['tiny', 'small', 'medium'], 'seed': 4},
             {'of': 'undergrowth', 'on': 'o', 'density': 0.9, 'clump': 1.2, 'seed': 7}],
    grime=0.3,
    camera={'x': 12.8, 'y': 31.5, 'look_at': [12.8, 3.0, 1.2], 'fov': 70},
    shots=[
        {'x': 12.8, 'y': 31.5, 'look_at': [12.8, 3.0, 1.2], 'fov': 70,
         'overlays': [{'type': 'caption', 'text': 'The nave, morning', 'at': 'top', 'box': True}]},
        {'x': 13.0, 'y': 22.4, 'look_at': [17.0, 9.0, 1.7], 'fov': 70},
        {'x': 10.8, 'y': 20.8, 'look_at': [10.6, 10.0, 1.0], 'fov': 62},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cathedral_ruin.json')))

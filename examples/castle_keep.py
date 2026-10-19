"""Castle keep: a throne room on a stepped dais, a portcullis, and the cells below.

Shows true block heights (the dais and its steps come from the `heights` layer), see-through
walls (the portcullis and the cell bars), stacked wall storeys (stained glass above stone),
contact shadows and look_at framing. Run:  python castle_keep.py  -> writes castle_keep.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(24, 34, fill='#')
g.room(1, 1, 22, 20, '#', '.')                       # the throne room
for y in (4, 8, 12, 16):
    g.put(1, y, 'W'); g.put(22, y, 'W')               # stained glass high in both long walls
for (x, y) in ((6, 7), (6, 11), (6, 15), (17, 7), (17, 11), (17, 15)):
    g.put(x, y, 'C')                                  # pillars
g.rect(7, 2, 16, 4, 'D')                              # the dais...
g.rect(8, 5, 15, 5, 'E')                              # ...and its two steps
g.rect(9, 6, 14, 6, 'E')
g.rect(11, 7, 12, 19, 'r')                            # carpet up the aisle
for x in (10, 11, 12, 13):
    g.put(x, 1, 'G')                                  # a great window of stained glass behind the throne
g.put(11, 20, 'P'); g.put(12, 20, 'P')                # portcullis down to the cells
g.rect(10, 21, 13, 32, 'f')                           # dungeon corridor
for y0 in (23, 28):                                   # two cells either side, behind bars
    g.rect(5, y0, 8, y0 + 3, 'c'); g.rect(9, y0, 9, y0 + 3, 'b')
    g.rect(15, y0, 18, y0 + 3, 'c'); g.rect(14, y0, 14, y0 + 3, 'b')

heights = [list('.' * 24) for _ in range(34)]
for y in (2, 3, 4):
    for x in range(7, 17):
        heights[y][x] = '3'                           # dais 0.3 high
for x in range(8, 16):
    heights[5][x] = '2'                               # first step 0.2
for x in range(9, 15):
    heights[6][x] = '1'                               # second step 0.1

lamp = [1.0, 0.82, 0.55]
fire = [1.0, 0.6, 0.3]
s = scene(
    g,
    title='Castle keep - throne room, portcullis and the cells below',
    heights=[''.join(r) for r in heights],
    legend={
        '#': {'wall': 'castle', 'h': 2.0},
        'W': {'wall': ['castle', 'stained_glass'], 'h': 2.0},
        'G': {'wall': ['castle', 'stained_glass'], 'h': 2.0},
        'C': {'wall': 'castle', 'h': 2.0},
        '.': {'floor': 'flagstone', 'ceil': 'beams'},
        'r': {'floor': 'carpet', 'ceil': 'beams'},
        'D': {'wall': 'castle', 'top': 'carpet'},
        'E': {'wall': 'castle', 'top': 'flagstone'},
        'P': {'wall': ['portcullis', 'castle'], 'h': 2.0},
        'f': {'floor': {'base': 'flagstone', 'tint': [0.7, 0.68, 0.72]}, 'ceil': 'rock'},
        'c': {'floor': 'dirt', 'ceil': 'rock'},
        'b': {'wall': 'bars', 'h': 2.0},
    },
    ceiling_height=2.0,
    sky=None,
    ambient=[0.07, 0.065, 0.075],
    fog={'color': [0.02, 0.016, 0.014], 'density': 0.025},
    lights=[
        {'x': 8.5, 'y': 6.6, 'z': 0.9, 'radius': 6.5, 'color': fire, 'intensity': 1.6},
        {'x': 15.5, 'y': 6.6, 'z': 0.9, 'radius': 6.5, 'color': fire, 'intensity': 1.6},
        {'x': 11.5, 'y': 9.0, 'z': 1.4, 'radius': 7.0, 'color': lamp, 'intensity': 1.0},
        {'x': 11.5, 'y': 15.0, 'z': 1.4, 'radius': 7.0, 'color': lamp, 'intensity': 1.0},
        {'x': 3.0, 'y': 8.0, 'z': 1.4, 'radius': 4.0, 'color': [0.55, 0.45, 1.0], 'intensity': 0.5},
        {'x': 2.5, 'y': 6.0, 'z': 0.8, 'radius': 4.5, 'color': fire, 'intensity': 1.1},
        {'x': 2.5, 'y': 10.0, 'z': 0.8, 'radius': 4.5, 'color': fire, 'intensity': 1.1},
        {'x': 2.5, 'y': 14.0, 'z': 0.8, 'radius': 4.5, 'color': fire, 'intensity': 1.1},
        {'x': 21.5, 'y': 6.0, 'z': 0.8, 'radius': 4.5, 'color': fire, 'intensity': 1.1},
        {'x': 21.5, 'y': 10.0, 'z': 0.8, 'radius': 4.5, 'color': fire, 'intensity': 1.1},
        {'x': 21.5, 'y': 14.0, 'z': 0.8, 'radius': 4.5, 'color': fire, 'intensity': 1.1},
        {'x': 20.0, 'y': 12.0, 'z': 1.4, 'radius': 4.0, 'color': [1.0, 0.45, 0.4], 'intensity': 0.5},
        {'x': 11.5, 'y': 19.3, 'z': 0.9, 'radius': 4.5, 'color': fire, 'intensity': 1.1},
        {'x': 10.6, 'y': 22.2, 'z': 0.9, 'radius': 7.0, 'color': fire, 'intensity': 1.7},
        {'x': 13.4, 'y': 27.5, 'z': 0.9, 'radius': 6.5, 'color': fire, 'intensity': 1.5},
        {'x': 11.8, 'y': 31.0, 'z': 0.9, 'radius': 5.0, 'color': fire, 'intensity': 1.0},
        {'x': 5.8, 'y': 23.6, 'z': 0.3, 'radius': 3.6, 'color': [1.0, 0.7, 0.4], 'intensity': 1.2},
        {'x': 8.0, 'y': 2.6, 'z': 0.9, 'radius': 5.0, 'color': fire, 'intensity': 1.2},
        {'x': 16.0, 'y': 2.6, 'z': 0.9, 'radius': 5.0, 'color': fire, 'intensity': 1.2},
        {'x': 12.0, 'y': 2.4, 'z': 1.6, 'radius': 4.5, 'color': [0.7, 0.5, 1.0], 'intensity': 0.8},   # the window's colour
        {'x': 10.4, 'y': 3.4, 'z': 1.4, 'radius': 3.5, 'color': [1.0, 0.72, 0.4], 'intensity': 0.9},  # the candelabras
        {'x': 13.6, 'y': 3.4, 'z': 1.4, 'radius': 3.5, 'color': [1.0, 0.72, 0.4], 'intensity': 0.9},
    ],
    sprites=[
        {'x': 12.0, 'y': 2.9, 'type': 'throne', 'scale': 1.3},                     # on the dais
        {'x': 9.6, 'y': 2.3, 'type': 'banner', 'z': 0.9, 'scale': 1.1},              # banners either side of it
        {'x': 14.4, 'y': 2.3, 'type': 'banner', 'z': 0.9, 'scale': 1.1},
        {'x': 10.4, 'y': 3.2, 'type': 'candelabra'}, {'x': 13.6, 'y': 3.2, 'type': 'candelabra'},
        {'x': 9.4, 'y': 7.3, 'type': 'soldier'}, {'x': 14.6, 'y': 7.3, 'type': 'soldier', 'flip': True},   # the guard
        {'id': 'knight', 'x': 13.3, 'y': 6.55, 'type': 'knight'},                   # on the lower step, to one side
        {'x': 8.5, 'y': 6.6, 'type': 'brazier'}, {'x': 15.5, 'y': 6.6, 'type': 'brazier'},
        {'x': 11.5, 'y': 9.0, 'type': 'chandelier', 'z': 1.45},
        {'x': 11.5, 'y': 15.0, 'type': 'chandelier', 'z': 1.45},
        {'x': 9.4, 'y': 10.0, 'type': 'armor'}, {'x': 14.6, 'y': 10.0, 'type': 'armor', 'flip': True},
        {'x': 9.4, 'y': 14.0, 'type': 'armor'}, {'x': 14.6, 'y': 14.0, 'type': 'armor', 'flip': True},
        {'x': 2.3, 'y': 6.0, 'type': 'banner', 'z': 0.95}, {'x': 2.3, 'y': 10.0, 'type': 'banner', 'z': 0.95},
        {'x': 2.3, 'y': 14.0, 'type': 'banner', 'z': 0.95}, {'x': 21.7, 'y': 6.0, 'type': 'banner', 'z': 0.95},
        {'x': 21.7, 'y': 10.0, 'type': 'banner', 'z': 0.95}, {'x': 21.7, 'y': 14.0, 'type': 'banner', 'z': 0.95},
        {'x': 10.2, 'y': 19.1, 'type': 'soldier'}, {'x': 13.8, 'y': 19.1, 'type': 'soldier', 'flip': True},
        {'x': 3.5, 'y': 18.5, 'type': 'chest'}, {'x': 20.0, 'y': 18.3, 'type': 'table'},
        {'x': 2.25, 'y': 6.0, 'type': 'sconce', 'z': 0.6}, {'x': 2.25, 'y': 10.0, 'type': 'sconce', 'z': 0.6},
        {'x': 2.25, 'y': 14.0, 'type': 'sconce', 'z': 0.6}, {'x': 21.75, 'y': 6.0, 'type': 'sconce', 'z': 0.6},
        {'x': 21.75, 'y': 10.0, 'type': 'sconce', 'z': 0.6}, {'x': 21.75, 'y': 14.0, 'type': 'sconce', 'z': 0.6},
        {'x': 10.25, 'y': 22.2, 'type': 'sconce', 'z': 0.7}, {'x': 13.75, 'y': 27.5, 'type': 'sconce', 'z': 0.7},
        {'x': 5.8, 'y': 23.6, 'type': 'candles'},
        {'x': 8.0, 'y': 2.6, 'type': 'brazier'}, {'x': 16.0, 'y': 2.6, 'type': 'brazier'},   # on the dais
        {'id': 'prisoner', 'x': 8.45, 'y': 24.6, 'type': 'creature',
         'light': {'radius': 2.6, 'color': [1.0, 0.35, 0.25], 'intensity': 0.9, 'z': 0.4}},
        {'x': 7.4, 'y': 23.4, 'type': 'chains', 'z': 1.3}, {'x': 16.5, 'y': 29.0, 'type': 'chains', 'z': 1.3},
        {'x': 16.2, 'y': 30.6, 'type': 'bones'}, {'x': 17.6, 'y': 23.6, 'type': 'bucket'},
        {'x': 5.6, 'y': 30.4, 'type': 'sack'}, {'x': 17.2, 'y': 25.4, 'type': 'sack', 'scale': 0.3},
    ],
    decals=[
        {'tex': 'leak', 'surface': 'wall', 'cell': [9, 27], 'face': 'east', 'u': 0.5, 'z': 1.3, 'size': 0.8},
        {'tex': 'moss_patch', 'surface': 'wall', 'cell': [14, 22], 'face': 'west', 'u': 0.5, 'z': 0.3, 'size': 0.7},
        {'tex': 'puddle_dark', 'surface': 'floor', 'x': 11.5, 'y': 26.0, 'size': 1.4},
        {'tex': 'splatter_dark', 'surface': 'floor', 'x': 6.2, 'y': 25.6, 'size': 0.9, 'opacity': 0.7},
        {'tex': 'cobweb', 'surface': 'wall', 'cell': [8, 22], 'face': 'south', 'u': 0.5, 'z': 1.6, 'size': 0.8},
        {'tex': 'crack', 'surface': 'floor', 'x': 6.5, 'y': 17.0, 'size': 1.6, 'opacity': 0.6},
    ],
    camera={'x': 12.0, 'y': 12.6, 'look_at': [12.0, 3.0, 0.8], 'fov': 62},
    shots=[
        {'x': 12.0, 'y': 12.6, 'look_at': [12.0, 3.0, 0.8], 'fov': 62,
         'overlays': [{'type': 'caption', 'text': 'The throne room', 'at': 'top', 'box': True}]},
        {'x': 3.6, 'y': 18.4, 'look_at': [1.6, 5.0, 1.15], 'fov': 70},
        {'x': 12.2, 'y': 10.0, 'look_at': 'knight', 'fov': 62,
         'overlays': [{'type': 'bubble', 'anchor': 'knight', 'name': 'Knight',
                       'text': 'The king sees no one tonight. State your business, or leave.'}]},
        {'x': 12.0, 'y': 17.0, 'angle': 90, 'fov': 70,
         'overlays': [{'type': 'prompt', 'key': 'E', 'text': 'Raise the portcullis'}]},
        {'x': 11.2, 'y': 25.6, 'look_at': [8.45, 24.6, 0.42], 'fov': 62,
         'post': [{'fx': 'vignette', 'strength': 0.55}]},
    ],
    contact_shadows=0.55,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'castle_keep.json')))

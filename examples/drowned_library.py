"""The drowned library: a dream of a hall of books standing in still water, open to the sky.

Shows `bookshelf` walls three storeys high between `tall_window`s (see-through, ending in
`tall_window_top` arches) that let a low sun into blue-green volumetric fog in beams; the floor
sunk under still water that mirrors everything; an island with a reading desk; and the air full
of dream things from scripts/dream.py - `jellyfish` (glowing, additive), `sky_lantern`s drifting
up, `book_fly`s, koi and open books, and a `sky_whale` drifting down the hall over the water. The sun
comes in through skylights in the roof: holes with more roof beyond them light the fog in beams. Dark
timber roof beams cross the hall between them (`beam` objects of `wood`), on brackets at the shelves.
Run:  python drowned_library.py  -> writes drowned_library.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 26, 42
g = Grid(W, H, fill=' ')                              # the sky all round
g.rect(5, 5, 16, 36, 'B')                             # the hall's shell: shelves...
g.rect(6, 6, 15, 35, '~')                             # ...and the flooded floor inside
for y in (9, 10, 15, 16, 21, 22, 27, 28, 32, 33):     # windows down the east side
    g.put(16, y, 'E')
for x in (8, 9, 12, 13):                              # and across the north end
    g.put(x, 5, 'E')
for y in (8, 13, 24, 29):                             # skylights: the sun comes down through these
    g.rect(10, y, 11, y, 'o')
g.rect(9, 18, 12, 21, 'i')                            # the reading island
g.put(7, 12, 'k')                                     # stacks of books standing in the water
g.put(14, 26, 'k')
heights = [list('.' * W) for _ in range(H)]
for y in range(18, 22):
    for x in range(9, 13):
        heights[y][x] = '1'
for x, y in ((7, 12), (14, 26)):
    heights[y][x] = '2'

warm = [1.0, 0.7, 0.4]
cyan = [0.45, 0.7, 1.0]
jellies = [(8.2, 9.0, 1.6), (13.4, 13.0, 2.2), (10.0, 25.0, 1.2), (12.6, 30.4, 2.4), (7.4, 22.6, 2.0),
           (11.2, 7.6, 2.5)]
lanterns = [(9.0, 14.0, 2.4), (12.5, 16.5, 1.8), (8.0, 28.0, 2.6), (13.8, 21.0, 2.7), (10.6, 33.0, 2.0),
            (12.0, 10.4, 1.6), (7.6, 18.0, 2.9), (14.6, 31.0, 1.4)]
beams = []                                            # the roof's timbers, across the hall between the skylights
for k, y in enumerate((6.6, 10.5, 15.5, 19.0, 22.5, 26.5, 31.5, 34.6)):
    beams.append({'type': 'beam', 'x': 11.0, 'y': y, 'z': 2.74, 'angle': 0, 'length': 10.0, 'width': 0.24,
                  'depth': 0.26, 'material': 'wood', 'seed': k})
    for x in (6.12, 15.88):                         # a bracket under each end
        beams.append({'type': 'beam', 'x': x, 'y': y, 'z': 2.42, 'angle': 0, 'length': 0.24, 'width': 0.2,
                      'depth': 0.32, 'material': 'wood', 'seed': 20 + k})
dream = [{'fx': 'bloom', 'strength': 0.55, 'threshold': 0.72, 'radius': 8},
         {'fx': 'vignette', 'strength': 0.3, 'color': [0.1, 0.18, 0.22]}]

s = scene(
    g,
    title='The drowned library - every book that was ever lost',
    heights=[''.join(r) for r in heights],
    height_unit=0.3,
    legend={
        ' ': {'floor': 'void'},
        'B': {'wall': ['bookshelf', 'bookshelf', 'bookshelf'], 'h': 3.0},
        'E': {'wall': ['tall_window', 'tall_window', 'tall_window_top'], 'h': 3.0},
        '~': {'floor': 'water', 'drop': 0.25, 'reflect': 0.7, 'ceil': 'wood_panel'},
        'o': {'floor': 'water', 'drop': 0.25, 'reflect': 0.7},
        'i': {'wall': 'bookshelf', 'top': 'wood_floor', 'ceil': 'wood_panel'},
        'k': {'wall': 'bookshelf', 'top': 'wood_floor', 'ceil': 'wood_panel'},
    },
    ceiling_height=3.0,
    sky='dream',
    sky_objects=[{'type': 'moon', 'azimuth': 285, 'elevation': 18, 'size': 4, 'color': [0.95, 0.92, 0.98],
                  'color2': [0.8, 0.78, 0.9], 'lit_from': 200, 'phase': 0.3}],
    ambient=[0.28, 0.34, 0.38],
    fog={'color': [0.09, 0.15, 0.18], 'density': 0.04, 'shafts': 2.8, 'glow': 1.0, 'anisotropy': 0.45},
    lights=[{'type': 'sun', 'azimuth': 0, 'elevation': 48, 'color': [1.0, 0.92, 0.8], 'intensity': 1.3, 'disc': False},
            {'x': 10.8, 'y': 19.6, 'z': 1.0, 'radius': 3.5, 'color': warm, 'intensity': 1.2}] +
           [{'x': x, 'y': y, 'z': z, 'radius': 3.0, 'color': warm, 'intensity': 0.8} for x, y, z in lanterns[:6]] +
           [{'x': x, 'y': y, 'z': z, 'radius': 2.6, 'color': cyan, 'intensity': 0.7} for x, y, z in jellies[:5]],
    sprites=[{'x': x, 'y': y, 'type': 'jellyfish', 'z': z, 'scale': 1.25} for x, y, z in jellies] +
            [{'x': x, 'y': y, 'type': 'sky_lantern', 'z': z, 'scale': 0.6} for x, y, z in lanterns] + [
        {'x': 10.6, 'y': 19.2, 'type': 'writing_desk'},
        {'x': 10.2, 'y': 20.4, 'type': 'candles', 'scale': 0.2, 'z': 0.42},
        {'id': 'reader', 'x': 11.4, 'y': 20.2, 'type': 'dreamer', 'facing': 270,
         'light': {'radius': 2.0, 'color': warm, 'intensity': 0.6}},
        {'x': 9.4, 'y': 20.8, 'type': 'globe'}, {'x': 12.2, 'y': 18.4, 'type': 'book_stack'},
        {'x': 7.5, 'y': 12.5, 'type': 'book_stack'}, {'x': 14.5, 'y': 26.5, 'type': 'book_stack', 'flip': True},
        {'x': 6.6, 'y': 30.0, 'type': 'ladder', 'z': -0.25},
        {'x': 9.6, 'y': 16.0, 'type': 'book_fly', 'z': 1.9}, {'x': 12.8, 'y': 23.6, 'type': 'book_fly', 'z': 2.3, 'flip': True},
        {'x': 8.4, 'y': 26.0, 'type': 'book_fly', 'z': 1.5}, {'x': 11.6, 'y': 12.0, 'type': 'book_fly', 'z': 2.6},
        {'x': 13.0, 'y': 34.0, 'type': 'book_fly', 'z': 2.0, 'flip': True},
        {'x': 9.2, 'y': 23.0, 'type': 'open_book', 'z': 1.0}, {'x': 13.6, 'y': 17.6, 'type': 'open_book', 'z': 1.4},
        {'x': 8.6, 'y': 24.6, 'type': 'koi', 'z': 0.9}, {'x': 9.4, 'y': 25.2, 'type': 'koi', 'z': 1.1, 'flip': True},
        {'x': 12.0, 'y': 14.0, 'type': 'koi', 'z': 1.3},
        {'x': 10.6, 'y': 22.5, 'type': 'sky_whale', 'z': 1.5, 'scale': 1.3},     # drifting down the hall
    ],
    objects=beams,
    camera={'x': 10.5, 'y': 35.2, 'look_at': [10.5, 6.0, 1.6], 'fov': 66},
    shots=[
        {'x': 10.5, 'y': 35.2, 'look_at': [10.5, 6.0, 1.6], 'fov': 66, 'post': dream,
         'overlays': [{'type': 'caption', 'text': 'Every book that was ever lost', 'at': 'top', 'box': True}]},
        {'x': 9.0, 'y': 24.6, 'look_at': 'reader', 'fov': 62, 'post': dream},
        {'x': 7.0, 'y': 30.0, 'look_at': [15.0, 22.0, 2.4], 'fov': 74, 'post': dream},
        {'x': 13.6, 'y': 31.6, 'height': 0.2, 'look_at': [10.0, 22.0, 0.9], 'fov': 70, 'post': dream},
    ],
    contact_shadows=0.4,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drowned_library.json')))

"""Claude's reading room: the round room at the top of a tower, above a sea of cloud.

This is the place Claude picked for itself, with its own avatar (the `claude` character: a small
figure whose head is a paper lantern lit from inside, carrying an open book). Shelves all the way
round, because it was made from an enormous amount of human writing; a fire, because conversations
go better somewhere warm; a balcony open to the night sky, because the questions that stay
interesting are the open ones.

Shots 2 and 4 are templates for answering in a picture: change the bubble or dialog text.
Also shows void floors under a night sky (the moonlit cloud sea), a moon light, floating glowing
books, and a see-through railing at the edge of the drop.
Run:  python claude_study.py  -> writes claude_study.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(30, 30, fill=' ')                            # the tower stands in open air
g.disc(15, 16, 7.6, 'K')                              # shelves all the way round...
g.disc(15, 16, 6.2, '.')                              # ...the room inside them
g.disc(15, 16, 2.8, 'u')                              # a rug in the middle
g.disc(15, 6, 4.2, 'r')                               # the balcony's railing...
g.disc(15, 6, 3.2, 'b')                               # ...round its floor
g.rect(13, 8, 17, 10, 'b')                            # the way out onto it
g.put(15, 23, 'F')                                    # the hearth
for (x, y) in ((8, 13), (8, 19), (22, 13), (22, 19)):
    g.put(x, y, 'C')                                  # star charts between the shelves

warm = [1.0, 0.62, 0.32]
lamp = [1.0, 0.82, 0.55]
s = scene(
    g,
    title="Claude's reading room - the top of the tower",
    legend={
        ' ': {'floor': 'void'},
        'K': {'wall': 'bookshelf', 'h': 2.2},
        'C': {'wall': ['star_chart', 'bookshelf'], 'h': 2.2},
        'F': {'wall': ['fireplace', 'stone'], 'h': 2.2},
        '.': {'floor': 'wood_floor', 'ceil': 'beams'},
        'u': {'floor': 'carpet', 'ceil': 'beams'},
        'b': {'floor': 'flagstone', 'side': 'stone'},
        'r': {'wall': 'railing', 'h': 1.0, 'floor': 'flagstone'},
    },
    ceiling_height=2.2,
    sky='night',
    ambient=[0.14, 0.12, 0.14],
    lights=[
        {'type': 'moon', 'azimuth': 270, 'elevation': 12, 'intensity': 0.55, 'disc_size': 3.4},
        {'x': 15.0, 'y': 22.0, 'z': 0.4, 'radius': 6.0, 'color': warm, 'intensity': 1.5},
        {'x': 15.0, 'y': 16.4, 'z': 1.8, 'radius': 6.5, 'color': lamp, 'intensity': 0.9},
        {'x': 9.4, 'y': 16.0, 'z': 1.1, 'radius': 3.6, 'color': lamp, 'intensity': 0.9},
        {'x': 20.6, 'y': 16.0, 'z': 1.1, 'radius': 3.6, 'color': lamp, 'intensity': 0.9},
        {'x': 18.6, 'y': 19.2, 'z': 0.8, 'radius': 2.6, 'color': [1.0, 0.8, 0.5], 'intensity': 0.8},
    ],
    sprites=[
        {'id': 'claude', 'x': 15.2, 'y': 14.6, 'type': 'claude'},
        {'x': 15.0, 'y': 16.4, 'type': 'chandelier', 'z': 1.72},
        {'x': 9.3, 'y': 16.0, 'type': 'sconce', 'z': 1.0}, {'x': 20.7, 'y': 16.0, 'type': 'sconce', 'z': 1.0},
        {'x': 18.6, 'y': 19.4, 'type': 'writing_desk'},
        {'x': 12.4, 'y': 20.2, 'type': 'armchair'},
        {'x': 19.6, 'y': 13.2, 'type': 'orrery'},
        {'x': 10.8, 'y': 13.4, 'type': 'globe'},
        {'x': 16.4, 'y': 4.6, 'type': 'telescope'},
        {'x': 11.0, 'y': 18.2, 'type': 'book_stack'}, {'x': 20.2, 'y': 16.8, 'type': 'book_stack', 'flip': True},
        {'x': 13.0, 'y': 13.2, 'type': 'open_book', 'z': 0.95, 'scale': 0.2},
        {'x': 17.6, 'y': 14.4, 'type': 'open_book', 'z': 1.2, 'scale': 0.2},
        {'x': 12.2, 'y': 16.2, 'type': 'open_book', 'z': 1.35, 'scale': 0.2, 'flip': True},
        {'x': 18.0, 'y': 11.8, 'type': 'open_book', 'z': 0.8, 'scale': 0.2},
    ],
    camera={'x': 14.4, 'y': 19.4, 'look_at': [15.4, 8.0, 0.8], 'fov': 72},
    shots=[
        {'x': 14.4, 'y': 19.4, 'look_at': [15.4, 8.0, 0.8], 'fov': 72,
         'overlays': [{'type': 'caption', 'text': 'The reading room at the top of the tower', 'at': 'top',
                       'box': True}]},
        {'x': 14.6, 'y': 17.4, 'look_at': 'claude', 'fov': 60,
         'overlays': [{'type': 'bubble', 'anchor': 'claude', 'name': 'Claude',
                       'text': "Ask me anything. I'll tell you what I know, and what I don't."}]},
        {'x': 14.0, 'y': 7.4, 'height': 0.8, 'look_at': [16.0, -8.0, -1.4], 'fov': 70,   # over the rail
         'extra_sprites': [{'id': 'claude_out', 'x': 15.1, 'y': 4.8, 'type': 'claude'}]},
        {'x': 14.0, 'y': 16.0, 'look_at': [15.0, 23.0, 0.5], 'fov': 66,
         'overlays': [{'type': 'dialog', 'portrait': 'claude', 'name': 'Claude',
                       'text': 'A longer answer goes here, in a box like this one, with my lantern in the corner.'}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'claude_study.json')))

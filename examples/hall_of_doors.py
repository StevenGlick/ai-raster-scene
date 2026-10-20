"""Hall of doors: a dream of a corridor that does not end - doors in every wall, storey above
storey, doors in the ceiling, a few of them opening onto the sky - and the sleepwalker going on
down it with her candle.

Shows `door_hall` (a painted door in a papered wall) tinted to make doors of every colour, used
for the walls at every storey and for the ceiling too; `sky_wall` cells where a door has opened
onto the sky; a `checker_marble` floor that mirrors it all; a `stair_float` rising to a
`door_frame` hung in the air; koi, books and lanterns drifting; and a soft pastel light in a pale
fog with a gentle bloom.
Run:  python hall_of_doors.py  -> writes hall_of_doors.json next to this file.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

TINTS = {'D': None, 'R': [1.05, 0.62, 0.6], 'B': [0.62, 0.78, 1.08], 'G': [0.7, 0.98, 0.76], 'Y': [1.1, 0.98, 0.62]}


def door(c):
    t = TINTS[c]
    return 'door_hall' if t is None else {'base': 'door_hall', 'tint': t}


def hall_of_doors():
    rng = np.random.default_rng(9)
    g = Grid(9, 46, fill='#')
    g.rect(2, 1, 6, 44, '.')                        # the hall
    for y in range(1, 45):                          # doors down both walls, every one its own colour
        for x in (1, 7):
            g.put(x, y, str(rng.choice(list(TINTS))))
    for x, y in ((1, 30), (7, 21), (1, 12)):
        g.put(x, y, 'S')                            # doors that have opened onto the sky
    g.rect(2, 0, 6, 0, 'E')                         # and at the far end, the sky
    legend = {c: {'wall': [door(c), door(c), door(c)], 'h': 3.0} for c in TINTS}
    legend.update({
        'S': {'wall': ['sky_wall', door('D'), door('D')], 'h': 3.0},
        '#': {'wall': 'wallpaper', 'h': 3.0},
        'E': {'wall': 'sky_wall', 'h': 3.0},
        '.': {'floor': 'checker_marble', 'ceil': 'door_hall'},
    })
    sprites = [
        {'id': 'dreamer', 'x': 4.4, 'y': 33.0, 'type': 'dreamer', 'facing': 270},
        {'x': 3.2, 'y': 25.4, 'type': 'stair_float', 'z': 0.0, 'scale': 1.6},
        {'x': 3.0, 'y': 23.9, 'type': 'door_frame', 'z': 1.55},
        {'x': 5.4, 'y': 16.0, 'type': 'door_frame', 'flip': True},
        {'x': 5.6, 'y': 8.0, 'type': 'door_frame', 'z': 0.9},
        {'x': 4.6, 'y': 28.0, 'type': 'koi', 'z': 1.9}, {'x': 3.4, 'y': 19.0, 'type': 'koi', 'z': 2.2, 'flip': True},
        {'x': 5.4, 'y': 12.0, 'type': 'koi', 'z': 1.4},
        {'x': 4.0, 'y': 22.0, 'type': 'book_fly', 'z': 1.6}, {'x': 5.2, 'y': 26.6, 'type': 'book_fly', 'z': 2.3},
        {'x': 2.6, 'y': 15.0, 'type': 'sky_lantern', 'z': 2.0}, {'x': 5.8, 'y': 31.0, 'type': 'sky_lantern', 'z': 2.4},
        {'x': 1.25, 'y': 35.5, 'type': 'wall_clock', 'z': 1.6, 'planes': 1, 'angle': 90, 'length': 0.4},
        {'x': 6.7, 'y': 39.0, 'type': 'melting_clock', 'z': 0.9, 'planes': 1, 'angle': 90, 'length': 0.7},
        {'x': 2.6, 'y': 38.0, 'type': 'paper_boat'},
    ]
    lights = [{'x': 4.5, 'y': y, 'z': 2.6, 'radius': 7.0, 'color': [1.0, 0.86, 0.7], 'intensity': 0.9}
              for y in (40.0, 32.0, 24.0, 16.0, 8.0)]
    lights += [{'x': 4.5, 'y': 1.5, 'z': 1.5, 'radius': 6.0, 'color': [0.8, 0.88, 1.0], 'intensity': 0.5},
               {'x': 4.4, 'y': 32.6, 'z': 0.5, 'radius': 2.6, 'color': [1.0, 0.7, 0.35], 'intensity': 1.0}]
    return scene(
        g,
        legend=legend,
        title='Hall of doors - a corridor that does not end',
        sky='dream',
        ceiling_height=3.0,
        ambient=[0.34, 0.32, 0.38],
        fog={'color': [0.8, 0.76, 0.88], 'density': 0.03, 'glow': 0.25},
        lights=lights,
        sprites=sprites,
        camera={'x': 4.5, 'y': 43.8, 'angle': 270, 'fov': 62, 'height': 0.5},
        shots=[
            {'x': 4.5, 'y': 43.8, 'angle': 270, 'post': [{'fx': 'bloom', 'threshold': 0.7, 'strength': 0.4, 'radius': 6}],
             'overlays': [{'type': 'caption', 'text': 'Every door is the right one', 'at': 'top', 'box': True}]},
            {'x': 5.2, 'y': 29.6, 'look_at': [3.0, 23.9, 2.0], 'fov': 66,
             'post': [{'fx': 'bloom', 'threshold': 0.7, 'strength': 0.4, 'radius': 6}]},
            {'x': 2.6, 'y': 21.0, 'look_at': [7.0, 21.5, 0.9], 'fov': 66,
             'post': [{'fx': 'bloom', 'threshold': 0.7, 'strength': 0.4, 'radius': 6}]},
            {'x': 4.5, 'y': 36.0, 'look_at': [4.5, 28.0, 3.0], 'fov': 70, 'height': 0.4,
             'post': [{'fx': 'bloom', 'threshold': 0.7, 'strength': 0.4, 'radius': 6}]},
        ],
        contact_shadows=0.4,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(hall_of_doors().save(os.path.join(HERE, 'hall_of_doors.json')))

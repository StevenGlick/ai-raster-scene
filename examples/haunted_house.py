"""Haunted house: Halloween night at the old house on the hill - jack-o'-lanterns on the steps, an
iron fence and dead trees, bats against the moon - and inside, the hall with its grand staircase,
where the family portraits watch and someone is waiting on the landing.

Shows a grand staircase built from the `heights` layer (a flight of steps with `carpet` treads up
to a landing at 1.4, a `balustrade` stood along its edge as cards at that height), a double-height
hall (`ceiling_height` 3), stacked walls of panelling and wallpaper, a fireplace, the haunted
props - `portrait`, `candelabra`, `grandfather_clock`, `cobweb` across the corners, `bats` - and
the ghost.
Run:  python haunted_house.py  -> writes haunted_house.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

WARM = [1.0, 0.64, 0.32]


def haunted_house():
    g = Grid(24, 38, fill='y')                     # the yard
    g.rect(2, 3, 21, 21, 'X')                      # the house
    g.rect(3, 4, 20, 20, 'h')                      # its hall
    g.rect(3, 4, 20, 10, 'L')                      # the landing across the back
    g.rect(9, 11, 14, 16, 'S')                     # the grand staircase down the middle
    g.put(2, 14, 'F')                              # the fireplace in the west wall
    g.rect(2, 21, 21, 21, 'M')                     # the front of the house
    for x in (2, 3, 4, 5, 18, 19, 20, 21):
        g.put(x, 21, 'w')                          # its lower wings
    g.rect(10, 21, 13, 21, 'U')                    # the tower over the door
    g.put(11, 21, 'D'); g.put(12, 21, 'D')          # the front door
    g.put(7, 21, 'N'); g.put(16, 21, 'N')           # two lit windows
    g.rect(11, 22, 12, 23, 'T')                    # the steps up to it
    g.rect(11, 24, 12, 35, 'p')                    # the path
    g.rect(0, 35, 23, 35, 'i')                     # the iron fence
    g.put(11, 35, 'p'); g.put(12, 35, 'p')          # the gate, open
    g.rect(0, 0, 23, 0, 'K'); g.rect(0, 0, 0, 37, 'K'); g.rect(23, 0, 23, 37, 'K')
    heights = []
    for y in range(38):
        row = ''
        for x in range(24):
            c = g.get(x, y)
            if c == 'S':
                row += str(1 + (16 - y))           # steps 0.2 .. 1.2, rising north
            elif c == 'L':
                row += '7'                         # the landing, 1.4
            elif c == 'T':
                row += '2' if y == 22 else '1'
            else:
                row += '.'
        heights.append(row)
    sprites = [
        # the yard: dead trees, the family plot, jack-o'-lanterns, the moon's bats
        {'x': 4.5, 'y': 28.0, 'type': 'dead_tree', 'scale': 3.6}, {'x': 19.5, 'y': 26.5, 'type': 'dead_tree', 'flip': True},
        {'x': 17.0, 'y': 30.5, 'type': 'gravestone'}, {'x': 19.0, 'y': 31.2, 'type': 'grave_cross'},
        {'x': 20.6, 'y': 29.6, 'type': 'gravestone', 'flip': True},
        {'x': 11.2, 'y': 22.3, 'type': 'jack_o_lantern', 'z': 0.4}, {'x': 12.8, 'y': 22.4, 'type': 'jack_o_lantern', 'z': 0.4},
        {'x': 10.6, 'y': 23.4, 'type': 'jack_o_lantern', 'z': 0.2, 'scale': 0.28},
        {'x': 10.6, 'y': 27.0, 'type': 'jack_o_lantern'}, {'x': 13.4, 'y': 30.0, 'type': 'jack_o_lantern', 'scale': 0.3},
        {'x': 13.0, 'y': 24.5, 'type': 'bats', 'z': 3.3, 'scale': 1.3},
        {'x': 7.0, 'y': 31.0, 'type': 'crow', 'z': 0.0},
        # the hall: candelabras, the clock, armour flanking the stair, the chandelier, cobwebs
        {'x': 8.4, 'y': 17.4, 'type': 'candelabra'}, {'x': 15.6, 'y': 17.4, 'type': 'candelabra'},
        {'x': 19.6, 'y': 14.0, 'type': 'grandfather_clock'},
        {'x': 8.5, 'y': 12.0, 'type': 'armor'}, {'x': 15.5, 'y': 12.0, 'type': 'armor', 'flip': True},
        {'x': 11.95, 'y': 15.0, 'type': 'chandelier', 'z': 2.3, 'scale': 0.8},
        {'x': 3.25, 'y': 11.25, 'type': 'cobweb', 'z': 2.1, 'planes': 1, 'angle': 135, 'length': 1.0},
        {'x': 20.75, 'y': 11.25, 'type': 'cobweb', 'z': 2.1, 'planes': 1, 'angle': 45, 'length': 1.0, 'flip': True},
        {'x': 3.25, 'y': 4.25, 'type': 'cobweb', 'z': 2.1, 'planes': 1, 'angle': 135, 'length': 1.0},
        {'x': 3.6, 'y': 15.6, 'type': 'armchair', 'flip': True},
        # the landing: the balustrade along its edge, portraits on the back wall, and the ghost
        *[{'x': x, 'y': 10.95, 'type': 'balustrade', 'z': 1.4, 'planes': 1, 'angle': 0, 'length': 3.0, 'scale': 0.5}
          for x in (4.5, 7.5, 16.5, 19.5)],
        {'x': 7.5, 'y': 4.22, 'type': 'portrait', 'z': 1.95, 'planes': 1, 'angle': 0, 'length': 0.6},
        {'x': 11.95, 'y': 4.22, 'type': 'portrait', 'z': 2.0, 'planes': 1, 'angle': 0, 'length': 0.6, 'flip': True},
        {'x': 16.5, 'y': 4.22, 'type': 'portrait', 'z': 1.95, 'planes': 1, 'angle': 0, 'length': 0.6},
        {'x': 3.22, 'y': 14.5, 'type': 'portrait', 'z': 1.25, 'planes': 1, 'angle': 90, 'length': 0.6},
        {'x': 8.0, 'y': 8.0, 'type': 'candelabra', 'z': 1.4}, {'x': 16.0, 'y': 8.0, 'type': 'candelabra', 'z': 1.4},
        {'id': 'ghost', 'x': 11.95, 'y': 11.5, 'type': 'ghost', 'z': 1.2, 'facing': 90},
    ]
    hall_lights = [{'x': 8.4, 'y': 17.4, 'z': 1.1, 'radius': 5.0, 'color': WARM, 'intensity': 1.6},
                   {'x': 15.6, 'y': 17.4, 'z': 1.1, 'radius': 5.0, 'color': WARM, 'intensity': 1.6},
                   {'x': 8.0, 'y': 8.0, 'z': 2.5, 'radius': 5.0, 'color': WARM, 'intensity': 1.5},
                   {'x': 16.0, 'y': 8.0, 'z': 2.5, 'radius': 5.0, 'color': WARM, 'intensity': 1.5},
                   {'x': 3.6, 'y': 14.5, 'z': 0.3, 'radius': 4.5, 'color': [1.0, 0.5, 0.2], 'intensity': 1.6},
                   {'x': 11.95, 'y': 15.0, 'z': 2.1, 'radius': 8.0, 'color': WARM, 'intensity': 1.3},
                   {'x': 11.95, 'y': 11.2, 'z': 1.8, 'radius': 2.6, 'color': [0.6, 0.8, 1.0], 'intensity': 0.9}]
    yard_lights = [{'x': x, 'y': y, 'z': 0.5, 'radius': 2.6, 'color': [1.0, 0.58, 0.22], 'intensity': 1.1}
                   for x, y in ((11.2, 22.6), (12.8, 22.6), (10.6, 27.3))]
    return scene(
        g,
        legend={
            'y': {'floor': 'dirt'},
            'p': {'floor': 'gravel'},
            'h': {'floor': 'wood_floor', 'ceil': 'beams'},
            'X': {'wall': ['wood_panel', 'wallpaper', 'wallpaper'], 'h': 3.0},
            'F': {'wall': ['fireplace', 'wallpaper', 'wallpaper'], 'h': 3.0},
            'M': {'wall': ['stone_dark', 'window_dark', 'window_dark'], 'h': 3.0},
            'N': {'wall': ['stone_dark', 'window_dark', 'window_lit'], 'h': 3.0},
            'w': {'wall': ['stone_dark', 'window_dark'], 'h': 2.2},
            'U': {'wall': ['stone_dark', 'window_dark', 'window_dark', 'window_lit', 'stone_dark'], 'h': 4.6},
            'D': {'wall': ['door_wood', 'window_dark', 'window_dark', 'window_lit', 'stone_dark'], 'h': 4.6},
            'S': {'wall': 'wood_panel', 'top': 'carpet', 'ceil': 'beams'},
            'L': {'wall': 'wood_panel', 'top': 'wood_floor', 'ceil': 'beams'},
            'T': {'wall': 'stone_dark', 'top': 'flagstone'},
            'i': {'wall': 'fence_iron', 'h': 0.9},
            'K': {'wall': 'forest_deep', 'h': 2.0, 'fringe': 'forest'},
        },
        heights=heights,
        height_unit=0.2,
        title='Haunted house - Halloween night',
        sky='night',
        ceiling_height=3.0,
        ambient=[0.13, 0.12, 0.17],
        fog={'color': [0.06, 0.07, 0.1], 'density': 0.02, 'glow': 0.7},
        lights=[{'type': 'moon', 'azimuth': 275, 'elevation': 24, 'intensity': 0.5}] + hall_lights + yard_lights,
        sprites=sprites,
        camera={'x': 11.95, 'y': 36.6, 'angle': 270, 'fov': 66, 'height': 0.5},
        shots=[
            {'x': 11.95, 'y': 36.6, 'angle': 270,
             'overlays': [{'type': 'caption', 'text': 'Halloween night', 'at': 'top', 'box': True}]},
            {'x': 11.95, 'y': 20.4, 'look_at': [11.95, 9.0, 1.6], 'fov': 70},
            {'x': 7.4, 'y': 18.4, 'look_at': [3.0, 14.5, 1.0], 'fov': 64,
             'overlays': [{'type': 'caption', 'text': 'Nobody has wound the clock in forty years.', 'at': 'bottom',
                           'box': True}]},
            {'x': 11.95, 'y': 18.8, 'look_at': 'ghost', 'fov': 50,
             'post': [{'fx': 'vignette', 'strength': 0.6}, {'fx': 'grain', 'amount': 0.05}],
             'overlays': [{'type': 'bubble', 'anchor': 'ghost', 'text': 'Welcome home.'}]},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(haunted_house().save(os.path.join(HERE, 'haunted_house.json')))

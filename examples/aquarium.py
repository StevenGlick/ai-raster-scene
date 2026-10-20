"""Aquarium: a dark hall in front of a great ocean tank, a tunnel through another, a gallery of
jellyfish and a reef tank at child height.

Shows the aquarium kit (scripts/aquarium.py) and glass that holds water. The ocean tank is a room
of `seabed` under a glowing `water_surface` roof, walled in `reef_wall` rockwork, a few cells of
the roof `glazed` so the sun comes down through the surface in shafts; its window is one long
`glass_pane`, floor to ceiling, whose glass has `fog` - the scene's fog carries on behind the
pane, so the water glows blue round the lamps in the tank and the shafts show, while the air in
the dark hall stays clear. A `whale_shark` and a `manta_ray` glide past, a `diver` cleans the
inside of the glass, visitors stand dark against it. The smaller tanks look through `tank_window`
frames: golden `sea_nettle`s against a glowing `jelly_backdrop`, a reef of `anemone` (with its
clownfish), `brain_coral`, `staghorn_coral`, `sea_fan`, `tube_sponge`, `angelfish` and
`blue_tang`. The tunnel has glass down both sides and a `tunnel_roof` overhead.
Run:  python aquarium.py  -> writes aquarium.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 38, 37
g = Grid(W, H, fill='#')
g.rect(1, 0, 36, 12, 'R')                            # the ocean tank, walled in rockwork
g.rect(2, 3, 35, 11, 'O')
for x, y in ((8, 5), (9, 5), (15, 4), (16, 4), (16, 5), (22, 6), (23, 6), (29, 4), (30, 4)):
    g.put(x, y, 'o')                                 # glazed: the sun comes down through the surface here
g.rect(10, 12, 27, 12, 'O')                          # the window bay: the pane stands at y = 13
g.rect(2, 13, 35, 20, 'H')                           # the hall
g.rect(4, 22, 10, 31, 'J')                           # the jelly gallery, off the hall
g.rect(5, 21, 7, 21, 'H')
for y0 in (23, 27):                                  # two jelly tanks in its west wall
    g.rect(1, y0, 2, y0 + 3, 'b')
    g.rect(2, y0 + 1, 2, y0 + 2, 'B')
    g.rect(3, y0 + 1, 3, y0 + 2, 'w')
g.rect(1, 27, 2, 30, 'd')                            # the second is the moon jellies', lit violet
g.rect(2, 28, 2, 29, 'D')
g.rect(12, 25, 13, 28, 'b')                          # and one in its east wall
g.rect(12, 26, 12, 27, 'B')
g.rect(11, 26, 11, 27, 'w')
g.rect(3, 33, 9, 35, 'R')                            # the reef tank, at the end of the gallery
g.rect(4, 33, 8, 34, 'r')
g.rect(5, 32, 7, 32, 'v')
g.rect(24, 21, 35, 35, 'R')                          # the tunnel tank
g.rect(25, 22, 34, 34, 'S')
g.rect(29, 21, 30, 32, 'T')                          # the tunnel through it

blue = [0.3, 0.68, 1.0]
lamp = [0.72, 0.9, 1.0]
water = {'tint': [0.62, 0.88, 1.0], 'opacity': 0.07, 'blur': 0, 'fog': True}
clear = {'tint': [0.9, 0.95, 1.0], 'opacity': 0.05, 'blur': 0, 'fog': True}
dark = [0.16, 0.2, 0.28]
surface = {'base': 'water_surface', 'tint': [0.55, 0.72, 0.82]}
violet = {'base': 'jelly_backdrop', 'tint': [0.3, 0.22, 0.5]}
panes = [
    {'x': 19.0, 'y': 13.0, 'type': 'glass_pane', 'angle': 0, 'length': 18.0, 'scale': 2.0, 'glass': water},
    {'x': 29.0, 'y': 27.5, 'type': 'glass_pane', 'angle': 90, 'length': 11.0, 'scale': 2.0, 'glass': water},
    {'x': 31.0, 'y': 27.5, 'type': 'glass_pane', 'angle': 90, 'length': 11.0, 'scale': 2.0, 'glass': water},
    {'x': 30.0, 'y': 33.0, 'type': 'glass_pane', 'angle': 0, 'length': 2.0, 'scale': 2.0, 'glass': water},
    {'x': 3.95, 'y': 25.0, 'type': 'glass_pane', 'angle': 90, 'length': 2.0, 'scale': 1.0, 'glass': clear},
    {'x': 3.95, 'y': 29.0, 'type': 'glass_pane', 'angle': 90, 'length': 2.0, 'scale': 1.0, 'glass': clear},
    {'x': 11.05, 'y': 27.0, 'type': 'glass_pane', 'angle': 90, 'length': 2.0, 'scale': 1.0, 'glass': clear},
    {'x': 6.5, 'y': 32.05, 'type': 'glass_pane', 'angle': 0, 'length': 3.0, 'scale': 1.0, 'glass': clear},
]
ocean = [
    {'id': 'whale', 'x': 19.6, 'y': 9.4, 'type': 'whale_shark', 'z': 0.5, 'flip': True},
    {'id': 'manta', 'x': 23.6, 'y': 8.8, 'type': 'manta_ray', 'z': 1.25},
    {'x': 11.8, 'y': 8.0, 'type': 'reef_shark', 'z': 0.45, 'scale': 0.32},
    {'x': 28.4, 'y': 6.0, 'type': 'reef_shark', 'z': 0.95, 'scale': 0.3, 'flip': True},
    {'x': 8.5, 'y': 9.6, 'type': 'sea_turtle', 'z': 0.95, 'scale': 0.34},
    {'x': 15.0, 'y': 5.4, 'type': 'fish_school', 'z': 1.25, 'scale': 1.4},
    {'x': 31.0, 'y': 8.0, 'type': 'fish_school', 'z': 0.5, 'scale': 1.0, 'flip': True},
    {'x': 10.5, 'y': 11.0, 'type': 'reef_shoal', 'z': 0.32, 'scale': 0.6},
    {'x': 26.8, 'y': 11.4, 'type': 'reef_shoal', 'z': 0.22, 'scale': 0.5, 'flip': True},
    {'id': 'diver', 'x': 15.9, 'y': 12.45, 'type': 'diver', 'z': 0.55, 'facing': 90},
    {'x': 15.92, 'y': 12.4, 'type': 'bubbles', 'z': 1.15, 'scale': 0.8},
] + [{'x': x, 'y': y, 'type': 'reef_rock', 'scale': s_, 'flip': f}
     for x, y, s_, f in ((4.0, 8.0, 0.9, False), (11.0, 4.0, 0.8, True), (19.5, 3.6, 0.9, False), (28.0, 3.8, 0.8, True),
                         (33.0, 7.0, 0.9, True), (24.0, 10.6, 0.55, False), (12.4, 11.3, 0.5, True),
                         (5.0, 11.2, 0.6, False), (33.5, 11.0, 0.6, True))] + [
    {'x': 6.6, 'y': 10.6, 'type': 'sea_fan', 'scale': 0.7},
    {'x': 30.4, 'y': 10.0, 'type': 'sea_fan', 'scale': 0.8, 'flip': True},
    {'x': 16.2, 'y': 11.6, 'type': 'staghorn_coral', 'scale': 0.36},
    {'x': 21.2, 'y': 11.7, 'type': 'brain_coral', 'scale': 0.3},
    {'x': 29.6, 'y': 11.5, 'type': 'tube_sponge', 'scale': 0.38},
    {'x': 18.4, 'y': 12.2, 'type': 'brain_coral', 'scale': 0.2, 'flip': True},
]
hall = [
    {'id': 'child', 'x': 17.3, 'y': 13.6, 'type': 'child', 'facing': 270, 'tint': dark},
    {'id': 'parent', 'x': 18.1, 'y': 13.9, 'type': 'explorer', 'facing': 280, 'tint': dark},
    {'x': 23.2, 'y': 14.3, 'type': 'scientist', 'facing': 250, 'tint': dark},
    {'x': 15.0, 'y': 17.4, 'type': 'bench', 'stretch': 2.0},
    {'x': 23.0, 'y': 17.4, 'type': 'bench', 'stretch': 2.0},
    {'x': 10.9, 'y': 13.7, 'type': 'info_plaque'},
    {'x': 27.1, 'y': 13.7, 'type': 'info_plaque'},
    {'x': 4.6, 'y': 30.6, 'type': 'info_plaque'},
]
jellies = [
    {'x': 2.5, 'y': 24.6, 'type': 'sea_nettle', 'z': 0.14, 'scale': 0.74},
    {'x': 2.3, 'y': 25.5, 'type': 'sea_nettle', 'z': 0.1, 'scale': 0.6},
    {'x': 2.7, 'y': 25.15, 'type': 'sea_nettle', 'z': 0.42, 'scale': 0.44, 'flip': True},
    {'x': 2.5, 'y': 28.4, 'type': 'moon_jelly', 'z': 0.62, 'scale': 0.2},
    {'x': 2.4, 'y': 29.2, 'type': 'moon_jelly', 'z': 0.36, 'scale': 0.17},
    {'x': 2.6, 'y': 29.6, 'type': 'moon_jelly', 'z': 0.72, 'scale': 0.14},
    {'x': 2.5, 'y': 28.8, 'type': 'moon_jelly', 'z': 0.14, 'scale': 0.15},
    {'x': 2.55, 'y': 28.3, 'type': 'moon_jelly', 'z': 0.3, 'scale': 0.11},
    {'x': 12.5, 'y': 26.6, 'type': 'sea_nettle', 'z': 0.4, 'scale': 0.4, 'flip': True},
    {'x': 12.5, 'y': 27.4, 'type': 'sea_nettle', 'z': 0.25, 'scale': 0.32},
    {'id': 'gazer', 'x': 4.45, 'y': 24.55, 'type': 'child', 'facing': 180, 'tint': dark},
]
reef = [
    {'x': 6.3, 'y': 34.5, 'type': 'reef_rock', 'scale': 0.7},
    {'x': 4.4, 'y': 34.2, 'type': 'reef_rock', 'scale': 0.55, 'flip': True},
    {'x': 8.2, 'y': 34.3, 'type': 'reef_rock', 'scale': 0.6},
    {'x': 4.6, 'y': 33.4, 'type': 'tube_sponge', 'scale': 0.34},
    {'x': 6.0, 'y': 33.35, 'type': 'anemone', 'scale': 0.3},
    {'x': 7.5, 'y': 33.4, 'type': 'brain_coral', 'scale': 0.24},
    {'x': 5.2, 'y': 33.8, 'type': 'staghorn_coral', 'scale': 0.36},
    {'x': 7.9, 'y': 33.9, 'type': 'sea_fan', 'scale': 0.62, 'flip': True},
    {'x': 6.9, 'y': 33.45, 'type': 'angelfish', 'z': 0.46, 'scale': 0.16},
    {'x': 5.4, 'y': 33.6, 'type': 'blue_tang', 'z': 0.62, 'scale': 0.1, 'flip': True},
    {'x': 7.6, 'y': 33.8, 'type': 'blue_tang', 'z': 0.34, 'scale': 0.09},
    {'x': 6.2, 'y': 34.0, 'type': 'reef_shoal', 'z': 0.74, 'scale': 0.4},
    {'x': 7.1, 'y': 32.7, 'type': 'clownfish', 'z': 0.3, 'scale': 0.06},
]
tunnel = [
    {'x': 27.0, 'y': 25.5, 'type': 'reef_shark', 'z': 0.9, 'scale': 0.34},
    {'x': 32.6, 'y': 29.0, 'type': 'reef_shark', 'z': 1.3, 'scale': 0.3, 'flip': True},
    {'x': 32.8, 'y': 24.5, 'type': 'sea_turtle', 'z': 0.7, 'scale': 0.32, 'flip': True},
    {'x': 26.6, 'y': 30.5, 'type': 'manta_ray', 'z': 1.1, 'scale': 0.6},
    {'x': 29.9, 'y': 33.9, 'type': 'fish_school', 'z': 0.8, 'scale': 1.0},
    {'x': 26.5, 'y': 23.5, 'type': 'fish_school', 'z': 1.5, 'scale': 0.8, 'flip': True},
    {'x': 33.4, 'y': 32.6, 'type': 'reef_shoal', 'z': 0.4, 'scale': 0.5},
] + [{'x': x, 'y': y, 'type': 'reef_rock', 'scale': s_, 'flip': f}
     for x, y, s_, f in ((25.6, 24.0, 0.7, False), (26.0, 28.4, 0.6, True), (25.8, 32.6, 0.8, False),
                         (33.8, 23.0, 0.7, True), (34.0, 27.2, 0.8, False), (33.6, 31.0, 0.6, True))] + [
    {'x': 27.6, 'y': 27.0, 'type': 'sea_fan', 'scale': 0.6}, {'x': 32.6, 'y': 26.0, 'type': 'staghorn_coral', 'scale': 0.4},
]

s = scene(
    g,
    title='Aquarium - the ocean tank, the tunnel, the jellies and the reef',
    legend={
        '#': {'wall': 'concrete', 'h': 2.0},
        'R': {'wall': 'reef_wall', 'h': 2.0},
        'O': {'floor': 'seabed', 'ceil': surface},
        'o': {'floor': 'seabed', 'ceil': surface, 'glazed': True},
        'S': {'floor': 'seabed', 'ceil': surface},
        'r': {'floor': 'seabed', 'ceil': surface},
        'H': {'floor': 'marble_dark', 'ceil': 'concrete', 'reflect': 0.4},
        'J': {'floor': 'marble_dark', 'ceil': 'concrete', 'reflect': 0.25},
        'T': {'floor': 'marble_dark', 'ceil': 'tunnel_roof', 'reflect': 0.2},
        'b': {'wall': 'jelly_backdrop', 'h': 2.0},
        'B': {'floor': 'jelly_backdrop', 'ceil': 'jelly_backdrop'},
        'd': {'wall': violet, 'h': 2.0},
        'D': {'floor': violet, 'ceil': violet},
        'w': {'wall': ['tank_window', 'concrete'], 'h': 2.0},
        'v': {'wall': ['tank_window', 'concrete'], 'h': 2.0},
    },
    ceiling_height=2.0,
    sky='day',
    ambient=[0.06, 0.08, 0.11],
    fog={'color': [0.02, 0.1, 0.17], 'density': 0.03, 'glow': 0.5, 'shafts': 5.0},
    lights=(
        [{'type': 'sun', 'azimuth': 270, 'elevation': 62, 'intensity': 1.3}]
        + [{'x': x, 'y': y, 'z': 1.8, 'radius': 7.0, 'color': lamp, 'intensity': 1.2}
           for x, y in ((6, 5), (13, 5), (20, 5), (27, 5), (33, 5), (9, 9.5), (17, 9.5), (25, 9.5), (32, 9.5))]
        + [{'x': x, 'y': 3.6, 'z': 0.9, 'radius': 3.5, 'color': [0.45, 0.75, 1.0], 'intensity': 0.7}
           for x in (5, 12, 19, 26, 33)]
        + [{'x': x, 'y': y, 'z': 1.8, 'radius': 4.5, 'color': lamp, 'intensity': 1.1}
           for x, y in ((27, 24), (27, 29), (27, 33), (33, 24), (33, 29), (33, 33))]
        + [{'x': 2.5, 'y': y, 'z': 0.9, 'radius': 1.8, 'color': [1.0, 0.94, 0.84], 'intensity': 1.5} for y in (25, 29)]
        + [{'x': 12.5, 'y': 27.0, 'z': 0.9, 'radius': 1.8, 'color': [1.0, 0.94, 0.84], 'intensity': 1.5},
           {'x': 6.5, 'y': 33.8, 'z': 1.6, 'radius': 3.5, 'color': [0.85, 0.92, 1.0], 'intensity': 1.9},
           {'x': 5.0, 'y': 34.4, 'z': 1.2, 'radius': 2.5, 'color': [0.55, 0.4, 1.0], 'intensity': 0.9},
           {'x': 19.0, 'y': 19.5, 'z': 0.2, 'radius': 3.0, 'color': [1.0, 0.7, 0.4], 'intensity': 0.25},
           {'x': 7.0, 'y': 26.5, 'z': 0.2, 'radius': 3.0, 'color': [1.0, 0.7, 0.4], 'intensity': 0.2}]),
    sprites=panes + ocean + hall + jellies + reef + tunnel,
    camera={'x': 19.0, 'y': 20.3, 'look_at': [19.0, 8.0, 0.75], 'fov': 74, 'height': 0.45},
    shots=[
        {'x': 19.0, 'y': 17.6, 'look_at': [19.0, 8.0, 1.05], 'fov': 76, 'height': 0.45},
        {'x': 22.6, 'y': 13.5, 'look_at': [23.6, 8.8, 1.5], 'fov': 70, 'height': 0.3},
        {'x': 29.95, 'y': 21.4, 'look_at': [30.0, 33.0, 0.7], 'fov': 74},
        {'x': 5.3, 'y': 25.6, 'look_at': [2.5, 25.0, 0.5], 'fov': 66},
        {'x': 6.5, 'y': 31.2, 'look_at': [6.5, 33.8, 0.36], 'fov': 64, 'height': 0.36},
        {'x': 4.9, 'y': 29.0, 'look_at': [2.5, 29.0, 0.48], 'fov': 64, 'height': 0.45,
         'overrides': {'ambient': [0.02, 0.02, 0.04],
                       'lights': [{'x': 2.5, 'y': 29.0, 'z': 0.9, 'radius': 1.4, 'color': [0.55, 0.45, 1.0],
                                   'intensity': 0.7}]}},
        {'x': 15.2, 'y': 14.4, 'look_at': [15.9, 12.45, 0.95], 'fov': 60, 'height': 0.55,
         'post': [{'fx': 'dof', 'blur': 1.8}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)

HERE = os.path.dirname(os.path.abspath(__file__))
print(s.save(os.path.join(HERE, 'aquarium.json')))

"""Sewer tunnels: walkways along a sunken channel, railings, pipes and something in the water.

Shows reflections in sunken water, see-through railings, a sprite rising out of the water (a
sprite set below the surface is hidden where the water covers it), and wet-floor puddles.
Run:  python sewer_tunnels.py  -> writes sewer_tunnels.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(18, 40, fill='#')
g.rect(4, 2, 5, 37, 'w')                              # west walkway
g.rect(6, 2, 6, 37, 'r')                              # its railing
g.rect(7, 2, 11, 37, '~')                             # the channel
g.rect(12, 2, 12, 37, 'r')
g.rect(13, 2, 14, 37, 'w')                            # east walkway
g.rect(1, 18, 3, 20, 'w')                             # a side passage to a ladder (walled at x=0)
g.put(6, 19, 'w'); g.put(12, 19, 'w')                 # gaps in the railings at the junction
for y in (6, 13, 25, 31):
    g.put(3, y, 'P'); g.put(15, y + 2, 'P')           # pipe banks set into the walls

work = [1.0, 0.85, 0.45]
s = scene(
    g,
    title='Sewer tunnels - walkways along the channel',
    legend={
        '#': {'wall': 'slime_brick', 'h': 1.6},
        'P': {'wall': 'pipes', 'h': 1.6},
        'w': {'floor': 'concrete_floor', 'ceil': 'concrete'},
        'r': {'wall': 'railing', 'h': 1.0, 'floor': 'concrete_floor', 'ceil': 'concrete'},
        '~': {'floor': 'water', 'drop': 0.25, 'reflect': 0.55, 'ceil': 'concrete'},
    },
    ceiling_height=1.6,
    sky=None,
    ambient=[0.085, 0.095, 0.09],
    fog={'color': [0.03, 0.04, 0.035], 'density': 0.05},
    lights=[{'x': 14.2, 'y': y, 'z': 1.25, 'radius': 6.5, 'color': work, 'intensity': 1.6}
            for y in (33.0, 25.0, 17.0, 9.0)] + [
        {'x': 4.6, 'y': y, 'z': 1.25, 'radius': 6.0, 'color': work, 'intensity': 1.3}
        for y in (35.0, 27.0, 19.0, 11.0, 3.0)] + [
        {'x': 2.0, 'y': 19.5, 'z': 1.2, 'radius': 4.5, 'color': [1.0, 0.15, 0.1], 'intensity': 1.4},
        {'x': 10.2, 'y': 29.0, 'z': 0.2, 'radius': 2.4, 'color': [0.5, 1.0, 0.4], 'intensity': 0.9},
    ],
    sprites=[{'x': 14.2, 'y': y, 'type': 'ceiling_lamp', 'z': 1.28} for y in (33.0, 25.0, 17.0, 9.0)] + [
        {'x': 4.6, 'y': y, 'type': 'ceiling_lamp', 'z': 1.28} for y in (35.0, 27.0, 19.0, 11.0, 3.0)] + [
        {'x': 1.25, 'y': 19.5, 'type': 'ladder', 'scale': 1.55},
        {'x': 3.75, 'y': 10.0, 'type': 'pipe_valve', 'z': 0.5}, {'x': 14.25, 'y': 21.5, 'type': 'pipe_valve', 'z': 0.5},
        {'x': 4.6, 'y': 22.4, 'type': 'barrel'}, {'x': 13.6, 'y': 12.6, 'type': 'crate'},
        {'x': 14.4, 'y': 28.6, 'type': 'sack'}, {'x': 5.2, 'y': 14.0, 'type': 'bucket'},
        {'id': 'thing', 'x': 10.2, 'y': 29.0, 'type': 'hybrid', 'z': -0.22},
    ],
    decals=[
        {'tex': 'drain', 'surface': 'floor', 'x': 4.6, 'y': 33.0, 'size': 0.8},
        {'tex': 'drain', 'surface': 'floor', 'x': 13.6, 'y': 20.5, 'size': 0.8},
        {'tex': 'puddle_shine', 'surface': 'floor', 'x': 14.0, 'y': 31.0, 'size': 1.4},
        {'tex': 'puddle_shine', 'surface': 'floor', 'x': 4.8, 'y': 26.0, 'size': 1.2},
        {'tex': 'leak', 'surface': 'wall', 'cell': [3, 27], 'face': 'east', 'u': 0.5, 'z': 1.1, 'size': 0.8},
        {'tex': 'leak', 'surface': 'wall', 'cell': [15, 15], 'face': 'west', 'u': 0.5, 'z': 1.1, 'size': 0.8},
        {'tex': 'moss_patch', 'surface': 'wall', 'cell': [15, 30], 'face': 'west', 'u': 0.5, 'z': 0.3, 'size': 0.7},
    ],
    scatter=[{'of': 'wreckage', 'on': 'w', 'density': 0.12, 'sizes': ['tiny', 'small'], 'seed': 2}],
    grime=0.25,
    camera={'x': 4.8, 'y': 36.6, 'look_at': [9.0, 4.0, 0.35], 'fov': 72},
    shots=[
        {'x': 4.8, 'y': 36.6, 'look_at': [9.0, 4.0, 0.3], 'fov': 72,
         'overlays': [{'type': 'caption', 'text': 'Storm drain, level two', 'at': 'top', 'box': True}]},
        {'x': 5.6, 'y': 20.6, 'look_at': [1.25, 19.4, 0.6], 'fov': 70},
        {'x': 14.4, 'y': 32.0, 'height': 0.72, 'look_at': [10.2, 29.0, 0.1], 'fov': 50,
         'post': [{'fx': 'vignette', 'strength': 0.5}],   # leaning over the rail
         'overlays': [{'type': 'viewmodel', 'item': 'flashlight'}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sewer_tunnels.json')))

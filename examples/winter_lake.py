"""Winter lake: a frozen lake, a lit cabin, mountains and the moon.

Shows a moon with long cast shadows, a mountain skyline, reflective ice mirroring the cabin's
lit windows, and the same place by day through shot `overrides` (a low sun instead). The cabin
wears a roof under snow in 3D (a `gable_roof` of `"cover": "snow"`), wood smoke rising from its
chimney, and the boulders round the shore are 3D (`boulder` objects of `snow` rock).
Run:  python winter_lake.py  -> writes winter_lake.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.5}  # the lights glow

g = Grid(40, 40, fill='s')
g.disc(20, 19, 8, 'i')                                # the frozen lake
g.rect(15, 4, 24, 8, 'L')                             # the cabin
for x in (17, 22):
    g.put(x, 8, 'W')                                  # two lit windows facing the lake
g.put(19, 8, 'D'); g.put(20, 8, 'D')                  # the door
boulders = [{'type': 'boulder', 'x': x, 'y': y, 'size': s_, 'height': h, 'rock': 'snow', 'angle': a, 'seed': k}
            for k, (x, y, s_, h, a) in enumerate(((10.0, 10.6, 2.0, 1.2, 30), (31.2, 9.8, 2.4, 1.4, 200),
                                                  (8.6, 26.4, 1.6, 0.9, 120), (33.0, 25.6, 2.0, 1.1, 300),
                                                  (11.6, 11.8, 0.8, 0.45, 80), (29.6, 10.6, 0.9, 0.5, 250)))]
roof = [{'type': 'gable_roof', 'x': 20.0, 'y': 6.5, 'z': 1.5, 'angle': 0, 'length': 10.0, 'width': 5.0, 'rise': 1.5,
         'cover': 'snow', 'overhang': [0.35, 0.3], 'chimney': 0.25, 'seed': 2}]   # the cabin's roof, under snow

warm = [1.0, 0.68, 0.38]
night_lights = [
    {'type': 'moon', 'azimuth': 300, 'elevation': 16, 'intensity': 0.75},
    {'x': 17.5, 'y': 9.3, 'z': 0.6, 'radius': 4.5, 'color': warm, 'intensity': 1.3},
    {'x': 22.5, 'y': 9.3, 'z': 0.6, 'radius': 4.5, 'color': warm, 'intensity': 1.3},
    {'x': 19.4, 'y': 9.2, 'z': 0.8, 'radius': 3.5, 'color': warm, 'intensity': 1.0},
]
day_lights = [{'type': 'sun', 'azimuth': 215, 'elevation': 13, 'intensity': 0.9}] + night_lights[1:]
DAY = {'sky': 'day', 'ambient': [0.42, 0.44, 0.5], 'lights': day_lights,
       'fog': {'color': [0.75, 0.8, 0.88], 'density': 0.018, 'sky_mix': 0.25}}
pines = [(12, 5), (13.5, 3), (27, 4), (28.5, 6), (6, 15), (5, 19), (34, 15), (35.5, 19), (25.5, 2.5),
         (10.5, 2.5), (31, 30), (7, 31)]
s = scene(
    g,
    title='Winter lake - the frozen lake and the cabin',
    legend={
        's': {'floor': 'snow'},
        'i': {'floor': 'ice', 'drop': 0.05, 'reflect': 0.5},
        'L': {'wall': 'logs', 'h': 1.5, 'top': 'shingle'},
        'W': {'wall': [{'base': 'window_lit_plaster', 'tint': [0.75, 0.6, 0.45]}, 'logs'], 'h': 1.5, 'top': 'shingle'},
        'D': {'wall': ['door_wood', 'logs'], 'h': 1.5, 'top': 'shingle'},
    },
    sky='night',
    skyline='mountains',
    ambient=[0.12, 0.14, 0.2],
    fog={'color': [0.16, 0.18, 0.24], 'density': 0.022, 'sky_mix': 0.3},
    lights=night_lights,
    sprites=[{'x': x, 'y': y, 'type': 'snowy_pine', 'flip': i % 2 == 1} for i, (x, y) in enumerate(pines)] + [
        {'x': 19.4, 'y': 9.2, 'type': 'lantern', 'z': 0.7},
        {'x': 17.5, 'y': 6.5, 'type': 'steam', 'z': 3.3, 'scale': 1.6, 'opacity': 0.9,
         'tint': [0.55, 0.55, 0.6]},                                    # wood smoke from the chimney
        {'x': 26.0, 'y': 31.0, 'type': 'snowman'},
        {'id': 'child', 'x': 24.8, 'y': 31.4, 'type': 'child'},
        {'x': 14.0, 'y': 30.0, 'type': 'log'}, {'x': 25.5, 'y': 9.6, 'type': 'crate'},
    ],
    scatter=[{'of': 'snow', 'on': 's', 'density': 0.06, 'sizes': ['tiny', 'small', 'medium'], 'seed': 7}],
    objects=roof + boulders,
    camera={'x': 20.0, 'y': 32.0, 'look_at': [20.0, 7.0, 0.7], 'fov': 70},
    shots=[
        {'x': 20.0, 'y': 32.0, 'look_at': [20.0, 7.0, 0.75], 'fov': 70, 'post': [GLOW],
         'overlays': [{'type': 'caption', 'text': 'The cabin on the ice', 'at': 'top', 'box': True}]},
        {'x': 22.6, 'y': 35.2, 'look_at': 'child', 'fov': 58, 'post': [GLOW],
         'overlays': [{'type': 'bubble', 'anchor': 'child', 'text': "He's been watching the cabin all night."}]},
        {'x': 20.0, 'y': 30.0, 'look_at': [20.0, 7.0, 0.7], 'fov': 70, 'post': ['blizzard']},
        {'x': 20.0, 'y': 32.0, 'look_at': [20.0, 7.0, 0.75], 'fov': 70,
         'overrides': DAY},
        # the cabin close by day, from the ice: turned by angle and pitch (a look_at's sight line would
        # move the snow's scatter in the other shots)
        {'x': 18.6, 'y': 16.0, 'angle': 266.39, 'pitch': 0.218, 'fov': 60, 'overrides': DAY},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'winter_lake.json')))

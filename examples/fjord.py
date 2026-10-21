"""Fjord: a longship drawn up on the shingle at the head of a fjord, cliffs rising sheer on both sides,
another riding at anchor under furled sail; a longhouse of logs and thatch on the grass above the
beach, smoke from its roof - by day, and at dusk with a fire on the shingle.

Shows the `longship` object (a long open hull of boards, its stem and stern curling up, a mast and a
striped square sail, round shields along both sides), cliffs built in 3D (the fjord's walls lined with
`stone` rock walls), a longhouse roofed in thatch in 3D (`gable_roof`), the `round_shield` prop on the
longhouse wall, `deep_water` mirroring the cliffs, and the `mountains` skyline under snow.
Run:  python fjord.py  -> writes fjord.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

FIRE = [1.0, 0.6, 0.3]


def fjord():
    g = Grid(34, 44, fill='C')                     # the cliffs
    g.rect(11, 0, 22, 24, 'w')                     # the fjord, running out north between them
    g.rect(9, 18, 10, 24, 'w'); g.rect(23, 15, 24, 24, 'w')   # its shore not quite straight
    g.rect(8, 25, 25, 28, 'g')                     # the shingle at its head
    g.rect(4, 29, 29, 43, 'm')                     # the grass above the beach
    g.rect(6, 33, 13, 36, 'L')                     # the longhouse
    g.put(9, 36, 'D'); g.put(10, 36, 'D')          # its doors, looking out to the fjord
    objects = [
        # the cliffs in 3D, in grey stone, and the longships: one drawn up on the shingle, one at anchor
        {'type': 'rock_wall', 'x': 0, 'y': 0, 'lining': 'C', 'rock': 'stone', 'depth': 1.2, 'height': [4.6, 7.6],
         'trim': 0.14, 'pieces': [1.6, 3.4], 'seed': 3},
        {'type': 'longship', 'x': 16.6, 'y': 25.0, 'angle': 272, 'length': 7.0, 'heel': 5, 'seed': 2},
        {'type': 'longship', 'x': 19.0, 'y': 12.0, 'z': -0.32, 'angle': 250, 'length': 6.4, 'sail': False, 'seed': 6},
        {'type': 'gable_roof', 'x': 10.0, 'y': 35.0, 'z': 1.3, 'angle': 0, 'length': 8.0, 'width': 4.0, 'rise': 1.7,
         'cover': 'thatch', 'overhang': [0.35, 0.3], 'seed': 4},
    ]
    sprites = [
        # the beach: the fire, barrels and a chest by the ship, logs, a seafarer and a farmer
        {'x': 13.2, 'y': 27.4, 'type': 'campfire'},
        {'x': 18.6, 'y': 27.0, 'type': 'barrel'}, {'x': 19.2, 'y': 27.5, 'type': 'barrel', 'flip': True},
        {'x': 14.6, 'y': 25.6, 'type': 'chest'}, {'x': 11.8, 'y': 28.2, 'type': 'log'},
        {'id': 'seafarer', 'x': 15.8, 'y': 26.3, 'type': 'pirate', 'facing': 290},
        {'x': 20.5, 'y': 30.5, 'type': 'farmer', 'facing': 250},
        # the longhouse: shields on its wall, smoke from its roof, goats on the grass
        {'x': 7.6, 'y': 37.05, 'type': 'round_shield', 'z': 0.55, 'angle': 0},
        {'x': 11.6, 'y': 37.05, 'type': 'round_shield', 'z': 0.55, 'angle': 0, 'flip': True},
        {'x': 10.0, 'y': 35.0, 'type': 'steam', 'z': 2.9, 'scale': 1.6, 'opacity': 0.8, 'tint': [0.55, 0.55, 0.6]},
        {'x': 16.0, 'y': 34.0, 'type': 'goat'}, {'x': 17.4, 'y': 35.6, 'type': 'goat', 'flip': True},
        # trees along the grass, gulls over the water
        {'x': 5.0, 'y': 30.4, 'type': 'pine', 'scale': 3.0}, {'x': 27.6, 'y': 31.0, 'type': 'pine', 'scale': 3.4},
        {'x': 26.0, 'y': 38.0, 'type': 'birch'}, {'x': 4.8, 'y': 40.0, 'type': 'pine'},
        {'x': 15.0, 'y': 16.0, 'type': 'seagull', 'z': 2.6}, {'x': 18.0, 'y': 20.0, 'type': 'seagull', 'z': 3.2, 'flip': True},
    ]
    day_sun = {'type': 'sun', 'azimuth': 285, 'elevation': 16, 'color': [1.0, 0.92, 0.78], 'intensity': 1.0}
    fire = {'x': 13.2, 'y': 27.4, 'z': 0.5, 'radius': 4.5, 'color': FIRE, 'intensity': 1.4}
    return scene(
        g,
        legend={
            'C': {'wall': 'rock', 'h': 4.4, 'top': 'grass'},
            'w': {'floor': 'deep_water', 'drop': 0.2, 'reflect': 0.55},
            'g': {'floor': 'gravel'},
            'm': {'floor': 'grass'},
            'L': {'wall': 'logs', 'h': 1.3, 'top': 'logs'},
            'D': {'wall': ['door_wood', 'logs'], 'h': 1.3, 'top': 'logs'},
        },
        title='Fjord - a longship on the shingle',
        sky='day',
        skyline={'type': 'mountains', 'color': [0.62, 0.66, 0.74], 'height': 1.4},
        ambient=[0.36, 0.38, 0.44],
        fog={'color': [0.7, 0.76, 0.84], 'density': 0.014, 'sky_mix': 0.3},
        lights=[day_sun],
        sprites=sprites,
        objects=objects,
        scatter=[{'of': ['rocks', 'rocks', 'grass_tuft'], 'on': 'g', 'density': 0.12, 'sizes': ['tiny', 'small'], 'seed': 5},
                 {'of': ['grass_tuft', 'grass_tuft', 'flowers', 'rocks'], 'on': 'm', 'density': 0.1,
                  'sizes': ['tiny', 'small'], 'seed': 6}],
        camera={'x': 11.6, 'y': 32.4, 'look_at': [17.0, 19.0, 1.6], 'fov': 70},
        shots=[
            {'x': 11.6, 'y': 32.4, 'look_at': [17.0, 19.0, 1.6], 'fov': 70,
             'overlays': [{'type': 'caption', 'text': 'The head of the fjord', 'at': 'top', 'box': True}]},
            {'x': 9.6, 'y': 27.6, 'look_at': [17.0, 25.0, 1.4], 'fov': 66, 'extra_sprites': [],
             'overrides': {'sky': 'sunset',
                           'ambient': [0.24, 0.2, 0.26],
                           'lights': [dict(day_sun, elevation=4, intensity=0.6, color=[1.0, 0.6, 0.4]), fire,
                                      {'x': 9.5, 'y': 37.4, 'z': 0.7, 'radius': 3.0, 'color': FIRE, 'intensity': 1.0}],
                           'fog': {'color': [0.42, 0.3, 0.36], 'density': 0.016, 'glow': 0.8}},
             'post': [{'fx': 'bloom', 'threshold': 0.6, 'strength': 0.5, 'radius': 5}]},
            {'x': 17.0, 'y': 17.0, 'look_at': [12.0, 30.0, 1.2], 'fov': 68},       # from the water, back at the beach
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(fjord().save(os.path.join(HERE, 'fjord.json')))

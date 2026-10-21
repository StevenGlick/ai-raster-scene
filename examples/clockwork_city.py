"""The clockwork city: a plaza of brass and copper at sundown in a brown smog - a clock tower with a
great clock on its face, gears the height of houses turning in the walls, pipes weeping green and
venting steam, gaslamps, an automaton on its rounds, and in the middle of it all an orrery: brass rings
turning round a golden sun, the planets riding them.

Shows the clockwork kit (scripts/clockwork.py): `brass_plate` and `copper_pipes` walls, a `clock_face`
storey on the little tower, a `great_clock` card on the tower, `gear` objects in 3D - brass wheels with teeth,
spokes and a boss, gone green in patches - standing out from the walls; the orrery is
wireframes - `torus` rings tilted round a `sphere`, all in brass - on a `cylinder` plinth. With `steam`
from the pipes and the chimneys, `lamp_post`s, and the `robot` tinted brass for an automaton.
Run:  python clockwork_city.py  -> writes clockwork_city.json
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 36, 40
g = Grid(W, H, fill='B')                              # the city: blocks of brick and brass...
g.rect(9, 12, 26, 29, '.')                            # ...round a plaza
g.rect(17, 30, 18, 39, '.')                           # a street running south
g.rect(9, 11, 16, 11, 'D')                            # taller houses along the north side
g.rect(19, 11, 26, 11, 'E')
g.rect(27, 12, 27, 29, 'D')                           # and the east
g.rect(17, 9, 18, 11, 'C')                            # the clock tower, its face on the plaza
g.rect(27, 11, 27, 11, 'K')                           # a little clock tower on the corner
for y in range(13, 29, 3):                            # pipe runs down the west side
    g.rect(8, y, 8, y, 'P')
for x in (11, 14, 21, 24):                            # and along the south
    g.rect(x, 30, x, 30, 'P')
g.rect(27, 21, 27, 22, 'P')                           # and a run on the east, under the gears

BRASS = [1.0, 0.78, 0.38]
BRASS_TOP = {'base': 'brass_plate', 'tint': [0.8, 0.8, 0.8]}
legend = {
    '.': {'floor': 'cobble'},
    'B': {'wall': ['brick_dark', 'brick_dark', 'brass_plate'], 'h': 3.0, 'top': BRASS_TOP},
    'D': {'wall': ['brick_dark', 'brick_dark', 'brick_dark', 'brass_plate'], 'h': 4.4, 'top': BRASS_TOP},
    'E': {'wall': ['brick_dark', 'brick_dark', 'brass_plate'], 'h': 3.6, 'top': BRASS_TOP},
    'P': {'wall': ['copper_pipes', 'copper_pipes', 'brass_plate'], 'h': 3.0, 'top': BRASS_TOP},
    'C': {'wall': ['brick_dark'] * 3 + ['brass_plate'] * 5, 'h': 8.0, 'top': BRASS_TOP},
    'K': {'wall': ['brick_dark'] * 4 + ['clock_face', 'brass_plate'], 'h': 6.0, 'top': BRASS_TOP},
}
# the orrery: brass rings round a golden sun, planets riding them, on a plinth
OX, OY = 18.0, 21.5
wireframes = [{'mesh': 'cylinder', 'x': OX, 'y': OY, 'size': 0.9, 'sides': 12, 'solid': True,
               'fill': [0.16, 0.1, 0.05], 'color': BRASS, 'intensity': 0.7},
              {'id': 'orrery', 'mesh': 'sphere', 'x': OX, 'y': OY, 'z': 1.75, 'size': 0.55, 'segments': 10,
               'rings': 6, 'solid': True, 'fill': [0.55, 0.36, 0.1], 'color': [1.0, 0.9, 0.55], 'intensity': 1.1}]
for tilt, ang, size in ((90, 0, 2.8), (90, 60, 2.8), (90, 120, 2.8), (18, 30, 3.4), (66, 10, 2.0)):
    wireframes.append({'mesh': 'torus', 'x': OX, 'y': OY, 'z': 2.0 - size / 2, 'size': size, 'thickness': 0.016,
                       'segments': 36, 'sides': 3, 'tilt': tilt, 'angle': ang, 'color': BRASS, 'intensity': 0.6})
for a, r, z, s, c in ((30, 1.65, 2.25, 0.22, BRASS), (150, 1.4, 1.55, 0.17, [0.55, 0.85, 1.0]),
                      (250, 1.0, 2.5, 0.14, [1.0, 0.55, 0.4]), (320, 1.7, 1.85, 0.12, BRASS)):
    wireframes.append({'mesh': 'sphere', 'x': OX + r * math.cos(math.radians(a)), 'y': OY + r * math.sin(math.radians(a)),
                       'z': z, 'size': s, 'segments': 6, 'rings': 4, 'solid': True, 'fill': [0.2, 0.14, 0.06],
                       'color': c, 'intensity': 0.8})
wireframes.append({'mesh': 'cone', 'x': 18.0, 'y': 10.5, 'z': 8.0, 'size': 2.1, 'scale': [1, 1.4, 1.3], 'sides': 4,
                   'angle': 45, 'solid': True, 'fill': [0.2, 0.13, 0.07], 'color': BRASS, 'intensity': 0.5})  # the tower's spire
sprites = [
    # the great clock on the tower
    {'id': 'clock', 'x': 18.0, 'y': 12.04, 'type': 'great_clock', 'angle': 0, 'scale': 1.7, 'z': 4.5},
    # steam from the pipes and the chimneys
    {'x': 9.6, 'y': 16.5, 'type': 'steam'}, {'x': 9.6, 'y': 25.5, 'type': 'steam', 'flip': True},
    {'x': 26.4, 'y': 21.6, 'type': 'steam'},
    {'x': 14.5, 'y': 9.5, 'type': 'steam', 'z': 4.4, 'scale': 1.6}, {'x': 23.0, 'y': 9.5, 'type': 'steam', 'z': 3.6, 'scale': 1.4},
    {'x': 29.5, 'y': 22.0, 'type': 'steam', 'z': 4.4, 'scale': 1.6}, {'x': 6.5, 'y': 18.0, 'type': 'steam', 'z': 3.0, 'scale': 1.4},
    # gaslamps round the plaza; the automaton, townsfolk
    {'id': 'automaton', 'x': 24.2, 'y': 21.0, 'type': 'robot', 'tint': [1.0, 0.8, 0.45], 'facing': 200},
    {'x': 12.4, 'y': 18.0, 'type': 'scientist', 'facing': 0}, {'x': 23.0, 'y': 15.5, 'type': 'shopkeeper', 'facing': 120},
    {'x': 10.0, 'y': 28.0, 'type': 'barrel'}, {'x': 10.7, 'y': 28.4, 'type': 'crate'}, {'x': 25.8, 'y': 28.3, 'type': 'barrel'},
    {'x': 10.2, 'y': 13.4, 'type': 'pipe_valve'},
]
# gears in the walls, in 3D: on the north side facing south, on the east facing west - (along, z, size, teeth)
gears = [{'type': 'gear', 'x': x, 'y': 12.0 + sz * 0.05 + 0.03, 'z': z, 'angle': 90, 'size': sz, 'teeth': t, 'seed': k}
         for k, (x, z, sz, t) in enumerate(((12.6, 0.9, 2.6, 28), (15.0, 0.3, 1.5, 16), (22.5, 1.2, 2.0, 22)))]
gears += [{'type': 'gear', 'x': 27.0 - sz * 0.05 - 0.03, 'y': y, 'z': z, 'angle': 180, 'size': sz, 'teeth': t, 'seed': 5 + k}
          for k, (y, z, sz, t) in enumerate(((17.0, 0.7, 3.0, 32), (19.6, 0.15, 1.7, 18), (25.5, 1.6, 2.2, 24)))]
gears.append({'type': 'gear', 'x': 18.0, 'y': 12.11, 'z': 2.75, 'angle': 90, 'size': 1.55, 'teeth': 20, 'spokes': 4,
              'seed': 9})                     # and one on the clock tower, under its face
lamps = [(10.5, 14.0), (25.5, 14.0), (10.5, 27.0), (25.5, 27.0), (16.0, 13.0), (20.0, 13.0)]
sprites += [{'x': x, 'y': y, 'type': 'lamp_post'} for x, y in lamps]
lights = [{'x': x, 'y': y, 'z': 1.5, 'radius': 5.0, 'color': [1.0, 0.72, 0.42], 'intensity': 1.2} for x, y in lamps]
lights += [{'x': OX, 'y': OY, 'z': 1.8, 'radius': 3.5, 'color': [1.0, 0.8, 0.45], 'intensity': 0.7},
           {'type': 'sun', 'azimuth': 120, 'elevation': 12, 'intensity': 0.6, 'color': [1.0, 0.66, 0.38]}]
GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.5, 'spread': 0.5}
s = scene(
    g,
    title='The clockwork city - brass and steam at sundown',
    legend=legend,
    sky='sunset',
    ambient=[0.3, 0.25, 0.21],
    lights=lights,
    fog={'color': [0.42, 0.3, 0.2], 'density': 0.022},
    sprites=sprites,
    wireframes=wireframes,
    objects=gears,
    camera={'x': 18.0, 'y': 30.0, 'look_at': [18.0, 12.0, 3.0], 'fov': 70},
    shots=[
        {'x': 18.0, 'y': 29.4, 'height': 0.5, 'look_at': [18.0, 12.0, 3.6], 'fov': 72, 'post': [GLOW],
         'overlays': [{'type': 'caption', 'text': 'The clockwork city', 'at': 'top', 'box': True}]},
        {'x': 22.2, 'y': 26.6, 'height': 0.6, 'look_at': [18.0, 21.5, 1.8], 'fov': 62,
         'post': [{'fx': 'dof', 'focus': 'orrery', 'blur': 1.6}, GLOW]},
        {'x': 22.4, 'y': 24.8, 'height': 0.5, 'look_at': [26.94, 18.0, 2.0], 'fov': 66, 'post': [GLOW]},
        {'x': 11.0, 'y': 26.0, 'height': 0.5, 'look_at': [16.7, 17.8, 3.2], 'fov': 68, 'post': [GLOW]},
    ],
    contact_shadows=0.45,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clockwork_city.json')))

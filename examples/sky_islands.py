"""Sky islands: meadows adrift high over a sea of cloud. A temple stands on the highest island, a
stream running off its edge into a waterfall that turns to mist long before it reaches the clouds;
roots trail from the islands' undersides, a plank bridge with rope rails crosses to an islet of
trees, rocks float loose in the air and gulls wheel between them.

Shows the sky-island kit (scripts/skyisles.py): `meadow` tops and `island_rock` sides with a deep
`cliff` (how far each island's rock drops into the void below it), a raised island (a block of rock
with a meadow `top`), a bridge of `planks` with a thin `cliff` and `rope_rail` cards along it, the
`waterfall` hung off an edge with `z` at minus its height, `island_roots` under the edges; under
every island its rock in 3D (`keel` objects, hung at the foot of each `cliff`); the temple a ring of
fluted Doric columns of `marble` in 3D, some fallen, an entablature (`beam`s) over the runs that stand,
round a `statue`; trees, `floating_rock`s and `seagull`s.
Run:  python sky_islands.py  -> writes sky_islands.json
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 60, 64
g = Grid(W, H, fill=' ')                              # nothing but sky in every direction
g.disc(30, 48, 7.5, 'a')                              # home: the meadow we stand on
g.disc(30, 22, 6.2, 'T')                              # the temple island, raised high on its rock
for y in range(25, 29):                               # its stream, running south to the edge
    g.put(30, y, 'S')
g.disc(13, 48, 3.6, 'c')                              # an islet of trees across the bridge
for x in range(17, 23):
    g.put(x, 48, '=')                                 # the bridge
g.disc(48, 30, 3.0, 'd')                              # a small high islet, east
g.disc(10, 12, 4.5, 'f')                              # far islands
g.disc(52, 8, 5.5, 'f')
g.disc(46, 54, 2.6, 'c')

ROCK = {'side': 'island_rock'}
legend = {
    ' ': {'floor': 'void'},
    'a': dict(ROCK, floor='meadow', cliff=2.6),
    'c': dict(ROCK, floor='meadow', cliff=2.0),
    'f': dict(ROCK, floor='meadow', cliff=2.4),
    'T': dict(ROCK, wall='island_rock', h=1.4, top='meadow', cliff=3.0),
    'S': dict(ROCK, wall='island_rock', h=1.4, top='shallows', cliff=3.0),
    'd': dict(ROCK, wall='island_rock', h=1.2, top='meadow', cliff=2.0),
    '=': {'floor': 'planks', 'side': 'planks', 'cliff': 0.12},
}

sprites, objects = [], []
STANDING = (True, True, True, True, True, False, True, False)     # the temple's columns, some fallen
ring = [(30.5 + 2.6 * math.cos(math.radians(k * 45 + 22.5)), 22.5 + 2.6 * math.sin(math.radians(k * 45 + 22.5)))
        for k in range(8)]
for k, ((x, y), up) in enumerate(zip(ring, STANDING)):          # the temple: a ring of columns round a statue
    objects.append({'type': 'column', 'x': x, 'y': y, 'z': 1.4, 'material': 'marble', 'flutes': 16, 'top': 0.8,
                    'radius': 0.17, 'height': 1.6 if up else 0.7 + 0.3 * k % 2, 'doric': up, 'capital': 0.2,
                    'broken': 0 if up else 0.2, 'seed': 60 + k})
    (x1, y1), up1 = ring[(k + 1) % 8], STANDING[(k + 1) % 8]
    if up and up1:                                    # the entablature over the pairs that stand
        mx, my, a = (x + x1) / 2, (y + y1) / 2, math.degrees(math.atan2(y1 - y, x1 - x))
        for z, w, d in ((3.0, 0.32, 0.2), (3.2, 0.42, 0.08)):
            objects.append({'type': 'beam', 'x': mx, 'y': my, 'z': z, 'angle': a, 'length': math.hypot(x1 - x, y1 - y) + 0.3,
                            'width': w, 'depth': d, 'material': 'marble', 'seed': 70 + k})
sprites.append({'id': 'statue', 'x': 30.5, 'y': 22.5, 'type': 'statue', 'z': 1.4, 'scale': 1.4})
# the waterfall pours off the temple island's south edge, from its lip down past the rock
sprites.append({'id': 'falls', 'x': 30.5, 'y': 29.04, 'type': 'waterfall', 'angle': 0, 'length': 1.1,
                'z': -10.6, 'scale': 12.0})
# under every island its rock in 3D, from the foot of its cliff to a ragged point
for k, (cx, cy, r, cliff) in enumerate(((30.5, 48.5, 7.5, 2.6), (30.5, 22.5, 6.2, 3.0), (13.5, 48.5, 3.6, 2.0),
                                        (48.5, 30.5, 3.0, 2.0), (10.5, 12.5, 4.5, 2.4), (52.5, 8.5, 5.5, 2.4),
                                        (46.5, 54.5, 2.6, 2.4))):
    objects.append({'type': 'keel', 'x': cx, 'y': cy, 'z': -cliff + 0.02, 'size': 2 * r + 0.6, 'depth': 1.5 * r,
                    'roots': False, 'seed': 80 + k})
# roots trailing from the undersides
for (cx, cy, r, zb) in ((30.5, 22.5, 6.2, -3.0), (30.5, 48.5, 7.5, -2.6), (13.5, 48.5, 3.6, -2.0)):
    for k in range(10):
        a = math.radians(k * 36 + 10)
        x, y = cx + (r - 0.3) * math.cos(a), cy + (r - 0.3) * math.sin(a)
        sprites.append({'x': x, 'y': y, 'type': 'island_roots', 'angle': math.degrees(a) + 90, 'length': 2.2,
                        'z': zb - 1.6, 'scale': 2.2})
# the bridge's rails
for y in (47.96, 49.04):
    sprites.append({'x': 20.0, 'y': y, 'type': 'rope_rail', 'angle': 0, 'length': 6.0})
# trees on the islets, flowers on the meadow, rocks and gulls in the air
sprites += [{'x': 12.4, 'y': 47.2, 'type': 'tree'}, {'x': 14.8, 'y': 49.6, 'type': 'birch'},
            {'x': 11.8, 'y': 50.2, 'type': 'tree', 'flip': True}, {'x': 46.6, 'y': 54.2, 'type': 'pine'},
            {'x': 48.4, 'y': 30.4, 'type': 'tree', 'z': 1.2}, {'x': 10.5, 'y': 12.0, 'type': 'tree'},
            {'x': 52.2, 'y': 8.6, 'type': 'pine'}, {'x': 50.8, 'y': 7.2, 'type': 'pine'}]
sprites += [{'x': 25.0 + k * 2.6, 'y': 51.0 + (k % 3) * 1.1, 'type': 'flowers'} for k in range(5)]
sprites += [{'x': x, 'y': y, 'type': 'floating_rock', 'z': z, 'scale': s} for x, y, z, s in
            ((22.0, 34.0, 1.8, 0.8), (39.5, 37.0, 3.2, 1.1), (19.0, 26.0, 4.0, 0.7), (41.0, 18.0, 1.0, 1.4),
             (36.5, 41.0, -1.2, 0.6))]
sprites += [{'x': x, 'y': y, 'type': 'seagull', 'z': z} for x, y, z in
            ((27.0, 33.0, 2.6), (34.5, 30.0, 3.4), (24.0, 28.0, 3.9))]
sprites.append({'id': 'explorer', 'x': 28.4, 'y': 41.6, 'type': 'explorer', 'facing': 270})

SUN = {'type': 'sun', 'azimuth': 250, 'elevation': 28, 'intensity': 0.9}
s = scene(
    g,
    title='Sky islands - meadows adrift over the clouds',
    legend=legend,
    sky='day',
    ambient=[0.42, 0.44, 0.5],
    lights=[SUN],
    fog={'color': [0.74, 0.82, 0.92], 'density': 0.012},
    sprites=sprites,
    objects=objects,
    camera={'x': 30.6, 'y': 45.0, 'look_at': [30.5, 24.0, 2.0], 'fov': 70},
    shots=[
        {'x': 30.9, 'y': 43.4, 'height': 0.62, 'look_at': [30.5, 24.0, 0.2], 'fov': 72,
         'overlays': [{'type': 'caption', 'text': 'The sky islands', 'at': 'top', 'box': True}]},
        {'x': 23.0, 'y': 48.5, 'look_at': [13.0, 48.5, 0.6], 'fov': 72},
        {'x': 27.6, 'y': 25.4, 'height': 1.9, 'look_at': [13.0, 48.0, 0.0], 'fov': 72},
        {'x': 13.0, 'y': 46.0, 'look_at': [30.5, 30.0, 1.0], 'fov': 72,
         'overrides': {'sky': 'golden', 'ambient': [0.4, 0.36, 0.38],
                       'lights': [dict(SUN, azimuth=300, elevation=9, color=[1.0, 0.78, 0.55])],
                       'fog': {'color': [0.94, 0.78, 0.62], 'density': 0.012}}},
        {'x': 26.2, 'y': 41.4, 'height': 0.6, 'look_at': [30.5, 29.0, -2.6], 'fov': 66},
    ],
    contact_shadows=0.4,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sky_islands.json')))

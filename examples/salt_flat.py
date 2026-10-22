"""The salt flat: a dry lake bed of salt after rain, the crust under a film of still water that
mirrors the whole sky out to the horizon, so ground and sky become one - with islands of dry crust
cracked into white-rimmed plates, salt raked up into rows of mounds and heaps, a house built of salt
blocks, and a few things that have no business being there: a door standing on its own, an armchair,
a clock.

Shows the salt flat kit (scripts/saltflat.py): `salt_water` (the crust under water) with `reflect`
0.9 and `"reflections": {"ripple": 0, "smear": 0}` - a still mirror instead of a rippled one -
`salt_flat` (the dry crust: pale plates with raised rims) in islands, `salt_brick` for the house, and
rows of `salt_mound`s with a `salt_heap` or a `salt_pile` among them and `salt_clods` lying about, no
two the same size; the sky doubled at sunset, at noon, at night and in a dream, with the `sky_whale`; and in
one shot the door is a `portal` onto a wood in winter in another scene (winter_woods.json).
Run:  python salt_flat.py  -> writes salt_flat.json
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 64, 64
g = Grid(W, H, fill='w')
# islands of dry crust in the water: a few rounded patches, wobbling at the edge
for cx, cy, r in ((44.0, 30.0, 6.5), (20.0, 18.0, 4.0), (12.0, 44.0, 5.0), (52.0, 52.0, 3.5), (30.0, 8.0, 3.0)):
    for y in range(int(cy - r - 2), int(cy + r + 3)):
        for x in range(int(cx - r - 2), int(cx + r + 3)):
            a = math.atan2(y + 0.5 - cy, x + 0.5 - cx)
            if 0 <= x < W and 0 <= y < H and math.hypot(x + 0.5 - cx, y + 0.5 - cy) < r * (1 + 0.18 * math.sin(3 * a + cx)):
                g.put(x, y, 'd')
g.rect(46, 26, 48, 27, 'B')                          # the salt house on the big island, a door on its south side
g.put(47, 27, 'D')

SUNSET = {'type': 'sun', 'azimuth': 270, 'elevation': 7, 'intensity': 0.9, 'color': [1.0, 0.72, 0.5],
          'disc_color': [1.0, 0.85, 0.6]}
rnd = random.Random(4)
SIZE = {'salt_mound': 0.22, 'salt_heap': 0.15, 'salt_pile': 0.12, 'salt_clods': 0.08}
salt, heaps = [], []
for j in range(4):                                   # rows of salt raked up to dry, no two alike: heaps in 3D
    x, y = 39.2 + 0.5 * (j % 2), 31.4 + 1.15 * j
    while x < 49.0:
        kind = rnd.choices(['salt_mound', 'salt_heap', 'salt_pile'], [7, 1, 1])[0]
        if g.get(int(x), int(y)) == 'd':
            h = SIZE[kind] * rnd.uniform(0.8, 1.15) * 1.15
            heaps.append({'type': 'heap', 'x': round(x + rnd.uniform(-0.12, 0.12), 2),
                          'y': round(y + rnd.uniform(-0.12, 0.12), 2), 'height': round(h, 3),
                          'size': round(h * 1.75, 3), 'fill': 0.8, 'seed': len(heaps)})
            rnd.random()                             # (as the cards' flip did, so the rest stays as it was)
        x += rnd.uniform(0.9, 1.2)
for _ in range(8):                                   # and clods lying about between them
    x, y = rnd.uniform(39.0, 48.5), rnd.uniform(30.8, 35.6)
    if g.get(int(x), int(y)) == 'd':
        salt.append({'x': round(x, 2), 'y': round(y, 2), 'type': 'salt_clods', 'flip': rnd.random() < 0.5})
sprites = salt + [
    {'id': 'walker', 'x': 31.4, 'y': 43.2, 'type': 'dreamer'},
    {'id': 'door', 'x': 26.5, 'y': 30.0, 'type': 'door_frame'},
    {'x': 22.0, 'y': 26.5, 'type': 'armchair', 'flip': True},
    {'x': 29.5, 'y': 24.0, 'type': 'grandfather_clock'},
]
# the door, in one shot, opening onto a wood in winter in another scene: a portal, the view through it taken from
# where the camera would stand on the far side (here on a path through the wood); an override, so the other
# shots keep their door standing open on nothing
PORTAL = {'type': 'portal', 'x': 26.5, 'y': 30.0, 'angle': 90, 'width': 0.44, 'height': 0.98, 'frame': 'wood',
          'paint': '#ece4d4', 'door': '#4a6a8a', 'swing': 140, 'fill': 1.0,
          'scene': 'winter_woods.json', 'to': {'x': 17.15, 'y': 35.6, 'angle': 270, 'z': 0.08}}
s = scene(
    g,
    title='The salt flat - the sky on the ground',
    legend={
        'w': {'floor': 'salt_water', 'reflect': 0.9},
        'd': {'floor': 'salt_flat', 'reflect': 0.0},
        'B': {'wall': 'salt_brick', 'h': 0.9, 'top': 'salt_flat'},
        'D': {'wall': ['door_wood'], 'h': 0.9, 'top': 'salt_flat'},
    },
    sky='sunset',
    skyline={'type': 'mountains', 'height': 0.7},
    ambient=[0.42, 0.36, 0.4],
    lights=[SUNSET],
    fog={'color': [0.86, 0.6, 0.58], 'density': 0.005},
    reflections={'ripple': 0, 'smear': 0},
    sprites=sprites,
    objects=heaps,
    camera={'x': 32.4, 'y': 48.0, 'look_at': [30.0, 20.0, 0.6], 'fov': 70},
    shots=[
        {'x': 32.4, 'y': 47.0, 'height': 0.32, 'look_at': [30.0, 20.0, 0.7], 'fov': 70,
         'overlays': [{'type': 'caption', 'text': 'The salt flat', 'at': 'top', 'box': True}]},
        {'x': 27.0, 'y': 35.0, 'height': 0.3, 'look_at': [26.5, 30.0], 'fov': 60},   # the door, by where it stands
        {'x': 40.5, 'y': 36.6, 'height': 0.28, 'look_at': [44.0, 31.0, 0.12], 'fov': 66,
         'overrides': {'sky': 'day', 'ambient': [0.34, 0.35, 0.4],
                       'lights': [{'type': 'sun', 'azimuth': 120, 'elevation': 55, 'intensity': 0.6}],
                       'fog': {'color': [0.78, 0.84, 0.92], 'density': 0.004}}},
        {'x': 32.6, 'y': 46.0, 'height': 0.3, 'look_at': [31.0, 30.0, 0.9], 'fov': 70,
         'overrides': {'sky': 'night', 'ambient': [0.1, 0.11, 0.16],
                       'lights': [{'type': 'moon', 'azimuth': 260, 'elevation': 14, 'intensity': 0.45}],
                       'fog': {'color': [0.05, 0.06, 0.1], 'density': 0.004}}},
        {'x': 24.0, 'y': 44.0, 'height': 0.35, 'look_at': [30.0, 28.0, 2.6], 'fov': 72,
         'extra_sprites': [{'x': 31.0, 'y': 26.0, 'type': 'sky_whale', 'z': 3.0, 'scale': 2.6}],
         'overrides': {'sky': 'dream', 'ambient': [0.55, 0.5, 0.58], 'lights': [dict(SUNSET, elevation=12)],
                       'fog': {'color': [0.96, 0.8, 0.84], 'density': 0.005}}},
        {'x': 26.95, 'y': 32.4, 'height': 0.42, 'look_at': [26.5, 30.0, 0.52], 'fov': 62,
         'overrides': {'sprites': [sp for sp in sprites if sp.get('id') != 'door'], 'objects': heaps + [PORTAL]}},
    ],
    contact_shadows=0.3,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'salt_flat.json')))

"""The salt flat: a dry lake bed of salt after rain, the crust under a film of still water that
mirrors the whole sky out to the horizon, so ground and sky become one - with islands of dry crust
cracked into white-rimmed plates, salt raked into mounds, a house built of salt blocks, and a few
things that have no business being there: a door standing on its own, an armchair, a clock.

Shows the salt flat kit (scripts/saltflat.py): `salt_water` (the crust under water) with `reflect`
0.9 and `"reflections": {"ripple": 0, "smear": 0}` - a still mirror instead of a rippled one -
`salt_flat` (the dry crust: pale plates with raised rims) in islands, `salt_brick` for the house, and
`salt_mound`s; the sky doubled at sunset, at noon, at night and in a dream, with the `sky_whale`.
Run:  python salt_flat.py  -> writes salt_flat.json
"""
import math
import os
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
mounds = [{'x': 40.0 + 1.3 * k + (0.4 if j % 2 else 0), 'y': 32.0 + 1.4 * j, 'type': 'salt_mound',
           'flip': (k + j) % 2 == 1} for j in range(3) for k in range(6)]
sprites = mounds + [
    {'id': 'walker', 'x': 31.4, 'y': 43.2, 'type': 'dreamer'},
    {'id': 'door', 'x': 26.5, 'y': 30.0, 'type': 'door_frame'},
    {'x': 22.0, 'y': 26.5, 'type': 'armchair', 'flip': True},
    {'x': 29.5, 'y': 24.0, 'type': 'grandfather_clock'},
]
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
    camera={'x': 32.4, 'y': 48.0, 'look_at': [30.0, 20.0, 0.6], 'fov': 70},
    shots=[
        {'x': 32.4, 'y': 47.0, 'height': 0.32, 'look_at': [30.0, 20.0, 0.7], 'fov': 70,
         'overlays': [{'type': 'caption', 'text': 'The salt flat', 'at': 'top', 'box': True}]},
        {'x': 27.0, 'y': 35.0, 'height': 0.3, 'look_at': 'door', 'fov': 60},
        {'x': 37.0, 'y': 36.5, 'height': 0.5, 'look_at': [45.0, 31.0, 0.3], 'fov': 66,
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
    ],
    contact_shadows=0.3,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'salt_flat.json')))

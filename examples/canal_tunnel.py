"""The canal tunnel: a brick vault over a canal, a boat moored in it - one of the three concept drawings this
project began from, made into a scene.

A tunnel three wide, a canal sunk down its middle (`water`, `drop`) between two walkways, its vault made of
`vault_arch` cards set across it every 1.3 so each frames the next, running away into the dark. Round
`wall_lamp`s light it in pairs; an `iron_cabinet` stands against one wall under the first and a `sigil` is
painted on the other; two pipes (`beam`s) run along the vault. A boat (a small `ship_hull`) is moored to a post
by a rope (`cable`), a `lantern` on a pole at its bow. The second shot is from the boat itself.
Run:  python canal_tunnel.py  -> writes canal_tunnel.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 5, 30
VAULT = [0.66, 0.63, 0.82]                 # the walls' stone, tinted to the vault's grey-violet
DROP = 0.18
WARM = [1.0, 0.7, 0.4]
BOAT = (2.45, 25.9)                        # the boat's middle; it lies a little across the canal, bow ahead
BOW = (BOAT[0] + 0.17, BOAT[1] - 0.47)       # 0.5 along it, toward the bow
GLOW = [{'fx': 'grade', 'exposure': 1.12, 'gamma': 0.9, 'tint': [0.88, 0.94, 1.14], 'lift': [0.008, 0.008, 0.02]},
        {'fx': 'bloom', 'source': 'light', 'strength': 1.1, 'radius': 2.0, 'spread': 0.5}]


def canal_tunnel():
    g = Grid(W, H, fill='B')
    g.rect(1, 1, 1, H - 2, 'w')
    g.rect(2, 1, 2, H - 2, 'c')
    g.rect(3, 1, 3, H - 2, 'w')
    arches = [{'x': 2.5, 'y': round(y, 2), 'type': 'vault_arch', 'angle': 0, 'z': DROP}
              for y in [27.0 - 1.3 * k for k in range(20)] if y > 1.2]
    lamps, lights = [], []
    for y in (24.6, 19.4, 14.2, 9.0, 3.8):
        for x, lx in ((1.07, 1.45), (3.93, 3.55)):
            lamps.append({'x': x, 'y': y, 'type': 'wall_lamp', 'z': 0.86, 'scale': 0.34})
            lights.append({'x': lx, 'y': y, 'z': 0.95, 'radius': 1.9, 'color': WARM, 'intensity': 0.7})
    sprites = arches + lamps + [
        {'x': 1.2, 'y': 24.3, 'type': 'iron_cabinet'},
        {'x': BOW[0], 'y': BOW[1] + 0.06, 'type': 'lantern', 'z': 0.4, 'scale': 0.2},
    ]
    lights.append({'x': BOW[0], 'y': BOW[1] + 0.06, 'z': 0.36, 'radius': 1.5, 'color': WARM, 'intensity': 0.85})
    objects = [
        {'type': 'ship_hull', 'x': BOAT[0], 'y': BOAT[1], 'z': -0.04, 'angle': 290, 'scale': 0.3,
         'length': 4.0, 'width': 1.3, 'depth': 0.55, 'seed': 3},          # a punt, a little over a metre long
        {'type': 'column', 'x': BOW[0], 'y': BOW[1] + 0.08, 'radius': 0.016, 'height': 0.4, 'sides': 6,
         'material': 'wood'},                                              # the lantern's pole
        {'type': 'column', 'x': 1.62, 'y': 26.6, 'radius': 0.04, 'height': 0.28, 'material': 'wood'},  # a post
        {'type': 'cable', 'x': 1.62, 'y': 26.6, 'z': 0.26, 'to': [2.32, 26.25, -0.06], 'sag': 0.06, 'width': 0.012,
         'color': '#5a4632'},                                              # the mooring rope
        {'type': 'beam', 'x': 3.72, 'y': 14.5, 'z': 1.2, 'angle': 90, 'length': 28.0, 'width': 0.07, 'depth': 0.07,
         'material': 'iron_green'},                                     # two pipes along the vault
        {'type': 'beam', 'x': 3.84, 'y': 14.5, 'z': 1.06, 'angle': 90, 'length': 28.0, 'width': 0.06, 'depth': 0.06,
         'material': 'iron_green'},
    ]
    decals = [{'tex': 'sigil', 'surface': 'wall', 'cell': [4, 25], 'face': 'west', 'u': 0.45, 'z': 0.3, 'size': 0.6},
              {'tex': 'stain', 'surface': 'wall', 'cell': [0, 20], 'face': 'east', 'u': 0.5, 'z': 0.3, 'size': 1.2,
               'opacity': 0.6},
              {'tex': 'leak', 'surface': 'wall', 'cell': [4, 17], 'face': 'west', 'u': 0.5, 'z': 1.0, 'size': 0.8}]
    return scene(
        g,
        title='The canal tunnel - a brick vault over a canal, a boat moored in it',
        legend={
            'B': {'wall': {'base': 'castle', 'tint': VAULT}, 'h': 1.6},
            'w': {'floor': {'base': 'flagstone', 'tint': [0.55, 0.55, 0.62]},
                  'ceil': {'base': 'castle', 'tint': VAULT}},
            'c': {'floor': 'water', 'drop': DROP, 'reflect': 0.45, 'ceil': {'base': 'castle', 'tint': VAULT}},
        },
        ceiling_height=1.6,
        sky=None,
        ambient=[0.15, 0.155, 0.22],
        lights=lights,
        fog={'color': [0.0, 0.0, 0.0], 'density': 0.11, 'glow': 0.5},
        sprites=sprites,
        objects=objects,
        decals=decals,
        camera={'x': 2.5, 'y': 28.6, 'angle': 270, 'fov': 62, 'height': 0.62},
        shots=[
            {'x': 2.5, 'y': 28.6, 'angle': 270, 'fov': 62, 'height': 0.62, 'pitch': -0.07, 'post': GLOW},
            {'x': 2.3, 'y': 26.3, 'angle': 272, 'fov': 64, 'height': 0.2, 'pitch': -0.04, 'post': GLOW},  # in the boat
            {'x': 3.4, 'y': 27.8, 'look_at': [2.45, 25.6, 0.05], 'fov': 58, 'height': 0.4, 'post': GLOW},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(canal_tunnel().save(os.path.join(HERE, 'canal_tunnel.json')))

"""Sunken temple: a temple of marble on the floor of the sea - fluted columns still standing on their
platform, others fallen in drums across the sand, coral growing over the stones, kelp swaying round it,
a manta ray gliding over and the sun coming down through the water in beams; a diver at the great
fallen head.

Shows the ruins' columns in 3D under water (`column` objects of `marble` with `flutes` and `"doric": true`,
`beam` architraves across the pairs that stand, others `broken`), the reef's corals and fish on the stones,
`kelp` and the `kelp` fringe, `boulder`s of `reef` rock, and water made of the air as in the kelp forest:
a dense teal fog with `shafts`, a high sun, a teal `grade`.
Run:  python sunken_temple.py  -> writes sunken_temple.json next to this file.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402


def sunken_temple():
    g = Grid(34, 40, fill='K')                     # the reef all round, kelp in front of it
    g.disc(17, 20, 14, 's')
    g.rect(6, 8, 28, 36, 's')
    g.rect(11, 10, 22, 21, 'B')                    # the temple's platform
    MARBLE = {'material': 'marble', 'flutes': 16, 'top': 0.8, 'fill': 0.6}
    STANDING = {(11.5, 10.5), (13.7, 10.5), (15.9, 10.5), (18.1, 10.5), (20.3, 10.5), (22.5, 10.5),
                (11.5, 12.7), (11.5, 14.9), (22.5, 12.7), (11.5, 19.3), (22.5, 19.3), (20.3, 21.5)}
    objects = []
    ring = [(11.5 + 2.2 * i, 10.5) for i in range(6)] + [(22.5, 10.5 + 2.2 * i) for i in range(1, 6)] + \
           [(22.5 - 2.2 * i, 21.5) for i in range(1, 6)] + [(11.5, 21.5 - 2.2 * i) for i in range(1, 5)]
    for k, (x, y) in enumerate(ring):              # the peristyle: most fallen, a run still standing at the back
        up = (round(x, 1), round(y, 1)) in STANDING
        objects.append(dict(MARBLE, type='column', x=x, y=y, z=0.3, radius=0.26, height=2.6 if up else 0.6 + 0.5 * (k % 3),
                            doric=up, capital=0.3, broken=0 if up else 0.25, seed=k))
    for x0 in (11.5, 13.7, 15.9, 18.1, 20.3):      # the architrave over the run that stands
        objects.append({'type': 'beam', 'x': x0 + 1.1, 'y': 10.5, 'z': 2.9, 'angle': 0, 'length': 2.6, 'width': 0.5,
                        'depth': 0.34, 'material': 'marble', 'fill': 0.6, 'seed': int(x0 * 10)})
    objects += [{'type': 'beam', 'x': 16.8, 'y': 24.8, 'z': 0.0, 'angle': 24, 'length': 2.4, 'width': 0.5, 'depth': 0.34,
                 'material': 'marble', 'fill': 0.6, 'seed': 90},          # a fallen block of it in the sand
                *[{'type': 'boulder', 'x': x, 'y': y, 'size': s_, 'height': h, 'rock': 'reef', 'angle': a, 'plants': 4,
                   'seed': 50 + k} for k, (x, y, s_, h, a) in enumerate(((7.4, 14.0, 2.2, 1.2, 30), (27.0, 13.0, 2.6, 1.0, 120),
                                                                         (8.0, 30.0, 2.0, 0.9, 220), (26.6, 31.0, 2.4, 1.1, 300)))]]
    rng = np.random.default_rng(5)
    kelp = []
    for _ in range(46):                            # kelp all round, but not on the temple or the way in
        x, y = rng.uniform(6, 28), rng.uniform(8, 36)
        if 10 < x < 24 and 9 < y < 23 or abs(x - 17) < 2.6 and y > 23:
            continue
        if g.get(int(x), int(y)) != 's':
            continue
        kelp.append({'x': round(x, 2), 'y': round(y, 2), 'type': 'kelp', 'scale': round(rng.uniform(4.0, 5.6), 2),
                     'flip': bool(rng.random() < 0.5)})
    sprites = kelp + [
        # coral grown over the stones, drums in the sand, the great head
        *[{'x': x, 'y': y, 'type': t, 'z': z, 'flip': k % 2 == 1} for k, (x, y, t, z) in enumerate((
            (12.4, 11.2, 'staghorn_coral', 0.3), (14.6, 11.4, 'brain_coral', 0.3), (19.4, 11.3, 'sea_fan', 0.3),
            (21.6, 13.6, 'anemone', 0.3), (12.2, 16.0, 'tube_sponge', 0.3), (21.4, 18.4, 'staghorn_coral', 0.3),
            (16.6, 15.0, 'reef_rock', 0.3), (14.0, 19.6, 'sea_fan', 0.3), (19.8, 20.4, 'brain_coral', 0.3)))],
        *[{'x': x, 'y': y, 'type': 'column_drum', 'flip': k % 2 == 1} for k, (x, y) in enumerate(
            ((9.4, 18.0), (10.0, 24.0), (24.0, 16.4), (23.6, 24.6), (14.4, 25.6)))],
        {'id': 'head', 'x': 19.6, 'y': 26.4, 'type': 'marble_head', 'tint': [0.82, 0.92, 0.9]},
        {'x': 18.6, 'y': 26.9, 'type': 'staghorn_coral'}, {'x': 20.6, 'y': 27.0, 'type': 'anemone'},
        # life: the manta overhead, shoals, a turtle, the diver and his bubbles
        {'x': 16.0, 'y': 18.0, 'type': 'manta_ray', 'z': 3.6, 'scale': 1.6},
        {'x': 13.0, 'y': 14.0, 'type': 'reef_shoal', 'z': 1.6}, {'x': 21.0, 'y': 16.0, 'type': 'fish_school', 'z': 2.2, 'flip': True},
        {'x': 9.0, 'y': 26.0, 'type': 'fish_school', 'z': 2.8}, {'x': 24.0, 'y': 28.0, 'type': 'sea_turtle', 'z': 1.4, 'scale': 0.5},
        {'id': 'diver', 'x': 18.4, 'y': 28.2, 'type': 'diver', 'facing': 45},
        {'x': 18.45, 'y': 28.15, 'type': 'bubbles', 'z': 0.62, 'scale': 1.6},
    ]
    return scene(
        g,
        legend={
            'K': {'wall': 'rock_wet', 'h': 0.8, 'top': 'seabed', 'fringe': {'set': 'kelp', 'depth': 1.2, 'wander': 0.3}},
            's': {'floor': 'seabed'},
            'B': {'wall': {'base': 'ruin_paving', 'tint': [0.78, 0.88, 0.84]}, 'h': 0.3, 'top': {'base': 'ruin_paving', 'tint': [0.78, 0.88, 0.84]}},
        },
        title='Sunken temple - marble on the floor of the sea',
        sky='day',
        ambient=[0.1, 0.22, 0.24],
        fog={'color': [0.0, 0.16, 0.2], 'density': 0.045, 'shafts': 1.4, 'anisotropy': 0.35},
        lights=[{'type': 'sun', 'azimuth': 100, 'elevation': 66, 'intensity': 1.2}],
        post=[{'fx': 'grade', 'tint': [0.74, 0.98, 1.05], 'saturation': 1.1}, {'fx': 'vignette', 'strength': 0.4}],
        sprites=sprites,
        objects=objects,
        scatter=[{'of': 'seabed', 'on': 's', 'density': 0.12, 'sizes': {'tiny': 3, 'small': 2}, 'seed': 4}],
        camera={'x': 16.2, 'y': 30.2, 'look_at': [17.0, 13.0, 1.8], 'fov': 66},
        shots=[
            {'x': 16.2, 'y': 30.2, 'height': 0.8, 'look_at': [17.0, 13.0, 1.8], 'fov': 66,
             'overlays': [{'type': 'caption', 'text': 'The temple under the sea', 'at': 'top', 'box': True}]},
            {'x': 14.8, 'y': 17.0, 'height': 0.7, 'look_at': [16.0, 10.5, 3.2], 'fov': 70},
            {'x': 15.6, 'y': 29.6, 'height': 0.8, 'look_at': 'head', 'fov': 60},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(sunken_temple().save(os.path.join(HERE, 'sunken_temple.json')))

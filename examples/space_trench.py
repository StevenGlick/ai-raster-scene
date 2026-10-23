"""The space trench: a road scene (road.py) - flying a starfighter low down a trench cut through the hull of a
great ship, its walls of panels and lit strips rushing past, a ringed planet overhead.

The trench floor is the road (plates of hull, `hangar_floor` beyond); its walls are `walls` cut into `blocks` of
different hull plating - lit strips, panels, conduits - each block its own height, with a lower tier of boxes and
gaps along the rims; the sky is `space` with a ringed planet in it. Red and blue lamps along the walls, red bolts
of fire flying back at you (`orb`s, tinted red, `additive`), drones ahead, a blast on the wall. You fly the
`starfighter`, a little off the floor.
Run:  python space_trench.py  -> writes space_trench.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

NEON = [{'fx': 'bloom', 'source': 'light', 'strength': 1.8, 'radius': 2.4, 'spread': 0.5}]
RED, BLUE = [1.0, 0.25, 0.2], [0.35, 0.6, 1.0]
BOLT = {'blend': 'additive', 'tint': [1.0, 0.25, 0.2], 'fullbright': True}


def space_trench():
    road = {
        'sections': [[20, 0, 0], [60, 0.15, 0], [60, -0.2, 0], [300, 0.1, 0]],
        'width': 3.4, 'surface': 'hull_dark', 'lines': False, 'rumble': False, 'bands': 0.05,
        'ground': 'hangar_floor',
        'walls': [
            {'side': 'both', 'offset': 0.6, 'height': 6, 'ragged': 1.2,
             'texture': ['hull_lit', 'tech_panel', 'conduit', 'hull', 'hull_red'], 'tile': 1.5, 'blocks': 3.0,
             'seed': 1},
            {'side': 'both', 'offset': 1.0, 'z': 6, 'height': 1.6, 'ragged': 0.8, 'texture': ['hull', 'tech_panel'],
             'tile': 1.5, 'blocks': 2.0, 'gaps': 0.5, 'seed': 2},
        ],
        'distance': 260,
    }
    lights = [{'at': a, 'x': (-1 if k % 2 else 1) * 2.1, 'z': 1.0, 'radius': 3.2, 'color': RED if k % 2 else BLUE,
               'intensity': 1.1} for k, a in enumerate(range(4, 200, 7))]
    sprites = [
        dict(BOLT, type='orb', at=6, x=-0.5, z=1.2, scale=0.16),          # bolts of fire coming back at you
        dict(BOLT, type='orb', at=7.5, x=-0.45, z=1.25, scale=0.12),
        dict(BOLT, type='orb', at=11, x=0.6, z=1.6, scale=0.16),
        dict(BOLT, type='orb', at=12.5, x=0.55, z=1.62, scale=0.12),
        dict(BOLT, type='orb', at=16, x=0.1, z=0.9, scale=0.16),
        {'type': 'drone', 'at': 18, 'x': -0.6, 'z': 1.6, 'scale': 1.6},
        {'type': 'drone', 'at': 24, 'x': 0.8, 'z': 2.2, 'scale': 1.6},
        {'type': 'fireball', 'at': 14, 'x': 2.2, 'z': 2.5, 'scale': 1.6},
    ]
    return road_scene(
        road,
        title='The space trench - a starfighter low down a trench in the hull of a great ship',
        sky='space',
        sky_objects=[{'type': 'ringed', 'azimuth': 268, 'elevation': 9, 'size': 9, 'color': [0.8, 0.62, 0.5]}],
        ambient=[0.32, 0.32, 0.4],
        lights=lights,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.9, 'fov': 66, 'pitch': 0.06},
        shots=[{'at': 2.0, 'x': 0.0, 'height': 0.9, 'fov': 66, 'pitch': 0.06, 'roll': 6, 'post': NEON,
                'vehicle': {'type': 'starfighter', 'ahead': 2.2, 'z': 0.35, 'scale': 0.4}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(space_trench().save(os.path.join(HERE, 'space_trench.json')))

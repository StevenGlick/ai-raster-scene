"""Night drive: a road scene (road.py) in the city-pop look - the red convertible on an elevated expressway into the
city on a summer night, towers rising on both sides out of the city's lights below, their windows lit one by one,
sodium lamps along the road, tail lights ahead, a big moon over a violet sky.

Shows the road's buildings in 3D and lit window by window: `walls` cut into `blocks` with a `depth` and a `setback`,
standing from far below the road (`z`) - boxes whose near ends and, below the eye, roofs show - their heights whole
`storeys`; two facades, `tower_glass` (four windows across and four storeys to a tile) and `office_bands` (two across,
four up), each with its lit twin in the walls' `windows`: each tower its own share of windows lit, each window its
own tint and brightness. The expressway in the air (`ground` `void` past a strip of concrete, the city at night far
`below`), `jersey_barrier` walls, `highway_lamp`s, the `vector` sky with a moon, `citypop_dusk` and a light bloom.
Run:  python night_drive.py  -> writes night_drive.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LANE = 4.4 / 4
# the windows' tints: mostly warm rooms and cool offices, now and then a neon one
TINTS = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 0.86, 0.62], [1.0, 0.78, 0.5], [0.78, 0.88, 1.1], [0.72, 0.82, 1.12],
         [1.0, 0.62, 0.86], [0.62, 1.05, 1.1]]
LOOK = ['citypop_dusk', {'fx': 'bloom', 'source': 'light', 'strength': 0.75, 'radius': 2.0, 'spread': 0.4}]


def towers(offset, height, ragged, blocks, seed, share, z=-24.0):
    return {'side': 'both', 'offset': offset, 'z': z, 'height': height, 'ragged': ragged, 'blocks': blocks,
            'gaps': 0.45, 'setback': 5.0, 'depth': 6.0, 'storeys': True, 'seed': seed, 'tile': [2.0, 2.0],
            'texture': ['tower_glass', 'office_bands', 'tower_glass'],
            'roof': {'base': 'concrete', 'tint': [0.5, 0.48, 0.6]},
            'windows': {'lit': ['tower_glass_lit', 'office_bands_lit', 'tower_glass_lit'], 'share': share,
                        'spread': 0.25, 'cells': [[4, 4], [2, 4], [4, 4]], 'dim': 0.35, 'colors': TINTS}}


def night_drive():
    road = {
        'sections': [[16, 0, 0], [60, 0.35, 0.6], [50, -0.45, -0.4], [80, 0.25, 0.3], [300, -0.1, 0.0]],
        'width': 4.4, 'lanes': 4, 'surface': 'blacktop', 'lines': '#f2f0ea', 'edges': '#ffc93a', 'rumble': False,
        'ground': {'left': [{'width': 0.3, 'texture': 'concrete'}, {'texture': 'void'}],
                   'right': [{'width': 0.3, 'texture': 'concrete'}, {'texture': 'void'}]},
        'below': {'depth': 24, 'tile': 14, 'haze': 0.3, 'texture': 'city_night'},
        'walls': [
            {'side': 'both', 'offset': 0.0, 'height': 0.28, 'texture': 'jersey_barrier', 'tile': [1.3, 0.28]},
            towers(11.0, 30.0, 12.0, 6.0, 2, 0.3),
            towers(32.0, 52.0, 20.0, 9.0, 5, 0.24),
        ],
        'bands': 0.03, 'distance': 400,
    }
    roadside = [{'type': 'highway_lamp', 'every': 9, 'offset': 0.15, 'side': 'both', 'from': 4}]
    lights = [{'at': a, 'x': (-1 if k % 2 else 1) * 2.6, 'z': 2.2, 'radius': 4.0, 'color': [1.0, 0.82, 0.55],
               'intensity': 1.0} for k, a in enumerate(range(4, 160, 9))]
    sprites = [
        {'type': 'car_compact', 'at': 14, 'x': -LANE * 0.5, 'variant': 1},
        {'type': 'car_sedan', 'at': 26, 'x': -LANE * 1.5, 'variant': 3},
        {'type': 'car_compact', 'at': 44, 'x': -LANE * 0.5, 'variant': 0},
        {'type': 'car_oncoming', 'at': 34, 'x': LANE * 1.5},
    ]
    return road_scene(
        road,
        title='Night drive - the convertible into the city at night, in the city-pop look',
        sky='vector',
        sky_objects=[{'type': 'moon', 'azimuth': 266, 'elevation': 24, 'size': 5.0, 'phase': 0.0}],
        ambient=[0.42, 0.36, 0.56],
        lights=lights,
        fog={'color': [0.3, 0.2, 0.42], 'density': 0.0045},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': -LANE * 0.5, 'height': 0.75, 'fov': 64, 'pitch': 0.08},
        shots=[
            {'at': 2.0, 'x': -LANE * 0.5, 'height': 0.75, 'fov': 64, 'pitch': 0.08, 'post': LOOK,
             'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}},
            # at the barrier, looking out over the towers and the city below
            {'at': 40.0, 'x': 1.9, 'height': 0.6, 'fov': 70, 'pitch': 0.02, 'yaw': 38, 'post': LOOK},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(night_drive().save(os.path.join(HERE, 'night_drive.json')))

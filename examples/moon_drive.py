"""The moon drive: a road scene (road.py) on the Moon - following a moon buggy across the grey dust toward the
base, the Earth hanging in the black sky, the sun low and the shadows long.

There is no road but the tracks: the `regolith` itself, its ruts laid as `rover_tracks` decals down it; the same
dust either side, `crater` decals stamped across it at every size, boulders scattered and standing. The base waits
ahead - a greenhouse `dome` lit from inside, habitat modules, solar arrays, a lander on its legs - and an astronaut
walks out to meet the buggy. The `space` sky, the Earth over the horizon; no air, so no fog and no haze.
Run:  python moon_drive.py  -> writes moon_drive.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.0, 'radius': 2.0}]


def moon_drive():
    road = {
        'sections': [[10, 0, 0], [30, 0.2, 0.8], [30, -0.25, -1.0], [40, 0.1, 0.6], [300, 0, 0.2]],
        'width': 1.6, 'surface': 'regolith', 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.3, 'blend': 0.8},
        'ground': 'regolith',
        'distance': 300,
    }
    roadside = [
        {'type': 'boulder', 'density': 0.12, 'offset': [0.6, 20.0], 'scale': [0.3, 1.4], 'tint': [0.85, 0.85, 0.88],
         'seed': 1},
    ]
    scatter = [{'of': 'rocks', 'density': 0.5, 'offset': [0.0, 6.0], 'tint': [0.85, 0.85, 0.88], 'seed': 2}]
    decals = [
        {'tex': 'rover_tracks', 'density': 0.5, 'size': [1.2, 1.4], 'side': 'road', 'seed': 1},
        {'tex': 'crater', 'density': 0.08, 'side': 'both', 'offset': [0.3, 10.0], 'size': [2.0, 6.0], 'seed': 2},
        {'tex': 'crater', 'at': 7, 'x': -3.0, 'size': 5.0},
    ]
    sprites = [
        {'type': 'dome', 'at': 46, 'x': -3.0, 'scale': 3.2,
         'light': {'color': [0.7, 1.0, 0.7], 'radius': 4.0, 'intensity': 0.8, 'z': 1.0}},
        {'type': 'hab_module', 'at': 49, 'x': 1.5, 'scale': 1.6},
        {'type': 'hab_module', 'at': 52, 'x': 4.0, 'scale': 1.6, 'flip': True},
        {'type': 'solar_array', 'at': 44, 'x': 7.0, 'scale': 1.8},
        {'type': 'solar_array', 'at': 47, 'x': 9.5, 'scale': 1.8},
        {'type': 'lander', 'at': 40, 'x': -8.0, 'scale': 2.4},
        {'type': 'astronaut', 'at': 11, 'x': 1.3, 'view': 'front'},
    ]
    return road_scene(
        road,
        title='The moon drive - following a moon buggy across the dust toward the base, the Earth in the black sky',
        sky='space',
        sky_objects=[{'type': 'earth', 'azimuth': 280, 'elevation': 14, 'size': 4.0}],
        lights=[{'type': 'sun', 'azimuth': 200, 'elevation': 12, 'intensity': 1.2, 'color': [1.0, 1.0, 0.98]}],
        ambient=[0.32, 0.32, 0.36],
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 62, 'pitch': 0.06},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 62, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'moon_buggy', 'ahead': 3.0, 'z': 0.0}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(moon_drive().save(os.path.join(HERE, 'moon_drive.json')))

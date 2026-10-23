"""The ice road: a road scene (road.py) - driving a ploughed track across a frozen lake at night under the aurora,
the black ice mirroring it.

The road is ice with snow over it (`snow` tinted grey-blue, little reflection); along its edges the plough's banks,
low `walls` of `snow`; either side the lake's ice, polished by the wind (`ice_floor`, mirror-like: the aurora and
the stars lie in it), drifts of snow across it (`sand_drift` decals tinted white). Marker poles stand along the
track, a truck's tail lights far ahead, the far shore a line of mountains; your jeep's headlights on the snow.
Run:  python ice_road.py  -> writes ice_road.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.4, 'spread': 0.5}]
SNOWDRIFT = [1.2, 1.3, 1.5]


def ice_road():
    road = {
        'sections': [[20, 0, 0], [80, 0.12, 0], [80, -0.15, 0], [400, 0.08, 0]],
        'width': 2.6, 'surface': {'base': 'snow', 'tint': [0.82, 0.88, 1.0]}, 'lines': False, 'rumble': False,
        'wet': 0.08, 'ripple': 0.2,
        'ground': {'base': 'ice_floor'},
        'walls': [{'side': 'both', 'offset': 0.05, 'height': 0.28, 'texture': 'snow', 'tile': 1.0, 'ragged': 0.1,
                   'seed': 1}],
        'bands': 0.02, 'distance': 400,
    }
    roadside = [{'type': 'reflector_post', 'every': 7, 'offset': 0.45, 'from': 3, 'scale': 0.45}]
    decals = [{'tex': 'sand_drift', 'side': 'both', 'density': 0.05, 'offset': [0.6, 14], 'size': [1.0, 2.4],
               'tint': SNOWDRIFT, 'seed': 1},
              {'tex': 'sand_drift', 'density': 0.06, 'size': [0.8, 1.4], 'tint': SNOWDRIFT, 'seed': 2}]
    sprites = [{'type': 'box_truck', 'at': 24, 'x': -0.55, 'tint': [0.6, 0.62, 0.7]}]
    return road_scene(
        road,
        title='The ice road - across a frozen lake at night under the aurora, the black ice mirroring it',
        sky='aurora',
        skyline='mountains',
        ambient=[0.2, 0.26, 0.36],
        lights=[{'type': 'moon', 'azimuth': 300, 'elevation': 25, 'intensity': 0.3, 'disc': False}],
        fog={'color': [0.1, 0.16, 0.22], 'density': 0.006, 'sky_mix': 0.1},
        roadside=roadside,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.95, 'fov': 66, 'pitch': 0.06},
        shots=[{'at': 2.0, 'x': 0.0, 'height': 0.95, 'fov': 66, 'pitch': 0.06, 'post': LOOK,
                'vehicle': {'type': 'jeep', 'ahead': 2.9, 'headlights': True, 'beam': 1.2}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(ice_road().save(os.path.join(HERE, 'ice_road.json')))

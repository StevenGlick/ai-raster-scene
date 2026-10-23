"""The lost valley: a road scene (road.py) in a valley the world forgot - following a jungle track by jeep in the
golden afternoon, long-necked dinosaurs crossing the track ahead in the haze, a tyrannosaur roaring out of the ferns
beside it, a volcano smoking beyond, great winged shapes over it.

A `dirt` track with ragged edges through `jungle_floor`; tree ferns, palms and ferns thick along it; `sauropod`s
crossing far ahead (`scale` 9 to 11), the `tyrannosaur` at the jungle's edge near the track, facing it; the
`erupting_volcano` far off, scaled down; dark winged shapes (`crow` tinted, scaled up) high over the valley. Your jeep
from behind.
Run:  python lost_valley.py  -> writes lost_valley.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.2}]


def lost_valley():
    road = {
        'sections': [[20, 0, 0], [40, 0.25, 0.3], [40, -0.2, -0.1], [300, 0.05, 0]],
        'width': 1.6, 'surface': 'dirt', 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.3, 'blend': 0.8},
        'ground': [{'width': 0.4, 'texture': 'mud'}, {'texture': 'jungle_floor'}],
        'distance': 300,
    }
    roadside = [
        {'type': ['tree_fern', 'palm', 'tree_fern', 'palm_lean'], 'density': 0.5, 'offset': [0.9, 10.0],
         'scale': [1.6, 3.2], 'from': 3, 'seed': 1},
        {'type': ['fern', 'fern', 'bush'], 'density': 1.4, 'offset': [0.2, 4.0], 'scale': [0.4, 0.9], 'seed': 2},
    ]
    sprites = [
        {'type': 'sauropod', 'at': 52, 'x': -7.0, 'scale': 10},
        {'type': 'sauropod', 'at': 60, 'x': 4.0, 'scale': 11, 'flip': True},
        {'type': 'sauropod', 'at': 74, 'x': 13.0, 'scale': 9},
        {'type': 'tyrannosaur', 'at': 13, 'x': -2.6, 'scale': 4.2, 'flip': True},
        {'type': 'erupting_volcano', 'at': 220, 'x': -26, 'z': -3, 'scale': 40},
        {'type': 'crow', 'at': 40, 'x': -4, 'z': 9, 'scale': 1.2, 'tint': [0.7, 0.5, 0.4]},
        {'type': 'crow', 'at': 46, 'x': 2, 'z': 11, 'scale': 1.0, 'tint': [0.7, 0.5, 0.4], 'flip': True},
    ]
    return road_scene(
        road,
        title='The lost valley - a jungle track by jeep, long-necked dinosaurs crossing ahead, a tyrannosaur roaring',
        sky='golden',
        skyline={'type': 'mountains', 'height': 1.2, 'color': [0.46, 0.5, 0.42]},
        lights=[{'type': 'sun', 'azimuth': 240, 'elevation': 24, 'intensity': 0.9, 'color': [1.0, 0.88, 0.7]}],
        ambient=[0.6, 0.6, 0.52],
        fog={'color': [0.86, 0.82, 0.62], 'density': 0.005, 'sky_mix': 0.3},
        roadside=roadside,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.1},
        shots=[{'at': 2.0, 'x': 0.0, 'height': 0.8, 'fov': 64, 'pitch': 0.1, 'post': LOOK,
                'vehicle': {'type': 'jeep', 'ahead': 2.9}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(lost_valley().save(os.path.join(HERE, 'lost_valley.json')))

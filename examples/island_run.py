"""The island run: a road scene (road.py) on the water - a speedboat across a tropical bay, the open sea on one side
and an island's shore on the other.

The road is the sea itself (`surface` `sea`, no lines, no kerb, no bands): it mirrors the sky, rippling, and every
boat and buoy on it stands over its own reflection. To the left the sea runs to the horizon; to the right it
shallows to turquoise, then wet sand, a beach with its flotsam and a line of palms, the jungle behind (the ground
in bands, the beach things `scatter`ed on them). You follow in your own speedboat (the shot's `vehicle`, set a
little into the water, laying a `wake` behind it); another boat runs ahead with its own wake, sailboats lie off
in the bay, gulls over the water. The second shot skims low over the water toward the shore.
Run:  python island_run.py  -> writes island_run.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'source': 'light', 'strength': 1.0, 'radius': 2.0, 'spread': 0.4}]
SHORE = 4.0 + 2.5 + 1.0                      # from the channel's edge to the beach: open water, shallows, wet sand


def island_run():
    road = {
        'sections': [[14, 0, 0], [50, 0.35, 0], [60, -0.3, 0], [70, 0.25, 0], [300, -0.15, 0]],
        'width': 3.0, 'surface': 'sea', 'lines': False, 'rumble': False, 'bands': 0.0, 'ripple': 1.2,
        'ground': {'left': 'sea',
                   'right': [{'width': 4.0, 'texture': 'sea'}, {'width': 2.5, 'texture': 'shallows'},
                             {'width': 1.0, 'texture': 'wet_sand'}, {'width': 5.0, 'texture': 'beach_sand'},
                             {'texture': 'jungle_floor'}]},
        'distance': 320,
    }
    roadside = [
        {'type': ['palm', 'palm_lean', 'palm'], 'side': 'right', 'density': 0.45, 'offset': [SHORE + 3.0, SHORE + 7.0],
         'scale': [2.8, 3.8], 'flip': True, 'seed': 1},
        {'type': ['kapok', 'tree_fern', 'palm', 'banana_plant'], 'side': 'right', 'density': 0.6,
         'offset': [SHORE + 6.5, SHORE + 16.0], 'scale': [2.5, 6.0], 'seed': 2},
        {'type': 'buoy', 'side': 'left', 'every': 22, 'offset': 0.8, 'from': 12, 'scale': 0.6},
    ]
    scatter = [
        {'of': 'beach', 'side': 'right', 'density': 0.25, 'offset': [SHORE + 0.2, SHORE + 4.5], 'seed': 1},
        {'of': ['rocks', 'boulder', 'rocks'], 'side': 'right', 'density': 0.08, 'offset': [4.3, 6.5],
         'sizes': ['medium', 'large'], 'seed': 2},                     # rocks in the shallows
    ]
    decals = [{'tex': 'wake', 'at': 8.2, 'x': -0.75, 'size': 1.1, 'opacity': 0.85}]       # the boat ahead's wake
    sprites = [
        {'type': 'speedboat', 'at': 10.0, 'x': -0.75, 'z': -0.05, 'tint': [0.9, 0.95, 1.1]},
        {'type': 'sailboat', 'at': 60, 'x': -14, 'scale': 3.4},
        {'type': 'sailboat', 'at': 95, 'x': -30, 'scale': 3.6, 'flip': True},
        {'type': 'sailboat', 'at': 140, 'x': -9, 'scale': 3.2},
        {'type': 'seagull', 'at': 22, 'x': -2.5, 'z': 3.2, 'scale': 0.3},
        {'type': 'seagull', 'at': 27, 'x': 0.8, 'z': 3.8, 'scale': 0.26, 'flip': True},
        {'type': 'seagull', 'at': 31, 'x': 3.5, 'z': 2.9, 'scale': 0.26},
    ]
    return road_scene(
        road,
        title='The island run - a speedboat across a tropical bay, the island\'s shore beside it',
        sky='day',
        skyline='islands',
        lights=[{'type': 'sun', 'azimuth': 258, 'elevation': 11, 'intensity': 0.85}],
        ambient=[0.62, 0.64, 0.68],
        fog={'color': [0.74, 0.84, 0.92], 'density': 0.0025},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.7, 'fov': 64, 'pitch': 0.06},
        shots=[
            {'at': 2.0, 'x': 0.0, 'height': 0.7, 'fov': 64, 'pitch': 0.06, 'post': LOOK,
             'vehicle': {'type': 'speedboat', 'ahead': 2.8, 'z': -0.05, 'wake': {'size': 1.3}}},
            {'at': 30.0, 'x': 1.8, 'height': 0.32, 'fov': 62, 'pitch': 0.02, 'yaw': 10, 'roll': -4, 'post': LOOK},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(island_run().save(os.path.join(HERE, 'island_run.json')))

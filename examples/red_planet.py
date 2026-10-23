"""The red planet: a road scene (road.py) on another world - following a buggy across the rust-red plain of a
desert planet in the afternoon, mesas on the horizon, a dust devil whirling across the plain, two small moons up in
the butterscotch sky, the colony's domes ahead.

No road but the tracks: `regolith` tinted rust for the track and the ground, `rover_tracks` down the middle;
boulders scattered (the Moon's grey `crater` decals read as puddles on red dust). A `tornado` tinted dust-orange and scaled down is the dust devil; mesas
as a red `mountains` skyline; two `moon`s small in a `golden` sky turned orange by a dusty `fog`; the colony's
`dome`s and a `lander` ahead; the `moon_buggy` on ahead of you.
Run:  python red_planet.py  -> writes red_planet.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.5, 'radius': 2.0}]
DUST = {'base': 'regolith', 'tint': [1.15, 0.62, 0.42]}


def red_planet():
    road = {
        'sections': [[14, 0, 0], [40, 0.15, 0.6], [40, -0.2, -0.5], [300, 0.05, 0.3]],
        'width': 1.6, 'surface': DUST, 'lines': False, 'rumble': False, 'bands': 0.0,
        'edge': {'ragged': 0.3, 'blend': 0.8},
        'ground': DUST,
        'distance': 300,
    }
    roadside = [{'type': 'boulder', 'density': 0.1, 'offset': [0.8, 20.0], 'scale': [0.3, 1.4],
                 'tint': [1.0, 0.6, 0.45], 'seed': 1}]
    scatter = [{'of': 'rocks', 'density': 0.5, 'offset': [0.0, 6.0], 'tint': [1.0, 0.6, 0.45], 'seed': 2}]
    decals = [
        {'tex': 'rover_tracks', 'density': 0.5, 'size': [1.2, 1.4], 'side': 'road', 'seed': 1},
    ]
    sprites = [
        {'type': 'moon_buggy', 'at': 4.5, 'x': 0.0},
        {'type': 'tornado', 'at': 70, 'x': -24, 'scale': 16, 'tint': [1.2, 0.7, 0.5], 'opacity': 0.5},
        {'type': 'dome', 'at': 60, 'x': 6, 'scale': 3.0, 'tint': [1.0, 0.9, 0.8],
         'light': {'color': [0.8, 1.0, 0.8], 'radius': 4.0, 'intensity': 0.5, 'z': 1.0}},
        {'type': 'dome', 'at': 64, 'x': 10, 'scale': 2.2, 'tint': [1.0, 0.9, 0.8]},
        {'type': 'lander', 'at': 54, 'x': -6, 'scale': 2.4},
    ]
    return road_scene(
        road,
        title='The red planet - following a buggy across a rust-red plain, a dust devil, two moons in the sky',
        sky='golden',
        skyline={'type': 'mountains', 'height': 1.3, 'color': [0.62, 0.32, 0.24]},
        sky_objects=[{'type': 'moon', 'azimuth': 262, 'elevation': 24, 'size': 1.4},
                     {'type': 'moon', 'azimuth': 282, 'elevation': 16, 'size': 0.9}],
        lights=[{'type': 'sun', 'azimuth': 230, 'elevation': 30, 'intensity': 0.9, 'color': [1.0, 0.86, 0.72]}],
        ambient=[0.62, 0.48, 0.42],
        fog={'color': [0.86, 0.56, 0.38], 'density': 0.006, 'sky_mix': 0.6},
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 62, 'pitch': 0.06},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 62, 'pitch': 0.06, 'post': LOOK}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(red_planet().save(os.path.join(HERE, 'red_planet.json')))

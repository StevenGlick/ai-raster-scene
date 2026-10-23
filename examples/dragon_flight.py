"""The dragon flight: a road scene (road.py) in the air - riding a dragon at sunset down a river valley, the fields
and forests far below, other dragons on the wing around you, a dark castle on its crag ahead.

The dragon's way is the road, too narrow to see; the ground is `void` and far `below` lies the valley in bands
out from its middle - a `river_water` river, `farmland` along it, `forest_canopy` beyond - bending with the way;
mountains round it as a `mountains` skyline. The `dark_castle` stands on the valley floor (its `z` the depth below)
and rises over the horizon; dragons (`dragon`, in its three colours by `variant`) hang at every height, clouds
(`storm_cloud` tinted to the dusk) drift below. Your own dragon's neck, horns and wings before you
(`dragon_neck`, the shot's vehicle).
Run:  python dragon_flight.py  -> writes dragon_flight.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.2}]
DUSK_CLOUD = [2.6, 1.7, 1.8]


def dragon_flight():
    road = {
        'sections': [[60, 0.0, 0], [120, 0.22, 0], [300, -0.12, 0]],
        'width': 0.002, 'surface': 'asphalt', 'lines': False, 'rumble': False, 'bands': 0.0,
        'ground': 'void',
        'below': {'depth': 30, 'tile': 16, 'haze': 0.5,
                  'texture': [{'width': 4, 'texture': 'river_water'}, {'width': 60, 'texture': 'farmland'},
                              {'texture': 'forest_canopy'}]},
        'distance': 400,
    }
    sprites = [
        {'type': 'dark_castle', 'at': 120, 'x': 20, 'z': -30, 'scale': 44},
        {'type': 'dragon', 'variant': 1, 'at': 16, 'x': -4.2, 'z': 0.9, 'scale': 2.6},
        {'type': 'dragon', 'variant': 2, 'at': 30, 'x': 12.5, 'z': -1.6, 'scale': 3.0, 'flip': True},
        {'type': 'dragon', 'variant': 0, 'at': 60, 'x': 3.0, 'z': 9.0, 'scale': 3.0},
        {'type': 'dragon', 'variant': 1, 'at': 140, 'x': 12, 'z': 9.0, 'scale': 3.0, 'flip': True},
        {'type': 'storm_cloud', 'at': 40, 'x': -18, 'z': -8, 'scale': 6, 'tint': DUSK_CLOUD, 'opacity': 0.9},
        {'type': 'storm_cloud', 'at': 70, 'x': 14, 'z': -12, 'scale': 8, 'tint': DUSK_CLOUD, 'opacity': 0.9},
        {'type': 'storm_cloud', 'at': 110, 'x': -30, 'z': -6, 'scale': 10, 'tint': DUSK_CLOUD, 'opacity': 0.9},
    ]
    return road_scene(
        road,
        title='The dragon flight - riding a dragon at sunset down a river valley toward a dark castle on its crag',
        sky='sunset',
        skyline={'type': 'mountains', 'height': 1.2, 'color': [0.3, 0.24, 0.34]},
        sky_objects=[{'type': 'sun', 'azimuth': 250, 'elevation': 4, 'size': 2.6}],
        lights=[{'type': 'sun', 'azimuth': 250, 'elevation': 8, 'intensity': 0.9, 'color': [1.0, 0.72, 0.5],
                 'disc': False}],
        ambient=[0.56, 0.48, 0.56],
        fog={'color': [0.86, 0.6, 0.56], 'density': 0.003, 'sky_mix': 0.3},
        sprites=sprites,
        camera={'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': -0.06},
        shots=[{'at': 1.0, 'x': 0.0, 'height': 0.6, 'fov': 64, 'pitch': -0.06, 'post': LOOK,
                'vehicle': {'type': 'dragon_neck', 'ahead': 0.7, 'z': 0.31, 'scale': 0.25}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(dragon_flight().save(os.path.join(HERE, 'dragon_flight.json')))

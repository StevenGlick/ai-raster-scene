"""The ring station: a road scene (road.py) in space - driving the inside of a great ring turning in space, its
land rising ahead of you and curving up into the sky until it fills it, a planet beyond the glass of its rim.

The ring's floor is the road and its ground: the `sections` climb more steeply every one, so the land goes on up
ahead the way the inside of a wheel would, its far reaches overhead. Fields and a river either side - `pasture`,
`water`, `forest_canopy` in bands - and then a ground band of `void`: the ring's floor ends at its rim walls of
glass (`glasshouse`, see-through), and beyond them is space. Trees by density, a car ahead; the `space` sky with a
ringed planet and the sun.
Run:  python ring_station.py  -> writes ring_station.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LOOK = [{'fx': 'bloom', 'strength': 0.6, 'radius': 2.0}]
RIM = 12.0                                 # from the road's edge to the rim wall


def ring_station():
    sections = [[12, 0, 0]] + [[10, 0, 0.4 + k * 0.9] for k in range(30)]        # climbing ever more steeply
    road = {
        'sections': sections,
        'width': 2.2, 'lanes': 2, 'surface': 'asphalt', 'lines': '#e0e0e0', 'rumble': False, 'bands': 0.03,
        'ground': {'left': [{'width': 1.5, 'texture': 'grass'}, {'width': 2.5, 'texture': 'water'},
                            {'width': RIM - 4.0, 'texture': 'forest_canopy', 'tile': 6}, {'texture': 'void'}],
                   'right': [{'width': 3.0, 'texture': 'grass'}, {'width': RIM - 3.0, 'texture': 'pasture', 'tile': 4},
                             {'texture': 'void'}]},
        'walls': [{'side': 'both', 'offset': RIM, 'height': 4.0, 'texture': 'glasshouse', 'tile': [2.0, 4.0]}],
        'distance': 320,
    }
    roadside = [{'type': ['tree', 'birch'], 'density': 0.25, 'offset': [1.0, RIM - 1.0], 'scale': [1.2, 2.0],
                 'seed': 1}]
    sprites = [{'type': 'car_compact', 'at': 12, 'x': 0.55, 'variant': 2}]
    return road_scene(
        road,
        title='The ring station - driving the inside of a ring in space, its land curving up ahead into the sky',
        sky='space',
        sky_objects=[{'type': 'ringed', 'azimuth': 300, 'elevation': 12, 'size': 14},
                     {'type': 'sun', 'azimuth': 228, 'elevation': 8, 'size': 2.0}],
        lights=[{'type': 'sun', 'azimuth': 228, 'elevation': 40, 'intensity': 0.9, 'disc': False}],
        ambient=[0.56, 0.58, 0.62],
        roadside=roadside,
        sprites=sprites,
        camera={'at': 1.0, 'x': -0.55, 'height': 0.6, 'fov': 66, 'pitch': 0.1},
        shots=[{'at': 1.0, 'x': -0.55, 'height': 0.6, 'fov': 66, 'pitch': 0.1, 'post': LOOK,
                'vehicle': {'type': 'sports_car', 'ahead': 2.4}}],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(ring_station().save(os.path.join(HERE, 'ring_station.json')))

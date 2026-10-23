"""The synthwave drive: a road scene (road.py) - the red convertible on a road of light across a grid, toward a
striped sun going down behind wireframe mountains.

Everything is light on black: the ground is the `vector_grid` tinted magenta (its lines glow), the road dark with
cyan edges and a kerb of pink and violet, the sky the `vector` gradient with a sun drawn in stripes (`disc_style`
`stripes`) low ahead over the `mountains` skyline; palms stand along it in black silhouette (`tint`ed nearly to
nothing) against the glow. The strong neon bloom; a second shot leans into the bend.
Run:  python synthwave_drive.py  -> writes synthwave_drive.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

NEON = [{'fx': 'bloom', 'source': 'light', 'strength': 2.0, 'radius': 2.6, 'spread': 0.6}]
CAR = {'type': 'sports_car', 'ahead': 2.6}


def synthwave_drive():
    road = {
        'sections': [[20, 0, 0], [80, 0.3, 0.6], [80, -0.35, -0.6], [400, 0.2, 0]],
        'width': 4.2, 'lanes': 3, 'surface': {'base': 'asphalt', 'tint': [0.22, 0.18, 0.3]},
        'lines': '#ff4ad8', 'edges': '#40f0ff',
        'rumble': {'width': 0.3, 'colors': ['#ff4ad8', '#3a1a6a']},
        'ground': {'base': 'vector_grid', 'tint': [1.0, 0.32, 0.9]},
        'bands': 0.06, 'distance': 300,
    }
    roadside = [
        {'type': ['palm', 'palm_lean'], 'every': 8, 'offset': [1.2, 2.0], 'scale': [3.0, 3.8], 'flip': True,
         'tint': [0.08, 0.04, 0.12]},
    ]
    return road_scene(
        road,
        title='The synthwave drive - the red convertible across a grid of light toward a striped sun',
        sky='vector',
        skyline='mountains',
        lights=[{'type': 'sun', 'azimuth': 270, 'elevation': 10, 'intensity': 0.3, 'disc_style': 'stripes',
                 'disc_size': 9, 'disc_color': [1.0, 0.4, 0.7]}],
        ambient=[0.42, 0.3, 0.5],
        roadside=roadside,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[
            {'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'post': NEON, 'vehicle': CAR},
            {'at': 60.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'roll': 7, 'yaw': 4, 'post': NEON,
             'vehicle': CAR},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(synthwave_drive().save(os.path.join(HERE, 'synthwave_drive.json')))

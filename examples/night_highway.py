"""The night highway: a road scene (road.py) - a city highway at night under sodium lamps, tail lights ahead, a
tunnel through the hill where it bends.

Three lanes with white edge lines and a gravel shoulder; beyond it concrete, then the city's dark ground. Lamp
posts stand along both sides every 9, each with its `light` hung out over the road, so the asphalt lies in pools of
orange between them; the cars ahead are dark but for their tail lights, which glow. Where the road bends into the
hill a `tunnel_portal` stands across it and `tunnel_ring`s carry the tunnel on (a row down the `middle` every 1.2),
the road under it roofed (`roofs`) and lit by its own lamps. The city's skyline is lit along the horizon; your car's
`headlights` light the road in front of it. The second shot is in the tunnel, its lamps in a line down its roof.
Run:  python night_highway.py  -> writes night_highway.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LANE = 4.2 / 3
SODIUM = [1.0, 0.66, 0.32]
TUNNEL = (34.0, 62.0)                      # where the tunnel runs
GLOW = [{'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 2.2, 'spread': 0.55}]


def night_highway():
    road = {
        'sections': [[16, 0, 0], [40, 0.45, 1.0], [40, -0.35, 0.0], [60, 0.3, -0.8], [140, 0, 0]],
        'width': 4.2, 'lanes': 3, 'surface': 'asphalt', 'edges': '#d8d8d8', 'rumble': False,
        'shoulder': {'width': 0.5, 'texture': 'gravel'},
        'ground': [{'width': 1.5, 'texture': 'concrete'}, {'texture': 'asphalt', 'tint': [0.5, 0.5, 0.55]}],
        'roofs': [[TUNNEL[0], TUNNEL[1], 0.1]],
        'bands': 0.05, 'distance': 200,
    }
    roadside = [
        {'type': 'lamp_post', 'every': 9, 'offset': 0.7, 'scale': 3.4, 'flip': True, 'from': 4, 'to': TUNNEL[0] - 2,
         'light': {'color': SODIUM, 'radius': 6.5, 'intensity': 1.5, 'z': 3.0, 'x': 1.2}},
        {'type': 'lamp_post', 'every': 9, 'offset': 0.7, 'scale': 3.4, 'flip': True, 'from': TUNNEL[1] + 3,
         'light': {'color': SODIUM, 'radius': 6.5, 'intensity': 1.5, 'z': 3.0, 'x': 1.2}},
        {'type': 'tunnel_ring', 'side': 'middle', 'every': 1.2, 'offset': 0.0, 'from': TUNNEL[0] + 0.6,
         'to': TUNNEL[1]},
    ]
    scatter = [                                     # litter along the kerb, weeds through the concrete
        {'of': 'street', 'density': 0.08, 'offset': [0.0, 1.3], 'sizes': ['small', 'medium'], 'seed': 1},
        {'of': ['dry_tuft', 'grass_tuft'], 'density': 0.5, 'offset': [0.1, 1.5], 'to': TUNNEL[0] - 1, 'seed': 2},
    ]
    decals = [                                      # the wear of a city road: oil, patches, a manhole, cracks
        {'tex': 'city', 'density': 0.06, 'size': [0.5, 1.0], 'seed': 1},
        {'tex': 'tyre_marks', 'at': 6.5, 'x': -0.6, 'size': 0.55, 'opacity': 0.75},
    ]
    sprites = [
        {'type': 'tunnel_portal', 'at': TUNNEL[0], 'x': 0.0},
        {'type': 'car_sedan', 'at': 12, 'x': -LANE, 'tint': [0.5, 0.5, 0.6]},
        {'type': 'car_compact', 'at': 21, 'x': LANE, 'tint': [0.5, 0.55, 0.7]},
        {'type': 'box_truck', 'at': 30, 'x': 0.0, 'tint': [0.6, 0.6, 0.62]},
        {'type': 'car_sedan', 'at': 45, 'x': -LANE, 'tint': [0.45, 0.45, 0.5]},
        {'type': 'car_compact', 'at': 56, 'x': LANE, 'tint': [0.4, 0.45, 0.6]},
    ]
    lights = [{'at': a, 'x': 0.0, 'z': 2.8, 'radius': 3.0, 'color': [1.0, 0.8, 0.5], 'intensity': 0.8}
              for a in range(int(TUNNEL[0]) + 2, int(TUNNEL[1]), 4)]          # the tunnel's own lamps
    return road_scene(
        road,
        title='The night highway - sodium lamps, tail lights, a tunnel through the hill',
        sky='night',
        skyline='city',
        ambient=[0.1, 0.11, 0.17],
        fog={'color': [0.08, 0.08, 0.13], 'density': 0.012},
        lights=lights,
        roadside=roadside,
        scatter=scatter,
        decals=decals,
        sprites=sprites,
        camera={'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[
            {'at': 2.0, 'x': 0.0, 'height': 0.75, 'fov': 64, 'pitch': 0.1, 'post': GLOW,
             'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}},
            {'at': 41.0, 'x': 0.2, 'height': 0.75, 'fov': 64, 'pitch': 0.08, 'post': GLOW,
             'vehicle': {'type': 'sports_car', 'ahead': 2.6, 'headlights': True}},      # in the tunnel
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(night_highway().save(os.path.join(HERE, 'night_highway.json')))

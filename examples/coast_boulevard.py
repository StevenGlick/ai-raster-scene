"""Coast boulevard: a road scene (road.py) in the city-pop look - the red convertible down a seaside boulevard on a
summer afternoon, tall fan palms down both sides, white and pastel hotels standing back on the land side, the
promenade, the beach and a cobalt sea on the other, cumulus heaped on the horizon. Then the same boulevard at dusk,
the hotels' windows lit.

Shows the city-pop kit (scripts/citypop.py) on a road: `fan_palm` rows down both sides (`roadside`), the hotels as
`walls` cut into `blocks` of `ribbon_window` tiled a storey to a unit (some tinted pink and peach), a promenade of
`pool_deck`, the beach and `summer_sea` in `ground` bands; the `summer` sky and the `citypop` preset. The dusk shot
swaps in `ribbon_window_lit`, the `sunset` sky and `citypop_dusk` in its overrides.
Run:  python coast_boulevard.py  -> writes coast_boulevard.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LANE = 4.2 / 4                             # two lanes each way on a road 4.2 wide
PINK, PEACH = [1.0, 0.82, 0.82], [1.0, 0.9, 0.78]


def hotels(lit=False):
    win = 'ribbon_window_lit' if lit else 'ribbon_window'
    return {'side': 'left', 'offset': 3.2, 'height': 6.0, 'ragged': 3.0, 'blocks': 9, 'gaps': 0.3, 'seed': 4,
            'tile': [1, 1], 'from': 6,
            'texture': [win, {'base': win, 'tint': PINK}, win, {'base': win, 'tint': PEACH}]}


def road(lit=False):
    return {
        'sections': [[20, 0, 0], [60, -0.22, 0.5], [60, 0.3, -0.7], [80, -0.18, 0.4], [120, 0, 0]],
        'width': 4.2, 'lanes': 4, 'surface': 'blacktop',
        'rumble': {'width': 0.14, 'colors': ['#f2f0ea', '#f2f0ea']},                       # white kerbs
        'ground': {'left': [{'width': 1.4, 'texture': 'pool_deck'}, {'texture': 'lawn_stripes', 'tile': 2}],
                   'right': [{'width': 1.4, 'texture': 'pool_deck'}, {'width': 4.5, 'texture': 'white_sand'},
                             {'texture': 'summer_sea'}]},
        'walls': [hotels(lit)],
    }


def coast_boulevard():
    roadside = [
        {'type': 'fan_palm', 'every': 6, 'offset': 0.7, 'scale': [6.2, 7.6]},
        {'type': ['palm', 'palm_lean'], 'every': 13, 'side': 'right', 'offset': 3.4, 'from': 8, 'scale': [3.4, 4.2],
         'flip': True},
        {'type': 'parasol', 'every': 9, 'side': 'right', 'offset': 4.6, 'from': 5},
    ]
    sprites = [
        {'type': 'car_compact', 'at': 16, 'x': -LANE * 1.5, 'variant': 2},
        {'type': 'car_sedan', 'at': 34, 'x': -LANE * 0.5, 'variant': 1},
        {'type': 'car_oncoming', 'at': 28, 'x': LANE * 1.5},
        {'type': 'yacht', 'at': 60, 'x': 16.0, 'scale': 3.2, 'variant': 0},
        {'type': 'yacht', 'at': 90, 'x': 24.0, 'scale': 3.0, 'variant': 2, 'flip': True},
    ]
    dusk = {
        'sky': 'sunset',
        'lights': [{'type': 'sun', 'azimuth': 262, 'elevation': 4, 'color': [1.0, 0.6, 0.42], 'intensity': 0.6,
                    'disc_size': 5}],
        'ambient': [0.5, 0.42, 0.56],
        'fog': {'color': [0.82, 0.5, 0.52], 'density': 0.004},
        'road': road(lit=True),
    }
    return road_scene(
        road(),
        title='Coast boulevard - the convertible under the fan palms, in the city-pop look',
        sky='summer',
        skyline={'type': 'islands', 'count': 4},
        lights=[{'type': 'sun', 'azimuth': 20, 'elevation': 46, 'intensity': 1.1, 'color': [1.0, 0.96, 0.88]}],
        ambient=[0.62, 0.66, 0.84],
        fog={'color': [0.71, 0.88, 0.96], 'density': 0.003},
        roadside=roadside,
        sprites=sprites,
        post=['citypop'],
        camera={'at': 2.0, 'x': -LANE * 0.5, 'height': 0.75, 'fov': 64, 'pitch': 0.1},
        shots=[
            {'at': 2.0, 'x': -LANE * 0.5, 'height': 0.75, 'fov': 64, 'pitch': 0.1,
             'vehicle': {'type': 'sports_car', 'ahead': 2.6}},
            # down at the kerb under the palms, looking up the boulevard
            {'at': 30.0, 'x': -2.6, 'height': 0.4, 'fov': 70, 'pitch': 0.22, 'yaw': 4},
            # at dusk, the hotels lit
            {'at': 2.0, 'x': -LANE * 0.5, 'height': 0.75, 'fov': 64, 'pitch': 0.1,
             'vehicle': {'type': 'sports_car', 'ahead': 2.6},
             'post': ['citypop_dusk', {'fx': 'bloom', 'source': 'light', 'strength': 0.8, 'radius': 2.0,
                                       'spread': 0.4}],
             'overrides': dict(dusk, post=[])},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(coast_boulevard().save(os.path.join(HERE, 'coast_boulevard.json')))

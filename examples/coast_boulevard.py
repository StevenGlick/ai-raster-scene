"""Coast boulevard: a road scene (road.py) in the city-pop look - the red convertible down a seaside boulevard on a
summer afternoon, tall fan palms down both sides, white and pastel hotels standing back on the land side, the
promenade, the beach and a cobalt sea on the other, cumulus heaped on the horizon. Then the same boulevard at dusk,
the hotels' rooms lit one by one.

Shows the city-pop kit (scripts/citypop.py) on a road: `fan_palm` rows down both sides (`roadside`), and the hotels
as buildings in 3D - `walls` cut into `blocks` with a `depth`, so each is a box whose near end shows (`ends` of plain
`stucco`), each standing back by its own `setback`, its height a whole number of `storeys` - their fronts
`ribbon_window` and `hotel_balconies` a storey to a unit (some tinted pink and peach), a taller row behind; a
promenade of `pool_deck`, a `lawn_stripes` lawn, the beach and `summer_sea` in `ground` bands; the `summer` sky and
the `citypop` preset. At dusk the walls' `windows` light the rooms one by one from the `_lit` facades - each hotel
its own share of them, each room its own tint - under the `sunset` sky, with `citypop_dusk`.
Run:  python coast_boulevard.py  -> writes coast_boulevard.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import road_scene  # noqa: E402

LANE = 4.2 / 4                             # two lanes each way on a road 4.2 wide
PINK, PEACH = [1.0, 0.82, 0.82], [1.0, 0.9, 0.78]
FACADES = ['ribbon_window', 'hotel_balconies', {'base': 'ribbon_window', 'tint': PINK},
           {'base': 'hotel_balconies', 'tint': PEACH}]
LIT = ['ribbon_window_lit', 'hotel_balconies_lit', {'base': 'ribbon_window_lit', 'tint': PINK},
       {'base': 'hotel_balconies_lit', 'tint': PEACH}]


def hotels(lit=False):
    """The hotels on the land side: boxes 5 deep, a storey to a unit, white ends; a taller row behind them."""
    near = {'side': 'left', 'offset': 3.2, 'height': 6.0, 'ragged': 2.5, 'blocks': 8, 'gaps': 0.3, 'seed': 4,
            'tile': [1, 1], 'from': 6, 'depth': 5.0, 'storeys': True, 'ends': 'stucco', 'setback': 2.5,
            'texture': FACADES}
    far = {**near, 'offset': 12.5, 'height': 10.0, 'ragged': 4.0, 'blocks': 12, 'gaps': 0.15, 'seed': 9,
           'depth': 7.0, 'setback': 3.0}
    if lit:                                        # the rooms lit one by one, each hotel its own share
        for wl, share in ((near, 0.68), (far, 0.55)):
            wl['windows'] = {'lit': LIT, 'share': share, 'spread': 0.2, 'cells': [2, 1], 'dim': 0.3,
                             'colors': [[1.0, 1.0, 1.0], [1.0, 0.92, 0.8], [1.0, 0.84, 0.66], [0.92, 0.96, 1.05]]}
    return [near, far]


def road(lit=False):
    return {
        'sections': [[20, 0, 0], [60, -0.22, 0.5], [60, 0.3, -0.7], [80, -0.18, 0.4], [120, 0, 0]],
        'width': 4.2, 'lanes': 4, 'surface': 'blacktop',
        'rumble': {'width': 0.14, 'colors': ['#f2f0ea', '#f2f0ea']},                       # white kerbs
        'ground': {'left': [{'width': 1.4, 'texture': 'pool_deck'}, {'texture': 'lawn_stripes', 'tile': 2}],
                   'right': [{'width': 1.4, 'texture': 'pool_deck'}, {'width': 4.5, 'texture': 'white_sand'},
                             {'texture': 'summer_sea'}]},
        'walls': hotels(lit),
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

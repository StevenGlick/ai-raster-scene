"""Seaside terrace: a white villa's terrace over the sea on a summer afternoon, in the city-pop look - terracotta
tiles and a white railing, palms in their planters framing the view, a table for two under a parasol, white yachts
heeled over on a cobalt sea, gulls, a lighthouse on its rock and cumulus heaped on the horizon. Then the same terrace
at sunset, the sun going down into the sea.

Shows the city-pop kit (scripts/citypop.py) by the sea: `summer_sea` sunk below the terrace with a `drop` (its glints
mirror the sky), `terracotta_tile`, a `white_railing` (see-through) along its edge, the villa's `glass_wall`; the props `yacht` (three
stripes: navy, red, turquoise), `bistro_set`, `parasol` and `agave`; the `islands` skyline; the `summer` sky with
the `citypop` preset, and `sprite_shadows` so the palms lay their shadows over the tiles. The sunset shot swaps the
sky, the sun and the preset (`citypop_dusk`) in its overrides.
Run:  python seaside_terrace.py  -> writes seaside_terrace.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

LEGEND = {
    '~': {'floor': 'summer_sea', 'drop': 0.4},
    '.': {'floor': 'terracotta_tile'},
    'p': {'wall': 'white_railing', 'h': 0.45},                                  # a white railing over the sea
    'V': {'wall': ['glass_wall', 'stucco'], 'h': 2.0, 'top': 'stucco'},        # the villa: glass doors, white above
    'S': {'wall': ['stucco', 'ribbon_window'], 'h': 2.0, 'top': 'stucco'},
    'q': {'wall': 'stucco', 'h': 0.45, 'top': 'grass'},                         # planters
    'b': {'floor': 'white_sand', 'drop': 0.25},                                 # a beach curving out to the west
}


def seaside_terrace():
    g = Grid(34, 32, fill='.')
    g.rect(0, 0, 33, 17, '~')                      # the sea
    for y in range(3, 18):                         # the beach, widening toward the terrace
        g.rect(0, y, min(7, 1 + (y - 3) // 2), y, 'b')
    g.rect(0, 18, 33, 18, 'p')                     # the railing along the terrace's edge
    g.rect(27, 20, 33, 31, 'V')                    # the villa, its glass doors onto the terrace
    g.rect(0, 29, 26, 31, 'S')
    g.rect(8, 19, 9, 19, 'q')                      # planters either side of the view
    g.rect(19, 19, 20, 19, 'q')
    sprites = [
        # palms in the planters, framing the view
        {'x': 8.8, 'y': 19.5, 'z': 0.45, 'type': 'palm', 'scale': 4.4},
        {'x': 20.0, 'y': 19.5, 'z': 0.45, 'type': 'palm_lean', 'scale': 4.0, 'flip': True},
        {'x': 30.8, 'y': 18.8, 'type': 'palm', 'scale': 4.6, 'flip': True},
        # palms along the beach
        {'x': 2.0, 'y': 7.0, 'type': 'palm', 'scale': 4.6},
        {'x': 3.6, 'y': 10.6, 'type': 'palm_lean', 'scale': 4.2, 'flip': True},
        {'x': 1.2, 'y': 13.0, 'type': 'palm', 'scale': 5.0, 'flip': True},
        {'x': 5.4, 'y': 15.2, 'type': 'palm', 'scale': 4.0},
        {'x': 4.6, 'y': 12.4, 'type': 'parasol', 'variant': 2},
        # a table for two under a parasol, another in the sun; agaves along the parapet
        {'x': 16.6, 'y': 20.2, 'type': 'bistro_set'}, {'x': 16.6, 'y': 20.2, 'type': 'parasol', 'variant': 0},
        {'x': 5.4, 'y': 20.6, 'type': 'bistro_set'},
        {'x': 11.6, 'y': 19.4, 'type': 'agave'}, {'x': 23.4, 'y': 19.4, 'type': 'agave'},
        # out at sea: yachts heeled over, a lighthouse on its rock far out, gulls
        {'x': 11.0, 'y': 8.5, 'type': 'yacht', 'variant': 0},
        {'x': 23.5, 'y': 3.5, 'type': 'yacht', 'variant': 1, 'scale': 3.2, 'flip': True},
        {'x': 4.0, 'y': -6.0, 'type': 'yacht', 'variant': 2, 'scale': 3.0},
        {'x': 30.0, 'y': -24.0, 'type': 'lighthouse_tower', 'scale': 6.0},
        {'x': 14.0, 'y': 12.0, 'z': 2.6, 'type': 'seagull'},
        {'x': 17.5, 'y': 10.0, 'z': 3.2, 'type': 'seagull', 'flip': True},
    ]
    objects = [
        {'type': 'lounger', 'x': 24.6, 'y': 21.4, 'angle': 270, 'paint': '#15a6c2'},
    ]
    sunset = {
        'sky': 'sunset',
        'ambient': [0.36, 0.3, 0.44],
        'lights': [{'type': 'sun', 'azimuth': 262, 'elevation': 4, 'color': [1.0, 0.62, 0.42], 'intensity': 0.7,
                    'disc_size': 3.2}],
        'fog': {'color': [0.78, 0.5, 0.52], 'density': 0.004},
        'post': ['citypop_dusk', {'fx': 'bloom', 'source': 'light', 'strength': 0.6, 'radius': 2.0, 'spread': 0.4}],
    }
    return scene(
        g,
        legend=LEGEND,
        title='Seaside terrace - a white villa over the sea, in the city-pop look',
        sky='summer',
        skyline={'type': 'islands', 'count': 5},
        ambient=[0.44, 0.48, 0.68],
        lights=[{'type': 'sun', 'azimuth': 140, 'elevation': 44, 'color': [1.0, 0.96, 0.88], 'intensity': 1.2}],
        fog={'color': [0.71, 0.88, 0.96], 'density': 0.004},
        sprites=sprites,
        objects=objects,
        reflections={'amount': 0.8, 'ripple': 0.6},
        surface_noise=0,
        light_levels=0,
        side_shade=1.0,
        sprite_shadows=True,
        post=['citypop'],
        max_distance=96,
        camera={'x': 14.4, 'y': 23.2, 'height': 0.5, 'look_at': [12.0, 6.0, 1.5], 'fov': 70},
        shots=[
            # over the railing to the yachts, palms either side
            {'x': 14.4, 'y': 23.2, 'height': 0.5, 'look_at': [12.0, 6.0, 1.5], 'fov': 70},
            # by the table under the parasol
            {'x': 13.2, 'y': 21.6, 'height': 0.46, 'look_at': [19.0, 12.0, 0.7], 'fov': 70},
            # back along the terrace to the villa
            {'x': 3.6, 'y': 20.6, 'height': 0.5, 'look_at': [30.0, 26.0, 1.0], 'fov': 72},
            # the sun going down into the sea
            {'x': 14.4, 'y': 23.2, 'height': 0.5, 'look_at': [8.0, 6.0, 1.4], 'fov': 70, 'overrides': sunset},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(seaside_terrace().save(os.path.join(HERE, 'seaside_terrace.json')))

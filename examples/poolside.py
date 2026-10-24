"""Poolside: a white house by a turquoise pool on a summer afternoon, in the city-pop look - after the paintings on
the sleeves of Japanese city-pop records: a deep cobalt sky with cumulus heaped on the horizon, white stucco and walls
of glass mirroring the sky, palms and the hard shadows they throw, striped parasols over the loungers, a diving board,
a float drifting on the water, and nobody about. Then the same pool at dusk, its lights on under the water.

Shows the city-pop kit (scripts/citypop.py): the `summer` sky; the `citypop` post preset - flat colour from the
`citypop` palette with no dither - with `surface_noise` 0 and `light_levels` 0, so every surface prints as one or two
inks; `stucco`, `ribbon_window` and `glass_wall` (and their `_lit` versions after dark, swapped in by the dusk shot's
overrides, with the `citypop_dusk` preset), `pool_water` sunk with a `drop` and `pool_deck` with `pool_tile` as its
`side` (the pool's wall, seen below the waterline); the props `parasol`, `fan_palm` and `agave`, the objects
`lounger`, `pool_ladder` and `diving_board`, the decal `pool_ring`; and `sprite_shadows`, so the palms and parasols
throw the sun's shadow over the deck and up the walls.
Run:  python poolside.py  -> writes poolside.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

DAY = {
    '.': {'floor': 'pool_deck', 'side': 'pool_tile'},
    '~': {'floor': 'pool_water', 'drop': 0.1},
    'o': {'floor': 'grass'},
    'h': {'wall': 'hedge', 'h': 0.6, 'top': 'hedge'},
    'G': {'wall': ['glass_wall', 'ribbon_window'], 'h': 2.0, 'top': 'stucco'},     # glass below, a long window above
    'L': {'wall': {'base': 'stucco', 'tint': [0.98, 0.72, 0.76]}, 'h': 1.2, 'top': 'stucco'},  # a pink pavilion
    'R': {'wall': ['ribbon_window', 'stucco', 'stucco'], 'h': 2.7, 'top': 'stucco'},  # the tower: a tall white wall
}
# after dark the house is lit inside and the pool from under its water
DUSK = dict(DAY, **{
    '~': {'floor': 'pool_water_lit', 'drop': 0.1},
    'G': {'wall': ['glass_wall_lit', 'ribbon_window_lit'], 'h': 2.0, 'top': 'stucco'},
    'R': {'wall': ['ribbon_window_lit', 'stucco', 'stucco'], 'h': 2.7, 'top': 'stucco'},
})


def poolside():
    g = Grid(30, 34, fill='.')
    g.rect(0, 0, 29, 33, 'o')                      # the lawn beyond the hedges
    g.rect(2, 3, 27, 33, '.')                      # the deck
    g.rect(1, 6, 1, 33, 'h')                       # hedges down either side
    g.rect(28, 6, 28, 33, 'h')
    g.rect(9, 3, 19, 7, 'G')                       # the house: glass below, a ribbon window above
    g.rect(5, 4, 8, 7, 'L')                        # its low wing
    g.rect(20, 1, 24, 7, 'R')                      # and its tower
    g.rect(9, 12, 20, 21, '~')                     # the pool
    objects = [
        # loungers in pairs down the west side, facing the water, and two on the east side
        *[{'type': 'lounger', 'x': 7.0, 'y': y, 'angle': 0, 'paint': p} for y, p in (
            (13.0, '#15a6c2'), (14.0, '#15a6c2'), (16.4, '#f05a5a'), (17.4, '#f05a5a'), (19.8, '#ffc93a'),
            (20.8, '#ffc93a'))],
        {'type': 'lounger', 'x': 22.8, 'y': 15.0, 'angle': 180, 'paint': '#2658c6'},
        {'type': 'lounger', 'x': 22.8, 'y': 16.0, 'angle': 180, 'paint': '#2658c6'},
        {'type': 'pool_ladder', 'x': 21.02, 'y': 13.4, 'angle': 180},
        {'type': 'pool_ladder', 'x': 8.98, 'y': 20.2, 'angle': 0},
        {'type': 'diving_board', 'x': 14.5, 'y': 11.3, 'angle': 90},
        # white slabs reaching out from the house: a balcony over the glass, the flat roof's eave above it
        {'type': 'beam', 'x': 14.5, 'y': 8.35, 'z': 0.96, 'length': 11.4, 'width': 0.7, 'depth': 0.08,
         'material': 'stucco', 'casts': True},
        {'type': 'beam', 'x': 14.5, 'y': 8.2, 'z': 2.0, 'length': 11.6, 'width': 0.4, 'depth': 0.07,
         'material': 'stucco'},
    ]
    sprites = [
        # a parasol over each pair of loungers
        {'x': 6.5, 'y': 13.5, 'type': 'parasol', 'variant': 1},
        {'x': 6.5, 'y': 16.9, 'type': 'parasol', 'variant': 0},
        {'x': 6.5, 'y': 20.3, 'type': 'parasol', 'variant': 2},
        {'x': 23.3, 'y': 15.5, 'type': 'parasol', 'variant': 3},
        # palms down the west side, their shadows thrown across the deck; one by the tower, shading its wall
        {'x': 3.6, 'y': 24.4, 'type': 'palm', 'scale': 4.2},
        {'x': 4.2, 'y': 18.6, 'type': 'palm_lean', 'scale': 3.8},
        {'x': 3.4, 'y': 11.6, 'type': 'palm', 'scale': 4.4, 'flip': True},
        {'x': 18.6, 'y': 9.4, 'type': 'palm', 'scale': 3.9, 'flip': True},
        {'x': 25.8, 'y': 13.0, 'type': 'palm', 'scale': 3.8},
        {'x': 25.4, 'y': 23.0, 'type': 'palm_lean', 'scale': 3.6, 'flip': True},
        # behind the house, palms over the roof and fan palms taller still
        {'x': 11.4, 'y': 1.6, 'type': 'palm', 'scale': 4.8},
        {'x': 15.8, 'y': 0.9, 'type': 'palm', 'scale': 5.2, 'flip': True},
        {'x': 3.0, 'y': 1.2, 'type': 'fan_palm', 'scale': 7.0},
        {'x': 6.4, 'y': 0.6, 'type': 'fan_palm'},
        {'x': 27.0, 'y': 2.4, 'type': 'fan_palm', 'scale': 7.4},
        # agaves by the glass doors
        {'x': 8.6, 'y': 8.6, 'type': 'agave'}, {'x': 19.4, 'y': 8.6, 'type': 'agave'},
    ]
    return scene(
        g,
        legend=DAY,
        title='Poolside - a white house by the pool, in the city-pop look',
        sky='summer',
        ambient=[0.44, 0.48, 0.68],
        lights=[{'type': 'sun', 'azimuth': 135, 'elevation': 40, 'color': [1.0, 0.96, 0.88], 'intensity': 1.2}],
        fog={'color': [0.71, 0.88, 0.96], 'density': 0.003},
        sprites=sprites,
        objects=objects,
        decals=[{'tex': 'pool_ring', 'surface': 'floor', 'x': 14.4, 'y': 19.6, 'size': 0.5}],
        reflections={'amount': 1.0, 'ripple': 0.35},
        surface_noise=0,
        light_levels=0,
        side_shade=1.0,
        sprite_shadows=True,
        post=['citypop'],
        camera={'x': 21.6, 'y': 22.8, 'height': 0.5, 'look_at': [11.0, 9.0, 0.8], 'fov': 70},
        shots=[
            # from the pool's corner, across the water to the house
            {'x': 21.6, 'y': 22.8, 'height': 0.5, 'look_at': [11.0, 9.0, 0.8], 'fov': 70},
            # from the shallow end, the diving board across the water
            {'x': 14.6, 'y': 24.2, 'height': 0.4, 'look_at': [14.6, 8.0, 1.1], 'fov': 66},
            # along the loungers on the west side
            {'x': 5.2, 'y': 25.4, 'height': 0.45, 'look_at': [8.4, 11.0, 0.5], 'fov': 68},
            # down at the water, the float drifting
            {'x': 13.2, 'y': 23.2, 'height': 0.48, 'look_at': [15.2, 15.6, -0.3], 'fov': 62},
            # the same pool at dusk, its lights on, the sun going down behind the house
            {'x': 21.6, 'y': 22.8, 'height': 0.5, 'look_at': [11.0, 9.0, 0.8], 'fov': 70,
             'overrides': {
                 'legend': DUSK,
                 'sky': 'sunset',
                 'ambient': [0.34, 0.28, 0.44],
                 'lights': [{'type': 'sun', 'azimuth': 226, 'elevation': 3, 'color': [1.0, 0.5, 0.42],
                             'intensity': 0.4, 'disc_size': 3.0},
                            *[{'x': x, 'y': y, 'z': 0.05, 'radius': 4.0, 'color': [0.35, 0.95, 1.0],
                               'intensity': 0.55} for x, y in ((11.5, 14.5), (18.0, 14.5), (11.5, 19.5), (18.0, 19.5))],
                            *[{'x': x, 'y': 9.2, 'z': 0.6, 'radius': 3.0, 'color': [1.0, 0.78, 0.5],
                               'intensity': 0.35} for x in (11.0, 15.0, 18.5)]],
                 'fog': {'color': [0.5, 0.36, 0.52], 'density': 0.006},
                 'post': ['citypop_dusk', {'fx': 'bloom', 'source': 'light', 'strength': 0.7, 'radius': 2.0,
                                           'spread': 0.4}],
             }},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(poolside().save(os.path.join(HERE, 'poolside.json')))

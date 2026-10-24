"""Roadside diner: a stainless-steel diner by a two-lane road on a summer afternoon, in the city-pop look - its
tall sign on a pole, two old gas pumps under a white canopy, cars in pastel paint on the lot, fan palms, telephone
poles along the road and a cobalt sky with cumulus heaped on the horizon. Then the same diner at dusk, its windows
lit, the sign and the pumps' globes glowing.

Shows the city-pop kit (scripts/citypop.py) in the American roadside: `diner_front` (and `diner_front_lit` after
dark), `blacktop` for the road and the lot, `blacktop_line` down its middle; the objects in 3D - the `diner_sign` on
its pole (`lit` after dark), two `gas_pump`s (their `paint`; `lights` after dark), `car`s in pastel paint, a canopy of
`stucco` (a `beam` on `column`s), `telegraph_pole`s along the old road behind with their wires (`cable`s from
insulator to insulator); `fan_palm` and `palm` props; the `summer` sky and the `citypop`
preset, `side_shade` 1 and `sprite_shadows`. The dusk shot swaps the legend, the objects, the sky and the preset
(`citypop_dusk`) in its overrides.
Run:  python roadside_diner.py  -> writes roadside_diner.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402


def legend(lit=False):
    return {
        ',': {'floor': {'base': 'stucco', 'tint': [1.0, 0.86, 0.66]}},          # the flat sand of the desert
        'r': {'floor': 'blacktop'},
        'm': {'floor': 'blacktop_line'},                                         # the road's centre line
        'l': {'floor': 'blacktop'},                                              # the lot
        'D': {'wall': 'diner_front_lit' if lit else 'diner_front', 'h': 1.0, 'top': 'stucco'},
        'K': {'wall': 'stucco', 'h': 1.3, 'top': 'stucco'},                    # the kitchen behind
        'i': {'wall': 'stucco', 'h': 0.06, 'top': 'stucco'},                   # the pumps' island
    }


def objects(lit=False):
    return [
        {'type': 'diner_sign', 'x': 21.8, 'y': 12.9, 'angle': 270, 'lit': lit},       # its arrow to the diner
        {'type': 'gas_pump', 'x': 5.6, 'y': 13.5, 'angle': 90, 'paint': '#d9302e', 'lights': lit},
        {'type': 'gas_pump', 'x': 6.6, 'y': 13.5, 'angle': 90, 'paint': '#15a6c2', 'lights': lit},
        {'type': 'car', 'x': 13.4, 'y': 13.2, 'angle': 90, 'paint': '#5cd6e2'},
        {'type': 'car', 'x': 17.8, 'y': 13.0, 'angle': 76, 'paint': '#ff8fa0'},
        # the canopy over the pumps: a white slab on two columns
        {'type': 'beam', 'x': 6.1, 'y': 13.5, 'z': 1.25, 'length': 3.4, 'width': 1.8, 'depth': 0.14,
         'material': 'stucco'},
        *[{'type': 'column', 'x': x, 'y': 13.5, 'material': 'stucco', 'sides': 8, 'radius': 0.06, 'height': 1.25,
           'base': 0.0, 'capital': 0.0, 'sink': 0.0, 'casts': True, 'seed': k} for k, x in enumerate((4.8, 7.4))],
        # telephone poles along the old road behind the diner, and their wires from insulator to insulator
        *[{'type': 'telegraph_pole', 'x': x, 'y': POLE_Y, 'seed': k} for k, x in enumerate(POLES)],
        *[{'type': 'cable', 'x': a, 'y': POLE_Y + dy, 'z': z, 'to': [b, POLE_Y + dy, z], 'sag': 0.12, 'width': 0.035,
           'color': '#1a2238'}
          for a, b in zip(POLES, POLES[1:]) for dy in (-0.35, 0.35) for z in (2.85, 2.61)],
    ]


POLES, POLE_Y = (1.0, 7.0, 13.0, 19.0, 25.0, 31.0), 4.6


def sprites():
    return [
        # fan palms behind the diner, palms by the lot
        {'x': 8.0, 'y': 6.0, 'type': 'fan_palm', 'scale': 7.2}, {'x': 12.5, 'y': 4.5, 'type': 'fan_palm'},
        {'x': 24.5, 'y': 6.0, 'type': 'fan_palm', 'scale': 7.6}, {'x': 28.0, 'y': 9.5, 'type': 'fan_palm', 'scale': 6.4},
        {'x': 3.0, 'y': 9.0, 'type': 'fan_palm', 'scale': 6.8},
        {'x': 28.2, 'y': 13.2, 'type': 'palm', 'scale': 3.8, 'flip': True},
        {'x': 2.6, 'y': 12.6, 'type': 'palm_lean', 'scale': 3.6},
        {'x': 10.4, 'y': 11.6, 'type': 'agave'}, {'x': 23.4, 'y': 11.6, 'type': 'agave'},
    ]


def roadside_diner():
    g = Grid(34, 30, fill=',')
    g.rect(0, 15, 33, 17, 'r')                     # the road
    g.rect(0, 16, 33, 16, 'm')
    g.rect(5, 12, 28, 14, 'l')                     # the lot
    g.rect(11, 9, 20, 11, 'D')                     # the diner
    g.rect(12, 7, 19, 8, 'K')                      # its kitchen behind
    g.rect(5, 13, 7, 13, 'i')                      # the pumps' island
    dusk = {
        'legend': legend(lit=True),
        'objects': objects(lit=True),
        'sky': 'sunset',
        'ambient': [0.38, 0.32, 0.48],
        'lights': [{'type': 'sun', 'azimuth': 200, 'elevation': 3, 'color': [1.0, 0.55, 0.42], 'intensity': 0.45,
                    'disc_size': 3.0},
                   {'x': 21.8, 'y': 13.2, 'z': 3.6, 'radius': 6.0, 'color': [1.0, 0.5, 0.78], 'intensity': 0.8},
                   {'x': 6.1, 'y': 13.5, 'z': 1.1, 'radius': 4.0, 'color': [1.0, 0.9, 0.7], 'intensity': 0.9},
                   *[{'x': x, 'y': 12.4, 'z': 0.6, 'radius': 3.5, 'color': [1.0, 0.8, 0.55], 'intensity': 0.6}
                     for x in (13.0, 16.0, 19.0)]],
        'fog': {'color': [0.5, 0.36, 0.52], 'density': 0.006},
        'post': ['citypop_dusk', {'fx': 'bloom', 'source': 'light', 'strength': 0.7, 'radius': 2.0, 'spread': 0.4}],
    }
    return scene(
        g,
        legend=legend(),
        title='Roadside diner - a stainless diner by the road, in the city-pop look',
        sky='summer',
        skyline={'type': 'mountains', 'height': 0.5},
        ambient=[0.44, 0.48, 0.68],
        lights=[{'type': 'sun', 'azimuth': 62, 'elevation': 48, 'color': [1.0, 0.96, 0.88], 'intensity': 1.2}],
        fog={'color': [0.71, 0.88, 0.96], 'density': 0.004},
        sprites=sprites(),
        objects=objects(),
        surface_noise=0,
        light_levels=0,
        side_shade=1.0,
        sprite_shadows=True,
        post=['citypop'],
        camera={'x': 16.8, 'y': 21.0, 'height': 0.5, 'look_at': [18.4, 10.0, 2.6], 'fov': 70},
        shots=[
            # across the road
            {'x': 16.8, 'y': 21.0, 'height': 0.5, 'look_at': [18.4, 10.0, 2.6], 'fov': 70},
            # by the pumps, along the front of the diner to its sign
            {'x': 4.0, 'y': 15.6, 'height': 0.45, 'look_at': [17.0, 10.6, 1.0], 'fov': 70},
            # the same at dusk, the neon on
            {'x': 16.8, 'y': 21.0, 'height': 0.5, 'look_at': [18.4, 10.0, 2.6], 'fov': 70, 'overrides': dusk},
        ],
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(roadside_diner().save(os.path.join(HERE, 'roadside_diner.json')))

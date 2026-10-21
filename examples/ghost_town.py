"""Ghost town: a frontier main street at high noon, and the same street at sundown when the dead come
back for a drink.

Shows the `western` facade style - clapboard false fronts in faded paint with their painted signs
(saloon, bank, general store...), sash windows in plain casings, the saloon's batwing doors - and
how to roof a boardwalk: the walk is a step of `planks` with a `ceil`, at a low `ceiling_height`,
and the facade stands the posts and fascia of the porch along its outer edge, a roof of boards
sloping down to it from the front; behind each false front the building's own gabled roof, so
the street has depth. The ends of each block are plain walls, so the fronts only face the street.
Desert at the end of the street, a windpump, red-rock mesas built in 3D (canyon rock lining the
mesa walls); the cowboy, tumbleweeds, troughs of boards with water in them (`trough` objects); and
at dusk the saloon lit, lanterns on the porches and a ghost in the street.
Run:  python ghost_town.py  -> writes ghost_town.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

NOON = {'type': 'sun', 'azimuth': 120, 'elevation': 62, 'intensity': 1.1}
WARM = [1.0, 0.62, 0.3]


def ghost_town():
    g = Grid(46, 72, fill='D')                     # the desert
    g.rect(0, 0, 45, 1, 'R')                       # mesas far off beyond the end of the street
    g.rect(0, 0, 0, 71, 'R'); g.rect(45, 0, 45, 71, 'R')
    for x0, x1, f, b in ((1, 17, 18, 19), (28, 44, 27, 26)):
        g.rect(x0, 36, x1, 71, 'W')                # the buildings, running to the edge of the map
        g.rect(f, 36, f, 71, 'f')                  # the fronts' cells
        g.rect(b, 36, b, 71, 'b')                  # the boardwalk
        g.rect(min(x0, b), 35, max(x1, b), 35, 'X')   # a plain wall at the end of the block
    g.rect(20, 2, 25, 71, 'd')                     # the street, rutted dust, on out into the desert
    sprites = [
        # the street at noon: the cowboy, tumbleweeds, a trough, barrels and crates on the walk
        {'id': 'cowboy', 'x': 22.9, 'y': 63.0, 'type': 'cowboy', 'facing': 90},
        {'x': 21.2, 'y': 67.6, 'type': 'tumbleweed'}, {'x': 24.4, 'y': 52.2, 'type': 'tumbleweed', 'scale': 0.36},
        {'x': 19.5, 'y': 65.5, 'type': 'barrel'}, {'x': 19.6, 'y': 66.2, 'type': 'crate'},
        {'x': 26.5, 'y': 46.6, 'type': 'barrel'}, {'x': 26.5, 'y': 47.3, 'type': 'barrel', 'flip': True},
        {'x': 19.6, 'y': 42.0, 'type': 'wagon_wheel'}, {'x': 26.4, 'y': 61.0, 'type': 'crate'},
        {'x': 24.8, 'y': 41.0, 'type': 'cart', 'flip': True},
        {'x': 22.0, 'y': 49.0, 'type': 'cow_skull'},
        # the end of the street: the windpump, saguaros, the open desert
        {'x': 17.0, 'y': 24.0, 'type': 'windpump'},
        {'x': 30.0, 'y': 22.0, 'type': 'saguaro'}, {'x': 34.5, 'y': 27.5, 'type': 'saguaro', 'scale': 2.4},
        {'x': 10.0, 'y': 18.0, 'type': 'saguaro', 'scale': 3.6, 'flip': True}, {'x': 27.5, 'y': 30.0, 'type': 'prickly_pear'},
        {'x': 13.5, 'y': 28.5, 'type': 'prickly_pear', 'flip': True}, {'x': 38.0, 'y': 14.0, 'type': 'saguaro'},
        {'x': 6.0, 'y': 30.0, 'type': 'saguaro', 'scale': 2.8},
    ]
    sprites.append({'id': 'barkeep', 'x': 20.3, 'y': 38.4, 'type': 'shopkeeper', 'facing': 0})
    objects = [{'type': 'trough', 'x': 20.6, 'y': 63.0, 'angle': 90, 'seed': 2},      # troughs of boards, water in them
               {'type': 'trough', 'x': 18.4, 'y': 25.4, 'seed': 5},
               # the mesas' cliffs in 3D, in beds of red and pale stone, over the old walls cut down
               {'type': 'rock_wall', 'x': 0, 'y': 0, 'lining': 'R', 'rock': 'canyon', 'depth': 1.0,
                'height': [5.2, 6.0], 'trim': 0.05, 'pieces': [3.0, 6.0], 'seed': 4}]      # broad: mesas, far off
    dusk = [{'id': 'ghost', 'x': 22.6, 'y': 56.0, 'type': 'ghost', 'facing': 90}]
    lanterns = [(19.55, y) for y in (40.0, 49.5, 59.0)] + [(26.45, y) for y in (44.5, 54.0, 64.0)]
    dusk += [{'x': x, 'y': y, 'type': 'lantern', 'z': 0.95} for x, y in lanterns]
    dusk_lights = [{'x': x, 'y': y, 'z': 1.0, 'radius': 3.4, 'color': WARM, 'intensity': 1.2} for x, y in lanterns]
    return scene(
        g,
        legend={
            'W': {'wall': 'boards', 'h': 1.0,
                  'facade': {'style': 'western', 'storeys': [1, 2], 'widths': [2, 4], 'lit': 0.3, 'seed': 8}},
            'X': {'wall': 'boards', 'h': 2.2, 'top': 'planks'},
            'f': {'floor': 'planks'},
            'b': {'wall': 'planks', 'h': 0.15, 'top': 'planks', 'ceil': 'planks'},
            'd': {'floor': 'desert_wash'},
            'D': {'floor': 'desert_wash'},
            'R': {'wall': ['sandstone', 'sandstone', 'sandstone_pale', 'sandstone', 'sandstone'], 'h': 5.0,
                  'top': 'desert_wash'},
        },
        title='Ghost town - a frontier main street',
        sky='day',
        ceiling_height=1.15,
        ambient=[0.42, 0.38, 0.34],
        fog={'color': [0.86, 0.76, 0.62], 'density': 0.008},
        lights=[NOON],
        sprites=sprites,
        objects=objects,
        scatter=[{'of': 'desert', 'on': 'D', 'density': 0.2, 'sizes': {'tiny': 4, 'small': 2}, 'seed': 9}],
        camera={'x': 22.9, 'y': 70.0, 'angle': 270, 'fov': 64, 'height': 0.5},
        shots=[
            {'x': 22.9, 'y': 70.0, 'angle': 270,
             'overlays': [{'type': 'caption', 'text': 'High noon', 'at': 'top', 'box': True}],
             'post': [{'fx': 'grade', 'tint': [1.06, 1.0, 0.9], 'saturation': 1.05}]},
            {'x': 23.6, 'y': 41.6, 'look_at': [19.0, 39.0, 1.0], 'fov': 62,
             'overlays': [{'type': 'bubble', 'anchor': 'barkeep', 'name': 'The Barkeep',
                           'text': "Whiskey's warm and the piano's dead. Come in anyway."}]},
            {'x': 22.9, 'y': 66.0, 'angle': 270, 'extra_sprites': dusk,
             'overlays': [{'type': 'caption', 'text': 'Ghost town', 'at': 'top', 'box': True}],
             'overrides': {'sky': 'sunset', 'ambient': [0.16, 0.13, 0.18],
                           'lights': [{'type': 'sun', 'azimuth': 250, 'elevation': 4, 'intensity': 0.45}] + dusk_lights,
                           'fog': {'color': [0.32, 0.2, 0.22], 'density': 0.02, 'glow': 0.8}},
             'post': [{'fx': 'bloom', 'threshold': 0.55, 'strength': 0.6, 'radius': 5}]},
            {'x': 23.0, 'y': 33.0, 'look_at': [17.0, 24.0, 2.4], 'fov': 66,
             'overrides': {'sky': 'sunset', 'ambient': [0.3, 0.22, 0.24],
                           'lights': [{'type': 'sun', 'azimuth': 236, 'elevation': 6, 'intensity': 0.8}],
                           'fog': {'color': [0.6, 0.38, 0.32], 'density': 0.012}}},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(ghost_town().save(os.path.join(HERE, 'ghost_town.json')))

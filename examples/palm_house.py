"""Palm house: a Victorian glasshouse full of palms - white cast iron and glass, the sun pouring in through
the roof onto tree ferns and banana plants, a fountain under the ridge, a path of encaustic tiles; and the
view back toward the garden through the glass.

Shows the glasshouse kit (scripts/glasshouse.py): walls of `glasshouse` (open panes in white iron frames,
see-through, so the garden shows through), a floor of `encaustic` tiles; the roof of glass in 3D (a
`gable_roof` with `"cover": "glass"` and glass `ends` - drawn as glass, so the sky shows through and the
sun comes in under it, for no cell is roofed); slender columns of painted iron (`column` objects of
`iron_white`) and ribs across under the roof (`beam`s); palms, tree ferns, banana plants, monstera,
heliconia and ferns in beds either side, a `fountain`, a macaw. (Seen from outside, walls of open panes
read as a cage: shoot a glasshouse from inside.)
Run:  python palm_house.py  -> writes palm_house.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402


def palm_house():
    g = Grid(24, 34, fill='o')                     # the garden round it
    g.rect(6, 5, 17, 24, 'G')                      # the glasshouse's walls of glass...
    g.rect(7, 6, 16, 23, 'b')                      # ...its beds of soil inside...
    g.rect(11, 6, 12, 24, 't')                     # ...the tiled path down the middle, out of the door
    g.rect(8, 14, 15, 15, 't')                     # and across it at the fountain
    g.rect(11, 25, 12, 33, 'p')                    # the gravel path through the garden
    objects = [
        # the roof of glass, on the walls; iron columns down both sides of the path; ribs across under the roof
        {'type': 'gable_roof', 'x': 11.5 + 0.5, 'y': 14.5 + 0.5, 'z': 2.2, 'angle': 90, 'length': 20.0, 'width': 12.0,
         'rise': 2.8, 'cover': 'glass', 'ends': 'glass', 'overhang': [0.15, 0.1], 'seed': 2},
    ]
    for k, y in enumerate((8.0, 11.5, 18.5, 22.0)):
        for x in (10.4, 13.6):
            objects.append({'type': 'column', 'x': x, 'y': y, 'material': 'iron_white', 'sides': 8, 'radius': 0.07,
                            'height': 2.2, 'base': 0.14, 'capital': 0.1, 'sink': 0.0, 'fill': 0.8, 'seed': 10 * k + int(x)})
    for k, y in enumerate(range(7, 24, 3)):
        objects.append({'type': 'beam', 'x': 12.0, 'y': y + 0.5, 'z': 2.12, 'angle': 0, 'length': 12.0, 'width': 0.06,
                        'depth': 0.08, 'material': 'iron_white', 'fill': 0.8, 'seed': 40 + k})
    sprites = [
        # the fountain under the ridge, a bench by it
        {'x': 12.0, 'y': 15.0, 'type': 'fountain', 'scale': 1.0},
        {'x': 14.4, 'y': 15.4, 'type': 'bench', 'scale': 0.36},
        # the palms and the tree ferns, under the roof
        {'x': 8.6, 'y': 8.4, 'type': 'palm', 'scale': 4.4}, {'x': 15.4, 'y': 9.6, 'type': 'palm', 'scale': 4.6, 'flip': True},
        {'x': 8.4, 'y': 19.8, 'type': 'palm', 'scale': 4.2, 'flip': True}, {'x': 15.6, 'y': 21.0, 'type': 'palm_lean', 'scale': 3.8},
        {'x': 9.6, 'y': 16.2, 'type': 'palm', 'scale': 4.8}, {'x': 14.6, 'y': 13.4, 'type': 'palm_lean', 'scale': 4.2, 'flip': True},
        {'x': 9.0, 'y': 12.6, 'type': 'tree_fern', 'scale': 2.2}, {'x': 15.0, 'y': 18.0, 'type': 'tree_fern', 'scale': 2.4, 'flip': True},
        {'x': 7.8, 'y': 16.6, 'type': 'banana_plant'}, {'x': 16.0, 'y': 12.4, 'type': 'banana_plant', 'flip': True},
        {'x': 9.6, 'y': 22.4, 'type': 'banana_plant', 'scale': 1.5},
        # the understorey along the path
        *[{'x': x, 'y': y, 'type': t, 'flip': (k % 2) == 1} for k, (x, y, t) in enumerate((
            (10.2, 7.0, 'monstera'), (13.8, 7.4, 'heliconia'), (10.3, 10.2, 'fern'), (13.7, 10.8, 'monstera'),
            (10.2, 13.0, 'heliconia'), (13.8, 13.2, 'fern'), (10.3, 17.2, 'monstera'), (13.7, 16.8, 'heliconia'),
            (10.2, 20.4, 'fern'), (13.8, 20.2, 'monstera'), (10.3, 23.2, 'heliconia'), (13.7, 23.4, 'fern'),
            (8.2, 10.6, 'fern'), (15.8, 15.0, 'monstera'), (8.0, 23.0, 'monstera'), (16.0, 6.8, 'fern')))],
        {'x': 10.3, 'y': 14.6, 'type': 'bromeliad'}, {'x': 13.7, 'y': 15.6, 'type': 'bromeliad'},
        # people, and a macaw on a rib
        {'id': 'gardener', 'x': 13.6, 'y': 19.6, 'type': 'farmer', 'facing': 200},
        {'id': 'visitor', 'x': 11.6, 'y': 17.4, 'type': 'child', 'facing': 270},
        {'x': 11.0, 'y': 12.55, 'type': 'macaw', 'z': 2.12},
        # the garden outside
        {'x': 3.0, 'y': 8.0, 'type': 'tree', 'scale': 3.4}, {'x': 21.0, 'y': 12.0, 'type': 'tree', 'scale': 3.0, 'flip': True},
        {'x': 2.6, 'y': 22.0, 'type': 'birch'}, {'x': 21.4, 'y': 26.0, 'type': 'tree', 'scale': 3.2},
        {'x': 9.0, 'y': 28.0, 'type': 'flowers'}, {'x': 14.6, 'y': 27.4, 'type': 'flowers'},
        {'x': 9.6, 'y': 30.4, 'type': 'bush'}, {'x': 14.4, 'y': 30.8, 'type': 'bush', 'flip': True},
    ]
    return scene(
        g,
        legend={
            'o': {'floor': 'grass'},
            'G': {'wall': ['glasshouse', 'glasshouse'], 'h': 2.2},
            'b': {'floor': 'jungle_floor'},
            't': {'floor': 'encaustic'},
            'p': {'floor': 'gravel'},
        },
        title='Palm house - the glasshouse full of palms',
        sky='day',
        ambient=[0.42, 0.44, 0.4],
        fog={'color': [0.82, 0.88, 0.8], 'density': 0.012, 'sky_mix': 0.2},
        lights=[{'type': 'sun', 'azimuth': 120, 'elevation': 48, 'color': [1.0, 0.95, 0.84], 'intensity': 1.1}],
        sprites=sprites,
        objects=objects,
        scatter=[{'of': ['grass_tuft', 'grass_tuft', 'flowers'], 'on': 'o', 'density': 0.08, 'sizes': ['tiny', 'small'],
                  'seed': 3}],
        camera={'x': 11.9, 'y': 23.4, 'look_at': [12.0, 6.0, 1.4], 'fov': 70},
        shots=[
            {'x': 11.9, 'y': 23.4, 'look_at': [12.0, 6.0, 1.4], 'fov': 70,
             'overlays': [{'type': 'caption', 'text': 'The palm house', 'at': 'top', 'box': True}]},
            {'x': 12.4, 'y': 19.2, 'height': 0.5, 'look_at': [12.0, 12.0, 2.5], 'fov': 74},
            {'x': 12.6, 'y': 7.2, 'look_at': [11.6, 18.0, 1.6], 'fov': 72},   # from the far end, back toward the door
        ],
        contact_shadows=0.45,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(palm_house().save(os.path.join(HERE, 'palm_house.json')))

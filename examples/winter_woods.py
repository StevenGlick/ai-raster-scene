"""Winter woods: a lane through a snowbound wood, a frozen stream under a plank footbridge, a deer
on the ice - by a low winter sun, in falling snow at dusk, and by moonlight with a lantern on
the bridge.

Shows the `forest_snow` fringe - snowy spruces, bare oaks and birches with snow along their
limbs and bushes buried in it - in front of `forest_deep_snow` walls, `snow` drifts underfoot, a
frozen stream (`ice` sunk with `drop`, its banks of snow), a footbridge of low `planks` blocks,
`tree_winter` and `birch_winter` standing free, `boulder`s of `snow` rock (snow lying on every face
that is near level), a `deer`, a snowman; and the `snow` post effect.
Run:  python winter_woods.py  -> writes winter_woods.json next to this file.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

SUN = {'type': 'sun', 'azimuth': 200, 'elevation': 11, 'intensity': 1.0}
WARM = [1.0, 0.66, 0.34]


def winter_woods():
    g = Grid(36, 40, fill='F')                     # the wood everywhere; the lane and the stream cut out
    g.rect(14, 22, 21, 39, ',')                    # the lane, south
    g.disc(17, 18, 8, ',')                         # a clearing where the stream crosses
    g.rect(14, 3, 21, 14, ',')                     # the lane, on north into the trees
    g.rect(4, 17, 31, 19, '~')                     # the frozen stream, west to east across the clearing
    for x in range(4, 32):
        if g.get(x, 16) == 'F':
            g.put(x, 16, ',')
        if g.get(x, 20) == 'F':
            g.put(x, 20, ',')
    g.rect(17, 17, 18, 19, 'B')                    # the footbridge
    sprites = [
        # trees standing free in the clearing and along the lane
        {'x': 11.6, 'y': 21.6, 'type': 'tree_winter', 'scale': 3.0},
        {'x': 23.4, 'y': 14.6, 'type': 'tree_winter', 'flip': True},
        {'x': 14.8, 'y': 27.0, 'type': 'birch_winter'}, {'x': 21.2, 'y': 25.4, 'type': 'birch_winter', 'flip': True},
        {'x': 21.4, 'y': 33.0, 'type': 'snowy_pine'}, {'x': 14.6, 'y': 35.4, 'type': 'snowy_pine', 'flip': True},
        {'x': 24.6, 'y': 21.6, 'type': 'snowy_pine', 'scale': 2.6},
        {'x': 10.6, 'y': 14.4, 'type': 'birch_winter'},
        {'x': 15.0, 'y': 31.0, 'type': 'bush_snow'}, {'x': 21.0, 'y': 29.4, 'type': 'bush_snow', 'flip': True},
        {'x': 12.2, 'y': 15.6, 'type': 'bush_snow'},
        # the stream: the deer on the ice, reeds frozen in it
        {'id': 'deer', 'x': 22.6, 'y': 18.3, 'type': 'deer', 'flip': True},
        {'x': 9.0, 'y': 19.6, 'type': 'reeds'}, {'x': 27.4, 'y': 17.2, 'type': 'reeds'},
        # the lane: a snowman, a child, a sledge of logs
        {'x': 19.6, 'y': 28.2, 'type': 'snowman'},
        {'id': 'child', 'x': 18.4, 'y': 28.8, 'type': 'child', 'facing': 270},
        {'x': 15.6, 'y': 23.2, 'type': 'log'},
    ]
    night = [{'x': 18.6, 'y': 19.2, 'type': 'lantern', 'z': 0.34}]
    night_lights = [{'x': 18.6, 'y': 19.4, 'z': 0.5, 'radius': 4.0, 'color': WARM, 'intensity': 1.4}]
    return scene(
        g,
        legend={
            'F': {'wall': 'forest_deep_snow', 'h': 2.4, 'top': 'snow', 'fringe': 'forest_snow'},
            ',': {'floor': 'snow'},
            '~': {'floor': 'ice', 'drop': 0.08, 'reflect': 0.3, 'side': 'snow'},
            'B': {'wall': 'planks', 'h': 0.14, 'top': 'planks'},
        },
        title='Winter woods - the frozen stream and the footbridge',
        sky='day',
        ambient=[0.36, 0.4, 0.5],
        fog={'color': [0.78, 0.82, 0.9], 'density': 0.01, 'ground': 0.06, 'height': 0.3, 'noise': 0.5,
             'shafts': 0.5, 'anisotropy': 0.3},
        lights=[SUN],
        sprites=sprites,
        objects=[{'type': 'boulder', 'x': x, 'y': y, 'angle': a, 'size': s_, 'height': h_, 'rock': 'snow', 'seed': 40 + k}
                 for k, (x, y, a, s_, h_) in enumerate((                     # boulders capped with snow
                     (24.6, 16.2, 120, 1.0, 0.55), (15.9, 33.0, 20, 0.9, 0.5), (20.5, 35.2, 200, 0.7, 0.4),
                     (13.4, 21.4, 80, 1.1, 0.6), (21.8, 14.2, 160, 0.9, 0.5), (19.2, 9.8, 300, 0.8, 0.45)))],
        scatter=[{'of': 'snow', 'on': ',', 'density': 0.12, 'sizes': {'tiny': 3, 'small': 2}, 'seed': 5}],
        camera={'x': 17.6, 'y': 38.0, 'angle': 270, 'fov': 66, 'height': 0.5},
        shots=[
            {'x': 17.6, 'y': 38.0, 'angle': 270,
             'overlays': [{'type': 'caption', 'text': 'The first snow', 'at': 'top', 'box': True}]},
            {'x': 20.6, 'y': 22.4, 'look_at': 'deer', 'fov': 52, 'height': 0.45,
             'overrides': {'sky': 'overcast', 'ambient': [0.36, 0.38, 0.46], 'lights': [],
                           'fog': {'color': [0.66, 0.7, 0.78], 'density': 0.03}},
             'post': [{'fx': 'snow', 'count': 260, 'size': 1, 'wind': 0.25, 'opacity': 0.6}]},
            {'x': 17.6, 'y': 31.6, 'angle': 272, 'extra_sprites': night,
             'overlays': [{'type': 'bubble', 'anchor': 'child', 'text': 'Do you think the deer gets cold?'}],
             'overrides': {'sky': 'night', 'ambient': [0.1, 0.12, 0.2],
                           'lights': [{'type': 'moon', 'azimuth': 230, 'elevation': 30, 'intensity': 0.55}] + night_lights,
                           'fog': {'color': [0.06, 0.08, 0.14], 'density': 0.02, 'glow': 0.8}}},
            {'x': 9.0, 'y': 18.0, 'look_at': [26.0, 17.0, 0.9], 'fov': 64, 'height': 0.4},
        ],
        contact_shadows=0.5,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(winter_woods().save(os.path.join(HERE, 'winter_woods.json')))

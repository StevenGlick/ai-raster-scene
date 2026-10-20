"""Night market: a lane of the neon city given over to stalls after dark, in the rain.

Shows the market kit (scripts/market.py) between `neon` facades: a `food_cart` with its wok over
the flame and `steam` over its pots, `stools_table`s pulled up to it, a `fruit_stall` and a
`gadget_stall` under their tarps, `lantern_span`s of red paper lanterns slung across the lane and
single `red_lantern`s at the stalls, `power_pole`s hung with cables, `scooter`s parked along the
fronts, a standing `neon_sign` at the mouth of a side alley, a `crowd` filling the far end, the
`runner` under a clear `umbrella` with a lit shaft and a `samurai` under another. Every stall carries a warm light of its own,
so the wet flagstones mirror the market back.
Run:  python night_market.py  -> writes night_market.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 34, 46
g = Grid(W, H, fill='N')
g.rect(11, 6, 20, H - 1, 's')                         # the lane
g.rect(21, 21, 28, 24, 's')                           # a side alley off it

PINK, CYAN, GOLD, VIOLET = [1.0, 0.3, 0.7], [0.3, 0.9, 1.0], [1.0, 0.75, 0.3], [0.7, 0.45, 1.0]
WARM, RED = [1.0, 0.72, 0.42], [1.0, 0.32, 0.18]
RAIN = [{'fx': 'rain', 'density': 0.75, 'length': 8, 'opacity': 0.24, 'angle': 8}, {'fx': 'splashes', 'density': 0.25},
        {'fx': 'bloom', 'source': 'light', 'strength': 2.4, 'radius': 2.5, 'spread': 0.6},
        {'fx': 'grade', 'saturation': 1.12, 'tint': [1.03, 0.95, 1.04]}]

# stalls down both sides: (x, y, kind, flip); every stall gets a warm light and a lantern
stalls = [(12.75, 40.5, 'food_cart', False), (19.25, 37.5, 'fruit_stall', True), (12.75, 33.5, 'gadget_stall', False),
          (19.25, 30.0, 'food_cart', True), (12.75, 26.5, 'fruit_stall', False), (19.25, 17.5, 'gadget_stall', True),
          (12.75, 15.5, 'food_cart', False), (19.25, 11.5, 'fruit_stall', True), (12.75, 9.5, 'gadget_stall', False)]
sprites = []
lights = []
for x, y, kind, flip in stalls:
    sprites.append({'x': x, 'y': y, 'type': kind, 'flip': flip})
    side = 1 if x < 15 else -1
    sprites.append({'x': x + side * 0.45, 'y': y + 0.3, 'type': 'red_lantern', 'z': 0.8})
    lights.append({'x': x + side * 0.6, 'y': y, 'z': 0.9, 'radius': 2.6, 'color': WARM, 'intensity': 1.0})
    if kind == 'food_cart':
        sprites.append({'x': x + side * 0.15, 'y': y - 0.25, 'type': 'steam', 'z': 0.62, 'scale': 0.7})
        sprites.append({'x': x + side * 1.4, 'y': y + 0.4, 'type': 'stools_table', 'flip': flip})
# lanterns slung across the lane, and the light they throw
for y, z in ((42.0, 2.5), (36.0, 2.7), (30.5, 2.45), (25.0, 2.65), (19.5, 2.5), (14.0, 2.7), (9.0, 2.5)):
    sprites.append({'x': 15.5, 'y': y, 'type': 'lantern_span', 'angle': 0, 'length': 10.0, 'z': z, 'scale': 0.6})
    lights.append({'x': 15.5, 'y': y, 'z': z - 0.2, 'radius': 3.5, 'color': RED, 'intensity': 0.55})
sprites += [
    {'x': 12.3, 'y': 37.0, 'type': 'power_pole'}, {'x': 19.7, 'y': 26.0, 'type': 'power_pole', 'flip': True},
    {'x': 12.3, 'y': 20.0, 'type': 'power_pole'},
    {'x': 19.4, 'y': 42.6, 'type': 'scooter', 'flip': True}, {'x': 19.4, 'y': 34.0, 'type': 'scooter'},
    {'x': 12.6, 'y': 29.8, 'type': 'scooter', 'tint': [1.0, 0.75, 0.75]},
    {'x': 20.35, 'y': 22.3, 'type': 'neon_sign'}, {'x': 20.35, 'y': 23.7, 'type': 'neon_sign', 'flip': True},
    {'x': 14.2, 'y': 8.2, 'type': 'crowd'}, {'x': 17.2, 'y': 7.4, 'type': 'crowd', 'flip': True},
    {'x': 15.6, 'y': 12.4, 'type': 'crowd', 'scale': 0.64},
    {'x': 25.0, 'y': 23.0, 'type': 'crowd', 'scale': 0.6, 'flip': True},
    {'id': 'cook', 'x': 13.45, 'y': 40.05, 'type': 'shopkeeper', 'facing': 160},
    {'id': 'cook2', 'x': 19.25, 'y': 29.5, 'type': 'shopkeeper', 'facing': 90},
    {'id': 'runner', 'x': 15.2, 'y': 37.2, 'type': 'runner', 'facing': 75},
    {'x': 15.2, 'y': 37.15, 'type': 'umbrella', 'z': 0.33},
    {'x': 14.1, 'y': 41.3, 'type': 'cowboy', 'facing': 250},
    {'x': 16.0, 'y': 26.2, 'type': 'crowd', 'scale': 0.62}, {'x': 14.6, 'y': 19.8, 'type': 'crowd', 'scale': 0.62, 'flip': True},
    {'id': 'samurai', 'x': 16.8, 'y': 31.6, 'type': 'samurai', 'facing': 100},
    {'x': 16.82, 'y': 31.55, 'type': 'umbrella', 'z': 0.35, 'scale': 0.4},
    {'x': 14.0, 'y': 24.0, 'type': 'child', 'facing': 260},
    {'x': 17.6, 'y': 20.5, 'type': 'scientist', 'facing': 90},
    {'x': 17.65, 'y': 20.45, 'type': 'umbrella', 'z': 0.33, 'scale': 0.4},
    {'x': 13.2, 'y': 34.6, 'type': 'barrel'}, {'x': 18.8, 'y': 43.6, 'type': 'sci_crate'},
]
glows = [(12.2, 43.0, PINK), (19.8, 39.5, CYAN), (12.2, 31.0, VIOLET), (19.8, 27.0, PINK), (12.2, 22.5, CYAN),
         (19.8, 16.0, GOLD), (12.2, 12.0, PINK), (19.8, 8.0, VIOLET), (24.0, 23.0, PINK)]
lights += [{'x': x, 'y': y, 'z': 2.2, 'radius': 4.0, 'color': c, 'intensity': 1.0} for x, y, c in glows]
lights += [{'x': 20.6, 'y': y, 'z': 1.0, 'radius': 2.5, 'color': PINK, 'intensity': 1.0} for y in (22.3, 23.7)]
lights += [{'x': 15.2, 'y': 37.3, 'z': 0.7, 'radius': 1.4, 'color': [0.5, 1.0, 0.95], 'intensity': 1.2},    # the umbrellas
           {'x': 17.0, 'y': 31.9, 'z': 0.7, 'radius': 1.3, 'color': [0.5, 1.0, 0.95], 'intensity': 1.1}]

s = scene(
    g,
    title='Night market - a lane of stalls in the rain',
    legend={
        'N': {'wall': 'brick_dark', 'h': 3.0,
              'facade': {'style': 'neon', 'storeys': [2, 5], 'widths': [2, 3], 'lit': 0.65, 'shops': 0.8, 'seed': 23}},
        's': {'floor': 'flagstone'},
    },
    sky='night',
    skyline='city',
    ambient=[0.11, 0.1, 0.14],
    wet=0.85,
    fog={'color': [0.06, 0.05, 0.08], 'density': 0.02, 'glow': 1.2},
    lights=lights,
    sprites=sprites,
    decals=[{'tex': 'puddle_shine', 'surface': 'floor', 'x': x, 'y': y, 'size': s_}
            for x, y, s_ in ((15.0, 39.0, 1.8), (16.4, 33.0, 1.4), (14.6, 27.5, 1.6), (16.0, 22.0, 1.2),
                             (15.2, 16.0, 1.6))] +
           [{'tex': 'drain', 'surface': 'floor', 'x': x, 'y': y, 'size': 0.7} for x, y in ((15.5, 35.0), (15.5, 21.0))],
    camera={'x': 15.6, 'y': 45.2, 'look_at': [15.5, 8.0, 1.3], 'fov': 66},
    shots=[
        {'x': 15.6, 'y': 45.2, 'look_at': [15.5, 8.0, 1.3], 'fov': 66, 'post': RAIN,
         'overlays': [{'type': 'caption', 'text': 'Night market, the lower city', 'at': 'top', 'box': True}]},
        {'x': 15.0, 'y': 43.6, 'look_at': [12.9, 40.3, 0.6], 'fov': 62, 'post': RAIN},
        {'x': 16.2, 'y': 44.6, 'look_at': [15.6, 30.0, 0.9], 'fov': 70, 'height': 0.14, 'post': RAIN},
        {'x': 16.6, 'y': 39.4, 'look_at': 'runner', 'fov': 56, 'post': RAIN,
         'overlays': [{'type': 'bubble', 'anchor': 'runner', 'name': 'Runner',
                       'text': 'Two bowls, extra chilli. Then we find your man.'}]},
        {'x': 16.3, 'y': 33.1, 'look_at': 'samurai', 'fov': 48, 'post': [{'fx': 'dof', 'blur': 2.5}] + RAIN},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'night_market.json')))

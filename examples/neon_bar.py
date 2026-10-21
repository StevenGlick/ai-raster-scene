"""Neon bar: a low room in the lower city, a bar in front of glowing shelves, a reef tank let into the
back wall, a row of arcade cabinets, booths, a jukebox, neon on the walls and smoke in the air.

Shows the bar kit (scripts/bar.py) with the aquarium's: `bar_shelves` on the wall behind the bar,
the bar itself a `bar_counter` card standing along it with `bar_stool`s in front and `bottles`
on top, `arcade_cabinet`s with a shooter on every screen, `booth`s, a `jukebox`, the `hacker` by the arcade row, `neon_cocktail`
and `neon_fish` on the walls (additive); and a reef tank done as the aquarium's are, small: its back
wall painted as open water (`deep_water` under `open_water`, dimmed for the bar), a low `rock_wall` of
`reef` rock along its foot and one small `boulder`, `reef_rock`, corals and reef fish in front, behind
a `glass_pane` whose glass has `fog`, so the haze glows blue inside it. A thick, glowing
volumetric fog is the smoke: every screen, tube and lamp gets a halo in it.
Run:  python neon_bar.py  -> writes neon_bar.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 9, 10
g = Grid(W, H, fill='#')
g.rect(1, 4, 6, 8, 'f')                              # the room
g.rect(1, 3, 3, 3, 'K')                              # the back bar's shelves
g.rect(4, 2, 7, 3, 'R')                              # the reef tank, let into the back wall
g.rect(5, 3, 6, 3, 'A')
g.rect(5, 2, 6, 2, 'O')                              # its back wall: painted as open water

PINK, CYAN, VIOLET, WARM = [1.0, 0.3, 0.7], [0.3, 0.9, 1.0], [0.65, 0.45, 1.0], [1.0, 0.72, 0.42]
BLOOM = [{'fx': 'bloom', 'source': 'light', 'strength': 2.0, 'radius': 2.5, 'spread': 0.6}]
water = {'tint': [0.62, 0.88, 1.0], 'opacity': 0.08, 'blur': 0, 'fog': True}
sprites = [
    {'x': 6.0, 'y': 4.0, 'type': 'glass_pane', 'angle': 0, 'length': 2.0, 'scale': 1.3, 'glass': water},
    {'x': 2.5, 'y': 4.95, 'type': 'bar_counter', 'angle': 0, 'length': 3.0},
    {'x': 1.4, 'y': 4.92, 'type': 'bottles', 'z': 0.35}, {'x': 3.5, 'y': 4.92, 'type': 'bottles', 'z': 0.35, 'flip': True},
    {'id': 'bartender', 'x': 2.3, 'y': 4.55, 'type': 'android', 'facing': 90},
] + [{'x': x, 'y': 5.3, 'type': 'bar_stool'} for x in (1.5, 2.2, 2.9, 3.6)] + [
    {'id': 'stranger', 'x': 3.25, 'y': 5.45, 'type': 'cowboy', 'facing': 280},
] + [{'x': 6.55, 'y': y, 'type': 'arcade_cabinet', 'flip': k % 2 == 1, 'tint': t}
     for k, (y, t) in enumerate(((5.1, [1.0, 1.0, 1.0]), (5.95, [0.75, 0.9, 1.1]), (6.8, [1.1, 0.85, 0.85]),
                                 (7.65, [0.9, 1.05, 0.9])))] + [
    {'id': 'player', 'x': 6.05, 'y': 6.0, 'type': 'runner', 'facing': 0},
    {'x': 1.45, 'y': 6.6, 'type': 'booth'}, {'x': 1.45, 'y': 7.9, 'type': 'booth'},
    {'id': 'regular', 'x': 5.75, 'y': 7.15, 'type': 'hacker', 'facing': 120},
    {'x': 1.3, 'y': 5.6, 'type': 'jukebox'},
    {'x': 1.05, 'y': 6.0, 'type': 'neon_cocktail', 'z': 0.62},
    {'x': 6.95, 'y': 4.5, 'type': 'neon_fish', 'z': 0.8},
    {'x': 4.6, 'y': 4.2, 'type': 'witch', 'facing': 270, 'tint': [0.5, 0.55, 0.7]},
    # the tank: live rock near the glass, in front of the rockwork along its back
    {'x': 5.4, 'y': 3.55, 'type': 'reef_rock', 'scale': 0.4}, {'x': 6.6, 'y': 3.6, 'type': 'reef_rock', 'scale': 0.36, 'flip': True},
    {'x': 5.1, 'y': 3.7, 'type': 'sea_fan', 'scale': 0.4}, {'x': 6.8, 'y': 3.75, 'type': 'staghorn_coral', 'scale': 0.24},
    {'x': 6.0, 'y': 3.75, 'type': 'anemone', 'scale': 0.2}, {'x': 5.6, 'y': 3.85, 'type': 'brain_coral', 'scale': 0.13},
    {'x': 6.4, 'y': 3.85, 'type': 'tube_sponge', 'scale': 0.2},
    {'x': 5.9, 'y': 3.45, 'type': 'reef_shoal', 'z': 0.55, 'scale': 0.36},
    {'x': 6.3, 'y': 3.6, 'type': 'angelfish', 'z': 0.42, 'scale': 0.13},
    {'x': 5.5, 'y': 3.6, 'type': 'blue_tang', 'z': 0.7, 'scale': 0.08, 'flip': True},
    {'x': 6.1, 'y': 3.2, 'type': 'moon_jelly', 'z': 0.9, 'scale': 0.1},
]
lights = (
    [{'x': x, 'y': 4.9, 'z': 1.15, 'radius': 1.5, 'color': WARM, 'intensity': 1.0} for x in (1.5, 2.5, 3.5)]
    + [{'x': x, 'y': 3.7, 'z': 0.5, 'radius': 1.3, 'color': PINK, 'intensity': 0.8} for x in (1.5, 3.2)]
    + [{'x': 6.0, 'y': 3.4, 'z': 1.1, 'radius': 1.8, 'color': [0.75, 0.9, 1.0], 'intensity': 1.5}]
    + [{'x': 6.2, 'y': y, 'z': 0.55, 'radius': 1.1, 'color': c, 'intensity': 1.0}
       for y, c in ((5.1, VIOLET), (5.95, CYAN), (6.8, PINK), (7.65, CYAN))]
    + [{'x': 1.6, 'y': 5.6, 'z': 0.5, 'radius': 1.3, 'color': [1.0, 0.6, 0.3], 'intensity': 1.0},
       {'x': 1.5, 'y': 6.0, 'z': 0.7, 'radius': 1.2, 'color': PINK, 'intensity': 0.9},
       {'x': 6.6, 'y': 4.5, 'z': 0.8, 'radius': 1.3, 'color': CYAN, 'intensity': 0.9},
       {'x': 1.6, 'y': 7.0, 'z': 0.4, 'radius': 1.0, 'color': WARM, 'intensity': 0.7},
       {'x': 1.6, 'y': 8.3, 'z': 0.4, 'radius': 1.0, 'color': WARM, 'intensity': 0.7}])

s = scene(
    g,
    title='Neon bar - smoke, a reef tank and the arcade row',
    legend={
        '#': {'wall': 'brick_dark', 'h': 1.3},
        'K': {'wall': 'bar_shelves', 'h': 1.3},
        'R': {'wall': 'reef_wall', 'h': 1.3},
        'O': {'wall': [{'base': 'deep_water', 'brightness': 0.62}, {'base': 'open_water', 'brightness': 0.62}], 'h': 1.3},
        'A': {'floor': 'seabed', 'ceil': {'base': 'water_surface', 'tint': [0.55, 0.72, 0.82]}},
        'f': {'floor': 'obsidian', 'ceil': 'concrete'},
    },
    ceiling_height=1.3,
    sky=None,
    ambient=[0.09, 0.07, 0.11],
    fog={'color': [0.05, 0.03, 0.07], 'density': 0.06, 'glow': 1.2},
    lights=lights,
    sprites=sprites,
    objects=[{'type': 'rock_wall', 'lining': 'O', 'rock': 'reef', 'depth': 0.3, 'height': [0.24, 0.5],
              'pieces': [0.8, 1.3], 'plants': False, 'seed': 3},                      # live rock along the tank's back
             {'type': 'boulder', 'x': 6.45, 'y': 3.42, 'angle': 90, 'size': 0.34, 'height': 0.2, 'rock': 'reef',
              'seed': 5}],
    camera={'x': 6.2, 'y': 8.6, 'look_at': [2.4, 4.3, 0.5], 'fov': 74},
    shots=[
        {'x': 6.2, 'y': 8.6, 'look_at': [2.4, 4.3, 0.5], 'fov': 74, 'post': BLOOM,
         'overlays': [{'type': 'caption', 'text': 'The Blue Lantern, past two', 'at': 'top', 'box': True}]},
        {'x': 5.2, 'y': 5.7, 'look_at': [6.0, 3.4, 0.55], 'fov': 64, 'post': BLOOM},
        {'x': 4.4, 'y': 7.9, 'look_at': [6.55, 6.0, 0.4], 'fov': 66, 'post': BLOOM},
        {'x': 2.6, 'y': 6.3, 'look_at': 'bartender', 'fov': 56, 'post': BLOOM,
         'overlays': [{'type': 'dialog', 'portrait': 'android', 'name': 'Bartender',
                       'text': 'Your man was in an hour ago. Sat by the fish. Paid in real money.'}]},
        {'x': 4.85, 'y': 8.45, 'look_at': 'regular', 'fov': 52, 'post': [{'fx': 'dof', 'blur': 2.0}] + BLOOM,
         'overlays': [{'type': 'bubble', 'anchor': 'regular', 'name': 'Hacker',
                       'text': "Don't look at the screen. It looks back."}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'neon_bar.json')))

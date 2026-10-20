"""The aurora palace: a palace of ice on the shore of a frozen lake, under the aurora - curtains of green
light hanging across the arctic night, doubled in the ice. Towers of blue ice blocks crowned with
crystal spires, icicles along the walls, a gate into a courtyard, and an open hall walled in frost with
a throne cut from the ice; snowy pines on the shore and a traveller out on the lake.

Shows the ice-palace kit (scripts/icepalace.py): the `aurora` sky, `ice_block` walls and towers with an
`ice_spire` on each, `icicles` hung along the walls, a hall of `frost_wall` round an `ice_throne`,
`ice_floor` (polished, it reflects) and `ice_shards`; the lake a still mirror
(`"reflections": {"ripple": 0, "smear": 0}`), the aurora's green on the snow from a moon light with no
disc, and a light bloom so the curtains glow.
Run:  python aurora_palace.py  -> writes aurora_palace.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 48, 58
g = Grid(W, H, fill='n')                              # snow
g.rect(14, 4, 33, 18, 'I')                            # the palace walls...
g.rect(15, 5, 32, 17, 'c')                            # ...round a courtyard
for x0, y0 in ((13, 3), (32, 3), (13, 17), (32, 17)):
    g.rect(x0, y0, x0 + 2, y0 + 2, 'T')               # corner towers
g.rect(22, 18, 25, 18, 'c')                           # the gate
g.rect(19, 6, 28, 12, 'F')                            # the hall, walled in frost...
g.rect(20, 7, 27, 11, 'h')                            # ...open to the sky
g.rect(23, 12, 24, 12, 'h')                           # its door
for y in range(26, 54):                               # the frozen lake
    for x in range(4, 44):
        if ((x + 0.5 - 24) / 19.5) ** 2 + ((y + 0.5 - 40) / 13.5) ** 2 < 1:
            g.put(x, y, 'L')

ICE_TOP = {'base': 'snow', 'tint': [0.85, 0.92, 1.0]}
legend = {
    'n': {'floor': 'snow'},
    'c': {'floor': 'snow'},
    'h': {'floor': 'ice_floor', 'reflect': 0.45},
    'L': {'floor': 'ice_floor', 'reflect': 0.85},
    'I': {'wall': ['ice_block', 'ice_block', 'ice_block'], 'h': 2.4, 'top': ICE_TOP},
    'T': {'wall': ['ice_block'] * 4, 'h': 4.0, 'top': ICE_TOP},
    'F': {'wall': ['frost_wall', 'frost_wall'], 'h': 1.8, 'top': ICE_TOP},
}
sprites = [{'x': x, 'y': y, 'type': 'ice_spire', 'z': 4.0, 'scale': 2.8} for x, y in
           ((14.5, 4.5), (33.5, 4.5), (14.5, 18.5), (33.5, 18.5))]
sprites += [{'x': x, 'y': 19.04, 'type': 'icicles', 'angle': 0, 'length': 6.0, 'z': 2.0} for x in (18.0, 30.0)]
sprites += [{'x': 13.96, 'y': y, 'type': 'icicles', 'angle': 90, 'length': 6.0, 'z': 2.0} for y in (8.0, 14.0)]
sprites += [{'x': 34.04, 'y': y, 'type': 'icicles', 'angle': 90, 'length': 6.0, 'z': 2.0} for y in (8.0, 14.0)]
sprites += [{'id': 'throne', 'x': 23.5, 'y': 7.6, 'type': 'ice_throne', 'scale': 1.3},
            {'id': 'queen', 'x': 22.4, 'y': 8.6, 'type': 'witch', 'tint': [0.75, 0.85, 1.0], 'facing': 90},
            {'id': 'traveller', 'x': 25.0, 'y': 46.0, 'type': 'explorer', 'facing': 270}]
sprites += [{'x': x, 'y': y, 'type': 'ice_shards', 'flip': k % 2 == 1} for k, (x, y) in enumerate(
    ((17.0, 21.0), (30.5, 21.6), (9.5, 24.5), (38.5, 25.0), (20.6, 9.0), (26.6, 10.2)))]
sprites += [{'x': x, 'y': y, 'type': 'snowy_pine', 'scale': s} for x, y, s in
            ((5.0, 22.0, 2.6), (8.0, 19.0, 3.0), (41.0, 20.0, 2.8), (44.0, 24.0, 2.4), (2.5, 30.0, 2.8),
             (45.5, 33.0, 2.6), (3.0, 45.0, 2.4), (45.0, 47.0, 2.8), (10.0, 55.0, 2.6), (38.0, 55.5, 3.0))]
AURORA = {'type': 'moon', 'azimuth': 300, 'elevation': 40, 'intensity': 0.45, 'color': [0.45, 1.0, 0.75],
          'disc': False}
GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 3, 'spread': 0.6}
s = scene(
    g,
    title='The aurora palace - ice under the northern lights',
    legend=legend,
    sky='aurora',
    ambient=[0.14, 0.18, 0.24],
    lights=[AURORA,
            {'x': 23.5, 'y': 9.0, 'z': 1.2, 'radius': 4.0, 'color': [0.5, 0.8, 1.0], 'intensity': 0.7},
            {'x': 23.5, 'y': 19.5, 'z': 1.0, 'radius': 3.0, 'color': [0.5, 0.8, 1.0], 'intensity': 0.5}],
    fog={'color': [0.04, 0.08, 0.12], 'density': 0.008},
    reflections={'ripple': 0, 'smear': 0},
    sprites=sprites,
    camera={'x': 24.0, 'y': 55.0, 'look_at': [24.0, 10.0, 2.0], 'fov': 72},
    shots=[
        {'x': 24.0, 'y': 52.0, 'height': 0.4, 'look_at': [24.0, 11.0, 3.6], 'fov': 72, 'post': [GLOW],
         'overlays': [{'type': 'caption', 'text': 'The aurora palace', 'at': 'top', 'box': True}]},
        {'x': 23.5, 'y': 24.5, 'height': 0.45, 'look_at': [23.5, 12.0, 3.0], 'fov': 72, 'post': [GLOW]},
        {'x': 23.5, 'y': 11.4, 'height': 0.45, 'look_at': 'throne', 'fov': 62, 'post': [GLOW]},
        {'x': 14.0, 'y': 50.0, 'height': 0.35, 'look_at': [30.0, 36.0, 1.6], 'fov': 74, 'post': [GLOW]},
    ],
    contact_shadows=0.3,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aurora_palace.json')))

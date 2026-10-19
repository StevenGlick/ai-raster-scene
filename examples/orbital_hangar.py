"""Orbital hangar: a shuttle bay in high orbit, its control room and the reactor below it.

Shows the sci-fi hardware (scripts/scifi.py) in a scene of several rooms: a hangar with a
`shuttle` on a painted pad, stacked `cargo_container`s, a `power_loader` and `robot_arm`s, amber
`beacon`s with lights of their own and `cables_hang` from the ceiling; the far wall glazed between
steel mullions with real glass (the glass pass: space and a ringed planet behind it, tinted and
softly blurred); a control room of `screen_wall`s looking down the bay through its own window;
and a reactor room of `conduit` walls where a `reactor_core` glows through cyan haze under red
alarm lights. Volumetric fog gives every light a halo.
Run:  python orbital_hangar.py  -> writes orbital_hangar.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 40, 32
g = Grid(W, H, fill='#')
g.rect(0, 0, W - 1, 3, ' ')                          # space beyond the glass
g.rect(3, 4, 28, 18, 'h')                            # the hangar bay
for x in range(3, 30, 5):                            # steel mullions between the panes
    g.put(x, 3, 'M')
g.rect(3, 3, 28, 3, 'g')                             # the glazed line (panes stand here)
for x in range(3, 30, 5):
    g.put(x, 3, 'M')
g.rect(30, 6, 37, 12, 'k')                           # the control room
g.rect(29, 7, 29, 11, 'w')                           # its window onto the bay
for y in range(6, 13):
    g.put(38, y, 'S')
g.rect(30, 5, 37, 5, 'T')
g.rect(19, 19, 21, 27, 'c')                          # the corridor down to the reactor
g.rect(22, 25, 29, 27, 'c')
g.rect(30, 20, 37, 29, 'r')                          # the reactor room, walled in cable runs
g.rect(38, 20, 38, 29, 'C')
g.rect(30, 19, 37, 19, 'C')
g.rect(30, 30, 37, 30, 'C')
for y in (20, 21, 22, 23, 24, 28, 29):
    g.put(29, y, 'C')

cool = [0.78, 0.88, 1.0]
amber = [1.0, 0.62, 0.22]
cyan = [0.35, 0.9, 1.0]
red = [1.0, 0.22, 0.16]
planet = [1.0, 0.8, 0.6]
beacons = [(12.6, 7.8), (18.4, 7.8), (12.6, 13.2), (18.4, 13.2)]
panes = [{'x': x + 3.0, 'y': 3.5, 'type': 'glass_pane', 'angle': 0, 'length': 4.0, 'scale': 3.2,
          'glass': {'opacity': 0.14, 'blur': 1}} for x in range(3, 28, 5)]
window = [{'x': 29.5, 'y': 9.5, 'type': 'glass_pane', 'angle': 90, 'length': 5.0, 'scale': 1.6, 'z': 0.5,
           'glass': {'opacity': 0.2, 'blur': 1}}]

s = scene(
    g,
    title='Orbital hangar - bay 3, its control room and the reactor',
    legend={
        ' ': {'floor': 'void'},
        '#': {'wall': 'hull_dark', 'h': 3.6},
        'M': {'wall': 'hull', 'h': 3.6},
        'g': {'floor': 'void'},
        'h': {'floor': 'hangar_floor', 'ceil': 'panel'},
        'k': {'floor': 'deck', 'ceil': 'panel'},
        'w': {'floor': 'deck', 'ceil': 'panel'},
        'T': {'wall': ['screen_wall', 'hull_dark'], 'h': 3.6},
        'S': {'wall': ['screen_wall', 'hull_dark'], 'h': 3.6},
        'c': {'floor': 'grate', 'ceil': 'panel'},
        'r': {'floor': 'grate', 'ceil': 'panel'},
        'C': {'wall': ['conduit', 'conduit', 'hull_dark'], 'h': 3.6},
    },
    ceiling_height=3.6,
    sky='space',
    sky_objects=[
        {'type': 'ringed', 'azimuth': 268, 'elevation': 6, 'size': 16, 'color': [0.62, 0.74, 0.92],
         'color2': [0.86, 0.8, 0.7], 'lit_from': 200, 'phase': 0.65, 'tilt': 0.2, 'angle': 10},
        {'type': 'moon', 'azimuth': 300, 'elevation': 22, 'size': 2.0, 'lit_from': 200},
        {'type': 'sun', 'azimuth': 215, 'elevation': 14, 'size': 0.9},
    ],
    ambient=[0.12, 0.13, 0.17],
    fog={'color': [0.05, 0.06, 0.08], 'density': 0.012, 'glow': 0.8},
    lights=(
        [{'x': x, 'y': y, 'z': 3.3, 'radius': 7.0, 'color': cool, 'intensity': 0.9}
         for x, y in ((8, 8), (16, 8), (24, 8), (8, 15), (16, 15), (24, 15))]
        + [{'x': x, 'y': 4.4, 'z': 1.6, 'radius': 6.0, 'color': planet, 'intensity': 0.6} for x in (8, 16, 24)]
        + [{'x': x, 'y': y, 'z': 0.4, 'radius': 3.0, 'color': amber, 'intensity': 1.2} for x, y in beacons]
        + [{'x': 34, 'y': 9, 'z': 1.4, 'radius': 6.0, 'color': cyan, 'intensity': 0.9},
           {'x': 36.6, 'y': 9.5, 'z': 1.2, 'radius': 4.0, 'color': [0.5, 0.95, 0.8], 'intensity': 0.9},
           {'x': 31.2, 'y': 7.4, 'z': 0.9, 'radius': 2.5, 'color': [1.0, 0.8, 0.5], 'intensity': 0.8},
           {'x': 33.5, 'y': 24.5, 'z': 1.4, 'radius': 8.0, 'color': cyan, 'intensity': 1.8},
           {'x': 30.6, 'y': 21.0, 'z': 3.0, 'radius': 5.0, 'color': red, 'intensity': 1.1},
           {'x': 36.4, 'y': 28.0, 'z': 3.0, 'radius': 5.0, 'color': red, 'intensity': 1.1},
           {'x': 20.0, 'y': 23.0, 'z': 3.0, 'radius': 4.0, 'color': cool, 'intensity': 0.6}]),
    sprites=panes + window + [
        # the bay
        {'x': 15.5, 'y': 10.5, 'type': 'shuttle'},
        {'x': 4.8, 'y': 6.0, 'type': 'cargo_container'},
        {'x': 4.8, 'y': 6.0, 'type': 'cargo_container', 'z': 1.2, 'tint': [0.45, 0.7, 1.0]},
        {'x': 4.8, 'y': 9.2, 'type': 'cargo_container', 'tint': [0.5, 0.85, 0.55]},
        {'x': 4.8, 'y': 14.5, 'type': 'cargo_container'},
        {'x': 4.8, 'y': 14.5, 'type': 'cargo_container', 'z': 1.2, 'tint': [0.85, 0.85, 0.9]},
        {'x': 8.6, 'y': 12.0, 'type': 'power_loader'},
        {'x': 19.6, 'y': 8.6, 'type': 'robot_arm', 'flip': True}, {'x': 19.8, 'y': 12.6, 'type': 'robot_arm', 'flip': True},
        {'x': 9.0, 'y': 5.2, 'type': 'cables_hang', 'z': 2.2}, {'x': 23.0, 'y': 5.4, 'type': 'cables_hang', 'z': 2.2},
        {'x': 26.5, 'y': 16.5, 'type': 'cables_hang', 'z': 2.2, 'flip': True},
        {'x': 25.8, 'y': 15.0, 'type': 'sci_crate'}, {'x': 26.6, 'y': 15.4, 'type': 'sci_crate', 'scale': 0.28},
        {'x': 26.8, 'y': 11.0, 'type': 'cargo_container', 'tint': [0.55, 0.6, 0.66]},
        {'x': 26.8, 'y': 7.2, 'type': 'cargo_container', 'tint': [0.9, 0.55, 0.45], 'flip': True},
        {'x': 26.8, 'y': 7.2, 'type': 'cargo_container', 'z': 1.2, 'tint': [0.6, 0.8, 0.95]},
        {'x': 7.4, 'y': 16.8, 'type': 'sci_crate'}, {'x': 8.2, 'y': 17.1, 'type': 'sci_crate', 'scale': 0.3},
        {'x': 26.0, 'y': 6.0, 'type': 'drone', 'z': 1.4},
        {'id': 'pilot', 'x': 13.2, 'y': 13.8, 'type': 'astronaut', 'facing': 120},
        {'id': 'mechanic', 'x': 10.0, 'y': 13.0, 'type': 'android', 'facing': 30},
    ] + [{'x': x, 'y': y, 'type': 'beacon'} for x, y in beacons] + [
        # the control room
        {'x': 31.0, 'y': 7.0, 'type': 'console'}, {'x': 36.8, 'y': 7.0, 'type': 'console', 'flip': True},
        {'x': 33.6, 'y': 11.4, 'type': 'hologram', 'scale': 0.75},
        {'id': 'controller', 'x': 31.8, 'y': 9.6, 'type': 'scientist', 'facing': 180},
        # the reactor room
        {'x': 33.5, 'y': 24.5, 'type': 'reactor_core'},
        {'x': 30.8, 'y': 21.2, 'type': 'beacon', 'z': 2.6, 'tint': [1.0, 0.35, 0.3]},
        {'x': 36.2, 'y': 27.8, 'type': 'beacon', 'z': 2.6, 'tint': [1.0, 0.35, 0.3]},
        {'x': 31.2, 'y': 28.4, 'type': 'sci_crate'}, {'x': 36.6, 'y': 21.2, 'type': 'cables_hang', 'z': 2.2},
        {'id': 'tech', 'x': 32.2, 'y': 27.0, 'type': 'android', 'facing': 300},
    ],
    decals=[
        {'tex': 'pad_marking', 'surface': 'floor', 'x': 15.5, 'y': 10.5, 'size': 6.0},
        {'tex': 'hazard_stripe', 'surface': 'floor', 'x': 15.5, 'y': 4.6, 'size': 8.0},
        {'tex': 'hazard_stripe', 'surface': 'floor', 'x': 20.0, 'y': 18.4, 'size': 3.0},
        {'tex': 'stain_rust', 'surface': 'floor', 'x': 9.0, 'y': 15.5, 'size': 1.6, 'opacity': 0.6},
    ],
    camera={'x': 22.6, 'y': 16.4, 'look_at': [13.0, 5.6, 1.6], 'fov': 72},
    shots=[
        {'x': 22.6, 'y': 16.4, 'look_at': [13.0, 5.6, 1.6], 'fov': 72,
         'overlays': [{'type': 'caption', 'text': 'Bay 3, high orbit', 'at': 'top', 'box': True}]},
        {'x': 35.0, 'y': 10.4, 'look_at': [24.0, 8.6, 1.1], 'fov': 66},
        {'x': 30.6, 'y': 28.8, 'look_at': [33.5, 24.5, 1.4], 'fov': 72},
        {'x': 11.2, 'y': 16.8, 'look_at': 'pilot', 'fov': 62,
         'overrides': {'ui': {'theme': 'terminal'}},
         'overlays': [{'type': 'dialog', 'portrait': 'astronaut', 'name': 'Pilot',
                       'text': 'Fuel her up. We drop through the rings at the next crossing.'}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orbital_hangar.json')))

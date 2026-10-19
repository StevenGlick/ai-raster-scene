"""Space station: an observation deck over a ringed planet, reached down a lit corridor.

Shows the `space` sky, `sky_objects` (a ringed planet, a moon, a distant sun), void floors (space
outside the glass carries on below the horizon), a see-through `viewport` wall two storeys tall,
a polished obsidian floor reflecting the planet, and light-strip corridors.
Run:  python space_station.py  -> writes space_station.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

g = Grid(24, 26, fill='#')
g.rect(0, 0, 23, 2, ' ')                              # open space beyond the glass
g.rect(3, 3, 20, 3, 'V')                              # the viewport wall
g.rect(3, 4, 20, 12, 'o')                             # the observation deck
for y in range(4, 13):
    g.put(2, y, 'T' if y % 3 else 'S')                # instrument walls and server racks
    g.put(21, y, 'S' if y % 3 else 'T')
g.rect(11, 13, 12, 13, 'c')                           # the doorway
g.rect(10, 14, 10, 23, 'L')                           # corridor walls with light strips
g.rect(13, 14, 13, 23, 'L')
g.rect(11, 14, 12, 23, 'c')
g.rect(11, 24, 12, 24, 'B')                           # a blast door at the far end

cool = [0.65, 0.85, 1.0]
glow = [1.0, 0.78, 0.55]                              # the planet's light through the glass
s = scene(
    g,
    title='Space station - the observation deck',
    legend={
        ' ': {'floor': 'void'},
        '#': {'wall': 'hull_dark', 'h': 2.0},
        'V': {'wall': ['viewport', 'viewport'], 'h': 2.0, 'floor': 'obsidian', 'ceil': 'panel'},
        'T': {'wall': ['tech_panel', 'hull_dark'], 'h': 2.0},
        'S': {'wall': ['server', 'server'], 'h': 2.0},
        'o': {'floor': 'obsidian', 'ceil': 'panel'},
        'c': {'floor': 'deck', 'ceil': 'panel'},
        'L': {'wall': ['hull_lit', 'hull'], 'h': 2.0},
        'B': {'wall': ['blast_door', 'hull_dark'], 'h': 2.0},
    },
    ceiling_height=2.0,
    sky='space',
    sky_objects=[
        {'type': 'ringed', 'azimuth': 285, 'elevation': 8, 'size': 14, 'color': [0.86, 0.66, 0.46],
         'color2': [0.8, 0.72, 0.6], 'lit_from': 205, 'phase': 0.7, 'tilt': 0.22, 'angle': -12},
        {'type': 'moon', 'azimuth': 300, 'elevation': 26, 'size': 2.4, 'lit_from': 205},
        {'type': 'sun', 'azimuth': 228, 'elevation': 20, 'size': 1.0},
    ],
    ambient=[0.13, 0.14, 0.18],
    lights=[
        {'x': 11.5, 'y': 4.8, 'z': 1.0, 'radius': 8.0, 'color': glow, 'intensity': 1.0},
        {'x': 5.0, 'y': 4.8, 'z': 1.0, 'radius': 5.0, 'color': glow, 'intensity': 0.6},
        {'x': 18.0, 'y': 4.8, 'z': 1.0, 'radius': 5.0, 'color': glow, 'intensity': 0.6},
        {'x': 8.0, 'y': 10.2, 'z': 0.6, 'radius': 3.5, 'color': [0.4, 0.9, 1.0], 'intensity': 1.1},
        {'x': 3.6, 'y': 11.0, 'z': 0.7, 'radius': 3.0, 'color': [0.4, 1.0, 0.6], 'intensity': 0.6},
        {'x': 20.4, 'y': 7.0, 'z': 0.7, 'radius': 3.0, 'color': [0.4, 1.0, 0.6], 'intensity': 0.6},
    ] + [{'x': 11.5, 'y': y, 'z': 1.8, 'radius': 3.6, 'color': cool, 'intensity': 0.8} for y in (15.0, 18.5, 22.0)],
    sprites=[
        {'x': 8.0, 'y': 10.2, 'type': 'hologram', 'scale': 0.7},
        {'id': 'android', 'x': 13.6, 'y': 5.4, 'type': 'android'},
        {'id': 'astronaut', 'x': 9.0, 'y': 7.6, 'type': 'astronaut'},
        {'x': 3.4, 'y': 11.0, 'type': 'console'}, {'x': 20.6, 'y': 7.0, 'type': 'console'},
        {'x': 19.4, 'y': 11.6, 'type': 'sci_crate'}, {'x': 18.5, 'y': 11.9, 'type': 'sci_crate', 'scale': 0.28},
        {'x': 4.0, 'y': 4.6, 'type': 'sci_crate', 'scale': 0.3},
        {'x': 12.0, 'y': 18.0, 'type': 'drone', 'z': 1.05},
    ],
    camera={'x': 10.6, 'y': 9.2, 'look_at': [12.5, 3.5, 0.95], 'fov': 76},
    shots=[
        {'x': 10.6, 'y': 9.2, 'look_at': [12.5, 3.5, 0.95], 'fov': 76,
         'overlays': [{'type': 'caption', 'text': 'Observation deck, high orbit', 'at': 'top', 'box': True}]},
        {'x': 12.0, 'y': 23.4, 'look_at': [12.0, 4.0, 0.7], 'fov': 70},
        {'x': 5.4, 'y': 11.2, 'look_at': 'astronaut', 'fov': 64,
         'overrides': {'ui': {'theme': 'terminal'}},
         'overlays': [{'type': 'dialog', 'portrait': 'android', 'name': 'Station',
                       'text': 'Orbit stable. Ring crossing in eleven minutes.'}]},
    ],
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'space_station.json')))

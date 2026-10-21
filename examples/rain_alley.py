"""Rain alley: a downpour at night on a city street that runs up to a T-junction.

Shows building `facade`s: every front cut into separate buildings of different heights and
brick, each with real depth - windows set back in the wall, glass (the glass pass: what is
behind it, tinted and softly blurred), curtains and blinds behind the glass, and lit or dark
rooms behind those - plus depth-aware rain and splashes (the `downpour` preset), `wet` ground
mirroring the lamps and windows, a road sunk a kerb's height below the pavements, street-lamp
prefabs, volumetric fog with `glow` (every lamp gets a halo), lightning, a figure walking away
from the camera (`facing`), and `car` objects (scripts/objects.py) built in 3D out of panels -
parked along both kerbs, and one coming up the street with its headlamps on.
Run:  python rain_alley.py  -> writes rain_alley.json
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 44, 60
g = Grid(W, H, fill='B')                              # buildings everywhere, then the streets
# the cross street along the top, from one end of the map to the other
g.rect(0, 7, W - 1, 7, 'f')                           # the building fronts' cell on its far side
g.rect(0, 8, W - 1, 9, 's')                           # pavement
g.rect(0, 10, W - 1, 13, '~')                         # the road
g.rect(0, 14, W - 1, 15, 's')
g.rect(0, 16, W - 1, 16, 'f')
# the street up to it, toward the camera
g.rect(17, 16, 17, H - 1, 'f')
g.rect(18, 16, 19, H - 1, 's')
g.rect(20, 14, 23, H - 1, '~')
g.rect(24, 16, 25, H - 1, 's')
g.rect(26, 16, 26, H - 1, 'f')
g.rect(18, 16, 25, 16, 's')                           # the corners of the junction
g.rect(20, 14, 23, 16, '~')
for x in (0, W - 1):                                  # a building closes each end of the cross street
    g.rect(x, 7, x, 16, 'B')

lamps = [(18.55, 54.0), (25.45, 48.0), (18.55, 42.0), (25.45, 36.0), (18.55, 30.0), (25.45, 24.0),
         (18.55, 18.0), (12.0, 8.55), (31.0, 8.55), (5.0, 15.45), (38.0, 15.45)]
RAIN = [{'fx': 'rain', 'density': 0.8, 'length': 8, 'opacity': 0.3, 'angle': 14}, {'fx': 'splashes', 'density': 0.7},
        {'fx': 'grade', 'saturation': 0.75, 'tint': [0.92, 0.97, 1.05]}]

s = scene(
    g,
    title='Rain alley - a downpour at night, up to the T-junction',
    legend={
        'B': {'wall': 'brick_dark', 'h': 3.0,
              'facade': {'style': ['brick', 'brick', 'brick', 'sooty', 'sooty'], 'storeys': [3, 6], 'widths': [3, 6],
                         'lit': 0.5, 'shops': 0.45, 'seed': 3}},
        'f': {'floor': 'boards'},                     # inside the fronts: the floor seen through a shop door
        's': {'floor': 'flagstone'},
        '~': {'floor': 'asphalt', 'drop': 0.05},      # a kerb's height below the pavement
    },
    sky='storm',
    ambient=[0.13, 0.13, 0.15],
    wet=0.75,
    fog={'color': [0.07, 0.08, 0.1], 'density': 0.016, 'ground': 0.05, 'height': 0.8, 'glow': 1.2},
    prefabs=[{'type': 'street_lamp', 'x': x, 'y': y, 'seed': i} for i, (x, y) in enumerate(lamps)],
    objects=[{'type': 'car', 'x': 20.4, 'y': y, 'angle': 270, 'paint': p}                       # parked along the kerbs
             for y, p in ((45.6, '#9a9ea4'), (38.6, '#8a2a26'))]
           + [{'type': 'car', 'x': 23.6, 'y': y, 'angle': 90, 'paint': p}
              for y, p in ((33.0, '#c8c0a8'), (20.6, '#c89a3a'))]
           + [{'type': 'car', 'x': 22.75, 'y': 49.0, 'angle': 90, 'paint': '#2e3c5a', 'lights': True}],   # coming up the street
    sprites=[
        {'id': 'officer', 'x': 19.1, 'y': 31.0, 'type': 'guard', 'facing': 270},
        {'x': 25.1, 'y': 38.6, 'type': 'barrel'}, {'x': 18.9, 'y': 45.4, 'type': 'crate'},
        {'x': 19.3, 'y': 45.9, 'type': 'sack'}, {'x': 25.0, 'y': 22.4, 'type': 'barrel', 'flip': True},
    ],
    decals=[{'tex': 'puddle_shine', 'surface': 'floor', 'x': x, 'y': y, 'size': 1.6}
            for x, y in ((21.2, 49.0), (22.6, 38.0), (21.0, 26.0), (22.2, 12.0), (12.0, 11.4), (33.0, 12.6))],
    scatter=[{'of': 'litter', 'on': 's', 'density': 0.05, 'sizes': ['tiny', 'small'], 'seed': 6}],
    camera={'x': 21.6, 'y': 58.0, 'look_at': [21.6, 8.0, 1.5], 'fov': 66},
    shots=[
        {'x': 21.6, 'y': 58.0, 'look_at': [21.6, 8.0, 1.5], 'fov': 66, 'post': RAIN,
         'overlays': [{'type': 'caption', 'text': 'Third night of rain', 'at': 'top', 'box': True}]},
        {'x': 20.3, 'y': 36.2, 'look_at': 'officer', 'fov': 60, 'post': RAIN},
        {'x': 24.7, 'y': 52.0, 'look_at': [26.4, 40.0, 1.3], 'fov': 62, 'post': RAIN},
        {'x': 22.0, 'y': 18.5, 'look_at': [40.0, 11.0, 1.6], 'fov': 70,
         'post': ['storm', {'fx': 'lightning', 'x': 0.66}]},
        {'x': 21.0, 'y': 54.5, 'look_at': [21.8, 44.0, 0.4], 'fov': 58,      # a car coming up the street
         'post': RAIN + [{'fx': 'bloom', 'source': 'light', 'strength': 1.2, 'radius': 2.0, 'spread': 0.5}]},
    ],
    contact_shadows=0.5,
    supersample=2,
)
print(s.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rain_alley.json')))

"""The kaiju in the harbour: a city at night, and something enormous wading in from the bay - at landscape scale.

Landscape scale: a map cell is about 100 m, so the camera's eye at 0.5 is fifty metres up, the kaiju stands the
way a person stands in a room, and the city is built small - `city_block` objects on a grid of `city_street_lit`
cells, each block's towers drawn floor by floor with their windows lit, a `city_park`, a `container_yard` and a
`quay` along the `harbor_water`. Searchlight beams (`searchlight` objects) swing across it from the rooftops and
helicopters hold it in theirs (`ray`), tanks fire up at it from the quay, the waterfront burns (`blaze`,
`smoke_plume`), and the `kaiju_wading` throws its head back and roars, its plates glowing; from the air its breath
(a `ray`) cuts into downtown, and a helicopter hangs eye to eye with it as it breathes. The last shot is another day: `time` golden - the city's windows dim and the
searchlights, marked for the night, gone - the monster ashore among the low buildings of the waterfront, `jet`s
overhead.
Run:  python kaiju_harbor.py  -> writes kaiju_harbor.json next to this file.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from maptools import Grid, scene  # noqa: E402

W, H = 42, 30
KAIJU = (20.6, 22.6)                    # where it wades, in the shallows off the quay
MOUTH = (20.44, 22.6, 0.33)             # its open jaws, as the cameras from the bay see them
STRUCK = (17.6, 16.6, 0.32)             # where its breath lands, a tower downtown
GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.3, 'radius': 2.5, 'spread': 0.5}
FIRES = [(17.4, 20.25), (24.8, 20.35), (27.6, 18.6), (15.6, 18.6)]


def city(rng):
    """The blocks: tall in the middle of downtown, lower out from it, low warehouses along the waterfront."""
    out = []
    for y in range(2, 20):
        for x in range(4, 38):
            if 8 <= x <= 10 and 8 <= y <= 10 or 28 <= x <= 36 and y >= 17:
                continue                                # the park; the container yard
            d = math.hypot(x - 20.5, (y - 9.5) * 1.4)
            if y >= 17:
                spec = {'height': [0.04, 0.14], 'style': ['brick', 'dark', 'office'], 'lit': 0.22}
            elif d < 5.5:
                spec = {'height': [0.35, 1.5 - d * 0.12], 'lit': 0.5}
            elif d < 11:
                spec = {'height': [0.1, 0.5], 'lit': 0.42}
            else:
                spec = {'height': [0.06, 0.24], 'count': 1 if rng.random() < 0.6 else 2, 'lit': 0.38}
            out.append(dict({'type': 'city_block', 'x': x + 0.5, 'y': y + 0.5, 'seed': rng.randrange(1 << 20)}, **spec))
    return out


def searchlights(rng):
    """Beams from the rooftops toward the monster, and a few still sweeping the sky."""
    out = []
    for x, y in ((14.5, 15.5), (18.5, 12.5), (23.5, 13.5), (27.5, 16.5), (11.5, 18.5), (31.5, 15.5), (21.5, 9.5)):
        ang = math.degrees(math.atan2(KAIJU[1] - y, KAIJU[0] - x)) + rng.uniform(-14, 14)
        out.append({'type': 'searchlight', 'x': x, 'y': y, 'z': 0.3, 'angle': round(ang, 1),
                    'elevation': round(rng.uniform(14, 34), 1), 'length': 11.0, 'night': True})
    for x, y, ang, el in ((8.5, 6.5, 200, 62), (33.5, 6.5, 330, 58), (26.5, 4.5, 280, 70)):
        out.append({'type': 'searchlight', 'x': x, 'y': y, 'z': 0.3, 'angle': ang, 'elevation': el, 'length': 13.0,
                    'night': True})
    return out


def kaiju_harbor():
    rng = random.Random(7)
    g = Grid(W, H, fill='~')
    g.rect(0, 0, W - 1, 19, 's')
    g.rect(8, 8, 10, 10, 'p')
    g.rect(28, 17, 36, 19, 'c')
    g.rect(0, 20, W - 1, 20, 'q')                   # the quay along the waterfront
    g.rect(30, 21, 31, 23, 'q')                     # a pier
    helis = [(19.2, 21.7, 0.42), (22.4, 21.9, 0.56), (21.4, 24.0, 0.62)]
    head = (KAIJU[0] - 0.12, KAIJU[1], 0.42)
    objects = city(rng) + searchlights(rng) + [
        {'type': 'ray', 'x': MOUTH[0], 'y': MOUTH[1], 'z': MOUTH[2], 'to': list(STRUCK), 'width': 0.035,
         'night': True}] + [
        {'type': 'ray', 'x': x, 'y': y, 'z': z, 'to': list(head), 'width': 0.01, 'color': '#e8f0ff', 'opacity': 0.45,
         'night': True} for x, y, z in helis]
    sprites = [{'id': 'kaiju', 'x': KAIJU[0], 'y': KAIJU[1], 'type': 'kaiju_wading', 'facing': 90}]
    sprites += [{'x': x, 'y': y, 'type': 'helicopter', 'z': z, 'flip': x > KAIJU[0]} for x, y, z in helis]
    sprites += [{'x': 18.2, 'y': 20.45, 'type': 'tanks_firing', 'flip': True},
                {'x': 20.02, 'y': 20.79, 'type': 'tanks_firing', 'flip': True},     # before the camera on the quay
                {'x': 20.29, 'y': 20.77, 'type': 'tanks_firing'},
                {'x': 23.2, 'y': 20.4, 'type': 'tanks_firing'}, {'x': 25.4, 'y': 20.5, 'type': 'tanks'},
                {'x': 33.4, 'y': 21.35, 'type': 'cargo_ship', 'flip': True}]   # berthed at the container quay
    for x, y in FIRES:
        sprites += [{'x': x, 'y': y, 'type': 'blaze'}, {'x': x + 0.1, 'y': y - 0.05, 'type': 'smoke_plume'}]
    sprites += [{'x': STRUCK[0], 'y': STRUCK[1], 'z': STRUCK[2] - 0.12, 'type': 'blaze', 'scale': 0.42, 'night': True}]
    lights = [{'type': 'moon', 'azimuth': 300, 'elevation': 28, 'intensity': 0.28, 'disc_size': 1.6},
              {'x': KAIJU[0] + 0.3, 'y': KAIJU[1] - 0.3, 'z': 0.3, 'radius': 1.0, 'color': [0.45, 0.85, 1.0],
               'intensity': 0.5, 'night': True}]                # the glow of its plates on the water behind it
    lights += [{'x': x, 'y': y, 'z': 0.1, 'radius': 1.5, 'color': [1.0, 0.55, 0.22], 'intensity': 1.5}
               for x, y in FIRES]
    lights += [{'x': STRUCK[0], 'y': STRUCK[1], 'z': STRUCK[2], 'radius': 1.8, 'color': [0.6, 0.85, 1.0],
                'intensity': 1.4, 'night': True}]                # the blast where the breath lands
    day_sprites = [{'id': 'kaiju', 'x': 21.4, 'y': 18.2, 'type': 'kaiju_roar', 'facing': 90},
                   {'x': 18.6, 'y': 15.0, 'type': 'jet', 'z': 0.9}, {'x': 19.4, 'y': 15.3, 'type': 'jet', 'z': 0.95},
                   {'x': 24.0, 'y': 17.0, 'type': 'smoke_plume'}, {'x': 18.2, 'y': 17.6, 'type': 'smoke_plume'},
                   {'x': 22.6, 'y': 20.4, 'type': 'tanks_firing'}]
    return scene(
        g,
        title='The kaiju in the harbour - a city at night at landscape scale',
        legend={
            '~': {'floor': 'harbor_water'},
            's': {'floor': 'city_street_lit'},
            'p': {'floor': 'city_park'},
            'c': {'floor': 'container_yard'},
            'q': {'floor': 'quay'},
        },
        sky='night',
        skyline='city',
        ambient=[0.13, 0.13, 0.19],
        lights=lights,
        fog={'color': [0.11, 0.1, 0.13], 'density': 0.035, 'glow': 0.7},
        objects=objects,
        sprites=sprites,
        camera={'x': 21.1, 'y': 24.3, 'look_at': [20.6, 22.6, 0.32], 'fov': 60, 'height': 0.035},
        shots=[
            {'x': 21.1, 'y': 24.3, 'look_at': [20.6, 22.6, 0.32], 'fov': 60, 'height': 0.035, 'post': [GLOW],
             'overlays': [{'type': 'caption', 'text': 'Something in the harbour', 'at': 'top', 'box': True}]},
            {'x': 20.05, 'y': 20.42, 'look_at': [20.6, 22.6, 0.42], 'fov': 54, 'height': 0.012, 'post': [GLOW]},
            {'x': 22.0, 'y': 24.0, 'look_at': [20.0, 21.0, 0.2], 'fov': 62, 'height': 0.75, 'post': [GLOW]},
            {'x': 21.0, 'y': 20.2, 'look_at': [21.4, 18.2, 0.4], 'fov': 60, 'height': 0.03,
             'overrides': {'time': 'golden', 'sprites': day_sprites,
                           'fog': {'color': [0.7, 0.66, 0.62], 'density': 0.03}}},
            {'x': 20.15, 'y': 23.55, 'look_at': [20.55, 22.6, 0.31], 'fov': 54, 'height': 0.3, 'post': [GLOW]},
        ],
        max_distance=48,
        supersample=2,
    )


HERE = os.path.dirname(os.path.abspath(__file__))
print(kaiju_harbor().save(os.path.join(HERE, 'kaiju_harbor.json')))

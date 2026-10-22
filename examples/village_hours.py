"""The village green through a day: one shot of its street eight times over - at dawn, in the morning, at noon,
in the afternoon, in the golden hour, at sunset, at dusk and at night - each shot a `time` of day and nothing
else: the sun going round from the east to the west and down, the sky, the light of the air, more and more of
the windows lit. The scene is village_green.json (run village_green.py first if it is missing), with the inn's
two lanterns added as lights marked "night": they burn only from sunset to sunrise.
Run:  python village_hours.py  -> writes village_hours.json next to this file.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TIMES = ['dawn', 'morning', 'noon', 'afternoon', 'golden', 'sunset', 'dusk', 'night']
GLOW = {'fx': 'bloom', 'source': 'light', 'strength': 1.4, 'radius': 2.5, 'spread': 0.5}  # the lamps glow
LANTERNS = [{'x': 19.6, 'y': y, 'z': 1.0, 'radius': 3.2, 'color': [1.0, 0.66, 0.34], 'intensity': 1.3, 'night': True}
            for y in (29.4, 31.6)]


def village_hours():
    with open(os.path.join(HERE, 'village_green.json'), encoding='utf-8') as f:
        sc = json.load(f)
    street = {'x': 17.0, 'y': 40.5, 'angle': 270, 'fov': 64}           # village_green's first shot
    sc.update(title='The village green through a day - one shot at eight times', lights=sc['lights'] + LANTERNS,
              shots=[dict(street, time=t, overlays=[{'type': 'caption', 'text': t.capitalize(), 'at': 'top',
                                                      'box': True}], **({'post': [GLOW]} if k >= 5 else {}))
                     for k, t in enumerate(TIMES)])
    return sc


with open(os.path.join(HERE, 'village_hours.json'), 'w', encoding='utf-8') as f:
    json.dump(village_hours(), f, indent=1)
print(os.path.join(HERE, 'village_hours.json'))

"""The time of day: one key, `time`, that sets a scene to an hour - "dawn", "morning", "noon", "afternoon",
"golden", "sunset", "dusk" or "night", or a number of hours (17.5 is half past five in the afternoon).

The hour puts the sun where the clock has it - rising in the east (azimuth 0, the camera's compass), high in the
south at noon, setting in the west - its light reddening and weakening as it sinks; after sunset a moon rises
opposite it. It picks the sky (`dawn`, `day`, `golden`, `sunset`, `dusk` or `night`) and darkens or lightens the
scene's ambient light and the colour of its air and tints them - scaled from what the scene has, taken to be
right for the hour its own sky shows, so a dim interior stays dim beside a bright street and a warm room stays
warm at any hour - and lights fewer of the rooms behind its facades' windows by day (a facade's `lit` is how many
show a lamp after dark). Lights marked
`"night": true` (street lamps, lanterns, a lit window's glow) burn only between sunset and sunrise, and ones marked
`"day": true` only by day.

A scene is rewritten once, as it is read (prefabs.expand calls apply). The time can be a dict to adjust what the
hour gives: `{"at": "dusk", "azimuth": 200}` (where the sun or moon stands), `"elevation"`, `"sky"`, `"ambient"`
and `"fog"` (a colour) - and keys a shot's `overrides` give beside its `time` win over the time's.
"""
import math

TIMES = {'dawn': 6.9, 'morning': 8.5, 'noon': 12.75, 'afternoon': 15.5, 'golden': 18.3, 'sunset': 18.85,
         'dusk': 19.5, 'night': 21.5}
RISE, SET = 6.5, 19.0                   # the sun's day, in hours
HIGH = 58.0                             # its height at noon, in degrees
# the air through the day: (hour, ambient, fog colour, the share of a facade's lit rooms whose lamps show)
AIR = [(0.0, (0.08, 0.09, 0.14), (0.05, 0.06, 0.1), 1.0),
       (5.2, (0.08, 0.09, 0.14), (0.05, 0.06, 0.1), 1.0),
       (6.1, (0.15, 0.14, 0.21), (0.24, 0.22, 0.32), 0.85),
       (6.9, (0.29, 0.26, 0.32), (0.62, 0.55, 0.6), 0.55),
       (8.5, (0.36, 0.36, 0.4), (0.7, 0.72, 0.78), 0.15),
       (12.75, (0.42, 0.42, 0.46), (0.72, 0.74, 0.8), 0.1),
       (15.5, (0.4, 0.39, 0.42), (0.72, 0.72, 0.76), 0.1),
       (18.3, (0.36, 0.32, 0.34), (0.76, 0.68, 0.6), 0.35),
       (18.85, (0.3, 0.22, 0.26), (0.66, 0.48, 0.46), 0.65),
       (19.5, (0.16, 0.14, 0.2), (0.22, 0.18, 0.26), 0.85),
       (20.8, (0.08, 0.09, 0.14), (0.05, 0.06, 0.1), 1.0),
       (24.0, (0.08, 0.09, 0.14), (0.05, 0.06, 0.1), 1.0)]
SKIES = [(5.2, 'night'), (6.3, 'dusk'), (7.4, 'dawn'), (17.6, 'day'), (18.6, 'golden'), (19.2, 'sunset'),
         (20.4, 'dusk'), (24.0, 'night')]                   # the sky up to each hour
SKY_HOURS = {'dawn': 6.9, 'day': 12.75, 'golden': 18.3, 'sunset': 18.85, 'dusk': 19.5, 'night': 21.5}
# the sun's colour and strength by its height in degrees: red and weak on the horizon, white and full high up
SUN = [(0.0, (1.0, 0.5, 0.32), 0.9), (3.0, (1.0, 0.6, 0.4), 1.05), (8.0, (1.0, 0.74, 0.5), 1.25),
       (15.0, (1.0, 0.86, 0.68), 1.4), (30.0, (1.0, 0.94, 0.84), 1.5), (90.0, (1.0, 0.98, 0.93), 1.5)]
MOON = 0.38                             # the moon's strength, full night
LIGHT_KEYS = ('type', 'azimuth', 'elevation', 'color', 'intensity', 'night', 'day')
SPEC_KEYS = {'at', 'azimuth', 'elevation', 'sky', 'ambient', 'fog'}      # what a time given as a dict may hold


def hour(t):
    """The hour a `time` names: one of TIMES, a number of hours, or a dict's `at`."""
    if isinstance(t, dict):
        t = t.get('at', 'noon')
    if isinstance(t, str):
        if t not in TIMES:
            raise KeyError(f"unknown time {t!r} - the times are {', '.join(TIMES)}, or a number of hours")
        return TIMES[t]
    return float(t) % 24.0


def _lerp(table, x):
    """Interpolate the rows of `table` (sorted by their first item) at x: every tuple item blended."""
    for (x0, *a), (x1, *b) in zip(table, table[1:]):
        if x <= x1:
            f = 0.0 if x1 <= x0 else max(0.0, min(1.0, (x - x0) / (x1 - x0)))
            return [tuple(p + (q - p) * f for p, q in zip(u, v)) if isinstance(u, tuple) else u + (v - u) * f
                    for u, v in zip(a, b)]
    return list(table[-1][1:])


def sun(h):
    """(azimuth, elevation) of the sun at hour h: rising due east at RISE, 15 degrees round the sky an hour, highest
    in the south at the middle of the day; under the horizon (negative) at night."""
    if RISE < h < SET:
        up = math.sin(math.pi * (h - RISE) / (SET - RISE))
    else:
        up = -math.sin(math.pi * ((h - SET) % 24.0) / (24.0 - (SET - RISE)))
    return (90.0 + (h - (RISE + SET) / 2) * 15.0) % 360.0, HIGH * up


def moon(h):
    """(azimuth, elevation) of a full moon at hour h: opposite the sun, rising as it sets."""
    az, el = sun(h)
    return (az + 180.0) % 360.0, -el * 50.0 / HIGH


def lamps_lit(h):
    """True between sunset and sunrise - near enough: while the sun is under 3 degrees."""
    return sun(h)[1] < 3.0


def _scaled(c, now, then):
    """Colour c as the hour `now` has it, if the scene wrote it for the hour `then`: times now / then, channel by
    channel."""
    return [round(float(v) * a / max(b, 1e-3), 4) for v, a, b in zip(c, now, then)]


def apply(scene, keep=()):
    """The scene set to its `time` (the same object when it has none), the key gone. Keys named in `keep` - the
    ones a shot's overrides give beside its time - are left as they are."""
    t = scene.get('time')
    if t is None:
        return scene
    spec = t if isinstance(t, dict) else {}
    h = hour(t)
    out = {k: v for k, v in scene.items() if k != 'time'}
    sky0 = scene.get('sky')
    then = SKY_HOURS.get(sky0, (RISE + SET) / 2)              # the hour the scene was written for
    amb, fog, lit = _lerp(AIR, h)
    amb0, fog0, _ = _lerp(AIR, then)
    outside = sky0 is not None                              # no sky: a world of its own, nowhere for the hour
    if 'sky' not in keep and (sky0 in SKY_HOURS or 'sky' in spec):
        out['sky'] = spec.get('sky') or next(s for top, s in SKIES if h <= top)
    if outside and 'ambient' not in keep:
        out['ambient'] = list(spec['ambient']) if 'ambient' in spec else _scaled(
            scene.get('ambient', [0.18, 0.18, 0.22]), amb, amb0)
    if outside and scene.get('fog') and 'fog' not in keep:
        out['fog'] = dict(scene['fog'], color=list(spec['fog']) if 'fog' in spec else _scaled(
            scene['fog'].get('color', [0.5, 0.5, 0.5]), fog, fog0))
    if outside and scene.get('legend'):                        # fewer lamps showing in the rooms by day
        legend = {}
        for ch, cell in scene['legend'].items():
            if isinstance(cell, dict) and isinstance(cell.get('facade'), dict):
                f = cell['facade']
                cell = dict(cell, facade=dict(f, lit=round(float(f.get('lit', 0.35)) * lit, 3)))
            legend[ch] = cell
        out['legend'] = legend
    lights = list(scene.get('lights') or [])
    old = [L for L in lights if L.get('type') in ('sun', 'moon')]
    # a sun or moon where the scene had one, or under a sky the hour sets - none under its own cloud or stars
    if ('lights' not in keep or not old) and (old or sky0 in SKY_HOURS or 'sky' in spec):
        lights = [L for L in lights if L.get('type') not in ('sun', 'moon')]
        az, el = sun(h)
        kind = 'sun' if el > 0.5 else 'moon'
        if kind == 'moon':
            az, el = moon(h)
        az, el = float(spec.get('azimuth', az)), float(spec.get('elevation', el))
        extra = {k: v for L in old[:1] for k, v in L.items() if k not in LIGHT_KEYS}
        if kind == 'sun':
            colour, power = _lerp(SUN, el)
            was = [L for L in old if L.get('type') == 'sun']
            if was:                                              # as strong as the scene's, for its height
                power *= float(was[0].get('intensity', 0.85)) / _lerp(SUN, float(was[0].get('elevation', 35)))[1]
            lights.append({**extra, 'type': 'sun', 'azimuth': round(az, 2), 'elevation': round(el, 2),
                           'color': [round(c, 3) for c in colour], 'intensity': round(power, 3)})
        elif el > 0.5:
            dark = max(0.0, min(1.0, -sun(h)[1] / 8.0))          # brightening as the twilight goes
            was = [L for L in old if L.get('type') == 'moon']    # the scene's own moon, as strong and as blue
            mine = {'color': was[0]['color']} if was and 'color' in was[0] else {}
            lights.append({**extra, **mine, 'type': 'moon', 'azimuth': round(az, 2), 'elevation': round(el, 2),
                           'intensity': round((float(was[0].get('intensity', 0.4)) if was else MOON) * dark, 3)})
    night = lamps_lit(h)
    out['lights'] = [L for L in lights if not (L.get('night') and not night) and not (L.get('day') and night)]
    return out

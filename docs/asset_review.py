"""Keep docs/ASSETS.md in step with the code, and render review sheets for improvement passes.

    python docs/asset_review.py sync                      # rows, computed columns and counts up to date
    python docs/asset_review.py check                     # exit 1 if ASSETS.md is out of date
    python docs/asset_review.py sheets                    # every review sheet, into renders/sheets
    python docs/asset_review.py sheets textures props     # just those sections
    python docs/asset_review.py sheets foliage tree       # just those assets
    python docs/asset_review.py sheets --status polish,rework --out renders/sheets/before

ASSETS.md is the working list for improvement passes. Its prose and its status and notes
columns are written by hand; the rows themselves, the computed columns and the counts belong to
this script, so the list cannot fall behind the code: a new texture appears as `new`, a removed
one disappears, and "used in" always names the examples that really use each asset.
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'docs'))
import assets  # noqa: E402
import buildings  # noqa: E402
import gui  # noqa: E402
import icons  # noqa: E402
import post  # noqa: E402
import prefabs  # noqa: E402
from characters import CHARACTERS  # noqa: E402

INVENTORY = os.path.join(ROOT, 'docs', 'ASSETS.md')
EXAMPLES = os.path.join(ROOT, 'examples')
SHEETS = os.path.join(ROOT, 'renders', 'sheets')
STATUSES = ('good', 'polish', 'rework', 'new')
UNSORTED = 'Not yet sorted'


def example_names():
    return sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(EXAMPLES, '*.json')))


# section heading -> (registry, header of the name column, computed columns between status and notes)
SECTIONS = {
    'Textures': (lambda: list(assets.TEXTURES), 'texture', ['traits', 'used in']),
    'Props': (lambda: list(assets.SPRITES), 'prop', ['traits', 'used in']),
    'Characters': (lambda: list(CHARACTERS), 'character', ['used in']),
    'Decals': (lambda: list(assets.DECALS), 'decal', ['used in']),
    'Skies': (lambda: list(assets.SKY_PRESETS), 'sky', ['used in']),
    'Skylines': (lambda: list(assets.SKYLINES), 'skyline', ['used in']),
    'Sky objects': (lambda: list(assets.SKY_OBJECTS), 'object', ['used in']),
    'Scatter sets': (lambda: list(assets.DEBRIS_SETS), 'set', ['contents', 'used in']),
    'Fringe sets': (lambda: list(assets.FRINGES), 'set', ['cards', 'used in']),
    'Facade styles': (lambda: list(buildings.FACADE_STYLES), 'style', ['used in']),
    'Prefabs': (lambda: list(prefabs.PREFABS), 'prefab', ['parts', 'used in']),
    'Objects': (lambda: list(prefabs.objects.OBJECTS), 'object', ['used in']),
    'Held items': (lambda: list(icons.VIEWMODELS), 'item', ['used in']),
    'Icons': (lambda: list(icons.ICONS), 'icon', ['used in']),
    'GUI themes': (lambda: list(gui.THEMES), 'theme', ['used in']),
    'GUI widgets': (lambda: list(gui.WIDGETS), 'widget', ['used in']),
    'Post presets': (lambda: list(post.PRESETS), 'preset', ['used in']),
    'Palettes': (lambda: list(post.PALETTES), 'palette', ['used in']),
    'Example scenes': (example_names, 'scene', ['shots', 'gallery']),
}


# ------------------------------------------------------------------ what each example uses

def _textures(v):
    """Texture names in a legend field: a name, a storey stack, or a {"base": ...} variant."""
    if isinstance(v, list):
        return [n for x in v for n in _textures(x)]
    if isinstance(v, dict):
        return _textures(v.get('base'))
    if isinstance(v, str) and v != 'void' and not v.lower().endswith('.png'):
        return [v]
    return []


def _post_entries(entries):
    """Preset and palette names in a `post` list, with presets opened up."""
    out = []
    for e in entries or []:
        if isinstance(e, str) and e in post.PRESETS:
            out.append(('Post presets', e))
            out += _post_entries(post.PRESETS[e])
        elif isinstance(e, dict) and e.get('fx') == 'palette' and isinstance(e.get('name'), str):
            out.append(('Palettes', e['name']))
    return out


def _overlay_assets(overlays):
    """(section, name) for the widget or held item of each overlay, and what it shows inside."""
    out = []
    for ov in overlays or []:
        if isinstance(ov, dict):
            kind = ov.get('type', 'bubble')
            out.append(('Held items', ov.get('item')) if kind == 'viewmodel' else ('GUI widgets', kind))
            out += _icon_refs(ov)
    return out


def _icon_refs(d):
    """Icons and portraits named anywhere inside one overlay entry."""
    out = []
    if isinstance(d, list):
        for x in d:
            out += _icon_refs(x)
    elif isinstance(d, dict):
        for k, v in d.items():
            if k == 'icon' and isinstance(v, str):
                out.append(('Icons', v))
            elif k == 'pointer' and v == 'hand':
                out.append(('Icons', 'hand_pointer'))
            elif k == 'portrait' and isinstance(v, str):
                out.append(('Characters' if v in CHARACTERS else 'Props' if v in assets.SPRITES else 'Icons', v))
            elif k in ('slots', 'items') and isinstance(v, list):
                out += [('Icons', x) for x in v if isinstance(x, str) and x in icons.ICONS]
            if isinstance(v, (dict, list)):
                out += _icon_refs(v)
    return out


def _sprite(name):
    return ('Characters' if name in CHARACTERS else 'Props', name)


def _road_assets(part):
    """What a road scene (road.py) uses: its surface, shoulder and ground textures, its roadside rows' props."""
    road = part.get('road')
    out = []
    if isinstance(road, dict):
        out += [('Textures', t) for t in _textures(road.get('surface', 'asphalt'))]
        if isinstance(road.get('shoulder'), dict):
            out += [('Textures', t) for t in _textures(road['shoulder'].get('texture', 'gravel'))]
        g = road.get('ground', 'grass')
        sides = g if isinstance(g, dict) and ('left' in g or 'right' in g) else {'left': g, 'right': g}
        for side in sides.values():
            for band in side if isinstance(side, list) else [side]:
                tex = band.get('texture', 'grass') if isinstance(band, dict) and 'base' not in band else band
                out += [('Textures', t) for t in _textures(tex)]
    for row in part.get('roadside') or []:
        types = row.get('type')
        out += [_sprite(t) for t in (types if isinstance(types, list) else [types])]
    return out


def _placed(placements, defs):
    """Every prefab a list of placements puts down, nested ones included."""
    out = []
    for pl in placements or []:
        name = pl.get('type')
        out.append(name)
        out += _placed((defs.get(name) or {}).get('prefabs'), defs)
    return out


def usage():
    """section -> name -> the examples that use it, read from the example scenes themselves
    (with their prefabs expanded, so a prefab's parts count as used)."""
    use = defaultdict(lambda: defaultdict(set))
    for ex in example_names():
        with open(os.path.join(EXAMPLES, ex + '.json'), encoding='utf-8') as f:
            raw = json.load(f)
        defs = {**prefabs.PREFABS, **(raw.get('prefab_defs') or {})}
        shots = [s for s in raw.get('shots') or [] if isinstance(s, dict)]
        found = [('Prefabs', n) for n in _placed(raw.get('prefabs'), defs)]
        for s in shots:
            found += [('Prefabs', n) for n in _placed((s.get('overrides') or {}).get('prefabs'), defs)]
        for objs in [raw.get('objects')] + [(s.get('overrides') or {}).get('objects') for s in shots]:
            found += [('Objects', o.get('type')) for o in objs or [] if isinstance(o, dict)]
        sc = prefabs.expand(raw)
        overrides = [prefabs.expand({**raw, **s['overrides']}) for s in shots if s.get('overrides')]
        for part in [sc] + overrides:
            default = part.get('default') or {}
            legend = part.get('legend') or {}
            for spec in list(legend.values()) + [default]:
                if not isinstance(spec, dict):
                    continue
                for key in ('wall', 'floor', 'ceil', 'top', 'side'):
                    found += [('Textures', t) for t in _textures(spec.get(key))]
                fa = spec.get('facade')
                if fa:
                    style = fa if isinstance(fa, str) else fa.get('style', fa.get('set', 'brick'))
                    found += [('Facade styles', st) for st in (style if isinstance(style, list) else [style])]
                fr = spec.get('fringe')
                if fr:
                    fr = {'set': fr} if isinstance(fr, str) else fr
                    cards = fr.get('cards') or assets.FRINGES.get(fr.get('set'), [])
                    found += [('Fringe sets', fr.get('set'))] + [('Props', c) for c in cards]
                if legend and 'wall' not in spec and 'floor' not in spec:
                    found.append(('Textures', default.get('floor', 'concrete_floor')))
            sky = part.get('sky')
            if isinstance(sky, str):
                found.append(('Skies', sky))
            skyline = part.get('skyline')
            for s in skyline if isinstance(skyline, list) else [skyline] if skyline else []:
                found.append(('Skylines', s if isinstance(s, str) else s.get('type')))
            found += [('Sky objects', o.get('type', 'planet')) for o in part.get('sky_objects') or []]
            found += [_sprite(s.get('type')) for s in part.get('sprites') or []]
            found += _road_assets(part)
            for spec in part.get('scatter') or []:
                of = spec.get('of', 'stones')
                found += [('Scatter sets', s) for s in (of if isinstance(of, list) else [of]) if s in assets.DEBRIS_SETS]
                found += [_sprite(n) for n in assets.debris_items(of)]
            g = part.get('grime', 0)
            if (g.get('amount', 0) if isinstance(g, dict) else g) > 0:
                if part.get('grime_debris', True):
                    found += [('Scatter sets', 'wreckage')] + [_sprite(n) for n in assets.DEBRIS_SETS['wreckage']]
                if part.get('grime_decals', True):
                    found += [('Decals', d) for d in assets.GRIME_WALL_DECALS + assets.GRIME_FLOOR_DECALS]
            for d in part.get('decals') or []:            # a road scene's row names a list, or a set of marks
                import road
                tex = d.get('tex')
                for t in tex if isinstance(tex, list) else [tex]:
                    found += [('Decals', t2) for t2 in road.DECAL_SETS.get(t, [t])]
            if part.get('contact_shadows', 1) and (part.get('sprites') or part.get('scatter')
                                                   or part.get('roadside')):
                found.append(('Decals', 'contact_shadow'))
            found += _post_entries(part.get('post'))
            if isinstance(part.get('palette'), str):
                found.append(('Palettes', part['palette']))
            found += _overlay_assets(part.get('overlays'))
            theme = (part.get('ui') or {}).get('theme')
            if theme:
                found.append(('GUI themes', theme))
        for s in shots:
            found += [_sprite(sp.get('type')) for sp in s.get('extra_sprites') or []]
            if isinstance(s.get('vehicle'), dict):
                found.append(_sprite(s['vehicle'].get('type')))
            found += _post_entries(s.get('post'))
            found += _overlay_assets(s.get('overlays'))
        widgets = [n for sec, n in found if sec == 'GUI widgets']
        if widgets and not (sc.get('ui') or {}).get('theme'):
            found.append(('GUI themes', 'classic'))
        for sec, name in found:
            if isinstance(name, str):
                use[sec][name].add(ex)
    return use


def _gallery():
    """example -> the gallery images built from it."""
    import build_gallery as bg
    out = defaultdict(list)
    for img, (ex, _) in bg.SHOTS.items():
        out[ex].append(img)
    for table in (bg.SHEETS, bg.MAPS):
        for img, ex in table.items():
            out[ex].append(img)
    return out


def computed(section, name, use, gallery):
    """The cells this script owns for one row."""
    used = sorted(use[section].get(name, ()))
    # something nearly every scene uses (contact shadows, the default theme) gets a count, not a list
    used = f'{len(used)} scenes' if len(used) >= 20 else ', '.join(used) or '-'
    if section == 'Textures':
        rgb, em = assets.get_texture(name)
        traits = []
        if em is not None and em.max() > 0.02:
            traits.append('glows')
        if assets.get_alpha(name) is not None:
            traits.append('see-through')
        if name in assets.TEXTURE_REFLECT:
            traits.append(f'mirror {assets.TEXTURE_REFLECT[name]:g}')
        return [', '.join(traits), used]
    if section == 'Props':
        rgba, em = assets.get_sprite(name)
        traits = [f'{assets.SPRITE_HEIGHT.get(name, 1.0):g} tall']
        if em is not None and em.max() > 0.02:
            traits.append('glows')
        if 'aura' in assets.PROP_DEFAULTS.get(name, {}):
            traits.append('aura')
        if name in assets.NO_CONTACT_SHADOW:
            traits.append('no shadow')
        return [', '.join(traits), used]
    if section == 'Scatter sets':
        items = assets.DEBRIS_SETS[name]
        seen = list(dict.fromkeys(items))
        return [', '.join(n + (f' x{items.count(n)}' if items.count(n) > 1 else '') for n in seen), used]
    if section == 'Fringe sets':
        return [', '.join(assets.FRINGES[name]), used]
    if section == 'Prefabs':
        pf = prefabs.PREFABS[name]
        bits = [f"{len(pf[k])} {k}" for k in ('sprites', 'objects', 'lights', 'decals', 'prefabs') if pf.get(k)]
        if pf.get('map'):
            bits.append('a map')
        return [', '.join(bits), used]
    if section == 'Example scenes':
        with open(os.path.join(EXAMPLES, name + '.json'), encoding='utf-8') as f:
            sc = json.load(f)
        return [str(len(sc.get('shots') or [sc.get('camera')])), ', '.join(gallery.get(name, ())) or '-']
    return [used]


# ------------------------------------------------------------------ the inventory file

ROW = re.compile(r'^\|\s*`([^`]+)`\s*\|')
HEADING = re.compile(r'^## (.+?)(?: \(\d+\))?\s*$')


def split_row(line):
    return [c.strip() for c in re.split(r'(?<!\\)\|', line.strip())[1:-1]]


def table_head(section):
    _, first, cols = SECTIONS[section]
    head = [first, 'status'] + cols + ['notes']
    return ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]


def read_inventory(path=INVENTORY):
    """[(section, group, name, status, notes)] for every asset row, in file order."""
    out, sec, group = [], None, ''
    with open(path, encoding='utf-8') as f:
        for line in f.read().split('\n'):
            m = HEADING.match(line)
            if m:
                sec, group = (m.group(1) if m.group(1) in SECTIONS else None), ''
            elif line.startswith('### '):
                group = line[4:].strip()
            elif sec and ROW.match(line):
                cells = split_row(line)
                out.append((sec, group, cells[0].strip('`'), cells[1], cells[-1]))
    return out


def sync_text(text):
    """(the inventory with its tables brought up to date, a list of what changed or is wrong)."""
    names = {s: reg() for s, (reg, _, _) in SECTIONS.items()}
    use, gallery = usage(), _gallery()
    out, changes, statuses = [], [], defaultdict(list)
    seen = defaultdict(set)
    state = {'sec': None, 'group': ''}

    def row(sec, name, status, notes):
        cells = [f'`{name}`', status] + computed(sec, name, use, gallery) + [notes]
        return '| ' + ' | '.join(cells) + ' |'

    def finish(sec):
        """Rows for registry entries the inventory does not list yet, under 'Not yet sorted'."""
        missing = [n for n in names[sec] if n not in seen[sec]]
        if not missing:
            return
        while out and not out[-1].strip():
            out.pop()
        if state['group'] != UNSORTED:
            out.extend(['', f'### {UNSORTED}', ''] + table_head(sec))
        for n in missing:
            out.append(row(sec, n, 'new', ''))
            statuses[sec].append('new')
            changes.append(f'{sec}: added {n}')
        out.append('')

    for line in text.split('\n'):
        m = HEADING.match(line)
        if m:
            if state['sec']:
                finish(state['sec'])
            sec = m.group(1) if m.group(1) in SECTIONS else None
            state.update(sec=sec, group='')
            out.append(f'## {sec} ({len(names[sec])})' if sec else line)
            continue
        sec = state['sec']
        if sec and line.startswith('### '):
            state['group'] = line[4:].strip()
        elif sec and line.startswith('|') and not ROW.match(line):
            # a table's header or rule: rewritten, so a new computed column reaches every table
            head = table_head(sec)
            first = split_row(line)[0] if split_row(line) else ''
            out.append(head[1] if set(first) <= set('-: ') else head[0])
            continue
        elif sec and ROW.match(line):
            cells = split_row(line)
            name, status, notes = cells[0].strip('`'), cells[1], cells[-1] if len(cells) > 2 else ''
            if name not in names[sec]:
                changes.append(f'{sec}: removed {name} (no longer in the code)')
                continue
            if name in seen[sec]:
                changes.append(f'{sec}: dropped a second row for {name}')
                continue
            if status not in STATUSES:
                changes.append(f"{sec}: {name} has status {status!r}; use one of {', '.join(STATUSES)}")
            seen[sec].add(name)
            statuses[sec].append(status)
            out.append(row(sec, name, status, notes))
            continue
        out.append(line)
    if state['sec']:
        finish(state['sec'])
    present = {m.group(1) for m in map(HEADING.match, out) if m}
    changes += [f'{sec}: the section is missing; add a "## {sec}" heading' for sec in SECTIONS if sec not in present]

    text = '\n'.join(out)
    start, end = '<!-- summary -->', '<!-- /summary -->'
    if start in text and end in text:
        rows = ['| | count | ' + ' | '.join(STATUSES) + ' |', '|---|' + '---|' * (len(STATUSES) + 1)]
        total = defaultdict(int)
        for sec in SECTIONS:
            counts = [statuses[sec].count(s) for s in STATUSES]
            for s, c in zip(STATUSES, counts):
                total[s] += c
            rows.append(f'| {sec} | {len(statuses[sec])} | ' + ' | '.join(str(c) for c in counts) + ' |')
        rows.append(f'| **all** | **{sum(total.values())}** | ' + ' | '.join(f'**{total[s]}**' for s in STATUSES) + ' |')
        a, b = text.index(start) + len(start), text.index(end)
        text = text[:a] + '\n' + '\n'.join(rows) + '\n' + text[b:]
    return text, changes


# ------------------------------------------------------------------ review sheets

STATUS_COLOUR = {'good': (110, 190, 110), 'polish': (230, 180, 70), 'rework': (230, 90, 80), 'new': (110, 160, 240)}
BG = (26, 26, 30)


def _im(a, mode='RGB'):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), mode)


def _checker(h, w, k=8):
    c = ((np.arange(h)[:, None] // k + np.arange(w)[None, :] // k) % 2)[..., None]
    return np.where(c == 0, 0.33, 0.5).astype(np.float32) * np.ones((1, 1, 3), np.float32)


def _over(rgba, under):
    a = rgba[..., 3:4]
    return rgba[..., :3] * a + under * (1 - a)


def _fit(im, box):
    """Integer zoom (nearest) so pixel art stays crisp, as large as fits in box; anything bigger
    than the box to begin with is shrunk to fit."""
    if im.width > box[0] or im.height > box[1]:
        f = min(box[0] / im.width, box[1] / im.height)
        return im.resize((max(1, int(im.width * f)), max(1, int(im.height * f))), Image.NEAREST)
    k = max(1, min(box[0] // im.width, box[1] // im.height))
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def tile_texture(name):
    rgb, em = assets.get_texture(name)
    a = assets.get_alpha(name)
    if a is not None:   # see-through: the holes against a checkerboard
        rgb = rgb * a[..., None] + _checker(*a.shape) * (1 - a[..., None])
    return _im(np.tile(rgb, (2, 2, 1))).resize((256, 256), Image.NEAREST)   # 2x2 shows the seams


def tile_prop(name):
    rgba, _ = assets.get_sprite(name)
    im = _fit(_im(rgba, 'RGBA'), (240, 232))
    tile = Image.new('RGB', (256, 256), (58, 60, 70))
    ImageDraw.Draw(tile).rectangle([0, 244, 255, 255], fill=(40, 38, 36))
    tile.paste(im, ((256 - im.width) // 2, 244 - im.height), im)
    return tile


def tile_character(name):
    tile = Image.new('RGB', (256, 256), (58, 60, 70))
    for i, view in enumerate(('front', 'back')):
        rgba, _ = assets.get_sprite(name, view=view)
        im = _fit(_im(rgba, 'RGBA'), (124, 240))
        tile.paste(im, (i * 128 + (128 - im.width) // 2, 248 - im.height), im)
    return tile


def tile_decal(name):
    rgba, _ = assets.get_decal(name)
    floor, _ = assets.get_texture('concrete_floor')
    under = np.tile(floor, (2, 2, 1))
    d = np.asarray(_im(rgba, 'RGBA').resize((128, 128), Image.NEAREST), np.float32) / 255
    return _im(_over(d, under)).resize((256, 256), Image.NEAREST)


def tile_sky(name, skyline=None):
    return _im(assets.make_sky(name, 768, 128, skyline=skyline))


def tile_sky_object(name):
    sky = assets.make_sky('night', 768, 128, objects=[{'type': name, 'azimuth': 180, 'elevation': 22}])
    return _im(sky[:, 256:512]).resize((256, 128), Image.NEAREST)


def tile_set(name):
    names = list(dict.fromkeys(assets.DEBRIS_SETS[name]))
    tile = Image.new('RGB', (64 * len(names), 72), (58, 60, 70))
    for i, n in enumerate(names):
        rgba, _ = assets.get_sprite(n)
        im = _fit(_im(rgba, 'RGBA'), (60, 64))
        tile.paste(im, (i * 64 + (64 - im.width) // 2, 68 - im.height), im)
    return tile


def tile_icon(name):
    rgba, _ = icons.get_icon(name)
    im = _fit(_im(rgba, 'RGBA'), (96, 96))
    tile = Image.new('RGB', im.size, (58, 60, 70))
    tile.paste(im, (0, 0), im)
    return tile


def tile_held(name):
    rgba, _, _ = icons.get_viewmodel(name)
    im = _fit(_im(rgba, 'RGBA'), (256, 256))
    tile = Image.new('RGB', (im.width, im.height), (44, 40, 48))
    tile.paste(im, (0, 0), im)
    return tile


def tile_object(name):
    """An object in a plain yard, seen from a front three-quarter and from behind, side by side (a
    rock wall with its back closed, as it would be standing free)."""
    import render
    import math as m
    yard = {'map': ['#' * 9] + ['#' + '.' * 7 + '#'] * 7 + ['#' * 9], 'sky': 'dusk', 'ambient': [0.5, 0.5, 0.55],
            'legend': {'#': {'wall': 'brick', 'h': 1.0}}, 'default': {'floor': 'concrete_floor'},
            'objects': [dict({'type': name, 'x': 4.5, 'y': 4.5}, **({'back': True} if name == 'rock_wall' else {}))]}
    views = []
    dist, aim = (3.4, 0.55) if name == 'rock_wall' else (2.3, 0.25)       # a rock wall is long and tall
    for bearing in (35, 215):
        b = m.radians(bearing)
        cam = {'x': 4.5 + m.cos(b) * dist, 'y': 4.5 + m.sin(b) * dist, 'look_at': [4.5, 4.5, aim], 'height': 0.62,
               'fov': 62}
        views.append(render.render_shot(dict(yard, camera=cam, shots=[cam]), 0).convert('RGB').resize((320, 200)))
    tile = Image.new('RGB', (646, 200), (44, 40, 48))
    for k, v in enumerate(views):
        tile.paste(v, (k * 326, 0))
    return tile


TILES = {
    'objects': ('Objects', tile_object, 1),
    'textures': ('Textures', tile_texture, 6),
    'props': ('Props', tile_prop, 6),
    'characters': ('Characters', tile_character, 6),
    'decals': ('Decals', tile_decal, 6),
    'skies': ('Skies', tile_sky, 1),
    'skylines': ('Skylines', lambda n: tile_sky('dusk', skyline=n), 1),
    'sky_objects': ('Sky objects', tile_sky_object, 3),
    'scatter_sets': ('Scatter sets', tile_set, 1),
    'held_items': ('Held items', tile_held, 3),
    'icons': ('Icons', tile_icon, 9),
}


def sheet(tiles, cols, title):
    """Tiles in a grid, each labelled with its name and a dot in its status colour."""
    cw = max(t.width for _, _, t in tiles) + 12
    ch = max(t.height for _, _, t in tiles) + 26
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new('RGB', (cw * min(cols, len(tiles)), ch * rows + 24), BG)
    d = ImageDraw.Draw(out)
    d.text((6, 6), title, fill=(235, 235, 235))
    for i, (name, status, t) in enumerate(tiles):
        x, y = (i % cols) * cw + 6, 24 + (i // cols) * ch
        out.paste(t, (x, y))
        d.ellipse([x, y + t.height + 7, x + 7, y + t.height + 14], fill=STATUS_COLOUR.get(status, (200, 200, 200)))
        d.text((x + 12, y + t.height + 5), f'{name}  ({status})', fill=(225, 225, 225))
    return out


def sheets(picks, statuses, out_dir):
    rows = read_inventory()
    wanted = set(picks)
    sections = {k for k in TILES if k in wanted} or (set(TILES) if not wanted else set())
    names = wanted - set(TILES)
    written = []
    os.makedirs(out_dir, exist_ok=True)
    for key, (sec, tile, cols) in TILES.items():
        groups = defaultdict(list)
        for s, group, name, status, _ in rows:
            if s != sec or (statuses and status not in statuses):
                continue
            if key in sections or name in names:
                groups[group or sec].append((name, status))
        # big sections get one sheet per group, the rest one sheet each
        split = key in ('textures', 'props')
        batches = list(groups.items()) if split else [(sec, [x for g in groups.values() for x in g])]
        for group, items in batches:
            if not items:
                continue
            tiles = [(n, st, tile(n)) for n, st in items]
            slug = key + ('_' + re.sub(r'[^a-z0-9]+', '_', group.lower()).strip('_') if split else '')
            path = os.path.join(out_dir, slug + '.png')
            sheet(tiles, cols, f'{sec}: {group}' if split else sec).save(path)
            written.append(path)
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('sync', help='bring the tables in ASSETS.md up to date')
    sub.add_parser('check', help='exit 1 if ASSETS.md is out of date')
    sp = sub.add_parser('sheets', help='render review sheets')
    sp.add_argument('picks', nargs='*', help=f"sections ({', '.join(TILES)}) or asset names; default all")
    sp.add_argument('--status', default='', help='only these statuses, e.g. polish,rework')
    sp.add_argument('--out', default=SHEETS, help='output folder (default renders/sheets)')
    args = ap.parse_args()

    if args.cmd == 'sheets':
        statuses = [s for s in args.status.split(',') if s]
        for path in sheets(args.picks, statuses, args.out):
            print(os.path.relpath(path, ROOT))
        return
    with open(INVENTORY, encoding='utf-8') as f:
        old = f.read()
    new, changes = sync_text(old)
    bad = [c for c in changes if 'has status' in c or 'is missing' in c]
    if args.cmd == 'check':
        if new != old or bad:
            for c in changes:
                print(c)
            if new != old:
                print('docs/ASSETS.md is out of date: run  python docs/asset_review.py sync')
            sys.exit(1)
        print('docs/ASSETS.md is up to date')
        return
    if new != old:
        with open(INVENTORY, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new)
    for c in changes:
        print(c)
    print('docs/ASSETS.md', 'updated' if new != old else 'already up to date')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

"""Smoke test: every example renders, frames are not blank, the main features run, past bugs stay
fixed, and the docs still match the code.
Run from the repo root:  python tests/smoke_test.py
"""
import glob
import json
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDER = os.path.join(ROOT, 'scripts', 'render.py')


def render(scene_path, out_dir, *flags):
    out = os.path.join(out_dir, os.path.splitext(os.path.basename(scene_path))[0] + '.png')
    res = subprocess.run([sys.executable, RENDER, scene_path, '-o', out, *flags], capture_output=True, text=True)
    assert res.returncode == 0, f'{scene_path} failed:\n{res.stderr}'
    return [p for p in res.stdout.split() if p.endswith('.png')]


def check_frame(path):
    a = np.asarray(Image.open(path).convert('RGB'), np.float32)
    assert a.mean() > 4, f'{path} is nearly black'
    assert a.std() > 4, f'{path} is nearly uniform'


def feature_scene():
    """Small scene exercising pixel-art defs (mirror, alpha, emissive), blends, lights and all overlays."""
    return {
        'map': ['#######', '#ccccc#', '#.~~~.#', '#.....#', '#######'],
        'legend': {'#': {'wall': ['stone', 'window_lit'], 'h': 2}, '.': {'floor': 'checker', 'ceil': None},
                   'c': {'floor': 'checker', 'ceil': 'beams'},
                   '~': {'floor': 'water', 'drop': 0.18}},
        'sky': 'dusk', 'ambient': [0.3, 0.3, 0.3], 'supersample': 2,
        'sprite_defs': {'imp': {'height': 0.4, 'mirror': True, 'emissive': 'e',
                                'palette': {'r': '#8a2020', 'e': '#ffee00', 'a': '#ffffff80'},
                                'pixels': ['..rr', '.rer', 'rrrr', '.aar', '..rr', '.r.r']}},
        'sprites': [
            {'id': 'imp', 'x': 3.5, 'y': 2.0, 'type': 'imp', 'light': True},
            {'x': 2.5, 'y': 2.2, 'type': 'ghost'},
            {'x': 4.6, 'y': 2.2, 'type': 'cultist', 'blend': 'additive', 'opacity': 0.6, 'wobble': 2},
            {'x': 3.5, 'y': 2.5, 'type': 'rowboat'},  # rests on the sunken water, not above it
            {'x': 1.6, 'y': 3.4, 'type': 'rubble'}, {'x': 5.4, 'y': 3.4, 'type': 'grass_tuft'},
            {'x': 5.4, 'y': 1.5, 'type': 'brazier'}, {'x': 1.6, 'y': 1.5, 'type': 'sconce', 'z': 0.7},
        ],
        'decals': [
            {'tex': 'puddle_shine', 'surface': 'floor', 'x': 3.5, 'y': 3.4, 'size': 1.4},
            {'tex': 'crack', 'surface': 'floor', 'x': 2.4, 'y': 3.6, 'size': 1.2, 'opacity': 0.8},
            {'tex': 'puddle_dark', 'surface': 'floor', 'x': 3.5, 'y': 2.5, 'size': 1.0},  # on the sunken plane
            {'tex': 'vines', 'surface': 'wall', 'cell': [3, 0], 'face': 'south', 'u': 0.5, 'z': 1.7, 'size': 0.9},
            {'tex': 'rune_mark', 'surface': 'wall', 'cell': [1, 0], 'face': 'south', 'u': 0.5, 'z': 0.8, 'size': 0.7},
            {'tex': 'stain', 'surface': 'ceiling', 'x': 3.5, 'y': 1.5, 'size': 1.5, 'opacity': 0.7},
        ],
        'camera': {'x': 3.5, 'y': 3.6, 'angle': 270, 'flashlight': True},
        'overlays': [{'type': 'caption', 'text': 'Smoke test', 'box': True}],
        'shots': [
            {'overlays': [{'type': 'bubble', 'anchor': 'imp', 'name': 'Imp', 'text': 'Hello there, traveller.'}]},
            {'overlays': [{'type': 'dialog', 'portrait': 'imp', 'name': 'Imp', 'text': 'A longer line that must wrap.'}]},
            {'overlays': [{'type': 'bubble', 'anchor': 'missing', 'text': 'Anchor not found falls back.'}]},
        ],
    }


def gui_post_scene():
    """Every GUI widget, theme, icon, held item, preset and effect, including JSON-defined icons."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import gui
    import icons
    import post
    icon_names = list(icons.ICONS)
    widgets = [
        {'type': 'viewmodel', 'item': 'revolver'},
        {'type': 'bars', 'items': [{'label': 'HP', 'value': 0.5}, {'label': 'ST', 'value': 1, 'segments': 4}]},
        {'type': 'counter', 'icon': 'ammo', 'value': '6/24', 'label': 'AMMO'},
        {'type': 'hotbar', 'slots': icon_names[:5] + [None, {'icon': 'fuse', 'count': 2}], 'selected': 1, 'numbers': True},
        {'type': 'compass'}, {'type': 'automap', 'markers': [{'x': 2, 'y': 2}], 'title': 'Map'},
        {'type': 'crosshair'}, {'type': 'toast', 'icon': 'key', 'text': 'Found: Key'},
        {'type': 'prompt', 'key': 'E', 'text': 'Open'},
        {'type': 'panel', 'title': 'Goals', 'lines': [{'text': 'One', 'done': True}, {'text': 'Two', 'icon': 'note'}, 'Three']},
        {'type': 'image', 'name': 'skull', 'at': 'left', 'scale': 2},
    ]
    menus = [
        {'type': 'choice', 'prompt': 'Pick one', 'options': ['A', {'text': 'B', 'hint': '1g'}, {'text': 'C', 'disabled': True}],
         'selected': 1, 'pointer': 'hand'},
        {'type': 'title', 'text': 'TITLE', 'subtitle': 'sub', 'band': True, 'at': 'top'},
        {'type': 'inventory', 'items': icon_names[:7] + [{'icon': 'note', 'name': 'Note', 'description': 'Words here.'}],
         'selected': 7, 'columns': 4},
        {'type': 'dialog', 'portrait': 'note', 'name': 'Narrator', 'text': 'An icon works as a portrait.'},
    ]
    shots = [{'overlays': widgets, 'post': ['storm', {'fx': 'lightning', 'x': 0.5}]},
             {'overlays': menus, 'post': [{'fx': 'fade', 'amount': 0.4}]}]
    for vm in icons.VIEWMODELS:
        shots.append({'overlays': [{'type': 'viewmodel', 'item': vm}]})
    shots.append({'overlays': [{'type': 'viewmodel', 'item': 'candle'}]})
    for theme in gui.THEMES:
        shots.append({'overrides': {'ui': {'theme': theme}}, 'overlays': menus[:1]})
    for preset in post.PRESETS:
        shots.append({'post': [preset]})
    for fx in sorted(post.WORLD | post.DISPLAY):
        shots.append({'post': [fx]})
    for pal in list(post.PALETTES) + [16, ['#000000', '#ff0000', '#ffffff']]:
        shots.append({'post': [{'fx': 'palette', 'name': pal} if isinstance(pal, str) else {'fx': 'palette', 'colors': pal}]
                      if not isinstance(pal, int) else [], **({'overrides': {'palette': pal}} if isinstance(pal, int) else {})})
    return {
        'map': ['########', '#......#', '#..##..#', '#......#', '########'],
        'legend': {'#': {'wall': 'brick', 'h': 1}, '.': {'floor': 'tile_floor', 'ceil': None}},
        'sky': 'night', 'ambient': [0.35, 0.35, 0.35],
        'lights': [{'x': 2, 'y': 2, 'radius': 5}],
        'sprites': [{'id': 'g', 'x': 5.5, 'y': 1.6, 'type': 'guard'}],
        'icon_defs': {'fuse': {'size': 16, 'ops': [['rect', [5, 2, 10, 13], '#c8c0a0'], ['poly', [[5, 2], [10, 2], [7, 0]], '#8a9098'],
                                                   ['px', [[7, 7], [8, 8]], '!#ff6020'], ['line', [7, 5, 8, 10], '!#ff6020']]}},
        'viewmodel_defs': {'candle': {'size': [40, 70], 'anchor': 'left', 'light': {'radius': 3, 'color': [1, 0.75, 0.4]},
                                      'ops': [['rect', [14, 20, 24, 69], '#e8e0c8'], ['ellipse', [15, 8, 23, 20], '!#ffd060']]}},
        'camera': {'x': 1.5, 'y': 3.4, 'angle': 315},
        'shots': shots,
    }


def check_effect(tmp):
    """Sunken floors and decals must actually change pixels - a frame that merely renders is not enough."""
    def render_variant(name, mutate):
        sc = json.loads(json.dumps(feature_scene()))
        sc['shots'] = [{}]
        sc['surface_noise'] = 0  # isolate the feature under test from world-space variation
        mutate(sc)
        p = os.path.join(tmp, name + '.json')
        with open(p, 'w') as f:
            json.dump(sc, f)
        out = render(p, tmp)[0]
        return np.asarray(Image.open(out).convert('RGB'), np.float32)

    full = render_variant('fx_full', lambda sc: None)
    no_decals = render_variant('fx_nodecals', lambda sc: sc.update(decals=[]))
    no_drop = render_variant('fx_nodrop', lambda sc: sc['legend']['~'].pop('drop'))
    for label, other in (('decals', no_decals), ('drop', no_drop)):
        diff = float(np.abs(full - other).mean())
        assert diff > 0.25, f'{label} changed nothing in the frame (mean diff {diff:.3f})'
        print(f'ok {label} changes the frame (mean diff {diff:.2f})')


def check_scatter(tmp):
    """Scatter must be deterministic, size-varied, and must not bury cameras or speakers."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import assets as amod
    import render as rmod

    for name, items in amod.DEBRIS_SETS.items():
        unknown = sorted(set(items) - set(amod.SPRITES))
        assert not unknown, f'debris set {name!r} names missing sprites: {unknown}'

    sc = json.loads(json.dumps(feature_scene()))
    sc['scatter'] = [{'of': 'stones', 'density': 1.2, 'seed': 5}]
    a, b = rmod.World(sc), rmod.World(sc)
    assert a.scatter_sprites, 'scatter produced nothing'
    assert a.scatter_sprites == b.scatter_sprites, 'scatter is not deterministic for a fixed seed'
    assert len({s['scale'] for s in a.scatter_sprites}) > 2, 'scatter used only one size'

    keep = a._keep_clear(sc)
    assert keep, 'no keep-clear zones derived from cameras and anchored sprites'
    for s in a.scatter_sprites:
        half = 0.5 * s['scale'] * amod.sprite_aspect(s['type'])
        for kx, ky, kr in keep:
            d2 = (s['x'] - kx) ** 2 + (s['y'] - ky) ** 2
            assert d2 >= (kr + half) ** 2 - 1e-6, (
                f"{s['type']} at ({s['x']}, {s['y']}) intrudes on a keep-clear zone")
    # nothing should end up inside a wall
    for s in a.scatter_sprites:
        assert a.height[int(s['y']), int(s['x'])] <= 0, f"{s['type']} scattered inside a wall"
    print(f'ok scatter is deterministic and clear of cameras ({len(a.scatter_sprites)} props)')

    # grime drives all three systems in the same direction
    counts = []
    for g in (0.0, 0.5, 1.0):
        gs = json.loads(json.dumps(feature_scene()))
        gs['grime'] = g
        w = rmod.World(gs)
        r = rmod.Renderer(w, gs)
        counts.append((len(w.scatter_sprites),
                       sum(len(v) for v in w.wall_decals.values()) + len(w.floor_decals),
                       r.sn_amount))
    for i in range(2):
        assert counts[i + 1][0] >= counts[i][0] and counts[i + 1][1] > counts[i][1] \
            and counts[i + 1][2] > counts[i][2], f'grime did not scale everything up: {counts}'
    print(f'ok grime scales debris, decals and surface noise together {counts[0]} -> {counts[2]}')


def check_surface_noise(tmp):
    """Surface variation must be anchored in world space, not screen space.

    Screen-anchored noise would crawl over the image as the camera moves and would not break up
    texture tiling. Render the same wall from two distances and compare the noise residual: if it
    were a screen-space overlay the two residuals would be near identical.
    """
    def frame(cam, amount, tag):
        sc = json.loads(json.dumps(feature_scene()))
        sc['shots'] = [cam]
        sc['overlays'] = []
        sc['surface_noise'] = amount
        p = os.path.join(tmp, tag + '.json')
        with open(p, 'w') as f:
            json.dump(sc, f)
        return np.asarray(Image.open(render(p, tmp)[0]).convert('RGB'), np.float32)

    # `amount` is documented as the typical brightness swing, which only holds while the
    # normalisation constant matches the octave blend. Changing the weights or periods without
    # re-measuring NOISE_TYPICAL would quietly make the parameter lie about its own strength.
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import render as rmod
    rng = np.random.default_rng(0)
    probe = type('P', (), {'sn': rmod.noise_field(), 'sn_scale': 1.0,
                           'surface_variation': rmod.Renderer.surface_variation})()
    typical = float(np.abs(probe.surface_variation(rng.random(200000) * 60,
                                                   rng.random(200000) * 60, 0.0)).mean())
    assert 0.9 < typical < 1.1, (
        f'surface noise is not normalised: mean |variation| is {typical:.2f}, so "amount" is off '
        f'by {1 / typical:.1f}x. Re-measure NOISE_TYPICAL after changing weights or periods.')
    print(f'ok surface noise amount is honest (mean |variation| {typical:.2f} per unit)')

    # every built-in material needs a variation factor, or a new texture silently inherits 1.0
    import assets as amod
    missing = sorted(set(amod.TEXTURES) - set(amod.TEXTURE_NOISE))
    stale = sorted(set(amod.TEXTURE_NOISE) - set(amod.TEXTURES))
    assert not missing, f'textures with no TEXTURE_NOISE factor: {missing}'
    assert not stale, f'TEXTURE_NOISE names no such texture: {stale}'
    assert amod.texture_noise({'base': 'cobble'}) == amod.texture_noise('cobble'), \
        'a tinted variant should inherit its base material factor'
    print(f'ok every material has a variation factor ({len(amod.TEXTURE_NOISE)} of them)')

    # by_texture must override the material factor outright
    sc = json.loads(json.dumps(feature_scene()))
    sc['surface_noise'] = {'amount': 0.10, 'by_texture': {'checker': 0.45}}
    world = rmod.World(sc)
    amounts = dict(zip(world.tex_key, rmod.Renderer(world, sc).tex_amount))
    assert abs(amounts['checker'] - 0.45) < 1e-6, f"by_texture ignored: {amounts['checker']}"
    assert abs(amounts['water'] - 0.10 * amod.TEXTURE_NOISE['water']) < 1e-6, \
        'a material not named in by_texture should keep its own factor'
    print('ok by_texture overrides one material and leaves the rest alone')

    near = {'x': 3.5, 'y': 3.6, 'angle': 270, 'flashlight': False}
    far = {'x': 3.5, 'y': 2.9, 'angle': 270, 'flashlight': False}
    res_a = frame(near, 0.14, 'sn_a_on') - frame(near, 0.0, 'sn_a_off')
    res_b = frame(far, 0.14, 'sn_b_on') - frame(far, 0.0, 'sn_b_off')
    mag = float(np.abs(res_a).mean())
    assert mag > 0.2, f'surface_noise changed nothing (mean |residual| {mag:.3f})'
    corr = float(np.corrcoef(res_a.ravel(), res_b.ravel())[0, 1])
    assert corr < 0.75, f'surface noise looks screen-anchored (residual correlation {corr:.2f})'
    print(f'ok surface noise is world-anchored (|residual| {mag:.2f}, cross-camera corr {corr:+.2f})')


def check_regressions(tmp):
    """One check per bug found in the release audit, so none of them can quietly come back."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import assets
    import gui
    import pixelfont
    import post
    import render as R

    room = {'map': ['#######', '#.....#', '#.....#', '#.....#', '#######'],
            'legend': {'#': {'wall': 'stone', 'h': 1}, '.': {'floor': 'cobble'}},
            'sky': 'dusk', 'ambient': [0.5, 0.5, 0.5], 'camera': {'x': 3.5, 'y': 3.5, 'angle': 270}}
    pebble = {'height': 0.2, 'palette': {'g': '#888888'}, 'pixels': ['.gg.', 'gggg', '.gg.']}

    def frame(scene):
        w = R.World(scene)
        return R.Renderer(w, scene).render(R.prepare_shot(scene, dict(scene['camera'])))

    def write(path, scene, encoding='utf-8'):
        with open(path, 'w', encoding=encoding) as f:
            json.dump(scene, f, ensure_ascii=False)
        return path

    def cli(*args, cwd=None):
        return subprocess.run([sys.executable, RENDER, *args], capture_output=True, text=True,
                              encoding='utf-8', errors='replace', cwd=cwd)

    # 1. scene files are UTF-8 (BOM included, as PowerShell writes them) whatever the locale is
    p = write(os.path.join(tmp, 'utf8.json'), dict(room, overlays=[
        {'type': 'caption', 'text': 'Ángel — don’t… café'}]), 'utf-8-sig')
    check_frame(render(p, tmp)[0])

    # 2. text an LLM writes lands on real glyphs, not '?'
    font = pixelfont.PixelFont()
    s = font._norm('café Zürich Ñandú naïve ¿sí? 10 PM «quote» a‑b — don’t… straße ø ~^{}|\\`')
    missing = sorted({c for c in s if c != ' ' and c not in font.glyphs})
    assert not missing, f'pixel font draws these as "?": {missing}'

    # 3. scatter accepts the scene's own pixel-art sprites, at their own height
    sc = dict(room, sprite_defs={'pebble': pebble},
              scatter=[{'of': 'pebble', 'density': 1, 'sizes': ['medium']}])
    placed = R.World(sc).scatter_sprites
    assert placed and all(abs(s['scale'] - 0.2) < 1e-6 for s in placed), placed[:2]

    # 4. every widget that takes an icon also takes a sprite_defs name; choice allows no selection
    frame(dict(room, sprite_defs={'pebble': pebble}, overlays=[
        {'type': 'image', 'name': 'pebble'}, {'type': 'hotbar', 'slots': ['key', 'pebble']},
        {'type': 'panel', 'lines': [{'text': 'x', 'icon': 'pebble'}]},
        {'type': 'choice', 'options': ['a', 'b'], 'selected': None}]))

    # 5. long text stays inside the frame
    for ov in ({'type': 'title', 'text': 'THE HOSPITAL ON THE HILL', 'scale': 4, 'subtitle': 'word ' * 40},
               {'type': 'panel', 'title': 'Objectives', 'lines': [{'text': 'word ' * 40, 'done': False}]},
               {'type': 'toast', 'icon': 'key', 'text': 'Found: ' + 'very ' * 30 + 'long key'}):
        ctx = gui.Ctx(Image.new('RGBA', (320, 200), (0, 0, 0, 0)), {}, {})
        gui.WIDGETS[ov['type']](ctx, ov)
        x0, _, x1, _ = ctx.layer.getbbox()
        assert x0 > 0 and x1 < 320, f"{ov['type']} runs off the frame: x {x0}..{x1}"

    # 6. "off" values for post effects mean off, not a crash or NaNs
    img = np.full((40, 40, 3), 0.5, np.float32)
    for fx in ({'fx': 'posterize', 'levels': 1}, {'fx': 'pixelate', 'factor': 1}):
        assert np.isfinite(post.apply_world(img, [fx], {'seed': 0})).all(), fx
    for fx in ({'fx': 'chromatic', 'offset': 0}, {'fx': 'vhs', 'bleed': 0}):
        post.apply_display(np.full((40, 40, 3), 128, np.uint8), [fx], {'scale': 2, 'seed': 0})

    # 7. surface noise darkens rough materials hard at full grime but never inverts them
    gs = dict(room, grime=1.0)
    r = R.Renderer(R.World(gs), gs)
    g = np.mgrid[0:120:0.07, 0:120:0.07]
    var = r.surface_variation(g[1].ravel(), g[0].ravel())
    mult = 1 + R.soft_swing(r.sn_amount * assets.texture_noise('cobble') * var)
    assert mult.min() > 0.05, f'albedo multiplier reaches {mult.min():.3f}'
    small = np.linspace(-0.5, 0.5, 11)
    assert np.allclose(R.soft_swing(small), small), 'soft_swing must leave small swings alone'

    # 8. relative asset paths resolve beside the scene file, wherever the renderer runs from
    sub = os.path.join(tmp, 'assets_beside')
    os.makedirs(sub, exist_ok=True)
    Image.new('RGB', (8, 8), (200, 40, 40)).save(os.path.join(sub, 'red.png'))
    p = write(os.path.join(sub, 'scene.json'),
              dict(room, legend={'#': {'wall': 'red.png', 'h': 1}, '.': {'floor': 'cobble'}}))
    res = cli(p, '-o', os.path.join(tmp, 'beside.png'), cwd=tmp)
    assert res.returncode == 0, res.stderr[-300:]

    # 9. CLI: a bad --shot is an error, a bare -o still writes a PNG, misspelt keys are flagged
    p = write(os.path.join(tmp, 'cli.json'), dict(room, ligths=[], _note='comments are fine'))
    res = cli(p, '-o', os.path.join(tmp, 'cli'), '--shot', '5')
    assert res.returncode != 0 and 'out of range' in res.stderr, res.stderr[-200:]
    res = cli(p, '-o', os.path.join(tmp, 'bare'))
    assert res.returncode == 0 and os.path.exists(os.path.join(tmp, 'bare.png')), res.stderr[-200:]
    assert "unknown key 'ligths'" in res.stderr and "'lights'" in res.stderr, res.stderr
    assert '_note' not in res.stderr, 'underscore keys are comments and must not warn'
    for ex in sorted(glob.glob(os.path.join(ROOT, 'examples', '*.json'))):
        warnings = R.lint_scene(R.load_scene(ex))
        assert not warnings, (os.path.basename(ex), warnings)

    # 10. --map shows scattered props
    sc = dict(room, scatter=[{'of': 'stones', 'density': 2}])
    mp = os.path.join(tmp, 'scattermap.png')
    R.draw_map(R.World(sc), sc, [sc['camera']], mp)
    px = np.asarray(Image.open(mp).convert('RGB')).reshape(-1, 3)
    assert (px == (120, 132, 84)).all(axis=1).any(), 'scatter missing from --map'

    # 11. a wall standing in sunken water carries on down to the water surface
    pool = {'map': ['##########', '#~~~~~~~~#', '#~~~~~~~~#', '#~~~~~~~~#', '#........#',
                    '#........#', '##########'],
            'legend': {'#': {'wall': 'brick', 'h': 1.4}, '.': {'floor': 'boards'},
                       '~': {'floor': 'water', 'drop': 0.25}},
            'ceiling_height': 1.4, 'sky': 'dusk', 'ambient': [0.55, 0.55, 0.6], 'surface_noise': 0,
            'camera': {'x': 5.0, 'y': 5.3, 'angle': 270, 'fov': 74, 'pitch': -0.12}}
    img = frame(pool)
    H, W = img.shape[:2]
    horizon = H / 2 - 0.12 * H
    proj = (W / 2) / math.tan(math.radians(74) / 2)
    dist = 5.3 - 1.0                                  # camera to the far wall's face

    def row(z):
        return int(horizon - (z - 0.5) * proj / dist)
    lum = img.mean(axis=2)[:, W // 2 - 20: W // 2 + 20]
    above, below = lum[row(0.35):row(0.05)].mean(), lum[row(-0.05):row(-0.2)].mean()
    assert below > 0.75 * above, f'wall under the waterline is {below / above:.2f}x the wall above'

    # 12. grime never leaves a wall decal hanging off its face
    with open(os.path.join(ROOT, 'examples', 'bunker_lab.json'), encoding='utf-8') as f:
        w = R.World(dict(json.load(f), grime=1.0))
    over = [d for lst in w.wall_decals.values() for d in lst
            if d['u'] - d['size'] / 2 < -1e-6 or d['u'] + d['size'] / 2 > 1 + 1e-6]
    assert not over, f'{len(over)} grime wall decals overhang their face'
    print('ok release regressions (12 checks)')


def check_docs():
    """The docs name assets, keys and counts by hand: fail as soon as they and the code disagree."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    sys.path.insert(0, os.path.join(ROOT, 'docs'))
    import assets
    import build_gallery
    import gui
    import icons
    import post
    import render as R
    from characters import CHARACTERS

    def read(*parts):
        with open(os.path.join(ROOT, *parts), encoding='utf-8') as f:
            return f.read()
    ref, skill, readme = read('references', 'scene_format.md'), read('SKILL.md'), read('README.md')

    def section(text, heading):
        i = text.index(heading)
        j = text.find('\n## ', i + len(heading))
        return text[i:j if j > 0 else None]

    problems = []

    def need(where, text, names):
        gone = sorted(n for n in names
                      if not re.search(r'(?<![a-z0-9_])' + re.escape(n) + r'(?![a-z0-9_])', text))
        if gone:
            problems.append(f'{where} does not mention {gone}')

    need('reference/Sprites', section(ref, '## Sprites'), list(assets.SPRITES) + list(CHARACTERS))
    need('reference/Decals', section(ref, '## Decals'), assets.DECALS)
    need('reference/GUI', section(ref, '## GUI'),
         list(icons.ICONS) + list(icons.VIEWMODELS) + list(gui.THEMES) + list(gui.WIDGETS))
    need('reference/Post-processing', section(ref, '## Post-processing'),
         list(post.PRESETS) + list(post.PALETTES) + sorted(post.WORLD | post.DISPLAY))
    need('reference/Scatter', section(ref, '## Scatter'),
         list(assets.DEBRIS_SETS) + list(assets.SIZE_CLASSES))
    meta = {'title', 'description', 'notes'}
    need('reference (scene keys)', ref,
         sorted((R.SCENE_KEYS | R.SHOT_KEYS | R.CELL_KEYS) - meta))
    need('SKILL.md (scatter sets)', skill, assets.DEBRIS_SETS)

    counts = {r'(\d+) procedural props': len(assets.SPRITES), r'(\d+) stamps': len(assets.DECALS),
              r'(\d+) item icons': len(icons.ICONS) - 2, r'(\d+)-character': len(CHARACTERS),
              r'(\d+) one-word presets': len(post.PRESETS)}
    for pat, n in counts.items():
        m = re.search(pat, readme)
        if not m or int(m.group(1)) != n:
            problems.append(f"README says {m.group(0) if m else pat!r}, the code has {n}")
    m = re.search(r'Built-in props \((\d+)\)', ref)
    if not m or int(m.group(1)) != len(assets.SPRITES):
        problems.append(f'reference prop count is stale (code has {len(assets.SPRITES)})')

    linked = set(re.findall(r'docs/gallery/([\w-]+)\.png', readme))
    problems += [f'README links missing image {n}.png' for n in sorted(linked - build_gallery.ALL)]
    problems += [f'gallery builds {n}.png but the README never shows it'
                 for n in sorted(build_gallery.ALL - linked)]
    problems += [f'docs/gallery/{n} is not built by docs/build_gallery.py' for n in build_gallery.unmanaged()]
    for name, (ex, shot) in build_gallery.SHOTS.items():
        sc = R.load_scene(os.path.join(ROOT, 'examples', ex + '.json'))
        if not 1 <= shot <= len(sc.get('shots') or [sc.get('camera')]):
            problems.append(f'gallery {name}: {ex} has no shot {shot}')
    assert not problems, 'docs and code disagree:\n  ' + '\n  '.join(problems)
    print('ok docs match the code (asset lists, counts, scene keys, gallery)')


def main():
    with tempfile.TemporaryDirectory() as tmp:
        scenes = sorted(glob.glob(os.path.join(ROOT, 'examples', '*.json')))
        assert scenes, 'no example scenes found'
        for sc in scenes:
            for p in render(sc, tmp, '--map', '--sheet'):
                check_frame(p)
            print('ok', os.path.basename(sc))
        fs = os.path.join(tmp, 'features.json')
        with open(fs, 'w') as f:
            json.dump(feature_scene(), f)
        outs = render(fs, tmp)
        assert len(outs) == 3
        for p in outs:
            check_frame(p)
        print('ok features')
        check_effect(tmp)
        check_surface_noise(tmp)
        check_scatter(tmp)
        check_regressions(tmp)
        check_docs()
        gs = os.path.join(tmp, 'gui_post.json')
        with open(gs, 'w') as f:
            json.dump(gui_post_scene(), f)
        outs = render(gs, tmp)
        for p in outs:
            check_frame(p)
        print(f'ok gui and post ({len(outs)} frames)')
        sys.path.insert(0, os.path.join(ROOT, 'scripts'))
        import assets
        assets.catalog(os.path.join(tmp, 'catalog.png'))
        print('ok catalog')
    print('all passed')


if __name__ == '__main__':
    main()

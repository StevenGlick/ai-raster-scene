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


def check_new_features():
    """Each engine feature from the castle/cave/winter release has to change the picture the way
    the reference says it does, not merely run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import assets
    import maptools
    import render as R

    flat = {'ambient': [0.6, 0.6, 0.6], 'surface_noise': 0, 'light_levels': 0, 'sky': 'dusk'}

    def frame(scene):
        w = R.World(scene)
        return R.Renderer(w, scene).render(R.prepare_shot(scene, R.merge_camera(scene, scene['camera'])))

    # 1. look_at aims the camera, an [x, y, z] target also pitches it, and a shot's own angle wins
    sc = {'sprites': [{'id': 'npc', 'x': 4.0, 'y': 1.0, 'type': 'guard'}]}
    assert abs(R.resolve_camera(sc, {'x': 1, 'y': 1, 'look_at': [2, 2]})['angle'] - 45) < 1e-6
    assert abs(R.resolve_camera(sc, {'x': 1, 'y': 1, 'look_at': 'npc'})['angle']) < 1e-6
    assert R.resolve_camera(sc, {'x': 1, 'y': 1, 'look_at': [5, 1, 1.5]})['pitch'] > 0
    try:
        R.resolve_camera(sc, {'x': 1, 'y': 1, 'look_at': 'nobody'})
        raise AssertionError('look_at at a missing sprite id must fail loudly')
    except KeyError:
        pass
    shot = R.merge_camera(dict(sc, camera={'x': 1, 'y': 1, 'look_at': [2, 2]}), {'angle': 180})
    assert abs(shot['angle'] - 180) < 1e-6, 'a shot angle must override an inherited look_at'

    # 2. see-through walls: the floor carries on under them, light passes, sprites show through
    def yard(wall):
        return dict(flat, map=['#######', '#.....#', '#.....#', '#.fff.#', '#.....#', '#.....#', '#######'],
                    legend={'#': {'wall': 'stone', 'h': 1}, '.': {'floor': 'cobble'}, 'f': {'wall': wall, 'h': 1}},
                    camera={'x': 3.5, 'y': 5.5, 'angle': 270},
                    lights=[{'x': 3.5, 'y': 1.5, 'z': 0.8, 'radius': 5, 'intensity': 1.5}],
                    sprites=[{'x': 3.5, 'y': 1.8, 'type': 'guard', 'fullbright': True, 'tint': [3, 3, 3]}])
    w = R.World(yard('bars'))
    assert w.see[3, 2:5].all() and (w.solid_h[3, 2:5] == 0).all(), 'bars must be see-through'
    assert (w.floor_tid[3, 2:5] == w.floor_tid[4, 3]).all(), 'a fence must stand on the floor around it'

    def lit_in_front(scene):
        r = R.Renderer(R.World(scene), scene)
        return float(R.sample_lm(r.lm, r.lres, np.array([3.5]), np.array([4.6])).sum())
    assert lit_in_front(yard('bars')) > 2 * lit_in_front(yard('stone')) + 1e-3, 'bars must not block light'
    seen = lambda scene: np.abs(frame(scene) - frame(dict(scene, sprites=[]))).sum()   # noqa: E731
    assert seen(yard('bars')) > 20, 'a sprite behind bars must show through the gaps'
    assert seen(yard('stone')) < 1e-6, 'a stone wall in the same place must hide it'
    rail = assets.get_alpha('railing')
    assert 1 - np.nonzero((rail > 0.5).any(axis=1))[0].min() / rail.shape[0] < 0.45, \
        'a railing must stay below eye height (0.5) so it can be looked over'

    # 3. heights: a digit layer makes low blocks whose tops show; sprites stand on them; roofs cover them
    dais = dict(flat, map=['#######', '#.....#', '#..B..#', '#.....#', '#.....#', '#######'],
                heights=['.......', '.......', '...3...', '.......', '.......', '.......'],
                legend={'#': {'wall': 'stone', 'h': 1}, '.': {'floor': 'cobble'},
                        'B': {'wall': 'stone', 'top': 'carpet'}},
                camera={'x': 3.5, 'y': 4.5, 'angle': 270})
    w = R.World(dais)
    assert abs(w.height[2, 3] - 0.3) < 1e-6 and abs(w.base_z(3.5, 2.5) - 0.3) < 1e-6
    img = frame(dais)
    proj = 160 / math.tan(math.radians(66) / 2)
    top_row = int(100 + 0.5 * ((0.2 * proj / 2.5) + (0.2 * proj / 1.5)))   # between the top's far and near edges
    face_row = int(100 + 0.5 * ((0.2 * proj / 1.5) + (0.5 * proj / 1.5)))  # halfway down the near face
    r, g, b = img[top_row, 150:170].mean(axis=0)
    assert r > 1.3 * g, f'the top of a low block shows its "top" texture (got rgb {r:.2f} {g:.2f} {b:.2f})'
    r, g, b = img[face_row, 150:170].mean(axis=0)
    assert r < 1.3 * g, 'the face of a low block shows its wall texture'
    roofed = dict(dais, legend=dict(dais['legend'], **{'.': {'floor': 'cobble', 'ceil': 'beams'}}))
    assert R.World(roofed).ceil_tid[2, 3] >= 0, 'a low block under a roof must get the roof above it'

    # 4. sun and moon: walls cast shadows away from the light, roofs block it, the disc is drawn
    field = dict(flat, map=['..........', '..........', '....##....', '..........', '..........'],
                 legend={'#': {'wall': 'stone', 'h': 1}, '.': {'floor': 'grass'}},
                 camera={'x': 4.5, 'y': 4.5, 'angle': 270, 'fov': 70})
    sun = R.build_sun(R.World(field), {'type': 'sun', 'azimuth': 270, 'elevation': 30})
    zl = lambda x, y: sun['zlit'][int(y * sun['res']), int(x * sun['res'])]   # noqa: E731
    assert zl(4.5, 3.5) > 0 > zl(8.5, 3.5) and zl(4.5, 1.5) < 0, 'a wall must shadow the far side only'
    covered = dict(field, legend=dict(field['legend'], **{'.': {'floor': 'grass', 'ceil': 'beams'}}))
    cov = R.build_sun(R.World(covered), {'type': 'sun'})
    deep = R.sun_visibility(cov, np.array([8.5, 1.5]), np.array([3.5, 1.5]), np.array([0.0, 0.0]))
    assert deep.max() < 0.05, 'no sunlight reaches a floor deep under a roof'
    with_disc = dict(field, sky='day', camera={'x': 4.5, 'y': 3.5, 'angle': 90, 'fov': 70},  # open sky
                     lights=[{'type': 'sun', 'azimuth': 90, 'elevation': 12}])
    no_disc = dict(with_disc, lights=[{'type': 'sun', 'azimuth': 90, 'elevation': 12, 'disc': False}])
    disc_row = int(100 - math.tan(math.radians(12)) * 160 / math.tan(math.radians(35)))
    patch = lambda img: img[disc_row - 3:disc_row + 4, 155:166].mean()     # noqa: E731
    assert patch(frame(with_disc)) > patch(frame(no_disc)) + 0.03, 'the sun disc must show in the sky'

    # 5. reflections: water mirrors the lit windows beyond it, and "reflections": false turns that off
    lake = dict(flat, ambient=[0.15, 0.15, 0.18], sky=None,
                map=['#########', '#.......#', '#~~~~~~~#', '#~~~~~~~#', '#.......#', '#########'],
                legend={'#': {'wall': 'window_lit', 'h': 1}, '.': {'floor': 'boards', 'ceil': 'beams'},
                        '~': {'floor': 'water', 'drop': 0.1, 'ceil': 'beams'}},
                camera={'x': 4.5, 'y': 4.6, 'angle': 270})
    on, off = frame(lake), frame(dict(lake, reflections=False))
    water = slice(165, 200)                                  # the near half of the pool
    assert on[water].max() > off[water].max() + 0.05, 'lit windows must glint in the water'
    assert np.abs(on[:95] - off[:95]).max() < 1e-6, 'reflections must only touch the floor'

    # 6. skylines paint the horizon band of the sky and nothing above it
    plain = assets.make_sky('dusk', 720, 120)
    for kind in assets.SKYLINES:
        sky = assets.make_sky('dusk', 720, 120, skyline=kind, proj=proj)
        assert np.abs(sky[-6:] - plain[-6:]).max() > 0.02, f'skyline {kind} draws nothing'
        assert np.abs(sky[:30] - plain[:30]).max() < 1e-6, f'skyline {kind} reaches the zenith'

    # 7. contact shadows: under floor props only, scaled by the scene setting, and they darken the floor
    room = dict(flat, map=['#####', '#...#', '#...#', '#...#', '#####'],
                legend={'#': {'wall': 'stone', 'h': 1}, '.': {'floor': 'tile_floor'}},
                camera={'x': 2.5, 'y': 3.6, 'angle': 270},
                sprites=[{'x': 2.5, 'y': 1.6, 'type': 'barrel'}, {'x': 1.5, 'y': 1.5, 'type': 'lantern', 'z': 0.7}])
    shadows = R.World(room)._contact_shadows(room)
    assert len(shadows) == 1, f'expected one contact shadow (barrel only), got {len(shadows)}'
    off_room = dict(room, contact_shadows=0)
    assert not R.World(off_room)._contact_shadows(off_room), 'contact_shadows: 0 must turn them off'
    assert frame(room)[150:200].mean() < frame(dict(room, contact_shadows=0))[150:200].mean() - 1e-4

    # 8. void floors: the sky carries on under the horizon, and an island across the void shows
    #    its cliff; sprites over a void stand at their own z
    def islands(far):
        legend = {' ': {'floor': 'void'}, 'g': {'floor': 'grass', 'side': 'rock'}}
        g = maptools.Grid(21, 21, fill=' ').disc(10, 18, 2.2, 'g')
        if far:
            g.disc(10, 7, 3.2, 'g')
        return dict(flat, sky='day', map=g.rows(), legend=legend, camera={'x': 10.5, 'y': 18.5, 'angle': 270})
    w = R.World(islands(True))
    assert w.void[0, 0] and not w.void[18, 10] and w.base_z(0.5, 0.5) == 0.0
    near_sky = frame(islands(False))
    assert near_sky[104:112, 150:170].mean() > 0.3, 'void must show the sky below the horizon, not black'
    cliff = frame(islands(True))[128:150, 150:170].mean()
    assert cliff < near_sky[128:150, 150:170].mean() - 0.1, 'an island across the void must show its cliff'

    # 9. sky objects and the new presets paint the panorama, and the sky wraps round 360 seamlessly
    plain = assets.make_sky('dusk', 720, 120, proj=proj)
    for kind in assets.SKY_OBJECTS:
        sky = assets.make_sky('dusk', 720, 120, proj=proj,
                              objects=[{'type': kind, 'azimuth': 90, 'elevation': 15, 'size': 8}])
        assert np.abs(sky - plain).max() > 0.1, f'sky object {kind} draws nothing'
    try:
        assets.make_sky('dusk', 720, 120, objects=[{'type': 'teapot'}])
        raise AssertionError('an unknown sky object must fail loudly')
    except KeyError:
        pass
    for preset in assets.SKY_PRESETS:
        sky = assets.make_sky(preset, 720, 120, proj=proj, below=40)
        assert sky.shape == (160, 720, 3) and sky[120:].mean() > 0.01, f'{preset} has nothing under the horizon'
        assert np.abs(sky[:, 0] - sky[:, -1]).mean() < 0.02, f'{preset} has a seam at 0/360 degrees'

    # 10. Grid.disc leaves no one-cell nub at its extremes
    g = maptools.Grid(21, 21, fill='#').disc(10, 10, 8, '.')
    for lines in (g.g, list(zip(*g.g))):                  # rows, then columns
        edge = [ln for ln in lines if '.' in ln]
        assert edge[0].count('.') > 1 and edge[-1].count('.') > 1, 'a whole-number radius left a nub'
    print('ok new features (look_at, see-through, heights, sun, reflections, skyline, contact shadows, '
          'void floors, sky objects)')


def check_atmosphere():
    """Volumetric fog, light through openings, weather, wet ground, back views and the render
    report each have to do what the reference promises, not merely run."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import assets
    import render as R
    import weather
    from characters import CHARACTERS

    def frame(scene, report=None):
        w = R.World(scene)
        rr = R.Renderer(w, scene)
        img = rr.render(R.prepare_shot(scene, R.merge_camera(scene, scene['camera'])))
        if report is not None:
            report.extend(rr.last_report)
        return img

    field = {'map': ['.' * 24] * 24, 'legend': {'.': {'floor': 'grass'}}, 'sky': 'dusk',
             'ambient': [0.5, 0.5, 0.5], 'surface_noise': 0, 'light_levels': 0,
             'camera': {'x': 12, 'y': 22, 'angle': 270}}

    # 1. ground fog lies low: it changes the view along the ground far more than the sky overhead
    clear = frame(field)
    misty = frame(dict(field, fog={'color': [0.8, 0.8, 0.85], 'density': 0.0, 'ground': 0.8, 'height': 0.3}))
    low = np.abs(misty[100:130] - clear[100:130]).mean()
    high = np.abs(misty[:25] - clear[:25]).mean()
    assert low > 3 * high + 0.02, f'ground fog must lie low (near the horizon {low:.3f}, overhead {high:.3f})'

    # 2. sunlight comes into a roofed room through its doorway, and only there
    rows = ['##########', '#........#', '#........#', '#........#', '####..####']
    room = dict(field, map=rows + ['          '] * 3, sky='day',
                legend={'#': {'wall': 'stone', 'h': 1.0}, '.': {'floor': 'flagstone', 'ceil': 'beams'},
                        ' ': {'floor': 'grass'}},
                lights=[{'type': 'sun', 'azimuth': 90, 'elevation': 25}], camera={'x': 5, 'y': 2, 'angle': 270})
    sun = R.build_sun(R.World(room), room['lights'][0])
    lit = lambda x, y: float(R.sun_visibility(sun, np.array([x]), np.array([y]), np.array([0.0]))[0])   # noqa: E731
    assert lit(5.0, 3.6) > 0.9, 'the floor just inside the doorway must catch the sun'
    assert lit(2.0, 3.6) < 0.1 and lit(5.0, 1.2) < 0.1, 'the rest of the roofed room must stay out of it'

    # 3. shafts and glow put light into the air
    hall = dict(room, ambient=[0.05, 0.05, 0.05], fog={'color': [0.03, 0.03, 0.03], 'density': 0.15, 'shafts': 0},
                camera={'x': 2.0, 'y': 2.0, 'angle': 0})
    beams = dict(hall, fog=dict(hall['fog'], shafts=2.0))
    assert frame(beams).mean() > frame(hall).mean() + 0.003, 'sun shafts must light the fog'
    lamp = dict(hall, lights=[{'x': 6.5, 'y': 2.0, 'z': 0.6, 'radius': 3, 'intensity': 1.5}])
    halo = dict(lamp, fog=dict(hall['fog'], glow=2.0))
    assert frame(halo)[60:140, 150:250].mean() > frame(lamp)[60:140, 150:250].mean() + 0.01, 'lamps must glow in fog'

    # 4. weather stays out from under roofs and behind walls
    w = R.World(room)
    ctx = {'seed': 1, 'shape': (200, 320), 'world': w, 'depth': np.full((200, 320), np.inf, np.float32),
           'rays': {'px': 5.0, 'py': 7.0, 'rdx': np.full(320, 0.0) + np.linspace(-0.6, 0.6, 320),
                    'rdy': np.full(320, -1.0), 'horizon': 100.0, 'proj': 246.0, 'camz': 0.5}}
    sx, sy, t, z, fade = weather.place(ctx, np.random.default_rng(0), 3000, 0.0, 3.0)
    col = np.clip(sx.astype(int), 0, 319)
    cx = np.floor(5.0 + ctx['rays']['rdx'][col] * t).astype(int)
    cy = np.floor(7.0 - t).astype(int)
    inside = (cy >= 0) & (cy < w.mh) & (cx >= 0) & (cx < w.mw)
    roofed = inside & (w.ceil_tid[np.clip(cy, 0, w.mh - 1), np.clip(cx, 0, w.mw - 1)] >= 0) & (z < w.ceil_h)
    assert len(t) > 100 and not roofed.any(), 'rain must not fall under a roof'
    ctx['depth'] = np.full((200, 320), 2.0, np.float32)
    sx, sy, t, z, fade = weather.place(ctx, np.random.default_rng(0), 3000, 0.0, 3.0)
    assert len(t) > 0 and (t < 2.0).all(), 'particles must hide behind anything nearer'

    # 5. wet ground: open floors turn mirror-like, roofed ones stay dry
    wet = R.World(dict(room, wet=0.8))
    assert wet.reflect[6, 4] > 0.25 and wet.reflect[2, 4] == 0.0

    # 6. every character has a back the size of its front, and `facing` picks it
    for name, d in CHARACTERS.items():
        front, _ = assets.get_sprite(name)
        back, _ = assets.get_sprite(name, view='back')
        assert front.shape == back.shape, name
        assert np.abs(front - back).max() > 0 or name == 'ghost', f'{name} looks the same from behind'
    stage = dict(field, sprites=[{'id': 'k', 'x': 12.0, 'y': 19.0, 'type': 'knight', 'facing': 90}])
    away = dict(stage, sprites=[dict(stage['sprites'][0], facing=270)])
    assert np.abs(frame(stage) - frame(away)).max() > 0.05, 'facing away from the camera must show the back'

    # 7. the render report catches what it says it does, and stays quiet on a good frame
    notes = []
    frame(stage, notes)
    assert not notes, notes
    for scene, expect in (
            (dict(field, ambient=[0.01, 0.01, 0.01], sky=None,
                  legend={'.': {'floor': 'grass', 'ceil': 'beams'}}), 'very dark'),
            (dict(stage, map=['.' * 24] * 20 + ['.' * 10 + '####' + '.' * 10] + ['.' * 24] * 3,
                  legend={'.': {'floor': 'grass'}, '#': {'wall': 'stone', 'h': 2}},
                  camera={'x': 12.0, 'y': 21.6, 'look_at': 'k'}), 'hidden'),
            (dict(stage, map=['.' * 24] * 22 + ['.' * 12 + '#' + '.' * 11] + ['.' * 24],
                  legend={'.': {'floor': 'grass'}, '#': {'wall': 'stone', 'h': 2}},
                  camera={'x': 12.5, 'y': 22.5, 'angle': 270}), 'inside a wall')):
        notes = []
        frame(scene, notes)
        assert any(expect in n for n in notes), (expect, notes)
    print('ok fog, light through openings, weather, wet ground, back views, render report')


def check_pixel_art():
    """The pixel-art toolkit and what it drew: textures tile, ramps shift hue the way an artist
    would, cut-out holes show what is behind them, and the beach's surf is visible from eye height."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import assets
    import biomes
    import pixelart as px
    import render as R

    # 1. a shape stamped across the edge of a tiling canvas comes round the other side
    cv = px.Canvas(32)
    cv.ellipse(1.0, 16.0, 4.0, 3.0)
    assert cv.id[16, 31] and cv.id[16, 0], 'stamps must wrap round a tiling canvas'
    sprite = px.Canvas(32, wrap=False)
    sprite.ellipse(1.0, 16.0, 4.0, 3.0)
    assert not sprite.id[16, 31], 'a sprite canvas must not wrap'

    # 2. every texture drawn with the toolkit tiles: the step across its edge, row against row (or
    # column against column), is no bigger than the biggest step inside it - a mortar joint may
    # fall on the edge, a seam would stand out from every joint. Only solid pixels count, and a
    # single storey (a cornice, a doorway, a crest) only has to tile sideways.
    storey = {'colonnade_top', 'colonnade_broken', 'temple_cornice', 'temple_door', 'roof_comb'}
    for name in biomes.TEXTURES:
        rgb, _ = assets.get_texture(name)
        alpha = assets.get_alpha(name)
        solid = np.ones(rgb.shape[:2], bool) if alpha is None else alpha > 0.5
        for axis in (1,) if name in storey else (1, 0):
            step = np.abs(np.roll(rgb, -1, axis) - rgb).mean(axis=2)          # pixel to its next neighbour
            pairs = solid & np.roll(solid, -1, axis)
            lines = [np.take(step, i, axis)[np.take(pairs, i, axis)] for i in range(rgb.shape[axis])]
            means = [ln.mean() if ln.size else 0.0 for ln in lines]
            wrap, inside = means[-1], max(means[:-1])
            assert wrap <= inside * 1.1 + 0.01, f'{name} shows a seam when tiled ({wrap:.3f} vs {inside:.3f})'

    # 3. ramps run dark to light, shadows cooler (bluer) and highlights warmer than the base
    rp = px.ramp('#5a8a3a')
    lum = rp @ np.array([0.3, 0.59, 0.11])
    assert (np.diff(lum) > 0).all(), 'a ramp must climb from shadow to highlight'
    warmth = (rp[:, 0] - rp[:, 2]) / (rp.sum(1) + 1e-6)
    assert warmth[0] < warmth[-1], 'shadows must be cooler than highlights'

    # 4. a cut punches a hole through a pasted layer and shows what was drawn before
    cv = px.Canvas(24, wrap=False)
    cv.box(2, 2, 20, 20, mat=1)
    top, cut = cv.layer(), cv.layer()
    top.box(4, 4, 16, 16, z=2.0, mat=0)
    cut.ellipse(12, 12, 3, 3)
    cv.paste(top, cut)
    assert cv.mat[12, 12] == 1 and cv.mat[6, 6] == 0, 'a cut must show the layer underneath'

    # 5. surf on the waterline reads from a standing eye height (a foam decal would be edge-on)
    beach = {'map': ['ssssss......'] * 12, 'legend': {'.': {'floor': 'beach_sand'}, 's': {'floor': 'shallows'}},
             'sky': 'day', 'ambient': [0.5, 0.5, 0.5], 'surface_noise': 0,
             'camera': {'x': 10.5, 'y': 9.5, 'look_at': [4.0, 5.0, 0.2], 'fov': 70}}

    def frame(scene):
        w = R.World(scene)
        return R.Renderer(w, scene).render(R.prepare_shot(scene, R.merge_camera(scene, scene['camera'])))
    surf = dict(beach, sprites=[{'x': 5.6, 'y': y + 0.5, 'type': 'surf'} for y in range(12)])
    changed = (np.abs(frame(surf) - frame(beach)).max(axis=2) > 0.1).sum()
    assert changed > 40, f'the surf line must show from eye height ({changed} pixels changed)'

    # 6. islands leave open sky down to the horizon between them
    plain = assets.make_sky('sunset', 720, 90)
    isles = assets.make_sky('sunset', 720, 90, skyline='islands')
    same = np.abs(plain[-1] - isles[-1]).max(axis=1) < 1e-6
    assert same.mean() > 0.5 and not same.all(), 'islands must sit apart on an open horizon'
    print('ok pixel-art toolkit, tiling, ramps, cut-outs, surf, islands')


def check_planes_prefabs():
    """Planar sprites, fringes and prefabs do what the reference says: crosses stand at the
    right angles, a card faces one way, layers follow a wall's outline, and a prefab lands
    turned, remapped and identical for the same seed."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import assets
    import prefabs
    import render as R

    # 1. a star is three planes 60 degrees apart, a cross two at right angles, a card repeats
    fern, _ = assets.get_sprite('fern')
    for n, want in ((2, [0, 90]), (3, [0, 60, 120])):
        quads = R.Renderer.plane_quads({'x': 5.0, 'y': 5.0, 'type': 'fern', 'planes': n, 'angle': 0}, fern)
        got = sorted(round(math.degrees(math.atan2(q[3] - q[1], q[2] - q[0])) % 180) for q in quads)
        assert got == want, (n, got)
    card = R.Renderer.plane_quads({'x': 0, 'y': 0, 'planes': 1, 'angle': 0, 'length': 6.0, 'scale': 1.0}, fern)
    assert abs(card[0][4] - 6.0 / (fern.shape[1] / fern.shape[0])) < 1e-6, 'a card repeats its image along its length'

    # 2. a card is drawn face-on and all but vanishes edge-on, and a wall in front hides it
    field = {'map': ['.' * 12] * 12, 'legend': {'.': {'floor': 'grass'}, '#': {'wall': 'stone', 'h': 2}},
             'sky': None, 'ambient': [0.6, 0.6, 0.6], 'surface_noise': 0, 'light_levels': 0,
             'camera': {'x': 6.0, 'y': 10.5, 'angle': 270}}

    def frame(scene):
        w = R.World(scene)
        return R.Renderer(w, scene).render(R.prepare_shot(scene, R.merge_camera(scene, scene['camera'])))

    def covered(scene, base):
        return int((np.abs(frame(scene) - base).max(axis=2) > 0.05).sum())
    base = frame(field)
    wide = {'x': 6.0, 'y': 6.0, 'type': 'jungle_card_4', 'planes': 1, 'length': 4.0}
    face_on = covered(dict(field, sprites=[dict(wide, angle=0)]), base)
    edge_on = covered(dict(field, sprites=[dict(wide, angle=90)]), base)
    assert face_on > 20 * max(edge_on, 1), f'a card must face its own way ({face_on} face-on, {edge_on} edge-on)'
    walled = dict(field, map=['.' * 12] * 8 + ['....####....'] + ['.' * 12] * 3, sprites=[dict(wide, angle=0)])
    hidden = covered(walled, frame(dict(walled, sprites=[])))
    assert hidden < face_on * 0.2, 'a wall in front of a card must hide it'

    # 3. a fringe lays one card per layer along a wall's open face, inside the cell in front,
    # and wraps all the way round a lone block; a camera standing in it keeps its spot clear
    row = dict(field, map=['#' * 12] + ['.' * 12] * 11,
               legend={'.': {'floor': 'grass'}, '#': {'wall': 'jungle_leaves', 'h': 3, 'fringe': 'jungle'}})
    w = R.World(row)
    layers = sorted(sp['y'] for sp in w.fringe_sprites)
    assert len(layers) == 4 and all(1.0 < y < 2.0 for y in layers), layers
    assert all(sp['angle'] == 0 and abs(sp['length'] - 12) < 1e-6 for sp in w.fringe_sprites)
    lone = dict(row, map=['.' * 12] * 5 + ['.....#......'] + ['.' * 12] * 6)
    cards = R.World(lone).fringe_sprites
    assert len(cards) == 16, 'four faces, four layers each'
    back = [sp for sp in cards if abs(sp['length'] - (1 + 2 * 0.125)) < 1e-6]
    assert len(back) == 4, 'the innermost layer wraps the outside corners'
    near = dict(row, camera={'x': 6.0, 'y': 1.6, 'angle': 90})
    assert len(R.World(near).fringe_sprites) < 4, 'a card through a camera position is left out'

    # 4. a prefab with a map turns in quarter turns and gets fresh legend characters
    sc = {'map': ['.' * 11] * 11, 'legend': {'.': {'floor': 'beach_sand'}}, 'camera': {'x': 1.5, 'y': 1.5, 'angle': 0},
          'prefabs': [{'type': 'beach_hut', 'x': 5.5, 'y': 5.5, 'angle': 90}]}
    ex = prefabs.expand(sc)
    hut = prefabs.PREFABS['beach_hut']['legend']
    floors = {k for k, v in ex['legend'].items() if v == hut['d']}
    walls = {k for k, v in ex['legend'].items() if v == hut['h']}
    assert floors and walls and not (floors | walls) & set(sc['legend']), 'prefab characters must not clash'
    assert ex['map'][7][5] in floors and ex['map'][7][4] in walls and ex['map'][7][6] in walls, \
        'at 90 degrees the door, east at 0, faces south'
    torches = [sp for sp in ex['sprites'] if sp['type'] == 'tiki_torch']
    assert all(abs(sp['y'] - 8.5) < 1e-6 for sp in torches), 'its torches turn with it'
    assert prefabs.expand(ex) is ex and prefabs.expand({'map': ['.']}) is not None

    # 5. the same seed gives the same group, nested prefabs and wall decals turn with their parent
    grove = lambda seed: prefabs.expand(dict(sc, prefabs=[{'type': 'palm_grove', 'x': 5, 'y': 5, 'seed': seed}]))  # noqa: E731
    assert grove(3)['sprites'] == grove(3)['sprites'] and grove(3)['sprites'] != grove(4)['sprites']
    defs = {'nook': {'map': ['W'], 'legend': {'W': {'wall': 'stone', 'h': 1}},
                     'decals': [{'tex': 'moss_patch', 'surface': 'wall', 'cell': [0, 0], 'face': 'south'}],
                     'sprites': [{'type': 'lantern', 'dx': 0, 'dy': 1.0, 'id': 'lamp'}]},
            'pair': {'prefabs': [{'type': 'nook', 'dx': 2.0, 'dy': 0}]}}
    ex = prefabs.expand(dict(sc, prefab_defs=defs, prefabs=[{'type': 'pair', 'x': 5.5, 'y': 5.5, 'angle': 90, 'id': 'p'}]))
    assert ex['map'][7][5] != '.', 'a nested prefab lands where its turned parent puts it'
    assert ex['decals'][0]['face'] == 'west' and ex['decals'][0]['cell'] == [5, 7]
    lamp = [sp for sp in ex['sprites'] if sp['type'] == 'lantern'][0]
    assert abs(lamp['x'] - 4.5) < 1e-6 and abs(lamp['y'] - 7.5) < 1e-6, (lamp['x'], lamp['y'])

    # 6. look_at finds an id inside a prefab, and the lint catches a misspelt placement key
    shot = R.merge_camera(dict(sc, prefabs=[{'type': 'street_lamp', 'x': 8.5, 'y': 1.5, 'id': 'lamp'}],
                               prefab_defs={'street_lamp': dict(prefabs.PREFABS['street_lamp'],
                                                                sprites=[{'type': 'lamp_post', 'id': 'post'}])}),
                          {'x': 1.5, 'y': 1.5, 'look_at': 'lamp.post'})
    assert abs(shot['angle']) < 1e-6
    assert R.lint_scene(dict(sc, prefabs=[{'type': 'campsite', 'x': 1, 'y': 1, 'angel': 30}]))
    print('ok planar sprites, fringe layers, prefabs (turns, remaps, seeds, nesting, ids)')


def check_glass_facades():
    """The glass pass shows what is behind a pane, tinted and blurred as asked, and a facade cuts
    a street front into buildings whose layers line up and stand in the right order."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    import buildings
    import render as R

    # 1. frost shrinks by k (each block averaged) and blows back up without smoothing
    a = np.arange(16, dtype=np.float32).reshape(4, 4, 1)
    f = R.frost(a, 2)
    assert f[0, 0, 0] == f[1, 1, 0] == (0 + 1 + 4 + 5) / 4 and f[2, 2, 0] == (10 + 11 + 14 + 15) / 4
    g = R.glass_spec(True)
    assert g['blur'] == 1 and 0 < g['opacity'] < 0.5 and g['tint'][2] >= g['tint'][0]

    # 2. through clear glass with no reflection, the wall behind shows exactly, times the tint;
    # through the default blur a striped wall comes out smoother
    room = {'map': ['######', '......', '......', '......'], 'sky': None, 'ambient': [0.8, 0.8, 0.8],
            'legend': {'#': {'wall': 'brick', 'h': 1.0}, '.': {'floor': 'concrete_floor'}},
            'surface_noise': 0, 'light_levels': 0, 'camera': {'x': 3.0, 'y': 3.5, 'angle': 270, 'fov': 60}}

    def frame(scene):
        w = R.World(scene)
        return R.Renderer(w, scene).render(R.prepare_shot(scene, R.merge_camera(scene, scene['camera'])))
    pane = {'x': 3.0, 'y': 2.0, 'type': 'glass_pane', 'angle': 0, 'length': 4.0, 'scale': 1.0}
    bare = frame(room)
    tinted = frame(dict(room, sprites=[dict(pane, glass={'opacity': 0.0, 'blur': 0, 'tint': [0.5, 1.0, 1.0]})]))
    win = (slice(70, 120), slice(120, 200))
    assert np.allclose(tinted[win][..., 0], bare[win][..., 0] * 0.5, atol=0.02), 'glass must tint what is behind'
    assert np.allclose(tinted[win][..., 1:], bare[win][..., 1:], atol=0.02)
    sharp = frame(dict(room, sprites=[dict(pane, glass={'opacity': 0.0, 'blur': 0, 'tint': [1, 1, 1]})]))
    soft = frame(dict(room, sprites=[dict(pane, glass={'opacity': 0.0, 'blur': 1, 'tint': [1, 1, 1]})]))
    rough = lambda im: np.abs(np.diff(im[win], axis=1)).mean()   # noqa: E731
    assert rough(soft) < rough(sharp) * 0.8, 'the default glass must blur what is behind it'

    # 3. a facade cuts a straight front into buildings, five layers each, back to front
    street = {'map': ['B' * 20] * 3 + ['.' * 20] * 6, 'sky': None, 'ambient': [0.5, 0.5, 0.5],
              'legend': {'B': {'wall': 'brick_dark', 'h': 3, 'facade': {'style': 'brick', 'widths': [3, 5],
                                                                             'storeys': [3, 6], 'seed': 4}},
                         '.': {'floor': 'flagstone'}},
              'camera': {'x': 10.0, 'y': 8.5, 'angle': 270}}
    sprites = R.World(street).fringe_sprites
    fronts = [sp for sp in sprites if '"layer":"wall"' in sp['type']]
    widths = sorted(round(sp['length'], 3) for sp in fronts)
    assert abs(sum(widths) - 20) < 1e-6 and all(3 <= w_ <= 5 or w_ == widths[-1] for w_ in widths), widths
    order = {}
    for sp in sprites:
        if sp['type'].startswith('facade:') and '"layer":"side"' not in sp['type']:
            order.setdefault(json.loads(sp['type'][7:])['layer'], set()).add(round(sp['y'], 4))
    assert max(order['room']) < min(order['drape']) < min(order['frame']) <= min(order['wall']), order
    assert order['glass'] == order['frame'] and all(sp.get('glass') for sp in sprites if '"layer":"glass"' in sp['type'])
    heights = [sp['scale'] for sp in fronts]
    sides = [sp for sp in sprites if '"layer":"side"' in sp['type']]
    steps = sum(1 for h0, h1 in zip(heights, heights[1:]) if h0 != h1)
    assert len(sides) == steps and all(sp['z'] >= 3 for sp in sides), 'a taller building shows a side wall'

    # 4. a corner building has one look on both its faces; a north face is read the right way round
    block = dict(street, map=['....'.ljust(12, '.')] * 2 + ['....BBBBBBBB'] * 6 + ['.' * 12] * 4,
                 camera={'x': 1.5, 'y': 11.5, 'angle': 300})
    fronts = [sp for sp in R.World(block).fringe_sprites if '"layer":"wall"' in sp['type']]
    corner = [json.loads(sp['type'][7:]) for sp in fronts
              if abs(sp['x'] - sp['length'] / 2 - 3.0) < 1e-6 or abs(sp['y'] - sp['length'] / 2 - 1.0) < 1e-6]
    looks = {c['look'] for c in corner}
    assert len(corner) >= 2 and len(looks) < len(corner), 'the building at the corner must turn it whole'
    assert all(sp['flip'] for sp in fronts if abs(sp['y'] - 1.0) < 1e-6), 'a north face reads left to right'

    # 5. every window is an opening in the wall, and glass in the glass layer
    params = dict(style='brick', w=5, h=4, look=7, seed=9, lit=0.5)
    wall, _ = buildings.layer_image(buildings.layer_name('wall', **params))
    pane, _ = buildings.layer_image(buildings.layer_name('glass', **params))
    holes = wall[..., 3] < 0.5
    assert holes.any() and (pane[..., 3][holes] > 0.5).mean() > 0.6, 'the glass must sit in the openings'

    # 6. the wall is as thick as the frames are set back in it, and a card with `reveal` shows the
    # far side of its openings from an angle - nearer than what was seen through them, from
    # either side - while its own face is untouched
    al = np.ones((6, 8))
    al[2:4, 3:6] = 0
    assert [int(r_[3, 4]) for r_ in R.hole_runs(al)] == [3, 6, 2, 4]
    gap = max(order['wall']) - max(order['frame'])
    assert all(gap <= sp['reveal'] < gap + 0.05 for sp in R.World(street).fringe_sprites if '"layer":"wall"' in sp['type'])
    card = {'x': 4.5, 'y': 3.0, 'type': buildings.layer_name('wall', **params), 'planes': 1, 'angle': 0,
            'length': 5.0, 'scale': 4.0}
    yard = dict(room, map=['#' * 9] + ['#.......#'] * 8 + ['#' * 9])

    def depth_of(scene, cam):
        r = R.Renderer(R.World(scene), scene)
        r.render(R.prepare_shot(scene, R.merge_camera(scene, cam)))
        return r.depth.copy()
    for cam in ({'x': 1.6, 'y': 7.4, 'angle': 312, 'fov': 70}, {'x': 7.4, 'y': 7.4, 'angle': 228, 'fov': 70}):
        flat = depth_of(dict(yard, sprites=[card]), cam)
        thick = depth_of(dict(yard, sprites=[dict(card, reveal=0.2)]), cam)
        assert (thick < flat - 1e-4).sum() > 200, 'an opening seen at an angle must show its far side'
        assert (thick <= flat + 1e-6).all(), 'the sides of an opening never push anything further away'

    # 7. a neon street: its signs glow in the wall layer, and blade signs stand out square to the front
    neon = dict(street, legend=dict(street['legend'], B={'wall': 'brick_dark', 'h': 3, 'facade': {
        'style': 'neon', 'widths': [3, 5], 'storeys': [3, 6], 'seed': 4}}))
    sprites = R.World(neon).fringe_sprites
    blades = [sp for sp in sprites if '"layer":"blade"' in sp['type']]
    assert blades and all(sp['angle'] == 90.0 and sp['planes'] == 1 for sp in blades), 'blade signs square to the front'
    assert all(4.0 < sp['y'] < 4.0 + sp['length'] for sp in blades), 'a blade sign stands out over the street'
    walls = [sp for sp in sprites if '"layer":"wall"' in sp['type']]
    assert any(buildings.layer_image(sp['type'])[1].max() > 0.5 for sp in walls), 'neon signs glow'
    assert buildings.layer_image(blades[0]['type'])[1].max() > 0.5
    print('ok glass pass (tint, blur), facades (buildings, layers, corners, side walls, reveals, neon)')


def check_docs():
    """The docs name assets, keys and counts by hand: fail as soon as they and the code disagree."""
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    sys.path.insert(0, os.path.join(ROOT, 'docs'))
    import assets
    import build_gallery
    import gui
    import icons
    import buildings
    import post
    import prefabs
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
    need('SKILL.md (cast)', skill, CHARACTERS)
    need('reference (skylines)', ref, assets.SKYLINES)
    need('reference (sky presets and objects)', ref, list(assets.SKY_PRESETS) + list(assets.SKY_OBJECTS))
    need('reference/Prefabs', section(ref, '## Prefabs'), prefabs.PREFABS)
    need('SKILL.md (prefabs)', skill, prefabs.PREFABS)
    need('reference (fringe sets)', ref, assets.FRINGES)
    need('reference (facade styles)', section(ref, '## Cell specs'), buildings.FACADE_STYLES)
    need('reference/Textures (see-through and emissive)', section(ref, '## Textures'),
         [t for t in assets.TEXTURES if assets.get_alpha(t) is not None or assets.get_texture(t)[1] is not None])

    counts = {r'(\d+) procedural props': len(assets.SPRITES), r'(\d+) stamps': len(assets.DECALS),
              r'(\d+) item icons': len(icons.ICONS) - 2, r'(\d+)-character': len(CHARACTERS),
              r'(\d+) one-word presets': len(post.PRESETS), r'(\d+) textures': len(assets.TEXTURES)}
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

    # the asset inventory: its rows, usage columns and counts are kept in step by asset_review.py
    import asset_review
    inventory = read('docs', 'ASSETS.md')
    synced, changes = asset_review.sync_text(inventory)
    if synced != inventory or changes:
        problems += [f'docs/ASSETS.md: {c}' for c in changes] or ['docs/ASSETS.md is out of date']
        problems.append('(run  python docs/asset_review.py sync)')
    assert not problems, 'docs and code disagree:\n  ' + '\n  '.join(problems)
    print('ok docs match the code (asset lists, counts, scene keys, gallery, asset inventory)')


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
        check_new_features()
        check_atmosphere()
        check_pixel_art()
        check_planes_prefabs()
        check_glass_facades()
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

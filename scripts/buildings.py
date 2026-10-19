"""Building facades in layers, for wall cells with a `facade`.

A street drawn the raycaster's usual way is a flat textured wall: the windows are painted on.
A facade is drawn instead as layers of planes standing one behind another in the cell in front
of a building's walls, each building on the street with its own images:

    wall    brick (or plaster) with openings for windows and door, sills, lintels, a cornice
    frame   window frames and glazing bars, and the door
    glass   the panes, drawn last by the glass pass: what is behind them, tinted and blurred
    drape   curtains, blinds, shutters or net curtains, a different choice in every window
    room    the rooms behind: lit or dark, a lamp, a picture, a shelf, now and then a figure
    roof    (village styles) the roof over the street: a gable end, or the slope of thatch or tiles

so a window has a reveal, the glass sits in it, the curtains hang behind the glass and the room
is further back still, and as the camera moves the layers slide against each other. The wall is
drawn as thick as the frames are set back in it (the renderer's `reveal`), so from an angle an
opening shows its brick jamb, the underside of its lintel and its sill, not a gap.

Every building has two seeds. Its `look` - colour, height, frame paint, whether it keeps a
shop - is shared by both faces of a corner building, so it turns the corner whole; its `seed`
lays out each face's windows. The renderer names each layer image `facade:` plus its
parameters, and get_sprite draws it on first use.
"""
import json
from functools import lru_cache

import numpy as np

from pixelart import Canvas, ramp, smooth_noise

PX = 64            # pixels per world unit, as the textures; a storey is a unit tall

FACADE_STYLES = {
    'brick': {
        'description': 'red and brown brick, painted sash windows, curtains and blinds',
        'colors': ['#8a3e2c', '#7a3428', '#6e4a36', '#8a5a3e', '#6a3a2c', '#9a5038', '#7a4a3a',
                   '#a0784e', '#6a5a50', '#5a2e26', '#94604a', '#7e6450'],
        'mortar': '#5a5048', 'trim': '#b8b0a0',
        'frames': ['#e4e0d4', '#e4e0d4', '#2a2a2a', '#3a4a3a', '#5a2a22'],
        'doors': ['#2a3a2a', '#5a2a1a', '#1a1a20', '#3a2a1a'],
        'bay': (1.1, 1.5), 'shops': 0.35, 'courses': True,
    },
    'sooty': {
        'description': 'soot-blackened brick tenements, dark frames, the windows mostly dark',
        'colors': ['#4a3a34', '#3e3430', '#55402e', '#4a3028', '#3a3632'],
        'mortar': '#3a3632', 'trim': '#8a8478',
        'frames': ['#1e1e20', '#2a2a2a', '#3a3a34', '#c8c4b8'],
        'doors': ['#1a1a1a', '#2a2018', '#1e2420'],
        'bay': (0.9, 1.2), 'shops': 0.2, 'courses': False,
    },
    'plaster': {
        'description': 'washed plaster in faded colours, shutters at most windows',
        'colors': ['#c8b48a', '#c09a80', '#a8b0a0', '#d0c4a8', '#b89a70', '#c8a8a0'],
        'mortar': '#a09a88', 'trim': '#e0dccc',
        'frames': ['#e8e4d8', '#3a5a4a', '#5a6a7a'],
        'doors': ['#3a5a4a', '#5a3a2a', '#4a4a5a'],
        'bay': (1.2, 1.6), 'shops': 0.3, 'courses': True, 'plaster': True,
    },
    'neon': {
        'description': 'dark concrete blocks hung with neon: signs on the walls and blade signs standing out over '
                       'the street, shutters half down, rooms lit pink, blue and green',
        'colors': ['#3c404a', '#35383f', '#42393f', '#2f353b', '#3d3b46', '#38403e'],
        'mortar': '#1e2026', 'trim': '#5c6068',
        'frames': ['#1a1c20', '#2a2d33', '#3a3036'],
        'doors': ['#1a1a1e', '#262a30', '#2e2228'],
        'bay': (0.9, 1.2), 'shops': 0.85, 'courses': False, 'concrete': True, 'neon': True, 'blades': 2,
        'room_tints': [(1.0, 0.32, 0.72), (0.32, 0.6, 1.0), (0.45, 1.0, 0.75), (1.0, 0.72, 0.38), (0.7, 0.45, 1.0)],
    },
    'timber': {
        'description': 'a village of timber-framed houses: limewashed or ochre plaster between dark oak posts, rails '
                       'and braces, leaded casements, plank doors, and over the street a gable end or a roof of '
                       'thatch or tiles, some with a chimney',
        'colors': ['#e8e2d0', '#e6dcc2', '#efe6cc', '#dcc8a0', '#e2c8b2', '#d8b8a6', '#d4d6c8'],
        'mortar': '#c8c0a8', 'trim': '#3a2c22',
        'frames': ['#2e241c', '#3a2e24', '#4a3e30', '#2e3a2e'],
        'doors': ['#3a2a1c', '#4a3424', '#2a3a2a', '#5a2a1a', '#2a2e3a'],
        'bay': (1.0, 1.3), 'shops': 0.3, 'courses': False, 'plaster': True, 'timber': True,
        'timber_colors': ['#2a1e16', '#33261c', '#3e3026', '#4e4236', '#5c544a'],
        'roofs': ['thatch', 'thatch', 'tile'], 'gables': 0.5,
    },
}

# the colours neon comes in: pink, cyan, gold, violet, green
NEON = [(1.0, 0.24, 0.66), (0.25, 0.95, 1.0), (1.0, 0.8, 0.25), (0.66, 0.42, 1.0), (0.35, 1.0, 0.5)]

DRAPE_COLORS = ['#7a2a2a', '#8a6a2a', '#2a5a3a', '#d8cfb8', '#3a3a6a', '#6a3a5a', '#c8b890']


def pick_style(style, look):
    """A building's style: the one named, or for a list one of them, chosen by its look (so both
    faces of a corner building agree)."""
    if isinstance(style, (list, tuple)):
        return style[int(np.random.default_rng((int(look) + 977) % (2 ** 32)).integers(len(style)))]
    return style


def layer_name(layer, **params):
    """The sprite name of one layer image: `facade:` and its parameters, which draw it."""
    return 'facade:' + json.dumps({'layer': layer, **params}, sort_keys=True, separators=(',', ':'))


def layer_image(name):
    """(rgba, emissive) for a `facade:` sprite name."""
    p = json.loads(name[len('facade:'):])
    layer = p.pop('layer')
    if layer == 'side':
        return _side(p)
    if layer == 'blade':
        return _blade(p)
    if layer == 'roof':
        return _roof(p)
    plan = _plan(json.dumps(p, sort_keys=True))
    return {'wall': _wall, 'frame': _frame, 'glass': _glass, 'drape': _drape, 'room': _room}[layer](plan)


def _surface(S):
    """What a style's walls are made of: 'brick', 'plaster' or 'concrete'."""
    return 'concrete' if S.get('concrete') else 'plaster' if S.get('plaster') else 'brick'


def _rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


# ------------------------------------------------------------------ the plan of one face

@lru_cache(maxsize=256)
def _plan(key):
    """Where everything goes on one building face: windows by storey and bay, the door, a
    shopfront, and what is in each window. Every layer draws from the same plan, so a window's
    frame, glass, curtains and room all line up with the opening in the wall."""
    p = json.loads(key)
    S = FACADE_STYLES[pick_style(p.get('style', 'brick'), p.get('look', 0))]
    look = np.random.default_rng(int(p.get('look', 0)) % (2 ** 32))
    rng = np.random.default_rng(int(p.get('seed', 0)) % (2 ** 32))
    W, H = max(8, int(round(float(p['w']) * PX))), max(PX, int(round(float(p['h']) * PX)))
    storeys = max(1, H // PX)
    color = _rgb(S['colors'][look.integers(len(S['colors']))]) * float(look.uniform(0.88, 1.12))
    frame = _rgb(S['frames'][look.integers(len(S['frames']))])
    door_col = _rgb(S['doors'][look.integers(len(S['doors']))])
    shop = look.random() < float(p.get('shops', S['shops']))
    lit = float(p.get('lit', 0.35))
    bays = max(1, int(round(W / PX / look.uniform(*S['bay']))))
    bay_w = W / bays
    win_w = int(min(bay_w - 10, bay_w * look.uniform(0.4, 0.52)))
    win_h = int(PX * look.uniform(0.46, 0.56))
    door_bay = int(rng.integers(bays))
    windows, door = [], None
    for st in range(storeys):
        floor_y = H - st * PX                    # the bottom row of this storey
        for b in range(bays):
            cx = int((b + 0.5) * bay_w)
            if st == 0 and b == door_bay:
                dw, dh = int(PX * 0.42), int(PX * 0.8)
                door = (cx - dw // 2, floor_y - dh, cx + dw // 2, floor_y)
                continue
            if st == 0 and shop:
                continue
            y1 = floor_y - int(PX * 0.28)
            windows.append({'box': (cx - win_w // 2, y1 - win_h, cx + win_w // 2, y1), 'storey': st})
    if shop and door is not None:
        x0 = 6 if door[0] > W / 2 else door[2] + 6
        x1 = door[0] - 6 if door[0] > W / 2 else W - 6
        if x1 - x0 > PX * 0.6:
            windows.append({'box': (x0, H - int(PX * 0.78), x1, H - int(PX * 0.14)), 'storey': 0, 'shop': True})
    for wnd in windows:
        r = rng.random()
        if wnd.get('shop'):                       # a shop window: no curtains, lit more often
            wnd.update(drape='none', drape_color=None, lit=rng.random() < min(0.9, lit * 1.6), warm=True,
                       motif='shop', split=0.0)
            continue
        wnd['drape'] = ('none' if r < 0.3 else 'curtains' if r < 0.62 else 'blind' if r < 0.8
                        else 'shutters' if r < 0.9 else 'net')
        wnd['drape_color'] = _rgb(DRAPE_COLORS[rng.integers(len(DRAPE_COLORS))])
        wnd['lit'] = rng.random() < lit
        wnd['warm'] = rng.random() < 0.85                 # most rooms lamp-lit, a few blue with a screen
        wnd['motif'] = str(rng.choice(['lamp', 'picture', 'shelf', 'plant', 'figure', 'empty'],
                                      p=[0.3, 0.2, 0.2, 0.12, 0.08, 0.1]))
        wnd['split'] = rng.uniform(0.18, 0.38)
    signs, acs = [], []
    if S.get('neon'):
        for wnd in windows:
            if wnd.get('shop'):
                wnd['neon'] = NEON[int(rng.integers(len(NEON)))]
                wnd['shutter'] = float(rng.uniform(0.3, 1.0)) if rng.random() < 0.4 else 0.0
            else:
                wnd['tint'] = S['room_tints'][int(rng.integers(len(S['room_tints'])))]
                if wnd['storey'] >= 1 and rng.random() < 0.3:               # an air conditioner under it
                    x0, y0, x1, y1 = wnd['box']
                    cx = (x0 + x1) // 2 + int(rng.integers(-4, 5))
                    acs.append((cx - 7, y1 + 5, cx + 7, y1 + 15))
        if bays > 1 and storeys >= 3:                                  # a tall sign between two bays
            x = int(int(rng.integers(1, bays)) * bay_w)
            top = H - int(PX * rng.uniform(2.3, min(storeys - 0.2, 4.4)))
            signs.append({'box': (x - 6, top, x + 6, H - int(PX * 1.1)), 'color': NEON[int(rng.integers(len(NEON)))]})
    return {'W': W, 'H': H, 'storeys': storeys, 'color': color, 'frame': frame, 'door_col': door_col,
            'mortar': _rgb(S['mortar']), 'trim': _rgb(S['trim']), 'windows': windows, 'door': door,
            'signs': signs, 'acs': acs, 'bays': bays, 'bay_w': bay_w,
            'style': S, 'seed': int(p.get('seed', 0)), 'look': int(p.get('look', 0))}


# ------------------------------------------------------------------ the layers

@lru_cache(maxsize=8)
def _brick_tile(kind='brick'):
    """A seamless 64x64 tile of neutral brick, plaster or concrete, lit from the upper left: a
    building's colour is multiplied in, so every building shades the same way whatever its colour."""
    rng = np.random.default_rng({'brick': 17, 'plaster': 18, 'concrete': 19}[kind])
    cv = Canvas(PX, ground=-0.6, mat=1)
    if kind == 'concrete':                          # cast panels, four to a unit, with form-tie holes
        for j in range(2):
            for i in range(2):
                cv.box(i * 32 + 0.5, j * 32 + 0.5, 31, 31, z=0.0, top=0.6, bevel=1.0, mat=0, tone=rng.normal(0, 0.05))
                for tx, ty in ((8, 8), (24, 8), (8, 24), (24, 24)):
                    cv.ellipse(i * 32 + tx, j * 32 + ty, 1.1, 1.1, dome=0.6, mode='carve')
        cv.noise(0.22, cells=6, rng=rng, octaves=3)
    elif kind == 'plaster':
        cv.z[:] = 0.0
        cv.mat[:] = 0
        cv.noise(0.35, cells=6, rng=rng, octaves=3)
        for _ in range(5):                          # cracks and patched render
            x, y = rng.random() * PX, rng.random() * PX
            cv.ellipse(x, y, rng.uniform(3, 7), rng.uniform(2, 5), dome=0.15, mode='carve', rough=0.4, rng=rng)
    else:
        for row in range(16):                       # bricks 8 x 4: a brick course every 4 pixels
            off = 4 if row % 2 else 0
            for col in range(-1, 9):
                cv.box(col * 8 + off + 0.5, row * 4 + 0.5, 7, 3, z=0, top=1.0, bevel=0.8, rough=0.15, rng=rng,
                       mat=0, tone=float(rng.normal(0, 0.08)))
        cv.noise(0.1, cells=12, rng=rng)
    shade = cv.light(relief=1.0, cavity=0.35, shadow=0.4)
    neutral = ramp(['#3a3a3a', '#5a5a5a', '#787878', '#949494', '#b0b0b0', '#c8c8c8'])
    k = len(neutral)
    idx = np.clip(np.round(np.clip(shade + cv.tone, 0, 1) * (k - 1)), 0, k - 1).astype(int)
    lum = neutral[idx][..., 0]
    return lum, cv.mat == 1                        # brightness, and where the mortar is


def _shade_rect(rgb, box, color, bevel=1, light=1.15, dark=0.7):
    """A flat block of colour with a lit top-left edge and a dark bottom-right one."""
    x0, y0, x1, y1 = box
    rgb[y0:y1, x0:x1] = color
    rgb[y0:y0 + bevel, x0:x1] = np.clip(color * light, 0, 1)
    rgb[y0:y1, x0:x0 + bevel] = np.clip(color * light, 0, 1)
    rgb[y1 - bevel:y1, x0:x1] = color * dark
    rgb[y0:y1, x1 - bevel:x1] = color * dark


def _wall(plan):
    """Brick (or plaster) with openings: sills and lintels round the windows, a surround to the
    door, a plinth, string courses, a cornice, and soot that runs down under the sills."""
    W, H, S = plan['W'], plan['H'], plan['style']
    lum, mortar = _brick_tile(_surface(S))
    ty, tx = np.arange(H) % PX, (np.arange(W) + plan['seed'] * 7) % PX
    L = lum[np.ix_(ty, tx)]
    m = mortar[np.ix_(ty, tx)]
    rgb = np.where(m[..., None], plan['mortar'][None, None, :] * (0.55 + 0.6 * L[..., None]),
                   plan['color'][None, None, :] * (0.45 + 0.95 * L[..., None]))
    rng = np.random.default_rng(plan['seed'] + 5)
    soot = smooth_noise(W, H, max(2, W // 48), rng, wrap=False, cells_y=2)
    rgb *= (0.84 + 0.22 * soot)[..., None]
    top = np.clip(1 - np.arange(H) / (H * 0.6), 0, 1)[:, None, None]     # weather darkens the top
    rgb *= 1 - 0.18 * top
    trim = plan['trim']
    alpha = np.ones((H, W), np.float32)
    timber = S.get('timber')
    if timber:                                                            # oak framing; the roof is a layer of its own
        _timbers(rgb, plan)
        _shade_rect(rgb, (0, H - 7, W, H), np.array((0.42, 0.4, 0.37), np.float32))     # a stone plinth
    else:
        if S.get('courses'):
            for st in range(1, plan['storeys']):
                y = H - st * PX
                _shade_rect(rgb, (0, y - 3, W, y), trim * 0.9)
        _shade_rect(rgb, (0, H - 7, W, H), trim * 0.62)                      # plinth
        _shade_rect(rgb, (0, 0, W, 9), trim, bevel=2)                         # cornice
        rgb[9:12] *= 0.45                                                     # the shadow under it
        for x in range(3, W - 3, 7):
            _shade_rect(rgb, (x, 9, min(x + 3, W), 12), trim * 0.85)           # dentils
    em = np.zeros((H, W), np.float32)
    for wnd in plan['windows']:
        x0, y0, x1, y1 = wnd['box']
        if timber and not wnd.get('shop'):                              # the rails are its sill and head
            alpha[y0:y1, x0:x1] = 0
            continue
        if wnd.get('shop') and wnd.get('neon') is not None:            # a neon sign over the shop
            _neon_sign(rgb, em, (x0 - 4, y0 - 13, x1 + 4, y0 - 2), wnd['neon'],
                       np.random.default_rng(plan['seed'] + x0), vertical=False)
        elif wnd.get('shop'):
            _shade_rect(rgb, (x0 - 4, y0 - 12, x1 + 4, y0 - 2), trim * 0.5, bevel=1)   # a sign board
            _shade_rect(rgb, (x0 - 4, y1, x1 + 4, H - 7), trim * 0.7)                   # stall riser
        else:
            _shade_rect(rgb, (x0 - 2, y1, x1 + 2, min(H, y1 + 3)), trim)                 # sill
            _shade_rect(rgb, (x0 - 1, max(0, y0 - 4), x1 + 1, y0), trim * 0.92)          # lintel
            streak = slice(y1 + 3, min(H, y1 + 3 + int(PX * 0.5)))
            rgb[streak, x0:x1] *= np.linspace(0.8, 1.0, streak.stop - streak.start)[:, None, None]
        alpha[y0:y1, x0:x1] = 0
    if plan['door']:
        x0, y0, x1, y1 = plan['door']
        if not timber:
            _shade_rect(rgb, (x0 - 4, y0 - 5, x1 + 4, y1), trim * 0.85, bevel=1)          # surround
        alpha[y0:y1, x0:x1] = 0
    for x0, y0, x1, y1 in plan.get('acs', []):                         # air conditioners
        _shade_rect(rgb, (x0, y0, x1, min(H, y1)), plan['trim'] * 0.75, bevel=1)
        rgb[y0 + 2:min(H, y1) - 2:2, x0 + 2:x1 - 2] *= 0.6
    for sg in plan.get('signs', []):
        _neon_sign(rgb, em, sg['box'], sg['color'], np.random.default_rng(plan['seed'] + sg['box'][0]), vertical=True)
    return np.concatenate([np.clip(rgb, 0, 1), alpha[..., None]], -1).astype(np.float32), em


def _frame(plan):
    """Window frames and glazing bars in the building's paint, and its door."""
    W, H = plan['W'], plan['H']
    rgba = np.zeros((H, W, 4), np.float32)
    f = plan['frame']

    def bar(x0, y0, x1, y1, color):
        x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
        rgba[y0:y1, x0:x1, :3] = color
        rgba[y0:y1, x0:x1, 3] = 1.0
    timber = plan['style'].get('timber')
    for wnd in plan['windows']:
        x0, y0, x1, y1 = wnd['box']
        if timber:
            _casement(rgba, wnd, f)
            continue
        for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
            bar(a, b, c, d, f)
        if wnd.get('shop') and wnd.get('shutter'):                     # a roller shutter part way down
            down = y0 + int((y1 - y0) * wnd['shutter'])
            metal = np.array((0.42, 0.44, 0.47), np.float32)
            bar(x0 - 2, y0 - 3, x1 + 2, y0 + 1, metal * 0.7)                 # its housing
            for yy in range(y0 + 1, down):
                bar(x0, yy, x1, yy + 1, metal * (1.08 if yy % 3 == 0 else 0.86))
            bar(x0, down - 2, x1, down, metal * 0.55)
        if wnd.get('shop'):
            for x in np.arange(x0, x1, PX * 0.55)[1:]:
                bar(x - 1, y0, x + 1, y1, f * 0.8)
            bar(x0, y0 + (y1 - y0) * 0.22, x1, y0 + (y1 - y0) * 0.22 + 2, f)          # transom
        else:
            mid = (y0 + y1) / 2
            bar(x0, mid - 1, x1, mid + 1, f)                                           # meeting rail
            bar((x0 + x1) / 2 - 0.5, y0, (x0 + x1) / 2 + 0.5, y1, f * 0.85)            # glazing bar
        rgba[y0:y0 + 1, x0:x1, :3] *= 1.15
        rgba[y1 - 1:y1, x0:x1, :3] *= 0.6
    if plan['door'] and timber:
        _plank_door(rgba, plan['door'], plan['door_col'])
    elif plan['door']:
        x0, y0, x1, y1 = plan['door']
        dc = plan['door_col']
        bar(x0, y0, x1, y1, dc)
        light = y0 + int((y1 - y0) * 0.3)
        rgba[y0 + 3:light - 1, x0 + 3:x1 - 3, 3] = 0                  # a glazed light at the top
        for py0, py1 in ((light + 2, light + int((y1 - light) * 0.45)), (light + int((y1 - light) * 0.52), y1 - 4)):
            for px0, px1 in ((x0 + 3, (x0 + x1) // 2 - 1), ((x0 + x1) // 2 + 1, x1 - 3)):
                rgba[py0:py1, px0:px1, :3] = dc * 1.25                # raised panels
                rgba[py0:py0 + 1, px0:px1, :3] = np.clip(dc * 1.7, 0, 1)
                rgba[py1 - 1:py1, px0:px1, :3] = dc * 0.6
        rgba[(y0 + y1) // 2 + 4:(y0 + y1) // 2 + 6, x1 - 6:x1 - 4, :3] = (0.8, 0.66, 0.3)   # the knob
        rgba[y0:y1, x0:x0 + 1, :3] = np.clip(dc * 1.6, 0, 1)
    return rgba, np.zeros((H, W), np.float32)


def _glass(plan):
    """The panes: every window, the shopfront and the light over the door, for the glass pass."""
    from biomes import glass_image
    W, H = plan['W'], plan['H']
    rgba = np.zeros((H, W, 4), np.float32)
    rng = np.random.default_rng(plan['seed'] + 11)
    boxes = [w['box'] for w in plan['windows']]
    if plan['door'] and not plan['style'].get('timber'):         # a plank door has no light in it
        x0, y0, x1, y1 = plan['door']
        boxes.append((x0 + 3, y0 + 3, x1 - 3, y0 + int((y1 - y0) * 0.3) - 1))
    for x0, y0, x1, y1 in boxes:
        if x1 > x0 and y1 > y0:
            rgba[y0:y1, x0:x1] = glass_image(x1 - x0, y1 - y0, rng)
    return rgba, np.zeros((H, W), np.float32)


def _drape(plan):
    """Behind the glass, a different choice in every window: drawn curtains, a roller blind
    half down, closed shutters, a net curtain, or nothing at all."""
    W, H = plan['W'], plan['H']
    rgba = np.zeros((H, W, 4), np.float32)
    for wnd in plan['windows']:
        x0, y0, x1, y1 = wnd['box']
        kind, c = wnd['drape'], wnd['drape_color']
        w, h = x1 - x0, y1 - y0
        if kind == 'curtains':
            for side in (0, 1):
                cw = max(3, int(w * wnd['split']))
                xs = np.arange(cw)
                fold = 0.82 + 0.3 * (np.sin(xs * 1.9 + side) > 0)          # vertical folds
                ys = np.arange(h)
                # tied back: narrower at the waist
                waist = 1 - 0.35 * np.exp(-((ys - h * 0.62) / (h * 0.12)) ** 2)
                for yy in range(h):
                    n = max(1, int(cw * waist[yy]))
                    cols = np.arange(n) if side == 0 else np.arange(w - n, w)
                    rgba[y0 + yy, x0 + cols, :3] = c * fold[:n, None] if side == 0 else c * fold[:n][::-1, None]
                    rgba[y0 + yy, x0 + cols, 3] = 1.0
            rgba[y0:y0 + 2, x0:x1, :3] = c * 0.6                             # the pelmet
            rgba[y0:y0 + 2, x0:x1, 3] = 1.0
        elif kind == 'blind':
            down = int(h * (0.3 + 0.45 * ((wnd['split'] - 0.18) / 0.2)))
            rgba[y0:y0 + down, x0:x1, :3] = c * 0.9 + 0.1
            rgba[y0:y0 + down, x0:x1, 3] = 1.0
            rgba[y0 + down - 2:y0 + down, x0:x1, :3] = c * 0.55
            cx = (x0 + x1) // 2
            rgba[y0 + down:y0 + down + 3, cx:cx + 1, :3] = 0.85                # the pull cord
            rgba[y0 + down:y0 + down + 3, cx:cx + 1, 3] = 1.0
        elif kind == 'shutters':
            sh = c * 0.6 + np.array([0.05, 0.12, 0.08], np.float32)
            for yy in range(h):
                rgba[y0 + yy, x0:x1, :3] = sh * (1.15 if yy % 3 == 0 else 0.9)  # slats
            rgba[y0:y1, x0:x1, 3] = 1.0
            cx = (x0 + x1) // 2
            rgba[y0:y1, cx:cx + 1, :3] = sh * 0.5
        elif kind == 'net':
            yy, xx = np.mgrid[y0:y1, x0:x1]
            sheer = ((yy + xx) % 2 == 0) & (yy < y0 + h * 0.85)
            rgba[yy[sheer], xx[sheer], :3] = 0.86
            rgba[yy[sheer], xx[sheer], 3] = 1.0
    return rgba, np.zeros((H, W), np.float32)


def _room(plan):
    """The rooms behind the windows: dark inside, and in a lit one a warm (or screen-blue) glow
    with a lamp, a picture, a shelf, a plant or a figure against the back wall."""
    W, H = plan['W'], plan['H']
    rng = np.random.default_rng(plan['seed'] + 23)
    rgb = np.empty((H, W, 3), np.float32)
    rgb[:] = (0.035, 0.032, 0.04)
    em = np.zeros((H, W), np.float32)
    for wnd in plan['windows']:
        x0, y0, x1, y1 = wnd['box']
        mx, my = max(6, (x1 - x0) // 2), max(6, (y1 - y0) // 2)        # rooms spill past the opening
        X0, Y0, X1, Y1 = max(0, x0 - mx), max(0, y0 - my), min(W, x1 + mx), min(H, y1 + my)
        h, w = Y1 - Y0, X1 - X0
        yy, xx = np.mgrid[0:h, 0:w]
        if wnd['lit']:
            warm = np.array([1.0, 0.72, 0.38], np.float32) if wnd['warm'] else np.array([0.45, 0.62, 0.9], np.float32)
            if wnd.get('tint') is not None:
                warm = np.array(wnd['tint'], np.float32)
            glow = np.clip(1.15 - np.hypot((xx - w * 0.5) / (w * 0.55), (yy - h * 0.25) / (h * 0.8)), 0.15, 1)
            rgb[Y0:Y1, X0:X1] = warm * (0.3 + 0.75 * glow[..., None])
            em[Y0:Y1, X0:X1] = 0.5 + 0.5 * glow
        else:
            rgb[Y0:Y1, X0:X1] = (0.05, 0.055, 0.075)
        ink = np.array([0.08, 0.05, 0.04], np.float32) if wnd['lit'] else np.array([0.025, 0.025, 0.035], np.float32)
        motif = wnd['motif']
        cx = X0 + w // 2 + int(rng.integers(-w // 6, w // 6 + 1))
        if motif == 'lamp':
            rgb[Y0 + h // 4:Y0 + h // 4 + 5, cx - 4:cx + 4] = ink * 3 if wnd['lit'] else ink
            rgb[Y0 + h // 4 + 5:Y0 + h * 3 // 4, cx:cx + 1] = ink
        elif motif == 'picture':
            rgb[Y0 + h // 3:Y0 + h // 3 + 7, cx - 5:cx + 5] = ink * 2
            rgb[Y0 + h // 3 + 1:Y0 + h // 3 + 6, cx - 4:cx + 4] = (0.3, 0.25, 0.2) if wnd['lit'] else ink * 1.5
        elif motif == 'shelf':
            for k in range(3):
                y = Y0 + h // 3 + k * 6
                rgb[y:y + 1, X0 + 3:X1 - 3] = ink
                for b in range(X0 + 4, X1 - 4, 3):
                    if rng.random() < 0.7:
                        rgb[y - 4:y, b:b + 2] = ink * (1 + rng.random())
        elif motif == 'plant':
            for k in range(7):
                a = np.radians(-150 + k * 20)
                for t in range(8):
                    px_, py_ = int(cx + np.cos(a) * t), int(Y0 + h * 0.62 + np.sin(a) * t)
                    if X0 <= px_ < X1 and Y0 <= py_ < Y1:
                        rgb[py_, px_] = ink
        elif motif == 'figure':
            fy = Y0 + h // 3
            rgb[fy:fy + 5, cx - 2:cx + 3] = ink                      # a head
            rgb[fy + 5:Y1, cx - 4:cx + 5] = ink                      # shoulders down
            em[fy:Y1, cx - 4:cx + 5] *= 0.3
        elif motif == 'shop':
            for k in range(3):                                       # shelves of goods
                y = Y0 + h // 4 + k * (h // 4)
                rgb[y:y + 1, X0 + 2:X1 - 2] = ink
                for b in range(X0 + 4, X1 - 4, 4):
                    if rng.random() < 0.8:
                        rgb[y - 3:y, b:b + 2] = (np.array([0.6, 0.3, 0.2]) + rng.random(3) * 0.4) * (1 if wnd['lit'] else 0.2)
    return np.concatenate([rgb, np.ones((H, W, 1), np.float32)], -1), em


def _timbers(rgb, plan):
    """Oak framing over the plaster of a timber-framed house: corner posts, a wall plate under the
    eaves and a sole plate on the plinth, a heavy rail at every floor, rails at the windows' sills
    and heads, posts at every bay and either side of every window and the door, and in each
    storey either braces at the ends or close studding all along. Every timber has a lit top-left
    edge and a dark one, and throws a hairline shadow on the plaster below and right of it."""
    W, H, S = plan['W'], plan['H'], plan['style']
    trng = np.random.default_rng([plan['look'] % (2 ** 31), 41])        # the building's own framing
    oak = _rgb(S['timber_colors'][int(trng.integers(len(S['timber_colors'])))])
    studs = trng.random() < 0.35
    tim = np.zeros((H, W), bool)

    def beam(x0, y0, x1, y1):
        tim[max(0, int(y0)):max(0, int(y1)), max(0, int(x0)):max(0, int(x1))] = True

    def brace(x0, y0, x1, y1, w=3):
        for k in range(w):
            _stroke_mask(tim, x0 + k, y0, x1 + k, y1)

    sole = H - 7                                                       # the top of the plinth
    beam(0, 0, 5, H)
    beam(W - 5, 0, W, H)                                               # corner posts
    beam(0, 0, W, 6)                                                   # the wall plate
    beam(0, sole - 5, W, sole)                                         # the sole plate
    for st in range(plan['storeys']):
        floor_y = sole - 5 if st == 0 else H - st * PX - 3            # the bottom of the storey's panels
        top_y = H - (st + 1) * PX + (6 if st == plan['storeys'] - 1 else 3)
        if st:
            beam(0, H - st * PX - 3, W, H - st * PX + 3)                # the floor rail
        mine = [w_['box'] for w_ in plan['windows'] if w_['storey'] == st and not w_.get('shop')]
        y1 = mine[0][3] if mine else floor_y - int(PX * 0.28)
        y0 = mine[0][1] if mine else y1 - int(PX * 0.5)
        beam(0, y1, W, y1 + 3)                                         # the sill rail
        beam(0, y0 - 3, W, y0)                                         # the head rail
        for b in range(1, plan['bays']):
            x = int(b * plan['bay_w'])
            beam(x - 2, top_y, x + 2, floor_y)
        for x0, _, x1, _ in mine:
            beam(x0 - 4, top_y, x0, floor_y)
            beam(x1, top_y, x1 + 4, floor_y)
        if studs:
            for x in range(10, W - 8, 11):
                beam(x, top_y, x + 3, floor_y)
        else:                                                          # braces up from the ends of the storey
            reach = min(plan['bay_w'] * 0.32, 22)
            brace(5, floor_y - 1, 5 + reach, y1 + 3)
            brace(W - 8, floor_y - 1, W - 8 - reach, y1 + 3)
            if mine:                                                   # and a pair under each window
                for x0, _, x1, _ in mine:
                    mid = (x0 + x1) // 2
                    brace(x0, floor_y - 1, mid - 1, y1 + 3, 2)
                    brace(x1 - 2, floor_y - 1, mid - 1, y1 + 3, 2)
    if plan['door']:                                                   # door posts and a lintel
        x0, y0, x1, y1 = plan['door']
        beam(x0 - 5, y0 - 7, x0, y1)
        beam(x1, y0 - 7, x1 + 5, y1)
        beam(x0 - 5, y0 - 7, x1 + 5, y0)
    srng = np.random.default_rng(plan['seed'] + 41)
    grain = smooth_noise(W, H, max(2, W // 5), srng, wrap=False, cells_y=max(2, H // 24))
    col = oak[None, None, :] * (0.8 + 0.4 * grain[..., None])
    up = np.zeros_like(tim)
    up[1:] = tim[:-1]                                                  # the pixel above is timber
    left = np.zeros_like(tim)
    left[:, 1:] = tim[:, :-1]
    down = np.zeros_like(tim)
    down[:-1] = tim[1:]
    right = np.zeros_like(tim)
    right[:, :-1] = tim[:, 1:]
    shadow = ~tim & (up | left)
    rgb[shadow] *= 0.72                                                # on the plaster, under and right of a timber
    rgb[tim] = col[tim]
    rgb[tim & (~up | ~left)] *= 1.35
    rgb[tim & (~down | ~right)] *= 0.62
    rgb[6:13] *= np.linspace(0.45, 0.92, 7)[:, None, None]            # the eaves' shadow on the wall


def _casement(rgba, wnd, f):
    """A leaded casement in an oak frame: a mullion down the middle (and a transom in a tall
    one), each light glazed in small diamond panes set in lead. A shop gets a bow of small square
    panes instead."""
    x0, y0, x1, y1 = wnd['box']
    lead = np.array((0.16, 0.16, 0.18), np.float32)

    def bar(a, b, c, d, color):
        rgba[int(b):int(d), int(a):int(c), :3] = color
        rgba[int(b):int(d), int(a):int(c), 3] = 1.0
    if wnd.get('shop'):
        for x in range(x0 + 7, x1 - 3, 7):
            bar(x, y0, x + 1, y1, f * 1.1)
        for y in range(y0 + 7, y1 - 3, 7):
            bar(x0, y, x1, y + 1, f * 1.1)
    else:
        yy, xx = np.mgrid[y0:y1, x0:x1]
        diamond = ((xx + yy) % 6 == 0) | ((xx - yy) % 6 == 0)
        rgba[y0:y1, x0:x1, :3] = np.where(diamond[..., None], lead, rgba[y0:y1, x0:x1, :3])
        rgba[y0:y1, x0:x1, 3] = np.where(diamond, 1.0, rgba[y0:y1, x0:x1, 3])
        mid = (x0 + x1) // 2
        bar(mid - 1, y0, mid + 2, y1, f)                               # the mullion
        if y1 - y0 > 34:
            bar(x0, y0 + (y1 - y0) // 3, x1, y0 + (y1 - y0) // 3 + 2, f)   # the transom
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        bar(a, b, c, d, f)
    rgba[y0:y0 + 1, x0:x1, :3] *= 1.2
    rgba[y1 - 1:y1, x0:x1, :3] *= 0.6


def _plank_door(rgba, box, dc):
    """A door of oak planks: the joints between them, two iron strap hinges across, a ring."""
    x0, y0, x1, y1 = box
    rgba[y0:y1, x0:x1, :3] = dc
    rgba[y0:y1, x0:x1, 3] = 1.0
    for x in range(x0 + 4, x1 - 1, 5):
        rgba[y0:y1, x:x + 1, :3] = dc * 0.5                          # the joints
    rgba[y0:y1, x0:x0 + 1, :3] = np.clip(dc * 1.5, 0, 1)
    iron = np.array((0.13, 0.13, 0.14), np.float32)
    for hy in (y0 + 8, y1 - 11):
        rgba[hy:hy + 2, x0 + 1:x1 - 4, :3] = iron                    # strap hinges
        rgba[hy - 1:hy + 3, x0 + 1:x0 + 4, :3] = iron
    cy = (y0 + y1) // 2
    rgba[cy:cy + 4, x1 - 7:x1 - 4, :3] = iron                        # the ring
    rgba[cy + 1:cy + 3, x1 - 6:x1 - 5, :3] = dc * 0.8


def roof_of(style, look, w):
    """The roof over a building of a village style, chosen by its look: (kind, cover, height in
    units, chimney) - a gable end facing the street on a narrow house, or the slope of a roof
    running along it, of thatch or tiles - or None for a style without roofs."""
    S = FACADE_STYLES[pick_style(style, look)]
    if not S.get('roofs'):
        return None
    r = np.random.default_rng([int(look) % (2 ** 31), 43])
    kind = 'gable' if r.random() < S.get('gables', 0.5) and w <= 3.4 else 'eaves'
    cover = str(S['roofs'][int(r.integers(len(S['roofs'])))])
    chimney = bool(kind == 'eaves' and r.random() < 0.6)
    if kind == 'gable':
        h = min(0.5 * w, 1.6)
    else:
        h = float(r.uniform(0.62, 0.78) if cover == 'thatch' else r.uniform(0.52, 0.66))
    return kind, cover, round(h + (CHIMNEY / PX if chimney else 0.0), 3), chimney


CHIMNEY = 26        # pixels a chimney stands above a ridge


def _thatch(W, H, rng):
    """Thatch seen from the street: reed ends in streaks of gold and weathered brown, a thick
    rounded eave at the foot, and a ridge along the top cut in points."""
    base = _rgb(['#a88a52', '#9a7e4c', '#8a7454'][int(rng.integers(3))])
    yy = np.arange(H)[:, None]
    streak = smooth_noise(W, H, max(2, W // 4), rng, wrap=False, cells_y=3)
    fine = rng.random((H, W)) * 0.14
    tone = 0.72 + 0.34 * streak + fine - 0.12 * (yy < H * 0.5)
    rgb = base[None, None, :] * tone[..., None]
    lip = np.clip((yy - (H - 11)) / 11.0, 0, 1)                      # the eave: lit above, dark below
    rgb *= (1 + 0.25 * np.sin(lip * np.pi) - 0.5 * (lip > 0.75))[..., None]
    alpha = np.ones((H, W), np.float32)
    ridge = 12
    xs = np.arange(W)
    points = ridge + 3 * np.abs(np.sin(np.pi * xs / 10.0))            # the ridge's cut edge
    band = yy < points[None, :]
    rgb[band] = (base * 1.12)[None, :] * (0.85 + 0.2 * rng.random((int(band.sum()), 1)))
    edge = (yy >= points[None, :]) & (yy < points[None, :] + 2)
    rgb[edge] *= 0.55
    top = 2 + 1.5 * np.sin(np.pi * xs / W)                             # a soft curve along the top
    alpha[yy < (2 - top)[None, :] + 2] = 0
    return rgb, alpha


def _tiles(W, H, rng):
    """A tiled roof seen from the street: courses of clay tiles, each its own shade of red-brown,
    a dark line under every course, patches of moss, ridge tiles along the top."""
    base = _rgb(['#8a4a32', '#7a4434', '#94583a'][int(rng.integers(3))])
    rgb = np.zeros((H, W, 3), np.float32)
    for row in range(0, H, 6):
        off = 4 if (row // 6) % 2 else 0
        for x in range(-8 + off, W, 8):
            c = base * float(rng.uniform(0.78, 1.15))
            a, b = max(0, x), min(W, x + 7)
            if b > a:
                rgb[row:row + 6, a:b] = c
                rgb[row:row + 1, a:b] = c * 1.2
                rgb[row + 4:row + 6, a:b] = c * 0.62
            if 0 <= x + 7 < W:
                rgb[row:row + 6, x + 7] = base * 0.45
    moss = smooth_noise(W, H, max(2, W // 12), rng, wrap=False) > 0.72
    rgb[moss & (rng.random((H, W)) < 0.6)] = (0.4, 0.44, 0.26)
    for x in range(0, W, 12):                                          # ridge tiles
        rgb[0:5, x:x + 11] = base * 0.7
        rgb[0:1, x:x + 11] = base * 0.95
    rgb[5:6] *= 0.5
    return rgb, np.ones((H, W), np.float32)


def _chimney(rgb, alpha, x0, rng):
    """A brick stack rising through the ridge, a cap course and a pot or two."""
    H = rgb.shape[0]
    brick = _rgb('#7a4a3a')
    for y in range(4, CHIMNEY + 10):
        for x in range(x0, x0 + 16):
            if (y // 4 + (x - x0) // 6) % 2 == 0 or y % 4 == 0:
                rgb[y, x] = brick * (0.65 if y % 4 == 0 else 1.0)
            else:
                rgb[y, x] = brick * 0.9
            alpha[y, x] = 1
    rgb[4:7, x0 - 1:x0 + 17] = brick * 1.15                            # the cap
    alpha[4:7, x0 - 1:x0 + 17] = 1
    for px in (x0 + 2, x0 + 9)[:1 + int(rng.random() < 0.5)]:         # pots
        rgb[0:4, px:px + 5] = _rgb('#9a5a3a')
        alpha[0:4, px:px + 5] = 1
    rgb[4:CHIMNEY + 10, x0 + 12:x0 + 16] *= 0.7                        # its shaded side


def _roof(p):
    """The roof over a village house, as a card standing on top of its wall: the slope of thatch or
    tiles (with a chimney now and then), or a gable end - a triangle of the house's own plaster and
    timbers under bargeboards, with a small leaded window."""
    S = FACADE_STYLES[pick_style(p.get('style', 'timber'), p.get('look', 0))]
    W, H = max(8, int(round(float(p['w']) * PX))), max(8, int(round(float(p['h']) * PX)))
    rng = np.random.default_rng([int(p.get('look', 0)) % (2 ** 31), 44])
    kind, cover, chimney = p['kind'], p['cover'], p.get('chimney')
    rgb = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    if kind == 'eaves':
        top = CHIMNEY if chimney else 0
        part, a = (_thatch if cover == 'thatch' else _tiles)(W, H - top, rng)
        rgb[top:], alpha[top:] = part, a
        if chimney:
            _chimney(rgb, alpha, int(W * rng.uniform(0.15, 0.7)), rng)
    else:
        look = np.random.default_rng(int(p.get('look', 0)) % (2 ** 32))           # the house's own colour
        color = _rgb(S['colors'][look.integers(len(S['colors']))]) * float(look.uniform(0.88, 1.12))
        lum, _ = _brick_tile('plaster')
        L = lum[np.ix_(np.arange(H) % PX, np.arange(W) % PX)]
        rgb[:] = color[None, None, :] * (0.45 + 0.95 * L[..., None])
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        half = (yy + 1) / H * (W / 2)
        off = np.abs(xx + 0.5 - W / 2)
        alpha[off <= half] = 1
        oak = _rgb(S['timber_colors'][int(np.random.default_rng([int(p.get('look', 0)) % (2 ** 31), 41])
                                              .integers(len(S['timber_colors'])))])
        tim = np.zeros((H, W), bool)
        cx = W // 2
        tim[H - 5:H] = True                                            # the tie beam
        tim[int(H * 0.2):H, cx - 2:cx + 2] = True                       # the king post
        cy = int(H * 0.55)
        tim[cy:cy + 3] = (off <= half)[cy:cy + 3]                       # the collar
        for k in range(3):                                             # struts
            _stroke_mask(tim, cx - 2 + k, H - 5, cx - W * 0.22 + k, cy + 3)
            _stroke_mask(tim, cx + 1 + k, H - 5, cx + W * 0.22 + k, cy + 3)
        tim &= off <= half
        rgb[tim] = oak * 0.95
        rgb[tim & (np.roll(tim, 1, 0) == 0)] = oak * 1.3
        ww, wh = max(8, int(W * 0.16)), max(8, int(H * 0.2))          # a small leaded window under the apex
        wx0, wy0 = cx - ww // 2, int(H * 0.3)
        if wy0 + wh < cy - 2:
            sub = np.mgrid[wy0:wy0 + wh, wx0:wx0 + ww]
            dia = ((sub[0] + sub[1]) % 5 == 0) | ((sub[0] - sub[1]) % 5 == 0)
            rgb[wy0:wy0 + wh, wx0:wx0 + ww] = np.where(dia[..., None], (0.16, 0.16, 0.18), (0.1, 0.12, 0.16))
            rgb[wy0:wy0 + wh, cx - 1:cx + 1] = oak
            rgb[wy0 - 2:wy0, wx0 - 2:wx0 + ww + 2] = oak
            rgb[wy0 + wh:wy0 + wh + 2, wx0 - 2:wx0 + ww + 2] = oak
        edge = (off <= half) & (off > half - 6)                       # the bargeboards
        rgb[edge] = oak * 0.85
        rgb[(off <= half) & (off > half - 1.5)] = oak * 1.3
        cover_c = _rgb('#a88a52') if cover == 'thatch' else _rgb('#8a4a32')
        lip = (off > half) & (off <= half + (7 if cover == 'thatch' else 3))   # the covering showing over them
        rgb[lip] = cover_c * (0.8 + 0.3 * rng.random((int(lip.sum()), 1)))
        alpha[lip] = 1
    return np.concatenate([np.clip(rgb, 0, 1), alpha[..., None]], -1).astype(np.float32), np.zeros((H, W), np.float32)


def _side(p):
    """The side wall a taller building shows above its lower neighbour: plain brick, cornice
    at the top, no windows (a party wall)."""
    S = FACADE_STYLES[pick_style(p.get('style', 'brick'), p.get('look', 0))]
    look = np.random.default_rng(int(p.get('look', 0)) % (2 ** 32))
    color = _rgb(S['colors'][look.integers(len(S['colors']))]) * float(look.uniform(0.88, 1.12))
    W, H = max(4, int(round(float(p['w']) * PX))), max(4, int(round(float(p['h']) * PX)))
    lum, mortar = _brick_tile(_surface(S))
    L = lum[np.ix_(np.arange(H) % PX, np.arange(W) % PX)]
    m = mortar[np.ix_(np.arange(H) % PX, np.arange(W) % PX)]
    rgb = np.where(m[..., None], _rgb(S['mortar'])[None, None, :] * (0.5 + 0.6 * L[..., None]),
                   color[None, None, :] * (0.4 + 0.85 * L[..., None]))
    _shade_rect(rgb, (0, 0, W, min(H, 9)), _rgb(S['trim']) * 0.9, bevel=2)
    return np.concatenate([np.clip(rgb, 0, 1), np.ones((H, W, 1), np.float32)], -1), np.zeros((H, W), np.float32)


def _stroke_mask(mask, x0, y0, x1, y1):
    """Set the pixels along a line in a boolean mask (one pixel wide)."""
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    xs = np.clip(np.round(np.linspace(x0, x1, n)).astype(int), 0, mask.shape[1] - 1)
    ys = np.clip(np.round(np.linspace(y0, y1, n)).astype(int), 0, mask.shape[0] - 1)
    mask[ys, xs] = True


def _glyph_mask(h, w, rng, vertical):
    """Pseudo-letters in neon tube: in each cell along the sign two to four strokes - bars, uprights,
    slants, a box or a hook - so a sign reads as writing without being in any real script."""
    mask = np.zeros((h, w), bool)
    cell = (w - 2) if vertical else max(6, h - 4)
    n = max(1, (h - 2) // (cell + 2) if vertical else (w - 2) // (cell + 2))
    for k in range(n):
        if vertical:
            cx0, cy0 = 1, 1 + k * (cell + 2)
        else:
            cx0, cy0 = 1 + k * (cell + 2), 2
        c = cell - 1
        for _ in range(int(rng.integers(2, 5))):
            kind = int(rng.integers(5))
            a, b = rng.uniform(0, c, 2)
            if kind == 0:
                _stroke_mask(mask, cx0, cy0 + a, cx0 + c, cy0 + a)
            elif kind == 1:
                _stroke_mask(mask, cx0 + a, cy0, cx0 + a, cy0 + c)
            elif kind == 2:
                _stroke_mask(mask, cx0, cy0 + a, cx0 + c, cy0 + b)
            elif kind == 3:
                for p0, p1 in (((0, 0), (c, 0)), ((c, 0), (c, c)), ((c, c), (0, c)), ((0, c), (0, 0))):
                    _stroke_mask(mask, cx0 + p0[0] * 0.8, cy0 + p0[1] * 0.8, cx0 + p1[0] * 0.8, cy0 + p1[1] * 0.8)
            else:
                _stroke_mask(mask, cx0 + a, cy0, cx0 + a, cy0 + c * 0.7)
                _stroke_mask(mask, cx0 + a, cy0 + c * 0.7, cx0 + c, cy0 + c * 0.7)
    return mask


def _neon_sign(rgb, em, box, color, rng, vertical):
    """A sign on a wall: a dark board edged in one neon tube, with glowing pseudo-letters on it and
    a soft spill of its colour round the letters."""
    x0, y0, x1, y1 = (int(v) for v in box)
    H, W = rgb.shape[:2]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < 6 or y1 - y0 < 6:
        return
    c = np.array(color, np.float32)
    rgb[y0:y1, x0:x1] = np.array((0.06, 0.06, 0.08), np.float32) + c * 0.06
    edge = np.zeros((y1 - y0, x1 - x0), bool)
    edge[[0, -1], :] = True
    edge[:, [0, -1]] = True
    letters = _glyph_mask(y1 - y0 - 4, x1 - x0 - 4, rng, vertical)
    tube = edge.copy()
    tube[2:-2, 2:-2] |= letters
    halo = tube.copy()
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        halo |= np.roll(tube, (dy, dx), (0, 1))
    sub = rgb[y0:y1, x0:x1]
    sub[halo & ~tube] = sub[halo & ~tube] * 0.5 + c * 0.35
    sub[tube] = np.clip(c * 0.85 + 0.25, 0, 1)
    em[y0:y1, x0:x1] = np.maximum(em[y0:y1, x0:x1], tube * 1.0 + (halo & ~tube) * 0.5)


def _blade(p):
    """A blade sign standing out from a wall over the street: a tall dark panel in a steel frame,
    edged in neon, glowing pseudo-letters stacked down it, two brackets at the wall end."""
    S = FACADE_STYLES[pick_style(p.get('style', 'neon'), p.get('look', 0))]
    W, H = max(12, int(round(float(p['w']) * PX))), max(24, int(round(float(p['h']) * PX)))
    rng = np.random.default_rng((int(p.get('look', 0)) * 31 + int(p.get('seed', 0))) % (2 ** 32))
    color = NEON[int(rng.integers(len(NEON)))]
    rgb = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    em = np.zeros((H, W), np.float32)
    x0 = 6                                                   # the brackets take the wall end
    frame = _rgb(S['trim']) * 0.6
    for y in (int(H * 0.15), int(H * 0.8)):
        rgb[y:y + 3, 0:x0] = frame
        alpha[y:y + 3, 0:x0] = 1
    _shade_rect(rgb, (x0, 0, W, H), frame, bevel=1)
    alpha[:, x0:W] = 1
    _neon_sign(rgb, em, (x0 + 2, 2, W - 2, H - 2), color, rng, vertical=True)
    return np.concatenate([np.clip(rgb, 0, 1), alpha[..., None]], -1).astype(np.float32), em

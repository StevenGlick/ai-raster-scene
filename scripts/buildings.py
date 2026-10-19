"""Building facades in layers, for wall cells with a `facade`.

A street drawn the raycaster's usual way is a flat textured wall: the windows are painted on.
A facade is drawn instead as layers of planes standing one behind another in the cell in front
of a building's walls, each building on the street with its own images:

    wall    brick (or plaster) with openings for windows and door, sills, lintels, a cornice
    frame   window frames and glazing bars, and the door
    glass   the panes, drawn last by the glass pass: what is behind them, tinted and blurred
    drape   curtains, blinds, shutters or net curtains, a different choice in every window
    room    the rooms behind: lit or dark, a lamp, a picture, a shelf, now and then a figure

so a window has a reveal, the glass sits in it, the curtains hang behind the glass and the room
is further back still, and as the camera moves the layers slide against each other.

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
}

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
    plan = _plan(json.dumps(p, sort_keys=True))
    return {'wall': _wall, 'frame': _frame, 'glass': _glass, 'drape': _drape, 'room': _room}[layer](plan)


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
    return {'W': W, 'H': H, 'storeys': storeys, 'color': color, 'frame': frame, 'door_col': door_col,
            'mortar': _rgb(S['mortar']), 'trim': _rgb(S['trim']), 'windows': windows, 'door': door,
            'style': S, 'seed': int(p.get('seed', 0)), 'look': int(p.get('look', 0))}


# ------------------------------------------------------------------ the layers

@lru_cache(maxsize=8)
def _brick_tile(plaster=False):
    """A seamless 64x64 tile of neutral brick (or plaster), lit from the upper left: a building's
    colour is multiplied in, so every building shades the same way whatever its colour."""
    rng = np.random.default_rng(17 if not plaster else 18)
    cv = Canvas(PX, ground=-0.6, mat=1)
    if plaster:
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
    lum, mortar = _brick_tile(S.get('plaster', False))
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
    if S.get('courses'):
        for st in range(1, plan['storeys']):
            y = H - st * PX
            _shade_rect(rgb, (0, y - 3, W, y), trim * 0.9)
    _shade_rect(rgb, (0, H - 7, W, H), trim * 0.62)                      # plinth
    _shade_rect(rgb, (0, 0, W, 9), trim, bevel=2)                         # cornice
    rgb[9:12] *= 0.45                                                     # the shadow under it
    for x in range(3, W - 3, 7):
        _shade_rect(rgb, (x, 9, min(x + 3, W), 12), trim * 0.85)           # dentils
    for wnd in plan['windows']:
        x0, y0, x1, y1 = wnd['box']
        if wnd.get('shop'):
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
        _shade_rect(rgb, (x0 - 4, y0 - 5, x1 + 4, y1), trim * 0.85, bevel=1)              # surround
        alpha[y0:y1, x0:x1] = 0
    return np.concatenate([np.clip(rgb, 0, 1), alpha[..., None]], -1).astype(np.float32), np.zeros((H, W), np.float32)


def _frame(plan):
    """Window frames and glazing bars in the building's paint, and its door."""
    W, H = plan['W'], plan['H']
    rgba = np.zeros((H, W, 4), np.float32)
    f = plan['frame']

    def bar(x0, y0, x1, y1, color):
        x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
        rgba[y0:y1, x0:x1, :3] = color
        rgba[y0:y1, x0:x1, 3] = 1.0
    for wnd in plan['windows']:
        x0, y0, x1, y1 = wnd['box']
        for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
            bar(a, b, c, d, f)
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
    if plan['door']:
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
    if plan['door']:
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


def _side(p):
    """The side wall a taller building shows above its lower neighbour: plain brick, cornice
    at the top, no windows (a party wall)."""
    S = FACADE_STYLES[pick_style(p.get('style', 'brick'), p.get('look', 0))]
    look = np.random.default_rng(int(p.get('look', 0)) % (2 ** 32))
    color = _rgb(S['colors'][look.integers(len(S['colors']))]) * float(look.uniform(0.88, 1.12))
    W, H = max(4, int(round(float(p['w']) * PX))), max(4, int(round(float(p['h']) * PX)))
    lum, mortar = _brick_tile(S.get('plaster', False))
    L = lum[np.ix_(np.arange(H) % PX, np.arange(W) % PX)]
    m = mortar[np.ix_(np.arange(H) % PX, np.arange(W) % PX)]
    rgb = np.where(m[..., None], _rgb(S['mortar'])[None, None, :] * (0.5 + 0.6 * L[..., None]),
                   color[None, None, :] * (0.4 + 0.85 * L[..., None]))
    _shade_rect(rgb, (0, 0, W, min(H, 9)), _rgb(S['trim']) * 0.9, bevel=2)
    return np.concatenate([np.clip(rgb, 0, 1), np.ones((H, W, 1), np.float32)], -1), np.zeros((H, W), np.float32)

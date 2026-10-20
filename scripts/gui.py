"""Retro game GUI toolkit, drawn into the frame at native resolution in a hand-drawn pixel font.

Every widget is an entry in a scene's (or shot's) "overlays" list with a "type". Most accept placement:
  "at": top-left | top | top-right | left | center | right | bottom-left | bottom | bottom-right
  "x"/"y": explicit pixels (negative = from the right/bottom edge), "margin": edge gap (default 6)
Styling comes from scene["ui"]: {"theme": "classic" | "parchment" | "terminal" | "blood" | "steel" | "doomed"}
plus any colour override (fill, border, border_dark, text, accent, dim, shadow, select).

Widgets: bubble, dialog, caption, choice, title, panel, toast, prompt, bars, counter, hotbar, inventory,
crosshair, compass, automap, statusbar, message, viewmodel, image.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import assets
import icons
from pixelfont import PixelFont

_PIXEL = PixelFont()  # big titles and counters always use the pixel font; build its glyphs once

THEMES = {
    'classic': {'fill': [14, 12, 20, 228], 'border': [196, 178, 128, 255], 'border_dark': [58, 46, 34, 255],
                'text': [238, 230, 206, 255], 'accent': [226, 176, 80, 255], 'dim': [120, 112, 100, 255],
                'shadow': [0, 0, 0, 200], 'select': [70, 54, 30, 230], 'frame': 'double'},
    'parchment': {'fill': [226, 204, 160, 245], 'border': [96, 62, 30, 255], 'border_dark': [54, 32, 14, 255],
                  'text': [52, 34, 18, 255], 'accent': [150, 32, 20, 255], 'dim': [140, 112, 80, 255],
                  'shadow': [255, 240, 210, 110], 'select': [196, 164, 112, 255], 'frame': 'double'},
    'terminal': {'fill': [3, 12, 6, 232], 'border': [60, 220, 110, 255], 'border_dark': [10, 60, 28, 255],
                 'text': [120, 255, 160, 255], 'accent': [220, 255, 120, 255], 'dim': [40, 120, 70, 255],
                 'shadow': [0, 0, 0, 200], 'select': [20, 80, 40, 240], 'frame': 'single'},
    'blood': {'fill': [14, 4, 6, 232], 'border': [150, 24, 22, 255], 'border_dark': [44, 4, 6, 255],
              'text': [232, 214, 204, 255], 'accent': [255, 80, 56, 255], 'dim': [120, 70, 70, 255],
              'shadow': [0, 0, 0, 220], 'select': [80, 10, 12, 240], 'frame': 'double'},
    'steel': {'fill': [186, 186, 180, 255], 'border': [250, 250, 244, 255], 'border_dark': [64, 64, 64, 255],
              'text': [18, 18, 18, 255], 'accent': [16, 40, 140, 255], 'dim': [110, 110, 110, 255],
              'shadow': [0, 0, 0, 0], 'select': [16, 40, 140, 255], 'select_text': [255, 255, 255, 255], 'frame': 'bevel'},
    'doomed': {'fill': [52, 50, 48, 240], 'border': [150, 146, 140, 255], 'border_dark': [22, 20, 20, 255],
               'text': [236, 64, 44, 255], 'accent': [250, 210, 64, 255], 'dim': [150, 140, 130, 255],
               'shadow': [0, 0, 0, 220], 'select': [96, 20, 14, 240], 'frame': 'bevel'},
}


class Ctx:
    def __init__(self, layer, scene, anchors, cam=None, world=None, cam_light=None):
        self.layer = layer
        self.d = ImageDraw.Draw(layer)
        self.d.fontmode = '1'
        self.W, self.H = layer.size
        ui = scene.get('ui', {})
        theme = ui.get('theme', 'classic')
        if theme not in THEMES:
            raise KeyError(f"unknown ui theme '{theme}'. Themes: {', '.join(THEMES)}")
        self.t = {**THEMES[theme], **{k: v for k, v in ui.items() if k != 'theme'}}
        if 'name' in ui:                                  # backwards-compatible key
            self.t['accent'] = ui['name']
        self.font = _font(ui)
        self.lh = self.font.line_height
        self.pad = int(ui.get('pad', 5))
        self.scene, self.anchors, self.cam, self.world = scene, anchors, cam or {}, world
        self.defs = scene.get('sprite_defs', {})
        self.icon_defs = scene.get('icon_defs', {})
        # every widget that shows an icon accepts icon_defs, sprite_defs and built-ins alike
        self.any_icon = {**self.icon_defs, **self.defs}
        self.cam_light = cam_light if cam_light is not None else np.ones(3, np.float32)
        self.emission = None   # the frame's light sources, which a held lantern or a muzzle flash adds to

    def c(self, key):
        return tuple(self.t[key])


class _PilFont:
    def __init__(self, font):
        self.font = font
        self.line_height = font.getbbox('Hg')[3] + 1
        self._d = ImageDraw.Draw(Image.new('L', (1, 1)))

    def getlength(self, text):
        return self._d.textlength(text, font=self.font)

    def draw(self, d, xy, text, fill):
        d.text(xy, text, font=self.font, fill=fill)


def _font(ui):
    f = ui.get('font', 'pixel')
    if f in (None, 'pixel'):
        return PixelFont()
    if f == 'pillow':
        return _PilFont(ImageFont.load_default_imagefont())
    return _PilFont(ImageFont.truetype(f, int(ui.get('font_size', 8))))


# ------------------------------------------------------------------ helpers

def wrap(font, text, max_w):
    lines = []
    for para in str(text).split('\n'):
        cur = ''
        for word in para.split(' '):
            trial = (cur + ' ' + word).strip()
            if font.getlength(trial) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def place(ctx, w, h, ov, default='center'):
    m = int(ov.get('margin', 6))
    W, H = ctx.W, ctx.H
    if 'x' in ov or 'y' in ov:
        x = int(ov.get('x', (W - w) // 2))
        y = int(ov.get('y', (H - h) // 2))
        x = W + x - w if x < 0 else x
        y = H + y - h if y < 0 else y
        return x, y
    at = ov.get('at', default)
    xs = {'left': m, 'center': (W - w) // 2, 'right': W - w - m}
    ys = {'top': m, 'center': (H - h) // 2, 'bottom': H - h - m}
    parts = at.split('-')
    v = parts[0] if parts[0] in ('top', 'bottom') else 'center'
    hz = parts[-1] if parts[-1] in ('left', 'right') else 'center'
    return xs[hz], ys[v]


def frame(ctx, box, fill=True):
    """Themed box: double gold border, single line, or Windows-95 style bevel."""
    d, x0, y0, x1, y1 = ctx.d, *box
    style = ctx.t.get('frame', 'double')
    if fill:
        d.rectangle(box, fill=ctx.c('fill'))
    if style == 'bevel':
        d.line([(x0, y1), (x0, y0), (x1, y0)], fill=ctx.c('border'))
        d.line([(x1, y0), (x1, y1), (x0, y1)], fill=ctx.c('border_dark'))
        d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1), (x1 - 1, y0 + 1)], fill=(128, 128, 128, 255))
        return
    if style == 'single':
        d.rectangle(box, outline=ctx.c('border'))
        return
    d.rectangle(box, outline=ctx.c('border_dark'))
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], outline=ctx.c('border'))
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], outline=ctx.c('border_dark'))
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        d.point((cx, cy), fill=(0, 0, 0, 0))
    for cx, cy in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        d.point((cx, cy), fill=ctx.c('border_dark'))


def text(ctx, xy, s, color=None, shadow=True):
    x, y = xy
    col = tuple(color) if color is not None else ctx.c('text')
    if shadow and ctx.t['shadow'][3] > 0:
        ctx.font.draw(ctx.d, (x + 1, y + 1), s, ctx.c('shadow'))
    ctx.font.draw(ctx.d, (x, y), s, col)


def big_text(ctx, xy, s, scale=3, color=None, outline=None, shadow=True):
    mask = _PIXEL.render_mask(s, scale)
    x, y = xy
    if outline is not False:
        thick = mask.filter(ImageFilter.MaxFilter(3 if scale < 3 else 5))
        if shadow:
            ctx.d.bitmap((x + scale, y + scale), thick, fill=(0, 0, 0, 160))
        ctx.d.bitmap((x, y), thick, fill=tuple(outline or [10, 6, 6, 255]))
    ctx.d.bitmap((x, y), mask, fill=tuple(color or ctx.t['accent']))
    return mask.size


def paste_rgba(ctx, rgba, xy, scale=1, tint=None):
    im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA')
    if scale != 1:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.NEAREST)
    ctx.layer.alpha_composite(im, (int(xy[0]), int(xy[1])))
    return im.size


def icon(ctx, name, xy, scale=1):
    if not name:
        return (0, 0)
    rgba, _ = icons.get_icon(name, ctx.any_icon)
    return paste_rgba(ctx, rgba, xy, scale)


def _items(opts):
    return [o if isinstance(o, dict) else {'text': str(o)} for o in opts]


# ------------------------------------------------------------------ dialogue widgets

def w_bubble(ctx, ov):
    pad, lh, name = ctx.pad, ctx.lh, ov.get('name')
    lines = wrap(ctx.font, ov['text'], int(ov.get('width', ctx.t.get('width', 150))))
    tw = max(ctx.font.getlength(s) for s in lines + ([name] if name else []))
    bw, bh = int(tw) + pad * 2 + 2, lh * (len(lines) + (1 if name else 0)) + pad * 2
    a = ctx.anchors.get(ov.get('anchor'))
    if a and a['visible']:
        ax = a['x']
        head = a['top'] + a['h'] * float(ov.get('head', 0.04))
        by0 = max(2, int(head - 3) - 7 - bh)
        bx0 = int(np.clip(ax - bw / 2 + float(ov.get('offset', 0)), 2, ctx.W - bw - 2))
    else:
        ax = head = None
        bx0, by0 = (ctx.W - bw) // 2, 6
    box = [bx0, by0, bx0 + bw, by0 + bh]
    frame(ctx, box)
    if ax is not None and head - box[3] > 2:
        tx = int(np.clip(ax, box[0] + 6, box[2] - 6))
        tip = (int(ax), int(head - 2))
        ctx.d.polygon([(tx - 4, box[3] - 2), (tx + 4, box[3] - 2), tip], fill=ctx.c('fill'))
        ctx.d.line([(tx - 4, box[3]), tip], fill=ctx.c('border'))
        ctx.d.line([(tx + 4, box[3]), tip], fill=ctx.c('border'))
        for k in (1, 2):
            ctx.d.line([(tx - 3, box[3] - k), (tx + 3, box[3] - k)], fill=ctx.c('fill'))
    y = box[1] + pad
    if name:
        text(ctx, (box[0] + pad + 1, y), name, ctx.t['accent'])
        y += lh
    for s in lines:
        text(ctx, (box[0] + pad + 1, y), s)
        y += lh


def _portrait(ctx, spec, size):
    try:
        rgba, _ = assets.get_sprite(spec, ctx.defs)
        crop = rgba[:min(rgba.shape[0], rgba.shape[1])]
    except KeyError:
        crop, _ = icons.get_icon(spec, ctx.icon_defs)
    im = Image.fromarray((np.clip(crop, 0, 1) * 255).astype(np.uint8), 'RGBA')
    k = max(1, int(size // max(im.width, im.height)))
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def w_dialog(ctx, ov):
    pad, lh, name = ctx.pad, ctx.lh, ov.get('name')
    margin = 6
    psize = 40 if ov.get('portrait') else 0
    x0 = margin
    inner_x = x0 + pad + (psize + pad + 2 if psize else 0)
    lines = wrap(ctx.font, ov['text'], ctx.W - margin - pad - inner_x - 4)
    bh = max(psize + pad * 2, lh * (len(lines) + (1 if name else 0)) + pad * 2 + 4)
    y0 = margin if ov.get('position', ov.get('at', 'bottom')) == 'top' else ctx.H - margin - bh
    box = [x0, y0, ctx.W - margin, y0 + bh]
    frame(ctx, box)
    if psize:
        fx, fy = x0 + pad, y0 + pad
        ctx.d.rectangle([fx - 1, fy - 1, fx + psize, fy + psize], fill=(4, 4, 8, 255), outline=ctx.c('border'))
        p = _portrait(ctx, ov['portrait'], psize - 2)
        px = fx + (psize - p.width) // 2
        ctx.layer.alpha_composite(p.crop((0, 0, min(p.width, psize - 1), min(p.height, psize - 1))), (max(fx, px), fy + 1))
    y = y0 + pad + 1
    if name:
        text(ctx, (inner_x, y), name, ctx.t['accent'])
        y += lh
    for s in lines:
        text(ctx, (inner_x, y), s)
        y += lh
    if ov.get('more', True):
        ax, ay = box[2] - pad - 4, box[3] - pad - 3
        ctx.d.polygon([(ax - 3, ay - 2), (ax + 3, ay - 2), (ax, ay + 1)], fill=ctx.c('accent'))


def w_caption(ctx, ov):
    lines = wrap(ctx.font, ov['text'], int(ov.get('width', ctx.W - 16)))
    tw = max(ctx.font.getlength(s) for s in lines)
    h = ctx.lh * len(lines)
    if 'at' in ov:
        x, y = place(ctx, int(tw), h, ov)
    else:
        x, y = int(ov.get('x', 8)), int(ov.get('y', 8))
    if ov.get('box'):
        frame(ctx, [x - ctx.pad, y - ctx.pad + 1, x + int(tw) + ctx.pad, y + h + ctx.pad - 1])
    for s in lines:
        text(ctx, (x, y), s, ov.get('color'))
        y += ctx.lh


def w_choice(ctx, ov):
    """Menu with a pointer next to the selected option. Options may be strings or
    {"text": "...", "hint": "3 idols", "disabled": true}."""
    pad, lh = ctx.pad, ctx.lh
    opts = _items(ov['options'])
    sel = ov.get('selected', 0)
    sel = -1 if sel is None else int(sel)  # "selected": null draws the menu with nothing highlighted
    prompt = wrap(ctx.font, ov['prompt'], int(ov.get('width', 170))) if ov.get('prompt') else []
    gutter = 12
    rows_w = [ctx.font.getlength(o['text']) + (ctx.font.getlength(o['hint']) + 12 if o.get('hint') else 0) for o in opts]
    tw = max(rows_w + [ctx.font.getlength(s) - gutter for s in prompt])
    bw = int(tw) + gutter + pad * 2 + 4
    bh = lh * (len(opts) + len(prompt)) + pad * 2 + (4 if prompt else 0) + 2
    x0, y0 = place(ctx, bw, bh, ov, 'center')
    frame(ctx, [x0, y0, x0 + bw, y0 + bh])
    y = y0 + pad + 1
    for s in prompt:
        text(ctx, (x0 + pad + 1, y), s)
        y += lh
    if prompt:
        ctx.d.line([(x0 + pad, y + 1), (x0 + bw - pad, y + 1)], fill=ctx.c('border_dark'))
        y += 4
    for i, o in enumerate(opts):
        tx = x0 + pad + gutter
        is_sel = i == sel
        col = ctx.t['dim'] if o.get('disabled') else ctx.t['text']
        if is_sel:
            ctx.d.rectangle([x0 + pad, y - 1, x0 + bw - pad, y + lh - 2], fill=ctx.c('select'))
            col = ctx.t.get('select_text', ctx.t['accent'])
            ptr = ov.get('pointer', 'arrow')
            if ptr == 'hand':
                icon(ctx, 'hand_pointer', (x0 + pad - 9, y - 1))
            elif ptr == 'arrow':
                px, py = x0 + pad + 3, y + 1
                ctx.d.polygon([(px, py), (px + 4, py + 3), (px, py + 6)], fill=tuple(col))
        text(ctx, (tx, y), o['text'], col, shadow=not (is_sel and ctx.t.get('frame') == 'bevel'))
        if o.get('hint'):
            hw = ctx.font.getlength(o['hint'])
            text(ctx, (x0 + bw - pad - 2 - hw, y), o['hint'], ctx.t['dim'] if not is_sel else col)
        y += lh


def w_title(ctx, ov):
    scale = int(ov.get('scale', 3))
    f = _PIXEL
    s = ov['text']
    room = ctx.W - 2 * int(ov.get('margin', 6))
    # a long title at scale 4 runs off both edges of a 320px frame: step down until it fits
    while scale > 1 and f.getlength(s) * scale > room:
        scale -= 1
    w, h = f.getlength(s) * scale, 9 * scale
    sub = ov.get('subtitle')
    sub_lines = wrap(ctx.font, sub, room) if sub else []
    sh = ctx.lh * len(sub_lines) + 4 if sub else 0
    x, y = place(ctx, w, h + sh, ov, 'center')
    if ov.get('band'):
        ctx.d.rectangle([0, y - 6, ctx.W, y + h + sh + 4], fill=tuple(ov.get('band_color', [0, 0, 0, 170])))
    big_text(ctx, (x, y), s, scale, ov.get('color'), ov.get('outline'))
    centred = ov.get('at', 'center') in ('center', 'top', 'bottom')
    for k, line in enumerate(sub_lines):
        sw = ctx.font.getlength(line)
        text(ctx, ((ctx.W - sw) // 2 if centred else x, y + h + 4 + k * ctx.lh), line,
             ov.get('subtitle_color'))


def w_panel(ctx, ov):
    """Titled box of lines, e.g. an objectives list. Lines may be strings or {"text","done","icon"}."""
    pad, lh = ctx.pad, ctx.lh
    lines = _items(ov.get('lines', []))
    title = ov.get('title')
    width = int(ov.get('width', 0)) or int(max([ctx.font.getlength(l['text']) + (12 if l.get('icon') or 'done' in l else 0)
                                                for l in lines] + [ctx.font.getlength(title or '')])) + pad * 2 + 4
    # an unwrapped long objective would size the panel past the frame edge: cap it and wrap
    width = min(width, ctx.W - 2 * int(ov.get('margin', 6)))
    wrapped = []
    for l in lines:
        indent = 12 if (l.get('icon') or 'done' in l) else 0
        for k, s in enumerate(wrap(ctx.font, l['text'], width - pad * 2 - 4 - indent)):
            wrapped.append((l, s, k == 0, indent))
    bh = lh * (len(wrapped) + (1 if title else 0)) + pad * 2 + (3 if title else 0)
    x0, y0 = place(ctx, width, bh, ov, 'top-right')
    frame(ctx, [x0, y0, x0 + width, y0 + bh])
    y = y0 + pad + 1
    if title:
        text(ctx, (x0 + pad + 1, y), title, ctx.t['accent'])
        y += lh
        ctx.d.line([(x0 + pad, y), (x0 + width - pad, y)], fill=ctx.c('border_dark'))
        y += 3
    for l, s, first, indent in wrapped:
        if first and 'done' in l:
            bx, by = x0 + pad + 1, y + 1
            ctx.d.rectangle([bx, by, bx + 6, by + 6], outline=ctx.c('border'))
            if l['done']:
                ctx.d.line([(bx + 1, by + 3), (bx + 3, by + 5), (bx + 6, by)], fill=ctx.c('accent'))
        elif first and l.get('icon'):
            rgba, _ = icons.get_icon(l['icon'], ctx.any_icon)
            paste_rgba(ctx, rgba, (x0 + pad, y - 1), 9 / max(rgba.shape[:2]))
        col = ctx.t['dim'] if l.get('done') else None
        text(ctx, (x0 + pad + 1 + indent, y), s, col)
        y += lh


def w_toast(ctx, ov):
    """Pickup / notification line with an optional icon, e.g. 'Found: Bolt Cutters'."""
    pad = ctx.pad
    ic = ov.get('icon')
    iw = 20 if ic else 0
    room = ctx.W - 2 * int(ov.get('margin', 6)) - iw - pad * 2 - 4
    lines = wrap(ctx.font, ov['text'], room)   # one line unless it would leave the frame
    tw = max(ctx.font.getlength(s) for s in lines)
    th = ctx.lh * len(lines)
    bw, bh = int(tw) + iw + pad * 2 + 4, max(th, 18 if ic else 0) + pad * 2 - 2
    x0, y0 = place(ctx, bw, bh, ov, 'top')
    frame(ctx, [x0, y0, x0 + bw, y0 + bh])
    if ic:
        icon(ctx, ic, (x0 + pad, y0 + (bh - 16) // 2))
    ty = y0 + (bh - th) // 2 + 1
    for s in lines:
        text(ctx, (x0 + pad + iw + 1, ty), s, ov.get('color'))
        ty += ctx.lh


def w_prompt(ctx, ov):
    """Interaction hint: a key cap plus an action, e.g. [E] Open."""
    key, s = str(ov.get('key', 'E')), ov['text']
    kw = ctx.font.getlength(key) + 6
    w = int(kw + 5 + ctx.font.getlength(s))
    x, y = place(ctx, w, 13, ov, 'center')
    if 'at' not in ov and 'x' not in ov and 'y' not in ov:
        y = int(ctx.H * 0.62)
    ctx.d.rectangle([x, y, x + kw, y + 12], fill=ctx.c('fill'), outline=ctx.c('border'))
    ctx.d.line([(x + 1, y + 12), (x + kw - 1, y + 12)], fill=ctx.c('border_dark'))
    text(ctx, (x + 3, y + 2), key, ctx.t['accent'], shadow=False)
    text(ctx, (x + kw + 5, y + 2), s)


# ------------------------------------------------------------------ HUD widgets

def w_bars(ctx, ov):
    """Stacked labelled meters. items: [{"label": "HP", "value": 0.7, "color": [200,40,40]}, ...]."""
    items = ov['items']
    bw = int(ov.get('width', 64))
    labw = int(max(ctx.font.getlength(i.get('label', '')) for i in items)) + 4
    h = len(items) * 11 - 2
    x, y = place(ctx, labw + bw + 2, h, ov, 'top-left')
    for it in items:
        v = float(np.clip(it.get('value', 1.0), 0, 1))
        col = tuple(it.get('color', [190, 40, 36])) + ((255,) if len(it.get('color', [0, 0, 0])) == 3 else ())
        text(ctx, (x, y), it.get('label', ''), ctx.t['text'])
        bx = x + labw
        ctx.d.rectangle([bx, y + 1, bx + bw, y + 8], fill=(0, 0, 0, 200), outline=ctx.c('border_dark'))
        fw = int((bw - 2) * v)
        if fw > 0:
            ctx.d.rectangle([bx + 1, y + 2, bx + fw, y + 7], fill=col)
            hi = tuple(min(255, int(c * 1.35)) for c in col[:3]) + (255,)
            ctx.d.line([(bx + 1, y + 2), (bx + fw, y + 2)], fill=hi)
        if it.get('segments'):
            n = int(it['segments'])
            for k in range(1, n):
                sx = bx + 1 + (bw - 2) * k // n
                ctx.d.line([(sx, y + 2), (sx, y + 7)], fill=(0, 0, 0, 255))
        y += 11


def w_counter(ctx, ov):
    """Big HUD number with an icon, e.g. ammo 6/18."""
    scale = int(ov.get('scale', 2))
    s = str(ov['value'])
    w = _PIXEL.getlength(s) * scale
    ic = ov.get('icon')
    iw = 22 if ic else 0
    x, y = place(ctx, w + iw, 9 * scale, ov, 'bottom-right')
    if ic:
        icon(ctx, ic, (x, y + (9 * scale - 16) // 2))
    big_text(ctx, (x + iw, y), s, scale, ov.get('color'), shadow=False)
    if ov.get('label'):
        text(ctx, (x + iw, y - ctx.lh - 2), ov['label'], ctx.t['dim'])


def _slot_items(slots):
    out = []
    for s in slots:
        if s is None or isinstance(s, str):
            out.append({'icon': s})
        else:
            out.append(s)
    return out


def w_hotbar(ctx, ov):
    slots = _slot_items(ov['slots'])
    sz = int(ov.get('slot', 20))
    n = len(slots)
    w = n * sz + (n - 1) * 2
    x, y = place(ctx, w, sz, ov, 'bottom')
    sel = ov.get('selected')
    for i, s in enumerate(slots):
        bx = x + i * (sz + 2)
        box = [bx, y, bx + sz - 1, y + sz - 1]
        ctx.d.rectangle(box, fill=ctx.c('fill'), outline=ctx.c('border_dark'))
        if i == sel:
            ctx.d.rectangle(box, outline=ctx.c('accent'))
            ctx.d.rectangle([bx + 1, y + 1, bx + sz - 2, y + sz - 2], outline=ctx.c('accent'))
        if s.get('icon'):
            icon(ctx, s['icon'], (bx + (sz - 16) // 2, y + (sz - 16) // 2))
        if s.get('count') is not None:
            c = str(s['count'])
            text(ctx, (bx + sz - 2 - ctx.font.getlength(c), y + sz - 10), c, ctx.t['text'])
        if ov.get('numbers', False):
            ctx.font.draw(ctx.d, (bx + 2, y + 1), str((i + 1) % 10), ctx.c('dim'))


def w_inventory(ctx, ov):
    """Grid of items in a titled panel, with the selected item's name and description below."""
    items = _slot_items(ov['items'])
    cols = int(ov.get('columns', 5))
    rows = max(1, math.ceil(len(items) / cols))
    sz, pad = 22, ctx.pad
    gw = cols * sz + (cols - 1) * 3
    desc_w = max(gw, int(ov.get('width', 0)))
    sel = ov.get('selected')
    title = ov.get('title', 'Inventory')
    s_item = items[sel] if sel is not None and sel < len(items) else None
    dlines = []
    if s_item:
        if s_item.get('name'):
            dlines.append(('name', s_item['name']))
        for s in wrap(ctx.font, s_item.get('description', ''), desc_w) if s_item.get('description') else []:
            dlines.append(('text', s))
    bw = desc_w + pad * 2 + 2
    bh = ctx.lh + 4 + rows * sz + (rows - 1) * 3 + pad * 2 + (len(dlines) * ctx.lh + 6 if dlines else 0)
    x0, y0 = place(ctx, bw, bh, ov, 'center')
    frame(ctx, [x0, y0, x0 + bw, y0 + bh])
    text(ctx, (x0 + pad + 1, y0 + pad), title, ctx.t['accent'])
    gx, gy = x0 + pad + 1 + (desc_w - gw) // 2, y0 + pad + ctx.lh + 4
    for i in range(rows * cols):
        bx, by = gx + (i % cols) * (sz + 3), gy + (i // cols) * (sz + 3)
        ctx.d.rectangle([bx, by, bx + sz - 1, by + sz - 1], fill=(0, 0, 0, 120), outline=ctx.c('border_dark'))
        if i < len(items):
            it = items[i]
            if i == sel:
                ctx.d.rectangle([bx, by, bx + sz - 1, by + sz - 1], fill=ctx.c('select'), outline=ctx.c('accent'))
            if it.get('icon'):
                icon(ctx, it['icon'], (bx + 3, by + 3))
            if it.get('count') is not None:
                c = str(it['count'])
                text(ctx, (bx + sz - 2 - ctx.font.getlength(c), by + sz - 10), c)
    y = gy + rows * sz + (rows - 1) * 3 + 6
    for kind, s in dlines:
        text(ctx, (x0 + pad + 1, y), s, ctx.t['accent'] if kind == 'name' else None)
        y += ctx.lh


def w_crosshair(ctx, ov):
    cx, cy = ctx.W // 2, int(ctx.H / 2 + float(ctx.cam.get('pitch', 0)) * ctx.H)
    col = tuple(ov.get('color', [240, 240, 230, 220]))
    st = ov.get('style', 'cross')
    d = ctx.d
    if st == 'dot':
        d.rectangle([cx - 1, cy - 1, cx, cy], fill=col)
    elif st == 'circle':
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], outline=col)
        d.point((cx, cy), fill=col)
    else:
        for a, b in (((cx - 6, cy), (cx - 3, cy)), ((cx + 3, cy), (cx + 6, cy)), ((cx, cy - 6), (cx, cy - 3)), ((cx, cy + 3), (cx, cy + 6))):
            d.line([a, b], fill=col)


def w_compass(ctx, ov):
    """Heading strip. North is map-up (-y), matching camera angle 270."""
    w = int(ov.get('width', 140))
    h = 14
    x0, y0 = place(ctx, w, h, ov, 'top')
    frame(ctx, [x0, y0, x0 + w, y0 + h])
    ang = float(ctx.cam.get('angle', 0))
    span = float(ov.get('span', 120))
    names = {270: 'N', 0: 'E', 90: 'S', 180: 'W', 315: 'NE', 45: 'SE', 135: 'SW', 225: 'NW'}
    for deg in range(0, 360, 15):
        delta = (deg - ang + 540) % 360 - 180
        if abs(delta) > span / 2:
            continue
        x = x0 + w / 2 + delta / span * (w - 8)
        if deg in names:
            lab = names[deg]
            col = ctx.t['accent'] if lab == 'N' else ctx.t['text']
            text(ctx, (int(x - ctx.font.getlength(lab) / 2), y0 + 3), lab, col, shadow=False)
        else:
            ctx.d.line([(int(x), y0 + 9), (int(x), y0 + 11)], fill=ctx.c('dim'))
    ctx.d.polygon([(x0 + w // 2 - 2, y0 + h + 1), (x0 + w // 2 + 2, y0 + h + 1), (x0 + w // 2, y0 + h - 2)], fill=ctx.c('accent'))


def w_automap(ctx, ov):
    """Doom-style automap of the scene grid around the camera: wall edges, player arrow, markers."""
    world = ctx.world
    if world is None:
        return
    full = ov.get('mode') == 'full'
    size = (ctx.W - 24, ctx.H - 24) if full else (int(ov.get('size', 76)),) * 2
    x0, y0 = place(ctx, size[0], size[1], ov, 'center' if full else 'top-right')
    cell = float(ov.get('cell', 5 if not full else 7))
    px, py = float(ctx.cam.get('x', 0)), float(ctx.cam.get('y', 0))
    frame(ctx, [x0, y0, x0 + size[0], y0 + size[1]])
    clip = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(clip)
    wall_col = tuple(ov.get('wall_color', ctx.t['border'][:3] + [255]))
    low_col = tuple(ov.get('low_color', ctx.t['dim'][:3] + [255]))
    cx, cy = size[0] / 2, size[1] / 2

    def sx(x):
        return cx + (x - px) * cell

    def sy(y):
        return cy + (y - py) * cell
    hgt = world.height
    for y in range(world.mh):
        for x in range(world.mw):
            if hgt[y, x] <= 0:
                continue
            col = wall_col if hgt[y, x] >= 0.95 else low_col
            for nx, ny, seg in ((x - 1, y, [(x, y), (x, y + 1)]), (x + 1, y, [(x + 1, y), (x + 1, y + 1)]),
                                (x, y - 1, [(x, y), (x + 1, y)]), (x, y + 1, [(x, y + 1), (x + 1, y + 1)])):
                if 0 <= nx < world.mw and 0 <= ny < world.mh and hgt[ny, nx] < hgt[y, x]:
                    d.line([(sx(seg[0][0]), sy(seg[0][1])), (sx(seg[1][0]), sy(seg[1][1]))], fill=col)
    for m in ov.get('markers', []):
        mx, my = sx(m['x']), sy(m['y'])
        mc = tuple(m.get('color', [230, 60, 50])) + (255,)
        d.rectangle([mx - 1, my - 1, mx + 1, my + 1], fill=mc)
    a = math.radians(float(ctx.cam.get('angle', 0)))
    pts = [(cx + math.cos(a) * 5, cy + math.sin(a) * 5),
           (cx + math.cos(a + 2.5) * 4, cy + math.sin(a + 2.5) * 4),
           (cx + math.cos(a - 2.5) * 4, cy + math.sin(a - 2.5) * 4)]
    d.polygon(pts, fill=ctx.c('accent'))
    inner = clip.crop((3, 3, size[0] - 3, size[1] - 3))
    ctx.layer.alpha_composite(inner, (x0 + 3, y0 + 3))
    if ov.get('title'):
        text(ctx, (x0 + 5, y0 + 4), ov['title'], ctx.t['accent'])


def w_statusbar(ctx, ov):
    """The stone status bar of a 1993 shooter along the bottom of the screen (scripts/doomed.py): ammo,
    health %, the arms owned (2-7), a face that bloodies as health falls, armour %, keys and the
    ammo table. {"ammo": 26, "health": 28, "armor": 75, "arms": [2, 3], "keys": ["blue"],
    "ammo_table": [[26, 200], [8, 50], [0, 50], [0, 300]], "face": "auto"|"grin"|"ouch"|"dead",
    "look": -1|0|1}. It takes the bottom sixth of the frame; aim the camera with that in mind."""
    import doomed
    bh = int(round(ctx.H * float(ov.get('height', 0.16))))
    rgb = doomed.statusbar(ctx.W, bh, ov)
    im = Image.fromarray((rgb * 255).astype(np.uint8), 'RGB').convert('RGBA')
    ctx.layer.alpha_composite(im, (0, ctx.H - bh))


def w_message(ctx, ov):
    """A game message at the top left, plain text with no box, as a pickup was reported in 1993:
    {"text": "Picked up a clip."}; `color` (the theme's text colour by default)."""
    m = int(ov.get('margin', 2))
    y = m
    for s in str(ov['text']).splitlines():
        text(ctx, (m, y), s, ov.get('color'))
        y += ctx.lh


def w_image(ctx, ov):
    """Any icon or sprite placed on screen, e.g. a logo, a held note, a portrait."""
    rgba, _ = icons.get_icon(ov['name'], ctx.any_icon)
    scale = float(ov.get('scale', 1))
    w, h = int(rgba.shape[1] * scale), int(rgba.shape[0] * scale)
    x, y = place(ctx, w, h, ov, 'center')
    paste_rgba(ctx, rgba, (x, y), scale)


# viewmodels draw straight into the float frame (before post effects) so they are lit and graded
def draw_viewmodel(img, ov, ctx):
    rgba, em, v = icons.get_viewmodel(ov['item'], ctx.scene.get('viewmodel_defs', {}), fire=ov.get('fire', False))
    scale = float(ov.get('scale', 1.0))
    if scale != 1:
        im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA').resize(
            (int(rgba.shape[1] * scale), int(rgba.shape[0] * scale)), Image.NEAREST)
        rgba = np.asarray(im, np.float32) / 255
        em = np.asarray(Image.fromarray((em * 255).astype(np.uint8)).resize(im.size, Image.NEAREST), np.float32) / 255
    H, W = img.shape[:2]
    h, w = rgba.shape[:2]
    x0, y0 = icons.viewmodel_origin(W, H, w, h, ov.get('side', v.get('anchor', 'right')),
                                    ov.get('x_offset', 0), ov.get('y_offset', 0))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    x1, y1 = min(W, x0 + w), min(H, y0 + h)
    if x1 <= max(0, x0) or y1 <= max(0, y0):
        return img
    part = rgba[sy0:sy0 + (y1 - max(0, y0)), sx0:sx0 + (x1 - max(0, x0))]
    e = em[sy0:sy0 + part.shape[0], sx0:sx0 + part.shape[1]][..., None]
    light = np.clip(ctx.cam_light * float(ov.get('brightness', 1.0)), 0, 1.6)
    col = part[..., :3] * (light * (1 - e) + 1.1 * e)
    a = part[..., 3:4]
    region = img[max(0, y0):y1, max(0, x0):x1]
    region[:] = region * (1 - a) + col * a
    if ctx.emission is not None and e.any():           # its flame or flash gives off light (bloom)
        em = ctx.emission.copy()
        reg = em[max(0, y0):y1, max(0, x0):x1]
        reg[:] = reg * (1 - a) + part[..., :3] * 1.1 * e * a
        ctx.emission = em
    return img


WIDGETS = {k[2:]: v for k, v in list(globals().items()) if k.startswith('w_')}


def draw_world_layer(img, overlays, ctx):
    # a status bar takes the bottom of the screen: whatever is held is held up above it
    bar = next((o for o in overlays if o.get('type') == 'statusbar'), None)
    lift = int(round(img.shape[0] * float(bar.get('height', 0.16)))) if bar else 0
    for ov in overlays:
        if ov.get('type') == 'viewmodel':
            if lift:
                ov = dict(ov, y_offset=int(ov.get('y_offset', 0)) - lift)
            img = draw_viewmodel(img, ov, ctx)
    return img


def draw_ui_layer(img, overlays, ctx):
    ui = [ov for ov in overlays if ov.get('type', 'bubble') != 'viewmodel']
    if not ui:
        return img
    for ov in ui:
        kind = ov.get('type', 'bubble')
        if kind not in WIDGETS:
            raise KeyError(f"unknown overlay type '{kind}'. Types: {sorted(WIDGETS) + ['viewmodel']}")
        WIDGETS[kind](ctx, ov)
    return overlay_ui(img, ctx)


def overlay_ui(img, ctx):
    """The widgets already drawn on ctx's layer, laid over a frame (again, without drawing them twice)."""
    lay = np.asarray(ctx.layer, np.float32) / 255
    a = lay[..., 3:4]
    return img * (1 - a) + lay[..., :3] * a

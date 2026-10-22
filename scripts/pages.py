"""Pages: several shots laid out on one page - a comic page or a storyboard - each panel a shot of any scene,
rendered at the panel's own size and shape, with the shot's own speech bubbles, caption boxes, big lettering
for a sound, and a title over it all.

    python pages.py page.json -o page.png

A page file (scene paths are relative to it):

    {"style": "comic",                                   # or "storyboard"
     "width": 1200, "title": "THE DOOR ON THE SALT FLAT",
     "rows": [{"height": 420, "panels": [
                 {"scene": "../salt_flat.json", "shot": 1, "width": 2, "caption": "An hour before dark."},
                 {"scene": "../salt_flat.json", "shot": 6, "caption": "Someone had left the door open."}]},
              {"height": 330, "panels": [{"scene": "../winter_woods.json", "shot": 1,
                                          "sfx": {"text": "CREAK", "x": 0.7, "y": 0.2}}]}]}

A panel takes `scene` and `shot` (counted from 1), `camera` (fields laid over the shot's: move it, turn it, give
it a `fov`), `overlays` (in place of the shot's own: `[]` for none - by default a comic keeps them but its captions,
the page has its own, and a storyboard keeps none: its words are in its notes), `caption` (a box of narration at its top - or `caption_at` bottom), `sfx` (a sound in big
letters: `text`, where across and down it as shares of the panel, `color`, `scale` - page pixels to a letter's
pixel, default 8), `note` (on a storyboard,
under the panel) and `width` (its share of its row, default 1). A row takes `height` (pixels on the page).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lettering  # noqa: E402
from pixelart import rgb  # noqa: E402

STYLES = {
    'comic': dict(paper='#f2ecdd', ink='#16130f', border=4, gutter=14, margin=26, box='#f4e7a4', box_ink='#16130f',
                  title='#16130f', numbers=False, notes=False),
    'storyboard': dict(paper='#26262b', ink='#e6e4dc', border=2, gutter=20, margin=28, box='#e6e4dc', box_ink='#1a1a1e',
                       title='#e6e4dc', numbers=True, notes=True),
}


def _c(c):
    return tuple(int(round(v * 255)) for v in rgb(c))


def _paste_mask(page, m, xy, color, k=1):
    """Ink a boolean mask onto the page at xy, each of its pixels k x k."""
    if k > 1:
        m = np.repeat(np.repeat(m, k, 0), k, 1)
    im = Image.fromarray((m * 255).astype(np.uint8), 'L')
    page.paste(Image.new('RGB', im.size, color), (int(xy[0]), int(xy[1])), im)


def _wrap(text, max_px, k):
    """Text broken into lines no wider than max_px at k page pixels to a font pixel."""
    out = []
    for para in str(text).split('\n'):
        cur = ''
        for word in para.split(' '):
            trial = (cur + ' ' + word).strip()
            if lettering._FONT.getlength(trial) * k <= max_px or not cur:
                cur = trial
            else:
                out.append(cur)
                cur = word
        out.append(cur)
    return out


def _box(page, d, lines, xy, k, st):
    """A caption box: the lines of narration in the box's ink on its colour, inside a rule, at xy (its top left)."""
    w = max(lettering._FONT.getlength(s) for s in lines) * k
    lh = 11 * k
    pad = 3 * k
    x0, y0 = xy
    x1, y1 = x0 + w + 2 * pad, y0 + lh * len(lines) + 2 * pad - 2 * k
    d.rectangle([x0, y0, x1, y1], fill=_c(st['box']), outline=_c(st['box_ink']), width=max(2, k))
    for i, s in enumerate(lines):
        m = np.asarray(lettering._FONT.render_mask(s)) > 127
        _paste_mask(page, m, (x0 + pad, y0 + pad + i * lh - k), _c(st['box_ink']), k)
    return x1, y1


def _render_panel(p, w, h, k, base, keep=True):
    """One panel's picture, w x h page pixels: its shot of its scene rendered at w/k x h/k and scaled k - with the
    shot's own overlays but its captions (`keep`; a storyboard keeps none) unless the panel gives its own."""
    import render as R
    sc = R.load_scene(os.path.join(base, p['scene']))
    shots = list(sc.get('shots') or [sc['camera']])
    i = max(0, min(len(shots), int(p.get('shot', 1))) - 1)
    shot = dict(shots[i])
    cam = p.get('camera') or {}
    if 'angle' in cam and 'look_at' not in cam:
        shot.pop('look_at', None)
    shot.update(cam)
    if 'overlays' in p:
        shot['overlays'] = list(p['overlays'])
    else:
        shot['overlays'] = [ov for ov in shot.get('overlays', []) if keep and ov.get('type') != 'caption']
    shots[i] = shot
    sc = dict(sc, shots=shots, resolution=[max(16, w // k), max(16, h // k)], scale=k)
    im = R.render_shot(sc, i).convert('RGB')
    return im.resize((w, h), Image.NEAREST) if im.size != (w, h) else im


def render_page(spec, base='.'):
    """A page (see the module's notes) as an image."""
    st = dict(STYLES[spec.get('style', 'comic')], **spec.get('look', {}))
    k = int(spec.get('scale', 3))                                     # page pixels to a frame's pixel
    PW = int(spec.get('width', 1200))
    m, g, b = st['margin'], st['gutter'], st['border']
    title = spec.get('title')
    tm = lettering.mask(title, 2, smooth=True) if title else None
    tk = 2 if title else 0
    top = m + (tm.shape[0] * tk + m // 2 if title else 0)
    note_h = 3 * 11 * 2 if st['notes'] else 0
    rows = spec['rows']
    PH = top + sum(int(r['height']) + note_h for r in rows) + g * (len(rows) - 1) + m
    page = Image.new('RGB', (PW, PH), _c(st['paper']))
    d = ImageDraw.Draw(page)
    if title:
        _paste_mask(page, tm, ((PW - tm.shape[1] * tk) // 2, m), _c(st['title']), tk)
    y, n = top, 0
    for row in rows:
        RH = int(row['height'])
        panels = row['panels']
        weights = [float(p.get('width', 1)) for p in panels]
        avail = PW - 2 * m - g * (len(panels) - 1)
        x = m
        for j, (p, wt) in enumerate(zip(panels, weights)):
            n += 1
            pw = avail - (x - m - g * j) if j == len(panels) - 1 else int(avail * wt / sum(weights))
            im = _render_panel(p, pw - 2 * b, RH - 2 * b, k, base, keep=not st['notes'])
            d.rectangle([x, y, x + pw - 1, y + RH - 1], fill=_c(st['ink']))
            page.paste(im, (x + b, y + b))
            if p.get('sfx'):                                          # a sound, in big letters
                s = p['sfx'] if isinstance(p['sfx'], dict) else {'text': p['sfx']}
                sm = lettering.mask(s['text'], int(s.get('scale', 8)), smooth=True)
                ring = lettering._grow(np.pad(sm, 3), 3)
                sx = x + b + int(float(s.get('x', 0.5)) * (pw - 2 * b)) - ring.shape[1] // 2
                sy = y + b + int(float(s.get('y', 0.25)) * (RH - 2 * b)) - ring.shape[0] // 2
                _paste_mask(page, ring, (sx, sy), _c(st['box_ink']))
                _paste_mask(page, np.pad(sm, 3), (sx, sy), _c(s.get('color', '#f4d24a')))
            if p.get('caption'):
                lines = _wrap(p['caption'], int((pw - 2 * b) * 0.62), 2)
                if p.get('caption_at') == 'bottom':
                    ch = len(lines) * 22 + 12 - 4
                    _box(page, d, lines, (x + b + 8, y + RH - b - 8 - ch), 2, st)
                else:
                    _box(page, d, lines, (x + b + 8, y + b + 8), 2, st)
            if st['numbers']:                                         # a storyboard's panel number
                nm = np.asarray(lettering._FONT.render_mask(str(n))) > 127
                d.rectangle([x + b, y + b, x + b + nm.shape[1] * 2 + 10, y + b + 24], fill=_c(st['ink']))
                _paste_mask(page, nm, (x + b + 5, y + b + 4), _c(st['paper']), 2)
            if st['notes'] and p.get('note'):
                for li, s in enumerate(_wrap(p['note'], pw, 2)[:3]):
                    nm = np.asarray(lettering._FONT.render_mask(s)) > 127
                    _paste_mask(page, nm, (x, y + RH + 6 + li * 22), _c(st['ink']), 2)
            x += pw + g
        y += RH + note_h + g
    return page


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('page', help='a page file (JSON)')
    ap.add_argument('-o', '--out', default='page.png')
    a = ap.parse_args()
    with open(a.page, encoding='utf-8-sig') as f:
        spec = json.load(f)
    render_page(spec, os.path.dirname(os.path.abspath(a.page))).save(a.out)
    print(a.out)


if __name__ == '__main__':
    main()

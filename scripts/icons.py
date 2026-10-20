"""Item icons, menu pointers and first-person held items ("viewmodels"), drawn from short lists of
draw operations and finished with an automatic 1px outline so they read as pixel art.

Draw op format: (kind, coords, colour, [width])
  kind: line | rect | ellipse | ring | poly | px
  colour: '#rrggbb'; prefix with '!' to make those pixels emissive (glow regardless of lighting)
New icons can be defined in a scene under "icon_defs": {"name": {"size": 16, "ops": [...]}}.
"""
import importlib

import numpy as np
from PIL import Image, ImageDraw

OUTLINE = '#120e0c'

# shared colours
METAL, METAL_D, METAL_L = '#8a9098', '#4e545c', '#c8ccd2'
IRON, IRON_D = '#4a4a50', '#2a2a2e'
WOOD, WOOD_D, WOOD_L = '#7a5030', '#4a2e18', '#a06a40'
RED, RED_D = '#b03028', '#6a1a14'
GOLD, GOLD_D, GOLD_L = '#d8a830', '#8a6418', '#f8e070'
PAPER, PAPER_D, INK = '#e8dcc0', '#b0a080', '#3a3040'
SKIN, SKIN_D, SKIN_L = '#c88a62', '#8e5a3e', '#e0a880'
COAT, COAT_D, COAT_L = '#2e2e36', '#1a1a20', '#45454f'
GLOW, GLOW_W = '!#ffc860', '!#fff2b8'

ICONS = {
    'revolver': [('poly', [(1, 13), (4, 13), (6, 8), (3, 8)], WOOD), ('line', [2, 12, 4, 9], WOOD_L),
                 ('rect', [4, 5, 8, 9], METAL_D), ('line', [5, 6, 7, 6], METAL),
                 ('rect', [8, 5, 14, 6], METAL), ('line', [8, 5, 14, 5], METAL_L), ('px', [(14, 4), (4, 4)], METAL_D),
                 ('line', [7, 10, 8, 11], METAL_D)],
    'bolt_cutters': [('line', [2, 14, 7, 8], RED, 2), ('line', [5, 15, 9, 10], RED, 2),
                     ('line', [7, 8, 12, 2], METAL, 2), ('line', [9, 10, 14, 4], METAL, 2),
                     ('px', [(8, 9)], METAL_D), ('line', [12, 2, 14, 4], METAL_L)],
    'screwdriver': [('poly', [(1, 12), (4, 9), (7, 12), (4, 15)], GOLD), ('line', [2, 12, 4, 10], GOLD_L),
                    ('line', [6, 10, 13, 3], METAL, 1), ('line', [5, 10, 12, 3], METAL_L, 1), ('px', [(14, 2)], METAL_D)],
    'crowbar': [('line', [3, 14, 11, 4], RED_D, 2), ('line', [11, 4, 12, 2], RED_D, 2), ('line', [12, 2, 14, 3], RED_D, 2),
                ('line', [3, 14, 1, 13], RED_D, 2), ('line', [4, 12, 10, 4], RED, 1)],
    'wrench': [('line', [3, 13, 10, 6], METAL, 2), ('line', [3, 12, 9, 6], METAL_L), ('ellipse', [8, 1, 14, 7], METAL),
               ('poly', [(11, 1), (14, 1), (14, 4)], (0, 0, 0, 0)), ('ellipse', [1, 11, 5, 15], METAL)],
    'lockpick': [('line', [2, 13, 12, 3], METAL_L, 1), ('line', [12, 3, 13, 4], METAL_L), ('line', [12, 2, 13, 2], METAL_L),
                 ('line', [3, 9, 10, 9], METAL_D, 1), ('line', [10, 9, 10, 6], METAL_D), ('rect', [1, 12, 3, 14], WOOD)],
    'hammer': [('line', [4, 14, 9, 7], WOOD, 2), ('line', [4, 13, 8, 8], WOOD_L),
               ('poly', [(6, 4), (10, 1), (14, 6), (11, 8)], IRON), ('line', [7, 4, 10, 2], METAL)],
    'axe': [('line', [4, 15, 11, 3], WOOD, 2), ('line', [5, 13, 10, 4], WOOD_L),
            ('poly', [(8, 2), (13, 0), (15, 6), (11, 6)], METAL), ('line', [13, 1, 15, 5], METAL_L)],
    'key': [('ring', [1, 1, 7, 7], GOLD, 2), ('line', [6, 6, 13, 13], GOLD, 2), ('line', [11, 13, 12, 12], GOLD_D, 2),
            ('line', [9, 11, 10, 10], GOLD_D, 2), ('px', [(3, 2)], GOLD_L)],
    'iron_key': [('ring', [1, 1, 8, 8], IRON, 2), ('line', [7, 7, 14, 14], IRON, 2), ('rect', [11, 13, 13, 15], IRON_D),
                 ('rect', [8, 11, 10, 13], IRON_D), ('px', [(3, 2)], METAL)],
    'note': [('poly', [(2, 2), (13, 1), (14, 13), (3, 14)], PAPER), ('line', [4, 5, 11, 4], INK), ('line', [4, 7, 12, 7], INK),
             ('line', [4, 10, 9, 10], INK), ('line', [3, 13, 14, 12], PAPER_D)],
    'idol': [('ellipse', [5, 1, 10, 6], GOLD), ('poly', [(4, 6), (11, 6), (12, 13), (3, 13)], GOLD_D),
             ('rect', [3, 13, 12, 14], GOLD_D), ('px', [(6, 3), (9, 3)], '!#ff4020'), ('line', [6, 8, 9, 8], GOLD_L)],
    'amulet': [('line', [3, 1, 7, 7], GOLD_D), ('line', [12, 1, 8, 7], GOLD_D), ('ellipse', [4, 6, 11, 13], GOLD),
               ('ellipse', [6, 8, 9, 11], '!#e02030'), ('px', [(6, 8)], '!#ff9090')],
    'tonic': [('rect', [6, 1, 9, 3], WOOD), ('rect', [6, 3, 9, 5], '#9ab0b8'), ('ellipse', [3, 5, 12, 14], '#9ab0b8'),
              ('ellipse', [4, 8, 11, 14], RED), ('px', [(5, 7), (5, 8)], '#ffffff')],
    'ammo': [('rect', [2, 8, 13, 14], WOOD_D), ('rect', [3, 3, 5, 9], GOLD), ('rect', [7, 2, 9, 9], GOLD), ('rect', [11, 4, 13, 9], GOLD),
             ('px', [(3, 3), (7, 2), (11, 4)], GOLD_L), ('line', [3, 11, 12, 11], WOOD)],
    'dispel': [('ring', [1, 1, 14, 14], '!#60b0ff', 1), ('poly', [(7, 2), (9, 6), (13, 7), (9, 9), (7, 13), (6, 9), (2, 7), (6, 6)], '!#c0e8ff'),
               ('px', [(7, 7)], '!#ffffff')],
    'lantern': [('line', [5, 2, 10, 2], IRON), ('rect', [4, 3, 11, 4], IRON), ('rect', [5, 5, 10, 11], GLOW),
                ('line', [7, 5, 7, 11], IRON_D), ('rect', [4, 12, 11, 13], IRON), ('ellipse', [6, 7, 8, 10], GLOW_W)],
    'flashlight': [('poly', [(2, 12), (9, 5), (11, 7), (4, 14)], IRON), ('line', [3, 12, 9, 6], METAL),
                   ('ellipse', [9, 2, 14, 7], METAL_L), ('ellipse', [10, 3, 13, 6], GLOW_W)],
    'fuel': [('rect', [2, 4, 13, 14], RED), ('line', [3, 5, 12, 13], RED_D), ('line', [3, 13, 12, 5], RED_D),
             ('rect', [4, 1, 9, 3], IRON), ('rect', [11, 2, 12, 4], IRON)],
    'boards': [('poly', [(1, 4), (14, 1), (15, 4), (2, 7)], WOOD), ('poly', [(1, 9), (14, 11), (13, 14), (0, 12)], WOOD_L),
               ('px', [(4, 5), (12, 3), (3, 11), (11, 12)], IRON)],
    'book': [('rect', [2, 2, 13, 14], '#5a1e22'), ('rect', [3, 3, 4, 13], '#3a1214'), ('ring', [6, 5, 11, 10], GOLD),
             ('px', [(8, 7)], '!#ff5030'), ('line', [3, 14, 13, 14], PAPER)],
    'map': [('poly', [(1, 3), (5, 1), (10, 3), (14, 1), (14, 12), (10, 14), (5, 12), (1, 14)], PAPER),
            ('line', [5, 1, 5, 12], PAPER_D), ('line', [10, 3, 10, 14], PAPER_D), ('line', [3, 6, 8, 9], RED), ('px', [(11, 7)], RED)],
    'gear': [('ring', [2, 2, 13, 13], METAL, 3), ('rect', [7, 0, 8, 2], METAL), ('rect', [7, 13, 8, 15], METAL),
             ('rect', [0, 7, 2, 8], METAL), ('rect', [13, 7, 15, 8], METAL)],
    'skull': [('ellipse', [2, 1, 13, 11], PAPER), ('rect', [5, 10, 10, 14], PAPER), ('ellipse', [4, 5, 7, 8], INK),
              ('ellipse', [8, 5, 11, 8], INK), ('px', [(7, 9)], INK), ('line', [6, 12, 9, 12], PAPER_D)],
    'pointer': [('poly', [(0, 0), (7, 4), (0, 8)], GOLD), ('line', [1, 1, 5, 4], GOLD_L)],
    'hand_pointer': [('rect', [0, 4, 7, 9], PAPER), ('rect', [7, 4, 13, 6], PAPER), ('rect', [2, 2, 5, 4], PAPER),
                     ('line', [2, 7, 6, 7], PAPER_D), ('line', [8, 6, 12, 6], PAPER_D)],
}

ICON_SIZE = {'pointer': 9, 'hand_pointer': 14}


def draw_ops(ops, size, outline=OUTLINE):
    """Run draw ops onto an RGBA canvas; returns (rgba float HxWx4, emissive HxW)."""
    w, h = (size, size) if isinstance(size, int) else size
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    em = Image.new('L', (w, h), 0)
    d, de = ImageDraw.Draw(im), ImageDraw.Draw(em)
    for op in ops:
        kind, coords, colour = op[0], op[1], op[2]
        width = op[3] if len(op) > 3 else 1
        glow = isinstance(colour, str) and colour.startswith('!')
        fill = colour.lstrip('!') if isinstance(colour, str) else tuple(colour)
        efill = 255 if glow else 0
        for dd, f in ((d, fill), (de, efill)):
            if kind == 'line':
                dd.line(coords, fill=f, width=width)
            elif kind == 'rect':
                dd.rectangle(coords, fill=f)
            elif kind == 'ellipse':
                dd.ellipse(coords, fill=f)
            elif kind == 'ring':
                dd.ellipse(coords, outline=f, width=width)
            elif kind == 'poly':
                dd.polygon(coords, fill=f)
            elif kind == 'px':
                dd.point(coords, fill=f)
            else:
                raise KeyError(f'unknown draw op {kind}')
    rgba = np.asarray(im, np.float32) / 255
    e = np.asarray(em, np.float32) / 255
    if outline:
        a = rgba[..., 3] > 0.5
        grown = a.copy()
        grown[1:] |= a[:-1]; grown[:-1] |= a[1:]; grown[:, 1:] |= a[:, :-1]; grown[:, :-1] |= a[:, 1:]
        ring = grown & ~a
        oc = np.array([int(outline[i:i + 2], 16) / 255 for i in (1, 3, 5)] + [1.0], np.float32)
        rgba[ring] = oc
    rgba[..., 3] = (rgba[..., 3] > 0.5).astype(np.float32)
    return rgba, e


def get_icon(name, defs=None):
    """An icon by name. `defs` may mix a scene's icon_defs (draw ops) with its sprite_defs (pixel
    grids): the GUI passes both, because any sprite can stand in as an icon."""
    defs = defs or {}
    dd = defs.get(name)
    if dd is not None and 'ops' in dd:
        return draw_ops(dd['ops'], dd.get('size', 16), dd.get('outline', OUTLINE))
    if dd is None and name in ICONS:
        return draw_ops(ICONS[name], ICON_SIZE.get(name, 16))
    import assets
    return assets.get_sprite(name, defs)    # a sprite_defs pixel grid, a built-in sprite, or a PNG


# ------------------------------------------------------------------ first-person held items
# Canvas sizes are in framebuffer pixels (320x200 screen). 'anchor' says which bottom corner/centre
# the canvas hugs. 'light' (optional) adds a point light at the camera when the item is shown.

VIEWMODELS = {
    # drawn with the pixel-art toolkit in held.py: a shaded hand round each, out of a coat sleeve
    'revolver': {'size': (84, 78), 'anchor': 'right', 'draw': 'held.vm_revolver'},
    'lantern': {'size': (60, 96), 'anchor': 'left', 'draw': 'held.vm_lantern',
                'light': {'radius': 4.5, 'color': [1.0, 0.72, 0.38], 'intensity': 1.2}},
    'flashlight': {'size': (70, 80), 'anchor': 'right', 'draw': 'held.vm_flashlight', 'flashlight': True},
    'axe': {'size': (90, 96), 'anchor': 'right', 'draw': 'held.vm_axe'},
    'crowbar': {'size': (80, 92), 'anchor': 'right', 'draw': 'held.vm_crowbar'},
    'torch': {'size': (56, 96), 'anchor': 'left', 'draw': 'held.vm_torch',
              'light': {'radius': 5.0, 'color': [1.0, 0.6, 0.25], 'intensity': 1.4}},
}

# the guns of the doomed mode are drawn with the pixel-art toolkit in doomed.py, held in the middle
VIEWMODELS['pistol'] = {'size': (56, 66), 'anchor': 'center', 'draw': 'doomed.vm_pistol',
                        'fire_light': {'radius': 3.5, 'color': [1.0, 0.72, 0.36], 'intensity': 1.6}}
VIEWMODELS['shotgun'] = {'size': (84, 78), 'anchor': 'center', 'draw': 'doomed.vm_shotgun',
                         'fire_light': {'radius': 4.5, 'color': [1.0, 0.72, 0.36], 'intensity': 2.0}}


def get_viewmodel(name, defs=None, fire=False):
    defs = defs or {}
    v = defs.get(name) or VIEWMODELS.get(name)
    if v is None:
        raise KeyError(f"unknown viewmodel item '{name}'. Built-in: {', '.join(VIEWMODELS)}; "
                       f"define new ones under viewmodel_defs")
    if 'draw' in v:                          # drawn by a function: 'module.function'
        module, _, fn = v['draw'].rpartition('.')
        rgba, em = getattr(importlib.import_module(module), fn)(fire=bool(fire))
        return rgba, em, v
    rgba, em = draw_ops(v['ops'], v['size'], v.get('outline', OUTLINE))
    return rgba, em, v

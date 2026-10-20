"""Item icons, menu pointers and first-person held items ("viewmodels"), drawn from short lists of
draw operations and finished with an automatic 1px outline so they read as pixel art.

Draw op format: (kind, coords, colour, [width])
  kind: line | rect | ellipse | ring | poly | px
  colour: '#rrggbb'; prefix with '!' to make those pixels emissive (glow regardless of lighting)
New icons can be defined in a scene under "icon_defs": {"name": {"size": 16, "ops": [...]}}.
"""
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
    'revolver': {'size': (84, 78), 'anchor': 'right', 'ops': [
        ('poly', [(52, 78), (84, 78), (84, 46), (64, 40)], COAT), ('poly', [(66, 78), (84, 78), (84, 56)], COAT_D),
        ('poly', [(30, 78), (60, 78), (63, 54), (54, 46), (36, 50)], SKIN),
        ('poly', [(32, 70), (40, 58), (48, 62), (42, 78)], SKIN_D),
        ('poly', [(38, 49), (52, 46), (50, 36), (41, 37)], WOOD), ('line', [41, 39, 49, 38], WOOD_L),
        ('rect', [36, 26, 54, 38], METAL_D), ('ellipse', [37, 18, 53, 34], METAL), ('ring', [37, 18, 53, 34], METAL_D, 1),
        ('line', [41, 21, 44, 19], METAL_L),
        ('px', [(45, 21), (41, 24), (49, 24), (41, 29), (49, 29), (45, 32)], IRON_D),
        ('px', [(45, 22), (42, 24), (48, 24)], IRON_D),
        ('poly', [(41, 22), (49, 22), (48, 4), (42, 4)], METAL), ('line', [43, 21, 43, 5], METAL_L),
        ('ellipse', [41, 1, 49, 7], IRON), ('ellipse', [43, 2, 47, 6], '#0a0a0c'), ('px', [(45, 0)], METAL_L),
        ('poly', [(34, 54), (38, 42), (44, 43), (42, 56)], SKIN_L),
    ]},
    'lantern': {'size': (60, 96), 'anchor': 'left', 'light': {'radius': 4.5, 'color': [1.0, 0.72, 0.38], 'intensity': 1.2},
                'ops': [
        ('poly', [(0, 96), (24, 96), (30, 70), (10, 62), (0, 66)], COAT), ('poly', [(0, 96), (10, 96), (8, 70), (0, 68)], COAT_D),
        ('line', [23, 56, 23, 44], IRON, 2), ('line', [14, 44, 32, 44], IRON, 2),
        ('poly', [(12, 58), (34, 56), (36, 66), (30, 74), (14, 74), (10, 66)], SKIN),
        ('line', [13, 61, 33, 59], SKIN_D), ('line', [13, 65, 34, 63], SKIN_D), ('line', [14, 69, 33, 68], SKIN_D),
        ('poly', [(28, 55), (36, 54), (37, 60), (31, 61)], SKIN_L),
        ('poly', [(12, 14), (34, 14), (30, 8), (16, 8)], IRON), ('rect', [21, 4, 25, 8], IRON_D),
        ('rect', [13, 15, 33, 37], GLOW), ('ellipse', [18, 20, 28, 34], GLOW_W),
        ('line', [13, 15, 13, 37], IRON_D, 2), ('line', [33, 15, 33, 37], IRON_D, 2), ('line', [23, 15, 23, 37], IRON_D),
        ('rect', [11, 37, 35, 42], IRON), ('line', [12, 38, 34, 38], METAL),
    ]},
    'flashlight': {'size': (70, 80), 'anchor': 'right', 'flashlight': True, 'ops': [
        ('poly', [(40, 80), (70, 80), (70, 50), (52, 46)], COAT), ('poly', [(56, 80), (70, 80), (70, 60)], COAT_D),
        ('poly', [(30, 44), (42, 44), (50, 80), (34, 80)], IRON), ('line', [33, 46, 38, 78], METAL),
        ('poly', [(27, 34), (45, 34), (43, 46), (29, 46)], METAL_D),
        ('ellipse', [26, 26, 46, 40], METAL_L), ('ellipse', [29, 28, 43, 38], GLOW_W),
        ('poly', [(28, 80), (36, 56), (50, 54), (56, 72), (52, 80)], SKIN), ('poly', [(34, 62), (48, 58), (50, 64), (36, 68)], SKIN_D),
        ('line', [36, 60, 48, 57], SKIN_L),
    ]},
    'axe': {'size': (90, 96), 'anchor': 'right', 'ops': [
        ('poly', [(60, 96), (90, 96), (90, 64), (70, 60)], COAT), ('poly', [(74, 96), (90, 96), (90, 76)], COAT_D),
        ('line', [62, 92, 34, 18], WOOD, 6), ('line', [60, 88, 34, 22], WOOD_L, 2),
        ('poly', [(28, 10), (14, 2), (6, 22), (18, 30), (36, 26)], METAL), ('line', [14, 3, 6, 21], METAL_L, 2),
        ('rect', [30, 12, 40, 26], IRON),
        ('poly', [(46, 96), (70, 96), (72, 72), (60, 64), (48, 70)], SKIN), ('poly', [(48, 80), (66, 76), (66, 84), (50, 88)], SKIN_D),
    ]},
    'crowbar': {'size': (80, 92), 'anchor': 'right', 'ops': [
        ('poly', [(52, 92), (80, 92), (80, 62), (62, 58)], COAT), ('poly', [(66, 92), (80, 92), (80, 74)], COAT_D),
        ('line', [56, 90, 30, 14], RED_D, 5), ('line', [54, 86, 30, 18], RED, 2),
        ('line', [30, 14, 26, 6], RED_D, 5), ('line', [26, 6, 16, 6], RED_D, 5), ('line', [16, 6, 14, 12], RED_D, 4),
        ('poly', [(40, 92), (64, 92), (66, 70), (54, 62), (42, 68)], SKIN), ('poly', [(42, 78), (60, 74), (60, 82), (44, 86)], SKIN_D),
    ]},
    'torch': {'size': (56, 96), 'anchor': 'left', 'light': {'radius': 5.0, 'color': [1.0, 0.6, 0.25], 'intensity': 1.4},
              'ops': [
        ('poly', [(0, 96), (26, 96), (32, 72), (10, 64), (0, 68)], COAT),
        ('line', [22, 70, 28, 22], WOOD_D, 6), ('line', [23, 66, 28, 26], WOOD, 2),
        ('poly', [(20, 26), (36, 26), (34, 18), (22, 18)], '#3a2a1a'),
        ('poly', [(18, 20), (28, 0), (40, 20), (34, 12), (29, 22), (24, 10)], '!#ff8a20'),
        ('poly', [(23, 20), (29, 6), (35, 20)], '!#ffd060'), ('poly', [(26, 20), (29, 12), (32, 20)], '!#fff4c0'),
        ('poly', [(12, 62), (34, 60), (36, 70), (30, 80), (14, 80), (10, 70)], SKIN),
        ('line', [13, 65, 33, 63], SKIN_D), ('line', [13, 69, 34, 67], SKIN_D), ('line', [14, 73, 33, 72], SKIN_D),
    ]},
}


# the guns of the doomed mode are drawn with the pixel-art toolkit in doomed.py, held in the middle
VIEWMODELS['pistol'] = {'size': (56, 66), 'anchor': 'center', 'draw': 'vm_pistol',
                        'fire_light': {'radius': 3.5, 'color': [1.0, 0.72, 0.36], 'intensity': 1.6}}
VIEWMODELS['shotgun'] = {'size': (84, 78), 'anchor': 'center', 'draw': 'vm_shotgun',
                         'fire_light': {'radius': 4.5, 'color': [1.0, 0.72, 0.36], 'intensity': 2.0}}


def get_viewmodel(name, defs=None, fire=False):
    defs = defs or {}
    v = defs.get(name) or VIEWMODELS.get(name)
    if v is None:
        raise KeyError(f"unknown viewmodel item '{name}'. Built-in: {', '.join(VIEWMODELS)}; "
                       f"define new ones under viewmodel_defs")
    if 'draw' in v:
        import doomed
        rgba, em = getattr(doomed, v['draw'])(fire=bool(fire))
        return rgba, em, v
    rgba, em = draw_ops(v['ops'], v['size'], v.get('outline', OUTLINE))
    return rgba, em, v

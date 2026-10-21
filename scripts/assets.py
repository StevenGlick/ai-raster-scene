"""The asset library of the ai-raster-scene renderer: every texture, prop, decal, scatter set, fringe
and sky by name, and how to get one.

Every texture is a float32 array (64, 64, 3) in 0..1, tileable.
Some textures carry an emissive mask (64, 64) in 0..1: those texels ignore scene lighting
(lit windows, glowing runes). Sprites are (H, W, 4) RGBA arrays plus an emissive mask.
Everything is deterministic: the same name always produces the same pixels.

The drawing is done elsewhere: the original library in classic.py and each world in a kit
(see KITS below), with the helpers in texlib.py and pixelart.py; the skies in skies.py.
"""
import importlib

import numpy as np
from PIL import Image, ImageDraw

# re-exported: render.py and world.py use some of these as assets.T, assets.fbm
from texlib import T, _rng, col, fbm, grain, shade, vnoise  # noqa: F401

# The tables every kit adds to (classic.py first): see KITS below.
TEXTURES = {}
SPRITES = {}
SPRITE_HEIGHT = {}
PROP_DEFAULTS = {}
NO_CONTACT_SHADOW = set()
DEBRIS_SETS = {}
DECALS = {}
TEXTURE_NOISE = {}
TEXTURE_REFLECT = {}


# ---------------------------------------------------------------- textures

_cache = {}
_alpha = {}


def get_texture(spec):
    """spec: a name from TEXTURES, a path to a PNG, or {"base": name, "tint": [r,g,b], "brightness": f}."""
    key = str(spec)
    if key in _cache:
        return _cache[key]
    em = alpha = None
    if isinstance(spec, dict):
        rgb, em = get_texture(spec['base'])
        alpha = get_alpha(spec['base'])
        rgb = rgb.copy()
        if 'tint' in spec:
            rgb = rgb * np.array(spec['tint'], dtype=np.float32)[None, None, :]
        rgb = np.clip(rgb * spec.get('brightness', 1.0), 0, 1)
    elif isinstance(spec, str) and spec.lower().endswith('.png'):
        rgba = np.asarray(Image.open(spec).convert('RGBA').resize((T, T), Image.NEAREST), np.float32) / 255
        rgb = rgba[..., :3]
        if (rgba[..., 3] < 0.5).any():   # a PNG with transparent pixels is a see-through wall
            alpha = (rgba[..., 3] >= 0.5).astype(np.float32)
    else:
        if spec not in TEXTURES:
            raise KeyError(f"unknown texture '{spec}'. Known: {', '.join(sorted(TEXTURES))}")
        res = TEXTURES[spec](spec)
        rgb, em = res[0], res[1]
        alpha = res[2] if len(res) > 2 else None
    out = (np.clip(rgb, 0, 1).astype(np.float32), None if em is None else em.astype(np.float32))
    _cache[key] = out
    _alpha[key] = alpha
    return out


def get_alpha(spec):
    """See-through mask for a texture (64x64, 1 = solid, 0 = hole), or None if it is solid."""
    get_texture(spec)
    return _alpha.get(str(spec))


# ---------------------------------------------------------------- debris and scatter

# Size classes multiply a prop's default height. Real ground litter is mostly small with the
# occasional big piece, so the default weighting leans heavily toward the lower classes.
# Classes are centred on each prop's default height, which is already tuned to read at 320x200.
# The spread stays modest on purpose: `scale` is a *height*, so a wide prop like `log` (48x14)
# grows sideways much faster than it grows tall, and a big multiplier turns debris into scenery.
# The low end has to stay visible too - `rocks` defaults to 0.22, so 0.3x of that is invisible.
SIZE_CLASSES = {'tiny': 0.6, 'small': 0.8, 'medium': 1.0, 'large': 1.3, 'huge': 1.7}
SIZE_WEIGHTS = {'tiny': 5, 'small': 4, 'medium': 2.5, 'large': 1, 'huge': 0.3}


# What `grime` stamps on surfaces when it is turned up.
GRIME_WALL_DECALS = ['stain', 'stain_rust', 'splatter_dark', 'leak', 'crack', 'moss_patch']
GRIME_FLOOR_DECALS = ['stain', 'stain_rust', 'splatter_dark', 'crack', 'puddle_dark', 'scorch']


def debris_items(spec):
    """Resolve a scatter `of` field to a list of sprite names (repeats act as weights)."""
    if isinstance(spec, str):
        if spec in DEBRIS_SETS:
            return list(DEBRIS_SETS[spec])
        return [spec]
    out = []
    for item in spec:
        out.extend(debris_items(item))
    return out


def sprite_aspect(name, defs=None):
    """Width / height of a prop, so callers can work out its world footprint from its scale."""
    rgba, _ = get_sprite(name, defs)
    h, w = rgba.shape[:2]
    return w / max(h, 1)


def size_scale(name, size_class, defs=None):
    """Absolute world height for a prop drawn at one of the named size classes.

    A scene's own sprite_defs carry their `height`, so scattered custom debris keeps the size
    its author gave it rather than falling back to one world unit.
    """
    base = sprite_defaults(name, defs).get('scale', SPRITE_HEIGHT.get(name, 1.0))
    return base * SIZE_CLASSES.get(size_class, 1.0)


_scache = {}


def _hex_rgba(h):
    h = h.lstrip('#')
    v = [int(h[i:i + 2], 16) / 255 for i in range(0, len(h), 2)]
    return v + [1.0] * (4 - len(v))


def sprite_from_pixels(defn):
    """Text-grid pixel art -> (rgba float HxWx4, emissive HxW). See characters.py for the format."""
    rows = defn['pixels']
    if defn.get('mirror'):
        rows = [r + r[::-1] for r in rows]
    w = max(len(r) for r in rows)
    h = len(rows)
    pal = {k: _hex_rgba(v) for k, v in defn['palette'].items()}
    glow = set(defn.get('emissive', ''))
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in '. ':
                continue
            if ch not in pal:
                raise KeyError(f"pixel char '{ch}' (row {y}) missing from palette")
            rgba[y, x] = pal[ch]
            if ch in glow:
                em[y, x] = 1.0
    return rgba, em


def sprite_defaults(spec, defs=None):
    """Default placement fields (height, opacity, aura...) for a sprite name."""
    from characters import CHARACTERS
    d = (defs or {}).get(spec) or CHARACTERS.get(spec) if isinstance(spec, str) else None
    out = {}
    if d:
        if 'height' in d:
            out['scale'] = d['height']
        out.update(d.get('defaults', {}))
    elif isinstance(spec, str) and spec in SPRITE_HEIGHT:
        out['scale'] = SPRITE_HEIGHT[spec]
        out.update(PROP_DEFAULTS.get(spec, {}))
    return out


def get_sprite(spec, defs=None, view='front'):
    """spec: built-in prop name, character name, a name defined in the scene's sprite_defs, or a PNG path.

    `view` 'back' gives the character from behind when its definition has a `back` grid (every
    built-in character does); anything without one looks the same from both sides.
    """
    from characters import CHARACTERS
    defs = defs or {}
    if view == 'back':
        d = defs.get(spec) if spec in defs else CHARACTERS.get(spec)
        if d and d.get('back'):
            key = 'back:' + (json_key(d) if spec in defs else spec)
            if key not in _scache:
                _scache[key] = sprite_from_pixels(dict(d, pixels=d['back']))
            return _scache[key]
    if spec in defs:
        key = 'def:' + json_key(defs[spec])
        if key not in _scache:
            _scache[key] = sprite_from_pixels(defs[spec])
        return _scache[key]
    if spec in _scache:
        return _scache[spec]
    if isinstance(spec, str) and spec.startswith('facade:'):
        import buildings                  # one layer of one building's front (see buildings.py)
        _scache[spec] = buildings.layer_image(spec)
        return _scache[spec]
    if spec in CHARACTERS:
        out = sprite_from_pixels(CHARACTERS[spec])
    elif spec.lower().endswith('.png'):
        im = Image.open(spec).convert('RGBA')
        rgba = np.asarray(im, dtype=np.float32) / 255
        out = (rgba, np.zeros(rgba.shape[:2], np.float32))
    else:
        if spec not in SPRITES:
            known = sorted(SPRITES) + sorted(CHARACTERS)
            raise KeyError(f"unknown sprite '{spec}'. Known: {', '.join(known)}")
        out = SPRITES[spec]()
    _scache[spec] = out
    return out


def json_key(obj):
    import json
    return json.dumps(obj, sort_keys=True)


# ---------------------------------------------------------------- per-material variation


# How mirror-like a puddle decal makes the floor under it (floors take theirs from
# TEXTURE_REFLECT, or a cell's own "reflect").
DECAL_REFLECT = {'puddle': 0.35, 'puddle_shine': 0.55, 'puddle_dark': 0.25}


def texture_reflect(spec):
    """Default reflectivity of a floor texture (0 = matte)."""
    return float(TEXTURE_REFLECT.get(texture_key(spec), 0.0))


def texture_key(spec):
    """The name a texture spec is keyed by: a built-in name, a PNG path, or a variant's base."""
    if isinstance(spec, dict):
        return spec.get('base') or spec.get('path') or ''
    return spec if isinstance(spec, str) else ''


def texture_noise(spec):
    """Relative surface-noise multiplier for a texture spec. Unknown materials get 1.0."""
    return float(TEXTURE_NOISE.get(texture_key(spec), 1.0))


# ---------------------------------------------------------------- the kits
# Each kit module draws a world's textures, props, scatter sets, decals and fringes (the newer ones with
# the pixel-art toolkit, scripts/pixelart.py) and lists them in tables named like the ones above. They are merged
# in this order, so a later kit's version of a name replaces an earlier one. A new kit: write the
# module, add it here.
KITS = (
    'classic',     # the original library: walls, floors, lamps, furniture, sci-fi, dream, the study, decals
    'biomes',      # jungle, ruins and beach; animals; the `jungle` fringe
    'forest',      # the temperate forest: spruce, oak, birch, bushes, the forest floor, the `forest` fringe
    'scifi',       # sci-fi hardware: hangar decks, conduits, screen walls, a shuttle, a power loader
    'dream',       # dream things: a marble chess set, a melting clock, an hourglass, floating stairs
    'basics',      # everyday things, redrawn: grass, hedge, dirt, gravel, panelling, water, barrels, crates
    'village',     # the countryside: a scarecrow, pumpkins, hay bales, crows
    'desert',      # sandstone, slot canyons, a cliff dwelling; saguaro, prickly pear, tumbleweed
    'swamp',       # black water, bog, cypresses hung with moss, a heron, an alligator, the `swamp` fringe
    'sea',         # under the sea: the kelp forest's floor, kelp, fish, bubbles, a wreck, the `kelp` fringe
    'haunted',     # the haunted house: cobwebs, a candelabra, a portrait, a grandfather clock, bats
    'moon',        # the Moon: regolith, rover tracks, a greenhouse dome, a rover, a habitat module
    'aquarium',    # the aquarium: sharks, a manta, a turtle, reef fish, corals, jellies, rockwork
    'market',      # the night market: a food cart, stalls, lanterns, a neon sign, a scooter, a crowd
    'bar',         # the neon bar: an arcade cabinet, the counter, a booth, a jukebox, the back bar
    'rooftop',     # the rooftops: a water tower, air conditioners, a giant sign, an elevated train, a cat
    'doomed',      # a 1993 shooter's base (doomed.py also draws the status bar and guns for the GUI)
    'vector',      # Vector World: lines of light on black (its shapes are wireframes, wires.py)
    'saltflat',    # the salt flat: the crust, the crust under water, salt bricks, salt mounds and heaps
    'skyisles',    # sky islands: meadows, layered rock, waterfalls, roots, rope rails
    'glowjungle',  # the jungle at night, lit from inside, and the `glow_jungle` fringe
    'icepalace',   # a palace of ice - and the aurora, which make_sky draws with icepalace.draw_aurora
    'clockwork',   # the clockwork city: brass, copper pipes, clock faces, great gears
    'saloon',      # a frontier saloon inside: wallpaper and wainscot, the back bar, a piano, a card table
    'mine',        # a gold mine: rock with veins of quartz and gold, a pick and shovel, dynamite, ore
    'temple',      # inside the jungle temple: a golden idol, treasure
)
FRINGES = {}
for _name in KITS:
    _kit = importlib.import_module(_name)
    TEXTURES.update(getattr(_kit, 'TEXTURES', {}))
    TEXTURE_REFLECT.update(getattr(_kit, 'TEXTURE_REFLECT', {}))
    TEXTURE_NOISE.update(getattr(_kit, 'TEXTURE_NOISE', {}))
    SPRITES.update(getattr(_kit, 'SPRITES', {}))
    SPRITE_HEIGHT.update(getattr(_kit, 'SPRITE_HEIGHT', {}))
    PROP_DEFAULTS.update(getattr(_kit, 'PROP_DEFAULTS', {}))
    NO_CONTACT_SHADOW |= getattr(_kit, 'NO_CONTACT_SHADOW', set())
    DEBRIS_SETS.update(getattr(_kit, 'DEBRIS_SETS', {}))
    DECALS.update(getattr(_kit, 'DECALS', {}))
    FRINGES.update(getattr(_kit, 'FRINGES', {}))

_dcache = {}


def get_decal(spec, defs=None):
    """spec: a built-in decal name, a name in the scene's decal_defs, or a PNG path (RGBA)."""
    defs = defs or {}
    if spec in defs:
        key = 'def:' + json_key(defs[spec])
        if key not in _dcache:
            _dcache[key] = sprite_from_pixels(defs[spec])
        return _dcache[key]
    if spec in _dcache:
        return _dcache[spec]
    if isinstance(spec, str) and spec.lower().endswith('.png'):
        im = Image.open(spec).convert('RGBA')
        rgba = np.asarray(im, dtype=np.float32) / 255
        out = (rgba, np.zeros(rgba.shape[:2], np.float32))
    else:
        if spec not in DECALS:
            raise KeyError(f"unknown decal '{spec}'. Known: {', '.join(sorted(DECALS))}")
        out = DECALS[spec]()
    _dcache[spec] = out
    return out


# ---------------------------------------------------------------- skies
# Drawn in skies.py; re-exported here, where the renderer and the docs look for them.
from skies import (SKY_OBJECTS, SKY_PRESETS, SKYLINES, draw_disc, draw_sky_object,  # noqa: E402,F401
                   draw_skyline, make_sky)


def catalog(path):
    """Contact sheet of every texture and sprite with its name, for picking materials."""
    names = sorted(TEXTURES)
    cols = 8
    cw, ch = 96, 110
    rows_t = (len(names) + cols - 1) // cols
    from characters import CHARACTERS
    snames = sorted(SPRITES) + sorted(CHARACTERS)
    rows_s = (len(snames) + cols - 1) // cols
    dnames = sorted(DECALS)
    rows_d = (len(dnames) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cw, (rows_t + rows_s + rows_d) * ch + 30), (20, 20, 24))
    d = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        rgb, _ = get_texture(n)
        a = get_alpha(n)
        if a is not None:   # see-through: show the holes against a checkerboard
            chk = np.where(((np.arange(T)[:, None] // 8 + np.arange(T)[None, :] // 8) % 2)[..., None] == 0, 0.35, 0.55)
            rgb = rgb * a[..., None] + chk * (1 - a[..., None])
        tile = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).resize((88, 88), Image.NEAREST)
        x, y = (i % cols) * cw + 4, (i // cols) * ch + 4
        sheet.paste(tile, (x, y))
        d.text((x, y + 90), n[:15], fill=(220, 220, 220))
    oy = rows_t * ch + 20
    for i, n in enumerate(snames):
        rgba, _ = get_sprite(n)
        hgt, wid = rgba.shape[:2]
        k = min(88 / hgt, 88 / wid)
        im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').resize((max(1, int(wid * k)), max(1, int(hgt * k))), Image.NEAREST)
        x, y = (i % cols) * cw + 4, oy + (i // cols) * ch + 4
        bg = Image.new('RGB', (88, 88), (60, 60, 70))
        bg.paste(im, ((88 - im.width) // 2, 88 - im.height), im)
        sheet.paste(bg, (x, y))
        d.text((x, y + 90), n, fill=(220, 220, 220))
    # decals, shown over a mid grey so their alpha reads
    oy = (rows_t + rows_s) * ch + 30
    for i, n in enumerate(dnames):
        rgba, _ = get_decal(n)
        im = Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), 'RGBA').resize((88, 88), Image.NEAREST)
        x, y = (i % cols) * cw + 4, oy + (i // cols) * ch + 4
        bg = Image.new('RGB', (88, 88), (118, 112, 104))
        bg.paste(im, (0, 0), im)
        sheet.paste(bg, (x, y))
        d.text((x, y + 90), n[:15], fill=(220, 220, 220))
    # icons and held items
    import icons
    inames = [n for n in icons.ICONS]
    vnames = list(icons.VIEWMODELS)
    rows_i = (len(inames) + cols * 2 - 1) // (cols * 2)
    extra = rows_i * 60 + 130 + 20
    big = Image.new('RGB', (sheet.width, sheet.height + extra), (20, 20, 24))
    big.paste(sheet, (0, 0))
    d = ImageDraw.Draw(big)
    oy = sheet.height + 10
    for i, n in enumerate(inames):
        rgba, _ = icons.get_icon(n)
        im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')
        im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        x, y = (i % (cols * 2)) * 48 + 8, oy + (i // (cols * 2)) * 60
        big.paste(im, (x + (32 - im.width) // 2, y), im)
        d.text((x - 2, y + 36), n[:8], fill=(200, 200, 200))
    oy += rows_i * 60 + 10
    for i, n in enumerate(vnames):
        rgba, _, _ = icons.get_viewmodel(n)
        im = Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')
        x = i * (sheet.width // len(vnames)) + 8
        bg = Image.new('RGB', (sheet.width // len(vnames) - 12, 110), (60, 60, 70))
        k = min(1.0, bg.width / im.width, bg.height / im.height)       # the big ones, shrunk to fit
        if k < 1:
            im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BOX)
        bg.paste(im, ((bg.width - im.width) // 2, 110 - im.height), im)
        big.paste(bg, (x, oy))
        d.text((x, oy + 112), n, fill=(220, 220, 220))
    big.save(path)


if __name__ == '__main__':
    import sys
    catalog(sys.argv[1] if len(sys.argv) > 1 else 'catalog.png')

# Scene format reference

A scene is one JSON file, read as UTF-8. Only `map`, `legend` and `camera` are required.

`render.py` prints `warning: unknown key ...` (with a did-you-mean) for any key it does not read - a misspelt key is otherwise silently ignored, so treat the warning as an error. JSON has no comments: prefix a key with `_` (`"_note": "..."`) to keep a note without a warning. `title`, `description` and `notes` are accepted as metadata and never read.

## Coordinates

- The map is a grid of characters. Row index is **y** (grows downward / south), column index is **x** (grows right / east).
- One cell is one world unit. Cell `(x, y)` spans `x..x+1`, `y..y+1`; its centre is `(x+0.5, y+0.5)`.
- Heights are in the same units. The default eye height is `0.5`, a standard room is `1.0` tall.
- Camera `angle` is in degrees: **0 = east (+x), 90 = south (+y), 180 = west, 270 = north**.

## Top-level keys

| key | default | meaning |
|---|---|---|
| `resolution` | `[320, 200]` | internal framebuffer size. 320x200 is the VGA look; 400x250 for more detail |
| `scale` | `3` | nearest-neighbour upscale of the final PNG |
| `map` | required | list of equal-length strings |
| `legend` | required | char -> cell spec (see below) |
| `default` | `{"floor":"concrete_floor"}` | spec for chars missing from the legend |
| `ceiling_height` | `1.0` | z of every ceiling. Walls in roofed areas should be at least this tall |
| `camera` | required | `{x, y, angle, fov=66, height=0.5, pitch=0, flashlight}` |
| `shots` | none | list of camera dicts; each inherits from `camera`. Renders `out_01.png`, `out_02.png`... |
| `sky` | `"night"` | `night`, `dusk`, `storm`, `day`, `overcast`, `blood`, or `null` for fully indoor |
| `ambient` | `[0.18,0.18,0.22]` | base light RGB. Night exterior ~0.13, dark interior ~0.05 |
| `lights` | `[]` | point lights, see below |
| `fog` | none | `{color:[r,g,b], density:0.05, sky_mix:0.35}`. Exponential by distance |
| `fog_sky` | `true` | whether fog also tints the sky panorama (by `sky_mix`) |
| `sprites` | `[]` | billboards, see below |
| `flashlight` | none | `true` or `{intensity:1.2, radius:0.35, range:5, color}`; per-shot override allowed |
| `light_levels` | `24` | brightness quantisation steps (Doom-style banding). `0` = smooth |
| `scatter` | `[]` | procedural debris: specs expanded into real sprites at load (see Scatter) |
| `grime` | `0` | 0-1 dial for neglect: raises surface noise, scatter density and wear decals |
| `grime_debris`, `grime_decals` | `true` | set either to `false` to keep that part out of `grime` |
| `decals` | `[]` | stamps blended into floors, walls and ceilings (see Decals) |
| `decal_defs` | `{}` | inline decal definitions, same text-grid format as `sprite_defs` |
| `surface_noise` | `0.10` | world-space albedo variation on walls, floors and ceilings, to break up texture tiling. A number (the base swing, scaled per material), or `{"amount", "scale", "by_texture"}`. `0` disables it |
| `palette` | `256` | adaptive palette size, a named palette, a hex list, or `0` for none (see Post-processing) |
| `auto_levels` | `true` | stretch the tonal range before a few-colour palette, so dark scenes keep detail |
| `dither` | `1.0` | ordered (Bayer 4x4) dither strength before quantisation |
| `scanlines` | `false` | shorthand for the `scanlines` post effect |
| `overbright` | `1.0` | global light multiplier |
| `lightmap_res` | `8` | lightmap samples per cell |
| `max_distance` | `64` | ray cut-off |
| `supersample` | `1` | render the 3D pass at Nx and average down. `2` removes most floor/ceiling shimmer; UI stays crisp |
| `sprite_defs` | `{}` | inline pixel-art sprite definitions (see Pixel-art sprites) |
| `overlays` | `[]` | GUI drawn on every shot (see GUI). Shots can add their own |
| `ui` | classic theme | GUI theme and styling |
| `post` | `[]` | post-processing effects and presets (see Post-processing). Shots can add their own |
| `icon_defs`, `viewmodel_defs` | `{}` | custom icons and held items (see GUI) |
| `seed` | `0` | randomness for scatter, grime, grain, rain, snow and VHS. Output is deterministic for a given seed |

A shot may also carry `"overrides": {...}` to change any top-level key (sky, fog, lights...) for that shot only. Besides the camera fields, a shot can set its own `overlays` and `post` (added to the scene's), `extra_sprites` (sprites that appear in that shot only - a figure that has just stepped into the doorway), and `flashlight`, `supersample`, `scanlines` and `seed`.

## Cell specs (legend values)

Open cell:
```json
".": {"floor": "linoleum", "ceil": "acoustic"}   // roofed
",": {"floor": "grass"}                            // no "ceil" -> open to the sky
"~": {"floor": "water", "drop": 0.16}              // surface sits 0.16 below the surrounding floor
```
- `drop` (0 to 0.9) sinks a cell's floor below `z=0`. This is what stops water sitting flush with the bank: the sunken surface is rendered as its own plane, a wall standing in the water carries on down to the surface, and sprites placed in a sunken cell rest on the lower surface (so a `rowboat` floats on the water rather than hovering over it). Keep drops small - 0.1 to 0.25 reads as water, more reads as a pit. Where a sunken cell meets an ordinary *floor* cell, the bank face between them is approximated by a darkened strip rather than modelled.

Wall cell (solid block, `h` units tall):
```json
"#": {"wall": "brick", "h": 1}
"H": {"wall": ["plaster_white", "window_dark", "window_lit", "window_dark"], "h": 4, "top": "concrete"}
```
- `wall` as a **list** stacks textures per storey, bottom to top (index = floor(z)); the last entry repeats for anything taller. This is how you make building facades with a door on the ground floor and varied lit windows above.
- Textures tile once per world unit vertically, so a 4-tall wall with one texture repeats it 4 times.
- `top` is what you see when looking down on a wall shorter than eye height (approximate; keep walls taller than `camera.height` where possible).
- Rays continue past walls, so a tall building behind a low hedge is drawn correctly. A wall stops the ray only when it fills the screen top to bottom.

## Textures

Any texture slot accepts:
- a built-in name (run `python scripts/assets.py catalog.png` to see them all),
- a PNG path (resized to 64x64, nearest). Relative paths are looked up beside the scene file first, then in the working directory - the same goes for PNG sprites, decals and TTF fonts,
- `{"base": "brick", "tint": [0.8, 0.9, 1.1], "brightness": 0.7}` for a recoloured variant.

Built-ins with emissive texels (glow regardless of lighting): `window_lit`, `window_lit_plaster`, `window_teal`, `runes`. Their dark counterparts are `window_dark`, `window_dark_plaster`.

## Lights

```json
{"x": 10.2, "y": 10.0, "z": 1.5, "radius": 4.5, "color": [1.0, 0.82, 0.5], "intensity": 1.1, "shadows": true}
```
- Falloff is `(1 - d/radius)^2 * intensity`, so `radius` is the hard edge of the pool of light. Lanterns 4-6, room lamps 3-4, big sources 6-8.
- Shadows are traced through the grid: walls at least `min(z, 0.95)` tall block the light.
- Light above ~1.4 units fades with height, so tall facades darken toward the top.
- Lights are invisible. Pair each with a sprite (`lamp_post`, `lantern`, `candles`) or an emissive texture so the source reads.

Lighting colour cheat sheet: oil/candle `[1,0.7,0.35]`, incandescent `[1,0.86,0.6]`, moonlight `[0.55,0.65,0.9]`, emergency/cult red `[1,0.15,0.1]`, sickly green `[0.5,1,0.6]`.

## Sprites

```json
{"id": "guard", "x": 11.3, "y": 20.3, "type": "guard", "scale": 0.6, "z": 0, "flip": false}
```
| field | meaning |
|---|---|
| `type` | built-in prop, built-in character, a name from `sprite_defs`, or a PNG path (RGBA) |
| `id` | name used by overlays to anchor a speech bubble |
| `scale` | world height in units (each built-in has a default; people are ~0.56-0.62) |
| `z` | height off the floor (wall lanterns ~0.8) |
| `flip` | mirror horizontally |
| `tint` | RGB multiplier, e.g. `[1.2, 0.8, 0.8]` |
| `fullbright` | ignore scene lighting (glows at full brightness) |
| `opacity` | 0-1. Below 1 the sprite is drawn in the translucent pass |
| `blend` | `"alpha"` (default) or `"additive"` (light-like: flames, spirits, magic) |
| `aura` | `{"color": [r,g,b], "strength": 0.5, "radius": 0.25}` soft additive glow around the silhouette |
| `wobble` | sideways sway in texels, stronger toward the bottom (ghost tails, heat) |
| `light` | `true` or a light dict (`radius`, `color`, `intensity`, `z`): attaches a point light at the sprite |
| `stretch` | horizontal scale factor |

Drawing order: opaque sprites first (they write depth), then translucent/additive ones back to front without writing depth, so ghosts show what is behind them. Built-in lamps, lanterns and candles have emissive flames; place sprites at least ~0.2 from wall faces.

Built-in props (46): barrel, bed, bench, boulder, brazier, buoy, bush, campfire, candles, column, console, crate, dead_tree, fern, flowers, fountain, gravestone, lamp_post, lantern, locker, log, mushrooms, palm, pine, rowboat, signpost, statue, stump, tree, wheelchair, plus the wall-mounted and ground props listed below.
Built-in characters (16x32 pixel art): cultist, scientist, guard, nurse, spiritualist, ghost (translucent with aura and wobble by default), hybrid.

Wall-mounted and hanging props (`sconce`, `painting`, `banner`, `wall_clock`, `pipe_valve`, `ceiling_lamp`, `chandelier`, `ivy_hang`) are ordinary sprites: place them a little off the surface (about 0.2-0.3 from a wall face) and set `z`. Ground clutter (`rocks`, `rubble`, `bones`, `sack`, `bucket`, `broken_barrel`, `grass_tuft`, `reeds`) is sized to read at 320x200; scatter a handful rather than a carpet.

## Decals

Decals are stamps blended into a surface's albedo at render time - puddles, stains, cracks, vines, scorch marks - so you can dirty a surface without authoring a new texture. They cost nothing per frame beyond the pixels they cover and never change the geometry.

```json
"decals": [
  {"tex": "puddle_shine", "surface": "floor",   "x": 16.6, "y": 26.4, "size": 2.2},
  {"tex": "stain",        "surface": "ceiling", "x": 7.5,  "y": 5.5,  "size": 2.0, "opacity": 0.7},
  {"tex": "vines",        "surface": "wall", "cell": [12, 13], "face": "east", "u": 0.5, "z": 3.2, "size": 1.3}
]
```

| field | meaning |
|---|---|
| `tex` | a built-in decal name, a name from `decal_defs` (same text-grid format as `sprite_defs`), or a PNG path with alpha |
| `surface` | `floor` (default), `ceiling`, or `wall` |
| `size` | the decal's **width** in world units; its other dimension follows the image aspect |
| `x`, `y` | centre, for floor and ceiling decals |
| `cell`, `face` | for wall decals: the wall cell `[x, y]` and which of its faces - `north`, `south`, `east`, `west` (the direction the surface looks toward) |
| `u` | 0-1 across that face, measured along **+x** (north/south faces) or **+y** (east/west faces). Default 0.5 |
| `z` | height of the decal's centre above the floor, for wall decals. Default 0.5 |
| `opacity` | 0-1 multiplier on the decal's own alpha. Default 1 |
| `tint`, `flip` | RGB multiplier; mirror horizontally |

Built-in decals: puddle, puddle_dark, puddle_shine, stain, stain_rust, splatter, splatter_dark, vines, moss_patch, crack, scorch, leak, cobweb, rune_mark, drain. `rune_mark` is emissive, so it glows regardless of lighting.

- A floor decal is drawn on the plane of the cell it sits in, so a puddle inside a cell with a `drop` lands on the sunken surface, not the bank above it.
- Dark puddles read as holes punched in a lit floor. Use `puddle_shine` on anything a lamp reaches (wet asphalt, sand, boards) and keep `puddle_dark` for dim interiors.
- Wall decals that hang (`vines`, `leak`, `cobweb`) are drawn from the top of their footprint down, so set `z` near the top of the wall.
- A wall decal is clipped to its own face, so one that overhangs the cell edge ends in a hard vertical cut. Keep `u - size/2` and `u + size/2` inside 0-1, or split a wide stain across two faces.

## Pixel-art sprites

Define new characters, creatures or props as text grids, inline in the scene or in `scripts/characters.py`:

```json
"sprite_defs": {
  "lighthouse_keeper": {
    "height": 0.58,
    "palette": {"k": "#1a1614", "y": "#c8a040", "s": "#d0a07a", "e": "#1a1a1a", "f": "#ffd060", "g": "#b8d0e070"},
    "emissive": "f",
    "defaults": {"light": {"radius": 3, "color": [1, 0.8, 0.5]}},
    "mirror": false,
    "pixels": [
      "....kkkkkkkk....",
      "...kyyyyyyyyk...",
      "..."
    ]
  }
}
```
- One character per pixel. `.` and space are transparent. Every other char must be in `palette`.
- Palette colours are `#rrggbb` or `#rrggbbaa`; the alpha channel makes translucent pixels (ghost wisps, glass).
- `emissive` lists palette chars that glow (eyes, flames, screens).
- `mirror: true` means each row is the left half; it is mirrored to build the right half (symmetric figures in half the typing).
- `defaults` are placement fields applied whenever the sprite is used (opacity, aura, light...).
- 16x32 is the house size for people (about 3x upscaled at conversation distance). Props can be any size; keep rows equal length.
- Shade with 2-3 tones per material (shadow, base, highlight) and a dark outline colour for readability.

## GUI (overlays)

UI is listed in `overlays` (scene-wide) and/or a shot's `overlays`, drawn at native resolution in a hand-drawn pixel font, after world post effects and before palette quantisation. Order matters: later entries draw on top.

The pixel font covers printable ASCII. Curly quotes, dashes, ellipses and no-break spaces are mapped onto it, and accented letters lose their accent (`café` draws as `cafe`); anything else shows as `?`. Text is kept inside the frame: a `title` too wide for its `scale` steps down a size, and bubbles, dialogs, captions, panels, toasts and subtitles wrap. Only `choice` options stay on one line each, so keep them short.

**Placement** (most widgets): `"at"`: `top-left`, `top`, `top-right`, `left`, `center`, `right`, `bottom-left`, `bottom`, `bottom-right`; or explicit `"x"`, `"y"` in framebuffer pixels (negative counts from the right/bottom); `"margin"` (default 6). The framebuffer is 320x200 by default.

**Themes**: `"ui": {"theme": "classic"}` with `classic` (navy and gold), `parchment` (tan paper, brown ink), `terminal` (green on black), `blood` (black and red), `steel` (Windows-95 bevel). Override any colour as RGBA lists: `fill`, `border`, `border_dark`, `text`, `accent`, `dim`, `shadow`, `select`, `select_text`; plus `pad`, `width` (bubble wrap) and `font` (`"pixel"` default, `"pillow"`, or a TTF path with `font_size`). A shot can switch theme through `"overrides": {"ui": {...}}`.

| type | key fields | notes |
|---|---|---|
| `bubble` | `anchor` (sprite id), `text`, `name`, `width`, `offset`, `head` | speech bubble with a tail over a sprite; falls back to top-centre |
| `dialog` | `text`, `name`, `portrait` (sprite or icon), `position` top/bottom, `more` | full-width panel with portrait and continue arrow |
| `caption` | `text`, `x`/`y` or `at`, `box`, `color`, `width` | plain or boxed text: location names, labels |
| `choice` | `options`, `selected`, `prompt`, `pointer` (`arrow`/`hand`/`none`), `width` | menu with highlighted selection; options can be `{"text", "hint", "disabled"}` (hint is right-aligned, e.g. a cost) |
| `title` | `text`, `scale` (2-5), `subtitle`, `color`, `outline`, `band` | big outlined title text: title cards, YOU DIED, chapter names |
| `panel` | `title`, `lines`, `width` | titled list; lines can be `{"text", "done": true/false}` (checkbox) or `{"text", "icon"}` - objectives, notes, stats |
| `toast` | `text`, `icon` | pickup/notification strip ("Found: Bolt Cutters") |
| `prompt` | `key`, `text` | interaction hint `[E] Open`, defaults to lower centre |
| `bars` | `items`: `[{"label","value" 0-1,"color","segments"}]`, `width` | health/stamina/sanity meters |
| `counter` | `value`, `icon`, `label`, `scale` | big HUD number, e.g. ammo `5/18` |
| `hotbar` | `slots`: icon names, `null`, or `{"icon","count"}`; `selected`, `slot` size, `numbers` | quick-slot bar |
| `inventory` | `items` (icons or `{"icon","count","name","description"}`), `columns`, `selected`, `title`, `width` | grid with the selected item's name and description |
| `crosshair` | `style` (`cross`/`dot`/`circle`), `color` | |
| `compass` | `width`, `span` | heading strip from the camera angle (north = map up) |
| `automap` | `mode` (`corner`/`full`), `size`, `cell`, `markers` `[{"x","y","color"}]`, `title` | Doom-style map traced from the scene grid around the camera |
| `image` | `name` (icon or sprite), `scale` | place any icon/sprite on screen |
| `viewmodel` | `item`, `side`, `x_offset`, `y_offset`, `scale`, `brightness`, `light` | first-person held item, lit by the light at the camera, drawn before world post effects |

**Icons** (16x16, used by toast/hotbar/inventory/panel/counter/image): revolver, bolt_cutters, screwdriver, crowbar, wrench, lockpick, hammer, axe, key, iron_key, note, idol, amulet, tonic, ammo, dispel, lantern, flashlight, fuel, boards, book, map, gear, skull, plus pointers `pointer` and `hand_pointer`. Any sprite name also works as an icon.

**Held items** (`viewmodel`): revolver, lantern, flashlight, axe, crowbar, torch. The lantern and torch add a point light at the camera automatically (`"light": false` to disable); the flashlight turns the flashlight cone on unless the shot sets it.

**Custom icons and held items** use draw ops, then get an automatic 1px dark outline:
```json
"icon_defs": {"fuse": {"size": 16, "ops": [
  ["rect", [5, 2, 10, 13], "#c8c0a0"], ["rect", [5, 2, 10, 4], "#8a9098"], ["rect", [5, 11, 10, 13], "#8a9098"],
  ["line", [7, 5, 8, 10], "!#ff6020"]]}},
"viewmodel_defs": {"candle": {"size": [40, 70], "anchor": "left", "light": {"radius": 3, "color": [1, 0.75, 0.4]},
  "ops": [["rect", [14, 20, 24, 60], "#e8e0c8"], ["ellipse", [15, 8, 23, 20], "!#ffd060"]]}}
```
Ops: `line` (with width), `rect`, `ellipse`, `ring` (with width), `poly` (point list), `px` (point list). Colours are `#rrggbb`; prefix `!` for emissive (glows). Icons use a 16x16 canvas with a 1px margin for the outline; held items are drawn in framebuffer pixels and hug the bottom edge.

## Surface variation

Every texture tiles once per world unit, which on a long wall or a big floor reads as obvious
repetition. `surface_noise` multiplies the **albedo** of walls, floors and ceilings by a smooth
world-space noise field - two octaves, one at about 6 world units (varies cell to cell) and one
below half a unit (breaks up the tile itself).

```json
"surface_noise": 0.10                           // base swing, scaled per material
"surface_noise": {"amount": 0.08, "scale": 1.6} // gentler, with larger blotches
"surface_noise": {"amount": 0.10, "by_texture": {"cobble": 0.3, "plaster": 0.07}}
"surface_noise": 0                              // off
```

`amount` is the **typical** brightness swing, not a peak: the two octaves are blended and then
divided by the blend's own average magnitude, so the number really is roughly what a lit surface
moves by on average (peaks are capped at 2.6x). An un-normalised blend of two octaves only
reaches its nominal range at rare extremes and delivers about a third of what it claims.

**There is no single right amount, because it depends on the material.** Flat man-made surfaces
show mottling almost at once, while rough natural ones swallow a great deal before they stop
looking like themselves. So `amount` is a base that each material scales by its own factor from
`assets.TEXTURE_NOISE` - plaster 0.7, cobble 3.0, marble 0.5, rust 2.6, and so on. At the 0.10
default that is about 7% on a plaster wall and 30% on a cobbled street, which is roughly where
each one looks best.

- Override a material with `by_texture`, which takes **absolute** amounts and ignores the
  material's factor. Key it by the built-in name, a PNG path, or the `base` of a tinted variant.
- Raise `amount` as a whole for a grimy, derelict place; drop it for somewhere clean and new.
- Emissive materials (`runes`, `window_lit`) are deliberately damped: mottled light reads as a
  rendering fault rather than as wear.
- A new texture with no entry in `TEXTURE_NOISE` gets a factor of 1.0.
- `scale` multiplies both feature sizes: above 1 gives broader patches, below 1 finer mottling.
- It modulates albedo, not light, so it fades out in darkness (you cannot see surface detail in
  an unlit corner) and survives `light_levels` banding.
- Because it is keyed to world position it stays put as the camera moves, and a long wall varies
  continuously instead of breaking at cell boundaries. This is the opposite of the `grain` post
  effect, which is screen-space and deliberately crawls - the two stack fine.
- Sprites are not affected: they are small, already hand-varied, and look wrong when mottled.

## Scatter

Hand-placing forty rocks is tedious and tends to look placed. `scatter` declares *what* goes
where and lets the loader expand it into ordinary sprites, so scene files stay small and the
result is deterministic for a given seed.

```json
"scatter": [
  {"of": "stones", "on": "s", "density": 1.7, "clump": 1.15,
   "sizes": {"tiny": 7, "small": 4, "medium": 2, "large": 0.7}, "seed": 1},
  {"of": ["rocks", "bones"], "on": ",p", "density": 0.4, "seed": 2}
]
```

| field | meaning |
|---|---|
| `of` | a named set (`stones`, `rubble`, `forest`, `undergrowth`, `shore`, `litter`, `wreckage`), a sprite name, or a list. Repeats inside a set act as weights |
| `on` | legend characters to scatter on, as a string or list. Omit for every open cell |
| `density` | items per eligible cell. 0.3 is a light dusting, 1.5+ is a stony beach |
| `sizes` | size classes to draw from: a list, or a dict of weights. Classes are `tiny`, `small`, `medium`, `large`, `huge`, multiplying the prop's default height |
| `clump` | how hard the noise field biases placement. 0 is uniform, 1-2 gives drifts and clearings |
| `margin` | keep this far from wall faces (default 0.22) |
| `seed` | vary it to reshuffle a layer without touching the others |

- Placement is weighted by the same world-space noise field used for surface variation, then
  jittered with a gaussian inside the chosen cell. Uniform random scatter reads as machine-made:
  evenly spaced, with no bare patches and no drifts.
- Scatter never lands on a camera position or in front of a sprite that has an `id`, and the
  exclusion grows with the item's own footprint - `scale` is a *height*, so a `huge` boulder is
  over a world unit wide and would otherwise fill a frame while still clearing a fixed radius.
- Size classes are centred on each prop's default height rather than scaling up from it. Wide
  props grow sideways faster than they grow tall, and the small end has to stay visible:
  `rocks` defaults to 0.22, so a third of that is invisible at 320x200.
- Scattered props are ordinary sprites once expanded: they light, occlude and fog normally, and
  show up in `--map`. Several hundred of them costs a few hundred milliseconds a frame.

## Grime

`grime` is one 0-1 dial for how neglected somewhere is, because dirt is never just one thing:

```json
"grime": 0.35
```

- multiplies `surface_noise` (by up to 2.5x at `grime: 1`), so worn surfaces mottle more;
- multiplies every `scatter` density (by up to 3x) and adds a light wreckage layer of its own;
- stamps wear decals on wall faces that face an open cell, and stains on floors.

Set `"grime_debris": false` or `"grime_decals": false` to keep one of those out of it. Use it
for a derelict sublevel or a damp cellar; leave it at 0 for somewhere clean and maintained.

## Post-processing

`"post"` (scene-wide) and a shot's `"post"` list effects, applied in order within three stages: **world** effects work on the lit frame before the GUI; the **palette** step quantises; **display** effects run on the upscaled image after the GUI (so they distort the UI too, like a real monitor). Entries are preset names, effect names with defaults, or dicts:

```json
"post": ["storm", {"fx": "lightning", "x": 0.7}, {"fx": "grade", "contrast": 1.2}, "crt"]
```

Presets: `crt`, `crt_amber`, `crt_green`, `vhs`, `gameboy`, `cga`, `ega`, `nightvision`, `cinematic`, `horror`, `old_photo`, `dream`, `bloodmoon`, `storm`, `blizzard`, `hurt`.

| effect | stage | parameters (defaults) |
|---|---|---|
| `grade` | world | `exposure` 1, `brightness` 0, `contrast` 1, `saturation` 1, `gamma` 1, `tint` [r,g,b], `lift` [r,g,b] |
| `bloom` | world | `threshold` 0.65, `strength` 0.6, `radius` 6, `color` |
| `vignette` | world | `strength` 0.5, `radius` 0.7, `color` |
| `grain` | world | `amount` 0.06, `color` false |
| `rain` | world | `density` 1, `length` 7, `angle` 12, `opacity` 0.35, `color` |
| `snow` | world | `count` 260, `opacity` 0.85, `color` |
| `lightning` | world | `amount` 0.45, `bolt` true, `x` (0-1 screen position), `y_end` 0.42 |
| `letterbox` | world | `height` 0.11, `color` |
| `hurt` | world | red damage vignette: `strength` 0.75 |
| `fade` | world | `amount` 0.5, `color` (dim the world behind a menu) |
| `pixelate` | world | `factor` 2 |
| `posterize` | world | `levels` 6 |
| `gradient_map` | world | `colors` list (shadows to highlights), `amount` 1 |
| `palette` | palette | `name` or `colors` (hex list), `auto_levels` true |
| `crt` | display | `curvature` 0.07, `scanline` 0.3, `mask` 0.18, `glow` 0.35, `vignette` 0.3 |
| `vhs` | display | `bleed` 4, `tracking` 0.85, `label` "PLAY", `timestamp` |
| `chromatic` | display | `offset` 2 |
| `scanlines` | display | `strength` 0.28 |

Palettes: `gameboy`, `cga`, `cga_warm`, `ega`, `amber`, `phosphor`, `sepia`, `mono`, `bone` (ramp palettes map by brightness), an integer for an adaptive palette (default 256), or a list of hex colours. Few-colour palettes stretch the frame's tonal range first (`auto_levels`) so dark scenes keep detail. `seed` (scene or shot) changes the random pattern of grain, rain, snow and VHS noise.

## Known limits (it is a 2.5D raycaster)

- No stairs, slopes, cliffs or general multi-level floors. A cell's floor can be sunk below z=0 with `drop` (for water and shallow pits) and that is the only floor-height variation; walls standing in it extend down to its surface, but the bank between two floor cells is approximated, so keep drops shallow. Fake real elevation by making the low area's surroundings tall walls (a cliff face) and placing the camera accordingly.
- One ceiling height per scene.
- Walls are whole grid cells; no thin walls, diagonal walls, arches or doors in the middle of a cell.
- Water and floors are flat textures; no reflections.
- Sprites are static billboards that always face the camera (one view per character, no animation).

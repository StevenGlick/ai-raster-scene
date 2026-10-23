# Scene format reference

A scene is one JSON file, read as UTF-8. Only `map`, `legend` and `camera` are required. The built-in textures, props and characters are listed in `assets.md`, beside this file.

`render.py` prints `warning: unknown key ...` (with a did-you-mean) for any key it does not read - a misspelt key is otherwise silently ignored, so treat the warning as an error. JSON has no comments: prefix a key with `_` (`"_note": "..."`) to keep a note without a warning. `title`, `description` and `notes` are accepted as metadata and never read.

## Coordinates

- The map is a grid of characters. Row index is **y** (grows downward / south), column index is **x** (grows right / east).
- One cell is one world unit. Cell `(x, y)` spans `x..x+1`, `y..y+1`; its centre is `(x+0.5, y+0.5)`.
- Heights are in the same units. The default eye height is `0.5`, a standard room is `1.0` tall, and people are about `0.6` (so a waist-high rail is about 0.35).
- At **landscape scale** the same units stand for far more: a cell is about 100 m, so the eye at 0.5 is fifty metres up and a giant monster 0.62 tall stands in a city as a person stands in a room (see Landscape scale).
- Camera `angle` is in degrees: **0 = east (+x), 90 = south (+y), 180 = west, 270 = north**. Sun and moon `azimuth` use the same compass.
- Rather than working out an angle, aim with `look_at`: a sprite `id`, `[x, y]`, or `[x, y, z]`. The last also sets `pitch` so that height sits mid-frame. Working out atan2 in your head is easy to get wrong by tens of degrees, so prefer `look_at`. A shot that sets its own `angle` (and no `look_at`) is aimed by that angle, not by a `look_at` it would otherwise inherit from `camera`.

## Top-level keys

| key | default | meaning |
|---|---|---|
| `resolution` | `[320, 200]` | internal framebuffer size. 320x200 is the VGA look; 400x250 for more detail |
| `scale` | `3` | nearest-neighbour upscale of the final PNG |
| `map` | required | list of equal-length strings - or, for a road, a `road` (see Road scenes) |
| `legend` | required | char -> cell spec (see below) |
| `road` | none | a road scene: the road of an arcade racer instead of a map - its run of bends and rises, its surface, lanes and kerbs, the ground either side (see Road scenes) |
| `roadside` | `[]` | rows of props along a road, by spacing or by density (see Road scenes) |
| `default` | `{"floor":"concrete_floor"}` | spec for chars missing from the legend |
| `ceiling_height` | `1.0` | z of every ceiling. Walls round a roofed room should be exactly this tall: a taller wall is drawn its full height, over the ceiling (give the outside of a building or a hill cells of their own) |
| `camera` | required | `{x, y, angle or look_at, fov=66, height=0.5, pitch=0, flashlight}` |
| `shots` | none | list of camera dicts; each inherits from `camera`. Renders `out_01.png`, `out_02.png`... |
| `sky` | `"night"` | `night`, `dawn`, `golden`, `sunset`, `dusk`, `storm`, `day`, `overcast`, `blood`, `space`, `alien`, `dream`, `vector` (black to violet with a magenta glow at the horizon, for Vector World), `aurora` (a clear arctic night with the aurora across it, no two stretches alike: a great curtain of green rays low in the north, of every width and height, violet at their tips and fringed pink where it burns brightest, a pleated teal ribbon above it, red-tipped rays to the west and a faint arc high over them all; brightest due north, glowing so a light bloom takes them up and ice or still water doubles them), or `null` for fully indoor |
| `skyline` | none | distant silhouettes on the horizon: `mountains`, `hills`, `treeline`, `city` (see Sky and skyline) |
| `sky_objects` | `[]` | planets, ringed planets, moons, suns and stranger things painted into the sky (see Sky objects) |
| `wireframes` | `[]` | low-poly meshes drawn as lines of light in true 3D: cubes, polyhedra, mountains, racers (see Wireframes) |
| `ambient` | `[0.18,0.18,0.22]` | base light RGB. Night exterior ~0.13, dark interior ~0.05 |
| `lights` | `[]` | point lights, plus `sun` and `moon` directional lights (see Lights) |
| `time` | none | the time of day: `dawn`, `morning`, `noon`, `afternoon`, `golden`, `sunset`, `dusk`, `night` or an hour (17.5): sets the sky, the sun or moon, the ambient light, the air (see Time of day) |
| `heights` | none | a digit layer over the map setting wall heights, for steps, daises and altars (see Heights) |
| `height_unit` | `0.1` | what one step of `heights` is worth |
| `reflections` | `true` | mirror-like floors: `false` turns them off, a number scales them, `{"amount", "ripple"}` tunes them (see Reflections) |
| `contact_shadows` | `0.55` | strength of the soft shadow under every prop standing on the floor; `0` or `false` turns them off |
| `fog` | none | `{color:[r,g,b], density:0.05, sky_mix:0.35}`, exponential by distance; add `ground`, `height`, `noise`, `glow` or `shafts` for volumetric fog: mist lying low, drifting banks, halos round lamps, beams of sun and moonlight (see Fog) |
| `fog_sky` | `true` | whether fog also tints the sky panorama (by `sky_mix`) |
| `wet` | `0` | 0-1: rain-soaked ground. Open floors under the sky darken and turn mirror-like; roofed and void cells stay dry |
| `sprites` | `[]` | billboards, see below |
| `flashlight` | none | `true` or `{intensity:1.2, radius:0.35, range:5, color}`; per-shot override allowed |
| `light_levels` | `24` | brightness quantisation steps (Doom-style banding). `0` = smooth |
| `scatter` | `[]` | procedural debris: specs expanded into real sprites at load (see Scatter) |
| `prefabs` | `[]` | named groups placed with one line each - sprites, lights, decals, scatter and patches of map (see Prefabs) |
| `prefab_defs` | `{}` | the scene's own prefabs, in the same form as the built-ins |
| `objects` | `[]` | things too big for a billboard, built in 3D out of flat panels - a car, a noodle stand (see Objects) |
| `grime` | `0` | 0-1 dial for neglect: raises surface noise, scatter density and wear decals |
| `grime_debris`, `grime_decals` | `true` | set either to `false` to keep that part out of `grime` |
| `decals` | `[]` | stamps blended into floors, walls and ceilings (see Decals) |
| `decal_defs` | `{}` | inline decal definitions, same text-grid format as `sprite_defs` - or `text` for lettering |
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
| `variants` | `true` | the decoration randomizer: every prop drawn a few ways (see a sprite's `variant`) shows one of them, picked by where it stands. `false` draws each the one way |
| `overlays` | `[]` | GUI drawn on every shot (see GUI). Shots can add their own |
| `ui` | classic theme | GUI theme and styling |
| `post` | `[]` | post-processing effects and presets (see Post-processing). Shots can add their own |
| `icon_defs`, `viewmodel_defs` | `{}` | custom icons and held items (see GUI) |
| `seed` | `0` | randomness for scatter, grime, grain, rain, snow and VHS. Output is deterministic for a given seed |

A shot may also carry `"overrides": {...}` to change any top-level key (sky, fog, lights...) for that shot only, and a `time` of day of its own (see Time of day). Besides the camera fields, a shot can set its own `overlays` and `post` (added to the scene's), `extra_sprites` (sprites that appear in that shot only - a figure that has just stepped into the doorway), `extra_wireframes` (the same for wireframes), and `flashlight`, `supersample`, `scanlines` and `seed`.

## Cell specs (legend values)

Open cell:
```json
".": {"floor": "linoleum", "ceil": "acoustic"}   // roofed
",": {"floor": "grass"}                            // no "ceil" -> open to the sky
"~": {"floor": "water", "drop": 0.16}              // surface sits 0.16 below the surrounding floor
"=": {"floor": "asphalt", "reflect": 0.3}          // wet street: mirrors what stands on it
```
- `reflect` (0-1) makes a floor mirror-like (see Reflections). `water` (0.5), `swamp_water` (0.42), `ice` (0.38), `obsidian` (0.45) and `grid_floor` (0.3) reflect by default; set `"reflect": 0` to stop them.
- `"floor": "void"` means no ground at all (see Void floors): the sky carries on below the horizon, so the cell is open air, deep space or the drop off the edge of a floating island.
- `glazed: true` on a roofed cell keeps its `ceil` but lets the sun and moon shine through it, as through glass - or, under a `water_surface` roof, the light coming down into the sea. Glaze a few cells of a roof and the sun comes down through them in beams (with volumetric fog), with no hole in the ceiling to show for it. Rain still stops at it.
- `side` is the texture of a cell's edge where it drops away: the bank under the waterline beside a `drop`, or the cliff under an island beside a void. Without it the cell's floor texture is used.
- `drop` (0 to 0.9) sinks a cell's floor below `z=0`. This is what stops water sitting flush with the bank: the sunken surface is rendered as its own plane, a wall standing in the water carries on down to the surface, and sprites placed in a sunken cell rest on the lower surface (so a `rowboat` floats on the water rather than hovering over it). Keep drops small - 0.1 to 0.25 reads as water, more reads as a pit. Where a sunken cell meets an ordinary *floor* cell, the bank face between them is approximated by a darkened strip rather than modelled.

Wall cell (solid block, `h` units tall):
```json
"#": {"wall": "brick", "h": 1}
"H": {"wall": ["plaster_white", "window_dark", "window_lit", "window_dark"], "h": 4, "top": "concrete"}
```
- `wall` as a **list** stacks textures per storey, bottom to top (index = floor(z)); the last entry repeats for anything taller. This is how you make building facades with a door on the ground floor and varied lit windows above.
- Textures tile once per world unit vertically, from the floor up, so a 4-tall wall with one texture repeats it 4 times and a 0.3-tall step shows the bottom 30% of its texture.
- `top` is the texture on the block's upper surface. A block lower than the eye shows it as a real surface you look down onto: a step, a dais, an altar, a table-high ledge (see Heights).
- A wall cell can also take `ceil`: under a roof, a block lower than the ceiling leaves the ceiling above it in view. Without one it borrows the roof of the room around it, so this is rarely needed.
- Rays continue past walls, so a tall building behind a low hedge is drawn correctly. A wall stops the ray only when it fills the screen top to bottom.

- `fringe` on a wall cell stands layered foliage cards in front of every face of it that looks onto open ground (see Fringe below).
- `facade` on a wall cell turns every face of it onto open ground into a street of separate buildings, each in layers with real windows (see Facades below).

### Fringe: layered edges

A solid wall of `jungle_leaves` or `foliage` is a flat green face. Give the wall cells a `fringe` and every face of them that looks onto open ground gets a few long cards of plants standing in front of it - four in each built-in set, from a dense wall of trees just off the wall to a scatter of bushes at the front - spread over the cell in front. The cards are planar sprites (see Planar sprites), so as the camera moves the layers slide past each other and the edge of the forest has depth.

```json
"J": {"wall": "jungle_leaves", "h": 3.0, "top": "canopy_top", "fringe": "jungle"}
"K": {"wall": "jungle_leaves", "h": 3.0, "fringe": {"set": "jungle", "depth": 1.5, "height": 1.2, "seed": 2}}
"F": {"wall": "foliage", "h": 2.4, "fringe": "forest"}
"Y": {"wall": "swamp_deep", "h": 2.6, "fringe": {"set": "swamp", "depth": 3.0, "wander": 0.35}}
```
| field | default | meaning |
|---|---|---|
| `set` | - | a fringe set: `jungle` (cards `jungle_card_4` .. `jungle_card_1`, back to front: rainforest trees, palms, tree ferns, bushes), `glow_jungle` (the same at night with light in its leaves: `glow_jungle_card_4` .. `glow_jungle_card_1`) `forest` (`forest_card_4` .. `forest_card_1`: spruce, oak and birch, then young trees, then bushes, ferns and grass) `forest_autumn` (`autumn_card_4` .. `autumn_card_1`: the same wood in October - oak, birch and bush turned orange, gold and rust, the spruce among them still green), `forest_snow` (`winter_card_4` .. `winter_card_1`: the wood in winter - snowy spruce, bare oak and birch with snow along their limbs, bushes buried in it), `swamp` (`swamp_card_4` .. `swamp_card_1`: a dense stand of tall bald cypresses hung with moss, then a looser one, then young ones among cattails, then cattails and knees at the water's edge) or `kelp` (`kelp_card_2`, `kelp_card_1`: a dense stand of giant kelp, then a few stalks) |
| `cards` | - | instead of a set: your own sprite names, back to front (a PNG or a `sprite_defs` card works) |
| `depth` | `1.0` | how far out from the wall the layers spread, in cells |
| `height` | `1.0` | a multiplier on the cards' heights |
| `seed` | `0` | reshuffles where along its card each run starts |
| `wander` | `0` | lay the layers along the forest's outline rounded - no square corners - each wandering in and out by up to this much (`0.35` is about a third of a cell), cut into straight cards a cell or so long: a natural, polygonal edge instead of the grid's. Give it room: a `depth` of 2-3 cells |

- The trees on the back cards rise to 4.6 units. Keep a `forest` wall lower than that (2-2.6) so the tops of the trees make the skyline, not the flat top of the wall.
- Plan a ring of open ground a cell deep in front of the walls for the fringe to stand in: make the solid part of the forest a cell smaller than the forest should look. A path through a jungle wants to be two cells wider than it should look.
- Each straight run of faces gets one card per layer; the layers wrap round outside corners and stop short in inside ones, so each follows the outline at its own distance. A card that would pass through a camera position is left out.
- With `wander` each layer is instead one line the same distance out from the forest all along - round at its corners - cut into cards that fade out where you see one almost edge on (`edge_fade`). The layers stop at any other wall, all but the back one short of it, so a house in a clearing keeps its trees behind it and none squeezed in beside it.
- Cards are drawn at the sprite stage: walls behind them show through their gaps, a ceiling over them (a canopy over a path) hides what rises above it, and they cast no shadows.

### Facades: buildings in layers

A city block drawn as walls is one flat face with windows painted on. Give the block's cells a `facade` and every straight run of its faces onto open ground is cut into separate buildings - different widths, heights, brick, paint and windows - and each building is drawn as layers of planes, one behind another in the cell in front of the block:

| layer | stands | holds |
|---|---|---|
| wall | on the street line | brick (or plaster) with openings for the windows and the door, sills, lintels, string courses, a cornice, soot |
| frame | a little back | window frames and glazing bars, the door |
| glass | with the frames | the panes, drawn by the glass pass (see Glass): what is behind, tinted and softly blurred |
| drape | further back | curtains, a roller blind, closed shutters, a net curtain or nothing - a different choice in every window |
| room | furthest back | the rooms: lit (a lamp-lit glow, now and then a screen's blue) or dark, with a lamp, a picture, a shelf, a plant or a figure |

So a window is set back in its wall, the glass sits in it, the curtains hang behind the glass and the room is further back, and as the camera moves they slide against each other. The wall is drawn as thick as the frames are set back in it (a `reveal`, see Planar sprites), so from an angle each window and door shows its far side - the brick jamb, the underside of the lintel, the sill - and never a gap into the room.

```json
"B": {"wall": "brick_dark", "h": 3.0,
      "facade": {"style": ["brick", "brick", "sooty"], "storeys": [3, 6], "widths": [3, 6], "lit": 0.5, "shops": 0.4, "seed": 3}}
"P": {"wall": "plaster", "h": 3.0, "facade": "plaster"}
```
| field | default | meaning |
|---|---|---|
| `style` | `brick` | `brick` (red and brown, painted sash windows), `sooty` (soot-blackened tenements, dark frames), `plaster` (washed colours), `neon` (dark concrete hung with glowing signs, blade signs standing out over the street on cards of their own, roller shutters half down over the shops, rooms lit pink, blue and green), `timber` (a village: limewashed and ochre plaster between dark oak posts, rails and braces, leaded casements, plank doors, and every house's roof built in 3D on plastered walls up from the block - running back from a gable end on a narrow house, or along the street in thatch or tiles, its eaves out over the front, some with a chimney; give it `storeys` [1, 2] and narrow `widths` [2, 3], and keep the block behind it no taller than one storey), `western` (a frontier main street: clapboard in faded paint peeling to grey wood, a false front standing up over every building's roofline - square, stepped, curved or pedimented - with its sign painted on it, no two alike along a street and a saloon among them, the saloon with batwing doors and a lamp-lit room behind; and the posts and fascia of a covered boardwalk standing `porch` units out (1 by default): make that a cell of `planks` a step high with a `ceil`, under a low `ceiling_height` such as 1.15, and a roof of boards slopes down over it from the front to the fascia; behind every false front the building's own gabled roof, built in 3D), or a list to mix them building by building |
| `porch` | `1` (western) | how far out from the fronts the boardwalk's posts and fascia stand; `0` for none |
| `storeys` | `[3, 5]` | the range of heights, a unit (a storey) each |
| `widths` | `[3, 6]` | the range of building widths along the street, in cells |
| `lit` | `0.35` | the share of windows with a light on |
| `shops` | per style | the chance a building keeps a shop: a big window and its door on the ground floor |
| `depth` | `1.0` | how deep the fronts are, in cells: the street line is that far out from the block |
| `glass` | `true` | the glass for its windows: `true`, or tint, opacity and blur (see Glass) |
| `seed` | `0` | shuffles the buildings |

- Plan the map like a fringe: the block's cells stand a cell back from where the fronts should be, with a cell of open ground in front of them for the layers (give it a floor: it is what a shop door looks onto). Pavement and road come after that.
- A building on an outside corner turns it: both its faces share its look and height. A building taller than its neighbour shows a plain side wall above it.
- The block itself can be low (its height only matters for shadows from a sun or moon); the buildings take their heights from `storeys`.
- Seen from straight down the street a front is flat, as everything in the raycaster is; the layers show best from the pavement, looking along the buildings.

### See-through walls

A wall whose texture has see-through texels (`bars`, `fence_iron`, `chainlink`, `railing`, `picket`, `portcullis`, `window_broken`, `lattice`, `tall_window` and `tall_window_top` (a gothic window to stack two or three storeys high), or any PNG with transparent pixels) is drawn as a single grille at the cell's near face. Everything behind it shows through the gaps, and it neither blocks light nor stops the ray.

```json
"f": {"wall": "fence_iron", "h": 1.0},
"P": {"wall": ["portcullis", "castle"], "h": 2.0},
"B": {"wall": ["brick", "window_broken", "brick"], "h": 3.0}
```
- The ground carries on under it. A see-through cell takes the floor (and roof) most common among its open neighbours, so a fence across a lawn stands on grass. Give it `floor`/`ceil` to choose.
- Stacking works as usual: a portcullis under solid stone, or a smashed window in the middle storey of a facade. The whole cell counts as see-through, so the solid storeys above don't cast shadows.
- Each built-in grille has its own height inside the tile: `railing` about 0.37 (waist height), `picket` about 0.45, `fence_iron` about 0.95 to its spear tips. `bars`, `chainlink`, `portcullis`, `lattice` and `window_broken` fill the whole tile. Use `h: 1` for them and let the texture set the visible height.
- Only one face per cell is drawn, so the grille has no thickness. Keep see-through cells one cell deep, and don't put sprites inside them.

### Heights: steps, platforms, altars

`heights` is an optional digit layer over the map. A digit `1`-`9` sets that **wall** cell's height to `digit x height_unit` (0.1 by default). Other characters, and open cells, are left alone:

```json
"map":     ["#######", "#.DDD.#", "#.SSS.#", "#.....#"],
"heights": [".......", "..333..", "..111..", "......."],
"legend":  {"D": {"wall": "marble", "top": "flagstone"}, "S": {"wall": "marble", "top": "flagstone"}, ...}
```
That gives a 0.3 dais behind a 0.1 step, which is a flight of stairs in one string per row. A cell's own `h` still works; `heights` only saves writing one legend entry per height.

- A block lower than the eye (0.5) is drawn as a solid with its `top` showing. Above eye height you only see its face, as in reality.
- Sprites placed in the cell of a block lower than 0.95 rest on its top (a throne on a dais, candles on an altar). In a `drop` cell they rest on the sunken surface. Either way `z` counts from that surface.
- Camera `height` is measured from `z=0`, not from the block underneath. To stand on a 0.3 dais, put the camera in a dais cell and set `height` to 0.8.
- The same goes for a roof: a camera in a block 5 tall with `height` 5.5 stands on top of it, and props up there take `z` 5. A cell is nearly three metres, so a parapet one cell deep is a wide deck: to look down into the street stand at its outer edge (or on it). A point light fades above its own height and shines over the roof to the edges of its `radius`, so a lamp set on the roof (`z` 5.6) lights the roof and the people on it as one at 0.6 lights a street; a lamp hung in the street below lights only what is near its own height. See `examples/neon_rooftop.py`.

### Void floors: space, open air, floating islands

A cell with `"floor": "void"` has no ground. Where you would see its floor you see sky instead: the panorama carries on below the horizon, as stars all the way round under the `space` sky, and as a sea of cloud far beneath under any other.

```json
" ": {"floor": "void"},
"g": {"floor": "grass", "side": "rock"},
"V": {"wall": ["viewport", "viewport"], "h": 2, "floor": "obsidian", "ceil": "panel"}
```
- Fill a map with void and draw islands on it for a world adrift in the sky. Each island's edge drops away as a cliff with a ragged underside, textured with the cell's `side` (or its floor). Walls standing at the brink sit on that cliff too.
- `cliff` (a cell key, default 2.5) is how deep that cliff drops: 0.1 for the thin edge of a plank bridge across the void, 3-7 for the rock under a floating island. For a floating mountain hang an `island_keel` (a billboard of rock tapering to a point) under the island with its top at the foot of the cliff, and `island_roots` cards round the edge; a block of rock with a `top` raises an island above the rest (see `examples/sky_islands.py`).
- Put void outside a `viewport` wall for a spaceship or station: looking out, space surrounds you, above the horizon and below it.
- Surround the islands with void all the way to the map edge. The ground past the edge carries on as the edge cells, so a map whose edge is grass is a continent, not an island.
- Sprites over a void have nothing to stand on: their `z` is simply their height. Scatter, grime and contact shadows skip void cells by themselves.
- A void cell can still have a `ceil`, but it rarely makes sense. A balcony or a ship's hull wants its own open cells or walls between the void and the roof.

## Textures

Any texture slot accepts:
- a built-in name (run `python scripts/assets.py catalog.png` to see them all),
- a PNG path (resized to 64x64, nearest). Relative paths are looked up beside the scene file first, then in the working directory - the same goes for PNG sprites, decals and TTF fonts,
- `{"base": "brick", "tint": [0.8, 0.9, 1.1], "brightness": 0.7}` for a recoloured variant.

The built-in textures - what each one is, which glow and which are see-through - are listed in `references/assets.md` (Textures).

## Lights

```json
{"x": 10.2, "y": 10.0, "z": 1.5, "radius": 4.5, "color": [1.0, 0.82, 0.5], "intensity": 1.1, "shadows": true}
```
- Falloff is `(1 - d/radius)^2 * intensity`, so `radius` is the hard edge of the pool of light. Lanterns 4-6, room lamps 3-4, big sources 6-8.
- A light dict is a point light unless it says `"type": "sun"` or `"moon"` (below).
- Shadows are traced through the grid: walls at least `min(z, 0.95)` tall block the light. See-through walls never do.
- Light fades above the lamp's own height: one at the default `z` 1.2 lights a wall up to about 1.4, one hung at 2.6 up to about 2.8, and fades above that, so tall facades darken toward the top. A lamp hung just under a ceiling lights the ceiling round it brightly; hang it lower for a softer room.
- Lights are invisible. Pair each with a sprite (`lamp_post`, `lantern`, `candles`) or an emissive texture so the source reads.

Lighting colour cheat sheet: oil/candle `[1,0.7,0.35]`, incandescent `[1,0.86,0.6]`, moonlight `[0.55,0.65,0.9]`, emergency/cult red `[1,0.15,0.1]`, sickly green `[0.5,1,0.6]`.

### Sun and moon

A light with `"type": "sun"` or `"type": "moon"` is directional. It comes from one compass direction, lights every open cell, casts long shadows from walls, and draws its own disc in the sky:

```json
{"type": "moon", "azimuth": 300, "elevation": 16, "intensity": 0.75}
{"type": "sun",  "azimuth": 215, "elevation": 13}
```

| field | default | meaning |
|---|---|---|
| `azimuth` | `300` | compass direction the light comes **from**, in camera degrees (0 east, 90 south, 180 west, 270 north) |
| `elevation` | `35` | degrees above the horizon, 1-89. Low values give long raking shadows and a disc near the skyline |
| `color` | sun `[1,0.94,0.82]`, moon `[0.55,0.65,0.95]` | |
| `intensity` | sun `0.85`, moon `0.4` | |
| `shadows` | `true` | walls shadow the ground, facades and sprites behind them |
| `disc` | `true` | draw the sun or moon in the sky. `false` keeps it off-screen. A visible disc replaces the sky preset's own moon |
| `disc_color`, `disc_size` | per type | disc colour and radius in degrees (sun 2.6, moon 2.0) |
| `disc_style` | none | `"stripes"`: a synthwave sun - yellow at the top through orange to pink, its lower half cut by gaps that widen toward the foot (`disc_color` then tints only its halo). Give it a `disc_size` of 7-9 and a low `elevation` in a `vector` sky |

- Shadows are exact to the wall heights: a facade is half-lit behind a lower building, and a character's legs fall into the shadow of a wall. Sprites themselves do not cast sun shadows.
- Under a roof, sun and moonlight only come in through openings: a doorway, a see-through window (`window_broken`, `viewport`, `lattice`...), a fallen stretch of roof or a skylight (open cells inside the walls, with or without more roof beyond them: the beam comes down through the hole). A low sun lays a long patch of light across the floor, and with volumetric fog the beam itself shows (see Fog). Everywhere else indoors still needs point lights.
- Coloured glass lets the light in coloured: a storey of `stained_glass`, `lancet_window` or `rose_window` in a wall is an opening whose panes each colour what comes through them - the window's pattern laid on the floor, the walls and whatever stands in its light, and with `shafts` the beams in the fog take its colours - while the lead and the stone round the panes stop it. Walls are a cell thick, so the light comes through where the sun stands in front of the window, within about 20 degrees of straight on; further round, the stone either side cuts it off as a deep window's jambs do, and past about 35 degrees none comes in. A wall of glass that rises to the roof lets nothing in over its top. See `examples/glass_chapel.py`.
- Put the disc in frame by aiming the camera near `azimuth` with a low `elevation` (10-25). Match the sky preset: a sun in `day`, `dusk` or `overcast`, a moon in `night` or `storm`. Lower `ambient` when you add a moon, because it already lights the whole ground.
- A shot's `overrides` can swap the moon for a sun to show the same place by day (see `examples/winter_lake.py`) - or give it a `time` (below).

### Time of day

`"time"` sets a scene to an hour in one key, on the scene or on a shot (`{"x": 4, "y": 9, "angle": 270, "time": "dusk"}`):

```json
"time": "golden"
"time": 7.25
"time": {"at": "dusk", "azimuth": 200}
```

- **The hour**: `dawn` (6.9), `morning` (8.5), `noon` (12.75), `afternoon` (15.5), `golden` (18.3, the last hour of sun), `sunset` (18.85), `dusk` (19.5, the sun gone) or `night` (21.5), or any hour as a number.
- **The sun** stands where the clock has it - rising due east (azimuth 0), crossing the south (90) at noon at 58 degrees, setting in the west - reddening and weakening as it sinks; once it has set a full moon rises opposite it. The scene's own sun or moon is replaced, keeping its other fields (`disc`, `shadows`...) and its strength for its height, so a room tuned to a bright sun stays bright; a scene with neither gets one only if its sky is one the hour sets (so none under `overcast` or `storm`). `azimuth` and `elevation` in a time dict put it elsewhere: turn it to stand in front of a window, say.
- **The sky** becomes `dawn`, `day`, `golden`, `sunset`, `dusk` or `night` if the scene's is one of those; any other (`overcast`, `storm`, `space`, `dream`...) is kept. A time dict's `sky` picks one.
- **The ambient light and the fog's colour** are darkened or lightened and tinted for the hour from the scene's own - taken to be right for the hour its sky shows - so a dim interior stays dim beside a bright street at any hour, and a warm room stays warm. A time dict's `ambient` and `fog` (a colour) set them outright. A scene with no sky (`null`) keeps its own: it is nowhere the hour reaches.
- **Lamps**: a facade's `lit` is how many of its rooms show a lamp after dark - by day few do - and a `tower`'s or a `city_block`'s is how many of its windows do. Lights marked `"night": true` burn only from sunset to sunrise - street lamps, lanterns, a lit window's glow - and `"day": true` only by day; objects and sprites take the same marks, so a city's `searchlight`s are out by day and the washing is hung out only by day.
- Keys a shot's `overrides` give beside its `time` stay as the shot gives them: `"overrides": {"time": "night", "ambient": [0.1, 0.1, 0.16]}`. Give a scene's lamps `"night": true` and one key turns the same street from noon to night.

## Sky and skyline

Open cells (no `ceil`) show a 360-degree sky panorama: `sky` picks the preset. `skyline` adds distant silhouettes along its horizon, so an open map doesn't end at a bare line where the ground meets the sky:

```json
"skyline": "mountains"
"skyline": {"type": "city", "height": 1.3, "lights": 0.35}
"skyline": ["mountains", {"type": "treeline", "color": [0.05, 0.08, 0.06]}]
```

| type | looks like |
|---|---|
| `mountains` | two ranges of peaks, the far one paler |
| `hills` | rolling downs in two layers |
| `treeline` | a dark wall of overlapping conifers: woods, churchyards, lakesides |
| `city` | blocky towers with a scatter of lit windows (`lights`, default 0.22, is the share that are lit) |
| `islands` | a few low islands far out at sea, the bigger ones crowned with palms (`count`, default 7); open sky between them down to the horizon |
| `jungle` | rolling rainforest crowns in two layers, the odd emergent giant standing clear |

- A dict takes `type`, `height` (a multiplier, default 1), `color` (RGB; by default each layer is tinted toward the sky's own horizon colour, so it sits in the haze) and `seed`. A list draws back to front, first entry farthest.
- Heights are in degrees above the horizon, so the silhouette keeps its proportions at any resolution or field of view. It is painted into the sky, so it never occludes anything in the map and costs nothing per frame.
- Pair it with the map: a `treeline` behind a fenced yard, `mountains` over a frozen lake, `city` beyond a rooftop. Fog's `sky_mix` hazes it along with the sky.

The presets: `night`, `dusk`, `storm`, `day`, `overcast` and `blood` for the world as it is; `space` (black, dense stars, a galaxy band and coloured nebula, continuing below the horizon); `alien` (teal overhead, sulphur at the horizon, magenta cloud); `dream` (periwinkle to rose to peach, pale cloud); `sunset` (indigo overhead, rose, a gold horizon, coral cloud: put a low sun in it over the sea); `golden` (late-afternoon blue over a warm horizon: golden hour).

### Sky objects

`sky_objects` paints planets and stranger things into the sky, placed like the sun and moon: by `azimuth` (camera compass) and `elevation` (degrees above the horizon; negative is below it, visible over a void floor), with `size` as an angular radius in degrees.

```json
"sky_objects": [
  {"type": "ringed", "azimuth": 285, "elevation": 8, "size": 14, "color": [0.86, 0.66, 0.46], "lit_from": 205},
  {"type": "moon", "azimuth": 300, "elevation": 26, "size": 2.4},
  {"type": "eye", "azimuth": 322, "elevation": 15, "size": 6.5}
]
```

| type | looks like | default size |
|---|---|---|
| `planet` | a banded gas giant with a storm spot, lit on one side | 9 |
| `ringed` | the same with a tilted ring, its far side behind the planet and its near side in front | 7 |
| `moon` | grey, cratered, lit on one side | 3.5 |
| `earth` | a blue world seen from space: oceans, green and desert continents, white cloud, polar ice, a blue limb, its night side dark | 6 |
| `sun` | a bright disc in a wide glow (it lights nothing: add a `sun` light for that) | 3 |
| `eye` | a vast eye, looking at the viewer | 8 |
| `clock` | a clock face hung in the sky, its hands stopped at `time` (hours: 10.15 is about ten past ten), the bottom of it running like wax (`melt`, 0-1, default 0.45) | 7 |

Fields: `color` and `color2` (the main colour and the bands, ring or iris secondary), `lit_from` (the screen direction light falls from, in degrees: 0 right, 90 below, 180 left, 270 above; default 210, upper left), `phase` (0 lit face-on to 1 lit from the side, a crescent; default 0.75), `glow` (the halo), `tilt` and `angle` (the ring's openness and slant), `bands`, `craters` and `seed`.

- Sky objects are part of the panorama: they never occlude anything in the map and cost nothing per frame. The skyline is drawn in front of them, so a planet can rise behind mountains.
- They light nothing. Give a scene a point light near a viewport, or a `sun` light, in the planet's colour if its glow should fall on the floor.
- Match `lit_from` to the scene's sun, so the planet and the shadows agree.
- Any sky object replaces the `night` preset's decorative moon, just as a sun or moon light does.

## Fog

The plain fog is a fade by distance: `{"color": [r, g, b], "density": 0.05}`. Every surface blends toward `color` as it recedes, and the sky takes `sky_mix` of it.

Add any of the keys below and fog becomes **volumetric**. Each pixel marches through the air in front of it, so the fog has a shape and carries light.

```json
"fog": {"color": [0.58, 0.55, 0.62], "density": 0.01, "ground": 0.4, "height": 0.3, "noise": 0.6, "shafts": 0.8}
"fog": {"color": [0.12, 0.11, 0.09], "density": 0.06, "glow": 0.6, "shafts": 2.4}
"fog": {"color": [0.06, 0.07, 0.09], "density": 0.035, "glow": 1.3}
```

| key | default | meaning |
|---|---|---|
| `density` | `0.02` | an even haze everywhere (per unit of distance) |
| `ground` | `0` | extra density at ground level: mist lying in hollows, sea fog, smoke along the floor |
| `height` | `0.6` | how fast the ground layer thins with height. 0.3 is knee-deep mist, 1.5 a fog bank you stand in |
| `noise` | `0` | 0-1: the ground layer drifts in banks instead of lying evenly |
| `scale` | `4` | the size of those banks, in world units |
| `glow` | `1` | how strongly the point lights light the fog: halos round lamps, light spilling through a doorway |
| `shafts` | `1` | how strongly sun and moonlight light it. The light keeps its shadows, so it falls in beams through gaps between stones, trees and windows. `false` or `0` for none |
| `anisotropy` | `0.3` | how much brighter the light is when you look toward it (0 even, 0.6 strong) |
| `steps`, `distance` | `32`, `48` | samples along each ray and how far they reach. Raise `steps` if a beam looks banded |

- The volumetric pass covers everything: walls, sprites and the sky. Looking up through a ground layer you see clear sky, and looking along it the horizon vanishes. `sky_mix` and `fog_sky` don't apply.
- Beams need three things: a `sun` or `moon` light, something to cast shadows (walls, stones, the edges of a window), and enough haze to catch the light. A dark scene shows them best: dusty interiors, forests, dawn mist.
- `glow` uses the point lights as the lightmap stores them, shadows included. A lamp gets a halo and a lit doorway breathes light into a foggy street.
- Light the fog brighter than the dark: `color` is the light the fog holds by itself, so a moonlit mist wants a pale blue-grey and a dusty hall a warm brown.
- It costs about as much again as the rest of the frame. Weather particles fade into the same fog.

## Sprites

```json
{"id": "guard", "x": 11.3, "y": 20.3, "type": "guard", "scale": 0.6, "z": 0, "flip": false}
```
| field | meaning |
|---|---|
| `type` | built-in prop, built-in character, a name from `sprite_defs`, or a PNG path (RGBA) |
| `id` | name for overlays to anchor a speech bubble to, and for a camera's `look_at` |
| `scale` | world height in units (each built-in has a default; people are ~0.6-0.66) |
| `variant` | which drawing of a prop that is drawn a few ways (`rocks`, `grass_tuft`, `dry_tuft`, `fern`, `bush`, `bush_autumn`, `boulder`, `boulder_snow`, `mushrooms`, the trees `pine`, `snowy_pine`, `tree`, `tree_autumn`, `birch`, `birch_autumn`, `bald_cypress`, `palm`, `dead_tree`, `log` and `stump`, the plants `cattails`, `flowers`, `poppies`, `monstera`, `prickly_pear`, `tumbleweed`, `kelp` and `cypress_knees`, and `rubble`; and on the road `traffic_light` (0 red, 1 amber, 2 green), `car_compact`, `car_sedan` and `car_oncoming` (their paint), `race_car` (its livery) and `billboard` (its ad)): `0` is its first drawing. Without it one is picked by where the prop stands - the same every render, but no two alike - wherever it comes from: `sprites`, `scatter`, a prefab or an object |
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
| `shadow` | this sprite's contact shadow: a strength, or `false` for none (default: the scene's `contact_shadows`) |
| `facing` | the compass direction a character faces (camera degrees). With the camera behind it, you see its back |
| `view` | `"front"` or `"back"`: force a view whatever the camera does |
| `planes` | `0` | `0` a billboard turning to face the camera; `1` a single card standing fixed in the world, `2` a cross of two, `3` a star of three (see Planar sprites). The low plants default to 2 or 3 |
| `angle` | from its position | for a planar sprite: the compass direction the (first) card runs along |
| `length` | its image's width | for a single card: its length in world units; the image repeats along it |
| `u0` | `0` | for a card: where along its image it starts, 0-1 |
| `edge_fade` | `false` | for a card: fade it out where it is seen almost edge on, instead of squeezing its whole picture into a narrow block (a wandering fringe's cards do) |
| `reveal` | none | for a card with see-through openings: how thick it is, in world units, so an opening seen at an angle shows its far side (see Planar sprites) |

### Planar sprites: crosses, stars and cards

A billboard turns to face the camera, so a bush is the same flat picture from every side. A sprite with `planes` stands as fixed vertical planes instead, each drawn with the sprite's image like a thin wall: `2` crosses two at right angles, `3` makes a star of three 60 degrees apart (cutting the ground round it into sixths). Seen from any side at least one plane is turned toward you, and as the camera moves they shift against each other, so plants have body. The low plants - ferns, tufts of grass, bromeliads, banana plants, tree ferns, monstera, heliconia, poppies, bushes, reeds and flowers - stand this way by default; `"planes": 0` makes one a billboard again.

```json
{"x": 7.0, "y": 15.5, "type": "fern"}                                    // a star, by default
{"x": 8.5, "y": 14.6, "type": "monstera", "planes": 3, "angle": 20}
{"x": 4.0, "y": 9.5, "type": "jungle_card_2", "planes": 1, "angle": 90, "length": 6.0}
```
- Each plane is depth-tested per pixel against everything else, its partners in a cross included, and lit by the lights and the sun at its own points, both faces alike.
- `planes: 1` with a `length` is a card: a long strip of scenery, its image repeating along it. Fringes are made of these (see Fringe).
- A card is as thin as paper: look through a hole in one at an angle and you see straight past its edge. Give it a `reveal` (a depth in world units) and it is drawn as a slab that thick instead: through each see-through opening, seen at an angle, the opening's far side shows - the jamb, the head above it, the sill below - in the colours of the card just past the opening's edge, darker the deeper it goes and lit by its own facing (a jamb turned to the sun is lit where the light gets in through the opening). The walls of a `facade` are drawn this way.
- Without an `angle`, each takes one from its position, so a bed of ferns is not all aligned. In a prefab, `angle` turns with the prefab.
- Trees that lean (`palm_lean`) and anything with a front (people, furniture) stay billboards: a leaning trunk crossed with itself leans three ways at once. Mix the two in a prefab instead: `palm_3d` is a billboard trunk under a star of `palm_crown` planes.

### Glass

Glass is drawn in a pass of its own, after all the geometry and sprites: each pane looks at what is already behind it and shows that, tinted, under a faint reflection of its own. By default what it shows is softened the cheap way - the finished frame shrunk to half size and blown back up without smoothing, so each 2x2 block of pixels is averaged - which reads as old window glass.

```json
{"x": 6.0, "y": 4.5, "type": "glass_pane", "angle": 0, "length": 3.0, "scale": 1.2}
{"x": 9.0, "y": 4.5, "type": "glass_pane", "glass": {"tint": [0.9, 1.0, 0.92], "opacity": 0.1, "blur": 0}}
```
- Any sprite with `"glass": true` (or a dict) is glass, drawn as a card (`planes` 1 unless it says otherwise). Its image's alpha says where the glass is and its colours are what the glass reflects; `glass_pane` is a plain one, a unit square, glass by default.
- `tint` multiplies what shows through (default `[0.82, 0.92, 1.0]`, a light blue), `opacity` mixes in the reflection (default `0.22`: mostly see-through), `blur` is `1` (half size, the default), `2` (quarter size: frosted), or `0` (clear), and `fog` (default `false`) lets the fog carry on behind it.
- Glass writes depth, so fog and rain treat it as a surface, and it shows in reflections on the floor. A pane behind another pane is not seen through it.
- `fog: true` lets volumetric fog carry on behind the pane: the water of a tank glowing round its lamps, the mist beyond a window. By default the fog stops at the glass, as it should at a window onto space. For water, give the glass a blue-green `tint` and `blur: 0`, and light the tank with white lamps - the tint and the fog make it blue. See `examples/aquarium.py`.
- The windows of a `facade` are glass (see Facades).

Drawing order: opaque sprites first (they write depth), then translucent/additive ones back to front without writing depth, so ghosts show what is behind them. Built-in lamps, lanterns and candles have emissive flames; place sprites at least ~0.2 from wall faces.

**Contact shadows.** Every opaque prop or character standing on the floor gets a soft dark stamp under its feet, sized to its width, so nothing looks pasted onto the ground. `contact_shadows` sets the strength for the scene (0.55 by default, `0` for none) and a sprite's `shadow` overrides it. Sprites lifted off the floor (`z` > 0.05), standing on a block, translucent, additive or `fullbright` get none, and nor do fires, light fixtures, hanging and wall-mounted props, ladders, crystals and glowing mushrooms.

The built-in props and characters - what each one is and how it is best placed - are listed in `references/assets.md` (Props, Characters).

Wall-mounted and hanging props (`sconce`, `painting`, `banner`, `wall_clock`, `pipe_valve`, `ceiling_lamp`, `chandelier`, `ivy_hang`, `chains`, `ladder`) are ordinary sprites: place them a little off the surface (about 0.2-0.3 from a wall face) and set `z`. Ground clutter (`rocks`, `rubble`, `bones`, `sack`, `bucket`, `broken_barrel`, `grass_tuft`, `dry_tuft`, `reeds`) is sized to read at 320x200; scatter a handful rather than a carpet.

## Wireframes

```json
"wireframes": [
  {"mesh": "cube", "x": 12.0, "y": 8.0, "size": 1.2, "angle": 25, "color": [0.3, 1.0, 1.0]},
  {"mesh": "dodecahedron", "x": 15.0, "y": 6.0, "z": 2.0, "size": 3.0, "tilt": 20, "solid": true, "color": [1, 1, 1]},
  {"mesh": "terrain", "x": 20.0, "y": -20.0, "size": 40, "scale": [1, 0.4, 0.3], "solid": true, "seed": 4,
   "gradient": [[0.62, 0.4, 1.0], [0.3, 1.0, 1.0]]}
]
```

Low-poly meshes drawn as lines of light, projected through the camera in true 3D: a cube is a cube from every side, a ring of them reads as solid space, and they stand in reflective floors. Every edge is one pixel wide (`width` in native pixels) whatever its distance, hidden behind anything nearer, and gives off light (a `bloom` with `"source": "light"` glows round them). With `"solid": true` a mesh fills its faces with `fill` (black by default), so it hides what is behind it - its own far edges included: black shapes edged in light, the look of 80s vector arcade games. A shot adds its own with `extra_wireframes`, and a shot can `look_at` a wireframe's `id` (and focus on it with `dof`).

| field | default | meaning |
|---|---|---|
| `mesh` | `"cube"` | a built-in shape (below), or your own: `{"vertices": [[x, y, z], ...], "faces": [[0, 1, 2], ...], "edges": [[0, 1], ...]}` (edges default to the faces' sides; a mesh of edges alone draws lines only) |
| `x`, `y`, `z` | `0` | where the base of the mesh stands; `z` lifts it off the floor |
| `size`, `scale` | `1`, `[1, 1, 1]` | the built-ins are about one unit across; `scale` stretches along x, y and z |
| `angle`, `tilt`, `roll` | `0` | turns, in degrees: about the vertical (like a camera's angle: 90 faces +y), then tipped forward, then rolled - all round the mesh's own middle |
| `color`, `gradient` | cyan | the lines' colour, or `[low, high]` colours blended by height (mountains purple at the foot and cyan at the peaks) |
| `intensity`, `glow` | `1`, `1` | brightness of the lines, and how much of it goes into the emission (bloom) |
| `solid`, `fill` | `false`, black | fill the faces, hiding what is behind; `fill` their colour |
| `blend` | `"add"` | `"add"` (lines add their light: brighter where they cross) or `"over"` |
| `id` | none | an anchor for `look_at`, `dof` focus and speech bubbles |

Built-in meshes (each about one unit, standing on z 0): `cube`, `pyramid`, `tetrahedron`, `octahedron`, `icosahedron`, `dodecahedron`, `prism` (`sides` 6), `cylinder` (`sides` 16), `cone` (`sides` 12), `sphere` (`segments` 12, `rings` 8: a globe of lines), `torus` (lying flat: `segments` 16, `sides` 8, `thickness` 0.15 - tilt it 90 for a ring standing up), `grid` (a flat lattice, `cells` 8), `terrain` (low-poly mountains, `cells` 14, `peaks` 3, `seed`: scale it wide and low for a range on the horizon), `racer` (a low-poly racer one unit long, nose toward +x, a wheel ring at each corner), `palm` (a synthwave palm in lines), `tree` (a low-poly pine), `tower` (a stepped spire), `gate` (two pillars and a lintel: scale it to span a street), `crystal` (six-sided, pointed at both ends).

- Dense meshes (a `sphere` or `torus` with many segments) pile up light where their lines crowd together; make them `solid`, or use fewer segments, when a bloom is strong.
- They are not lit by the scene: their lines are light. Put a point light under a big one for its colour to land on the floor.
- Mountains far beyond the map are fine - a wireframe is not bound to the grid - and they fade into a plain fog with distance like everything else.
- See `examples/vector_world.py`.

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
| `reflect` | 0-1, floor decals only: how mirror-like the decal makes the floor where it covers it (see Reflections) |

Built-in decals: puddle, puddle_dark, puddle_shine, stain, stain_rust, splatter, splatter_dark, vines, moss_patch, crack, scorch, leak, cobweb, rune_mark, drain, contact_shadow, for the shore and the jungle pool: foam, foam_glow, starfish, shells, seaweed, lily_pads, and for hangars: pad_marking (a painted landing ring with an H, 4-6 units across) and hazard_stripe (a worn yellow-and-black band), and on the Moon rover_tracks (a rover's two tracks of chevron treads pressed into the dust) and crater (a bowl lit on one wall and shadowed on the other, its rim and a paler blanket round it - a few units across), and for the doomed mode toxic_sign (a yellow warning triangle with a skull, TOXIC under it, for a wall), and for a saloon's walls wanted_poster (yellowed paper, WANTED over a sketched face, $500), and for a house gone to ruin glass_shards (broken glass on a floor under a window, a glint at each shard's sharpest corner) and sigil (a sigil painted in red on a wall - a circle, a triangle in it, a line down through both, the paint run in drips), and for roads (they lie on a road scene's road and ground - see Road scenes) oil_stain, tyre_marks (two skid marks, four times as long as wide), road_patch (newer asphalt in a sealed square), pothole, manhole, lane_arrow (an arrow painted on a lane, pointing on), zebra_crossing (lay it across the road with a `size` of its width), start_line (a chequered band across a race track, laid the same way), wake (a boat's wake spreading behind it), leaf_litter, sand_drift and pebbles. `rune_mark` and `foam_glow` are emissive, so they glow regardless of lighting. Seen from eye height a floor decal is foreshortened almost to a line, so `foam` reads from a raised camera or close up; for surf seen from a standing height use the `surf` props. `contact_shadow` is the soft disc used for contact shadows, which you can also stamp by hand (under a prop hanging low over the floor, say). The puddles reflect by default (`puddle_shine` 0.55, `puddle` 0.35, `puddle_dark` 0.25), so a lamp post shows in the wet patch at its foot.

- A floor decal is drawn on the plane of the cell it sits in, so a puddle inside a cell with a `drop` lands on the sunken surface, not the bank above it.
- Dark puddles read as holes punched in a lit floor. Use `puddle_shine` on anything a lamp reaches (wet asphalt, sand, boards) and keep `puddle_dark` for dim interiors.
- Wall decals that hang (`vines`, `leak`, `cobweb`) are drawn from the top of their footprint down, so set `z` near the top of the wall.
- A wall decal is clipped to its own face, so one that overhangs the cell edge ends in a hard vertical cut. Keep `u - size/2` and `u + size/2` inside 0-1, or split a wide stain across two faces.

## Reflections

Water, ice, wet streets and puddles mirror whatever stands over them: lit windows across a frozen lake, a creature wading in a cave pool, a lamp post in the puddle at its foot.

- A floor reflects if its cell has `reflect` (0-1), its texture reflects by default (`water` 0.5, `ice` 0.38), or a reflective decal covers it (the puddles).
- `"reflections": false` turns them off for the scene, a number scales every reflection (`0.5` halves them), and `{"amount": 1.0, "ripple": 1.0, "smear": 1.0}` also sets the sideways shimmer (`0` for a still, glassy surface, `2` for choppy water) and the vertical streak.
- **A mirror**: `{"ripple": 0, "smear": 0}` makes still water a perfect mirror - below 1, `smear` mirrors as a real mirror does: each thing about its own foot, whether it wades in the water, stands on a dry bank past it or floats in the air (a figure, a mound of salt, a palace across the ice, a whale), and the sky about the horizon; dry ground mirrors nothing, so the water before a bank shows the sky. Give the floor `reflect` 0.9 and a big sky: ground and sky become one (see `examples/salt_flat.py`).
- Reflections are stronger at a grazing angle than looking straight down. Bright things (lamps, lit windows, glowing eyes) come through harder than the rest, and the mirror image is smeared a little vertically the way wet ground streaks light.
- It is screen-space: a reflective floor mirrors what is on screen just above it in the same column. Across water at eye height that is nearly everything. Very close to the camera the mirrored point would be above the frame, so the floor there only takes a faint sheen of the sky or ceiling. Walls never reflect.
- Reflections read best on dark, still surfaces with something bright beyond them. Give a lake or a wet street a light source on the far side.

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
- `"hd": true` draws it as the built-in characters are drawn (scripts/charhd.py): about a tenth taller (a row of the torso and two of the legs said twice, where nothing is doubled) and at twice the resolution (scale2x - smooth silhouettes, no new colours), a finer face where it uses `s` skin, `S` its shade and dark `e` eyes (a one-pixel pupil with the socket's shade beside it, a brow, the nose's shade only at its foot), and form shading from the upper left. Its `height` is then that tenth taller too, so each pixel stays the size it was. Use it for a person who will be seen close.
- `back` (optional) is the same figure from behind, as another grid of the same size, written the same way as `pixels`. It shows when the sprite's `facing` points away from the camera. Every built-in character has one. Turn the face to hair or hood, and the front details (buttons, a badge, a held book) to plain cloth.
- 16x32 is the house size for people; the built-ins are drawn from it at 32 x ~70 (see `hd`). Props can be any size; keep rows equal length.
- Shade with 2-3 tones per material (shadow, base, highlight) and a dark outline colour for readability.

### Lettering

Any words you want in the world - a shop's name over its door, a neon sign in a window, a brass plaque, a date cut
over an arch, the soup of the day on a blackboard, a wanted poster - are lettering (scripts/lettering.py): the pixel
font drawn at a whole-number scale into a texture, in a style. Give a `sprite_defs` or `decal_defs` entry `text`
instead of `pixels`:

```json
"sprite_defs": {"inn_name": {"text": "THE CROWN", "style": "painted", "color": "#d8b048", "ground": "#6a2420",
                             "height": 0.2}},
"decal_defs": {"open": {"text": "OPEN", "style": "neon", "color": "#ff4fa0"}}
```

or place a `sign` object (see Objects), which stands it in 3D on a board. `text` takes a newline for a second
line (lines are centred). Styles:

| style | what it is |
|---|---|
| `painted` | a board of `ground` (default dark brown) with a bevelled edge, the grain of its wood and a painted line inside its edge, the letters in `color` (default cream) with a shadow, flaking here and there |
| `neon` | glowing tubes of `color` (default pink) with a halo, on a dark backing (`"backing": false`: on nothing) - it glows; give it a light of its colour, or bloom with `source: light` |
| `plaque` | a brass plate, the letters engraved, a screw at each corner |
| `carved` | letters cut into stone (`ground`, default grey): dark in the cut, light on its lower wall |
| `chalk` | chalk on a blackboard in a wooden frame |
| `gilt` | gold leaf letters, light along their tops, a dark line round them - on `ground` if given, else on nothing (gilt on a window) |
| `ink` | plain letters of `color` (default near black) on nothing |
| `poster` | ink letters on a sheet of paper |

`scale` (default 2) is how many pixels make a pixel of the font; `"smooth": true` draws big lettering at half that
with its steps rounded off (scale2x). A sprite's `height` sets its size in the world, its width following.

## GUI (overlays)

UI is listed in `overlays` (scene-wide) and/or a shot's `overlays`, drawn at native resolution in a hand-drawn pixel font, after world post effects and before palette quantisation. Order matters: later entries draw on top.

The pixel font covers printable ASCII. Curly quotes, dashes, ellipses and no-break spaces are mapped onto it, and accented letters lose their accent (`café` draws as `cafe`); anything else shows as `?`. Text is kept inside the frame: a `title` too wide for its `scale` steps down a size, and bubbles, dialogs, captions, panels, toasts and subtitles wrap. Only `choice` options stay on one line each, so keep them short.

**Placement** (most widgets): `"at"`: `top-left`, `top`, `top-right`, `left`, `center`, `right`, `bottom-left`, `bottom`, `bottom-right`; or explicit `"x"`, `"y"` in framebuffer pixels (negative counts from the right/bottom); `"margin"` (default 6). The framebuffer is 320x200 by default.

**Themes**: `"ui": {"theme": "classic"}` with `classic` (navy and gold), `parchment` (tan paper, brown ink), `terminal` (green on black), `blood` (black and red), `steel` (Windows-95 bevel), `doomed` (stone grey, red text, yellow accents). Override any colour as RGBA lists: `fill`, `border`, `border_dark`, `text`, `accent`, `dim`, `shadow`, `select`, `select_text`; plus `pad`, `width` (bubble wrap) and `font` (`"pixel"` default, `"pillow"`, or a TTF path with `font_size`). A shot can switch theme through `"overrides": {"ui": {...}}`.

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
| `statusbar` | `ammo`, `health`, `armor`, `arms` (slots owned, 2-7), `keys` (`blue`/`yellow`/`red`), `ammo_table` (four `[current, max]`), `face` (`auto`/`grin`/`ouch`/`dead`), `look` (-1/0/1), `height` 0.16 | the stone status bar of a 1993 shooter across the bottom of the screen: big red numbers, the arms grid, a face in the middle that bloodies as `health` falls, the ammo table; held items are held up above it |
| `message` | `text`, `color` | a game message at the top left, plain text with no box ("Picked up a clip.") |
| `image` | `name` (icon or sprite), `scale` | place any icon/sprite on screen |
| `viewmodel` | `item`, `side`, `x_offset`, `y_offset`, `scale`, `brightness`, `light`, `fire` | first-person held item, lit by the light at the camera, drawn before world post effects; `fire` (pistol, shotgun) adds a muzzle flash that lights the room for the shot |

**Doomed mode.** For a frame from a 1993 shooter: the default 320x200, `"ui": {"theme": "doomed"}`, a `statusbar` and a `message` in the shot's `overlays` with a `pistol` or `shotgun` `viewmodel` (`"fire": true` for a shot going off), a camera aimed with a 2-point `look_at` and `"pitch": -0.08` so the horizon sits in the middle of the view above the bar, `"light_levels": 16` and a near-black `fog` so the light falls off into the dark in bands, and the doomed textures and props. See `examples/doomed.py`.

**Icons** (16x16, used by toast/hotbar/inventory/panel/counter/image): revolver, bolt_cutters, screwdriver, crowbar, wrench, lockpick, hammer, axe, key, iron_key, note, idol, amulet, tonic, ammo, dispel, lantern, flashlight, fuel, boards, book, map, gear, skull, plus pointers `pointer` and `hand_pointer`. Any sprite name also works as an icon.

**Held items** (`viewmodel`): revolver, lantern, flashlight, axe, crowbar, torch (modelled in 3D and seen from the player's eye - the revolver from behind, its barrel running away into the view; each hand from the holder's side, its sleeve running off the edge of the screen), pistol, shotgun (the last two held out in the middle of the view, 1993-style). The lantern and torch add a point light at the camera automatically (`"light": false` to disable); the flashlight turns the flashlight cone on unless the shot sets it.

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

## Prefabs

A prefab is a named group of things placed with one line: sprites (billboards or planes), point lights, decals, scatter, other prefabs, and even a patch of map with its own legend. Put them in `prefabs`; the loader turns each into ordinary parts before anything else reads the scene, so they light, occlude and scatter like parts placed by hand.

```json
"prefabs": [
  {"type": "campsite", "x": 12.5, "y": 20.5, "seed": 2},
  {"type": "beach_hut", "x": 31.5, "y": 14.5, "angle": 180},
  {"type": "palm_grove", "x": 36.0, "y": 22.0, "angle": 40, "scale": 1.1, "seed": 4, "id": "grove"}
]
```
| field | meaning |
|---|---|
| `type` | a built-in prefab or a name from `prefab_defs` |
| `x`, `y` | where its origin goes |
| `angle` | turn, in compass degrees: at 0 a part's `dx` points east, at 90 south. A prefab with a map turns in quarter turns |
| `scale` | grow or shrink the whole group (not a prefab with a map) |
| `seed` | picks its variations: the same seed gives the same group |
| `id` | prefixes the ids of its parts (`grove.tall`), so two copies can both be aimed at |

Built-in prefabs: `campsite` (a fire, logs, stones and its light), `palm_grove`, `palm_3d` (a billboard trunk under a star of crown planes), `jungle_clump`, `jungle_bush` (planes and billboards mixed), `fern_bed`, `ruined_columns`, `altar_fire` (a stone block of map with a brazier on it), `beach_hut` (bamboo and thatch walls, door, lattice window, roofed floor, its torches and lights; the door faces east at angle 0), `tiki_torches`, `street_lamp`, `graves`, `shrine`.

Defining one (in `prefab_defs`, or the same form in `scripts/prefabs.py` for a built-in):
```json
"prefab_defs": {
  "well": {
    "map": ["W"], "legend": {"W": {"wall": "stone_dark", "h": 0.6, "top": "water"}},
    "sprites": [{"type": "bucket", "dx": 0.7, "dy": 0.2},
                {"type": "grass_tuft", "dx": -0.6, "dy": 0.5, "jitter": 0.3, "chance": 0.7, "scale": [0.3, 0.45]}],
    "lights": [{"dx": 0, "dy": 0.8, "z": 0.9, "radius": 2.5}],
    "decals": [{"tex": "puddle", "dx": 0.5, "dy": 0.7, "size": 0.8},
               {"tex": "moss_patch", "surface": "wall", "cell": [0, 0], "face": "south", "z": 0.3}]
  }
}
```
- Parts sit at `dx`, `dy` from the origin (world units, before the turn). `lights` are point lights; put suns and moons in the scene.
- A `map` is laid with its `anchor` cell (`[column, row]`, the middle one by default) on the cell holding the origin, and the origin moves to that cell's centre so the parts line up with the walls. Its legend's characters get fresh ones, so they never clash with the scene's; any other character is written as it is and means whatever the scene's legend says; a space leaves the scene's cell alone. Wall decals name a `cell` of the prefab's map and turn with it.
- Variation: `jitter` (move by up to that much), `chance` (keep only that often), a `[low, high]` pair for `scale`, `z` or `angle`, `"flip": "random"`, and a prefab-level `scale` pair for the whole group.
- `scatter` entries keep working inside a prefab: an `on` naming the prefab's own legend characters scatters over its cells alone. `prefabs` nest, turning and scaling with their parent.
- A shot's `overrides` can change `prefabs` (a campfire only at night): give the whole list, it replaces the scene's.

## Objects

An object is a thing too big to be a billboard - a car, a food stand, rock, crystals - built in 3D out of flat panels, the way Build-engine maps built cars and counters out of flat sprites: panels standing, lying and sloped at any angle, see-through wherever the thing is not (a car's side is its outline, open above the hood), glass you can see the seats through, and among them, for the small things that read best as pictures (bowls on a counter, lanterns), ordinary billboards. Every panel is drawn in true perspective, depth-tested per pixel and lit like a wall, so from any side you see the sides you should, and a figure can stand in front of the counter and behind the awning post. Put them in `objects`:

```json
"objects": [
  {"type": "car", "x": 20.4, "y": 45.6, "angle": 270, "paint": "#9a9ea4"},
  {"type": "car", "x": 22.75, "y": 49.0, "angle": 90, "paint": "#2e3c5a", "lights": true},
  {"type": "noodle_stand", "x": 17.95, "y": 22.0, "angle": 180},
  {"type": "rock_wall", "x": 19.0, "y": 3.0, "angle": 90, "length": 34, "depth": 1.8, "height": [0.5, 1.45],
   "rock": "reef", "seed": 3},
  {"type": "boulder", "x": 9.5, "y": 6.4, "angle": 90, "size": 1.5, "height": 0.9, "rock": "reef", "plants": 3},
  {"type": "rock_wall", "lining": "RQU", "rock": "sandstone", "depth": 1.4, "height": [0.9, 2.6], "seed": 4},
  {"type": "crystal_cluster", "x": 20.0, "y": 10.4, "color": "cyan", "size": 2.4, "count": 7},
  {"type": "trough", "x": 20.6, "y": 63.0, "angle": 90},
  {"type": "shed_roof", "x": 19.5, "y": 40.0, "z": 1.15, "angle": 0, "length": 3.0, "depth": 0.95, "rise": 0.3},
  {"type": "gable_roof", "x": 12.0, "y": 8.0, "z": 1.2, "length": 3.0, "width": 2.0, "rise": 0.8, "walls": 1.2},
  {"type": "gable_roof", "x": 6.0, "y": 8.0, "z": 1.0, "length": 2.6, "width": 2.4, "rise": 0.9, "walls": 1.0,
   "cover": "thatch", "chimney": 0.3, "plaster": "#e8dcc0"},
  {"type": "market_stand", "x": 15.5, "y": 33.6, "angle": 44},
  {"type": "well", "x": 16.5, "y": 10.5, "scale": 1.35},
  {"type": "crate", "x": 14.5, "y": 34.6, "angle": 12, "size": 0.34, "goods": "cabbages"},
  {"type": "arcade_cabinet", "x": 6.84, "y": 5.95, "angle": 180, "color": "#40e0ff", "seed": 1},
  {"type": "card_table", "x": 4.5, "y": 3.0},
  {"type": "saloon_chair", "x": 4.12, "y": 3.08, "angle": -8},
  {"type": "piano", "x": 6.8, "y": 1.12, "angle": 90},
  {"type": "portal", "x": 26.5, "y": 30.0, "angle": 90, "frame": "wood", "door": "#4a6a8a",
   "scene": "winter_woods.json", "to": {"x": 17.15, "y": 35.6, "angle": 270}},
  {"type": "screen", "x": 2.45, "y": 4.04, "z": 0.77, "angle": 90, "frame": "wall", "width": 0.7, "height": 0.38,
   "show": {"scene": "neon_street.json", "shot": 3}}
]
```
| field | meaning |
|---|---|
| `type` | a built-in object |
| `x`, `y` | where it stands; it rests on the floor there (a road sunk below the pavement, a raised platform) |
| `z` | lift it off that floor |
| `angle` | the way it faces, in compass degrees: 0 east, 90 south |
| `scale` | grow or shrink it |
| `paint` | a car's colour, `#rrggbb`. An arcade cabinet's body (default a dark violet), a vending machine's (default red), a market stand's awning and skirt, striped with cream (default red) |
| `lights` | a car: `true` turns its headlamps on, with light on the road ahead (otherwise only its tail lamps glow, faintly). The noodle stand and a crystal cluster: `false` leaves out the light they give; an arcade cabinet and a vending machine: `false` leaves out the glow they throw - give the scene a light of its own there instead |
| `rock` | rock's kind: `stone` (grey, lichen and moss, ferns and grass tufts on top - the default), `reef` (live rock under water: coralline crusts, algae, pits; corals and sea fans on top, lit from straight above), `sandstone` (red rock in beds, dry tufts), `canyon` (cliff rock: beds of red and pale stone by height, streaked dark with desert varnish - for a canyon's walls, with a small `trim`), `snow` (grey stone, snow lying on every face that is near level), `cave` (dark violet-grey, pitted, mushrooms and glowshrooms on top), `lumen` (cave rock grown with moss that glows, glowing ferns on top), `island` (grey and brown in beds, painted coarser - the rock under a sky island; a `keel`'s default), `menhir` (grey, lichened in pale patches, rain streaks, moss where it faces up - a `standing_stone`'s default), `basalt` (dark columnar rock, weathered pale on top, its joints across a `column` at heights of its own - for a causeway), `salt` (white grains, a little pitted - a `heap`'s default), `fieldstone` (small stones laid dry, every joint showing, each stone its own shade - a `well`'s default), `alpine` (grey rock in bands, meadow where it lies gently, snow above the `snowline` - a `mountain`'s default), `tropical` (green with jungle, grey-brown rock showing through - a tropical island's hill), `volcanic` (dark basalt, rust-red and ash-grey in patches - a volcano's) and `lava` (molten: bright glowing cracks between plates of dark crust; it glows). A crystal cluster's bed of rock (default `cave`) |
| `length` | a rock wall's length along the wall (default 4). A searchlight's beam: how far it reaches (default 12). A mountain: how far it is drawn out along its x into a ridge (default its `size`) |
| `lining` | a rock wall: map characters, instead of `x`, `y`, `angle` and `length` - a rock wall along every straight run of those cells' faces that look onto open ground, facing out from it (none where a shot's camera stands within its reach). `"lining": "#"` lines a whole cave |
| `height` | a rock wall: how tall its pieces are, `[lowest, highest]` (default `[0.5, 1.4]`), each piece its own height between them. A boulder: its height (default 0.55 of its size). A column: its height (default 1). A well: its wall's (default 0.32); a barrel: its own (default 0.33). A tower: its own (default 0.6); a city block: its towers', `[lowest, tallest]` (default `[0.08, 0.35]`, most of them nearer the lowest); a mountain: its own (default 7) |
| `depth` | how far a rock wall juts out from the wall (default 0.7). A beam: how deep it is (default 0.2). A tower: across, along its y (default its `width`) |
| `pieces` | how wide a rock wall's pieces are, `[narrowest, widest]` (default `[1.4, 2.8]`) |
| `trim` | the wavy trim along a rock wall's top, as a share of each piece's height (default 0.28) |
| `size` | how wide a boulder is (default 0.8). A crystal cluster: how tall its tallest crystal is (default 0.9). A crate: its length (default 0.24); a barrel: how wide it bulges (default 0.23); a card table: across its top (default 0.42); a well: across its wall (default 0.56). A mountain: across its foot (default 14); a village: across (default 2.4) |
| `count` | how many crystals a cluster has (default 5; 1 for a single crystal). A city block: its plots a side (default 2: four plots); a village: its cottages (default 16) |
| `spread` | how far a cluster's crystals stand from its middle (default 0.3 of its size) |
| `color` | crystals' colour: `cyan` (the default), `violet`, `rose`, `green`, `amber`, `ice`, `white` or `#rrggbb`. An arcade cabinet's colour, `#rrggbb`: its side art, the strip of light round its edge, its marquee (default pink). A searchlight's beam (default a cold white) or a ray (default an electric blue): `#rrggbb` or `[r, g, b]`. A cable's (default a dark steel) |
| `goods` | a market stand: the produce heaped on its three trays, a list from `apples`, `cabbages`, `loaves` and `potatoes` (default apples, cabbages, loaves), one of them also in the full crate by it. A crate: heap it with one and leave it open (otherwise it is nailed shut) |
| `game` | a card table: `false` for one with no game on it - no cards, no chips (default true) |
| `refract` | how far a crystal's facets bend the light through them, in units (default 0.16; 0 for plain glass) |
| `glow` | how much crystals glow (default 0.6); how much a screen shines (default 0.9) |
| `to` | a portal: where it comes out - `x`, `y`, `angle` (the way you face coming through) and `z` (its foot's height there) - in its `scene`, or in this one. The view through it is taken from where the camera would stand on the far side, so it lines up from any shot. A ray: the point it reaches, `[x, y, z]` in the scene's own units; a cable, the point it is slung to |
| `view` | a portal: a camera of its own instead of `to` (`x`, `y`, `angle` or `look_at`, `height`, and `scene`) - the portal then shows that one view whatever the shot, a window onto it |
| `scene` | a portal: the scene file it opens on (default this one), beside this one or a path |
| `show` | a screen: what it shows - `{"scene": "file.json", "shot": 2}` (shots counted from 1; leave out `scene` for this scene) or `{"camera": {...}}`, with a `resolution` (`[w, h]`, default the scene's). With nothing to show it shows snow. An arcade cabinet: another scene on its screen instead of a game |
| `shape` | a portal's opening: `rect` (the default), `arch` (a round head) or `round` |
| `frame` | a portal's frame (a `rect` one's): `wood` (in its `paint`, if any), `stone`, `marble` or `gold`; none by default. A screen's: `tv` (a boxy television on legs, rabbit ears), `monitor` (a bezel on a stand), `wall` (a flat screen hung on a wall) or none (a bare picture) |
| `door` | a portal: a door of this colour hung on its left post, swung open toward you by `swing` degrees (default 105) |
| `edge` | a portal: rims its opening with light of this colour, and a little light from it |
| `crt` | a screen: scanlines over its picture, its corners darkened like a tube's |
| `text` | a sign: its lettering (a newline starts another line) |
| `style` | a bridge's: `suspension` (the default) or `stone`. A sign's: `painted` (the default), `neon`, `plaque`, `carved`, `chalk`, `gilt` or `poster` (see Lettering). A tower's: `office` (the default: punched windows in pale frames), `glass` (a curtain wall), `apartment` (balconies), `brick` or `dark` (black stone and glass); a city block's: one of those or a list to draw from (default a mix) |
| `ground` | a sign: the colour of its board, plate or stone (`#rrggbb`) |
| `smooth` | a sign: big lettering, its steps rounded off |
| `base` | a crystal cluster: `false` leaves out its bed of rock. A column: the height of a wider plinth under it |
| `material` | a column or a beam: a kind of rock (`stone`, `sandstone`, `snow`, `cave`, ... - cut from solid stone as rock is), `ashlar` (pale dressed stone laid in courses - a column in drums), `iron_white` and `iron_green` (painted cast iron, for a glasshouse), `lime_white` and `lime_red` (whitewashed and red-painted masonry, smoothly round - or painted wood: a gate's posts), `lacquer_black` (black lacquer: a gate's top beam), `brass` (gone green with verdigris in patches: a gear's default), `marble` (cream-white, in drums, a golden patina in patches) or `wood` (weathered timber, its grain running along it, dark and grown over where it stands in water) |
| `sides` | a column's faces (default 8, an octagon) |
| `radius` | a column's radius at its foot, across the corners (default 0.12) |
| `top` | a column's radius at its head, as a share of its foot's (default 1: no taper). A mountain: cut flat at this share of its height - a mesa, a butte (default 1: a summit) |
| `capital` | the height of a wider block on a column's head |
| `flutes` | a column: that many sides, each hollowed into a flute that takes the light on one side and shadow on the other (20 for a Greek column) |
| `doric` | a column: `true` for the Doric order - no base, a capital of a cushion (the echinus) under a square slab (the abacus) |
| `fill` | any object: light from the sky and the ground on the faces the sun misses, as this many times the scene's `ambient` again (`1.0` doubles it there) - for an object backlit by a low sun |
| `teeth`, `spokes` | a gear: how many teeth round it (default 24) and spokes from its hub to its rim (default 6) - both even |
| `casts` | any object: `true` and it casts the sun's (or moon's) shadow - on the ground, on everything else and into the fog, where the gaps between such things become shafts of light - by the shape of its panels seen from above (its highest panel over each spot), never on itself. It stands in the light as if solid from the ground up to that panel, so give it to things that stand on the ground - stones, columns, a tower - and not to a beam or a roof held up over open space, which would shade everything under it as a wall would. Off by default: an object is lit, but stands in no light's way |
| `sink` | how far a column's foot goes into the ground or the water (default 0.02) |
| `broken` | a column: break it off ragged instead of a head - each corner stops up to this far below `height` and the break is rough. A ship's hull: how much of its starboard side is stove in (0-1) |
| `width` | a beam's width (default 0.2); its `depth` is how deep it is (default 0.2) and `length` how long, along the way it faces. A trough: how wide (default 0.5); a gabled roof: how wide across its eaves (default 2). A tower: along its x (default 0.3). A searchlight: its beam's width at the lamp (default 0.1), opening to six times that; a ray: where it leaves (default 0.03), twice that where it lands; a cable: how thick (default 0.008); a bridge: its road (default 0.22) |
| `rise` | a shed roof: how much higher its back edge is than its front (default 0.3); a gabled roof: its ridge's height over the eaves (default 0.8) |
| `overhang` | a gabled roof: how far its slopes reach past the walls (default 0.12), or `[at the eaves, at the ends]` |
| `walls` | a gabled roof: how tall the walls under it are (default 0: none) - a shed on the ground, or a building's body on a lower block |
| `inset` | a gabled roof: how far its walls stand back from its front end (default 0), or `[front, back, left, right]` from its ends and eaves |
| `cover` | a gabled roof (or a well's roof): `boards` (the default), `thatch` (reed ends in streaks of gold and brown, laid in courses, greener at the ridge), `tile` (clay tiles in staggered courses, each its own shade, lichen on a few), `slate` (dark blue-grey slates in narrow courses), `snow` (a roof under snow: soft drifts, the shingles showing at the ridge, a rounded lip at the eave) or `glass` (panes between white iron glazing bars, drawn as glass: the sky shows through, and the sun comes in under it as no cell is roofed) |
| `chimney` | a gabled roof: a brick chimney through the ridge, this far along it from the back (0-1), or a list of places for several; stouter on a bigger roof |
| `ends` | a gabled roof: its gable ends (and walls) of stone - a rock kind such as `ashlar` - instead of boards, or `glass` |
| `plaster` | a gabled roof: its walls and gable ends plaster of this colour (`#rrggbb`) instead of boards |
| `gauge` | rails: how far apart (default 0.24) |
| `roots` | a keel: `false` leaves out the roots trailing from its top |
| `piece` | a chess piece: `pawn` (the default), `rook`, `bishop`, `knight`, `queen` or `king` |
| `side` | a chess piece: `white` (the default) or `black` |
| `heel` | a ship's hull or a longship: how far it lists toward its starboard side, in degrees |
| `sail` | a longship: `false` furls its sail (the mast and yard stay) |
| `band` | a lighthouse: `false` leaves its tower all white |
| `lit` | a lighthouse or a stone lantern: `false` puts its lamp out. A piano: `true` lights the candles in its sconces, and they give a little light. A tower, a city block or a village: the share of its windows lit, glowing (default 0) - turned down by day when there is a `time`. A suspension bridge: `true` lights its lamps (on from dusk to dawn with a `time`) |
| `ore` | an ore cart: `false` leaves it empty |
| `seed` | another arrangement of the same rock; another game on an arcade cabinet's screen (a shooter, a maze chase or a racer) and another name on its marquee, another stock in a vending machine, another hand dealt on a card table; another tower, city block, village or mountain |
| `plants` | a rock wall: `false` leaves its tops bare. A boulder: how many plants grow on top (default 0) |
| `back` | a rock wall: `true` closes the back of each piece, for rock standing free of a wall |
| `setback` | a tower: from this share of its height up (0-1) its top steps in, to 0.7 of its width and depth |
| `antenna` | a tower: a mast this tall on its roof |
| `pad` | a tower: `true` puts a helicopter pad on its roof, a pale H in a ring |
| `built` | a city block: the share of its plots built on (default 1) |
| `elevation` | a searchlight: how far up its beam points, in degrees (default 55) |
| `opacity` | a searchlight's beam (default 0.45) or a ray (default 1): how strongly it glows over what is behind it |
| `sag` | a cable: how far its middle hangs below the straight line between its ends (default 3% of its length) |
| `snowline` | a mountain: where its snow begins, as a share of its height (default 0.62; 0 for none) - wandering up and down, lying wherever the slope is gentle enough, and everywhere near the summit |
| `ridges` | a mountain: how many spurs run down from its summit, with gullies between (default 4) |
| `church` | a village: `false` leaves out its church, for a hamlet. A village also takes `lit` (lamps in that share of its windows), `snow` (`true`: its roofs under snow) and `roof` (one cover for all its houses: `tile`, `slate`, `thatch` or `red`) |
| `deck` | a bridge: its road's height over the ground or the water (default 0.55 for a suspension bridge, 0.16 for stone) |
| `span` | a stone bridge: how far apart its arches stand (default 0.9) |
| `cliff` | a mountain: this share of it a sheer wall (0-0.95) - a slope of talus up to the wall's foot, the wall all but straight up to a flat top at `height` (or at `top`): a butte, a mesa, a spire |
| `crater` | a mountain: a crater sunk into its top, this share of its height deep - its top cut at 0.86 of its height unless `top` says - a volcano |
| `lava` | a mountain: lava running down its flanks from the top, glowing, narrow at the top and widening below - how many flows, down its gullies, or a list of the compass directions they run (`[80, 112, 150]`), to aim them at the camera; with a `crater` its floor is a lake of lava |
| `night`, `day` | any object: `true` and it is there only at night (sunset to sunrise) or only by day, when the scene or the shot has a `time` |

Built-in objects: `car` (a saloon 1.6 long, 0.6 wide and 0.47 tall - eye height is 0.5: its body a box whose sides are the car's outline, the hood and trunk lid flat across it, the roof, a windscreen, rear and side windows of glass with the seats, dashboard and steering wheel seen through them, four wheels set in under the body in dark wells, a floor pan and a soft shadow under it), `noodle_stand` (a street-food stand 1.4 wide and about 1.2 tall: a counter of lacquered boards under a sloping striped awning on four posts, a scalloped valance, split indigo curtains hanging from its front, a lit sign on the roof, red lanterns with their own light; bowls of noodles, a condiment tray, a stock pot with steam, bowls and bottles on its counter and stools before it, as billboards; it faces its customers. Put a `shopkeeper` behind its counter for a cook), `rock_wall` (rockwork along the foot of a wall: set it on the wall's foot facing into the room, `length` along it. Pieces side by side and overlapping, each in plan a rounded mass of a few broad faces jutting from the wall (now and then a spike or a notch), each piece its own height, with a trim of faces along its top cut by one long smooth wavy edge so no top is level, a flat top on each and plants growing along its rim), `boulder` (a low-poly mass of rock, every face a triangle: an irregular polygon at its foot, bulging a little, drawing in to its shoulders and up to a peak off its centre - solid and closed from every side, so it can be looked down on; the `boulder` prop in `sprites` is a flat billboard of one, fine in the distance), `column` (a column or a post: a prism of `sides` faces, tapering if `top` is under 1, with a plinth and a capital if asked, in stone or wood - pier piles, porch posts, the pillars of a nave; the `column` prop in `sprites` is a billboard of a fluted classical one), `beam` (a squared timber or a stone lintel lying level, its underside at the placement's `z`: a wall plate along a row of piers, a lintel over a door, a fallen timber on the floor), `trough` (a horse trough: an open box of weathered boards 1.6 long, 0.5 wide and 0.45 tall - `length`, `width`, `height` - still water in it a hand below the rim), `shed_roof` (a roof of boards sloping down to its front edge at the placement's `z`, `length` along it and reaching `depth` out the way it faces, its back edge `rise` higher - over a porch, a lean-to, an awning), `gable_roof` (a gabled roof of boards - or `thatch` or `tile` - its ridge `length` long the way it faces and `rise` over the eaves at `z`, `width` across, gable ends of upright boards, and with `walls` the walls under it: a shed, a barn, a cottage, the body of a building), `heap` (a heap of something loose - salt raked up to dry, sand, spoil: an irregular cone `size` across at its foot (default 0.5) and `height` tall (default 0.6 of its size), lumpy, drawing in to a blunt top a little off its centre; `rock` defaults to `salt`; give it `fill` under a high sun so its shaded side stays white), `gear` (a toothed wheel `size` across (default 2.0) and `depth` thick (default a tenth of its size), standing on its rim - lift it with `z` - its axle along x, so turn it with `angle` to face where it should, flat to a wall say; `teeth` round it (default 24) and `spokes` (default 6), both even; a rim, the spokes and a boss at its hub each a shade of their own, its teeth's sides standing out from its faces; of `material`, default `brass`), `standing_stone` (a rough slab of rock set on end, `size` across (default 1.0), `depth` through (default 0.45 of its size) and `height` tall (default 2.0): an irregular outline at its foot, its broad faces nearly flat, swelling and drawing in by uneven steps as it rises, leaning a few degrees, to a weathered top sloping down from one shoulder with the corners knocked off; `rock` defaults to `menhir`; its broad faces look along x, so turn them with `angle` - into a stone circle, say; low and wide it is a slab lying, an altar stone; `plants` sets tufts round its foot), `stone_lantern` (a stone lantern for a garden: a hexagonal foot, a round shaft, a platform, a firebox of four posts with the flame between them - `"lit": false` puts it out - a wide six-sided roof and a ball finial; `height` tall, default 1.1, of `material`, default `stone`), `lighthouse` (a round tower of whitewashed masonry `height` tall (default 8), `radius` at its foot (default 0.9), tapering to 0.7 of that, a red `band` round it (`false` for none), a gallery with an iron rail round its head, a lantern room of glass with the lamp lit in it - `"lit": false` puts it out - and a domed iron cap), `longship` (a longship: a long open hull of boards, its stem and stern curling up high, a mast with a yard and a square sail in red and cream stripes - `"sail": false` furls it - and round shields along both sides at the gunwale; `length` long the way it faces, default 7; `heel` lists it), `ship_hull` (a wooden ship's hull, open: `length` long the way it faces (the bow), `width` across, `depth` from keel to gunwale - a square stern, the sides curving out from the keel and in to a pointed bow whose stem sweeps up, planked along its length, ribs inside; `heel` lists it toward its starboard side in degrees, `broken` (0-1) staves in that much of that side; sink it into a sea floor with a negative `z`), `chess_piece` (a chess piece in 3D, turned in polished marble: `piece` a `pawn`, `rook`, `bishop`, `knight`, `queen` or `king`, `side` `white` or `black`, `height` tall (default 1) - smoothly shaded round, a sheen where it faces the light, veins in the stone; the rook's battlements, the queen's coronet and ball, the king's crown and cross, the knight's head carved side on and cut thick, facing the way the piece faces), `keel` (the rock under a floating island: an irregular ring `size` across at its top - set `z` at the foot of the island's `cliff` - drawing in by uneven steps to a ragged point `depth` below, crags hanging from its flanks, every face a triangle of rock lit from above, so its underside is in shade; `rock` defaults to `island`, grey and brown in beds; `"roots": false` leaves out the roots trailing from it), `rails` (a narrow track: two iron rails `length` long the way it faces, `gauge` apart (default 0.24), on wooden sleepers, their tops worn bright), `ore_cart` (a riveted iron tub on four small wheels set to the rails, its length the way it faces, ore heaped in it - `"ore": false` for none), `saloon_bar` (a saloon's counter of dark mahogany `length` long (default 3), 0.38 tall: raised panels between pilasters, a polished top, the bartender's shelves behind, a brass foot rail on brackets, bottles on it; it faces the drinkers), `sign` (lettering on a board in 3D - `text` in a `style` (see Lettering), its letters in `color`, the board in `ground` - `height` tall (default 0.22) and as wide as its lettering, `depth` thick (default 0.03; 0 for a flat sheet on a wall, seen only from the front), reading from the front and from behind; a `neon` one throws its light), `portal` (an opening `width` across (default 0.36) and `height` tall (default 0.92) through which another place shows - another scene, or another part of this one: the frame is drawn first from where the camera would stand beyond its exit (`to`), looking the way it would look, at the same size and lens, and the opening shows that, through this scene's own air - so a door in a desert opens on a snowy wood, and the view through it shifts as the camera moves; `view` shows one fixed view instead. A frame, a door swung open and a rim of light on request; it faces the side it opens toward and is not there from behind), `screen` (a picture of another shot - of another scene file or of this one, a security camera's view say - lit, on a television, a monitor, a screen on a wall, or bare: the shot is rendered once with its own effects and palette and laid on the screen keeping its pixels; `crt` adds scanlines), `market_stand` (a trestle table of boards 1.5 long with a striped skirt, under a striped awning on four poles sloping down to the front, a scalloped valance round it - striped in `paint` and cream; on the table three trays heaped with `goods` in 3D, every apple, cabbage, loaf or potato a round lump of its own; by it a crate full of the first and one nailed shut, and a sack; it faces its customers), `crate` (a wooden crate `size` long: planks behind a frame of battens, a brace across each side; with `goods` heaped full and open), `barrel` (a barrel of twelve oak staves bulging at its middle, each stave its own tone, four iron hoops, its lid sunk inside the rim), `well` (a village well: a round wall of fieldstones laid dry - `rock`, default `fieldstone` - capped by a coping of flat stones, the water dark far down the shaft; two oak posts on the coping carry a little gabled roof - `cover`, boards by default - and between them the windlass, its rope wound round it and hanging down the shaft, an iron crank at its front end; a bucket on the rim. The windlass runs the way it faces; scale it up a little to make it a scene's subject), `card_table` (a round card table: green baize in a rim of polished mahogany at a man's waist height, on a turned pedestal with a round foot; mid-game - unless `"game": false` - a hand dealt at each of four places, one fanned face up, the pot spilled in the middle, stacks of chips standing in 3D, a bottle and glass), `saloon_chair` (a bentwood chair: a round seat, four legs splayed out with a ring round them, the back a hoop with a smaller hoop inside, leaning back - a cut-out panel, see-through between its hoops; it faces the way whoever sits on it looks: turn it to its table), `piano` (an upright piano of polished mahogany, chest high: its sides carved, with the arms that hold the keyboard; the fall open on white keys and black in their twos and threes, a gilt maker's name over them, carved panels and the music open on the desk, candles in brass sconces at its corners - `"lit": true` burns them - a long panel below with two brass pedals, on turned legs; it faces the player: stand its back to a wall), `pew` (a chapel's pew of oak `length` long (default 1.2): a seat at the height of a knee, its back leaning a little back with a pale cap along its top and boarded down to the floor behind the seat, a carved end board at each end standing past it all round, scrolled over at the top; it faces the way its sitters look - set rows of them facing an altar, 0.4-0.6 apart), `arcade_cabinet` (an upright arcade cabinet as tall as a man, its sides cut to the cabinet's outline - the marquee jutting over the screen, the screen tilted back, the control panel standing out - in `paint`, side art of a ringed planet, stars and bands in its `color` and its edge lit round in that colour; the marquee lit from behind, a game glowing on the screen - a shooter, a maze chase or a racer, by `seed` - buttons on the controls and a joystick standing up from them (a billboard), a coin door with its inserts lit; it faces the player), `vending_machine` (a drinks machine a little taller than a man, a steel box in `paint`: its window let into its front, lit, on three shelves of cans and bottles with a glowing button under each behind clear plastic, a lit sign over it, a money panel beside it, the hatch at its foot let in under a smoked flap, a white wave and a maker's ring on its sides; it throws a cool light - `"lights": false` leaves it out), `searchlight` (a searchlight's beam: a cone of light from its lamp - on the ground, or on a roof with `z` - reaching `length` toward the compass `angle` it faces, `elevation` degrees up, opening as it goes and fading along its length: two glowing panels crossed along it, drawn as light over whatever is behind them, so it shows from any side; give the air a little fog and the shot a light `bloom` and it reads as a beam), `ray` (a ray of light, fire or energy from where it is placed - `z` the height it leaves at - straight to the point `to`: a monster's breath, a laser, a beam from a flying saucer, a helicopter's lamp held on something; drawn as a searchlight's beam is), `cable` (a cable slung from where it is placed - `z` the height it hangs from - to the point `to`, sagging `sag` below the straight line at its middle: power lines from pylon to pylon, a ropeway, a bridge's cables; dark, two thin strips crossed along it so it shows from any side), `bridge` (a bridge `length` long the way it faces, its road `width` across at `deck` height: `suspension` - two towers `height` tall carrying main cables from an anchorage at each end, sagging between them nearly to the road, hangers down to it, in `paint`, `lit` for lamps along its road and red lights on its towers - or `stone`, its road on round arches `span` apart, of `color` stone), `tower`, `city_block`, `village` and `mountain` (a building, a city's block of them, a village and a mountain at landscape scale - see Landscape scale), `crystal_cluster` (hexagonal crystals with pointed tips growing from a bed of rock, the tallest near upright and the rest leaning out; each carries a light of its colour. Every facet is its own panel with its own clarity - clear across the middle, milky toward the base, bright along the edges - and bends the light through it its own way: it shows one coherent piece of what is behind it, shifted by the way the facet is turned, its neighbours other pieces, the colours parting a little at the edges - so a crystal reads as cut stone from any side, and a crystal behind it shows through it bent).

- Shoot an object at an angle: its depth is the point of it. Objects light, occlude and mirror in wet floors like everything else; their billboards get contact shadows and their lights join the scene's. They do not cast shadows from the scene's lights.
- They render fast - a car is about seventy panels, each touching only its own patch of the screen.
- Rock is cut from one solid block of stone: every face samples the same 3D masses, cracks and chips at its own place in space, so the stone runs on round a corner while each face is lit by the way it faces - from the south-west and above, the same for every rock in a scene however it is turned (nearly straight down for `reef`), with the scene's own lights on top. Cutting it takes a moment (a few seconds for an aquarium's worth); a placement is cut once and kept, so the shots of a scene share it.
- A portal costs one more render for each one in sight, at the frame's own size. The view through it is taken from beyond its exit, so keep the ground behind the exit open (the camera there would see anything standing between it and the exit); seen from far off, the camera on the far side comes no further than 8 units back. A portal seen through a portal shows its misty face, and a screen within a screen shows snow.
- Crystals are drawn last, with glass, far to near, each facet over the frame as drawn so far: put bright things behind them - glowing plants, other crystals, a lit lake - and the bending shows; in front of a plain wall it is subtle. A shift that would land on something nearer than the crystal looks straight through instead.
- A rock wall stands in front of the wall it lines, so whatever is above its tops is the wall itself: give that wall something to read against - open water (`open_water` over `deep_water`), sky, a dark cave wall.

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
| `of` | a named set (`stones`, `snow`, `rubble`, `forest`, `undergrowth`, `autumn`, `desert`, `swamp`, `seabed`, `shore`, `litter`, `wreckage`, `cave`, `alien`, `derelict`, `jungle`, `beach`, `ruins`, and for a road's verges `verge`, `alpine`, `street` and `overgrown`), a sprite name, or a list. Repeats inside a set act as weights |
| `on` | legend characters to scatter on, as a string or list. Omit for every open cell |
| `density` | items per eligible cell. 0.3 is a light dusting, 1.5+ is a stony beach |
| `sizes` | size classes to draw from: a list, or a dict of weights. Classes are `tiny`, `small`, `medium`, `large`, `huge`, multiplying the prop's default height |
| `clump` | how hard the noise field biases placement. 0 is uniform, 1-2 gives drifts and clearings |
| `margin` | keep this far from wall faces (default 0.22) |
| `seed` | vary it to reshuffle a layer without touching the others |
| `scale` | multiplies every item's size (default 1): `0.09` shrinks trees to how they look from a giant's height (see Landscape scale) |

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

## Landscape scale

Make the world small and the camera's eye is a giant's: at landscape scale a map cell is about 100 m across, so the eye at its default `0.5` is fifty metres up, a ten-storey building comes to its knee, and a giant monster - the `kaiju`, 0.62 tall - stands in a city as a person stands in a room. Nothing in the renderer changes; what changes is what the cells and the objects are drawn as. The landscape examples are built this way: `kaiju_harbor.py` (a city at night, a kaiju wading in from the bay), `kaiju_country.py`, `volcano_island.py`, `mesa_desert.py`, `winter_valley.py`, `strait_bridge.py`, `archipelago.py` and `giant_valley.py` (a river valley at dawn), all in `examples/`.

- **The ground** is the landscape kit's floors, each seen from high up (assets.md, Textures): `city_street` has half a street along each edge of its cell, so a grid of them is a grid of streets, and `city_street_lit` is the same at night, its street lamps and the cars' lights glowing; `harbor_water`, `quay`, `container_yard`, `city_park`; `farmland` in six layouts (`farmland` to `farmland_f`) whose fields cross the cells' edges - mix them at random and they read as one countryside - `pasture`, `forest_canopy`, `pine_canopy` and `river_water`; country roads across them - `road_ew`, `road_ns` and a crossroads `road_x`, each over a field so a road runs through the farmland; `desert_floor` (three layouts, `_b` and `_c`, to mix) with a highway, `desert_road` (north-south) or `desert_road_ew`; winter's `snow_fields` (and `_b`), `snow_forest` and `frozen_lake` (and `_b`, `_c`); the tropics' `ocean`, `lagoon`, `reef_flat`, `white_sand` and `palm_canopy`. Keep the map open: a wall a unit tall is a cliff 100 m high.
- **The buildings are objects.** A `city_block` set at the middle of each `city_street` cell builds that block: `count` plots a side, each a `tower` with floors of windows in a `style`, its `height` drawn between `[lowest, tallest]` and its windows `lit` after dark. Set the heights by where a block stands - tall downtown, lower out from it, low warehouses along a waterfront - and the skyline makes itself. A `tower` alone stands for a landmark; a `village` is a cluster of cottages round a church; `mountain`s ring a valley, `length` drawing one out into a ridge, a few overlapping for a range, and `top` cutting one flat; with a `cliff` it stands on a slope of talus with sheer walls to its flat top - a butte, a mesa, a spire (`sandstone` or `canyon`, `"snowline": 0`, `"casts": true` for long shadows over a desert). A volcano is a `mountain` of `volcanic` rock with a `crater` and `lava` down its flanks: put large `blaze`s on its rim for lava fountaining over it, an `ash_plume` above (9 tall) with a light inside it, and `lava_flow` cells to carry its river on to the sea.
- **Light in the dark.** A `searchlight` sweeps its beam from a roof, and a `ray` reaches from one point to another: a helicopter's lamp held on the monster, its breath striking a tower. Give the air a thin `fog` with some `glow` and the shot a light `bloom` and they read as beams; mark them `"night": true` and the `time` puts them out by day. A line of `pylon`s carries `cable`s from arm to arm (the arms' tips are at heights 0.495, 0.458 and 0.43, reaching 0.07, 0.09 and 0.066 to either side; turn each pylon square to the line).
- **On the water**: `cargo_ship` (two hundred metres of it, 0.5 tall), `ferry`, `sailboat` - side on, bow to the left (`flip` to sail the other way); a `bridge` over a strait or a river.
- **The props**: `kaiju` (0.62 tall), `giant_moth` (its rival, wings spread twice its height, glowing at their rims), `kaiju_roar` (its head thrown back, its plates and throat glowing), `kaiju_wading` (roaring, the sea up to its thighs: stand it on a water cell), `tanks` and `tanks_firing`, `helicopter` and `jet` (float them with `z`), `blaze` and `smoke_plume` for a city on fire, and `pylon`. The other kits' props work too, shrunk with a scatter's `scale`: `{"of": "pine", "on": "w", "density": 3, "scale": 0.09}` stands small pines along a wood's edges.
- **The camera**: at its default eye a giant looks out over it all; a `height` of 0.6 to 4 is a view from the air; 0.012 to 0.035 is a person's eye on the quay or in a boat, and from there a kaiju towers. Over fields keep it above 0.07 - the ground is drawn to be seen from the air, and from a few metres up the nearest hedgerow becomes a wide stripe - and bring it close: a kaiju a few cells off is a speck. A long lens (`fov` 20-30) from a few cells away stacks it against a town and the hills, as the films do.
- **Distance and air**: the world runs many cells away, so give the scene a `max_distance` to match (48 for the city, 80 for the valley) and keep the `fog` thin (`density` 0.008 to 0.035) - air that would fill a room fills a valley. A point light's `radius` is in cells too: a fire's light of radius 1.5 lights the 150 m round it.

## Road scenes

A scene with a `road` instead of a `map` is drawn the way an arcade racer of the 80s drew its road. The road is a long run of short segments, each bending a little and rising or falling a little from the last; every segment ahead is projected onto the screen and filled row by row from the camera outward, so a crest hides the road beyond it until it comes back into view lower down, and every few segments the road and the ground shift a shade - the bands that read as speed. Props stand along it, scaled by their distance and hidden behind the crests in front of them. The frame then goes through the same post effects, weather, GUI and palette as any other (scripts/road.py). It is not only for racing: any way stretching ahead - a path through a wood, a trail into the jungle, a cobbled way through an enchanted forest, a road of marble across the clouds. Examples: `coast_road.py`, `night_highway.py`, `forest_path.py`, `jungle_trail.py`, `enchanted_path.py`, `sky_road.py`, `mountain_pass.py`, `canyon_run.py`, `island_run.py`, `canal_boat.py`, `neon_race.py`, `neon_avenue.py`, `roller_coaster.py`, `synthwave_drive.py`, `desert_highway.py`, `winter_road.py`, `mine_ride.py`, `space_trench.py`, `grand_prix.py`, `ice_road.py`, `desert_motel.py`, `sea_tunnel.py`, `viaduct_train.py`, `jungle_river.py`, `autumn_lane_road.py`, `rain_motorway.py`, `suspension_bridge.py`, `dark_road.py`, `rope_bridge.py`, `underworld_river.py`, `night_canal.py`, `ski_run.py`, `sky_lane.py`, `moon_drive.py`, `tulip_ride.py`, `night_runway.py`, `bayou_run.py`, `camel_caravan.py`, `candy_road.py`, `ghost_train.py`, `blossom_road.py`, `storm_chase.py`, `kelp_run.py`, `ring_station.py`, `sled_run.py`, `high_seas.py`, `safari_drive.py`, `close_encounter.py`, `night_fair.py`, `high_noon.py`, `storm_coast.py`, `volcano_road.py`, `metro_ride.py`, `drowned_city.py`, `log_flume.py`, `pilgrim_path.py`, `balloon_flight.py`, `hayride.py`, `sleigh_ride.py`, `hill_street.py`, `red_planet.py`, `ice_cave.py`, `dragon_flight.py`, `overgrown_highway.py`, `neon_canal.py`, `lantern_river.py`, `launch_day.py`, `airship_voyage.py`, `market_ride.py`, `night_pass.py`, `redwood_road.py`, `canyon_rapids.py`, `salt_mirror.py`, `asteroid_field.py`, `lost_valley.py`, `midnight_ride.py`, `fjord_voyage.py`, `torii_path.py`, `bamboo_path.py`, `lavender_ride.py`, `ghost_ship.py` and `cattle_drive.py` in `examples/`.

```json
{
  "road": {
    "sections": [[12, 0, 0], [60, -0.55, 1.2], [50, 0.7, -1.4], [120, 0, 0]],
    "width": 4.2, "lanes": 3, "surface": "asphalt",
    "rumble": {"width": 0.32, "colors": ["#ececec", "#c83024"]},
    "ground": {"left": "beach_sand", "right": [{"width": 5, "texture": "beach_sand"}, {"texture": "ocean"}]}
  },
  "roadside": [{"type": ["palm", "palm_lean"], "every": 7, "offset": 1.0, "scale": [3.0, 3.8], "flip": true}],
  "sprites": [{"type": "car_sedan", "at": 30, "x": 1.4}, {"type": "checkpoint", "at": 24, "x": 0}],
  "sky": "sunset",
  "lights": [{"type": "sun", "azimuth": 262, "elevation": 6}],
  "camera": {"at": 2, "x": 0, "height": 0.75, "pitch": 0.1, "vehicle": {"type": "sports_car", "ahead": 2.6}}
}
```

The road (`road`):

| key | default | meaning |
|---|---|---|
| `sections` | 400 straight | the road's run, one after another: `[length, curve, rise]` (or `{"length", "curve", "rise"}`) - `length` in units; `curve` how hard it bends, -1 to 1 for gentle to sharp, negative to the left, eased in over its first quarter and out over its last; `rise` how far it climbs over the section (negative falls), eased at both ends |
| `width` | `4` | across the road, in units (a unit is about 3 m: 4.2 holds three lanes, 1.5 is a path) |
| `surface` | `asphalt` | its texture - any texture, or `{"base", "tint"}`: `dirt`, `mud`, `cobble`, `marble`, `gravel`, `sea`, `water`...; a see-through texture leaves holes in the road, whatever lies beyond showing through (`coaster_track`: rails and ties, for a roller coaster over `void` ground); a texture that glows lights itself (`light_lane`, a lane of light) |
| `lanes`, `lines` | `2`, `#eeeeee` | lanes across it, the lines between them dashed on alternate bands in that colour (`false` for none) |
| `edges` | none | a solid line in this colour just inside each edge |
| `centre` | none | a solid centre line in this colour (a country road's yellow) |
| `rumble` | white and red, 0.3 wide | the kerb along both edges, `{"width", "colors": [light band, dark band]}`; `false` for none |
| `shoulder` | none | `{"width", "texture"}`: a strip beyond the kerb (`gravel`) |
| `ground` | `grass` | the ground either side: a texture, or bands out from the road's edge - `[{"width": 5, "texture": "beach_sand"}, {"texture": "ocean"}]`, the last running on - or `{"left": ..., "right": ...}`, each side its own - a band can also take a `tile` (units to its texture: 8 makes a lava field's cracks big) and a `reflect`, and a band of `"void"` ends the ground there (the sky, or the land `below`, beyond it - a ring habitat's floor between its rims); `"void"` for none at all, the sky carrying on below the road (a sea of cloud under it) |
| `edge` | none | for a path: `{"ragged": 0.2, "blend": 0.4}` - its edge wanders by `ragged` units and the ground mixes into it over a band `blend` wide |
| `stripe`, `bands` | `3`, `0.08` | segments to a band, and how much the bands shift the shade |
| `segment`, `distance` | `1`, `260` | a segment's length; how far ahead the road is drawn |
| `roofs` | none | `[[from, to, light]]`: stretches under a roof - a tunnel - where the sky's light falls to `light` (default 0.2) and only lamps light the road |
| `wet`, `ripple` | by the surface, `1` | how mirror-like the road is (0-1): a water `surface` (`sea`, `water`...) mirrors by its own nature; `wet` 0.3 makes a street after rain. `ripple` scales the waves that break up what it mirrors |
| `walls` | none | continuous walls along the road - guard rails, fences, hedges, cliffs, canyon walls, rows of buildings: see below |
| `ceiling` | none | `{"height", "texture", "tile", "from", "to", "light"}` (or a list): a ceiling over a stretch of road, `height` over it and following its rises - with walls either side, a tunnel you are inside. The stretch is also a roof (`light`, default 0.2) |
| `below` | none | `{"depth", "texture", "tile", "haze"}`: land far below a drop - past the edge of a `void` side, a flat plane `depth` units down; `texture` one, or bands out from the road's edge as the `ground` takes them (`forest_canopy`, `river_water`, `pasture`, `farmland`... - the landscape textures, drawn as seen from the air: a `tile` of about 33 is their own scale); `haze` scales the `fog` down there (0.5: thinner air). Props stand on it at a `z` of minus its `depth` - a castle in the valley, a ship on the sea - and are seen past the void side, nothing in front cutting them off. A texture that glows glows down there too, in the dark: `city_night`'s streets, `lava_field` |

`walls` stand along the road without a break, as a prop in a row cannot: each is a strip on every segment, `offset` out from the road's edge (negative is back over the road), `height` tall from `z` over it, `side` `both`, `left` or `right`, `from` and `to` along it, and a `texture` - tiled from the wall's foot every `tile` units (or `[along, up]`), so a band of strata stays level and a rail sits on the ground; a see-through texture keeps its holes. `ragged` lets the top wander by that much (a cliff's broken skyline, a canyon's rim; `seed` varies it), and `light` scales the light on it. The sun lights a wall by how squarely it faces it, so one side of a canyon is in shade. `blocks` cuts a wall into buildings that many units long, each its own height (`height` give or take `ragged`) with its facade starting at its own edge; `texture` a list gives each building one of them, and `gaps` (0-1) leaves that share of the blocks out - the alleys between. Built for it: `guard_rail` (a steel W-beam on posts, see-through: height 0.3, `"tile": [1, 0.3]`), `jersey_barrier` (a concrete safety barrier, height 0.27, `"tile": [1.3, 0.27]`), `cliff_face` (granite, `tile` 3.5) and `power_lines` (three wires sagging between poles: a wall 0.6 high at the crossarms, `"z": 2.6`, `"tile": [8, 0.6]`, with `power_pole`s every 8 from 0). Any texture serves: `rock` for a dry-stone wall, `hedge`, `picket`, `brick`, `slot_rock` or `sandstone` for a canyon, `tile_white` down a tunnel.

```json
"walls": [{"side": "left", "offset": 0.8, "height": 8, "texture": "cliff_face", "tile": 3.5, "ragged": 2.5},
          {"side": "right", "offset": 0.25, "height": 0.3, "texture": "guard_rail", "tile": [1, 0.3]}],
"ground": {"left": "gravel", "right": "void"},
"below": {"depth": 30, "texture": "farmland", "tile": 30}
```

Along it, `roadside` is rows of props: `type` a prop or a list to draw from; `every` units apart, or `density` (so many to a unit, anywhere in the band: a wood rather than an avenue); on `side` `both` (the default), `left`, `right` or `middle`; `offset` how far out from the road's edge, a number or `[from, to]` (negative is back onto the road; for `middle`, from the centre line); `scale` and `z` (or `[min, max]`: heights between the two, so wisps or islands float at many); `jitter` (moves each along the road, so a row is not a fence); `from` and `to` along the road; `flip` (mirrors those on the right), `tint`, `opacity`, `blend`, `view`, `fullbright`, `shadow`, `variant`, `seed`; `light` (one on each: `color`, `radius`, `intensity`, `z`, and `x` out over the road); and `clear` - a scattered row leaves this many units in front of every camera empty (default 3: a tree at the lens is a smear of magnified pixels). The scene's `sprites` stand where they are put: `at` how far along the road, `x` across it from the centre line (+ to the right), and the usual `z`, `scale`, `flip`, `tint`, `id` (for a bubble), `view` (`back` for a figure walking away), `light`. A `tint` paints a prop but not its lamps (a car's tail lights keep their red), unless the prop is all light - `fullbright` or `additive` - when it takes the tint whole (red `orb`s for bolts of fire). Across a road `width` w of n lanes, lane k (from 0 on the left) is centred at `x` = -w/2 + (k + 0.5) w / n. Props are billboards and the camera always faces along the road, so a sign, a banner or an arch over the road is just a prop at `x` 0 - and a row of arches down the `middle` every unit or so frames each other into a tunnel: `tunnel_ring`s behind a `tunnel_portal` with `roofs` over that stretch, `vault_arch`es for a vault, a `stone_arch` every 18 for a processional way.

`scatter` fills the verges as it fills a map's floor: what (`of` - a set, a prop or a list), `density` so many to a square unit, `sizes`, `clump` (drifts and clearings), `scale`, `seed` - and where, by the road: `side` `both` (the default), `left`, `right` or `road` (on it), `offset` the band (`[from, to]` out from the edge, default `[0, 2.5]`; for `road`, across from the centre line), `from` and `to` along it, `tint`; the few units in front of each camera stay `clear` (default 1.5). The sets `verge` (tufts, flowers, a stone, a bush), `alpine` (stones and boulders in thin grass), `street` (rubbish bags, litter, an old tyre, a cone) and `overgrown` (weeds up through the cracks: scatter it on the road, `side` `road`) are for roads, and every other set works too - `beach`, `forest`, `jungle`, `desert`, `snow`.

```json
"scatter": [{"of": "verge", "density": 1.2, "offset": [0, 3]},
            {"of": "street", "density": 0.06, "offset": [0, 1], "sizes": ["small", "medium"]}],
"decals":  [{"tex": "wear", "density": 0.05, "size": [0.5, 1.0]},
            {"tex": "zebra_crossing", "at": 12, "x": 0, "size": 4.2},
            {"tex": "tyre_marks", "at": 9, "x": 0.5, "size": 0.55}]
```

`decals` are marks lying on the road and the ground: one placed by `at` and `x`, or a row - `density` so many to a square unit, or one `every` so many units - on the road (`side` `road`, the default) or beside it (`both`, `left`, `right`, with `offset` out from the edge), gathering as `scatter` does (`clump`). `tex` is a decal, a list, or a set: `wear` (cracks, a patch, oil, a stain), `ruin` (potholes and puddles), `city` (oil, manholes, patches), `trail` (pebbles and leaves on a path), `fall` (leaf litter) and `drifts` (sand blown over a desert road). `size` is its width across the road (or `[min, max]`), its length along it following the image; `angle` turns it (a row's are turned at random, except marks that run with the road - skid marks, arrows, crossings, patches, manholes); `opacity`, `tint`, `flip`. A mark that glows (`rune_mark`) lights itself.

The camera of a road scene: `at` (how far along), `x` (across, from the centre line), `height` over the road there (0.75 behind a car, 0.5 on foot), `fov`, `pitch`, `yaw` (degrees off straight ahead) and `roll` (degrees: the frame tilted, as a racer leans the view into a bend - its vehicle stays level). It always faces along the road. `vehicle` stands a prop ahead of it, your own car: `{"type": "sports_car", "ahead": 2.6}`, with `x` across from the camera, `z` (a boat sits a little into the water), `scale`, `headlights` (true, or a colour) pooling light on the road ahead, and `beam` their strength; a `light` it carries (`color`, `radius`, `intensity`, `z`, `at` forward of it: a lantern at a boat's bow), and a `wake` (true, or `{"size", "opacity"}`) spread on the water behind it.

- **Water and wet roads mirror.** A road or a band of ground whose texture is water (`sea`, `water`, `river_water`, `shallows`, `wet_sand`... - their own `reflect`, or set `reflect` on a band) or a road made `wet` mirrors the sky about the horizon, and every prop and wall about its foot - a boat stands over its reflection, a lamp's light lies in the wet street - rippling (`ripple`). Under a roof it mirrors no sky, and the rain has not reached there: a `wet` road (or a band's `reflect`) is dry under a roof, while water mirrors by its nature even under a vault. Puddle decals mirror where they lie (`puddle_shine` 0.55, `puddle` 0.35, a row's own `reflect`). A sun low over the water lays its image on it.

- **Light.** The road runs north from the camera, so a `sun` or `moon` at `azimuth` 270 stands over the road straight ahead and 250 a little to its left; the disc is drawn in the sky, and its light falls on the ground by its height. Point lights stand by `at`, `x` and `z`. `ambient`, `fog`, `time`, `sky`, `skyline`, `sky_objects`, `post`, `overlays`, `sprite_defs`, `decal_defs`, `contact_shadows`, `resolution`, `supersample`, `seed` and `palette` work as in any scene; a map's own keys - `legend`, `objects`, `prefabs` - do not apply.
- **Length is cheap**: sections can run a kilometre; only `distance` ahead of the camera is drawn, and each shot stands where it likes along it.
- `render.py --map` draws a road scene from above - the road bending as its curves bend it, its props, the cameras - to check a layout.

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

Presets: `crt`, `crt_amber`, `crt_green`, `vhs`, `gameboy`, `cga`, `ega`, `nightvision`, `cinematic`, `horror`, `old_photo`, `dream`, `bloodmoon`, `hurt`, and the weather presets `storm`, `downpour`, `blizzard`, `autumn`, `sandstorm`, `ashfall`.

| effect | stage | parameters (defaults) |
|---|---|---|
| `grade` | world | `exposure` 1, `brightness` 0, `contrast` 1, `saturation` 1, `gamma` 1, `tint` [r,g,b], `lift` [r,g,b] |
| `bloom` | world | `source` "image" or "light" (see below), `threshold` 0.65 (0 for light), `strength` 0.6 (0.8 for light), `radius` 6 (4 for light), `spread` (0-1: the share of the glow in a wide halo), `color` |
| `dof` | world (lens) | depth of field: `focus` (a distance, a sprite's id, or left out to focus on the shot's `look_at`), `blur` 2.5 (the widest blur, in pixels), `range` 0.1 (0-1: widens the band that stays sharp) |
| `streaks` | world | light drawn out in thin lines from the brightest lights (see below): `points` 4 (a cross; 6 or 8 a star; 2 one horizontal line, the anamorphic look), `length` 12 (pixels), `strength` 0.6, `angle` 0, `count` 24 (lights), `white` 0.4, `color`, `sun` true |
| `flare` | world | a lens flare (see below): `strength` 0.6, `ghosts` 7, `halo` 0.25, `source` "sun" (a sun or moon in the frame) or "light" (the `sources` brightest lights in view) |
| `vignette` | world | `strength` 0.5, `radius` 0.7, `color` |
| `speed` | world | the frame streaked outward from the point it rushes toward - in a road scene its vanishing point, else `x`, `y` (0-1) - more toward its edges, the middle (`clear` 0.3) and a road shot's own `vehicle` left sharp: `strength` 0.4, `samples` 10 |
| `grain` | world | `amount` 0.06, `color` false |
| `rain` | world | `density` 1, `length` 7 (pixels, for a drop two units away), `angle` 12, `opacity` 0.35, `color` |
| `snow` | world | `count` 260, `size` 1, `wind` 0 (-1 to 1), `opacity` 0.85, `color` |
| `splashes` | world | rain landing on open ground: `density` 1, `opacity` 0.3, `color` |
| `embers` | world | glowing sparks drifting up: `count` 80, `size`, `glow`, `color` |
| `ash` | world | grey flakes drifting down: `count` 300, `wind` 0.2 |
| `leaves` | world | autumn leaves tumbling: `count` 120, `colors` |
| `fireflies` | world | little lights hanging low: `count` 40, `glow` 1.5, `color` |
| `spores` | world | glowing motes in the air: `count` 70, `colors`, `glow` |
| `dust` | world | wind-blown dust or sand: `density` 1, `wind` 1, `haze` 0.12, `color` |
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

**Bloom from light.** `"source": "image"` (the default) blooms whatever is bright in the finished frame, a pale wall as much as a lamp. `"source": "light"` blooms only what gives off light: emissive texels (lit windows, neon, screens, runes), glowing sprites and their flames, auras, a sun or moon disc - and their reflections in wet ground and water - read from an emission buffer the renderer keeps beside the frame. The glow is blurred in float at three widths, a tight core and a halo `spread` wide, so it can go far stronger without washing the walls out: `{"fx": "bloom", "source": "light", "strength": 2.4, "radius": 2.5, "spread": 0.6}` makes a neon street glow (see `examples/neon_street.py`). Fireflies, embers and spores give off light too, and so do a held lantern's or torch's flame and a muzzle flash: put the bloom after the weather in the list. For a night scene lit by lamps, windows and flames, `{"fx": "bloom", "source": "light", "strength": 1.4, "radius": 2.5, "spread": 0.5}` is a good start (see `examples/haunted_house.py`).

**Streaks and flares.** `streaks` draws light out in thin lines from the brightest compact lights in view - a lamp, a flame, a string of bulbs, a sign's hottest letters, not every glowing pixel, so a long neon tube does not smear into a sheet - and from a sun or moon in the frame, longest of all. `"points": 4` makes a little cross, the twinkle of a star filter on fairy lights (`{"fx": "streaks", "length": 9, "strength": 0.7}`); `6` a star on a low sun; `2` one long horizontal line through each light, the anamorphic look of a night street on film (`{"fx": "streaks", "points": 2, "length": 50, "strength": 0.4, "color": [0.55, 0.75, 1.3]}`). `flare` strings faint coloured ghosts - discs, a ring, the six-sided shape of the aperture - from the light through the middle of the frame and out the far side, with a pale ring round the light. It needs the sun or moon in the frame, and weakens as less of the disc shows: behind a wall or a tree there is none. Shoot into a low sun with the light off to one side for the longest flare: `[{"fx": "bloom", "source": "light", "strength": 1.0, "radius": 3}, {"fx": "streaks", "points": 6, "angle": 15}, {"fx": "flare"}]` (see the last shot of `examples/tropical_beach.py`).

**Depth of field.** `{"fx": "dof"}` keeps the frame sharp at the focus and softens it nearer and farther, as a lens wide open does: the blur grows with the difference between 1/distance and 1/focus, so it is greatest at the horizon and at half the focus distance. The background is gathered only from pixels at or beyond the focus, so a sharp subject never smears into it; a soft foreground spreads past its edges over what is behind. Lens effects run first, whatever their place in the list, and a held item (`viewmodel`) is drawn after them, so it stays sharp. Left without a `focus` it focuses where the shot looks (`look_at`); give a close shot of a character `"blur": 2-3` and the street behind melts into soft light (see the samurai in `examples/night_market.py` and the cat in `examples/neon_rooftop.py`). The palette is chosen from the frame as it would be without the lens, so a subject kept sharp keeps exactly the colours it has in a shot without depth of field.

**Weather.** The weather effects place their particles in the world in front of the camera. A drop or flake has a real depth: it hides behind anything nearer, shrinks and fades with distance, and fades into the scene's fog. Rain, snow, leaves, ash, dust and splashes never fall under a roof, so the inside of a doorway stays dry. Embers, fireflies and spores glow and go anywhere. Pair rain with `"wet"`, and with `splashes` for a downpour. A heavy shower reads better with a little `ground` fog and `glow`, so the lamps get halos.

## Render report

After each shot the CLI prints warnings, with a suggested fix, for problems that are easy to miss in a small preview:
- the frame is very dark, or its bottom is nearly black because no light reaches the floor near the camera;
- a large part of it is near white;
- part of it shows nothing (`"sky": null` with an open cell that has no `ceil`, or a gap in the walls);
- something within 0.6 units of the camera fills much of the frame;
- the camera is outside the map or inside a wall;
- the subject (a `look_at` sprite id, or a speech bubble's `anchor`) is behind the camera, hidden behind something, mostly hidden or cut off by the frame edge, under 14 pixels tall, or almost black.

Treat them like the unknown-key warnings: look at the frame and fix the cause, unless the darkness or the silhouette is the point.

## Known limits (it is a 2.5D raycaster)

- No slopes, cliffs or walkable upper floors. Low blocks give steps, daises, altars and platforms you look down onto (see Heights), and `drop` sinks water and shallow pits below z=0. The bank between two floor cells is approximated, so keep drops shallow. Fake real elevation by making the low area's surroundings tall walls (a cliff face) and placing the camera accordingly.
- One ceiling height per scene.
- Walls are whole grid cells; no thin walls, diagonal walls, arches or doors in the middle of a cell. A see-through cell (a fence, bars) is drawn as one flat grille at its near face.
- Reflections are screen-space and on floors only: a puddle can't mirror something that is off-screen, and walls are never mirrors.
- Sun and moon shadows come from walls only. Sprites cast no shadows beyond their contact shadow, and sunlight reaches a roofed cell only through an opening - a doorway, a see-through window, a hole in the roof, coloured glass.
- Floating islands are slabs: flat on top, with a cliff of fixed depth (2.5 units) and a ragged edge underneath, not a tapering rock. Sky objects are painted on the sky, so they have no parallax and light nothing.
- Sprites are static billboards that face the camera: characters have a front and a back, but no side view and no animation.
- Volumetric fog and weather are stills. A beam is lit air, and nothing moves.

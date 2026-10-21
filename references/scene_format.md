# Scene format reference

A scene is one JSON file, read as UTF-8. Only `map`, `legend` and `camera` are required. The built-in textures, props and characters are listed in `assets.md`, beside this file.

`render.py` prints `warning: unknown key ...` (with a did-you-mean) for any key it does not read - a misspelt key is otherwise silently ignored, so treat the warning as an error. JSON has no comments: prefix a key with `_` (`"_note": "..."`) to keep a note without a warning. `title`, `description` and `notes` are accepted as metadata and never read.

## Coordinates

- The map is a grid of characters. Row index is **y** (grows downward / south), column index is **x** (grows right / east).
- One cell is one world unit. Cell `(x, y)` spans `x..x+1`, `y..y+1`; its centre is `(x+0.5, y+0.5)`.
- Heights are in the same units. The default eye height is `0.5`, a standard room is `1.0` tall, and people are about `0.6` (so a waist-high rail is about 0.35).
- Camera `angle` is in degrees: **0 = east (+x), 90 = south (+y), 180 = west, 270 = north**. Sun and moon `azimuth` use the same compass.
- Rather than working out an angle, aim with `look_at`: a sprite `id`, `[x, y]`, or `[x, y, z]`. The last also sets `pitch` so that height sits mid-frame. Working out atan2 in your head is easy to get wrong by tens of degrees, so prefer `look_at`. A shot that sets its own `angle` (and no `look_at`) is aimed by that angle, not by a `look_at` it would otherwise inherit from `camera`.

## Top-level keys

| key | default | meaning |
|---|---|---|
| `resolution` | `[320, 200]` | internal framebuffer size. 320x200 is the VGA look; 400x250 for more detail |
| `scale` | `3` | nearest-neighbour upscale of the final PNG |
| `map` | required | list of equal-length strings |
| `legend` | required | char -> cell spec (see below) |
| `default` | `{"floor":"concrete_floor"}` | spec for chars missing from the legend |
| `ceiling_height` | `1.0` | z of every ceiling. Walls round a roofed room should be exactly this tall: a taller wall is drawn its full height, over the ceiling (give the outside of a building or a hill cells of their own) |
| `camera` | required | `{x, y, angle or look_at, fov=66, height=0.5, pitch=0, flashlight}` |
| `shots` | none | list of camera dicts; each inherits from `camera`. Renders `out_01.png`, `out_02.png`... |
| `sky` | `"night"` | `night`, `dusk`, `storm`, `day`, `overcast`, `blood`, `space`, `alien`, `dream`, `vector` (black to violet with a magenta glow at the horizon, for Vector World), `aurora` (a clear arctic night with the aurora across it, no two stretches alike: a great curtain of green rays low in the north, of every width and height, violet at their tips and fringed pink where it burns brightest, a pleated teal ribbon above it, red-tipped rays to the west and a faint arc high over them all; brightest due north, glowing so a light bloom takes them up and ice or still water doubles them), or `null` for fully indoor |
| `skyline` | none | distant silhouettes on the horizon: `mountains`, `hills`, `treeline`, `city` (see Sky and skyline) |
| `sky_objects` | `[]` | planets, ringed planets, moons, suns and stranger things painted into the sky (see Sky objects) |
| `wireframes` | `[]` | low-poly meshes drawn as lines of light in true 3D: cubes, polyhedra, mountains, racers (see Wireframes) |
| `ambient` | `[0.18,0.18,0.22]` | base light RGB. Night exterior ~0.13, dark interior ~0.05 |
| `lights` | `[]` | point lights, plus `sun` and `moon` directional lights (see Lights) |
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

A shot may also carry `"overrides": {...}` to change any top-level key (sky, fog, lights...) for that shot only. Besides the camera fields, a shot can set its own `overlays` and `post` (added to the scene's), `extra_sprites` (sprites that appear in that shot only - a figure that has just stepped into the doorway), `extra_wireframes` (the same for wireframes), and `flashlight`, `supersample`, `scanlines` and `seed`.

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
- Put the disc in frame by aiming the camera near `azimuth` with a low `elevation` (10-25). Match the sky preset: a sun in `day`, `dusk` or `overcast`, a moon in `night` or `storm`. Lower `ambient` when you add a moon, because it already lights the whole ground.
- A shot's `overrides` can swap the moon for a sun to show the same place by day (see `examples/winter_lake.py`).

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

Built-in decals: puddle, puddle_dark, puddle_shine, stain, stain_rust, splatter, splatter_dark, vines, moss_patch, crack, scorch, leak, cobweb, rune_mark, drain, contact_shadow, for the shore and the jungle pool: foam, foam_glow, starfish, shells, seaweed, lily_pads, and for hangars: pad_marking (a painted landing ring with an H, 4-6 units across) and hazard_stripe (a worn yellow-and-black band), and on the Moon rover_tracks (a rover's two tracks of chevron treads pressed into the dust), and for the doomed mode toxic_sign (a yellow warning triangle with a skull, TOXIC under it, for a wall), and for a saloon's walls wanted_poster (yellowed paper, WANTED over a sketched face, $500). `rune_mark` and `foam_glow` are emissive, so they glow regardless of lighting. Seen from eye height a floor decal is foreshortened almost to a line, so `foam` reads from a raised camera or close up; for surf seen from a standing height use the `surf` props. `contact_shadow` is the soft disc used for contact shadows, which you can also stamp by hand (under a prop hanging low over the floor, say). The puddles reflect by default (`puddle_shine` 0.55, `puddle` 0.35, `puddle_dark` 0.25), so a lamp post shows in the wet patch at its foot.

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
- `back` (optional) is the same figure from behind, as another grid of the same size, written the same way as `pixels`. It shows when the sprite's `facing` points away from the camera. Every built-in character has one. Turn the face to hair or hood, and the front details (buttons, a badge, a held book) to plain cloth.
- 16x32 is the house size for people (about 3x upscaled at conversation distance). Props can be any size; keep rows equal length.
- Shade with 2-3 tones per material (shadow, base, highlight) and a dark outline colour for readability.

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
  {"type": "market_stand", "x": 15.5, "y": 33.6, "angle": 44}
]
```
| field | meaning |
|---|---|
| `type` | a built-in object |
| `x`, `y` | where it stands; it rests on the floor there (a road sunk below the pavement, a raised platform) |
| `z` | lift it off that floor |
| `angle` | the way it faces, in compass degrees: 0 east, 90 south |
| `scale` | grow or shrink it |
| `paint` | a car's colour, `#rrggbb` |
| `lights` | a car: `true` turns its headlamps on, with light on the road ahead (otherwise only its tail lamps glow, faintly). The noodle stand and a crystal cluster: `false` leaves out the light they give |
| `rock` | rock's kind: `stone` (grey, lichen and moss, ferns and grass tufts on top - the default), `reef` (live rock under water: coralline crusts, algae, pits; corals and sea fans on top, lit from straight above), `sandstone` (red rock in beds, dry tufts), `canyon` (cliff rock: beds of red and pale stone by height, streaked dark with desert varnish - for a canyon's walls, with a small `trim`), `snow` (grey stone, snow lying on every face that is near level), `cave` (dark violet-grey, pitted, mushrooms and glowshrooms on top), `lumen` (cave rock grown with moss that glows, glowing ferns on top), `island` (grey and brown in beds, painted coarser - the rock under a sky island; a `keel`'s default). A crystal cluster's bed of rock (default `cave`) |
| `length` | a rock wall's length along the wall (default 4) |
| `lining` | a rock wall: map characters, instead of `x`, `y`, `angle` and `length` - a rock wall along every straight run of those cells' faces that look onto open ground, facing out from it (none where a shot's camera stands within its reach). `"lining": "#"` lines a whole cave |
| `height` | a rock wall: how tall its pieces are, `[lowest, highest]` (default `[0.5, 1.4]`), each piece its own height between them. A boulder: its height (default 0.55 of its size). A column: its height (default 1) |
| `depth` | how far a rock wall juts out from the wall (default 0.7). A beam: how deep it is (default 0.2) |
| `pieces` | how wide a rock wall's pieces are, `[narrowest, widest]` (default `[1.4, 2.8]`) |
| `trim` | the wavy trim along a rock wall's top, as a share of each piece's height (default 0.28) |
| `size` | how wide a boulder is (default 0.8). A crystal cluster: how tall its tallest crystal is (default 0.9) |
| `count` | how many crystals a cluster has (default 5; 1 for a single crystal) |
| `spread` | how far a cluster's crystals stand from its middle (default 0.3 of its size) |
| `color` | crystals' colour: `cyan` (the default), `violet`, `rose`, `green`, `amber`, `ice`, `white` or `#rrggbb` |
| `refract` | how far a crystal's facets bend the light through them, in units (default 0.16; 0 for plain glass) |
| `glow` | how much crystals glow (default 0.6) |
| `base` | a crystal cluster: `false` leaves out its bed of rock. A column: the height of a wider plinth under it |
| `material` | a column or a beam: a kind of rock (`stone`, `sandstone`, `snow`, `cave`, ... - cut from solid stone as rock is), `ashlar` (pale dressed stone laid in courses - a column in drums), `marble` (cream-white, in drums, a golden patina in patches) or `wood` (weathered timber, its grain running along it, dark and grown over where it stands in water) |
| `sides` | a column's faces (default 8, an octagon) |
| `radius` | a column's radius at its foot, across the corners (default 0.12) |
| `top` | a column's radius at its head, as a share of its foot's (default 1: no taper) |
| `capital` | the height of a wider block on a column's head |
| `flutes` | a column: that many sides, each hollowed into a flute that takes the light on one side and shadow on the other (20 for a Greek column) |
| `doric` | a column: `true` for the Doric order - no base, a capital of a cushion (the echinus) under a square slab (the abacus) |
| `fill` | any object: light from the sky and the ground on the faces the sun misses, as this many times the scene's `ambient` again (`1.0` doubles it there) - for an object backlit by a low sun |
| `sink` | how far a column's foot goes into the ground or the water (default 0.02) |
| `broken` | a column: break it off ragged instead of a head - each corner stops up to this far below `height` and the break is rough |
| `width` | a beam's width (default 0.2); its `depth` is how deep it is (default 0.2) and `length` how long, along the way it faces. A trough: how wide (default 0.5); a gabled roof: how wide across its eaves (default 2) |
| `rise` | a shed roof: how much higher its back edge is than its front (default 0.3); a gabled roof: its ridge's height over the eaves (default 0.8) |
| `overhang` | a gabled roof: how far its slopes reach past the walls (default 0.12), or `[at the eaves, at the ends]` |
| `walls` | a gabled roof: how tall the walls under it are (default 0: none) - a shed on the ground, or a building's body on a lower block |
| `inset` | a gabled roof: how far its walls stand back from its front end (default 0), or `[front, back, left, right]` from its ends and eaves |
| `cover` | a gabled roof: `boards` (the default), `thatch` (reed ends in streaks of gold and brown, laid in courses, greener at the ridge) or `tile` (clay tiles in staggered courses, each its own shade, lichen on a few) |
| `chimney` | a gabled roof: a brick chimney through the ridge, this far along it from the back (0-1) |
| `plaster` | a gabled roof: its walls and gable ends plaster of this colour (`#rrggbb`) instead of boards |
| `gauge` | rails: how far apart (default 0.24) |
| `roots` | a keel: `false` leaves out the roots trailing from its top |
| `piece` | a chess piece: `pawn` (the default), `rook`, `bishop`, `knight`, `queen` or `king` |
| `side` | a chess piece: `white` (the default) or `black` |
| `ore` | an ore cart: `false` leaves it empty |
| `seed` | another arrangement of the same rock |
| `plants` | a rock wall: `false` leaves its tops bare. A boulder: how many plants grow on top (default 0) |
| `back` | a rock wall: `true` closes the back of each piece, for rock standing free of a wall |

Built-in objects: `car` (a saloon 1.6 long, 0.6 wide and 0.47 tall - eye height is 0.5: its body a box whose sides are the car's outline, the hood and trunk lid flat across it, the roof, a windscreen, rear and side windows of glass with the seats, dashboard and steering wheel seen through them, four wheels set in under the body in dark wells, a floor pan and a soft shadow under it), `noodle_stand` (a street-food stand 1.4 wide and about 1.2 tall: a counter of lacquered boards under a sloping striped awning on four posts, a scalloped valance, split indigo curtains hanging from its front, a lit sign on the roof, red lanterns with their own light; bowls of noodles, a condiment tray, a stock pot with steam, bowls and bottles on its counter and stools before it, as billboards; it faces its customers. Put a `shopkeeper` behind its counter for a cook), `rock_wall` (rockwork along the foot of a wall: set it on the wall's foot facing into the room, `length` along it. Pieces side by side and overlapping, each in plan a rounded mass of a few broad faces jutting from the wall (now and then a spike or a notch), each piece its own height, with a trim of faces along its top cut by one long smooth wavy edge so no top is level, a flat top on each and plants growing along its rim), `boulder` (a low-poly mass of rock, every face a triangle: an irregular polygon at its foot, bulging a little, drawing in to its shoulders and up to a peak off its centre - solid and closed from every side, so it can be looked down on; the `boulder` prop in `sprites` is a flat billboard of one, fine in the distance), `column` (a column or a post: a prism of `sides` faces, tapering if `top` is under 1, with a plinth and a capital if asked, in stone or wood - pier piles, porch posts, the pillars of a nave; the `column` prop in `sprites` is a billboard of a fluted classical one), `beam` (a squared timber or a stone lintel lying level, its underside at the placement's `z`: a wall plate along a row of piers, a lintel over a door, a fallen timber on the floor), `trough` (a horse trough: an open box of weathered boards 1.6 long, 0.5 wide and 0.45 tall - `length`, `width`, `height` - still water in it a hand below the rim), `shed_roof` (a roof of boards sloping down to its front edge at the placement's `z`, `length` along it and reaching `depth` out the way it faces, its back edge `rise` higher - over a porch, a lean-to, an awning), `gable_roof` (a gabled roof of boards - or `thatch` or `tile` - its ridge `length` long the way it faces and `rise` over the eaves at `z`, `width` across, gable ends of upright boards, and with `walls` the walls under it: a shed, a barn, a cottage, the body of a building), `chess_piece` (a chess piece in 3D, turned in polished marble: `piece` a `pawn`, `rook`, `bishop`, `knight`, `queen` or `king`, `side` `white` or `black`, `height` tall (default 1) - smoothly shaded round, a sheen where it faces the light, veins in the stone; the rook's battlements, the queen's coronet and ball, the king's crown and cross, the knight's head carved side on and cut thick, facing the way the piece faces), `keel` (the rock under a floating island: an irregular ring `size` across at its top - set `z` at the foot of the island's `cliff` - drawing in by uneven steps to a ragged point `depth` below, crags hanging from its flanks, every face a triangle of rock lit from above, so its underside is in shade; `rock` defaults to `island`, grey and brown in beds; `"roots": false` leaves out the roots trailing from it), `rails` (a narrow track: two iron rails `length` long the way it faces, `gauge` apart (default 0.24), on wooden sleepers, their tops worn bright), `ore_cart` (a riveted iron tub on four small wheels set to the rails, its length the way it faces, ore heaped in it - `"ore": false` for none), `saloon_bar` (a saloon's counter of dark mahogany `length` long (default 3), 0.38 tall: raised panels between pilasters, a polished top, the bartender's shelves behind, a brass foot rail on brackets, bottles on it; it faces the drinkers), `market_stand` (a trestle table of boards 1.5 long with a striped skirt, under a striped awning on four poles sloping down to the front, a scalloped valance round it; apples, cabbages and loaves heaped on the table and crates by it, as billboards; it faces its customers), `crystal_cluster` (hexagonal crystals with pointed tips growing from a bed of rock, the tallest near upright and the rest leaning out; each carries a light of its colour. Every facet is its own panel with its own clarity - clear across the middle, milky toward the base, bright along the edges - and bends the light through it its own way: it shows one coherent piece of what is behind it, shifted by the way the facet is turned, its neighbours other pieces, the colours parting a little at the edges - so a crystal reads as cut stone from any side, and a crystal behind it shows through it bent).

- Shoot an object at an angle: its depth is the point of it. Objects light, occlude and mirror in wet floors like everything else; their billboards get contact shadows and their lights join the scene's. They do not cast shadows from the scene's lights.
- They render fast - a car is about seventy panels, each touching only its own patch of the screen.
- Rock is cut from one solid block of stone: every face samples the same 3D masses, cracks and chips at its own place in space, so the stone runs on round a corner while each face is lit by the way it faces - from the south-west and above, the same for every rock in a scene however it is turned (nearly straight down for `reef`), with the scene's own lights on top. Cutting it takes a moment (a few seconds for an aquarium's worth); a placement is cut once and kept, so the shots of a scene share it.
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
| `of` | a named set (`stones`, `snow`, `rubble`, `forest`, `undergrowth`, `autumn`, `desert`, `swamp`, `seabed`, `shore`, `litter`, `wreckage`, `cave`, `alien`, `derelict`, `jungle`, `beach`, `ruins`), a sprite name, or a list. Repeats inside a set act as weights |
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

Presets: `crt`, `crt_amber`, `crt_green`, `vhs`, `gameboy`, `cga`, `ega`, `nightvision`, `cinematic`, `horror`, `old_photo`, `dream`, `bloodmoon`, `hurt`, and the weather presets `storm`, `downpour`, `blizzard`, `autumn`, `sandstorm`, `ashfall`.

| effect | stage | parameters (defaults) |
|---|---|---|
| `grade` | world | `exposure` 1, `brightness` 0, `contrast` 1, `saturation` 1, `gamma` 1, `tint` [r,g,b], `lift` [r,g,b] |
| `bloom` | world | `source` "image" or "light" (see below), `threshold` 0.65 (0 for light), `strength` 0.6 (0.8 for light), `radius` 6 (4 for light), `spread` (0-1: the share of the glow in a wide halo), `color` |
| `dof` | world (lens) | depth of field: `focus` (a distance, a sprite's id, or left out to focus on the shot's `look_at`), `blur` 2.5 (the widest blur, in pixels), `range` 0.1 (0-1: widens the band that stays sharp) |
| `streaks` | world | light drawn out in thin lines from the brightest lights (see below): `points` 4 (a cross; 6 or 8 a star; 2 one horizontal line, the anamorphic look), `length` 12 (pixels), `strength` 0.6, `angle` 0, `count` 24 (lights), `white` 0.4, `color`, `sun` true |
| `flare` | world | a lens flare (see below): `strength` 0.6, `ghosts` 7, `halo` 0.25, `source` "sun" (a sun or moon in the frame) or "light" (the `sources` brightest lights in view) |
| `vignette` | world | `strength` 0.5, `radius` 0.7, `color` |
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
- Sun and moon shadows come from walls only. Sprites cast no shadows beyond their contact shadow, and sunlight reaches a roofed cell only through an opening - a doorway, a see-through window, a hole in the roof.
- Floating islands are slabs: flat on top, with a cliff of fixed depth (2.5 units) and a ragged edge underneath, not a tapering rock. Sky objects are painted on the sky, so they have no parallax and light nothing.
- Sprites are static billboards that face the camera: characters have a front and a back, but no side view and no animation.
- Volumetric fog and weather are stills. A beam is lit air, and nothing moves.

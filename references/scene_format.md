# Scene format reference

A scene is one JSON file, read as UTF-8. Only `map`, `legend` and `camera` are required.

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
| `ceiling_height` | `1.0` | z of every ceiling. Walls in roofed areas should be at least this tall |
| `camera` | required | `{x, y, angle or look_at, fov=66, height=0.5, pitch=0, flashlight}` |
| `shots` | none | list of camera dicts; each inherits from `camera`. Renders `out_01.png`, `out_02.png`... |
| `sky` | `"night"` | `night`, `dusk`, `storm`, `day`, `overcast`, `blood`, `space`, `alien`, `dream`, or `null` for fully indoor |
| `skyline` | none | distant silhouettes on the horizon: `mountains`, `hills`, `treeline`, `city` (see Sky and skyline) |
| `sky_objects` | `[]` | planets, ringed planets, moons, suns and stranger things painted into the sky (see Sky objects) |
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
```
| field | default | meaning |
|---|---|---|
| `set` | - | a fringe set: `jungle` (cards `jungle_card_4` .. `jungle_card_1`, back to front: rainforest trees, palms, tree ferns, bushes) `forest` (`forest_card_4` .. `forest_card_1`: spruce, oak and birch, then young trees, then bushes, ferns and grass) `forest_autumn` (`autumn_card_4` .. `autumn_card_1`: the same wood in October - oak, birch and bush turned orange, gold and rust, the spruce among them still green), `forest_snow` (`winter_card_4` .. `winter_card_1`: the wood in winter - snowy spruce, bare oak and birch with snow along their limbs, bushes buried in it), `swamp` (`swamp_card_3` .. `swamp_card_1`: bald cypresses hung with moss, then young ones, then cattails and knees at the water's edge) or `kelp` (`kelp_card_2`, `kelp_card_1`: a dense stand of giant kelp, then a few stalks) |
| `cards` | - | instead of a set: your own sprite names, back to front (a PNG or a `sprite_defs` card works) |
| `depth` | `1.0` | how far out from the wall the layers spread, in cells |
| `height` | `1.0` | a multiplier on the cards' heights |
| `seed` | `0` | reshuffles where along its card each run starts |

- The trees on the back cards rise to 4.6 units. Keep a `forest` wall lower than that (2-2.6) so the tops of the trees make the skyline, not the flat top of the wall.
- Plan a ring of open ground a cell deep in front of the walls for the fringe to stand in: make the solid part of the forest a cell smaller than the forest should look. A path through a jungle wants to be two cells wider than it should look.
- Each straight run of faces gets one card per layer; the layers wrap round outside corners and stop short in inside ones, so each follows the outline at its own distance. A card that would pass through a camera position is left out.
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
| `style` | `brick` | `brick` (red and brown, painted sash windows), `sooty` (soot-blackened tenements, dark frames), `plaster` (washed colours), `neon` (dark concrete hung with glowing signs, blade signs standing out over the street on cards of their own, roller shutters half down over the shops, rooms lit pink, blue and green), `timber` (a village: limewashed and ochre plaster between dark oak posts, rails and braces, leaded casements, plank doors, and a roof standing on every house - a gable end facing the street, or the slope of thatch or tiles set back behind the eave, some with a chimney; give it `storeys` [1, 2] and narrow `widths` [2, 3], and keep the block behind it no taller than one storey), `western` (a frontier main street: clapboard in faded paint peeling to grey wood, a false front standing up over every building's roofline - square, stepped, curved or pedimented - with its sign painted on it, no two alike along a street and a saloon among them, the saloon with batwing doors and a lamp-lit room behind; and the posts and fascia of a covered boardwalk standing `porch` units out (1 by default): make that a cell of `planks` a step high with a `ceil`, under a low `ceiling_height` such as 1.3, and it becomes the porch roof), or a list to mix them building by building |
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
- The same goes for a roof: a camera in a block 5 tall with `height` 5.5 stands on top of it, and props up there take `z` 5. A cell is nearly three metres, so a parapet one cell deep is a wide deck: to look down into the street stand at its outer edge (or on it). Point lights fade with height above about 1.4, so on a high roof lean on ambient light, emissive props and a brighter `tint` for the people. See `examples/neon_rooftop.py`.

### Void floors: space, open air, floating islands

A cell with `"floor": "void"` has no ground. Where you would see its floor you see sky instead: the panorama carries on below the horizon, as stars all the way round under the `space` sky, and as a sea of cloud far beneath under any other.

```json
" ": {"floor": "void"},
"g": {"floor": "grass", "side": "rock"},
"V": {"wall": ["viewport", "viewport"], "h": 2, "floor": "obsidian", "ceil": "panel"}
```
- Fill a map with void and draw islands on it for a world adrift in the sky. Each island's edge drops away as a cliff with a ragged underside, textured with the cell's `side` (or its floor). Walls standing at the brink sit on that cliff too.
- Put void outside a `viewport` wall for a spaceship or station: looking out, space surrounds you, above the horizon and below it.
- Surround the islands with void all the way to the map edge. The ground past the edge carries on as the edge cells, so a map whose edge is grass is a continent, not an island.
- Sprites over a void have nothing to stand on: their `z` is simply their height. Scatter, grime and contact shadows skip void cells by themselves.
- A void cell can still have a `ceil`, but it rarely makes sense. A balcony or a ship's hull wants its own open cells or walls between the void and the roof.

## Textures

Any texture slot accepts:
- a built-in name (run `python scripts/assets.py catalog.png` to see them all),
- a PNG path (resized to 64x64, nearest). Relative paths are looked up beside the scene file first, then in the working directory - the same goes for PNG sprites, decals and TTF fonts,
- `{"base": "brick", "tint": [0.8, 0.9, 1.1], "brightness": 0.7}` for a recoloured variant.

Built-ins with emissive texels (glow regardless of lighting): `water_surface` (the sea's surface from below), `window_lit`, `window_lit_plaster`, `window_teal`, `runes`, `stained_glass`, `hull_lit` and `hull_red` (a light strip at eye height), `tech_panel` (readouts), `server` (status lights), `blast_door` (a warning light), `grid_floor` (glowing grid lines), `alien_rock` (glowing veins), `fireplace` (the fire), `star_chart` (the stars), `canopy` (light through the leaves, and sky in the gaps), `temple_door` (something burning inside), `conduit` (status lights on a junction box), `screen_wall` (a wall of monitors), `tunnel_roof` (the view up through an aquarium tunnel's roof: deep water, the bright surface far above, a seam of the acrylic at every tile), `jelly_backdrop` (the glowing blue back wall of a jelly tank), `bar_shelves` (bottles on two shelves, each lit from below, for the wall behind a bar), `capsules` and `capsules_lit` (a capsule hotel's berths, four to a unit, each with a glowing number plate and lamp-lit bedding, a drawn blind, a screen's glow or dark inside; `capsules_lit` has more of them occupied - alternate the two cell by cell), `nukage` (toxic slime in slow green swirls: sink it with `drop` and it lights the room from below). Their dark counterparts are `window_dark`, `window_dark_plaster`.

See-through built-ins (see See-through walls): `bars`, `fence_iron`, `chainlink`, `railing`, `picket`, `portcullis`, `window_broken`, `lattice`, `viewport` (an observation window from just above the floor to just under the top: stack two for a glass wall two storeys tall), `tank_window` (a viewing window into an aquarium tank, in a deep frame of dark steel with rounded corners; stand a `glass_pane` just behind it and stack plain wall above), `green_window` (the doomed mode's green plating with a window cut through it), `roof_comb` (a temple's stone lattice crest), and the Doric colonnade: `colonnade` (one fluted column to a cell), `colonnade_top` (capital, architrave, triglyph frieze and cornice) and `colonnade_broken` (shafts snapped off at different heights). Stack them per storey: `["colonnade", "colonnade", "colonnade_top"]` with `h` 3 is an intact colonnade, `["colonnade", "colonnade_broken"]` a ruined one. Seen square-on a colonnade is convincing; seen along its length the columns are flat and thin, so for a row you look down, use `column` props instead. A PNG with transparent pixels behaves the same way.

The built-ins also include gothic windows in pale stone, see-through between their leads (`tall_window`, ending in `tall_window_top`), castle and dungeon stone (`castle`, `flagstone`, `slime_brick`, `door_wood`), winter ground (`snow`, drifts with their lee sides in blue shadow; `ice`, `snow_rock`; `forest_deep_snow`, the deep wood with snow on its boughs, behind a `forest_snow` fringe), the desert (`sandstone` - beds of red, orange and cream standing out as ledges, streaked with varnish; stack it with bands of `sandstone_pale` for a canyon wall - `slot_rock`, the swept curves of a slot canyon, `desert_wash`, the sand and pebbles of a dry wash, and for a cliff dwelling `pueblo_stone` and `pueblo_door`, a T-shaped doorway), the Moon (`regolith`, grey dust pocked with craters), the sea floor (`seabed`, rippled sand under a net of caustic light; `water_surface`, the surface seen from below, glowing, for the roof of an underwater room; `reef_wall`, the rockwork at the back of a reef tank - live rock, coralline, coral heads, algae and polyps), a 1993 shooter's base (`hex_floor`, brown hexagonal tiles; `green_tech`, green plating in vertical strakes; `green_trim`, the same under a band of brown metal with a row of pale teeth, to stack storey on storey; `tech_ceiling`, ceiling tiles in a grid; `slime_edge`, brown plates stained green, for the `side` of a slime pit), the swamp (`swamp_water`, black water skinned with duckweed that mirrors; sink it with `drop` and give it a `bog` `side`; `bog`, peat and sphagnum; `swamp_deep`, grey trunks in the murk hung with moss, for the walls behind a `swamp` fringe), the wood in autumn (`forest_deep_autumn`, the dark between the trunks hung with turned leaves, for the walls behind a `forest_autumn` fringe, and `leaves_fallen` underfoot: leaves of every autumn colour over dark earth), starships (`hull`, `hull_dark`, `hazard`, `deck`, `hex_panel`, plus the lit ones above), alien and dream worlds (`alien_ground`, `organic` living walls, `sky_wall` painted with sky and clouds, `cloud_floor`, polished `obsidian`), and a study's `fireplace` and `star_chart`. `python scripts/assets.py catalog.png` draws them all, with see-through textures over a checkerboard.

**Jungle, ruins and beach.** These are drawn a newer way (shapes lit from one direction and snapped onto colour ramps; see `scripts/pixelart.py`), so leaves and stones read as themselves even small on screen:

- Jungle: `jungle_leaves` (a wall of rainforest), `canopy` (the leaf ceiling seen from below), `canopy_top` (the canopy seen from above: use it as the `top` of jungle walls), `jungle_floor` (leaf litter and roots), `jungle_bark` (a giant trunk netted with strangler-fig roots), `temple_stone` (big chipped blocks with moss in the joints), `temple_cornice` (the top course of a temple tier: make it the last storey of each tier's wall stack, so a stepped pyramid reads as steps), `glyphs` (carved cartouches), `temple_roots` (blocks with roots poured over them), `temple_door` (a corbelled doorway into the dark), `roof_comb`.
- Ruins: `limestone` (sun-bleached ashlar), `ruin_paving` (worn slabs with grass in the joints), `dry_grass`, and the colonnade above.
- Beach: `beach_sand` (pale, wind-rippled), `wet_sand`, `shallows` (clear turquoise over a caustic-lit bed), `sea` (open water with whitecaps), `bamboo`, `thatch`. `wet_sand`, `shallows` and `sea` reflect by default. Leave the water at ground level on a beach: a `drop` draws a bank along the waterline, which looks like the edge of a pool.

## Lights

```json
{"x": 10.2, "y": 10.0, "z": 1.5, "radius": 4.5, "color": [1.0, 0.82, 0.5], "intensity": 1.1, "shadows": true}
```
- Falloff is `(1 - d/radius)^2 * intensity`, so `radius` is the hard edge of the pool of light. Lanterns 4-6, room lamps 3-4, big sources 6-8.
- A light dict is a point light unless it says `"type": "sun"` or `"moon"` (below).
- Shadows are traced through the grid: walls at least `min(z, 0.95)` tall block the light. See-through walls never do.
- Light above ~1.4 units fades with height, so tall facades darken toward the top.
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

Built-in props (260): armor, barrel, bed, bench, birch, birch_autumn, birch_winter, boulder, boulder_snow, brazier, buoy, bush, bush_autumn, bush_snow, campfire, candles, chest, column, console, crate, crystal, dead_tree, deer, fern, flowers, fountain, glowshroom, grave_cross, gravestone, lamp_post, lantern, lectern, locker, log, mushrooms, palm, pew, pine, rowboat, signpost, snowman, snowy_pine, stalagmite, statue, stump, table, throne, tree, tree_autumn, tree_winter, wheelchair, plus the wall-mounted, ground, countryside, sci-fi, dream and study props listed below. `tree_autumn`, `birch_autumn` and `bush_autumn` are the oak, the birch and the bush turned for the fall; `tree_winter` and `birch_winter` the oak and the birch bare in winter with snow along their limbs, `bush_snow` a bush buried in snow. `deer` (0.62 tall, antlered) stands side on. `boulder_snow` is the boulder under a cap of snow, for winter (the `snow` scatter set uses it). `crystal` and `glowshroom` glow (pair them with a coloured light); `pew`, `table` and `bench` take `stretch` for length.

- Sci-fi and alien: `stasis_pod` (lit glass, a sleeper inside; tint it dark for a dead one), `hologram` (a wireframe world over its emitter, with a soft glow), `sci_crate`, `drone` (float it with `z`), `lander` (a landing craft, 1.6 tall), `antenna`, `alien_plant` (glowing pods), `monolith`, `alien_egg`. For hangars and engine rooms: `shuttle` (a short-hop craft on landing legs, 2.2 tall, engines and cockpit lit), `cargo_container` (corrugated, faded orange; tint it for other colours and stack one on another with `z` 1.2), `power_loader` (a hazard-yellow exosuit with forks), `beacon` (an amber warning light; give it a light of its own), `reactor_core` (a glowing column 2.8 tall in steel collars), `robot_arm` (a welding arm on a turntable), `cables_hang` (slack cables from the ceiling: set `z` near the ceiling; no contact shadow). For a neon street: `vending_machine` (a lit front of cans), `noodle_stall` (lanterns, a neon sign, pots on the counter), `steam` (a see-through plume: stand it on a drain or a pot), `holo_ad` (a hologram koi drawn in light, additive: float it over the street with `z`), `wires_span` (wires slung across a street with lanterns on them: `planes` 1 by default; give it an `angle` across the street, a `length` and a `z` of 2.5-3.5).
- Dream and surreal: `orb` (a floating light with its own glow), `floating_rock` (an islet of earth adrift), `door_frame` (a door standing on its own), `sky_whale` (stars along its back; float it high), `koi`, `pocket_watch`, `balloon`, a whole chess set in marble - `chess_pawn`, `chess_rook`, `chess_knight`, `chess_bishop`, `chess_queen`, `chess_king` (tint them dark for the other side; scale them up for a giant game) - `melting_clock` (a clock gone soft: stand it just off the front face of a block with its `z` set so the fold lies on the edge), `hourglass`, `stone_arch` (a lone archway, 2.4 tall; it floats with `z`), `stair_float` (a flight of stairs broken off at both ends), `paper_boat` (it sails on a mirror floor), `jellyfish` (a bell of light trailing tentacles; additive, so it glows - float it with `z`), `sky_lantern` (a paper lantern lit from inside, drifting up), `book_fly` (an open book flying on its covers). `checker_marble` is a polished floor of black and white marble squares (mirror 0.35); `door_hall` is a pale panelled door in a papered wall, as in a hotel corridor - tint it for doors of every colour, stack it storey on storey, or use it as a `ceil` for doors overhead; `tall_window` and `tall_window_top` are a gothic window in pale stone, see-through between its leads, to stack two or three storeys high: `["tall_window", "tall_window", "tall_window_top"]`. Things meant to float carry no contact shadow, so set their `z` and they hang in the air. Over a void floor `z` is simply height above z=0.
- On the Moon: `dome` (a greenhouse under a geodesic frame of glass, lit from inside - it glows; 2.6 tall, scale it up for a big one), `hab_module` (a habitat cylinder on legs, its portholes lit), `solar_array`, `rover` (six wire wheels, two seats, a dish).
- Standing stones: build each as a wall cell of `menhir` (a weathered face, moss at its foot) with `menhir_top` above it, its height from a `heights` layer, and set a `stone_cap` on it (`z` a little under its height, `flip` half of them) for a slanted, chipped top instead of a flat one.
- A haunted house: `cobweb` (stand it across a corner as a card - `planes` 1, `angle` 45 or 135 - with `z` near the ceiling), `candelabra` (five candles burning; give it a warm light), `portrait` (an oval gilt frame round a pale, unsmiling face whose eyes catch a little light; hang it 0.2 off a wall with `z`), `grandfather_clock` (1.6 tall, its hands near midnight), `balustrade` (turned balusters between rails, three units long at its own height of 0.5: stand it as cards along the edge of a landing with `z` at the landing's height), `bats` (float them against the moon).
- A study: `telescope`, `globe`, `armchair`, `book_stack`, `open_book` (glowing pages; float a few for magic), `writing_desk` (with a lit candle), `orrery` (a glowing sun at its heart).
- The countryside: `scarecrow` (1.9 tall: a sack head under a battered hat, a patched coat on a crossbar, a crow on one arm), `pumpkin`, `jack_o_lantern` (carved and lit from inside: it glows - give it a warm light of its own at dusk), `hay_bale`, `crow`. On a village street: `well` (a round wall of fieldstones under a little shingled roof, a windlass and a bucket), `cart` (a hand cart loaded with sacks), `market_stall` (a striped awning over a trestle of apples, cabbages and bread), `inn_sign` (a gilt crown on a red board hanging from an iron bracket at its left end: stand it out from a front as a card - `planes` 1, `angle` square to the wall, `z` about 1.2 - so it reads from up and down the street).
- Desert: `saguaro` (3.2 tall, two arms and a few blossoms on its crown), `prickly_pear` (pads and magenta fruit), `tumbleweed`, `cow_skull`, `clay_pot` (white, painted in black zigzags), and for a frontier town `windpump` (4.2 tall: a lattice tower under a wheel of blades and a tail vane), `water_trough`, `wagon_wheel`.
- Swamp: `bald_cypress` (4.2 tall, buttressed at the foot, Spanish moss hanging from every limb; stand it in the water), `spanish_moss` (a curtain of it to hang from a limb or an eave with `z`), `cypress_knees`, `cattails`, `heron`, `alligator` (only its back and eyes above the surface: stand it in a sunken water cell; its eyes catch the light), `fireflies` (a swarm of tiny glowing lights, additive; float it with `z` at night).
- Under the sea: `kelp` (a stalk of giant kelp 5 tall, its blades streaming off small floats), `fish_school` (a shoal of silvery fish; float it with `z`), `bubbles` (a rising column, additive: float it from a diver's helmet), `anchor`, `wreck_mast` (a broken mast with a yard askew and torn rigging, furred with weed).
- The aquarium: the big tank's animals - `whale_shark` (3.4 long, spotted, its mouth at the very front), `manta_ray` (seen from below as it glides over, 0.9 tall and twice as wide), `reef_shark` (a blacktip), `sea_turtle` - the reef's fish - `clownfish` (a pair, a hand long), `angelfish` (an emperor, striped yellow and blue), `blue_tang`, `reef_shoal` (a shoal of orange-pink anthias) - the reef itself - `brain_coral`, `staghorn_coral`, `sea_fan` (a purple lace), `anemone` (with its pair of clownfish nestled in), `tube_sponge`, `reef_rock` (a mound of live rock grown over with all of them, the piece to build a reef from) - and for a jelly tank `sea_nettle` (golden, half see-through, for a blue backdrop) and `moon_jelly` (clear, glowing, additive). The fish face right (`flip` turns them), are lit from above and float with `z`; nothing that swims has a shadow. `info_plaque` is a visitors' sign on a post, its panel lit from behind.
- The night market: `food_cart` (a teal cart on two wheels, a wok over a roaring burner, stock pots, bowls, a glowing menu board and bare bulbs under its tin roof), `fruit_stall` (crates in three tiers heaped with fruit under a green tarp) and `gadget_stall` (glowing screens and odds and ends under a blue tarp), `red_lantern` (a paper lantern lit from inside; hang it with `z`), `lantern_span` (a rope of them to sling across a lane, a card like `wires_span`), `neon_sign` (a standing lightbox lettered in neon, 1.5 tall), `umbrella` (clear, with a lit shaft: stand it at a person's place with `z` 0.33), `scooter`, `stools_table` (a folding table with bowls, a red and a blue plastic stool), `power_pole` (concrete, cables looping off its crossarm, a street lamp) and `crowd` (a dozen people in the rain, some under umbrellas, to fill the far end of a street). Their signs carry the same glowing pseudo-letters as the `neon` facades.
- The neon bar: `arcade_cabinet` (an upright cabinet, a shooter on its screen, a lit marquee, a joystick and buttons, neon side art), `bar_counter` (the front of a bar - dark panelling, a steel rail, a strip of magenta light along its foot - to stand as a card along the bar, `planes` 1 with a `length`), `bar_stool`, `booth` (a high-backed bench in teal vinyl behind a formica table with a lamp), `jukebox` (bands of colour round its arch, bubble tubes), `neon_cocktail` and `neon_fish` (neon art for a wall, additive: hang them with `z`), `bottles` (a cluster for the bar top). `bar_shelves` is the wall behind a bar: two shelves of bottles lit from below.
- Up on the roofs: `water_tower` (a wooden tank on steel legs under a conical cap), `ac_unit`, `rooftop_sign` (three tall panels lettered in neon on a steel scaffold, 2.6 tall), `sky_train` (an elevated train, every window lit, on a beam held up on pillars: a card to sling across a street, `planes` 1 with a `length`, its `scale` the height of the line) and `black_cat` (sitting with its back to you, one green eye catching the light; set it on a ledge).
- Doomed (a 1993 shooter's base): `toxic_barrel` (a ribbed drum brimming with glowing green sludge), `corpse` (a fallen soldier in a pool of blood), pickups `medkit`, `ammo_clip` and `armor_vest`, and a `fireball` (additive: float it with `z`).
- Cards and parts: `jungle_card_1`, `jungle_card_2`, `jungle_card_3` and `jungle_card_4`, the long strips of the jungle fringe (front to back), `forest_card_1`, `forest_card_2`, `forest_card_3` and `forest_card_4` likewise for the forest (`autumn_card_1`, `autumn_card_2`, `autumn_card_3` and `autumn_card_4` for the forest in autumn, `winter_card_1`, `winter_card_2`, `winter_card_3` and `winter_card_4` in winter; `swamp_card_1`, `swamp_card_2` and `swamp_card_3` for the swamp, `kelp_card_1` and `kelp_card_2` for a kelp forest), and `palm_trunk` and `palm_crown`, the palm in two pieces in one frame, which stack back into a palm (see the `palm_3d` prefab). `glass_pane` is a plain pane of glass (see Glass).
- Jungle: `banana_plant`, `monstera`, `tree_fern`, `heliconia`, `bromeliad`, `fern`, `liana` (hangs down from the canopy; no contact shadow), `kapok` (an emergent giant 7.5 tall: stand it in the jungle and its crown clears the canopy), `canopy_crown` (set it on top of a jungle wall with `z` a little under the wall's height, a few to a stretch, and the canopy edge becomes a line of rounded crowns against the sky), `stone_head` (a colossal carved head), `stela`, `jaguar` (its eyes glow), `macaw`.
- Ruins: `column` (Doric, 1 tall by default: scale it to 2.5-3 for a temple), `broken_column`, `column_drum` (fallen, on its side), `marble_head` (colossal, broken off at the neck), `amphora`, `cypress`, `olive_tree`, `poppies`, `goat`, `dry_tuft`.
- Beach: `palm` and `palm_lean` (leaning out over the water), `coconuts`, `canoe` (an outrigger), `tiki_torch` (a flame with its own glow), `hammock`, `driftwood`, `crab`, `seagull` (float it with `z`), and `surf` and `surf_glow`: a low line of foam, about 1 unit long, for a row along a waterline (a foam decal is seen edge-on from eye height; these stay visible), `surf_glow` being surf on a night of glowing plankton.

Built-in characters (16x32 pixel art): cultist, scientist, guard, nurse, spiritualist, ghost (translucent with aura and wobble by default), hybrid, soldier, knight, child (about 0.42 tall), creature, robot, shopkeeper, astronaut, android, alien (about 0.7 tall), dreamer (in a nightgown, holding a candle), explorer (pith helmet and khaki), hoplite (crested bronze helmet, round shield and spear), castaway (straw hat, ragged shirt, barefoot), diver (a brass diving helmet with a round faceplate, a canvas suit, weighted boots), runner (a lit visor, a black jacket striped in neon), cowboy (a wide-brimmed hat, a red bandana, a vest and a gun belt), witch (a crooked pointed hat, green skin and a robe, a lit lantern at her side), farmer (a straw hat, a plaid shirt and overalls, a pitchfork), pirate (a tricorn edged in gold, an eye patch, a red coat and a cutlass), samurai (a street samurai of the neon city: a topknot, a red visor, a long black coat lined in crimson, a sword slung across the back, one chrome arm), hacker (hood up, cyan goggles, a deck glowing in the hands, sneakers with lit soles), and claude. The creature's eyes, the robot's eyes and chest lights, the astronaut's suit lights, the android's visor, the runner's visor and stripes, the samurai's visor, the hacker's goggles, deck and soles, the witch's eyes and lantern and the alien's eyes glow in the dark.

`claude` is Claude's own avatar: a small figure whose head is a paper lantern lit from inside, in a clay-coloured coat with a teal scarf, holding an open book. It carries its own warm light. `examples/claude_study.py` puts it in the reading room it chose, with ready-made shots for answering a question in a picture.

Wall-mounted and hanging props (`sconce`, `painting`, `banner`, `wall_clock`, `pipe_valve`, `ceiling_lamp`, `chandelier`, `ivy_hang`, `chains`, `ladder`) are ordinary sprites: place them a little off the surface (about 0.2-0.3 from a wall face) and set `z`. Ground clutter (`rocks`, `rubble`, `bones`, `sack`, `bucket`, `broken_barrel`, `grass_tuft`, `dry_tuft`, `reeds`) is sized to read at 320x200; scatter a handful rather than a carpet.

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

Built-in decals: puddle, puddle_dark, puddle_shine, stain, stain_rust, splatter, splatter_dark, vines, moss_patch, crack, scorch, leak, cobweb, rune_mark, drain, contact_shadow, for the shore and the jungle pool: foam, foam_glow, starfish, shells, seaweed, lily_pads, and for hangars: pad_marking (a painted landing ring with an H, 4-6 units across) and hazard_stripe (a worn yellow-and-black band), and on the Moon rover_tracks (a rover's two tracks of chevron treads pressed into the dust), and for the doomed mode toxic_sign (a yellow warning triangle with a skull, TOXIC under it, for a wall). `rune_mark` and `foam_glow` are emissive, so they glow regardless of lighting. Seen from eye height a floor decal is foreshortened almost to a line, so `foam` reads from a raised camera or close up; for surf seen from a standing height use the `surf` props. `contact_shadow` is the soft disc used for contact shadows, which you can also stamp by hand (under a prop hanging low over the floor, say). The puddles reflect by default (`puddle_shine` 0.55, `puddle` 0.35, `puddle_dark` 0.25), so a lamp post shows in the wet patch at its foot.

- A floor decal is drawn on the plane of the cell it sits in, so a puddle inside a cell with a `drop` lands on the sunken surface, not the bank above it.
- Dark puddles read as holes punched in a lit floor. Use `puddle_shine` on anything a lamp reaches (wet asphalt, sand, boards) and keep `puddle_dark` for dim interiors.
- Wall decals that hang (`vines`, `leak`, `cobweb`) are drawn from the top of their footprint down, so set `z` near the top of the wall.
- A wall decal is clipped to its own face, so one that overhangs the cell edge ends in a hard vertical cut. Keep `u - size/2` and `u + size/2` inside 0-1, or split a wide stain across two faces.

## Reflections

Water, ice, wet streets and puddles mirror whatever stands over them: lit windows across a frozen lake, a creature wading in a cave pool, a lamp post in the puddle at its foot.

- A floor reflects if its cell has `reflect` (0-1), its texture reflects by default (`water` 0.5, `ice` 0.38), or a reflective decal covers it (the puddles).
- `"reflections": false` turns them off for the scene, a number scales every reflection (`0.5` halves them), and `{"amount": 1.0, "ripple": 1.0}` also sets the sideways shimmer (`0` for a still, glassy surface, `2` for choppy water).
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

**Held items** (`viewmodel`): revolver, lantern, flashlight, axe, crowbar, torch, pistol, shotgun (the last two held out in the middle of the view, 1993-style). The lantern and torch add a point light at the camera automatically (`"light": false` to disable); the flashlight turns the flashlight cone on unless the shot sets it.

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

**Bloom from light.** `"source": "image"` (the default) blooms whatever is bright in the finished frame, a pale wall as much as a lamp. `"source": "light"` blooms only what gives off light: emissive texels (lit windows, neon, screens, runes), glowing sprites and their flames, auras, a sun or moon disc - and their reflections in wet ground and water - read from an emission buffer the renderer keeps beside the frame. The glow is blurred in float at three widths, a tight core and a halo `spread` wide, so it can go far stronger without washing the walls out: `{"fx": "bloom", "source": "light", "strength": 2.4, "radius": 2.5, "spread": 0.6}` makes a neon street glow (see `examples/neon_street.py`).

**Depth of field.** `{"fx": "dof"}` keeps the frame sharp at the focus and softens it nearer and farther, as a lens wide open does: the blur grows with the difference between 1/distance and 1/focus, so it is greatest at the horizon and at half the focus distance. The background is gathered only from pixels at or beyond the focus, so a sharp subject never smears into it; a soft foreground spreads past its edges over what is behind. Lens effects run first, whatever their place in the list, and a held item (`viewmodel`) is drawn after them, so it stays sharp. Left without a `focus` it focuses where the shot looks (`look_at`); give a close shot of a character `"blur": 2-3` and the street behind melts into soft light (see the samurai in `examples/night_market.py` and the cat in `examples/neon_rooftop.py`).

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

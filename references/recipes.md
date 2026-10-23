# Recipes: how to build particular places

Each recipe is the textures, props, sky and light that make one kind of place read, and the scene
file in `examples/` that shows it. Read the one for the place you are drawing (and the general
advice in SKILL.md, "Making it look good"), then write the scene. Every name here is in
`references/scene_format.md` and `references/assets.md`.

## Out of doors

### Woodland

Fill the grid with `forest_deep` wall cells (trunks receding into the dark) about 2.4 high with `"fringe": {"set": "forest", "depth": 1.2, "wander": 0.3}` (wandering, so the wood's edge is a natural line and no flat wall face shows at its corners) and carve the paths and clearings out with `maptools.Grid.rect` and `disc`. The fringe stands four layered cards in front of every face onto open ground - a dense wall of spruce and oak, then younger trees, then bushes, ferns and grass - so leave a cell of open ground in front of the walls and make paths two cells wider than they should look; the tree tops on the cards make the skyline. Stand `pine` (a spruce), `tree` (an oak), `birch`, `dead_tree`, `bush`, `stump`, `log`, `boulder`, `fern` and `mushrooms` in the clearings. Floors: `pine_needles`, `moss`, `mud`; `bark` and `bark_pine` walls for trunks; `foliage_autumn` for the fall. The wood in autumn: `forest_deep_autumn` walls with `"fringe": "forest_autumn"`, `leaves_fallen` underfoot, `tree_autumn`, `birch_autumn` and `bush_autumn` standing free and the `autumn` scatter set on the verges; at a field's edge a `scarecrow`, `pumpkin`s, `hay_bale`s and `crow`s, and `jack_o_lantern`s lit at dusk; the `leaves` post effect sets leaves falling. Light it with a low sun at the end of a lane in a thin, dark-gold fog (a pale or dense one blows out toward the sun). The wood in winter: `forest_deep_snow` walls with `"fringe": "forest_snow"`, `snow` underfoot, `tree_winter`, `birch_winter`, `snowy_pine` and `bush_snow` standing free, a stream of `ice` sunk with `drop` 0.08 under a footbridge of `planks` blocks 0.14 high, a `deer`, the `snow` scatter set; keep any ground fog thin or the snow and the mist run together, and add the `snow` post effect for falling snow. See `examples/woodland_night.py`, `autumn_lane.py` and `winter_woods.py`.

### Standing stones

`standing_stone` objects, 1.5 to 2.25 tall, a little different in size and each its own `seed`, set round a ring with their broad faces turned into it (`angle` toward the centre) and an altar in the middle (`height` 0.45, `size` 1.7, `depth` 0.9: a slab lying); strays out on the moor turned any way. Give them `"casts": true` so a low sun throws their long shadows across the grass and through a ground fog, the gaps between them shafts of light. (Wall cells of `["menhir", "menhir_top"]` at different heights, each with a `stone_cap` sprite on top, make a blockier circle that needs no objects.) See `examples/misty_moor.py`.

### Jungle, ruins and beaches

A jungle is walls of `jungle_leaves` at a few heights (2.5-4) with `canopy_top` tops and `"fringe": {"set": "jungle", "depth": 1.4, "wander": 0.3}`, which stands four layered cards of trees and bushes in front of every face that looks onto open ground, along a natural, wandering line - so leave a cell or two of open ground in front of the walls for it, and make paths two cells wider than they should look. Keep the canopy at one height within two cells of open ground, so the fringe's trees make the edge and no steps of the canopy show between them like clipped hedges. Add a `canopy` ceiling over the paths with a few cells left open for shafts of sun in the mist, `kapok` giants standing clear of it, and `canopy_crown` props on the wall tops so its edge is rounded crowns; plants (`banana_plant`, `monstera`, `heliconia`, `tree_fern`, `liana`, the `jungle` scatter set), a `jaguar` and a `macaw`. A stepped pyramid is rings of `heights` a unit apart, each tier's wall stack ending in `temple_cornice`, stairs up one face, a `temple_door` shrine and a `roof_comb`. Classical ruins: `column` objects of `"material": "marble"` with `"flutes": 20` and `"doric": true` on a stylobate, `beam` architraves and cornices across the runs that stand, others `broken` off, `"fill": 1.0` if the low sun is behind them and `"casts": true` so it throws their shadows in stripes across the ground; `limestone`, `ruin_paving`, `dry_grass`, `cypress`, `olive_tree`, `marble_head`, `goat`, a `hoplite`, the `ruins` scatter set, under `golden`. A beach: `beach_sand`, a band of `wet_sand`, `shallows` then `sea`, all at ground level; a row of `surf` props along the waterline, `palm` and `palm_lean`, a hut of `["bamboo", "thatch"]` walls, `tiki_torch`, `canoe`, `hammock`, the `beach` scatter set and the `islands` skyline under `sunset`; a pier of low `boards` blocks on wooden piles - `column` objects of `"material": "wood"` down both edges, `sink` 0.06 so they stand in the water - and the jungle behind it with a `jungle` fringe. See `examples/jungle_temple.py`, `ancient_ruins.py`, `tropical_beach.py`.

### Inside a temple

A passage one cell wide of `temple_stone` with `glyphs` every other cell, under a `ceiling_height` of 1.4 (walls exactly that tall), running into a sanctum; in the sanctum's roof one cell with no `ceil`, and a high sun (elevation 70 or more) shining down through it in a thick fog (density 0.06, `shafts` 4) - a column of light on the altar. The altar a `beam` of `stone` on the floor, a `golden_idol` on it, `treasure` round it, square `column`s of `stone` (`"sides": 4`, a `base` and `capital`), `temple_roots` in the wall behind, `liana`s down the light, `stela`s, `brazier`s with firelight at the door, the floor flooded at the front with `water` sunk a little (it mirrors). See `examples/temple_inside.py`.

### Deserts and canyons

Carve a wash out of rock cells stacked in bands (`["sandstone", "sandstone", "sandstone_pale", ...]`, 5-7 high) and give the rim a few heights so the skyline is ragged; nudge the canyon's edges in and out a cell here and there so the walls are not a corridor. A `desert_wash` floor with the `desert` scatter set, `saguaro`s and `prickly_pear`, a `cow_skull`; the ruins of a cliff dwelling are low blocks of `pueblo_stone` with `pueblo_door` cells, a `ladder` and `clay_pot`s. A `rock_wall` of `"rock": "sandstone"` along a wall's foot and a few sandstone `boulder`s break up a canyon floor's straight edges. For a slot canyon, a winding gap two cells wide in `slot_rock`, its cells roofed (`ceil`, with `ceiling_height` under the rim) and one cell left open: a high sun comes down through it in a single beam in a warm, dusty fog with strong `shafts`. See `examples/red_canyon.py`.

### A Japanese garden

A garden of `grass` inside a wood of `forest_deep_autumn` with a wandering `forest_autumn` fringe; a `gravel` path from a gate - two `column`s of `lime_red` (`sides` 12, `top` 0.85, 2.8 tall), a tie `beam` of it at 2.3 and a wider top `beam` of `lacquer_black` at 2.8 - to a tea house of white walls under a `gable_roof` of `slate` with deep eaves (`overhang` [0.7, 0.5]); a pond of still `water` across the path with a plank bridge (a row of low `boards` blocks) and red `beam` rails on short posts; `stone_lantern` objects along the path and by the water, `boulder`s of `stone`, `tree_autumn` maples close round the pond, `bush_autumn`, a few `pine`s, `lily_pads`. A `golden` sky; at dusk the lanterns' lights (warm, radius 3) along the path. See `examples/autumn_garden.py`.

### A glasshouse

Walls of `glasshouse` (open panes in white iron, see-through) two storeys high round beds of `jungle_floor` and a path of `encaustic` tiles, no `ceil` anywhere inside, and over it all a `gable_roof` object with `"cover": "glass"` and `"ends": "glass"` on the walls' tops: the sky shows through the glass and the sun comes in. Slender `column`s of `iron_white` along the path (`sides` 8, radius 0.07, a base and capital) and `beam`s of it across under the roof, both with `fill` 0.8 so the white reads against the light; `palm`s scaled up to 4-5 so their crowns reach into the glass, `tree_fern`s, `banana_plant`s, `monstera`, `heliconia`, `fern`s, a `fountain` under the ridge. Shoot it from inside: from outside, walls of open panes read as a cage. See `examples/palm_house.py`.

### A basalt causeway

`column` objects in a hexagonal grid - `sides` 6, `radius` 0.34 across the corners, centres `2 * radius * cos(30deg)` plus 0.05 apart (a dark joint between them), every other row shifted half a step and the rows `0.866` of a step apart - of `"material": "basalt"` (dark rock, its joints across each column at heights of its own), each `"casts": true` so the low sun's shadow of one falls on the next, `fill` 0.5. Heights from a slope (highest at a cliff's foot, down to just over the water) plus a smooth noise and a few steps of difference between neighbours, so their sides show; one or two stacks. Set each `z` -0.3 so the columns in the water stand in it. Organ pipes up the cliff behind: two rows 3 to 5 high. A `sea` floor (`drop` 0.2, `reflect` 0.45) mirrors a `sunset` sky; a sun from the side (not behind the columns, or the tops go black), the `islands` skyline, gulls, surf on the shingle. See `examples/basalt_coast.py`.

### A fjord

Water (`deep_water`, `drop` 0.2, `reflect` 0.55) down the middle of the map between cells of cliff (`rock` walls about 4.4 high with a `grass` top) lined with a tall `rock_wall` of `stone` (`height` [4.6, 7.6], `trim` 0.14 for a ragged rim, `pieces` [1.6, 3.4]); a beach of `gravel` at its head and `grass` above. A `longship` object drawn up on the shingle (`heel` 5), another riding at anchor (`z` -0.3, `"sail": false`); a longhouse of `logs` walls under a `gable_roof` of `thatch`, `round_shield`s on its wall, `steam` tinted grey for smoke from its roof; a `campfire`, `barrel`s, a `chest`, `goat`s, `pine`s and `birch`es, `seagull`s; the `mountains` skyline pale under a `day` sky. At dusk the fire lights the shields. See `examples/fjord.py`.

### Swamps and bayous

`swamp_deep` walls (about 2.6) with `"fringe": {"set": "swamp", "depth": 3.0, "wander": 0.35}` - four layers of cypresses spread three cells out along a natural line, so the trees stand at every depth - round open water of `swamp_water` sunk with `drop` 0.12 and a `bog` `side`, `bog` hummocks and an island; `bald_cypress`es standing in the water with `cypress_knees` round them, `cattails`, `lily_pads` decals, a `heron` in the shallows, an `alligator` with only its eyes up; a shack of `boards` with a lit window and a lantern on a porch of low `boards` blocks, a `rowboat` at the landing. Frame the shack between two near cypresses and keep the fog thin (0.008-0.012) or the far side vanishes; at night add `fireflies` and a `bloom`. See `examples/bayou.py`.

### Under the sea

Make water of the air - a dense teal fog (`[0, 0.15, 0.19]`, density about 0.05) with weak `shafts`, a high sun from behind the camera, and a teal `grade` post (`tint` `[0.74, 0.98, 1.05]`); a `seabed` floor, `kelp` stalks 4-5.6 tall scattered at random with a clearing, low `rock_wet` ledges with `"fringe": "kelp"` round the edge, `fish_school`s at different `z`, the `seabed` scatter set and `starfish`, `shells` and `seaweed` decals; a wreck - a `ship_hull` object listing in the sand (`heel`, its side stove in with `broken`, turned toward the camera) - with a `wreck_mast`, `boulder`s of `reef` rock for outcrops, an `anchor` and a `chest`; a `diver` with `bubbles` rising from the helmet. For a night dive: `flashlight`, a black fog and glowing `jellyfish`. See `examples/kelp_forest.py`.

### Castles and dungeons

`castle` walls, `flagstone` floors, `beams` ceilings, `stained_glass` (glows) in a storey of the wall, `portcullis` and `bars` for gates and cells, with `throne`, `armor`, `banner`, `chains`, `chest`, `table`, `sconce` and `brazier`. Chapels: `stone_pale`, `lancet_window`s down the walls and a `rose_window` over the altar - stand the sun in front of them and they lay their colours across the floor and the pews, with coloured beams in a thin fog (`shafts`; see `examples/glass_chapel.py`) - rows of `pew` objects facing the altar (or the `pew` prop with `stretch`), `lectern`, `candles` on a raised altar. Caves: `rock_wet` walls lined with a `rock_wall` of `"rock": "cave"` (`"lining": "#"` lines every wall face of those cells; `lumen` rock grows glowing moss) round a sunken pool of `glow_water`, `crystal_cluster`s - each carries its own coloured light - and `glowshroom`, `glow_fern` and `glow_pods` on `lumen_floor`, `stalagmite`, the `cave` scatter set; keep the ambient low but not black (about 0.08) and the mist thin, or the walls vanish. Sewers: `slime_brick`, `pipes`, a sunken channel with `railing`. Winter: `snow`, `ice` (reflective), `snow_rock`, `snowy_pine`, `boulder_snow`, `snowman`, and the `snow` scatter set (stones and snow-capped boulders) instead of `stones`, whose boulders are mossy. See `examples/castle_keep.py`, `chapel_graveyard.py`, `crystal_cave.py`, `sewer_tunnels.py`, `winter_lake.py`.

### The spooky island: a canal tunnel, a garden through a broken window, a storm over a town

The three concept drawings this project began from, made into scenes - each a different trick.

*A canal tunnel.* A tunnel three wide, its middle column a canal (`water`, `drop` 0.18, `reflect` 0.45) between two walkways of `flagstone`, `castle` walls and ceilings tinted a cool grey-violet, `ceiling_height` 1.6; a `vault_arch` card across it every 1.3 (`angle` 0 for a tunnel running north-south, `z` the drop, since a sprite in a sunken cell already rests on the water) and the arches frame each other away into the dark. `wall_lamp`s in pairs at about 0.9, each with a warm light half a cell out from the wall (on the wall itself it only grazes it); an `iron_cabinet` under the first lamp and a `sigil` on the wall across - nearer the camera than the lamps, because a wall seen along a tunnel is foreshortened and a decal far down it reads as a smear. The boat is a `ship_hull` at `scale` 0.3 (`length` 4, `width` 1.3, `depth` 0.55: a punt a little over a metre long), turned a little across the canal so the view down the tunnel sees its side; objects in a sunken cell are lowered to the water as sprites are, so its `z` is only how deep it sits. A `lantern` on a wooden pole at its bow, a `cable` from a post on the walkway for the mooring rope, two `beam`s of painted iron along the vault for pipes. Cool ambient (0.15, 0.155, 0.22), black fog, a cool grade with a lift in the shadows; pitch the main shot down a little (-0.07) so the boat is not cut off. A shot from the boat itself (`height` 0.2, its bow and lantern in the corner) is the one that says *you can get on*. See `examples/canal_tunnel.py`.

*A garden through a broken window.* A dark room whose north wall has a gap two cells wide with a low sill (a wall cell `h` 0.25 with a `ceil`, so the roof carries on over it); a `broken_casement` at `scale` 1.5 stands just inside it (`y` 0.02 into the room), its plaster laid over the wall either side, `tint` it to the room; a `tattered_curtain` each side over the frame; `glass_shards` on the floor under it with a cool light low inside the window for the moonlight coming in. Outside, a gravel path to a `robed_statue` on its pedestal with a cool light before its face (the moon is behind it), `rose_bush`es either side, a `lamp_post` lit, `cypress`es against the sky, a house on the left in plaster tinted blue with one cell's storey `window_lit_plaster` (tint it warm, or the night grade turns it white), a tower of `stone_dark` with a `window_teal` storey on the right; the `moon` low (elevation 14) a little to the right so its disc sits in the window. Keep the grade neutral - a blue tint on top of moonlight turns every lamp grey. See `examples/window_garden.py`.

*A storm over an island town.* At landscape scale with the camera on a ferry's deck (`height` 0.1 - lower and the waves of `harbor_water` near it are drawn huge), 400 m out, `pitch` 0.15 so the sea is the lower third. Compress the town so its parts overlap in depth as a drawing's do: tenements (`tower`s) on the sand in front of a steep hill (a `mountain`, `ridges` 0, cut flat with `top` 0.84) with a house on its flat top (a `tower` with a slate `gable_roof` and a spire, a `column` with `top` 0.08), cottages (a `village` with no church, `scale` 2) along the shore, a plateau behind (a `mountain` with `length` and `cliff`, `ridges` 0 for a clean edge) carrying an institution, a factory with two chimneys smoking and a power station. A flat top's middle and height are not the placement's: render one, or read them off the object's panels, and set the buildings on it. A `lighthouse` (`scale` 0.036) on a `boulder` at the end of a pier of `beam`s on `column` piles, its beam a `searchlight` at `elevation` 1.5. The storm: `storm_cloud`s far off and high over the `storm` sky - eight of them hide its stars - and `lightning` in the post with `y_end` set so the bolt comes down on the power station, a cold light there and the fog's `glow` making a halo of it; `reflections` `{"ripple": 1.8, "smear": 1.5}` for a choppy sea. Small saturated colours - red warning lights, a lighthouse's red band - are a few pixels in a 320 x 200 frame, and in a dark scene the adaptive palette can drop them: don't hang the picture on them. See `examples/storm_island.py`.

### Haunted houses

Give the house a steep roof outside - a `gable_roof` object of `"cover": "slate"` on its walls' tops (`z` at their height), a `chimney` at two places - the ceilings inside hide it. A double-height hall (`ceiling_height` 3) with walls stacked `["wood_panel", "wallpaper", "wallpaper"]` and a `beams` ceiling; a grand staircase from the `heights` layer (a straight flight of 0.2 steps with `carpet` tops up to a landing block at 1.4) with `balustrade` cards along the landing's edge at `z` 1.4; `portrait`s on the walls, `candelabra`s (with warm lights) on the floor and the landing, a `chandelier`, a `grandfather_clock`, `armor`, `cobweb`s across the corners, a `fireplace` with an `armchair`, and the `ghost` on the stairs. Outside: a dark front with a taller middle (stacked `stone_dark` and dark windows, one or two `window_lit`), `jack_o_lantern`s on the steps, a `fence_iron` with the gate open, `dead_tree`s and `gravestone`s, `bats` against the moon. See `examples/haunted_house.py`.

## Cities

### City streets

Build each block of buildings one cell back from where its fronts should stand and give its cells a `facade` (`{"style": ["brick", "sooty"], "storeys": [3, 6], "lit": 0.5, "shops": 0.4}`): the fronts become separate buildings of different heights and brick, with windows set back in the walls, glass, curtains and lit or dark rooms behind. Then pavement, then a road sunk a kerb's height (`drop` 0.05) between, `street_lamp` prefabs, `wet` ground and rain. Show the depth from the pavement, looking along the buildings. Any sprite with `"glass": true` is glass: it shows what is behind it, tinted light blue and softly blurred; `glass_pane` is a plain pane. For a cyberpunk street use `"style": "neon"` (signs on the walls, blade signs over the street, shutters, tinted rooms) with `wires_span` across overhead, a `holo_ad`, a `noodle_stand` object (or a `noodle_stall` billboard far off), `vending_machine` objects, `steam` from the drains and coloured lights under the signs so their colour lands on the wet street; a `bloom` with `"source": "light"` makes the neon glow. For a night market fill a lane with stalls a unit out from the fronts (the facades' street line is `depth` 1 from the blocks: anything nearer the wall is behind it): `food_cart`s with `steam` and a `stools_table`, `fruit_stall`s, `gadget_stall`s, a `red_lantern` and a warm light at each, `lantern_span`s across overhead every five units with a red light under each, `power_pole`s, `scooter`s, a `neon_sign` at a side alley, `crowd`s down the far end and people under a lit `umbrella` (with a small cyan light at the shaft). For a village use `"style": "timber"` with `storeys` [1, 2] and `widths` [2, 3] over a block one storey high: timber-framed houses in limewash and ochre, each with its roof built in 3D - running back behind a gable end, or along the street in thatch or tiles, chimneys - on a `cobble` street, with `market_stand` objects (one in red stripes, one in blue, `goods` heaped on their trays), `crate` and `barrel` objects by the inn's door, an `inn_sign` standing out as a card, a `cart` and `flowers`, and a `well` object on a green. For a frontier town use `"style": "western"` with `storeys` [1, 2]: false fronts with painted signs (a saloon with batwing doors among them), clapboard, and the posts of a covered boardwalk a cell out - make that cell a `planks` step 0.15 high with a `ceil` and set `ceiling_height` 1.15, so the walk is roofed; each porch gets a roof of boards sloping down to its fascia, and each building its own gabled roof behind its false front, both built in 3D, so the street has depth; end each block with a plain wall so the fronts only face the street. Dust (`desert_wash`), `tumbleweed`s, a `trough` object, a `windpump` where the street runs out into the desert, the `cowboy`. See `examples/rain_alley.py`, `neon_street.py`, `night_market.py`, `village_green.py` and `ghost_town.py`.

### Facades

Stacked wall textures per storey with `window_lit` / `window_dark` mixed per cell and storey; tall background buildings (h 6-9) give scale and skyline.

### On a rooftop

Stand the camera on a tall block (a block `h` 5 with `height` 5.5-6, roof props at `z` 5) at the very edge, looking down a street of `neon` facades between blocks taller than the fronts; `lantern_span`s and `wires_span`s across it a few units down, a `holo_ad` over it, a `sky_train` card crossing it, towers of window walls behind. On the roof: a `water_tower`, `ac_unit`s, a `rooftop_sign`, the `runner` and a `black_cat` on the ledge; a lamp set up there (`z` a little over the roof) lights the roof round it as a lamp lights a street. From the street, look up at the train. See `examples/neon_rooftop.py`.

### A neon bar

Keep a room small - a unit is nearly three metres, so a bar is about 6 by 5 cells under a `ceiling_height` of 1.3. `bar_shelves` on the wall behind the bar, a `bar_counter` card along it (0.35 tall: a bartender shows from the chest up), `bar_stool`s, `bottles` on top, `arcade_cabinet` objects down one wall, backs to it, each in its own `color` with a light of that colour in front of it, `booth`s with a character just behind the table (it reads as seated), a `jukebox`, `neon_cocktail`/`neon_fish` on the walls, `obsidian` underfoot to mirror it all, and a thick glowing fog (density 0.06, `glow` 1.2) for the smoke. A reef tank in the back wall as in the aquarium. See `examples/neon_bar.py`.

### A saloon

The same scale: a saloon is about 8 by 6 cells under a `ceiling_height` of 1.6. Walls of `["saloon_wainscot", "saloon_paper"]`, the back bar `["saloon_backbar", "saloon_backbar_top"]` along one wall with a `saloon_bar` object in front of it (a 3D counter 0.38 tall with a brass foot rail: a bartender shows from the chest up), front windows of `["saloon_window", "saloon_paper"]` and a doorway onto a bright street with nothing across it, so they glow; a `tin_ceiling`, `wood_floor`. `card_table` objects with `saloon_chair` objects round them, turned to the table, and a character standing just behind (it reads as seated), a `piano` object against a wall (give the night's overrides `objects` with the piano `lit`, so its candles burn), `spittoon`s along the rail, a `chandelier` and `sconce`s with warm lights, `wanted_poster` decals, a `cow_skull` on a wall. A sun low in the windows' direction (elevation 20-25) with a dusty fog (density about 0.025, `shafts` 3) lays the beams. Put the day's people in the shots' `extra_sprites`, so the room at night is empty but for a ghost at the piano. See `examples/saloon.py`.

### A mine

A tunnel two cells wide under a `ceiling_height` of 1.0, its walls `mine_rock` exactly that tall (a wall taller than the ceiling is drawn its full height, over the ceiling - give the hill outside cells of its own), a few cells `mine_rock_vein`; `rock_floor` underfoot and a `ceil` of `boards` for the lagging. Timber sets every 1.3: two `column`s of `"material": "wood"` with `"sides": 4` against the walls and a `beam` across at 0.88; a `rails` object down the middle and `ore_cart`s on it; a `lantern` on every third set with a warm light. A stope off the tunnel with its face in `mine_rock_gold` (the gold glints), a character at it with a lantern by him, `ore_heap`s, a `pick_shovel`, a `dynamite_crate`. Outside, the hill in cells of its own, lined with `canyon` rock, the portal a heavier set with a `rock_wall` lifted over it (`z` at the cap, `"back": true`) to close the hillside above the opening. See `examples/gold_mine.py`.

### A capsule hotel

A corridor one cell wide under a `ceiling_height` of 1, its walls `capsules` and `capsules_lit` alternated cell by cell (two rows of berths to a unit), cool strip lights every few cells, a white floor with `reflect`, a `vending_machine` object at the end and someone padding down it. See `examples/capsule_hotel.py`.

### A clockwork city

Blocks of `brick_dark` with a `brass_plate` top storey, runs of `copper_pipes` venting `steam`, a tower with a `great_clock` card on its face (and a `cone` wireframe for a brass spire), `gear` objects standing out from the walls (`angle` so their faces look out from the wall, set `depth / 2` off it; mixed sizes, `teeth` to suit - 16 to 32 - `z` to lift them; the `brass_gear` card is a flat stand-in), `lamp_post`s with warm lights, the `robot` tinted brass for an automaton. An orrery is wireframes: thin brass `torus` rings (`thickness` about 0.016) at different `tilt`s round a `sphere`. `sunset` sky, brown fog, ambient about 0.28, a low warm sun, a gentle light bloom (1.2). See `examples/clockwork_city.py`.

## Sci-fi and other worlds

### Industrial and sci-fi

`panel`, `panel_green`, `pipes`, `rust` walls over a `grate` or `tile_floor` floor, with `console` (emissive screen), `locker`, barrels and crates; pair with the `terminal` GUI theme and `crt_green`.

### Space and sci-fi

Corridors of `hull_lit` (or `hull_red` for emergency power) draw lines of light to the vanishing point; `tech_panel`, `server` and `blast_door` walls, `deck` or `grid_floor` underfoot. For a view of space, build a `viewport` wall (stack two for a glass wall) with `"floor": "void"` cells outside under `"sky": "space"`, and hang a `ringed` planet in `sky_objects`: stars surround you above and below the horizon, and an `obsidian` floor mirrors the planet. Props: `stasis_pod`, `hologram`, `drone`, `sci_crate`, `console`; cast: `astronaut`, `android`. Infested ships: `organic` walls, floors and ceilings, `alien_egg`, the `derelict` scatter set. Hangars and engine rooms: `hangar_floor` decks with a `pad_marking` decal under a `shuttle`, `conduit` and `screen_wall` (glowing monitors) walls, stacked `cargo_container`s, a `power_loader`, a `robot_arm`, `cables_hang` near the ceiling, a `reactor_core` (pair it with a cyan light) and amber `beacon`s with lights of their own; glaze a wall onto space with `glass_pane` cards between steel mullions. See `examples/orbital_hangar.py`, `space_station.py` and `derelict_ship.py`.

### On the Moon

A plain of `regolith` ringed by a crater rim of `rock` at several heights, the `space` sky with an `earth` in `sky_objects`, a low, hard, white `sun` (no fog at all - there is no air) and a very low ambient, so the shadows run long and black; greenhouse `dome`s glowing at different scales, `hab_module`s, a row of `solar_array`s, a `rover` with `rover_tracks` decals behind it, the `lander` on a `pad_marking`, `astronaut`s. For the lunar night drop the sun for a dim `moon`-type light from the Earth's direction and let the domes' windows light the base. See `examples/moon_base.py`.

### Alien worlds

The `alien` sky with a huge `ringed` planet and a moon or two in `sky_objects`, a `sun` light to match their lit side, `alien_ground` with outcrops of `alien_rock` (glowing veins), a pool of tinted water, `alien_plant`, `crystal`, a `monolith` on a raised plateau, and the `alien` scatter set; a `lander` and an `astronaut` for the visitors, the `alien` for the locals. See `examples/alien_world.py`.

### A sunken temple

The kelp forest's water - a dense teal fog (`[0, 0.16, 0.2]`, density about 0.045) with `shafts`, a high sun, a teal `grade` - over a temple: a platform of `ruin_paving` tinted sea-green, a ring of `column` objects of `marble` (`flutes` 16, `top` 0.8, `z` 0.3 on the platform) with a run still standing (`doric`, `capital`) under `beam` architraves and the rest `broken` low, a fallen `beam` block in the sand, `column_drum`s, the `marble_head`; corals and `reef_rock` set on the platform (`z` 0.3), `boulder`s of `reef` rock, `kelp` round it but not on the stones, a `manta_ray` high over it, `reef_shoal`s and `fish_school`s, a `sea_turtle`, the `diver` with `bubbles`. `fill` 0.6 on the marble keeps its shaded sides from going black in the green. See `examples/sunken_temple.py`.

### An aquarium

A dark hall (`marble_dark` with `reflect` 0.4, silhouettes tinted dark) in front of a tank of `seabed` under a `water_surface` roof (tinted down), its walls painted as open water (`["deep_water", "open_water"]`, two high) with rockwork along their foot - a `rock_wall` of `"rock": "reef"` down each wall, `depth` 1.4-1.8 and `height` about `[0.5, 1.45]` so the water shows over it, and `boulder`s with `plants` out on the sand - its window one long `glass_pane` floor to ceiling with `"glass": {"tint": [0.62, 0.88, 1.0], "blur": 0, "fog": true}` so the fog carries on into the water; light the tank with white lamps near its roof and let a blue fog (`[0.02, 0.1, 0.17]`, density 0.03, `glow` 0.5) do the rest; for sunbeams, mark a few roof cells `"glazed": true` (the ceiling stays, the sun shines through) and add a sun behind the tank with `shafts` 5. `whale_shark`, `manta_ray`, `reef_shark`, `sea_turtle`, shoals; `reef_rock`s and corals on the floor near the glass. Smaller tanks look through `tank_window` frames: `sea_nettle`s lit white against a `jelly_backdrop`, a reef of `anemone`, `brain_coral`, `staghorn_coral`, `sea_fan`, `angelfish`, `blue_tang`. A tunnel: glass down both sides and `tunnel_roof` overhead. See `examples/aquarium.py`.

## Wild places

### Dreams and the surreal

Fill the map with void and draw islands on it under the `dream` sky. They float over a sea of cloud, each with a ragged cliff underneath (`side` sets its texture). Then add a `sky_wall` with a door in it, a staircase to nowhere (`heights` with `height_unit` 0.3), a mirror lake (`obsidian` with `reflect` 0.9), and things adrift at a set `z`: `orb`, `koi`, `sky_whale`, `pocket_watch`, `floating_rock`, `balloon`. An `eye` in `sky_objects` watches. The `dream` post preset blows out bright pastel scenes, so use a gentle `bloom` instead. For impossible architecture: a plain of `checker_marble` (it mirrors), a giant chess game of `chess_piece` objects (turned in 3D in polished `white` and `black` marble, 1.8 to 3 tall; turn the knights a little off the camera's line, or they show only the thickness of their heads), a `clock` in `sky_objects` with `melt`, a `melting_clock` over a plinth, `stone_arch`es and `stair_float`s hung in the air, a stair out of the floor to a lone `door_frame`, a hole of void cells in the floor (give its rim a `sky_wall` side), `paper_boat`s on the polish. A drowned library: `bookshelf` walls three storeys high between `tall_window`s, a floor of `water` with `drop` and a high `reflect`, an island of books, and the air full of `jellyfish`, `sky_lantern`s, `book_fly`s, koi and a `sky_whale`; open a few cells of the roof as skylights and the sun comes down through them in beams in a dark, dense fog. An endless hall of doors: walls of `door_hall` at every storey (tinted per cell for doors of every colour) with `door_hall` as the ceiling too, a few `sky_wall` cells where a door has opened onto the sky, a `checker_marble` floor, a `stair_float` rising to a `door_frame` in the air, and the `dreamer` walking away down it. See `examples/dream_world.py`, `dream_chess.py`, `drowned_library.py` and `hall_of_doors.py`.

### Sky islands

A map of `void` with islands drawn on it (`"floor": "meadow", "side": "island_rock"` and a `cliff` of 2-3); hang a `keel` object under each (`size` the island's width plus a little, `depth` about 1.5 x its radius, `z` = -cliff) so it floats as a mountain of faceted rock (the `island_keel` prop is a billboard of one, for far islands), `island_roots` cards round the edges, a `waterfall` card off an edge (from a stream of `shallows` on top) with `z` at minus its `scale`. Raise one island on a block of `island_rock` with a `meadow` `top`; join two with a bridge of `planks` cells with `cliff` 0.12 and `rope_rail` cards along both sides. A `day` or `golden` sky, a light haze, `floating_rock`s, `seagull`s, trees, a ring of `column` objects of `marble` (`flutes`, `doric`) with `beam`s across the pairs that stand for a temple - lift them with `z` onto a raised island. See `examples/sky_islands.py`.

### A mirror salt flat

A big open map of `salt_water` with `reflect` 0.9 and `"reflections": {"ripple": 0, "smear": 0}` (a still mirror), islands of dry `salt_flat` with `reflect` 0, rows of `heap` objects of `salt` (0.15 to 0.3 tall, 1.75 times as wide, each a little different, `fill` 0.8 so their shaded sides stay white; the `salt_mound`, `salt_heap` and `salt_pile` cards are flat stand-ins) and `salt_clods` about, a little house of `salt_brick`; a `sunset`, `day`, `night` or `dream` sky with a low sun and `"skyline": "mountains"`, all doubled; a low camera (`height` 0.3) and one figure close enough to read with their reflection. Surreal touches stand well on it: a `door_frame`, an `armchair`, a `grandfather_clock`, a `sky_whale`. See `examples/salt_flat.py`.

### An aurora ice palace

`"sky": "aurora"` (rayed curtains of green light, no two stretches alike, a teal ribbon and red-tipped rays among them, brightest due north - aim north to have them over the scene); walls and towers of `ice_block` with an `ice_spire` on each tower top (`z` = the tower's height), `icicles` cards along the wall tops, an open hall of `frost_wall` round an `ice_throne`, `ice_shards` in the snow, `snowy_pine`s; a frozen lake of `ice_floor` with `reflect` 0.85 and `"reflections": {"ripple": 0, "smear": 0}` doubles the aurora. Light the snow green with a `moon` that has `"disc": false` and `color` [0.45, 1, 0.75]; ambient about 0.15; a gentle light bloom (1.3). Ice `crystal_cluster`s (`"color": "ice"`, `"rock": "snow"`) at the gate and round the throne bend the aurora and light the walls. See `examples/aurora_palace.py`.

### A glowing jungle (bioluminescent, at night)

Walls of `glow_leaves` with `"fringe": "glow_jungle"` round a clearing of `lumen_floor`, a pool of `glow_water` sunk with `drop` 0.1; `glow_monstera`, `glow_fern`, `glow_tree_fern`, `glow_heliconia`, `glow_bromeliad`, `glow_liana`, `glow_pods` and `glowshroom`s in clusters, big trees tinted dark; a few low coloured lights (cyan, violet, pink, intensity 0.6-0.9) among the plants and a brighter one on anything that should be seen (a stone head); `night` sky, a thin ground mist with `glow`, a handful of `spores` and `fireflies` (6 or so - more turn to snow), and a light bloom (strength 1.8). Stand at the water's edge: from further back a pool flattens into a line. See `examples/glow_jungle.py`.

### Vector World (the 80s computer world)

Black cells ruled in light - `vector_grid` (a wall of squares), `vector_windows`, `vector_bands`, `vector_data`, `vector_circuit`, `vector_frame` walls, each `{"base": ..., "tint": colour}` - over a `vector_floor` grid with `reflect` 0.4, under the `vector` sky with a sun of `"disc_style": "stripes"` (`disc_size` 8, `elevation` 9) and a fog the colour of its horizon (`[0.2, 0.05, 0.26]`). Put the shapes in `wireframes`: `terrain` mountains scaled wide and low beyond the map, `pyramid`s and polyhedra (`solid` for black faces edged in light), a `racer` with two `glint`s at its nose and a `light_trail` behind, `palm`s, a `gate` across the avenue, a `tower` with a `glint` on top for a beacon. People are `vector_runner`s (`tint` sets their light), and `light_beam`s ring a plaza. Light it with a strong light bloom; add `streaks` (anamorphic, `points` 2) for headlights and a `flare` (`"source": "light"`) for a beacon. See `examples/vector_world.py`.

### Doomed mode (a 1993 shooter)

`"ui": {"theme": "doomed"}`; in the shot's overlays a `statusbar` (`ammo`, `health` - the face bloodies below 80 - `armor`, `arms`, `keys`, `ammo_table`, `face`: `grin`/`ouch`), a `message` ("Picked up a clip.") and a `pistol` or `shotgun` viewmodel (`"fire": true`); aim with a 2-point `look_at` and `"pitch": -0.08`, `"light_levels": 16`, a near-black `fog`. The base: `nukage` sunk with `drop` and `"side": "slime_edge"`, `hex_floor` ledges and walkways, `green_trim` walls stacked storey on storey under a `tech_ceiling`, a `green_window`, `toxic_barrel`s, soldiers tinted sick green, a `corpse`, pickups, a `fireball`, `toxic_sign` decals. See `examples/doomed.py`.

## Road scenes

### An arcade racer's road

Three lanes (`width` 4.2), a kerb red and white, sand either side and the sea past it on one (`ground` in bands), palms along both sides every 7 (`palm` and `palm_lean`, `flip`ped on the right), billboards set back on the land side, a `curve_sign` before the first bend and a `checkpoint` over the road on a crest, cars ahead in their lanes; a low sun ahead in a `sunset` sky over the `islands` skyline. The camera 0.75 up and 2.6 behind a `sports_car` (the shot's `vehicle`), `pitch` 0.1. A second shot under the checkpoint with `roll` -6 and `yaw` -4 leans into the bend, the car level under the tilted world. Keep the fog thin (0.0035) and the ambient light (0.74, 0.66, 0.64), or the palms go brown in the sunset. See `examples/coast_road.py`.

### Verges that look lived in

A bare verge reads as a model railway. Scatter the small things along it - `{"of": "verge", "density": 1.2, "offset": [0, 3]}` for a country road (tufts, flowers, a stone, a bush, gathered in drifts with clearings between), `beach` on sand, `forest` or `jungle` along a path, `desert` by a desert road, a little `street` litter (`density` 0.06) along a city kerb - and mark the road itself: a `wear` row (`density` 0.03 to 0.06: cracks, patches, oil), `city` for a street (manholes too), `ruin` for a road gone to potholes, `trail` on a dirt path, `drifts` of sand on a desert road, and one or two placed marks where they tell a story - `tyre_marks` into a bend, a `lane_arrow`, a `zebra_crossing`. Keep marks on the road sparse: from a driver's height each is foreshortened to a sliver, so a few read as wear and many read as noise. See `examples/coast_road.py` and `examples/night_highway.py`.

### A mountain pass

The road cut into the mountainside: a `cliff_face` wall on the uphill side, `offset` 0.7, 9 high with a `ragged` top of 3 (`tile` 3.5), marker posts (`reflector_post` every 4) and the `alpine` scatter along its foot; on the other side a `guard_rail` (`offset` 0.2, 0.3 high, `"tile": [1, 0.3]`) and then nothing - that side's ground is `void` - and far below the valley, `below`: `depth` 70 and a `tile` of 33 (the landscape textures are drawn as seen from the air at about 33 units a tile), in bands along the road - `forest_canopy`, a `river_water` 8 wide, `pasture` - with `haze` 0.5 so the air down there is thinner than the scene's `fog` (0.0012). Close the valley with its far side: a wall of `cliff_face` 240 out, from `z` -70, 150 high, `tile` 30, `ragged` 40 - a ridge of broad peaks (the top's wander lengthens with `ragged`), hazy with the distance. Bends that climb (`rise` 2 to 3 on each), a `curve_sign` and a `speed_sign` before the first, a `goat` on the verge, the `mountains` skyline; a second shot at the rail, `yaw` 14 and `pitch` -0.05, looks out down the valley. A road runs alongside a valley, so its far side runs alongside too: a camera cannot turn to face across it, only look along it. See `examples/mountain_pass.py`.

### Off the road: a canyon

A dirt track (`dirt` tinted red, `width` 2.2, a `ragged` edge 0.3, two ruts - `tyre_marks` laid along it `every` 3.6, faint) over a floor of `desert_wash`, bumping over short rises. The canyon is `walls`: `slot_rock` on one side 3 out and 16 high, `sandstone` on the other 4 out and 13 high, both with `ragged` rims, and `sandstone_pale` 15 out and 34 high behind both; boulders fallen at their feet (`rocks` and `boulder` scattered `medium` to `huge` in a band along each wall's foot) and the `desert` set between. Set the sun to one side (`azimuth` 228): the far wall lights and the near one falls into shade. You drive a `jeep`; a `rally_car` ahead with a `dust_cloud` or two just behind it, low, half see-through (`opacity` 0.55-0.7). A second shot with `roll` -7 leans into a bend. See `examples/canyon_run.py`.

### On the water: a boat across a bay

The road is the sea: `surface` `sea`, no lines, no kerb, `bands` 0, the `ground` `sea` on one side and on the other in bands - more `sea`, `shallows`, `wet_sand`, `beach_sand`, `jungle_floor` - with palms and jungle trees on the land (`roadside` rows by density, out past the beach) and the `beach` set and rocks in the shallows (`scatter`). The water mirrors the sky and the shore; a sun low ahead (`elevation` 11) lays its image on it. Your boat is the shot's `vehicle`, `{"type": "speedboat", "ahead": 2.8, "z": -0.05, "wake": {"size": 1.3}}`; another `speedboat` ahead with a `wake` decal behind it, `sailboat`s (`scale` 3.4) off in the bay, a `buoy` row, gulls high and small. A second shot skims low (`height` 0.32) toward the shore. See `examples/island_run.py`.

### A canal tunnel by boat

`surface` `water` and `ground` `water`, `bands` 0, a gentle `ripple`; the vault is `brick_ring`s down the `middle` every 0.9 under a `roof` (light 0.25) - each frames the next, and the water mirrors them. `wall_lamp`s along both walls in turn every 8 at `z` 1.2, each with a warm `light` hung out over the water; a `narrowboat` ahead with a `light` in its cabin, set against the daylight at the tunnel's mouth (keep the bends gentle so the mouth stays in view); past it low brick walls. Your boat: `{"type": "boat_bow", "ahead": 1.25, "z": -0.1, "scale": 0.5}` with a `light` at its lantern. Murky `fog` (0.02) and a stronger bloom. See `examples/canal_boat.py`.

### The neon city: a race, and an avenue in the rain

The street is `walls` cut into buildings: shops at street level - `"texture": ["shopfront", "shopfront_b", "shopfront_c"]`, `blocks` 2.2 with a `tile` of `[2.2, 1.4]` so each shop is one tile - towers over them from `z` 1.4 (`tower_windows` and `tower_windows_b`, `blocks` 4.4, `ragged` 7 for their heights, `gaps` 0.12 for alleys), and taller towers 14 out behind (`ragged` 18) for the skyline. Make the road `wet` (0.26: a wet street; 0.42 is a canal) with a little `ripple`, cyan `lines` and magenta `edges`, and hang pink, cyan and amber lights along the shopfronts every 6: the street mirrors the windows, the signs and the cars. Signs out over the street (`neon_sign`, `holo_ad`, `neon_fish`, `neon_cocktail` at `z` 2 to 4.5), a `sky_train` crossing on its bridge (`z` 6.5), drones; racers ahead - `hover_car`s (`z` 0.06, `tint`ed) and a `neon_bike` - and yours as the `vehicle`, a racer's HUD over it, the strong neon bloom (2.2, spread 0.6). For the avenue: walk the pavement (camera `x` past the kerb, `height` 0.55), pavements 2.4 wide and wet too (`reflect` 0.18 on their band), `puddle_shine` decals on them, `lantern_span`s and `wires_span`s across the street, a `noodle_stall` with a light, `steam` from the road, a `zebra_crossing` with `traffic_light`s, a `taxi`, hover cars flying in lanes over the street (`z` 4.5 to 6.5), the `crowd` scattered with `clump` near 0 (people do not gather in drifts), and `rain` with `splashes`. See `examples/neon_race.py` and `examples/neon_avenue.py`.

### A roller coaster

The road is the track: `surface` `coaster_track` (rails and ties, see-through), `width` 1.4, no lines, no kerb, `bands` 0, the `ground` `void` and the park far `below` (`depth` 2.5 under the station: `city_park`, `pasture`, `farmland` in bands). The `sections` are the ride: the station (a `ceiling` of `planks` over its first units), the lift hill (`[30, 0, 22]`), a short crest, the drop (`[20, 0.15, -22]`), a banked curve at its foot, a camel back. The frame under the track is `walls` of `coaster_frame` from `z` -60, 59.9 high, a little in from the track's edges - the land below hides what is under the ground. Ride in the second car: `{"type": "coaster_car", "ahead": 1.25, "scale": 0.5}`. Over the drop, set the camera just past the crest and `pitch` it down hard (-0.55): the camera tilts by moving the horizon, so a steep drop needs a strong pitch to come into view. See `examples/roller_coaster.py`.

### A synthwave drive

Light on black: the `vector` sky, a sun with `disc_style` `stripes` (`disc_size` 9) at `elevation` 10 straight ahead over the `mountains` skyline - low enough to sit on them, high enough that its cut lower half clears them - the `ground` `vector_grid` tinted magenta (its lines glow), the road asphalt tinted dark violet with magenta `lines`, cyan `edges` and a kerb of pink and deep violet, palms every 8 `tint`ed almost to black so they stand in silhouette. The red convertible as the `vehicle`, a strong neon bloom. See `examples/synthwave_drive.py`.

### A desert highway

Two lanes of faded asphalt (tinted a little pale), a yellow centre `lines`, white `edges`, a `gravel` shoulder, pale `desert_wash` then `sand`. Make the `sections` long and nearly straight but give them real rises and dips - 3 units up or down over 50 to 70 - so each crest hides the road until it comes up again further on; a camera on a crest with a long lens (`fov` 46) shows it best. Buttes are `walls` far out (70 and 110), cut into `blocks` 26-34 long with `gaps` 0.55 - most left out - each its own height (`ragged` 9-10), banded `sandstone`; `saguaro`s by density, the `desert` scatter, `power_pole`s every 10 from 0 with `power_lines` between them (`"tile": [10, 0.6]` at `z` 3), a `billboard`, a `box_truck` ahead, sand `drifts` on the road. A noon sun, a pale hazy `fog`. See `examples/desert_highway.py`.

### A winter road at night

Asphalt with snow blown over it (`sand_drift` decals `tint`ed blue-white, more of them along the edges), the plough's banks low `walls` of `snow` (0.32 high, `ragged` 0.12) just past both edges, `snow` beyond, `snowy_pine`s by density, `reflector_post`s every 5; the moon over the `mountains`, a blue night (`ambient` 0.22, 0.26, 0.38), your `headlights` with a stronger `beam` and `snow` falling through them; drive in one lane (camera `x` -0.65) so a car ahead in the other shows its tail lights. See `examples/winter_road.py`.

### A mine ride

The road is the rails: `surface` `rail_track` (rails and sleepers on ballast), `width` 1.4, no lines, no kerb; `gravel` along its edges, `rock_floor` beyond. The tunnel is `walls` of `mine_rock`, `mine_rock_vein` and `mine_rock_gold` in `blocks` (a list: each stretch its own rock) 0.5 past the edge, a `ceiling` of `mine_rock` at 2.6 (`light` 0.3), and `mine_frame`s down the `middle` every 2.2 at `scale` 2.6 - narrow enough that their posts stand in front of the rock - each with a warm `light` under its lamp. Bends that dip (`rise` -1 to -2): a mine coaster; a few `crystal`s with their own blue lights in the rock, stones and `ore_heap`s at the walls' feet, a `pick_shovel`. You ride behind a `mine_cart` (the `vehicle`, `scale` 0.42), leaning into the bend. See `examples/mine_ride.py`.

### A space trench

The trench floor is the road (`hull_dark`, `hangar_floor` beyond); its walls are `walls` in `blocks` of a list of hull plating - `hull_lit`, `tech_panel`, `conduit`, `hull`, `hull_red` - 6 high give or take 1.2, and a tier of boxes along the rims (`z` 6, `gaps` 0.5); `sky` `space` with a `ringed` planet low at the trench's far end. Red and blue lamps along the walls every 7. Bolts of fire are `orb`s, `blend` `additive`, `fullbright`, tinted red, in pairs; `drone`s ahead, a `fireball` on the wall. You fly the `starfighter` (`z` 0.35, `scale` 0.4), banking. See `examples/space_trench.py`.

### A grand prix start

A wide track (`width` 5, one lane, white `edges`), kerbs striped red and white (`rumble` 0.4 wide, `stripe` 1 for short stripes), grass, then on one side a `jersey_barrier` with `chainlink` catch fencing on it and on the other `tyre_stack`s every 0.55; `grandstand` walls 3 out on both sides, 3 high (`"tile": [2, 3]`: one tile is the whole stand) with a roof edge over them. The field on the grid in two staggered columns - `race_car`s, `variant` for their liveries - the `start_lights` over the `start_line`, rubber laid down in the grid boxes (`tyre_marks` along it). You in your own car on the back row; a second shot from the side of the track. See `examples/grand_prix.py`.

### An ice road under the aurora

A track ploughed across a frozen lake: `surface` `snow` tinted grey-blue, the plough's banks low `walls` of `snow`, and either side the lake's `ice_floor` (it mirrors by its nature: the aurora lies in it, green, and the far shore's `mountains` upside down under the horizon). Raise the camera a little (0.95) so more ice shows; drifts of snow over it all (`sand_drift` decals tinted blue-white), marker posts along the track, a truck's tail lights ahead, the `aurora` sky, your `jeep`'s headlights. See `examples/ice_road.py`.

### A desert motel at night

The desert highway after dark (`night` sky, a moon, low blue `ambient`): a `motel_sign` on the left (`scale` 4.2) with a pink light beside it and the motel's rooms behind - a `wall` of `window_lit_plaster` 1.1 high (`"tile": [1.4, 1.1]`) with a concrete eave on it - and a `gas_station` on the right (`scale` 2.6) with a white light under its canopy and a car at the pumps; saguaros `tint`ed nearly black against the sky, power poles and their wires, your headlights. See `examples/desert_motel.py`.

### A sea tunnel

A road through a glass tube on the sea floor: `walls` of `viewport` (open glass between a frame at its foot and head, a rib at each tile's side: `"tile": [2, 2.6]`) and a `ceiling` of `tunnel_roof` (the deep water seen from below, the surface lit far above), lamps along the roof; outside, `seabed` with `reef_rock`, corals and `kelp` by density, and the sea's life at every height beyond the glass - a `reef_shark`, a `manta_ray`, a `sea_turtle`, a `fish_school`, `moon_jelly`s, a `whale_shark` far off. Make the `fog` thick and blue (0.06) with `sky_mix` 1, so the water closes in and the sky is all sea. See `examples/sea_tunnel.py`.

### A viaduct by train

The line (`rail_track`) between low parapets (`walls` of `stone` 0.42 high), the ground `void` either side and the valley far `below` in bands (woods, a river, pasture); `telegraph_pole`s every 9 with a `power_lines` wall at their arms (`z` 2.35), the engine's boiler ahead (`loco_boiler` as the shot's vehicle, `ahead` 1.6) and `steam` rising from its chimney and drifting back over the cab in three puffs, each nearer, higher and fainter; a `golden` sky and a low sun. A wall can only run along the line, never across it - a tunnel ahead needs a portal prop, not a wall. See `examples/viaduct_train.py`.

### A jungle river by canoe

The river is the road (`water` tinted green-brown, `bands` 0, a gentle `ripple`), its first band of ground river too, then mud, then `jungle_floor`; the jungle behind is a `wall` of `jungle_leaves` (`ragged` 2.5) with kapoks, palms, tree ferns and banana plants standing in front of it over the water and ferns, heliconias and reeds at the edge - the still water mirrors them all. A `canoe` ahead, a `heron` in the shallows, an `alligator` on the bank, a `stone_head`, `macaw`s overhead; your own `boat_bow`. See `examples/jungle_river.py`.

### A country lane between hedges

One narrow track (`width` 1.8, no lines, a `ragged` edge), the hedges `walls` of `hedge` 1.5 high just past its edges with a `ragged` top, the hedgerow's trees by density behind them (turned for the fall), leaves on the lane (`fall` and `leaf_litter` decals) and tufts at the hedges' feet; a little car ahead, a low sun in a haze. See `examples/autumn_lane_road.py`.

### A motorway in the rain

Both carriageways in one road (`lanes` 4), a `jersey_barrier` down the middle as a `wall` placed back over the road (`side` left, `offset` minus half the width), `highway_lamp`s down the `middle` with sodium lights; `car_oncoming`s in the far lanes, each with a `light` thrown out in front of it (`at` -2), tail lights in ours; `wet` 0.3 and the shoulder's band wet too, `rain` with `splashes`, a `dusk` sky. See `examples/rain_motorway.py`.

### A suspension bridge

The deck is the road over `void`, the bay far `below`; `bridge_tower`s down the `middle` every span (40) from 0 at `scale` 10, and the cables `walls` of `suspension_cables` along both edges, `"tile": [40, 10]` - one tile a span, so the main cable sags from tower to tower; a guard rail and lamps along the deck, a `dawn` sky over the `city`. See `examples/suspension_bridge.py`.

### A dark road to a dark castle

An old paved road (`ruin_paving` tinted, a `ragged` edge) across `black_sand`, then a lava field (`lava_field` with the band's `tile` 8, so its glowing cracks are big); dead trees `tint`ed black, broken columns, robed statues and bones along it, `brazier`s every 9 each with its fire's `light`; a `knight` walking ahead (`view` back), the `dark_castle` at the road's end (`scale` 34, a thin `fog` so it shows) with an `ash_plume` behind it, the `blood` sky and the `ashfall` preset. See `examples/dark_road.py`.

### A rope bridge between floating islands

The road is the bridge: `planks` 1.1 wide, its `sections` sagging in the middle and rising to the far side, rails of `railing` as `walls`, the ground `void` so the `dream` sky's clouds carry on below; `floating_rock`s by density at every height (`z` -8 to 6), a big one under the bridge's far end with a `stone_arch` on it, crows below, a traveller crossing. See `examples/rope_bridge.py`.

### An underworld river

A dark river (`water` tinted black-green) between banks of bones, the cavern's `walls` of `stone_dark` with a `ragged` top under a high `ceiling` of `rock` (`light` 0.35, so the walls still show); robed statues every 8 with a `brazier` at each one's feet and its fire's light - the water mirrors the flames - green wisps over it (`orb`s, `additive`, `fullbright`, tinted), a `stone_arch` spanning the river with braziers either side; your ferry's `boat_bow` and its lantern. See `examples/underworld_river.py`.

### A canal at night between old houses

The canal is the road (`water` tinted dark, `ripple` 0.35); a quay along one side (`flagstone`), the houses rising
straight from the water on the other: `walls` in `blocks` 1.6 long with a `ragged` top, a list of faces
(`canal_house`, `_b`, `_c`: plaster worn to the brick, a few windows lit) on a low wall of `canal_footing`. Striped
`mooring_pole`s off the houses in pairs, `wall_lamp`s and `lamp_post`s with their lights, two `canal_bridge`s
across, `washing_line`s strung over the water at `z` 2.4, a `gondola` ahead with its lamp, the moon over the roofs;
everything lit is doubled in the water. Your own `boat_bow` as the shot's vehicle. See `examples/night_canal.py`.

### A ski run

The run is the road: `piste` falling in steep `sections` that bend, then levelling out into a valley so the land
fills the view under the peaks (a run that only falls shows haze where the land drops away). Deep `snow`, then
`snow_forest` (`tile` 3) beyond; the orange safety net as see-through `walls` of `ski_fence`; the chairlift as two
`chairlift` walls at `z` 1.45 on `lift_tower`s; `snowy_pine`s by density. Red and blue `slalom_gate`s turn and turn
about down the course (`variant`), a `skier` ahead; `ski_tips` as the vehicle (`ahead` 0.85, `z` 0.3, `scale`
0.24) under a camera pitched down the slope (`pitch` -0.25). See `examples/ski_run.py`.

### A lane of light in the sky

The road is a `light_lane` (2 wide: a line of light at each edge and down the middle, chevrons between - it glows,
and it is see-through), the ground `void`, the city at night far `below` (`city_night`, `depth` 20, `tile` 10).
Towers stand either side as `walls` from `z` -20, `tower_windows` in `blocks` with `gaps` 0.45 so the city shows
between them, a farther rank taller still; neon signs hung out from them, hover cars in the lane and the lanes
above and below, yours as the shot's vehicle; `speed` 0.35 streaks it all past. See `examples/sky_lane.py`.

### A drive on the Moon

No road but the tracks: `regolith` for the road and the ground, `rover_tracks` decals down the middle and `crater`
decals either side at every size; boulders and rocks tinted pale. The base ahead - `dome` (lit), `hab_module`s,
`solar_array`s, a `lander` - an `astronaut` walking out; a `moon_buggy` as the vehicle. The `space` sky with the
`earth` over the horizon, a low sun, no fog. See `examples/moon_drive.py`.

### A bike ride through the bulb fields

A narrow path of red asphalt (`asphalt` tinted, no lines), then either side a strip of grass, a ditch of `water`
0.7 wide that mirrors the sky and the windmills, and the fields as ground bands 2.6 wide in turn - `tulip_field`,
`_b`, `_c`, `_d` - whose rows close up into stripes of colour to the horizon, `pasture` beyond; `reeds` along the
ditches, a row of trees far out every 2.2, `windmill`s in the fields (one near), two `cyclist`s ahead, and your
`bike_bars` as the shot's vehicle (`ahead` 0.8, `z` 0.17). A `day` sky and a high sun. See `examples/tulip_ride.py`.

### A runway at night

The runway is the road, flat and straight: `concrete` 6 wide, a dashed centre line (`lanes` 2, `stripe` 4) and white
`edges`, the threshold's bars a `zebra_crossing` decal 6 across. `runway_light`s every 1.5 down both edges, smaller
every unit down the `middle`, blue along a taxiway, red across the far end; an `airliner` lifting off ahead (`z`
1.0) with a light of its own, the `control_tower`, the terminal as a low wall of `tower_windows`, the `city`
skyline under a `dusk` sky (at full night the runway was a dark band under the cockpit). The view is from the
`cockpit` (the shot's vehicle), with `bloom` from the lights. See
`examples/night_runway.py`.

### A bayou by skiff

The channel is the road (`swamp_water`, still, `ripple` 0.3), its banks `bog` and then the swamp's water; `bald_cypress`
by density (hung with moss already - moss sprites set floating at a height read as clumps in the sky), `cypress_knees`,
the `swamp` scatter, a row of `swamp_card_3` far out as a wall of trees, `fireflies` over the water (`side`
`middle`), a heron and an alligator; a `stilt_shack` round the bend with a warm light, mirrored; your `boat_bow`
and its lantern. A `dusk` sky, a sun just down, a close fog. See `examples/bayou_run.py`.

### A camel caravan

`sand` (tinted warm) for the track and the ground, the edge ragged and blended so there is no road but the
caravan's; `sections` that swell up and down; the dunes beyond as a `hills` skyline in the sand's colour. A line of
`camel`s ahead, two `pyramid`s on the horizon by the low sun (`sunset` sky, a `sun` sky object), and the camera a
little to one side of the line so your own `camel_head` (the vehicle, `scale` 0.34) does not hide them. See
`examples/camel_caravan.py`.

### A candy road

`peppermint` for the road with `rumble` strips of white and pink, `frosting` for the ground, and a river of chocolate
as a band of `mud` tinted brown with a little `reflect` (0.15 - more and it mirrors the sky grey). `candy_cane`s
every 5 either side (`flip` the right-hand ones, so the crooks lean over the road), `lollipop` trees and `gumdrop`s
by density at every size, `gingerbread_house`s, the `dream` sky with a pink `hills` skyline; your car `tint`ed pink.
See `examples/candy_road.py`.

### A ghost train

Indoors all the way: the track (`rail_track` 1 wide) through `sections` that twist hard, a floor of dark `planks`,
the rooms as `walls` of `wallpaper` and `wallpaper_green` in `blocks` 3 long under a low `ceiling` of `wood_panel`
(`light` 0, so only the ride's own lights show) and a close dark fog. `portrait`s on the walls at `z` 0.9,
`cobweb`s high in the corners, `candelabra`s and `jack_o_lantern`s with their lights, a `skeleton` leaping out lit
green, the `ghost` drifting over the rails (`opacity` 0.75), `bats` overhead, a `grandfather_clock`; your
`ghost_car` as the vehicle with a dim purple light. See `examples/ghost_train.py`.

### A blossom road in spring

A narrow road of old asphalt (tinted pale, a slightly `ragged` edge), flooded paddies on one side (a broad band of
`water`) and grass and fields on the other; `cherry_tree`s every 4.4 either side, set back 0.9 and not too big, or
their crowns close over the road and hide everything; a `torii` over the road 10 ahead with the `snow_peak` behind
it in line (`x` 0, so the gate frames it) and a thin fog (much more and the peak is lost). Petals are the `snow`
post effect in pink (`"color": [1.0, 0.78, 0.86]`). A `dawn` sky. See `examples/blossom_road.py`.

### A storm chase on the plains

Two lanes dead straight over gentle swells (`sections` that only rise and fall), a `centre` line in yellow and a
`gravel` shoulder; grass, then `wheat_field` (`tile` 1.5) to the horizon; `telegraph_pole`s every 9 with a
`power_lines` wall at their arms. The `tornado` out in the fields ahead and to one side (`at` 110, `scale` 46), a
`barn`, a few `hay_bale`s; the `storm` sky with a low sun under it; the `lightning` post effect (`amount` 0.18, the
bolt placed with `x`). The `pickup_truck` as the vehicle. See `examples/storm_chase.py`.

### A submarine through a kelp forest

No road: `seabed` for the road and the ground, the edge blended away (`blend` 1); the surface overhead is a `ceiling`
of `water_surface` (it glows) at height 9, the murk a close teal fog. `kelp` by density, `light_shaft`s in the
`middle` by density, the `seabed` scatter; a `mini_sub` ahead with a light and `bubbles`, a `fish_school`, a
`sea_turtle`, a `reef_shark`, an `anchor`, a `wreck_mast`; marine snow as the `snow` effect, pale and faint, and the
`porthole` as the vehicle. Draw the road far (`distance` 300) under a dark sky - where the ceiling and the floor
stop, a sliver of sky shows between them. See `examples/kelp_run.py`.

### A ring station in space

The inside of a ring habitat: `sections` that each rise more than the last (0.4, 1.3, 2.2 ... over 10 units) so
the land climbs ahead and on up into the sky until it fills it. Fields, a river and forest either side in ground
bands, then a band of `void` - the floor ends at the rim - with see-through `walls` of `glasshouse` along the edge,
so space shows past them: the `space` sky, a `ringed` planet and the sun as sky objects. Trees by density, a car
ahead, your own as the vehicle. See `examples/ring_station.py`.

### A dog sled under the aurora

The trail is the road (`snow` tinted cold, 1 wide, the edge blended into the drifts, `tyre_marks` decals for the
runners' ruts); deep `snow` either side, `snowy_pine`s by density, the `snow` scatter; a `log_cabin` by the trail
with a warm light and `steam` from its chimney. The `aurora` sky, a moon's light, a thin cold fog. The `dog_team`
2.7 ahead of the camera (`scale` 0.55) is the team you drive. See `examples/sled_run.py`.

### A voyage under sail

The sea is the road and the ground (`sea`, `ripple` 0.8), the `islands` skyline far off, a `golden` sky and a low sun
ahead so the water carries its glow; a `galleon` ahead with a warm light of its own (its reflection sits in the
glow), a `sea_fort` on its rock off to one side, palms on a sandbar, a `seagull` or two. The `bowsprit` as the
vehicle (`ahead` 1.2, `scale` 0.75): its jib stands off to starboard, so keep what matters to port and ahead. See
`examples/high_seas.py`.

### A safari drive

A red dirt track (`dirt` tinted, the edge ragged into the grass) across `dry_grass` tinted gold, a low `hills`
skyline, a `sunset` sky with a big `sun` sky object low ahead; `acacia`s far apart by density and one near, a
`giraffe` or two under it, `elephant`s walking across the plain, `zebra`s in a knot (flip some), the `jeep` ahead,
the `dry_tuft` and rocks scatter. See `examples/safari_drive.py`.

### A close encounter on a desert road

Two lanes of old asphalt at night with a `centre` line, `desert_wash` either side, `telegraph_pole`s and their
`power_lines`, `saguaro`s; a `barn` and a few `cow`s by the road. The `flying_saucer` hangs over the road (`z` 4.2)
with a green light of its own; a `tractor_beam` stands under it at the same `at` and `x`, tall enough to reach the
saucer's port, a `cow` floating up inside it (tinted green); your car with its headlights on, the camera pitched up
(`pitch` 0.16) to take in the saucer. See `examples/close_encounter.py`.

### A fair at night

The midway is the road (trampled `dirt`, the edge blended into worn grass); stalls along both sides every 3.2
(`market_stall`, `food_cart`, `fruit_stall`, `gadget_stall`, each with a warm light), a `lantern_span` across now
and then (every 14 - more and it is a night market), `balloon`s, the `crowd` scatter along the stalls; the
`ferris_wheel` ahead to one side, the `carousel` behind the stalls on the other, both with lights. See
`examples/night_fair.py`.

### A frontier main street at noon

The street is the road (`desert_wash` tinted, no lines), a boardwalk of `planks` either side, then the buildings as
`walls` in `blocks` 2 long with a little `ragged` - `western_front`, `_b`, `_c` with `"tile": [2.0, 2.2]`, one
building to a tile. A `cowboy` standing square in the street ahead (`view` front), `horse`s at the rails every 7,
`tumbleweed`s, a `water_trough`, a `wagon_wheel`, the `water_tower` closing the street; a red `mountains` skyline
and a high sun. See `examples/high_noon.py`.

### A storm coast and its lighthouse

The road along a cliff's edge: `cliff_face` walls with a `ragged` top on one side, a `guard_rail` and then a `void`
side with the `sea` far `below`; `wet` 0.32 so the road shines, `reflector_post`s. The `lighthouse_tower` on a
headland ahead (`z` -6, `scale` 10), its `lighthouse_beam` at the lantern's height thrown back across the view
(`flip`); the `storm` sky, the `rain` post effect slanting, `lightning` far out, your car's headlights. See
`examples/storm_coast.py`.

### A volcano road

A dirt road through the jungle at night (`jungle_floor` either side) with bands of `lava_flow` out in the fields
(`tile` 4 - it glows); jungle trees and palms `tint`ed dark against the glow; the `erupting_volcano` at the road's far
end (`scale` 56) with a big red light of its own, an `ash_plume` over it, `fireball`s in the sky; the `blood` sky and
`ashfall`. See `examples/volcano_road.py`.

### A metro ride

Indoors: the track (`rail_track`) under a low `ceiling` of `concrete` (`light` 0); the tunnel as `walls` of
`tunnel_cables` with `wall_lamp`s, broken by a station (the walls `from`/`to`): `metro_tiles` set back behind the
platforms' faces (a low `concrete` wall 0.42 high), `ceiling_lamp`s under the ceiling, the `crowd` on the platforms
(`z` 0.42), a `signal_light`. The `metro_cab` as the vehicle with `headlights` - they light the tunnel. Put the
camera at the station's mouth: from deeper in, the tunnel's walls hide the platforms. See `examples/metro_ride.py`.

### A drowned city

The avenue is under still `water` (tinted, `ripple` 0.3) for the road and the ground; the towers rise out of it as
`walls` in `blocks` - `ruined_tower`, `_b` - with `gaps` 0.25 (fallen ones; the low sun comes through) and a `ragged`
top, a second rank behind taller still; all of it is doubled in the water. `driftwood`, logs and barrels floating
(`z` -0.08), a `lamp_post` drowned to its lamp, crows; your `boat_bow`; a `sunset` sky with the sun low at the end of
the avenue. See `examples/drowned_city.py`.

### A log flume

The flume is the road: `water` 0.9 wide between low `walls` of `planks` at its edges (`offset` 0, 0.35 high), the
`sections` level to the lip and then dropping steeply (7 down over 10); pines by density on `pine_needles` and
grass, a `surf` sprite for the splash at the bottom, a `ferris_wheel` over the trees; the `log_boat` as the vehicle
with the camera at the lip pitched hard down the drop (`pitch` -0.4). See `examples/log_flume.py`.

### A pilgrims' path in the mountains

A stony path (`gravel` tinted, the edge ragged) climbing gently; thin turf (`dry_grass` tinted down), scree
(`rock_floor`) and then `snow` in bands; `prayer_flags` across the path every 6 (`side` `middle`, `z` 1.4), a
`stupa` beside it every 18, stones scattered; a `monk` walking ahead (`view` back); `snow_peak`s far round the
valley (not too big, or they fill the sky) over a `mountains` skyline, a deep blue `day` sky, almost no haze. See
`examples/pilgrim_path.py`.

### A balloon flight

The balloon's way is a road too narrow to see (`width` 0.002) over `void` ground, the land far `below` (`depth` 26,
`desert_floor` at landscape scale), mesas as a red `mountains` skyline; `balloon`s scattered by density with a
spread of `z` (-12 to 8) and a few placed near, the sun low in a `dawn` sky; the `basket_rim` as the vehicle (`ahead`
0.6, `z` 0.3) under a camera pitched a little down. See `examples/balloon_flight.py`.

### A hayride and a sleigh ride

A hayride: a dirt farm lane at dusk, `pumpkin`s thick in the fields either side (density 2.2), `jack_o_lantern`s
along the verges with their glow, `scarecrow`s, autumn trees and a `barn`, crows; the `tractor` 5 ahead, the
`hay_wagon` as the vehicle, the camera up on the bales (`height` 0.68). See `examples/hayride.py`.

A sleigh ride: a lane of packed `snow` at night, `log_cabin`s along both sides with warm lights, `christmas_tree`s
between them, `lamp_post`s, snowy pines behind, the moon, the `snow` post effect; the `sleigh_horse` as the vehicle
(`ahead` 1.2, `z` 0.14) with a lamp's light. See `examples/sleigh_ride.py`.

### A steep city street by the bay

The street drops away in its `sections` (5.5 down over 20) with a dark `centre` for the cable's slot; a pavement
(`concrete_floor`) and then `harbor_water` either side, hidden behind the townhouses (`walls` in `blocks` of
`townhouse`, `_b`, `_c`) until they end at the shore (`to`) - then the street runs on across the bay to the
`bridge_tower`s in a thick fog. A `tram` going down, cars parked at the kerbs (start them a few units past the
camera), street lamps. Stand the camera at the brow of the hill (`pitch` about 0): looking down the slope itself
it reads flat. See `examples/hill_street.py`.

### A drive on a red planet

The Moon's kit, recoloured: `regolith` tinted rust for the track and the ground, `rover_tracks` down the middle (not
the `crater` decals - grey bowls on red dust read as puddles), boulders and rocks tinted; a `tornado` tinted orange,
scaled down and half see-through is a dust devil; mesas as a red `mountains` skyline, two small `moon`s, a `golden`
sky turned orange by a dusty `fog` (`sky_mix` 0.6); `dome`s, a `lander`, a `moon_buggy` ahead. See
`examples/red_planet.py`.

### An ice cave by boat

The river is the road (`water` tinted glacier blue), its banks `ice_floor`; the cave's `walls` of `ice_block` and
`frost_wall` in `blocks` under a low `ceiling` of `ice` with its `light` up at 1.0 - the daylight through the ice
makes the whole cave glow; a pale blue fog and a high blue ambient (darker, it read as a dungeon); `icicles` along
the walls' tops (`z` just under the ceiling), `ice_spire`s and `ice_shards` on the banks; your `boat_bow`. See
`examples/ice_cave.py`.

### A dragon flight

The way is the road, too narrow to see (`width` 0.002); the `ground` is `void` and the valley lies `below` (`depth`
30) in bands out from its middle - `river_water`, then `farmland`, then `forest_canopy` - bending as the way bends.
Props stand down there at a `z` of minus the depth: the `dark_castle` on its crag, scaled to rise over your level.
Dragons in their colours (`dragon`, `variant` 0-2) at every height and distance, clouds (`storm_cloud` tinted to the
dusk) drifting below you; a `sunset` sky, the sun low; your own `dragon_neck` as the shot's `vehicle`, wide and low
(`scale` about a third of its `ahead`, its `z` setting the head just under the horizon). See
`examples/dragon_flight.py`.

### An overgrown highway

A motorway years after everyone left: `asphalt` tinted pale, its `lines` a dull colour; the years in decals -
`crack`s thick on it, `pothole`s, `moss_patch`es, `vines` creeping in; weeds up through the road (`scatter` of
`overgrown`, `side` `road`, `clump` 0.8, `scale` 0.7) and `undergrowth` on the verges; the guard rails `guard_rail`
tinted rust. Trees crowd in (keep them a little back, or they hide the way ahead), a birch grows up through the
road; `wrecked_car`s where they stopped, a doe and her fawn on the asphalt, the `broken_overpass` across the way, a
`city` skyline unlit in the haze, a `golden` sky. See `examples/overgrown_highway.py`.

### A water taxi in the neon city

The neon avenue's street with the street turned to water: the canal is the road (`water` tinted violet, `ripple`
0.5), a ledge of wet `concrete_floor` either side (`reflect` 0.18), then the same walls - `shopfront`s in `blocks` at
the water's edge, `tower_windows` over them, taller towers behind - and coloured lamps along both sides. Signs hung
out over the water, `lantern_span`s (start them some way off, or the nearest fill the sky) and `wires_span`s across
it, a `holo_ad`, another boat ahead with a `light`, `hover_car`s overhead; the water mirrors it all. Your
`water_taxi` as the shot's `vehicle` (`ahead` 1.25, `z` -0.1, `scale` 0.5 - nearer and lower it falls out of the
view); bloom from the lights, and `rain`. See `examples/neon_canal.py`.

### A river of lanterns

A wide river (`width` 6, `water` tinted night blue) between grass banks; `floating_lantern`s scattered over the water
(a `roadside` row with `side` middle, `density` 3, `offset` across its width), every third or so carrying a warm
`light` so the water glows round them; `sky_lantern`s rising over the river and the banks at every height (`z`
spread, `scale` 0.35-0.6: smaller they are specks); `cherry_tree`s along both banks, a `torii` standing in the water
ahead with a light at its foot; a dark `mountains` skyline, the moon. Your `boat_bow` and its lantern; `bloom` 1.0.
See `examples/lantern_river.py`.

### Launch day

A straight causeway across a lagoon at dusk: `asphalt` with its lines, `ground` bands of a grass shoulder and then
`water` tinted to the dusk; reeds and a few palms along it. The `rocket_pad` at the road's end, a little off to the
side so the road leads to it (`scale` 34 at 150 - smaller it is lost on the horizon), `fullbright` as if the
floodlights were on it; cars pulled over on the shoulder and people by them (`crowd`); your convertible from behind
with its `headlights`, a `dusk` sky. See `examples/launch_day.py`.

### An airship voyage

As the balloon flight, from your own `airship_deck` (`ahead` 0.7, `scale` 0.24, its `z` setting the rail just
under the horizon): the course too narrow to see, the `ground` `void`, the clouds `below` (`cloud_floor`, `depth`
16). `floating_rock` islands at every height (a `roadside` row with `z` spread, and two big ones placed) with
`island_falls` pouring off their edges - their tops at the grass's near edge, about 0.85 of the island's height up -
`airship`s in their colours at every distance, gulls; the sun just up in a `dawn` sky. (The tall `waterfall` is a
cliff's - stood under an island it is a slab of glass.) See `examples/airship_voyage.py`.

### A ride through a medieval market

A `cobble` street with a strip of `flagstone` either side; the houses are one wall each side of `timber_house`,
`_b` and `_c` in `blocks` of 2.0 with a `tile` of `[2.0, 2.6]` and the wall 2.6 tall - each block exactly one tile,
so each is its own house with its own gable on the sky. Stalls (`market_stall`, `fruit_stall`) from some way up the
street (the nearest ones fill the view), `banner`s on the houses at `z` 1.4, barrels, sacks and hay along the
fronts; the townspeople are the characters (`villager`, `farmer`, `shopkeeper`, `monk`, `child`, a `knight`
walking away), a `cart`, a `well`; the `castle_hill` at the end. Your `horse_neck` as the shot's `vehicle`, the
camera a rider's height (0.8). See `examples/market_ride.py`.

### A mountain pass at night, the city below

The mountain pass's road (the cliff on one side, a `guard_rail` and the `void` drop on the other) under a `night`
sky, and far `below` the city at night: `city_night`, its lights glowing in the dark (`tile` 18 shows its avenues as
a grid - smaller it is noise; `haze` 0.35 fades the far side). A rival car ahead, reflector posts and a curve sign
for the headlights to find, your convertible with its `headlights`; bloom from the lights. See
`examples/night_pass.py`.

### A road through the giant redwoods

A two-lane road with a yellow centre line through `pine_needles` and `moss`; `redwood_trunk`s in a row near the
road (`every` 10, `offset` 1.0-1.8, from 10 on - where the road bends a near one stands in front of you) and more
back in the wood (`density` 0.1 out to 16), ferns and `undergrowth` between; a high `ceiling` of `canopy` (16 up,
`light` 0.7) closes the sky; `light_shaft`s slant down through a green-gold `fog`. Your convertible from behind.
See `examples/redwood_road.py`.

### Rafting the canyon rapids

The river is the road (`river_water`, `ripple` 0.8) dropping away section by section; rapids hardly mirror, so its
`wet` is 0.1 (left at the water's own it was a smooth mirror of the walls); `foam` decals thick over it, two rows of
them in different sizes, for the white water; `boulder`s in the stream (`side` middle) and on the gravel banks; the
canyon run's walls (`slot_rock`, `sandstone`, paler rock behind). Your `raft_bow` as the shot's `vehicle` (`ahead`
1.0, `z` 0.12, `scale` 0.28). See `examples/canyon_rapids.py`.

### A salt flat after rain

No road but your tracks: the `surface` and the `ground` are both `salt_flat`, the ground's band mirroring nearly all
of the sky (`reflect` 0.85) and the surface the same (`wet` 0.85), `tyre_marks` down the middle; a `mountains`
skyline, the sun on the horizon of a `sunset` sky. Anything standing on it is doubled - a figure out on the water, a
truck far ahead, your jeep. See `examples/salt_mirror.py`.

### An asteroid field

The course is the road, too narrow to see, the `ground` `void` both sides so the `space` sky runs on below the
horizon. `asteroid`s at every height and distance - a `roadside` row across the course (`side` middle, `z` spread,
from a little way ahead) and another out to the sides, bigger - and a few big ones placed near; two `starfighter`s
ahead as wingmen (out to the sides, or the rocks hide them); a `ringed` planet; a hard sun from the side and little
ambient light. Your starfighter from behind as the shot's `vehicle`. See `examples/asteroid_field.py`.

### A lost valley of dinosaurs

A `dirt` track with ragged edges through `jungle_floor`; tree ferns and palms thick along it (back from the track a
little) and ferns under them; `sauropod`s crossing far ahead at `scale` 9-11 (a thin `fog`: thicker, they fade to
ghosts), a `tyrannosaur` at the jungle's edge near the track, `flip`ped to face it; the `erupting_volcano` far off and
small; dark winged shapes high up (`crow` tinted, scaled up); a `golden` sky. Your jeep from behind. See
`examples/lost_valley.py`.

### A midnight ride

A `mud` lane with ragged edges between `leaves_fallen` and `dry_grass`; `dead_tree`s crowding both sides,
gravestones and crosses among them near the lane; `orb`s as will-o'-wisps at every height, a few with a violet
`light` (a tint leaves their glow its own colour); the `ghost` by the lane; crows; the `dark_castle` at the end; a big
moon and a cold blue `fog`. Your `horse_neck` as the shot's `vehicle`, carrying a lantern's warm `light`. See
`examples/midnight_ride.py`.

### A longship up a fjord

The fjord is the road (`width` 9, `water` tinted cold), a strip of `rock_wet` at the cliffs' feet; the cliffs are
`cliff_face` walls 26 high and ragged, a unit out from the water, taller ones far behind (closer, the sky was a slit);
`island_falls` pouring down their faces (the tall `waterfall` is too wide to hang off a cliff in a fjord: it reads as
a slab), pines on the ledges (`z` spread up the cliffs), gulls; a `dawn` sky with the sun low down the fjord and a
warm mist (under `overcast` it was all one grey). Your `longship_bow` as the shot's `vehicle`. See
`examples/fjord_voyage.py`.

### A tunnel of torii gates

A `flagstone` path climbing gently (`moss_stone` at its edges, `moss` beyond); `torii` in a `roadside` row over
the path (`side` middle, `every` 0.9, `scale` 2.2), so close they make a tunnel of red; small `red_lantern`s at their
feet, a warm `light` in each; pines crowding the slope behind them; a low `golden` sun. On foot. See
`examples/torii_path.py`.

### A path through a bamboo grove

A `gravel` path between low fences of the dry `bamboo` texture (walls 0.45 high at its edges); `bamboo_stalks`
crowding both sides at `scale` 8-11 - a dense row from a few units ahead (nearer they are fat as trunks) and another
farther back - so the grove closes over the path; a high `ceiling` of `jungle_leaves`, lit, for the canopy; a
green-gold `fog`; the `samurai` walking away ahead (where the path bends the stalks hide him: it runs straight
first). See `examples/bamboo_path.py`.

### A scooter through the lavender

A narrow lane (`asphalt` tinted pale, no lines) with dry verges, then `lavender_field` to the horizon (its rows run
along the road and close into purple bands); `cypress`es in a line along one side, `olive_tree`s out in the fields;
low blue `hills`, a `golden` sky. Your `scooter_bars` as the shot's `vehicle` (`ahead` 0.7, `z` 0.33, `scale`
0.24: the mirrors just under the horizon). See `examples/lavender_ride.py`.

### A ghost ship at midnight

The sea is the road and the ground (`sea`, `ripple` 0.2); a cove's rocks close either side (`cliff_face` walls,
low and ragged, `to` 14 so it opens out ahead); the `galleon` tinted ghost green, half see-through (`opacity` 0.6)
and `fullbright` - lit from within, so it glows pale in the dark - with a green `light`, `scale` 6.5 at 21 (smaller
it was a toy in the cove's mouth), another fainter farther off; `orb`s floating on the water; a big moon, a cold
`fog`. Your `boat_bow` and its lantern. See `examples/ghost_ship.py`.

### A cattle drive

No road but the trail the herd has beaten (`dirt`, wide, its edges ragged and blending into `dry_grass`); `cow`s
tinted brown for range cattle, a dense `roadside` row on the trail itself (`side` middle, from a few units ahead)
and a thinner one out to both sides; `dust_cloud`s half see-through over the herd; `cowboy`s on `horse`s out on
the flanks; red buttes as a `mountains` skyline, a `sunset` sky. Your `horse_neck` as the shot's `vehicle`. See
`examples/cattle_drive.py`.

### A dive on a coral reef

No road but the sand: `reef_flat` for the floor and the way, its edges ragged; the reef wall rising along one side
(`reef_wall`, ragged); the surface a bright `ceiling` of `water_surface` close overhead (`light` 1.0); corals
crowding both sides (`brain_coral`, `staghorn_coral`, `anemone`), clownfish and angelfish, a `fish_school`, a
`sea_turtle`, the `manta_ray` and the `whale_shark` overhead, `light_shaft`s; your buddy the `diver` swimming ahead
(`z` 0.7) with `bubbles`. A turquoise `fog` with `sky_mix` 1.0 - and a dark sky, drawn far - or the sky shows as a
band where the ceiling ends; marine snow. See `examples/reef_dive.py`.

### The clockwork city's high street

The clockwork kit along a road: a `cobble` street with `flagstone` pavements; `brass_plate`, `copper_pipes` and
`clock_face` walls in `blocks` of their own heights, taller ones behind; `brass_gear`s up the fronts (a `roadside`
row at the walls' face with `z` spread), `steam` from them half see-through, `lamp_post`s with warm `light`s; a
`great_clock` on a front; the `tram` tinted brass ahead; `airship`s overhead; a `sunset` sky in a brown smog. On
foot. See `examples/brass_city.py`.

### A winter market at night

The market ride's street turned to a snowy night: `cobble` tinted cold, `snow` either side, the houses
`timber_house_night` - their windows lit - in `blocks`; the stalls with warm `light`s of their own (a roadside row's `light` lights every one), gaslit
`lamp_post`s; the townspeople; the `christmas_tree` in the square ahead with a light at its foot; the `castle_hill`
tinted to the night; `snow` falling and bloom from the lights. See `examples/winter_market.py`.

### A snowmobile under the aurora

A frozen lake: `ice` tinted cold for the way and a wide band of the ground, polished enough to mirror the sky (`wet`
0.6 on the way, `reflect` 0.6 on the band), then `snow` at the shore; `snowy_pine`s along it and `log_cabin`s with
a warm `light` each; two `snowmobile`s ahead, their tail lights glowing; the `aurora` sky, doubled in the ice. Your
`snowmobile_bars` as the shot's `vehicle` with its `headlights`. See `examples/aurora_lake.py`.

### A highway at night, and a tunnel

Edge lines, a `gravel` shoulder, concrete beyond; `lamp_post`s every 9 down both sides, each with a sodium `light` hung out over the road (radius 6.5, intensity 1.5), so the road lies in pools of orange; cars ahead `tint`ed dark - a tint darkens a car, not its tail lights, which glow. Where it bends into a hill a `tunnel_portal` stands across it, `tunnel_ring`s every 1.2 down the `middle` carry the tunnel on, `roofs` cover that stretch, and lights every 4 at 2.8 along its roof; your car's `headlights` on. From inside, the rings make the tube and their lamps a line down its roof, the city at the far end. See `examples/night_highway.py`.

### A path through a wood, or a jungle

A path is a road with no lines and no kerb: `width` 1.5, `surface` `dirt` (or `mud`), `edge` `{"ragged": 0.16, "blend": 0.35}`, the ground in bands - a verge of `grass`, `moss`, then `pine_needles` (or all `jungle_floor`). The wood is rows by `density`: trees 1-7 out at about 1 to a unit and more behind them, bushes, ferns and tufts at the path's edge, now and then a stump or mushrooms; a figure walking ahead, seen from behind (`view` back). A low sun ahead in haze (`fog` 0.035) closes the far end. Let the nearest trees frame the shot (`clear` 0.5). In the jungle, kapoks well back and only past the camera (`from`), palms, tree ferns and banana plants, monstera and heliconias at the edges, a `stone_arch` over the trail with a `stone_head` beside it and an explorer walking toward it. See `examples/forest_path.py` and `examples/jungle_trail.py`.

### A fairy-tale path at night

`cobble` through a verge of glowing moss (`lumen_floor`), the glowing jungle's plants and `crystal`s at its edges, dark trees `tint`ed blue behind, giant `glowshroom`s every 8 each with a teal `light`, wisps (`orb`, `blend` `additive`, `z` between 0.4 and 1.1) over the path; two moons in `sky_objects`, `fireflies` (`count` 16, `size` 0.6) and a strong bloom. Give the figure on the path a lantern - a `light` on its sprite - or it is a shadow. See `examples/enchanted_path.py`.

### A road in the sky

`ground` `void` and the `dream` sky: the road floats over its sea of cloud. `marble`, a gilded kerb (the `rumble` in gold), `column`s along its edges (`offset` -0.12, back onto it), a `stone_arch` over it every 18, `floating_rock`s off to the sides at heights between -3 and 5, a `sky_whale` far off and high, balloons in the distance; the sun low ahead. See `examples/sky_road.py`.

## Landscape scale

### A kaiju in the city

A city seen as a giant sees it (see Landscape scale in scene_format.md): a grid of `city_street_lit` cells with a `city_block` object at the middle of each - their `height`s tall downtown (up to 1.5), lower out from it (`[0.1, 0.5]`), low warehouses along the waterfront (`[0.04, 0.14]`), `lit` 0.4-0.5 - a `city_park` and a `container_yard`, and a `quay` along the `harbor_water`. The `kaiju_wading` stands in the shallows off the quay; `searchlight`s on the roofs swing toward it (`elevation` 14-34) and a few sweep the sky, `helicopter`s hold it in `ray`s, `tanks_firing` line the quay, and the waterfront burns - `blaze`s with a `smoke_plume` over each and an orange light (`radius` 1.5) under it - while from the air its breath, a cyan `ray`, cuts into a tower downtown. A `night` sky with the `city` skyline, a low moon, `ambient` about 0.13, a thin `fog` (`density` 0.035) with `glow` 0.7, and a light `bloom` on every shot. Put a camera on the quay at a person's eye (`height` 0.012) or a boat's (0.035) and the monster towers; mark the searchlights and the breath `"night": true` and a shot's `"time": "golden"` turns the same city to the next day; a `giant_moth` over the bay, added by a shot's `overrides`, makes a monster fight. See `examples/kaiju_harbor.py`.

### A kaiju in the country

A plain of `farmland` (`farmland` to `farmland_f` at random) with woods of `forest_canopy` in it, small trees along their edges (a `scatter` with `scale` 0.09), crossed by country roads (`road_ew`, `road_ns`, `road_x` where they meet) with a market town at the crossing: a few `city_street` cells with low `city_block`s (`height` `[0.03, 0.1]`) and a `village` beside them. A line of `pylon`s across the fields, each turned square to the line, `cable`s slung from arm to arm (`sag` 0.09); the `kaiju` walking in beside the line - a pylon nearly its height makes the scale - `jet`s over it, `helicopter`s at its shoulder, `tanks_firing` on the road, a wood burning where it has walked (`blaze`, `smoke_plume`, an orange light). Rounded `mountain`s to the north (`"snowline": 0`), the `hills` skyline, `"time": "afternoon"`, thin fog. Keep cameras over fields at 0.07 or higher and close in: from a rooftop at the edge of town, a helicopter at its shoulder, the foot of a pylon looking up, and a long lens (`fov` 19) at golden hour. See `examples/kaiju_country.py`.

### A volcano island

An island of `black_sand` round its shore and `forest_canopy` within, old lava (`lava_field`) on one side, in a dark sea (`harbor_water`); in the middle a `mountain` of `volcanic` rock (`size` 21, `height` 9, `"snowline": 0`) with a `crater` (0.06) and `lava` aimed the way the cameras look (`[80, 112, 150]`), a river of `lava_flow` cells going on from its foot to the shore and white steam (`smoke_plume` with a pale `tint`) where it meets the sea. Lava fountains over the rim: four or five `blaze`s at scale 2-3.5 round the crater, `z` just under the rim; an `ash_plume` over it, tinted warm; an orange light of radius 11 at the crater, more up the ash column and along the river. A harbour town on the shore (`city_street_lit`, lit `city_block`s, `quay`). `night` sky, low `ambient`, fog with `glow`, a light `bloom`. Shoot it from the sea, from the town's quay, from the air over the lava field and from a boat off the delta. See `examples/volcano_island.py`.

### A mesa desert

A plain of `desert_floor` (`desert_floor`, `_b`, `_c` at random) with a highway straight across it (`desert_road`), and the monuments: `mountain`s of `sandstone` or `canyon` rock with a `cliff` - long mesas (`size` 9-12, `length` 20-40, `height` 3-3.6, `cliff` 0.5-0.6), buttes (`size` 4.5, `height` 4, `cliff` 0.7) and spires (`size` 1.4, `height` 2.6-3.2, `cliff` 0.85), `"snowline": 0`, `ridges` 2-4, each with `"casts": true` so the low sun throws its shadow across the plain. A lone ranch by the road (a `village` of four, `"church": false`). The `mountains` skyline, thin warm fog, `"time": "golden"`. Shoot it down the road (`height` 0.04), from the air, against the sunset (`"time": "sunset"`, looking west) and by moonlight (`"time": "night"`). See `examples/mesa_desert.py`.

### A winter valley under the aurora

The `aurora` sky - its great curtain is due north, so look north up the valley. A valley floor of `snow_fields` (and `_b`), flanks of `snow_forest` with `snowy_pine`s along their edges (a `scatter` with `scale` 0.09), a `frozen_lake` (mix `_b` and `_c` so it does not repeat) and a `village` on its shore with `"snow": true` and `lit` 0.55, warm lights of radius 0.7 among its houses marked `"night": true`; `mountain`s all round with `"snowline": 0.02` so they are white to their feet. A low moon, `ambient` about 0.15, cool and blue; a light `bloom` makes the windows glow. Shoot it across the ice to the village, from the village street to the white peak, and the morning after (`overrides`: `"time": "morning"`, `"sky": "day"` and a brighter `ambient` and fog). See `examples/winter_valley.py`.

### A strait bridge

Two shores across two kilometres of `harbor_water`, `black_sand` along them, woods and pasture in patches (not cell by cell - a checkerboard reads from the air), rounded hills behind (`mountain`s, `"snowline": 0`); a town where the bridge comes ashore. The `bridge` across: `length` from shore to shore, `deck` 0.55, `height` 1.9, `"lit": true`. Under it a `cargo_ship`, a `ferry` and `sailboat`s; a `lighthouse` on a point at `scale` 0.04. Keep the cameras on the water - from a shore, the foreground is woods seen from a few metres up. Golden hour, and dusk for the lamps. See `examples/strait_bridge.py`.

### An archipelago

Deep `ocean` and islands in it, each ringed outward from its middle: `palm_canopy`, a rim of `white_sand`, a band of `lagoon` and then `reef_flat` before the open sea; an atoll is the same ring round a lagoon of its own. Give the high islands a hill - a `mountain` of `tropical` rock, `"snowline": 0`, low (`height` 1.3-2.4) - and a `village` on a shore with `"roof": "thatch"` and `"church": false`; `palm`s scattered on the palm cells at `scale` 0.07; `sailboat`s in the lagoons, a `ferry`. The `islands` skyline, a bright `ambient`, `"time": "afternoon"`. Shoot it from a boat, from the air and from an atoll's beach across its lagoon. See `examples/archipelago.py`.

### A valley from a giant's height

A river (`river_water`) winding down the middle of the map between `pasture` water meadows, the valley floor in `farmland` - `farmland` to `farmland_f` picked at random cell by cell, so the fields join up into one countryside - and up the flanks `forest_canopy` woods and then `pine_canopy`, small pines along their edges from a `scatter` with `scale` 0.09. `mountain` objects down both sides (`size` 12-16, `length` 16-24 to draw each out into a ridge, `height` 5.5-9.5, turned with `angle` 90 along the valley) and a great peak at its head (`size` 30, `height` 16, `ridges` 6), snow on their tops; a `village` by the water (`size` 3.2, `count` 26) with an old stone `bridge` over the river (`"style": "stone"`), and a hamlet upstream (`"church": false`). `"time": "dawn"`, the `mountains` skyline, a mist along the valley floor (`fog` `density` 0.008, `ground` 0.22, `height` 0.1) and `max_distance` 80. Shoot it from a giant's eye (`height` 0.6) up the valley, from the air (`height` 4), or low over the village. See `examples/giant_valley.py`.

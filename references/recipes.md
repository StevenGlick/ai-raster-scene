# Recipes: how to build particular places

Each recipe is the textures, props, sky and light that make one kind of place read, and the scene
file in `examples/` that shows it. Read the one for the place you are drawing (and the general
advice in SKILL.md, "Making it look good"), then write the scene. Every name here is in
`references/scene_format.md` and `references/assets.md`.

## Out of doors

### Woodland

Fill the grid with `forest_deep` wall cells (trunks receding into the dark) about 2.4 high with `"fringe": "forest"` and carve the paths and clearings out with `maptools.Grid.rect` and `disc`. The fringe stands four layered cards in front of every face onto open ground - a dense wall of spruce and oak, then younger trees, then bushes, ferns and grass - so leave a cell of open ground in front of the walls and make paths two cells wider than they should look; the tree tops on the cards make the skyline. Stand `pine` (a spruce), `tree` (an oak), `birch`, `dead_tree`, `bush`, `stump`, `log`, `boulder`, `fern` and `mushrooms` in the clearings. Floors: `pine_needles`, `moss`, `mud`; `bark` and `bark_pine` walls for trunks; `foliage_autumn` for the fall. The wood in autumn: `forest_deep_autumn` walls with `"fringe": "forest_autumn"`, `leaves_fallen` underfoot, `tree_autumn`, `birch_autumn` and `bush_autumn` standing free and the `autumn` scatter set on the verges; at a field's edge a `scarecrow`, `pumpkin`s, `hay_bale`s and `crow`s, and `jack_o_lantern`s lit at dusk; the `leaves` post effect sets leaves falling. Light it with a low sun at the end of a lane in a thin, dark-gold fog (a pale or dense one blows out toward the sun). The wood in winter: `forest_deep_snow` walls with `"fringe": "forest_snow"`, `snow` underfoot, `tree_winter`, `birch_winter`, `snowy_pine` and `bush_snow` standing free, a stream of `ice` sunk with `drop` 0.08 under a footbridge of `planks` blocks 0.14 high, a `deer`, the `snow` scatter set; keep any ground fog thin or the snow and the mist run together, and add the `snow` post effect for falling snow. See `examples/woodland_night.py`, `autumn_lane.py` and `winter_woods.py`.

### Standing stones

Build them as wall cells of `["menhir", "menhir_top"]` at different heights (a `heights` layer), each with a `stone_cap` sprite on top so the circle's outline is not a row of boxes. See `examples/misty_moor.py`.

### Jungle, ruins and beaches

A jungle is walls of `jungle_leaves` at a few heights (2.5-4) with `canopy_top` tops and `"fringe": "jungle"`, which stands four layered cards of trees and bushes in front of every face that looks onto open ground - so leave a cell of open ground in front of the walls for it, and make paths two cells wider than they should look. Add a `canopy` ceiling over the paths with a few cells left open for shafts of sun in the mist, `kapok` giants standing clear of it, and `canopy_crown` props on the wall tops so its edge is rounded crowns; plants (`banana_plant`, `monstera`, `heliconia`, `tree_fern`, `liana`, the `jungle` scatter set), a `jaguar` and a `macaw`. A stepped pyramid is rings of `heights` a unit apart, each tier's wall stack ending in `temple_cornice`, stairs up one face, a `temple_door` shrine and a `roof_comb`. Classical ruins: the colonnade wall stacks, `column` props scaled to ~3 along a sacred way, `limestone`, `ruin_paving`, `dry_grass`, `cypress`, `olive_tree`, `marble_head`, `goat`, a `hoplite`, the `ruins` scatter set, under `golden`. A beach: `beach_sand`, a band of `wet_sand`, `shallows` then `sea`, all at ground level; a row of `surf` props along the waterline, `palm` and `palm_lean`, a hut of `["bamboo", "thatch"]` walls, `tiki_torch`, `canoe`, `hammock`, the `beach` scatter set and the `islands` skyline under `sunset`. See `examples/jungle_temple.py`, `ancient_ruins.py`, `tropical_beach.py`.

### Deserts and canyons

Carve a wash out of rock cells stacked in bands (`["sandstone", "sandstone", "sandstone_pale", ...]`, 5-7 high) and give the rim a few heights so the skyline is ragged; nudge the canyon's edges in and out a cell here and there so the walls are not a corridor. A `desert_wash` floor with the `desert` scatter set, `saguaro`s and `prickly_pear`, a `cow_skull`; the ruins of a cliff dwelling are low blocks of `pueblo_stone` with `pueblo_door` cells, a `ladder` and `clay_pot`s. A `rock_wall` of `"rock": "sandstone"` along a wall's foot and a few sandstone `boulder`s break up a canyon floor's straight edges. For a slot canyon, a winding gap two cells wide in `slot_rock`, its cells roofed (`ceil`, with `ceiling_height` under the rim) and one cell left open: a high sun comes down through it in a single beam in a warm, dusty fog with strong `shafts`. See `examples/red_canyon.py`.

### Swamps and bayous

`swamp_deep` walls (about 2.6) with `"fringe": "swamp"` round open water of `swamp_water` sunk with `drop` 0.12 and a `bog` `side`, `bog` hummocks and an island; `bald_cypress`es standing in the water with `cypress_knees` round them, `cattails`, `lily_pads` decals, a `heron` in the shallows, an `alligator` with only its eyes up; a shack of `boards` with a lit window and a lantern on a porch of low `boards` blocks, a `rowboat` at the landing. Frame the shack between two near cypresses and keep the fog thin (0.008-0.012) or the far side vanishes; at night add `fireflies` and a `bloom`. See `examples/bayou.py`.

### Under the sea

Make water of the air - a dense teal fog (`[0, 0.15, 0.19]`, density about 0.05) with weak `shafts`, a high sun from behind the camera, and a teal `grade` post (`tint` `[0.74, 0.98, 1.05]`); a `seabed` floor, `kelp` stalks 4-5.6 tall scattered at random with a clearing, low `rock_wet` ledges with `"fringe": "kelp"` round the edge, `fish_school`s at different `z`, the `seabed` scatter set and `starfish`, `shells` and `seaweed` decals; a wreck of low `planks` blocks with a `wreck_mast`, an `anchor` and a `chest`; a `diver` with `bubbles` rising from the helmet. For a night dive: `flashlight`, a black fog and glowing `jellyfish`. See `examples/kelp_forest.py`.

### Castles and dungeons

`castle` walls, `flagstone` floors, `beams` ceilings, `stained_glass` (glows) in a storey of the wall, `portcullis` and `bars` for gates and cells, with `throne`, `armor`, `banner`, `chains`, `chest`, `table`, `sconce` and `brazier`. Chapels: `stone_pale`, `pew` with `stretch`, `lectern`, `candles` on a raised altar. Caves: `rock_wet` walls lined with a `rock_wall` of `"rock": "cave"` (`"lining": "#"` lines every wall face of those cells; `lumen` rock grows glowing moss) round a sunken pool of `glow_water`, `crystal_cluster`s - each carries its own coloured light - and `glowshroom`, `glow_fern` and `glow_pods` on `lumen_floor`, `stalagmite`, the `cave` scatter set; keep the ambient low but not black (about 0.08) and the mist thin, or the walls vanish. Sewers: `slime_brick`, `pipes`, a sunken channel with `railing`. Winter: `snow`, `ice` (reflective), `snow_rock`, `snowy_pine`, `boulder_snow`, `snowman`, and the `snow` scatter set (stones and snow-capped boulders) instead of `stones`, whose boulders are mossy. See `examples/castle_keep.py`, `chapel_graveyard.py`, `crystal_cave.py`, `sewer_tunnels.py`, `winter_lake.py`.

### Haunted houses

A double-height hall (`ceiling_height` 3) with walls stacked `["wood_panel", "wallpaper", "wallpaper"]` and a `beams` ceiling; a grand staircase from the `heights` layer (a straight flight of 0.2 steps with `carpet` tops up to a landing block at 1.4) with `balustrade` cards along the landing's edge at `z` 1.4; `portrait`s on the walls, `candelabra`s (with warm lights) on the floor and the landing, a `chandelier`, a `grandfather_clock`, `armor`, `cobweb`s across the corners, a `fireplace` with an `armchair`, and the `ghost` on the stairs. Outside: a dark front with a taller middle (stacked `stone_dark` and dark windows, one or two `window_lit`), `jack_o_lantern`s on the steps, a `fence_iron` with the gate open, `dead_tree`s and `gravestone`s, `bats` against the moon. See `examples/haunted_house.py`.

## Cities

### City streets

Build each block of buildings one cell back from where its fronts should stand and give its cells a `facade` (`{"style": ["brick", "sooty"], "storeys": [3, 6], "lit": 0.5, "shops": 0.4}`): the fronts become separate buildings of different heights and brick, with windows set back in the walls, glass, curtains and lit or dark rooms behind. Then pavement, then a road sunk a kerb's height (`drop` 0.05) between, `street_lamp` prefabs, `wet` ground and rain. Show the depth from the pavement, looking along the buildings. Any sprite with `"glass": true` is glass: it shows what is behind it, tinted light blue and softly blurred; `glass_pane` is a plain pane. For a cyberpunk street use `"style": "neon"` (signs on the walls, blade signs over the street, shutters, tinted rooms) with `wires_span` across overhead, a `holo_ad`, a `noodle_stall`, `vending_machine`s, `steam` from the drains and coloured lights under the signs so their colour lands on the wet street; a `bloom` with `"source": "light"` makes the neon glow. For a night market fill a lane with stalls a unit out from the fronts (the facades' street line is `depth` 1 from the blocks: anything nearer the wall is behind it): `food_cart`s with `steam` and a `stools_table`, `fruit_stall`s, `gadget_stall`s, a `red_lantern` and a warm light at each, `lantern_span`s across overhead every five units with a red light under each, `power_pole`s, `scooter`s, a `neon_sign` at a side alley, `crowd`s down the far end and people under a lit `umbrella` (with a small cyan light at the shaft). For a village use `"style": "timber"` with `storeys` [1, 2] and `widths` [2, 3] over a block one storey high: timber-framed houses in limewash and ochre, each with a roof - a gable end or thatch or tiles, chimneys - on a `cobble` street, with a `market_stall`, an `inn_sign` standing out as a card, a `cart`, `barrel`s and `flowers`, and a `well` on a green. For a frontier town use `"style": "western"` with `storeys` [1, 2]: false fronts with painted signs (a saloon with batwing doors among them), clapboard, and the posts of a covered boardwalk a cell out - make that cell a `planks` step 0.15 high with a `ceil` and set `ceiling_height` 1.3, so the walk has its porch roof; end each block with a plain wall so the fronts only face the street. Dust (`desert_wash`), `tumbleweed`s, a `water_trough`, a `windpump` where the street runs out into the desert, the `cowboy`. See `examples/rain_alley.py`, `neon_street.py`, `night_market.py`, `village_green.py` and `ghost_town.py`.

### Facades

Stacked wall textures per storey with `window_lit` / `window_dark` mixed per cell and storey; tall background buildings (h 6-9) give scale and skyline.

### On a rooftop

Stand the camera on a tall block (a block `h` 5 with `height` 5.5-6, roof props at `z` 5) at the very edge, looking down a street of `neon` facades between blocks taller than the fronts; `lantern_span`s and `wires_span`s across it a few units down, a `holo_ad` over it, a `sky_train` card crossing it, towers of window walls behind. On the roof: a `water_tower`, `ac_unit`s, a `rooftop_sign`, the `runner` and a `black_cat` on the ledge; a lamp set up there (`z` a little over the roof) lights the roof round it as a lamp lights a street. From the street, look up at the train. See `examples/neon_rooftop.py`.

### A neon bar

Keep a room small - a unit is nearly three metres, so a bar is about 6 by 5 cells under a `ceiling_height` of 1.3. `bar_shelves` on the wall behind the bar, a `bar_counter` card along it (0.35 tall: a bartender shows from the chest up), `bar_stool`s, `bottles` on top, `arcade_cabinet`s down one wall with a coloured light at each, `booth`s with a character just behind the table (it reads as seated), a `jukebox`, `neon_cocktail`/`neon_fish` on the walls, `obsidian` underfoot to mirror it all, and a thick glowing fog (density 0.06, `glow` 1.2) for the smoke. A reef tank in the back wall as in the aquarium. See `examples/neon_bar.py`.

### A capsule hotel

A corridor one cell wide under a `ceiling_height` of 1, its walls `capsules` and `capsules_lit` alternated cell by cell (two rows of berths to a unit), cool strip lights every few cells, a white floor with `reflect`, a `vending_machine` at the end and someone padding down it. See `examples/capsule_hotel.py`.

### A clockwork city

Blocks of `brick_dark` with a `brass_plate` top storey, runs of `copper_pipes` venting `steam`, a tower with a `great_clock` card on its face (and a `cone` wireframe for a brass spire), `brass_gear` cards against the walls (`angle` square to the wall, mixed sizes, some `flip`ped), `lamp_post`s with warm lights, the `robot` tinted brass for an automaton. An orrery is wireframes: thin brass `torus` rings (`thickness` about 0.016) at different `tilt`s round a `sphere`. `sunset` sky, brown fog, ambient about 0.28, a low warm sun, a gentle light bloom (1.2). See `examples/clockwork_city.py`.

## Sci-fi and other worlds

### Industrial and sci-fi

`panel`, `panel_green`, `pipes`, `rust` walls over a `grate` or `tile_floor` floor, with `console` (emissive screen), `locker`, barrels and crates; pair with the `terminal` GUI theme and `crt_green`.

### Space and sci-fi

Corridors of `hull_lit` (or `hull_red` for emergency power) draw lines of light to the vanishing point; `tech_panel`, `server` and `blast_door` walls, `deck` or `grid_floor` underfoot. For a view of space, build a `viewport` wall (stack two for a glass wall) with `"floor": "void"` cells outside under `"sky": "space"`, and hang a `ringed` planet in `sky_objects`: stars surround you above and below the horizon, and an `obsidian` floor mirrors the planet. Props: `stasis_pod`, `hologram`, `drone`, `sci_crate`, `console`; cast: `astronaut`, `android`. Infested ships: `organic` walls, floors and ceilings, `alien_egg`, the `derelict` scatter set. Hangars and engine rooms: `hangar_floor` decks with a `pad_marking` decal under a `shuttle`, `conduit` and `screen_wall` (glowing monitors) walls, stacked `cargo_container`s, a `power_loader`, a `robot_arm`, `cables_hang` near the ceiling, a `reactor_core` (pair it with a cyan light) and amber `beacon`s with lights of their own; glaze a wall onto space with `glass_pane` cards between steel mullions. See `examples/orbital_hangar.py`, `space_station.py` and `derelict_ship.py`.

### On the Moon

A plain of `regolith` ringed by a crater rim of `rock` at several heights, the `space` sky with an `earth` in `sky_objects`, a low, hard, white `sun` (no fog at all - there is no air) and a very low ambient, so the shadows run long and black; greenhouse `dome`s glowing at different scales, `hab_module`s, a row of `solar_array`s, a `rover` with `rover_tracks` decals behind it, the `lander` on a `pad_marking`, `astronaut`s. For the lunar night drop the sun for a dim `moon`-type light from the Earth's direction and let the domes' windows light the base. See `examples/moon_base.py`.

### Alien worlds

The `alien` sky with a huge `ringed` planet and a moon or two in `sky_objects`, a `sun` light to match their lit side, `alien_ground` with outcrops of `alien_rock` (glowing veins), a pool of tinted water, `alien_plant`, `crystal`, a `monolith` on a raised plateau, and the `alien` scatter set; a `lander` and an `astronaut` for the visitors, the `alien` for the locals. See `examples/alien_world.py`.

### An aquarium

A dark hall (`marble_dark` with `reflect` 0.4, silhouettes tinted dark) in front of a tank of `seabed` under a `water_surface` roof (tinted down), its walls painted as open water (`["deep_water", "open_water"]`, two high) with rockwork along their foot - a `rock_wall` of `"rock": "reef"` down each wall, `depth` 1.4-1.8 and `height` about `[0.5, 1.45]` so the water shows over it, and `boulder`s with `plants` out on the sand - its window one long `glass_pane` floor to ceiling with `"glass": {"tint": [0.62, 0.88, 1.0], "blur": 0, "fog": true}` so the fog carries on into the water; light the tank with white lamps near its roof and let a blue fog (`[0.02, 0.1, 0.17]`, density 0.03, `glow` 0.5) do the rest; for sunbeams, mark a few roof cells `"glazed": true` (the ceiling stays, the sun shines through) and add a sun behind the tank with `shafts` 5. `whale_shark`, `manta_ray`, `reef_shark`, `sea_turtle`, shoals; `reef_rock`s and corals on the floor near the glass. Smaller tanks look through `tank_window` frames: `sea_nettle`s lit white against a `jelly_backdrop`, a reef of `anemone`, `brain_coral`, `staghorn_coral`, `sea_fan`, `angelfish`, `blue_tang`. A tunnel: glass down both sides and `tunnel_roof` overhead. See `examples/aquarium.py`.

## Wild places

### Dreams and the surreal

Fill the map with void and draw islands on it under the `dream` sky. They float over a sea of cloud, each with a ragged cliff underneath (`side` sets its texture). Then add a `sky_wall` with a door in it, a staircase to nowhere (`heights` with `height_unit` 0.3), a mirror lake (`obsidian` with `reflect` 0.9), and things adrift at a set `z`: `orb`, `koi`, `sky_whale`, `pocket_watch`, `floating_rock`, `balloon`. An `eye` in `sky_objects` watches. The `dream` post preset blows out bright pastel scenes, so use a gentle `bloom` instead. For impossible architecture: a plain of `checker_marble` (it mirrors), a marble chess set scaled up into a giant game (`chess_pawn` to `chess_king`, tinted dark for one side), a `clock` in `sky_objects` with `melt`, a `melting_clock` over a plinth, `stone_arch`es and `stair_float`s hung in the air, a stair out of the floor to a lone `door_frame`, a hole of void cells in the floor (give its rim a `sky_wall` side), `paper_boat`s on the polish. A drowned library: `bookshelf` walls three storeys high between `tall_window`s, a floor of `water` with `drop` and a high `reflect`, an island of books, and the air full of `jellyfish`, `sky_lantern`s, `book_fly`s, koi and a `sky_whale`; open a few cells of the roof as skylights and the sun comes down through them in beams in a dark, dense fog. An endless hall of doors: walls of `door_hall` at every storey (tinted per cell for doors of every colour) with `door_hall` as the ceiling too, a few `sky_wall` cells where a door has opened onto the sky, a `checker_marble` floor, a `stair_float` rising to a `door_frame` in the air, and the `dreamer` walking away down it. See `examples/dream_world.py`, `dream_chess.py`, `drowned_library.py` and `hall_of_doors.py`.

### Sky islands

A map of `void` with islands drawn on it (`"floor": "meadow", "side": "island_rock"` and a `cliff` of 2-3); hang an `island_keel` under each (`scale` about 1.6 x its radius, `z` = -(cliff + scale)) so it floats as a mountain, `island_roots` cards round the edges, a `waterfall` card off an edge (from a stream of `shallows` on top) with `z` at minus its `scale`. Raise one island on a block of `island_rock` with a `meadow` `top`; join two with a bridge of `planks` cells with `cliff` 0.12 and `rope_rail` cards along both sides. A `day` or `golden` sky, a light haze, `floating_rock`s, `seagull`s, trees, a ring of `column`s for a temple. See `examples/sky_islands.py`.

### A mirror salt flat

A big open map of `salt_water` with `reflect` 0.9 and `"reflections": {"ripple": 0, "smear": 0}` (a still mirror), islands of dry `salt_flat` with `reflect` 0, rows of `salt_mound`s (vary each `scale` a little) with a `salt_heap` or `salt_pile` among them and `salt_clods` about, a little house of `salt_brick`; a `sunset`, `day`, `night` or `dream` sky with a low sun and `"skyline": "mountains"`, all doubled; a low camera (`height` 0.3) and one figure close enough to read with their reflection. Surreal touches stand well on it: a `door_frame`, an `armchair`, a `grandfather_clock`, a `sky_whale`. See `examples/salt_flat.py`.

### An aurora ice palace

`"sky": "aurora"` (rayed curtains of green light, no two stretches alike, a teal ribbon and red-tipped rays among them, brightest due north - aim north to have them over the scene); walls and towers of `ice_block` with an `ice_spire` on each tower top (`z` = the tower's height), `icicles` cards along the wall tops, an open hall of `frost_wall` round an `ice_throne`, `ice_shards` in the snow, `snowy_pine`s; a frozen lake of `ice_floor` with `reflect` 0.85 and `"reflections": {"ripple": 0, "smear": 0}` doubles the aurora. Light the snow green with a `moon` that has `"disc": false` and `color` [0.45, 1, 0.75]; ambient about 0.15; a gentle light bloom (1.3). See `examples/aurora_palace.py`.

### A glowing jungle (bioluminescent, at night)

Walls of `glow_leaves` with `"fringe": "glow_jungle"` round a clearing of `lumen_floor`, a pool of `glow_water` sunk with `drop` 0.1; `glow_monstera`, `glow_fern`, `glow_tree_fern`, `glow_heliconia`, `glow_bromeliad`, `glow_liana`, `glow_pods` and `glowshroom`s in clusters, big trees tinted dark; a few low coloured lights (cyan, violet, pink, intensity 0.6-0.9) among the plants and a brighter one on anything that should be seen (a stone head); `night` sky, a thin ground mist with `glow`, a handful of `spores` and `fireflies` (6 or so - more turn to snow), and a light bloom (strength 1.8). Stand at the water's edge: from further back a pool flattens into a line. See `examples/glow_jungle.py`.

### Vector World (the 80s computer world)

Black cells ruled in light - `vector_grid` (a wall of squares), `vector_windows`, `vector_bands`, `vector_data`, `vector_circuit`, `vector_frame` walls, each `{"base": ..., "tint": colour}` - over a `vector_floor` grid with `reflect` 0.4, under the `vector` sky with a sun of `"disc_style": "stripes"` (`disc_size` 8, `elevation` 9) and a fog the colour of its horizon (`[0.2, 0.05, 0.26]`). Put the shapes in `wireframes`: `terrain` mountains scaled wide and low beyond the map, `pyramid`s and polyhedra (`solid` for black faces edged in light), a `racer` with two `glint`s at its nose and a `light_trail` behind, `palm`s, a `gate` across the avenue, a `tower` with a `glint` on top for a beacon. People are `vector_runner`s (`tint` sets their light), and `light_beam`s ring a plaza. Light it with a strong light bloom; add `streaks` (anamorphic, `points` 2) for headlights and a `flare` (`"source": "light"`) for a beacon. See `examples/vector_world.py`.

### Doomed mode (a 1993 shooter)

`"ui": {"theme": "doomed"}`; in the shot's overlays a `statusbar` (`ammo`, `health` - the face bloodies below 80 - `armor`, `arms`, `keys`, `ammo_table`, `face`: `grin`/`ouch`), a `message` ("Picked up a clip.") and a `pistol` or `shotgun` viewmodel (`"fire": true`); aim with a 2-point `look_at` and `"pitch": -0.08`, `"light_levels": 16`, a near-black `fog`. The base: `nukage` sunk with `drop` and `"side": "slime_edge"`, `hex_floor` ledges and walkways, `green_trim` walls stacked storey on storey under a `tech_ceiling`, a `green_window`, `toxic_barrel`s, soldiers tinted sick green, a `corpse`, pickups, a `fireball`, `toxic_sign` decals. See `examples/doomed.py`.

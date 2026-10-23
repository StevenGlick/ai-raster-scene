# Asset inventory

Every texture, prop, character, decal, sky, icon and look the renderer ships with: how good each one is today, what is wrong with it, and which example scenes use it. It is the working list for improvement passes. Take a group, fix what its notes name, re-render the examples in its "used in" column, then move the status on and say what changed in the pass log at the bottom.

- **good**: holds up both in a scene and close up. Leave it unless a pass has a reason.
- **polish**: works, but has the flaw its notes name.
- **rework**: redraw it from scratch.
- **new**: added since the last review.

The prose, groups, statuses and notes here are written by hand. The rows themselves, the computed columns ("traits", "used in", "contents", "shots", "gallery") and the counts belong to `docs/asset_review.py`, so this file cannot fall behind the code:

```bash
python docs/asset_review.py sync      # add new assets (as new), drop removed ones, refresh the computed columns
python docs/asset_review.py sheets    # review sheets for every section into renders/sheets
```

The smoke test fails while this file is out of date. Sheets show textures tiled 2x2 so seams show, props on a ground line, characters front and back, and mark each tile with its status. `sheets textures props` or `sheets foliage tree` narrow them, `--status polish,rework` keeps what still needs work, and `--out renders/sheets/before` saves a set to compare against after a pass.

## Summary

<!-- summary -->
| | count | good | polish | rework | new |
|---|---|---|---|---|---|
| Textures | 282 | 282 | 0 | 0 | 0 |
| Props | 456 | 456 | 0 | 0 | 0 |
| Characters | 33 | 33 | 0 | 0 | 0 |
| Decals | 42 | 42 | 0 | 0 | 0 |
| Skies | 14 | 14 | 0 | 0 | 0 |
| Skylines | 6 | 6 | 0 | 0 | 0 |
| Sky objects | 7 | 7 | 0 | 0 | 0 |
| Scatter sets | 22 | 22 | 0 | 0 | 0 |
| Fringe sets | 7 | 7 | 0 | 0 | 0 |
| Facade styles | 6 | 6 | 0 | 0 | 0 |
| Prefabs | 13 | 13 | 0 | 0 | 0 |
| Objects | 43 | 43 | 0 | 0 | 0 |
| Held items | 8 | 8 | 0 | 0 | 0 |
| Icons | 26 | 26 | 0 | 0 | 0 |
| GUI themes | 6 | 6 | 0 | 0 | 0 |
| GUI widgets | 18 | 18 | 0 | 0 | 0 |
| Post presets | 20 | 20 | 0 | 0 | 0 |
| Palettes | 9 | 9 | 0 | 0 | 0 |
| Example scenes | 152 | 152 | 0 | 0 | 0 |
| **all** | **1170** | **1170** | **0** | **0** | **0** |
<!-- /summary -->

## Pass plan

Passes 1-5 - nature, stone and ruins, water and ice, interiors, the small things - are done (see the pass log). What is left is the second look: every scene, shot by shot, from a catalog of current renders (2026-10-21, all 60 example scenes), with the new techniques - objects, solid rock, crystals, layered facades and fringes - in hand.

### The user's list (2026-10-21)

From going through the catalog. One scene at a time, each done properly; no rush.

- [x] **coast_lighthouse** - the billboard boulders swapped for 3D ones. Done: the scatter's larger billboard boulders became 3D ones where they lay (a third bigger, as a 3D rock carries less bulk than a billboard of its height), with more at the water's edge, the foot of the cliffs and before every shot; the scatter keeps only small rocks. At dusk they take the scene's light, so the waterline reads darker than the old mossy domes did.
- [x] **misty_moor** - the billboard boulders swapped for 3D ones, and a boulder or two more in the foreground of the shots. Done: mossy boulders framing each shot and out on the moor, and the scatter's larger ones swapped where they lay.
- [x] **tropical_beach** - posts under the pier; the tree line given layers if it has none. Done: wooden piles (`column` objects of `wood`) down both edges of the pier, taller at its end; the jungle given a `jungle` fringe.
- [x] **neon_bar** - the reef tank in the back wall done like the aquarium at a small scale: open water behind, a little live rock, perhaps one small boulder at the back. Keep the density; adding too much would throw off the balance. Done: the tank's back wall painted as open water (dimmed to the bar's mood), a low reef `rock_wall` along its foot and one small boulder; the `reef_rock`s and corals kept in front, near the glass.
- [x] **red_canyon** - the canyon walls themselves updated (the fallen rock along their foot is done). Done: every face of the canyon lined with a tall `rock_wall` of a new `canyon` rock - beds of red and pale stone by height, desert varnish streaking down - rising 6-7.4 over the old walls (cut down to 5.2 as cores), so the cliffs jut and step and the rim is ragged against the sky.
- [x] **ghost_town** - the buildings that have no depth fixed, drawn with the layered facade technique of the city; the horse trough in 3D; shot 2: the empty space under the frame in front of the building filled - planks overhead for shade, or a deck; shot 4: the mountain walls updated, as for the canyon. Done: every western building now has its body behind the false front - a gabled roof of boards running back from the street on walls up from the block - and its porch a roof of boards sloping down from the front to the fascia, so it shows from the street over the posts and gives shade (the walk's ceiling lowered to 1.15 so it does); troughs of boards with water in them (`trough`, new); the mesas lined with `canyon` rock in 3D, a ragged skyline of cliffs in beds.
- [x] **village_green** - the market cart rebuilt in 3D, as the noodle stand was; the houses need roofs with depth (they read as if roofless); the buildings drawn with the layered facade technique. Done: every house's roof built in 3D by the facade code - behind a gable end a gabled roof running back from the street, its slopes on the gable's edges; over an eaves house a roof along the street, its eaves out over the front, a brick chimney through some ridges - thatch (`_thatch`) or clay tiles (`_tiles`), on plastered walls of the house's colour up from the block, behind every facade layer; the market stall a `market_stand` object (a trestle table with a striped skirt under a striped awning, `goods_*` heaped on it).
- [x] **cathedral_ruin** - the pillars modelled in 3D (octagonal) instead of billboards, and moved inward to where they would carry the roof. Done: two arcades of octagonal piers of `ashlar` (dressed stone in drums, plinths and capitals) 3.2 in from each wall between the windows, carrying timber wall plates (`beam`) under the roof; the pier under the fallen roof broken off ragged, its plate down on the floor; the pews between the arcades, behind the cameras.
- [x] **ancient_ruins** - the pillars remodelled in 3D, as for the cathedral; perhaps the fallen statue's head in 3D too (not a priority). A scene to give more love. Done: the peristyle and the sacred way's columns are fluted Doric columns of `marble` in 3D (`flutes`, `doric`), laid in drums, architraves and cornices (`beam`) across the runs that stand, the rest snapped off (`broken`) or fallen; the `ruined_columns` prefab in 3D; `fill` so the backlit columns are not black; a new shot, `ruins_columns`. The statue's head is still a billboard.
- [x] **bayou** - the trees redone with the jungle's layered fringe, its layers spread further apart, so the trees look properly 3D. Done: the swamp fringe in four layers (a new middle stand; no more moss curtains hanging in the air on their own bough, which read as signboards over the trees) spread three cells out from the wall along a natural, wandering line (`wander`, new) - the heron's shot now looks into a misty forest of trunks at every depth, and the canopy behind the shack is whole.
- [x] **jungle_temple** - the tree line broken up as the aquarium's rock wall was: a natural, polygonal edge instead of the hard grid angles. A scene to give more love. Done: the jungle's fringe `wander`s (1.4 deep), so the trees stand along a natural, polygonal line round the clearing and down the path; the canopy is one height within two cells of open ground, so no steps of it show between the trees - the view from the pyramid top is a forest edge, not clipped hedges.

New scenes:

- [x] A saloon interior, in the frontier town. Done: `saloon` - a long mahogany bar (`saloon_bar`), the back bar's bottles and mirror, a piano, card tables, a tin ceiling, the noon sun through the front windows into dusty air.
- [x] Inside a mine, in the same wild west. Done: `gold_mine` - a tunnel timbered in 3D, `rails` and an `ore_cart`, lanterns, a prospector at a vein of gold, the portal in the hillside.
- [x] Inside the jungle temple. Done: `temple_inside` - a passage of carved stone to the idol of the jaguar in a shaft of light, an explorer reaching for it, treasure.

## Textures (282)

64x64 tiles, drawn in code. "glows" means the texture lights itself (windows, screens, runes), "see-through" that the map shows through its holes, "mirror" that floors made of it reflect.

### Masonry and plaster

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `brick` | good |  | canal_boat, rainy_street |  |
| `brick_dark` | good |  | clockwork_city, neon_bar, neon_rooftop, neon_street, night_market, rain_alley |  |
| `brick_yellow` | good |  | - |  |
| `stone` | good |  | claude_study, garden_encounter, gui_menus, hospital_garden, post_presets, viaduct_train | Even block sizes; a few varied heights would help on long walls. |
| `stone_dark` | good |  | cathedral_ruin, garden_encounter, gui_menus, gui_themes, gui_trade, haunted_house, hospital_garden, library_medium, mansion_library, post_presets, rainy_street, underworld_river, window_garden |  |
| `stone_pale` | good |  | cathedral_ruin, chapel_graveyard, dream_world, garden_encounter, glass_chapel, gui_menus, hospital_garden, post_presets |  |
| `castle` | good |  | canal_tunnel, castle_keep | Mortar grid is very regular; chip a few corners. |
| `moss_stone` | good |  | autumn_lane, coast_lighthouse |  |
| `menhir` | good |  | - | Drawn with the toolkit in basics.py: one weathered stone face - broad swells, rain runnels, long cracks, lichen rosettes - moss at its foot. |
| `menhir_top` | good |  | - | Drawn with the toolkit in basics.py: the upper courses of a standing stone: greyer, more lichen, no moss. |
| `slime_brick` | good |  | sewer_tunnels |  |
| `plaster` | good |  | rainy_street, village_green, village_hours, window_garden | Redrawn with the toolkit in basics.py: smooth render mottled where patched, a hairline crack, faint streaks; no band, so it stacks storey on storey. |
| `plaster_white` | good |  | autumn_garden, garden_encounter, gui_menus, hospital_garden, post_presets | Redrawn with the toolkit in basics.py: the same render in white. |
| `hospital_wall` | good |  | ghost_corridor, gui_hud, hospital_corridor |  |
| `ivy` | good |  | rainy_street | Redrawn with the toolkit in basics.py: red brick with woody stems climbing and branching and clusters of dark leaves, the newest brighter. |
| `concrete` | good |  | 23 scenes |  |
| `marble` | good |  | cathedral_ruin, chapel_graveyard, dream_chess, dream_world, glass_chapel, gui_themes, gui_trade, library_medium, mansion_library, sky_road |  |
| `marble_dark` | good |  | aquarium | Redrawn with the toolkit in basics.py: dark slabs with long, thin, continuous veins of white and grey drifting across them. |
| `rock` | good |  | basalt_coast, castle_keep, coast_lighthouse, crystal_cave, doomed, fjord, forest_path, garden_encounter, gui_lantern, gui_menus, hospital_garden, moon_base, post_presets, tunnel_encounter, underground_waterway, underworld_river | Redrawn with the toolkit in basics.py: masses of every size, each a facet tilted to the light, split by crevices that wander, widen and close; finer cracks, grain. |
| `rock_wet` | good |  | crystal_cave, gui_lantern, kelp_forest, sunken_temple, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: the same rock darker and blue-grey, with glints of water where the faces catch the light. |
| `snow_rock` | good |  | - | Redrawn with the toolkit in basics.py: faceted rock with snow lying on the top of every mass, thick on the flats, and drifted in the crevices. |
| `sky_wall` | good |  | dream_chess, dream_world, hall_of_doors |  |

### Wood

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `wood_panel` | good |  | drowned_library, ghost_train, glass_chapel, haunted_house, mansion_library | Redrawn with the toolkit in basics.py: stiles and rails framing two raised panels per unit, all one dark wood, the bevels catching the light, figure streaked along the grain. |
| `planks` | good |  | bayou, ghost_town, ghost_train, high_noon, log_flume, roller_coaster, rope_bridge, sky_islands, winter_woods |  |
| `boards` | good |  | autumn_garden, bayou, coast_lighthouse, ghost_town, gold_mine, rain_alley, tropical_beach, window_garden |  |
| `logs` | good |  | coast_lighthouse, fjord, winter_lake |  |
| `door_wood` | good |  | autumn_garden, bayou, dream_chess, dream_world, fjord, haunted_house, salt_flat, winter_lake |  |
| `bookshelf` | good |  | claude_study, drowned_library, gui_themes, gui_trade, library_medium, mansion_library |  |
| `bark` | good |  | - | Redrawn with the toolkit in forest.py: long wavy ridges split by deep dark furrows; tiles without a seam. |
| `bark_pine` | good |  | - | Redrawn with the toolkit in forest.py: a mosaic of tall plates (nearest-seed cells) with dark fissures and flaking. |
| `wood_floor` | good |  | claude_study, drowned_library, gui_lantern, gui_themes, gui_trade, haunted_house, library_medium, mansion_library, saloon, tunnel_encounter, underground_waterway, window_garden |  |
| `shingle` | good |  | bayou, chapel_graveyard, coast_lighthouse, rainy_street, storm_island, winter_lake | Redrawn with the toolkit in basics.py: courses of staggered slates, each tipped up to its foot so it throws a shadow on the course below, chipped corners, moss in the joints. |

### Metal and sci-fi

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `iron_door` | good |  | bunker_lab, garden_encounter, ghost_corridor, gui_hud, gui_lantern, gui_menus, hospital_corridor, hospital_garden, post_presets, rainy_street, tunnel_encounter, underground_waterway |  |
| `corrugated` | good |  | grand_prix, rainy_street | Redrawn with the toolkit in basics.py: galvanised sheets in rounded ribs lapped at the seam, nail rows, rust in patches and streaks from the nails. |
| `rust` | good |  | bunker_lab, rainy_street |  |
| `pipes` | good |  | bunker_lab, sewer_tunnels |  |
| `panel` | good |  | bunker_lab, capsule_hotel, derelict_ship, orbital_hangar, space_station |  |
| `panel_green` | good |  | bunker_lab |  |
| `hull` | good |  | orbital_hangar, space_station, space_trench |  |
| `hull_dark` | good |  | derelict_ship, orbital_hangar, space_station, space_trench |  |
| `hull_lit` | good | glows | space_station, space_trench |  |
| `hull_red` | good | glows | derelict_ship, space_trench |  |
| `tech_panel` | good | glows | space_station, space_trench |  |
| `server` | good | glows | space_station |  |
| `blast_door` | good | glows | derelict_ship, space_station |  |
| `hazard` | good |  | - |  |
| `deck` | good |  | derelict_ship, orbital_hangar, space_station |  |
| `grate` | good |  | bunker_lab, derelict_ship, orbital_hangar |  |
| `grid_floor` | good | glows, mirror 0.3 | - |  |
| `hex_panel` | good |  | alien_world |  |
| `hex_floor` | good |  | doomed | Drawn in doomed.py: brown hexagonal tiles, each its own shade, worn at the edges, dark grout. |
| `green_tech` | good |  | - | Drawn in doomed.py: green plating in vertical strakes of different shades, panel seams, grime running down. |
| `green_trim` | good |  | doomed | Drawn in doomed.py: the green plating under a band of brown metal with a row of pale teeth; stack it storey on storey. |
| `tech_ceiling` | good |  | doomed | Drawn in doomed.py: grey-brown ceiling tiles in a grid, each a shade of its own. |
| `slime_edge` | good |  | doomed | Drawn in doomed.py: brown metal plates stained green toward the bottom: the side of a slime pit. |
| `vector_grid` | good | glows | synthwave_drive, vector_world | Drawn in vector.py: black ruled in lines of white light, two squares to a unit each way; a tint colours it. |
| `vector_floor` | good | glows | vector_world | Drawn in vector.py: a line of light at every unit, running away to the horizon; reflects well. |
| `vector_frame` | good | glows | vector_world | Drawn in vector.py: a line of light round the edge of each cell, so a block reads as a box of light. |
| `vector_circuit` | good | glows | vector_world | Drawn in vector.py: traces of light at right angles ending in pads and rings. |
| `vector_windows` | good | glows | vector_world | Drawn in vector.py: a tower face of window outlines, four by four to a unit, a few of them lit. |
| `vector_bands` | good | glows | vector_world | Drawn in vector.py: a bold band of light at each storey and thin ones between. |
| `vector_data` | good | glows | vector_world | Drawn in vector.py: dashes of light streaming down in columns, brighter at their heads. |
| `salt_flat` | good |  | salt_flat | Drawn in saltflat.py: the dry crust of a salt flat: pale plates, each its own shade, edged by raised white rims. |
| `salt_water` | good |  | salt_flat | Drawn in saltflat.py: the crust under a film of still water: darker, the plates faint; give it reflect 0.9. |
| `salt_brick` | good |  | salt_flat | Drawn in saltflat.py: blocks cut from the salt crust laid in courses: rough cream faces, deep joints. |
| `meadow` | good |  | sky_islands | Drawn in skyisles.py: grass in tufts with tiny white, yellow and pink flowers, for an island's top. |
| `island_rock` | good |  | sky_islands | Drawn in skyisles.py: rock in bands of grey and brown with roots working through it, for an island's side. |
| `glow_leaves` | good | glows | glow_jungle | Drawn in glowjungle.py: the jungle wall at night: dark blue-green leaves, ribs and tips glowing. |
| `lumen_floor` | good | glows | crystal_cave, enchanted_path, glow_jungle | Drawn in glowjungle.py: dark leaf litter with glowing moss and fungus specks. |
| `glow_water` | good | glows, mirror 0.55 | crystal_cave, glow_jungle | Drawn in glowjungle.py: black water with plankton glowing in swirling streams; reflects. |
| `ice_block` | good |  | aurora_palace, ice_cave | Drawn in icepalace.py: big blocks of blue ice, frosted faces paler at their edges, deep joints, cracks. |
| `frost_wall` | good |  | aurora_palace, ice_cave | Drawn in icepalace.py: ice grown over with feathery frost. |
| `ice_floor` | good | mirror 0.6 | aurora_palace, ice_cave, ice_road | Drawn in icepalace.py: polished ice over dark water, cracked white; reflects. |
| `brass_plate` | good |  | clockwork_city | Drawn in clockwork.py: riveted brass panels, darker in their middles, worn bright at their edges. |
| `copper_pipes` | good |  | clockwork_city | Drawn in clockwork.py: a wall run with copper pipes, a valve wheel, green where they weep. |
| `clock_face` | good |  | clockwork_city | Drawn in clockwork.py: a clock dial on a dark ground, one to a cell. |
| `hangar_floor` | good |  | orbital_hangar, space_trench | Drawn with the toolkit in scifi.py: heavy plates four to a unit, corner bolts, tread, a tie-down ring at each crossing, wear and oil. |
| `conduit` | good | glows | orbital_hangar, space_trench | Drawn with the toolkit in scifi.py: cable bundles in four colours and pipes up the wall, steel clamps, a junction box with lit LEDs. |
| `screen_wall` | good | glows | orbital_hangar | Drawn with the toolkit in scifi.py: monitors four to a unit, each with a trace, readouts, a radar or a wireframe, in cyan, green or amber; glows. |
| `tunnel_roof` | good | glows | aquarium, sea_tunnel | Drawn with the toolkit in aquarium.py: deep blue water with the rippled surface far above and its net of light; a dark acrylic seam at every tile; glows. |
| `jelly_backdrop` | good | glows | aquarium | Drawn with the toolkit in aquarium.py: an even glowing deep blue, faintly mottled, so jellies stand out in front of it. |
| `open_water` | good | glows | aquarium, neon_bar | Drawn in aquarium.py: the open water painted on the back of a big tank, paler toward the surface, soft shafts in it; the upper storey over `deep_water`, so the rockwork's tops read against it. Dithered for distance: up close its steps show. |
| `deep_water` | good | glows | aquarium, fjord, neon_bar | The lower storey of `open_water`, deepening toward the floor. |
| `bar_shelves` | good | glows | neon_bar | Drawn with the toolkit in bar.py: two glass shelves of bottles in a dark mirrored recess, each bottle lit from below by a magenta strip; glows. |
| `capsules` | good | glows | capsule_hotel | Drawn in bar.py: four berths to a unit in white moulded plastic, each with a glowing number plate; lamp-lit bedding, a drawn blind, a screen or dark inside; glows. |
| `capsules_lit` | good | glows | capsule_hotel | The same berths with more of them occupied and lit; alternate it with `capsules` so the pattern does not march. |
| `nukage` | good | glows | doomed | Drawn in doomed.py: bright green sludge in slow swirls with paler veins and darker clots; glows - sink it with `drop`. |

### Nature

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `foliage` | good |  | window_garden | Redrawn with the toolkit in forest.py: small leaves at three depths over a dark tangle of twigs. The wall behind a `forest` fringe. |
| `foliage_autumn` | good |  | - | The same leaves in orange, gold and red over dark brown. |
| `forest_deep` | good |  | haunted_house, woodland_night | Trunks at four depths in the dark, the farthest thinnest and darkest, boughs and a few leaves catching light; sways repeat with the tile. The wall behind a `forest` fringe: gaps between the cards read as more wood. |
| `forest_deep_autumn` | good |  | autumn_garden, autumn_lane | Drawn with the toolkit in forest.py: forest_deep with the leaves hanging in the dark turned a deep rust. |
| `forest_deep_snow` | good |  | winter_woods | Drawn with the toolkit in forest.py: forest_deep with snow lying on the boughs between the dark trunks. |
| `swamp_deep` | good |  | bayou | Drawn with the toolkit in swamp.py: grey trunks at four depths in the murk with curtains of Spanish moss between them. |
| `hedge` | good |  | autumn_lane_road, garden_encounter, gui_menus, hospital_garden, post_presets | Redrawn with the toolkit in basics.py: small leaves packed in three depths, the face kept flat by the shears, thin patches darker. |
| `grass` | good |  | 30 scenes | Redrawn with the toolkit in basics.py: blades stroked in clumps, dark at the roots and bright at the tips, yellow-green tufts, a daisy or two. |
| `moss` | good |  | autumn_lane, enchanted_path, forest_path, redwood_road | Redrawn with the toolkit in forest.py: crowded cushions with fine bobbles, a stone showing here and there. |
| `mud` | good |  | candy_road, jungle_river, jungle_trail, lantern_river, woodland_night |  |
| `bog` | good |  | bayou, bayou_run | Drawn with the toolkit in swamp.py: black peat with cushions of sphagnum in green and rust, standing puddles. |
| `dirt` | good |  | autumn_lane, canyon_run, castle_keep, forest_path, haunted_house, hayride, night_fair, safari_drive, volcano_road | Redrawn with the toolkit in basics.py: soil broken into clods, pebbles, a root or two, darker damp patches. |
| `gravel` | good |  | 22 scenes | Redrawn with the toolkit in basics.py: rounded pebbles in three stone colours, each lit on top with a shadow under it. |
| `sand` | good |  | camel_caravan, coast_lighthouse, desert_highway, desert_motel | Redrawn with the toolkit in basics.py: wind ripples with a lit face and a shaded lee, wandering, a shell fragment or two, dark grains. |
| `snow` | good |  | aurora_palace, ice_road, pilgrim_path, ski_run, sled_run, sleigh_ride, winter_lake, winter_road, winter_woods | Redrawn with the toolkit in basics.py: drifts sculpted by the wind, their lee sides in blue shadow, faint ripples, glitter. |
| `ice` | good | mirror 0.38 | ice_cave, winter_lake, winter_woods | Redrawn with the toolkit in basics.py: clear blue with gentle depth, straight fractures with a branch each and a dark side, strings of bubbles, frost. |
| `water` | good | mirror 0.5 | 23 scenes | Redrawn with the toolkit in basics.py: a deep teal in slow swells and a broken net of light where the ripples gather it; kept dark, so reflections read. |
| `swamp_water` | good | mirror 0.42 | bayou, bayou_run | Drawn with the toolkit in swamp.py: black-brown water with a skin of duckweed drifting in patches and a few floating leaves; mirror 0.42. |
| `seabed` | good |  | aquarium, kelp_forest, kelp_run, neon_bar, sea_tunnel, sunken_temple | Drawn with the toolkit in sea.py: pale sand in gentle ripples, shell and pebble, and a broken net of caustic light over it. |
| `water_surface` | good | glows | aquarium, kelp_run, neon_bar | Drawn with the toolkit in sea.py: the surface from below, rippled and glowing with a net of brighter lines; for an underwater roof. |
| `reef_wall` | good |  | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: lumps of live rock, patches of pink coralline, coral heads, algae tufts and polyps, dark crevices. |
| `pine_needles` | good |  | forest_path, log_flume, redwood_road, woodland_night | Redrawn with the toolkit in forest.py: criss-crossed needle litter over dark soil, a few green needles, cones and twigs. |
| `leaves_fallen` | good |  | autumn_lane, autumn_lane_road | Drawn with the toolkit in forest.py: leaves lying flat over dark earth, each its own colour - orange, gold, rust, brown, a few green - grass where they lie thin. |
| `alien_ground` | good |  | alien_world | Redrawn with the toolkit in basics.py: violet dust drifting over teal grit, the edge broken grain by grain, crystal shards of pink, cyan and white. |
| `regolith` | good |  | moon_base, moon_drive, red_planet | Drawn with the toolkit in moon.py: grey dust with craters - a rim lit toward the sun, a dark bowl - and thrown-out rocks. |
| `alien_rock` | good | glows | alien_world | Redrawn with the toolkit in basics.py: dark violet masses, each a facet to the light, with a teal glow welling up in the crevices between them and spilling onto the faces (emissive). |
| `organic` | good |  | derelict_ship |  |
| `cloud_floor` | good |  | airship_voyage |  |

### Floors

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `checker` | good |  | dream_world |  |
| `checker_marble` | good | mirror 0.35 | dream_chess, hall_of_doors | Drawn with the toolkit in dream.py: black and white marble squares, veined, fine joints; mirror 0.35. |
| `door_hall` | good |  | hall_of_doors | Drawn with the toolkit in dream.py: a pale four-panelled door with a brass knob and number plate in a moulded frame on striped paper; tint it. |
| `linoleum` | good |  | ghost_corridor, gui_hud, hospital_corridor |  |
| `tile_floor` | good |  | bunker_lab, derelict_ship, neon_street |  |
| `tile_white` | good |  | capsule_hotel |  |
| `tile_green` | good |  | - |  |
| `cobble` | good |  | clockwork_city, enchanted_path, garden_encounter, gui_menus, hospital_garden, market_ride, night_canal, post_presets, rainy_street, storm_island, village_green, village_hours | Redrawn with the toolkit in basics.py: a Voronoi mosaic of 36 rounded stones a tile in grey and brown, dark grit and moss in the joints; the repeat no longer shows. |
| `asphalt` | good |  | 32 scenes |  |
| `carpet` | good |  | castle_keep, chapel_graveyard, claude_study, gui_themes, gui_trade, haunted_house, library_medium, mansion_library |  |
| `carpet_green` | good |  | - |  |
| `flagstone` | good |  | canal_tunnel, castle_keep, cathedral_ruin, chapel_graveyard, claude_study, glass_chapel, haunted_house, market_ride, neon_street, night_canal, night_market, rain_alley |  |
| `obsidian` | good | mirror 0.45 | dream_world, neon_bar, space_station |  |
| `concrete_floor` | good |  | 85 scenes |  |
| `rock_floor` | good |  | crystal_cave, doomed, gold_mine, gui_lantern, mine_ride, mountain_pass, night_pass, pilgrim_path, storm_coast, tunnel_encounter, underground_waterway, underworld_river | Redrawn with the toolkit in basics.py: flatter, smaller masses in brown with grit in the cracks. |

### Ceilings

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `acoustic` | good |  | ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: four bevelled tiles a unit in a grid of runners, pitted with fissures and pin-holes, a water stain. |
| `ceiling_plaster` | good |  | gui_themes, gui_trade, library_medium, window_garden | Redrawn with the toolkit in basics.py: the plaster render in a darker tone, with no band across it. |
| `beams` | good |  | castle_keep, cathedral_ruin, chapel_graveyard, claude_study, haunted_house | Redrawn with the toolkit in basics.py: two oak beams a unit, proud of the limewash: a lit edge, a side in shadow and a soft shadow on the plaster; grain and checks. |

### Fabric and interior

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `curtain` | good |  | gui_themes, gui_trade, library_medium, mansion_library | Redrawn with the toolkit in basics.py: velvet folds of every width, each a rounded column lit on its left, deep shadow between. |
| `curtain_black` | good |  | - | Redrawn with the toolkit in basics.py: the same folds in black velvet. |
| `wallpaper` | good |  | ghost_train, gui_themes, gui_trade, hall_of_doors, haunted_house, library_medium, mansion_library |  |
| `wallpaper_green` | good |  | ghost_train |  |

### Light sources

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `window_lit` | good | glows | garden_encounter, gui_menus, haunted_house, hospital_garden, neon_rooftop, post_presets, rainy_street | Simple; a silhouette in one pane now and then would add life. |
| `window_dark` | good |  | garden_encounter, gui_menus, gui_themes, gui_trade, haunted_house, hospital_garden, library_medium, mansion_library, neon_rooftop, post_presets, rainy_street |  |
| `window_lit_plaster` | good | glows | bayou, desert_motel, garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, window_garden, winter_lake |  |
| `window_dark_plaster` | good |  | garden_encounter, ghost_corridor, gui_hud, gui_menus, hospital_corridor, hospital_garden, post_presets, rainy_street, window_garden |  |
| `window_teal` | good | glows | garden_encounter, gui_menus, hospital_garden, post_presets, window_garden |  |
| `stained_glass` | good | glows | castle_keep, chapel_graveyard | The sun comes in through it coloured, as through the glass chapel's lancets. |
| `lancet_window` | good | glows | glass_chapel | New: a tall lancet with a pointed head in pale stone - a column of ruby in a border of cobalt and gold, a medallion at its middle and another in its head, leaded. The panes glow, and a sun standing in front of it comes in through them coloured: its pattern on the floor, coloured beams in the fog (render.sun_tint). |
| `rose_window` | good | glows | glass_chapel | New: a great round of stained glass in pale stone - twelve petals of ruby and cobalt round a gold heart, a ring of small panes outside them, stone tracery and lead between. It lets the sun in coloured too. |
| `runes` | good | glows | gui_lantern, gui_themes, gui_trade, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `fireplace` | good | glows | claude_study, haunted_house |  |
| `star_chart` | good | glows | claude_study |  |

### See-through

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `bars` | good | see-through | castle_keep |  |
| `fence_iron` | good | see-through | chapel_graveyard, haunted_house |  |
| `chainlink` | good | see-through | grand_prix |  |
| `railing` | good | see-through | claude_study, rope_bridge, sewer_tunnels |  |
| `picket` | good | see-through | - |  |
| `portcullis` | good | see-through | castle_keep |  |
| `window_broken` | good | see-through | cathedral_ruin |  |
| `tall_window` | good | see-through | drowned_library | Drawn with the toolkit in dream.py: two lancets in pale ashlar, leaded every quarter unit, open between the leads (see-through). |
| `tall_window_top` | good | see-through | drowned_library | Drawn with the toolkit in dream.py: the lancets closing in pointed arches under a small rose; see-through. |
| `lattice` | good | see-through | tropical_beach |  |
| `viewport` | good | see-through | sea_tunnel, space_station |  |
| `tank_window` | good | see-through | aquarium | Drawn with the toolkit in aquarium.py: a rounded opening in a deep frame of dark painted steel, bolt heads top and bottom. |
| `green_window` | good | see-through | doomed | Drawn in doomed.py: the trimmed green plating with a window cut through it in a deep dark frame; see-through. |

### Jungle

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `jungle_leaves` | good |  | jungle_river, jungle_temple, temple_inside, tropical_beach | Drawn with the pixel-art toolkit. |
| `canopy` | good | glows | jungle_temple, redwood_road | Leaves at three depths - lit far ones, a middle layer, near silhouettes - with sky in the gaps. |
| `canopy_top` | good |  | glow_jungle, jungle_temple, tropical_beach | Use as the top of jungle walls. |
| `jungle_floor` | good |  | island_run, jungle_river, jungle_temple, jungle_trail, palm_house, temple_inside, volcano_road |  |
| `jungle_bark` | good |  | jungle_temple |  |
| `temple_stone` | good |  | jungle_temple, temple_inside |  |
| `temple_cornice` | good |  | jungle_temple | The last storey of each tier of a stepped pyramid. |
| `glyphs` | good |  | jungle_temple, temple_inside | Five kinds of cartouche; faces and animals would add variety. |
| `temple_roots` | good |  | jungle_temple, temple_inside |  |
| `temple_door` | good | glows | jungle_temple |  |
| `roof_comb` | good | see-through | jungle_temple |  |

### Ruins

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `limestone` | good |  | ancient_ruins, tropical_beach |  |
| `sandstone` | good |  | canyon_run, desert_highway, ghost_town, gold_mine, red_canyon | Drawn with the toolkit in desert.py: beds of red, orange and cream, the hard ones standing out as ledges, cross-bedding, joints, varnish streaking down from the ledges. |
| `sandstone_pale` | good |  | canyon_run, ghost_town, gold_mine, red_canyon | Drawn with the toolkit in desert.py: the cream cap rock near a canyon rim, for bands among the sandstone. |
| `slot_rock` | good |  | canyon_run, red_canyon | Drawn with the toolkit in desert.py: beds swept into flowing curves of orange, red, cream and violet, polished smooth. |
| `pueblo_stone` | good |  | red_canyon | Drawn with the toolkit in desert.py: thin sandstone slabs laid in courses in a thick mud mortar, chinked with small stones. |
| `pueblo_door` | good |  | red_canyon | Drawn with the toolkit in desert.py: the coursed stone with a T-shaped doorway, dark inside, poles laid over its head. |
| `ruin_paving` | good |  | ancient_ruins, dark_road, jungle_temple, sunken_temple, temple_inside |  |
| `dry_grass` | good |  | ancient_ruins, autumn_lane, autumn_lane_road, overgrown_highway, pilgrim_path, safari_drive | Fewer, larger clumps with more earth between them, so it is not busy at grazing angles. |
| `desert_wash` | good |  | canyon_run, close_encounter, desert_highway, desert_motel, ghost_town, gold_mine, high_noon, red_canyon, saloon | Drawn with the toolkit in desert.py: pale sand faintly rippled, washed-down pebbles, patches of crazed dried mud. |
| `colonnade` | good | see-through | - | Flat when seen along its length: use `column` objects for a row you look down (the ruins' peristyle now is). |
| `colonnade_top` | good | see-through | - |  |
| `colonnade_broken` | good | see-through | - |  |

### Beach

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `beach_sand` | good |  | coast_road, island_run, tropical_beach |  |
| `wet_sand` | good | mirror 0.28 | coast_road, island_run, tropical_beach |  |
| `shallows` | good | mirror 0.3 | canyon_run, island_run, jungle_temple, sky_islands, tropical_beach |  |
| `sea` | good | mirror 0.45 | ancient_ruins, basalt_coast, high_seas, island_run, storm_coast, tropical_beach |  |
| `bamboo` | good |  | tropical_beach | A node in each third of every pole, so they stagger from pole to pole instead of lining up across them. |
| `thatch` | good |  | tropical_beach | Each row stands out over the one under it and shades its top, so the rows read. |

### Landscape scale

Drawn in `scripts/landscape.py` for a map cell of about 100 m, seen from a giant's height (see Landscape scale in references/scene_format.md).

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `city_street` | good |  | kaiju_country | Drawn in landscape.py for a map cell of about 100 m: half a street along each edge - asphalt, kerbs, a dashed centre line along the top and left edges, zebra crossings at the corners - pale pavements with street trees, the block's own paving inside, where its `city_block` stands. The country town in kaiju_country. |
| `city_street_lit` | good | glows | kaiju_harbor, strait_bridge, volcano_island | The streets at night: sodium lamps along the pavements, cars' lights in the lanes, white coming and red going - they glow. |
| `harbor_water` | good | mirror 0.35 | hill_street, kaiju_harbor, storm_island, strait_bridge, volcano_island | Open water from high up: dark blue-grey, a slow swell and short waves catching the light, all lying one way; it reflects. |
| `quay` | good |  | kaiju_harbor, storm_island, strait_bridge, volcano_island | Big pale concrete slabs with dark joints, tyre marks and stains, a yellow line along it, the dots of the mooring bollards. |
| `container_yard` | good |  | kaiju_harbor | Blocks of shipping containers in rows, each its own colour - rust red, blue, green, grey, white, orange - their tops catching the light, a line of shadow under each row, lanes between the blocks. |
| `city_park` | good |  | kaiju_harbor | Lawns of two greens, pale gravel paths crossing them, clumps of tree crowns, each dark with a lit side. |
| `farmland` | good |  | giant_valley, kaiju_country | A patchwork of fields - wheat, ploughed earth, pasture, rapeseed, young crops, stubble - each with its rows running its own way, between hedgerows with trees in them. The layout is slid and wraps, so the fields cross the cell's edges; the six layouts (`farmland` to `farmland_f`) mixed at random read as one countryside. |
| `farmland_b` | good |  | giant_valley, kaiju_country | Another layout of `farmland`. |
| `farmland_c` | good |  | giant_valley, kaiju_country | Another layout of `farmland`. |
| `farmland_d` | good |  | giant_valley, hayride, kaiju_country | Another layout of `farmland`. |
| `farmland_e` | good |  | giant_valley, kaiju_country | Another layout of `farmland`. |
| `farmland_f` | good |  | giant_valley, kaiju_country | Another layout of `farmland`. |
| `forest_canopy` | good |  | giant_valley, kaiju_country, ring_station, strait_bridge, volcano_island | Broadleaf woods from above: big round crowns of many greens packed close, each lit on its upper left, dark gaps between; it wraps cell to cell. |
| `pine_canopy` | good |  | giant_valley | Pines from above: small dark blue-green crowns, close as bristles. |
| `river_water` | good | mirror 0.5 | giant_valley | A river from high up: green-grey water, lighter than the sea, the current drawn out in long streaks; it reflects. |
| `pasture` | good |  | blossom_road, giant_valley, ring_station, storm_island, strait_bridge, tulip_ride | Grass in broad patches of lighter and darker green, the stripes of the last mowing faint across it, a lone tree or two. |
| `road_ew` | good |  | kaiju_country | A country road at landscape scale across a cell of farmland: two lanes of asphalt, a dashed white line, pale edge lines, grass verges and a hedgerow with trees either side; its ends meet the next cell's. |
| `road_ns` | good |  | kaiju_country | The road down the cell. |
| `road_x` | good |  | kaiju_country | A crossroads, both roads, no hedge across either. |
| `lava_field` | good | glows | dark_road, volcano_island | Old lava from high up: black crust broken into plates (a wrapping Voronoi), ropy and rough, and in patches - where it still moves underneath - its cracks glowing orange. |
| `lava_flow` | good | glows | volcano_island, volcano_road | A river of molten lava: plates of dark crust riding on bright melt, yellow-white where it runs hottest; it all glows. |
| `black_sand` | good |  | dark_road, strait_bridge, volcano_island | A beach of black volcanic sand: wind ripples, darker where the sea wets it, pale pebbles and drift. |
| `desert_floor` | good |  | balloon_flight, mesa_desert | Desert from high up: red-brown sand and gravel in broad patches, darker desert pavement, pale braided washes, dots of scrub with their shadows. Three layouts to mix at random. |
| `desert_floor_b` | good |  | mesa_desert | Another layout of `desert_floor`. |
| `desert_floor_c` | good |  | mesa_desert | Another layout of `desert_floor`. |
| `desert_road` | good |  | mesa_desert | A desert highway down the cell: sun-faded asphalt, a dashed yellow line, pale sandy shoulders, the desert either side. |
| `desert_road_ew` | good |  | - | The highway across the cell. |
| `snow_fields` | good |  | winter_valley | Farmland under snow, from `farmland`'s own layout repainted: the fields white, each its own shade, the hedges buried to a faint line (dark ones read as paving from a low eye), their trees standing out; drifts across it. |
| `snow_fields_b` | good |  | winter_valley | Another layout of `snow_fields`. |
| `snow_forest` | good |  | ski_run, winter_valley | Pines under snow from above, from `pine_canopy`: the dark crowns white on their lit sides. |
| `frozen_lake` | good | mirror 0.18 | winter_valley | Grey-blue ice, white drifts streaked across it, a few long straight cracks; it reflects a little (0.18). Three layouts, mixed so a lake does not repeat cell by cell. |
| `frozen_lake_b` | good | mirror 0.18 | winter_valley | Another layout of `frozen_lake`. |
| `frozen_lake_c` | good | mirror 0.18 | winter_valley | Another layout of `frozen_lake`. |
| `ocean` | good | mirror 0.12 | archipelago, coast_road | Deep tropical sea from high up: saturated blue, a long swell, rare single-texel whitecaps (two-texel dashes read as floating slabs from a boat); it reflects a little. |
| `lagoon` | good | mirror 0.1 | archipelago | Clear turquoise over pale sand, light rippling on the bottom, a coral head here and there. |
| `reef_flat` | good |  | archipelago | Coral heads and spurs from above - brown, olive, a purple one - with channels of sand and turquoise between (the lagoon under it). |
| `white_sand` | good |  | archipelago, storm_island | White coral sand, faintly rippled, wetter in patches, a line of wrack here and there. |
| `palm_canopy` | good |  | archipelago | Coconut palms from above: stars of fronds, lit on one side, pale sand and shadow between. |

### Road scenes

Walls along a road scene's road, and its see-through surfaces (highway.py).

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `guard_rail` | good | see-through | mountain_pass, night_pass, overgrown_highway, storm_coast, suspension_bridge | A galvanised W-beam on thin posts, see-through; drawn for a wall along a road (`tile` [1, 0.3]). |
| `jersey_barrier` | good |  | grand_prix, rain_motorway | A concrete safety barrier: lit top, upright face, sloped foot, road dirt, a joint per block. |
| `cliff_face` | good |  | mountain_pass, night_pass, storm_coast | Granite in tall blocks, each leaning its own way to the light, fine joints, a few ledges, lichen. First a cracked mosaic. |
| `power_lines` | good | see-through | close_encounter, desert_highway, desert_motel, storm_chase, viaduct_train | Three wires sagging between poles over one tile (see-through): a wall at the crossarms. |
| `tower_windows` | good | glows | neon_avenue, neon_canal, neon_race, night_runway, sky_lane | A tower's face at night: windows four by four to a tile, some lit warm, cool or neon (glow). |
| `tower_windows_b` | good | glows | neon_avenue, neon_canal, neon_race, sky_lane | The same, another layout of lit windows. |
| `shopfront` | good | glows | neon_avenue, neon_canal, neon_race | A shop at a building's foot: its lit window of goods, a shutter half down, a sign in a pink neon tube with glyphs (glow). The window's glow toned down after it blew out to white close up. |
| `shopfront_b` | good | glows | neon_avenue, neon_canal, neon_race | The same with a cyan tube. |
| `shopfront_c` | good | glows | neon_avenue, neon_canal, neon_race | The same with an amber tube. |
| `coaster_track` | good | see-through | roller_coaster | A roller coaster's rails and ties and nothing else: a see-through road surface. |
| `coaster_frame` | good | see-through | roller_coaster | A coaster's white steel frame - uprights, girders, cross braces - see-through, for walls under the track. |
| `rail_track` | good |  | ghost_train, metro_ride, mine_ride, viaduct_train | Rails and sleepers in grey ballast, a road surface 1.4 wide: a mine's track, a railway's. |
| `grandstand` | good |  | grand_prix | Tiers of concrete steps and a crowd on every one, heads and shirts of every colour, a flag or two. |
| `suspension_cables` | good | see-through | suspension_bridge | A suspension bridge's main cable sagging across the tile from its top at both ends, the suspenders hanging from it every few texels (see-through): a wall along the deck, tiled at the towers' spacing. |
| `canal_house` | good | glows | night_canal | An old house's face over a canal at night: ochre plaster worn through to the brick in patches, a pale string course at each floor, four windows across and two floors up to a tile with stone sills and green shutters - a few lit warm behind a curtain, some shuttered. Walls in `blocks`. |
| `canal_house_b` | good | glows | night_canal | The same in rose plaster. |
| `canal_house_c` | good | glows | night_canal | The same in pale cream. |
| `canal_footing` | good |  | night_canal | The foot of a house standing in a canal: courses of pale stone, the waterline's band of green-black weed, wet streaks running up from it. A low wall under the houses. |
| `piste` | good |  | ski_run | Groomed snow: the corduroy ridges running down the slope (along a road), blue-white in their troughs, a seam between passes, glints of ice. A ski run's road surface. |
| `ski_fence` | good | see-through | ski_run | The orange safety net along a ski run: a diamond mesh between posts, its top edge banded, see-through between the cords. |
| `chairlift` | good | see-through | ski_run | A chairlift's cable along the top of the tile and one chair hanging from it, two riding, their skis dangling (see-through): a wall high over a run, a chair every tile. |
| `city_night` | good | glows | night_pass, sky_lane | A city at night from far above: avenues lit sodium orange with cars' lights along them, streets between, dark roofs pricked with lit windows, a sign or two in pink or cyan. For the land `below` a road in the sky. |
| `light_lane` | good | glows, see-through | sky_lane | A lane of light: cyan lines a unit apart down its length, magenta chevrons between, see-through and glowing - a road surface for flying traffic (a road surface tiles a unit to a texture, so a lane 2 wide has a line at each edge and one down the middle). |
| `tulip_field` | good |  | tulip_ride | A field of tulips in flower: rows of red blooms four to a tile running along the road, their leaves and the dark soil between. Ground bands of them close up into stripes of colour to the horizon. |
| `tulip_field_b` | good |  | tulip_ride | The same in yellow. |
| `tulip_field_c` | good |  | tulip_ride | The same in pink. |
| `tulip_field_d` | good |  | tulip_ride | The same in purple. |
| `peppermint` | good |  | candy_road | A road of peppermint candy: broad red and white stripes slantwise, glossy, their edges a little melted, a glint of sugar. |
| `frosting` | good |  | candy_road | Pink frosting spread thick, soft swirls in it, sprinkles of every colour: the ground of a land of sweets. |
| `wheat_field` | good |  | storm_chase | Ripe wheat in rows along the road, gold ears packed close, darker between the rows, patches bent over by the wind: the plains' ground. |
| `western_front` | good |  | high_noon | A frontier town's false front: upright boards painted faded red, a sign board across the top with its lettering, two dark windows either side of batwing doors, the porch's roof a dark band with its posts. One building to a tile, for walls in `blocks` along a main street. |
| `western_front_b` | good |  | high_noon | The same in ochre. |
| `western_front_c` | good |  | high_noon | The same in grey-blue. |
| `tunnel_cables` | good |  | metro_ride | A metro tunnel's wall: sooty concrete in its ring segments, bundles of cables slung along it in brackets, water stains. |
| `ruined_tower` | good |  | drowned_city | An abandoned tower block's face gone back to nature: weathered concrete in floor bands, empty windows four across, broken frames and scraps of blind, rust under the sills, ivy climbing from below and hanging from the ledges. |
| `ruined_tower_b` | good |  | drowned_city | The same in a warmer concrete. |
| `metro_tiles` | good |  | metro_ride | A metro station's wall: white tiles in their grid, a band of colour at shoulder height with the station's name in it. |
| `townhouse` | good |  | hill_street | A painted townhouse's face: lavender clapboard, a bay window on each floor in white trim, a few lit, a cornice along the top. Two floors to a tile, for walls in `blocks`. |
| `townhouse_b` | good |  | hill_street | The same in mint. |
| `townhouse_c` | good |  | hill_street | The same in cream. |
| `timber_house` | good | see-through | market_ride | A half-timbered house's face, gable and all: cream plaster between dark oak posts, beams and braces, leaded windows, a box of flowers, a plank door; see-through round the gable, so a street of them in `blocks` one tile each has a skyline of gables. |
| `timber_house_b` | good | see-through | market_ride | The same in ochre plaster. |
| `timber_house_c` | good | see-through | market_ride | The same in rose plaster. |

### Not yet sorted

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `saloon_wainscot` | good |  | saloon | Drawn with the toolkit in saloon.py: dark raised panels to a chair rail, skirting at the foot, flocked red paper (a gold trellis, a sprig in each lozenge) above. |
| `saloon_paper` | good |  | saloon | The flocked paper, a dark cornice along its top: the storey over `saloon_wainscot`. |
| `saloon_backbar` | good |  | saloon | A cabinet of dark panels, a shelf on it, shelves of green, amber and clear bottles in carved uprights. |
| `saloon_backbar_top` | good |  | saloon | A tall mirror in a carved frame under an arched cresting, a glint across it. |
| `saloon_window` | good | see-through | saloon | Six open panes in a dark frame: the sun comes through, and a bright street shows. |
| `tin_ceiling` | good |  | saloon | Pressed tin, cream gone yellow with smoke: square panels each pressed with a rosette. |
| `mine_rock` | good |  | gold_mine, mine_ride | Drawn with the toolkit in mine.py: brown rock broken into small masses by dark cracks, drill and pick marks. |
| `mine_rock_vein` | good |  | gold_mine, mine_ride | The rock with a seam of milky quartz running across it in a gentle wave, so cell to cell it joins up into one seam. Use it for a few cells only. |
| `mine_rock_gold` | good | glows | gold_mine, mine_ride | The seam with gold in it - flecks and a thread - glinting: it glows a little, so a lamp seems to catch it. |
| `glasshouse` | good | see-through | palm_house, ring_station | Drawn with the toolkit in glasshouse.py: white cast-iron uprights and transoms, a kick panel at the foot, open panes between (see-through). From outside, walls of it read as a cage: shoot a glasshouse from inside. |
| `encaustic` | good | mirror 0.12 | palm_house | Encaustic tiles: a diamond in each square of terracotta, cream centres alternating black and blue, faint black joints. |

## Props (456)

Camera-facing sprites. "tall" is the default height in world units (a wall is 1); "no shadow" props hang, float or burn, so they get no contact shadow.

### Furniture and interior

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `armchair` | good | 0.6 tall | claude_study, haunted_house, mansion_library, salt_flat |  |
| `bed` | good | 0.4 tall | bunker_lab, ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: an iron bedstead with uprights, a mattress in white sheets, a pillow, a grey blanket turned back, castors. |
| `bench` | good | 0.35 tall | aquarium, coast_lighthouse, garden_encounter, gui_menus, hospital_garden, palm_house, post_presets, rainy_street, village_green, village_hours | Redrawn with the toolkit in basics.py: three backrest slats and two in the seat, held in cast-iron ends with scrolled armrests and curving legs. |
| `arcade_cabinet` | good | 0.68 tall, glows, aura | - | Drawn with the toolkit in bar.py: a dark cabinet with neon side art, a lit marquee in pseudo-letters, a space shooter on a scanlined screen, joystick and buttons, a coin door. The `arcade_cabinet` object is one in 3D: the neon bar uses that. |
| `bar_counter` | good | 0.35 tall, glows, no shadow | neon_bar | Drawn with the toolkit in bar.py: dark raised panels, a chrome rail, the black lip of the top, a magenta light strip along the foot; a card that repeats along its length. |
| `bar_stool` | good | 0.27 tall | neon_bar, neon_street | Drawn with the toolkit in bar.py: a red vinyl seat on a chrome pole with a foot ring and a weighted base. |
| `booth` | good | 0.5 tall, glows | neon_bar | Drawn with the toolkit in bar.py: a high back buttoned in teal vinyl, the seat, a formica table on a chrome leg with a glowing lamp. |
| `jukebox` | good | 0.56 tall, glows, aura | neon_bar | Drawn with the toolkit in bar.py: bands of red, gold and blue light round its arch, bubble tubes up both sides, the records in a window, a grille. |
| `bottles` | good | 0.12 tall | neon_bar, neon_street, saloon | Drawn with the toolkit in bar.py: green, amber and clear bottles at different heights with labels and glints. |
| `info_plaque` | good | 0.42 tall, glows | aquarium | Drawn with the toolkit in aquarium.py: a slanted panel on a post, lit blue from behind, a fish outline and lines of text too small to read. |
| `book_stack` | good | 0.22 tall | claude_study, drowned_library, mansion_library |  |
| `chest` | good | 0.3 tall | castle_keep, fjord, kelp_forest | Redrawn with the toolkit in basics.py: oak planks under a rounded lid, iron straps studded with rivets, iron corners, a brass lock plate. |
| `console` | good | 0.85 tall, glows | bunker_lab, orbital_hangar, space_station |  |
| `crate` | good | 0.4 tall | 20 scenes | Redrawn with the toolkit in basics.py: planks behind battens and a diagonal brace, nails at the corners, a stencilled arrow. |
| `barrel` | good | 0.45 tall | 22 scenes | Redrawn with the toolkit in basics.py: bulging staves turned on a lathe, three iron hoops, the lid showing at the top. |
| `locker` | good | 1 tall | bunker_lab |  |
| `lectern` | good | 0.5 tall | chapel_graveyard |  |
| `open_book` | good | 0.12 tall, glows, no shadow | claude_study, drowned_library, mansion_library |  |
| `pew` | good | 0.42 tall | cathedral_ruin, chapel_graveyard | The `pew` object is one in 3D: the glass chapel stands rows of them. |
| `table` | good | 0.36 tall | castle_keep | Redrawn with the toolkit in basics.py: a thick top with grain along it, an apron, turned legs, the far pair darker. |
| `throne` | good | 0.95 tall | castle_keep |  |
| `wheelchair` | good | 0.45 tall | ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: side on: a big spoked wheel with its push rim, a caster, leather seat and back, armrest, handles, footrest. |
| `writing_desk` | good | 0.55 tall, glows | claude_study, drowned_library, mansion_library |  |
| `globe` | good | 0.45 tall | claude_study, drowned_library, mansion_library |  |
| `orrery` | good | 0.6 tall, glows | claude_study |  |
| `telescope` | good | 0.8 tall | claude_study, mansion_library |  |
| `painting` | good | 0.45 tall, no shadow | - |  |
| `wall_clock` | good | 0.28 tall, no shadow | bunker_lab, hall_of_doors, rainy_street |  |
| `banner` | good | 0.95 tall, no shadow | castle_keep, grand_prix, market_ride, rainy_street |  |
| `chains` | good | 0.6 tall, no shadow | castle_keep |  |
| `ladder` | good | 1 tall, no shadow | capsule_hotel, drowned_library, red_canyon, sewer_tunnels |  |
| `pipe_valve` | good | 0.32 tall, no shadow | bunker_lab, clockwork_city, sewer_tunnels |  |
| `sack` | good | 0.42 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, gold_mine, market_ride, neon_street, rain_alley, rainy_street, sewer_tunnels, village_green, village_hours, woodland_night |  |
| `bucket` | good | 0.32 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, neon_street, rain_alley, rainy_street, sewer_tunnels, village_green, village_hours |  |

### Light and fire

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `brazier` | good | 0.85 tall, glows, no shadow | ancient_ruins, castle_keep, coast_lighthouse, dark_road, temple_inside, underworld_river |  |
| `campfire` | good | 0.4 tall, glows, no shadow | fjord, tropical_beach, woodland_night |  |
| `candles` | good | 0.2 tall, glows, no shadow | autumn_garden, castle_keep, cathedral_ruin, chapel_graveyard, drowned_library, glass_chapel, gui_lantern, gui_themes, gui_trade, jungle_temple, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `ceiling_lamp` | good | 0.3 tall, glows, no shadow | bunker_lab, metro_ride, sewer_tunnels |  |
| `chandelier` | good | 0.45 tall, glows, no shadow | castle_keep, claude_study, haunted_house, saloon |  |
| `cobweb` | good | 0.9 tall, no shadow | ghost_train, haunted_house, mansion_library | Drawn with the toolkit in haunted.py: threads radiating from a corner with sagging spiral rings, a broken strand; translucent. |
| `candelabra` | good | 1.2 tall, glows, aura | castle_keep, ghost_train, haunted_house, mansion_library | Drawn with the toolkit in haunted.py: a turned brass stem on a tripod foot, five curved arms with candles burning, wax run down them; aura. |
| `portrait` | good | 0.75 tall, glows, no shadow | ghost_train, haunted_house, mansion_library | Drawn with the toolkit in haunted.py: an oval beaded gilt frame round a pale, unsmiling face, black coat and white collar; the eyes glow faintly. |
| `grandfather_clock` | good | 1.6 tall | ghost_train, haunted_house, mansion_library, salt_flat | Drawn with the toolkit in haunted.py: a mahogany case: hood with a broken pediment and finial, a dial near midnight, a glass door on the pendulum. |
| `balustrade` | good | 0.5 tall | haunted_house | Drawn with the toolkit in haunted.py: turned balusters every eighth of a unit between handrail and base rail, newel posts; three units a card. |
| `lamp_post` | good | 1.6 tall, glows | clockwork_city, drowned_city, garden_encounter, gui_menus, hill_street, hospital_garden, night_canal, night_highway, post_presets, rain_alley, rainy_street, sleigh_ride, window_garden | Thin at a distance. |
| `lantern` | good | 0.3 tall, glows, no shadow | 21 scenes |  |
| `sconce` | good | 0.32 tall, glows, no shadow | castle_keep, claude_study, rainy_street, saloon |  |

### Nature

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `boulder` | good | 0.55 tall | canyon_run, chapel_graveyard, island_run, kelp_forest, kelp_run, moon_drive, mountain_pass, pilgrim_path, red_planet, sunken_temple | Redrawn with the toolkit in forest.py: a settled rock with a lesser lobe and cracks, moss over its top, lichen spots. Drawn 4 ways (variants), one picked per placement. |
| `bush` | good | 0.5 tall | cathedral_ruin, chapel_graveyard, coast_lighthouse, forest_path, mountain_pass, overgrown_highway, palm_house, redwood_road, window_garden, woodland_night | Redrawn with the toolkit in forest.py: leaf clusters on fanned twigs, lit on top, dark underneath. Drawn 4 ways (variants), one picked per placement. |
| `bush_autumn` | good | 0.5 tall | autumn_garden, autumn_lane | Drawn with the toolkit in forest.py: the bush in rust red and orange. Drawn 4 ways (variants), one picked per placement. |
| `bush_snow` | good | 0.45 tall | winter_road, winter_woods | Drawn with the toolkit in forest.py: a lumpy cushion of snow, blue in its hollows, twigs poking up through it. |
| `birch` | good | 3 tall | fjord, forest_path, overgrown_highway, palm_house, ring_station, sky_islands, village_green, village_hours, woodland_night | White trunk and a second stem banded with black, an airy crown of small leaves in drooping clumps. Drawn 3 ways (variants), one picked per placement. |
| `birch_autumn` | good | 3 tall | autumn_lane, autumn_lane_road, hayride | Drawn with the toolkit in forest.py: the birch gone to gold, a few patches already orange. Drawn 3 ways (variants), one picked per placement. |
| `birch_winter` | good | 3 tall | winter_woods | Drawn with the toolkit in forest.py: the white birch bare: branches reaching out with fine twigs weeping from them, snow on a few. |
| `dead_tree` | good | 2.9 tall | chapel_graveyard, dark_road, enchanted_path, haunted_house, misty_moor, woodland_night | Redrawn with the toolkit in forest.py: a split trunk on a gnarled foot, bare limbs forking into twigs, grey peeling bark. Drawn 3 ways (variants), one picked per placement. |
| `fern` | good | 0.42 tall | autumn_garden, autumn_lane, cathedral_ruin, chapel_graveyard, fjord, forest_path, jungle_river, jungle_temple, jungle_trail, misty_moor, mountain_pass, overgrown_highway, palm_house, redwood_road, temple_inside, tropical_beach, woodland_night | Redrawn: arching fronds from one crown. Drawn 3 ways (variants), one picked per placement. |
| `flowers` | good | 0.35 tall | blossom_road, fjord, garden_encounter, gui_menus, hospital_garden, mountain_pass, overgrown_highway, palm_house, post_presets, rainy_street, sky_islands, village_green, village_hours | Redrawn with the toolkit in basics.py: leaves and stems with blooms of four colours, five petals round a dark eye, at different heights. Drawn 3 ways (variants), one picked per placement. |
| `grass_tuft` | good | 0.4 tall | 22 scenes | Redrawn: thin arching blades. Drawn 4 ways (variants), one picked per placement. |
| `ivy_hang` | good | 0.8 tall, no shadow | cathedral_ruin, rainy_street |  |
| `log` | good | 0.28 tall | cathedral_ruin, drowned_city, fjord, forest_path, tropical_beach, winter_lake, winter_woods, woodland_night | Redrawn with the toolkit in forest.py: bark in long ridges, a branch stub, moss along the top, a pale ringed end. Drawn 3 ways (variants), one picked per placement. |
| `mushrooms` | good | 0.12 tall | autumn_garden, autumn_lane, autumn_lane_road, cathedral_ruin, chapel_graveyard, crystal_cave, enchanted_path, forest_path, jungle_temple, jungle_trail, overgrown_highway, redwood_road, woodland_night | Redrawn with the toolkit: a cluster of toadstools, domed caps on pale stems, the gills in shadow, white flecks on the red ones (one of them brown). Drawn 4 ways (variants), one picked per placement. |
| `palm` | good | 3.2 tall | archipelago, coast_road, garden_encounter, gui_menus, high_seas, hospital_garden, island_run, jungle_river, jungle_trail, launch_day, palm_house, post_presets, synthwave_drive, tropical_beach, volcano_road | Redrawn with the pixel-art toolkit: a ringed trunk, arching ragged fronds, coconuts. Drawn 3 ways (variants), one picked per placement. |
| `pine` | good | 3.4 tall | autumn_garden, autumn_lane, coast_lighthouse, enchanted_path, fjord, forest_path, giant_valley, kaiju_country, log_flume, ski_run, sky_islands, strait_bridge, woodland_night | Redrawn with the toolkit in forest.py: a spruce, tier on tier of drooping boughs with ragged hems over a straight trunk. Drawn 4 ways (variants), one picked per placement. |
| `reeds` | good | 0.8 tall | bayou_run, coast_lighthouse, jungle_river, launch_day, tulip_ride, winter_woods |  |
| `bald_cypress` | good | 4.2 tall | bayou, bayou_run | Drawn with the toolkit in swamp.py: a fluted, buttressed foot, limbs under flat sprays of feathery leaves, moss hanging from every limb, knees round it. Drawn 3 ways (variants), one picked per placement. |
| `spanish_moss` | good | 1.4 tall, no shadow | bayou | Drawn with the toolkit in swamp.py: a curtain of grey-green strands from a stub of branch, to hang with `z`. |
| `cypress_knees` | good | 0.3 tall | bayou, bayou_run | Drawn with the toolkit in swamp.py: knobbly cones of root standing out of the water. Drawn 3 ways (variants), one picked per placement. |
| `cattails` | good | 1 tall | bayou, bayou_run | Drawn with the toolkit in swamp.py: long blades and stems with brown velvet heads. Drawn 3 ways (variants), one picked per placement. |
| `kelp` | good | 5 tall | kelp_forest, kelp_run, sea_tunnel, sunken_temple | Drawn with the toolkit in sea.py: a swaying stipe from its holdfast, long golden blades streaming off small floats, a tangle at the top. Drawn 3 ways (variants), one picked per placement. |
| `brain_coral` | good | 0.3 tall | aquarium, kelp_forest, neon_bar, sea_tunnel, sunken_temple | Drawn with the toolkit in aquarium.py: a dome lit on its crown, its surface all meandering ridges (ochre) and grooves (green-brown). |
| `staghorn_coral` | good | 0.42 tall | aquarium, kelp_forest, neon_bar, sea_tunnel, sunken_temple | Drawn with the toolkit in aquarium.py: a thicket of golden-brown branches forking like antlers, lilac-white growing tips. |
| `sea_fan` | good | 0.62 tall | aquarium, kelp_forest, neon_bar, sea_tunnel, sunken_temple | Drawn with the toolkit in aquarium.py: a flat purple lace: thicker branches fanning from a short trunk with a fine net of little cells between them. |
| `anemone` | good | 0.26 tall | aquarium, kelp_forest, neon_bar, sunken_temple | Drawn with the toolkit in aquarium.py: a bubble-tip anemone: a red foot, salmon tentacles swollen to magenta bulbs, its pair of clownfish nestled among them. |
| `tube_sponge` | good | 0.36 tall | aquarium, kelp_forest, neon_bar, sunken_temple | Drawn with the toolkit in aquarium.py: violet tubes from a shared base, each with its lip and dark open mouth. |
| `reef_rock` | good | 0.6 tall | aquarium, neon_bar, sea_tunnel, sunken_temple | Drawn with the toolkit in aquarium.py: a mound of live rock in coralline and algae, with a sea fan, staghorn, a tube sponge and brain corals grown on it. |
| `rocks` | good | 0.22 tall | 40 scenes | Redrawn faceted like the 3D boulders: a heap of half-sunk stones - one big, a middling one or two, small ones in front - their faces flat planes lit by the way they face, pebbles at their feet, lichen in spots, a crack across the big one; greys and browns. Drawn 6 ways (variants), one picked per placement. |
| `snowy_pine` | good | 3.4 tall | aurora_palace, ski_run, sled_run, sleigh_ride, winter_lake, winter_road, winter_valley, winter_woods | Drawn with the toolkit in forest.py: the new spruce with snow lying in clumps along every tier's shoulders, crumbs on the hems and a small cap on the leader; dark needles between, so it still reads at a distance. Drawn 4 ways (variants), one picked per placement. |
| `boulder_snow` | good | 0.55 tall | ski_run, sled_run, winter_lake, winter_road, winter_woods | Drawn with the toolkit in forest.py: the boulder under a cushion of snow, deep where the top is flat and thin down the steep sides; in the `snow` scatter set. Drawn 4 ways (variants), one picked per placement. |
| `stump` | good | 0.3 tall | forest_path, tropical_beach, woodland_night | Redrawn with the toolkit in forest.py: a pale ringed cut face, furrowed sides, roots, a cushion of moss. Drawn 3 ways (variants), one picked per placement. |
| `tree` | good | 2.6 tall | dream_world, forest_path, garden_encounter, giant_valley, gui_menus, hospital_garden, kaiju_country, overgrown_highway, palm_house, post_presets, rain_motorway, ring_station, sky_islands, strait_bridge, tulip_ride, village_green, village_hours, woodland_night | Redrawn with the toolkit in forest.py: an oak with a furrowed trunk on a flared foot, limbs showing between lobes of crown lit from above. Drawn 3 ways (variants), one picked per placement. |
| `tree_autumn` | good | 2.6 tall | autumn_garden, autumn_lane, autumn_lane_road, hayride | Drawn with the toolkit in forest.py: the oak turned: orange and gold in patches cluster by cluster, a side going first, a little rust. Drawn 3 ways (variants), one picked per placement. |
| `tree_winter` | good | 2.6 tall | winter_woods | Drawn with the toolkit in forest.py: a bare oak grown by recursive branching down to twigs, snow along every limb level enough to hold it. |
| `glowshroom` | good | 0.16 tall, glows, no shadow | alien_world, crystal_cave, enchanted_path, glow_jungle | Redrawn with the toolkit in basics.py: domed caps freckled with paler spots over dark gills, pale stems; the caps glow. |
| `crystal` | good | 0.36 tall, glows, no shadow | alien_world, crystal_cave, enchanted_path, mine_ride |  |
| `stalagmite` | good | 0.8 tall | crystal_cave |  |

### Debris

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `bones` | good | 0.22 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, crystal_cave, dark_road, derelict_ship, neon_street, rain_alley, sewer_tunnels, temple_inside, underworld_river, woodland_night |  |
| `broken_barrel` | good | 0.46 tall | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, neon_street, rain_alley, rainy_street, sewer_tunnels, woodland_night | Redrawn with the toolkit in basics.py: the hooped bottom half, its front staves splintered off at different heights over the dark inside, the back staves taller, loose staves and a fallen hoop. |
| `rubble` | good | 0.34 tall | ancient_ruins, bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, rainy_street, sewer_tunnels, woodland_night | Drawn 3 ways (variants), one picked per placement. |

### Monuments and outdoors

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `column` | good | 1 tall | sky_road | Redrawn: a fluted Doric column with capital and plinth. |
| `fountain` | good | 0.9 tall | palm_house | Redrawn with the toolkit in basics.py: a moulded basin with water in it, a fluted pedestal and bowl, water spilling in arcs. |
| `gravestone` | good | 0.6 tall | chapel_graveyard, haunted_house |  |
| `stone_cap` | good | 0.44 tall | - | Drawn with the toolkit in basics.py: a slanted, chipped crown of stone with lichen, to set on a one-cell block so a standing stone has a weathered top. |
| `grave_cross` | good | 0.55 tall | chapel_graveyard, haunted_house |  |
| `signpost` | good | 1.3 tall | coast_lighthouse |  |
| `statue` | good | 1.5 tall | garden_encounter, gui_menus, hospital_garden, mansion_library, post_presets, sky_islands | Redrawn with the toolkit in basics.py: a draped woman in weathered marble raising a wreath, folds catching the light, on a moulded plinth with lichen. |
| `monolith` | good | 2.2 tall | alien_world |  |
| `rowboat` | good | 0.3 tall | bayou, coast_lighthouse, gui_lantern, storm_island, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: a clinker hull of lapped strakes, the top one painted a faded teal, a lighter gunwale, the bow rising, an oar along it. |
| `anchor` | good | 0.75 tall | kelp_forest, kelp_run | Drawn with the toolkit in sea.py: an iron anchor: ring, stock, shank, curved arms and spade flukes, rusted and grown over. |
| `wreck_mast` | good | 3.6 tall | kelp_forest, kelp_run | Drawn with the toolkit in sea.py: a snapped mast leaning, a yard askew, torn rigging, furred with weed. |
| `buoy` | good | 0.5 tall, glows | coast_lighthouse, island_run | Redrawn with the toolkit in basics.py: a red can with a white band, a lattice cage carrying its lit lamp, ripples at the waterline. |
| `snowman` | good | 0.62 tall | winter_lake, winter_woods |  |
| `scarecrow` | good | 1.9 tall | autumn_lane, hayride | Drawn with the toolkit in village.py: post and crossbar, a sack head with a stitched face, a battered hat, a patched coat with straw at the cuffs and hem, a crow on one arm. |
| `pumpkin` | good | 0.32 tall | autumn_lane, hayride | Drawn with the toolkit in village.py: a squat gourd of deep ribs, a woody stem, a curl of vine and a leaf. |
| `jack_o_lantern` | good | 0.34 tall, glows, aura | autumn_lane, ghost_train, haunted_house, hayride | Drawn with the toolkit in village.py: the pumpkin carved into a face that burns yellow (emissive), the rind darker round it; aura. |
| `hay_bale` | good | 0.5 tall | autumn_lane, market_ride, storm_chase | Drawn with the toolkit in village.py: a square bale packed with stalks, two bands of twine, loose ends bristling. |
| `well` | good | 1.7 tall | market_ride | Drawn with the toolkit in village.py: a round wall of fieldstones with a coping, oak posts under a little shingled roof, a windlass, a rope and a bucket. The `well` object is one in 3D: the village uses that. |
| `cart` | good | 0.75 tall | ghost_town, market_ride, village_green, village_hours | Drawn with the toolkit in village.py: a hand cart: a plank bed with stakes on a big spoked wheel, its shafts down, loaded with sacks. |
| `market_stall` | good | 1.9 tall | market_ride, night_fair | Drawn with the toolkit in village.py: a red and white striped awning with a scalloped valance over a trestle of apples, cabbages and bread, crates beneath. |
| `inn_sign` | good | 0.75 tall | village_green, village_hours | Drawn with the toolkit in village.py: an iron bracket and scroll with a red board hanging from it, a gilt border and crown; stand it out from a front as a card. |
| `armor` | good | 0.66 tall | castle_keep, haunted_house |  |

### Sci-fi

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `antenna` | good | 2.4 tall, glows | alien_world, moon_base, neon_rooftop |  |
| `drone` | good | 0.22 tall, glows, no shadow | neon_race, orbital_hangar, space_station, space_trench |  |
| `hologram` | good | 0.55 tall, glows, aura, no shadow | neon_avenue, neon_canal, orbital_hangar, sky_lane, space_station |  |
| `lander` | good | 1.6 tall, glows | alien_world, moon_base, moon_drive, red_planet |  |
| `dome` | good | 2.6 tall, glows, aura | moon_base, moon_drive, red_planet | Drawn with the toolkit in moon.py: a geodesic frame of white struts over glass, rows of plants under pink grow lights, an airlock; glows. |
| `hab_module` | good | 1.3 tall, glows | moon_base, moon_drive | Drawn with the toolkit in moon.py: a ribbed white cylinder on legs, lit portholes, an end hatch, a radiator fin. |
| `solar_array` | good | 1.4 tall | moon_base, moon_drive | Drawn with the toolkit in moon.py: dark-blue cells in a silver frame tilted on a mast, a cable down. |
| `rover` | good | 0.8 tall | moon_base | Drawn with the toolkit in moon.py: a white chassis on six wire-mesh wheels, two seats, a dish on a mast, a foil-wrapped box. |
| `sci_crate` | good | 0.35 tall, glows | derelict_ship, moon_base, neon_street, night_market, orbital_hangar, space_station |  |
| `toxic_barrel` | good | 0.4 tall, glows, aura | doomed | Drawn in doomed.py: a ribbed, dented drum brimming with glowing green sludge that runs down its sides. |
| `corpse` | good | 0.13 tall | doomed | Drawn in doomed.py: a fallen soldier on his side in a pool of blood, an arm flung out, the helmet rolled off. |
| `medkit` | good | 0.1 tall | doomed | Drawn in doomed.py: a white kit with a red cross on its lid and a handle. |
| `ammo_clip` | good | 0.07 tall | doomed | Drawn in doomed.py: a magazine with the brass of its top round showing. |
| `armor_vest` | good | 0.12 tall | doomed | Drawn in doomed.py: a green combat vest laid flat: chest plates and a strap. |
| `fireball` | good | 0.22 tall, glows, no shadow | doomed, space_trench, volcano_road | Drawn in doomed.py: a white-hot core in orange flame with a ragged tail; additive. |
| `vector_runner` | good | 0.6 tall, glows | vector_world | Drawn in vector.py: a figure in a black suit traced with light: a visor, seams, a diamond on the chest, glowing hands; tint sets the colour. |
| `light_trail` | good | 0.22 tall, glows, no shadow | vector_world | Drawn in vector.py: a ribbon of light, brightest at its top edge; a card laid behind a racer, additive. |
| `light_beam` | good | 3 tall, glows, no shadow | vector_world | Drawn in vector.py: a column of light rising from the floor, bright at its foot and core; additive. |
| `glint` | good | 0.09 tall, glows, no shadow | vector_world | Drawn in vector.py: a white-hot point in a soft halo - a headlight, a beacon; it streaks and flares. |
| `salt_mound` | good | 0.22 tall | - | Drawn in saltflat.py: a round-topped mound of raked salt, lumpy, damp at its foot; set out in rows, each `scale` a little different. |
| `salt_heap` | good | 0.15 tall | - | Drawn in saltflat.py: two mounds of salt slumped together, long and low. |
| `salt_pile` | good | 0.12 tall | - | Drawn in saltflat.py: a small rough shovelful of salt, a clod rolled off its side. |
| `salt_clods` | good | 0.08 tall | salt_flat | Drawn in saltflat.py: a few lumps of salt left lying, of different sizes. |
| `waterfall` | good | 6 tall, no shadow | sky_islands | Drawn in skyisles.py: a sheet of falling water, white at its lip, breaking into mist toward its foot; a card. |
| `island_roots` | good | 2 tall, no shadow | dream_world, sky_islands | Drawn in skyisles.py: roots and vines dangling under an island's edge; a card. |
| `island_keel` | good | 6 tall, no shadow | - | Drawn in skyisles.py: the rock under a floating island tapering to a ragged point, banded, roots trailing; a billboard. |
| `rope_rail` | good | 0.42 tall, no shadow | sky_islands | Drawn in skyisles.py: a bridge's railing: a post at every unit and two sagging ropes; a card. |
| `glow_monstera` | good | 0.75 tall, glows | enchanted_path, glow_jungle | Drawn in glowjungle.py: the monstera at night, every leaf traced in cyan light. |
| `glow_fern` | good | 0.42 tall, glows | crystal_cave, enchanted_path, glow_jungle | Drawn in glowjungle.py: the fern at night, its fronds edged in light. |
| `glow_tree_fern` | good | 2.4 tall, glows | enchanted_path, glow_jungle | Drawn in glowjungle.py: the tree fern at night, traced in blue light. |
| `glow_heliconia` | good | 1.1 tall, glows | enchanted_path, glow_jungle | Drawn in glowjungle.py: the heliconia at night: leaves edged in green light, the flowers burning pink. |
| `glow_bromeliad` | good | 0.22 tall, glows | crystal_cave, enchanted_path, glow_jungle | Drawn in glowjungle.py: the bromeliad at night: violet light, a magenta heart. |
| `glow_liana` | good | 2.4 tall, glows | glow_jungle | Drawn in glowjungle.py: the liana at night, hanging, edged in blue. |
| `glow_pods` | good | 1.1 tall, glows | crystal_cave, glow_jungle | Drawn in glowjungle.py: a curling stalk hung with seed pods glowing from inside. |
| `glow_jungle_card_1` | good | 1.4 tall, glows, no shadow | glow_jungle | Drawn in glowjungle.py: jungle card 1 at night, faintly edged and specked with light. |
| `glow_jungle_card_2` | good | 3.4 tall, glows, no shadow | glow_jungle | Drawn in glowjungle.py: jungle card 2 at night, faintly edged and specked with light. |
| `glow_jungle_card_3` | good | 4 tall, glows, no shadow | glow_jungle | Drawn in glowjungle.py: jungle card 3 at night, faintly edged and specked with light. |
| `glow_jungle_card_4` | good | 4.6 tall, glows, no shadow | glow_jungle | Drawn in glowjungle.py: jungle card 4 at night, faintly edged and specked with light. |
| `ice_spire` | good | 2.4 tall, no shadow | aurora_palace, ice_cave | Drawn in icepalace.py: a tower's spire of ice, a tall faceted crystal. |
| `ice_throne` | good | 1.1 tall | aurora_palace | Drawn in icepalace.py: a throne cut from a block of ice, a high pointed back. |
| `icicles` | good | 0.4 tall, no shadow | aurora_palace, ice_cave | Drawn in icepalace.py: a row of icicles hanging from an eave; a card. |
| `ice_shards` | good | 0.5 tall | aurora_palace, ice_cave | Drawn in icepalace.py: shards of ice breaking up through the snow. |
| `brass_gear` | good | 2 tall, no shadow | - | Drawn in clockwork.py: a great toothed brass wheel with spokes and a hub; a card for a wall. |
| `great_clock` | good | 1.6 tall, no shadow | clockwork_city | Drawn in clockwork.py: a tower's great clock: an ivory dial in a brass ring, roman hours; a card. |
| `stasis_pod` | good | 1 tall, glows | derelict_ship |  |
| `shuttle` | good | 2.2 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: nose-on wedge hull in white and orange, lit cockpit and engine pods, landing legs, panel lines and vents. |
| `cargo_container` | good | 1.2 tall | orbital_hangar | Drawn with the toolkit in scifi.py: corrugated orange steel, corner castings, door rods, rust streaking down the ribs. Tint for other colours. |
| `power_loader` | good | 2 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: roll cage, hydraulic arms with forks, hazard stripes on the hip block, a lit work light. |
| `beacon` | good | 0.3 tall, glows, aura | orbital_hangar | Drawn with the toolkit in scifi.py: an amber dome in a wire cage on a squat base; glows, with an aura. |
| `reactor_core` | good | 2.8 tall, glows, aura | orbital_hangar | Drawn with the toolkit in scifi.py: a glowing column in steel collars with coolant pipes; glows, with an aura. |
| `robot_arm` | good | 1.8 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: three orange segments, dark joints, a turntable base, a welding spark. |
| `cables_hang` | good | 1.4 tall, no shadow | orbital_hangar | Drawn with the toolkit in scifi.py: slack loops of cable and a few dangling ends; hangs from a ceiling, no contact shadow. |
| `vending_machine` | good | 1.1 tall, glows, aura | - | Drawn with the toolkit in scifi.py: a red steel box, its front a lit window of cans in rows, a glowing strip, coin slot and hatch. The `vending_machine` object is one in 3D: the capsule hotel and the neon street use that. |
| `noodle_stall` | good | 1.6 tall, glows | neon_avenue | Drawn with the toolkit in scifi.py: a counter under a striped awning, red paper lanterns lit, a neon sign of pseudo-letters, pots. |
| `steam` | good | 1.2 tall, no shadow | clockwork_city, fjord, neon_avenue, neon_street, night_market, sled_run, viaduct_train, winter_lake | A dithered plume, soft and spreading as it rises; see-through by default. |
| `holo_ad` | good | 1.6 tall, glows, no shadow | neon_canal, neon_race, neon_rooftop, neon_street | A hologram koi in cyan and pink with scanlines, dorsal and pectoral fins; additive by default. |
| `wires_span` | good | 0.75 tall, glows, no shadow | neon_avenue, neon_canal, neon_rooftop, neon_street | Drawn with the toolkit in scifi.py: four sagging wires with paper lanterns, a card to sling across a street. |
| `food_cart` | good | 1 tall, glows | neon_rooftop, night_fair, night_market | Drawn with the toolkit in market.py: a teal cabinet on two wheels, a steel counter with a wok over a roaring burner, stock pots, bowls, a tin roof, a neon menu board and three bare bulbs. |
| `fruit_stall` | good | 0.95 tall, glows | market_ride, night_fair, night_market | Drawn with the toolkit in market.py: crates stepped back in three tiers heaped with oranges, apples, limes, bananas and grapes, price cards, a green tarp with a bulb and coloured lights. |
| `gadget_stall` | good | 0.95 tall, glows | night_fair, night_market | Drawn with the toolkit in market.py: glowing screens on a table in dark cloth, a pegboard of cables, headphones and boxes, a blue tarp with a neon sign along it. |
| `red_lantern` | good | 0.16 tall, glows, no shadow | neon_street, night_market | Drawn with the toolkit in market.py: ribbed red paper glowing from inside, black bands, a gold tassel, a painted pseudo-letter. |
| `lantern_span` | good | 0.6 tall, glows, no shadow | neon_avenue, neon_canal, neon_rooftop, night_fair, night_market | Drawn with the toolkit in market.py: a sagging rope hung with big red lanterns, a card to sling across a lane. |
| `neon_sign` | good | 1.5 tall, glows, aura | neon_avenue, neon_canal, neon_race, night_market, sky_lane | Drawn with the toolkit in market.py: a standing lightbox on a steel post, edged in pink tube and lettered top to bottom. |
| `neon_cocktail` | good | 0.4 tall, glows, no shadow | neon_avenue, neon_bar, neon_canal, neon_race, sky_lane | Drawn with the toolkit in bar.py: a cocktail glass in pink tube with an olive on a stick in green; additive. |
| `neon_fish` | good | 0.32 tall, glows, no shadow | neon_avenue, neon_bar, neon_canal, neon_race, sky_lane | Drawn with the toolkit in bar.py: a fish outline in cyan tube with scales, an eye and bubbles rising; additive. |
| `umbrella` | good | 0.42 tall, glows, no shadow | night_market | Drawn with the toolkit in market.py: a clear canopy beaded with rain, its ribs showing, a glowing shaft from tip to handle. |
| `scooter` | good | 0.42 tall, glows | neon_rooftop, night_market | Drawn with the toolkit in market.py: mint body panels, a dark seat, the front shield with its headlight lit, small fat wheels, a kickstand. |
| `stools_table` | good | 0.26 tall | night_market | Drawn with the toolkit in market.py: a low folding table with two bowls and chopsticks, a red and a blue plastic stool. |
| `power_pole` | good | 3.4 tall, glows | desert_highway, desert_motel, night_market | Drawn with the toolkit in market.py: a concrete pole, crossarm and insulators, a transformer drum, a street lamp, cables looping, posted bills. |
| `water_tower` | good | 1.5 tall | high_noon, neon_rooftop | Drawn with the toolkit in rooftop.py: a barrel of staves bound with iron hoops under a conical cap, on steel legs with cross bracing and a platform, a ladder. |
| `ac_unit` | good | 0.32 tall | neon_rooftop | Drawn with the toolkit in rooftop.py: a pale steel box on rails, louvres down one side, a round fan grille, a pipe. |
| `rooftop_sign` | good | 2.6 tall, glows, aura | neon_rooftop | Drawn with the toolkit in rooftop.py: three tall panels edged in neon and lettered in bold glowing pseudo-letters, on a steel lattice scaffold with a catwalk. |
| `sky_train` | good | 2.5 tall, glows, no shadow | neon_race, neon_rooftop | Drawn with the toolkit in rooftop.py: three pale cars with a red stripe and every window lit, on a concrete beam on slim pillars; a card that repeats along its length. |
| `crowd` | good | 0.66 tall, glows | launch_day, metro_ride, neon_avenue, neon_rooftop, night_fair, night_market | Drawn with the toolkit in market.py: a dozen figures in dark coats at different depths, some under umbrellas (a few lit), hoods, a bag. |
| `noodle_bowl` | good | 0.055 tall | neon_street | Red lacquer bowl seen a little from above: amber broth, noodles, half an egg, a pink swirl of fish cake, green onion, chopsticks across it. Sits on the noodle_stand counter. |
| `stock_pot` | good | 0.11 tall | neon_street | Stainless pot, lid ajar, riveted handles; steam set over it by the noodle_stand. |
| `bowl_stack` | good | 0.075 tall | neon_street | Five white rice bowls with blue bands, stacked. |
| `condiments` | good | 0.07 tall | neon_street | A tray of soy sauce, chilli oil and a cup of chopsticks. |

### Alien and dream

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `alien_egg` | good | 0.35 tall, glows | alien_world, derelict_ship | Redrawn with the toolkit in basics.py: a leathery, mottled egg with a wet sheen, veins glowing faintly green, four lips at its crown parting on a glow. |
| `alien_plant` | good | 1.1 tall, glows | alien_world |  |
| `balloon` | good | 2.6 tall, no shadow | balloon_flight, dream_world, night_fair, sky_road |  |
| `chess_king` | good | 1.55 tall | - | Drawn with the toolkit in dream.py: the tallest piece, crown and cross, turned marble. |
| `chess_rook` | good | 1.1 tall | - | Drawn with the toolkit in dream.py: a turned tower with a flared, crenellated top. |
| `chess_knight` | good | 1.2 tall | - | Drawn with the toolkit in dream.py: a horse head and neck on a turned foot, ridged mane, eye and ear. |
| `chess_bishop` | good | 1.3 tall | - | Drawn with the toolkit in dream.py: a slender stem and a mitre with its slit, a bead on top. |
| `chess_queen` | good | 1.45 tall | - | Drawn with the toolkit in dream.py: a tall stem and a beaded coronet with an orb. |
| `melting_clock` | good | 0.6 tall, no shadow | dream_chess, hall_of_doors | Drawn with the toolkit in dream.py: a clock face warped over a ledge, the hanging part stretched and dripping. |
| `hourglass` | good | 0.6 tall | dream_chess | Drawn with the toolkit in dream.py: glass bulbs in a wooden frame, sand running into a heap, a gleam. |
| `stone_arch` | good | 2.4 tall | dream_chess, jungle_trail, rope_bridge, sky_road, underworld_river | Drawn with the toolkit in dream.py: coursed piers and a round arch of voussoirs with a keystone, open in the middle. |
| `stair_float` | good | 2 tall | dream_chess, hall_of_doors | Drawn with the toolkit in dream.py: a flight of stairs on a soffit, broken off at both ends, stones falling. |
| `paper_boat` | good | 0.3 tall | dream_chess, hall_of_doors | Drawn with the toolkit in dream.py: folded planes, a peak and a crease. |
| `jellyfish` | good | 0.9 tall, glows, no shadow | drowned_library, kelp_forest | A bell of light frilled at the rim, oral arms and tentacles; additive and glowing, no shadow. |
| `sky_lantern` | good | 0.34 tall, glows, aura, no shadow | drowned_library, hall_of_doors, lantern_river | Drawn with the toolkit in dream.py: a tapering paper shade lit from inside, the flame at its foot, a wire ring; aura. |
| `book_fly` | good | 0.3 tall, no shadow | drowned_library, hall_of_doors, mansion_library | Drawn with the toolkit in dream.py: an open book with its covers raised as wings and its pages fanned. |
| `chess_pawn` | good | 0.9 tall | - | Drawn with the toolkit in dream.py: a turned marble pawn (lathe profile), faint veins. Tint dark for the other side. |
| `door_frame` | good | 1.1 tall | dream_chess, dream_world, salt_flat |  |
| `floating_rock` | good | 1.6 tall, no shadow | airship_voyage, dream_world, rope_bridge, sky_islands, sky_road |  |
| `koi` | good | 0.35 tall, no shadow | dream_chess, dream_world, drowned_library, hall_of_doors |  |
| `orb` | good | 0.2 tall, glows, aura, no shadow | coast_lighthouse, dream_world, enchanted_path, space_trench, storm_island, strait_bridge, underworld_river |  |
| `pocket_watch` | good | 0.8 tall, no shadow | dream_world |  |
| `sky_whale` | good | 2 tall, glows, no shadow | dream_world, drowned_library, salt_flat, sky_road |  |

### Jungle

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `banana_plant` | good | 1.7 tall | island_run, jungle_river, jungle_temple, jungle_trail, palm_house |  |
| `monstera` | good | 0.75 tall | jungle_river, jungle_temple, jungle_trail, palm_house | Drawn 3 ways (variants), one picked per placement. |
| `tree_fern` | good | 2.4 tall | island_run, jungle_river, jungle_temple, jungle_trail, palm_house, redwood_road |  |
| `heliconia` | good | 1.1 tall | jungle_river, jungle_temple, jungle_trail, palm_house |  |
| `bromeliad` | good | 0.22 tall | jungle_temple, jungle_trail, palm_house |  |
| `liana` | good | 2.4 tall, no shadow | jungle_temple, temple_inside |  |
| `kapok` | good | 7.5 tall | glow_jungle, island_run, jungle_river, jungle_temple, jungle_trail, volcano_road | An emergent tree: its crown clears a 4-unit canopy. |
| `canopy_crown` | good | 1.2 tall, no shadow | jungle_temple | Set on jungle wall tops so the canopy edge is crowns, not a hedge. |
| `stone_head` | good | 1.5 tall | glow_jungle, jungle_river, jungle_temple, jungle_trail |  |
| `stela` | good | 2.1 tall | dark_road, jungle_temple, temple_inside |  |

### Ruins

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `broken_column` | good | 1 tall | dark_road |  |
| `column_drum` | good | 0.42 tall | ancient_ruins, cathedral_ruin, sunken_temple | Flutes now run back along the drum, so it reads as a column; the end face is lit and stands proud of the body on a shadowed rim, scalloped by the flutes, a worn ring and the dowel hole. |
| `marble_head` | good | 1.1 tall | ancient_ruins, sunken_temple |  |
| `amphora` | good | 0.36 tall | ancient_ruins |  |
| `cow_skull` | good | 0.2 tall | canyon_run, desert_highway, ghost_town, gold_mine, red_canyon, saloon | Drawn with the toolkit in desert.py: a bleached longhorn skull: dark sockets and nose, horns curving out and up. |
| `clay_pot` | good | 0.34 tall | red_canyon, temple_inside | Drawn with the toolkit in desert.py: a round white pot painted in black bands and a zigzag, turned on a lathe. |
| `windpump` | good | 4.2 tall | ghost_town | Drawn with the toolkit in desert.py: a lattice tower of four splayed legs, cross-braced, a wheel of galvanised blades with its tail vane. |
| `water_trough` | good | 0.4 tall | high_noon | Drawn with the toolkit in desert.py: grey boards on short legs, water near the brim. |
| `wagon_wheel` | good | 0.55 tall | ghost_town, high_noon | Drawn with the toolkit in desert.py: an iron-shod rim, twelve spokes, a heavy hub. |
| `cypress` | good | 4 tall | ancient_ruins, window_garden |  |
| `saguaro` | good | 3.2 tall | close_encounter, desert_highway, desert_motel, ghost_town, gold_mine, red_canyon | Drawn with the toolkit in desert.py: a ribbed column with two arms bending up, spines along the ribs, white blossoms on the crown. |
| `prickly_pear` | good | 0.6 tall | canyon_run, desert_highway, ghost_town, gold_mine, red_canyon | Drawn with the toolkit in desert.py: oval pads growing out of one another, spines, magenta fruit along the top. Drawn 3 ways (variants), one picked per placement. |
| `tumbleweed` | good | 0.45 tall | canyon_run, desert_highway, ghost_town, gold_mine, high_noon, red_canyon, saloon | Drawn with the toolkit in desert.py: a loose ball of wiry dry stems, the light coming through. Drawn 3 ways (variants), one picked per placement. |
| `olive_tree` | good | 2.2 tall | ancient_ruins |  |
| `poppies` | good | 0.24 tall | ancient_ruins | Drawn 3 ways (variants), one picked per placement. |
| `dry_tuft` | good | 0.36 tall | ancient_ruins, autumn_lane_road, canyon_run, coast_road, desert_highway, ghost_town, gold_mine, island_run, night_highway, overgrown_highway, red_canyon, safari_drive, tropical_beach | Drawn 4 ways (variants), one picked per placement. |

### Beach

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `palm_lean` | good | 3 tall | coast_road, island_run, launch_day, palm_house, synthwave_drive, tropical_beach |  |
| `coconuts` | good | 0.1 tall | coast_road, island_run, tropical_beach |  |
| `canoe` | good | 0.3 tall | jungle_river, tropical_beach |  |
| `tiki_torch` | good | 0.75 tall, glows, aura, no shadow | tropical_beach |  |
| `hammock` | good | 0.55 tall | tropical_beach |  |
| `driftwood` | good | 0.2 tall | coast_road, drowned_city, island_run, tropical_beach |  |
| `surf` | good | 0.1 tall, no shadow | basalt_coast, log_flume, tropical_beach | A row along a waterline reads from eye height, where foam decals are edge-on. |
| `surf_glow` | good | 0.1 tall, glows, no shadow | tropical_beach |  |

### Animals

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `jaguar` | good | 0.34 tall, glows | glow_jungle, jungle_temple | Redrawn with the toolkit in basics.py: prowling, side on: a long low body, heavy shoulders, a broad head, rosettes spread over a golden coat, a pale belly; the eyes glow. |
| `macaw` | good | 0.3 tall | jungle_river, jungle_temple, palm_house |  |
| `goat` | good | 0.34 tall | ancient_ruins, fjord, mountain_pass | Redrawn with the toolkit in basics.py: compact and deep-bodied on short sturdy legs, a piebald coat, horns swept back, a beard, the tail flicked up. |
| `crab` | good | 0.08 tall | coast_road, island_run, kelp_forest, kelp_run, sunken_temple, tropical_beach |  |
| `seagull` | good | 0.14 tall, no shadow | airship_voyage, basalt_coast, fjord, high_seas, island_run, sky_islands, tropical_beach |  |
| `heron` | good | 0.95 tall | bayou, bayou_run, jungle_river | Drawn with the toolkit in swamp.py: a grey heron: long legs, the neck in an S, a yellow dagger of a beak, the black crest. |
| `deer` | good | 0.62 tall | forest_path, overgrown_highway, redwood_road, winter_woods | Drawn with the toolkit in forest.py: a deer side on: russet coat, pale belly and throat, slim legs, big ears, an antlered head up, a white tail. |
| `black_cat` | good | 0.13 tall, glows | neon_rooftop | Drawn with the toolkit in rooftop.py: sitting with its back to you, ears up, its tail round its feet, one green eye catching the light. |
| `alligator` | good | 0.2 tall, glows, no shadow | bayou, bayou_run, jungle_river | Drawn with the toolkit in swamp.py: only the snout, the eyes (which catch the light) and the ridged back above the water. |
| `fireflies` | good | 1.2 tall, glows, no shadow | bayou, bayou_run | Drawn with the toolkit in swamp.py: a loose swarm of tiny glowing lights with soft halos; additive. |
| `fish_school` | good | 0.9 tall, no shadow | aquarium, kelp_forest, kelp_run, sea_tunnel, sunken_temple | Drawn with the toolkit in sea.py: thirty-odd silvery fish headed one way, dark backs, thicker in the middle of the shoal. |
| `whale_shark` | good | 1.36 tall, no shadow | aquarium, sea_tunnel | Drawn with the toolkit in aquarium.py: the broad flat head with its mouth at the front, ridges down the flanks, tall first dorsal, crescent tail; pale spots and broken bars on a blue-grey back, white belly. |
| `manta_ray` | good | 0.9 tall, no shadow | aquarium, sea_tunnel, sunken_temple | Drawn with the toolkit in aquarium.py: seen from below: pointed wings, curled cephalic fins either side of the mouth, gill slits, a few dark blotches on the white belly shading grey to the dark margins. |
| `reef_shark` | good | 0.25 tall, no shadow | aquarium, kelp_run, sea_tunnel | Drawn with the toolkit in aquarium.py: a blacktip: sleek bronze-grey body, pointed snout, gill slits, white belly, black tips on the dorsal, pectoral and tail. |
| `sea_turtle` | good | 0.3 tall, no shadow | aquarium, kelp_run, sea_tunnel, sunken_temple | Drawn with the toolkit in aquarium.py: a green turtle from a little above: amber scutes and a rim of small plates, the head reaching forward, long front flippers swept back. |
| `clownfish` | good | 0.07 tall, no shadow | aquarium | Drawn with the toolkit in aquarium.py: a pair: orange with three black-edged white bands and black-edged fins. |
| `angelfish` | good | 0.13 tall, no shadow | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: an emperor angelfish: clean diagonal stripes of yellow and blue, a black mask edged pale blue, a blue face, a yellow tail. |
| `blue_tang` | good | 0.08 tall, no shadow | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: royal blue with the black palette loop, black-edged fins and a yellow tail. |
| `reef_shoal` | good | 0.5 tall, no shadow | aquarium, neon_bar, sunken_temple | Drawn with the toolkit in aquarium.py: three dozen anthias, orange-pink with a few purple and gold, spaced so they never clump. |
| `sea_nettle` | good | 0.45 tall, glows, no shadow | aquarium | Drawn with the toolkit in aquarium.py: a golden bell striped rust to its scalloped rim, long maroon tentacles, four pale frilled arms twisting; half see-through. |
| `moon_jelly` | good | 0.12 tall, glows, no shadow | aquarium, neon_bar, sea_tunnel | Drawn with the toolkit in aquarium.py: a clear saucer with the four lilac crescents in a ring, a fringe of short tentacles; additive and glowing. |
| `bubbles` | good | 1.2 tall, no shadow | aquarium, kelp_forest, kelp_run, sunken_temple | Drawn with the toolkit in sea.py: a column of bubbles swelling as they rise, bright rings with a glint; additive. |
| `crow` | good | 0.2 tall | autumn_lane, drowned_city, haunted_house, hayride, red_canyon, rope_bridge, village_green, village_hours | Drawn with the toolkit in village.py: glossy black with a blue sheen, the head up, a heavy beak. |
| `bats` | good | 0.6 tall, no shadow | ghost_train, haunted_house | Drawn with the toolkit in haunted.py: black bat silhouettes, wings spread or beating, at different sizes. |

### Cards and parts

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `jungle_card_1` | good | 1.4 tall | jungle_temple, tropical_beach | The front of a jungle fringe: bushes alone. |
| `jungle_card_2` | good | 3.4 tall | jungle_temple, tropical_beach | A few trees with bushes in front. |
| `jungle_card_3` | good | 4 tall | jungle_temple, tropical_beach | More trees, tall ones with crowns. |
| `jungle_card_4` | good | 4.6 tall | jungle_temple, tropical_beach | The back: a dense wall of trunks, crowns, palms and bushes. Repeats every 8 units. |
| `forest_card_1` | good | 1.2 tall | haunted_house, window_garden, woodland_night | The front of a forest fringe: bushes, ferns and grass. |
| `forest_card_2` | good | 3 tall | haunted_house, window_garden, woodland_night | Young spruce and birch with bushes in front. |
| `forest_card_3` | good | 4 tall | haunted_house, window_garden, woodland_night | Spruce, oak and birch with gaps between them. |
| `forest_card_4` | good | 4.8 tall | haunted_house, window_garden, woodland_night | The back: a dense wall of spruce and oak over undergrowth, darkest. Repeats every 8 units. |
| `autumn_card_1` | good | 1.2 tall | autumn_garden, autumn_lane | The front of an autumn fringe: turned bushes, ferns and grass. |
| `autumn_card_2` | good | 3 tall | autumn_garden, autumn_lane | Young gold birch and a spruce with turned bushes in front. |
| `autumn_card_3` | good | 4 tall | autumn_garden, autumn_lane | Oak, birch and spruce with gaps between them. |
| `autumn_card_4` | good | 4.8 tall | autumn_garden, autumn_lane | The back: a dense wall of turned oak and green spruce over undergrowth. |
| `winter_card_1` | good | 1.2 tall | winter_woods | The front of a winter fringe: bushes under snow and dry tufts. |
| `winter_card_2` | good | 3 tall | winter_woods | Young snowy spruce and bare birch with snowy bushes in front. |
| `winter_card_3` | good | 4 tall | winter_woods | Snowy spruce, bare oak and birch with gaps between them. |
| `winter_card_4` | good | 4.8 tall | winter_woods | The back: a dense stand of snowy spruce with bare oaks. |
| `swamp_card_1` | good | 1.4 tall | bayou | The front of a swamp fringe: cattails, reeds and cypress knees. |
| `swamp_card_2` | good | 3 tall | bayou | Young cypresses among cattails and knees (the moss that hung in the air on its own bough is gone). |
| `swamp_card_3` | good | 3.9 tall | bayou, bayou_run | A looser stand of cypresses hung with moss, cattails and knees at their feet. |
| `kelp_card_1` | good | 5 tall | kelp_forest, sunken_temple | The front of a kelp fringe: a few stalks. |
| `kelp_card_2` | good | 5.8 tall | kelp_forest, sunken_temple | The back: a dense stand of kelp. |
| `palm_trunk` | good | 3.2 tall | tropical_beach | The palm without its crown, for palm_3d. |
| `palm_crown` | good | 3.2 tall, no shadow | tropical_beach | The palm's crown alone, in the same frame as the trunk. |
| `glass_pane` | good | 1 tall | aquarium, neon_bar, orbital_hangar | A plain pane for the glass pass. |

### Landscape scale

At landscape scale, a map cell about 100 m: a kaiju is the height of a person in an ordinary scene.

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `kaiju` | good | 0.62 tall, glows | kaiju_country | Drawn with the toolkit in landscape.py: upright on legs like pillars, a heavy tail sweeping out behind it, small clawed arms held forward, a thick neck and a heavy blunt head; charcoal skin pebbled over, a pale ridged belly, two rows of jagged plates along its back and tail, traced from the body's edge and alternating in size. 0.62 tall, a person's height in an ordinary scene. Redrawn in the landscapes loop at the user's word: the legs set under the hips, the near one's haunch swelling out of the body (it used to stand in front of the belly and cut across it), the belly whole to the groin. Walking across the fields in kaiju_country. |
| `kaiju_roar` | good | 0.62 tall, glows | kaiju_harbor | Roaring: its head thrown back, its jaws open on two rows of teeth, its plates glowing a cold blue. The lower jaw is hinged at the cheek into the neck (there was a gap behind it), and the glow sits deep in the mouth (a big pale throat read as a hole). |
| `kaiju_wading` | good | 0.463 tall, glows | kaiju_harbor, strait_bridge | The roaring kaiju with the sea up to its thighs, stopping in a ring of surf where the water meets it - stand it on a water cell and it never floats. The surf is thin broken foam: close up, a solid band read as a plinth. |
| `blaze` | good | 0.24 tall, glows, no shadow | kaiju_country, kaiju_harbor, volcano_island | A building ablaze from a giant's height: flame tongues of red, orange and a white-yellow heart over embers, all glowing (additive). |
| `smoke_plume` | good | 1.2 tall, glows, no shadow | kaiju_country, kaiju_harbor, storm_island, volcano_island | Ninety billows heaped into a column a hundred metres and more, widening and leaning with the wind, dark brown-grey with paler tops, lit orange at its foot by the fire under it. |
| `tanks` | good | 0.071 tall | kaiju_harbor | A column of four tanks, side on, facing left, olive drab on dark tracks, their guns raised toward something tall. Redrawn at twice the resolution in the landscapes loop: road wheels in the tracks, a sloped glacis, a turret with its cupola. |
| `tanks_firing` | good | 0.071 tall, glows | kaiju_country, kaiju_harbor | The tanks with a burst at every muzzle - a white-hot core, flame thrown forward, smoke rolling off it (the old flash, a pale blob, read as a white box close up). |
| `helicopter` | good | 0.05 tall, glows, no shadow | kaiju_country, kaiju_harbor, strait_bridge | An army helicopter, side on: an olive body, a tail boom, skids, the blur of its rotor, a lamp burning at its nose. Float it with `z`; kaiju_harbor's hold the monster in `ray`s. |
| `jet` | good | 0.045 tall, glows, no shadow | kaiju_country, kaiju_harbor | A fighter jet, side on: grey, a swept wing and tail fin, the canopy, its afterburner glowing. |
| `pylon` | good | 0.55 tall | kaiju_country | An electricity pylon of steel lattice: legs splayed at its foot drawing in to a waist, three crossarms with insulators, braced in diagonals all the way up - see-through, two crossed planes. A line of them marches across kaiju_country, cables slung from arm to arm (`cable`). |
| `ash_plume` | good | 9 tall, glows, no shadow | dark_road, volcano_island, volcano_road | A volcano's ash column, 9 tall: 170 billows boiling up dense and dark, rising nearly straight and spreading into a flattened head, lit orange at its foot (it glows there). Tint it warm and give it a light inside at night. |
| `cargo_ship` | good | 0.5 tall | kaiju_harbor, strait_bridge | A container ship, side on, bow to the left: a dark hull over a red boot-top, containers of every colour stacked in bays, the white superstructure and bridge at the stern, its funnel. 0.5 tall, four times as long. Under the strait bridge; berthed at kaiju_harbor's container quay. |
| `ferry` | good | 0.28 tall, glows | archipelago, strait_bridge, volcano_island | A car ferry, side on: a white hull with a blue band, two decks of windows (lit), a squat funnel. |
| `sailboat` | good | 0.16 tall | archipelago, island_run, strait_bridge, volcano_island | A yacht under main and jib, side on, white against the water. |
| `giant_moth` | good | 0.72 tall, glows, no shadow | kaiju_harbor | The kaiju's rival, a giant moth seen from in front: four wings spread, each forewing with a pale band, a dark band and a ringed eye-spot, veins pressed into them, every wing rimmed in glowing blue-white (a slightly larger glowing copy of the wing under it); a furry thorax, a ringed abdomen, feathery antennae, glowing eyes. 0.72 tall. Over the bay in kaiju_harbor's sixth shot. |

### Road scenes

What a road scene (road.py) needs that nothing else drew (highway.py): cars from behind, signs, a checkpoint, a road tunnel.

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `sports_car` | good | 0.42 tall, glows | candy_road, close_encounter, coast_road, desert_motel, launch_day, mountain_pass, night_highway, night_pass, rain_motorway, redwood_road, ring_station, sea_tunnel, storm_coast, suspension_bridge, synthwave_drive, winter_road | Drawn with the toolkit in highway.py: a red convertible from behind, the top down - the driver dark-haired, the passenger's fair hair blown back - fat tyres under the fenders, the tail lights glowing either side of the plate, twin exhausts. Your own car, as a road shot's `vehicle`. |
| `car_compact` | good | 0.44 tall, glows | autumn_lane_road, coast_road, hill_street, launch_day, night_highway, night_pass, rain_motorway, ring_station, sea_tunnel, suspension_bridge | A small rounded car from behind, in blue: its roof and rear window, round tail lights, a chrome bumper. |
| `car_sedan` | good | 0.48 tall, glows | coast_road, desert_motel, hill_street, launch_day, mountain_pass, night_highway, rain_motorway, suspension_bridge | A boxy sedan from behind, pale: a raked rear window, the trunk lid, wide tail lights. |
| `box_truck` | good | 1.05 tall, glows | coast_road, desert_highway, ice_road, night_highway, rain_motorway, suspension_bridge | A delivery truck from behind: a tall box with a roll-up door, small tail lights low down, a black steel bumper. |
| `curve_sign` | good | 0.95 tall | coast_road, mountain_pass, night_pass | Black chevrons on a yellow board on two posts, pointing left (`flip` it for a bend to the right). |
| `billboard` | good | 2.6 tall | coast_road, desert_highway, overgrown_highway | A billboard on two legs and a catwalk: a sunset over the sea and a palm in flat bands of colour. |
| `checkpoint` | good | 2.6 tall | coast_road | A chequered banner with CHECKPOINT on a white band, slung between two red-and-white poles; stand it at `x` 0 over the road. |
| `traffic_cone` | good | 0.24 tall | night_highway | Orange, two white bands, on a black square foot. |
| `tunnel_ring` | good | 3.6 tall, glows | night_highway | One ring of a road tunnel end on: a tiled lining round the opening in a wide mass of concrete, a lamp at the crown. A row of them down the `middle` every 1.2 frames itself into the tube. |
| `tunnel_portal` | good | 5.775 tall | night_highway | A road tunnel's mouth: a concrete face round the opening, set in a grassy hillside wide enough to hide the rings behind it. |
| `trash_bag` | good | 0.16 tall | night_highway | A black rubbish bag, knotted, slumped: lumps inside, creases, a shine on the plastic. First drawn pale with a bottle's neck - it read as a vase; darker, wider, lumpier. For a city kerb (`street` scatter set). |
| `old_tyre` | good | 0.22 tall | night_highway | An old tyre propped on its edge, the tread round its rim, the hole through it (see-through). |
| `trash` | good | 0.05 tall | night_highway | Litter: a crumpled paper, a red can, a green bottle - a few pixels of colour in the grass. |
| `reflector_post` | good | 0.34 tall, glows | ice_road, mountain_pass, night_pass, storm_coast, winter_road | A white marker post, a black band, an amber reflector that glows a little (it catches the headlights). Every few units along a country road. |
| `highway_lamp` | good | 3.6 tall, glows | neon_avenue, rain_motorway, suspension_bridge | A tall steel street lamp, its arm curving out to a long lamp head glowing underneath; the arm reaches right, so a row is `flip`ped. |
| `sign_gantry` | good | 3.2 tall | rain_motorway | Two green motorway signs on a steel truss over the road - CITY CENTRE ahead, AIRPORT EXIT 12 to the right - white lettering and arrows, lattice legs. |
| `speed_sign` | good | 0.95 tall | desert_highway, mountain_pass | 80 in a red ring on a grey post. |
| `traffic_light` | good | 1.5 tall, glows | neon_avenue | A traffic light on its pole, three lamps under hoods: drawn three ways, red, amber or green lit (VARIANTS). |
| `tyre_stack` | good | 0.32 tall | grand_prix | Tyres stacked as a crash barrier, every other one banded white. First a red-and-white cushion; redrawn as black rubber with grooves. |
| `road_barrier` | good | 0.36 tall, glows | - | A road-works barrier: a plank striped red and white on two legs, an amber lamp on top, lit. |
| `start_lights` | good | 3 tall, glows | grand_prix | Five columns of red lamps, all lit, on a black panel slung between two poles over the start. |
| `jeep` | good | 0.62 tall, glows | canyon_run, ice_road, safari_drive, volcano_road | An open-top four-by-four from behind: olive, a roll bar, two in it - the passenger under a bush hat (fair hair read as a lamp) - a spare wheel on the tailgate, mud up its back. |
| `rally_car` | good | 0.48 tall, glows | canyon_run, volcano_road | A white hatchback in a blue livery from behind, a wing on its roof, mud flaps, mud sprayed up it. |
| `dirt_bike` | good | 0.55 tall, glows | desert_highway | A dirt bike and its rider standing on the pegs, from behind: a red helmet, a dark jacket. |
| `dust_cloud` | good | 0.62 tall | canyon_run | Dust thrown up behind a car: shaded puffs, lit on top (first a flat blob). Translucent by default (`opacity` 0.75). |
| `speedboat` | good | 0.44 tall | island_run, neon_canal | A white speedboat from behind, a red stripe, the outboard churning white water; set a little into the water, a `wake` decal behind it. |
| `narrowboat` | good | 0.9 tall | canal_boat | A canal boat's stern: green and red, the steerer at his brass tiller, the stove's chimney beyond. |
| `boat_bow` | good | 0.42 tall, glows | bayou_run, canal_boat, drowned_city, ice_cave, jungle_river, lantern_river, night_canal, underworld_river | The bow of your own boat from inside it: gunwales running to the stem, floorboards, a lantern lit on a post. A shot's `vehicle`. |
| `hover_car` | good | 0.36 tall, glows | neon_avenue, neon_canal, neon_race, sky_lane | A hover car from behind: a low dark wedge edged in cyan, a light bar, twin blue jets, floating on its own glow. |
| `neon_bike` | good | 0.52 tall, glows | neon_race | A long low bike lined in pink light, its rider crouched in a white helmet with a band of light. |
| `taxi` | good | 0.5 tall, glows | neon_avenue | A yellow taxi from behind, a chequered band, TAXI lit on its roof. |
| `brick_ring` | good | 3.25 tall | canal_boat | One ring of a brick barrel vault end on, moss and wet streaks on it; a row every unit vaults a canal (the first vault, `vault_arch` cards, read as square frames). Made taller so no sky shows over it. |
| `coaster_car` | good | 0.55 tall | roller_coaster | A roller coaster's front car from the seat behind: red, two riders with their arms up. |
| `mine_frame` | good | 2.2 tall, glows | mine_ride | A mine's timber set end on: two posts and a cap, braces, a lamp hung from it, lit; a row down the middle shores up a tunnel. |
| `mine_cart` | good | 0.38 tall | mine_ride | An iron mine cart from behind, riveted, ore heaped in it with gold glinting. |
| `starfighter` | good | 0.4 tall, glows | space_trench | A small starfighter from behind: a grey hull swept into wings angled down, a canopy, red wingtip lights, twin engines glowing (generic: no film's fighter). |
| `race_car` | good | 0.3 tall, glows | grand_prix | An open-wheel race car from behind: the rear wing on its pylon, fat tyres, the gearbox, the rain light, the driver's helmet; four liveries (red, blue, white, orange). |
| `car_oncoming` | good | 0.48 tall, glows | rain_motorway, winter_road | A car coming the other way, from the front: the windscreen with the driver dim behind it, the grille between two headlights lit white; the sedan's four paints (VARIANTS). Far off its lights are a pixel lost in fog - bring it within a dozen units. |
| `motel_sign` | good | 4.2 tall, glows | desert_motel | MOTEL in pink neon on an arrow board, a star at its tip, VACANCY lit green on a panel under it, on a tall pole; its tubes glow. |
| `gas_station` | good | 2.6 tall, glows | desert_motel | A gas station seen across its forecourt: a canopy lit white underneath over two red pumps, the shop's window lit behind, a price board on a pole. |
| `bridge_tower` | good | 10 tall, glows | hill_street, suspension_bridge | A suspension bridge's tower spanning the road: two tall legs in red paint stepping in as they rise, joined by portal beams; 10 tall, its legs 7 apart - a row of them every span, `suspension_cables` walls between. |
| `dark_castle` | good | 30 tall, glows | dark_road, dragon_flight | Black towers and spires on a crag, a curtain wall between them, a few windows lit red: a billboard for the far end of a fantasy road. Close enough, and under a thin fog, or it is lost. |
| `mooring_pole` | good | 1.3 tall | night_canal | A mooring pole striped round like a barber's pole with a gilt knob on top, weed where it meets the water: red, or `variant` 1 blue, 2 green. In twos and threes off the houses. |
| `canal_bridge` | good | 1.45 tall | night_canal | A bridge humped over a canal, seen from the water: one brick arch ringed in pale stone, the parapet capped in the same stone, the opening open so you pass under it. |
| `gondola` | good | 0.85 tall | night_canal | A gondola from behind: the black lacquered hull, the gondolier on the stern in a striped shirt and a straw hat, his long oar down into the water. |
| `washing_line` | good | 0.6 tall | night_canal | Sheets, shirts, trousers, towels and socks pegged on a sagging line, the colours in turn: a long card to hang across a canal or a lane at `z` 2 or so. |
| `slalom_gate` | good | 0.62 tall | ski_run | A slalom gate: a panel stretched between two poles, a white stripe across it - red, or `variant` 1 blue - set down the course turn and turn about. |
| `skier` | good | 0.5 tall | ski_run | A skier from behind, crouched over the skis in a red jacket and dark salopettes, a white helmet, the poles tucked back. |
| `ski_tips` | good | 0.4 tall | ski_run | Your own skis from the skier's eye, curling up at their tips, a stripe down each: a shot's `vehicle` (`ahead` 0.85, `z` 0.3, `scale` 0.24 under a camera pitched down the slope). |
| `lift_tower` | good | 3 tall | ski_run | A chairlift's steel tower on its footing, the crossarm at its head with the wheel trains either end that the `chairlift` walls' cables ride on. |
| `moon_buggy` | good | 0.55 tall | moon_drive, red_planet | A moon buggy from behind: two astronauts side by side (the commander's red stripes), their packs and helmets, the gold visors catching the light; the dish antenna at the front left, a gold box at the back, wire-mesh wheels. |
| `loco_boiler` | good | 0.6 tall | viaduct_train | The view from a steam engine's footplate: the boiler running away ahead in green paint, brass bands round it, the handrails, the dome and the chimney over the smokebox. A shot's `vehicle`; a stroke's dome read flat - toned round by hand. |
| `telegraph_pole` | good | 2.9 tall | close_encounter, storm_chase, viaduct_train | A weathered wooden pole of the railway age with three crossarms of glass insulators; a `power_lines` wall at its arms. |
| `windmill` | good | 4 tall | tulip_ride | A windmill of the low country: a brick base, the tapering thatched body with a stage round it, the cap and four lattice sails in an X. 4 tall. |
| `cyclist` | good | 0.6 tall | tulip_ride | Someone cycling ahead on an upright bike, from behind: a coat and a scarf, the back wheel and its red light, one knee up. |
| `bike_bars` | good | 0.3 tall | tulip_ride | Your own bicycle from the saddle: the swept-back bars, your hands on the grips, a bell, a wicker basket of tulips on the front. A shot's `vehicle`. |
| `runway_light` | good | 0.08 tall, glows | night_runway | A runway's edge light: a lens on a short stalk, lit, fullbright - tint it white, blue, green or red. |
| `control_tower` | good | 8 tall, glows | night_runway | An airport's control tower at night: the concrete shaft, the cab glazed all round and lit green-white, a red beacon, a few lit windows. 8 tall. |
| `airliner` | good | 2.6 tall, glows | night_runway | An airliner from behind, lifting off: the fin, the tailplane, the wings swept to their red and green lights, the engines under them, its lights lit. |
| `cockpit` | good | 0.84 tall, glows | night_runway | Your own cockpit from the left seat: the panel's glowing screens, the glareshield, the windscreen's frame and pillars, the yoke. A shot's `vehicle`, big enough that the frame's top is out of view (a centre post hid the runway: dropped). |
| `stilt_shack` | good | 2.2 tall, glows | bayou_run | A shack on stilts over the bayou: weathered boards under a rusted tin roof, a porch on its posts, the window and a lantern lit. 2.2 tall. |
| `camel` | good | 0.8 tall | camel_caravan | A camel walking ahead in a caravan, from behind: the long legs, the haunches and tail, a saddle blanket in red and blue, its rider in a pale robe and headcloth, the neck and head off to one side. The first drawing's thin legs read as a jellyfish. |
| `camel_head` | good | 0.5 tall | camel_caravan | Your own camel from the saddle: the long neck reaching away, the head with its ears up, the halter's rope, a corner of the blanket. A shot's `vehicle`; keep it small and ride beside the caravan, or it hides it. |
| `pyramid` | good | 20 tall | camel_caravan | A great pyramid for the horizon: pale stone, one face sunlit and one in shade. 20 tall. |
| `candy_cane` | good | 1.8 tall | candy_road | A candy cane as tall as a lamp post, striped slantwise round its stem, its crook over the road. |
| `lollipop` | good | 2.4 tall | candy_road | A lollipop tree: a swirled disc of pink and white candy on a white stick. |
| `gumdrop` | good | 0.8 tall | candy_road | A sugared gumdrop the size of a hill: pink, or `variant` 1 blue, 2 green, 3 orange. |
| `gingerbread_house` | good | 2 tall, glows | candy_road | A gingerbread house: piped icing on its walls, a roof thick with icing, sweets along the eaves, a candy-cane door frame, its windows lit. |
| `skeleton` | good | 0.75 tall | ghost_train | A skeleton leaping out at a ghost train's riders: the skull grinning, the ribs, arms flung up with the fingers spread, one leg kicked up. Light it green. |
| `cherry_tree` | good | 3.2 tall | blossom_road, lantern_river | A cherry tree in full bloom: a dark trunk and limbs under a cloud of pink blossom, a few petals falling. 3.2 tall; set back from a road and not too big, or the crowns close over it. |
| `torii` | good | 3.6 tall | blossom_road, lantern_river | A vermilion shrine gate to stand over a road: two pillars on black feet, the lower beam through them, the top beam curving up at its ends and capped in black, a plaque between. 3.6 tall. |
| `snow_peak` | good | 18 tall | blossom_road, pilgrim_path | A lone volcano for the horizon, snow streaking its upper slopes, the rest blue with distance. 18 tall; a thick fog loses it. |
| `ghost_car` | good | 0.4 tall, glows | ghost_train | Your own ghost-train car from its seat: a purple cowl with a skull on its nose, its eyes lit red, the lap bar. A shot's `vehicle`; it needs a dim light of its own in the dark. |
| `tornado` | good | 30 tall | red_planet, storm_chase | A tornado: the funnel dropping from its cloud base, twisting in bands and snaking down to a rope in a skirt of dust. 30 tall; the first funnel's tip was too thin to reach the ground and it floated. |
| `barn` | good | 2.4 tall | close_encounter, hayride, storm_chase | A red barn with a gambrel roof, white trim and braced doors, a hay door in the gable, a tin silo beside it. |
| `pickup_truck` | good | 0.62 tall, glows | storm_chase | A storm chasers' pickup from behind: the tailgate, gear strapped in the bed, a mast of instruments on the cab's roof, its tail lights lit. |
| `mini_sub` | good | 0.5 tall, glows | kelp_run | A little research sub from behind: an orange hull, its glass dome with the pilot in it, the ducted propeller and side thrusters, a red tail light. |
| `light_shaft` | good | 8 tall, glows | kelp_run, redwood_road | A shaft of sunlight slanting down through water, brightest at the top, soft-edged; drawn `additive`. 8 tall. |
| `dog_team` | good | 0.4 tall | sled_run | Three pairs of huskies running away up a trail on their gangline, each its own coat, red harness, tails curled; the lead pair farthest. A few units ahead of the camera: the team you drive (the sled's own frame, drawn as a vehicle, fell out of view below them - dropped). |
| `log_cabin` | good | 1.8 tall, glows | sled_run, sleigh_ride | A log cabin in the snow: round logs crossing at the corners, a roof deep in snow, a stone chimney, its windows lit warm. |
| `porthole` | good | 1 tall | kelp_run | Your own submarine's viewport from inside: a bolted brass ring round the view, dark steel beyond. A shot's `vehicle`, close and big enough to frame the view. |
| `galleon` | good | 4 tall, glows | high_seas | A galleon from astern: the stern castle in dark wood and gilt, the stern windows lit, lanterns, the rudder; three masts of square sails with their yards, pennants. The first sails merged into one white cloud until the masts and yards were drawn over them. |
| `sea_fort` | good | 4 tall | high_seas | A stone fort on its rock in the sea: a crenellated curtain wall with gun ports, a round tower. |
| `bowsprit` | good | 0.75 tall | high_seas | Your own ship's bow from the deck: the rail, the bowsprit running out and up, a jib on its stays off to starboard. A shot's `vehicle`; drawn first with the jib in the middle, it hid the view. |
| `acacia` | good | 2.4 tall | safari_drive | An acacia: a thin forked trunk, the crown spread flat like a parasol. 2.4 tall. |
| `giraffe` | good | 1.8 tall | safari_drive | A giraffe side on, browsing: the long legs, the sloping back, the neck, the ossicones, the coat patched brown on tan. 1.8 tall. |
| `elephant` | good | 1.1 tall | safari_drive | An elephant side on, walking: the grey body, column legs, the ear spread in its shade, the trunk curling, a tusk. |
| `zebra` | good | 0.5 tall | safari_drive | A zebra side on, grazing, striped, its head down to the grass. |
| `flying_saucer` | good | 1.6 tall, glows | close_encounter | A flying saucer seen from below: the hull's wide disc, a ring of rim lights, the dome glowing, the port underneath blazing. |
| `tractor_beam` | good | 4 tall, glows | close_encounter | A cone of pale green light let down from a saucer to the ground, brightest at its walls and foot; drawn `additive`. Stand it tall enough to reach the saucer's port. |
| `cow` | good | 0.5 tall | close_encounter | A dairy cow side on, black patches on white. |
| `ferris_wheel` | good | 6 tall, glows | log_flume, night_fair | A big wheel at a fair at night: rim and spokes outlined in bulbs, red and blue cars hanging round it, the A-frame legs, the hub lit. 6 tall. |
| `horse` | good | 0.6 tall | high_noon | A saddled horse side on at a hitching rail, its reins round the rail. The first drawing - short body, neck straight up - read as a camel. |
| `lighthouse_tower` | good | 7 tall, glows | storm_coast | A lighthouse on its rock: the tower in red and white bands, the gallery, the lantern room blazing, a keeper's cottage at its foot with a window lit. 7 tall. |
| `lighthouse_beam` | good | 1.6 tall, glows | storm_coast | A lighthouse's beam: a long wedge of pale light from its point, rain caught in it; drawn `additive`. Far off and thin it was lost: big, near and thrown across the view. |
| `carousel` | good | 2.2 tall, glows | night_fair | A carousel at night: a striped canopy on its centre pole fringed with bulbs, horses on their poles, glowing warm. |
| `erupting_volcano` | good | 25 tall, glows | volcano_road | A volcano erupting at night: the dark cone, fire fountaining from its crater, rivers of lava down its flanks in glowing threads, the rim lit from inside. A billboard for the horizon, 25 tall; an `ash_plume` over it. |
| `log_boat` | good | 0.4 tall | log_flume | The front of your log-flume boat from its seat: the bark along its sides, the pale cut end, the grab bar. A shot's `vehicle`; its first light bark read as a pale block. |
| `prayer_flags` | good | 0.4 tall | pilgrim_path | A string of prayer flags: squares of cloth in blue, white, red, green and yellow in turn on a sagging line, lifting in the wind. A long card across a path. |
| `stupa` | good | 2.4 tall | pilgrim_path | A whitewashed stupa: a stepped base, the white dome with a painted band, a gilded spire of rings and its finial. |
| `basket_rim` | good | 0.4 tall | balloon_flight | Your own balloon basket's rim from inside: the wicker edge padded in leather, the burner's frame and ropes rising at its sides. A shot's `vehicle`, wider than the view. |
| `signal_light` | good | 0.5 tall, glows | metro_ride | A signal on a tunnel wall: two lamps in a black head on a bracket, red lit, or `variant` 1 green. |
| `metro_cab` | good | 1 tall, glows | metro_ride | Your own metro train's cab: the console's dials and glowing screen, the windscreen's frame, the controller's handle. A shot's `vehicle`; at 0.6 ahead its frame fell outside the view until it was made smaller and set higher. |
| `tractor` | good | 0.75 tall | hayride | An old red tractor from behind: the great rear wheels and their tread, the driver between the fenders in a cap, the exhaust stack, the hitch. |
| `hay_wagon` | good | 0.4 tall | hayride | The back of a hay wagon from your seat on a bale: bales along the sides, loose straw on the boards, the front rail and tow bar. A shot's `vehicle`, a `tractor` a little ahead. |
| `sleigh_horse` | good | 0.5 tall, glows | sleigh_ride | Your sleigh from its seat: the red dash with a lamp, the horse beyond - its rump, the collar and the harness hung with bells, the neck and the ears. The first drawing, all rump, read as a beetle. |
| `christmas_tree` | good | 1.6 tall, glows | sleigh_ride | A fir dressed for the winter feast: snow on its boughs, strings of small lights, a star on top; they glow. |
| `tram` | good | 0.8 tall, glows | hill_street | A cable tram from behind as it climbs or goes down a hill: red and cream, people standing on its back platform holding the poles, a lamp. |
| `dragon_neck` | good | 0.24 tall | dragon_flight | Your dragon from the saddle: its scaled neck with a row of spines, the head from behind - horns swept back, frills behind the jaw - the reins, the wings spread out past the view's edges. A shot's `vehicle`. Drawn tall at first, its head filled the view: it is wide and low now. |
| `dragon` | good | 3 tall | dragon_flight | A dragon on the wing from the side: the long neck and horned head, both wings raised, the barbed tail; crimson, or emerald or bronze by `variant`. |
| `wrecked_car` | good | 0.46 tall | overgrown_highway | A car left on the road years ago, from behind: rusted through in patches, tyres flat, the back window smashed, tail lights dead, the bumper hanging; moss on the roof, a vine down its back, weeds round its wheels. Faded red, blue or cream by `variant`. |
| `broken_overpass` | good | 4 tall | overgrown_highway | A motorway overpass snapped in the middle over the road: two piers, the deck broken with rebar out of both ends and one half sagging, a slab hanging by its bars, vines and ivy, a green sign askew, rubble under the gap. |
| `water_taxi` | good | 0.42 tall, glows | neon_canal | Your water taxi's bow from its seat: taxi yellow, a band of black and white checks down it, dark trim with a strip of cyan light inside each edge, the fare's display, a lamp at the bow - they glow. A shot's `vehicle`; set where the wooden bow sat it fell out of the view. |
| `floating_lantern` | good | 0.22 tall, glows, aura | lantern_river | A paper lantern on a little wooden float, lit from inside - its paper glows, a warm aura round it. Scattered on a river by the hundred. |
| `rocket_pad` | good | 20 tall, glows | launch_day | A rocket on its launch pad, ready: white, two boosters, black bands, fins; the steel service tower beside it with its arms across and its lights lit, vapour round its foot, the pad and its flame trench. For the horizon, `fullbright` under floodlights. |
| `airship` | good | 3 tall, glows | airship_voyage | An airship under way from the side: the long seamed envelope with two bands round it, fins at its tail, the brass-trimmed gondola slung under it, windows lit, a propeller. Cream, rust red or slate blue by `variant`. |
| `airship_deck` | good | 0.3 tall | airship_voyage | The bow of your own airship's gondola from its deck: the planks to the prow, a brass rail on both sides, the rigging rising out of view, a pennant. A shot's `vehicle`, wide and low. |
| `island_falls` | good | 12 tall | airship_voyage | A ribbon of water off a floating island's edge, in streaks, spreading as it falls and breaking into spray. The tall `waterfall` stood under an island read as a slab of glass. |
| `horse_neck` | good | 0.22 tall | market_ride | Your horse from the saddle: the shoulders and neck, the dark mane along its crest, the ears pricked and the forelock, the bridle, the reins. A shot's `vehicle`. The first neck was a narrow column: it has shoulders now. |
| `castle_hill` | good | 12 tall | market_ride | A fairy-tale castle on its green hill on a bright day: pale stone walls with battlements round a tall keep, round towers under blue pointed roofs, red pennants, the gate. |
| `redwood_trunk` | good | 24 tall | redwood_road | A giant redwood's trunk: red-brown bark in deep ridges, round and shaded, its foot flaring over the roots with moss and ferns, running up out of the view. Its first foot flared so wide the trunks read as hills. |

### The spooky island

The pieces of the three drawings the project began from (spooky.py): the canal tunnel, the window garden, the storm island.

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `vault_arch` | good | 1.6 tall, no shadow | canal_tunnel | Drawn in spooky.py: brickwork in the card's upper corners down to a ring of voussoirs, the courses beyond darkening toward the crown, open inside the arch. A card (`planes` 1): set across a tunnel every 1.3 they frame each other into the canal tunnel's vault. |
| `broken_casement` | good | 1 tall, no shadow | window_garden | A card 2 wide: plaster round a window of dark wood, its middle bar snapped and the transom broken, a shard left in each corner - clear but for glints across it and along its broken edge - a sill under it. Stood just inside a gap in the window garden's wall at `scale` 1.5. |
| `rose_bush` | good | 0.42 tall | window_garden | Drawn with the toolkit: a mound of dark leaves, red roses open over it. |
| `robed_statue` | good | 1.9 tall | dark_road, underworld_river, window_garden | A hooded figure in pale stone on a pedestal, its robe carved in folds, its hands folded, the face a shadow in the cowl. Light its front: in the window garden the moon is behind it. |
| `tattered_curtain` | good | 1.45 tall, no shadow | window_garden | Dusty red velvet hanging in folds from rings on an iron rod, its hem rotted ragged, a tear and moth holes. A card: one each side of the window garden's window. |
| `wall_lamp` | good | 0.2 tall, glows, aura, no shadow | canal_boat, canal_tunnel, metro_ride, night_canal | A round bulkhead lamp, a warm glass behind an iron cage; it glows, with an aura. Give it a light half a cell out from the wall - on the wall it only grazes it. |
| `iron_cabinet` | good | 0.7 tall | canal_tunnel | Riveted iron: two doors one over the other in a dark frame, hinges down one side, a rivet at each corner, a round black lock plate with its keyhole, rust weeping from the rivets. |
| `punt` | good | 0.2 tall | - | A flat-bottomed boat seen from its stern, a billboard - for a boat ahead down a canal. The canal tunnel uses a `ship_hull` in 3D instead, so its boat holds up from the side. |
| `storm_cloud` | good | 6 tall, no shadow | dragon_flight, storm_island | A bank of storm cloud for a sky at landscape scale: heavy puffs on a flat dark underside, their tops pale. `fullbright` - drawn in its own colours, as the sky is; eight of them far off and high over the storm island hide the `storm` sky's stars. |

### Not yet sorted

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `swamp_card_4` | good | 4.6 tall | bayou | The back: a dense stand of tall bald cypresses hung with moss, their crowns high enough to hide the wall's top. |
| `goods_apples` | good | 0.22 tall | - | Drawn with the toolkit in village.py: a heap of red apples on a shallow tray, for a stall's table. The `market_stand` heaps its trays in 3D now (`goods`). |
| `goods_cabbages` | good | 0.22 tall | - | Cabbages heaped on a tray, as the apples. The `market_stand` heaps its trays in 3D now (`goods`). |
| `goods_loaves` | good | 0.22 tall | - | Loaves heaped on a tray, as the apples. The `market_stand` heaps its trays in 3D now (`goods`). |
| `piano` | good | 0.46 tall | - | An upright: a dark case on carved legs, the fall open on ivory and ebony keys, brass sconces, music on the stand. Stand it as a card against a wall. The `piano` object is one in 3D: the saloon uses that. |
| `card_table` | good | 0.3 tall | - | A round table of green baize mid-game, seen a little from above: cards, stacks of chips, a bottle and two glasses. The `card_table` object is one in 3D: the saloon uses that. |
| `saloon_chair` | good | 0.32 tall | - | A bentwood chair, side on: the hooped back, the round seat, splayed legs. The `saloon_chair` object is one in 3D: the saloon uses that. |
| `spittoon` | good | 0.09 tall | saloon | Brass, squat and bellied, a wide funnel mouth. |
| `pick_shovel` | good | 0.46 tall | gold_mine, mine_ride | A pick and a shovel leaning together, their hickory handles worn pale. |
| `dynamite_crate` | good | 0.2 tall | gold_mine | A crate stencilled DYNAMITE, its lid off, red sticks standing in it with their fuses. |
| `ore_heap` | good | 0.16 tall | gold_mine, mine_ride | Broken ore in a mound, quartz in some lumps, a glint of gold; the `ore_cart` heaps it too. |
| `golden_idol` | good | 0.38 tall | temple_inside | Drawn with the toolkit in temple.py: a squat golden jaguar crouched on a carved pedestal, jade in its eyes and collar. |
| `treasure` | good | 0.1 tall | temple_inside | Gold coins heaped and scattered, a jade mask, a golden cup on its side. |
| `round_shield` | good | 0.32 tall, no shadow | fjord | Drawn with the toolkit in norse.py: boards painted in quarters red and pale, the seams carved, an iron boss, a rawhide rim. A card by default. |
| `joystick` | good | 0.045 tall, no shadow | neon_bar | Drawn with the toolkit in bar.py: a red ball on a black shaft; the `arcade_cabinet` object stands one on its control panel, the one billboard among its panels. |
| `whiskey` | good | 0.085 tall | saloon | Drawn with the toolkit in saloon.py: an amber bottle with a pale label and a cork, a shot glass beside it; the `card_table` object stands one on a table mid-game. |
| `candle` | good | 0.06 tall | saloon | Drawn with the toolkit in saloon.py: a candle in a brass sconce, unlit; the `piano` object stands one at each corner. |
| `candle_lit` | good | 0.06 tall, glows | saloon | The candle burning, its flame glowing; the `piano` object's with `lit`. |

## Characters (33)

Pixel-art grids written as text in `scripts/characters.py`, each with a back view.

| character | status | used in | notes |
|---|---|---|---|
| `cultist` | good | garden_encounter, gui_lantern, gui_menus, neon_street, post_presets, tunnel_encounter, woodland_night |  |
| `scientist` | good | aquarium, bunker_lab, clockwork_city, coast_lighthouse, gui_lantern, night_market, orbital_hangar, tunnel_encounter |  |
| `guard` | good | garden_encounter, gui_menus, post_presets, rain_alley, rainy_street |  |
| `nurse` | good | ghost_corridor, gui_hud |  |
| `spiritualist` | good | cathedral_ruin, chapel_graveyard, gui_themes, gui_trade, library_medium, mansion_library |  |
| `ghost` | good | chapel_graveyard, garden_encounter, ghost_corridor, ghost_town, ghost_train, gui_hud, gui_menus, haunted_house, post_presets, saloon, woodland_night |  |
| `hybrid` | good | gui_lantern, sewer_tunnels, tunnel_encounter |  |
| `soldier` | good | castle_keep, doomed |  |
| `knight` | good | castle_keep, dark_road, market_ride, misty_moor, village_green, village_hours |  |
| `child` | good | aquarium, autumn_lane, market_ride, night_market, palm_house, village_green, village_hours, winter_lake, winter_woods | The head narrowed to ten pixels with a fringe, the eyes closer together, a small mouth and a tapered chin, so it reads as a child rather than a round mask; back view. |
| `creature` | good | castle_keep, crystal_cave |  |
| `robot` | good | clockwork_city, crystal_cave |  |
| `shopkeeper` | good | clockwork_city, ghost_town, market_ride, neon_street, night_market, saloon, village_green, village_hours |  |
| `astronaut` | good | alien_world, moon_base, moon_drive, orbital_hangar, space_station |  |
| `android` | good | neon_bar, neon_street, orbital_hangar, space_station |  |
| `alien` | good | alien_world, derelict_ship | A familiar archetype; could be made stranger. |
| `dreamer` | good | capsule_hotel, dream_chess, dream_world, drowned_library, hall_of_doors, salt_flat, sky_road | Eyes closed now (two soft lines, not dark pupils), so she reads as a sleepwalker; nightgown and candle. |
| `claude` | good | claude_study | Claude's own avatar. |
| `explorer` | good | aquarium, aurora_palace, basalt_coast, glow_jungle, jungle_temple, jungle_trail, red_canyon, rope_bridge, sky_islands, temple_inside |  |
| `hoplite` | good | ancient_ruins |  |
| `castaway` | good | tropical_beach |  |
| `diver` | good | aquarium, kelp_forest, sunken_temple | A brass diving helmet with a round faceplate and an air hose, a canvas suit, a weight belt, heavy boots. |
| `runner` | good | neon_bar, neon_rooftop, neon_street, night_market | A cyberpunk: dark hair with a pink streak, a lit cyan visor, a black jacket striped in neon. |
| `samurai` | good | autumn_garden, night_market | A street samurai: topknot, glowing red visor, a long black coat lined in crimson over a grey shirt and a gold belt, a sword slung across the back with its hilt over the shoulder, one chrome arm; back view. |
| `hacker` | good | capsule_hotel, neon_bar | Hood up in deep violet, cyan goggles glowing in the shadow of it, a deck held in both hands with a green screen, cargo trousers, white sneakers on lit pink soles; back view. |
| `cowboy` | good | ghost_town, high_noon, neon_bar, night_market, red_canyon, saloon | A wide-brimmed hat, moustache, red bandana, a vest over a tan shirt, a gun belt, jeans and boots; for the canyon. |
| `witch` | good | aurora_palace, autumn_lane, enchanted_path, neon_bar | A crooked pointed hat banded in purple, green skin, glowing yellow eyes, a robe, a lit lantern at her side. |
| `farmer` | good | fjord, market_ride, palm_house | A straw hat, plaid shirt and blue overalls, a pitchfork taller than him. |
| `pirate` | good | bayou | A gold-edged tricorn, an eye patch and beard, a red coat with gold buttons, a cutlass. |

### Not yet sorted

| character | status | used in | notes |
|---|---|---|---|
| `miner` | good | gold_mine | A gold-rush prospector: a dusty slouch hat, a grey beard, red flannel under dark suspenders, jeans and boots, a pick on his shoulder. From behind, grey hair under the hat. |
| `viking` | good | fjord | An iron cap, a braided red beard, a fur cloak over a green tunic, a belt with a gold buckle, leg wraps, an axe in hand. From behind, red hair under the cap. |
| `monk` | good | autumn_garden, glass_chapel, market_ride, pilgrim_path | Shaven head, a brown robe with its cowl down on the shoulders, hands folded, a rope belt with a hanging end, sandals. |
| `villager` | good | forest_path, market_ride, village_green, village_hours | A red kerchief over brown hair, a green dress under a white apron, a basket on her arm. From behind, her hair and the dress. |

## Decals (42)

Stamps blended into floors, walls and ceilings. `grime` stamps some of them on its own, and `contact_shadow` goes under every prop that stands on the ground.

| decal | status | used in | notes |
|---|---|---|---|
| `puddle` | good | coast_lighthouse, dark_road, jungle_trail, rainy_street, woodland_night |  |
| `puddle_dark` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, sewer_tunnels, woodland_night |  |
| `puddle_shine` | good | coast_lighthouse, jungle_trail, neon_avenue, neon_street, night_market, rain_alley, rainy_street, sewer_tunnels |  |
| `stain` | good | bunker_lab, canal_tunnel, cathedral_ruin, coast_lighthouse, coast_road, derelict_ship, desert_highway, forest_path, jungle_trail, mountain_pass, neon_avenue, night_highway, sewer_tunnels, woodland_night | A ragged edge, darker along the tide line where it dried, blotchy inside, drops round it and short runs from its foot. |
| `stain_rust` | good | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, orbital_hangar, rainy_street, sewer_tunnels | As stain, in rust. |
| `splatter` | good | doomed |  |
| `splatter_dark` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, sewer_tunnels |  |
| `vines` | good | jungle_temple, overgrown_highway, rainy_street |  |
| `moss_patch` | good | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, enchanted_path, jungle_temple, overgrown_highway, rainy_street, sewer_tunnels, temple_inside, woodland_night | A cushion of rounded clumps lit along their tops and dark under them, speckled, a few stray tufts round it. |
| `crack` | good | bunker_lab, canyon_run, castle_keep, cathedral_ruin, coast_lighthouse, coast_road, dark_road, derelict_ship, desert_highway, mountain_pass, neon_avenue, night_highway, overgrown_highway, rainy_street, sewer_tunnels, sky_road |  |
| `scorch` | good | bunker_lab, cathedral_ruin, derelict_ship, sewer_tunnels, tropical_beach |  |
| `leak` | good | bunker_lab, canal_tunnel, castle_keep, cathedral_ruin, derelict_ship, rainy_street, sewer_tunnels |  |
| `cobweb` | good | bunker_lab, castle_keep, temple_inside |  |
| `rune_mark` | good | enchanted_path |  |
| `drain` | good | bunker_lab, neon_street, night_market, rainy_street, sewer_tunnels |  |
| `contact_shadow` | good | 149 scenes |  |
| `pad_marking` | good | moon_base, orbital_hangar | A painted landing ring with an H and a dashed outer ring, worn in patches. |
| `rover_tracks` | good | moon_base, moon_drive, red_planet | Drawn with the toolkit in moon.py: two tracks of chevron treads pressed into dust. |
| `hazard_stripe` | good | orbital_hangar | A band of yellow and black diagonal stripes, worn through in places. |
| `toxic_sign` | good | doomed | Drawn in doomed.py: a yellow triangle edged in black with a skull, TOXIC on a plate below. |

### Shore and pool

| decal | status | used in | notes |
|---|---|---|---|
| `foam` | good | tropical_beach | Edge-on from eye height: pair it with the surf props. |
| `foam_glow` | good | tropical_beach | As foam. |
| `starfish` | good | kelp_forest, tropical_beach |  |
| `shells` | good | kelp_forest, tropical_beach |  |
| `seaweed` | good | kelp_forest, tropical_beach |  |
| `lily_pads` | good | autumn_garden, bayou, jungle_temple |  |

### Roads

Marks lying on a road scene's road and verges (`decals`, highway.py).

| decal | status | used in | notes |
|---|---|---|---|
| `oil_stain` | good | coast_road, desert_highway, mountain_pass, neon_avenue, night_highway | A dark blotch soaked into the road, a faint blue sheen at its rim. |
| `tyre_marks` | good | canyon_run, coast_road, grand_prix, night_highway, sled_run | Two skid marks wavering down the road, heaviest in the middle; four times as long as wide. |
| `road_patch` | good | coast_road, dark_road, desert_highway, mountain_pass, neon_avenue, night_highway | A square of newer asphalt, its seams tarred. |
| `pothole` | good | dark_road, overgrown_highway | The road broken through, a crumbled rim, cracks running out. |
| `leaf_litter` | good | autumn_lane_road, forest_path | Leaves in autumn colours lying thick in the middle. |
| `manhole` | good | neon_avenue, night_highway | A cast-iron cover, a ring round it, a raised grid. |
| `lane_arrow` | good | - | A worn white arrow painted on a lane, pointing on. |
| `zebra_crossing` | good | neon_avenue, night_runway | White bars across the road, worn where the wheels run. |
| `sand_drift` | good | canyon_run, coast_road, desert_highway, ice_road, winter_road | Pale sand blown over the road, ripples, stray grains (tinted white, snow). |
| `pebbles` | good | autumn_lane_road, canyon_run, desert_highway, forest_path, jungle_trail | Gravel spilled on a path, each stone lit and shadowed. |
| `start_line` | good | grand_prix | A chequered band across a race track. |
| `wake` | good | island_run | A boat's wake: a V of foam spreading behind it, churned water down its middle. |
| `crater` | good | moon_drive | A crater in the Moon's dust: a bowl with its sunward wall lit and the other in shadow, a raised rim, a paler blanket of ejecta fading out round it. A few units across beside a road. |

### Not yet sorted

| decal | status | used in | notes |
|---|---|---|---|
| `wanted_poster` | good | saloon | Yellowed paper with a torn corner: WANTED over a sketched face in a hat, $500. |
| `glass_shards` | good | window_garden | Jagged shards of a window on a floor, pale, a glint at each one's sharpest corner. |
| `sigil` | good | canal_tunnel | Painted in red on a wall: a circle, a triangle in it, a line down through both, the paint run in drips. Not the glowing `rune_mark`. |

## Skies (14)

| sky | status | used in | notes |
|---|---|---|---|
| `night` | good | 44 scenes |  |
| `dusk` | good | autumn_garden, autumn_lane, bayou_run, coast_lighthouse, launch_day, misty_moor, night_runway, rain_motorway |  |
| `storm` | good | coast_lighthouse, kelp_run, rain_alley, rainy_street, storm_chase, storm_coast, storm_island | Could use darker cloud masses. |
| `day` | good | 39 scenes |  |
| `overcast` | good | doomed, winter_woods |  |
| `blood` | good | dark_road, volcano_road |  |
| `space` | good | moon_base, moon_drive, orbital_hangar, ring_station, space_station, space_trench |  |
| `alien` | good | alien_world |  |
| `dream` | good | candy_road, dream_chess, dream_world, drowned_library, hall_of_doors, rope_bridge, salt_flat, sky_road |  |
| `sunset` | good | basalt_coast, bayou, camel_caravan, clockwork_city, coast_road, dragon_flight, drowned_city, fjord, ghost_town, gold_mine, hayride, red_canyon, safari_drive, salt_flat, tropical_beach |  |
| `golden` | good | ancient_ruins, autumn_garden, autumn_lane, autumn_lane_road, bayou, high_seas, kaiju_harbor, mesa_desert, overgrown_highway, red_planet, sky_islands, strait_bridge, viaduct_train, woodland_night |  |
| `dawn` | good | airship_voyage, balloon_flight, blossom_road, canal_boat, forest_path, giant_valley, suspension_bridge | New: just after sunrise - night going off the top of the sky, rose through the middle, peach at the horizon, clouds lit pink; `"time": "dawn"` picks it. |
| `vector` | good | synthwave_drive, vector_world | Black to violet with a magenta glow at the horizon and a few stars; pair it with a striped sun. |
| `aurora` | good | aurora_palace, ice_road, sled_run, winter_valley | A clear arctic night with the aurora across it, no two stretches alike: a curtain of green rays of every width and height fringed pink, a pleated teal ribbon, red-tipped rays to the west, a faint high arc; brightest due north; they glow. |

## Skylines (6)

| skyline | status | used in | notes |
|---|---|---|---|
| `mountains` | good | alien_world, balloon_flight, dragon_flight, fjord, giant_valley, high_noon, ice_road, jungle_temple, lantern_river, mesa_desert, mountain_pass, pilgrim_path, red_planet, salt_flat, ski_run, synthwave_drive, viaduct_train, winter_lake, winter_road |  |
| `hills` | good | camel_caravan, candy_road, desert_motel, grand_prix, kaiju_country, misty_moor, roller_coaster, safari_drive, strait_bridge |  |
| `treeline` | good | chapel_graveyard, forest_path |  |
| `city` | good | kaiju_harbor, neon_avenue, neon_canal, neon_race, neon_rooftop, neon_street, night_highway, night_market, night_runway, overgrown_highway, rain_motorway, sky_lane, suspension_bridge | Window grid is regular; vary building tops (spires, water towers). |
| `islands` | good | ancient_ruins, archipelago, basalt_coast, coast_road, high_seas, island_run, tropical_beach | Flat-topped and lopsided with a low strip of beach either side, so an island and its reflection read as land on the water, not a saucer. |
| `jungle` | good | jungle_river, jungle_temple, jungle_trail |  |

## Sky objects (7)

| object | status | used in | notes |
|---|---|---|---|
| `planet` | good | - |  |
| `ringed` | good | alien_world, orbital_hangar, ring_station, space_station, space_trench |  |
| `moon` | good | alien_world, desert_motel, dream_chess, dream_world, drowned_library, enchanted_path, lantern_river, night_canal, orbital_hangar, red_planet, sleigh_ride, space_station, winter_road |  |
| `earth` | good | moon_base, moon_drive | Oceans, green and desert continents and cloud from noise mapped onto the sphere, polar ice, a blue limb; the night side dark. |
| `sun` | good | airship_voyage, balloon_flight, camel_caravan, dragon_flight, drowned_city, orbital_hangar, ring_station, safari_drive, space_station |  |
| `eye` | good | dream_world |  |
| `clock` | good | dream_chess | A cream face in a dark rim, twelve ticks, two hands set by `time`, its bottom running like wax (`melt`). |

## Scatter sets (22)

Named mixes for `scatter`; repeats in the contents act as weights.

| set | status | contents | used in | notes |
|---|---|---|---|---|
| `stones` | good | rocks x3, boulder | chapel_graveyard |  |
| `snow` | good | rocks x3, boulder_snow | ski_run, sled_run, winter_lake, winter_woods | The stones set for winter: its boulder is under snow, not moss. |
| `rubble` | good | rubble x2, rocks, broken_barrel | cathedral_ruin, rainy_street |  |
| `forest` | good | rocks x2, log, stump, mushrooms, grass_tuft x2, fern, bush | forest_path, woodland_night |  |
| `undergrowth` | good | grass_tuft x3, fern, bush, mushrooms | cathedral_ruin, chapel_graveyard, overgrown_highway, redwood_road, woodland_night |  |
| `autumn` | good | grass_tuft x2, fern, bush_autumn x2, mushrooms | autumn_garden, autumn_lane | The undergrowth set for the fall: its bush turned. |
| `shore` | good | rocks x3, boulder, reeds, bones | - |  |
| `litter` | good | sack, bucket, crate, barrel, broken_barrel, bones | neon_street, rain_alley |  |
| `wreckage` | good | rubble x2, broken_barrel, rocks, bones, sack, bucket | bunker_lab, cathedral_ruin, derelict_ship, sewer_tunnels |  |
| `cave` | good | rocks x3, stalagmite, glowshroom, crystal, bones | crystal_cave |  |
| `alien` | good | rocks x2, crystal, glowshroom, alien_plant, alien_egg | alien_world |  |
| `derelict` | good | rubble x2, sci_crate, bones, rocks, alien_egg | derelict_ship |  |
| `jungle` | good | fern x3, monstera, bromeliad x2, heliconia, mushrooms | jungle_temple, jungle_trail |  |
| `beach` | good | coconuts, driftwood, rocks x2, crab, dry_tuft | coast_road, island_run, tropical_beach |  |
| `ruins` | good | column_drum, rubble, rocks x2, poppies, dry_tuft x2, amphora | ancient_ruins |  |
| `desert` | good | rocks x3, prickly_pear, tumbleweed, cow_skull, dry_tuft | canyon_run, desert_highway, ghost_town, gold_mine, red_canyon | Rocks with the odd prickly pear, tumbleweed, skull and dry tuft. |
| `swamp` | good | cattails x2, reeds, cypress_knees, rocks | bayou_run | Cattails and reeds with cypress knees and the odd rock. |
| `seabed` | good | rocks x3, crab, boulder | kelp_forest, kelp_run, sunken_temple | Rocks with the odd crab and boulder. |

### Not yet sorted

| set | status | contents | used in | notes |
|---|---|---|---|---|
| `verge` | good | grass_tuft x3, dry_tuft, flowers, rocks, bush | - | A country road's verge: tufts, dry tufts, flowers, a stone, a bush. |
| `alpine` | good | rocks x3, boulder, grass_tuft x2, flowers | mountain_pass | Stones and boulders in thin grass, a few flowers: a mountain road's verge. |
| `street` | good | trash_bag x2, trash x2, old_tyre, traffic_cone | night_highway | Rubbish bags, litter, an old tyre, a cone: a city kerb. |
| `overgrown` | good | grass_tuft x3, dry_tuft x2, fern, flowers | overgrown_highway | Weeds up through a road's cracks: tufts, dry tufts, a fern, flowers - scattered on the road itself (`side` road). With a bush in it the road vanished under them. |

## Fringe sets (7)

The cards a `fringe` wall stands in front of its open faces, back to front.

| set | status | cards | used in | notes |
|---|---|---|---|---|
| `jungle` | good | jungle_card_4, jungle_card_3, jungle_card_2, jungle_card_1 | jungle_temple, tropical_beach | Four cards: bushes alone at the front, a dense wall of trees, crowns and bushes at the back. |
| `forest` | good | forest_card_4, forest_card_3, forest_card_2, forest_card_1 | haunted_house, window_garden, woodland_night | Four cards: bushes, ferns and grass at the front, a dense wall of spruce and oak at the back. Keep the wall behind lower (2-2.6) than the trees. |
| `forest_autumn` | good | autumn_card_4, autumn_card_3, autumn_card_2, autumn_card_1 | autumn_garden, autumn_lane | The forest fringe in October: oak, birch and bush turned, the spruce among them still green. |
| `forest_snow` | good | winter_card_4, winter_card_3, winter_card_2, winter_card_1 | winter_woods | The forest fringe in winter: snowy spruce, bare oak and birch with snow on their limbs, bushes under snow. |
| `swamp` | good | swamp_card_4, swamp_card_3, swamp_card_2, swamp_card_1 | bayou | Four cards: cattails and knees, then young cypresses, then a looser stand, then a dense one. The bayou spreads them three cells deep with `wander`. |
| `kelp` | good | kelp_card_2, kelp_card_1 | kelp_forest, sunken_temple | Two cards: a few stalks, then a dense stand. |
| `glow_jungle` | good | glow_jungle_card_4, glow_jungle_card_3, glow_jungle_card_2, glow_jungle_card_1 | glow_jungle | Four cards: the jungle fringe at night, faintly edged and specked with light. |

## Facade styles (6)

The looks a `facade` can give its buildings (`scripts/buildings.py`); each building is drawn in layers - wall, frames and glass, drapes, rooms.

| style | status | used in | notes |
|---|---|---|---|
| `brick` | good | rain_alley | Red and brown brick, painted sash windows, curtains and blinds, shops. |
| `sooty` | good | rain_alley | Soot-blackened tenements, dark frames. |
| `plaster` | good | - | Washed plaster; fine on the review sheet, though no example uses it yet. |
| `neon` | good | neon_rooftop, neon_street, night_market | Concrete panels with form-tie holes, neon signs over the shops and up the walls, blade signs on their own cards, roller shutters, air conditioners, rooms lit pink, blue and green. |
| `timber` | good | village_green, village_hours | Timber framing over limewash and ochre - posts at the bays and jambs, rails at the floors, sills and heads, braces or close studding - leaded casements, plank doors, and a roof layer: a gable end, or thatch or tiles set back behind the eave, chimneys. Other styles unchanged. |
| `western` | good | ghost_town | Clapboard in faded paint peeling to grey, false fronts (flat, stepped, curved, pediment) with painted signs from the pixel font, never repeated along a street, a saloon with batwing doors and a lit room, porch posts and fascia for a roofed boardwalk. |

## Prefabs (13)

Named groups placed with one line (`scripts/prefabs.py`).

| prefab | status | parts | used in | notes |
|---|---|---|---|---|
| `campsite` | good | 7 sprites, 1 lights, 1 decals | tropical_beach |  |
| `palm_grove` | good | 6 sprites | tropical_beach |  |
| `palm_3d` | good | 2 sprites | tropical_beach | A billboard trunk under a star of crown planes: the mixed kind. |
| `jungle_clump` | good | 6 sprites | jungle_temple |  |
| `jungle_bush` | good | 3 sprites | - | Planes and billboards mixed in one plant. |
| `fern_bed` | good | 6 sprites | jungle_temple |  |
| `ruined_columns` | good | 6 sprites, 2 objects | ancient_ruins |  |
| `altar_fire` | good | 1 sprites, 1 lights, a map | - | Brings its own block of map. |
| `beach_hut` | good | 2 sprites, 2 lights, a map | tropical_beach | A patch of map with its own legend: walls, door, window, roof, light. |
| `tiki_torches` | good | 2 sprites, 1 lights | tropical_beach |  |
| `street_lamp` | good | 1 sprites, 1 lights, 1 decals | rain_alley |  |
| `graves` | good | 5 sprites | - |  |
| `shrine` | good | 2 sprites, 1 lights | jungle_temple |  |

## Objects (43)

Things too big for a billboard, built in 3D out of flat panels (`scripts/objects.py`).

| object | status | used in | notes |
|---|---|---|---|
| `car` | good | rain_alley | A saloon from panels, laid out as the user drew it: the overall box with the car's outline on its sides, hood and trunk lid across it at the belt (body 60%, glass 40%), the roof, glass windows with seats, dashboard and steering wheel inside, four wheels set in under the body in dark wells, a floor pan and a soft shadow; `paint`, `lights`. Proportions and handles tuned with the user. |
| `noodle_stand` | good | neon_street | Counter, awning, valance, noren and sign as panels; bowls, pot, tray, lanterns and stools as billboards, with its own lamp and lantern lights. |
| `rock_wall` | good | aquarium, basalt_coast, crystal_cave, fjord, ghost_town, gold_mine, neon_bar, red_canyon | Laid out as the user drew it: overlapping pieces along a wall's foot, each in plan a rounded mass of a few broad faces jutting from the wall (the user's sharper zigzag read as spikes; a few spikes and notches are left), each its own height, a trim of faces along its top cut by one long smooth wavy edge, a flat top (inset a texel, so it never shows past the faces), plants on the rim. Kinds `stone`, `reef`, `sandstone`, `snow`, `cave`, `lumen` (glowing moss); `lining` lines every wall face of some map cells. The faces cut from one solid block of stone. Seen from above its tops are flat with the trim standing round them, as Build's were. |
| `boulder` | good | aquarium, autumn_garden, autumn_lane, coast_lighthouse, crystal_cave, kelp_forest, misty_moor, neon_bar, red_canyon, storm_island, sunken_temple, winter_lake, winter_woods, woodland_night | A low-poly mass, every face a triangle: an irregular foot, a belly, drawn-in shoulders, a peak off its centre; closed from every side. Plants on top by count. |
| `column` | good | ancient_ruins, autumn_garden, basalt_coast, canal_tunnel, castle_keep, cathedral_ruin, gold_mine, hall_of_doors, palm_house, sky_islands, storm_island, sunken_temple, temple_inside, tropical_beach | A column or a post: a prism of `sides` faces (an octagon by default), tapering if `top` is under 1, a plinth (`base`) and a capital if asked; stone cut from the solid rock as rock is, or `wood` - weathered timber, the grain running up it, dark and grown over below `wet` where it stands in water. Built for the pier's piles first; the cathedral's piers are `ashlar` (dressed stone in drums) with plinths and capitals, one `broken` off ragged. The ruins' columns are Greek: `flutes` (20 faces, each hollowed, so it takes the light on one side and shadow on the other) and `doric` (an echinus widening under a square abacus), in `marble` laid in drums; `fill` lifts a backlit column's dark side. |
| `beam` | good | ancient_ruins, autumn_garden, canal_tunnel, castle_keep, cathedral_ruin, drowned_library, gold_mine, hall_of_doors, palm_house, sky_islands, storm_island, sunken_temple, temple_inside | A squared timber or stone lintel lying level, `length` along the way it faces, its underside at the placement's `z`; timber's grain runs along it. Wall plates on the cathedral's piers, and one fallen on the floor; the architraves and cornices over the ruins' columns. |
| `crystal_cluster` | good | alien_world, aurora_palace, crystal_cave | The user's idea: crystals whose facets refract. Hexagonal prisms with pointed tips from a bed of rock, every facet a panel with its own clarity (clear across the middle, milky toward the base, bright edges) and its own bend: drawn with the glass, each facet shows the frame drawn so far shifted by one offset from the way it is turned (Renderer._bend), so it shows one coherent piece of what is behind, the colours parting a little at the edges. Strongest with glowing things behind. |

### Not yet sorted

| object | status | used in | notes |
|---|---|---|---|
| `trough` | good | ghost_town | A horse trough of weathered boards (`_wood` with `boards`: a seam between each, each its own tone), a rim, still water a hand below it, a soft shadow. Replaces the `water_trough` billboard in the ghost town. |
| `shed_roof` | good | - | A roof of boards sloping down to its front edge, the boards running down the slope. The western facade builds one over every porch (ghost_town), sloping from the front down to the fascia so it shows from the street. |
| `gable_roof` | good | autumn_garden, chapel_graveyard, fjord, haunted_house, palm_house, storm_island, winter_lake | A gabled roof of boards with gable ends of upright boards, `walls` under it (`inset` back from its front). The western facade builds one behind every false front (ghost_town): the building's body, low enough for the front to hide. |
| `market_stand` | good | village_green, village_hours | The market stall in 3D, as the noodle stand: a trestle table of weathered boards with a striped skirt (the awning's valance, in step), four poles, a striped awning sloping down to the front with a scalloped valance round it; on the table three trays heaped with `goods` in 3D (produce painted as rock is, each apple, cabbage, loaf or potato a round lump of its own, `PRODUCE`), a full `crate` and a shut one by it, a sack (a billboard); `paint` stripes its awning. Replaces the `market_stall` billboard in the village, where a second, blue, stands across the street. |
| `saloon_bar` | good | saloon | A saloon's counter in 3D, 0.38 tall: raised mahogany panels between pilasters, a polished top overhanging the drinkers' side, the bartender's shelves behind, a brass foot rail on brackets, bottles on it. |
| `rails` | good | gold_mine | A narrow track: two iron rails on wooden sleepers every 0.22, their tops worn bright. |
| `ore_cart` | good | gold_mine | A riveted iron tub gone to rust (`_iron_side`: rivets along its lip and foot, rust running down) on a low frame and four small wheels set to the rails, ore heaped in it. |
| `keel` | good | dream_world, sky_islands | The rock under a floating island in 3D: an irregular ring at the foot of the cliff drawing in by uneven steps - each corner its own reach - to a point off its centre, crags hanging from its flanks; `island` rock (grey and brown in beds) painted at half a wall's texels, lit from above so its underside is in shade. Replaces the `island_keel` billboards. |
| `chess_piece` | good | dream_chess, dream_world | A chess piece in 3D, turned (`_lathe`: each pair of profile points a frustum of 16 faces, smoothly shaded round with a convex `tilt`) in polished marble (`_polished`: lit by the way each texel faces, a sheen toward the light, veins), white or black; the rook's battlements, the queen's coronet and ball, the king's crown and cross; the knight's head carved side on from a slab, its eyes nicked in. Replaces the billboards in dream_chess. |
| `ship_hull` | good | canal_tunnel, kelp_forest | A wooden ship's hull in 3D, open: a square stern, the sides curving out from the keel and in to a pointed bow whose stem sweeps up, the gunwale rising toward both ends; planked along its length (`_timber` boards), ribs inside; `heel` lists it, `broken` staves in its starboard side. The kelp forest's wreck. |
| `longship` | good | fjord | A longship: the `ship_hull`'s planked hull, stem and stern posts curling up and over, a six-sided mast, a yard and a square sail in red and cream stripes (bellied lighter in the middle; `"sail": false` furls it), round shields at the gunwale down both sides. |
| `lighthouse` | good | coast_lighthouse, storm_island, strait_bridge | A round tower of whitewashed masonry tapering up, smoothly shaded (`lime_white`, `_painted`), a red band (`lime_red`), a gallery on corbels with an iron rail of posts, a lantern room of ten glass panes (the `glass` cover's painter, translucent) with the lamp lit in it (an `orb` and a light), a domed iron cap with a ball. |
| `stone_lantern` | good | autumn_garden | A garden's stone lantern: a hexagonal foot, a round shaft (smooth), a platform, a firebox of four posts with a flame showing between them and a little light, a wide six-sided roof, a finial. |
| `standing_stone` | good | misty_moor | A standing stone: a rough slab of `menhir` rock set on end (`size`, `depth`, `height`), its broad faces nearly flat, swelling and drawing in as it rises, leaning a few degrees, its top sloping down from one shoulder with the corners knocked off; low and wide, an altar slab. |
| `gear` | good | clockwork_city | A gear: a toothed wheel of `brass` (`size`, `depth`, `teeth`, `spokes`), its faces cut to the teeth, rim, spokes and boss, each a shade of its own, the sides of its teeth standing out; verdigris in patches. |
| `heap` | good | salt_flat | A heap of something loose: an irregular cone of `salt` (or any rock) `size` across and `height` tall, lumpy, its top a blunt point a little off centre; salt raked up to dry on a salt flat. |
| `arcade_cabinet` | good | neon_bar | An upright cabinet in 3D: its sides cut to the outline (marquee jutting over a screen tilted back, the control panel standing out), side art of a ringed planet, stars and bands in its `color`, the T-moulding lit round its edge; a backlit marquee in pseudo-letters, a game glowing on the screen - a shooter, a maze chase or a racer, by `seed` - buttons on the controls and a `joystick` billboard standing up from them, a coin door with its inserts lit. The neon bar's row of four, each its own colour and game. |
| `vending_machine` | good | capsule_hotel, neon_street | A drinks machine in 3D, a steel box in its `paint`: its window let into the front (a recess, lit) on three shelves of cans and bottles with a glowing button under each behind clear plastic, a lit sign, a money panel (a red price display, coin and note slots, the coin return), the hatch let in under a smoked flap, a white wave carried on round the corners, a maker's ring on the sides. |
| `well` | good | village_green, village_hours | A village well in 3D: a round wall of `fieldstone` (new rock: small stones laid dry, every joint showing, each its own shade), a coping of flat stones proud of it, the dark water far down the shaft; two oak posts carrying a little gabled roof, the windlass between them with its rope wound round and hanging down, an iron crank; a bucket on the rim. |
| `crate` | good | village_green, village_hours | A wooden crate in 3D: planks behind a frame of battens, a brace across each side, nails; `goods` heaps it full of produce and leaves it open, else it is nailed shut. |
| `barrel` | good | village_green, village_hours | A barrel in 3D: twelve oak staves bulging at the middle, each its own tone with a seam down its edges, shaded round smoothly, four iron hoops, its lid of boards sunk inside the rim (`_staves`). |
| `card_table` | good | saloon | A round card table in 3D: green baize in a rim of polished mahogany, a turned pedestal on a round foot; mid-game (`game`) a hand dealt at each of four places, one fanned face up, the pot spilled in the middle, chips standing in stacks (tiny prisms), a `whiskey` bottle and glass. |
| `saloon_chair` | good | saloon | A bentwood chair in 3D: a round seat with a rounded edge, four legs splayed out (bars between two points, `_strut`) with a ring round them, the back a cut-out panel - two posts bent over in a hoop, a smaller hoop inside - leaning back. |
| `piano` | good | saloon | An upright piano in 3D, polished mahogany: its sides cut to its outline with the arms that hold the keyboard, carved; the keys from above (white keys, the black in their twos and threes), a gilt maker's name, carved panels, the music open on the desk, `candle`s in sconces at its corners (`lit` burns them, the night shot's does), a long panel with two brass pedals, turned legs. |
| `portal` | good | hall_of_doors, salt_flat | An opening onto another place - another scene file, or another part of this one: before the frame, the renderer draws the view from where the camera would stand beyond its exit (`to`), at the frame's own size and lens, and the opening shows that through this scene's air (Renderer._portal_views, _through), so it lines up from any shot; `view` a fixed camera instead. A frame (wood, stone, marble, gold), a door swung open, a rim of light. The salt flat's door onto the winter woods; the hall of doors' three. |
| `screen` | good | neon_bar | A picture of another shot, of another scene file or of this one, rendered once with its own effects and palette and laid on the screen keeping its pixels (render.screen_texture), lit: on a `tv` (a boxy set on legs, rabbit ears), a `monitor`, a flat screen on a `wall`, or bare; `crt` scanlines. Snow with nothing to show, or within another screen. The neon bar's screen over the bar; an arcade cabinet's `show` lays one on its screen. |
| `sign` | good | neon_bar | Lettering on a board in 3D (scripts/lettering.py): any text, a newline for a second line, in a style - painted (wood grain, a painted line inside the edge, flaking), neon (tubes and a halo, glowing, with its light), plaque (brass, engraved, screws), carved (cut in stone), chalk (a blackboard), gilt (gold leaf), poster (ink on paper); as tall as asked, as wide as its words; reads from both sides. The neon bar's name on its wall. |
| `pew` | good | glass_chapel | A chapel's pew in 3D, oak: built on its side's profile - the back leaning a little back with a pale cap along its top, the seat, boarded down to the floor behind it - and a carved end board at each end, scrolled over at the top, a panel sunk in it, a roundel above; each face's boards their own tone. |
| `tower` | good | storm_island | A building at landscape scale: a box - two with a `setback` - whose faces are floors of two texels, a row of windows over a band of wall, in five styles (office, glass, apartment, brick, dark); a lobby of dark glass, a parapet catching the light; `lit` windows lit in runs, warm or cool; a flat roof with its plant on it, or a helicopter pad; a mast. Used through `city_block`. |
| `city_block` | good | kaiju_country, kaiju_harbor, strait_bridge, volcano_island | A city block's buildings: `count` plots a side inside the pavements, each built (`built`) to a `tower` of a height drawn toward the low end of `height`, in a style from `style`; the tall ones step back and carry masts and pads. kaiju_harbor's whole city is city blocks, tall downtown and low toward its edges. |
| `searchlight` | good | kaiju_harbor, storm_island | A searchlight's beam: two additive panels crossed along it, brightest along its middle and fading to its edges and along its length, opening six times as wide - in a thin fog with a bloom it reads as a beam from any side. |
| `ray` | good | kaiju_harbor | A ray from a point to a point (`to`), drawn as the searchlight's beam is, twice as wide where it lands: the kaiju's breath striking a tower, the helicopters' lamps on the monster. |
| `mountain` | good | archipelago, giant_valley, kaiju_country, mesa_desert, storm_island, strait_bridge, volcano_island, winter_valley | A mountain of triangles of solid rock - the new `alpine` kind: grey bands, meadow where it lies gently, snow above a wandering `snowline` and over everything near the summit. Rings of points from a broad foot steepen up its flanks, then round over into a broken crown about an off-centre summit (a cone's point was too sharp); spurs (`ridges`) bulge out with gullies between, one flank steeper than the other; `length` draws it out into a ridge; `top` cuts it flat for a mesa; a `crater` sinks one into its top and `lava` runs down its flanks, painted texel by texel as bands that wander as they fall and widen below (rock kinds `volcanic` and `lava`); a `cliff` stands it on a slope of talus with walls all but sheer to a flat top - a butte, a spire. |
| `village` | good | archipelago, giant_valley, kaiju_country, mesa_desert, storm_island, winter_valley | Cottages - plaster or stone walls with small windows, roofs of tile, slate or thatch, a chimney - along a winding street, a few farms off by themselves, and a church with a square tower and a spire near the middle. `lit` puts lamps in its windows, `snow` lays its roofs under snow (winter_valley). |
| `cable` | good | canal_tunnel, kaiju_country | A cable slung between two points with a sag at its middle: two dark strips crossed along it, in segments, so it shows from any side. Power lines from pylon to pylon in kaiju_country. |
| `bridge` | good | giant_valley, strait_bridge | A bridge at landscape scale. `suspension`: a steel deck with its road on top (lane lines), a truss under it, two towers of braced legs in `paint`, main cables slung from anchorages over the towers sagging nearly to the road, hangers down to it (strips, as a `cable`), lamps and red tower lights when `lit` (the hour turns them off by day). `stone`: the road on round arches - each side one panel with the arches cut out of it, a darker ring of voussoirs round each - and its parapet. The strait's bridge, and giant_valley's old bridge by the village. |

## Held items (8)

| item | status | used in | notes |
|---|---|---|---|
| `revolver` | good | gui_hud, rainy_street | Modelled in 3D in held.py (sculpt.py) and seen from the player's eye: the hand from the holder's side (the back of the hand, the thumb, the top of the index finger), the sleeve running off the screen. |
| `lantern` | good | gui_lantern, woodland_night | Modelled in 3D in held.py (sculpt.py) and seen from the player's eye: hanging by its bail from a fist built bone by bone - the back of the hand on top and held up, the fingers curled under the handle - the forearm reaching in from the left in its sleeve. |
| `flashlight` | good | bunker_lab, derelict_ship, sewer_tunnels | Modelled in 3D in held.py (sculpt.py) and seen from the player's eye, posed from a reference photo: a fist built bone by bone round the barrel - the back of the hand up and out, the thumb across the top, the fingertips curled round under it - the sleeve running off the screen. |
| `axe` | good | - | Modelled in 3D in held.py (sculpt.py) and seen from the player's eye, posed from a reference photo: held like a hammer in a fist built bone by bone - the thumb across the near side of the haft, the back of the hand outward, the wrist straight below, only the fingertips showing - the blade turned in the hand to point away from the eye; the sleeve running off the screen. |
| `crowbar` | good | - | Modelled in 3D in held.py (sculpt.py) and seen from the player's eye, posed from a reference photo: held like a hammer in a fist built bone by bone - the thumb across the near side of the bar, the back of the hand outward, the wrist straight below, only the fingertips showing - the claw turned in the hand to hook away from the eye; the sleeve running off the screen. |
| `torch` | good | - | Modelled in 3D in held.py (sculpt.py) and seen from the player's eye, posed from reference photos: held like a hammer in the left fist, closed tight round a slim haft - the thumb across the near side, the back of the hand outward, the wrist straight below, only the fingertips showing - the sleeve running off the screen. |
| `pistol` | good | doomed | Drawn in doomed.py: held out in the middle of the view: a fist round the grip, the slide from behind with its sights; `fire` adds a muzzle flash. |
| `shotgun` | good | doomed | Drawn in doomed.py: a pump shotgun in the middle: the receiver, the barrel running away to its bead, a hand on the wooden pump; `fire` adds a flash. |

## Icons (26)

| icon | status | used in | notes |
|---|---|---|---|
| `revolver` | good | bunker_lab, gui_hud, gui_trade |  |
| `bolt_cutters` | good | gui_hud, gui_trade |  |
| `screwdriver` | good | - |  |
| `crowbar` | good | gui_hud, gui_trade |  |
| `wrench` | good | bunker_lab |  |
| `lockpick` | good | - |  |
| `hammer` | good | - |  |
| `axe` | good | - |  |
| `key` | good | bunker_lab |  |
| `iron_key` | good | gui_trade |  |
| `note` | good | gui_trade |  |
| `idol` | good | gui_trade |  |
| `amulet` | good | - |  |
| `tonic` | good | gui_hud, gui_trade |  |
| `ammo` | good | bunker_lab, gui_hud |  |
| `dispel` | good | gui_hud, gui_trade |  |
| `lantern` | good | gui_hud, gui_trade |  |
| `flashlight` | good | bunker_lab |  |
| `fuel` | good | - |  |
| `boards` | good | - |  |
| `book` | good | - |  |
| `map` | good | gui_trade |  |
| `gear` | good | - |  |
| `skull` | good | - |  |
| `pointer` | good | - |  |
| `hand_pointer` | good | gui_menus |  |

## GUI themes (6)

| theme | status | used in | notes |
|---|---|---|---|
| `classic` | good | 65 scenes |  |
| `parchment` | good | gui_themes, gui_trade |  |
| `terminal` | good | bunker_lab, gui_themes, orbital_hangar, space_station |  |
| `blood` | good | gui_themes |  |
| `steel` | good | gui_themes |  |
| `doomed` | good | doomed | Stone grey panels, red text, yellow accents, a bevel - to match the status bar. |

## GUI widgets (18)

| widget | status | used in | notes |
|---|---|---|---|
| `bubble` | good | 24 scenes |  |
| `dialog` | good | bunker_lab, chapel_graveyard, claude_study, coast_lighthouse, ghost_corridor, library_medium, neon_bar, orbital_hangar, space_station |  |
| `caption` | good | 56 scenes |  |
| `choice` | good | gui_menus, gui_themes, gui_trade |  |
| `title` | good | gui_menus |  |
| `panel` | good | bunker_lab, gui_lantern |  |
| `toast` | good | gui_hud |  |
| `prompt` | good | bunker_lab, castle_keep, gui_lantern |  |
| `bars` | good | bunker_lab, gui_hud |  |
| `counter` | good | bunker_lab, coast_road, gui_hud, neon_race |  |
| `hotbar` | good | bunker_lab, gui_hud |  |
| `inventory` | good | gui_trade |  |
| `crosshair` | good | bunker_lab, gui_hud, rainy_street |  |
| `compass` | good | gui_hud |  |
| `automap` | good | bunker_lab, gui_hud |  |
| `statusbar` | good | doomed | The stone status bar of a 1993 shooter: big red gradient numbers, labels, the arms grid, a face that bloodies as health falls (grin, ouch, dead), keys, the ammo table. |
| `message` | good | doomed | A plain message at the top left, no box. |
| `image` | good | - |  |

## Post presets (20)

| preset | status | used in | notes |
|---|---|---|---|
| `crt` | good | post_presets |  |
| `crt_amber` | good | - |  |
| `crt_green` | good | bunker_lab, gui_themes |  |
| `vhs` | good | derelict_ship, post_presets |  |
| `gameboy` | good | post_presets |  |
| `cga` | good | - |  |
| `ega` | good | post_presets |  |
| `nightvision` | good | post_presets |  |
| `cinematic` | good | gui_menus, post_presets |  |
| `horror` | good | derelict_ship, post_presets, woodland_night |  |
| `old_photo` | good | coast_lighthouse, post_presets |  |
| `dream` | good | post_presets | A gentle bloom: pastel skies blow out under anything stronger. |
| `bloodmoon` | good | post_presets |  |
| `storm` | good | coast_lighthouse, post_presets, rain_alley, rainy_street |  |
| `blizzard` | good | winter_lake |  |
| `downpour` | good | - |  |
| `autumn` | good | - |  |
| `sandstorm` | good | - |  |
| `ashfall` | good | dark_road, volcano_road |  |
| `hurt` | good | bunker_lab |  |

## Palettes (9)

| palette | status | used in | notes |
|---|---|---|---|
| `gameboy` | good | post_presets |  |
| `cga` | good | - |  |
| `cga_warm` | good | - |  |
| `ega` | good | post_presets |  |
| `amber` | good | - |  |
| `phosphor` | good | bunker_lab, gui_themes, post_presets |  |
| `sepia` | good | coast_lighthouse, post_presets |  |
| `mono` | good | - |  |
| `bone` | good | - |  |

## Example scenes (152)

The environments, judged on their gallery images and shots.

### Horror and mystery

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `garden_encounter` | good | 2 | garden_01, garden_02, layout_map | The cobble path repeats a little in the wide shot. |
| `ghost_corridor` | good | 3 | corridor_03 |  |
| `hospital_corridor` | good | 3 | - | An empty corridor; the second shot is very dark. |
| `hospital_garden` | good | 3 | hospital_garden_01 |  |
| `library_medium` | good | 1 | library_medium |  |
| `mansion_library` | good | 2 | - | Taller, under a panelled ceiling (the beams radiated as stripes), shelves two storeys high, furnished: a desk and reader, armchair, globe, telescope, clock, candelabras, books flying. |
| `haunted_house` | good | 4 | haunted_front, haunted_hall, haunted_parlour, haunted_ghost | Halloween at the old house: the front with jack-o'-lanterns and bats, the hall's grand stair and landing, the parlour, the ghost on the stairs. Roofed in 3D now: a steep `slate` roof over the house with two brick chimneys, the tower over the door its own gable - the house read as a flat-topped box. |
| `tunnel_encounter` | good | 2 | tunnel_01 |  |
| `underground_waterway` | good | 4 | waterway_01 | A thinner fog with halos and lanterns at the far end: the channel recedes into lit stone, the boat and its reflection read. |
| `sewer_tunnels` | good | 3 | sewer_thing |  |
| `bunker_lab` | good | 4 | bunker_hud, bunker_crt |  |

### Outdoors

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `woodland_night` | good | 6 | woods_path, woods_fire, woods_dawn, woods_moon | Rebuilt for the forest fringe: `forest_deep` walls 2.4 high, free-standing spruce, oak, birch and dead trees, a moon in volumetric fog, a dawn shot through overrides, a ghost up the north road. |
| `autumn_lane` | good | 4 | autumn_lane, autumn_scarecrow, autumn_dusk, autumn_walk | A lane through an autumn wood under a low sun, a field with a scarecrow, pumpkins and hay bales behind a wall; jack-o'-lanterns at dusk. |
| `bayou` | good | 4 | bayou_dusk, bayou_night, bayou_gator, bayou_heron | A shack on an island in black water between mossy cypresses: sundown, fireflies at night, an alligator, a heron in mist. |
| `kelp_forest` | good | 4 | sea_kelp, sea_diver, sea_shoal, sea_night | A kelp forest in teal water: a wreck with its mast, a diver with bubbles rising, a shoal; a night dive by flashlight with jellyfish. The wreck is a `ship_hull` in 3D now, listing toward the cameras with its side stove in and the ribs showing, and the rock outcrops are `boulder`s of live `reef` rock. |
| `aquarium` | good | 8 | aquarium_hall, aquarium_manta, aquarium_tunnel, aquarium_jellies, aquarium_reef, aquarium_moon, aquarium_diver, aquarium_rockwork | A dark hall before the great window (whale shark, manta, a diver cleaning the glass, silhouettes, the floor mirroring it); the manta from below; the tunnel; sea nettles against blue; the reef tank; inside the ocean tank by a boulder. The big tanks' backs are rockwork against open water. |
| `coast_lighthouse` | good | 4 | coast_tower, coast_jetty | The shore rocks are the redrawn boulders now, not grey lumps; sand and water redrawn too. The lighthouse itself is 3D now (a `lighthouse` object), its lamp lit at dusk. |
| `rainy_street` | good | 4 | street_rain, street_lightning |  |
| `rain_alley` | good | 5 | alley_street, alley_rain, alley_glass, alley_storm, alley_cars |  |
| `neon_street` | good | 5 | neon_street, neon_stall, neon_signs, neon_runner, neon_counter | The neon facade style in the rain: signs, blade signs, lantern wires, a hologram koi, a noodle stall, vending machines, steam, the runner; bloom on the neon. |
| `night_market` | good | 5 | market_lane, market_cart, market_puddle, market_runner, market_samurai | A lane of stalls between neon fronts in the rain: lantern strings overhead, food carts, fruit and gadget stalls, a crowd; the cart close up; the lanterns in the wet; the runner under a lit umbrella. |
| `neon_bar` | good | 5 | bar_room, bar_tank, bar_arcade, bar_bartender, bar_hacker | A small smoky bar: glowing shelves, the counter and stools, a jukebox and booths, a reef tank in the back wall, the arcade row mirrored in the floor, the bartender. |
| `neon_rooftop` | good | 4 | rooftop_canyon, rooftop_down, rooftop_train, rooftop_cat | From a roof five storeys up: the neon canyon below with lanterns and a holo koi, the runner and a black cat on the ledge; straight down past the blade signs; the elevated train from the street. |
| `capsule_hotel` | good | 4 | capsule_corridor, capsule_berths, capsule_sleepwalker, capsule_vending | A corridor between two walls of berths at 4 a.m.: the berths up close, the sleepwalker with her candle, the hacker at the vending machine. |
| `doomed` | good | 4 | doomed_pit, doomed_overview, doomed_fight, doomed_window | The slime pit: a walkway zigzagging over glowing sludge, green banded walls, barrels, zombified soldiers; the HUD with a pistol; the pit from above; a shotgun going off and a fireball coming in; the window onto the rock. |
| `vector_world` | good | 5 | vector_sunset, vector_racers, vector_beacon, vector_core, vector_runner | A city of light on the grid: towers ruled in neon, racers trailing light down the avenue under a striped sun, a black core over a plaza of light beams, a beacon's flare, a runner in a suit of light. |
| `salt_flat` | good | 6 | salt_sunset, salt_door, salt_noon, salt_night, salt_whale, salt_portal | A salt flat after rain mirroring the sky: a girl with a candle at sunset, a door standing alone, raked heaps of salt in 3D at noon, the stars doubled, a whale over the mirror. |
| `sky_islands` | good | 5 | isles_temple, isles_bridge, isles_above, isles_golden, isles_falls | Meadows adrift over a sea of cloud: a temple island with a waterfall, keels of rock in 3D, a ruined ring of Doric columns in marble, a plank bridge to an islet of trees, golden hour. Ringing the islands' cliffs with `rock_wall`s was tried and dropped: they turned the floating meadows into a rocky fortress. |
| `glow_jungle` | good | 4 | glow_pool, glow_head, glow_flowers, glow_path | A clearing at night where every plant glows: a pool of glowing plankton, a stone head lit green, a heliconia burning pink, a path into the jungle. |
| `aurora_palace` | good | 4 | aurora_lake, aurora_gate, aurora_throne, aurora_shore | A palace of ice on a frozen lake under the aurora: the lake doubling it, the gate, the throne in a hall of frost, the shore. Crystals of ice in 3D now flank the gate, the throne and the shore, bending the aurora; their light makes the palace glow (it was dark blocks). |
| `clockwork_city` | good | 4 | clock_plaza, clock_orrery, clock_gears, clock_tower | A plaza of brass and brick at sundown: the orrery (wireframes) before the clock tower, gears of brass in 3D standing out from the walls and under the clock, pipes venting steam, gaslamps, an automaton. |
| `village_green` | good | 4 | village_market, village_stall, village_well, village_night | A cobbled street of timber-framed houses to a green: a market stall and its keeper, the inn sign, a cart, the well; the inn lit after closing. |
| `ghost_town` | good | 4 | western_noon, western_saloon, western_ghost, western_windpump | A frontier main street: a cowboy at high noon, the saloon and its barkeep, sundown with lanterns and a ghost, a windpump in the desert. |
| `misty_moor` | good | 3 | moor_dawn, moor_circle | A stone circle in 3D (`standing_stone`s, leaning, their tops sloping, an altar slab) throwing long shadows and shafts of sun through the dawn mist. |
| `winter_lake` | good | 5 | winter_night, winter_day, winter_cabin | Ice redrawn (fractures, depth) and snow redrawn (drifts); the snowy spruce and snow-capped boulders. The cabin wears a roof under snow in 3D with wood smoke from its chimney (it was a flat-topped box), the shore boulders are 3D, and a fifth shot shows the cabin close by day. |
| `winter_woods` | good | 4 | winter_lane, winter_deer, winter_lantern, winter_stream | A snowbound wood: the lane, a deer on a frozen stream in falling snow, a child by a lantern-lit footbridge, trees mirrored in the ice. |
| `chapel_graveyard` | good | 4 | chapel_yard, chapel_nave | The yard is a little sparse. Roofed in 3D now: a steep `slate` roof down the nave, its gable over the door in pale stone (`ends`: `ashlar`). |

### Castles, ruins and caves

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `castle_keep` | good | 6 | castle_throne, castle_gate, castle_hall | The throne hall closer: a great stained-glass window, banners and candelabras behind a larger throne, guards at the steps, the knight to one side. The hall's square pillars are round in 3D (`column`s of `ashlar`, bases and capitals) with timber beams across the hall over them; a sixth shot, `castle_hall`, takes them in from the hall's foot. |
| `cathedral_ruin` | good | 3 | cathedral_beam, cathedral_pilgrim | The beam through the fallen roof, rafters still spanning the hole with ivy hanging from it, column drums and rubble in the light; shot from the aisle. |
| `crystal_cave` | good | 5 | cave_beast, crystal_cave, crystal_violet, crystal_close | Rebuilt round crystal clusters that refract: a great cavern with a lake of glowing water, the great crystal on its island, clusters round the walls, the walls lined with cave rock and glowing-moss rock, the glowing jungle's plants along the shore; the survey robot and the beast wading before the great crystal. |

### Space, alien and dream

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `space_station` | good | 3 | station_deck, station_corridor |  |
| `derelict_ship` | good | 3 | derelict_corridor, derelict_hive |  |
| `orbital_hangar` | good | 4 | hangar_bay, hangar_control, hangar_reactor, hangar_pilot | A shuttle bay in orbit, its control room and the reactor: the scifi.py hardware, glass panes between mullions onto space and a ringed planet, a window onto the bay, cyan haze and red alarm light. |
| `alien_world` | good | 3 | alien_landing, alien_monolith | Its two billboard crystals are `crystal_cluster`s in 3D now, with two more flanking the plateau: the monolith shot is framed in violet and cyan crystal. |
| `moon_base` | good | 4 | moon_base, moon_rover, moon_night, moon_earth | Greenhouse domes and habitat modules on the grey plain under the Earth: day, the rover, the lunar night, Earthrise over the domes. |
| `dream_world` | good | 3 | dream_stair, dream_mirror | Islands in a pastel sky, each with a `keel` of rock in 3D under its cliff; the stair shot is taken from out over the void, so the island floats; chess pieces in 3D on the chequered island. |
| `dream_chess` | good | 4 | dream_plain, dream_door, dream_hole, dream_clock | A giant chess game in 3D (`chess_piece`, polished white and black marble, mirrored in the floor) on a floating plain of checker_marble under a melting sky clock: arches and stairs in the air, a stair up to a lone door, a hole onto the sky. |
| `drowned_library` | good | 4 | library_hall, library_reader, library_beams, library_water | Bookshelves three storeys high in still water under tall windows and skylights: beams in dark fog, jellyfish, lanterns, flying books, koi and a whale. Dark timber roof beams cross the hall between the skylights (`beam` objects of wood, on brackets), and the light is a touch stronger so the shelves read. |
| `hall_of_doors` | good | 5 | doors_hall, doors_stair, doors_sky, doors_up, doors_portal | An endless corridor of doors in every colour, three storeys and the ceiling; a door onto the sky, a stair to a door in the air, the sleepwalker. In relief now: a pilaster of cream marble between every two doors and a cornice along every storey (`column` and `beam` objects), so the corridor catches the light. |

### Claude

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `claude_study` | good | 4 | claude_ask, claude_balcony | Claude's own place: the study under the stars, and the balcony. |

### Feature demos

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `gui_hud` | good | 1 | gui_hud |  |
| `gui_lantern` | good | 1 | gui_lantern |  |
| `gui_menus` | good | 2 | gui_menus_01, gui_menus_02 |  |
| `gui_themes` | good | 5 | gui_themes |  |
| `gui_trade` | good | 2 | gui_trade_01, gui_trade_02 |  |
| `post_presets` | good | 12 | post_presets |  |

### Jungle, ruins and beach

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `jungle_temple` | good | 4 | jungle_path, jungle_temple, jungle_jaguar, jungle_canopy | The fringe wanders and the canopy is level by open ground, so from the pyramid top the clearing's edge is a line of trees, not stepped hedges. |
| `ancient_ruins` | good | 5 | ruins_way, ruins_head, ruins_night, ruins_columns | The cella shot could use shafts of light through the columns. Adding a shot moves the scatter (it is kept off cameras and sight lines): place a new one where none lies. |
| `red_canyon` | good | 4 | canyon_wash, canyon_ruins, canyon_slot, canyon_sunset | A wash between ragged walls of layered sandstone, saguaros, cliff-dwelling ruins, a slot canyon lit by one beam, the wall at sunset. |
| `tropical_beach` | good | 5 | beach_sunset, beach_pier, beach_day, beach_night, beach_flare | A palm-fringed lagoon at sunset, the pier and the hut, midday, glowing surf at night by a fire; into the sun with a lens flare. |

### Not yet sorted

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `saloon` | good | 5 | saloon_noon, saloon_cards, saloon_piano, saloon_gambler, saloon_barkeep | New: the frontier town's saloon - the noon sun through the front windows into dusty air, a card game, and after midnight a ghost at the piano. The day's people are the shots' extra sprites, so the room at night is empty. |
| `gold_mine` | good | 3 | mine_tunnel, mine_vein, mine_portal | New: the frontier mine - a tunnel timbered in 3D with rails and lanterns, a prospector at a vein of gold, the portal in a hillside of canyon rock at dusk. |
| `temple_inside` | good | 3 | temple_passage, temple_idol, temple_reach | New: inside the jungle pyramid - a passage of glyphs, the idol on its altar in a shaft of sun through the broken roof between square pillars, the explorer beside it. |
| `fjord` | good | 3 | fjord_day, fjord_dusk, fjord_water | New: a longship on the shingle at the head of a fjord, cliffs in 3D on both sides, a longhouse under thatch, another ship at anchor - by day, at dusk by the fire, and from the water. |
| `palm_house` | good | 3 | palm_path, palm_fountain, palm_back | New: a Victorian glasshouse full of palms, its roof of glass in 3D (`gable_roof`, `cover` and `ends` of `glass`, drawn as glass) on iron columns and ribs (`iron_white`), the sun pouring in, a fountain under the ridge. |
| `autumn_garden` | good | 3 | garden_gate, garden_pond, garden_dusk | New: a Japanese garden in autumn - a red gate, stone lanterns, maples, a pond and bridge, a tea house under grey tiles; at dusk the lanterns lit. |
| `sunken_temple` | good | 3 | sunken_temple, sunken_colonnade, sunken_head | New: a temple of marble on the floor of the sea - the ruins' fluted columns in 3D standing under their architrave in the kelp forest's water, others fallen, coral on the stones, a manta overhead, the diver at the marble head. |
| `basalt_coast` | good | 3 | causeway_sunset, causeway_organ, causeway_hexagons | New: a causeway of hexagonal basalt columns stepping down into a sea that mirrors the sunset, organ pipes up the cliff, every column casting its shadow on the next. |
| `glass_chapel` | good | 3 | glass_matins, glass_beam, glass_monk | New: a nave of pale stone, lancets down both walls and a rose window over the altar, mid-morning, the sun behind the south lancets - their colours laid across the floor, the pews and a monk, coloured beams in a thin fog; rows of `pew` objects either side of the aisle. |
| `village_hours` | good | 8 | village_hours | New: the village green's market street eight times over, each shot one `time` of day and nothing else - dawn to night: the sun going round and down, the sky, the air, the windows, the inn's lanterns (lights marked `"night": true`) lit from sunset. A sheet in the gallery. |
| `giant_valley` | good | 4 | valley_dawn, valley_village, valley_above, valley_afternoon | New: landscape scale - a river valley seen from a giant's height at dawn: the river winding through water meadows and a patchwork of fields, woods and then pines up the flanks, ranges of snow-topped mountains either side and a great peak at its head, a village with its church and a hamlet upstream, mist along the valley floor; the afternoon in shot 4. |
| `kaiju_harbor` | good | 6 | kaiju_bay, kaiju_quay, kaiju_breath, kaiju_ashore, kaiju_close, kaiju_moth | New: landscape scale - a city at night and a kaiju wading in from the bay: blocks of lit towers, searchlights and the helicopters' lamps on it, tanks firing from the quay, the waterfront burning, its breath cutting into downtown from the air; shot 4 is the next day at golden hour, the monster ashore and jets overhead; shot 5 a helicopter's view, eye to eye with it as it breathes; shot 6 a giant moth coming in over the bay to meet it. |
| `kaiju_country` | good | 4 | country_town, country_stride, country_pylon, country_evening | New: landscape scale by day - the kaiju walking in across a plain of farmland and woods toward a market town at a crossroads, a line of pylons with their cables slung arm to arm (a pylon nearly its height makes the scale), jets, helicopters, tanks on the road, a wood burning; from the edge of town, a helicopter, the foot of a pylon, and a long lens at golden hour. |
| `volcano_island` | good | 4 | island_eruption, island_town, island_above, island_delta | New: landscape scale at night - a volcano erupting over a harbour town: lava fountaining over the crater's rim (big blazes), running down its flanks (`lava` aimed at the cameras) and on to the sea as a river (`lava_flow`) that steams where it meets it, an ash column lit from below; from the sea, the quay, the air and a boat off the delta. |
| `mesa_desert` | good | 4 | desert_road, desert_above, desert_sunset, desert_moon | New: landscape scale - buttes, spires and long mesas (`mountain`s with a `cliff`) standing out of a red plain, a highway running straight at them, each casting its shadow over the desert in the low sun; down the road at golden hour, from the air, against the sunset, by moonlight. |
| `strait_bridge` | good | 5 | strait_golden, strait_quay, strait_above, strait_dusk, strait_kaiju | New: landscape scale - a suspension bridge across a sea strait, a town where it comes ashore, a cargo ship, a ferry and sailboats under it, a lighthouse on the far point; golden hour from the water and the quay, from the air, and dusk with its lamps lit. |
| `winter_valley` | good | 4 | winter_lake, winter_village, winter_street, winter_morning | New: landscape scale at night under the `aurora` - a frozen lake, a village on its shore with snow on its roofs and its lamps lit, white mountains, pines under snow; across the ice, from the village street to the white peak, and the morning after. |
| `archipelago` | good | 4 | archipelago_boat, archipelago_above, archipelago_atoll, archipelago_golden | New: landscape scale - tropical islands in a blue sea: a high island with a jungle hill (`tropical` rock) and a thatched village, a smaller one, a low atoll round its own lagoon, all ringed with sand, lagoon and reef; from a boat, from the air, from the atoll's beach, and golden hour. |
| `canal_tunnel` | good | 3 | canal_tunnel, canal_boat, canal_moored | New: one of the three drawings the project began from - a canal under a brick vault (`vault_arch` cards), paired wall lamps, an iron cabinet, a painted sigil, pipes along the vault, a boat (a `ship_hull`) moored with a lantern at its bow; a shot from the boat. |
| `storm_island` | good | 2 | storm_island, storm_town | New: the first drawing - an island town on a stormy night at landscape scale: a hill with a house on its flat top, tenements and cottages on the shore, a plateau of buildings, a lighthouse and its beam, lightning on the power station under `storm_cloud`s. The lighthouse's red band and the plateau's warning lights are lost to the palette in this dark frame. |
| `window_garden` | good | 2 | garden_window, garden_statue | New: the second drawing - a moonlit garden through a broken casement between tattered curtains, glass on the floor; a robed statue on its pedestal, roses, a lamp post, a house with one window lit, a tower; and the statue under the moon. |
| `coast_road` | good | 2 | road_coast, road_checkpoint | New: a road scene (road.py) - an arcade racer's road along a coast at sunset from behind the wheel of a red convertible: palms, billboards, the beach and the sea, cars ahead, a checkpoint over the road, a racer's time, score and speed; and leaning into the bend (`roll`). |
| `enchanted_path` | good | 1 | road_enchanted | New: a road scene - a cobbled path at night through a wood that glows, giant mushrooms lighting it, wisps, two moons, a witch with her lantern. |
| `forest_path` | good | 1 | road_forest | New: a road scene that is a path - dirt, ragged and blended into the grass, through a wood of spruce, oak and birch on a misty morning, someone walking it ahead. |
| `jungle_trail` | good | 1 | road_jungle | New: a road scene - a muddy trail into the jungle under kapoks, an explorer going on toward a ruined stone arch. |
| `night_highway` | good | 2 | road_night, road_tunnel | New: a road scene - a city highway at night under sodium lamps, tail lights ahead, headlights; a tunnel through the hill (`tunnel_ring`s behind a `tunnel_portal`, `roofs`), and from inside it. |
| `sky_road` | good | 1 | road_sky | New: a road scene with no ground - a road of marble across a sea of cloud, columns and arches, floating islands, a sky whale, a dreamer walking toward the sun. |
| `mountain_pass` | good | 2 | road_mountain, road_valley | New: a road scene - a road cut into a mountainside: the `cliff_face` with a ragged top, a guard rail and the drop, the valley far `below` in bands (woods, a river, pasture, pine forest), its far side a hazy ridge; and the view at the rail. A flat green carpet below until true scale and the far side closed the view. |
| `canal_boat` | good | 1 | road_canal | New: a road scene on the water - a canal tunnel vaulted in `brick_ring`s, lamps on the walls, a narrowboat against the daylight at its mouth, your bow and its lantern. |
| `canyon_run` | good | 2 | road_canyon | New: a road scene off the road - a jeep down a dirt track through a red rock canyon after a rally car's dust; one wall in light, one in shade; leaning into a bend. |
| `island_run` | good | 2 | road_island, road_island_low | New: a road scene on the water - a speedboat across a tropical bay, the island's palms and the boats mirrored, a low sun's image on the sea; and low over the water toward the shore. |
| `neon_avenue` | good | 1 | road_neon_avenue | New: a road scene in the neon city - walking the pavement in the rain, red lanterns strung over the street, a noodle stall, signs, a taxi, hover cars flying over. |
| `neon_race` | good | 2 | road_neon_race, road_neon_lean | New: a road scene in the neon city - a hover car down a wet street of shops and towers (walls in `blocks`), every window and sign mirrored, a racer's HUD; and leaning into the bend. |
| `roller_coaster` | good | 2 | road_coaster_drop, road_coaster_curve | New: a road scene that is a ride - a roller coaster's see-through track over the park, its frame as walls down into the ground; the top of the drop, and a banked curve. |
| `desert_highway` | good | 2 | road_desert, road_desert_crest | New: a road scene - a motorbike down a desert highway at noon, buttes in the haze (walls in `blocks` with gaps), power lines; and from a crest, the road dropping out of sight and rising again. |
| `synthwave_drive` | good | 2 | road_synthwave | New: a road scene - the red convertible across a magenta grid of light toward a striped sun, palms in silhouette; and leaning into the bend. |
| `winter_road` | good | 1 | road_winter | New: a road scene - a mountain road at night after snow, the plough's banks, snowy pines, headlights on the falling snow, a car's tail lights ahead. |
| `grand_prix` | good | 2 | road_grand_prix, road_grand_prix_side | New: a road scene - on the grid at the start of a race, the five red lights lit, the field ahead in four liveries, grandstands full; and from the side of the track. |
| `mine_ride` | good | 1 | road_mine | New: a road scene that is a ride - a runaway mine cart down the rails through a gold mine, timber sets with their lamps, crystals. |
| `space_trench` | good | 1 | road_trench | New: a road scene in space - a starfighter low down a trench in a great ship's hull, walls of panels and lit strips, bolts of fire, a ringed planet. |
| `desert_motel` | good | 1 | road_motel | New: a road scene - the desert highway at night, a motel's neon sign and its row of lit rooms, a gas station lit white across the road. |
| `ice_road` | good | 1 | road_ice | New: a road scene - a track ploughed across a frozen lake at night under the aurora, the black ice mirroring it, a truck's tail lights ahead. |
| `jungle_river` | good | 1 | road_jungle_river | New: a road scene on the water - by canoe up a jungle river, its banks mirrored in the still water, a heron, an alligator, macaws. |
| `sea_tunnel` | good | 1 | road_sea_tunnel | New: a road scene - a road through a glass tube on the sea floor (walls of `viewport`, a roof of `tunnel_roof`), a shark and a turtle gliding past outside. |
| `viaduct_train` | good | 1 | road_viaduct | New: a road scene - at the front of a train crossing a long stone viaduct over a valley, steam drifting back. A hill of walls ahead stood beside the line like a building: dropped. |
| `autumn_lane_road` | good | 1 | road_lane | New: a road scene - a narrow lane between high hedges in autumn, leaves on it, a little car ahead (`autumn_lane` is the raycaster's lane: an example's name must be new). |
| `rain_motorway` | good | 1 | road_rain_motorway | New: a road scene - a dual carriageway at dusk in the rain, oncoming headlights across the barrier, tail lights ahead, the wet road mirroring all of it. |
| `suspension_bridge` | good | 1 | road_bridge | New: a road scene - across a great suspension bridge at dawn, its red towers over the road every span, the cables sagging between them, the bay far below, the city ahead. |
| `dark_road` | good | 1 | road_dark | New: a road scene - an old road across a land of lava toward the dark castle, braziers burning, a knight walking it. The lava's glowing cracks read as city lights until the band's `tile` was 8. |
| `rope_bridge` | good | 1 | road_rope_bridge | New: a road scene - a bridge of planks and rope between floating islands, the dream sky's sea of cloud beneath it, a stone gate where it lands. |
| `underworld_river` | good | 1 | road_underworld | New: a road scene on the water - a ferry down a dark river through a cavern, statues holding fire on its banks, green wisps over the water. A dim ceiling hid the walls: its light went up. |
| `moon_drive` | good | 1 | road_moon | New: a road scene - following a moon buggy across the dust toward the base, the Earth in the black sky, craters and rover tracks, an astronaut walking out. |
| `night_canal` | good | 1 | road_canal_night | New: a road scene on the water - by boat down a canal between old houses at night, their lit windows doubled in the water, a gondola ahead, washing over the canal, a bridge, the moon. Side-on rowboats moored along it read as rafts across the canal: dropped. |
| `ski_run` | good | 1 | road_ski | New: a road scene - down a groomed run on a bright day, slalom gates, a skier ahead, the chairlift beside it, your ski tips below. A run that only fell showed haze where the land dropped away: it levels out into a valley and climbs the far side. |
| `sky_lane` | good | 1 | road_sky_lane | New: a road scene - racing a lane of light hung high between the towers of the neon city at night, flying cars ahead, the city far below. A road surface's glow now lights it (it was ignored). |
| `night_runway` | good | 1 | road_runway | New: a road scene - from the cockpit, lined up on a runway at night, its edge lights running away to the horizon, an airliner lifting off ahead, the tower lit. |
| `tulip_ride` | good | 1 | road_tulips | New: a road scene - cycling a red path through the bulb fields in spring, bands of tulips to the horizon, windmills, ditches mirroring them, tulips in your basket. White edge lines swamped the narrow path: dropped. |
| `bayou_run` | good | 1 | road_bayou | New: a road scene on the water - poling a skiff down a bayou at dusk, cypresses hung with moss, fireflies, a shack on stilts with its window lit and mirrored. Moss sprites set at a height floated as clumps in the sky: dropped (the cypresses carry their own). |
| `blossom_road` | good | 1 | road_blossom | New: a road scene - walking a country road through cherry trees in bloom, petals falling (the `snow` effect in pink), a shrine gate over the road with the snowy peak framed in it. The first trees closed into a tunnel of blossom that hid the gate and the peak. |
| `camel_caravan` | good | 1 | road_caravan | New: a road scene - riding a camel in a caravan over the dunes at sunset, the camels ahead, two pyramids against the sun. Dunes as walls with a `ragged` top came out as jagged rock: they are a `hills` skyline in the sand's colour. |
| `candy_road` | good | 1 | road_candy | New: a road scene - racing a road of peppermint through a land of sweets: candy canes, lollipop trees, gumdrop hills, gingerbread houses, a chocolate river (mud, a little `reflect`: more mirrored the sky grey). |
| `ghost_train` | good | 1 | road_ghost_train | New: a road scene - riding a ghost train through its haunted house: rooms of wallpaper under a low ceiling, candelabras and jack-o'-lanterns, a skeleton leaping out lit green, a ghost over the rails. |
| `kelp_run` | good | 1 | road_kelp | New: a road scene under the sea - gliding a submarine through a kelp forest behind a little sub, light slanting down, fish, a turtle, a shark. A sliver of bright sky showed where the ceiling and the floor stopped: drawn far, under a dark sky. |
| `ring_station` | good | 1 | road_ring | New: a road scene - driving the inside of a ring in space, the land climbing ahead into the sky, space past the glass of its rims (a ground band of `void`, new). |
| `sled_run` | good | 1 | road_sled | New: a road scene - driving a dog sled down a trail through snowy pines under the aurora, the huskies running ahead, a log cabin's windows lit. |
| `storm_chase` | good | 1 | road_storm_chase | New: a road scene - chasing a tornado down a straight road across the plains, lightning, wheat to the horizon, a red barn, the chasers' pickup. |
| `close_encounter` | good | 1 | road_encounter | New: a road scene - pulled up on a desert road at night, a flying saucer over the road, its beam letting down and a cow rising up it, a farm by the road. |
| `high_seas` | good | 1 | road_high_seas | New: a road scene on the water - from the bow of a sailing ship at golden hour, a galleon ahead mirrored in the sun's glow, a stone fort on its rock, gulls. |
| `night_fair` | good | 1 | road_fair | New: a road scene on foot - walking the midway of a fair at night, stalls lit, the big wheel ahead, a carousel. A paper lantern every five units made it a night market: one every fourteen. |
| `safari_drive` | good | 1 | road_safari | New: a road scene - following a jeep down a red track across the savanna at sunset, giraffes under an acacia, elephants and zebras. |
| `high_noon` | good | 1 | road_high_noon | New: a road scene on foot - the main street of a frontier town at noon, false fronts either side, a gunslinger waiting in the street, horses at the rails, the water tower at the end. |
| `storm_coast` | good | 1 | road_storm_coast | New: a road scene - a cliff road at night in a storm, rain across the headlights, the lighthouse on the headland sweeping its beam over the sea. |
| `balloon_flight` | good | 1 | road_balloon | New: a road scene in the air - drifting in a hot-air balloon over the desert at dawn, balloons at every height, the mesas far below. A cable car ride over a valley was tried first and dropped: from that height the fields read as a game board. |
| `drowned_city` | good | 1 | road_drowned | New: a road scene on the water - by boat down a flooded avenue of an abandoned city at sunset, the towers overgrown and doubled in the water, driftwood, crows. |
| `log_flume` | good | 1 | road_flume | New: a road scene at the fair - at the lip of a log flume's big drop, the channel plunging away through the pines to the splash far below. |
| `metro_ride` | good | 1 | road_metro | New: a road scene underground - from the cab of a metro train running into the next station, the platforms lit, people waiting. From deeper in the tunnel its walls hid the station. |
| `pilgrim_path` | good | 1 | road_pilgrims | New: a road scene on foot - a stony path high in the mountains under prayer flags, white stupas, a monk ahead, snow peaks round the valley (big peaks first filled the sky). |
| `volcano_road` | good | 1 | road_volcano | New: a road scene - racing down a jungle road at night under an erupting volcano, lava in the fields, ash falling, the jungle black against the glow. |
| `hayride` | good | 1 | road_hayride | New: a road scene on a farm - on the back of a hay wagon down a lane at dusk, the tractor towing, pumpkins thick in the fields, jack-o'-lanterns lit. The tractor first filled the view. |
| `hill_street` | good | 1 | road_hill_street | New: a road scene - at the brow of a steep street of painted townhouses, a cable tram going down, the street running out across the bay to the bridge in the fog. Looking down the slope it read flat: the camera stands at the brow. |
| `ice_cave` | good | 1 | road_ice_cave | New: a road scene on the water - paddling through a cave of blue ice under a glacier, the daylight glowing through its roof, icicles; from the kits as they were (dim, it read as a dungeon). |
| `red_planet` | good | 1 | road_red_planet | New: a road scene on another world - following a buggy across a rust-red plain, mesas, a dust devil (the tornado, recoloured), two small moons; the Moon's kit tinted, no new assets. |
| `sleigh_ride` | good | 1 | road_sleigh | New: a road scene on a winter night - by horse-drawn sleigh down a snowy village's lane, cabins' windows lit, firs strung with lights, snow falling. |
| `dragon_flight` | good | 1 | road_dragon | New: a road scene in the air - riding a dragon at sunset down a river valley toward a dark castle on its crag, other dragons on the wing. Props below a `void` side used to be cut off at the road's line (the crest clip); now they stand in the valley and are seen. |
| `lantern_river` | good | 1 | road_lanterns | New: a road scene on a festival night - drifting down a river among floating lanterns, sky lanterns rising into the stars, cherry trees on the banks, a shrine gate in the water. The sky lanterns at their own small size were specks: larger, and more of them. |
| `launch_day` | good | 1 | road_launch | New: a road scene on the coast at dusk - driving the causeway across a lagoon toward a rocket floodlit on its pad, cars pulled over and people out to watch. At its first size the rocket was lost on the horizon. |
| `neon_canal` | good | 1 | road_neon_canal | New: a road scene in the neon city's flooded quarter - by water taxi down a canal at night in the rain, shops lit at the water's edge, signs and lanterns over it, hover cars overhead, all of it doubled in the water. The nearest lanterns filled the sky: they start farther off, smaller. |
| `overgrown_highway` | good | 1 | road_overgrown | New: a road scene years after - walking down a motorway gone back to the wild, weeds up through the cracks (the new `overgrown` scatter set), rusted cars, a doe and her fawn on the road, a broken overpass ahead. With bushes in the weeds the road vanished under them; trees close to it hid the overpass. |
| `airship_voyage` | good | 1 | road_airship | New: a road scene in the air - at the bow of an airship at sunrise over a sea of cloud, islands floating at every height with water pouring off them, airships under way. The falls first hung loose under the islands' keels. |
| `market_ride` | good | 1 | road_market | New: a road scene in a medieval town - riding a horse up the high street on market day between half-timbered houses, stalls and banners, the townspeople out, the castle on its hill at the end. The nearest stalls first hid the street and its people. |
| `night_pass` | good | 1 | road_night_pass | New: a road scene racing a mountain road at night - a rival ahead, the cliff beside you, the city spread out in lights far below the drop. The city below was dark until the land down there glowed where its texture does; at a small `tile` its lights were noise. |
| `redwood_road` | good | 1 | road_redwood | New: a road scene through a forest of giant redwoods on a misty morning - trunks wider than the car, the canopy closed overhead, sunlight slanting down. Where the road bent a near trunk stood in the middle of the view: the road runs straight first. |

## Pass log

- **2026-10-19, pass 0.** First full review of every asset, on review sheets and in the gallery. This file and `docs/asset_review.py` were added.
- **2026-10-23, the roads loop.** Eight hours on road scenes while the user rested: verges scattered and roads marked (`scatter` and `decals` for roads); walls along the road (rails, cliffs, canyons, streets of buildings in `blocks`), ceilings, land far `below` a drop; reflections (water, wet streets, puddles: the sky, the props and the walls mirrored); vehicles that carry a light or lay a wake; see-through road surfaces. Road furniture, off-road vehicles, boats, the neon city's cars and facades, a coaster, a mine, a starfighter, race cars and a grandstand; the traffic and the billboard drawn a few ways; an oncoming car, a motel sign, a gas station; a suspension bridge's towers and cables, a dark castle; canal houses, a gondola, mooring poles, a humped bridge, washing; a ski run's piste, net, chairlift, gates, skier and ski tips; a lane of light over a city at night, a moon buggy, craters; a steam engine's boiler from the footplate, telegraph poles; tulip fields, a windmill, a cyclist, handlebars; runway lights, a control tower, an airliner, a cockpit; a shack on stilts, a camel and your own camel's head, a pyramid; peppermint, frosting, candy canes, lollipops, gumdrops, a gingerbread house; a skeleton and a ghost-train car; cherry trees, a shrine gate, a lone snowy peak; wheat, a tornado, a barn, a pickup; a mini sub, light shafts, a porthole; a dog team, a log cabin; a galleon, a sea fort, a bowsprit; acacias, giraffes, elephants, zebras; a flying saucer, its beam, a cow; a big wheel, a carousel; false fronts, a horse; a lighthouse and its beam; an erupting volcano; a metro tunnel and station, a signal, a cab; ruined towers; a log boat; prayer flags, a stupa; a balloon basket; a tractor and a hay wagon, a sleigh and its horse, a Christmas tree; painted townhouses and a tram; a dragon to ride and dragons on the wing; wrecked cars and a broken overpass; a water taxi; a floating lantern; a rocket on its pad; airships, an airship's deck and falls off a floating island; half-timbered houses, a horse from the saddle and a castle on its hill; a giant redwood; glowing road surfaces and ground bands of `void`; the `speed` post effect. Sixty-five new road scenes: mountain_pass, canyon_run, island_run, canal_boat, neon_race, neon_avenue, roller_coaster, synthwave_drive, desert_highway, winter_road, mine_ride, space_trench, grand_prix, ice_road, desert_motel, sea_tunnel, viaduct_train, jungle_river, autumn_lane_road, rain_motorway, suspension_bridge, dark_road, rope_bridge, underworld_river, night_canal, ski_run, sky_lane, moon_drive, tulip_ride, night_runway, bayou_run, camel_caravan, candy_road, ghost_train, blossom_road, storm_chase, kelp_run, ring_station, sled_run, high_seas, safari_drive, close_encounter, night_fair, high_noon, storm_coast, volcano_road, metro_ride, drowned_city, log_flume, pilgrim_path, balloon_flight, hayride, sleigh_ride, hill_street, red_planet, ice_cave, dragon_flight, overgrown_highway, neon_canal, lantern_river, launch_day, airship_voyage, market_ride, night_pass, redwood_road. The night runway now takes off at nightfall (at full night it was a dark band under the cockpit). The viaduct is now seen from the footplate; scrub clings to the mountain pass's cliff.
- **2026-10-23, road scenes.** The user's idea: a second renderer, the road of an 80s arcade racer - a scene with a `road` instead of a `map` (scripts/road.py): segments that bend and rise, projected from the camera outward so a crest hides what is beyond, the bands, lanes, kerbs and shoulders, the ground in bands or `void`, props along it by spacing or density (`roadside`), lamps and headlights, `roofs` for tunnels, a shot's `vehicle`, `roll` with the vehicle level; finished by the same post, GUI and palette (render.finish_world, render.make_renderer). The `highway` kit: `sports_car`, `car_compact`, `car_sedan`, `box_truck`, `curve_sign`, `billboard`, `checkpoint`, `traffic_cone`, `tunnel_ring`, `tunnel_portal`. Scenes `coast_road`, `night_highway`, `forest_path`, `jungle_trail`, `enchanted_path` and `sky_road`.
- **2026-10-23, where it started.** The user's idea: the three drawings this project began from - concept art Claude drew out of plain shapes in a chat, for a game - made into scenes and set beside them in the README (the drawings are in `docs/origins`). `scripts/spooky.py`: `vault_arch`, `broken_casement`, `tattered_curtain`, `rose_bush`, `robed_statue`, `wall_lamp`, `iron_cabinet`, `punt` and `storm_cloud`; decals `glass_shards` and `sigil`. Scenes `storm_island` (landscape scale: a hill and its house, the town on the shore, a plateau of buildings, the lighthouse, a storm), `window_garden` (the garden through a broken casement) and `canal_tunnel` (a boat moored under a brick vault, and a shot from it).
- **2026-10-22, the landscapes loop.** The user's three hours: the kaiju redrawn where it was wrong (the jaw hinged into the neck, no gap; the legs under the hips so the belly shows whole; thin surf), the mountains' points rounded into crowns (and `top` for mesas). New: the `cable` object, country roads (`road_ew`, `road_ns`, `road_x`), and a volcano from the mountain - `crater`, `lava` flows, rock kinds `volcanic` and `lava`, textures `lava_field`, `lava_flow`, `black_sand`, the `ash_plume`; buttes from the mountain (`cliff`) and the desert's ground (`desert_floor` in three layouts, `desert_road`). New scenes `kaiju_country`, `volcano_island` and `mesa_desert`; a fifth kaiju_harbor shot, eye to eye with the monster. Then: winter (`snow_fields`, `snow_forest`, `frozen_lake`; a `village` takes `lit` and `snow`), the `bridge` object (`suspension`, `stone`), ships (`cargo_ship`, `ferry`, `sailboat`); scenes `winter_valley` and `strait_bridge`; a stone bridge by giant_valley's village. Last: the tropics (`ocean`, `lagoon`, `reef_flat`, `white_sand`, `palm_canopy`, rock `tropical`, a village's `roof`) and the `archipelago`; a rival for the kaiju, the `giant_moth`.
- **2026-10-22, landscape scale.** The user's idea: shrink the world and the camera is a giant's - a map cell about 100 m, so a kaiju 0.62 tall stands in a city as a person stands in a room. `scripts/landscape.py`: the city's ground (`city_street`, `city_street_lit`, `harbor_water`, `quay`, `container_yard`, `city_park`) and the country's (`farmland` in six layouts whose fields cross the cells' edges, `pasture`, `forest_canopy`, `pine_canopy`, `river_water`); the `kaiju` (standing, roaring, wading), `tanks`, `helicopter`, `jet`, `blaze`, `smoke_plume`, `pylon`. Objects: `tower` and `city_block` (floors of windows, lit at night and turned down by day by the `time`), `searchlight` and `ray` (beams of additive light), `mountain` (a new rock kind, `alpine`, its snow above a wandering line) and `village`. Objects and sprites take the `night` and `day` marks; the hour is applied after the prefabs and before the objects; a scatter takes `scale`. `examples/kaiju_harbor.py` and `examples/giant_valley.py`, four gallery shots each.
- **2026-10-22, the time of day.** One key, `time`, sets a scene or a shot to an hour - `dawn`, `morning`, `noon`, `afternoon`, `golden`, `sunset`, `dusk`, `night` or a number (scripts/daylight.py): the sun where the clock has it, east to west, reddening as it sinks, and a moon after it; the sky; the ambient light and the fog darkened and tinted from the scene's own (taken to be right for the hour its sky shows); fewer of the facades' rooms showing a lamp by day; lights marked `"night": true` lit only from sunset to sunrise. A new `dawn` sky. `examples/village_hours.py`: the village street at eight times, a sheet in the gallery.
- **2026-10-22, coloured glass.** The sun now comes in through stained glass coloured: a storey of `stained_glass`, `lancet_window` or `rose_window` (both new) is an opening for the light, each pane letting it on in its own colour and the lead and stone stopping it - worked out for every point the light reaches (render.sun_tint): where its ray toward the sun enters a wall of glass beyond it, at the height and the place along the face it crosses, so the window's pattern lies on the floor texel for texel at any height of sun, and the air outside a window, or over the roof, is lit by the sun itself. Two leaks closed on the way: where a solid wall rises to meet the roof, a sheet of light used to slip in along the join (the wall's shadow and the roof's, each with a soft edge); and the fog march took light from past the surface each pixel shows - the sunlit air over a roof or behind a wall - so ceilings and walls indoors glowed. Scenes with fog shafts indoors are a little darker and cleaner for it, the temple passage most. A `pew` object; `examples/glass_chapel.py` with three gallery shots.
- **2026-10-22, lettering and pages.** Lettering (scripts/lettering.py): the pixel font drawn into textures in eight styles - painted board, neon tubes, brass plaque, carved stone, chalk, gilt, ink, poster - big lettering rounded by scale2x; a `sign` object stands it on a board in 3D, and `sprite_defs` / `decal_defs` take `text`. The neon bar's name now hangs in neon on its wall. Pages (scripts/pages.py): rows of panels, each a shot of any scene rendered at the panel's own shape, as a comic page (caption boxes, the shots' bubbles, a sound in big letters, a title) or a storyboard (numbered panels, a note under each, no bubbles - they crowd small panels); examples/pages/, gallery `page_door` and `page_saloon`.
- **2026-10-22, pictures within pictures.** The user's idea, from the salt flat's lone door: mark where a portal shows, render another scene, lay it there. A `portal` object: before each frame the renderer draws the view from its far side - the camera moved through the portal to stand beyond its exit, at the same size and lens - and the opening shows those pixels, depth-tested and fogged as any panel (so it is hidden behind nearer things and lies in the scene's air). A `screen` object shows a whole shot, rendered once, as its texture: a TV, a monitor, a screen on a wall; an arcade cabinet's `show`. New shots `salt_portal` (the door onto the winter woods) and `doors_portal` (the hall's door onto the salt flat); the hall's three free doors are portals (the sky islands, the salt flat, the kelp forest); in the neon bar a screen over the bar shows the street and a cabinet plays the Vector World. Tried: the beach and an autumn lane behind the hall's door - seen at an angle they looked into palms and hedges; a wide-open place (the salt flat) reads from any side.
- **2026-10-22, props in 3D.** The user's list: the arcade cabinets, the capsule hotel's vending machine, the village's market stalls and well, the saloon's tables and piano - all objects now: `arcade_cabinet` (a `joystick` billboard on its controls, three games on the screens), `vending_machine` (its window and hatch let in as recesses, `_recess`), `well` (new rock `fieldstone`, rock keys `joint`, `mottle`, `dome`), `crate`, `barrel`, `card_table`, `saloon_chair`, `piano` (new props `whiskey`, `candle`, `candle_lit`); the `market_stand` heaps its trays in 3D (`PRODUCE`, `_mound`) and takes `paint` and `goods`, and a second stand, blue, joined the village. The neon street's machines went 3D too. And the user's catch on the headland temple: thin streaks of sky down the broken columns - a broken column's faces were laid with their top corners raised straight up off the taper, so each sat a hair off its true plane and the faces gaped where they met. Each face is now a panel in its own plane, solid in every texel it reaches into, as the standing columns' faces were.
- **2026-10-21, kelp, knees and rubble.** Kelp (three, and the kelp fringe stamps one per frond), cypress knees and rubble drawn three ways. The saguaro, banana plant and driftwood were tried and left: their seeds barely touch the drawing (the driftwood's not at all).
- **2026-10-21, and the small plants.** Cattails, flowers, poppies, monstera, prickly pear and tumbleweed drawn three ways each (another stream for each). Heliconia was tried and left: its stream only jitters a few pixels.
- **2026-10-21, more drawn a few ways.** The bald cypress (three, its limbs set another way; the swamp's edge stamps one per tree), the palm (three), the dead tree (three, forking another way), the log and the stump (three each).
- **2026-10-21, eyes and close shots.** Seen close, the upper lid that ran outward over a pupil on the nose's side made people look cross-eyed; now each eye is a one-pixel pupil with the socket's shade beside it at the top - straight ahead up close, still an eye from across a room. Two close shots in the saloon to show people seen close: `saloon_gambler` and `saloon_barkeep`.
- **2026-10-21, four new characters.** `miner` (a gold-rush prospector: slouch hat, grey beard, red flannel and suspenders, a pick), `viking` (iron cap, braided red beard, fur cloak over a green tunic, leg wraps, an axe), `monk` (shaven, brown robe, rope belt, sandals) and `villager` (red kerchief, green dress, white apron, a basket) - 16x32 grids with back views, drawn in finer pixels like the rest; they take over from the stand-ins in the mine (the cowboy), the fjord (the pirate), the garden (the shopkeeper) and the village (a farmer).
- **2026-10-21, the decoration randomizer.** Props drawn a few ways (`VARIANTS` in a kit: name -> count and draw(k)); wherever one is placed the renderer picks a drawing by where it stands (assets.variant_name), the same every render; a sprite's `variant` pins one, a scene's `"variants": false` turns it off. Drawn so far: `rocks` (redrawn faceted like the 3D boulders, six heaps, greys and browns - the user: the small billboard rocks "could use an update"), `grass_tuft` and `dry_tuft` (four), `fern` (three), `bush` and `bush_autumn` (four), `boulder` and `boulder_snow` (four - the old drawing's sides were cut off by its canvas), `mushrooms` (redrawn with the toolkit, four); the trees - `pine` and `snowy_pine` (four spruces, fuller or leaner), `tree` and `tree_autumn` (three oaks, the crown's lobes set another way), `birch` and `birch_autumn` (three, the second stem leaning another way) - and the forest and jungle fringe cards stamp a drawing per plant (assets.variant_pick), so a wood's edge is no longer seventeen copies of one spruce.
- **2026-10-21, characters in finer pixels.** Every built-in character drawn from its 16x32 grid at twice the resolution and a tenth taller (scripts/charhd.py, new): a torso row and two leg rows said twice where nothing is doubled, scale2x for smooth silhouettes, a finer face (one-pixel pupils, brows, the nose only at its foot), form shading from the upper left; back views the same size; a scene's own character with `"hd": true`. The user: the environments had "blown past" the characters, close-ups "a little too chunky", people "a little bit taller".
- **2026-10-21, the salt flat's heaps.** In 3D: `heap` (new object) - an irregular cone of `salt` (new rock kind: white grains), `fill` so the side away from the noon sun stays white - in place of the dome cards, which read as tents (an open note from the worlds loop).
- **2026-10-21, the clockwork city's gears.** In 3D: `gear` (new object) - a toothed wheel of `brass` (new paint, verdigris in patches), its faces cut to the teeth, rim, spokes and boss, each a shade of its own, the sides of its teeth standing out - in place of the flat `brass_gear` cards on the walls, and one under the tower's clock.
- **2026-10-21, the basalt coast.** A new scene: a causeway of 400-odd hexagonal `column`s of `basalt` (new rock kind: dark, pale on top, each column's joints at heights of its own) stepping down into a `sea` at sunset, organ pipes up the cliff, every column casting. Three tries: backlit, the tops went black (sun moved to the side); `deep_water`'s blue fought the sunset (the `sea` floor mirrors it).
- **2026-10-21, the ancient ruins' shadows.** The columns `"casts": true` (not the architraves: a thing that casts stands in the light as if solid from the ground up, so they would shade the gaps between the columns under them): since they became 3D objects the low sun had thrown no shadow of them; now the colonnade's shadows stripe the sacred way at golden hour and the moon's fall across the paving at night, as the scene was meant to have.
- **2026-10-21, the misty moor.** Its stones in 3D: `standing_stone` (new object) - rough slabs of `menhir` rock (new kind), leaning a little, their tops sloping down from one shoulder, broad faces turned into the circle; the altar a slab lying. Objects can now cast the sun's shadow (`"casts": true`, off by default): the grid-block stones had thrown the long dawn shadows and the shafts in the mist, and without that the fog went flat white.
- **2026-10-21, the sunken temple.** A new scene from pieces already made: the ruins' fluted marble columns and architraves set on the sea floor in the kelp forest's water, coral on the stones, a manta ray, the diver at the marble head. (A 3D moon-base dome of glass was tried just before and dropped: it was no better than the drawn domes.)
- **2026-10-21, the aurora palace.** The last of the fantasy scenes: `crystal_cluster`s of `ice` on beds of snow rock flank the gate, the throne and the lake's shore - every facet bending the aurora, and their pale light making the ice walls and the throne glow where they were dark blocks; doubled in the polished ice.
- **2026-10-21, the autumn garden.** A new scene: a Japanese garden in autumn - a gate of `lime_red` columns and beams with a `lacquer_black` top beam (new paint), `stone_lantern`s (new object: foot, shaft, platform, a firebox lit between four posts, a six-sided roof, a finial), a tea house under `slate`, a pond with a plank bridge and red rails, boulders, maples. First drawn, the camera stood in the gate and the garden read empty: the gate moved up the path to frame the view whole, maples came in close round the pond (one moved out of the second shot's line), and the dusk shot moved onto the path, where the lanterns line the way.
- **2026-10-21, the lighthouse.** The coast's lighthouse was a square tower of wall cells nine high. It is a `lighthouse` object now (new): a round whitewashed tower tapering up, a red band, a gallery with its rail, a lantern room of glass with the lamp lit in it, a domed cap; painted masonry `lime_white` and `lime_red`. The tower shot tilts up a little (`pitch` 0.24) to take in the lantern, with a bloom on the lights.
- **2026-10-21, the palm house.** A new scene: a Victorian glasshouse. Its roof is a `gable_roof` with the new `glass` cover and `glass` ends - painted as panes between white glazing bars with each texel's own opacity and drawn as glass (`translucent`), so the sky shows through, and no cell is roofed, so the sun comes in; painted cast iron for columns and beams (`iron_white`, `iron_green`; `_painted`); a new kit, glasshouse.py, with the `glasshouse` wall and `encaustic` tiles. Palms scaled to 4-5 so their crowns fill the glass. The shot from the garden was dropped: walls of open panes read as a cage from outside.
- **2026-10-21, the fjord.** A new scene, the north: a `longship` object (new - the hull with its stem and stern curling up, a mast, a yard and a striped square sail, round shields along both sides), `round_shield` (new, norse.py), cliffs lined with tall ragged `stone` rock walls, a longhouse under a thatch `gable_roof`. First drawn, the cliffs' trim was low and they read as castle walls (`trim` 0.14 now, for a ragged rim), the dusk shot looked at nothing and the third sat inside the ship - now dusk is the fire lighting the shields and the third looks back from the water. Pines on the cliff tops were tried and dropped: the rock walls stand taller than the cells they line, so they hid them.
- **2026-10-21, the woods' edges.** The woodland, the autumn lane and the winter woods take the jungle's natural edge: their fringes `wander` (0.3, 1.2 deep), so the forest's flat wall faces stop showing between the layers at its corners - most in the winter woods, where the lane's straight green walls are now trees. The other shots change little.
- **2026-10-21, alien crystals.** The alien world's two billboard crystals by the glowing pool became `crystal_cluster`s in 3D, cyan and violet, and two more stand at the foot of the plateau's step - the monolith shot is framed by them, their light on the step, every facet bending the view. (The waterway's rowboat was tried as a small `ship_hull` and kept as the billboard: seen at that distance the drawn boat, oars and all, reads better.)
- **2026-10-21, the great hall.** The castle's throne room had square pillars of wall cells, out of both gallery shots. They are round now - 12-sided `column`s of `ashlar` with bases and capitals - with timber `beam`s across the hall over them under the ceiling; the throne shot is kept as it was, and a new one, `castle_hall`, from the hall's foot, has the pillars and beams framing the throne (the castle has no scatter, so a new shot moves nothing).
- **2026-10-21, the cabin on the ice.** The winter lake's cabin, a flat-topped box, wears a roof under snow (`snow` cover, new: `_snow_roof` - drifts, the shingles at the ridge, a lip at the eave) with grey wood smoke rising from its chimney, and the blocks round the shore are `boulder`s of `snow` rock; a new shot, `winter_cabin`, close by day, turned by angle and pitch so the scatter stays. The window lamps lit the roof's top in scallops - the lamps' light is mapped on the floor, so anything over them takes it all - so a roof's top takes a quarter of it (`dyn` on a panel, `ROOF_LAMPS`): the village's inn at night and the ghost town at dusk have darker, moonlit roofs over their lit fronts.
- **2026-10-21, roofs for the old houses.** The haunted house and the churchyard chapel were flat-topped boxes - the village's fault, the user's word was 'roofless'. Both have steep roofs of `slate` in 3D (a new cover: dark blue-grey, narrow courses): the house's with two brick chimneys (`chimney` takes a list; chimneys grow stouter on a bigger roof) and the tower's own gable, the chapel's with its front gable in pale stone (`ends`, new: gable ends of a rock kind). Inside, the ceilings hide the roofs: the interior shots are unchanged to the pixel.
- **2026-10-21, the wreck.** After the user's list and the fantasy refresh, a look over the scenes not touched today: the kelp forest's wreck was a ring of plank walls round a low block, its rock outcrops blocks too. A new object, `ship_hull` - planked and ribbed, stern, curving sides, a bow whose stem sweeps up, `heel` and `broken` - lies listing in the sand turned toward the cameras (broadside on, at first, it read as a wall), and the outcrops are boulders of live reef rock.
- **2026-10-21, the hall of doors.** The fantasy refresh, fifth: its walls of doors were flat paint. Now a pilaster of cream marble stands between every two doors, on a base, and a cornice runs along every storey - 90 `column`s and 6 `beam`s - so the corridor's rhythm stands out and catches the light down its length.
- **2026-10-21, the drowned library.** The fantasy refresh, fourth: its ceiling was one flat dark plane - now dark timber roof beams cross the hall between the skylights, on brackets at the shelves, catching the light from the holes; the ambient a little higher and the fog a little thinner, so the shelves read.
- **2026-10-21, the dream world.** The fantasy refresh, third: keels under the dream islands, the chequered island's pieces in 3D; the stair to nowhere shot from out over the void (from the next island its keel was hidden behind that island's floor), so the island visibly floats, the whale and the eye still over it.
- **2026-10-21, the chess set.** The fantasy refresh, second: the chequered plain's giant chess pieces were billboards. Now `chess_piece` objects: turned from a profile of (radius, height) points, smoothly shaded round (a convex `tilt`: the normal swings across each face as round a cylinder), in polished marble with a sheen and veins - the floor mirrors them. The knight is a head carved side on from a slab, so it is turned a little off the cameras' lines; seen head on it is only the slab's thickness. Its head first faced inward (its panels' winding), so the white knight's head was dark.
- **2026-10-21, the sky islands.** The fantasy refresh, first: the islands' keels in 3D (`keel`, new: rings of triangles drawing in to a point, crags hanging off them; a new `island` rock kind, and any rock kind can be painted coarser with `density`), and the temple's ring of billboard columns a ruined tholos of fluted Doric `marble` columns with an entablature over the pairs that stand. Tried and dropped: a ring of `rock_wall`s round every island - from the meadows it walled the view in, and the islands lost their look of floating meadows.
- **2026-10-21, inside the temple.** The third new scene: inside the jungle pyramid. A small kit, temple.py: a `golden_idol` and `treasure`; the pillars and altar are `column`s and a `beam` of stone. One roof cell left open, a sun at 72 degrees through a thick fog with strong shafts, makes the column of light; at first the sun came from the wrong side of the hole and missed the altar (azimuth 100 lit the floor behind it), and the room was too murky to read.
- **2026-10-21, the gold mine.** The second new scene: a frontier gold mine. A kit, mine.py: `mine_rock` (and with a seam of quartz, and with gold in it, glinting), a pick and shovel, a dynamite crate, an ore heap; objects `rails` and `ore_cart`; the timber sets are `column`s and `beam`s of wood. Lessons: a vein drawn on every tile repeats as a graphic zigzag - it is a gentle wave that joins tile to tile now, on a few cells only; and a wall taller than the ceiling is drawn its full height, over the ceiling (the stope showed its seam twice and no roof), so the mine's inner rock is exactly the roof's height and the hill outside is cells of its own, with a rock wall lifted over the portal. scene_format's `ceiling_height` row said walls should be 'at least' that tall: now 'exactly'.
- **2026-10-21, the saloon.** The first of the user's new scenes: inside the frontier town's saloon. A new kit, saloon.py: wainscot and flocked paper, the back bar's bottles and mirror, open-paned windows, a pressed-tin ceiling, a piano, a card table, a bentwood chair, a spittoon, a wanted poster; and a `saloon_bar` object in 3D. First drawn 14 by 10 cells it was a hall forty metres long - a unit is nearly three metres - so it is 8 by 6 under a 1.6 ceiling; the windows looked dark until the store across the street went (its shaded front was all they showed); the noon shot looks across the beams toward them.
- **2026-10-21, the village's roofs.** The user's eleventh: the village's houses read as roofless and flat, the market cart a billboard. The timber style now has a `body` (2.8): the facade code builds each house's roof as a `gable_roof` - behind a gable end, running back from the street with its slopes on the gable card's edges (the card stays the front); over an eaves house, along the street with its eaves 0.15 out over the front (its slope card is gone) and a chimney where the card had one - on plastered walls (`plaster`, the house's colour, `buildings.house_color`) up from the block, inset behind every facade layer (`inset` takes four sides now). New roof covers `thatch` and `tile` (painters `_thatch`, `_tiles`; `ROOFS`, with brick for chimneys), `overhang` per eaves and ends. `market_stand`: a trestle table of boards with a striped skirt (the valance's stripes), an awning on four poles, goods heaped on it (`goods_apples`, `goods_cabbages`, `goods_loaves`, new in village.py) - the keeper kept out in front, where the approved shot had him; behind the table the bubble lost him. `_timber` is never wet (its wet line was measured from the roof's eaves).
- **2026-10-21, the frontier town.** The user's tenth: depth for the ghost town's buildings, its trough in 3D, the porch frame filled, the mountain walls redone. Three timber objects: `trough`, `shed_roof` and `gable_roof` (with `walls` and `inset`), all of boards - `_wood` gains `boards`: a seam between each and each its own tone, the seams lining up across panels. The facade code builds objects now (World.panels, drawn with the scene's): a western porch's roof (a ceiling at the fascia's height is hidden behind the fascia from the street, so the porch read as a bare frame; a roof sloping down to it shows), and behind each false front its building, a gabled roof low enough for the front to hide from the street (`body`, 5 cells back). The body's walls stand behind every facade layer - first built on the facade's own plane, they covered the windows. Mesas: R lined with `canyon` rock walls, the old walls cut to 5.
- **2026-10-21, the jungle's edge.** The user's ninth: the jungle temple's tree line natural and polygonal, not the grid's. Its fringe now `wander`s, 1.4 deep, round the clearing and down the path under the canopy; and the canopy walls within two cells of open ground are all at its lowest height, because their steps (2.5 to 4 in 0.3s) showed between the trees as clipped hedges from the pyramid top. The temple shot is all but unchanged.
- **2026-10-21, the bayou's trees.** The user's eighth: the swamp's layers spread further apart. A fringe can now `wander`: each layer one line the same distance out from the forest all along (marching squares on the distance from it, sampled four to a cell), round at the corners, wandering in and out on smooth noise, cut into straight cards (`_chords`: never under 0.6, so a sharp bend makes no sliver - a slice of forest seen face on reads as a tower) that carry the picture on from one to the next and fade out seen almost edge on (`edge_fade`, new). Layers stop at other walls; all but the back one keep 0.75 clear of them, so the shack has trees behind it and none squeezed beside it, and pieces broken where a layer grazes a corner are joined (no slit of sky). The swamp set in four layers, its back stand denser and taller so the wall's flat top never shows, and without the floating moss.
- **2026-10-21, the temple's columns.** The user's seventh: the ancient ruins' columns in 3D. `column` gains `flutes` (every face hollowed: its normal bends across it, `tilt` in _stone, so it takes the light on one side and shadow on the other) and `"doric": true` (an echinus - frustums can now widen upward - under a square abacus); a `marble` stone in drums. The peristyle's painted see-through colonnade walls became columns on the stylobate with architraves and cornices (`beam`) over every run of three that still stand; the sacred way's and the fallen groups' columns too (prefabs can now carry `objects`). Backlit by the low sun the columns went black, so objects take `fill`: light from the sky and the ground on the faces the sun misses, a multiple of the scene's ambient, so it dims at night. A fluted column is one stone round: every face cut from the same block, so a drum is one tone and its patina runs on round it (cut a face at a time, the patches stopped at the faces' edges and read as holes); marble seldom cracks. New shot `ruins_columns`, the fallen group in the sun from the west - turned by `angle` and `pitch` and stood where no scatter is, because a shot keeps scatter off its camera and its sight lines and a new one reshuffled the poppies out of `ruins_head`. The statue's head is still a billboard.
- **2026-10-21, the cathedral's arcades.** The user's sixth: the nave on two rows of octagonal stone piers moved in from the walls to carry the roof - `column` objects in a new `ashlar` stone (pale, laid in courses, `courses`, so a column reads as drums), with plinths and capitals - carrying timber wall plates, a new `beam` object; the pier where the roof fell in broken off (`broken`: each corner stops at its own height, the break a fan of rough triangles) and a length of its plate down on the floor. Shot 2's camera moved into the aisle and the pews behind the cameras, so the arcades and the light read.
- **2026-10-21, the canyon's cliffs.** The user's fifth: the red canyon's walls built in 3D - every face lined with a tall `rock_wall` of a new `canyon` rock kind (its stone in beds by height, `strata`, with dark `varnish` streaks running down), over the old banded walls cut down to cores - so the cliffs jut, step and catch the light by facet, and the rim is ragged. The slot canyon is unchanged.
- **2026-10-21, the bar's reef tank.** The user's fourth: the neon bar's tank done as the aquarium is, small - open water behind (`deep_water` and `open_water` at 0.62 brightness, so it does not outshine the bar), low live rock along the back (`rock_wall` with `lining`) and one small boulder, the reef rocks and corals kept in front for the density the user likes.
- **2026-10-21, the beach.** The user's third: the pier on wooden piles, down both edges and taller at its end - a new `column` object (any number of sides, taper, plinth and capital, stone or `wood`), built with the cathedral's and the ruins' pillars in mind - and the jungle behind the beach given the `jungle` fringe, so the tree line has depth.
- **2026-10-21, boulders on the moor and the coast.** The first two of the user's list: 3D boulders in place of billboards on the misty moor (framing the wanderer in the first shot) and round the lighthouse. Fixed on the way: the light painted on rock turned with each object, so a boulder placed facing north was dark on the side the camera saw; it is now a direction in the world, the same for every rock in a scene (objects at angle 90, most of the aquarium, render exactly as before).
- **2026-10-21, rock elsewhere and crystals.** Rock walls take `lining` (map characters: a rock wall along every straight run of their faces onto open ground) and three more kinds, `snow`, `cave` and `lumen` (glowing moss). The red canyon's walls are lined with fallen sandstone, with sandstone boulders in the wash; the night wood, the autumn lane and the winter woods have 3D boulders (mossy, ferns on top; snow-capped in winter) in place of billboards. Crystals refract, as the user designed it: `crystal_cluster`, each facet its own panel with its own clarity and its own shift of what is behind it (Renderer._bend). The crystal cave rebuilt round them, with the glowing jungle's plants; new shots `crystal_cave`, `crystal_violet`, `crystal_close`.
- **2026-10-21, rock.** Rock built in 3D out of panels, as the user laid it out: `rock_wall` (overlapping pieces along a wall's foot, each a rounded mass of broad faces in plan, each its own height, a trim of faces along the top cut by one long wavy edge, a flat top, plants on the rim) and `boulder` (a low-poly mass of triangles), in three kinds - `stone`, `reef` and `sandstone`. Every face is cut from one solid block (`pixelart.cells3` and `noise3`): masses, a few fractures, chips and pits sampled at each texel's place in 3D and lit by the way the face faces, so the stone runs on round a corner. The aquarium's big tanks have rockwork along their walls and boulders on the sand, the walls behind painted as `open_water` over `deep_water`; a new shot, `aquarium_rockwork`, from inside the ocean tank.
- **2026-10-21, objects.** `scripts/objects.py`: things too big for a billboard built in 3D out of flat panels the renderer draws in true perspective, depth-tested per pixel and lit like walls - a `car` and a `noodle_stand` - with `noodle_bowl`, `stock_pot`, `bowl_stack` and `condiments` for its counter. Cars in the rain alley, the stand in the neon street; new shots `alley_cars` and `neon_counter`.
- **2026-10-20, held items in 3D.** The six held items were drawn from the wrong side - the hand facing the player, the revolver muzzle-on. Now each is a small 3D model (scripts/sculpt.py: rounded primitives as distance fields, ray-marched from the eye, painted on the colour ramps with dithering, contour lines and an outline) posed in a hand and seen as its holder sees it; their canvases reach the screen edge so the sleeve runs off it.
- **2026-10-20, the polish list.** The six held items redrawn in held.py (a shaded hand of four fingers, knuckles and a thumb, out of a coat sleeve); `stain`, `stain_rust` and `moss_patch` redrawn; `bamboo`, `thatch`, `canopy` and the `islands` skyline touched up; `foam`, `foam_glow` and the `plaster` facade style judged fine. Nothing is left on the polish list.
- **2026-10-20, salt piles and the aurora.** `salt_mound` redrawn round-topped and smaller (0.22), with `salt_heap`, `salt_pile` and `salt_clods` beside it - the salt flat's rows now mix them, no two the same size. The `aurora` varied: rays of every width and height in bundles, a pleated ribbon, red-tipped rays, a high arc. Reflections: a still mirror (`smear` under 1) now mirrors each thing about its own foot.
- **2026-10-20, second passes.** `aurora_shore` re-shot from the lake's western shore: the palace and its spires under the aurora, a pine and the ice edge framing it (it was a dark view with the palace small on the horizon).
- **2026-10-20, the clockwork city.** `scripts/clockwork.py`: `brass_plate`, `copper_pipes`, `clock_face`, `brass_gear`, `great_clock`. `examples/clockwork_city.py` with four gallery shots; its orrery is brass wireframes.
- **2026-10-20, the aurora palace.** `scripts/icepalace.py`: the `aurora` sky (drawn into the panorama by `draw_aurora`), `ice_block`, `frost_wall`, `ice_floor`, `ice_spire`, `ice_throne`, `icicles`, `ice_shards`. `examples/aurora_palace.py` with four gallery shots.
- **2026-10-20, the glowing jungle.** `scripts/glowjungle.py`: glowing variants of the jungle plants (a rim of light round every leaf, flowers by their colour), `glow_pods`, the `glow_jungle` fringe, `glow_leaves`, `lumen_floor`, `glow_water`. `examples/glow_jungle.py` with four gallery shots.
- **2026-10-20, the sky islands.** `scripts/skyisles.py`: `meadow`, `island_rock`, `waterfall`, `island_roots`, `island_keel`, `rope_rail`. A cell key `cliff` (how deep an edge drops into a void). `examples/sky_islands.py` with four gallery shots.
- **2026-10-20, the salt flat.** `scripts/saltflat.py`: `salt_flat`, `salt_water`, `salt_brick`, `salt_mound`. Reflections: `smear` (0 for a still mirror), and below 1 the sky past a figure is mirrored about the horizon and dry ground counts as flat. `examples/salt_flat.py` with five gallery shots.
- **2026-10-20, Vector World.** `scripts/wires.py`: `wireframes`, low-poly meshes drawn as lines of light in true 3D (19 built-in shapes, or your own vertices and faces; `solid` fills the faces black so they hide what is behind). `scripts/vector.py`: seven black textures ruled in light, the `vector_runner`, `light_trail`, `light_beam` and `glint`; the `vector` sky and a striped sun (`disc_style`). `examples/vector_world.py`, with five gallery shots - the racers' headlights streak like an anamorphic lens, a beacon throws a lens flare.
- **2026-10-20, light and lens.** A point light fades above its own height (`Renderer.fade_z`): a lamp hung high lights the walls round it, and one set on a roof lights the roof round it (`build_lightmap` keeps a map for roofs, where the light passes over what lies below the line to it). Depth of field takes its palette from the frame without the lens, so a sharp subject keeps its colours. New `streaks` (a star filter's twinkle, or an anamorphic lens's long lines) and `flare` (from a sun or moon in the frame) effects; fireflies, embers, spores, held lanterns and muzzle flashes feed a light bloom. A light bloom on the night shots of the bayou, the autumn lane, the haunted house, the woods, the castle, the village, the frozen lake, the crystal cave, the churchyard, the ruins and the beach; streaks on the neon street and the train; `beach_flare`, a new shot into the sun. The hall of doors' lamps hang lower (1.8) and the rooftop runner's tint is softer, since both were set against the old falloff.
- **2026-10-20, doomed.** `scripts/doomed.py`: a 1993 shooter's status bar (`statusbar` widget: stone, red digits, arms, a face that bloodies with health, keys, ammo table), a `message` line, the `pistol` and `shotgun` held in the middle with `fire`, the `doomed` theme; the slime pit's textures and props. `examples/doomed.py`, an homage to the first level, with four gallery shots.
- **2026-10-19, glow and focus.** The renderer keeps an emission buffer beside the frame; `bloom` takes `source: light` (only what gives off light, with a wide halo) and the neon scenes use it; a new `dof` effect (depth of field) on the close shots of the samurai, the hacker, the cat, the sleepwalker and the diver. Scenes that do not opt in render byte-identical.
- **2026-10-19, the child.** A narrower head with a fringe, eyes closer, a small mouth, a tapered chin; the galleries of the six scenes the child appears in rebuilt. Rated good.
- **2026-10-19, the column drum.** Flutes along its length, a lit end face on a shadowed rim; the ruins' and the cathedral's images rebuilt. Rated good.
- **2026-10-19, the goat.** Redrawn with the toolkit in basics.py (it overrides the old grid), short-legged and piebald; the ancient ruins' images rebuilt. Rated good.
- **2026-10-19, the sleepwalker's eyes.** `dreamer`: closed eyes; the galleries she appears in are rebuilt. Rated good.
- **2026-10-19, the capsule hotel.** bar.py: `capsules` and `capsules_lit`. `examples/capsule_hotel.py`: a corridor one cell wide between walls of berths, with four gallery shots.
- **2026-10-19, the moon jellies and the diver.** Two more aquarium shots: moon jellies glowing in a tank lit low and violet (a tinted `jelly_backdrop`), and the diver behind the glass with a sunbeam on the sand. A sprite behind glass no longer counts as hidden in the render report.
- **2026-10-19, sunbeams in the tank.** A `glazed` cell key: the roof is drawn but the sun and moon shine through it (existing scenes unchanged: none glaze). The aquarium glazes a few cells of its water surface, and the sun comes down into the big tank in beams.
- **2026-10-19, two for the neon city.** Characters `samurai` and `hacker` (16x32, with back views): the samurai walks the night market under an umbrella, the hacker works in a booth of the neon bar.
- **2026-10-19, the rooftops.** `scripts/rooftop.py`: `water_tower`, `ac_unit`, `rooftop_sign`, `sky_train`, `black_cat`. `examples/neon_rooftop.py`: the camera on a tower 5 tall at the end of a neon street, with four gallery shots. Noted: point lights fade with absolute height, so a high roof is lit by ambient and emission only.
- **2026-10-19, the neon bar.** `scripts/bar.py`: `arcade_cabinet`, `bar_counter`, `bar_stool`, `booth`, `jukebox`, `neon_cocktail`, `neon_fish`, `bottles` and the `bar_shelves` texture. `examples/neon_bar.py` (a reef tank in the back wall, with fog behind its glass) with four gallery shots.
- **2026-10-19, the night market.** `scripts/market.py`: 11 props (a food cart, fruit and gadget stalls, red lanterns and a string of them, a standing neon sign, a lit umbrella, a scooter, stools and a table, a utility pole, a crowd). buildings.py: a face too narrow for a door or a window gets none instead of crashing (the existing facade scenes render byte-identical). `examples/night_market.py` with four gallery shots.
- **2026-10-19, the aquarium.** `scripts/aquarium.py`: 17 props (a whale shark, a manta, a reef shark, a turtle, reef fish, corals, jellies, a plaque) and `reef_wall`, `tunnel_roof`, `jelly_backdrop`, `tank_window`. Glass takes `fog`, so volumetric fog carries on behind a pane (existing scenes render byte-identical). `examples/aquarium.py` with five gallery shots.
- **2026-10-19, the occult library.** mansion_library: raised to 2 units under a panelled ceiling, shelves two storeys high, and furnished - a reading desk with the spiritualist at it, an armchair, a globe, a telescope, the grandfather clock, lit candelabras, a portrait, cobwebs, books flying. Every example scene is now rated good.
- **2026-10-19, the hall of doors.** dream.py: `door_hall`. `examples/hall_of_doors.py`: doors in every wall at every storey and in the ceiling, tinted per cell, a few open onto the sky, with four gallery shots.
- **2026-10-19, the waterway.** underground_waterway: a thinner fog with `glow`, lanterns at the far end, so the channel reads in depth. winter_lake and coast_lighthouse re-rated good: their ice, snow, sand, water and rocks were all redrawn earlier today.
- **2026-10-19, the fallen roof.** cathedral_ruin: rafters across the hole in the roof (`log` cards at the ceiling) with ivy hanging from its edges, column drums, a broken column and rubble under it, grass in the light, and the beam shot moved out of the pews into the aisle.
- **2026-10-19, the throne hall.** castle_keep: the camera closer, a larger throne under a great stained-glass window, banners and candelabras on the dais, guards at the foot of the steps, the knight to one side.
- **2026-10-19, the stone circle.** `menhir`, `menhir_top` and a `stone_cap` prop: the misty moor's stones get varied heights, weathered faces and slanted, chipped tops instead of flat-topped blocks.
- **2026-10-19, polish pass 4.** `alien_rock` (faceted, glowing in its crevices), `alien_ground`, `dry_grass` (fewer, larger clumps), and the `jaguar` redrawn prowling side on in rosettes.
- **2026-10-19, the Moon.** An `earth` sky object; `scripts/moon.py`: `regolith`, `rover_tracks`, `dome`, `hab_module`, `solar_array`, `rover`. `examples/moon_base.py` with four gallery shots.
- **2026-10-19, the haunted house.** `scripts/haunted.py`: `cobweb`, `candelabra`, `portrait`, `grandfather_clock`, `balustrade`, `bats`. `examples/haunted_house.py`: a grand staircase from the `heights` layer up to a landing with a balustrade, four gallery shots.
- **2026-10-19, polish pass 3b.** Redrawn with the toolkit in `scripts/basics.py`: `curtain`, `curtain_black`, `acoustic`, `ceiling_plaster`, `corrugated`, `marble_dark`.
- **2026-10-19, polish pass 3.** Redrawn with the toolkit in `scripts/basics.py`: `bed`, `wheelchair`, `table`, `chest`, `glowshroom`, `buoy`, `alien_egg` (its veins glow, so a dark hive still reads as a field of eggs).
- **2026-10-19, winter woods.** forest.py: `tree_winter` (recursive bare branches with snow along them), `birch_winter`, `bush_snow`, `deer`, `forest_deep_snow` and a `forest_snow` fringe (the green and autumn wood unchanged, hashed); `snow` redrawn. `examples/winter_woods.py` with four gallery shots.
- **2026-10-19, the ghost town.** A `western` facade style: clapboard false fronts with painted signs (drawn with the pixel font, shuffled along each street), batwing doors on the saloon, and a `porch` layer - posts and fascia out at the edge of a boardwalk whose `ceil` is the porch roof. desert.py: `windpump`, `water_trough`, `wagon_wheel`. `examples/ghost_town.py` with four gallery shots.
- **2026-10-19, under the sea.** `scripts/sea.py`: `seabed`, `water_surface`; `kelp`, `fish_school`, `bubbles`, `anchor`, `wreck_mast`; a `kelp` fringe and a `seabed` scatter set; the `diver`. `examples/kelp_forest.py` with four gallery shots.
- **2026-10-19, polish pass 2b.** Redrawn with the toolkit in `scripts/basics.py`: `rock`, `rock_wet`, `rock_floor`, `snow_rock`, `ice`, `sand`, `plaster`, `plaster_white`, `ivy`.
- **2026-10-19, polish pass 2.** Redrawn with the toolkit in `scripts/basics.py`: `shingle`, `cobble`, `beams`, `rowboat`, `bench`, `flowers`, `statue` - all of them in many scenes.
- **2026-10-19, four more characters.** `cowboy`, `witch`, `farmer`, `pirate` (16x32, with back views), put to work in the canyon, the autumn lane at dusk, the village green and the bayou.
- **2026-10-19, the bayou.** `scripts/swamp.py`: `swamp_water` (mirrors), `bog`, `swamp_deep`; `bald_cypress`, `spanish_moss`, `cypress_knees`, `cattails`, `heron`, `alligator`, `fireflies`; a `swamp` fringe and scatter set. `examples/bayou.py` with four gallery shots.
- **2026-10-19, the desert.** `scripts/desert.py`: `sandstone`, `sandstone_pale`, `slot_rock`, `desert_wash`, `pueblo_stone`, `pueblo_door`; `saguaro`, `prickly_pear`, `tumbleweed`, `cow_skull`, `clay_pot`; a `desert` scatter set. `examples/red_canyon.py` (a slot canyon lit through one gap in its roof) with four gallery shots.
- **2026-10-19, the village.** A `timber` facade style (`scripts/buildings.py`): oak framing drawn over plaster to fit each building's windows, leaded casements, plank doors, and a new `roof` layer the renderer stands on each house - a gable end, or thatch or tiles set back behind the eave, chimneys - the other styles' images unchanged. village.py: `well`, `cart`, `market_stall`, `inn_sign`. `examples/village_green.py` with four gallery shots.
- **2026-10-19, autumn.** The forest turned: `tree_autumn`, `birch_autumn`, `bush_autumn` (recoloured in patches from the green ones, which stay pixel-identical), a `forest_autumn` fringe, `forest_deep_autumn` and `leaves_fallen`, an `autumn` scatter set. `scripts/village.py`: `scarecrow`, `pumpkin`, `jack_o_lantern`, `hay_bale`, `crow`. `examples/autumn_lane.py` with four gallery shots.
- **2026-10-19, snow on the spruce.** `snowy_pine` redrawn from the new spruce, and a `boulder_snow` for winter shores, with a `snow` scatter set to use it (the `stones` set's boulders are mossy); winter_lake uses it.
- **2026-10-19, everyday things.** The oldest textures and props, which turn up in a great many scenes, redrawn with the toolkit in `scripts/basics.py`: `grass`, `hedge`, `dirt`, `gravel`, `wood_panel`, `water`, `barrel`, `broken_barrel`, `crate`, `fountain`.
- **2026-10-19, the drowned library.** Sunlight now comes down through skylights - holes in a roof with more roof beyond them, which the roof test used to treat as roofed (the cathedral's beam through its fallen roof got brighter and truer with it). dream.py: `tall_window`/`tall_window_top`, `jellyfish`, `sky_lantern`, `book_fly`. `examples/drowned_library.py` with four gallery shots.
- **2026-10-19, the chequered plain.** `scripts/dream.py`: a marble chess set turned on a lathe (pawn and king redrawn, rook, knight, bishop and queen new), `melting_clock`, `hourglass`, `stone_arch`, `stair_float`, `paper_boat`, the `checker_marble` floor, and a `clock` sky object that melts. `examples/dream_chess.py`: a giant unfinished game on a floating plain, with four gallery shots.
- **2026-10-19, the neon street.** A `neon` facade style (`scripts/buildings.py`): concrete, neon signs drawn into the wall layer, which now returns a glow, blade signs standing out over the street (a new `blade` layer, placed by the renderer), shutters and tinted rooms - the other styles' buildings unchanged. Street props in scifi.py (`vending_machine`, `noodle_stall`, `steam`, `holo_ad`, `wires_span`), the `runner`, and `examples/neon_street.py` with four gallery shots.
- **2026-10-19, the orbital hangar.** `examples/orbital_hangar.py`, a scene of several rooms built from the sci-fi hardware: the bay with its shuttle, loader and robot arms behind real glass onto a ringed planet, a control room looking down the bay, and a reactor room in cyan haze under red alarms. Gallery: `hangar_bay`, `hangar_pilot`, `hangar_control`, `hangar_reactor`.
- **2026-10-19, sci-fi hardware.** `scripts/scifi.py`: `hangar_floor`, `conduit` and `screen_wall` textures, `pad_marking` and `hazard_stripe` decals, and a `shuttle`, `cargo_container`, `power_loader`, `beacon`, `reactor_core`, `robot_arm` and `cables_hang`, all drawn with the toolkit, lights and screens writing an emissive mask.
- **2026-10-19, the forest, part 2.** The original woodland rebuilt: the `forest` fringe in front of low `forest_deep` walls (a new texture: trunks receding into the dark), trees standing free along the road, a real moon in volumetric fog instead of blue point lights, and two new shots, first light through a gap in the trees and a ghost on the moonlit road (`woods_dawn`, `woods_moon`). `boulder`, `stump`, `log` and `dead_tree` redrawn with the toolkit.
- **2026-10-19, the forest, part 1.** `scripts/forest.py` draws the temperate forest with the toolkit: a spruce (`pine`), an oak (`tree`), a new `birch`, the `bush`, and the `foliage`, `foliage_autumn`, `bark`, `bark_pine`, `pine_needles` and `moss` textures, replacing the flat first versions. A `forest` fringe set (`forest_card_1`-`4`) stands layered spruce, oak, birch and undergrowth in front of a wood's walls, so its skyline is tree tops.
- **2026-10-19, reveals.** A card can have a `reveal` (a thickness): through its openings, seen at an angle, it draws their far sides - jamb, head, sill - folded from its own colours and lit by their own facing, with the wall's shadow in them. Facade walls use it, so a window or door seen from the pavement shows its brick sides instead of a sliver of the lit room behind.
- **2026-10-19, glass and facades.** A glass pass: panes drawn after everything else, showing what is behind them through the frame shrunk to half size and blown back up (a cheap blur), tinted light blue, under a faint reflection. Building `facade`s: a block's fronts cut into separate buildings of varied height, brick and paint, each in five layers - wall, frames, glass, drapes, rooms - so windows have depth. Rain alley rebuilt as a wider street with a road, pavements and a T-junction.
- **2026-10-19, planes, fringe and prefabs.** Sprites can stand as fixed planes in the world: one card, a cross of two or a star of three, and the low plants do so by default. A `fringe` wall stands layered foliage cards in front of its open faces (four jungle cards, sparse to dense). Prefabs place named groups - sprites, lights, decals, scatter, nested prefabs and patches of map - with one line; 13 built-ins. The jungle temple was rebuilt round the fringe; the beach and the ruins use prefabs.
- **2026-10-19, jungle, ruins and beach.** A pixel-art toolkit (`scripts/pixelart.py`: shapes in a height field, one light, hue-shifted ramps, shadow-side outlines) and `scripts/biomes.py`, drawn with it: 23 textures, 31 props (5 of them hand-drawn animals), 6 decals, 3 characters, the `sunset` and `golden` skies, the `islands` and `jungle` skylines, three scatter sets and three scenes. `palm`, `column`, `fern`, `grass_tuft` and `rocks` were redrawn the same way.

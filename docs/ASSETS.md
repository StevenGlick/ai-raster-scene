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
| Textures | 197 | 197 | 0 | 0 | 0 |
| Props | 306 | 306 | 0 | 0 | 0 |
| Characters | 29 | 29 | 0 | 0 | 0 |
| Decals | 27 | 27 | 0 | 0 | 0 |
| Skies | 13 | 13 | 0 | 0 | 0 |
| Skylines | 6 | 6 | 0 | 0 | 0 |
| Sky objects | 7 | 7 | 0 | 0 | 0 |
| Scatter sets | 18 | 18 | 0 | 0 | 0 |
| Fringe sets | 7 | 7 | 0 | 0 | 0 |
| Facade styles | 6 | 6 | 0 | 0 | 0 |
| Prefabs | 13 | 13 | 0 | 0 | 0 |
| Objects | 14 | 14 | 0 | 0 | 0 |
| Held items | 8 | 8 | 0 | 0 | 0 |
| Icons | 26 | 26 | 0 | 0 | 0 |
| GUI themes | 6 | 6 | 0 | 0 | 0 |
| GUI widgets | 18 | 18 | 0 | 0 | 0 |
| Post presets | 20 | 20 | 0 | 0 | 0 |
| Palettes | 9 | 9 | 0 | 0 | 0 |
| Example scenes | 63 | 63 | 0 | 0 | 0 |
| **all** | **793** | **793** | **0** | **0** | **0** |
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

- [ ] A saloon interior, in the frontier town.
- [ ] Inside a mine, in the same wild west.
- [ ] Inside the jungle temple.

## Textures (197)

64x64 tiles, drawn in code. "glows" means the texture lights itself (windows, screens, runes), "see-through" that the map shows through its holes, "mirror" that floors made of it reflect.

### Masonry and plaster

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `brick` | good |  | rainy_street |  |
| `brick_dark` | good |  | clockwork_city, neon_bar, neon_rooftop, neon_street, night_market, rain_alley |  |
| `brick_yellow` | good |  | - |  |
| `stone` | good |  | claude_study, garden_encounter, gui_menus, hospital_garden, post_presets | Even block sizes; a few varied heights would help on long walls. |
| `stone_dark` | good |  | cathedral_ruin, garden_encounter, gui_menus, gui_themes, gui_trade, haunted_house, hospital_garden, library_medium, mansion_library, post_presets, rainy_street |  |
| `stone_pale` | good |  | cathedral_ruin, chapel_graveyard, coast_lighthouse, dream_world, garden_encounter, gui_menus, hospital_garden, post_presets |  |
| `castle` | good |  | castle_keep | Mortar grid is very regular; chip a few corners. |
| `moss_stone` | good |  | autumn_lane, coast_lighthouse, misty_moor |  |
| `menhir` | good |  | misty_moor | Drawn with the toolkit in basics.py: one weathered stone face - broad swells, rain runnels, long cracks, lichen rosettes - moss at its foot. |
| `menhir_top` | good |  | misty_moor | Drawn with the toolkit in basics.py: the upper courses of a standing stone: greyer, more lichen, no moss. |
| `slime_brick` | good |  | sewer_tunnels |  |
| `plaster` | good |  | rainy_street, village_green | Redrawn with the toolkit in basics.py: smooth render mottled where patched, a hairline crack, faint streaks; no band, so it stacks storey on storey. |
| `plaster_white` | good |  | garden_encounter, gui_menus, hospital_garden, post_presets | Redrawn with the toolkit in basics.py: the same render in white. |
| `hospital_wall` | good |  | ghost_corridor, gui_hud, hospital_corridor |  |
| `ivy` | good |  | rainy_street | Redrawn with the toolkit in basics.py: red brick with woody stems climbing and branching and clusters of dark leaves, the newest brighter. |
| `concrete` | good |  | aquarium, bunker_lab, capsule_hotel, garden_encounter, gui_lantern, gui_menus, hospital_garden, neon_bar, neon_rooftop, post_presets, sewer_tunnels, tunnel_encounter, underground_waterway |  |
| `marble` | good |  | cathedral_ruin, chapel_graveyard, dream_chess, dream_world, gui_themes, gui_trade, library_medium, mansion_library |  |
| `marble_dark` | good |  | aquarium | Redrawn with the toolkit in basics.py: dark slabs with long, thin, continuous veins of white and grey drifting across them. |
| `rock` | good |  | castle_keep, coast_lighthouse, crystal_cave, doomed, garden_encounter, gui_lantern, gui_menus, hospital_garden, kelp_forest, moon_base, post_presets, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: masses of every size, each a facet tilted to the light, split by crevices that wander, widen and close; finer cracks, grain. |
| `rock_wet` | good |  | crystal_cave, gui_lantern, kelp_forest, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: the same rock darker and blue-grey, with glints of water where the faces catch the light. |
| `snow_rock` | good |  | winter_lake | Redrawn with the toolkit in basics.py: faceted rock with snow lying on the top of every mass, thick on the flats, and drifted in the crevices. |
| `sky_wall` | good |  | dream_chess, dream_world, hall_of_doors |  |

### Wood

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `wood_panel` | good |  | drowned_library, haunted_house, mansion_library | Redrawn with the toolkit in basics.py: stiles and rails framing two raised panels per unit, all one dark wood, the bevels catching the light, figure streaked along the grain. |
| `planks` | good |  | bayou, ghost_town, kelp_forest, sky_islands, winter_woods |  |
| `boards` | good |  | bayou, coast_lighthouse, ghost_town, gold_mine, kelp_forest, rain_alley, tropical_beach |  |
| `logs` | good |  | coast_lighthouse, winter_lake |  |
| `door_wood` | good |  | bayou, dream_chess, dream_world, haunted_house, salt_flat, winter_lake |  |
| `bookshelf` | good |  | claude_study, drowned_library, gui_themes, gui_trade, library_medium, mansion_library |  |
| `bark` | good |  | - | Redrawn with the toolkit in forest.py: long wavy ridges split by deep dark furrows; tiles without a seam. |
| `bark_pine` | good |  | - | Redrawn with the toolkit in forest.py: a mosaic of tall plates (nearest-seed cells) with dark fissures and flaking. |
| `wood_floor` | good |  | claude_study, drowned_library, gui_lantern, gui_themes, gui_trade, haunted_house, library_medium, mansion_library, saloon, tunnel_encounter, underground_waterway |  |
| `shingle` | good |  | bayou, chapel_graveyard, coast_lighthouse, rainy_street, winter_lake | Redrawn with the toolkit in basics.py: courses of staggered slates, each tipped up to its foot so it throws a shadow on the course below, chipped corners, moss in the joints. |

### Metal and sci-fi

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `iron_door` | good |  | bunker_lab, garden_encounter, ghost_corridor, gui_hud, gui_lantern, gui_menus, hospital_corridor, hospital_garden, post_presets, rainy_street, tunnel_encounter, underground_waterway |  |
| `corrugated` | good |  | rainy_street | Redrawn with the toolkit in basics.py: galvanised sheets in rounded ribs lapped at the seam, nail rows, rust in patches and streaks from the nails. |
| `rust` | good |  | bunker_lab, rainy_street |  |
| `pipes` | good |  | bunker_lab, sewer_tunnels |  |
| `panel` | good |  | bunker_lab, capsule_hotel, derelict_ship, orbital_hangar, space_station |  |
| `panel_green` | good |  | bunker_lab |  |
| `hull` | good |  | orbital_hangar, space_station |  |
| `hull_dark` | good |  | derelict_ship, orbital_hangar, space_station |  |
| `hull_lit` | good | glows | space_station |  |
| `hull_red` | good | glows | derelict_ship |  |
| `tech_panel` | good | glows | space_station |  |
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
| `vector_grid` | good | glows | vector_world | Drawn in vector.py: black ruled in lines of white light, two squares to a unit each way; a tint colours it. |
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
| `lumen_floor` | good | glows | crystal_cave, glow_jungle | Drawn in glowjungle.py: dark leaf litter with glowing moss and fungus specks. |
| `glow_water` | good | glows, mirror 0.55 | crystal_cave, glow_jungle | Drawn in glowjungle.py: black water with plankton glowing in swirling streams; reflects. |
| `ice_block` | good |  | aurora_palace | Drawn in icepalace.py: big blocks of blue ice, frosted faces paler at their edges, deep joints, cracks. |
| `frost_wall` | good |  | aurora_palace | Drawn in icepalace.py: ice grown over with feathery frost. |
| `ice_floor` | good | mirror 0.6 | aurora_palace | Drawn in icepalace.py: polished ice over dark water, cracked white; reflects. |
| `brass_plate` | good |  | clockwork_city | Drawn in clockwork.py: riveted brass panels, darker in their middles, worn bright at their edges. |
| `copper_pipes` | good |  | clockwork_city | Drawn in clockwork.py: a wall run with copper pipes, a valve wheel, green where they weep. |
| `clock_face` | good |  | clockwork_city | Drawn in clockwork.py: a clock dial on a dark ground, one to a cell. |
| `hangar_floor` | good |  | orbital_hangar | Drawn with the toolkit in scifi.py: heavy plates four to a unit, corner bolts, tread, a tie-down ring at each crossing, wear and oil. |
| `conduit` | good | glows | orbital_hangar | Drawn with the toolkit in scifi.py: cable bundles in four colours and pipes up the wall, steel clamps, a junction box with lit LEDs. |
| `screen_wall` | good | glows | orbital_hangar | Drawn with the toolkit in scifi.py: monitors four to a unit, each with a trace, readouts, a radar or a wireframe, in cyan, green or amber; glows. |
| `tunnel_roof` | good | glows | aquarium | Drawn with the toolkit in aquarium.py: deep blue water with the rippled surface far above and its net of light; a dark acrylic seam at every tile; glows. |
| `jelly_backdrop` | good | glows | aquarium | Drawn with the toolkit in aquarium.py: an even glowing deep blue, faintly mottled, so jellies stand out in front of it. |
| `open_water` | good | glows | aquarium, neon_bar | Drawn in aquarium.py: the open water painted on the back of a big tank, paler toward the surface, soft shafts in it; the upper storey over `deep_water`, so the rockwork's tops read against it. Dithered for distance: up close its steps show. |
| `deep_water` | good | glows | aquarium, neon_bar | The lower storey of `open_water`, deepening toward the floor. |
| `bar_shelves` | good | glows | neon_bar | Drawn with the toolkit in bar.py: two glass shelves of bottles in a dark mirrored recess, each bottle lit from below by a magenta strip; glows. |
| `capsules` | good | glows | capsule_hotel | Drawn in bar.py: four berths to a unit in white moulded plastic, each with a glowing number plate; lamp-lit bedding, a drawn blind, a screen or dark inside; glows. |
| `capsules_lit` | good | glows | capsule_hotel | The same berths with more of them occupied and lit; alternate it with `capsules` so the pattern does not march. |
| `nukage` | good | glows | doomed | Drawn in doomed.py: bright green sludge in slow swirls with paler veins and darker clots; glows - sink it with `drop`. |

### Nature

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `foliage` | good |  | - | Redrawn with the toolkit in forest.py: small leaves at three depths over a dark tangle of twigs. The wall behind a `forest` fringe. |
| `foliage_autumn` | good |  | - | The same leaves in orange, gold and red over dark brown. |
| `forest_deep` | good |  | haunted_house, woodland_night | Trunks at four depths in the dark, the farthest thinnest and darkest, boughs and a few leaves catching light; sways repeat with the tile. The wall behind a `forest` fringe: gaps between the cards read as more wood. |
| `forest_deep_autumn` | good |  | autumn_lane | Drawn with the toolkit in forest.py: forest_deep with the leaves hanging in the dark turned a deep rust. |
| `forest_deep_snow` | good |  | winter_woods | Drawn with the toolkit in forest.py: forest_deep with snow lying on the boughs between the dark trunks. |
| `swamp_deep` | good |  | bayou | Drawn with the toolkit in swamp.py: grey trunks at four depths in the murk with curtains of Spanish moss between them. |
| `hedge` | good |  | garden_encounter, gui_menus, hospital_garden, post_presets | Redrawn with the toolkit in basics.py: small leaves packed in three depths, the face kept flat by the shears, thin patches darker. |
| `grass` | good |  | cathedral_ruin, chapel_graveyard, dream_world, garden_encounter, gui_menus, hospital_garden, misty_moor, post_presets, village_green | Redrawn with the toolkit in basics.py: blades stroked in clumps, dark at the roots and bright at the tips, yellow-green tufts, a daisy or two. |
| `moss` | good |  | autumn_lane | Redrawn with the toolkit in forest.py: crowded cushions with fine bobbles, a stone showing here and there. |
| `mud` | good |  | woodland_night |  |
| `bog` | good |  | bayou | Drawn with the toolkit in swamp.py: black peat with cushions of sphagnum in green and rust, standing puddles. |
| `dirt` | good |  | autumn_lane, castle_keep, haunted_house | Redrawn with the toolkit in basics.py: soil broken into clods, pebbles, a root or two, darker damp patches. |
| `gravel` | good |  | chapel_graveyard, coast_lighthouse, garden_encounter, gui_menus, haunted_house, hospital_garden, post_presets | Redrawn with the toolkit in basics.py: rounded pebbles in three stone colours, each lit on top with a shadow under it. |
| `sand` | good |  | coast_lighthouse | Redrawn with the toolkit in basics.py: wind ripples with a lit face and a shaded lee, wandering, a shell fragment or two, dark grains. |
| `snow` | good |  | aurora_palace, winter_lake, winter_woods | Redrawn with the toolkit in basics.py: drifts sculpted by the wind, their lee sides in blue shadow, faint ripples, glitter. |
| `ice` | good | mirror 0.38 | winter_lake, winter_woods | Redrawn with the toolkit in basics.py: clear blue with gentle depth, straight fractures with a branch each and a dark side, strings of bubbles, frost. |
| `water` | good | mirror 0.5 | alien_world, coast_lighthouse, drowned_library, gui_lantern, sewer_tunnels, temple_inside, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: a deep teal in slow swells and a broken net of light where the ripples gather it; kept dark, so reflections read. |
| `swamp_water` | good | mirror 0.42 | bayou | Drawn with the toolkit in swamp.py: black-brown water with a skin of duckweed drifting in patches and a few floating leaves; mirror 0.42. |
| `seabed` | good |  | aquarium, kelp_forest, neon_bar | Drawn with the toolkit in sea.py: pale sand in gentle ripples, shell and pebble, and a broken net of caustic light over it. |
| `water_surface` | good | glows | aquarium, neon_bar | Drawn with the toolkit in sea.py: the surface from below, rippled and glowing with a net of brighter lines; for an underwater roof. |
| `reef_wall` | good |  | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: lumps of live rock, patches of pink coralline, coral heads, algae tufts and polyps, dark crevices. |
| `pine_needles` | good |  | woodland_night | Redrawn with the toolkit in forest.py: criss-crossed needle litter over dark soil, a few green needles, cones and twigs. |
| `leaves_fallen` | good |  | autumn_lane | Drawn with the toolkit in forest.py: leaves lying flat over dark earth, each its own colour - orange, gold, rust, brown, a few green - grass where they lie thin. |
| `alien_ground` | good |  | alien_world | Redrawn with the toolkit in basics.py: violet dust drifting over teal grit, the edge broken grain by grain, crystal shards of pink, cyan and white. |
| `regolith` | good |  | moon_base | Drawn with the toolkit in moon.py: grey dust with craters - a rim lit toward the sun, a dark bowl - and thrown-out rocks. |
| `alien_rock` | good | glows | alien_world | Redrawn with the toolkit in basics.py: dark violet masses, each a facet to the light, with a teal glow welling up in the crevices between them and spilling onto the faces (emissive). |
| `organic` | good |  | derelict_ship |  |
| `cloud_floor` | good |  | - |  |

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
| `cobble` | good |  | clockwork_city, garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, village_green | Redrawn with the toolkit in basics.py: a Voronoi mosaic of 36 rounded stones a tile in grey and brown, dark grit and moss in the joints; the repeat no longer shows. |
| `asphalt` | good |  | neon_rooftop, neon_street, rain_alley, rainy_street |  |
| `carpet` | good |  | castle_keep, chapel_graveyard, claude_study, gui_themes, gui_trade, haunted_house, library_medium, mansion_library |  |
| `carpet_green` | good |  | - |  |
| `flagstone` | good |  | castle_keep, cathedral_ruin, chapel_graveyard, claude_study, haunted_house, neon_street, night_market, rain_alley |  |
| `obsidian` | good | mirror 0.45 | dream_world, neon_bar, space_station |  |
| `concrete_floor` | good |  | 63 scenes |  |
| `rock_floor` | good |  | crystal_cave, doomed, gold_mine, gui_lantern, kelp_forest, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: flatter, smaller masses in brown with grit in the cracks. |

### Ceilings

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `acoustic` | good |  | ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: four bevelled tiles a unit in a grid of runners, pitted with fissures and pin-holes, a water stain. |
| `ceiling_plaster` | good |  | gui_themes, gui_trade, library_medium | Redrawn with the toolkit in basics.py: the plaster render in a darker tone, with no band across it. |
| `beams` | good |  | castle_keep, cathedral_ruin, chapel_graveyard, claude_study, haunted_house | Redrawn with the toolkit in basics.py: two oak beams a unit, proud of the limewash: a lit edge, a side in shadow and a soft shadow on the plaster; grain and checks. |

### Fabric and interior

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `curtain` | good |  | gui_themes, gui_trade, library_medium, mansion_library | Redrawn with the toolkit in basics.py: velvet folds of every width, each a rounded column lit on its left, deep shadow between. |
| `curtain_black` | good |  | - | Redrawn with the toolkit in basics.py: the same folds in black velvet. |
| `wallpaper` | good |  | gui_themes, gui_trade, hall_of_doors, haunted_house, library_medium, mansion_library |  |
| `wallpaper_green` | good |  | - |  |

### Light sources

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `window_lit` | good | glows | coast_lighthouse, garden_encounter, gui_menus, haunted_house, hospital_garden, neon_rooftop, post_presets, rainy_street | Simple; a silhouette in one pane now and then would add life. |
| `window_dark` | good |  | garden_encounter, gui_menus, gui_themes, gui_trade, haunted_house, hospital_garden, library_medium, mansion_library, neon_rooftop, post_presets, rainy_street |  |
| `window_lit_plaster` | good | glows | bayou, garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, winter_lake |  |
| `window_dark_plaster` | good |  | garden_encounter, ghost_corridor, gui_hud, gui_menus, hospital_corridor, hospital_garden, post_presets, rainy_street |  |
| `window_teal` | good | glows | garden_encounter, gui_menus, hospital_garden, post_presets |  |
| `stained_glass` | good | glows | castle_keep, chapel_graveyard |  |
| `runes` | good | glows | gui_lantern, gui_themes, gui_trade, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `fireplace` | good | glows | claude_study, haunted_house |  |
| `star_chart` | good | glows | claude_study |  |

### See-through

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `bars` | good | see-through | castle_keep |  |
| `fence_iron` | good | see-through | chapel_graveyard, haunted_house |  |
| `chainlink` | good | see-through | - |  |
| `railing` | good | see-through | claude_study, sewer_tunnels |  |
| `picket` | good | see-through | - |  |
| `portcullis` | good | see-through | castle_keep |  |
| `window_broken` | good | see-through | cathedral_ruin |  |
| `tall_window` | good | see-through | drowned_library | Drawn with the toolkit in dream.py: two lancets in pale ashlar, leaded every quarter unit, open between the leads (see-through). |
| `tall_window_top` | good | see-through | drowned_library | Drawn with the toolkit in dream.py: the lancets closing in pointed arches under a small rose; see-through. |
| `lattice` | good | see-through | tropical_beach |  |
| `viewport` | good | see-through | space_station |  |
| `tank_window` | good | see-through | aquarium | Drawn with the toolkit in aquarium.py: a rounded opening in a deep frame of dark painted steel, bolt heads top and bottom. |
| `green_window` | good | see-through | doomed | Drawn in doomed.py: the trimmed green plating with a window cut through it in a deep dark frame; see-through. |

### Jungle

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `jungle_leaves` | good |  | jungle_temple, temple_inside, tropical_beach | Drawn with the pixel-art toolkit. |
| `canopy` | good | glows | jungle_temple | Leaves at three depths - lit far ones, a middle layer, near silhouettes - with sky in the gaps. |
| `canopy_top` | good |  | glow_jungle, jungle_temple, tropical_beach | Use as the top of jungle walls. |
| `jungle_floor` | good |  | jungle_temple, temple_inside |  |
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
| `sandstone` | good |  | ghost_town, gold_mine, red_canyon | Drawn with the toolkit in desert.py: beds of red, orange and cream, the hard ones standing out as ledges, cross-bedding, joints, varnish streaking down from the ledges. |
| `sandstone_pale` | good |  | ghost_town, gold_mine, red_canyon | Drawn with the toolkit in desert.py: the cream cap rock near a canyon rim, for bands among the sandstone. |
| `slot_rock` | good |  | red_canyon | Drawn with the toolkit in desert.py: beds swept into flowing curves of orange, red, cream and violet, polished smooth. |
| `pueblo_stone` | good |  | red_canyon | Drawn with the toolkit in desert.py: thin sandstone slabs laid in courses in a thick mud mortar, chinked with small stones. |
| `pueblo_door` | good |  | red_canyon | Drawn with the toolkit in desert.py: the coursed stone with a T-shaped doorway, dark inside, poles laid over its head. |
| `ruin_paving` | good |  | ancient_ruins, jungle_temple, temple_inside |  |
| `dry_grass` | good |  | ancient_ruins, autumn_lane | Fewer, larger clumps with more earth between them, so it is not busy at grazing angles. |
| `desert_wash` | good |  | ghost_town, gold_mine, red_canyon, saloon | Drawn with the toolkit in desert.py: pale sand faintly rippled, washed-down pebbles, patches of crazed dried mud. |
| `colonnade` | good | see-through | - | Flat when seen along its length: use `column` objects for a row you look down (the ruins' peristyle now is). |
| `colonnade_top` | good | see-through | - |  |
| `colonnade_broken` | good | see-through | - |  |

### Beach

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `beach_sand` | good |  | tropical_beach |  |
| `wet_sand` | good | mirror 0.28 | tropical_beach |  |
| `shallows` | good | mirror 0.3 | jungle_temple, sky_islands, tropical_beach |  |
| `sea` | good | mirror 0.45 | ancient_ruins, tropical_beach |  |
| `bamboo` | good |  | tropical_beach | A node in each third of every pole, so they stagger from pole to pole instead of lining up across them. |
| `thatch` | good |  | tropical_beach | Each row stands out over the one under it and shades its top, so the rows read. |

### Not yet sorted

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `saloon_wainscot` | good |  | saloon | Drawn with the toolkit in saloon.py: dark raised panels to a chair rail, skirting at the foot, flocked red paper (a gold trellis, a sprig in each lozenge) above. |
| `saloon_paper` | good |  | saloon | The flocked paper, a dark cornice along its top: the storey over `saloon_wainscot`. |
| `saloon_backbar` | good |  | saloon | A cabinet of dark panels, a shelf on it, shelves of green, amber and clear bottles in carved uprights. |
| `saloon_backbar_top` | good |  | saloon | A tall mirror in a carved frame under an arched cresting, a glint across it. |
| `saloon_window` | good | see-through | saloon | Six open panes in a dark frame: the sun comes through, and a bright street shows. |
| `tin_ceiling` | good |  | saloon | Pressed tin, cream gone yellow with smoke: square panels each pressed with a rosette. |
| `mine_rock` | good |  | gold_mine | Drawn with the toolkit in mine.py: brown rock broken into small masses by dark cracks, drill and pick marks. |
| `mine_rock_vein` | good |  | gold_mine | The rock with a seam of milky quartz running across it in a gentle wave, so cell to cell it joins up into one seam. Use it for a few cells only. |
| `mine_rock_gold` | good | glows | gold_mine | The seam with gold in it - flecks and a thread - glinting: it glows a little, so a lamp seems to catch it. |

## Props (306)

Camera-facing sprites. "tall" is the default height in world units (a wall is 1); "no shadow" props hang, float or burn, so they get no contact shadow.

### Furniture and interior

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `armchair` | good | 0.6 tall | claude_study, haunted_house, mansion_library, salt_flat |  |
| `bed` | good | 0.4 tall | bunker_lab, ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: an iron bedstead with uprights, a mattress in white sheets, a pillow, a grey blanket turned back, castors. |
| `bench` | good | 0.35 tall | aquarium, coast_lighthouse, garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, village_green | Redrawn with the toolkit in basics.py: three backrest slats and two in the seat, held in cast-iron ends with scrolled armrests and curving legs. |
| `arcade_cabinet` | good | 0.68 tall, glows, aura | neon_bar | Drawn with the toolkit in bar.py: a dark cabinet with neon side art, a lit marquee in pseudo-letters, a space shooter on a scanlined screen, joystick and buttons, a coin door. |
| `bar_counter` | good | 0.35 tall, glows, no shadow | neon_bar | Drawn with the toolkit in bar.py: dark raised panels, a chrome rail, the black lip of the top, a magenta light strip along the foot; a card that repeats along its length. |
| `bar_stool` | good | 0.27 tall | neon_bar, neon_street | Drawn with the toolkit in bar.py: a red vinyl seat on a chrome pole with a foot ring and a weighted base. |
| `booth` | good | 0.5 tall, glows | neon_bar | Drawn with the toolkit in bar.py: a high back buttoned in teal vinyl, the seat, a formica table on a chrome leg with a glowing lamp. |
| `jukebox` | good | 0.56 tall, glows, aura | neon_bar | Drawn with the toolkit in bar.py: bands of red, gold and blue light round its arch, bubble tubes up both sides, the records in a window, a grille. |
| `bottles` | good | 0.12 tall | neon_bar, neon_street, saloon | Drawn with the toolkit in bar.py: green, amber and clear bottles at different heights with labels and glints. |
| `info_plaque` | good | 0.42 tall, glows | aquarium | Drawn with the toolkit in aquarium.py: a slanted panel on a post, lit blue from behind, a fish outline and lines of text too small to read. |
| `book_stack` | good | 0.22 tall | claude_study, drowned_library, mansion_library |  |
| `chest` | good | 0.3 tall | castle_keep, kelp_forest | Redrawn with the toolkit in basics.py: oak planks under a rounded lid, iron straps studded with rivets, iron corners, a brass lock plate. |
| `console` | good | 0.85 tall, glows | bunker_lab, orbital_hangar, space_station |  |
| `crate` | good | 0.4 tall | 20 scenes | Redrawn with the toolkit in basics.py: planks behind battens and a diagonal brace, nails at the corners, a stencilled arrow. |
| `barrel` | good | 0.45 tall | 20 scenes | Redrawn with the toolkit in basics.py: bulging staves turned on a lathe, three iron hoops, the lid showing at the top. |
| `locker` | good | 1 tall | bunker_lab |  |
| `lectern` | good | 0.5 tall | chapel_graveyard |  |
| `open_book` | good | 0.12 tall, glows, no shadow | claude_study, drowned_library, mansion_library |  |
| `pew` | good | 0.42 tall | cathedral_ruin, chapel_graveyard |  |
| `table` | good | 0.36 tall | castle_keep | Redrawn with the toolkit in basics.py: a thick top with grain along it, an apron, turned legs, the far pair darker. |
| `throne` | good | 0.95 tall | castle_keep |  |
| `wheelchair` | good | 0.45 tall | ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: side on: a big spoked wheel with its push rim, a caster, leather seat and back, armrest, handles, footrest. |
| `writing_desk` | good | 0.55 tall, glows | claude_study, drowned_library, mansion_library |  |
| `globe` | good | 0.45 tall | claude_study, drowned_library, mansion_library |  |
| `orrery` | good | 0.6 tall, glows | claude_study |  |
| `telescope` | good | 0.8 tall | claude_study, mansion_library |  |
| `painting` | good | 0.45 tall, no shadow | - |  |
| `wall_clock` | good | 0.28 tall, no shadow | bunker_lab, hall_of_doors, rainy_street |  |
| `banner` | good | 0.95 tall, no shadow | castle_keep, rainy_street |  |
| `chains` | good | 0.6 tall, no shadow | castle_keep |  |
| `ladder` | good | 1 tall, no shadow | capsule_hotel, drowned_library, red_canyon, sewer_tunnels |  |
| `pipe_valve` | good | 0.32 tall, no shadow | bunker_lab, clockwork_city, sewer_tunnels |  |
| `sack` | good | 0.42 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, gold_mine, neon_street, rain_alley, rainy_street, sewer_tunnels, village_green, woodland_night |  |
| `bucket` | good | 0.32 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, neon_street, rain_alley, rainy_street, sewer_tunnels |  |

### Light and fire

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `brazier` | good | 0.85 tall, glows, no shadow | ancient_ruins, castle_keep, coast_lighthouse, temple_inside |  |
| `campfire` | good | 0.4 tall, glows, no shadow | tropical_beach, woodland_night |  |
| `candles` | good | 0.2 tall, glows, no shadow | castle_keep, cathedral_ruin, chapel_graveyard, drowned_library, gui_lantern, gui_themes, gui_trade, jungle_temple, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `ceiling_lamp` | good | 0.3 tall, glows, no shadow | bunker_lab, sewer_tunnels |  |
| `chandelier` | good | 0.45 tall, glows, no shadow | castle_keep, claude_study, haunted_house, saloon |  |
| `cobweb` | good | 0.9 tall, no shadow | haunted_house, mansion_library | Drawn with the toolkit in haunted.py: threads radiating from a corner with sagging spiral rings, a broken strand; translucent. |
| `candelabra` | good | 1.2 tall, glows, aura | castle_keep, haunted_house, mansion_library | Drawn with the toolkit in haunted.py: a turned brass stem on a tripod foot, five curved arms with candles burning, wax run down them; aura. |
| `portrait` | good | 0.75 tall, glows, no shadow | haunted_house, mansion_library | Drawn with the toolkit in haunted.py: an oval beaded gilt frame round a pale, unsmiling face, black coat and white collar; the eyes glow faintly. |
| `grandfather_clock` | good | 1.6 tall | haunted_house, mansion_library, salt_flat | Drawn with the toolkit in haunted.py: a mahogany case: hood with a broken pediment and finial, a dial near midnight, a glass door on the pendulum. |
| `balustrade` | good | 0.5 tall | haunted_house | Drawn with the toolkit in haunted.py: turned balusters every eighth of a unit between handrail and base rail, newel posts; three units a card. |
| `lamp_post` | good | 1.6 tall, glows | clockwork_city, garden_encounter, gui_menus, hospital_garden, post_presets, rain_alley, rainy_street | Thin at a distance. |
| `lantern` | good | 0.3 tall, glows, no shadow | bayou, chapel_graveyard, coast_lighthouse, garden_encounter, ghost_town, gold_mine, gui_lantern, gui_menus, gui_themes, gui_trade, library_medium, mansion_library, post_presets, tunnel_encounter, underground_waterway, village_green, winter_lake, winter_woods, woodland_night |  |
| `sconce` | good | 0.32 tall, glows, no shadow | castle_keep, claude_study, rainy_street, saloon |  |

### Nature

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `boulder` | good | 0.55 tall | chapel_graveyard, kelp_forest | Redrawn with the toolkit in forest.py: a settled rock with a lesser lobe and cracks, moss over its top, lichen spots. |
| `bush` | good | 0.5 tall | cathedral_ruin, chapel_graveyard, coast_lighthouse, woodland_night | Redrawn with the toolkit in forest.py: leaf clusters on fanned twigs, lit on top, dark underneath. |
| `bush_autumn` | good | 0.5 tall | autumn_lane | Drawn with the toolkit in forest.py: the bush in rust red and orange. |
| `bush_snow` | good | 0.45 tall | winter_woods | Drawn with the toolkit in forest.py: a lumpy cushion of snow, blue in its hollows, twigs poking up through it. |
| `birch` | good | 3 tall | sky_islands, village_green, woodland_night | White trunk and a second stem banded with black, an airy crown of small leaves in drooping clumps. |
| `birch_autumn` | good | 3 tall | autumn_lane | Drawn with the toolkit in forest.py: the birch gone to gold, a few patches already orange. |
| `birch_winter` | good | 3 tall | winter_woods | Drawn with the toolkit in forest.py: the white birch bare: branches reaching out with fine twigs weeping from them, snow on a few. |
| `dead_tree` | good | 2.9 tall | chapel_graveyard, haunted_house, misty_moor, woodland_night | Redrawn with the toolkit in forest.py: a split trunk on a gnarled foot, bare limbs forking into twigs, grey peeling bark. |
| `fern` | good | 0.42 tall | autumn_lane, cathedral_ruin, chapel_graveyard, jungle_temple, misty_moor, temple_inside, tropical_beach, woodland_night | Redrawn: arching fronds from one crown. |
| `flowers` | good | 0.35 tall | garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, sky_islands, village_green | Redrawn with the toolkit in basics.py: leaves and stems with blooms of four colours, five petals round a dark eye, at different heights. |
| `grass_tuft` | good | 0.4 tall | autumn_lane, cathedral_ruin, chapel_graveyard, coast_lighthouse, misty_moor, rainy_street, tropical_beach, village_green, woodland_night | Redrawn: thin arching blades. |
| `ivy_hang` | good | 0.8 tall, no shadow | cathedral_ruin, rainy_street |  |
| `log` | good | 0.28 tall | cathedral_ruin, tropical_beach, winter_lake, winter_woods, woodland_night | Redrawn with the toolkit in forest.py: bark in long ridges, a branch stub, moss along the top, a pale ringed end. |
| `mushrooms` | good | 0.12 tall | autumn_lane, cathedral_ruin, chapel_graveyard, crystal_cave, jungle_temple, woodland_night |  |
| `palm` | good | 3.2 tall | garden_encounter, gui_menus, hospital_garden, post_presets, tropical_beach | Redrawn with the pixel-art toolkit: a ringed trunk, arching ragged fronds, coconuts. |
| `pine` | good | 3.4 tall | autumn_lane, coast_lighthouse, sky_islands, woodland_night | Redrawn with the toolkit in forest.py: a spruce, tier on tier of drooping boughs with ragged hems over a straight trunk. |
| `reeds` | good | 0.8 tall | coast_lighthouse, winter_woods |  |
| `bald_cypress` | good | 4.2 tall | bayou | Drawn with the toolkit in swamp.py: a fluted, buttressed foot, limbs under flat sprays of feathery leaves, moss hanging from every limb, knees round it. |
| `spanish_moss` | good | 1.4 tall, no shadow | bayou | Drawn with the toolkit in swamp.py: a curtain of grey-green strands from a stub of branch, to hang with `z`. |
| `cypress_knees` | good | 0.3 tall | bayou | Drawn with the toolkit in swamp.py: knobbly cones of root standing out of the water. |
| `cattails` | good | 1 tall | bayou | Drawn with the toolkit in swamp.py: long blades and stems with brown velvet heads. |
| `kelp` | good | 5 tall | kelp_forest | Drawn with the toolkit in sea.py: a swaying stipe from its holdfast, long golden blades streaming off small floats, a tangle at the top. |
| `brain_coral` | good | 0.3 tall | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: a dome lit on its crown, its surface all meandering ridges (ochre) and grooves (green-brown). |
| `staghorn_coral` | good | 0.42 tall | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: a thicket of golden-brown branches forking like antlers, lilac-white growing tips. |
| `sea_fan` | good | 0.62 tall | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: a flat purple lace: thicker branches fanning from a short trunk with a fine net of little cells between them. |
| `anemone` | good | 0.26 tall | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: a bubble-tip anemone: a red foot, salmon tentacles swollen to magenta bulbs, its pair of clownfish nestled among them. |
| `tube_sponge` | good | 0.36 tall | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: violet tubes from a shared base, each with its lip and dark open mouth. |
| `reef_rock` | good | 0.6 tall | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: a mound of live rock in coralline and algae, with a sea fan, staghorn, a tube sponge and brain corals grown on it. |
| `rocks` | good | 0.22 tall | 20 scenes | Redrawn: half-sunk stones with lit tops and the odd crack. |
| `snowy_pine` | good | 3.4 tall | aurora_palace, winter_lake, winter_woods | Drawn with the toolkit in forest.py: the new spruce with snow lying in clumps along every tier's shoulders, crumbs on the hems and a small cap on the leader; dark needles between, so it still reads at a distance. |
| `boulder_snow` | good | 0.55 tall | winter_lake, winter_woods | Drawn with the toolkit in forest.py: the boulder under a cushion of snow, deep where the top is flat and thin down the steep sides; in the `snow` scatter set. |
| `stump` | good | 0.3 tall | tropical_beach, woodland_night | Redrawn with the toolkit in forest.py: a pale ringed cut face, furrowed sides, roots, a cushion of moss. |
| `tree` | good | 2.6 tall | dream_world, garden_encounter, gui_menus, hospital_garden, post_presets, sky_islands, village_green, woodland_night | Redrawn with the toolkit in forest.py: an oak with a furrowed trunk on a flared foot, limbs showing between lobes of crown lit from above. |
| `tree_autumn` | good | 2.6 tall | autumn_lane | Drawn with the toolkit in forest.py: the oak turned: orange and gold in patches cluster by cluster, a side going first, a little rust. |
| `tree_winter` | good | 2.6 tall | winter_woods | Drawn with the toolkit in forest.py: a bare oak grown by recursive branching down to twigs, snow along every limb level enough to hold it. |
| `glowshroom` | good | 0.16 tall, glows, no shadow | alien_world, crystal_cave, glow_jungle | Redrawn with the toolkit in basics.py: domed caps freckled with paler spots over dark gills, pale stems; the caps glow. |
| `crystal` | good | 0.36 tall, glows, no shadow | alien_world, crystal_cave |  |
| `stalagmite` | good | 0.8 tall | crystal_cave |  |

### Debris

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `bones` | good | 0.22 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, crystal_cave, derelict_ship, neon_street, rain_alley, sewer_tunnels, temple_inside, woodland_night |  |
| `broken_barrel` | good | 0.46 tall | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, neon_street, rain_alley, rainy_street, sewer_tunnels, woodland_night | Redrawn with the toolkit in basics.py: the hooped bottom half, its front staves splintered off at different heights over the dark inside, the back staves taller, loose staves and a fallen hoop. |
| `rubble` | good | 0.34 tall | ancient_ruins, bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, rainy_street, sewer_tunnels, woodland_night |  |

### Monuments and outdoors

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `column` | good | 1 tall | sky_islands | Redrawn: a fluted Doric column with capital and plinth. |
| `fountain` | good | 0.9 tall | - | Redrawn with the toolkit in basics.py: a moulded basin with water in it, a fluted pedestal and bowl, water spilling in arcs. |
| `gravestone` | good | 0.6 tall | chapel_graveyard, haunted_house |  |
| `stone_cap` | good | 0.44 tall | misty_moor | Drawn with the toolkit in basics.py: a slanted, chipped crown of stone with lichen, to set on a one-cell block so a standing stone has a weathered top. |
| `grave_cross` | good | 0.55 tall | chapel_graveyard, haunted_house |  |
| `signpost` | good | 1.3 tall | coast_lighthouse |  |
| `statue` | good | 1.5 tall | garden_encounter, gui_menus, hospital_garden, mansion_library, post_presets, sky_islands | Redrawn with the toolkit in basics.py: a draped woman in weathered marble raising a wreath, folds catching the light, on a moulded plinth with lichen. |
| `monolith` | good | 2.2 tall | alien_world |  |
| `rowboat` | good | 0.3 tall | bayou, coast_lighthouse, gui_lantern, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: a clinker hull of lapped strakes, the top one painted a faded teal, a lighter gunwale, the bow rising, an oar along it. |
| `anchor` | good | 0.75 tall | kelp_forest | Drawn with the toolkit in sea.py: an iron anchor: ring, stock, shank, curved arms and spade flukes, rusted and grown over. |
| `wreck_mast` | good | 3.6 tall | kelp_forest | Drawn with the toolkit in sea.py: a snapped mast leaning, a yard askew, torn rigging, furred with weed. |
| `buoy` | good | 0.5 tall, glows | coast_lighthouse | Redrawn with the toolkit in basics.py: a red can with a white band, a lattice cage carrying its lit lamp, ripples at the waterline. |
| `snowman` | good | 0.62 tall | winter_lake, winter_woods |  |
| `scarecrow` | good | 1.9 tall | autumn_lane | Drawn with the toolkit in village.py: post and crossbar, a sack head with a stitched face, a battered hat, a patched coat with straw at the cuffs and hem, a crow on one arm. |
| `pumpkin` | good | 0.32 tall | autumn_lane | Drawn with the toolkit in village.py: a squat gourd of deep ribs, a woody stem, a curl of vine and a leaf. |
| `jack_o_lantern` | good | 0.34 tall, glows, aura | autumn_lane, haunted_house | Drawn with the toolkit in village.py: the pumpkin carved into a face that burns yellow (emissive), the rind darker round it; aura. |
| `hay_bale` | good | 0.5 tall | autumn_lane | Drawn with the toolkit in village.py: a square bale packed with stalks, two bands of twine, loose ends bristling. |
| `well` | good | 1.7 tall | village_green | Drawn with the toolkit in village.py: a round wall of fieldstones with a coping, oak posts under a little shingled roof, a windlass, a rope and a bucket. |
| `cart` | good | 0.75 tall | ghost_town, village_green | Drawn with the toolkit in village.py: a hand cart: a plank bed with stakes on a big spoked wheel, its shafts down, loaded with sacks. |
| `market_stall` | good | 1.9 tall | - | Drawn with the toolkit in village.py: a red and white striped awning with a scalloped valance over a trestle of apples, cabbages and bread, crates beneath. |
| `inn_sign` | good | 0.75 tall | village_green | Drawn with the toolkit in village.py: an iron bracket and scroll with a red board hanging from it, a gilt border and crown; stand it out from a front as a card. |
| `armor` | good | 0.66 tall | castle_keep, haunted_house |  |

### Sci-fi

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `antenna` | good | 2.4 tall, glows | alien_world, moon_base, neon_rooftop |  |
| `drone` | good | 0.22 tall, glows, no shadow | orbital_hangar, space_station |  |
| `hologram` | good | 0.55 tall, glows, aura, no shadow | orbital_hangar, space_station |  |
| `lander` | good | 1.6 tall, glows | alien_world, moon_base |  |
| `dome` | good | 2.6 tall, glows, aura | moon_base | Drawn with the toolkit in moon.py: a geodesic frame of white struts over glass, rows of plants under pink grow lights, an airlock; glows. |
| `hab_module` | good | 1.3 tall, glows | moon_base | Drawn with the toolkit in moon.py: a ribbed white cylinder on legs, lit portholes, an end hatch, a radiator fin. |
| `solar_array` | good | 1.4 tall | moon_base | Drawn with the toolkit in moon.py: dark-blue cells in a silver frame tilted on a mast, a cable down. |
| `rover` | good | 0.8 tall | moon_base | Drawn with the toolkit in moon.py: a white chassis on six wire-mesh wheels, two seats, a dish on a mast, a foil-wrapped box. |
| `sci_crate` | good | 0.35 tall, glows | derelict_ship, moon_base, neon_street, night_market, orbital_hangar, space_station |  |
| `toxic_barrel` | good | 0.4 tall, glows, aura | doomed | Drawn in doomed.py: a ribbed, dented drum brimming with glowing green sludge that runs down its sides. |
| `corpse` | good | 0.13 tall | doomed | Drawn in doomed.py: a fallen soldier on his side in a pool of blood, an arm flung out, the helmet rolled off. |
| `medkit` | good | 0.1 tall | doomed | Drawn in doomed.py: a white kit with a red cross on its lid and a handle. |
| `ammo_clip` | good | 0.07 tall | doomed | Drawn in doomed.py: a magazine with the brass of its top round showing. |
| `armor_vest` | good | 0.12 tall | doomed | Drawn in doomed.py: a green combat vest laid flat: chest plates and a strap. |
| `fireball` | good | 0.22 tall, glows, no shadow | doomed | Drawn in doomed.py: a white-hot core in orange flame with a ragged tail; additive. |
| `vector_runner` | good | 0.6 tall, glows | vector_world | Drawn in vector.py: a figure in a black suit traced with light: a visor, seams, a diamond on the chest, glowing hands; tint sets the colour. |
| `light_trail` | good | 0.22 tall, glows, no shadow | vector_world | Drawn in vector.py: a ribbon of light, brightest at its top edge; a card laid behind a racer, additive. |
| `light_beam` | good | 3 tall, glows, no shadow | vector_world | Drawn in vector.py: a column of light rising from the floor, bright at its foot and core; additive. |
| `glint` | good | 0.09 tall, glows, no shadow | vector_world | Drawn in vector.py: a white-hot point in a soft halo - a headlight, a beacon; it streaks and flares. |
| `salt_mound` | good | 0.22 tall | salt_flat | Drawn in saltflat.py: a round-topped mound of raked salt, lumpy, damp at its foot; set out in rows, each `scale` a little different. |
| `salt_heap` | good | 0.15 tall | salt_flat | Drawn in saltflat.py: two mounds of salt slumped together, long and low. |
| `salt_pile` | good | 0.12 tall | salt_flat | Drawn in saltflat.py: a small rough shovelful of salt, a clod rolled off its side. |
| `salt_clods` | good | 0.08 tall | salt_flat | Drawn in saltflat.py: a few lumps of salt left lying, of different sizes. |
| `waterfall` | good | 6 tall, no shadow | sky_islands | Drawn in skyisles.py: a sheet of falling water, white at its lip, breaking into mist toward its foot; a card. |
| `island_roots` | good | 2 tall, no shadow | sky_islands | Drawn in skyisles.py: roots and vines dangling under an island's edge; a card. |
| `island_keel` | good | 6 tall, no shadow | sky_islands | Drawn in skyisles.py: the rock under a floating island tapering to a ragged point, banded, roots trailing; a billboard. |
| `rope_rail` | good | 0.42 tall, no shadow | sky_islands | Drawn in skyisles.py: a bridge's railing: a post at every unit and two sagging ropes; a card. |
| `glow_monstera` | good | 0.75 tall, glows | glow_jungle | Drawn in glowjungle.py: the monstera at night, every leaf traced in cyan light. |
| `glow_fern` | good | 0.42 tall, glows | crystal_cave, glow_jungle | Drawn in glowjungle.py: the fern at night, its fronds edged in light. |
| `glow_tree_fern` | good | 2.4 tall, glows | glow_jungle | Drawn in glowjungle.py: the tree fern at night, traced in blue light. |
| `glow_heliconia` | good | 1.1 tall, glows | glow_jungle | Drawn in glowjungle.py: the heliconia at night: leaves edged in green light, the flowers burning pink. |
| `glow_bromeliad` | good | 0.22 tall, glows | crystal_cave, glow_jungle | Drawn in glowjungle.py: the bromeliad at night: violet light, a magenta heart. |
| `glow_liana` | good | 2.4 tall, glows | glow_jungle | Drawn in glowjungle.py: the liana at night, hanging, edged in blue. |
| `glow_pods` | good | 1.1 tall, glows | crystal_cave, glow_jungle | Drawn in glowjungle.py: a curling stalk hung with seed pods glowing from inside. |
| `glow_jungle_card_1` | good | 1.4 tall, glows, no shadow | glow_jungle | Drawn in glowjungle.py: jungle card 1 at night, faintly edged and specked with light. |
| `glow_jungle_card_2` | good | 3.4 tall, glows, no shadow | glow_jungle | Drawn in glowjungle.py: jungle card 2 at night, faintly edged and specked with light. |
| `glow_jungle_card_3` | good | 4 tall, glows, no shadow | glow_jungle | Drawn in glowjungle.py: jungle card 3 at night, faintly edged and specked with light. |
| `glow_jungle_card_4` | good | 4.6 tall, glows, no shadow | glow_jungle | Drawn in glowjungle.py: jungle card 4 at night, faintly edged and specked with light. |
| `ice_spire` | good | 2.4 tall, no shadow | aurora_palace | Drawn in icepalace.py: a tower's spire of ice, a tall faceted crystal. |
| `ice_throne` | good | 1.1 tall | aurora_palace | Drawn in icepalace.py: a throne cut from a block of ice, a high pointed back. |
| `icicles` | good | 0.4 tall, no shadow | aurora_palace | Drawn in icepalace.py: a row of icicles hanging from an eave; a card. |
| `ice_shards` | good | 0.5 tall | aurora_palace | Drawn in icepalace.py: shards of ice breaking up through the snow. |
| `brass_gear` | good | 2 tall, no shadow | clockwork_city | Drawn in clockwork.py: a great toothed brass wheel with spokes and a hub; a card for a wall. |
| `great_clock` | good | 1.6 tall, no shadow | clockwork_city | Drawn in clockwork.py: a tower's great clock: an ivory dial in a brass ring, roman hours; a card. |
| `stasis_pod` | good | 1 tall, glows | derelict_ship |  |
| `shuttle` | good | 2.2 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: nose-on wedge hull in white and orange, lit cockpit and engine pods, landing legs, panel lines and vents. |
| `cargo_container` | good | 1.2 tall | orbital_hangar | Drawn with the toolkit in scifi.py: corrugated orange steel, corner castings, door rods, rust streaking down the ribs. Tint for other colours. |
| `power_loader` | good | 2 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: roll cage, hydraulic arms with forks, hazard stripes on the hip block, a lit work light. |
| `beacon` | good | 0.3 tall, glows, aura | orbital_hangar | Drawn with the toolkit in scifi.py: an amber dome in a wire cage on a squat base; glows, with an aura. |
| `reactor_core` | good | 2.8 tall, glows, aura | orbital_hangar | Drawn with the toolkit in scifi.py: a glowing column in steel collars with coolant pipes; glows, with an aura. |
| `robot_arm` | good | 1.8 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: three orange segments, dark joints, a turntable base, a welding spark. |
| `cables_hang` | good | 1.4 tall, no shadow | orbital_hangar | Drawn with the toolkit in scifi.py: slack loops of cable and a few dangling ends; hangs from a ceiling, no contact shadow. |
| `vending_machine` | good | 1.1 tall, glows, aura | capsule_hotel, neon_street | Drawn with the toolkit in scifi.py: a red steel box, its front a lit window of cans in rows, a glowing strip, coin slot and hatch. |
| `noodle_stall` | good | 1.6 tall, glows | - | Drawn with the toolkit in scifi.py: a counter under a striped awning, red paper lanterns lit, a neon sign of pseudo-letters, pots. |
| `steam` | good | 1.2 tall, no shadow | clockwork_city, neon_street, night_market | A dithered plume, soft and spreading as it rises; see-through by default. |
| `holo_ad` | good | 1.6 tall, glows, no shadow | neon_rooftop, neon_street | A hologram koi in cyan and pink with scanlines, dorsal and pectoral fins; additive by default. |
| `wires_span` | good | 0.75 tall, glows, no shadow | neon_rooftop, neon_street | Drawn with the toolkit in scifi.py: four sagging wires with paper lanterns, a card to sling across a street. |
| `food_cart` | good | 1 tall, glows | neon_rooftop, night_market | Drawn with the toolkit in market.py: a teal cabinet on two wheels, a steel counter with a wok over a roaring burner, stock pots, bowls, a tin roof, a neon menu board and three bare bulbs. |
| `fruit_stall` | good | 0.95 tall, glows | night_market | Drawn with the toolkit in market.py: crates stepped back in three tiers heaped with oranges, apples, limes, bananas and grapes, price cards, a green tarp with a bulb and coloured lights. |
| `gadget_stall` | good | 0.95 tall, glows | night_market | Drawn with the toolkit in market.py: glowing screens on a table in dark cloth, a pegboard of cables, headphones and boxes, a blue tarp with a neon sign along it. |
| `red_lantern` | good | 0.16 tall, glows, no shadow | neon_street, night_market | Drawn with the toolkit in market.py: ribbed red paper glowing from inside, black bands, a gold tassel, a painted pseudo-letter. |
| `lantern_span` | good | 0.6 tall, glows, no shadow | neon_rooftop, night_market | Drawn with the toolkit in market.py: a sagging rope hung with big red lanterns, a card to sling across a lane. |
| `neon_sign` | good | 1.5 tall, glows, aura | night_market | Drawn with the toolkit in market.py: a standing lightbox on a steel post, edged in pink tube and lettered top to bottom. |
| `neon_cocktail` | good | 0.4 tall, glows, no shadow | neon_bar | Drawn with the toolkit in bar.py: a cocktail glass in pink tube with an olive on a stick in green; additive. |
| `neon_fish` | good | 0.32 tall, glows, no shadow | neon_bar | Drawn with the toolkit in bar.py: a fish outline in cyan tube with scales, an eye and bubbles rising; additive. |
| `umbrella` | good | 0.42 tall, glows, no shadow | night_market | Drawn with the toolkit in market.py: a clear canopy beaded with rain, its ribs showing, a glowing shaft from tip to handle. |
| `scooter` | good | 0.42 tall, glows | neon_rooftop, night_market | Drawn with the toolkit in market.py: mint body panels, a dark seat, the front shield with its headlight lit, small fat wheels, a kickstand. |
| `stools_table` | good | 0.26 tall | night_market | Drawn with the toolkit in market.py: a low folding table with two bowls and chopsticks, a red and a blue plastic stool. |
| `power_pole` | good | 3.4 tall, glows | night_market | Drawn with the toolkit in market.py: a concrete pole, crossarm and insulators, a transformer drum, a street lamp, cables looping, posted bills. |
| `water_tower` | good | 1.5 tall | neon_rooftop | Drawn with the toolkit in rooftop.py: a barrel of staves bound with iron hoops under a conical cap, on steel legs with cross bracing and a platform, a ladder. |
| `ac_unit` | good | 0.32 tall | neon_rooftop | Drawn with the toolkit in rooftop.py: a pale steel box on rails, louvres down one side, a round fan grille, a pipe. |
| `rooftop_sign` | good | 2.6 tall, glows, aura | neon_rooftop | Drawn with the toolkit in rooftop.py: three tall panels edged in neon and lettered in bold glowing pseudo-letters, on a steel lattice scaffold with a catwalk. |
| `sky_train` | good | 2.5 tall, glows, no shadow | neon_rooftop | Drawn with the toolkit in rooftop.py: three pale cars with a red stripe and every window lit, on a concrete beam on slim pillars; a card that repeats along its length. |
| `crowd` | good | 0.66 tall, glows | neon_rooftop, night_market | Drawn with the toolkit in market.py: a dozen figures in dark coats at different depths, some under umbrellas (a few lit), hoods, a bag. |
| `noodle_bowl` | good | 0.055 tall | neon_street | Red lacquer bowl seen a little from above: amber broth, noodles, half an egg, a pink swirl of fish cake, green onion, chopsticks across it. Sits on the noodle_stand counter. |
| `stock_pot` | good | 0.11 tall | neon_street | Stainless pot, lid ajar, riveted handles; steam set over it by the noodle_stand. |
| `bowl_stack` | good | 0.075 tall | neon_street | Five white rice bowls with blue bands, stacked. |
| `condiments` | good | 0.07 tall | neon_street | A tray of soy sauce, chilli oil and a cup of chopsticks. |

### Alien and dream

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `alien_egg` | good | 0.35 tall, glows | alien_world, derelict_ship | Redrawn with the toolkit in basics.py: a leathery, mottled egg with a wet sheen, veins glowing faintly green, four lips at its crown parting on a glow. |
| `alien_plant` | good | 1.1 tall, glows | alien_world |  |
| `balloon` | good | 2.6 tall, no shadow | dream_world |  |
| `chess_king` | good | 1.55 tall | dream_chess, dream_world | Drawn with the toolkit in dream.py: the tallest piece, crown and cross, turned marble. |
| `chess_rook` | good | 1.1 tall | dream_chess | Drawn with the toolkit in dream.py: a turned tower with a flared, crenellated top. |
| `chess_knight` | good | 1.2 tall | dream_chess | Drawn with the toolkit in dream.py: a horse head and neck on a turned foot, ridged mane, eye and ear. |
| `chess_bishop` | good | 1.3 tall | dream_chess | Drawn with the toolkit in dream.py: a slender stem and a mitre with its slit, a bead on top. |
| `chess_queen` | good | 1.45 tall | dream_chess | Drawn with the toolkit in dream.py: a tall stem and a beaded coronet with an orb. |
| `melting_clock` | good | 0.6 tall, no shadow | dream_chess, hall_of_doors | Drawn with the toolkit in dream.py: a clock face warped over a ledge, the hanging part stretched and dripping. |
| `hourglass` | good | 0.6 tall | dream_chess | Drawn with the toolkit in dream.py: glass bulbs in a wooden frame, sand running into a heap, a gleam. |
| `stone_arch` | good | 2.4 tall | dream_chess | Drawn with the toolkit in dream.py: coursed piers and a round arch of voussoirs with a keystone, open in the middle. |
| `stair_float` | good | 2 tall | dream_chess, hall_of_doors | Drawn with the toolkit in dream.py: a flight of stairs on a soffit, broken off at both ends, stones falling. |
| `paper_boat` | good | 0.3 tall | dream_chess, hall_of_doors | Drawn with the toolkit in dream.py: folded planes, a peak and a crease. |
| `jellyfish` | good | 0.9 tall, glows, no shadow | drowned_library, kelp_forest | A bell of light frilled at the rim, oral arms and tentacles; additive and glowing, no shadow. |
| `sky_lantern` | good | 0.34 tall, glows, aura, no shadow | drowned_library, hall_of_doors | Drawn with the toolkit in dream.py: a tapering paper shade lit from inside, the flame at its foot, a wire ring; aura. |
| `book_fly` | good | 0.3 tall, no shadow | drowned_library, hall_of_doors, mansion_library | Drawn with the toolkit in dream.py: an open book with its covers raised as wings and its pages fanned. |
| `chess_pawn` | good | 0.9 tall | dream_chess, dream_world | Drawn with the toolkit in dream.py: a turned marble pawn (lathe profile), faint veins. Tint dark for the other side. |
| `door_frame` | good | 1.1 tall | dream_chess, dream_world, hall_of_doors, salt_flat |  |
| `floating_rock` | good | 1.6 tall, no shadow | dream_world, sky_islands |  |
| `koi` | good | 0.35 tall, no shadow | dream_chess, dream_world, drowned_library, hall_of_doors |  |
| `orb` | good | 0.2 tall, glows, aura, no shadow | dream_world |  |
| `pocket_watch` | good | 0.8 tall, no shadow | dream_world |  |
| `sky_whale` | good | 2 tall, glows, no shadow | dream_world, drowned_library, salt_flat |  |

### Jungle

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `banana_plant` | good | 1.7 tall | jungle_temple |  |
| `monstera` | good | 0.75 tall | jungle_temple |  |
| `tree_fern` | good | 2.4 tall | jungle_temple |  |
| `heliconia` | good | 1.1 tall | jungle_temple |  |
| `bromeliad` | good | 0.22 tall | jungle_temple |  |
| `liana` | good | 2.4 tall, no shadow | jungle_temple, temple_inside |  |
| `kapok` | good | 7.5 tall | glow_jungle, jungle_temple | An emergent tree: its crown clears a 4-unit canopy. |
| `canopy_crown` | good | 1.2 tall, no shadow | jungle_temple | Set on jungle wall tops so the canopy edge is crowns, not a hedge. |
| `stone_head` | good | 1.5 tall | glow_jungle, jungle_temple |  |
| `stela` | good | 2.1 tall | jungle_temple, temple_inside |  |

### Ruins

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `broken_column` | good | 1 tall | - |  |
| `column_drum` | good | 0.42 tall | ancient_ruins, cathedral_ruin | Flutes now run back along the drum, so it reads as a column; the end face is lit and stands proud of the body on a shadowed rim, scalloped by the flutes, a worn ring and the dowel hole. |
| `marble_head` | good | 1.1 tall | ancient_ruins |  |
| `amphora` | good | 0.36 tall | ancient_ruins |  |
| `cow_skull` | good | 0.2 tall | ghost_town, gold_mine, red_canyon, saloon | Drawn with the toolkit in desert.py: a bleached longhorn skull: dark sockets and nose, horns curving out and up. |
| `clay_pot` | good | 0.34 tall | red_canyon, temple_inside | Drawn with the toolkit in desert.py: a round white pot painted in black bands and a zigzag, turned on a lathe. |
| `windpump` | good | 4.2 tall | ghost_town | Drawn with the toolkit in desert.py: a lattice tower of four splayed legs, cross-braced, a wheel of galvanised blades with its tail vane. |
| `water_trough` | good | 0.4 tall | - | Drawn with the toolkit in desert.py: grey boards on short legs, water near the brim. |
| `wagon_wheel` | good | 0.55 tall | ghost_town | Drawn with the toolkit in desert.py: an iron-shod rim, twelve spokes, a heavy hub. |
| `cypress` | good | 4 tall | ancient_ruins |  |
| `saguaro` | good | 3.2 tall | ghost_town, gold_mine, red_canyon | Drawn with the toolkit in desert.py: a ribbed column with two arms bending up, spines along the ribs, white blossoms on the crown. |
| `prickly_pear` | good | 0.6 tall | ghost_town, gold_mine, red_canyon | Drawn with the toolkit in desert.py: oval pads growing out of one another, spines, magenta fruit along the top. |
| `tumbleweed` | good | 0.45 tall | ghost_town, gold_mine, red_canyon, saloon | Drawn with the toolkit in desert.py: a loose ball of wiry dry stems, the light coming through. |
| `olive_tree` | good | 2.2 tall | ancient_ruins |  |
| `poppies` | good | 0.24 tall | ancient_ruins |  |
| `dry_tuft` | good | 0.36 tall | ancient_ruins, ghost_town, gold_mine, red_canyon, tropical_beach |  |

### Beach

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `palm_lean` | good | 3 tall | tropical_beach |  |
| `coconuts` | good | 0.1 tall | tropical_beach |  |
| `canoe` | good | 0.3 tall | tropical_beach |  |
| `tiki_torch` | good | 0.75 tall, glows, aura, no shadow | tropical_beach |  |
| `hammock` | good | 0.55 tall | tropical_beach |  |
| `driftwood` | good | 0.2 tall | tropical_beach |  |
| `surf` | good | 0.1 tall, no shadow | tropical_beach | A row along a waterline reads from eye height, where foam decals are edge-on. |
| `surf_glow` | good | 0.1 tall, glows, no shadow | tropical_beach |  |

### Animals

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `jaguar` | good | 0.34 tall, glows | glow_jungle, jungle_temple | Redrawn with the toolkit in basics.py: prowling, side on: a long low body, heavy shoulders, a broad head, rosettes spread over a golden coat, a pale belly; the eyes glow. |
| `macaw` | good | 0.3 tall | jungle_temple |  |
| `goat` | good | 0.34 tall | ancient_ruins | Redrawn with the toolkit in basics.py: compact and deep-bodied on short sturdy legs, a piebald coat, horns swept back, a beard, the tail flicked up. |
| `crab` | good | 0.08 tall | kelp_forest, tropical_beach |  |
| `seagull` | good | 0.14 tall, no shadow | sky_islands, tropical_beach |  |
| `heron` | good | 0.95 tall | bayou | Drawn with the toolkit in swamp.py: a grey heron: long legs, the neck in an S, a yellow dagger of a beak, the black crest. |
| `deer` | good | 0.62 tall | winter_woods | Drawn with the toolkit in forest.py: a deer side on: russet coat, pale belly and throat, slim legs, big ears, an antlered head up, a white tail. |
| `black_cat` | good | 0.13 tall, glows | neon_rooftop | Drawn with the toolkit in rooftop.py: sitting with its back to you, ears up, its tail round its feet, one green eye catching the light. |
| `alligator` | good | 0.2 tall, glows, no shadow | bayou | Drawn with the toolkit in swamp.py: only the snout, the eyes (which catch the light) and the ridged back above the water. |
| `fireflies` | good | 1.2 tall, glows, no shadow | bayou | Drawn with the toolkit in swamp.py: a loose swarm of tiny glowing lights with soft halos; additive. |
| `fish_school` | good | 0.9 tall, no shadow | aquarium, kelp_forest | Drawn with the toolkit in sea.py: thirty-odd silvery fish headed one way, dark backs, thicker in the middle of the shoal. |
| `whale_shark` | good | 1.36 tall, no shadow | aquarium | Drawn with the toolkit in aquarium.py: the broad flat head with its mouth at the front, ridges down the flanks, tall first dorsal, crescent tail; pale spots and broken bars on a blue-grey back, white belly. |
| `manta_ray` | good | 0.9 tall, no shadow | aquarium | Drawn with the toolkit in aquarium.py: seen from below: pointed wings, curled cephalic fins either side of the mouth, gill slits, a few dark blotches on the white belly shading grey to the dark margins. |
| `reef_shark` | good | 0.25 tall, no shadow | aquarium | Drawn with the toolkit in aquarium.py: a blacktip: sleek bronze-grey body, pointed snout, gill slits, white belly, black tips on the dorsal, pectoral and tail. |
| `sea_turtle` | good | 0.3 tall, no shadow | aquarium | Drawn with the toolkit in aquarium.py: a green turtle from a little above: amber scutes and a rim of small plates, the head reaching forward, long front flippers swept back. |
| `clownfish` | good | 0.07 tall, no shadow | aquarium | Drawn with the toolkit in aquarium.py: a pair: orange with three black-edged white bands and black-edged fins. |
| `angelfish` | good | 0.13 tall, no shadow | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: an emperor angelfish: clean diagonal stripes of yellow and blue, a black mask edged pale blue, a blue face, a yellow tail. |
| `blue_tang` | good | 0.08 tall, no shadow | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: royal blue with the black palette loop, black-edged fins and a yellow tail. |
| `reef_shoal` | good | 0.5 tall, no shadow | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: three dozen anthias, orange-pink with a few purple and gold, spaced so they never clump. |
| `sea_nettle` | good | 0.45 tall, glows, no shadow | aquarium | Drawn with the toolkit in aquarium.py: a golden bell striped rust to its scalloped rim, long maroon tentacles, four pale frilled arms twisting; half see-through. |
| `moon_jelly` | good | 0.12 tall, glows, no shadow | aquarium, neon_bar | Drawn with the toolkit in aquarium.py: a clear saucer with the four lilac crescents in a ring, a fringe of short tentacles; additive and glowing. |
| `bubbles` | good | 1.2 tall, no shadow | aquarium, kelp_forest | Drawn with the toolkit in sea.py: a column of bubbles swelling as they rise, bright rings with a glint; additive. |
| `crow` | good | 0.2 tall | autumn_lane, haunted_house, red_canyon, village_green | Drawn with the toolkit in village.py: glossy black with a blue sheen, the head up, a heavy beak. |
| `bats` | good | 0.6 tall, no shadow | haunted_house | Drawn with the toolkit in haunted.py: black bat silhouettes, wings spread or beating, at different sizes. |

### Cards and parts

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `jungle_card_1` | good | 1.4 tall | jungle_temple, tropical_beach | The front of a jungle fringe: bushes alone. |
| `jungle_card_2` | good | 3.4 tall | jungle_temple, tropical_beach | A few trees with bushes in front. |
| `jungle_card_3` | good | 4 tall | jungle_temple, tropical_beach | More trees, tall ones with crowns. |
| `jungle_card_4` | good | 4.6 tall | jungle_temple, tropical_beach | The back: a dense wall of trunks, crowns, palms and bushes. Repeats every 8 units. |
| `forest_card_1` | good | 1.2 tall | haunted_house, woodland_night | The front of a forest fringe: bushes, ferns and grass. |
| `forest_card_2` | good | 3 tall | haunted_house, woodland_night | Young spruce and birch with bushes in front. |
| `forest_card_3` | good | 4 tall | haunted_house, woodland_night | Spruce, oak and birch with gaps between them. |
| `forest_card_4` | good | 4.8 tall | haunted_house, woodland_night | The back: a dense wall of spruce and oak over undergrowth, darkest. Repeats every 8 units. |
| `autumn_card_1` | good | 1.2 tall | autumn_lane | The front of an autumn fringe: turned bushes, ferns and grass. |
| `autumn_card_2` | good | 3 tall | autumn_lane | Young gold birch and a spruce with turned bushes in front. |
| `autumn_card_3` | good | 4 tall | autumn_lane | Oak, birch and spruce with gaps between them. |
| `autumn_card_4` | good | 4.8 tall | autumn_lane | The back: a dense wall of turned oak and green spruce over undergrowth. |
| `winter_card_1` | good | 1.2 tall | winter_woods | The front of a winter fringe: bushes under snow and dry tufts. |
| `winter_card_2` | good | 3 tall | winter_woods | Young snowy spruce and bare birch with snowy bushes in front. |
| `winter_card_3` | good | 4 tall | winter_woods | Snowy spruce, bare oak and birch with gaps between them. |
| `winter_card_4` | good | 4.8 tall | winter_woods | The back: a dense stand of snowy spruce with bare oaks. |
| `swamp_card_1` | good | 1.4 tall | bayou | The front of a swamp fringe: cattails, reeds and cypress knees. |
| `swamp_card_2` | good | 3 tall | bayou | Young cypresses among cattails and knees (the moss that hung in the air on its own bough is gone). |
| `swamp_card_3` | good | 3.9 tall | bayou | A looser stand of cypresses hung with moss, cattails and knees at their feet. |
| `kelp_card_1` | good | 5 tall | kelp_forest | The front of a kelp fringe: a few stalks. |
| `kelp_card_2` | good | 5.8 tall | kelp_forest | The back: a dense stand of kelp. |
| `palm_trunk` | good | 3.2 tall | tropical_beach | The palm without its crown, for palm_3d. |
| `palm_crown` | good | 3.2 tall, no shadow | tropical_beach | The palm's crown alone, in the same frame as the trunk. |
| `glass_pane` | good | 1 tall | aquarium, neon_bar, orbital_hangar | A plain pane for the glass pass. |

### Not yet sorted

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `swamp_card_4` | good | 4.6 tall | bayou | The back: a dense stand of tall bald cypresses hung with moss, their crowns high enough to hide the wall's top. |
| `goods_apples` | good | 0.22 tall | village_green | Drawn with the toolkit in village.py: a heap of red apples on a shallow tray, for a stall's table (the `market_stand` heaps them). |
| `goods_cabbages` | good | 0.22 tall | village_green | Cabbages heaped on a tray, as the apples. |
| `goods_loaves` | good | 0.22 tall | village_green | Loaves heaped on a tray, as the apples. |
| `piano` | good | 0.46 tall | saloon | An upright: a dark case on carved legs, the fall open on ivory and ebony keys, brass sconces, music on the stand. Stand it as a card against a wall. |
| `card_table` | good | 0.3 tall | saloon | A round table of green baize mid-game, seen a little from above: cards, stacks of chips, a bottle and two glasses. |
| `saloon_chair` | good | 0.32 tall | saloon | A bentwood chair, side on: the hooped back, the round seat, splayed legs. |
| `spittoon` | good | 0.09 tall | saloon | Brass, squat and bellied, a wide funnel mouth. |
| `pick_shovel` | good | 0.46 tall | gold_mine | A pick and a shovel leaning together, their hickory handles worn pale. |
| `dynamite_crate` | good | 0.2 tall | gold_mine | A crate stencilled DYNAMITE, its lid off, red sticks standing in it with their fuses. |
| `ore_heap` | good | 0.16 tall | gold_mine | Broken ore in a mound, quartz in some lumps, a glint of gold; the `ore_cart` heaps it too. |
| `golden_idol` | good | 0.38 tall | temple_inside | Drawn with the toolkit in temple.py: a squat golden jaguar crouched on a carved pedestal, jade in its eyes and collar. |
| `treasure` | good | 0.1 tall | temple_inside | Gold coins heaped and scattered, a jade mask, a golden cup on its side. |

## Characters (29)

Pixel-art grids written as text in `scripts/characters.py`, each with a back view.

| character | status | used in | notes |
|---|---|---|---|
| `cultist` | good | garden_encounter, gui_lantern, gui_menus, neon_street, post_presets, tunnel_encounter, woodland_night |  |
| `scientist` | good | aquarium, bunker_lab, clockwork_city, coast_lighthouse, gui_lantern, night_market, orbital_hangar, tunnel_encounter |  |
| `guard` | good | garden_encounter, gui_menus, post_presets, rain_alley, rainy_street |  |
| `nurse` | good | ghost_corridor, gui_hud |  |
| `spiritualist` | good | cathedral_ruin, chapel_graveyard, gui_themes, gui_trade, library_medium, mansion_library |  |
| `ghost` | good | chapel_graveyard, garden_encounter, ghost_corridor, ghost_town, gui_hud, gui_menus, haunted_house, post_presets, saloon, woodland_night |  |
| `hybrid` | good | gui_lantern, sewer_tunnels, tunnel_encounter |  |
| `soldier` | good | castle_keep, doomed |  |
| `knight` | good | castle_keep, misty_moor, village_green |  |
| `child` | good | aquarium, autumn_lane, night_market, village_green, winter_lake, winter_woods | The head narrowed to ten pixels with a fringe, the eyes closer together, a small mouth and a tapered chin, so it reads as a child rather than a round mask; back view. |
| `creature` | good | castle_keep, crystal_cave |  |
| `robot` | good | clockwork_city, crystal_cave |  |
| `shopkeeper` | good | clockwork_city, ghost_town, neon_street, night_market, saloon, village_green |  |
| `astronaut` | good | alien_world, moon_base, orbital_hangar, space_station |  |
| `android` | good | neon_bar, neon_street, orbital_hangar, space_station |  |
| `alien` | good | alien_world, derelict_ship | A familiar archetype; could be made stranger. |
| `dreamer` | good | capsule_hotel, dream_chess, dream_world, drowned_library, hall_of_doors, salt_flat | Eyes closed now (two soft lines, not dark pupils), so she reads as a sleepwalker; nightgown and candle. |
| `claude` | good | claude_study | Claude's own avatar. |
| `explorer` | good | aquarium, aurora_palace, glow_jungle, jungle_temple, red_canyon, sky_islands, temple_inside |  |
| `hoplite` | good | ancient_ruins |  |
| `castaway` | good | tropical_beach |  |
| `diver` | good | aquarium, kelp_forest | A brass diving helmet with a round faceplate and an air hose, a canvas suit, a weight belt, heavy boots. |
| `runner` | good | neon_bar, neon_rooftop, neon_street, night_market | A cyberpunk: dark hair with a pink streak, a lit cyan visor, a black jacket striped in neon. |
| `samurai` | good | night_market | A street samurai: topknot, glowing red visor, a long black coat lined in crimson over a grey shirt and a gold belt, a sword slung across the back with its hilt over the shoulder, one chrome arm; back view. |
| `hacker` | good | capsule_hotel, neon_bar | Hood up in deep violet, cyan goggles glowing in the shadow of it, a deck held in both hands with a green screen, cargo trousers, white sneakers on lit pink soles; back view. |
| `cowboy` | good | ghost_town, gold_mine, neon_bar, night_market, red_canyon, saloon | A wide-brimmed hat, moustache, red bandana, a vest over a tan shirt, a gun belt, jeans and boots; for the canyon. |
| `witch` | good | aurora_palace, autumn_lane, neon_bar | A crooked pointed hat banded in purple, green skin, glowing yellow eyes, a robe, a lit lantern at her side. |
| `farmer` | good | village_green | A straw hat, plaid shirt and blue overalls, a pitchfork taller than him. |
| `pirate` | good | bayou | A gold-edged tricorn, an eye patch and beard, a red coat with gold buttons, a cutlass. |

## Decals (27)

Stamps blended into floors, walls and ceilings. `grime` stamps some of them on its own, and `contact_shadow` goes under every prop that stands on the ground.

| decal | status | used in | notes |
|---|---|---|---|
| `puddle` | good | coast_lighthouse, rainy_street, woodland_night |  |
| `puddle_dark` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, sewer_tunnels, woodland_night |  |
| `puddle_shine` | good | coast_lighthouse, neon_street, night_market, rain_alley, rainy_street, sewer_tunnels |  |
| `stain` | good | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, sewer_tunnels, woodland_night | A ragged edge, darker along the tide line where it dried, blotchy inside, drops round it and short runs from its foot. |
| `stain_rust` | good | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, orbital_hangar, rainy_street, sewer_tunnels | As stain, in rust. |
| `splatter` | good | doomed |  |
| `splatter_dark` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, sewer_tunnels |  |
| `vines` | good | jungle_temple, rainy_street |  |
| `moss_patch` | good | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, jungle_temple, rainy_street, sewer_tunnels, temple_inside, woodland_night | A cushion of rounded clumps lit along their tops and dark under them, speckled, a few stray tufts round it. |
| `crack` | good | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, rainy_street, sewer_tunnels |  |
| `scorch` | good | bunker_lab, cathedral_ruin, derelict_ship, sewer_tunnels, tropical_beach |  |
| `leak` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, rainy_street, sewer_tunnels |  |
| `cobweb` | good | bunker_lab, castle_keep, temple_inside |  |
| `rune_mark` | good | - |  |
| `drain` | good | bunker_lab, neon_street, night_market, rainy_street, sewer_tunnels |  |
| `contact_shadow` | good | 62 scenes |  |
| `pad_marking` | good | moon_base, orbital_hangar | A painted landing ring with an H and a dashed outer ring, worn in patches. |
| `rover_tracks` | good | moon_base | Drawn with the toolkit in moon.py: two tracks of chevron treads pressed into dust. |
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
| `lily_pads` | good | bayou, jungle_temple |  |

### Not yet sorted

| decal | status | used in | notes |
|---|---|---|---|
| `wanted_poster` | good | saloon | Yellowed paper with a torn corner: WANTED over a sketched face in a hat, $500. |

## Skies (13)

| sky | status | used in | notes |
|---|---|---|---|
| `night` | good | 21 scenes |  |
| `dusk` | good | autumn_lane, coast_lighthouse, misty_moor |  |
| `storm` | good | coast_lighthouse, rain_alley, rainy_street | Could use darker cloud masses. |
| `day` | good | aquarium, cathedral_ruin, ghost_town, jungle_temple, kelp_forest, red_canyon, saloon, salt_flat, sky_islands, temple_inside, tropical_beach, village_green, winter_lake, winter_woods |  |
| `overcast` | good | doomed, winter_woods |  |
| `blood` | good | - |  |
| `space` | good | moon_base, orbital_hangar, space_station |  |
| `alien` | good | alien_world |  |
| `dream` | good | dream_chess, dream_world, drowned_library, hall_of_doors, salt_flat |  |
| `sunset` | good | bayou, clockwork_city, ghost_town, gold_mine, red_canyon, salt_flat, tropical_beach |  |
| `golden` | good | ancient_ruins, autumn_lane, bayou, sky_islands, woodland_night |  |
| `vector` | good | vector_world | Black to violet with a magenta glow at the horizon and a few stars; pair it with a striped sun. |
| `aurora` | good | aurora_palace | A clear arctic night with the aurora across it, no two stretches alike: a curtain of green rays of every width and height fringed pink, a pleated teal ribbon, red-tipped rays to the west, a faint high arc; brightest due north; they glow. |

## Skylines (6)

| skyline | status | used in | notes |
|---|---|---|---|
| `mountains` | good | alien_world, jungle_temple, salt_flat, winter_lake |  |
| `hills` | good | misty_moor |  |
| `treeline` | good | chapel_graveyard |  |
| `city` | good | neon_rooftop, neon_street, night_market | Window grid is regular; vary building tops (spires, water towers). |
| `islands` | good | ancient_ruins, tropical_beach | Flat-topped and lopsided with a low strip of beach either side, so an island and its reflection read as land on the water, not a saucer. |
| `jungle` | good | jungle_temple |  |

## Sky objects (7)

| object | status | used in | notes |
|---|---|---|---|
| `planet` | good | - |  |
| `ringed` | good | alien_world, orbital_hangar, space_station |  |
| `moon` | good | alien_world, dream_chess, dream_world, drowned_library, orbital_hangar, space_station |  |
| `earth` | good | moon_base | Oceans, green and desert continents and cloud from noise mapped onto the sphere, polar ice, a blue limb; the night side dark. |
| `sun` | good | orbital_hangar, space_station |  |
| `eye` | good | dream_world |  |
| `clock` | good | dream_chess | A cream face in a dark rim, twelve ticks, two hands set by `time`, its bottom running like wax (`melt`). |

## Scatter sets (18)

Named mixes for `scatter`; repeats in the contents act as weights.

| set | status | contents | used in | notes |
|---|---|---|---|---|
| `stones` | good | rocks x3, boulder | chapel_graveyard |  |
| `snow` | good | rocks x3, boulder_snow | winter_lake, winter_woods | The stones set for winter: its boulder is under snow, not moss. |
| `rubble` | good | rubble x2, rocks, broken_barrel | cathedral_ruin, rainy_street |  |
| `forest` | good | rocks x2, log, stump, mushrooms, grass_tuft x2, fern, bush | woodland_night |  |
| `undergrowth` | good | grass_tuft x3, fern, bush, mushrooms | cathedral_ruin, chapel_graveyard, woodland_night |  |
| `autumn` | good | grass_tuft x2, fern, bush_autumn x2, mushrooms | autumn_lane | The undergrowth set for the fall: its bush turned. |
| `shore` | good | rocks x3, boulder, reeds, bones | - |  |
| `litter` | good | sack, bucket, crate, barrel, broken_barrel, bones | neon_street, rain_alley |  |
| `wreckage` | good | rubble x2, broken_barrel, rocks, bones, sack, bucket | bunker_lab, cathedral_ruin, derelict_ship, sewer_tunnels |  |
| `cave` | good | rocks x3, stalagmite, glowshroom, crystal, bones | crystal_cave |  |
| `alien` | good | rocks x2, crystal, glowshroom, alien_plant, alien_egg | alien_world |  |
| `derelict` | good | rubble x2, sci_crate, bones, rocks, alien_egg | derelict_ship |  |
| `jungle` | good | fern x3, monstera, bromeliad x2, heliconia, mushrooms | jungle_temple |  |
| `beach` | good | coconuts, driftwood, rocks x2, crab, dry_tuft | tropical_beach |  |
| `ruins` | good | column_drum, rubble, rocks x2, poppies, dry_tuft x2, amphora | ancient_ruins |  |
| `desert` | good | rocks x3, prickly_pear, tumbleweed, cow_skull, dry_tuft | ghost_town, gold_mine, red_canyon | Rocks with the odd prickly pear, tumbleweed, skull and dry tuft. |
| `swamp` | good | cattails x2, reeds, cypress_knees, rocks | - | Cattails and reeds with cypress knees and the odd rock. |
| `seabed` | good | rocks x3, crab, boulder | kelp_forest | Rocks with the odd crab and boulder. |

## Fringe sets (7)

The cards a `fringe` wall stands in front of its open faces, back to front.

| set | status | cards | used in | notes |
|---|---|---|---|---|
| `jungle` | good | jungle_card_4, jungle_card_3, jungle_card_2, jungle_card_1 | jungle_temple, tropical_beach | Four cards: bushes alone at the front, a dense wall of trees, crowns and bushes at the back. |
| `forest` | good | forest_card_4, forest_card_3, forest_card_2, forest_card_1 | haunted_house, woodland_night | Four cards: bushes, ferns and grass at the front, a dense wall of spruce and oak at the back. Keep the wall behind lower (2-2.6) than the trees. |
| `forest_autumn` | good | autumn_card_4, autumn_card_3, autumn_card_2, autumn_card_1 | autumn_lane | The forest fringe in October: oak, birch and bush turned, the spruce among them still green. |
| `forest_snow` | good | winter_card_4, winter_card_3, winter_card_2, winter_card_1 | winter_woods | The forest fringe in winter: snowy spruce, bare oak and birch with snow on their limbs, bushes under snow. |
| `swamp` | good | swamp_card_4, swamp_card_3, swamp_card_2, swamp_card_1 | bayou | Four cards: cattails and knees, then young cypresses, then a looser stand, then a dense one. The bayou spreads them three cells deep with `wander`. |
| `kelp` | good | kelp_card_2, kelp_card_1 | kelp_forest | Two cards: a few stalks, then a dense stand. |
| `glow_jungle` | good | glow_jungle_card_4, glow_jungle_card_3, glow_jungle_card_2, glow_jungle_card_1 | glow_jungle | Four cards: the jungle fringe at night, faintly edged and specked with light. |

## Facade styles (6)

The looks a `facade` can give its buildings (`scripts/buildings.py`); each building is drawn in layers - wall, frames and glass, drapes, rooms.

| style | status | used in | notes |
|---|---|---|---|
| `brick` | good | rain_alley | Red and brown brick, painted sash windows, curtains and blinds, shops. |
| `sooty` | good | rain_alley | Soot-blackened tenements, dark frames. |
| `plaster` | good | - | Washed plaster; fine on the review sheet, though no example uses it yet. |
| `neon` | good | neon_rooftop, neon_street, night_market | Concrete panels with form-tie holes, neon signs over the shops and up the walls, blade signs on their own cards, roller shutters, air conditioners, rooms lit pink, blue and green. |
| `timber` | good | village_green | Timber framing over limewash and ochre - posts at the bays and jambs, rails at the floors, sills and heads, braces or close studding - leaded casements, plank doors, and a roof layer: a gable end, or thatch or tiles set back behind the eave, chimneys. Other styles unchanged. |
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

## Objects (14)

Things too big for a billboard, built in 3D out of flat panels (`scripts/objects.py`).

| object | status | used in | notes |
|---|---|---|---|
| `car` | good | rain_alley | A saloon from panels, laid out as the user drew it: the overall box with the car's outline on its sides, hood and trunk lid across it at the belt (body 60%, glass 40%), the roof, glass windows with seats, dashboard and steering wheel inside, four wheels set in under the body in dark wells, a floor pan and a soft shadow; `paint`, `lights`. Proportions and handles tuned with the user. |
| `noodle_stand` | good | neon_street | Counter, awning, valance, noren and sign as panels; bowls, pot, tray, lanterns and stools as billboards, with its own lamp and lantern lights. |
| `rock_wall` | good | aquarium, crystal_cave, ghost_town, gold_mine, neon_bar, red_canyon | Laid out as the user drew it: overlapping pieces along a wall's foot, each in plan a rounded mass of a few broad faces jutting from the wall (the user's sharper zigzag read as spikes; a few spikes and notches are left), each its own height, a trim of faces along its top cut by one long smooth wavy edge, a flat top (inset a texel, so it never shows past the faces), plants on the rim. Kinds `stone`, `reef`, `sandstone`, `snow`, `cave`, `lumen` (glowing moss); `lining` lines every wall face of some map cells. The faces cut from one solid block of stone. Seen from above its tops are flat with the trim standing round them, as Build's were. |
| `boulder` | good | aquarium, autumn_lane, coast_lighthouse, crystal_cave, misty_moor, neon_bar, red_canyon, winter_woods, woodland_night | A low-poly mass, every face a triangle: an irregular foot, a belly, drawn-in shoulders, a peak off its centre; closed from every side. Plants on top by count. |
| `column` | good | ancient_ruins, cathedral_ruin, gold_mine, temple_inside, tropical_beach | A column or a post: a prism of `sides` faces (an octagon by default), tapering if `top` is under 1, a plinth (`base`) and a capital if asked; stone cut from the solid rock as rock is, or `wood` - weathered timber, the grain running up it, dark and grown over below `wet` where it stands in water. Built for the pier's piles first; the cathedral's piers are `ashlar` (dressed stone in drums) with plinths and capitals, one `broken` off ragged. The ruins' columns are Greek: `flutes` (20 faces, each hollowed, so it takes the light on one side and shadow on the other) and `doric` (an echinus widening under a square abacus), in `marble` laid in drums; `fill` lifts a backlit column's dark side. |
| `beam` | good | ancient_ruins, cathedral_ruin, gold_mine, temple_inside | A squared timber or stone lintel lying level, `length` along the way it faces, its underside at the placement's `z`; timber's grain runs along it. Wall plates on the cathedral's piers, and one fallen on the floor; the architraves and cornices over the ruins' columns. |
| `crystal_cluster` | good | crystal_cave | The user's idea: crystals whose facets refract. Hexagonal prisms with pointed tips from a bed of rock, every facet a panel with its own clarity (clear across the middle, milky toward the base, bright edges) and its own bend: drawn with the glass, each facet shows the frame drawn so far shifted by one offset from the way it is turned (Renderer._bend), so it shows one coherent piece of what is behind, the colours parting a little at the edges. Strongest with glowing things behind. |

### Not yet sorted

| object | status | used in | notes |
|---|---|---|---|
| `trough` | good | ghost_town | A horse trough of weathered boards (`_wood` with `boards`: a seam between each, each its own tone), a rim, still water a hand below it, a soft shadow. Replaces the `water_trough` billboard in the ghost town. |
| `shed_roof` | good | - | A roof of boards sloping down to its front edge, the boards running down the slope. The western facade builds one over every porch (ghost_town), sloping from the front down to the fascia so it shows from the street. |
| `gable_roof` | good | - | A gabled roof of boards with gable ends of upright boards, `walls` under it (`inset` back from its front). The western facade builds one behind every false front (ghost_town): the building's body, low enough for the front to hide. |
| `market_stand` | good | village_green | The market stall in 3D, as the noodle stand: a trestle table of weathered boards with a striped skirt (the awning's valance, in step), four poles, a striped awning sloping down to the front with a scalloped valance round it; `goods_*` heaped on the table, crates and a sack by it, as billboards. Replaces the `market_stall` billboard in the village. |
| `saloon_bar` | good | saloon | A saloon's counter in 3D, 0.38 tall: raised mahogany panels between pilasters, a polished top overhanging the drinkers' side, the bartender's shelves behind, a brass foot rail on brackets, bottles on it. |
| `rails` | good | gold_mine | A narrow track: two iron rails on wooden sleepers every 0.22, their tops worn bright. |
| `ore_cart` | good | gold_mine | A riveted iron tub gone to rust (`_iron_side`: rivets along its lip and foot, rust running down) on a low frame and four small wheels set to the rails, ore heaped in it. |

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
| `classic` | good | 55 scenes |  |
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
| `caption` | good | 48 scenes |  |
| `choice` | good | gui_menus, gui_themes, gui_trade |  |
| `title` | good | gui_menus |  |
| `panel` | good | bunker_lab, gui_lantern |  |
| `toast` | good | gui_hud |  |
| `prompt` | good | bunker_lab, castle_keep, gui_lantern |  |
| `bars` | good | bunker_lab, gui_hud |  |
| `counter` | good | bunker_lab, gui_hud |  |
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
| `ashfall` | good | - |  |
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

## Example scenes (63)

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
| `haunted_house` | good | 4 | haunted_front, haunted_hall, haunted_parlour, haunted_ghost | Halloween at the old house: the front with jack-o'-lanterns and bats, the hall's grand stair and landing, the parlour, the ghost on the stairs. |
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
| `kelp_forest` | good | 4 | sea_kelp, sea_diver, sea_shoal, sea_night | A kelp forest in teal water: a wreck with its mast, a diver with bubbles rising, a shoal; a night dive by flashlight with jellyfish. |
| `aquarium` | good | 8 | aquarium_hall, aquarium_manta, aquarium_tunnel, aquarium_jellies, aquarium_reef, aquarium_moon, aquarium_diver, aquarium_rockwork | A dark hall before the great window (whale shark, manta, a diver cleaning the glass, silhouettes, the floor mirroring it); the manta from below; the tunnel; sea nettles against blue; the reef tank; inside the ocean tank by a boulder. The big tanks' backs are rockwork against open water. |
| `coast_lighthouse` | good | 4 | coast_tower, coast_jetty | The shore rocks are the redrawn boulders now, not grey lumps; sand and water redrawn too. |
| `rainy_street` | good | 4 | street_rain, street_lightning |  |
| `rain_alley` | good | 5 | alley_street, alley_rain, alley_glass, alley_storm, alley_cars |  |
| `neon_street` | good | 5 | neon_street, neon_stall, neon_signs, neon_runner, neon_counter | The neon facade style in the rain: signs, blade signs, lantern wires, a hologram koi, a noodle stall, vending machines, steam, the runner; bloom on the neon. |
| `night_market` | good | 5 | market_lane, market_cart, market_puddle, market_runner, market_samurai | A lane of stalls between neon fronts in the rain: lantern strings overhead, food carts, fruit and gadget stalls, a crowd; the cart close up; the lanterns in the wet; the runner under a lit umbrella. |
| `neon_bar` | good | 5 | bar_room, bar_tank, bar_arcade, bar_bartender, bar_hacker | A small smoky bar: glowing shelves, the counter and stools, a jukebox and booths, a reef tank in the back wall, the arcade row mirrored in the floor, the bartender. |
| `neon_rooftop` | good | 4 | rooftop_canyon, rooftop_down, rooftop_train, rooftop_cat | From a roof five storeys up: the neon canyon below with lanterns and a holo koi, the runner and a black cat on the ledge; straight down past the blade signs; the elevated train from the street. |
| `capsule_hotel` | good | 4 | capsule_corridor, capsule_berths, capsule_sleepwalker, capsule_vending | A corridor between two walls of berths at 4 a.m.: the berths up close, the sleepwalker with her candle, the hacker at the vending machine. |
| `doomed` | good | 4 | doomed_pit, doomed_overview, doomed_fight, doomed_window | The slime pit: a walkway zigzagging over glowing sludge, green banded walls, barrels, zombified soldiers; the HUD with a pistol; the pit from above; a shotgun going off and a fireball coming in; the window onto the rock. |
| `vector_world` | good | 5 | vector_sunset, vector_racers, vector_beacon, vector_core, vector_runner | A city of light on the grid: towers ruled in neon, racers trailing light down the avenue under a striped sun, a black core over a plaza of light beams, a beacon's flare, a runner in a suit of light. |
| `salt_flat` | good | 5 | salt_sunset, salt_door, salt_noon, salt_night, salt_whale | A salt flat after rain mirroring the sky: a girl with a candle at sunset, a door standing alone, raked mounds at noon, the stars doubled, a whale over the mirror. |
| `sky_islands` | good | 5 | isles_temple, isles_bridge, isles_above, isles_golden, isles_falls | Meadows adrift over a sea of cloud: a temple island with a waterfall, keels of rock, a plank bridge to an islet of trees, golden hour. |
| `glow_jungle` | good | 4 | glow_pool, glow_head, glow_flowers, glow_path | A clearing at night where every plant glows: a pool of glowing plankton, a stone head lit green, a heliconia burning pink, a path into the jungle. |
| `aurora_palace` | good | 4 | aurora_lake, aurora_gate, aurora_throne, aurora_shore | A palace of ice on a frozen lake under the aurora: the lake doubling it, the gate, the throne in a hall of frost, the shore. |
| `clockwork_city` | good | 4 | clock_plaza, clock_orrery, clock_gears, clock_tower | A plaza of brass and brick at sundown: the orrery (wireframes) before the clock tower, gears in the walls, pipes and steam. |
| `village_green` | good | 4 | village_market, village_stall, village_well, village_night | A cobbled street of timber-framed houses to a green: a market stall and its keeper, the inn sign, a cart, the well; the inn lit after closing. |
| `ghost_town` | good | 4 | western_noon, western_saloon, western_ghost, western_windpump | A frontier main street: a cowboy at high noon, the saloon and its barkeep, sundown with lanterns and a ghost, a windpump in the desert. |
| `misty_moor` | good | 3 | moor_dawn, moor_circle | Stones of varied heights with weathered menhir faces and slanted, chipped stone_cap tops in dawn mist. |
| `winter_lake` | good | 4 | winter_night, winter_day | Ice redrawn (fractures, depth) and snow redrawn (drifts); the snowy spruce and snow-capped boulders. |
| `winter_woods` | good | 4 | winter_lane, winter_deer, winter_lantern, winter_stream | A snowbound wood: the lane, a deer on a frozen stream in falling snow, a child by a lantern-lit footbridge, trees mirrored in the ice. |
| `chapel_graveyard` | good | 4 | chapel_yard, chapel_nave | The yard is a little sparse. |

### Castles, ruins and caves

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `castle_keep` | good | 5 | castle_throne, castle_gate | The throne hall closer: a great stained-glass window, banners and candelabras behind a larger throne, guards at the steps, the knight to one side. |
| `cathedral_ruin` | good | 3 | cathedral_beam, cathedral_pilgrim | The beam through the fallen roof, rafters still spanning the hole with ivy hanging from it, column drums and rubble in the light; shot from the aisle. |
| `crystal_cave` | good | 5 | cave_beast, crystal_cave, crystal_violet, crystal_close | Rebuilt round crystal clusters that refract: a great cavern with a lake of glowing water, the great crystal on its island, clusters round the walls, the walls lined with cave rock and glowing-moss rock, the glowing jungle's plants along the shore; the survey robot and the beast wading before the great crystal. |

### Space, alien and dream

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `space_station` | good | 3 | station_deck, station_corridor |  |
| `derelict_ship` | good | 3 | derelict_corridor, derelict_hive |  |
| `orbital_hangar` | good | 4 | hangar_bay, hangar_control, hangar_reactor, hangar_pilot | A shuttle bay in orbit, its control room and the reactor: the scifi.py hardware, glass panes between mullions onto space and a ringed planet, a window onto the bay, cyan haze and red alarm light. |
| `alien_world` | good | 3 | alien_landing, alien_monolith |  |
| `moon_base` | good | 4 | moon_base, moon_rover, moon_night, moon_earth | Greenhouse domes and habitat modules on the grey plain under the Earth: day, the rover, the lunar night, Earthrise over the domes. |
| `dream_world` | good | 3 | dream_stair, dream_mirror |  |
| `dream_chess` | good | 4 | dream_plain, dream_door, dream_hole, dream_clock | A giant marble chess game on a floating plain of checker_marble under a melting sky clock: arches and stairs in the air, a stair up to a lone door, a hole onto the sky. |
| `drowned_library` | good | 4 | library_hall, library_reader, library_beams, library_water | Bookshelves three storeys high in still water under tall windows and skylights: beams in dark fog, jellyfish, lanterns, flying books, koi and a whale. |
| `hall_of_doors` | good | 4 | doors_hall, doors_stair, doors_sky, doors_up | An endless corridor of doors in every colour, three storeys and the ceiling; a door onto the sky, a stair to a door in the air, the sleepwalker. |

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
| `saloon` | good | 3 | saloon_noon, saloon_cards, saloon_piano | New: the frontier town's saloon - the noon sun through the front windows into dusty air, a card game, and after midnight a ghost at the piano. The day's people are the shots' extra sprites, so the room at night is empty. |
| `gold_mine` | good | 3 | mine_tunnel, mine_vein, mine_portal | New: the frontier mine - a tunnel timbered in 3D with rails and lanterns, a prospector at a vein of gold, the portal in a hillside of canyon rock at dusk. |
| `temple_inside` | good | 3 | temple_passage, temple_idol, temple_reach | New: inside the jungle pyramid - a passage of glyphs, the idol on its altar in a shaft of sun through the broken roof between square pillars, the explorer beside it. |

## Pass log

- **2026-10-19, pass 0.** First full review of every asset, on review sheets and in the gallery. This file and `docs/asset_review.py` were added.
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

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
| Textures | 148 | 145 | 3 | 0 | 0 |
| Props | 212 | 210 | 2 | 0 | 0 |
| Characters | 27 | 25 | 2 | 0 | 0 |
| Decals | 25 | 20 | 5 | 0 | 0 |
| Skies | 11 | 11 | 0 | 0 | 0 |
| Skylines | 6 | 5 | 1 | 0 | 0 |
| Sky objects | 7 | 7 | 0 | 0 | 0 |
| Scatter sets | 18 | 18 | 0 | 0 | 0 |
| Fringe sets | 6 | 6 | 0 | 0 | 0 |
| Facade styles | 6 | 5 | 1 | 0 | 0 |
| Prefabs | 13 | 13 | 0 | 0 | 0 |
| Held items | 6 | 0 | 6 | 0 | 0 |
| Icons | 26 | 26 | 0 | 0 | 0 |
| GUI themes | 5 | 5 | 0 | 0 | 0 |
| GUI widgets | 16 | 16 | 0 | 0 | 0 |
| Post presets | 20 | 20 | 0 | 0 | 0 |
| Palettes | 9 | 9 | 0 | 0 | 0 |
| Example scenes | 47 | 40 | 7 | 0 | 0 |
| **all** | **608** | **581** | **27** | **0** | **0** |
<!-- /summary -->

## Pass plan

Weakest first, and in the order the new scenes need them.

1. **Nature.** The plant and ground textures are the weakest part of the set: foliage, hedge, grass and dirt are coloured noise, and bark has a seam. Rework `foliage`, `foliage_autumn`, `hedge`, `grass`, `dirt`, `bark`, `bark_pine` and the `tree` and `bush` props; polish `moss`, `gravel`, `sand`, `pine_needles` and the `flowers`, `boulder` and `log` props. The pixel-art toolkit (`scripts/pixelart.py`) that drew the jungle, ruins and beach is the way to do it: clusters of shaped leaves lit from above rather than noise.
2. **Stone and ruins.** `rock`, `rock_wet`, `rock_floor`, `snow_rock`, `cobble`, `marble_dark`, `ivy`, `shingle`; the `column`, `statue` and `fountain` props; the standing stones in misty_moor and the roof hole in cathedral_ruin.
3. **Water and ice.** `water` (depth, caustics, a ripple that tiles), `ice`; the `rowboat` and `buoy` props; the shore rocks in coast_lighthouse.
4. **Interiors.** `plaster`, `plaster_white`, `ceiling_plaster`, `acoustic`, `beams`, `wood_panel`, `curtain`, `curtain_black`, `corrugated`; the `barrel`, `broken_barrel`, `crate`, `chest`, `bed`, `bench`, `table` and `wheelchair` props; the castle_keep throne hall.
5. **Small things.** The hands on the held items, the `stain`, `stain_rust` and `moss_patch` decals, the `child` and `dreamer` characters, the `city` skyline, `alien_rock`, `alien_ground`, and the `glowshroom` and `alien_egg` props.
6. **Second look.** Every asset marked good, checked again on the review sheets and in its scenes, with fresh eyes and the new techniques in hand.

## Textures (148)

64x64 tiles, drawn in code. "glows" means the texture lights itself (windows, screens, runes), "see-through" that the map shows through its holes, "mirror" that floors made of it reflect.

### Masonry and plaster

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `brick` | good |  | rainy_street |  |
| `brick_dark` | good |  | neon_street, rain_alley |  |
| `brick_yellow` | good |  | - |  |
| `stone` | good |  | claude_study, garden_encounter, gui_menus, hospital_garden, post_presets | Even block sizes; a few varied heights would help on long walls. |
| `stone_dark` | good |  | cathedral_ruin, garden_encounter, gui_menus, gui_themes, gui_trade, haunted_house, hospital_garden, library_medium, mansion_library, misty_moor, post_presets, rainy_street |  |
| `stone_pale` | good |  | cathedral_ruin, chapel_graveyard, coast_lighthouse, dream_world, garden_encounter, gui_menus, hospital_garden, post_presets |  |
| `castle` | good |  | castle_keep | Mortar grid is very regular; chip a few corners. |
| `moss_stone` | good |  | autumn_lane, coast_lighthouse, misty_moor |  |
| `slime_brick` | good |  | sewer_tunnels |  |
| `plaster` | good |  | rainy_street, village_green | Redrawn with the toolkit in basics.py: smooth render mottled where patched, a hairline crack, faint streaks; no band, so it stacks storey on storey. |
| `plaster_white` | good |  | garden_encounter, gui_menus, hospital_garden, post_presets | Redrawn with the toolkit in basics.py: the same render in white. |
| `hospital_wall` | good |  | ghost_corridor, gui_hud, hospital_corridor |  |
| `ivy` | good |  | rainy_street | Redrawn with the toolkit in basics.py: red brick with woody stems climbing and branching and clusters of dark leaves, the newest brighter. |
| `concrete` | good |  | bunker_lab, garden_encounter, gui_lantern, gui_menus, hospital_garden, post_presets, sewer_tunnels, tunnel_encounter, underground_waterway |  |
| `marble` | good |  | cathedral_ruin, chapel_graveyard, dream_chess, dream_world, gui_themes, gui_trade, library_medium, mansion_library |  |
| `marble_dark` | good |  | - | Redrawn with the toolkit in basics.py: dark slabs with long, thin, continuous veins of white and grey drifting across them. |
| `rock` | good |  | castle_keep, coast_lighthouse, crystal_cave, garden_encounter, gui_lantern, gui_menus, hospital_garden, kelp_forest, moon_base, post_presets, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: masses of every size, each a facet tilted to the light, split by crevices that wander, widen and close; finer cracks, grain. |
| `rock_wet` | good |  | crystal_cave, gui_lantern, kelp_forest, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: the same rock darker and blue-grey, with glints of water where the faces catch the light. |
| `snow_rock` | good |  | winter_lake | Redrawn with the toolkit in basics.py: faceted rock with snow lying on the top of every mass, thick on the flats, and drifted in the crevices. |
| `sky_wall` | good |  | dream_chess, dream_world |  |

### Wood

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `wood_panel` | good |  | drowned_library, haunted_house | Redrawn with the toolkit in basics.py: stiles and rails framing two raised panels per unit, all one dark wood, the bevels catching the light, figure streaked along the grain. |
| `planks` | good |  | bayou, ghost_town, kelp_forest, winter_woods |  |
| `boards` | good |  | bayou, coast_lighthouse, ghost_town, kelp_forest, rain_alley, tropical_beach |  |
| `logs` | good |  | coast_lighthouse, winter_lake |  |
| `door_wood` | good |  | bayou, dream_chess, dream_world, haunted_house, winter_lake |  |
| `bookshelf` | good |  | claude_study, drowned_library, gui_themes, gui_trade, library_medium, mansion_library |  |
| `bark` | good |  | - | Redrawn with the toolkit in forest.py: long wavy ridges split by deep dark furrows; tiles without a seam. |
| `bark_pine` | good |  | - | Redrawn with the toolkit in forest.py: a mosaic of tall plates (nearest-seed cells) with dark fissures and flaking. |
| `wood_floor` | good |  | claude_study, drowned_library, gui_lantern, gui_themes, gui_trade, haunted_house, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `shingle` | good |  | bayou, chapel_graveyard, coast_lighthouse, rainy_street, winter_lake | Redrawn with the toolkit in basics.py: courses of staggered slates, each tipped up to its foot so it throws a shadow on the course below, chipped corners, moss in the joints. |

### Metal and sci-fi

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `iron_door` | good |  | bunker_lab, garden_encounter, ghost_corridor, gui_hud, gui_lantern, gui_menus, hospital_corridor, hospital_garden, post_presets, rainy_street, tunnel_encounter, underground_waterway |  |
| `corrugated` | good |  | rainy_street | Redrawn with the toolkit in basics.py: galvanised sheets in rounded ribs lapped at the seam, nail rows, rust in patches and streaks from the nails. |
| `rust` | good |  | bunker_lab, rainy_street |  |
| `pipes` | good |  | bunker_lab, sewer_tunnels |  |
| `panel` | good |  | bunker_lab, derelict_ship, orbital_hangar, space_station |  |
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
| `hangar_floor` | good |  | orbital_hangar | Drawn with the toolkit in scifi.py: heavy plates four to a unit, corner bolts, tread, a tie-down ring at each crossing, wear and oil. |
| `conduit` | good | glows | orbital_hangar | Drawn with the toolkit in scifi.py: cable bundles in four colours and pipes up the wall, steel clamps, a junction box with lit LEDs. |
| `screen_wall` | good | glows | orbital_hangar | Drawn with the toolkit in scifi.py: monitors four to a unit, each with a trace, readouts, a radar or a wireframe, in cyan, green or amber; glows. |

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
| `snow` | good |  | winter_lake, winter_woods | Redrawn with the toolkit in basics.py: drifts sculpted by the wind, their lee sides in blue shadow, faint ripples, glitter. |
| `ice` | good | mirror 0.38 | winter_lake, winter_woods | Redrawn with the toolkit in basics.py: clear blue with gentle depth, straight fractures with a branch each and a dark side, strings of bubbles, frost. |
| `water` | good | mirror 0.5 | alien_world, coast_lighthouse, crystal_cave, drowned_library, gui_lantern, sewer_tunnels, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: a deep teal in slow swells and a broken net of light where the ripples gather it; kept dark, so reflections read. |
| `swamp_water` | good | mirror 0.42 | bayou | Drawn with the toolkit in swamp.py: black-brown water with a skin of duckweed drifting in patches and a few floating leaves; mirror 0.42. |
| `seabed` | good |  | kelp_forest | Drawn with the toolkit in sea.py: pale sand in gentle ripples, shell and pebble, and a broken net of caustic light over it. |
| `water_surface` | good | glows | - | Drawn with the toolkit in sea.py: the surface from below, rippled and glowing with a net of brighter lines; for an underwater roof. |
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
| `checker_marble` | good | mirror 0.35 | dream_chess | Drawn with the toolkit in dream.py: black and white marble squares, veined, fine joints; mirror 0.35. |
| `linoleum` | good |  | ghost_corridor, gui_hud, hospital_corridor |  |
| `tile_floor` | good |  | bunker_lab, derelict_ship, neon_street |  |
| `tile_white` | good |  | - |  |
| `tile_green` | good |  | - |  |
| `cobble` | good |  | garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, village_green | Redrawn with the toolkit in basics.py: a Voronoi mosaic of 36 rounded stones a tile in grey and brown, dark grit and moss in the joints; the repeat no longer shows. |
| `asphalt` | good |  | neon_street, rain_alley, rainy_street |  |
| `carpet` | good |  | castle_keep, chapel_graveyard, claude_study, gui_themes, gui_trade, haunted_house, library_medium, mansion_library |  |
| `carpet_green` | good |  | - |  |
| `flagstone` | good |  | castle_keep, cathedral_ruin, chapel_graveyard, claude_study, haunted_house, neon_street, rain_alley |  |
| `obsidian` | good | mirror 0.45 | dream_world, space_station |  |
| `concrete_floor` | good |  | 47 scenes |  |
| `rock_floor` | good |  | crystal_cave, gui_lantern, kelp_forest, tunnel_encounter, underground_waterway | Redrawn with the toolkit in basics.py: flatter, smaller masses in brown with grit in the cracks. |

### Ceilings

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `acoustic` | good |  | ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: four bevelled tiles a unit in a grid of runners, pitted with fissures and pin-holes, a water stain. |
| `ceiling_plaster` | good |  | gui_themes, gui_trade, library_medium | Redrawn with the toolkit in basics.py: the plaster render in a darker tone, with no band across it. |
| `beams` | good |  | castle_keep, cathedral_ruin, chapel_graveyard, claude_study, haunted_house, mansion_library | Redrawn with the toolkit in basics.py: two oak beams a unit, proud of the limewash: a lit edge, a side in shadow and a soft shadow on the plaster; grain and checks. |

### Fabric and interior

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `curtain` | good |  | gui_themes, gui_trade, library_medium, mansion_library | Redrawn with the toolkit in basics.py: velvet folds of every width, each a rounded column lit on its left, deep shadow between. |
| `curtain_black` | good |  | - | Redrawn with the toolkit in basics.py: the same folds in black velvet. |
| `wallpaper` | good |  | gui_themes, gui_trade, haunted_house, library_medium, mansion_library |  |
| `wallpaper_green` | good |  | - |  |

### Light sources

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `window_lit` | good | glows | coast_lighthouse, garden_encounter, gui_menus, haunted_house, hospital_garden, post_presets, rainy_street | Simple; a silhouette in one pane now and then would add life. |
| `window_dark` | good |  | garden_encounter, gui_menus, gui_themes, gui_trade, haunted_house, hospital_garden, library_medium, mansion_library, post_presets, rainy_street |  |
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

### Jungle

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `jungle_leaves` | good |  | jungle_temple, tropical_beach | Drawn with the pixel-art toolkit. |
| `canopy` | polish | glows | jungle_temple | From below it can still read a little like camouflage; more depth between the layers. |
| `canopy_top` | good |  | jungle_temple, tropical_beach | Use as the top of jungle walls. |
| `jungle_floor` | good |  | jungle_temple |  |
| `jungle_bark` | good |  | jungle_temple |  |
| `temple_stone` | good |  | jungle_temple |  |
| `temple_cornice` | good |  | jungle_temple | The last storey of each tier of a stepped pyramid. |
| `glyphs` | good |  | jungle_temple | Five kinds of cartouche; faces and animals would add variety. |
| `temple_roots` | good |  | jungle_temple |  |
| `temple_door` | good | glows | jungle_temple |  |
| `roof_comb` | good | see-through | jungle_temple |  |

### Ruins

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `limestone` | good |  | ancient_ruins, tropical_beach |  |
| `sandstone` | good |  | ghost_town, red_canyon | Drawn with the toolkit in desert.py: beds of red, orange and cream, the hard ones standing out as ledges, cross-bedding, joints, varnish streaking down from the ledges. |
| `sandstone_pale` | good |  | ghost_town, red_canyon | Drawn with the toolkit in desert.py: the cream cap rock near a canyon rim, for bands among the sandstone. |
| `slot_rock` | good |  | red_canyon | Drawn with the toolkit in desert.py: beds swept into flowing curves of orange, red, cream and violet, polished smooth. |
| `pueblo_stone` | good |  | red_canyon | Drawn with the toolkit in desert.py: thin sandstone slabs laid in courses in a thick mud mortar, chinked with small stones. |
| `pueblo_door` | good |  | red_canyon | Drawn with the toolkit in desert.py: the coursed stone with a T-shaped doorway, dark inside, poles laid over its head. |
| `ruin_paving` | good |  | ancient_ruins, jungle_temple |  |
| `dry_grass` | good |  | ancient_ruins, autumn_lane | Fewer, larger clumps with more earth between them, so it is not busy at grazing angles. |
| `desert_wash` | good |  | ghost_town, red_canyon | Drawn with the toolkit in desert.py: pale sand faintly rippled, washed-down pebbles, patches of crazed dried mud. |
| `colonnade` | good | see-through | ancient_ruins | Flat when seen along its length: use column props for a row you look down. |
| `colonnade_top` | good | see-through | ancient_ruins |  |
| `colonnade_broken` | good | see-through | ancient_ruins |  |

### Beach

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `beach_sand` | good |  | tropical_beach |  |
| `wet_sand` | good | mirror 0.28 | tropical_beach |  |
| `shallows` | good | mirror 0.3 | jungle_temple, tropical_beach |  |
| `sea` | good | mirror 0.45 | ancient_ruins, tropical_beach |  |
| `bamboo` | polish |  | tropical_beach | The nodes still line up into a grid across the poles. |
| `thatch` | polish |  | tropical_beach | The rows could be clearer, each with a shadow under its fringe. |

## Props (212)

Camera-facing sprites. "tall" is the default height in world units (a wall is 1); "no shadow" props hang, float or burn, so they get no contact shadow.

### Furniture and interior

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `armchair` | good | 0.6 tall | claude_study, haunted_house |  |
| `bed` | good | 0.4 tall | bunker_lab, ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: an iron bedstead with uprights, a mattress in white sheets, a pillow, a grey blanket turned back, castors. |
| `bench` | good | 0.35 tall | coast_lighthouse, garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, village_green | Redrawn with the toolkit in basics.py: three backrest slats and two in the seat, held in cast-iron ends with scrolled armrests and curving legs. |
| `book_stack` | good | 0.22 tall | claude_study, drowned_library |  |
| `chest` | good | 0.3 tall | castle_keep, kelp_forest | Redrawn with the toolkit in basics.py: oak planks under a rounded lid, iron straps studded with rivets, iron corners, a brass lock plate. |
| `console` | good | 0.85 tall, glows | bunker_lab, orbital_hangar, space_station |  |
| `crate` | good | 0.4 tall | bunker_lab, coast_lighthouse, ghost_town, gui_lantern, gui_themes, gui_trade, hospital_corridor, library_medium, mansion_library, neon_street, rain_alley, rainy_street, sewer_tunnels, tunnel_encounter, underground_waterway, village_green, winter_lake, woodland_night | Redrawn with the toolkit in basics.py: planks behind battens and a diagonal brace, nails at the corners, a stencilled arrow. |
| `barrel` | good | 0.45 tall | bayou, bunker_lab, coast_lighthouse, ghost_town, gui_lantern, gui_themes, gui_trade, library_medium, mansion_library, neon_street, rain_alley, rainy_street, sewer_tunnels, tunnel_encounter, underground_waterway, village_green | Redrawn with the toolkit in basics.py: bulging staves turned on a lathe, three iron hoops, the lid showing at the top. |
| `locker` | good | 1 tall | bunker_lab |  |
| `lectern` | good | 0.5 tall | chapel_graveyard |  |
| `open_book` | good | 0.12 tall, glows, no shadow | claude_study, drowned_library |  |
| `pew` | good | 0.42 tall | cathedral_ruin, chapel_graveyard |  |
| `table` | good | 0.36 tall | castle_keep | Redrawn with the toolkit in basics.py: a thick top with grain along it, an apron, turned legs, the far pair darker. |
| `throne` | good | 0.95 tall | castle_keep |  |
| `wheelchair` | good | 0.45 tall | ghost_corridor, gui_hud, hospital_corridor | Redrawn with the toolkit in basics.py: side on: a big spoked wheel with its push rim, a caster, leather seat and back, armrest, handles, footrest. |
| `writing_desk` | good | 0.55 tall, glows | claude_study, drowned_library |  |
| `globe` | good | 0.45 tall | claude_study, drowned_library |  |
| `orrery` | good | 0.6 tall, glows | claude_study |  |
| `telescope` | good | 0.8 tall | claude_study |  |
| `painting` | good | 0.45 tall, no shadow | - |  |
| `wall_clock` | good | 0.28 tall, no shadow | bunker_lab, rainy_street |  |
| `banner` | good | 0.95 tall, no shadow | castle_keep, rainy_street |  |
| `chains` | good | 0.6 tall, no shadow | castle_keep |  |
| `ladder` | good | 1 tall, no shadow | drowned_library, red_canyon, sewer_tunnels |  |
| `pipe_valve` | good | 0.32 tall, no shadow | bunker_lab, sewer_tunnels |  |
| `sack` | good | 0.42 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, neon_street, rain_alley, rainy_street, sewer_tunnels, woodland_night |  |
| `bucket` | good | 0.32 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, neon_street, rain_alley, rainy_street, sewer_tunnels |  |

### Light and fire

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `brazier` | good | 0.85 tall, glows, no shadow | ancient_ruins, castle_keep, coast_lighthouse |  |
| `campfire` | good | 0.4 tall, glows, no shadow | tropical_beach, woodland_night |  |
| `candles` | good | 0.2 tall, glows, no shadow | castle_keep, cathedral_ruin, chapel_graveyard, drowned_library, gui_lantern, gui_themes, gui_trade, jungle_temple, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `ceiling_lamp` | good | 0.3 tall, glows, no shadow | bunker_lab, sewer_tunnels |  |
| `chandelier` | good | 0.45 tall, glows, no shadow | castle_keep, claude_study, haunted_house |  |
| `cobweb` | good | 0.9 tall, no shadow | haunted_house | Drawn with the toolkit in haunted.py: threads radiating from a corner with sagging spiral rings, a broken strand; translucent. |
| `candelabra` | good | 1.2 tall, glows, aura | haunted_house | Drawn with the toolkit in haunted.py: a turned brass stem on a tripod foot, five curved arms with candles burning, wax run down them; aura. |
| `portrait` | good | 0.75 tall, glows, no shadow | haunted_house | Drawn with the toolkit in haunted.py: an oval beaded gilt frame round a pale, unsmiling face, black coat and white collar; the eyes glow faintly. |
| `grandfather_clock` | good | 1.6 tall | haunted_house | Drawn with the toolkit in haunted.py: a mahogany case: hood with a broken pediment and finial, a dial near midnight, a glass door on the pendulum. |
| `balustrade` | good | 0.5 tall | haunted_house | Drawn with the toolkit in haunted.py: turned balusters every eighth of a unit between handrail and base rail, newel posts; three units a card. |
| `lamp_post` | good | 1.6 tall, glows | garden_encounter, gui_menus, hospital_garden, post_presets, rain_alley, rainy_street | Thin at a distance. |
| `lantern` | good | 0.3 tall, glows, no shadow | bayou, chapel_graveyard, coast_lighthouse, garden_encounter, ghost_town, gui_lantern, gui_menus, gui_themes, gui_trade, library_medium, mansion_library, post_presets, tunnel_encounter, underground_waterway, village_green, winter_lake, winter_woods, woodland_night |  |
| `sconce` | good | 0.32 tall, glows, no shadow | castle_keep, claude_study, rainy_street |  |

### Nature

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `boulder` | good | 0.55 tall | chapel_graveyard, coast_lighthouse, kelp_forest, misty_moor, woodland_night | Redrawn with the toolkit in forest.py: a settled rock with a lesser lobe and cracks, moss over its top, lichen spots. |
| `bush` | good | 0.5 tall | chapel_graveyard, coast_lighthouse, woodland_night | Redrawn with the toolkit in forest.py: leaf clusters on fanned twigs, lit on top, dark underneath. |
| `bush_autumn` | good | 0.5 tall | autumn_lane | Drawn with the toolkit in forest.py: the bush in rust red and orange. |
| `bush_snow` | good | 0.45 tall | winter_woods | Drawn with the toolkit in forest.py: a lumpy cushion of snow, blue in its hollows, twigs poking up through it. |
| `birch` | good | 3 tall | village_green, woodland_night | White trunk and a second stem banded with black, an airy crown of small leaves in drooping clumps. |
| `birch_autumn` | good | 3 tall | autumn_lane | Drawn with the toolkit in forest.py: the birch gone to gold, a few patches already orange. |
| `birch_winter` | good | 3 tall | winter_woods | Drawn with the toolkit in forest.py: the white birch bare: branches reaching out with fine twigs weeping from them, snow on a few. |
| `dead_tree` | good | 2.9 tall | chapel_graveyard, haunted_house, misty_moor, woodland_night | Redrawn with the toolkit in forest.py: a split trunk on a gnarled foot, bare limbs forking into twigs, grey peeling bark. |
| `fern` | good | 0.42 tall | autumn_lane, chapel_graveyard, jungle_temple, misty_moor, tropical_beach, woodland_night | Redrawn: arching fronds from one crown. |
| `flowers` | good | 0.35 tall | garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, village_green | Redrawn with the toolkit in basics.py: leaves and stems with blooms of four colours, five petals round a dark eye, at different heights. |
| `grass_tuft` | good | 0.4 tall | autumn_lane, chapel_graveyard, coast_lighthouse, misty_moor, rainy_street, tropical_beach, village_green, woodland_night | Redrawn: thin arching blades. |
| `ivy_hang` | good | 0.8 tall, no shadow | cathedral_ruin, rainy_street |  |
| `log` | good | 0.28 tall | tropical_beach, winter_lake, winter_woods, woodland_night | Redrawn with the toolkit in forest.py: bark in long ridges, a branch stub, moss along the top, a pale ringed end. |
| `mushrooms` | good | 0.12 tall | autumn_lane, chapel_graveyard, jungle_temple, woodland_night |  |
| `palm` | good | 3.2 tall | garden_encounter, gui_menus, hospital_garden, post_presets, tropical_beach | Redrawn with the pixel-art toolkit: a ringed trunk, arching ragged fronds, coconuts. |
| `pine` | good | 3.4 tall | autumn_lane, coast_lighthouse, woodland_night | Redrawn with the toolkit in forest.py: a spruce, tier on tier of drooping boughs with ragged hems over a straight trunk. |
| `reeds` | good | 0.8 tall | coast_lighthouse, winter_woods |  |
| `bald_cypress` | good | 4.2 tall | bayou | Drawn with the toolkit in swamp.py: a fluted, buttressed foot, limbs under flat sprays of feathery leaves, moss hanging from every limb, knees round it. |
| `spanish_moss` | good | 1.4 tall, no shadow | bayou | Drawn with the toolkit in swamp.py: a curtain of grey-green strands from a stub of branch, to hang with `z`. |
| `cypress_knees` | good | 0.3 tall | bayou | Drawn with the toolkit in swamp.py: knobbly cones of root standing out of the water. |
| `cattails` | good | 1 tall | bayou | Drawn with the toolkit in swamp.py: long blades and stems with brown velvet heads. |
| `kelp` | good | 5 tall | kelp_forest | Drawn with the toolkit in sea.py: a swaying stipe from its holdfast, long golden blades streaming off small floats, a tangle at the top. |
| `rocks` | good | 0.22 tall | alien_world, ancient_ruins, bunker_lab, cathedral_ruin, chapel_graveyard, coast_lighthouse, crystal_cave, derelict_ship, ghost_town, kelp_forest, misty_moor, moon_base, rainy_street, red_canyon, sewer_tunnels, tropical_beach, winter_lake, winter_woods, woodland_night | Redrawn: half-sunk stones with lit tops and the odd crack. |
| `snowy_pine` | good | 3.4 tall | winter_lake, winter_woods | Drawn with the toolkit in forest.py: the new spruce with snow lying in clumps along every tier's shoulders, crumbs on the hems and a small cap on the leader; dark needles between, so it still reads at a distance. |
| `boulder_snow` | good | 0.55 tall | winter_lake, winter_woods | Drawn with the toolkit in forest.py: the boulder under a cushion of snow, deep where the top is flat and thin down the steep sides; in the `snow` scatter set. |
| `stump` | good | 0.3 tall | tropical_beach, woodland_night | Redrawn with the toolkit in forest.py: a pale ringed cut face, furrowed sides, roots, a cushion of moss. |
| `tree` | good | 2.6 tall | dream_world, garden_encounter, gui_menus, hospital_garden, post_presets, village_green, woodland_night | Redrawn with the toolkit in forest.py: an oak with a furrowed trunk on a flared foot, limbs showing between lobes of crown lit from above. |
| `tree_autumn` | good | 2.6 tall | autumn_lane | Drawn with the toolkit in forest.py: the oak turned: orange and gold in patches cluster by cluster, a side going first, a little rust. |
| `tree_winter` | good | 2.6 tall | winter_woods | Drawn with the toolkit in forest.py: a bare oak grown by recursive branching down to twigs, snow along every limb level enough to hold it. |
| `glowshroom` | good | 0.16 tall, glows, no shadow | alien_world, crystal_cave | Redrawn with the toolkit in basics.py: domed caps freckled with paler spots over dark gills, pale stems; the caps glow. |
| `crystal` | good | 0.36 tall, glows, no shadow | alien_world, crystal_cave |  |
| `stalagmite` | good | 0.8 tall | crystal_cave |  |

### Debris

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `bones` | good | 0.22 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, crystal_cave, derelict_ship, neon_street, rain_alley, sewer_tunnels, woodland_night |  |
| `broken_barrel` | good | 0.46 tall | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, neon_street, rain_alley, rainy_street, sewer_tunnels, woodland_night | Redrawn with the toolkit in basics.py: the hooped bottom half, its front staves splintered off at different heights over the dark inside, the back staves taller, loose staves and a fallen hoop. |
| `rubble` | good | 0.34 tall | ancient_ruins, bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, rainy_street, sewer_tunnels, woodland_night |  |

### Monuments and outdoors

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `column` | good | 1 tall | ancient_ruins, cathedral_ruin | Redrawn: a fluted Doric column with capital and plinth. |
| `fountain` | good | 0.9 tall | - | Redrawn with the toolkit in basics.py: a moulded basin with water in it, a fluted pedestal and bowl, water spilling in arcs. |
| `gravestone` | good | 0.6 tall | chapel_graveyard, haunted_house |  |
| `grave_cross` | good | 0.55 tall | chapel_graveyard, haunted_house |  |
| `signpost` | good | 1.3 tall | coast_lighthouse |  |
| `statue` | good | 1.5 tall | garden_encounter, gui_menus, hospital_garden, mansion_library, post_presets | Redrawn with the toolkit in basics.py: a draped woman in weathered marble raising a wreath, folds catching the light, on a moulded plinth with lichen. |
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
| `market_stall` | good | 1.9 tall | village_green | Drawn with the toolkit in village.py: a red and white striped awning with a scalloped valance over a trestle of apples, cabbages and bread, crates beneath. |
| `inn_sign` | good | 0.75 tall | village_green | Drawn with the toolkit in village.py: an iron bracket and scroll with a red board hanging from it, a gilt border and crown; stand it out from a front as a card. |
| `armor` | good | 0.66 tall | castle_keep, haunted_house |  |

### Sci-fi

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `antenna` | good | 2.4 tall, glows | alien_world, moon_base |  |
| `drone` | good | 0.22 tall, glows, no shadow | orbital_hangar, space_station |  |
| `hologram` | good | 0.55 tall, glows, aura, no shadow | orbital_hangar, space_station |  |
| `lander` | good | 1.6 tall, glows | alien_world, moon_base |  |
| `dome` | good | 2.6 tall, glows, aura | moon_base | Drawn with the toolkit in moon.py: a geodesic frame of white struts over glass, rows of plants under pink grow lights, an airlock; glows. |
| `hab_module` | good | 1.3 tall, glows | moon_base | Drawn with the toolkit in moon.py: a ribbed white cylinder on legs, lit portholes, an end hatch, a radiator fin. |
| `solar_array` | good | 1.4 tall | moon_base | Drawn with the toolkit in moon.py: dark-blue cells in a silver frame tilted on a mast, a cable down. |
| `rover` | good | 0.8 tall | moon_base | Drawn with the toolkit in moon.py: a white chassis on six wire-mesh wheels, two seats, a dish on a mast, a foil-wrapped box. |
| `sci_crate` | good | 0.35 tall, glows | derelict_ship, moon_base, neon_street, orbital_hangar, space_station |  |
| `stasis_pod` | good | 1 tall, glows | derelict_ship |  |
| `shuttle` | good | 2.2 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: nose-on wedge hull in white and orange, lit cockpit and engine pods, landing legs, panel lines and vents. |
| `cargo_container` | good | 1.2 tall | orbital_hangar | Drawn with the toolkit in scifi.py: corrugated orange steel, corner castings, door rods, rust streaking down the ribs. Tint for other colours. |
| `power_loader` | good | 2 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: roll cage, hydraulic arms with forks, hazard stripes on the hip block, a lit work light. |
| `beacon` | good | 0.3 tall, glows, aura | orbital_hangar | Drawn with the toolkit in scifi.py: an amber dome in a wire cage on a squat base; glows, with an aura. |
| `reactor_core` | good | 2.8 tall, glows, aura | orbital_hangar | Drawn with the toolkit in scifi.py: a glowing column in steel collars with coolant pipes; glows, with an aura. |
| `robot_arm` | good | 1.8 tall, glows | orbital_hangar | Drawn with the toolkit in scifi.py: three orange segments, dark joints, a turntable base, a welding spark. |
| `cables_hang` | good | 1.4 tall, no shadow | orbital_hangar | Drawn with the toolkit in scifi.py: slack loops of cable and a few dangling ends; hangs from a ceiling, no contact shadow. |
| `vending_machine` | good | 1.1 tall, glows, aura | neon_street | Drawn with the toolkit in scifi.py: a red steel box, its front a lit window of cans in rows, a glowing strip, coin slot and hatch. |
| `noodle_stall` | good | 1.6 tall, glows | neon_street | Drawn with the toolkit in scifi.py: a counter under a striped awning, red paper lanterns lit, a neon sign of pseudo-letters, pots. |
| `steam` | good | 1.2 tall, no shadow | neon_street | A dithered plume, soft and spreading as it rises; see-through by default. |
| `holo_ad` | good | 1.6 tall, glows, no shadow | neon_street | A hologram koi in cyan and pink with scanlines, dorsal and pectoral fins; additive by default. |
| `wires_span` | good | 0.75 tall, glows, no shadow | neon_street | Drawn with the toolkit in scifi.py: four sagging wires with paper lanterns, a card to sling across a street. |

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
| `melting_clock` | good | 0.6 tall, no shadow | dream_chess | Drawn with the toolkit in dream.py: a clock face warped over a ledge, the hanging part stretched and dripping. |
| `hourglass` | good | 0.6 tall | dream_chess | Drawn with the toolkit in dream.py: glass bulbs in a wooden frame, sand running into a heap, a gleam. |
| `stone_arch` | good | 2.4 tall | dream_chess | Drawn with the toolkit in dream.py: coursed piers and a round arch of voussoirs with a keystone, open in the middle. |
| `stair_float` | good | 2 tall | dream_chess | Drawn with the toolkit in dream.py: a flight of stairs on a soffit, broken off at both ends, stones falling. |
| `paper_boat` | good | 0.3 tall | dream_chess | Drawn with the toolkit in dream.py: folded planes, a peak and a crease. |
| `jellyfish` | good | 0.9 tall, glows, no shadow | drowned_library, kelp_forest | A bell of light frilled at the rim, oral arms and tentacles; additive and glowing, no shadow. |
| `sky_lantern` | good | 0.34 tall, glows, aura, no shadow | drowned_library | Drawn with the toolkit in dream.py: a tapering paper shade lit from inside, the flame at its foot, a wire ring; aura. |
| `book_fly` | good | 0.3 tall, no shadow | drowned_library | Drawn with the toolkit in dream.py: an open book with its covers raised as wings and its pages fanned. |
| `chess_pawn` | good | 0.9 tall | dream_chess, dream_world | Drawn with the toolkit in dream.py: a turned marble pawn (lathe profile), faint veins. Tint dark for the other side. |
| `door_frame` | good | 1.1 tall | dream_chess, dream_world |  |
| `floating_rock` | good | 1.6 tall, no shadow | dream_world |  |
| `koi` | good | 0.35 tall, no shadow | dream_chess, dream_world, drowned_library |  |
| `orb` | good | 0.2 tall, glows, aura, no shadow | dream_world |  |
| `pocket_watch` | good | 0.8 tall, no shadow | dream_world |  |
| `sky_whale` | good | 2 tall, glows, no shadow | dream_world, drowned_library |  |

### Jungle

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `banana_plant` | good | 1.7 tall | jungle_temple |  |
| `monstera` | good | 0.75 tall | jungle_temple |  |
| `tree_fern` | good | 2.4 tall | jungle_temple |  |
| `heliconia` | good | 1.1 tall | jungle_temple |  |
| `bromeliad` | good | 0.22 tall | jungle_temple |  |
| `liana` | good | 2.4 tall, no shadow | jungle_temple |  |
| `kapok` | good | 7.5 tall | jungle_temple | An emergent tree: its crown clears a 4-unit canopy. |
| `canopy_crown` | good | 1.2 tall, no shadow | jungle_temple | Set on jungle wall tops so the canopy edge is crowns, not a hedge. |
| `stone_head` | good | 1.5 tall | jungle_temple |  |
| `stela` | good | 2.1 tall | jungle_temple |  |

### Ruins

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `broken_column` | good | 1 tall | ancient_ruins |  |
| `column_drum` | polish | 0.42 tall | ancient_ruins | The fluted end face could stand out more from the body. |
| `marble_head` | good | 1.1 tall | ancient_ruins |  |
| `amphora` | good | 0.36 tall | ancient_ruins |  |
| `cow_skull` | good | 0.2 tall | ghost_town, red_canyon | Drawn with the toolkit in desert.py: a bleached longhorn skull: dark sockets and nose, horns curving out and up. |
| `clay_pot` | good | 0.34 tall | red_canyon | Drawn with the toolkit in desert.py: a round white pot painted in black bands and a zigzag, turned on a lathe. |
| `windpump` | good | 4.2 tall | ghost_town | Drawn with the toolkit in desert.py: a lattice tower of four splayed legs, cross-braced, a wheel of galvanised blades with its tail vane. |
| `water_trough` | good | 0.4 tall | ghost_town | Drawn with the toolkit in desert.py: grey boards on short legs, water near the brim. |
| `wagon_wheel` | good | 0.55 tall | ghost_town | Drawn with the toolkit in desert.py: an iron-shod rim, twelve spokes, a heavy hub. |
| `cypress` | good | 4 tall | ancient_ruins |  |
| `saguaro` | good | 3.2 tall | ghost_town, red_canyon | Drawn with the toolkit in desert.py: a ribbed column with two arms bending up, spines along the ribs, white blossoms on the crown. |
| `prickly_pear` | good | 0.6 tall | ghost_town, red_canyon | Drawn with the toolkit in desert.py: oval pads growing out of one another, spines, magenta fruit along the top. |
| `tumbleweed` | good | 0.45 tall | ghost_town, red_canyon | Drawn with the toolkit in desert.py: a loose ball of wiry dry stems, the light coming through. |
| `olive_tree` | good | 2.2 tall | ancient_ruins |  |
| `poppies` | good | 0.24 tall | ancient_ruins |  |
| `dry_tuft` | good | 0.36 tall | ancient_ruins, ghost_town, red_canyon, tropical_beach |  |

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
| `jaguar` | good | 0.34 tall, glows | jungle_temple | Redrawn with the toolkit in basics.py: prowling, side on: a long low body, heavy shoulders, a broad head, rosettes spread over a golden coat, a pale belly; the eyes glow. |
| `macaw` | good | 0.3 tall | jungle_temple |  |
| `goat` | polish | 0.34 tall | ancient_ruins | Legs long and stiff. |
| `crab` | good | 0.08 tall | kelp_forest, tropical_beach |  |
| `seagull` | good | 0.14 tall, no shadow | tropical_beach |  |
| `heron` | good | 0.95 tall | bayou | Drawn with the toolkit in swamp.py: a grey heron: long legs, the neck in an S, a yellow dagger of a beak, the black crest. |
| `deer` | good | 0.62 tall | winter_woods | Drawn with the toolkit in forest.py: a deer side on: russet coat, pale belly and throat, slim legs, big ears, an antlered head up, a white tail. |
| `alligator` | good | 0.2 tall, glows, no shadow | bayou | Drawn with the toolkit in swamp.py: only the snout, the eyes (which catch the light) and the ridged back above the water. |
| `fireflies` | good | 1.2 tall, glows, no shadow | bayou | Drawn with the toolkit in swamp.py: a loose swarm of tiny glowing lights with soft halos; additive. |
| `fish_school` | good | 0.9 tall, no shadow | kelp_forest | Drawn with the toolkit in sea.py: thirty-odd silvery fish headed one way, dark backs, thicker in the middle of the shoal. |
| `bubbles` | good | 1.2 tall, no shadow | kelp_forest | Drawn with the toolkit in sea.py: a column of bubbles swelling as they rise, bright rings with a glint; additive. |
| `crow` | good | 0.2 tall | autumn_lane, haunted_house, red_canyon, village_green | Drawn with the toolkit in village.py: glossy black with a blue sheen, the head up, a heavy beak. |
| `bats` | good | 0.6 tall, no shadow | haunted_house | Drawn with the toolkit in haunted.py: black bat silhouettes, wings spread or beating, at different sizes. |

### Cards and parts

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `jungle_card_1` | good | 1.4 tall | jungle_temple | The front of a jungle fringe: bushes alone. |
| `jungle_card_2` | good | 3.4 tall | jungle_temple | A few trees with bushes in front. |
| `jungle_card_3` | good | 4 tall | jungle_temple | More trees, tall ones with crowns. |
| `jungle_card_4` | good | 4.6 tall | jungle_temple | The back: a dense wall of trunks, crowns, palms and bushes. Repeats every 8 units. |
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
| `swamp_card_2` | good | 3.4 tall | bayou | Young cypresses and moss with cattails in front. |
| `swamp_card_3` | good | 4.6 tall | bayou | The back: a dense stand of bald cypresses hung with moss. |
| `kelp_card_1` | good | 5 tall | kelp_forest | The front of a kelp fringe: a few stalks. |
| `kelp_card_2` | good | 5.8 tall | kelp_forest | The back: a dense stand of kelp. |
| `palm_trunk` | good | 3.2 tall | tropical_beach | The palm without its crown, for palm_3d. |
| `palm_crown` | good | 3.2 tall, no shadow | tropical_beach | The palm's crown alone, in the same frame as the trunk. |
| `glass_pane` | good | 1 tall | orbital_hangar | A plain pane for the glass pass. |

## Characters (27)

Pixel-art grids written as text in `scripts/characters.py`, each with a back view.

| character | status | used in | notes |
|---|---|---|---|
| `cultist` | good | garden_encounter, gui_lantern, gui_menus, neon_street, post_presets, tunnel_encounter, woodland_night |  |
| `scientist` | good | bunker_lab, coast_lighthouse, gui_lantern, orbital_hangar, tunnel_encounter |  |
| `guard` | good | garden_encounter, gui_menus, post_presets, rain_alley, rainy_street |  |
| `nurse` | good | ghost_corridor, gui_hud |  |
| `spiritualist` | good | cathedral_ruin, chapel_graveyard, gui_themes, gui_trade, library_medium |  |
| `ghost` | good | chapel_graveyard, garden_encounter, ghost_corridor, ghost_town, gui_hud, gui_menus, haunted_house, post_presets, woodland_night |  |
| `hybrid` | good | gui_lantern, sewer_tunnels, tunnel_encounter |  |
| `soldier` | good | castle_keep |  |
| `knight` | good | castle_keep, misty_moor, village_green |  |
| `child` | polish | autumn_lane, village_green, winter_lake, winter_woods | Head reads large and round; check the proportions. |
| `creature` | good | castle_keep, crystal_cave |  |
| `robot` | good | crystal_cave |  |
| `shopkeeper` | good | ghost_town, neon_street, village_green |  |
| `astronaut` | good | alien_world, moon_base, orbital_hangar, space_station |  |
| `android` | good | neon_street, orbital_hangar, space_station |  |
| `alien` | good | alien_world, derelict_ship | A familiar archetype; could be made stranger. |
| `dreamer` | polish | dream_chess, dream_world, drowned_library | The face reads as open-eyed; a sleepwalker wants closed eyes. |
| `claude` | good | claude_study | Claude's own avatar. |
| `explorer` | good | jungle_temple, red_canyon |  |
| `hoplite` | good | ancient_ruins |  |
| `castaway` | good | tropical_beach |  |
| `diver` | good | kelp_forest | A brass diving helmet with a round faceplate and an air hose, a canvas suit, a weight belt, heavy boots. |
| `runner` | good | neon_street | A cyberpunk: dark hair with a pink streak, a lit cyan visor, a black jacket striped in neon. |
| `cowboy` | good | ghost_town, red_canyon | A wide-brimmed hat, moustache, red bandana, a vest over a tan shirt, a gun belt, jeans and boots; for the canyon. |
| `witch` | good | autumn_lane | A crooked pointed hat banded in purple, green skin, glowing yellow eyes, a robe, a lit lantern at her side. |
| `farmer` | good | village_green | A straw hat, plaid shirt and blue overalls, a pitchfork taller than him. |
| `pirate` | good | bayou | A gold-edged tricorn, an eye patch and beard, a red coat with gold buttons, a cutlass. |

## Decals (25)

Stamps blended into floors, walls and ceilings. `grime` stamps some of them on its own, and `contact_shadow` goes under every prop that stands on the ground.

| decal | status | used in | notes |
|---|---|---|---|
| `puddle` | good | coast_lighthouse, rainy_street, woodland_night |  |
| `puddle_dark` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, sewer_tunnels, woodland_night |  |
| `puddle_shine` | good | coast_lighthouse, neon_street, rain_alley, rainy_street, sewer_tunnels |  |
| `stain` | polish | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, sewer_tunnels, woodland_night | A plain blob; uneven edge, drip marks. |
| `stain_rust` | polish | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, orbital_hangar, rainy_street, sewer_tunnels | Same as stain. |
| `splatter` | good | - |  |
| `splatter_dark` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, sewer_tunnels |  |
| `vines` | good | jungle_temple, rainy_street |  |
| `moss_patch` | polish | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, jungle_temple, rainy_street, sewer_tunnels, woodland_night | Blob; give it clumps and a soft edge. |
| `crack` | good | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, rainy_street, sewer_tunnels |  |
| `scorch` | good | bunker_lab, cathedral_ruin, derelict_ship, sewer_tunnels, tropical_beach |  |
| `leak` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, rainy_street, sewer_tunnels |  |
| `cobweb` | good | bunker_lab, castle_keep |  |
| `rune_mark` | good | - |  |
| `drain` | good | bunker_lab, neon_street, rainy_street, sewer_tunnels |  |
| `contact_shadow` | good | 47 scenes |  |
| `pad_marking` | good | moon_base, orbital_hangar | A painted landing ring with an H and a dashed outer ring, worn in patches. |
| `rover_tracks` | good | moon_base | Drawn with the toolkit in moon.py: two tracks of chevron treads pressed into dust. |
| `hazard_stripe` | good | orbital_hangar | A band of yellow and black diagonal stripes, worn through in places. |

### Shore and pool

| decal | status | used in | notes |
|---|---|---|---|
| `foam` | polish | tropical_beach | Edge-on from eye height: pair with the surf props. |
| `foam_glow` | polish | tropical_beach | As foam. |
| `starfish` | good | kelp_forest, tropical_beach |  |
| `shells` | good | kelp_forest, tropical_beach |  |
| `seaweed` | good | kelp_forest, tropical_beach |  |
| `lily_pads` | good | bayou, jungle_temple |  |

## Skies (11)

| sky | status | used in | notes |
|---|---|---|---|
| `night` | good | ancient_ruins, bayou, chapel_graveyard, claude_study, garden_encounter, gui_menus, haunted_house, hospital_garden, kelp_forest, neon_street, post_presets, tropical_beach, village_green, winter_lake, winter_woods, woodland_night |  |
| `dusk` | good | autumn_lane, coast_lighthouse, misty_moor |  |
| `storm` | good | coast_lighthouse, rain_alley, rainy_street | Could use darker cloud masses. |
| `day` | good | cathedral_ruin, ghost_town, jungle_temple, kelp_forest, red_canyon, tropical_beach, village_green, winter_lake, winter_woods |  |
| `overcast` | good | winter_woods |  |
| `blood` | good | - |  |
| `space` | good | moon_base, orbital_hangar, space_station |  |
| `alien` | good | alien_world |  |
| `dream` | good | dream_chess, dream_world, drowned_library |  |
| `sunset` | good | bayou, ghost_town, red_canyon, tropical_beach |  |
| `golden` | good | ancient_ruins, autumn_lane, bayou, woodland_night |  |

## Skylines (6)

| skyline | status | used in | notes |
|---|---|---|---|
| `mountains` | good | alien_world, jungle_temple, winter_lake |  |
| `hills` | good | misty_moor |  |
| `treeline` | good | chapel_graveyard |  |
| `city` | good | neon_street | Window grid is regular; vary building tops (spires, water towers). |
| `islands` | polish | ancient_ruins, tropical_beach | In haze an island and its reflection can read as a saucer floating on the horizon. |
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
| `stones` | good | rocks x3, boulder | chapel_graveyard, coast_lighthouse, misty_moor |  |
| `snow` | good | rocks x3, boulder_snow | winter_lake, winter_woods | The stones set for winter: its boulder is under snow, not moss. |
| `rubble` | good | rubble x2, rocks, broken_barrel | cathedral_ruin, rainy_street |  |
| `forest` | good | rocks x2, log, stump, mushrooms, grass_tuft x2, fern, bush | woodland_night |  |
| `undergrowth` | good | grass_tuft x3, fern, bush, mushrooms | chapel_graveyard, woodland_night |  |
| `autumn` | good | grass_tuft x2, fern, bush_autumn x2, mushrooms | autumn_lane | The undergrowth set for the fall: its bush turned. |
| `shore` | good | rocks x3, boulder, reeds, bones | coast_lighthouse |  |
| `litter` | good | sack, bucket, crate, barrel, broken_barrel, bones | neon_street, rain_alley |  |
| `wreckage` | good | rubble x2, broken_barrel, rocks, bones, sack, bucket | bunker_lab, cathedral_ruin, derelict_ship, sewer_tunnels |  |
| `cave` | good | rocks x3, stalagmite, glowshroom, crystal, bones | crystal_cave |  |
| `alien` | good | rocks x2, crystal, glowshroom, alien_plant, alien_egg | alien_world |  |
| `derelict` | good | rubble x2, sci_crate, bones, rocks, alien_egg | derelict_ship |  |
| `jungle` | good | fern x3, monstera, bromeliad x2, heliconia, mushrooms | jungle_temple |  |
| `beach` | good | coconuts, driftwood, rocks x2, crab, dry_tuft | tropical_beach |  |
| `ruins` | good | column_drum, rubble, rocks x2, poppies, dry_tuft x2, amphora | ancient_ruins |  |
| `desert` | good | rocks x3, prickly_pear, tumbleweed, cow_skull, dry_tuft | ghost_town, red_canyon | Rocks with the odd prickly pear, tumbleweed, skull and dry tuft. |
| `swamp` | good | cattails x2, reeds, cypress_knees, rocks | - | Cattails and reeds with cypress knees and the odd rock. |
| `seabed` | good | rocks x3, crab, boulder | kelp_forest | Rocks with the odd crab and boulder. |

## Fringe sets (6)

The cards a `fringe` wall stands in front of its open faces, back to front.

| set | status | cards | used in | notes |
|---|---|---|---|---|
| `jungle` | good | jungle_card_4, jungle_card_3, jungle_card_2, jungle_card_1 | jungle_temple | Four cards: bushes alone at the front, a dense wall of trees, crowns and bushes at the back. |
| `forest` | good | forest_card_4, forest_card_3, forest_card_2, forest_card_1 | haunted_house, woodland_night | Four cards: bushes, ferns and grass at the front, a dense wall of spruce and oak at the back. Keep the wall behind lower (2-2.6) than the trees. |
| `forest_autumn` | good | autumn_card_4, autumn_card_3, autumn_card_2, autumn_card_1 | autumn_lane | The forest fringe in October: oak, birch and bush turned, the spruce among them still green. |
| `forest_snow` | good | winter_card_4, winter_card_3, winter_card_2, winter_card_1 | winter_woods | The forest fringe in winter: snowy spruce, bare oak and birch with snow on their limbs, bushes under snow. |
| `swamp` | good | swamp_card_3, swamp_card_2, swamp_card_1 | bayou | Three cards: cattails and knees, then young cypresses and moss, then a dense stand. |
| `kelp` | good | kelp_card_2, kelp_card_1 | kelp_forest | Two cards: a few stalks, then a dense stand. |

## Facade styles (6)

The looks a `facade` can give its buildings (`scripts/buildings.py`); each building is drawn in layers - wall, frames and glass, drapes, rooms.

| style | status | used in | notes |
|---|---|---|---|
| `brick` | good | rain_alley | Red and brown brick, painted sash windows, curtains and blinds, shops. |
| `sooty` | good | rain_alley | Soot-blackened tenements, dark frames. |
| `plaster` | polish | - | Washed plaster; only seen on the review sheets so far, no scene uses it. |
| `neon` | good | neon_street | Concrete panels with form-tie holes, neon signs over the shops and up the walls, blade signs on their own cards, roller shutters, air conditioners, rooms lit pink, blue and green. |
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
| `ruined_columns` | good | 8 sprites | ancient_ruins |  |
| `altar_fire` | good | 1 sprites, 1 lights, a map | - | Brings its own block of map. |
| `beach_hut` | good | 2 sprites, 2 lights, a map | tropical_beach | A patch of map with its own legend: walls, door, window, roof, light. |
| `tiki_torches` | good | 2 sprites, 1 lights | tropical_beach |  |
| `street_lamp` | good | 1 sprites, 1 lights, 1 decals | rain_alley |  |
| `graves` | good | 5 sprites | - |  |
| `shrine` | good | 2 sprites, 1 lights | jungle_temple |  |

## Held items (6)

| item | status | used in | notes |
|---|---|---|---|
| `revolver` | polish | gui_hud, rainy_street | The hand and sleeve are blocky; shade the knuckles and cuff. |
| `lantern` | polish | gui_lantern, woodland_night | The hand and sleeve are blocky; shade the knuckles and cuff. |
| `flashlight` | polish | bunker_lab, derelict_ship, sewer_tunnels | The hand and sleeve are blocky; shade the knuckles and cuff. |
| `axe` | polish | - | The hand and sleeve are blocky; shade the knuckles and cuff. |
| `crowbar` | polish | - | The hand and sleeve are blocky; shade the knuckles and cuff. |
| `torch` | polish | - | The hand and sleeve are blocky; shade the knuckles and cuff. |

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

## GUI themes (5)

| theme | status | used in | notes |
|---|---|---|---|
| `classic` | good | 41 scenes |  |
| `parchment` | good | gui_themes, gui_trade |  |
| `terminal` | good | bunker_lab, gui_themes, orbital_hangar, space_station |  |
| `blood` | good | gui_themes |  |
| `steel` | good | gui_themes |  |

## GUI widgets (16)

| widget | status | used in | notes |
|---|---|---|---|
| `bubble` | good | alien_world, autumn_lane, castle_keep, claude_study, crystal_cave, garden_encounter, ghost_corridor, ghost_town, gui_menus, gui_trade, haunted_house, neon_street, rainy_street, tunnel_encounter, village_green, winter_lake, winter_woods, woodland_night |  |
| `dialog` | good | bunker_lab, chapel_graveyard, claude_study, coast_lighthouse, ghost_corridor, library_medium, orbital_hangar, space_station |  |
| `caption` | good | 34 scenes |  |
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

## Example scenes (47)

The environments, judged on their gallery images and shots.

### Horror and mystery

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `garden_encounter` | good | 2 | garden_01, garden_02, layout_map | The cobble path repeats a little in the wide shot. |
| `ghost_corridor` | good | 3 | corridor_03 |  |
| `hospital_corridor` | good | 3 | - | An empty corridor; the second shot is very dark. |
| `hospital_garden` | good | 3 | hospital_garden_01 |  |
| `library_medium` | good | 1 | library_medium |  |
| `mansion_library` | polish | 2 | - | Wide and empty: the shelves are far off and the beamed ceiling becomes radiating stripes. |
| `haunted_house` | good | 4 | haunted_front, haunted_hall, haunted_parlour, haunted_ghost | Halloween at the old house: the front with jack-o'-lanterns and bats, the hall's grand stair and landing, the parlour, the ghost on the stairs. |
| `tunnel_encounter` | good | 2 | tunnel_01 |  |
| `underground_waterway` | polish | 4 | waterway_01 | Murky: the far end and the boat are hard to read. |
| `sewer_tunnels` | good | 3 | sewer_thing |  |
| `bunker_lab` | good | 4 | bunker_hud, bunker_crt |  |

### Outdoors

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `woodland_night` | good | 6 | woods_path, woods_fire, woods_dawn, woods_moon | Rebuilt for the forest fringe: `forest_deep` walls 2.4 high, free-standing spruce, oak, birch and dead trees, a moon in volumetric fog, a dawn shot through overrides, a ghost up the north road. |
| `autumn_lane` | good | 4 | autumn_lane, autumn_scarecrow, autumn_dusk, autumn_walk | A lane through an autumn wood under a low sun, a field with a scarecrow, pumpkins and hay bales behind a wall; jack-o'-lanterns at dusk. |
| `bayou` | good | 4 | bayou_dusk, bayou_night, bayou_gator, bayou_heron | A shack on an island in black water between mossy cypresses: sundown, fireflies at night, an alligator, a heron in mist. |
| `kelp_forest` | good | 4 | sea_kelp, sea_diver, sea_shoal, sea_night | A kelp forest in teal water: a wreck with its mast, a diver with bubbles rising, a shoal; a night dive by flashlight with jellyfish. |
| `coast_lighthouse` | polish | 4 | coast_tower, coast_jetty | The shore rocks in the tower shot are grey lumps. |
| `rainy_street` | good | 4 | street_rain, street_lightning |  |
| `rain_alley` | good | 4 | alley_street, alley_rain, alley_glass, alley_storm |  |
| `neon_street` | good | 4 | neon_street, neon_stall, neon_signs, neon_runner | The neon facade style in the rain: signs, blade signs, lantern wires, a hologram koi, a noodle stall, vending machines, steam, the runner; bloom on the neon. |
| `village_green` | good | 4 | village_market, village_stall, village_well, village_night | A cobbled street of timber-framed houses to a green: a market stall and its keeper, the inn sign, a cart, the well; the inn lit after closing. |
| `ghost_town` | good | 4 | western_noon, western_saloon, western_ghost, western_windpump | A frontier main street: a cowboy at high noon, the saloon and its barkeep, sundown with lanterns and a ghost, a windpump in the desert. |
| `misty_moor` | polish | 3 | moor_dawn, moor_circle | The standing stones are plain blocks; weathered tops and lichen would help. |
| `winter_lake` | polish | 4 | winter_night, winter_day | The ice is blotchy (see the ice texture). |
| `winter_woods` | good | 4 | winter_lane, winter_deer, winter_lantern, winter_stream | A snowbound wood: the lane, a deer on a frozen stream in falling snow, a child by a lantern-lit footbridge, trees mirrored in the ice. |
| `chapel_graveyard` | good | 4 | chapel_yard, chapel_nave | The yard is a little sparse. |

### Castles, ruins and caves

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `castle_keep` | polish | 5 | castle_throne, castle_gate | The throne hall is long and bare, and the throne small and far. |
| `cathedral_ruin` | polish | 3 | cathedral_beam, cathedral_pilgrim | The hole in the roof reads as a flat white quad; the nave is bare. |
| `crystal_cave` | good | 3 | cave_beast |  |

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
| `jungle_temple` | good | 4 | jungle_path, jungle_temple, jungle_jaguar, jungle_canopy | The canopy from the pyramid top still shows hedge-like steps up close. |
| `ancient_ruins` | good | 4 | ruins_way, ruins_head, ruins_night | The cella shot could use shafts of light through the columns. |
| `red_canyon` | good | 4 | canyon_wash, canyon_ruins, canyon_slot, canyon_sunset | A wash between ragged walls of layered sandstone, saguaros, cliff-dwelling ruins, a slot canyon lit by one beam, the wall at sunset. |
| `tropical_beach` | good | 4 | beach_sunset, beach_pier, beach_day, beach_night |  |

## Pass log

- **2026-10-19, pass 0.** First full review of every asset, on review sheets and in the gallery. This file and `docs/asset_review.py` were added.
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

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
| Textures | 126 | 90 | 29 | 7 | 0 |
| Props | 123 | 101 | 19 | 3 | 0 |
| Characters | 21 | 19 | 2 | 0 | 0 |
| Decals | 22 | 17 | 5 | 0 | 0 |
| Skies | 11 | 11 | 0 | 0 | 0 |
| Skylines | 6 | 5 | 1 | 0 | 0 |
| Sky objects | 5 | 5 | 0 | 0 | 0 |
| Scatter sets | 13 | 13 | 0 | 0 | 0 |
| Fringe sets | 1 | 1 | 0 | 0 | 0 |
| Facade styles | 3 | 2 | 1 | 0 | 0 |
| Prefabs | 13 | 13 | 0 | 0 | 0 |
| Held items | 6 | 0 | 6 | 0 | 0 |
| Icons | 26 | 26 | 0 | 0 | 0 |
| GUI themes | 5 | 5 | 0 | 0 | 0 |
| GUI widgets | 16 | 16 | 0 | 0 | 0 |
| Post presets | 20 | 20 | 0 | 0 | 0 |
| Palettes | 9 | 9 | 0 | 0 | 0 |
| Example scenes | 34 | 26 | 8 | 0 | 0 |
| **all** | **460** | **379** | **71** | **10** | **0** |
<!-- /summary -->

## Pass plan

Weakest first, and in the order the new scenes need them.

1. **Nature.** The plant and ground textures are the weakest part of the set: foliage, hedge, grass and dirt are coloured noise, and bark has a seam. Rework `foliage`, `foliage_autumn`, `hedge`, `grass`, `dirt`, `bark`, `bark_pine` and the `tree` and `bush` props; polish `moss`, `gravel`, `sand`, `pine_needles` and the `flowers`, `boulder` and `log` props. The pixel-art toolkit (`scripts/pixelart.py`) that drew the jungle, ruins and beach is the way to do it: clusters of shaped leaves lit from above rather than noise.
2. **Stone and ruins.** `rock`, `rock_wet`, `rock_floor`, `snow_rock`, `cobble`, `marble_dark`, `ivy`, `shingle`; the `column`, `statue` and `fountain` props; the standing stones in misty_moor and the roof hole in cathedral_ruin.
3. **Water and ice.** `water` (depth, caustics, a ripple that tiles), `ice`; the `rowboat` and `buoy` props; the shore rocks in coast_lighthouse.
4. **Interiors.** `plaster`, `plaster_white`, `ceiling_plaster`, `acoustic`, `beams`, `wood_panel`, `curtain`, `curtain_black`, `corrugated`; the `barrel`, `broken_barrel`, `crate`, `chest`, `bed`, `bench`, `table` and `wheelchair` props; the castle_keep throne hall.
5. **Small things.** The hands on the held items, the `stain`, `stain_rust` and `moss_patch` decals, the `child` and `dreamer` characters, the `city` skyline, `alien_rock`, `alien_ground`, and the `glowshroom` and `alien_egg` props.
6. **Second look.** Every asset marked good, checked again on the review sheets and in its scenes, with fresh eyes and the new techniques in hand.

## Textures (126)

64x64 tiles, drawn in code. "glows" means the texture lights itself (windows, screens, runes), "see-through" that the map shows through its holes, "mirror" that floors made of it reflect.

### Masonry and plaster

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `brick` | good |  | rainy_street |  |
| `brick_dark` | good |  | rain_alley |  |
| `brick_yellow` | good |  | - |  |
| `stone` | good |  | claude_study, garden_encounter, gui_menus, hospital_garden, post_presets | Even block sizes; a few varied heights would help on long walls. |
| `stone_dark` | good |  | cathedral_ruin, garden_encounter, gui_menus, gui_themes, gui_trade, hospital_garden, library_medium, mansion_library, misty_moor, post_presets, rainy_street |  |
| `stone_pale` | good |  | cathedral_ruin, chapel_graveyard, coast_lighthouse, dream_world, garden_encounter, gui_menus, hospital_garden, post_presets |  |
| `castle` | good |  | castle_keep | Mortar grid is very regular; chip a few corners. |
| `moss_stone` | good |  | coast_lighthouse, misty_moor |  |
| `slime_brick` | good |  | sewer_tunnels |  |
| `plaster` | polish |  | rainy_street | The vertical stains read as stripes in a 2x2 tiling; the dado band is hard-edged. |
| `plaster_white` | polish |  | garden_encounter, gui_menus, hospital_garden, post_presets | Same as plaster. |
| `hospital_wall` | good |  | ghost_corridor, gui_hud, hospital_corridor |  |
| `ivy` | polish |  | rainy_street | Ivy is soft blotches; give it leaf shapes and stems. |
| `concrete` | good |  | bunker_lab, garden_encounter, gui_lantern, gui_menus, hospital_garden, post_presets, sewer_tunnels, tunnel_encounter, underground_waterway |  |
| `marble` | good |  | cathedral_ruin, chapel_graveyard, dream_world, gui_themes, gui_trade, library_medium, mansion_library |  |
| `marble_dark` | polish |  | - | Veins read as dotted lines; make them continuous and softer. |
| `rock` | polish |  | castle_keep, coast_lighthouse, crystal_cave, garden_encounter, gui_lantern, gui_menus, hospital_garden, post_presets, tunnel_encounter, underground_waterway | Crack network looks like jigsaw pieces; add strata and lit edges. |
| `rock_wet` | polish |  | crystal_cave, gui_lantern, tunnel_encounter, underground_waterway | Same as rock; wet sheen highlights would sell it. |
| `snow_rock` | polish |  | winter_lake | Snow is blotchy; it should lie on ledges and in cracks. |
| `sky_wall` | good |  | dream_world |  |

### Wood

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `wood_panel` | polish |  | - | Flat; needs panel frames and grain. |
| `planks` | good |  | - |  |
| `boards` | good |  | coast_lighthouse, rain_alley, tropical_beach |  |
| `logs` | good |  | coast_lighthouse, winter_lake |  |
| `door_wood` | good |  | dream_world, winter_lake |  |
| `bookshelf` | good |  | claude_study, gui_themes, gui_trade, library_medium, mansion_library |  |
| `bark` | rework |  | woodland_night | Reads as wavy wood grain, not bark, and shows a horizontal seam when tiled; needs plates and furrows. |
| `bark_pine` | rework |  | - | Same as bark; pine bark is flaky reddish plates. |
| `wood_floor` | good |  | claude_study, gui_lantern, gui_themes, gui_trade, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `shingle` | polish |  | chapel_graveyard, coast_lighthouse, rainy_street, winter_lake | Looks like grey brick; shingles want staggered rounded tabs and shadow under each row. |

### Metal and sci-fi

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `iron_door` | good |  | bunker_lab, garden_encounter, ghost_corridor, gui_hud, gui_lantern, gui_menus, hospital_corridor, hospital_garden, post_presets, rainy_street, tunnel_encounter, underground_waterway |  |
| `corrugated` | polish |  | rainy_street | Rust blotches repeat visibly. |
| `rust` | good |  | bunker_lab, rainy_street |  |
| `pipes` | good |  | bunker_lab, sewer_tunnels |  |
| `panel` | good |  | bunker_lab, derelict_ship, space_station |  |
| `panel_green` | good |  | bunker_lab |  |
| `hull` | good |  | space_station |  |
| `hull_dark` | good |  | derelict_ship, space_station |  |
| `hull_lit` | good | glows | space_station |  |
| `hull_red` | good | glows | derelict_ship |  |
| `tech_panel` | good | glows | space_station |  |
| `server` | good | glows | space_station |  |
| `blast_door` | good | glows | derelict_ship, space_station |  |
| `hazard` | good |  | - |  |
| `deck` | good |  | derelict_ship, space_station |  |
| `grate` | good |  | bunker_lab, derelict_ship |  |
| `grid_floor` | good | glows, mirror 0.3 | - |  |
| `hex_panel` | good |  | alien_world |  |

### Nature

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `foliage` | rework |  | woodland_night | Green noise, no leaves: the weakest texture in the set. Needs leaf clusters with lit tops and dark gaps. |
| `foliage_autumn` | rework |  | - | Same as foliage. |
| `hedge` | rework |  | garden_encounter, gui_menus, hospital_garden, post_presets | Same as foliage, clipped: small leaves, flatter face. |
| `grass` | rework |  | cathedral_ruin, chapel_graveyard, dream_world, garden_encounter, gui_menus, hospital_garden, misty_moor, post_presets | Noise; needs blade strokes and clumps seen from above. |
| `moss` | polish |  | - | Noise with stone patches; add cushion clumps. |
| `mud` | good |  | woodland_night |  |
| `dirt` | rework |  | castle_keep | Salt-and-pepper speckle; needs clods, pebbles and damp patches. |
| `gravel` | polish |  | chapel_graveyard, coast_lighthouse, garden_encounter, gui_menus, hospital_garden, post_presets | Speckle; give it individual pebbles with a lit edge. |
| `sand` | polish |  | coast_lighthouse | Plain noise; wind ripples and the odd shell fragment. |
| `snow` | good |  | winter_lake |  |
| `ice` | polish | mirror 0.38 | winter_lake | Cracks look like scribbles; straighter fractures, depth in the blue. |
| `water` | polish | mirror 0.5 | alien_world, coast_lighthouse, crystal_cave, gui_lantern, sewer_tunnels, tunnel_encounter, underground_waterway | Flat teal with white dashes; needs depth, caustics and a ripple pattern that tiles. |
| `pine_needles` | polish |  | woodland_night | Noise with green patches; needs needle strokes and cones. |
| `alien_ground` | polish |  | alien_world | Crystal flecks are uniform white specks; vary size and tint. |
| `alien_rock` | polish | glows | alien_world | Veins too thick and dense; the repeat shows when tiled. |
| `organic` | good |  | derelict_ship |  |
| `cloud_floor` | good |  | - |  |

### Floors

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `checker` | good |  | dream_world |  |
| `linoleum` | good |  | ghost_corridor, gui_hud, hospital_corridor |  |
| `tile_floor` | good |  | bunker_lab, derelict_ship |  |
| `tile_white` | good |  | - |  |
| `tile_green` | good |  | - |  |
| `cobble` | polish |  | garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street | Good stones, but the same few repeat in a 2x2 tiling. |
| `asphalt` | good |  | rain_alley, rainy_street |  |
| `carpet` | good |  | castle_keep, chapel_graveyard, claude_study, gui_themes, gui_trade, library_medium, mansion_library |  |
| `carpet_green` | good |  | - |  |
| `flagstone` | good |  | castle_keep, cathedral_ruin, chapel_graveyard, claude_study, rain_alley |  |
| `obsidian` | good | mirror 0.45 | dream_world, space_station |  |
| `concrete_floor` | good |  | 34 scenes |  |
| `rock_floor` | polish |  | crystal_cave, gui_lantern, tunnel_encounter, underground_waterway | Same as rock. |

### Ceilings

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `acoustic` | polish |  | ghost_corridor, gui_hud, hospital_corridor | Flat; a slight bevel per tile. |
| `ceiling_plaster` | polish |  | gui_themes, gui_trade, library_medium | A hard horizontal band across the middle of the tile. |
| `beams` | polish |  | castle_keep, cathedral_ruin, chapel_graveyard, claude_study, mansion_library | Reads as stripes; beams want depth (a lit side and a shadow side). |

### Fabric and interior

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `curtain` | polish |  | gui_themes, gui_trade, library_medium, mansion_library | Folds are even stripes; vary width and add a hem. |
| `curtain_black` | polish |  | - | Same as curtain. |
| `wallpaper` | good |  | gui_themes, gui_trade, library_medium, mansion_library |  |
| `wallpaper_green` | good |  | - |  |

### Light sources

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `window_lit` | good | glows | coast_lighthouse, garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street | Simple; a silhouette in one pane now and then would add life. |
| `window_dark` | good |  | garden_encounter, gui_menus, gui_themes, gui_trade, hospital_garden, library_medium, mansion_library, post_presets, rainy_street |  |
| `window_lit_plaster` | good | glows | garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street, winter_lake |  |
| `window_dark_plaster` | good |  | garden_encounter, ghost_corridor, gui_hud, gui_menus, hospital_corridor, hospital_garden, post_presets, rainy_street |  |
| `window_teal` | good | glows | garden_encounter, gui_menus, hospital_garden, post_presets |  |
| `stained_glass` | good | glows | castle_keep, chapel_graveyard |  |
| `runes` | good | glows | gui_lantern, gui_themes, gui_trade, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `fireplace` | good | glows | claude_study |  |
| `star_chart` | good | glows | claude_study |  |

### See-through

| texture | status | traits | used in | notes |
|---|---|---|---|---|
| `bars` | good | see-through | castle_keep |  |
| `fence_iron` | good | see-through | chapel_graveyard |  |
| `chainlink` | good | see-through | - |  |
| `railing` | good | see-through | claude_study, sewer_tunnels |  |
| `picket` | good | see-through | - |  |
| `portcullis` | good | see-through | castle_keep |  |
| `window_broken` | good | see-through | cathedral_ruin |  |
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
| `ruin_paving` | good |  | ancient_ruins, jungle_temple |  |
| `dry_grass` | polish |  | ancient_ruins | Busy at grazing angles; fewer, larger clumps. |
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

## Props (123)

Camera-facing sprites. "tall" is the default height in world units (a wall is 1); "no shadow" props hang, float or burn, so they get no contact shadow.

### Furniture and interior

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `armchair` | good | 0.6 tall | claude_study |  |
| `bed` | polish | 0.4 tall | bunker_lab, ghost_corridor, gui_hud, hospital_corridor | Plain; add a pillow, blanket fold and frame detail. |
| `bench` | polish | 0.35 tall | coast_lighthouse, garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street | Plain slats; add a backrest variant. |
| `book_stack` | good | 0.22 tall | claude_study |  |
| `chest` | polish | 0.3 tall | castle_keep | Lid corners read as dark notches. |
| `console` | good | 0.85 tall, glows | bunker_lab, space_station |  |
| `crate` | polish | 0.4 tall | bunker_lab, coast_lighthouse, gui_lantern, gui_themes, gui_trade, hospital_corridor, library_medium, mansion_library, rain_alley, rainy_street, sewer_tunnels, tunnel_encounter, underground_waterway, winter_lake, woodland_night | Just a cross brace; add plank seams. |
| `barrel` | polish | 0.45 tall | bunker_lab, coast_lighthouse, gui_lantern, gui_themes, gui_trade, library_medium, mansion_library, rain_alley, rainy_street, sewer_tunnels, tunnel_encounter, underground_waterway | Flat: needs a cylindrical highlight and stave lines. |
| `locker` | good | 1 tall | bunker_lab |  |
| `lectern` | good | 0.5 tall | chapel_graveyard |  |
| `open_book` | good | 0.12 tall, glows, no shadow | claude_study |  |
| `pew` | good | 0.42 tall | cathedral_ruin, chapel_graveyard |  |
| `table` | polish | 0.36 tall | castle_keep | Plain. |
| `throne` | good | 0.95 tall | castle_keep |  |
| `wheelchair` | polish | 0.45 tall | ghost_corridor, gui_hud, hospital_corridor | Reads as a box on a wheel. |
| `writing_desk` | good | 0.55 tall, glows | claude_study |  |
| `globe` | good | 0.45 tall | claude_study |  |
| `orrery` | good | 0.6 tall, glows | claude_study |  |
| `telescope` | good | 0.8 tall | claude_study |  |
| `painting` | good | 0.45 tall, no shadow | - |  |
| `wall_clock` | good | 0.28 tall, no shadow | bunker_lab, rainy_street |  |
| `banner` | good | 0.95 tall, no shadow | castle_keep, rainy_street |  |
| `chains` | good | 0.6 tall, no shadow | castle_keep |  |
| `ladder` | good | 1 tall, no shadow | sewer_tunnels |  |
| `pipe_valve` | good | 0.32 tall, no shadow | bunker_lab, sewer_tunnels |  |
| `sack` | good | 0.42 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, rain_alley, rainy_street, sewer_tunnels, woodland_night |  |
| `bucket` | good | 0.32 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, rain_alley, rainy_street, sewer_tunnels |  |

### Light and fire

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `brazier` | good | 0.85 tall, glows, no shadow | ancient_ruins, castle_keep, coast_lighthouse |  |
| `campfire` | good | 0.4 tall, glows, no shadow | tropical_beach, woodland_night |  |
| `candles` | good | 0.2 tall, glows, no shadow | castle_keep, cathedral_ruin, chapel_graveyard, gui_lantern, gui_themes, gui_trade, jungle_temple, library_medium, mansion_library, tunnel_encounter, underground_waterway |  |
| `ceiling_lamp` | good | 0.3 tall, glows, no shadow | bunker_lab, sewer_tunnels |  |
| `chandelier` | good | 0.45 tall, glows, no shadow | castle_keep, claude_study |  |
| `lamp_post` | good | 1.6 tall, glows | garden_encounter, gui_menus, hospital_garden, post_presets, rain_alley, rainy_street | Thin at a distance. |
| `lantern` | good | 0.3 tall, glows, no shadow | chapel_graveyard, coast_lighthouse, garden_encounter, gui_lantern, gui_menus, gui_themes, gui_trade, library_medium, mansion_library, post_presets, tunnel_encounter, underground_waterway, winter_lake, woodland_night |  |
| `sconce` | good | 0.32 tall, glows, no shadow | castle_keep, claude_study, rainy_street |  |

### Nature

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `boulder` | polish | 0.55 tall | chapel_graveyard, coast_lighthouse, misty_moor, winter_lake, woodland_night | The moss patches read as two eyes and a mouth. |
| `bush` | polish | 0.5 tall | chapel_graveyard, coast_lighthouse, woodland_night | A stack of green circles; needs leaf texture and a lit side. |
| `dead_tree` | good | 2.9 tall | chapel_graveyard, misty_moor, woodland_night |  |
| `fern` | good | 0.42 tall | chapel_graveyard, jungle_temple, misty_moor, tropical_beach, woodland_night | Redrawn: arching fronds from one crown. |
| `flowers` | polish | 0.35 tall | garden_encounter, gui_menus, hospital_garden, post_presets, rainy_street | Red dots on a bush. |
| `grass_tuft` | good | 0.4 tall | chapel_graveyard, coast_lighthouse, misty_moor, rainy_street, tropical_beach, woodland_night | Redrawn: thin arching blades. |
| `ivy_hang` | good | 0.8 tall, no shadow | cathedral_ruin, rainy_street, woodland_night |  |
| `log` | polish | 0.28 tall | tropical_beach, winter_lake, woodland_night | A flat bar with a dotted seam; needs bark and a lit top. |
| `mushrooms` | good | 0.12 tall | chapel_graveyard, jungle_temple, woodland_night |  |
| `palm` | good | 3.2 tall | garden_encounter, gui_menus, hospital_garden, post_presets, tropical_beach | Redrawn with the pixel-art toolkit: a ringed trunk, arching ragged fronds, coconuts. |
| `pine` | good | 3.4 tall | coast_lighthouse, woodland_night |  |
| `reeds` | good | 0.8 tall | coast_lighthouse |  |
| `rocks` | good | 0.22 tall | alien_world, ancient_ruins, bunker_lab, cathedral_ruin, chapel_graveyard, coast_lighthouse, crystal_cave, derelict_ship, misty_moor, rainy_street, sewer_tunnels, tropical_beach, winter_lake, woodland_night | Redrawn: half-sunk stones with lit tops and the odd crack. |
| `snowy_pine` | good | 3.4 tall | winter_lake |  |
| `stump` | good | 0.3 tall | tropical_beach, woodland_night |  |
| `tree` | rework | 2.6 tall | dream_world, garden_encounter, gui_menus, hospital_garden, post_presets | Canopy is a blob of circles; needs leaf clusters, light from above, gaps. |
| `glowshroom` | polish | 0.16 tall, glows, no shadow | alien_world, crystal_cave | Flat cut-outs; the caps want a gradient and a bright rim. |
| `crystal` | good | 0.36 tall, glows, no shadow | alien_world, crystal_cave |  |
| `stalagmite` | good | 0.8 tall | crystal_cave |  |

### Debris

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `bones` | good | 0.22 tall | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, crystal_cave, derelict_ship, rain_alley, sewer_tunnels, woodland_night |  |
| `broken_barrel` | rework | 0.46 tall | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, rain_alley, rainy_street, sewer_tunnels, woodland_night | An unreadable brown heap. |
| `rubble` | good | 0.34 tall | ancient_ruins, bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, rainy_street, sewer_tunnels, woodland_night |  |

### Monuments and outdoors

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `column` | good | 1 tall | ancient_ruins, cathedral_ruin | Redrawn: a fluted Doric column with capital and plinth. |
| `fountain` | rework | 0.9 tall | - | Flat grey shapes; needs water, a basin rim and shading. |
| `gravestone` | good | 0.6 tall | chapel_graveyard |  |
| `grave_cross` | good | 0.55 tall | chapel_graveyard |  |
| `signpost` | good | 1.3 tall | coast_lighthouse |  |
| `statue` | polish | 1.5 tall | garden_encounter, gui_menus, hospital_garden, mansion_library, post_presets | Featureless grey figure; give it a pose and lit planes. |
| `monolith` | good | 2.2 tall | alien_world |  |
| `rowboat` | polish | 0.3 tall | coast_lighthouse, gui_lantern, tunnel_encounter, underground_waterway | A flat brown shape; planks, gunwale, oars. |
| `buoy` | polish | 0.5 tall, glows | coast_lighthouse | Reads as a bottle. |
| `snowman` | good | 0.62 tall | winter_lake |  |
| `armor` | good | 0.66 tall | castle_keep |  |

### Sci-fi

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `antenna` | good | 2.4 tall, glows | alien_world |  |
| `drone` | good | 0.22 tall, glows, no shadow | space_station |  |
| `hologram` | good | 0.55 tall, glows, aura, no shadow | space_station |  |
| `lander` | good | 1.6 tall, glows | alien_world |  |
| `sci_crate` | good | 0.35 tall, glows | derelict_ship, space_station |  |
| `stasis_pod` | good | 1 tall, glows | derelict_ship |  |

### Alien and dream

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `alien_egg` | polish | 0.35 tall, glows | alien_world, derelict_ship | Reads as a brown sack with a green cross; it wants a wet sheen and veins. |
| `alien_plant` | good | 1.1 tall, glows | alien_world |  |
| `balloon` | good | 2.6 tall, no shadow | dream_world |  |
| `chess_king` | good | 1.5 tall | dream_world |  |
| `chess_pawn` | good | 0.9 tall | dream_world |  |
| `door_frame` | good | 1.1 tall | dream_world |  |
| `floating_rock` | good | 1.6 tall, no shadow | dream_world |  |
| `koi` | good | 0.35 tall, no shadow | dream_world |  |
| `orb` | good | 0.2 tall, glows, aura, no shadow | dream_world |  |
| `pocket_watch` | good | 0.8 tall, no shadow | dream_world |  |
| `sky_whale` | good | 2 tall, glows, no shadow | dream_world |  |

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
| `cypress` | good | 4 tall | ancient_ruins |  |
| `olive_tree` | good | 2.2 tall | ancient_ruins |  |
| `poppies` | good | 0.24 tall | ancient_ruins |  |
| `dry_tuft` | good | 0.36 tall | ancient_ruins, tropical_beach |  |

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
| `jaguar` | polish | 0.34 tall, glows | jungle_temple | Reads as a friendly cat: a leaner body, rosettes rather than stripes. |
| `macaw` | good | 0.3 tall | jungle_temple |  |
| `goat` | polish | 0.34 tall | ancient_ruins | Legs long and stiff. |
| `crab` | good | 0.08 tall | tropical_beach |  |
| `seagull` | good | 0.14 tall, no shadow | tropical_beach |  |

### Cards and parts

| prop | status | traits | used in | notes |
|---|---|---|---|---|
| `jungle_card_1` | good | 1.4 tall | jungle_temple | The front of a jungle fringe: bushes alone. |
| `jungle_card_2` | good | 3.4 tall | jungle_temple | A few trees with bushes in front. |
| `jungle_card_3` | good | 4 tall | jungle_temple | More trees, tall ones with crowns. |
| `jungle_card_4` | good | 4.6 tall | jungle_temple | The back: a dense wall of trunks, crowns, palms and bushes. Repeats every 8 units. |
| `palm_trunk` | good | 3.2 tall | tropical_beach | The palm without its crown, for palm_3d. |
| `palm_crown` | good | 3.2 tall, no shadow | tropical_beach | The palm's crown alone, in the same frame as the trunk. |
| `glass_pane` | good | 1 tall | - | A plain pane for the glass pass. |


## Characters (21)

Pixel-art grids written as text in `scripts/characters.py`, each with a back view.

| character | status | used in | notes |
|---|---|---|---|
| `cultist` | good | garden_encounter, gui_lantern, gui_menus, post_presets, tunnel_encounter, woodland_night |  |
| `scientist` | good | bunker_lab, coast_lighthouse, gui_lantern, tunnel_encounter |  |
| `guard` | good | garden_encounter, gui_menus, post_presets, rain_alley, rainy_street |  |
| `nurse` | good | ghost_corridor, gui_hud |  |
| `spiritualist` | good | cathedral_ruin, chapel_graveyard, gui_themes, gui_trade, library_medium |  |
| `ghost` | good | chapel_graveyard, garden_encounter, ghost_corridor, gui_hud, gui_menus, post_presets |  |
| `hybrid` | good | gui_lantern, sewer_tunnels, tunnel_encounter |  |
| `soldier` | good | castle_keep |  |
| `knight` | good | castle_keep, misty_moor |  |
| `child` | polish | winter_lake | Head reads large and round; check the proportions. |
| `creature` | good | castle_keep, crystal_cave |  |
| `robot` | good | crystal_cave |  |
| `shopkeeper` | good | - |  |
| `astronaut` | good | alien_world, space_station |  |
| `android` | good | space_station |  |
| `alien` | good | alien_world, derelict_ship | A familiar archetype; could be made stranger. |
| `dreamer` | polish | dream_world | The face reads as open-eyed; a sleepwalker wants closed eyes. |
| `claude` | good | claude_study | Claude's own avatar. |
| `explorer` | good | jungle_temple |  |
| `hoplite` | good | ancient_ruins |  |
| `castaway` | good | tropical_beach |  |

## Decals (22)

Stamps blended into floors, walls and ceilings. `grime` stamps some of them on its own, and `contact_shadow` goes under every prop that stands on the ground.

| decal | status | used in | notes |
|---|---|---|---|
| `puddle` | good | coast_lighthouse, rainy_street, woodland_night |  |
| `puddle_dark` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, sewer_tunnels, woodland_night |  |
| `puddle_shine` | good | coast_lighthouse, rain_alley, rainy_street, sewer_tunnels |  |
| `stain` | polish | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, sewer_tunnels, woodland_night | A plain blob; uneven edge, drip marks. |
| `stain_rust` | polish | bunker_lab, cathedral_ruin, coast_lighthouse, derelict_ship, rainy_street, sewer_tunnels | Same as stain. |
| `splatter` | good | - |  |
| `splatter_dark` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, sewer_tunnels |  |
| `vines` | good | jungle_temple, rainy_street, woodland_night |  |
| `moss_patch` | polish | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, jungle_temple, rainy_street, sewer_tunnels, woodland_night | Blob; give it clumps and a soft edge. |
| `crack` | good | bunker_lab, castle_keep, cathedral_ruin, coast_lighthouse, derelict_ship, rainy_street, sewer_tunnels |  |
| `scorch` | good | bunker_lab, cathedral_ruin, derelict_ship, sewer_tunnels, tropical_beach |  |
| `leak` | good | bunker_lab, castle_keep, cathedral_ruin, derelict_ship, rainy_street, sewer_tunnels |  |
| `cobweb` | good | bunker_lab, castle_keep |  |
| `rune_mark` | good | - |  |
| `drain` | good | bunker_lab, rainy_street, sewer_tunnels |  |
| `contact_shadow` | good | 34 scenes |  |

### Shore and pool

| decal | status | used in | notes |
|---|---|---|---|
| `foam` | polish | tropical_beach | Edge-on from eye height: pair with the surf props. |
| `foam_glow` | polish | tropical_beach | As foam. |
| `starfish` | good | tropical_beach |  |
| `shells` | good | tropical_beach |  |
| `seaweed` | good | tropical_beach |  |
| `lily_pads` | good | jungle_temple |  |

## Skies (11)

| sky | status | used in | notes |
|---|---|---|---|
| `night` | good | ancient_ruins, chapel_graveyard, claude_study, garden_encounter, gui_menus, hospital_garden, post_presets, tropical_beach, winter_lake, woodland_night |  |
| `dusk` | good | coast_lighthouse, misty_moor |  |
| `storm` | good | coast_lighthouse, rain_alley, rainy_street | Could use darker cloud masses. |
| `day` | good | cathedral_ruin, jungle_temple, tropical_beach, winter_lake |  |
| `overcast` | good | - |  |
| `blood` | good | - |  |
| `space` | good | space_station |  |
| `alien` | good | alien_world |  |
| `dream` | good | dream_world |  |
| `sunset` | good | tropical_beach |  |
| `golden` | good | ancient_ruins |  |

## Skylines (6)

| skyline | status | used in | notes |
|---|---|---|---|
| `mountains` | good | alien_world, jungle_temple, winter_lake |  |
| `hills` | good | misty_moor |  |
| `treeline` | good | chapel_graveyard |  |
| `city` | good | - | Window grid is regular; vary building tops (spires, water towers). |
| `islands` | polish | ancient_ruins, tropical_beach | In haze an island and its reflection can read as a saucer floating on the horizon. |
| `jungle` | good | jungle_temple |  |

## Sky objects (5)

| object | status | used in | notes |
|---|---|---|---|
| `planet` | good | - |  |
| `ringed` | good | alien_world, space_station |  |
| `moon` | good | alien_world, dream_world, space_station |  |
| `sun` | good | space_station |  |
| `eye` | good | dream_world |  |

## Scatter sets (13)

Named mixes for `scatter`; repeats in the contents act as weights.

| set | status | contents | used in | notes |
|---|---|---|---|---|
| `stones` | good | rocks x3, boulder | chapel_graveyard, coast_lighthouse, misty_moor, winter_lake, woodland_night |  |
| `rubble` | good | rubble x2, rocks, broken_barrel | cathedral_ruin, rainy_street |  |
| `forest` | good | rocks x2, log, stump, mushrooms, grass_tuft x2, fern, bush | woodland_night |  |
| `undergrowth` | good | grass_tuft x3, fern, bush, mushrooms | chapel_graveyard, woodland_night |  |
| `shore` | good | rocks x3, boulder, reeds, bones | coast_lighthouse |  |
| `litter` | good | sack, bucket, crate, barrel, broken_barrel, bones | rain_alley |  |
| `wreckage` | good | rubble x2, broken_barrel, rocks, bones, sack, bucket | bunker_lab, cathedral_ruin, derelict_ship, sewer_tunnels |  |
| `cave` | good | rocks x3, stalagmite, glowshroom, crystal, bones | crystal_cave |  |
| `alien` | good | rocks x2, crystal, glowshroom, alien_plant, alien_egg | alien_world |  |
| `derelict` | good | rubble x2, sci_crate, bones, rocks, alien_egg | derelict_ship |  |
| `jungle` | good | fern x3, monstera, bromeliad x2, heliconia, mushrooms | jungle_temple |  |
| `beach` | good | coconuts, driftwood, rocks x2, crab, dry_tuft | tropical_beach |  |
| `ruins` | good | column_drum, rubble, rocks x2, poppies, dry_tuft x2, amphora | ancient_ruins |  |

## Fringe sets (1)

The cards a `fringe` wall stands in front of its open faces, back to front.

| set | status | cards | used in | notes |
|---|---|---|---|---|
| `jungle` | good | jungle_card_4, jungle_card_3, jungle_card_2, jungle_card_1 | jungle_temple | Four cards: bushes alone at the front, a dense wall of trees, crowns and bushes at the back. |

## Facade styles (3)

The looks a `facade` can give its buildings (`scripts/buildings.py`); each building is drawn in layers - wall, frames and glass, drapes, rooms.

| style | status | used in | notes |
|---|---|---|---|
| `brick` | good | rain_alley | Red and brown brick, painted sash windows, curtains and blinds, shops. |
| `sooty` | good | rain_alley | Soot-blackened tenements, dark frames. |
| `plaster` | polish | - | Washed plaster; only seen on the review sheets so far, no scene uses it. |

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
| `classic` | good | 28 scenes |  |
| `parchment` | good | gui_themes, gui_trade |  |
| `terminal` | good | bunker_lab, gui_themes, space_station |  |
| `blood` | good | gui_themes |  |
| `steel` | good | gui_themes |  |

## GUI widgets (16)

| widget | status | used in | notes |
|---|---|---|---|
| `bubble` | good | alien_world, castle_keep, claude_study, crystal_cave, garden_encounter, ghost_corridor, gui_menus, gui_trade, rainy_street, tunnel_encounter, winter_lake, woodland_night |  |
| `dialog` | good | bunker_lab, chapel_graveyard, claude_study, coast_lighthouse, ghost_corridor, library_medium, space_station |  |
| `caption` | good | 21 scenes |  |
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

## Example scenes (34)

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
| `tunnel_encounter` | good | 2 | tunnel_01 |  |
| `underground_waterway` | polish | 4 | waterway_01 | Murky: the far end and the boat are hard to read. |
| `sewer_tunnels` | good | 3 | sewer_thing |  |
| `bunker_lab` | good | 4 | bunker_hud, bunker_crt |  |

### Outdoors

| scene | status | shots | gallery | notes |
|---|---|---|---|---|
| `woodland_night` | polish | 4 | woods_path, woods_fire | Foreground logs and stumps read as brown blocks; boulders as grey teeth. |
| `coast_lighthouse` | polish | 4 | coast_tower, coast_jetty | The shore rocks in the tower shot are grey lumps. |
| `rainy_street` | good | 4 | street_rain, street_lightning |  |
| `rain_alley` | good | 4 | alley_street, alley_rain, alley_glass, alley_storm |  |
| `misty_moor` | polish | 3 | moor_dawn, moor_circle | The standing stones are plain blocks; weathered tops and lichen would help. |
| `winter_lake` | polish | 4 | winter_night, winter_day | The ice is blotchy (see the ice texture). |
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
| `alien_world` | good | 3 | alien_landing, alien_monolith |  |
| `dream_world` | good | 3 | dream_stair, dream_mirror |  |

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
| `tropical_beach` | good | 4 | beach_sunset, beach_pier, beach_day, beach_night |  |

## Pass log

- **2026-10-19, pass 0.** First full review of every asset, on review sheets and in the gallery. This file and `docs/asset_review.py` were added.
- **2026-10-19, reveals.** A card can have a `reveal` (a thickness): through its openings, seen at an angle, it draws their far sides - jamb, head, sill - folded from its own colours and lit by their own facing, with the wall's shadow in them. Facade walls use it, so a window or door seen from the pavement shows its brick sides instead of a sliver of the lit room behind.
- **2026-10-19, glass and facades.** A glass pass: panes drawn after everything else, showing what is behind them through the frame shrunk to half size and blown back up (a cheap blur), tinted light blue, under a faint reflection. Building `facade`s: a block's fronts cut into separate buildings of varied height, brick and paint, each in five layers - wall, frames, glass, drapes, rooms - so windows have depth. Rain alley rebuilt as a wider street with a road, pavements and a T-junction.
- **2026-10-19, planes, fringe and prefabs.** Sprites can stand as fixed planes in the world: one card, a cross of two or a star of three, and the low plants do so by default. A `fringe` wall stands layered foliage cards in front of its open faces (four jungle cards, sparse to dense). Prefabs place named groups - sprites, lights, decals, scatter, nested prefabs and patches of map - with one line; 13 built-ins. The jungle temple was rebuilt round the fringe; the beach and the ruins use prefabs.
- **2026-10-19, jungle, ruins and beach.** A pixel-art toolkit (`scripts/pixelart.py`: shapes in a height field, one light, hue-shifted ramps, shadow-side outlines) and `scripts/biomes.py`, drawn with it: 23 textures, 31 props (5 of them hand-drawn animals), 6 decals, 3 characters, the `sunset` and `golden` skies, the `islands` and `jungle` skylines, three scatter sets and three scenes. `palm`, `column`, `fern`, `grass_tuft` and `rocks` were redrawn the same way.

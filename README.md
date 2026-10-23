# ai-raster-scene

[![smoke](https://github.com/StevenGlick/ai-raster-scene/actions/workflows/smoke.yml/badge.svg)](https://github.com/StevenGlick/ai-raster-scene/actions/workflows/smoke.yml)

**90s game pictures from a text file.** A tiny software raycaster in Python with a Doom/Wolfenstein/Build-engine look, plus everything that makes a frame read as a real game screen: rain-soaked streets whose windows have depth behind glass, layered jungle, fog and sunbeams, reflections in wet stone and water, pixel-art characters and translucent ghosts, a full retro GUI toolkit (dialog, choice menus, HUDs, inventories, title cards) and post-processing (CRT, VHS, Game Boy, night vision, rain, film looks). It can also shrink the world so the camera is a giant's - valleys, volcanoes, deserts and a kaiju loose in the harbour - draw a road the way an 80s arcade racer drew one, and lay its shots out as comic pages.

It ships as a Claude skill and works as Claude's retro imagination: ask for a picture of a place, a moment or a game screen, and Claude builds the scene, renders it, looks at the result, iterates, then hands you the image. It also works as a plain command-line tool. It began as three concept drawings Claude made out of plain shapes - [see where it started](#where-it-started), and the same places now.

![Sunset down the sacred way, between broken columns, to the temple on the headland](docs/gallery/ruins_way.png)

*Every image on this page is rendered straight from a scene file in [`examples/`](examples/) - no hand-painted assets anywhere - but for the three drawings it [started from](#where-it-started).*

**On this page:** [What's new](#whats-new) · [Where it started](#where-it-started) · [Install](#install) · [A scene in 30 seconds](#a-scene-in-30-seconds) · [The gallery](#the-gallery) · [Landscape scale](#landscape-scale) · [Road scenes](#road-scenes) · [Comic mode](#comic-mode) · [GUI toolkit](#gui-toolkit) · [Post-processing](#post-processing) · [Features](#features) · [Materials](#materials) · [Development](#development)

## What's new

- **[Road scenes](#road-scenes)** - a second renderer: the road of an 80s arcade racer, its bends and crests drawn segment by segment, props scaled along it - a coast road at sunset behind the wheel, a highway at night through a tunnel, a forest path, a jungle trail, an enchanted wood and a road across the clouds. The same post effects, GUI and palette finish it.
- **[Where it started](#where-it-started)** - the three drawings this project grew from, made of plain shapes in a chat, beside the same three places rendered now: a storm over an island town, a garden through a broken window, a boat waiting in a canal tunnel.
- **[Landscape scale](#landscape-scale)** - shrink the world and the camera is a giant's: a kaiju wading into a harbour city at night and a giant moth coming in over the bay to meet it, a volcano erupting over an island, buttes and mesas on a red plain, a winter valley under the aurora, a suspension bridge over a sea strait, a tropical archipelago.
- **[Comic mode](#comic-mode)** - lay shots of any scenes out as a comic page or a storyboard. *It came from the bay* tells the kaiju's night in six panels.

| | |
|---|---|
| ![Behind the wheel on the coast road at sunset](docs/gallery/road_coast.png) | ![A road of marble across the clouds](docs/gallery/road_sky.png) |
| ![The giant moth comes in over the bay, the kaiju roaring up at it](docs/gallery/kaiju_moth.png) | ![A volcano erupting over a harbour town at night](docs/gallery/island_eruption.png) |
| ![Down the highway into the mesa desert at golden hour](docs/gallery/desert_road.png) | ![A village under snow, the aurora over the white peak](docs/gallery/winter_street.png) |

## Where it started

This project began with three drawings. Working on a game, its author asked Claude, in a chat, for concept art drawn from the game's design doc - and Claude, which has no image generator, drew three scenes out of plain shapes: an island town on a stormy night, a moonlit garden through a broken window, a boat waiting in a canal tunnel. Not bad for rectangles and circles, and they showed how much further a proper renderer could take the same idea. This is that renderer. Here are the three drawings beside the same three places as it draws them now, each a scene file in [`examples/`](examples/) ([`storm_island`](examples/storm_island.py), [`window_garden`](examples/window_garden.py), [`canal_tunnel`](examples/canal_tunnel.py)):

| Then: drawn with shapes, in a chat | Now: rendered from a scene file |
|---|---|
| ![The first drawing, in flat shapes: an island town at night - a hill with a house on top, tenements, a plateau of buildings, a lighthouse and its beam, lightning](docs/origins/island.png) | ![The storm island: the hill and its house over the tenements and cottages, the lighthouse sweeping the harbour, the plateau's power station struck by lightning under storm clouds](docs/gallery/storm_island.png) |
| ![The second drawing, in flat shapes: a garden by moonlight through a broken window - a statue, roses, a lamp post, a house and a tower](docs/origins/garden.png) | ![The window onto the garden: tattered curtains either side of a broken casement, glass on the floor, the robed statue in the moonlight beyond](docs/gallery/garden_window.png) |
| ![The third drawing, in flat shapes: a vaulted canal tunnel, a lamp on each wall, an iron cabinet, a sigil, a boat in the water](docs/origins/tunnel.png) | ![The canal tunnel: its arches running off into the dark under paired lamps, the cabinet, the sigil, a boat moored in the canal with a lantern at its bow](docs/gallery/canal_tunnel.png) |

And from inside them:

| | |
|---|---|
| ![The island town from the lighthouse: the tenements and cottages lit, the hill and its house against the storm](docs/gallery/storm_town.png) | ![The robed statue on its pedestal, the full moon over it and the cypresses](docs/gallery/garden_statue.png) |
| ![Aboard: the boat's bow and its lantern, the canal running on under the lamps](docs/gallery/canal_boat.png) | ![The boat at its mooring, the rope to its post, the cabinet under the lamp](docs/gallery/canal_moored.png) |

The pieces they needed - a vault's arch, a broken casement, tattered curtains, rose bushes, a robed statue, a round wall lamp, an iron cabinet, storm clouds, broken glass and a painted sigil - are their own kit, [`scripts/spooky.py`](scripts/spooky.py).

## Install

Requirements: Python 3.10+, `numpy`, `Pillow` (`pip install -r requirements.txt`).

**As a Claude skill**

```bash
git clone https://github.com/StevenGlick/ai-raster-scene
cd ai-raster-scene
python package_skill.py
```
writes `dist/ai-raster-scene.zip` (about 600 KB) containing only what the skill needs at runtime - `SKILL.md`, `scripts/`, `references/`, `examples/` and `requirements.txt`. The README gallery, tests and CI config are deliberately left out; `docs/` alone is several megabytes of PNG and is no use inside a skill.

- Claude apps: upload that zip as a custom skill in Claude's settings.
- Claude Code: clone straight into your skills folder, `git clone https://github.com/StevenGlick/ai-raster-scene ~/.claude/skills/ai-raster-scene` (or a project's `.claude/skills/`), or unzip the package there.

Then just ask, for example: *"Show me a foggy pine forest at night with a campfire and someone sitting at it."*

There are no asset files to install. Every texture, prop, character, sky and the pixel font are generated procedurally in `scripts/` - `classic.py` and a kit per world (listed in `assets.py`), `skies.py`, `buildings.py`, `characters.py` and `pixelfont.py` - which is why the whole skill is a few hundred KB of Python and renders identically everywhere.

**As a CLI**
```bash
python scripts/render.py examples/garden_encounter.json -o out.png --map --sheet
```
`--map` writes a top-down layout check, `--sheet` a contact sheet of all shots, `--shot N` renders one shot.

## A scene in 30 seconds

```json
{
  "map": ["#####",
          "#...#",
          "#...#",
          "##D##"],
  "legend": {
    "#": {"wall": "stone_dark", "h": 1},
    "D": {"wall": "iron_door", "h": 1},
    ".": {"floor": "cobble", "ceil": "rock"}
  },
  "sky": null,
  "ambient": [0.06, 0.06, 0.08],
  "lights": [{"x": 2.5, "y": 1.6, "radius": 4, "color": [1, 0.7, 0.35]}],
  "sprites": [
    {"x": 2.5, "y": 1.4, "type": "lantern", "z": 0.8},
    {"id": "c", "x": 2.5, "y": 1.9, "type": "cultist"}
  ],
  "overlays": [{"type": "bubble", "anchor": "c", "text": "You should not be here."}],
  "camera": {"x": 2.5, "y": 3.4, "angle": 270}
}
```

Rows are y (south is down), columns are x, one cell is one unit, eye height is 0.5. The full reference, including the pixel-art sprite format and every option, is in [`references/scene_format.md`](references/scene_format.md); every built-in texture, prop and character is listed in [`references/assets.md`](references/assets.md), and how to build particular places in [`references/recipes.md`](references/recipes.md). [`SKILL.md`](SKILL.md) holds the workflow and art-direction notes Claude follows.

![Layout map](docs/gallery/layout_map.png)

## The gallery

Eighty-seven example scenes in [`examples/`](examples/), every one a single JSON file you can open, change and render:

- **[Where it started](#where-it-started)** - the storm island · the window onto the garden · the canal tunnel
- **[Cities](#cities)** - [streets in the rain](#city-streets) · [the neon city](#the-neon-city) · [a night market](#the-night-market) · [a bar](#the-bar) · [the rooftops](#the-rooftops) · [a capsule hotel](#the-capsule-hotel) · [a village](#the-village) · [a frontier town](#the-frontier-town) · [a clockwork city](#the-clockwork-city)
- **[Woods and weather](#woods-and-weather)** - [the woods at night](#the-woods-at-night) · [autumn](#autumn) · [the autumn garden](#the-autumn-garden) · [winter](#winter) · [fog and light](#fog-and-light) · [the palm house](#the-palm-house) · [the bayou](#the-bayou)
- **[Jungle, desert and coast](#jungle-desert-and-coast)** - [jungle, ruins and the beach](#jungle-ruins-and-the-beach) · [the glowing jungle](#the-glowing-jungle) · [the desert](#the-desert) · [the salt flat](#the-salt-flat) · [the fjord](#the-fjord) · [the basalt coast](#the-basalt-coast) · [the lighthouse](#the-lighthouse)
- **[Underground and undersea](#underground-and-undersea)** - [the crystal cave](#the-crystal-cave) · [under the sea](#under-the-sea) · [the sunken temple](#the-sunken-temple) · [the aquarium](#the-aquarium)
- **[Haunts and old stones](#haunts-and-old-stones)** - [the haunted house](#the-haunted-house) · [the castle and the chapel](#the-castle-and-the-chapel) · [encounters](#encounters)
- **[Space and other worlds](#space-and-other-worlds)** - [stations and ships](#stations-and-ships) · [the Moon](#the-moon) · [Vector World](#vector-world) · [Doomed](#doomed)
- **[Dreams and wonders](#dreams-and-wonders)** - [dreams](#dreams) · [the drowned library](#the-drowned-library) · [the hall of doors](#the-hall-of-doors) · [the sky islands](#the-sky-islands) · [the aurora palace](#the-aurora-palace) · [ask Claude](#ask-claude)
- **[Landscape scale](#landscape-scale)** - [the kaiju in the harbour](#the-kaiju-in-the-harbour) · [the kaiju in the country](#the-kaiju-in-the-country) · [the volcano island](#the-volcano-island) · [the mesa desert](#the-mesa-desert) · [the winter valley](#the-winter-valley) · [the strait bridge](#the-strait-bridge) · [the archipelago](#the-archipelago) · [the giant valley](#the-giant-valley)
- **[Road scenes](#road-scenes)** - the coast road · the night highway · the forest path · the jungle trail · the enchanted path · the sky road
- **[Comic mode](#comic-mode)** - comics and storyboards, every panel a shot

## Cities

### City streets

Give a block of buildings a `facade` and its fronts become a row of separate buildings, each drawn in layers - brick with its openings, frames and glass, curtains and blinds, lit or dark rooms - so the windows have depth, and the wall has its thickness: from the pavement every window and door shows its sides and sill. The glass shows what is behind it, tinted and softly blurred.

| | |
|---|---|
| ![A rain-soaked city street at night, running up to a T-junction, every building different](docs/gallery/alley_street.png) | ![An officer walking away up the street under the lamps](docs/gallery/alley_rain.png) |
| ![Windows set back in their walls, curtains and rooms behind glass, a shop window blurred and tinted](docs/gallery/alley_glass.png) | ![Lightning over the junction, a lit shopfront across the street](docs/gallery/alley_storm.png) |
| ![Rainy town street](docs/gallery/street_rain.png) | ![Lightning over the street](docs/gallery/street_lightning.png) |

### The neon city

The `neon` style turns the same street to the lower city: dark concrete hung with signs, blade signs standing out over the street, shutters half down, rooms lit pink and blue, wires and lanterns overhead and the whole of it mirrored in the wet.

| | |
|---|---|
| ![A neon street at night in the rain, signs on both sides and lantern wires overhead](docs/gallery/neon_street.png) | ![A noodle stand built in 3D, its awning, curtains and lanterns, its cook at the counter](docs/gallery/neon_stall.png) |
| ![Looking up at the blade signs and the wires](docs/gallery/neon_signs.png) | ![A runner in a lit visor: walk with me](docs/gallery/neon_runner.png) |

Objects are things too big to be a billboard, built in 3D out of flat panels the way Build-engine maps built them - standing, lying and sloped, see-through wherever the thing is not - so they show the right sides from any angle: a car, parked along the kerb or coming up the street with its headlamps on, its seats seen through the glass, and the noodle stand, bowls and a stock pot on its counter as billboards.

| | |
|---|---|
| ![A car coming up the rain alley at night, its headlamps on, another parked under the lamps](docs/gallery/alley_cars.png) | ![Up at the noodle stand's counter: bowls of noodles, a stock pot steaming, the cook under the curtains](docs/gallery/neon_counter.png) |

### The night market

After dark a lane of the same city fills with a night market: food carts with their woks over the flame, fruit and gadget stalls under tarps, strings of red paper lanterns overhead, scooters, plastic stools, a crowd under umbrellas.

| | |
|---|---|
| ![A night market in the rain, strings of red lanterns down the lane](docs/gallery/market_lane.png) | ![A food cart's wok over the flame, a customer at the counter](docs/gallery/market_cart.png) |
| ![Down in the wet: the lanterns mirrored in the flagstones](docs/gallery/market_puddle.png) | ![The runner under a clear umbrella with a lit shaft: two bowls, extra chilli](docs/gallery/market_runner.png) |

### The bar

And off the market, a bar: smoke in the air, bottles glowing on their shelves, a reef tank let into the back wall, a row of arcade cabinets built in 3D, each in its own colour with its own game on the screen - one of them playing another scene, the Vector World - a screen over the bar showing the street outside, booths, a jukebox, neon on the walls.

| | |
|---|---|
| ![A neon bar in the small hours: the bar, a jukebox, a booth, smoke](docs/gallery/bar_room.png) | ![The reef tank in the bar's back wall](docs/gallery/bar_tank.png) |
| ![The arcade row, a runner at a cabinet, all of it mirrored in the floor](docs/gallery/bar_arcade.png) | ![The bartender under the screen showing the street outside: your man was in an hour ago](docs/gallery/bar_bartender.png) |
| ![A street samurai in the market, under a clear umbrella](docs/gallery/market_samurai.png) | ![A hacker in a booth: don't look at the screen, it looks back](docs/gallery/bar_hacker.png) |

### The rooftops

And up on the roofs, five storeys over the street: the canyon of signs going away below, lanterns strung across it, an elevated train crossing it, a black cat on the ledge.

| | |
|---|---|
| ![From a rooftop ledge: the neon canyon below, the runner at the edge](docs/gallery/rooftop_canyon.png) | ![Straight down past the blade signs to the lanterns and the street](docs/gallery/rooftop_down.png) |
| ![From the street: the elevated train crossing between the towers](docs/gallery/rooftop_train.png) | ![A black cat on the ledge, watching the city](docs/gallery/rooftop_cat.png) |

### The capsule hotel

And a capsule hotel at four in the morning: a corridor between two walls of berths, lamps and screens glowing behind the blinds, a sleepwalker coming down it with her candle.

| | |
|---|---|
| ![A capsule hotel corridor, berths stacked down both walls](docs/gallery/capsule_corridor.png) | ![The berths up close: lamps, blinds, a screen](docs/gallery/capsule_berths.png) |
| ![A sleepwalker with her candle between the berths](docs/gallery/capsule_sleepwalker.png) | ![The hacker at the vending machine: it only takes old coins](docs/gallery/capsule_vending.png) |

### The village

The `timber` style builds a village instead: timber-framed houses in limewash and ochre, oak posts, rails and braces, leaded casements and plank doors, and a roof on every house - a gable end over the street, or thatch or tiles with a chimney. Market stalls, crates, barrels and the well on the green are built in 3D too: the stalls' trays heaped with apples, cabbages, loaves and potatoes, the well a round wall of fieldstones under a little roof, its windlass and rope.

| | |
|---|---|
| ![Market day on a village street of timber-framed houses, the inn's sign out over it](docs/gallery/village_market.png) | ![A stallholder by a striped stall of apples and bread](docs/gallery/village_stall.png) |
| ![The well on the village green, an oak and a row of gables behind](docs/gallery/village_well.png) | ![The inn's lanterns lit after closing, a knight at the door](docs/gallery/village_night.png) |

The same street through a day, one key per shot - `"time": "dawn"`, `"morning"`, `"noon"`, `"afternoon"`, `"golden"`, `"sunset"`, `"dusk"`, `"night"` (or any hour, 17.5): the sun goes round from the east to the west and down and the moon rises after it, the sky turns, the air darkens and tints, more of the windows show a lamp, and the inn's lanterns, lights marked `"night": true`, burn from sunset on.

![The village street at eight times of day, from dawn to night](docs/gallery/village_hours.png)

### The frontier town

The `western` style raises a frontier main street: clapboard false fronts with their painted signs - saloon, bank, livery, general store - a covered boardwalk out in front, the saloon's batwing doors lit from inside.

| | |
|---|---|
| ![High noon: a cowboy alone in the dust of a frontier main street](docs/gallery/western_noon.png) | ![The saloon: the barkeep in the lamp-lit doorway](docs/gallery/western_saloon.png) |
| ![The same street at sundown, lanterns lit, a ghost in the dust](docs/gallery/western_ghost.png) | ![A windpump against the sunset where the street runs out](docs/gallery/western_windpump.png) |

Inside the saloon: flocked wallpaper over dark panels, the back bar's bottles round a tall mirror, a mahogany bar in 3D with its brass rail, round card tables of green baize with the cards dealt and the chips standing, bentwood chairs, an upright piano with its music open and candles at its corners, all in 3D - and the noon sun slanting through the front windows into the dust.

| | |
|---|---|
| ![High noon in the saloon: the sun through the front windows into dusty air, the bar and its mirror](docs/gallery/saloon_noon.png) | ![A gambler over the cards: "Read em and weep, friend."](docs/gallery/saloon_cards.png) |

![After midnight the piano plays itself: a ghost at the keys by candlelight](docs/gallery/saloon_piano.png)

| | |
|---|---|
| ![Close across the card table: the gambler, "Sit down. Cards are dealt."](docs/gallery/saloon_gambler.png) | ![Close across the bar: the bartender before his bottles](docs/gallery/saloon_barkeep.png) |

And up in the hills the gold mine: a tunnel timbered every few paces in 3D, rails running into the dark under the lanterns, a prospector at a vein of gold glinting in the rock, and the portal in the hillside at dusk.

| | |
|---|---|
| ![Into the mine: timber sets and lanterns down a tunnel, rails running into the dark](docs/gallery/mine_tunnel.png) | ![A prospector by lamplight at a seam of gold in the rock](docs/gallery/mine_vein.png) |

![The mine's portal in a hillside of red rock at dusk, the rails coming out to an ore cart](docs/gallery/mine_portal.png)

### The clockwork city

A plaza of brass and brick at sundown in a brown smog: a clock tower with a great clock and a brass spire, gears the height of houses turning in the walls, copper pipes venting steam, gaslamps, an automaton on its rounds, and in the middle an orrery - brass rings turning round a golden sun, its planets riding them, drawn as wireframes.

| | |
|---|---|
| ![The clockwork plaza at sundown: the orrery glowing before the clock tower, gears in the walls](docs/gallery/clock_plaza.png) | ![The orrery close up: brass rings round a golden sun, the clock tower behind](docs/gallery/clock_orrery.png) |
| ![Great brass gears in the walls over copper pipes, steam and an automaton](docs/gallery/clock_gears.png) | ![The clock tower and its spire over the plaza, gears in the walls, the orrery glowing](docs/gallery/clock_tower.png) |

## Woods and weather

### The woods at night

A forest road at night, running to a clearing where a fire burns: every edge of the wood is layered cards of spruce, oak, birch and undergrowth, mossy boulders lie by the road, and the moon throws the shadows of the trees across the mist - then the same wood at first light.

| | |
|---|---|
| ![A fire in the woods at night](docs/gallery/woods_fire.png) | ![Lantern on the forest road](docs/gallery/woods_path.png) |
| ![First light: a low sun through a gap in the spruce, mist lying in the clearing](docs/gallery/woods_dawn.png) | ![Something standing on the moonlit road](docs/gallery/woods_moon.png) |

### Autumn

The wood turns: oak, birch and bush gone orange, gold and rust with the spruce still green among them, leaves underfoot and falling, a field behind a dry-stone wall with a scarecrow, hay bales and pumpkins - and the gateway at dusk with the jack-o'-lanterns lit.

| | |
|---|---|
| ![A lane through an autumn wood, the low sun at its end, leaves falling, a child walking home](docs/gallery/autumn_lane.png) | ![A scarecrow in the stubble with a crow on its arm](docs/gallery/autumn_scarecrow.png) |
| ![Jack-o'-lanterns on the gateposts at dusk](docs/gallery/autumn_dusk.png) | ![The child on the lane: can we go the long way?](docs/gallery/autumn_walk.png) |

### The autumn garden

A Japanese garden in autumn: a red gate on the gravel path, stone lanterns, maples turned scarlet and gold, a pond with a plank bridge and boulders of mossy stone, a tea house under a roof of grey tiles - and at dusk, the lanterns lit along the way.

![Through the red gate: the gravel path between maples to the tea house, stone lanterns either side](docs/gallery/garden_gate.png)

| | |
|---|---|
| ![Across the pond: the bridge's red rails, a mossy boulder, a lantern, the tea house beyond](docs/gallery/garden_pond.png) | ![Dusk: the lanterns lit along the path to the tea house](docs/gallery/garden_dusk.png) |

### Winter

The wood under snow: snowy spruce and bare oaks and birches with snow along their limbs, a frozen stream mirroring them under a plank footbridge, a deer on the ice in falling snow, and the lantern on the bridge at night.

| | |
|---|---|
| ![A lane through a snowbound wood](docs/gallery/winter_lane.png) | ![A deer on the frozen stream in falling snow](docs/gallery/winter_deer.png) |
| ![A child in the snow at night, a lantern on the footbridge](docs/gallery/winter_lantern.png) | ![The frozen stream mirroring the snowy spruces](docs/gallery/winter_stream.png) |
| ![The cabin on the ice by moonlight](docs/gallery/winter_night.png) | ![The same lake by day, through shot overrides](docs/gallery/winter_day.png) |

![The cabin close by day: snow lying deep on its roof, wood smoke from the chimney](docs/gallery/winter_cabin.png)

### Fog and light

A stone circle on the moor at dawn, mist lying in the hollows and the low sun cutting through the stones; and a cathedral fallen open to the sky, sunbeams through its broken windows and dust hanging in the light.

| | |
|---|---|
| ![A stone circle at dawn, mist lying low, a knight seen from behind](docs/gallery/moor_dawn.png) | ![The low sun through the stones](docs/gallery/moor_circle.png) |
| ![A sunbeam through the fallen roof of a cathedral](docs/gallery/cathedral_beam.png) | ![A pilgrim standing in the light](docs/gallery/cathedral_pilgrim.png) |

### The palm house

A Victorian glasshouse full of palms: white cast iron and glass, the sun pouring in through the roof onto tree ferns and banana plants, a fountain under the ridge, a path of encaustic tiles.

![The palm house: palms reaching up into the glass roof, iron columns, a path of encaustic tiles to the fountain](docs/gallery/palm_path.png)

| | |
|---|---|
| ![Under the palms by the fountain, the glazing bars against the sky](docs/gallery/palm_fountain.png) | ![From the far end, back toward the door, the iron dark against the light](docs/gallery/palm_back.png) |

### The bayou

Black water under bald cypresses hung with Spanish moss, a shack on its island with a lamp in the window - at sundown, at night with the fireflies out, the eyes of something in the water, a heron in the morning mist.

| | |
|---|---|
| ![A shack on the bayou at sundown, framed by mossy cypresses, the sky in the water](docs/gallery/bayou_dusk.png) | ![The same water at night, fireflies over it, the window lit](docs/gallery/bayou_night.png) |
| ![Two eyes in the black water, the shack behind](docs/gallery/bayou_gator.png) | ![A heron in the morning mist](docs/gallery/bayou_heron.png) |

## Jungle, desert and coast

### Jungle, ruins and the beach

A stepped pyramid swallowed by the rainforest at the end of a path under the canopy; a Doric temple on a headland above the sea, at golden hour and by moonlight; a lagoon with a pier and a hut on the sand. All of it is pixel art drawn in code - leaves, stones and planks stamped into a height field and lit.

| | |
|---|---|
| ![A stepped pyramid mirrored in a long pool, giant trees standing over the canopy](docs/gallery/jungle_temple.png) | ![An explorer on the top of the pyramid, looking out over the canopy](docs/gallery/jungle_canopy.png) |
| ![A jaguar guarding the stairs up to the shrine](docs/gallery/jungle_jaguar.png) | ![The path in, under the canopy, an explorer ahead in the mist](docs/gallery/jungle_path.png) |
| ![A fallen marble head among the poppies, the colonnade behind](docs/gallery/ruins_head.png) | ![The temple by moonlight, a fire on the altar](docs/gallery/ruins_night.png) |
| ![Midday on the beach, a crab on the sand, palms and the hut along the shore](docs/gallery/beach_day.png) | ![The lagoon at sunset, a castaway at the water's edge](docs/gallery/beach_sunset.png) |
| ![The hut and the palms mirrored in the lagoon, from the end of the pier](docs/gallery/beach_pier.png) | ![Glowing surf on the beach at night, a fire on the sand](docs/gallery/beach_night.png) |

![Doric columns in 3D in the low sun: one still standing under its capital by a cypress, others snapped off, fluted marble laid in drums](docs/gallery/ruins_columns.png)

Inside the pyramid: a passage of carved glyphs, and at its heart a golden idol on its altar in a single shaft of sun through the broken roof.

| | |
|---|---|
| ![Into the temple: a passage of carved stone, an explorer ahead, light at its end](docs/gallery/temple_passage.png) | ![The idol of the jaguar on its altar in a shaft of sun between dark pillars](docs/gallery/temple_idol.png) |

![The explorer beside the idol in the light: "Steady... nobody breathe."](docs/gallery/temple_reach.png)

### The glowing jungle

A clearing in the rainforest at night where everything that grows has light in it - ferns and monsteras traced in cold blue-green, heliconias burning pink, pods glowing on curling stalks, moss aglow on the floor - round a black pool where plankton swirls in streams of light and an old stone head watches from the water's edge.

| | |
|---|---|
| ![A black pool swirling with glowing plankton, the glowing plants round it doubled in the water](docs/gallery/glow_pool.png) | ![An old stone head at the water's edge, lit green by the glow, mirrored in the pool](docs/gallery/glow_head.png) |
| ![A heliconia traced in light, its flowers burning pink, glowing pods beside it, the jungle soft behind](docs/gallery/glow_flowers.png) | ![A path into the glowing jungle between walls of light-specked leaves](docs/gallery/glow_path.png) |

### The desert

A canyon of layered sandstone, ragged at the rim, saguaros on the floor of a dry wash, the ruins of a cliff dwelling with its T-shaped doors - and a slot canyon where the sun comes down through a gap in the rock in a single beam.

| | |
|---|---|
| ![A dry wash between walls of layered red sandstone, saguaros along it](docs/gallery/canyon_wash.png) | ![A beam of sunlight falling into a slot canyon onto an explorer](docs/gallery/canyon_slot.png) |
| ![The ruins of a cliff dwelling: stone rooms, T-shaped doors, a ladder](docs/gallery/canyon_ruins.png) | ![The canyon wall glowing at sunset](docs/gallery/canyon_sunset.png) |

### The salt flat

A dry lake bed of salt after rain: a film of still water over the crust mirrors the whole sky out to the horizon, so ground and sky become one - with islands of dry crust cracked into white-rimmed plates, salt raked up into rows of mounds and heaps, a house of salt blocks, and a few things that have no business being there. The mirror is the reflections' still mode: crisp, each thing mirrored about its own foot, with no streak.

![The salt flat at sunset: a girl with a candle standing on the mirror, the sun and the mountains doubled](docs/gallery/salt_sunset.png)

| | |
|---|---|
| ![A door standing on its own in the mirror, a clock and an armchair](docs/gallery/salt_door.png) | ![Noon: rows of raked salt - mounds, heaps and clods - on a white island of cracked crust, the sky in the water](docs/gallery/salt_noon.png) |
| ![Night: the moon and every star doubled in the flat](docs/gallery/salt_night.png) | ![A whale drifting over the mirror in a pastel dream sky](docs/gallery/salt_whale.png) |

And the door can open somewhere else. A `portal` shows another scene through its opening, rendered from where the camera would stand on the far side, so it lines up as you look: here a pine wood in winter, mirrored in the flat.

![The door on the salt flat swung open on a snowy pine wood, the view mirrored in the water](docs/gallery/salt_portal.png)

### The fjord

A longship drawn up on the shingle at the head of a fjord, its striped sail set and its shields along the side, cliffs of grey stone rising sheer on both sides, another ship riding at anchor; a longhouse of logs under thatch on the grass above, smoke from its roof - by day, at dusk by the fire, and from out on the water.

![The head of the fjord: a longship on the shingle, its sail set, cliffs rising on both sides](docs/gallery/fjord_day.png)

| | |
|---|---|
| ![Dusk: the fire on the shingle lighting the longship's shields, the cliffs black against a pink sky](docs/gallery/fjord_dusk.png) | ![From the water: the longship's bow and sail, the longhouse under thatch, all mirrored in the fjord](docs/gallery/fjord_water.png) |

### The basalt coast

A causeway of basalt at sunset: hundreds of hexagonal columns packed tight, stepping down from the foot of a cliff into the sea, organ pipes of them up the cliff behind, the low sun throwing the shadow of each across the next - and someone standing out on the last of them.

![The causeway at sunset: hexagonal columns stepping down to a sea reflecting the pink sky](docs/gallery/causeway_sunset.png)

| | |
|---|---|
| ![From the water's edge: the causeway rising to a cliff of basalt organ pipes](docs/gallery/causeway_organ.png) | ![Looking down on the hexagons, the sea between them, a figure on the last](docs/gallery/causeway_hexagons.png) |

### The lighthouse

A lighthouse on its point at dusk, the sea running in under it, and the keeper out on the jetty.

| | |
|---|---|
| ![The lighthouse at dusk, its lamp lit, a red band round the white tower](docs/gallery/coast_tower.png) | ![The keeper on the jetty](docs/gallery/coast_jetty.png) |

## Underground and undersea

### The crystal cave

A great cavern under the hill: a lake of glowing water, a crystal taller than a man on the island in its middle, clusters of crystals round its walls and plants that give their own light along the shore. The crystals are built in 3D, every facet a panel of its own - and every facet bends the light through it its own way, showing its own shifted piece of the cave behind it, the colours parting at its edges, the way cut stone does.

| | |
|---|---|
| ![The lake under the hill: the great crystal on its island, doubled in the glowing water, something wading toward it](docs/gallery/crystal_cave.png) | ![The great crystal close up: each facet shows its own bent piece of the cave behind](docs/gallery/crystal_close.png) |
| ![Violet crystals on the shore, the great crystal across the water, something standing in the lake](docs/gallery/crystal_violet.png) | ![Something wading in the cave lake, reflected](docs/gallery/cave_beast.png) |

### Under the sea

A forest of giant kelp on the floor of the sea, a shoal of fish turning, the wreck of a ship and a diver in a brass helmet working round it - and the same wreck on a night dive, by flashlight, the jellyfish glowing.

| | |
|---|---|
| ![Kelp standing up through teal water, the wreck beyond](docs/gallery/sea_kelp.png) | ![A diver by the wreck, bubbles rising from the helmet](docs/gallery/sea_diver.png) |
| ![A shoal of fish among the kelp](docs/gallery/sea_shoal.png) | ![A night dive: the wreck by flashlight, jellyfish glowing](docs/gallery/sea_night.png) |

### The sunken temple

A temple of marble on the floor of the sea: fluted columns still standing on their platform under a run of architrave, others fallen in drums across the sand, coral grown over the stones, kelp swaying round it, a manta ray gliding over - and a diver at the great fallen head.

![The temple under the sea: columns standing in teal water, a manta ray gliding over, kelp all round](docs/gallery/sunken_temple.png)

| | |
|---|---|
| ![Looking up at the colonnade's architrave, kelp between the columns](docs/gallery/sunken_colonnade.png) | ![A diver at the great marble head on the sea floor](docs/gallery/sunken_head.png) |

### The aquarium

A dark hall in front of a great ocean tank, a whale shark and a manta gliding past and a diver cleaning the glass from inside; a tunnel through the water, a gallery of jellyfish and a reef at child height. The glass holds water: the fog carries on behind it, so the tank glows blue round its lamps while the air of the hall stays clear. Along the foot of the big tanks' walls stands rockwork built in 3D - overlapping rounded masses jutting out from the wall in broad faces, each its own height, their tops cut along one long wavy edge, coral growing on them - with boulders out on the sand, every face cut from one solid block of stone.

![Visitors dark against the great window, a whale shark and a manta going by, mirrored in the floor](docs/gallery/aquarium_hall.png)

| | |
|---|---|
| ![Looking up through the glass at a manta against the bright surface](docs/gallery/aquarium_manta.png) | ![The tunnel: glass down both sides, the water over the roof](docs/gallery/aquarium_tunnel.png) |
| ![Sea nettles drifting in front of the glowing blue of their tank](docs/gallery/aquarium_jellies.png) | ![The reef tank: an anemone and its clownfish, corals, an angelfish, a shoal](docs/gallery/aquarium_reef.png) |
| ![Moon jellies glowing in a dark tank](docs/gallery/aquarium_moon.png) | ![A diver behind the glass, bubbles rising, a sunbeam on the sand](docs/gallery/aquarium_diver.png) |

![Inside the ocean tank: a boulder grown with coral on the sand, a reef shark gliding past the rockwork](docs/gallery/aquarium_rockwork.png)

## Haunts and old stones

### The haunted house

Halloween night at the old house on the hill: jack-o'-lanterns on the steps and bats against the moon - and inside, the grand staircase up to the landing, the portraits, the candelabras, the clock nobody winds, and someone waiting at the top of the stairs.

| | |
|---|---|
| ![The old house on Halloween night, jack-o'-lanterns on the steps](docs/gallery/haunted_front.png) | ![The hall: a grand staircase up to a landing, a ghost at the top](docs/gallery/haunted_hall.png) |
| ![The parlour: a portrait over the fireplace, a cobweb in the corner](docs/gallery/haunted_parlour.png) | ![The ghost on the stairs: welcome home](docs/gallery/haunted_ghost.png) |

### The castle and the chapel

A castle keep with its throne on a stepped dais and a portcullis you can see through; and a chapel in its iron-fenced churchyard under the moon, stained glass over the altar inside.

| | |
|---|---|
| ![The throne room on its raised dais](docs/gallery/castle_throne.png) | ![The portcullis: a see-through wall](docs/gallery/castle_gate.png) |
| ![The churchyard under the moon, with a treeline skyline](docs/gallery/chapel_yard.png) | ![The nave: stained glass and a stepped altar](docs/gallery/chapel_nave.png) |

![The great hall from its foot: round pillars of dressed stone and timber beams framing the throne](docs/gallery/castle_hall.png)

### The glass chapel

Mid-morning in a nave of pale stone, the sun standing behind the lancets down its south wall: the light comes in through them coloured, each window's pattern laid across the floor and the pews where it falls and hanging in the dusty air as coloured shafts, a monk standing in it. Glass the sun shines through (`lancet_window`, `rose_window`, `stained_glass`) lets the light on in each pane's colour and stops it at the lead and the stone; the pews are 3D `pew` objects.

![Matins: the aisle to the altar under the rose window, a window's colours laid across the floor](docs/gallery/glass_matins.png)

| | |
|---|---|
| ![A lancet's light falling over the pews](docs/gallery/glass_beam.png) | ![A monk standing in the coloured light](docs/gallery/glass_monk.png) |

### Encounters

Ghosts, guards and things in the dark, with the GUI doing the talking.

| | |
|---|---|
| ![A security officer stops you in the garden](docs/gallery/garden_01.png) | ![Ghost, guard and cultists in the garden](docs/gallery/garden_02.png) |
| ![Ghost in the ward corridor](docs/gallery/corridor_03.png) | ![The spiritualist's offer](docs/gallery/library_medium.png) |
| ![Something in the flashlight](docs/gallery/tunnel_01.png) | ![Something in the storm drain](docs/gallery/sewer_thing.png) |
| ![Hospital garden skyline](docs/gallery/hospital_garden_01.png) | ![Underground waterway dock](docs/gallery/waterway_01.png) |

## Space and other worlds

### Stations and ships

An observation deck over a ringed planet; a derelict on emergency power with a hive grown into its hull; a shuttle bay in high orbit with its control room and its reactor; a landing site under a gas giant and the monolith waiting there.

| | |
|---|---|
| ![A ringed planet through the observation deck's glass, mirrored in the floor](docs/gallery/station_deck.png) | ![A light-strip corridor leading to the deck](docs/gallery/station_corridor.png) |
| ![A derelict ship on emergency power](docs/gallery/derelict_corridor.png) | ![Found footage from the hive](docs/gallery/derelict_hive.png) |
| ![A shuttle on its pad in an orbital hangar, robot arms at work, a ringed planet beyond the glass](docs/gallery/hangar_bay.png) | ![The pilot by the shuttle: fuel her up, we drop through the rings](docs/gallery/hangar_pilot.png) |
| ![The control room looking down the bay through its window](docs/gallery/hangar_control.png) | ![The reactor core glowing through cyan haze under red alarm lights](docs/gallery/hangar_reactor.png) |
| ![A landing site under a gas giant](docs/gallery/alien_landing.png) | ![The monolith and the one who waits by it](docs/gallery/alien_monolith.png) |

### The Moon

A colony on the grey plain: greenhouse domes glowing under their glass, habitat modules, solar arrays turned to a low sun, a rover in its tracks - and the Earth hanging in a black sky.

| | |
|---|---|
| ![Greenhouse domes on the Moon, the Earth overhead](docs/gallery/moon_base.png) | ![An astronaut by the rover, the solar arrays beyond](docs/gallery/moon_rover.png) |
| ![The lunar night: the base lit by its windows and the earthlight](docs/gallery/moon_night.png) | ![An astronaut looking up at the Earth over the domes](docs/gallery/moon_earth.png) |

### Vector World

A world drawn in lines of light on black, after the vector arcade games and computer-world films of the 80s: a city of towers ruled in neon on a grid that runs to the horizon, racers trailing ribbons of light down its avenue, a giant black core hanging over a plaza in a ring of light beams, and a striped sun going down between wireframe mountains. The shapes are wireframes - low-poly meshes projected in true 3D, black faces edged in light, mirrored in the floor - and the light is bloom, the long blue lines of an anamorphic lens through the racers' headlights, and a beacon's flare.

![Vector World: a grid running to the horizon, a black core edged in white over a ring of light beams, a tower against a striped sun](docs/gallery/vector_sunset.png)

| | |
|---|---|
| ![Racers trailing light down an avenue of neon-ruled towers toward the setting sun, headlights streaking](docs/gallery/vector_racers.png) | ![A stepped pylon edged in orange, its beacon throwing a lens flare across the frame](docs/gallery/vector_beacon.png) |
| ![The core: a giant black dodecahedron edged in white, hanging over the plaza in a ring of light beams](docs/gallery/vector_core.png) | ![A runner in a suit traced with light, in focus, the wireframe plain soft behind](docs/gallery/vector_runner.png) |

### Doomed

An homage to the first level of the 1993 shooter that named a genre: the slime pit, a walkway zigzagging across a room flooded with glowing toxic sludge, seen down the barrel of a pistol over a stone status bar - big red numbers, the arms grid, and a face in the middle that gets bloodier as health runs down. Everything in it is drawn fresh in code; the GUI template (`statusbar`, `message`, the `pistol` and `shotgun`, the `doomed` theme) works over any scene.

| | |
|---|---|
| ![The slime pit: a walkway zigzagging over glowing toxic sludge, a pistol, the status bar](docs/gallery/doomed_pit.png) | ![A shotgun going off, a fireball coming in, the face bloodied at 28%](docs/gallery/doomed_fight.png) |
| ![The slime pit from above: the walkway snaking across it](docs/gallery/doomed_overview.png) | ![The window onto the rock outside](docs/gallery/doomed_window.png) |

## Dreams and wonders

### Dreams

Islands adrift in a pastel sky over a sea of cloud, a staircase to nowhere, koi over a mirror lake; and a plain of chequered marble where a chess game was never finished, under a clock gone soft.

| | |
|---|---|
| ![A staircase to nowhere on an island floating in the sky, its rock hanging under it](docs/gallery/dream_stair.png) | ![Koi over a mirror lake](docs/gallery/dream_mirror.png) |
| ![Giant chess pieces on a plain of chequered marble under a melting clock](docs/gallery/dream_plain.png) | ![A stair out of the floor up to a door that leads nowhere](docs/gallery/dream_door.png) |
| ![A hole in the floor with the sky underneath](docs/gallery/dream_hole.png) | ![A clock gone soft, slumped over a marble plinth](docs/gallery/dream_clock.png) |

### The drowned library

A hall of books standing in still water and open to the sky: a whale drifting down it, jellyfish and lanterns hanging in the air, a reader on an island of books.

| | |
|---|---|
| ![A whale drifting down a flooded library, jellyfish and lanterns in the air](docs/gallery/library_hall.png) | ![A reader on an island of books, a desk and a candle](docs/gallery/library_reader.png) |
| ![Sunlight slanting in through the tall windows](docs/gallery/library_beams.png) | ![Low over the water: the whale, the jellyfish and their reflections](docs/gallery/library_water.png) |

### The hall of doors

A corridor that does not end: doors in every wall, storey above storey, doors in the ceiling, a few of them opening onto the sky, and a sleepwalker going on down it with her candle. Three doors stand free in the hall, and each is a portal onto another scene: the sky islands from the top of the stair, the salt flat at sunset on the floor, the kelp forest hanging in the air.

| | |
|---|---|
| ![An endless hall of doors in every colour, a sleepwalker going on down it](docs/gallery/doors_hall.png) | ![A stair rising out of the floor to a door hung in the air](docs/gallery/doors_stair.png) |
| ![A door in the wall that has opened onto the sky](docs/gallery/doors_sky.png) | ![Looking up: doors in the ceiling, koi drifting under them](docs/gallery/doors_up.png) |

![A door standing in the hall swung open on the salt flat at sunset, its light on the marble floor](docs/gallery/doors_portal.png)

### The sky islands

Meadows adrift high over a sea of cloud: a ruined ring of marble columns on the highest island, a stream running off its edge into a waterfall that turns to mist long before it reaches the clouds, roots trailing from the islands' keels of rock - solid, faceted, built in 3D - a plank bridge with rope rails across to an islet of trees, and rocks floating loose in the air.

![Golden hour: the islands and their keels of rock floating in a golden haze, the sun behind the temple](docs/gallery/isles_golden.png)

| | |
|---|---|
| ![The temple island across the gulf, its waterfall pouring into the cloud sea](docs/gallery/isles_temple.png) | ![A plank bridge with rope rails over the void to an islet of trees](docs/gallery/isles_bridge.png) |
| ![From the temple island: the bridge and the islet of trees, the cloud sea below](docs/gallery/isles_above.png) | ![The waterfall falling past the island's keel of rock, turning to mist](docs/gallery/isles_falls.png) |

### The aurora palace

A palace of ice on the shore of a frozen lake, under the aurora: curtains of green light hanging across the arctic night, doubled in the ice. Towers of blue ice blocks crowned with crystal spires, icicles along the walls, a courtyard, and an open hall walled in frost round a throne cut from the ice.

| | |
|---|---|
| ![The ice palace across the frozen lake, the aurora over it and doubled in the ice](docs/gallery/aurora_lake.png) | ![The gate between two towers of ice, the aurora glowing over the courtyard](docs/gallery/aurora_gate.png) |
| ![A throne of ice in a hall walled in frost, the queen beside it, the aurora overhead](docs/gallery/aurora_throne.png) | ![The palace across the frozen lake from its western shore, the aurora over its spires and doubled in the ice](docs/gallery/aurora_shore.png) |

### Ask Claude

Asked what it would look like and where it would want to be, Claude picked a small figure whose head is a paper lantern lit from inside, in a coat the colour of fired clay, carrying an open book. It picked a round reading room at the top of a tower, above a sea of cloud. The shelves are there because it was made from an enormous amount of human writing, the fire because conversations go better somewhere warm, and the open balcony because the questions that stay interesting are the open ones. The avatar is the `claude` character, and [`examples/claude_study.py`](examples/claude_study.py) has ready-made shots for answering a question in a picture.

| | |
|---|---|
| ![Claude's avatar in its reading room, answering](docs/gallery/claude_ask.png) | ![On the balcony above the clouds](docs/gallery/claude_balcony.png) |

## Landscape scale

Shrink the world and the camera is a giant's: a map cell is about 100 m, the eye at 0.5 is fifty metres up, and a giant monster 0.62 tall stands in a city the way a person stands in a room. The renderer is the same; the city's streets, its harbour and the fields are textures drawn as seen from the air, and the towers, villages and mountains are objects built small.

### The kaiju in the harbour

A city at night, and something enormous wading in from the bay. Every block is a `city_block` object, its towers drawn floor by floor with their windows lit; searchlights swing across the sky from the rooftops, helicopters hold the monster in their lamps, tanks fire up at it from the quay and the waterfront burns. From the air its breath cuts into downtown; a giant moth comes in over the bay to meet it; the next day, at golden hour, it comes ashore.

![The giant moth comes in over the bay, the kaiju roaring up at it under the searchlights](docs/gallery/kaiju_moth.png)

| | |
|---|---|
| ![Something in the harbour: the kaiju wading in under the searchlights](docs/gallery/kaiju_bay.png) | ![From the quay, behind the tanks](docs/gallery/kaiju_quay.png) |
| ![From the air: its breath cuts into downtown](docs/gallery/kaiju_breath.png) | ![Eye to eye from a helicopter: its breath streams toward downtown](docs/gallery/kaiju_close.png) |
| ![The next day: ashore among the warehouses at golden hour](docs/gallery/kaiju_ashore.png) | |

### The kaiju in the country

An afternoon on the plain: a patchwork of fields and woods, country roads meeting at a market town, a line of pylons marching across with their cables slung from arm to arm - and the kaiju walking in beside it, a pylon nearly its own height, jets over it and a wood burning where it has been.

| | |
|---|---|
| ![From the edge of town: the kaiju beyond the power line](docs/gallery/country_town.png) | ![From a helicopter at its shoulder](docs/gallery/country_stride.png) |
| ![At the foot of a pylon, looking up](docs/gallery/country_pylon.png) | ![Golden hour, through a long lens over the town](docs/gallery/country_evening.png) |

### The volcano island

A volcano erupting over a harbour town at night: lava fountaining over the crater's rim and running down its flanks, a river of it reaching the sea in steam, an ash column towering over it lit from below. The volcano is a `mountain` of volcanic rock with a `crater` and `lava`.

| | |
|---|---|
| ![From the sea: the eruption mirrored in the water](docs/gallery/island_eruption.png) | ![From the quay of the harbour town](docs/gallery/island_town.png) |
| ![From the air, over the old lava field](docs/gallery/island_above.png) | ![A boat off the lava delta, steam where the river meets the sea](docs/gallery/island_delta.png) |

### The mesa desert

Buttes, spires and long mesas standing out of a red plain, a highway running straight at them. Each is a `mountain` with a `cliff` - a slope of talus up to sheer walls and a flat top - casting its shadow across the desert in the low sun.

| | |
|---|---|
| ![Down the highway at golden hour](docs/gallery/desert_road.png) | ![From the air: the monuments' long shadows](docs/gallery/desert_above.png) |
| ![The buttes against the sunset](docs/gallery/desert_sunset.png) | ![The road by moonlight](docs/gallery/desert_moon.png) |

### The winter valley

A frozen lake and a village under snow at night, its windows lit, white mountains all round and the aurora over them - and the morning after.

| | |
|---|---|
| ![Across the frozen lake, the aurora over the valley](docs/gallery/winter_lake.png) | ![The village on the ice's shore, its lamps lit](docs/gallery/winter_village.png) |
| ![From the village street to the white peak](docs/gallery/winter_street.png) | ![The morning after](docs/gallery/winter_morning.png) |

### The strait bridge

A suspension bridge across a sea strait, two hundred metres tall at its towers, a town where it comes ashore, a cargo ship, a ferry and sailboats going by under it - a `bridge` object, its main cables slung over its towers and its lamps lit at dusk. And one night the kaiju comes up the strait to it.

![The kaiju rising under the bridge at night, its plates glowing in the water](docs/gallery/strait_kaiju.png)

| | |
|---|---|
| ![Golden hour on the strait, a cargo ship under the bridge](docs/gallery/strait_golden.png) | ![From the water by the town quay](docs/gallery/strait_quay.png) |
| ![From the air](docs/gallery/strait_above.png) | ![Dusk, the bridge's lamps lit](docs/gallery/strait_dusk.png) |

### The archipelago

Tropical islands in a blue sea: a high island with a jungle hill and a village of thatch on its shore, a smaller one beside it, a low atoll round its own lagoon - every one fringed with white sand and palms and ringed with reef in turquoise shallows.

| | |
|---|---|
| ![From a boat, the high island across the blue](docs/gallery/archipelago_boat.png) | ![From the air: reefs and lagoons](docs/gallery/archipelago_above.png) |
| ![From the atoll's beach across its lagoon](docs/gallery/archipelago_atoll.png) | ![Golden hour](docs/gallery/archipelago_golden.png) |

### The giant valley

A river valley at dawn as a giant would see it: the river winding through water meadows and a patchwork of fields, woods and then pines up the flanks, snow-capped `mountain`s down both sides and a great peak at the valley's head, a `village` with its church by the water, mist lying along the valley floor.

| | |
|---|---|
| ![Dawn: up the valley to the great peak, mist on the valley floor](docs/gallery/valley_dawn.png) | ![The village and its church by the river](docs/gallery/valley_village.png) |
| ![From the air, down the whole valley](docs/gallery/valley_above.png) | ![The same view in the afternoon](docs/gallery/valley_afternoon.png) |

## Road scenes

The road of an 80s arcade racer, as a second renderer: a scene with a `road` instead of a `map` is a run of short segments, each bending and rising a little from the last, projected onto the screen from the camera outward, so a crest hides what lies beyond it; every few segments the road and the ground shift a shade - the bands that read as speed - and the props along it are scaled by distance and hidden behind the crests in front of them. The sky, the light, the post effects, the GUI and the palette are the same as every other picture's. It is not only for racing: any way stretching ahead - a path through a wood, a trail into the jungle, a road across the clouds.

![The coast road at sunset, from behind the wheel: palms, a chequered checkpoint over the road, the sea beside it, the time and the score over it all](docs/gallery/road_coast.png)

| | |
|---|---|
| ![Under the checkpoint, the world leaning into the bend and the car level](docs/gallery/road_checkpoint.png) | ![A highway at night under sodium lamps, tail lights ahead, a tunnel in the hill](docs/gallery/road_night.png) |
| ![In the tunnel, its lamps in a line down its roof, the city at the far end](docs/gallery/road_tunnel.png) | ![A forest path on a misty morning, someone walking it ahead](docs/gallery/road_forest.png) |
| ![A jungle trail toward a ruined arch, an explorer ahead](docs/gallery/road_jungle.png) | ![A cobbled path through a glowing wood under two moons, a witch with her lantern](docs/gallery/road_enchanted.png) |
| ![A road of marble across a sea of cloud, arches over it, a sky whale beside it](docs/gallery/road_sky.png) | |

## Comic mode

Shots of any scenes laid out on one page, each panel rendered at its own size and shape: a comic page with caption
boxes, the shots' speech bubbles and a sound in big letters, or a storyboard with numbered panels and a note under
each. A page is a JSON file of rows of panels ([`examples/pages/`](examples/pages/)), and
`python scripts/pages.py page.json -o page.png` lays it out.

![It came from the bay: a comic page - the kaiju comes in from the bay, the army on the quay, its breath, and something comes in over the water to meet it](docs/gallery/page_kaiju.png)

![A comic page: the door on the salt flat, and through it, winter](docs/gallery/page_door.png)

![A storyboard: the frontier town's saloon in six numbered panels, a note under each](docs/gallery/page_saloon.png)

## GUI toolkit

Speech bubbles anchored over characters, dialog panels, choice menus, HUDs, inventories and title cards, drawn in a hand-made pixel font over any shot.

![Survival-horror HUD](docs/gallery/gui_hud.png)

| | |
|---|---|
| ![Choice menu with the security officer](docs/gallery/gui_menus_01.png) | ![Trading with the spiritualist, parchment theme](docs/gallery/gui_trade_01.png) |
| ![Inventory over a paused game](docs/gallery/gui_trade_02.png) | ![Held lantern, interaction prompt and objectives](docs/gallery/gui_lantern.png) |
| ![Bunker laboratory HUD](docs/gallery/bunker_hud.png) | ![Objectives on a green CRT](docs/gallery/bunker_crt.png) |

![Title card with the cinematic preset](docs/gallery/gui_menus_02.png)

![The five GUI themes](docs/gallery/gui_themes.png)

```json
"overlays": [
  {"type": "bubble", "anchor": "guard", "name": "Security Officer", "text": "Password. Now."},
  {"type": "choice", "at": "bottom-right", "prompt": "What do you do?", "pointer": "hand", "selected": 0,
   "options": [{"text": "Show the scrawled note", "hint": "note"}, "Claim you're staff",
               {"text": "Bribe him", "hint": "2 idols", "disabled": true}]}
]
```

## Post-processing

One frame, twelve looks: none, crt, vhs, gameboy, nightvision, old_photo, storm + lightning, ega, cinematic, horror, dream, bloodmoon.

![Post-processing presets](docs/gallery/post_presets.png)

```json
"post": ["storm", {"fx": "lightning", "x": 0.7}, "crt"]
```

Bloom can come from light sources alone, so neon glows hard and walls stay walls, and depth of field puts the subject in focus and melts the street behind it into soft light.

| | |
|---|---|
| ![A street samurai in focus under a clear umbrella, the market behind melted into soft neon](docs/gallery/market_samurai.png) | ![A black cat on a ledge in focus, the neon canyon below blurred into glowing shapes](docs/gallery/rooftop_cat.png) |

Streaks draw the brightest lights out into the little cross of a star filter, or the long blue lines of an anamorphic lens, and a low sun in the frame throws a flare across it: a string of coloured ghosts through the middle of the frame, gone the moment a wall or a tree hides the sun.

| | |
|---|---|
| ![Into the sun on the beach: a six-pointed star on it, a lens flare of coloured ghosts across the frame, a palm on the left](docs/gallery/beach_flare.png) | ![The strings of bulbs over a neon street twinkle with little crosses of light in the rain](docs/gallery/neon_signs.png) |

## Features

- **2.5D raycaster** with multi-hit rays: walls of any height, so towers rise over hedges; per-storey wall textures for building facades; low blocks with real tops for steps, daises and altars
- **See-through walls**: iron fences, railings, picket fences, chain-link, jail bars, portcullises, lattices, smashed windows, Doric colonnades and a temple's roof comb, with the scene showing through the gaps
- **Floors, ceilings and open sky** per cell, with thirteen procedural sky panoramas (night, dusk, storm, day, overcast, blood, sunset, golden hour, deep space, alien, dream, vector, aurora), distant skylines (mountains, hills, treeline, city, islands, rainforest), and planets, ringed gas giants, moons and stranger things hung in the sky
- **Void floors**: no ground at all, just sky carrying on below the horizon, for space outside a station's viewport or islands adrift over a sea of cloud with ragged cliffs underneath
- **Lighting**: coloured point lights baked into a shadowed lightmap, fading above their own height (a lamp hung high lights the walls round it, one on a roof lights the roof), a sun or moon with long cast shadows and its disc in the sky, emissive texels (lit windows, stained glass, glowing runes), flashlight cone, Doom-style light banding, and a soft contact shadow under every prop
- **Volumetric fog**: mist that lies low and drifts in banks, halos round every lamp, and beams of sun or moonlight through windows, doorways, standing stones and trees; sunlight finds its way into roofed rooms through their doorways, windows and skylights
- **Reflections**: water, ice, wet streets and puddles mirror the lamps, windows and figures beyond them
- **The 90s look**: 320x200 framebuffer, Bayer-dithered 256-colour palette, chunky nearest-neighbour upscale, optional scanlines and 2x supersampling
- **Sprites**: 345 procedural props - scenery, light fixtures, wall decorations, castle furnishings, jungle plants, classical ruins, beach gear, sci-fi gear, alien flora, dream objects, animals, debris and vegetation - a 33-character pixel-art cast, each with a back view for over-the-shoulder shots, any PNG, or new pixel art written as text grids right in the scene
- **Planar sprites**: a plant can stand as fixed planes in the world instead of a billboard - a cross of two, or a star of three that cuts the ground round it into sixths - so it has body as the camera moves; the low plants do by default, and a prefab can mix billboards and planes (a billboard palm trunk under a star of fronds)
- **Layered forest edges**: give the walls of a jungle or a wood a `fringe` and every face that looks onto open ground gets long cards of plants standing in front of it, sparse bushes at the front to a dense wall of trunks and crowns at the back, so the edge of the forest has real depth; with `wander` the layers follow a natural, rounded line instead of the grid's square corners
- **City streets with depth**: give a block of buildings a `facade` and its fronts become separate buildings - different heights, brick, paint and windows - each drawn in layers: the wall, then frames and glass set back in it, curtains and blinds behind, and lit or dark rooms behind those, so the windows have real depth as the camera moves; the wall has its thickness, so from an angle every window and door shows its brick sides, lintel and sill
- **Glass**: a pass of its own after everything else, showing what is behind each pane tinted and softly blurred - the frame shrunk to half size and blown back up without smoothing - under a faint reflection
- **Objects**: things bigger than a prop - a `car`, a `noodle_stand`, a `rock_wall` of overlapping rounded pieces along a wall's foot, a `boulder`, a `column` of stone or wood and a `beam` to lay across them, a `trough`, a `shed_roof` and a `gable_roof` of weathered boards (or thatch, or clay tiles, with a chimney), a `market_stand` with its goods heaped in 3D, `crate`s and `barrel`s, a village `well`, a `saloon_bar` with `card_table`s, `saloon_chair`s and a `piano`, `arcade_cabinet`s and a `vending_machine`, a `portal` that opens onto another scene and a `screen` that shows one, `rails` and an `ore_cart`, a `keel` of rock to hang under a floating island, a `chess_piece` turned in polished marble, a wrecked `ship_hull`, a `longship` under sail, a `lighthouse` with its lamp lit, a `stone_lantern`, a `standing_stone` (that, like any object, can cast the sun's shadow), a `gear` of brass, a `heap` of salt, a roof of `glass` between iron glazing bars, a `crystal_cluster` whose every facet bends the light through it, and at landscape scale `tower`s and `city_block`s, a `village`, `mountain`s, a `searchlight`, a `ray` of light, a `cable` and a `bridge` - built in 3D out of flat panels at any angle, see-through wherever the thing is not, with glass to see inside and billboards among them for the small things; drawn in true perspective, depth-tested per pixel and lit like walls; rock is cut from one solid block of stone, so it runs on round a corner (`scripts/objects.py`)
- **Landscape scale**: shrink the world - a map cell about 100 m - and the camera is a giant's: city streets, a harbour, farmland and woods drawn as seen from the air, towers, villages and mountains built small, and a kaiju standing in a city as a person stands in a room
- **Pictures within pictures**: a `portal` - a door, an arch - opens onto another scene, or another part of this one: the view through it is rendered from where the camera would stand beyond its exit, so it lines up as the camera moves; a `screen` shows another shot on a television, a monitor or a wall, or on an arcade cabinet's screen
- **Lettering**: any words in the world as pixel art - a painted shop board, neon tubes, a brass plaque, letters cut in stone, chalk on a blackboard, gilt, a poster - on a `sign` object in 3D, or as a sprite or a decal of your own
- **Road scenes**: a second renderer for roads and paths - the arcade racer's road of segments, bends and rises, crests that hide what lies beyond, the bands, lanes and kerbs, the ground in bands (sand, then the sea; or none, the sky below), props along it by spacing or by density, your own car ahead of the camera with its headlights, tunnels, and a roll into the bends
- **Comic mode (pages)**: comic pages and storyboards, every panel a shot of any scene at its own shape, with captions, speech bubbles, sound effects and notes
- **Wireframes**: low-poly meshes - cubes, pyramids, polyhedra, mountains, racers, palms, or your own vertices - drawn as lines of light in true 3D, one pixel wide at any distance, hidden behind what is nearer and mirrored in wet floors; solid ones are black faces edged in light
- **Prefabs**: named groups placed with one line - a campsite with its light, a palm grove, a beach hut with its walls, door, window, roof and torches - turned, scaled and varied by seed; scenes can define their own
- **Procedural scatter**: declare debris by set, density and size class and the loader expands it into hundreds of placed props, clumped by a noise field so it drifts and leaves bare patches instead of spreading evenly - and never piles up on a camera or in front of a speaker
- **One grime dial**: raises surface variation, debris density and wall/floor wear together
- **Surface variation**: a world-space noise field breaks up texture tiling on walls, floors and ceilings - anchored to the world, so it stays put as the camera moves instead of crawling like film grain, and scaled per material so plaster stays subtle while cobble and rust vary hard
- **Decals**: 29 stamps (puddles, stains, splatter, vines, moss, cracks, scorch, leaks, cobwebs, glowing runes, surf foam, shells, starfish, lily pads, landing-pad markings, hazard stripes, wanted posters, broken glass, a painted sigil, contact shadows) blended into any floor, wall or ceiling, so surfaces get dirty without new textures
- **Sunken floors**: water cells sit below their banks, with the submerged edge shaded and sprites floating on the surface
- **Translucency**: opacity, additive blending, soft auras and wobbling tails for ghosts, spirits and magic; translucent sprites render after opaque ones without writing depth
- **GUI toolkit** in a hand-drawn pixel font: speech bubbles anchored over characters, dialog panels with portraits, choice menus with pointers and costs, title cards, objective panels, pickup toasts, interaction prompts, health bars, ammo counters, hotbars, inventories, crosshair, compass and a Doom-style automap traced from the level; a 1993 shooter's stone status bar with a face that bloodies as health falls; six themes (classic, parchment, terminal, blood, steel, doomed)
- **First-person held items**: revolver, lantern, flashlight, axe, crowbar, torch, lit by the scene; the lantern and torch cast their own light
- **24 item icons** and a draw-op format (with automatic outlines) for new icons and held items
- **Weather**: rain, snow, splashes, ash, embers, autumn leaves, fireflies, glowing spores and blowing dust, placed in the world rather than painted over it - hidden behind walls, kept out from under roofs, shrinking and fading into the fog with distance - plus wet ground that mirrors the lamps
- **Post-processing**: colour grading, bloom (from the whole frame, or only from what gives off light - neon, windows, flames, fireflies, a held lantern, the sun - so it can glow hard), depth of field that focuses on the shot's subject and leaves its colours alone, streaks (the twinkle of a star filter on the brightest lights, or the long blue lines of an anamorphic lens), a lens flare from a sun in the frame, vignette, grain, lightning, letterbox, damage flash, fade, pixelate, posterize, gradient maps, retro palettes (Game Boy, CGA, EGA, amber, phosphor, sepia...), CRT curvature and shadow mask, VHS chroma bleed and tracking, chromatic aberration; 20 one-word presets
- **Authoring tools**: a render report after every shot (too dark, blown out, a hidden or tiny subject, a wall in the lens, a camera inside a wall - each with a fix), `look_at` camera aiming, top-down layout maps with camera cones, contact sheets, a material catalog, and `maptools.Grid` for building maps in Python
- **Pixel art drawn in code**: the jungle, ruins and beach are built from shapes - leaves, stones, planks, blades of grass, carved glyphs - stamped into a height field, lit from one direction, and snapped onto hue-shifted colour ramps with dark edges on their shadow sides (`scripts/pixelart.py`), so they read as pixel art rather than noise. The held items go a step further: each is a small 3D model - capsules for finger bones, cylinders and boxes for a revolver - posed in a hand, rendered from the player's eye and painted onto the same ramps with an outline (`scripts/sculpt.py`), so the perspective is right: the barrel runs away into the view and you see the back of your own hand
- **No assets to download**: all 239 textures, 326 props, 33 characters, 27 decals, the skies and the font are generated in code, so the whole thing is a few hundred KB of Python

![Character cast](docs/gallery/cast.png)

## Materials

![Texture and sprite catalog](docs/gallery/catalog.png)

Regenerate with `python scripts/assets.py catalog.png`. Any texture slot also takes a PNG path or a tinted variant: `{"base": "brick", "tint": [0.8, 0.9, 1.2]}`.

## Limits

It is a 2.5D raycaster: one ground floor (plus shallow sunken cells for water, and low blocks for steps and daises you look down onto), one ceiling height per scene, grid-aligned block walls, camera-facing sprites with a front and a back but no side view, no slopes or walkable upper floors. Reflections are screen-space and on floors only; sun and moon shadows come from walls, not sprites. In-frame text uses a pixel font covering printable ASCII; accented letters are drawn without their accents.

## Roadmap

- Sectors with variable floor and ceiling heights (Build-engine style) for slopes, cliffs and floors you can stand on
- Directional sprites (front, side, back)
- Thin walls, doors and windows inside cells; sprites casting sun and moon shadows
- More settings, characters and materials

## Development

```bash
python tests/smoke_test.py
```
renders every example plus stress scenes that exercise every widget, theme, held item, effect, preset and palette, checks no frame comes out blank, runs regression checks for past bugs, and checks the docs still match the code (asset lists, counts, scene keys, gallery links, the asset inventory). CI runs it on Python 3.10 and 3.13 on every push.

```bash
python docs/build_gallery.py
```
regenerates every image on this page from the example scenes. The gallery is never edited by hand: each picture is declared with the scene and shot it comes from, so after changing the engine or an example, one command brings the README up to date.

```bash
python docs/asset_review.py sheets
```
renders review sheets of every texture, prop, character, decal, sky and icon into `renders/sheets`. [docs/ASSETS.md](docs/ASSETS.md) is the working list for improving them: each asset's status, what is wrong with it, and which examples use it. `python docs/asset_review.py sync` keeps its rows and usage columns in step with the code.

## License

MIT, see [LICENSE](LICENSE). Built in collaboration with Claude (Anthropic).

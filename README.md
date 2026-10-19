# ai-raster-scene

[![smoke](https://github.com/StevenGlick/ai-raster-scene/actions/workflows/smoke.yml/badge.svg)](https://github.com/StevenGlick/ai-raster-scene/actions/workflows/smoke.yml)

**90s game pictures from a text file.** A tiny software raycaster in Python with a Doom/Wolfenstein/Build-engine look, plus everything that makes a frame read as a real game screen: pixel-art characters, translucent ghosts, a full retro GUI toolkit (dialog, choice menus, HUDs, inventories, title cards) and post-processing (CRT, VHS, Game Boy, night vision, rain, film looks).

It ships as a Claude skill and works as Claude's retro imagination: ask for a picture of a place, a moment or a game screen, and Claude builds the scene, renders it, looks at the result, iterates, then hands you the image. It also works as a plain command-line tool.

![A security officer stops you in the garden](docs/gallery/garden_01.png)

| | |
|---|---|
| ![Ghost in the ward corridor](docs/gallery/corridor_03.png) | ![The spiritualist's offer](docs/gallery/library_medium.png) |
| ![Something in the flashlight](docs/gallery/tunnel_01.png) | ![Ghost, guard and cultists in the garden](docs/gallery/garden_02.png) |
| ![Hospital garden skyline](docs/gallery/hospital_garden_01.png) | ![Underground waterway dock](docs/gallery/waterway_01.png) |

*Every image on this page is rendered straight from a scene file in [`examples/`](examples/) - no hand-painted assets anywhere.*

## Settings

Interiors, streets, woodland and coast, all from the same renderer and the same built-in materials.

| | |
|---|---|
| ![A fire in the woods at night](docs/gallery/woods_fire.png) | ![Lantern on the forest road](docs/gallery/woods_path.png) |
| ![Rainy town street](docs/gallery/street_rain.png) | ![Lightning over the street](docs/gallery/street_lightning.png) |
| ![The lighthouse at dusk](docs/gallery/coast_tower.png) | ![The keeper on the jetty](docs/gallery/coast_jetty.png) |
| ![Bunker laboratory HUD](docs/gallery/bunker_hud.png) | ![Objectives on a green CRT](docs/gallery/bunker_crt.png) |

## Features

- **2.5D raycaster** with multi-hit rays: walls of any height, so towers rise over hedges; per-storey wall textures for building facades
- **Floors, ceilings and open sky** per cell, with six procedural sky panoramas (night, dusk, storm, day, overcast, blood)
- **Lighting**: coloured point lights baked into a shadowed lightmap, emissive texels (lit windows, glowing runes), flashlight cone, exponential fog, Doom-style light banding
- **The 90s look**: 320x200 framebuffer, Bayer-dithered 256-colour palette, chunky nearest-neighbour upscale, optional scanlines and 2x supersampling
- **Sprites**: 46 procedural props - scenery, light fixtures, wall decorations, debris and vegetation - a 7-character pixel-art cast, any PNG, or new pixel art written as text grids right in the scene
- **Procedural scatter**: declare debris by set, density and size class and the loader expands it into hundreds of placed props, clumped by a noise field so it drifts and leaves bare patches instead of spreading evenly - and never piles up on a camera or in front of a speaker
- **One grime dial**: raises surface variation, debris density and wall/floor wear together
- **Surface variation**: a world-space noise field breaks up texture tiling on walls, floors and ceilings - anchored to the world, so it stays put as the camera moves instead of crawling like film grain, and scaled per material so plaster stays subtle while cobble and rust vary hard
- **Decals**: 15 stamps (puddles, stains, splatter, vines, moss, cracks, scorch, leaks, cobwebs, glowing runes) blended into any floor, wall or ceiling, so surfaces get dirty without new textures
- **Sunken floors**: water cells sit below their banks, with the submerged edge shaded and sprites floating on the surface
- **Translucency**: opacity, additive blending, soft auras and wobbling tails for ghosts, spirits and magic; translucent sprites render after opaque ones without writing depth
- **GUI toolkit** in a hand-drawn pixel font: speech bubbles anchored over characters, dialog panels with portraits, choice menus with pointers and costs, title cards, objective panels, pickup toasts, interaction prompts, health bars, ammo counters, hotbars, inventories, crosshair, compass and a Doom-style automap traced from the level; five themes (classic, parchment, terminal, blood, steel)
- **First-person held items**: revolver, lantern, flashlight, axe, crowbar, torch, lit by the scene; the lantern and torch cast their own light
- **24 item icons** and a draw-op format (with automatic outlines) for new icons and held items
- **Post-processing**: colour grading, bloom, vignette, grain, rain, snow, lightning, letterbox, damage flash, fade, pixelate, posterize, gradient maps, retro palettes (Game Boy, CGA, EGA, amber, phosphor, sepia...), CRT curvature and shadow mask, VHS chroma bleed and tracking, chromatic aberration; 16 one-word presets
- **Authoring tools**: top-down layout maps with camera cones, contact sheets, a material catalog, and `maptools.Grid` for building maps in Python
- **No assets to download**: all 142+ textures, props, skies, characters and the font are generated in code, so the whole thing is a few hundred KB of Python

![Character cast](docs/gallery/cast.png)

## GUI toolkit

![Survival-horror HUD](docs/gallery/gui_hud.png)

| | |
|---|---|
| ![Choice menu with the security officer](docs/gallery/gui_menus_01.png) | ![Trading with the spiritualist, parchment theme](docs/gallery/gui_trade_01.png) |
| ![Inventory over a paused game](docs/gallery/gui_trade_02.png) | ![Held lantern, interaction prompt and objectives](docs/gallery/gui_lantern.png) |

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

## Install

Requirements: Python 3.9+, `numpy`, `Pillow` (`pip install -r requirements.txt`).

**As a Claude skill**

```bash
git clone https://github.com/StevenGlick/ai-raster-scene
cd ai-raster-scene
python package_skill.py
```
writes `dist/ai-raster-scene.zip` (about 100 KB) containing only what the skill needs at runtime - `SKILL.md`, `scripts/`, `references/`, `examples/` and `requirements.txt`. The README gallery, tests and CI config are deliberately left out; `docs/` alone is several megabytes of PNG and is no use inside a skill.

- Claude apps: upload that zip as a custom skill in Claude's settings.
- Claude Code: clone straight into your skills folder, `git clone https://github.com/StevenGlick/ai-raster-scene ~/.claude/skills/ai-raster-scene` (or a project's `.claude/skills/`), or unzip the package there.

Then just ask, for example: *"Show me a foggy pine forest at night with a campfire and someone sitting at it."*

There are no asset files to install. Every texture, prop, character and the pixel font are generated procedurally in `scripts/assets.py`, `characters.py` and `pixelfont.py`, which is why the whole skill is a few hundred KB of Python and renders identically everywhere.

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

Rows are y (south is down), columns are x, one cell is one unit, eye height is 0.5. The full reference, including the pixel-art sprite format and every option, is in [`references/scene_format.md`](references/scene_format.md). [`SKILL.md`](SKILL.md) holds the workflow and art-direction notes Claude follows.

![Layout map](docs/gallery/layout_map.png)

## Materials

![Texture and sprite catalog](docs/gallery/catalog.png)

Regenerate with `python scripts/assets.py catalog.png`. Any texture slot also takes a PNG path or a tinted variant: `{"base": "brick", "tint": [0.8, 0.9, 1.2]}`.

## Limits

It is a 2.5D raycaster: one floor plane (plus shallow sunken cells for water), one ceiling height per scene, grid-aligned block walls, camera-facing sprites with one view each, no slopes, stairs or reflections. In-frame text uses a pixel font covering printable ASCII; accented letters are drawn without their accents.

## Roadmap

- Sectors with variable floor and ceiling heights (Build-engine style) for cliffs, stairs and raised platforms
- Directional sprites (front, side, back) and animated GIF walkthroughs along a camera path, with animated post effects
- Thin walls, doors and windows inside cells; sprite shadows
- More characters, creatures and material packs

## Development

```bash
python tests/smoke_test.py
```
renders every example plus stress scenes that exercise every widget, theme, held item, effect, preset and palette, checks no frame comes out blank, runs regression checks for past bugs, and checks the docs still match the code (asset lists, counts, scene keys, gallery links). CI runs it on Python 3.9 and 3.13 on every push.

```bash
python docs/build_gallery.py
```
regenerates every image on this page from the example scenes. The gallery is never edited by hand: each picture is declared with the scene and shot it comes from, so after changing the engine or an example, one command brings the README up to date.

## License

MIT, see [LICENSE](LICENSE). Built in collaboration with Claude (Anthropic).

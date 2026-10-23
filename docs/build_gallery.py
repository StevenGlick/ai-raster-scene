"""Rebuild every image in docs/gallery from the example scenes.

    python docs/build_gallery.py               # everything
    python docs/build_gallery.py woods_fire    # just the named images
    python docs/build_gallery.py --check       # list stale or unmanaged files, render nothing

The gallery is generated, never hand-edited. Each image below names the example scene and shot
it comes from, so after a change to the engine or an example the whole gallery is one command
from current - and a caption or character name that changed in a scene cannot survive in an old
picture. Files in docs/gallery that this script does not build are reported (or removed with
--prune), because an image nobody regenerates is an image that silently goes stale.
"""
import argparse
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import assets  # noqa: E402
import render  # noqa: E402
from characters import CHARACTERS  # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'gallery')
EXAMPLES = os.path.join(ROOT, 'examples')

# gallery image -> (example scene, shot number counted from 1)
SHOTS = {
    'garden_01': ('garden_encounter', 1),
    'garden_02': ('garden_encounter', 2),
    'corridor_03': ('ghost_corridor', 3),
    'library_medium': ('library_medium', 1),
    'tunnel_01': ('tunnel_encounter', 1),
    'hospital_garden_01': ('hospital_garden', 1),
    'waterway_01': ('underground_waterway', 1),
    'woods_path': ('woodland_night', 1),
    'woods_fire': ('woodland_night', 2),
    'woods_dawn': ('woodland_night', 5),
    'woods_moon': ('woodland_night', 6),
    'autumn_lane': ('autumn_lane', 1),
    'autumn_scarecrow': ('autumn_lane', 2),
    'autumn_dusk': ('autumn_lane', 3),
    'autumn_walk': ('autumn_lane', 4),
    'village_market': ('village_green', 1),
    'village_stall': ('village_green', 2),
    'village_well': ('village_green', 3),
    'village_night': ('village_green', 4),
    'canyon_wash': ('red_canyon', 1),
    'canyon_ruins': ('red_canyon', 2),
    'canyon_slot': ('red_canyon', 3),
    'canyon_sunset': ('red_canyon', 4),
    'bayou_dusk': ('bayou', 1),
    'bayou_night': ('bayou', 2),
    'bayou_gator': ('bayou', 3),
    'bayou_heron': ('bayou', 4),
    'sea_kelp': ('kelp_forest', 1),
    'sea_diver': ('kelp_forest', 2),
    'sea_shoal': ('kelp_forest', 3),
    'sea_night': ('kelp_forest', 4),
    'aquarium_hall': ('aquarium', 1),
    'aquarium_manta': ('aquarium', 2),
    'aquarium_tunnel': ('aquarium', 3),
    'aquarium_jellies': ('aquarium', 4),
    'aquarium_reef': ('aquarium', 5),
    'aquarium_moon': ('aquarium', 6),
    'aquarium_diver': ('aquarium', 7),
    'aquarium_rockwork': ('aquarium', 8),
    'western_noon': ('ghost_town', 1),
    'western_saloon': ('ghost_town', 2),
    'western_ghost': ('ghost_town', 3),
    'western_windpump': ('ghost_town', 4),
    'saloon_noon': ('saloon', 1),
    'saloon_cards': ('saloon', 2),
    'saloon_piano': ('saloon', 3),
    'saloon_gambler': ('saloon', 4),
    'saloon_barkeep': ('saloon', 5),
    'mine_tunnel': ('gold_mine', 1),
    'mine_vein': ('gold_mine', 2),
    'mine_portal': ('gold_mine', 3),
    'fjord_day': ('fjord', 1),
    'fjord_dusk': ('fjord', 2),
    'fjord_water': ('fjord', 3),
    'palm_path': ('palm_house', 1),
    'palm_fountain': ('palm_house', 2),
    'palm_back': ('palm_house', 3),
    'garden_gate': ('autumn_garden', 1),
    'garden_pond': ('autumn_garden', 2),
    'garden_dusk': ('autumn_garden', 3),
    'sunken_temple': ('sunken_temple', 1),
    'sunken_colonnade': ('sunken_temple', 2),
    'sunken_head': ('sunken_temple', 3),
    'causeway_sunset': ('basalt_coast', 1),
    'causeway_organ': ('basalt_coast', 2),
    'causeway_hexagons': ('basalt_coast', 3),
    'winter_lane': ('winter_woods', 1),
    'winter_deer': ('winter_woods', 2),
    'winter_lantern': ('winter_woods', 3),
    'winter_stream': ('winter_woods', 4),
    'haunted_front': ('haunted_house', 1),
    'haunted_hall': ('haunted_house', 2),
    'haunted_parlour': ('haunted_house', 3),
    'haunted_ghost': ('haunted_house', 4),
    'moon_base': ('moon_base', 1),
    'moon_rover': ('moon_base', 2),
    'moon_night': ('moon_base', 3),
    'moon_earth': ('moon_base', 4),
    'street_rain': ('rainy_street', 1),
    'street_lightning': ('rainy_street', 3),
    'coast_tower': ('coast_lighthouse', 1),
    'coast_jetty': ('coast_lighthouse', 2),
    'bunker_hud': ('bunker_lab', 1),
    'bunker_crt': ('bunker_lab', 3),
    'castle_throne': ('castle_keep', 1),
    'castle_gate': ('castle_keep', 4),
    'castle_hall': ('castle_keep', 6),
    'chapel_yard': ('chapel_graveyard', 1),
    'chapel_nave': ('chapel_graveyard', 3),
    'glass_matins': ('glass_chapel', 1),
    'glass_beam': ('glass_chapel', 2),
    'glass_monk': ('glass_chapel', 3),
    'kaiju_bay': ('kaiju_harbor', 1),
    'kaiju_quay': ('kaiju_harbor', 2),
    'kaiju_breath': ('kaiju_harbor', 3),
    'kaiju_ashore': ('kaiju_harbor', 4),
    'kaiju_close': ('kaiju_harbor', 5),
    'kaiju_moth': ('kaiju_harbor', 6),
    'country_town': ('kaiju_country', 1),
    'country_stride': ('kaiju_country', 2),
    'country_pylon': ('kaiju_country', 3),
    'country_evening': ('kaiju_country', 4),
    'island_eruption': ('volcano_island', 1),
    'island_town': ('volcano_island', 2),
    'island_above': ('volcano_island', 3),
    'island_delta': ('volcano_island', 4),
    'desert_road': ('mesa_desert', 1),
    'desert_above': ('mesa_desert', 2),
    'desert_sunset': ('mesa_desert', 3),
    'desert_moon': ('mesa_desert', 4),
    'winter_lake': ('winter_valley', 1),
    'winter_village': ('winter_valley', 2),
    'winter_street': ('winter_valley', 3),
    'winter_morning': ('winter_valley', 4),
    'strait_golden': ('strait_bridge', 1),
    'strait_quay': ('strait_bridge', 2),
    'strait_above': ('strait_bridge', 3),
    'strait_dusk': ('strait_bridge', 4),
    'strait_kaiju': ('strait_bridge', 5),
    'archipelago_boat': ('archipelago', 1),
    'archipelago_above': ('archipelago', 2),
    'archipelago_atoll': ('archipelago', 3),
    'archipelago_golden': ('archipelago', 4),
    'valley_dawn': ('giant_valley', 1),
    'valley_village': ('giant_valley', 2),
    'valley_above': ('giant_valley', 3),
    'valley_afternoon': ('giant_valley', 4),
    'cave_beast': ('crystal_cave', 3),
    'crystal_cave': ('crystal_cave', 1),
    'crystal_violet': ('crystal_cave', 4),
    'crystal_close': ('crystal_cave', 5),
    'sewer_thing': ('sewer_tunnels', 3),
    'winter_night': ('winter_lake', 1),
    'winter_day': ('winter_lake', 4),
    'winter_cabin': ('winter_lake', 5),
    'station_deck': ('space_station', 1),
    'station_corridor': ('space_station', 2),
    'derelict_corridor': ('derelict_ship', 1),
    'derelict_hive': ('derelict_ship', 3),
    'hangar_bay': ('orbital_hangar', 1),
    'hangar_control': ('orbital_hangar', 2),
    'hangar_reactor': ('orbital_hangar', 3),
    'hangar_pilot': ('orbital_hangar', 4),
    'alien_landing': ('alien_world', 1),
    'alien_monolith': ('alien_world', 3),
    'dream_stair': ('dream_world', 2),
    'dream_mirror': ('dream_world', 3),
    'dream_plain': ('dream_chess', 1),
    'dream_door': ('dream_chess', 2),
    'dream_hole': ('dream_chess', 3),
    'dream_clock': ('dream_chess', 4),
    'library_hall': ('drowned_library', 1),
    'library_reader': ('drowned_library', 2),
    'library_beams': ('drowned_library', 3),
    'library_water': ('drowned_library', 4),
    'doors_hall': ('hall_of_doors', 1),
    'doors_stair': ('hall_of_doors', 2),
    'doors_sky': ('hall_of_doors', 3),
    'doors_up': ('hall_of_doors', 4),
    'doors_portal': ('hall_of_doors', 5),
    'claude_ask': ('claude_study', 2),
    'claude_balcony': ('claude_study', 3),
    'moor_dawn': ('misty_moor', 1),
    'moor_circle': ('misty_moor', 2),
    'cathedral_beam': ('cathedral_ruin', 2),
    'cathedral_pilgrim': ('cathedral_ruin', 3),
    'alley_street': ('rain_alley', 1),
    'alley_rain': ('rain_alley', 2),
    'alley_glass': ('rain_alley', 3),
    'alley_storm': ('rain_alley', 4),
    'alley_cars': ('rain_alley', 5),
    'neon_street': ('neon_street', 1),
    'neon_stall': ('neon_street', 2),
    'neon_signs': ('neon_street', 3),
    'neon_runner': ('neon_street', 4),
    'neon_counter': ('neon_street', 5),
    'market_lane': ('night_market', 1),
    'market_cart': ('night_market', 2),
    'market_puddle': ('night_market', 3),
    'market_runner': ('night_market', 4),
    'bar_room': ('neon_bar', 1),
    'bar_tank': ('neon_bar', 2),
    'bar_arcade': ('neon_bar', 3),
    'bar_bartender': ('neon_bar', 4),
    'market_samurai': ('night_market', 5),
    'bar_hacker': ('neon_bar', 5),
    'rooftop_canyon': ('neon_rooftop', 1),
    'rooftop_down': ('neon_rooftop', 2),
    'rooftop_train': ('neon_rooftop', 3),
    'rooftop_cat': ('neon_rooftop', 4),
    'capsule_corridor': ('capsule_hotel', 1),
    'capsule_berths': ('capsule_hotel', 2),
    'capsule_sleepwalker': ('capsule_hotel', 3),
    'capsule_vending': ('capsule_hotel', 4),
    'doomed_pit': ('doomed', 1),
    'doomed_overview': ('doomed', 2),
    'doomed_fight': ('doomed', 3),
    'doomed_window': ('doomed', 4),
    'clock_plaza': ('clockwork_city', 1),
    'clock_orrery': ('clockwork_city', 2),
    'clock_gears': ('clockwork_city', 3),
    'clock_tower': ('clockwork_city', 4),
    'aurora_lake': ('aurora_palace', 1),
    'aurora_gate': ('aurora_palace', 2),
    'aurora_throne': ('aurora_palace', 3),
    'aurora_shore': ('aurora_palace', 4),
    'glow_pool': ('glow_jungle', 1),
    'glow_head': ('glow_jungle', 2),
    'glow_flowers': ('glow_jungle', 3),
    'glow_path': ('glow_jungle', 4),
    'isles_temple': ('sky_islands', 1),
    'isles_bridge': ('sky_islands', 2),
    'isles_above': ('sky_islands', 3),
    'isles_golden': ('sky_islands', 4),
    'isles_falls': ('sky_islands', 5),
    'salt_sunset': ('salt_flat', 1),
    'salt_door': ('salt_flat', 2),
    'salt_noon': ('salt_flat', 3),
    'salt_night': ('salt_flat', 4),
    'salt_whale': ('salt_flat', 5),
    'salt_portal': ('salt_flat', 6),
    'vector_sunset': ('vector_world', 1),
    'vector_racers': ('vector_world', 2),
    'vector_beacon': ('vector_world', 3),
    'vector_core': ('vector_world', 4),
    'vector_runner': ('vector_world', 5),
    'jungle_path': ('jungle_temple', 1),
    'jungle_temple': ('jungle_temple', 2),
    'jungle_jaguar': ('jungle_temple', 3),
    'jungle_canopy': ('jungle_temple', 4),
    'temple_passage': ('temple_inside', 1),
    'temple_idol': ('temple_inside', 2),
    'temple_reach': ('temple_inside', 3),
    'ruins_way': ('ancient_ruins', 1),
    'ruins_head': ('ancient_ruins', 3),
    'ruins_night': ('ancient_ruins', 4),
    'ruins_columns': ('ancient_ruins', 5),
    'beach_sunset': ('tropical_beach', 1),
    'beach_pier': ('tropical_beach', 2),
    'beach_day': ('tropical_beach', 3),
    'beach_night': ('tropical_beach', 4),
    'beach_flare': ('tropical_beach', 5),
    'gui_hud': ('gui_hud', 1),
    'gui_lantern': ('gui_lantern', 1),
    'gui_menus_01': ('gui_menus', 1),
    'gui_menus_02': ('gui_menus', 2),
    'gui_trade_01': ('gui_trade', 1),
    'gui_trade_02': ('gui_trade', 2),
}
# gallery image -> example whose every shot is tiled at half size, two to a row
SHEETS = {'post_presets': 'post_presets', 'gui_themes': 'gui_themes', 'village_hours': 'village_hours'}
# gallery image -> example whose --map layout check is shown
MAPS = {'layout_map': 'garden_encounter'}
# gallery image -> a page of panels in examples/pages/, laid out by scripts/pages.py
PAGES = {'page_door': 'the_door', 'page_saloon': 'the_saloon', 'page_kaiju': 'the_kaiju'}
SPECIAL = {'cast', 'catalog'}
ALL = set(SHOTS) | set(SHEETS) | set(MAPS) | set(PAGES) | SPECIAL

_scenes = {}


def scene(name):
    """Load an example once and keep its (World, Renderer) for every shot that reuses it."""
    if name not in _scenes:
        sc = render.load_scene(os.path.join(EXAMPLES, name + '.json'))
        w = render.World(sc)
        _scenes[name] = (sc, (w, render.Renderer(w, sc)))
    return _scenes[name]


def build_shot(out, example, shot):
    sc, base = scene(example)
    render.save_png(render.render_shot(sc, shot - 1, base), out)


def build_sheet(out, example, gutter=4):
    sc, base = scene(example)
    n = len(sc.get('shots') or [sc['camera']])
    # frames are 3x upscaled pixel art; a box filter halves them cleanly, nearest would not
    frames = [render.render_shot(sc, i, base) for i in range(n)]
    frames = [f.resize((f.width // 2, f.height // 2), Image.BOX) for f in frames]
    w, h = frames[0].size
    rows = (n + 1) // 2
    sheet = Image.new('RGB', (w * 2 + gutter, h * rows + gutter * (rows - 1)), (0, 0, 0))
    for k, f in enumerate(frames):
        sheet.paste(f, ((k % 2) * (w + gutter), (k // 2) * (h + gutter)))
    render.save_png(sheet, out)


def build_map(out, example):
    sc, (world, _) = scene(example)
    cams = [render.merge_camera(sc, c) for c in (sc.get('shots') or [sc['camera']])]
    render.draw_map(world, sc, cams, out)


def build_cast(out, zoom=3, slot=112, top=20, bg=(28, 26, 34)):
    """The built-in characters side by side at 3x (each drawn in finer pixels - charhd), standing on one
    line, in the order the docs list them."""
    names = list(CHARACTERS)
    sprites = [assets.get_sprite(n)[0] for n in names]
    tall = max(rgba.shape[0] for rgba in sprites) * zoom
    sheet = Image.new('RGB', (slot * len(names), tall + 2 * top), bg)
    for i, rgba in enumerate(sprites):
        im = Image.fromarray((rgba.clip(0, 1) * 255).astype('uint8'), 'RGBA')
        im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
        sheet.paste(im, (i * slot + (slot - im.width) // 2, top + tall - im.height), im)
    render.save_png(sheet, out)


def build(name):
    out = os.path.join(OUT, name + '.png')
    if name in SHOTS:
        build_shot(out, *SHOTS[name])
    elif name in SHEETS:
        build_sheet(out, SHEETS[name])
    elif name in MAPS:
        build_map(out, MAPS[name])
    elif name in PAGES:
        import pages
        path = os.path.join(EXAMPLES, 'pages', PAGES[name] + '.json')
        with open(path, encoding='utf-8') as f:
            render.save_png(pages.render_page(json.load(f), os.path.dirname(path)), out)
    elif name == 'cast':
        build_cast(out)
    elif name == 'catalog':
        assets.catalog(out)
        render.save_png(Image.open(out), out)
    return out


def unmanaged():
    """Files in docs/gallery that no rule here builds."""
    return sorted(f for f in os.listdir(OUT) if f.endswith('.png') and f[:-4] not in ALL)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('names', nargs='*', help='gallery images to rebuild (default: all)')
    ap.add_argument('--check', action='store_true', help='report unmanaged files and exit')
    ap.add_argument('--prune', action='store_true', help='delete files no rule builds')
    args = ap.parse_args()

    stray = unmanaged()
    if args.check:
        print('unmanaged:', ', '.join(stray) or 'none')
        sys.exit(1 if stray else 0)
    unknown = [n for n in args.names if n not in ALL]
    if unknown:
        ap.error(f"no rule builds {unknown}; known: {', '.join(sorted(ALL))}")
    os.makedirs(OUT, exist_ok=True)
    for name in args.names or sorted(ALL):
        print(os.path.relpath(build(name), ROOT))
    if stray and args.prune:
        for f in stray:
            os.remove(os.path.join(OUT, f))
            print('removed', f)
    elif stray:
        print('not built by any rule (delete them, or add a rule):', ', '.join(stray), file=sys.stderr)


if __name__ == '__main__':
    main()

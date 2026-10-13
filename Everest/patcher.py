"""
Everest ROM Patcher and Injection Engine:
Handles inserting 3D object files, DrawGI tables, and item table entries
into game ROMs (e.g. Ocarina of Time and Super Mario 64).
"""

import logging
from typing import Any, Dict

from .registry import (
    get_registry,
    EVEREST_SM64_POWER_STAR,
    EVEREST_SM64_1UP,
    EVEREST_SM64_KEY,
    EVEREST_SM64_CAP,
    EVEREST_SM_MORPH_BALL,
    EVEREST_LTTP_SWORD,
    OOT_OBJ_SM64_STAR,
    OOT_OBJ_SM64_1UP,
    OOT_OBJ_SM64_KEY,
    OOT_GRAPHIC_SM64_STAR,
    OOT_GRAPHIC_SM64_1UP,
    OOT_GRAPHIC_SM64_KEY,
    OOT_CHEST_GOLD,
    OOT_CHEST_BROWN,
    OOT_CHEST_SILVER,
    OOT_ACTION_TWO_HANDS,
    OOT_ACTION_ONE_HAND,
)
from .models import build_star_zobj, build_mushroom_zobj, build_key_zobj

logger = logging.getLogger("Everest")


def patch_oot_physical_items(world: Any, rom: Any) -> None:
    """
    Patches physical cross-game item models, DrawGI table entries, and item rows
    into the Ocarina of Time ROM.
    """
    from worlds.oot.Patches import write_rom_item, add_to_extended_object_table
    from worlds.oot.MQ import File, update_dmadata

    logger.info("Everest: Injecting physical cross-game item models into OoT ROM...")

    # 1. Inject Super Mario 64 Power Star (.zobj)
    star_data = build_star_zobj()
    star_file = File({'Name': 'object_gi_sm64_star'})
    star_file.copy(rom)
    rom.write_bytes(star_file.start, star_data)
    star_file.end = star_file.start + len(star_data)
    update_dmadata(rom, star_file)
    add_to_extended_object_table(rom, OOT_OBJ_SM64_STAR, star_file)

    # 2. Inject Super Mario 64 1-Up Mushroom (.zobj)
    mushroom_data = build_mushroom_zobj()
    mushroom_file = File({'Name': 'object_gi_sm64_1up'})
    mushroom_file.copy(rom)
    rom.write_bytes(mushroom_file.start, mushroom_data)
    mushroom_file.end = mushroom_file.start + len(mushroom_data)
    update_dmadata(rom, mushroom_file)
    add_to_extended_object_table(rom, OOT_OBJ_SM64_1UP, mushroom_file)

    # 3. Inject Super Mario 64 Bowser Key (.zobj)
    key_data = build_key_zobj()
    key_file = File({'Name': 'object_gi_sm64_key'})
    key_file.copy(rom)
    rom.write_bytes(key_file.start, key_data)
    key_file.end = key_file.start + len(key_data)
    update_dmadata(rom, key_file)
    add_to_extended_object_table(rom, OOT_OBJ_SM64_KEY, key_file)

    # 4. Patch item_draw_table for physical items
    # DrawGI function for simple segment 6 model: 0x8040AE74
    draw_table_addr = rom.sym('item_draw_table')
    if draw_table_addr:
        # Star DrawGI entry
        rom.write_int32(draw_table_addr + (OOT_GRAPHIC_SM64_STAR * 36), 0x8040AE74)
        rom.write_int32(draw_table_addr + (OOT_GRAPHIC_SM64_STAR * 36) + 4, 0x060001B0) # dlist offset

        # 1-Up Mushroom DrawGI entry
        rom.write_int32(draw_table_addr + (OOT_GRAPHIC_SM64_1UP * 36), 0x8040AE74)
        rom.write_int32(draw_table_addr + (OOT_GRAPHIC_SM64_1UP * 36) + 4, 0x06000170)

        # Bowser Key DrawGI entry
        rom.write_int32(draw_table_addr + (OOT_GRAPHIC_SM64_KEY * 36), 0x8040AE74)
        rom.write_int32(draw_table_addr + (OOT_GRAPHIC_SM64_KEY * 36) + 4, 0x06000140)

    # 5. Write Item Rows in OoT item_table
    # Base handlers: upgrade_fn = 2151732344, effect_fn = 2151731180
    UPGRADE_FN = 2151732344
    EFFECT_FN = 2151731180

    # SM64 Power Star
    write_rom_item(rom, EVEREST_SM64_POWER_STAR, {
        'base_item_id': 83,
        'action_id': OOT_ACTION_TWO_HANDS,
        'text_id': 0x90A0,
        'object_id': OOT_OBJ_SM64_STAR,
        'graphic_id': OOT_GRAPHIC_SM64_STAR,
        'chest_type': OOT_CHEST_GOLD,
        'upgrade_fn': UPGRADE_FN,
        'effect_fn': EFFECT_FN,
        'effect_arg1': -1,
        'effect_arg2': -1,
        'collectible': 255,
    })

    # SM64 1-Up Mushroom
    write_rom_item(rom, EVEREST_SM64_1UP, {
        'base_item_id': 77,
        'action_id': OOT_ACTION_ONE_HAND,
        'text_id': 0x90A1,
        'object_id': OOT_OBJ_SM64_1UP,
        'graphic_id': OOT_GRAPHIC_SM64_1UP,
        'chest_type': OOT_CHEST_BROWN,
        'upgrade_fn': UPGRADE_FN,
        'effect_fn': EFFECT_FN,
        'effect_arg1': -1,
        'effect_arg2': -1,
        'collectible': 4,
    })

    # SM64 Bowser Key
    write_rom_item(rom, EVEREST_SM64_KEY, {
        'base_item_id': 83,
        'action_id': OOT_ACTION_ONE_HAND,
        'text_id': 0x90A2,
        'object_id': OOT_OBJ_SM64_KEY,
        'graphic_id': OOT_GRAPHIC_SM64_KEY,
        'chest_type': OOT_CHEST_SILVER,
        'upgrade_fn': UPGRADE_FN,
        'effect_fn': EFFECT_FN,
        'effect_arg1': -1,
        'effect_arg2': -1,
        'collectible': 255,
    })

    # SM64 Wing/Metal/Vanish Cap
    write_rom_item(rom, EVEREST_SM64_CAP, {
        'base_item_id': 83,
        'action_id': OOT_ACTION_TWO_HANDS,
        'text_id': 0x90A3,
        'object_id': OOT_OBJ_SM64_STAR,
        'graphic_id': OOT_GRAPHIC_SM64_STAR,
        'chest_type': OOT_CHEST_GOLD,
        'upgrade_fn': UPGRADE_FN,
        'effect_fn': EFFECT_FN,
        'effect_arg1': -1,
        'effect_arg2': -1,
        'collectible': 255,
    })

    # Super Metroid Morph Ball
    write_rom_item(rom, EVEREST_SM_MORPH_BALL, {
        'base_item_id': 83,
        'action_id': OOT_ACTION_TWO_HANDS,
        'text_id': 0x90A4,
        'object_id': 239, # Compass object with morph ball texture
        'graphic_id': 59,
        'chest_type': OOT_CHEST_GOLD,
        'upgrade_fn': UPGRADE_FN,
        'effect_fn': EFFECT_FN,
        'effect_arg1': -1,
        'effect_arg2': -1,
        'collectible': 255,
    })

    # A Link to the Past Master Sword
    write_rom_item(rom, EVEREST_LTTP_SWORD, {
        'base_item_id': 83,
        'action_id': OOT_ACTION_TWO_HANDS,
        'text_id': 0x90A5,
        'object_id': 0x0158, # Master Sword object
        'graphic_id': 0x56,
        'chest_type': OOT_CHEST_GOLD,
        'upgrade_fn': UPGRADE_FN,
        'effect_fn': EFFECT_FN,
        'effect_arg1': -1,
        'effect_arg2': -1,
        'collectible': 255,
    })

    logger.info("Everest: Successfully patched physical items into OoT ROM!")


def get_everest_oot_item_definitions() -> Dict[int, Dict[str, Any]]:
    """
    Returns the dictionary of custom item row definitions for OoT's item_table.
    """
    return {
        EVEREST_SM64_POWER_STAR: {
            'item_id': 83,
            'special_flag': OOT_ACTION_TWO_HANDS,
            'text_id': 0x90A0,
            'object_id': OOT_OBJ_SM64_STAR,
            'graphic_id': OOT_GRAPHIC_SM64_STAR,
            'chest_type': OOT_CHEST_GOLD,
            'collectible_type': 0,
            'flags': 0,
            'upgrade_type': -1,
            'upgrade_flag': -1,
            'draw_func': 0,
        },
        EVEREST_SM64_1UP: {
            'item_id': 77,
            'special_flag': OOT_ACTION_ONE_HAND,
            'text_id': 0x90A1,
            'object_id': OOT_OBJ_SM64_1UP,
            'graphic_id': OOT_GRAPHIC_SM64_1UP,
            'chest_type': OOT_CHEST_BROWN,
            'collectible_type': 4,
            'flags': 0,
            'upgrade_type': -1,
            'upgrade_flag': -1,
            'draw_func': 0,
        },
        EVEREST_SM64_KEY: {
            'item_id': 83,
            'special_flag': OOT_ACTION_ONE_HAND,
            'text_id': 0x90A2,
            'object_id': OOT_OBJ_SM64_KEY,
            'graphic_id': OOT_GRAPHIC_SM64_KEY,
            'chest_type': OOT_CHEST_SILVER,
            'collectible_type': 0,
            'flags': 0,
            'upgrade_type': -1,
            'upgrade_flag': -1,
            'draw_func': 0,
        },
        EVEREST_SM64_CAP: {
            'item_id': 83,
            'special_flag': OOT_ACTION_TWO_HANDS,
            'text_id': 0x90A3,
            'object_id': OOT_OBJ_SM64_STAR,
            'graphic_id': OOT_GRAPHIC_SM64_STAR,
            'chest_type': OOT_CHEST_GOLD,
            'collectible_type': 0,
            'flags': 0,
            'upgrade_type': -1,
            'upgrade_flag': -1,
            'draw_func': 0,
        },
        EVEREST_SM_MORPH_BALL: {
            'item_id': 83,
            'special_flag': OOT_ACTION_TWO_HANDS,
            'text_id': 0x90A4,
            'object_id': 239,
            'graphic_id': 59,
            'chest_type': OOT_CHEST_GOLD,
            'collectible_type': 0,
            'flags': 0,
            'upgrade_type': -1,
            'upgrade_flag': -1,
            'draw_func': 0,
        },
        EVEREST_LTTP_SWORD: {
            'item_id': 83,
            'special_flag': OOT_ACTION_TWO_HANDS,
            'text_id': 0x90A5,
            'object_id': 0x0158,
            'graphic_id': 0x56,
            'chest_type': OOT_CHEST_GOLD,
            'collectible_type': 0,
            'flags': 0,
            'upgrade_type': -1,
            'upgrade_flag': -1,
            'draw_func': 0,
        },
    }


def get_sm64_physical_slot_data(world_or_mw: Any, player: Any = None) -> Dict[str, Any]:
    """
    Builds the Everest physical item mapping dictionary for Super Mario 64's slot data.
    Maps location addresses or items to foreign physical item 3D model specifications.
    """
    reg = get_registry()
    mapping: Dict[Any, Dict[str, Any]] = {}

    if hasattr(world_or_mw, "multiworld") and hasattr(world_or_mw, "player"):
        multiworld = world_or_mw.multiworld
        player_id = world_or_mw.player
    else:
        multiworld = world_or_mw
        player_id = player

    if multiworld and player_id is not None and hasattr(multiworld, "get_filled_locations"):
        player_locations = multiworld.get_filled_locations(player_id)
        for loc in player_locations:
            if loc.item and loc.item.player != player_id:
                source_game = loc.item.game
                item_name = loc.item.name
                spec = reg.resolve_sm64_spec(source_game, item_name)
                player_name = getattr(multiworld, "player_name", {}).get(loc.item.player, f"Player {loc.item.player}")
                mapping[loc.address] = {
                    "source_game": source_game,
                    "item_name": item_name,
                    "player_name": player_name,
                    **spec
                }

    # Include default known game models for client-side rendering
    general_mappings = {
        "Ocarina of Time": {
            "Kokiri Sword": reg.resolve_sm64_spec("Ocarina of Time", "Kokiri Sword"),
            "Master Sword": reg.resolve_sm64_spec("Ocarina of Time", "Master Sword"),
            "Biggoron's Sword": reg.resolve_sm64_spec("Ocarina of Time", "Biggoron's Sword"),
            "Hylian Shield": reg.resolve_sm64_spec("Ocarina of Time", "Hylian Shield"),
            "Mirror Shield": reg.resolve_sm64_spec("Ocarina of Time", "Mirror Shield"),
            "Megaton Hammer": reg.resolve_sm64_spec("Ocarina of Time", "Megaton Hammer"),
        }
    }

    return {
        "EverestPhysicalItems": True,
        "LocationPhysicalItems": mapping,
        "PhysicalItemMappings": general_mappings,
    }

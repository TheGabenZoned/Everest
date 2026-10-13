"""
Everest Model Specification: Ocarina of Time Items in Super Mario 64
Defines 3D model structures, tokens, behaviors, animations, and sound effects
for rendering Ocarina of Time physical items inside Super Mario 64 (sm64ex).
"""

from typing import Dict, Any


def get_oot_sword_sm64_spec(item_name: str) -> Dict[str, Any]:
    """
    Returns the SM64 model specification for OoT Swords (Kokiri, Master, Biggoron).
    """
    is_master = "Master" in item_name
    is_biggoron = "Biggoron" in item_name

    model_name = "MODEL_OOT_MASTER_SWORD" if is_master else ("MODEL_OOT_BIGGORON_SWORD" if is_biggoron else "MODEL_OOT_KOKIRI_SWORD")
    scale = 1.4 if is_biggoron else (1.1 if is_master else 0.85)

    return {
        "model_name": model_name,
        "model_id": 0x71 if is_master else (0x72 if is_biggoron else 0x70),
        "geo_layout": "oot_sword_geo",
        "behavior": "bhvEverestPhysicalItem",
        "scale": scale,
        "spin_speed": 0x400,
        "bob_amplitude": 15.0,
        "sparkle_particles": True,
        "collect_sound": "SOUND_GENERAL_COLLECT_1UP" if not is_master else "SOUND_MENU_STAR_SOUND",
        "collect_animation": "MARIO_ANIM_STAR_DANCE",
        "display_name": item_name,
        "origin_game": "Ocarina of Time",
        "category": "sword",
        "colors": {
            "blade": [220, 225, 235],
            "hilt": [40, 60, 160] if is_master else [80, 50, 20],
            "gem": [220, 180, 20] if is_master else [180, 30, 20],
        }
    }


def get_oot_shield_sm64_spec(item_name: str) -> Dict[str, Any]:
    """
    Returns the SM64 model specification for OoT Shields (Hylian, Mirror, Deku).
    """
    is_mirror = "Mirror" in item_name
    model_name = "MODEL_OOT_MIRROR_SHIELD" if is_mirror else "MODEL_OOT_HYLIAN_SHIELD"

    return {
        "model_name": model_name,
        "model_id": 0x74 if is_mirror else 0x73,
        "geo_layout": "oot_shield_geo",
        "behavior": "bhvEverestPhysicalItem",
        "scale": 1.0,
        "spin_speed": 0x300,
        "bob_amplitude": 12.0,
        "sparkle_particles": True,
        "collect_sound": "SOUND_GENERAL_COLLECT_1UP",
        "collect_animation": "MARIO_ANIM_STAR_DANCE",
        "display_name": item_name,
        "origin_game": "Ocarina of Time",
        "category": "shield",
    }


def get_oot_hammer_sm64_spec(item_name: str) -> Dict[str, Any]:
    """
    Returns the SM64 model specification for Megaton Hammer.
    """
    return {
        "model_name": "MODEL_OOT_MEGATON_HAMMER",
        "model_id": 0x75,
        "geo_layout": "oot_hammer_geo",
        "behavior": "bhvEverestPhysicalItem",
        "scale": 1.2,
        "spin_speed": 0x350,
        "bob_amplitude": 10.0,
        "sparkle_particles": True,
        "collect_sound": "SOUND_GENERAL_COLLECT_1UP",
        "collect_animation": "MARIO_ANIM_STAR_DANCE",
        "display_name": item_name,
        "origin_game": "Ocarina of Time",
        "category": "hammer",
    }


OOT_TO_SM64_MODELS = {
    "Kokiri Sword": get_oot_sword_sm64_spec("Kokiri Sword"),
    "Master Sword": get_oot_sword_sm64_spec("Master Sword"),
    "Biggoron's Sword": get_oot_sword_sm64_spec("Biggoron's Sword"),
    "Hylian Shield": get_oot_shield_sm64_spec("Hylian Shield"),
    "Mirror Shield": get_oot_shield_sm64_spec("Mirror Shield"),
    "Megaton Hammer": get_oot_hammer_sm64_spec("Megaton Hammer"),
}


def get_oot_model_spec(item_name: str) -> Dict[str, Any]:
    """Lookup or generate an SM64 physical model spec for an OoT item."""
    if item_name in OOT_TO_SM64_MODELS:
        return OOT_TO_SM64_MODELS[item_name]
    if "Sword" in item_name or "Blade" in item_name:
        return get_oot_sword_sm64_spec(item_name)
    if "Shield" in item_name:
        return get_oot_shield_sm64_spec(item_name)
    if "Hammer" in item_name:
        return get_oot_hammer_sm64_spec(item_name)
    return {
        "model_name": "MODEL_OOT_GENERIC_CHEST",
        "model_id": 0x70,
        "behavior": "bhvEverestPhysicalItem",
        "scale": 1.0,
        "display_name": item_name,
        "category": "generic",
    }

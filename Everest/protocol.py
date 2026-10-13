"""
Everest Network Protocol Extensions:
Provides network packet enhancements and client tags for live physical item
synchronization across emulators and native PC ports.
"""

from typing import Dict, Any, Optional
from .registry import get_registry

# Client Tag signaling Everest physical item support
TAG_EVEREST_PHYSICAL_ITEMS = "EverestPhysicalItems"


def get_network_physical_metadata(game: str, item_name: str) -> Dict[str, Any]:
    """
    Returns network visual metadata for a physical item, enabling connected
    clients to display live physical 3D models when items are received or unlocked.
    """
    reg = get_registry()
    phys_item = reg.get(game, item_name)

    if phys_item:
        return {
            "everest_enabled": True,
            "origin_game": game,
            "item_name": item_name,
            "display_name": phys_item.display_name,
            "category": phys_item.category,
            "oot_item_id": phys_item.oot_data.get("item_id"),
            "sm64_model_name": phys_item.sm64_data.get("model_name"),
            "sm64_model_id": phys_item.sm64_data.get("model_id"),
            "is_progression": phys_item.is_progression,
        }

    # Generic fallback metadata
    oot_id = reg.resolve_oot_item_id(game, item_name)
    sm64_spec = reg.resolve_sm64_spec(game, item_name)
    return {
        "everest_enabled": True,
        "origin_game": game,
        "item_name": item_name,
        "display_name": item_name,
        "category": "generic",
        "oot_item_id": oot_id,
        "sm64_model_name": sm64_spec.get("model_name"),
        "sm64_model_id": sm64_spec.get("model_id"),
        "is_progression": True,
    }


def build_physical_item_bounced_packet(
    sender_slot: int,
    sender_game: str,
    item_name: str,
    target_player: int,
    target_game: str,
) -> Dict[str, Any]:
    """
    Constructs an Archipelago Bounce packet containing physical appearance metadata.
    """
    meta = get_network_physical_metadata(sender_game, item_name)
    return {
        "cmd": "Bounce",
        "tags": [TAG_EVEREST_PHYSICAL_ITEMS],
        "data": {
            "sender_slot": sender_slot,
            "source_game": sender_game,
            "item_name": item_name,
            "target_player": target_player,
            "target_game": target_game,
            "physical_appearance": {
                "model_id": meta.get("sm64_model_name") or f"MODEL_{item_name.upper().replace(' ', '_')}",
                "category": meta.get("category", "generic"),
                "oot_item_id": meta.get("oot_item_id"),
            },
        },
    }

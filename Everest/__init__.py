"""
Everest: The Archipelago Fork with Physical Item Integration.

Everest enhances multiworld randomizers by rendering true in-game physical 3D models,
sprites, and animations for items from other games (such as Link receiving and lifting
a Super Mario 64 Power Star in Ocarina of Time, or Mario collecting Link's Master Sword
in Super Mario 64).
"""

__version__ = "1.0.0"
FORK_NAME = "Everest"

from .registry import (
    ItemCategory,
    PhysicalAppearance,
    PhysicalItem,
    PhysicalItemRegistry,
    get_registry,
    EVEREST_SM64_POWER_STAR,
    EVEREST_SM64_1UP,
    EVEREST_SM64_KEY,
    EVEREST_SM64_CAP,
    EVEREST_SM_MORPH_BALL,
    EVEREST_LTTP_SWORD,
    EVEREST_GENERIC_PHYSICAL,
)
from .patcher import (
    patch_oot_physical_items,
    get_sm64_physical_slot_data,
    get_everest_oot_item_definitions,
)
from .protocol import (
    TAG_EVEREST_PHYSICAL_ITEMS,
    get_network_physical_metadata,
    build_physical_item_bounced_packet,
)
from .models.sm64_star import build_sm64_star_zobj
from .models.sm64_mushroom import build_sm64_mushroom_zobj
from .models.sm64_key import build_sm64_key_zobj
from .models.oot_sword import get_oot_model_spec, OOT_TO_SM64_MODELS

__all__ = [
    "__version__",
    "FORK_NAME",
    "ItemCategory",
    "PhysicalAppearance",
    "PhysicalItem",
    "PhysicalItemRegistry",
    "get_registry",
    "patch_oot_physical_items",
    "get_sm64_physical_slot_data",
    "get_everest_oot_item_definitions",
    "TAG_EVEREST_PHYSICAL_ITEMS",
    "get_network_physical_metadata",
    "build_physical_item_bounced_packet",
    "build_sm64_star_zobj",
    "build_sm64_mushroom_zobj",
    "build_sm64_key_zobj",
    "get_oot_model_spec",
    "OOT_TO_SM64_MODELS",
    "EVEREST_SM64_POWER_STAR",
    "EVEREST_SM64_1UP",
    "EVEREST_SM64_KEY",
    "EVEREST_SM64_CAP",
    "EVEREST_SM_MORPH_BALL",
    "EVEREST_LTTP_SWORD",
    "EVEREST_GENERIC_PHYSICAL",
]

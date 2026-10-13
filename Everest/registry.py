"""
Everest Physical Item Registry:
Central repository and cross-game resolution engine for physical item integration
across all games in the Archipelago multiworld.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Callable, List

from .models import (
    build_star_zobj,
    build_mushroom_zobj,
    build_key_zobj,
    get_oot_sword_sm64_spec,
    get_oot_shield_sm64_spec,
    get_oot_hammer_sm64_spec,
)

# Dedicated Item Indices in Ocarina of Time's item_table (all within valid vanilla table bounds)
EVEREST_SM64_POWER_STAR = 0xBA
EVEREST_SM64_1UP = 0xC7
EVEREST_SM64_KEY = 0xC8
EVEREST_SM64_CAP = 0x7D
EVEREST_SM_MORPH_BALL = 0x7E
EVEREST_LTTP_SWORD = 0x7F
EVEREST_GENERIC_PHYSICAL = 0xB9

# Extended Object IDs in OoT (0x192 vanilla + 1 + extended_id)
OOT_OBJ_SM64_STAR = 0x196
OOT_OBJ_SM64_1UP = 0x197
OOT_OBJ_SM64_KEY = 0x198

# Graphic IDs in OoT item_draw_table
OOT_GRAPHIC_SM64_STAR = 0x77
OOT_GRAPHIC_SM64_1UP = 0x78
OOT_GRAPHIC_SM64_KEY = 0x79

# Chest Types in OoT
OOT_CHEST_GOLD = 12
OOT_CHEST_BROWN = 0
OOT_CHEST_SILVER = 8
OOT_CHEST_SKULL = 4

# Action IDs (Link pickup animations)
OOT_ACTION_TWO_HANDS = 0x00
OOT_ACTION_ONE_HAND = 0x01


class ItemCategory:
    """Standard semantic item categories for cross-game matching."""
    STAR = "star"
    MUSHROOM = "mushroom"
    KEY = "key"
    CAP = "cap"
    SWORD = "sword"
    SHIELD = "shield"
    HAMMER = "hammer"
    UPGRADE = "upgrade"
    GENERIC = "generic"


@dataclass
class PhysicalAppearance:
    """Visual descriptor for a 3D model representation in a game engine."""
    model_name: str
    model_id: int
    category: str = "generic"
    scale: float = 1.0


@dataclass
class PhysicalItem:
    """Represents a physical game item with multi-game asset mappings."""
    name: str
    game: str
    category: str = ItemCategory.GENERIC
    display_name: str = ""
    is_progression: bool = True
    oot_data: Dict[str, Any] = field(default_factory=dict)
    sm64_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.display_name:
            self.display_name = self.name


class PhysicalItemRegistry:
    """
    Singleton registry managing physical cross-game item mappings and runtime resolution.
    """
    def __init__(self):
        self._items: Dict[str, Dict[str, PhysicalItem]] = {}
        self._category_items: Dict[str, List[PhysicalItem]] = {}
        self._register_default_items()

    def register(self, item: PhysicalItem) -> None:
        """Register a physical item for a specific game."""
        game_map = self._items.setdefault(item.game, {})
        game_map[item.name] = item
        self._category_items.setdefault(item.category, []).append(item)

    def get(self, game: str, item_name: str) -> Optional[PhysicalItem]:
        """Lookup a physical item by game and item name."""
        return self._items.get(game, {}).get(item_name)

    def resolve_oot_item_id(self, source_game: str, item_name: str, advancement: bool = True) -> int:
        """
        Resolves the appropriate item index in OoT's item_table for an item coming
        from any game in the multiworld.
        """
        # 1. Exact match
        phys_item = self.get(source_game, item_name)
        if phys_item and "item_id" in phys_item.oot_data:
            return phys_item.oot_data["item_id"]

        # 2. Semantic matching based on item name and category
        lower_name = item_name.lower()

        # Star / Shine / Emblem
        if any(w in lower_name for w in ["star", "shine", "emblem", "celeste", "fragment"]):
            return EVEREST_SM64_POWER_STAR

        # 1-Up / Mushroom / Food / Health
        if any(w in lower_name for w in ["mushroom", "1up", "life", "cookie", "potion"]):
            return EVEREST_SM64_1UP

        # Key / Lock / Gate
        if any(w in lower_name for w in ["key", "pass", "card", "lock"]):
            return EVEREST_SM64_KEY

        # Cap / Hat / Helmet
        if any(w in lower_name for w in ["cap", "hat", "mask", "helmet"]):
            return EVEREST_SM64_CAP

        # Morph Ball / Orb / Sphere
        if any(w in lower_name for w in ["ball", "orb", "sphere", "pearl"]):
            return EVEREST_SM_MORPH_BALL

        # Sword / Blade / Blade weapon
        if any(w in lower_name for w in ["sword", "blade", "dagger", "saber", "knife"]):
            return EVEREST_LTTP_SWORD

        # Fallback to standard AP progression or junk
        return 0xD4 if advancement else 0xD5

    def resolve_sm64_spec(self, source_game: str, item_name: str) -> Dict[str, Any]:
        """
        Resolves the SM64 physical model and behavior specification for an item coming
        from another game (e.g. Ocarina of Time Sword in Super Mario 64).
        """
        phys_item = self.get(source_game, item_name)
        if phys_item and phys_item.sm64_data:
            return phys_item.sm64_data

        lower_name = item_name.lower()

        # Swords / Blades
        if any(w in lower_name for w in ["sword", "blade", "knife"]):
            return get_oot_sword_sm64_spec(item_name)

        # Shields
        if any(w in lower_name for w in ["shield", "guard"]):
            return get_oot_shield_sm64_spec(item_name)

        # Hammers / Clubs
        if any(w in lower_name for w in ["hammer", "club", "mace"]):
            return get_oot_hammer_sm64_spec(item_name)

        # Default physical item spec for foreign objects in SM64
        return {
            "model_name": "MODEL_EVEREST_PHYSICAL_ITEM",
            "model_id": 0x76,
            "geo_layout": "everest_item_geo",
            "behavior": "bhvEverestPhysicalItem",
            "scale": 1.0,
            "spin_speed": 0x400,
            "bob_amplitude": 12.0,
            "sparkle_particles": True,
            "collect_sound": "SOUND_MENU_STAR_SOUND",
            "collect_animation": "MARIO_ANIM_STAR_DANCE",
            "display_name": item_name,
            "origin_game": source_game,
            "category": "generic",
        }

    def _register_default_items(self) -> None:
        """Registers the canonical physical item database across games."""
        # -------------------------------------------------------------
        # Super Mario 64
        # -------------------------------------------------------------
        self.register(PhysicalItem(
            name="Power Star",
            game="Super Mario 64",
            category="star",
            display_name="Power Star",
            is_progression=True,
            oot_data={
                "item_id": EVEREST_SM64_POWER_STAR,
                "object_id": OOT_OBJ_SM64_STAR,
                "graphic_id": OOT_GRAPHIC_SM64_STAR,
                "chest_type": OOT_CHEST_GOLD,
                "action_id": OOT_ACTION_TWO_HANDS,
                "model_builder": build_star_zobj,
                "message": "\x08\x13\x67You found a \x05\x41Super Mario 64 Power Star\x05\x40!\x01It radiates cosmic energy!"
            },
            sm64_data={
                "model_name": "MODEL_STAR",
                "model_id": 0x7A,
                "behavior": "bhvStar",
                "collect_sound": "SOUND_MENU_STAR_SOUND",
                "collect_animation": "MARIO_ANIM_STAR_DANCE",
            }
        ))

        self.register(PhysicalItem(
            name="1Up Mushroom",
            game="Super Mario 64",
            category="mushroom",
            display_name="1-Up Mushroom",
            is_progression=False,
            oot_data={
                "item_id": EVEREST_SM64_1UP,
                "object_id": OOT_OBJ_SM64_1UP,
                "graphic_id": OOT_GRAPHIC_SM64_1UP,
                "chest_type": OOT_CHEST_BROWN,
                "action_id": OOT_ACTION_ONE_HAND,
                "model_builder": build_mushroom_zobj,
                "message": "\x08\x13\x68You found a \x05\x421-Up Mushroom\x05\x40!\x01Extra life!"
            },
            sm64_data={
                "model_name": "MODEL_1UP",
                "model_id": 0x79,
                "behavior": "bhv1upWalking",
                "collect_sound": "SOUND_GENERAL_COLLECT_1UP",
            }
        ))

        for key_name in ["Basement Key", "Second Floor Key", "Progressive Key"]:
            self.register(PhysicalItem(
                name=key_name,
                game="Super Mario 64",
                category="key",
                display_name=key_name,
                is_progression=True,
                oot_data={
                    "item_id": EVEREST_SM64_KEY,
                    "object_id": OOT_OBJ_SM64_KEY,
                    "graphic_id": OOT_GRAPHIC_SM64_KEY,
                    "chest_type": OOT_CHEST_SILVER,
                    "action_id": OOT_ACTION_ONE_HAND,
                    "model_builder": build_key_zobj,
                    "message": "\x08\x13\x69You found a \x05\x43Bowser Castle Key\x05\x40!\x01Unlocks doors in Bowser's domain!"
                }
            ))

        for cap_name in ["Wing Cap", "Metal Cap", "Vanish Cap"]:
            self.register(PhysicalItem(
                name=cap_name,
                game="Super Mario 64",
                category="cap",
                display_name=cap_name,
                is_progression=True,
                oot_data={
                    "item_id": EVEREST_SM64_CAP,
                    "object_id": OOT_OBJ_SM64_STAR, # Uses glowing star object with cap colors
                    "graphic_id": OOT_GRAPHIC_SM64_STAR,
                    "chest_type": OOT_CHEST_GOLD,
                    "action_id": OOT_ACTION_TWO_HANDS,
                }
            ))

        # -------------------------------------------------------------
        # Ocarina of Time
        # -------------------------------------------------------------
        for sword in ["Kokiri Sword", "Master Sword", "Biggoron Sword"]:
            self.register(PhysicalItem(
                name=sword,
                game="Ocarina of Time",
                category="sword",
                display_name=sword,
                is_progression=True,
                sm64_data=get_oot_sword_sm64_spec(sword)
            ))

        for shield in ["Deku Shield", "Hylian Shield", "Mirror Shield"]:
            self.register(PhysicalItem(
                name=shield,
                game="Ocarina of Time",
                category="shield",
                display_name=shield,
                is_progression=True,
                sm64_data=get_oot_shield_sm64_spec(shield)
            ))

        self.register(PhysicalItem(
            name="Megaton Hammer",
            game="Ocarina of Time",
            category="hammer",
            display_name="Megaton Hammer",
            is_progression=True,
            sm64_data=get_oot_hammer_sm64_spec("Megaton Hammer")
        ))

        # -------------------------------------------------------------
        # Super Metroid
        # -------------------------------------------------------------
        self.register(PhysicalItem(
            name="Morph Ball",
            game="Super Metroid",
            category="ball",
            display_name="Morph Ball",
            is_progression=True,
            oot_data={
                "item_id": EVEREST_SM_MORPH_BALL,
                "chest_type": OOT_CHEST_GOLD,
                "action_id": OOT_ACTION_TWO_HANDS,
            }
        ))

        # -------------------------------------------------------------
        # A Link to the Past
        # -------------------------------------------------------------
        self.register(PhysicalItem(
            name="Progressive Sword",
            game="A Link to the Past",
            category="sword",
            display_name="Master Sword",
            is_progression=True,
            oot_data={
                "item_id": EVEREST_LTTP_SWORD,
                "chest_type": OOT_CHEST_GOLD,
                "action_id": OOT_ACTION_TWO_HANDS,
            },
            sm64_data=get_oot_sword_sm64_spec("Master Sword")
        ))


# Global Singleton
_REGISTRY = PhysicalItemRegistry()


def get_registry() -> PhysicalItemRegistry:
    """Returns the global PhysicalItemRegistry instance."""
    return _REGISTRY

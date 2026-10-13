import unittest
import struct
from Everest import (
    PhysicalItemRegistry,
    get_registry,
    PhysicalItem,
    ItemCategory,
    PhysicalAppearance,
    build_sm64_star_zobj,
    build_sm64_mushroom_zobj,
    build_sm64_key_zobj,
    get_sm64_physical_slot_data,
    patch_oot_physical_items,
    get_everest_oot_item_definitions,
    TAG_EVEREST_PHYSICAL_ITEMS,
    build_physical_item_bounced_packet,
    get_oot_model_spec,
    OOT_TO_SM64_MODELS,
)
from Options import PhysicalItemIntegration, PerGameCommonOptions
from worlds.oot.Patches import AP_PROGRESSION, AP_JUNK


class TestEverestPhysicalItems(unittest.TestCase):
    """Test Everest cross-game physical item integration."""

    def test_options_definition(self):
        """Verify PhysicalItemIntegration option is registered and configured properly."""
        self.assertIn("physical_item_integration", PerGameCommonOptions.type_hints)
        opt_cls = PerGameCommonOptions.type_hints["physical_item_integration"]
        self.assertEqual(opt_cls.default, PhysicalItemIntegration.option_enabled)
        self.assertEqual(opt_cls.option_disabled, 0)
        self.assertEqual(opt_cls.option_progression_only, 1)
        self.assertEqual(opt_cls.option_enabled, 2)

    def test_registry_sm64_items(self):
        """Test resolving Super Mario 64 items to OoT physical item IDs."""
        reg = get_registry()

        # Power Star -> 0xBA
        star_id = reg.resolve_oot_item_id("Super Mario 64", "Power Star", advancement=True)
        self.assertEqual(star_id, 0xBA)

        # 1-Up Mushroom -> 0xC7
        mushroom_id = reg.resolve_oot_item_id("Super Mario 64", "1Up Mushroom", advancement=False)
        self.assertEqual(mushroom_id, 0xC7)

        # Bowser Key -> 0xC8
        key_id = reg.resolve_oot_item_id("Super Mario 64", "Basement Key", advancement=True)
        self.assertEqual(key_id, 0xC8)

        # Wing Cap -> 0x7D
        cap_id = reg.resolve_oot_item_id("Super Mario 64", "Wing Cap", advancement=True)
        self.assertEqual(cap_id, 0x7D)

    def test_registry_cross_game_categories(self):
        """Test that unknown/other game items map by semantic category."""
        reg = get_registry()

        # Metroid Morph Ball -> 0x7E
        mb_id = reg.resolve_oot_item_id("Super Metroid", "Morph Ball", advancement=True)
        self.assertEqual(mb_id, 0x7E)

        # ALTTP Master Sword -> 0x7F
        sword_id = reg.resolve_oot_item_id("A Link to the Past", "Master Sword", advancement=True)
        self.assertEqual(sword_id, 0x7F)

        # Generic key in unknown game -> Bowser Key model (0xC8)
        generic_key = reg.resolve_oot_item_id("Unknown Game", "Dungeon Key", advancement=True)
        self.assertEqual(generic_key, 0xC8)

        # Generic unknown progression item -> AP_PROGRESSION (0xD4)
        generic_item = reg.resolve_oot_item_id("Unknown Game", "Strange Gizmo XYZ", advancement=True)
        self.assertEqual(generic_item, AP_PROGRESSION)

        # Generic unknown junk item -> AP_JUNK (0xD5)
        generic_junk = reg.resolve_oot_item_id("Unknown Game", "Strange Dust XYZ", advancement=False)
        self.assertEqual(generic_junk, AP_JUNK)

    def test_sm64_star_zobj_generation(self):
        """Verify Fast3D .zobj model generation for Mario 64 Power Star."""
        zobj_bytes = build_sm64_star_zobj()
        self.assertIsInstance(zobj_bytes, bytes)
        self.assertGreater(len(zobj_bytes), 500)
        # F3DEX2 display list end opcode G_ENDDL is 0xDF000000 0x00000000
        self.assertIn(b"\xdf\x00\x00\x00", zobj_bytes)

    def test_sm64_mushroom_zobj_generation(self):
        """Verify Fast3D .zobj model generation for Mario 64 1-Up Mushroom."""
        zobj_bytes = build_sm64_mushroom_zobj()
        self.assertIsInstance(zobj_bytes, bytes)
        self.assertGreater(len(zobj_bytes), 300)
        self.assertIn(b"\xdf\x00\x00\x00", zobj_bytes)

    def test_sm64_key_zobj_generation(self):
        """Verify Fast3D .zobj model generation for Mario 64 Bowser Key."""
        zobj_bytes = build_sm64_key_zobj()
        self.assertIsInstance(zobj_bytes, bytes)
        self.assertGreater(len(zobj_bytes), 200)
        self.assertIn(b"\xdf\x00\x00\x00", zobj_bytes)

    def test_oot_to_sm64_model_specs(self):
        """Verify OoT items have defined SM64 physical model specifications."""
        for item_name in ["Kokiri Sword", "Master Sword", "Biggoron's Sword", "Hylian Shield", "Megaton Hammer"]:
            spec = get_oot_model_spec(item_name)
            self.assertIsNotNone(spec, f"Model spec missing for {item_name}")
            self.assertIn("model_id", spec)
            self.assertIn("behavior", spec)
            self.assertIn("scale", spec)

    def test_sm64_slot_data(self):
        """Verify SM64 slot data generation includes Everest physical item mappings."""
        class MockOptions:
            physical_item_integration = PhysicalItemIntegration.from_any(2)

        class MockMultiworld:
            pass

        class MockWorld:
            options = MockOptions()
            multiworld = MockMultiworld()

        slot_data = get_sm64_physical_slot_data(MockWorld())
        self.assertIn("EverestPhysicalItems", slot_data)
        self.assertTrue(slot_data["EverestPhysicalItems"])
        self.assertIn("PhysicalItemMappings", slot_data)
        mappings = slot_data["PhysicalItemMappings"]
        self.assertIn("Ocarina of Time", mappings)
        self.assertIn("Kokiri Sword", mappings["Ocarina of Time"])
        self.assertIn("Master Sword", mappings["Ocarina of Time"])

    def test_protocol_packet_builder(self):
        """Verify protocol bounce packet generation for physical items."""
        packet = build_physical_item_bounced_packet(
            sender_slot=1,
            sender_game="Ocarina of Time",
            item_name="Master Sword",
            target_player=2,
            target_game="Super Mario 64",
        )
        self.assertEqual(packet["cmd"], "Bounce")
        self.assertEqual(packet["tags"], [TAG_EVEREST_PHYSICAL_ITEMS])
        data = packet["data"]
        self.assertEqual(data["sender_slot"], 1)
        self.assertEqual(data["source_game"], "Ocarina of Time")
        self.assertEqual(data["item_name"], "Master Sword")
        self.assertEqual(data["target_player"], 2)
        self.assertEqual(data["target_game"], "Super Mario 64")
        self.assertIn("physical_appearance", data)
        self.assertEqual(data["physical_appearance"]["model_id"], "MODEL_OOT_MASTER_SWORD")

    def test_oot_custom_item_definitions(self):
        """Verify item definitions table structure for OoT ROM patching."""
        defs = get_everest_oot_item_definitions()
        self.assertIn(0xBA, defs)
        self.assertIn(0xC7, defs)
        self.assertIn(0xC8, defs)

        # Check packing format matches OoT item_table row format (24 bytes)
        item_table_row = struct.Struct('>BBHHBBIIhhBxxx')
        self.assertEqual(item_table_row.size, 24)

        for index, item in defs.items():
            packed = item_table_row.pack(
                item['item_id'],
                item['special_flag'],
                item['text_id'],
                item['object_id'],
                item['graphic_id'],
                item['chest_type'],
                item['collectible_type'],
                item['flags'],
                item['upgrade_type'],
                item['upgrade_flag'],
                item['draw_func'],
            )
            self.assertEqual(len(packed), 24)

    def test_oot_override_entry_resolution(self):
        """Verify get_override_entry resolves physical items when enabled and falls back when disabled."""
        from worlds.oot.Patches import get_override_entry

        class MockItem:
            game = "Super Mario 64"
            name = "Power Star"
            advancement = True
            player = 2
            trap = False
            index = 0

        class MockLocation:
            scene = 0x51
            default = 0x01
            type = "Chest"
            disabled = None
            item = MockItem()

        class MockOptions:
            def __init__(self, phys_val):
                self.physical_item_integration = PhysicalItemIntegration.from_any(phys_val)

        class MockOoTWorld:
            def __init__(self, phys_val):
                self.player = 1
                self.options = MockOptions(phys_val)
                self.trap_appearances = {}

        # 1. Enabled (val=2) -> should resolve to SM64 Power Star (0xBA)
        world_enabled = MockOoTWorld(2)
        override = get_override_entry(world_enabled, MockLocation())
        self.assertIsNotNone(override)
        # override tuple is (scene, type, default, item_id, player_id, looks_like_item_id)
        scene, type_, default, item_id, player_id, looks_like_item_id = override
        self.assertEqual(item_id, 0xBA)
        self.assertEqual(player_id, 2)

        # 2. Disabled (val=0) -> should resolve to vanilla AP_PROGRESSION (0xD4)
        world_disabled = MockOoTWorld(0)
        override_dis = get_override_entry(world_disabled, MockLocation())
        self.assertIsNotNone(override_dis)
        _, _, _, item_id_dis, _, _ = override_dis
        self.assertEqual(item_id_dis, AP_PROGRESSION)


if __name__ == "__main__":
    unittest.main()

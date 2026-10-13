# Everest: Physical Item Integration

**Everest** is a specialized fork of Archipelago engineered to bring physical immersion to multiworld randomizers.

---

## The Problem in Vanilla Multiworlds
In standard Archipelago multiworlds, when a player opens a chest or inspects an item sent to another game, the game engine usually falls back to a generic token (e.g. `AP_PROGRESSION` or `AP_JUNK` in Ocarina of Time, or a standard colored coin). Players are told by a textbox or client log what was found, but the visual world does not reflect the item's true identity.

## The Everest Solution
**Everest** injects native game assets, geometry generators, and cross-game model specifications so that each game physically renders foreign items:

* **Ocarina of Time <-> Super Mario 64 Example:**
  * When Link opens a chest containing a **Super Mario 64 Power Star**, the chest opens as a **Gold Chest**, and Link lifts a true **3D Mario 64 Power Star** over his head using the iconic two-handed fanfare animation.
  * In shops, the pedestal physically showcases the 3D Power Star or 1-Up Mushroom.
  * When Mario finds Link's **Sword or Shield** in Super Mario 64, a 3D model of the **Master Sword** or **Hylian Shield** hovers and rotates in the level with sparkle effects, triggering Mario's star dance upon collection.

---

## Technical Architecture

### 1. Fast3D / F3DEX2 Display List and Object Generation
Everest includes standalone Fast3D binary compilers (`Everest/models/`):
* `sm64_star.py`: Generates complete vertex structures (with front bevels, back bevels, and blue oval eye geometry) and F3DEX2 display lists compiled into an authentic `.zobj` file.
* `sm64_mushroom.py`: Builds a 3D 1-Up Mushroom with cap, white spots, and stem.
* `sm64_key.py`: Builds a 3D Bowser Key with ring, shaft, and tooth bit.

### 2. Ocarina of Time ROM Patching
* **Extended Object Table:** Injects custom `.zobj` files into OoT's `EXTENDED_OBJECT_TABLE` (Object IDs `0x196` for Power Star, `0x197` for 1-Up, `0x198` for Bowser Key).
* **Item Table Utilization:** Assigns unused vanilla item rows without table relocation:
  * `0xBA`: Super Mario 64 Power Star (Gold chest, 2-hand lift animation, textbox `0x90A0`)
  * `0xC7`: Super Mario 64 1-Up Mushroom (Brown chest, 1-hand lift, textbox `0x90A1`)
  * `0xC8`: Super Mario 64 Bowser Key (Silver chest, 1-hand lift, textbox `0x90A2`)
  * `0x7D`: Mario Cap (Gold chest, 2-hand lift, textbox `0x90A3`)
  * `0x7E`: Super Metroid Morph Ball (Gold chest, 2-hand lift, textbox `0x90A4`)
  * `0x7F`: ALTTP Master Sword (Gold chest, 2-hand lift, textbox `0x90A5`)
* **DrawGI Function Hooking:** Binds graphic IDs (`0x77`, `0x78`, `0x79`) in `item_draw_table` to execute standard model render routines pointing directly to Segment 6 display lists.
* **Override Resolution:** Updates `get_override_entry()` and shop generation to resolve foreign multiworld items to their corresponding Everest physical item IDs based on player settings.

### 3. Super Mario 64 (sm64ex) Integration
* Generates custom slot data containing `EverestPhysicalItems: True` and location-to-model mappings.
* Exports 3D model specifications, rotation behaviors, scales, and sound effects for OoT items:
  * `MODEL_OOT_KOKIRI_SWORD`, `MODEL_OOT_MASTER_SWORD`, `MODEL_OOT_BIGGORON_SWORD`
  * `MODEL_OOT_HYLIAN_SHIELD`, `MODEL_OOT_MIRROR_SHIELD`
  * `MODEL_OOT_MEGATON_HAMMER`

### 4. Semantic Category Matching
For games without bespoke 1-to-1 models, Everest uses a fallback category classifier (`Everest/registry.py`):
* Sword / Blade items -> Master Sword model
* Shield / Armor items -> Hylian Shield model
* Key / Lock items -> Bowser Key model
* Star / Artifact items -> Power Star model
* Mushroom / Consumable items -> 1-Up Mushroom model
* Unknown progression -> AP Progression token
* Unknown junk -> AP Junk token

---

## Configuration Options

Each player can configure physical item integration in their YAML options file:

```yaml
Ocarina of Time:
  physical_item_integration: enabled # Options: disabled (0), progression_only (1), enabled (2)

Super Mario 64:
  physical_item_integration: enabled
```

* `disabled` (0): Vanilla Archipelago behavior (standard progression/junk tokens).
* `progression_only` (1): Only progression and major items render as physical foreign models; junk items render as normal junk.
* `enabled` (2 - **Default**): All supported foreign items render as physical 3D models.

---

## Network Protocol Extension

Everest clients announce support using the `EverestPhysicalItems` tag:
```json
{
  "cmd": "ConnectUpdate",
  "tags": ["EverestPhysicalItems"]
}
```

Cross-game visual sync can also be broadcast via Archipelago `Bounce` packets:
```json
{
  "cmd": "Bounce",
  "tags": ["EverestPhysicalItems"],
  "data": {
    "sender_slot": 1,
    "source_game": "Ocarina of Time",
    "item_name": "Master Sword",
    "target_player": 2,
    "target_game": "Super Mario 64",
    "physical_appearance": {
      "model_id": "MODEL_OOT_MASTER_SWORD",
      "category": "sword"
    }
  }
}
```

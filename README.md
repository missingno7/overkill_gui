# Overkill RE Editor

Refactored project layout.

## Run

```bash
python overkill_graphics_browser.py
```

or:

```bash
python -m overkill.gui.app
```

## Current structure

```text
overkill_editor/
├─ overkill_graphics_browser.py      # small compatibility runner
├─ game_data/OVERKILL                # original game data archive
├─ overkill/
│  ├─ core.py                        # raw archive parsing, BIC parsing, EGA rendering helpers
│  └─ gui/
│     └─ app.py                      # Tkinter GUI/editor
├─ archive/
│  ├─ research/                      # old PASS*.md research logs
│  └─ analysis/                      # disassembly / analysis artifacts
└─ resources_extracted/              # generated extracted resources, if present
```

## GUI tabs

The GUI now has two top-level tabs:

- **Graphics Browser** – raw resource browser for BIC/ENC/archive entries.
- **Level Viewer** – focused level renderer using LEVxMAP + paired LEVxBLX, with click inspector.

The old Preview / Hex / Inspector notebook still exists inside the Graphics Browser tab.

## Architecture rule

`overkill/core.py` contains parser/rendering logic that can be used from CLI tools or tests without Tkinter.

`overkill/gui/app.py` contains UI code only and imports from `overkill.core`.

Future cleanup can split `core.py` further into:

```text
overkill/archive.py
overkill/formats/bic.py
overkill/formats/bic_type0_logo.py
overkill/formats/bic_type3.py
overkill/formats/bic_type4.py
overkill/formats/blx.py
overkill/formats/map.py
overkill/render/ega.py
overkill/render/level.py
```

For now this pass keeps one `core.py` to reduce refactor risk while removing parsing logic from the GUI file.


---

# Overkill graphics/resource browser — pass 12

Research GUI for the DOS game **Overkill**.

## Run

```bash
pip install -r requirements.txt
python overkill_graphics_browser.py
```

Windows:

```bat
run_browser.bat
```

## Current reverse-engineering status

- `OVERKILL` is parsed as a `SHADOW` resource archive.
- `.BIC` files use PackBits-like RLE after a 7-byte header.
- `1X1.BIC`, `2X2.BIC`, `2X2C.BIC` decode as transposed sprite records.
- `G1.BIC`, `G2.BIC`, `G4.BIC`, `G5.BIC` decode as 32x32 transposed frame sheets.
- `LEVxMAP.BIC` decodes to a 13 x 288 tile map.
- **Pass 12 fix:** `LEVxBLX.BIC` is not sequential 132-byte records. It is four plane-grouped blocks. Each tile has four 33-byte plane records: 1 byte header/control + 32 bytes of 16x16 1bpp plane data.
- Level map values are rendered as 1-based tile indices: map value `1` = BLX tile `0`.
- Unknown/out-of-range map values are likely object/trigger/flag codes and are hidden as black in the visual level render.

## Still unresolved

- Exact EGA palette/register mapping for levels.
- Meaning of high/out-of-range map values.
- `.ENC` screen/music formats.
- `G0.BIC`, `G3.BIC`, `SHIP.BIC` exact layouts.

## BIC image-stream alignment rule

For image payload streams discovered so far, the first **decoded** byte is an alignment/padding byte, not image data:

- `type=3` full images: `PackBits(source_data[5:])[1:]`
- `LOGO.BIC` type=0 escape-RLE: decode `image_size + 1`, then use `[1:]`

This fixes the classic 8px horizontal shift without hard-coded image translation.

## Pass51 level-object notes

Level rendering now skips a metadata-like canonical row 0 when it starts with `0x00`. This removes the bogus final display row from LEV1/LEV2/etc.

High MAP values are now shown as experimental 2X2 object/enemy candidates using:

```text
2X2 sprite index = raw MAP value - 0x26
```

The inspector reports both the BLX tile interpretation and the candidate 2X2 sprite index.


## Pass52 level layer controls

The Level Viewer now has a right-side layer panel:

- Show experimental enemies/objects
- Show red debug overlay
- Show grid

The base render is terrain-only by default. Experimental enemies/objects are rendered as an overlay over MAP/BLX terrain, not as replacement tiles.


## Pass53 enemy mapping update

The object/enemy overlay now uses a small calibrated mapping table before the diagnostic fallback:

- `0x92 -> 2X2 sprite 68`
- `0x93 -> 2X2 sprite 69`
- `0x95 -> 2X2 sprite 70`
- `0xB1..0xB3 -> 2X2 sprites 139..141`

The MAP inspector now reports nearby object candidates within radius 3, because visible sprites can overlap adjacent terrain cells whose direct MAP value is `0x01`.


## Pass54 enemy/object research update

The previous experimental MAP-to-2X2 enemy sprite overlay has been disabled because it produced false enemies. Disassembly shows a separate runtime object-slot system with object fields such as position, sprite/animation field, dispatch class, and behavior type. MAP/BLX remains the terrain layer; enemies appear to be spawned by EXE tables/state machines and may exist over empty space. The Level Viewer checkbox now shows MAP special/out-of-range markers only.


## Pass55 enemy encoding research

The LEV1 enemy at canonical row 125 / col 2 is not encoded as the clicked MAP value. The clicked cell is raw `0x01`.

Disassembly now points to a runtime object system:
- object `+0x08` is sprite/frame-ish,
- object `+0x18` is behavior/type-ish,
- sprites 68..70 (`0x44..0x46`) are selected by runtime code,
- the drop sprite 71 is probably table/computed, not a direct MAP value.

See `archive/research/PASS55_ENEMY_ENCODING_DEEPER.md`.


## Pass56 verification overlays and zoom

Level Viewer now defaults to `3x` zoom and has a zoom selector from `1x` to `5x`.

New toggles:
- Show research observations
- Show canonical row ruler

Research observations live in:

```text
research_overlays/level_observations.json
```

The first observation marks the reported LEV1 enemy at canonical row `125`, col `2`, using 2X2 sprites `68..70` and drop `71`.


## Pass57 off-grid enemy markers

The Level Viewer research overlay now supports off-grid pixel-coordinate observations via `level_x` / `level_y` in `research_overlays/level_observations.json`.

Pass57 adds four approximate LEV1 enemy markers derived by matching the provided screenshot to the rendered LEV1 terrain. See `archive/research/PASS57_OFFGRID_ENEMY_RESEARCH.md`.


## Pass58 c160 enemy feedback

The screenshot section around `c160` is now annotated as four off-grid enemies using `2X2` sprites `147..150`.

Updated file:

```text
research_overlays/level_observations.json
```

New previews:

```text
sample_previews_pass58/2X2_sprites_147_150.png
sample_previews_pass58/LEV1_c160_offgrid_enemies_147_150_crop_3x.png
```


## Pass59 c160 enemy sprite formula

The c160 enemy feedback now matches a concrete runtime sprite formula found in EXE:

```text
0x233C cycles 0..3
object +0x08 = 0x93 + [0x233C]
```

This yields 2X2 sprites:

```text
147, 148, 149, 150
```

Added:

```text
research_overlays/runtime_spawn_hypotheses.json
archive/research/PASS59_C160_ENEMY_SPRITE_FORMULA.md
```


## Pass60 object behavior dispatch

Found the central object behavior dispatcher:

```text
object +0x18 = behavior/type dispatch field
object +0x08 = sprite/frame-ish field
```

The c160 sprite formula remains:

```text
object +0x08 = 0x93 + [0x233C] => 2X2 sprites 147..150
```

Added analysis under:

```text
archive/analysis/pass60/
archive/research/PASS60_OBJECT_BEHAVIOR_DISPATCH.md
```


## Pass61 pickup/drop formula

Found a strong drop/pickup sprite formula:

```text
object +0x08 = object +0x06 + 0x3B
2X2 sprite = drop_type + 59
```

This explains the reported `2X2:71` drop as:

```text
drop_type = 12
59 + 12 = 71
```

Added:

```text
archive/research/PASS61_PICKUP_DROP_FORMULA.md
archive/analysis/pass61/
research_overlays/runtime_spawn_hypotheses.json
```


## Pass62 formation table breakthrough

Found a real 4-object runtime formation pattern:

```text
scroll 0x2350 == 0x0EA0
SI = DS:0xA3EE
CX = 4
record = object+0x02, object+0x04, object+0x08
behavior = 0x53
```

This proves that some off-grid enemies/objects are stored as runtime formation tables, not MAP cells.

Added:

```text
archive/research/PASS62_FORMATION_TABLE_AND_DROP_TYPE_SEARCH.md
archive/analysis/pass62/
sample_previews_pass62/PASS62_formation_table_breakthrough_card.png
```


## Pass63 enemy position research

Added a disassembly-derived candidate list for runtime enemy/object positions:

```text
research_overlays/runtime_formation_candidates.json
archive/research/PASS63_ENEMY_POSITION_RESEARCH.md
```

Strongest candidate:

```text
scroll 0x2350 == 0x0EA0
DS:0xA3EE
4 records × 3 words
word0 -> object+0x02
word1 -> object+0x04
word2 -> object+0x08
```

The actual DS:0xA3EE table contents are not in the flat EXE offset, so the next step is a runtime memory dump.


## Pass64 suspected runtime positions overlay

Level Viewer now has a toggle:

```text
Show suspected runtime formations
```

This displays:
- orange observed off-grid markers from screenshots/user feedback,
- magenta disassembly-derived runtime formation trigger lines/placeholders.

Current previews:

```text
sample_previews_pass64/LEV1_c160_suspected_positions_crop_3x.png
sample_previews_pass64/LEV1_scroll_0xEA0_candidate_crop_3x.png
```


## Pass65 enemy position research update

The `Show suspected runtime formations` layer is now OFF by default because the previous magenta candidates were not visually correlated with the game.

Important correction:

```text
0x2350 is not simply canonical_row * 16.
It is a runtime scroll/progress variable updated by 0x0D steps.
```

Added:

```text
archive/research/PASS65_ENEMY_POSITION_RESEARCH_UPDATE.md
archive/analysis/pass65/
sample_previews_pass65/PASS65_enemy_position_research_update_card.png
```


## Pass66 real object pool breakthrough

Found the live runtime object pools:

```text
Pool A: DS:23B4..DS:2B5B, 35 slots
Pool B: DS:2B5C..DS:32CB, 34 slots
slot size: 0x38
```

This gives a practical path to real enemy positions: dump `DS:23B4..DS:32CB` while enemies are visible.

Added:

```text
tools/convert_runtime_object_dump.py
research_overlays/runtime_object_slots.json
archive/research/PASS66_REAL_OBJECT_POOL_BREAKTHROUGH.md
sample_previews_pass66/PASS66_real_object_pool_breakthrough_card.png
```

Level Viewer now has:

```text
Show runtime object dump
```


## Pass67 c160 watch-sprite workflow

The runtime object dump converter now watches sprites:

```text
147,148,149,150,71
```

These watched objects are highlighted in the GUI runtime dump overlay.

Important caveat: the static formula `object+0x08 = 0x93 + [0x233C]` matches sprites `147..150`, but its owning behavior entry is not yet statically proven. The next reliable step is to dump `DS:23B4..DS:32CB` while the c160 enemies are visible.

Added:

```text
archive/research/PASS67_C160_WATCH_SPRITE_WORKFLOW.md
sample_previews_pass67/PASS67_c160_watch_sprite_workflow_card.png
```


## Pass68 c160 runtime dump breakthrough

The uploaded DOSBox-X dump revealed the exact live objects for the four c160 enemies:

```text
A14: x=64,  y=54, sprite=149, behavior=0x2D
A15: x=80,  y=50, sprite=149, behavior=0x2D
A16: x=112, y=50, sprite=149, behavior=0x2D
A17: x=128, y=54, sprite=149, behavior=0x2D
```

Added a dedicated GUI tab:

```text
Runtime Objects
```

It renders screen/playfield-space runtime dump positions and lists active object slots.

Added:

```text
runtime_dumps/MEMDUMP_c160_enemies.bin
research_overlays/runtime_object_slots.json
archive/research/PASS68_C160_RUNTIME_DUMP_BREAKTHROUGH.md
sample_previews_pass68/PASS68_runtime_object_dump_screen_space_3x.png
```


## Pass69 second dump comparison

The second uploaded `MEMDUMP.BIN` was byte-for-byte identical to the first one, so it does not correspond to the screenshot with the green enemy.

Added:

```text
runtime_dumps/MEMDUMP_second_upload.bin
archive/research/PASS69_SECOND_DUMP_IDENTICAL.md
tools/compare_runtime_dumps.py
```


## Pass70 segment breakthrough

The second unique dump (`MEMDUMP2.BIN`) revealed that the object-pool dump target should use the stable data segment / DGROUP, which matches `SS`, not the transient `DS` used inside blit routines.

For the green-enemy screenshot:

```text
DS = 2C41
SS = 1F0D
```

Therefore the next correct dump command is:

```text
MEMDUMPBIN 1F0D:23B4 F18
```

or `SS:23B4` if supported.


## Pass71 valid SS dump with green enemy

A correct `SS:23B4` dump from the screenshot with the green enemy was decoded successfully.

Confirmed live objects:

```text
A02: x=128, y=192, sprite=104, behavior=0x8B   <-- green enemy
A03: x=64,  y=127, sprite=150, behavior=0x2D   <-- blue enemy
A05: x=112, y=107, sprite=150, behavior=0x2D   <-- blue enemy
A06: x=128, y=127, sprite=150, behavior=0x2D   <-- blue enemy
```

Added:

```text
runtime_dumps/MEMDUMP_valid_ss_green_enemy.bin
research_overlays/runtime_object_slots_green_snapshot.json
archive/research/PASS71_VALID_SS_DUMP_GREEN_ENEMY.md
```


## Pass72 enemy map-event breakthrough

Confirmed that at least some enemies are encoded directly in `LEV1MAP.BIC` as special event bytes.

The green enemy from the runtime dump:

```text
sprite 104, behavior 0x8B, x=128
```

matches:

```text
LEV1MAP canonical row 153, col 8, raw 0x04
0x04 -> initializer 0x78D4 -> behavior 0x8B
x = col * 16 = 128
```

Added Level Viewer overlay:

```text
Show decoded map events
```

Added:

```text
research_overlays/decoded_map_events_LEV1.json
archive/research/PASS72_ENEMY_MAP_EVENT_BREAKTHROUGH.md
sample_previews_pass72/LEV1_row153_green_event_crop_3x.png
```


## Pass73 PLAQ check and moving-enemy stream

`PLAQ0.ENC..PLAQ5.ENC` now look very unlikely to contain moving enemy positions. They share a graphics-like common header/prefix pattern and sit next to UI/screen `.ENC` resources in the internal filename table.

More importantly, the actual moving-enemy system has now been identified:

```text
stream parser: 0x4987..0x4B96
record: trigger + formation descriptor pointer + base_x + base_y
descriptor: behavior + count + pixel dx/dy offsets
```

The blue behavior `0x2D` formation descriptor is confirmed statically:

```text
(0,0), (16,-16), (48,-16), (64,0)
```

which exactly matches the runtime X positions `64,80,112,128` when `base_x=64`.

Added:

```text
archive/research/PASS73_PLAQ_CHECK_AND_MOVING_SPAWN_STREAM.md
research_overlays/moving_enemy_formation_descriptors_static.json
tools/inspect_moving_formation_descriptors.py
```


## Pass74 Level 1 intro minigame dump

The intro-minigame dump confirms:

```text
20 visible minigame ships = behavior 0x20
1 controller-like object  = behavior 0x1F
```

The executable contains an exact hardcoded 20-position table at raw EXE offset `0x11161`.
Those 20 records match the runtime dump positions exactly.

Added:

```text
runtime_dumps/MEMDUMP_intro_minigame_level1.bin
research_overlays/runtime_object_slots_intro_minigame.json
research_overlays/intro_minigame_level1_enemy_position_table.json
archive/research/PASS74_INTRO_MINIGAME_DUMP_AND_POSITION_TABLE.md
```


## Pass75 scrolling moving-enemy placement found

The ordinary scrolling-level moving-enemy placement layer is now decoded from the unpacked EXE artifact.

```text
spawn streams:       raw 0x12D7D..0x13249
formation descriptors: raw 0x13249..0x136DD
```

Six per-level streams were parsed, with 138 total spawn records and 53 shared formation descriptors.

LEV1/Edrax blue formation is confirmed:

```text
trigger 130 -> approx row 158
descriptor 0xD0B0 -> behavior 0x2D × 4
base_x 64, base_y -16
x positions 64,80,112,128
```

This exactly matches the runtime dump.

Added Level Viewer overlay:

```text
Show moving enemy spawns
```

Added:

```text
research_overlays/moving_enemy_spawn_streams_all_levels.json
research_overlays/moving_enemy_spawn_stream_LEV1.json
archive/research/PASS75_SCROLLING_MOVING_ENEMY_PLACEMENT_FOUND.md
tools/decode_moving_enemy_spawn_streams.py
```


## Pass76 moving-enemy sprite families

Sprite/frame assignment is now being attached to decoded moving-enemy behaviors.

Confirmed:

```text
0x2D -> 2X2:147–150
0x8B -> 2X2:101–104
```

Strong static candidates include:

```text
0x89 -> 28–31
0x30 -> 16–19
0x19 -> 54–58
0x1A -> 36–41
0x1B -> 39–44
0x3B -> 81–86
0x8C -> likely 93–96
```

The Level Viewer moving-enemy overlay now appends sprite-family hints where available.

Added:

```text
research_overlays/moving_enemy_sprite_family_hints.json
research_overlays/moving_enemy_behavior_handler_sprite_evidence.json
archive/research/PASS76_MOVING_ENEMY_SPRITE_FAMILIES.md
```

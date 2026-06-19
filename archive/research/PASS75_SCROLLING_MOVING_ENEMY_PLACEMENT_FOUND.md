# Pass75 - scrolling moving-enemy placement fully located

## Main breakthrough

The regular **scrolling-level moving enemies** are now located in executable data, separate from both:

```text
LEVxMAP.BIC static grid events
intro-minigame hardcoded position tables
```

The game uses:

```text
1. six per-level moving spawn streams
2. one shared formation descriptor table
```

## Exact storage regions in the unpacked EXE artifact

```text
moving spawn streams:
    raw EXE 0x12D7D .. 0x13249

shared formation descriptors:
    raw EXE 0x13249 .. 0x136DD
```

Parsed counts:

```text
streams:     6
descriptors: 53
records:     138
```

Per-stream record counts:

```text
stream 0: 15 records
stream 1: 34 records
stream 2: 62 records
stream 3: 8 records
stream 4: 5 records
stream 5: 14 records
```

`stream 1` is confirmed to correspond to **LEV1 / EDRAX**, because it contains the blue `0x2D` formation that matches the user's screenshot and runtime dump.

## Spawn stream record format

The parser around `0x4987..0x4B96` reads:

```text
u16 trigger
u16 descriptor_ptr
u16 base_x
s16 base_y
```

Special variant:

```text
u16 trigger
u16 0xFFFF marker
u16 descriptor_ptr
u16 base_x
s16 base_y
```

The code then reads the descriptor and creates objects at:

```text
x = base_x + dx
y = base_y + dy
```

## Formation descriptor format

Each descriptor is:

```text
u16 field_14
u16 field_0A
u16 behavior
u16 count

repeat count:
    s16 dx
    s16 dy
```

In the unpacked EXE artifact:

```text
raw_descriptor_offset = descriptor_ptr + 0x6521
```

That mapping resolves **all 52 unique descriptor pointers** used by the six streams.

## Confirmed LEV1 blue formation

The user-observed blue formation with:

```text
behavior 0x2D
sprites 147..150
runtime X positions 64,80,112,128
```

comes from **LEV1 stream record**:

```text
stream index: 1
trigger:      130
descriptor:   0xD0B0
base_x:       64
base_y:       -16
```

The descriptor is:

```text
behavior = 0x2D
count    = 4

offsets:
    ( 0,   0)
    (16, -16)
    (48, -16)
    (64,   0)
```

X positions:

```text
64 + [0,16,48,64]
= [64,80,112,128]
```

This is an exact match to the runtime object dump.

## Level-row mapping

The stream triggers run from values near `272` down to `4`.

I added an inferred map-row projection:

```text
approx canonical row = 288 - trigger
```

This is strongly supported by the confirmed blue event:

```text
trigger 130 -> approx row 158
```

which matches the user's screenshot section around `c160`.

I still mark this as **inferred**, because the game advances the trigger/progress variable through its own scroll update logic.

## What this means for "where all enemies are stored"

Current storage model:

```text
A. Static terrain-bound objects/enemies
   LEVxMAP.BIC event bytes
   Example: LEV1 raw 0x04 -> green behavior 0x8B static/grid event

B. Scrolling moving enemy formations
   EXE raw 0x12D7D..0x13249 spawn streams
   EXE raw 0x13249..0x136DD formation descriptors

C. Intro minigame enemies
   separate hardcoded tables, e.g. Level 1 intro table at raw 0x11161

D. Likely remaining special cases
   bosses / special scripted encounters may still have bespoke code paths,
   but the ordinary scrolling moving-enemy placement layer is now found.
```

## New data files

```text
research_overlays/moving_enemy_spawn_streams_all_levels.json
research_overlays/moving_enemy_spawn_stream_LEV1.json
```

## New Level Viewer overlay

The editor now has a grounded moving-enemy spawn overlay:

```text
Show moving enemy spawns
```

It projects stream events to an approximate map row using `288-trigger`, and shows the descriptor behavior/count at each spawn anchor.

## Analysis files

```text
archive/analysis/pass75/moving_enemy_spawn_streams_all_levels.tsv
archive/analysis/pass75/moving_enemy_formation_descriptors_all.tsv
archive/analysis/pass75/moving_enemy_stream_parser_4987_4b96.txt
archive/analysis/pass75/moving_enemy_stream_raw_region_12d7d_13249.hex.txt
archive/analysis/pass75/moving_enemy_descriptor_raw_region_13249_136dd.hex.txt
```

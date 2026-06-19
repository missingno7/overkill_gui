# Pass72 - enemy map-event breakthrough

## Breakthrough

We now have direct evidence that **some enemy/object positions are encoded in the 13-wide `LEVxMAP.BIC` rows as special event codes**.

The code path is:

```asm
9e70: [A408] = [2350]          ; current row offset into map/event buffer

77ae: ES = CS:[9592]           ; decoded map/event buffer
77b3: SI = [A408]
77b7: [A406] = 13              ; scan 13 columns
77bd: [A40A] = 0               ; current x in pixels

77c3: AL = ES:[SI]             ; read one MAP/event byte
77cc: call level_dispatch[2356]

77d0: [A40A] += 0x10           ; next column = +16 px
77d5: SI++
```

The generic event object initializer:

```asm
802f: ...
803b: AX = [A40A]
803e: object+0x04 = AX         ; x
8041: object+0x02 = 0x10       ; y at spawn time
```

So a MAP event at:

```text
col = C
```

spawns at:

```text
x = C * 16
```

## Confirmed LEV1 green enemy

From the runtime dump:

```text
green enemy:
    sprite   = 104  (within 2X2:101..104)
    behavior = 0x8B
    x        = 128
```

Static disassembly shows behavior `0x8B` is created by:

```asm
78d4: call 0x802f
78da: object+0x18 = 0x8B
```

The LEV1/Edrax dispatcher path maps raw byte `0x04` to that initializer:

```asm
77dd: cmp AL, 0x04
77e1: jmp 0x78D4
```

And `LEV1MAP.BIC` contains:

```text
canonical row 153
col 8
raw value 0x04
```

Position rule:

```text
x = 8 * 16 = 128
```

This **exactly matches** the runtime object dump.

## Important interpretation

The green enemy from the screenshot is now strongly explained as:

```text
LEV1MAP row 153 col 8 raw 0x04
    -> initializer 0x78D4
    -> behavior 0x8B
    -> spawn x = 128
    -> later visible as the green enemy 2X2:101..104
```

Its current screenshot Y (`192`) is not the spawn Y; the generic initializer starts at `y=16`, then behavior `0x8B` moves it.

## LEV1/Edrax decoded event codes

The first LEV1 dispatcher region around `0x77DD` statically decodes:

```text
raw 0x04 -> behavior 0x8B
raw 0x07 -> behavior 0x8C
raw 0x6C -> behavior 0x24
raw 0x6D -> behavior 0x25
raw 0xAC -> behavior 0x90
raw 0xB1 -> behavior 0x91
raw 0xC9 -> behavior 0x28
```

These have now been extracted into:

```text
research_overlays/decoded_map_events_LEV1.json
```

## What about the blue 0x2D formation?

The four blue enemies are still confirmed as:

```text
behavior 0x2D
sprites 147..150
```

But their positions are **not yet explained by the confirmed LEV1 `0x04`-style event path**.

Their only direct initializer found so far is:

```asm
7e90..7ea0 -> behavior 0x2D
```

which appears to belong to a different/high-code dispatch cluster or scripted formation path.

So the best current model is:

```text
Some enemies are LEVxMAP event codes.
Some formations may use a different scripted/formation path.
```

## New editor overlay

Added:

```text
research_overlays/decoded_map_events_LEV1.json
```

The GUI now has a Level Viewer layer for:

```text
Show decoded map events
```

These markers represent **actual decoded event cells**, not speculative runtime candidates.

## Files added

```text
archive/research/PASS72_ENEMY_MAP_EVENT_BREAKTHROUGH.md
archive/analysis/pass72/row_scanner_and_spawn_position_77ae_804e.txt
archive/analysis/pass72/lev1_dispatcher_77dd_780b.txt
archive/analysis/pass72/green_enemy_initializer_78d4_78df.txt
archive/analysis/pass72/lev1_event_positions.tsv
research_overlays/decoded_map_events_LEV1.json
```

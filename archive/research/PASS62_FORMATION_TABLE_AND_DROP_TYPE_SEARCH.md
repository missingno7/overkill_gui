# Pass62 - formation table breakthrough and drop-type search

## Goal

Continue from pass61:

```text
2X2 drop sprite = object +0x06 + 0x3B
reported c160 drop 2X2:71 => object +0x06 should be 12
```

## Drop type search result

I searched for immediate writes like:

```asm
movw $0x0C, object+0x06
```

No direct write was found.

Observed immediate writes to `object +0x06` only use small state values:

```text
0,1,2,3,4,5,6,7
```

So if `2X2:71` really comes from the `+0x06 + 0x3B` formula, then `+0x06 = 12` is probably produced through:

```text
register copy
lookup table
state conversion
or a different code path using the same formula
```

This matters because the drop type is likely not hardcoded as a simple immediate constant.

## New strong formation-table breakthrough

Found a clean 4-object spawn/formation routine:

```asm
9cf4: cmpw $0x0EA0, 0x2350
9cfa: jne  0x9d40

9d05: mov  $0xA3EE, %si
9d08: mov  $0x0004, %cx

loop:
9d0d: call 0x6b67        ; allocate/find object slot
9d16: object+0x00 = 1
9d1a: object+0x14 = 2
9d1f: object+0x16 = 4
9d24: object+0x18 = 0x53
9d29: object+0x28 = 0xFFFF

9d2e: lodsw -> object+0x02
9d32: lodsw -> object+0x04
9d36: lodsw -> object+0x08
9d3a: object+0x36 = object+0x08
9d3e: loop
```

This is a real breakthrough because it proves a concrete storage model:

```text
off-grid runtime formations can be stored as object tables:
    word y_or_screen_pos -> object +0x02
    word x_or_screen_pos -> object +0x04
    word sprite/frame    -> object +0x08
```

It creates exactly 4 objects.

## Important caveat

This trigger is:

```text
scroll variable 0x2350 == 0x0EA0
```

That may not be the c160 screenshot formation. It could be another 4-object formation elsewhere.

But structurally it is exactly the kind of system we have been looking for:

```text
runtime object formation
off-grid positions
explicit object count
table-driven x/y/sprite
not MAP-cell based
```

## Why table contents are not decoded yet

The table pointer is:

```text
DS:0xA3EE
```

In the flat unpacked EXE file, the same flat offset contains code bytes, not the DS table. So the table is in the program's runtime data segment, not directly at flat file offset `0xA3EE`.

This is the same segment-mapping issue already seen with other DS tables.

The next step is to identify how DS is laid out in memory or where that data is copied from in the unpacked EXE/archive.

## Pickup/drop formula appears again

A second related area around `0xA947` again uses:

```asm
object+0x08 = object+0x06 + 0x3B
```

Then it remaps the same `object+0x06` to other sprite ranges depending on current level `0x2356`:

```text
level 5/6/0: +0x115 / +0x105
level 1:     +0x2A
level 2:     +0xD2
level 3/4/7: +0xEC
```

This suggests `object +0x06` is a compact item/state/type value reused across several visual families.

## Updated runtime hypotheses

Updated:

```text
research_overlays/runtime_spawn_hypotheses.json
```

New entries:

```text
scroll_0xEA0_four_object_table
pickup_drop_sprite_formula pass62 update
```

## Files added

```text
archive/analysis/pass62/scroll_0xEA0_four_object_table_9cf4_9d40.txt
archive/analysis/pass62/pickup_drop_and_level_specific_sprite_a8ff_aa45.txt
archive/analysis/pass62/field06_writes_and_drop_type_search.txt
archive/analysis/pass62/scroll_0x2350_triggers.txt
archive/research/PASS62_FORMATION_TABLE_AND_DROP_TYPE_SEARCH.md
```

## Next concrete target

Find DS table `0xA3EE`.

Possible approaches:

1. Trace data segment setup and copy/decompression into DS.
2. Search for code that initializes or writes to DS:0xA3EE.
3. Correlate runtime memory address `0xA3EE` with packed EXE sections.
4. Use DOSBox debugger/memory dump at runtime and inspect DS:0xA3EE directly.

Once DS:0xA3EE is decoded, we can render the first generated off-grid object formation overlay from real data.

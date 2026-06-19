# Pass67 - c160 watch-sprite workflow and behavior caveat

## Goal

Continue from pass66's real object-pool breakthrough and make the next step practical.

## What I checked

I re-inspected the behavior dispatch table and the code region around the previously identified c160 sprite formula:

```asm
8615: mov 0x233C, ax
8618: add ax, 0x0093
861B: mov ax, object+0x08
```

This formula still perfectly produces:

```text
0x93..0x96 = 2X2 147..150
```

which matches the user-reported c160 enemies.

## Important caveat

Static control-flow does **not** show a clean behavior-table entry pointing directly to `0x8615`.

The extended behavior table has entries near the region, such as:

```text
0x26 -> 0x8302
0x27 -> 0x835D
0x28 -> 0x8676
0x29 -> 0x8721
0x2A -> 0x8676
0x2B -> 0x8715
0x7A -> 0x870C
0x7C -> 0x8707
0x8F -> 0x8769
0x9D -> 0x83D2
```

but not a direct `-> 0x8615`.

So the correct professional interpretation is:

```text
0x8615 formula is a strong sprite formula candidate,
but the owning behavior/type is not yet statically proven.
```

It may be:
- a branch/substate within a larger handler,
- an entry reached by a computed or non-table path,
- dead/alternate code,
- or a disassembly boundary artifact.

## Why the runtime object dump now matters

Instead of arguing from static control-flow, we can solve this directly:

1. Run the game until the c160 enemies are visible.
2. Dump the object pools:

```text
DS:23B4..DS:32CB
```

3. Convert with:

```bash
python tools/convert_runtime_object_dump.py dump.bin --binary \
  --watch-sprites 147,148,149,150,71 \
  -o research_overlays/runtime_object_slots.json
```

4. Open Level Viewer and enable:

```text
Show runtime object dump
```

The converter now flags watched sprites:

```text
147,148,149,150,71
```

and the GUI draws those watched objects in orange/yellow instead of regular green/cyan.

## What we expect to learn

For each c160 enemy visible in the dump:

```text
object +0x02 = exact y
object +0x04 = exact x
object +0x08 = sprite 147..150
object +0x18 = real behavior/type
object +0x06 = state/substate/drop-ish value
```

The `+0x18` value will tell us which behavior actually owns the c160 enemy, avoiding the uncertainty around `0x8615`.

For the drop:

```text
sprite 71
```

the same dump may show a pickup object with:

```text
object +0x08 = 71
object +0x06 = likely 12 if pass61 formula applies
object +0x18 = pickup/drop behavior
```

## Tool update

Updated:

```text
tools/convert_runtime_object_dump.py
```

New default watched sprites:

```text
147,148,149,150,71
```

The tool prints watched active objects after conversion.

## GUI update

Runtime object dump overlay now emphasizes watched sprites:

```text
orange/yellow = watched sprite 147..150 or 71
green/cyan = other active runtime object
```

## Added files

```text
archive/research/PASS67_C160_WATCH_SPRITE_WORKFLOW.md
archive/analysis/pass67/behavior_region_8300_8676.txt
archive/analysis/pass67/behavior_dispatch_table_decoded_extended.txt
```

## Professional next step

A runtime dump is no longer optional guesswork; it is the shortest path to exact enemy positions and behavior IDs.

If the dump contains the c160 objects, we can then trace their exact behavior backwards in disassembly and build the first real generated enemy overlay.

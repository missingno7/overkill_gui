# Pass68 - c160 runtime dump breakthrough

## Dump received

The user dumped:

```text
DS = 1F0D
MEMDUMPBIN 1F0D:23B4 F18
```

This is exactly the full runtime object-pool range:

```text
DS:23B4 .. DS:32CB
```

Length:

```text
0x0F18 bytes = 3864 bytes
```

## Active objects found

The dump contains 6 active runtime objects.

### Player / projectile-like objects

```text
A00: x=96, y=175, sprite=11,  behavior=0x00
A07: x=96, y=145, sprite=15,  behavior=0x00
```

These validate that:

```text
object+0x04 = screen/playfield X
object+0x02 = screen/playfield Y
```

### The four visible c160 enemies

Exactly four watched enemy objects were found:

```text
A14: x= 64, y=54, sprite=149, behavior=0x2D
A15: x= 80, y=50, sprite=149, behavior=0x2D
A16: x=112, y=50, sprite=149, behavior=0x2D
A17: x=128, y=54, sprite=149, behavior=0x2D
```

This matches the screenshot formation.

All four share:

```text
behavior/type       = 0x2D
state/substate +06  = 4
sprite/frame +08    = 149
class/layer +16     = 4
field +20           = 2
field +22           = 9
```

## Major conclusions

### 1. Enemy positions are real pixel positions, not MAP-grid positions

The four enemies are at:

```text
(64,54), (80,50), (112,50), (128,54)
```

Those are screen/playfield pixels, not tile-aligned MAP cells.

### 2. c160 enemy behavior is now known

The observed enemy class has:

```text
object+0x18 = 0x2D
```

This is the concrete behavior/type ID to trace in disassembly.

### 3. The sprite formula candidate remains consistent

All four currently show:

```text
sprite = 149 = 0x95
```

This lies in the user-verified animation range:

```text
147..150 = 0x93..0x96
```

So the earlier formula candidate:

```text
0x93 + animation_counter
```

still looks very plausible, but the dump now gives the harder fact:

```text
behavior 0x2D owns this live enemy formation at this moment.
```

## User correction

The user clarified:

```text
These four enemies do not drop anything.
They remain briefly and then fly downward.
```

So they should not be used for the `2X2:71` drop investigation.

## New GUI support

Added a dedicated top-level tab:

```text
Runtime Objects
```

This tab renders a `208x200` screen/playfield-coordinate preview from:

```text
research_overlays/runtime_object_slots.json
```

It also lists active object slots in a table.

Watched sprites:

```text
147,148,149,150,71
```

are highlighted in orange/yellow.

## Files added

```text
runtime_dumps/MEMDUMP_c160_enemies.bin
research_overlays/runtime_object_slots.json
archive/analysis/pass68/MEMDUMP_c160_active_objects.json
sample_previews_pass68/PASS68_runtime_object_dump_screen_space.png
sample_previews_pass68/PASS68_runtime_object_dump_screen_space_3x.png
archive/research/PASS68_C160_RUNTIME_DUMP_BREAKTHROUGH.md
```

## Next reverse-engineering target

Trace behavior `0x2D` and its initializer/spawner:

```text
object+0x18 = 0x2D
```

The dump has now turned a visual enemy into a precise code target.

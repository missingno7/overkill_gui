# Pass73 - PLAQ check and moving enemy spawn stream breakthrough

## User hypothesis checked

Hypothesis:

```text
PLAQ0.ENC..PLAQ5.ENC might be the per-level files that hold moving enemy positions/formations.
PLAQ1.ENC might correspond to LEV1MAP.BIC.
```

## Result

`PLAQ*.ENC` now looks **very unlikely** to be the moving-enemy position data.

### Why

1. All six PLAQ files share the same graphics-like opening structure.

```text
PLAQ0.ENC: 87 4f 00 13 ...
PLAQ1.ENC: 87 4f 00 13 ...
PLAQ2.ENC: 87 4f 00 13 ...
PLAQ3.ENC: 87 4f 00 13 ...
PLAQ4.ENC: 87 4f 00 13 ...
PLAQ5.ENC: 87 4f 00 13 ...
```

2. They have long identical prefixes:
- PLAQ0/1 identical for 76 bytes,
- PLAQ2/3 identical for 98 bytes,
- PLAQ3/4 identical for 98 bytes.

That is normal for same-format compressed images with similar blank/prologue data, but not what I would expect from unrelated level enemy streams.

3. The internal filename table places `plaq0.enc..plaq5.enc` next to:

```text
winscr.enc
levscr.enc
choose.enc
```

which strongly suggests screen/UI art assets.

4. The exact confirmed blue formation descriptor is **not** present in any PLAQ file.

## More important finding: moving enemies really do use a separate stream

While checking this, I found the actual architecture for moving enemies.

There is a dedicated stream parser around:

```text
0x4987 .. 0x4B96
```

It is separate from the LEVxMAP row scanner.

### Event stream model

The parser:

1. selects a per-level stream,
2. reads a trigger/progress value,
3. reads a pointer to a formation descriptor,
4. reads `base_x` and `base_y`,
5. spawns `count` enemies using pixel offsets.

The code directly writes:

```asm
object.y = base_y + dy
object.x = base_x + dx
object.behavior = descriptor.behavior
```

This is exactly the pixel-space moving-enemy layer we expected.

## Formation descriptor format

The descriptor parser matches:

```text
u16 field_14
u16 field_0A
u16 behavior
u16 count
repeat count:
    s16 dx
    s16 dy
```

## Direct confirmation: the blue 0x2D formation

In executable data I found:

```text
behavior = 0x2D
count    = 4

offsets:
    ( 0,   0)
    (16, -16)
    (48, -16)
    (64,   0)
```

The earlier runtime dump had blue enemies at:

```text
x = 64, 80, 112, 128
```

If:

```text
base_x = 64
```

then:

```text
64 + [0,16,48,64] = [64,80,112,128]
```

That is an exact formation match.

## Current model

```text
LEVxMAP.BIC
    static grid-bound terrain/object events

moving enemy event stream
    trigger + descriptor pointer + base_x/base_y

formation descriptor block
    behavior + count + pixel-space relative offsets

runtime object pool
    actual live objects
```

## What remains

The remaining missing piece is **mapping the per-level event stream records to exact level progress positions** and linking a specific stream record to the `0x2D` formation descriptor.

That should let us render a real moving-enemy overlay in the editor.

## Files added

```text
archive/research/PASS73_PLAQ_CHECK_AND_MOVING_SPAWN_STREAM.md
archive/analysis/pass73/plaq_enc_comparison.md
archive/analysis/pass73/moving_spawn_stream_4987_4b96.txt
archive/analysis/pass73/descriptor_block_135d1_136dd_hex.txt
research_overlays/moving_enemy_formation_descriptors_static.json
tools/inspect_moving_formation_descriptors.py
```

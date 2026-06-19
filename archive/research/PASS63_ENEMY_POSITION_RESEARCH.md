# Pass63 - enemy position research from disassembly

## Goal

User asked to find enemy positions in maps by looking into disassembly.

## Main result

Enemy positions are not stored in `LEVxMAP` cells. They are produced by several runtime systems:

1. table-driven formation records,
2. relative child spawns from existing objects,
3. script-pointer based clusters,
4. projectile/burst generators.

I extracted the first set of concrete formation/spawn candidates into:

```text
research_overlays/runtime_formation_candidates.json
```

## Best current position-storage candidate

The strongest table-driven candidate remains:

```asm
9cf4: cmpw $0x0EA0, 0x2350
9cfa: jne  0x9d40

9d05: mov  $0xA3EE, %si
9d08: mov  $0x0004, %cx
```

Then for each of 4 objects:

```asm
call 0x6b67        ; allocate object slot

object+0x18 = 0x53

lodsw -> object+0x02
lodsw -> object+0x04
lodsw -> object+0x08
object+0x36 = object+0x08
```

This is a direct enemy/object position table shape:

```text
record word 0 -> object +0x02
record word 1 -> object +0x04
record word 2 -> object +0x08 sprite/frame
```

## Why actual positions are not decoded yet

The table is referenced as:

```text
DS:0xA3EE
```

But the flat unpacked EXE at file offset `0xA3EE` contains code bytes, not four coordinate records.

I checked:
- raw file offset `0xA3EE`,
- `0xA3EE + MZ header size`,
- `0xA3EE - MZ header size`,
- references/writes to `DS:0xA3EE`.

Result:

```text
No static write references to DS:0xA3EE were found.
```

So `DS:0xA3EE` is likely runtime data:
- copied/decompressed into memory,
- generated during runtime,
- or located through a DS segment mapping that is not flat-file == DS offset.

This means we need either:
- a runtime DOSBox memory dump,
- or more segment/copy tracing.

## Other position systems found

### 0xAA45..0xAAAA: 8-object relative burst

This routine creates 8 objects:

```asm
child+0x04 = parent+0x04 + dx
child+0x02 = parent+0x02 + dx
child+0x06 = loop_index - 1
child+0x08 = loop_index + 8
child+0x18 = 0x03
```

where:

```text
dx = 0x0C if parent+0x14 == 2 else 0x04
```

This is not map-position storage; it is a runtime relative burst/projectile/fragment generator.

### 0xB8A2..0xB8E5: relative child spawn

This creates a child object relative to parent:

```asm
child+0x04 = parent+0x04 + 4 or 12
child+0x02 = parent+0x02 + 4 or 12
child+0x08 = 0x30
child+0x18 = 0x04
```

### 0x9A0D..0x9A5D / 0x99BB..0x9A0C: runtime script-pointer cluster

This area reads pointers like:

```text
DS:0xA962
DS:0xA964
DS:0xA966
DS:0xA968
DS:0xA96A
DS:0xA96C
```

then uses `SI+0x02` and `SI+0x04` as object positions.

This looks like another runtime object/spawn cluster mechanism, but those pointers are also runtime DS values.

## Important implication for GUI overlay

A real generated enemy overlay needs one of these:

1. decoded DS formation tables, or
2. runtime object memory snapshot, or
3. a reconstructed simulation of the spawning code.

Until then, the best GUI layer is:
- manual verified observations,
- runtime formation candidates,
- scroll trigger lines,
- and eventually loaded memory-dump markers.

## Added files

```text
research_overlays/runtime_formation_candidates.json
archive/analysis/pass63/formation_candidate_scan.txt
archive/analysis/pass63/scroll_0xEA0_table_context.txt
archive/analysis/pass63/relative_8_object_burst_aa45_aaaa.txt
archive/analysis/pass63/relative_child_spawn_b8a2_b8e5.txt
archive/analysis/pass63/script_pointer_cluster_99bb_9a5d.txt
archive/research/PASS63_ENEMY_POSITION_RESEARCH.md
```

## Next practical step

The most practical next move is to dump runtime memory from DOSBox/debugger around DS:0xA3EE while level 1 is running.

If we can get bytes at:

```text
DS:0xA3EE .. DS:0xA405
```

we can decode the first 4-object formation table immediately:

```text
4 records * 3 words = 24 bytes
```

and render it in the GUI as a real overlay.

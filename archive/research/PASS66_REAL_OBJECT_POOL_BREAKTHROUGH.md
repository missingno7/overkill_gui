# Pass66 - real object pool breakthrough

## Professional breakthrough

Instead of chasing speculative formation rows, I traced the live object loop and allocator patterns.

The game has two contiguous runtime object pools in DS memory.

## Object pools

From the allocator/update code:

```asm
738a: b9 23 00        mov cx,0x23
738d: mov bx,[0x95D8]
...
7396: add bx,0x38
7399: cmp bx,0x2B5C
739f: mov bx,0x23B4

73b6: b9 22 00        mov cx,0x22
73b9: mov bx,0x2B5C
...
73d9: b9 22 00        mov cx,0x22
73e0: cmp bx,0x32CC
73e6: mov bx,0x2B5C
```

And the main object update loop uses the same pools/pointer ranges:

```asm
9e89: mov cx,0x24
9e91: mov bp,[0x32CA + bx]
9e9b: call 0x510B

9ea1: mov cx,0x22
9ea9: mov bp,[0x8D12 + bx]
9eb3: call 0x510B
```

The key concrete result:

```text
object slot size = 0x38
Pool A = DS:0x23B4 .. DS:0x2B5B, 35 slots
Pool B = DS:0x2B5C .. DS:0x32CB, 34 slots
```

## Why this is better than the previous candidates

The old magenta candidates tried to infer positions from scroll triggers.
That was too speculative.

This is now a direct way to get real positions:

```text
dump the live object pools while enemies are visible
parse every active object slot
draw object+0x04 / object+0x02 as x/y
show object+0x08 sprite and object+0x18 behavior
```

For the c160 screenshot, this should immediately show the four active objects using:

```text
sprite 147..150
behavior ? unknown
x/y actual runtime positions
```

## Object struct fields

Known/strong fields:

```text
+0x00 active flag
+0x02 y / vertical position
+0x04 x / horizontal position
+0x06 state / drop type / animation substate
+0x08 sprite / frame
+0x16 class/layer-ish
+0x18 behavior/type dispatch
+0x32 target/aux y
+0x34 target/aux x
+0x36 sprite backup / aux
```

## GUI update

Added a new overlay:

```text
Show runtime object dump
```

It reads:

```text
research_overlays/runtime_object_slots.json
```

and draws active objects as green/cyan crosshair markers with labels:

```text
pool/slot sprite behavior
```

## New converter tool

Added:

```text
tools/convert_runtime_object_dump.py
```

Usage:

```bash
python tools/convert_runtime_object_dump.py dump.bin --binary -o research_overlays/runtime_object_slots.json
```

or for a text hex dump:

```bash
python tools/convert_runtime_object_dump.py dump_hex.txt -o research_overlays/runtime_object_slots.json
```

## Runtime dump target

Dump this memory range while the desired enemies are visible:

```text
DS:23B4 .. DS:32CB
```

Length:

```text
0x0F18 bytes
```

This covers:

```text
Pool A: 35 slots
Pool B: 34 slots
```

## Why this should move us forward

We no longer need to guess if c160 enemies are in MAP cells, scroll candidates, or hidden BIC payloads.

If we can get one dump while those four enemies are on screen, we can read their live object structs:

```text
x/y position
sprite = 147..150
behavior type
state/drop fields
```

Then we can trace backwards from that exact behavior to the spawn code.

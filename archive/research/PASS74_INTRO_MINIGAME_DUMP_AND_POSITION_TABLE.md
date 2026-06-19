# Pass74 - Level 1 intro minigame dump and position table

## Dump decoded

The uploaded dump from the Level 1 intro minigame is valid:

```text
dump target: SS:23B4..SS:32CB
size:        0x0F18 bytes
```

It contains:

```text
active runtime objects: 22
behavior 0x20 enemies: 20
behavior 0x1F controller-like object: 1
```

## Active objects

```text
A00: x= 96, y=217, sprite= 10, behavior=0x00, state=0, class=6
A01: x=  0, y=232, sprite= 63, behavior=0x1F, state=4, class=4
A02: x=144, y= 96, sprite=123, behavior=0x20, state=4, class=4
A03: x=128, y= 96, sprite=123, behavior=0x20, state=4, class=4
A04: x=128, y= 80, sprite=123, behavior=0x20, state=4, class=4
A05: x=144, y= 80, sprite=123, behavior=0x20, state=4, class=4
A06: x=112, y= 64, sprite=123, behavior=0x20, state=4, class=4
A07: x= 80, y= 64, sprite=126, behavior=0x20, state=4, class=4
A08: x= 64, y= 80, sprite=126, behavior=0x20, state=4, class=4
A09: x= 48, y= 80, sprite=126, behavior=0x20, state=4, class=4
A10: x= 48, y= 96, sprite=126, behavior=0x20, state=4, class=4
A11: x= 64, y= 96, sprite=126, behavior=0x20, state=4, class=4
A12: x= 16, y= 80, sprite=126, behavior=0x20, state=4, class=4
A13: x= 16, y= 64, sprite=126, behavior=0x20, state=4, class=4
A14: x= 16, y= 48, sprite=126, behavior=0x20, state=4, class=4
A15: x= 32, y= 48, sprite=126, behavior=0x20, state=4, class=4
A16: x= 48, y= 48, sprite=126, behavior=0x20, state=4, class=4
A17: x=144, y= 48, sprite=123, behavior=0x20, state=4, class=4
A18: x=160, y= 48, sprite=123, behavior=0x20, state=4, class=4
A19: x=176, y= 48, sprite=123, behavior=0x20, state=4, class=4
A20: x=176, y= 64, sprite=123, behavior=0x20, state=4, class=4
A21: x=176, y= 80, sprite=123, behavior=0x20, state=4, class=4
```

## Important runtime interpretation

The 20 visible intro-minigame enemies are:

```text
behavior = 0x20
sprites  = 123 or 126 in this snapshot
```

There is also:

```text
A01: behavior 0x1F, sprite 63, x=0, y=232
```

which is a strong controller/parent candidate for the intro-wave spawning logic.

## Static code path

The relevant spawn branch is:

```asm
DD81: add [A482], 4
DD86: CX = 5
DD8A: allocate object
DD92: SI = [A842]
DD96: [A842] += 4
DDA0: AX = [SI] ; stored_y_minus_0x20
DDA1: AX += 0x20
DDA4: object+0x34 = AX
DDA7: AX = [SI+2] ; x
DDA8: object+0x32 = AX
DDAB: object+0x18 = 0x20
```

This branch creates enemies in batches of 5.

## Exact hardcoded minigame position table

The executable contains the exact 20-position table at raw EXE offset:

```text
0x11161
```

The preceding little-endian word:

```text
44 A8 = 0xA844
```

is consistent with the runtime variable `DS:A842` initially pointing at `DS:A844`.

The table record format is:

```text
s16 stored_y_minus_0x20
s16 x
```

and runtime Y is:

```text
y = stored_y_minus_0x20 + 0x20
```

## Exact table/runtime match

```text
00: runtime x=144, y= 96 | table x=144, y= 96
01: runtime x=128, y= 96 | table x=128, y= 96
02: runtime x=128, y= 80 | table x=128, y= 80
03: runtime x=144, y= 80 | table x=144, y= 80
04: runtime x=112, y= 64 | table x=112, y= 64
05: runtime x= 80, y= 64 | table x= 80, y= 64
06: runtime x= 64, y= 80 | table x= 64, y= 80
07: runtime x= 48, y= 80 | table x= 48, y= 80
08: runtime x= 48, y= 96 | table x= 48, y= 96
09: runtime x= 64, y= 96 | table x= 64, y= 96
10: runtime x= 16, y= 80 | table x= 16, y= 80
11: runtime x= 16, y= 64 | table x= 16, y= 64
12: runtime x= 16, y= 48 | table x= 16, y= 48
13: runtime x= 32, y= 48 | table x= 32, y= 48
14: runtime x= 48, y= 48 | table x= 48, y= 48
15: runtime x=144, y= 48 | table x=144, y= 48
16: runtime x=160, y= 48 | table x=160, y= 48
17: runtime x=176, y= 48 | table x=176, y= 48
18: runtime x=176, y= 64 | table x=176, y= 64
19: runtime x=176, y= 80 | table x=176, y= 80
```

These 20 table records **exactly match** the 20 visible behavior-`0x20` runtime enemies from the dump.

## Conclusion

The Level 1 intro "Space Invaders" minigame has its own hardcoded positional data in executable data, separate from:

```text
LEV1MAP.BIC grid events
moving-enemy scrolling-level formation descriptors
```

So we now have three distinct object-placement systems:

```text
1. LEVxMAP event bytes
   - static/grid-bound level objects

2. moving-enemy spawn stream + formation descriptors
   - scrolling-level mobile enemy formations

3. intro-minigame hardcoded position table
   - Level 1 opening wave, behavior 0x20
```

## Files added

```text
runtime_dumps/MEMDUMP_intro_minigame_level1.bin
research_overlays/runtime_object_slots_intro_minigame.json
research_overlays/intro_minigame_level1_enemy_position_table.json
sample_previews_pass74/PASS74_intro_minigame_runtime_objects_3x.png
archive/research/PASS74_INTRO_MINIGAME_DUMP_AND_POSITION_TABLE.md
```

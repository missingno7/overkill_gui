# Pass55 - deeper enemy encoding research

## Key user clue

At LEV1:

    display row = 162
    canonical row = 125
    col = 2
    MAP raw = 0x01

But the game shows an enemy there using:

    2X2 sprites 68, 69, 70

and after killing it drops:

    2X2 sprite 71

This proves the enemy is not encoded as a direct visible special MAP value in that cell.

## Main conclusion

The enemy layer is not solved by LEV1MAP special markers.

The MAP contains terrain/background and some special commands, but this specific enemy is almost certainly produced by the runtime object system.

## Why no special marker appears

The clicked cell is raw 0x01.

The MAP-special dispatcher found in disassembly handles high/special raw codes, e.g.:

    0x30
    0xB6
    0xBA..0xBC
    0xD2,0xD3,0xD7,0xD8
    range around 0xD7..0xF1 via jump table / dispatch

It does not explain a raw 0x01 cell.

Therefore absence of special markers in LEV1 around that point is expected.

## What was found for sprites 68..70

2X2 indices:

    68 = 0x44
    69 = 0x45
    70 = 0x46
    71 = 0x47

Disassembly contains relevant object sprite writes:

    0x8605: [object+0x08] = 0x44
    0x7cda: [object+0x08] = 0x46
    0x86e0: [object+0x08] = table_value + 0x44

This is strong evidence that object field `+0x08` is sprite/frame-ish and that sprites 68..70 are selected by runtime code.

## Important correction about 0x92 / 0x93

Values like 0x92 and 0x93 appear in object behavior field `+0x18`, not necessarily as MAP sprite values:

    0x7cf0: [object+0x18] = 0x92
    0x7d06: [object+0x18] = 0x92
    0xde86: [object+0x18] = 0x93

So using MAP raw 0x92/0x93 as sprite mapping was misleading.

## About the drop 2X2:71

No direct write was found for:

    [object+0x08] = 0x47

There is:

    0x7eac: [object+0x18] = 0x47

but `+0x18` is behavior/type, not sprite.

Also:

    0xabd2: [object+0x08] = 0x71

but `0x71` is decimal 113, not decimal 71.

So the drop sprite 71 is probably selected indirectly through a table or computed frame/pickup routine.

## Added analysis files

See:

    archive/analysis/pass55/enemy_system_summary.md
    archive/analysis/pass55/map_special_dispatch_7b80_7d60.txt
    archive/analysis/pass55/sprite_44_46_enemy_routines_85c0_8720.txt
    archive/analysis/pass55/possible_pickup_drop_runtime_ab90_ac10.txt
    archive/analysis/pass55/runtime_object_child_spawn_b8bd_b9e5.txt
    archive/analysis/pass55/later_pickup_object_logic_de50_e0a0.txt
    archive/analysis/pass55/field08_and_field18_immediates.txt

## Next step

The next proper parser is not a MAP overlay.
It should be a reconstructed runtime spawn/event layer.

Need to trace:
    object allocation calls 0x802f / 0xc09d / 0xa460
    object fields +0x02/+0x04 coordinates
    +0x08 sprite/frame
    +0x18 behavior type
    scroll variables such as 0x232a/0x232e/0x233c
    current level variable 0x2356

Then we can generate an enemy/spawn overlay from script/runtime data instead of raw MAP values.

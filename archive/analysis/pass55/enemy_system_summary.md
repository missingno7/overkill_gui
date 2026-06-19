# Pass55 enemy-system disassembly summary

## Important object struct fields seen repeatedly

The same object slot struct pattern appears across routines:

    +0x00 active/used flag
    +0x02 y / vertical position-ish
    +0x04 x / horizontal position-ish
    +0x06 animation/state variant
    +0x08 sprite/frame index-ish
    +0x16 dispatch class
    +0x18 behavior/object type
    +0x20 speed/timer-ish
    +0x32/+0x34 target/destination-ish

## Concrete findings relevant to the reported LEV1 enemy

Reported enemy:
    location: LEV1 display row 162 / canonical row 125 / col 2
    clicked MAP value: 0x01
    visible sprites: 2X2 68,69,70
    drop: 2X2 71

Important conversion:
    68 = 0x44
    69 = 0x45
    70 = 0x46
    71 = 0x47

## Why MAP special markers do not show it

The clicked MAP cell is raw 0x01, a normal terrain/empty value.
The disassembly shows a MAP-special-object dispatcher around 0x7c2e, but it handles high/special raw codes such as:

    0x30
    0xB6
    0xBA..0xBC
    0xD2,0xD3,0xD7,0xD8
    and a jump-table-like range around 0xD7..0xF1

It does not explain an enemy located at a raw 0x01 terrain cell.

So this enemy is almost certainly not encoded as a visible special value in LEV1MAP at that exact cell.

## Strong sprite evidence

The EXE does contain writes to object field +0x08 using the sprite values involved:

    0x8605: mov [bx+0x08], 0x44   ; 2X2 sprite 68
    0x7cda: mov [bx+0x08], 0x46   ; 2X2 sprite 70
    0x86e0: +0x44 is added to a table-derived value and stored into [bp+0x08]

This strongly suggests that 2X2 sprite IDs 68..70 are selected by enemy behavior/runtime code, not directly read from the clicked MAP cell.

There is no direct immediate write found for:

    [object+0x08] = 0x47

So the reported 2X2 sprite 71 drop is probably selected indirectly:
- by a lookup table,
- by adding an offset to a state/drop value,
- or by a routine where +0x08 is computed rather than written as an immediate.

## Behavior/type evidence

Several routines set field +0x18, which appears to be behavior/object type, not sprite:

    0x7cf0: [bx+0x18] = 0x92, [bx+0x08] = 0x15a
    0x7d06: [bx+0x18] = 0x92, [bx+0x08] = 0x15b
    0xde86: [bp+0x18] = 0x93
    0x7eac: [bx+0x18] = 0x47

This is important:
    0x47 appears as a behavior/type value, not as a direct sprite field write.

So do not assume every 0x47 in the EXE means sprite 71.

## Candidate routines

### 0x7c2e / 0x7c80 area

This looks like a MAP special-code dispatcher. It reads AL, compares it against special raw map codes, allocates an object with 0x802f, and initializes fields.

Example:

    0x7cda:
        [bx+0x08] = 0x46
        [bx+0x18] = 0x30
        [bx+0x06] = 0x04

This is probably a map-command-created object, but it is not the raw 0x01 enemy case.

### 0x85cf / 0x8605 / 0x86e0

This is more interesting for the visible 68..70 enemy.

It computes frame values from runtime variables/tables:

    0x85cf:
        bx = [0x232e] >> 3
        bx = word table[-0x693e + bx*2]
        bx += 0xbf
        [bp+0x08] = bx

    0x8605:
        child/new object [bx+0x08] = 0x44

    0x86e0:
        bx = word table[-0x692e + [0x233c]*2]
        bx += 0x44
        [bp+0x08] = bx

That suggests runtime animation/frame selection, not map value -> sprite value.

### 0xabcd / 0xabd2

This sets:

    [bp+0x18] = 0x22
    [bp+0x08] = 0x71

Careful:
    0x71 decimal is 113, not 2X2 sprite 71.
This may still be a pickup/bonus-related routine, but it is not direct evidence for 2X2 index 71.

## Current model

Current best model:

    LEVxMAP/BLX:
        terrain/background and some special map command markers

    Runtime object system:
        creates enemies/spawns using EXE logic and object slots

    Sprite rendering:
        object +0x08 controls sprite/frame or an index into a render table

    Behavior:
        object +0x18 controls behavior/object type

The reported enemy in blank/terrain area is probably a runtime object whose position is based on scroll/time/level-script logic, not a direct MAP cell value.

## Next research target

Trace the routine that sets object +0x08 to values 0x44..0x46 and connect it to:
    - scroll position variables,
    - level id variable 0x2356,
    - object allocation calls 0x802f / 0xc09d / 0xa460,
    - and behavior field +0x18.

Then reconstruct a spawn/event layer as a sequence of:
    scroll_y / trigger
    x
    y
    behavior type
    sprite base/frame
    drop rule

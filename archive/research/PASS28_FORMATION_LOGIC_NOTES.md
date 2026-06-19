# Overkill RE pass28 - formation/minigame logic deeper notes

## Summary

The pre-level Space-Invaders-like part is very likely implemented as object-state logic in the EXE,
not as LEVxMAP tiles.

The important distinction is now:

1. Formation / pre-level phase:
   - empty starfield / no BLX tilemap
   - enemy waves created by timed object spawners
   - driven by object state machine and global counters

2. Main scrolling level:
   - LEVnMAP + LEVnBLX background
   - 13 x 288 tile cells
   - raw MAP values in range 1..tile_count are direct 1-based tile IDs
   - out-of-range values are special/unknown only in some levels

## Strong object system clues

### Object list size

The main object loop uses `cx = 0x23`, so about 35 object slots:

    a020: mov $0x23,%cx
    ...
    a028: mov 0x32ca(%bx),%bp
    ...
    a044: call 0xa06e

The dispatch routine uses object field +0x16 as a state class:

    a06e: mov 0x16(%bp),%bx
    a073: jmp *%cs:-0x55ca(%bx)

So objects are state-machine driven.

### Object struct fields

Repeated patterns indicate a 0x38-byte object structure:

- +0x00 active
- +0x02 y or vertical position
- +0x04 x or horizontal position
- +0x06/+0x08 sprite/animation frame fields
- +0x14 side/type group
- +0x16 state dispatch class
- +0x18 behavior/object type
- +0x1c substate/variant/counter
- +0x20 movement/direction/speed
- +0x28 often 0xffff
- +0x32/+0x34 target position / stored destination

The code repeatedly increments object pointer by 0x38 in collision/object loops.

## Candidate formation spawn

The routine around `0xaa45` creates a group of eight objects:

    aa61: mov $0x8,%cx
    aa65: call 0x6bb6       ; allocate/find object
    aa70: mov %cx,0x6(%bx)
    aa76: mov %cx,0x8(%bx)
    aa79: mov 0xa8b2,%ax
    aa7c: mov %ax,0x4(%bx)
    aa7f: mov 0xa8b4,%ax
    aa82: mov %ax,0x2(%bx)
    aa85: movw $0x1,(%bx)   ; active
    aa98: movw $0x2,0x16(%bx)
    aa9d: movw $0x3,0x18(%bx)
    aaa2: movw $0xffff,0x1c(%bx)

This is highly consistent with a formation/wave spawn:
- 8 objects at once
- same base position from `a8b2/a8b4`
- loop counter used for frame/slot fields
- behavior type/state set uniformly

## Timed wave gates

The variable at `0xa7a0` is incremented each frame:

    5e92: incw -0x5860

Spawn logic tests this counter against thresholds:

    aace: cmpw $0x32,-0x5860   ; 50
    aad8: cmpw $0x5a,-0x5860   ; 90

    abb7: cmpw $0xc8,-0x5860   ; 200
    abc2: cmpw $0xf0,-0x5860   ; 240

This looks like timed wave/formation phases.

## Level-specific formation branches

Several sections branch by current level `0x2356`.

Example around `ab99..abcd`:

    if level == 4: jump 0x83c6
    if level == 3: jump 0xaace
    if level == 0: jump 0xaae5
    otherwise:
        if frame < 200: jump 0xac58
        if frame < 240: do nothing / wait
        else set object behavior and speed based on level

So pre-level behavior is level-specific.

## Spawn-position / destination logic

The routine around `acb6` reads from a pointer at `0xa894`:

    acb6: mov -0x576c,%si        ; SI = [a894]
    acba: cmp $0xa8b2,%si
    acc0: movw $0xa896,-0x576c  ; wrap pointer
    acca: lodsw
    accb: mov %ax,0x32(%bx)
    acce: mov %si,-0x576c

This is probably a cyclic table of target X/Y positions or destination coordinates for formation enemies.
Because the raw file offset is not directly reliable for interpreting this table, this needs DOS memory/runtime mapping or further static segment analysis before extracting clean coordinates.

## Why the previous "beginning of EDRAX" screenshot does not match LEV1MAP

The screenshot shows:
- mostly empty starfield
- player ship and enemies
- no heavy LEV1 tilemap background
- possibly a few formation objects / enemy wave

That matches the pre-level object phase, not `LEV1MAP row 0`.

Therefore:
- do not calibrate LEV1MAP row 0 against that screenshot
- the tilemap editor should represent the scrolling phase
- the formation editor needs separate object-wave logic

## Next tasks

1. Identify exact state transition from formation phase to scrolling tilemap phase:
   - watch variables 0x2384, 0x2350, 0xa7a0, 0xa97a, 0xa47c
   - especially code around 0x8d77, 0x8dea, 0x8f45, 0x9081, 0x9171

2. Decode object allocation routine names:
   - 0x6bb6 / 0x6b67 / 0x738a appear in object creation/collision/lookup logic.

3. Extract formation tables:
   - resolve runtime addresses around 0xa894, 0xa896, 0xa8b2
   - avoid treating raw file offsets as direct tables until segment mapping is verified.

4. GUI idea:
   - Add level structure tab:
       Phase A: Pre-level formation/waves
       Phase B: Scrolling MAP

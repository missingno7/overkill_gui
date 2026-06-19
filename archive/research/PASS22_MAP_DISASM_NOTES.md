# Overkill RE pass22 - deeper MAP / object / flag research

## Key conclusion

MAP is not "only tiles", but the current evidence says the high bit is not directly "enemy id".
It is too common and follows terrain patterns. The safe render path remains:

    visual_tile = (map_byte & 0x7f) - 1

but the original byte must be preserved for behavior.

## Important disassembly clues

### 1) The game has a 3744-byte MAP counter

The value 0x0EA0 appears as a boundary against address 0x2350:

    cmpw $0xea0, 0x2350
    movw $0xea0, 0x2350

0x0EA0 = 3744 = 13 × 288, exactly the decoded LEVxMAP size.

This strongly suggests 0x2350 is a map buffer pointer/counter/remaining length for level map streaming.

### 2) The game scrolls / consumes 13 map bytes at a time

There are routines that add/subtract 0x0D to/from 0x2350:

    addw $0xd, 0x2350
    subw $0xd, 0x2350

0x0D = 13 columns, matching one map row.
This supports the model:

    LEVxMAP = 13 columns × 288 rows

### 3) There is a 0x2340 counter up to 0x05DC

0x05DC = 1500 decimal.

Code pattern:

    incw 0x2340
    cmpw $0x5dc, 0x2340
    if >= then reset 0x2340 to 0

This is probably not a tile index. It looks more like a global timing/scroll/object sequencing counter.

### 4) There is explicit 0x7F masking

Several routines mask values with 0x7F:

    andw $0x7f, 0x2330
    and ax, 0x7f

This is consistent with treating high bit separately.

### 5) 0x2356 looks like current level/theme id

0x2356 is compared against 0..6 repeatedly and is used to select level-specific behavior.
This likely stores current level number / theme index / game section.

## Enemy/object implication

Enemies/pickups are probably not encoded as simply:

    map_byte >= 128 => enemy

More likely:

- MAP gives background tile low7 plus behavior flag highbit.
- Enemy/object spawns are controlled by separate code tables and global counters.
- Some map bytes may still mark special cells, but the object type likely comes from a table or state machine, not directly from the high-bit value.
- The 2X2/2X2C/G/SHIP graphics are sprite assets; spawn scripts are probably embedded in EXE tables or another resource, not obvious by resource name.

## Current working renderer rule

For editor background rendering:

    tile_id = (map_byte & 0x7f) - 1

For editor data preservation:

    keep original map_byte unchanged

For UI:

    show flags:
        high_bit = bool(map_byte & 0x80)
        raw_value = map_byte
        tile_low7 = map_byte & 0x7f

## Next concrete tasks

1. Add a MAP inspector overlay:
   - normal background render
   - high-bit overlay
   - raw value tooltip/grid display

2. Find the exact routine that consumes MAP rows:
   - follow references to 0x2350
   - identify where bytes are read from the decoded LEVxMAP buffer

3. Find enemy/object spawn tables:
   - inspect jump tables around 0xA06E / 0xAA36 and 0xACxx
   - inspect structures referenced through BP fields:
       offset +0x02, +0x04 = probably x/y
       offset +0x18 = object state/type
       offset +0x1c = substate/animation/variant
       offset +0x20 = direction/speed/flag
       offset +0x32/+0x34 = target/current coordinates

4. Keep MAP/BLX pairing manual until resource mapping is proven.

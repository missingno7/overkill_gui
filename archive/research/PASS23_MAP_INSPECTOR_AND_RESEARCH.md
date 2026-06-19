# Overkill RE pass23 - MAP inspector + scroll/object research

## GUI change

MAP previews now show a side-by-side inspector:

- left: background render using `tile = (byte & 0x7f) - 1`
- right: MAP diagnostic overlay
  - red = byte has high bit set
  - gray = nonblank low7 visual tile
  - black = blank/background low7 tile
  - blue horizontal lines every 16 map rows

This keeps the important distinction:
- low7 is useful for visual background
- original byte must be preserved because high bit is gameplay/tile behavior data

## Important research update

The MAP data is very likely streamed row-by-row.

Disassembly evidence:

- `0x0EA0 = 3744 = 13 × 288`
- `0x009C = 156 = 13 × 12`

The code initializes a counter/pointer:

    movw $0xea0, 0x2350

Then repeatedly calls a routine until:

    cmpw $0x9c, 0x2350

This suggests the engine starts with the full 13×288 map and consumes rows until only about 12 visible rows remain.
That matches a vertical shooter viewport of roughly 12-13 tile rows.

There are also row-step operations:

    addw/subw $0xd, 0x2350

where 0x0D = 13 columns.

## Meaning of high bit

High bit is still not decoded semantically.

It is probably not direct enemy ID because:
- too many cells have it,
- the pattern follows terrain bands,
- the game explicitly masks low7 in places.

Current hypothesis:

    byte & 0x7f = tile id / behavior id
    byte & 0x80 = flag bit used by collision/priority/animation/special tile logic

Enemies/spawns likely use separate object/state logic in EXE, though MAP may still participate through special cells or timing.

## Useful variables from disassembly

- `0x2350`: map stream pointer/counter; bounded by 0x0EA0 and stepped by 13.
- `0x2356`: current level/theme id; compared against 0..6 repeatedly.
- `0x2330`: 7-bit cyclic counter; masked with 0x7f.
- `0x2340`: larger global/object timing counter; wraps around 0x05DC.
- `0x2324..0x233e`: many cyclic animation counters with masks 1,3,7,15,31,63,127.
- Object structs use BP-relative fields like +0x02/+0x04 position, +0x18 type/state, +0x1c variant/substate.

## Next targets

1. Follow the routine called from the map bootstrap loop around `0x5f2b..0x5f43`.
2. Locate where the map byte itself is read from the decoded LEVxMAP buffer.
3. Identify what tests the high bit.
4. Add mouse-cell inspector to GUI: x/y, raw byte, low7 tile id, high bit.
5. Keep MAP/BLX pairing manually selectable until the exact resource mapping is proven.

# Overkill RE pass20 - MAP tile IDs use low 7 bits

## Breakthrough

The MAP/BLX mismatch is mostly explained by the high bit in MAP bytes.

Previous wrong interpretation:
    tile_index = value - 1

Corrected working interpretation:
    tile_index = (value & 0x7f) - 1

So MAP values 128..255 are not out-of-range tile IDs. They are tile IDs with a high-bit flag.

Examples:
    215 -> 0xD7 -> low7 = 87
    228 -> 0xE4 -> low7 = 100
    249 -> 0xF9 -> low7 = 121

This explains why every LEVxMAP has `max low7 = 127` even when raw max values are 199..249.

## What the high bit probably is

Not proven yet. Candidate meanings:
- collision/solid flag
- animated/foreground/priority bit
- object/special marker
- alternate drawing layer

The important part for background rendering is:
    ignore high bit for tile selection.

## Result

With low7 mapping, LEV0MAP + LEV1BLX renders a clean EDRAX-style tech/lava level with no missing tiles.

## Still unresolved

- exact MAP -> BLX resource pairing is not proven
- the high-bit flag semantics need to be found in disassembly
- there may be additional object/enemy data elsewhere
- G0/G3 and ENC still need more work

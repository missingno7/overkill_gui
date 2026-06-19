# Overkill RE pass21 - MAP is mixed data, not only background tiles

## Important correction

The MAP files should not be treated as pure background tile arrays.

The low 7 bits work well for visual background rendering:

    visual_tile = (map_byte & 0x7f) - 1

But the high bit is probably not simply "enemy".
It appears too frequently and is spread across terrain-like horizontal structures.
So it is more likely a tile/cell flag such as:

- collision / solid
- priority / foreground
- animated tile marker
- special tile behavior
- possible gameplay flag used by object/spawn code

## Evidence

All MAP files have many high-bit values:

- LEV0MAP: 731 / 3744 cells = 19.5%
- LEV1MAP: 448 / 3744 cells = 12.0%
- LEV2MAP: 496 / 3744 cells = 13.2%
- LEV3MAP: 818 / 3744 cells = 21.8%
- LEV4MAP: 745 / 3744 cells = 19.9%
- LEV5MAP: 774 / 3744 cells = 20.7%

This is too many for direct enemy instances, and the overlay pattern follows terrain bands.
So high-bit cells are likely map/tile flags, not direct enemies.

## Enemy / object hypothesis

Enemies and pickups may still be connected to the map, but probably in one of these ways:

1. Specific MAP byte ranges encode objects/spawns, while low7 remains background fallback.
2. High bit marks "special cell"; the low7 value selects a special table entry.
3. Object spawns are stored in another resource, and MAP only provides collision/background.
4. The game derives spawns from MAP plus a separate script/table in EXE or another BIC/ENC resource.

## Disassembly clues

There are routines in the unpacked EXE that mask values with 0x7f:

    and ax, 0x7f
    cmp ax, [...]

This supports the idea that the game deliberately strips the high bit in some logic.

## Added diagnostics

sample_previews/all_MAP_highbit_overlay_contact.png

Red cells = map byte has high bit set.
Gray cells = non-empty low7 tile IDs.
Black cells = blank / tile 1-like background.

Next step:
- trace where map bytes are read in disassembly,
- identify the logic that does `& 0x7f`,
- find what tests the high bit,
- search for object/spawn tables keyed by MAP position or by low7 tile IDs.

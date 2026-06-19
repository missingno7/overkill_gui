# Overkill RE pass25 - MAP high values and BLX orientation

## User-provided clue

LEV1BLX is EDRAX, the first game level.

Tiles that appear in the map as raw values 201, 202, 203, 204 are visibly used as vertical/top-bottom pairs in-game.
In the data, these are high-bit MAP values, not BLX indices above 200.

## Important correction to MAP byte -> tile index

Earlier render rule was:

    tile_index = (map_byte & 0x7f) - 1

This is wrong for high-bit values.

Corrected rule:

    if map_byte >= 0x80:
        tile_index = map_byte - 0x80
    else:
        tile_index = map_byte - 1

Examples:

    raw 201 = 0xC9 -> tile index 73
    raw 202 = 0xCA -> tile index 74
    raw 203 = 0xCB -> tile index 75
    raw 204 = 0xCC -> tile index 76

This fixes the off-by-one for flagged cells.

Interpretation:
- low range 1..127 is 1-based tile index
- high range 128..255 is flagged direct tile index
- high bit means "flagged cell", but the remaining 7 bits are zero-based, not one-based

## BLX orientation clue

The BLX tile sheet itself appears stored in a rotated/reflected orientation compared with how the tile is mentally viewed in the game.
The candidate transform suggested by the user is:

    rotate 90 degrees left
    then flip vertically

This transform makes the 201/202/203/204-style components line up much more naturally as vertical pairs.
However, the full level render using untransformed tiles already has coherent structures, so this may be:
- a tile-sheet display orientation issue,
- a coordinate convention issue,
- or the game drawing tiles using a rotated memory layout.

For the editor, the safest next UI is to expose tile display transform as a toggle:
- raw BLX orientation
- game-view orientation candidate

## What changed in code

The pass25 GUI updates MAP tile lookup to:

    map_value_to_tile_index(value)

with the corrected high-value rule above.

## Added previews

- pass25_LEV1_tiles_201_204_transforms.png
- pass25_LEV1_level_transform_compare.png
- pass25_map_index_rules_compare.png
- pass25_raw201_204_neighborhoods_flag_direct.png

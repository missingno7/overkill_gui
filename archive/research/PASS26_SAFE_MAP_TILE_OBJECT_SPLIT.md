# Overkill RE pass26 - safe MAP tile/object separation and EDRAX calibration

## User screenshot

The provided screenshot is from the beginning of game level 1 EDRAX.
EDRAX is resource level 1:

    LEV1MAP.BIC + LEV1BLX.BIC + G1.BIC

## Important correction

The earlier high-bit rule was too aggressive.

For EDRAX:

    LEV1MAP max raw value = 205
    LEV1BLX tile count    = 205

So every value 1..205 in LEV1MAP is a direct 1-based tile index.

Correct for EDRAX:

    tile_index = raw_value - 1

Therefore raw values 201, 202, 203, 204 are real background tile indices near the end of LEV1BLX.
They are not low7 values.

## General safe MAP rule

Use the paired BLX tile count:

    if 1 <= raw_value <= blx_tile_count:
        render as background tile raw_value - 1
    else:
        treat as special/object/trigger/unknown cell data

This separates background from extra data much better than applying `(raw & 0x7f)` globally.

## Per-level out-of-range cells

Using same-index resource pairing:

    LEV0: 224 tiles, max raw 249, 276 cells out of tile range
    LEV1: 205 tiles, max raw 205, 1 cell out of tile range
    LEV2: 199 tiles, max raw 199, 1 cell out of tile range
    LEV3: 205 tiles, max raw 233, 282 cells out of tile range
    LEV4: 205 tiles, max raw 224, 254 cells out of tile range
    LEV5: 214 tiles, max raw 239, 192 cells out of tile range

So LEV1/EDRAX and LEV2 are mostly pure tilemaps.
Other levels include additional special/object/trigger values embedded in MAP.

## Scroll / structure observations

The map is still 13 × 288 cells.

The visible playfield is 13 tiles wide = 208 px wide.
Height is roughly 12.5 tiles on a 320×200 EGA screen, so a viewport is about 13 map rows.

The EXE uses:
    0x0EA0 = 3744 = 13 × 288
    add/sub 0x0D = add/sub one map row

So scrolling consumes/presents the MAP in 13-byte rows.

## Screenshot mismatch

The supplied screenshot's beginning section has:
- mostly empty starfield
- a large left-side wall
- a central/right structure
- sprites/enemies/player/HUD

The raw LEV1MAP row 0 starts with a dense base/lava structure, so the visible "start" in the game is probably not simply row 0 of the background map. Possibilities:

1. the viewport starts at an offset into the map,
2. the scroll direction means the apparent beginning uses a lower part of the 13×288 map,
3. additional foreground/object layers are drawn over/around the MAP background,
4. some MAP special values in other levels represent object/trigger data, but LEV1 is mostly direct background.

## BLX orientation

The user observed that certain EDRAX tiles appear rotated/reflected relative to game usage.
This likely affects editor/tile-browser presentation. It does not yet prove that the full MAP render should transform every tile, because full raw render already forms coherent structures.

Candidate display transform:
    rotate 90 degrees left, then flip vertical

This should become a GUI toggle, not a hard-coded global transform yet.

## Added previews

- pass26_LEV1_rule_compare_rows.png
- pass26_raw201_204_neighborhoods_raw_minus1.png
- pass26_safe_tile_vs_special_first64.png
- pass26_LEV1_all_row_windows_step8.png
- pass26_LEV1_reversed_row_windows_step8.png
- pass26_start_variants_raw_vs_rotLflipV.png
- pass26_all_levels_norm_early_rows.png
- pass26_all_levels_rev_early_rows.png

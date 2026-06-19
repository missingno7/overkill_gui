# Pass57 - off-grid enemy research and verification overlay

## User clue

The screenshot shows enemies in LEV1 that are not aligned to the 16x16 MAP grid.
This strongly supports the model that enemies are runtime objects with pixel coordinates, not MAP tiles.

## Screenshot/terrain alignment

The provided screenshot was resized to the gameplay width of 208 px and matched against the rendered LEV1 terrain.

Best match:

    level image y ≈ 2085
    screenshot resized size = 208x170

Detected blue/white enemy blobs land at approximate level-image pixel positions:

    x=70, y=2109
    x=86, y=2104
    x=119, y=2104
    x=135, y=2107

These are clearly not tile-grid positions.

## GUI update

`research_overlays/level_observations.json` now supports off-grid observations using:

```json
{
  "level_x": 86,
  "level_y": 2104,
  "label": "off-grid enemy candidate",
  "sprites": [68, 69, 70]
}
```

The Level Viewer draws these as orange/yellow circular crosshair markers.

## Disassembly clues

Relevant routines saved in `archive/analysis/pass57/`:

- `runtime_enemy_sprite_44_46_routines.txt`
- `level_specific_runtime_sprite_selection_a8ff_aa45.txt`
- `object_slot_bounds_and_render_b288_b35a.txt`

The key sprite values appear in runtime object code:

    2X2 68 = 0x44
    2X2 69 = 0x45
    2X2 70 = 0x46

Routines around 0x85cf/0x86e0 write or compute object `+0x08` sprite/frame values using `0x44` as a base.

This is better evidence than MAP bytes.

## What to verify next

Open LEV1 in Level Viewer with:

- zoom 3x or 4x
- Show research observations ON
- Show canonical row ruler ON

Then check whether the orange off-grid markers line up with the enemy positions from the screenshot.
If they are shifted, report approximate direction/amount.

# Overkill RE pass30 - vertically flipped BLX tiles and reversed MAP display order

## New findings

Two separate things were still off after pass29:

1. **BLX tiles themselves are vertically mirrored** relative to the in-game background.
2. **The scrolling map is easier to understand in reverse row order for display**, because the game progresses upward.

## Interpretation

### 1) BLX tile orientation

The individual level tiles render correctly structurally, but within each tile the artwork is upside-down.
This is not about the long-map row order; it is a per-tile issue.

Fix:

    rendered_blx_tile = vertical_flip(decoded_blx_tile)

This change applies to the BLX tile browser and to full level rendering.

### 2) MAP display order vs canonical storage order

The canonical decoded LEVxMAP rows are still:

    row_y = bytes(decoded[x * 288 + y] for x in range(13))

But for human-friendly level preview/editor display, we now reverse the rows:

    display_rows = reversed(canonical_rows)

Reason: Overkill is a vertical shooter where progress goes from bottom toward top, so the visually useful editor order is the opposite of the storage order.

## Practical model now

- Decode LEVxMAP as type-4 transposed rows.
- Decode LEVxBLX as before.
- Vertically flip each BLX tile for display.
- Display the MAP rows in reversed order for gameplay-oriented preview.
- Raw MAP values in range `1..tile_count` are direct 1-based tile indices.
- Out-of-range values remain special/unknown cells.

## Caveat

This is a **display-order fix**, not proof that the game stores rows reversed internally.
The editor can keep the canonical row order internally, but the preview should default to gameplay order.

## Added previews

- sample_previews/LEV0_pass30_gameplay_order_contact.png
- sample_previews/LEV1_pass30_gameplay_order_contact.png
- sample_previews/LEV2_pass30_gameplay_order_contact.png
- sample_previews/LEV3_pass30_gameplay_order_contact.png
- sample_previews/LEV4_pass30_gameplay_order_contact.png
- sample_previews/LEV5_pass30_gameplay_order_contact.png

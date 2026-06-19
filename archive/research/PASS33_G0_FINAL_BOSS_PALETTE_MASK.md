# Overkill RE pass33 - G0 final boss transparency/palette research

## User confirmation

G0 contains the final boss. The shape is recognizable now, but colors/backgrounds do not match the game.

This means:
- the structural layout is mostly correct,
- the remaining issue is palette/transparency/mask interpretation,
- not the basic 32x32 row-plane decode.

## G0 structure

G0.BIC:

    type = 3
    expected_size = 8199
    decoded_len = 4632

The useful decoded payload contains:

    8 complete chunks × 516 bytes = 4128 bytes
    leftover tail = 504 bytes

Each complete chunk:

    4-byte header
    512 bytes row-plane EGA bitmap
    32x32 px

These 8 chunks are final-boss pieces/animation parts.

## Why colors looked wrong

The decoded frames contain large bright fill areas:
- green
- cyan
- magenta
- red strips

These are probably not intended visible colors. They behave like:
- transparency key colors,
- temporary/background fill colors,
- or palette-dependent placeholders.

In pass33 the preview applies a conservative display heuristic:

    replace dominant corner color with black

This makes the final boss much more readable on a black gameplay background.

This is not the final real game palette. It is only a better editor preview.

## G0 leftover tail

The 504-byte tail is not random.

Rendered as 1bpp in several widths, it shows boss-like silhouettes/strips.
So it is probably:
- a mask,
- transparency/occlusion data,
- hit/collision shape,
- partial overlay data,
- or a compressed/packed continuation for the final boss.

Added diagnostic:

    sample_previews/G0.BIC_pass33_tail_mask_diagnostic.png

## Plane order

G0 was tested under all 24 EGA plane orders.

Different plane orders change color mapping but keep the same boss shape.
The default order `(0,1,2,3)` appears structurally correct.
The wrong-looking colors are more likely transparency/palette issues than plane-order issues.

Added diagnostic:

    sample_previews/G0.BIC_pass33_plane_order_diagnostic.png

## Parser direction

The BIC parser should become a dispatcher:

- Type 4:
  - transposed records
  - normal G sheets, sprites, BLX, MAP
  - G3 special split: 129 records × 8 bytes -> two 516-byte streams

- Type 3:
  - full row-plane image:
      WINDOW.BIC
      BLUEBITS.BIC
  - special 516-byte chunk sheet:
      G0.BIC

- Type 0:
  - unresolved custom/sparse blitter:
      LOGO.BIC

## LOGO.BIC

LOGO should not crash; pass33 shows a diagnostic message.
It is unresolved and likely needs tracing the EXE draw routine.

## BLUEBITS

BLUEBITS appears to decode as a source bitmap.
The animation in-game likely reveals/draws parts algorithmically rather than storing frames.

## Next work

1. Find if G0 has a palette table or if the game simply treats one color index as transparent.
2. Determine whether the 504-byte tail is a mask and how it maps onto the 8 boss chunks.
3. Trace the final-boss drawing routine in EXE to confirm transparency and palette behavior.
4. Trace LOGO type-0 draw routine.

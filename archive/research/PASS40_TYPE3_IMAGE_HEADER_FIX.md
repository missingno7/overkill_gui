# Overkill RE pass40 - Type-3 image header correction

## User clue

WINDOW.BIC was not fully visible. It should be a 320x200 image.

This revealed a systematic header interpretation bug in the type-3 image renderer.

## Main fix

For BIC type=3 full-image resources, visible dimensions are:

    height      = source_data[2]
    widthBytes  = source_data[4]

Not:

    height = source_data[5]

## WINDOW.BIC

Header:

    03 02 C8 00 28 82 00

Interpreted as:

    source_data[2] = 0xC8 = 200 height
    source_data[4] = 0x28 = 40 widthBytes = 320 px

So WINDOW.BIC is now rendered as:

    320x200

Earlier pass rendered only 320x130 because it incorrectly used byte 5 = 0x82 = 130.

## BLUEBITS.BIC

Header:

    03 02 4F 00 0C ED 00

Interpreted as:

    source_data[2] = 0x4F = 79 height
    source_data[4] = 0x0C = 12 widthBytes = 96 px

So the clean source image is:

    96x79

The rest of the decoded payload likely belongs to animation/reveal/blitter data, not a taller visible bitmap.
That matches the observation that BLUEBITS appears in-game as an animation by parts, not as stored frames.

## LOGO.BIC

LOGO.BIC is still unresolved, but pass40 expands its diagnostics.

Because type-3 proved that 320px-wide candidates matter, LOGO diagnostics now include:
- header widthBytes candidates,
- 320px-wide candidates with widthBytes=40,
- byte1/byte2/byte5 height candidates,
- raw and PackBits probes.

These still look noisy, so LOGO.BIC is probably not a simple full row-plane bitmap.
It likely uses a custom type-0 sparse/compiled blitter.

## Practical state

Fixed:
- WINDOW.BIC full 320x200 render
- BLUEBITS.BIC clean source-image dimensions

Still unresolved:
- LOGO.BIC type-0 blitter
- meaning of type-3 extra decoded data after the visible image
- BLUEBITS reveal/animation algorithm

## Added previews

- sample_previews/WINDOW.BIC_pass40_preview.png
- sample_previews/BLUEBITS.BIC_pass40_preview.png
- sample_previews/LOGO.BIC_pass40_preview.png
- sample_previews/all_bic_pass40_contact.png

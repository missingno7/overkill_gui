# Overkill RE pass41 - Type-3 stream offset correction

## User clue

WINDOW.BIC should match the 320x200 in-game background screenshot.
Pass40 fixed the dimensions, but the image was still shifted and wrong-colored.

## Systematic finding

For type=3 full-image BIC resources, the PackBits/RLE stream starts at byte 5, not byte 7.

WINDOW.BIC header:

    03 02 C8 00 28 82 00 ...

Old generic decoder:
    PackBits from source_data[7:]

Correct full-image type=3 renderer:
    PackBits from source_data[5:]
    then drop the first decoded padding/alignment byte

This fixes:
- WINDOW.BIC colors,
- the 8px-ish horizontal shift,
- the title/background alignment against the known game screenshot.

## WINDOW.BIC

Current model:

    type = 3
    height = source_data[2] = 200
    widthBytes = source_data[4] = 40
    payload = PackBits(source_data[5:])[1:]

Render as:
    320x200 row-interleaved EGA planes

## BLUEBITS.BIC

Same type-3 stream rule:

    type = 3
    height = source_data[2] = 79
    widthBytes = source_data[4] = 12
    payload = PackBits(source_data[5:])[1:]

Render as:
    96x79 row-interleaved EGA source image

The remaining decoded stream is likely animation/reveal/blitter data.

## Important

This is not a screenshot magic patch.
The screenshot exposed the bug, but the fix comes from stream alignment:
byte 5 is the first RLE control byte. Starting at byte 7 skipped valid RLE setup bytes.

## Still unresolved

- Why the first decoded byte is alignment/padding.
- LOGO.BIC true type-0 blitter format.
- BLUEBITS reveal/animation algorithm.
- Type=3 extra data after visible source image.

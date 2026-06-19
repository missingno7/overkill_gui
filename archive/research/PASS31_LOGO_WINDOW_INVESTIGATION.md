# Overkill RE pass31 - LOGO.BIC and WINDOW.BIC investigation

## Main finding

The remaining graphics are not all one BIC format.

So far:

- Type 4: transposed records
  - sprites, BLX, MAP
- Type 3: full/image-like row-plane resources
  - WINDOW.BIC
  - BLUEBITS.BIC
- Type 0: custom/sparse/compiled sprite-like resource
  - LOGO.BIC

## WINDOW.BIC

WINDOW.BIC is BIC type 3:

    raw header: 03 02 C8 00 28 82 00 ...
    byte 4 = 0x28 = 40 width bytes = 320 px
    byte 5 = 0x82 = 130 px height

The useful bitmap is:

    decoded_payload[:40 * 130 * 4]

Layout:

    for each row:
        plane0: 40 bytes
        plane1: 40 bytes
        plane2: 40 bytes
        plane3: 40 bytes

So WINDOW.BIC renders as a 320x130 EGA row-plane image.

The earlier browser rendered it as generic probes, which made it look broken.

## BLUEBITS.BIC

BLUEBITS.BIC follows the same type-3 idea:

    byte 4 = 0x0C = 12 width bytes = 96 px
    byte 5 = 0xED = 237 px height

It also renders as row-plane EGA.

## LOGO.BIC

LOGO.BIC is type 0:

    raw header: 00 36 40 00 22 36 17 ...
    byte 4 = 0x22 = 34 width bytes = 272 px
    byte 5 = 0x36 = 54 px height

However, LOGO.BIC does NOT decode as:
- plain raw row-plane bitmap,
- normal PackBits row-plane bitmap,
- the LZSS-style stream used elsewhere,
- simple nibble/chunky bitmap.

Those probes still look noisy.

The repeated `0x36 xx 00` patterns and the fact that it is a title logo strongly suggest it is not a full bitmap, but a custom sparse/compiled logo blitter format:
- probably transparent logo data,
- possibly per-scanline spans or masks,
- likely meant to be drawn over another background rather than previewed directly.

## Code changes in pass31

Added:

    render_bic_type3_image(decoded, source_data)

Used for WINDOW.BIC and BLUEBITS.BIC.

Added:

    make_logo_probe_image(source_data)

So LOGO.BIC no longer pretends to be ordinary bitmap data. It shows a diagnostic note until the type-0 sparse format is solved.

## Next targets

1. Find the EXE routine that draws LOGO.BIC.
2. Trace how type-0 resources are unpacked/rendered.
3. Decode type-0 as span/mask/sparse logo format.
4. Apply the same type-3 renderer to any other matching type-3 resources.

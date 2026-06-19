# Overkill RE pass48 - LOGO.BIC solved

## Breakthrough

LOGO.BIC is now decoded.

It is not PackBits, PCX RLE, raw row-plane, or type-4 transpose.

It uses a simple type-0 escape-RLE format.

## Header

LOGO.BIC starts with:

    00 36 40 00 22 ...

Interpretation:

    byte 0 = type = 0
    byte 1 = escape marker = 0x36
    word 2 = height = 0x0040 = 64
    byte 4 = widthBytes = 0x22 = 34

So the decoded bitmap is:

    width  = 34 * 8 = 272 px
    height = 64 px
    planes = 4
    decoded size = 34 * 64 * 4 = 8704 bytes

## Payload

Payload starts at byte 5.

RLE rule:

    if byte == escape:
        count = next byte
        value = next byte
        emit value repeated count times
    else:
        emit byte literally

For LOGO.BIC:

    escape = 0x36

This explains the previously suspicious repeated pattern:

    36 NN 00
    36 NN FF
    36 NN 55
    36 NN AA

They are RLE runs of repeated bytes, not scanline/span commands.

## Rendering

After escape-RLE decode, render as row-interleaved EGA planes:

    for each row:
        plane0 widthBytes bytes
        plane1 widthBytes bytes
        plane2 widthBytes bytes
        plane3 widthBytes bytes

This produces the OVERKILL title logo.

## Important clarification

LOGO.BIC is not the whole 320x200 intro screen.

It is the title logo overlay:

    272x64

The 320x200 background is WINDOW.BIC.
The full intro/title screen is a composition of WINDOW.BIC plus LOGO.BIC and likely other art/resources.

The GUI preview shows:
1. LOGO solved 272x64
2. LOGO over WINDOW at 0,0 for context

## Why the earlier size clue was close but wrong

Earlier clue:

    34 * 54 * 4 = 7344
    file size 7377
    difference 33

This looked like 33-byte header + 272x54 raw bitmap.

But byte 0x36 is not height.
It is the escape byte.

Actual height is the word at bytes 2..3:

    0x0040 = 64

Actual decoded size:

    34 * 64 * 4 = 8704

The source file is smaller because of escape-RLE compression.

## Added previews

- sample_previews/LOGO.BIC_pass48_solved_272x64.png
- sample_previews/LOGO.BIC_pass48_preview.png
- sample_previews/all_bic_pass48_contact.png

## Parser state

LOGO.BIC moves from unresolved to solved.

Remaining complex items:
- BLUEBITS reveal/animation algorithm
- exact composition of full intro screen beyond WINDOW + LOGO
- some blitter/mask semantics for complex resources

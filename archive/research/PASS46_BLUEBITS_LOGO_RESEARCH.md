# Overkill RE pass46 - BLUEBITS sub-images and LOGO status

## BLUEBITS.BIC

Pass45 showed that BLUEBITS is not just one bitmap.

Pass46 improves the diagnostic parser by selecting non-overlapping embedded image-like chunks from the extra stream.

Current confirmed base:

    type = 3
    corrected stream = PackBits(source_data[5:])[1:]
    visible source image = 96x79
    visible bytes = 3792
    corrected stream length = 45112
    extra bytes after visible image = 41320

The extra stream contains multiple plausible image-like chunks with headers:

    word height
    word widthBytes

The strongest selected candidates include:

    extra@0      128x93
    extra@5956   144x113
    extra@15200   96x35
    extra@16884  120x44
    extra@20732  128x36
    extra@23040  144x44

There are also strip/text/panel-like chunks later:

    extra@26212 128x45
    extra@29096 128x45
    extra@36472 320x10
    extra@38076 320x10

This supports the user's suspicion:
BLUEBITS likely contains 2-3 main images plus additional reveal/animation/strip data.

Important:
This is still diagnostic. The real game probably does not simply display these as independent frames. It likely uses a reveal/blitter routine.

## LOGO.BIC

LOGO remains unresolved.

What was tested in pass46:

- raw EGA row-plane candidates,
- plane-block candidates,
- PackBits variants,
- PCX-style RLE variants,
- 272x54 candidates,
- 320x200 candidates,
- different starts/drops.

None produced the expected intro/title image.

Important size clue:

    LOGO.BIC size = 7377
    34 * 54 * 4 = 7344
    difference = 33 bytes

This strongly hints at a 33-byte prefix + 272x54-related payload, but direct raw rendering at offset 33 does not work.

Header:

    00 36 40 00 22 36 17 00 ...

Likely meanings, not yet confirmed:

    type = 0
    height = 0x36 = 54
    widthBytes = 0x22 = 34
    possible x/stride/value = 0x0040

The recurring pattern:

    36 NN 00 ...

looks like command/span data or a custom blitter stream.

## Disassembly clue

Code around 0x5aac looks important. It reads two words from DS:SI and then calls a mode-dependent blitter through a jump table.

This may be the path for:
- LOGO.BIC type=0,
- BLUEBITS reveal data,
- or another image command stream.

It still needs full tracing before implementing a true LOGO parser.

## Added previews/research artifacts

- sample_previews/BLUEBITS.BIC_pass46_preview.png
- sample_previews/pass46_bluebits_selected_candidates.png
- sample_previews/LOGO.BIC_pass46_preview.png
- sample_previews/pass46_logo_decompress_variants.png
- sample_previews/all_bic_pass46_contact.png
- analysis/pass46/logo_bluebits_disasm_notes.txt

## Current state

Fixed/solid:
- G3
- MANEXPL
- WINDOW
- THEND
- SHIP
- normal G sheets
- level BLX/MAP previews

Improved/diagnostic:
- BLUEBITS, now clearly multi-chunk

Still unresolved:
- true LOGO.BIC type=0 parser
- BLUEBITS animation/reveal algorithm

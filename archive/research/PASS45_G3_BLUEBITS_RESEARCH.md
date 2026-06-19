# Overkill RE pass45 - G3 fixed and BLUEBITS research

## G3.BIC

The previous G3 parser was wrong.

Old interpretation:
    G3 type=4 has 129 records of 8 bytes.
    frame A = concat(record[:4] for record in records)
    frame B = concat(record[4:8] for record in records)

That produced two interleaved/incorrect images.

## Correct G3 interpretation

After type-4 transposition, reconstruct the 129 records of 8 bytes, then simply concatenate them:

    data = concat(records)

Because:

    129 * 8 = 1032 = 2 * 516

So:

    frame0 = data[0:516]
    frame1 = data[516:1032]

Each frame is a normal 32x32 EGA record:

    20 00 04 00
    512 bytes row-plane EGA data

This is the same systematic header rule used elsewhere.

Added:
    sample_previews/G3.BIC_pass45_preview.png
    sample_previews/pass45_g3_interpretations.png

## BLUEBITS.BIC

BLUEBITS is confirmed more complex than a single image.

Current type=3 stream model still holds:

    header: 03 02 4F 00 0C ED 00
    height = 0x4F = 79
    widthBytes = 0x0C = 12
    corrected stream = PackBits(source_data[5:])[1:]

Visible source image:

    96x79
    visible_len = 12 * 79 * 4 = 3792 bytes

But the corrected stream length is much larger:

    corrected stream len = 45112 bytes
    extra after visible image = 41320 bytes

So BLUEBITS.BIC is not just one bitmap.
It likely contains a visible source image plus reveal/animation/blitter data.

## BLUEBITS extra data

The pass45 diagnostic scans the extra stream for plausible embedded image headers of the form:

    word height
    word widthBytes

It finds several plausible candidates, and the preview now shows a few of them as diagnostics.

Important:
These extra images are candidates only.
The real in-game animation likely uses a blitter/reveal routine, not a simple list of images.

Added:
    sample_previews/BLUEBITS.BIC_pass45_preview.png

## Disassembly clues

The code around 0x572d is very relevant for full-screen/type-3 image drawing.

It explicitly sets up:

    height 0xC8 = 200
    widthBytes 0x28 = 40

Then loops over 200 rows and copies either:
- 0x50 bytes,
- or four planes of 0x28 bytes,
depending on mode/jump-table.

This supports the type=3 row-plane full-image interpretation for WINDOW.BIC.

Relevant snippets included:

    analysis/pass45/type3_fullscreen_blitter_572d.txt
    analysis/pass45/bluebits_menu_context_5654.txt

## LOGO.BIC

Still unresolved.

The likely issue is a custom type=0 compression/blitter, possibly more sophisticated because the referenced image is detailed and would otherwise be large.

Current clues:
- LOGO.BIC is resource index 24.
- Type byte is 0.
- Size relation to 272x54 raw EGA is suspicious but raw offset render does not work.
- Repeated 36 NN 00 patterns look like command/span data.
- Needs EXE routine tracing, not more bitmap guessing.

## Current unknowns

1. Exact type=0 LOGO.BIC decode/blitter.
2. BLUEBITS reveal/animation routine.
3. Meaning of extra type=3 data after visible BLUEBITS image.
4. Whether type=3 extra stream encodes multiple sub-images, strip commands, or timed reveal masks.

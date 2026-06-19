# Overkill RE pass42 - LOGO.BIC and BLUEBITS direction

## User clue

The provided screenshot might be the image encoded by LOGO.BIC.

The screenshot is useful as calibration only. Parser changes still need to be derived from the game data or EXE logic.

## LOGO.BIC observations

LOGO.BIC header:

    00 36 40 00 22 36 17 00 ...

File size:

    7377 bytes

Interesting exact-size relation:

    34 widthBytes * 54 height * 4 planes = 7344 bytes
    7377 - 7344 = 33 bytes

So LOGO.BIC has a very suspicious relationship to a 272x54 EGA row-plane bitmap with a 33-byte prefix.

However, rendering raw data at offsets around 33 as:
- row-interleaved EGA,
- plane-block EGA,
- several nearby offsets,
- PackBits variants,

still produces noise rather than the OVERKILL title graphic.

This means one of these is probably true:

1. LOGO.BIC is not a plain EGA row-plane bitmap despite the size coincidence.
2. The 33-byte prefix is not the only transform; the payload may be encoded/bit-shuffled.
3. Type=0 uses a custom sparse/compiled blitter.
4. LOGO.BIC may only be one component/overlay, not the entire intro screen.

## LOGO.BIC structure clue

The byte 0x36 appears hundreds of times and repeatedly occurs in patterns like:

    36 NN 00 ...

This may indicate:
- row/span command structure,
- repeated scanline command,
- or a custom blitter language.

The early bytes:

    00 36 40 00 22 36 ...

look plausibly like:
- type = 0,
- height or rows = 0x36 = 54,
- some word/value = 0x0040,
- widthBytes = 0x22 = 34,
- height again = 0x36.

But this is not confirmed.

## Important conclusion for LOGO.BIC

Do not treat LOGO.BIC as solved.
Do not hard-code it from the screenshot.

The next real step is to trace the EXE routine that draws resource index 24:

    filename table index 24 = LOGO.BIC

Known nearby indices:

    23 = MANEXPL.BIC
    24 = LOGO.BIC
    25 = THEND.BIC
    28 = BLUEBITS.BIC
    29 = WINDOW.BIC

## BLUEBITS.BIC

BLUEBITS.BIC is now known to be type=3 with a clean visible source image:

    header: 03 02 4F 00 0C ED 00
    height = source_data[2] = 79
    widthBytes = source_data[4] = 12
    visible source = 96x79
    payload = PackBits(source_data[5:])[1:]

The large decoded stream beyond the visible 96x79 image is probably not more image height.
It likely drives the in-game reveal/animation by strips or parts.

So BLUEBITS likely has:
- source bitmap,
- additional animation/reveal/blitter command data in the same BIC stream.

## WINDOW.BIC contrast

WINDOW.BIC has the same type=3 full-image stream rule:

    header: 03 02 C8 00 28 82 00
    height = 200
    widthBytes = 40
    payload = PackBits(source_data[5:])[1:]
    visible image = 320x200

This is now visually calibrated against the known in-game screenshot.

## Added previews

- sample_previews/pass42_logo_raw_offset24_40.png
- sample_previews/reference_possible_logo_intro_screen.png

## Next work

1. Trace EXE draw routine for LOGO.BIC / resource index 24.
2. Trace EXE draw routine for BLUEBITS.BIC / resource index 28 to understand reveal animation.
3. Identify whether type=0 LOGO uses:
   - span commands,
   - XOR/delta blitting,
   - EGA write mode,
   - or bitplane transform.
4. Keep the GUI LOGO preview diagnostic-only until that routine is understood.

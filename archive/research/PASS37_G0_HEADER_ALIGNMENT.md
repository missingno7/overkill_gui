# Overkill RE pass37 - G0 systematic header alignment fix

## Why this pass exists

The goal is to avoid magic constants inferred from screenshots.

The screenshot is useful only as a visual sanity check. The fix in this pass comes directly from the G0 decoded data.

## Critical finding

G0 was chunked from the wrong offset.

The standard 32x32 row-plane record header is:

    20 00 04 00

For normal G resources this appears at the beginning of each 516-byte record.

In G0 decoded payload, this header appears at:

    504, 1020, 1536, 2052, 2568, 3084, 3600, 4116

That is:

    first true record starts at 504
    then every 516 bytes

So the first 504 bytes are not a trailing mask after 8 records.
They are a prefix/preamble before the first true graphic record.

## Consequence

Previous G0 parsing:

    records = decoded[0:516], decoded[516:1032], ...

was wrong.

Correct G0 parsing:

    records = every 516-byte block starting at embedded header 20 00 04 00

This removes the need for the earlier magic/screenshot-derived special plane order.
The colors become much more game-like using the normal plane order once record alignment is fixed.

## New G0 record model

G0 decoded payload:

    504-byte prefix/preamble
    8 true records × 516 bytes

Each true record:

    20 00 04 00
    512 bytes 32x32 row-plane EGA data

## Final boss composition after alignment

Because records shifted by the 504-byte prefix, the body that was previously described as old chunks 4..7 is now true records:

    3 4
    5 6

Composite method is still row/plane merge:

    top    = merge records 3 + 4 into 64x32
    bottom = merge records 5 + 6 into 64x32
    boss   = top above bottom

## Preview

Pass37 shows:

- raw header-aligned 64x64 boss,
- magenta-keyed preview,
- all true records.

The magenta keying is still preview-only. It is not a claimed in-game rule yet.
The real blitter/mask behavior must still be traced.

## What we still do not know

1. What exactly is the 504-byte prefix/preamble?
   - likely mask/strip/blitter setup data,
   - not trailing tail.

2. How does the game use transparency?
   - color key?
   - mask?
   - EGA write mode?

3. How are records 0..2 and 7 used?
   - likely alternate boss animation pieces / head / effect parts.

4. Is LOGO.BIC another prefix+record or a true type-0 custom blitter?

## Added previews

- sample_previews/G0.BIC_pass37_header_aligned_preview.png
- sample_previews/G0.BIC_pass37_64x64_raw.png
- sample_previews/G0.BIC_pass37_64x64_keyed.png
- sample_previews/pass37_G0_header_aligned_records_default.png
- sample_previews/pass37_G0_header_aligned_composition_candidates.png

# Overkill RE pass43 - MANEXPL.BIC fixed

## Problem

The previous MANEXPL.BIC parser incorrectly assumed:

    903 = 7 prefix records + 28 * 32 data records

and rendered each frame by skipping the first seven 16-byte records and synthesizing a 20 00 04 00 header.

That caused frame indices and colors/sections to be wrong.

## Systematic fix

After type-4 transposition, concatenate all 903 small records:

    903 records * 16 bytes = 14448 bytes

And:

    14448 / 516 = 28

The normal 32x32 record header:

    20 00 04 00

appears exactly at:

    0, 516, 1032, 1548, ...

for all 28 frames.

So MANEXPL.BIC is simply:

    28 direct 516-byte records

Each record already has:

    20 00 04 00
    512 bytes row-plane EGA bitmap
    32x32 px

## Correct parser rule

Do:

    small = type4_records(record_size=16, count=903)
    data = concat(small)
    records = chunks(data, 516)

Do NOT:
- skip 7 small records,
- synthesize headers,
- shift frame indices.

## Result

The corrected preview now shows coherent frames:
- player/ship explosion frames,
- explosion fireballs,
- large enemy/boss explosion pieces.

## Added previews

- sample_previews/MANEXPL.BIC_pass43_fixed_preview.png
- sample_previews/MANEXPL_correct_direct_28_frames.png
- sample_previews/MANEXPL_old_skip7_wrong.png
- sample_previews/all_bic_pass43_contact.png

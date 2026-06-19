# Overkill RE pass32 - G0/G3 decode and BIC parser direction

## Goal

Move toward a complete/general BIC parser instead of one-off guesses.

Current BIC dispatcher model:

- Type 4: transposed records.
- Type 3: has at least two sublayouts:
  - full row-plane image: WINDOW.BIC, BLUEBITS.BIC
  - G0 special sheet: complete 516-byte 32x32 frame chunks in decoded payload
- Type 0: custom sparse/compiled blitter: LOGO.BIC, still unresolved

## Why G1/G2/G4/G5 worked

These are type=4 records with a 16-bit record size:

    G1: record_size_word=516, count=6
    G2: record_size_word=516, count=10
    G4: record_size_word=516, count=6
    G5: record_size_word=516, count=13

Each record:

    4-byte header
    512 bytes row-plane EGA bitmap
    32x32 pixels, widthBytes=4, height=32

## Why G3 was wrong

G3 is also type=4, but it is packed differently:

    G3: record_size=8, count=129
    decoded_size = 1032 = 2 * 516

It is not two contiguous 516-byte records.

After type-4 transposition, each 8-byte record contains two 4-byte streams:

    frame A = concat(record[0:4] for record in records)
    frame B = concat(record[4:8] for record in records)

Those two streams produce two normal 516-byte 32x32 records.

So G3 is now decoded as two 32x32 frames.

## Why G0 was wrong

G0 is type=3, not type=4:

    G0: type=3
    expected_size=8199
    decoded length with PackBits-like stream = 4632

It does not use the WINDOW/BLUEBITS type-3 full-image layout.

But the decoded payload contains complete 516-byte chunks:

    4632 // 516 = 8 complete frames, plus 504 leftover bytes

Each complete 516-byte chunk renders as:

    4-byte header
    512 bytes row-plane 32x32 EGA bitmap

So G0 is a special type-3 G-sheet variant.
The leftover 504 bytes are still not understood; likely partial/mask/continuation data or a compression edge case.

## LOGO.BIC status

LOGO.BIC is type=0 and still unresolved.

It should not crash now; it shows a diagnostic preview.

It does not decode correctly as:
- type-3 row-plane image
- type-4 transposed record sheet
- normal PackBits bitmap
- LZSS bitmap
- nibble/chunky bitmap

Likely format:
- sparse/compiled logo blitter
- transparent logo spans/masks
- drawn over another screen/background by a special EXE routine

## Code changes

Added:

    make_g0_sheet()
    make_g3_sheet()
    make_labelled_sheet()

GUI now explicitly dispatches:
    G0.BIC -> G0 special sheet
    G3.BIC -> G3 two-frame split stream
    G1/G2/G4/G5 -> existing 516-byte type-4 sheet

## BLUEBITS animation note

BLUEBITS.BIC now decodes as a type-3 row-plane source image.
In-game animation likely does not mean the file stores frames. More likely the game reveals/draws parts of this source image algorithmically.

## Next work

1. Make BicDecoded store both header byte and header word:
   - record_size_byte = data[3]
   - record_size_word = word(data[3:5])
   - count_word = word(data[5:7])

2. Use the word record size for G1/G2/G4/G5 instead of hard-coded record_size=516.

3. Decode LOGO.BIC by finding the EXE routine that draws type=0 resources.

4. Understand BLUEBITS animation:
   - current type-3 bitmap decode is probably correct as source image
   - in-game animation likely reveals/draws it algorithmically by strips/parts, not frame records.

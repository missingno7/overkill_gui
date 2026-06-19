# Overkill RE pass35 - G0 final boss row/plane merge

## User correction

Chunks 4..7 should form one metal-looking final boss on transparent/black background.
The green/fuchsia areas are not a normal palette issue; they are part of incorrectly understood blitter/background semantics.

## New finding

Chunks 4 and 5 should not merely be pasted as two already-rendered 32x32 images.

Because G0 stores EGA row-plane data, making a 64px-wide top half requires merging at the byte-plane level:

    for each row:
        plane0 = chunk4.plane0 + chunk5.plane0
        plane1 = chunk4.plane1 + chunk5.plane1
        plane2 = chunk4.plane2 + chunk5.plane2
        plane3 = chunk4.plane3 + chunk5.plane3

The same applies to chunks 6 and 7 for the bottom half.

So the final boss composite is:

    top    = row/plane merge of chunks 4 + 5  -> 64x32
    bottom = row/plane merge of chunks 6 + 7  -> 64x32
    boss   = top above bottom                 -> 64x64

This is noticeably more coherent than simple pasting.

## Preview modes

G0 preview now shows:

1. merged raw 64x64 boss,
2. merged keyed preview,
3. individual chunks.

The keyed preview removes obvious fill/key colors:
- green,
- bright green,
- magenta.

This is still a preview heuristic, not the final in-game blitter.

## Important caveat

The remaining green background in the raw composite is probably not palette data.
It is likely one of:

- transparent fill color,
- masked background,
- EGA write-mode behavior,
- use of the 504-byte tail as a mask/strip table.

## G0 tail

The 504-byte tail remains suspicious. It is close to a 64x64 1bpp mask size:

    64 * 64 / 8 = 512 bytes

but it is 8 bytes short.

So the tail may be:
- a 64x63 1bpp mask,
- a strip mask with omitted blank row,
- a blitter command/mask stream,
- or mask data for only part of the boss.

This still needs EXE tracing.

## Added previews

- sample_previews/G0.BIC_pass35_merged_final_boss.png
- sample_previews/G0.BIC_pass35_64x64_raw.png
- sample_previews/G0.BIC_pass35_64x64_keyed.png
- sample_previews/G0.BIC_pass35_paste_vs_merge.png

## Next work

Trace the final-boss draw routine in EXE to answer:

- Is green/magenta used as color-key?
- Is the 504-byte tail a mask?
- Are the first 4 bytes of each 516-byte record blitter metadata?
- How are chunks 0..3 used relative to chunks 4..7?

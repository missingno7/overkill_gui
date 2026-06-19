# Overkill RE pass34 - G0 final boss composition

## User correction

G0 is not primarily a set of independent frames.

In the game, the final boss is one large object assembled from pieces:

    4 5
    6 7

That means the earlier preview was misleading because it displayed all chunks as separate frames.

## What was verified

Several chunking interpretations were tested:

- 516-byte chunk + skip 4 bytes
- 516-byte chunk + skip 0 bytes
- 512-byte chunk + offsets 0,4,8,24

The best structural match remains:

    516-byte chunks
    first 4 bytes = record/blitter metadata
    next 512 bytes = 32x32 row-plane EGA bitmap

The composition:

    chunk 4 at top-left
    chunk 5 at top-right
    chunk 6 at bottom-left
    chunk 7 at bottom-right

forms a coherent 64x64 final boss.

## Important interpretation change

The weird colors are less likely a global palette problem and more likely caused by missing blitter semantics:

- the chunks include fill/background areas,
- the game probably uses transparency key or mask data when drawing,
- the 504-byte tail likely participates as mask/strip/blitter data.

So the parser should not blindly treat every pixel color as visible final output.

## Current G0 model

G0.BIC:

    type = 3
    decoded_len = 4632

    8 complete chunks × 516 bytes
    504-byte tail

Each 516-byte chunk:

    4 bytes metadata/header
    512 bytes bitmap data
    32x32 row-plane EGA

Chunks:

    0..3 = likely head/animation/alternate parts
    4..7 = final boss 64x64 body composite

## GUI change

G0 preview now shows:

1. assembled final boss raw:
       4 5
       6 7

2. assembled keyed preview,
3. individual pieces.

This is much closer to how the game uses the resource.

## Remaining problem

The correct in-game blitter still needs to be traced.
Specifically:

- what exactly are the first 4 bytes of each 516-byte chunk?
- how is the 504-byte tail used?
- does the game use a mask, transparent color, or special EGA write mode?
- are chunks 0..3 alternate head states or separate animation pieces?

## Added previews

- sample_previews/G0.BIC_pass34_final_boss_composite.png
- sample_previews/pass34_G0_4567_assemblies.png

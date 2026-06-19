# Overkill RE pass24 - resource level pairing research

## Key finding

The resource names are probably meant to pair by the same numeric index:

    LEVnMAP.BIC + LEVnBLX.BIC + Gn.BIC

But the playable order does not start at resource 0.

## Evidence from unpacked EXE

The unpacked EXE contains an internal filename table in this order:

    LEV0MAP.BIC
    LEV1MAP.BIC
    LEV2MAP.BIC
    LEV3MAP.BIC
    LEV4MAP.BIC
    LEV5MAP.BIC
    LEV6MAP.BIC
    LEV7MAP.BIC

    LEV0BLX.BIC
    LEV1BLX.BIC
    LEV2BLX.BIC
    LEV3BLX.BIC
    LEV4BLX.BIC
    LEV5BLX.BIC

    G0.BIC
    G1.BIC
    G2.BIC
    G3.BIC
    G4.BIC
    G5.BIC

This strongly suggests same-index pairing by a current level number.

## Important level-order clue

The code initializes current level variable `0x2356` to 0:

    8d31: movw $0x0, 0x2356

But then it jumps directly to code that increments it before the main level load:

    8d75: jmp 0x8d87
    8d87: incw 0x2356
    8d8b: cmpw $0x6, 0x2356
    8d92: movw $0x0, 0x2356   ; wrap when >= 6

So the likely playable resource order is:

    1, 2, 3, 4, 5, 0

That resolves the confusion where LEV0 looked like a late-game / last-level tileset.

## Current best pairing model

Resource pairing:

    resource level 0: LEV0MAP + LEV0BLX + G0
    resource level 1: LEV1MAP + LEV1BLX + G1
    resource level 2: LEV2MAP + LEV2BLX + G2
    resource level 3: LEV3MAP + LEV3BLX + G3
    resource level 4: LEV4MAP + LEV4BLX + G4
    resource level 5: LEV5MAP + LEV5BLX + G5

Playable order:

    game stage 1: resource level 1
    game stage 2: resource level 2
    game stage 3: resource level 3
    game stage 4: resource level 4
    game stage 5: resource level 5
    game stage 6: resource level 0

This matches the observation that LEV0BLX appears to be a later/last level tileset.

## MAP render rule still applies

For visual background rendering:

    visual_tile = (map_byte & 0x7f) - 1

The original byte must be preserved, because the high bit is a gameplay/tile flag.

## Remaining uncertainty

- The exact planet names still need confirmation from in-game screens/manual.
- `LEV6MAP` and `LEV7MAP` are referenced by the EXE filename table but not present in the SHADOW archive we extracted.
- G0/G3 still need better decoding; even if they belong to the same numeric resource level, their subformat differs.

## Added previews

sample_previews/game_order_same_pair_LEV1_2_3_4_5_0.png

This shows first chunks of the levels in the code-indicated playable order.

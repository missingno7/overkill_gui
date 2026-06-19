# Overkill RE pass16 - BLX decode fixed and resource/game-level mapping split

## What changed

Corrected LEVxBLX decoding is now integrated into the GUI.

The important model:

    BIC type 4 transpose:
    record_i = bytes(raw[field * count + i] for field in range(record_size))

For most decoded BLX resources:

    record_size = 4
    count % 33 == 0

After transpose, group every 33 four-byte records:

    33 × 4 = 132 bytes

Each 132-byte tile record:

    word height       usually 16
    word width_bytes  usually 2
    rows:
        plane0 bytes
        plane1 bytes
        plane2 bytes
        plane3 bytes

So the 128 graphics bytes are row-plane grouped, not contiguous plane blocks.

## Important mapping correction

Resource names are not necessarily game-level numbers.

User noticed:
    LEV0BLX visually appears to be tiles for game level 5.

Confirmed visually:
    LEV1BLX matches the Level 1 / EDRAX screenshot style: grey tech base, blue/red light strips, lava/fire.

The GUI therefore now separates:
    resource name: LEV0BLX, LEV1BLX...
    visual/game level mapping: tentative and adjustable later.

Current tentative default map-to-BLX mapping:

    LEV0MAP -> LEV1BLX   # EDRAX style
    LEV1MAP -> LEV2BLX
    LEV2MAP -> LEV4BLX
    LEV3MAP -> LEV3BLX   # not decoded yet
    LEV4MAP -> LEV0BLX   # user says this looks like level 5/PAX VERDE
    LEV5MAP -> LEV5BLX   # unknown/not decoded yet

This mapping is not final. It is only better than assuming same-number resource pairs.

## Remaining work

- Decode LEV3BLX (record_size=2, count=13530)
- Decode LEV5BLX (record_size=8, count=3531)
- Decode G0.BIC type=3
- Decode G3.BIC record_size=8/count=129
- Decode ENC screen format
- Add GUI dropdown for manual MAP/BLX pairing

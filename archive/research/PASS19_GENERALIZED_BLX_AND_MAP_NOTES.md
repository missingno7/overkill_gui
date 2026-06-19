# Overkill RE pass19 - generalized BLX and MAP/BLX mismatch notes

## Fixes

LEV3BLX now decodes.

Generalized BLX model:

1. BIC type-4 transpose:
   record_i = bytes(raw[field * count + i] for field in range(record_size))

2. Form 132-byte tile records:
   - record_size=4  -> group 33 records
   - record_size=2  -> group 66 records  (LEV3BLX)
   - record_size=8  -> group 33 records into 264 bytes and split into two 132-byte tiles (LEV5BLX)

3. Render each 132-byte tile as:
   word height
   word width_bytes
   row-plane grouped bitmap:
       for each row:
           plane0 bytes
           plane1 bytes
           plane2 bytes
           plane3 bytes

## Current BLX status

- LEV0BLX: decoded, 224 tiles
- LEV1BLX: decoded, 205 tiles
- LEV2BLX: decoded, 199 tiles
- LEV3BLX: decoded, 205 tiles
- LEV4BLX: decoded, 205 tiles
- LEV5BLX: decoded, 214 tiles

## MAP mismatch

The MAP files do not cleanly pair by resource number.

Tile index max values:

- LEV0MAP max=249
- LEV1MAP max=205
- LEV2MAP max=199
- LEV3MAP max=233
- LEV4MAP max=224
- LEV5MAP max=239

But decoded BLX tile counts are:

- LEV0BLX 224
- LEV1BLX 205
- LEV2BLX 199
- LEV3BLX 205
- LEV4BLX 205
- LEV5BLX 214

This means at least one of these must be true:
- MAP values above tile_count are object/special codes, not background tile indices.
- MAP and BLX resource numbering is shuffled.
- There is another lookup/remap table between MAP byte values and BLX tile IDs.
- Some tile graphics are in Gx or another resource, not only BLX.

The GUI still renders MAP using a tentative pairing; manual MAP/BLX pairing should be added next.

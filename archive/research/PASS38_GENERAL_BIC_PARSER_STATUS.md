# Overkill RE pass38 - more complete BIC parser inventory

## Goal

Move toward a systematic BIC dispatcher instead of per-file magic.

This pass resolves several remaining BIC resources into data-derived layouts:
- SHIP.BIC
- MANEXPL.BIC
- THEND.BIC

It also adds a full contact sheet of every BIC resource so regressions are easier to catch.

## Current BIC dispatcher model

### BIC type 4: transposed records

General rule:
    decoded payload is field-major / transposed.
    Reconstruct small records with:
        record_i = bytes(decoded[field * count + i] for field in range(record_size))

But several resources group these small records into larger logical images.

#### 1X1.BIC

Header:
    record_size = 36
    count = 117

Direct type-4 records.
Each record is an 8x8-ish sprite:

    08 00 01 00 + 32 bytes row-plane data

#### 2X2.BIC / 2X2C.BIC

Header:
    record_size = 132
    count = 250 / 130

Direct type-4 records.
Each record:

    10 00 02 00 + 128 bytes row-plane data

Meaning:
    height = 16
    widthBytes = 2
    16x16 sprite

#### LEVxBLX.BIC

Most BLX resources are small-record grouped:
    record_size = 4
    group 33 records -> 132-byte tile

Variants:
    LEV3BLX: record_size=2, group 66 records -> 132-byte tile
    LEV5BLX: record_size=8, group 33 records -> 264 bytes -> two 132-byte tiles

Each tile:
    height,widthBytes header
    row-plane EGA data

#### LEVxMAP.BIC

Type-4 transposed map rows:

    width = 13
    height = 288
    row_y = bytes(decoded[x * 288 + y] for x in range(13))

Preview displays rows reversed for gameplay/editor order.

#### G1/G2/G4/G5

Normal G sheets:
    record_size_word = 516
    count = resource-specific

Each record:
    20 00 04 00
    512 bytes 32x32 row-plane EGA data

#### G3

Special type-4 split:
    record_size = 8
    count = 129
    decoded_size = 1032 = 2 * 516

After type-4 transpose:
    frame A = concat(record[0:4] for record in records)
    frame B = concat(record[4:8] for record in records)

#### SHIP.BIC

New in pass38.

Header:
    record_size = 4
    count = 1452

Because:
    1452 / 33 = 44

Group every 33 small records:

    33 * 4 = 132 bytes

Each logical record:
    10 00 02 00
    128 bytes row-plane data
    16x16 sprite piece

This fixes the previous noisy SHIP preview.

#### MANEXPL.BIC

New in pass38.

Header:
    record_size = 16
    count = 903

Structure:

    903 = 7 prefix records + 28 * 32 data records

The 7 prefix records start with a header-like structure.
The 28 frames are:

    32 records * 16 bytes = 512 bytes image payload

For rendering:
    prepend synthetic normal 32x32 header:
        20 00 04 00

This produces 28 32x32 explosion/object frames.

The prefix is still not fully understood; likely mask/blitter/preamble data.

#### THEND.BIC

New in pass38.

Header:
    record_size = 2
    count = 3522

Concatenating all small records gives one image record:

    2c 00 28 00
    height = 44
    widthBytes = 40 = 320 px
    7040 bitmap bytes

So THEND is one 320x44 row-plane image.

### BIC type 3

#### WINDOW.BIC

Full row-plane image:
    widthBytes = source_data[4] = 40
    height = source_data[5] = 130

Render:
    decoded[:40 * 130 * 4]

#### BLUEBITS.BIC

Same type-3 full row-plane source image:
    widthBytes = 12
    height = 237

In-game animation is probably algorithmic reveal/drawing of this source image, not stored frames.

#### G0.BIC

Special type-3 resource with embedded 32x32 records.

Systematic pass37 fix:
    find embedded headers 20 00 04 00

True record positions:
    504, 1020, 1536, 2052, 2568, 3084, 3600, 4116

So:
    504-byte prefix/preamble
    8 true records * 516 bytes

Final boss body:
    true records 3,4,5,6

Composite:
    top    = merge records 3 + 4 as 64x32 row/plane data
    bottom = merge records 5 + 6 as 64x32 row/plane data
    boss   = top above bottom

### BIC type 0

#### LOGO.BIC

Still unresolved.

Current state:
- does not crash
- shows diagnostic preview
- likely custom/sparse/compiled blitter format
- must be solved by tracing EXE draw routine, not by guessing bitmap layout

## What is now reasonably decoded

Useful visual decoders exist for all BIC files except LOGO.BIC's true pixel format.

Decoded/previewed:
- 1X1
- 2X2
- 2X2C
- BLUEBITS
- G0
- G1
- G2
- G3
- G4
- G5
- LEV0..5 BLX
- LEV0..5 MAP
- MANEXPL
- SHIP
- THEND
- WINDOW

Unresolved:
- LOGO.BIC true type-0 blitter format
- exact G0 504-byte prefix semantics
- MANEXPL 7-record prefix semantics
- BLUEBITS animation algorithm
- exact transparency/mask rules for some sprite resources

## Added previews

- sample_previews/all_bic_pass38_contact.png
- sample_previews/SHIP_group33_16x16_sheet.png
- sample_previews/MANEXPL_prefix7_group32_sheet.png
- sample_previews/THEND_combined_320x44.png
- plus individual pass38 previews for every BIC resource

## Next work

1. Trace LOGO.BIC drawing routine in EXE.
2. Trace G0 final boss draw routine to explain 504-byte prefix and transparency.
3. Trace MANEXPL/explosion draw routine to explain 7-record prefix.
4. Convert these discoveries into clean parser classes:
   - BicType4Transposed
   - BicSpriteSheet
   - BicGroupedSmallRecords
   - BicFullImage
   - BicEmbeddedHeaderRecords
   - BicUnknownType0Logo

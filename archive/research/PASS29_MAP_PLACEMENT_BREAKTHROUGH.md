# Overkill RE pass29 - MAP placement breakthrough

## Critical breakthrough

LEVxMAP.BIC was being interpreted incorrectly.

The MAP resources are also BIC type=4 transposed records.

Example:

    LEV1MAP.BIC
    type = 4
    decoded_size = 3744
    fields_or_count_byte = 13
    block_size = 288

This does NOT mean the decoded payload is already row-major.

Correct interpretation:

    width  = 13
    height = 288

    row_i = bytes(decoded[field * height + i] for field in range(width))

So the decoded stream is column/field-major after RLE, exactly like other type-4 resources.
The previous code treated it as:

    row_i = decoded[i * 13 : (i + 1) * 13]

That was wrong and is why MAP placement did not resemble the game.

## Visual evidence

With direct row-major interpretation, LEV1 looks like random broken placement.

With type-4 row reconstruction, LEV1 becomes coherent:
- vertical walls
- symmetric structures
- empty space columns
- believable shooter map chunks

See previews:

    sample_previews/pass29_LEV1_wrong_direct_map_rows.png
    sample_previews/pass29_LEV1_correct_type4_map_rows.png
    sample_previews/all_levels_correct_type4_map_contact.png

## Correct MAP decode

For every LEVxMAP:

    rows = []
    for y in range(288):
        row = []
        for x in range(13):
            row.append(decoded[x * 288 + y])
        rows.append(row)

## Correct MAP tile lookup

After row reconstruction:

    if 1 <= raw_value <= paired_blx_tile_count:
        tile_index = raw_value - 1
    else:
        cell is special / unknown / object / trigger / non-background data

Do NOT use `(raw & 0x7f)` for normal rendering.

## Why this makes sense

All these resources share the same BIC type-4 transposition idea:

- Sprite sheets: fields are record bytes, records are sprites.
- BLX: fields are small record bytes, grouped into 132-byte tile records.
- MAP: fields are 13 columns, records are 288 rows.

So LEVxMAP.BIC is effectively:

    13 fields × 288 records

not:

    288 sequential rows already laid out.

## Remaining work

- Re-check scroll direction and actual start row after this correction.
- Separate special/out-of-range MAP cells from pure background.
- Add proper mouse inspector for:
    row, col, raw value, tile index, special flag.
- Revisit BLX game-view orientation after the MAP placement fix, because some earlier orientation conclusions were based on wrongly arranged MAPs.
- Continue pre-level formation reverse engineering separately; it is not the scrolling MAP.

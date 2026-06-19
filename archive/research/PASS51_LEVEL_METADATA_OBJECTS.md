# Pass51 - level metadata row and object/enemy overlay research

## User observation

In LEV1MAP the last displayed row is not a normal playfield row:

    display row 287 -> canonical/storage row 0
    raw value at col 0 = 0

The level display is reversed for gameplay preview, so canonical row 0 appears at the bottom.

## Fix: metadata/header row

Several LEVxMAP files have canonical row 0 starting with 0x00. This row is now treated as metadata/header-like and excluded from the playable level render.

Rule:

    if canonical_rows[0][0] == 0:
        skip canonical row 0 for gameplay display

This is deliberately narrow. LEV0 row 0 does not currently match this rule and remains visible.

The inspector now preserves true canonical row indices via `display_canonical_indices`, so row numbers do not become off-by-one after metadata rows are skipped.

## Object/enemy hypothesis

The user's LEV1 example:

    raw MAP value = 0xB1 / 177
    expected 2X2 sprite around 139..141

This gives a very clean mapping:

    177 - 0x26 = 139

So pass51 adds a diagnostic object rule:

    if raw >= 0x80:
        candidate_2x2_sprite = raw - 0x26

This is now shown in the inspector.

## Rendering change

Level renders can now optionally receive a 2X2 sprite sheet. High-value cells are drawn as 2X2 object/enemy sprite candidates using:

    sprite_index = raw - 0x26

The diagnostic overlay marks these cells red.

This is still marked experimental because the exact game spawn/object table is not fully traced yet, but it matches the supplied LEV1 example.

## Disassembly clues

The unpacked EXE contains logic around 0x7b0f that explicitly compares map/object bytes such as:

    cmp al, 0xB1
    cmp al, 0xC9

and other routines around 0xdc93 read object/spawn-like tables into runtime objects.

This supports the idea that high MAP values are not merely BLX tiles; they can be gameplay object/enemy codes.

## Added previews

- sample_previews_pass51/LEV1_pass51_object_overlay.png
- sample_previews_pass51/LEV1_canonical17_object_crop.png
- sample_previews_pass51/2X2_130_149_keyed.png

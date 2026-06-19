# Overkill RE pass39 - MAP inspector, transparency preview, LOGO diagnostics

## User guidance

Screenshots are calibration only. Do not hard-code magic constants from screenshots.
All parser changes in this pass are either UI/diagnostic helpers or derived from file structure.

## GUI changes

### MAP click inspector

The old `Notes` tab was replaced by an `Inspector` tab.

When a LEVxMAP preview is open, click on a cell in either:
- the background render,
- or the diagnostic overlay.

The inspector shows:

- map resource name,
- paired BLX tileset,
- display row/column,
- canonical/storage row,
- pixel position inside the 16x16 cell,
- raw MAP byte value,
- high-bit status,
- tile count,
- decoded tile index,
- tile record length,
- tile header height/widthBytes,
- tile header bytes.

This should make it easy to report bad cells precisely.

### MAP label fix

The preview label no longer says the old/wrong `(byte & 0x7f)-1` rule.
It now says:

    raw 1..tile_count -> tile index raw-1

## Transparency preview

Many sprites use magenta/fuchsia as transparent fill.

Pass39 adds preview-only transparency keying:
- dominant non-gray/non-black corner color -> black,
- known EGA magenta colors -> black.

This is only for display. It does not modify source data.

This makes sheets like 2X2/2X2C/SHIP/MANEXPL easier to inspect.

## LOGO.BIC

LOGO.BIC is still not solved, but it no longer only shows a static text message.

Pass39 now displays:
- type-0 header info,
- candidate dimensions,
- several systematic raw/PackBits row-plane probes.

All probes still look noisy, which reinforces that LOGO.BIC is likely a custom/sparse/compiled blitter format.

Important:
The pass39 LOGO preview is diagnostic, not a final decode.

Next real fix:
Trace the EXE routine that draws LOGO.BIC and implement that type-0 blitter.

## MANEXPL.BIC

The current MANEXPL decode is improved but still marked partly uncertain.

Known structure:
    type=4
    record_size=16
    count=903
    903 = 7 prefix records + 28 * 32 data records

Current preview:
    prefix_count = len(records) % 32 = 7
    each 32-record group becomes one 512-byte 32x32 frame payload
    synthetic header 20 00 04 00 is prepended for preview

Unresolved:
    exact meaning of the first 7 prefix records,
    whether frame numbering/indexing should start after prefix or if the prefix is part of a blitter/mask table.

## Still unresolved

- LOGO.BIC true type-0 blitter format.
- MANEXPL 7-record prefix semantics and possibly frame indexing.
- G0 504-byte prefix/preamble semantics.
- BLUEBITS animation/reveal algorithm.
- exact mask/transparency behavior used by game blitters.

## Added/updated previews

- sample_previews/all_bic_pass39_contact.png
- LOGO.BIC_pass39_preview.png now includes diagnostic probes
- MAP previews now support click inspector in the GUI

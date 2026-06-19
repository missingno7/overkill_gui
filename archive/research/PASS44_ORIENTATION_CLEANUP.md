# Overkill RE pass44 - orientation cleanup

## User observation

Several resources were upside-down in the GUI:

- MANEXPL.BIC
- G sheets
- 2X2.BIC / 2X2C.BIC
- THEND.BIC

WINDOW.BIC was correct.

This pointed to an over-broad orientation correction, not a per-resource data problem.

## Root cause

The generic planar renderer contained a global vertical flip:

    render_planar_4bpp(...)
        img = ega_image(...)
        img = img.transpose(FLIP_TOP_BOTTOM)
        return img

This was introduced while investigating level/BLX orientation, but it affected every resource using the generic planar renderer:

- 1X1
- 2X2
- 2X2C
- G0/G1/G2/G3/G4/G5
- MANEXPL
- SHIP
- THEND

WINDOW.BIC stayed correct because it uses its own type-3 full-image renderer and did not go through render_planar_4bpp().

## Fix

Removed the global vertical flip from render_planar_4bpp().

New rule:

    generic planar renderer = raw orientation only
    orientation corrections must be resource-specific

If a resource later proves that it needs a vertical flip, the flip must be applied in that resource's parser/renderer, not in the shared low-level function.

## Result

The following previews now render upright:

- 2X2.BIC
- 2X2C.BIC
- G sheets
- MANEXPL.BIC
- SHIP.BIC
- THEND.BIC

WINDOW.BIC remains unchanged and still renders correctly as 320x200.

LEVxBLX / LEVxMAP rendering is unchanged by this fix, because BLX tiles use their own render_blx_tile_record() path, not render_planar_4bpp().

## Added previews

- sample_previews/all_bic_pass44_orientation_contact.png
- sample_previews/orientation_focused_pass44.png
- sample_previews/2X2.BIC_pass44_orientation_preview.png
- sample_previews/G1.BIC_pass44_orientation_preview.png
- sample_previews/MANEXPL.BIC_pass44_orientation_preview.png
- sample_previews/THEND.BIC_pass44_orientation_preview.png
- sample_previews/WINDOW.BIC_pass44_orientation_preview.png

## Remaining caution

Some complex resources still need exact blitter/mask semantics:

- LOGO.BIC type-0 renderer
- BLUEBITS.BIC reveal animation
- G0 504-byte prefix/blitter data

But the broad upside-down issue was caused by the shared renderer flip and is fixed here.

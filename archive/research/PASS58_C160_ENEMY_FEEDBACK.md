# Pass58 - c160 enemy feedback correction

## User feedback

In the screenshot section around c160, there are four enemies using:

    2X2 sprites 147, 148, 149, 150

The previous pass57 observation labels were wrong because they guessed 2X2 68-70 for this screenshot.

## Update

The four off-grid screenshot markers were kept at the same approximate pixel positions, but their metadata now says:

    sprites = [147, 148, 149, 150]
    canonical_section = 160

Labels in the GUI were shortened to E1..E4 to avoid clutter.
Metadata still stores the full sprite list and notes.

## Important interpretation

This strengthens the current model:

    enemy positions are off-grid runtime objects

They are not directly rendered from LEV1MAP cells.
The section marker c160 is useful for correlating screenshot scroll position with canonical map rows, but the enemy coordinates are pixel-level, not tile-grid-level.

## Files

Updated:

    research_overlays/level_observations.json

Added previews:

    sample_previews_pass58/2X2_sprites_147_150.png
    sample_previews_pass58/LEV1_c160_offgrid_enemies_147_150_overlay.png
    sample_previews_pass58/LEV1_c160_offgrid_enemies_147_150_crop_3x.png

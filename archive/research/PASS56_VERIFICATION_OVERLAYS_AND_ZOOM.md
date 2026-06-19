# Pass56 - verification overlays and default zoom

## Goal

Give the user something concrete to verify in the GUI without pretending that the runtime enemy layer is solved.

## GUI changes

Level Viewer now defaults to 3x zoom.

A Zoom dropdown was added:

    1x, 2x, 3x, 4x, 5x

Default:

    3x

Click handling is zoom-aware:
the canvas displays the scaled image, but inspector coordinates are converted back to original level-image pixels before MAP cell calculation.

## New overlay toggles

The right-side Level Viewer panel now has:

- Show MAP special markers
- Show red debug overlay
- Show grid
- Show research observations
- Show canonical row ruler

Default:
- research observations: on
- canonical row ruler: on
- zoom: 3x

## Research observations

Observations are stored outside parsers:

    research_overlays/level_observations.json

Current observation:

    LEV1 canonical row 125, col 2:
        reported enemy uses 2X2 sprites 68,69,70
        reported drop sprite 71
        clicked MAP value is 0x01

This marker is drawn as a cyan/yellow target on the terrain.
It is intentionally not parsed as an enemy object.

## Why this helps

The user can now open Level Viewer and verify:
- the exact reported location,
- canonical row alignment,
- whether the marker is on the correct apparent in-game position,
- whether additional observations should be added/corrected,
- whether enemy positions are tied to scroll/canonical rows, not MAP bytes.

## Important interpretation

This pass does not add a fake enemy overlay.

It adds a feedback/annotation layer for observations so we can build a real runtime spawn layer later.

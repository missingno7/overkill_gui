# Pass53 - calibrated enemy mapping and nearby inspector

## User observation

A visible enemy uses 2X2 sprites 68, 69, 70 near this clicked MAP cell:

    LEV1MAP.BIC
    display row = 162
    canonical row = 125
    col = 2
    raw = 0x01

The clicked cell itself is terrain/empty (raw 0x01), so the enemy cannot be encoded only by the clicked cell's MAP value.

## Nearby data

Around canonical row 125:

    row 121: 92 93 95 ...
    row 123: 92 93 95 ...
    row 125: 92 93 01 ...

This gives a calibrated mapping:

    raw 0x92 -> 2X2 sprite 68
    raw 0x93 -> 2X2 sprite 69
    raw 0x95 -> 2X2 sprite 70

The sprite visually overlaps adjacent terrain cells, so clicking a raw 0x01 cell can still hit the visible enemy.

## Update

Added `KNOWN_OBJECT_SPRITE_MAP` in `overkill/core.py`:

    0x92 -> 68
    0x93 -> 69
    0x95 -> 70
    0xB1 -> 139
    0xB2 -> 140
    0xB3 -> 141

The old raw-0x26 mapping is now explicitly a diagnostic fallback, not the primary rule.

## Inspector

MAP inspector now includes:

    Nearby object candidates within radius 3

This helps diagnose cases where the clicked cell is raw 0x01 but a nearby object code draws a sprite overlapping it.

## Remaining research

This still does not prove the full enemy table.
It only confirms that there are calibrated object codes and that enemy sprites are rendered as an overlay layer over terrain.

Next step:
Find the actual object/enemy lookup table in EXE or data that maps raw MAP codes to 2X2 sprite frames and behavior.

# Suspected position layers

## Layer types

### Observation layer

Source:

    research_overlays/level_observations.json

Drawn as orange/yellow crosshair markers.

Contains manually observed approximate positions, e.g. c160 enemies.

### Runtime candidate layer

Source:

    research_overlays/runtime_formation_candidates.json

Drawn as magenta trigger lines/placeholders.

Contains disassembly-derived formation candidates, e.g. scroll trigger + DS table pointer.

## Current c160 points

    E1: level_x=70,  level_y=2109
    E2: level_x=86,  level_y=2104
    E3: level_x=119, level_y=2104
    E4: level_x=135, level_y=2107

## Current unresolved formation table

    id: scroll_0xEA0_table_4_objects
    trigger: 0x2350 == 0x0EA0
    table: DS:0xA3EE
    count: 4
    record: 3 words

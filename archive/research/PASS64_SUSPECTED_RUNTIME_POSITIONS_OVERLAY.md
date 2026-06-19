# Pass64 - suspected runtime positions overlay

## User question

Do we have any suspected positions that can be shown?

## Answer

Yes, in two categories:

1. **Observed off-grid positions**
   - these are manually derived from screenshots/user feedback;
   - they are already approximate level-pixel positions;
   - example: c160 section, four enemies E1..E4, sprites 2X2 147..150.

2. **Disassembly-derived runtime formation candidates**
   - these have known trigger/code/table shape;
   - actual object coordinates may still be unknown;
   - example: scroll 0xEA0, DS:0xA3EE, 4 objects, 3 words per object.

## GUI change

Added a Level Viewer toggle:

```text
Show suspected runtime formations
```

Default: ON.

It draws:
- magenta trigger lines for known scroll-triggered runtime formation candidates;
- magenta/yellow placeholder object markers where the count is known but table contents are not decoded;
- existing orange/yellow off-grid observation markers remain under "Show research observations".

## Current visible markers

### c160 user-observed enemies

From `research_overlays/level_observations.json`:

```text
LEV1 c160-ish section
E1..E4
approx level-pixel points:
    (70,2109)
    (86,2104)
    (119,2104)
    (135,2107)
sprites:
    2X2 147..150
formula hypothesis:
    object+0x08 = 0x93 + [0x233C]
```

These are approximate and meant for user feedback.

### scroll 0xEA0 runtime formation

From `research_overlays/runtime_formation_candidates.json`:

```text
trigger:
    0x2350 == 0x0EA0

object count:
    4

data table:
    DS:0xA3EE

record format:
    word0 -> object+0x02
    word1 -> object+0x04
    word2 -> object+0x08
```

Because the table contents are not decoded yet, the overlay draws a magenta trigger line and four placeholder markers.

## Added previews

```text
sample_previews_pass64/LEV1_suspected_positions_runtime_candidates.png
sample_previews_pass64/LEV1_c160_suspected_positions_crop_3x.png
sample_previews_pass64/LEV1_scroll_0xEA0_candidate_crop_3x.png
```

## Important caveat

The magenta 0xEA0 placeholders are not real decoded x/y positions.
They mean:

```text
there is a real 4-object formation trigger here,
but DS:0xA3EE has not been decoded yet
```

The orange c160 markers are approximate observed positions from screenshot alignment.

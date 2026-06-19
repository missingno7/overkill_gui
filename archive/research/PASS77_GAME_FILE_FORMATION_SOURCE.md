# Pass77 - game-file source probe for moving formations

## Goal

Move the level viewer away from predecoded research JSON files and toward direct game-file parsing for static enemies and moving formations.

## Findings

`LEVxMAP.BIC` static event bytes can be decoded directly from the archive resource data. The viewer now scans all levels with the generic static MAP event table instead of preferring `decoded_map_events_LEV1.json`.

The ordinary moving formation parser from pass75 is now implemented in `overkill.core` as a normal byte parser for:

```text
spawn streams:       0x12D7D..0x13249
formation table:     0x13249..0x136DD
```

The shipped `game_data/OVERKILL` and `game_data/OVERKILL.EXE` files are packed executable images. A conservative LZEXE-style load-module decoder has been added and is probed before falling back to the pass75 artifact data. The current packed-file load modules still do not expose the pass75 table at those raw offsets, so the exact bridge from shipped file to the larger unpacked/runtime artifact remains the next research item.

## Current viewer behavior

1. Static map events: direct from `LEVxMAP.BIC`.
2. Moving enemy formations: tries direct executable byte sources and LZEXE load modules first.
3. If those sources do not match the known pass75 layout, the viewer uses the existing pass75 JSON artifact temporarily and reports that source in the inspector.

## Next step

Trace how the larger pass75 executable/runtime artifact was produced from the shipped packed files, or identify the runtime copy/decompression path that creates the DS table containing the moving formation streams.

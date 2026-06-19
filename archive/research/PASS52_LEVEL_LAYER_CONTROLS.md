# Pass52 - Level layer controls and object-layer interpretation

## User observation

Fixed cannons/enemies appear to overlay the terrain:
- when the object is destroyed, the background tile remains,
- some enemies appear over black space with no terrain,
- therefore the object/enemy visual layer should not replace the MAP/BLX tile layer.

## Interpretation update

The previous pass rendered experimental object candidates as replacements for the terrain tile.
That was wrong for fixed cannons and likely wrong in general.

New rule:

    pass 1: render terrain/background from LEVxMAP + LEVxBLX
    pass 2: optionally overlay experimental object/enemy sprites

The current object overlay is still diagnostic:

    candidate 2X2 sprite index = raw MAP value - 0x26

This is based on the LEV1 observation:
    raw 0xB1 -> 177 - 0x26 = 139

But it is not yet a final enemy parser.

## Separate layer question

No separate enemy resource file has been identified yet in the archive.
The archive contains LEVxMAP and LEVxBLX pairs but no obvious LEVxOBJ/LEVxENEMY file.

The disassembly has relevant clues:
- comparisons against values such as 0xB1 and 0xC9,
- several references to 0x26,
- high MAP values are likely interpreted by gameplay code as objects/spawns/triggers.

So the likely model is:

    MAP still contains object/spawn codes or references,
    but gameplay draws those as a sprite layer over the terrain.

This explains why a cannon can leave the underlying terrain tile after being destroyed:
the terrain tile is rendered independently, while the object sprite is transient/game-state controlled.

## GUI changes

Level Viewer now has a right-side "Level layers" panel with toggles:

- Show experimental enemies/objects
- Show red debug overlay
- Show grid

Defaults:
- enemies/objects: off
- red debug overlay: off
- grid: off

This keeps the normal level view clean.

## Rendering changes

`render_level_from_map_and_tiles(...)` now accepts:

    show_objects: bool
    show_grid: bool

The terrain pass always renders valid MAP tile values as BLX tiles.

The object overlay pass only runs when enabled, and pastes sprites with a non-black mask so objects can overlay terrain instead of replacing it with a black box.

## Debug overlay

The red high-value/object-candidate overlay is no longer always shown in Level Viewer.
It is controlled separately by the "Show red debug overlay" toggle.

## Remaining research

1. Find the exact gameplay routine that interprets MAP high values.
2. Confirm whether high MAP values encode:
   - direct object type,
   - object type + terrain index,
   - spawn script/event reference,
   - or another lookup table.
3. Determine exactly which 2X2 sprite indices belong to:
   - enemies,
   - player upgrades,
   - dropped pickups,
   - explosions,
   - UI/panel art.
4. Identify why collectible sprites 59..62 drop only from certain enemies.

## Added previews

- sample_previews_pass52/LEV1_terrain_only.png
- sample_previews_pass52/LEV1_experimental_objects_overlay.png
- sample_previews_pass52/LEV1_terrain_grid.png
- sample_previews_pass52/LEV1_debug_overlay.png
- sample_previews_pass52/LEV1_combined_objects_debug.png
- sample_previews_pass52/LEV1_canonical17_col3_object_overlay_crop.png

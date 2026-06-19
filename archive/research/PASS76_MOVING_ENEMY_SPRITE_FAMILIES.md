# Pass76 - moving enemy behavior → sprite-family research

## What changed

The moving-enemy placement stream is already decoded.  
This pass starts attaching **sprite families / animation frame ranges** to the decoded moving enemy behaviors.

The important distinction is:

```text
spawn stream record
    says when, where, and which behavior spawns

behavior handler
    decides which 2X2.BIC sprite/frame the object uses over time
```

So placement and sprite assignment are related, but not stored in the same structure.

## Confirmed sprite families

### Behavior 0x2D — blue LEV1 formation

```text
2X2:147..150
```

Evidence:

- Runtime dump of the LEV1 blue 4-enemy formation showed behavior `0x2D` and sprite `149`.
- User confirmed the visual family is `2X2:147–150`.
- A static sprite formula candidate exists at raw `0x8615`:

```asm
AX = [0x233C] + 0x93
object.sprite = AX
```

Since `[0x233C]` cycles `0..3`, that is:

```text
0x93..0x96 = 147..150
```

I still keep the CFG ownership of this exact formula marked as “tightening”, but the sprite family itself is confirmed by runtime.

### Behavior 0x8B — green enemy

```text
2X2:101..104
```

Evidence:

- Runtime dump showed behavior `0x8B`, sprite `104`.
- User identified the family as `2X2:101–104`.
- Static code around raw `0xB1CB..0xB1F5` computes the same range for the `state=0` case.

## Strong static sprite-family candidates

These are not yet runtime-confirmed, but their formulas are explicit.

| Behavior | Candidate frames | Formula |
|---|---:|---|
| `0x89` | `28..31` | `0x1C + [0x233C]` |
| `0x30` | `16..19` | `0x10 + [0x233C]` |
| `0x19` | `54..58` | `0x36 + [0x233A]` |
| `0x1A` | `36..41` | `0x24 + [0x2338]` |
| `0x1B` | `39..44` | `0x27 + [0x2338]` |
| `0x3B` | `81..86` | `0x51 + [0x2338]` |
| `0x8C` | likely `93..96` | sibling formula of `0x8B`, sign/control word `-1` |

Animation counter facts from the earlier counter analysis:

```text
[0x2338] cycles 0..5
[0x233A] cycles 0..4
[0x233C] cycles 0..3
```

## More complex cases found

Some behaviors are clearly not a single simple contiguous frame range:

- `0x30` has a primary `16..19` animation but later also writes sprite `110`.
- `0x40` has a phase that computes `128..135`, but also uses a DS lookup-table-driven frame path.
- `0x83` computes either `259..260` or `376..377` depending on level.
- Several behaviors (`0x32`, `0x37`, `0x3A`, `0x3E`) use lookup-table-driven frame expressions.

I did **not** guess those into simple ranges where the code says they are more complex.

## New data files

```text
research_overlays/moving_enemy_sprite_family_hints.json
research_overlays/moving_enemy_behavior_handler_sprite_evidence.json
```

The first is a practical GUI-facing hint table.  
The second preserves the raw handler mapping and sprite-write evidence.

## GUI update

The Level Viewer moving-enemy overlay now appends sprite hints when known.

Example label:

```text
0x2D×4 t130 2X2:147–150
```

This should make it much easier to visually validate event types against the level.

## Files added

```text
archive/research/PASS76_MOVING_ENEMY_SPRITE_FAMILIES.md
archive/analysis/pass76/moving_enemy_sprite_family_hints.tsv
archive/analysis/pass76/sprite_formula_*.txt
sample_previews_pass76/PASS76_sprite_family_research_card.png
```

## Best future runtime verification targets

The most useful next dumps/screenshots would be visible instances of:

```text
behavior 0x89  expected sprites 28..31
behavior 0x30  expected sprites 16..19
behavior 0x19  expected sprites 54..58
behavior 0x8C  expected sprites 93..96
```

The GUI overlay can now tell us where these should spawn.

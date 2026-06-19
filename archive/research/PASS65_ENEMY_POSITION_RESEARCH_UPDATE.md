# Pass65 - enemy position research update

## User feedback

The previously shown magenta runtime candidates were not useful:

```text
User does not see anything like that in the game.
```

So the editor should not show them as if they are real positions.

## GUI change

The `Show suspected runtime formations` overlay is now OFF by default.

The c160 observed screenshot markers remain useful because they came from user screenshot feedback.
The 0xEA0 candidate remains in JSON only as a code-pattern candidate, not as a visually trusted overlay.

## Important correction

The `scroll 0xEA0 -> DS:0xA3EE -> 4 objects` routine is a real code pattern, but it is **not visually correlated** with the current known LEV1 screenshots.

So its status is now:

```text
code_pattern_found_but_not_visually_correlated
```

That means:
- keep it for RE notes,
- do not trust it as a level overlay yet,
- do not treat row16 = scroll/16 as canonical map row.

## More precise scroll finding

The scroll/update manager around `0x9D4A..0x9EC0` shows that `0x2350` is a runtime scroll/progress variable updated in steps of `0x0D`, not a direct simple `canonical_row * 16` coordinate.

Relevant code:

```asm
9d69: addw $0x0D,0x2350
9da8: addw $0x0D,0x2350
9df3: subw $0x0D,0x2350
9e16: subw $0x0D,0x2350
```

Therefore my earlier drawing:

```text
trigger y = trigger_value / 16
```

was too naive.

This explains why the magenta line did not match what the user sees.

## Level data check

I checked the archive-level data again:

```text
LEVxMAP.BIC
LEVxBLX.BIC
2X2.BIC
OPAGE/IPAGE/PLAQ/ENC resources
```

Current conclusion:

- `LEVxMAP.BIC` does not contain a second hidden enemy layer after the 13*288 map payload.
- `LEVxBLX.BIC` are background tile sets.
- `2X2.BIC` contains sprite frames, not placements.
- no obvious `LEVxOBJ` / `LEVxENEMY` / per-level coordinate resource exists in the archive.
- enemies/positions are probably driven by EXE runtime object/spawn code and runtime DS tables/pointers.

## What is more likely now

There are probably multiple systems:

1. **Terrain:** `LEVxMAP + LEVxBLX`
2. **Sprites:** `2X2.BIC`
3. **Runtime object spawns:** EXE code, object slots, behavior dispatch
4. **Some formation/script data:** runtime DS tables or pointer structures, not directly visible as flat archive files

## Practical next target

The best next RE target is not drawing arbitrary scroll candidates, but decoding one concrete runtime object source.

Candidates:

### A. c160 observed formation

Known:

```text
4 off-grid enemies
sprites 2X2:147..150
sprite formula: object+0x08 = 0x93 + [0x233C]
```

Need to find:
- which behavior entry owns that formula,
- where its object slots are allocated,
- where x/y are set.

### B. object creation paths around `0x9A0D..0x9A5D`

These use runtime pointers:

```text
DS:0xA962..DS:0xA96C
positions from SI+0x02 and SI+0x04
```

This looks more promising for real placements than the misleading 0xEA0 row marker.

### C. runtime memory dump

Still the fastest way to break this open:

```text
dump object slots while c160 enemies are visible
```

Then we can read actual `object+0x02`, `object+0x04`, `object+0x08`, `object+0x18` and trace back to the creating routine.

## Added files

```text
archive/research/PASS65_ENEMY_POSITION_RESEARCH_UPDATE.md
archive/analysis/pass65/scroll_manager_9d4a_9ec0.txt
archive/analysis/pass65/level_runtime_trigger_contexts_5da9_5ec8.txt
archive/analysis/pass65/scroll_trigger_values.txt
archive/analysis/pass65/resource_inventory_enemy_data_check.md
```

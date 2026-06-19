# Pass61 - pickup/drop formula breakthrough

## Main breakthrough

Found a strong formula for pickup/drop sprites.

At `0xDE61..0xDE67`:

```asm
de61: mov 0x6(%bp), %ax
de64: add $0x3b, %ax
de67: mov %ax, 0x8(%bp)
```

So:

```text
object +0x08 = object +0x06 + 0x3B
```

Since `0x3B` decimal is `59`, this means:

```text
2X2 sprite = drop_state_or_type + 59
```

Examples:

```text
state 0  -> 2X2:59
state 1  -> 2X2:60
state 2  -> 2X2:61
state 3  -> 2X2:62
state 12 -> 2X2:71
```

This lines up very well with your observation:

```text
some collectibles are 2X2:59..62
the c160 enemy drops 2X2:71
```

The reported drop `2X2:71` is explained if the pickup/drop object has:

```text
object +0x06 = 12
```

## Behavior 0x93 connection

Nearby code at `0xDE86` sets:

```asm
de86: movw $0x93, 0x18(%bp)
```

Given pass60 confirmed:

```text
object +0x18 = behavior/type dispatch
```

this strongly suggests behavior `0x93` is involved in a pickup/drop object lifecycle.

The update region `0xDE8C..0xE09E` then looks like pickup movement/collection/check logic. It repeatedly calls a far routine with `AX=0xAFD8`, changes `object +0x06`, and later computes sprite frames.

## Important correction

This does not yet tell us which enemy drops which item, but it explains how the dropped item sprite is selected once the drop object exists.

So the model becomes:

```text
enemy behavior / death routine
    decides drop_state/type, probably stores it into object +0x06
drop behavior 0x93
    renders sprite = object +0x06 + 59
```

## BIC/game-data check

I also verified the compressed `.BIC` payload boundaries.

For `LEVxMAP.BIC`, there is no meaningful trailing second layer after the MAP payload. The trailing byte is essentially a final `0x80` no-op/alignment byte.

So enemies are still not hidden after the MAP payload.

## New runtime hypothesis

Updated:

```text
research_overlays/runtime_spawn_hypotheses.json
```

with:

```text
pickup_drop_sprite_formula:
    object +0x08 = object +0x06 + 0x3B
```

## Files added

```text
archive/analysis/pass61/pickup_drop_behavior_0x93_de40_e0b0.txt
archive/analysis/pass61/object_initializers_0x28_0x2a_0x8f_0x29_0x2b_0x93.txt
archive/analysis/pass61/bic_trailing_payload_check.md
archive/research/PASS61_PICKUP_DROP_FORMULA.md
```

## Next target

Find the death/drop routine that creates the pickup object and sets:

```text
object +0x06 = drop_type
```

Specifically, for your c160 enemy:

```text
drop sprite 71 -> drop_type 12
```

So searching for assignments of `+0x06 = 0x0C` or computed values leading to `0x0C` near enemy death logic is now a concrete next step.

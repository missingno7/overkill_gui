# Pass60 - object behavior dispatch and enemy storage research

## What improved

Pass59 found the c160 enemy sprite formula:

    object +0x08 = 0x93 + [0x233C]

Pass60 found the main object behavior dispatch mechanism.

## Main object dispatch

The EXE has a central object behavior dispatcher:

    d1e3: mov 0x18(%bp), %bx
    d1e6: shl $1, %bx
    d1e8: jmp *%cs:[table + bx]

This confirms:

    object +0x18 = behavior/type dispatch field

The flat unpacked table is visible around 0xD1ED.

Important decoded entries include:

    behavior 0x28 -> 0x8676
    behavior 0x29 -> 0x8721
    behavior 0x2A -> 0x8676
    behavior 0x2B -> 0x8715
    behavior 0x7A -> 0x870C
    behavior 0x7C -> 0x8707
    behavior 0x8F -> 0x8769
    behavior 0x93 -> 0x8D5F
    behavior 0x9D -> 0x83D2

## Important correction

The c160 sprite formula at 0x8615:

    object +0x08 = 0x93 + [0x233C]

is inside the large behavior-code region but has not yet been mapped cleanly to a single behavior table entry.

The likely explanations are:

1. It is reached by fall-through from a behavior handler.
2. It is a sub-state branch inside a larger behavior routine.
3. Some disassembly offsets are slightly misaligned around table/code boundaries.
4. It is used by a related but not identical enemy class.

So the formula is solid, but the owning behavior type is still unresolved.

## Possible scripted/formation system

A promising area is behavior 0x9D:

    behavior 0x9D -> 0x83D2

This code touches structures around:

    0x9682
    0x968C
    0x9696
    0x96A0

and uses a script-like update flow with function pointers/calls.

This may be related to enemy formations or scripted object groups. It is not yet proven to be the c160 formation.

## What this means for the overlay

We still should not auto-generate enemies from MAP bytes.

Current reliable overlay types are:

1. terrain/background from MAP+BLX,
2. manual research observations,
3. runtime-spawn hypotheses from disassembly.

The next overlay should probably be a "Runtime hypotheses" layer, showing known observed formations and formulas, not pretending to know all object positions.

## Next target

Trace object creation and initialization for the c160 formation:

- find where object +0x18 is assigned the behavior that reaches 0x8615/0x93 frames,
- find where object +0x02 and +0x04 are initialized,
- connect the formation to scroll/canonical section c160,
- locate possible script/formation tables around 0x9682..0x96A0 or related data.

## Added files

    archive/analysis/pass60/main_object_behavior_dispatch_d1e3_table.md
    archive/analysis/pass60/behavior_dispatch_table_decoded.txt
    archive/analysis/pass60/behavior_region_84d0_8725.txt
    archive/analysis/pass60/script_or_formation_system_81e0_8455.txt
    archive/analysis/pass60/object_loop_and_updates_9e89_a06e.txt
    research_overlays/runtime_spawn_hypotheses.json

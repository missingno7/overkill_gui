# Runtime object pool dump target

Strongest practical target:

```text
DS:23B4 .. DS:32CB
```

Length:

```text
0x0F18 bytes
```

Object slot size:

```text
0x38 bytes
```

Pools:

```text
Pool A: DS:23B4 .. DS:2B5B, 35 slots
Pool B: DS:2B5C .. DS:32CB, 34 slots
```

Fields:

```text
+00 active
+02 y / vertical position
+04 x / horizontal position
+06 state / drop type / animation substate
+08 sprite / frame
+16 class/layer-ish
+18 behavior/type dispatch
+32 target/aux y
+34 target/aux x
+36 sprite backup / aux
```

Use:

```bash
python tools/convert_runtime_object_dump.py dump.bin --binary -o research_overlays/runtime_object_slots.json
```

Then open Level Viewer and enable:

```text
Show runtime object dump
```

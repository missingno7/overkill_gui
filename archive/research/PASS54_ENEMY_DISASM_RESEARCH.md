# Pass54 - enemy/object encoding research

## Why the previous overlay was wrong

The broad `raw MAP value -> 2X2 sprite` overlay produced many false enemies.
The reason is simple: in levels such as EDRAX, values like `0x92` are valid terrain tile IDs because LEV1BLX has 205 tiles.
A MAP value in `1..tile_count` must be treated as background terrain unless runtime code proves otherwise.

So the pass53 calibrated mappings such as `0x92 -> sprite 68` were removed from rendering. They were useful observations, but not valid MAP decoding rules.

## Important disassembly findings

### 1. There is an object slot system independent of MAP/BLX rendering

The object dispatcher loop around load-image address `0x9e4e` iterates object slots and dispatches through field `+0x16`:

```asm
9e53: mov cx,bx
9e58: mov -0x72ee(bx),bp   ; object pointer table
9e5c: cmp word ptr [bp+0],0
9e62: call 0x9e6e
9e6e: mov [bp+0x16], bx
9e73: jmp cs:[bx + dispatch_table]
```

Object structs are still consistent with the earlier 0x38-byte model:

- `+0x00` active
- `+0x02` y/vertical position
- `+0x04` x/horizontal position
- `+0x08` sprite/animation frame-ish value
- `+0x16` dispatch/state class
- `+0x18` behavior/object type
- `+0x20` speed/direction-ish value
- `+0x32/+0x34` target/destination coordinates

### 2. There are runtime spawns not derived directly from visible MAP cells

Code around `0xa8ce..0xaa58` is a runtime/formation spawn system driven by level number and timers:

- `0x2356` = current level/theme id
- `0xa7a0` = frame/timer counter
- objects are allocated and then fields like `+0x18`, `+0x08`, `+0x20`, `+0x32`, `+0x34` are set explicitly

Examples:

```asm
a9cd: mov word ptr [bp+0x18],0x22
a9d2: mov word ptr [bp+0x08],0x71
a9e4: mov word ptr [bp+0x04],0x60

aa42: mov word ptr [bx+0x18],0x61
aa47: mov word ptr [bx+0x08],0xe7
```

This explains enemies in empty space: they can be spawned by code/tables and are not necessarily present in LEVxMAP.

### 3. `0x92` is a runtime object type, not proof of MAP sprite 68

Routine around `0xb6a2` spawns/initializes a child object and then checks the **parent object's `+0x18` behavior field**:

```asm
b6fb: mov [bp+0x18], bx
b6fe: cmp bx,0x92
b704: jmp special_case_0x92
```

So `0x92` is meaningful in the object system, but not as a direct MAP byte -> sprite mapping. The same number can appear as a perfectly valid MAP tile ID.

### 4. MAP has a separate special-value scan, but it is not the enemy table

The routine around load-image address `0x4b48` scans roughly `0x9c` bytes around the current map pointer and compares MAP bytes against a per-level special table:

```asm
4b56: si = [0x2350]
4b5a: cx = 0x9c
4b6e: al = es:[si]
4b73: cmp ax, cs/table_value
4b78: jmp handler
```

Some handlers rewrite MAP bytes to `0x28` or `0x01`. This looks like terrain/special-cell processing, not a full enemy placement table.

## Editor change

The Level Viewer no longer draws experimental enemy sprites from MAP values. The right-side checkbox now shows only MAP special/out-of-range markers.

Current safe interpretation:

```text
LEVxMAP + LEVxBLX = terrain/background
runtime object system = enemies, bullets, pickups, formations
MAP special scan = terrain/special-cell triggers, not direct sprite placement
```

## What remains to solve

1. Identify the exact table/routine that creates enemies during the scrolling phase.
2. Decode object behavior type `+0x18` and sprite/animation field `+0x08`.
3. Determine where level-specific enemy spawn scripts/tables live in the EXE/data segment.
4. Reintroduce an enemy overlay only after the actual spawn table is decoded.

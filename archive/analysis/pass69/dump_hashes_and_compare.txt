# Pass69 - second uploaded MEMDUMP comparison

## Result

The newly uploaded `MEMDUMP.BIN` is **byte-for-byte identical** to the first uploaded dump.

```text
first dump sha256  = 6f3f59be57d20ac34cd6246ec7f1af673d0215c7742fe00c51eb14582bcf20ae
second dump sha256 = 6f3f59be57d20ac34cd6246ec7f1af673d0215c7742fe00c51eb14582bcf20ae
identical          = True
```

## Consequence

The second uploaded file does **not** reflect the screenshot with:

- 3 blue enemies visible
- 1 green enemy visible
- DS = 2C41

Instead it decodes to the same 6 active objects as before, including the same four blue enemies:

```text
A14: x= 64, y=54, sprite=149, behavior=0x2D
A15: x= 80, y=50, sprite=149, behavior=0x2D
A16: x=112, y=50, sprite=149, behavior=0x2D
A17: x=128, y=54, sprite=149, behavior=0x2D
```

and **no green enemy**.

## Most likely explanations

1. The uploaded file was the old `MEMDUMP.BIN` again.
2. DOSBox-X wrote the new dump to a different directory than expected.
3. The file was not copied/renamed immediately and got mixed up.

## Practical advice for the next dump

Right after running the dump command, immediately rename/copy the file to a unique name, for example:

```text
MEMDUMP2.BIN
```

or outside DOSBox:

```bash
copy MEMDUMP.BIN MEMDUMP_2C41_GREEN.BIN
```

If possible, also send the file size and modification timestamp.

## Best next target

Please make a fresh dump when the green enemy is visible, then upload that uniquely named file.
The expected command is still:

```text
MEMDUMPBIN 2C41:23B4 F18
```

(or using the current DS shown by the debugger).

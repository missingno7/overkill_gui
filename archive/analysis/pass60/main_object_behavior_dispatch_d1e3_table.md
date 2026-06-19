# Main object behavior dispatch

Disassembly:

```
d1e3: mov 0x18(%bp), %bx
d1e6: shl $1, %bx
d1e8: jmp *%cs:[table + bx]
```

In the flat unpacked file, the table appears directly after the jump instruction at approximately 0xD1ED.

Relevant decoded entries:

- behavior 0x28 -> 0x8676
- behavior 0x29 -> 0x8721
- behavior 0x2A -> 0x8676
- behavior 0x2B -> 0x8715
- behavior 0x7A -> 0x870C
- behavior 0x7C -> 0x8707
- behavior 0x8F -> 0x8769
- behavior 0x93 -> 0x8D5F
- behavior 0x9D -> 0x83D2

This confirms object +0x18 is the primary behavior dispatch field.

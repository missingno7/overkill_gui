# Pass70 - segment breakthrough from MEMDUMP2

## What happened

`MEMDUMP2.BIN` is **not** the same as the first good object-pool dump, but it also does **not** decode as a valid object-pool dump.

The key clue is in the debugger screenshot:

```text
DS = 2C41
SS = 1F0D
```

In the first successful dump, the register state happened to be:

```text
DS = 1F0D
SS = 1F0D
```

So the first time, dumping `DS:23B4` worked only because `DS` and `SS` were equal.

## New conclusion

The runtime object pool is very likely in the program's stable data segment / DGROUP, which matches **SS** here, not the transient **DS** used during the blit routine.

That means the correct dump target should be:

```text
SS:23B4 .. SS:32CB
```

or concretely for the screenshot with the green enemy:

```text
1F0D:23B4 length F18
```

## Why MEMDUMP2 looks wrong

The second screenshot stopped in a `repe movsw` blit/copy routine. During that routine, `DS` is being used as a temporary source segment (`2C41`), while `SS` still holds the stable data segment (`1F0D`).

So dumping:

```text
DS:23B4
```

captured the wrong memory.

## Practical next command

When the green enemy is visible, use:

```text
MEMDUMPBIN 1F0D:23B4 F18
```

or more generally, if the debugger supports it:

```text
MEMDUMPBIN SS:23B4 F18
```

## Why this is a real breakthrough

We now know the correct segment selection rule:

```text
Do NOT trust DS when paused in arbitrary code.
Use the stable data segment (currently equal to SS).
```

This explains both:
- why the first dump worked,
- why `MEMDUMP2.BIN` turned into garbage under the object-pool parser.

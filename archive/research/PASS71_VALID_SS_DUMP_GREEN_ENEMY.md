# Pass71 - valid SS dump with green enemy

## Active objects in the new valid dump

- A01: x=84, y=217, sprite=12, behavior=0x00, state=0, class=6
- A02: x=128, y=192, sprite=104, behavior=0x8B, state=0, class=4
- A03: x=64, y=127, sprite=150, behavior=0x2D, state=4, class=4
- A05: x=112, y=107, sprite=150, behavior=0x2D, state=4, class=4
- A06: x=128, y=127, sprite=150, behavior=0x2D, state=4, class=4

## Key findings

- The new dump is valid and contains 5 active objects.
- The green enemy is confirmed as sprite 104 (within the user-reported 101..104 range).
- The green enemy uses behavior 0x8B and class/layer 4.
- The three remaining blue enemies still use behavior 0x2D and now show sprite 150.
- Their positions are screen-space pixels, not map-grid cells.

## Blue c160 formation comparison

Previous blue snapshot:
  - A14: x=64, y=54, sprite=149
  - A15: x=80, y=50, sprite=149
  - A16: x=112, y=50, sprite=149
  - A17: x=128, y=54, sprite=149
Current blue snapshot:
  - A03: x=64, y=127, sprite=150
  - A05: x=112, y=107, sprite=150
  - A06: x=128, y=127, sprite=150

Observations:
- Blue enemies have moved downward substantially (roughly +57 to +73 pixels in Y since the first snapshot).
- They are still behavior 0x2D, so the dive appears to be a movement/state phase inside the same enemy class, not a new class.
- One blue enemy is absent because the user shot it before the dump.

## Green enemy object

- +0x00 = 1
- +0x02 = 192
- +0x04 = 128
- +0x06 = 0
- +0x08 = 104
- +0x16 = 4
- +0x18 = 139
- +0x1A = 49
- +0x1C = 65535
- +0x20 = 4
- +0x22 = 9
- +0x24 = 0
- +0x26 = 1
- +0x28 = 65535
- +0x2A = 0
- +0x2C = 0
- +0x2E = 0
- +0x30 = 0
- +0x32 = 88
- +0x34 = 192
- +0x36 = 0
Interpretation:
- sprite/frame +08 = 104
- behavior/type +18 = 0x8B
- x/y = (128, 192)
- +32 = 88 and +34 = 192 may be target/aux coordinates; needs another time-adjacent dump to verify.

## Best next dumps from the same paused session

1. Unpause just a little (a few frames) and dump again with SS:23B4 to measure motion of the green enemy and blue enemies.
2. If possible, dump once when the green enemy shoots or changes animation frame.
3. Keep unique names, e.g. MEMDUMP3.BIN, MEMDUMP4.BIN.
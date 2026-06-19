# PLAQ*.ENC comparison

All six PLAQ resources have the same 4-byte apparent graphics-style header:

```text
PLAQ0.ENC: size=1224 header=87 4f 00 13 dc ff 02 0f
PLAQ1.ENC: size=1201 header=87 4f 00 13 dc ff 02 0f
PLAQ2.ENC: size=1203 header=87 4f 00 13 dc ff 02 0f
PLAQ3.ENC: size=1211 header=87 4f 00 13 dc ff 02 0f
PLAQ4.ENC: size=1211 header=87 4f 00 13 dc ff 02 0f
PLAQ5.ENC: size=1234 header=87 4f 00 13 dc ff 02 0f
```

Common-prefix comparison:

```text
PLAQ0/PLAQ1: sizes 1224/1201, identical prefix 76 bytes, shared-position equality 10.7%
PLAQ1/PLAQ2: sizes 1201/1203, identical prefix 76 bytes, shared-position equality 10.8%
PLAQ2/PLAQ3: sizes 1203/1211, identical prefix 98 bytes, shared-position equality 11.6%
PLAQ3/PLAQ4: sizes 1211/1211, identical prefix 98 bytes, shared-position equality 16.3%
PLAQ4/PLAQ5: sizes 1211/1234, identical prefix 76 bytes, shared-position equality 9.6%
```

Interpretation:

- The identical opening structure across all PLAQ resources looks like a common encoded-image prologue, not heterogeneous enemy-spawn data.
- The internal filename table places `plaq0.enc..plaq5.enc` next to `winscr.enc`, `levscr.enc`, and `choose.enc`, which strongly suggests screen/UI graphic assets.
- The exact 0x2D moving-formation descriptor found in executable data is absent from PLAQ0..PLAQ5.
- Full ENC decoding is still not solved here; this is a format-role conclusion, not a completed image parser.
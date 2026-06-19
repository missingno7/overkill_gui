# BIC trailing payload check

LEV0MAP.BIC: expected=3744, consumed_total=2108, trailing=1, trailing_bytes=80
LEV1MAP.BIC: expected=3744, consumed_total=1814, trailing=1, trailing_bytes=80
LEV2MAP.BIC: expected=3744, consumed_total=1717, trailing=1, trailing_bytes=80
LEV3MAP.BIC: expected=3744, consumed_total=1822, trailing=1, trailing_bytes=80
LEV4MAP.BIC: expected=3744, consumed_total=2179, trailing=1, trailing_bytes=80
LEV5MAP.BIC: expected=3744, consumed_total=1881, trailing=1, trailing_bytes=80
LEV1BLX.BIC: expected=27060, consumed_total=21685, trailing=1, trailing_bytes=80
2X2.BIC: expected=33000, consumed_total=25933, trailing=1, trailing_bytes=80

Conclusion: LEVxMAP resources do not appear to contain a second enemy layer after the compressed MAP payload. Most trailing bytes are just a final 0x80/no-op alignment byte.

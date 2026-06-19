#!/usr/bin/env python3
"""Inspect the statically identified moving-enemy formation descriptor block.

This is a reverse-engineering helper for the unpacked OVERKILL executable artifact.
It parses the descriptor block currently identified at raw file offset 0x135D1.

Descriptor format inferred from the spawn code around 0x4987:
    u16 field_14
    u16 field_0A
    u16 behavior
    u16 count
    count * (s16 dx, s16 dy)

The behavior 0x2D descriptor yields:
    (0,0), (16,-16), (48,-16), (64,0)
which matches the four blue runtime enemies' relative X formation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

START = 0x135D1

def parse_descriptor(data: bytes, off: int) -> tuple[dict, int] | None:
    if off + 8 > len(data):
        return None
    f14 = int.from_bytes(data[off:off+2], "little")
    f0a = int.from_bytes(data[off+2:off+4], "little")
    behavior = int.from_bytes(data[off+4:off+6], "little")
    count = int.from_bytes(data[off+6:off+8], "little")
    if count == 0 or count > 64:
        return None
    p = off + 8
    if p + count * 4 > len(data):
        return None
    offsets = []
    for _ in range(count):
        dx = int.from_bytes(data[p:p+2], "little", signed=True)
        dy = int.from_bytes(data[p+2:p+4], "little", signed=True)
        offsets.append({"dx": dx, "dy": dy})
        p += 4
    return ({
        "raw_file_offset": f"0x{off:05X}",
        "field_14": f14,
        "field_0A": f0a,
        "behavior": behavior,
        "behavior_hex": f"0x{behavior:02X}",
        "count": count,
        "offsets": offsets,
    }, p)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("unpacked_exe", type=Path)
    ap.add_argument("--start", type=lambda s: int(s, 0), default=START)
    ap.add_argument("--max", type=int, default=64)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    data = args.unpacked_exe.read_bytes()
    off = args.start
    descs = []
    for _ in range(args.max):
        parsed = parse_descriptor(data, off)
        if parsed is None:
            break
        desc, nxt = parsed
        if desc["field_14"] > 16 or desc["field_0A"] > 16 or desc["behavior"] > 0x200:
            break
        descs.append(desc)
        off = nxt

    if args.json:
        print(json.dumps(descs, indent=2))
        return

    for d in descs:
        coords = ", ".join(f"({p['dx']},{p['dy']})" for p in d["offsets"])
        print(f"{d['raw_file_offset']} behavior={d['behavior_hex']} count={d['count']} offsets={coords}")

if __name__ == "__main__":
    main()

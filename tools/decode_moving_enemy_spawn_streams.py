#!/usr/bin/env python3
"""Decode Overkill's scrolling moving-enemy spawn streams from the unpacked EXE artifact.

Known regions:
    streams:      raw 0x12D7D..0x13249
    descriptors:  raw 0x13249..0x136DD

Record format:
    trigger u16
    descriptor_ptr u16
    base_x u16
    base_y s16

or:
    trigger u16
    0xFFFF marker
    descriptor_ptr u16
    base_x u16
    base_y s16

Descriptor format:
    field_14 u16
    field_0A u16
    behavior u16
    count u16
    count * (dx s16, dy s16)
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

STREAM_STARTS = [0x12D7D, 0x12DF7, 0x12F23, 0x13157, 0x131A1, 0x131CB]
DESCRIPTOR_START = 0x13249
DESCRIPTOR_END = 0x136DD
RAW_FROM_PTR_DELTA = 0x6521

def u16(data: bytes, off: int) -> int:
    return int.from_bytes(data[off:off+2], "little")

def s16(data: bytes, off: int) -> int:
    return int.from_bytes(data[off:off+2], "little", signed=True)

def parse_descriptors(data: bytes):
    descs = []
    off = DESCRIPTOR_START
    while off < DESCRIPTOR_END:
        f14 = u16(data, off)
        f0a = u16(data, off+2)
        behavior = u16(data, off+4)
        count = u16(data, off+6)
        p = off + 8
        offsets = []
        for _ in range(count):
            offsets.append({"dx": s16(data, p), "dy": s16(data, p+2)})
            p += 4
        ptr = off - RAW_FROM_PTR_DELTA
        descs.append({
            "descriptor_ptr": ptr,
            "descriptor_ptr_hex": f"0x{ptr:04X}",
            "raw_file_offset": off,
            "raw_file_offset_hex": f"0x{off:05X}",
            "field_14": f14,
            "field_0A": f0a,
            "behavior": behavior,
            "behavior_hex": f"0x{behavior:02X}",
            "count": count,
            "offsets": offsets,
        })
        off = p
    return descs

def parse_stream(data: bytes, start: int):
    off = start
    recs = []
    while True:
        rec_start = off
        trigger = u16(data, off)
        off += 2
        if trigger == 0xFFFF:
            break
        ptr = u16(data, off)
        off += 2
        marker = False
        if ptr == 0xFFFF:
            marker = True
            ptr = u16(data, off)
            off += 2
        base_x = u16(data, off)
        base_y = s16(data, off+2)
        off += 4
        recs.append({
            "raw_record_start": rec_start,
            "raw_record_start_hex": f"0x{rec_start:05X}",
            "trigger": trigger,
            "approx_canonical_row_inferred_288_minus_trigger": 288 - trigger,
            "descriptor_ptr": ptr,
            "descriptor_ptr_hex": f"0x{ptr:04X}",
            "base_x": base_x,
            "base_y": base_y,
            "special_marker_FFFF_before_descriptor_ptr": marker,
        })
    return recs, off

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("unpacked_exe", type=Path)
    ap.add_argument("-o", "--output", type=Path)
    args = ap.parse_args()

    data = args.unpacked_exe.read_bytes()
    descs = parse_descriptors(data)
    desc_by_ptr = {d["descriptor_ptr"]: d for d in descs}
    streams = []
    for idx, start in enumerate(STREAM_STARTS):
        recs, end = parse_stream(data, start)
        for r in recs:
            d = desc_by_ptr.get(r["descriptor_ptr"])
            if d:
                r["descriptor_behavior"] = d["behavior"]
                r["descriptor_behavior_hex"] = d["behavior_hex"]
                r["descriptor_count"] = d["count"]
                r["descriptor_offsets"] = d["offsets"]
        streams.append({
            "stream_index": idx,
            "raw_stream_start": start,
            "raw_stream_start_hex": f"0x{start:05X}",
            "raw_stream_end_exclusive": end,
            "raw_stream_end_exclusive_hex": f"0x{end:05X}",
            "record_count": len(recs),
            "records": recs,
        })
    out = {"streams": streams, "formation_descriptors": descs}
    text = json.dumps(out, indent=2)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)

if __name__ == "__main__":
    main()

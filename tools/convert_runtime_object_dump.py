#!/usr/bin/env python3
"""Convert an Overkill runtime object-pool memory dump to overlay JSON.

This is meant for DOSBox/debugger memory dumps.

Best dump target:

    DS:23B4 .. DS:32CB

Length:

    0xF18 bytes

Why:
    Pool A: DS:23B4 .. DS:2B5B, 35 slots, slot size 0x38
    Pool B: DS:2B5C .. DS:32CB, 34 slots, slot size 0x38

Usage examples:

    python tools/convert_runtime_object_dump.py dump.bin --binary -o research_overlays/runtime_object_slots.json
    python tools/convert_runtime_object_dump.py dump_hex.txt -o research_overlays/runtime_object_slots.json

The output JSON can be shown in the Level Viewer with:
    Show runtime object dump
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SLOT_SIZE = 0x38
POOL_A_START = 0x23B4
POOL_A_COUNT = 0x23
POOL_B_START = 0x2B5C
POOL_B_COUNT = 0x22


def u16le(buf: bytes, off: int) -> int:
    if off + 2 > len(buf):
        return 0
    return int.from_bytes(buf[off:off + 2], "little")


def parse_hex_dump(text: str) -> bytes:
    # Accept plain "AA BB CC", DOSBox-ish lines with addresses, or mixed text.
    pairs = re.findall(r"\b[0-9A-Fa-f]{2}\b", text)
    return bytes(int(x, 16) for x in pairs)


def parse_slot(buf: bytes, pool: str, slot: int, ds_offset: int) -> dict:
    base = slot * SLOT_SIZE
    fields = {f"field_{off:02X}": u16le(buf, base + off) for off in range(0, SLOT_SIZE, 2)}
    obj = {
        "pool": pool,
        "slot": slot,
        "ds_offset": f"0x{ds_offset:04X}",
        "active": fields["field_00"],
        "y": fields["field_02"],
        "x": fields["field_04"],
        "state_or_drop_type": fields["field_06"],
        "sprite": fields["field_08"],
        "class_or_layer": fields["field_16"],
        "behavior": fields["field_18"],
        "field_1E": fields["field_1E"],
        "field_20": fields["field_20"],
        "target_y_or_aux": fields["field_32"],
        "target_x_or_aux": fields["field_34"],
        "sprite_backup_or_aux": fields["field_36"],
        **fields,
    }
    obj["label"] = f"{pool}{slot:02d} s{obj['sprite']} b{obj['behavior']:02X}"
    return obj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=Path("research_overlays/runtime_object_slots.json"))
    ap.add_argument("--binary", action="store_true", help="Input is raw binary; default parses text hex dump.")
    ap.add_argument("--level", default="LEV1")
    ap.add_argument(
        "--watch-sprites",
        default="147,148,149,150,71",
        help="Comma-separated sprite IDs to flag in output. Default: c160 enemies 147-150 and drop 71.",
    )
    args = ap.parse_args()
    watched_sprites = {int(x.strip(), 0) for x in args.watch_sprites.split(",") if x.strip()}

    raw = args.input.read_bytes() if args.binary else parse_hex_dump(args.input.read_text(errors="replace"))

    expected = POOL_A_COUNT * SLOT_SIZE + POOL_B_COUNT * SLOT_SIZE
    if len(raw) < expected:
        raise SystemExit(f"Dump too short: got {len(raw)} bytes, expected at least {expected} bytes")

    pool_a = raw[:POOL_A_COUNT * SLOT_SIZE]
    pool_b = raw[POOL_A_COUNT * SLOT_SIZE:expected]

    objects = []
    for i in range(POOL_A_COUNT):
        objects.append(parse_slot(pool_a[i*SLOT_SIZE:(i+1)*SLOT_SIZE], "A", i, POOL_A_START + i*SLOT_SIZE))
    for i in range(POOL_B_COUNT):
        objects.append(parse_slot(pool_b[i*SLOT_SIZE:(i+1)*SLOT_SIZE], "B", i, POOL_B_START + i*SLOT_SIZE))

    # Keep active objects first, but preserve all for debugging.
    for o in objects:
        o["watched_sprite"] = bool(o["sprite"] in watched_sprites)
        if o["watched_sprite"]:
            o["label"] = f"{o['pool']}{o['slot']:02d} WATCH s{o['sprite']} b{o['behavior']:02X}"

    objects.sort(key=lambda o: (0 if (o["active"] and o.get("watched_sprite")) else 1 if o["active"] else 2, o["pool"], o["slot"]))
    watched_active = [o for o in objects if o["active"] and o.get("watched_sprite")]

    out = {
        args.level.upper(): objects,
        "_watched_active": watched_active,
        "_meta": {
            "source": str(args.input),
            "dump_target": "DS:23B4..DS:32CB",
            "slot_size": SLOT_SIZE,
            "pool_A": {"start": "0x23B4", "count": POOL_A_COUNT},
            "pool_B": {"start": "0x2B5C", "count": POOL_B_COUNT},
            "watched_sprites": sorted(watched_sprites),
            "notes": "Place this file at research_overlays/runtime_object_slots.json and enable Show runtime object dump in Level Viewer.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Active objects: {sum(1 for o in objects if o['active'])}/{len(objects)}")
    print(f"Watched active objects: {len(watched_active)}")
    for o in watched_active:
        print(f"  {o['pool']}{o['slot']:02d}: x={o['x']} y={o['y']} sprite={o['sprite']} behavior=0x{o['behavior']:02X} state={o['state_or_drop_type']}")


if __name__ == "__main__":
    main()

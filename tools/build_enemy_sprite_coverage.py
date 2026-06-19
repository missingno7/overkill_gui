#!/usr/bin/env python3
"""Build a compact enemy/static-object behavior -> sprite coverage report.

This helper intentionally avoids importing the GUI/core modules, so it can run
in a minimal Python without Pillow. It only summarizes existing JSON research
data and points out behavior IDs whose sprite families still need work.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


STATIC_MAP_EVENT_DEFS = {
    "0x8B": {"raw": "0x04", "label": "static enemy 8B"},
    "0x8C": {"raw": "0x07", "label": "static enemy 8C"},
    "0x24": {"raw": "0x6C", "label": "static event 24"},
    "0x25": {"raw": "0x6D", "label": "static event 25"},
    "0x90": {"raw": "0xAC", "label": "static event 90"},
    "0x91": {"raw": "0xB1", "label": "static event 91"},
    "0x28": {"raw": "0xC9", "label": "static event 28"},
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def behavior_key(value) -> str:
    if isinstance(value, int):
        return f"0x{value:02X}"
    text = str(value).strip()
    return f"0x{int(text, 16 if text.lower().startswith('0x') else 10):02X}"


def merge_sprite_hints(project_dir: Path) -> dict:
    hints_data = load_json(project_dir / "research_overlays" / "moving_enemy_sprite_family_hints.json")
    hints = dict(hints_data.get("behaviors", {}))

    evidence = load_json(project_dir / "research_overlays" / "moving_enemy_behavior_handler_sprite_evidence.json")
    for rec in evidence.get("handler_evidence", []):
        key = behavior_key(rec.get("behavior_hex", rec.get("behavior", 0)))
        if key in hints:
            continue
        frames: list[int] = []
        for ev in rec.get("sprite_evidence", []) or []:
            candidate = ev.get("frame_family_candidate")
            if candidate:
                frames.extend(int(x) for x in candidate)
            exact = ev.get("exact_sprite")
            if exact is not None:
                frames.append(int(exact))
        frames = sorted(dict.fromkeys(frames))
        if frames:
            if len(frames) == 1:
                display = f"2X2:{frames[0]}"
            elif frames == list(range(frames[0], frames[-1] + 1)):
                display = f"2X2:{frames[0]}-{frames[-1]}"
            else:
                display = "2X2:" + ",".join(str(frame) for frame in frames)
            hints[key] = {
                "status": "static_evidence",
                "display": display,
                "sprite_frames": frames,
            }

    intro = hints_data.get("intro_minigame", {})
    for key, value in intro.items():
        hints.setdefault(behavior_key(key), value)
    return hints


def collect_behavior_sources(project_dir: Path) -> dict:
    sources: dict[str, list[str]] = {}

    streams = load_json(project_dir / "research_overlays" / "moving_enemy_spawn_streams_all_levels.json")
    for stream in streams.get("streams", []):
        stream_index = stream.get("stream_index", "?")
        for rec in stream.get("records", []):
            if "descriptor_behavior_hex" not in rec:
                continue
            key = behavior_key(rec["descriptor_behavior_hex"])
            sources.setdefault(key, []).append(f"moving stream {stream_index}")

    for key, info in STATIC_MAP_EVENT_DEFS.items():
        sources.setdefault(key, []).append(f"MAP event raw {info['raw']}")

    intro = load_json(project_dir / "research_overlays" / "intro_minigame_level1_enemy_position_table.json")
    spawned_behavior = intro.get("_meta", {}).get("spawned_behavior")
    if spawned_behavior:
        sources.setdefault(behavior_key(spawned_behavior), []).append("intro minigame table")

    return {key: sorted(dict.fromkeys(value)) for key, value in sources.items()}


def build_report(project_dir: Path) -> dict:
    hints = merge_sprite_hints(project_dir)
    sources = collect_behavior_sources(project_dir)
    behaviors = {}
    for key in sorted(sources, key=lambda x: int(x, 16)):
        hint = hints.get(key, {})
        frames = hint.get("sprite_frames") or hint.get("observed_snapshot_sprites") or []
        behaviors[key] = {
            "sources": sources[key],
            "status": hint.get("status", "unresolved"),
            "display": hint.get("display", ""),
            "sprite_frames": frames,
            "needs_sprite_research": not bool(frames),
        }
    unresolved = [key for key, value in behaviors.items() if value["needs_sprite_research"]]
    return {
        "_meta": {
            "purpose": "Coverage of behavior IDs currently used by decoded enemy/map-event placement layers.",
            "total_behaviors": len(behaviors),
            "resolved_behaviors": len(behaviors) - len(unresolved),
            "unresolved_behaviors": len(unresolved),
            "unresolved_behavior_ids": unresolved,
        },
        "behaviors": behaviors,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path("."))
    parser.add_argument("-o", "--output", type=Path, default=Path("research_overlays/enemy_sprite_coverage.json"))
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    report = build_report(project_dir)
    output = args.output if args.output.is_absolute() else project_dir / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"wrote {output}")
    print(json.dumps(report["_meta"], indent=2))


if __name__ == "__main__":
    main()

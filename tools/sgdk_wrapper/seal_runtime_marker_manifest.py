#!/usr/bin/env python3
"""Create a derived manifest after a BlastEm terminal SRAM flush."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct
import time


def read_hanc(path: Path) -> dict | None:
    for _ in range(20):
        try:
            raw = path.read_bytes(); offset = raw.find(b"HANC")
            if offset >= 0 and len(raw) >= offset + 24:
                schema, size = struct.unpack_from(">HH", raw, offset + 4)
                if schema == 1 and size == 24:
                    words = struct.unpack_from(">8H", raw, offset + 8)
                    return {"schema": schema, "bytes": size, "marker_id": words[0],
                            "runtime_presentation_frame": (words[1] << 16) | words[2],
                            "marker_period_frames": words[3], "visible_hold_frames": words[4],
                            "psg_channel": words[5], "psg_frequency_hz": words[6],
                            "scene": words[7], "source": "save.sram:HANC"}
        except (OSError, ValueError, struct.error):
            pass
        time.sleep(0.25)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    bundle = Path(args.bundle).resolve()
    source = bundle / "manifest.json"
    manifest = json.loads(source.read_text(encoding="utf-8"))
    marker = read_hanc(bundle / "userdata/blastem/rom/save.sram")
    if marker is None:
        print(json.dumps({"status": "needs_review", "reason": "HANC_missing_after_flush"}))
        return 1
    manifest["runtime_media_marker"] = marker
    manifest["runtime_media_marker_manifest"] = {
        "status": "derived_from_terminal_sram_flush", "source_manifest": source.name,
        "claim_limit": "runtime marker context only; no video PTS/audio sample approval",
    }
    Path(args.out).resolve().write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "marker_id": marker["marker_id"], "out": args.out}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

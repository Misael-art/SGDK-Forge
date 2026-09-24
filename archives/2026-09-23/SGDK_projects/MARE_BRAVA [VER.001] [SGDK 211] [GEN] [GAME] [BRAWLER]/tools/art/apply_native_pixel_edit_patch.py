#!/usr/bin/env python3
"""Literal executor for hand-authored native pixel edit patches.

This program performs no shape, palette, threshold or semantic decisions. It
only verifies old indices and writes the declared new indices.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_patch(patch: dict) -> bytes:
    clean = dict(patch)
    clean["patch_sha256"] = None
    clean["result_png_sha256"] = None
    return json.dumps(clean, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patch", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    patch = json.loads(args.patch.read_text(encoding="utf-8"))
    source_sha = digest(args.source)
    if source_sha != patch["source_candidate_sha256"]:
        raise SystemExit(f"source SHA mismatch: {source_sha} != {patch['source_candidate_sha256']}")
    if patch["target_scale"] != "48x64":
        raise SystemExit("target scale must remain 48x64")
    image = Image.open(args.source).convert("P")
    if image.size != (48, 64):
        raise SystemExit(f"source dimensions are not 48x64: {image.size}")
    allowed = set(patch["palette_indices_allowed"])
    seen: set[tuple[int, int]] = set()
    operations = []
    for group in patch["groups"]:
        for operation in group["operations"]:
            x, y = operation["x"], operation["y"]
            if (x, y) in seen:
                raise SystemExit(f"duplicate operation coordinate: {(x, y)}")
            seen.add((x, y))
            old = image.getpixel((x, y))
            if old != operation["old_index"]:
                raise SystemExit(f"old index mismatch at {(x, y)}: {old} != {operation['old_index']}")
            if operation["new_index"] not in allowed:
                raise SystemExit(f"new index not allowed at {(x, y)}")
            image.putpixel((x, y), operation["new_index"])
            operations.append({"x": x, "y": y, "old_index": old, "new_index": operation["new_index"],
                               "region": group["region"], "group_id": group["id"]})
    image.info["transparency"] = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, "PNG", bits=4, transparency=0)
    result_sha = digest(args.output)
    report = {"schema_version": "1.0.0", "status": "passed", "patch_path": str(args.patch),
              "patch_sha256": hashlib.sha256(canonical_patch(patch)).hexdigest(),
              "source_candidate_sha256": source_sha, "target_asset_id": patch["target_asset_id"],
              "result_png_sha256": result_sha, "operations_applied": len(operations),
              "operations": operations, "executor_policy": "literal_old_index_to_new_index_only",
              "decision_logic_used": False}
    report_path = args.output.with_name("native_pixel_edit_application_report.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "target_asset_id": patch["target_asset_id"],
                      "patch_sha256": report["patch_sha256"], "result_png_sha256": result_sha,
                      "operations_applied": len(operations)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Hash protected Kirby trees without relying on Git tracking state."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_REL = "SGDK_projects/KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]"
PROTECTED = {
    "v04": "out/forward_test_v04_native_temporal",
    "v05": "out/forward_test_v05_visual_bitmap_temporal",
    "v06": "out/forward_test_v06_corrected_native_temporal",
    "v07": "out/forward_test_v07_review_blocked_native_temporal",
    "v08": "out/forward_test_v08_isolated_technical_temporal",
    "v09": "out/forward_test_v09_isolated_critical_audit",
    "res": "res",
    "runtime": "src",
    "rom": "out/rom.bin",
}


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_target(project: Path, relative: str) -> dict[str, object]:
    target = project / relative
    if target.is_file():
        return {"path": relative, "kind": "file", "exists": True, "sha256": file_sha(target), "files": [{"path": relative, "sha256": file_sha(target)}]}
    if not target.is_dir():
        return {"path": relative, "kind": "missing", "exists": False, "sha256": None, "files": []}
    files = []
    for path in sorted(item for item in target.rglob("*") if item.is_file()):
        files.append({"path": path.relative_to(project).as_posix(), "sha256": file_sha(path)})
    canonical = "\n".join(f"{item['path']}\0{item['sha256']}" for item in files).encode("utf-8")
    return {"path": relative, "kind": "directory", "exists": True, "sha256": hashlib.sha256(canonical).hexdigest(), "files": files}


def build(project: Path) -> dict[str, object]:
    entries = {name: hash_target(project, relative) for name, relative in PROTECTED.items()}
    return {
        "schema_version": "1.0.0",
        "project": PROJECT_REL,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "algorithm": "sha256(sorted_project_relative_path_nul_file_sha256)",
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = build(args.project_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({name: entry["sha256"] for name, entry in value["entries"].items()}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

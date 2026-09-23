#!/usr/bin/env python3
"""Build a deterministic context_pack_manifest for SGDK art/code work."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def find_workspace_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        marker = candidate / "tools" / "sgdk_wrapper" / ".agent" / "framework_manifest.json"
        if marker.exists():
            return candidate
    raise SystemExit("Could not locate MegaDrive_DEV workspace root.")


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_entry(root: Path, role: str, path: Path) -> dict:
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = str(path)

    exists = path.is_file()
    stat = path.stat() if exists else None
    return {
        "role": role,
        "path": rel,
        "exists": exists,
        "size_bytes": stat.st_size if stat else None,
        "mtime_utc": (
            datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z")
            if stat
            else None
        ),
        "sha256": sha256(path) if exists else None,
    }


def unique_paths(paths: Iterable[tuple[str, Path]]) -> list[tuple[str, Path]]:
    seen: set[Path] = set()
    result: list[tuple[str, Path]] = []
    for role, path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append((role, path))
    return result


def build_manifest(project_root: Path, workspace_root: Path, include_headers: bool) -> dict:
    project_root = project_root.resolve()
    workspace_root = workspace_root.resolve()

    source_paths: list[tuple[str, Path]] = [
        ("project_memory", project_root / "doc" / "10-memory-bank.md"),
        ("gdd", project_root / "doc" / "11-gdd.md"),
        ("scene_spec", project_root / "doc" / "13-spec-cenas.md"),
        ("agent_guidelines", project_root / "doc" / "00-diretrizes-agente.md"),
        ("script", project_root / "doc" / "12-roteiro.md"),
        ("architecture", project_root / "doc" / "03-arquitetura.md"),
        ("project_manifest", project_root / ".mddev" / "project.json"),
        ("global_memory", workspace_root / "doc" / "06_AI_MEMORY_BANK.md"),
        ("visual_feedback_bank", workspace_root / "doc" / "03_art" / "02_visual_feedback_bank.md"),
        ("visual_quality_bar", workspace_root / "doc" / "03_art" / "00_visual_quality_bar.md"),
        ("visual_cohesion_system", workspace_root / "doc" / "03_art" / "01_visual_cohesion_system.md"),
        ("engine_pattern_registry", workspace_root / "doc" / "05_technical" / "92_sgdk_engine_pattern_registry.json"),
        ("engine_scan_appendix", workspace_root / "doc" / "05_technical" / "99_sgdk_engines_scan_appendix.md"),
        ("framework_manifest", workspace_root / "tools" / "sgdk_wrapper" / ".agent" / "framework_manifest.json"),
    ]

    for manifest in sorted((project_root / "doc" / "source_cases").glob("**/case_manifest.json")):
        source_paths.append(("source_case_manifest", manifest))

    if include_headers:
        inc = workspace_root / "sdk" / "sgdk-2.11" / "inc"
        for header in [
            "types.h",
            "vdp.h",
            "vdp_tile.h",
            "vdp_pal.h",
            "sprite_eng.h",
            "sys.h",
            "dma.h",
            "resources.h",
            "maths.h",
        ]:
            source_paths.append(("sgdk_header", inc / header))

    sources = [file_entry(workspace_root, role, path) for role, path in unique_paths(source_paths)]
    project_memory_found = (project_root / "doc" / "10-memory-bank.md").is_file()
    fallback_global_memory = not project_memory_found and (workspace_root / "doc" / "06_AI_MEMORY_BANK.md").is_file()

    notes: list[str] = []
    if fallback_global_memory:
        notes.append("project doc/10-memory-bank.md missing; using workspace doc/06_AI_MEMORY_BANK.md as fallback memory")

    return {
        "schema": "context_pack_manifest.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "workspace_root": str(workspace_root),
        "project_root": str(project_root),
        "memory_policy": {
            "project_memory_found": project_memory_found,
            "fallback_global_memory": fallback_global_memory,
        },
        "sources": sources,
        "notes": notes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".", help="Project root to inspect.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--no-sgdk-headers", action="store_true", help="Skip SGDK header entries.")
    args = parser.parse_args()

    script_root = Path(__file__).resolve()
    workspace_root = find_workspace_root(script_root)
    project_root = Path(args.project)
    if not project_root.is_absolute():
        project_root = (Path.cwd() / project_root).resolve()

    manifest = build_manifest(project_root, workspace_root, include_headers=not args.no_sgdk_headers)
    payload = json.dumps(manifest, indent=2, ensure_ascii=False)

    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = (Path.cwd() / output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Minimal documentation drift audit for MegaDrive_DEV SGDK projects."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_manifest(project_root: Path) -> dict:
    manifest_path = project_root / ".mddev" / "project.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] Manifesto invalido em '{manifest_path}': {exc}") from exc


def main() -> int:
    project_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    manifest = load_manifest(project_root)

    issues: list[str] = []

    if not (project_root / ".agent" / "ARCHITECTURE.md").exists():
        issues.append("Projeto sem `.agent` bootstrapada.")

    if not (project_root / "README.md").exists():
        issues.append("README.md ausente.")

    if not (project_root / ".mddev" / "project.json").exists():
        issues.append("Manifesto `.mddev/project.json` ausente.")

    if manifest and not manifest.get("layout"):
        issues.append("Manifesto sem campo `layout`.")

    if (project_root / "src").exists() and not (project_root / "doc").exists():
        issues.append("Projeto com codigo, mas sem pasta `doc/`.")

    report = {
        "project_root": str(project_root),
        "display_name": manifest.get("display_name", project_root.name),
        "issue_count": len(issues),
        "issues": issues,
    }

    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Project status inspector for MegaDrive_DEV SGDK projects."""

from __future__ import annotations

import json
import sys
from pathlib import Path


STATUS_FIELDS = [
    "documentado",
    "implementado",
    "buildado",
    "testado_em_emulador",
    "validado_budget",
    "placeholder",
    "parcial",
    "futuro_arquitetural",
    "agent_bootstrapped",
]


def load_manifest(project_root: Path) -> dict:
    manifest_path = project_root / ".mddev" / "project.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] Manifesto invalido em '{manifest_path}': {exc}") from exc


def has_any(*paths: Path) -> bool:
    return any(path.exists() for path in paths)


def main() -> int:
    project_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    manifest = load_manifest(project_root)

    doc_dir = project_root / "doc"
    docs_dir = project_root / "docs"
    out_dir = project_root / "out"
    rom_path = out_dir / "rom.bin"
    agent_dir = project_root / ".agent"

    status = {
        "project_root": str(project_root),
        "display_name": manifest.get("display_name", project_root.name),
        "layout": manifest.get("layout", "unknown"),
        "build_policy": manifest.get("build_policy", "enabled"),
        "documentado": has_any(project_root / "README.md", doc_dir / "README.md", docs_dir / "README.md"),
        "implementado": has_any(project_root / "src", project_root / "inc", project_root / "res"),
        "buildado": rom_path.exists(),
        "testado_em_emulador": False,
        "validado_budget": False,
        "placeholder": False,
        "parcial": False,
        "futuro_arquitetural": False,
        "agent_bootstrapped": (agent_dir / "ARCHITECTURE.md").exists(),
    }

    missing_fields = [field for field in STATUS_FIELDS if field not in status]
    if missing_fields:
        raise SystemExit(f"[ERROR] Campos de status ausentes: {', '.join(missing_fields)}")

    print(json.dumps(status, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

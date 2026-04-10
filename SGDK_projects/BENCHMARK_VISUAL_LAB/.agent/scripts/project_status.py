#!/usr/bin/env python3
"""Project status inspector for MegaDrive_DEV SGDK projects."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


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


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] JSON invalido em '{path}': {exc}") from exc


def resolve_workspace_root(project_root: Path) -> Path | None:
    for candidate in [project_root, *project_root.parents]:
        if (candidate / "tools" / "sgdk_wrapper" / ".agent" / "framework_manifest.json").exists():
            return candidate
    return None


def resolve_canonical_agent_dir(project_root: Path) -> Path | None:
    workspace_root = resolve_workspace_root(project_root)
    if workspace_root is None:
        return None
    return workspace_root / "tools" / "sgdk_wrapper" / ".agent"


def resolve_memory_artifact(project_root: Path, canonical_manifest: dict[str, Any]) -> Path | None:
    candidates = [project_root / "doc" / "10-memory-bank.md"]
    workspace_root = resolve_workspace_root(project_root)
    for relative_path in canonical_manifest.get("canonical_memory_artifacts", []):
        if workspace_root is None:
            continue
        candidate = workspace_root / relative_path
        if candidate not in candidates:
            candidates.append(candidate)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def has_local_agent_bootstrap(agent_dir: Path) -> bool:
    return (agent_dir / "ARCHITECTURE.md").exists() and (agent_dir / "framework_manifest.json").exists()


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect_tree_hashes(base_dir: Path, relative_entries: list[str]) -> dict[str, str]:
    hashed: dict[str, str] = {}
    for entry in relative_entries:
        root = base_dir / entry
        if not root.exists():
            continue
        if root.is_file():
            if root.suffix == ".pyc" or "__pycache__" in root.parts:
                continue
            hashed[entry.replace("\\", "/")] = hash_file(root)
            continue
        for child in sorted(
            p for p in root.rglob("*") if p.is_file() and p.suffix != ".pyc" and "__pycache__" not in p.parts
        ):
            hashed[str(child.relative_to(base_dir)).replace("\\", "/")] = hash_file(child)
    return hashed


def compare_agent_versions(project_root: Path, local_agent_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    canonical_agent_dir = resolve_canonical_agent_dir(project_root)
    if canonical_agent_dir is None:
        return {}, {}, {"available": False}

    canonical_manifest = load_json(canonical_agent_dir / "framework_manifest.json")
    local_manifest = load_json(local_agent_dir / "framework_manifest.json")
    tracked_paths = canonical_manifest.get("tracked_paths", [])
    canonical_hashes = collect_tree_hashes(canonical_agent_dir, tracked_paths)
    local_hashes = collect_tree_hashes(local_agent_dir, tracked_paths) if local_agent_dir.exists() else {}
    differing_paths = sorted(
        path for path in set(canonical_hashes) | set(local_hashes) if canonical_hashes.get(path) != local_hashes.get(path)
    )
    return canonical_manifest, local_manifest, {
        "available": True,
        "canonical_version": canonical_manifest.get("framework_version"),
        "local_version": local_manifest.get("framework_version"),
        "version_match": canonical_manifest.get("framework_version") == local_manifest.get("framework_version"),
        "drift_count": len(differing_paths),
        "drift_paths": differing_paths[:25],
    }


def normalize_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "ok", "validado"}
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def main() -> int:
    project_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    manifest = load_manifest(project_root)

    doc_dir = project_root / "doc"
    docs_dir = project_root / "docs"
    out_dir = project_root / "out"
    rom_path = out_dir / "rom.bin"
    agent_dir = project_root / ".agent"
    logs_dir = out_dir / "logs"
    validation_report_path = logs_dir / "validation_report.json"
    runtime_metrics_path = logs_dir / "runtime_metrics.json"
    emulator_session_path = logs_dir / "emulator_session.json"

    validation_report = load_json(validation_report_path)
    runtime_metrics = load_json(runtime_metrics_path)
    emulator_session = load_json(emulator_session_path)
    status_from_report = validation_report.get("status_panel", {})
    qa_axes = validation_report.get("qa_axes", {})
    runtime_profile = validation_report.get("runtime_profile", {})

    canonical_manifest, local_manifest, agent_audit = compare_agent_versions(project_root, agent_dir)
    memory_artifact = resolve_memory_artifact(project_root, canonical_manifest)

    runtime_samples = int(runtime_metrics.get("samples_recorded", 0) or 0)
    runtime_capture_present = runtime_samples > 0
    emulator_name = (
        emulator_session.get("emulator")
        or emulator_session.get("reference_emulator")
        or validation_report.get("evidence", {}).get("emulator_reference")
        or ""
    )
    blastem_gate = normalize_bool(status_from_report.get("blastem_gate")) or (
        "blastem" in emulator_name.lower() and emulator_session.get("boot_emulador") == "ok"
    )

    status = {
        "project_root": str(project_root),
        "display_name": manifest.get("display_name", project_root.name),
        "layout": manifest.get("layout", "unknown"),
        "build_policy": manifest.get("build_policy", "enabled"),
        "documentado": status_from_report.get(
            "documentado",
            has_any(project_root / "README.md", doc_dir / "README.md", docs_dir / "README.md"),
        ),
        "implementado": status_from_report.get(
            "implementado",
            has_any(project_root / "src", project_root / "inc", project_root / "res"),
        ),
        "buildado": status_from_report.get("buildado", rom_path.exists()),
        "testado_em_emulador": status_from_report.get(
            "testado_em_emulador",
            runtime_capture_present or emulator_session.get("boot_emulador") == "ok",
        ),
        "validado_budget": status_from_report.get(
            "validado_budget",
            runtime_capture_present and runtime_profile.get("frame_stability") == "estavel",
        ),
        "placeholder": status_from_report.get("placeholder", manifest.get("placeholder", False)),
        "parcial": status_from_report.get("parcial", manifest.get("partial", False)),
        "futuro_arquitetural": status_from_report.get(
            "futuro_arquitetural",
            manifest.get("future_architectural", False),
        ),
        "agent_bootstrapped": has_local_agent_bootstrap(agent_dir),
        "runtime_profile": runtime_profile,
        "qa_axes": qa_axes,
        "evidence": {
            "validation_report": str(validation_report_path) if validation_report_path.exists() else None,
            "runtime_metrics": str(runtime_metrics_path) if runtime_metrics_path.exists() else None,
            "emulator_session": str(emulator_session_path) if emulator_session_path.exists() else None,
            "memory_artifact": str(memory_artifact) if memory_artifact else None,
            "runtime_samples_recorded": runtime_samples,
            "blastem_gate": blastem_gate,
        },
        "agent_framework": {
            "local_version": local_manifest.get("framework_version"),
            "canonical_version": canonical_manifest.get("framework_version"),
            "version_match": agent_audit.get("version_match"),
            "drift_count": agent_audit.get("drift_count", 0),
            "drift_paths": agent_audit.get("drift_paths", []),
        },
    }

    missing_fields = [field for field in STATUS_FIELDS if field not in status]
    if missing_fields:
        raise SystemExit(f"[ERROR] Campos de status ausentes: {', '.join(missing_fields)}")

    print(json.dumps(status, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

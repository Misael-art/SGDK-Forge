#!/usr/bin/env python3
"""Documentation, evidence and framework drift audit for MegaDrive_DEV SGDK projects."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def load_manifest(project_root: Path) -> dict:
    manifest_path = project_root / ".mddev" / "project.json"
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] Manifesto invalido em '{manifest_path}': {exc}") from exc


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


def get_agent_audit(project_root: Path) -> dict[str, Any]:
    workspace_root = resolve_workspace_root(project_root)
    local_agent_dir = project_root / ".agent"
    if workspace_root is None:
        return {"available": False, "issues": ["Nao foi possivel localizar a .agent canonica do workspace."]}

    canonical_agent_dir = workspace_root / "tools" / "sgdk_wrapper" / ".agent"
    canonical_manifest = load_json(canonical_agent_dir / "framework_manifest.json")
    local_manifest = load_json(local_agent_dir / "framework_manifest.json")
    tracked_paths = canonical_manifest.get("tracked_paths", [])
    canonical_hashes = collect_tree_hashes(canonical_agent_dir, tracked_paths)
    local_hashes = collect_tree_hashes(local_agent_dir, tracked_paths) if local_agent_dir.exists() else {}
    differing_paths = sorted(
        path for path in set(canonical_hashes) | set(local_hashes) if canonical_hashes.get(path) != local_hashes.get(path)
    )
    issues: list[str] = []
    if not local_agent_dir.exists():
        issues.append("Projeto sem `.agent` bootstrapada.")
    if not local_manifest:
        issues.append("`.agent` local sem `framework_manifest.json` valido.")
    if canonical_manifest.get("framework_version") != local_manifest.get("framework_version"):
        issues.append(
            "Versao da `.agent` local diverge da canonica "
            f"({local_manifest.get('framework_version')} != {canonical_manifest.get('framework_version')})."
        )
    if differing_paths:
        issues.append(f"`.agent` local diverge da canonica em {len(differing_paths)} arquivo(s) rastreados.")
    return {
        "available": True,
        "canonical_version": canonical_manifest.get("framework_version"),
        "local_version": local_manifest.get("framework_version"),
        "tracked_paths": tracked_paths,
        "drift_count": len(differing_paths),
        "drift_paths": differing_paths[:50],
        "issues": issues,
        "memory_artifacts": canonical_manifest.get("canonical_memory_artifacts", []),
    }


def resolve_memory_artifact(project_root: Path, workspace_root: Path | None, memory_artifacts: list[str]) -> Path | None:
    candidates = [project_root / "doc" / "10-memory-bank.md"]
    if workspace_root is not None:
        for relative_path in memory_artifacts:
            candidate = workspace_root / relative_path
            if candidate not in candidates:
                candidates.append(candidate)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    project_root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    manifest = load_manifest(project_root)
    workspace_root = resolve_workspace_root(project_root)
    logs_dir = project_root / "out" / "logs"
    validation_report_path = logs_dir / "validation_report.json"
    runtime_metrics_path = logs_dir / "runtime_metrics.json"
    emulator_session_path = logs_dir / "emulator_session.json"
    validation_report = load_json(validation_report_path)
    runtime_metrics = load_json(runtime_metrics_path)
    emulator_session = load_json(emulator_session_path)
    agent_audit = get_agent_audit(project_root)
    memory_artifact = resolve_memory_artifact(
        project_root,
        workspace_root,
        list(agent_audit.get("memory_artifacts", [])),
    )

    issues: list[str] = []
    warnings: list[str] = []
    required_docs = [
        project_root / "README.md",
        project_root / ".mddev" / "project.json",
        project_root / "doc",
        project_root / "doc" / "11-gdd.md",
        project_root / "doc" / "13-spec-cenas.md",
    ]
    for doc_path in required_docs:
        if not doc_path.exists():
            issues.append(f"Artefato obrigatorio ausente: {doc_path.relative_to(project_root)}")

    if memory_artifact is None:
        issues.append("Nenhum artefato canônico de memória operacional foi encontrado.")

    if manifest and not manifest.get("layout"):
        issues.append("Manifesto sem campo `layout`.")

    if (project_root / "src").exists() and not (project_root / "doc").exists():
        issues.append("Projeto com codigo, mas sem pasta `doc/`.")

    if not validation_report_path.exists():
        warnings.append("validation_report.json ausente; painel de status perde a fonte primaria.")
    else:
        status_panel = validation_report.get("status_panel", {})
        if not status_panel:
            issues.append("validation_report.json existe, mas nao contem `status_panel` estruturado.")

    runtime_samples = int(runtime_metrics.get("samples_recorded", 0) or 0)
    if runtime_metrics_path.exists() and runtime_samples <= 0:
        warnings.append("runtime_metrics.json existe, mas nao contem amostras validas.")

    if validation_report.get("status_panel", {}).get("testado_em_emulador") and not (
        runtime_samples > 0 or emulator_session.get("boot_emulador") == "ok"
    ):
        issues.append("Status declara `testado_em_emulador`, mas faltam evidencias estruturadas de emulador.")

    if validation_report.get("status_panel", {}).get("validado_budget") and runtime_samples <= 0:
        warnings.append("Status declara `validado_budget` sem runtime capture valido; confirme auditoria equivalente.")

    issues.extend(agent_audit.get("issues", []))

    report = {
        "project_root": str(project_root),
        "display_name": manifest.get("display_name", project_root.name),
        "workspace_root": str(workspace_root) if workspace_root else None,
        "issue_count": len(issues),
        "warning_count": len(warnings),
        "issues": issues,
        "warnings": warnings,
        "required_evidence": {
            "validation_report": str(validation_report_path),
            "runtime_metrics": str(runtime_metrics_path),
            "emulator_session": str(emulator_session_path),
            "memory_artifact": str(memory_artifact) if memory_artifact else None,
        },
        "agent_audit": agent_audit,
    }

    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())

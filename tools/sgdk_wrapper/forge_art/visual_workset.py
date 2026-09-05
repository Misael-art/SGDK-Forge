"""Validate the active visual source set and enforce project freezes.

The manifest is deliberately small: it answers which files may own new pixels,
which files are comparison-only, and whether visual production is frozen.  It
does not replace provenance, pixel, aesthetic, budget or human gates.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from forge_art import schema_gate

MANIFEST_RELATIVE_PATH = Path("doc/art/visual_workset_manifest.json")
READ_ONLY_OPERATIONS = {
    "read_only_audit",
    "pixel_validate",
    "route_verify",
    "case_study_review",
}


class VisualWorksetError(ValueError):
    def __init__(self, blocker: str, message: str) -> None:
        super().__init__(f"[{blocker}] {message}")
        self.blocker = blocker


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _portable_file(root: Path, value: str, blocker: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise VisualWorksetError(blocker, f"caminho nao-portavel: {value}")
    resolved = (root / relative).resolve()
    if root not in resolved.parents or not resolved.is_file():
        raise VisualWorksetError(blocker, f"arquivo ausente ou fora do projeto: {value}")
    return resolved


def _under_root(value: str, prefix: str) -> bool:
    path = Path(value)
    root = Path(prefix)
    return path == root or root in path.parents


def validate_project_workset(project_root: Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    manifest_path = root / MANIFEST_RELATIVE_PATH
    if not manifest_path.is_file():
        return {
            "schema_version": "1.0.0",
            "status": "not_present",
            "manifest_path": MANIFEST_RELATIVE_PATH.as_posix(),
            "blocking": False,
            "note": "projetos legados continuam auditaveis; producao visual critica deve criar o workset antes de novos pixels",
        }
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema_gate.validate_named(manifest, "visual_workset_manifest")
    except (OSError, json.JSONDecodeError, schema_gate.SchemaError) as exc:
        raise VisualWorksetError("visual_workset_manifest_invalid", str(exc)) from exc

    production_sources = manifest["production_sources"]
    reference_sources = manifest["reference_only_sources"]
    forbidden_roots = manifest["forbidden_source_roots"]
    allowed_operations = manifest["allowed_operations"]

    if len(allowed_operations) != len(set(allowed_operations)):
        raise VisualWorksetError("visual_workset_duplicate_operation", "allowed_operations possui duplicatas")

    seen_ids: set[str] = set()
    measured_sources: list[dict[str, Any]] = []
    for entry in [*production_sources, *reference_sources]:
        asset_id = entry["asset_id"]
        if asset_id in seen_ids:
            raise VisualWorksetError("visual_workset_duplicate_asset_id", asset_id)
        seen_ids.add(asset_id)
        path = _portable_file(root, entry["path"], "visual_workset_source_invalid")
        actual_hash = _sha256(path)
        if actual_hash != entry["sha256"]:
            raise VisualWorksetError(
                "visual_workset_source_hash_mismatch",
                f"{entry['path']}: esperado {entry['sha256']}, obtido {actual_hash}",
            )
        if entry in production_sources and any(
            _under_root(entry["path"], prefix) for prefix in forbidden_roots
        ):
            raise VisualWorksetError(
                "forbidden_source_promoted_to_workset",
                f"{entry['path']} pertence a raiz proibida",
            )
        measured_sources.append({
            "asset_id": asset_id,
            "path": entry["path"],
            "role": entry["role"],
            "status": entry["status"],
            "sha256": actual_hash,
        })

    if manifest["state"] == "frozen_case_study":
        if production_sources:
            raise VisualWorksetError(
                "frozen_workset_has_production_source",
                "estudo congelado nao pode manter production_sources",
            )
        if set(allowed_operations) - READ_ONLY_OPERATIONS:
            raise VisualWorksetError(
                "frozen_workset_allows_production",
                "estudo congelado permite operacao de producao",
            )
        freeze = manifest.get("freeze_record")
        if not isinstance(freeze, dict):
            raise VisualWorksetError("freeze_record_missing", "freeze_record obrigatorio")
        _portable_file(root, freeze["case_study_path"], "case_study_missing")

    return {
        "schema_version": "1.0.0",
        "status": "passed",
        "state": manifest["state"],
        "active_epoch": manifest["active_epoch"],
        "manifest_path": MANIFEST_RELATIVE_PATH.as_posix(),
        "manifest_sha256": _sha256(manifest_path),
        "production_source_count": len(production_sources),
        "reference_source_count": len(reference_sources),
        "allowed_operations": allowed_operations,
        "measured_sources": measured_sources,
        "blocking": False,
    }


def enforce_operation(project_root: Path, operation: str) -> dict[str, Any]:
    report = validate_project_workset(project_root)
    if report["status"] == "not_present":
        return report
    if operation not in report["allowed_operations"]:
        blocker = (
            "visual_production_frozen"
            if report["state"] == "frozen_case_study"
            else "visual_operation_not_authorized"
        )
        raise VisualWorksetError(blocker, f"operacao {operation} nao autorizada pelo workset")
    return report


def _normalized_relative_source(project_root: Path, source: str | Path) -> str:
    root = Path(project_root).resolve()
    raw = Path(source)
    resolved = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
    if root not in resolved.parents or not resolved.is_file():
        raise VisualWorksetError(
            "visual_workset_source_invalid",
            f"fonte ausente ou fora do projeto: {source}",
        )
    return resolved.relative_to(root).as_posix()


def enforce_declared_source(
    project_root: Path,
    source: str | Path,
    *,
    require_production_eligible: bool,
) -> dict[str, Any]:
    """Reject directory-discovered sources when a project owns a workset.

    Legacy projects without a workset remain compatible. Once a workset exists,
    every consumed source must be hash-bound in it; pixel-derived operations
    additionally require an entry from ``production_sources``.
    """
    report = validate_project_workset(project_root)
    if report["status"] == "not_present":
        return report
    relative = _normalized_relative_source(project_root, source)
    matches = [item for item in report["measured_sources"] if item["path"] == relative]
    if not matches:
        raise VisualWorksetError(
            "source_not_in_active_visual_workset",
            f"{relative} nao esta declarado no workset ativo",
        )
    selected = matches[0]
    if require_production_eligible and selected["status"] != "eligible":
        raise VisualWorksetError(
            "reference_only_used_as_pixel_source",
            f"{relative} e somente referencia e nao pode fornecer pixels",
        )
    return {**report, "selected_source": selected}


def self_check() -> dict[str, Any]:
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="forge-art-workset-") as temp:
        root = Path(temp)
        (root / "doc/art").mkdir(parents=True)
        (root / "data/source_art").mkdir(parents=True)
        source = root / "data/source_art/source.png"
        source.write_bytes(b"source")
        case_study = root / "doc/art/case_study.md"
        case_study.write_text("case\n", encoding="utf-8")
        base = {
            "schema_version": "1.0.0",
            "project_id": "fixture",
            "active_epoch": "fixture_v01",
            "state": "active_production",
            "production_sources": [{
                "asset_id": "source",
                "path": "data/source_art/source.png",
                "sha256": _sha256(source),
                "role": "identity_authority",
                "status": "eligible"
            }],
            "reference_only_sources": [],
            "forbidden_source_roots": ["out", "data/archive", "data/staging"],
            "forbidden_source_roles": ["negative_evidence", "procedural_code_probe"],
            "allowed_operations": ["native_authoring"]
        }
        manifest_path = root / MANIFEST_RELATIVE_PATH
        manifest_path.write_text(json.dumps(base), encoding="utf-8")
        checks["active_source_hash_bound"] = validate_project_workset(root)["status"] == "passed"
        checks["active_source_is_production_eligible"] = (
            enforce_declared_source(root, source, require_production_eligible=True)["selected_source"]["status"]
            == "eligible"
        )

        frozen = dict(base)
        frozen.update({
            "active_epoch": "fixture_frozen_v01",
            "state": "frozen_case_study",
            "production_sources": [],
            "reference_only_sources": [{
                "asset_id": "source_reference",
                "path": "data/source_art/source.png",
                "sha256": _sha256(source),
                "role": "quality_reference_only",
                "status": "reference_only"
            }],
            "allowed_operations": ["read_only_audit", "case_study_review"],
            "freeze_record": {
                "decision": "freeze_visual_production_as_case_study",
                "frozen_at": "2026-09-04T00:00:00Z",
                "reason": "fixture",
                "case_study_path": "doc/art/case_study.md",
                "reactivation_requires": ["explicit human unfreeze"]
            }
        })
        manifest_path.write_text(json.dumps(frozen), encoding="utf-8")
        checks["frozen_read_only_passes"] = enforce_operation(root, "read_only_audit")["state"] == "frozen_case_study"
        try:
            enforce_declared_source(root, source, require_production_eligible=True)
        except VisualWorksetError as exc:
            checks["reference_cannot_supply_pixels"] = exc.blocker == "reference_only_used_as_pixel_source"
        else:
            checks["reference_cannot_supply_pixels"] = False
        try:
            enforce_operation(root, "native_authoring")
        except VisualWorksetError as exc:
            checks["frozen_production_rejected"] = exc.blocker == "visual_production_frozen"
        else:
            checks["frozen_production_rejected"] = False

        source.write_bytes(b"tampered")
        try:
            validate_project_workset(root)
        except VisualWorksetError as exc:
            checks["tampered_source_rejected"] = exc.blocker == "visual_workset_source_hash_mismatch"
        else:
            checks["tampered_source_rejected"] = False

    failed = [name for name, passed in checks.items() if not passed]
    return {
        "fixtures_passed": len(checks) - len(failed),
        "fixtures_total": len(checks),
        "blocking": bool(failed),
        "fixtures": checks,
    }

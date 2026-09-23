#!/usr/bin/env python3
"""Validate the 16-bit hardware mastery registry human proficiency layer."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REQUIRED_ENTRY_FIELDS = {
    "id",
    "title",
    "module",
    "current_status",
    "operational_policy",
    "owner_skills",
    "human_proficiency_status",
    "technique_tags",
    "promotion_evidence",
}

ALLOWED_HUMAN_STATUS = {
    "LABORATORIO",
    "TEORICA_STANDARD",
    "TEORICA_PRIORITARIA",
    "MESTRE_STANDARD",
    "MESTRE_PRIORITARIA",
}

MASTER_EVIDENCE_FIELDS = {
    "approved_project_path",
    "rom_sha256",
    "blastem_evidence_paths",
    "budget_report_path",
    "human_approval_record",
    "status_change_record",
}

TAG_PATTERN = re.compile(r"^[A-Z0-9_]+$")
CURATION_ID_PATTERN = re.compile(r"^[a-z0-9_]+$")

REQUIRED_CURATION_BATCH_FIELDS = {
    "id",
    "source_type",
    "source_path",
    "captured_at",
    "verification_status",
    "promotion_allowed",
    "summary",
    "technique_ids",
}

REQUIRED_COVERAGE_FIELDS = {
    "human_technique",
    "domain",
    "canonical_ids",
    "classification",
    "application_rule",
    "status_snapshot",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def non_empty(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return True


def main() -> int:
    repo = repo_root()
    registry_path = repo / "doc" / "05_technical" / "93_16bit_hardware_mastery_registry.json"
    matrix_path = repo / "doc" / "05_technical" / "93_16bit_hardware_mastery_matrix.md"
    coverage_path = repo / "doc" / "05_technical" / "96_advanced_hardware_technique_coverage.json"
    errors: list[str] = []
    warnings: list[str] = []

    if not registry_path.exists():
        print(f"ERROR: missing {registry_path}")
        return 1

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        return 1

    if registry.get("coverage_catalog_path") != "doc/05_technical/96_advanced_hardware_technique_coverage.json":
        errors.append("registry.coverage_catalog_path must point to the canonical coverage catalog")

    coverage_catalog: dict[str, object] = {}
    if not coverage_path.exists():
        errors.append(f"missing coverage catalog: {coverage_path}")
    else:
        try:
            coverage_catalog = json.loads(coverage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid coverage catalog JSON: {exc}")

    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("registry.entries must be a non-empty list")
        entries = []

    statuses = set(registry.get("human_proficiency_statuses") or [])
    if statuses != ALLOWED_HUMAN_STATUS:
        errors.append("human_proficiency_statuses must match the canonical five-status taxonomy")

    legend = registry.get("human_proficiency_legend")
    if not isinstance(legend, dict):
        errors.append("missing human_proficiency_legend")
    else:
        for status in ALLOWED_HUMAN_STATUS:
            if not non_empty(legend.get(status)):
                errors.append(f"human_proficiency_legend missing {status}")

    curation_batches: dict[str, dict[str, object]] = {}
    raw_curation_batches = registry.get("external_curation_batches", [])
    if raw_curation_batches is None:
        raw_curation_batches = []
    if not isinstance(raw_curation_batches, list):
        errors.append("external_curation_batches must be a list when present")
        raw_curation_batches = []

    for index, batch in enumerate(raw_curation_batches):
        if not isinstance(batch, dict):
            errors.append(f"external_curation_batches[{index}] must be an object")
            continue
        batch_id = batch.get("id", f"external_curation_batches[{index}]")
        missing = sorted(REQUIRED_CURATION_BATCH_FIELDS - set(batch))
        if missing:
            errors.append(f"{batch_id}: curation batch missing fields: {', '.join(missing)}")
            continue
        if not isinstance(batch_id, str) or not CURATION_ID_PATTERN.match(batch_id):
            errors.append(f"{batch_id}: invalid curation batch id")
            continue
        if batch_id in curation_batches:
            errors.append(f"{batch_id}: duplicated curation batch id")
        curation_batches[batch_id] = batch

        for field in ("source_type", "source_path", "captured_at", "verification_status", "summary"):
            if not non_empty(batch.get(field)):
                errors.append(f"{batch_id}: curation batch field {field} must be non-empty")

        source_path = batch.get("source_path")
        if isinstance(source_path, str) and source_path and "://" not in source_path:
            resolved_source = repo / source_path
            if not resolved_source.exists():
                errors.append(f"{batch_id}: local curation source does not exist: {source_path}")

        if not isinstance(batch.get("promotion_allowed"), bool):
            errors.append(f"{batch_id}: promotion_allowed must be boolean")

        technique_ids = batch.get("technique_ids")
        if not isinstance(technique_ids, list) or not technique_ids:
            errors.append(f"{batch_id}: technique_ids must be a non-empty list")
        else:
            for technique_id in technique_ids:
                if not isinstance(technique_id, str) or not technique_id.strip():
                    errors.append(f"{batch_id}: invalid technique id in technique_ids")

        if (
            batch.get("verification_status") == "unverified_secondary_text"
            and batch.get("promotion_allowed") is not False
        ):
            errors.append(f"{batch_id}: unverified_secondary_text must set promotion_allowed=false")

    seen_ids: set[str] = set()
    entry_status_by_id: dict[str, str] = {}
    all_tags: set[str] = set()
    human_counts: dict[str, int] = {status: 0 for status in ALLOWED_HUMAN_STATUS}

    for index, entry in enumerate(entries):
        entry_id = entry.get("id", f"entry[{index}]")
        missing = sorted(REQUIRED_ENTRY_FIELDS - set(entry))
        if missing:
            errors.append(f"{entry_id}: missing fields: {', '.join(missing)}")
            continue

        if entry_id in seen_ids:
            errors.append(f"{entry_id}: duplicated id")
        seen_ids.add(entry_id)

        human_status = entry.get("human_proficiency_status")
        if human_status not in ALLOWED_HUMAN_STATUS:
            errors.append(f"{entry_id}: invalid human_proficiency_status {human_status}")
        else:
            human_counts[human_status] += 1
            entry_status_by_id[entry_id] = human_status

        tags = entry.get("technique_tags")
        if not isinstance(tags, list) or not tags:
            errors.append(f"{entry_id}: technique_tags must be a non-empty list")
        else:
            for tag in tags:
                if not isinstance(tag, str) or not TAG_PATTERN.match(tag):
                    errors.append(f"{entry_id}: invalid technique tag {tag!r}")
                else:
                    all_tags.add(tag)

        owner_skills = entry.get("owner_skills")
        if not isinstance(owner_skills, list) or not owner_skills:
            errors.append(f"{entry_id}: owner_skills must be a non-empty list")

        promotion_evidence = entry.get("promotion_evidence")
        if not isinstance(promotion_evidence, dict):
            errors.append(f"{entry_id}: promotion_evidence must be an object")
            promotion_evidence = {}

        if human_status in {"MESTRE_STANDARD", "MESTRE_PRIORITARIA"}:
            missing_evidence = sorted(
                field for field in MASTER_EVIDENCE_FIELDS if not non_empty(promotion_evidence.get(field))
            )
            if missing_evidence:
                errors.append(f"{entry_id}: MESTRE status without evidence: {', '.join(missing_evidence)}")

        curation_source_ids = entry.get("curation_source_ids", [])
        if curation_source_ids is None:
            curation_source_ids = []
        if not isinstance(curation_source_ids, list):
            errors.append(f"{entry_id}: curation_source_ids must be a list when present")
            curation_source_ids = []
        referenced_curation_batches: list[dict[str, object]] = []
        for curation_source_id in curation_source_ids:
            if not isinstance(curation_source_id, str) or not curation_source_id.strip():
                errors.append(f"{entry_id}: invalid curation_source_id {curation_source_id!r}")
                continue
            batch = curation_batches.get(curation_source_id)
            if batch is None:
                errors.append(f"{entry_id}: unknown curation_source_id {curation_source_id}")
            else:
                referenced_curation_batches.append(batch)

        if human_status in {"MESTRE_STANDARD", "MESTRE_PRIORITARIA"} and referenced_curation_batches:
            if not any(batch.get("promotion_allowed") is True for batch in referenced_curation_batches):
                errors.append(f"{entry_id}: MESTRE status cannot be based only on non-promotional external curation batches")

        if human_status == "LABORATORIO" and entry.get("current_status") in {"blastem_proven", "senior_default"}:
            errors.append(f"{entry_id}: LABORATORIO conflicts with mature current_status={entry.get('current_status')}")

        if human_status and human_status.endswith("PRIORITARIA"):
            if not registry.get("promotion_policy"):
                errors.append(f"{entry_id}: PRIORITARIA requires registry.promotion_policy")

    for batch_id, batch in curation_batches.items():
        for technique_id in batch.get("technique_ids", []):
            if technique_id not in seen_ids:
                errors.append(f"{batch_id}: technique_ids references unknown registry id {technique_id}")

    coverage_ids: set[str] = set()
    coverage_items = coverage_catalog.get("coverage", []) if isinstance(coverage_catalog, dict) else []
    if isinstance(coverage_catalog, dict):
        if coverage_catalog.get("registry_source") != "doc/05_technical/93_16bit_hardware_mastery_registry.json":
            errors.append("coverage catalog registry_source must point to the canonical registry")
        if coverage_catalog.get("human_panel") != "doc/05_technical/93_16bit_hardware_mastery_matrix.md":
            errors.append("coverage catalog human_panel must point to the canonical human panel")

        mastery_truth = coverage_catalog.get("mastery_truth")
        expected_master_count = human_counts["MESTRE_STANDARD"] + human_counts["MESTRE_PRIORITARIA"]
        if not isinstance(mastery_truth, dict):
            errors.append("coverage catalog mastery_truth must be an object")
        elif mastery_truth.get("master_count") != expected_master_count:
            errors.append(
                "coverage catalog mastery_truth.master_count must match the registry MESTRE count"
            )

    if not isinstance(coverage_items, list) or not coverage_items:
        errors.append("coverage catalog must contain a non-empty coverage list")
        coverage_items = []
    for index, item in enumerate(coverage_items):
        if not isinstance(item, dict):
            errors.append(f"coverage[{index}] must be an object")
            continue
        missing = sorted(REQUIRED_COVERAGE_FIELDS - set(item))
        if missing:
            errors.append(f"coverage[{index}] missing fields: {', '.join(missing)}")
        human_technique = item.get("human_technique")
        canonical_ids = item.get("canonical_ids")
        if not non_empty(human_technique):
            errors.append(f"coverage[{index}] missing human_technique")
        for field in ("domain", "classification", "application_rule"):
            if not non_empty(item.get(field)):
                errors.append(f"coverage[{index}] field {field} must be non-empty")
        if not isinstance(canonical_ids, list) or not canonical_ids:
            errors.append(f"coverage[{index}] must declare canonical_ids")
            continue
        for canonical_id in canonical_ids:
            if canonical_id not in seen_ids:
                errors.append(f"coverage[{index}] references unknown registry id {canonical_id}")
            elif isinstance(canonical_id, str):
                coverage_ids.add(canonical_id)

        snapshots = item.get("status_snapshot")
        if not isinstance(snapshots, list) or not snapshots:
            errors.append(f"coverage[{index}] status_snapshot must be a non-empty list")
            continue
        snapshot_ids: set[str] = set()
        for snapshot_index, snapshot in enumerate(snapshots):
            if not isinstance(snapshot, dict):
                errors.append(f"coverage[{index}].status_snapshot[{snapshot_index}] must be an object")
                continue
            snapshot_id = snapshot.get("registry_id")
            snapshot_status = snapshot.get("human_proficiency_status")
            if not isinstance(snapshot_id, str) or snapshot_id not in seen_ids:
                errors.append(
                    f"coverage[{index}].status_snapshot[{snapshot_index}] references unknown registry id "
                    f"{snapshot_id!r}"
                )
                continue
            if snapshot_id in snapshot_ids:
                errors.append(f"coverage[{index}] duplicates status snapshot for {snapshot_id}")
            snapshot_ids.add(snapshot_id)
            if snapshot_status != entry_status_by_id.get(snapshot_id):
                errors.append(
                    f"coverage[{index}] status snapshot for {snapshot_id} is stale: "
                    f"{snapshot_status!r} != {entry_status_by_id.get(snapshot_id)!r}"
                )
        if set(canonical_ids) != snapshot_ids:
            errors.append(f"coverage[{index}] status_snapshot must cover exactly its canonical_ids")

    coverage_batch_id = coverage_catalog.get("curation_source_id") if isinstance(coverage_catalog, dict) else None
    coverage_batch = curation_batches.get(coverage_batch_id) if isinstance(coverage_batch_id, str) else None
    if coverage_batch is None:
        errors.append("coverage catalog curation_source_id must reference an existing curation batch")
    else:
        missing_from_coverage = sorted(set(coverage_batch.get("technique_ids", [])) - coverage_ids)
        if missing_from_coverage:
            errors.append(
                "coverage catalog does not map all techniques from its curation batch: "
                + ", ".join(missing_from_coverage)
            )

    if matrix_path.exists():
        matrix = matrix_path.read_text(encoding="utf-8")
        if "HUMAN_PROFICIENCY_PANEL_START" not in matrix or "HUMAN_PROFICIENCY_PANEL_END" not in matrix:
            errors.append("matrix missing HUMAN_PROFICIENCY_PANEL markers")
        for entry_id in seen_ids:
            if f"`{entry_id}`" not in matrix:
                errors.append(f"matrix does not mention registry id {entry_id}")
    else:
        errors.append(f"missing matrix: {matrix_path}")

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    counts = ", ".join(f"{key}={value}" for key, value in sorted(human_counts.items()))
    print(f"technique registry ok: {len(entries)} entries, {len(all_tags)} tags, {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Aggregate animation evidence and cap claims at the weakest proven gate."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from animation_validation_common import load_object, resolve_inside, sha256_file, validate_canonical_schema
from validate_motion_semantics import CANONICAL_REGISTRY_REL, DEFAULT_REGISTRY, TOOL_VERSION as MOTION_TOOL_VERSION, validate as validate_motion_semantics
from validate_strip import TOOL_VERSION as STRIP_TOOL_VERSION, validate_strip


TOOL_VERSION = "1.3.0"
CLAIMS = ["technical_candidate", "motion_semantic_candidate", "human_review_candidate", "ready_for_res", "runtime_candidate", "ready_for_aaa"]
VISUAL_DEPENDENCIES = ("sprite_artifact", "fidelity", "art_direction", "blind_visual_review")
PRINCIPLE_IDS = {
    "squash_and_stretch", "anticipation", "staging",
    "straight_ahead_and_pose_to_pose", "follow_through_and_overlapping_action",
    "slow_in_and_slow_out", "arcs", "secondary_action", "timing",
    "exaggeration", "solid_drawing", "appeal",
}
PRINCIPLES_NEVER_NOT_APPLICABLE = {
    "staging", "straight_ahead_and_pose_to_pose", "timing", "solid_drawing", "appeal",
}
PRINCIPLES_REQUIRING_HUMAN_REVIEW = {"staging", "exaggeration", "solid_drawing", "appeal"}
PRODUCTION_METHODS = {"pose_to_pose", "straight_ahead", "hybrid"}
PRINCIPLE_EVIDENCE_KINDS = {"automated_measurement", "human_visual_review", "artifact_inspection", "runtime_evidence"}
MOTION_REPORT_MINIMUM_VERSION = (1, 2, 0)
MOTION_CONTRACT_BLOCKERS = {
    "source_has_no_temporal_frames",
    "single_pose_source_only",
    "mechanical_probe_cannot_prove_motion",
    "single_pose_affine_animation_masquerade",
}


def _json_normalize(value: Any) -> Any:
    """Make in-memory validator values comparable to their JSON encoding."""
    if isinstance(value, tuple):
        return [_json_normalize(item) for item in value]
    if isinstance(value, list):
        return [_json_normalize(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_normalize(item) for key, item in value.items()}
    return value


def _evidence_ref_is_bound(
    ref: Any, expected_action: str, expected_subject: str, project_root: Path,
    blockers: list[str], *, allow_human: bool = True
) -> bool:
    if not isinstance(ref, dict):
        blockers.append("evidence_ref_unbound")
        return False
    required = {"path", "sha256", "subject_sha256", "action", "evidence_kind"}
    if not required.issubset(ref) or ref.get("action") != expected_action:
        blockers.append("evidence_ref_action_mismatch" if ref.get("action") != expected_action else "evidence_ref_unbound")
        return False
    if ref.get("evidence_kind") not in PRINCIPLE_EVIDENCE_KINDS:
        blockers.append("evidence_ref_unbound")
        return False
    if not allow_human and ref.get("evidence_kind") == "human_visual_review":
        blockers.append("human_visual_review_unproven")
        return False
    if ref.get("subject_sha256") != expected_subject or not isinstance(ref.get("sha256"), str):
        blockers.append("evidence_ref_subject_mismatch")
        return False
    try:
        path = resolve_inside(project_root, ref.get("path", ""))
    except ValueError:
        blockers.append("evidence_ref_unbound")
        return False
    if not path.is_file() or sha256_file(path) != ref.get("sha256"):
        blockers.append("evidence_ref_unbound")
        return False
    return True


def _rederive_child_reports(
    contract: dict[str, Any], strip_report: dict[str, Any], motion_report: dict[str, Any],
    project_root: Path, index: int, blockers: list[str]
) -> None:
    """Re-run both canonical owners; persisted child JSON is never authoritative."""
    try:
        schema_major = int(str(contract.get("schema_version", "0")).split(".", 1)[0])
    except ValueError:
        schema_major = 0
    if schema_major < 3:
        return
    derived_strip = validate_strip(contract, project_root)
    expected_strip_blockers = sorted(set(derived_strip.blockers))
    persisted_strip_blockers = sorted(set(strip_report.get("blockers", [])))
    if (
        strip_report.get("status") != derived_strip.status
        or persisted_strip_blockers != expected_strip_blockers
        or _json_normalize(strip_report.get("metrics")) != _json_normalize(derived_strip.metrics)
    ):
        blockers.append("child_validation_report_tampered")
    derived_motion = validate_motion_semantics(contract, project_root, load_object(DEFAULT_REGISTRY), DEFAULT_REGISTRY)
    expected_motion_blockers = sorted(set(derived_motion.get("blockers", [])))
    persisted_motion_blockers = sorted(set(motion_report.get("blockers", [])))
    if (
        motion_report.get("status") != derived_motion.get("status")
        or persisted_motion_blockers != expected_motion_blockers
        or _json_normalize(motion_report.get("metrics")) != _json_normalize(derived_motion.get("metrics"))
    ):
        blockers.append("child_validation_report_tampered")
    if motion_report.get("tool_name") != "validate_motion_semantics" or motion_report.get("tool_version") != MOTION_TOOL_VERSION:
        blockers.append(f"motion_semantic_report_outdated:{index}")
    if strip_report.get("tool_name") != "validate_strip" or strip_report.get("tool_version") != STRIP_TOOL_VERSION:
        blockers.append("child_validation_report_tampered")
    if motion_report.get("strip_sha256") != derived_motion.get("strip_sha256"):
        blockers.append(f"motion_semantic_report_outdated:{index}")


def _validate_motion_report_binding(
    contract: dict[str, Any], motion_report: dict[str, Any], blockers: list[str]
) -> None:
    expected_strip_sha = str((contract.get("artifact") or {}).get("sha256", ""))
    if motion_report.get("strip_sha256") != expected_strip_sha:
        blockers.append("motion_semantic_report_outdated")
    registry = motion_report.get("registry")
    canonical_sha = sha256_file(DEFAULT_REGISTRY) if DEFAULT_REGISTRY.is_file() else None
    if (
        not isinstance(registry, dict)
        or registry.get("path") != CANONICAL_REGISTRY_REL
        or registry.get("sha256") != canonical_sha
        or registry.get("schema_version") != "1.0.0"
        or registry.get("is_canonical") is not True
    ):
        blockers.append("motion_semantic_report_outdated")


def _validate_action_subject_report(
    report: dict[str, Any], expected_actions: dict[str, str], blockers: list[str]
) -> None:
    subjects = report.get("action_subject_sha256")
    if not isinstance(subjects, dict) or set(subjects) != set(expected_actions):
        blockers.append("package_visual_report_subject_incomplete")
        return
    if any(subjects.get(action) != strip_sha for action, strip_sha in expected_actions.items()):
        blockers.append("package_visual_report_subject_incomplete")


def _validate_human_decision(
    report: dict[str, Any] | None, expected_actions: dict[str, str], report_bindings: dict[str, Any],
    project_root: Path, blockers: list[str]
) -> bool:
    if not isinstance(report, dict) or report.get("review_type") != "human_visual_decision":
        return False
    if report.get("status") != "passed":
        return False
    subjects = report.get("action_subject_sha256")
    reviews = report.get("action_reviews")
    if not isinstance(subjects, dict) or subjects != expected_actions or not isinstance(reviews, dict) or set(reviews) != set(expected_actions):
        blockers.append("human_decision_report_binding_invalid")
        return False
    if any(not isinstance(reviews[action], dict) or reviews[action].get("subject_sha256") != subject for action, subject in expected_actions.items()):
        blockers.append("human_decision_report_binding_invalid")
        return False
    reviewed = report.get("reviewed_reports")
    required = {"fidelity", "art_direction", "blind_visual_review", "animation_principles"}
    if not isinstance(reviewed, dict) or set(reviewed) != required:
        blockers.append("human_decision_report_binding_invalid")
        return False
    valid = True
    for kind in required:
        expected = report_bindings.get(kind)
        item = reviewed.get(kind)
        if not isinstance(expected, dict) or not isinstance(item, dict):
            valid = False
            continue
        if (
            item.get("path") != expected.get("path")
            or item.get("sha256") != expected.get("sha256")
            or item.get("subject_sha256") != expected.get("subject_sha256")
            or item.get("action_subject_sha256") != expected_actions
        ):
            valid = False
            continue
        try:
            path = resolve_inside(project_root, item.get("path", ""))
        except ValueError:
            valid = False
            continue
        if not path.is_file() or sha256_file(path) != item.get("sha256"):
            valid = False
    if not valid:
        blockers.append("human_decision_report_binding_invalid")
    return valid


def _validate_diagnostic_review(
    report: dict[str, Any] | None, expected_actions: dict[str, str], project_root: Path,
    blockers: list[str], expected_review_type: str
) -> bool:
    if not isinstance(report, dict) or report.get("review_type") != expected_review_type:
        return False
    reviews = report.get("action_reviews")
    if not isinstance(reviews, dict) or set(reviews) != set(expected_actions):
        return False
    for action, strip_sha in expected_actions.items():
        item = reviews.get(action)
        if not isinstance(item, dict) or item.get("subject_sha256") != strip_sha:
            return False
        evidence_refs = item.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs or not all(
            _evidence_ref_is_bound(ref, action, strip_sha, project_root, blockers, allow_human=False)
            for ref in evidence_refs
        ):
            return False
        observations = item.get("observations")
        if not isinstance(observations, list) or not observations or not all(
            isinstance(value, str) and action in value for value in observations
        ):
            return False
    return True


def _validate_fidelity_review(
    report: dict[str, Any] | None, expected_actions: dict[str, str], project_root: Path, blockers: list[str]
) -> bool:
    if not _validate_diagnostic_review(
        report, expected_actions, project_root, blockers, "agent_curated_diagnostic_review"
    ):
        return False
    reviews = report.get("action_reviews", {}) if isinstance(report, dict) else {}
    for action in expected_actions:
        findings = reviews[action].get("must_preserve_findings")
        if not isinstance(findings, list) or not findings or any(
            not isinstance(item, dict) or item.get("status") != "passed" for item in findings
        ):
            return False
    return True


def _version_tuple(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    parts = value.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def _contract_semantic_precheck(contract: dict[str, Any], index: int, blockers: list[str]) -> None:
    frames = contract.get("frames") if isinstance(contract.get("frames"), list) else []
    authored = [
        frame for frame in frames
        if isinstance(frame, dict)
        and (frame.get("lineage") or {}).get("transformation") in {"native_reauthored", "authored_inbetween"}
        and (frame.get("lineage") or {}).get("duplicate_role") != "approved_hold"
    ]
    source_ids = [str((frame.get("lineage") or {}).get("source_frame_id", "")) for frame in authored]
    if len(authored) > 1 and len(set(source_ids)) < len(authored):
        blockers.append(f"single_pose_affine_animation_masquerade:{index}")
    if any((frame.get("lineage") or {}).get("transformation") == "mechanical_affine_probe" for frame in frames if isinstance(frame, dict)):
        blockers.append(f"mechanical_probe_cannot_prove_motion:{index}")
    if any(
        (frame.get("support") or {}).get("grounded")
        and (frame.get("support") or {}).get("measurement_method") in {None, "declared_only"}
        for frame in frames if isinstance(frame, dict)
    ):
        blockers.append(f"support_contact_not_artifact_bound:{index}")
    lineart = contract.get("state_lineart_lineage")
    if isinstance(lineart, dict) and lineart.get("lineart_role") == "native_key_pose_lineart":
        if lineart.get("authorship_method") not in {"hand_authored_native", "assisted_native_reauthored"}:
            code = "procedural_contour_declared_native_lineart" if lineart.get("authorship_method") == "procedural_contour_probe" else "native_lineart_authorship_unproven"
            blockers.append(f"{code}:{index}")
        if not isinstance(lineart.get("approval_record"), dict):
            blockers.append(f"native_lineart_approval_unbound:{index}")
    unresolved = set(contract.get("blockers") or []) & MOTION_CONTRACT_BLOCKERS
    if unresolved:
        blockers.append(f"strip_contract_has_unresolved_motion_blocker:{index}")


def _values_for_key(value: Any, key: str) -> list[Any]:
    out: list[Any] = []
    if isinstance(value, dict):
        for item_key, item_value in value.items():
            if item_key == key:
                out.append(item_value)
            out.extend(_values_for_key(item_value, key))
    elif isinstance(value, list):
        for item in value:
            out.extend(_values_for_key(item, key))
    return out


def _load_binding(root: Path, binding: Any, kind: str, blockers: list[str]) -> dict[str, Any] | None:
    if not isinstance(binding, dict):
        blockers.append(f"{kind}_report_missing")
        return None
    try:
        path = resolve_inside(root, binding.get("path", ""))
    except ValueError:
        blockers.append(f"{kind}_report_path_invalid")
        return None
    if not path.is_file():
        blockers.append(f"{kind}_report_missing")
        return None
    if sha256_file(path) != binding.get("sha256"):
        blockers.append(f"{kind}_report_hash_mismatch")
        return None
    try:
        report = load_object(path)
    except (ValueError, json.JSONDecodeError):
        blockers.append(f"{kind}_report_invalid")
        return None
    subject = binding.get("subject_sha256")
    if not isinstance(subject, str) or len(subject) != 64:
        blockers.append(f"{kind}_subject_hash_missing")
    else:
        all_strings = _values_for_key(report, "sha256") + _values_for_key(report, "asset_sha256") + _values_for_key(report, "sheet_sha256") + _values_for_key(report, "strip_sha256")
        all_strings.extend(_values_for_key(report, "subject_sha256"))
        if subject not in all_strings:
            blockers.append(f"{kind}_subject_hash_unbound")
    return report


def _validate_principles_report(
    report: dict[str, Any],
    candidate_id: Any,
    expected_actions: dict[str, str],
    project_root: Path,
    blockers: list[str],
) -> bool:
    schema_errors = validate_canonical_schema(report, "animation_principles_report")
    if schema_errors:
        blockers.append("animation_principles_schema_invalid")
    if set(report) - {"schema_version", "candidate_id", "subject_sha256", "status", "actions"}:
        blockers.append("animation_principles_schema_invalid")
    if report.get("schema_version") != "1.0.0":
        blockers.append("animation_principles_schema_invalid")
    if report.get("candidate_id") != candidate_id:
        blockers.append("animation_principles_candidate_mismatch")
    actions = report.get("actions")
    if not isinstance(actions, list) or not actions:
        blockers.append("animation_principles_incomplete")
        return False
    action_map: dict[str, dict[str, Any]] = {}
    for item in actions:
        if not isinstance(item, dict):
            blockers.append("animation_principles_incomplete")
            continue
        if set(item) - {"action", "strip_sha256", "production_method", "assessments"}:
            blockers.append("animation_principles_schema_invalid")
        action = item.get("action")
        if not isinstance(action, str) or not action or action in action_map:
            blockers.append("animation_principles_action_mismatch")
            continue
        action_map[action] = item
    if set(action_map) != set(expected_actions):
        blockers.append("animation_principles_action_mismatch")

    derived_status = "passed"
    for action, expected_sha in expected_actions.items():
        item = action_map.get(action)
        if not item:
            continue
        if item.get("strip_sha256") != expected_sha:
            blockers.append("animation_principles_strip_hash_mismatch")
        if item.get("production_method") not in PRODUCTION_METHODS:
            blockers.append("animation_production_method_missing")
        assessments = item.get("assessments")
        if not isinstance(assessments, list):
            blockers.append("animation_principles_incomplete")
            continue
        assessment_map: dict[str, dict[str, Any]] = {}
        for assessment in assessments:
            if not isinstance(assessment, dict):
                blockers.append("animation_principles_incomplete")
                continue
            if set(assessment) - {"principle_id", "status", "observation", "evidence_kinds", "evidence_refs", "not_applicable_reason"}:
                blockers.append("animation_principles_schema_invalid")
            principle_id = assessment.get("principle_id")
            if principle_id not in PRINCIPLE_IDS or principle_id in assessment_map:
                blockers.append("animation_principles_incomplete")
                continue
            assessment_map[str(principle_id)] = assessment
        if set(assessment_map) != PRINCIPLE_IDS:
            blockers.append("animation_principles_incomplete")
        for principle_id, assessment in assessment_map.items():
            status = assessment.get("status")
            evidence_kinds = assessment.get("evidence_kinds")
            evidence_refs = assessment.get("evidence_refs")
            if status not in {"passed", "not_applicable", "needs_review", "failed"}:
                blockers.append("animation_principles_incomplete")
                continue
            if not isinstance(assessment.get("observation"), str) or not assessment["observation"].strip():
                blockers.append("animation_principles_incomplete")
            if not isinstance(evidence_kinds, list) or not evidence_kinds or not isinstance(evidence_refs, list) or not evidence_refs:
                blockers.append("animation_principles_evidence_missing")
            elif any(kind not in PRINCIPLE_EVIDENCE_KINDS for kind in evidence_kinds):
                blockers.append("animation_principles_evidence_kind_invalid")
            if isinstance(evidence_refs, list):
                for ref in evidence_refs:
                    if isinstance(ref, dict) and ref.get("action") != action:
                        blockers.append("animation_principle_evidence_not_action_specific")
                        continue
                    if not _evidence_ref_is_bound(ref, action, expected_sha, project_root, blockers):
                        continue
                    if ref.get("evidence_kind") not in (evidence_kinds or []):
                        blockers.append("animation_principle_evidence_not_action_specific")
            if status == "not_applicable":
                if principle_id in PRINCIPLES_NEVER_NOT_APPLICABLE:
                    blockers.append("animation_principle_illegal_not_applicable")
                reason = assessment.get("not_applicable_reason")
                if not isinstance(reason, str) or not reason.strip():
                    blockers.append("animation_principle_not_applicable_without_reason")
            if status == "passed" and principle_id in PRINCIPLES_REQUIRING_HUMAN_REVIEW:
                if "human_visual_review" not in (evidence_kinds or []):
                    blockers.append("animation_principle_human_review_missing")
            if status == "failed":
                derived_status = "failed"
            elif status == "needs_review" and derived_status != "failed":
                derived_status = "needs_review"
    if report.get("status") != derived_status:
        blockers.append("animation_principles_status_inconsistent")
    if report.get("status") != "passed":
        blockers.append("animation_principles_gate_failed")
    principle_blockers = {
        "animation_principles_candidate_mismatch", "animation_principles_incomplete",
        "animation_principles_schema_invalid",
        "animation_principles_action_mismatch", "animation_principles_strip_hash_mismatch",
        "animation_production_method_missing", "animation_principles_evidence_missing",
        "animation_principle_illegal_not_applicable",
        "animation_principle_not_applicable_without_reason",
        "animation_principle_human_review_missing", "animation_principles_status_inconsistent",
        "animation_principles_gate_failed", "animation_principles_evidence_kind_invalid",
        "animation_principle_evidence_not_action_specific",
        "evidence_ref_unbound", "evidence_ref_action_mismatch", "evidence_ref_subject_mismatch",
        "human_visual_review_unproven",
    }
    return not any(code in principle_blockers for code in blockers)


def validate(manifest: dict[str, Any], project_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    if validate_canonical_schema(manifest, "animation_candidate_manifest"):
        blockers.append("animation_candidate_schema_invalid")
    quality_target = manifest.get("quality_target")
    if quality_target not in {"standard", "premium", "aaa"}:
        blockers.append("animation_quality_target_missing")
    loaded_reports: dict[str, dict[str, Any]] = {}
    frame_hash_owners: dict[str, set[str]] = {}
    expected_actions: dict[str, str] = {}
    strips = manifest.get("strips")
    if not isinstance(strips, list) or not strips:
        blockers.append("animation_candidate_has_no_strips")
        strips = []
    for index, strip in enumerate(strips):
        if not isinstance(strip, dict):
            blockers.append(f"strip_binding_invalid:{index}")
            continue
        contract = _load_binding(project_root, strip.get("contract"), f"strip_{index}_contract", blockers)
        strip_report = _load_binding(project_root, strip.get("artifact_report"), f"strip_{index}_artifact", blockers)
        motion_report = _load_binding(project_root, strip.get("motion_report"), f"strip_{index}_motion", blockers)
        if strip_report and strip_report.get("status") != "ok":
            blockers.append(f"strip_artifact_gate_failed:{index}")
        if motion_report and motion_report.get("status") != "ok":
            blockers.append(f"motion_semantic_gate_failed:{index}")
        if motion_report and (
            motion_report.get("tool_name") != "validate_motion_semantics"
            or (_version_tuple(motion_report.get("tool_version")) or (0, 0, 0)) < MOTION_REPORT_MINIMUM_VERSION
        ):
            blockers.append(f"motion_semantic_report_outdated:{index}")
        if contract and motion_report:
            _validate_motion_report_binding(contract, motion_report, blockers)
            if strip_report:
                _rederive_child_reports(contract, strip_report, motion_report, project_root, index, blockers)
        if contract and any((frame.get("lineage") or {}).get("transformation") == "source_cell_reorder" for frame in contract.get("frames", [])):
            blockers.append("action_is_reordered_source_cells")
        if contract:
            try:
                schema_major = int(str(contract.get("schema_version", "0")).split(".", 1)[0])
            except ValueError:
                schema_major = 0
            if schema_major >= 3 and validate_canonical_schema(contract, "animation_strip_contract"):
                blockers.append(f"animation_strip_schema_invalid:{index}")
            _contract_semantic_precheck(contract, index, blockers)
        action = str(contract.get("action", f"strip_{index}")) if contract else f"strip_{index}"
        if contract:
            strip_sha = str((contract.get("artifact") or {}).get("sha256") or strip["contract"].get("subject_sha256", ""))
            if action in expected_actions:
                blockers.append("duplicate_action_strip")
            expected_actions[action] = strip_sha
        if motion_report:
            motion_metrics = motion_report.get("metrics", {})
            hashes = motion_metrics.get("frame_pixel_sha256") or motion_metrics.get("frame_mask_sha256", [])
            for frame_hash in hashes:
                frame_hash_owners.setdefault(str(frame_hash), set()).add(action)

    authorized = {
        item.get("frame_mask_sha256") for item in manifest.get("authorized_cross_action_frame_reuse", [])
        if isinstance(item, dict) and isinstance(item.get("reason"), str) and item.get("reason").strip()
    }
    cross_action = {key: sorted(value) for key, value in frame_hash_owners.items() if len(value) > 1 and key not in authorized}
    if cross_action:
        blockers.append("cross_action_frame_reuse")

    reports = manifest.get("reports", {})
    if not isinstance(reports, dict):
        reports = {}
    for kind, binding in reports.items():
        report = _load_binding(project_root, binding, kind, blockers)
        if report is not None:
            loaded_reports[kind] = report

    principles_report = loaded_reports.get("animation_principles")
    principles_passed = False
    if principles_report is None:
        warnings.append("animation_principles_not_closed")
    else:
        principles_passed = _validate_principles_report(
            principles_report, manifest.get("candidate_id"), expected_actions, project_root, blockers
        )

    human_report = loaded_reports.get("human_decision")
    human_decision_valid = _validate_human_decision(
        human_report, expected_actions, manifest.get("reports", {}), project_root, blockers
    )
    principle_needs_human = any(
        isinstance(action, dict)
        and any(
            isinstance(assessment, dict)
            and "human_visual_review" in (assessment.get("evidence_kinds") or [])
            for assessment in (action.get("assessments") or [])
        )
        for action in (principles_report.get("actions", []) if isinstance(principles_report, dict) else [])
    )
    if principle_needs_human and not human_decision_valid and (
        not isinstance(human_report, dict) or human_report.get("review_type") != "human_visual_decision"
    ):
        blockers.append("human_visual_review_unproven")

    for kind in VISUAL_DEPENDENCIES:
        report = loaded_reports.get(kind)
        if report is not None:
            _validate_action_subject_report(report, expected_actions, blockers)

    dependency_status = {kind: str(loaded_reports.get(kind, {}).get("status", "missing")) for kind in VISUAL_DEPENDENCIES}
    sprite_artifact = loaded_reports.get("sprite_artifact", {})
    visual_dependencies_passed = all(value == "passed" for value in dependency_status.values()) and sprite_artifact.get("visual_pass") is True
    action_recognition_passed = dependency_status.get("blind_visual_review") == "passed"
    if not _validate_diagnostic_review(
        loaded_reports.get("blind_visual_review"), expected_actions, project_root, blockers,
        "independent_blind_visual_review"
    ):
        blockers.append("viewpoint_continuity_unproven")
    if not _validate_fidelity_review(loaded_reports.get("fidelity"), expected_actions, project_root, blockers):
        blockers.append("model_sheet_to_sprite_fidelity_unproven")
    if sprite_artifact.get("visual_pass") is True and not visual_dependencies_passed:
        blockers.append("visual_pass_self_asserted")
    if "blind_visual_review" in loaded_reports and loaded_reports["blind_visual_review"].get("status") != "passed":
        blockers.append("blind_action_recognition_failed")
    if any(value in {"needs_review", "failed", "missing"} for value in dependency_status.values()):
        warnings.append("visual_dependencies_not_closed")

    hardware_keys = ("hardware_cells_per_frame", "peak_sprites_per_scanline", "peak_pixels_per_scanline")
    hardware_values: dict[str, list[Any]] = {}
    sources = list(loaded_reports.values())
    for strip in strips:
        if isinstance(strip, dict):
            contract = _load_binding(project_root, strip.get("contract"), "contract_recheck", [])
            if contract:
                sources.append(contract)
    for key in hardware_keys:
        values = [value for source in sources for value in _values_for_key(source, key)]
        normalized = sorted({json.dumps(value, sort_keys=True) for value in values})
        hardware_values[key] = [json.loads(value) for value in normalized]
        if len(normalized) > 1:
            blockers.append("metasprite_layout_conflict")

    strip_gates_passed = bool(strips) and not any(
        code.startswith("strip_") or code.startswith("motion_") or code in {
            "cross_action_frame_reuse", "action_is_reordered_source_cells",
            "duplicate_action_strip", "animation_quality_target_missing",
            "single_pose_affine_animation_masquerade", "mechanical_probe_cannot_prove_motion",
            "support_contact_not_artifact_bound", "procedural_contour_declared_native_lineart",
            "native_lineart_authorship_unproven", "native_lineart_approval_unbound",
            "native_lineart_approval_status_invalid", "animation_strip_schema_invalid",
            "animation_production_provenance_missing", "code_authored_character_pixels",
            "native_pixel_integer_scale_masquerade", "authored_pixel_source_unbound",
            "animation_producer_record_unbound", "animation_producer_record_not_closed",
            "animation_producer_record_mismatch",
            "strip_contract_has_unresolved_motion_blocker", "motion_semantic_report_outdated",
            "package_visual_report_subject_incomplete", "noncanonical_motion_profile",
            "source_frame_artifact_unbound", "source_frame_region_outside",
            "source_frame_pixel_hash_mismatch", "approved_hold_lineage_unbound",
            "child_validation_report_tampered",
        }
        or any(code.startswith(prefix + ":") for prefix in (
            "single_pose_affine_animation_masquerade", "mechanical_probe_cannot_prove_motion",
            "support_contact_not_artifact_bound", "procedural_contour_declared_native_lineart",
            "native_lineart_authorship_unproven", "native_lineart_approval_unbound",
            "native_lineart_approval_status_invalid", "animation_strip_schema_invalid",
            "animation_production_provenance_missing", "code_authored_character_pixels",
            "native_pixel_integer_scale_masquerade", "authored_pixel_source_unbound",
            "animation_producer_record_unbound", "animation_producer_record_not_closed",
            "animation_producer_record_mismatch",
            "strip_contract_has_unresolved_motion_blocker", "motion_semantic_report_outdated",
            "child_validation_report_tampered",
        ))
        for code in blockers
    )
    maximum_claim = "technical_candidate" if strip_gates_passed else "none"
    if strip_gates_passed and action_recognition_passed:
        maximum_claim = "motion_semantic_candidate"
    if strip_gates_passed and visual_dependencies_passed and principles_passed:
        maximum_claim = "human_review_candidate"
    human = loaded_reports.get("human_decision", {})
    budget = loaded_reports.get("budget", {})
    if maximum_claim == "human_review_candidate" and human_decision_valid and budget.get("status") == "passed" and "metasprite_layout_conflict" not in blockers:
        maximum_claim = "ready_for_res"
    runtime = loaded_reports.get("runtime", {})
    if maximum_claim == "ready_for_res" and runtime.get("status") == "passed":
        maximum_claim = "runtime_candidate"
    if manifest.get("validator_fixture") is True:
        maximum_claim = "technical_candidate"

    requested = manifest.get("requested_claim", "technical_candidate")
    if requested not in CLAIMS:
        blockers.append("requested_claim_unknown")
    if manifest.get("validator_fixture") is True and requested != "technical_candidate":
        blockers.append("validator_fixture_claim_ceiling_exceeded")
    elif requested != "technical_candidate" and (maximum_claim == "none" or CLAIMS.index(requested) > CLAIMS.index(maximum_claim)):
        blockers.append("claim_dependency_violation")
    if requested == "ready_for_aaa":
        blockers.append("ready_for_aaa_requires_aaa_pipeline_guardian")

    human_gate_ready = (
        manifest.get("validator_fixture") is not True
        and strip_gates_passed and visual_dependencies_passed and principles_passed
    )
    if manifest.get("human_gate_open") is True and not human_gate_ready:
        blockers.append("human_gate_opened_on_failed_candidate")
    return {
        "tool_name": "validate_animation_candidate",
        "tool_version": TOOL_VERSION,
        "status": "ok" if not blockers else "error",
        "candidate_id": manifest.get("candidate_id"),
        "quality_target": quality_target,
        "requested_claim": requested,
        "maximum_proven_claim": maximum_claim,
        "human_gate_ready": human_gate_ready,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "metrics": {
            "strip_count": len(strips),
            "visual_dependency_status": dependency_status,
            "animation_principles_status": (
                principles_report.get("status") if principles_report else "missing"
            ),
            "animation_principles_actions": sorted(expected_actions),
            "blind_action_recognition_passed": action_recognition_passed,
            "cross_action_frame_reuse": cross_action,
            "hardware_values_by_report": hardware_values,
        },
    }


def self_check() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        def write(name: str, value: dict[str, Any], subject: str) -> dict[str, str]:
            value = dict(value)
            value.setdefault("subject_sha256", subject)
            path = root / name
            path.write_text(json.dumps(value), encoding="utf-8")
            return {"path": name, "sha256": sha256_file(path), "subject_sha256": subject}

        idle_subject, run_subject, candidate_subject = "1" * 64, "2" * 64, "3" * 64
        def contract_value(action: str, subject: str) -> dict[str, Any]:
            return {
                "action": action,
                "frames": [{
                    "lineage": {"source_frame_id": f"{action}_0", "transformation": "native_reauthored", "duplicate_role": "none"},
                    "support": {"grounded": True, "measurement_method": "pixel_derived", "contacts": [{"id": "ground", "x": 8, "y": 15}]},
                }],
                "state_lineart_lineage": {
                    "lineart_role": "native_key_pose_lineart", "authorship_method": "hand_authored_native",
                    "approval_record": {"path": "approval.json", "sha256": "a" * 64, "subject_sha256": subject},
                },
                "artifact": {"sha256": subject},
                "blockers": [],
                "metasprite_layout": {"hardware_cells_per_frame": 1, "peak_sprites_per_scanline": 1, "peak_pixels_per_scanline": 16},
            }
        contract_idle = write("idle_contract.json", contract_value("idle", idle_subject), idle_subject)
        contract_run = write("run_contract.json", contract_value("run", run_subject), run_subject)
        artifact_idle = write("artifact_idle.json", {"status": "ok", "strip_sha256": idle_subject}, idle_subject)
        artifact_run = write("artifact_run.json", {"status": "ok", "strip_sha256": run_subject}, run_subject)
        registry_binding = {
            "path": CANONICAL_REGISTRY_REL,
            "sha256": sha256_file(DEFAULT_REGISTRY),
            "schema_version": "1.0.0",
            "is_canonical": True,
        }
        motion_idle = write("motion_idle.json", {"tool_name": "validate_motion_semantics", "tool_version": "1.2.0", "status": "ok", "strip_sha256": idle_subject, "registry": registry_binding, "metrics": {"frame_mask_sha256": ["a" * 64]}}, idle_subject)
        motion_run = write("motion_run.json", {"tool_name": "validate_motion_semantics", "tool_version": "1.2.0", "status": "ok", "strip_sha256": run_subject, "registry": registry_binding, "metrics": {"frame_mask_sha256": ["b" * 64]}}, run_subject)
        evidence_refs: dict[str, dict[str, str]] = {}
        human_refs: dict[str, dict[str, str]] = {}
        for action, subject in {"idle": idle_subject, "run": run_subject}.items():
            evidence_path = root / f"{action}_diagnostic_evidence.json"
            evidence_path.write_text(json.dumps({"action": action, "subject_sha256": subject, "kind": "diagnostic"}), encoding="utf-8")
            evidence_refs[action] = {"path": evidence_path.name, "sha256": sha256_file(evidence_path), "subject_sha256": subject, "action": action, "evidence_kind": "artifact_inspection"}
            human_path = root / f"{action}_human_evidence.json"
            human_path.write_text(json.dumps({"action": action, "subject_sha256": subject, "kind": "human_decision"}), encoding="utf-8")
            human_refs[action] = {"path": human_path.name, "sha256": sha256_file(human_path), "subject_sha256": subject, "action": action, "evidence_kind": "human_visual_review"}
        passed_reports = {}
        for kind in (*VISUAL_DEPENDENCIES, "human_decision", "budget"):
            value = {"status": "passed", "visual_pass": True if kind == "sprite_artifact" else None,
                     "hardware_cells_per_frame": 1, "peak_sprites_per_scanline": 1, "peak_pixels_per_scanline": 16}
            if kind in VISUAL_DEPENDENCIES:
                value["action_subject_sha256"] = {"idle": idle_subject, "run": run_subject}
            if kind in {"blind_visual_review", "fidelity"}:
                value["review_type"] = "independent_blind_visual_review" if kind == "blind_visual_review" else "agent_curated_diagnostic_review"
                value["action_reviews"] = {
                    action: {
                        "subject_sha256": subject,
                        "observations": [f"{action}: diagnostic evidence is present for this action"],
                        "evidence_refs": [evidence_refs[action]],
                        "must_preserve_findings": [{"feature": "round_body_r1", "status": "passed"}],
                    }
                    for action, subject in {"idle": idle_subject, "run": run_subject}.items()
                }
            if kind == "human_decision":
                value["review_type"] = "human_visual_decision"
                value["action_subject_sha256"] = {"idle": idle_subject, "run": run_subject}
                value["action_reviews"] = {action: {"subject_sha256": subject, "evidence_refs": [human_refs[action]]} for action, subject in {"idle": idle_subject, "run": run_subject}.items()}
            passed_reports[kind] = write(f"{kind}.json", value, candidate_subject)
        def assessments_for(action: str) -> list[dict[str, Any]]:
            assessments = []
            for principle_id in sorted(PRINCIPLE_IDS):
                evidence_kinds = ["artifact_inspection"]
                if principle_id in PRINCIPLES_REQUIRING_HUMAN_REVIEW:
                    evidence_kinds.append("human_visual_review")
                assessments.append({
                    "principle_id": principle_id,
                    "status": "passed",
                    "observation": f"{action}: {principle_id} observed in native playback evidence",
                    "evidence_kinds": evidence_kinds,
                    "evidence_refs": [human_refs[action] if principle_id in PRINCIPLES_REQUIRING_HUMAN_REVIEW else evidence_refs[action]],
                })
            return assessments
        passed_reports["animation_principles"] = write(
            "animation_principles.json",
            {
                "schema_version": "1.0.0",
                "candidate_id": "hero_motion",
                "status": "passed",
                "actions": [
                    {"action": "idle", "strip_sha256": idle_subject, "production_method": "pose_to_pose", "assessments": assessments_for("idle")},
                    {"action": "run", "strip_sha256": run_subject, "production_method": "hybrid", "assessments": assessments_for("run")},
                ],
            },
            candidate_subject,
        )
        human_value = json.loads((root / "human_decision.json").read_text(encoding="utf-8"))
        human_value["reviewed_reports"] = {
            kind: {
                "path": passed_reports[kind]["path"], "sha256": passed_reports[kind]["sha256"],
                "subject_sha256": passed_reports[kind]["subject_sha256"],
                "action_subject_sha256": {"idle": idle_subject, "run": run_subject},
            }
            for kind in ("fidelity", "art_direction", "blind_visual_review", "animation_principles")
        }
        passed_reports["human_decision"] = write("human_decision_bound.json", human_value, candidate_subject)
        manifest = {
            "schema_version": "1.1.0",
            "candidate_id": "hero_motion",
            "quality_target": "premium",
            "requested_claim": "ready_for_res",
            "human_gate_open": True,
            "strips": [
                {"contract": contract_idle, "artifact_report": artifact_idle, "motion_report": motion_idle},
                {"contract": contract_run, "artifact_report": artifact_run, "motion_report": motion_run},
            ],
            "reports": passed_reports,
        }
        positive = validate(manifest, root)
        contradiction = json.loads(json.dumps(manifest))
        contradiction["reports"]["fidelity"] = write("fidelity_review.json", {"status": "needs_review"}, candidate_subject)
        negative = validate(contradiction, root)
        reused = json.loads(json.dumps(manifest))
        reused["strips"][1]["motion_report"] = write("motion_reused.json", {"tool_name": "validate_motion_semantics", "tool_version": "1.1.0", "status": "ok", "strip_sha256": run_subject, "metrics": {"frame_mask_sha256": ["a" * 64]}}, run_subject)
        reused_report = validate(reused, root)
        conflict = json.loads(json.dumps(manifest))
        conflict["reports"]["budget"] = write("budget_conflict.json", {"status": "passed", "hardware_cells_per_frame": 4, "peak_sprites_per_scanline": 4, "peak_pixels_per_scanline": 32}, candidate_subject)
        conflict_report = validate(conflict, root)
        blind_fail = json.loads(json.dumps(manifest))
        blind_fail["reports"]["blind_visual_review"] = write("blind_failed.json", {"status": "failed"}, candidate_subject)
        blind_fail_report = validate(blind_fail, root)
        unbound = json.loads(json.dumps(manifest))
        unbound["reports"]["fidelity"]["subject_sha256"] = "9" * 64
        unbound_report = validate(unbound, root)
        package_incomplete = json.loads(json.dumps(manifest))
        incomplete_visual = json.loads((root / "art_direction.json").read_text(encoding="utf-8"))
        incomplete_visual["action_subject_sha256"] = {"idle": idle_subject}
        package_incomplete["reports"]["art_direction"] = write("art_direction_incomplete.json", incomplete_visual, candidate_subject)
        package_incomplete_report = validate(package_incomplete, root)
        incomplete = json.loads(json.dumps(manifest))
        incomplete_principles = json.loads((root / "animation_principles.json").read_text(encoding="utf-8"))
        incomplete_principles["actions"][0]["assessments"] = incomplete_principles["actions"][0]["assessments"][:-1]
        incomplete["reports"]["animation_principles"] = write("principles_incomplete.json", incomplete_principles, candidate_subject)
        incomplete_report = validate(incomplete, root)
        fake_human = json.loads(json.dumps(manifest))
        fake_report_value = json.loads((root / "animation_principles.json").read_text(encoding="utf-8"))
        for assessment in fake_report_value["actions"][0]["assessments"]:
            if assessment["principle_id"] == "appeal":
                assessment["evidence_kinds"] = ["automated_measurement"]
        fake_human["reports"]["animation_principles"] = write("principles_fake_human.json", fake_report_value, candidate_subject)
        fake_human_report = validate(fake_human, root)
        illegal_na = json.loads(json.dumps(manifest))
        illegal_na_value = json.loads((root / "animation_principles.json").read_text(encoding="utf-8"))
        for assessment in illegal_na_value["actions"][0]["assessments"]:
            if assessment["principle_id"] == "appeal":
                assessment["status"] = "not_applicable"
                assessment["not_applicable_reason"] = "incorrectly waived for fixture"
        illegal_na["reports"]["animation_principles"] = write("principles_illegal_na.json", illegal_na_value, candidate_subject)
        illegal_na_report = validate(illegal_na, root)
        missing_method = json.loads(json.dumps(manifest))
        missing_method_value = json.loads((root / "animation_principles.json").read_text(encoding="utf-8"))
        missing_method_value["actions"][0].pop("production_method")
        missing_method["reports"]["animation_principles"] = write("principles_missing_method.json", missing_method_value, candidate_subject)
        missing_method_report = validate(missing_method, root)
        invalid_evidence = json.loads(json.dumps(manifest))
        invalid_evidence_value = json.loads((root / "animation_principles.json").read_text(encoding="utf-8"))
        invalid_evidence_value["actions"][0]["assessments"][0]["evidence_kinds"] = ["motion_report"]
        invalid_evidence["reports"]["animation_principles"] = write("principles_invalid_evidence.json", invalid_evidence_value, candidate_subject)
        invalid_evidence_report = validate(invalid_evidence, root)
        action_specific = json.loads(json.dumps(manifest))
        action_specific_value = json.loads((root / "animation_principles.json").read_text(encoding="utf-8"))
        action_specific_value["actions"][0]["assessments"][0]["evidence_refs"] = [evidence_refs["run"]]
        action_specific["reports"]["animation_principles"] = write("principles_wrong_action.json", action_specific_value, candidate_subject)
        action_specific_report = validate(action_specific, root)
        no_diagnostic = json.loads(json.dumps(manifest))
        no_diagnostic_value = json.loads((root / "blind_visual_review.json").read_text(encoding="utf-8"))
        no_diagnostic_value.pop("review_type", None)
        no_diagnostic_value.pop("action_reviews", None)
        no_diagnostic["reports"]["blind_visual_review"] = write("blind_without_diagnostic_review.json", no_diagnostic_value, candidate_subject)
        no_diagnostic_report = validate(no_diagnostic, root)
        fidelity_unproven = json.loads(json.dumps(manifest))
        fidelity_unproven_value = json.loads((root / "fidelity.json").read_text(encoding="utf-8"))
        fidelity_unproven_value["action_reviews"]["idle"]["must_preserve_findings"] = [{"feature": "drifted_identity", "status": "failed"}]
        fidelity_unproven["reports"]["fidelity"] = write("fidelity_unproven.json", fidelity_unproven_value, candidate_subject)
        fidelity_unproven_report = validate(fidelity_unproven, root)
        one_pose = json.loads(json.dumps(manifest))
        one_pose_contract = contract_value("idle", idle_subject)
        one_pose_contract["frames"] = [
            {"lineage": {"source_frame_id": "one_pose", "transformation": "native_reauthored", "duplicate_role": "none"}, "support": {"grounded": True, "measurement_method": "pixel_derived", "contacts": []}},
            {"lineage": {"source_frame_id": "one_pose", "transformation": "native_reauthored", "duplicate_role": "none"}, "support": {"grounded": True, "measurement_method": "pixel_derived", "contacts": []}},
        ]
        one_pose["strips"][0]["contract"] = write("idle_one_pose_contract.json", one_pose_contract, idle_subject)
        one_pose_report = validate(one_pose, root)
    if positive["status"] != "ok" or positive["maximum_proven_claim"] != "ready_for_res":
        print(f"self-check failed: positive aggregate rejected: {positive}", file=sys.stderr)
        return 1
    if "visual_pass_self_asserted" not in negative["blockers"] or "claim_dependency_violation" not in negative["blockers"]:
        print(f"self-check failed: visual contradiction passed: {negative}", file=sys.stderr)
        return 1
    if "cross_action_frame_reuse" not in reused_report["blockers"]:
        print("self-check failed: cross-action reuse passed", file=sys.stderr)
        return 1
    if "metasprite_layout_conflict" not in conflict_report["blockers"]:
        print("self-check failed: contradictory metasprite layouts passed", file=sys.stderr)
        return 1
    if "blind_action_recognition_failed" not in blind_fail_report["blockers"]:
        print("self-check failed: blind action recognition failure passed", file=sys.stderr)
        return 1
    if "fidelity_subject_hash_unbound" not in unbound_report["blockers"]:
        print("self-check failed: report not bound to its subject passed", file=sys.stderr)
        return 1
    if "package_visual_report_subject_incomplete" not in package_incomplete_report["blockers"]:
        print("self-check failed: incomplete per-action visual subject report passed", file=sys.stderr)
        return 1
    if "animation_principles_incomplete" not in incomplete_report["blockers"]:
        print("self-check failed: incomplete 12-principle report passed", file=sys.stderr)
        return 1
    if "animation_principle_human_review_missing" not in fake_human_report["blockers"]:
        print("self-check failed: automated appeal report passed as human review", file=sys.stderr)
        return 1
    if "animation_principle_illegal_not_applicable" not in illegal_na_report["blockers"]:
        print("self-check failed: required principle passed as not-applicable", file=sys.stderr)
        return 1
    if "animation_production_method_missing" not in missing_method_report["blockers"]:
        print("self-check failed: missing production method passed", file=sys.stderr)
        return 1
    if "animation_principles_evidence_kind_invalid" not in invalid_evidence_report["blockers"]:
        print("self-check failed: non-canonical principle evidence kind passed", file=sys.stderr)
        return 1
    if "animation_principle_evidence_not_action_specific" not in action_specific_report["blockers"]:
        print("self-check failed: cross-action principle evidence passed", file=sys.stderr)
        return 1
    if "viewpoint_continuity_unproven" not in no_diagnostic_report["blockers"]:
        print("self-check failed: missing viewpoint diagnostic review passed", file=sys.stderr)
        return 1
    if "model_sheet_to_sprite_fidelity_unproven" not in fidelity_unproven_report["blockers"]:
        print("self-check failed: failed must-preserve fidelity review passed", file=sys.stderr)
        return 1
    if not any(code.startswith("single_pose_affine_animation_masquerade:") for code in one_pose_report["blockers"]):
        print("self-check failed: single source pose passed aggregate motion gate", file=sys.stderr)
        return 1
    print("validate_animation_candidate self-check passed (claims, provenance, principles, reuse, metasprite, blind review, hash binding)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()
    if not args.manifest or not args.project_root:
        parser.error("--manifest and --project-root are required")
    report = validate(load_object(args.manifest), args.project_root.resolve())
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())

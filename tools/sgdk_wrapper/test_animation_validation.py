#!/usr/bin/env python3
"""Regression runner for the canonical artifact-bound animation gate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = [
    "tools/sgdk_wrapper/.agent/scripts/validate_lineart_topology.py",
    "tools/sgdk_wrapper/.agent/scripts/validate_animation_strip_artifact.py",
    "tools/sgdk_wrapper/.agent/scripts/validate_motion_semantics.py",
    "tools/sgdk_wrapper/.agent/scripts/validate_animation_candidate.py",
    "tools/sgdk_wrapper/.agent/scripts/render_animation_evidence.py",
]
SCHEMAS = [
    "tools/sgdk_wrapper/schemas/animation_strip_contract.schema.json",
    "tools/sgdk_wrapper/schemas/motion_profile_registry.schema.json",
    "tools/sgdk_wrapper/schemas/animation_candidate_manifest.schema.json",
    "tools/sgdk_wrapper/schemas/animation_principles_report.schema.json",
]


def main() -> int:
    passed = 0
    failed: list[str] = []
    for rel in TOOLS:
        proc = subprocess.run([sys.executable, str(ROOT / rel), "--self-check"], cwd=ROOT, capture_output=True, text=True)
        if proc.returncode == 0:
            passed += 1
            print(f"[PASS] {rel}: {(proc.stdout + proc.stderr).strip().splitlines()[-1]}")
        else:
            failed.append(rel)
            print(f"[FAIL] {rel}\n{proc.stdout}{proc.stderr}")
    for rel in SCHEMAS:
        try:
            value = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            if not isinstance(value, dict) or value.get("type") != "object":
                raise ValueError("object schema required")
        except Exception as exc:
            failed.append(rel)
            print(f"[FAIL] {rel}: {exc}")
        else:
            passed += 1
            print(f"[PASS] {rel}: valid JSON object schema")
    fixture_path = ROOT / "tools/sgdk_wrapper/ci/fixtures/animation_validation/fixture_manifest.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    expected = {case["expected_blocker"] for case in fixture["cases"]}
    required = {
        "neighbor_cell_fragment_detected", "lineart_fill_masquerading_as_contour",
        "lineart_stroke_over_1px", "action_is_reordered_source_cells",
        "undeclared_duplicate_frame", "cross_action_frame_reuse",
        "visual_pass_self_asserted", "claim_dependency_violation",
        "gif_delay_contract_mismatch", "metasprite_layout_conflict",
        "foot_slide_detected",
        "blind_action_recognition_failed", "fidelity_subject_hash_unbound",
        "duplicate_timing_authority",
        "animation_principles_incomplete",
        "animation_principle_illegal_not_applicable",
        "animation_principle_human_review_missing",
        "animation_production_method_missing",
        "single_pose_affine_animation_masquerade",
        "mechanical_probe_cannot_prove_motion",
        "procedural_contour_declared_native_lineart",
        "support_contact_not_artifact_bound",
        "motion_semantic_report_outdated",
        "strip_contract_has_unresolved_motion_blocker",
        "animation_principles_evidence_kind_invalid",
        "animation_strip_schema_invalid",
        "native_lineart_approval_status_invalid",
        "native_pixel_integer_scale_masquerade",
        "code_authored_character_pixels",
        "animation_production_provenance_missing",
        "mechanical_resize_mislabeled_native",
        "vector_procedural_lineart_declared_native",
        "source_frame_lineage_not_independent",
        "source_frame_lineage_mismatch",
        "noncanonical_motion_profile",
        "package_visual_report_subject_incomplete",
        "animation_principle_evidence_not_action_specific",
        "viewpoint_continuity_unproven",
        "model_sheet_to_sprite_fidelity_unproven",
        "source_frame_artifact_unbound",
        "source_frame_region_outside",
        "source_frame_pixel_hash_mismatch",
        "motion_semantic_report_outdated",
        "child_validation_report_tampered",
        "evidence_ref_unbound",
        "human_visual_review_unproven",
        "human_decision_report_binding_invalid",
    }
    if expected != required:
        failed.append(str(fixture_path))
        print(f"[FAIL] fixture blocker coverage mismatch: {sorted(expected ^ required)}")
    else:
        passed += 1
        print(f"[PASS] adversarial fixture manifest: {len(fixture['cases'])}/{len(required)} blockers declared")
    physical_cases = [case for case in fixture["cases"] if case.get("package")]
    fixture_root = ROOT / "tools/sgdk_wrapper/ci/fixtures/animation_validation"
    physical_required = {"contracts/run_strip_contract.json", "sources/source.png", "sources/frame_0.png", "sources/frame_1.png", "lineart/run_lineart.png",
                         "reports/producer_record.json", "reports/lineart_approval.json",
                         "reports/strip_validation.json", "reports/motion_validation.json",
                         "reports/candidate_validation.json", "reports/human_decision.json",
                         "evidence/run_diagnostic.json", "evidence/run_human_decision.json",
                         "candidate_manifest.json"}
    for case in physical_cases:
        package = fixture_root / case["package"]
        missing = [rel for rel in physical_required if not (package / rel).is_file()]
        if missing:
            failed.append(str(package))
            print(f"[FAIL] physical fixture {case['id']}: missing {missing}")
            continue
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            commands = {
                "validate_animation_strip_artifact": [sys.executable, str(ROOT / TOOLS[1]), "--input", str(package / "contracts/run_strip_contract.json"), "--project-root", str(package), "--output", str(temp / "strip.json")],
                "validate_motion_semantics": [sys.executable, str(ROOT / TOOLS[2]), "--contract", str(package / "contracts/run_strip_contract.json"), "--project-root", str(package), "--output", str(temp / "motion.json")],
                "validate_animation_candidate": [sys.executable, str(ROOT / TOOLS[3]), "--manifest", str(package / "candidate_manifest.json"), "--project-root", str(package), "--output", str(temp / "candidate.json")],
            }
            baseline_package = fixture_root / "baseline_package"
            baseline_commands = {
                "validate_animation_strip_artifact": [sys.executable, str(ROOT / TOOLS[1]), "--input", str(baseline_package / "contracts/run_strip_contract.json"), "--project-root", str(baseline_package), "--output", str(temp / "baseline_strip.json")],
                "validate_motion_semantics": [sys.executable, str(ROOT / TOOLS[2]), "--contract", str(baseline_package / "contracts/run_strip_contract.json"), "--project-root", str(baseline_package), "--output", str(temp / "baseline_motion.json")],
                "validate_animation_candidate": [sys.executable, str(ROOT / TOOLS[3]), "--manifest", str(baseline_package / "candidate_manifest.json"), "--project-root", str(baseline_package), "--output", str(temp / "baseline_candidate.json")],
            }
            baseline_ok = True
            for name, command in baseline_commands.items():
                proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                baseline_ok = baseline_ok and proc.returncode == 0
            if not baseline_ok:
                failed.append(str(package))
                print(f"[FAIL] physical fixture {case['id']}: clean baseline rejected")
                continue
            target_name = case["validator"]
            proc = subprocess.run(commands[target_name], cwd=ROOT, capture_output=True, text=True)
            output_name = {"validate_animation_strip_artifact": "strip.json", "validate_motion_semantics": "motion.json", "validate_animation_candidate": "candidate.json"}[target_name]
            report = json.loads((temp / output_name).read_text(encoding="utf-8")) if (temp / output_name).is_file() else {}
            expected_blockers = set(case.get("allowed_blockers", [case["expected_blocker"]]))
            actual_blockers = set(report.get("blockers", []))
            claim_ceiling_ok = True
            if case["id"] == "physical_human_decision_invalid_bindings":
                claim_order = ["none", "technical_candidate", "motion_semantic_candidate", "human_review_candidate"]
                claim_ceiling_ok = report.get("maximum_proven_claim") in claim_order
            if proc.returncode != 1 or report.get("status") != "error" or actual_blockers != expected_blockers or not claim_ceiling_ok:
                failed.append(str(package))
                print(f"[FAIL] physical fixture {case['id']}: expected exactly {sorted(expected_blockers)}, rc={proc.returncode}, report={report}")
            else:
                passed += 1
                print(f"[PASS] physical fixture {case['id']}: baseline accepted; mutation rc={proc.returncode}; blocker={case['expected_blocker']}")
    total = len(TOOLS) + len(SCHEMAS) + 1 + len(physical_cases)
    print(f"animation validation: {passed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

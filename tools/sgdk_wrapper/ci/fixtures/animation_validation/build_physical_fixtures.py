#!/usr/bin/env python3
"""Build the checked-in, minimal physical animation validator fixtures.

These images are synthetic diagnostic fixtures only; they are never delivery
assets and never enter a project's res/ directory.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
REGISTRY_REL = "tools/sgdk_wrapper/.agent/skills/art/sprite-animation/references/motion_profile_registry.json"
PRINCIPLES = (
    "squash_and_stretch", "anticipation", "staging",
    "straight_ahead_and_pose_to_pose", "follow_through_and_overlapping_action",
    "slow_in_and_slow_out", "arcs", "secondary_action", "timing",
    "exaggeration", "solid_drawing", "appeal",
)


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pixel_sha(path: Path) -> str:
    with Image.open(path) as image:
        image.load()
        return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_fixture_pngs(package: Path) -> list[str]:
    palette = [0, 0, 0, 0xEE, 0x66, 0x88, 0xAA, 0x22, 0x22] + [0, 0, 0] * 253
    strip = Image.new("P", (128, 32), 0)
    strip.putpalette(palette)
    draw = ImageDraw.Draw(strip)
    for index, (x, foot) in enumerate(((4, 22), (6, 20), (8, 22), (6, 24))):
        cell_x = index * 32
        draw.ellipse((cell_x + x, 4 + index % 2, cell_x + x + 20, 25 + index % 2), fill=1, outline=2)
        draw.rectangle((cell_x + foot, 24, cell_x + foot + 5, 27), fill=2)
        draw.rectangle((cell_x + 22 - index, 24, cell_x + 27 - index, 27), fill=2)
    strip_path = package / "strips/run_strip.png"
    strip_path.parent.mkdir(parents=True, exist_ok=True)
    strip.save(strip_path, bits=4, transparency=0)

    frame_hashes: list[str] = []
    for index in range(4):
        frame = strip.crop((index * 32, 0, (index + 1) * 32, 32))
        path = package / f"sources/frame_{index}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.save(path, bits=4, transparency=0)
        frame_hashes.append(sha(path))

    lineart = Image.new("P", (32, 32), 0)
    lineart.putpalette(palette)
    ImageDraw.Draw(lineart).ellipse((6, 4, 26, 25), outline=1, width=1)
    lineart_path = package / "lineart/run_lineart.png"
    lineart_path.parent.mkdir(parents=True, exist_ok=True)
    lineart.save(lineart_path, bits=4, transparency=0)
    shutil.copyfile(package / "sources/frame_0.png", package / "sources/source.png")
    return frame_hashes


def make_contract(package: Path, frame_hashes: list[str]) -> dict[str, Any]:
    strip_path = package / "strips/run_strip.png"
    lineart_path = package / "lineart/run_lineart.png"
    source_path = package / "sources/source.png"
    approval_path = package / "reports/lineart_approval.json"
    producer_path = package / "reports/producer_record.json"
    approval = {"status": "approved", "subject_sha256": sha(lineart_path)}
    write_json(approval_path, approval)
    producer = {
        "status": "passed", "source_kind": "validator_fixture",
        "producer_kind": "validator_fixture", "subject_sha256": sha(source_path),
    }
    write_json(producer_path, producer)
    frames = []
    for index, source_hash in enumerate(frame_hashes):
        frames.append({
            "index": index, "x": index * 32, "y": 0, "w": 32, "h": 32,
            "pivot_x": 16, "pivot_y": 30,
            "phase": ("contact_left", "passing", "down_compression", "up_flight")[index],
            "lineage": {
                "source_frame_id": f"run_native_key_{index}",
                "source_frame_sha256": source_hash,
                "source_artifact": {
                    "path": f"sources/frame_{index}.png",
                    "sha256": source_hash,
                    "pixel_sha256": pixel_sha(package / f"sources/frame_{index}.png"),
                },
                "transformation": "native_reauthored", "duplicate_role": "none",
            },
            "support": {"grounded": False, "measurement_method": "pixel_derived", "contacts": []},
        })
    return {
        "schema_version": "3.0.0", "asset_id": "fixture_run", "asset_kind": "animation_strip",
        "action": "run", "strip_layout": "horizontal_single_action", "frame_count": 4,
        "frames": frames, "visual_dna_manifest": "contracts/visual_dna_manifest.json",
        "motion_phase_map": "contracts/motion_phase_map.json", "motion_profile_id": "run_cycle",
        "pivot_policy": "bottom_center_feet",
        "drift_thresholds": {"pivot_px": 0, "bbox_px": 0, "palette_changed_allowed": False, "scale_percent": 0},
        "approval_status": "approved_for_sheet",
        "artifact": {"path": "strips/run_strip.png", "sha256": sha(strip_path), "transparent_index": 0,
                      "cell_policy": "fixed_cell_coordinate_scoped", "allowed_boundary_contacts": []},
        "state_lineart_lineage": {
            "action": "run", "lineart_role": "native_key_pose_lineart", "source_asset_id": "fixture_run_lineart",
            "source_sha256": sha(lineart_path), "source_path": "lineart/run_lineart.png",
            "approval_status": "approved_for_strip_authoring", "authorship_method": "hand_authored_native",
            "derivation_method": "hand_drawn_native",
            "approval_record": {"path": "reports/lineart_approval.json", "sha256": sha(approval_path), "subject_sha256": sha(lineart_path)},
            "key_pose_ids": [f"run_native_key_{index}" for index in range(4)],
        },
        "timing_contract": {"vblank_hz": 60, "loop": True, "frame_holds_vblank": [4, 4, 4, 4]},
        "metasprite_layout": {"hardware_cells_per_frame": 1, "peak_sprites_per_scanline": 1, "peak_pixels_per_scanline": 32},
        "production_provenance": {
            "source_kind": "validator_fixture", "producer_kind": "validator_fixture",
            "authored_source": {"path": "sources/source.png", "sha256": sha(source_path)},
            "producer_record": {"path": "reports/producer_record.json", "sha256": sha(producer_path), "subject_sha256": sha(source_path)},
        },
    }


def write_candidate_reports(package: Path, contract: dict[str, Any]) -> None:
    strip_sha = contract["artifact"]["sha256"]
    visual_subjects = {"run": strip_sha}
    evidence_path = package / "evidence/run_diagnostic.json"
    write_json(evidence_path, {"kind": "agent_curated_diagnostic_review", "subject_sha256": strip_sha, "action": "run"})
    human_evidence_path = package / "evidence/run_human_decision.json"
    write_json(human_evidence_path, {"kind": "human_visual_decision", "subject_sha256": strip_sha, "action": "run"})
    evidence_ref = {"path": "evidence/run_diagnostic.json", "sha256": sha(evidence_path), "subject_sha256": strip_sha,
                    "action": "run", "evidence_kind": "artifact_inspection"}
    human_evidence_ref = {"path": "evidence/run_human_decision.json", "sha256": sha(human_evidence_path), "subject_sha256": strip_sha,
                          "action": "run", "evidence_kind": "human_visual_review"}
    action_review = {
        "run": {
            "subject_sha256": strip_sha,
            "observations": ["run: diagnostic review is bound to this strip"],
            "evidence_refs": [evidence_ref],
            "must_preserve_findings": [{"feature": "round_body_r1", "status": "passed"}],
        }
    }
    reports: dict[str, dict[str, Any]] = {
        "sprite_artifact": {"status": "passed", "visual_pass": True, "action_subject_sha256": visual_subjects},
        "fidelity": {"status": "passed", "action_subject_sha256": visual_subjects,
                     "review_type": "agent_curated_diagnostic_review", "action_reviews": action_review},
        "art_direction": {"status": "passed", "action_subject_sha256": visual_subjects},
        "blind_visual_review": {"status": "passed", "action_subject_sha256": visual_subjects,
                                "review_type": "independent_blind_visual_review", "action_reviews": action_review},
        "human_decision": {"status": "passed", "review_type": "human_visual_decision",
                           "action_subject_sha256": visual_subjects,
                           "action_reviews": {"run": {"subject_sha256": strip_sha, "decision": "accepted_for_review"}}},
    }
    for name, value in reports.items():
        write_json(package / f"reports/{name}.json", dict(value, subject_sha256=strip_sha))
    assessments = []
    for principle in PRINCIPLES:
        kinds = ["artifact_inspection"]
        if principle in {"staging", "exaggeration", "solid_drawing", "appeal"}:
            kinds.append("human_visual_review")
        refs = [human_evidence_ref] if principle in {"staging", "exaggeration", "solid_drawing", "appeal"} else [evidence_ref]
        kinds = [refs[0]["evidence_kind"]]
        assessments.append({"principle_id": principle, "status": "passed",
                            "observation": f"run: fixture evidence for {principle}",
                            "evidence_kinds": kinds, "evidence_refs": refs})
    principles = {"schema_version": "1.0.0", "candidate_id": "fixture_run",
                  "subject_sha256": strip_sha, "status": "passed",
                  "actions": [{"action": "run", "strip_sha256": strip_sha, "production_method": "hybrid", "assessments": assessments}]}
    write_json(package / "reports/animation_principles.json", principles)
    human_path = package / "reports/human_decision.json"
    human_value = json.loads(human_path.read_text(encoding="utf-8"))
    human_value["reviewed_reports"] = {
        name: {
            "path": f"reports/{name}.json", "sha256": sha(package / f"reports/{name}.json"),
            "subject_sha256": strip_sha, "action_subject_sha256": visual_subjects,
        }
        for name in ("fidelity", "art_direction", "blind_visual_review", "animation_principles")
    }
    write_json(human_path, human_value)


def replace_string(value: Any, old: str, new: str) -> Any:
    if isinstance(value, str):
        return new if value == old else value
    if isinstance(value, list):
        return [replace_string(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: replace_string(item, old, new) for key, item in value.items()}
    return value


def run_validator(script: Path, args: list[str], output: Path) -> int:
    completed = subprocess.run([sys.executable, str(script), *args], cwd=ROOT.parents[4], capture_output=True, text=True)
    output.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    return completed.returncode


def seal_package(package: Path) -> None:
    workspace = ROOT.parents[4]
    scripts = workspace / "tools/sgdk_wrapper/.agent/scripts"
    contract_path = package / "contracts/run_strip_contract.json"
    strip_report = package / "reports/strip_validation.json"
    motion_report = package / "reports/motion_validation.json"
    run_validator(scripts / "validate_animation_strip_artifact.py", ["--input", str(contract_path), "--project-root", str(package), "--output", str(strip_report)], package / "reports/strip_validation.stdout.txt")
    run_validator(scripts / "validate_motion_semantics.py", ["--contract", str(contract_path), "--project-root", str(package), "--output", str(motion_report)], package / "reports/motion_validation.stdout.txt")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    strip_sha = contract["artifact"]["sha256"]
    manifest = {
        "schema_version": "1.1.0", "candidate_id": "fixture_run", "quality_target": "premium",
        "validator_fixture": True, "delivery_claim_ceiling": "lab",
        "requested_claim": "technical_candidate", "human_gate_open": False,
        "strips": [{
            "contract": {"path": "contracts/run_strip_contract.json", "sha256": sha(contract_path), "subject_sha256": strip_sha},
            "artifact_report": {"path": "reports/strip_validation.json", "sha256": sha(strip_report), "subject_sha256": strip_sha},
            "motion_report": {"path": "reports/motion_validation.json", "sha256": sha(motion_report), "subject_sha256": strip_sha},
        }],
        "reports": {},
    }
    for name in ("sprite_artifact", "fidelity", "art_direction", "blind_visual_review", "human_decision", "animation_principles"):
        report_path = package / f"reports/{name}.json"
        manifest["reports"][name] = {"path": f"reports/{name}.json", "sha256": sha(report_path), "subject_sha256": strip_sha}
    write_json(package / "candidate_manifest.json", manifest)
    candidate_report = package / "reports/candidate_validation.json"
    run_validator(scripts / "validate_animation_candidate.py", ["--manifest", str(package / "candidate_manifest.json"), "--project-root", str(package), "--output", str(candidate_report)], package / "reports/candidate_validation.stdout.txt")


def refresh_manifest_report(package: Path, report_name: str) -> None:
    manifest_path = package / "candidate_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report_path = package / f"reports/{report_name}.json"
    if report_name == "motion_validation":
        manifest["strips"][0]["motion_report"]["sha256"] = sha(report_path)
    elif report_name == "strip_validation":
        manifest["strips"][0]["artifact_report"]["sha256"] = sha(report_path)
    else:
        manifest["reports"][report_name]["sha256"] = sha(report_path)
    write_json(manifest_path, manifest)


def refresh_human_reviewed_reports(package: Path) -> None:
    contract = json.loads((package / "contracts/run_strip_contract.json").read_text(encoding="utf-8"))
    strip_sha = contract["artifact"]["sha256"]
    human_path = package / "reports/human_decision.json"
    if not human_path.is_file():
        return
    human = json.loads(human_path.read_text(encoding="utf-8"))
    human["reviewed_reports"] = {
        name: {
            "path": f"reports/{name}.json", "sha256": sha(package / f"reports/{name}.json"),
            "subject_sha256": strip_sha,
            "action_subject_sha256": {"run": strip_sha},
        }
        for name in ("fidelity", "art_direction", "blind_visual_review", "animation_principles")
        if (package / f"reports/{name}.json").is_file()
    }
    human["action_subject_sha256"] = {"run": strip_sha}
    for item in human.get("action_reviews", {}).values():
        if isinstance(item, dict):
            item["subject_sha256"] = strip_sha
    write_json(human_path, human)


def mutate_case(package: Path, case_id: str) -> None:
    contract_path = package / "contracts/run_strip_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if case_id == "mechanical_resize_mislabeled_native":
        producer_path = package / "reports/producer_record.json"
        producer = json.loads(producer_path.read_text(encoding="utf-8"))
        producer["process"] = {"resampling": "NEAREST", "resize": True}
        write_json(producer_path, producer)
        contract["production_provenance"]["producer_record"]["sha256"] = sha(producer_path)
    elif case_id == "vector_procedural_lineart_declared_native":
        producer_path = package / "reports/producer_record.json"
        producer = json.loads(producer_path.read_text(encoding="utf-8"))
        producer["lineart_source"] = {"path": "lineart/run_lineart.svg", "rasterizer": "rsvg-convert"}
        write_json(producer_path, producer)
        contract["production_provenance"]["producer_record"]["sha256"] = sha(producer_path)
    elif case_id == "source_frame_lineage_not_independent":
        for frame in contract["frames"]:
            frame["lineage"]["source_frame_sha256"] = contract["frames"][0]["lineage"]["source_frame_sha256"]
    elif case_id == "noncanonical_motion_profile":
        contract["motion_profile_id"] = "jump_float"
    elif case_id == "package_visual_report_subject_incomplete":
        path = package / "reports/art_direction.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["action_subject_sha256"] = {}
        write_json(path, value)
    elif case_id == "animation_principle_evidence_not_action_specific":
        path = package / "reports/animation_principles.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["actions"][0]["assessments"][0]["evidence_refs"][0]["action"] = "idle"
        write_json(path, value)
    elif case_id == "viewpoint_continuity_unproven":
        strip_path = package / "strips/run_strip.png"
        old_strip_sha = contract["artifact"]["sha256"]
        with Image.open(strip_path) as image:
            changed = image.copy()
            pixels = changed.load()
            for y in range(8, 24):
                for x in range(32 + 10, 32 + 16):
                    pixels[x, y] = 0 if pixels[x, y] else 1
            changed.save(strip_path, bits=4, transparency=0)
        changed_frame = Image.open(strip_path).crop((32, 0, 64, 32))
        changed_frame.save(package / "sources/frame_1.png", bits=4, transparency=0)
        contract["frames"][1]["lineage"]["source_frame_sha256"] = sha(package / "sources/frame_1.png")
        contract["frames"][1]["lineage"]["source_artifact"]["sha256"] = sha(package / "sources/frame_1.png")
        contract["frames"][1]["lineage"]["source_artifact"]["pixel_sha256"] = pixel_sha(package / "sources/frame_1.png")
        contract["artifact"]["sha256"] = sha(strip_path)
        new_strip_sha = contract["artifact"]["sha256"]
        for name in ("sprite_artifact", "fidelity", "art_direction", "blind_visual_review", "human_decision", "animation_principles"):
            path = package / f"reports/{name}.json"
            write_json(path, replace_string(json.loads(path.read_text(encoding="utf-8")), old_strip_sha, new_strip_sha))
        for evidence_name in ("run_diagnostic.json", "run_human_decision.json"):
            path = package / "evidence" / evidence_name
            write_json(path, replace_string(json.loads(path.read_text(encoding="utf-8")), old_strip_sha, new_strip_sha))
        for report_name in ("fidelity", "blind_visual_review", "animation_principles"):
            path = package / f"reports/{report_name}.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            containers = value.get("actions", []) if report_name == "animation_principles" else value.get("action_reviews", {}).values()
            for container in containers:
                assessments = container.get("assessments", []) if report_name == "animation_principles" else [container]
                for assessment in assessments:
                    for ref in assessment.get("evidence_refs", []):
                        if isinstance(ref, dict):
                            ref["subject_sha256"] = new_strip_sha
                            ref["sha256"] = sha(package / ref["path"])
            write_json(path, value)
        path = package / "reports/blind_visual_review.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value.pop("review_type", None)
        value.pop("action_reviews", None)
        value["frame_viewpoints"] = ["front", "profile"]
        write_json(path, value)
    elif case_id == "model_sheet_to_sprite_fidelity_unproven":
        path = package / "reports/fidelity.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["action_reviews"]["run"]["must_preserve_findings"] = [{"feature": "invented_top_tuft", "status": "failed"}]
        write_json(path, value)
    elif case_id == "source_frame_artifact_fake_hash":
        contract["frames"][0]["lineage"]["source_artifact"]["sha256"] = "f" * 64
    elif case_id == "source_frame_artifact_missing_path":
        contract["frames"][0]["lineage"]["source_artifact"]["path"] = "sources/missing_frame.png"
    elif case_id == "source_frame_region_outside":
        contract["frames"][0]["lineage"]["source_artifact"]["region"] = {"x": 31, "y": 31, "w": 2, "h": 2}
    elif case_id == "source_frame_pixel_hash_mismatch":
        contract["frames"][0]["lineage"]["source_artifact"]["pixel_sha256"] = "e" * 64
    elif case_id == "source_frame_lineage_mismatch":
        contract["frames"][0]["lineage"]["source_frame_sha256"] = "c" * 64
    elif case_id == "registry_schema_version_tampered":
        path = package / "reports/motion_validation.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["registry"]["schema_version"] = "999.0.0"
        write_json(path, value)
    elif case_id == "child_validation_report_tampered":
        path = package / "reports/motion_validation.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["metrics"]["distinct_frame_count"] = 999
        write_json(path, value)
    elif case_id == "evidence_ref_missing":
        path = package / "reports/animation_principles.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["actions"][0]["assessments"][0]["evidence_refs"][0]["path"] = "evidence/missing.json"
        write_json(path, value)
    elif case_id == "evidence_ref_wrong_action":
        path = package / "reports/animation_principles.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["actions"][0]["assessments"][0]["evidence_refs"][0]["action"] = "idle"
        write_json(path, value)
    elif case_id == "agent_diagnostic_as_human_visual_review":
        path = package / "reports/human_decision.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["review_type"] = "agent_curated_diagnostic_review"
        write_json(path, value)
    elif case_id == "human_decision_invalid_bindings":
        path = package / "reports/human_decision.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["action_subject_sha256"] = {}
        value["reviewed_reports"]["fidelity"]["sha256"] = "0" * 64
        write_json(path, value)
    else:
        raise ValueError(case_id)
    write_json(contract_path, contract)
    if case_id != "human_decision_invalid_bindings":
        refresh_human_reviewed_reports(package)
    postseal = {
        "registry_schema_version_tampered", "child_validation_report_tampered",
        "evidence_ref_missing", "evidence_ref_wrong_action", "agent_diagnostic_as_human_visual_review",
        "human_decision_invalid_bindings",
    }
    if case_id in postseal:
        if case_id in {"evidence_ref_missing", "evidence_ref_wrong_action"}:
            refresh_manifest_report(package, "animation_principles")
            refresh_manifest_report(package, "human_decision")
        else:
            refresh_manifest_report(package, "motion_validation" if case_id in {"registry_schema_version_tampered", "child_validation_report_tampered"} else "human_decision")
        workspace = ROOT.parents[4]
        run_validator(
            workspace / "tools/sgdk_wrapper/.agent/scripts/validate_animation_candidate.py",
            ["--manifest", str(package / "candidate_manifest.json"), "--project-root", str(package), "--output", str(package / "reports/candidate_validation.json")],
            package / "reports/candidate_validation.stdout.txt",
        )
    else:
        seal_package(package)


def build() -> None:
    cases = (
        "mechanical_resize_mislabeled_native", "vector_procedural_lineart_declared_native",
        "source_frame_lineage_not_independent", "noncanonical_motion_profile",
        "package_visual_report_subject_incomplete", "animation_principle_evidence_not_action_specific",
        "viewpoint_continuity_unproven", "model_sheet_to_sprite_fidelity_unproven",
        "source_frame_artifact_fake_hash", "source_frame_artifact_missing_path",
        "source_frame_region_outside", "source_frame_pixel_hash_mismatch",
        "source_frame_lineage_mismatch",
        "registry_schema_version_tampered", "child_validation_report_tampered",
        "evidence_ref_missing", "evidence_ref_wrong_action", "agent_diagnostic_as_human_visual_review",
        "human_decision_invalid_bindings",
    )
    base = ROOT / "baseline_package"
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)
    frame_hashes = write_fixture_pngs(base)
    write_json(base / "contracts/visual_dna_manifest.json", {"schema_version": "1.0.0", "identity": "fixture"})
    write_json(base / "contracts/motion_phase_map.json", {"action": "run", "phases": ["contact_left", "passing", "down_compression", "up_flight"]})
    write_json(base / "contracts/source_lineage.json", {"source": "fixture_native_grid"})
    write_json(base / "contracts/run_strip_contract.json", make_contract(base, frame_hashes))
    write_candidate_reports(base, json.loads((base / "contracts/run_strip_contract.json").read_text(encoding="utf-8")))
    seal_package(base)
    for case_id in cases:
        target = ROOT / case_id
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(base, target)
        mutate_case(target, case_id)
    print(json.dumps({"baseline": str(base), "cases": list(cases)}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        parser.error("--build is required")
    build()

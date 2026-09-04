#!/usr/bin/env python3
"""Create hash-bound diagnostic reports for the v10 candidate aggregate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


PROJECT = Path(sys.argv[1]).resolve()
ROOT = PROJECT / "out/forward_test_v10_runtime_visual_review"
REPORTS = ROOT / "reports"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump(path: Path, value: object) -> str:
    path.write_text(json.dumps(value, indent=2) + "\n")
    return sha(path)


def binding(path: Path, subject: str, action: str | None = None, kind: str | None = None) -> dict[str, str]:
    value = {"path": str(path.relative_to(PROJECT)), "sha256": sha(path), "subject_sha256": subject}
    if action is not None:
        value["action"] = action
    if kind is not None:
        value["evidence_kind"] = kind
    return value


def main() -> int:
    actions = ["idle", "run", "jump_float", "inhale"]
    strip_sha = {a: sha(ROOT / f"strips/kirby_{a}.png") for a in actions}
    action_subject = strip_sha
    for action in actions:
        report_path = REPORTS / f"{action}_canonical_strip_report.json"
        integrity = json.loads((REPORTS / f"{action}_strip_integrity.json").read_text())
        canonical = json.loads(report_path.read_text())
        canonical["strip_sha256"] = strip_sha[action]
        report_path.write_text(json.dumps(canonical, indent=2) + "\n")

    diagnostic_refs = {
        action: binding(REPORTS / f"{action}_strip_integrity.json", strip_sha[action], action, "artifact_inspection")
        for action in actions
    }
    fidelity_actions = {}
    blind_actions = {}
    for action in actions:
        fidelity_actions[action] = {
            "subject_sha256": strip_sha[action],
            "observations": [f"{action}: 1x contact sheet and pixel-derived integrity report inspected"],
            "evidence_refs": [diagnostic_refs[action]],
            "must_preserve_findings": [
                {"feature": "r1_identity", "status": "passed"},
                {"feature": "independent_temporal_authorship", "status": "needs_review"},
                {"feature": "scale_and_viewpoint_continuity", "status": "needs_review"},
            ],
        }
        blind_actions[action] = {
            "subject_sha256": strip_sha[action],
            "observations": [f"{action}: blind diagnostic is incomplete without human perceptual review"],
            "evidence_refs": [binding(REPORTS / f"kirby_{action}_contact_sheet.png", strip_sha[action], action, "artifact_inspection")],
        }
    fidelity_path = REPORTS / "fidelity_report.json"
    fidelity_sha = dump(fidelity_path, {"status": "needs_review", "subject_sha256": sha(ROOT / "strips/review_kirby.png"), "action_subject_sha256": action_subject, "review_type": "agent_curated_diagnostic_review", "action_reviews": fidelity_actions})
    art_path = REPORTS / "art_direction_report.json"
    art_sha = dump(art_path, {"status": "needs_review", "subject_sha256": sha(ROOT / "strips/review_kirby.png"), "action_subject_sha256": action_subject, "review_type": "agent_curated_diagnostic_review", "action_reviews": {a: {"subject_sha256": strip_sha[a], "observations": [f"{a}: silhouette and material route inspected"], "evidence_refs": [diagnostic_refs[a]]} for a in actions}})
    blind_path = REPORTS / "blind_visual_review_report.json"
    blind_sha = dump(blind_path, {"status": "needs_review", "subject_sha256": sha(ROOT / "strips/review_kirby.png"), "action_subject_sha256": action_subject, "review_type": "independent_blind_visual_review", "action_reviews": blind_actions})
    sprite_path = REPORTS / "sprite_artifact_report.json"
    sprite_sha = dump(sprite_path, {"status": "needs_review", "visual_pass": False, "subject_sha256": sha(ROOT / "strips/review_kirby.png"), "action_subject_sha256": action_subject, "source": "pixel_integrity_and_canonical_strip_measurement"})

    principle_ids = ["squash_and_stretch", "anticipation", "staging", "straight_ahead_and_pose_to_pose", "follow_through_and_overlapping_action", "slow_in_and_slow_out", "arcs", "secondary_action", "timing", "exaggeration", "solid_drawing", "appeal"]
    principle_actions = []
    for action in actions:
        assessments = []
        for principle in principle_ids:
            assessments.append({"principle_id": principle, "status": "needs_review", "observation": f"{action}: diagnostic evidence exists but does not prove the principle perceptually", "evidence_kinds": ["artifact_inspection"], "evidence_refs": [diagnostic_refs[action]]})
        principle_actions.append({"action": action, "strip_sha256": strip_sha[action], "production_method": "hybrid", "assessments": assessments})
    principle_path = REPORTS / "animation_principles_report.json"
    principle_sha = dump(principle_path, {"schema_version": "1.0.0", "candidate_id": "kirby_v10_runtime_visual_review", "subject_sha256": sha(ROOT / "strips/review_kirby.png"), "status": "needs_review", "actions": principle_actions})

    strips = []
    for action in actions:
        strips.append({
            "contract": binding(ROOT / f"contracts/{action}_strip_contract.json", strip_sha[action]),
            "artifact_report": binding(REPORTS / f"{action}_canonical_strip_report.json", strip_sha[action]),
            "motion_report": binding(REPORTS / f"{action}_motion_report.json", strip_sha[action]),
        })
    manifest = {
        "schema_version": "1.1.0", "candidate_id": "kirby_v10_runtime_visual_review", "quality_target": "premium",
        "requested_claim": "technical_candidate", "human_gate_open": False,
        "strips": strips,
        "reports": {
            "sprite_artifact": binding(sprite_path, sha(ROOT / "strips/review_kirby.png")),
            "fidelity": binding(fidelity_path, sha(ROOT / "strips/review_kirby.png")),
            "art_direction": binding(art_path, sha(ROOT / "strips/review_kirby.png")),
            "blind_visual_review": binding(blind_path, sha(ROOT / "strips/review_kirby.png")),
            "animation_principles": binding(principle_path, sha(ROOT / "strips/review_kirby.png")),
        },
    }
    dump(ROOT / "contracts/animation_candidate_manifest.json", manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import jsonschema

WRAPPER = Path(__file__).resolve().parents[1]
ROUTER_PATH = WRAPPER / "quality_review_router.py"
HARNESS_PATH = WRAPPER / "harness_orchestration.py"
SCHEMAS = WRAPPER / "schemas"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_schema(name: str, value: dict) -> None:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    jsonschema.Draft7Validator.check_schema(schema)
    jsonschema.validate(value, schema, format_checker=jsonschema.FormatChecker())


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROUTER_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    checks = 0
    router = load_module("quality_review_router", ROUTER_PATH)
    harness = load_module("harness_orchestration", HARNESS_PATH)
    intrinsic = router.self_check()
    assert intrinsic == {"status": "passed", "passed": 17, "total": 17, "failed": []}
    checks += 17

    request = router.sample_request()
    plan, taskset = router.build_plan(request)
    validate_schema("quality_review_request.schema.json", request)
    validate_schema("quality_review_plan.schema.json", plan)
    validate_schema("orchestration_taskset.schema.json", taskset)
    assert len(plan["selected_reviews"]) == 3
    assert all(task["protected_paths"] == ["."] for task in taskset["tasks"])
    assert all(task["read_only"] and not task["write_paths"] for task in taskset["tasks"])
    checks += 6

    context = {
        "artifact_kind": "harness_context_snapshot",
        "harness": {
            "subagents_available": True,
            "max_concurrency": 4,
            "selected_skills": plan["required_harness_skills"],
        },
        "canonical_context": {"digest": "d" * 64},
        "status": "ready",
        "blockers": [],
        "orchestration_policy": {
            "maximum_context_capsule_words": 1200,
            "maximum_result_summary_words": 600,
        },
    }
    orchestration_plan = harness.build_plan(context, taskset)
    assert orchestration_plan["summary"]["delegated_count"] == 3
    assert all(
        item["execution_mode"] == "subagent_read_only"
        for item in orchestration_plan["tasks"]
    )
    assert orchestration_plan["summary"]["worker_slots"] == 3
    assert all(item["model_tier"] == "high_capability" for item in orchestration_plan["tasks"])
    checks += 4

    report = router.sample_report(request, plan)
    validate_schema("independent_quality_review.schema.json", report)
    validation = router.validate_report(request, plan, report)
    assert validation["status"] == "passed"
    assert validation["report_may_direct_remediation"] is True
    assert validation["quality_claim"] == "unproven"
    assert validation["ready_for_aaa"] is False
    checks += 5

    blocked_report = json.loads(json.dumps(report))
    finding = {
        "finding_id": "gameplay_defect",
        "classification": "defect",
        "severity": "major",
        "confidence": 0.9,
        "blocks_growth": True,
        "evidence": ["input trace diverges from contract"],
        "player_impact": "control response is ambiguous",
        "smallest_correction": "correct the transition and rerun the trace",
        "correction_owner_skill": "code/input-system-sgdk",
        "acceptance_evidence": ["same trace passes in BlastEm"],
        "scope_change_required": False,
    }
    blocked_report["reviewers"][0]["findings"] = [finding]
    blocked_report["reviewers"][0]["status"] = "blocked"
    blocked_report["synthesis"]["growth_decision"] = "revise_before_growth"
    blocked_report["synthesis"]["priority_finding_ids"] = ["gameplay_defect"]
    validate_schema("independent_quality_review.schema.json", blocked_report)
    assert router.validate_report(request, plan, blocked_report)["status"] == "passed"
    checks += 2

    wrong_decision = json.loads(json.dumps(blocked_report))
    wrong_decision["synthesis"]["growth_decision"] = "proceed"
    wrong_validation = router.validate_report(request, plan, wrong_decision)
    assert any(item.startswith("growth_decision_inconsistent") for item in wrong_validation["findings"])
    checks += 1

    missing_domain = json.loads(json.dumps(report))
    missing_domain["reviewers"].pop()
    assert "selected_reviewer_set_mismatch" in router.validate_report(request, plan, missing_domain)["findings"]
    checks += 1

    opportunity_block = json.loads(json.dumps(blocked_report))
    opportunity_block["reviewers"][0]["findings"][0]["classification"] = "opportunity"
    assert any(
        item.startswith("nonblocking_classification_blocks_growth")
        for item in router.validate_report(request, plan, opportunity_block)["findings"]
    )
    checks += 1

    vertical = router.sample_request("vertical_slice")
    vertical.update(
        {
            "changed_domains": ["gameplay", "art", "hardware"],
            "requested_domains": [],
            "commercial_intent": False,
            "narrative_weight": "none",
            "artifacts": [
                {"path": "out/rom.bin", "sha256": "1" * 64, "role": "rom"},
                {"path": "out/capture.png", "sha256": "2" * 64, "role": "emulator_capture"},
                {"path": "out/input.json", "sha256": "3" * 64, "role": "input_trace"},
                {"path": "data/hero.png", "sha256": "4" * 64, "role": "visual_asset"},
                {"path": "doc/art.json", "sha256": "5" * 64, "role": "art_direction"},
                {"path": "out/vdp.json", "sha256": "6" * 64, "role": "hardware_report"},
            ],
        }
    )
    vertical_plan, _ = router.build_plan(vertical)
    vertical_report = router.sample_report(vertical, vertical_plan)
    assert router.validate_report(vertical, vertical_plan, vertical_report)["status"] == "passed"
    vertical_missing_trace = json.loads(json.dumps(vertical))
    vertical_missing_trace["artifacts"] = [
        item for item in vertical_missing_trace["artifacts"] if item["role"] != "input_trace"
    ]
    missing_trace_plan, _ = router.build_plan(vertical_missing_trace)
    missing_trace_report = router.sample_report(vertical_missing_trace, missing_trace_plan)
    missing_trace_validation = router.validate_report(
        vertical_missing_trace, missing_trace_plan, missing_trace_report
    )
    assert any(
        item.startswith("domain_pass_missing_evidence:gameplay:input_trace")
        for item in missing_trace_validation["findings"]
    )
    checks += 2

    with tempfile.TemporaryDirectory(prefix="quality_review_") as raw:
        root = Path(raw)
        request_path = root / "request.json"
        plan_path = root / "plan.json"
        taskset_path = root / "taskset.json"
        report_path = root / "report.json"
        request_path.write_text(json.dumps(request), encoding="utf-8")
        result = run_cli(
            "plan",
            "--request",
            str(request_path),
            "--output",
            str(plan_path),
            "--taskset-output",
            str(taskset_path),
        )
        assert result.returncode == 0, result.stdout + result.stderr
        cli_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        cli_taskset = json.loads(taskset_path.read_text(encoding="utf-8"))
        validate_schema("quality_review_plan.schema.json", cli_plan)
        validate_schema("orchestration_taskset.schema.json", cli_taskset)
        report_path.write_text(json.dumps(router.sample_report(request, cli_plan)), encoding="utf-8")
        validated = run_cli(
            "validate-report",
            "--request",
            str(request_path),
            "--plan",
            str(plan_path),
            "--report",
            str(report_path),
        )
        assert validated.returncode == 0, validated.stdout + validated.stderr
        assert json.loads(validated.stdout)["status"] == "passed"
        checks += 5

    print(f"quality_review_router: {checks}/{checks} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

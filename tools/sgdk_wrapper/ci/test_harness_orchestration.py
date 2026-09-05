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
TOOL = WRAPPER / "harness_orchestration.py"
SCHEMAS = WRAPPER / "schemas"


def load_module():
    spec = importlib.util.spec_from_file_location("harness_orchestration", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_schema(name: str, data: dict) -> None:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    jsonschema.Draft7Validator.check_schema(schema)
    jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())


def base_task(task_id: str, kind: str, **overrides):
    value = {
        "task_id": task_id,
        "objective": f"Execute {task_id}",
        "task_kind": kind,
        "owner_skill": "operation/harness-orchestration",
        "dependencies": [],
        "read_only": True,
        "isolated_write": False,
        "write_paths": [],
        "protected_paths": ["res", "doc/10-memory-bank.md"],
        "input_artifacts": [],
        "output_paths": [],
        "expected_seconds": 90,
        "context_words": 500,
        "result_words": 200,
        "model_tier": "economical",
        "claim_ceiling": "documentado",
        "human_decision_required": False,
        "shared_capability_blocker": False,
        "acceptance_commands": [],
        "prohibitions": ["no promotion"],
    }
    value.update(overrides)
    return value


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    checks = 0
    module = load_module()
    intrinsic = module.self_check()
    assert intrinsic == {"status": "passed", "passed": 24, "total": 24, "failed": []}
    checks += 24

    with tempfile.TemporaryDirectory(prefix="harness_orchestration_") as raw:
        root = Path(raw)
        project = root / "SGDK_projects" / "fixture"
        (project / "doc").mkdir(parents=True)
        (project / "doc" / "10-memory-bank.md").write_text("fixture\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("fixture\n", encoding="utf-8")
        global_rules = root / "tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md"
        global_rules.parent.mkdir(parents=True)
        global_rules.write_text("fixture\n", encoding="utf-8")
        skill = root / "tools/sgdk_wrapper/.agent/skills/operation/harness-orchestration/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("fixture\n", encoding="utf-8")
        pipeline = root / "tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json"
        pipeline.parent.mkdir(parents=True)
        pipeline.write_text("{}\n", encoding="utf-8")
        context_path = root / "context.json"
        taskset_path = root / "taskset.json"
        plan_path = root / "plan.json"
        result_path = root / "result.json"

        probe = run_cli(
            "probe",
            "--workspace-root", str(root),
            "--project-root", str(project),
            "--objective", "fixture",
            "--surface", "codex_desktop",
            "--subagents", "available",
            "--max-concurrency", "4",
            "--supports-wait",
            "--supports-interrupt",
            "--permission-profile", "workspace_write",
            "--skill", "operation/harness-orchestration",
            "--pipeline", "aaa_scene_v1",
            "--output", str(context_path),
        )
        assert probe.returncode == 0, probe.stdout + probe.stderr
        context = json.loads(context_path.read_text(encoding="utf-8"))
        validate_schema("harness_context_snapshot.schema.json", context)
        assert context["orchestration_policy"]["default_worker_slots"] == 2
        assert any(item["sha256"] for item in context["canonical_context"]["sources"])
        assert context["harness"]["selected_skills"] == ["operation/harness-orchestration"]
        assert any(item["role"] == "selected_pipeline:aaa_scene_v1" for item in context["canonical_context"]["sources"])
        assert all('"' not in path for path in context["git"]["dirty_path_examples"])
        checks += 6

        tasks = [
            base_task("inventory", "inventory"),
            base_task("logs", "log_analysis"),
            base_task(
                "code",
                "implementation",
                dependencies=["inventory"],
                read_only=False,
                isolated_write=True,
                write_paths=["src/camera"],
                output_paths=["src/camera/camera.c"],
                expected_seconds=180,
                model_tier="balanced",
            ),
            base_task(
                "claim",
                "claim_decision",
                dependencies=["code", "logs"],
                expected_seconds=90,
                model_tier="high_capability",
            ),
        ]
        taskset = {
            "schema_version": "1.0.0",
            "artifact_kind": "orchestration_taskset",
            "run_id": "fixture-run",
            "tasks": tasks,
        }
        validate_schema("orchestration_taskset.schema.json", taskset)
        taskset_path.write_text(json.dumps(taskset), encoding="utf-8")
        plan_result = run_cli(
            "plan", "--context", str(context_path), "--taskset", str(taskset_path),
            "--output", str(plan_path),
        )
        assert plan_result.returncode == 0, plan_result.stdout + plan_result.stderr
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        validate_schema("orchestration_plan.schema.json", plan)
        modes = {task["task_id"]: task["execution_mode"] for task in plan["tasks"]}
        assert modes == {
            "inventory": "subagent_read_only",
            "logs": "subagent_read_only",
            "code": "subagent_isolated_writer",
            "claim": "coordinator_local",
        }
        assert plan["summary"]["worker_slots"] == 3
        assert plan["token_policy"]["full_history_fork_default"] is False
        planned_models = {task["task_id"]: task["model_tier"] for task in plan["tasks"]}
        assert planned_models["inventory"] == "economical"
        assert planned_models["claim"] == "high_capability"
        checks += 7

        result = {
            "schema_version": "1.0.0",
            "artifact_kind": "agent_task_result",
            "task_id": "inventory",
            "status": "passed",
            "context_digest": plan["context_digest"],
            "claim_ceiling": "documentado",
            "summary_words": 40,
            "raw_log_embedded": False,
            "files_read": [],
            "files_written": [],
            "commands": [],
            "evidence": [],
            "blockers_removed": [],
            "new_blockers": [],
            "next_causal_action": None,
            "usage": {
                "model": "fixture",
                "reasoning_effort": "low",
                "input_tokens": 100,
                "cached_input_tokens": 50,
                "output_tokens": 20,
                "tool_calls": 1,
                "elapsed_ms": 1000,
                "context_capsule_words": 100,
                "result_words": 40,
                "duplicate_files_read": 0,
                "validation_cache_hits": 0,
            },
        }
        validate_schema("agent_task_result.schema.json", result)
        result_path.write_text(json.dumps(result), encoding="utf-8")
        validation = run_cli("validate-result", "--plan", str(plan_path), "--result", str(result_path))
        assert validation.returncode == 0, validation.stdout + validation.stderr
        assert json.loads(validation.stdout)["result_may_be_integrated"] is True
        checks += 2

        metrics_path = root / "metrics.json"
        metrics_result = run_cli(
            "metrics", "--plan", str(plan_path), "--result", str(result_path),
            "--output", str(metrics_path),
        )
        assert metrics_result.returncode == 1, metrics_result.stdout + metrics_result.stderr
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        validate_schema("orchestration_metrics.schema.json", metrics)
        assert metrics["usage"]["observed_total_tokens"] == 120
        assert metrics["quality_claim"] == "unproven" and metrics["ready_for_aaa"] is False
        assert metrics["status"] == "needs_review"
        assert metrics["result_counts"]["missing_task_ids"] == ["claim", "code", "logs"]
        checks += 6

        bad_result = dict(result)
        bad_result["task_id"] = "code"
        bad_result["files_written"] = [{"path": "res/escape.png", "sha256": "b" * 64}]
        result_path.write_text(json.dumps(bad_result), encoding="utf-8")
        invalid = run_cli("validate-result", "--plan", str(plan_path), "--result", str(result_path))
        assert invalid.returncode == 1
        invalid_report = json.loads(invalid.stdout)
        assert "write_outside_lease:res/escape.png" in invalid_report["findings"]
        assert "protected_path_written:res/escape.png" in invalid_report["findings"]
        checks += 3

        unavailable_path = root / "unavailable.json"
        unavailable = run_cli(
            "probe", "--workspace-root", str(root), "--objective", "serial",
            "--subagents", "unavailable", "--max-concurrency", "4",
            "--skill", "operation/harness-orchestration",
            "--output", str(unavailable_path),
        )
        assert unavailable.returncode == 0
        unavailable_context = json.loads(unavailable_path.read_text(encoding="utf-8"))
        assert unavailable_context["harness"]["max_concurrency"] == 1
        checks += 1

        outside = run_cli(
            "probe", "--workspace-root", str(root), "--project-root", str(root.parent),
            "--objective", "escape", "--output", str(root / "escape.json"),
        )
        assert outside.returncode == 2
        assert "project_root_outside_workspace" in outside.stderr
        checks += 2

        missing = run_cli(
            "probe", "--workspace-root", str(root), "--objective", "missing skill",
            "--subagents", "available", "--max-concurrency", "2",
            "--skill", "operation/does-not-exist", "--output", str(root / "missing.json"),
        )
        assert missing.returncode == 1
        missing_context = json.loads((root / "missing.json").read_text(encoding="utf-8"))
        assert missing_context["status"] == "blocked"
        assert missing_context["blockers"] == [
            "selected_context_missing:tools/sgdk_wrapper/.agent/skills/operation/does-not-exist/SKILL.md"
        ]
        validate_schema("harness_context_snapshot.schema.json", missing_context)
        checks += 4

    print(f"harness_orchestration: {checks}/{checks} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

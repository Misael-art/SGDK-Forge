#!/usr/bin/env python3
"""Deterministic context resolver and conservative multi-agent planner.

This module does not spawn agents.  It decides whether delegation is useful,
builds a dependency-aware execution plan, and validates the compact result
envelope returned by a worker.  The caller (Codex, CLI, IDE, or another
harness) remains responsible for executing the plan.

The policy optimizes total work, not agent count: read-heavy independent work
may be delegated; claims, promotion, human decisions, short tasks, shared
capability blockers, and overlapping writes stay with the coordinator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

VERSION = "1.1.0"
SCHEMA_VERSION = "1.1.0"

TRUTH_FILES = (
    "doc/10-memory-bank.md",
    "doc/11-gdd.md",
    "doc/13-spec-cenas.md",
    "doc/00-diretrizes-agente.md",
    "doc/project_context_manifest.json",
    "doc/project_methodology_manifest.json",
    "doc/project_hygiene_manifest.json",
    "doc/active_iteration.json",
    ".mddev/project.json",
)

LOCAL_ONLY_KINDS = {
    "claim_decision",
    "promotion",
    "human_gate",
    "integration",
    "canonical_memory_update",
    "git_integration",
}

READ_HEAVY_KINDS = {
    "inventory",
    "documentation_audit",
    "log_analysis",
    "test_execution",
    "budget_analysis",
    "source_audit",
    "code_review",
    "visual_review",
}

VALID_TASK_KINDS = READ_HEAVY_KINDS | LOCAL_ONLY_KINDS | {
    "implementation",
    "asset_production",
    "runtime_production",
    "documentation_update",
    "external_dependency",
}

VALID_MODEL_TIERS = {"economical", "balanced", "high_capability"}
VALID_STATUSES = {"passed", "failed", "blocked", "stale", "needs_review"}

HIGH_CAPABILITY_OWNER_SKILLS = {
    "art/sprite-animation",
    "art/visual-excellence-standards",
    "design/gameplay-experience-reviewer",
    "planning/game-design-planning",
    "planning/narrative-design-reviewer",
    "planning/product-market-reviewer",
}


class ContractError(ValueError):
    """Raised when a context, taskset, plan, or result violates the contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid_json:{path}:{exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"json_root_not_object:{path}")
    return data


def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def resolve_project(workspace: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = workspace / candidate
    candidate = candidate.resolve()
    if not inside(workspace, candidate):
        raise ContractError("project_root_outside_workspace")
    if not candidate.is_dir():
        raise ContractError(f"project_root_missing:{candidate}")
    return candidate


def command_output(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_status_paths(workspace: Path, relative: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=normal", "--", relative],
            cwd=workspace,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    records = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    paths: list[str] = []
    index = 0
    while index < len(records):
        record = records[index]
        if not record:
            index += 1
            continue
        if len(record) >= 4:
            paths.append(record[3:])
            if record[:2].strip().startswith(("R", "C")) and index + 1 < len(records):
                index += 1  # Skip the second rename/copy path.
        index += 1
    return paths


def detect_git(workspace: Path, scope: Path | None) -> dict[str, Any]:
    branch = command_output(["git", "branch", "--show-current"], workspace)
    target = scope or workspace
    relative = "."
    if target != workspace:
        relative = target.relative_to(workspace).as_posix()
    paths = git_status_paths(workspace, relative)
    return {
        "branch": branch,
        "scope": relative,
        "dirty": bool(paths),
        "dirty_path_count": len(paths),
        "dirty_path_examples": paths[:20],
    }


def detect_tools() -> list[dict[str, Any]]:
    names = ("python3", "pwsh", "git", "magick", "gimp", "java", "wine", "blastem")
    return [
        {
            "name": name,
            "path": shutil.which(name),
            "state": "found" if shutil.which(name) else "not_found",
        }
        for name in names
    ]


def context_source(workspace: Path, path: Path, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "path": path.relative_to(workspace).as_posix(),
        "exists": path.is_file(),
        "sha256": sha256_file(path) if path.is_file() else None,
        "size_bytes": path.stat().st_size if path.is_file() else 0,
    }


def canonical_sources(
    workspace: Path,
    project: Path | None,
    skill_ids: list[str],
    pipeline_ids: list[str],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    result.append(context_source(workspace, workspace / "AGENTS.md", "workspace_instructions"))
    result.append(
        context_source(
            workspace,
            workspace / "tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md",
            "global_rules",
        )
    )
    if project is not None:
        for relative in TRUTH_FILES:
            result.append(context_source(workspace, project / relative, f"project_truth:{relative}"))
    for skill_id in skill_ids:
        if not re.fullmatch(r"[a-z0-9-]+/[a-z0-9-]+", skill_id):
            raise ContractError(f"invalid_skill_id:{skill_id}")
        path = workspace / "tools/sgdk_wrapper/.agent/skills" / skill_id / "SKILL.md"
        result.append(context_source(workspace, path, f"selected_skill:{skill_id}"))
    for pipeline_id in pipeline_ids:
        if not re.fullmatch(r"[a-z0-9_-]+", pipeline_id):
            raise ContractError(f"invalid_pipeline_id:{pipeline_id}")
        path = workspace / "tools/sgdk_wrapper/.agent/pipelines" / f"{pipeline_id}.json"
        result.append(context_source(workspace, path, f"selected_pipeline:{pipeline_id}"))
    return result


def build_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    workspace = Path(args.workspace_root).resolve()
    if not workspace.is_dir():
        raise ContractError(f"workspace_root_missing:{workspace}")
    project = resolve_project(workspace, args.project_root)
    subagents_available = args.subagents == "available"
    max_concurrency = args.max_concurrency if subagents_available else 1
    if max_concurrency < 1:
        raise ContractError("max_concurrency_must_be_positive")

    skill_ids = sorted(set(args.skill))
    pipeline_ids = sorted(set(args.pipeline))
    context_manifest = canonical_sources(workspace, project, skill_ids, pipeline_ids)
    context_hash_payload = "\n".join(
        f"{item['path']}={item['sha256']}" for item in context_manifest
    ).encode("utf-8")
    context_digest = hashlib.sha256(context_hash_payload).hexdigest()
    critical_roles = {"workspace_instructions", "global_rules"}
    blockers = [
        f"selected_context_missing:{item['path']}"
        for item in context_manifest
        if not item["exists"]
        and (
            item["role"] in critical_roles
            or item["role"].startswith("selected_skill:")
            or item["role"].startswith("selected_pipeline:")
        )
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "harness_context_snapshot",
        "tool": {"name": "harness_orchestration", "version": VERSION},
        "generated_at": utc_now(),
        "workspace_root": str(workspace),
        "project_root": str(project) if project else None,
        "objective": args.objective,
        "harness": {
            "surface": args.surface,
            "subagents_available": subagents_available,
            "max_concurrency": max_concurrency,
            "supports_wait": bool(args.supports_wait and subagents_available),
            "supports_interrupt": bool(args.supports_interrupt and subagents_available),
            "permission_profile": args.permission_profile,
            "selected_skills": skill_ids,
            "selected_pipelines": pipeline_ids,
        },
        "host": {
            "os": platform.system().lower(),
            "architecture": platform.machine(),
            "python": platform.python_version(),
            "execution_mode": "wsl" if os.environ.get("WSL_DISTRO_NAME") else "native",
        },
        "git": detect_git(workspace, project),
        "tools": detect_tools(),
        "canonical_context": {
            "sources": context_manifest,
            "digest": context_digest,
            "stale_state_policy": "reject_or_refresh",
        },
        "orchestration_policy": {
            "coordinator_is_single_claim_owner": True,
            "coordinator_is_single_promotion_owner": True,
            "default_worker_access": "read_only",
            "default_worker_slots": min(2, max(0, max_concurrency - 1)),
            "maximum_context_capsule_words": 1200,
            "maximum_result_summary_words": 600,
            "full_history_fork_default": False,
        },
        "status": "ready" if not blockers else "blocked",
        "blockers": blockers,
        "claim_ceiling": "orchestration_diagnostic_only",
    }


def build_frontier(args: argparse.Namespace) -> dict[str, Any]:
    workspace = Path(args.workspace_root).resolve()
    if not workspace.is_dir():
        raise ContractError(f"workspace_root_missing:{workspace}")
    project = resolve_project(workspace, args.project_root)
    if project is None:
        raise ContractError("project_root_required_for_frontier")
    blocked_nodes = sorted(set(args.blocked_node))
    independent_nodes = sorted(set(args.independent_node))
    if not blocked_nodes and not independent_nodes:
        raise ContractError("frontier_requires_at_least_one_node")
    overlap = sorted(set(blocked_nodes) & set(independent_nodes))
    if overlap:
        raise ContractError(f"frontier_node_both_blocked_and_independent:{','.join(overlap)}")
    if blocked_nodes and not args.dominant_blocker:
        raise ContractError("dominant_blocker_required_for_blocked_nodes")
    eligible_sources: list[dict[str, str]] = []
    for raw in args.eligible_source:
        normalized = normalize_scope(raw)
        path = (project / normalized).resolve()
        if not inside(project, path) or not path.is_file():
            raise ContractError(f"eligible_source_missing_or_external:{raw}")
        eligible_sources.append({"path": normalized, "sha256": sha256_file(path)})
    forbidden_sources = [
        {"path": normalize_scope(raw), "reason": "forbidden_by_active_frontier"}
        for raw in sorted(set(args.forbidden_source))
    ]
    forbidden_paths = {item["path"] for item in forbidden_sources}
    conflicting_sources = sorted(item["path"] for item in eligible_sources if item["path"] in forbidden_paths)
    if conflicting_sources:
        raise ContractError(f"frontier_source_both_eligible_and_forbidden:{','.join(conflicting_sources)}")
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "work_frontier_snapshot",
        "tool": {"name": "harness_orchestration", "version": VERSION},
        "generated_at": utc_now(),
        "project_root": project.relative_to(workspace).as_posix(),
        "active_epoch": args.active_epoch,
        "claim_ceiling": args.claim_ceiling,
        "dominant_blocker": args.dominant_blocker,
        "blocked_nodes": blocked_nodes,
        "independent_nodes": independent_nodes,
        "eligible_sources": eligible_sources,
        "forbidden_sources": forbidden_sources,
        "next_causal_action": args.next_causal_action,
        "status": "active" if independent_nodes else "fully_blocked",
    }


def validate_frontier(frontier: dict[str, Any]) -> None:
    required = {
        "schema_version", "artifact_kind", "tool", "generated_at", "project_root",
        "active_epoch", "claim_ceiling", "dominant_blocker", "blocked_nodes",
        "independent_nodes", "eligible_sources", "forbidden_sources",
        "next_causal_action", "status",
    }
    missing = sorted(required - set(frontier))
    if missing:
        raise ContractError(f"frontier_required_fields_missing:{','.join(missing)}")
    if frontier.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("invalid_frontier_schema_version")
    if frontier.get("artifact_kind") != "work_frontier_snapshot":
        raise ContractError("invalid_frontier_artifact_kind")
    blocked = frontier.get("blocked_nodes")
    independent = frontier.get("independent_nodes")
    if not isinstance(blocked, list) or not isinstance(independent, list):
        raise ContractError("frontier_nodes_missing")
    if len(blocked) != len(set(blocked)) or len(independent) != len(set(independent)):
        raise ContractError("frontier_duplicate_node")
    overlap = sorted(set(blocked) & set(independent))
    if overlap:
        raise ContractError(f"frontier_node_both_blocked_and_independent:{','.join(overlap)}")
    if blocked and not frontier.get("dominant_blocker"):
        raise ContractError("frontier_dominant_blocker_missing")
    if frontier.get("status") not in {"active", "fully_blocked"}:
        raise ContractError("invalid_frontier_status")
    expected_status = "active" if independent else "fully_blocked"
    if frontier.get("status") != expected_status:
        raise ContractError("frontier_status_does_not_match_nodes")
    if not blocked and not independent:
        raise ContractError("frontier_requires_at_least_one_node")
    if not isinstance(frontier.get("active_epoch"), str) or not frontier["active_epoch"]:
        raise ContractError("frontier_active_epoch_missing")
    if not isinstance(frontier.get("next_causal_action"), str) or not frontier["next_causal_action"]:
        raise ContractError("frontier_next_causal_action_missing")
    eligible = frontier.get("eligible_sources")
    forbidden = frontier.get("forbidden_sources")
    if not isinstance(eligible, list) or not isinstance(forbidden, list):
        raise ContractError("frontier_source_lists_missing")
    for item in eligible:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise ContractError("frontier_eligible_source_invalid")
        normalize_scope(item["path"])
        if not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            raise ContractError(f"frontier_eligible_source_hash_invalid:{item['path']}")
    for item in forbidden:
        if not isinstance(item, dict) or set(item) != {"path", "reason"}:
            raise ContractError("frontier_forbidden_source_invalid")
        normalize_scope(item["path"])
        if not isinstance(item["reason"], str) or not item["reason"]:
            raise ContractError(f"frontier_forbidden_source_reason_missing:{item['path']}")
    eligible_paths = {item["path"] for item in eligible}
    forbidden_paths = {item["path"] for item in forbidden}
    conflicts = sorted(eligible_paths & forbidden_paths)
    if conflicts:
        raise ContractError(f"frontier_source_both_eligible_and_forbidden:{','.join(conflicts)}")


def revalidate_frontier_sources(context: dict[str, Any], frontier: dict[str, Any]) -> None:
    workspace_raw = context.get("workspace_root")
    project_raw = context.get("project_root")
    if not isinstance(workspace_raw, str) or not isinstance(project_raw, str):
        raise ContractError("context_roots_missing_for_frontier")
    workspace = Path(workspace_raw).resolve()
    project = Path(project_raw).resolve()
    expected_relative = project.relative_to(workspace).as_posix()
    if frontier["project_root"] != expected_relative:
        raise ContractError("frontier_project_root_mismatch")
    for source in frontier["eligible_sources"]:
        path = (project / source["path"]).resolve()
        if not inside(project, path) or not path.is_file():
            raise ContractError(f"frontier_eligible_source_missing:{source['path']}")
        if sha256_file(path) != source["sha256"]:
            raise ContractError(f"frontier_eligible_source_stale:{source['path']}")


def blocked_task_ids(tasks: list[dict[str, Any]], frontier: dict[str, Any] | None) -> set[str]:
    if frontier is None:
        return set()
    validate_frontier(frontier)
    task_ids = {task["task_id"] for task in tasks}
    blocked = set(frontier["blocked_nodes"]) & task_ids
    changed = True
    while changed:
        changed = False
        for task in tasks:
            if task["task_id"] not in blocked and any(dep in blocked for dep in task["dependencies"]):
                blocked.add(task["task_id"])
                changed = True
    mislabeled = sorted(blocked & set(frontier["independent_nodes"]))
    if mislabeled:
        raise ContractError(f"independent_node_depends_on_blocked_node:{','.join(mislabeled)}")
    undeclared_runnable = sorted(task_ids - blocked - set(frontier["independent_nodes"]))
    if undeclared_runnable:
        raise ContractError(f"runnable_task_missing_from_work_frontier:{','.join(undeclared_runnable)}")
    return blocked


def validate_context(context: dict[str, Any]) -> None:
    if context.get("artifact_kind") != "harness_context_snapshot":
        raise ContractError("invalid_context_artifact_kind")
    harness = context.get("harness")
    if not isinstance(harness, dict):
        raise ContractError("context_harness_missing")
    if not isinstance(harness.get("max_concurrency"), int) or harness["max_concurrency"] < 1:
        raise ContractError("invalid_context_max_concurrency")
    canonical = context.get("canonical_context")
    if not isinstance(canonical, dict) or not canonical.get("digest"):
        raise ContractError("canonical_context_digest_missing")
    if context.get("status") != "ready" or context.get("blockers"):
        raise ContractError("harness_context_not_ready")


def validate_taskset(taskset: dict[str, Any]) -> list[dict[str, Any]]:
    if taskset.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("invalid_taskset_schema_version")
    if taskset.get("artifact_kind") != "orchestration_taskset":
        raise ContractError("invalid_taskset_artifact_kind")
    if not isinstance(taskset.get("run_id"), str) or not taskset["run_id"]:
        raise ContractError("taskset_run_id_missing")
    tasks = taskset.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ContractError("taskset_requires_tasks")
    ids: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ContractError("task_not_object")
        task_id = task.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise ContractError("task_id_missing")
        if task_id in ids:
            raise ContractError(f"duplicate_task_id:{task_id}")
        ids.add(task_id)
        if task.get("task_kind") not in VALID_TASK_KINDS:
            raise ContractError(f"invalid_task_kind:{task_id}")
        if task.get("model_tier") not in VALID_MODEL_TIERS:
            raise ContractError(f"invalid_model_tier:{task_id}")
        identity_scope = task.get("identity_scope")
        if identity_scope is not None and (not isinstance(identity_scope, str) or not identity_scope):
            raise ContractError(f"invalid_identity_scope:{task_id}")
        if task.get("task_kind") == "asset_production" and not identity_scope:
            raise ContractError(f"asset_production_identity_scope_required:{task_id}")
        for key in ("dependencies", "write_paths", "protected_paths", "input_artifacts", "output_paths"):
            if not isinstance(task.get(key), list):
                raise ContractError(f"task_list_missing:{task_id}:{key}")
        for key in ("write_paths", "protected_paths", "output_paths"):
            for path in task[key]:
                if not isinstance(path, str):
                    raise ContractError(f"task_path_not_string:{task_id}:{key}")
                normalize_scope(path)
        for artifact in task["input_artifacts"]:
            if not isinstance(artifact, dict):
                raise ContractError(f"input_artifact_not_object:{task_id}")
            artifact_path = artifact.get("path")
            artifact_sha = artifact.get("sha256")
            if not isinstance(artifact_path, str):
                raise ContractError(f"input_artifact_path_missing:{task_id}")
            normalize_scope(artifact_path)
            if not isinstance(artifact_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", artifact_sha):
                raise ContractError(f"input_artifact_sha256_invalid:{task_id}:{artifact_path}")
        for key in ("expected_seconds", "context_words", "result_words"):
            if not isinstance(task.get(key), int) or task[key] < 0:
                raise ContractError(f"task_integer_invalid:{task_id}:{key}")
        if task["context_words"] > 1200:
            # The task may still run locally, but its worker capsule is invalid.
            task.setdefault("planning_warnings", []).append("context_capsule_above_worker_limit")
        if task["result_words"] > 600:
            task.setdefault("planning_warnings", []).append("result_summary_above_worker_limit")
    for task in tasks:
        unknown = sorted(set(task["dependencies"]) - ids)
        if unknown:
            raise ContractError(f"unknown_dependencies:{task['task_id']}:{','.join(unknown)}")
    _topological_levels(tasks)  # cycle check
    return tasks


def normalize_scope(path: str) -> str:
    if not isinstance(path, str) or not path:
        raise ContractError("empty_or_non_string_scope")
    portable = path.replace("\\", "/")
    if portable.startswith("/") or re.match(r"^[A-Za-z]:", portable):
        raise ContractError(f"absolute_scope_forbidden:{path}")
    parts = PurePosixPath(portable).parts
    if ".." in parts:
        raise ContractError(f"path_traversal:{path}")
    normalized = "/".join(part for part in parts if part not in {"", "."})
    if not normalized:
        return "."
    return normalized


def scopes_overlap(left: str, right: str) -> bool:
    a = normalize_scope(left)
    b = normalize_scope(right)
    if a == "." or b == ".":
        return True
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def overlapping_writer_ids(tasks: list[dict[str, Any]]) -> set[str]:
    conflicts: set[str] = set()
    writers = [task for task in tasks if task["write_paths"]]
    for index, left in enumerate(writers):
        for right in writers[index + 1 :]:
            if any(scopes_overlap(a, b) for a in left["write_paths"] for b in right["write_paths"]):
                conflicts.update((left["task_id"], right["task_id"]))
    return conflicts


def decide_task(
    task: dict[str, Any], context: dict[str, Any], writer_conflicts: set[str]
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    harness = context["harness"]

    if task["task_kind"] in LOCAL_ONLY_KINDS:
        return "coordinator_local", ["single_authority_task"]
    if task.get("human_decision_required"):
        return "coordinator_local", ["human_decision_cannot_be_delegated"]
    if task.get("shared_capability_blocker"):
        return "coordinator_local", ["shared_capability_blocker_no_parallel_retry"]
    if task["task_kind"] == "external_dependency":
        return "coordinator_local", ["external_state_cannot_be_multiplied"]
    if not harness.get("subagents_available") or harness.get("max_concurrency", 1) < 2:
        return "coordinator_local", ["subagents_unavailable"]
    if task["context_words"] > context["orchestration_policy"]["maximum_context_capsule_words"]:
        return "coordinator_local", ["context_capsule_too_large_for_economic_delegation"]
    if task["result_words"] > context["orchestration_policy"]["maximum_result_summary_words"]:
        return "coordinator_local", ["result_envelope_too_large"]
    if task["expected_seconds"] < 60:
        return "coordinator_local", ["task_too_short_for_delegation_overhead"]

    if task.get("read_only") and not task["write_paths"]:
        if task["task_kind"] in READ_HEAVY_KINDS:
            reasons.extend(("independent_read_heavy_work", "protects_coordinator_context"))
            return "subagent_read_only", reasons
        return "coordinator_local", ["read_only_but_not_specialist_worthy"]

    if task["task_id"] in writer_conflicts:
        return "coordinator_local", ["overlapping_write_scope_requires_serial_owner"]
    if task.get("isolated_write") and task["write_paths"] and task["expected_seconds"] >= 120:
        return "subagent_isolated_writer", ["disjoint_write_lease", "long_bounded_production"]

    return "coordinator_local", ["write_task_not_safely_isolated"]


def recommended_model_tier(task_kind: str, owner_skill: str | None = None) -> str:
    if owner_skill in HIGH_CAPABILITY_OWNER_SKILLS:
        return "high_capability"
    if task_kind in {"inventory", "log_analysis", "test_execution", "source_audit"}:
        return "economical"
    if task_kind in {
        "documentation_audit", "budget_analysis", "code_review", "implementation",
        "runtime_production", "documentation_update",
    }:
        return "balanced"
    return "high_capability"


def _topological_levels(tasks: list[dict[str, Any]]) -> list[list[str]]:
    remaining = {task["task_id"]: set(task["dependencies"]) for task in tasks}
    levels: list[list[str]] = []
    completed: set[str] = set()
    while remaining:
        ready = sorted(task_id for task_id, deps in remaining.items() if deps <= completed)
        if not ready:
            raise ContractError("task_dependency_cycle")
        levels.append(ready)
        completed.update(ready)
        for task_id in ready:
            remaining.pop(task_id)
    return levels


def build_plan(
    context: dict[str, Any], taskset: dict[str, Any], frontier: dict[str, Any] | None = None
) -> dict[str, Any]:
    validate_context(context)
    tasks = validate_taskset(taskset)
    selected_skills = set(context["harness"].get("selected_skills", []))
    missing_owners = sorted({task["owner_skill"] for task in tasks} - selected_skills)
    if missing_owners:
        raise ContractError(f"owner_skill_not_in_context:{','.join(missing_owners)}")
    for task in tasks:
        if any(
            scopes_overlap(write_path, protected_path)
            for write_path in task["write_paths"]
            for protected_path in task["protected_paths"]
        ):
            raise ContractError(f"write_lease_overlaps_protected_path:{task['task_id']}")
    writer_conflicts = overlapping_writer_ids(tasks)
    if frontier is not None:
        validate_frontier(frontier)
        revalidate_frontier_sources(context, frontier)
    frontier_blocked = blocked_task_ids(tasks, frontier)
    frontier_digest = None
    if frontier is not None:
        frontier_digest = hashlib.sha256(
            json.dumps(frontier, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
    planned: list[dict[str, Any]] = []
    for task in tasks:
        if task["task_id"] in frontier_blocked:
            mode, reasons = "blocked_by_frontier", ["blocked_node_or_descendant"]
        else:
            mode, reasons = decide_task(task, context, writer_conflicts)
        selected_model_tier = recommended_model_tier(
            task["task_kind"], task["owner_skill"]
        )
        model_warnings = []
        if task["model_tier"] != selected_model_tier:
            model_warnings.append(
                f"requested_model_tier_overridden:{task['model_tier']}->{selected_model_tier}"
            )
        planned.append(
            {
                "task_id": task["task_id"],
                "objective": task["objective"],
                "task_kind": task["task_kind"],
                "owner_skill": task["owner_skill"],
                "identity_scope": task.get("identity_scope"),
                "dependencies": task["dependencies"],
                "execution_mode": mode,
                "decision_reasons": reasons,
                "requested_model_tier": task["model_tier"],
                "model_tier": selected_model_tier,
                "expected_seconds": task["expected_seconds"],
                "context_capsule": {
                    "inherit_full_history": False,
                    "maximum_words": task["context_words"],
                    "canonical_context_digest": context["canonical_context"]["digest"],
                    "work_frontier_digest": frontier_digest,
                    "input_artifacts": task["input_artifacts"],
                    "required_output_paths": task["output_paths"],
                    "claim_ceiling": task["claim_ceiling"],
                    "acceptance_commands": task.get("acceptance_commands", []),
                    "prohibitions": task.get("prohibitions", []),
                },
                "write_lease": {
                    "mode": "none" if not task["write_paths"] else "exclusive",
                    "paths": [normalize_scope(path) for path in task["write_paths"]],
                    "protected_paths": [normalize_scope(path) for path in task["protected_paths"]],
                },
                "result_contract": {
                    "maximum_summary_words": task["result_words"],
                    "raw_logs_must_be_files": True,
                    "hash_bindings_required": True,
                    "claim_ceiling": task["claim_ceiling"],
                },
                "planning_warnings": task.get("planning_warnings", []) + model_warnings,
            }
        )

    planned_by_id = {task["task_id"]: task for task in planned}
    worker_slots = max(0, min(3, context["harness"]["max_concurrency"] - 1))
    waves: list[dict[str, Any]] = []
    wave_number = 0
    for level in _topological_levels(tasks):
        delegated = [
            task_id
            for task_id in level
            if planned_by_id[task_id]["execution_mode"].startswith("subagent_")
        ]
        local = [
            task_id for task_id in level
            if task_id not in delegated
            and planned_by_id[task_id]["execution_mode"] != "blocked_by_frontier"
        ]
        remaining_delegated = list(delegated)
        while remaining_delegated:
            batch: list[str] = []
            used_identity_scopes: set[str] = set()
            for task_id in list(remaining_delegated):
                identity_scope = planned_by_id[task_id].get("identity_scope")
                if identity_scope and identity_scope in used_identity_scopes:
                    continue
                batch.append(task_id)
                if identity_scope:
                    used_identity_scopes.add(identity_scope)
                if len(batch) >= max(1, worker_slots):
                    break
            for task_id in batch:
                remaining_delegated.remove(task_id)
            wave_number += 1
            waves.append(
                {
                    "wave": wave_number,
                    "mode": "parallel_workers",
                    "task_ids": batch,
                }
            )
        for task_id in local:
            wave_number += 1
            waves.append({"wave": wave_number, "mode": "coordinator_serial", "task_ids": [task_id]})

    delegated_count = sum(task["execution_mode"].startswith("subagent_") for task in planned)
    expected_worker_words = sum(
        task["context_capsule"]["maximum_words"] + task["result_contract"]["maximum_summary_words"]
        for task in planned
        if task["execution_mode"].startswith("subagent_")
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "orchestration_plan",
        "tool": {"name": "harness_orchestration", "version": VERSION},
        "generated_at": utc_now(),
        "run_id": taskset["run_id"],
        "context_digest": context["canonical_context"]["digest"],
        "work_frontier_digest": frontier_digest,
        "coordinator_policy": {
            "single_claim_owner": True,
            "single_promotion_owner": True,
            "single_final_memory_owner": True,
            "worker_default_access": "read_only",
            "human_gate_may_block_only_dependent_branches": True,
        },
        "tasks": planned,
        "waves": waves,
        "summary": {
            "task_count": len(planned),
            "delegated_count": delegated_count,
            "coordinator_count": len(planned) - delegated_count - len(frontier_blocked),
            "blocked_count": len(frontier_blocked),
            "runnable_count": len(planned) - len(frontier_blocked),
            "identity_serial_groups": sorted({
                task["identity_scope"] for task in planned if task.get("identity_scope")
            }),
            "writer_conflict_task_ids": sorted(writer_conflicts),
            "worker_slots": worker_slots,
            "maximum_worker_context_and_result_words": expected_worker_words,
        },
        "token_policy": {
            "goal": "minimize_total_tokens_before_minimizing_wall_clock",
            "static_instructions_first": True,
            "dynamic_capsule_last": True,
            "full_history_fork_default": False,
            "raw_logs_in_coordinator_context": False,
            "validation_cache_key": "tool_sha256+tool_version+args+input_manifest_sha256+schema_sha256",
            "final_critical_validation_must_rerun": True,
        },
        "claim_ceiling": "orchestration_plan_only",
        "status": "ready",
    }


def task_from_plan(plan: dict[str, Any], task_id: str) -> dict[str, Any]:
    for task in plan.get("tasks", []):
        if task.get("task_id") == task_id:
            return task
    raise ContractError(f"result_task_not_in_plan:{task_id}")


def path_allowed(path: str, allowed: Iterable[str]) -> bool:
    normalized = normalize_scope(path)
    return any(scopes_overlap(normalized, scope) and (normalized == normalize_scope(scope) or normalized.startswith(normalize_scope(scope) + "/")) for scope in allowed)


def validate_result(plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    if plan.get("artifact_kind") != "orchestration_plan":
        raise ContractError("invalid_plan_artifact_kind")
    if result.get("artifact_kind") != "agent_task_result":
        raise ContractError("invalid_result_artifact_kind")
    task_id = result.get("task_id")
    task = task_from_plan(plan, task_id)
    findings: list[str] = []

    if task.get("execution_mode") == "blocked_by_frontier":
        findings.append("result_returned_for_blocked_frontier_node")

    if result.get("status") not in VALID_STATUSES:
        findings.append("invalid_result_status")
    if result.get("context_digest") != plan.get("context_digest"):
        findings.append("stale_context_digest")
    if result.get("work_frontier_digest") != plan.get("work_frontier_digest"):
        findings.append("stale_work_frontier_digest")
    if result.get("claim_ceiling") != task["result_contract"]["claim_ceiling"]:
        findings.append("worker_claim_ceiling_mismatch")
    if result.get("raw_log_embedded") is not False:
        findings.append("raw_log_embedded_in_result")
    if result.get("summary_words", 0) > task["result_contract"]["maximum_summary_words"]:
        findings.append("result_summary_budget_exceeded")
    usage = result.get("usage")
    if not isinstance(usage, dict):
        findings.append("result_usage_missing")
        usage = {}
    if usage.get("result_words") != result.get("summary_words"):
        findings.append("result_word_count_mismatch")
    if usage.get("context_capsule_words", 0) > task["context_capsule"]["maximum_words"]:
        findings.append("worker_context_budget_exceeded")
    files_read = result.get("files_read")
    if not isinstance(files_read, list):
        findings.append("files_read_missing")
        files_read = []
    read_by_path = {
        item.get("path"): item.get("sha256")
        for item in files_read
        if isinstance(item, dict) and item.get("path")
    }
    for expected in task["context_capsule"]["input_artifacts"]:
        if read_by_path.get(expected.get("path")) != expected.get("sha256"):
            findings.append(f"input_hash_binding_missing_or_stale:{expected.get('path')}")
    written = result.get("files_written")
    if not isinstance(written, list):
        findings.append("files_written_missing")
        written = []
    lease_paths = task["write_lease"]["paths"]
    for item in written:
        if not isinstance(item, dict) or not item.get("path") or not item.get("sha256"):
            findings.append("written_file_hash_binding_missing")
            continue
        if not lease_paths or not path_allowed(item["path"], lease_paths):
            findings.append(f"write_outside_lease:{item.get('path')}")
    protected = task["write_lease"]["protected_paths"]
    for item in written:
        if isinstance(item, dict) and item.get("path") and any(
            scopes_overlap(item["path"], scope) for scope in protected
        ):
            findings.append(f"protected_path_written:{item['path']}")
    if task["execution_mode"] == "subagent_read_only" and written:
        findings.append("read_only_worker_wrote_files")
    evidence = result.get("evidence")
    if not isinstance(evidence, list):
        findings.append("result_evidence_missing")

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "agent_task_result_validation",
        "task_id": task_id,
        "status": "passed" if not findings else "failed",
        "findings": sorted(set(findings)),
        "performance_warnings": (
            ["duplicate_context_reads_detected"]
            if isinstance(usage.get("duplicate_files_read"), int) and usage["duplicate_files_read"] > 0
            else []
        ),
        "result_may_be_integrated": not findings,
        "claim_ceiling": "orchestration_validation_only",
    }


def derive_metrics(plan: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    if plan.get("artifact_kind") != "orchestration_plan":
        raise ContractError("invalid_plan_artifact_kind")
    validations = [validate_result(plan, result) for result in results]
    usages = [result.get("usage", {}) for result in results]

    def total(field: str) -> int:
        return sum(value for usage in usages if isinstance((value := usage.get(field)), int))

    input_tokens = total("input_tokens")
    cached_tokens = total("cached_input_tokens")
    output_tokens = total("output_tokens")
    observed_tokens = input_tokens + output_tokens
    uncached_proxy = max(0, input_tokens - cached_tokens) + output_tokens
    removed = sorted(
        {
            blocker
            for result in results
            for blocker in result.get("blockers_removed", [])
            if isinstance(blocker, str)
        }
    )
    invalid = [item["task_id"] for item in validations if item["status"] != "passed"]
    task_ids = [result.get("task_id") for result in results]
    duplicate_results = sorted({task_id for task_id in task_ids if task_ids.count(task_id) > 1})
    expected = {task["task_id"] for task in plan.get("tasks", [])}
    observed = {task_id for task_id in task_ids if isinstance(task_id, str)}
    missing = sorted(expected - observed)

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "orchestration_metrics",
        "tool": {"name": "harness_orchestration", "version": VERSION},
        "generated_at": utc_now(),
        "run_id": plan.get("run_id"),
        "status": (
            "passed"
            if not invalid and not duplicate_results and not missing
            else "needs_review"
        ),
        "result_counts": {
            "expected": len(expected),
            "observed": len(results),
            "valid": len(results) - len(invalid),
            "invalid": len(invalid),
            "missing_task_ids": missing,
            "duplicate_task_ids": duplicate_results,
        },
        "usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_tokens,
            "output_tokens": output_tokens,
            "observed_total_tokens": observed_tokens,
            "uncached_token_proxy": uncached_proxy,
            "cache_fraction": round(cached_tokens / input_tokens, 4) if input_tokens else 0.0,
            "tool_calls": total("tool_calls"),
            "elapsed_sum_ms": total("elapsed_ms"),
            "elapsed_max_ms": max(
                (usage.get("elapsed_ms", 0) for usage in usages if isinstance(usage.get("elapsed_ms"), int)),
                default=0,
            ),
            "context_capsule_words": total("context_capsule_words"),
            "result_words": total("result_words"),
            "duplicate_files_read": total("duplicate_files_read"),
            "validation_cache_hits": total("validation_cache_hits"),
        },
        "causal_efficiency": {
            "blockers_removed": removed,
            "blockers_removed_count": len(removed),
            "blockers_removed_per_10000_observed_tokens": (
                round(len(removed) * 10000 / observed_tokens, 4) if observed_tokens else 0.0
            ),
        },
        "invalid_result_task_ids": invalid,
        "quality_claim": "unproven",
        "ready_for_aaa": False,
        "claim_ceiling": "process_metrics_only",
    }


def self_check() -> dict[str, Any]:
    context = {
        "artifact_kind": "harness_context_snapshot",
        "workspace_root": "/tmp/harness-fixture",
        "project_root": "/tmp/harness-fixture/SGDK_projects/fixture",
        "harness": {
            "subagents_available": True,
            "max_concurrency": 4,
            "selected_skills": ["operation/harness-orchestration"],
        },
        "canonical_context": {"digest": "a" * 64},
        "status": "ready",
        "blockers": [],
        "orchestration_policy": {
            "maximum_context_capsule_words": 1200,
            "maximum_result_summary_words": 600,
        },
    }

    def task(task_id: str, kind: str, **overrides: Any) -> dict[str, Any]:
        value: dict[str, Any] = {
            "task_id": task_id,
            "objective": task_id,
            "task_kind": kind,
            "owner_skill": "operation/harness-orchestration",
            "identity_scope": None,
            "dependencies": [],
            "read_only": True,
            "isolated_write": False,
            "write_paths": [],
            "protected_paths": ["res"],
            "input_artifacts": [],
            "output_paths": [],
            "expected_seconds": 90,
            "context_words": 500,
            "result_words": 200,
            "model_tier": "economical",
            "claim_ceiling": "documentado",
            "human_decision_required": False,
            "shared_capability_blocker": False,
        }
        value.update(overrides)
        return value

    checks: list[tuple[str, bool]] = []
    read = task("read", "inventory")
    mode, _ = decide_task(read, context, set())
    checks.append(("delegates_long_read_only", mode == "subagent_read_only"))
    checks.append(("routes_inventory_to_economical_model", recommended_model_tier("inventory") == "economical"))
    checks.append(("routes_visual_review_to_high_model", recommended_model_tier("visual_review") == "high_capability"))
    checks.append(("routes_narrative_owner_to_high_model", recommended_model_tier("documentation_audit", "planning/narrative-design-reviewer") == "high_capability"))

    short = task("short", "inventory", expected_seconds=20)
    mode, _ = decide_task(short, context, set())
    checks.append(("keeps_short_task_local", mode == "coordinator_local"))

    claim = task("claim", "claim_decision")
    mode, _ = decide_task(claim, context, set())
    checks.append(("keeps_claim_local", mode == "coordinator_local"))

    blocked = task("blocked", "asset_production", identity_scope="fighter_a", shared_capability_blocker=True)
    mode, _ = decide_task(blocked, context, set())
    checks.append(("does_not_multiply_shared_blocker", mode == "coordinator_local"))

    writer_a = task(
        "writer_a", "implementation", read_only=False, isolated_write=True,
        write_paths=["src/system"], expected_seconds=180,
    )
    writer_b = task(
        "writer_b", "implementation", read_only=False, isolated_write=True,
        write_paths=["src/system/audio"], expected_seconds=180,
    )
    conflicts = overlapping_writer_ids([writer_a, writer_b])
    mode, _ = decide_task(writer_a, context, conflicts)
    checks.append(("serializes_overlapping_writers", mode == "coordinator_local"))

    writer_c = task(
        "writer_c", "implementation", read_only=False, isolated_write=True,
        write_paths=["src/camera"], expected_seconds=180,
    )
    conflicts = overlapping_writer_ids([writer_a, writer_c])
    mode, _ = decide_task(writer_c, context, conflicts)
    checks.append(("delegates_disjoint_isolated_writer", mode == "subagent_isolated_writer"))

    no_agents = dict(context)
    no_agents["harness"] = {
        "subagents_available": False,
        "max_concurrency": 1,
        "selected_skills": ["operation/harness-orchestration"],
    }
    mode, _ = decide_task(read, no_agents, set())
    checks.append(("falls_back_to_serial", mode == "coordinator_local"))

    taskset = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "orchestration_taskset",
        "run_id": "fixture",
        "tasks": [read, task("audit", "documentation_audit", dependencies=["read"])],
    }
    plan = build_plan(context, taskset)
    checks.append(("builds_dependency_waves", len(plan["waves"]) == 2))
    checks.append(("never_inherits_full_history", all(not t["context_capsule"]["inherit_full_history"] for t in plan["tasks"])))

    result = {
        "artifact_kind": "agent_task_result",
        "task_id": "read",
        "status": "passed",
        "context_digest": "a" * 64,
        "work_frontier_digest": None,
        "claim_ceiling": "documentado",
        "summary_words": 20,
        "raw_log_embedded": False,
        "files_written": [],
        "files_read": [],
        "evidence": [],
        "usage": {
            "result_words": 20,
            "context_capsule_words": 20,
            "duplicate_files_read": 0,
        },
    }
    checks.append(("accepts_valid_result", validate_result(plan, result)["status"] == "passed"))
    stale = dict(result, context_digest="b" * 64)
    checks.append(("rejects_stale_result", "stale_context_digest" in validate_result(plan, stale)["findings"]))

    visual = task("visual", "asset_production", identity_scope="fighter_a", read_only=False, expected_seconds=180)
    animation = task("animation", "asset_production", identity_scope="fighter_a", dependencies=["visual"], read_only=False)
    budget = task("budget", "budget_analysis")
    frontier = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "work_frontier_snapshot",
        "tool": {"name": "harness_orchestration", "version": VERSION},
        "generated_at": "2026-01-01T00:00:00Z",
        "project_root": "SGDK_projects/fixture",
        "active_epoch": "fixture",
        "claim_ceiling": "technical_candidate",
        "dominant_blocker": "native_authoring_unavailable",
        "blocked_nodes": ["visual"],
        "independent_nodes": ["budget"],
        "eligible_sources": [],
        "forbidden_sources": [],
        "next_causal_action": "continue budget",
        "status": "active",
    }
    propagated = blocked_task_ids([visual, animation, budget], frontier)
    checks.append(("propagates_blocker_to_descendants", propagated == {"visual", "animation"}))
    try:
        blocked_task_ids(
            [visual, animation, budget],
            {**frontier, "independent_nodes": ["animation", "budget"]},
        )
        mislabeled_descendant_rejected = False
    except ContractError as exc:
        mislabeled_descendant_rejected = str(exc) == "independent_node_depends_on_blocked_node:animation"
    checks.append(("rejects_blocked_descendant_labeled_independent", mislabeled_descendant_rejected))
    try:
        validate_frontier({**frontier, "blocked_nodes": [], "independent_nodes": [], "status": "fully_blocked"})
        empty_frontier_rejected = False
    except ContractError as exc:
        empty_frontier_rejected = str(exc) == "frontier_requires_at_least_one_node"
    checks.append(("rejects_empty_frontier", empty_frontier_rejected))
    with tempfile.TemporaryDirectory(prefix="harness_frontier_self_check_") as raw:
        fixture_workspace = Path(raw)
        fixture_project = fixture_workspace / "SGDK_projects" / "fixture"
        fixture_project.mkdir(parents=True)
        frontier_context = dict(context)
        frontier_context["workspace_root"] = str(fixture_workspace)
        frontier_context["project_root"] = str(fixture_project)
        frontier_plan = build_plan(
            frontier_context,
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_kind": "orchestration_taskset",
                "run_id": "frontier",
                "tasks": [visual, animation, budget],
            },
            frontier,
        )
    checks.append((
        "runs_only_independent_frontier_nodes",
        frontier_plan["summary"]["blocked_count"] == 2
        and frontier_plan["summary"]["runnable_count"] == 1
        and [task_id for wave in frontier_plan["waves"] for task_id in wave["task_ids"]] == ["budget"],
    ))
    stale_frontier_result = dict(result, task_id="budget", work_frontier_digest="f" * 64)
    checks.append((
        "rejects_stale_work_frontier",
        "stale_work_frontier_digest" in validate_result(frontier_plan, stale_frontier_result)["findings"],
    ))

    pose_a = task(
        "pose_a", "asset_production", identity_scope="fighter_a", read_only=False,
        isolated_write=True, write_paths=["out/pose_a"], expected_seconds=180,
    )
    pose_b = task(
        "pose_b", "asset_production", identity_scope="fighter_a", read_only=False,
        isolated_write=True, write_paths=["out/pose_b"], expected_seconds=180,
    )
    identity_plan = build_plan(
        context,
        {
            "schema_version": SCHEMA_VERSION,
            "artifact_kind": "orchestration_taskset",
            "run_id": "identity-serialization",
            "tasks": [pose_a, pose_b],
        },
    )
    checks.append((
        "serializes_same_identity_asset_workers",
        all(len(wave["task_ids"]) == 1 for wave in identity_plan["waves"]),
    ))

    writer_plan = build_plan(
        context,
        {"schema_version": SCHEMA_VERSION, "artifact_kind": "orchestration_taskset", "run_id": "writer", "tasks": [writer_c]},
    )
    escaped = dict(result, task_id="writer_c", files_written=[{"path": "res/bad.png", "sha256": "c" * 64}])
    escaped["claim_ceiling"] = "documentado"
    validation = validate_result(writer_plan, escaped)
    checks.append(("rejects_write_outside_lease", any(item.startswith("write_outside_lease") for item in validation["findings"])))

    try:
        validate_taskset(
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_kind": "orchestration_taskset",
                "run_id": "cycle",
                "tasks": [
                    task("cycle_a", "inventory", dependencies=["cycle_b"]),
                    task("cycle_b", "inventory", dependencies=["cycle_a"]),
                ],
            }
        )
        cycle_rejected = False
    except ContractError as exc:
        cycle_rejected = str(exc) == "task_dependency_cycle"
    checks.append(("rejects_dependency_cycle", cycle_rejected))

    try:
        normalize_scope("/tmp/escape")
        absolute_scope_rejected = False
    except ContractError as exc:
        absolute_scope_rejected = str(exc).startswith("absolute_scope_forbidden:")
    checks.append(("rejects_absolute_scope", absolute_scope_rejected))

    try:
        normalize_scope(r"C:\\temp\\escape")
        windows_scope_rejected = False
    except ContractError as exc:
        windows_scope_rejected = str(exc).startswith("absolute_scope_forbidden:")
    checks.append(("rejects_windows_absolute_scope", windows_scope_rejected))

    try:
        normalize_scope(r"..\\res\\escape.png")
        backslash_traversal_rejected = False
    except ContractError as exc:
        backslash_traversal_rejected = str(exc).startswith("path_traversal:")
    checks.append(("rejects_backslash_traversal", backslash_traversal_rejected))

    protected_writer = task(
        "protected_writer",
        "implementation",
        read_only=False,
        isolated_write=True,
        write_paths=["res/generated"],
        protected_paths=["res"],
        expected_seconds=180,
    )
    try:
        build_plan(
            context,
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_kind": "orchestration_taskset",
                "run_id": "protected-writer",
                "tasks": [protected_writer],
            },
        )
        protected_overlap_rejected = False
    except ContractError as exc:
        protected_overlap_rejected = str(exc) == (
            "write_lease_overlaps_protected_path:protected_writer"
        )
    checks.append(("rejects_lease_over_protected_path", protected_overlap_rejected))

    metrics_result = dict(
        result,
        files_read=[],
        blockers_removed=["fixture_blocker"],
        usage={
            "input_tokens": 100,
            "cached_input_tokens": 40,
            "output_tokens": 20,
            "tool_calls": 2,
            "elapsed_ms": 500,
            "context_capsule_words": 20,
            "result_words": 20,
            "duplicate_files_read": 0,
            "validation_cache_hits": 1,
        },
    )
    metrics = derive_metrics(plan, [metrics_result])
    checks.append(("derives_token_metrics", metrics["usage"]["observed_total_tokens"] == 120))
    checks.append(("derives_causal_efficiency", metrics["causal_efficiency"]["blockers_removed_count"] == 1))
    checks.append(("metrics_never_promote_quality", metrics["quality_claim"] == "unproven" and metrics["ready_for_aaa"] is False))
    checks.append(("incomplete_metrics_need_review", metrics["status"] == "needs_review"))

    failed = [name for name, passed in checks if not passed]
    return {
        "status": "passed" if not failed else "failed",
        "passed": sum(passed for _, passed in checks),
        "total": len(checks),
        "failed": failed,
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    probe = sub.add_parser("probe", help="Resolve the current harness and project context.")
    probe.add_argument("--workspace-root", required=True)
    probe.add_argument("--project-root")
    probe.add_argument("--objective", required=True)
    probe.add_argument("--surface", choices=("codex_desktop", "codex_cli", "ide", "generic"), default="generic")
    probe.add_argument("--subagents", choices=("available", "unavailable"), default="unavailable")
    probe.add_argument("--max-concurrency", type=int, default=1)
    probe.add_argument("--supports-wait", action="store_true")
    probe.add_argument("--supports-interrupt", action="store_true")
    probe.add_argument("--permission-profile", choices=("read_only", "workspace_write", "unrestricted", "unknown"), default="unknown")
    probe.add_argument("--skill", action="append", default=[], help="Selected canonical skill id (category/name). Repeat as needed.")
    probe.add_argument("--pipeline", action="append", default=[], help="Selected pipeline id without .json. Repeat as needed.")
    probe.add_argument("--output", type=Path, required=True)

    frontier = sub.add_parser("frontier", help="Create a compact node-scoped work frontier snapshot.")
    frontier.add_argument("--workspace-root", required=True)
    frontier.add_argument("--project-root", required=True)
    frontier.add_argument("--active-epoch", required=True)
    frontier.add_argument("--claim-ceiling", required=True)
    frontier.add_argument("--dominant-blocker")
    frontier.add_argument("--blocked-node", action="append", default=[])
    frontier.add_argument("--independent-node", action="append", default=[])
    frontier.add_argument("--eligible-source", action="append", default=[])
    frontier.add_argument("--forbidden-source", action="append", default=[])
    frontier.add_argument("--next-causal-action", required=True)
    frontier.add_argument("--output", type=Path, required=True)

    plan = sub.add_parser("plan", help="Compile tasks into a conservative execution DAG.")
    plan.add_argument("--context", type=Path, required=True)
    plan.add_argument("--taskset", type=Path, required=True)
    plan.add_argument("--frontier", type=Path)
    plan.add_argument("--output", type=Path, required=True)

    validate = sub.add_parser("validate-result", help="Validate one worker result against its lease and context.")
    validate.add_argument("--plan", type=Path, required=True)
    validate.add_argument("--result", type=Path, required=True)
    validate.add_argument("--output", type=Path)

    metrics = sub.add_parser("metrics", help="Aggregate token, cache, latency, and causal-efficiency telemetry.")
    metrics.add_argument("--plan", type=Path, required=True)
    metrics.add_argument("--result", type=Path, action="append", required=True)
    metrics.add_argument("--output", type=Path, required=True)

    sub.add_parser("self-check", help="Run permanent adversarial routing fixtures.")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "probe":
            output = build_snapshot(args)
            atomic_write_json(args.output, output)
        elif args.command == "frontier":
            output = build_frontier(args)
            atomic_write_json(args.output, output)
        elif args.command == "plan":
            output = build_plan(
                load_json(args.context),
                load_json(args.taskset),
                load_json(args.frontier) if args.frontier else None,
            )
            atomic_write_json(args.output, output)
        elif args.command == "validate-result":
            output = validate_result(load_json(args.plan), load_json(args.result))
            if args.output:
                atomic_write_json(args.output, output)
        elif args.command == "metrics":
            output = derive_metrics(load_json(args.plan), [load_json(path) for path in args.result])
            atomic_write_json(args.output, output)
        else:
            output = self_check()
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0 if output.get("status") in {"ready", "passed", "active", "fully_blocked"} else 1
    except ContractError as exc:
        print(json.dumps({"status": "error", "blockers": [str(exc)]}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

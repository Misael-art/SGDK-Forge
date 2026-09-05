#!/usr/bin/env python3
"""Plan and validate proportional independent quality reviews for SGDK work."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
MAX_DOMAINS = 3
MARKET_MAX_AGE_DAYS = 90

PROJECT_CONTEXTS = {"aaa_game", "technical_demo", "exercise", "game_review", "consulting"}

DOMAINS = (
    "game_design",
    "gameplay",
    "mechanics",
    "level_design",
    "narrative",
    "market",
    "art",
    "animation",
    "audio",
    "code",
    "hardware",
    "governance",
)

OWNERS = {
    "game_design": "planning/game-design-planning",
    "gameplay": "design/gameplay-experience-reviewer",
    "mechanics": "design/systems-mechanics-validator",
    "level_design": "design/level-design-canonical",
    "narrative": "planning/narrative-design-reviewer",
    "market": "planning/product-market-reviewer",
    "art": "art/visual-excellence-standards",
    "animation": "art/sprite-animation",
    "audio": "code/xgm2-audio-director",
    "code": "code/sgdk-code-reviewer",
    "hardware": "hardware/megadrive-vdp-budget-analyst",
    "governance": "governance/aaa-pipeline-guardian",
}

STAGE_PRIORITIES = {
    "foundation": {"game_design": 45, "narrative": 30, "market": 25},
    "pre_growth": {"mechanics": 45, "level_design": 40, "gameplay": 35, "audio": 20},
    "vertical_slice": {"gameplay": 50, "art": 40, "animation": 35, "audio": 30, "hardware": 25},
    "release_candidate": {"governance": 50, "gameplay": 40, "code": 35, "hardware": 35, "audio": 25, "market": 20},
}

STAGE_DEFAULTS = {
    "foundation": ("game_design",),
    "pre_growth": ("mechanics", "level_design", "gameplay"),
    "vertical_slice": ("gameplay", "art", "hardware"),
    "release_candidate": ("governance", "gameplay", "hardware"),
}

RISK_DOMAINS = {
    "scope_growth": ("game_design", "governance"),
    "identity_drift": ("art", "game_design"),
    "gameplay_unproven": ("gameplay",),
    "level_rhythm": ("level_design", "gameplay"),
    "narrative_drift": ("narrative", "game_design"),
    "commercial_release": ("market", "governance"),
    "audio_masking": ("audio", "gameplay"),
    "art_regression": ("art",),
    "animation_semantics": ("animation", "gameplay"),
    "runtime_risk": ("code", "hardware"),
    "hardware_pressure": ("hardware",),
    "claim_risk": ("governance",),
}

RISK_FLAGS = set(RISK_DOMAINS)

ARTIFACT_ROLES = {
    "design_doc",
    "gdd",
    "script",
    "level_blueprint",
    "mechanic_report",
    "rom",
    "emulator_capture",
    "input_trace",
    "visual_asset",
    "art_direction",
    "audio_capture",
    "audio_contract",
    "market_source_pack",
    "code_diff",
    "hardware_report",
    "other",
}

EVIDENCE_REQUIREMENTS = {
    "game_design": ("gdd_or_design_doc", "project_promise", "scope"),
    "gameplay": ("rom", "emulator_capture", "input_trace"),
    "mechanics": ("mechanic_report", "gdd_or_design_doc"),
    "level_design": ("level_blueprint", "mechanic_report"),
    "narrative": ("gdd", "script_when_substantial", "level_or_scene_context"),
    "market": ("commercial_intent", "two_current_external_sources", "region_and_audience"),
    "art": ("visual_asset", "art_direction"),
    "animation": ("visual_asset_or_strip", "motion_contract", "timing_evidence"),
    "audio": ("audio_contract", "audio_capture_when_runtime_or_critical"),
    "code": ("code_diff", "build_or_validation_report"),
    "hardware": ("hardware_report", "rom_when_runtime_claimed"),
    "governance": ("claim_matrix", "fresh_hash_bound_evidence"),
}

MODEL_TIERS = {
    "game_design": "high_capability",
    "gameplay": "high_capability",
    "mechanics": "balanced",
    "level_design": "balanced",
    "narrative": "high_capability",
    "market": "high_capability",
    "art": "high_capability",
    "animation": "high_capability",
    "audio": "balanced",
    "code": "balanced",
    "hardware": "balanced",
    "governance": "balanced",
}

TASK_KINDS = {
    "game_design": "documentation_audit",
    "gameplay": "visual_review",
    "mechanics": "documentation_audit",
    "level_design": "documentation_audit",
    "narrative": "documentation_audit",
    "market": "source_audit",
    "art": "visual_review",
    "animation": "visual_review",
    "audio": "documentation_audit",
    "code": "code_review",
    "hardware": "budget_analysis",
    "governance": "documentation_audit",
}


class ContractError(ValueError):
    """Raised when a request or report violates the quality-review contract."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"invalid_json:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"json_root_not_object:{path}")
    return value


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalize_relative_path(raw: str) -> str:
    if not isinstance(raw, str) or not raw:
        raise ContractError("empty_or_non_string_path")
    portable = raw.replace("\\", "/")
    if portable.startswith("/") or re.match(r"^[A-Za-z]:", portable):
        raise ContractError(f"absolute_path_forbidden:{raw}")
    parts = PurePosixPath(portable).parts
    if ".." in parts:
        raise ContractError(f"path_traversal:{raw}")
    normalized = "/".join(part for part in parts if part not in {"", "."})
    return normalized or "."


def validate_request(request: dict[str, Any]) -> None:
    if request.get("schema_version") != SCHEMA_VERSION:
        raise ContractError("invalid_request_schema_version")
    if request.get("artifact_kind") != "quality_review_request":
        raise ContractError("invalid_request_artifact_kind")
    if request.get("review_stage") not in STAGE_PRIORITIES:
        raise ContractError("invalid_review_stage")
    if not isinstance(request.get("review_id"), str) or not re.fullmatch(
        r"[a-z0-9][a-z0-9_-]{2,63}", request["review_id"]
    ):
        raise ContractError("review_id_missing")
    if request.get("project_context") not in PROJECT_CONTEXTS:
        raise ContractError("invalid_project_context")
    if not isinstance(request.get("current_claim_ceiling"), str) or not request[
        "current_claim_ceiling"
    ]:
        raise ContractError("current_claim_ceiling_missing")
    try:
        date.fromisoformat(request.get("as_of", ""))
    except ValueError as exc:
        raise ContractError("invalid_review_as_of") from exc
    normalize_relative_path(request.get("project_root", ""))
    for key in ("changed_domains", "risk_flags", "requested_domains", "artifacts", "producer_ids"):
        if not isinstance(request.get(key), list):
            raise ContractError(f"request_list_missing:{key}")
    if not request["changed_domains"]:
        raise ContractError("changed_domains_empty")
    if len(set(request["changed_domains"])) != len(request["changed_domains"]):
        raise ContractError("duplicate_changed_domain")
    if len(set(request["risk_flags"])) != len(request["risk_flags"]):
        raise ContractError("duplicate_risk_flag")
    unknown_risks = sorted(set(request["risk_flags"]) - RISK_FLAGS)
    if unknown_risks:
        raise ContractError(f"unknown_risk_flag:{','.join(unknown_risks)}")
    if len(request["requested_domains"]) > MAX_DOMAINS:
        raise ContractError("too_many_requested_domains")
    for domain in request["changed_domains"] + request["requested_domains"]:
        if domain not in DOMAINS:
            raise ContractError(f"unknown_review_domain:{domain}")
    if len(set(request["requested_domains"])) != len(request["requested_domains"]):
        raise ContractError("duplicate_requested_domain")
    if not request["artifacts"]:
        raise ContractError("review_artifacts_empty")
    artifact_paths: set[str] = set()
    for artifact in request["artifacts"]:
        if not isinstance(artifact, dict):
            raise ContractError("artifact_not_object")
        path = normalize_relative_path(artifact.get("path", ""))
        if path in artifact_paths:
            raise ContractError(f"duplicate_artifact_path:{path}")
        artifact_paths.add(path)
        if not re.fullmatch(r"[0-9a-f]{64}", str(artifact.get("sha256", ""))):
            raise ContractError(f"invalid_artifact_sha256:{path}")
        if artifact.get("role") not in ARTIFACT_ROLES:
            raise ContractError(f"artifact_role_missing:{path}")
    if (
        not request["producer_ids"]
        or any(not isinstance(item, str) or not item for item in request["producer_ids"])
        or len(set(request["producer_ids"])) != len(request["producer_ids"])
    ):
        raise ContractError("producer_ids_invalid")
    if request.get("narrative_weight") not in {"none", "light", "substantial"}:
        raise ContractError("invalid_narrative_weight")
    if request.get("audio_weight") not in {"none", "supporting", "critical"}:
        raise ContractError("invalid_audio_weight")
    if not isinstance(request.get("commercial_intent"), bool):
        raise ContractError("commercial_intent_missing")


def domain_applicable(domain: str, request: dict[str, Any]) -> bool:
    explicit = domain in request["requested_domains"] or domain in request["changed_domains"]
    if domain == "market":
        return bool(
            request["commercial_intent"]
            or domain in request["requested_domains"]
            or "commercial_release" in request["risk_flags"]
        )
    if domain == "narrative":
        return explicit or request["narrative_weight"] != "none" or "narrative_drift" in request["risk_flags"]
    if domain == "audio":
        return explicit or request["audio_weight"] != "none" or "audio_masking" in request["risk_flags"]
    return True


def score_domain(domain: str, request: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    if domain in request["requested_domains"]:
        score += 100
        reasons.append("explicitly_requested")
    if domain in request["changed_domains"]:
        score += 60
        reasons.append("changed_domain")
    stage_score = STAGE_PRIORITIES[request["review_stage"]].get(domain, 0)
    if stage_score:
        score += stage_score
        reasons.append(f"stage_priority:{request['review_stage']}")
    if domain in STAGE_DEFAULTS[request["review_stage"]]:
        score += 35
        reasons.append("checkpoint_default")
    for risk in request["risk_flags"]:
        if domain in RISK_DOMAINS.get(risk, ()):
            score += 70
            reasons.append(f"risk:{risk}")
    return score, reasons


def make_taskset(request: dict[str, Any], reviews: list[dict[str, Any]]) -> dict[str, Any]:
    tasks = []
    for review in reviews:
        domain = review["domain"]
        tasks.append(
            {
                "task_id": f"review_{domain}",
                "objective": f"Independently review {domain} for {request['review_id']}",
                "task_kind": TASK_KINDS[domain],
                "owner_skill": review["owner_skill"],
                "dependencies": [],
                "read_only": True,
                "isolated_write": False,
                "write_paths": [],
                "protected_paths": ["."],
                "input_artifacts": [
                    {
                        "path": normalize_relative_path(item["path"]),
                        "sha256": item["sha256"],
                    }
                    for item in request["artifacts"]
                ],
                "output_paths": [],
                "expected_seconds": 120,
                "context_words": 900,
                "result_words": 350,
                "model_tier": review["model_tier"],
                "claim_ceiling": "independent_quality_review_only",
                "human_decision_required": False,
                "shared_capability_blocker": False,
                "acceptance_commands": [
                    "python3 tools/sgdk_wrapper/quality_review_router.py validate-report"
                ],
                "prohibitions": [
                    "no writes",
                    "no self approval",
                    "no scope expansion",
                    "no claim promotion",
                    "no taste-only blocker",
                ],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "orchestration_taskset",
        "run_id": f"quality-{request['review_id']}",
        "tasks": tasks,
    }


def build_plan(request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_request(request)
    candidates: list[dict[str, Any]] = []
    considered = set(request["changed_domains"]) | set(request["requested_domains"])
    considered.update(STAGE_PRIORITIES[request["review_stage"]])
    for risk in request["risk_flags"]:
        considered.update(RISK_DOMAINS.get(risk, ()))
    for domain in DOMAINS:
        if domain not in considered or not domain_applicable(domain, request):
            continue
        score, reasons = score_domain(domain, request)
        if score <= 0:
            continue
        candidates.append(
            {
                "domain": domain,
                "owner_skill": OWNERS[domain],
                "score": score,
                "selection_reasons": reasons,
                "model_tier": MODEL_TIERS[domain],
                "evidence_requirements": list(EVIDENCE_REQUIREMENTS[domain]),
            }
        )
    candidates.sort(key=lambda item: (-item["score"], DOMAINS.index(item["domain"])))
    by_domain = {item["domain"]: item for item in candidates}
    selected = [
        by_domain[domain]
        for domain in request["requested_domains"]
        if domain in by_domain
    ]
    selected_domains = {item["domain"] for item in selected}
    selected.extend(
        item
        for item in candidates
        if item["domain"] not in selected_domains
    )
    selected = selected[:MAX_DOMAINS]
    selected_domains = {item["domain"] for item in selected}
    deferred = [
        {"domain": item["domain"], "reason": "capacity_limit_review_next_delta"}
        for item in candidates
        if item["domain"] not in selected_domains
    ]
    blockers = [] if selected else ["no_applicable_review_domain"]
    request_digest = canonical_digest(request)
    digest_payload = {
        "request_digest": request_digest,
        "review_id": request["review_id"],
        "review_stage": request["review_stage"],
        "selected_reviews": selected,
        "deferred_domains": deferred,
    }
    plan_digest = canonical_digest(digest_payload)
    required_skills = sorted(
        {
            "governance/independent-quality-review",
            "operation/harness-orchestration",
            *(item["owner_skill"] for item in selected),
        }
    )
    plan = {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "quality_review_plan",
        "tool": {"name": "quality_review_router", "version": VERSION},
        "generated_at": utc_now(),
        "review_id": request["review_id"],
        "request_digest": request_digest,
        "plan_digest": plan_digest,
        "review_stage": request["review_stage"],
        "selected_reviews": selected,
        "deferred_domains": deferred,
        "required_harness_skills": required_skills,
        "status": "ready" if not blockers else "blocked",
        "blockers": blockers,
        "claim_ceiling": "quality_review_plan_only",
    }
    return plan, make_taskset(request, selected)


def artifact_tuples(items: Any) -> list[tuple[str, str, str]]:
    if not isinstance(items, list):
        return []
    values = []
    for item in items:
        if isinstance(item, dict):
            values.append((str(item.get("path")), str(item.get("sha256")), str(item.get("role"))))
    return sorted(values)


def required_roles_for_pass(domain: str, request: dict[str, Any]) -> set[str]:
    stage = request["review_stage"]
    if domain == "gameplay" and stage in {"vertical_slice", "release_candidate"}:
        return {"rom", "emulator_capture", "input_trace"}
    if domain == "level_design":
        return {"level_blueprint", "mechanic_report"}
    if domain == "art" and stage in {"vertical_slice", "release_candidate"}:
        return {"visual_asset", "art_direction"}
    if domain == "audio" and request["audio_weight"] == "critical":
        return {"audio_contract", "audio_capture"}
    if domain == "narrative" and request["narrative_weight"] == "substantial":
        return {"gdd", "script"}
    return set()


def expected_growth_decision(reviewers: list[dict[str, Any]]) -> str:
    findings = [finding for reviewer in reviewers for finding in reviewer.get("findings", [])]
    if any(finding.get("blocks_growth") for finding in findings):
        return "revise_before_growth"
    if any(finding.get("scope_change_required") for finding in findings):
        return "human_scope_decision_required"
    if findings:
        return "proceed_with_tracked_risks"
    return "proceed"


def validate_report(
    request: dict[str, Any], plan: dict[str, Any], report: dict[str, Any]
) -> dict[str, Any]:
    validate_request(request)
    findings: list[str] = []
    if plan.get("artifact_kind") != "quality_review_plan":
        raise ContractError("invalid_plan_artifact_kind")
    expected_plan, _ = build_plan(request)
    if plan.get("request_digest") != expected_plan["request_digest"]:
        findings.append("plan_request_digest_stale")
    if plan.get("plan_digest") != expected_plan["plan_digest"]:
        findings.append("plan_decision_digest_stale")
    if plan.get("selected_reviews") != expected_plan["selected_reviews"]:
        findings.append("plan_selected_reviews_tampered")
    if plan.get("deferred_domains") != expected_plan["deferred_domains"]:
        findings.append("plan_deferred_domains_tampered")
    if plan.get("required_harness_skills") != expected_plan["required_harness_skills"]:
        findings.append("plan_required_skills_tampered")
    if report.get("artifact_kind") != "independent_quality_review":
        findings.append("invalid_report_artifact_kind")
    if report.get("review_id") != request["review_id"]:
        findings.append("review_id_mismatch")
    if report.get("request_digest") != expected_plan["request_digest"]:
        findings.append("report_request_digest_stale")
    if report.get("plan_digest") != expected_plan["plan_digest"]:
        findings.append("report_plan_digest_stale")
    if artifact_tuples(report.get("artifact_bindings")) != artifact_tuples(request["artifacts"]):
        findings.append("artifact_hash_bindings_mismatch")

    expected_reviews = {item["domain"]: item for item in expected_plan["selected_reviews"]}
    reviewers = report.get("reviewers")
    if not isinstance(reviewers, list):
        reviewers = []
        findings.append("reviewers_missing")
    domains = [item.get("domain") for item in reviewers if isinstance(item, dict)]
    if len(domains) != len(set(domains)):
        findings.append("duplicate_reviewer_domain")
    if set(domains) != set(expected_reviews):
        findings.append("selected_reviewer_set_mismatch")

    all_finding_ids: list[str] = []
    artifact_roles = {item["role"] for item in request["artifacts"]}
    review_as_of = date.fromisoformat(request["as_of"])
    for reviewer in reviewers:
        if not isinstance(reviewer, dict):
            findings.append("reviewer_not_object")
            continue
        domain = reviewer.get("domain")
        expected = expected_reviews.get(domain)
        if expected and reviewer.get("owner_skill") != expected["owner_skill"]:
            findings.append(f"review_owner_mismatch:{domain}")
        reviewer_id = reviewer.get("reviewer_id")
        if not isinstance(reviewer_id, str) or not reviewer_id:
            findings.append(f"reviewer_id_missing:{domain}")
        if reviewer_id in request["producer_ids"]:
            findings.append(f"producer_self_review:{domain}")
        if reviewer.get("producer_context_visible") is not False:
            findings.append(f"producer_rationale_visible:{domain}")
        domain_findings = reviewer.get("findings")
        if not isinstance(domain_findings, list):
            domain_findings = []
            findings.append(f"domain_findings_missing:{domain}")
        blocking = False
        for item in domain_findings:
            if not isinstance(item, dict):
                findings.append(f"finding_not_object:{domain}")
                continue
            finding_id = item.get("finding_id")
            if not isinstance(finding_id, str) or not re.fullmatch(
                r"[a-z0-9][a-z0-9_-]{2,63}", finding_id
            ):
                findings.append(f"finding_id_missing:{domain}")
                continue
            all_finding_ids.append(finding_id)
            classification = item.get("classification")
            if classification not in {"defect", "risk", "opportunity", "taste"}:
                findings.append(f"finding_classification_invalid:{finding_id}")
            if item.get("severity") not in {"info", "minor", "major", "critical"}:
                findings.append(f"finding_severity_invalid:{finding_id}")
            confidence = item.get("confidence")
            if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
                findings.append(f"finding_confidence_invalid:{finding_id}")
            if not isinstance(item.get("blocks_growth"), bool):
                findings.append(f"finding_blocks_growth_invalid:{finding_id}")
            for key in ("evidence", "acceptance_evidence"):
                values = item.get(key)
                if not isinstance(values, list) or not values or any(
                    not isinstance(value, str) or not value for value in values
                ):
                    findings.append(f"finding_{key}_invalid:{finding_id}")
            for key in ("player_impact", "smallest_correction"):
                if not isinstance(item.get(key), str) or not item[key]:
                    findings.append(f"finding_{key}_invalid:{finding_id}")
            if not re.fullmatch(
                r"[a-z0-9-]+/[a-z0-9-]+", str(item.get("correction_owner_skill", ""))
            ):
                findings.append(f"finding_correction_owner_invalid:{finding_id}")
            if not isinstance(item.get("scope_change_required"), bool):
                findings.append(f"finding_scope_change_invalid:{finding_id}")
            if classification in {"taste", "opportunity"} and item.get("blocks_growth"):
                findings.append(f"nonblocking_classification_blocks_growth:{finding_id}")
            if item.get("blocks_growth") and item.get("severity") not in {"major", "critical"}:
                findings.append(f"blocking_severity_too_low:{finding_id}")
            if item.get("blocks_growth") and (
                not isinstance(confidence, (int, float))
                or isinstance(confidence, bool)
                or confidence < 0.7
            ):
                findings.append(f"blocking_confidence_too_low:{finding_id}")
            if classification == "taste" and item.get("severity") not in {"info", "minor"}:
                findings.append(f"taste_severity_excessive:{finding_id}")
            blocking = blocking or bool(item.get("blocks_growth"))
        expected_status = "blocked" if blocking else "needs_adjustment" if domain_findings else "passed"
        if reviewer.get("status") != expected_status:
            findings.append(f"review_status_inconsistent:{domain}")
        required_roles = required_roles_for_pass(str(domain), request)
        if reviewer.get("status") == "passed" and not required_roles <= artifact_roles:
            missing_roles = ",".join(sorted(required_roles - artifact_roles))
            findings.append(f"domain_pass_missing_evidence:{domain}:{missing_roles}")
        if domain == "market":
            sources = reviewer.get("external_sources")
            if not isinstance(sources, list) or len(sources) < 2:
                findings.append("market_requires_two_current_sources")
            else:
                urls = [str(source.get("url", "")) for source in sources if isinstance(source, dict)]
                if len(set(urls)) != len(urls):
                    findings.append("market_sources_not_independent")
                hosts = [urlparse(url).netloc.lower() for url in urls]
                if len(set(hosts)) != len(hosts):
                    findings.append("market_sources_not_independent")
                for source in sources:
                    if not isinstance(source, dict):
                        findings.append("market_source_not_object")
                        continue
                    try:
                        observed = date.fromisoformat(source.get("observed_at", ""))
                    except (AttributeError, ValueError):
                        findings.append("market_source_date_invalid")
                        continue
                    age = (review_as_of - observed).days
                    if age < 0 or age > MARKET_MAX_AGE_DAYS:
                        findings.append(f"market_source_stale:{source.get('url', 'unknown')}")
                    if not str(source.get("url", "")).startswith("https://"):
                        findings.append("market_source_url_invalid")
                    if not isinstance(source.get("title"), str) or not source["title"]:
                        findings.append("market_source_title_invalid")
                    if source.get("source_type") not in {
                        "primary",
                        "storefront",
                        "dataset",
                        "trade_publication",
                        "secondary",
                    }:
                        findings.append("market_source_type_invalid")

    if len(all_finding_ids) != len(set(all_finding_ids)):
        findings.append("duplicate_finding_id")
    synthesis = report.get("synthesis")
    if not isinstance(synthesis, dict):
        synthesis = {}
        findings.append("synthesis_missing")
    expected_decision = expected_growth_decision(reviewers)
    if synthesis.get("growth_decision") != expected_decision:
        findings.append(
            f"growth_decision_inconsistent:{synthesis.get('growth_decision')}->{expected_decision}"
        )
    priorities = synthesis.get("priority_finding_ids")
    if not isinstance(priorities, list):
        findings.append("priority_finding_ids_missing")
        priorities = []
    if len(priorities) > 3:
        findings.append("too_many_immediate_priorities")
    if len(priorities) != len(set(priorities)):
        findings.append("duplicate_priority_finding_id")
    for finding_id in priorities:
        if finding_id not in all_finding_ids:
            findings.append(f"priority_finding_unknown:{finding_id}")
    blocking_ids = {
        item.get("finding_id")
        for reviewer in reviewers
        for item in reviewer.get("findings", [])
        if isinstance(item, dict) and item.get("blocks_growth")
    }
    if blocking_ids:
        if not priorities:
            findings.append("blocking_findings_not_prioritized")
        elif any(finding_id not in blocking_ids for finding_id in priorities):
            findings.append("nonblocking_priority_precedes_blocker")
        elif len(blocking_ids) <= 3 and not blocking_ids <= set(priorities):
            findings.append("blocking_finding_missing_from_priorities")
    if report.get("quality_claim") != "unproven":
        findings.append("quality_claim_must_remain_unproven")
    if report.get("ready_for_aaa") is not False:
        findings.append("quality_review_cannot_claim_aaa")
    if report.get("claim_ceiling") != "independent_quality_review_only":
        findings.append("quality_review_claim_ceiling_mismatch")

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "independent_quality_review_validation",
        "review_id": request["review_id"],
        "status": "passed" if not findings else "failed",
        "findings": sorted(set(findings)),
        "growth_decision": synthesis.get("growth_decision"),
        "report_may_direct_remediation": not findings,
        "quality_claim": "unproven",
        "ready_for_aaa": False,
        "claim_ceiling": "quality_review_validation_only",
    }


def sample_request(stage: str = "foundation") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "quality_review_request",
        "review_id": "fixture_review",
        "review_stage": stage,
        "project_context": "aaa_game",
        "project_root": "SGDK_projects/fixture",
        "as_of": "2026-09-05",
        "current_claim_ceiling": "documentado",
        "changed_domains": ["game_design", "narrative"],
        "risk_flags": [],
        "requested_domains": ["market"],
        "commercial_intent": True,
        "narrative_weight": "substantial",
        "audio_weight": "none",
        "artifacts": [
            {"path": "doc/11-gdd.md", "sha256": "a" * 64, "role": "gdd"},
            {"path": "doc/12-roteiro.md", "sha256": "b" * 64, "role": "script"},
        ],
        "producer_ids": ["producer"],
    }


def sample_report(request: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    reviewers = []
    for item in plan["selected_reviews"]:
        sources = []
        if item["domain"] == "market":
            sources = [
                {"title": "Store A", "url": "https://example.com/a", "observed_at": request["as_of"], "source_type": "storefront"},
                {"title": "Dataset B", "url": "https://example.org/b", "observed_at": request["as_of"], "source_type": "dataset"},
            ]
        reviewers.append(
            {
                "domain": item["domain"],
                "owner_skill": item["owner_skill"],
                "reviewer_id": f"reviewer_{item['domain']}",
                "producer_context_visible": False,
                "status": "passed",
                "findings": [],
                "external_sources": sources,
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "independent_quality_review",
        "review_id": request["review_id"],
        "request_digest": plan["request_digest"],
        "plan_digest": plan["plan_digest"],
        "artifact_bindings": request["artifacts"],
        "reviewers": reviewers,
        "synthesis": {
            "growth_decision": "proceed",
            "priority_finding_ids": [],
            "cross_domain_conflicts": [],
        },
        "quality_claim": "unproven",
        "ready_for_aaa": False,
        "claim_ceiling": "independent_quality_review_only",
    }


def self_check() -> dict[str, Any]:
    checks: list[tuple[str, bool]] = []
    request = sample_request()
    plan, taskset = build_plan(request)
    selected = [item["domain"] for item in plan["selected_reviews"]]
    checks.append(("selects_maximum_three", len(selected) == 3))
    checks.append(("selects_explicit_market", "market" in selected))
    checks.append(("review_tasks_are_read_only", all(task["read_only"] and not task["write_paths"] for task in taskset["tasks"])))
    report = sample_report(request, plan)
    checks.append(("accepts_clean_independent_report", validate_report(request, plan, report)["status"] == "passed"))

    self_review = json.loads(json.dumps(report))
    self_review["reviewers"][0]["reviewer_id"] = "producer"
    checks.append(("rejects_producer_self_review", any(item.startswith("producer_self_review") for item in validate_report(request, plan, self_review)["findings"])))

    taste = json.loads(json.dumps(report))
    taste_finding = {
        "finding_id": "taste_block",
        "classification": "taste",
        "severity": "critical",
        "confidence": 1.0,
        "blocks_growth": True,
        "evidence": ["personal preference"],
        "player_impact": "unproven",
        "smallest_correction": "change style",
        "correction_owner_skill": "art/visual-excellence-standards",
        "acceptance_evidence": ["reviewer likes it"],
        "scope_change_required": False,
    }
    taste["reviewers"][0]["findings"] = [taste_finding]
    taste["reviewers"][0]["status"] = "blocked"
    taste["synthesis"]["growth_decision"] = "revise_before_growth"
    taste_validation = validate_report(request, plan, taste)
    checks.append(("rejects_taste_blocker", any(item.startswith("nonblocking_classification") for item in taste_validation["findings"])))
    checks.append(("rejects_excessive_taste_severity", any(item.startswith("taste_severity_excessive") for item in taste_validation["findings"])))

    stale = json.loads(json.dumps(report))
    market = next(item for item in stale["reviewers"] if item["domain"] == "market")
    market["external_sources"][0]["observed_at"] = "2025-01-01"
    checks.append(("rejects_stale_market_source", any(item.startswith("market_source_stale") for item in validate_report(request, plan, stale)["findings"])))

    wrong_hash = json.loads(json.dumps(report))
    wrong_hash["artifact_bindings"][0]["sha256"] = "c" * 64
    checks.append(("rejects_artifact_hash_drift", "artifact_hash_bindings_mismatch" in validate_report(request, plan, wrong_hash)["findings"]))

    scope = json.loads(json.dumps(report))
    opportunity = dict(taste_finding)
    opportunity.update({"finding_id": "new_feature", "classification": "opportunity", "severity": "major", "blocks_growth": False, "scope_change_required": True})
    scope["reviewers"][0]["findings"] = [opportunity]
    scope["reviewers"][0]["status"] = "needs_adjustment"
    scope["synthesis"]["growth_decision"] = "proceed_with_tracked_risks"
    checks.append(("requires_human_decision_for_scope_growth", any(item.startswith("growth_decision_inconsistent") for item in validate_report(request, plan, scope)["findings"])))

    pre_growth = sample_request("pre_growth")
    pre_growth.update({"changed_domains": ["mechanics", "level_design", "gameplay"], "requested_domains": [], "commercial_intent": False, "narrative_weight": "none"})
    pre_plan, _ = build_plan(pre_growth)
    checks.append(("pre_growth_routes_core_three", {item["domain"] for item in pre_plan["selected_reviews"]} == {"mechanics", "level_design", "gameplay"}))

    no_market = sample_request()
    no_market.update({"requested_domains": [], "commercial_intent": False, "changed_domains": ["game_design"], "narrative_weight": "none"})
    no_market_plan, _ = build_plan(no_market)
    checks.append(("market_not_automatic_without_intent", "market" not in {item["domain"] for item in no_market_plan["selected_reviews"]}))

    explicit = sample_request()
    explicit.update(
        {
            "requested_domains": ["market", "art", "audio"],
            "changed_domains": ["game_design"],
            "audio_weight": "supporting",
        }
    )
    explicit_plan, _ = build_plan(explicit)
    checks.append(
        (
            "preserves_three_explicit_domains",
            [item["domain"] for item in explicit_plan["selected_reviews"]]
            == ["market", "art", "audio"],
        )
    )

    tampered_plan = json.loads(json.dumps(plan))
    tampered_plan["selected_reviews"][0]["owner_skill"] = "planning/tdd-authoring"
    checks.append(
        (
            "rejects_plan_payload_tamper",
            "plan_selected_reviews_tampered"
            in validate_report(request, tampered_plan, report)["findings"],
        )
    )

    duplicate_market = json.loads(json.dumps(report))
    market_review = next(
        item for item in duplicate_market["reviewers"] if item["domain"] == "market"
    )
    market_review["external_sources"][1]["url"] = market_review["external_sources"][0]["url"]
    checks.append(
        (
            "rejects_duplicate_market_sources",
            "market_sources_not_independent"
            in validate_report(request, plan, duplicate_market)["findings"],
        )
    )

    malformed_finding = json.loads(json.dumps(taste))
    malformed_finding["reviewers"][0]["findings"][0]["confidence"] = 2.0
    checks.append(
        (
            "rejects_malformed_finding",
            any(
                item.startswith("finding_confidence_invalid")
                for item in validate_report(request, plan, malformed_finding)["findings"]
            ),
        )
    )

    weak_blocker = json.loads(json.dumps(taste))
    weak_item = weak_blocker["reviewers"][0]["findings"][0]
    weak_item.update(
        {
            "finding_id": "weak_risk",
            "classification": "risk",
            "severity": "minor",
            "confidence": 0.4,
        }
    )
    weak_blocker["synthesis"]["priority_finding_ids"] = ["weak_risk"]
    weak_validation = validate_report(request, plan, weak_blocker)
    checks.append(
        (
            "rejects_weak_blocker",
            "blocking_severity_too_low:weak_risk" in weak_validation["findings"]
            and "blocking_confidence_too_low:weak_risk" in weak_validation["findings"],
        )
    )

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
    plan = sub.add_parser("plan", help="Select up to three independent review domains.")
    plan.add_argument("--request", type=Path, required=True)
    plan.add_argument("--output", type=Path, required=True)
    plan.add_argument("--taskset-output", type=Path, required=True)
    validate = sub.add_parser("validate-report", help="Validate an independent consolidated review.")
    validate.add_argument("--request", type=Path, required=True)
    validate.add_argument("--plan", type=Path, required=True)
    validate.add_argument("--report", type=Path, required=True)
    validate.add_argument("--output", type=Path)
    sub.add_parser("self-check", help="Run permanent adversarial fixtures.")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "plan":
            output, taskset = build_plan(load_json(args.request))
            atomic_write_json(args.output, output)
            atomic_write_json(args.taskset_output, taskset)
        elif args.command == "validate-report":
            output = validate_report(
                load_json(args.request), load_json(args.plan), load_json(args.report)
            )
            if args.output:
                atomic_write_json(args.output, output)
        else:
            output = self_check()
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0 if output.get("status") in {"ready", "passed"} else 1
    except ContractError as exc:
        print(json.dumps({"status": "error", "blockers": [str(exc)]}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

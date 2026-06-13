#!/usr/bin/env python3
"""Extract project-local lessons and generate unapplied canonical patch proposals."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
OWNER_CATALOG_PATH = ROOT / "tools" / "sgdk_wrapper" / ".agent" / "references" / "learning_owner_catalog.json"
REQUIRED_MARKDOWN = {
    "README.md": None,
    "success_patterns.md": "success_pattern",
    "failure_patterns.md": "failure_pattern",
    "skill_promotion_candidates.md": "skill_promotion_candidate",
    "canonical_promotion_review.md": "canonical_promotion_review",
}
LEDGER_NAME = "learning_ledger.json"
PLACEHOLDER_MARKERS = ("[data]", "[cena/sistema]", "[o que ", "[nome", "[problema]", "[motivo]")
SECTION_BLACKLIST = {
    "regras",
    "criterios minimos",
    "checklist de revisao",
    "decisoes",
    "politica",
    "como usar",
    "regra central",
    "classificacoes permitidas",
    "relacao com out/agent_learning",
}
FIELD_ALIASES = {
    "date": "date",
    "data": "date",
    "context": "context",
    "contexto": "context",
    "symptom": "observation",
    "falha observada": "observation",
    "padrao observado": "observation",
    "problema resolvido": "observation",
    "technical diagnosis": "diagnosis",
    "causa provavel": "diagnosis",
    "preventive heuristic": "heuristic",
    "mitigacao": "heuristic",
    "limite de uso": "scope",
    "risco": "scope",
    "proxima revisao humana": "scope",
    "check in rom": "check",
    "evidence": "evidence",
    "evidencia": "evidence",
    "evidencia minima": "evidence",
    "classificacao": "classification",
    "candidato": "candidate",
    "decisao": "decision",
    "justificativa": "diagnosis",
}
RELATIVE_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:out|doc|res|src|data|rascunho)[\\/][A-Za-z0-9_./\\ \[\]-]+\.(?:json|md|png|gif|bin|sram|log|txt))",
    re.IGNORECASE,
)
ABSOLUTE_REF_RE = re.compile(r"(?:[A-Za-z]:[\\/]|\\\\)[^\s`|]+")
PRESERVED_LIFECYCLE = {
    "approved_for_canonical_patch",
    "implemented",
    "verified",
    "rejected",
    "superseded",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return {}


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "unclassified_lesson"


def project_name(project_root: Path) -> str:
    manifest = load_json(project_root / ".mddev" / "project.json")
    return str(manifest.get("display_name") or manifest.get("name") or project_root.name)


def is_placeholder(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def parse_field_lines(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current: str | None = None
    for raw in lines:
        stripped = raw.strip()
        match = re.match(r"^-\s+([^:]+):\s*(.*)$", stripped)
        if match:
            label = FIELD_ALIASES.get(match.group(1).strip().lower(), match.group(1).strip().lower())
            current = label
            fields[current] = match.group(2).strip()
            continue
        if current and stripped.startswith("-"):
            addition = stripped.lstrip("- ").strip()
            if addition:
                fields[current] = (fields[current] + " " + addition).strip()
        elif current and stripped and not stripped.startswith("#"):
            fields[current] = (fields[current] + " " + stripped).strip()
    return fields


def parse_heading_entries(text: str, source_kind: str) -> list[dict[str, Any]]:
    headings = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", text))
    entries: list[dict[str, Any]] = []
    for index, heading in enumerate(headings):
        title = heading.group(1).strip()
        if title.lower() in SECTION_BLACKLIST or is_placeholder(title):
            continue
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[heading.end() : end].strip()
        fields = parse_field_lines(body.splitlines())
        if not fields or is_placeholder(body):
            continue
        entries.append({"title": title, "body": body, "fields": fields, "source_kind": source_kind})
    return entries


def parse_table_entries(text: str, source_kind: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return entries
    headers = [cell.strip().lower() for cell in lines[0].strip("|").split("|")]
    for raw in lines[2:]:
        cells = [cell.strip().strip("`") for cell in raw.strip("|").split("|")]
        if len(cells) != len(headers) or is_placeholder(raw):
            continue
        fields: dict[str, str] = {}
        for header, cell in zip(headers, cells):
            fields[FIELD_ALIASES.get(header, header)] = cell
        title = fields.get("candidate") or fields.get("observation") or fields.get("decision")
        if not title:
            continue
        entries.append({"title": title, "body": raw, "fields": fields, "source_kind": source_kind})
    return entries


def source_digest(learning_dir: Path) -> str:
    digest = hashlib.sha256()
    for name in REQUIRED_MARKDOWN:
        path = learning_dir / name
        if not path.exists():
            continue
        digest.update(name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def load_owner_catalog() -> list[dict[str, Any]]:
    catalog = load_json(OWNER_CATALOG_PATH)
    rules = catalog.get("rules", [])
    return rules if isinstance(rules, list) else []


def match_owner(entry: dict[str, Any], rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    haystack = f"{entry['title']} {entry['body']}".lower()
    for rule in rules:
        phrases = rule.get("match_any", [])
        if any(str(phrase).lower() in haystack for phrase in phrases):
            return rule
    return None


def normalize_relative_ref(value: str) -> str:
    return value.strip().strip("`.,;:()[]").replace("\\", "/")


def extract_evidence(
    project_root: Path,
    source_document: str,
    entry_text: str,
    warnings: list[str],
) -> dict[str, Any]:
    if ABSOLUTE_REF_RE.search(entry_text):
        warnings.append("external_evidence_reference_rejected")

    refs = {source_document}
    for match in RELATIVE_REF_RE.finditer(entry_text):
        relative = normalize_relative_ref(match.group(1))
        candidate = (project_root / relative).resolve()
        try:
            candidate.relative_to(project_root)
        except ValueError:
            warnings.append("external_evidence_reference_rejected")
            continue
        if candidate.exists():
            refs.add(relative)

    grade = "E1_artifact"
    if "out/rom.bin" in refs:
        grade = "E2_build"
    if any("blastem" in ref.lower() or ref.lower().endswith("emulator_session.json") for ref in refs):
        grade = "E3_blastem"
    if any("budget" in ref.lower() or "scene_regression_report" in ref.lower() for ref in refs):
        grade = "E4_budget_and_regression"

    freshness = "unknown"
    freshness_report = load_json(project_root / "out" / "logs" / "freshness_audit_report.json")
    freshness_status = str(freshness_report.get("status") or "").lower()
    if freshness_status:
        freshness = "stale" if freshness_status in {"stale", "blocked", "failed", "drift"} else "fresh"
    elif not any(ref.startswith("out/") for ref in refs):
        freshness = "not_applicable"

    gaps: list[str] = []
    if grade in {"E0_note_only", "E1_artifact"}:
        gaps.append("operational_evidence_missing")
    if freshness in {"unknown", "stale"}:
        gaps.append("evidence_freshness_unproven")
    return {
        "grade": grade,
        "freshness": freshness,
        "refs": sorted(refs),
        "gaps": sorted(set(gaps)),
    }


def route_entry(entry: dict[str, Any], matched_rule: dict[str, Any] | None) -> tuple[dict[str, Any], dict[str, Any]]:
    source_kind = entry["source_kind"]
    if matched_rule:
        routing = {
            "candidate_kind": matched_rule.get("candidate_kind", "human_review"),
            "deduplication": "matched_existing_owner",
            "canonical_target": matched_rule.get("canonical_target"),
            "owner_skill": matched_rule.get("owner_skill"),
            "match_rule_id": matched_rule.get("id"),
        }
        proposal = {
            "action": "patch_existing_owner",
            "target_path": matched_rule.get("canonical_target"),
            "summary": f"Review existing owner against project lesson: {entry['title']}",
            "required_tests": matched_rule.get("required_tests", []),
        }
    elif source_kind == "skill_promotion_candidate":
        routing = {
            "candidate_kind": "skill",
            "deduplication": "no_match",
            "canonical_target": None,
            "owner_skill": None,
            "match_rule_id": None,
        }
        proposal = {
            "action": "create_skill",
            "target_path": None,
            "summary": f"Evaluate whether a new skill is justified: {entry['title']}",
            "required_tests": ["cross-project reproduction", "skill framework validation", "human approval"],
        }
    elif source_kind in {"failure_pattern", "canonical_promotion_review"}:
        routing = {
            "candidate_kind": "human_review",
            "deduplication": "no_match",
            "canonical_target": None,
            "owner_skill": None,
            "match_rule_id": None,
        }
        proposal = {
            "action": "none",
            "target_path": None,
            "summary": "Keep local until an existing owner or reusable procedural gap is proven.",
            "required_tests": ["human classification review"],
        }
    else:
        routing = {
            "candidate_kind": "none",
            "deduplication": "not_applicable",
            "canonical_target": None,
            "owner_skill": None,
            "match_rule_id": None,
        }
        proposal = {
            "action": "none",
            "target_path": None,
            "summary": "Local success note; no canonical change proposed.",
            "required_tests": [],
        }

    proposal.update(
        {
            "human_approval_required": True,
            "human_approval": {"status": "pending", "record_ref": None},
            "apply_status": "not_applied",
        }
    )
    return routing, proposal


def build_lesson(
    project_root: Path,
    source_document: str,
    entry: dict[str, Any],
    rules: list[dict[str, Any]],
    warnings: list[str],
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    fields = entry["fields"]
    signature = slug(entry["title"])
    lesson_id = "lesson_" + hashlib.sha256(f"{source_document}|{signature}".encode("utf-8")).hexdigest()[:16]
    evidence = extract_evidence(project_root, source_document, entry["body"], warnings)
    matched_rule = match_owner(entry, rules)
    routing, proposal = route_entry(entry, matched_rule)

    if entry["source_kind"] == "skill_promotion_candidate":
        classification = "promotion_candidate"
        lifecycle = "human_review_required"
    elif entry["source_kind"] == "canonical_promotion_review" or matched_rule:
        classification = "needs_human_review"
        lifecycle = "human_review_required"
    elif entry["source_kind"] == "failure_pattern":
        classification = "local_note"
        lifecycle = "evidence_incomplete"
    else:
        classification = "local_note"
        lifecycle = "qualified_local" if evidence["grade"] not in {"E0_note_only", "E1_artifact"} else "evidence_incomplete"

    if existing:
        if existing.get("lifecycle_status") in PRESERVED_LIFECYCLE:
            lifecycle = existing["lifecycle_status"]
        existing_proposal = existing.get("canonical_patch_proposal", {})
        if existing_proposal.get("human_approval", {}).get("status") in {"approved", "rejected"}:
            proposal["human_approval"] = existing_proposal["human_approval"]
            proposal["apply_status"] = existing_proposal.get("apply_status", proposal["apply_status"])

    scope_values = [fields.get("scope", ""), fields.get("check", "")]
    return {
        "lesson_id": lesson_id,
        "title": entry["title"],
        "source_kind": entry["source_kind"],
        "source_document": source_document,
        "classification": classification,
        "lifecycle_status": lifecycle,
        "observed_at": fields.get("date") or "date_not_declared",
        "problem_signature": signature,
        "context": fields.get("context", ""),
        "observation": fields.get("observation") or entry["title"],
        "diagnosis": fields.get("diagnosis", ""),
        "resolution_or_preventive_heuristic": fields.get("heuristic", ""),
        "scope_limits": sorted({value for value in scope_values if value}),
        "evidence": evidence,
        "routing": routing,
        "canonical_patch_proposal": proposal,
    }


def candidate_index(lessons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "lesson_id": lesson["lesson_id"],
            "title": lesson["title"],
            "lifecycle_status": lesson["lifecycle_status"],
            "evidence_grade": lesson["evidence"]["grade"],
            "action": lesson["canonical_patch_proposal"]["action"],
            "target_path": lesson["canonical_patch_proposal"]["target_path"],
        }
        for lesson in lessons
        if lesson["routing"]["candidate_kind"] != "none"
    ]


def context_status(learning_dir: Path) -> tuple[str, list[str], list[str]]:
    required = [*REQUIRED_MARKDOWN.keys(), LEDGER_NAME]
    if not learning_dir.exists():
        return "learning_context_absent", [], required
    present = [name for name in required if (learning_dir / name).is_file()]
    missing = [name for name in required if name not in present]
    return ("learning_context_present" if not missing else "learning_context_incomplete"), present, missing


def detect_recurring_blockers(project_root: Path, threshold: int = 3) -> list[str]:
    log_dir = project_root / "out" / "logs"
    if not log_dir.is_dir():
        return []

    candidates: list[Path] = []
    primary = log_dir / "validation_report.json"
    if primary.is_file():
        candidates.append(primary)
    candidates.extend(sorted(log_dir.glob("validation_report_*.json")))

    unique_files: dict[str, Path] = {}
    for path in candidates:
        unique_files[str(path.resolve())] = path
    ordered = sorted(unique_files.values(), key=lambda p: p.stat().st_mtime)
    if len(ordered) < threshold:
        return []

    recent = ordered[-threshold:]
    blocker_sets: list[set[str]] = []
    for report_path in recent:
        payload = load_json(report_path)
        blockers = payload.get("blocking_statuses") or []
        if not blockers:
            return []
        blocker_sets.append(set(str(b) for b in blockers if str(b).strip()))
    common = set.intersection(*blocker_sets) if blocker_sets else set()
    return sorted(common)


def parse_no_qualified_lessons_justification(learning_dir: Path) -> str | None:
    review_path = learning_dir / "canonical_promotion_review.md"
    if not review_path.is_file():
        return None
    text = review_path.read_text(encoding="utf-8-sig", errors="ignore")
    match = re.search(r"(?ms)^no_qualified_lessons_justification:\s*(.+?)(?:\n#|\Z)", text)
    if not match:
        return None
    value = match.group(1).strip()
    if len(value) < 16:
        return None
    if is_placeholder(value):
        return None
    return value


def collect_entries(learning_dir: Path) -> list[tuple[str, dict[str, Any]]]:
    collected: list[tuple[str, dict[str, Any]]] = []
    for name, source_kind in REQUIRED_MARKDOWN.items():
        if not source_kind:
            continue
        path = learning_dir / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        entries = parse_heading_entries(text, source_kind)
        entries.extend(parse_table_entries(text, source_kind))
        source_document = f"doc/agent_learning/{name}"
        collected.extend((source_document, entry) for entry in entries)
    return collected


def emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return
    print(f"[project_learning] status: {payload['status']}")
    print(f"[project_learning] mode: {payload['mode']}")
    print(f"[project_learning] lessons: {payload['lesson_count']}")
    print(f"[project_learning] candidates: {payload['candidate_count']}")
    print("[project_learning] canonical_promotion_performed: false")
    for warning in payload.get("warnings", []):
        print(f"[project_learning] warning: {warning}")


def run(project_root: Path, mode: str, output_format: str) -> int:
    project_root = project_root.resolve()
    learning_dir = project_root / "doc" / "agent_learning"
    ledger_path = learning_dir / LEDGER_NAME
    runtime_report_path = project_root / "out" / "logs" / "project_learning_report.json"
    status, present, missing = context_status(learning_dir)
    warnings: list[str] = []
    written_files: list[str] = []

    if not learning_dir.exists():
        report = {
            "schema_version": "1.0.0",
            "project_root": str(project_root),
            "mode": mode,
            "status": status,
            "capture_status": "not_captured",
            "is_blocking": False,
            "canonical_promotion_performed": False,
            "required_files": [*REQUIRED_MARKDOWN.keys(), LEDGER_NAME],
            "present_files": present,
            "missing_files": missing,
            "lesson_count": 0,
            "candidate_count": 0,
            "candidate_index": [],
            "warnings": ["legacy_learning_context_absent"],
            "written_files": [],
        }
        emit(report, output_format)
        return 0

    existing_ledger = load_json(ledger_path)
    existing_lessons = {
        lesson.get("lesson_id"): lesson
        for lesson in existing_ledger.get("lessons", [])
        if isinstance(lesson, dict) and lesson.get("lesson_id")
    }
    rules = load_owner_catalog()
    lessons_by_id: dict[str, dict[str, Any]] = {}
    for source_document, entry in collect_entries(learning_dir):
        lesson = build_lesson(project_root, source_document, entry, rules, warnings, None)
        existing = existing_lessons.get(lesson["lesson_id"])
        if existing:
            lesson = build_lesson(project_root, source_document, entry, rules, warnings, existing)
        lessons_by_id[lesson["lesson_id"]] = lesson
    lessons = list(lessons_by_id.values())
    lessons.sort(key=lambda item: (item["source_kind"], item["title"].lower(), item["lesson_id"]))
    compact_index = candidate_index(lessons)
    ledger = {
        "schema_version": "1.0.0",
        "project": {"name": project_name(project_root)},
        "policy": {
            "local_auto_update": True,
            "canonical_auto_mutation": False,
            "human_approval_required": True,
            "evidence_required": True,
        },
        "generated_at": now_iso(),
        "source_digest": source_digest(learning_dir),
        "lessons": lessons,
        "candidate_index": compact_index,
        "canonical_promotion_performed": False,
    }
    if existing_ledger:
        comparable_keys = (
            "schema_version",
            "project",
            "policy",
            "source_digest",
            "lessons",
            "candidate_index",
            "canonical_promotion_performed",
        )
        if all(existing_ledger.get(key) == ledger.get(key) for key in comparable_keys):
            ledger["generated_at"] = existing_ledger.get("generated_at", ledger["generated_at"])

    capture_status = "not_captured"
    if mode == "capture":
        write_json(ledger_path, ledger)
        written_files.append("doc/agent_learning/learning_ledger.json")
        status, present, missing = context_status(learning_dir)
        capture_status = "captured" if lessons else "no_qualified_lessons"

    recurring_blockers = detect_recurring_blockers(project_root)
    justification = None
    if mode == "capture" and capture_status == "no_qualified_lessons" and recurring_blockers:
        justification = parse_no_qualified_lessons_justification(learning_dir)
        if not justification:
            warnings.append("learning_capture_skipped_no_justification")

    report = {
        "schema_version": "1.0.0",
        "project_root": str(project_root),
        "mode": mode,
        "status": "learning_capture_skipped" if (mode == "capture" and capture_status == "no_qualified_lessons" and recurring_blockers and not justification) else status,
        "capture_status": capture_status,
        "is_blocking": bool(mode == "capture" and capture_status == "no_qualified_lessons" and recurring_blockers and not justification),
        "canonical_promotion_performed": False,
        "required_files": [*REQUIRED_MARKDOWN.keys(), LEDGER_NAME],
        "present_files": present,
        "missing_files": missing,
        "lesson_count": len(lessons),
        "candidate_count": len(compact_index),
        "candidate_index": compact_index,
        "warnings": sorted(set(warnings)),
        "written_files": written_files.copy(),
        "recurring_blockers": recurring_blockers,
        "no_qualified_lessons_justification": justification,
    }
    if mode == "capture":
        write_json(runtime_report_path, report)
        report["written_files"].append("out/logs/project_learning_report.json")
        write_json(runtime_report_path, report)

    emit(report, output_format)
    return 1 if report["is_blocking"] else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--mode", choices=("audit", "capture"), default="audit")
    parser.add_argument("--output-format", choices=("host", "json"), default="host")
    args = parser.parse_args()
    try:
        return run(Path(args.project_root), args.mode, args.output_format)
    except Exception as exc:  # fail closed with a machine-readable error
        payload = {
            "schema_version": "1.0.0",
            "project_root": str(Path(args.project_root)),
            "mode": args.mode,
            "status": "audit_error",
            "capture_status": "failed",
            "is_blocking": True,
            "canonical_promotion_performed": False,
            "lesson_count": 0,
            "candidate_count": 0,
            "candidate_index": [],
            "warnings": [str(exc)],
            "written_files": [],
        }
        emit(payload, args.output_format)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Regression suite for the safe project-local closed learning loop."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools" / "sgdk_wrapper" / ".agent" / "scripts" / "extract_project_learning.py"
SCHEMA = ROOT / "tools" / "sgdk_wrapper" / "schemas" / "learning_ledger.schema.json"
WRAPPER = ROOT / "tools" / "sgdk_wrapper" / "audit_project_learning.ps1"
ADOPT = ROOT / "tools" / "sgdk_wrapper" / "adopt_project_methodology.ps1"
MODEL_LEDGER = ROOT / "tools" / "sgdk_wrapper" / "modelo" / "doc" / "agent_learning" / "learning_ledger.json"
CANONICAL_AGENT = ROOT / "tools" / "sgdk_wrapper" / ".agent"
FIXTURE_ROOT = ROOT / "out" / "ci" / "project_learning_fixture"

passed = 0
failed = 0
total = 0


def assert_true(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        suffix = f" -- {detail}" if detail else ""
        print(f"  [FAIL] {name}{suffix}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def reset_fixture(with_learning: bool = True) -> None:
    if FIXTURE_ROOT.exists():
        shutil.rmtree(FIXTURE_ROOT)
    (FIXTURE_ROOT / "out" / "logs").mkdir(parents=True)
    if not with_learning:
        return
    learning = FIXTURE_ROOT / "doc" / "agent_learning"
    learning.mkdir(parents=True)
    write_text(learning / "README.md", "# Agent Learning\n")
    write_text(
        learning / "success_patterns.md",
        "# Success Patterns\n\n| Data | Classificacao | Contexto | Padrao observado | Evidencia | Limite de uso |\n"
        "|---|---|---|---|---|---|\n"
        "| [DATA] | `local_note` | [cena/sistema] | [o que funcionou] | [build/log] | [limite] |\n",
    )
    write_text(
        learning / "failure_patterns.md",
        "# Failure Patterns\n\n| Data | Classificacao | Contexto | Falha observada | Causa provavel | Mitigacao | Evidencia |\n"
        "|---|---|---|---|---|---|---|\n"
        "| [DATA] | `local_note` | [cena/sistema] | [o que falhou] | [causa] | [como evitar] | [log] |\n",
    )
    write_text(
        learning / "skill_promotion_candidates.md",
        "# Skill Promotion Candidates\n\n"
        "| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |\n"
        "|---|---|---|---|---|---|---|\n"
        "| [DATA] | `promotion_candidate` | [nome] | [problema] | [evidencia] | [risco] | [criterio] |\n",
    )
    write_text(learning / "canonical_promotion_review.md", "# Canonical Promotion Review\n")


def run_loop(mode: str) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(FIXTURE_ROOT),
            "--mode",
            mode,
            "--output-format",
            "json",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = {}
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {}
    return result, payload


def run_powershell(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


print("=== Project Learning Loop Test ===")

assert_true("extractor exists", SCRIPT.exists(), str(SCRIPT))
assert_true("learning ledger schema exists", SCHEMA.exists(), str(SCHEMA))
assert_true("PowerShell learning wrapper exists", WRAPPER.exists(), str(WRAPPER))
assert_true("canonical model learning ledger exists", MODEL_LEDGER.exists(), str(MODEL_LEDGER))

if SCRIPT.exists() and SCHEMA.exists() and WRAPPER.exists() and MODEL_LEDGER.exists():
    reset_fixture(with_learning=False)
    result, report = run_loop("audit")
    assert_true("legacy project without learning context audits successfully", result.returncode == 0, result.stderr)
    assert_true("absent learning context remains a warning", report.get("status") == "learning_context_absent", str(report))
    assert_true(
        "audit mode creates no project files",
        not (FIXTURE_ROOT / "doc" / "agent_learning" / "learning_ledger.json").exists()
        and not (FIXTURE_ROOT / "out" / "logs" / "project_learning_report.json").exists(),
    )

    reset_fixture()
    result, report = run_loop("capture")
    ledger_path = FIXTURE_ROOT / "doc" / "agent_learning" / "learning_ledger.json"
    runtime_report_path = FIXTURE_ROOT / "out" / "logs" / "project_learning_report.json"
    assert_true("capture mode writes the local ledger", result.returncode == 0 and ledger_path.exists(), result.stderr)
    assert_true("capture mode writes the runtime report", runtime_report_path.exists())
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert_true("empty templates produce no qualified lessons", ledger.get("lessons") == [], str(ledger.get("lessons")))
    assert_true("empty templates report no qualified lessons", report.get("capture_status") == "no_qualified_lessons", str(report))
    assert_true("capture never claims canonical promotion", report.get("canonical_promotion_performed") is False)

    for i in range(1, 4):
        validation_report = {
            "schema_version": "1.0.0",
            "generated_at": f"2026-06-0{i}T00:00:0{i}Z",
            "project_root": str(FIXTURE_ROOT),
            "blocking_statuses": ["visual_gate_blocked"],
        }
        write_text(FIXTURE_ROOT / "out" / "logs" / f"validation_report_{i}.json", json.dumps(validation_report))
    result, blocked_report = run_loop("capture")
    assert_true("loop with no lessons blocks capture without justification", result.returncode == 1, result.stderr)
    assert_true("blocked capture reports learning_capture_skipped", blocked_report.get("status") == "learning_capture_skipped", str(blocked_report))

    write_text(
        FIXTURE_ROOT / "doc" / "agent_learning" / "canonical_promotion_review.md",
        "# Canonical Promotion Review\n\nno_qualified_lessons_justification: loop reproduced; no new patterns beyond existing owners; human approved to proceed.\n",
    )
    result, unblocked_report = run_loop("capture")
    assert_true("loop with justification allows capture", result.returncode == 0, result.stderr)
    assert_true("unblocked capture keeps no_qualified_lessons", unblocked_report.get("capture_status") == "no_qualified_lessons", str(unblocked_report))

    reset_fixture()
    write_text(
        FIXTURE_ROOT / "doc" / "agent_learning" / "failure_patterns.md",
        """# Failure Patterns

## Static Sprite Scaling Is Not A Modular Boss

- date: 2026-06-04
- symptom: the pursuer appeared as one flat image despite a modular boss claim.
- technical diagnosis: child modules were never instantiated or updated.
- preventive heuristic: require separate runtime sprites, relative motion and a worst-scanline report.
- evidence: C:\\outside\\untrusted_capture.png
- check in ROM: capture two frames where child parts change relative position.
""",
    )
    canonical_before = tree_hash(CANONICAL_AGENT)
    result, report = run_loop("capture")
    canonical_after = tree_hash(CANONICAL_AGENT)
    ledger = json.loads((FIXTURE_ROOT / "doc" / "agent_learning" / "learning_ledger.json").read_text(encoding="utf-8"))
    assert_true("structured failure is extracted", len(ledger.get("lessons", [])) == 1, str(ledger.get("lessons")))
    lesson = ledger["lessons"][0]
    assert_true(
        "known failure routes to an existing canonical owner",
        lesson["routing"]["deduplication"] == "matched_existing_owner"
        and lesson["canonical_patch_proposal"]["action"] == "patch_existing_owner",
        str(lesson["routing"]),
    )
    assert_true(
        "canonical proposal remains unapplied and human-gated",
        lesson["canonical_patch_proposal"]["apply_status"] == "not_applied"
        and lesson["canonical_patch_proposal"]["human_approval"]["status"] == "pending",
        str(lesson["canonical_patch_proposal"]),
    )
    assert_true(
        "external evidence path is rejected",
        "external_evidence_reference_rejected" in report.get("warnings", [])
        and all("outside" not in ref for ref in lesson["evidence"]["refs"]),
        str(report.get("warnings")),
    )
    assert_true("capture does not mutate the canonical agent tree", canonical_before == canonical_after)
    assert_true("auto-captured ledger contains no MESTRE status", "MESTRE_" not in json.dumps(ledger))

    first_ids = [entry["lesson_id"] for entry in ledger["lessons"]]
    first_ledger_hash = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    result, _ = run_loop("capture")
    second_ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    second_ids = [entry["lesson_id"] for entry in second_ledger["lessons"]]
    assert_true(
        "repeated capture is byte-idempotent",
        first_ids == second_ids
        and len(second_ids) == len(set(second_ids))
        and first_ledger_hash == hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
    )

    ledger_hash_before_audit = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    report_hash_before_audit = hashlib.sha256(runtime_report_path.read_bytes()).hexdigest()
    result, audit_report = run_loop("audit")
    assert_true("audit after capture succeeds", result.returncode == 0, result.stderr)
    assert_true(
        "audit mode remains read-only",
        ledger_hash_before_audit == hashlib.sha256(ledger_path.read_bytes()).hexdigest()
        and report_hash_before_audit == hashlib.sha256(runtime_report_path.read_bytes()).hexdigest(),
    )
    assert_true("audit exposes compact candidate index", len(audit_report.get("candidate_index", [])) == 1)

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(Draft7Validator(schema).iter_errors(second_ledger), key=lambda error: list(error.path))
    assert_true("generated ledger validates against schema", not errors, "; ".join(error.message for error in errors[:3]))

    reset_fixture()
    write_text(
        FIXTURE_ROOT / "doc" / "agent_learning" / "skill_promotion_candidates.md",
        """# Skill Promotion Candidates

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| 2026-06-04 | `promotion_candidate` | deterministic_palette_lab_helper | repeated palette experiment setup | doc/agent_learning/skill_promotion_candidates.md | medio | cross-project proof |
""",
    )
    result, _ = run_loop("capture")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    candidate = ledger["lessons"][0]
    assert_true(
        "explicit unmatched candidate may propose a new skill but stays pending",
        candidate["canonical_patch_proposal"]["action"] == "create_skill"
        and candidate["lifecycle_status"] == "human_review_required"
        and candidate["canonical_patch_proposal"]["apply_status"] == "not_applied",
        str(candidate),
    )

    reset_fixture()
    write_text(
        FIXTURE_ROOT / "doc" / "agent_learning" / "skill_promotion_candidates.md",
        """# Skill Promotion Candidates

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| 2026-06-16 | `promotion_candidate` | planning_mode_pre_runtime_spec_closure_checklist | Planejamento AAA parecia completo sem contratos executaveis para runtime | doc/critical_gap_audit.json | medio | human review |
""",
    )
    write_text(FIXTURE_ROOT / "doc" / "critical_gap_audit.json", "{}")
    result, _ = run_loop("capture")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    routed = ledger["lessons"][0]
    assert_true(
        "known planning candidate patches an existing owner instead of creating a skill",
        routed["routing"]["deduplication"] == "matched_existing_owner"
        and routed["canonical_patch_proposal"]["action"] == "patch_existing_owner"
        and routed["routing"]["owner_skill"] == "planning/game-design-planning",
        str(routed),
    )

    reset_fixture()
    wrapper_result = run_powershell(
        WRAPPER,
        "-ProjectRoot",
        str(FIXTURE_ROOT),
        "-Mode",
        "Capture",
        "-OutputFormat",
        "Json",
    )
    wrapper_payload = json.loads(wrapper_result.stdout) if wrapper_result.stdout.strip() else {}
    assert_true(
        "PowerShell wrapper exposes capture mode",
        wrapper_result.returncode == 0
        and wrapper_payload.get("mode") == "capture"
        and (FIXTURE_ROOT / "doc" / "agent_learning" / "learning_ledger.json").exists(),
        wrapper_result.stderr or wrapper_result.stdout,
    )

    reset_fixture(with_learning=False)
    adopt_result = run_powershell(
        ADOPT,
        "-ProjectRoot",
        str(FIXTURE_ROOT),
        "-Lifecycle",
        "existing",
        "-ProjectName",
        "Learning Fixture [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]",
    )
    adopted_ledger = FIXTURE_ROOT / "doc" / "agent_learning" / "learning_ledger.json"
    assert_true(
        "methodology adoption safely materializes missing learning context",
        adopt_result.returncode == 0 and adopted_ledger.exists(),
        adopt_result.stderr or adopt_result.stdout,
    )
    if adopted_ledger.exists():
        adopted = json.loads(adopted_ledger.read_text(encoding="utf-8-sig"))
        assert_true(
            "adopted ledger is personalized and empty",
            adopted.get("project", {}).get("name")
            == "Learning Fixture [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]"
            and adopted.get("lessons") == [],
            str(adopted),
        )

    reset_fixture()
    write_text(
        FIXTURE_ROOT / "doc" / "agent_learning" / "canonical_promotion_review.md",
        """# Canonical Promotion Review

## Checklist de revisao

| Item | Status |
|---|---|
| O aprendizado tem evidencia rastreavel? | [pendente] |
| Um humano aprovou a promocao? | [pendente] |
""",
    )
    result, _ = run_loop("capture")
    ledger = json.loads((FIXTURE_ROOT / "doc" / "agent_learning" / "learning_ledger.json").read_text(encoding="utf-8"))
    assert_true(
        "review checklist rows are not learned as lessons",
        result.returncode == 0 and ledger.get("lessons") == [],
        str(ledger.get("lessons")),
    )

if FIXTURE_ROOT.exists():
    shutil.rmtree(FIXTURE_ROOT)

print(f"=== Results: {passed}/{total} passed, {failed} failed ===")
raise SystemExit(1 if failed else 0)

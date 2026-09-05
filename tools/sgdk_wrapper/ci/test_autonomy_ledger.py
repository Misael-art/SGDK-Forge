#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORDER = ROOT / "record_autonomy_event.py"
DERIVER = ROOT / "derive_autonomy_metrics.py"


def record(ledger: Path, *args: str, expected: int = 0) -> None:
    result = subprocess.run([sys.executable, str(RECORDER), "--ledger", str(ledger), "--session-id", "fixture", *args], capture_output=True, text=True, check=False)
    assert result.returncode == expected, result.stdout + result.stderr


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="autonomy_ledger_") as temp:
        root = Path(temp)
        ledger = root / "ledger.json"
        report = root / "report.json"
        record(ledger, "--event-type", "session_started", "--reason-code", "session_boundary")
        record(ledger, "--event-type", "task_started", "--task-id", "A")
        record(ledger, "--event-type", "task_completed", "--task-id", "A", "--reason-code", "acceptance_met")
        record(ledger, "--event-type", "task_started", "--task-id", "B")
        record(ledger, "--event-type", "task_reworked", "--task-id", "B", "--reason-code", "implementation_defect")
        record(ledger, "--event-type", "human_intervention", "--task-id", "B", "--reason-code", "human_correction", "--intervention-category", "correction")
        record(ledger, "--event-type", "task_completed", "--task-id", "B", "--reason-code", "acceptance_met")
        record(ledger, "--event-type", "task_started", "--task-id", "C")
        record(ledger, "--event-type", "task_blocked", "--task-id", "C", "--reason-code", "external_dependency")
        record(ledger, "--event-type", "session_closed", "--reason-code", "session_boundary")

        missing_category = subprocess.run([sys.executable, str(RECORDER), "--ledger", str(ledger), "--session-id", "fixture", "--event-type", "human_intervention", "--reason-code", "human_correction"], capture_output=True, text=True, check=False)
        assert missing_category.returncode != 0

        subprocess.run([sys.executable, str(DERIVER), "--ledger", str(ledger), "--output", str(report), "--session-id", "fixture"], check=True)
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["task_counts"] == {"started": 3, "completed": 2, "blocked": 1, "reworked": 1}
        assert data["derived_rates"]["completion_rate"] == 0.6667
        assert data["derived_rates"]["first_attempt_success_rate"] == 0.5
        assert data["derived_rates"]["autonomous_completion_rate"] == 0.5
        assert data["human_interventions"]["by_category"] == {"correction": 1}
        assert data["human_interventions"]["sensitive_content_stored"] is False
        assert data["quality_claim"] == "unproven" and data["ready_for_aaa"] is False

    print("autonomy_ledger: 3 checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

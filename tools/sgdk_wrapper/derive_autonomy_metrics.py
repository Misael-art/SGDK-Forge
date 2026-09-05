#!/usr/bin/env python3
"""Derive process metrics from autonomy events; never promote product quality."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def derive(ledger: dict[str, Any], session_id: str | None) -> dict[str, Any]:
    events = [event for event in ledger.get("events", []) if not session_id or event.get("session_id") == session_id]
    sessions = sorted({str(event.get("session_id")) for event in events})
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    interventions = Counter()
    for event in events:
        task_id = event.get("task_id")
        if task_id:
            by_task[str(task_id)].append(event)
        if event.get("event_type") == "human_intervention":
            interventions[str(event.get("intervention_category"))] += 1

    started = {task for task, task_events in by_task.items() if any(e.get("event_type") == "task_started" for e in task_events)}
    completed = {task for task, task_events in by_task.items() if any(e.get("event_type") == "task_completed" for e in task_events)}
    blocked = {task for task, task_events in by_task.items() if any(e.get("event_type") == "task_blocked" for e in task_events)}
    reworked = {task for task, task_events in by_task.items() if any(e.get("event_type") == "task_reworked" for e in task_events)}
    intervened = {task for task, task_events in by_task.items() if any(e.get("event_type") == "human_intervention" for e in task_events)}
    first_attempt = completed - reworked - blocked
    autonomous_completed = completed - intervened

    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_name": "derive_autonomy_metrics",
        "tool_version": "1.0.0",
        "status": "ok",
        "ledger_id": ledger.get("ledger_id"),
        "session_filter": session_id,
        "sessions_observed": sessions,
        "events_observed": len(events),
        "task_counts": {
            "started": len(started),
            "completed": len(completed),
            "blocked": len(blocked),
            "reworked": len(reworked),
        },
        "derived_rates": {
            "completion_rate": ratio(len(completed), len(started)),
            "blocked_task_rate": ratio(len(blocked), len(started)),
            "reworked_task_rate": ratio(len(reworked), len(started)),
            "first_attempt_success_rate": ratio(len(first_attempt), len(completed)),
            "autonomous_completion_rate": ratio(len(autonomous_completed), len(completed)),
        },
        "human_interventions": {
            "total": sum(interventions.values()),
            "by_category": dict(sorted(interventions.items())),
            "sensitive_content_stored": False,
        },
        "quality_claim": "unproven",
        "ready_for_aaa": False,
        "claim_limit": "Autonomy metrics describe process events only and cannot promote technical, creative, gameplay, audio, hardware, release, or AAA quality.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--session-id")
    args = parser.parse_args()
    ledger = json.loads(args.ledger.read_text(encoding="utf-8-sig"))
    report = derive(ledger, args.session_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "ok", "events": report["events_observed"], "tasks": report["task_counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

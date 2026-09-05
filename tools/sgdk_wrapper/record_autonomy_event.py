#!/usr/bin/env python3
"""Append a structured autonomy event without accepting free-form sensitive content."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EVENT_TYPES = {
    "session_started", "task_started", "task_completed", "task_blocked",
    "task_reworked", "human_intervention", "session_closed",
}
TASK_EVENTS = {"task_started", "task_completed", "task_blocked", "task_reworked"}
REASON_CODES = {
    "session_boundary", "acceptance_met", "external_dependency",
    "validation_failure", "implementation_defect", "scope_change",
    "clarification_needed", "approval_required", "human_correction", "safety_gate",
}
INTERVENTION_CATEGORIES = {
    "clarification", "approval", "correction", "scope_change",
    "external_dependency", "safety_gate",
}


def load_or_create(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"schema_version": "1.0.0", "ledger_id": path.stem, "events": []}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--event-type", required=True, choices=sorted(EVENT_TYPES))
    parser.add_argument("--task-id")
    parser.add_argument("--reason-code", choices=sorted(REASON_CODES))
    parser.add_argument("--intervention-category", choices=sorted(INTERVENTION_CATEGORIES))
    parser.add_argument("--timestamp")
    args = parser.parse_args()

    if args.event_type in TASK_EVENTS and not args.task_id:
        parser.error(f"{args.event_type} requires --task-id")
    if args.event_type == "human_intervention":
        if not args.intervention_category or not args.reason_code:
            parser.error("human_intervention requires category and reason code")
    elif args.intervention_category:
        parser.error("intervention category is valid only for human_intervention")

    ledger = load_or_create(args.ledger)
    timestamp = args.timestamp or datetime.now(timezone.utc).isoformat()
    event = {
        "schema_version": "1.0.0",
        "event_id": str(uuid.uuid4()),
        "session_id": args.session_id,
        "timestamp": timestamp,
        "event_type": args.event_type,
        "task_id": args.task_id,
        "reason_code": args.reason_code,
        "intervention_category": args.intervention_category,
        "sensitive_content_stored": False,
    }
    ledger.setdefault("events", []).append(event)
    write_atomic(args.ledger, ledger)
    print(json.dumps({"status": "recorded", "event_id": event["event_id"], "event_type": args.event_type}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

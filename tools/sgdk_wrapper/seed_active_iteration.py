#!/usr/bin/env python3
"""Seed an active_iteration.json for a project from its current memory bank.

Writes a valid v0 artifact anchored to the SHA-256 of doc/10-memory-bank.md.
The artifact is advisory state and never replaces the memory bank, contracts,
validators or emulator evidence.

Usage:
    python3 seed_active_iteration.py \
      --project-root "SGDK_projects/MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]" \
      --active-claim "..." --blocker-leaf "..." --route "..." --hypothesis "..." \
      --evidence-before "..."
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0.0"
TOOL_NAME = "seed_active_iteration"
TOOL_VERSION = "1.0.0"


def sha256_file(path):
    hasher = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    ap.add_argument("--workspace-root", required=False,
                    default=os.getcwd())
    ap.add_argument("--memory-bank-path", required=False, default=None,
                    help="Path to doc/10-memory-bank.md. Defaults to project_root/doc/10-memory-bank.md")
    ap.add_argument("--active-claim", required=True)
    ap.add_argument("--blocker-leaf", required=True)
    ap.add_argument("--route", required=True)
    ap.add_argument("--hypothesis", required=True)
    ap.add_argument("--evidence-before", required=False, default=None)
    ap.add_argument("--out", required=False, default=None,
                    help="Where to write the artifact. Defaults to project_root/doc/active_iteration.json")
    ap.add_argument("--human-gate-question", required=False, default=None)
    args = ap.parse_args()

    project_root = args.project_root
    if not os.path.isabs(project_root):
        project_root = os.path.normpath(os.path.join(args.workspace_root, project_root))
    project_root = os.path.normpath(project_root)

    mem_bank = args.memory_bank_path
    if not mem_bank:
        mem_bank = os.path.join(project_root, "doc", "10-memory-bank.md")
    mem_bank = os.path.normpath(mem_bank)

    if not os.path.isfile(mem_bank):
        print(f"[ERROR] memory bank not found: {mem_bank}", file=sys.stderr)
        sys.exit(1)

    mb_hash = sha256_file(mem_bank)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    human_gate = None
    if args.human_gate_question:
        human_gate = {
            "decision_question": args.human_gate_question,
            "options": [],
            "depends_on_artifact": args.blocker_leaf,
        }

    artifact = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now,
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "project_root": project_root,
        "workspace_root": os.path.normpath(args.workspace_root),
        "memory_bank_path": os.path.relpath(mem_bank, project_root),
        "status": "in_progress",
        "iteration_count": 1,
        "active_claim": args.active_claim,
        "blocker_leaf": args.blocker_leaf,
        "route": args.route,
        "hypothesis": args.hypothesis,
        "evidence_before": args.evidence_before,
        "evidence_after": None,
        "delta_status": "pending",
        "cause": None,
        "routes_closed": [],
        "human_gate_pending": human_gate,
        "independent_branches": [],
        "memory_bank_hash": mb_hash,
        "next_causal_action": None,
        "stop_reason": None,
    }

    out_path = args.out
    if not out_path:
        out_path = os.path.join(project_root, "doc", "active_iteration.json")
    out_path = os.path.normpath(out_path)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"[OK] wrote {out_path}")
    print(f"    memory_bank_hash={mb_hash}")
    print(f"    memory_bank_path={artifact['memory_bank_path']}")


if __name__ == "__main__":
    main()

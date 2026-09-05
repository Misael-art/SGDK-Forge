#!/usr/bin/env python3
"""Run the synthetic regressions that protect canonical agent decisions."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CI_DIR = Path(__file__).resolve().parent
TESTS = (
    "test_art_diagnostic_ownership.py",
    "test_sprite_artifact_report.py",
    "test_screenshot_semantic_gate.py",
    "test_doc_sync_audit.py",
    "test_sgdk_build_route_selector.py",
)


def main() -> int:
    failures: list[str] = []
    for name in TESTS:
        process = subprocess.run(
            [sys.executable, str(CI_DIR / name)],
            check=False,
            capture_output=True,
            text=True,
        )
        output = (process.stdout + process.stderr).strip()
        if output:
            print(f"=== {name} ===")
            print(output)
        if process.returncode != 0:
            failures.append(f"{name}:{process.returncode}")
    if failures:
        print("canonical_agent_regressions=failed " + ",".join(failures))
        return 1
    print(f"canonical_agent_regressions=passed count={len(TESTS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

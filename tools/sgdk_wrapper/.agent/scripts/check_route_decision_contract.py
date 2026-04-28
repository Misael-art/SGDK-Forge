#!/usr/bin/env python3
"""Smoke-check that the agent routing gate stays wired into core docs.

This is intentionally lightweight: it catches accidental removal of the
methodology guardrail that prevents new projects/scenes from jumping straight
into image conversion, .res edits or runtime attempts without a route decision.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]


CHECKS = [
    (
        ROOT / "workflows" / "route-decision-gate.md",
        ["route_decision_record", "SpriteDefinition.w", "forbidden_shortcuts_until_evidence"],
    ),
    (
        ROOT / "ARCHITECTURE.md",
        ["workflows/route-decision-gate.md", "route_decision_record"],
    ),
    (
        ROOT / "workflows" / "project-opening.md",
        ["route_decision_record", "workflows/route-decision-gate.md"],
    ),
    (
        ROOT / "workflows" / "plan.md",
        ["workflows/route-decision-gate.md", "scene-architecture-triage.md"],
    ),
    (
        ROOT / "workflows" / "production-loop.md",
        ["route_decision_record", "workflows/route-decision-gate.md"],
    ),
    (
        ROOT / "pipelines" / "aaa_scene_v1.json",
        ["route_decision_record", "route-decision-gate.md"],
    ),
    (
        ROOT / "skills" / "planning" / "game-design-planning" / "SKILL.md",
        ["route_decision_record", "first_tool"],
    ),
    (
        ROOT / "skills" / "art" / "multi-plane-composition" / "SKILL.md",
        ["resource_topology_plan", "route_decision_record"],
    ),
    (
        ROOT / "skills" / "hardware" / "megadrive-vdp-budget-analyst" / "SKILL.md",
        ["resident_window_unique_tiles", "world_total_unique_tiles"],
    ),
    (
        ROOT / "skills" / "code" / "sgdk-runtime-coder" / "SKILL.md",
        ["Roteamento antes de runtime", "SpriteDefinition"],
    ),
    (
        WORKSPACE / "tools" / "sgdk_wrapper" / "modelo" / "doc" / "11-gdd.md",
        ["Route Decision Record", "resource_loading_model"],
    ),
    (
        WORKSPACE / "sgdk_templates" / "base-elite" / "doc" / "11-gdd.md",
        ["Route Decision Record", "resource_loading_model"],
    ),
]


def main() -> int:
    failures: list[str] = []
    for path, needles in CHECKS:
        if not path.exists():
            failures.append(f"MISSING {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                failures.append(f"MISSING '{needle}' in {path}")

    if failures:
        print("[FAIL] route decision contract drift detected")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"[OK] route decision contract wired in {len(CHECKS)} surfaces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

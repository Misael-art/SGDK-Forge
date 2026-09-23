#!/usr/bin/env python3
"""Adversarial fixtures for the causal persistence loop decision guard.

The scenarios required before the loop may pilot native sprite production:
  (F1) tool failure with an alternative safe route -> retry/advance, never stop.
  (F2) unproductive equivalent repetition          -> close_route, not project.
  (F3) human gate with an independent branch       -> blocked_human + branch ok.
  (F4) global/irrelevant blocker                   -> advance the claim anyway.
  (F5) destructive action                          -> stop_unauthorized.
  (F6) real exhaustion of alternatives             -> stop_exhausted.

The guard (causal_persistence_guard.py) is the executable oracle. Each fixture
declares an expected verdict; a mismatch fails the suite. No jsonschema needed.

Usage:
    python tools/sgdk_wrapper/ci/test_causal_persistence_loop.py
Exit codes:
    0 = all fixtures pass
    1 = at least one fixture failed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sgdk_wrapper"))

from causal_persistence_guard import decide  # noqa: E402

passed = 0
failed = 0
total = 0


def run(name, state, expected_verdict):
    global passed, failed, total
    total += 1
    decision = decide(state)
    got = decision["verdict"]
    if got == expected_verdict:
        passed += 1
        print(f"  [PASS] {name} -> {got}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -- expected {expected_verdict}, got {got}")
        print(f"         {decision.get('message', '')[:160]}")


def main():
    print("\n=== Causal Persistence Loop Adversarial Fixtures ===\n")

    # F1: tool failure (GIMP/pointer automation) with a safe CLI alternative.
    run(
        "F1_tool_failure_safe_alternative",
        {
            "delta_status": "no_change",
            "cause": "tool_capability_failure",
            "evidence_before": "stage:rgba_raw",
            "evidence_after": None,
            "available_routes": ["forge-art", "pillow", "gimp_batch"],
            "routes_closed": ["gimp_gui_pointer"],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": True,
            "human_gate_pending": None,
        },
        "advance",
    )

    # F2: two equivalent attempts with no new evidence -> close the route, not
    #     the project (the project stays open).
    run(
        "F2_unproductive_repetition",
        {
            "delta_status": "no_change",
            "cause": "environment_failure",
            "evidence_before": "same",
            "evidence_after": "same",
            "available_routes": ["pillow", "gimp_batch"],
            "routes_closed": ["forge-art"],
            "used_equivalent_attempts": 2,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": True,
        },
        "close_route",
    )

    # F3: human gate present WITH an independent branch -> blocked_human, but
    #     the independent branch may continue.
    run(
        "F3_human_gate_with_independent_branch",
        {
            "delta_status": "pending",
            "cause": None,
            "evidence_before": None,
            "evidence_after": None,
            "available_routes": ["fixture_tool"],
            "routes_closed": [],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": True,
            "human_gate_pending": {
                "decision_question": "approve TAINA silhouette?",
                "options": ["yes", "no"],
                "depends_on_artifact": "taina_idle_silhouette",
            },
            "independent_branches": ["fixture_tool"],
        },
        "blocked_human",
    )

    # F4: guard that a global/irrelevant blocker does not stop a claim that
    #     does not depend on it.
    run(
        "F4_global_irrelevant_blocker",
        {
            "delta_status": "pending",
            "cause": None,
            "evidence_before": None,
            "evidence_after": None,
            "available_routes": ["forge-art"],
            "routes_closed": [],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": False,
            "human_gate_pending": None,
        },
        "advance",
    )

    # F5: destructive / external / expensive action -> stop for authorization.
    run(
        "F5_destructive_action",
        {
            "delta_status": "pending",
            "cause": None,
            "evidence_before": None,
            "evidence_after": None,
            "available_routes": ["pillow"],
            "routes_closed": [],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": True,
            "proposed_action": "overwrite_asset",
        },
        "stop_unauthorized",
    )

    # F6: real exhaustion of all safe/authorized alternatives with evidence.
    run(
        "F6_real_exhaustion",
        {
            "delta_status": "no_change",
            "cause": "representation_mismatch",
            "evidence_before": "asset_v1",
            "evidence_after": "asset_v1_no_change",
            "available_routes": [],
            "routes_closed": ["forge-art", "pillow", "gimp_batch"],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": True,
        },
        "stop_exhausted",
    )

    # F7: a capable producer returned the wrong representation (1086x1448 RGB
    # instead of native 48x64 indexed). This is NOT a human gate — the agent
    # must change representation and retry, never ask a human to supply it.
    run(
        "F7_representation_mismatch_not_human_gate",
        {
            "delta_status": "no_change",
            "cause": "representation_mismatch",
            "evidence_before": "approved_model_sheet",
            "evidence_after": "1086x1448_rgb_not_native",
            "available_routes": ["native_grid_stamp", "change_producer"],
            "routes_closed": ["codex_builtin_image_generation"],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": True,
            # The false human gate the agent wrote; must be dismissed by the guard.
            "human_gate_pending": {
                "decision_question": "Quem fornece a lineart nativa 48x64?",
                "options": [],
                "depends_on_artifact": "taina_native_48x64_lineart_missing",
            },
        },
        "retry_changed_representation",
    )

    # F8: a locked 48x64 contract that loses semantic detail must be reauthored
    # in 48x64. A visually stronger 64x96 probe is not silent authorization.
    run(
        "F8_locked_scale_reauthors_native_grid",
        {
            "delta_status": "regressed",
            "cause": "scale_density_mismatch",
            "evidence_before": "approved_identity_source",
            "evidence_after": "native_48x64_visual_fail",
            "available_routes": ["direct_native_cluster_redraw"],
            "routes_closed": ["automatic_downscale"],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": True,
            "scale_lock_status": "locked",
        },
        "retry_changed_representation",
    )

    # F9: provisional scale is an engineering question before it is a human
    # preference. Measure bounded candidates first.
    run(
        "F9_provisional_scale_requires_measurement",
        {
            "delta_status": "no_change",
            "cause": "scale_density_mismatch",
            "evidence_before": "native_48x64_visual_fail",
            "evidence_after": "64x96_probe_visual_pass",
            "available_routes": ["bounded_scale_probe"],
            "routes_closed": [],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 0,
            "blocker_relevant": True,
            "scale_lock_status": "provisional",
            "scale_tradeoff_measured": False,
        },
        "retry_scale_measurement",
    )

    # F10: after camera/budget tradeoffs are measured, a product-changing
    # scale decision is legitimately human and blocks only that branch.
    run(
        "F10_measured_product_scale_opens_human_gate",
        {
            "delta_status": "advanced",
            "cause": "scale_density_mismatch",
            "evidence_before": "48x64_and_64x96_unmeasured",
            "evidence_after": "bounded_scale_comparison_with_budget",
            "available_routes": ["keep_48x64", "adopt_64x96"],
            "routes_closed": [],
            "used_equivalent_attempts": 0,
            "artifact_kind": "asset",
            "blockers_removed": 1,
            "blocker_relevant": True,
            "scale_lock_status": "provisional",
            "scale_tradeoff_measured": True,
            "scale_product_change_required": True,
            "human_gate_pending": {
                "decision_question": "Adotar a escala que altera camera e workload?",
                "options": ["keep_48x64", "adopt_64x96"],
                "depends_on_artifact": "scale_comparison_report",
            },
        },
        "blocked_human",
    )

    print(f"\n{passed}/{total} causal-persistence fixtures passed")
    return 0 if failed == 0 else 1


# Verify the module at least loads its own schema contract imports cleanly.
if __name__ == "__main__":
    sys.exit(main())

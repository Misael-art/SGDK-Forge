#!/usr/bin/env python3
"""Causal persistence loop decision guard (machine-checkable).

Encodes the causal loop rules from workflows/causal-persistence-loop.md as a
pure decision function so the adversarial scenarios in
ci/test_causal_persistence_loop.py can be asserted deterministically. This is
not a replacement for the workflow narrative or for the ps1 validator — it is
the executable oracle for the repressible-failure / repetition / human-gate /
destructive-action / exhaustion guards.

Tie-break rule: a REPRESENTATION failure (wrong dimensions, indexing or grid)
is never a human decision. Change representation or producer and retry, even
when a human_gate_pending field was written for it (guard dismisses it to
`retry_changed_representation`).

Usage: import and call `decide(state)`; or run directly on a state JSON.

Exit codes: 0 = runnable/decision computed, 1 = invalid state or no decision.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Optional

DESTRUCTIVE_ACTIONS = {
    "force_reset",
    "delete_project",
    "overwrite_asset",
    "rm_rf",
    "git_push_force",
    "modify_header",
    "external_network_call",
    "release_publish",
}
EXPENSE_REASONS = {"expensive", "destructive", "external", "scope_expansion"}

REPETITION_LIMIT = 2

CAUSAL_CLASSES = {
    "implementation_failure",
    "tool_capability_failure",
    "interaction_channel_mismatch",
    "representation_mismatch",
    "scale_density_mismatch",
    "environment_failure",
    "contract_or_spec_conflict",
    "human_decision_required",
}


# --- decisions -------------------------------------------------------------

def _equivalent_attempts(state: Dict[str, Any]) -> bool:
    """True when the current route+hypothesis is one of >=N equivalent attempts
    that produced no new evidence (a repeated attempt with no registered delta)."""
    used = state.get("used_equivalent_attempts", 0) or 0
    return used >= REPETITION_LIMIT


def _delta_measured(state: Dict[str, Any]) -> bool:
    after = state.get("evidence_after")
    before = state.get("evidence_before")
    if not after or not before:
        return False
    return after != before


def decide(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return a decision dict: {verdict, reason, message}. Verdicts follow the
    workflow vocabulary: advance, retry_changed, close_route, blocked_human,
    stop_unauthorized, stop_exhausted, invalid_causal, invalid_state."""
    reasons = []

    # Hard invariants --------------------------------------------------------
    delta_status = state.get("delta_status")
    cause = state.get("cause")

    if delta_status not in {
        "pending", "advanced", "no_change", "regressed", "stale_anchor",
    }:
        return {
            "verdict": "invalid_causal",
            "reason": "delta_status_not_in_vocabulary",
            "message": f"delta_status '{delta_status}' is not a causal vocabulary value.",
        }

    if cause is not None and cause not in CAUSAL_CLASSES:
        return {
            "verdict": "invalid_causal",
            "reason": "cause_not_in_vocabulary",
            "message": f"cause '{cause}' is not a causal class.",
        }

    # 1. Destructive / external / expensive / scope expansion ---------------
    proposed = state.get("proposed_action")
    if proposed in DESTRUCTIVE_ACTIONS:
        reasons.append("destructive_action_without_authorization")
        return {
            "verdict": "stop_unauthorized",
            "reason": "destructive_action_without_authorization",
            "message": (
                f"Action {proposed!r} is destructive/expensive/external and "
                "requires explicit human authorization."
            ),
        }

    # 1b. Representation mismatch is a route problem, evaluated AFTER exhaustion
    # and repetition so that a genuinely exhausted set still stops correctly.
    # Done here (before the human gate) so a false human_gate_pending written
    # on a representation blocker is dismissed.
    if cause == "representation_mismatch" and (state.get("available_routes") or []):
        reasons.append("representation_mismatch_change_representation_not_human")
        return {
            "verdict": "retry_changed_representation",
            "reason": "representation_mismatch_change_representation_not_human",
            "message": (
                "The route produced the wrong representation (dimensions, "
                "indexing or grid). This is a capability/representation "
                "failure, NOT a human decision: stamp/author in the native "
                "grid or change the producer, then retry. Do not ask a human "
                "to supply the artifact."
            ),
        }

    # 1c. A sprite can be syntactically native and still carry more semantic
    # density than the locked canvas can express.  That is not the same as a
    # malformed PNG and it is not permission to silently enlarge the asset.
    if cause == "scale_density_mismatch" and (state.get("available_routes") or []):
        scale_status = state.get("scale_lock_status")
        if scale_status == "locked":
            return {
                "verdict": "retry_changed_representation",
                "reason": "locked_scale_requires_native_reauthoring",
                "message": (
                    "The locked scale is a product constraint. Simplify and "
                    "reauthor clusters directly in that grid; a larger probe "
                    "may be evidence, never a replacement asset."
                ),
            }
        if scale_status == "provisional" and not state.get("scale_tradeoff_measured", False):
            return {
                "verdict": "retry_scale_measurement",
                "reason": "provisional_scale_tradeoff_unmeasured",
                "message": (
                    "Compare the bounded scale candidates at native 1x and "
                    "measure camera, hitbox, workload, metasprite and scanline "
                    "cost before asking for a product decision."
                ),
            }
        if (
            scale_status == "provisional"
            and state.get("scale_tradeoff_measured", False)
            and state.get("scale_product_change_required", False)
            and state.get("human_gate_pending") is None
        ):
            return {
                "verdict": "invalid_state",
                "reason": "scale_change_requires_human_gate",
                "message": (
                    "The measured alternative changes the product contract; "
                    "record a human scale decision instead of advancing silently."
                ),
            }

    # 2. Human decision required ----------------------------------------------
    # A pending human gate pauses the blocked route regardless of independent
    # branches; the branches are a separate answer of what MAY continue.
    gate = state.get("human_gate_pending")
    if gate is not None:
        reasons.append("human_decision_required")
        return {
            "verdict": "blocked_human",
            "reason": "human_decision_required",
            "message": (
                "A human decision is required. Record the exact question and "
                "options, then continue only the independent branches."
            ),
        }

    # 3. All safe / authorized routes exhausted -----------------------------
    # A closed route is removed from the safe set by design, so it is a normal
    # thing for routes_closed to contain routes absent from available_routes.
    remaining = state.get("available_routes", []) or []
    if not remaining:
        reasons.append("all_safe_routes_exhausted")
        return {
            "verdict": "stop_exhausted",
            "reason": "all_safe_routes_exhausted",
            "message": "All safe and authorized routes have been exhausted with evidence.",
        }

    # 4. Repetition: N equivalent attempts with no new evidence ---------------
    if _equivalent_attempts(state) and not _delta_measured(state):
        reasons.append("equivalent_repetition_no_new_evidence")
        return {
            "verdict": "close_route",
            "reason": "equivalent_repetition_no_new_evidence",
            "message": (
                f"{REPETITION_LIMIT} equivalent attempts produced no new "
                "evidence; close this route rather than the project."
            ),
        }

    # 5. A no-op document/build with blockers_removed=0 is not causal progress -
    if state.get("artifact_kind") == "document" and state.get("blockers_removed", 0) == 0:
        reasons.append("documentary_progress_not_causal")
        return {
            "verdict": "close_route",
            "reason": "documentary_progress_not_causal",
            "message": "A document/build with blockers_removed=0 is not causal progress.",
        }

    # 6. Blocked by the smaller claim ceiling --------------------------------
    # A global/irrelevant blocker must not stop a claim that does not depend on it.
    if state.get("blocker_relevant") is False:
        return {
            "verdict": "advance",
            "reason": "blocker_irrelevant_to_active_claim",
            "message": (
                "The blocker is irrelevant to the active claim; advance the "
                "claim without unwinding the irrelevant blocker."
            ),
        }

    # 7. Advance --------------------------------------------------------------
    if _delta_measured(state) and delta_status in {"advanced", "no_change", "regressed"}:
        return {
            "verdict": "advance",
            "reason": "delta_registered",
            "message": (
                "Delta measured; record evidence and advance (or re-classify a "
                "failure cause before retrying with a changed route)."
            ),
        }

    # Default: no decision needed, but state is valid.
    return {
        "verdict": "advance",
        "reason": "valid_state_retry_changed_route",
        "message": "State is valid; attempt one causal hypothesis and measure.",
    }


# --- CLI -------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: causal_persistence_guard.py <state.json>", file=sys.stderr)
        return 1
    try:
        with open(args[0], encoding="utf-8") as fh:
            state = json.load(fh)
        decision = decide(state)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(json.dumps(decision, indent=2, ensure_ascii=False))
    return 0 if decision["verdict"].startswith(("advance", "retry", "blocked")) else 0


if __name__ == "__main__":
    sys.exit(main())

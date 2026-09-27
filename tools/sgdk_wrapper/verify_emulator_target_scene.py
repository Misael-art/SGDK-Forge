"""Fail closed when a requested BlastEm scene was not actually observed."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def verify(metrics: dict, requested: int) -> dict:
    observed = metrics.get("scene_id")
    if observed is None and isinstance(metrics.get("vlab"), dict):
        observed = metrics["vlab"].get("scene_id")
    if isinstance(observed, bool) or not isinstance(observed, int):
        status = "needs_review"
        reason = "runtime_scene_id_missing"
    elif observed != requested:
        status = "blocked"
        reason = "runtime_target_scene_mismatch"
    else:
        status = "passed"
        reason = None
    return {"status": status, "reason": reason, "requested_scene": requested,
            "observed_scene": observed, "claim_limit":
            "Scene ID proves only the sampled capture state, not the full transition."}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--target-scene", type=int, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        metrics = {}
        error = str(exc)
    else:
        error = None
    result = verify(metrics, args.target_scene)
    if error:
        result["input_error"] = error
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

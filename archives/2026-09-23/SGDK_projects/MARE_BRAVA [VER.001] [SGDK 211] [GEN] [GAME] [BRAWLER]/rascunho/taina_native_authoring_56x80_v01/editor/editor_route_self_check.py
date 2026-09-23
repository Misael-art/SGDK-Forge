#!/usr/bin/env python3
"""Exercise the local editor API, including its negative path guards."""
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def post(base, path, payload):
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(base + path, data=raw, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=10) as res:
            return {"http": res.status, "body": json.loads(res.read().decode("utf-8"))}
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {"http": exc.code, "body": body}


def get(base, path):
    with urlopen(base + path, timeout=10) as res:
        return {"http": res.status, "body": json.loads(res.read().decode("utf-8"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--base", default="http://127.0.0.1:8765")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.project_root.resolve()
    spec_path = root / "rascunho/taina_native_authoring_56x80_v01/editor/spec/taina_idle_guard_56x80_native_spec_v01.json"
    action_path = root / "rascunho/taina_native_authoring_56x80_v01/exports/taina_idle_guard_56x80_native_authoring_v04.actions.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    action_log = json.loads(action_path.read_text(encoding="utf-8"))
    result = {"schema_version": "editor_route_self_check.v1", "route": "editor_api_save", "checks": {}}
    result["checks"]["health"] = get(args.base, "/api/health")
    result["checks"]["open_56x80_session"] = post(args.base, "/api/session", {"spec": spec})
    result["checks"]["restore_v04_action_log"] = post(args.base, "/api/restore", {"action_log": action_log})
    result["checks"]["validate_restored_session"] = post(args.base, "/api/validate", {})
    result["checks"]["export_png_and_log"] = post(args.base, "/api/export", {"name": "route_self_check_probe.png", "target_dir": "rascunho/taina_native_authoring_56x80_v01/exports"})
    result["checks"]["reject_absolute_export"] = post(args.base, "/api/export", {"name": "reject.png", "target_dir": "/tmp"})
    result["checks"]["reject_res_export"] = post(args.base, "/api/export", {"name": "reject.png", "target_dir": "res"})
    result["checks"]["reject_non_grid_session"] = post(args.base, "/api/session", {"spec": {**spec, "canvas": {**spec["canvas"], "width": 55}}})
    result["checks"]["reject_traversal_session"] = post(args.base, "/api/session", {"spec": {**spec, "export_dir": "rascunho/../res"}})
    result["checks"]["restore_after_negative_tests_open"] = post(args.base, "/api/session", {"spec": spec})
    result["checks"]["restore_after_negative_tests"] = post(args.base, "/api/restore", {"action_log": action_log})
    passed = {
        "health": result["checks"]["health"]["http"] == 200,
        "open_56x80_session": result["checks"]["open_56x80_session"]["http"] == 200,
        "restore_v04_action_log": result["checks"]["restore_v04_action_log"]["http"] == 200,
        "validate_restored_session": result["checks"]["validate_restored_session"]["http"] == 200 and result["checks"]["validate_restored_session"]["body"].get("dimensions_valid") is True,
        "export_png_and_log": result["checks"]["export_png_and_log"]["http"] == 200,
        "reject_absolute_export": result["checks"]["reject_absolute_export"]["http"] == 400,
        "reject_res_export": result["checks"]["reject_res_export"]["http"] == 400,
        "reject_non_grid_session": result["checks"]["reject_non_grid_session"]["http"] == 400,
        "reject_traversal_session": result["checks"]["reject_traversal_session"]["http"] == 400,
        "restore_after_negative_tests_open": result["checks"]["restore_after_negative_tests_open"]["http"] == 200,
        "restore_after_negative_tests": result["checks"]["restore_after_negative_tests"]["http"] == 200,
    }
    result["passed"] = sum(passed.values())
    result["total"] = len(passed)
    result["check_status"] = "passed" if all(passed.values()) else "failed"
    result["assertions"] = passed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["check_status"], "passed": result["passed"], "total": result["total"]}, ensure_ascii=False))
    raise SystemExit(0 if result["check_status"] == "passed" else 1)


if __name__ == "__main__":
    main()

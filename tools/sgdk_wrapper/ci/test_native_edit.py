#!/usr/bin/env python3
"""Small physical regression suite for the native-edit bridge."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/sgdk_wrapper"))
from forge_art import native_edit


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_spec(root: Path) -> dict:
    source = root / "data/source.png"
    Image.new("RGBA", (1, 1), (0, 0, 0, 0)).save(source)
    source_sha = sha(source)
    return {
        "schema_version": "1.0.0", "command": "native-edit",
        "asset_id": "fixture_asset", "frame_id": "fixture_frame",
        "canvas": {"width": 32, "height": 32},
        "palette": [[0, 0, 0], [34, 0, 34], [238, 136, 170]],
        "identity_source": {"path": "data/source.png", "sha256": source_sha, "role": "exclusive_visual_authority"},
        "actions": [{
            "action_id": "paint_one", "asset_id": "fixture_asset", "frame_id": "fixture_frame",
            "operation": "pencil_pixel", "region": {"x": 1, "y": 1, "w": 1, "h": 1},
            "color_index": 1, "symptom": "fixture", "visual_reference": "data/source.png",
            "before_indices": [0], "after_indices": [1], "reason": "fixture", "operator": native_edit.OPERATOR,
        }],
    }


def run(spec: dict, root: Path, output: str = "out/v11_native_edit/fixture") -> str | None:
    path = root / "actions.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    try:
        native_edit.native_edit(root, Path("actions.json"), Path(output))
    except native_edit.NativeEditError as exc:
        return exc.blocker
    return None


def move_and_mirror_checks(root: Path) -> dict[str, bool]:
    moved = base_spec(root)
    moved["actions"].append({
        "action_id": "move_one", "asset_id": "fixture_asset", "frame_id": "fixture_frame",
        "operation": "move_selection_integer", "region": {"x": 1, "y": 1, "w": 1, "h": 1},
        "dx": 1, "dy": 0, "symptom": "fixture", "visual_reference": "data/source.png",
        "before_indices": [1], "after_indices": [1], "reason": "fixture", "operator": native_edit.OPERATOR,
    })
    symmetric = base_spec(root)
    symmetric["actions"][0]["region"] = {"x": 1, "y": 1, "w": 1, "h": 1}
    symmetric["actions"].append({
        "action_id": "paint_two", "asset_id": "fixture_asset", "frame_id": "fixture_frame",
        "operation": "pencil_pixel", "region": {"x": 2, "y": 1, "w": 1, "h": 1},
        "color_index": 1, "symptom": "fixture", "visual_reference": "data/source.png",
        "before_indices": [0], "after_indices": [1], "reason": "fixture", "operator": native_edit.OPERATOR,
    })
    symmetric["actions"].append({
        "action_id": "mirror_symmetric", "asset_id": "fixture_asset", "frame_id": "fixture_frame",
        "operation": "mirror_selection", "region": {"x": 1, "y": 1, "w": 2, "h": 1},
        "axis": "horizontal", "allow_mirror": True, "symptom": "fixture",
        "visual_reference": "data/source.png", "before_indices": [1], "after_indices": [1],
        "reason": "fixture", "operator": native_edit.OPERATOR,
    })
    return {
        "move": run(moved, root, "out/v11_native_edit/move") is None,
        "mirror_noop": run(symmetric, root, "out/v11_native_edit/mirror_noop") == "action_noop",
    }


def main() -> int:
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "data").mkdir()
        (root / "res").mkdir()
        good = base_spec(root)
        checks["baseline"] = run(copy.deepcopy(good), root) is None
        malformed = copy.deepcopy(good)
        malformed["actions"][0]["operation"] = "not_allowed"
        checks["malformed_operation"] = run(malformed, root, "out/v11_native_edit/malformed") == "action_schema_invalid"
        duplicate = copy.deepcopy(good)
        duplicate["actions"].append(copy.deepcopy(duplicate["actions"][0]))
        checks["duplicate_action_id"] = run(duplicate, root, "out/v11_native_edit/duplicate") == "duplicate_action_id"
        noop = copy.deepcopy(good)
        noop["actions"][0]["before_indices"] = [0]
        noop["actions"][0]["after_indices"] = [0]
        noop["actions"][0]["color_index"] = 0
        checks["noop"] = run(noop, root, "out/v11_native_edit/noop") == "action_noop"
        checks["prohibited_write"] = run(copy.deepcopy(good), root, "res/forbidden") == "staging_only_violation"
        out = root / "out/v11_native_edit/atomic"
        atomic = copy.deepcopy(good)
        bad = copy.deepcopy(atomic["actions"][0])
        bad["action_id"] = "bad_after_good"
        bad["region"] = {"x": 32, "y": 0, "w": 1, "h": 1}
        atomic["actions"].append(bad)
        checks["atomic"] = run(atomic, root, "out/v11_native_edit/atomic") == "region_out_of_bounds" and not out.exists()
        clean = root / "out/v11_native_edit/clean"
        run(copy.deepcopy(good), root, "out/v11_native_edit/clean")
        hashes = json.loads((clean / "artifact_hashes.json").read_text())
        execution = json.loads((clean / "execution_report.json").read_text())
        checks["hash_manifest"] = hashes["execution_report_sha256"] == sha(clean / "execution_report.json") and hashes["candidate_sha256"] == sha(clean / "candidate.png")
        checks["procedural_claim_ceiling"] = execution["claim_ceiling"] == "procedural_code_probe"
        checks["never_production_eligible"] = execution["production_eligible"] is False
        checks.update(move_and_mirror_checks(root))
    failed = [name for name, ok in checks.items() if not ok]
    for name, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    print(f"native-edit physical suite: {len(checks) - len(failed)}/{len(checks)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

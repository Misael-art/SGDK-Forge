#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
SCHEMA = json.loads((ROOT / "schemas/sprite_artifact_report.schema.json").read_text())
AUDITOR = WORKSPACE / "tools/image-tools/sprite_artifact_audit.py"


def run(spec_path: Path, output: Path) -> tuple[int, dict]:
    completed = subprocess.run(
        [
            sys.executable,
            str(AUDITOR),
            "--spec",
            str(spec_path),
            "--output",
            str(output),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode, json.loads(output.read_text(encoding="utf-8"))


def main() -> int:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        sheet = Image.new("P", (48, 32), 0)
        sheet.putpalette([255, 0, 255, 0, 0, 0] + [0, 0, 0] * 254)
        for offset in (0, 24):
            for y in range(4, 30):
                for x in range(offset + 8, offset + 16):
                    sheet.putpixel((x, y), 1)
        sheet_path = root / "sheet.png"
        sheet.save(sheet_path)
        review = [{"status": "passed", "note": "complete silhouette"}] * 2
        spec = {
            "project_root": str(root),
            "asset_id": "fixture",
            "sheet": "sheet.png",
            "cell": {"w": 24, "h": 32},
            "pivot": {"x": 12, "y": 29},
            "transparent_index": 0,
            "required_actions": ["run"],
            "actions": [
                {
                    "name": "run",
                    "row": 0,
                    "start": 0,
                    "count": 2,
                    "grounded": [True, True],
                    "manual_anatomy_review": review,
                    "frame_delta_min": 0.0
                }
            ],
            "previews": {
                "contact_sheet": "contact.png",
                "animation_root": "animations"
            }
        }
        spec_path = root / "spec.json"
        output = root / "report.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        return_code, report = run(spec_path, output)
        errors = list(Draft7Validator(SCHEMA).iter_errors(report))
        assert not errors, "; ".join(error.message for error in errors)
        assert report["required_checks"]["edge_clipping"]
        assert report["required_checks"]["anatomy"]
        assert report["required_checks"]["frame_delta"]
        assert report["required_checks"]["action_coverage"]
        assert report["action_coverage"]["status"] == "passed"
        assert return_code == 0, report
        assert report["status"] == "passed"
        assert Path(root / report["evidence"]["contact_sheet"]).is_file()
        assert Path(root / report["evidence"]["animated_captures"]["run"]).is_file()

        missing_review = json.loads(json.dumps(spec))
        del missing_review["actions"][0]["manual_anatomy_review"]
        missing_spec = root / "missing_anatomy.json"
        missing_output = root / "missing_anatomy_report.json"
        missing_spec.write_text(json.dumps(missing_review), encoding="utf-8")
        return_code, failed = run(missing_spec, missing_output)
        assert return_code == 2
        assert failed["technical_pass"] is True
        assert failed["visual_pass"] is False
        assert failed["status"] == "technical_pass_visual_fail"
        assert any(
            finding["code"] == "ANATOMY_REVIEW_MISSING"
            for finding in failed["findings"]
        )

        clipped_sheet = Image.open(sheet_path)
        clipped_sheet.putpixel((0, 8), 1)
        clipped_path = root / "clipped.png"
        clipped_sheet.save(clipped_path)
        clipped = json.loads(json.dumps(spec))
        clipped["sheet"] = "clipped.png"
        clipped_spec = root / "clipped_spec.json"
        clipped_output = root / "clipped_report.json"
        clipped_spec.write_text(json.dumps(clipped), encoding="utf-8")
        return_code, failed = run(clipped_spec, clipped_output)
        assert return_code == 2
        assert failed["status"] == "technical_pass_visual_fail"
        assert any(
            finding["code"] == "FRAME_EDGE_CLIPPING"
            for finding in failed["findings"]
        )

        missing_action = json.loads(json.dumps(spec))
        missing_action["required_actions"] = ["run", "damage"]
        missing_action_spec = root / "missing_action_spec.json"
        missing_action_output = root / "missing_action_report.json"
        missing_action_spec.write_text(json.dumps(missing_action), encoding="utf-8")
        return_code, failed = run(missing_action_spec, missing_action_output)
        assert return_code == 2
        assert failed["status"] == "technical_pass_visual_fail"
        assert failed["action_coverage"]["missing_required_actions"] == ["damage"]
        assert any(
            finding["code"] == "REQUIRED_ACTION_MISSING"
            for finding in failed["findings"]
        )

    print("[PASS] sprite_artifact_report schema and six mandatory checks")
    print("[PASS] technical validity cannot override anatomy or clipping failures")
    print("[PASS] actions promised by the animation plan cannot disappear from the artifact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

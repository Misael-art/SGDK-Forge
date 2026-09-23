#!/usr/bin/env python3
"""Negative/positive contract checks for the runtime media-marker binder."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess as sp
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BINDER = ROOT / "bind_runtime_media_anchor.py"


def run_case(*, reviewer: str | None, evidence: str | None) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory(prefix="media_marker_contract_") as raw:
        bundle = Path(raw)
        (bundle / "manifest.json").write_text(json.dumps({
            "rom_sha256": "c" * 64,
            "runtime_media_marker": {"marker_id": 7, "runtime_presentation_frame": 700},
        }))
        (bundle / "analysis.json").write_text(json.dumps({
            "video": {"video_sha256": "a" * 64,
                      "events": [{"source_frame_index": 12, "video_pts_seconds": 1.0}]},
            "audio": {"audio_sha256": "b" * 64, "sample_rate_hz": 48000,
                      "events": [{"audio_sample_index": 48000, "audio_time_seconds": 1.0}]},
        }))
        (bundle / "review.png").write_bytes(b"fixture")
        command = ["python3", str(BINDER), "--manifest", str(bundle / "manifest.json"),
                   "--analysis", str(bundle / "analysis.json"),
                   "--out-manifest", str(bundle / "derived.json"), "--marker-id", "7",
                   "--video-event-index", "0", "--audio-event-index", "0"]
        command += ["--reviewer", reviewer or "", "--review-evidence", evidence or "missing.png"]
        result = sp.run(command, capture_output=True, text=True)
        payload = json.loads(result.stdout.strip())
        return result.returncode, payload


def main() -> int:
    code, payload = run_case(reviewer=None, evidence=None)
    assert code != 0 and payload["status"] == "needs_review"
    code, payload = run_case(reviewer="fixture_reviewer", evidence="review.png")
    assert code == 0 and payload["status"] == "passed"
    print("media_marker_contract: 2 passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

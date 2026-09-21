#!/usr/bin/env python3
"""Self-contained contract gate for hash-bound audiovisual review.

This is intentionally independent of a real capture.  It proves that the
wrapper can consume a qualified packet without converting metadata into
approval, and that invalid coverage/reviewer packets remain blocked.
"""
from __future__ import annotations

import importlib.util
import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "audiovisual_review.py"
SPEC = importlib.util.spec_from_file_location("audiovisual_review", TOOL)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def base_report(*, temporal: str = "passed", sync: str = "passed") -> dict:
    return {
        "artifacts": {
            "video": {"master_preserved": True, "sha256": "a" * 64, "duration_seconds": 10.0},
            "audio": {"master_preserved": True, "sha256": "b" * 64},
        },
        "manifest": {"rom_sha256": "c" * 64},
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": temporal},
        "synchronization": {"status": sync, "measured_event_sync_error_ms": 1 if sync == "passed" else None},
        "game_cadence": {"status": "passed", "reason": "fixture HCAD invariant"},
    }


def qualified_event_review(**overrides: object) -> dict:
    review = {
        "reviewer": "qualified_fixture_reviewer",
        "method": "sequential_frame_review_with_hash_bound_runtime_context",
        "evidence_root": str(TOOL.parent),
        "tools": ["ffprobe", "ffmpeg", "frame_sequence_inspector"],
        "method_capabilities": {"images_only": True, "video_playback": False, "audio_audition": False},
        "source_media": {"video_sha256": "a" * 64, "audio_sha256": "b" * 64, "rom_sha256": "c" * 64},
        "observed_intervals": [{
            "event_id": "special",
            "start_seconds": 2.0,
            "end_seconds": 4.0,
            "actually_seen": True,
            "evidence_refs": ["audiovisual_review.py"],
        }],
        "coverage": {"unexamined_intervals": ["0-2", "4-10"], "coverage_ratio": 0.2},
        "verdicts": {
            "visual_quality": {"status": "passed", "evidence_refs": ["audiovisual_review.py"]},
            "motion_quality": {"status": "needs_review", "evidence_refs": ["audiovisual_review.py"]},
            "audio_quality": {"status": "needs_review", "evidence_refs": ["audiovisual_review.py"]},
        },
    }
    review.update(overrides)
    return review


def test_axes_are_independent() -> None:
    result = MODULE.evaluate_gate(base_report(temporal="failed", sync="needs_review"))
    assert result["claims"]["artifact_identity"] == "released"
    assert result["claims"]["media_temporal_integrity"] == "blocked"
    assert result["claims"]["game_cadence"] == "released"
    assert result["claims"]["visual_approval"] == "blocked"


def test_qualified_event_review_releases_only_supported_visual_scope() -> None:
    result = MODULE.evaluate_gate(base_report(temporal="failed", sync="needs_review"), qualified_event_review())
    assert result["review_validation"]["qualified"] is True
    assert result["review_validation"]["coverage"]["coverage_ratio"] == 0.2
    assert result["claims"]["visual_approval"] == "released"
    assert result["claims"]["temporal_motion_approval"] == "blocked"
    assert result["claims"]["audio_approval"] == "blocked"
    assert result["claims"]["coverage_complete"] == "blocked"
    assert result["claim_scopes"]["visual_approval"] == "unspecified"
    assert result["claim_scopes"]["temporal_motion_approval"] == "none"
    assert result["claim_scopes"]["audio_approval"] == "none"


def test_missing_review_and_invalid_coverage_block_claims() -> None:
    no_review = MODULE.evaluate_gate(base_report())
    assert no_review["claims"]["visual_approval"] == "blocked"
    assert no_review["claims"]["coverage_complete"] == "blocked"

    invalid = qualified_event_review(coverage={"unexamined_intervals": ["not-an-interval"]})
    result = MODULE.evaluate_gate(base_report(), invalid)
    assert result["review_validation"]["qualified"] is False
    assert "unexamined_interval_0_invalid" in result["review_validation"]["errors"]
    assert result["claims"]["coverage_complete"] == "blocked"
    assert result["claims"]["visual_approval"] == "blocked"


def test_qualified_review_requires_resolvable_evidence_refs() -> None:
    invalid = qualified_event_review(
        observed_intervals=[{
            "event_id": "special",
            "start_seconds": 2.0,
            "end_seconds": 4.0,
            "actually_seen": True,
            "evidence_refs": ["missing_evidence.json"],
        }]
    )
    result = MODULE.evaluate_gate(base_report(), invalid)
    assert result["review_validation"]["qualified"] is False
    assert "observed_interval_0_evidence_ref_0_missing" in result["review_validation"]["errors"]
    assert result["claims"]["visual_approval"] == "blocked"


def test_v5_consumer_requires_hashes_and_finding_query_binding() -> None:
    with tempfile.TemporaryDirectory(prefix="audiovisual_v5_contract_") as raw:
        root = Path(raw)
        bundle = root / "bundle"
        review_dir = root / "review"
        bundle.mkdir()
        review_dir.mkdir()
        (bundle / "video.bin").write_bytes(b"video")
        (bundle / "audio.bin").write_bytes(b"audio")
        (bundle / "rom.bin").write_bytes(b"rom")
        (review_dir / "seen.txt").write_text("seen\n", encoding="utf-8")
        video_sha = MODULE.sha256(bundle / "video.bin")
        audio_sha = MODULE.sha256(bundle / "audio.bin")
        rom_sha = MODULE.sha256(bundle / "rom.bin")
        files = {
            "freeze": {"stage": "V0_freeze", "rom": {"sha256": rom_sha}, "frozen_rom": {"sha256": rom_sha}},
            "capture": {"rom_sha256": rom_sha, "video": "video.bin", "audio_wav": "audio.bin"},
            "ingest": {"stage": "V1_ingest_integrity", "manifest": {"rom_sha256": rom_sha},
                       "artifacts": {"video": {"sha256": video_sha, "master_preserved": True, "duration_seconds": 1.0},
                                     "audio": {"sha256": audio_sha, "master_preserved": True}},
                       "artifact_identity": {"status": "passed"},
                       "media_temporal_integrity": {"status": "passed"},
                       "synchronization": {"status": "needs_review"},
                       "game_cadence": {"status": "passed", "reason": "fixture"}},
            "query": {"stage": "V2_query", "source_video_sha256": video_sha,
                      "interval": {"start_seconds": 0.0, "end_seconds": 1.0},
                      "requested_frame_count": 1, "decoded_frame_count": 1, "frame_count_match": True,
                      "source_frame_index_range": {"first": 0, "last": 0},
                      "extraction": {"exact_source_binding": True, "no_cfr": True,
                                     "no_interpolation": True, "no_duplicate_removal": True}},
            "finding": {"stage": "V3_findings", "findings": [{
                "status": "candidate", "approval_status": "not_approved",
                "timestamp": {"start_seconds": 0.1, "end_seconds": 0.2}, "confidence": 0.8,
                "hypothesis": "fixture", "impact": "fixture", "causal_test": "fixture",
                "routing": {"owner": "fixture", "next_action": "fixture"},
                "frame_context": {"source_query": "query.json", "source_frame_first": 0, "source_frame_last": 0},
                "media_sha256": video_sha, "audio_sha256": audio_sha}]},
        }
        overhead = {
            "status": "measured", "same_rom_sha256": True,
            "cases": [{"rom_sha256": rom_sha}, {"rom_sha256": rom_sha}],
            "successful_pairs": [{"repetition": 1}, {"repetition": 2}],
            "observed_overhead": {
                "cadence_telemetry_complete": True,
                "phase_medians": {phase: {"delta_median_ms": 1.0}
                                   for phase in ("boot_ms", "capture_ms", "finalization_ms", "total_ms")},
            },
        }
        review = qualified_event_review()
        review.update({"evidence_root": ".", "source_media": {"video_sha256": video_sha,
                       "audio_sha256": audio_sha, "rom_sha256": rom_sha},
                       "observed_intervals": [{"event_id": "fixture", "start_seconds": 0,
                       "end_seconds": 1, "actually_seen": True, "evidence_refs": ["seen.txt"]}],
                       "coverage": {"unexamined_intervals": [], "coverage_ratio": 1.0},
                       "verdicts": {axis: {"status": "needs_review", "evidence_refs": ["seen.txt"]}
                                    for axis in ("visual_quality", "motion_quality", "audio_quality")}})
        paths = {}
        for name, value in files.items():
            path = root / f"{name}.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            paths[name] = path
        overhead_path = root / "overhead.json"
        overhead_path.write_text(json.dumps(overhead), encoding="utf-8")
        capture_path = bundle / "manifest.json"
        capture_path.write_text(json.dumps(files["capture"]), encoding="utf-8")
        review_path = review_dir / "review.json"
        review_path.write_text(json.dumps(review), encoding="utf-8")
        review_for_gate = dict(review)
        review_for_gate["_manifest_dir"] = str(review_dir)
        gate_path = root / "gate.json"
        gate_path.write_text(json.dumps(MODULE.evaluate_gate(files["ingest"], review_for_gate)), encoding="utf-8")
        args = type("Args", (), {"freeze": str(paths["freeze"]), "capture_manifest": str(capture_path),
                                  "ingest": str(paths["ingest"]), "query": str(paths["query"]),
                                  "finding": str(paths["finding"]), "review": str(review_path),
                                  "gate": str(gate_path), "overhead": str(overhead_path),
                                  "out": str(root / "v5.json")})()
        with redirect_stdout(io.StringIO()):
            assert MODULE.end_to_end(args) == 0
        result = json.loads((root / "v5.json").read_text(encoding="utf-8"))
        assert result["execution_status"] == "passed"
        assert result["status"] == "blocked"
        assert result["steps"]["finding_query_binding"]["status"] == "passed"
        assert result["steps"]["capture_overhead"]["status"] == "passed"

        bad_review = dict(review, reviewer=None)
        bad_review_path = review_dir / "bad_review.json"
        bad_review_path.write_text(json.dumps(bad_review), encoding="utf-8")
        bad_review_for_gate = dict(bad_review)
        bad_review_for_gate["_manifest_dir"] = str(review_dir)
        bad_gate_path = root / "bad_gate.json"
        bad_gate_path.write_text(json.dumps(MODULE.evaluate_gate(files["ingest"], bad_review_for_gate)), encoding="utf-8")
        bad_args = type("Args", (), {"freeze": str(paths["freeze"]), "capture_manifest": str(capture_path),
                                      "ingest": str(paths["ingest"]), "query": str(paths["query"]),
                                      "finding": str(paths["finding"]), "review": str(bad_review_path),
                                      "gate": str(bad_gate_path), "out": str(root / "bad_v5.json")})()
        with redirect_stdout(io.StringIO()):
            assert MODULE.end_to_end(bad_args) == 2


def main() -> int:
    tests = [test_axes_are_independent, test_qualified_event_review_releases_only_supported_visual_scope,
             test_missing_review_and_invalid_coverage_block_claims,
             test_qualified_review_requires_resolvable_evidence_refs,
             test_v5_consumer_requires_hashes_and_finding_query_binding]
    for test in tests:
        test()
    print(f"audiovisual_review_contract: {len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

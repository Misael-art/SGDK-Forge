#!/usr/bin/env python3
"""Regression tests for the audiovisual gate; no threshold is tuned to a bundle."""
from __future__ import annotations

import importlib.util
import json
from argparse import Namespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT.parents[1] / "tools" / "sgdk_wrapper" / "audiovisual_review.py"
EVIDENCE_ROOT = str(TOOL.parent)
EVIDENCE_REF = "audiovisual_review.py"
REVIEW_PROTOCOL = {
    "schema_version": "2.3.0",
    "generated_at": "2026-09-22T00:00:00Z",
    "tool_name": "audiovisual_review",
    "tool_version": "2.6.0",
}


def review_verdicts(status: str, evidence_ref: str = EVIDENCE_REF) -> dict:
    return {
        "event_observed": {"status": status, "evidence_refs": [evidence_ref]},
        "visual_legibility": {"status": status, "evidence_refs": [evidence_ref]},
        "visual_quality": {
            "status": status,
            "evidence_refs": [evidence_ref],
            "criteria_checked": ["native_320x224_readability", "silhouette_and_material_separation"],
            "reference_comparison": {"status": status, "evidence_refs": [evidence_ref]},
        },
        "motion_quality": {"status": status, "evidence_refs": [evidence_ref]},
        "audio_quality": {"status": status, "evidence_refs": [evidence_ref]},
    }
spec = importlib.util.spec_from_file_location("audiovisual_review", TOOL)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_fixture_axes_remain_separate() -> None:
    cases = json.loads((ROOT / "tests/fixtures/audiovisual_review/cases.json").read_text(encoding="utf-8"))
    for case in cases:
        result = module.evaluate_gate(case["report"])
        for axis, expected in case["expected"].items():
            assert result["axes"][axis]["status"] == expected, (case["id"], result)
        assert result["claims"]["visual_approval"] == "blocked"
        assert result["claims"]["audio_approval"] == "blocked"


def test_query_context_is_segmented_without_relabeling_event_frames() -> None:
    assert module.query_segment(9.9, 10.0, 11.0) == "pre_context"
    assert module.query_segment(10.0, 10.0, 11.0) == "event"
    assert module.query_segment(11.0, 10.0, 11.0) == "event"
    assert module.query_segment(11.1, 10.0, 11.0) == "post_context"


def test_query_selector_binds_contiguous_source_indices_without_seek_ordinal() -> None:
    expression = module._ffmpeg_select_expression([620, 621, 622])
    assert expression == r"select=between(n\,620\,622)"
    sparse = module._ffmpeg_select_expression([620, 622])
    assert sparse == r"select=eq(n\,620)+eq(n\,622)"


def test_no_review_cannot_release_temporal_claim() -> None:
    report = {
        "artifacts": {"video": {"master_preserved": True, "duration_seconds": 1}, "audio": {"master_preserved": True}},
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": "passed"},
        "synchronization": {"status": "needs_review"},
        "game_cadence": {"status": "unsupported"},
    }
    result = module.evaluate_gate(report)
    assert result["claims"]["temporal_motion_approval"] == "blocked"
    assert result["claims"]["audio_approval"] == "blocked"


def test_historical_empty_v5_review_packet_is_not_coverage() -> None:
    report = {
        "artifacts": {"video": {"master_preserved": True, "sha256": "video", "duration_seconds": 10},
                      "audio": {"master_preserved": True, "sha256": "audio"}},
        "manifest": {"rom_sha256": "rom"},
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": "passed"},
        "synchronization": {"status": "needs_review"},
        "game_cadence": {"status": "passed"},
    }
    review = {
        **REVIEW_PROTOCOL,
        "reviewer": None,
        "method": "indexed_only",
        "evidence_root": EVIDENCE_ROOT,
        "tools": ["ffprobe"],
        "method_capabilities": {"video_playback": False, "audio_audition": False},
        "source_media": {"video_sha256": "video", "audio_sha256": "audio", "rom_sha256": "rom"},
        "observed_intervals": [],
        "coverage": {"unexamined_intervals": ["0-10"], "coverage_ratio": 0},
        "verdicts": {
            "event_observed": {"status": "needs_review", "evidence_refs": [EVIDENCE_REF]},
            "visual_legibility": {"status": "needs_review", "evidence_refs": [EVIDENCE_REF]},
            "visual_quality": {"status": "needs_review", "evidence_refs": [EVIDENCE_REF]},
            "motion_quality": {"status": "needs_review", "evidence_refs": [EVIDENCE_REF]},
            "audio_quality": {"status": "needs_review", "evidence_refs": [EVIDENCE_REF]},
        },
    }
    result = module.evaluate_gate(report, review)
    assert result["review_validation"]["qualified"] is False
    assert "reviewer_missing" in result["review_validation"]["errors"]
    assert "observed_intervals_missing_or_empty" in result["review_validation"]["errors"]
    assert result["claims"]["coverage_complete"] == "blocked"
    assert result["claims"]["visual_approval"] == "blocked"


def test_null_coverage_is_rejected_even_with_review_fields() -> None:
    report = {
        "artifacts": {"video": {"master_preserved": True, "sha256": "video", "duration_seconds": 1},
                      "audio": {"master_preserved": True, "sha256": "audio"}},
        "manifest": {"rom_sha256": "rom"},
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": "passed"},
        "synchronization": {"status": "passed", "measured_event_sync_error_ms": 2},
        "game_cadence": {"status": "passed"},
    }
    review = {
        **REVIEW_PROTOCOL,
        "reviewer": "qualified-reviewer",
        "method": "playback_and_audition",
        "evidence_root": EVIDENCE_ROOT,
        "tools": ["ffplay", "ffprobe", "audition_log"],
        "method_capabilities": {"video_playback": True, "audio_audition": True},
        "source_media": {"video_sha256": "video", "audio_sha256": "audio", "rom_sha256": "rom"},
        "observed_intervals": [{"event_id": "all", "start_seconds": 0, "end_seconds": 1,
                                "actually_seen": True, "evidence_refs": [EVIDENCE_REF]}],
        "coverage": {"unexamined_intervals": None, "coverage_ratio": 1.0},
        "verdicts": review_verdicts("passed"),
    }
    result = module.evaluate_gate(report, review)
    assert "unexamined_intervals_must_be_list" in result["review_validation"]["errors"]
    assert result["axes"]["coverage"]["status"] == "needs_review"
    assert result["claims"]["visual_approval"] == "blocked"


def test_qualified_review_can_release_only_supported_axes() -> None:
    report = {
        "artifacts": {"video": {"master_preserved": True, "sha256": "video", "duration_seconds": 1},
                      "audio": {"master_preserved": True, "sha256": "audio"}},
        "manifest": {"rom_sha256": "rom"},
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": "passed"},
        "synchronization": {"status": "passed", "measured_event_sync_error_ms": 2},
        "game_cadence": {"status": "passed"},
    }
    review = {
        **REVIEW_PROTOCOL,
        "reviewer": "qualified-reviewer",
        "method": "playback_and_audition",
        "evidence_root": EVIDENCE_ROOT,
        "tools": ["ffplay", "ffprobe", "audition_log"],
        "method_capabilities": {"video_playback": True, "audio_audition": True},
        "source_media": {"video_sha256": "video", "audio_sha256": "audio", "rom_sha256": "rom"},
        "observed_intervals": [{"event_id": "all", "start_seconds": 0, "end_seconds": 1,
                                "actually_seen": True, "evidence_refs": [EVIDENCE_REF]}],
        "coverage": {"unexamined_intervals": [], "coverage_ratio": 1.0},
        "verdicts": review_verdicts("passed"),
    }
    result = module.evaluate_gate(report, review)
    assert result["review_validation"]["qualified"] is True
    assert result["axes"]["visual_quality"]["status"] == "passed"
    assert result["axes"]["motion_quality"]["status"] == "passed"
    assert result["axes"]["audio_quality"]["status"] == "passed"
    assert result["axes"]["coverage"]["status"] == "passed"
    assert result["claims"]["visual_approval"] == "released"
    assert result["claims"]["temporal_motion_approval"] == "released"
    assert result["claims"]["audio_approval"] == "released"


def test_invalid_unexamined_interval_cannot_release_coverage() -> None:
    report = {
        "artifacts": {"video": {"master_preserved": True, "sha256": "video", "duration_seconds": 10},
                      "audio": {"master_preserved": True, "sha256": "audio"}},
        "manifest": {"rom_sha256": "rom"},
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": "passed"},
        "synchronization": {"status": "passed", "measured_event_sync_error_ms": 1},
        "game_cadence": {"status": "passed"},
    }
    review = {
        **REVIEW_PROTOCOL,
        "reviewer": "qualified-reviewer",
        "method": "playback_and_audition",
        "evidence_root": EVIDENCE_ROOT,
        "method_capabilities": {"video_playback": True, "audio_audition": True},
        "source_media": {"video_sha256": "video", "audio_sha256": "audio", "rom_sha256": "rom"},
        "observed_intervals": [{"event_id": "partial", "start_seconds": 0, "end_seconds": 3,
                                "actually_seen": True, "evidence_refs": [EVIDENCE_REF]}],
        "coverage": {"unexamined_intervals": [{"start_seconds": 5, "end_seconds": 4}],
                     "coverage_ratio": 0.3},
        "verdicts": review_verdicts("passed"),
    }
    result = module.evaluate_gate(report, review)
    assert result["review_validation"]["qualified"] is False
    assert "unexamined_interval_0_invalid" in result["review_validation"]["errors"]
    assert "unexamined_intervals_do_not_match_observed_complement" in result["review_validation"]["errors"]
    assert result["claims"]["coverage_complete"] == "blocked"
    assert result["claims"]["visual_approval"] == "blocked"


def test_qualified_packet_requires_capability_flags_and_verdict_evidence() -> None:
    report = {
        "artifacts": {"video": {"master_preserved": True, "sha256": "video", "duration_seconds": 1},
                      "audio": {"master_preserved": True, "sha256": "audio"}},
        "manifest": {"rom_sha256": "rom"},
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": "passed"},
        "synchronization": {"status": "passed", "measured_event_sync_error_ms": 1},
        "game_cadence": {"status": "passed"},
    }
    review = {
        **REVIEW_PROTOCOL,
        "reviewer": "qualified-reviewer",
        "method": "image_sequence_only",
        "evidence_root": EVIDENCE_ROOT,
        "tools": ["ffprobe", "view_image"],
        "method_capabilities": {"images_only": True},
        "source_media": {"video_sha256": "video", "audio_sha256": "audio", "rom_sha256": "rom"},
        "observed_intervals": [{"event_id": "all", "start_seconds": 0, "end_seconds": 1,
                                "actually_seen": True, "evidence_refs": [EVIDENCE_REF]}],
        "coverage": {"unexamined_intervals": [], "coverage_ratio": 1.0},
        "verdicts": {
            "event_observed": {"status": "passed", "evidence_refs": [EVIDENCE_REF]},
            "visual_legibility": {"status": "passed", "evidence_refs": [EVIDENCE_REF]},
            "visual_quality": {"status": "passed", "evidence_refs": [EVIDENCE_REF]},
            "motion_quality": {"status": "needs_review"},
            "audio_quality": {"status": "needs_review", "evidence_refs": [EVIDENCE_REF]},
        },
    }
    result = module.evaluate_gate(report, review)
    assert result["review_validation"]["qualified"] is False
    assert "method_capability_video_playback_missing_or_invalid" in result["review_validation"]["errors"]
    assert "method_capability_audio_audition_missing_or_invalid" in result["review_validation"]["errors"]
    assert "verdict_motion_quality_evidence_missing" in result["review_validation"]["errors"]
    assert result["claims"]["visual_approval"] == "blocked"


def test_game_cadence_does_not_release_media_temporal_integrity() -> None:
    report = {
        "artifacts": {"video": {"master_preserved": True, "sha256": "video", "duration_seconds": 1},
                      "audio": {"master_preserved": True, "sha256": "audio"}},
        "manifest": {"rom_sha256": "rom"},
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": "failed", "pts_gap_count": 1},
        "synchronization": {"status": "needs_review"},
        "game_cadence": {"status": "passed", "probe": {"cadence_invariant": True}},
    }
    result = module.evaluate_gate(report)
    assert result["axes"]["game_cadence"]["status"] == "passed"
    assert result["axes"]["media_temporal_integrity"]["status"] == "failed"
    assert result["claims"]["game_cadence"] == "released"
    assert result["claims"]["media_temporal_integrity"] == "blocked"


def test_host_capture_clock_is_not_a_shared_av_anchor() -> None:
    video = {"sha256": "a" * 64}
    audio = {"sha256": "b" * 64}
    result = module.shared_runtime_anchor_from_manifest(
        {"capture_clock": {"video_started_monotonic_ns": 123}}, video, audio, "c" * 64)
    assert result["status"] == "needs_review"
    assert result["rejected_host_clock"] is True
    assert result["measured_event_sync_error_ms"] is None


def test_shared_anchor_requires_hashes_and_runtime_video_audio_bindings() -> None:
    manifest = {
        "runtime_media_anchor": {
            "marker_id": "fixture-001",
            "runtime_presentation_frame": 120,
            "video_source_frame_index": 118,
            "video_pts_seconds": 1.966667,
            "audio_sample_index": 94400,
            "audio_sample_rate_hz": 48000,
            "measured_event_sync_error_ms": 0.25,
            "video_sha256": "a" * 64,
            "audio_sha256": "b" * 64,
            "rom_sha256": "c" * 64,
            "evidence_refs": ["marker.json"],
        }
    }
    result = module.shared_runtime_anchor_from_manifest(
        manifest, {"sha256": "a" * 64}, {"sha256": "b" * 64}, "c" * 64)
    assert result["status"] == "passed"
    assert result["event_anchor"].startswith("shared_runtime_marker")
    assert result["measured_event_sync_error_ms"] == 0.25


def test_unqualified_marker_binding_cannot_release_sync() -> None:
    manifest = {
        "runtime_media_anchor": {
            "marker_id": "fixture-001", "runtime_presentation_frame": 120,
            "video_source_frame_index": 118, "video_pts_seconds": 1.966667,
            "audio_sample_index": 94400, "audio_sample_rate_hz": 48000,
            "measured_event_sync_error_ms": 0.25,
            "video_sha256": "a" * 64, "audio_sha256": "b" * 64,
            "rom_sha256": "c" * 64, "evidence_refs": ["marker.json"],
        },
        "runtime_media_anchor_binding": {"status": "needs_review", "errors": ["reviewer_missing"]},
    }
    result = module.shared_runtime_anchor_from_manifest(
        manifest, {"sha256": "a" * 64}, {"sha256": "b" * 64}, "c" * 64)
    assert result["status"] == "needs_review"
    assert result["reason"] == "runtime_media_anchor_binding_not_qualified"


def test_review_manifest_schema_exists_and_requires_observation_contract() -> None:
    schema_path = ROOT.parents[1] / "tools" / "sgdk_wrapper" / "schemas" / "audiovisual_review_manifest.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["title"] == "SGDK Audiovisual Qualified Review Manifest"
    assert "tools" in schema["required"]
    assert "evidence_root" in schema["required"]
    assert "observed_intervals" in schema["required"]
    assert "coverage" in schema["required"]
    assert schema["properties"]["method_capabilities"]["required"] == ["video_playback", "audio_audition"]


def test_v5_end_to_end_consumes_qualified_review_but_keeps_blocked_claims(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    review_dir = tmp_path / "review"
    bundle.mkdir()
    review_dir.mkdir()
    (bundle / "video.bin").write_bytes(b"video-master")
    (bundle / "audio.bin").write_bytes(b"audio-master")
    (bundle / "rom.bin").write_bytes(b"rom-master")
    seen = review_dir / "seen.txt"
    seen.write_text("qualified fixture evidence\n", encoding="utf-8")
    video_sha = module.sha256(bundle / "video.bin")
    audio_sha = module.sha256(bundle / "audio.bin")
    rom_sha = module.sha256(bundle / "rom.bin")

    freeze = {"stage": "V0_freeze", "rom": {"sha256": rom_sha},
              "frozen_rom": {"sha256": rom_sha}}
    capture = {"rom_sha256": rom_sha, "video": "video.bin", "audio_wav": "audio.bin"}
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
    ingest = {
        "stage": "V1_ingest_integrity",
        "manifest": {"rom_sha256": rom_sha},
        "artifacts": {
            "video": {"sha256": video_sha, "master_preserved": True, "duration_seconds": 1.0},
            "audio": {"sha256": audio_sha, "master_preserved": True},
        },
        "artifact_identity": {"status": "passed"},
        "media_temporal_integrity": {"status": "passed"},
        "synchronization": {"status": "needs_review"},
        "game_cadence": {"status": "passed", "reason": "fixture HCAD", "claim_limit": "fixture only"},
    }
    query = {
        "stage": "V2_query", "source_video_sha256": video_sha,
        "interval": {"start_seconds": 0.0, "end_seconds": 1.0},
        "requested_frame_count": 1, "decoded_frame_count": 1, "frame_count_match": True,
        "extraction": {"exact_source_binding": True, "no_cfr": True,
                       "no_interpolation": True, "no_duplicate_removal": True},
    }
    finding = {
        "stage": "V3_findings", "findings": [{
            "status": "candidate", "approval_status": "not_approved",
            "timestamp": {"start_seconds": 0.1, "end_seconds": 0.2},
            "confidence": 0.8, "hypothesis": "fixture hypothesis",
            "impact": "fixture impact", "causal_test": "fixture test",
            "routing": {"owner": "fixture-owner", "next_action": "fixture-action"},
            "frame_context": {"source_query": "query.json", "source_frame_first": 0,
                               "source_frame_last": 0},
            "media_sha256": video_sha, "audio_sha256": audio_sha,
        }],
    }
    review = {
        **REVIEW_PROTOCOL,
        "reviewer": "fixture-reviewer", "method": "image_sequence_only", "evidence_root": ".",
        "tools": ["view_image"],
        "method_capabilities": {"video_playback": False, "audio_audition": False},
        "source_media": {"video_sha256": video_sha, "audio_sha256": audio_sha, "rom_sha256": rom_sha},
        "observed_intervals": [{"event_id": "fixture", "start_seconds": 0, "end_seconds": 1,
                                "actually_seen": True, "evidence_refs": ["seen.txt"]}],
        "coverage": {"unexamined_intervals": [], "coverage_ratio": 1.0},
        "verdicts": review_verdicts("needs_review", "seen.txt"),
    }
    paths = {
        "freeze": tmp_path / "freeze.json", "capture": bundle / "manifest.json",
        "overhead": tmp_path / "overhead.json",
        "ingest": tmp_path / "ingest.json", "query": tmp_path / "query.json",
        "finding": tmp_path / "finding.json", "review": review_dir / "review.json",
        "gate": tmp_path / "gate.json", "out": tmp_path / "v5.json",
    }
    for path, value in ((paths["freeze"], freeze), (paths["capture"], capture),
                        (paths["overhead"], overhead),
                        (paths["ingest"], ingest), (paths["query"], query),
                        (paths["finding"], finding), (paths["review"], review)):
        path.write_text(json.dumps(value), encoding="utf-8")
    review_for_gate = dict(review)
    review_for_gate["_manifest_dir"] = str(review_dir)
    paths["gate"].write_text(json.dumps(module.evaluate_gate(ingest, review_for_gate)), encoding="utf-8")
    args = Namespace(freeze=str(paths["freeze"]), capture_manifest=str(paths["capture"]),
                     ingest=str(paths["ingest"]), query=str(paths["query"]),
                     finding=str(paths["finding"]), review=str(paths["review"]),
                     gate=str(paths["gate"]), overhead=str(paths["overhead"]), out=str(paths["out"]))
    assert module.end_to_end(args) == 0
    result = json.loads(paths["out"].read_text(encoding="utf-8"))
    assert result["execution_status"] == "passed"
    assert result["status"] == "blocked"
    assert result["steps"]["qualified_review"]["status"] == "passed"
    assert result["steps"]["capture_overhead"]["status"] == "passed"
    assert result["steps"]["capture_overhead"]["rom_binding"] is True
    assert result["claims"]["visual_approval"] == "blocked"

    bad_overhead = dict(overhead)
    bad_overhead["cases"] = [{"rom_sha256": "d" * 64}, {"rom_sha256": "d" * 64}]
    bad_overhead_path = tmp_path / "bad_overhead.json"
    bad_overhead_path.write_text(json.dumps(bad_overhead), encoding="utf-8")
    bad_overhead_args = Namespace(**{**vars(args), "overhead": str(bad_overhead_path),
                                     "out": str(tmp_path / "bad_overhead_v5.json")})
    assert module.end_to_end(bad_overhead_args) == 2
    bad_overhead_result = json.loads(Path(bad_overhead_args.out).read_text(encoding="utf-8"))
    assert "capture_overhead_rom_hash_mismatch_or_missing" in bad_overhead_result["blocking_errors"]

    bad_review = dict(review)
    bad_review["reviewer"] = None
    bad_review_path = review_dir / "bad_review.json"
    bad_review_path.write_text(json.dumps(bad_review), encoding="utf-8")
    bad_gate_path = tmp_path / "bad_gate.json"
    bad_review_for_gate = dict(bad_review)
    bad_review_for_gate["_manifest_dir"] = str(review_dir)
    bad_gate_path.write_text(json.dumps(module.evaluate_gate(ingest, bad_review_for_gate)), encoding="utf-8")
    bad_args = Namespace(**{**vars(args), "review": str(bad_review_path),
                            "gate": str(bad_gate_path), "out": str(tmp_path / "bad_v5.json")})
    assert module.end_to_end(bad_args) == 2
    bad_result = json.loads(Path(bad_args.out).read_text(encoding="utf-8"))
    assert "qualified_review_missing_or_invalid" in bad_result["blocking_errors"]

    legacy_capture = dict(capture)
    legacy_capture["capture_integrity"] = "released"
    legacy_capture_path = bundle / "legacy_manifest.json"
    legacy_capture_path.write_text(json.dumps(legacy_capture), encoding="utf-8")
    legacy_args = Namespace(**{**vars(args), "capture_manifest": str(legacy_capture_path),
                               "out": str(tmp_path / "legacy_v5.json")})
    assert module.end_to_end(legacy_args) == 2
    legacy_result = json.loads(Path(legacy_args.out).read_text(encoding="utf-8"))
    assert "deprecated_capture_integrity_claim_present" in legacy_result["blocking_errors"]

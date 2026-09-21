#!/usr/bin/env python3
"""Bind a reviewed marker selection to runtime, video PTS and audio samples.

The selection is explicit because automatic detection is only a candidate.  A
derived manifest is written; the preserved capture manifest is never replaced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--out-manifest", required=True)
    parser.add_argument("--marker-id", type=int, required=True)
    parser.add_argument("--video-event-index", type=int, required=True)
    parser.add_argument("--audio-event-index", type=int, required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--review-evidence", required=True,
                        help="existing frame/audio evidence reviewed for this marker selection")
    parser.add_argument("--max-error-ms", type=float, default=40.0)
    args = parser.parse_args()
    manifest_path = Path(args.manifest).resolve()
    analysis_path = Path(args.analysis).resolve()
    output_path = Path(args.out_manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    marker = manifest.get("runtime_media_marker")
    video = analysis.get("video", {}); audio = analysis.get("audio", {})
    video_events = video.get("events", []); audio_events = audio.get("events", [])
    errors = []
    evidence_path = (manifest_path.parent / args.review_evidence).resolve()
    try:
        evidence_path.relative_to(manifest_path.parent)
    except ValueError:
        errors.append("review_evidence_outside_bundle")
    if not evidence_path.is_file():
        errors.append("review_evidence_missing")
    if not args.reviewer.strip():
        errors.append("reviewer_missing")
    if not isinstance(marker, dict): errors.append("runtime_media_marker_missing")
    if not (0 <= args.video_event_index < len(video_events)): errors.append("video_event_selection_invalid")
    if not (0 <= args.audio_event_index < len(audio_events)): errors.append("audio_event_selection_invalid")
    if isinstance(marker, dict) and marker.get("marker_id") != args.marker_id:
        errors.append("runtime_marker_id_mismatch")
    try:
        selected_video = video_events[args.video_event_index]
        selected_audio = audio_events[args.audio_event_index]
        error_ms = abs(float(selected_video["video_pts_seconds"]) -
                       float(selected_audio["audio_time_seconds"])) * 1000.0
    except (IndexError, KeyError, TypeError, ValueError):
        selected_video = {}; selected_audio = {}; error_ms = math.inf
        errors.append("selected_event_numeric_binding_invalid")
    if not math.isfinite(error_ms): errors.append("measured_sync_error_non_finite")
    if error_ms > args.max_error_ms: errors.append("measured_sync_error_over_limit")
    # The manifest does not have to know media paths to be useful; analysis
    # hashes are authoritative for this derived binding.
    anchor = {
        "marker_id": args.marker_id,
        "method": "explicit_reviewed_marker_selection",
        "runtime_presentation_frame": marker.get("runtime_presentation_frame") if isinstance(marker, dict) else None,
        "video_source_frame_index": selected_video.get("source_frame_index"),
        "video_pts_seconds": selected_video.get("video_pts_seconds"),
        "audio_sample_index": selected_audio.get("audio_sample_index"),
        "audio_sample_rate_hz": audio.get("sample_rate_hz"),
        "measured_event_sync_error_ms": error_ms if math.isfinite(error_ms) else None,
        "video_sha256": video.get("video_sha256"), "audio_sha256": audio.get("audio_sha256"),
        "rom_sha256": manifest.get("rom_sha256"),
        "evidence_refs": [analysis_path.name, manifest_path.name, args.review_evidence],
        "reviewer": args.reviewer,
    }
    derived = dict(manifest)
    derived["runtime_media_anchor"] = anchor
    derived["runtime_media_anchor_binding"] = {"status": "passed" if not errors else "needs_review",
        "errors": errors, "source_manifest": manifest_path.name,
        "selection": {"video_event_index": args.video_event_index,
                       "audio_event_index": args.audio_event_index,
                       "max_error_ms": args.max_error_ms,
                       "reviewer": args.reviewer,
                       "review_evidence": args.review_evidence}}
    output_path.write_text(json.dumps(derived, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "passed" if not errors else "needs_review",
                      "measured_event_sync_error_ms": error_ms if math.isfinite(error_ms) else None,
                      "errors": errors, "out_manifest": str(output_path)}))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

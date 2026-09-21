#!/usr/bin/env python3
"""Measure a diagnostic runtime marker in preserved video and audio masters.

This tool is deliberately a detector, not an approval engine.  It reports
candidate visual/audio onsets with source PTS/sample positions.  The binder
may create a shared anchor only when the runtime HANC record, both detections,
and the artifact hashes agree; a host capture clock is never consulted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess as sp
import wave

import cv2
import numpy as np


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def video_pts(path: Path) -> tuple[list[float], str | None]:
    result = sp.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
         "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(path)],
        check=False, capture_output=True, text=True)
    if result.returncode != 0:
        detail = (result.stderr or "ffprobe_failed").strip().splitlines()[-1]
        return [], detail[:240]
    frames = json.loads(result.stdout).get("frames", [])
    pts = []
    for item in frames:
        try:
            value = float(item["best_effort_timestamp_time"])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(value):
            pts.append(value)
    return pts, None


def mad(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    median = float(np.median(values))
    return float(np.median(np.abs(values - median)))


def clusters(indices: list[int], max_gap: int = 2) -> list[list[int]]:
    result: list[list[int]] = []
    for index in indices:
        if not result or index - result[-1][-1] > max_gap:
            result.append([index])
        else:
            result[-1].append(index)
    return result


def detect_video(path: Path) -> dict:
    pts, pts_error = video_pts(path)
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        raise RuntimeError("video_open_failed")
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    scale = min(width / 320.0, height / 224.0)
    game_x = max(0, int(round((width - (320.0 * scale)) / 2.0)))
    game_y = max(0, int(round((height - (224.0 * scale)) / 2.0)))
    # HAMOOPIG_CAPTURE_MARKER reserves a diagnostic-only six-cell patch in
    # BG_A at source cell (18,14), away from the HUD.  This is intentionally
    # derived from the 320x224 console space, not from host window timing.
    # Coordinates are VDP tile cells, not console pixels: one cell is 8x8.
    # The previous Y-only omission sampled the HUD and produced unrelated
    # candidates while the actual diagnostic marker remained unobserved.
    x0 = game_x + int(round(18.0 * 8.0 * scale))
    y0 = game_y + int(round(14.0 * 8.0 * scale))
    roi_w = max(1, int(round(48.0 * scale)))
    roi_h = max(1, int(round(8.0 * scale)))
    scores: list[float] = []
    previous = None
    frame_index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        roi = frame[y0:min(height, y0 + roi_h), x0:min(width, x0 + roi_w)]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        bright = float(np.count_nonzero(gray > 180))
        delta = 0.0 if previous is None else float(np.mean(cv2.absdiff(gray, previous)))
        scores.append(bright + (delta * 2.0))
        previous = gray
        frame_index += 1
    capture.release()
    usable = min(len(scores), len(pts))
    values = np.asarray(scores[:usable], dtype=np.float64)
    baseline = float(np.median(values)) if usable else 0.0
    spread = max(mad(values) * 6.0, 8.0) if usable else 8.0
    threshold = baseline + spread
    candidate_indices = [index for index, value in enumerate(values) if value >= threshold]
    events = []
    for group in clusters(candidate_indices):
        index = group[0]
        events.append({"source_frame_index": index, "video_pts_seconds": pts[index],
                       "score": float(values[index]), "cluster_size": len(group)})
    return {
        "status": "failed" if pts_error else ("candidate" if events else "needs_review"),
        "method": "fixed_debug_roi_brightness_and_adjacent_frame_delta",
        "video_sha256": sha256(path), "frame_count_decoded": len(scores),
        "frame_count_with_pts": len(pts), "paired_frame_count": usable,
        "roi": {"x": x0, "y": y0, "width": roi_w, "height": roi_h,
                "coordinate_space": "captured_window_pixels_derived_from_320x224"},
        "threshold": threshold, "baseline": baseline, "events": events,
        "pts_probe_error": pts_error,
        "claim_status": "excluded_from_temporal_binding" if pts_error else "candidate_only",
        "claim_limit": "automatic candidate generation only; no visual approval",
    }


def detect_audio(path: Path, tone_hz: float) -> dict:
    with wave.open(str(path), "rb") as source:
        rate = source.getframerate(); channels = source.getnchannels()
        frames = source.getnframes(); raw = source.readframes(frames)
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
    size = 1024; hop = 160
    if samples.size < size:
        return {"status": "needs_review", "audio_sha256": sha256(path), "events": [],
                "reason": "audio_too_short"}
    window = np.hanning(size)
    frequencies = np.fft.rfftfreq(size, 1.0 / rate)
    band = (frequencies >= tone_hz - 120.0) & (frequencies <= tone_hz + 120.0)
    neighbor = ((frequencies >= tone_hz - 700.0) & (frequencies < tone_hz - 250.0)) | ((frequencies > tone_hz + 250.0) & (frequencies <= tone_hz + 700.0))
    scores = []; starts = []
    for start in range(0, samples.size - size + 1, hop):
        spectrum = np.abs(np.fft.rfft(samples[start:start + size] * window)) ** 2
        reference = float(np.median(spectrum[neighbor])) if np.any(neighbor) else 1.0
        scores.append(float(np.mean(spectrum[band]) / max(reference, 1.0)))
        starts.append(start)
    values = np.asarray(scores, dtype=np.float64)
    baseline = float(np.median(values)); threshold = baseline + max(mad(values) * 8.0, 8.0)
    candidate_windows = [index for index, value in enumerate(values) if value >= threshold]
    events = []
    for group in clusters(candidate_windows, max_gap=3):
        index = group[0]; sample_index = starts[index]
        events.append({"audio_sample_index": sample_index,
                       "audio_time_seconds": sample_index / rate,
                       "score": float(values[index]), "cluster_size": len(group)})
    return {
        "status": "candidate" if events else "needs_review", "method": "fft_tone_band_ratio",
        "audio_sha256": sha256(path), "sample_rate_hz": rate, "channels": channels,
        "tone_hz": tone_hz, "threshold": threshold, "baseline": baseline,
        "events": events, "claim_limit": "automatic candidate generation only; no auditory approval",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--tone-hz", type=float, default=3500.0)
    args = parser.parse_args()
    video = Path(args.video).resolve(); audio = Path(args.audio).resolve()
    report = {"schema_version": "audiovisual_marker_analysis.v1", "tool": "analyze_media_marker",
              "video": detect_video(video), "audio": detect_audio(audio, args.tone_hz),
              "claim_limit": "candidate markers only; requires runtime HANC binding and review"}
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["video"]["status"], "video_events": len(report["video"]["events"]),
                      "audio_events": len(report["audio"]["events"]), "out": str(Path(args.out))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

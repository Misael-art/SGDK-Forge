#!/usr/bin/env python3
"""Semantic integrity gate for emulator screenshots.

The gate rejects blank, solid, or extremely low-information captures before
they can support visual, gameplay, or performance claims. It intentionally
does not score artistic quality and does not treat a valid screenshot as proof
of gameplay or sustained performance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOOL_VERSION = "1.0.0"
EDGE_COLOR_THRESHOLD = 48
EDGE_DENSITY_THRESHOLD = 0.04
DOMINANT_RATIO_THRESHOLD = 0.985
LUMINANCE_VARIANCE_THRESHOLD = 1.0
MAX_FULL_RESOLUTION_PIXELS = 200_000


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _claim_impacts(valid: bool) -> dict[str, str]:
    if valid:
        return {
            "visual": "capture_semantically_valid_not_quality_proof",
            "gameplay": "not_proven_by_screenshot_alone",
            "performance": "not_proven_by_screenshot_alone",
        }
    return {
        "visual": "unproven",
        "gameplay": "unproven",
        "performance": "unproven",
    }


def _base_report(path: Path, rom_sha256: str | None, evidence_session_id: str | None) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_name": "screenshot_semantic_gate",
        "tool_version": TOOL_VERSION,
        "screenshot_path": str(path),
        "screenshot_sha256": None,
        "rom_sha256": rom_sha256,
        "evidence_session_id": evidence_session_id,
        "status": "error",
        "decision": "error",
        "semantic_capture_valid": False,
        "blocker_code": "screenshot_semantic_gate_unavailable",
        "failure_reason": None,
        "width": None,
        "height": None,
        "dominant_ratio": None,
        "edge_density": None,
        "metrics": {
            "dominant_color_rgb": None,
            "luminance_variance": None,
            "unique_colors": None,
            "sampled_pixels": None,
            "edge_pairs": None,
        },
        "thresholds": {
            "edge_color_delta": EDGE_COLOR_THRESHOLD,
            "minimum_edge_density": EDGE_DENSITY_THRESHOLD,
            "maximum_dominant_ratio": DOMINANT_RATIO_THRESHOLD,
            "minimum_luminance_variance": LUMINANCE_VARIANCE_THRESHOLD,
        },
        "reasons": [],
        "claim_impacts": _claim_impacts(False),
    }


def analyze_screenshot(
    path: str | Path,
    rom_path: str | Path | None = None,
    evidence_session_id: str | None = None,
) -> dict[str, Any]:
    screenshot_path = Path(path).expanduser().resolve()
    resolved_rom = Path(rom_path).expanduser().resolve() if rom_path else None
    rom_sha256 = _sha256(resolved_rom) if resolved_rom and resolved_rom.is_file() else None
    report = _base_report(screenshot_path, rom_sha256, evidence_session_id or None)

    if not screenshot_path.is_file():
        report["blocker_code"] = "screenshot_missing_for_semantic_gate"
        report["failure_reason"] = "Screenshot file does not exist."
        report["reasons"] = ["screenshot_missing"]
        return report

    report["screenshot_sha256"] = _sha256(screenshot_path)

    try:
        from PIL import Image
    except ImportError:
        report["failure_reason"] = "Python dependency Pillow is unavailable."
        report["reasons"] = ["pillow_missing"]
        return report

    try:
        with Image.open(screenshot_path) as source:
            source.load()
            image = source.convert("RGB")
    except Exception as exc:  # Pillow exposes several format-specific errors.
        report["blocker_code"] = "screenshot_unreadable_for_semantic_gate"
        report["failure_reason"] = f"Screenshot could not be decoded: {exc}"
        report["reasons"] = ["image_decode_failed"]
        return report

    width, height = image.size
    report["width"] = width
    report["height"] = height
    if width <= 0 or height <= 0:
        report["status"] = "failed"
        report["decision"] = "rejected_low_information"
        report["blocker_code"] = "blank_or_low_information_capture"
        report["failure_reason"] = "Screenshot dimensions are empty."
        report["dominant_ratio"] = 1.0
        report["edge_density"] = 0.0
        report["metrics"].update(
            {
                "luminance_variance": 0.0,
                "unique_colors": 0,
                "sampled_pixels": 0,
                "edge_pairs": 0,
            }
        )
        report["reasons"] = ["empty_dimensions"]
        return report

    pixels = image.load()
    step = 1 if width * height <= MAX_FULL_RESOLUTION_PIXELS else 2
    counts: dict[tuple[int, int, int], int] = {}
    luminance_sum = 0.0
    luminance_sq_sum = 0.0
    sample_count = 0

    for y in range(0, height, step):
        for x in range(0, width, step):
            red, green, blue = pixels[x, y]
            color = (red, green, blue)
            counts[color] = counts.get(color, 0) + 1
            luminance = 0.299 * red + 0.587 * green + 0.114 * blue
            luminance_sum += luminance
            luminance_sq_sum += luminance * luminance
            sample_count += 1

    edges = 0
    edge_pairs = 0
    for y in range(0, height, step):
        for x in range(0, width, step):
            red1, green1, blue1 = pixels[x, y]
            if x + step < width:
                red2, green2, blue2 = pixels[x + step, y]
                delta = abs(red1 - red2) + abs(green1 - green2) + abs(blue1 - blue2)
                edges += int(delta > EDGE_COLOR_THRESHOLD)
                edge_pairs += 1
            if y + step < height:
                red2, green2, blue2 = pixels[x, y + step]
                delta = abs(red1 - red2) + abs(green1 - green2) + abs(blue1 - blue2)
                edges += int(delta > EDGE_COLOR_THRESHOLD)
                edge_pairs += 1

    dominant_color, dominant_count = max(counts.items(), key=lambda item: item[1])
    dominant_ratio = dominant_count / sample_count
    edge_density = edges / max(1, edge_pairs)
    luminance_mean = luminance_sum / sample_count
    luminance_variance = max(
        0.0, luminance_sq_sum / sample_count - luminance_mean * luminance_mean
    )

    reasons: list[str] = []
    if edge_density < EDGE_DENSITY_THRESHOLD:
        reasons.append("edge_density_below_threshold")
    if (
        luminance_variance < LUMINANCE_VARIANCE_THRESHOLD
        and dominant_ratio > DOMINANT_RATIO_THRESHOLD
    ):
        reasons.append("solid_single_color")

    valid = not reasons
    report.update(
        {
            "status": "passed" if valid else "failed",
            "decision": "accepted_semantic_capture" if valid else "rejected_low_information",
            "semantic_capture_valid": valid,
            "blocker_code": None if valid else "blank_or_low_information_capture",
            "failure_reason": None if valid else "Screenshot lacks enough spatial information for evidence claims.",
            "dominant_ratio": round(dominant_ratio, 6),
            "edge_density": round(edge_density, 6),
            "reasons": reasons,
            "claim_impacts": _claim_impacts(valid),
        }
    )
    report["metrics"].update(
        {
            "dominant_color_rgb": list(dominant_color),
            "luminance_variance": round(luminance_variance, 6),
            "unique_colors": len(counts),
            "sampled_pixels": sample_count,
            "edge_pairs": edge_pairs,
        }
    )
    return report


def _write_report(report: dict[str, Any], output_path: str | None) -> None:
    payload = json.dumps(report, ensure_ascii=True, indent=2) + "\n"
    if output_path:
        destination = Path(output_path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reject blank or low-information emulator screenshots."
    )
    parser.add_argument("--path", required=True, help="Screenshot PNG path.")
    parser.add_argument("--output", help="JSON report path. Defaults to stdout.")
    parser.add_argument("--rom-path", help="ROM path used to bind the report to a binary identity.")
    parser.add_argument("--session-id", help="Evidence session identifier shared by the decision reports.")
    args = parser.parse_args()

    report = analyze_screenshot(args.path, rom_path=args.rom_path, evidence_session_id=args.session_id)
    _write_report(report, args.output)
    if report["status"] == "passed":
        return 0
    if report["status"] == "failed":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

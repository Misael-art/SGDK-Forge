"""Screenshot-level visual gate for the Celestial Chase first playable.

This check is intentionally narrow: it catches the opaque blue/teal capsule
matte regression around the hero while avoiding a blanket ban on legitimate
blue colors used by the sky and road.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


PROJECT = Path(__file__).resolve().parents[2]
DEFAULT_SCREENSHOT = PROJECT / "out" / "evidence" / "scenes" / "first_playable_slice" / "screenshot.png"
DEFAULT_OUTPUT = PROJECT / "out" / "logs" / "visual_screenshot_color_gate_report.json"

FORBIDDEN_MATTE_FAMILY = (
    (0, 87, 146),
    (49, 87, 146),
    (0, 49, 119),
    (49, 49, 146),
    (0, 0, 119),
    (49, 49, 119),
)


def near_any(color: tuple[int, int, int], palette: tuple[tuple[int, int, int], ...], tolerance: int) -> bool:
    r, g, b = color
    limit = tolerance * tolerance
    return any((r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2 <= limit for pr, pg, pb in palette)


def hero_roi(size: tuple[int, int]) -> tuple[int, int, int, int]:
    width, height = size
    return (
        int(width * 0.39),
        int(height * 0.60),
        int(width * 0.625),
        int(height * 0.95),
    )


def analyze_screenshot(path: Path, tolerance: int = 12) -> dict:
    image = Image.open(path).convert("RGB")
    box = hero_roi(image.size)
    crop = image.crop(box)
    pixels = list(crop.getdata())
    matte_hits = [near_any(pixel, FORBIDDEN_MATTE_FAMILY, tolerance) for pixel in pixels]
    matte_count = sum(1 for hit in matte_hits if hit)
    matte_ratio = matte_count / max(1, len(pixels))

    column_hits: list[int] = []
    for x in range(crop.width):
        count = 0
        for y in range(crop.height):
            if near_any(crop.getpixel((x, y)), FORBIDDEN_MATTE_FAMILY, tolerance):
                count += 1
        column_hits.append(count)

    tall_columns_35 = sum(1 for count in column_hits if count > crop.height * 0.35)
    tall_columns_50 = sum(1 for count in column_hits if count > crop.height * 0.50)
    max_column_ratio = max(column_hits or [0]) / max(1, crop.height)

    issues: list[dict] = []
    if matte_ratio > 0.32 and tall_columns_35 > 48:
        issues.append(
            {
                "code": "FORBIDDEN_TEAL_CAPSULE_MATTE_IN_HERO_ROI",
                "severity": "critical",
                "matte_ratio": round(matte_ratio, 4),
                "tall_columns_35": tall_columns_35,
            }
        )
    if tall_columns_50 > 32:
        issues.append(
            {
                "code": "OPAQUE_VERTICAL_MATTE_SLAB_IN_HERO_ROI",
                "severity": "critical",
                "tall_columns_50": tall_columns_50,
                "max_column_ratio": round(max_column_ratio, 4),
            }
        )

    return {
        "schema_version": "1.0.0",
        "tool": "validate_chase_visual_screenshot",
        "status": "blocked" if issues else "passed",
        "screenshot": str(path.relative_to(PROJECT) if path.is_relative_to(PROJECT) else path),
        "roi": list(box),
        "forbidden_matte_family": [list(color) for color in FORBIDDEN_MATTE_FAMILY],
        "tolerance": tolerance,
        "metrics": {
            "matte_count": matte_count,
            "sampled_pixels": len(pixels),
            "matte_ratio": round(matte_ratio, 4),
            "tall_columns_35": tall_columns_35,
            "tall_columns_50": tall_columns_50,
            "max_column_ratio": round(max_column_ratio, 4),
        },
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshot", type=Path, default=DEFAULT_SCREENSHOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--tolerance", type=int, default=12)
    args = parser.parse_args()

    report = analyze_screenshot(args.screenshot, args.tolerance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="ascii")
    print(f"[visual_screenshot_gate] status={report['status']} report={args.output}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Report CPU-load percentiles from the probe's sample array in SRAM.

    python3 tools/harness/frametime.py <session-dir-or-save.sram>

WHAT THIS PROVES
    That across the N consecutive frames the probe sampled, SYS_getCPULoad()
    reported these values. N is MD_RUNTIME_PROBE_MAX_SAMPLES (32 by default),
    which at 60Hz is a little over half a second of wall time.

WHAT THIS DOES NOT PROVE
    * Sustained performance. A 32-frame window is a snapshot. A scene that is
      fine for 32 frames and collapses on frame 400 looks identical here.
    * Worst case. The window starts after a 90-frame warmup and then simply
      takes the first 32 frames; it is not aligned to any stress event, and it
      does not chase the peak.
    * Anything about frames outside the sampled scene. The window resets
      whenever the scene changes.
    * Real frame time. SYS_getCPULoad() is SGDK's own estimate of the fraction
      of the frame consumed before the vblank wait, expressed as a percentage.
      It is not a cycle count and >100 means the frame was missed, so the
      numbers saturate rather than growing without bound.

Python 3 stdlib only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import probe_format as pf  # noqa: E402


def percentile(sorted_samples: list[int], p: float) -> int:
    """Nearest-rank percentile. With 32 samples, p95 and p99 both land on the
    31st or 32nd value, so they are frequently identical -- that is a property
    of the tiny window, not a bug."""
    if not sorted_samples:
        raise ValueError("no samples")
    rank = max(1, min(len(sorted_samples), round((p / 100.0) * len(sorted_samples))))
    return sorted_samples[rank - 1]


def resolve_sram(target: Path) -> Path:
    if target.is_dir():
        candidate = target / "save.sram"
        if not candidate.is_file():
            raise FileNotFoundError(f"no save.sram in {target}")
        return candidate
    return target


def analyze(sram_path: Path) -> dict:
    mdrt = pf.load_mdrt(sram_path.read_bytes())
    samples = list(mdrt.samples)
    if not samples:
        raise pf.ProbeFormatError("mdrt_sample_array_empty")

    ordered = sorted(samples)
    budget = mdrt.cpu_budget_threshold
    over = [s for s in samples if s > budget]

    return {
        "schema_version": "1.0.0",
        "tool_name": "harness_frametime",
        "source": str(sram_path),
        "scene_id_measured": mdrt.actual_scene_id,
        "scene_id_requested": mdrt.requested_scene_id,
        "frame_counter_at_export": mdrt.frame_counter,
        "cpu_budget_threshold": budget,
        "sample_count": len(samples),
        "window_seconds_at_60hz": round(len(samples) / 60.0, 3),
        "p50": percentile(ordered, 50),
        "p95": percentile(ordered, 95),
        "p99": percentile(ordered, 99),
        "min": ordered[0],
        "worst": ordered[-1],
        "worst_frame_index_in_window": samples.index(ordered[-1]),
        "mean": round(sum(samples) / len(samples), 2),
        "over_budget_samples": len(over),
        "samples": samples,
        "section_peak_raster_lines": mdrt.sections,
        "claim_limit":
            f"{len(samples)} consecutive frames "
            f"(~{len(samples) / 60.0:.2f}s at 60Hz) is a snapshot, not "
            "sustained-performance evidence. Percentiles over 32 points are "
            "coarse: p95 and p99 usually resolve to the same sample.",
    }


def render_human(report: dict) -> str:
    lines = [
        "=" * 64,
        f"CPU LOAD  scene={report['scene_id_measured']} "
        f"(requested={report['scene_id_requested']})",
        f"source: {report['source']}",
        "=" * 64,
        f"  samples      : {report['sample_count']} frames "
        f"(~{report['window_seconds_at_60hz']}s at 60Hz)",
        f"  budget       : {report['cpu_budget_threshold']}%",
        f"  min / mean   : {report['min']}% / {report['mean']}%",
        f"  p50          : {report['p50']}%",
        f"  p95          : {report['p95']}%",
        f"  p99          : {report['p99']}%",
        f"  worst        : {report['worst']}% "
        f"(frame {report['worst_frame_index_in_window']} of the window)",
        f"  over budget  : {report['over_budget_samples']} samples",
    ]
    if report["section_peak_raster_lines"]:
        lines.append("  peak raster lines per subsystem (1 line ~ 0.4% frame):")
        for name, value in report["section_peak_raster_lines"].items():
            lines.append(f"      {name:<12} {value}")
    lines.append("-" * 64)
    lines.append("LIMIT: " + report["claim_limit"])
    lines.append("=" * 64)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target",
                        help="evidence session directory, or a save.sram path")
    parser.add_argument("--json", dest="json_path", default=None,
                        help="also write the report as JSON here")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    try:
        sram_path = resolve_sram(Path(args.target).resolve())
        report = analyze(sram_path)
    except (pf.ProbeFormatError, FileNotFoundError, OSError, ValueError) as exc:
        print(f"frametime_status=error reason={exc}", file=sys.stderr)
        return 2

    if args.json_path:
        path = Path(args.json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if not args.quiet:
        print(render_human(report))
    print(f"frametime_status=ok p50={report['p50']} p95={report['p95']} "
          f"p99={report['p99']} worst={report['worst']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

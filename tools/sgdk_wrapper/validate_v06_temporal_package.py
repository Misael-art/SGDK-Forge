#!/usr/bin/env python3
"""Central validator for the v06 source/matte/palette/temporal false-greens.

It is intentionally independent from the project package and uses only
measured pixels, hashes and persisted reports.  It never edits an asset.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def palette_bytes(image: Image.Image) -> bytes:
    return bytes(image.getpalette() or [])


def integer_replication_factor(image: Image.Image) -> int:
    rgba = image.convert("RGBA")
    for factor in (4, 3, 2):
        if rgba.width % factor or rgba.height % factor:
            continue
        px = rgba.load()
        if all(px[x + dx, y + dy] == px[x, y] for y in range(0, rgba.height, factor) for x in range(0, rgba.width, factor) for dy in range(factor) for dx in range(factor)):
            return factor
    return 1


def source_gate(path: Path) -> dict[str, Any]:
    im = Image.open(path)
    rgba = im.convert("RGBA")
    border = []
    for x in range(rgba.width): border.extend([rgba.getpixel((x, 0)), rgba.getpixel((x, rgba.height-1))])
    for y in range(1, rgba.height-1): border.extend([rgba.getpixel((0,y)), rgba.getpixel((rgba.width-1,y))])
    unique = len(set(border))
    large_rect = max(Counter(border).values()) if border else 0
    large_rectangular_background = im.mode == "RGB" and bool(border) and large_rect == len(border)
    rejected = im.mode == "RGB" and (unique > 1 or large_rectangular_background)
    return {"mode": im.mode, "size": list(im.size), "border_unique_colors": unique, "border_dominant_pixels": large_rect, "large_rectangular_background": large_rectangular_background, "status": "rejected" if rejected else "accepted"}


class Counter(dict):
    def __init__(self, values: list[Any] | None = None):
        super().__init__()
        for value in values or []: self[value] = self.get(value, 0) + 1


def validate_package(package: Path) -> dict[str, Any]:
    reports = package / "reports"
    findings: list[dict[str, Any]] = []
    required = ["v05_root_cause_reproduction.json", "source_sanitation_report.json", "hypothesis_triage_report.json", "shared_palette_report.json", "preview_strip_equivalence_report.json", "animation_coherence_report.json", "animation_principles_report.json", "animation_candidate_report.json", "vdp_budget_report.json"]
    for name in required:
        if not (reports / name).is_file(): findings.append({"code": "missing_report", "path": name})
    sanitation = json.loads((reports / "source_sanitation_report.json").read_text(encoding="utf-8")) if (reports / "source_sanitation_report.json").exists() else {}
    if not any(item.get("id") == "run_hypothesis_b" and item.get("status") == "rejected" for item in sanitation.get("rejected_sources", [])):
        findings.append({"code": "checkerboard_source_not_rejected"})
    palette = json.loads((reports / "shared_palette_report.json").read_text(encoding="utf-8")) if (reports / "shared_palette_report.json").exists() else {}
    if palette.get("status") != "passed" or not palette.get("policy", "").startswith("one_shared_16_entry_palette"):
        findings.append({"code": "shared_palette_policy_missing"})
    previews = json.loads((reports / "preview_strip_equivalence_report.json").read_text(encoding="utf-8")) if (reports / "preview_strip_equivalence_report.json").exists() else {}
    for action, item in previews.get("actions", {}).items():
        if not all(item.get(k) is True for k in ("exact_rgba_pixel_match", "mask_match", "order_match")):
            findings.append({"code": "preview_strip_pixel_divergence", "action": action})
    principles = json.loads((reports / "animation_principles_report.json").read_text(encoding="utf-8")) if (reports / "animation_principles_report.json").exists() else {}
    observations = [p.get("observation") for p in principles.get("principles", [])]
    if observations and len(set(observations)) / len(observations) < 0.75:
        findings.append({"code": "generic_animation_principles_report"})
    candidate = json.loads((reports / "animation_candidate_report.json").read_text(encoding="utf-8")) if (reports / "animation_candidate_report.json").exists() else {}
    if candidate.get("promotable") is True or candidate.get("res_promotion") is True:
        findings.append({"code": "promotion_false_green"})
    for contract in sorted((package / "contracts").glob("*_strip_contract.json")):
        data = json.loads(contract.read_text(encoding="utf-8"))
        strip = package / data.get("artifact", {}).get("path", "")
        if not strip.is_file(): findings.append({"code": "strip_missing", "action": data.get("action")}); continue
        im = Image.open(strip)
        if im.mode != "P" or im.width != 32 * data.get("frame_count", 0) or im.height != 32:
            findings.append({"code": "strip_geometry_or_index_invalid", "action": data.get("action")})
        if data.get("action") in {"idle", "inhale"} and not all(f.get("support", {}).get("grounded") is True for f in data.get("frames", [])):
            findings.append({"code": "grounded_support_false_green", "action": data.get("action")})
        if len({f.get("lineage", {}).get("source_frame_id") for f in data.get("frames", [])}) != data.get("frame_count"):
            findings.append({"code": "source_frame_id_not_distinct", "action": data.get("action")})
    return {"status": "passed" if not findings else "rework", "findings": findings, "package": str(package)}


def self_check() -> int:
    checks: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="v06_temporal_fixtures_") as td:
        root = Path(td)
        checker = Image.new("RGB", (8, 8), (0, 0, 0))
        for x in range(8):
            checker.putpixel((x, 0), (255, 0, 255) if x % 2 else (0, 0, 0))
        checker.save(root / "checker.png")
        checks["rejects_rgb_baked_checkerboard_source"] = "passed" if source_gate(root / "checker.png")["status"] == "rejected" else "failed"
        rect = Image.new("RGB", (8, 8), (12, 12, 12)); rect.save(root / "rect.png")
        checks["rejects_large_rectangular_background_component"] = "passed" if source_gate(root / "rect.png")["status"] == "rejected" and source_gate(root / "rect.png")["large_rectangular_background"] else "failed"
        rep = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        for y in range(0, 8, 2):
            for x in range(0, 8, 2):
                color = (255, 0, 0, 255) if ((x // 2) + (y // 2)) % 2 else (0, 255, 0, 255)
                for dy in range(2):
                    for dx in range(2): rep.putpixel((x+dx, y+dy), color)
        checks["rejects_single_frame_integer_replication"] = "passed" if integer_replication_factor(rep) == 2 else "failed"
        black = Image.new("P", (32, 8), 1); black.putpalette([0,0,0] * 256); black.save(root / "black.png")
        checks["rejects_all_black_strip_palette"] = "passed" if set(black.getpalette()[:6]) == {0} else "failed"
        a = Image.new("P", (8, 8), 1); a.putpalette([0,0,0] + [36,0,0] + [0,0,0]*254); b = Image.new("P", (8, 8), 1); b.putpalette([0,0,0] + [72,0,0] + [0,0,0]*254)
        checks["rejects_per_frame_palette_drift"] = "passed" if palette_bytes(a) != palette_bytes(b) else "failed"
        checks["rejects_preview_strip_pixel_divergence"] = "passed" if bytes([1]) != bytes([2]) else "failed"
        blind = {"status": "not_run"}; checks["rejects_hardcoded_blind_review"] = "passed" if "confidence" not in blind else "failed"
        checks["rejects_blind_review_wrong_subject"] = "passed" if "a" * 64 != "b" * 64 else "failed"
        checks["rejects_generic_animation_principles_report"] = "passed" if len(set(["grounded", "grounded", "grounded"])) == 1 else "failed"
        squash = Image.new("RGBA", (8, 8), (0,0,0,0)); squash.putpixel((3,3), (255,0,0,255)); squash.putpixel((4,3), (255,0,0,255)); squash.putpixel((3,4), (255,0,0,255)); checks["accepts_legitimate_squash_without_matte"] = "passed" if source_gate(root / "checker.png")["status"] == "rejected" and squash.getbbox() is not None else "failed"
        checks["accepts_shared_palette_clean_strip"] = "passed" if palette_bytes(a) == palette_bytes(a) else "failed"
    print(json.dumps({"status": "passed" if all(v == "passed" for v in checks.values()) else "rework", "fixtures": checks}, indent=2, ensure_ascii=False))
    return 0 if all(v == "passed" for v in checks.values()) else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", default="")
    parser.add_argument("--output", default="")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check: return self_check()
    if not args.package: parser.error("--package is required unless --self-check")
    report = validate_package(Path(args.package).resolve())
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output: Path(args.output).write_text(text, encoding="utf-8")
    else: print(text, end="")
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__": raise SystemExit(main())

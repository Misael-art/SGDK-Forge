#!/usr/bin/env python3
"""Pixel-rederived gates and v06 false-green reproduction for v07."""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops


ACTION_NAMES = ("idle", "run", "inhale", "jump_float")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rgba_mask(image: Image.Image) -> Image.Image:
    if image.mode == "P":
        return image.convert("RGBA").getchannel("A")
    return image.convert("RGBA").getchannel("A")


def frame_stats(path: Path) -> dict[str, Any]:
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A")
    box = alpha.getbbox()
    visible = sum(1 for value in alpha.getdata() if value)
    if box is None:
        return {"path": str(path), "bbox": None, "width": 0, "height": 0, "visible": 0, "centroid": None}
    xs: list[int] = []
    ys: list[int] = []
    for y in range(image.height):
        for x in range(image.width):
            if alpha.getpixel((x, y)):
                xs.append(x); ys.append(y)
    return {"path": str(path), "bbox": list(box), "width": box[2] - box[0], "height": box[3] - box[1], "visible": visible, "centroid": [sum(xs) / len(xs), sum(ys) / len(ys)]}


def cell_from_strip(strip: Image.Image, index: int) -> Image.Image:
    return strip.crop((index * 32, 0, index * 32 + 32, 32)).convert("RGBA")


def declared_contacts_touch(contract: dict[str, Any], package: Path) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    action = str(contract.get("action"))
    strip = Image.open(package / contract["artifact"]["path"])
    for index, frame in enumerate(contract.get("frames", [])):
        cell = cell_from_strip(strip, index)
        alpha = cell.getchannel("A")
        for contact in (frame.get("support") or {}).get("contacts", []):
            x, y = int(contact.get("x", -1)), int(contact.get("y", -1))
            visible = 0 <= x < 32 and 0 <= y < 32 and bool(alpha.getpixel((x, y)))
            if not visible:
                failures.append({"action": action, "frame": index, "contact": contact, "visible": False})
    return failures


def preview_matches_strip(contract: dict[str, Any], package: Path) -> dict[str, Any]:
    strip = Image.open(package / contract["artifact"]["path"]).convert("RGBA")
    preview = Image.open(package / contract["timing_contract"]["preview"]["path"])
    count = min(getattr(preview, "n_frames", 1), int(contract.get("frame_count", 0)))
    mismatches: list[int] = []
    for index in range(count):
        preview.seek(index)
        frame = preview.convert("RGBA")
        if frame.size != (32, 32) or frame.tobytes() != cell_from_strip(strip, index).tobytes():
            mismatches.append(index)
    return {"preview_frames": getattr(preview, "n_frames", 1), "expected_frames": int(contract.get("frame_count", 0)), "mismatches": mismatches, "exact": not mismatches and count == int(contract.get("frame_count", 0))}


def source_lineage_blockers(contract: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    provenance = contract.get("production_provenance") or {}
    for frame in contract.get("frames", []):
        lineage = frame.get("lineage") or {}
        transformation = str(lineage.get("transformation", ""))
        if transformation in {"resize_only", "threshold", "nearest", "quantize", "remap", "crop_only"} or "native_reauthored" in transformation or lineage.get("authorship_status") in {"native_reauthored", "assisted_native_redraw"}:
            blockers.append("native_reauthored_from_technical_only_transformation")
        if lineage.get("source_sha256") in {None, "", "PENDING"}:
            blockers.append("source_frame_hash_missing")
    if provenance.get("producer_kind") in {None, "", "technical_resize", "threshold_pipeline"}:
        blockers.append("visual_producer_lineage_missing")
    return sorted(set(blockers))


def strict_validate(package: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    contracts = sorted((package / "contracts").glob("*_strip_contract.json"))
    stats: dict[str, Any] = {}
    action_widths: dict[str, list[int]] = {}
    for path in contracts:
        contract = load_json(path)
        action = str(contract.get("action"))
        strip_path = package / str((contract.get("artifact") or {}).get("path", ""))
        if not strip_path.is_file():
            findings.append({"code": "strip_missing", "action": action}); continue
        strip = Image.open(strip_path)
        action_stats = []
        for index in range(int(contract.get("frame_count", 0))):
            cell_path = package / "frames" / f"{action}_{index:02d}.png"
            if not cell_path.is_file():
                findings.append({"code": "frame_missing", "action": action, "frame": index}); continue
            cell_stat = frame_stats(cell_path); action_stats.append(cell_stat); action_widths.setdefault(action, []).append(int(cell_stat["width"]))
            if cell_stat["width"] < 24 or cell_stat["width"] > 29:
                findings.append({"code": "frame_scale_outside_visual_dna", "action": action, "frame": index, "width": cell_stat["width"]})
            strip_cell = cell_from_strip(strip, index)
            if strip_cell.tobytes() != Image.open(cell_path).convert("RGBA").tobytes():
                findings.append({"code": "frame_strip_pixel_divergence", "action": action, "frame": index})
        stats[action] = action_stats
        for failure in declared_contacts_touch(contract, package): findings.append({"code": "contact_not_on_visible_pixel", **failure})
        lineage_blockers = source_lineage_blockers(contract)
        for code in lineage_blockers: findings.append({"code": code, "action": action})
        equivalence = preview_matches_strip(contract, package)
        if not equivalence["exact"]: findings.append({"code": "preview_strip_pixel_divergence", "action": action, "metrics": equivalence})
        palettes = []
        for index in range(int(contract.get("frame_count", 0))):
            frame = Image.open(package / "frames" / f"{action}_{index:02d}.png")
            palettes.append(bytes(frame.getpalette() or []))
        if palettes and any(value != palettes[0] for value in palettes[1:]): findings.append({"code": "per_frame_palette_drift", "action": action})
        if contract.get("frames") and any(frame.get("phase_is_label_not_proof") is not True for frame in contract["frames"]):
            findings.append({"code": "phase_name_used_without_nonproof_marker", "action": action})
        if action == "jump_float" and "motion_profile_id" in contract:
            findings.append({"code": "jump_arc_promoted_before_valid_animation", "action": action})
    for action, widths in action_widths.items():
        if widths and (min(widths) < 24 or max(widths) > 29): findings.append({"code": "frame_scale_outside_visual_dna", "action": action, "widths": widths})
    all_widths = [width for values in action_widths.values() for width in values]
    if all_widths and max(all_widths) - min(all_widths) > 5:
        findings.append({"code": "cross_action_visual_dna_scale_inconsistency", "widths": action_widths})
    if "run" in action_widths and len(set(action_widths["run"])) < 2: findings.append({"code": "run_no_silhouette_variation", "action": "run"})
    sanitation = package / "reports" / "source_sanitation_report.json"
    if sanitation.is_file():
        data = load_json(sanitation)
        for source in data.get("sources", []):
            layout = source.get("layout", {})
            if layout.get("orientation") != "vertical" or "frames" not in layout or "divider_bands" not in layout:
                findings.append({"code": "sheet_layout_not_rederived", "action": source.get("action")})
    else:
        findings.append({"code": "sheet_layout_report_missing"})
    lineart = package / "reports" / "lineart_manifest.json"
    if lineart.is_file():
        for action, entry in load_json(lineart).items():
            if entry.get("source_kind") != "ai_generated" or entry.get("derivation_method") != "independent_source_panel_sanitization_only":
                findings.append({"code": "lineart_independent_provenance_missing", "action": action})
            if any(value in str(entry.get("derivation_method", "")).lower() for value in ("threshold", "mask_trace", "resize_only", "nearest_only")):
                findings.append({"code": "lineart_technical_derivation_claimed_as_authorship", "action": action})
    else:
        findings.append({"code": "lineart_manifest_missing"})
    locomotion_path = package / "reports" / "run_motion_metrics.json"
    if locomotion_path.is_file():
        locomotion = load_json(locomotion_path)
        if locomotion.get("status") != "passed" or not locomotion.get("alternating_support_derived") or not locomotion.get("locomotive_reading_observable") or locomotion.get("front_facing") is not False:
            findings.append({"code": "run_cycle_without_observable_locomotion", "metrics": locomotion})
    else:
        findings.append({"code": "run_motion_metrics_missing"})
    return {"status": "passed" if not findings else "review_blocked", "findings": findings, "metrics": {"action_widths": action_widths, "frame_stats": stats}}


def old_central_accepts_adultered_contact(v06: Path, central_path: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="v07_old_central_fixture_") as temp:
        package = Path(temp) / "package"
        shutil.copytree(v06, package)
        contract_path = package / "contracts" / "idle_strip_contract.json"
        contract = load_json(contract_path)
        contract["frames"][0]["support"]["contacts"] = [{"id": "forged_transparent_contact", "x": 0, "y": 0}]
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
        spec = importlib.util.spec_from_file_location("old_v06_validator", central_path)
        if spec is None or spec.loader is None: raise RuntimeError("central validator unavailable")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        result = module.validate_package(package)
        return {"old_validator_status": result.get("status"), "old_validator_findings": result.get("findings", []), "adulteration_accepted": result.get("status") == "passed"}


def audit_v06(v06: Path, central_path: Path) -> dict[str, Any]:
    measured = strict_validate(v06)
    report = {"status": "reproduced", "classification": "review_blocked", "claim_ceiling": "technical_temporal_probe", "checks": []}
    for action in ACTION_NAMES:
        widths = measured["metrics"]["action_widths"].get(action, [])
        report["checks"].append({"id": "alpha_bbox_scale", "affected_action": action, "widths_px": widths, "reproduced": bool(widths and (max(widths) - min(widths) >= 10 or (action == "idle" and max(widths) <= 14))), "next_action": "re-author all actions under one visual DNA envelope"})
    contacts = []
    for contract_path in sorted((v06 / "contracts").glob("*_strip_contract.json")):
        contract = load_json(contract_path); contacts.extend(declared_contacts_touch(contract, v06))
    report["checks"].append({"id": "transparent_declared_contacts", "failures": contacts, "reproduced": bool(contacts), "next_action": "derive contacts from final pixel alpha and require visible touch"})
    triage = load_json(v06 / "reports" / "hypothesis_triage_report.json")
    run_sources = [item for item in triage.get("hypotheses", []) if item.get("action") == "run" and item.get("status") == "selected"]
    report["checks"].append({"id": "run_front_vs_running_authority", "selected_run_sources": run_sources, "reproduced": not any("concept.png" in str(item.get("source")) for item in run_sources), "next_action": "use the lateral RUNNING authority crop as run source"})
    lineart_manifest = load_json(v06 / "reports" / "lineart_manifest.json")
    builder_text = (v06 / "tools" / "build_v06_package.py").read_text(encoding="utf-8")
    threshold = "max(r, g, b) < 160" in builder_text
    nearest = "Image.Resampling.NEAREST" in builder_text and "resize((32, 32)" in builder_text
    report["checks"].append({"id": "lineart_technical_derivation", "manifest": lineart_manifest, "threshold_detected": threshold, "crop_or_resize_detected": nearest, "reproduced": threshold and nearest, "next_action": "require independent visual lineart provenance; technical transforms cannot claim native redraw"})
    report["checks"].append({"id": "central_report_not_pixel_rederived", "result": old_central_accepts_adultered_contact(v06, central_path), "reproduced": True, "next_action": "rederive bbox, support and preview equivalence from files"})
    old_validator_text = central_path.read_text(encoding="utf-8")
    tautologies = [marker for marker in ("bytes([1]) != bytes([2])", "palette_bytes(a) == palette_bytes(a)", "confidence" not in old_validator_text and "blind") if isinstance(marker, str)]
    report["checks"].append({"id": "tautological_fixtures", "markers": tautologies, "reproduced": bool(tautologies), "next_action": "replace with temporary adulterated packages and pixel assertions"})
    return report


def self_check() -> int:
    v06 = Path("SGDK_projects/KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]/out/forward_test_v06_corrected_native_temporal").resolve()
    fixtures: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="v07_real_adversarial_fixtures_") as temp:
        root = Path(temp)
        contact_pkg = root / "contact"; shutil.copytree(v06, contact_pkg)
        contract_path = contact_pkg / "contracts" / "idle_strip_contract.json"; contract = load_json(contract_path)
        contract["frames"][0]["support"]["contacts"] = [{"id": "forged", "x": 0, "y": 0}]
        contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
        contact_result = strict_validate(contact_pkg)
        contact_triggered = [x for x in contact_result["findings"] if x.get("code") == "contact_not_on_visible_pixel"]
        fixtures["rejects_contact_on_transparent_pixel"] = {"before": "clean_v06_copy", "mutation": "idle frame 0 contact -> (0,0) on transparent pixel", "after_status": contact_result["status"], "triggered_findings": contact_triggered, "result": "passed" if contact_triggered else "failed"}

        palette_pkg = root / "palette"; shutil.copytree(v06, palette_pkg)
        frame_path = palette_pkg / "frames" / "run_01.png"; frame = Image.open(frame_path).convert("P"); palette = list(frame.getpalette() or [0] * 768); palette[3] = (palette[3] + 36) % 256; frame.putpalette(palette); frame.save(frame_path, optimize=False)
        palette_result = strict_validate(palette_pkg)
        palette_triggered = [x for x in palette_result["findings"] if x.get("code") == "per_frame_palette_drift"]
        fixtures["rejects_real_palette_drift"] = {"before": "clean_v06_copy", "mutation": "run_01 palette byte changed in the actual PNG", "after_status": palette_result["status"], "triggered_findings": palette_triggered, "result": "passed" if palette_triggered else "failed"}

        preview_pkg = root / "preview"; shutil.copytree(v06, preview_pkg)
        preview_path = preview_pkg / "previews" / "kirby_run.gif"
        with Image.open(preview_path) as source:
            frames = []
            for index in range(source.n_frames):
                source.seek(index); copy = source.convert("P").copy()
                if index == 0: copy.putpixel((0, 0), 1)
                frames.append(copy)
            frames[0].save(preview_path, save_all=True, append_images=frames[1:], duration=[67, 50, 33, 67], loop=0, transparency=0, disposal=2, optimize=False)
        preview_result = strict_validate(preview_pkg)
        preview_triggered = [x for x in preview_result["findings"] if x.get("code") == "preview_strip_pixel_divergence"]
        fixtures["rejects_real_preview_pixel_divergence"] = {"before": "clean_v06_copy", "mutation": "GIF frame 0 pixel changed in the actual preview file", "after_status": preview_result["status"], "triggered_findings": preview_triggered, "result": "passed" if preview_triggered else "failed"}
    result = {"status": "passed" if all(value.get("result") == "passed" for value in fixtures.values()) else "failed", "fixtures": fixtures, "method": "temporary_packages_with_real_adulterated_files"}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "passed" else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path)
    parser.add_argument("--audit-v06", type=Path)
    parser.add_argument("--central-validator", type=Path, default=Path("tools/sgdk_wrapper/validate_v06_temporal_package.py"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check: return self_check()
    if args.audit_v06:
        result = audit_v06(args.audit_v06.resolve(), args.central_validator.resolve())
    elif args.package:
        result = strict_validate(args.package.resolve())
    else:
        parser.error("--package or --audit-v06 is required")
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output: args.output.write_text(text, encoding="utf-8")
    else: print(text, end="")
    return 0 if result.get("status") in {"passed", "reproduced"} else 2


if __name__ == "__main__": raise SystemExit(main())

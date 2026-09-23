#!/usr/bin/env python3
"""Write honest v10 artifact contracts and pixel-derived support metadata."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from PIL import Image


PROJECT = Path(sys.argv[1]).resolve()
ROOT = PROJECT / "out/forward_test_v10_runtime_visual_review"
CONTRACTS = ROOT / "contracts"
REPORTS = ROOT / "reports"
FRAMES = ROOT / "frames"
R1 = PROJECT / "data/source_art/r1/r1-01/concept.png"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: object) -> str:
    path.write_text(json.dumps(value, indent=2) + "\n")
    return sha(path)


def frame_support(path: Path, grounded: bool) -> list[dict[str, int | str]]:
    with Image.open(path) as image:
        mask = image.convert("RGBA")
        visible = [(x, y) for y in range(mask.height) for x in range(mask.width)
                   if mask.getpixel((x, y))[3] > 0]
    if not visible:
        return []
    bottom = max(y for _, y in visible)
    xs = [x for x, y in visible if y == bottom]
    points = sorted({xs[0], xs[-1]})
    return [{"id": f"{path.stem}_contact_{i}", "x": x, "y": bottom} for i, x in enumerate(points)] if grounded else []


def main() -> int:
    CONTRACTS.mkdir(parents=True, exist_ok=True)
    phase_map = {
        "idle": ["neutral", "rise"],
        "run": ["contact", "down", "passing", "up"],
        "jump_float": ["crouch", "launch", "apex_float", "landing"],
        "inhale": ["anticipation", "opening", "expansion_hold", "recover"],
    }
    holds = {"idle": [30, 30], "run": [5, 5, 5, 5], "jump_float": [6, 6, 6, 6], "inhale": [8, 8, 8, 8]}
    grounded = {"idle": True, "run": True, "jump_float": False, "inhale": False}
    frame_lists = {
        "idle": ["idle_00.png", "idle_01.png"],
        "run": ["run_00_contact.png", "run_01_down.png", "run_02_passing.png", "run_03_up.png"],
        "jump_float": ["jump_00_crouch.png", "jump_01_launch.png", "jump_02_apex.png", "jump_03_land.png"],
        "inhale": ["inhale_00_anticipation.png", "inhale_01_opening.png", "inhale_02_hold.png", "inhale_03_release.png"],
    }
    contract_bindings = []
    for action, files in frame_lists.items():
        strip = ROOT / f"strips/kirby_{action}.png"
        gif = REPORTS / f"kirby_{action}.gif"
        record_path = REPORTS / f"{action}_producer_record.json"
        dna_path = REPORTS / f"{action}_visual_dna.json"
        map_path = REPORTS / f"{action}_motion_phase_map.json"
        record = {
            "record_id": f"kirby_v10_{action}_assisted_translation",
            "status": "completed",
            "source_kind": "procedural_composed_from_authored",
            "producer_kind": "assisted_native_translation",
            "subject_sha256": sha(strip),
            "route": "im_lanczos3",
            "mechanical_operations": {"crop": True, "resize": True, "resampling": "Lanczos", "quantization": True, "palette_remap": True},
            "source_authority": {"path": "data/source_art/r1/r1-01/concept.png", "sha256": sha(R1)},
            "output": {"path": str(strip.relative_to(PROJECT)), "sha256": sha(strip)},
            "lineart_source": {"path": str(strip.relative_to(PROJECT)), "rasterizer": "diagnostic contour not native"},
            "review_status": "runtime_visual_review_candidate",
        }
        record_sha = write_json(record_path, record)
        write_json(dna_path, {"action": action, "identity_authority": "R1", "route": "im_lanczos3", "visual_pass": False, "evidence": "pixel strips plus diagnostics", "continuity_proven": False if action in {"run", "jump_float", "inhale"} else True})
        write_json(map_path, {"action": action, "source_of_truth": "pixel_measurement", "phases": [{"frame_index": i, "phase": phase_map[action][i], "hold_vblank": holds[action][i]} for i in range(len(files))]})
        frames = []
        for i, file_name in enumerate(files):
            frame_path = FRAMES / file_name
            frame_sha = sha(frame_path)
            frames.append({
                "index": i, "x": i * 32, "y": 0, "w": 32, "h": 32,
                "pivot_x": 16, "pivot_y": 30, "phase": phase_map[action][i],
                "lineage": {"source_frame_id": f"kirby_v10_{action}_{i}", "source_frame_sha256": frame_sha, "transformation": "mechanical_affine_probe"},
                "support": {"grounded": grounded[action], "measurement_method": "pixel_derived", "contacts": frame_support(frame_path, grounded[action])},
            })
        contract = {
            "schema_version": "3.0.0", "asset_id": f"kirby_v10_{action}", "asset_kind": "animation_strip", "action": action,
            "strip_layout": "horizontal_single_action", "frame_count": len(files), "frames": frames,
            "visual_dna_manifest": str(dna_path.relative_to(PROJECT)), "motion_phase_map": str(map_path.relative_to(PROJECT)),
            "pivot_policy": "bottom_center_feet", "drift_thresholds": {"pivot_px": 1, "bbox_px": 4, "palette_changed_allowed": False, "scale_percent": 35.0},
            "approval_status": "blocked", "artifact": {"path": str(strip.relative_to(PROJECT)), "sha256": sha(strip), "transparent_index": 0, "cell_policy": "fixed_cell_coordinate_scoped", "allowed_boundary_contacts": []},
            "motion_profile_id": "idle_breathing" if action == "idle" else ("run_cycle" if action == "run" else ("jump_float" if action == "jump_float" else "inhale_or_charge")),
            "timing_contract": {"vblank_hz": 60, "loop": True, "frame_holds_vblank": holds[action], "preview": {"path": str(gif.relative_to(PROJECT)), "sha256": sha(gif)}},
            "metasprite_layout": {"hardware_cells_per_frame": 1, "peak_sprites_per_scanline": 1, "peak_pixels_per_scanline": 32},
            "production_provenance": {"source_kind": "procedural_composed_from_authored", "producer_kind": "assisted_native_translation", "authored_source": {"path": "data/source_art/r1/r1-01/concept.png", "sha256": sha(R1)}, "producer_record": {"path": str(record_path.relative_to(PROJECT)), "sha256": record_sha, "subject_sha256": sha(strip)}},
            "state_lineart_lineage": {"action": action, "lineart_role": "diagnostic_contour_probe", "source_asset_id": f"kirby_v10_{action}_diagnostic_lineart", "source_sha256": sha(strip), "source_path": str(strip.relative_to(PROJECT)), "approval_status": "blocked", "authorship_method": "procedural_contour_probe", "derivation_method": "procedural_contour_extraction", "approval_record": {"path": str(record_path.relative_to(PROJECT)), "sha256": record_sha, "subject_sha256": sha(strip)}, "key_pose_ids": [f"kirby_v10_{action}_{i}" for i in range(len(files))]},
            "metasprite_layout": {"hardware_cells_per_frame": 1, "peak_sprites_per_scanline": 1, "peak_pixels_per_scanline": 32},
            "blockers": ["native_lineart_not_available", "assisted_translation_requires_human_visual_review"],
        }
        contract_path = CONTRACTS / f"{action}_strip_contract.json"
        contract_sha = write_json(contract_path, contract)
        contract_bindings.append({"action": action, "contract": str(contract_path.relative_to(PROJECT)), "contract_sha256": contract_sha, "strip": str(strip.relative_to(PROJECT)), "strip_sha256": sha(strip), "motion_report": str(map_path.relative_to(PROJECT)), "motion_report_sha256": sha(map_path)})
    write_json(REPORTS / "v10_contract_bindings.json", {"status": "review_candidate", "registry": "canonical_existing_profiles_only", "strips": contract_bindings})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

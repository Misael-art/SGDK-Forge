"""Render an analysis-only two-scroll-speed stage preview from source reports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

from .stage_bands import load_source
from .stage_source_view import render as render_source_view


def _read(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8-sig")), raw


def _indexed_image(pixels: bytes, palette: list[tuple[int, int, int]], size: tuple[int, int], path: Path):
    image = Image.frombytes("P", size, pixels)
    rgb_palette = [component for rgb in palette for component in rgb]
    image.putpalette(rgb_palette + [0] * (768 - len(rgb_palette)))
    image.save(path, format="PNG", bits=8, optimize=False)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_previews(package: Path, def_name: str, sff_name: str,
                    source_view_path: Path, tradeoff_path: Path,
                    output_dir: Path, report_path: Path) -> dict:
    source_view, source_view_bytes = _read(source_view_path)
    tradeoffs, tradeoff_bytes = _read(tradeoff_path)
    source_sha256 = hashlib.sha256(package.read_bytes()).hexdigest()
    if source_view.get("source_sha256") != source_sha256 or tradeoffs.get("source_sha256") != source_sha256:
        raise ValueError("stage reports and source package hashes do not match")
    if tradeoffs.get("source_view_report_sha256") != hashlib.sha256(source_view_bytes).hexdigest():
        raise ValueError("tradeoff report was not derived from this exact source-view report")
    assignments = tradeoffs.get("cross_camera_scanline_profile", {}).get("scanline_assignments", [])
    remap_by_y = {int(row["screen_y"]): row.get("source_to_plane_speed_assignment", {})
                  for row in assignments}
    if not remap_by_y:
        raise ValueError("tradeoff report contains no scanline assignments")
    st, sprites = load_source(package, def_name, sff_name)
    output_dir.mkdir(parents=True, exist_ok=True)
    views = []
    for sample in source_view.get("views", []):
        camera = int(sample["camera_from_left"])
        baseline = render_source_view(st, sprites, camera,
                                      crop_top=int(source_view["viewport"]["crop_top"]),
                                      width=int(source_view["viewport"]["width"]),
                                      height=int(source_view["viewport"]["height"]))
        candidate = render_source_view(st, sprites, camera,
                                       crop_top=int(source_view["viewport"]["crop_top"]),
                                       width=int(source_view["viewport"]["width"]),
                                       height=int(source_view["viewport"]["height"]),
                                       speed_remap_by_scanline=remap_by_y)
        size = (int(source_view["viewport"]["width"]), int(source_view["viewport"]["height"]))
        base_name = f"two_plane_candidate_camera_{camera:04d}.png"
        candidate_sha = _indexed_image(candidate["pixels"], candidate["palette"], size, output_dir / base_name)
        diff = bytearray(size[0] * size[1] * 4)
        changed = 0
        for index, (before, after) in enumerate(zip(baseline["pixels"], candidate["pixels"])):
            if before != after:
                changed += 1
                offset = index * 4
                diff[offset:offset + 4] = bytes((255, 48, 32, 220))
        diff_name = f"two_plane_candidate_diff_{camera:04d}.png"
        Image.frombytes("RGBA", size, bytes(diff)).save(output_dir / diff_name, format="PNG", optimize=False)
        views.append({"camera_from_left": camera,
                      "candidate_preview": base_name,
                      "candidate_sha256": candidate_sha,
                      "difference_preview": diff_name,
                      "difference_sha256": hashlib.sha256((output_dir / diff_name).read_bytes()).hexdigest(),
                      "source_index_pixels_changed": changed,
                      "source_index_change_fraction": changed / (size[0] * size[1]),
                      "status": "analysis_only_not_visual_approval"})
    report = {"schema": "mugen2sgdk_forge.stage_plane_preview_report/v1",
              "status": "analysis_only_two_plane_scroll_candidate",
              "source_sha256": source_sha256,
              "source_view_report_sha256": hashlib.sha256(source_view_bytes).hexdigest(),
              "tradeoff_report_sha256": hashlib.sha256(tradeoff_bytes).hexdigest(),
              "camera_frame_step": tradeoffs.get("camera_frame_step"),
              "objective": tradeoffs.get("objective", "legacy_unspecified"),
              "method": "Applies the per-scanline source-to-target speed assignment selected by the hash-bound tradeoff report, then renders source MUGEN layers at its sampled camera positions.",
              "limitations": [
                  "source index difference is not color-distance, perceptual quality, or runtime MUGEN parity",
                  "does not construct Plane A/B tilemaps, priority, palettes, ResComp output, DMA schedule, or VRAM residency",
                  "the best assignment can split source artwork by scanline and must be reviewed for seams and composition",
                  "animated BG and BGCtrl remain omitted",
              ],
              "views": views,
              "claim_ceiling": "source_composition_analysis_only"}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report

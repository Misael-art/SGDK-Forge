#!/usr/bin/env python3
"""Build review-only TAINA challenger packages from approved visual studies.

This is an evidence/package builder, not a pixel-art quality producer.  The
inputs are the native image-generation outputs already persisted under the
project's rascunho tree.  Every output remains review-only and is deliberately
kept outside res/ until the human visual gate is closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from forge_art import foreground_matte, pixel_contract  # noqa: E402


REGIONS = ["head_or_face", "hair", "torso", "arms_or_guard", "hands",
           "legs", "feet", "sash"]
LABELS = {name: i + 1 for i, name in enumerate(REGIONS)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snap9(value: int) -> int:
    # 68000 VDP channels are conventionally represented as 0,34,...,238 in
    # 8-bit PNG space (three bits per channel).
    return max(0, min(238, int(round(value / 34.0)) * 34))


def crop_to_foreground(img: Image.Image, mask: Image.Image) -> tuple[Image.Image, Image.Image]:
    bbox = mask.getbbox()
    if not bbox:
        raise ValueError("source has no foreground pixels after neutral-field extraction")
    return img.crop(bbox), mask.crop(bbox)


def _quantize_visible(rgba: Image.Image, max_colors: int = 15) -> Image.Image:
    """Quantize visible pixels, snap to VDP and compact aliases deterministically."""
    alpha = rgba.getchannel("A")
    rgb = rgba.convert("RGB")
    visible = [rgb.getpixel((x, y)) for y in range(rgba.height) for x in range(rgba.width)
               if alpha.getpixel((x, y)) >= 128]
    if not visible:
        raise ValueError("native translation produced no visible pixels")
    strip = Image.new("RGB", (len(visible), 1))
    strip.putdata(visible)
    quant = strip.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
    raw_palette = quant.getpalette() or []
    snapped: list[tuple[int, int, int]] = []
    for idx in sorted(set(quant.tobytes())):
        color = tuple(raw_palette[idx * 3:idx * 3 + 3])
        grid_color = tuple(snap9(channel) for channel in color)
        if grid_color not in snapped:
            snapped.append(grid_color)
    if not snapped:
        raise ValueError("palette compaction produced no visible colors")

    out = Image.new("P", rgba.size, 0)
    flat_palette = [0, 0, 0]
    for color in snapped:
        flat_palette.extend(color)
    flat_palette.extend([0, 0, 0] * (256 - len(snapped) - 1))
    out.putpalette(flat_palette)
    dst = out.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            if alpha.getpixel((x, y)) < 128:
                continue
            color = rgb.getpixel((x, y))
            nearest = min(range(len(snapped)),
                          key=lambda i: sum((color[c] - snapped[i][c]) ** 2 for c in range(3)))
            dst[x, y] = nearest + 1
    out.info["transparency"] = 0
    return out


def fit_native(source: Path, width: int, height: int) -> tuple[Image.Image, dict]:
    src = Image.open(source).convert("RGB")
    mask, matte_report = foreground_matte.extract_foreground_mask(src)
    if matte_report["status"] != "passed":
        raise ValueError("foreground matte rejected: " + ",".join(matte_report["blocking_statuses"]))
    src, mask = crop_to_foreground(src, mask)
    # Preserve the whole figure in the target cell with a small breathing
    # margin.  This is an assisted native translation study, never a promoted
    # runtime asset and never a source for a later generation.
    margin_x = max(2, width // 16)
    margin_y = max(2, height // 24)
    box_w = width - 2 * margin_x
    box_h = height - 2 * margin_y
    scale = min(box_w / src.width, box_h / src.height)
    dst_w = max(1, int(round(src.width * scale)))
    dst_h = max(1, int(round(src.height * scale)))
    pixel_contract.assert_nearest_resample("NEAREST")
    art = src.resize((dst_w, dst_h), Image.Resampling.NEAREST)
    alpha = mask.resize((dst_w, dst_h), Image.Resampling.NEAREST).point(
        lambda v: 255 if v else 0)
    rgba = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = (width - dst_w) // 2
    y = max(0, height - margin_y - dst_h)
    rgba.paste(art.convert("RGBA"), (x, y), alpha)

    return _quantize_visible(rgba), matte_report


def write_rgba_overlay(native: Image.Image, path: Path, kind: str) -> None:
    rgba = native.convert("RGBA")
    alpha = rgba.getchannel("A")
    bg_rgb = {"light": (238, 238, 230), "dark": (28, 30, 38),
              "chroma": (238, 0, 238)}[kind]
    bg = Image.new("RGBA", rgba.size, bg_rgb + (255,))
    bg.alpha_composite(rgba)
    bg.save(path)


def semantic_map(native: Image.Image, path: Path) -> dict[str, int]:
    alpha = native.convert("RGBA").getchannel("A")
    out = Image.new("P", native.size, 0)
    semantic_palette = [0, 0, 0]
    for i in range(1, 9):
        semantic_palette.extend((34 * min(i, 7), 34 * ((i + 2) % 8),
                                 34 * ((i + 4) % 8)))
    semantic_palette.extend([0, 0, 0] * (256 - 9))
    out.putpalette(semantic_palette)
    apx, opx = alpha.load(), out.load()
    counts = {name: 0 for name in REGIONS}

    def region(x: int, y: int) -> str:
        nx, ny = x / native.width, y / native.height
        if ny < 0.24:
            return "hair" if nx < 0.32 or nx > 0.68 else "head_or_face"
        if ny < 0.30:
            return "head_or_face"
        if ny < 0.52 and (nx < 0.28 or nx > 0.72):
            return "hands" if ny < 0.43 else "arms_or_guard"
        if ny < 0.58:
            return "torso"
        if ny >= 0.84:
            return "feet"
        if nx > 0.58 and ny > 0.46:
            return "sash"
        return "legs"

    for y in range(native.height):
        for x in range(native.width):
            if apx[x, y] >= 128:
                name = region(x, y)
                opx[x, y] = LABELS[name]
                counts[name] += 1

    out.save(path, "PNG", bits=4)
    return counts


def silhouette(native: Image.Image, path: Path) -> None:
    alpha = native.convert("RGBA").getchannel("A")
    out = Image.new("P", native.size, 0)
    out.putpalette([0, 0, 0, 32, 32, 48] + [0, 0, 0] * 254)
    for y in range(native.height):
        for x in range(native.width):
            if alpha.getpixel((x, y)) >= 128:
                out.putpixel((x, y), 1)
    out.save(path, "PNG", bits=1, transparency=0)


def contour(native: Image.Image, path: Path) -> None:
    alpha = native.convert("RGBA").getchannel("A")
    out = Image.new("P", native.size, 0)
    out.putpalette([0, 0, 0, 64, 32, 72, 224, 180, 72] + [0, 0, 0] * 253)
    for y in range(native.height):
        for x in range(native.width):
            if alpha.getpixel((x, y)) < 128:
                continue
            edge = any(nx < 0 or ny < 0 or nx >= native.width or ny >= native.height or
                       alpha.getpixel((nx, ny)) < 128
                       for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
            out.putpixel((x, y), 1 if edge else 2)
    out.save(path, "PNG", bits=2, transparency=0)


def build_one(source: Path, out_root: Path, asset_id: str, width: int, height: int) -> dict:
    scale = f"{width}x{height}"
    root = out_root / asset_id
    source_dir = root / "source"
    evidence_dir = root / "evidence"
    shape_dir = root / "shape_block"
    for d in (source_dir, evidence_dir, shape_dir):
        d.mkdir(parents=True, exist_ok=True)
    persisted_source = source_dir / source.name
    if source.resolve() != persisted_source.resolve():
        shutil.copy2(source, persisted_source)

    native, matte_report = fit_native(persisted_source, width, height)
    candidate = root / f"{asset_id}.png"
    native.save(candidate, "PNG", bits=4, transparency=0)
    native = Image.open(candidate).convert("P")
    native.info["transparency"] = 0
    pc = pixel_contract.validate_png(candidate, pixel_contract.ROLE_TRANSPARENT0)
    with Image.open(candidate) as saved:
        transparent = {0}
        palette = saved.getpalette() or []
        visible_indices = {idx for idx in saved.tobytes() if idx not in transparent}
        visible_rgb_colors = len({tuple(palette[idx * 3:idx * 3 + 3])
                                  for idx in visible_indices
                                  if idx * 3 + 3 <= len(palette)})
    alpha = native.convert("RGBA").getchannel("A")
    bbox = alpha.getbbox()
    filled = sum(1 for yy in range(height) for xx in range(width)
                 if alpha.getpixel((xx, yy)) >= 128)
    pixel_report_path = root / "pixel_compliance_report.json"
    pixel_report_path.write_text(json.dumps({
        "schema_version": "1.0.0",
        "tool": pc["tool"], "tool_version": pc["tool_version"],
        "asset_id": asset_id, "candidate_path": str(candidate.relative_to(out_root.parent.parent.parent)),
        "candidate_sha256": sha(candidate), "content_sha256": pc["content_sha256"],
        "width": width, "height": height, "mode": "P", "bit_depth": pc["bit_depth"],
        "color_type": pc["color_type"], "transparent_index": 0,
        "visible_colors": visible_rgb_colors, "filled_pixels": filled,
        "canvas_pixels": width * height,
        "bbox": list(bbox) if bbox else None,
        "occupancy_pct": round(filled / (width * height) * 100, 2),
        "status": pc["status"], "blocking_statuses": pc.get("blocking_statuses", []),
    }, indent=2) + "\n", encoding="utf-8")
    matte_report["input_source_path"] = str(persisted_source.relative_to(out_root.parent.parent.parent))
    matte_report["input_source_sha256"] = sha(persisted_source)
    matte_report_path = root / "foreground_matte_report.json"
    matte_report_path.write_text(json.dumps(matte_report, indent=2) + "\n", encoding="utf-8")
    native_1x = evidence_dir / "native_1x.png"
    shutil.copy2(candidate, native_1x)
    nearest = evidence_dir / "nearest_8x.png"
    nearest_img = native.resize((width * 8, height * 8), Image.Resampling.NEAREST)
    nearest_img.info["transparency"] = 0
    nearest_img.save(nearest, "PNG", transparency=0)
    light = evidence_dir / "light_background.png"
    dark = evidence_dir / "dark_background.png"
    chroma = evidence_dir / "chroma_background.png"
    write_rgba_overlay(native, light, "light")
    write_rgba_overlay(native, dark, "dark")
    write_rgba_overlay(native, chroma, "chroma")
    sil = shape_dir / "silhouette_mask.png"
    sem = shape_dir / "semantic_region_map.png"
    con = shape_dir / "contour_overlay.png"
    silhouette(native, sil)
    counts = semantic_map(native, sem)
    contour(native, con)
    artifacts = {}
    for role, p in (("silhouette_mask", sil), ("semantic_region_map", sem), ("contour_overlay", con)):
        artifacts[role] = {"path": str(p.relative_to(out_root.parent.parent.parent)),
                           "sha256": sha(p), "asset_id": asset_id,
                           "scale": scale, "source": str(candidate.relative_to(out_root.parent.parent.parent))}
    return {
        "asset_id": asset_id, "scale": scale, "width": width, "height": height,
        "source_path": str(persisted_source.relative_to(out_root.parent.parent.parent)),
        "source_sha256": sha(persisted_source),
        "candidate_path": str(candidate.relative_to(out_root.parent.parent.parent)),
        "candidate_sha256": sha(candidate),
        "pixel_report_path": str(pixel_report_path.relative_to(out_root.parent.parent.parent)),
        "foreground_matte_report_path": str(matte_report_path.relative_to(out_root.parent.parent.parent)),
        "native_1x_path": str(native_1x.relative_to(out_root.parent.parent.parent)),
        "nearest_path": str(nearest.relative_to(out_root.parent.parent.parent)),
        "light_path": str(light.relative_to(out_root.parent.parent.parent)),
        "dark_path": str(dark.relative_to(out_root.parent.parent.parent)),
        "chroma_path": str(chroma.relative_to(out_root.parent.parent.parent)),
        "shape_artifacts": artifacts,
        "semantic_label_legend": LABELS,
        "semantic_label_counts": counts,
        "semantic_map_method": "geometric_prescreen_only_requires_visual_verification",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    sources = sorted(args.source_dir.glob("*.png"))
    specs = []
    for source in sources:
        stem = source.stem.replace("_source", "")
        if "48x64" in stem:
            specs.append((source, stem, 48, 64))
        elif "64x96" in stem:
            specs.append((source, stem, 64, 96))
    if len(specs) != 4:
        raise SystemExit(f"expected 4 persisted studies, found {len(specs)}")
    records = [build_one(source, args.output_dir, asset_id, width, height)
               for source, asset_id, width, height in specs]
    manifest = args.output_dir / "challenger_package_manifest.json"
    manifest.write_text(json.dumps({"schema_version": "1.0.0", "review_only": True,
                                    "generation_source": "approved_model_sheet_only",
                                    "candidates": records}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest), "candidates": records}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

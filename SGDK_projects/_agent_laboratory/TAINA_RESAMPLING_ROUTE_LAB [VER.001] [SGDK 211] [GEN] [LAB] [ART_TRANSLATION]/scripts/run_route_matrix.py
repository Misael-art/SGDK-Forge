#!/usr/bin/env python3
"""Deterministic stage-1 resampling laboratory.

All outputs are raw geometry probes.  This script does not quantize to a VDP
palette and does not author a character; it only resamples one normalized,
alpha-matted source through named algorithms and writes diagnostic evidence.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw


TARGET = (56, 80)
CROP = (114, 28, 933, 1450)
IM_FILTERS = {
    "im_nearest": ("Point", {}), "im_box_area": ("Box", {}),
    "im_bilinear_triangle": ("Triangle", {}), "im_bicubic": ("Cubic", {}),
    "im_lanczos2": ("Lanczos2", {}), "im_lanczos3": ("Lanczos", {}),
    "im_mitchell_netravali": ("Mitchell", {}), "im_catmull_rom": ("Catrom", {}),
    "im_b_spline": ("Spline", {}),
}
PIL_FILTERS = {
    "pil_nearest": Image.Resampling.NEAREST, "pil_box": Image.Resampling.BOX,
    "pil_bilinear": Image.Resampling.BILINEAR, "pil_hamming": Image.Resampling.HAMMING,
    "pil_bicubic": Image.Resampling.BICUBIC, "pil_lanczos": Image.Resampling.LANCZOS,
}
CV_FILTERS = {
    "cv_nearest": cv2.INTER_NEAREST, "cv_area": cv2.INTER_AREA,
    "cv_linear": cv2.INTER_LINEAR, "cv_cubic": cv2.INTER_CUBIC,
    "cv_lanczos4": cv2.INTER_LANCZOS4,
}
GIMP_FILTERS = ["gimp_none", "gimp_linear", "gimp_cubic", "gimp_nohalo", "gimp_lohalo"]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def command_version(command, args):
    try:
        return subprocess.run([command, *args], capture_output=True, text=True, timeout=10).stdout.strip().splitlines()[0]
    except Exception:
        return "unavailable"


def premultiplied_source(source):
    rgb = np.array(source.convert("RGB"), dtype=np.int16)
    bg = np.array([252, 245, 232], dtype=np.int16)
    distance = np.max(np.abs(rgb - bg), axis=2)
    alpha = np.clip((distance.astype(np.float32) - 12.0) * 255.0 / 28.0, 0, 255).astype(np.uint8)
    rgba = np.dstack([rgb.astype(np.uint8), alpha])
    rgba[:, :, :3] = (rgba[:, :, :3].astype(np.uint16) * alpha[:, :, None] // 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def fit_canvas(image):
    image = image.convert("RGBA")
    ratio = min(TARGET[0] / image.width, TARGET[1] / image.height)
    size = (max(1, round(image.width * ratio)), max(1, round(image.height * ratio)))
    resized = image.resize(size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", TARGET, (0, 0, 0, 0))
    x = (TARGET[0] - size[0]) // 2
    y = TARGET[1] - size[1]
    canvas.alpha_composite(resized, (x, y))
    return canvas


def pillow_route(source, resample):
    ratio = min(TARGET[0] / source.width, TARGET[1] / source.height)
    size = (max(1, round(source.width * ratio)), max(1, round(source.height * ratio)))
    resized = source.resize(size, resample)
    canvas = Image.new("RGBA", TARGET, (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((TARGET[0] - size[0]) // 2, TARGET[1] - size[1]))
    return canvas


def cv_route(source, interpolation):
    rgba = np.array(source.convert("RGBA"))
    ratio = min(TARGET[0] / rgba.shape[1], TARGET[1] / rgba.shape[0])
    size = (max(1, round(rgba.shape[1] * ratio)), max(1, round(rgba.shape[0] * ratio)))
    resized = cv2.resize(rgba, size, interpolation=interpolation)
    canvas = np.zeros((TARGET[1], TARGET[0], 4), dtype=np.uint8)
    x = (TARGET[0] - size[0]) // 2
    canvas[TARGET[1] - size[1]:, x:x + size[0]] = resized
    return Image.fromarray(canvas, "RGBA")


def save_rgba(image, path):
    image.save(path, "PNG")


def derived_evidence(image, directory):
    directory.mkdir(parents=True, exist_ok=True)
    image.save(directory / "raw_rgba_56x80.png", "PNG")
    image.resize((448, 640), Image.Resampling.NEAREST).save(directory / "preview_nearest_8x.png", "PNG")
    alpha = image.getchannel("A")
    alpha.point(lambda p: 255 if p >= 128 else 0).save(directory / "silhouette_binary.png", "PNG")
    edges = ImageChops.subtract(alpha, alpha.filter(ImageFilter.MinFilter(3))) if False else None
    # A simple edge diagnostic is intentionally derived from alpha only.
    arr = np.array(alpha)
    edge = np.zeros_like(arr)
    edge[1:, :] = np.maximum(edge[1:, :], np.abs(arr[1:].astype(int) - arr[:-1].astype(int)).astype(np.uint8))
    edge[:, 1:] = np.maximum(edge[:, 1:], np.abs(arr[:, 1:].astype(int) - arr[:, :-1].astype(int)).astype(np.uint8))
    Image.fromarray(edge, "L").save(directory / "edge_map.png", "PNG")
    for name, rgb in (("light", (238, 238, 230)), ("dark", (28, 30, 38)), ("chroma", (238, 0, 238))):
        bg = Image.new("RGBA", TARGET, rgb + (255,)); bg.alpha_composite(image)
        bg.convert("RGB").save(directory / f"background_{name}.png", "PNG")
    scene = Image.new("RGBA", (320, 224), (68, 102, 102, 255)); ImageDraw.Draw(scene).rectangle((0, 168, 319, 223), fill=(34, 34, 68, 255)); scene.alpha_composite(image, (132, 88)); scene.convert("RGB").save(directory / "composition_320x224.png", "PNG")
    crops = {"head_face": (8, 0, 48, 24), "shoulders_guard": (4, 14, 52, 34), "waist_hip": (10, 28, 48, 50), "knees": (8, 46, 50, 68), "feet": (6, 66, 52, 80)}
    for name, box in crops.items(): image.crop(box).resize(((box[2]-box[0])*8, (box[3]-box[1])*8), Image.Resampling.NEAREST).save(directory / f"crop_{name}.png", "PNG")
    rgba = np.array(image.convert("RGBA")); alpha = rgba[:, :, 3]
    transparent_rgb_nonzero = int(np.count_nonzero(np.any(rgba[:, :, :3] != 0, axis=2) & (alpha == 0)))
    (directory / "matte_halo_report.json").write_text(json.dumps({"schema_version": "matte_halo_report.v1", "status": "passed" if transparent_rgb_nonzero == 0 else "failed", "alpha_policy": "premultiplied_before_filter_then_rgba_probe", "transparent_rgb_nonzero": transparent_rgb_nonzero, "partial_alpha_pixels": int(np.count_nonzero((alpha > 0) & (alpha < 255))), "halo_cleanup": "not_applied_in_raw_geometry_stage", "interpretation": "stage-1 raw output only; perceptual edge review remains human"}, indent=2) + "\n", encoding="utf-8")


def metrics(image):
    alpha = np.array(image.getchannel("A"))
    visible = alpha > 0
    ys, xs = np.where(visible)
    if len(xs) == 0: bbox = None
    else: bbox = [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
    rows = np.count_nonzero(visible, axis=1); cols = np.count_nonzero(visible, axis=0)
    partial = int(np.count_nonzero((alpha > 0) & (alpha < 255)))
    return {"occupancy_pixels": int(visible.sum()), "occupancy_pct": round(float(visible.mean() * 100), 3), "bbox": bbox, "row_span": int(np.count_nonzero(rows)), "column_span": int(np.count_nonzero(cols)), "partial_alpha_pixels": partial, "silhouette_thresholds": {str(t): int(np.count_nonzero(alpha >= t)) for t in (1, 64, 128, 224)}}


def landmarks(image):
    alpha = np.array(image.getchannel("A")); visible = alpha >= 128
    def band(name, y0, y1, x0=0, x1=56):
        area = visible[y0:y1, x0:x1]
        ys, xs = np.where(area)
        if not len(xs): return {"status": "missing"}
        return {"status": "ambiguous", "observed_pixels": int(len(xs)), "roi": [x0, y0, x1, y1]}
    return {"hair_top_and_width": band("hair", 0, 18), "head_center": band("head", 4, 25, 12, 44), "eye_line": band("eyes", 10, 25, 14, 44), "shoulders": band("shoulders", 18, 34, 4, 52), "guard_and_wrists": band("guard", 14, 36, 0, 56), "waist_hip": band("hip", 28, 50, 8, 50), "knees": band("knees", 48, 68, 4, 52), "feet_ground": band("feet", 66, 80, 0, 56), "line_of_action": {"status": "ambiguous", "reason": "requires perceptual review, not inferred from filter output"}}


def run_im(route_id, filt, out):
    cmd = ["magick", str(out["canonical"]), "-filter", filt, "-resize", "56x80", "-gravity", "South", "-background", "none", "-extent", "56x80", f"PNG32:{out['raw']}"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return proc, cmd


def route_definitions():
    defs = []
    for rid, (filt, params) in IM_FILTERS.items(): defs.append((rid, "ImageMagick", filt, params))
    for rid, filt in PIL_FILTERS.items(): defs.append((rid, "Pillow", getattr(filt, "name", str(filt)), {"resampling": getattr(filt, "name", str(filt))}))
    for rid, filt in CV_FILTERS.items(): defs.append((rid, "OpenCV", rid.split("_", 1)[1], {"interpolation": int(filt)}))
    for rid in GIMP_FILTERS: defs.append((rid, "GIMP Console", rid.split("_", 1)[1], {"batch_only": True}))
    return defs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--lab-root", type=Path, required=True); ap.add_argument("--repeat", action="store_true")
    args = ap.parse_args(); lab = args.lab_root.resolve(); inp = lab / "inputs"; source_path = inp / "approved_direction_56x80.png"
    output = lab / ("route_reports_repeat" if args.repeat else "route_reports"); output.mkdir(parents=True, exist_ok=True)
    with Image.open(source_path) as source:
        canonical = premultiplied_source(source.crop(CROP))
    canonical_path = inp / "canonical_crop_premultiplied.png"
    if not canonical_path.exists() or not args.repeat: canonical.save(canonical_path, "PNG")
    canonical_path = canonical_path.resolve()
    results = []
    for rid, tool, algorithm, params in route_definitions():
        directory = output / rid; directory.mkdir(parents=True, exist_ok=True); raw = directory / "raw_rgba_56x80.png"; started = time.perf_counter(); warnings = []
        status = "passed"; command = None; version = ""
        try:
            if tool == "ImageMagick":
                proc, command = run_im(rid, algorithm, {"canonical": canonical_path, "raw": raw}); version = command_version("magick", ["--version"])
                if proc.returncode != 0: raise RuntimeError(proc.stderr.strip() or "ImageMagick failed")
            elif tool == "Pillow":
                with Image.open(canonical_path) as src: save_rgba(pillow_route(src, PIL_FILTERS[rid]), raw)
                version = f"Pillow {Image.__version__}"
            elif tool == "OpenCV":
                with Image.open(canonical_path) as src: save_rgba(cv_route(src, CV_FILTERS[rid]), raw)
                version = f"OpenCV {cv2.__version__}"
            else:
                command = ["gimp-console", "--no-interface", "--batch-interpreter=plug-in-script-fu", "--batch", "(gimp-quit 0)"]
                version = command_version("gimp-console", ["--version"])
                status = "skipped"; warnings.append("GIMP batch attempts timed out without deterministic export; route intentionally skipped and does not block the matrix.")
        except Exception as exc:
            if tool == "GIMP Console":
                status = "skipped"; warnings.append("GIMP batch bridge did not complete a deterministic export: " + str(exc))
            else:
                status = "failed"; warnings.append(str(exc))
        elapsed = round(time.perf_counter() - started, 6)
        if raw.exists():
            with Image.open(raw) as image: image = image.convert("RGBA"); derived_evidence(image, directory); measured = metrics(image); lm = landmarks(image)
            raw_sha = sha(raw)
        else: measured = {}; lm = {}; raw_sha = None
        report = {"schema_version": "mechanical_geometry_probe.v1", "route_id": rid, "tool": tool, "tool_version": version, "algorithm": algorithm, "parameters": params, "source": {"path": "inputs/approved_direction_56x80.png", "sha256": sha(source_path)}, "canonical_crop": {"path": "inputs/canonical_crop_premultiplied.png", "sha256": sha(canonical_path), "crop_xyxy_source": list(CROP)}, "target": "56x80", "colorspace": "sRGB", "alpha_policy": "premultiplied_before_filter_then_rgba_probe", "output": {"path": str((directory / "raw_rgba_56x80.png").relative_to(lab)) if raw.exists() else None, "sha256": raw_sha}, "elapsed_seconds": elapsed, "status": status, "warnings": warnings, "metrics": measured, "landmarks": lm, "command": command, "claim_ceiling": "mechanical_geometry_probe"}
        (directory / "route_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"); results.append(report)
    matrix = {"schema_version": "route_matrix.v1", "stage": 1, "status": "completed_with_skips", "source_policy": "identity model sheet remains authoritative; approved 56x80 source is directional only; no v01-v04 pixels used", "target": "56x80", "routes": results, "executed": sum(r["status"] == "passed" for r in results), "skipped": sum(r["status"] == "skipped" for r in results), "failed": sum(r["status"] == "failed" for r in results), "no_native_candidate": True}
    (lab / ("route_matrix_repeat.json" if args.repeat else "route_matrix.json")).write_text(json.dumps(matrix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": matrix["status"], "executed": matrix["executed"], "skipped": matrix["skipped"], "failed": matrix["failed"], "repeat": args.repeat}, ensure_ascii=False))


if __name__ == "__main__": main()

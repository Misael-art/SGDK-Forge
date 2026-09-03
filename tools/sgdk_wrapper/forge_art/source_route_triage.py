"""Source sanitation and deterministic route exploration for raster art.

This module does not author pixels and never produces a native/final asset. It
audits whether a source is safe for translation, executes mechanical resampling
routes through owned wrappers, binds every result to its causal input and emits
compact visual evidence for a later visual/native-authoring decision.
"""
from __future__ import annotations

import hashlib
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFont

from forge_art import foreground_matte, schema_gate


TOOL_NAME = "forge_art.source_route_triage"
TOOL_VERSION = "1.0.0"
REGISTRY_PATH = Path(__file__).with_name("route_prior_registry.json")
EFFECT_FIELDS = (
    "ground_shadow", "dust_or_particles", "smoke_or_clouds", "floor_line",
    "text_or_annotation",
)
BOOLEAN_CONTAMINANTS = (
    "baked_checkerboard", "multiple_overlapping_poses", "cropped_extremities",
    "occluded_identity_features", "motion_blur", "background_color_collision",
)
PIL_FILTERS = {
    "pil_nearest": Image.Resampling.NEAREST,
    "pil_box": Image.Resampling.BOX,
    "pil_bilinear": Image.Resampling.BILINEAR,
    "pil_hamming": Image.Resampling.HAMMING,
    "pil_bicubic": Image.Resampling.BICUBIC,
    "pil_lanczos": Image.Resampling.LANCZOS,
}
IM_FILTERS = {
    "im_nearest": "Point", "im_box_area": "Box",
    "im_bilinear_triangle": "Triangle", "im_bicubic": "Cubic",
    "im_lanczos2": "Lanczos2", "im_lanczos3": "Lanczos",
    "im_mitchell_netravali": "Mitchell", "im_catmull_rom": "Catrom",
    "im_b_spline": "Spline",
}
CV_FILTERS = {
    "cv_nearest": "INTER_NEAREST", "cv_area": "INTER_AREA",
    "cv_linear": "INTER_LINEAR", "cv_cubic": "INTER_CUBIC",
    "cv_lanczos4": "INTER_LANCZOS4",
}


class TriageError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TriageError(f"json_root_not_object:{path}")
    return value


def _registry() -> dict[str, Any]:
    value = _load_json(REGISTRY_PATH)
    schema_gate.validate_named(value, "route_prior_registry")
    route_ids = [route["route_id"] for route in value["routes"]]
    if len(route_ids) != len(set(route_ids)):
        raise TriageError("duplicate_route_id_in_registry")
    known = set(route_ids)
    for source_class, profile in value["source_classes"].items():
        expected_keys = {"evidence_confidence", "preferred_prior",
                         "viable_challenger", "experimental",
                         "negative_control", "host_optional_unavailable", "notes"}
        if not isinstance(profile, dict) or set(profile) != expected_keys:
            raise TriageError(f"invalid_source_class_profile:{source_class}")
        classified: list[str] = []
        for category in ("preferred_prior", "viable_challenger", "experimental",
                         "negative_control", "host_optional_unavailable"):
            if not isinstance(profile[category], list) or not all(
                    isinstance(route_id, str) for route_id in profile[category]):
                raise TriageError(f"invalid_route_category:{source_class}:{category}")
            classified.extend(profile[category])
        if len(classified) != len(set(classified)):
            raise TriageError(f"route_in_multiple_categories:{source_class}")
        if set(classified) != known:
            raise TriageError(f"route_registry_incomplete_for_source_class:{source_class}")
    return value


def _resolve_relative(root: Path, value: str, *, must_exist: bool = True) -> Path:
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        raise TriageError(f"non_portable_path:{value}")
    result = (root / rel).resolve()
    try:
        result.relative_to(root.resolve())
    except ValueError as exc:
        raise TriageError(f"path_escapes_project:{value}") from exc
    if must_exist and not result.exists():
        raise TriageError(f"path_not_found:{value}")
    return result


def _resolve_output(root: Path, value: str) -> Path:
    result = _resolve_relative(root, value, must_exist=False)
    rel = result.relative_to(root.resolve())
    if not rel.parts or rel.parts[0] not in {"out", "rascunho"}:
        raise TriageError(f"output_must_be_staging_or_evidence:{value}")
    return result


def _identity_binding(root: Path, spec: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Validate the identity authority before a translation source is accepted."""
    if spec["intended_role"] != "translation_source":
        return None, []
    blockers: list[str] = []
    try:
        authority = _resolve_relative(root, spec["identity_authority_path"])
        observed = _sha256(authority)
        if observed != spec["identity_authority_sha256"].lower():
            blockers.append("identity_authority_hash_mismatch")
        contract = _resolve_relative(root, spec["visual_source_of_truth_contract"])
        if not contract.is_file():
            blockers.append("visual_source_of_truth_contract_missing")
    except (KeyError, TriageError):
        blockers.append("identity_authority_missing")
        authority = None
        contract = None
        observed = None
    if not str(spec.get("derivation", "")).strip():
        blockers.append("identity_derivation_missing")
    binding = {
        "identity_authority_path": spec.get("identity_authority_path"),
        "identity_authority_sha256": spec.get("identity_authority_sha256"),
        "identity_authority_observed_sha256": observed,
        "visual_source_of_truth_contract": spec.get("visual_source_of_truth_contract"),
        "derivation": spec.get("derivation"),
    }
    return binding, list(dict.fromkeys(blockers))


def _human_review_binding(root: Path, spec: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Human labels are evidence only when linked to a real, hashed record."""
    if spec["reviewer"] not in {"human", "human_and_vision"}:
        return None, []
    blockers: list[str] = []
    try:
        record = _resolve_relative(root, spec["human_decision_record_path"])
        observed = _sha256(record)
        if observed != spec["human_decision_record_sha256"].lower():
            blockers.append("human_decision_record_hash_mismatch")
    except (KeyError, TriageError):
        blockers.append("human_decision_record_missing")
        observed = None
    return {
        "path": spec.get("human_decision_record_path"),
        "declared_sha256": spec.get("human_decision_record_sha256"),
        "observed_sha256": observed,
    }, blockers


def _alpha_metrics(image: Image.Image) -> dict[str, Any]:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    histogram = alpha.histogram()
    total = rgba.width * rgba.height
    partial = sum(histogram[1:255])
    visible = total - histogram[0]
    return {
        "width": rgba.width,
        "height": rgba.height,
        "source_mode": image.mode,
        "has_alpha_channel": "A" in image.getbands() or "transparency" in image.info,
        "alpha_extrema": list(alpha.getextrema()),
        "visible_pixels": visible,
        "partial_alpha_pixels": partial,
        "opaque_pixels": histogram[255],
        "alpha_bbox": list(alpha.getbbox()) if alpha.getbbox() else None,
    }


def _border_signal(image: Image.Image) -> dict[str, Any]:
    rgb = image.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    values = [px[x, 0] for x in range(w)] + [px[x, h - 1] for x in range(w)]
    if h > 2:
        values += [px[0, y] for y in range(1, h - 1)]
        values += [px[w - 1, y] for y in range(1, h - 1)]
    buckets: dict[tuple[int, int, int], int] = {}
    for color in values:
        key = tuple(channel // 16 for channel in color)
        buckets[key] = buckets.get(key, 0) + 1
    dominant = max(buckets.values(), default=0)
    return {
        "sampled_pixels": len(values),
        "quantized_border_buckets": len(buckets),
        "dominant_bucket_ratio": round(dominant / len(values), 4) if values else 0.0,
        "interpretation": "diagnostic_only_not_a_visual_contaminant_detector",
    }


def audit_source(project_root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    """Audit a source using explicit visual observations plus raw measurements."""
    schema_gate.validate_named(spec, "source_triage_spec")
    root = project_root.resolve()
    source = _resolve_relative(root, spec["source_path"])
    with Image.open(source) as opened:
        opened.load()
        measurements = _alpha_metrics(opened)
        border = _border_signal(opened)

    obs = spec["observations"]
    blockers: list[str] = []
    warnings: list[str] = []
    identity_binding, identity_blockers = _identity_binding(root, spec)
    human_review_binding, human_review_blockers = _human_review_binding(root, spec)
    blockers.extend(identity_blockers)
    blockers.extend(human_review_blockers)
    severe_effects = [name for name in EFFECT_FIELDS
                      if obs[name] in {"touching_silhouette", "covering_identity", "unknown"}]
    detached_effects = [name for name in EFFECT_FIELDS if obs[name] == "detached"]
    boolean_hits = [name for name in BOOLEAN_CONTAMINANTS if obs[name]]

    if obs["baked_checkerboard"]:
        blockers.append("baked_checkerboard_is_not_transparency")
    for name in severe_effects:
        blockers.append(f"{name}_{obs[name]}")
    for name in boolean_hits:
        blocker = f"{name}_blocks_direct_translation"
        if blocker not in blockers:
            blockers.append(blocker)

    direct = spec["intended_role"] == "translation_source"
    if direct:
        for name in detached_effects:
            blockers.append(f"{name}_must_be_removed_before_translation")
        if spec["matte_policy"] == "reference_only":
            blockers.append("reference_only_matte_cannot_enter_route_shootout")
        if spec["matte_policy"] == "existing_alpha" and not measurements["has_alpha_channel"]:
            blockers.append("declared_existing_alpha_is_absent")
        if spec["matte_policy"] == "border_connected" and obs["background_color_collision"]:
            blockers.append("border_matte_unsafe_with_background_color_collision")
    elif detached_effects:
        warnings.append("detached_effects_keep_source_reference_only")

    if measurements["partial_alpha_pixels"]:
        warnings.append("partial_alpha_requires_premultiplied_filtering_and_halo_review")
    if spec["source_class"] == "unclassified_raster":
        warnings.append("source_class_has_no_historical_route_favorite")

    blockers = list(dict.fromkeys(blockers))
    if direct and not blockers:
        status = "accepted_translation_source"
    elif spec["intended_role"] == "identity_authority" and not severe_effects and not boolean_hits:
        status = "accepted_identity_reference_only"
    else:
        status = "reference_only_requires_clean_source" if blockers else "accepted_reference_only"

    report = {
        "schema_version": "source_triage_report.v1",
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "source": {"path": spec["source_path"], "sha256": _sha256(source)},
        "source_class": spec["source_class"],
        "intended_role": spec["intended_role"],
        "reviewer": spec["reviewer"],
        "identity_binding": identity_binding,
        "human_review_binding": human_review_binding,
        "matte_policy": spec["matte_policy"],
        "observations": obs,
        "automatic_measurements": measurements,
        "border_signal": border,
        "status": status,
        "route_exploration_allowed": direct and not blockers,
        "blocking": bool(blockers),
        "blockers": blockers,
        "warnings": warnings,
        "safe_reference_roles": ([spec["intended_role"]] if spec["intended_role"] != "translation_source" else []),
        "next_action": (
            "run route-shootout; outputs remain mechanical guides"
            if direct and not blockers else
            "retain this file only in its safe reference role and obtain a clean single-pose source without shadow, dust, smoke, floor, checkerboard, labels or occlusion"
        ),
        "claim_ceiling": "source_triage_only",
    }
    return report


def write_source_audit(project_root: Path, spec_path: Path, out_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    spec = _load_json(spec_path)
    report = audit_source(root, spec)
    out = out_path.resolve()
    try:
        out.relative_to(root)
    except ValueError as exc:
        raise TriageError("source_audit_output_outside_project") from exc
    rel = out.relative_to(root)
    if not rel.parts or rel.parts[0] not in {"out", "rascunho"}:
        raise TriageError("source_audit_output_must_be_staging_or_evidence")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def _canonical_source(source: Path, matte_policy: str, source_class: str) -> tuple[Image.Image, dict[str, Any] | None]:
    with Image.open(source) as opened:
        opened.load()
        rgba = opened.convert("RGBA")
        matte_report = None
        if matte_policy == "border_connected":
            mask, matte_report = foreground_matte.extract_foreground_mask(opened)
            if matte_report["blocking_statuses"]:
                raise TriageError("foreground_matte_rejected:" + ",".join(matte_report["blocking_statuses"]))
            rgba.putalpha(mask)
        elif matte_policy != "existing_alpha":
            raise TriageError("route_shootout_requires_real_or_border_connected_alpha")
    bbox = rgba.getchannel("A").getbbox()
    if not bbox:
        raise TriageError("source_has_no_visible_foreground")
    # Native art is already authored in its gameplay canvas.  Cropping the
    # occupied bbox changes the scale contract and incorrectly rejects a
    # valid 32x32 cell whose character occupies fewer pixels.
    if source_class == "native_pixel_art_integer_scale":
        return rgba, matte_report
    return rgba.crop(bbox), matte_report


def _authorized_targets(root: Path, contract_path: str) -> tuple[set[tuple[int, int]], dict[str, Any]]:
    """Read an explicit project scale contract; never infer a target silently."""
    contract = _load_json(_resolve_relative(root, contract_path))
    scale = contract.get("scale_contract", contract)
    targets: set[tuple[int, int]] = set()
    entries = scale.get("authorized_targets") or scale.get("allowed_targets") or []
    for item in entries:
        if isinstance(item, dict) and "width" in item and "height" in item:
            targets.add((int(item["width"]), int(item["height"])))
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            targets.add((int(item[0]), int(item[1])))
    for w_key, h_key in (("target_width", "target_height"), ("selected_width", "selected_height")):
        if w_key in scale and h_key in scale:
            targets.add((int(scale[w_key]), int(scale[h_key])))
    nominal = scale.get("nominal_bbox_px")
    if isinstance(nominal, dict) and "w" in nominal and "h" in nominal:
        targets.add((int(nominal["w"]), int(nominal["h"])))
    if not targets:
        raise TriageError("scale_contract_has_no_authorized_target")
    return targets, contract


def _fit_size(size: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
    ratio = min(target[0] / size[0], target[1] / size[1])
    return max(1, round(size[0] * ratio)), max(1, round(size[1] * ratio))


def _place(resized: Image.Image, target: tuple[int, int], anchor: str) -> Image.Image:
    canvas = Image.new("RGBA", target, (0, 0, 0, 0))
    x = (target[0] - resized.width) // 2
    y = target[1] - resized.height if anchor == "bottom_center" else (target[1] - resized.height) // 2
    canvas.alpha_composite(resized.convert("RGBA"), (x, y))
    return canvas


def _pillow_route(source: Image.Image, target: tuple[int, int], anchor: str,
                  resample: Image.Resampling) -> Image.Image:
    size = _fit_size(source.size, target)
    # RGBa is premultiplied alpha in Pillow; this prevents colored matte halos.
    resized = source.convert("RGBa").resize(size, resample).convert("RGBA")
    return _place(resized, target, anchor)


def _imagemagick_route(source_path: Path, output_path: Path, target: tuple[int, int],
                       anchor: str, filter_name: str) -> list[str]:
    gravity = "South" if anchor == "bottom_center" else "Center"
    command = [
        "magick", str(source_path), "-alpha", "on", "-filter", filter_name,
        "-resize", f"{target[0]}x{target[1]}", "-gravity", gravity,
        "-background", "none", "-extent", f"{target[0]}x{target[1]}",
        f"PNG32:{output_path}",
    ]
    proc = subprocess.run(command, capture_output=True, text=True, timeout=45)
    if proc.returncode:
        raise TriageError("imagemagick_failed:" + (proc.stderr.strip() or str(proc.returncode)))
    return command


def _opencv_route(source: Image.Image, target: tuple[int, int], anchor: str,
                  algorithm: str) -> tuple[Image.Image, str]:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise TriageError("opencv_unavailable") from exc
    interpolation = getattr(cv2, algorithm)
    rgba = np.array(source.convert("RGBA"), dtype=np.float32)
    alpha = rgba[:, :, 3:4] / 255.0
    rgba[:, :, :3] *= alpha
    size = _fit_size(source.size, target)
    resized = cv2.resize(rgba, size, interpolation=interpolation)
    resized_alpha = resized[:, :, 3:4] / 255.0
    nonzero = resized_alpha[:, :, 0] > 0
    resized[nonzero, :3] /= resized_alpha[nonzero]
    resized[~nonzero, :3] = 0
    resized = np.clip(np.rint(resized), 0, 255).astype(np.uint8)
    canvas = np.zeros((target[1], target[0], 4), dtype=np.uint8)
    x = (target[0] - size[0]) // 2
    y = target[1] - size[1] if anchor == "bottom_center" else (target[1] - size[1]) // 2
    canvas[y:y + size[1], x:x + size[0]] = resized
    return Image.fromarray(canvas, "RGBA"), f"OpenCV {cv2.__version__}"


def _image_metrics(image: Image.Image) -> dict[str, Any]:
    alpha = image.getchannel("A")
    histogram = alpha.histogram()
    total = image.width * image.height
    return {
        "visible_pixels": total - histogram[0],
        "partial_alpha_pixels": sum(histogram[1:255]),
        "bbox": list(alpha.getbbox()) if alpha.getbbox() else None,
        "alpha_threshold_128_pixels": sum(histogram[128:]),
    }


def _save_evidence(image: Image.Image, directory: Path, target: tuple[int, int]) -> dict[str, str]:
    directory.mkdir(parents=True, exist_ok=False)
    raw = directory / "raw_rgba.png"
    image.save(raw, "PNG")
    preview = directory / "preview_nearest_8x.png"
    image.resize((target[0] * 8, target[1] * 8), Image.Resampling.NEAREST).save(preview, "PNG")
    silhouette = Image.new("RGBA", target, (0, 0, 0, 255))
    silhouette.putalpha(image.getchannel("A").point(lambda p: 255 if p >= 128 else 0))
    silhouette_path = directory / "silhouette.png"
    silhouette.save(silhouette_path, "PNG")
    backgrounds: dict[str, str] = {}
    for name, color in (("light", (238, 238, 230, 255)), ("dark", (24, 28, 38, 255)), ("chroma", (238, 0, 238, 255))):
        bg = Image.new("RGBA", target, color)
        bg.alpha_composite(image)
        path = directory / f"background_{name}.png"
        bg.convert("RGB").save(path, "PNG")
        backgrounds[name] = path.name
    scene = Image.new("RGBA", (320, 224), (62, 86, 96, 255))
    draw = ImageDraw.Draw(scene)
    draw.rectangle((0, 176, 319, 223), fill=(30, 38, 58, 255))
    scene.alpha_composite(image, ((320 - target[0]) // 2, 176 - target[1]))
    composition = directory / "composition_320x224.png"
    scene.convert("RGB").save(composition, "PNG")
    return {
        "raw": raw.name,
        "nearest_8x": preview.name,
        "silhouette": silhouette_path.name,
        "background_light": backgrounds["light"],
        "background_dark": backgrounds["dark"],
        "background_chroma": backgrounds["chroma"],
        "composition_320x224": composition.name,
    }


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/noto/NotoSans-Bold.ttf" if bold else "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _route_board(root: Path, output_dir: Path, routes: list[dict[str, Any]],
                 target: tuple[int, int], source_class: str) -> Path:
    cols, card_w, card_h, gap, side = 5, 260, 300, 14, 20
    rows = max(1, math.ceil(len(routes) / cols))
    board = Image.new("RGB", (side * 2 + cols * card_w + (cols - 1) * gap,
                              80 + rows * (card_h + gap) + side), (18, 20, 26))
    draw = ImageDraw.Draw(board)
    title = _font(25, True); label = _font(15, True); text = _font(12)
    draw.text((side, 14), "FORGE-ART ROUTE SHOOTOUT", font=title, fill=(245, 245, 245))
    draw.text((side, 48), f"{source_class} | guides only | no automatic winner", font=text, fill=(175, 185, 205))
    tones = {
        "preferred_prior": (36, 126, 82), "viable_challenger": (65, 108, 74),
        "experimental": (130, 101, 42), "negative_control": (150, 51, 51),
        "host_optional_unavailable": (76, 76, 80),
    }
    for index, route in enumerate(routes):
        row, col = divmod(index, cols)
        x = side + col * (card_w + gap); y = 80 + row * (card_h + gap)
        tone = tones.get(route["curatorial_prior"], (90, 90, 100))
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), 8, fill=(29, 31, 38), outline=tone, width=3)
        draw.rectangle((x + 3, y + 3, x + card_w - 3, y + 31), fill=tone)
        draw.text((x + 9, y + 7), route["route_id"], font=label, fill="white")
        image_box = (card_w - 18, 190)
        draw.rectangle((x + 9, y + 40, x + 9 + image_box[0], y + 40 + image_box[1]), fill=(220, 220, 208))
        if route["status"] == "passed":
            raw = root / route["output"]["path"]
            with Image.open(raw) as source:
                art = source.convert("RGBA").resize((target[0] * 2, target[1] * 2), Image.Resampling.NEAREST)
            board.paste(art, (x + 9 + (image_box[0] - art.width) // 2, y + 40 + (image_box[1] - art.height) // 2), art)
        else:
            draw.text((x + 65, y + 122), route["status"].upper(), font=label, fill=(90, 90, 95))
        draw.text((x + 9, y + 238), f'{route["backend"]} / {route["algorithm"]}', font=text, fill=(190, 198, 215))
        draw.text((x + 9, y + 258), route["curatorial_prior"], font=text, fill=(255, 226, 160))
        draw.text((x + 9, y + 278), "mechanical guide only", font=text, fill=(150, 157, 170))
    path = output_dir / "route_exploration_board.png"
    board.save(path, "PNG")
    return path


def _selected_routes(registry: dict[str, Any], source_class: str, policy: str,
                     include_negative: bool, include_unavailable: bool) -> list[tuple[dict[str, Any], str]]:
    profile = registry["source_classes"][source_class]
    category_for: dict[str, str] = {}
    categories = ["preferred_prior", "viable_challenger", "experimental"]
    if include_negative:
        categories.append("negative_control")
    if include_unavailable:
        categories.append("host_optional_unavailable")
    for category in categories:
        for route_id in profile.get(category, []):
            category_for[route_id] = category
    if policy == "preferred_plus_challengers":
        allowed = set(profile.get("preferred_prior", []) + profile.get("viable_challenger", []))
        if include_negative:
            allowed.update(profile.get("negative_control", []))
        if include_unavailable:
            allowed.update(profile.get("host_optional_unavailable", []))
    else:
        allowed = set(category_for)
    return [(route, category_for[route["route_id"]]) for route in registry["routes"]
            if route["route_id"] in allowed]


def _version(command: str, args: list[str]) -> str:
    try:
        proc = subprocess.run([command, *args], capture_output=True, text=True, timeout=10)
        output = proc.stdout.strip() or proc.stderr.strip()
        return output.splitlines()[0] if output else "unknown"
    except Exception:
        return "unavailable"


def _pairwise_deltas(root: Path, routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    passed = [route for route in routes if route["status"] == "passed"]
    pairs: list[dict[str, Any]] = []
    for index, left in enumerate(passed):
        with Image.open(root / left["output"]["path"]) as opened:
            a = opened.convert("RGBA")
        for right in passed[index + 1:]:
            with Image.open(root / right["output"]["path"]) as opened:
                b = opened.convert("RGBA")
            if a.size != b.size:
                continue
            difference = ImageChops.difference(a, b)
            changed = sum(1 for pixel in difference.get_flattened_data()
                          if pixel != (0, 0, 0, 0))
            ratio = changed / (a.width * a.height)
            if ratio < 0.01:
                pairs.append({
                    "left": left["route_id"], "right": right["route_id"],
                    "changed_pixels": changed, "canvas_ratio": round(ratio, 6),
                    "status": "near_duplicate_warning",
                })
    return pairs


def verify_shootout(project_root: Path, report: dict[str, Any]) -> dict[str, Any]:
    root = project_root.resolve(); blockers: list[str] = []
    registry = _registry(); definitions = {r["route_id"]: r for r in registry["routes"]}
    try:
        source = _resolve_relative(root, report["source"]["path"])
        if _sha256(source) != report["source"]["sha256"]:
            blockers.append("source_hash_mismatch")
        canonical = _resolve_relative(root, report["canonical_source"]["path"])
        if _sha256(canonical) != report["canonical_source"]["sha256"]:
            blockers.append("canonical_source_hash_mismatch")
    except (KeyError, TriageError):
        blockers.append("report_lineage_invalid")
    for route in report.get("routes", []):
        definition = definitions.get(route.get("route_id"))
        if not definition:
            blockers.append(f"unknown_route:{route.get('route_id')}")
            continue
        if route.get("backend") != definition["backend"] or route.get("algorithm") != definition["algorithm"]:
            blockers.append(f"route_label_not_causal:{route['route_id']}")
        if route.get("status") == "passed":
            output = route.get("output") or {}
            try:
                path = _resolve_relative(root, output["path"])
                if _sha256(path) != output["sha256"]:
                    blockers.append(f"output_hash_mismatch:{route['route_id']}")
                with Image.open(path) as image:
                    if list(image.size) != report["target"]["size"]:
                        blockers.append(f"output_dimensions_mismatch:{route['route_id']}")
            except (KeyError, TriageError, OSError):
                blockers.append(f"passed_route_missing_output:{route['route_id']}")
        elif route.get("output") is not None:
            blockers.append(f"skipped_route_has_output:{route['route_id']}")
    return {
        "status": "passed" if not blockers else "failed",
        "blocking": bool(blockers),
        "blockers": blockers,
        "claim_ceiling": "route_manifest_integrity_only",
    }


def run_shootout(project_root: Path, spec: dict[str, Any], *,
                  allowed_backends: set[str] | None = None) -> dict[str, Any]:
    schema_gate.validate_named(spec, "route_shootout_spec")
    root = project_root.resolve()
    source = _resolve_relative(root, spec["source_path"])
    triage_path = _resolve_relative(root, spec["source_triage_report_path"])
    triage = _load_json(triage_path)
    if triage.get("source", {}).get("sha256") != _sha256(source):
        raise TriageError("source_triage_hash_mismatch")
    if triage.get("source_class") != spec["source_class"]:
        raise TriageError("source_class_mismatch")
    if not triage.get("route_exploration_allowed") or triage.get("blocking"):
        raise TriageError("source_not_eligible_for_route_exploration")
    authorized_targets, _scale_contract = _authorized_targets(root, spec["scale_contract_path"])
    output_dir = _resolve_output(root, spec["output_dir"])
    if output_dir.exists() and any(output_dir.iterdir()):
        raise TriageError("route_output_dir_not_empty")
    target = (spec["target"]["width"], spec["target"]["height"])
    if target not in authorized_targets:
        raise TriageError("target_scale_not_authorized")
    output_dir.mkdir(parents=True, exist_ok=True)
    anchor = spec["target"]["anchor"]
    canonical, matte_report = _canonical_source(source, triage["matte_policy"], spec["source_class"])
    if spec["source_class"] == "native_pixel_art_integer_scale":
        if target == canonical.size:
            native_route = "native_same_canvas"
        elif target[0] % canonical.width or target[1] % canonical.height:
            raise TriageError("native_pixel_integer_scale_mismatch")
        else:
            native_route = "native_integer_scale"
    else:
        native_route = None
    canonical_path = output_dir / "canonical_source_rgba.png"
    canonical.save(canonical_path, "PNG")
    registry = _registry()
    definitions = _selected_routes(registry, spec["source_class"], spec["route_policy"],
                                   spec["include_negative_controls"],
                                   spec["include_unavailable_placeholders"])
    routes: list[dict[str, Any]] = []
    for definition, prior in definitions:
        route_id = definition["route_id"]; backend = definition["backend"]
        route_dir = output_dir / "routes" / route_id
        record: dict[str, Any] = {
            "route_id": route_id, "backend": backend,
            "algorithm": definition["algorithm"], "curatorial_prior": prior,
            "status": "skipped", "reason": None, "tool_version": None,
            "command": None, "output": None, "evidence": None,
            "metrics": None, "claim_ceiling": "mechanical_geometry_probe",
        }
        if allowed_backends is not None and backend not in allowed_backends:
            record["reason"] = "backend_excluded_by_test_or_host_policy"
            routes.append(record); continue
        try:
            if backend == "GIMP Console":
                record["reason"] = "gimp_batch_route_requires_separate_curated_operation; GUI is forbidden"
                routes.append(record); continue
            if backend == "Pillow":
                image = _pillow_route(canonical, target, anchor, PIL_FILTERS[route_id])
                record["tool_version"] = f"Pillow {Image.__version__}"
                record["command"] = [TOOL_NAME, "Pillow", route_id]
            elif backend == "ImageMagick":
                if not shutil.which("magick"):
                    raise TriageError("imagemagick_unavailable")
                route_dir.mkdir(parents=True, exist_ok=False)
                raw = route_dir / "raw_rgba.png"
                command = _imagemagick_route(canonical_path, raw, target, anchor, IM_FILTERS[route_id])
                with Image.open(raw) as opened:
                    image = opened.convert("RGBA")
                shutil.rmtree(route_dir)
                record["tool_version"] = _version("magick", ["--version"])
                record["command"] = command
            elif backend == "OpenCV":
                image, version = _opencv_route(canonical, target, anchor, CV_FILTERS[route_id])
                record["tool_version"] = version
                record["command"] = [TOOL_NAME, "OpenCV", CV_FILTERS[route_id]]
            else:
                raise TriageError("unsupported_backend")
            evidence = _save_evidence(image, route_dir, target)
            raw = route_dir / evidence["raw"]
            record.update({
                "status": "passed", "reason": None,
                "output": {"path": str(raw.relative_to(root)), "sha256": _sha256(raw)},
                "evidence": {name: str((route_dir / value).relative_to(root)) for name, value in evidence.items()},
                "metrics": _image_metrics(image),
                "causal_binding": {
                    "source_sha256": _sha256(source),
                    "canonical_source_sha256": _sha256(canonical_path),
                    "executor": TOOL_NAME,
                    "executor_version": TOOL_VERSION,
                },
            })
        except Exception as exc:
            if route_dir.exists():
                shutil.rmtree(route_dir)
            record["status"] = "skipped"
            record["reason"] = str(exc)
        routes.append(record)
    board = _route_board(root, output_dir, routes, target, spec["source_class"])
    report = {
        "schema_version": "route_shootout_report.v1",
        "tool": TOOL_NAME, "tool_version": TOOL_VERSION,
        "source": {"path": spec["source_path"], "sha256": _sha256(source)},
        "source_triage_report": {"path": spec["source_triage_report_path"], "sha256": _sha256(triage_path)},
        "canonical_source": {"path": str(canonical_path.relative_to(root)), "sha256": _sha256(canonical_path)},
        "source_class": spec["source_class"],
        "target": {"size": list(target), "anchor": anchor},
        "scale_contract": {
            "path": spec["scale_contract_path"],
            "sha256": _sha256(_resolve_relative(root, spec["scale_contract_path"])),
            "authorized_targets": [list(item) for item in sorted(authorized_targets)],
        },
        "route_policy": spec["route_policy"],
        "registry": {"path": str(REGISTRY_PATH), "sha256": _sha256(REGISTRY_PATH)},
        "matte_report": matte_report,
        "routes": routes,
        "executed": sum(route["status"] == "passed" for route in routes),
        "skipped": sum(route["status"] != "passed" for route in routes),
        "near_duplicate_warnings": _pairwise_deltas(root, routes),
        "board": {"path": str(board.relative_to(root)), "sha256": _sha256(board)},
        "automatic_winner": None,
        "winner_policy": "visual_and_identity_review_required_before_native_reauthoring",
        "native_candidate": False,
        "promotable": False,
        "res_promotion": False,
        "claim_ceiling": "mechanical_geometry_probe",
        "native_representation": native_route,
    }
    report["verification"] = verify_shootout(root, report)
    report_path = output_dir / "route_shootout_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def run_shootout_from_spec(project_root: Path, spec_path: Path) -> dict[str, Any]:
    return run_shootout(project_root, _load_json(spec_path))


def verify_shootout_file(project_root: Path, report_path: Path) -> dict[str, Any]:
    return verify_shootout(project_root, _load_json(report_path))


def self_check() -> dict[str, Any]:
    fixtures: list[dict[str, str]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        fixtures.append({"fixture": name, "status": "passed" if passed else "failed", "detail": detail})

    with tempfile.TemporaryDirectory(prefix="forge-art-route-") as temp:
        root = Path(temp)
        (root / "data/source_art").mkdir(parents=True)
        source = root / "data/source_art/clean.png"
        image = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
        image.paste((34, 68, 102, 255), (8, 4, 24, 46))
        image.save(source, "PNG")
        authority = root / "data/source_art/authority.png"
        image.save(authority, "PNG")
        contract = root / "data/source_art/visual_dna.json"
        contract.write_text(json.dumps({"scale_contract": {"authorized_targets": [{"width": 32, "height": 48}]}}), encoding="utf-8")
        authority_sha = _sha256(authority)

        def spec(**changes: Any) -> dict[str, Any]:
            value: dict[str, Any] = {
                "schema_version": "1.0.0", "source_path": "data/source_art/clean.png",
                "source_class": "high_res_full_body_character",
                "intended_role": "translation_source", "matte_policy": "existing_alpha",
                "reviewer": "agent_visual_triage",
                "identity_authority_path": "data/source_art/authority.png",
                "identity_authority_sha256": authority_sha,
                "visual_source_of_truth_contract": "data/source_art/visual_dna.json",
                "derivation": "fixture_translation_from_authority",
                "observations": {
                    "baked_checkerboard": False, "ground_shadow": "absent",
                    "dust_or_particles": "absent", "smoke_or_clouds": "absent",
                    "floor_line": "absent", "text_or_annotation": "absent",
                    "multiple_overlapping_poses": False, "cropped_extremities": False,
                    "occluded_identity_features": False, "motion_blur": False,
                    "background_color_collision": False, "notes": "fixture",
                },
            }
            value.update(changes)
            return value

        clean = audit_source(root, spec())
        add("clean_translation_source_passes", clean["route_exploration_allowed"], str(clean["blockers"]))
        bad_checker = spec(); bad_checker["observations"]["baked_checkerboard"] = True
        checker = audit_source(root, bad_checker)
        add("baked_checkerboard_rejected", "baked_checkerboard_is_not_transparency" in checker["blockers"], str(checker["blockers"]))
        bad_dust = spec(); bad_dust["observations"]["dust_or_particles"] = "touching_silhouette"
        dust = audit_source(root, bad_dust)
        add("touching_dust_rejected", any("dust_or_particles" in item for item in dust["blockers"]), str(dust["blockers"]))
        identity = spec(intended_role="identity_authority"); identity["observations"]["ground_shadow"] = "detached"
        identity_report = audit_source(root, identity)
        add("detached_shadow_kept_reference_only", not identity_report["route_exploration_allowed"], identity_report["status"])
        no_alpha = root / "data/source_art/no_alpha.png"; image.convert("RGB").save(no_alpha)
        no_alpha_spec = spec(source_path="data/source_art/no_alpha.png")
        no_alpha_report = audit_source(root, no_alpha_spec)
        add("missing_declared_alpha_rejected", "declared_existing_alpha_is_absent" in no_alpha_report["blockers"], str(no_alpha_report["blockers"]))

        (root / "out/logs").mkdir(parents=True)
        triage_path = root / "out/logs/source_triage_report.json"
        triage_path.write_text(json.dumps(clean), encoding="utf-8")
        shootout_spec = {
            "schema_version": "1.0.0", "source_path": "data/source_art/clean.png",
            "source_triage_report_path": "out/logs/source_triage_report.json",
            "source_class": "high_res_full_body_character",
            "scale_contract_path": "data/source_art/visual_dna.json",
            "output_dir": "out/route_fixture", "target": {"width": 32, "height": 48, "anchor": "bottom_center"},
            "route_policy": "all_applicable", "include_negative_controls": True,
            "include_unavailable_placeholders": True,
        }
        shootout = run_shootout(root, shootout_spec, allowed_backends={"Pillow"})
        add("shootout_emits_causal_routes", shootout["executed"] == len(PIL_FILTERS) and not shootout["verification"]["blocking"], str(shootout["verification"]))
        passed_route = next(route for route in shootout["routes"] if route["status"] == "passed")
        forged = json.loads(json.dumps(shootout)); forged_route = next(route for route in forged["routes"] if route["status"] == "passed")
        forged_route["algorithm"] = "FORGED"
        forged_check = verify_shootout(root, forged)
        add("forged_route_label_rejected", any("route_label_not_causal" in item for item in forged_check["blockers"]), str(forged_check["blockers"]))
        output_path = root / passed_route["output"]["path"]
        output_path.write_bytes(output_path.read_bytes() + b"tamper")
        tamper_check = verify_shootout(root, shootout)
        add("tampered_output_rejected", any("output_hash_mismatch" in item for item in tamper_check["blockers"]), str(tamper_check["blockers"]))

        divergent = spec(identity_authority_sha256="0" * 64)
        divergent_report = audit_source(root, divergent)
        add("divergent_identity_authority_rejected", "identity_authority_hash_mismatch" in divergent_report["blockers"], str(divergent_report["blockers"]))

        native = Image.new("RGB", (32, 32), (255, 0, 255))
        native.paste((34, 68, 102), (10, 7, 22, 28))
        native_path = root / "data/source_art/native.png"; native.save(native_path, "PNG")
        native_spec = spec(source_path="data/source_art/native.png", source_class="native_pixel_art_integer_scale", matte_policy="border_connected")
        native_triage = audit_source(root, native_spec)
        native_triage_path = root / "out/logs/native_source_triage.json"; native_triage_path.write_text(json.dumps(native_triage), encoding="utf-8")
        native_scale = root / "data/source_art/native_scale.json"; native_scale.write_text(json.dumps({"authorized_targets": [{"width": 32, "height": 32}, {"width": 48, "height": 48}]}), encoding="utf-8")
        native_shootout = {
            "schema_version": "1.0.0", "source_path": "data/source_art/native.png",
            "source_triage_report_path": "out/logs/native_source_triage.json",
            "source_class": "native_pixel_art_integer_scale", "scale_contract_path": "data/source_art/native_scale.json",
            "output_dir": "out/native_same_canvas", "target": {"width": 32, "height": 32, "anchor": "bottom_center"},
            "route_policy": "all_applicable", "include_negative_controls": False, "include_unavailable_placeholders": False,
        }
        native_result = run_shootout(root, native_shootout, allowed_backends={"Pillow"})
        canonical = Image.open(root / native_result["canonical_source"]["path"]).convert("RGBA")
        add("native_32_cell_keeps_canvas", native_result["native_representation"] == "native_same_canvas" and canonical.size == (32, 32), str(native_result["native_representation"]))
        add("native_content_preserved_inside_canvas", canonical.getpixel((0, 0))[3] == 0 and canonical.getpixel((12, 12))[3] == 255, str(canonical.size))

        non_integer = dict(native_shootout); non_integer["output_dir"] = "out/native_bad_scale"; non_integer["target"] = {"width": 48, "height": 48, "anchor": "bottom_center"}
        try: run_shootout(root, non_integer, allowed_backends={"Pillow"}); failed_scale = False
        except TriageError as exc: failed_scale = str(exc) == "native_pixel_integer_scale_mismatch"
        add("native_non_integer_scale_rejected", failed_scale, "native_pixel_integer_scale_mismatch")

        unauthorized = dict(native_shootout); unauthorized["output_dir"] = "out/native_unauthorized"; unauthorized["target"] = {"width": 24, "height": 32, "anchor": "bottom_center"}
        try: run_shootout(root, unauthorized, allowed_backends={"Pillow"}); failed_target = False
        except TriageError as exc: failed_target = str(exc) == "target_scale_not_authorized"
        add("target_outside_scale_contract_rejected", failed_target, "target_scale_not_authorized")

        human_without_record = dict(spec(reviewer="human")); human_without_record.pop("identity_authority_path", None); human_without_record.pop("identity_authority_sha256", None)
        try: audit_source(root, human_without_record); failed_human = False
        except schema_gate.SchemaError: failed_human = True
        add("human_reviewer_without_record_rejected", failed_human, "schema gate")

    failed = [fixture for fixture in fixtures if fixture["status"] != "passed"]
    return {
        "tool": TOOL_NAME, "tool_version": TOOL_VERSION,
        "fixtures_total": len(fixtures), "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures, "blocking": bool(failed),
    }

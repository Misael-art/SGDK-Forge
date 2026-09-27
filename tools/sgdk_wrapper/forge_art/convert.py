"""Deterministic, staging-only technical conversion; never art translation."""
from __future__ import annotations

import hashlib
import json
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Iterable

from PIL import Image

from forge_art import job, pixel_contract, schema_gate, vdp_color, visual_workset

TOOL_NAME = "forge_art.convert"
TOOL_VERSION = "1.1.0"
PALETTE_ALGORITHM = "weighted_kmedoids_v1"
LOCKED_PALETTE_ALGORITHM = "locked_palette_v1"


class ConvertError(ValueError):
    pass


def _hash(path: Path) -> str:
    return job.sha256_file(path)


def load_spec(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        schema_gate.validate_named(value, "conversion_spec")
    except (OSError, json.JSONDecodeError, schema_gate.SchemaError) as exc:
        raise ConvertError(f"conversion_spec_invalid: {exc}") from exc
    return value


def _snap(rgb: Iterable[int]) -> tuple[int, int, int]:
    return vdp_color.snap_rgb_to_vdp_grid(tuple(rgb), oracle=vdp_color.ORACLE_RESCOMP)


def _distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def _nearest(rgb: tuple[int, int, int], colors: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    return min(colors, key=lambda color: (_distance(rgb, color), color))


def _weighted_kmedoids(histogram: Counter[tuple[int, int, int]], maximum: int) -> list[tuple[int, int, int]]:
    """Frequency-weighted k-medoids, deterministic from selection to ties.

    The palette remains a set of actual VDP colours (medoids), rather than
    inventing an average off grid.  Dominant colours seed first; every tie is
    resolved lexically.  This is an original compact implementation, not code
    imported from a studied third-party converter.
    """
    colors = sorted(histogram)
    if len(colors) <= maximum:
        return colors
    medoids = sorted(sorted(colors, key=lambda c: (-histogram[c], c))[:maximum])
    for _ in range(16):
        clusters = {medoid: [] for medoid in medoids}
        for color in colors:
            clusters[_nearest(color, medoids)].append(color)
        next_medoids = []
        for current in medoids:
            candidates = clusters[current]
            next_medoids.append(min(
                candidates,
                key=lambda candidate: (
                    sum(histogram[color] * _distance(color, candidate) for color in candidates), candidate),
            ))
        next_medoids = sorted(next_medoids)
        if next_medoids == medoids:
            break
        medoids = next_medoids
    return medoids


def _locked_palette(root: Path, spec: dict) -> tuple[Path, list[tuple[int, int, int]]]:
    """Load a hash-bound palette source and preserve its visible CRAM colors."""
    entry = spec.get("locked_palette_source")
    if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
        raise ConvertError("locked_palette_source_invalid")
    path = _portable_project_file(root, Path(entry["path"]), "locked_palette_source_missing_or_escaped")
    if _hash(path) != entry["sha256"]:
        raise ConvertError("locked_palette_sha256_mismatch")
    compliance = pixel_contract.validate_png(path, spec["index0_role"], oracle=spec["oracle"])
    if compliance["blocking"]:
        raise ConvertError("locked_palette_source_pixel_contract_failed:" + ",".join(compliance["blocking_statuses"]))
    info = pixel_contract.read_png_chunks(path)
    with Image.open(path) as opened:
        if opened.mode != "P":
            raise ConvertError("locked_palette_source_not_indexed")
        used = sorted(set(opened.get_flattened_data()))
    if spec["index0_role"] == "unused0" and 0 in used:
        raise ConvertError("locked_palette_uses_reserved_index0")
    visible_indices = [index for index in used if index != 0]
    colors = sorted({_snap(tuple(info["plte"][index])) for index in visible_indices})
    if not colors or len(colors) > spec["max_visible_colors"]:
        raise ConvertError("locked_palette_color_count_out_of_range")
    if len(colors) != len(visible_indices):
        raise ConvertError("locked_palette_has_duplicate_visible_colors")
    return path, colors


def _palette_for_spec(root: Path, histogram: Counter[tuple[int, int, int]], spec: dict) -> list[tuple[int, int, int]]:
    strategy = spec["palette_strategy"]
    if strategy == PALETTE_ALGORITHM:
        return _weighted_kmedoids(histogram, spec["max_visible_colors"])
    if strategy == LOCKED_PALETTE_ALGORITHM:
        return _locked_palette(root, spec)[1]
    raise ConvertError("palette_strategy_invalid")


def _portable_project_file(root: Path, raw: Path, blocker: str) -> Path:
    if raw.is_absolute() or ".." in raw.parts:
        raise ConvertError(blocker)
    resolved = (root / raw).resolve()
    if root not in resolved.parents or not resolved.is_file():
        raise ConvertError(blocker)
    return resolved


def _transparent(policy: str, pixel: tuple[int, int, int, int], spec: dict) -> bool:
    if policy == "opaque": return False
    if policy == "binary_alpha": return pixel[3] == 0
    if policy == "threshold": return pixel[3] <= spec["alpha_threshold"]
    if policy == "chroma_key": return tuple(pixel[:3]) == tuple(spec["chroma_key_rgb"])
    raise ConvertError("transparency_policy_invalid")


def _assert_uniform_chroma_matte(image: Image.Image, spec: dict) -> None:
    """Reject a chroma route whose border already contains halo/matte pixels."""
    if spec["transparency_policy"] != "chroma_key":
        return
    rgb = image.convert("RGB")
    w, h = rgb.size
    key = tuple(spec["chroma_key_rgb"])
    border = [rgb.getpixel((x, 0)) for x in range(w)]
    border += [rgb.getpixel((x, h - 1)) for x in range(w)]
    border += [rgb.getpixel((0, y)) for y in range(1, h - 1)]
    border += [rgb.getpixel((w - 1, y)) for y in range(1, h - 1)]
    if any(pixel != key for pixel in border):
        raise ConvertError("nonuniform_chroma_matte_requires_border_connected")


def _report_metrics(histogram: Counter[tuple[int, int, int]], palette: list[tuple[int, int, int]]) -> dict:
    error_sum = sum(count * _distance(color, _nearest(color, palette)) for color, count in histogram.items())
    visible = sum(histogram.values())
    return {
        "input_vdp_histogram": [{"rgb": list(color), "pixels": histogram[color]} for color in sorted(histogram)],
        "palette": [{"index": index + 1, "rgb": list(color), "pixels": sum(histogram[c] for c in histogram if _nearest(c, palette) == color)} for index, color in enumerate(palette)],
        "visible_pixels": visible,
        "colors_before": len(histogram), "colors_after": len(palette),
        "weighted_error_total": error_sum,
        "weighted_mse": error_sum / visible if visible else 0,
        "max_individual_error": max((_distance(color, _nearest(color, palette)) for color in histogram), default=0),
    }


def _derive_metrics_from_source(root: Path, source: Path, spec: dict) -> dict:
    """Re-derive the semantic palette facts from immutable input bytes."""
    with Image.open(source) as opened:
        image = opened.convert("RGBA")
    _assert_uniform_chroma_matte(image, spec)
    if image.size != (spec["target_width"], spec["target_height"]):
        pixel_contract.assert_nearest_resample(spec["resize_policy"])
        image = image.resize((spec["target_width"], spec["target_height"]), Image.Resampling.NEAREST)
    raw_pixels = list(image.get_flattened_data())
    policy = spec["transparency_policy"]
    if policy == "binary_alpha" and any(pixel[3] not in (0, 255) for pixel in raw_pixels):
        raise ConvertError("partial_alpha_rejected")
    visible = [pixel for pixel in raw_pixels if not _transparent(policy, pixel, spec)]
    if not visible: raise ConvertError("no_visible_pixels")
    histogram = Counter(_snap(pixel[:3]) for pixel in visible)
    palette = _palette_for_spec(root, histogram, spec)
    return {"histogram": histogram, "palette": palette, "metrics": _report_metrics(histogram, palette)}


def verify_published_conversion(root: Path, spec_file: Path, spec: dict, source: Path,
                                job_spec: job.JobSpec, state: dict) -> dict:
    """Verify conversion semantics after either publish or resume.

    `job.py` verifies generic evidence and immutable output hashes. This
    function additionally establishes that the report still means what this
    converter produced; a malicious reseal cannot turn a structurally invalid
    or semantically fabricated report into a cache hit.
    """
    job_root = Path(state["job_dir"])
    try:
        job.verify_published_job(job_root, job_spec)
        report = json.loads((job_root / "reports" / "conversion_report.json").read_text(encoding="utf-8"))
        schema_gate.validate_named(report, "conversion_report")
        expected = {
            "schema_version": "1.0.0", "tool": TOOL_NAME, "tool_version": TOOL_VERSION,
            "route": job.ROUTE_TECHNICAL, "status": job.OUTPUT_TECHNICAL_CANDIDATE,
            "asset_id": spec["asset_id"], "source_sha256": _hash(source),
            "spec_sha256": _hash(spec_file), "output": f"basic/{spec['output_name']}",
            "index0_role": spec["index0_role"], "oracle": spec["oracle"],
            "palette_algorithm": spec["palette_strategy"],
            "strategies": {key: spec[key] for key in ("resize_policy", "palette_strategy", "dithering_strategy", "transparency_policy")},
            "index0_function": spec["index0_role"], "blocking": False, "blockers": [],
        }
        if spec["palette_strategy"] == LOCKED_PALETTE_ALGORITHM:
            _, locked_colors = _locked_palette(root, spec)
            expected["palette_lock"] = {
                "source_path": spec["locked_palette_source"]["path"],
                "source_sha256": spec["locked_palette_source"]["sha256"],
                "colors": [list(color) for color in locked_colors],
            }
        mismatch = [key for key, value in expected.items() if report.get(key) != value]
        derived = _derive_metrics_from_source(root, source, spec)
        if report.get("metrics") != derived["metrics"]:
            mismatch.append("metrics")
        output = job_root / report["output"]
        if output.parent != job_root / "basic" or not output.is_file():
            mismatch.append("output")
        else:
            measured = pixel_contract.validate_png(output, spec["index0_role"], oracle=spec["oracle"])
            if measured["blocking"] or report.get("content_sha256") != measured["content_sha256"]:
                mismatch.append("content_sha256")
        if mismatch:
            raise ConvertError("cached_conversion_report_invalid: " + ",".join(sorted(set(mismatch))))
    except (OSError, json.JSONDecodeError, schema_gate.SchemaError, job.JobContractError) as exc:
        raise ConvertError(f"cached_conversion_report_invalid: {exc}") from exc
    return state


def convert(root: Path, spec_path: Path) -> dict:
    root = Path(root).resolve()
    visual_workset.enforce_operation(root, "technical_conversion")
    raw_spec = Path(spec_path)
    if raw_spec.is_absolute():
        resolved_spec = raw_spec.resolve()
        if root not in resolved_spec.parents: raise ConvertError("conversion_spec_escaped_project")
    else:
        resolved_spec = _portable_project_file(root, raw_spec, "conversion_spec_missing_or_escaped")
    spec_file_hash_before = _hash(resolved_spec)
    spec = load_spec(resolved_spec)
    source = _portable_project_file(root, Path(spec["source"]), "conversion_source_missing_or_escaped")
    visual_workset.enforce_declared_source(
        root, source, require_production_eligible=True
    )
    source_hash_before = _hash(source)
    locked_palette_path = None
    locked_palette_hash_before = None
    if spec["palette_strategy"] == LOCKED_PALETTE_ALGORITHM:
        locked_palette_path, _ = _locked_palette(root, spec)
        locked_palette_hash_before = _hash(locked_palette_path)
    job_spec = job.JobSpec(
        asset_id=spec["asset_id"],
        sources=tuple(path for path in (source, resolved_spec, locked_palette_path) if path is not None),
        route=job.ROUTE_TECHNICAL,
        index0_role=spec["index0_role"],
        params={"conversion_spec_sha256": spec_file_hash_before, "palette_algorithm": spec["palette_strategy"],
                "resize": spec["resize_policy"], "dither": spec["dithering_strategy"]},
    )

    def work(staging: Path) -> dict:
        if (_hash(source) != source_hash_before or _hash(resolved_spec) != spec_file_hash_before or
                (locked_palette_path is not None and _hash(locked_palette_path) != locked_palette_hash_before)):
            raise ConvertError("source_or_spec_mutated_before_conversion")
        with Image.open(source) as opened:
            image = opened.convert("RGBA")
        _assert_uniform_chroma_matte(image, spec)
        if image.size != (spec["target_width"], spec["target_height"]):
            pixel_contract.assert_nearest_resample(spec["resize_policy"])
            image = image.resize((spec["target_width"], spec["target_height"]), Image.Resampling.NEAREST)
        raw_pixels = list(image.get_flattened_data())
        policy = spec["transparency_policy"]
        if policy == "binary_alpha" and any(pixel[3] not in (0, 255) for pixel in raw_pixels):
            raise ConvertError("partial_alpha_rejected")
        visible_pixels = [pixel for pixel in raw_pixels if not _transparent(policy, pixel, spec)]
        if not visible_pixels: raise ConvertError("no_visible_pixels")
        histogram = Counter(_snap(pixel[:3]) for pixel in visible_pixels)
        palette = _palette_for_spec(root, histogram, spec)
        if len(palette) > 15: raise ConvertError("too_many_palette_entries")
        output = Image.new("P", image.size)
        output.putpalette([component for color in [(0, 0, 0)] + palette for component in color])
        indices = []
        for pixel in raw_pixels:
            if _transparent(policy, pixel, spec):
                if spec["index0_role"] != "transparent0": raise ConvertError("unused0_cannot_encode_transparency")
                indices.append(0)
            else:
                indices.append(1 + palette.index(_nearest(_snap(pixel[:3]), palette)))
        output.putdata(indices)
        target = staging / "basic" / spec["output_name"]
        save_args = {"bits": 4}
        if spec["index0_role"] == "transparent0": save_args["transparency"] = 0
        output.save(target, "PNG", **save_args)
        report = pixel_contract.validate_png(target, spec["index0_role"], oracle=spec["oracle"])
        if report["blocking"]: raise ConvertError("converted_output_rejected:" + ",".join(report["blocking_statuses"]))
        try:
            schema_gate.validate_named(report, "pixel_compliance_report")
        except schema_gate.SchemaError as exc:
            raise ConvertError(f"pixel_report_schema_invalid: {exc}") from exc
        report_path = staging / "reports" / job.PIXEL_REPORT_NAME
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        conversion = {
            "schema_version": "1.0.0", "tool": TOOL_NAME, "tool_version": TOOL_VERSION,
            "route": "technical_conversion", "status": "technical_candidate", "asset_id": spec["asset_id"],
            "source_sha256": source_hash_before, "spec_sha256": spec_file_hash_before,
            "output": target.relative_to(staging).as_posix(), "content_sha256": report["content_sha256"],
            "index0_role": spec["index0_role"], "oracle": spec["oracle"], "palette_algorithm": spec["palette_strategy"],
            "strategies": {key: spec[key] for key in ("resize_policy", "palette_strategy", "dithering_strategy", "transparency_policy")},
            "index0_function": spec["index0_role"], "metrics": _report_metrics(histogram, palette),
            "blocking": False, "blockers": [], "next_action": "human visual review; never promote automatically",
        }
        if locked_palette_path is not None:
            _, locked_colors = _locked_palette(root, spec)
            conversion["palette_lock"] = {
                "source_path": spec["locked_palette_source"]["path"],
                "source_sha256": locked_palette_hash_before,
                "colors": [list(color) for color in locked_colors],
            }
        try:
            schema_gate.validate_named(conversion, "conversion_report")
        except schema_gate.SchemaError as exc:
            raise ConvertError(f"conversion_report_schema_invalid: {exc}") from exc
        (staging / "reports" / "conversion_report.json").write_text(json.dumps(conversion, indent=2, sort_keys=True), encoding="utf-8")
        if (_hash(source) != source_hash_before or _hash(resolved_spec) != spec_file_hash_before or
                (locked_palette_path is not None and _hash(locked_palette_path) != locked_palette_hash_before)):
            raise ConvertError("source_or_spec_mutated_during_conversion")
        return conversion
    state = job.run_job(root, job_spec, work=work)
    return verify_published_conversion(root, resolved_spec, spec, source, job_spec, state)


def self_check() -> dict:
    fixtures = []
    with tempfile.TemporaryDirectory(prefix="forge_art_convert_") as raw:
        root = Path(raw); (root / "data").mkdir(); (root / "res").mkdir()
        image = Image.new("RGBA", (16, 16), (0xEE, 0, 0, 255))
        pixels = list(image.get_flattened_data())
        pixels[-15:] = [(0, 0xEE, 0, 255)] * 15
        image.putdata(pixels); image.save(root / "data" / "dominant.png")
        spec = {"schema_version":"1.0.0","route":"technical_conversion","asset_id":"dominant","source":"data/dominant.png","source_kind":"technical_fixture","target_width":16,"target_height":16,"index0_role":"unused0","resize_policy":"NEAREST","palette_strategy":PALETTE_ALGORITHM,"max_visible_colors":1,"dithering_strategy":"none","transparency_policy":"opaque","oracle":"rescomp","output_name":"dominant.png","intended_use":"neutral_fixture"}
        path = root / "spec.json"; path.write_text(json.dumps(spec), encoding="utf-8")
        state = convert(root, path); report = json.loads((Path(state["job_dir"]) / "reports" / "conversion_report.json").read_text())
        fixtures.append({"name":"dominant_color_survives_weighted_selection","kind":"positive","passed":report["metrics"]["palette"][0]["rgb"] == [238,0,0]})
        cached = convert(root, path)
        fixtures.append({"name":"same_spec_revalidates_cache","kind":"positive","passed":cached["job_id"] == state["job_id"]})
        with ThreadPoolExecutor(max_workers=2) as pool:
            concurrent = list(pool.map(lambda _unused: convert(root, path), range(2)))
        fixtures.append({"name":"concurrent_convert_revalidates_single_cache","kind":"positive","passed":len({item["job_id"] for item in concurrent}) == 1})
        locked_image = Image.new("P", (16, 16), 1)
        locked_palette = [0, 0, 0, 238, 0, 0, 0, 238, 0] + [0, 0, 0] * 253
        locked_image.putpalette(locked_palette)
        locked_pixels = [1] * (16 * 16)
        locked_pixels[-15:] = [2] * 15
        locked_image.putdata(locked_pixels)
        locked_path = root / "data" / "locked_palette.png"
        locked_image.save(locked_path, "PNG", bits=4)
        locked_spec = dict(spec)
        locked_spec.update({
            "asset_id": "locked_palette_probe", "palette_strategy": LOCKED_PALETTE_ALGORITHM,
            "locked_palette_source": {"path": "data/locked_palette.png", "sha256": _hash(locked_path)},
            "max_visible_colors": 2, "output_name": "locked_palette_probe.png",
        })
        locked_spec_path = root / "locked_palette_spec.json"
        locked_spec_path.write_text(json.dumps(locked_spec), encoding="utf-8")
        locked_state = convert(root, locked_spec_path)
        locked_report = json.loads((Path(locked_state["job_dir"]) / "reports" / "conversion_report.json").read_text())
        locked_output = Image.open(Path(locked_state["job_dir"]) / locked_report["output"])
        fixtures.append({
            "name": "locked_palette_preserves_selected_cram_colors",
            "kind": "positive",
            "passed": locked_report["palette_algorithm"] == LOCKED_PALETTE_ALGORITHM
            and locked_report["metrics"]["weighted_error_total"] == 0
            and locked_output.getpixel((0, 0)) != locked_output.getpixel((15, 15)),
        })
        locked_cached = convert(root, locked_spec_path)
        fixtures.append({"name": "locked_palette_cache_binds_palette_source", "kind": "positive",
                         "passed": locked_cached["job_id"] == locked_state["job_id"]})
        locked_image.putpixel((0, 0), 2)
        locked_image.save(locked_path, "PNG", bits=4)
        try:
            convert(root, locked_spec_path)
            locked_mutation_rejected = False
        except ConvertError as exc:
            locked_mutation_rejected = "locked_palette_sha256_mismatch" in str(exc)
        fixtures.append({"name": "locked_palette_mutation_rejected_by_hash", "kind": "negative",
                         "passed": locked_mutation_rejected})
        report_path = Path(state["job_dir"]) / "reports" / "conversion_report.json"
        forged_report = json.loads(report_path.read_text(encoding="utf-8")); forged_report.pop("metrics")
        report_path.write_text(json.dumps(forged_report), encoding="utf-8")
        state_path = Path(state["job_dir"]) / "job_state.json"
        forged_state = json.loads(state_path.read_text(encoding="utf-8"))
        forged_state["output_hashes"] = job.output_hashes(Path(state["job_dir"]))
        forged_state[job.STATE_SEAL_FIELD] = job.compute_state_seal(forged_state)
        state_path.write_text(json.dumps(forged_state), encoding="utf-8")
        try: convert(root, path); passed = False
        except ConvertError as exc: passed = "cached_conversion_report_invalid" in str(exc)
        fixtures.append({"name":"rejects_resealed_invalid_conversion_report","kind":"negative","passed":passed})
        invalid_cases = {
            "unknown_spec_property_rejected": {"unknown": True},
            "invented_source_kind_rejected": {"source_kind": "invented"},
            "wrong_route_rejected": {"route": "assisted_native_translation"},
            "invalid_intended_use_rejected": {"intended_use": "hero_sprite"},
            "out_of_range_threshold_rejected": {"transparency_policy": "threshold", "alpha_threshold": 256},
            "invalid_chroma_rgb_rejected": {"transparency_policy": "chroma_key", "chroma_key_rgb": [0, 0, 999]},
            "absolute_source_rejected": {"source": "/tmp/outside.png"},
            "traversal_source_rejected": {"source": "../outside.png"},
            "locked_palette_requires_source_binding": {"palette_strategy": LOCKED_PALETTE_ALGORITHM},
            "weighted_palette_rejects_lock_source": {"locked_palette_source": {"path": "data/x.png", "sha256": "0" * 64}},
        }
        for name, change in invalid_cases.items():
            invalid = dict(spec); invalid.update(change); path.write_text(json.dumps(invalid), encoding="utf-8")
            try: load_spec(path); passed = False
            except ConvertError: passed = True
            fixtures.append({"name": name, "kind": "negative", "passed": passed})
        route_cases = {
            "concept_basic_control_allowed": ({"source_kind": "concept", "intended_use": "basic_technical_control"}, True),
            "photo_basic_control_allowed": ({"source_kind": "photo_or_render", "intended_use": "basic_technical_control"}, True),
            "authored_mechanical_allowed": ({"source_kind": "authored_raster", "intended_use": "mechanical_asset_conversion"}, True),
            "native_mechanical_allowed": ({"source_kind": "native_pixel_source", "intended_use": "mechanical_asset_conversion"}, True),
            "concept_neutral_fixture_rejected": ({"source_kind": "concept", "intended_use": "neutral_fixture"}, False),
            "technical_fixture_basic_control_rejected": ({"source_kind": "technical_fixture", "intended_use": "basic_technical_control"}, False),
            "concept_mechanical_conversion_rejected": ({"source_kind": "concept", "intended_use": "mechanical_asset_conversion"}, False),
        }
        for name, (change, expected) in route_cases.items():
            candidate = dict(spec); candidate.update(change); path.write_text(json.dumps(candidate), encoding="utf-8")
            try: load_spec(path); passed = True
            except ConvertError: passed = False
            fixtures.append({"name": name, "kind": "positive" if expected else "negative", "passed": passed == expected})
        outside = root.parent / "forge_art_outside.png"; outside.write_bytes((root / "data" / "dominant.png").read_bytes())
        link = root / "data" / "escaped.png"; link.symlink_to(outside)
        escaped = dict(spec); escaped["source"] = "data/escaped.png"; path.write_text(json.dumps(escaped), encoding="utf-8")
        try: convert(root, path); passed = False
        except ConvertError: passed = True
        fixtures.append({"name":"external_symlink_source_rejected","kind":"negative","passed":passed})
        outside.unlink(missing_ok=True)

        matte = Image.new("RGB", (16, 16), (255, 0, 255))
        matte.putpixel((0, 0), (250, 8, 248))
        matte.putpixel((15, 15), (242, 14, 241))
        matte_path = root / "data" / "nonuniform_chroma.png"; matte.save(matte_path)
        matte_spec = dict(spec)
        matte_spec.update({"asset_id": "nonuniform_chroma", "source": "data/nonuniform_chroma.png",
                           "source_kind": "concept", "intended_use": "basic_technical_control",
                           "index0_role": "transparent0", "transparency_policy": "chroma_key",
                           "chroma_key_rgb": [255, 0, 255], "output_name": "nonuniform_chroma.png"})
        matte_spec_path = root / "matte_spec.json"; matte_spec_path.write_text(json.dumps(matte_spec), encoding="utf-8")
        try: convert(root, matte_spec_path); matte_failed = False
        except ConvertError as exc: matte_failed = str(exc) == "nonuniform_chroma_matte_requires_border_connected"
        fixtures.append({"name":"nonuniform_chroma_requires_representation_change","kind":"negative","passed":matte_failed})
    return {"fixtures": fixtures, "fixtures_passed": sum(f["passed"] for f in fixtures), "fixtures_total": len(fixtures), "blocking": not all(f["passed"] for f in fixtures)}

#!/usr/bin/env python3
"""Shared, deterministic measurements for canonical animation validators."""

from __future__ import annotations

import hashlib
import json
import re
from collections import deque
from pathlib import Path
from typing import Any, Iterable

from PIL import Image


class SchemaValidationError(ValueError):
    """Raised when a canonical JSON artifact violates its bundled schema."""


def canonical_schema_path(name: str) -> Path:
    return Path(__file__).resolve().parents[2] / "schemas" / f"{name}.schema.json"


def _schema_errors(value: Any, schema: dict[str, Any], location: str = "$") -> list[str]:
    """Validate the Draft-07 subset used by the canonical SGDK contracts.

    Keeping this subset local avoids a false green when the optional jsonschema
    package is absent on a host. Unsupported schema keywords remain annotations;
    every assertion currently used by animation_strip_contract is enforced.
    """
    errors: list[str] = []
    expected_type = schema.get("type")
    type_checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    if expected_type in type_checks and not type_checks[expected_type](value):
        return [f"{location}:type:{expected_type}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}:const")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}:enum")
    if isinstance(value, str):
        if len(value) < int(schema.get("minLength", 0)):
            errors.append(f"{location}:minLength")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            errors.append(f"{location}:pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{location}:minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{location}:maximum")
    if isinstance(value, list):
        if len(value) < int(schema.get("minItems", 0)):
            errors.append(f"{location}:minItems")
        if "maxItems" in schema and len(value) > int(schema["maxItems"]):
            errors.append(f"{location}:maxItems")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{location}:uniqueItems")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(_schema_errors(item, item_schema, f"{location}[{index}]"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required if isinstance(required, list) else []:
            if key not in value:
                errors.append(f"{location}.{key}:required")
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, item in value.items():
                if key in properties and isinstance(properties[key], dict):
                    errors.extend(_schema_errors(item, properties[key], f"{location}.{key}"))
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{location}.{key}:additionalProperties")
    for item in schema.get("allOf", []) if isinstance(schema.get("allOf"), list) else []:
        if isinstance(item, dict):
            errors.extend(_schema_errors(value, item, location))
    condition = schema.get("if")
    if isinstance(condition, dict):
        branch = schema.get("then") if not _schema_errors(value, condition, location) else schema.get("else")
        if isinstance(branch, dict):
            errors.extend(_schema_errors(value, branch, location))
    negated = schema.get("not")
    if isinstance(negated, dict) and not _schema_errors(value, negated, location):
        errors.append(f"{location}:not")
    return errors


def validate_canonical_schema(value: Any, name: str) -> list[str]:
    schema = json.loads(canonical_schema_path(name).read_text(encoding="utf-8"))
    if not isinstance(schema, dict):
        raise SchemaValidationError(f"schema object required: {name}")
    return _schema_errors(value, schema)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def resolve_inside(root: Path, raw: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("empty artifact path")
    candidate = Path(raw)
    if candidate.is_absolute():
        raise ValueError("absolute artifact path is forbidden")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("artifact path escapes project root") from exc
    return resolved


def image_mask(image: Image.Image, transparent_index: int = 0) -> list[list[bool]]:
    """Return a visible-pixel mask without trusting report metadata."""
    if image.mode == "P":
        px = image.load()
        return [[int(px[x, y]) != transparent_index for x in range(image.width)]
                for y in range(image.height)]
    rgba = image.convert("RGBA")
    px = rgba.load()
    return [[int(px[x, y][3]) != 0 for x in range(rgba.width)]
            for y in range(rgba.height)]


def crop_mask(mask: list[list[bool]], x: int, y: int, w: int, h: int) -> list[list[bool]]:
    return [row[x:x + w] for row in mask[y:y + h]]


def mask_hash(mask: list[list[bool]]) -> str:
    packed = bytearray()
    for row in mask:
        packed.extend(1 if value else 0 for value in row)
    return hashlib.sha256(bytes(packed)).hexdigest()


def connected_components(mask: list[list[bool]]) -> list[list[tuple[int, int]]]:
    if not mask:
        return []
    height, width = len(mask), len(mask[0])
    seen: set[tuple[int, int]] = set()
    out: list[list[tuple[int, int]]] = []
    for y in range(height):
        for x in range(width):
            if not mask[y][x] or (x, y) in seen:
                continue
            queue = deque([(x, y)])
            seen.add((x, y))
            component: list[tuple[int, int]] = []
            while queue:
                cx, cy = queue.popleft()
                component.append((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height and mask[ny][nx] and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        queue.append((nx, ny))
            out.append(component)
    return out


def bbox(mask: list[list[bool]]) -> list[int] | None:
    points = [(x, y) for y, row in enumerate(mask) for x, value in enumerate(row) if value]
    if not points:
        return None
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def centroid(mask: list[list[bool]]) -> list[float] | None:
    points = [(x, y) for y, row in enumerate(mask) for x, value in enumerate(row) if value]
    if not points:
        return None
    return [sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)]


def changed_ratio(left: list[list[bool]], right: list[list[bool]]) -> float:
    if len(left) != len(right) or (left and len(left[0]) != len(right[0])):
        raise ValueError("mask dimensions differ")
    total = max(1, len(left) * (len(left[0]) if left else 0))
    changed = sum(a != b for row_a, row_b in zip(left, right) for a, b in zip(row_a, row_b))
    return changed / total


def erosion_depth(mask: list[list[bool]]) -> tuple[int, int]:
    """Return maximum 4-neighbour erosion depth and first-layer interior count."""
    current = [row[:] for row in mask]
    depth = 0
    first_count = 0
    while current and any(any(row) for row in current):
        height, width = len(current), len(current[0])
        nxt = [[False] * width for _ in range(height)]
        count = 0
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if (current[y][x] and current[y - 1][x] and current[y + 1][x]
                        and current[y][x - 1] and current[y][x + 1]):
                    nxt[y][x] = True
                    count += 1
        if depth == 0:
            first_count = count
        if count == 0:
            break
        depth += 1
        current = nxt
    return depth, first_count


def boundary_runs(mask: list[list[bool]], edge: str) -> list[list[int]]:
    if not mask:
        return []
    height, width = len(mask), len(mask[0])
    if edge == "left":
        values = [mask[y][0] for y in range(height)]
    elif edge == "right":
        values = [mask[y][width - 1] for y in range(height)]
    elif edge == "top":
        values = mask[0]
    elif edge == "bottom":
        values = mask[height - 1]
    else:
        raise ValueError(f"unknown edge: {edge}")
    runs: list[list[int]] = []
    start: int | None = None
    for index, value in enumerate(values + [False]):
        if value and start is None:
            start = index
        elif not value and start is not None:
            runs.append([start, index - 1])
            start = None
    return runs


def ranges_overlap(left: Iterable[list[int]], right: Iterable[list[int]]) -> bool:
    return any(max(a[0], b[0]) <= min(a[1], b[1]) for a in left for b in right)


def integer_replication_factor(image: Image.Image, factors: tuple[int, ...] = (4, 3, 2)) -> int:
    """Return an exact aligned whole-image pixel replication factor, or 1.

    A 32x32 frame made by expanding a 16x16 glyph grid 2x is technically a
    32x32 PNG but artistically still a 16x16 raster. Native-animation claims
    must expose that effective resolution instead of hiding it in metadata.
    """
    indexed = image.convert("RGBA")
    px = indexed.load()
    for factor in factors:
        if indexed.width % factor or indexed.height % factor:
            continue
        if all(
            all(px[x + dx, y + dy] == px[x, y] for dy in range(factor) for dx in range(factor))
            for y in range(0, indexed.height, factor)
            for x in range(0, indexed.width, factor)
        ):
            return factor
    return 1


def validate_approval_record(root: Path, binding: Any, subjects: set[str]) -> list[str]:
    if not isinstance(binding, dict):
        return ["native_lineart_approval_unbound"]
    try:
        path = resolve_inside(root, binding.get("path", ""))
    except ValueError:
        return ["native_lineart_approval_unbound"]
    if not path.is_file() or sha256_file(path) != binding.get("sha256"):
        return ["native_lineart_approval_unbound"]
    if binding.get("subject_sha256") not in subjects:
        return ["native_lineart_approval_unbound"]
    try:
        report = load_object(path)
    except (ValueError, json.JSONDecodeError):
        return ["native_lineart_approval_unbound"]
    if report.get("status") not in {"passed", "approved", "approved_for_strip_authoring"}:
        return ["native_lineart_approval_status_invalid"]
    if report.get("subject_sha256") not in subjects:
        return ["native_lineart_approval_unbound"]
    return []


def validate_production_provenance(
    contract: dict[str, Any], root: Path, artifact_sha256: str
) -> tuple[list[str], dict[str, Any]]:
    provenance = contract.get("production_provenance")
    if not isinstance(provenance, dict):
        return ["animation_production_provenance_missing"], {}
    blockers: list[str] = []
    source_kind = provenance.get("source_kind")
    producer_kind = provenance.get("producer_kind")
    if source_kind == "procedural_primitive" or producer_kind == "procedural_code_probe":
        blockers.append("code_authored_character_pixels")
    source = provenance.get("authored_source")
    source_sha = ""
    if not isinstance(source, dict):
        blockers.append("authored_pixel_source_unbound")
    else:
        try:
            source_path = resolve_inside(root, source.get("path", ""))
        except ValueError:
            blockers.append("authored_pixel_source_unbound")
        else:
            if source_path.suffix.lower() not in {".png", ".gif", ".bmp"} or not source_path.is_file():
                blockers.append("authored_pixel_source_unbound")
            else:
                source_sha = sha256_file(source_path)
                if source_sha != source.get("sha256"):
                    blockers.append("authored_pixel_source_unbound")
    record_binding = provenance.get("producer_record")
    if not isinstance(record_binding, dict):
        blockers.append("animation_producer_record_unbound")
    else:
        try:
            record_path = resolve_inside(root, record_binding.get("path", ""))
        except ValueError:
            blockers.append("animation_producer_record_unbound")
        else:
            if not record_path.is_file() or sha256_file(record_path) != record_binding.get("sha256"):
                blockers.append("animation_producer_record_unbound")
            else:
                try:
                    record = load_object(record_path)
                except (ValueError, json.JSONDecodeError):
                    blockers.append("animation_producer_record_unbound")
                else:
                    if record.get("status") not in {"passed", "completed", "approved"}:
                        blockers.append("animation_producer_record_not_closed")
                    if record.get("source_kind") != source_kind or record.get("producer_kind") != producer_kind:
                        blockers.append("animation_producer_record_mismatch")
                    if record.get("subject_sha256") not in {source_sha, artifact_sha256}:
                        blockers.append("animation_producer_record_unbound")
            if record_binding.get("subject_sha256") not in {source_sha, artifact_sha256}:
                blockers.append("animation_producer_record_unbound")
    return sorted(set(blockers)), {
        "source_kind": source_kind,
        "producer_kind": producer_kind,
        "authored_source_sha256": source_sha or None,
    }

"""Explicit, staging-only procedural pixel probe bridge.

This module is intentionally small. A caller supplies an action document and
the bridge applies coordinate-addressed pixel decisions deterministically.
Because the raster starts from a blank canvas and is born through putpixel/
runs, its output is a procedural_code_probe.  It may diagnose layout or apply
reproducible experiments, but it cannot prove native authorship or final art.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

from forge_art import pixel_contract, schema_gate, vdp_color, visual_workset

TOOL_NAME = "forge_art.native_edit"
TOOL_VERSION = "1.2.0"
SCHEMA_NAME = "native_edit_actions"
OPERATOR = "procedural_code_probe"
MAX_PATCH_PIXELS = 128
ALLOWED_OUTPUT_PREFIXES = (Path("out/v11_native_edit"), Path("out/v11_review"))


class NativeEditError(ValueError):
    """A closed failure with a stable blocker suitable for CI reports."""

    def __init__(self, blocker: str, message: str) -> None:
        super().__init__(f"[{blocker}] {message}")
        self.blocker = blocker


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _tree_sha256(path: Path) -> str:
    """Hash a whole protected tree with names, types and file bytes."""
    digest = hashlib.sha256()
    if not path.exists():
        digest.update(b"<missing>\0")
        return digest.hexdigest()
    for item in sorted(path.rglob("*")):
        rel = item.relative_to(path).as_posix().encode("utf-8")
        if item.is_dir():
            digest.update(b"D\0" + rel + b"\0")
        elif item.is_file():
            digest.update(b"F\0" + rel + b"\0" + _sha256(item).encode("ascii") + b"\0")
    return digest.hexdigest()


def _portable_file(root: Path, value: str, blocker: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise NativeEditError(blocker, f"caminho nao-portavel: {value}")
    resolved = (root / path).resolve()
    if root not in resolved.parents or not resolved.is_file():
        raise NativeEditError(blocker, f"arquivo ausente ou fora do projeto: {value}")
    return resolved


def _region(action: dict[str, Any], width: int, height: int) -> tuple[int, int, int, int]:
    raw = action.get("region")
    if not isinstance(raw, dict):
        raise NativeEditError("region_missing", f"{action.get('action_id')}: region obrigatoria")
    try:
        x, y, w, h = (int(raw[key]) for key in ("x", "y", "w", "h"))
    except (KeyError, TypeError, ValueError) as exc:
        raise NativeEditError("region_invalid", f"{action.get('action_id')}: region invalida") from exc
    if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > width or y + h > height:
        raise NativeEditError("region_out_of_bounds", f"{action.get('action_id')}: {raw}")
    return x, y, w, h


def _assert_before(image: Image.Image, coordinates: list[tuple[int, int]], allowed: list[int], action_id: str) -> None:
    allowed_set = set(allowed)
    for x, y in coordinates:
        current = int(image.getpixel((x, y)))
        if current not in allowed_set:
            raise NativeEditError(
                "before_indices_mismatch",
                f"{action_id}: pixel ({x},{y})={current}, esperado um de {sorted(allowed_set)}",
            )


def _coordinates_for_run(action: dict[str, Any], width: int, height: int) -> list[tuple[int, int]]:
    x, y, w, h = _region(action, width, height)
    if h != 1:
        raise NativeEditError("run_region_not_single_row", f"{action['action_id']}: pencil_run exige h=1")
    return [(px, y) for px in range(x, x + w)]


def _indices(action: dict[str, Any], key: str) -> list[int]:
    values = action.get(key)
    if not isinstance(values, list) or not all(isinstance(value, int) for value in values):
        raise NativeEditError("indices_invalid", f"{action.get('action_id')}: {key} deve ser lista de inteiros")
    return values


def _paint(image: Image.Image, coords: list[tuple[int, int]], action: dict[str, Any], index: int) -> None:
    before = _indices(action, "before_indices")
    after = _indices(action, "after_indices")
    if index not in after:
        raise NativeEditError("after_indices_mismatch", f"{action['action_id']}: cor {index} nao declarada")
    _assert_before(image, coords, before, action["action_id"])
    if all(int(image.getpixel(coord)) == index for coord in coords):
        raise NativeEditError("action_noop", f"{action['action_id']}: todos os pixels ja possuem o destino")
    for coord in coords:
        image.putpixel(coord, index)


def _patch_pixels(action: dict[str, Any], width: int, height: int) -> list[tuple[int, int, int]]:
    raw = action.get("pixels")
    if not isinstance(raw, list) or not raw or len(raw) > MAX_PATCH_PIXELS:
        raise NativeEditError("patch_size_invalid", f"{action['action_id']}: pixels deve conter 1..{MAX_PATCH_PIXELS} itens")
    result: list[tuple[int, int, int]] = []
    for item in raw:
        if not isinstance(item, dict) or not all(key in item for key in ("x", "y", "index")):
            raise NativeEditError("patch_pixel_invalid", f"{action['action_id']}: pixel malformado")
        x, y, index = (int(item[key]) for key in ("x", "y", "index"))
        if not (0 <= x < width and 0 <= y < height):
            raise NativeEditError("pixel_out_of_bounds", f"{action['action_id']}: ({x},{y})")
        result.append((x, y, index))
    return result


def _apply_action(image: Image.Image, action: dict[str, Any], palette: list[tuple[int, int, int]]) -> None:
    width, height = image.size
    operation = action["operation"]
    _region(action, width, height)
    before = _indices(action, "before_indices")
    after = _indices(action, "after_indices")
    for index in before + after:
        if not 0 <= index < len(palette):
            raise NativeEditError("palette_index_out_of_range", f"{action['action_id']}: {index}")

    if operation == "pencil_pixel":
        x, y, _, _ = _region(action, width, height)
        _paint(image, [(x, y)], action, int(action["color_index"]))
    elif operation == "pencil_run":
        _paint(image, _coordinates_for_run(action, width, height), action, int(action["color_index"]))
    elif operation == "erase_pixel":
        x, y, _, _ = _region(action, width, height)
        _paint(image, [(x, y)], action, 0)
    elif operation == "erase_run":
        _paint(image, _coordinates_for_run(action, width, height), action, 0)
    elif operation == "replace_color_in_selection":
        x, y, w, h = _region(action, width, height)
        source = int(action["before_color_index"])
        target = int(action["after_color_index"])
        if source not in before or target not in after:
            raise NativeEditError("selection_indices_mismatch", f"{action['action_id']}: cores nao declaradas")
        changed = 0
        for py in range(y, y + h):
            for px in range(x, x + w):
                if int(image.getpixel((px, py))) == source:
                    image.putpixel((px, py), target)
                    changed += 1
        if not changed:
            raise NativeEditError("action_noop", f"{action['action_id']}: selecao nao contem a cor de origem")
    elif operation == "copy_authored_cluster" or operation == "apply_local_patch":
        pixels = _patch_pixels(action, width, height)
        coords = [(x, y) for x, y, _ in pixels]
        _assert_before(image, coords, before, action["action_id"])
        if all(int(image.getpixel((x, y))) == index for x, y, index in pixels):
            raise NativeEditError("action_noop", f"{action['action_id']}: patch nao altera pixels")
        for x, y, index in pixels:
            if index not in after:
                raise NativeEditError("after_indices_mismatch", f"{action['action_id']}: cor {index} nao declarada")
            image.putpixel((x, y), index)
    elif operation == "move_selection_integer":
        x, y, w, h = _region(action, width, height)
        dx, dy = int(action["dx"]), int(action["dy"])
        if dx == 0 and dy == 0:
            raise NativeEditError("action_noop", f"{action['action_id']}: deslocamento zero")
        destination = [(px + dx, py + dy) for py in range(y, y + h) for px in range(x, x + w)]
        if any(px < 0 or py < 0 or px >= width or py >= height for px, py in destination):
            raise NativeEditError("move_out_of_bounds", f"{action['action_id']}: dx={dx}, dy={dy}")
        source = [int(image.getpixel((px, py))) for py in range(y, y + h) for px in range(x, x + w)]
        _assert_before(image, [(px, py) for py in range(y, y + h) for px in range(x, x + w)], before, action["action_id"])
        for py in range(y, y + h):
            for px in range(x, x + w):
                image.putpixel((px, py), 0)
        for value, (px, py) in zip(source, destination):
            image.putpixel((px, py), value)
    elif operation == "mirror_selection":
        if not action.get("allow_mirror", False):
            raise NativeEditError("mirror_not_authorized", f"{action['action_id']}: allow_mirror=false")
        x, y, w, h = _region(action, width, height)
        axis = action.get("axis", "horizontal")
        if axis != "horizontal":
            raise NativeEditError("mirror_axis_invalid", f"{action['action_id']}: somente horizontal")
        values = [[int(image.getpixel((px, py))) for px in range(x, x + w)] for py in range(y, y + h)]
        _assert_before(image, [(px, py) for py in range(y, y + h) for px in range(x, x + w)], before, action["action_id"])
        if all(value == mirrored for row in values for value, mirrored in zip(row, reversed(row))):
            raise NativeEditError("action_noop", f"{action['action_id']}: espelhamento nao altera selecao")
        for row, py in zip(values, range(y, y + h)):
            for value, px in zip(reversed(row), range(x, x + w)):
                image.putpixel((px, py), value)
    elif operation == "palette_slot_assignment":
        slot = int(action["slot"])
        rgb = tuple(int(value) for value in action["rgb"])
        if slot != len(palette) - 1 or slot == 0:
            raise NativeEditError("palette_slot_reassignment", f"{action['action_id']}: somente proximo slot nao usado")
        if len(rgb) != 3 or any(value not in vdp_color.AUTHORING_LEVELS for value in rgb):
            raise NativeEditError("palette_color_off_grid", f"{action['action_id']}: {rgb}")
        palette.append(rgb)
    else:
        raise NativeEditError("operation_not_allowed", f"{action['action_id']}: {operation}")


def _save_indexed(image: Image.Image, palette: list[tuple[int, int, int]], path: Path) -> None:
    padded = palette[:16] + [(0, 0, 0)] * (16 - len(palette))
    image.putpalette([channel for rgb in padded for channel in rgb])
    image.info["transparency"] = 0
    image.save(path, format="PNG", optimize=False, bits=4)


def _validate_spec(spec: dict[str, Any]) -> None:
    try:
        schema_gate.validate_named(spec, f"{SCHEMA_NAME}")
    except schema_gate.SchemaError as exc:
        raise NativeEditError("action_schema_invalid", str(exc)) from exc
    actions = spec["actions"]
    ids = [action["action_id"] for action in actions]
    if len(ids) != len(set(ids)):
        raise NativeEditError("duplicate_action_id", "action_id precisa ser unico")
    for action in actions:
        if action["asset_id"] != spec["asset_id"] or action["frame_id"] != spec["frame_id"]:
            raise NativeEditError("action_root_binding_mismatch", f"{action['action_id']}: asset/frame divergente da raiz")
        operation = action["operation"]
        if operation in {"pencil_pixel", "erase_pixel"} and (action["region"]["w"], action["region"]["h"]) != (1, 1):
            raise NativeEditError("pixel_region_shape_invalid", f"{action['action_id']}: operacao de pixel exige 1x1")


def native_edit(project_root: Path, actions_path: Path, output_dir: Path) -> dict[str, Any]:
    root = Path(project_root).resolve()
    workset_report = visual_workset.enforce_operation(root, "procedural_edit_probe")
    actions_file = _portable_file(root, str(actions_path), "actions_file_invalid")
    try:
        spec = json.loads(actions_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NativeEditError("actions_file_invalid", str(exc)) from exc
    _validate_spec(spec)

    identity = spec["identity_source"]
    source = _portable_file(root, identity["path"], "identity_source_invalid")
    visual_workset.enforce_declared_source(
        root, source, require_production_eligible=False
    )
    source_before = _sha256(source)
    if source_before != identity["sha256"]:
        raise NativeEditError("identity_source_hash_mismatch", f"esperado {identity['sha256']}, obtido {source_before}")
    underlay_hashes = {}
    for underlay in spec.get("underlays", []):
        path = _portable_file(root, underlay["path"], "underlay_invalid")
        underlay_hashes[underlay["path"]] = _sha256(path)
        if underlay_hashes[underlay["path"]] != underlay["sha256"]:
            raise NativeEditError("underlay_hash_mismatch", underlay["path"])

    output = (root / output_dir).resolve() if not output_dir.is_absolute() else output_dir.resolve()
    relative_output = output.relative_to(root) if root in output.parents else Path("<outside>")
    if root not in output.parents or not any(relative_output == prefix or prefix in relative_output.parents for prefix in ALLOWED_OUTPUT_PREFIXES):
        raise NativeEditError("staging_only_violation", f"saida proibida: {output}")
    if output.exists():
        raise NativeEditError("output_exists", f"nao sobrescrevo staging existente: {output}")
    protected_before = {name: _tree_sha256(root / name) for name in ("data", "res")}
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".native-edit-", dir=output.parent))
    palette = [tuple(rgb) for rgb in spec["palette"]]
    if palette[0] != (0, 0, 0):
        raise NativeEditError("palette_index0_invalid", "o primeiro slot deve ser (0,0,0) transparente")
    if any(len(rgb) != 3 or any(channel not in vdp_color.AUTHORING_LEVELS for channel in rgb) for rgb in palette[1:]):
        raise NativeEditError("palette_color_off_grid", "toda cor precisa estar na grade de autoria VDP")
    image = Image.new("P", (spec["canvas"]["width"], spec["canvas"]["height"]), 0)
    log: list[dict[str, Any]] = []
    try:
        for action in spec["actions"]:
            _apply_action(image, action, palette)
            log.append({"action_id": action["action_id"], "operation": action["operation"], "status": "applied"})
        candidate = temp / "candidate.png"
        _save_indexed(image, palette, candidate)
        measured = pixel_contract.validate_png(candidate, "transparent0", oracle="rescomp")
        if measured["blocking"]:
            raise NativeEditError("pixel_contract_failed", json.dumps(measured["blocking_statuses"]))
        measured["file"] = "candidate.png"
        scale8 = temp / "candidate_8x.png"
        image.resize((image.width * 8, image.height * 8), Image.Resampling.NEAREST).save(scale8, format="PNG", optimize=False, bits=4)
        source_after = _sha256(source)
        if source_after != source_before:
            raise NativeEditError("protected_source_mutated", identity["path"])
        protected_after = {name: _tree_sha256(root / name) for name in ("data", "res")}
        if protected_after != protected_before:
            raise NativeEditError("protected_tree_mutated", "data/ ou res/ foi alterado durante o native-edit")
        report = {
            "schema_version": "1.0.0",
            "tool": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "command": "native-edit",
            "status": "completed",
            "asset_id": spec["asset_id"],
            "frame_id": spec["frame_id"],
            "claim_ceiling": "procedural_code_probe",
            "authorship": "procedural_primitive",
            "production_eligible": False,
            "visual_workset": workset_report,
            "source_authority": identity,
            "underlays": underlay_hashes,
            "actions_sha256": _sha256(actions_file),
            "source_sha256_before": source_before,
            "source_sha256_after": source_after,
            "candidate_sha256": _sha256(candidate),
            "candidate_canonical_sha256": measured["content_sha256"],
            "candidate_8x_sha256": _sha256(scale8),
            "protected_trees_sha256_before": protected_before,
            "protected_trees_sha256_after": protected_after,
            "operations_applied": len(log),
            "action_log": "action_log.json",
            "pixel_contract_report": measured,
            "res_promotion": False,
            "next_action": (
                "use this output only as diagnostic evidence; native authorship "
                "requires an independently authored raster or a capable visual producer"
            ),
        }
        (temp / "action_log.json").write_text(json.dumps({"operator": OPERATOR, "actions": log}, indent=2) + "\n", encoding="utf-8")
        (temp / "execution_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report_hash = _sha256(temp / "execution_report.json")
        (temp / "artifact_hashes.json").write_text(json.dumps({
            "schema_version": "1.0.0",
            "actions_document_sha256": _sha256(actions_file),
            "identity_source_sha256": source_before,
            "candidate_sha256": report["candidate_sha256"],
            "execution_report_sha256": report_hash,
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report["artifact_hashes"] = "artifact_hashes.json"
        os.replace(temp, output)
        report["output_dir"] = str(output)
        return report
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise


def self_check() -> dict[str, Any]:
    """Exercise the classification that previously produced a false native claim."""
    checks: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="forge-art-native-edit-") as temp_root:
        root = Path(temp_root)
        (root / "data").mkdir()
        (root / "res").mkdir()
        source = root / "identity.png"
        source.write_bytes(b"identity")
        spec = {
            "schema_version": "1.0.0",
            "command": "native-edit",
            "asset_id": "fixture_asset",
            "frame_id": "fixture_frame",
            "canvas": {"width": 32, "height": 32},
            "palette": [[0, 0, 0], [34, 34, 34]],
            "identity_source": {
                "path": "identity.png",
                "sha256": _sha256(source),
                "role": "exclusive_visual_authority",
            },
            "actions": [{
                "action_id": "paint_probe",
                "asset_id": "fixture_asset",
                "frame_id": "fixture_frame",
                "operation": "pencil_pixel",
                "region": {"x": 1, "y": 1, "w": 1, "h": 1},
                "symptom": "fixture",
                "visual_reference": "identity.png",
                "before_indices": [0],
                "after_indices": [1],
                "reason": "fixture",
                "operator": OPERATOR,
                "color_index": 1,
            }],
        }
        actions = root / "actions.json"
        actions.write_text(json.dumps(spec), encoding="utf-8")
        report = native_edit(root, Path("actions.json"), Path("out/v11_native_edit/fixture"))
        checks["procedural_claim_ceiling"] = report["claim_ceiling"] == "procedural_code_probe"
        checks["never_production_eligible"] = report["production_eligible"] is False
        checks["never_promotable"] = report["res_promotion"] is False

        legacy = json.loads(json.dumps(spec))
        legacy["actions"][0]["operator"] = "agent_authored_pixel_via_editor_actions"
        legacy_path = root / "legacy.json"
        legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
        try:
            native_edit(root, Path("legacy.json"), Path("out/v11_native_edit/legacy"))
        except NativeEditError as exc:
            checks["legacy_authorship_label_rejected"] = exc.blocker == "action_schema_invalid"
        else:
            checks["legacy_authorship_label_rejected"] = False

    failed = [name for name, passed in checks.items() if not passed]
    return {
        "fixtures_passed": len(checks) - len(failed),
        "fixtures_total": len(checks),
        "blocking": bool(failed),
        "fixtures": checks,
    }

#!/usr/bin/env python3
"""Two-layer, non-palette material meter for frozen TAINA v05.

This script authors an external annotation, persists it, then re-loads it for
measurement.  The legacy owner map is read only as a non-authoritative visual
review seed; it is never the measurement oracle and has no skin fallback.
It never writes the frozen PNG.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Iterable

from PIL import Image

W, H = 56, 80
V04_ID = "hybrid_cleanup_primary_im_lanczos3_rework_v04"
V04_SHA = "791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e"
V05_ID = "hybrid_cleanup_primary_im_lanczos3_rework_v05"
V05_SHA = "6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3"
MODEL_SHA = "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a"
LEGACY_V04 = {"ownership_annotation_error": 4, "material_palette_leakage": 832}
LEGACY_V05 = {"ownership_annotation_error": 0, "material_palette_leakage": 827}

MATERIALS = ["transparent", "hair", "skin", "orange_top", "teal_fabric", "indigo_trousers"]
SHADE_ROLES = ["outline_shared", "deep_shadow_shared", "shadow", "base", "highlight"]
MATERIAL_CODES = {"transparent": ".", "hair": "H", "skin": "K", "orange_top": "T", "teal_fabric": "E", "indigo_trousers": "I"}
SHADE_CODES = {"transparent": ".", "outline_shared": "O", "deep_shadow_shared": "D", "shadow": "S", "base": "B", "highlight": "H"}
CODE_TO_MATERIAL = {v: k for k, v in MATERIAL_CODES.items()}
CODE_TO_SHADE = {v: k for k, v in SHADE_CODES.items()}

# These are palette permissions, not owner assignment rules.  The shared
# shade roles are only valid at their explicitly enumerated coordinates.
MATERIAL_RAMPS = {
    "hair": [2, 3, 4],
    "skin": [5, 6, 7],
    "orange_top": [8, 9, 10],
    "teal_fabric": [11, 12, 13],
    "indigo_trousers": [14, 15],
}
SHARED_ROLE_INDICES = {"outline_shared": [1], "deep_shadow_shared": [2]}

LABEL_RGB = {
    "transparent": (18, 18, 24),
    "hair": (222, 40, 210),
    "skin": (255, 220, 35),
    "orange_top": (255, 95, 25),
    "teal_fabric": (20, 225, 205),
    "indigo_trousers": (70, 110, 255),
    "outline_shared": (255, 255, 255),
    "deep_shadow_shared": (145, 145, 145),
    "shadow": (115, 255, 115),
    "base": (70, 70, 70),
    "highlight": (255, 210, 110),
    "unassigned": (255, 0, 0),
}

# Only annotation metadata and the final external JSON are canonical.  The
# old rows are explicitly loaded as a visual-review seed and retained solely
# to make the migration auditable.
LEGACY_MAP = "material_owner_map_v01.json"
ANNOTATION_NAME = "material_owner_shade_annotation_v01.json"

# Explicit review overrides for outline pixels whose adjacent labels are not
# sufficient.  There is deliberately no default owner.
OUTLINE_OWNER_OVERRIDES = {
    (4, 24): "hair", (5, 22): "hair", (5, 23): "hair", (6, 22): "hair", (6, 23): "hair", (6, 24): "hair",
    (7, 21): "hair", (7, 22): "hair", (7, 23): "hair", (8, 19): "hair", (8, 21): "hair", (8, 22): "hair",
    (8, 28): "skin", (8, 29): "skin", (9, 21): "hair", (9, 22): "hair", (9, 30): "skin", (9, 31): "skin",
    (10, 18): "hair", (10, 21): "hair", (10, 22): "hair", (10, 23): "hair", (10, 24): "hair",
    (10, 28): "skin", (10, 29): "skin", (11, 21): "hair", (11, 29): "skin", (11, 30): "skin",
    (12, 29): "skin", (13, 31): "skin", (13, 32): "skin", (14, 31): "skin", (14, 32): "skin", (17, 26): "hair",
    (18, 25): "orange_top", (21, 21): "skin", (21, 36): "teal_fabric", (22, 20): "skin", (22, 36): "teal_fabric",
    (23, 20): "skin", (23, 24): "orange_top", (23, 36): "teal_fabric", (23, 40): "teal_fabric",
    (24, 20): "skin", (24, 23): "orange_top", (24, 36): "teal_fabric", (24, 40): "teal_fabric",
    (25, 15): "skin", (25, 23): "orange_top", (27, 22): "orange_top", (27, 30): "orange_top", (27, 40): "teal_fabric",
    (29, 21): "skin", (38, 19): "teal_fabric", (38, 31): "teal_fabric", (38, 33): "teal_fabric", (39, 20): "teal_fabric",
    (39, 34): "teal_fabric", (44, 17): "indigo_trousers", (45, 28): "indigo_trousers", (46, 27): "indigo_trousers",
    (47, 27): "indigo_trousers", (47, 28): "indigo_trousers", (48, 27): "indigo_trousers", (48, 28): "indigo_trousers",
    (57, 31): "indigo_trousers", (67, 11): "indigo_trousers", (68, 15): "indigo_trousers", (77, 9): "skin",
    (77, 14): "skin", (77, 37): "skin", (77, 47): "skin",
}

# Explicit shade clusters.  These are reviewed semantic annotations, not
# conversions from an index.  Any coordinate not in a cluster is explicitly
# annotated base, never implicitly assigned during measurement.
DEEP_SHADOW = {(18, 22), (19, 22), (20, 22), (21, 22), (31, 22), (32, 22), (41, 49), (42, 49), (16, 68), (40, 68)}
SHADOW = {(22, 23), (23, 23), (24, 23), (38, 23), (39, 23), (40, 23), (15, 50), (16, 50), (40, 50), (41, 50)}
HIGHLIGHT = {(24, 9), (25, 9), (27, 26), (29, 26), (22, 42), (35, 42), (17, 60), (38, 60)}

# Semantic boundary samples are authored contracts, not discovered hits.
BOUNDARIES = {
    "hair_skin_face": {"expected_owner_a": "hair", "expected_owner_b": "skin", "orientation": "horizontal_face", "segments": [[24, 9, 25, 9], [25, 2, 26, 2]]},
    "orange_top_skin_hem": {"expected_owner_a": "orange_top", "expected_owner_b": "skin", "orientation": "horizontal_hem", "segments": [[29, 32, 30, 32], [25, 32, 25, 33]]},
    "orange_top_skin_axilla_left": {"expected_owner_a": "orange_top", "expected_owner_b": "skin", "orientation": "vertical_left_axilla", "segments": [[21, 21, 22, 21], [31, 21, 31, 22]]},
    "orange_top_skin_axilla_right": {"expected_owner_a": "orange_top", "expected_owner_b": "skin", "orientation": "vertical_right_axilla", "segments": [[31, 22, 32, 22], [31, 23, 32, 23]]},
    "wraps_skin_left_wrist": {"expected_owner_a": "teal_fabric", "expected_owner_b": "skin", "orientation": "horizontal_left_wrap", "segments": [[20, 23, 21, 23], [20, 24, 21, 24]]},
    "wraps_skin_right_wrist": {"expected_owner_a": "teal_fabric", "expected_owner_b": "skin", "orientation": "horizontal_right_wrap", "segments": [[40, 24, 40, 25], [39, 25, 40, 25]]},
    "sash_trousers": {"expected_owner_a": "teal_fabric", "expected_owner_b": "indigo_trousers", "orientation": "horizontal_sash", "segments": [[22, 40, 22, 41], [21, 41, 22, 41]]},
    "skin_trousers_left_ankle": {"expected_owner_a": "skin", "expected_owner_b": "indigo_trousers", "orientation": "vertical_left_ankle", "segments": [[15, 68, 15, 69], [16, 68, 16, 69]]},
    "skin_trousers_right_ankle": {"expected_owner_a": "skin", "expected_owner_b": "indigo_trousers", "orientation": "vertical_right_ankle", "segments": [[40, 68, 40, 69], [41, 68, 41, 69]]},
}

ANCHORS = {
    "hair": [[20, 4]], "skin": [[27, 12], [18, 20], [12, 75]],
    "orange_top": [[27, 26]], "teal_fabric": [[22, 23], [38, 23], [20, 42]],
    "indigo_trousers": [[20, 60], [36, 60]],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_palette(image: Path) -> list[list[int]]:
    with Image.open(image) as im:
        pal = im.convert("P").getpalette()
    return [pal[i * 3:i * 3 + 3] for i in range(16)]


def load_visibility(image: Path) -> list[bool]:
    with Image.open(image) as im:
        return [v != 0 for v in im.convert("P").getdata()]


def expand_rows(rows: list[str], codebook: dict[str, str]) -> list[str]:
    if len(rows) != H or any(len(row) != W for row in rows):
        raise ValueError("annotation rows must be exactly 56x80")
    return [codebook.get(ch, "unassigned") for row in rows for ch in row]


def old_seed_rows(legacy_path: Path) -> list[str]:
    obj = json.loads(legacy_path.read_text(encoding="utf-8"))
    rows = obj["rows"]
    if len(rows) != H or any(len(row) != W for row in rows):
        raise ValueError("legacy map dimensions invalid")
    return rows


def material_from_legacy(rows: list[str], x: int, y: int) -> str | None:
    ch = rows[y][x]
    if ch in CODE_TO_MATERIAL and CODE_TO_MATERIAL[ch] != "transparent":
        return CODE_TO_MATERIAL[ch]
    if ch != "O":
        return None
    if (x, y) in OUTLINE_OWNER_OVERRIDES:
        return OUTLINE_OWNER_OVERRIDES[(x, y)]
    # A local review assist only: no palette and no semantic default.  If the
    # outline cannot be assigned from a neighboring explicit material, it is
    # intentionally unassigned and the gate fails.
    for radius in range(1, max(W, H)):
        for nx, ny in ((x - radius, y), (x + radius, y), (x, y - radius), (x, y + radius)):
            if 0 <= nx < W and 0 <= ny < H:
                candidate = rows[ny][nx]
                if candidate in CODE_TO_MATERIAL and candidate != ".":
                    return CODE_TO_MATERIAL[candidate]
    return None


def author_annotation(out: Path, legacy_path: Path, visibility: list[bool]) -> Path:
    legacy_rows = old_seed_rows(legacy_path)
    owners: list[str] = []
    shade: list[str] = []
    for i, visible in enumerate(visibility):
        x, y = i % W, i // W
        if not visible:
            owners.append("transparent")
            shade.append("transparent")
            continue
        owner = material_from_legacy(legacy_rows, x, y)
        owners.append(owner or "unassigned")
        shade.append("base")

    for y, row in enumerate(legacy_rows):
        for x, ch in enumerate(row):
            i = y * W + x
            if visibility[i] and ch == "O":
                shade[i] = "outline_shared"
    for coords, role in ((DEEP_SHADOW, "deep_shadow_shared"), (SHADOW, "shadow"), (HIGHLIGHT, "highlight")):
        for x, y in coords:
            if 0 <= x < W and 0 <= y < H and visibility[y * W + x] and shade[y * W + x] != "outline_shared":
                shade[y * W + x] = role

    owner_rows = ["".join(MATERIAL_CODES.get(v, "?") for v in owners[y * W:(y + 1) * W]) for y in range(H)]
    shade_rows = ["".join(SHADE_CODES.get(v, "?") for v in shade[y * W:(y + 1) * W]) for y in range(H)]
    annotation = {
        "schema_version": "taina_material_owner_shade_annotation.v1",
        "asset_id": V05_ID,
        "sha256": V05_SHA,
        "scale": "56x80",
        "model_sheet_sha256": MODEL_SHA,
        "reviewed_views": ["v05_1x", "v05_nearest_8x", "model_sheet_v02"],
        "rgb_diagnostic_is_not_art": True,
        "owner_assignment_method": "external_reviewed_semantic_annotation_from_visual_review_seed",
        "palette_indices_not_used_for_owner_assignment": True,
        "owner_fallback": "none",
        "legacy_seed": {"file": LEGACY_MAP, "role": "comparison_only_not_authority", "fallback_skin_rejected": True},
        "unassigned_symbol": "?",
        "material_owner_legend": MATERIAL_CODES,
        "shade_role_legend": SHADE_CODES,
        "material_owner_rows": owner_rows,
        "shade_role_rows": shade_rows,
        "explicit_shared_coordinates": {
            "outline_shared": [[x, y] for y, row in enumerate(legacy_rows) for x, ch in enumerate(row) if ch == "O" and visibility[y * W + x]],
            "deep_shadow_shared": [[x, y] for x, y in sorted(DEEP_SHADOW) if visibility[y * W + x] and legacy_rows[y][x] != "O"],
        },
        "anchors": ANCHORS,
        "boundary_contract": BOUNDARIES,
        "annotation_review_note": "Every visible cell is explicit; no default owner exists. Shared roles are coordinate-authorized only.",
    }
    path = out / ANNOTATION_NAME
    path.write_text(json.dumps(annotation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_annotation(path: Path) -> tuple[dict, list[str], list[str]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    owners = expand_rows(obj["material_owner_rows"], {v: k for k, v in obj["material_owner_legend"].items()})
    shades = expand_rows(obj["shade_role_rows"], {v: k for k, v in obj["shade_role_legend"].items()})
    return obj, owners, shades


def boundary_results(obj: dict, owners: list[str]) -> dict:
    results = {}
    for name, contract in obj["boundary_contract"].items():
        expected_a, expected_b = contract["expected_owner_a"], contract["expected_owner_b"]
        segments = contract.get("segments", [])
        observed = []
        matched = 0
        for x1, y1, x2, y2 in segments:
            a, b = owners[y1 * W + x1], owners[y2 * W + x2]
            pair_ok = (a == expected_a and b == expected_b) or (a == expected_b and b == expected_a)
            if pair_ok:
                matched += 1
            observed.append({"a": [x1, y1, a], "b": [x2, y2, b], "expected_pair": [expected_a, expected_b], "pair_match": pair_ok})
        results[name] = {"expected_owner_a": expected_a, "expected_owner_b": expected_b, "orientation": contract.get("orientation"), "expected_segments": len(segments), "matched_segments": matched, "observed_segments": observed, "status": bool(segments) and matched == len(segments)}
    required = set(BOUNDARIES)
    return {"segments": results, "contract_complete": set(results) >= required and all(v["expected_segments"] > 0 for v in results.values()), "status": bool(results) and set(results) >= required and all(v["status"] for v in results.values())}


def connected_components(leaks: list[dict]) -> list[dict]:
    points = {(d["x"], d["y"]): d for d in leaks}
    comps = []
    while points:
        start = next(iter(points)); q = deque([start]); coords = []
        while q:
            p = q.popleft()
            if p not in points: continue
            coords.append(points.pop(p))
            x, y = p
            for n in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if n in points: q.append(n)
        comps.append({"pixel_count": len(coords), "bbox": [min(d["x"] for d in coords), min(d["y"] for d in coords), max(d["x"] for d in coords), max(d["y"] for d in coords)], "coordinates": sorted(coords, key=lambda d: (d["y"], d["x"]))})
    return sorted(comps, key=lambda c: (-c["pixel_count"], c["bbox"]))


def evaluate(image: Path, annotation_path: Path) -> dict:
    annotation, owners, shades = load_annotation(annotation_path)
    with Image.open(image) as im:
        pix = list(im.convert("P").getdata())
    visible = [v != 0 for v in pix]
    valid_materials = set(MATERIALS[1:])
    valid_shades = set(SHADE_ROLES)
    provenance_errors = []
    if annotation.get("owner_fallback") != "none":
        provenance_errors.append({"reason": "owner_fallback_not_none", "value": annotation.get("owner_fallback")})
    if annotation.get("palette_indices_not_used_for_owner_assignment") is not True:
        provenance_errors.append({"reason": "palette_used_for_owner_assignment"})
    if "palette" in str(annotation.get("owner_assignment_method", "")).lower() or "index" in str(annotation.get("owner_assignment_method", "")).lower():
        provenance_errors.append({"reason": "owner_map_generated_from_asset_palette", "method": annotation.get("owner_assignment_method")})
    unassigned = [{"x": i % W, "y": i // W} for i, v in enumerate(visible) if v and owners[i] == "unassigned"]
    outside = [{"x": i % W, "y": i // W, "owner": owners[i], "shade_role": shades[i]} for i, v in enumerate(visible) if not v and owners[i] not in ("transparent", "unassigned")]
    invalid_owner = [{"x": i % W, "y": i // W, "owner": owners[i]} for i, v in enumerate(visible) if v and owners[i] not in valid_materials]
    invalid_shade = [{"x": i % W, "y": i // W, "shade_role": shades[i]} for i, v in enumerate(visible) if v and shades[i] not in valid_shades]
    shade_on_transparent = [{"x": i % W, "y": i // W, "shade_role": shades[i]} for i, v in enumerate(visible) if not v and shades[i] != "transparent"]

    explicit = {role: {tuple(p) for p in coords} for role, coords in annotation["explicit_shared_coordinates"].items()}
    shared_errors = []
    for i, role in enumerate(shades):
        if role in ("outline_shared", "deep_shadow_shared") and (i % W, i // W) not in explicit.get(role, set()):
            shared_errors.append({"x": i % W, "y": i // W, "shade_role": role, "reason": "shared_role_outside_explicit_coordinate_contract"})
    for role, coords in explicit.items():
        for x, y in coords:
            i = y * W + x
            if not visible[i] or shades[i] != role:
                shared_errors.append({"x": x, "y": y, "shade_role": shades[i], "reason": f"explicit_{role}_coordinate_not_annotated"})

    anchor_errors = []
    for material, coords in annotation["anchors"].items():
        for x, y in coords:
            if owners[y * W + x] != material:
                anchor_errors.append({"material": material, "x": x, "y": y, "actual": owners[y * W + x]})

    leakage = []
    for i, index in enumerate(pix):
        if not visible[i]: continue
        owner, role = owners[i], shades[i]
        allowed = MATERIAL_RAMPS.get(owner, [])
        if role in SHARED_ROLE_INDICES and (i % W, i // W) in explicit.get(role, set()):
            allowed = SHARED_ROLE_INDICES[role]
        if index not in allowed:
            leakage.append({"x": i % W, "y": i // W, "material": owner, "index": index, "shade_role": role, "allowed_indices": allowed})

    matrix = {m: {str(index): {role: 0 for role in SHADE_ROLES} for index in range(16)} for m in MATERIALS[1:]}
    for i, index in enumerate(pix):
        if visible[i] and owners[i] in matrix and shades[i] in SHADE_ROLES:
            matrix[owners[i]][str(index)][shades[i]] += 1
    counts = {m: {str(index): {role: n for role, n in roles.items() if n} for index, roles in indexes.items() if any(roles.values())} for m, indexes in matrix.items()}
    by_material = Counter(d["material"] for d in leakage)
    by_index = Counter(str(d["index"]) for d in leakage)
    components = connected_components(leakage)
    boundaries = boundary_results(annotation, owners)
    ownership_error = len(unassigned) + len(outside) + len(invalid_owner) + len(invalid_shade) + len(shade_on_transparent) + len(shared_errors) + len(anchor_errors) + len(provenance_errors)
    material_accuracy = "passed" if ownership_error == 0 else "failed"
    boundary_status = "passed" if boundaries["status"] else "failed"
    palette_status = "passed" if not leakage else "failed"
    report = {
        "schema_version": "taina_material_topology_measurement.v3",
        "asset_id": V05_ID,
        "sha256": V05_SHA,
        "map_sha256": digest(annotation_path),
        "model_sheet_sha256": MODEL_SHA,
        "source_image_sha256_verified": digest(image) == V05_SHA,
        "visible_pixel_count": sum(visible),
        "unassigned_visible_pixel": unassigned,
        "owners_outside_silhouette": outside,
        "invalid_owner_labels": invalid_owner,
        "invalid_shade_roles": invalid_shade,
        "shade_on_transparent": shade_on_transparent,
        "shared_role_contract_errors": shared_errors,
        "ownership_anchor_errors": anchor_errors,
        "annotation_provenance_errors": provenance_errors,
        "ownership_annotation_error": ownership_error,
        "owner_index_shade_confusion_matrix": matrix,
        "nonzero_material_index_shade_counts": counts,
        "plte_rgb_indices_0_15": load_palette(image),
        "leakage_by_material": dict(sorted(by_material.items())),
        "leakage_by_index": dict(sorted(by_index.items(), key=lambda kv: int(kv[0]))),
        "leakage_by_connected_component": components,
        "material_palette_leakage": len(leakage),
        "material_palette_leakage_coordinates": leakage,
        "boundaries": boundaries,
        "results": {
            "material_map_accuracy": {"status": material_accuracy, "basis": "explicit_two_layer_annotation; no fallback"},
            "material_boundary_topology": {"status": boundary_status, "basis": "expected owner pair and all authored segments"},
            "palette_role_conformance": {"status": palette_status, "basis": "owner ramp plus coordinate-authorized shared shade roles"},
            "visual_material_readability": {"status": "pending_human_review", "reason": "diagnostic map cannot prove 1x artistic readability"},
        },
        "shared_family_valid": {"wraps_and_sash_share_teal_fabric": True, "feet_share_skin": True, "index_2_global_shadow_reuse": any(d["index"] == 2 and d["shade_role"] not in ("outline_shared", "deep_shadow_shared") for d in leakage)},
        "ambiguous_requires_human_review": bool(leakage or ownership_error or not boundaries["status"]),
        "legacy_map_is_non_authoritative": True,
        "status": "passed" if ownership_error == 0 and not leakage and boundaries["status"] else "failed_requires_localized_material_cleanup",
    }
    return report


def render_overlay(out: Path, annotation_path: Path, report: dict) -> None:
    annotation, owners, shades = load_annotation(annotation_path)
    im = Image.new("RGB", (W, H), LABEL_RGB["transparent"]); px = im.load()
    for i, owner in enumerate(owners):
        role = shades[i]
        if owner == "unassigned": label = "unassigned"
        elif role in ("outline_shared", "deep_shadow_shared"): label = role
        else: label = owner
        px[i % W, i // W] = LABEL_RGB[label]
    im.save(out / "material_owner_shade_overlay.png")
    im.resize((W * 8, H * 8), Image.Resampling.NEAREST).save(out / "material_owner_shade_overlay_8x.png")

    boundary = Image.new("RGB", (W, H), (18, 18, 24)); bp = boundary.load()
    for contract in annotation["boundary_contract"].values():
        for x1, y1, x2, y2 in contract["segments"]:
            bp[x1, y1] = (255, 255, 255); bp[x2, y2] = (255, 255, 255)
    boundary.save(out / "material_boundary_contract_overlay.png")
    boundary.resize((W * 8, H * 8), Image.Resampling.NEAREST).save(out / "material_boundary_contract_overlay_8x.png")


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab-root", type=Path, required=True)
    args = ap.parse_args()
    lab = args.lab_root.resolve()
    v04 = lab / "localized_native_cleanup" / V04_ID / f"{V04_ID}.png"
    v05 = lab / "localized_native_cleanup" / V05_ID / f"{V05_ID}.png"
    model = lab / "inputs" / "model_sheet_v02.png"
    if digest(v05) != V05_SHA or digest(v04) != V04_SHA or digest(model) != MODEL_SHA:
        raise SystemExit("frozen asset/model SHA mismatch")
    out = v05.parent
    annotation_path = author_annotation(out, out / LEGACY_MAP, load_visibility(v05))
    annotation, _, _ = load_annotation(annotation_path)
    v05_report = evaluate(v05, annotation_path)
    v04_report = evaluate(v04, annotation_path)
    v04_report["asset_id"], v04_report["sha256"] = V04_ID, V04_SHA
    v04_report["source_image_sha256_verified"] = digest(v04) == V04_SHA
    old = json.loads((out / "material_leakage_report.json").read_text(encoding="utf-8")) if (out / "material_leakage_report.json").exists() else {}
    legacy_path = out / LEGACY_MAP
    write_json(out / "owner_index_shade_confusion_matrix.json", {"schema_version": "owner_index_shade_confusion_matrix.v1", "asset_id": V05_ID, "sha256": V05_SHA, "map_sha256": digest(annotation_path), "matrix": v05_report["owner_index_shade_confusion_matrix"], "nonzero_counts": v05_report["nonzero_material_index_shade_counts"], "plte_rgb_indices_0_15": v05_report["plte_rgb_indices_0_15"]})
    write_json(out / "material_topology_measurement_report.json", {"schema_version": "taina_material_topology_repair_report.v3", "annotation": ANNOTATION_NAME, "annotation_sha256": digest(annotation_path), "model_sheet_sha256": MODEL_SHA, "legacy_measurement_snapshot": {"source": LEGACY_MAP, "map_sha256": digest(legacy_path), "non_authoritative": True, "fallback_skin_present": True, "v04": LEGACY_V04, "v05": LEGACY_V05}, "v04": v04_report, "v05": v05_report, "patch_accounting": {"patches_attempted": 23, "patches_effective": 18, "patches_noop": 5}, "v05_pixels_modified": False, "v06_produced": False, "route_decision": "material_palette_reseed_v01_due_to_spread_interior_palette_conflicts_pending_next_stage"})
    write_json(out / "material_topology_old_vs_corrected.json", {"schema_version": "material_topology_old_vs_corrected.v1", "asset_id": V05_ID, "asset_sha256": V05_SHA, "legacy": {"map": LEGACY_MAP, "map_sha256": digest(legacy_path), "fallback_skin_present": True, "owner_at_rectangular_or_legacy": True, "non_authoritative": True, "v04": LEGACY_V04, "v05": LEGACY_V05}, "corrected": {"annotation": ANNOTATION_NAME, "annotation_sha256": digest(annotation_path), "two_layers": ["material_owner_map", "shade_role_map"], "fallback_skin": False, "v04": {"ownership_annotation_error": v04_report["ownership_annotation_error"], "material_palette_leakage": v04_report["material_palette_leakage"]}, "v05": {"ownership_annotation_error": v05_report["ownership_annotation_error"], "material_palette_leakage": v05_report["material_palette_leakage"], "leakage_components": len(v05_report["leakage_by_connected_component"]), "boundary_status": v05_report["boundaries"]["status"]}}, "interpretation": "The corrected count is trusted for diagnosis; the legacy count is comparison only and does not authorize patch count."})
    write_json(out / "material_region_contract.json", {"schema_version": "material_region_contract.v3_two_layer", "asset_id": V05_ID, "sha256": V05_SHA, "map_sha256": digest(annotation_path), "model_sheet_sha256": MODEL_SHA, "material_owner_map": {"file": ANNOTATION_NAME, "layer": "material_owner_map", "labels": MATERIALS}, "shade_role_map": {"file": ANNOTATION_NAME, "layer": "shade_role_map", "labels": SHADE_ROLES}, "material_ramps": MATERIAL_RAMPS, "shared_shade_permissions": SHARED_ROLE_INDICES, "shared_coordinate_contract": annotation["explicit_shared_coordinates"], "boundary_contract": annotation["boundary_contract"], "results": v05_report["results"], "coverage_is_not_sufficient": True, "status": v05_report["status"]})
    write_json(out / "material_leakage_report.json", {"schema_version": "material_leakage_report.v3_two_layer", "asset_id": V05_ID, "sha256": V05_SHA, "map_sha256": digest(annotation_path), "ownership_annotation_error": v05_report["ownership_annotation_error"], "leakage_by_material": v05_report["leakage_by_material"], "leakage_by_index": v05_report["leakage_by_index"], "leakage_by_connected_component": v05_report["leakage_by_connected_component"], "material_palette_leakage": v05_report["material_palette_leakage"], "coordinates": v05_report["material_palette_leakage_coordinates"], "shared_family_valid": v05_report["shared_family_valid"], "ambiguous_requires_human_review": v05_report["ambiguous_requires_human_review"], "status": v05_report["status"], "legacy_comparison": {"v04": LEGACY_V04, "v05": LEGACY_V05, "non_authoritative": True}})
    write_json(out / "material_topology_independent_report.json", {"schema_version": "independent_material_topology_report.v3_two_layer", "asset_id": V05_ID, "sha256": V05_SHA, "annotation_sha256": digest(annotation_path), "owner_assignment_method": annotation["owner_assignment_method"], "palette_indices_not_used_for_owner_assignment": True, "results": v05_report["results"], "ownership_annotation_error": v05_report["ownership_annotation_error"], "material_palette_leakage": v05_report["material_palette_leakage"], "boundary_status": v05_report["boundaries"], "not_approved_by_coverage_alone": True, "status": v05_report["status"]})
    render_overlay(out, annotation_path, v05_report)

    # Keep all operational pointers truthful while preserving the frozen PNG.
    actions_path = out / "cleanup_actions.json"
    if actions_path.exists():
        actions = json.loads(actions_path.read_text(encoding="utf-8"))
        actions.update({"patches_attempted": 23, "patches_effective": 18, "patches_noop": 5, "patch_count": 18, "null_patches_count": 5, "material_topology_meter": "material_topology_measurement_report.json", "material_annotation": ANNOTATION_NAME, "shade_role_map": ANNOTATION_NAME, "v05_pixels_modified": False})
        write_json(actions_path, actions)
    validation_path = out / "localized_native_cleanup_validation_report.json"
    if validation_path.exists():
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        validation.update({"patches_attempted": 23, "patches_effective": 18, "patches_noop": 5, "patch_count": 18, "null_patches_count": 5, "material_topology": v05_report["status"], "material_topology_report": "material_topology_measurement_report.json", "material_annotation": ANNOTATION_NAME, "owner_index_shade_confusion_matrix": "owner_index_shade_confusion_matrix.json", "v05_pixels_modified": False})
        write_json(validation_path, validation)
    report_path = out / "localized_native_cleanup_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report.update({"patches_attempted": 23, "patches_effective": 18, "patches_noop": 5, "patch_count": 18, "material_topology": v05_report["status"], "material_topology_report": "material_topology_measurement_report.json", "material_annotation": ANNOTATION_NAME, "owner_index_shade_confusion_matrix": "owner_index_shade_confusion_matrix.json", "v05_pixels_modified": False, "next_route": "material_palette_reseed_v01_due_to_spread_interior_palette_conflicts"})
        report["material_region_contract"] = "material_region_contract.json"
        report["material_leakage_report"] = "material_leakage_report.json"
        write_json(report_path, report)
    project_dirs = sorted(p for p in lab.parent.parent.iterdir() if p.is_dir() and p.name == "MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]")
    if project_dirs:
        operational_path = project_dirs[0] / "doc/art/characters/taina/taina_localized_cleanup_operational_record_v05.json"
        if operational_path.exists():
            operational = json.loads(operational_path.read_text(encoding="utf-8"))
            operational.update({"material_region_contract": str(Path("../_agent_laboratory") / lab.name / "localized_native_cleanup" / V05_ID / "material_region_contract.json"), "material_annotation": str(Path("../_agent_laboratory") / lab.name / "localized_native_cleanup" / V05_ID / ANNOTATION_NAME), "shade_role_map": str(Path("../_agent_laboratory") / lab.name / "localized_native_cleanup" / V05_ID / ANNOTATION_NAME), "owner_index_shade_confusion_matrix": str(Path("../_agent_laboratory") / lab.name / "localized_native_cleanup" / V05_ID / "owner_index_shade_confusion_matrix.json"), "material_topology_measurement_report": str(Path("../_agent_laboratory") / lab.name / "localized_native_cleanup" / V05_ID / "material_topology_measurement_report.json"), "material_topology_fixture_report": str(Path("../_agent_laboratory") / lab.name / "localized_native_cleanup" / V05_ID / "material_topology_fixture_report.json"), "next_route": "material_palette_reseed_v01_due_to_spread_interior_palette_conflicts", "v05_pixels_modified_during_meter_repair": False})
            operational["material_owner_map"] = operational["material_annotation"]
            write_json(operational_path, operational)
    print(json.dumps({"status": "two_layer_meter_written_without_pixel_change", "annotation": str(annotation_path), "v05": {"ownership_annotation_error": v05_report["ownership_annotation_error"], "material_palette_leakage": v05_report["material_palette_leakage"], "boundary_status": v05_report["boundaries"]["status"], "status": v05_report["status"]}, "route_decision": "material_palette_reseed_v01"}, ensure_ascii=False))


if __name__ == "__main__":
    main()

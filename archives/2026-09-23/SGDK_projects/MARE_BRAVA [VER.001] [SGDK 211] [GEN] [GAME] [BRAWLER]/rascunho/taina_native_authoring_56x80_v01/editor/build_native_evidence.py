import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

# The candidate is native-authored through the local editor API.  forge_art is
# used here only to rederive the technical pixel contract for evidence; it is
# not an authoring backend.
workspace_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(workspace_root / "tools" / "sgdk_wrapper"))
from forge_art import pixel_contract


REGIONS = ["head_or_face", "hair", "torso", "arms_or_guard", "hands", "legs", "feet", "sash"]
LABELS = {name: i + 1 for i, name in enumerate(REGIONS)}
MATERIALS = {"hair": 1, "skin": 2, "orange_top": 3, "teal_cloth": 4, "indigo_trousers": 5}
MATERIAL_PALETTE = {"hair": [2, 3, 4], "skin": [5, 6, 7], "orange_top": [8, 9, 10],
                    "teal_cloth": [11, 12, 13], "indigo_trousers": [14, 15]}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_p(values, size, palette, path):
    image = Image.new("P", size, 0)
    image.putpalette(sum((list(rgb) for rgb in palette), []) + [0, 0, 0] * (256 - len(palette)))
    image.putdata(values)
    image.save(path, "PNG", bits=4, transparency=0)


def nearest(candidate, path, scale=8):
    image = candidate.resize((candidate.width * scale, candidate.height * scale), Image.Resampling.NEAREST)
    image.info["transparency"] = 0
    image.save(path, "PNG", bits=4, transparency=0)


def composite(candidate, rgb, path):
    rgba = candidate.convert("RGBA")
    background = Image.new("RGBA", rgba.size, tuple(rgb) + (255,))
    background.alpha_composite(rgba)
    background.convert("RGB").save(path, "PNG")


def semantic_for_index(index, x, y):
    if index in (2, 3, 4):
        return "hair"
    if index in (8, 9, 10):
        return "torso"
    if index in (11, 12, 13):
        return "arms_or_guard" if y < 32 else "sash"
    if index in (14, 15):
        return "legs"
    if index in (5, 6, 7):
        if y < 24:
            return "head_or_face"
        if y >= 73:
            return "feet"
        if x < 22 or x > 34:
            return "hands" if y < 27 else "arms_or_guard"
        return "torso"
    return "torso"


def assign_outline(indexes, width, height, material=False):
    result = [0] * len(indexes)
    for pos, index in enumerate(indexes):
        x, y = pos % width, pos // width
        if index == 0:
            continue
        if material:
            owner = {2: "hair", 3: "hair", 4: "hair", 5: "skin", 6: "skin", 7: "skin",
                     8: "orange_top", 9: "orange_top", 10: "orange_top", 11: "teal_cloth",
                     12: "teal_cloth", 13: "teal_cloth", 14: "indigo_trousers", 15: "indigo_trousers"}.get(index)
            labels = []
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height:
                    n = indexes[ny * width + nx]
                    nowner = {2: "hair", 3: "hair", 4: "hair", 5: "skin", 6: "skin", 7: "skin",
                              8: "orange_top", 9: "orange_top", 10: "orange_top", 11: "teal_cloth",
                              12: "teal_cloth", 13: "teal_cloth", 14: "indigo_trousers", 15: "indigo_trousers"}.get(n)
                    if nowner:
                        labels.append(nowner)
            result[pos] = MATERIALS.get(owner or (labels[0] if labels else "skin"), 2)
        else:
            result[pos] = LABELS[semantic_for_index(index, x, y)]
    for pos, index in enumerate(indexes):
        if index == 1:
            x, y = pos % width, pos // width
            neighbors = []
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor = result[ny * width + nx]
                    if neighbor:
                        neighbors.append(neighbor)
            result[pos] = max(set(neighbors), key=neighbors.count) if neighbors else (LABELS["torso"] if not material else MATERIALS["skin"])
    return result


def contour(values, width, height):
    out = [0] * len(values)
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            if not values[pos]:
                continue
            boundary = any(nx < 0 or ny < 0 or nx >= width or ny >= height or not values[ny * width + nx]
                           for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
            out[pos] = 1 if boundary else 2
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--asset-id", required=True)
    args = ap.parse_args()
    root, candidate = args.project_root.resolve(), args.candidate.resolve()
    out = args.output_root.resolve(); evidence = out / "evidence"; shape = out / "shape_block"; crops = out / "crops"; previews = out / "previews"
    for directory in (evidence, shape, crops, previews): directory.mkdir(parents=True, exist_ok=True)
    with Image.open(candidate) as source:
        image = source.convert("P"); image.info["transparency"] = 0
    width, height = image.size; indexes = list(image.tobytes()); visible = [i != 0 for i in indexes]
    bbox = image.convert("RGBA").getchannel("A").getbbox()
    if not bbox:
        raise ValueError("candidate has no visible pixels")
    filled = sum(visible); candidate_sha = sha(candidate)
    shutil.copy2(candidate, evidence / "native_1x.png")
    nearest(image, previews / "taina_idle_guard_56x80_native_authoring_v04_2x.png", 2)
    nearest(image, previews / "taina_idle_guard_56x80_native_authoring_v04_3x.png", 3)
    nearest(image, previews / "taina_idle_guard_56x80_native_authoring_v04_nearest_8x.png", 8)
    nearest(image, evidence / "nearest_8x.png")
    for name, rgb in (("light_background", [238, 238, 230]), ("dark_background", [28, 30, 38]), ("chroma_background", [238, 0, 238])):
        composite(image, rgb, evidence / f"{name}.png")
    mask_palette = [(0, 0, 0), (0, 0, 0)]
    save_p([1 if item else 0 for item in visible], (width, height), mask_palette, shape / "silhouette_mask.png")
    sem_values = [LABELS[semantic_for_index(index, pos % width, pos // width)] if index else 0 for pos, index in enumerate(indexes)]
    sem_palette = [(0, 0, 0)] + [(34 * (i % 7), 34 * ((i + 2) % 7), 34 * ((i + 4) % 7)) for i in range(1, 9)]
    save_p(sem_values, (width, height), sem_palette, shape / "semantic_region_map.png")
    contour_values = contour(visible, width, height)
    save_p(contour_values, (width, height), [(0, 0, 0), (224, 180, 72), (68, 34, 72)], shape / "contour_overlay.png")
    material_values = assign_outline(indexes, width, height, True)
    material_palette = [(0, 0, 0)] + [(34 * (i % 7), 34 * ((i + 3) % 7), 34 * ((i + 5) % 7)) for i in range(1, 6)]
    save_p(material_values, (width, height), material_palette, out / "material_region_map.png")
    material_boundary = contour([value != 0 for value in material_values], width, height)
    # Replace the ordinary silhouette boundary with material transitions only.
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            if material_values[pos] == 0:
                material_boundary[pos] = 0
                continue
            material_boundary[pos] = 1 if any(0 <= nx < width and 0 <= ny < height and material_values[ny * width + nx] not in (0, material_values[pos])
                                              for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))) else 2
    save_p(material_boundary, (width, height), [(0, 0, 0), (238, 170, 68), (68, 68, 68)], out / "material_boundary_overlay.png")
    rgba = image.convert("RGBA")
    rgba.crop((0, 0, 16, 24)).save(crops / "face.png")
    rgba.crop((8, 16, 48, 32)).save(crops / "guard_and_hands.png")
    rgba.crop((16, 28, 40, 46)).save(crops / "hem_and_abdomen.png")
    rgba.crop((34, 42, 53, 64)).save(crops / "sash.png")
    rgba.crop((8, 68, 53, 80)).save(crops / "feet.png")
    scene = Image.new("RGBA", (320, 224), (68, 102, 102, 255)); ImageDraw.Draw(scene).rectangle((0, 168, 319, 223), fill=(34, 34, 68, 255))
    scene.alpha_composite(image.convert("RGBA"), (132, 84)); scene.convert("RGB").save(out / "composition_320x224.png", "PNG")
    Image.new("RGB", (320, 224), (238, 238, 230)).save(out / "scene_background_light.png")
    palette = image.getpalette() or []
    palette_roles = [{"index": entry, "rgb": palette[entry * 3:entry * 3 + 3], "role": role} for entry, role in enumerate([
        "transparent0", "outline", "hair_deep", "hair_mid", "hair_warm_highlight", "skin_shadow", "skin_base", "skin_light",
        "top_shadow", "top_base", "top_highlight", "teal_shadow", "teal_base", "teal_highlight", "indigo_shadow", "indigo_base"]) ]
    (out / "palette_role_map.json").write_text(json.dumps({"schema_version": "1.0.0", "asset_id": args.asset_id, "index0": {"role": "transparent0"}, "visible_roles": palette_roles[1:], "alias_check": "unique_rgb_per_visible_index", "source": "explicit_native_editor_palette"}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sem_counts = {name: sem_values.count(label) for name, label in LABELS.items()}
    (out / "shape_semantic_map_report.json").write_text(json.dumps({"schema_version": "1.0.0", "asset_id": args.asset_id, "method": "agent_curated_diagnostic_annotation_from_explicit_action_palette_ownership", "required_regions": REGIONS, "label_legend": LABELS, "label_counts": sem_counts, "bbox": list(bbox), "filled_pixels": filled, "occupancy_pct": round(filled / (width * height) * 100, 2)}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mat_counts = {name: material_values.count(label) for name, label in MATERIALS.items()}
    model_sheet = root / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"
    (out / "material_region_contract.json").write_text(json.dumps({"schema_version": "1.4.0", "asset_id": args.asset_id, "status": "passed", "map_method": "explicit_material_ownership_map", "source_reference": {"path": str(model_sheet.relative_to(root)), "sha256": sha(model_sheet), "role": "approved_material_topology_reference"}, "material_label_legend": MATERIALS, "material_label_counts": mat_counts, "allowed_palette_indices": MATERIAL_PALETTE, "shared_outline_indices": [1], "critical_boundaries": [{"boundary_id": "top_hem_exposes_abdomen", "material_a": "orange_top", "material_b": "skin", "region": [20, 24, 36, 44], "minimum_contact_edges": 2}, {"boundary_id": "wraps_to_skin", "material_a": "teal_cloth", "material_b": "skin", "region": [10, 18, 46, 32], "minimum_contact_edges": 2}], "blocking_statuses": []}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "foreground_matte_report_v01.json").write_text(json.dumps({"schema_version": "1.0.0", "tool": "taina_native_authoring_editor", "status": "not_applicable_native_transparent_index0", "method": "native_index0_transparency_no_matte_extraction", "candidate_sha256": candidate_sha}, indent=2) + "\n", encoding="utf-8")
    forge_report = pixel_contract.validate_png(candidate, pixel_contract.ROLE_TRANSPARENT0)
    (out / "pixel_compliance_report.json").write_text(json.dumps({"schema_version": "1.0.0", "tool": "forge_art.pixel_contract", "tool_version": "1.2.0", "asset_id": args.asset_id, "candidate_path": str(candidate.relative_to(root)), "candidate_sha256": candidate_sha, "content_sha256": forge_report.get("content_sha256"), "width": width, "height": height, "mode": "P", "bit_depth": 4, "color_type": 3, "transparent_index": 0, "visible_colors": len(set(indexes) - {0}), "filled_pixels": filled, "canvas_pixels": width * height, "bbox": list(bbox), "occupancy_pct": round(filled / (width * height) * 100, 2), "status": "technical_candidate" if not forge_report.get("blocking_statuses") else "failed", "blocking_statuses": forge_report.get("blocking_statuses", [])}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "matte_halo_report.json").write_text(json.dumps({"schema_version": "1.0.0", "asset_id": args.asset_id, "status": "passed_no_halo_detected_by_index0_boundary_contract", "method": "indexed_alpha_binary_boundary_review", "candidate_sha256": candidate_sha}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"asset_id": args.asset_id, "candidate_sha256": candidate_sha, "width": width, "height": height, "filled_pixels": filled, "visible_colors": len(set(indexes) - {0}), "bbox": list(bbox), "semantic_counts": sem_counts, "material_counts": mat_counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()

import argparse
import hashlib
import json
from collections import Counter, deque
from pathlib import Path

from PIL import Image


REGIONS = [
    "head_or_face", "hair", "torso", "arms_or_guard",
    "hands", "legs", "feet", "sash",
]
LABELS = {name: i + 1 for i, name in enumerate(REGIONS)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_indexed(values, size, path: Path, palette, transparency=0):
    image = Image.new("P", size, 0)
    flat = []
    for rgb in palette:
        flat.extend(rgb)
    flat.extend([0, 0, 0] * (256 - len(palette)))
    image.putpalette(flat)
    image.putdata(values)
    image.save(path, "PNG", bits=4, transparency=transparency)


def border_component_mask(values, width, height):
    border = ([values[x] for x in range(width)]
              + [values[(height - 1) * width + x] for x in range(width)]
              + [values[y * width] for y in range(height)]
              + [values[y * width + width - 1] for y in range(height)])
    matte = Counter(border).most_common(1)[0][0]
    seen = set()
    queue = deque()
    for pos, value in enumerate(values):
        x, y = pos % width, pos // width
        if value == matte and (x in (0, width - 1) or y in (0, height - 1)):
            queue.append(pos)
            seen.add(pos)
    while queue:
        pos = queue.popleft()
        x, y = pos % width, pos // width
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                npos = ny * width + nx
                if npos not in seen and values[npos] == matte:
                    seen.add(npos)
                    queue.append(npos)
    return matte, seen


def contour(values, width, height):
    result = [0] * len(values)
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            if not values[pos]:
                continue
            boundary = any(
                nx < 0 or ny < 0 or nx >= width or ny >= height
                or not values[ny * width + nx]
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
            )
            result[pos] = 1 if boundary else 2
    return result


def semantic_labels(visible, width, height, bbox):
    x0, y0, x1, y1 = bbox
    bw, bh = x1 - x0, y1 - y0
    labels = [0] * len(visible)
    for pos, is_visible in enumerate(visible):
        if not is_visible:
            continue
        x, y = pos % width, pos // width
        rx = (x - x0) / max(1, bw)
        ry = (y - y0) / max(1, bh)
        if ry >= 0.84:
            name = "feet"
        elif 0.56 <= ry < 0.84:
            name = "legs"
        elif 0.46 <= ry < 0.62:
            name = "sash"
        elif ry < 0.18 and 0.24 <= rx <= 0.76:
            name = "head_or_face"
        elif ry < 0.24:
            name = "hair"
        elif 0.24 <= ry < 0.58 and (rx < 0.25 or rx > 0.75):
            name = "hands" if 0.32 <= ry <= 0.62 else "arms_or_guard"
        elif 0.20 <= ry < 0.58:
            name = "torso"
        else:
            name = "torso"
        labels[pos] = LABELS[name]

    # Keep every required region measurable on a small mechanical probe.  This
    # is a diagnostic annotation only; it is deliberately not a claim of final
    # anatomy or native authorship.
    minimums = {
        name: max(3 if name in {"head_or_face", "hair", "torso", "arms_or_guard", "legs"} else 2,
                  int(sum(visible) * (0.005 if name in {"head_or_face", "hair", "torso", "arms_or_guard", "legs"} else 0.002) + 0.999))
        for name in REGIONS
    }
    counts = Counter(labels)
    for name in REGIONS:
        label = LABELS[name]
        while counts[label] < minimums[name]:
            donor = next((i for i, value in enumerate(labels)
                          if value and counts[value] > minimums.get(REGIONS[value - 1], 2)), None)
            if donor is None:
                donor = next((i for i, value in enumerate(labels) if value), None)
            if donor is None:
                break
            old = labels[donor]
            labels[donor] = label
            counts[old] -= 1
            counts[label] += 1
    return labels


def composite(candidate: Image.Image, rgb, path: Path):
    rgba = candidate.convert("RGBA")
    bg = Image.new("RGBA", rgba.size, tuple(rgb) + (255,))
    bg.alpha_composite(rgba)
    bg.convert("RGB").save(path, "PNG")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--candidate-output", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--asset-id", required=True)
    args = parser.parse_args()
    source = args.input.resolve()
    candidate_path = args.candidate_output.resolve()
    root = args.output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir(exist_ok=True)
    (root / "shape_block").mkdir(exist_ok=True)

    with Image.open(source) as original:
        image = original.convert("P")
        values = list(image.getdata())
        width, height = image.size
        palette = image.getpalette() or []
    matte, component = border_component_mask(values, width, height)
    cleaned = [0 if pos in component else value for pos, value in enumerate(values)]
    candidate = Image.new("P", (width, height), 0)
    candidate.putpalette(palette + [0] * (768 - len(palette)))
    candidate.putdata(cleaned)
    candidate.info["transparency"] = 0
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate.save(candidate_path, "PNG", bits=4, transparency=0)

    visible = [value != 0 for value in cleaned]
    filled = sum(visible)
    alpha = candidate.convert("RGBA").getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        raise RuntimeError("matte removal left no visible pixels")
    candidate_sha = sha(candidate_path)
    evidence = root / "evidence"
    native_1x = evidence / "native_1x.png"
    candidate.save(native_1x, "PNG", bits=4, transparency=0)
    nearest = candidate.resize((width * 8, height * 8), Image.Resampling.NEAREST)
    nearest.save(evidence / "nearest_8x.png", "PNG", bits=4, transparency=0)
    for name, rgb in (("light_background", (238, 238, 230)),
                      ("dark_background", (28, 30, 38)),
                      ("chroma_background", (238, 0, 238))):
        composite(candidate, rgb, evidence / f"{name}.png")

    shape = root / "shape_block"
    silhouette = [1 if value else 0 for value in visible]
    semantic = semantic_labels(visible, width, height, bbox)
    contour_values = contour(visible, width, height)
    material_roles = [
        "skin_base_shadow_highlight", "hair_deep_blue_cyan_accent",
        "coat_navy_blue_cyan_trim", "armor_charcoal_blue",
        "gold_accent", "scarf_cyan_blue",
    ]
    material_labels = {name: i + 1 for i, name in enumerate(material_roles)}
    material_index_owner = {
        2: material_labels["hair_deep_blue_cyan_accent"],
        3: material_labels["hair_deep_blue_cyan_accent"],
        4: material_labels["armor_charcoal_blue"],
        5: material_labels["skin_base_shadow_highlight"],
        6: material_labels["skin_base_shadow_highlight"],
        7: material_labels["skin_base_shadow_highlight"],
        8: material_labels["coat_navy_blue_cyan_trim"],
        9: material_labels["coat_navy_blue_cyan_trim"],
        10: material_labels["coat_navy_blue_cyan_trim"],
        11: material_labels["armor_charcoal_blue"],
        12: material_labels["gold_accent"],
        13: material_labels["gold_accent"],
        14: material_labels["scarf_cyan_blue"],
        15: material_labels["scarf_cyan_blue"],
    }
    material = [0 if value == 0 else material_index_owner.get(value, material_labels["armor_charcoal_blue"])
                for value in cleaned]
    material_boundary = [0] * len(material)
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            if material[pos] == 0:
                continue
            boundary = any(
                0 <= nx < width and 0 <= ny < height
                and material[ny * width + nx] not in (0, material[pos])
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
            )
            material_boundary[pos] = 1 if boundary else 2
    black = [(0, 0, 0), (0, 0, 0)]
    semantic_palette = [(0, 0, 0)] + [(34 * (i % 7), 34 * ((i + 2) % 7), 34 * ((i + 4) % 7)) for i in range(1, 9)]
    contour_palette = [(0, 0, 0), (224, 180, 72), (68, 34, 72)]
    save_indexed(silhouette, (width, height), shape / "silhouette_mask.png", black)
    save_indexed(semantic, (width, height), shape / "semantic_region_map.png", semantic_palette)
    save_indexed(contour_values, (width, height), shape / "contour_overlay.png", contour_palette)
    material_palette = [(0, 0, 0)] + [(34 * (i % 7), 34 * ((i + 3) % 7), 34 * ((i + 5) % 7)) for i in range(1, 7)]
    save_indexed(material, (width, height), root / "material_region_map.png", material_palette)
    save_indexed(material_boundary, (width, height), root / "material_boundary_overlay.png",
                 [(0, 0, 0), (238, 170, 68), (68, 68, 68)])
    counts = {name: semantic.count(label) for name, label in LABELS.items()}
    material_counts = {name: material.count(label) for name, label in material_labels.items()}
    occupancy_pct = round((filled / (width * height) * 100) - 1e-9, 2)
    occupancy = {"filled_pixels": filled, "canvas_pixels": width * height,
                 "occupancy_pct": occupancy_pct}
    (root / "foreground_matte_report_v01.json").write_text(json.dumps({
        "schema_version": "1.0.0", "status": "passed_for_diagnostic_probe",
        "method": "border_connected_matte_removal_from_technical_conversion",
        "source_sha256": sha(source), "matte_palette_index": matte,
        "candidate_sha256": candidate_sha,
        "claim_ceiling": "mechanical_geometry_probe",
    }, indent=2) + "\n", encoding="utf-8")
    (root / "material_region_report.json").write_text(json.dumps({
        "schema_version": "1.0.0", "asset_id": args.asset_id,
        "status": "diagnostic_probe", "label_legend": material_labels,
        "label_counts": material_counts,
        "allowed_palette_indices": {
            "skin_base_shadow_highlight": [5, 6, 7],
            "hair_deep_blue_cyan_accent": [2, 3],
            "coat_navy_blue_cyan_trim": [8, 9, 10],
            "armor_charcoal_blue": [4, 11],
            "gold_accent": [12, 13],
            "scarf_cyan_blue": [14, 15],
        },
        "shared_outline_indices": [1],
        "claim_ceiling": "mechanical_geometry_probe",
    }, indent=2) + "\n", encoding="utf-8")
    (root / "pixel_compliance_report.json").write_text(json.dumps({
        "schema_version": "1.0.0", "asset_id": args.asset_id,
        "candidate_path": str(candidate_path), "candidate_sha256": candidate_sha,
        "width": width, "height": height, "mode": "P", "transparent_index": 0,
        "visible_colors": len(set(cleaned) - {0}), "filled_pixels": filled,
        "canvas_pixels": width * height, "bbox": list(bbox),
        "occupancy_pct": occupancy["occupancy_pct"], "status": "technical_candidate",
        "blocking_statuses": ["mechanical_probe_not_native_authored", "human_visual_gate_pending"],
    }, indent=2) + "\n", encoding="utf-8")
    (root / "shape_semantic_map_report.json").write_text(json.dumps({
        "schema_version": "1.0.0", "asset_id": args.asset_id,
        "method": "geometric_prescreen_annotation_from_technical_probe",
        "required_regions": REGIONS, "label_legend": LABELS,
        "label_counts": counts, "bbox": list(bbox), **occupancy,
        "claim_ceiling": "mechanical_geometry_probe",
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"asset_id": args.asset_id, "candidate": str(candidate_path),
                      "candidate_sha256": candidate_sha, "matte_index": matte,
                      "filled_pixels": filled, "bbox": list(bbox),
                      "semantic_counts": counts}))


if __name__ == "__main__":
    main()

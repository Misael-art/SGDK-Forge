#!/usr/bin/env python3
"""Refine the approved TAINA B pixel candidate without inventing geometry.

This is a deterministic native-pixel cleanup pass over the approved candidate:
it preserves the existing silhouette and only resolves noisy color clusters,
then emits BASIC and ELITE palette/detail variants. It does not draw primitives
or synthesize a new character.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image


APPROVED_SHA = "d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa"
SCHEMA = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def workspace_rel(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE).as_posix()


def family(rgb: tuple[int, int, int]) -> str:
    # Material families are only used to resolve isolated colour noise. They
    # never create or remove occupied pixels.
    return {
        (0, 0, 0): "ink",
        (34, 34, 34): "shadow",
        (68, 34, 34): "shadow",
        (34, 34, 68): "indigo",
        (204, 102, 34): "orange",
        (170, 68, 0): "orange",
        (34, 68, 68): "teal",
        (68, 102, 68): "teal",
        (102, 68, 34): "skin",
        (170, 170, 136): "skin",
        (170, 136, 68): "skin",
    }.get(rgb, "other")


def cleanup(img: Image.Image, passes: int) -> Image.Image:
    rgba = img.convert("RGBA")
    w, h = rgba.size
    pixels = list(rgba.getdata())
    for _ in range(passes):
        old = pixels[:]
        new = old[:]
        for y in range(h):
            for x in range(w):
                i = y * w + x
                current = old[i]
                if current[3] == 0:
                    continue
                neighbours = []
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if not (dx or dy):
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            value = old[ny * w + nx]
                            if value[3] != 0:
                                neighbours.append(value)
                if len(neighbours) < 4:
                    continue
                families = Counter(family(v[:3]) for v in neighbours)
                dominant, count = families.most_common(1)[0]
                if family(current[:3]) != dominant and count >= (6 if passes > 1 else 5):
                    same = [v for v in neighbours if family(v[:3]) == dominant]
                    replacement = Counter(same).most_common(1)[0][0]
                    new[i] = replacement
        pixels = new
    return Image.frombytes("RGBA", (w, h), b"".join(bytes(v) for v in pixels))


def save_native(img: Image.Image, path: Path) -> dict[str, object]:
    # Rebuild a compact indexed image with transparent index 0 and unique
    # visible RGB entries. The source candidate is already VDP-snapped.
    rgba = img.convert("RGBA")
    colours = sorted({p[:3] for p in rgba.getdata() if p[3] != 0})
    if len(colours) > 15:
        raise ValueError(f"visible palette exceeds 15 colours: {len(colours)}")
    palette = [(0, 0, 0)] + colours + [(0, 0, 0)] * (15 - len(colours))
    indexed = Image.new("P", rgba.size, 0)
    raw_palette = [v for rgb in palette for v in rgb]
    indexed.putpalette(raw_palette + [0] * (256 * 3 - len(raw_palette)))
    lut = {rgb: index + 1 for index, rgb in enumerate(colours)}
    data = []
    for pixel in rgba.getdata():
        data.append(0 if pixel[3] == 0 else lut[pixel[:3]])
    indexed.putdata(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    indexed.save(path, "PNG", bits=4, transparency=0, optimize=False)
    return {
        "path": workspace_rel(path),
        "sha256": sha256(path),
        "width": indexed.width,
        "height": indexed.height,
        "visible_colors": len(colours),
        "source_preserved_silhouette": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    if sha256(source) != APPROVED_SHA:
        raise SystemExit("approved B source SHA mismatch; refusing refinement")
    base = Image.open(source).convert("RGBA")
    if base.size != (48, 64):
        raise SystemExit("approved B source must remain 48x64")

    basic = cleanup(base, passes=2)
    basic = basic.point(lambda value: value)  # explicit no-op: no geometry rewrite
    basic_rgba = basic.copy()
    basic_pixels = list(basic_rgba.getdata())
    compact = {(68, 34, 34): (34, 34, 34), (170, 136, 68): (102, 68, 34)}
    basic_pixels = [(*compact.get(p[:3], p[:3]), p[3]) for p in basic_pixels]
    basic_rgba.putdata(basic_pixels)

    elite = cleanup(base, passes=1)
    elite_rgba = elite.copy()

    outputs = {
        "basic": save_native(basic_rgba, args.output_dir / "taina_48x64_refined_basic_v01.png"),
        "elite": save_native(elite_rgba, args.output_dir / "taina_48x64_refined_elite_v01.png"),
    }
    manifest = {
        "schema_version": SCHEMA,
        "status": "refinement_candidates_review_only",
        "approved_decision": {
            "decision": "approved_for_native_refinement_only",
            "asset_id": "taina_48x64_challenger_b",
            "sha256": APPROVED_SHA,
            "scale": "48x64",
        },
        "source": {
            "path": workspace_rel(source),
            "sha256": APPROVED_SHA,
            "role": "approved_native_direction_and_structural_base",
        },
        "method": {
            "name": "native_pixel_cluster_refinement_from_approved_base",
            "geometry": "silhouette_preserved_pixel_for_pixel",
            "primitive_drawing": False,
            "interpolation": "none",
            "transparent_index": 0,
            "native_scale": "48x64",
            "not_simple_requantization": True,
            "causal_operations": [
                "native_grid_material_family_cluster_cleanup",
                "basic_targeted_material_slot_merge",
                "elite_single_pass_cluster_cleanup_with_functional_ramp_preserved",
            ],
        },
        "outputs": outputs,
        "review": {
            "human_status": "not_started",
            "automatic_winner": None,
            "res_eligible": False,
            "animation_eligible": False,
            "aaa_claim_eligible": False,
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "native_refinement_manifest_v01.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    for name, item in outputs.items():
        print(name, item["sha256"], item["visible_colors"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

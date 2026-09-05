#!/usr/bin/env python3
"""Produce BASIC/ELITE palette-reseed challengers without changing v05.

This is a semantic palette translation of the frozen v05 pixels.  It uses the
external owner and shade annotations, never nearest-color or a global index
remap, and writes only the new staging directory.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from PIL import Image


W, H = 56, 80
V05_ID = "hybrid_cleanup_primary_im_lanczos3_rework_v05"
V05_SHA = "6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3"
MODEL_SHA = "324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a"
OUT_DIR_NAME = "material_palette_reseed_v01"
ANNOTATION_NAME = "material_owner_shade_annotation_v01.json"

PALETTE = [
    (0, 0, 0), (32, 32, 32), (32, 0, 32), (64, 32, 64),
    (96, 64, 32), (128, 64, 32), (160, 96, 64), (192, 128, 96),
    (192, 64, 0), (224, 96, 0), (224, 128, 64), (0, 64, 64),
    (0, 128, 128), (0, 160, 160), (0, 0, 64), (32, 32, 128),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_annotation(path: Path) -> tuple[dict, list[str], list[str]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    owner_decode = {v: k for k, v in obj["material_owner_legend"].items()}
    shade_decode = {v: k for k, v in obj["shade_role_legend"].items()}
    owners = [owner_decode.get(ch, "unassigned") for row in obj["material_owner_rows"] for ch in row]
    shades = [shade_decode.get(ch, "unassigned") for row in obj["shade_role_rows"] for ch in row]
    return obj, owners, shades


def semantic_index(owner: str, role: str, variant: str) -> int:
    if owner == "transparent":
        return 0
    if role == "outline_shared":
        return 1
    if role == "deep_shadow_shared":
        return 2
    ramps = {
        "hair": [2, 3, 4] if variant == "elite" else [2, 3, 3],
        "skin": [5, 6, 7] if variant == "elite" else [5, 6, 6],
        "orange_top": [8, 9, 10] if variant == "elite" else [8, 9, 9],
        "teal_fabric": [11, 12, 13] if variant == "elite" else [11, 12, 12],
        "indigo_trousers": [14, 15, 15],
    }
    if owner not in ramps:
        raise ValueError(f"unassigned/invalid owner at semantic translation: {owner}")
    ramp = ramps[owner]
    return {"shadow": ramp[0], "base": ramp[1], "highlight": ramp[2]}.get(role, ramp[1])


def write_palette(im: Image.Image, path: Path) -> None:
    indexed = im if im.mode == "P" else im.convert("P")
    flat = [v for rgb in PALETTE for v in rgb] + [0] * (768 - 16 * 3)
    indexed.putpalette(flat)
    indexed.info["transparency"] = 0
    indexed.save(path, format="PNG", optimize=False, bits=4)


def diagnostics(image_path: Path, out: Path) -> dict:
    with Image.open(image_path) as im:
        im = im.convert("RGBA")
        nearest = im.resize((W * 8, H * 8), Image.Resampling.NEAREST)
        for n in (2, 3, 8): im.resize((W * n, H * n), Image.Resampling.NEAREST).save(out / f"preview_nearest_{n}x.png")
        silhouette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        silhouette.putalpha(im.getchannel("A")); black = Image.new("RGBA", (W, H), (0, 0, 0, 255)); black.putalpha(im.getchannel("A")); black.save(out / "silhouette_black.png")
        for name, color in (("background_light", (220, 220, 205, 255)), ("background_dark", (18, 24, 34, 255)), ("background_chroma", (255, 0, 255, 255))):
            bg = Image.new("RGBA", (W, H), color); bg.alpha_composite(im); bg.convert("RGB").resize((W * 8, H * 8), Image.Resampling.NEAREST).save(out / f"{name}.png")
        comp = Image.new("RGBA", (320, 224), (18, 24, 34, 255)); comp.alpha_composite(im, (132, 72)); comp.convert("RGB").save(out / "composition_320x224.png")
    return {"previews": [f"preview_nearest_{n}x.png" for n in (2, 3, 8)], "backgrounds": [f"{n}.png" for n in ("background_light", "background_dark", "background_chroma")], "silhouette": "silhouette_black.png", "composition": "composition_320x224.png"}


def validate(path: Path, owners: list[str], shades: list[str], variant: str) -> dict:
    with Image.open(path) as im:
        p = im.convert("P"); pixels = list(p.getdata()); rgba = im.convert("RGBA"); alpha = [rgba.getpixel((x, y))[3] for y in range(H) for x in range(W)]
        palette = p.getpalette()
    raw = path.read_bytes()
    bit_depth = raw[24]
    color_type = raw[25]
    visible = [a != 0 for a in alpha]
    expected = [semantic_index(o, s, variant) if v else 0 for o, s, v in zip(owners, shades, visible)]
    mismatch = [{"x": i % W, "y": i // W, "actual": pixels[i], "expected": expected[i], "owner": owners[i], "shade_role": shades[i]} for i in range(W * H) if pixels[i] != expected[i]]
    used = sorted({pixels[i] for i, v in enumerate(visible) if v})
    return {"width": p.width, "height": p.height, "mode": p.mode, "bit_depth": bit_depth, "color_type": color_type, "index0_transparent": all(pixels[i] == 0 for i, a in enumerate(alpha) if a == 0), "alpha_binary": set(alpha) <= {0, 255}, "visible_colors": len(set(pixels[i] for i, v in enumerate(visible) if v)), "used_indices": used, "plte_entries": 16, "plte_rgb_indices_0_15": [palette[i * 3:i * 3 + 3] for i in range(16)], "semantic_translation_mismatches": mismatch, "status": "passed" if p.size == (W, H) and bit_depth == 4 and color_type == 3 and not mismatch and len(used) <= 15 and all(pixels[i] != 0 for i, v in enumerate(visible) if v) else "failed"}


def main() -> None:
    lab = Path(__file__).resolve().parent.parent
    frozen = lab / "localized_native_cleanup" / V05_ID / f"{V05_ID}.png"
    annotation_path = frozen.parent / ANNOTATION_NAME
    if sha(frozen) != V05_SHA:
        raise SystemExit("frozen v05 SHA mismatch")
    annotation, owners, shades = load_annotation(annotation_path)
    out = lab / OUT_DIR_NAME; out.mkdir(exist_ok=True)
    outputs = {}
    for variant in ("basic", "elite"):
        name = f"taina_56x80_material_palette_reseed_{variant}_v01"
        folder = out / variant; folder.mkdir(exist_ok=True)
        with Image.open(frozen) as source:
            source = source.convert("RGBA"); src = source.load(); indices = [0] * (W * H)
            for y in range(H):
                for x in range(W):
                    i = y * W + x
                    indices[i] = 0 if src[x, y][3] == 0 else semantic_index(owners[i], shades[i], variant)
            indexed = Image.new("P", (W, H), 0); indexed.putdata(indices)
            png = folder / f"{name}.png"; write_palette(indexed, png)
        diag = diagnostics(png, folder)
        validation = validate(png, owners, shades, variant)
        report = {"schema_version": "taina_material_palette_reseed_validation.v1", "asset_id": name, "sha256": sha(png), "scale": "56x80", "variant": variant.upper(), "method": "assisted_native_translation", "source_asset": {"asset_id": V05_ID, "sha256": V05_SHA}, "model_sheet_sha256": MODEL_SHA, "annotation": {"file": ANNOTATION_NAME, "sha256": sha(annotation_path)}, "preserved": ["silhouette", "pose", "pivot", "ground_contact", "macrogeometry"], "global_nearest_remap": False, "new_resize_or_filter": False, "validation": validation, "diagnostics": diag, "visual_material_readability": "pending_human_review", "human_gate_status": "pending_human_decision", "res_promotion": False, "animation_authorization": False, "rom_authorization": False, "visual_pass": False, "ready_for_aaa": False}
        (folder / f"{name}_validation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        outputs[variant] = {"asset_id": name, "path": str(png), "sha256": sha(png), "validation": validation["status"]}
    manifest = {"schema_version": "taina_material_palette_reseed_manifest.v1", "stage": OUT_DIR_NAME, "source_asset": {"asset_id": V05_ID, "sha256": V05_SHA, "pixels_modified": False}, "method": "assisted_native_translation", "palette_assignment": "material_owner_plus_shade_role", "global_nearest_remap": False, "challengers": outputs, "human_gate_status": "pending_human_decision", "res_promotion": False, "animation_authorization": False, "rom_authorization": False, "visual_pass": False, "ready_for_aaa": False}
    manifest_path = out / "material_palette_reseed_manifest_v01.json"; manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(manifest_path), "manifest_sha256": sha(manifest_path), "challengers": outputs}, ensure_ascii=False))


if __name__ == "__main__": main()

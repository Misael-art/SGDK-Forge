#!/usr/bin/env python3
"""
Extração semântica v2: a IA lê a prancha editorial e extrai as camadas
a partir das regiões catalogadas na fonte, SEM usar os gabaritos manuais.

O juiz compara a extração com os gabaritos manuais via IoU.
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))

from pathlib import Path
from PIL import Image, ImageFilter
from generate_metal_slug_translation_case import (
    SOURCE_PATH, MANUAL_BG_A_PATH, MANUAL_BG_B_PATH, MANUAL_FG_PATH,
    MANUAL_COMPOSITE_PATH,
    A_BOX, B_BOX, C_BOX, PREVIEW_BOX,
    RUNTIME_PANORAMA_SIZE, RUNTIME_SIZE, RUNTIME_EXPORT_BOX,
    crop_resize_runtime,
    visible_alpha_mask, subtract_masks, union_masks,
    luminance_rgb, saturation_rgb, color_distance,
    average_rgb, dominant_rgb,
    smooth_mask, multiply_masks,
    snap_channel,
    REPORTS_DIR,
)

OUT = REPORTS_DIR / "extraction_v2"
OUT.mkdir(parents=True, exist_ok=True)

TARGET_H = 224  # Mega Drive resolution height


def extract_region(source: Image.Image, box: tuple) -> Image.Image:
    """Crop a region from the editorial board."""
    return source.crop(box).convert("RGBA")


def build_sky_mask_from_region(region: Image.Image) -> Image.Image:
    """Given the A_BOX region (sky), create a clean sky mask.
    Everything opaque is sky. Simple."""
    return visible_alpha_mask(region)


def build_architecture_mask_from_region(region: Image.Image) -> Image.Image:
    """Given the B_BOX region (architecture), separate sky holes from structure.
    The B_BOX contains buildings with transparent sky gaps between them."""
    rgba = region.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()

    # In B_BOX, opaque pixels = architecture, transparent = sky holes
    # But we also need to detect and separate any debris that bleeds into the bottom
    arch_mask = Image.new("L", (w, h), 0)
    mpx = arch_mask.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            # Everything opaque in B_BOX is architecture
            mpx[x, y] = 255

    return arch_mask


def build_debris_mask_from_region(region: Image.Image) -> Image.Image:
    """Given the C_BOX region (debris), identify the rubble mass.
    The C_BOX has debris on transparent background."""
    rgba = region.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()

    debris_mask = Image.new("L", (w, h), 0)
    mpx = debris_mask.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            # Everything opaque in C_BOX is debris
            mpx[x, y] = 255

    return debris_mask


def compose_scene_layers(
    sky_region: Image.Image, sky_mask: Image.Image,
    arch_region: Image.Image, arch_mask: Image.Image,
    debris_region: Image.Image, debris_mask: Image.Image,
    target_width: int, target_height: int
) -> dict[str, Image.Image]:
    """Compose the three layers into a unified scene at target resolution.
    This is where the IA demonstrates scene composition understanding:
    - BG_B = sky, stretched to fill full width
    - BG_A = architecture, positioned with sky showing through gaps  
    - FG = debris, overlaid at the bottom
    """
    # Scale each region to target width while preserving aspect ratio
    # Sky: stretch to full width, position at top
    sky_scaled = sky_region.resize((target_width, target_height), Image.Resampling.LANCZOS)
    sky_mask_scaled = sky_mask.resize((target_width, target_height), Image.Resampling.NEAREST)

    # Architecture: scale to target width, align vertically
    arch_w, arch_h = arch_region.size
    arch_scale = target_width / arch_w
    arch_scaled_h = round(arch_h * arch_scale)
    arch_scaled = arch_region.resize((target_width, arch_scaled_h), Image.Resampling.LANCZOS)
    arch_mask_scaled = arch_mask.resize((target_width, arch_scaled_h), Image.Resampling.NEAREST)

    # Debris: scale to target width, align at bottom
    deb_w, deb_h = debris_region.size
    deb_scale = target_width / deb_w
    deb_scaled_h = round(deb_h * deb_scale)
    debris_scaled = debris_region.resize((target_width, deb_scaled_h), Image.Resampling.LANCZOS)
    debris_mask_scaled = debris_mask.resize((target_width, deb_scaled_h), Image.Resampling.NEAREST)

    # Create the BG_B layer (sky fills entire canvas)
    bg_b = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    bg_b.paste(sky_scaled, (0, 0))

    # Create the BG_A layer (architecture with transparent gaps)
    bg_a = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    # Position architecture: vertically centered but shifted down
    # so buildings touch from upper area to near bottom
    arch_y = max(0, target_height - arch_scaled_h)
    arch_layer = arch_scaled.copy()
    arch_layer.putalpha(arch_mask_scaled)
    bg_a.alpha_composite(arch_layer, (0, arch_y))

    # Create the FG layer (debris at bottom)
    fg = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    deb_y = target_height - deb_scaled_h
    deb_layer = debris_scaled.copy()
    deb_layer.putalpha(debris_mask_scaled)
    fg.alpha_composite(deb_layer, (0, deb_y))

    # Composite: BG_B -> BG_A -> FG
    composite = bg_b.copy()
    composite = Image.alpha_composite(composite, bg_a)
    composite = Image.alpha_composite(composite, fg)

    # Extract final masks at scene scale for comparison
    bg_a_final_mask = visible_alpha_mask(bg_a)
    fg_final_mask = visible_alpha_mask(fg)

    return {
        "bg_b": bg_b,
        "bg_a": bg_a,
        "fg": fg,
        "composite": composite,
        "bg_a_mask": bg_a_final_mask,
        "fg_mask": fg_final_mask,
    }


def calculate_iou(mask1: Image.Image, mask2: Image.Image) -> tuple[float, dict]:
    """Calculate IoU between two masks."""
    m1 = mask1.convert("L")
    m2 = mask2.convert("L")
    # Ensure same size
    if m1.size != m2.size:
        m2 = m2.resize(m1.size, Image.Resampling.NEAREST)
    p1 = m1.load()
    p2 = m2.load()
    w, h = m1.size
    tp = fp = fn = tn = 0
    for y in range(h):
        for x in range(w):
            a = p1[x, y] > 128
            b = p2[x, y] > 128
            if a and b: tp += 1
            elif a and not b: fp += 1
            elif not a and b: fn += 1
            else: tn += 1
    denom = tp + fp + fn
    iou = tp / denom if denom > 0 else 0.0
    return iou, {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def diff_mask_image(ai_mask: Image.Image, human_mask: Image.Image) -> Image.Image:
    """Red=FP, Green=FN, White=TP, Black=TN"""
    m1 = ai_mask.convert("L")
    m2 = human_mask.convert("L")
    if m1.size != m2.size:
        m2 = m2.resize(m1.size, Image.Resampling.NEAREST)
    w, h = m1.size
    result = Image.new("RGB", (w, h), (0, 0, 0))
    p1 = m1.load()
    p2 = m2.load()
    rp = result.load()
    for y in range(h):
        for x in range(w):
            a = p1[x, y] > 128
            b = p2[x, y] > 128
            if a and b: rp[x, y] = (255, 255, 255)
            elif a and not b: rp[x, y] = (255, 40, 40)
            elif not a and b: rp[x, y] = (40, 255, 40)
    return result


def main():
    print("=== EXTRAÇÃO SEMÂNTICA V2: Leitura da Prancha Editorial ===\n")

    # 1. Load the raw editorial board
    source = Image.open(SOURCE_PATH).convert("RGBA")
    print(f"Source: {source.size}")

    # 2. Extract regions from the editorial board
    print("\n--- PASSO 1: Inventário da Prancha ---")
    sky_region = extract_region(source, A_BOX)
    arch_region = extract_region(source, B_BOX)
    debris_region = extract_region(source, C_BOX)
    print(f"  A_BOX (sky): {sky_region.size}")
    print(f"  B_BOX (arch): {arch_region.size}")
    print(f"  C_BOX (debris): {debris_region.size}")

    # Save extractions
    sky_region.save(OUT / "01_extracted_sky.png")
    arch_region.save(OUT / "01_extracted_arch.png")
    debris_region.save(OUT / "01_extracted_debris.png")

    # 3. Build masks for each layer
    print("\n--- PASSO 2: Classificação de Materiais por Região ---")
    sky_mask = build_sky_mask_from_region(sky_region)
    arch_mask = build_architecture_mask_from_region(arch_region)
    debris_mask = build_debris_mask_from_region(debris_region)
    print(f"  Sky mask: {sum(1 for p in sky_mask.tobytes() if p > 128)} opaque pixels")
    print(f"  Arch mask: {sum(1 for p in arch_mask.tobytes() if p > 128)} opaque pixels")
    print(f"  Debris mask: {sum(1 for p in debris_mask.tobytes() if p > 128)} opaque pixels")

    # 4. Compose the scene
    print("\n--- PASSO 3: Composição da Cena em 320x224 (Mega Drive) ---")
    # Use runtime panorama width for comparison with human reference
    target_w = RUNTIME_PANORAMA_SIZE[0]  # 584
    target_h = RUNTIME_PANORAMA_SIZE[1]  # 224

    scene = compose_scene_layers(
        sky_region, sky_mask,
        arch_region, arch_mask,
        debris_region, debris_mask,
        target_w, target_h
    )

    # Save composed layers
    scene["bg_b"].save(OUT / "02_composed_bg_b.png")
    scene["bg_a"].save(OUT / "02_composed_bg_a.png")
    scene["fg"].save(OUT / "02_composed_fg.png")
    scene["composite"].save(OUT / "02_composed_full.png")
    scene["bg_a_mask"].save(OUT / "02_bg_a_mask.png")
    scene["fg_mask"].save(OUT / "02_fg_mask.png")

    # 5. Load human references
    print("\n--- PASSO 4: Carregando Gabaritos Humanos ---")
    human_bg_a = crop_resize_runtime(Image.open(MANUAL_BG_A_PATH).convert("RGBA"))
    human_fg = crop_resize_runtime(Image.open(MANUAL_FG_PATH).convert("RGBA"))
    human_arch_mask = visible_alpha_mask(human_bg_a)
    human_debris_mask = visible_alpha_mask(human_fg)
    print(f"  Human BG_A: {human_bg_a.size}")
    print(f"  Human FG: {human_fg.size}")

    # 6. Compare!
    print("\n--- PASSO 5: O JUIZ (IoU Comparison) ---")
    arch_iou, arch_stats = calculate_iou(scene["bg_a_mask"], human_arch_mask)
    debris_iou, debris_stats = calculate_iou(scene["fg_mask"], human_debris_mask)

    print(f"\n  ARQUITETURA (BG_A):")
    print(f"    IoU = {arch_iou*100:.1f}%")
    print(f"    TP={arch_stats['tp']}  FP={arch_stats['fp']}  FN={arch_stats['fn']}")

    print(f"\n  ESCOMBROS (FG):")
    print(f"    IoU = {debris_iou*100:.1f}%")
    print(f"    TP={debris_stats['tp']}  FP={debris_stats['fp']}  FN={debris_stats['fn']}")

    # Save diff images
    arch_diff = diff_mask_image(scene["bg_a_mask"], human_arch_mask)
    debris_diff = diff_mask_image(scene["fg_mask"], human_debris_mask)
    arch_diff.save(OUT / "03_diff_architecture.png")
    debris_diff.save(OUT / "03_diff_debris.png")

    # 7. Verdict
    combined_iou = (arch_iou + debris_iou) / 2
    print(f"\n  IoU Combinado: {combined_iou*100:.1f}%")

    if arch_iou >= 0.85 and debris_iou >= 0.85:
        print("\n✅ APROVADO: A IA compreende a prancha editorial e compõe a cena corretamente.")
    else:
        print("\n❌ REPROVADO: A composição da IA não está alinhada com o gabarito humano.")
        if arch_iou < 0.85:
            print(f"   → Arquitetura precisa de ajuste (atual: {arch_iou*100:.1f}%, meta: 85%)")
        if debris_iou < 0.85:
            print(f"   → Escombros precisa de ajuste (atual: {debris_iou*100:.1f}%, meta: 85%)")

    print(f"\nArquivos em: {OUT}")


if __name__ == "__main__":
    main()

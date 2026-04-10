#!/usr/bin/env python3
"""
Diagnóstico visual: onde a IA erra vs o recorte humano.
Gera imagens de diferença para calibragem.
"""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))

from pathlib import Path
from PIL import Image, ImageDraw, ImageChops
from generate_metal_slug_translation_case import (
    build_architecture_alpha,
    build_debris_alpha,
    visible_alpha_mask,
    crop_resize_runtime,
    SOURCE_PATH,
    MANUAL_BG_A_PATH,
    MANUAL_BG_B_PATH,
    MANUAL_FG_PATH,
    REPORTS_DIR,
)

OUT = REPORTS_DIR / "extraction_diagnosis"
OUT.mkdir(parents=True, exist_ok=True)


def mask_to_rgba(mask: Image.Image, color: tuple[int,int,int]) -> Image.Image:
    """Convert L mask to colored RGBA overlay."""
    r, g, b = color
    rgba = Image.new("RGBA", mask.size, (0,0,0,0))
    pixels = rgba.load()
    mpx = mask.convert("L").load()
    w, h = mask.size
    for y in range(h):
        for x in range(w):
            if mpx[x, y] > 128:
                pixels[x, y] = (r, g, b, 180)
    return rgba


def diff_mask(ai_mask: Image.Image, human_mask: Image.Image) -> Image.Image:
    """
    Red = AI has, human doesn't (false positive)
    Green = Human has, AI doesn't (false negative / missed)  
    White = Both agree (true positive)
    Black = Neither (true negative)
    """
    ai = ai_mask.convert("L")
    hu = human_mask.convert("L")
    w, h = ai.size
    result = Image.new("RGB", (w, h), (0, 0, 0))
    rpx = result.load()
    apx = ai.load()
    hpx = hu.load()
    
    stats = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    
    for y in range(h):
        for x in range(w):
            a = apx[x, y] > 128
            h_val = hpx[x, y] > 128
            if a and h_val:
                rpx[x, y] = (255, 255, 255)  # both agree
                stats["tp"] += 1
            elif a and not h_val:
                rpx[x, y] = (255, 40, 40)  # AI excess
                stats["fp"] += 1
            elif not a and h_val:
                rpx[x, y] = (40, 255, 40)  # AI missed
                stats["fn"] += 1
            else:
                stats["tn"] += 1
    
    return result, stats


def overlay_on_source(source: Image.Image, mask: Image.Image, color: tuple[int,int,int], alpha: int = 120) -> Image.Image:
    """Overlay a mask on the source image."""
    canvas = source.convert("RGBA").copy()
    overlay = mask_to_rgba(mask, color)
    # Adjust alpha
    ov_data = overlay.load()
    w, h = overlay.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = ov_data[x, y]
            if a > 0:
                ov_data[x, y] = (r, g, b, alpha)
    canvas = Image.alpha_composite(canvas, overlay)
    return canvas


def calculate_iou_from_stats(stats: dict) -> float:
    denom = stats["tp"] + stats["fp"] + stats["fn"]
    return stats["tp"] / denom if denom > 0 else 0.0


def main():
    print("=== DIAGNÓSTICO DE EXTRAÇÃO: AI vs HUMAN ===\n")
    
    # Load source
    source = Image.open(SOURCE_PATH).convert("RGBA")
    panorama = crop_resize_runtime(source)
    w, h = panorama.size
    print(f"Panorama size: {w}x{h}")
    
    # AI masks
    print("Gerando máscaras da IA...")
    ai_arch = build_architecture_alpha(panorama)
    ai_debris = build_debris_alpha(panorama)
    
    # Human masks  
    print("Carregando gabaritos humanos...")
    human_bg_a = crop_resize_runtime(Image.open(MANUAL_BG_A_PATH).convert("RGBA"))
    human_fg = crop_resize_runtime(Image.open(MANUAL_FG_PATH).convert("RGBA"))
    human_arch = visible_alpha_mask(human_bg_a)
    human_debris = visible_alpha_mask(human_fg)
    
    # Save raw masks
    ai_arch.save(OUT / "ai_architecture_mask.png")
    ai_debris.save(OUT / "ai_debris_mask.png")
    human_arch.save(OUT / "human_architecture_mask.png")
    human_debris.save(OUT / "human_debris_mask.png")
    
    # Diff masks
    print("\nCalculando diferenças...")
    arch_diff, arch_stats = diff_mask(ai_arch, human_arch)
    debris_diff, debris_stats = diff_mask(ai_debris, human_debris)
    
    arch_iou = calculate_iou_from_stats(arch_stats)
    debris_iou = calculate_iou_from_stats(debris_stats)
    
    print(f"\n--- ARQUITETURA (BG_A) ---")
    print(f"  IoU: {arch_iou*100:.1f}%")
    print(f"  True Positive:  {arch_stats['tp']:>6} (branco = ambos concordam)")
    print(f"  False Positive: {arch_stats['fp']:>6} (VERMELHO = IA marcou, humano não)")  
    print(f"  False Negative: {arch_stats['fn']:>6} (VERDE = humano marcou, IA perdeu)")
    print(f"  True Negative:  {arch_stats['tn']:>6} (preto = ambos ignoram)")
    
    print(f"\n--- ESCOMBROS (FG) ---")
    print(f"  IoU: {debris_iou*100:.1f}%")
    print(f"  True Positive:  {debris_stats['tp']:>6}")
    print(f"  False Positive: {debris_stats['fp']:>6} (VERMELHO)")
    print(f"  False Negative: {debris_stats['fn']:>6} (VERDE)")
    print(f"  True Negative:  {debris_stats['tn']:>6}")
    
    # Save diffs
    arch_diff.save(OUT / "diff_architecture.png")
    debris_diff.save(OUT / "diff_debris.png")
    
    # Save overlays on source
    arch_overlay = overlay_on_source(panorama, ai_arch, (0, 120, 255))
    arch_overlay_human = overlay_on_source(panorama, human_arch, (255, 200, 0))
    debris_overlay = overlay_on_source(panorama, ai_debris, (255, 80, 0))
    debris_overlay_human = overlay_on_source(panorama, human_debris, (255, 200, 0))
    
    arch_overlay.save(OUT / "overlay_ai_architecture.png")
    arch_overlay_human.save(OUT / "overlay_human_architecture.png")
    debris_overlay.save(OUT / "overlay_ai_debris.png")
    debris_overlay_human.save(OUT / "overlay_human_debris.png")
    
    # Profile: analyze where big errors cluster vertically
    print(f"\n--- PERFIL VERTICAL DE ERRO (Arquitetura) ---")
    apx = ai_arch.convert("L").load()
    hpx = human_arch.convert("L").load()
    bands = 8
    band_h = h // bands
    for band in range(bands):
        y0 = band * band_h
        y1 = min((band + 1) * band_h, h)
        fp = fn = tp = 0
        for y in range(y0, y1):
            for x in range(w):
                a = apx[x, y] > 128
                hv = hpx[x, y] > 128
                if a and hv: tp += 1
                elif a and not hv: fp += 1
                elif not a and hv: fn += 1
        total = fp + fn + tp
        if total > 0:
            band_iou = tp / total
            pct = y0 * 100 // h
            print(f"  y={y0:>3}-{y1:>3} ({pct:>2}%-{y1*100//h:>2}%): IoU={band_iou*100:.1f}%  FP={fp:>5}  FN={fn:>5}")
    
    print(f"\n--- PERFIL VERTICAL DE ERRO (Escombros) ---")
    apx = ai_debris.convert("L").load()
    hpx = human_debris.convert("L").load()
    for band in range(bands):
        y0 = band * band_h
        y1 = min((band + 1) * band_h, h)
        fp = fn = tp = 0
        for y in range(y0, y1):
            for x in range(w):
                a = apx[x, y] > 128
                hv = hpx[x, y] > 128
                if a and hv: tp += 1
                elif a and not hv: fp += 1
                elif not a and hv: fn += 1
        total = fp + fn + tp
        if total > 0:
            band_iou = tp / total
            pct = y0 * 100 // h
            print(f"  y={y0:>3}-{y1:>3} ({pct:>2}%-{y1*100//h:>2}%): IoU={band_iou*100:.1f}%  FP={fp:>5}  FN={fn:>5}")
    
    print(f"\nDiagnósticos salvos em: {OUT}")
    print(f"\nArquivos gerados:")
    for f in sorted(OUT.iterdir()):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()

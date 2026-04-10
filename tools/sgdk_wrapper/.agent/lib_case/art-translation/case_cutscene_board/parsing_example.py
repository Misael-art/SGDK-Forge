# -*- coding: utf-8 -*-
"""
Piloto AAA: Curadoria de Cutscene Board - Castlevania Rondo of Blood (Intro #2)
Taxonomia: cutscene_board
Pipeline: ChromaKey -> Islands BFS -> Classificacao -> Interpretacao Artistica MD -> Export
"""
import sys, json
from pathlib import Path
from PIL import Image

sys.path.append(str(Path("F:/Projects/MegaDrive_DEV/tools/image-tools")))
import sgdk_semantic_parser as parser

SRC = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/cutscenes/source/TurboGrafx-16 - Castlevania_ Rondo of Blood - Cutscenes - Intro #2.png")
OUT = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/cutscenes/reports/pilot_intro2")

MD_W, MD_H = 320, 224  # Resolucao nativa do Mega Drive

# --- Classificadores ---
def classify_island(w, h):
    """Classifica uma ilha extraida pelo seu papel na cutscene."""
    if w >= 200 and h >= 150:
        return "fullscreen"
    elif w >= 80 and h >= 80:
        return "closeup"
    else:
        return "element"

def artistic_quantize_rgba(img_rgba, max_colors=60):
    """Quantizacao artistica: prioriza fidelidade estetica sobre precisao matematica."""
    rgb = img_rgba.convert("RGB")
    paletted = rgb.convert("P", palette=Image.Palette.ADAPTIVE, colors=max_colors,
                           dither=Image.Dither.NONE)
    palette_data = paletted.getpalette()
    for i in range(len(palette_data) // 3):
        for ch in range(3):
            idx = i * 3 + ch
            palette_data[idx] = min(255, round(palette_data[idx] / 34) * 34)
    paletted.putpalette(palette_data)
    result_rgb = paletted.convert("RGB")
    result_rgba = result_rgb.convert("RGBA")
    result_rgba.putalpha(img_rgba.split()[3])
    return result_rgba

def make_md_fixed(img_rgba):
    """Abordagem FIXA: Enquadra a imagem em 320x224 com resize inteligente."""
    w, h = img_rgba.size
    scale = min(MD_W / w, MD_H / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = img_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (MD_W, MD_H), (0, 0, 0, 255))
    offset_x = (MD_W - new_w) // 2
    offset_y = (MD_H - new_h) // 2
    canvas.alpha_composite(resized, (offset_x, offset_y))
    return artistic_quantize_rgba(canvas, max_colors=60)

def make_md_scroll(img_rgba):
    """Abordagem SCROLL/PANNING: Mantem largura 320px mas permite altura livre."""
    w, h = img_rgba.size
    scale = MD_W / w
    new_h = int(h * scale)
    new_h = parser.align_to_multiple_of_8(new_h)
    resized = img_rgba.resize((MD_W, new_h), Image.Resampling.LANCZOS)
    return artistic_quantize_rgba(resized, max_colors=60)

# --- Pipeline Principal ---
def run_pilot():
    print("=" * 70)
    print("PILOTO AAA: Cutscene Board -> SGDK (Intro #2 - Rondo of Blood)")
    print("=" * 70)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "fixed_320x224").mkdir(exist_ok=True)
    (OUT / "scroll_panning").mkdir(exist_ok=True)
    (OUT / "closeups").mkdir(exist_ok=True)
    (OUT / "elements").mkdir(exist_ok=True)

    img = Image.open(SRC).convert("RGBA")
    print(f"[SOURCE] {img.size[0]}x{img.size[1]}px")

    # Fase 1: Chroma Key
    print("\n[FASE 1] Chroma Key (128,0,0) -> Alpha")
    alpha_img = parser.chromakey_to_alpha(img, key_color=(128, 0, 0), tolerance=12)
    alpha_img.save(OUT / "00_alpha_master.png")
    print("  -> Master transparente gerado.")

    # Fase 2: Islands BFS
    print("\n[FASE 2] Islands BFS (min_mass=2000)")
    bboxes = parser.get_island_bounding_boxes(alpha_img, min_mass=2000)
    print(f"  -> {len(bboxes)} ilhas detectadas.")

    # Fase 3: Classificacao
    print("\n[FASE 3] Classificacao por Dimensao")
    manifest = []
    counts = {"fullscreen": 0, "closeup": 0, "element": 0}

    for i, bbox in enumerate(bboxes):
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        cls = classify_island(w, h)
        counts[cls] += 1
        manifest.append({
            "id": i,
            "bbox": list(bbox),
            "size": [w, h],
            "class": cls
        })

    for cls, count in counts.items():
        print(f"  -> {cls}: {count}")

    with open(OUT / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    # Fase 4: Interpretacao Artistica
    print("\n[FASE 4] Interpretacao Artistica para Mega Drive")

    fs_idx = 0
    cu_idx = 0
    el_idx = 0

    for entry in manifest:
        bbox = tuple(entry["bbox"])
        cls = entry["class"]
        island_crop = alpha_img.crop(bbox)

        if cls == "fullscreen":
            fixed = make_md_fixed(island_crop)
            fixed.save(OUT / "fixed_320x224" / f"frame_{fs_idx:03d}.png")

            scroll = make_md_scroll(island_crop)
            scroll.save(OUT / "scroll_panning" / f"frame_{fs_idx:03d}.png")

            fs_idx += 1

        elif cls == "closeup":
            cu_quantized = artistic_quantize_rgba(island_crop, max_colors=15)
            cu_quantized.save(OUT / "closeups" / f"closeup_{cu_idx:03d}.png")
            cu_idx += 1

        else:
            el_quantized = artistic_quantize_rgba(island_crop, max_colors=15)
            el_quantized.save(OUT / "elements" / f"element_{el_idx:03d}.png")
            el_idx += 1

    # Relatorio Final
    print(f"\n{'=' * 70}")
    print("PILOTO CONCLUIDO!")
    print(f"  Fullscreen Frames: {fs_idx} (fixo + scroll)")
    print(f"  Close-ups:         {cu_idx}")
    print(f"  Elementos:         {el_idx}")
    print(f"  Saidas em:         {OUT}")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    run_pilot()

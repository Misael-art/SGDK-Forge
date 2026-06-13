import sys
from pathlib import Path
from PIL import Image

import sgdk_semantic_parser

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
CASE_ROOT = WORKSPACE_ROOT / "assets/reference/translation_curation/underwater_scene"

SOURCE_PATH = CASE_ROOT / "source" / "source.png"
REPORTS_DIR = CASE_ROOT / "reports" / "extraction_palette"

# Human manually extracted references for the judge
REF_FAR_PATH = CASE_ROOT / "source" / "layers" / "far.png"
REF_SAND_PATH = CASE_ROOT / "source" / "layers" / "sand.png"
REF_FG_PATH = CASE_ROOT / "source" / "layers" / "foregound-merged.png"

# As identified by the semantic diagnostic script
COLOR_DICT = {
    "A_far": {(52, 109, 214), (62, 121, 221)},
    "B_sand": {(57, 124, 194), (99, 155, 181), (35, 79, 161), (53, 108, 194), (56, 123, 194), (34, 78, 161), (43, 93, 184), (76, 127, 171)},
    "C_fg": {(23, 66, 126), (102, 47, 184), (24, 91, 153), (35, 129, 161), (18, 44, 100), (158, 60, 212), (65, 43, 161), (22, 65, 125), (51, 166, 181)}
}

def ensure_dirs():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def run():
    print("=== EXTRAÇÃO SEMÂNTICA: Palette Separated Panorama ===")
    
    source = Image.open(SOURCE_PATH).convert("RGBA")
    print(f"Taxonomy: flat_panorama. Modality: palette_separated. Size: {source.size}")
    
    print("\n--- PASSO 1: Extraindo camadas via Dicionário Semântico ---")
    layer_a = sgdk_semantic_parser.extract_by_colors(source, COLOR_DICT["A_far"])
    layer_b = sgdk_semantic_parser.extract_by_colors(source, COLOR_DICT["B_sand"])
    layer_c = sgdk_semantic_parser.extract_by_colors(source, COLOR_DICT["C_fg"])
    
    layer_a_mask = sgdk_semantic_parser.mask_from_isolated_region(layer_a)
    layer_b_mask = sgdk_semantic_parser.mask_from_isolated_region(layer_b)
    layer_c_mask = sgdk_semantic_parser.mask_from_isolated_region(layer_c)
    
    print("Pixels obtidos:")
    print(f"  Far mask: {layer_a_mask.getbbox()}")
    print(f"  Sand mask: {layer_b_mask.getbbox()}")
    print(f"  FG mask: {layer_c_mask.getbbox()}")
    
    print("\n--- PASSO 2: O JUIZ ESTÉTICO (IoU contra camadas do Humano) ---")
    ref_a_mask = sgdk_semantic_parser.mask_from_isolated_region(Image.open(REF_FAR_PATH))
    ref_b_mask = sgdk_semantic_parser.mask_from_isolated_region(Image.open(REF_SAND_PATH))
    ref_c_mask = sgdk_semantic_parser.mask_from_isolated_region(Image.open(REF_FG_PATH))

    iou_a, stats_a = sgdk_semantic_parser.calculate_iou(layer_a_mask, ref_a_mask)
    iou_b, stats_b = sgdk_semantic_parser.calculate_iou(layer_b_mask, ref_b_mask)
    iou_c, stats_c = sgdk_semantic_parser.calculate_iou(layer_c_mask, ref_c_mask)
    
    print(f"  A (Far):   IoU = {iou_a*100:.1f}%")
    print(f"  B (Sand):  IoU = {iou_b*100:.1f}%")
    print(f"  C (FG):    IoU = {iou_c*100:.1f}%")
    
    print("\nSalvando imagens de diagnóstico em reports...")
    ensure_dirs()
    layer_a.save(REPORTS_DIR / "01_ai_far.png")
    layer_b.save(REPORTS_DIR / "01_ai_sand.png")
    layer_c.save(REPORTS_DIR / "01_ai_fg.png")
    
    sgdk_semantic_parser.render_diff_image(layer_a_mask, ref_a_mask).save(REPORTS_DIR / "02_diff_far.png")
    sgdk_semantic_parser.render_diff_image(layer_b_mask, ref_b_mask).save(REPORTS_DIR / "02_diff_sand.png")
    sgdk_semantic_parser.render_diff_image(layer_c_mask, ref_c_mask).save(REPORTS_DIR / "02_diff_fg.png")

if __name__ == '__main__':
    run()

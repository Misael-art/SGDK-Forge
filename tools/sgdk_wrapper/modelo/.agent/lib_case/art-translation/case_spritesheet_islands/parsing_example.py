import sys
from pathlib import Path
from PIL import Image

sys.path.append(str(Path("F:/Projects/MegaDrive_DEV/tools/image-tools")))
import sgdk_semantic_parser

src_path = Path("F:/Projects/MegaDrive_DEV/assets/reference/translation_curation/fighters_gaira_anim/source.png")
reports_dir = src_path.parent / "reports" / "gaira_assembled_strips"

def run_case():
    print("=== AUTO-ASSEMBLER SGDK: Spritesheet Stripping ===")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    img = Image.open(src_path).convert("RGBA")
    
    print("1. Chroma Key Integral [Roxo p/ Alpha]")
    alpha_img = sgdk_semantic_parser.chromakey_to_alpha(img, key_color=(175, 177, 249), tolerance=10)
    
    print("2. Escaneando Geometria de Sprites (min_mass=1500)")
    bboxes = sgdk_semantic_parser.get_island_bounding_boxes(alpha_img, min_mass=1500)
    print(f"-> Detectadas {len(bboxes)} Ilhas viáveis.")
    
    print("3. Clusterização Semântica (Eixo Y)")
    # Agrupa frames que partilham do mesmo piso Y com tolerância de 20px
    clusters = sgdk_semantic_parser.cluster_bboxes_by_y(bboxes, tolerance=20)
    print(f"-> Formadas {len(clusters)} Fitas de Animação (Action Strips)!")
    
    print("4. Normalização Grid SGDK e Quantização VDP")
    
    for i, cluster in enumerate(clusters):
        if len(cluster) < 2:
            # Ignoramos fitas de um só frame ou logotipos isolados
            continue
            
        # Montar a fita canônica alinhada
        raw_strip = sgdk_semantic_parser.assemble_sgdk_strip(alpha_img, cluster)
        
        # Quantizar para 15 cores do Mega Drive
        sprite_flattened = sgdk_semantic_parser.flatten_visible_rgb(raw_strip, fill=(255, 0, 255))
        sprite_snapped = sgdk_semantic_parser.snap_palette_image(sprite_flattened, colors=15, dither=False)
        
        # Restaurar transparency via index magenta
        res_rgba = sprite_snapped.convert("RGBA")
        w_res, h_res = res_rgba.size
        px = res_rgba.load()
        for y in range(h_res):
            for x in range(w_res):
                if px[x, y][:3] == (255, 0, 255):
                    px[x, y] = (0, 0, 0, 0)
                    
        # Salvar Fita de Ação Montada
        out_name = f"strip_action_{i:02d}.png"
        res_rgba.save(reports_dir / out_name)
    
    print(f"SGDK ASSEMBLER CONCLUDED. Saídas geradas em: {reports_dir.name}")

if __name__ == "__main__":
    run_case()

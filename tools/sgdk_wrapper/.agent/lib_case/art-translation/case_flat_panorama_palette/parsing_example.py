"""
Caso Didático: Panorama Achatado Sem Bounding Boxes.
Regra Empreendida: Identificação Isolada de Paleta Semântica

Este código ensina um Agente LLM a atuar num panorama flat (onde as camadas se sobrepõem em Z),
usando extração baseada na paleta de cores, e rechaçando uso de edge-detection ou máscaras espaciais falsas.
"""
from PIL import Image
import sys
import os

# Adiciona o parser ao path para uso didático
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../image-tools")))
import sgdk_semantic_parser

def run_case():
    source = Image.open("source.png").convert("RGBA")

    # 1. No modelo plano, não existem Bounding Boxes. Levantamos as chaves químicas de cor:
    # (Neste exemplo didático, mapeamos uma faixa de azuis que pertencem EXCLUSIVAMENTE ao Foreground)
    FG_COLORS = {
        (23, 66, 126), (102, 47, 184), (24, 91, 153), 
        (35, 129, 161), (18, 44, 100), (158, 60, 212), 
        (65, 43, 161), (22, 65, 125), (51, 166, 181)
    }

    # 2. Extraímos todo o cluster filtrando matematicamente pelo Color Set.
    # Pixels alienígenas assumirão alpha=0 automaticamente:
    foreground = sgdk_semantic_parser.extract_by_colors(source, FG_COLORS)

    # 3. Alpha isolation acontece respeitando keyholes internos (áreas ocluídas por Z-depth)
    fg_mask = sgdk_semantic_parser.mask_from_isolated_region(foreground)
    
    print("Panorama interpretado e limpo com sucesso via Palette Clusters (Chemical Separation).")

if __name__ == '__main__':
    run_case()

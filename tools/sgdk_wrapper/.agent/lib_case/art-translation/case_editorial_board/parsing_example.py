"""
Caso Didático: Prancha Editorial (Editorial Board)
Regra Empreendida: Layout First (Spatial Bounding Boxes)

Este código ensina um Agente LLM a recortar sprites de uma prancha curada por humanos
usando recortes espaciais (Bounding Boxes) antes de qualquer manipulação de pixel.
"""
from PIL import Image
import sys
import os

# Adiciona o parser ao path para uso didático
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../image-tools")))
import sgdk_semantic_parser

def run_case():
    source = Image.open("source.png").convert("RGBA")

    # 1. Em pranchas editoriais, mapeamos topologicamente no espaço XY:
    A_BOX = (0, 0, 512, 128)
    B_BOX = (0, 128, 672, 384)
    C_BOX = (0, 384, 672, 527)

    # 2. Extraímos as regiões brutas sem mesclar matemáticas:
    sky        = sgdk_semantic_parser.extract_region(source, A_BOX)
    arch       = sgdk_semantic_parser.extract_region(source, B_BOX)
    foreground = sgdk_semantic_parser.extract_region(source, C_BOX)

    # 3. Alpha isolation acontece regionalmente
    arch_mask = sgdk_semantic_parser.mask_from_isolated_region(arch)
    
    print("Prancha editorial destrinchada com sucesso via Layout Espacial.")

if __name__ == '__main__':
    run_case()

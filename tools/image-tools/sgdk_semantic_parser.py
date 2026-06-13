import math
from PIL import Image

def extract_region(source: Image.Image, box: tuple) -> Image.Image:
    """Extrai uma sub-região de uma prancha editorial."""
    return source.crop(box).convert("RGBA")

def scale_layer(region: Image.Image, target_width: int) -> Image.Image:
    """Escalona uma região (usando Lanczos) travando o target_width e mantendo aspect ratio."""
    w, h = region.size
    scale = target_width / w
    target_h = int(round(h * scale))
    return region.resize((target_width, target_h), Image.Resampling.LANCZOS)

def chromakey_to_alpha(source: Image.Image, key_color: tuple[int, int, int] = None, tolerance: int = 5) -> Image.Image:
    """Converte a cor de fundo (Chroma Key) para transparência (Alpha=0).
    Se key_color não for fornecido, a cor do pixel (0,0) será considerada o chroma.
    """
    rgba = source.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    
    if key_color is None:
        key_color = (px[0, 0][0], px[0, 0][1], px[0, 0][2])
        
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    res_px = result.load()
    
    def color_dist(c1, c2):
        return abs(c1[0]-c2[0]) + abs(c1[1]-c2[1]) + abs(c1[2]-c2[2])

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 128 and color_dist((r, g, b), key_color) > tolerance:
                res_px[x, y] = (r, g, b, 255)
    return result

def extract_large_islands(source: Image.Image, min_mass: int = 500) -> Image.Image:
    """Detecta todos os blocos isolados de pixels opacos, remove os lixos menores que min_mass 
    (textos e ruídos) e retorna uma imagem transparente apenas com os sprites sólidos."""
    rgba = source.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    
    # 1. Obter bool mask
    mask = [[(px[x, y][3] > 128) for x in range(w)] for y in range(h)]
    visited = [[False]*w for _ in range(h)]
    
    # BFS para encontrar ilhas
    islands = []
    
    for y in range(h):
        for x in range(w):
            if mask[y][x] and not visited[y][x]:
                island_pixels = []
                queue = [(x, y)]
                visited[y][x] = True
                
                while queue:
                    cx, cy = queue.pop(0)
                    island_pixels.append((cx, cy))
                    
                    # Checar os 8 vizinhos para manter os sprites coesos
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if dx == 0 and dy == 0: continue
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                if mask[ny][nx] and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                islands.append(island_pixels)
                
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    res_px = result.load()
    
    for island in islands:
        if len(island) >= min_mass:
            for x, y in island:
                res_px[x, y] = px[x, y]
                
    return result

def get_island_bounding_boxes(source: Image.Image, min_mass: int = 500) -> list[tuple[int, int, int, int]]:
    """Detecta ilhas contínuas de massa >= min_mass e retorna a caixa delimitadora (left, top, right, bottom)
    para cada ilha encontrada."""
    rgba = source.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    
    mask = [[(px[x, y][3] > 128) for x in range(w)] for y in range(h)]
    visited = [[False]*w for _ in range(h)]
    
    bboxes = []
    
    for y in range(h):
        for x in range(w):
            if mask[y][x] and not visited[y][x]:
                island_mass = 0
                min_x, max_x = x, x
                min_y, max_y = y, y
                
                queue = [(x, y)]
                visited[y][x] = True
                
                while queue:
                    cx, cy = queue.pop(0)
                    island_mass += 1
                    
                    if cx < min_x: min_x = cx
                    if cx > max_x: max_x = cx
                    if cy < min_y: min_y = cy
                    if cy > max_y: max_y = cy
                    
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if dx == 0 and dy == 0: continue
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                if mask[ny][nx] and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                                    
                if island_mass >= min_mass:
                    bboxes.append((min_x, min_y, max_x+1, max_y+1))
                    
    return bboxes

def cluster_bboxes_by_y(bboxes: list[tuple[int, int, int, int]], tolerance: int = 20) -> list[list[tuple[int, int, int, int]]]:
    """Agrupa as Bounding Boxes baseado no 'chão' (Max Y).
    Se duas boxes tem seu piso num limiar de 'tolerance' px de diferença, elas pertencem à mesma animação."""
    if not bboxes: return []
    
    # Sort boxes by their bottom Y
    sorted_boxes = sorted(bboxes, key=lambda b: b[3])
    
    clusters = []
    current_cluster = [sorted_boxes[0]]
    
    for box in sorted_boxes[1:]:
        # O piso (box[3]) está perto do piso médio do cluster atual?
        cluster_bottoms = [b[3] for b in current_cluster]
        avg_bottom = sum(cluster_bottoms) / len(cluster_bottoms)
        
        if abs(box[3] - avg_bottom) <= tolerance:
            current_cluster.append(box)
        else:
            clusters.append(current_cluster)
            current_cluster = [box]
            
    if current_cluster:
        clusters.append(current_cluster)
        
    # Ordenar as strips pelo eixo Y geral (do topo pra baixo da página)
    clusters.sort(key=lambda c: c[0][3])
    
    # E para cada cluster, ordenar as animações da esquerda pra direita (Eixo X)
    for c in clusters:
        c.sort(key=lambda b: b[0])
        
    return clusters

def align_to_multiple_of_8(val: int) -> int:
    """Retorna o multiplo de 8 mais próximo (ceiling)."""
    rem = val % 8
    if rem == 0: return val
    return val + (8 - rem)

def assemble_sgdk_strip(alpha_source: Image.Image, cluster_bboxes: list[tuple[int, int, int, int]]) -> Image.Image:
    """Dada uma source image e as bounding boxes que pertencem à uma animação,
    encontra a maior altura e largura, arredonda para múltiplo de 8 (padrão SGDK)
    e alinha todos os frames num único strip mestre, presos pelo piso center-bottom."""
    
    if not cluster_bboxes: return None
    
    max_w = max(b[2] - b[0] for b in cluster_bboxes)
    max_h = max(b[3] - b[1] for b in cluster_bboxes)
    
    # Arredondamentos de segurança SGDK VRAM
    sgdk_w = align_to_multiple_of_8(max_w)
    sgdk_h = align_to_multiple_of_8(max_h)
    
    frames_count = len(cluster_bboxes)
    strip_w = sgdk_w * frames_count
    strip_h = sgdk_h
    
    strip_img = Image.new("RGBA", (strip_w, strip_h), (0, 0, 0, 0))
    
    for i, bbox in enumerate(cluster_bboxes):
        frame_crop = alpha_source.crop(bbox)
        fw = bbox[2] - bbox[0]
        fh = bbox[3] - bbox[1]
        
        # Bottom-Center align
        # O chao do sprite fica grudado no chao da box grid. (Y = sgdk_h - fh)
        # E centralizado no X local: (X = (sgdk_w - fw) // 2)
        local_x = (sgdk_w - fw) // 2
        local_y = sgdk_h - fh
        
        global_x = (i * sgdk_w) + local_x
        global_y = local_y
        
        strip_img.alpha_composite(frame_crop, (global_x, global_y))
        
    return strip_img

def scale_mask(mask: Image.Image, target_width: int) -> Image.Image:
    """Escalona uma máscara alfa preservando a opacidade binária dura (Nearest Neighbour)."""
    w, h = mask.size
    scale = target_width / w
    target_h = int(round(h * scale))
    return mask.resize((target_width, target_h), Image.Resampling.NEAREST)

def extract_by_colors(source: Image.Image, valid_colors: set[tuple[int, int, int]]) -> Image.Image:
    """Retorna uma nova imagem contendo apenas os pixels da imagem-fonte cujas cores estejam no conjunto valid_colors.
    O restante fica vazio (Alpha=0).
    """
    rgba = source.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()
    
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    res_px = result.load()
    
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a >= 128 and (r, g, b) in valid_colors:
                res_px[x, y] = (r, g, b, 255)
                
    return result

def mask_from_isolated_region(region: Image.Image, alpha_threshold: int = 128) -> Image.Image:
    """Gera o alpha de uma região que já se encontra isolada,
    onde tudo >= alpha_threshold é considerado bloco opaco ativo.
    Retorna uma imagem base 'L' (Grayscale 0-255).
    """
    rgba = region.convert("RGBA")
    w, h = rgba.size
    px = rgba.load()

    mask = Image.new("L", (w, h), 0)
    mpx = mask.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a >= alpha_threshold:
                mpx[x, y] = 255

    return mask

def calculate_iou(mask1: Image.Image, mask2: Image.Image) -> tuple[float, dict]:
    """Calcula o índice Intersection over Union entre duas máscaras."""
    m1 = mask1.convert("L")
    m2 = mask2.convert("L")
    
    # Check if dimensions differ. Resize m2 if needed to match m1.
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

def render_diff_image(ai_mask: Image.Image, human_mask: Image.Image) -> Image.Image:
    """Retorna uma imagem diagnóstico de erros. White=Concordam, Red=FP, Green=FN."""
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

def alpha_composite_layer(canvas: Image.Image, layer: Image.Image, mask: Image.Image, position: tuple[int, int]) -> Image.Image:
    """Aplica o matte do mask e faz o alpha composite no canvas base."""
    applied = layer.copy()
    applied.putalpha(mask)
    result = canvas.copy()
    result.alpha_composite(applied, position)
    return result

def flatten_visible_rgb(image: Image.Image, fill: tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
    rgba = image.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (*fill, 255))
    return Image.alpha_composite(background, rgba).convert("RGB")

def snap_channel(value: int) -> int:
    return min(255, round(value / 34) * 34)

def snap_palette_image(image: Image.Image, colors: int = 15, dither: bool = False, return_indexed: bool = False) -> Image.Image:
    paletted = image.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors, dither=Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE)
    palette = paletted.getpalette()
    for i in range(len(palette) // 3):
        palette[i*3] = snap_channel(palette[i*3])
        palette[i*3+1] = snap_channel(palette[i*3+1])
        palette[i*3+2] = snap_channel(palette[i*3+2])
    paletted.putpalette(palette)
    if return_indexed:
        return paletted
    return paletted.convert("RGB")

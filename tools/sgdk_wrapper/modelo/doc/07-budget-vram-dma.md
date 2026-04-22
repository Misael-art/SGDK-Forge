# 07 - Budget VRAM e DMA — __PROJECT_NAME__

## Semantica obrigatoria

Separar sempre:

- `rom_asset_cost`: asset em ROM e compressao (`FAST`, `BEST`, `NONE`)
- `vram_resident_set`: tiles/fontes/sprites/mapas simultaneamente residentes na cena
- `load_time_dma_cost`: uploads de boot, loading ou troca de cena
- `per_frame_dma_cost`: uploads por VBlank durante gameplay
- `active_animation_window`: frames/ciclos realmente residentes agora
- `scene_local_scope`: assets permitidos na cena atual
- `scanline_sprite_pressure`: sprites totais e pior scanline

## VRAM residente por cena

- [Cena 1]: [tiles residentes / fontes / sprites / mapas]
- [Cena 2]: [tiles residentes / fontes / sprites / mapas]

## ROM e compressao

- [Asset]: [FAST/BEST/NONE + custo ROM conhecido]
- Observacao: compressao reduz ROM/load, nao o custo final em VRAM quando descompactado.

## DMA de preload/loading

- [Cena 1]: [uploads permitidos fora de gameplay responsivo]
- [Cena 2]: [uploads permitidos fora de gameplay responsivo]

## DMA por frame no pior caso

- [Cena 1]: [words por VBlank durante gameplay]
- [Cena 2]: [words por VBlank durante gameplay]

## Animacao, streaming e sprites

- `active_animation_window`: [quais ciclos/frames ficam residentes]
- `scene_local_scope`: [quais assets entram/saem por cena]
- `streaming/fallback`: [tilemap_streaming / animation_window_streaming / scene_local_preload / reduced]
- `scanline_sprite_pressure`: [sprites totais e pior scanline]

## Politica

- nao contar o mundo inteiro como residente se houver scene-local loading ou streaming declarado
- nao contar asset `BEST` como menor em VRAM; medir tiles descompactados
- nao trocar tiles inteiros por frame sem necessidade
- preferir paleta e scroll para animacao de ambiente
- redraw de tilemap completo so em troca de estado ou mudanca estrutural

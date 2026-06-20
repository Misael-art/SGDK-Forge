# Case Study - 16 Tile e atributos de tilemap

Status: `case_study_candidate`
Owner principal: `multi-plane-composition`
Owners complementares: `tiled-hybrid-parallax-curator`, `megadrive-vdp-budget-analyst`, `art-translation-to-vdp`

## Licao util

Tilemap de Mega Drive nao e apenas uma imagem cortada em 8x8. Cada celula do
mapa carrega uma palavra de atributo com indice de tile, paleta, prioridade e
flip horizontal/vertical. Ferramentas como 16 Tile sao uteis quando ajudam o
designer a autorar esses metadados em vez de deixar tudo como macro global.

## O que o agente deve absorver

- Tratar tilemap como matriz semantica, nao screenshot.
- Exigir `scene_tilemap_conversion_report` para cena critica.
- Exigir `tilemap_flag_report` quando houver dedup ou flip.
- Exigir `per_tile_palette_conflict_report` antes de promocao visual.
- Separar ferramenta usada de contrato produzido: 16 Tile, Tiled ou builder
  proprio so passam se emitirem evidencias equivalentes.

## Gate recomendado

Antes de runtime:

1. `depth_role_map`
2. `camera_motion_contract`, se houver scroll/camera
3. `scene_tilemap_conversion_report`
4. `tilemap_flag_report`
5. `per_tile_palette_conflict_report`
6. `palette_vitality_report`, se a fonte tiver cor forte
7. `vram_residency_report` ou budget equivalente

## Limites

- `MAP_create(..., 0)` nao prova atributos por tile. Os atributos precisam
  estar presentes no mapa gerado.
- Blocos de ancoragem de paleta podem ser uteis em importacao, mas nao devem
  inflar o tileset final jogavel.
- Snap de cor deve seguir politica do projeto e ser validado contra palette
  strip/CRAM, nao por frase solta de video.

## Falha que previne

Evita que o agente aprove uma cena porque ela "aparece no emulador" enquanto
perde prioridade de foreground, vitalidade de paleta, parallax ou flags de flip.

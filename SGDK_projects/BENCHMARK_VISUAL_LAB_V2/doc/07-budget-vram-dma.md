# 07 - Budget VRAM e DMA - BENCHMARK_VISUAL_LAB_V2

## Estado

- status: `documentado`
- laudo vigente: `nao_medido`
- motivo: o projeto ainda usa placeholders code-only e `res/resources.res` nao declara assets reais.
- regra de leitura: nenhum budget pode ser promovido para `validado_budget` sem numeros extraidos do build, da cena real e da evidencia em BlastEm.

## Semantica obrigatoria

Separar sempre:

- `rom_asset_cost`: asset em ROM e compressao (`FAST`, `BEST`, `NONE`).
- `vram_resident_set`: tiles, fontes, sprites, mapas e tabelas simultaneamente residentes na cena.
- `load_time_dma_cost`: uploads de boot, loading, troca de cena ou trecho sem controle responsivo.
- `per_frame_dma_cost`: uploads por VBlank durante gameplay/controle ativo.
- `active_animation_window`: frames/ciclos realmente residentes na janela atual.
- `scene_local_scope`: assets permitidos na cena atual; assets de outra cena nao entram no set residente.
- `scanline_sprite_pressure`: sprites totais, pior scanline e risco de flicker/multiplexing.

## Baseline tecnico conhecido

- `VDP_setPlaneSize(64, 32, TRUE)` em `src/core/app.c`.
- `SPR_initEx(768)` em `src/core/app.c`; esta reserva reduz o espaco util para tiles de BG.
- Overlay tecnico usa `WINDOW`, conforme `src/system/overlay.c`.
- `resources.res` esta vazio de recursos reais; assets futuros devem entrar por cena, nao como mundo inteiro residente.
- `out/logs/validation_report.json` registra build limpo, mas `validado_budget=false`, `testado_em_emulador=false` e `ready_for_aaa=false`.

## VRAM residente por cena

### `front_end_main_menu`

- `scene_local_scope`: menu/title e assets de navegacao do laboratorio.
- `vram_resident_set`: fonte/HUD em `WINDOW`, tiles de fundo do menu, cursor/feedback e possiveis sprites de selecao.
- `active_animation_window`: apenas frames de cursor, brilho, pulso ou parallax visivel no menu.
- `streaming/fallback`: `scene_local_preload`; fallback para `window_plane_static_hud` + fundo menos variado.

### `scene_multiplane_showcase_v2`

- `scene_local_scope`: BG_B atmosferico, BG_A foreground/estrutura, sprite heroico e overlay tecnico.
- `vram_resident_set`: somente tiles unicos da cena 1, nao assets das cenas 2/3.
- `active_animation_window`: sem animacao obrigatoria ate assets reais; se houver sprite, manter apenas ciclo ativo.
- `streaming/fallback`: `scene_local_preload`; fallback `compare_flat` se BG_A+BG_B excederem budget.

### `scene_water_fx_showcase_v2`

- `scene_local_scope`: tiles da cena de agua, tabela de line scroll, overlay em `WINDOW`.
- `vram_resident_set`: tiles e mapas locais; nao contar cenas de profundidade ou menu como residentes.
- `active_animation_window`: ondas/tiles animados apenas na faixa visivel.
- `streaming/fallback`: `scene_local_preload`; se `HSCROLL_LINE` competir com leitura, recuar para agua menos granular ou palette cycling.

### `scene_depth_tower_showcase_v2`

- `scene_local_scope`: tiles da torre/profundidade, dados de `VSCROLL_COLUMN`, overlay em `WINDOW`.
- `vram_resident_set`: tiles e mapas locais da torre; nada herdado das cenas anteriores.
- `active_animation_window`: nenhum ciclo pesado aprovado ate laudo real.
- `streaming/fallback`: `scene_local_preload`; fallback para menos colunas, menos parallax ou `compare_flat`.

## ROM e compressao

- `resources.res`: atualmente sem assets declarados.
- Politica: `FAST`, `BEST` e `NONE` mudam custo de ROM/decompress/load, mas nao reduzem os tiles descompactados quando residentes em VRAM.
- Todo asset aprovado deve registrar `rom_asset_cost` e custo descompactado em tiles antes de entrar no runtime.

## DMA de preload/loading

- Permitido carregar assets de cena em troca de cena, menu ou loading honesto.
- Upload pesado em preload nao deve ser confundido com `per_frame_dma_cost`.
- Toda transicao futura deve declarar se usa `scene_local_preload`, `tilemap_streaming` ou `animation_window_streaming`.

## DMA por frame no pior caso

- Cena 1: `nao_medido`; esperado baixo ate assets reais.
- Cena 2: `nao_medido`; deve medir tabela de `HSCROLL_LINE`, tile animation e qualquer upload concorrente.
- Cena 3: `nao_medido`; deve medir atualizacao de `VSRAM`/colunas e limpeza no teardown.
- Regra: upload por frame precisa caber no pior VBlank, nao no frame mais vazio.

## Sprites e scanline pressure

- Baseline de sprite engine: `SPR_initEx(768)`.
- Cena 1: sprite heroico futuro deve declarar total de sprites, tiles e pior scanline.
- Cena 2: FX de agua nao deve usar sprites decorativos se tile animation ou scroll resolverem com menos pressao.
- Cena 3: sprites de profundidade/grafts so entram com pior scanline auditado.
- Multiplexing/flicker controlado e tecnica de risco, nao mascara para overflow.

## Politica de fallback

- Se o mundo inteiro nao couber residente, recortar por `scene_local_scope` antes de reduzir ambicao visual.
- Se uma sheet completa nao couber, propor `active_animation_window`, SGDK auto VRAM alloc ou streaming manual validado.
- Se um stage maior exceder o plano, propor `tilemap_streaming` com seam budget.
- Se o pior quadro nao fechar, usar `fallback_reduced_residency`, reduzir tiles unicos, diminuir frames, simplificar parallax ou promover `compare_flat`.

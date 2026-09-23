# 07 - Budget VRAM e DMA — TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

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

- `combat_cinder_circuit` D1: BG_B 500 tiles + BG_A 100 tiles + Kairo probe 15 tiles; a medição source-bound registra pico de 946 tiles no estado `enter_stage`, teto estático 1740 e utilização 54,4%. `SPR_initEx(64)` reserva tiles 1376–1439; planos/fontes permanecem separados e não há overlaps no `res_graph_report`.
- Branding/front-end: fora do resident set do combate; os recursos de branding são carregados por cena. A cena de luta não conta o roster inteiro: apenas os lutadores ativos entram na janela residente.

## ROM e compressao

- `res/resources.res`: ResComp informa 76.468 bytes binários, 93.012 bytes de origem, 35.630 bytes compactados e 77.718 bytes totais de metadados/dados. `BEST` reduz ROM/load; não reduz o custo final dos 600 tiles de background residentes.
- Observação: compressão reduz ROM/load, não o custo final em VRAM quando descompactado.

## DMA de preload/loading

- `combat_cinder_circuit`: a captura BlastEm Linux observou o estado da fila durante 90 observações de warmup: pico de 1000 bytes, 4 entradas, capacidade de 7200 bytes, no frame 1. Isso mede o estado observado da fila de preload, não prova que todo o carregamento/streaming foi concluído.
- Troca de lutador/streaming: contrato declara janela ativa e fallback para Jack/Ryo/C1 no slice, mas não há `dma_queue_report` hash-bound; não promover como DMA validado.

## DMA por frame no pior caso

- Captura BlastEm Linux da ROM `869a0eedde787d632aa1997edfebe36c556f386bc40c57fba3e14cdc8a660e18`, sessão `blastem-linux-20260909T173215Z-3070928`, observou a cena 3 após 90 frames de warmup: pico de fila DMA por frame de 32 bytes, 1 entrada, contra capacidade medida de 7200 bytes, no frame 91. Isso é medição real do gameplay observado.
- A mesma captura separou o estado de preload: 1000 bytes, 4 entradas e capacidade de 7200 bytes no frame 1, em 90 observações. Isso não prova completude de loading/streaming, troca de lutador, residency viva nem performance sustentada; `sample_count=32` e `over_budget_frames=0` continuam insuficientes para o pior quadro regional.

## Animacao, streaming e sprites

- `active_animation_window`: dois lutadores ativos e FX do envelope D1; o sprite de martelo é declarado streamado. O frame completo de personagens finais ainda não foi promovido.
- `scene_local_scope`: stage Cinder Circuit + dois lutadores ativos + HUD/FX do slice; roster inativo sai da residência.
- `streaming/fallback`: `scene_local_preload` para BG e `animation_window_streaming` planejado para roster; fallback declarado: apenas Jack/Ryo/C1 no slice.
- `scanline_sprite_pressure`: simulador H40 self-check passou; envelope D1 mediu 8 sprites e 160 pixels no pior scanline, 16 links totais, contra limites 20/320. Nenhuma linha excedeu o limite.

## Politica

- nao contar o mundo inteiro como residente se houver scene-local loading ou streaming declarado
- nao contar asset `BEST` como menor em VRAM; medir tiles descompactados
- nao trocar tiles inteiros por frame sem necessidade
- preferir paleta e scroll para animacao de ambiente
- redraw de tilemap completo so em troca de estado ou mudanca estrutural

## Parecer vigente

- Eixo técnico: `cabe com recuo`. A residência source-bound e a pressão de scanline estão dentro do limite; a sessão `blastem-linux-20260909T173215Z-3070928` mediu quatro faixas runtime (`[16,516)`, `[516,616)`, `[1376,1391)`, `[1391,1406)`) sem overflow, DMA baixo (32/7200 bytes, 1 entrada) e preload de 1000/7200 bytes com 4 entradas. Isso ainda não prova todos os estados, completude de streaming, arte final ou desempenho sustentado; a captura teve janela 59,4 fps e `cpu_load_max=100`, sem promoção para 60 fps.
- Eixo perceptivo: não avaliado. Os lutadores ativos continuam probes de laboratório e a cena não pode receber `visual_aprovado`/`ready_for_aaa`.
- Recuo obrigatório antes de fechar: medir completude de preload/streaming e a janela regional sustentada, manter a janela local de dois lutadores e substituir os probes por arte nativa aprovada; não usar flicker/multiplexing como fallback.

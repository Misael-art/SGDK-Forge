# Especificacao de cenas - Shadow Dancer Revisitado

## scene_id: stage_virtual_map

- papel: slice jogavel tecnico
- entrada: reset do console
- owner: `main.c` + `map_handler.c`
- planos: BG_A para MAP; sprites para player
- tecnicas: `tile_cache_streaming_refcount`, `dma_transfer_safety`, `camera_scroll_management`, `rescomp_metasprite_decomposition_audit`
- budget: 576 tiles ativos; 1 player; 1 mapa residente em ROM; 10000 bytes de fila DMA configurada
- fallback: erro de MAP/cache entra em tela textual de falha e permanece em VBlank
- evidencia: build, validation_report, screenshot BlastEm e log de DMA quando o closeout for executado

### Reset e ownership

- aloca: `Map`, tile cache estatico, `Sprite` do player
- reseta: input, camera, cache, sprite e callbacks do mapa
- callback global alterado: apenas o callback de patch do `stageMap`
- teardown futuro: `tileCache_shutdown`, `SPR_reset`, limpeza de BG_A e scroll antes de qualquer nova cena

### Medicao pendente

O pior caso de scroll deve ser medido com `vdp_scanline_simulator.py` e com captura BlastEm antes de qualquer claim de performance. O build atual foi gerado pela rota `linux_wine_bridge` em SGDK 2.11; ROM SHA-256: `ee071686940c7f2f853b3f3120f9f2baf8d1bc4e5e0d3aeaf8081501a725eb54`.

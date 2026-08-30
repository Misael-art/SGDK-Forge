# Plano de Continuidade — Showdown SFF v1 (AAA por incrementos)

**versao:** 1.11.0 · **atualizado:** 2026-08-30 · **mantenedor:** proximo agente
**regra-mae:** SGDK_GLOBAL §38 (sonda antes de promessa) · prompt modelo `doc/prompts_modelo/prompt_modelo_direcionamento_projeto.md`
**estado na emissao:** paletas v002 seladas; ROM corrente `d99f8d12…`; viewer streaming 41×29 / cache 1190

## Como trabalhar daqui em frente

1. Leia `lab_report.json` (fonte #1) e o ultimo learning doc em `doc/agent_learning/`.
2. Execute o PRIMEIRO item `pending` na ordem abaixo — nunca pule a fila.
3. Feche o incremento com: gate de aceite verde + evidencia selada + linha no
   REGISTRO deste arquivo + learning doc se houver licao nova. So entao o
   proximo item se torna `pending`.
4. Nada de claim sem numero. Adjetivo sem piso = defeito (§36).

## Fila sequenciada

### DONE — P1: Paletas otimizadas v002 (2026-08-26)
- Aceite cumprido: remaps oficiais 235880→205283 (−13%); bundles sealed A/B;
  dedup intacto (+2 tiles). Evidencia: `evidence_optimized_v002/…084143Z…`,
  `analysis/optimized_palettes_v002.json`, learning doc de 2026-08-26.

### DONE — P1b: Bloco VLAB portado para a probe do viewer
- Fecha gap do selador; status de evidencia subiu de `blastem_minimal` para
  `sealed`. Qualquer nova cena deve manter VLAB + heartbeat MDRT vivos.

### DONE — P2: `code_loaded_tiles_unmeasured` -> MEDIDO (2026-08-26)
- Instrumentacao: `gTileStreamStats[8]` em scene_demo.c + bloco TSTR
  (SRAM 0x300) na probe + leitor `tools/diagnostics/read_tile_stream_stats.py`.
- Numeros da sessao selada `…120420Z…`: pedidos=DMA=1157 tiles, 73 uploads,
  pico residente 1157/1190, **margem real 33 tiles (2,77%)**, 0 overflows,
  37.024 bytes DMA. Report: `analysis/tile_stream_stats_v002.json`.
- ALERTA para o proximo agente: margem real (33) e MENOR que a estimativa
  estatica antiga (64). P3 deixou de ser rotina e virou gate critico.

### DONE — P3: Varredura de cantos medida (2026-08-26)
- TSTR v2 (5 paradas): center 818, nw 657, ne 689, sw 1094, se 1105.
- Todos < 1190, zero overflow; pior canto SE com margem 85 (7,14%).
- Bundle selado `evidence_sweep_p3/…131919Z…`; report `analysis/tile_stream_stats_p3_sweep.json`.

### PENDING — P3b: Gate de folga DURANTE P6 (reframed pelo soak 420s)
- Soak provou: demo estatica nao re-streama (contadores congelados pos-varredura);
  'pico dinamico 1157' corrigido para 'passe de restauracao da posicao padrao'.
- Hoje NAO ha risco de overflow em operacao. O risco nasce quando P6 ligar
  animacoes SFF (bg2 troca tiles entre frames -> passes variam).
- Gate para habilitar P6: com animacoes ligadas, rodar burst/soak e exigir
  TSTR com overflow_events_total==0 E requested/passe <= 1071 (90% de 1190).
  Se estourar: janela 40x28 (-69 slots) ou eviction LRU por epoca.
- Ferramentas prontas: TSTR v2 + read_tile_stream_stats.py ja medem isso.

### DONE — P4: Escape por erro nas bandas BG_A + re-otimização (2026-08-29)
- Patch: `export_showdown_bins.py` BG_A agora com escape 1.45× igual ao BG_B.
- Medida oficial: manual novo 184.078 → otimizado 175.699 (**−4,5%** sobre manual novo; **−25,5%** vs manual original 235.880).
- Evidência selada `evidence_p4_escape/…150342Z…`; margem VRAM mantida 38 (vs 33), pior canto 1106/1190.
- Próximo agente herda paletas v002 já com escape; não reverter.

### DONE — P5: Performance sustentada provada (2026-08-29)
- Soak 120s selado `evidence_p5_soak/…155104Z…`: VLAB 32 samples, 0 over_budget, max_cpu 88%, p50=82 p95=88 p99=88 (MDRT samples).
- Report: `analysis/p5_performance_report.json` — claim `proven_for_sample_window`, nota de 32-sample window limitação honesta.
- Próximo soak burst pode ampliar janela amostral se P6 aumentar carga.

### MEASURED_WITH_LIMITATION — P6: Animacoes SFF (2026-08-29)
- Teste: FRAME_ANIMATION_ENABLED=1 interval 45f; animação visível (61% pixels) mas soak 120s: overflow=7, over_budget=15.
- Veredito: **REPROVADO para reload completo**. AAA exige streaming incremental/delta entre frames.
- ROM revertida para DISABLED para manter selo verde; evidências em `evidence_p6_*` + `analysis/p6_animation_report.json`.
- Próximo AAA real: implementar diff incremental e re-medir via TSTR.

### MEASURED_WITH_LIMITATION — P6b: Incremental delta sem eviction (2026-08-29)
- Método: delta entre frames sem reset; DMA 10112→6698 (−33%) mas cache acumula.
- Medida: 1190 cap → 121 overflows (piora), 1400 cap → 7 overflows, max 1276, over_budget 15.
- Veredito: **REPROVADO sem eviction**. Report: `analysis/p6b_incremental_report.json`.
- Evidências: `evidence_p6b_soak` (1190) e `evidence_p6b_soak2` (1400) selados.

### MEASURED_WITH_LIMITATION — P6c: Capacity 1480 sem eviction (2026-08-29)
- Teste: CACHE 1480 + incremental; soak 120s: overflow 7, max 1276, over_budget 15.
- Veredito: **REPROVADO** — ampliar VRAM sozinho não zera; união ainda cresce.
- Report: `analysis/p6c_capacity_test.json`; evidência `evidence_p6c_soak`.

### DONE — P6d: Eviction por época + DMA_QUEUE (2026-08-30)
- Método: sSlotToGlobal + sNeeded + eviction do slot não usado na nova janela; DMA_QUEUE em vez de CPU.
- Medida: soak 120s `evidence_p6d_soak/…012522Z…` overflow **0** (antes 121) ✅, max_res 1190/1190, mas over_budget 15/32, max_cpu 317.
- Veredito: **REPROVADO para CPU** mas cache OK; report `analysis/p6d_eviction_report.json`.
- Código incremental + eviction permanece no viewer para próximo passo.

### DONE — P6e: Throttle 90f + eviction (2026-08-30)
- Interval 90f (~0.66 fps) + eviction + DMA_QUEUE: soak 120s `evidence_p6e_soak/…013639Z…` overflow **0** ✅, over_budget **7** (antes 15, −53%), max_cpu 249, p50=82 p99=88.
- Report: `analysis/p6e_throttle_report.json` — 120f piora (8 over_budget), 90f é melhor compromisso.
- Veredito: **ainda REPROVADO para AAA** (7/32 >0) mas sequencialmente melhor; próximo é split DMA.

### MEASURED_WITH_LIMITATION — P6f: Split DMA 16/frame (2026-08-30)
- Método: pending queue 16/frame para espalhar uploads.
- Medida: soak 120s `evidence_p6f_soak/…112611Z…` overflow 0 ✅, over_budget **11** (piora vs 7 do throttle puro), max_cpu 299.
- Veredito: **REPROVADO** — split aumentou CPU (overhead de queue); próximo é otimizar custo por tile, não apenas distribuir.
- Report: `analysis/p6f_split_report.json`; evidência burst mostra 5.32% diff.
- ROM revertida para DISABLED para selo verde.

### MEASURED_WITH_LIMITATION — P6g: Sweep espalhado 1/frame (2026-08-30)
- Método: sweep de cantos espalhado 1 por frame para reduzir pico no enter.
- Medida: soak 120s `evidence_p6g_soak/…113617Z…` overflow 0 ✅, over_budget **8** (vs 7 do throttle puro), max_cpu 250.
- Veredito: **REPROVADO** — overhead de 5 frames extras supera economia; report `analysis/p6g_sweep_spread_report.json`.

### MEASURED_WITH_LIMITATION — P6h: precomputeOpacityTable (2026-08-30)
- Método: tabela de opacidade pré-preenchida no enter, eliminando scan lazy 32B/tile.
- Medida: soak 120s `evidence_p6h_soak/…142715Z…` overflow 0 ✅, over_budget **8**, max_cpu 250 — NEUTRO vs P6e (7/249).
- Conclusão: o custo dominante NÃO é o scan de opacidade (cache já quente); é o **re-upload full-window no tick**. Cache gate PASS; animação AAA precisa de dirty-region.
- Report: `analysis/p6h_precompute_report.json`.
- Default verde fixado (animation OFF): `evidence_clean_final5/…143338Z…` **0 overflows, 0 over_budget, max_cpu 89**.

### MEASURED_WITH_LIMITATION — P6i: Animação via dirty-region delta (2026-08-30)
- Método: VDP_setTileMapDataRect sub-rect (dirty bounding box por plano) no tick de animação.
- Medida: soak 120s `evidence_p6i_soak/…145116Z…` overflow 0 ✅, over_budget **8**, max_cpu **243** (vs 250 full-window).
- Veredito: **REPROVADO** — frame-swap SFF é difuso (bg2 cobre quase a janela), dirty rect ≈ full-window. Cache PASS.
- Report: `analysis/p6i_dirty_region_report.json`. Código dirty-region mantido (melhoria leve/inofensiva).
- Default verde fixado: `evidence_clean_final6/…145424Z…` 0/0/89.

### DONE — P6j: Instrumentação de peak-frame VLAB (isolar causa) (2026-08-30)
- Portado VLAB metric_words 24→32 com peak-frame (words 26..31: scanline/cpu/sprite) como no canonico Celestial Chase.
- Leitura: soak `evidence_p6j_soak/…151815Z…` peak_cpu_frame=**97** → pico no ENTER (sweep+stream inicial), NÃO no tick de animação. max_scanline=0, max_cpu=243.
- Veredito: a causa do over_budget persistente (7-8) é o trabalho de streaming no ENTER, não a animação.
- Report: `analysis/p6j_peak_frame_report.json`. Default verde mantido: `evidence_clean_final7/…152838Z…` 0/0/89.

### PENDING — P6k: Descarregar trabalho do ENTER (AAA real)
- Objetivo: mover sweep de cantos + stream inicial para pós-enter (ex.: frame 30+) ou VBlank, para zerar os 8 over_budget com animação ligada.
- Aceite: 0 overflows + 0 over_budget em soak 120s com animação 90f ligada (peak_frame fora da janela de enter).

## Limites estruturais lembrados
- Host Linux: build SO via `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh`;
  captura via `capture_blastem_evidence_linux.sh` (exige VLAB vivo).
- `*.bin` nunca vai pro git (politica); hashes moram nos JSONs.
- Este estudo e `_agent_training`: `lab_not_delivery=true` permanece; promocao
  canonica exige curadoria humana (ver canonical_promotion_review.md).

# Plano de Continuidade — Showdown SFF v1 (AAA por incrementos)

**versao:** 1.0.0 · **atualizado:** 2026-08-26 · **mantenedor:** proximo agente
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

### PENDING — P3: Margem VRAM sob camera movendo (estresse real) — CRITICO
- Objetivo: varrer camera pelos 4 cantos do mundo 768×480 e provar que
  `max_resident < CACHE_TILE_CAPACITY` com folga declarada.
- Contexto P2: margem medida no centro = 33 tiles (2,77%). Cantos podem pedir
  mais. Se qualquer passe estourar: reduzir janela (41x29 -> 40x28 = -69 slots)
  ou implementar eviction LRU por linha; re-medir com o mesmo TSTR.
- Aceite: varredura scripted (input gravado ou loop automatico no demo),
  folga >= 5% ou plano de reducao de janela/eviction LRU documentado.

### PENDING — P4: Escape por erro nas bandas BG_A (fidelidade extra)
- Pre-condicao: P3 verde (mudanca de pid pode alterar unique tiles).
- Objetivo: replicar o escape 1.45x do BG_B nas bandas BG_A; refazer
  otimizacao; medir remaps de novo.
- Aceite: remaps < 205283 E dedup <= limite E anti-magenta pass AND A/B
  mesmo-emulador mostra melhoria sem regressao de silhueta.

### PENDING — P5: Performance sustentada provada
- Objetivo: captura burst (varios minutos / burst_count do capturador) com
  frametime estavel; substituir claim `unproven` por p50/p95/p99.
- Aceite: p99 <= 16.67ms na cena mais pesada OU slowdown documentado.

### PENDING — P6: Animacoes SFF (frame_animation_enabled=false hoje)
- Objetivo: animar ao menos 1 layer BG com budget DMA medido pelo P2/P5.
- Aceite: animacao visivel em BlastEm + gates verdes + A/B.

## Limites estruturais lembrados
- Host Linux: build SO via `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh`;
  captura via `capture_blastem_evidence_linux.sh` (exige VLAB vivo).
- `*.bin` nunca vai pro git (politica); hashes moram nos JSONs.
- Este estudo e `_agent_training`: `lab_not_delivery=true` permanece; promocao
  canonica exige curadoria humana (ver canonical_promotion_review.md).

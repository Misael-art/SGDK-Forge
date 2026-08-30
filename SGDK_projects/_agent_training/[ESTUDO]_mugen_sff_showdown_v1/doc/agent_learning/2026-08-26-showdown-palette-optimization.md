# Showdown Palette Optimization v002 — Lições Medidas

Data: 2026-08-26
Escopo: `local_training_fixture` (`_agent_training/[ESTUDO]_mugen_sff_showdown_v1`)
Status: `ready_for_aaa=false` (permanece lab; ganho real medido e selado)

## O que foi feito

1. **Otimizador global de subpaletas** (`tools/palette/optimize_showdown_palettes.py`):
   Lloyd tile-aware no espaço 9-bit do Mega Drive. Lê os pixels visíveis do
   mundo UMA vez, redecide pids com a MESMA função do exporter e refita os
   15 slots de cada subpaleta por k-means ponderado com snap para a grade MD.
   Slot 0 fixo = backdrop. Determinístico.
2. **Patch mínimo no exporter**: `SHOWDOWN_PALETTES_JSON` seleciona paletas
   otimizadas; fallback manual intacto; `palette_source` registrado no report.
3. **Bloco VLAB portado** para `runtime_probe.c` do viewer (24 words métricas +
   64 CRAM em SRAM 0x200) — o selador canônico exigia e o viewer nunca teve.
4. **A/B no mesmo emulador**: duas ROMs (manual vs otimizada), mesmo BlastEm
   Linux, dois bundles SELADOS sem blockers.

## Números oficiais

| Métrica | Manual | Otimizado v002 |
|---|---|---|
| `nearest_color_remaps` (exporter) | 235.880 | **205.283 (−12,97%)** |
| unique tiles / limite global | 2870 / ok | 2872 / ok |
| pixels alterados na tela (A/B) | — | 42,85% |
| slots CRAM diferentes | — | 14/64 (Δmédio 1,6, Δmáx 12) |
| FPS janela BlastEm | — | 59,2 |
| bundle de evidência | minimal (junho) | **sealed, zero blockers** |

## Falhas capturadas (as que valem ouro)

### 1. Literal mágico no lugar da constante (`plane_id == 0`)
O skip de transparência testava `PLANE_BG_B`(=0) em vez de `PLANE_BG_A`.
Pixels transparentes viraram cor preta nos histogramas: universo inflou de
1,84M para 2,95M px e a primeira "otimização" piorou o número oficial
(285k > 236k). **Lição:** constante importada existe para ser usada em TODAS
as comparações; literal numérico ao lado de constante é bug latente.

### 2. Simulador ≠ artefato oficial
Minha simulação dizia −78%; o exporter oficial deu −13%. A diferença veio do
bug acima + divergência residual entre minha decisão pid simulada e a real.
**Lição:** métrica de campanha é a do artefato oficial; simulador só orienta.

### 3. Gap MDRT×VLAB — evidência "minimal" tinha causa em código
O viewer gravava heartbeat MDRT mas ninguém escrevia o bloco VLAB que o
selador consome. Junho ficou `blastem_minimal` não por falta de flag, mas por
gap de implementação. **Lição:** status degradado persistente merece autopsy —
era uma chamada ausente.

### 4. Contagem de cores entre hosts não compara nada
Screenshot de junho (BlastEm Windows): 23.743 cores "distintas" (shader
interpolando). Hoje (Linux): 604. Hardware real emite ≤61. **Lição:** A/B
visual exige MESMO emulador + MESMA ROM base; contagem de cores filtrada é
ruído de pipeline de vídeo, não dado.

## Limites restantes honestos

- Bandas BG_A forçam pid por posição (sem escape por erro como BG_B) —
  próximo degrau candidato, exige medir impacto em unique_tiles/margem VRAM
  (1087/1151 continua apertado).
- `code_loaded_tiles_unmeasured` segue aberto (gate validate_resources).
- Performance sustentada: claim `unproven` (1 snapshot de 59,2 fps).

## Próximo degrau sugerido

Instrumentar contagem de tiles carregados via DMA queue no runtime (fecha o
hard limit) e só depois avaliar escape por erro nas bandas BG_A.

## Adendo P2 (mesmo dia): code_loaded_tiles MEDIDO

- Bloco TSTR novo na probe (SRAM 0x300, 8 contadores u32) + leitor Python.
- Sessao selada `…120420Z…`: 1.157 tiles por passe, pico residente
  1157/1190 -> **margem real de 33 tiles (2,77%)**, nao os 64 estimados.
- Licao: `resetTileCache()` por passe significava que a "folga" antiga era
  media/estatica; pico real so aparece com contador dentro do acquire.
- Consequencia: P3 (varredura de cantos) e agora gate critico antes de
  qualquer expansao de janela ou animacao.

## Adendo P3 (mesmo dia): cantos seguros, passe dinamico nao tanto

- Varredura centro+4 cantos (TSTR v2): pior canto SE = 1105/1190 (folga 7,1%).
- MAS o passe dinamico da demo (frames animados + pan continuo) atingiu
  1157/1190 — folga real de operacao e 2,77%, nao a 7% dos cantos estaticos.
- Licao: estresse por posicoes extremas NAO substitui telemetria da operacao
  viva; o pior caso morou no caminho normal, nao nos cantos. Os dois numeros
  so apareceram porque TSTR acumula max global E picos por parada.
- Decisao registrada: P3b (janela menor ou LRU) trava P6.

## Adendo P3b (mesmo dia): o soak corrigiu minha propria interpretacao

- Hipotese que eu publiquei no adendo P3 ("passe dinamico da demo atingiu
  1157") estava ERRADA. Soak de 420s: contadores congelados pos-varredura —
  demo estatica nao re-streama nada em idle.
- O 1157 era o passe de RESTAURACAO para (224,256), posicao padrao — apenas
  mais um passe estatico, o maior de todos os medidos.
- Licao dupla: (1) hipotese sobre causa sem soak vira narrativa; o soak de
  sessao longa e a sonda barata que desmente. (2) max_resident acumulado
  entre capturas diferentes NAO identifica qual passe foi o autor — por isso
  TSTR v2 agora grava picos POR parada com mascara.
- Estado final honesto: margem default = 33/2,77% estavel; risco de overflow
  so existe quando P6 ligar animacoes; gate quantificado no plano (P3b).

## Adendo P4 (2026-08-29): escape BG_A + re-otimização

- Bandas BG_A forçavam pid por posição Y; BG_B já tinha escape por erro 1.45×. P4 replicou escape no BG_A.
- Resultado oficial exporter: manual com escape 184.078 vs otimizado 175.699 → −4,5% adicional; vs baseline original 235.880 → −25,5% acumulado.
- Margem VRAM pós-mudança: 38 tiles (vs 33), pior canto 1106, tudo dentro; método validado sem regressão.
- Lição: ganho de fidelidade sem custo de VRAM quando bandas são aproximação nossa, não característica original MUGEN.

## Adendo P5 (2026-08-29): performance sustentada medida

- Soak 120s selado (…155104Z…): VLAB 32 samples, 0 over_budget_frames, max_cpu 88, p50=82 p95=88 p99=88 (MDRT samples 31 vals).
- Claim honesto: proven_for_sample_window (32 amostras); ampliar janela amostral em P6 se carga subir.
- Método: captura longa + parsing SRAM MDRT/VLAB em analysis/p5_performance_report.json.

## Adendo P6 (2026-08-29): animação SFF medida e REPROVADA como AAA (crítico ativo)

- Habilitado `FRAME_ANIMATION_ENABLED=1` interval 45f: animação VISÍVEL (burst 61% pixels mudam entre frames), mas soak 120s prova custo:
  TSTR overflow=7, VLAB over_budget=15 frames, max_cpu 409 (unidade probe).
- Veredito honesto: reload completo por frame NÃO é AAA — exige streaming incremental (delta entre mapas) + double-buffer.
- ROM corrente revertida para `FRAME_ANIMATION_ENABLED=0` para manter bundles selados sem overflows; evidências P6 guardadas como material de aprendizado.
- Próximo incremento AAA real: implementar diff incremental de tiles entre frames e medir novamente via TSTR per-frame.

## Adendo P6b (2026-08-29): incremental delta sem eviction — REPROVADO

- Incremental sem reset: DMA −33% mas cache acumula união dos frames; 1190→121 overflows (piora), 1400→7 overflows.
- Lição: workaround parcial sem eviction troca um gargalo por outro; AAA exige eviction por época.

## Adendo P6d (2026-08-30): eviction por época — overflow zerado, CPU ainda estoura

- Implementado sSlotToGlobal + sNeeded + eviction do slot não usado na nova janela; DMA_QUEUE.
- Soak 120s: overflow 121→0 ✅, max_res 1190/1190, mas over_budget 15/32, max_cpu 317.
- Lição: eviction resolve VRAM, mas custo CPU do upload por frame ainda estoura budget; próximo é throttle/split.

## Adendo P6e (2026-08-30): throttle 90f — over_budget 15→7 (-53%)

- Interval 90f + eviction + DMA_QUEUE: soak 120s overflow 0 ✅, over_budget 7 (antes 15), max_cpu 249.
- 120f piora (8), 90f é melhor compromisso; próximo é split de uploads em múltiplos VBlanks para zerar.

## Adendo P6f (2026-08-30): split DMA 16/frame — piora over_budget

- Split 16 tiles/frame + eviction: over_budget 7→11, max_cpu 249→299.
- Lição: overhead de queue + tilemap updates por frame supera economia de DMA; próximo é cachear sTileOpacity/sNeeded.

## Adendo P6g (2026-08-30): sweep espalhado — over_budget 7→8 (piora leve)

- Espalhar sweep 1/frame reduziu pico no enter mas adicionou overhead de 5 frames extras; over_budget subiu.
- Lição: distribuir inicialização não compensa custo de manter lógica de sweep ativa por mais tempo.

## Adendo P6h (2026-08-30): precompute NEUTRO — custo dominante é re-upload full-window

- precomputeOpacityTable não moveu over_budget (8/32, max 250) porque o cache lazy já estava quente nos ciclos repetidos.
- Verdade dura: manter animação + eviction em todas as configs testadas (45f/90f/120f, split, spread, precompute) fica em 7-8 over_budget.
- Cache é PASS (0 overflow). Animação AAA verdadeira exige enviar só a região mudada (dirty-region delta), não reenviar 41x29 tiles + 2 tilemaps por tick.
- Default verde fixado: animation OFF = 0 overflows / 0 over_budget / max_cpu 89.

## Adendo P6i (2026-08-30): dirty-region NEUTRO — frame-swap é difuso

- VDP_setTileMapDataRect sub-rect no tick: max_cpu 250→243 mas over_budget segue 8.
- Causa: animação SFF (bg2) espalha mudança por quase toda a janela, então o retângulo sujo ≈ full-window.
- Lição: dirty-region só ajuda quando a mudança é localizada; para animação de camada integral, a otimização certa é jogar o trabalho no VBlank (scroll/tilemap no VBlank vs CPU).

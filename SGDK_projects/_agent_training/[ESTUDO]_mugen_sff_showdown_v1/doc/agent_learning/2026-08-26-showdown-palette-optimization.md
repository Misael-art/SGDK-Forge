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

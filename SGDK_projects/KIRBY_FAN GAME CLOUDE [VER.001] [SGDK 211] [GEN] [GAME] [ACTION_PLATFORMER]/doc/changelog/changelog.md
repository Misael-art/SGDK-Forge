# Changelog Canonico - KIRBY_FAN GAME CLOUDE [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

## Estado Inicial

- projeto bootstrapado a partir do wrapper central
- documentacao minima materializada
- scene regression declarada em `doc/scene-regression.json`
- companion inicial esperado em `doc/scene-contracts.json`

## 2026-09-02 - v05_visual_bitmap_temporal

- Produzido `out/forward_test_v05_visual_bitmap_temporal/` com 16 fontes bitmap independentes, duas hipóteses por ação, quatro strips separados (`idle`, `run`, `inhale`, `jump_float`), timing VBlank e evidências offline. O pouso recebeu fonte própria; não há duplicação de fonte entre quadros selecionados e v04 não alimentou pixels.
- Procedência declarada como `ai_generated` / `visual_generation_tool`, com `producer_record` separado e hash-bound por ação. A geração referenciada foi bloqueada pelo filtro da ferramenta; o pacote registra a rota textual derivada do r1 sem alegar referência direta.
- O pacote não foi promovido a `res/`. Os validadores por strip retornam `error` por ausência deliberada de lineart nativa separada; o agregado também permanece `error`, `maximum_proven_claim=none`, pois a revisão cega não reconheceu as quatro ações com confiança mínima e os princípios estão `needs_review`.
- Budget, 320×224, pivot/contact, delta, silhueta, nearest scales, paleta, tiles, metasprite, DMA e scanline foram persistidos como diagnóstico offline. Não houve build, ROM, runtime, áudio ou BlastEm para v05.

## 2026-08-31 - nexialist_visual_nucleus_v01

- Task: primeiro ciclo de direção visual para Vegetable Valley; nenhum arquivo em `res/` alterado.
- Diagnóstico: `art_diagnostic.py` detectou `2_res_inadequate_check`; 22 ativos legíveis/0 ausentes/0 blockers de build e 78 fontes em `data/`.
- Persistidos três candidatos autorais gerados com `Codex built-in image_gen`: painel de rotas, model sheet revisado e cena-dourada. Prompts completos, hashes SHA-256 e status `visual_source_candidate` registrados no pacote `rascunho/nexialist_visual_nucleus_v01/`.
- Reconciliados `visual_delivery_gate_report.json`, `art_gameplay_direction_gate.json` e `project_methodology_manifest.json` com o estado real; claims `critical_motion` e `modular_boss` seguem required e bloqueados por evidência futura, `road_physics` é `not_applicable`.
- Criado `doc/asset_provenance_manifest.json` declarando os 22 símbolos visuais ativos como placeholders procedurais; auditoria de proveniência passou sem blockers.
- Entregues `layer_plan.json`, `palette_contract.json`, `budget_preliminary.json`, painel comparativo e gate humano. Medição VDP offline: 12 links/4 por linha (base), 20 links/7 por linha (degrau seguinte), stress 336/320 pixels (overflow medido).
- Teto honesto: `visual_source_candidate`; sem promoção, sem build novo, sem ROM ou BlastEm para a direção nova.
## 2026-06-03T10:55:11.3513283-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_brand_fx_tiles -> v001 (res/branding/brand_fx_tiles.png)
  - img_brand_engine_logo -> v001 (res/branding/brand_engine_logo.png)
  - img_brand_author_logo -> v001 (res/branding/brand_author_logo.png)
  - img_brand_project_logo -> v001 (res/branding/brand_project_logo.png)
  - img_brand_presents_text -> v001 (res/branding/brand_presents_text.png)
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=10
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, changelog_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: report_older_than_rom

## 2026-06-03T10:55:35.2022830-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=7
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao

## 2026-06-03T10:56:07.3006878-03:00 - branding_sequence_xgm2_probe

- Task: branding_sequence_xgm2_probe
- Skills: sgdk-build-wrapper-operator, sgdk-runtime-coder, scene-state-architect, megadrive-vdp-budget-analyst, xgm2-audio-director
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=7
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Fase 0 branding: preserved existing brand_* PNG baseline, added WAV XGM2 cue declarations/assets, integrated runtime_probe boot/tick, generated explicit blocked visual_delivery_gate_report.

## 2026-06-03T11:09:40.7744181-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=9
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T11:10:00.1427886-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, emulator_evidence_stale, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale

## 2026-06-03T11:11:36.1661598-03:00 - branding_sequence_xgm2_probe_capture

- Task: branding_sequence_xgm2_probe_capture
- Skills: sgdk-build-wrapper-operator, sgdk-runtime-coder, scene-state-architect, megadrive-vdp-budget-analyst, xgm2-audio-director
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, emulator_evidence_stale, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale
- Notes: Fase 0/branding: preserved brand_* PNG baseline, added XGM2 WAV cues, integrated MDRuntimeProbe boot/tick, reduced inactive line-scroll uploads, rebuilt ROM SHA256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, captured TargetScene 0 in BlastEm with screenshot/save.sram/runtime_metrics partial; one CPU budget spike remains at frame_index 128 so performance gate stays blocked.


## 2026-07-29 - sessao_001_fase0_parcial

- Task: FASE 0 (contrato) + FASE 3 (harness), ambas parciais
- Projeto criado via `new_project.sh` com PATH corrigido; nome validado `valid`
- `doc/project_context_manifest.json` classificado `aaa_game` / `vertical_slice`;
  `validate_project_context.ps1` = `status=ok blockers=0`
- Rota de build em Linux VERIFICADA: `build_sgdk_wine_bridge.sh` -> `wine_bridge_status=buildado`,
  `out/rom.bin` 262144 bytes (com o probe)
- `tools/sgdk_wrapper/build.sh` e `new_project.sh` documentados como QUEBRADOS em Linux
  (PATH de `$GDK/bin` sombreia coreutils com `cp.exe`/`mkdir.exe`/`rm.exe` sob Wine).
  NAO corrigidos: sao canonicos e exigem aprovacao humana.
- Rota de captura VERIFICADA: `capture_blastem_evidence_linux.sh`, BlastEm a 60.3 fps,
  gate semantico de screenshot `passed`
- `doc/ARCHITECTURE.md` escrito (contrato mestre): decisao de 5 camadas via line-scroll
  em BG_B, tabela de faixas de H-int com dono unico, cotas fixas de sprite,
  orcamento do boss Whispy Woods em 58 sprites, numeros de game feel
- Probe VLAB portado do projeto Celestial Chase Revive e ligado ao boot/loop;
  2 bundles selados com `status: sealed blockers: []` incluindo `vdp_dump` e `runtime_metrics`
- `tools/harness/gates.py` operacional com 13 gates; `frametime.py` e `probe_format.py` escritos
- Primeira medicao real: 21/61 cores, 0 CRAM ilegal, 0 frames acima do budget,
  cpu p99=42/100, `vblank_idle=171` scanlines/frame
- `doc/art/AI_IMAGE_PROMPT_PACK.md` + `image_request_manifest.json`: 7 pedidos R1
  para agente externo de geracao de imagem, com grade RGB333 explicita
- `doc/10-memory-bank.md` SOBRESCRITO: continha historico operacional do template
  (branding intro, ROM 22a80b7c de 262144 bytes, build_v002, datas de mai/jun 2026).
  Nada disso pertencia a este projeto.
- NAO ENTREGUE nesta sessao: `doc/VRAMMAP.md`, `doc/PALETTES.md`, `doc/SOUNDMAP.md`,
  `doc/17-audio-design.md`, `tools/harness/build_and_capture.sh`,
  `tools/harness/imagediff.py`, playtest scriptado, e todo o codigo de jogo.
  Causa: limite de sessao da API atingido; 3 subagentes terminados prematuramente.

## 2026-07-29 - r1_source_art_delivery_codex

- Task: gerar e documentar os 7 pedidos de `doc/art/AI_IMAGE_PROMPT_PACK.md`.
- Delivery: 11 PNGs normalizados (R1-01..R1-07, incluindo `layers.png`, `above_below.png` e `distortion.png`) em `data/source_art/r1/`; os 11 originais de geracao foram preservados ao lado para auditoria de proveniencia.
- Validation: canvas previsto, sem alpha, 10-15 cores nas folhas e 30-41 nos estudos de cena; normalizacao por nearest-neighbor e RGB333. Hashes, prompts verbatim e notas de autocritica em `data/source_art/r1/r1_delivery_manifest.json`.
- Status: `source_candidate_pending_human_judgment`; `promotion_allowed=false`; nenhuma imagem foi colocada em `res/`, nenhum build ou emulador foi usado como alegacao de arte final.
- Signature: Codex.

## 2026-07-29 - r1_art_judged_r2_issued

- Task: julgamento da rodada R1 de arte conceitual entregue por agente externo (Codex)
- 7 pedidos / 11 PNGs normalizados recebidos em `data/source_art/r1/`
- Metodo: medicao programatica com PIL+numpy sobre o PNG entregue, nao inspecao visual
- Gate de legalidade RGB333: **7/7 pass, 0.00% de pixels ilegais em todos os 11 entregaveis**
- Gate de teto de cores: 7/7 pass
- Vereditos: 3 aprovados sem correcao (r1-05, r1-06, r1-07), 3 aprovados com correcao
  (r1-01, r1-02, r1-04), 1 REPROVADO (r1-03, chave de transparencia)
- r1-03 reprovado: fundo dominante medido `(255,0,219)` 56.4%, com tres magentas coexistindo;
  a chave especificada `(255,0,255)` respondia por so 4.6%
- r1-02 defeito medido: camada 5 (primeiro plano) com luminancia media 0.370 contra 0.340
  da camada 4 (terreno) — colapsam em escala de cinza, e a camada 5 passa na frente do heroi
- r1-01: teste real a 28px aprovou 3 de 4 poses; `floating` colapsa. Meio-tom rosa medido
  em 0.58% da area (alvo 8-12%)
- CORRECAO DE ERRO DO DIRETOR: a rampa de rosa do protagonista especificada no pacote R1
  era salmao, nao rosa chiclete. Substituida por rampa de 5 tons com lean de magenta.
  Registrada em `failure_patterns.md`
- Emitido `doc/art/R1_VERDICT_AND_R2_PACK.md` com 4 correcoes cirurgicas (R2-01..R2-04),
  todas com criterio de aceite medivel. Nenhuma arte nova pedida.
- `doc/art/image_request_manifest.json` atualizado com veredito por pedido
- Nenhuma entrega promovida para `res/`. Status maximo segue `source_candidate`.

## 2026-07-29 - r2_surgical_art_corrections_applied

- Task: aplicar as quatro correcoes do veredito R2 sem sobrescrever R1 e sem promover arte.
- R2-03 (bloqueador): `r2-03/concept.png` re-keyed por substituicao RGB exata; `#ff00db` e `#db00db` = 0 pixel, chave `#ff00ff` unica, 13 cores totais e duas vagas para flash de dano.
- R2-02 (bloqueador): `r2-02/layers.png` alterou apenas y=730..895; luminancia da camada 5 = 0.269899 e diff de pixel em y<730 = 0.
- R2-01: pose floating localizada corrigida, rampa rosa chiclete aplicada e meio-tom `#ff92b6` em 10.001950% dos pixels visiveis da pose.
- R2-04: removidas as duas cores de franja proibidas (`#db00db`, `#db24b6`), ambas com 0 pixel; 13 cores totais.
- Evidencia rastreavel: `data/source_art/r2/r2_delivery_manifest.json`, `r2_mechanical_validation.json` e notas por correcao; assinatura Codex.
- Nenhuma arte foi promovida para `res/`, nenhum build/ROM/emulador foi alegado para estes conceitos.

## 2026-07-29 - r3_02_layer5_palette_noise_collapsed

- Task: executar somente R3-02 de `doc/art/R2_VERDICT_AND_R3_PACK.md`; R2-01, R2-03 e R2-04 permaneceram fechados e intocados.
- Colapsadas apenas as cinco cores de ruido declaradas de `r2-02/layers.png` no vizinho RGB mais proximo ja existente; desempates sao lexicograficos e estao no relatorio.
- Resultado: 47 -> 42 cores (teto <=45), zero cores novas, luminancia da camada 5 = 0.270037 (janela 0.23-0.28), diff de pixel nas camadas 1-4 = 0 e 0 pixels ilegais na grade RGB333 do projeto.
- Evidencia rastreavel: `data/source_art/r3/r3_delivery_manifest.json`, `r3_validation_report.json` e `r3-02/notes.md`; assinatura Codex.
- Nenhum asset foi promovido para `res/` e nao ha alegacao de ROM/emulador.

## 2026-07-29 - r2_art_judged_r3_issued

- Task: julgamento da rodada R2 (4 correcoes cirurgicas) por verificacao independente
- R1 preservado: hashes de `data/source_art/r1/` inalterados
- Gate de legalidade RGB333: 4/4 pass, 0.00% de pixels ilegais
- R2-01 APROVADO: rampa de rosa canonica adotada 5/5 tons, zero tom salmao restante;
  pose floating corrigida com prova mensuravel (largura da silhueta no topo 6->19 px
  no downscale real para 28px); 12/15 cores
- R2-03 APROVADO: chave unica `(255,0,255)` 63.01%; `(255,0,219)` e `(219,0,219)` = 0 px;
  13/13 cores; metodo verificado como exact RGB replacement sem resampling
- R2-04 APROVADO: franja proibida = 0 px; chave unica; 13/13 cores
- R2-02 APROVADO NA INTENCAO, REPROVADO NO TETO: luminancia da camada 5 corrigida de
  0.3703 para 0.2496 (na janela) e camadas 1-4 com pixel diff EXATAMENTE 0, mas a paleta
  foi de 39 para 47 cores contra teto de 45
- Causa raiz do R2-02 autodeclarada pelo Codex no proprio relatorio: 4454 px de
  micro-dither para caber na janela de luminancia apos snap na grade discreta.
  5 das 8 cores novas sao ruido (<0.03% cada)
- CORRECOES DE PROCESSO DO DIRETOR (segunda rodada consecutiva em que o erro e meu):
  1. formula de luminancia nao estava especificada (0.299/0.587/0.114 minha vs sRGB deles);
     canonizada como sRGB `0.2126/0.7152/0.0722`
  2. criterio de luminancia em float sobre grade discreta forca dithering; migrado para
     "remapear em degraus de paleta existentes, zero cores novas"
  3. "area do corpo" ambiguo no criterio de meio-tom
- Emitido `doc/art/R2_VERDICT_AND_R3_PACK.md` com 1 item (R3-02)
- Nenhuma promocao para `res/`. Status segue `source_candidate`.

## 2026-07-29 - r3_verified_art_loop_closed

- Task: verificacao de R3-02 e encerramento do loop de arte do escopo R1
- R3-02 APROVADO por medicao independente (formula canonica sRGB):
  42 cores (teto 45), 0.00% ilegal, as 5 cores de ruido removidas, zero cores novas
  vs R2, camadas 1-4 com pixel diff EXATAMENTE 0, luminancia da camada 5 = 0.2579
- Escada de valor final, agora MONOTONICAMENTE DECRESCENTE do fundo para a frente:
  ceu 0.7339 / montanhas 0.5024 / colinas 0.4526 / terreno 0.3401 / primeiro plano 0.2579.
  Registrada como referencia normativa de valor para o futuro `doc/PALETTES.md`.
  Ponto mais fragil: gap camada2->camada3 = 0.0498, separado tambem por saturacao.
- LOOP DE ARTE ENCERRADO pelo criterio do proprio brief ("/loop ate o critico hesitar
  ou errar"): nas tres ultimas rodadas os defeitos foram dos criterios do diretor
  (janela de luminancia em float sobre grade discreta, formula nao especificada,
  "area do corpo" ambigua, rampa de rosa errada no contrato), e nenhum foi da arte.
- Estado final da arte: 7 pedidos em `source_candidate`, 100% legais em RGB333.
  Nenhuma promocao para `res/`. Nenhuma arte vista rodando em ROM — pela regra de ferro
  do workspace, ainda nao existe como asset.
- GARGALO TRANSFERIDO para `doc/PALETTES.md` e `doc/VRAMMAP.md`, que sao trabalho do
  diretor e nao do agente de imagem. `PALETTES.md` nasce com 4 entradas obrigatorias
  vindas deste loop (ver `doc/art/image_request_manifest.json` -> loop_closure).

## 2026-07-29 - fase0_palettes_vrammap_gates

- Task: fechar 2 dos 4 documentos de contrato da FASE 0 e ligar os gates que dependiam deles
- Aprendizado registrado antes de prosseguir: `success_patterns.md` +4 entradas,
  `failure_patterns.md` +10 no total da sessao. `audit_project_learning.ps1 -Mode Capture`
  rodou: 14 licoes, 10 candidatas, `canonical_promotion_performed: false` (correto)
- `doc/PALETTES.md` escrito:
  - layout de CRAM `[VERIFICADO]` em `pal.h:18-26`: `0000 BBB0 GGG0 RRR0`,
    teste de legalidade `(word & ~0x0EEE) == 0`
  - **DECISAO DE SHADOW/HIGHLIGHT: ligado globalmente no jogo inteiro, todo tile de
    fundo autorado com priority=1.** Motivo: o vortex de inalar e o verbo central e
    precisa existir em toda cena; trocar S/H por cena tornaria a arte nao portavel
  - custo declarado: bit de prioridade dos tiles gasto (layering por ordem de plano),
    e PAL3[14]/PAL3[15] reservados como operadores
  - **TETO DE CORES CORRIGIDO DE 61 PARA 58**: 64 - 4 transparentes - 2 operadores
  - PAL0-PAL3 com papel fixo; PAL2 travada na rampa canonica vinda do loop de arte
  - escada de valor de 5 camadas importada como normativa
  - teto conservador de 1 word de CRAM por faixa de H-int enquanto nao houver medicao
  - 7 gates especificados (P1-P7), 2 implementados
- `doc/VRAMMAP.md` escrito:
  - mapa de 64 KB byte-exato, soma conferida em 65536, **zero byte nao contabilizado**
  - plano travado em 64x32; 64x64 custaria 256 tiles (25% do orcamento de fundo).
    Troca justificada: CPU e abundante (171 scanlines idle), tile e escasso
  - orcamento de DMA `[VERIFICADO]` em `dma.h:172`: **7.2 KB NTSC / 15 KB PAL**.
    Alocado com 43% de uso e 57% de folga; HScroll e sprite list nunca sao cortados
  - alocacao alvo de tile para 5 cenas; fase 2 (lago) identificada como maior risco
  - 5 alavancas de recuperacao com preco declarado; alavanca 1 (recuperar a fonte,
    +96 tiles) reservada para a fase 2
  - 6 gates especificados (V1-V6), 3 implementados + 1 novo nesta sessao
- `tools/harness/gates.py` corrigido:
  - `max_simultaneous_colors` 61 -> **58**, com a aritmetica citada no comentario
  - `max_screenshot_colors` 61 -> **174** (58 x 3): com S/H ligado o screenshot
    legitimamente triplica a contagem de cor. O comentario original do harness
    ja antecipava isso e agora existe a decisao que resolve
  - novo gate `plane_size_locked` (V4): pega regressao silenciosa de tamanho de plano
- Resultado medido no bundle `probe_scene_demo`: **14 gates, VERDICT: PASS,
  0 hard failures, 1 warning honesto** (`sprites_observed` vacuo, nao ha sprite ainda).
  `vram_tile_budget` passou de `warn` para **PASS**; `plane_size_locked` **PASS**
- Blockers resolvidos: `vrammap_ausente`, `palettes_ausente`, `r1_julgamento_humano_pendente`
- Blocker novo declarado: `probe_nao_exporta_sh_prioridade_dma` — os gates P4/P5/V6
  nao podem existir sem instrumentar o probe. Registrado, nao fingido.

## 2026-07-29 - fase0_completa_soundmap_audio_gates

- Task: fechar a FASE 0 (4o e ultimo documento de contrato) e implementar os gates
  de audio que nao dependem do probe
- `doc/SOUNDMAP.md` escrito:
  - **XGM2 escolhido, e a decisao NAO era obvia.** `[VERIFICADO]` XGM v1 (`xgm.h:9`)
    tem 4 canais PCM a 14 kHz; XGM2 (`xgm2.h:9-10`) tem 3 canais a 13.3/6.65 kHz.
    O XGM v1 ganha em canais e taxa. **Fator decisivo: so o XGM2 tem controle de
    volume de FM/PSG (`bin/rescomp.txt`), sem o qual DUCKING NAO EXISTE**
  - reforcado por prior art medido nesta stack (Celestial Chase visual benchmark:
    `max_xgm2_cpu_load=92`, `max_dma_wait=0`, `missed_frames=1/1363`)
  - custo declarado: sobram 2 canais PCM para SFX, nao 3 (PCM1 e da musica)
  - BRIEF CORRIGIDO: taxa de PCM e 13.3 ou 6.65 kHz (`bin/xgm2.txt`), nao
    "14-22 kHz" como o brief pedia. Nao e escolha nossa
  - **gate #5 do brief satisfeito por ARQUITETURA, nao por politica:** SFX sai
    todo por PCM; FM/PSG pertencem integralmente ao driver de musica
  - 8 faixas de prioridade (1-15) com supressao de 4 frames para morte de inimigo,
    e fila de 1 slot para prio >= 11 (nunca descartada silenciosamente)
  - orcamento de PCM em 384 KB; 10 samples ganham PCM, 5 sons ficam sinteticos
  - **restricao imposta ao resto do codebase: DMA <= 4096 B/frame**, mais apertado
    que o teto de 7.2 KB do VDP de proposito, porque o teto real antes do XGM2
    engasgar e `[NAO MEDIDO]`
  - 7 gates automatizaveis + checklist humano EXPLICITO para o que script nao julga
- `doc/17-audio-design.md` escrito: tensao Koshiro-vs-Kirby resolvida ("engenharia
  de Koshiro, melodia de Kirby"; inimigo declarado e o "FM fino"). 8 faixas em 99 KB
  de 128. 15 SFX com a informacao que cada um carrega. **Fase 2 usa UMA faixa** com
  filtragem por volume na linha d'agua — possivel so por causa do XGM2. Pipeline
  `.vgm` -> rescomp `XGM2` verificado; multi-track para as 3 fases por economia de PCM.
  Normalizacao a -3 dBFS para nao clipar com 2 PCM somados
- `tools/harness/audio_gates.py` criado: gates A1/A2/A3/A6/A7, estaticos, sem probe
- **O gate encontrou 11 violacoes REAIS no codigo do template** na primeira execucao:
  10 chamadas diretas a `PSG_*` (`src/system/audio.c`, `src/scenes/scene_branding.c`)
  e 1 uso de `SOUND_PCM_CH1`. Nenhuma e codigo de jogo
- Tratamento: `tools/harness/audio_gate_baseline.json`. **Divida rastreada, nao
  silenciada** — o gate falha em qualquer violacao NOVA e reporta a herdada como
  warning com owner e condicao de expiracao. Verificado injetando uma violacao nova
  em `src/system/input.c`: gate deu FAIL com 1 hit novo + 10 baselined; teste revertido
- Resultado: `audio_gates_status=pass`, 5 gates hard PASS, 3 warnings honestos
- Rebuild de verificacao: `wine_bridge_status=buildado`
- FASE 0 COMPLETA. Blocker `soundmap_ausente` resolvido. FASE 1 desbloqueada.

## 2026-07-30 - fase1_nucleo_kirby_5_camadas

- Task: FASE 1, nucleo — Kirby jogavel dentro do parallax de 5 camadas
- Modulos novos: `src/systems/raster.c` (dono unico de scroll+paleta+raster, UM
  unico callback de H-int no jogo inteiro), `src/entities/kirby.c` (fisica em
  fix16: coyote 4, jump buffer 5, hit-stop 4, float sustentado),
  `src/systems/stage_map.c`, `src/scenes/scene_stage.c`
- `data/builders/build_placeholder_art.py`: arte provisoria que JA obedece o
  contrato de cor (grade RGB333 validada no gerador, paletas canonicas de
  PALETTES.md, escada de valor verificada monotonica na geracao)
- Tilesets apos dedup do rescomp: ceu 0 tiles, montanhas 20, colinas 92,
  terreno 8. Muito abaixo do orcamento de 1004
- **GATES: 14 PASS, 0 hard failures, 0 warnings.** O warning `sprites_observed`
  desapareceu porque agora existem sprites (pico 5/80, 4/20)
- Medido na cena STAGE: 40/58 cores, 0 CRAM ilegal, 152/174 cores de screenshot,
  cpu p99 39/100, 0 frames acima do budget
- **PARALLAX PROVADO POR MEDICAO:** duas capturas em pontos diferentes do pan,
  correlacao cruzada por banda. Camada 2 (montanhas) -15 px, camada 3 (colinas)
  -40 px. Razao medida 1:2.67 == razao de projeto 3/8. CONFERE
- NAO PROVADO: deslocamento da camada 4 (terreno). Correlacao deu +42 px,
  inconsistente com a camera inferida (~118 px). O padrao xadrez e periodico e
  aliasa. Registrado como medicao devida, nao como numero
- DESCOBERTA DE RUNTIME 1: o gradiente de ceu deve dirigir o BACKDROP (CRAM 0),
  nao um indice de tile. Dirigindo o indice 1, o backdrop ficava na chave magenta
  e a faixa das montanhas saia magenta. Com o backdrop, o ceu custa 1 entrada de
  CRAM e ZERO tiles — melhor que o previsto em PALETTES.md §4.1
- DESCOBERTA DE RUNTIME 2: secao `sprite` = 104 scanlines/frame para apenas 5
  sprites. Maior fatia da cena e parece alta demais. NAO investigado; registrado
  como suspeita medida
- API: `fix16ToInt` esta deprecado no SGDK 2.11 e o compilador REJEITA com erro.
  Substituido por `F16_toInt`
- NAO ENTREGUE da FASE 1: titulo proprio, inimigos, inalar, copy abilities, boss,
  game over/continue, audio, playtest scriptado. `INTRO_PAN_FRAMES=900` e
  provisorio (esticado para a captura cair dentro do pan)

## 2026-07-30 - fase1_inimigos_inalar_e_bug_de_cram

- Task: inimigos + inalar + copy ability, e as duas investigacoes que eu havia recomendado
- INVESTIGACAO 1 (secao `sprite` = 104 scanlines): **hipotese REFUTADA por medicao.**
  Teste de estresse com 25 sprites -> secao caiu para 53; com 9 sprites -> 43.
  A secao e pico ruidoso e NAO escala com contagem de sprite. O que escala e
  `cpu_load_p99` (39% -> 60% -> 43% -> 51%). Nao havia custo a otimizar
- ACHADO NOVO do estresse: com 24 tufos numa unica fileira horizontal,
  `sprites_per_frame` 25/80 PASSOU mas `sprites_per_scanline` 24/20 **FALHOU**.
  Para uma faixa horizontal de sprites o limite que morde e o POR SCANLINE.
  Cota da camada 5 restaurada para os 8 documentados, com o motivo medido no codigo
- INVESTIGACAO 2 (deslocamento da camada 4): 4 metodos de forense de screenshot
  falharam (correlacao aliasou em padrao periodico, deteccao de borda divergiu,
  centroide rosa pegou faixas do ceu). **Conclusao: a ferramenta esta errada.**
  A medicao exata exige instrumentar o probe com `cameraX`. Registrado como devido
- Descoberta lateral: as cores do screenshot NAO estao na grade RGB333; o BlastEm
  usa curva de DAC realista. Legalidade de cor so pode ser verificada no CRAM
- Novos modulos: `src/entities/enemy.c` + `inc/entities/enemy.h`. Pool FIXO de 6,
  estado WALK/PULLED/SWALLOWED, IA que vira em beirada e borda de plano
- Mecanica de inalar: cone a frente do Kirby (`INHALE_REACH` 72 px), inimigo e
  puxado, engolido dentro de 12 px, e o engolir CONCEDE a copy ability. Inalar
  enraiza o Kirby: o vortex e um compromisso, nao acao gratuita
- Botoes remapeados: **A = pular/flutuar, B = inalar.** C ficou com o toggle de HUD
  do template e por isso e proibido para gameplay
- BUG 1 corrigido: o pan congelava a simulacao inteira e Kirby/inimigos FLUTUAVAM.
  Agora o pan suprime apenas o INPUT; o mundo continua simulando
- **BUG 2, GRAVE, corrigido: corrupcao nao deterministica de 17 a 31 entradas
  contiguas de CRAM.** Causa diagnosticada por dump de CRAM, nao por palpite: o
  H-int escreve a porta de controle do VDP e caia no meio do flush da fila de DMA
  do SGDK em VBlank, desviando a transferencia da tabela de HScroll para o CRAM.
  Corrigido mascarando o H-int durante TODO o VBlank via `SYS_setVIntCallback`,
  re-armando em `RASTER_frameStart`. Verificado: 31 -> 17 -> **0** entradas corrompidas
- Primeiro suspeito (flash de paleta) foi REFUTADO desligando-o: a corrupcao
  persistiu. A aritmetica ja indicava (1 entrada escrita vs 31 corrompidas)
- GATES FINAIS: 14 runtime **PASS, 0 warnings** + 5 audio **PASS**.
  40/58 cores, 0 CRAM ilegal, 166/174 cores de screenshot, 15/80 sprites por frame,
  8/20 por scanline, 0 frames acima do budget, cpu p99 51/100

## 2026-07-30 - probe_instrumentado_bloco_krb1

- Task: instrumentar o probe para destravar as medicoes devidas
- Bloco proprio **KRB1 em SRAM 0x300**, 16 words, com leitor proprio.
  NAO estendi o VLAB: o selador canonico le words[24..] como paleta e acrescentar
  metrica corromperia todos os gates de cor do workspace. AGENTS.md proibe alterar
  o selador sem aprovacao humana
- Novos modulos: `inc/system/probe_stage.h` + `src/system/probe_stage.c`.
  `raster.c` publica os valores de HScroll REAIS que programou; a cena publica
  camera, atores e contadores
- **PARALLAX VERIFICADO EXATAMENTE** (o que 4 metodos de forense de screenshot
  falharam em medir): cameraX=23 -> ceu 0, montanhas -2, colinas -7, terreno -23,
  todos identicos a formula de projeto. Divida de medicao da sessao 003 quitada
- **DMA agora medido**: pico 1792 B/frame, contra limite de projeto 4096 e teto de
  hardware 7372. Abaixo da estimativa de 3176 B de VRAMMAP.md §3.1
- BUG encontrado pela instrumentacao: `VDP_clearTextArea` em cena com S/H global
  gerava 16/16 tiles de BG_A em prioridade 0 (preenche com o glifo branco da
  fonte, indice nao-zero, prioridade 0). Trocado por `VDP_clearPlane`: 16/16 -> 0
- **Gate P5 marcado PARCIAL, nao aprovado**: BG_B amostra 16 e reporta 0 violacoes;
  BG_A reporta 0 de 0 amostradas apesar do terreno estar desenhado nas linhas
  amostradas. Leituras de VRAM em BG_A retornam zero por motivo NAO DETERMINADO.
  Limitacao escrita no proprio codigo para nao ser lida como aprovacao
- `sh_enabled` prova INTENCAO, nao hardware: SGDK 2.11 nao expoe leitura do
  registro 0x0C
- Erro de processo: cirurgia repetida por regex em `scene_stage.c` embaralhou o
  arquivo (bloco de telemetria caiu em `SCENE_stageEnter`, chaves duplicadas,
  2 builds quebrados). Reorganizado por numero de linha. Para edicao estrutural,
  usar limites de funcao explicitos, nao `replace` com count=1
- Gates: 14 runtime PASS 0 warnings, 5 audio PASS, cpu p99 57/100

## 2026-07-30 - p5_resolvido_gates_krb1_e_readme

- Task: fechar a investigacao de P5 e transformar o bloco KRB1 em gates reais
- **CORRECAO DE UMA LICAO ERRADA MINHA.** Eu havia registrado que a auditoria de
  prioridade lia 0 entradas de BG_A "por motivo nao determinado", levantando
  suspeita de delay de leitura de VRAM ou restricao em display ativo.
  **Estava errado.** Diagnostico cru (words 16-19 do KRB1) provou que as leituras
  sempre funcionaram: BG_A linha 22 col 0 devolve `0xA083` = tile 131,
  prioridade 1, paleta 1. A causa real foi um `str.replace` que NAO APLICOU,
  deixando o passo de amostragem em 128 bytes (1 linha), cobrindo so as linhas
  0-15, onde BG_A esta vazio. Entrada corrigida em `failure_patterns.md`
- Segunda ocorrencia da mesma classe de erro nesta sessao (a primeira foi o bloco
  de telemetria caindo em `SCENE_stageEnter`). Licao consolidada: **verificar por
  `grep` que toda edicao por script aplicou, antes de interpretar o resultado**
- Passo corrigido para 256 bytes (2 linhas), cobrindo as 32 linhas do plano.
  **Gate P5 agora NAO VACUO e PASS: 0 violacoes de 17 amostrados (BG_A 4, BG_B 13).**
  Os denominadores conferem com a predicao a partir do layout das camadas
- `tools/harness/krb1.py`: leitor do bloco proprio, com as formulas de projeto
  espelhadas exatamente como `raster.c` as calcula (mesmos shifts inteiros)
- **4 gates novos em `gates.py`**, todos impossiveis antes do KRB1:
  `parallax_layer_speeds` (as 4 camadas contra a formula, lido da tabela de
  HScroll), `tile_priority_under_sh` (P5), `dma_peak_per_frame` (V6/A4, 1792 de
  4096 B), `shadow_highlight_intent` (soft, rotulado como intencao)
- Ambos os gates amostrados emitem AVISO EXPLICITO quando o denominador e zero ou
  a camera esta parada, porque "0 de 0" ja foi confundido com aprovacao aqui
- `tools/harness/README.md` escrito: o header do `gates.py` mandava le-lo desde a
  sessao 001 mas o arquivo nunca existiu. Separa os gates que PODEM falhar dos
  que sao invariantes estruturais, lista as armadilhas medidas (cor de screenshot
  != cor de CRAM, teto 174 por causa do S/H, secao `sprite` nao e custo por
  sprite) e o que continua sem gate nenhum
- Gates: **18 runtime PASS 0 warnings**, 5 audio PASS, cpu p99 58/100

## 2026-08-06 - playtest_scriptado_e_boss_articulado

- **Playtest scriptado** (`src/system/playtest.c` + `inc/system/playtest.h`),
  input gravado do lado da ROM. Escolhido em vez de injecao de teclas no emulador
  porque injecao depende de foco de janela, timing do X11 e polling do emulador,
  e o gate seria instavel. Tabela compilada e frame-exata e versionada
- Roda na cena 5 `APP_SCENE_STAGE_PLAYTEST`, separada da cena 4 jogavel. Cena
  separada porque o bloco de bootstrap canonico carrega so scene id, sem flags,
  e e escrito por ferramenta compartilhada que nao podemos alterar
- **Cobertura 11/11, script completo (step=17, finished=1)**. `swallow` e
  `ability` SIM, `enemies_alive` de 4 para 2: o loop inalar -> engolir -> copiar
  esta PROVADO rodando, nao apenas compilando
- Cada bit e marcado pela cena OBSERVANDO o estado acontecer, nao pelo script
  pedindo: cobertura alcancada, nao pretendida
- 2 gates novos: `playtest_coverage`, `playtest_completed`. Ambos SKIP (nao fail)
  em captura que nao seja de playtest
- **Boss Whispy Woods** (`src/entities/boss_whispy.c`, cena 6): 4 galhos x 7
  segmentos, cinematica direta com `F16_sin`/`F16_cos` em graus, zero float.
  Tronco em tiles de BG_A com custo zero de sprite. Arte placeholder em PAL3
- Medido: **39 sprites de hardware/frame**, 10/scanline, 39/58 cores
- **O boss REPROVOU o gate na primeira captura**: `zero_over_budget_frames` com
  2 frames estourados e cpu p99 87%. Risco A3 do ARCHITECTURE.md §10 real
- **Alavanca 1 da escada de degradacao do §5.1 aplicada** (interpolar e resolver
  as cadeias a cada 2 frames): cpu p99 87% -> **75%**, frames acima do budget
  2 -> **0**, pico da secao sprite 148 -> 114, veredito FAIL -> **PASS**.
  Funcionou porque a escada foi escrita ANTES do problema existir
- BUG: backdrop apontando para a chave de transparencia. Arena inteira saiu roxa
  porque com S/H global o backdrop descoberto renderiza SOMBREADO, e magenta
  pela metade e aquele roxo. Corrigido com `PAL_setColor(0, ...)`
- BUG operacional: `window_timeout` com `blastem.log` vazio. Matar o `blastem.bin`
  orfao por PID NAO resolveu — o bloqueio era instancia **flatpak** presa,
  visivel em `flatpak ps` e nao em `ps`. `tools/harness/README.md` corrigido
- `tools/harness/README.md` tambem corrigido em duas obsolescencias: listava o
  playtest como inexistente e nao tinha os gates novos na tabela

## 2026-08-06 - arena_do_boss_4_camadas

- Arena do boss ligada com o mesmo contrato de 5 camadas da fase: BG_B fatiado em
  3 bandas por HScroll, BG_A com terreno + tronco, gradiente de ceu por H-int
- **Estourou o budget como eu havia previsto**: cpu p99 75% -> **96%**,
  frames acima do budget 0 -> **19 de 32**. Falha, nao marginal
- **Resolvido por OTIMIZACAO SEM PERDA, nao por degradacao.** A camera da arena e
  estatica e `RASTER_updateScroll` reconstruia 224 linhas x 2 planos todo frame
  com valores identicos. Rebuild agora e condicional a mudanca de camera:
  **p99 96% -> 78%, frames 19 -> 0, DMA 1792 -> 896 B, render byte-identico**
- As alavancas 2 e 3 da escada de degradacao do §5.1 seguem SEM USO
- BUG: `sh_enabled=0` na arena. `PROBE_STAGE_reset()` zera os campos publicados e
  rodava depois do publish do S/H. Corrigido publicando apos o reset
- BUG NO GATE: `screenshot_color_count` reprovou com 262 contra teto 174 numa
  cena CORRETA. O modelo "CRAM uteis x 3" quebra com raster — o gradiente percorre
  UMA entrada por 12 stops no mesmo frame, rendendo ate 36 cores sozinha.
  **Rebaixado a SOFT com o motivo escrito no gate.** A restricao real e ocupacao
  de CRAM, coberta por `color_budget` (mediu 38 de 58)
- BUG operacional: `blastem.bin` sobrevive ao `flatpak kill`, nao aparece de forma
  confiavel em `flatpak ps`, e acumula a cada captura falha. 5 capturas perdidas.
  Limpeza por PID resolve. README corrigido (a instrucao anterior, minha, tambem
  estava errada: eu havia culpado a instancia flatpak)
- Gates finais da arena: **0 hard failures**, cpu p99 78%, 0 frames estourados,
  DMA 896 B de 4096, 38/58 cores, 39 sprites/frame, 13 entradas de prioridade
  amostradas sem violacao

## 2026-08-06 - dano_por_contato_derrota_e_sintese_pedagogica

- `doc/agent_learning/LICOES_MEGADRIVE.md`: sintese tematica das 40 entradas do
  ledger em 7 temas (hardware do VDP, interrupcao vs portas, orcamento, medicao,
  processo, ferramental do host, contratos de arte). Uma tabela de 29 linhas
  registra mas nao ensina
- Lacunas do ledger preenchidas: adicionar cena exige 4 lugares e esquecer
  `APP_SCENE_COUNT` da fallback mudo; um sprite de hardware vai ate 32x32 px,
  logo Kirby custa UM sprite e nao quatro
- Kirby: vida 6, i-frames 60 com blink, knockback com o arco do ARCHITECTURE.md §7
  (`vy -2.5`, gravidade `0.25`) em `fix16`. `KIRBY_damage` retorna se o hit landou
- Dano por contato no boss: pontas dos galhos (2 ultimos segmentos) apenas durante
  `BOSS_WHIP`, e macas em queda. Galho que fere parado seria ilegivel
- **Contra-ataque pelo verbo do Kirby**: inalar a maca do boss e devolve-la como
  dano. Sem espada
- Cena 7 `APP_SCENE_BOSS_PLAYTEST` com script proprio, e 3 estados novos no
  contrato de cobertura: `kirby_hurt`, `boss_hurt`, `boss_dead`
- **`playtest_boss_combat: 3/3` — loop completo PROVADO.** boss hp=0,
  kirby health=4/6, boss derrotado. Primeiro loop completo do jogo em evidencia
- 3 erros meus corrigidos: (a) script que segurava B nunca tomava dano, entao
  `kirby_hurt` ficava NAO — script bom de jogar e ruim de cobrir; (b) script de
  2400 frames sob captura de 32 s nao terminava; (c) `playtest_coverage` exigia
  locomocao de uma captura de boss, que nunca prometeu isso
- Gates: 0 hard failures. 39 sprites/frame, 11/scanline, cpu p99 90/100 (subiu de
  78% com a colisao AABB ativa), 0 frames acima do budget

## 2026-08-06 - game_over_continue_loop_fase1_fechado

- Cena 8 `APP_SCENE_GAMEOVER`: game over e vitoria com continue (countdown 9 s,
  START/A, trava de 45 frames antes de aceitar input)
- Dano de inimigo na fase. Regra de design: inimigo sendo INALADO nao machuca —
  o vortex nao pode punir o jogador por usar o verbo central
- Transicoes: derrota na fase e na arena -> game over; boss derrotado -> vitoria.
  Cenas de playtest nao transicionam, senao a captura sai antes de amostrar
- **O selador canonico rejeitou a primeira versao com
  `blank_or_low_information_capture`, e estava certo.** Tela chapada com texto e
  defeito real para alvo AAA. Refeita com o vale ao fundo e gradiente de humor
- S/H DESLIGADO na cena de texto: os tiles de fonte do SGDK sao prioridade 0 e sob
  S/H global renderizariam a meio brilho
- **Criterio literal da FASE 1 cumprido menos o titulo**: fase -> boss ->
  game over/continue, 5 cenas com evidencia por captura
- Regressao: `stage_regress` PASS com parallax 4/4 EXATO e camera em movimento
  (camera_x=47 -> ceu 0, montanhas -5, colinas -16, terreno -47), cpu p99 50%.
  `gameover2` PASS, cpu p99 15%
- Defeito aberto registrado: coluna pontilhada no ceu da tela de game over

## 2026-08-06 - audio_router_musica_tocando

- `src/audio/xgm_router.c`: dono unico de FM/PSG/PCM conforme SOUNDMAP §2.
  8 faixas de prioridade, supressao de 4 frames, fila de 1 slot para prio >= 11,
  ducking (50%/12f em dano, 75%/8f no verbo, nada abaixo de 9)
- `data/builders/build_placeholder_audio.py`: gera VGM real (header 1.50) com
  baixo/lead FM + PSG, e 3 samples PCM. NAO e a trilha composta
- **Custo de CPU do audio: praticamente zero no 68000** (p99 50% -> 50%, secao
  audio 1 -> 2 scanlines, DMA inalterado). O XGM2 mixa no Z80. A preocupacao era
  legitima e a arquitetura ja a resolvia
- **ERRO MEU**: li `audio.raw` como int16 e diagnostiquei "onda quadrada em escala
  cheia" (-0.1 dBFS). O formato e float32 48 kHz estereo e o pico real era
  -18.5 dBFS. Exposto por um teste de controle que deu resultado impossivel
  (RMS MAIOR sem musica). A info estava no `blastem.log` do bundle
- Mudancas feitas sob a leitura errada (silenciar PSG, subir TL) foram MANTIDAS
  por serem corretas em si, mas o comentario foi corrigido para nao reivindicar
  ter consertado um problema inexistente
- Gates novos **A8 `music_audible`** (RMS 0.0340 vs piso de silencio 0.015 MEDIDO)
  e **A9 `dac_headroom`** (pico 0.1186 vs teto 0.85)
- Baseline de audio: condicao de expiracao CORRIGIDA. Dizia "quando xgm_router.c
  existir"; ele existe e a divida continua porque as violacoes estao nas cenas do
  template. O warning agora le a condicao do arquivo em vez de repeti-la

## 2026-08-06 - tela_de_titulo_fase1_fechada

- Cena 9 `APP_SCENE_TITLE`, agora a cena de BOOT (substitui o branding do template)
- Gradiente noturno de 12 stops reusando o MESMO H-int e a MESMA entrada de CRAM
  da fase; so a tabela muda via `RASTER_setNightSky`. Custo identico
- Campo de estrelas com drift de 1 px a cada 4 frames, silhueta de colina com
  arvore, logo no terco superior reservado pelo briefing R1-07
- **CRITERIO LITERAL DA FASE 1 COMPLETO**: titulo -> fase -> boss ->
  game over/continue -> titulo. 6 cenas, todas com bundle selado e gates PASS
- "PRESS START" custou TRES capturas: (1) WINDOW nao aparece sem
  `VDP_setWindowVPos`; (2) `VDP_setTextPriority(TRUE)` renderizou bloco cinza;
  (3) so funcionou com S/H DESLIGADO. Licao: cena sem efeito que dependa de S/H
  deve rodar com S/H desligado. Efeito colateral: gradiente ficou mais vivo
- Prompt piscante foi pego apagado por 2 capturas — indistinguivel de quebrado.
  Agora e sempre visivel: affordance essencial nao pisca
- 3a ocorrencia de erro de ordem de declaracao em C por insercao via script
- Divida de audio NAO zerou: as cenas do template estao inalcancaveis mas os
  ARQUIVOS seguem em `src/`, e o gate faz grep em arquivo. Nao deletei: nao fui
  eu que os criei. Decisao do usuario
- cpu p99 por cena: titulo 14%, fase 50%, arena 78%, arena+combate 90%, game over 15%

## 2026-08-06 - copy_abilities_com_moveset

- `src/entities/ability.c` + header: pool FIXO de 12 (cota de projeteis do §5),
  5 movesets diferenciados por FEEL: FIRE pressao continua, BEAM precisao
  instantanea, CUTTER compromisso (viaja e VOLTA), STONE defesa, SWORD decisao
- FX 240x16 com 5 formas distintas (pluma, raio irregular, crescente vazado,
  bloco duro, arco fino) — R1-04 exige distincao por forma, nao so por cor
- **B faz dupla funcao**: sem ability inala, com ability ataca. O jogador troca o
  vortex pelo moveset, que e o custo que a mecanica de copia deve ter
- 6 inimigos concedendo as 5 abilities diferentes (o ultimo nao concede nada)
- **Gate novo `ability_moveset_fires`**: reprova captura que CONCEDA ability sem
  que nenhum moveset DISPARE. Era literalmente o estado do projeto ate hoje
- Alavanca de degradacao gasta ANTES de quebrar: `sprites_per_scanline` mediu
  19/20, gastei a alavanca documentada (camada 5 de 8 para 6 tufos) -> 18/20
- BUG NO GATE: `playtest_boss_combat` reprovou captura de FASE porque eu detectava
  contexto de boss por QUALQUER bit de combate, e `kirby_hurt` passou a ser
  alcancavel na fase. Corrigido para usar bits EXCLUSIVOS (`PLAYTEST_BOSS_ONLY`)
- **BLOQUEIO DE AMBIENTE**: `/run/user/1000` (tmpfs 1,5 GB) 100% cheio por
  `codex-desktop/tmp/pytest-of-misael` (3 arquivos de 512 MB de OUTRO app) fazia
  todo `flatpak run` falhar com `fallocate: ENOSPC` em 0.07 s. O host tinha 46 GB
  livres. Nao deletei (dados de terceiro). Provavel causa tambem dos
  `window_timeout` intermitentes — diagnostico anterior estava incompleto
- 4a ocorrencia de `str.replace` que nao casa por espacamento e falha em silencio
- Gates: 25/80 sprites, 18/20 scanline, cpu p99 60/100, 11/11 locomocao,
  `ability_moveset_fires` PASS, 0 frames acima do budget

## 2026-08-06 - r3_r4_agua

- **R3** (distorcao senoidal por linha abaixo da linha d'agua) e **R4** (troca de
  paleta submersa no H-int) implementados na cena 10 `APP_SCENE_LAKE`
- R4 VERIFICADO NO DUMP DE CRAM: PAL1[1..4] de verdes/marrons para azuis/cianos,
  PAL1[5] intacto — exatamente os 4 words configurados
- Rampa submersa materializada como TABELA (regra do estudo r1-06), nao como
  aritmetica cega, que achataria materiais diferentes na mesma cor
- Tensao do contrato resolvida por instrumento: §6.1 limitava o H-int a 1 word
  com teto `[NAO MEDIDO]`, §6.3 falava em 16. Contagem virou configuravel
  (`RASTER_setWaterCramWords`); 4 words provados sem corrupcao
- BUG 1: a otimizacao "pular rebuild com camera estatica" (que salvou a arena do
  boss) tambem pulava a distorcao ANIMADA. Camera parada != tabela estatica
- BUG 2: R4 nunca disparava porque eu derivava a scanline de `stop * 12`, e
  `stop` satura em 12 (linha travava em 144, agua em 150). Contador proprio
- **DEFEITO ABERTO**: apos as mudancas a 1a parada do gradiente de ceu dura mais
  scanlines em ambas as cenas. Causa NAO determinada. Gates passam. Registrado no
  codigo com a instrucao de diagnosticar por telemetria (exportar `s_skyStop`),
  NAO por comparacao de screenshot

## 2026-08-06 - pacote_de_assets_de_producao_p1

- `doc/art/PRODUCTION_ASSET_PACK.md`: 16 assets de producao com dimensao EXATA,
  paleta travada, ordem de frames e criterio de aceite medivel
- `doc/art/production_asset_manifest.json`: manifesto machine-readable + 16
  diretorios de saida criados em `data/source_art/p1/`
- Inverte a proibicao de `animated_sprite_final`/`res_direct` do R1, com
  justificativa MEDIDA: 11 entregas de R1/R2/R3 com 0.00% de pixels ilegais
- Restricoes que carregam licoes anteriores: chave `255,0,255` como cor RESERVADA
  (falha do R1-03), PAL3[14]/[15] proibidos como cor (operadores de S/H usados
  pelo holofote), escada de valor com a FORMULA de luminancia junto
- `ph_light.png` marcado NAO DESENHE: e mascara de operador, nao arte
- `tools/harness/validate_assets.py`: valida dimensao, RGB333, chave, teto de
  cores, escada de valor, ladrilhamento e vaos do terreno
- **Zero entregas NAO e pass**: reporta `status=empty` e sai != 0. Corrigido logo
  na primeira execucao, que mostrava `0/16 failed 0 -> pass`
- `--self-test` valida os placeholders atuais para provar que os checks disparam:
  achou costura de ladrilhamento em B2, B3 e E2, e confirmou a escada de valor
  (0.511 / 0.419 / 0.361 / 0.308, monotonica)

## 2026-08-06 - rodada_p1_executada_source_candidate

- A1 anterior preservada apenas em `obsolete_technical_pass_visual_fail/`; nao e
  fonte de geracao. Causa: elipses radiais, corrida quase congelada, salto lido
  como idle e FLOAT/INHALE com silhueta/anatomia fracas
- Nova A1 reconstruida em grid 32x32 a partir do model sheet R2 e de uma prancha
  de key poses gerada como referencia. A imagem de IA nao virou sprite final
- `sprite_artifact_report.v2` A1: 8 frames, zero findings; clipping, ilhas,
  anatomia, pivot, contato de pes, delta e cobertura de acoes passaram
- 16/16 assets P1 entregues; 16/16 passam o harness mecanico. C5 `ph_light.png`
  permaneceu intocado conforme contrato
- Primeira contact sheet reprovou repeticao procedural em B1-B3, C1, E1/E2 e
  logo excessivamente quadrado. Panoramas foram recompostos sem repeticao curta,
  bark ganhou sulcos/nos irregulares e o logo virou letreiro gordo/arredondado
- Escada medida final: B2 0.512, B3 0.462, B4 0.324, B5 0.200; monotonica
- Todas as 16 pastas possuem PNG, `notes.md` com autocritica e `prompt_used.txt`
- Status final desta rodada: `source_candidate_complete`, nao `delivered`. Nenhum
  arquivo P1 foi copiado para `res/`, buildado ou visto em nova sessao BlastEm
- `validate_project_hygiene.ps1` segue bloqueado por tres classes: entradas de
  raiz preexistentes, nomes legados/IDs maiusculos exigidos pelo pack e caminho
  absoluto preexistente em `doc/scene-contracts.json:5`

## 2026-08-06 - rodada_p1_arquivada_reprovacao_visual

- O solicitante reprovou explicitamente a qualidade visual da P1. Os checks
  técnicos não foram aceitos como substitutos de direção de arte.
- P1 foi preservada integralmente em
  `data/source_art/archive/p1_2026-08-06_visual_rejected/p1/`, com veredito
  `archived_visual_rejected` em `ARCHIVED_ATTEMPT.md`.
- A nova P2 deve criar masters de pixel art arcade dos anos 90 em alta definição,
  fiéis ao conceito aprovado, sem limites de hardware nesta etapa e aguardando
  avaliação humana antes de conversão ou integração.

## 2026-08-06 - proposta_p2_hd_arcade_original

- A geração tentou preservar a identidade existente e foi recusada antes de
  produzir um arquivo; não houve tentativa de burlar esse bloqueio.
- Seis masters novos e originais foram gerados em
  `rascunho/propostas_p2_hd_arcade/` para avaliação de acabamento: herói,
  inimigo, cenário, chefe, FX e tela de título.
- O diretório é `proposal_only_human_review_required`: não é fonte de `res/`,
  não é conversível sem nova decisão humana e não substitui o conceito original.

## 2026-08-06 - segunda_proposta_arquivada_reprovacao_visual

- O solicitante reprovou a segunda proposta visual.
- A proposta foi preservada sem exclusão em
  `rascunho/archive/p2_hd_arcade_original_proposal_2026-08-06_rejected/`.
- Veredito: `archived_visual_rejected`; nenhum master desta rodada é referência,
  candidato a asset, conteúdo de `res/` ou evidência de runtime.

## 2026-08-06 - p3_frames_flat_incompleta

- P3 mudou para conceitos de frame individuais, fundo magenta e preenchimentos
  flat, sem qualquer formatação de ROM.
- O primeiro idle individual teve gradiente e foi reprovado internamente.
- A reexecução sem gradientes foi recusada antes de criar arte; nenhum PNG P3
  foi salvo ou promovido. Registro em `rascunho/p3_flat_frame_concepts/`.

## 2026-08-06 - p3_arquivada_e_p4_master_vetorial_iniciado

- P3 foi arquivada integralmente em
  `data/archive/p3_2026-08-06_geometry_preserved_pixelization_rejected/` com
  o veredito `archived_visual_rejected` e notas de estudo.
- A separação entre conceito e conversão técnica permanece válida, mas a
  geometria precisa ser refinada antes de qualquer redução: P3 não é fonte
  permitida para a próxima conversão.
- P4 começa apenas pelo master vetorial/flat de A1 frame 0 idle. Não houve
  escala para 32×32, quantização RGB333/PAL2, sprite sheet, alteração de `res/`,
  build ou validação em emulador.
- A tentativa de gerar o master não retornou imagem. P4 permanece
  `blocked_no_generated_output`, documentada em
  `data/source_art/p4/A1/master_vector/P4_A1_STATUS.md`; nenhum substituto
  visual foi criado.

## 2026-08-06 - p4_a1_master_vetorial_proposta

- Criado o master vetorial editável de A1 frame 0 idle em
  `data/source_art/p4/A1/master_vector/ph_kirby_frame_00_idle_master_vector_v1.svg`.
- A construção usa somente paths e fills sólidos, fundo `#FF00FF`, contorno
  único e cel-shading de borda dura; não há gradientes, filtros ou rasterização
  para 32×32.
- Status: `proposal_waiting_human_visual_approval`. Não houve quantização,
  indexação, montagem de sheet, alteração de `res/`, build ou emulador.

## 2026-08-06 - p4_a1_master_vetorial_v2_anatomia

- A revisão visual identificou falha anatômica no master v1: braços e pés
  excessivos, separados e pouco coerentes com o modelo conceitual.
- Criado `ph_kirby_frame_00_idle_master_vector_v2.svg` com silhueta corporal
  mais estável, braços curtos conectados e pés compactos com base equilibrada.
- A revisão continua somente como proposta visual; etapas 3 e 4 de P4 seguem
  bloqueadas até aprovação humana explícita.

## 2026-08-06 - p4_arquivada_reprovacao_anatomica

- O solicitante reprovou a última tentativa P4 por anatomia insuficiente.
- P4 foi preservada em
  `data/archive/p4_2026-08-06_vector_master_anatomy_rejected/`.
- Veredito: `archived_visual_rejected`; os SVGs e previews são apenas
  `negative_evidence`/`comparison_only` e não podem alimentar geração,
  quantização, `res/` ou baseline.
- Lição: limpeza vetorial, ausência de gradiente e cores flat são condições
  técnicas; não aprovam topologia, proporção, integração de membros ou acting.
## 2026-08-31 - decisão humana e challenger visual v02

- Rota A — `Sunlit Cultivation` travada somente como `locked_visual_direction`, vinculada ao asset_id e SHA existentes.
- Cena-dourada travada somente como referência de composição, iluminação, profundidade, camadas e densidade; nenhum bitmap foi convertido ou promovido.
- Model sheet anterior preservado como `model_sheet_challenger_v01`, `visual_gate=needs_rework`, `promotable=false`, `translation_authorized=false`; checks não comprovados corrigidos para `not_proven`.
- Gerado `model_sheet_challenger_v02` com referência explícita ao challenger anterior; novo challenger, não canônico.
- Criados gates independentes para direção visual, cena-dourada, model sheet e tradução nativa.
- Criados decomposição semântica, inventário de tile kit e estudo visual de três distribuições de paleta.
- GDD/spec/memória reconciliados com a identidade de fan game derivado da identidade de Kirby/Nintendo/HAL, execução gráfica original e sem reutilização/extração de pixels.
- Nenhum arquivo de `res/` foi alterado. Nenhum claim de arte nativa, ROM, `visual_pass` ou AAA foi emitido.
- Decisão humana: `rework_before_native_translation` para o v02, aceito somente como `turnaround_volume_reference_only`; tradução nativa permanece não autorizada.
- Gerados challengers v03-A `cluster_strict` e v03-B `silhouette_first`, com hashes e proveniência registrados. v03-B foi gerado sem referência após bloqueios da ferramenta e está marcado como novo challenger.
- Criados probes mecânicos 32×32, 64×64 nearest, 320×224 e silhueta preta 32×32; microcores high-res causam rejeição automática para uso nativo.
- Nenhum arquivo de `res/`, sprite sheet ou animação final foi criado.

## 2026-08-31 - aprovação limitada do model sheet v03-A

- Registrada a decisão humana `approved_as_model_sheet_source_for_single_native_key_pose` para `model_sheet_challenger_v03_a_cluster_strict`.
- SHA-256: `989d1a2398e9609dffe3e4f673e95b73e081ddffdcba9764829684498d8c6241`; `revision=v03_a`; rota `cluster_strict`; escala `32x32`.
- Autorizados somente `model_sheet_reference` e `single_idle_native_key_pose_translation`.
- Turnaround completo, outras poses, sprite sheet, `res/` e runtime continuam bloqueados.
- O PNG permanece `visual_source`; os gates de autoria nativa, pixel-strict, ResComp, budget e aprovação humana da pose continuam pendentes.

## 2026-08-31 - candidatos nativos da pose idle 32x32

- Corrigida a evidência de escala: 64×64 e 256×256 foram regenerados exclusivamente por repetição NEAREST dos probes 32×32; o teste de índice/alpha exato passou em 2× e 8× para BASIC e ELITE.
- Produzidos dois candidatos da mesma silhueta e lineart: BASIC `native_idle_key_pose_basic_v01`, SHA-256 `473bcdeab5b1b7edf7d32aeafe4d5d7f49aedb780684e94fddfde66c5aec3ecd`, 9 cores; ELITE `native_idle_key_pose_elite_v01`, SHA-256 `58004465b39c826ce970c5c8018cb202f2befbf45b8ce8c2fa355804daa9fb29`, 12 cores.
- Os candidatos são P/4bpp, 32×32, índice 0 transparente, alpha binário, RGB333, sem AA, gradiente, dithering ou sombra de chão. Registros, mapas de forma/material e budget foram adicionados.
- Estado encerrado em `pending_human_decision`: nenhum candidato venceu visualmente, nenhum foi promovido a `res/`, nenhuma animação/sheet/runtime/ROM foi tentada.

## 2026-09-01 - ELITE idle runtime review e motion proof controlado

- Registrada a decisão humana `approved_for_native_idle_key_pose_and_runtime_visual_proof` para `native_idle_key_pose_elite_v01`, SHA `58004465b39c826ce970c5c8018cb202f2befbf45b8ce8c2fa355804daa9fb29`, 32×32, pivot `(16,31)`, baseline `30`, 12 cores, escala travada no escopo da pose.
- BASIC foi preservado como `comparison_control` superseded by visual choice; v03-B permanece `comparison_only`; nenhum turnaround completo foi promovido.
- Criada a cena isolada `APP_SCENE_NATIVE_ART_REVIEW` com o `SPRITE spr_native_idle_elite` real em `resources.res`. O herói do first playable não foi substituído.
- Criados contratos machine-readable para estados runtime, roster de poses, budget, pivot/escala, direção, fases, tracking, física e transições. Três novos key poses foram produzidos para prova reversível: contact, passing e airborne.
- Regenerados probes 64×64/96×96/256×256 exclusivamente do PNG 32×32 com NEAREST. Repetição exata de pixels/alpha foi registrada; previews e painéis são `mechanical_scale_probe`/evidência.
- Status encerrado antes do closeout: `runtime_pass=pending`, motion package `animation_candidate`, `ready_for_aaa=false`. Build/BlastEm e métricas contextuais permanecem como próximo passo desta rodada.

## 2026-09-01 - prova isolada BlastEm concluída e gates selados

- Build canônico e ResComp passaram para `APP_SCENE_NATIVE_ART_REVIEW`/scene 11 usando `spr_native_idle_elite`; o herói de `first_playable` permaneceu intacto.
- Registro ELITE passou no validator semântico: schema, pixel contract, shape block, oito regiões, contorno, topologia de quatro materiais e fronteiras críticas; `promotable=false` permanece obrigatório.
- A falsa evidência de escala foi corrigida novamente no fechamento: `64x64` e `256x256` são rederivados exclusivamente do PNG 32×32 por NEAREST; os backgrounds do record são recomposites 32×32 exatos. O erro anterior de modo declarado (`P/4bpp indexed PNG`) foi corrigido para o modo real `P`.
- BlastEm passou na sessão `blastem-linux-20260901T084532Z-4098997`, com ROM SHA-256 `d37077b2d1c6e8c2f65a24ee0ffd4e64ebac57d37ef75520d5d7c1aef7cce8ad`, screenshot/VDP dump/SRAM e freshness no mesmo bundle. Cena 11, 1 sprite ativo, 1 sprite/scanline amostrado, 39 CRAM/58 e 0 frames acima do budget.
- `frametime_report` mediu 32 amostras: p99 12%, pior 12%, 0 acima do limite; isso permanece snapshot isolado, não prova de performance sustentada. Corrigido o bug de caminho do harness antes da medição.
- A primeira sessão, com células magenta no backdrop, foi descartada; a segunda sessão corrigida é a única evidência canônica.
- O motion package com três key poses permanece `animation_candidate`; não houve sheet completa, animação final, substituição do first playable, promoção final de `res/` ou claim AAA.

## 2026-09-02 - forward-test r1 de animação

- Executado forward-test sobre os sete projetos `[GAME]` da raiz operacional `/mnt/sdcard/Projects/Sgdk Forge`; diagnósticos e blockers foram mantidos por projeto, sem deixar um projeto sem arte bloquear os demais.
- No Kirby Cloude GEN, r1-01 foi persistido e eleito autoridade de identidade/turnaround/expressões/movimento. A auditoria de escala rejeitou downscale direto por ausência de fator inteiro global comprovado.
- Produzido pacote isolado `out/forward_test_v03_r1/` com crops, lineart de auditoria, strips `idle/run/inhale`, previews GIF, contratos e relatórios. Nenhum arquivo de `res/`, runtime, ROM ou `resources.res` foi alterado.
- Gates mecânicos passaram nas três ações: artifact strip, motion semantics e sprite integrity. Claim consolidado: `motion_semantic_candidate`; princípios de animação, qualidade visual, autoria/derivative review, integração e BlastEm continuam pendentes.
- O crop idle passou `source-audit`; o shootout executou 20 rotas/5 skips e verificou a cadeia de hashes, sem vencedor automático. O painel permaneceu explicitamente `mechanical_geometry_probe`.

## 2026-09-02 - autoria nativa temporal v04

- Reclassificados os strips v03 como probes mecânicos de pose única; proibidos como fonte de pixels.
- Autorados 16 frames nativos em quatro ações (`idle`, `run`, `inhale`, `jump_float`) no pacote isolado `out/forward_test_v04_native_temporal/`, com contratos, fases, transições, GIFs, lineart auxiliar e proveniência.
- Quatro gates por ação passaram: strip artifact, motion semantics e sprite integrity. O agregado passou sem blockers com teto `motion_semantic_candidate`; não é aprovação visual nem promoção.
- Criados relatório dos 12 princípios (`needs_review`), gate visual bloqueado e budget offline. `human_gate_status=pending`, `promotable=false`, `res_promotion=false`; sem alteração em `res/`, build, ROM, runtime ou BlastEm.

## 2026-09-02 - forward-test v06 corrigido de produção visual temporal

- Criado o pacote isolado `out/forward_test_v06_corrected_native_temporal/` a partir da autoridade r1; v04/v05, `res/`, `resources.res`, runtime e ROM permaneceram intocados.
- Fechada a reprodução dos falsos verdes v05 com gates executáveis para matte RGB/checkerboard, fundo retangular, replicação inteira, paleta preta/deriva, equivalência GIF/strip, duplicação temporal e review cego não executado.
- Produzidos novos outputs do produtor visual integrado: fontes raw, diagnósticos, lineart independente, quatro ações com 16 frames, strips indexados com índice 0 transparente, GIFs hash-bound, contratos, fases, contatos e evidências.
- Corrigido o colapso do GIF de inhale (frames idênticos) com variação temporal de probe declarada; corrigida a borda indevida de jump; `idle_breathing` e `run_cycle` passaram o validator semântico.
- Persistidos como blockers reais: `inhale_or_charge` ainda é probe mecânico abaixo do perfil e o registry oficial não contém `jump_arc`. Não houve fabricação de aprovação, confiança, review cego ou claim de runtime.
- Validação v06 central limpa e self-check 11/11. Estado final: `needs_review`, teto `temporal_translation_probe`, gate humano pendente e promoção para `res/` bloqueada.
- Avançado o gate de evidência visual: gerados GIFs 2×/3×/8×, contact sheets, silhuetas, overlays pivot/contact, fundos diagnósticos, composição 320×224, deltas e timing derivados das células finais; sem alteração dos strips já confirmados.
- Relatório de proposta de curadoria completado com campos causais, antes/depois, aplicabilidade, risco e recomendação; nenhum `SKILL.md` foi editado.

## 2026-09-03 - fechamento da rota native_grid_encoded

- Corrigido o estado operacional para `technical_runtime_creative_blocked`, com o ramo Kirby em `blocked_native_pixel_authorship`; v08/v09 continuam preservados em seus estados históricos.
- A rota limitada `native_grid_encoded` teve exatamente dois ensaios. O primeiro falhou por incompatibilidade mensurável de grid/paleta; o segundo foi rejeitado pelo produtor externo com `HTTP 400 moderation_blocked`. A moderação não foi contornada.
- Persistidos os registros de tentativa e o relatório de fechamento em `data/staging/animation_curation_run_keyposes_20260903/`.
- Persistidos inventário gráfico completo e triagem dos ramos independentes em `data/staging/visual_inventory_20260903/`.
- Sem nova arte final, sem promoção para `res/`, sem alteração de runtime ou ROM e sem mudança em v04–v09.

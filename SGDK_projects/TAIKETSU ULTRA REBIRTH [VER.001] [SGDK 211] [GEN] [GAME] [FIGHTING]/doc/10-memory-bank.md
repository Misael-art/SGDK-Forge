<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-09-09T17:45:00-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 20
- Ultimo build versionado: build_v007
- ROM vigente: `869a0eedde787d632aa1997edfebe36c556f386bc40c57fba3e14cdc8a660e18` (`262144` bytes)
- Validation summary: errors=2 warnings=13 (os dois são estados de claim/closeout, não falhas de compilação ou host)
- Blockers vigentes: visual_gate_blocked, visual_direction_failed, animation_gate_failed, scene_regression_incomplete, runtime_capture_partial, perceptual_metrics_zero
- Evidencia de emulador: ok (BlastEm Linux selado; cena 3 observada; audio.raw hash-bound)
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=parcial_scene3 performance=unproven audio=sidecar_signal_integrity_only hardware_real=BlastEm_linux_flatpak
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker - TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

## 25. Epoch VLAB runtime ranges, áudio atual e reconciliação — 2026-09-09

- A ROM vigente é `869a0eedde787d632aa1997edfebe36c556f386bc40c57fba3e14cdc8a660e18`, 262144 bytes; o hash foi preservado antes e depois da captura Linux.
- A sessão válida é `blastem-linux-20260909T173215Z-3070928`, rota Linux Bash/Flatpak/BlastEm, cena 3 observada, janela `59.4 fps`. O pacote canônico contém screenshot, SRAM, manifest selado, selo, métricas e `audio.raw`; `visual_vdp_dump.bin` tem 240 bytes de VLAB real e não é dump integral de VRAM.
- O VLAB observou quatro faixas distintas sem overflow: `[16,516)`, `[516,616)`, `[1376,1391)` e `[1391,1406)`. Isso fecha apenas residência runtime parcial da cena observada; não prova todos os estados, densidade final, completude de streaming ou performance sustentada.
- O sidecar atual `audio.raw` tem 10.223.616 bytes, SHA `4dfa07b65274eb4c427ce96467923b5ae7cefc0f289d1000bf750ebe59e33f0e`; análise objetiva derivada passa com 26,624 s, sinal não silencioso e sem clipping. Mix, loop, SFX, driver real e escuta humana continuam sem prova.
- O blocker histórico de backend permanece classificado somente como `host_executor_route_mismatch_resolved`; não houve instalação de WinForms, Mono, Xvfb, Wine ou uso de captura Win32. `ready_for_aaa=false` permanece.
- O finalizador de evidência agora propaga `session_id`; relatórios ativos de evidência, performance, visual, áudio, VDP e DMA foram reconciliados para a mesma ROM/sessão. A regressão atual capturou as seis cenas: quatro baselines passaram e `branding_sequence`/`front_end_main_menu` têm divergência de screenshot; nenhum baseline foi sobrescrito.

## 23. Epoch budget VDP e continuidade pós-route-fix — 2026-09-09

- A captura Linux resolveu o blocker causal de backend, mas não encerrou a produção. A ROM do TAIKETSU permanece `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3`.
- Self-checks canônicos passaram para residência, scanline e DMA. O laudo consolidado em `out/logs/d1_runtime_vdp_budget_assessment_20260909.json` decide `cabe com recuo`: 946/1740 tiles residentes (54,4%), 4 sprites/120 pixels/7 links no pior scanline offline e nenhuma violação no contrato DMA.
- O recuo obrigatório é medir o resident set dos símbolos carregados por código, integrar os assets nativos finais de Kairo/C1, recapturar o pior quadro sustentado com áudio e manter os relatórios vinculados à ROM promovida. Portanto `validado_budget=false` e `ready_for_aaa=false` continuam corretos.
- Os blockers prioritários agora são: aprovação/reautoria visual nativa, continuidade de animação, VDP runtime final, áudio audível com loop/mix/SFX e regressão das cenas sem bootstrap suportado. A correção de rota não é tratada como dependência gráfica ausente.

## 24. Epoch audio QA baseline — 2026-09-09

- A validação estática continua aprovada para 8 recursos, 2 XGM2, 6 WAV e 0,95% estimado de ROM; isso confirma declaração/estrutura, não qualidade sonora.
- O relatório `out/logs/audio_qa_baseline_20260909.json` classifica a execução como `needs_review`: o sidecar `audio.raw` é não vazio e hash-bound à sessão Linux, mas não declara formato, taxa ou canais.
- Permanecem sem prova escutada: motivo BGM, emenda de loop, fadiga, arbitragem BGM/SFX na cena pesada e banco final aprovado. Nenhum claim de áudio final foi elevado.

## 22. Epoch scene-baseline reconciliation — 2026-09-09

- Reavaliada a matriz host-aware com `--reuse-evidence`: `first_playable_slice`
  e `combat_cinder_circuit` agora passam por SHA de baseline usando os bundles
  Linux já selados para a ROM vigente; nenhum VDP dump foi criado ou alterado
  fora desses artefatos observados.
- A regressão permanece parcial, com quatro cenas abertas: `branding_sequence`
  (alvo 0, cena 2 observada), `front_end_main_menu` (erro de captura),
  `stage_intro_cinder_circuit` e `dialogue_cinematic_d1` (bootstrap não
  suportado). O report atual é `scenes_passed=2`, `scenes_failed=4`.
- `validate_resources.ps1` terminou novamente com `errors=0`, `warnings=13`;
  `scene_closeout_gate` permanece `warn/blocked` apenas pelos blockers de
  produção reais. `freshness_audit` está `ok` (`stale=0`, `missing_required=0`)
  e `claim_reconciliation` continua `passed` com `ready_for_aaa=false`.

## 21. Epoch visual review and live-scene report reconciliation — 2026-09-09

- A revisão de staging do candidato Kairo 88x136 foi persistida em
  `rascunho/scale_correction_20260909/direct_native_pixel_art_v01/direct_pixel_art_v01_visual_review_20260909.json`, vinculada à fonte SHA `0c3095038b69328a304a819ed9201ae3038467a1b88128b4fbd7de91ac88dae3` e ao candidato técnico SHA `1c7c86a503ecc966b47f43cdf6e408ef90fba52fd48dbe9ceb1f65c5ea653df5`.
- A leitura em 1x confirma silhueta, escala de 128px, cachecol, materiais índigo/ciano/âmbar e contato dos pés; olhos/olhar e junções mão-luva ainda precisam de reautoria nativa. O registro mantém `technical_candidate`, sem aprovação humana, sem promoção para `/res` e sem alteração da ROM.
- A variante corretiva v02 foi preservada somente como rejeição em
  `rascunho/scale_correction_20260909/rejected_attempts/`: o checkerboard está
  rasterizado no PNG (`30d819ab3442771102b3b406df86e5b170384b140639c08f925e1e363af16fae`), portanto não é transparência confiável e não é elegível para o workset ou `/res`.
- `out/logs/live_scene_bar_report.json` foi reconciliado com a sessão Linux `blastem-linux-20260909T124600Z-1554938`, `blastem_current`, `visual_vdp_dump.bin` real e o report de regressão atual. O status permanece `needs_review`; áudio bruto, cena 3 e VLAB parcial não foram elevados a prova de qualidade, áudio ouvido, regressão completa ou performance sustentada.
- Após a reconciliação, `validate_resources.ps1` terminou com `errors=0`, `warnings=14`; `scene_closeout_gate.ps1` e freshness passaram. ROM antes/depois permanece SHA `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3`.

## 20. Epoch hygiene and closeout reconciliation — 2026-09-09

- removido somente o `doc_sync_report.json` duplicado criado dentro da raiz
  `SGDK_projects/`; os diretórios vazios foram eliminados e o relatório
  canônico permaneceu em `out/logs/`;
- `validate_project_hygiene.ps1` passou com zero blockers, eliminando
  `orphan_project_root_entry` e `noncanonical_project_entry_name`;
- validação atual: `errors=0`, `warnings=13`; blockers restantes são
  `visual_gate_blocked`, `visual_direction_failed`, `animation_gate_failed` e
  `scene_regression_incomplete`;
- closeout seguro foi reexecutado sem build, captura ou regressão: `warn/blocked`;
  claims permanecem `ready_for_aaa=false`, `technical_ready=false`,
  `creative_ready=false` e performance `unproven`;
- o guard semântico ainda detecta o diretório irmão
  `TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [SGDK 211] [GEN] [GAME] [FIGHTING]`,
  com uma cópia hash-idêntica de PNG; ele permanece preservado até autorização
  humana explícita para remoção ou renomeação;
- freshness audit passou com `stale=0` e `missing_required=0`; ROM e bundle
  BlastEm vigente permaneceram inalterados.

## 19. Epoch direct pixel-art hypothesis and offline budget — 2026-09-09

- Uma nova hipótese causal foi gerada diretamente como pose pixel-art de Kairo, fora do caminho de resize da probe anterior. A fonte `kairo_vant_direct_pixel_art_source_v01.png` passou `source-audit`, entrou no workset ativo com SHA `0c3095038b69328a304a819ed9201ae3038467a1b88128b4fbd7de91ac88dae3` e permanece `translation_source` de staging.
- O route-shootout C executou Lanczos3, Catrom e Nearest no mesmo canvas 88x136; não há vencedor automático. O handoff registra Lanczos3 como guia primário, Catrom como challenger e Nearest como controle. Todos continuam mecânicos e fora de `res/`.
- A conversão técnica v01 produziu `88x136`, 15 cores visíveis, index 0 transparente e SHA do conteúdo `d8ef6c8bf90b7a0ac53055eeac6e8cb960d862110be84cc11db834b564654f51`; o PNG é `technical_candidate`, não arte nativa nem aprovação visual.
- O envelope offline dessa pose mediu 100 tiles únicos/3.200 bytes e, com Kairo 88x136 + Ryo 64x104 + quatro FX 32x32, 27 links, 9 sprites por scanline e 280 pixels por scanline em H40, sem overflow. Isso não prova residency, DMA, animação, gameplay ou performance em runtime.
- A inspeção nearest 8x mostra ganho de leitura de silhueta e materiais sobre a probe C anterior, mas rosto/olhos ainda exigem revisão. Uma iteração corretiva gerada depois foi rejeitada por checkerboard; não entrou no projeto. Nenhum código, asset ativo, `/res`, build ou ROM foi alterado.
- `ready_for_aaa=false`; a próxima etapa é autoria nativa/revisão visual humana do candidato v01, seguida de material topology, animação, budget de cena viva e integração SGDK. O guard semântico ainda registra `duplicate_project_identity_detected` pela raiz vazia preservada.

## 18. Epoch fighting semantic guard and art routing — 2026-09-09

- O diagnostico de arte foi refeito com `art_diagnostic.py`: `/res` possui 20 assets tecnicamente conformes e nenhum blocker de conversao ativa; o blocker e de producao visual, pois os lutadores ativos ainda sao probes/lab e nao arte final aprovada.
- O workset ativo `d1_scale_reset_20260905` passou `workset-validate`; as fontes de Kairo permanecem source/reference-only e nenhuma imagem foi promovida para `res/`, build ou ROM.
- Foi criado `doc/art/kairo_vant/fighting_sprite_semantic_contract.json`. O guard rederiva a escala de 128px a partir dos frames Jack/Ryo, confirma o marcador do GDD e classifica as tres referencias como `scale_reference` nao-promoviveis.
- O unico blocker retornado pelo guard semantico e `duplicate_project_identity_detected`, referente a raiz vazia `[SGDK 211] [SGDK 211]`; ela permanece inventariada e preservada, sem delecao autorizada. O teto de claim continua `semantic_scale_gate_only`.
- Nenhuma alteracao de codigo, asset ativo, ROM ou captura foi feita nesta epoch. `ready_for_aaa=false`; a proxima acao causal continua sendo reautoria nativa no grid C, seguida de validacao pixel/animacao, budget, BlastEm e aprovacao humana.

## 17. Epoch preload DMA separation and Linux evidence reseal — 2026-09-09

- A ROM `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3` foi compilada como build_v007; hash antes/depois da captura permaneceu igual.
- A sessão canônica é `blastem-linux-20260909T124600Z-1554938`, rota Linux/Flatpak/X11, janela `SAMPLE PROGRAM - BlastEm - 59.6 fps`, alvo 3 e cena 3 observados. Screenshot, SRAM, manifest, selo, métricas, `audio.raw` e VLAB real de 222 bytes estão selados.
- O probe agora separa gameplay de preload: gameplay ficou em 32 bytes/1 entrada/7200 bytes no frame 91 após 90 frames de warmup; preload foi observado em 90 amostras, com pico de 1000 bytes/4 entradas/7200 bytes no frame 1. Isso não prova completude de loading/streaming, residency viva ou performance sustentada.
- `audio.raw` tem 12.591.104 bytes, 84,2975% não-zero e SHA `17a08c1c7b0f65fd77b34bdc0301a15f453e9ea2689ee7cadc7c7580dfdc5471`; prova somente sidecar não vazio, não prova escuta, loop, mix, SFX ou áudio final.
- A causa histórica permanece `host_executor_route_mismatch_resolved`; `blastem_capture_host_dependency_missing` e `display_backend_missing` não são blockers atuais. O `visual_vdp_dump.bin` presente é VLAB parcial real, não um dump integral de VRAM.
- `ready_for_aaa=false`: continuam bloqueadores a arte nativa final, animação, regressão das cenas não suportadas, áudio contextual e performance sustentada.

## 16. Epoch DMA probe correction and Linux evidence reseal — 2026-09-09

- A instrumentação MDRT/VLAB foi corrigida: `[18]/[19]/[20]` agora são exclusivamente pico de fila DMA, bytes transferidos e capacidade; alocação de sprites foi movida para `[30]/[31]`. O VLAB passou a schema 2 e o parser aceita payload variável sem truncamento.
- A ROM dessa epoch anterior foi supersedida pela build_v007 atual; seu registro permanece histórico e não é claim ativo.
- A sessão dessa epoch anterior foi supersedida pela sessão Linux atual; seu bundle permanece histórico e não é claim ativo.
- Medição observada na cena 3 após a exclusão dos 90 frames de warmup: pico DMA por frame de 32 bytes, 1 entrada, capacidade 7200 bytes, no frame 91. Isso fecha apenas o eixo DMA de gameplay observado; preload/streaming DMA, residency viva e performance sustentada permanecem abertos.
- `audio.raw` tem 12.419.072 bytes, 84,1476% não-zero e SHA `f452f10330a69a1f54d06aa37385a4ffce7de51dd6f72c4edf8175048017b507`; prova sidecar não vazio, não prova escuta, loop, mix, SFX ou áudio final.
- A causa histórica continua `host_executor_route_mismatch_resolved`; `blastem_capture_host_dependency_missing` e `display_backend_missing` não são blockers atuais. Nenhum `visual_vdp_dump` foi inventado: o arquivo presente é VLAB parcial real.
- `ready_for_aaa=false`: continuam bloqueadores a arte nativa final, animação, regressão das cenas não suportadas, áudio contextual e performance sustentada.

## 15. Epoch current-ROM audio candidate and Linux evidence — 2026-09-09

- O build atual integra um candidato BGM PSG autoral de Cinder Circuit em `res/music/cinder_circuit_arena_candidate.vgm`; a partitura foi compilada para VGM e convertida para XGM2 com os dois self-checks aprovados. O runtime de combate seleciona essa música, mas o contrato permanece `vertical_slice_candidate`: ainda falta escuta humana, reprodução real, arbitragem e máscara de SFX em cena pesada.
- A ROM vigente dessa epoch anterior foi supersedida; o registro é histórico e foi substituído pelas epochs posteriores.
- A captura dessa epoch anterior foi supersedida; seu selo permanece histórico e o VLAB era parcial, não dump integral de VRAM.
- `runtime_metrics`, `evidence_closeout`, `emulator_session`, `performance_capture`, `code_review`, claim reconciliation e documentos ativos foram reconciliados para a mesma ROM/sessão. A causa anterior permanece `host_executor_route_mismatch_resolved`; não há dependência gráfica ausente vigente.
- A medição estática de residência foi refeita na build atual: pico de plano 946 tiles sob teto estático 1740. Isso não fecha VDP/DMA em runtime. Os blockers reais continuam arte nativa final, animação, baselines/protocolos de cenas, áudio real e performance sustentada; `ready_for_aaa=false`.
- O parecer VDP D1 foi consolidado em `doc/07-budget-vram-dma.md`: `cabe com recuo` no eixo técnico (946/1740 tiles, 8 sprites e 160 pixels no pior scanline do envelope, 16 links, sem overflow), mas DMA/VBlank, tiles carregados por código e desempenho sustentado continuam sem prova. A captura registrou janela 57,3 fps e `cpu_load_max=98`; o eixo perceptivo segue não avaliado por os lutadores serem probes.
- A mesma sessão BlastEm também gerou o sidecar bruto `audio.raw` de 12.148.736 bytes, com 10.335.768 bytes não-zero e SHA `9cd2f06d44b8698149d66e0203e8205ff5110ad5fb7624e984ad939194a4d1b5`. Ele prova somente saída de áudio não vazia; como não possui cabeçalho de formato, ainda não prova que o BGM, loop, mix ou máscara de SFX foram ouvidos corretamente. Ver `out/logs/audio_runtime_capture_report.json`.
- A regressão host-aware capturou e atualizou baselines para `front_end_main_menu` e `first_playable_slice`; ambos agora comparam por SHA na ROM vigente. Permanecem falhos apenas o branding (alvo 0, cena 2 observada) e as cenas CS-C/CS-E sem bootstrap suportado.
- O sealer Linux agora inclui `audio.raw` opcional no manifesto quando presente; os fixtures antigos continuam com cinco artefatos. O validator de tilemap deixou de depender de `scene_contract_compile`/`res_graph` como outputs, eliminando o ciclo temporal que marcava o report stale a cada closeout. Self-check do sealer, fixtures de bundle/rota e `test_scene_closeout_gate.ps1` passaram.
- A curadoria do seletor agora tem fixtures explícitos para os cinco contratos: Linux nunca usa WinForms/PowerShell, Windows nunca usa Flatpak, `DISPLAY=:0` não é classificado como backend ausente, DISPLAY ausente produz blocker X11 distinto de dependência do emulador, e o comando pertence à rota/host reportado. O guard do ambiente foi reexecutado com host real Linux/KDE/Wayland, e `sgdk_build_route_report.json` confirma `linux_wine_bridge` sem blockers.

**Ultima atualizacao:** 2026-09-09T07:57:00-03:00
**Fase atual:** D1 contrato/runtime tecnico ampliado; captura Linux BlastEm selada para cena 3; regressao host-aware parcialmente observada; gate visual, audio e performance ainda bloqueados
**Proxima fase:** fechar arte nativa aprovada, baselines/protocolos das cenas restantes, audio vivo e performance antes de promover o slice

## 1. Estado operacional

- documentado: Fase -1, Q1, rota Wine bridge, roster, GDD, TDD, opt-in fighting e cobertura planejada
- implementado: sim (D1 runtime probe em `src/scenes/scene_demo.c`; ainda nao e entrega final)
- buildado: sim (ROM vigente SHA-256 `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3`)
- testado_em_emulador: parcial para boot/superfície visual da ROM vigente; alvo de cena, gameplay sustentado, performance e input ainda não provados
- validado_budget: medição estática atualizada por `audit_tile_residency.py`; pico de plano 946 tiles sob teto estático de 1740, mas DMA/runtime residency ainda não provados
- audio: candidato PSG autoral de 8 barras compilado para VGM/XGM2, 2 músicas declaradas e orçamento validado; reprodução/arbiter/human listen em cena pesada ainda não fechados
- ready_for_aaa: false

## 2. Bloqueios iniciais

- gap de medicao 17/18: `validate_native_sprite_production.py` nao possui self-check; ready_for_aaa bloqueado
- o diagnóstico anterior foi corrigido para `host_executor_route_mismatch`; Linux agora seleciona explicitamente `capture_blastem_evidence_linux.sh`, enquanto `run_runtime_capture.ps1` falha cedo fora do Windows
- gate visual bloqueado: Kairo/C1 sao proxies de laboratorio e a arte final de Jack/C1 ainda nao foi aprovada
- `res_graph_report.json` agora reporta `vram_residency_status=ok`; regressao por cena, audio em cena pesada e o fechamento visual ainda nao estao aprovados
- agent bridge degradado por symlink `.agents/skills` com alvo relativo divergente
- A captura canônica vigente é `blastem-linux-20260909T124600Z-1554938`; hash antes/depois preservado em `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3`. O `visual_vdp_dump.bin` é VLAB real de 222 bytes, não um dump integral de VRAM.

## 3. Regra de continuidade

Atualize este arquivo, o changelog e os manifests sempre que a verdade
operacional mudar. Nunca copie hashes, builds, aprovacao ou evidencia do modelo.

## 4. Fechamento da ativacao - Fase -1 / D0

- Sessao registrada em `doc/agent_session_state.json`: modo `create_new_project`, perspectiva `director`, projeto ativo correto.
- Rota Linux executada por `tools/sgdk_wrapper/build.sh`; `out/rom.bin` gerado via Wine bridge SGDK 2.11.
- ROM de prova: 262144 bytes; SHA-256 `bc2120e83ae6ae280a6f2146c24c7b5e9989c161a112e8b829a72f528b748cb0`.
- Relatorio de build: `out/logs/linux_wine_build_report.json`; ROM vigente `build_v003` hash-bound.
- `validate_measurement_tools.py`: 17/18 self-checks; bloqueio conhecido em `validate_native_sprite_production.py` sem self-check. `ready_for_aaa` permanece `false`.
- `validate_fighting_specialization.ps1`: regras do manifesto, contrato e seis movesets aprovadas; a auto-validacao do proprio relatorio registrou incompatibilidade `OrderedDictionary` e foi preservada como bloqueio de ferramenta/documentacao.
- Contexto, metodologia e higiene do projeto passaram; runtime foi observado apenas como slice tecnico, sem promocao de hardware, audio ou aprovacao visual.

## 5. Q1 foundation

- Request, plan, taskset e parecer independente foram materializados e vinculados por digest.
- Três revisores read-only retornaram `needs_adjustment`; `quality_review_router validate-report` passou.
- Decisão: `revise_before_growth`; as prioridades são contrato CS-C/D1, evidência BlastEm e self-check 18/18.
- O Q1 não promove claims: `quality_claim=unproven`, `ready_for_aaa=false`, teto `vertical_slice`.

## 6. D1 runtime probe e evidencia

- `src/scenes/scene_demo.c` implementa o slice de luta com input centralizado, hit/hurt/push/solid boxes, guard, hitstop, meter, especial, camera lock/shake e ownership de VBlank.
- `SPR_initEx(64)` foi aplicado após medir o envelope de dois lutadores 32x40 e 12 FX; o laudo `out/logs/d1_kairo_v06_budget_report.json` registra 19 tiles únicos no Kairo v06, 40 tiles brutos no par e pressão máxima de 8 sprites/160 pixels por scanline.
- ROM vigente: `out/rom.bin`, 262144 bytes, SHA-256 `97ce57eaf1707613b150c15af2556004c50f5cff69a5eb77aebc2222a9b23ea4`.
- Pacote BlastEm: `out/evidence/blastem/screenshot.png`, `save.sram`, `visual_vdp_dump.bin` e `session_manifest.json`; bundle Linux `blastem-linux-20260905T195659Z-1447821` selou a identidade da ROM e o gate semântico passou, com `runtime_scene_id=2` para alvo 3.
- `scene_closeout_gate_report.json`: `warn`; compiler de contrato, res_graph, screenshot semantico, freshness e learning passaram, enquanto validacao final/document sync continuam com warnings.
- Probe v003 parcial de boot: 1111 frames no snapshot VLAB, 32 samples, 0 frames acima do budget e 60 fps no título; não há prova de D1 porque a cena observada foi 2 e a screenshot é a superfície FORGE/SAMPLE PROGRAM.
- Claim permitido: `boot_emulador=ok`, `testado_em_emulador=sim` com evidencia parcial e gameplay observado parcial. `validado_budget`, audio e `ready_for_aaa` continuam falsos ou incompletos até os gates restantes.

## 6.1 Epoch 2026-09-08 — VRAM residency and closeout reconciliation

- `doc/vram_residency_report.json` foi emitido para a cena 3 vigente, preso à ROM `27deb2e6ed47948c1eb55b1e093a0d26b72bdd2257dc6cd0b03f0e89a2cc79cc` e aos hashes dos quatro recursos observados. BGB=500 tiles, BGA=100 e o conjunto de sprites byte-identico=15; total único=615 tiles / 19.680 bytes.
- A distinção é deliberada: o snapshot é uma medição `rescomp_origin_size_snapshot` vinculada à origem; não é `visual_vdp_dump`, não prova residency sustentada, DMA, performance ou ownership de VRAM durante a luta.
- O auditor de recursos foi ajustado para aceitar evidência VRAM explícita válida como fechamento do aviso estático de nametable/C sem apagar a telemetria de que existem chamadas C. `validation_report.json` passou a `errors=0`, e `code_loaded_tiles_unmeasured` saiu dos blockers.
- `vdp_scanline_simulator.py` passou no envelope D1: H40, 16 hardware sprite links, pico 160 pixels e 8 sprites por scanline, sem overflow; isso é envelope offline, não prova da cena viva.
- O blocker de regressão permanece honesto: `run_scene_regression.ps1` ainda é uma rota Win32/`blastem.exe` e não foi executado no host Linux; não foi criado baseline por substituição.

## 7. Epoch d1_scale_reset_20260905 — Kairo scale correction

- A raiz canonica foi confirmada e a raiz duplicada `[SGDK 211] [SGDK 211]` esta vazia; foi inventariada e preservada sem delecao. Ver `doc/duplicate_project_inventory_20260905.json`.
- A regua anterior de 24px/32x40 foi invalidada: `Jack 100` mede 74–76px visiveis, `Jack 410` 73–75px e `Ryo 100` 98–102px. Pela regra do GDD, Kairo exige no minimo 128px visiveis.
- Shootout A/B/C medido em composicao 320x224: A=102px, B=115px, C=128px. Os tres passaram os limites H40 na amostra mecanica sem FX; C=88x136 foi selecionado por ser o unico que cumpre o GDD. Ver `doc/art/kairo_vant/fighter_scale_benchmark_report.json` e `doc/art/kairo_vant/scale_correction_report.json`.
- Todos os caminhos Kairo 32x40, os probes em `res/` e o XPM foram reclassificados como `negative_evidence`; o XPM e `procedural_code_probe` e nao pode ser fonte de pixels. Ver `doc/art/kairo_vant/negative_case_reclassification_32x40.json`.
- A nova fonte de traducao 3/4 `kairo_vant_combat_idle_3quarter_visual_producer_output_v02_alpha_clean.png` tem alpha real e triagem aceita. Ela e fonte visual de traducao, nao sprite nativo. `im_lanczos3` foi escolhido apenas como underlay primario para reautoria; nao houve vencedor visual automatico.
- Animacao, `res/`, build novo e BlastEm desta epoch nao foram iniciados porque a reautoria nativa no grid C, fidelidade, palette/index0, tile/DMA, gate humano e budget ainda estao abertos. ROM v003 e evidencia historica stale para este reset de escala.
- Claim ceiling atual: `measured_visual_translation_candidate_and_mechanical_geometry_probe`; `ready_for_res`, `testado_em_emulador` para a nova pose e `ready_for_aaa` permanecem falsos.

## 8. Iteracao visual C-scale v02 fitted — 2026-09-05

- A guia assistida v02 foi gerada apenas como traducao/high-res e passou `source-audit`; a primeira reducao v02 falhou honestamente na escala, com bbox 118px. Ela foi mantida como diagnostico, nao como candidata C.
- O probe fitted foi obtido por recorte mecanico do foreground saneado e encaixe NEAREST em canvas 88x136. Medicao: bbox 87x128 (`y=8..135`), portanto cumpre exatamente o minimo GDD de 128px visiveis.
- Conversao tecnica: PNG indexado 4bpp, PLTE16, 15 cores visiveis, index0 transparente; content hash `f0ef93aeb7df2a2a8b7d734d16703c059724a468dc9329c014507c764b106135`. `validate_native_sprite_production.py` passou o registro `doc/art/kairo_vant/combat_idle_3quarter_v02_fitted_native_sprite_production_record.json`.
- Budget offline do candidato: 117 tiles unicos com flip dedup, 3744 bytes de tiles, 29 links de hardware; pior quadro amostrado com Kairo C + Ryo + quatro FX: 9 sprites e 216 pixels na scanline (limites H40 20/320). Isso e geometria offline, nao `validado_budget` de runtime.
- O workset permanece ativo no epoch `d1_scale_reset_20260905`, manifesto atualizado com SHA `913fc9c58a58075ae44a02ec2ff39c419bb7f9e6897fdb8b1f33975c91274650`; `res/`, build novo, animacao e BlastEm continuam bloqueados por autoria nativa, material topology, budget completo e aprovacao humana.
- Claim ceiling atual: `technical_candidate_measured_scale_and_offline_geometry`; nao e `visually_approved`, nao e `ready_for_res`, nao e `testado_em_emulador` para esta pose e nao e `ready_for_aaa`.
- Laudo visual objetivo: silhueta/guarda/contato/cyan/âmbar passam em 1x, mas rosto/olhar e fronteiras de material ficam `needs_review`; revisão em `rascunho/scale_correction_20260905/technical_candidate_visual_quality_review.json`. Próximo passo é reautoria nativa direta no grid C, não novo build.

- Duas tentativas adicionais de geração visual foram encerradas após contaminação: v03 trouxe glow/gradiente opaco e v04 assou checkerboard. Ambas estão em `rascunho/scale_correction_20260905/generation_failures/`, `reference_only`, fora do workset produtivo. A rota de geração foi fechada após duas falhas equivalentes; o próximo avanço causal é reautoria nativa sobre o guia C aprovado.
- O encaminhamento canônico `forge_art translate` foi executado e retornou exit 3 por design: não gera pixels nativos automaticamente. O registro foi corrigido para o alvo C de 88x136 em `rascunho/scale_correction_20260905/native_reauthoring_translate_block_v01.json`; permanece pendente um produtor nativo capaz.
- Auditoria de capacidade do host: somente GIMP 3.2.4 e ImageMagick estão disponíveis; GIMP headless expirou no preflight e ImageMagick é apenas mecânico. Não há backend nativo capaz no host. Ver `rascunho/scale_correction_20260905/native_authoring_capability_audit_v01.json`.

## 9. D1 contrato e runtime tecnico — 2026-09-06

- A especificacao de cenas foi alinhada ao parser canonico (`### Cena`) e compilou quatro cenas: menu, CS-C, CS-E e combate. Os contratos de CS-C/CS-E foram materializados em `doc/contracts/`; o linter production passou sem erros, mantendo `boot_mode=unsupported` ate a captura deterministica.
- O runtime D1 recebeu frame data tecnico para light/medium/heavy/special, startup/active/recovery, hitstun, hitstop, salto/gravidade, guarda, relogio de 60 segundos e melhor-de-tres. O especial consome 100 na ativacao e agenda o refill para dois frames apos o impacto; os probes continuam fora de qualquer claim visual final.
- `INPUT_repeat` foi adicionado com buffer estatico e atraso/período fixos; nenhuma alocacao dinamica foi introduzida. Cues de luta deixaram de interromper a musica XGM2.
- Build bridge SGDK 2.11 passou com exit code 0 e ROM `out/rom.bin` de 262144 bytes, SHA-256 `bd7a28cb8e2ee44c0be64af6a3bc5816b91057bcaef271276714f97fcc8534b0`.
- A captura PowerShell anterior foi classificada como `host_executor_route_mismatch`, não como falha do BlastEm. A captura Linux canônica foi executada e selada para a ROM vigente; o pacote contém screenshot, SRAM e burst GIF, sem `visual_vdp_dump` inventado.
- O boot agora consome o marcador SRAM `SBIS` (versao/tamanho/checksum) para selecionar deterministicamente as cenas existentes `MENU` ou `DEMO`; sem marcador, o boot normal permanece branding -> menu. Isso torna o alvo de captura alcançavel quando o host BlastEm estiver operacional.
- O compilador de contratos recebeu fallback `powershell.exe` -> `pwsh` no Linux e passa a gravar `compiled_from` relativo; a compilacao production agora fecha com `lint=ok` no host atual.

## 10. Captura Linux e seleção explícita de host — 2026-09-06

- Guard reexecutado: `agent_environment_status=ready`; host registrado como Linux BigLinux/Arch, KDE/Wayland, `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`, com Flatpak, `xdotool`, `import` e `convert` disponíveis.
- ROM congelada antes e depois da captura: SHA-256 `761bdd0f105f6a24e9deb21399bc3f8ad6f00ed7438d6ba5ee7b421a3688020f`, 262144 bytes.
- Rota selecionada: `linux_flatpak_blastem`; sessão `blastem-linux-20260906T111553Z-520147`; janela `SAMPLE PROGRAM - BlastEm - 60.1 fps`; commit Flatpak `c1f3f4435e9d009fa001322e26e73e785fe443fcedfae1f3187836685c602221`.
- Selo e freshness do pacote passaram. O screenshot semântico foi aceito; a captura observa somente o estado visível e não prova sozinha transição de cena, gameplay sustentado, áudio ou budget VDP.
- Criado `tools/sgdk_wrapper/select_blastem_capture_route.py`, integrado ao `scene_closeout_gate.ps1`, com fixtures permanentes para Linux/Windows/DISPLAY/host mismatch. `run_runtime_capture.ps1` agora falha cedo em host não Windows.
- Relatórios reconciliados: `emulator_session.json`, `evidence_closeout_report.json`, `code_review_report.json`, `memory bank` e changelog apontam para a mesma ROM. `ready_for_aaa=false` permanece correto.

## 11. Epoch golden_slice_visual_reset_20260906 — retomada de produção

- A rota Linux foi confirmada como resolvida: o erro anterior é `host_executor_route_mismatch_resolved`, não dependência gráfica ausente. Nenhum substituto Win32 foi instalado e nenhuma captura PowerShell foi usada.
- A fonte autoral de estágio Cinder Circuit foi persistida somente em `rascunho/golden_slice_visual_reset_20260906/cinder_circuit_visual_source_v01.png`, SHA-256 `281778896b3e7d6098686ac4bccf954d0a812d67ed34d9db56dfa8a60600c914`, status `ai_generated/visual_lab_control/visual_source`.
- O parsing semântico foi emitido e auditado: 4 regiões, IoU médio 1.0, classificação 1.0, layout 1.0, engine affordance 1.0. A direção declara BG_B atmosférico, BG_A reactor/arena, foreground composicional e WINDOW para HUD; não há terceiro plano.
- O controle de tradução produziu `cinder_circuit_translation_report.json`: basic=0.5864, elite underlay=0.4629, delta=-0.1235, `NO_ELITE_DELTA`. O underlay elite mediu 4269 tiles únicos e `WHOLE_IMAGE_CONVERSION_RISK`; não foi promovido. A rota correta é reautoria nativa modular por plano.
- O laudo de tilemap preliminar da variante de controle registrou 1120 tiles, 684 únicos com flip, 38.93% de deduplicação e 21.888 bytes estimados sob contrato transparente; ele permanece em `rascunho/translation/review` e não é ainda relatório canônico da ROM, pois o índice 0 do controle precisa ser refeito para o papel opaco da cena.
- O áudio recebeu correção causal de teardown: `AUDIO_stopAll()` agora zera `sCueFrames` antes de liberar PSG/PCM/XGM2. O validator canônico passou 7 recursos, 0 issues e 0.9% estimado da ROM; reprodução/arbitragem em cena pesada continuam pendentes.
- Auditorias read-only confirmaram: probes Kairo/C1 continuam proibidos como arte final; Jack/Kairo final, HUD, animações, residency/DMA, áudio e cena visual ainda não estão aprovados. Claim ceiling permanece `runtime_probe_passed_visual_epoch_failed`.

## 12. Captura Linux corrigida e reconciliada — 2026-09-08

- O guard de ambiente foi reexecutado no host Linux BigLinux/Arch KDE/Wayland (`DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`); nenhuma dependência Win32 foi instalada.
- `scene_closeout_gate.ps1` agora consome `out/evidence/blastem_current/evidence_manifest.json`, com fallback legado somente para compatibilidade. A rota Linux publica o bundle canônico sem classificá-lo como evidência fora do sandbox interno.
- A rota Linux foi recapturada com BlastEm Flatpak, sessão `blastem-linux-20260908T175405Z-2417733`, rota `linux_flatpak_x11_bridge`, alvo 3 observado como cena 3. O hash da ROM permaneceu `27deb2e6ed47948c1eb55b1e093a0d26b72bdd2257dc6cd0b03f0e89a2cc79cc` antes/depois.
- Artefatos históricos selados: screenshot, `save.sram`, `runtime_animation.gif`, `runtime_metrics.json` e VLAB parcial; o dump prova somente a telemetria exportada pela probe.
- `evidence_closeout_report`, `fresh_evidence_bundle_audit`, screenshot semantic gate e `emulator_session` estão coerentes com a ROM vigente. `ready_for_aaa` continua falso; blockers reais seguem VDP residency/tilemap/paleta, regressão, GDD, animação e arte final.

## 13. Contrato GDD e auditoria inicial de tilemap — 2026-09-08

- O GDD recebeu as seções substantivas de kit do jogador, regras sistêmicas,
  progressão/mapa, inimigos e riscos, ritmo, tutorial invisível, clímax,
  critérios visuais, ambição técnica e direção sonora. O validator deixou de
  emitir `gdd_substantial_insufficient`.
- A rota existente `analyze_tilemap_dedup_flags.py` auditou o BG_B atual
  `res/fighting/stage/room_0_bgb.png`: 1120 tiles, 500 únicos após flip,
  55.3571% de deduplicação, 16.000 bytes estimados e zero conflitos de
  sub-paleta. Os relatórios canônicos foram escritos em `out/logs/`.
- O escopo do laudo é somente o BG_B legado usado pela probe. Ele não aprova o
  BG_A, não promove a arte Cinder Circuit da staging e não fecha residency/DMA
  ou VRAM em runtime. A medição vinculada à ROM e o snapshot explícito de VRAM
  retiraram apenas o blocker estático `code_loaded_tiles_unmeasured`; não
  transformaram o snapshot em prova de runtime.

## 14. Epoch host-aware scene regression — 2026-09-09

- `run_scene_regression_host.py` selecionou a rota Linux Bash/Flatpak por host; os fixtures permanentes Linux/Windows/DISPLAY/host-command passaram. Nenhuma rota PowerShell, `System.Windows.Forms`, `blastem.exe`, Wine, Xvfb ou substituto foi usada para captura.
- A matriz agora declara seis cenas. `front_end_main_menu` e `first_playable_slice` foram capturadas com `scene_match=true`, mas ainda não têm baseline. `combat_cinder_circuit` compara por SHA de screenshot/SRAM/VLAB e passa. `branding_sequence` foi observado como cena 2, não como o alvo 0; CS-C e CS-E continuam sem protocolo/evidência selada.
- O relatório de regressão permanece `warn` e o validator continua com `errors=0`; isso não é redução de escopo nem aprovação AAA. O closeout stale é um blocker de governança temporal, separado dos blockers reais de arte, animação, áudio, performance, baselines e higiene.

## 15. Closeout reconciliado e hipótese visual rejeitada — 2026-09-09

- O guard foi reexecutado no host real Linux BigLinux/Arch, KDE/Wayland, com `DISPLAY=:0` e `WAYLAND_DISPLAY=wayland-0`; `agent_environment_status=ready` e `graph_status=fresh`. A classificação permanece `host_executor_route_mismatch_resolved`.
- O closeout executado sem rebuild, recaptura ou regressão adicional passou contrato de cena, grafo de recursos, validação, screenshot semântico, auditoria de promoção, fresh evidence, freshness, doc sync e learning capture. Resultado honesto: `status=warn`, `closeout_status=blocked`.
- `validation_report.json` está com `errors=0`, `warnings=15`; permanecem seis blockers: `orphan_project_root_entry`, `noncanonical_project_entry_name`, `visual_gate_blocked`, `visual_direction_failed`, `animation_gate_failed` e `scene_regression_incomplete`. O closeout também registra `scene_regression_failed`/`scene_regression_baseline_missing` para cenas que não foram observadas; não foram inventados captures ou baselines.
- A evidência canônica vigente dessa epoch anterior foi supersedida pela sessão Linux atual; o pacote histórico continha screenshot, SRAM, VLAB parcial, métricas e `audio.raw`, sem provar formato, mix, loop ou escuta humana.
- A nova hipótese ImageGen v05 foi copiada somente para `rascunho/scale_correction_20260909/`, SHA-256 `4a471b24e8caed917b14a71438361c1fcdada7aec47c60a0465757d8e2beef08`, e rejeitada por fundo luminoso/halo contaminante. O candidato assistido v07 em 88x136 também foi rejeitado visualmente por sparse/weak read. Nenhum dos dois entrou no workset produtivo, `res/`, build ou ROM.
- O budget vigente continua `cabe_com_recuo`: 946/1740 tiles source-bound (54,4%) e envelope H40 offline de 8 sprites/160 pixels/16 links, sem overflow; DMA por frame, tiles carregados por código e desempenho sustentado continuam não medidos. `ready_for_aaa=false`.

## 16. Reconciliacao final de identidade — 2026-09-09

- `assert_agent_environment.ps1` terminou `agent_environment_status=ready`, `graph_status=fresh` no host Linux BigLinux/Arch KDE/Wayland, com `DISPLAY=:0` e `WAYLAND_DISPLAY=wayland-0`.
- `evidence_closeout_report.json`, `emulator_session.json`, `code_review_report.json`, `validation_report.json`, `memory bank` e changelog apontam para a ROM vigente `a8ae5bea37ef1525725b6e3ea0299deb64318f79ba5f884bafa0dc2a3c1865d3`; captura `blastem-linux-20260909T124600Z-1554938`; `same_rom=true` e `same_evidence_session=true` no claim reconciliation.
- `audit_doc_sync` passou e `freshness_audit` está sem stale/missing; o route-fix segue classificado como `host_executor_route_mismatch_resolved`. A regressão de cenas foi encerrada em `6/6`; os blockers reais agora permanecem visual final/aprovação, animação, budget runtime, áudio escutável e densidade sustentada.

## 17. Regressao de cenas host-aware — 2026-09-09

- O seletor de captura passou a aceitar `capture_warmup_seconds` por cena; a rota Linux continua exclusivamente Bash/Flatpak/BlastEm e a rota Windows continua PowerShell/Win32.
- `branding_sequence`, `stage_intro_cinder_circuit` e `dialogue_cinematic_d1` agora usam SRAM bootstrap deterministico para os estados alcancaveis da ROM. As seis cenas foram capturadas em BlastEm Linux, com `scene_match=true`, manifest selado, screenshot, SRAM e VLAB parcial presentes.
- A regressao passou `6/6` por SHA-256 de screenshot. SRAM e VLAB continuam validados como artefatos selados, mas nao entram na comparacao visual porque carregam contadores/telemetria variaveis.
- Esta mudanca resolve apenas `scene_regression_incomplete`; nao aprova a qualidade da arte, nao mede densidade final, nao prova residencia carregada por codigo, nao prova mix/loop audivel e nao altera `ready_for_aaa=false`.
- O `blastem.log` da mesma sessão declara `48000 Hz`, estéreo e `32-bit float`; a cópia WAV derivada foi analisada sem reinterpretar o raw como PCM16. O sinal teve 32,789 s, pico -22,85 dBFS, RMS -29,17 dBFS, 84,39% de frames ativos e zero clipping. Isso fecha apenas integridade objetiva do sinal; escuta humana, BGM/mix/loop e SFX continuam pendentes.

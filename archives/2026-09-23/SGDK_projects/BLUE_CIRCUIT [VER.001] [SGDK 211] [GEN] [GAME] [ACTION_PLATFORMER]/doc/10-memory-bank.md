<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-07-20T01:13:00-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 9
- Ultimo build versionado: build_v005
- ROM vigente: `40b924f7895386458c7810204464fe47207c40b7f97d0c4585e840ee8d21bbf5` (`262144` bytes)
- Validation summary: validacao global ainda nao reclassificada; P1-003 fechado por provas dedicadas
- Blockers vigentes: visual_gate_blocked, visual_direction_failed, audio_validation_stale, emulator_evidence_stale, whole_image_unique_ratio_high_without_justification, freshness_audit_stale, scene_closeout_gate_stale
- Evidencia de emulador: janelas completas NTSC 900/900 e PAL 750/750
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=cena_3_observada performance=estavel_nas_janelas_observadas audio=nao_provado_driver_dummy hardware_real=nao_provado
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

**Ultima atualizacao:** 2026-07-20
**Fase atual:** `technical_ready_creative_blocked`; cena jogavel medida em janelas completas NTSC e PAL no BlastEm.
**Proxima fase:** resolver gate visual interno/closeout AAA ou aceitar o teto tecnico do vertical slice.

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

## 1. Estado Atual Do Projeto

### O que existe

- Projeto criado pelo template canonico em `SGDK_projects/BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]`.
- Contexto classificado como `aaa_game`, com teto `vertical_slice`.
- GDD, TDD, spec de cenas e QA foram resemeados para um jogo curto de acao/plataforma.
- Rota Vibe Playable documentada com bloqueio honesto antes de arte/runtime.
- Reports atuais em `out/logs/`: contexto, metodologia, higiene, visual delivery gate bloqueado e validation report bloqueado.
- Tres candidatos de revisao visual foram aprovados pelo humano como fonte para traducao VDP em `data/source_art/`:
  - `storyboard/blue_circuit_storyboard_candidate_v001.png`
  - `model_sheet/blue_circuit_model_sheet_candidate_v001.png`
  - `spritesheet/blue_circuit_spritesheet_candidate_v001.png`
- O contrato dos tres gates humanos foi registrado em `doc/contracts/human_visual_gate_plan.json`.
- Assets VDP ativos existem em `res/blue_circuit/` para title, stage BG/FG, player, inimigo, mini-boss e projetil.
- Runtime SGDK implementado em fatias pequenas: title, fase jogavel, correr, pular, atirar, inimigo comum, mini-boss, HUD e tela de fim.
- ROM vigente: `out/rom.bin`, SHA-256 `40b924f7895386458c7810204464fe47207c40b7f97d0c4585e840ee8d21bbf5`, 262144 bytes, build limpo no contêiner SGDK 2.11.
- Evidencia BlastEm vigente:
  - `out/evidence/blastem/screenshot.png`
  - `out/evidence/blastem/save.sram`
  - `out/evidence/blastem/visual_vdp_dump.bin`
  - `out/evidence/blastem_pal/` (prova regional complementar)
  - `out/logs/runtime_metrics.json`
  - `out/logs/runtime_metrics_pal.json`
  - `out/logs/performance_capture_report.json`
  - `out/logs/performance_budget_report.json`
  - `out/logs/emulator_session.json`
  - `out/logs/blastem_evidence.json`
  - `out/logs/evidence_closeout_report.json`
- Captura: `target_scene=3`, `runtime_scene_id=3`; NTSC 900/900, P95 44, 0 over-budget, 61.0 fps no titulo; PAL 750/750, P95 17, 0 over-budget, 50.3 fps no titulo. Performance fica `estavel_nas_janelas_observadas`; audio e hardware real nao foram provados.

### O que nao existe ainda

- Aprovacao visual AAA interna ainda nao existe: `visual_gate_blocked` e `visual_direction_failed` permanecem ativos pelo juiz estetico.
- `scene_closeout_gate_report.json` ficou `stale` depois do refresh de reports; closeout AAA segue `warn`, nao `ok`.
- Performance das demais cenas nao foi medida por P1-003; o claim sustentado limita-se a `first_playable_slice`/cena 3.
- `gameplay_rom_aprovada` permanece `false`; ha evidencia tecnica de emulador, mas nao aprovacao de produto final.
- Nenhum asset procedural/debug/lab deve ser tratado como final fora da linhagem aprovada e registrada.

### Escopo aprovado

- Title screen.
- Uma fase curta `stage_01_blue_circuit`.
- Um personagem jogavel com correr, pular e atirar.
- Um inimigo comum `line_sentry`.
- Um mini-boss simples `breaker_core`.
- Tela de fim.

### Blockers QA ativos

- `visual_gate_blocked`: gate visual interno bloqueia promocao AAA.
- `visual_direction_failed`: juiz estetico ainda reprova a direcao visual como entrega AAA.
- `scene_closeout_gate_stale`: closeout foi gerado, mas ficou stale apos refresh posterior de reports.
- Estado maximo aceito pelo validator: `technical_ready_creative_blocked`.

## 2. Decisoes De 2026-06-25

- Classificar como `aaa_game`, nao `technical_demo`, porque o pedido define jogo jogavel com fase, title, fim e mini-boss.
- Manter teto `vertical_slice`, nao `ready_for_aaa`.
- Usar identidade autoral de circuito industrial energizado, sem copiar IP protegida.
- Bloquear runtime de entrega ate source premium -> aprovacao humana -> conversao VDP -> build -> BlastEm.
- Tratar o mini-boss como single body FSM; boss modular fica fora do escopo.
- Tratar slopes, one-way, dash, charge shot, armas alternadas, save e multiplas fases como fora do primeiro slice.
- Declarar `camera_scroll_management` como tecnica documentada para a fase; promocao bloqueada ate contrato, budget, build e BlastEm.

## 3. Decision Log Conservador

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia | Proximo gate |
|------|----------|---------|------------------------|-----------|--------------|
| 2026-06-25 | Abertura | `aaa_game` com teto `vertical_slice` | `technical_demo`, `ready_for_aaa` | prompt humano + `project_context_manifest.json` | validar contexto |
| 2026-06-25 | Direcao visual | circuito industrial azul/ciano com acentos amber/magenta/lime | silhueta, arma, musica, layout ou paleta de IP protegida | GDD/brief | fonte premium |
| 2026-06-25 | Runtime | manter bloqueado antes de assets e contratos | prototipo com placeholder final | `runtime_admission_report.json` | gate visual |
| 2026-06-25 | Camera | selecionar `camera_scroll_management` como tecnica documentada | camera paralela por layer, parallax sem budget | `doc/technique_usage_manifest.json` | camera_behavior_contract |
| 2026-06-25 | Validacao | aceitar `validate_resources=blocked` como estado correto pre-arte | forcar res_graph/audio de template como aprovacao do jogo | `out/logs/validation_report.json` | fonte premium |
| 2026-06-27 | Gates humanos | aprovar storyboard, model sheet e spritesheet para traducao VDP | promover PNG high-res direto para `res/` | `doc/human_approval_record.md` | conversao VDP |
| 2026-06-27 | Runtime + BlastEm | implementar bootstrap `SBIS`, runtime jogavel e capturar cena 3 no BlastEm com audio dummy | declarar pronto sem emulador; aceitar captura em menu como gameplay | `out/logs/emulator_session.json`, `out/evidence/blastem/screenshot.png`, `out/evidence/blastem/save.sram` | resolver gate visual/closeout AAA |
| 2026-07-20 | P1-003 performance | ampliar MDRT para janela regional completa, medir DMA antes do VBlank e exigir flag explicita de conclusao | manter teto de 32 amostras; promover captura parcial; aceitar configuracao regional nao confirmada pela ROM | `out/logs/performance_capture_report.json`, `out/logs/performance_budget_report.json`, bundles NTSC/PAL | P1-004 hardware real/FPGA |
| 2026-07-20 | P1-004 hardware gate | implementar protocolo e gate de ROM/captura/atestacao, mantendo o teste externo bloqueado | inventar console, revisao, video ou avaliacao humana; tratar BlastEm como hardware real | `doc/hardware_test_protocol.md`, `out/logs/hardware_test_gate_report.json`, `out/logs/rom_mastering_report.json` | executar sessao externa em console/FPGA |
| 2026-07-20 | aprendizado e curadoria | capturar falhas, sucessos e candidatos com maturidade e gatilhos de retomada, sem promocao automatica | deixar as licoes apenas em conversa; universalizar constantes do projeto; aplicar patch canonico sem generalizacao | `doc/agent_learning/learning_ledger.json`, `doc/agent_learning/canonical_promotion_review.md` | fechar P2-001 e retomar candidatos quando seus gatilhos forem cumpridos |

## 4. Roteiro De Fechamento Do Primeiro Slice

1. Passar `validate_project_context.ps1`, `validate_project_methodology.ps1` e `validate_project_hygiene.ps1`.
2. Validar humanamente Gate 1 - Storyboard. Concluido em 2026-06-27.
3. Validar humanamente Gate 2 - Model sheet. Concluido em 2026-06-27.
4. Validar humanamente Gate 3 - Spritesheet. Concluido em 2026-06-27.
5. Converter assets aprovados para SGDK/VDP e gerar laudos visuais/budget. Concluido tecnicamente em 2026-06-27.
6. Implementar runtime em fatias pequenas com fixtures antes do codigo. Concluido em 2026-06-27.
7. Buildar pelo wrapper central. Concluido: build_v004.
8. Capturar no BlastEm. Concluido: cena 3, screenshot + SRAM.
9. Rodar freshness e scene closeout. Concluido com freshness `ok` e closeout `warn`.

## 5. Referencias Rapidas

- Brief: `doc/00-project-brief.md`
- GDD: `doc/11-gdd.md`
- TDD: `doc/15-tdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- QA: `doc/14-plano-de-provas-qa.md`
- Asset register: `doc/18-asset-register.json`
- Diretrizes agente: `doc/00-diretrizes-agente.md`

## 6. Aprendizado Capturado E Retomavel

- `doc/agent_learning/failure_patterns.md` registra falsos positivos, captura
  parcial, ownership de SRAM, drift documental e vazamento de escopo de claim.
- `doc/agent_learning/success_patterns.md` registra bundles por sessao,
  janelas NTSC/PAL completas, bloqueio externo honesto e status por eixo.
- `doc/agent_learning/skill_promotion_candidates.md` mantem candidatos de
  doc sync, retomada independente, probe parametrico, SRAM selada e adocao do
  gate de hardware.
- `doc/agent_learning/canonical_promotion_review.md` classifica o que ja esta
  integrado e o que deve aguardar maturidade.
- O Capture consolidou 15 licoes e 10 candidatos; 6 propostas foram
  deduplicadas para owners existentes, todas `not_applied`. Schema, Audit
  read-only e regressao 34/34 passaram.
- Ordem de retomada aplicavel ao projeto: P2-001 doc sync, P2-002 contexto
  independente e depois candidatos com evidencia cross-project ou externa.
- Nenhuma captura local promove automaticamente o framework canonico.

## 7. Revalidacao obrigatoria dos sprites — 2026-07-24

- O parecer anterior dos strips foi formalmente retraido como
  `technical_pass_visual_fail`: dimensoes, paleta e grid nao provavam
  anatomia, integridade ou animacao.
- O gate obrigatorio agora e `sprite_artifact_report.v2`, com clipping de
  borda, ilhas soltas, anatomia, pivot, contato de pes e delta entre frames.
- Os strips antigos foram preservados somente como evidencia historica em
  `out/evidence/sprite_rework_20260723/original_res/`; reutilizacao como fonte,
  runtime ou evidencia esta proibida por
  `doc/contracts/sprite_strip_rejection_report_20260723.json`.
- O player v002 foi reconstruido em grid 24x32 a partir do model sheet
  aprovado. O auditor mediu 14 frames, 0 findings e 0 blockers.
- Contact sheet e GIFs de idle, corrida, tiro e salto vivem em
  `out/evidence/sprite_rework_20260723/`.
- Build Linux/Wine SGDK 2.11: ROM de 262144 bytes, SHA-256
  `b2fbb1bcc916bd30e26693064e4d5371df7ede2216b72b0a85dd6700c022e0b5`.
- Sessao BlastEm fresca `blastem-linux-20260724T034450Z-505289`, cena 3:
  screenshot, SRAM, VLAB e metricas selados com `same_session=true` e zero
  blockers. O personagem v002 foi observado completo em runtime.
- Decisao: `sprite_visual_pass` somente para o player v002 e sua integracao
  estatica. `ready_for_aaa=false`; corrida, tiro e salto ainda nao possuem
  captura interativa no emulador e nao podem ser alegados como tal.
- Parecer escopado:
  `doc/contracts/sprite_revalidation_report_20260724.json`.

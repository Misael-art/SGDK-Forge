# Changelog de aprendizado - 2026-07-18

Status: `diagnostic_registered_no_runtime_promotion`

## Diagnostico global do agente SGDK

- registrado o laudo em
  `doc/agent_learning/agent_capability_diagnostic_2026-07-18.md`;
- criado backlog machine-readable em
  `doc/agent_learning/agent_capability_remediation_backlog_2026-07-18.json`;
- classificacao consolidada: `functional_with_human_supervision`;
- claim ceiling: `technical_vertical_slice_candidate`;
- `ready_for_aaa=false`;
- blocker dominante: falso positivo de captura branca em BLUE_CIRCUIT;
- registrados owners, dependencias, evidencias e acceptance checks para P0-P2;
- registrados blockers de ambiente: PowerShell ausente, schemas sem
  `jsonschema`, 13 hashes lifecycle divergentes e falta de reexecucao BlastEm;
- nenhuma ROM, tecnica, asset, report de projeto ou claim AAA foi promovido.

## Prompt de execucao persistente

- criado `doc/agent_learning/agent_remediation_execution_prompt_2026-07-18.md`;
- o prompt obriga infraestrutura Linux reproduzivel, correcao em ordem P0-P2,
  geracao e conversao real de assets, evidencia BlastEm e decisao conservadora;
- ele nao permite declarar exito total sem todos os acceptance checks,
  evidencia fresca e jogo curto completo;
- bloqueio externo real deve ser reportado como tal, nunca mascarado como
  entrega parcial ou sucesso.

## Regra de continuidade

O proximo agente deve iniciar por `P0-001` ou por outro item
`ready_for_assignment` sem dependencias, nunca pela construcao do jogo completo.
O item `P1-006` permanece bloqueado ate os gates fundamentais serem corrigidos.

## P0-001 concluido — integridade semantica de screenshot

- criado gate canonico com schema e report machine-readable;
- captura quase branca de BLUE_CIRCUIT rejeitada com
  `blank_or_low_information_capture`;
- controles escuros de Celestial Chase Revive e MUGEN aceitos sem promover
  gameplay ou performance;
- captura, selagem de evidencia, closeout de cena e validacao geral integrados;
- regressao Python 3/3, integracao PowerShell e closeout passaram;
- suite de schemas passou 81/81 no ambiente Python provisionado;
- validacao real forçou visual/gameplay/performance para falso ou `unproven`;
- evidencia consolidada em
  `doc/agent_learning/p0_001_screenshot_semantic_remediation_report_2026-07-18.json`;
- backlog atualizado: `P0-001=completed`, `P0-002=ready_for_assignment`;
- nenhuma promocao de ROM, runtime, tecnica ou `ready_for_aaa` foi realizada.

## P0-002 concluido — menor status provado

- criado reconciliador canonico e schema machine-readable;
- gate bloqueado versus claim positivo agora produz `report_status_conflict`;
- captura parcial impede performance estavel;
- metricas perceptuais zeradas impedem `creative_ready=true`;
- ROM e evidence session ausentes ou divergentes bloqueiam a decisao;
- BLUE_CIRCUIT foi rebaixado conservadoramente para claims falsos ou
  `unproven`;
- regressao passou 4/4 e o report real passou no schema;
- evidencia consolidada em
  `doc/agent_learning/p0_002_claim_reconciliation_report_2026-07-18.json`;
- backlog atualizado: `P0-002=completed`, `P0-003` e `P0-005` prontos;
- nenhuma promocao de runtime ou `ready_for_aaa` foi realizada.

## P0-003 concluido — ambiente de schemas reproduzivel

- adicionados manifest, lock com hashes e bootstrap local de dependencias;
- `jsonschema==4.25.1` reconstruido em target limpo sem instalacao global;
- criado entrypoint Linux e shim controlado para scripts legados;
- falha de bootstrap agora gera blocker explicito, sem skip silencioso;
- runner canonico passou 84/84 schemas e 12/12 checks complementares;
- `combined_status=passed` registrado em
  `out/remediation/P0-003/schema_mode/contract_gates_report.json`;
- evidencia consolidada em
  `doc/agent_learning/p0_003_reproducible_schema_environment_report_2026-07-18.json`;
- backlog atualizado: `P0-003=completed`, `P0-004=dominant_blocker`;
- nenhuma promocao de runtime ou claim AAA foi realizada.

## P0-004 concluido — lifecycle hash deterministico

- auditados os 13 payloads legados contra o commit em que foram introduzidos;
- todos foram classificados como `registry_obsolete_at_introduction`, sem
  alteracao de payload e sem evidencia de corrupcao;
- unificado o hash entre Python e PowerShell com ordem ordinal UTF-8,
  caminhos relativos e normalizacao LF;
- registry atualizado somente apos o review machine-readable;
- framework validado com 47 skills ativas e 13 legadas;
- auditor lifecycle passou com zero erros e a restauracao legada passou;
- evidencia consolidada em
  `doc/agent_learning/p0_004_legacy_hash_reconciliation_report_2026-07-19.json`;
- backlog atualizado: `P0-004=completed`, `P0-005=dominant_blocker`;
- nenhuma promocao de ROM, runtime ou claim AAA foi realizada.

## P0-005 concluido — evidencia fresca no BlastEm Linux

- provisionado BlastEm oficial via Flatpak com commit fixado;
- criado executor Linux com ROM de basename unico, janela renderizada e
  warm-up suficiente para exportar VLAB;
- selada a sessao `blastem-linux-20260720T023600Z-152199` com ROM, screenshot,
  SRAM, VDP dump e metricas no mesmo `session_id`;
- gate semantico do screenshot passou e freshness ficou sem blockers;
- tentativas sem VLAB ou com janela transitoria foram rejeitadas e preservadas;
- closeout passou a revalidar tamper, hash da ROM vigente e coerencia de
  sessao;
- regressao Python 4/4, regressao PowerShell e schemas passaram;
- mastering permaneceu `mastering_needs_fix`, sem promocao indevida;
- evidencia consolidada em
  `doc/agent_learning/p0_005_fresh_same_session_evidence_report_2026-07-19.json`;
- backlog atualizado: `P0-005=completed`, `P1-001=dominant_blocker`.

## P1-001 concluido — discovery de arte em laboratorios aninhados

- criado o cenario `4_lab_nested_art_review` no diagnostico de arte;
- inventarios de fonte, evidencia, `res` ativo, trabalho, analise e bins
  gerados agora possuem ownership separado;
- discovery confinado ao root ignora symlinks e nao atravessa diretorios
  externos;
- compatibilidade Pillow atualizada sem o aviso de `Image.getdata`;
- regressao sintetica passou 46/46, incluindo subprojeto aninhado, hygiene
  manifest, symlink externo e `DeprecationWarning` como erro;
- estudo MUGEN real passou de falso `3_no_art` para
  `4_lab_nested_art_review`, com 90 artefatos e um viewer SGDK identificado;
- evidencia consolidada em
  `doc/agent_learning/p1_001_nested_lab_art_discovery_report_2026-07-19.json`;
- backlog atualizado: `P1-001=completed`, `P1-002=dominant_blocker`;
- nenhuma promocao de runtime, budget, qualidade visual ou AAA foi realizada.

## P1-002 tecnico concluido — XGM2 FM/PSG, review humano pendente

- criada musica VGM original com YM2612 FM + SN76489 PSG e recurso XGM2 real;
- removidos score PCM_CH1 e writes PSG diretos; ownership centralizado;
- PCM_CH2/CH3 receberam prioridades e budget explicitos;
- adicionada telemetria AUD2, extrator testado 4/4 e analise objetiva de WAV;
- `validate_audio` passou com 10 recursos, zero issues e 0,96% do budget;
- ROM `8eeef763...d450` buildada via SGDK Docker v2.11;
- BlastEm atual provou 8 janelas music+SFX e 5/5 SFX aceitos;
- captura de 24,064 s passou sinal/clipping; um missed frame ficou como warning;
- evidencia consolidada em
  `doc/agent_learning/p1_002_xgm2_fm_psg_runtime_report_2026-07-19.json`;
- backlog atualizado para `blocked_external_human_review`, com `P1-003` como
  proximo blocker dominante;
- nenhuma aprovacao auditiva humana ou promocao AAA foi fabricada.

## P1-003 concluido — janelas completas NTSC e PAL

- ampliado o probe MDRT de 32 para 900 amostras, com alvo PAL de 750;
- adicionados contrato de conclusao, regiao, P95, sprites e fila DMA;
- corrigida corrupcao pos-exportacao causada pelo heartbeat sobre a SRAM;
- parser endurecido e regressao aprovada em 10/10 casos;
- build SGDK Docker v2.11 gerou ROM `40b924f7...d21bbf5`;
- BlastEm NTSC fechou 900/900 a 61.0 fps, P95 44 e zero over-budget;
- BlastEm PAL `-r E` fechou 750/750 a 50.3 fps, P95 17 e zero over-budget;
- os dois bundles passaram freshness; screenshot e schemas passaram;
- evidencia consolidada em
  `doc/agent_learning/p1_003_full_window_performance_report_2026-07-20.json`;
- backlog atualizado: `P1-003=completed`, `P1-004=dominant_blocker`;
- nenhuma promocao de audio, hardware real, FPGA, release ou AAA foi feita.

## P1-004 gate concluido — execucao externa pendente

- adicionados schema, protocolo e validador de hardware/FPGA;
- o gate exige ROM igual ao BlastEm, dispositivo/regiao/revisao, metodo de
  carga, captura de boot/input/audio/gameplay e decisoes explicitas;
- regressao passou 3/3, incluindo rejeicao por hash divergente;
- mastering confirmou header JUE, alinhamento e checksum SGDK valido;
- evidencia consolidada em
  `doc/agent_learning/p1_004_hardware_gate_report_2026-07-20.json`;
- backlog atualizado para `blocked_external_hardware_evidence`, com P1-005
  como proximo item executavel;
- nenhum teste fisico, FPGA, video ou atestacao foi fabricado.

## P1-005 concluido — metricas de autonomia derivadas

- criado ledger schema com lifecycle de sessao/tarefa e intervencoes humanas;
- gravador atomico nao aceita texto humano livre nem conteudo sensivel;
- derivador calcula completion, blocked, rework, first-attempt e autonomia a
  partir dos eventos;
- regressao passou 3 checks e cobre intervencao `correction` classificada;
- amostra real registrou 9 eventos e gerou taxas sem preenchimento manual;
- relatorio sempre mantem qualidade `unproven` e `ready_for_aaa=false`;
- evidencia consolidada em
  `doc/agent_learning/p1_005_autonomy_instrumentation_report_2026-07-20.json`;
- backlog atualizado: `P1-005=completed`; P2-001 e o proximo item executavel.

## 2026-07-20 — checkpoint de curadoria e retomada por maturidade

- registrada autorizacao humana para capturar os aprendizados maduros da
  jornada e retomar a curadoria quando os gatilhos objetivos forem cumpridos;
- criado checkpoint humano e machine-readable em
  `doc/agent_learning/remediation_learning_curation_checkpoint_2026-07-20.md`
  e `.json`;
- o checkpoint classifica P0-001 a P2-003 como integrado, comprovado
  localmente, bloqueado externo, pendente ou nao executado;
- o backlog passou a apontar para o checkpoint, ledger do BLUE_CIRCUIT e ordem
  de retomada P2-001 -> P2-002 -> P2-003 -> P1-002 -> P1-004 -> P1-006;
- os aprendizados do BLUE_CIRCUIT foram registrados em failure patterns,
  success patterns, promotion candidates e canonical promotion review;
- o Capture gerou 15 licoes e 10 candidatos; 6 propostas apontam para owners
  existentes, todas permanecem `not_applied`;
- schema do ledger e Audit read-only passaram; regressao do ciclo passou 34/34;
- promocao automatica continua proibida: cada patch futuro ainda exige
  evidencia, limite, generalizacao e regressao;
- nenhum claim de ROM, tecnica, hardware, release ou AAA foi promovido.

# 14 - Plano de Provas QA Canonicas - BLUE_CIRCUIT [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

**Objetivo:** tornar explicito como este projeto pretende provar os gates finais do wrapper sem depender de memoria implicita.

**Regra:** se um eixo ainda nao tem evidencia minima definida, ele deve permanecer `nao_testado` e o blocker precisa ficar documentado aqui e no `doc/10-memory-bank.md`.

## 1. Mapa dos Gates

### Gate `documentado`

Passa quando:

- `project_context_manifest.json` classificado como `aaa_game`.
- GDD, TDD, spec de cenas, QA, asset register, memory e changelog atualizados.
- Metodologia sem claims `review_required`.

Status atual: em validacao.

### Gate `visual_lab_aprovado`

Este gate sobe apenas quando todas as condicoes abaixo forem verdadeiras:

- fonte premium local em `data/source_art/` com hash e autorizacao/licenca.
- aprovacao humana registrada em `doc/human_approval_record.md` para os tres
  marcos definidos em `doc/contracts/human_visual_gate_plan.json`:
  storyboard, model sheet e spritesheet.
- `art_gameplay_direction_gate` sem blocker de direcao.
- assets convertidos para SGDK/VDP sem placeholder final.
- `visual_delivery_gate_report.json` sem blockers criativos.

Status atual: candidatos visuais criados, aguardando validacao humana.

### Gate `buildado`

Este gate sobe apenas quando:

- build canonico via wrapper gerar `out/rom.bin`.
- `validation_report.json` existir e referenciar a ROM vigente.
- changelog e memory registrarem hash/tamanho da ROM.

Status atual: nao executado.

### Gate `testado_em_emulador`

Este gate sobe apenas quando:

- BlastEm abrir a ROM vigente.
- screenshot dedicada for capturada.
- `save.sram` e `visual_vdp_dump.bin` forem coletados quando o bloco visual canonico estiver ativo.
- `emulator_session.json`/`qa_emulator_report.json` apontarem para o mesmo hash da ROM.

Status atual: nao executado.

### Gate `gameplay_rom_aprovada`

Este gate sobe apenas quando:

- title -> stage -> mini-boss -> ending for observado.
- input publicado for confirmado pela ROM quando houver roteiro automatizado.
- gameplay_basico estiver funcional.
- performance estiver estavel.
- audio estiver ok ou explicitamente not_implemented para a fase.

Status atual: nao executado.

### Gate `ready_for_aaa`

Nao e objetivo desta rodada. Permanece false ate todos os gates tecnicos, visuais, budgetarios e de emulator evidence passarem.

## 2. Plano Inicial de Evidencia

### Visual

- Cena-alvo do gate visual: `title_screen` e `stage_01_blue_circuit`.
- Baseline canonico: ainda nao existe.
- Tipo de captura: screenshot BlastEm + VDP dump quando disponivel.
- Referencia estetica: somente eixos genericos de ritmo/leitura 16-bit; nenhuma IP vira fonte visual.
- Candidatos de review:
  - `data/source_art/storyboard/blue_circuit_storyboard_candidate_v001.png`
  - `data/source_art/model_sheet/blue_circuit_model_sheet_candidate_v001.png`
  - `data/source_art/spritesheet/blue_circuit_spritesheet_candidate_v001.png`
- O que ainda falta: aprovacao humana dos tres gates, conversao VDP,
  visual delivery report limpo e evidencia BlastEm.

### Audio

- Ha audio final declarado em `.res`? nao para o jogo novo.
- Relatorio esperado quando houver audio: `out/logs/audio_validation_report.json`.
- Prova funcional em emulador: operador registra `audio=ok` apenas depois de ouvir SFX/BGM na ROM vigente.
- O que ainda falta: audio design, fontes/patches autorais e validacao.

### Hardware Real

- Hardware alvo: Mega Drive/Genesis real fica futuro; BlastEm fecha gate atual.
- Operador responsavel: humano futuro.
- Evidencia minima: foto/video/log/hash quando for solicitado.
- Hash da ROM a registrar: inexistente nesta sessao.
- O que ainda falta: ROM buildada.

### Freshness e Closeout

- Auditoria esperada: `out/logs/freshness_audit_report.json`.
- Orquestrador esperado no fechamento: `out/logs/scene_closeout_gate_report.json`.
- Sequencia minima: docs -> visual source -> VDP conversion -> build -> validation -> runtime capture -> scene regression -> freshness -> closeout.
- O que ainda falta: todos os artefatos pos-documentacao.

## 3. Blockers Atuais

- `visual_lab_aprovado`: `awaiting_human_storyboard_validation`,
  `awaiting_human_model_sheet_validation`,
  `awaiting_human_spritesheet_validation`, `blocked_no_vdp_conversion`.
- `build`: `not_run`.
- `blastem`: `not_run`.
- `gameplay_basico`: `not_implemented`.
- `performance`: `nao_medido`.
- `audio`: `not_implemented`.
- `hardware_real`: `not_applicable_for_current_gate`.
- `freshness_audit`: pendente apos primeira ROM/captura.
- `scene_closeout_gate`: pendente apos primeira cena candidata.
- `ready_for_aaa`: `blocked_by_design`.

## 4. Atualizacao Operacional

Sempre que um eixo mudar de estado:

1. Atualize este documento.
2. Atualize `doc/10-memory-bank.md`.
3. Registre a mudanca em `doc/changelog/changelog.md`.
4. Reexecute o wrapper canonico para refletir o novo estado em `validation_report.json`.
5. Rode `freshness_audit.ps1` para garantir que os artefatos medem a mesma ROM.
6. No fechamento de cena, rode `scene_closeout_gate.ps1` ou registre a justificativa conservadora para nao rodar.

## 5. Vibe Playable Birth Seed

- `vibe_playable_birth_seed=documented_user_request`
- `visual_delivery=blocked_no_premium_source`
- `runtime_admission=blocked`
- `ready_for_aaa=false_until_real_evidence`

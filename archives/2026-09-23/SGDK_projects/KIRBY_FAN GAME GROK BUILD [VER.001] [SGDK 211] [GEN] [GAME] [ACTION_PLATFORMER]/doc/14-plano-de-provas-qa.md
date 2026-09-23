# 14 - Plano de Provas QA Canonicas - KIRBY_FAN GAME GROK BUILD [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_PLATFORMER]

**Objetivo:** tornar explicito como este projeto pretende provar os gates finais do wrapper sem depender de memoria implicita.

**Regra:** se um eixo ainda nao tem evidencia minima definida, ele deve permanecer `nao_testado` e o blocker precisa ficar documentado aqui e no `doc/10-memory-bank.md`.

---

## 1. Mapa dos Gates

### Gate `visual_lab_aprovado`

Este gate sobe apenas quando todas as condicoes abaixo forem verdadeiras:

- `buildado=true`
- `changelog_ready=true`
- `scene_regression_ready=true`
- `visual_gate_ready=true`
- `blastem_gate=true`
- `emulator_evidence_stale=false`
- `freshness_audit_report.json` sem stale bloqueante nos artefatos visuais/captura

Evidencia minima esperada:

- `out/logs/validation_report.json`
- `out/logs/scene_regression_report.json`
- `out/logs/emulator_session.json`
- `out/logs/freshness_audit_report.json`
- `out/logs/scene_closeout_gate_report.json` no fechamento de cena
- artefatos de captura coerentes com a cena alvo

### Gate `audio_validation_ready`

Este gate so e obrigatorio quando houver audio declarado em `.res`.

Evidencia minima esperada:

- `out/logs/audio_validation_report.json`
- status `pass=true`
- relatorio nao obsoleto frente aos insumos de audio

### Gate `gameplay_rom_aprovada`

Este gate sobe apenas quando todas as condicoes abaixo forem verdadeiras:

- `visual_lab_aprovado=true`
- `qa_axes.gameplay_basico in {funcional, ok}`
- `qa_axes.performance=estavel`
- `qa_axes.audio=ok`
- `qa_axes.hardware_real` fora de `nao_testado`, `stale`, `falha`, `nao_medido`, `invalido`, `ausente`

### Gate `ready_for_aaa`

Este gate sobe apenas quando todas as condicoes abaixo forem verdadeiras:

- `summary.errors=0`
- `gameplay_rom_aprovada=true`
- `validado_budget=true`
- `scene_closeout_gate_report.json` status `ok`

---

## 2. Plano Inicial de Evidencia

Preencha este bloco antes de tentar promover os gates finais.

### Visual

- Cena-alvo do gate visual: [scene_id]
- Baseline canonico: `doc/baselines/[scene]`
- Tipo de captura: [evidence_bundle/screenshot/etc]
- Benchmark ou referencia estetica: [arquivo/perfil]
- O que ainda falta: [lacuna atual]

### Audio

- Ha audio declarado em `.res`? [sim/nao]
- Relatorio esperado: `out/logs/audio_validation_report.json`
- Prova funcional em emulador: [como o operador registra `audio=ok`]
- O que ainda falta: [lacuna atual]

### Hardware Real

- Hardware alvo: [console/cart flash/etc]
- Operador responsavel: [nome]
- Evidencia minima: [foto/video/hash/log]
- Hash da ROM a registrar: [sha256]
- O que ainda falta: [lacuna atual]

### Freshness e Closeout

- Auditoria esperada: `out/logs/freshness_audit_report.json`
- Orquestrador esperado no fechamento: `out/logs/scene_closeout_gate_report.json`
- Sequencia minima: build -> scene_contract_compiler -> res_graph_audit -> validate_resources -> runtime_capture -> scene_regression -> freshness_audit
- O que ainda falta: [lacuna atual]

---

## 3. Blockers Atuais

Use esta secao para manter os blockers em linguagem objetiva.

- `visual_lab_aprovado`: [ok ou blocker]
- `audio`: [ok ou blocker]
- `hardware_real`: [ok ou blocker]
- `freshness_audit`: [ok ou blocker]
- `scene_closeout_gate`: [ok ou blocker]
- `ready_for_aaa`: [ok ou blocker]

---

## 4. Atualizacao Operacional

Sempre que um eixo mudar de estado:

1. Atualize este documento.
2. Atualize `doc/10-memory-bank.md`.
3. Registre a mudanca em `doc/changelog/changelog.md`.
4. Reexecute o wrapper canonico para refletir o novo estado em `validation_report.json`.
5. Rode `freshness_audit.ps1` para garantir que os artefatos medem a mesma ROM.
6. No fechamento de cena, rode `scene_closeout_gate.ps1` ou registre a justificativa conservadora para nao rodar.

---

## 5. Vibe Playable Birth Seed

- `vibe_playable_birth_seed=structural_only`
- `visual_delivery=blocked_no_premium_source`
- `ready_for_aaa=false_until_real_evidence`

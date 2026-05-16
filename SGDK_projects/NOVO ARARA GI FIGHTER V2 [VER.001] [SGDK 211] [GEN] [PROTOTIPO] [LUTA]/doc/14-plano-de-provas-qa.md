# 14 - Plano de Provas QA Canonicas - NOVO ARARA GI FIGHTER V2 [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]

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

## 2. Evidencia Atual

Estado observado em 2026-05-16 para ROM `93d02b59721980b69f2d7862d0866818bc371cdd2b71e2984f4261a3c9fb750e`.

### Visual

- Cena-alvo do gate visual: `scene_id=2` (`lapa_open_mat_demo`)
- Captura: `out/evidence/blastem/screenshot.png`
- Fonte premium: `data/source_art/` com `premium_source_manifest.json`
- Gate critico: `out/logs/visual_delivery_gate_report.json`
- Observacao: `visual_vdp_dump.bin` nao e gerado neste slice; a ROM exporta MDRT em SRAM.

### Audio

- Ha audio declarado em `.res`? nao
- Estado: `audio_validation.state=not_required`, `qa_axes.audio=ok`
- Proximo slice: adicionar SFX/music e entao exigir `audio_validation_report.json`

### Hardware Real

- Hardware alvo deste gate: BlastEm como emulador de referencia obrigatorio do workspace
- Evidencia minima: `out/logs/blastem_evidence.json`, `out/logs/emulator_session.json`, `out/evidence/blastem/screenshot.png`, `out/evidence/blastem/save.sram`
- Hash da ROM registrado: `93d02b59721980b69f2d7862d0866818bc371cdd2b71e2984f4261a3c9fb750e`
- Estado: `blastem_gate=true`, `fresh_sram_confirmed=true`

### Freshness e Closeout

- Auditoria esperada: `out/logs/freshness_audit_report.json`
- Orquestrador esperado no fechamento: `out/logs/scene_closeout_gate_report.json`
- Sequencia executada: build -> runtime_capture -> BlastEm evidence -> scene_contract_compiler -> res_graph_audit -> validate_resources -> freshness_audit -> scene_closeout_gate
- Estado: freshness `ok`, closeout `ok`

---

## 3. Blockers Atuais

Use esta secao para manter os blockers em linguagem objetiva.

- `visual_lab_aprovado`: ok
- `audio`: ok/not_required
- `hardware_real`: ok via BlastEm reference gate
- `freshness_audit`: ok
- `scene_closeout_gate`: ok
- `ready_for_aaa`: ok

---

## 4. Atualizacao Operacional

Sempre que um eixo mudar de estado:

1. Atualize este documento.
2. Atualize `doc/10-memory-bank.md`.
3. Registre a mudanca em `doc/changelog/changelog.md`.
4. Reexecute o wrapper canonico para refletir o novo estado em `validation_report.json`.
5. Rode `freshness_audit.ps1` para garantir que os artefatos medem a mesma ROM.
6. No fechamento de cena, rode `scene_closeout_gate.ps1` ou registre a justificativa conservadora para nao rodar.
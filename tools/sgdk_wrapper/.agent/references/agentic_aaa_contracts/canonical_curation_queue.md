# Canonical Curation Queue

## Purpose

Recurring failures must become rules, validators, schemas, skills, or lib cases. They must not remain as one-off chat advice.

## Queue Fields

| Field | Meaning |
|---|---|
| `id` | Stable lowercase id |
| `source` | Report, screenshot, code review, emulator session, or human note |
| `symptom` | What failed in concrete terms |
| `technical_diagnosis` | Hardware, art, runtime, audio, or process cause |
| `promotion_target` | rule, validator, schema, skill, workflow, lib_case, or doc |
| `owner_skill` | Existing skill that owns the improvement |
| `status` | queued, implemented, verified, rejected |
| `proof_required` | Self-check, schema validation, ROM, BlastEm, or human approval |

## Current Queue

| id | source | symptom | promotion_target | owner_skill | status |
|---|---|---|---|---|---|
| animation_strip_validator | pasted plan 2026-05 | multi-action sheets accepted as animation | validator | sprite-animation | implemented |
| hardware_report_templates | pasted plan 2026-05 | budget claims lack machine-readable reports | schema/report | megadrive-vdp-budget-analyst | implemented |
| emulator_qa_contract | pasted plan 2026-05 | emulator evidence can drift from ROM | schema/report | sgdk-build-wrapper-operator | implemented |

## Local Proposal Intake

`doc/agent_learning/learning_ledger.json` pode gerar propostas locais automaticamente, mas nao adiciona, altera ou conclui itens desta fila.

Uma proposta local so entra aqui depois de:

1. aprovacao humana explicita;
2. evidencia e freshness suficientes;
3. deduplicacao contra owner existente;
4. teste de generalizacao proporcional ao risco;
5. definicao de patch e regressao.

## Exit Rule

An item leaves this queue only when the target artifact exists, has a minimal example, and has either a self-check or a documented verification path.

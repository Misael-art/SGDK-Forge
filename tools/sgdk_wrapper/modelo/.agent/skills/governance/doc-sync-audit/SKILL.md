---
name: doc-sync-audit
description: Audita deriva entre manifesto, documentacao tecnica, wrappers e estado implementado.
---

# Doc Sync Audit

Use esta skill quando houver duvida sobre coerencia entre estado real e narrativa documental.

## Contrato Operacional

### Entrada minima

- docs canonicos do projeto ou do framework
- manifesto relevante (`.mddev/project.json` ou `framework_manifest.json`)
- sinais de implementacao real (codigo, wrapper, logs ou artefatos)

### Saida minima

- lista curta de conflitos classificados
- recomendacao objetiva de ajuste
- linguagem de status sem ambiguidade
- referencia ao `freshness_audit_report.json` quando existir
- indicacao se o problema e editorial, estrutural ou operacional

### Passa quando

- os conflitos relevantes estao classificados em `coerente`, `parcial`, `desatualizado` ou `contraditorio`
- a recomendacao nao depende de suposicao nao auditada

### Handoff para proxima etapa

- se o conflito for de manifesto/bootstrap: entregar para `operation/sgdk-build-wrapper-operator`
- se o conflito for de hierarquia: entregar para `governance/truth-hierarchy-guard`

## Verifique

- manifesto `.mddev/project.json`
- docs de onboarding e arquitetura
- memory bank e status operacional
- wrappers locais versus wrapper central
- presenca ou ausencia da `.agent`
- `out/logs/freshness_audit_report.json`
- `out/logs/scene_closeout_gate_report.json`
- `validation_report.json` versus `runtime_metrics.json`, `scene_regression_report.json`, `emulator_session.json` e docs

## Drift de Evidencia

- se `validation_report.json` disser um estado e `freshness_audit_report.json` marcar stale, prevalece o stale ate nova validacao
- se docs afirmam `testado_em_emulador` mas `emulator_session.json` ou `scene_regression_report.json` faltam, classifique como `contraditorio`
- se closeout de cena nao foi executado, classifique como `parcial` mesmo que build e screenshot existam

## Classificacao

- `coerente`
- `parcial`
- `desatualizado`
- `contraditorio`

## Resultado esperado

- lista curta de conflitos
- recomendacao objetiva de ajuste
- linguagem de status sem ambiguidade

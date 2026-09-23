# Handoff Checklist - Implementacao Sprint por Sprint

**Data:** 2026-04-21  
**Referencia principal:** `tools/sgdk_wrapper/doc/aaa_agent_feature_implementation_spec.md`  
**Regra maxima:** nao causar regressao no comportamento atual do wrapper

---

## Sprint 0 - Preflight

- ler integralmente `aaa_agent_feature_roadmap.md`
- ler integralmente `aaa_agent_feature_implementation_spec.md`
- confirmar quais scripts atuais nao podem mudar por default
- confirmar que toda feature nova vai nascer atras de flag ou como script isolado
- nao editar `build.bat`, `build_inner.bat`, `run.bat` ou `validate_resources.ps1` neste sprint

**Passa quando**
- existe entendimento claro da ordem de codificacao
- existe entendimento claro da regra de preservacao

---

## Sprint 1 - Fundacao Comum

- criar `schemas/common_artifact.schema.json`
- criar `schemas/scene_id.schema.json`
- criar `lib/sgdk_artifact_contracts.psm1`
- criar `validate_artifact_schema.ps1`
- validar que nenhum fluxo atual foi tocado

**Passa quando**
- os arquivos base existem
- um artefato JSON de teste consegue ser serializado e validado

---

## Sprint 2 - Capturador Canonico BlastEm

- criar `schemas/blastem_session_manifest.schema.json`
- criar `schemas/blastem_evidence.schema.json`
- criar `lib/blastem_evidence.psm1`
- criar `capture_blastem_evidence.ps1`
- testar em um projeto laboratorio sem integrar no `run.bat`

**Passa quando**
- o comando gera `blastem_evidence.json`
- o pacote de evidencia sai em `out/evidence/blastem/`
- a feature ainda e manual e nao altera o runtime atual

---

## Sprint 3 - Linter de Contrato de Cena

- criar `schemas/scene_contract.schema.json`
- criar `schemas/scene_contract_report.schema.json`
- criar `lint_scene_contract.ps1`
- testar com um `doc/scene-contracts.json` minimo em projeto laboratorio

**Passa quando**
- o linter gera `scene_contract_report.json`
- problemas aparecem como `warn` ou `error` apenas no comando novo

---

## Sprint 4 - Runner de Regressao por Cena

- criar `schemas/scene_regression_manifest.schema.json`
- criar `schemas/scene_evidence_bundle.schema.json`
- criar `schemas/scene_regression_report.schema.json`
- criar `lib/evidence_compare.psm1`
- criar `lib/scene_regression.psm1`
- criar `run_scene_regression.ps1`
- pilotar com uma unica cena de bootstrap deterministico

**Passa quando**
- uma cena consegue gerar evidencia e comparacao
- o relatorio final marca `passed`, `failed`, `missing`, `stale` ou `unsupported`

---

## Sprint 5 - Auditor de Budget

- criar `schemas/scene_budget_frame.schema.json`
- criar `schemas/scene_budget.schema.json`
- criar `lib/scene_budget.psm1`
- criar `merge_scene_budget_metrics.ps1`
- criar `audit_scene_budget.ps1`
- consolidar primeiro o que ja existe em `runtime_metrics.json`

**Passa quando**
- o relatorio deixa claro o que foi `measured`, `estimated` e `inferred`
- nao existe telemetria obrigatoria nova no runtime por default

---

## Sprint 6 - Inspector VDP

- criar `schemas/vdp_palette_snapshot.schema.json`
- criar `schemas/vdp_sprite_snapshot.schema.json`
- criar `schemas/vdp_inspection.schema.json`
- criar `lib/vdp_inspection.psm1`
- criar `inspect_vdp_scene_state.ps1`
- criar `render_vdp_inspection_report.py`

**Passa quando**
- `vdp_inspection.json` e gerado
- relatorio HTML inicial e legivel e util

---

## Sprint 7 - Integracoes Opt-In

- integrar captura canonica no `run.bat` somente por flag
- integrar consumo de artefatos novos em `validate_resources.ps1` somente por flag ou warning
- nunca mudar o fluxo default nesta etapa

**Passa quando**
- com flags desligadas, o comportamento atual continua igual
- com flags ligadas, os artefatos novos aparecem sem quebrar o fluxo legado

---

## Checklist de Nao-Regressao

- verificar que `build.bat` continua com o mesmo comportamento default
- verificar que `run.bat` continua com o mesmo comportamento default
- verificar que `validate_resources.ps1` nao ganhou bloqueio novo por default
- verificar que scripts novos escrevem apenas em `out/logs`, `out/evidence` ou `out/reports`
- verificar que toda falha nova registra `failure_reason`
- verificar que todo JSON novo possui `schema_version`

---

## Se Algo Travar

- nao improvisar mudanca em contrato legado
- nao transformar warning experimental em gate
- registrar a dependencia como decisao arquitetural pendente
- parar antes de introduzir regressao

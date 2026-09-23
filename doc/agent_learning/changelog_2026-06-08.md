# Changelog de Curadoria Canonica - 2026-06-08

## Contexto de Producao e Documentacao Proporcional

Escopo: aumentar a capacidade do agente SGDK Forge de entender se a sessao e
jogo AAA, demo tecnica, exercicio, review de jogo ou consultoria antes de
iniciar arte, runtime, QA ou parecer final.

## Canonizado

- Novo contrato `doc/project_context_manifest.json` no template canonico.
- Novo schema `tools/sgdk_wrapper/schemas/project_context_manifest.schema.json`.
- Novo validador `tools/sgdk_wrapper/validate_project_context.ps1`, com report
  em `out/logs/project_context_report.json`.
- Novo workflow `tools/sgdk_wrapper/.agent/workflows/project-context-classification.md`.
- Nova matriz humana `doc/04_project_context_document_matrix.md`.
- Novos documentos de template:
  - `doc/00-project-brief.md`
  - `doc/15-tdd.md`
  - `doc/16-ldd.md`
  - `doc/17-audio-design.md`
  - `doc/18-asset-register.json`
  - `doc/19-roadmap-risk-register.md`
  - `doc/20-release-marketing-legal.md`
  - `doc/21-review-consulting-context.md`

## Regras Assimiladas

- `aaa_game` exige pacote documental proporcional de jogo real.
- `technical_demo` exige prova tecnica, spec, QA, assets e tecnica declarada,
  mas nao exige GDD/TDD completo durante o planejamento.
- `exercise` nao pode declarar `ready_for_aaa`.
- `game_review` e `consulting` nao exigem ROM por padrao; exigem escopo,
  evidencias citadas e limites do parecer.
- `project_context` entra como validacao metodologica base.

## Validacao

- `py tools/sgdk_wrapper/ci/test_schema_contract_gates.py`: `67/67`.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_project_context_governance.ps1`: `10/10`.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/test_project_bootstrap_qaproof.ps1`: `27/27`.
- `python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`: passed.
- `python tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`: ok.
- `powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/ci/run_all_contract_gates.ps1 -Mode smoke`: `combined_status=passed`.

Regra factual: esta curadoria altera o framework e o template, mas nao valida
nenhuma ROM, asset ou projeto especifico. A regra final permanece: se nao foi
visto rodando no emulador, nao existe.

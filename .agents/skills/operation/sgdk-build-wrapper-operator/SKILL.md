---
name: sgdk-build-wrapper-operator
description: Operacao segura do wrapper central SGDK, layouts de projeto e bootstrap da .agent.
---

# SGDK Build Wrapper Operator

Use esta skill ao tocar qualquer arquivo em `tools/sgdk_wrapper/` ou ao diagnosticar build/run/clean/rebuild.

## Principios

- o wrapper central e a fonte unica de logica compartilhada
- wrappers locais dos projetos devem continuar finos
- o manifesto resolve layout e policy
- o bootstrap da `.agent` acontece apenas quando a pasta local nao existe; se `.agent` existir sem `framework_manifest.json`, `ensure_project_agent.ps1` faz **heal** copiando so esse ficheiro da canonica

## Jornada AAA cena (ordem obrigatoria)

1. Pipeline machine-readable: `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
2. Roteamento curto: `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`
3. Loop de producao (narrativa + skills reais): `tools/sgdk_wrapper/.agent/workflows/production-loop.md`

Nao declarar barra AAA nem tile budget "cabe" sem passar por `skills/hardware/megadrive-vdp-budget-analyst` depois da arte definida.

## Checklist

- **Preflight host** (antes do primeiro build da sessao): `powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/preflight_host.ps1` (exit 1 = bloqueante; exit 2 = OK com avisos Python/Magick)
- confirmar `MD_ROOT`, `GDK` e `SGDK_EMULATOR_PATH`
- resolver contexto do projeto via manifesto ou heuristica controlada
- verificar `build_policy`
- preservar compatibilidade com projetos antigos
- evitar sobrescrita de `.agent` local
- apos build com validacao: `validate_resources.ps1 -WorkDir <raiz_projeto>` e passos 7–12 de `workflows/build-validate.md` (ROM, `validation_report.json`, evidencia BlastEm)

## Proibido

- duplicar regras de copia da `.agent` em varios arquivos sem helper comum
- depender de um unico layout de projeto

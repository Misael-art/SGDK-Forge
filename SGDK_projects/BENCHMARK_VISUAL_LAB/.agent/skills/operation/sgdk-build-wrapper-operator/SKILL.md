---
name: sgdk-build-wrapper-operator
description: Operacao segura do wrapper central SGDK, layouts de projeto, bootstrap da .agent e continuidade entre build, changelog e memoria operacional.
---

# SGDK Build Wrapper Operator

Use esta skill ao tocar qualquer arquivo em `tools/sgdk_wrapper/` ou ao diagnosticar build, run, clean ou rebuild.

## Principios

- o wrapper central e a fonte unica de logica compartilhada
- wrappers locais dos projetos devem continuar finos
- o manifesto resolve layout e policy
- a `.agent` local nao pode ser tratada como saudavel se faltar contexto canonico critico
- `doc/changelog` e parte do fluxo operacional, nao pos-processo opcional

## Jornada AAA cena (ordem obrigatoria)

1. `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
2. `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`
3. `tools/sgdk_wrapper/.agent/workflows/production-loop.md`

Nao declarar barra AAA nem tile budget `cabe` sem passar por `skills/hardware/megadrive-vdp-budget-analyst` depois da arte definida.

## Contrato Operacional

### Entrada minima

- raiz do projeto
- manifesto resolvido
- wrapper central disponivel

### Saida minima

- contexto do projeto resolvido
- bootstrap da `.agent` auditado
- build e validacao executados no wrapper central
- `doc/changelog` atualizado quando houver novo asset ou nova ROM

### Passa quando

- o projeto nao esta em contexto degradado silencioso
- a ROM, o changelog e a memoria operacional apontam para o mesmo estado

### Handoff para proxima etapa

- entregar `validation_report.json`, `doc/changelog` e `doc/10-memory-bank.md` coerentes para o fechamento de QA

## Checklist

- executar `tools/sgdk_wrapper/preflight_host.ps1` antes do primeiro build da sessao
- confirmar `MD_ROOT`, `GDK` e `SGDK_EMULATOR_PATH`
- resolver contexto do projeto via manifesto ou heuristica controlada
- verificar `build_policy`
- preservar compatibilidade com projetos antigos
- evitar sobrescrita de `.agent` local
- apos build com validacao, garantir `validation_report.json`, `doc/changelog` e memoria operacional coerentes

## Proibido

- duplicar regras de copia da `.agent` em varios arquivos sem helper comum
- depender de um unico layout de projeto
- tratar changelog, budget e evidencia como assuntos separados

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
- o bootstrap da `.agent` acontece apenas quando a pasta local nao existe

## Checklist

- confirmar `MD_ROOT`, `GDK` e `SGDK_EMULATOR_PATH`
- resolver contexto do projeto via manifesto ou heuristica controlada
- verificar `build_policy`
- preservar compatibilidade com projetos antigos
- evitar sobrescrita de `.agent` local

## Proibido

- duplicar regras de copia da `.agent` em varios arquivos sem helper comum
- depender de um unico layout de projeto

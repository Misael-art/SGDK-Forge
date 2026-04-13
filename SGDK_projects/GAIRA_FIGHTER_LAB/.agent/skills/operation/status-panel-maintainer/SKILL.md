---
name: status-panel-maintainer
description: Mantem o vocabulario e a leitura de status operacional dos projetos SGDK.
---

# Status Panel Maintainer

Use esta skill quando precisar descrever o estado de um projeto sem criar ambiguidade.

## Campos minimos

- `documentado`
- `implementado`
- `buildado`
- `testado_em_emulador`
- `validado_budget`
- `placeholder`
- `parcial`
- `futuro_arquitetural`
- `agent_bootstrapped`

## Regras

- nunca colapsar todos os estados em um unico `ok`
- distinguir ausencia de evidencia de evidencia negativa
- declarar explicitamente quando o build ou teste esta `nao comprovado`

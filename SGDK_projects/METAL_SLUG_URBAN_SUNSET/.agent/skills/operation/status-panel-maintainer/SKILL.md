---
name: status-panel-maintainer
description: Mantem o vocabulario e a leitura de status operacional dos projetos SGDK.
---

# Status Panel Maintainer

Use esta skill quando precisar descrever o estado de um projeto sem criar ambiguidade.

## Contrato Operacional

### Entrada minima

- docs canonicos do contexto
- `out/logs/validation_report.json` quando existir
- artefatos de build, ROM e emulador disponiveis

### Saida minima

- painel com eixos canonicos preenchidos
- diferenca explicita entre evidencia positiva, ausencia de evidencia e evidencia negativa
- bloqueios ativos e gaps de prova rastreaveis

### Passa quando

- nenhum eixo foi colapsado em `ok` generico
- o painel deixa claro o que esta comprovado versus o que apenas existe em documento ou codigo

### Handoff para proxima etapa

- entregar resumo objetivo para `workflows/status.md`, `workflows/handoff.md` ou `validation_report.json`

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

## Gates semanticos

- quando existir viewer/lab, separar `visual_lab_aprovado` de `gameplay_rom_aprovada`
- nunca usar `ready_for_aaa` como sinonimo de "viewer aprovado"
- `ready_for_aaa` so pode subir quando gameplay, performance, audio e hardware_real tiverem evidencia suficiente

## Regras

- nunca colapsar todos os estados em um unico `ok`
- distinguir ausencia de evidencia de evidencia negativa
- declarar explicitamente quando o build ou teste esta `nao comprovado`

---
name: scene-state-architect
description: Protege modularidade, separacao de responsabilidades e fronteiras de estado em projetos SGDK.
---

# Scene State Architect

Use esta skill quando criar ou revisar estados, cenas, modulos ou contratos centrais.

## Foco

- `main.c` minimo
- cabecalho central quando o projeto adotar essa estrategia
- separacao entre core, states, game, render, audio e ui
- expansao de escopo separada da implementacao real

## Perguntas chave

- esta mudanca cria um segundo sistema concorrente?
- a responsabilidade ficou no modulo certo?
- a arquitetura futura esta sendo confundida com feature pronta?

## Proibido

- mover logica compartilhada para lugares ad hoc
- duplicar state machine, scroll manager ou pipeline de render

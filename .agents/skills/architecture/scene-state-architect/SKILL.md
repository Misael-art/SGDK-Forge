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
- ownership unico para callbacks globais e modos especiais de display
## Perguntas chave
- esta mudanca cria um segundo sistema concorrente?
- a responsabilidade ficou no modulo certo?
- a arquitetura futura esta sendo confundida com feature pronta?
- existe mais de um dono implicito para `H-Int`, `WINDOW` ou modo interlaced?
## Proibido
- mover logica compartilhada para lugares ad hoc
- duplicar state machine, scroll manager ou pipeline de render
- criar segundo arbitro de `H-Int`
- tratar `WINDOW` como recurso livre quando o HUD ja tem dono
- ligar `interlaced_448` como default de cena em vez de modo especial com gate explicito

## Competencias estruturais

Esta skill deve proteger explicitamente:

- `h_int_control_plane`
  - um callback global, um owner, um contrato de reset
- `window ownership`
  - `WINDOW` como plano fixo legitimo ou recurso explicitamente livre para tecnica avancada
- `display mode boundaries`
  - `interlaced_448` como `special_scene_only`
- `mutable surface ownership`
  - setor mutavel, `RAM shadow copy` e pool local de tiles com dono claro
- `microbuffer boundaries`
  - regiao de simulacao pequena, cadence explicita e sem concorrencia invisivel com outros sistemas de cena

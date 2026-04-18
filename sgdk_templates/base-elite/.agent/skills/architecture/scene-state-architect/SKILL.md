---
name: scene-state-architect
description: Protege modularidade, separacao de responsabilidades e fronteiras de estado em projetos SGDK.
---

# Scene State Architect

Use esta skill quando criar ou revisar estados, cenas, modulos ou contratos centrais.

## Contrato Operacional

### Entrada minima

- raiz do projeto
- `src/` relevante (ou arquivo alvo)
- docs canonicos disponiveis (`doc/10-memory-bank.md`, `doc/03-arquitetura.md` quando existirem)
- restricoes de hardware pertinentes (H-Int, WINDOW, modos especiais)

### Saida minima

- recomendacao de arquitetura e fronteiras de responsabilidade (com nomes de modulos)
- riscos de concorrencia (ex.: segundo owner de H-Int ou WINDOW)
- handoff objetivo para o proximo gate (budget/runtime/QA)

### Passa quando

- nao existe "segundo sistema concorrente" introduzido por acidente
- ownership de callback global e de WINDOW fica explicitamente declarado
- mudancas futuras ficam marcadas como `futuro_arquitetural`, nao misturadas com feature pronta

### Handoff para proxima etapa

- se houver mudanca de runtime: entregar plano para `code/sgdk-runtime-coder`
- se houver impacto de budget: solicitar veredito em `hardware/megadrive-vdp-budget-analyst`

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

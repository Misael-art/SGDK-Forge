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
- `ui_decision_card` quando a cena tiver HUD/UI/overlay/FX formal
- `scene_transition_card` quando houver troca formal de cena, zona, ato, menu, cutscene ou estado visual

### Saida minima

- recomendacao de arquitetura e fronteiras de responsabilidade (com nomes de modulos)
- riscos de concorrencia (ex.: segundo owner de H-Int ou WINDOW)
- `plane_ownership_map` e `fx_ownership_map` coerentes quando houver UI formal
- `runtime_state_handoff`, `teardown_reset_plan` e donos de FX coerentes quando houver transicao formal
- `font_owner` e ownership de cache temporario de glifos coerentes quando houver anexo tipografico
- handoff objetivo para o proximo gate (budget/runtime/QA)

### Passa quando

- nao existe "segundo sistema concorrente" introduzido por acidente
- ownership de callback global e de WINDOW fica explicitamente declarado
- quando houver UI formal, o `ui_decision_card` nao deixa ownership implicito
- quando houver transicao formal, o `scene_transition_card` nao deixa implicito o dono de camera, scroll, H-Int, CRAM, VSRAM, tiles mutaveis, audio ou estado persistente
- quando houver anexo tipografico, `font_owner`, cache de glifos e teardown tipografico nao ficam implicitos
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
- o `ui_decision_card` declara `plane_ownership_map` e `fx_ownership_map` sem ambiguidade?
- o `scene_transition_card` declara `runtime_state_handoff`, `teardown_reset_plan` e fallback sem esconder carregamento?
- se houver anexo tipografico, `font_owner`, tiles temporarios e `glyph_manifest` estao sob o owner correto?
## Proibido
- mover logica compartilhada para lugares ad hoc
- duplicar state machine, scroll manager ou pipeline de render
- criar segundo arbitro de `H-Int`
- tratar `WINDOW` como recurso livre quando o HUD ja tem dono
- deixar transicao formal mexer em scroll, paleta, tiles, audio ou callback global sem owner unico e reset
- ligar `interlaced_448` como default de cena em vez de modo especial com gate explicito

## Menu Scene Ownership

Menu nao e excecao improvisada. E estado formal da aplicacao.

Exigir:
- owner explicito de `WINDOW`, callbacks de display e paleta especial
- `ui_decision_card` com `profile_kind=front_end_profile` para menu/title/front-end
- contrato de enter, update e exit tao claro quanto o de gameplay
- nenhuma escrita concorrente de texto ou HUD fora do owner da cena
- teardown completo antes de transitar para gameplay ou outra tela

Se o menu usar FX de showcase, eles continuam sujeitos ao mesmo contrato de reset e ownership das cenas jogaveis.

## Competencias estruturais

Esta skill deve proteger explicitamente:

- `h_int_control_plane`
  - um callback global, um owner, um contrato de reset
- `window ownership`
  - `WINDOW` como plano fixo legitimo ou recurso explicitamente livre para tecnica avancada
- `ui_decision_card ownership`
  - `plane_ownership_map` e `fx_ownership_map` sem segundo owner invisivel
- `scene_transition_card ownership`
  - `runtime_state_handoff`, `player_control_policy`, `teardown_reset_plan` e fallback sem segundo owner invisivel
- `font surface ownership`
  - fonte fixa, atlas dedicado, cache temporario e teardown com owner unico
- `display mode boundaries`
  - `interlaced_448` como `special_scene_only`
- `mutable surface ownership`
  - setor mutavel, `RAM shadow copy` e pool local de tiles com dono claro
- `microbuffer boundaries`
  - regiao de simulacao pequena, cadence explicita e sem concorrencia invisivel com outros sistemas de cena

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
- `text_presentation_profile` quando texto, fala, painel, balao, retrato, alerta ou flavor tiver peso dramatico
- `cutscene_scene_contract` quando a cena for abertura, cutscene, contexto, briefing, final, painel narrativo ou retrato falante
- `scene_transition_card` quando houver troca formal de cena, zona, ato, menu, cutscene ou estado visual
- `scene_direction_record`, `parallax_layer_contract`, `palette_cycle_decision_card`, `raster_fx_ownership_map` e `background_ecology_card` quando o cenario for competente, monumental ou usar FX de plano
- `production_runtime_contract` quando o alvo for AAA, stable, release, jogo completo ou projeto piloto
- `tdd_contract.json > technique_selection.application_plan`
- cards de espetaculo runtime quando houver feedback FX, boss/setpiece, tilemap avancado ou audio senior

### Saida minima

- recomendacao de arquitetura e fronteiras de responsabilidade (com nomes de modulos)
- riscos de concorrencia (ex.: segundo owner de H-Int ou WINDOW)
- `plane_ownership_map` e `fx_ownership_map` coerentes quando houver UI formal
- ownership de paineis, baloes, retratos, texto cinetico, cache de texto e SFX de texto quando houver apresentacao expressiva
- ownership da FSM de cutscene, surfaces, glyph cache, paletas, H-Int, audio cues e teardown quando houver `cutscene_scene_contract`
- ownership de parallax, scroll por linha, H-Int, CRAM, tiles mutaveis, background actors e reset quando houver `scene_direction_record`
- ownership de scene manager, input abstraction, save system e region/timing quando houver `production_runtime_contract`
- ownership e teardown de `scene_indexed_promotion`, `cooperative_multitasking`, MegaWiFi ou qualquer tarefa fatiada quando selecionados no TDD
- `runtime_state_handoff`, `teardown_reset_plan` e donos de FX coerentes quando houver transicao formal
- ownership de H-Int, CRAM, VSRAM, sprites, tiles, boss plane takeover, streaming e audio channel coerente quando houver cards de espetaculo runtime
- `font_owner` e ownership de cache temporario de glifos coerentes quando houver anexo tipografico
- handoff objetivo para o proximo gate (budget/runtime/QA)

### Passa quando

- nao existe "segundo sistema concorrente" introduzido por acidente
- ownership de callback global e de WINDOW fica explicitamente declarado
- quando houver UI formal, o `ui_decision_card` nao deixa ownership implicito
- quando houver texto expressivo, `text_presentation_profile` nao deixa owner, timing, audio, cache ou reset implicitos
- quando houver cutscene, `cutscene_scene_contract` nao deixa estado, trigger, resource plan, texto, audio, H-Int, paleta ou teardown implicitos
- quando houver direcao de cenario, `scene_direction_record` nao deixa parallax, CRAM, H-Int, tiles mutaveis, atores de fundo, fallback ou teardown implicitos
- quando houver producao AAA/stable/release, `production_runtime_contract` nao deixa scene manager, input, save, region, mastering, review ou CI como suposicao
- toda tecnica selecionada no TDD possui owner unico, lifecycle, fallback e estado de teardown; tecnica nao selecionada nao aparece por improviso no runtime
- quando houver transicao formal, o `scene_transition_card` nao deixa implicito o dono de camera, scroll, H-Int, CRAM, VSRAM, tiles mutaveis, audio ou estado persistente
- quando houver espetaculo runtime, nenhum card deixa owner, reset ou fallback implicito
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
- se houver `text_presentation_profile`, quem possui paineis, baloes, retratos, texto cinetico, SFX de texto e teardown?
- se houver `cutscene_scene_contract`, qual modulo possui a FSM, qual estado carrega cada painel/retrato, e quem reseta WINDOW, CRAM, H-Int, scroll e audio?
- se houver `scene_direction_record`, quem possui cada tecnica assinada e qual modulo faz reset de H-Int, CRAM, scroll table, actor pool e tiles mutaveis?
- se houver `production_runtime_contract`, qual modulo possui scene stack, input buffer, SRAM, region/timing e closeout?
- o `scene_transition_card` declara `runtime_state_handoff`, `teardown_reset_plan` e fallback sem esconder carregamento?
- os cards de feedback FX, boss, tilemap e audio declaram donos sem sobrepor callbacks, planos, tiles, sprites ou canais?
- se houver anexo tipografico, `font_owner`, tiles temporarios e `glyph_manifest` estao sob o owner correto?
## Proibido
- mover logica compartilhada para lugares ad hoc
- duplicar state machine, scroll manager ou pipeline de render
- criar segundo arbitro de `H-Int`
- tratar `WINDOW` como recurso livre quando o HUD ja tem dono
- deixar texto expressivo criar segundo renderer, segundo cache de glifos ou SFX de texto sem dono
- deixar cutscene nascer como script visual solto, sem FSM, resource plan por estado, owner de surfaces e teardown
- deixar cenario monumental nascer como parallax decorativo solto, sem owner, custo, fallback, funcao de gameplay e teardown
- declarar Mode 7 no Mega Drive; quando a referencia for SNES Mode 7, registrar tecnica real equivalente (`pseudo3d_road_stack`, `line_scroll_floor`, pre-render ou paineis)
- chamar prototipo de AAA/stable/release quando scene manager, input abstraction, save system ou region/timing forem reimplementacoes ad hoc sem contrato
- deixar transicao formal mexer em scroll, paleta, tiles, audio ou callback global sem owner unico e reset
- deixar FX, boss, tilemap streaming ou audio senior nascerem sem card formal, owner e teardown
- ligar `interlaced_448` como default de cena em vez de modo especial com gate explicito
- usar microthread, rede, scene promotion ou tarefa Z80 como concorrencia magica; todo trabalho continua cooperativo, limitado e observavel

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
- `expressive text ownership`
  - paineis, baloes, retratos, hype text, typewriter voice e flavor text com owner, timing, cache, audio e reset declarados
- `cutscene FSM ownership`
  - abertura, contexto, final e cena cinematica como estado formal, com enter/update/advance/exit, resource plan, text timing e teardown
- `scene direction ownership`
  - parallax extremo, palette cycling, H-Int FX, background ecology e foreground mutavel como recursos de cena com owner unico, budget, fallback e reset
- `production runtime ownership`
  - scene manager, input abstraction, save system, region/timing, ROM mastering, code review e CI/local CI como fronteiras reais de entrega, nao backlog invisivel
- `display mode boundaries`
  - `interlaced_448` como `special_scene_only`
- `mutable surface ownership`
  - setor mutavel, `RAM shadow copy` e pool local de tiles com dono claro
- `microbuffer boundaries`
  - regiao de simulacao pequena, cadence explicita e sem concorrencia invisivel com outros sistemas de cena

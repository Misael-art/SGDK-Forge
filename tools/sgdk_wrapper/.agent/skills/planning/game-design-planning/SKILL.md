---
name: game-design-planning
description: Use quando um projeto SGDK estiver nascendo, quando o GDD/spec ainda nao derem conta do escopo atual, ou quando for preciso transformar nome + genero + fantasia + referencias + restricoes em briefing, seeds documentais e first playable slice antes de abrir arte ou runtime. Nao use quando a tarefa ja tem GDD/spec aprovados e o trabalho restante e apenas arte, budget, runtime ou validacao.
---

# Game Design Planning

Use esta skill para preencher o espaco entre intencao e producao.

Antes de usa-la, classifique o contexto via `workflows/project-opening.md`.

Regra:

- se for `projeto_existente`, esta skill nao deve reabrir briefing do zero sem pedido explicito
- se for `reseed` ou `projeto_novo`, esta skill vira a primeira superficie canonica antes de arte ou runtime

- `project_brief`
- `core_loop_statement`
- `feature_scope_map`
- `scene_roadmap`
- `first_playable_slice`
- `front_end_profile`
- `scene_transition_card` seed quando houver troca de cena, zona, ato ou estado visual com peso dramatico/tecnico
- `gdd_seed`
- `scene_spec_seed`
- `roteiro_scope`

Esta skill **nao auto-aprova o GDD**. Ela semeia e estrutura o projeto para a etapa humana de escopo.

---

## Entrada minima

- nome do projeto
- genero ou subgenero
- fantasia, tema ou fantasia-alvo
- referencias primarias
- plataforma alvo: Mega Drive / SGDK 2.11
- escopo desejado ou slice pretendido

Se ja existirem documentos canonicos, ler primeiro:

- `doc/11-gdd.md`
- `doc/13-spec-cenas.md`
- `doc/12-roteiro.md` quando houver narrativa
- `doc/10-memory-bank.md` quando houver historico real

Se o projeto ja existir e esses documentos sustentarem o escopo atual, prefira continuar a iteracao em vez de reseedar o planejamento.

---

## Saida minima

- `project_brief`
- `core_loop_statement`
- `feature_scope_map`
- `scene_roadmap`
- `first_playable_slice`
- `front_end_profile`
- `scene_transition_card` seed quando houver transicao formal prevista
- `gdd_seed`
- `scene_spec_seed`
- `roteiro_scope`

### Mapeamento recomendado para docs

- `project_brief`, `core_loop_statement`, `feature_scope_map` e `front_end_profile` -> `doc/11-gdd.md`
- `scene_roadmap`, `first_playable_slice`, `scene_transition_card` seed e `scene_spec_seed` -> `doc/13-spec-cenas.md`
- `roteiro_scope` -> `doc/12-roteiro.md`

Regra:

- `front_end_profile` aqui e um **seed de planejamento**
- quando a iteracao tocar HUD/UI formal, ele deve ser formalizado depois via `ui_decision_card`
- em menu, title screen ou front-end, esse card usa `profile_kind=front_end_profile`
- `scene_transition_card` aqui nasce como seed; antes de arte/runtime, ele precisa virar contrato completo conforme `doc/03_art/14_contextual_scene_transition_system.md`

---

## Passa quando

- ha escopo fechado sem feature creep
- existe um `first_playable_slice` implementavel
- a ordem de cenas e o papel de cada uma estao claros o suficiente para handoff
- transicoes formais entre cenas, zonas, atos, menus ou cutscenes tem causa, controle do jogador e fallback declarados quando aplicavel
- menu, title screen e front-end ja tem papel declarado quando aplicavel
- arte, runtime e budget conseguem trabalhar sem adivinhacao de objetivo

---

## Handoff para proxima etapa

- `art/art-asset-diagnostic`
  - quando a producao for seguir por descoberta de assets
- `art/multi-plane-composition`
  - quando a cena inicial ja estiver escolhida e precisar de desenho de planos
- `operation/sgdk-build-wrapper-operator`
  - quando o projeto estiver sendo bootstrapado ou reestruturado no wrapper

---

## Processo canonico

### 1. Congelar a promessa do projeto

Definir:

- o que o jogo e
- o que o jogo nao e
- qual fantasia ele promete no primeiro contato
- qual experencia precisa existir no primeiro slice jogavel

### 2. Fechar o loop central

Emitir um `core_loop_statement` simples:

`acao principal -> feedback -> risco -> recompensa -> repeticao`

Se o loop nao couber em uma frase curta, o projeto ainda esta difuso.

### 3. Cortar escopo cedo

Emitir `feature_scope_map` com tres classes:

- `entra_no_slice`
- `entra_depois`
- `fora_de_escopo`

Nao promova backlog futuro como se fosse parte do escopo atual.

### 4. Planejar front-end desde o inicio

Se houver menu, title screen ou front-end:

- declarar `front_end_profile`
- dizer qual fantasia ele comunica
- dizer qual movimento/vida existe em idle
- dizer qual feedback de selecao existe
- dizer o que seria fora de tom

Menu e title nao sao apendice tardio.

### 5. Fechar o first playable slice

O slice inicial deve responder:

- qual cena o jogador ve primeiro
- qual acao principal ele executa
- qual feedback prova que o jogo funciona
- quais sistemas ficam de fora nesta primeira entrega

### 6. Abrir o roadmap de cenas

Emitir `scene_roadmap` com:

- ordem de aparicao
- papel da cena
- objetivo no slice
- dependencia principal
- transicao de entrada/saida quando ela carregar geografia, ritmo, causa narrativa ou tecnica especial

Se a cena inicial ainda nao estiver clara, nao abrir runtime.

### 7. Delimitar narrativa

Quando houver historia, `roteiro_scope` deve dizer:

- quais cenas/telas precisam de texto neste slice
- qual tom geral
- o que fica fora por enquanto

Nao abrir dialogo aprovado sem saber em que slice ele cabe.

---

## Anti-padroes

- pular de pitch para runtime
- tratar GDD como texto bonito sem corte de escopo
- colocar menu/title fora do planejamento inicial
- confundir wishlist com `feature_scope_map`
- escrever `scene_spec_seed` sem `first_playable_slice`
- abrir arte sem cena inicial escolhida

---

## Saida esperada

Quando responder usando esta skill, entregar algo suficientemente concreto para popular os docs canonicos com:

- `project_brief`
- `core_loop_statement`
- `feature_scope_map`
- `scene_roadmap`
- `first_playable_slice`
- `front_end_profile`
- `scene_transition_card` seed quando houver transicao formal
- `roteiro_scope`

Se faltar algum desses blocos, o planejamento ainda esta parcial.

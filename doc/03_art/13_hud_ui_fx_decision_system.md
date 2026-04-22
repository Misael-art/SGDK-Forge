# HUD/UI FX Decision System

## Objetivo

Definir um sistema de decisao tecnica para HUD, interface, overlay, subscreen e FX de interface no MegaDrive_DEV.

Este documento nao define uma estetica unica.
Ele define como escolher, de forma inteligente e honesta com o hardware, a arquitetura mais forte para cada surface formal de UI.

S3.2 passa a ser a trilha canonica desta doutrina.

## Regra Principal

Nao escolher UI pelo "look" isolado.

Escolher pela combinacao entre:

- tema
- mecanica
- carga cognitiva
- budget
- papel narrativo
- oportunidade real de espetaculo tecnico

## O que e uma surface formal de UI

Emitir `ui_decision_card` quando a cena tiver qualquer uma destas superficies:

- HUD persistente de gameplay
- overlay critico de estado
- subscreen de inventario, mapa ou status
- cockpit, visor ou sensor
- menu, title screen ou front-end
- FX de interface que disputem `WINDOW`, `H-Int`, `CRAM` ou legibilidade critica

Regra de compatibilidade:

- `front_end_profile` pode existir como seed de planejamento em GDD/spec
- quando a UI vira contrato formal, ele nao concorre com `ui_decision_card`
- menu, title screen e front-end devem ser formalizados como `ui_decision_card` com `profile_kind=front_end_profile`

## Formula de Decisao

Toda decisao de HUD/UI deve responder, nesta ordem:

1. Qual e a funcao dramatica da interface?
2. Qual e a funcao mecanica da interface?
3. Qual e a carga de leitura exigida por segundo?
4. A informacao precisa ficar fixa, contextual ou incorporada ao mundo?
5. Qual plano do VDP e mais adequado?
6. Existe oportunidade real de FX sem sacrificar clareza?
7. O budget permite a solucao elite?
8. Se nao permitir, qual e o fallback honesto?

## Classes canonicas de solucao

### A. `window_plane_static_hud`

Melhor para:

- HUD fixa
- score
- barras
- cronometros
- indicadores permanentes

Escolher quando:

- a prioridade e legibilidade
- a tela tem scroll constante
- sprites precisam ser preservados para gameplay

Risco:

- ocluir parte de `BG_A`
- virar muleta para UI excessiva

Politica:

- default seguro quando a leitura precisa ser constante
- nao confundir com `window alias`

### B. `sprite_hud`

Melhor para:

- elementos altamente animados
- cursores, marcadores, ponteiros vivos
- overlays pequenos e reativos

Escolher quando:

- a expressividade visual compensa o custo de sprite
- a pressao de scanline continua sob controle

Risco:

- competir com gameplay
- degradar o pior quadro

### C. `subscreen_inventory`

Melhor para:

- loadout
- inventario
- mapa
- status secundario
- economia

Escolher quando:

- a informacao nao precisa permanecer o tempo todo na tela principal
- a surface pode assumir outro ritmo de leitura

### D. `diegetic_avatar_state`

Melhor para:

- vida corporal
- dano visivel
- energia embutida no avatar ou equipamento

Escolher quando:

- a leitura corporal substitui barras tradicionais sem ambiguidade
- a diegese melhora a tensao em vez de atrasar leitura

### E. `sensor_resource_ui`

Melhor para:

- radar
- scanner
- bateria
- detector de ameacas
- visores de risco

Escolher quando:

- a interface e uma mecanica limitada por recurso
- a propria leitura parcial faz parte da pressao de jogo

### F. `meta_frame_ui`

Melhor para:

- jogos com moldura narrativa forte
- teatro
- quadrinho
- simulador
- terminal
- painel de cabine
- title/menu/front-end com moldura dramatica

Escolher quando:

- a moldura da tela e parte do universo
- a fantasia do jogo pede composicao de showcase

### G. `raster_enhanced_ui`

Melhor para:

- split de paleta
- spotlight
- waterline
- wobble
- highlight/shadow localizado
- feedback de alta intensidade

Escolher quando:

- o ganho perceptivo e real
- a leitura continua clara
- ha owner explicito de callback e reset

Risco:

- disputar `H-Int`, `CRAM`, `WINDOW` e budget do pior quadro ao mesmo tempo

Politica:

- nunca e default
- sempre precisa de fallback honesto

## Mapeamento de hardware

### `BG_B`

Usar para:

- atmosfera distante
- fundo de baixa competicao
- profundidade

### `BG_A`

Usar para:

- primeiro plano jogavel
- arquitetura
- obstaculos
- leitura principal de cenario

### `WINDOW`

Usar para:

- HUD fixa
- texto critico
- overlays ancorados
- interfaces que nao podem sofrer scroll

### Sprites

Usar para:

- avatar
- inimigos
- projeteis
- feedbacks dinamicos curtos
- cursores ou elementos de selecao quando realmente compensar

## Regras de escolha

- se a leitura precisa ser constante, preferir `window_plane_static_hud`
- se a interface deve fazer parte da tensao, considerar `sensor_resource_ui`
- se a interface pode ser lida no corpo do avatar, considerar `diegetic_avatar_state`
- se a identidade do jogo depende da moldura, considerar `meta_frame_ui`
- se o efeito especial comprometer leitura, recusar
- se o FX so for "bonito", recusar
- se a mesma informacao puder ser comunicada com menos custo, usar a solucao mais barata

## Politica hibrida de tipografia AAA

Default do agente:

- a politica base para tipografia forte e `hibrido`
- `hud_critical` tende a `fixed_custom_hud_font`
- `narrative_text` tende a `variable_width_tidytext`
- `front_end_premium` tende a `display_font_plus_body_font`

Regras:

- decidir tipografia por `surface_role`, nao por "fonte bonita"
- emitir `glyph_manifest` a partir de strings reais da HUD, menu, inventario, roteiro ou creditos antes de aprovar charset expandido
- `charset_profile` sobe em camadas: `ascii_core`, `ptbr_core_accents`, `extended_optional`
- se houver PT-BR visivel ao jogador, tratar cedilha, agudos, tis, circunflexos e minusculas realmente usadas no script como requisito de primeira classe
- texto critico fixo deve preferir `WINDOW` com fonte custom fixa e barata
- render proporcional nao entra em HUD de combate por frame
- `variable_width_tidytext` fica para dialogo, creditos, lore, terminais, subtelas e front-end controlado
- a escada de fallback tipografico e obrigatoria:
  - `premium`: proporcional + acentos + composicao refinada
  - `strong`: fixa custom + subset acentuado + header nobre
  - `honest`: fonte utilitaria simples para debug ou recuo de budget

## FX de interface permitidos com criterio

- palette cycling
- pulso de selecao
- brilho corrido
- scanline wobble localizado
- split de paleta
- spotlight com highlight/shadow
- deformacao controlada de horizonte
- marker animation
- animacao de cursor

Todos precisam de:

- owner declarado
- reset simetrico
- ganho perceptivo real
- budget validado

## Bloqueios

Nao aprovar:

- texto critico em plano rolavel sem justificativa forte
- uso de `sprite_hud` que cause desaparecimento de gameplay
- interface que exija leitura lenta em combate rapido
- FX que vazem entre cenas
- split de paleta sem teardown
- "HUD cinematica" que esconda o estado do jogador
- diegese que confunda o usuario

## Artefato canonico: `ui_decision_card`

Todo HUD/UI formal deve produzir um `ui_decision_card`.

Cabecalho minimo:

- `scene_or_surface_id`
- `surface_kind`
- `profile_kind`

Campos obrigatorios:

- `ui_role`
- `diegese_level`
- `hud_density`
- `ui_psychology_goal`
- `attention_profile`
- `plane_ownership_map`
- `ui_architecture_choice`
- `budget_decision`
- `fallback_plan`

Campo condicional:

- `fx_ownership_map`
  - obrigatorio quando houver FX de interface

Anexo tipografico condicional:

- obrigatorio quando a tipografia tiver peso dramatico, de leitura ou de identidade de front-end
- campos:
  - `typography_role`
  - `font_render_mode`
  - `charset_profile`
  - `glyph_budget_class`
  - `font_owner`
  - `fallback_font_plan`
- supporting artifact:
  - `glyph_manifest`
    - obrigatorio quando houver anexo tipografico
    - deve nascer de strings reais e ser anexado ou referenciado pelo GDD/spec

Convencoes:

- `profile_kind=ui_decision_card`
  - default para HUD, overlay, subscreen, visor e UI de gameplay
- `profile_kind=front_end_profile`
  - obrigatorio para menu, title screen e front-end
- `budget_decision`
  - deve usar `cabe`, `cabe com recuo` ou `nao cabe`
- `fallback_plan`
  - descreve a rota honesta se a solucao elite nao couber
- `typography_role`
  - valores canonicos: `hud_critical`, `narrative_text`, `front_end_premium`
- `font_render_mode`
  - valores canonicos: `fixed_custom_hud_font`, `variable_width_tidytext`, `display_font_plus_body_font`
- `charset_profile`
  - default em camadas: `ascii_core`, `ptbr_core_accents`, `extended_optional`
- `glyph_budget_class`
  - usar `lean`, `moderate` ou `premium`

Template minimo:

```yaml
scene_or_surface_id: scene_menu_main
surface_kind: title_menu
profile_kind: front_end_profile

ui_role: "moldura dramatica de navegacao"
diegese_level: "meta_frame"
hud_density: "baixa"
ui_psychology_goal: "controle, fantasia e expectativa"
attention_profile: "ancorada com picos curtos"
plane_ownership_map:
  BG_B: "atmosfera e profundidade"
  BG_A: "estrutura da moldura e massa principal"
  WINDOW: "texto critico e labels fixas"
  SPRITES: "cursor e feedback curto"
ui_architecture_choice: "meta_frame_ui"
fx_ownership_map:
  H-Int: "scene_menu_main"
  palette: "scene_menu_main"
  window: "scene_menu_main"
budget_decision: "cabe"
fallback_plan: "desligar wobble e manter cursor animado + palette cycling leve"
glyph_manifest_ref: "doc/13-spec-cenas.md#scene_menu_main_glyph_manifest"
typography_role: "front_end_premium"
font_render_mode: "display_font_plus_body_font"
charset_profile: "ptbr_core_accents"
glyph_budget_class: "moderate"
font_owner: "scene_menu_main"
fallback_font_plan: "manter display_font so no logo e reduzir body_font para fixed_custom_hud_font"
```

## Handoff entre skills

- `visual-excellence-standards`
  - decide linguagem visual, legibilidade, `attention_profile` e `hud_density`
- `scene-state-architect`
  - decide ownership, teardown e fronteiras de responsabilidade
- `megadrive-vdp-budget-analyst`
  - valida `ui_architecture_choice`, `budget_decision` e o custo real do pior quadro
- `sgdk-runtime-coder`
  - implementa a surface escolhida seguindo ownership, fallback e reset
- `art-translation-to-vdp`
  - traduz assets quando a interface exigir arte dedicada
  - entra tambem quando a fonte precisar alma visual propria e atlas dedicado

## Referencias de pattern, nao defaults

- `window_plane_static_hud`
  - continua sendo o default seguro para leitura constante
- `window_plane_lifebar`
  - e referencia forte de pattern, nao regra universal
- `sonic_hud_physics_family`
  - e referencia de feel e animacao, nao default automatico
- `procedural_raster_glitch_suite`
  - continua opcao de alto risco e so pode entrar com owner explicito, reset simetrico e ganho perceptivo real

## Matriz minima de sanity check

- platformer com leitura constante e scroll forte deve tender a `window_plane_static_hud`
- timer, score, life, ammo e warning curto devem tender a `fixed_custom_hud_font`
- inventario, mapa ou status secundario deve tender a `subscreen_inventory`
- dialogo, credito ou texto corrido em PT-BR deve tender a `variable_width_tidytext` com `glyph_manifest` fechado
- vida corporal legivel no avatar pode tender a `diegetic_avatar_state`
- radar, bateria ou scanner limitado por recurso deve tender a `sensor_resource_ui`
- menu/title com moldura dramatica deve tender a `meta_frame_ui` com `profile_kind=front_end_profile`
- tentativa de `raster_enhanced_ui` sem owner, reset e ganho perceptivo deve ser recusada ou rebaixada para fallback

## Regra final

A melhor interface nao e a mais chamativa.

E a que entrega:

- mais impacto
- mais clareza
- mais coerencia
- mais hardware mastery

com o menor grau de mentira sobre o que o Mega Drive realmente consegue sustentar.

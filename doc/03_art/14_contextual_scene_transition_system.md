# Contextual Scene Transition System

## Objetivo

Definir uma doutrina integrada para transicoes de tela, cena, zona, ato, menu, cutscene e estado visual no MegaDrive_DEV.

Este documento nao cria uma skill nova.
Ele ensina as skills existentes a escolher transicoes por funcao dramatica, continuidade espacial, ritmo de gameplay, budget e oportunidade real de hardware.

S3.4 passa a ser a trilha canonica desta doutrina.

## Regra principal

Transicao nao e tela de carregamento disfarçada.

Transicao e parte da narrativa, da geografia, do ritmo e da percepcao de mundo do jogador.

Nao escolher transicao pelo "efeito bonito" isolado.

Escolher pela combinacao entre:

- causa narrativa
- continuidade espacial
- ritmo de controle
- estado do jogador
- custo de VDP / DMA / H-Int / CRAM
- audio e silencio
- oportunidade real de espetaculo tecnico
- fallback honesto

## Quando emitir `scene_transition_card`

Emitir `scene_transition_card` quando houver qualquer uma destas fronteiras:

- troca de cena jogavel
- troca de zona, ato ou bioma
- entrada ou saida de sala, caverna, porta, elevador, veiculo ou portal
- menu, title, front-end ou cutscene entrando ou saindo de gameplay
- mudanca de estado visual com peso dramatico
- transicao que use H-Int, CRAM, VSRAM, tile mutation, pseudo-3D, palette split ou audio fade

Regra de compatibilidade:

- `scene_transition_card` e separado de `ui_decision_card`
- se a transicao tocar HUD, menu, title, overlay ou texto critico, o card deve referenciar o `ui_decision_card`
- a transicao nunca pode assumir ownership implicito de `WINDOW`, `H-Int`, paleta ou tiles mutaveis

## Formula de decisao

Toda transicao formal deve responder, nesta ordem:

1. Qual e a causa dramatica da transicao?
2. Qual e a causa mecanica da transicao?
3. A geografia pode ser preservada ou a ruptura e intencional?
4. O jogador mantem, perde ou troca controle?
5. A camera precisa guiar, esconder, revelar ou impactar?
6. Qual plano do VDP e qual sistema de FX e mais adequado?
7. O audio deve manter, cortar, cruzar, cair ou explodir em sting?
8. O budget permite a rota elite no pior quadro?
9. Se nao permitir, qual fallback ainda comunica a mesma ideia?

## Classes canonicas de solucao

### A. `palette_fade_bridge`

Melhor para:

- transicoes simples
- cuts de baixo risco
- entrada ou saida de menu
- fallback honesto
- fade de audio/paleta sincronizado

Escolher quando:

- a continuidade espacial nao e essencial
- o budget nao permite transicao elite
- a clareza vale mais que espetaculo

Politica:

- e fallback seguro
- nao deve virar fade preto generico sem causa dramatica

### B. `spatial_scroll_bridge`

Melhor para:

- zonas conectadas
- passagem fisica entre areas
- camera que conduz o jogador de um lugar ao outro
- streaming ou scroll que escondem a troca de assets

Escolher quando:

- a nova area pode ser percebida como parte do mesmo mundo
- preservar ritmo e imersao e mais importante que cortar rapido

Risco:

- seam de tilemap
- camera sem contrato
- streaming cego sem budget

### C. `scripted_avatar_bridge`

Melhor para:

- queda
- correnteza
- porta
- elevador
- veiculo
- explosao
- personagem sendo arremessado ou guiado pelo mundo

Escolher quando:

- o corpo do avatar pode explicar a transicao
- a perda ou restricao de controle tem payoff visivel

Risco:

- cutscene travando jogo sem ganho
- input perdido sem justificativa

### D. `tile_mask_mosaic_transition`

Melhor para:

- wipe
- tile fade
- mosaic
- mascara por dados de tile
- transicao grafica estilizada

Escolher quando:

- a estetica da cena pede materialidade de tile
- o efeito comunica magia, memoria, terminal, desenho, sonho ou glitch controlado

Exige:

- backup do tileset original
- restauro simetrico
- budget de `VDP_loadTileSet`, `VDP_fillTileMapRect` ou upload equivalente

### E. `raster_distortion_bridge`

Melhor para:

- wobble
- line scroll
- scaling por H-Int
- waterline
- distorcao surreal
- tremor, calor, sonho, agua ou impacto cosmico

Escolher quando:

- a distorcao explica o mundo ou o estado do personagem
- ha owner unico de H-Int

Exige:

- `fx_ownership_map`
- reset simetrico
- fallback sem H-Int

### F. `lighting_state_transition`

Melhor para:

- silhueta
- backlight
- Shadow/Highlight
- palette split
- mudanca dramatica de luz
- passagem de normal para modo sombra/luz

Escolher quando:

- a luz muda o contexto emocional ou mecanico da cena
- a leitura do avatar e do objetivo continua clara

Exige:

- auditoria de paleta
- legibilidade de silhueta
- reset de CRAM / highlight / shadow

### G. `pseudo3d_perspective_bridge`

Melhor para:

- tunnel
- corrida para dentro da tela
- queda em profundidade
- fuga em perspectiva
- road-stack ou camera pseudo-3D

Escolher quando:

- a transicao e uma cena-espetaculo e nao um corte comum
- o ganho perceptivo justifica custo alto

Politica:

- sempre `advanced_tradeoff`
- nunca default
- exige fallback seguro

### H. `meta_cut_bridge`

Melhor para:

- teatro
- filme
- terminal
- painel de cabine
- quadrinho
- vinheta
- corte assumidamente narrativo

Escolher quando:

- a moldura da ficcao justifica a ruptura
- a transicao reforca o tema em vez de esconder carregamento

## Artefato canonico: `scene_transition_card`

Toda transicao formal deve produzir um `scene_transition_card`.

Campos obrigatorios:

- `transition_id`
- `from_scene`
- `to_scene`
- `transition_role`
- `transition_trigger`
- `continuity_model`
- `player_control_policy`
- `camera_motion_contract`
- `plane_ownership_map`
- `audio_transition_plan`
- `runtime_state_handoff`
- `budget_decision`
- `fallback_plan`
- `teardown_reset_plan`
- `evidence_plan`

Campo condicional:

- `fx_ownership_map`
  - obrigatorio quando houver H-Int, CRAM, VSRAM, tile mutation, pseudo-3D, palette split, Shadow/Highlight ou FX de interface
- `ui_decision_card_ref`
  - obrigatorio quando a transicao tocar HUD, menu, title, overlay, texto critico ou front-end

Convencoes:

- `continuity_model`
  - usar uma das classes canonicas deste documento
- `player_control_policy`
  - valores canonicos: `preserve`, `constrain`, `pause`, `cutscene`
- `budget_decision`
  - deve usar `cabe`, `cabe com recuo` ou `nao cabe`
- `fallback_plan`
  - deve preservar a intencao dramatica com custo menor
- `teardown_reset_plan`
  - deve citar paleta, scroll, H-Int, tiles, sprites e `WINDOW` quando aplicavel

Template minimo:

```yaml
transition_id: zone_01_to_zone_02
from_scene: scene_zone_01
to_scene: scene_zone_02
transition_role: "conectar geografia, ritmo e causa narrativa"
transition_trigger: "boss derrotado abre correnteza para a proxima area"
continuity_model: "scripted_avatar_bridge"
player_control_policy: "constrain"
camera_motion_contract: "camera segue avatar ate a correnteza e oculta snap de mapa"
plane_ownership_map:
  BG_B: "continuidade atmosferica"
  BG_A: "geometria da passagem"
  WINDOW: "sem uso durante a transicao"
  SPRITES: "avatar, espuma e feedback curto"
fx_ownership_map:
  H-Int: "scene_zone_01_to_zone_02"
  CRAM: "scene_zone_01_to_zone_02"
audio_transition_plan: "manter musica, aplicar sting curto e filtrar SFX de agua"
runtime_state_handoff: "posicao, vida, inventario e flags de boss atravessam; mapa novo carrega no snap oculto"
budget_decision: "cabe com recuo"
fallback_plan: "palette_fade_bridge com sting de agua se H-Int nao couber"
teardown_reset_plan: "resetar H-Int, scroll line, CRAM, sprites temporarios e WINDOW"
evidence_plan: "BlastEm com screenshot dedicada + save.sram quando virar runtime"
```

## Regras de aprovacao

- se a nova area pode ser conectada pelo mundo, preferir `spatial_scroll_bridge` ou `scripted_avatar_bridge` antes de fade preto
- se a transicao so e bonita e nao comunica causa, geografia, tom ou risco, recusar
- se usar H-Int, palette split, wobble, pseudo-3D ou tile mutation, exigir owner unico, budget, reset simetrico e fallback
- se pausar controle do jogador, declarar motivo dramatico e duracao
- pausa sem payoff e bloqueio
- se a transicao esconder carregamento, declarar isso no `runtime_state_handoff`
- se a transicao tocar HUD, menu ou title, consumir tambem `ui_decision_card`
- se a rota elite nao couber, o fallback default e `palette_fade_bridge` contextualizado, nao fade preto generico

## Bloqueios

Nao aprovar:

- hard cut quando a geografia pede continuidade e o budget permite ponte
- fade preto generico como primeira resposta AAA
- transicao que retira controle sem payoff claro
- H-Int sem owner unico
- tile mutation sem backup/restauro
- palette split sem teardown
- pseudo-3D vendido como barato
- audio cortado sem plano de continuidade
- transicao que esconde estado critico do jogador

## Handoff entre skills

- `game-design-planning`
  - declara papel da transicao no roadmap de cenas e no first playable slice
- `multi-plane-composition`
  - decide continuidade espacial, camera, planos e seam visual
- `visual-excellence-standards`
  - julga impacto, clareza, silhueta, luz, ritmo visual e coerencia de mundo
- `scene-state-architect`
  - decide ownership, estado que atravessa a fronteira e teardown
- `megadrive-vdp-budget-analyst`
  - valida custo real de VDP, DMA, H-Int, CRAM, sprites, tile mutation e audio
- `sgdk-runtime-coder`
  - implementa runtime, reset, fallback, audio transition e evidencia

## Referencias de pattern, nao defaults

- `fade_transition`
  - fallback seguro e bridge simples, nao default AAA universal
- `tile_mask_transition_fade`
  - referencia para `tile_mask_mosaic_transition`; exige backup/restauro e budget de DMA
- `lizardrive_hint_fx_family`
  - base para `raster_distortion_bridge`; sempre com H-Int owner
- `hint_palette_blending`
  - base para `lighting_state_transition`; sempre com reset de CRAM
- `pseudo3d_road_stack`
  - referencia para `pseudo3d_perspective_bridge`; sempre `advanced_tradeoff`
- fades de audio XGM2
  - parte do `audio_transition_plan`, nao substituto da decisao visual

## Matriz minima de sanity check

- platformer com zona conectada deve tender a `spatial_scroll_bridge` ou `scripted_avatar_bridge`
- transicao surreal deve aceitar `raster_distortion_bridge` somente com `fx_ownership_map` e reset
- cena de luz/silhueta deve aceitar `lighting_state_transition` somente com auditoria de paleta e legibilidade
- tile fade ou mosaic deve falhar sem backup/restauro de tileset
- tunnel ou queda em profundidade deve sair como `pseudo3d_perspective_bridge` com fallback seguro
- qualquer H-Int sem owner unico ou teardown deve ser recusado

## Regra final

A melhor transicao nao e a mais chamativa.

E a que faz o jogador sentir que o mundo continuou existindo entre uma tela e outra, com:

- causa clara
- ritmo preservado
- estado rastreavel
- hardware mastery real
- fallback honesto

sem mentir sobre o que o Mega Drive consegue sustentar.

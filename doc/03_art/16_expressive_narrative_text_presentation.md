# Expressive Narrative Text Presentation

Status: `canonico / doutrina operacional`
Trilha: `S3.5 Expressive Narrative Text Presentation`

## Objetivo

Definir como o agente escolhe apresentacao de texto com peso dramatico no Mega Drive.

Esta doutrina nao substitui `ui_decision_card`, `glyph_manifest` ou a politica hibrida de tipografia.
Ela entra como anexo `text_presentation_profile` dentro do mesmo `ui_decision_card`.

## Regra central

Texto expressivo nao e caixa bonita.

Ele so entra quando melhora pelo menos um destes pontos:

- ritmo dramatico
- identidade de personagem
- leitura de mundo
- impacto de alerta
- imersao de fala
- recompensa de exploracao

Se o texto so parecer estiloso, recusar ou reduzir para tipografia simples.

## Perguntas de decisao

Responder nesta ordem:

1. O texto e leitura critica, fala, narrativa, alerta ou flavor?
2. O jogador precisa ler parado, em controle restrito ou durante acao?
3. A apresentacao deve ser fixa, diegetica, cinetica ou em painel?
4. O texto precisa de fonte fixa, proporcional ou display?
5. Ha retrato, balao, painel, hype text ou voz de texto?
6. Qual plano/sistema e dono de texto, tiles, sprites, paleta e audio?
7. O ganho dramatico justifica VRAM, DMA, sprites, CRAM e SFX?
8. Qual fallback preserva leitura se a rota premium nao couber?

## Classes canonicas

### `panel_sequence_text`

Usar para:

- cenas tipo manga/quadrinho
- cutscenes curtas com quadros revelados em ritmo controlado
- reacoes fortes de personagem sem animacao completa

Exige:

- ordem de paineis
- budget de tiles por painel
- regra de entrada/saida
- fallback para painel unico ou texto comum

### `diegetic_speech_balloon`

Usar para:

- fala curta ancorada a personagem
- meta-frame de quadrinho
- dialogo durante acao leve

Exige:

- speaker anchor
- lifetime curto
- regra para nao cobrir hitbox, HUD ou rota
- fallback para caixa fixa

### `animated_portrait_dialog`

Usar para:

- dialogo longo com empatia
- RPG, estrategia, briefing, cena narrativa
- personagem que precisa parecer vivo

Exige:

- retrato com blink ou mouth frames
- ritmo de fala
- estado emocional simples
- fallback para retrato estatico

### `kinetic_hype_text`

Usar para:

- warning, boss intro, titulo de fase, chamada de impacto
- texto que age como FX de cena

Exige:

- duracao curta
- leitura em 1 segundo
- owner de sprites, tiles, CRAM ou H-Int
- fallback para warning fixo

### `typewriter_voice_text`

Usar para:

- dialogo com reveal por caractere, silaba ou palavra
- texto que precisa de "voz" sem dublagem
- terminais, RPG, investigacao ou narrador

Exige:

- cadence de reveal
- SFX de texto com prioridade baixa
- variacao por personagem quando houver
- silencio dramatico quando o texto pedir pausa

### `flavor_text_interaction`

Usar para:

- estantes, placas, objetos, terminais, lore curta
- mundo que responde com texto especifico

Exige:

- strings reais no `glyph_manifest`
- politica anti-repeticao
- limite de leitura por interacao
- fallback para descricao curta

## Anexo canonico: `text_presentation_profile`

O anexo e obrigatorio quando texto, fala ou alerta tiver peso dramatico, cinetico ou diegetico.

```yaml
text_presentation_profile:
  text_surface_id: scene_intro_panel_01
  text_surface_class: panel_sequence_text
  presentation_role: "ritmo dramatico e reacao de personagem"
  reading_context: "pause | constrained_control | live_action | menu"
  narrative_timing_model: "instant | typewriter | panel_step | timed_burst | player_advance"
  layout_anchor: "WINDOW | BG_A | BG_B | SPRITES | hybrid"
  speaker_binding: "none | actor_id | portrait_id | world_object_id"
  portrait_animation_plan: "none | blink | mouth_flap | emotion_set"
  text_audio_plan: "none | type_tick | speaker_tick | stinger_ref"
  glyph_manifest_ref: "doc/13-spec-cenas.md#glyph_manifest"
  plane_ownership_map: "BG_A/BG_B/WINDOW/SPRITES durante o texto"
  asset_budget_plan: "tiles, sprites, palette slots, DMA e cache temporario"
  teardown_reset_plan: "limpar tiles temporarios, sprites, WINDOW, paleta e audio tick"
  fallback_plan: "caixa fixa, retrato estatico, texto curto ou sem FX"
```

## Regras de aprovacao

- fala em combate rapido deve ser curta, ancorada e cancelavel quando cobrir leitura
- texto narrativo longo deve pausar ou restringir controle de forma declarada
- hype text deve ser lido antes de virar efeito
- balao diegetico nao pode esconder estado do jogador
- retrato animado nao pode consumir sprites/tiles que quebrem gameplay
- typewriter voice nao pode roubar SFX critico
- flavor text deve recompensar exploracao sem inflar roteiro inutil

## Bloqueios

Nao aprovar:

- texto longo durante acao rapida
- balao sem anchor claro
- painel sem budget de tiles
- lip sync prometido sem mouth frames ou cadence real
- hype text ilegivel em 320x224
- som de texto competindo com dano, alerta ou boss cue
- flavor text generico repetido como se fosse polish AAA

## Handoff entre skills

- `visual-excellence-standards`
  - julga leitura, ritmo visual, personalidade e excesso
- `scene-state-architect`
  - declara owner de texto, retratos, baloes, paineis, cache e teardown
- `sgdk-runtime-coder`
  - implementa reveal, draw cadence, cache, reset e fallback
- `xgm2-audio-director`
  - valida typewriter voice, stinger e prioridade de SFX
- `art-translation-to-vdp`
  - traduz paineis, retratos e baloes para assets reais de VDP
- `megadrive-vdp-budget-analyst`
  - valida VRAM, DMA, sprites, CRAM e pior quadro

## Regra final

Texto AAA no Mega Drive nao e mais texto.

E ritmo, voz, personagem, mundo e hardware trabalhando juntos.
Se qualquer uma dessas partes ficar implicita, a apresentacao ainda nao esta madura.

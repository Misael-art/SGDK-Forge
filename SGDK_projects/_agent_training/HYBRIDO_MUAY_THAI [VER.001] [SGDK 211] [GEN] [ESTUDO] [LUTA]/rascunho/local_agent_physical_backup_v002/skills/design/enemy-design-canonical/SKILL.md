---
name: enemy-design-canonical
description: Use quando a tarefa envolver design de inimigos no Mega Drive com matriz de IA (6 roles + 2 extras: patrulheiro, perseguidor, atirador, guarda, voador, bloqueador, tecnico_suporte, boss), metrica de cabecas (S/M/L/XL), telegraph obrigatorio, synergy coletiva e feedback multimodal. Emite enemy_design_report, enemy_ai_role_map, synergy_composition_map, head_metric_audit. Nao use para projetar apenas o visual do sprite (use character-design) ou para implementar IA em C (use sgdk-runtime-coder).
---

# Enemy Design Canonical

Esta skill existe para impedir que inimigo vire "sprite com HP". Todo inimigo precisa de role tatica, head metric, telegraph explicito e funcao na composicao da fase.

## Quando usar

- cena jogavel nova precisa de roster de inimigos
- reseed de inimigos existentes
- boss novo com FSM de estados
- composicao de IA sinergica (vanguarda + retaguarda, por exemplo)
- audit pre-AAA de enemy roster

## Nao use

- para projetar visual do sprite: use `character-design`
- para implementar IA em C: use `sgdk-runtime-coder`
- para tunar parametros numericos: use `systems-mechanics-validator` (numeric_attribute_table)
- para inimigos de fase final: ainda use esta skill, mas respeite `boss_state_count >= 3`

## Ler antes de agir

1. `tools/sgdk_wrapper/schemas/enemy_roster.schema.json`
2. `tools/sgdk_wrapper/schemas/enemy_design_report.schema.json`
3. `tools/sgdk_wrapper/.agent/references/enemy_ai_role_catalog.json`
4. `tools/sgdk_wrapper/.agent/references/head_metric_reference.json`
5. `level_blueprint.json` da cena (entrada obrigatoria)
6. `mechanic_validation_report.json` (entrada obrigatoria, para fraquezas)
7. `doc/13-spec-cenas.md`
8. `moodboard_manifest.json` quando existir

## Entrada minima

- `enemy_roster.json` da cena
- `level_blueprint.json` da cena
- player kit
- scene spec

## Saida minima

- `enemy_design_report.json` (status passed/warn/blocked)
- `enemy_ai_role_map` (mapa de cada inimigo -> role -> funcao tatica)
- `synergy_composition_map` (combinacoes validadas)
- `head_metric_audit` (distribuicao S/M/L/XL, compliance boss=XL)

## 6 Roles + 2 Extras

| Role | Funcao tatica | Head metric tipico | Synergy prefer |
|------|---------------|---------------------|----------------|
| `patrulheiro` | loop de waypoints, ameaca previsivel | S, M | perseguidor, atirador |
| `perseguidor` | caca ativa dentro do aggro | S, M | atirador, bloqueador |
| `atirador` | ataque a distancia, recuo | M, L | bloqueador, guarda |
| `guarda` | protege ponto/item | M, L | atirador, bloqueador |
| `voador` | movimentacao 3D | S, M, L | perseguidor, atirador |
| `bloqueador` | mitigacao de dano, escudo | M, L | atirador, tecnico_suporte |
| `tecnico_suporte` | heal, buff, controle de zona | M | bloqueador, atirador |
| `boss` | tela tomada, FSM >= 3 estados | XL | (sem synergy) |
| `solo_tutorial` | ensino isolado, sem synergy | S | (sem synergy) |

## Metrica de Cabecas (S/M/L/XL)

- `S` (< 0.5x jogador): HP baixo, ataque fraco, rapido. Exige que jogador abaixe.
- `M` (~ 1x jogador): parametros equilibrados.
- `L` (4-7x jogador): HP alto, ataque massivo, lento. Exige pulo para weak point.
- `XL` (> 7x jogador): imenso, chefe de fase. `boss` requer XL.

Regra critica:

- `role=boss` E `head_metric != XL` -> `enemy_head_metric_invalid`
- `role != boss` E `head_metric == XL` -> `enemy_head_metric_invalid`

## Telegraph Obrigatorio

Todo inimigo de combate precisa de `telegraph_model`:

- `telegraph_frames` (>= 1 frame antes do ataque)
- `visual_cue` (cor, scale, blink)
- `audio_cue` (stinger ou SFX dedicado)
- `color_contract` (consistente com `consistency law` da mecanica)

## Synergy Coletiva

Combinacoes que enriquecem o combate:

- `bloqueador` (vanguarda) + `atirador` (retaguarda) = escudo + DPS seguro
- `perseguidor` (flanqueador) + `atirador` (estatico) = pressiona gap
- `voador` (interrompe pulo) + `guarda` (trava chao) = sem rota
- `tecnico_suporte` (heal) + `bloqueador` (escudo) = composicao defensiva

Cada synergy precisa de `synergy_type` declarado: `frontline_shield`, `backline_dps`, `flanker`, `support_heal`, `control_zoner`, `bait`.

## Feedback Multimodal

Todo inimigo precisa de:

- `feedback_on_hit` (visual + audio + hitstop_frames)
- `feedback_on_alert` (visual + audio + stinger_id quando for transicao para combate)

Sincronizar com `xgm2-audio-director` para stinger.

## Bloqueios emitidos

- `enemy_roster_missing` (tecnico)
- `enemy_role_missing` (criativo)
- `enemy_telegraph_missing` (criativo)
- `enemy_synergy_missing` (criativo)
- `enemy_level_function_missing` (criativo)
- `enemy_head_metric_invalid` (criativo)

## Passa quando

- cada inimigo tem `role`, `head_metric`, `telegraph_model`, `synergy_partners` (vazio so para `solo_tutorial`)
- `boss` tem `head_metric=XL` e `boss_state_count >= 3` (ou `boss_curto_justification`)
- nenhum `non-boss` tem `head_metric=XL`
- `head_metric_audit.boss_xl_compliance = true`
- `synergy_composition_map` tem pelo menos 1 composicao com 2+ membros para cenas com 4+ inimigos
- `feedback_on_hit` e `feedback_on_alert` declarados para todos os inimigos de combate

## Handoff

- para `character-design`: entregar `enemy_roster.json` (filtro por head metric) para identidade visual
- para `sprite-animation`: entregar lista de inimigos com `movement_model` para escolha de cycles
- para `xgm2-audio-director`: entregar `feedback_on_alert.stinger_id` para eventos de audio
- para `sgdk-runtime-coder`: entregar `enemy_design_report.json` + `ai_behavior` + `movement_model` para implementacao da IA

## Anti-padroes

- inimigo sem role tatica definida
- boss com 1 estado so ("ele so da soco")
- `head_metric=XL` para inimigo nao-boss (foge do frame)
- telegraph de 0 frames (inimigo "injusto")
- 6 patrulheiros sem diversity de role (todas as ameacas iguais)
- synergy vazia para inimigo de fase normal (sugere erro de design, nao tutorial)

## Senior Competencies

- `tactical_function_per_role` - cada role tem funcao clara
- `head_metric_compliance` - boss sempre XL, nao-boss nunca XL
- `telegraph_discipline` - telegraph consistente entre inimigos
- `synergy_curation` - composicoes validadas manualmente, nao aleatorias
- `feedback_synchronization` - feedback visual e audio coordenados

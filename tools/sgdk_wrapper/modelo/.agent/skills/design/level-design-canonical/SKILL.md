---
name: level-design-canonical
description: Use quando a tarefa envolver design de fase jogavel no Mega Drive com Golden Path visivel, narrativa ambiental, agencia no desafio, ritmo de fase (calm/pressure/payoff) e quebra de padrao entre cenas. Emite level_design_report, golden_path_review, phase_rhythm_review, mechanic_reuse_review. Nao use para criar apenas a arte da fase (use multi-plane-composition) ou para implementar a fase (use sgdk-runtime-coder).
---

# Level Design Canonical

Esta skill existe para impedir que fase vire apenas "tilemap + spawn points". Toda fase jogavel precisa de Golden Path visivel, ritmo declarado, narrativa ambiental e reuso declarado de mecanicas core.

## Quando usar

- cena jogavel nova (gameplay, boss, platformer, run_and_gun, etc.)
- reseed de fase existente que perdeu coerencia
- transicao entre fases precisa de pattern_break_audit
- validacao pre-AAA de fase contra nivel canonico

## Nao use

- para cena nao-jogavel: use `cutscene-cinematic-direction` ou `scene-direction-curator`
- para arte visual: use `multi-plane-composition`
- para implementar: use `sgdk-runtime-coder`
- para mecanicas: use `systems-mechanics-validator` antes desta skill

## Ler antes de agir

1. `tools/sgdk_wrapper/schemas/level_blueprint.schema.json`
2. `tools/sgdk_wrapper/schemas/level_design_report.schema.json`
3. `mechanic_validation_report.json` (entrada obrigatoria)
4. `moodboard_manifest.json` quando existir
5. `enemy_roster.json` da cena ou fase quando existir
6. `doc/13-spec-cenas.md`
7. `tools/sgdk_wrapper/.agent/references/head_metric_reference.json` para escala de inimigos
8. `camera_behavior_contract.json` quando camera ou scroll ja estiverem planejados

## Entrada minima

- `scene_roadmap` ou lista de cenas
- `mechanic_validation_report.json` (para `mechanic_reuse_map`)
- `level_blueprint.json` da cena alvo
- GDD/spec
- `camera_visibility_plan` ou `camera_behavior_seed` quando a fase depender de scroll, plataforma, chase, boss room, queda ou ameaca fora da tela
- opcional: `enemy_roster.json` da cena
- opcional: `moodboard_manifest.json`

## Saida minima

- `level_design_report.json` (status passed/warn/blocked + reviews)
- `golden_path_review` (waypoint count, landmarks, risk_markers telegraphed)
- `phase_rhythm_review` (calm/pressure/payoff presente, boss phase, breathing zones)
- `mechanic_reuse_review` (core mechanics covered, missing core mechanic ids)
- `camera_readability_review` quando a fase usar camera jogavel
- opcional: `pattern_break_audit` (vs cena anterior)

## Golden Path

Toda fase jogavel precisa de:

- `waypoint_sequence` (minimo 2 waypoints)
- `visible_landmarks` (referencias visuais que guiam o jogador sem texto)
- `telegraph_chain` (sequencia de sinais que mostram ameaca antes de chegar)
- `risk_markers` com `telegraph` declarado
- o caminho dourado e o caminho obvio, nao o unico

## Narrativa Ambiental

A historia da fase precisa ser contada pelo cenario, nao por dialogo:

- `environmental_narrative_map` (elemento -> story_beat)
- `no_text_required` sempre que possivel
- destruicao, iluminacao e disposicao contam o que aconteceu
- a cena seguinte deve poder ser inferida olhando a fase anterior

## Agencia no Desafio

O mapa deve escancarar a existencia do perigo e para onde ir, mas nunca a solucao:

- `risk_markers` visiveis
- `gates` com `telegraph` declarado
- `optional_routes` sinalizados por recompensa, nao por arrow
- o jogador falha por decisao, nao por falta de informacao

## Camera e Legibilidade

Camera e parte do level design, nao apenas runtime. Quando houver scroll jogavel:

- `camera_visibility_plan` declara visao a frente, politica vertical, blind jumps e trigger zones
- plataformas, quedas, inimigos e hazards precisam entrar no campo visivel antes do ponto de decisao
- boss room, auto-scroll e room lock exigem trigger claro e saida/reset planejado
- deadzone e look-ahead devem servir a leitura do desafio, nao apenas suavizar movimento

## Quebra de Padrao

A cada nova fase, a experiencia precisa mudar:

- paleta diferente da cena anterior
- ritmo diferente (calm/pressure/payoff ou boss)
- pelo menos 1 hazard novo
- `pattern_break_audit.palette_differentiation` >= minor
- `pattern_break_audit.rhythm_variation` >= minor

## Ritmo de Fase (phase_rhythm_map)

Toda fase precisa de:

- `calm` (respiracao, aprendizagem)
- `pressure` (tensao crescente, encounter)
- `payoff` (recompensa, conclusao) ou `boss`
- `breathing_zones` (pelo menos 1 entre phases intensas)
- `audio_state` por phase (referencia ao adaptive_music_state_map)

## Reuso de Mecanicas

Toda mecanica core deve ser reutilizada na fase:

- `mechanic_reuse_map` lista core_mechanic_id -> target_scene -> reuse_count
- `missing_core_mechanic_ids` reporta core mechanics que nao aparecem
- `level_mechanic_reuse_missing` bloqueia quando ha core mechanic na cena sem reuso

## Bloqueios emitidos

- `level_blueprint_missing` (tecnico)
- `golden_path_missing` (criativo)
- `phase_rhythm_missing` (criativo)
- `level_mechanic_reuse_missing` (criativo)
- `level_goal_path_unclear` (criativo)
- `level_risk_untelegraphed` (criativo)
- `camera_visibility_missing` (criativo)
- `blind_jump_untelegraphed` (criativo)

## Passa quando

- `golden_path.waypoint_sequence` tem >= 2 waypoints
- `phase_rhythm_map` contem `calm` E `pressure` (ou justifica `not_applicable`)
- `mechanic_reuse_map` cobre todas as core mechanics declaradas no contract
- `risk_markers` tem `telegraph` declarado
- camera jogavel possui `camera_visibility_plan` ou contrato equivalente antes do runtime
- `pattern_break_audit` mostra diferenciacao vs cena anterior (quando aplicavel)

## Handoff

- para `enemy-design-canonical`: entregar `level_blueprint.json` para que inimigos sejam posicionados
- para `multi-plane-composition`: entregar `golden_path` + `narrative_environmental_map` para composicao visual
- para `scene-state-architect`: entregar `camera_visibility_plan` quando houver camera owner/triggers
- para `xgm2-audio-director`: entregar `phase_rhythm_map` com `audio_state` por phase
- para `sgdk-runtime-coder`: entregar `level_design_report.json` + `waypoints` + `gates` para implementacao

## Anti-padroes

- "fase linear sem breathing zone"
- inimigos spawnados sem risck_marker com telegraph
- mecanica core declarada mas nunca usada na fase
- mesma paleta e mesmo ritmo da fase anterior
- golden path sem landmarks visuais (jogador perdido sem texto)
- blind jump, inimigo ou hazard que so aparece depois do compromisso de movimento
- boss room ou auto-scroll sem camera trigger e plano de reset
- narrativa ambiental que exige texto explicativo

## Senior Competencies

- `golden_path_visibility` - sem texto, o caminho e obvio
- `rhythm_curation` - alterna calm/pressure/payoff com variacao vs cena anterior
- `narrative_through_environment` - historia contada por cenario, luz, destruicao
- `mechanic_density` - core mechanics aparecem com frequencia suficiente para serem dominadas
- `pattern_break_audit` - cada cena introduz variacao detectavel
- `camera_readability` - camera mostra decisao antes do risco e nao transforma desafio em surpresa injusta

# Workflow: Production Loop

Use este fluxo para o pipeline completo de uma iteracao: design -> arte -> runtime -> QA -> evidencia.

Cada passo referencia skills reais. A ordem canonica da jornada de cena AAA vive em:

- `workflows/aaa-scene-pipeline.md`
- `pipelines/aaa_scene_v1.json`

Nenhum passo pode ser pulado.

---

## Pipeline: Design -> Art -> Code -> QA -> Iteracao

### 1. Escopo, planejamento e mecanica

Papel humano: direcao de produto.

Skill canonica de apoio quando o projeto estiver nascendo ou precisar de reseed:

- `planning/game-design-planning`

- consultar `doc/11-gdd.md` e `doc/13-spec-cenas.md`
- em projeto novo ou reseed de escopo, emitir `project_brief`, `core_loop_statement`, `feature_scope_map`, `scene_roadmap`, `first_playable_slice`, `roteiro_scope` e `front_end_profile`
- delimitar escopo da iteracao
- registrar criterio de aceitacao
- quando houver menu, title screen ou front-end, `front_end_profile` nasce aqui como seed de design e depois e formalizado como `ui_decision_card`
- quando a iteracao envolver HUD/UI formal, declarar `ui_decision_card` no GDD/spec antes de abrir arte/runtime
- quando a UI tiver peso tipografico real, derivar `glyph_manifest` de strings reais e anexar `typography_role`, `font_render_mode`, `charset_profile`, `glyph_budget_class`, `font_owner` e `fallback_font_plan` ao mesmo card
- quando a iteracao envolver transicao formal entre cenas, zonas, atos, menu, cutscene ou estado visual, declarar `scene_transition_card` antes de abrir arte/runtime
- quando a transicao tocar HUD, menu, title, overlay ou texto critico, referenciar tambem o `ui_decision_card`
- quando a iteracao envolver menu, title screen ou front-end, o mesmo card deve usar `profile_kind=front_end_profile`

Saida minima:

- briefing aceito
- seeds de planejamento suficientes quando o projeto estiver nascendo ou o escopo estiver sendo redefinido
- `ui_decision_card` quando houver surface formal de UI
- `glyph_manifest` + anexo tipografico quando a tipografia tiver peso dramatico ou de leitura
- `scene_transition_card` quando houver transicao formal

### 2. Arte e composicao

Skills oficiais:

1. `art/art-asset-diagnostic`
2. `art/multi-plane-composition`
3. `art/art-translation-to-vdp`
4. `art/visual-excellence-standards`
5. `hardware/megadrive-vdp-budget-analyst`

Saida minima:

- laudos e artefatos de arte completos
- decisao explicita `cabe`, `cabe com recuo` ou `nao cabe`
- quando houver UI formal, `ui_decision_card` coerente com ownership, budget e fallback
- quando houver tipografia relevante, o card tambem precisa ficar coerente com `font_render_mode`, `charset_profile` e `fallback_font_plan`
- quando houver transicao formal, `scene_transition_card` coerente com continuidade, camera, ownership, audio, teardown e fallback
- quando houver mais de uma rota visual honesta, `route_exploration_board` + `route_decision_record` antes do runtime

Regra de curadoria AAA:

- explorar alternativas e permitido
- reabrir a direcao visual do zero a cada iteracao, nao e permitido
- a exploracao deve acontecer dentro do mesmo `shared_canvas_contract` e congelar uma `locked_visual_direction` escolhida pelo usuario ou recomendada pelo juiz estetico

### 3. Integracao runtime

Skills oficiais:

- `code/sgdk-runtime-coder`
- `architecture/scene-state-architect`
- `operation/sgdk-build-wrapper-operator`

Saida minima:

- build limpo
- `runtime_decision_log`
- ownership de `WINDOW`, `H-Int` e FX de interface rastreavel quando houver UI formal
- ownership de fonte, cache temporario de glifos e fallback_font_plan rastreavel quando houver anexo tipografico
- `runtime_state_handoff`, `teardown_reset_plan` e fallback rastreaveis quando houver transicao formal
- ROM gerada

### 4. Validacao e evidencia

Ferramentas e gates:

- `validate_resources.ps1`
- `workflows/build-validate.md`
- BlastEm obrigatorio
- `doc/changelog`
- `doc/10-memory-bank.md`

Saida minima:

- `validation_report.json`
- `emulator_session.json`
- changelog atualizado
- memoria operacional coerente

### 5. Iteracao

- triagem humana
- voltar para a skill da etapa afetada
- nunca corrigir no escuro sem registrar a classe real do erro

---

## Regras do Loop

- nenhum passo pode ser pulado
- assets nao validados nao entram no build
- budget nao e declarado por intuicao
- ROM nao testada nao e entregue
- changelog nao e opcional
- memoria operacional nao substitui evidência
- BlastEm fecha gate de entrega
- FX de interface sem owner, teardown e fallback nao sobe
- menu/title screen segue a mesma barra AAA das cenas jogaveis e nao pode ser tratado como overlay funcional tardio
- transicao de cena sem `scene_transition_card`, causa dramatica, teardown e fallback nao sobe

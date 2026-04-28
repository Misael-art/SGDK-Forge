# Workflow: Production Loop

Use este fluxo para o pipeline completo de uma iteracao: design -> arte -> runtime -> QA -> evidencia.

Cada passo referencia skills reais. A ordem canonica da jornada de cena AAA vive em:

- `workflows/aaa-scene-pipeline.md`
- `pipelines/aaa_scene_v1.json`

Nenhum passo pode ser pulado.

---

## Pipeline: Design -> Art -> Code -> QA -> Iteracao

### 0. Abertura e classificacao do contexto

Workflow canonico de entrada:

- `workflows/project-opening.md`
- `workflows/route-decision-gate.md`

O agente deve primeiro classificar o pedido como:

- `projeto_existente`
- `reseed`
- `projeto_novo`

Regra:

- se for `projeto_existente`, continuar a iteracao vigente
- se for `reseed` ou `projeto_novo`, emitir fundacao documental minima antes de arte ou runtime
- se a rota tecnica da entrega ainda nao estiver declarada, emitir `route_decision_record` antes de escolher ferramenta ou skill de implementacao

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
- quando texto, fala, alerta cinetico, painel, balao, retrato, typewriter voice ou flavor text tiver peso dramatico, anexar `text_presentation_profile` ao mesmo card
- quando a iteracao envolver transicao formal entre cenas, zonas, atos, menu, cutscene ou estado visual, declarar `scene_transition_card` antes de abrir arte/runtime
- quando a transicao tocar HUD, menu, title, overlay ou texto critico, referenciar tambem o `ui_decision_card`
- quando a iteracao envolver menu, title screen ou front-end, o mesmo card deve usar `profile_kind=front_end_profile`
- quando a iteracao for o primeiro slice de projeto novo, declarar tambem `route_decision_record` com `dominant_route`, `first_skill`, `first_tool`, `resource_loading_model`, `asset_strategy`, evidencias e atalhos bloqueados
- quando a iteracao envolver raster, H-Int, line scroll, palette split, Shadow/Highlight, palette cycling, hit sparks, particulas ou feedback dramatizado, declarar `feedback_fx_decision_card`
- quando a iteracao envolver boss, setpiece, weak point, telegraph, plane takeover ou arena especial, declarar `boss_setpiece_card`
- quando a iteracao envolver streaming, metatiles, priority foreground, destruicao local, parallax regional ou rota complexa, declarar `advanced_tilemap_design_card`
- quando a iteracao envolver XGM2, PCM ownership, ambience, stinger, boss cue, fade ou prioridade de SFX, declarar `audio_architecture_card`
- quando houver audio declarado em `.res`, rodar `tools/sgdk_wrapper/validate_audio.ps1` e registrar `out/logs/audio_validation_report.json` antes do fechamento
- quando a cena tiver perfil `aaa_layered`, registrar antes da arte/runtime uma triagem arquitetural com `scene_profile`, `baseline_technique_applicability`, `baseline_contract`, `baseline_decision`, `divergence_reason` quando houver divergencia e `reference_implementation` quando houver referencia interna forte
- para esse perfil, `tilemap streaming guiado pela camera` vira baseline arquitetural prioritario de analise, sem obrigar replicacao cega
- se a tecnica for aplicavel em modo `sim` ou `parcial`, extrair dela explicitamente: divisao base/foreground, papel de cada plano, staging visual, organizacao de tilemaps, forma de oclusao e relacao sprite/cenario
- se houver uma referencia interna madura, como a `BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BRIGA DE RUA]`, usa-la como implementacao de apoio, nao como nome da tecnica
- se a cena divergir, justificar o desvio com constraints reais antes de abrir depuracao residual de VRAM, paleta, `rescomp`, `WINDOW` ou sprite runtime

Saida minima:

- briefing aceito
- seeds de planejamento suficientes quando o projeto estiver nascendo ou o escopo estiver sendo redefinido
- `route_decision_record` quando a rota tecnica ainda nao estiver congelada
- `ui_decision_card` quando houver surface formal de UI
- `glyph_manifest` + anexo tipografico quando a tipografia tiver peso dramatico ou de leitura
- anexo `ui_decision_card.text_presentation_profile` quando texto for encenacao, fala, alerta, flavor ou ritmo dramatico
- `scene_transition_card` quando houver transicao formal
- `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` e `audio_architecture_card` quando a cena tocar esses dominios
- em audio senior, combinar `xgm2-audio-director` com `z80-pcm-custom-driver` apenas quando o XGM2 padrao nao cobrir a necessidade real

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
- quando o projeto ja tiver builder dedicado em `tools/image-tools/build_*.py` ou `doc/source_cases/**/case_manifest.json`, essa rota curada deve ser tentada antes de OCR, thumbnailing, crop manual ou lote generico
- quando houver UI formal, `ui_decision_card` coerente com ownership, budget e fallback
- quando houver tipografia relevante, o card tambem precisa ficar coerente com `font_render_mode`, `charset_profile` e `fallback_font_plan`
- quando houver texto expressivo, o card tambem precisa declarar `text_surface_class`, ritmo, ancoragem, audio, teardown e fallback
- quando houver transicao formal, `scene_transition_card` coerente com continuidade, camera, ownership, audio, teardown e fallback
- quando houver feedback FX, boss/setpiece, tilemap avancado ou audio senior, os cards precisam ficar coerentes com gameplay_signal, leitura, ownership, budget e fallback
- quando houver mais de uma rota visual honesta, `route_exploration_board` + `route_decision_record` antes do runtime

Regra de curadoria AAA:

- explorar alternativas e permitido
- reabrir a direcao visual do zero a cada iteracao, nao e permitido
- a exploracao deve acontecer dentro do mesmo `shared_canvas_contract` e congelar uma `locked_visual_direction` escolhida pelo usuario ou recomendada pelo juiz estetico
- em cenas `aaa_layered`, a exploracao visual deve acontecer depois da comparacao com o baseline de `tilemap streaming guiado pela camera`, nunca no lugar dela

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
- ownership de paineis, baloes, retratos, texto cinetico, SFX de texto e teardown rastreavel quando houver `text_presentation_profile`
- `runtime_state_handoff`, `teardown_reset_plan` e fallback rastreaveis quando houver transicao formal
- ownership, teardown e fallback rastreaveis para feedback FX, boss/setpiece, tilemap avancado e audio senior quando seus cards existirem
- se houver audio declarado, `validation_report.json` deve refletir o estado de `audio_validation_report.json`; trilha de audio fora do validator principal nao fecha gate
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
- em cenas `aaa_layered`, revisar primeiro se o erro e de contrato arquitetural antes de descer para depuracao residual de recurso, VDP ou sprite

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
- raster/luz/particula/boss/tilemap/audio sem card formal, owner, budget e fallback nao sobe

# Workflow: AAA Scene Pipeline

Ordem canonica para uma cena visual de barra AAA.

Fonte machine-readable: `pipelines/aaa_scene_v1.json`.

Este arquivo nao substitui as skills. Ele so define sequencia, minima entrada, minima saida e passagem segura.

---

| # | Etapa | Entrada minima | Saida minima | Passa quando | Handoff |
|---|-------|----------------|--------------|--------------|---------|
| 0 | Escopo humano | classificacao previa via `workflows/project-opening.md`; quando a rota tecnica ainda nao estiver clara, abrir `workflows/route-decision-gate.md`; para projeto existente, `doc/11-gdd.md` e `doc/13-spec-cenas.md`; para projeto novo ou reseed, respostas do questionario de fundacao | briefing com objetivo, limites e criterio de aceitacao; em projeto novo ou reseed, usar `planning/game-design-planning` para emitir `project_brief`, `scene_roadmap`, `first_playable_slice`, `route_decision_record`, `roteiro_scope` e `front_end_profile`; quando houver HUD/UI formal, `ui_decision_card` declarado; quando houver peso tipografico real, `glyph_manifest` + anexo tipografico declarados; quando houver texto dramatico, fala, alerta cinetico ou flavor text, o anexo `ui_decision_card.text_presentation_profile` deve ser declarado dentro do mesmo card; quando houver transicao formal, `scene_transition_card` declarado; quando houver raster/luz/FX, boss/setpiece, tilemap avancado ou audio senior, declarar `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` ou `audio_architecture_card`; em menu/title/front-end, usar `profile_kind=front_end_profile` | o contexto foi classificado corretamente; escopo fechado sem creep e, quando aplicavel, seeds de planejamento, rota tecnica, UI, texto, transicao, FX, boss, tilemap e audio declarados antes do runtime | `art/art-asset-diagnostic` |
| 1 | `art/art-asset-diagnostic` | `res/`, `res/data/`, `.res` | laudo de cenario + issues bloqueantes | rota de arte decidida e registrada | `art/multi-plane-composition` ou `art/art-conversion-pipeline` |
| 2 | `art/multi-plane-composition` | mapa de composicao, spec da cena, referencia visual | `depth_role_map`, `composition_schema`, `layer_plan`, `shared_canvas_contract`, `hardware_budget_review`, `delivery_findings` e cards formais quando houver UI/transicao/FX/boss/tilemap | planos, parallax e estrategia de ROM declarados; se houver rotas, a mesma cena continua travada por um `shared_canvas_contract` unico; cards formais saem com ownership, arquitetura, fallback, leitura e budget preliminar congelados | `art/art-translation-to-vdp` |
| 3 | `art/art-translation-to-vdp` | `source_image`, alvo, `layer_plan`, referencia e expectativas de hardware | `semantic_parse_report`, `translation_report`, `basic`, `elite`, `review estrutural` + opcionalmente `route_exploration_board`, `route_comparison_matrix`, `route_decision_record` | a traducao preserva leitura, gera artefatos auditaveis e congela uma direcao se houver multiplas rotas fortes | `art/visual-excellence-standards` |
| 4 | `art/visual-excellence-standards` | assets por layer, benchmark, cards formais quando existirem e `route_exploration_board` quando existir | parecer estetico + status por asset + recomendacao de rota | nenhum asset critico fica em `rework`; cards formais de UI, tipografia, texto expressivo, transicao, feedback FX, boss/setpiece, tilemap e audio ficam julgados por clareza, impacto e coerencia | `hardware/megadrive-vdp-budget-analyst` |
| 5 | `hardware/megadrive-vdp-budget-analyst` | `.res`, dimensoes, `build_output.log` quando existir, parametros reais de runtime e cards formais existentes | laudo `cabe` / `cabe com recuo` / `nao cabe` | budget explicito, motivado por numeros e coerente com UI, tipografia, texto expressivo, transicao, feedback FX, boss/setpiece, tilemap avancado, audio, ownership e fallback | `code/sgdk-runtime-coder` |
| 6 | `code/sgdk-runtime-coder` | specs, laudo de budget vigente, `.res`, `src/**/*.c` e cards formais existentes | `runtime_decision_log`, `build_evidence`, `delivery_findings` | build limpo, decisao de runtime coerente com budget; cards formais registram owner, reset, fallback e handoff no `runtime_decision_log` | `validate_resources.ps1` |
| 7 | `validate_resources.ps1` | projeto buildado, logs, `doc/changelog` | `validation_report.json` | `summary.errors == 0` e nenhum blocker de fechamento ativo | BlastEm + `build-validate.md` |
| 8 | BlastEm + `build-validate.md` | ROM, logs e captura | `emulator_session.json`, evidencia dedicada, `doc/changelog`, `doc/10-memory-bank.md` atualizados | a ROM vigente foi observada com evidencia rastreavel | encerramento / proxima iteracao |

---

## Triagem arquitetural prioritaria

Antes da etapa 2, toda cena com perfil `aaa_layered` deve registrar uma triagem arquitetural minima:

- `scene_profile`
- `baseline_technique_applicability`
- `baseline_contract`
- `baseline_decision`
- `divergence_reason` quando houver divergencia
- `reference_implementation` quando houver referencia interna forte

Regra de decisao:

- use `tilemap streaming guiado pela camera` como baseline arquitetural prioritario para cenas com base + foreground + oclusao + relacao forte entre sprite e cenario
- trate essa prioridade como presuncao forte de metodo, nao como regra cega de replicacao
- se a tecnica for `sim` ou `parcial`, extraia explicitamente: divisao base/foreground, papel de cada plano, staging visual, organizacao de tilemaps, forma de oclusao e relacao sprite/cenario
- se houver uma referencia interna madura, como a `BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BRIGA DE RUA]`, registre-a como implementacao de apoio, nao como nome da tecnica
- se a decisao final for `divergir`, a justificativa deve citar constraints reais da cena antes de qualquer depuracao residual
- bugs de VRAM, paleta, `rescomp`, visibilidade de sprite ou workaround de `WINDOW` nao devem ser tratados como primeira linha quando a triagem arquitetural ainda nao foi fechada

---

## Dependencias Fixas

- Antes do primeiro build da sessao: `tools/sgdk_wrapper/preflight_host.ps1`
- Antes de declarar que a cena `cabe`: laudo da `megadrive-vdp-budget-analyst`
- Antes de declarar `validado` ou `AAA`: BlastEm + changelog + memoria operacional coerentes

---

## Escada Forense Obrigatoria

1. header PNG / PLTE
2. `rescomp` raw tiles
3. formula real de VRAM
4. decisao de arquitetura (`IMAGE`, `MAP`, streaming, `compare_flat`)
5. BlastEm

Se esta ordem nao foi cumprida, a analise nao esta completa.

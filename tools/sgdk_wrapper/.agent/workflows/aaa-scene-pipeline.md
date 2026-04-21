# Workflow: AAA Scene Pipeline

Ordem canonica para uma cena visual de barra AAA.

Fonte machine-readable: `pipelines/aaa_scene_v1.json`.

Este arquivo nao substitui as skills. Ele so define sequencia, minima entrada, minima saida e passagem segura.

---

| # | Etapa | Entrada minima | Saida minima | Passa quando | Handoff |
|---|-------|----------------|--------------|--------------|---------|
| 0 | Escopo humano | `doc/11-gdd.md`, `doc/13-spec-cenas.md` | briefing com objetivo, limites e criterio de aceitacao; em projeto novo ou reseed, usar `planning/game-design-planning` para emitir `project_brief`, `scene_roadmap`, `first_playable_slice`, `roteiro_scope` e `front_end_profile`; quando houver HUD/UI formal, `ui_decision_card` declarado; quando houver peso tipografico real, `glyph_manifest` + anexo tipografico declarados; quando houver transicao formal, `scene_transition_card` declarado; em menu/title/front-end, usar `profile_kind=front_end_profile` | escopo fechado sem creep e, quando aplicavel, seeds de planejamento, UI e transicao declarados antes do runtime | `art/art-asset-diagnostic` |
| 1 | `art/art-asset-diagnostic` | `res/`, `res/data/`, `.res` | laudo de cenario + issues bloqueantes | rota de arte decidida e registrada | `art/multi-plane-composition` ou `art/art-conversion-pipeline` |
| 2 | `art/multi-plane-composition` | mapa de composicao, spec da cena, referencia visual | `depth_role_map`, `composition_schema`, `layer_plan`, `shared_canvas_contract`, `hardware_budget_review`, `delivery_findings` e, quando houver UI/transicao formal, `ui_decision_card` / `scene_transition_card` | planos, parallax e estrategia de ROM declarados; se houver rotas, a mesma cena continua travada por um `shared_canvas_contract` unico; UI formal sai com ownership, arquitetura, fallback e, quando aplicavel, `font_render_mode`; transicao formal sai com continuidade, camera e fallback congelados | `art/art-translation-to-vdp` |
| 3 | `art/art-translation-to-vdp` | `source_image`, alvo, `layer_plan`, referencia e expectativas de hardware | `semantic_parse_report`, `translation_report`, `basic`, `elite`, `review estrutural` + opcionalmente `route_exploration_board`, `route_comparison_matrix`, `route_decision_record` | a traducao preserva leitura, gera artefatos auditaveis e congela uma direcao se houver multiplas rotas fortes | `art/visual-excellence-standards` |
| 4 | `art/visual-excellence-standards` | assets por layer, benchmark, `ui_decision_card` / `scene_transition_card` quando existirem e `route_exploration_board` quando existir | parecer estetico + status por asset + recomendacao de rota | nenhum asset critico fica em `rework`; se houver multiplas rotas validas, uma `locked_visual_direction` foi escolhida antes do budget final; UI formal sai com `attention_profile` e `hud_density` julgados; tipografia relevante sai julgada; transicao formal sai com `transition_role`, continuidade e clareza julgados | `hardware/megadrive-vdp-budget-analyst` |
| 5 | `hardware/megadrive-vdp-budget-analyst` | `.res`, dimensoes, `build_output.log` quando existir, parametros reais de runtime, `ui_decision_card` e `scene_transition_card` quando existirem | laudo `cabe` / `cabe com recuo` / `nao cabe` | budget explicito, motivado por numeros e coerente com UI, tipografia e, quando houver transicao formal, `continuity_model`, `fx_ownership_map`, audio e fallback | `code/sgdk-runtime-coder` |
| 6 | `code/sgdk-runtime-coder` | specs, laudo de budget vigente, `.res`, `src/**/*.c`, `ui_decision_card` e `scene_transition_card` quando existirem | `runtime_decision_log`, `build_evidence`, `delivery_findings` | build limpo, decisao de runtime coerente com o budget e contratos de WINDOW/H-Int/FX respeitados; tipografia relevante fica rastreavel; transicao formal registra handoff de estado, teardown e fallback | `validate_resources.ps1` |
| 7 | `validate_resources.ps1` | projeto buildado, logs, `doc/changelog` | `validation_report.json` | `summary.errors == 0` e nenhum blocker de fechamento ativo | BlastEm + `build-validate.md` |
| 8 | BlastEm + `build-validate.md` | ROM, logs e captura | `emulator_session.json`, evidencia dedicada, `doc/changelog`, `doc/10-memory-bank.md` atualizados | a ROM vigente foi observada com evidencia rastreavel | encerramento / proxima iteracao |

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

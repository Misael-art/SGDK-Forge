# Workflow: AAA Scene Pipeline

Ordem canonica para uma cena visual de barra AAA.

Fonte machine-readable: `pipelines/aaa_scene_v1.json`.

Este arquivo nao substitui as skills. Ele so define sequencia, minima entrada, minima saida e passagem segura.

---

| # | Etapa | Entrada minima | Saida minima | Passa quando | Handoff |
|---|-------|----------------|--------------|--------------|---------|
| 0 | Escopo humano | `doc/11-gdd.md`, `doc/13-spec-cenas.md` | briefing com objetivo, limites e criterio de aceitacao | escopo fechado sem creep | `art/art-asset-diagnostic` |
| 1 | `art/art-asset-diagnostic` | `res/`, `res/data/`, `.res` | laudo de cenario + issues bloqueantes | rota de arte decidida e registrada | `art/multi-plane-composition` ou `art/art-conversion-pipeline` |
| 2 | `art/multi-plane-composition` | mapa de composicao, spec da cena, referencia visual | `depth_role_map`, `composition_schema`, `layer_plan`, `shared_canvas_contract`, `hardware_budget_review`, `delivery_findings` | planos, parallax e estrategia de ROM declarados; se houver rotas, a mesma cena continua travada por um `shared_canvas_contract` unico | `art/art-translation-to-vdp` |
| 3 | `art/art-translation-to-vdp` | `source_image`, alvo, `layer_plan`, referencia e expectativas de hardware | `semantic_parse_report`, `translation_report`, `basic`, `elite`, `review estrutural` + opcionalmente `route_exploration_board`, `route_comparison_matrix`, `route_decision_record` | a traducao preserva leitura, gera artefatos auditaveis e congela uma direcao se houver multiplas rotas fortes | `art/visual-excellence-standards` |
| 4 | `art/visual-excellence-standards` | assets por layer, benchmark e `route_exploration_board` quando existir | parecer estetico + status por asset + recomendacao de rota | nenhum asset critico fica em `rework`; se houver multiplas rotas validas, uma `locked_visual_direction` foi escolhida antes do budget final | `hardware/megadrive-vdp-budget-analyst` |
| 5 | `hardware/megadrive-vdp-budget-analyst` | `.res`, dimensoes, `build_output.log` quando existir, parametros reais de runtime | laudo `cabe` / `cabe com recuo` / `nao cabe` | budget explicito e motivado por numeros | `code/sgdk-runtime-coder` |
| 6 | `code/sgdk-runtime-coder` | specs, laudo de budget vigente, `.res`, `src/**/*.c` | `runtime_decision_log`, `build_evidence`, `delivery_findings` | build limpo e decisao de runtime coerente com o budget | `validate_resources.ps1` |
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

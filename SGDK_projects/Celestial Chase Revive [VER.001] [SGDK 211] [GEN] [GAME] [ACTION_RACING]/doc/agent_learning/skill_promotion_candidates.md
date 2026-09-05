# Skill Promotion Candidates

Este arquivo lista candidatos locais que talvez merecam virar skill, workflow, regra, script ou `lib_case` canonico no futuro.

Nenhum item aqui esta promovido.

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| [DATA] | `promotion_candidate` | [nome curto] | [problema] | [build/log/screenshot/hash] | [baixo/medio/alto] | [criterio] |
| 2026-06-16 | `promotion_candidate` | `planning_mode_pre_runtime_spec_closure_checklist` | Planejamento AAA parecia completo sem contratos executaveis para runtime | `doc/canonical_planning_curation_handoff.json`, `doc/critical_gap_audit.json`, validacoes JSON/context/metodologia/higiene | medio | Humano avaliar como gate proporcional para `aaa_game` |
| 2026-06-16 | `promotion_candidate` | `front_end_identity_minimum_contract` | Fonte, logo, menu e creditos podem ficar subespecificados | `doc/front_end_element_audit.json`, schemas de brand/UI ok | baixo | Humano decidir se entra no checklist visual/front-end |
| 2026-06-16 | `promotion_candidate` | `central_build_contract_before_runtime_seed` | Pedido de Makefile local conflita com wrapper canonico | `doc/build_system_contract.json`, `.mddev/project.json` | baixo | Humano decidir se vira contrato obrigatorio para projetos SGDK |
| 2026-06-16 | `promotion_candidate` | `local_mockup_manifest_for_planning_art` | Texto puro nao guia pixel art; mockup sem hash pode virar evidencia falsa | `doc/concept_art_pack_manifest.json`, hashes dos SVGs locais | medio | Humano avaliar politica de mockups locais em `data/source_art` |
| 2026-06-16 | `promotion_candidate` | `creative_cohesion_pass_before_runtime_seed` | Specs tecnicamente corretas podem gerar um jogo generico se nao houver perseguicao visivel, risco significativo, identidade por setor, momento assinatura, audio reativo e replay hooks antes do first playable | `doc/creative_cohesion_pass.md`, `doc/creative_cohesion_audit.json`, contratos de pursuer/Lumen/setor/setpiece/audio/replay | medio | Humano avaliar como gate proporcional para `aaa_game` antes de runtime seed |
| 2026-06-27 | `promotion_candidate` | `scene_contract_compiler_cutscene_contract_projection` | Contratos de cutscene podem existir em `doc/contracts/` e ainda assim o gate compilado continuar `SC100`, porque o compilador nao injeta `cutscene_contract` em `doc/scene-contracts.json` | `doc/contracts/opening_cinematic_storyboard_contract.json`, `doc/contracts/race_start_handoff_cinematic_storyboard_contract.json`, `out/logs/scene_contract_overlay_probe.json`, `out/logs/scene_contract_report.json` | medio | Humano autorizar mudanca em `tools/sgdk_wrapper/scene_contract_compiler.ps1` com teste CI para abertura/handoff |

## Criterios minimos

- Deve ter sido usado com sucesso em contexto real do projeto.
- Deve reduzir erro recorrente, custo de producao ou ambiguidade.
- Deve ter limites declarados.
- Deve exigir revisao humana antes de qualquer mudanca canonica.

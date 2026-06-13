# Skill Promotion Candidates

Este arquivo lista candidatos locais que talvez merecam virar skill, workflow, regra, script ou `lib_case` canonico no futuro.

Nenhum item aqui esta promovido.

| Data | Classificacao | Candidato | Problema resolvido | Evidencia minima | Risco | Proxima revisao humana |
|---|---|---|---|---|---|---|
| 2026-06-05 | `promotion_candidate` | preflight_host_files_count_array_wrap | Evita falha de preflight quando Get-ProjectCodeFiles retorna escalar (sem `.Count`). | out/logs/build_output.log + build OK em projeto novo | baixo | revisar aplicacao em outros projetos + adicionar teste |
| 2026-06-05 | `promotion_candidate` | png_plte_trim_to_16 | Remove PLTE 256 entradas em PNG indexado gerado por Pillow, garantindo PLTE <=16 (pixel-strict). | validate_hibrido_pngs_v001.py + build sem warn de PLTE | medio | revisar compatibilidade com tRNS e outros exporters |
| 2026-06-07 | `promotion_candidate` | visual_input_gatekeeper_anatomy_acting_48x64 | technical stability masked visual failure; bloqueia source/model sheet com membro extra, face estatica e baixa fidelidade 48x64 antes de converter para PNG final. | out/logs/hibrido_v002_visual_rejection_report.json + out/logs/hibrido_v002_input_gatekeeper_report.json | alto | promover para visual-excellence/art-translation somente com teste de fixture e aprovacao humana |
| 2026-06-07 | `promotion_candidate` | no_direct_downscale_for_critical_48x64_sprites | Impede downscale/quantizacao global de concept high-res como rota final para lutador 48x64; exige redraw em clusters e PAL2/PAL3 por material. | out/logs/hibrido_v002_runtime_fidelity_report.json + doc/03_art/02_visual_feedback_bank.md | alto | criar teste visual comparativo original/basic/elite/rom |
| 2026-06-07 | `promotion_candidate` | canonical_model_sheet_scale_turnaround_marker_gate | Exige escala coerente, pose de costas e continuidade de marcadores de figurino antes de aprovar model sheet canonico. | out/logs/hibrido_v003_model_sheet_review_report.json + data/source_art/hibrido_fighter_v005/source_concept.png | medio | promover somente apos validar em outro personagem/sheet |
| 2026-06-07 | `promotion_candidate` | asymmetric_accessory_material_lock_palette_map_gate | Exige contrato de adereco/material por membro assimetrico e mapa de paleta/material antes de spritesheet. | out/logs/hibrido_v005_model_sheet_review_report.json + doc/contracts/hibrido_fighter_v006_palette_map.json | medio | validar com personagem assimetrico adicional |
| 2026-06-08 | `promotion_candidate` | special_limb_endpoint_cluster_shading_palette_gate | Exige extremidade legivel em membro especial, shading por clusters e plano de 1 paleta 16 cores antes de spritesheet. | out/logs/hibrido_v006_model_sheet_review_report.json + data/source_art/hibrido_fighter_v006/source_concept.png | alto | validar com source v007 e fixture 48x64 |
| 2026-06-13 | `promotion_candidate` | model_sheet_to_sprite_fidelity_gate | Impede que sprite sheet tecnicamente valido mas blocado/generico seja promovido quando perde DNA visual do model sheet aprovado. | out/logs/hibrido_v009_model_sheet_to_sprite_fidelity_report.json + data/source_art/hibrido_fighter_v008/source_concept.png + data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png | alto | promover para skills existentes e schema; criar fixture automatica quando houver comparador visual |
| [DATA] | `promotion_candidate` | [nome curto] | [problema] | [build/log/screenshot/hash] | [baixo/medio/alto] | [criterio] |

## Criterios minimos

- Deve ter sido usado com sucesso em contexto real do projeto.
- Deve reduzir erro recorrente, custo de producao ou ambiguidade.
- Deve ter limites declarados.
- Deve exigir revisao humana antes de qualquer mudanca canonica.

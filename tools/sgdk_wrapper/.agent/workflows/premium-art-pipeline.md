# Workflow: Premium Art Pipeline

Pipeline criativo e tecnico para arte final. Ele nao substitui o pipeline AAA de cena; endurece a parte de fonte, triagem e prova visual antes de qualquer claim `AAA`, `delivery` ou `ready_for_aaa`.

## Principio

Arte final nao nasce de procedural/debug, screenshot bonito ou reducao automatica. Ela nasce de fonte autoral persistida, direcao visual, traducao para VDP, comparacao em emulador e revisao perceptiva.

## Ordem canonica

| # | Etapa | Entrada minima | Saida minima | Gate |
|---|---|---|---|---|
| 1 | `source_art` | briefing, GDD/spec, direcao visual | fonte persistida em `data/source_art/` com hash, licenca, autoria e lineage | sem fonte persistida, status maximo `planning` ou `debug_lab` |
| 2 | model sheet autoral | personagem, faccao, boss ou objeto critico | `authorial_model_sheet` ou `authorial_stage_concept` | clone risk declarado |
| 3 | sprite sheet / layer sheet | model sheet e escala 320x224 | sheet com silhueta legivel, pivot, estados, paleta planejada e `model_sheet_to_sprite_fidelity_report` quando houver personagem | index 0 transparente, contratos de animacao e fidelidade ao model sheet quando aplicavel |
| 4 | contact sheet | todos candidatos e variantes | contact sheet de triagem com aprovacao/rework por asset | candidato sem triagem nao entra em `res/` final |
| 5 | traducao VDP | source aprovado, budget preliminar | PNG indexed SGDK-safe, `.res`, `source_to_rom_asset_map` | sem procedural/debug como final |
| 6 | comparacao BlastEm | ROM vigente, screenshot, baseline | screenshot dedicada, diff/baseline, observacao de leitura nativa | captura de baixa informacao reprova |
| 7 | revisao de direcao visual | evidencia do emulador, benchmark honesto | parecer de direcao visual e `perceptual_quality` | `perceptual_quality=measured` para AAA |
| 8 | fechamento | validation, res graph, freshness, closeout | `capture_status=complete`, docs e memoria atualizados | `ready_for_aaa` so sem blockers |

## Regras bloqueantes

- `source_art` obrigatorio para personagem, boss, cenario, HUD heroico, title ou asset de identidade.
- Model sheet autoral obrigatorio para personagem principal, faccao visual e boss.
- Contact sheet obrigatorio como triagem antes de promover asset para final.
- Sprite sheet final precisa ter silhueta legivel em 320x224 nativo e estados nomeados.
- Sprite sheet derivado de model sheet precisa passar `model_sheet_to_sprite_fidelity_report`; arte blocada/generica com `technical_pass=true` continua reprovada.
- Procedural/debug, texto cru, placeholder, benchmark-derived ou `local_author_pixel_rasterization` nao podem ser fonte final.
- Comparacao visual deve acontecer em BlastEm para claims de entrega.
- `capture_status=complete` e obrigatorio para entrega final.
- `perceptual_quality=measured` e obrigatorio para claims AAA.

## Artefatos esperados

- `premium_source_manifest`
- `authorial_model_sheet` ou `authorial_stage_concept`
- `sprite_sheet_contract`
- `model_sheet_to_sprite_fidelity_report`
- `contact_sheet_review`
- `source_to_rom_asset_map`
- `visual_delivery_gate_report`
- `perceptual_quality_report`
- `blastem_visual_comparison`

## Handoff

- Para budget: entregar dimensoes, paletas, tiles estimados, estados simultaneos e active animation window.
- Para runtime: entregar owner de planos, paletas, sprites, animacao e teardown.
- Para QA: entregar ROM hash, screenshot, baseline, VDP dump quando aplicavel e lista de blockers.

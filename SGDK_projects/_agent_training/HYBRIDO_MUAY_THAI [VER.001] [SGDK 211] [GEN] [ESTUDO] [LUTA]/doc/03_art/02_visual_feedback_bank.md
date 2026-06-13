# Visual Feedback Bank - Hibrido Muay Thai

## 2026-06-07 - Reprovacao do v002 por topologia, acting e fidelidade 48x64

- Falha observada: O concept/model sheet v002 foi aceito por estetica geral, mas a Pose 3 apresenta anomalia de membros: braco duplicado/sobreposto em posicao de guarda, criando leitura de tres bracos.
- Falha observada: O rosto permanece frio e igual em idle, joelho e chute, sem tensao de mandibula, dentes cerrados, kiai ou olhos estreitos no impacto.
- Falha observada: A traducao runtime 48x64 priorizou conformidade de PNG e perdeu olhos, braco de lava, calcao e contraste quente de material.
- Technical diagnosis: O pipeline confundiu sintaxe tecnica com semantica visual. `art_diagnostic`, build SGDK e screenshot BlastEm provaram execucao, mas nao provaram anatomia, acting ou fidelidade perceptiva.
- Preventive heuristic: Todo source/model sheet de personagem passa por `input_gatekeeper` antes de qualquer conversao. O gate conta membros, valida conexoes em ombro/quadril, audita extremidades e exige acting facial por estado.
- Preventive heuristic: Todo concept high-res precisa de `semantic_parse_report` e reconstrucao em clusters 48x64. Downscale direto ou quantizacao global nao sao rota de final art.
- Evidence: out/logs/hibrido_v002_visual_rejection_report.json, out/logs/hibrido_v002_input_gatekeeper_report.json, data/source_art/hibrido_fighter_v002/source_concept.png, data/processed/model_sheets/hibrido_fighter_model_sheet_48x64_v002.png

## Regras incorporadas

- Um asset tecnicamente valido pode ser visualmente reprovado.
- Anatomia basica e topologia de membros sao gates antes da paleta.
- Acting facial e parte do movimento, nao detalhe opcional.
- PAL2/PAL3 sao contratos semanticos de material, nao apenas slots.
- Runtime BlastEm deve ser julgado por leitura perceptiva: olhos, lava, calcao, bandagens, pose e direcao do olhar.

## 2026-06-07 - Rework v003 por escala, costas e marcador de figurino

- Falha observada: v003 avancou em anatomia/acting, mas o primeiro personagem ficou maior que os demais, criando risco de escala instavel para pivots/bbox no spritesheet.
- Falha observada: faltou pose de costas, insuficiente para uma fonte canonica de longo prazo.
- Falha observada: a faixa vermelha no biceps do braco nao-lava aparece em algumas poses e falta na pose frontal, quebrando continuidade de figurino.
- Technical diagnosis: O gate v003 corrigiu topologia grossa, mas ainda nao tinha `model_sheet_scale_lock`, `turnaround_minimum` e `costume_marker_continuity`.
- Preventive heuristic: Antes de aprovar source canonico, medir/checar proporcao de cabeca/torso/ombros/quadris por pose, exigir back view e listar marcadores obrigatorios que nunca podem desaparecer sem oclusao justificada.
- Evidence: out/logs/hibrido_v003_model_sheet_review_report.json, data/source_art/hibrido_fighter_v003/source_concept.png

## 2026-06-07 - Rework v005 por consistencia da mao lava e falta de mapa de cores

- Falha observada: Em v005, a mao de rocha/lava muda tratamento entre poses; na ultima pose le como se tivesse faixa/luva que nao aparece nas primeiras.
- Falha observada: A fonte ainda nao tinha paleta/mapa de cores, fragilizando a producao futura.
- Technical diagnosis: O gate de marcador de figurino ainda era generico demais; membros assimetricos precisam de contrato por lado/material.
- Preventive heuristic: Antes de aprovar model sheet, declarar accessory lock por membro: lava arm/hand sempre rocha exposta sem wrap/glove; human hand e pes com faixas; red armband no braco nao-lava. Exigir palette/material map junto do source.
- Evidence: out/logs/hibrido_v005_model_sheet_review_report.json, doc/contracts/hibrido_fighter_v006_palette_map.json, data/processed/reports/hibrido_v006_palette_map.png

## 2026-06-08 - Reprovacao v006 por mao lava ausente e excesso de ruido

- Falha observada: v006 introduziu nova falha anatomica: a mao/punho do braco de rocha/lava ficou ausente ou ilegivel.
- Falha observada: a arte ainda depende de microdetalhe/spray de pixels, arriscando tile-noise e baixa legibilidade em 48x64.
- Technical diagnosis: O gate de consistencia de acessorio corrigiu wrap/glove, mas nao exigiu explicitamente extremidade legivel no membro especial. A direcao visual tambem ainda permitia textura fina demais para SGDK/VDP.
- Preventive heuristic: Membro assimetrico deve passar `limb_endpoint_readability`: ombro, cotovelo, punho/mao e silhueta da extremidade precisam ser legiveis. Shading deve usar clusters de 2-3 tons; spray/noise reprovam.
- Preventive heuristic: Fonte para personagem deve nascer com plano de 1 paleta de 16 cores para o corpo; FX separado so quando estiver destacado em PAL3/strip proprio.
- Evidence: out/logs/hibrido_v006_model_sheet_review_report.json, data/source_art/hibrido_fighter_v006/source_concept.png

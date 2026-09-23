# Failure patterns (local)

- Misturar fogo/glow e corpo no mesmo sprite strip e depois tentar “separar por código” (quebra paleta por tile).
- Gerar cores fora do grid 9-bits ou PNG não-indexado (rejeição no gate pixel-strict).
- Mudar bbox/pivô durante produção (inconsistência de metasprite e colisão).

## technical stability masked visual failure

- Data: 2026-06-07
- Falha observada: v002 foi tratado como progressao porque PNG, PLTE, build SGDK e BlastEm funcionaram, mas a arte falhou em anatomia, acting facial e fidelidade perceptiva 48x64.
- Causa provavel: O pipeline confundiu sintaxe tecnica com semantica visual e nao bloqueou a fonte no input gatekeeper antes da traducao.
- Mitigacao: Separar gates: `technical_pass` nunca implica `visual_pass`. Qualquer personagem critico exige input gatekeeper anatomico, acting facial por estado e runtime fidelity check no BlastEm.
- Evidencia: out/logs/hibrido_v002_visual_rejection_report.json, out/logs/hibrido_v002_runtime_fidelity_report.json
- Limite de uso: Build e screenshot continuam validos para provar execucao, mas nao podem aprovar arte final.

## model sheet accepted without anatomy gate

- Data: 2026-06-07
- Falha observada: Pose 3 do source/model sheet foi aceita apesar de leitura de tres bracos por duplicacao/sobreposicao de braco com faixa.
- Causa provavel: A avaliacao focou textura, volume e estilo geral antes de contar membros e conferir articulacoes.
- Mitigacao: Antes de paleta ou conversao, contar 2 bracos, 2 pernas, 1 cabeca e 1 tronco por pose; rejeitar membro duplicado no mesmo ombro/quadril.
- Evidencia: out/logs/hibrido_v002_input_gatekeeper_report.json, data/source_art/hibrido_fighter_v002/source_concept.png
- Limite de uso: Designs nao-humanos precisam declarar excecao anatomica explicita antes do gate.

## static face breaks combat acting

- Data: 2026-06-07
- Falha observada: Idle, knee e teep/kick mantiveram a mesma expressao fria, quebrando acting de esforco fisico.
- Causa provavel: A geracao/curadoria tratou rosto como detalhe estetico e nao como parte do estado de animacao.
- Mitigacao: Cada estado animado deve declarar expressao facial esperada e direcao do olhar; golpes precisam de maxilar tenso, dentes ou kiai e olhos estreitos.
- Evidencia: out/logs/hibrido_v002_input_gatekeeper_report.json, doc/contracts/animation_direction_contract_v002.json
- Limite de uso: Em sprites muito pequenos, acting pode ser minimo, mas precisa ser intencional e verificavel em pixels de olhos/boca/cabeca.

## direct high resolution translation destroyed 48x64 readability

- Data: 2026-06-07
- Falha observada: A traducao runtime perdeu olhos, braco de lava, calcao preto/dourado e contraste quente, embora mantivesse formato SGDK valido.
- Causa provavel: A reducao/traducao priorizou textura/quantizacao e nao reconstrucao manual de clusters nativos 48x64.
- Mitigacao: Proibir downscale suave e quantizacao global como rota final; reconstruir lineart 1px, silhueta e materiais com PAL2/PAL3 mapeados manualmente.
- Evidencia: out/logs/hibrido_v002_runtime_fidelity_report.json, out/evidence/blastem/screenshot.png
- Limite de uso: Downscale pode servir como thumbnail de referencia, nunca como sprite final.

## canonical model sheet needs scale lock turnaround and marker continuity

- Data: 2026-06-07
- Falha observada: v003 melhorou anatomia/acting, mas a pose frontal ficou maior, nao havia pose de costas e a faixa vermelha do biceps sumiu na primeira pose.
- Causa provavel: O gate focou contagem de membros e expressao, mas ainda nao exigia escala travada, turnaround minimo e continuidade de marcadores de figurino.
- Mitigacao: Model sheet canonico deve ter proporcao base consistente entre poses, pose de costas quando o personagem tiver futuro longo, e checklist de marcadores obrigatorios por pose.
- Evidencia: out/logs/hibrido_v003_model_sheet_review_report.json, data/source_art/hibrido_fighter_v005/source_concept.png
- Limite de uso: Acoes podem alterar bbox por mecanica, mas nao podem alterar escala estrutural do personagem.

## asymmetric character accessories need per limb material lock and palette map

- Data: 2026-06-07
- Falha observada: v005 manteve avanco geral, mas a mao de rocha/lava ganhou leitura de faixa/luva na ultima pose, diferente das poses anteriores, e faltava mapa de cores.
- Causa provavel: O model sheet nao tinha contrato explicito de aderecos por membro nem paleta/material map para estabilizar producao futura.
- Mitigacao: Personagem assimetrico precisa declarar por membro o que pode ou nao aparecer. No Hibrido, lava hand e sempre rocha exposta sem faixa/luva; human hand e pes usam faixas; mapa PAL2/PAL3 precisa existir antes do redraw.
- Evidencia: out/logs/hibrido_v005_model_sheet_review_report.json, doc/contracts/hibrido_fighter_v006_palette_map.json, data/source_art/hibrido_fighter_v006/source_concept.png
- Limite de uso: Oclusao por pose pode esconder um acessorio, mas nao pode trocar o material do membro.

## special limb endpoint readability and cluster shading are mandatory

- Data: 2026-06-08
- Falha observada: v006 corrigiu parte da consistencia de acessorios, mas introduziu mao/punho ausente ou ilegivel no braco lava e manteve ruido de detalhe inadequado para Mega Drive.
- Causa provavel: O gate verificou wrap/glove, mas nao exigiu leitura da extremidade do membro especial nem bloqueou textura tipo spray.
- Mitigacao: Todo membro especial precisa de ombro/cotovelo/punho/mao legiveis. Sombreamento deve usar clusters limpos de 2-3 tons; microdetalhe que vira tile-noise reprova. Personagem deve ser planejado com uma paleta de 16 cores para corpo.
- Evidencia: out/logs/hibrido_v006_model_sheet_review_report.json, data/source_art/hibrido_fighter_v006/source_concept.png
- Limite de uso: Ruido fino pode existir em concept exploratorio, mas nao em source candidato a spritesheet.

## model sheet to sprite sheet fidelity gate is mandatory

- Data: 2026-06-13
- Falha observada: v009 produziu sprite sheet 48x64 tecnicamente organizado, mas com arte blocada e generica, perdendo a anatomia, rosto/olhos, braco de lava, shorts preto/dourado, bandagens e acting do model sheet v008.
- Causa provavel: O pipeline tratou `native redraw` e `sprite_strip_integrity` como garantia visual. Eles provam celula e integridade tecnica, mas nao medem heranca do design aprovado.
- Mitigacao: Antes de promocao para `res/`, baseline visual ou claim de qualidade, emitir `model_sheet_to_sprite_fidelity_report` comparando model sheet, sprite sheet e contact sheet. Cada traço `must_preserve` precisa passar ou o asset volta para lineart/blocking por estado.
- Evidencia: out/logs/hibrido_v009_model_sheet_to_sprite_fidelity_report.json, data/source_art/hibrido_fighter_v008/source_concept.png, data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png
- Limite de uso: Aplica-se a personagem, lutador, boss, inimigo grande e NPC expressivo derivados de model sheet. Nao substitui pixel compliance, strip integrity, motion preview nem BlastEm; complementa esses gates.

## art and game design supervision is mandatory

- Data: 2026-06-13
- Falha observada: v009 foi produzida como sprite sheet isolado, sem provar supervisao conjunta de art director e game design antes da geracao/conversao.
- Falha observada: o model sheet v008 aceito ainda tinha drift interno de coesao, como cabelo diferente entre a primeira pose e as demais, mas isso nao foi transformado em contrato antes da folha final.
- Causa provavel: O pipeline tinha gates para formato, paleta, pivot, integridade e fidelidade posterior, mas nao exigia um contrato pre-producao com GDD/spec, camera, interacoes, papel de gameplay, marcadores de identidade e movimento/carismo.
- Mitigacao: Model sheet, background, sprite art, key pose, animation strip, sprite sheet final, FX sheet, HUD heroico e title/menu criticos exigem `art_gameplay_direction_gate` antes de prompt, redraw, conversao ou promocao.
- Evidencia: doc/contracts/art_gameplay_direction_gate_v009.json, doc/contracts/human_validation_record_v009.md, data/source_art/hibrido_fighter_v008/source_concept.png, data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png
- Limite de uso: Aplica-se a asset critico visual. Nao substitui `model_sheet_to_sprite_fidelity_report`, pixel compliance, preview de animacao, budget VDP ou BlastEm; ele impede comecar a producao sem direcao.

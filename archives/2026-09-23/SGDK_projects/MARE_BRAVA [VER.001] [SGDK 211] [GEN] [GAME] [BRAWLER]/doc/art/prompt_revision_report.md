# Prompt Revision Report — MARE_BRAVA source candidates

Data: 2026-07-04

## Escopo

Este report registra a revisao curatorial do prompt pack para que o agente de
imagem gere materia-prima premium organizada, nao level pronto, sprite final ou
asset para `res/`.

## Mudancas principais

- Criado `doc/art/authorial_line_style_contract.json`: o estilo deixou de ser
  apenas um rotulo de referencia e passou a declarar assinatura de linha,
  gramatica de rosto/maos, hooks de silhueta, assimetria, materiais e blockers
  contra arte competente porem intercambiavel.
- Criado `doc/art/prompt_pack/06_image_agent_master_prompt.md` como handoff
  autocontido para o agente de imagem.
- `00_leia_primeiro.md` agora exige status `source_candidate`, relatorio de
  prompts, relatorio de aceite, registro de modelo/seed/config e proibe status
  de promocao.
- `01_taina_model_sheet.md` foi ajustado para identidade compactavel e nao
  sprite final 48x48; adiciona silhouette board.
- `02_cria_estivador_model_sheets.md` separa identidade, telegraph e hit/down
  em assets distintos para CRIA e ESTIVADOR.
- `03_cais_world_concept.md` reforca `dock_scene_kit` modular e adiciona
  `dock_pickups_small_props`.
- `04_logo_mare_brava.md` adiciona teste monocromatico/miniatura e trava texto
  exato `MARE BRAVA`.
- `05_hud_fx_studies.md` separa HUD, chip damage, digitos, retrato e FX em
  assets pequenos e auditaveis.

## Motivo da revisao

O pacote anterior ja rejeitava panorama-first, mas ainda deixava alguns outputs
agrupados demais. A revisao transforma cada necessidade em asset_id proprio,
com pasta propria, criterio de aceite proprio e sem caminho direto para `res/`.

## Status final

`documentado`: prompts corrigidos e novo lote autoral gerado como
`source_candidate`, registrado em
`data/source_art/concept/authorial_style_validation_2026_07_04/`.
O contact sheet para ratificacao e
`data/processed/contact_sheets/authorial_style_validation_contact_sheet_v01.png`.
Uma geracao do kit do cais foi rejeitada por inserir rotulos; a regeneracao sem
texto foi preservada como candidata. Nenhum asset ficou
`ready_for_conversion`, `ready_for_res_promotion`, `ready_for_aaa`,
`sprite_final`, `tilemap_final` ou `production_tilemap_source`.

## Atualização 2026-07-09 — TAÍNA native callable turnaround

O roteamento foi retomado pela capacidade nativa de geração de imagem da sessão,
conforme `doc/art/prompt_pack/06_image_agent_master_prompt.md` e
`out/logs/generation_channel_decision.json`.

Foram geradas 4 variações para `taina_identity_turnaround` usando
`native_chat_image_generation_callable`; 2 foram preservadas como
`source_candidate` e 2 foram arquivadas em `descartes/` por drift de anatomia
alta/ilustrativa. O registro completo está em
`doc/art/characters/taina/taina_identity_turnaround_native_callable_review_v01.json`
e o prompt final em
`doc/art/generated_prompts/taina_identity_turnaround/taina_identity_turnaround_native_callable_v01.md`.

Resultado: a miniatura 320x224/16 cores preserva cabelo, bandagens, faixa,
punhos/pés e guarda alta melhor que os probes procedurais anteriores, mas ainda
é concept source. Nada foi promovido para `res/`, build, ROM ou gate AAA.

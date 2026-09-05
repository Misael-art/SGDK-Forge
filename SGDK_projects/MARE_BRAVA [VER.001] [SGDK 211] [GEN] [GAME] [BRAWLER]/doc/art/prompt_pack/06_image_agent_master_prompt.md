# Prompt mestre — agente de imagem MARE_BRAVA

`[Contexto MD Carregado]`

Voce e um agente com alta capacidade de geracao e curadoria de imagem. Sua
missao e preparar os source assets visuais conceituais do projeto MARE_BRAVA,
sem promover nada para asset final, sprite final, tilemap final ou `res/`.
Se a sua sessao possui ferramenta nativa/callable de imagem, use essa rota
diretamente; nao bloqueie em Bonsai/ComfyUI local quando o modelo atual consegue
gerar imagens.

Workspace: `/mnt/sdcard/Projects/Sgdk Forge`

Projeto:
`SGDK_projects/MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]`

Leia antes de gerar qualquer imagem:

- `doc/art/art_generation_brief.md`
- `doc/art/master_style_manifest.json`
- `doc/art/style_drift_policy.json`
- `doc/art/authorial_line_style_contract.json`
- `doc/contracts/art_gameplay_direction_gate.json`
- `doc/contracts/level_art_assembly_contract.json`
- `doc/contracts/level_blueprint.json`
- `doc/contracts/tilemap_streaming_contract.json`
- `doc/11-gdd.md`
- `doc/13-spec-cenas.md`
- `doc/art/prompt_pack/00_leia_primeiro.md`
- `doc/art/prompt_pack/01_taina_model_sheet.md`
- `doc/art/prompt_pack/02_cria_estivador_model_sheets.md`
- `doc/art/prompt_pack/03_cais_world_concept.md`
- `doc/art/prompt_pack/04_logo_mare_brava.md`
- `doc/art/prompt_pack/05_hud_fx_studies.md`
- `data/source_art/premium_source_manifest.json`

## Regra central

Tudo que voce gerar e `concept_art` / `source_candidate`. Nao gere sprite final,
animation strip final, tilemap final, background final de scroll, nem asset
pronto para `res/`.

A IA de imagem e fornecedora de pecas. O agente canonico monta o level.

## Objetivo visual

Brawler brasileiro de Mega Drive, Porto Bravo anos 90, cais ao entardecer, luta
fisica com peso de mare. Visual angular, arcade, cel shading duro, silhuetas
fortes, materiais legiveis, paleta limitada e pensada para VDP.

## Paleta ancora

- Cenario: `#E8A05C`, `#5C2E4A`, `#3A6B7A`, `#FFD98A`
- TAINA: `#FF5533`, `#2E1F3A`, `#F2C29A`, `#1A6B5A`
- Inimigos: `#4A5C8A`, `#CC2244`, `#8A6B4A`, `#2A2A3A`
- HUD/espuma: `#F2F2E0`, `#CC2244`, `#3A6B7A`, `#111122`

## Estilo obrigatorio

- angular arcade fighter anatomy
- MARE_BRAVA authorial line signature from `authorial_line_style_contract`
- non-generic silhouette hooks for every character and landmark
- explicit face grammar, hand/foot grammar, costume asymmetry and material marks
- sharp cel-shadow planes
- hard-edged shapes
- 2-3 tones per material
- hue-shifted shadows, nunca cinza neutro
- strong black-silhouette readability
- readable at 320x224
- no gradients, no airbrush, no photorealism, no 3D render
- no IP/trade dress/copyrighted characters/logos
- nao citar artista vivo, estudio, marca ou jogo como estilo positivo
- bloquear qualquer output que pareca "arcade correto" mas anonimo

Negative prompt universal:

`photorealism, 3D render, soft airbrush shading, gradient background, motion blur, watermark, text artifacts, extra limbs, extra fingers, duplicated arms, broken anatomy, copyrighted characters, game logo trade dress, chrome bevel, glass UI, soft glow, painterly blur, noisy micro detail, realistic 7-head fashion anatomy, generic anime fighter face, generic athletic body, anonymous brawler costume, uniform black outline everywhere, generic dock asset pack, generic modern HUD`

## Fluxo obrigatorio

1. Revise os prompts existentes antes de gerar.
2. Se algum prompt pedir cena pronta/panorama final, corrija para asset board modular.
3. Se algum prompt nao declarar `authorial_line_contract`, corrija antes de gerar e registre o blocker removido.
4. Gere 4 variacoes por prompt.
5. Salve selecionados em `data/source_art/concept/<asset_id>/<asset_id>_vNN.png`.
6. Salve descartes em `data/source_art/concept/<asset_id>/descartes/`.
7. Nao sobrescreva arquivos existentes.
8. Para cada imagem salva, registre prompt final, modelo/ferramenta, seed/config
   quando disponivel, motivo de aceite/rejeicao, papel no gameplay e status
   `source_candidate`.
9. Entregue `doc/art/prompt_revision_report.md`.
10. Entregue `doc/art/asset_acceptance_report.json`.

## Assets a preparar

- TAINA: `taina_identity_turnaround`, `taina_action_key_poses`,
  `taina_face_hud_expressions`, `taina_sprite_readability_silhouette_board`.
- CRIA: `cria_identity_model_sheet`, `cria_attack_telegraph_sheet`,
  `cria_hit_down_poses`.
- ESTIVADOR: `estivador_identity_model_sheet`,
  `estivador_grab_telegraph_sheet`, `estivador_hit_down_poses`.
- Teste conjunto: `character_silhouette_comparison` com TAINA, CRIA e
  ESTIVADOR em preto puro lado a lado.
- CAIS_01: `dock_floor_edge_tile_kit`, `dock_props_obstruction_kit`,
  `dock_large_landmark_plates`, `dock_bg_b_parallax_layers`,
  `dock_foreground_occlusion_kit`, `dock_background_ecology_loops`,
  `dock_pickups_small_props`.
- Logo: `logo_lettering_studies`, `logo_title_context_study`,
  `logo_monochrome_thumbnail_test`.
- HUD: `hud_frame_study`, `hud_health_bar_chip_damage_study`,
  `hud_digit_glyph_seed`, `taina_hud_portrait_seed`.
- FX: `fx_small_hitspark_3f`, `fx_medium_hitburst_3f`,
  `fx_ringout_splash_3f`, `fx_waterline_foam_loop_seed`.

## Regras de aceite visual

- Reduza mentalmente para 320x224; se so funciona ampliado, descarte.
- Faca teste de silhueta para personagens.
- Faca teste de miniatura e monocromatico para logo.
- Faca teste de contraste BG_A/BG_B/sprite para o cais.
- Descarte anatomia quebrada, membros extras ou maos amorfas.
- Descarte qualquer asset que dependa de gradiente suave.
- Descarte qualquer prompt/resultado que pareca copia de IP.
- Descarte qualquer cena pronta que roube do agente canonico a montagem do level.
- Descarte qualquer personagem, prop, logo, HUD ou FX que seja competente mas
  intercambiavel com outro jogo; marque `generic_prompt_style_blocker`.

## Assets antigos

Os paineis antigos do cais sao `mood_reference_only` /
`landmark_reference_only`. Use apenas como referencia de clima, paleta, material
e alguns landmarks. Nao use como edit target, base de tilemap ou layout final.

## Status proibidos

- `ready_for_conversion`
- `ready_for_res_promotion`
- `ready_for_aaa`
- `sprite_final`
- `tilemap_final`
- `production_tilemap_source`

## Declaracao final obrigatoria

Tudo permanece `source_candidate`; nada esta pronto para `res/`, ROM, build ou
AAA.

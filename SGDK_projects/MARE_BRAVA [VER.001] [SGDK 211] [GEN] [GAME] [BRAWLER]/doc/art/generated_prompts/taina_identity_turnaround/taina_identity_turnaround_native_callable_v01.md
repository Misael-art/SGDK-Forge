# TAÍNA identity turnaround — native callable generation v01

Data: 2026-07-09

Canal usado: `codex_builtin_image_generation` / `native_chat_image_generation_callable`.

Escopo: `concept_art` / `source_candidate`. Esta geração não produz sprite final,
strip de animação, tilemap, asset de `res/`, nem estado `ready_for_conversion`.

## Contexto curatorial consumido

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
- `doc/art/prompt_pack/06_image_agent_master_prompt.md`
- `data/source_art/premium_source_manifest.json`

## Prompt base efetivamente usado

```text
Use case: stylized-concept
Asset type: game character compact-proportion concept source candidate for MARE_BRAVA, not final pixel art, not a sprite sheet, not animation frames
Primary request: Create one clean full-body turnaround model sheet for TAÍNA using deliberately compact 3.5-head arcade sprite proportions. She must look like a hand-authored 16-bit brawler heroine compressed for a 48px Mega Drive sprite, not a tall fashion illustration.

Subject: TAÍNA, original Brazilian female muay thai fighter, brown-skinned, about 28, functional athletic build. Compact stocky arcade anatomy: head, fists, knees and feet slightly enlarged for tiny-sprite readability; shorter torso; wide stable fighting stance; readable silhouette at 48px. Front and 3/4 views show relaxed high diagonal muay thai guard. Worn burnt-orange sports top, dark loose cropped training pants, asymmetric waist sash hanging to one side like a graphic tail, pale hand wraps and shin wraps as big block shapes, short tied curly hair mass. No glamour pose.

Required authorial hooks: high diagonal guard, short irregular curly hair mass, strong brow and wedge nose, compact jaw, large wrapped fists, readable wrapped shins, asymmetric sash/green cloth tail, dark loose pants with large wedge folds. These hooks must read in pure black silhouette.

Authorial line contract: variable dark purple/navy contour, not uniform black; sparse angular internal cuts; hard triangular cel-shadow planes; 2-3 tones per material; hue-shifted shadows; no neutral gray. Line economy suitable for later pixel cluster translation.

Composition/framing: one landscape sheet with four evenly spaced full-body views: front, 3/4, side, back. Full body visible, neutral flat light-gray background, no labels, no typography, no UI, no scene.

Style/medium: hand-drawn 16-bit arcade character concept, angular arcade fighter anatomy, hard cel shading, vibrant limited palette, readable at 320x224 and at tiny sprite scale.

Color palette anchors: burnt orange #FF5533, deep cool dark #2E1F3A, warm brown skin #F2C29A, muted green accent #1A6B5A, pale wraps off-white. Use limited color logic.

Constraints: original character only; no text; no labels; no logos; no watermark; no photorealism; no 3D render; no soft airbrush; no gradients; no painterly blur; no realistic 6-head or 7-head anatomy; no long fashion legs; no pin-up; no generic anime fighter face; no generic gym outfit; no broken hands; no extra fingers; no extra limbs; no copyrighted character resemblance; no uniform black outline everywhere.
```

## Variações geradas e decisão

1. `discard_v01_tall_illustrative`: identidade forte, mas anatomia alta e
   ilustrativa demais para a compressão 48px.
2. `taina_identity_turnaround_v01`: candidata principal; melhor compromisso
   entre compactação, punhos/pés legíveis, cabelo, faixa e guarda.
3. `discard_v02_tall_illustrative`: boa linha, mas retorna a corpo alto e
   postura mais fashion/anime.
4. `taina_identity_turnaround_v02`: segunda candidata; leitura forte em
   miniatura, mas ainda exige compressão autoral antes de lineart nativa.

## Resultado honesto

O lote remove o desvio operacional de depender de geração local precária e
restabelece a rota nativa curada. A miniatura 320x224/16 cores preserva os hooks
principais da TAÍNA, mas ainda não resolve o blocker de pixel art: falta model
sheet nativo 3.5 heads, lineart 1px aprovada, key poses, strips, budget VDP e
evidência BlastEm de gameplay.

# Chase Visual Benchmark - Asset Promotion Report

Date: 2026-06-02
Status: `lab_not_delivery`

## Promoted Runtime Asset

- Symbol: `img_chase_compare_flat`
- Runtime path: `res/gfx/chase_compare_flat.png`
- Source lineage:
  - approved concept package: `rascunho\entrada_bruta\legacy_megadrive_dev\source_art\celestial_chase_v001`
  - processed preview: `rascunho\processado\legacy_megadrive_dev\processed\celestial_chase_v001\vdp_preview\scene_concept_basic_16color_320x224.png`
- PNG audit:
  - size: `320x224`
  - color type: indexed PNG
  - bit depth: `4`
  - PLTE entries: `16`
  - used palette indexes: `16`
  - measured unique 8x8 tiles before ResComp: `1110`

## Route Decision

- `scene_profile`: `aaa_layered` source intent, reduced to `compare_flat` lab proof
- `resource_loading_model`: `scene_local_preload`
- `asset_strategy`: `IMAGE`
- `builder_route`: manual promotion from processed preview; no final curated builder yet
- `fallback_plan`: use the flat proof only to verify source-to-ROM visual presence before building `elite_split_scene`

## Blocking Statuses Preserved

- `elite_split_scene_not_built`
- `sprite_animation_strips_missing`
- `source_to_rom_visual_match_not_measured`
- `budget_not_validated_in_emulator`
- `lab_not_delivery`

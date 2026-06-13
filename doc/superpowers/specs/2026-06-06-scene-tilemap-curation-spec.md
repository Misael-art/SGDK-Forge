# Canonical Scene/Tilemap Conversion Curation Spec

> Status: `approved_for_implementation`  
> Date: 2026-06-06  
> Scope: workspace canonical curation (`tools/sgdk_wrapper/`, `tools/sgdk_wrapper/.agent/`, `doc/`)

## Goal

Prevent any agent (future or current) from declaring a scene/tilemap conversion "approved" based only on PNG quantization or ResComp compiling. Approval requires auditable structure: tile slicing, dedup (including H/V/HV flip), tilemap flags preservation, per-tile sub-palette safety, budget semantics, and ROM evidence.

## Non-goals

- Do not auto-generate reports inside `validate_resources.ps1` (validator validates; tools generate).
- Do not promote any technique to `MESTRE_*` in this batch.
- Do not duplicate skills or create parallel skill trees.

## Definitions

### Critical scene (operational)

A scene/resource is **critical** if any of the following is true:

- Any `IMAGE` or `MAP` whose effective dimensions are `>= 320x224`.
- Any resource/scene with techniques declared in `doc/technique_usage_manifest.json` linked to: tilemap, visual conversion, palette, parallax, foreground/priority, dedup/HV flip, priority split, or scene portability.
- Any scene marked as delivery/AAA/closeout scope (by methodology/claims or closeout execution mode).

### Storage convention for generated reports

- Generated per-project reports MUST live under the active project root:
  - Primary: `out/logs/`
  - Snapshot for closeout: copy into `doc/changelog/assets/<asset_id>/v###/` (or equivalent per-project changelog structure).
- No report may contain an absolute path pointing outside the project/workspace scope (enforced as a blocker).
- Without schema-valid JSON, a report is treated as missing.

## Required reports (generated artifacts)

### 1) `scene_tilemap_conversion_report.json`

Purpose: provide the minimum auditable contract for scene slice / tilemap conversion, including flip-aware dedup summary, palette risk summary, and ROM strategy.

Required fields:

- `source_path`
- `source_sha256`
- `conversion_target`: `scene_slice | tilemap | background_layer | foreground_layer`
- `output_tileset_path`
- `output_tilemap_path`
- `output_palette_path`
- `tile_size_px` = `8`
- `total_tiles`
- `unique_tiles_exact`
- `unique_tiles_hflip`
- `unique_tiles_vflip`
- `unique_tiles_hvflip`
- `final_unique_tiles`
- `dedup_savings_tiles`
- `dedup_savings_percent`
- `palette_count`
- `per_tile_palette_conflicts`
- `priority_tile_count`
- `hflip_tile_count`
- `vflip_tile_count`
- `hvflip_tile_count`
- `estimated_vram_bytes`
- `estimated_map_bytes`
- `rom_resource_strategy`: `IMAGE | TILESET_MAP | BIN_CUSTOM | COMPARE_FLAT`
- `status`: `ok | needs_review | blocked`
- `blockers[]`
- `generated_at`
- `tool_name`
- `tool_version`

### 2) `tilemap_flag_report.json`

Purpose: prove that flip and priority bits are preserved in the exported tilemap, not merely estimated aesthetically.

Each entry MUST include:

- `tile_x`
- `tile_y`
- `tile_index`
- `palette_id`
- `priority`
- `hflip`
- `vflip`
- `source_tile_hash`
- `canonical_tile_hash`

### 3) `per_tile_palette_conflict_report.json`

Purpose: detect per-tile violations that break SGDK/VDP palette domain assumptions.

It MUST detect:

- a tile using more colors than one sub-palette allows;
- a tile using indices incompatible with the declared palette domain;
- material mixing that should be separated by layer/palette;
- index 0 / transparency contaminating visible pixels.

It MUST output:

- `conflicts_total`
- `conflicts[]` with enough detail to locate the tile(s) and the rule violated.

## Enforcement (validator)

### Policy

- Enforcement is a **closeout/delivery blocker**, not an exploration blocker:
  - In non-closeout mode: report as warnings (or non-fatal blockers, per existing closeout-only mechanism).
  - In closeout mode (`-CloseoutGate`): report as errors and block final status.

### Closeout/delivery blockers to add

- `scene_tilemap_conversion_report_missing` (critical scene without report)
- `scene_tilemap_conversion_report_invalid` (schema invalid)
- `scene_tilemap_conversion_report_stale` (optional if dependency invalidation is implemented)
- `tilemap_flag_report_missing` when `TILE_DEDUP_HVFLIP` is declared
- `tilemap_flag_report_invalid`
- `per_tile_palette_conflict_report_missing` for critical scene conversions
- `per_tile_palette_conflict_report_invalid`
- `per_tile_palette_conflicts_detected` when `conflicts_total > 0`
- `whole_image_unique_ratio_high_without_justification` when `rom_resource_strategy=IMAGE` for `>=320x224` with high unique ratio and no declared justification (compare-flat/benchmark strategy)

Also required (already present in the framework; harden where needed):

- `evidence_root_mismatch` when report paths reference outside project root
- `technique_manifest_empty_in_lab` when a visual lab uses tilemap/palette/conversion techniques but declares an empty manifest

## Skill updates (no duplication; minimum edits)

### `art-conversion-pipeline`

- Critical scene/tilemap conversion requires `scene_tilemap_conversion_report`.
- Distinguish "ResComp accepted" from "optimized conversion approved".
- Block promotion if dedup/HV flip is claimed without `tilemap_flag_report` and `scene_tilemap_conversion_report`.

### `art-translation-to-vdp`

- If target is `scene_slice`/`tilemap`: require `semantic_parse_report` before conversion.
- Require `basic` vs `elite` and the human comparison panel.
- Require structural review (tileset/palette) and dedup/flags reports when tilemap optimization exists.

### `multi-plane-composition`

- Require `layer_plan` before converting a scene.
- Require BG_A/BG_B/foreground roles declared.
- Block `IMAGE` whole-scene default when unique tiles explode without justification (`COMPARE_FLAT` or explicit benchmark strategy).

### `megadrive-vdp-budget-analyst`

- Consume `scene_tilemap_conversion_report` as required input for critical scenes.
- Separate ROM cost, VRAM resident, preload DMA, per-frame DMA; do not treat `.res` compression as VRAM reduction.
- Block `validado_budget` for critical scenes without tilemap reports.

### `visual-excellence-standards`

- Reinforce: tile-first cannot destroy visual soul.
- Visual approval for scene portability requires comparison: original/basic/elite/ROM (and evidence where applicable).

## Registry and human matrix policy (conservative)

- Keep statuses unchanged (no MESTRE):
  - `tile_dedup_hvflip_hashing`: `TEORICA_PRIORITARIA`
  - `advanced_tilemap_design`: `TEORICA_STANDARD`
  - `priority_split_foreground`: `TEORICA_STANDARD`
  - `palette_remastering_slot_audit`: `TEORICA_STANDARD`
- Add curation notes:
  - status only rises with fixture + ROM + BlastEm + budget + tilemap_flag_report + human approval.
  - dedup/HV flip must prove tilemap flags preservation.
  - whole-scene `IMAGE` is suspicious by default for `>=320x224`.
- Remove any non-canonical absolute external paths from registry entries.

## Fixture (canonical lab)

Create a controlled lab fixture under `SGDK_projects/_agent_laboratory/` that documents:

- rich scene input in `rascunho/` (hashed);
- conversion to tileset/tilemap;
- dedup/HV flip report;
- per-tile sub-palette conflict report;
- `resources.res` or SGDK export;
- ROM viewer;
- BlastEm screenshot;
- `visual_vdp_dump.bin` when possible;
- `res_graph_report`, `validation_report`;
- human comparison panel original/basic/elite/rom.

MUGEN/Showdown:

- Register as candidate fixture only; first audit `tools/mugen2sgdk`.
- If tool lacks CLI/testability, mark `legacy_gui_tool_without_cli`.
- Only create wrapper/substitute with explicit tool-first audit justification.

## Required tests

Tests MUST cover:

- PNG with duplicate tiles (exact).
- PNG with duplicates by H flip.
- PNG with duplicates by V flip.
- PNG with duplicates by HV flip.
- Tile with palette conflict.
- Full-screen `IMAGE` with high unique ratio blocked as whole-image risk.
- Path with brackets works under `-LiteralPath`.
- ASCII-safe output in CP1252.
- Technique `TILE_DEDUP_HVFLIP` declared without reports yields blocker.
- Report with `source_path` outside project yields blocker.
- `ready_for_aaa` remains false when structural/evidence reports are missing.

## Final validation checklist (must run)

- If registry altered: `tools/sgdk_wrapper/.agent/scripts/validate_technique_registry.py`
- If skills altered: `tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`
- If templates altered: `tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`
- Unit tests (Python) relevant to image-tools
- `validate_resources.ps1` on the lab fixture project
- `res_graph_audit.ps1` when `.res` exists


# Changelog - MUGEN SFF Showdown Study

## 2026-06-13 - Curadoria camera/paleta reprovada

- Classificado o root do estudo como `exercise` em `doc/project_context_manifest.json`.
- Atualizado `doc/00-project-brief.md` para refletir o escopo real: treino controlado de conversao MUGEN SFF/DEF, nao entrega AAA.
- Atualizado `doc/project_methodology_manifest.json` para declarar `project_context` entre as validacoes obrigatorias.
- Criado `doc/showdown_camera_palette_curation_2026-06-13.md` com a avaliacao formal.
- Decisao visual: `rework_required`.
- Principais blockers:
  - `flattened_mugen_parallax`: deltas BG0/BG1/BG2/BG3 foram achatados em um unico `BG_A`;
  - `fighting_stage_camera_contract_missing`: camera de laboratorio/autopan nao preserva zoffset, verticalfollow e foco de palco de luta;
  - `palette_vibrancy_lost`: `banded_palette_v1_world` gerou `187569` nearest-color remaps e reduziu o viewport de 76 para 26 cores uteis;
  - `visual_gate_too_narrow`: gate atual mede matte/magenta, mas nao mede composicao, vitalidade cromatica ou fidelidade perceptiva;
  - `nested_lab_art_not_detected`: `art_diagnostic.py` no root retorna `3_no_art` para um estudo com arte em `work/`, `analysis/`, `evidence/` e viewer aninhado.
- Validacoes da curadoria:
  - `validate_project_context`: passed, `context=exercise`, `blockers=0`;
  - `validate_project_methodology`: passed, `blockers=0`;
  - `validate_project_hygiene`: blocked, `blockers=3`;
  - `freshness_audit`: warning, `stale=2`, `missing_required=2`;
  - `validate_resources`: failed, `errors=8`, `warnings=6`, `checked=0`;
  - `audit_project_learning` via Python embutido: `lessons=13`, `candidates=9`, `canonical_promotion_performed=false`.
- Status permanece `controlled_training_area`, `lab_not_delivery=true`, `ready_for_aaa=false`, `validado_budget=false`.

## 2026-06-08 - Full-world camera streaming fixture

- Corrected the stage contract from 320x224 output to the full MUGEN camera world:
  - `boundleft=-224`, `boundright=224`, `boundhigh=-240`, `boundlow=0`;
  - reconstructed world `768x480` px, `96x60` tiles;
  - viewer viewport remains `320x224` px with camera scroll bounds `x=0..448`, `y=0..256`.
- Updated DEF parsing to carry camera bounds and `verticalfollow`, and expanded the visual gate to validate declared world dimensions.
- Rebuilt the pipeline so `work/reconstructed_layers/frame_0000.png` through `frame_0003.png` are full-world 768x480 frames; no downscale/crop is used for the source conversion.
- Generated viewport previews under `work/reconstructed_viewports/` for default/start and world corners.
- Re-exported SGDK bins as custom streaming resources:
  - `showdown_tiles_4bpp.bin`: 2253 global ROM tiles;
  - `showdown_maps_u16.bin`: 96x60 maps for 4 frames using custom map words;
  - `showdown_palettes_u16.bin`: four banded sub-palettes.
- Updated tile reports:
  - raw tiles `23040`;
  - unique global tiles `2253`;
  - dedup saving ratio `0.902214`;
  - H/V/HV flip matches `5/12/4`;
  - lossy tile merge disabled.
- Reworked the SGDK viewer from full-resident 40x28 loading to a streamed 42x30 camera window. The camera supports D-pad movement and delayed autopan across the full 768x480 world.
- Added a RAM staging buffer and batch tile upload to reduce visible tile-stream tearing during evidence capture.
- Disabled automatic frame animation in the viewer (`FRAME_ANIMATION_ENABLED=0`) after evidence showed large per-frame tile-cache reloads could tear the image. The four reconstructed frames remain in the export/report surface for later curation.
- Built final ROM `sgdk_viewer/showdown_viewer/out/rom.bin` with SHA256 `4b0ce91f5e370a8d6fd4e842a511c7f6c2e52a8f49ee4f2419696c972305fe2e`.
- Captured final BlastEm evidence:
  - screenshot `evidence/blastem_showdown_screenshot.png`;
  - SRAM `evidence/blastem_showdown_save.sram`;
  - session manifest `evidence/blastem_session_manifest.json`;
  - matte check `evidence/blastem_screenshot_visual_check.json` with `bad_ratio=0.0`.
- Gate state:
  - Python tests: 8 passed;
  - `res_graph_audit.ps1`: `warn`, code-loaded tile budget unmeasured;
  - viewer `freshness_audit.ps1`: `warning`, `stale=2`, `missing_required=2`;
  - root `freshness_audit.ps1`: `warning`, `stale=1`, `missing_required=2`;
  - `validate_resources.ps1`: failed with 1 error and 11 warnings, expected for lab because VDP tile streaming lacks dump/telemetry and canonical closeout schemas are not delivery-clean.
- Status remains `controlled_training_area`, `lab_not_delivery=true`, `ready_for_aaa=false`, `validado_budget=false`.

## 2026-06-07 - Root fixture consolidation

- Audited `tools/mugen2sgdk` before continuing local automation.
- Kept the study parser/exporter local because no reproducible CLI output was found for the existing packaged tool.
- Regenerated reconstruction/export reports with relative paths.
- Added measured reports for tilemap conversion, tilemap flags, palette violations and per-tile palette conflicts.
- Added root memory bank, technique manifest, learning ledger and viewer aggregate manifest.
- Updated SGDK viewer flow to boot directly into the Showdown viewer instead of the generic branding/template path.
- Built `sgdk_viewer/showdown_viewer/out/rom.bin` via direct SGDK 2.11 debug make after wrapper validation blocked the normal build path.
- Captured initial BlastEm evidence for ROM SHA256 `3fe934583099d632b2407a46dadc43571dbf246eb8634a5348dbcf6fe656a3e1`; this was later superseded by the anti-magenta rebuild below.
- Copied root evidence to `evidence/blastem_showdown_screenshot.png`, `evidence/blastem_showdown_save.sram` and `evidence/blastem_evidence.json`.
- Recorded the initial visual/budget limits before the reconstruction fix: Showdown was visible in BlastEm, but magenta matte/background remained, VDP dump was absent and `validado_budget=false`.
- Regenerated `tilemap_flag_report.json` in the canonical schema with 4480 measured entries.
- Final gate state for the initial consolidation pass was superseded by the later validation below.
- Status remains `controlled_training_area`, `lab_not_delivery=true`, `ready_for_aaa=false`.

## 2026-06-07 - Logical reconstruction anti-magenta fix

- Fixed the MUGEN reconstruction pipeline before SGDK export:
  - parses `start`, `delta`, `tile`, `zoffset` and camera start from `showdown.def`;
  - composes `[BG x]` sections in DEF order;
  - uses SFF sprite axes for x/y placement, capped to the 240 px MUGEN logical canvas on Y;
  - converts PCX palette index 0 to alpha for `mask=1`;
  - infers alpha for unmistakable magenta index 0 mattes in animation frames and records `mask_source=inferred_chroma_key_index0`.
- Added `mugen_sff/visual_gate.py` and wired it into reconstruction/export. `frame_0000.png` now fails the pipeline if matte/magenta/transparent pixels exceed 5%.
- Regenerated reconstructed frames; current `frame_0000.png` has `bad_ratio=0.0`.
- Reworked SGDK export to `banded_palette_v1` to prevent slot-0 holes after palette fitting. Palette status is `pass_with_degradation`, with 15623 nearest-color remaps.
- Updated viewer runtime to load 895 unique tiles and stopped overwriting `PAL3` with a debug text palette.
- Rebuilt and recaptured BlastEm evidence for ROM SHA256 `69cffe7b834699d0313c8896d849f69272d91d5400f52bfbf5132a1322a51556`.
- Final gate state after technique-manifest cleanup: `freshness_audit.ps1` warning (`stale=2`, `missing_required=2`) and `validate_resources.ps1` failed with 1 error / 8 warnings. The remaining hard error is `code_loaded_tiles_unmeasured`.
- Remaining status: stage appears without catastrophic magenta; palette banding/degradation remains a curation target; `validado_budget=false`, `ready_for_aaa=false`.

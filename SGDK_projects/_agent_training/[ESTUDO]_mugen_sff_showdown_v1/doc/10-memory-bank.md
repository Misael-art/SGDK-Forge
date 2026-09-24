# Memory Bank - MUGEN SFF Showdown Study

## Current Status

- Status: `controlled_training_area`
- Training mode: `train_agent`
- `lab_not_delivery=true`
- `ready_for_aaa=false`
- Root is the authority for the study; `sgdk_viewer/showdown_viewer/` is an embedded proof viewer, not an independent delivery project.
- Curadoria 2026-06-13: o resultado foi `rework_required` para composicao, camera e paleta.
- Recovery route A 2026-06-15: a ROM atual implementa `route_a_multi_plane` em runtime SGDK com `BG_B` distante, `BG_A` mid/floor, camera de foco duplo, super jump fixture, line scroll e culling de `BG_B` atras de tiles opacos de `BG_A`.
- Status atual: `route_a_runtime_reworked_emulator_seen_budget_dump_pending`. A cena foi vista no BlastEm com screenshot e SRAM, mas nao ha `visual_vdp_dump.bin`; portanto nao declarar `validado_budget`, `ready_for_aaa` ou asset autoral final.

## Operational Truth

- Fixture inputs live in `rascunho/inputs/` and are registered in `rascunho/inputs_manifest.json`.
- Existing workspace tool `tools/mugen2sgdk` was audited first. The packaged executable behaved as a legacy GUI/unknown noninteractive tool and did not expose a reproducible CLI contract during this pass.
- The local parser/exporter remains inside this study as a controlled training pipeline only. It is not promoted to canonical wrapper tooling.
- Latest generated conversion reports live in `analysis/`.
- Viewer runtime consumes generated binaries from `sgdk_viewer/showdown_viewer/res/data/showdown/`.

## Latest Conversion Snapshot

- Reconstructed frames: 4
- World size: 768x480 px, 96x60 tiles. This preserves the original MUGEN camera extent instead of downscaling the stage to 320x224.
- Viewer viewport: 320x224 px. Camera scroll bounds: x `0..448`, y `0..256`; default/MUGEN start scroll is `224,256`.
- Raw tiles across all frames/planes: 46080
- Global unique ROM tiles: 2870
- Runtime model: route A multi-plane streaming. `showdown_maps_u16.bin` stores, per frame, `BG_B` then `BG_A`; runtime streams a 41x29 tile window into a shared local VDP cache.
- Streaming cache estimate with BG_B occlusion culling: max active-window unique tiles `1174`; cache capacity `1190`; estimated tile VRAM `38080` bytes; tile data ends at `38592`, before first tilemap at `49152`.
- Max active-window unique tiles without BG_B culling: `1630`; max culled BG_B cells in a window: `753`.
- Dedup saving ratio: `0.937717`
- H/V/HV flip reuse measured: `184/140/68`
- Lossy tile merge: disabled (`0` merges). The fixture keeps exact global tiles for the streaming route.
- Visual reconstruction gate: `pass`, matte/magenta/transparent ratio `0.0` on all four 768x480 reconstructed frames.
- Palette status: `vivid_anchor_palette_repaired_export_pending_art_review`; manual contextual MD palettes replace the blind banded palette and separate sky/buildings, vegetation, water/reflections and rocks/floor. Current nearest-color remaps: `235880`.
- Latest palette metrics: source useful colors `76`, source saturation `0.3805`; export preview useful colors `44`, source/export mean RGB distance `26.4448`; BlastEm normalized crop source/blastem mean RGB distance `69.5612`. Visual board shows the BlastEm route follows the export preview, but this remains a controlled fixture, not final authored art.
- Runtime camera/depth status: dual-focus fixture camera is implemented; `BG_B` uses far delta `43/100,285/1000`, `BG_A` uses mid/floor bands `71/100,635/1000` and `1/1`, and both planes receive line-scroll offsets.
- Preliminary budget: `documented_not_validated_budget`, not `validado_budget`.
- Budget caveat: `analysis/showdown_vdp_contract_audit_v001.json` passes bin/CRAM/tile/map/VRAM-layout checks, but `visual_vdp_dump.bin` is absent; budget is documented and audited, not `validado_budget`.

## 2026-06-15 Route A Runtime Recovery Snapshot

- Route outcome: `route_a_multi_plane` implemented in the current ROM.
- Runtime changes: two SGDK planes (`BG_B` far, `BG_A` mid/floor), shared streaming cache, 41x29 window, BG_B occlusion culling under opaque BG_A cells, explicit VRAM layout (`BG_A=0xC000`, WINDOW `0xD000`, `BG_B=0xE000`, HScroll `0xF000`, SAT `0xF800`), and small batched tile uploads.
- Camera contract: default camera `x=224`, `y=256`; floor anchor screen Y `215`; virtual fighters start at world x `314`/`454`, floor y `471`; X follows midpoint; Y uses deadzone plus `verticalfollow=1/2` for super jump.
- Build: direct SGDK 2.11 debug make passed and generated `sgdk_viewer/showdown_viewer/out/rom.bin`.
- ROM SHA256: `7e4f6a2e2149ff19b9788ffd3034adb556d595e1163b6af8c575ff09533ece2a`.
- BlastEm evidence: `sgdk_viewer/showdown_viewer/out/evidence/blastem/screenshot.png`, `save.sram`, and `sgdk_viewer/showdown_viewer/out/logs/blastem_evidence.json`; readiness source `post_close_sram_heartbeat`; `visual_vdp_dump.bin` absent.
- Reports: `analysis/showdown_camera_report_v001.json`, `analysis/showdown_recovery_palette_measurement_v001.json`, `analysis/showdown_budget_report_v001.json`, `analysis/showdown_vdp_contract_audit_v001.json`, and `work/diagnostics/showdown_recovery_comparison_v001.png`.
- Pedagogical decision flow: `doc/showdown_recovery_ascii_decision_flow.md` maps V00..V05, human interventions H01..H03, decision syntax, route status and next-version syntax.
- Python tests: `22 passed`.
- Validation snapshot: `validate_project_context` ok; `validate_project_methodology` passed; `validate_project_hygiene` blocked with 3 blockers; final `freshness_audit` warning with `stale=0`, `missing_required=2`; `validate_resources -WorkDir` failed at study root with 8 errors/5 warnings and at viewer root with 1 error/10 warnings; `audit_project_learning -Mode Capture` recorded 13 lessons and 9 candidates with no canonical promotion.
- Closeout status: not `blocked_rework_required` for the visual route anymore, but still `route_a_runtime_reworked_emulator_seen_budget_dump_pending`; no `validado_budget` or AAA/final claim.

## 2026-06-08 Emulator Evidence Snapshot

- ROM: `sgdk_viewer/showdown_viewer/out/rom.bin`
- ROM SHA256: `4b0ce91f5e370a8d6fd4e842a511c7f6c2e52a8f49ee4f2419696c972305fe2e`
- Build path used for evidence: direct SGDK 2.11 debug make after the wrapper build path timed out/degraded in consultive validation. The normal wrapper gates were still run separately and remain recorded.
- BlastEm report: `evidence/blastem_evidence.json`
- Screenshot: `evidence/blastem_showdown_screenshot.png`
- SRAM heartbeat: `evidence/blastem_showdown_save.sram`
- Session manifest: `evidence/blastem_session_manifest.json`
- Screenshot matte check: `evidence/blastem_screenshot_visual_check.json`
- Visual VDP dump: absent.
- Emulator status: `testado_em_blastem_minimal`; the Showdown stage is visible in BlastEm without catastrophic magenta matte and without the earlier 320x224 downscale/crop assumption.
- Remaining visual limit: banded palette approximation leaves visible color degradation/blue gaps and the MUGEN parallax model is flattened into one streamed SGDK plane for this lab viewer.
- Curadoria visual: `analysis/palette_violations.json` marcar `pass_with_degradation` nao e suficiente para aprovar qualidade. O export usa `187569` nearest-color remaps, reduz o viewport de 76 cores uteis para 26 e perde vitalidade cromatica.
- Curadoria de camera: `showdown.def` declara `zoffset=215`, bounds X/Y e `verticalfollow=.5`; o runtime atual usa camera de explorador/autopan livre, sem contrato de palco de luta.
- Runtime limit: frame animation is disabled in the viewer (`FRAME_ANIMATION_ENABLED=0`) because changing frames forced large tile-cache reloads and caused visible tearing during capture. All four reconstructed frames remain exported and reported for curation.
- Camera status: manual D-pad camera works from boot; autopan is delayed for 1800 ticks so evidence starts on the canonical MUGEN view, then sweeps the 768x480 world.
- Budget status: `validado_budget=false`; `res_graph_report` is present but still warns that code-loaded tiles require explicit VDP dump or telemetry.
- Latest `res_graph_audit.ps1`: `status=warn`, issue `RG_CODETILE001`.
- Latest viewer `freshness_audit.ps1`: `status=warning`, `stale=2`, `missing_required=2`.
- Latest root `freshness_audit.ps1`: `status=warning`, `stale=1`, `missing_required=2`.
- Latest `validate_resources.ps1`: failed with 1 error and 11 warnings. The hard error remains code-loaded tile budget unmeasured; this is acceptable only as `lab_not_delivery`.
- Latest `audit_project_learning.ps1 -Mode Capture`: `learning_context_present`, lessons `11`, candidates `7`, `canonical_promotion_performed=false`.
- Curadoria 2026-06-13 validations:
  - `validate_project_context`: passed, `context=exercise`, `blockers=0`.
  - `validate_project_methodology`: passed, `blockers=0`.
  - `validate_project_hygiene`: blocked, `blockers=3`.
  - `validate_resources`: failed, `errors=8`, `warnings=6`, `checked=0`; this is expected for the current lab root because technique manifests, hygiene, visual gate and freshness are not delivery-clean.
  - `audit_project_learning` fallback via bundled Python: `lessons=13`, `candidates=9`, `canonical_promotion_performed=false`.

## 2026-06-14 Recovery Attempt Snapshot

- Route outcome: `route_b_compare_flat_degraded_runtime_with_palette_camera_repair`; `route_a_multi_plane` was contracted but not implemented in this ROM.
- ROM: `sgdk_viewer/showdown_viewer/out/rom.bin`, SHA256 `535cac333cea8d3410a36fa054b9cc7188d43246f7cfef447b387cb993060564`, size `262144` bytes.
- Build status: `buildado_debug_make`; wrapper build failed before compilation because the system Python used by asset preparation lacks `PIL`. Direct debug make was used only for lab evidence.
- BlastEm evidence: screenshot `sgdk_viewer/showdown_viewer/out/evidence/blastem/screenshot.png`, SRAM `sgdk_viewer/showdown_viewer/out/evidence/blastem/save.sram`, report `sgdk_viewer/showdown_viewer/out/logs/blastem_evidence.json`.
- Evidence caveat: `blastem_evidence.json` has the new ROM hash and screenshot/SRAM status, but `out/evidence/blastem/session_manifest.json` remained stale from 2026-06-08; the current session log is `out/evidence/blastem/evidence_session_20260614_062303_2883de4b.log`.
- Visual VDP dump: absent; current SRAM exposes `MDRT` heartbeat but no auditavel `VLAB` block.
- Camera report: `analysis/showdown_camera_report_v001.json`; default camera stays at `x=224`, `y=256`, floor anchor screen Y `215`, autopan disabled as evidence, D-pad marked lab-only.
- Palette report: `analysis/showdown_recovery_palette_measurement_v001.json`; palette is more vibrant, but nearest-color remaps and the BlastEm right-edge artifact block visual approval.
- Budget report: `analysis/showdown_budget_report_v001.json`; global tile id limit fits, but budget is not validated without VDP dump/frame telemetry and the runtime still streams a single flat BG_A window.
- Comparison board: `work/diagnostics/showdown_recovery_comparison_v001.png`.
- Final validations:
  - `validate_project_context`: ok, `context=exercise`, `blockers=0`;
  - `validate_project_methodology`: passed, `blockers=0`;
  - `validate_project_hygiene`: blocked, `blockers=3`;
  - `freshness_audit`: warning, `stale=0`, `missing_required=2`;
  - `validate_resources -WorkDir`: failed, `errors=8`, `warnings=5`;
  - Python tests: `22 passed`;
  - `audit_project_learning -Mode Capture`: `lessons=13`, `candidates=9`, `canonical_promotion_performed=false`.
- Closeout status: `blocked_rework_required`, not `testado_em_emulador` final, not `validado_budget`, not `ready_for_aaa`.

## 2026-06-14 Follow-up Recovery Snapshot

- Supersedes the earlier 2026-06-14 recovery attempt for the current ROM/evidence.
- Route outcome: `route_b_compare_flat_degraded_runtime_with_palette_camera_line_scroll_repair`; `route_a_multi_plane` remains contracted but not implemented.
- ROM: `sgdk_viewer/showdown_viewer/out/rom.bin`, SHA256 `80b91d451261a38b2db115eaa0f2558328bcd25f5dc03e0b89131bd093ffcd80`.
- Build status: canonical wrapper build still fails before compilation because the host Python used by asset preparation lacks `PIL`; direct SGDK 2.11 debug make was used only for lab evidence.
- BlastEm evidence: screenshot `sgdk_viewer/showdown_viewer/out/evidence/blastem/screenshot.png`, SRAM present, report `sgdk_viewer/showdown_viewer/out/logs/blastem_evidence.json`.
- Visual VDP dump: absent; no `validado_budget` claim is allowed.
- Camera report: `analysis/showdown_camera_report_v001.json`; default camera `x=224`, `y=256`, floor anchor screen Y `215`, dual-focus fixture starts P1/P2 at world x `314`/`454`, floor y `471`.
- Camera runtime: D-pad now moves virtual fighters rather than free camera; A/B trigger super jump fixture; vertical dead zone and `verticalfollow=1/2` are implemented with integer math.
- Depth runtime: `BG_A` uses row-multicamera streaming and `HSCROLL_LINE`; far band uses `43/100`, mid band `71/100`, floor band `1/1`, water line-scroll y range `88..176`.
- Depth caveat: this is still one streamed BG_A route; no BG_B far plane, sprite graft foreground, or true MUGEN BG0/BG1/BG2/BG3 split exists in this ROM.
- Palette report: `analysis/showdown_recovery_palette_measurement_v001.json`; export saturation rose to `0.534`, BlastEm crop saturation `0.4819`, but nearest-color remaps remain `390536` and perceptual loss is still visible.
- VDP contract audit: `analysis/showdown_vdp_contract_audit_v001.json`, status `pass`, bin preview roundtrip `diff_pixels=0`, invalid CRAM words `0`, invalid tile nibbles `0`.
- Budget report: `analysis/showdown_budget_report_v001.json`; unique tiles `2244`, max active-window unique tiles `1074`, cache capacity `1138`, estimated cache VRAM `36416`, line-scroll DMA estimate `448` bytes/frame.
- Comparison board: `work/diagnostics/showdown_recovery_comparison_v001.png`.
- Closeout status: `blocked_rework_required`, not `testado_em_emulador` final, not `validado_budget`, not `ready_for_aaa`.

## Required Evidence Chain

Root -> `doc/viewer_aggregate_manifest.json` -> `sgdk_viewer/showdown_viewer/out/rom.bin` -> BlastEm evidence under `evidence/` or viewer `out/evidence/`.

## Blockers / Honest Limits

- This is a training/lab fixture, not an AAA delivery.
- No `ready_for_aaa` declaration is allowed.
- `flattened_mugen_parallax`: BG0/BG1/BG2/BG3 possuem deltas distintos; o viewer atual tem apenas row-multicamera/line-scroll parcial dentro de um unico `BG_A`, nao um split multi-plano real.
- `fighting_stage_camera_contract_partial`: contrato existe e autopan foi removido como evidencia; ha fixture de foco duplo/deadzone/super jump, mas ainda nao ha integracao com entidades finais de lutador nem telemetria de camera.
- `palette_vibrancy_partial`: a paleta semantica recupera cor e saturacao, mas ainda ha `390536` remaps e perda perceptiva no BlastEm normalizado.
- `visual_gate_too_narrow`: o gate mede matte/magenta e conflitos, mas nao mede fidelidade perceptiva, vitalidade de paleta ou composicao.
- `nested_lab_art_not_detected` foi encerrado em 2026-07-19: o diagnostico
  retorna `4_lab_nested_art_review`, separa 9 fontes, 3 evidencias, 5 recursos
  ativos e 73 imagens de trabalho, e identifica o viewer SGDK aninhado. Isso
  corrige discovery apenas; nao promove qualidade, budget ou runtime.
- `tools/mugen2sgdk` should be wrapped or improved only with explicit human approval.
- Any future claim of HV flip savings must remain report-backed; current full-world Showdown fixture reports H/V/HV matches `5/12/4`.
- `validate_resources.ps1` still reports methodology/resource blockers for canonical closeout, including local `.agent` degraded mode, missing visual delivery/scene closeout gates, stale freshness/documentation, and missing VDP measurement evidence for code-loaded tiles.
- Do not regress the reconstruction pipeline to metadata-only parsing: PCX index 0 alpha, SFF axes, DEF start/tile and layer order are all executable composition rules.
- Do not let viewer HUD/debug text overwrite PAL0-PAL3 after stage palettes are loaded.
- Do not reduce the source world to 320x224 to make a viewer pass. The correct training contract is world-size reconstruction plus camera/tilemap streaming or another explicitly justified large-map strategy.
- Do not re-enable SGDK frame animation until tile-cache streaming is incremental or double-buffered enough to avoid tearing during emulator evidence capture.

## Next Operator Notes

- Leia `doc/showdown_camera_palette_curation_2026-06-13.md` antes de qualquer rework.
- Re-run `python tools/pipeline/run_showdown_pipeline.py` and `python tools/sgdk_export/export_showdown_bins.py` after changing SFF/DEF parsing.
- Copy updated `work/sgdk_bins/*.bin` into `sgdk_viewer/showdown_viewer/res/data/showdown/` before building.
- Build and evidence must use the workspace SGDK 2.11 wrapper and BlastEm gate.
- If the wrapper path degrades, record the blocker, run the relevant gates separately, and keep any direct SGDK make build labeled as technical/lab evidence only.

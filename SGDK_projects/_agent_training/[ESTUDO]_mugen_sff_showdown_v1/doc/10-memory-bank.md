# Memory Bank - MUGEN SFF Showdown Study

## Current Status

- Status: `controlled_training_area`
- Training mode: `train_agent`
- `lab_not_delivery=true`
- `ready_for_aaa=false`
- Root is the authority for the study; `sgdk_viewer/showdown_viewer/` is an embedded proof viewer, not an independent delivery project.
- Curadoria 2026-06-13: o resultado atual esta `rework_required` para composicao, camera e paleta. A ROM aparece no BlastEm, mas nao preserva a qualidade visual do stage.

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
- Raw tiles across all frames: 23040
- Global unique ROM tiles: 2253
- Runtime model: tile graphics + tilemap window streaming. The SGDK viewer streams a 42x30 tile window from custom map words into a local VDP cache.
- Streaming cache estimate: max observed active-window unique tiles `1087`; cache capacity `1151`; estimated cache VRAM `36832` bytes.
- Dedup saving ratio: `0.902214`
- H/V/HV flip reuse measured: `5/12/4`
- Lossy tile merge: disabled (`0` merges). The fixture keeps exact global tiles for the streaming route.
- Visual reconstruction gate: `pass`, matte/magenta/transparent ratio `0.0` on all four 768x480 reconstructed frames.
- BlastEm screenshot visual check: `pass`, exact/near-magenta ratio `0.0` inside the active captured viewport.
- Palette status: `pass_with_degradation`; final export fits four banded sub-palettes but uses `187569` nearest-color remaps.
- Preliminary budget: `streaming_lab_proof`, not `validado_budget`.
- Budget caveat: `res_graph_report` still warns `RG_CODETILE001` because runtime code streams tiles and no VDP dump/telemetry proves the actual live VRAM state.

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

## Required Evidence Chain

Root -> `doc/viewer_aggregate_manifest.json` -> `sgdk_viewer/showdown_viewer/out/rom.bin` -> BlastEm evidence under `evidence/` or viewer `out/evidence/`.

## Blockers / Honest Limits

- This is a training/lab fixture, not an AAA delivery.
- No `ready_for_aaa` declaration is allowed.
- `flattened_mugen_parallax`: BG0/BG1/BG2/BG3 possuem deltas distintos, mas o viewer atual achata tudo em um unico `BG_A`.
- `fighting_stage_camera_contract_missing`: nao ha contrato que preserve chao, zoffset, foco dos lutadores e verticalfollow.
- `palette_vibrancy_lost`: a paleta encaixa tecnicamente, mas perde cores vibrantes e separacao de materiais.
- `visual_gate_too_narrow`: o gate mede matte/magenta e conflitos, mas nao mede fidelidade perceptiva, vitalidade de paleta ou composicao.
- `nested_lab_art_not_detected`: `art_diagnostic.py` retorna `3_no_art` no root porque nao entende arte em `work/`, `analysis/`, `evidence/` e viewer aninhado.
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

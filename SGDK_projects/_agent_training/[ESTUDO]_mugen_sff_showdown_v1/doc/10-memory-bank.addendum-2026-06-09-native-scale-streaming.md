# Memory Bank Addendum - Native-Scale Showdown Streaming

## Operational State

The Showdown study remains a controlled training area:

- `controlled_training_area`
- `lab_not_delivery=true`
- `ready_for_aaa=false`
- `validado_budget=false` until wrapper gates and/or VDP dump evidence accept the active streaming cache.

## Current Fixture Contract

The MUGEN stage must be reconstructed at native world size, not resized into the Mega Drive viewport.

- reconstructed world: 768x480 pixels;
- tilemap: 96x60 tiles;
- viewport: 320x224 pixels;
- camera coverage: horizontal and vertical;
- SGDK viewer: `sgdk_viewer/showdown_viewer`;
- ROM: `sgdk_viewer/showdown_viewer/out/rom.bin`;
- ROM SHA-256: `4b0ce91f5e370a8d6fd4e842a511c7f6c2e52a8f49ee4f2419696c972305fe2e`.

## Guardrails Added

- `analysis/native_scale_camera_streaming_report.json` records the no-resize camera/streaming contract.
- `sgdk_viewer/showdown_viewer/doc/vram_residency_report.json` records the active VDP tile cache contract for `res_graph_audit.ps1`.
- `doc/agent_learning/2026-06-09-showdown-native-scale-streaming.md` captures the alpha/Z-order/tiling lesson for later curation.

## Remaining Verification

The next successful tool execution must rerun:

- `tools/sgdk_wrapper/res_graph_audit.ps1` on `sgdk_viewer/showdown_viewer`;
- `tools/sgdk_wrapper/validate_resources.ps1` on `sgdk_viewer/showdown_viewer`;
- `tools/sgdk_wrapper/freshness_audit.ps1` for viewer and root where applicable;
- `tools/sgdk_wrapper/audit_project_learning.ps1 -Mode Capture`;
- BlastEm screenshot/SRAM if the ROM changes.

If `res_graph_audit.ps1` rejects the new VRAM residency report, do not claim budget validation. Capture the rejection and replace the evidence model with wrapper-native VDP dump or runtime telemetry.

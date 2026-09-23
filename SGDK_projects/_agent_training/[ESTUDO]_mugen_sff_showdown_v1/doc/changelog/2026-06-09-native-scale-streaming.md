# 2026-06-09 - Native-Scale Streaming Addendum

## Changed

- Added a root-level native-scale camera/streaming report to prevent future agents from resizing the MUGEN stage down to 320x224.
- Added viewer-level VRAM residency evidence describing the active 1151-tile VDP streaming cache for `bin_showdown_tiles`.
- Added a local learning note documenting the anti-magenta reconstruction failure, required DEF layer composition behavior, and no-resize camera contract.
- Added this memory-bank addendum because command execution was unavailable during the follow-up pass and the canonical memory file could not be safely inspected before direct editing.

## Evidence

- `analysis/native_scale_camera_streaming_report.json`
- `sgdk_viewer/showdown_viewer/doc/vram_residency_report.json`
- `doc/agent_learning/2026-06-09-showdown-native-scale-streaming.md`
- `doc/10-memory-bank.addendum-2026-06-09-native-scale-streaming.md`

## Status

- `controlled_training_area`
- `lab_not_delivery=true`
- `ready_for_aaa=false`
- budget still requires wrapper verification or VDP dump acceptance after the execution sandbox recovers.

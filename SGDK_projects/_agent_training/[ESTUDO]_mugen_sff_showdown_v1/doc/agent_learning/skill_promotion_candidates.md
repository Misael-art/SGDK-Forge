# Skill Promotion Candidates

No canonical promotion candidates approved. This study remains a controlled training area.

## mugen_stage_logical_composition_gate

- Candidato: mugen_stage_logical_composition_gate
- Contexto: Local Showdown training fixture only.
- Padrao observado: Parse DEF stage instructions, apply SFF axes, apply PCX index-0 alpha, compose layers in engine order, support tiling, then run a matte/magenta histogram gate before any SGDK export.
- Justificativa: This prevented a catastrophic magenta matte regression from being hidden by later tile/bin/ROM steps.
- Evidencia: analysis/reconstruction.json analysis/tile_stats.json evidence/blastem_evidence.json evidence/blastem_showdown_screenshot.png
- Limite de uso: Not promoted. Before canonical promotion, compare against at least two more SFF v1 stages, define mask inference policy, and decide how to represent palette degradation separately from hard palette violations.

## mugen_stage_full_world_camera_streaming_fixture

- Candidato: mugen_stage_full_world_camera_streaming_fixture
- Contexto: Local Showdown training fixture only.
- Padrao observado: Derive the full stage world from MUGEN DEF camera bounds, export global ROM tiles and a world tilemap, then use a SGDK camera/window-streamed viewer instead of resizing to the Mega Drive viewport.
- Justificativa: This prevented a false 320x224 conversion from hiding the actual 768x480 stage and made camera/budget tradeoffs explicit.
- Evidencia: analysis/reconstruction.json analysis/tile_stats.json doc/viewer_aggregate_manifest.json evidence/blastem_showdown_screenshot.png
- Limite de uso: Not promoted. Needs at least two additional MUGEN stages, an explicit parallax/delta model, VDP dump/telemetry, and a production-safe incremental streaming strategy before any canonical skill/tool change.

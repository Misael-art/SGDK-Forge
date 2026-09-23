# Failure Patterns

- Do not ignore `tools/mugen2sgdk` when working on MUGEN conversion.
- Do not let a template-derived SGDK viewer become the only place with memory/changelog/learning context.
- Do not claim `validado_budget` from a PNG reconstruction or binary export without a current ROM and emulator evidence.
- Do not treat MUGEN `.def` as metadata only. Reconstructing a stage means executing 2D engine composition rules: layer order, PCX index-0 alpha, SFF axes, `start`, animation offsets and tiling.
- Do not let a successful SGDK build hide a bad `work/reconstructed_layers/frame_*.png`; the anti-magenta visual gate must run before export.
- Do not reserve a stage subpalette for debug text after loading scene palettes; PAL0-PAL3 are part of the visual asset contract.
- Do not resize a MUGEN stage to the Mega Drive viewport when the DEF camera bounds prove the original world is larger than 320x224.
- Do not treat global ROM tile count as resident VDP tile count. A large world needs a separate runtime cache/streaming budget.
- Do not animate full-world streamed frames until the tile-cache update strategy is incremental or double-buffered enough to avoid capture tearing.
- Do not claim visual success for an imported fighting stage just because it appears in BlastEm; parallax, camera floor anchor and palette vitality must survive source/export/runtime comparison.

## MUGEN stage composition is execution, not metadata

- Data: 2026-06-07
- Contexto: showdown.sff/showdown.def reconstruction for work/reconstructed_layers/frame_0000.png before SGDK export.
- Falha observada: The previous reconstructed frames contained a large solid magenta matte and displaced layers even though SFF/DEF properties were parsed.
- Causa provavel: The renderer treated the DEF as metadata instead of executing MUGEN 2D composition rules: SFF axes, PCX index-0 alpha, BG order, start offsets, animation offsets and tiling.
- Mitigacao: Convert masked PCX sprites to RGBA with palette index 0 alpha 0, compose with alpha paste, draw BG sections in DEF order, apply start/offset/axis/tile rules, then run the anti-magenta histogram gate before SGDK binary export.
- Evidencia: analysis/reconstruction.json analysis/tile_stats.json analysis/palette_violations.json evidence/blastem_evidence.json evidence/blastem_showdown_screenshot.png
- Limite de uso: Local training evidence only; this is not a canonical parser promotion.

## SGDK viewer palettes must not overwrite stage palettes

- Data: 2026-06-07
- Contexto: sgdk_viewer/showdown_viewer rendered the reconstructed Showdown bins in BlastEm.
- Falha observada: The viewer loaded stage palettes and then reused PAL3 for debug text, corrupting foreground colors.
- Causa provavel: Template/debug UI assumptions leaked into a full-screen art viewer where all four subpalettes are part of the asset contract.
- Mitigacao: Do not reserve PAL0-PAL3 for debug text after loading full-screen stage palettes; keep debug text out of the palette contract or use a separate validated presentation path.
- Evidencia: sgdk_viewer/showdown_viewer/src/scenes/scene_demo.c evidence/blastem_showdown_screenshot.png evidence/blastem_evidence.json
- Limite de uso: Applies to full-screen code-loaded art fixtures using all four MD subpalettes.

## Viewport crop is not stage conversion

- Data: 2026-06-08
- Contexto: Showdown DEF camera bounds are larger than the Mega Drive viewport: world 768x480, viewport 320x224.
- Falha observada: A 40x28/320x224 reconstruction made the SGDK viewer easier to build but lost the original MUGEN stage extent and hid the need for camera management.
- Causa provavel: The conversion treated the display viewport as the source world instead of deriving the world from `boundleft`, `boundright`, `boundhigh` and `boundlow`.
- Mitigacao: Reconstruct full-world frames, export 96x60 tilemaps, and make the SGDK viewer manage camera/streaming. Use viewport previews only as evidence, not as source data.
- Evidencia: analysis/reconstruction.json analysis/tile_stats.json doc/viewer_aggregate_manifest.json sgdk_viewer/showdown_viewer/src/scenes/scene_demo.c evidence/blastem_showdown_screenshot.png
- Limite de uso: Local training evidence only. Exact MUGEN parallax/delta behavior still needs additional curation.

## Global ROM tiles are not resident VDP budget

- Data: 2026-06-08
- Contexto: Full-world Showdown export produced 2253 global unique ROM tiles, which cannot be claimed as a simple full-resident VDP fit.
- Falha observada: Treating all unique world tiles as resident would either exceed practical VDP layout expectations or obscure the difference between ROM storage and live VRAM cache.
- Causa provavel: Dedup metrics were initially read as a direct resident-budget claim instead of a source/export metric.
- Mitigacao: Report global ROM tiles separately from active-window unique tiles. The viewer now streams a 42x30 window with max observed active unique tiles 1087 and cache capacity 1151, while `validado_budget` remains false until VDP dump/telemetry exists.
- Evidencia: analysis/tile_stats.json analysis/scene_tilemap_conversion_report.json sgdk_viewer/showdown_viewer/out/logs/res_graph_report.json
- Limite de uso: This is a budget-audit pattern, not proof of runtime performance.

## Full-frame streaming can tear capture evidence

- Data: 2026-06-08
- Contexto: Runtime attempted to cycle four full-world frames by reloading a large camera tile cache.
- Falha observada: Short-warmup BlastEm screenshots showed horizontal tile-cache tearing/corruption even after the PNG reconstruction and exported bins were correct.
- Causa provavel: Large code-driven tile uploads were observable by the emulator/capture before the tile graphics and tilemap reached a stable state.
- Mitigacao: Batch tile uploads through a RAM staging buffer, disable display during scene-enter load, delay autopan, and keep `FRAME_ANIMATION_ENABLED=0` until incremental/double-buffered streaming is implemented.
- Evidencia: sgdk_viewer/showdown_viewer/src/scenes/scene_demo.c evidence/blastem_showdown_screenshot.png evidence/blastem_screenshot_visual_check.json
- Limite de uso: This fixes evidence stability for the lab viewer; it does not establish a production streaming engine.

## Visible stage can still fail composition and color

- Data: 2026-06-13
- Contexto: Curatorial review of Showdown source viewport, exported bin viewport and BlastEm evidence after full-world streaming fixture.
- Falha observada: The stage appears in BlastEm, but the MUGEN multi-delta parallax is flattened into one BG_A, the runtime camera behaves like a lab explorer instead of a fighting-stage camera, and the palette looks dull despite a vibrant source.
- Causa provavel: The agent treated anti-magenta, per-tile palette fit and ROM visibility as sufficient visual gates. It did not require `camera_motion_contract`, `parallax_layer_contract` or `palette_vitality_check`.
- Mitigacao: Before rework, derive camera from `zoffset`, bounds and `verticalfollow`; map BG deltas to SGDK planes/fallback; compare source/export/BlastEm for color vitality. If flattening is chosen, label it `lab_flattened_reference` or `compare_flat`, not `elite_ready`.
- Evidencia: doc/showdown_camera_palette_curation_2026-06-13.md analysis/reconstruction.json analysis/palette_violations.json evidence/blastem_showdown_screenshot.png
- Limite de uso: Applies to imported fighting stages and large scrolling backgrounds; a production-ready rule needs more fixtures before tool promotion.

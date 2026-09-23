# Success Patterns

- Keep MUGEN fixture automation inside the study until a human approves canonical promotion.
- Report dedup/HV results even when flip matches are zero; zero is a valid measured result.
- Make the root study own the evidence chain for nested SGDK viewers.
- Add visual reconstruction gates before tile export, not after ROM build. A simple matte/magenta histogram would have blocked the bad frame before SGDK entered the loop.
- Record inferred alpha separately from declared `mask=1`; this keeps the stage usable while preserving curation evidence for questionable source data.
- For full-screen MUGEN stage fixtures, generate an offline reconstructed PNG and a BlastEm screenshot for the same ROM/hash before judging SGDK integration.
- For MUGEN stages larger than the target viewport, derive the world from DEF camera bounds first, then decide between resident, streaming or segmented tilemaps.
- Use a delayed autopan plus manual camera controls in training viewers so the evidence starts on the canonical view while the runtime can still inspect the full world.

## Anti-magenta gate before tile export

- Data: 2026-06-07
- Contexto: Showdown reconstruction produces work/reconstructed_layers/frame_0000.png through frame_0003.png before SGDK export.
- Problema resolvido: A visual histogram gate rejected solid magenta or transparent matte leakage before the tile/bin/ROM stage could hide the root cause.
- Mitigacao: Count exact magenta, near-magenta and transparent pixels in the 320x224 reconstructed frame and fail export when the bad-pixel ratio exceeds 5 percent.
- Evidencia: analysis/tile_stats.json analysis/reconstruction.json evidence/blastem_evidence.json
- Limite de uso: This gate detects catastrophic matte leakage, not palette quality or artistic fidelity.

## Root-owned evidence chain for nested viewer

- Data: 2026-06-07
- Contexto: sgdk_viewer/showdown_viewer remains nested, but the study root owns the ROM hash, reports and BlastEm evidence.
- Problema resolvido: The viewer stopped being an orphan proof because root manifests connect source inputs, reconstruction reports, SGDK bins, ROM and emulator screenshot.
- Mitigacao: Keep doc/viewer_aggregate_manifest.json, doc/10-memory-bank.md, lab_report.json and doc/changelog/changelog.md aligned with the same ROM SHA256 and evidence files.
- Evidencia: doc/viewer_aggregate_manifest.json doc/10-memory-bank.md lab_report.json evidence/blastem_evidence.json
- Limite de uso: This is governance for training fixtures, not a delivery claim.

## Full-world tilemap plus camera viewer

- Data: 2026-06-08
- Contexto: Showdown camera bounds produce a 768x480 stage world, larger than the 320x224 Mega Drive viewport.
- Problema resolvido: The viewer can now display the stage as a large tilemap with a managed camera instead of relying on a resized/cropped PNG reconstruction.
- Mitigacao: Reconstruct 768x480 frames, export 96x60 maps, keep global ROM tile IDs in a custom map format, stream a 42x30 active window into VDP, and document camera bounds in the root manifest.
- Evidencia: analysis/reconstruction.json analysis/tile_stats.json doc/viewer_aggregate_manifest.json sgdk_viewer/showdown_viewer/src/scenes/scene_demo.c evidence/blastem_showdown_screenshot.png
- Limite de uso: Lab proof only. Budget is estimated and parallax is flattened.

## Evidence-friendly streaming hold

- Data: 2026-06-08
- Contexto: The BlastEm capture tool may take its screenshot after several seconds of emulation, while large tile uploads can still be visually unstable if the camera/animation is moving.
- Problema resolvido: The final evidence starts on the canonical Showdown view and avoids tile tearing.
- Mitigacao: Disable frame animation, batch upload active-window tiles, disable the display during scene-enter load, and delay autopan for 1800 ticks while keeping D-pad camera available.
- Evidencia: evidence/blastem_showdown_screenshot.png evidence/blastem_screenshot_visual_check.json sgdk_viewer/showdown_viewer/src/scenes/scene_demo.c
- Limite de uso: This is a training viewer evidence pattern, not a substitute for production streaming telemetry.

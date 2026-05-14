# CURATION_LEARNINGS_REPORT - AXE DE ACO FIGHTER

Generated: 2026-05-14T05:34:46-03:00

## Erros Evitados Pelos Gates Novos

- Fake proof avoided: final evidence cites persistent out/rom.bin, persistent screenshot and persistent SRAM, not a throwaway tempdir.
- Stable laundering avoided: the closeout remains blocked and the final status is prototype_playable, not Stable or AAA.
- Stale runtime avoided: after visual capture rebuilt the ROM, runtime capture and validation were re-run before final closeout.
- VRAM collision avoided: res_graph_audit.ps1 reports VRAM ok and overlap_count=0.
- Sprite slicing blockers avoided: 26 character strips passed integrity checks with no edge clipping, matte mismatch, island debris or baked FX blockers.
- Palette/material drift caught: the visual gate refuses AAA because the source-to-ROM art path is not premium enough.

## Assets Que Precisaram de Regeneracao ou Correcao

- Marina and Bento strips were regenerated/rebuilt by the dedicated asset builder as horizontal per-action strips.
- Runtime cells were enlarged to Marina 80x88 and Bento 88x88 to remove clipping risk and preserve pivot/ground line.
- Indexed PNGs were re-saved as 4bpp with explicit 16-entry palettes and index 0 transparency.
- BG_A/B were regenerated within a low unique-tile budget: BG_B 156 unique tiles and BG_A 255 unique tiles.
- The native concept image was persisted as source art, but it remains concept evidence, not final per-action strip source.

## Decisoes Conservadoras Tomadas

- Boot direto na cena de luta para cumprir a missao sem criar menu textual ou landing page.
- SPR_initEx(420) used to reserve a predictable sprite tile window and satisfy the res graph.
- No float/double/malloc/free in the fight loop; state and runtime data are static/simple.
- FX kept as separate sprites instead of baked into fighter sheets.
- Closeout final was run with no rebuild and no new capture to avoid changing the ROM after BlastEm evidence.
- Autoprepare was disabled for this project after generated res assets became the validated source of the build path.

## Oportunidades de Curadoria Canonica Ainda Restantes

- Produce real premium per-action animation strips for Marina and Bento using image generation or curated source art, then repeat slicing and gates.
- Add formal audio validation and document the audio evidence axis.
- Enable VLAB/visual VDP dump path if the project needs the newer SRAM + VDP dump evidence bundle.
- Add deterministic input scene regression for the fight scene.
- Create a longer BlastEm soak window after art and runtime stop changing.
- Recover VRAM headroom before adding new resident art; current model has 0 tile headroom before maps.

## Resultado Final Com Evidencia

- Final status: prototype_playable.
- Visual status: visual_gate_blocked.
- Build proof: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\rom.bin (5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f).
- Emulator proof: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\captures\benchmark_visual.png, F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\captures\save.sram, F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\emulator_session.json.
- Budget proof: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\res_graph_report.json, F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\vram_residency_report.json.
- Validation proof: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\validation_report.json, F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\scene_closeout_gate_report.json.

The result is playable and real, but not AAA ready.

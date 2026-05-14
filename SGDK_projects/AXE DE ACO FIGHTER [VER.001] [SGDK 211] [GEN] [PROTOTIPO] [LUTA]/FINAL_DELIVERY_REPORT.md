# FINAL_DELIVERY_REPORT - AXE DE ACO FIGHTER

Generated: 2026-05-14T05:34:46-03:00

## Verdict

Final classification: prototype_playable.
AAA status: visual_gate_blocked.
Stable status: not_stable.

This is a real playable SGDK/BlastEm proof, not a fake proof: out/rom.bin is persistent, the ROM was booted in BlastEm, a persistent screenshot was captured, and a fresh SRAM evidence file exists. It is not AAA because the visual source pipeline did not produce premium per-action fighter strips; the runtime strips are local/procedural and the visual gate correctly blocks promotion.

## Evidence Paths

- ROM: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\rom.bin
- ROM sha256: 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f
- BlastEm screenshot: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\captures\benchmark_visual.png
- Screenshot sha256: c0cb2d1d196fd3a6dd23b638676e08bb692fb540058424a25122b19fb56e3c58
- Fresh SRAM: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\captures\save.sram
- SRAM sha256: 4d18466bc9fad69c28e61861f58826484bd632165042acbd1925bb11711ce6b8
- validation_report.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\validation_report.json
- res_graph_report.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\res_graph_report.json
- vram_residency_report.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\vram_residency_report.json
- visual_delivery_gate_report.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\visual_delivery_gate_report.json
- scene_closeout_gate_report.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\scene_closeout_gate_report.json
- runtime_metrics.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\runtime_metrics.json
- emulator_session.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\emulator_session.json
- sprite_integrity_summary.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\sprite_integrity_summary.json
- delivery_findings.json: F:\Projects\MegaDrive_DEV\SGDK_projects\AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]\out\logs\delivery_findings.json

## Gate Matrix

| Axis | Result | Evidence |
|------|--------|----------|
| Build | ok | out/rom.bin, sha256 5f8a5d66969554c08861975d5080863d652b89512956afdd5647931d66eff00f |
| BlastEm boot | ok | emulator_session.json, fresh_sram_confirmed=True |
| Screenshot | ok | out/captures/benchmark_visual.png |
| Gameplay basic | funcional | emulator_session.json, scene id 3 runtime probe |
| Runtime probe | partial real capture | frames_seen=151, samples=32, over_budget_frames=0 |
| Resource validation | ok with visual blockers | errors=0, warnings=2, blockers=visual_gate_blocked, local_rasterization_used_as_final, source_to_rom_mismatch |
| Res graph | ok | VRAM ok, overlaps=0 |
| Sprite integrity | passed | 26/26 strips passed |
| Visual delivery | blocked | visual_gate_blocked, local_rasterization_used_as_final, source_to_rom_mismatch |
| Scene closeout | blocked honestly | substeps ok, final status blocked |
| Audio | not fully validated | PSG hooks built, emulator-session audio=nao_testado |

## Implemented Playable Slice

- Direct fight screen, no debug landing/menu.
- Two visible fighters with distinct palettes and silhouettes.
- P1 controls: walk, dash, crouch, hop, guard, light, medium and sweep/special.
- P2 CPU: approach, retreat, guard and attack intervals.
- HP, timer, hit stun, pushback, knockdown/getup, impact spark, dust and light camera shake.
- Terreiro Neon da Ladeira stage with BG_B/BG_A split and readable HUD.

## Known Blockers

- visual_gate_blocked: final fighter art is not premium per-action generated/curated strips.
- local_rasterization_used_as_final: procedural local rasterization is acceptable for prototype, not final AAA.
- source_to_rom_mismatch: generated concept exists, but the exact final ROM sprite strips do not come from premium source strips.
- Runtime evidence is real but partial, not a long soak.
- Audio validation is not measured.
- visual_vdp_dump.bin is absent in this MDRT evidence path; screenshot + fresh SRAM are the persistent emulator evidence.

## Final Statement

Do not call this Stable or AAA. The honest delivery state is prototype_playable with real BlastEm evidence and an active visual_gate_blocked blocker.

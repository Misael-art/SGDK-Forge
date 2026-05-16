# Final Delivery Report - NOVO ARARA GI FIGHTER V2

Date: 2026-05-16

## Status

- Delivery classification: playable SGDK/Mega Drive prototype, tested in BlastEm.
- ROM: `out/rom.bin`
- ROM SHA256: `93d02b59721980b69f2d7862d0866818bc371cdd2b71e2984f4261a3c9fb750e`
- ROM size: 262144 bytes
- Final gate: `ready_for_aaa=true` in `out/logs/validation_report.json`

## Evidence

- Build/changelog: `doc/changelog/changelog.md`, `doc/changelog/roms/build_v005/build_meta.json`
- Resource validation: `out/logs/validation_report.json`
- Runtime metrics: `out/logs/runtime_metrics.json`
- BlastEm session: `out/logs/emulator_session.json`
- BlastEm evidence: `out/logs/blastem_evidence.json`
- Screenshot: `out/evidence/blastem/screenshot.png`
- SRAM: `out/evidence/blastem/save.sram`
- Resource graph: `out/logs/res_graph_report.json`
- Freshness: `out/logs/freshness_audit_report.json`
- Closeout: `out/logs/scene_closeout_gate_report.json`

## Runtime Metrics

- Scene: `2`
- Samples: `32`
- Over-budget frames: `0`
- CPU max: `39`
- CPU p95: `39`
- Scanline sprite pressure proxy: `6`
- FX peak concurrency: `1`

## Resource Symbols

- Stage: `lapa_bg_b`, `lapa_bg_a`
- FX: `spr_hit_spark`
- Caio: `spr_caio_idle`, `spr_caio_walk_forward`, `spr_caio_walk_back`, `spr_caio_dash`, `spr_caio_crouch`, `spr_caio_jump`, `spr_caio_guard`, `spr_caio_jab`, `spr_caio_medium`, `spr_caio_grip`, `spr_caio_hip_throw`, `spr_caio_hurt`, `spr_caio_knockdown`, `spr_caio_getup`
- Davi: `spr_davi_idle`, `spr_davi_walk_forward`, `spr_davi_walk_back`, `spr_davi_dash`, `spr_davi_crouch`, `spr_davi_jump`, `spr_davi_guard`, `spr_davi_jab`, `spr_davi_medium`, `spr_davi_grip`, `spr_davi_hip_throw`, `spr_davi_hurt`, `spr_davi_knockdown`, `spr_davi_getup`

## Honest Gaps

- No audio resources are declared in `.res`; audio is `not_required` for this slice.
- `visual_vdp_dump.bin` is not generated because this ROM exports MDRT runtime evidence, not VLAB visual dumps.
- Visual aesthetic analyzer still reports generic `needs_review` on non-critical assets; critical delivery assets are approved by `visual_delivery_gate_report.json`.

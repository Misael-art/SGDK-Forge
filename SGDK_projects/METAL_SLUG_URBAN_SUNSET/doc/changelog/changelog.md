# Changelog Canonico

Este arquivo registra snapshots reais de assets e ROMs do projeto.

- assets vivem em `doc/changelog/assets/`
- ROMs vivem em `doc/changelog/roms/`
- novas versoes so nascem quando o hash muda

## 2026-04-13T22:47:25.4409082-03:00 - initial_canonical_snapshot

- Task: initial_canonical_snapshot
- Asset snapshots:
  - sky_bg_b -> v001 (res/gfx/sky_bg_b.png)
  - city_bg_a -> v001 (res/gfx/city_bg_a.png)
  - spr_debris_01 -> v001 (res/gfx/debris_01.png)
  - spr_debris_02 -> v001 (res/gfx/debris_02.png)
  - spr_debris_03 -> v001 (res/gfx/debris_03.png)
  - spr_player -> v001 (res/gfx/spr_marco.png)
- ROM: build_v001 (sha256 9f4c01bc281220d59cdd34275b4811da459446860bb2fed669bd5bf03f52bd9a, 131072 bytes)
- Validation: errors=0, warnings=3
- Emulator evidence: runtime_metrics_stale

## 2026-04-14T06:10:00-03:00 - route_exploration_anime_style_study

- Task: route_exploration_anime_style_study
- Study artifacts:
  - route_exploration_board.md updated with `anime_style`
  - route_comparison_matrix.md updated with default vs `high_key_haze` vs `cool_evening` vs `anime_style`
  - route_decision_record.md updated with `anime_style` as challenger ready for user choice
  - out/route_tests/route_anime_style_candidate_strict15.png
  - out/route_tests/route_anime_style_aesthetic.json
  - out/route_tests/route_compare_with_incumbent_and_anime.png
- Asset snapshots: none
- ROM: unchanged
- Validation: curadoria only, sem novo build
- Emulator evidence: unchanged

## 2026-04-14T06:45:00-03:00 - anime_reference_retarget

- Task: anime_reference_retarget
- Study artifacts:
  - `anime_style` anterior marcado como interpretacao rejeitada
  - nova referencia correta: `Gemini_Generated_Image_riu4i2riu4i2riu4.png`
  - provas geradas em `out/route_tests/route_anime_reference_*`
  - `route_comparison_matrix.md` e `route_decision_record.md` atualizados com a nova leitura humana
- Asset snapshots: none
- ROM: unchanged
- Validation: curadoria only, sem novo build
- Emulator evidence: unchanged

## 2026-04-15T14:30:00-03:00 - anime_linefirst_process_lock

- Task: anime_linefirst_process_lock
- Study artifacts:
  - pipeline travado em `crop -> anime style -> line art only -> promocao Mega Drive do traco -> pintura inteligente por massas`
  - gerador canonico: `tools/image-tools/generate_linefirst_anime_route.py`
  - variantes geradas:
    - `out/route_tests/route_anime_linefirst_balanced_*`
    - `out/route_tests/route_anime_linefirst_cohesive_*`
    - `out/route_tests/route_anime_linefirst_board.png`
  - docs atualizados:
    - `doc/route_exploration_board.md`
    - `doc/route_comparison_matrix.md`
    - `doc/route_decision_record.md`
    - `doc/10-memory-bank.md`
- Measured outcomes:
  - `anime_linefirst_balanced`: score `0.7184`, `1261` tiles totais
  - `anime_linefirst_cohesive`: score `0.6988`, `1248` tiles totais
- Asset snapshots: none
- ROM: unchanged
- Validation: curadoria only, sem novo build
- Emulator evidence: unchanged

## 2026-04-16T23:00:55.9732070-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - urban_default_bg_b -> v001 (res/gfx/sky_bg_b.png)
  - urban_default_bg_a -> v001 (res/gfx/city_bg_a_448.png)
  - urban_linefirst_balanced_bg_b -> v001 (res/gfx/urban_linefirst_balanced_bg_b.png)
  - urban_linefirst_balanced_bg_a -> v001 (res/gfx/urban_linefirst_balanced_bg_a.png)
  - urban_linefirst_cohesive_bg_b -> v001 (res/gfx/urban_linefirst_cohesive_bg_b.png)
  - urban_linefirst_cohesive_bg_a -> v001 (res/gfx/urban_linefirst_cohesive_bg_a.png)
  - mission1_shared_bg_b -> v001 (res/gfx/mission1_skylift_bg_b.png)
  - mission1_flat_strict15_bg_a -> v001 (res/gfx/mission1_flat_strict15.png)
  - mission1_flat_snap700_bg_a -> v001 (res/gfx/mission1_flat_snap_700.png)
  - mission1_skylift_bg_a -> v001 (res/gfx/mission1_skylift_bg_a.png)
- ROM: build_v002 (sha256 4afe6c85e2fec36681adec89c96e1844cff018384977f610f2ff13cc8d798e0f, 262144 bytes)
- Validation: errors=0, warnings=4
- Blockers: visual_gate_blocked, changelog_missing, emulator_evidence_stale
- Emulator evidence: rom_identity_mismatch

## 2026-04-16T23:25:12.0899336-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v003 (sha256 ca660262e4ad2a57a080cd2ff6bef24313e89677669962428989efb730782a72, 262144 bytes)
- Validation: errors=0, warnings=3
- Blockers: visual_gate_blocked, emulator_evidence_stale
- Emulator evidence: rom_identity_mismatch

## 2026-04-16T23:30:50.9763583-03:00 - viewer_blastem_evidence_refresh

- Task: viewer_blastem_evidence_refresh
- Scene viewer proof refreshed against ROM `build_v003`
- Evidence files:
  - `out/captures/viewer_urban_default_20260416_pw.png`
  - `out/captures/viewer_mission1_flat_snap700_20260416_pw.png`
- Emulator session: `out/logs/emulator_session.json`
- Validation after refresh: errors=0, warnings=1
- Blockers: visual_gate_blocked
- Emulator evidence: ok

## 2026-04-17T00:05:34.5760449-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - urban_linefirst_balanced_bg_b -> v002 (res/gfx/urban_linefirst_balanced_bg_b.png)
  - mission1_skylift_bg_a -> v002 (res/gfx/mission1_skylift_bg_a.png)
- ROM: build_v004 (sha256 c09168516d2c112e09ba2458ac999e5568130f3ac0d892f1aed3366dfafe5583, 262144 bytes)
- Validation: errors=0, warnings=3
- Blockers: changelog_missing
- Emulator evidence: rom_identity_mismatch

## 2026-04-17T01:02:24.2451271-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - urban_default_bg_b -> v002 (res/gfx/sky_bg_b.png)
  - urban_linefirst_cohesive_bg_b -> v002 (res/gfx/urban_linefirst_cohesive_bg_b.png)
  - mission1_shared_bg_b -> v002 (res/gfx/mission1_skylift_bg_b.png)
  - mission1_flat_strict15_bg_a -> v002 (res/gfx/mission1_flat_strict15.png)
  - mission1_flat_snap700_bg_a -> v002 (res/gfx/mission1_flat_snap_700.png)
  - mission1_skylift_bg_a -> v003 (res/gfx/mission1_skylift_bg_a.png)
- ROM: build_v005 (sha256 22398477a18be069243b612daaa0e1b197cfae7d618353b900ab40a06a957e05, 262144 bytes)
- Validation: errors=0, warnings=2
- Blockers: changelog_missing
- Emulator evidence: rom_identity_mismatch

## 2026-04-17T10:51:44.3290851-03:00 - viewer_semantic_gate_refresh

- Task: viewer_semantic_gate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v005 (sha256 22398477a18be069243b612daaa0e1b197cfae7d618353b900ab40a06a957e05, 262144 bytes)
- Validation: errors=0, warnings=1
- Blockers: gameplay_gate_incomplete
- Emulator evidence: ok
- Notes: Sincronizacao canonica apos curadoria semantica do gate: viewer segue como laboratorio visual aprovado; gameplay_rom_aprovada e ready_for_aaa permanecem fechados.


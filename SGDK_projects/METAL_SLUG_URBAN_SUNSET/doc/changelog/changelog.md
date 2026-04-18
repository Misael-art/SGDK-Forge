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


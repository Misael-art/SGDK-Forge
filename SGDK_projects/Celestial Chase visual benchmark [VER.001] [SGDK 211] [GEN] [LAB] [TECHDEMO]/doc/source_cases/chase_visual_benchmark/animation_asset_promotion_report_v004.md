# Chase Animation Runtime Promotion v004

Date: 2026-06-03
Status: `promoted_to_res_pending_build`

## Human Approval Basis

- Animation strip candidate v003 approved by the user.
- Pipeline freeze released by user instruction.
- Quality rule preserved: no automatic dither, no post-process outlining, no unapproved sprite redraw.

## Runtime Residency Decision

- `resource_loading_model`: `fallback_reduced_residency`
- Background proof surface is tile-light to reserve VRAM for large 64x80 hero and modular pursuer sprites.
- Approved `runtime_split_candidates_v007` remains the art direction route for later composition tuning.

## Promoted Background

- `img_chase_anim_runtime_bg` -> `.\res\gfx\chase_anim_runtime_bg_v004.png`; unique tiles `258`

## Promoted Sprites

- `spr_chase_hero_run_toward` -> `.\res\sprites\chase\hero_run_toward_64x80_strip_v003.png`; cell `64x80`; frames `8`; unique tiles `404`
- `spr_chase_pursuer_body_zloop` -> `.\res\sprites\chase\pursuer_3q_front_mid_96x80_zloop_strip_v003.png`; cell `96x80`; frames `6`; unique tiles `261`
- `spr_chase_pursuer_head_zloop` -> `.\res\sprites\chase\pursuer_head_horns_112x64_zloop_strip_v003.png`; cell `112x64`; frames `6`; unique tiles `168`
- `spr_chase_pursuer_hoof_zloop` -> `.\res\sprites\chase\pursuer_attack_hoof_96x64_zloop_strip_v003.png`; cell `96x64`; frames `6`; unique tiles `163`
- `spr_chase_pursuer_dust_impact` -> `.\res\sprites\chase\pursuer_impact_dust_fx_64x32_strip_v003.png`; cell `64x32`; frames `6`; unique tiles `28`

## Runtime Contract

- Hero ticks: `4, 3, 3, 4, 4, 3, 3, 4`
- Pursuer ticks: `6, 5, 5, 7, 5, 5`
- Impact frame: `B3`
- Shake offsets: `+2, -2, +1, -1, 0`

## Blocking Statuses Still Active

- `not_rescomp_validated`
- `not_tested_in_emulator`

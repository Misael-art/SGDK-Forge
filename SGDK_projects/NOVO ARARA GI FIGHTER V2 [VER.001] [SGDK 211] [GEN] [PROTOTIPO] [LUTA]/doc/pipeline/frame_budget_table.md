# frame_budget_table

frame_w: 96
frame_h: 112
hardware_sprite_blocks_per_frame_estimate: up to 12 hardware sprites per fighter frame
active_animation_window: one state per fighter plus one transition state; full sheet not assumed resident.

| State | Frames | Runtime symbol | Timing target | Active frames |
|---|---:|---|---|---|
| idle | 6 | spr_caio_idle | 8 ticks/frame | none |
| walk_forward | 6 | spr_caio_walk_forward | 5 ticks/frame | none |
| walk_back | 6 | spr_caio_walk_back | 6 ticks/frame | none |
| dash | 4 | spr_caio_dash | 4 ticks/frame | frame 1-2 movement |
| crouch | 2 | spr_caio_crouch | held | none |
| jump | 6 | spr_caio_jump | state-driven | none |
| guard | 3 | spr_caio_guard | held / 5 ticks | block window all |
| jab | 4 | spr_caio_jab | 4 ticks/frame | frame 1-2 |
| medium | 5 | spr_caio_medium | 5 ticks/frame | frame 2-3 |
| grip | 5 | spr_caio_grip | 5 ticks/frame | frame 2-3 |
| hip_throw | 8 | spr_caio_hip_throw | 5 ticks/frame | frame 3-5 |
| hurt | 4 | spr_caio_hurt | 6 ticks/frame | none |
| knockdown | 6 | spr_caio_knockdown | 6 ticks/frame | none |
| getup | 6 | spr_caio_getup | 6 ticks/frame | invulnerable transition |

## Budget Decision Seed

Initial decision: cabe com recuo. Recuo is active_animation_window/per-state strips instead of one enormous always-resident sprite sheet. P1 and P2 share rig scale; P2 uses curated palette variant after P1 is accepted.
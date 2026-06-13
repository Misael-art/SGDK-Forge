# Animation Production Contract

Use this reference when an agent must create, audit, or expand character sprites with AI image generation. It turns "make a sprite sheet" into a deterministic animation production flow.

## Required artifacts before image generation

Do not generate character images before these exist:

- `animation_state_plan.md`: gameplay states, priority, loop policy and transitions.
- `pose_roster.md`: exact poses/keyframes to request from the image model.
- `frame_budget_table.md`: frame count, frame size and VBlank timing per action.
- `pivot_and_scale_contract.md`: frame box, pivot, ground/contact rule, camera, scale and invariant proportions.
- `asset_kind_declaration.md`: classify each image as `model_sheet`, `key_pose_sheet`, `animation_strip`, or `final_sprite_sheet`.
- `idle_breathing_cycle_contract.md`: required for hero/fighter/boss idle in AAA when the body is readable.
- `facial_expression_phase_map.md`: required for hero/fighter/boss/NPC faces in AAA when the face is readable.
- `cloth_secondary_animation_contract.md`: required when cloth, hair, sash, cape, jacket or loose accessory is visible in critical motion.
- `hand_pose_keyframe_contract.md`: required when hands, claws, grips, weapons or gestures are readable in 320x224.

If any artifact is missing, status is `blocked_animation_planning`.

## Asset kinds

Every produced image must declare one kind:

- `model_sheet`: locks identity. It is not animation.
- `key_pose_sheet`: one pose per action/state. It is not animation.
- `animation_strip`: one action only, sequential frames over time.
- `final_sprite_sheet`: assembly of accepted strips only.

Rules:

- `key_pose_sheet` can become a reference for strips, but never passes as `accepted_strip`.
- `animation_strip` must contain exactly one action. If it mixes idle, run, jump, attack or victory in one strip, status is `rejeitado_multi_action_sheet`.
- `final_sprite_sheet` cannot be created from unaccepted strips.

## Production passes

1. `model_sheet`: neutral stance front/side/back plus gameplay pose. Locks design.
2. `key_poses`: idle, locomotion extremes, crouch/jump, anticipation, contact, hurt, victory.
3. `animation_strips`: one action per generation request. No full sheet yet.
4. `full_sheet_assembly`: only after accepted strips.
5. `qa`: continuity, pivots, timing, overlays and budget.

Never generate a full production sheet before accepted model sheet and key poses.

## Continuity contract

Every frame in a strip must preserve:

- same character identity, outfit, palette, outline, lighting and pixel density
- same frame box and camera
- same head/hand/feet scale
- same `bottom_center_feet` pivot unless the action declares an airborne exception
- clear anticipation, contact/action and recovery where applicable

Reject if frames look like separate drawings instead of a movement.

## Motion phase map

Before every `animation_strip`, write `motion_phase_map.md` for that action.

Minimum shape:

```yaml
animation_id: run
frame_count: 8
phase_sequence:
  - frame: 1
    phase: contact
    note: front foot plants, torso compressed
  - frame: 2
    phase: down
    note: weight drops, rear leg passes
  - frame: 3
    phase: passing
    note: feet cross under body
  - frame: 4
    phase: up
    note: body rises, scarf/cape follows
```

For attacks, phases must include `ready`, `anticipation`, `windup`, `contact`, `follow_through`, and `recovery` as applicable.

Without `motion_phase_map`, status is `rejeitado_sem_motion_phase_map`.

## Character charisma sub-contracts

These contracts are conditional. They do not apply to every blob, drone or tiny enemy. They apply when `production_runtime_contract.target=AAA` and the profile is `hero`, `fighter`, `boss` or an expressive NPC.

Every contract includes:

- `applicability`: `required`, `warning`, or `not_applicable`
- `reason`: why it applies or why it is safely not applicable
- `frame_budget_impact_estimate`: extra frames/tiles or `no_new_frames_palette_or_subpixel_only`
- `measurement_level`: `declared`, `estimated`, `measured`, `emulator_verified`, or `vdp_dump_verified`

### `idle_breathing_cycle_contract`

Minimum fields:

- `breath_areas`: chest, shoulders, head, hair tip, cloth edge, weapon hand
- `cycle_length_frames`
- `inhale_frames`, `hold_frames`, `exhale_frames`
- `amplitude_per_area`
- `personality_modifier`: calm, tense, exhausted, arrogant, nervous, disciplined
- `loop_closure_rule`

Blockers:

- `idle_breathing_unspecified`
- `mechanical_breathing_loop`
- `breathing_breaks_scale_lock`

### `facial_expression_phase_map`

Minimum fields:

- `emotion_arc` per action or dialogue beat
- `eye_blink_pattern`
- `mouth_phoneme_set` when speech is visible
- `asymmetry_policy`: pain, effort, surprise, anger, charm
- `eyebrow_independence`
- `pain_keyframe_anchors`

Blockers:

- `facial_expression_phase_map_missing`
- `face_static_during_impact`
- `expression_unreadable_at_native`

### `cloth_secondary_animation_contract`

Minimum fields:

- `cloth_regions`: hair, sash, sleeve, jacket, cape, scarf, belt tail
- `delay_frames`
- `damping_curve`: linear, ease_out, spring, stepped
- `bounce_amplitude`
- `inertia_direction`
- `rest_pose`
- `critical_actions`

Blockers:

- `cloth_secondary_unspecified`
- `cloth_moves_before_body`
- `cloth_frozen_during_dash_or_fall`
- `cloth_budget_unbounded`

### `hand_pose_keyframe_contract`

Minimum fields:

- `hand_states`: fist_clenched, open_palm, pointing, grip_weapon, relaxed_curl, finger_spread, guard_hook
- `transitions` per action
- `finger_articulation_level`: low, medium, high
- `iconic_pose_references`: internal design anchors, not copied IP
- `readability_at_native`

Blockers:

- `hand_pose_keyframe_missing`
- `hand_shape_generic_across_actions`
- `weapon_or_grip_pose_unreadable`

## P0 state rosters

Fighting / beat-em-up:

| state | frames |
|---|---:|
| idle | 6 |
| walk | 6 |
| dash_or_step | 4 |
| crouch | 3 |
| jump | 5 |
| light_attack_A | 5 |
| medium_attack_B | 6 |
| heavy_or_grapple_entry | 7 |
| special_throw_or_skill | 8 |
| block | 3 |
| hurt | 3 |
| knockdown_getup | 8 |
| victory_or_taunt | 6 |

Platform/action:

| state | frames |
|---|---:|
| idle | 6 |
| run | 8 |
| jump | 5 |
| fall | 2 |
| landing | 3 |
| attack | 6 |
| ability_or_projectile | 6 |
| ledge_wall_or_glide | 3-6 |
| hurt | 3 |
| death_or_transform | 8 |

RPG top-down:

| state | frames |
|---|---:|
| idle_down_up_side | 1 each |
| walk_down_up_side | 3 each |
| talk | 2 |
| interact | 2 |
| battle_idle | 4 |
| attack | 6 |
| cast | 6 |
| hurt | 3 |
| victory | 5 |

## Strip prompt contract

Each strip prompt must specify:

- `animation_id`
- `frame_count`
- `frame_size`
- `asset_kind: animation_strip`
- `camera`
- `pivot`
- frame-by-frame motion notes copied from `motion_phase_map`
- continuity invariants
- grid layout and flat chroma/transparent background
- no text, watermark, copied IP, random redesign, blur, AA or smooth gradients

## Evidence required

For produced frames, save at least:

- `contact_sheet.png`
- `pivot_overlay.png`
- `frame_box_overlay.png`
- `onion_skin_overlay.png`
- `frame_delta_report.md`
- `animation_preview.gif` or numbered frame sequence

Without visual movement evidence, an animation cannot be accepted.

## Sprite strip integrity gate

Before any generated character strip is promoted to `data/processed/` or `res/`, run a frame-cell integrity audit and save `sprite_artifact_report`:

```bat
python tools\image-tools\analyze_sprite_strip_integrity.py ^
  --image "<project>\res\sprites\characters\<character>\<state>.png" ^
  --frame-width <pixels> ^
  --frame-height <pixels> ^
  --output "<project>\out\logs\sprite_artifact_<character>_<state>.json"
```

For character damage/impact states, add `--detect-baked-fx`.

Blockers:

- `FRAME_EDGE_CLIPPING`: visible pixels touch a frame boundary; enlarge/re-slice before SGDK promotion.
- `NON_INDEX0_BACKGROUND_MATTE`: a non-transparent matte color remains inside cells.
- `TRANSPARENCY_INDEX0_BACKGROUND_MISMATCH`: the background is not palette index 0.
- `SMALL_ISLAND_DEBRIS`: stray disconnected fragments or cleanup debris remain around the body.
- `STRAY_LARGE_COMPONENT`: significant disconnected mass remains outside the main body; this usually means a neighboring pose leaked into the cell.
- `SCALE_INCONSISTENCY`: the body scale drifts beyond the declared tolerance.
- `BAKED_FX_IN_CHARACTER_SHEET`: hit spark or impact VFX is baked into the character sheet.

These blockers produce `needs_review` or `rework`; they cannot be hidden inside a larger atlas or excused because the ROM compiles.

## Slicing Cell Contract

Every large fighter, boss, or hero character strip must include `slicing_cell_contract` before promotion:

- `cell_width`, `cell_height`, `tile_width`, `tile_height`
- `source`: `max_bbox_plus_padding`, `fixed_manifest_cell`, or `manual_curated_cell`
- `padding_left/right/top/bottom`
- `ground_y`, `pivot_x`, measured foot/contact policy
- `reason` when a fixed cell is used

`FRAME_W` / `FRAME_H` constants in a builder are only implementation detail. They are not acceptance evidence unless the contract explains why the fixed cell safely contains every pose.

## Adjacent frame QA

Every strip must compare frame N to frame N+1.

- too low delta: frames are almost identical and do not animate
- acceptable delta: limbs, cloth, face or action shape move while mass and identity stay stable
- too high delta: it looks like a different pose, action or character

If adjacent deltas do not read as temporal continuation, status is `rejeitado_sem_frame_delta`.

## QA additions

Use these metrics with threshold 8 for acceptance:

- `pose_continuity`
- `volume_consistency`
- `pivot_consistency`
- `frame_flow_readability`
- `adjacent_frame_delta`
- `gameplay_state_coverage`

Statuses:

- `accepted_key_pose_sheet`
- `accepted_strip`
- `revisar_frame_roster`
- `rejeitado_multi_action_sheet`
- `rejeitado_sem_motion_phase_map`
- `rejeitado_sem_frame_delta`
- `rejeitado_sem_preview_animado`
- `rejeitado_sem_fluxo_animacao`
- `rejeitado_placeholder`
- `blocked_animation_planning`

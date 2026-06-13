# Premium Motion Direction Contract

Use this reference for hero characters, fighting-game casts, bosses and any animation that claims arcade, premium or AAA quality.

This contract does not replace `animation_production_contract.md`. It adds art direction for motion performance: timing, spacing, force, impact, recovery, lighting motion and modular rigs.

## Required artifact

Before requesting or accepting any premium `animation_strip`, create `animation_direction_contract`.

Minimum fields per action:

```yaml
animation_id: medium_attack
gameplay_role: mid range strike, punishable on whiff
motion_archetype: compression -> burst -> recovery
frame_count: 6
startup_frames: [1]
anticipation_frames: [1, 2]
active_frames: [3]
smear_frames: [3]
hitstop_hold_frame: 3
recovery_frames: [4, 5, 6]
root_foot_policy: rear foot locks until recovery, front foot advances on active
center_of_mass_curve: back 3px, forward 9px, return 4px
silhouette_peak_frame: 3
impact_readability: fully extended limb, clear torso twist, readable contact line
shading_motion: highlights and shadows travel with torso and limb rotation
fx_policy: hit spark, dust and flash are separate runtime assets, not baked into character sheet
palette_flash_policy: optional CRAM/runtime flash, never uncontrolled requantization
```

If this artifact is missing for a critical action, status is `blocked_motion_direction_contract`.

## Character life contracts

Premium motion is not only attack anatomy. A memorable Mega Drive character needs quiet motion, expressive face shapes, readable hands and secondary motion that lags behind the body.

Use these sub-contracts when applicable:

- `idle_breathing_cycle_contract`
- `facial_expression_phase_map`
- `cloth_secondary_animation_contract`
- `hand_pose_keyframe_contract`

Each one must declare `applicability`, `reason`, `frame_budget_impact_estimate` and `measurement_level`. If a project is AAA and the character is a hero, fighter, boss or expressive NPC, a missing applicable contract becomes a blocker. In prototype/lab mode these contracts may be warnings, but the warning must stay visible in the report.

### Idle breathing

Idle is a personality loop, not just a technical loop.

- Calm characters breathe slow with low shoulder amplitude.
- Tense fighters keep chest and guard active with shorter holds.
- Exhausted characters drop shoulders and recover slower.
- Arrogant characters may move head or weapon more than torso.

Blockers:

- `idle_breathing_unspecified`
- `idle_loop_mechanical`
- `personality_not_reflected_in_idle`

### Facial expression and asymmetry

The face must support effort, pain, speech and attitude when it is readable at native resolution.

- Pain and effort may be asymmetrical.
- Blinks should not be regular clock ticks unless the character is mechanical.
- Mouth shapes for dialogue/cutscene must be limited but intentional.

Blockers:

- `facial_expression_phase_map_missing`
- `static_face_on_hitstop`
- `speech_without_mouth_plan`

### Cloth and secondary motion

Cloth, hair, belts and loose parts should follow the body with delay, damping and return.

- Dash pulls cloth backward after the body starts moving.
- Landing/knockdown creates bounce and settle.
- Recovery lets cloth finish after the torso returns.

Blockers:

- `cloth_secondary_unspecified`
- `secondary_motion_breaks_budget`
- `cloth_frozen_during_critical_motion`

### Hand pose keyframes

Hands sell intent: grip, throw, guard, strike and personality.

- Fingers can be low-detail, but the pose family must change.
- Grips and throws need a readable hand state.
- Iconic poses must be authored, not copied.

Blockers:

- `hand_pose_keyframe_missing`
- `hand_shape_generic_across_actions`
- `grip_or_weapon_pose_unreadable`

## Timing and spacing rules

Animation quality comes from timing distribution, not frame count alone.

- Light attacks may use short anticipation, but never start directly on the active hit frame.
- Medium and heavy attacks require visible anticipation before active frames.
- The active hit is fast: usually 1 or 2 frames.
- Recovery is slower than the hit: the body pays inertia before returning to idle.
- Identical timing for every frame is an anti-pattern unless the action is intentionally mechanical.

Acceptance checks:

- `timing_spacing_report` declares startup, anticipation, active, follow-through and recovery in VBlanks.
- `recovery_curve_report` proves the character does not snap back to idle.
- `impact_frame_contract` identifies the frame that will be held during hitstop.
- `hitstop_hold_frame` must be visually clean, unclipped, strongly silhouetted and readable at 320x224.

## Strike anatomy

Attacks must show force through the whole body.

- Anticipation compresses muscle, shifts weight and prepares inertia.
- Active frames extend the damaging limb or weapon with clear line of action.
- Smear frames are intentional drawn motion, not debris, blur or palette noise.
- Recovery shows deceleration, gravity and posture repair.
- Root foot and center of mass must be coherent with the gameplay role.

Blockers:

- `attack_starts_on_active_frame`
- `missing_anticipation`
- `missing_recovery`
- `hitstop_frame_weak`
- `smear_noise_not_motion`
- `root_foot_sliding_unjustified`
- `center_of_mass_jump`
- `pose_sequence_reads_as_unrelated_drawings`

## Damage reaction

Impact must be readable before SFX or camera shake.

- Hurt frames declare force direction.
- The first damage frame may use slight squash/stretch, but must keep identity and scale.
- Heavy damage breaks posture: knees, spine, shoulders and arms react to the hit.
- Knockdown/getup must preserve scale lock and ground contact logic.
- The selected hitstop frame must be the best-looking frame, because the engine may freeze it briefly.

Required artifacts:

- `hit_reaction_contract`
- `impact_frame_contract`
- `hitstop_hold_frame`
- `force_direction`
- `posture_break_notes`

## Shading motion and palette rigor

Pixel art lighting is topology, not a filter.

- Highlights and shadows must move with the rotating body or material.
- Do not only move the outline while the light stays pasted in place.
- White or light fabric must preserve hue-shifted cool shadows and clean highlights.
- Flash frames are a runtime/CRAM or explicitly separated art decision, not accidental quantization.
- FX colors must not silently steal material slots from the character palette.

Required artifacts:

- `shading_motion_report`
- `palette_flash_policy`
- `palette_domain_report` when FX, P2 palette or HUD share CRAM space

Blockers:

- `static_shading_on_rotating_body`
- `muddy_requantized_flash`
- `fx_palette_coupled_to_character_without_contract`
- `white_material_palette_contract_failed`

## Modular boss and giant sprite logic

When a boss, vehicle, creature or setpiece exceeds a sane frame-by-frame budget, do not request giant full-body frames as the default.

Use `modular_boss_rig_contract`:

- parts: head, torso, shoulder, upper_arm, forearm, hand, weapon, core, etc.
- pivot for each joint
- parent/child relationship
- local palette domain
- maximum tiles per part
- active pose budget
- runtime articulation model

Rules:

- Each part needs its own pivot and bounding box.
- Large parts must be budgeted as separate sprites/metasprites.
- Runtime may animate joints, but the art contract must provide clean pieces and readable rest poses.
- A full-body reference can guide the rig, but should not be the shipped frame strategy when it overflows VDP budget.

Blockers:

- `giant_single_sheet_without_budget`
- `missing_joint_pivots`
- `modular_part_palette_conflict`
- `boss_active_window_over_budget`

## Acceptance summary

A premium action strip passes only when it answers:

- Where does the body accumulate energy?
- Where exactly does damage happen?
- Which frame will hitstop hold?
- How does the body pay inertia during recovery?
- Does the pivot/foot/center-of-mass curve make sense?
- Does light move with volume?
- Does smear improve readability instead of becoming debris?
- Does the runtime have a timing map to reproduce the intended feel?

If these questions are not answered, the strip is `needs_review` even when the PNG is clean and the ROM builds.

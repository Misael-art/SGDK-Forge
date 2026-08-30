# sprite-scanline-budgeter

Use when a project has large sprites, bosses, crowds, projectiles, beat 'em up enemies, fighting-game characters or any scene at risk of sprite flicker/cutoff.

## Purpose

Translate sprite ambition into Mega Drive SAT and scanline limits before art or runtime code is approved.

## Required Inputs

- Sprite dimensions in 8x8 tile units.
- Expected on-screen counts.
- Animation poses with maximum horizontal spread.
- Priority and palette assignments.
- Collision/hurtbox plan when sprites are decomposed.

## Required Outputs

- Worst-case sprites per scanline estimate.
- Worst-case sprite pixels per scanline estimate.
- Decomposition plan for large bodies, limbs, weapons and FX.
- Flicker, dropout or priority risks.
- Optional flicker/multiplexing policy when limits cannot be avoided: which
  sprites rotate priority, cadence, fairness rule and gameplay readability risk.

## Hard Rules

- Do not approve a boss, fighter or crowd from total sprite count alone.
- Check per-scanline density.
- Split large animated characters into stable parts only when the runtime can keep SAT order, priority and hitboxes coherent.
- Treat temporal multiplexing/flicker as controlled degradation, not an
  optimization victory. It needs a design reason, a priority rotation policy and
  evidence that critical targets remain readable.
- Never flicker player hurtboxes, active hitboxes, telegraphs or mandatory UI.
- If evidence is missing, report `sprite_scanline_budget_unproven`.

## Candidate Curation Note

Source: attached graphical-tricks transcript summary reviewed on 2026-06-17,
`E1_text`. The retained improvement is stricter handling of sprite multiplexing:
rotating visibility may preserve perceived density, but it must be budgeted,
fair, non-critical and validated in motion.

## Handoff

- Use `articulated-sprite-architect` for multi-part bodies.
- Use `collision-system-architect` for hit/hurt/push box coherence.
- Use `megadrive-vdp-budget-analyst` for final hardware budget review.

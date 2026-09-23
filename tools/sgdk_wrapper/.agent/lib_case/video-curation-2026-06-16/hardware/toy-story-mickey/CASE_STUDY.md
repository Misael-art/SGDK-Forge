# Case Study: Toy Story / Mickey Mania

- title: Toy Story / Mickey Mania visuals
- batch_id: curation_batch_2026_06_16
- evidence_grade: E1_text
- source_status: agent_aggregate_summary_or_direct_label_only
- nearest_owner_skills: megadrive-vdp-budget-analyst, software-tile-rasterizer, shadow-highlight-scroll-fx, hscroll-linescroll-road-fx
- canonical_promotion: false

## observed_techniques

- Pre-rendered / pseudo-3D set-piece visuals as labeled by the source. Only the
  label is available; exact techniques, frames or budgets were not provided and
  are not invented here.

## why_not_new_skill

- Pre-render and pseudo-3D tile rewrite are already owned by
  `software-tile-rasterizer` (bounded) and `megadrive-vdp-budget-analyst`.

## applicable_lessons

- Pre-rendered "3D look" is software tile rewrite + DMA, never native scaling;
  it must fit a measured per-frame budget.

## required_followups_before_production

- A per-frame DMA/CPU budget plus screenshot and VDP dump evidence before any
  production or visual-quality statement.

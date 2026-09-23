# Causal persistence cycle - 2026-09-03

- Previous blocker: `native_pixel_authorship_producer_unavailable` for new
  native Kirby animation pixels; global status was too narrow when applied to
  unrelated branches.
- Hypothesis: an explicitly encoded logical 32x32 grid could provide a safe,
  measurable producer route without treating a high-resolution illustration as
  native art.
- Causal change: prepared one R1-bound production reference and made exactly
  two materially distinct producer attempts; no post-processing rescue was
  allowed.
- New evidence: attempt 01 measured as 1254x1254 RGB, non-divisible by 32,
  non-uniform blocks and 28285 colors. Attempt 02 returned
  `HTTP 400 moderation_blocked` at output.
- Blocker reduced/removed: the limited `native_grid_encoded` hypothesis is now
  conclusively closed after its two-attempt budget. The external producer
  blocker is scoped to new native pixel authorship only.
- Independent progress: persisted a complete source/runtime/staging inventory,
  per-file active hashes, runtime consumers, and branch-level next actions;
  ran provenance, measurement, VDP, and project-context audits.
- Next step: continue only existing independent non-character work or wait for
  an authorized human/native-pixel producer. Do not generate another high-res
  guide, do not create v10, and do not promote to `res/`, runtime, or ROM.

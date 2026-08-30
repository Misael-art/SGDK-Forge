# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when `sgdk-code-reviewer` reviews code implementing advanced visual/runtime techniques.

## New Review Targets

- Function-pointer vtables and entity catalogs from `entity-polymorphism-architect`.
- Transition locks, fade/flush cleanup and re-entry guards from `game-state-transition-architect`.
- DMA queue ownership and dirty tile uploads from `vram-streaming-dma-queue`.
- Software tile rasterizer loops and upload size.
- Z80/audio boundary assumptions.

## Review Rules

- Prioritize bugs, corruption risk, VBlank misuse, API mismatch and missing evidence.
- Treat unbounded DMA, state re-entry and palette ownership collisions as high-risk.
- Do not accept "works in build" as runtime proof.

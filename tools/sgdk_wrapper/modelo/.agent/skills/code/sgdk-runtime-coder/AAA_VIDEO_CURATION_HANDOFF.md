# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when `sgdk-runtime-coder` implements gameplay/runtime code related to advanced Mega Drive techniques.

## New Required Routes

- Route entity catalogs and behavior dispatch to `entity-polymorphism-architect`.
- Route scene/state changes to `game-state-transition-architect`.
- Route tile streaming and runtime graphics uploads to `vram-streaming-dma-queue`.
- Route CPU-rendered tile effects to `software-tile-rasterizer`.

## Runtime Rules

- Do not implement large switch-case enemy catalogs when a static function-pointer plan is required.
- Do not change state during active fade/flush without a transition mutex.
- Do not perform unbounded VRAM updates outside a declared DMA queue.
- Keep SGDK 2.11 API claims verified against headers before implementation.

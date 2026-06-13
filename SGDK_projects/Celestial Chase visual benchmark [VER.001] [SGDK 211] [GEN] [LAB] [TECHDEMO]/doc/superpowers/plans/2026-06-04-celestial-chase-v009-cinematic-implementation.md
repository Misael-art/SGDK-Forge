# Celestial Chase v009 Cinematic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the visually invalid v008 chase composition with a source-derived, modular and budgeted v009 cinematic runtime.

**Architecture:** Scene-owned VDP composition drives a fixed cosmic background and pseudo-3D road, while focused gameplay modules own the hero afterimages, modular pursuer rig, animated FX and compact HUD. All advanced effects use fixed-point or integer math and VBlank-safe SGDK operations.

**Tech Stack:** SGDK 2.11 C, ResComp, indexed PNG assets, project-local Pillow builder, PowerShell wrapper, BlastEm.

---

### Task 1: Canonize v008 Failure And v009 Contracts

**Files:**
- Modify: `doc/project_methodology_manifest.json`
- Modify: `doc/technique_usage_manifest.json`
- Modify: `doc/tdd_contract.json`
- Modify: `doc/13-spec-cenas.md`
- Create: `doc/agent_learning/failure_patterns.md`

- [ ] Mark `road_physics` and `modular_boss` as required claims with measurable runtime symbols.
- [ ] Add v009 selected techniques, owners, budgets and fallbacks to the TDD application plan.
- [ ] Record the v008 visual failure as a permanent anti-pattern before correcting assets.
- [ ] Validate methodology and hygiene.

### Task 2: Build Source-Derived v009 Assets

**Files:**
- Modify: `data/builders/build_chase_first_playable_assets.py`
- Modify: `res/resources.res`
- Create: `res/sprites/chase/hero_run_toward_64x80_strip_v009.png`
- Create: `res/sprites/chase/hero_ghost_64x80_strip_v009.png`
- Create: `res/sprites/chase/pursuer_torso_96x80_strip_v009.png`
- Create: `res/sprites/chase/pursuer_head_80x64_strip_v009.png`
- Create: `res/sprites/chase/pursuer_claw_64x48_strip_v009.png`
- Create: `res/sprites/chase/chase_energy_star_32x32_strip_v009.png`
- Create: `res/sprites/chase/chase_pulse_impact_64x48_strip_v009.png`
- Create: `res/sprites/chase/chase_cloud_64x32_strip_v009.png`
- Create: `res/gfx/chase/chase_letterbox_tile_v009.png`

- [ ] Reserve index 0 and snap the runtime palettes to the 9-bit grid.
- [ ] Curate the hero cycle from valid source-baked frames only.
- [ ] Derive ghost, modular rig, cloud and FX strips from project-local approved sources.
- [ ] Generate contact sheets, palette strips and a v009 translation report.
- [ ] Run the art diagnostic and pixel/index validation.

### Task 3: Implement Pseudo-3D Composition

**Files:**
- Create: `inc/gameplay/chase_road.h`
- Create: `src/gameplay/chase_road.c`
- Modify: `src/scenes/scene_chase.c`

- [ ] Add deterministic road HScroll and two-tile VScroll tables.
- [ ] Keep `BG_B` fixed and move source-derived cloud sprites diagonally.
- [ ] Add safe palette cycling and contextual Shadow/Highlight ownership.
- [ ] Add climax top/bottom cinematic framing with symmetric teardown.
- [ ] Verify that all table and CRAM updates are queued for VBlank.

### Task 4: Implement Hero Motion And Modular Pursuer

**Files:**
- Modify: `inc/gameplay/chase_player.h`
- Modify: `src/gameplay/chase_player.c`
- Modify: `inc/gameplay/chase_pursuer.h`
- Modify: `src/gameplay/chase_pursuer.c`

- [ ] Replace the invalid eight-frame hero runtime cycle with the corrected four-frame cycle.
- [ ] Add two delayed dithered afterimages during lane movement and Pulse.
- [ ] Replace the monolithic pursuer with torso, head and two claw sprites.
- [ ] Update rig nodes in parent-before-child order using fixed-point/LUT motion.
- [ ] Animate Pulse expansion, energy star and impact response.
- [ ] Prune nonessential rig/ghost sprites when pressure exceeds the scanline target.

### Task 5: Compact HUD And Gameplay Integration

**Files:**
- Modify: `src/gameplay/chase_hud.c`
- Modify: `src/gameplay/chase_obstacles.c`
- Modify: `src/scenes/scene_chase.c`

- [ ] Reduce the HUD to a compact two-row fixed surface.
- [ ] Animate pickups using the v009 star strip.
- [ ] Synchronize Pulse, rig recoil, hitstop, shake and palette state.
- [ ] Preserve pause/result/restart/menu behavior and full display teardown.

### Task 6: Build, Budget And Emulator Proof

**Files:**
- Modify: `doc/budget_inputs/chase_dma_queue.json`
- Modify: `doc/07-budget-vram-dma.md`
- Modify: `doc/10-memory-bank.md`
- Modify: `doc/changelog/changelog.md`

- [ ] Run canonical build and resource validation.
- [ ] Generate VRAM residency, DMA queue and sprite scanline reports.
- [ ] Fix any compiler, resource, overlap or budget regression.
- [ ] Run the current ROM in BlastEm and capture active gameplay, Pulse and result evidence.
- [ ] Run scene regression, freshness, closeout and mastering.
- [ ] Record technical and perceptual status separately; do not infer human approval.


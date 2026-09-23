# Celestial Chase v009 Cinematic Design

## Status

- Design source: corrective visual direction supplied by the user on 2026-06-04.
- Approval: treated as locked because the user explicitly defined the v009 cinematic target and rejected the v008 result.
- Delivery ceiling: `vertical_slice_candidate`; no AAA or ready claim without fresh BlastEm and human perceptual approval.

## Problem Statement

ROM v008 is technically stable but visually invalid. It exposes opaque matte around FX, broken hero anatomy, a flat full-body pursuer, inverted depth motion, washed palette contrast and a composition dominated by empty or globally-colored regions. Those failures block the intended 1990s anime chase fantasy.

## Selected Route

Use a safe cinematic VDP route built from the approved project-local source package:

- remaster index-zero transparency and CRAM contrast before runtime work;
- replace invalid hero frames with a curated source-baked cycle and add dithered afterimages during lateral movement;
- split the pursuer into torso, head and claws, then animate the parts through forward kinematics and pre-rendered scale frames;
- keep moon and deep stars fixed on `BG_B`, while source-derived cloud sprite grafts move diagonally at a slow ratio;
- deform the road through `HSCROLL_LINE` plus `VSCROLL_2TILE`, so lower road regions move faster than the horizon;
- animate energy and Pulse FX through real frame strips;
- use safe VBlank-queued CRAM/VSRAM updates, contextual Shadow/Highlight and deterministic hitstop/shake;
- use `WINDOW` for the fixed top HUD and a scene-owned BG_A bar for the lower climax letterbox.

## Rejected Or Deferred Routes

- `cram_overdrive_midline`: deferred. It is a laboratory-only active-display write and conflicts with the workspace delivery rule that DMA remains VBlank-safe.
- monolithic full-body pursuer scaling: rejected because it cannot communicate articulation, weight or spatial attack.
- globally scrolling `BG_B`: rejected because it makes distant objects move faster than the road and breaks depth.
- procedural replacement art: rejected as final art. Builders may only remaster or derive animation from project-local source-baked assets.

## Architecture

### Scene Ownership

- `scene_chase.c`: owns VDP modes, plane composition, road tables, palette timeline, cinematic framing and teardown.
- `chase_player.c`: owns the hero, afterimage history and animation timing.
- `chase_pursuer.c`: owns the modular rig, Pulse/impact FX and camera shake request.
- `chase_obstacles.c`: owns lane objects, pickup animation and telegraph visibility.
- `chase_hud.c`: owns the fixed `WINDOW` surface and compact HUD.
- asset builder: owns deterministic source-derived v009 assets and visual reports.

### Display Contract

- `BG_B`: fixed cosmic sky, moon and deep stars. No plane scroll.
- `BG_A`: road structure, line deformation and lower cinematic bar.
- `WINDOW`: fixed top HUD and expanded top letterbox during climax.
- Sprites: hero, afterimages, modular pursuer, clouds, threats and FX.
- H-Int: unused in v009 safe route.
- Shadow/Highlight: scene-owned and used contextually for Pulse/climax only.

### Road Motion

- A 224-entry horizontal scroll table bends the road using an integer Z gain and a slow curve phase.
- A 20-entry vertical two-tile scroll table advances road texture faster near the screen edges and slower near the vanishing point.
- Camera shake is composed into both tables without moving the fixed HUD.
- `BG_B` stays fixed; cloud sprite grafts provide the only distant diagonal motion.

### Pursuer Rig

- Root torso is the parent.
- Head and two claws are child nodes updated in topological order.
- Angles use fixed-point SGDK sine/cosine helpers or deterministic LUTs.
- Scale is represented by the existing six pre-rendered frames.
- Hidden/far parts are pruned from the active SAT set when they do not improve the silhouette.

## Asset Corrections

- Reserve palette index 0 as transparent/global deep black for every scene asset.
- Generate four-frame animated energy star and six-frame expanding Pulse strips from the project-local source FX.
- Build a four-frame hero cycle only from anatomically valid source-baked frames.
- Build a dither-masked ghost strip from the corrected hero cycle.
- Build torso/head/claw modular strips from the approved pursuer source-baked strips.
- Build two source-derived cloud frames using the `BG_B` palette.
- Snap palette colors to the Mega Drive 9-bit grid and increase separation between deep black, indigo, ivory and gold.

## Performance And Fallback

- Target remains 60 FPS NTSC.
- Maximum 20 sprites per scanline and 80 SAT links.
- Large sprite frame uploads remain alternated across frames.
- All per-frame VRAM/CRAM/VSRAM changes use SGDK queued VBlank operations.
- If the modular rig exceeds scanline or DMA budget, prune the far claw first, then one afterimage, then cloud grafts. Do not return to a monolithic pursuer.
- If Shadow/Highlight harms sprite readability, disable it while preserving palette, road and rig improvements.

## Evidence Gates

- Pixel/index audit for every v009 PNG.
- ResComp/resource validation and VRAM residency report.
- DMA queue plan including road tables, VSRAM, sprites and palette changes.
- Sprite scanline pressure report for hero + rig + obstacles + FX.
- Fresh BlastEm screenshot of active gameplay, Pulse impact and result state.
- Fresh SRAM and runtime metrics tied to the same ROM hash.
- Human review remains required for anatomy, motion, composition and cinematic impact.


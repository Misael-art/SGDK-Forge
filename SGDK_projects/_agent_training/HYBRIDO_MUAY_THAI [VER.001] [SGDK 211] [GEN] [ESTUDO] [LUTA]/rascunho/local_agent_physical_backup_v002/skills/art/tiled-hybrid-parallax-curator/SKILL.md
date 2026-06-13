---
name: "tiled-hybrid-parallax-curator"
description: "Builds Mega Drive-ready scenes from Tiled JSON plus background and overlay plates. Invoke when a case mixes tilemaps, flip flags, parallax layers, and occlusion art."
---

# Tiled Hybrid Parallax Curator

Use this skill when the scene is not pure tileset and not pure panorama.

Typical triggers:
- `map.json` from Tiled plus `tileset.png`
- painterly or panoramic plates: back, middle, fog, canopy, horizon, occluder
- Tiled flip flags need decoding
- rebuild of Mega Drive compatible composition and SGDK ROM proof

Core procedure:
1. Audit the asset package: dimensions, tile size, columns, gid ranges, Tiled flip flags, palette and alpha per plate.
2. Classify layers: back plate as BG_B, world plate as tilemap, occlusion plate, collision/support plate only.
3. Rebuild the world board: decode gids after masking flip flags, apply transforms, render full RGBA world board, count unique logical tile ids and transformed placements.
4. Choose the hero camera: scan 320x224 windows, balance composition, avoid empty areas, overfilled areas and dead repetition.
5. Translate to Mega Drive layers: BG_B distant where possible, merge crop plus occlusion into BG_A proof, use semantic extraction for matte-backed occlusion, snap RGB to `/34`, keep each plane inside palette budget.
6. Generate proof artifacts: world reconstruction, hero crop, BG_B proof, BG_A proof, final `virtual_proof.png`, metrics JSON.
7. Judge the proof like a scene artist: reject opaque strips, sky band loss, dead voids, matte support plates and IoU-only approvals that hide composition failures.
8. Promote to ROM proof when needed: SGDK resources, BG_B/BG_A setup and minimal parallax.

## Contrato Operacional

### Entrada minima

- Tiled JSON and tileset package, or an equivalent scene package with plates.
- Target scene window and expected Mega Drive resolution.
- Existing GDD/TDD or scene spec when this is part of an active project.
- Any collision, occlusion or support-only layer declarations available in the source.

### Saida minima

- Source audit with tile size, gid ranges, flip flag handling, palette and alpha findings.
- Layer classification for BG_B, BG_A, occlusion, collision/support and fallback.
- Reconstructed world proof and selected hero crop.
- Mega Drive layer plan with palette risk and tile uniqueness notes.
- Proof artifacts list and blockers for ROM promotion.

### Passa quando

- Tiled flip flags are decoded before counting or rendering tiles.
- Visual layers and support-only layers are not flattened into the same output by accident.
- The selected camera crop has composition value and is not approved by overlap metrics alone.
- Palette, tile and plane risks are explicit before runtime.
- ROM promotion is blocked until the proof artifacts are reviewed and budgeted.

### Handoff

- Send the layer plan to `multi-plane-composition` when plane ownership needs review.
- Send palette, tile and DMA risks to `megadrive-vdp-budget-analyst`.
- Send accepted proofs to `art-translation-to-vdp` or the project converter/builder.
- Send ROM-ready decisions to `sgdk-runtime-coder` only after blockers are resolved.

## Validation

- Never ignore diagonal gid flags.
- Never flatten collision art unless explicitly visual.
- Never exceed palette budget.
- Never approve opaque border or matte slab artifacts.
- Never let IoU hide composition failures.
- Prefer deterministic reconstruction.
- If the grammar is reusable, capture it as local learning before proposing canonical promotion.

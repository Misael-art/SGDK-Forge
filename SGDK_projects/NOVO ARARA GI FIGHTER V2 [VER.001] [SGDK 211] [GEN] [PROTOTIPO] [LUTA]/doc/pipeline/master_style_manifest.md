# master_style_manifest

style_anchor_id: novo_arara_gi_fighter_v2_arcade_bjj_001
date: 2026-05-13

## Visual Target

Arcade 2D fighting game presence on Mega Drive: large readable fighters, strong outlines, grounded athletic poses, rich but hardware-aware color, and clean separation between fighters and a cold/warm night stage.

## Technical References

- Streets of Rage 2: inherited only for strong 16-bit body volume and readable street-night contrast.
- Eternal Champions: inherited only for large Genesis fighting-game character presence and HUD density awareness.
- Shinobi III: inherited only for clean foreground/background separation and disciplined hard pixel readability.

No reference provides source pixels, poses, stage layout, palette, timing, or silhouette.

## Character Scale

- Target frame envelope: 96x112 px.
- Runtime visible character mass: approximately 78-92 px tall.
- Pivot: bottom center, x=48, ground_y=104.
- Max animation state width: 96 px, one horizontal strip per action.

## Palette Story

PAL0/BG_B: cold blue, violet, dark navy, reduced contrast.
PAL1/BG_A: arena blue/green tatame, warm bulbs, rail silhouettes.
PAL2/Fighters: Caio white gi ramp with cool blue/purple shadows, navy rashguard, skin ramp, green/yellow patches.
PAL3/HUD: high contrast formal UI, black/dark backing, white/yellow/red/blue accents.

## White Material Contract Summary

White gi is not pure flat white. It uses cold shadow, blue-violet folds, warm midtone, clean highlight, and a hard dark outline.

## Line And Lighting

- Line weight: 1-2 px hard pixel outline at sprite scale.
- Light direction: warm top-left/top-center arena bulbs.
- Shadow direction: cool lower-right and inner fold shadows.
- Drift limit: assets that change face structure, gi silhouette, pivot, or lighting beyond 15 percent are rework.
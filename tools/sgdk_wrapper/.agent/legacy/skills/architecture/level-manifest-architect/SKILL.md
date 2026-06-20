# level-manifest-architect

Use when a level, scene, arena or stage needs a manifest tying together art, collision, camera, entities, palettes, audio and runtime gates.

## Purpose

Stop levels from being assembled as disconnected assets. A level manifest is the contract that binds visual ambition to SGDK resources, camera rules, spawn tables and validation evidence.

## Required Inputs

- Scene goal and gameplay role.
- Background and sprite assets.
- Camera constraints.
- Collision topology.
- Entity spawn requirements.
- Audio and transition requirements.

## Required Outputs

- Level manifest with asset ownership.
- Camera and plane composition rules.
- Required skill gates for the level.
- Runtime evidence checklist.

## Hard Rules

- Do not approve a level by screenshot alone.
- Do not let camera, collision and art use different coordinate truths.
- Do not add assets not declared in the manifest.

## Handoff

- Use `multi-plane-composition` for BG planes.
- Use `collision-system-architect` for collision.
- Use `entity-polymorphism-architect` for spawn/runtime behavior.
- Use `emulator-vdp-evidence-curator` for closeout.

# articulated-sprite-architect

Use when a character, boss, vehicle, weapon, tail, arm, limb chain or set-piece is built from multiple linked sprites.

## Purpose

Convert "large impressive sprite" ambition into a stable hierarchy of parts that respects SAT order, scanline density, animation timing and gameplay hitboxes.

## Required Inputs

- Part list and parent-child relationship.
- Anchor points in pixel coordinates.
- Animation timeline.
- Sprite priority and palette plan.
- Collision/hurtbox ownership.

## Required Outputs

- Articulation tree.
- Local/global transform update order.
- SAT ordering and priority risks.
- Hit/hurt/push box sync notes.

## Hard Rules

- Do not build articulated sprites by visual offsets alone.
- Do not let anchor drift change collision truth.
- Do not approve a multi-part boss without scanline budget review.

## Handoff

- Use `sprite-scanline-budgeter` for hardware limits.
- Use `collision-system-architect` for gameplay boxes.
- Use `entity-polymorphism-architect` for runtime behavior ownership.

# Benchmark Usage Policy

## Purpose

Benchmarks are technical references, never source art, clone recipes, or prompt commands. They may guide scale, density, timing, staging, material readability, palette pressure, budget, and quality bar.

## Allowed

- compare sprite silhouette readability in 320x224
- compare motion timing categories such as startup, active, hitstop, recovery
- compare tile density and reuse pressure
- compare palette role and material contrast
- compare audio channel priority and event timing

## Live scene bar

Live-scene handles are quality-bar pointers, not source art:
`RheoGamer`, `PigsyRetro`, `GabrielPyron`, `ReySilveira28`, `RDiggoSilva`,
`MXRetroDev`, `birt_shannon`, `danielmoura79`.
Allowed: scale, density, palette-as-budget, shared roster CRAM chart,
tile-ceiling restage (~980 BG+FG), second-pass stage conversion, 320x224
4:3 as gate, metasprite stability, shadow/highlight, enhanced 8-bit,
9-bit ramp curation, YM2612 identity translation, DMA+music as one budget,
honest FPS, HAMOOPIG fight contract, motion proof.
Blocked: their sprites, stages, palettes, HUD, PCM, characters, or any IP
they ported (KOF, Fatal Fury, Metal Slug, SotN, Shinobi, Mario, Pocket
Bravery, Final Fight, SSF2, Art of Fighting) under `data/source_art` or
in a prompt as a copy command.
Doctrine: `doc/03_art/18_live_scene_bar.md`.

## Blocked

- copying pose, silhouette, stage layout, palette identity, UI identity, character identity, or IP symbols
- using a game, studio, artist, or IP name as a direct prompt command
- storing benchmark pixels under `data/source_art`
- promoting a recolor as authorial art
- name-dropping Rheo/Pigsy without applying the 12 shared checks

## Required Reports

- `source_validity_report`
- `authoriality_gate_report`
- `clone_risk_report`
- `authorial_consistency_report.json`
- `style_drift_report.json` when project style shifts

## Minimal Example

```json
{
  "benchmark_id": "genre_sprite_quality_bar",
  "allowed_use": ["scale", "timing", "density"],
  "blocked_use": ["silhouette_copy", "palette_copy", "layout_copy"],
  "max_similarity": 0.35,
  "measurement_method": "declared_clone_risk_method"
}
```

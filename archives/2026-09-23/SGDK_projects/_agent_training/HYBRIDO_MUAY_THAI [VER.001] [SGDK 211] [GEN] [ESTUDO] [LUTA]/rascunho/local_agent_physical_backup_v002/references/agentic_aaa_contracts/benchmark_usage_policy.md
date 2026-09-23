# Benchmark Usage Policy

## Purpose

Benchmarks are technical references, never source art, clone recipes, or prompt commands. They may guide scale, density, timing, staging, material readability, palette pressure, budget, and quality bar.

## Allowed

- compare sprite silhouette readability in 320x224
- compare motion timing categories such as startup, active, hitstop, recovery
- compare tile density and reuse pressure
- compare palette role and material contrast
- compare audio channel priority and event timing

## Blocked

- copying pose, silhouette, stage layout, palette identity, UI identity, character identity, or IP symbols
- using a game, studio, artist, or IP name as a direct prompt command
- storing benchmark pixels under `data/source_art`
- promoting a recolor as authorial art

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

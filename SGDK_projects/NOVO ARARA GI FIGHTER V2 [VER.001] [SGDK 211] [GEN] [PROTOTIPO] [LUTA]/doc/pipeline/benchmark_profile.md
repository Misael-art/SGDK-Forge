# benchmark_profile

benchmark_profile_id: ARCADE_FIGHTER_PRESENCE_AUTHORIAL_1994
benchmark_used_as: technical_reference
required_match: 8.0
max_similarity: 0.30

## Allowed Inheritance

- scale impression of a real 2D fighter sprite on a 320x224 screen.
- animation density expectations for idle/walk/attack readability.
- HUD density and match-formality expectations.
- budget discipline for two large fighters plus stage plus HUD.

## Explicitly Forbidden

- copying pose, stance, silhouette, facial archetype, palette, frame timing, tiles, or stage layout from any benchmark.
- using HAMOOPIG, KOF, Alpha, Ryu, Ken, Ryo, Kyo, or any commercial sheet as source pixels.
- recolor-only character production.

## Measurement Method

clone_risk_method: prompt exclusion + manual structural review + source file hash lineage + optional perceptual/structural comparison when reference images are present.
benchmark_similarity_method: observational genre-presence rubric; high authorial novelty is required even when technical presence score is high.
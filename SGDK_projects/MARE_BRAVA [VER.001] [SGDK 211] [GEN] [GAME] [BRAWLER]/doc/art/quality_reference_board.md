# Quality Reference Board — MARE BRAVA

This board is the project's required quality baseline for character, scene and
FX review. It is not source art and must never be copied into a production
asset. Canonical review behavior lives in
`tools/sgdk_wrapper/.agent/references/production_visual_quality_contract.md`.

| Reference | Project-local copy | Role in review |
|---|---|---|
| CRIA production sheet | `rascunho/entrada_bruta/quality_reference/cria_production_reference_v01.png` | Preserve body construction, clothing/material markers, readable action phases and clustered smoke. |
| TAÍNA production sheet | `rascunho/entrada_bruta/quality_reference/taina_production_reference_v01.png` | Preserve face, hair, bandages, athletic weight, costume asymmetry and action readability. |
| CAIS modular kit | `rascunho/entrada_bruta/quality_reference/cais_modular_kit_reference_v01.png` | Require a modular dock kit, authored landmarks, water edge, props and semantic depth. |
| Combined production board | `rascunho/entrada_bruta/quality_reference/mare_brava_production_sheet_reference_v01.png` | Check that characters, animation, scene and props belong to one production language. |

## Non-negotiable reading

- The current procedural CAIS/TAÍNA/CRIA/FX assets are technical probes, never
  the visual baseline for a later review.
- A character translation fails when it loses anatomy, face, clothing markers,
  material ramps or action intent visible in its assigned reference.
- A CAIS translation fails when it replaces the modular kit with a flattened
  illustration or generic harbor dressing.
- FX fail when they do not show clustered phase change and gameplay/world
  consequence.
- Conceptual `BG_C`, `BG_B` and `BG_A` are semantic layers. Runtime must map
  them honestly to BG_A, BG_B, WINDOW and sprites under a measured VDP budget.

No asset can be marked visually approved through comparison with the current
runtime placeholder, a build result or a single screenshot.

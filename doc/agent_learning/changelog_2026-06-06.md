# Changelog (workspace) 2026-06-06

## Agent startup environment + Graphify default

- Added `tools/sgdk_wrapper/prepare_agent_environment.ps1` for first-use agent startup: validates `.agents/skills` and `.trae/skills`, checks/installs `pwsh`, `uv` and Graphify, and prepares the consultive graph.
- Added `tools/sgdk_wrapper/assert_agent_environment.ps1` as the default guard; it runs the preparation automatically and blocks the session when the report is not ready.
- Added `graphify-out/AGENT_ENVIRONMENT_REPORT.json` as the machine-readable readiness report and a global lock in `prepare_agent_environment.ps1` to avoid concurrent Graphify cache races.
- `show_agent_menu.ps1` now runs the environment guard automatically unless `SGDK_SKIP_AGENT_ENVIRONMENT_GUARD=1`.
- Added `tools/sgdk_wrapper/.agent/workflows/agent-startup-environment.md`.
- Connected `.cursor`, `.serena`, `.superpowers`, `.trae`, `.agents` and `.claude` to the same startup rule, preserving Graphify as a consultive index only.

## Scene/tilemap conversion curation

- Added schemas:
  - `tools/sgdk_wrapper/schemas/scene_tilemap_conversion_report.schema.json`
  - `tools/sgdk_wrapper/schemas/tilemap_flag_report.schema.json`
  - `tools/sgdk_wrapper/schemas/per_tile_palette_conflict_report.schema.json`
- Added doc templates:
  - `doc/scene_tilemap_conversion_report.json`
  - `doc/tilemap_flag_report.json`
  - `doc/per_tile_palette_conflict_report.json`
- Added analyzer tool:
  - `tools/image-tools/analyze_tilemap_dedup_flags.py`
  - Unit tests: `tools/image-tools/tests/test_tilemap_dedup_flags_reports.py`
- Hardened `tools/sgdk_wrapper/validate_resources.ps1` (closeout/delivery enforcement):
  - Defines critical scene conversion intent: size >=320x224 OR technique declared OR delivery/closeout scope
  - Validates the 3 reports against schemas; invalid schema => treated as missing
  - Closeout-only blockers:
    - `scene_tilemap_conversion_report_missing|invalid|stale`
    - `tilemap_flag_report_missing|invalid` (when HV flip/dedup is claimed)
    - `per_tile_palette_conflict_report_missing|invalid`
    - `per_tile_palette_conflicts_detected`
    - `whole_image_unique_ratio_high_without_justification`
    - `technique_usage_manifest_empty`
  - Blocks report path references that escape project root (`external_path_reference_outside_project`)
- Updated canonical skills to require the reports for critical scene/tilemap conversions:
  - `art-conversion-pipeline`
  - `art-translation-to-vdp`
  - `multi-plane-composition`
  - `megadrive-vdp-budget-analyst`
  - `visual-excellence-standards`
- Updated technique registry:
  - Removed absolute external references (`C:/Users/.../.codex/attachments/...`)
  - Added curation notes: status only rises with fixture + ROM + BlastEm + budget + required reports + human approval

## Operational maturity gates

- Added schema:
  - `tools/sgdk_wrapper/schemas/operational_loop_decision.schema.json`
- Hardened build gate:
  - `tools/sgdk_wrapper/build.bat` now runs `tools/sgdk_wrapper/detect_operational_loop.ps1`
  - Blocks only on 3 consecutive reports with the same blockers
  - Unlock requires `doc/operational_loop_decision.json` (valid per schema)
- Hardened tool-first audit:
  - `tools/sgdk_wrapper/audit_tool_first.ps1` requires fixture executed or `fixture_skip_reason` (skip still blocks canonical use)
  - Added blocker codes: `tool_first_fixture_missing`, `tool_first_fixture_skipped`
- Hardened evidence root gate:
  - `tools/sgdk_wrapper/audit_evidence_root.ps1` blocks absolute paths outside project in active reports unless registered+hashed in `doc/project_hygiene_manifest.json` external_inputs
  - Added blocker code: `evidence_external_path_detected`
- Fixed orphan subproject gate:
  - `tools/sgdk_wrapper/audit_orphan_subproject.ps1` validates aggregation at the study root via `.mddev/project.json` `nested_viewers`
- Hardened learning capture:
  - `tools/sgdk_wrapper/.agent/scripts/extract_project_learning.py` blocks capture when loop/blockers recur and there is no lesson and no parseable `no_qualified_lessons_justification:` in `doc/agent_learning/canonical_promotion_review.md`
  - `tools/sgdk_wrapper/scene_closeout_gate.ps1` now calls `audit_project_learning.ps1 -Mode Capture` in closeout gate
- ASCII-safe art diagnostics:
  - `tools/sgdk_wrapper/art_diagnostic.py` default output is ASCII-only; `--unicode` is optional and never required by gates

## Graphify + Obsidian cockpit

- Added conservative Graphify integration (consultive index only):
  - `.graphifyignore` restricts index scope to canonical knowledge paths
  - `tools/sgdk_wrapper/graphify_forge.ps1` wrapper adds build/update/query/report, freshness (stale guard) and scope audit (blocks on `graph_scope_violation`)
  - `tools/sgdk_wrapper/ci/test_graphify_integration.ps1` validates spaces/brackets paths, excluded dirs, stale blocking and contaminated-graph blocking
  - `graphify-out/` is treated as generated/cache and is ignored by Git
- Added minimal policy doc:
  - `doc/GRAPHIFY_OBSIDIAN_POLICY.md`

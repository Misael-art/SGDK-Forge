# Context Orchestration V1

Use this reference when art creation or SGDK code generation needs project-local grounding before prompts, downloads, or implementation.

## Principle

RAG in this workspace means controlled retrieval from canonical files. It is not a vector database requirement in v1.

The agent must declare what it consulted, then emit decision artifacts. Do not request or expose Chain of Thought.

## `context_pack_manifest`

Purpose: prove which sources shaped the next proposal.

Minimum shape:

```json
{
  "schema": "context_pack_manifest.v1",
  "project_root": "<absolute path>",
  "generated_at_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "memory_policy": {
    "project_memory_found": true,
    "fallback_global_memory": false
  },
  "sources": [
    {
      "role": "gdd",
      "path": "doc/11-gdd.md",
      "exists": true,
      "sha256": "...",
      "mtime_utc": "..."
    }
  ],
  "notes": []
}
```

Required source families when present:

- project truth: `doc/10-memory-bank.md`, `doc/11-gdd.md`, `doc/13-spec-cenas.md`, `doc/00-diretrizes-agente.md`, `doc/12-roteiro.md`, `doc/03-arquitetura.md`, `.mddev/project.json`
- global memory: `doc/06_AI_MEMORY_BANK.md`
- art memory: `doc/03_art/02_visual_feedback_bank.md`, visual quality bar and cohesion docs
- source cases: `doc/source_cases/**/case_manifest.json`
- engine patterns: `doc/05_technical/92_sgdk_engine_pattern_registry.json` and relevant engine profile docs
- SGDK API reality: local headers under `sdk/sgdk-2.11/inc/` or the runtime skill API references

If a project lacks `doc/10-memory-bank.md`, record the fallback to `doc/06_AI_MEMORY_BANK.md`. Do not invent a memory file.

## `asset_lineage_record`

Purpose: keep each asset auditable from prompt/source to acceptance.

Minimum fields:

- `asset_id`
- `asset_role`
- `source_kind`: `ai_generated`, `external_free_asset`, `manual_seed`, `translated_source`
- `source_ref`: prompt id, URL, file path, or case manifest
- `premium_source_path` when accepted as final art source
- `premium_source_sha256` or size + mtime when hashing is unavailable
- `style_anchor_id`
- `master_style_manifest_ref`
- `palette_ref`
- `engine_reference_profile_ids`
- `raw_output_path`
- `generation_channel`: `native_chat_image_generation_callable`, `native_chat_inline_generation`, `api_cli_generation`, `external_source`, or `manual_seed`
- `tool_callable`: true/false
- `image_rendered_inline`: true/false
- `persisted_to_filesystem`: true/false
- `chat_asset_label` when inline
- `conversion_plan`
- `validation_refs`
- `source_to_rom_visual_match` when promoted to runtime
- `benchmark_profile_id` and `benchmark_match` when a benchmark gate applies
- `acceptance_status`: `accepted`, `rejected`, `revise`, `blocked`, `debug_lab`
- `decision_reason`

If the source is procedural/local rasterization, record `source_kind: procedural_debug_lab` and `acceptance_status: debug_lab`. It cannot become the final source for a critical AAA asset.

## `style_memory_index`

Purpose: provide deterministic long-term style memory without vector storage.

Recommended location:

- project: `doc/source_cases/style_memory_index.json`
- lab/output: `out/logs/style_memory_index.json`

Minimum fields:

- `style_anchor_id`
- `master_style_manifest_ref`
- accepted asset ids
- rejected asset ids and rejection reasons
- palette families
- line weight policy
- lighting policy
- drift thresholds

Vector DB use is a future optional optimization. The file index remains authoritative.

## `qa_correction_loop`

Purpose: replace hidden reasoning with explicit correction artifacts.

Loop:

1. `qa_findings`: observable issue, metric, affected asset, source evidence
2. `correction_request`: concrete prompt/edit/conversion change
3. regenerated or corrected asset
4. updated `asset_lineage_record`
5. re-run pixel, visual and budget checks

Common blockers:

- style drift above threshold
- palette outside 9-bit grid
- PLTE inflated above 16 entries
- antialiasing or blur
- pivot drift across frames
- asset looks strong alone but conflicts with `master_style_manifest`

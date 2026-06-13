# Scene/Tilemap Curation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add canonical schemas + validator enforcement + budget/skill/registry updates so scene/tilemap conversions cannot be approved without audited tilemap structure, flags, palette safety, and ROM-evidence gates.

**Architecture:** Validator (`tools/sgdk_wrapper/validate_resources.ps1`) validates presence/schema + closeout-only blockers; report generation remains tool-side (image-tools). Skills and registry reinforce process and prohibit premature mastery claims.

**Tech Stack:** PowerShell 7 (wrapper), Python (tools/image-tools), JSON Schema, SGDK wrapper `.agent` docs.

---

## File map (create/modify)

**Create (spec already exists):**
- Create: `f:/Projects/Sgdk Forge/doc/superpowers/specs/2026-06-06-scene-tilemap-curation-spec.md`

**Create (schemas/templates):**
- Create: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/schemas/scene_tilemap_conversion_report.schema.json`
- Create: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/schemas/tilemap_flag_report.schema.json`
- Create: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/schemas/per_tile_palette_conflict_report.schema.json`
- Create: `f:/Projects/Sgdk Forge/doc/scene_tilemap_conversion_report.json`
- Create: `f:/Projects/Sgdk Forge/doc/tilemap_flag_report.json`
- Create: `f:/Projects/Sgdk Forge/doc/per_tile_palette_conflict_report.json`

**Create (tool-first audit report):**
- Create: `f:/Projects/Sgdk Forge/doc/agent_learning/tool_first_audit_scene_tilemap_reports_2026-06-06.md`

**Modify (validator):**
- Modify: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/validate_resources.ps1`

**Modify (skills):**
- Modify: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/.agent/skills/art/art-conversion-pipeline/SKILL.md`
- Modify: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md`
- Modify: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md`
- Modify: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`
- Modify: `f:/Projects/Sgdk Forge/tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`

**Modify (registry/matrix + memory/changelog):**
- Modify: `f:/Projects/Sgdk Forge/doc/05_technical/93_16bit_hardware_mastery_registry.json`
- Modify: `f:/Projects/Sgdk Forge/doc/06_AI_MEMORY_BANK.md`
- Create: `f:/Projects/Sgdk Forge/doc/agent_learning/changelog_2026-06-06.md`

**Maybe create (only if tool-first audit concludes low-risk extension is impossible):**
- Create: `f:/Projects/Sgdk Forge/tools/image-tools/analyze_tilemap_dedup_flags.py`

**Tests:**
- Create: `f:/Projects/Sgdk Forge/tools/image-tools/tests/test_tilemap_dedup_flags_reports.py`

**Fixture (lab project):**
- Create: `f:/Projects/Sgdk Forge/SGDK_projects/_agent_laboratory/SCENE_TILEMAP_CURATION_FIXTURE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/` (minimal SGDK project + evidence placeholders)

---

### Task 1: Tool-first audit (required before any new script)

**Files:**
- Create: `doc/agent_learning/tool_first_audit_scene_tilemap_reports_2026-06-06.md`

- [ ] **Step 1: Read candidate tools and record capabilities**

Read and summarize (links must be file paths, not external URLs):
- `tools/image-tools/analyze_aesthetic.py` (flip-aware dedup exists)
- `tools/image-tools/analyze_translation_case.py` (tile budget + whole-image risk signals)
- `tools/image-tools/analyze_source_semantics.py` (semantic_parse_report coupling)
- `tools/sgdk_wrapper/res_graph_audit.ps1` (rescomp evidence + graph auditing)
- `tools/sgdk_wrapper/lib/res_graph.psm1` (PNG tile stats; currently non-flip-aware)
- `tools/mugen2sgdk/` (audit for CLI/testability; mark `legacy_gui_tool_without_cli` if applicable)

- [ ] **Step 2: Write the audit report**

Create `doc/agent_learning/tool_first_audit_scene_tilemap_reports_2026-06-06.md` with sections:
- `Decision`: `reuse | extend | wrap | replace | reject`
- `Chosen path`: explicitly state if we will extend an existing Python script or create `analyze_tilemap_dedup_flags.py`
- `Why not validate_resources auto-generate`: restate the rule
- `Risk notes`: Windows paths with spaces/brackets; ASCII-only output; schema validation requirement

---

### Task 2: Add JSON Schemas for the three reports

**Files:**
- Create: `tools/sgdk_wrapper/schemas/scene_tilemap_conversion_report.schema.json`
- Create: `tools/sgdk_wrapper/schemas/tilemap_flag_report.schema.json`
- Create: `tools/sgdk_wrapper/schemas/per_tile_palette_conflict_report.schema.json`

- [ ] **Step 1: Create `scene_tilemap_conversion_report.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "scene_tilemap_conversion_report",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "source_path",
    "source_sha256",
    "conversion_target",
    "output_tileset_path",
    "output_tilemap_path",
    "output_palette_path",
    "tile_size_px",
    "total_tiles",
    "unique_tiles_exact",
    "unique_tiles_hflip",
    "unique_tiles_vflip",
    "unique_tiles_hvflip",
    "final_unique_tiles",
    "dedup_savings_tiles",
    "dedup_savings_percent",
    "palette_count",
    "per_tile_palette_conflicts",
    "priority_tile_count",
    "hflip_tile_count",
    "vflip_tile_count",
    "hvflip_tile_count",
    "estimated_vram_bytes",
    "estimated_map_bytes",
    "rom_resource_strategy",
    "status",
    "blockers",
    "generated_at",
    "tool_name",
    "tool_version"
  ],
  "properties": {
    "source_path": { "type": "string", "minLength": 1 },
    "source_sha256": { "type": "string", "pattern": "^[0-9a-f]{64}$" },
    "conversion_target": {
      "type": "string",
      "enum": ["scene_slice", "tilemap", "background_layer", "foreground_layer"]
    },
    "output_tileset_path": { "type": "string", "minLength": 1 },
    "output_tilemap_path": { "type": "string", "minLength": 1 },
    "output_palette_path": { "type": "string", "minLength": 1 },
    "tile_size_px": { "type": "integer", "const": 8 },
    "total_tiles": { "type": "integer", "minimum": 0 },
    "unique_tiles_exact": { "type": "integer", "minimum": 0 },
    "unique_tiles_hflip": { "type": "integer", "minimum": 0 },
    "unique_tiles_vflip": { "type": "integer", "minimum": 0 },
    "unique_tiles_hvflip": { "type": "integer", "minimum": 0 },
    "final_unique_tiles": { "type": "integer", "minimum": 0 },
    "dedup_savings_tiles": { "type": "integer" },
    "dedup_savings_percent": { "type": "number" },
    "palette_count": { "type": "integer", "minimum": 0 },
    "per_tile_palette_conflicts": { "type": "integer", "minimum": 0 },
    "priority_tile_count": { "type": "integer", "minimum": 0 },
    "hflip_tile_count": { "type": "integer", "minimum": 0 },
    "vflip_tile_count": { "type": "integer", "minimum": 0 },
    "hvflip_tile_count": { "type": "integer", "minimum": 0 },
    "estimated_vram_bytes": { "type": "integer", "minimum": 0 },
    "estimated_map_bytes": { "type": "integer", "minimum": 0 },
    "rom_resource_strategy": {
      "type": "string",
      "enum": ["IMAGE", "TILESET_MAP", "BIN_CUSTOM", "COMPARE_FLAT"]
    },
    "status": { "type": "string", "enum": ["ok", "needs_review", "blocked"] },
    "blockers": {
      "type": "array",
      "items": { "type": "string", "minLength": 1 }
    },
    "generated_at": { "type": "string", "minLength": 1 },
    "tool_name": { "type": "string", "minLength": 1 },
    "tool_version": { "type": "string", "minLength": 1 }
  }
}
```

- [ ] **Step 2: Create `tilemap_flag_report.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "tilemap_flag_report",
  "type": "object",
  "additionalProperties": false,
  "required": ["entries", "generated_at", "tool_name", "tool_version"],
  "properties": {
    "generated_at": { "type": "string", "minLength": 1 },
    "tool_name": { "type": "string", "minLength": 1 },
    "tool_version": { "type": "string", "minLength": 1 },
    "entries": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "tile_x",
          "tile_y",
          "tile_index",
          "palette_id",
          "priority",
          "hflip",
          "vflip",
          "source_tile_hash",
          "canonical_tile_hash"
        ],
        "properties": {
          "tile_x": { "type": "integer", "minimum": 0 },
          "tile_y": { "type": "integer", "minimum": 0 },
          "tile_index": { "type": "integer", "minimum": 0 },
          "palette_id": { "type": "integer", "minimum": 0, "maximum": 3 },
          "priority": { "type": "boolean" },
          "hflip": { "type": "boolean" },
          "vflip": { "type": "boolean" },
          "source_tile_hash": { "type": "string", "pattern": "^[0-9a-f]{64}$" },
          "canonical_tile_hash": { "type": "string", "pattern": "^[0-9a-f]{64}$" }
        }
      }
    }
  }
}
```

- [ ] **Step 3: Create `per_tile_palette_conflict_report.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "per_tile_palette_conflict_report",
  "type": "object",
  "additionalProperties": false,
  "required": ["conflicts_total", "conflicts", "generated_at", "tool_name", "tool_version"],
  "properties": {
    "generated_at": { "type": "string", "minLength": 1 },
    "tool_name": { "type": "string", "minLength": 1 },
    "tool_version": { "type": "string", "minLength": 1 },
    "conflicts_total": { "type": "integer", "minimum": 0 },
    "conflicts": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["rule_id", "severity", "tile_x", "tile_y", "details"],
        "properties": {
          "rule_id": { "type": "string", "minLength": 1 },
          "severity": { "type": "string", "enum": ["warning", "error"] },
          "tile_x": { "type": "integer", "minimum": 0 },
          "tile_y": { "type": "integer", "minimum": 0 },
          "details": { "type": "string", "minLength": 1 }
        }
      }
    }
  }
}
```

---

### Task 3: Add canonical doc templates (minimal examples)

**Files:**
- Create: `doc/scene_tilemap_conversion_report.json`
- Create: `doc/tilemap_flag_report.json`
- Create: `doc/per_tile_palette_conflict_report.json`

- [ ] **Step 1: Add `doc/scene_tilemap_conversion_report.json` example**

```json
{
  "$schema": "tools/sgdk_wrapper/schemas/scene_tilemap_conversion_report.schema.json",
  "source_path": "rascunho/source_scene.png",
  "source_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
  "conversion_target": "scene_slice",
  "output_tileset_path": "res/gfx/scene_ts.png",
  "output_tilemap_path": "res/gfx/scene_map.bin",
  "output_palette_path": "res/gfx/scene_pal.bin",
  "tile_size_px": 8,
  "total_tiles": 0,
  "unique_tiles_exact": 0,
  "unique_tiles_hflip": 0,
  "unique_tiles_vflip": 0,
  "unique_tiles_hvflip": 0,
  "final_unique_tiles": 0,
  "dedup_savings_tiles": 0,
  "dedup_savings_percent": 0.0,
  "palette_count": 0,
  "per_tile_palette_conflicts": 0,
  "priority_tile_count": 0,
  "hflip_tile_count": 0,
  "vflip_tile_count": 0,
  "hvflip_tile_count": 0,
  "estimated_vram_bytes": 0,
  "estimated_map_bytes": 0,
  "rom_resource_strategy": "TILESET_MAP",
  "status": "needs_review",
  "blockers": [],
  "generated_at": "2026-06-06T00:00:00Z",
  "tool_name": "analyze_tilemap_dedup_flags",
  "tool_version": "0.1"
}
```

- [ ] **Step 2: Add `doc/tilemap_flag_report.json` example**

```json
{
  "$schema": "tools/sgdk_wrapper/schemas/tilemap_flag_report.schema.json",
  "generated_at": "2026-06-06T00:00:00Z",
  "tool_name": "analyze_tilemap_dedup_flags",
  "tool_version": "0.1",
  "entries": [
    {
      "tile_x": 0,
      "tile_y": 0,
      "tile_index": 0,
      "palette_id": 0,
      "priority": false,
      "hflip": false,
      "vflip": false,
      "source_tile_hash": "0000000000000000000000000000000000000000000000000000000000000000",
      "canonical_tile_hash": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ]
}
```

- [ ] **Step 3: Add `doc/per_tile_palette_conflict_report.json` example**

```json
{
  "$schema": "tools/sgdk_wrapper/schemas/per_tile_palette_conflict_report.schema.json",
  "generated_at": "2026-06-06T00:00:00Z",
  "tool_name": "analyze_tilemap_dedup_flags",
  "tool_version": "0.1",
  "conflicts_total": 0,
  "conflicts": []
}
```

---

### Task 4: Extend or create the tilemap dedup/flags analyzer (Python)

**Files:**
- Modify (preferred): `tools/image-tools/analyze_aesthetic.py` OR `tools/image-tools/analyze_translation_case.py`
- Create (only if tool-first audit chooses): `tools/image-tools/analyze_tilemap_dedup_flags.py`
- Test: `tools/image-tools/tests/test_tilemap_dedup_flags_reports.py`

- [ ] **Step 1: Write failing tests (unittest) for dedup modes**

Create `tools/image-tools/tests/test_tilemap_dedup_flags_reports.py` with tests that generate small indexed PNGs (P mode) and assert:
- exact duplicate detection
- H flip duplicate detection
- V flip duplicate detection
- HV flip duplicate detection
- palette conflict detection (tile uses > 15 visible indices or mixes palette domains)
- ASCII-only stdout (encode to cp1252)
- temp path with `[]` works (create temp dir named `case_[brackets]`)

Test skeleton:

```python
import io
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]


def _make_indexed_png(path: Path, w: int, h: int, pixels: list[int], palette: list[int]):
    img = Image.new("P", (w, h))
    img.putpalette(palette + [0] * (768 - len(palette)))
    img.putdata(pixels)
    img.save(path)


class TilemapDedupFlagsReportTest(unittest.TestCase):
    def test_ascii_stdout_cp1252_safe(self):
        buf = io.StringIO()
        old = sys.stdout
        try:
            sys.stdout = buf
            print("ASCII_ONLY_OUTPUT_OK")
        finally:
            sys.stdout = old
        buf.getvalue().encode("cp1252")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Implement minimal analyzer behavior to satisfy tests**

Requirements for the analyzer function(s):
- load indexed PNG via Pillow
- slice 8x8 tiles
- compute SHA-256 of raw index bytes per tile for:
  - normal
  - hflip
  - vflip
  - hvflip
- compute canonical hash = min among the four hashes (lexicographic)
- compute counts:
  - total tiles
  - unique by exact
  - unique by flip families
  - dedup savings
- compute tilemap flag report entries for each tile:
  - detect which orientation matches canonical (normal/h/v/hv) and set flags
  - palette_id: for now default to 0 unless analyzer also reads a palette-domain map (future extension)
  - priority: default false (future extension if tilemap format includes priority bit)
- compute per-tile palette conflicts:
  - detect if visible pixels include index 0 (transparency contamination) when transparency is not allowed for this target
  - detect if tile uses > 15 non-zero indices

CLI requirements:
- accept `--input <png>` and `--out-dir <dir>`
- write three JSON files to out-dir, schema-valid
- print only ASCII to stdout/stderr

- [ ] **Step 3: Run tests**

Run:
`python -m unittest tools/image-tools/tests/test_tilemap_dedup_flags_reports.py -v`

Expected: PASS

---

### Task 5: Harden `validate_resources.ps1` (closeout-only enforcement)

**Files:**
- Modify: `tools/sgdk_wrapper/validate_resources.ps1`

- [ ] **Step 1: Identify existing closeout-only blocker mechanism**

Confirm the closeout-only mechanism used by `Add-BlockingStatus` and `Test-CloseoutOnlyBlockingStatus`.

- [ ] **Step 2: Add report path constants**

Add paths (project-relative) for:
- `out/logs/scene_tilemap_conversion_report.json`
- `out/logs/tilemap_flag_report.json`
- `out/logs/per_tile_palette_conflict_report.json`

- [ ] **Step 3: Implement schema validation helper**

Implement a helper that:
- reads JSON
- checks `$schema` exists
- validates against the corresponding schema file in `tools/sgdk_wrapper/schemas/`
- returns `(present, schema_valid, parsed_json)`

Constraints:
- Must use `-LiteralPath` for any filesystem reads
- Must treat invalid schema as missing (per policy)

- [ ] **Step 4: Define critical-scene detection**

Implement a function that returns `true` if:
- any resource map/image is `>= 320x224` (use res_graph or resources parsing if available), OR
- `doc/technique_usage_manifest.json` declares any technique tag/id in the critical set, OR
- closeout/delivery flags are active (existing manifest/claims usage)

- [ ] **Step 5: Add closeout-only blockers**

Add new status codes (closeout-only) and enforce:
- missing/invalid scene_tilemap_conversion_report for critical scenes
- missing/invalid tilemap_flag_report when `TILE_DEDUP_HVFLIP` declared
- missing/invalid palette conflict report for critical scenes
- `conflicts_total > 0` blocks
- `rom_resource_strategy=IMAGE` + high unique ratio blocks unless `COMPARE_FLAT` or declared justification
- any report path absolute outside project blocks via `evidence_root_mismatch`

- [ ] **Step 6: Run validator against fixture**

Run:
`powershell -File tools/sgdk_wrapper/validate_resources.ps1 -ProjectRoot "<fixture_root>" -CloseoutGate`

Expected: blockers fire until reports exist; then pass once reports and `.res` are correct.

---

### Task 6: Update the five canonical skills (minimum necessary edits)

**Files:**
- Modify: `tools/sgdk_wrapper/.agent/skills/art/art-conversion-pipeline/SKILL.md`
- Modify: `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md`
- Modify: `tools/sgdk_wrapper/.agent/skills/art/multi-plane-composition/SKILL.md`
- Modify: `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`
- Modify: `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`

- [ ] **Step 1: Add explicit requirement statements**

Update each SKILL.md to include:
- what report(s) are required for critical scenes
- what gates block promotion
- no "ResComp compiled" == "approved"

- [ ] **Step 2: Run skill framework validator**

Run:
`python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`

Expected: PASS

---

### Task 7: Update registry (remove external absolute paths; add curation notes)

**Files:**
- Modify: `doc/05_technical/93_16bit_hardware_mastery_registry.json`

- [ ] **Step 1: Remove any absolute external paths**

Specifically remove/replace `C:/Users/.../.codex/attachments/...` references from:
- `palette_remastering_slot_audit`
- `tile_dedup_hvflip_hashing`

- [ ] **Step 2: Add/strengthen notes**

Add notes aligning with:
- reports required for tile_dedup_hvflip_hashing (`tilemap_flag_report`, dedup report, collision checks)
- whole-image `IMAGE` suspicious by default for `>=320x224`
- status remains TEORICA/LAB until ROM + BlastEm + budget + fixture + human approval

- [ ] **Step 3: Run registry validator**

Run:
`python tools/sgdk_wrapper/.agent/scripts/validate_technique_registry.py`

Expected: PASS

---

### Task 8: Create canonical lab fixture project (no pollution of active projects)

**Files:**
- Create: `SGDK_projects/_agent_laboratory/SCENE_TILEMAP_CURATION_FIXTURE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/...`

- [ ] **Step 1: Bootstrap the lab project from the canonical template**

Use `tools/sgdk_wrapper/modelo` as baseline and keep everything self-contained in the lab project.

- [ ] **Step 2: Add a rich indexed PNG scene under `rascunho/`**

Record hash in lab doc and ensure the source is inside the project root.

- [ ] **Step 3: Add conversion outputs and resources**

Add:
- tileset/tilemap/palette outputs
- `res/resources.res` using `TILESET` + `MAP` (and optionally `IMAGE` variant for compare)

- [ ] **Step 4: Add a minimal ROM viewer**

ROM should:
- load and display the MAP/TILESET scene
- expose deterministic boot and (if available in template) SRAM heartbeat for capture tooling

- [ ] **Step 5: Generate reports into `out/logs/`**

Generate:
- `scene_tilemap_conversion_report.json`
- `tilemap_flag_report.json`
- `per_tile_palette_conflict_report.json`

- [ ] **Step 6: Build and capture BlastEm evidence**

Run:
- project `build.bat`
- BlastEm capture workflow (existing wrapper flow)

Collect:
- screenshot BlastEm
- `save.sram` (if the fixture supports it)
- `visual_vdp_dump.bin` when possible

- [ ] **Step 7: Run res_graph and validator**

Run:
- `powershell -File tools/sgdk_wrapper/res_graph_audit.ps1 -ProjectRoot "<fixture_root>"`
- `powershell -File tools/sgdk_wrapper/validate_resources.ps1 -ProjectRoot "<fixture_root>" -CloseoutGate`

Expected: PASS (after reports + `.res` are correct)

---

### Task 9: Harden documentation memory + changelog (objective blockers)

**Files:**
- Modify: `doc/06_AI_MEMORY_BANK.md`
- Create: `doc/agent_learning/changelog_2026-06-06.md`

- [ ] **Step 1: Update `doc/06_AI_MEMORY_BANK.md`**

Add:
- new report contracts and their enforcement
- definition of critical scene
- reminder: no technique promoted to MESTRE without evidence bundle

- [ ] **Step 2: Write changelog entry**

Create `doc/agent_learning/changelog_2026-06-06.md` summarizing:
- what was added/changed
- which blockers exist
- how to satisfy them in a project

---

### Task 10: Final validations (must run before finish)

- [ ] **Step 1: Run skill framework validator**

Run:
`python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`

Expected: PASS

- [ ] **Step 2: Run technique registry validator (if registry changed)**

Run:
`python tools/sgdk_wrapper/.agent/scripts/validate_technique_registry.py`

Expected: PASS

- [ ] **Step 3: Run template registry validator (if templates changed)**

Run:
`python tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`

Expected: PASS

- [ ] **Step 4: Run Python unit tests**

Run:
`python -m unittest discover tools/image-tools/tests -v`

Expected: PASS

- [ ] **Step 5: Run validate_resources on fixture**

Run:
`powershell -File tools/sgdk_wrapper/validate_resources.ps1 -ProjectRoot "<fixture_root>" -CloseoutGate`

Expected: PASS


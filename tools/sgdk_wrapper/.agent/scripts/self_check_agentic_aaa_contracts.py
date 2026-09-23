#!/usr/bin/env python3
"""Self-check for the agentic AAA contract pack.

Checks:
- new schemas are valid JSON
- example contracts and reports are valid JSON
- schema examples validate when jsonschema is available
- new validators pass their built-in self-checks
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
AGENT_ROOT = ROOT / "tools" / "sgdk_wrapper" / ".agent"
SCRIPT_ROOT = AGENT_ROOT / "scripts"
SCHEMA_ROOT = ROOT / "tools" / "sgdk_wrapper" / "schemas"
EXAMPLE_ROOT = AGENT_ROOT / "references" / "agentic_aaa_contracts" / "examples"

SCHEMAS = [
    "visual_dna_manifest.schema.json",
    "design_inheritance.schema.json",
    "animation_strip_contract.schema.json",
    "audio_architecture_card.schema.json",
    "blastem_input_script.schema.json",
    "camera_behavior_contract.schema.json",
    "project_bible.schema.json",
]

EXAMPLES = [
    "visual_dna_manifest.example.json",
    "design_inheritance.example.json",
    "animation_strip_contract.example.json",
    "audio_architecture_card.example.json",
    "blastem_input_script.example.json",
    "project_bible.example.json",
    "cpu_frame_budget_report.json",
    "dma_queue_contract.json",
    "z80_task_ownership_contract.json",
    "sprite_scanline_pressure_report.json",
    "palette_slot_audit.json",
    "h_int_ownership_map.json",
    "vram_residency_report.json",
    "constraint_budget_report.json",
    "audio_channel_ownership_report.json",
    "dac_stream_budget_report.json",
    "sfx_priority_matrix.json",
    "input_latency_contract.json",
    "movement_curve_report.json",
    "camera_behavior_contract.json",
    "hitbox_sprite_alignment_report.json",
    "enemy_readability_report.json",
    "playable_scene_design_card.json",
    "qa_emulator_report.json",
    "softlock_detection_report.json",
    "runtime_fuzz_report.json",
    "authorial_consistency_report.json",
    "style_drift_report.json",
    "vdp_scanline_input.example.json",
    "ym2612_patch.example.json",
]

SCHEMA_EXAMPLES = {
    "visual_dna_manifest.schema.json": "visual_dna_manifest.example.json",
    "design_inheritance.schema.json": "design_inheritance.example.json",
    "animation_strip_contract.schema.json": "animation_strip_contract.example.json",
    "audio_architecture_card.schema.json": "audio_architecture_card.example.json",
    "blastem_input_script.schema.json": "blastem_input_script.example.json",
    "camera_behavior_contract.schema.json": "camera_behavior_contract.json",
    "project_bible.schema.json": "project_bible.example.json",
}

SCRIPTS = [
    "validate_strip.py",
    "vdp_scanline_simulator.py",
    "dma_queue_planner.py",
    "ym2612_patch_validator.py",
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for name in SCHEMAS:
        path = SCHEMA_ROOT / name
        if not path.exists():
            errors.append(f"missing schema: {path}")
            continue
        try:
            load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid schema JSON {path}: {exc}")

    for name in EXAMPLES:
        path = EXAMPLE_ROOT / name
        if not path.exists():
            errors.append(f"missing example: {path}")
            continue
        try:
            load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid example JSON {path}: {exc}")

    try:
        import jsonschema  # type: ignore
    except Exception:  # noqa: BLE001
        jsonschema = None
        warnings.append("jsonschema package not available; schema pair validation skipped")

    if jsonschema is not None:
        for schema_name, example_name in SCHEMA_EXAMPLES.items():
            schema = load_json(SCHEMA_ROOT / schema_name)
            example = load_json(EXAMPLE_ROOT / example_name)
            try:
                jsonschema.Draft7Validator(schema).validate(example)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"schema validation failed for {example_name}: {exc}")

    for script in SCRIPTS:
        path = SCRIPT_ROOT / script
        result = subprocess.run(
            [sys.executable, str(path), "--self-check"],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            errors.append(f"{script} --self-check failed:\n{result.stdout}")
        else:
            print(result.stdout.strip())

    for warning in warnings:
        print(f"WARN: {warning}")

    if errors:
        print("agentic AAA contract self-check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("agentic AAA contract self-check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

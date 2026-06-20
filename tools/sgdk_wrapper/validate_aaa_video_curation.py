"""Validate current AAA curation owners without preserving historical skill counts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AGENT = ROOT / ".agent"
ACTIVE_SKILLS = AGENT / "skills"
LEGACY_SKILLS = AGENT / "legacy" / "skills"

REQUIRED_ACTIVE_SKILLS = (
    "architecture/game-state-transition-architect",
    "code/camera-system-sgdk",
    "code/collision-system-architect",
    "code/entity-polymorphism-architect",
    "code/input-system-sgdk",
    "governance/aaa-pipeline-guardian",
    "hardware/megadrive-vdp-budget-analyst",
    "hardware/shadow-highlight-scroll-fx",
    "hardware/vram-streaming-dma-queue",
    "operation/emulator-vdp-evidence-curator",
)

REQUIRED_SCHEMAS = (
    "collision_topology_report.schema.json",
    "dma_queue_contract.schema.json",
    "scroll_fx_contract.schema.json",
    "entity_vtable_plan.schema.json",
    "state_transition_contract.schema.json",
    "aaa_pipeline_gate_report.schema.json",
    "input_mapping_contract.schema.json",
    "input_latency_contract.schema.json",
    "multiplayer_input_plan.schema.json",
    "camera_bounds_policy.schema.json",
    "parallax_camera_contract.schema.json",
    "skill_lifecycle_registry.schema.json",
)

ARCHIVED_ALIASES = (
    "level-manifest-architect",
    "color-conversion-curator",
    "dither-composite-transparency",
    "palette-cram-curator",
    "sprite-asset-budget-curator",
    "tilemap-attribute-director",
    "sfx-prep-fm-psg-pcm",
    "z80-audio-boundary-architect",
    "articulated-sprite-architect",
    "software-tile-rasterizer",
    "hscroll-linescroll-road-fx",
    "raster-palette-hint-director",
    "sprite-scanline-budgeter",
)

FORBIDDEN_INPUT_CALLS = ("JOY_read(", "JOY_getPort(", "JOY_readAll")


def load_json(path: Path, errors: list[str]) -> dict | list | None:
    if not path.is_file():
        errors.append(f"missing JSON: {path.relative_to(ROOT).as_posix()}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"unreadable JSON {path.relative_to(ROOT).as_posix()}: {exc}")
        return None


def main() -> int:
    errors: list[str] = []

    for skill_id in REQUIRED_ACTIVE_SKILLS:
        skill_dir = ACTIVE_SKILLS / skill_id
        if not (skill_dir / "SKILL.md").is_file():
            errors.append(f"required active skill missing: {skill_id}")
        if not (skill_dir / "agents" / "openai.yaml").is_file():
            errors.append(f"required skill metadata missing: {skill_id}")

    for schema_name in REQUIRED_SCHEMAS:
        if not (ROOT / "schemas" / schema_name).is_file():
            errors.append(f"required schema missing: {schema_name}")

    registry = load_json(AGENT / "references" / "skill_lifecycle_registry.json", errors)
    route_map = load_json(AGENT / "references" / "aaa_pipeline_curated_skill_map.json", errors)
    manifest = load_json(AGENT / "framework_manifest.json", errors)

    if isinstance(registry, dict):
        entries = registry.get("entries", [])
        by_id = {item.get("skill_id"): item for item in entries if isinstance(item, dict)}
        for alias in ARCHIVED_ALIASES:
            matches = [item for sid, item in by_id.items() if sid and sid.endswith(f"/{alias}")]
            if len(matches) != 1:
                errors.append(f"archived alias lifecycle entry missing or duplicated: {alias}")
            elif matches[0].get("lifecycle") == "active":
                errors.append(f"archived alias incorrectly active: {alias}")

    if isinstance(route_map, dict):
        text = json.dumps(route_map, ensure_ascii=False)
        if route_map.get("default_gate") != "aaa-pipeline-guardian":
            errors.append("curated route map default gate is not aaa-pipeline-guardian")
        for alias in ARCHIVED_ALIASES:
            if alias in text:
                errors.append(f"active route map references archived alias: {alias}")
        for required in (
            "collision-system-architect",
            "vram-streaming-dma-queue",
            "shadow-highlight-scroll-fx",
            "entity-polymorphism-architect",
            "game-state-transition-architect",
            "camera-system-sgdk",
            "input-system-sgdk",
            "emulator-vdp-evidence-curator",
        ):
            if required not in text:
                errors.append(f"active route map missing owner: {required}")
        if "experimental_requires_benchmark" not in text:
            errors.append("software raster route lacks experimental benchmark gate")

    if isinstance(manifest, dict):
        tracked = set(manifest.get("tracked_paths", []))
        for skill_id in REQUIRED_ACTIVE_SKILLS:
            if f"skills/{skill_id}" not in tracked:
                errors.append(f"framework manifest missing active owner: {skill_id}")
        manifest_text = json.dumps(manifest, ensure_ascii=False)
        for alias in ARCHIVED_ALIASES:
            if re.search(rf"skills/[^\"']*/{re.escape(alias)}(?:[\"'/])", manifest_text):
                errors.append(f"framework manifest references archived alias: {alias}")

    for skill_id in ("code/input-system-sgdk", "code/camera-system-sgdk"):
        skill_dir = ACTIVE_SKILLS / skill_id
        for path in skill_dir.rglob("*"):
            if not path.is_file():
                continue
            plain = re.sub(r"`[^`]*`", "", path.read_text(encoding="utf-8", errors="ignore"))
            for forbidden in FORBIDDEN_INPUT_CALLS:
                if forbidden in plain:
                    errors.append(f"skill uses fake input API {forbidden}: {skill_id}")

    for alias in ARCHIVED_ALIASES:
        matches = list(LEGACY_SKILLS.rglob(f"{alias}/SKILL.md"))
        if len(matches) != 1:
            errors.append(f"legacy payload missing or duplicated: {alias}")

    if errors:
        print("AAA curation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AAA curation validation passed with active-owner lifecycle routing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

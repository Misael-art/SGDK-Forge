#!/usr/bin/env python3
"""Validate the MegaDrive_DEV Codex skill framework.

This script checks the repo-native skill bridge, SKILL.md metadata,
openai.yaml discovery metadata, framework manifest coverage, pipeline
references, and known stale terminology that can confuse future agents.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
AGENT_ROOT = ROOT / "tools" / "sgdk_wrapper" / ".agent"
SKILLS_ROOT = AGENT_ROOT / "skills"
BRIDGE_ROOT = ROOT / ".agents" / "skills"
FORBIDDEN_TERMS = (
    "megadrive-elite",
    "blaze_applicability",
)


def rel(path: Path, base: Path = ROOT) -> str:
    return path.relative_to(base).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def parse_frontmatter(text: str) -> tuple[list[str], dict[str, str]] | None:
    match = re.match(r"^---\s*\n(?P<body>.*?)\n---\s*\n", text, re.S)
    if not match:
        return None

    keys: list[str] = []
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if key_match:
            key = key_match.group(1)
            keys.append(key)
            values[key] = key_match.group(2).strip().strip("\"'")
    return keys, values


def check_bridge(errors: list[str]) -> None:
    if not BRIDGE_ROOT.exists():
        errors.append(f"missing bridge: {rel(BRIDGE_ROOT)}")
        return

    if BRIDGE_ROOT.resolve() != SKILLS_ROOT.resolve():
        errors.append(
            "bridge target mismatch: "
            f"{rel(BRIDGE_ROOT)} -> {BRIDGE_ROOT.resolve()} "
            f"expected {SKILLS_ROOT.resolve()}"
        )


def check_skill_frontmatter(errors: list[str]) -> list[Path]:
    skill_files = sorted(SKILLS_ROOT.rglob("SKILL.md"))
    if not skill_files:
        errors.append(f"no skills found under {rel(SKILLS_ROOT)}")
        return []

    for skill_file in skill_files:
        parsed = parse_frontmatter(read_text(skill_file))
        if parsed is None:
            errors.append(f"missing frontmatter: {rel(skill_file)}")
            continue

        keys, values = parsed
        if keys != ["name", "description"]:
            errors.append(f"frontmatter keys must be name,description: {rel(skill_file)}")

        name = values.get("name", "")
        if name != skill_file.parent.name:
            errors.append(
                f"skill name does not match folder: {rel(skill_file)} "
                f"({name!r} != {skill_file.parent.name!r})"
            )

        if not values.get("description"):
            errors.append(f"empty skill description: {rel(skill_file)}")

    return skill_files


def check_openai_yaml(skill_files: list[Path], errors: list[str]) -> None:
    for skill_file in skill_files:
        skill_name = skill_file.parent.name
        yaml_file = skill_file.parent / "agents" / "openai.yaml"
        if not yaml_file.exists():
            errors.append(f"missing openai.yaml: {rel(yaml_file)}")
            continue

        text = read_text(yaml_file)
        short = re.search(r'short_description:\s*"([^"]*)"', text)
        prompt = re.search(r'default_prompt:\s*"([^"]*)"', text)
        implicit = re.search(r"allow_implicit_invocation:\s*(true|false)", text)

        if not short:
            errors.append(f"missing short_description: {rel(yaml_file)}")
        else:
            length = len(short.group(1))
            if length < 25 or length > 64:
                errors.append(
                    f"short_description length must be 25-64 chars: "
                    f"{rel(yaml_file)} ({length})"
                )

        if not prompt:
            errors.append(f"missing default_prompt: {rel(yaml_file)}")
        elif f"${skill_name}" not in prompt.group(1):
            errors.append(f"default_prompt must mention ${skill_name}: {rel(yaml_file)}")

        if not implicit:
            errors.append(f"missing allow_implicit_invocation policy: {rel(yaml_file)}")


def check_manifest(skill_files: list[Path], errors: list[str]) -> None:
    manifest_file = AGENT_ROOT / "framework_manifest.json"
    manifest = json.loads(read_text(manifest_file))
    tracked = {item.replace("\\", "/") for item in manifest.get("tracked_paths", [])}

    for skill_file in skill_files:
        skill_path = rel(skill_file.parent, AGENT_ROOT)
        if skill_path not in tracked:
            errors.append(f"skill missing from framework_manifest tracked_paths: {skill_path}")


def check_pipeline_references(errors: list[str]) -> None:
    pipeline_file = AGENT_ROOT / "pipelines" / "aaa_scene_v1.json"
    pipeline = json.loads(read_text(pipeline_file))

    for step in pipeline.get("steps", []):
        paths = []
        if step.get("skill_path"):
            paths.append(step["skill_path"])
        paths.extend(step.get("supporting_skills") or [])

        for skill_path in paths:
            target = AGENT_ROOT / skill_path
            if not target.exists() or not (target / "SKILL.md").exists():
                errors.append(f"pipeline references missing skill: {skill_path}")


def check_contract_blocks(skill_files: list[Path], errors: list[str]) -> None:
    required = (
        ("entrada minima", r"(?i)entrada minima|entrada m.nima"),
        ("saida minima", r"(?i)saida minima|sa.da minima"),
        ("passa quando", r"(?i)passa quando"),
        ("handoff", r"(?i)handoff"),
    )

    for skill_file in skill_files:
        text = read_text(skill_file)
        missing = [label for label, pattern in required if not re.search(pattern, text)]
        if missing:
            errors.append(
                f"skill missing contract blocks {missing}: "
                f"{rel(skill_file, SKILLS_ROOT)}"
            )


def check_forbidden_terms(errors: list[str]) -> None:
    for path in sorted(AGENT_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".yaml"}:
            continue

        text = read_text(path)
        for term in FORBIDDEN_TERMS:
            if term in text:
                errors.append(f"forbidden term {term!r}: {rel(path, AGENT_ROOT)}")


def main() -> int:
    errors: list[str] = []
    check_bridge(errors)
    skill_files = check_skill_frontmatter(errors)
    check_openai_yaml(skill_files, errors)
    check_manifest(skill_files, errors)
    check_pipeline_references(errors)
    check_contract_blocks(skill_files, errors)
    check_forbidden_terms(errors)

    if errors:
        print("Skill framework validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Skill framework validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

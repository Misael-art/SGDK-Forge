"""Validate the active SGDK skill framework and reversible legacy lifecycle."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
AGENT_ROOT = ROOT / "tools" / "sgdk_wrapper" / ".agent"
SKILLS_ROOT = AGENT_ROOT / "skills"
LEGACY_ROOT = AGENT_ROOT / "legacy" / "skills"
BRIDGE_ROOT = ROOT / ".agents" / "skills"
MANIFEST_PATH = AGENT_ROOT / "framework_manifest.json"
LIFECYCLE_PATH = AGENT_ROOT / "references" / "skill_lifecycle_registry.json"
FORBIDDEN_TERMS = ("megadrive-elite", "blaze_applicability")
CONTRACT_BLOCKS = (
    ("entrada minima", r"(?i)entrada minima|entrada m.nima"),
    ("saida minima", r"(?i)saida minima|sa.da minima"),
    ("passa quando", r"(?i)passa quando"),
    ("handoff", r"(?i)handoff"),
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
        item = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if item:
            key = item.group(1)
            keys.append(key)
            values[key] = item.group(2).strip().strip("\"'")
    return keys, values


def directory_hash(path: Path) -> str:
    payload = bytearray()
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        relative = file_path.relative_to(path).as_posix()
        file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        payload.extend(relative.encode("utf-8"))
        payload.extend(b"\0")
        payload.extend(file_hash.encode("ascii"))
        payload.extend(b"\n")
    return hashlib.sha256(payload).hexdigest()


def skill_dirs(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    if not root.exists():
        return result
    for skill_file in sorted(root.rglob("SKILL.md")):
        skill_dir = skill_file.parent
        result[skill_dir.relative_to(root).as_posix()] = skill_dir
    return result


def check_bridge(errors: list[str]) -> None:
    if not BRIDGE_ROOT.exists():
        errors.append(f"missing bridge: {rel(BRIDGE_ROOT)}")
    elif BRIDGE_ROOT.resolve() != SKILLS_ROOT.resolve():
        errors.append(
            f"bridge target mismatch: {rel(BRIDGE_ROOT)} -> "
            f"{BRIDGE_ROOT.resolve()} expected {SKILLS_ROOT.resolve()}"
        )


def check_active_structure(active: dict[str, Path], errors: list[str]) -> None:
    for yaml_file in sorted(SKILLS_ROOT.rglob("agents/openai.yaml")):
        skill_dir = yaml_file.parent.parent
        if not (skill_dir / "SKILL.md").is_file():
            errors.append(f"active skill metadata without SKILL.md: {rel(skill_dir)}")

    for skill_id, skill_dir in active.items():
        skill_file = skill_dir / "SKILL.md"
        text = read_text(skill_file)
        parsed = parse_frontmatter(text)
        if parsed is None:
            errors.append(f"missing frontmatter: {rel(skill_file)}")
        else:
            keys, values = parsed
            if keys != ["name", "description"]:
                errors.append(f"frontmatter keys must be name,description: {rel(skill_file)}")
            if values.get("name") != skill_dir.name:
                errors.append(
                    f"skill name does not match folder: {rel(skill_file)} "
                    f"({values.get('name')!r} != {skill_dir.name!r})"
                )
            if not values.get("description"):
                errors.append(f"empty skill description: {rel(skill_file)}")

        yaml_file = skill_dir / "agents" / "openai.yaml"
        if not yaml_file.is_file():
            errors.append(f"missing openai.yaml: {rel(yaml_file)}")
        else:
            yaml = read_text(yaml_file)
            short = re.search(r'short_description:\s*"([^"]*)"', yaml)
            prompt = re.search(r'default_prompt:\s*"([^"]*)"', yaml)
            implicit = re.search(r"allow_implicit_invocation:\s*(true|false)", yaml)
            if not short:
                errors.append(f"missing short_description: {rel(yaml_file)}")
            elif not 25 <= len(short.group(1)) <= 64:
                errors.append(
                    f"short_description length must be 25-64 chars: "
                    f"{rel(yaml_file)} ({len(short.group(1))})"
                )
            if not prompt:
                errors.append(f"missing default_prompt: {rel(yaml_file)}")
            elif f"${skill_dir.name}" not in prompt.group(1):
                errors.append(f"default_prompt must mention ${skill_dir.name}: {rel(yaml_file)}")
            if not implicit:
                errors.append(f"missing allow_implicit_invocation policy: {rel(yaml_file)}")

        missing = [label for label, pattern in CONTRACT_BLOCKS if not re.search(pattern, text)]
        if missing:
            errors.append(f"skill missing contract blocks {missing}: {skill_id}/SKILL.md")


def check_manifest(active: dict[str, Path], errors: list[str]) -> None:
    try:
        manifest = json.loads(read_text(MANIFEST_PATH))
    except Exception as exc:
        errors.append(f"framework manifest unreadable: {exc}")
        return
    tracked = {str(item).replace("\\", "/") for item in manifest.get("tracked_paths", [])}
    for skill_id in active:
        expected = f"skills/{skill_id}"
        if expected not in tracked:
            errors.append(f"skill missing from framework_manifest tracked_paths: {expected}")
    for item in sorted(tracked):
        if not re.match(r"^skills/[^/]+/[^/]+$", item):
            continue
        target = AGENT_ROOT / item
        if not (target / "SKILL.md").is_file():
            errors.append(f"framework_manifest references inactive or missing skill: {item}")


def check_lifecycle(active: dict[str, Path], legacy: dict[str, Path], errors: list[str]) -> None:
    try:
        registry = json.loads(read_text(LIFECYCLE_PATH))
    except Exception as exc:
        errors.append(f"skill lifecycle registry unreadable: {exc}")
        return
    entries = registry.get("entries", [])
    by_id: dict[str, dict] = {}
    for entry in entries:
        skill_id = entry.get("skill_id")
        if not isinstance(skill_id, str) or not skill_id:
            errors.append("lifecycle entry missing skill_id")
            continue
        if skill_id in by_id:
            errors.append(f"duplicate lifecycle entry: {skill_id}")
            continue
        by_id[skill_id] = entry
        lifecycle = entry.get("lifecycle")
        if lifecycle == "active":
            if skill_id not in active:
                errors.append(f"active lifecycle skill missing: {skill_id}")
            else:
                words = len(re.findall(r"\S+", read_text(active[skill_id] / "SKILL.md")))
                if words > int(entry.get("context_budget_words", 0)):
                    errors.append(
                        f"active skill exceeds context budget: {skill_id} "
                        f"({words}>{entry.get('context_budget_words')})"
                    )
        else:
            if skill_id in active:
                errors.append(f"legacy lifecycle skill still active: {skill_id}")
            if skill_id not in legacy:
                errors.append(f"legacy lifecycle payload missing: {skill_id}")
            elif directory_hash(legacy[skill_id]) != entry.get("content_sha256"):
                errors.append(f"legacy lifecycle hash mismatch: {skill_id}")

        for replacement in entry.get("replacement_skills", []):
            if replacement not in active:
                errors.append(f"replacement skill is not active: {skill_id} -> {replacement}")

    for skill_id in legacy:
        if skill_id not in by_id:
            errors.append(f"legacy skill unregistered: {skill_id}")
        elif by_id[skill_id].get("lifecycle") == "active":
            errors.append(f"legacy payload marked active: {skill_id}")


def check_pipeline_references(errors: list[str]) -> None:
    pipeline_file = AGENT_ROOT / "pipelines" / "aaa_scene_v1.json"
    try:
        pipeline = json.loads(read_text(pipeline_file))
    except Exception as exc:
        errors.append(f"pipeline unreadable: {exc}")
        return
    for step in pipeline.get("steps", []):
        paths: list[str] = []
        if step.get("skill_path"):
            paths.append(step["skill_path"])
        paths.extend(step.get("supporting_skills") or [])
        for skill_path in paths:
            target = AGENT_ROOT / skill_path
            if not (target / "SKILL.md").is_file():
                errors.append(f"pipeline references missing skill: {skill_path}")


def check_forbidden_terms(errors: list[str]) -> None:
    for path in sorted(AGENT_ROOT.rglob("*")):
        if LEGACY_ROOT in path.parents:
            continue
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".yaml"}:
            continue
        text = read_text(path)
        for term in FORBIDDEN_TERMS:
            if term in text:
                errors.append(f"forbidden term {term!r}: {rel(path, AGENT_ROOT)}")


def main() -> int:
    errors: list[str] = []
    active = skill_dirs(SKILLS_ROOT)
    legacy = skill_dirs(LEGACY_ROOT)
    if not active:
        errors.append(f"no active skills found under {rel(SKILLS_ROOT)}")
    check_bridge(errors)
    check_active_structure(active, errors)
    check_manifest(active, errors)
    check_lifecycle(active, legacy, errors)
    check_pipeline_references(errors)
    check_forbidden_terms(errors)
    if errors:
        print("Skill framework validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Skill framework validation passed: {len(active)} active, {len(legacy)} legacy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate the workspace template registry."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_TEMPLATE_FIELDS = {
    "id",
    "path",
    "status",
    "purpose",
    "used_by_scripts",
    "has_mddev_project_json",
    "has_build_bat",
    "has_run_bat",
    "has_clean_bat",
    "has_rebuild_bat",
    "has_src",
    "has_inc",
    "has_res",
    "has_doc",
    "contains_out",
    "file_count",
    "dir_count",
    "bytes",
    "recommendation",
}

ALLOWED_STATUS = {
    "CANONICAL_BOOTSTRAP",
    "REFERENCE_TEMPLATE",
    "LOGIC_TEMPLATE",
    "LEGACY_TEMPLATE",
    "PARTIAL_TEMPLATE",
    "OWNER_REVIEW",
}


def main() -> int:
    repo = Path(__file__).resolve().parents[4]
    registry_path = repo / "doc" / "template_registry.json"
    errors: list[str] = []
    warnings: list[str] = []

    if not registry_path.exists():
        print(f"ERROR: missing {registry_path}")
        return 1

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}")
        return 1

    templates = registry.get("templates")
    if not isinstance(templates, list) or not templates:
        errors.append("registry.templates must be a non-empty list")
        templates = []

    canonical = [t for t in templates if t.get("status") == "CANONICAL_BOOTSTRAP"]
    if len(canonical) != 1:
        errors.append(f"expected exactly one CANONICAL_BOOTSTRAP, found {len(canonical)}")
    elif canonical[0].get("path") != "tools/sgdk_wrapper/modelo":
        if not registry.get("canonical_override_justification"):
            errors.append("canonical bootstrap differs from tools/sgdk_wrapper/modelo without justification")

    for index, template in enumerate(templates):
        missing = sorted(REQUIRED_TEMPLATE_FIELDS - set(template))
        if missing:
            errors.append(f"template[{index}] missing fields: {', '.join(missing)}")
            continue

        if template["status"] not in ALLOWED_STATUS:
            errors.append(f"{template['id']}: invalid status {template['status']}")

        path = repo / template["path"]
        if not path.exists():
            errors.append(f"{template['id']}: path does not exist: {template['path']}")

        if template["status"] in {"CANONICAL_BOOTSTRAP", "REFERENCE_TEMPLATE", "LOGIC_TEMPLATE"} and template.get("contains_out"):
            warnings.append(f"{template['id']}: active template contains out/ artifacts")

    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        return 1

    print(f"template registry ok: {len(templates)} templates, canonical={canonical[0]['path'] if canonical else 'n/a'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

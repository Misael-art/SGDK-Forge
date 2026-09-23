#!/usr/bin/env python3
"""Classify legacy lifecycle hash drift without mutating the registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
AGENT_ROOT = ROOT / "tools/sgdk_wrapper/.agent"
LEGACY_ROOT = AGENT_ROOT / "legacy/skills"
REGISTRY_PATH = AGENT_ROOT / "references/skill_lifecycle_registry.json"
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt"}


def normalized_bytes(path: Path, raw: bytes) -> bytes:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return raw


def payload_hash(files: list[tuple[str, bytes]]) -> str:
    payload = bytearray()
    for relative, raw in sorted(files):
        digest = hashlib.sha256(normalized_bytes(Path(relative), raw)).hexdigest()
        payload.extend(relative.encode("utf-8"))
        payload.extend(b"\0")
        payload.extend(digest.encode("ascii"))
        payload.extend(b"\n")
    return hashlib.sha256(payload).hexdigest()


def working_hash(path: Path) -> str:
    return payload_hash([
        (file_path.relative_to(path).as_posix(), file_path.read_bytes())
        for file_path in path.rglob("*")
        if file_path.is_file()
    ])


def git(*args: str, text: bool = True) -> str | bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=text)


def introduction_commit(relative_path: str) -> str | None:
    output = str(git("log", "--diff-filter=A", "--format=%H", "--", relative_path)).strip().splitlines()
    return output[-1] if output else None


def committed_hash(commit: str, prefix: str) -> str | None:
    names = str(git("ls-tree", "-r", "--name-only", commit, "--", prefix)).splitlines()
    if not names:
        return None
    files: list[tuple[str, bytes]] = []
    for name in names:
        raw = git("show", f"{commit}:{name}", text=False)
        assert isinstance(raw, bytes)
        files.append((name[len(prefix) + 1 :], raw))
    return payload_hash(files)


def audit() -> dict[str, Any]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []
    for entry in registry.get("entries", []):
        if entry.get("lifecycle") == "active":
            continue
        skill_id = str(entry["skill_id"])
        path = LEGACY_ROOT / skill_id
        relative_path = path.relative_to(ROOT).as_posix()
        current_hash = working_hash(path)
        introduced_commit = introduction_commit(relative_path)
        introduced_hash = committed_hash(introduced_commit, relative_path) if introduced_commit else None
        status_output = str(git("status", "--porcelain", "--untracked-files=all", "--", relative_path)).strip()
        registry_hash = str(entry.get("content_sha256") or "")
        if status_output:
            classification = "payload_change_requires_review"
        elif introduced_hash == current_hash and registry_hash != current_hash:
            classification = "registry_obsolete_at_introduction"
        elif registry_hash == current_hash:
            classification = "already_consistent"
        else:
            classification = "historical_drift_requires_review"
        skill_file = path / "SKILL.md"
        records.append({
            "skill_id": skill_id,
            "lifecycle": entry.get("lifecycle"),
            "legacy_path": relative_path,
            "replacement_skills": entry.get("replacement_skills") or [],
            "registry_sha256": registry_hash,
            "working_sha256": current_hash,
            "introduction_commit": introduced_commit,
            "introduction_sha256": introduced_hash,
            "working_tree_clean": not bool(status_output),
            "working_tree_status": status_output or None,
            "classification": classification,
            "review": {
                "skill_file_present": skill_file.is_file(),
                "skill_file_sha256": hashlib.sha256(normalized_bytes(skill_file, skill_file.read_bytes())).hexdigest() if skill_file.is_file() else None,
                "word_count": len(skill_file.read_text(encoding="utf-8", errors="ignore").split()) if skill_file.is_file() else 0,
                "replacement_count": len(entry.get("replacement_skills") or []),
            },
            "recommended_registry_sha256": current_hash if classification == "registry_obsolete_at_introduction" else None,
        })
    blocking = [record["skill_id"] for record in records if record["classification"] not in {"already_consistent", "registry_obsolete_at_introduction"}]
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tool_name": "audit_legacy_hash_reconciliation",
        "status": "reviewable" if not blocking else "blocked",
        "mutation_performed": False,
        "hash_algorithm": "sha256_directory_manifest_text_lf_normalized_v1",
        "registry_path": REGISTRY_PATH.relative_to(ROOT).as_posix(),
        "record_count": len(records),
        "blocking_records": blocking,
        "classification_counts": {
            classification: sum(record["classification"] == classification for record in records)
            for classification in sorted({record["classification"] for record in records})
        },
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = audit()
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "records": report["record_count"], "blocking": len(report["blocking_records"])}))
    return 0 if report["status"] == "reviewable" else 1


if __name__ == "__main__":
    raise SystemExit(main())

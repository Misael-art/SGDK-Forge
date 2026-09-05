#!/usr/bin/env python3
"""Auditor de proveniência de assets de audio (sfx_bank_manifest).

Espelha o que `audit_procedural_asset_provenance.py` ja faz para o lado visual
(AUDIT_PROVENANCE no SGDK_GLOBAL.md 8.2), aplicado a som: um SFX/musica de
"final" nao pode nascer de primitiva procedural (synth de cortina), todo
asset autoral/composto precisa de hash persistido, e a taxa precisa ser XGM2.

O manifesto e lido de `doc/sfx_bank_manifest.json` no projeto (passivel de
sobrescrita via `--manifest`), e o auditor cruza com os simbolos declarados em
`res/resources.res` (linhas `XGM2 <name> <file>` e `WAV <name> <file> XGM2 <rate>`).

Blockers emitidos:
  audio_provenance_undeclared        simbolo no .res sem entrada no manifesto
  audio_synth_promoted_final         source_kind=synthesized com acceptance_status=final
  audio_missing_hash                 aceito autoral/final sem sha256
  audio_invalid_rate                 taxa fora de {6650,13300}
  audio_unknown_status               acceptance_status fora do vocabulario
  audio_unknown_kind                 source_kind fora do vocabulario

Exemplo:
  python3 tools/audio-tools/audit_audio_provenance.py \\
      --project-root "SGDK_projects/<projeto>" --manifest doc/sfx_bank_manifest.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from audio_core import SCHEMA_VERSION, XGM2_RATES, now_iso, sha256_file

TOOL_NAME = "audit_audio_provenance"
TOOL_VERSION = "1.0.0"

ACCEPTED_KINDS = frozenset({
    "hand_authored", "ai_generated", "photo_or_render_derived",
    "procedural_composed_from_authored", "procedural_primitive",
    "synthesized", "licensed_reference", "sgdk_builtin", "unverified",
})
ACCEPTED_STATUS = frozenset({
    "final", "placeholder", "lab", "debug_lab",
    "visual_lab_control", "licensed_reference",
})
# proibido esta combinacao final: primitiva procedural/synth nao pode ser final
FORBIDDEN_FINAL_KINDS = frozenset({"procedural_primitive", "synthesized"})

RES_XGM2_RE = re.compile(r"^\s*XGM2\s+(\S+)\s+\"([^\"]+)\"\s*", re.IGNORECASE)
RES_WAV_RE = re.compile(r"^\s*WAV\s+(\S+)\s+\"([^\"]+)\"\s+\S+\s*(\S*)\s*", re.IGNORECASE)


def parse_res_symbols(res_path: Path) -> dict:
    """Devolve {simbolo: {kind, file, rate}} lido de res/resources.res."""
    symbols: dict[str, dict] = {}
    if not res_path.is_file():
        return symbols
    for line in res_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = RES_XGM2_RE.match(line)
        if m:
            if m.group(1) in symbols:
                raise ValueError(f"simbolo de audio duplicado em resources.res: {m.group(1)}")
            symbols[m.group(1)] = {"type": "music", "file": m.group(2), "rate": None}
            continue
        m = RES_WAV_RE.match(line)
        if m:
            if m.group(1) in symbols:
                raise ValueError(f"simbolo de audio duplicado em resources.res: {m.group(1)}")
            rate_str = m.group(3)
            symbols[m.group(1)] = {
                "type": "sfx", "file": m.group(2),
                "rate": int(rate_str) if rate_str else None,
            }
    return symbols


def safe_relative_path(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    return path.as_posix()


def audit_entry(entry: dict, errors: list[str], warnings: list[str]) -> None:
    eid = entry.get("id") or entry.get("name") or "<sem-id>"
    status = entry.get("acceptance_status")
    kind = entry.get("source_kind")

    if status not in ACCEPTED_STATUS:
        errors.append(f"{eid}: audio_unknown_status ({status})")
    if kind not in ACCEPTED_KINDS:
        errors.append(f"{eid}: audio_unknown_kind ({kind})")

    if kind in FORBIDDEN_FINAL_KINDS and status == "final":
        errors.append(f"{eid}: audio_synth_promoted_final (a origem {kind} nao pode ser final)")

    if kind == "unverified" and status == "final":
        errors.append(f"{eid}: audio_unverified_promoted_final (origem nao verificada nao pode ser final)")

    if status not in ("placeholder", None) and not entry.get("sha256"):
        errors.append(f"{eid}: audio_missing_hash (aceito autoral/final sem hash)")

    rate = entry.get("rate")
    if rate is not None and int(rate) not in XGM2_RATES:
        errors.append(f"{eid}: audio_invalid_rate ({rate})")

    if entry.get("type") == "sfx" and not entry.get("channel"):
        warnings.append(f"{eid}: sem ownership de canal declarado (XGM2 mg: CH2/CH3)")


def audit(manifest_path: Path, project_root: Path | None,
          verify_hashes: bool) -> dict:
    if not manifest_path.is_file():
        return {
            "schema_version": SCHEMA_VERSION,
            "tool": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "generated_at": now_iso(),
            "error": f"manifesto nao encontrado: {manifest_path}",
            "blocking": True,
            "blockers": ["audio_provenance_manifest_missing"],
        }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("entries", [])
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(entries, list):
        entries = []
        errors.append("audio_manifest_entries_invalid (entries deve ser array)")

    known: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("audio_manifest_entry_invalid (entrada nao e objeto)")
            continue
        eid = entry.get("id") or entry.get("name")
        if not isinstance(eid, str) or not eid:
            errors.append("audio_manifest_id_missing")
            continue
        if eid in known:
            errors.append(f"{eid}: audio_manifest_duplicate_id")
            continue
        known[eid] = entry

    for entry in entries:
        if isinstance(entry, dict):
            audit_entry(entry, errors, warnings)
            if safe_relative_path(entry.get("file")) is None:
                eid = entry.get("id") or entry.get("name") or "<sem-id>"
                errors.append(f"{eid}: audio_unsafe_or_missing_path")

    # hash verificado contra o ficheiro se `verify_hashes`
    if verify_hashes:
        root = (project_root or manifest_path.parent).resolve()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            eid = entry.get("id") or entry.get("name") or "<sem-id>"
            file_rel = safe_relative_path(entry.get("file"))
            if file_rel is None:
                continue
            fp = (root / file_rel).resolve()
            if not fp.is_relative_to(root):
                errors.append(f"{eid}: audio_path_escapes_project ({file_rel})")
                continue
            if fp.is_file():
                entry_sha = entry.get("sha256")
                if entry_sha and sha256_file(fp) != entry_sha:
                    errors.append(f"{eid}: hash diverge do ficheiro {file_rel}")
            else:
                errors.append(f"{eid}: ficheiro declarado ausente ({file_rel})")

    # cruza com o .res
    if project_root is not None:
        try:
            res_symbols = parse_res_symbols(project_root / "res" / "resources.res")
        except ValueError as exc:
            errors.append(f"audio_resources_duplicate_symbol ({exc})")
            res_symbols = {}
        for symbol, info in res_symbols.items():
            if symbol not in known:
                errors.append(
                    f"{symbol}: audio_provenance_undeclared ({info['type']} "
                    f"em resources.res sem entrada no manifesto)")
                continue
            entry = known[symbol]
            declared_file = safe_relative_path(entry.get("file"))
            resource_file = (Path("res") / info["file"]).as_posix()
            if declared_file != resource_file:
                errors.append(
                    f"{symbol}: audio_resource_path_mismatch "
                    f"(manifest={declared_file}, resources.res={resource_file})")
            if entry.get("type") != info["type"]:
                errors.append(
                    f"{symbol}: audio_resource_type_mismatch "
                    f"(manifest={entry.get('type')}, resources.res={info['type']})")
            if info["type"] == "sfx" and entry.get("rate") != info["rate"]:
                errors.append(
                    f"{symbol}: audio_resource_rate_mismatch "
                    f"(manifest={entry.get('rate')}, resources.res={info['rate']})")
        for symbol in sorted(set(known) - set(res_symbols)):
            warnings.append(f"{symbol}: manifesto sem simbolo ativo em resources.res")

    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "generated_at": now_iso(),
        "manifest": str(manifest_path),
        "entries_total": len(entries),
        "errors": errors,
        "warnings": warnings,
        "blocking": bool(errors),
        "blockers": sorted({e for e in errors}),
    }


GOOD_MANIFEST = {
    "bank": "chase",
    "entries": [
        {
            "id": "snd_chase_hit", "type": "sfx", "file": "res/audio/chase/chase_hit.wav",
            "source_kind": "hand_authored", "acceptance_status": "final",
            "rate": 13300, "channel": 2, "priority": 13, "sha256": "cafe" * 8,
        },
        {
            "id": "snd_chase_menu", "type": "sfx", "file": "res/audio/chase/chase_menu.wav",
            "source_kind": "hand_authored", "acceptance_status": "final",
            "rate": 13300, "channel": 3, "priority": 5, "sha256": "dead" * 8,
        },
        {
            "id": "mus_chase_core", "type": "music", "file": "res/audio/chase/chase_core_fm_psg.vgm",
            "source_kind": "hand_authored", "acceptance_status": "final",
            "sha256": "beef" * 8,
        },
    ],
}

BAD_MANIFEST = {
    "bank": "chase",
    "entries": [
        {
            "id": "snd_chase_hit", "type": "sfx", "file": "res/audio/chase/chase_hit.wav",
            "source_kind": "synthesized", "acceptance_status": "final",
            "rate": 8000, "channel": 2, "priority": 13,
        },
        {
            "id": "snd_phantom", "type": "sfx", "file": "res/audio/chase/phantom.wav",
            "source_kind": "hand_authored", "acceptance_status": "final",
            "rate": 13300, "channel": 3, "priority": 5,
        },
    ],
}


def _positive_fixtures(tmpdir: Path) -> list[dict]:
    name = "audio_provenance_accepts_clean"
    fails = []
    try:
        manifest = tmpdir / "sfx_bank_manifest.json"
        manifest.write_text(json.dumps(GOOD_MANIFEST), encoding="utf-8")
        report = audit(manifest, None, verify_hashes=False)
        if report["blocking"]:
            fails.append(f"manifesto limpo bloqueou: {report['blockers']}")
    except Exception as exc:  # noqa: BLE001
        fails.append(f"excecao: {exc}")
    return [{
        "fixture": name,
        "kind": "positive",
        "passed": not fails,
        "blocker": "audio_self_check_failed:" + name,
        "detail": fails,
    }]


def _negative_fixtures(tmpdir: Path) -> list[dict]:
    fixtures = []
    manifest = tmpdir / "sfx_bank_manifest.json"
    manifest.write_text(json.dumps(BAD_MANIFEST), encoding="utf-8")
    report = audit(manifest, None, verify_hashes=False)
    caught = {
        "synth_promoted_final": any("audio_synth_promoted_final" in b for b in report["blockers"]),
        "invalid_rate": any("audio_invalid_rate" in b for b in report["blockers"]),
        "missing_hash": any("audio_missing_hash" in b for b in report["blockers"]),
    }
    for label, expected in caught.items():
        fixtures.append({
            "fixture": f"rejects_{label}",
            "kind": "negative",
            "passed": expected,
            "blocker": f"audio_self_check_expected_blocker:rejects_{label}",
            "detail": [] if expected else [f"nao detectou {label}"],
        })

    unsafe_manifest = tmpdir / "unsafe_manifest.json"
    unsafe = json.loads(json.dumps(GOOD_MANIFEST))
    unsafe["entries"][0]["file"] = "../../escape.wav"
    unsafe_manifest.write_text(json.dumps(unsafe), encoding="utf-8")
    unsafe_report = audit(unsafe_manifest, None, verify_hashes=False)
    caught_unsafe = any("audio_unsafe_or_missing_path" in item
                        for item in unsafe_report["blockers"])
    fixtures.append({
        "fixture": "rejects_path_traversal",
        "kind": "negative",
        "passed": caught_unsafe,
        "blocker": "audio_self_check_expected_blocker:rejects_path_traversal",
        "detail": [] if caught_unsafe else ["nao bloqueou traversal no caminho do asset"],
    })

    duplicate_manifest = tmpdir / "duplicate_manifest.json"
    duplicate = json.loads(json.dumps(GOOD_MANIFEST))
    duplicate["entries"].append(dict(duplicate["entries"][0]))
    duplicate_manifest.write_text(json.dumps(duplicate), encoding="utf-8")
    duplicate_report = audit(duplicate_manifest, None, verify_hashes=False)
    caught_duplicate = any("audio_manifest_duplicate_id" in item
                           for item in duplicate_report["blockers"])
    fixtures.append({
        "fixture": "rejects_duplicate_manifest_id",
        "kind": "negative",
        "passed": caught_duplicate,
        "blocker": "audio_self_check_expected_blocker:rejects_duplicate_manifest_id",
        "detail": [] if caught_duplicate else ["nao bloqueou ID duplicado"],
    })

    project = tmpdir / "project"
    (project / "res").mkdir(parents=True)
    (project / "res" / "resources.res").write_text(
        'WAV snd_chase_hit "audio/chase/chase_hit.wav" XGM2 13300\n',
        encoding="utf-8",
    )
    mismatch_manifest = project / "manifest.json"
    mismatch = {
        "entries": [{
            "id": "snd_chase_hit",
            "type": "sfx",
            "file": "res/audio/chase/other.wav",
            "source_kind": "hand_authored",
            "acceptance_status": "lab",
            "rate": 6650,
            "channel": 2,
            "sha256": "cafe" * 8,
        }],
    }
    mismatch_manifest.write_text(json.dumps(mismatch), encoding="utf-8")
    mismatch_report = audit(mismatch_manifest, project, verify_hashes=False)
    caught_binding = (
        any("audio_resource_path_mismatch" in item for item in mismatch_report["blockers"])
        and any("audio_resource_rate_mismatch" in item for item in mismatch_report["blockers"])
    )
    fixtures.append({
        "fixture": "rejects_resources_binding_mismatch",
        "kind": "negative",
        "passed": caught_binding,
        "blocker": "audio_self_check_expected_blocker:rejects_resources_binding_mismatch",
        "detail": [] if caught_binding else ["nao bloqueou path/rate divergentes do .res"],
    })
    return fixtures


def self_check() -> dict:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        fixtures = _positive_fixtures(tmpdir) + _negative_fixtures(tmpdir)
    failed = [f for f in fixtures if not f["passed"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "rule_ref": "SGDK_GLOBAL.md 8.2 (proveniência) + xgm2.txt",
        "exercised": (
            "manifesto limpo passa; synth->final, taxa invalida, hash ausente, "
            "traversal, ID duplicado e binding divergente do .res bloqueiam."
        ),
        "limitation": "Audita proveniência e formato. Nao prova qualidade auditiva.",
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f["blocker"] for f in failed if not f["passed"]}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TOOL_NAME + " (proveniência de audio).")
    parser.add_argument("--project-root", dest="project_root",
                        help="raiz do projeto SGDK (para ler res/resources.res).")
    parser.add_argument("--manifest", dest="manifest", default="doc/sfx_bank_manifest.json",
                        help="caminho do sfx_bank_manifest.json.")
    parser.add_argument("--verify-hashes", dest="verify_hashes", action="store_true",
                        help="re-hash dos ficheiros declarados e compara com sha256.")
    parser.add_argument("--self-check", action="store_true",
                        help="Roda fixtures positivas e negativas e emite report JSON.")
    args = parser.parse_args(argv)

    if args.self_check:
        report = self_check()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1 if report["blocking"] else 0

    project_root = Path(args.project_root) if args.project_root else None
    manifest_path = Path(args.manifest) if args.manifest else None
    manifest_base = project_root / manifest_path if project_root and manifest_path else manifest_path
    if manifest_base is None or (project_root is None and manifest_path is None):
        parser.print_help()
        return 2
    report = audit(manifest_base, project_root, args.verify_hashes)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main())

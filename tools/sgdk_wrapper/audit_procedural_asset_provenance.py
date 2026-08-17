#!/usr/bin/env python3
"""Audit the aesthetic blocking directive: no code-drawn graphics in the final build.

Measures what SGDK_GLOBAL rules 8.2 and 17 already state in prose:

  - every visual symbol in res/*.res must declare provenance in
    doc/asset_provenance_manifest.json;
  - art drawn by code primitives (PIL/ImageDraw, polygons, solid fills) can be
    placeholder, debug_lab or visual_lab_control, never a final character,
    enemy, boss or scenery asset;
  - runtime primitive drawing (tile synthesis, solid plane fills) is only legal
    inside debug/telemetry scope;
  - a validator fixture may ship without external assets, but then it may not
    claim visual delivery.

Output is ASCII-safe on purpose: Unicode icons break CP1252 hosts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"

# Resource kinds that put pixels on screen. WAV/XGM/BIN are out of scope.
VISUAL_RES_KINDS = {"IMAGE", "SPRITE", "TILESET", "TILEMAP", "MAP", "BITMAP", "PALETTE"}

# Kinds that represent a character, enemy, boss or scenery to the player.
# PALETTE alone paints nothing, so it never blocks on its own.
PIXEL_BEARING_KINDS = {"IMAGE", "SPRITE", "TILESET", "TILEMAP", "MAP", "BITMAP"}

RES_ENTRY_RE = re.compile(
    r"^\s*(?P<kind>[A-Z][A-Z0-9_]*)\s+(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)\s+"
    r'(?:"(?P<qpath>[^"]+)"|(?P<upath>\S+))',
)

# PIL/Pillow primitive drawing surface.
PRIMITIVE_CALL_RE = re.compile(
    r"\.(?:rectangle|rounded_rectangle|ellipse|polygon|line|arc|chord|pieslice|point|"
    r"regular_polygon|bitmap|text)\s*\("
)
IMAGEDRAW_RE = re.compile(r"\bImageDraw\b|\bImage\s*\.\s*new\s*\(")

# Runtime graphics authored in C instead of imported from res/.
#
# Only pixel authorship counts here. TILE_USER_INDEX, VDP_setTileMapXY and
# VDP_fillTileMapRect are VRAM addressing and map composition for assets that
# were imported by ResComp; flagging them makes the gate cry wolf in every
# healthy project. The real violation is tile pixel data written as C literals.
TILE_UPLOAD_RE = re.compile(
    r"\bVDP_(?:loadTileData|loadTileSet|setTileData)\s*\(\s*&?\s*"
    r"(?P<arg>[A-Za-z_][A-Za-z0-9_]*)"
)
# Tile pixel data in SGDK is u32[8] per tile: eight 8-digit words, one per row.
# Restricting to u32 + 8-digit literals keeps hand-authored palettes (u16[16] of
# 4-digit CRAM entries) out of the finding, which is legitimate palette work.
TILE_ARRAY_DECL_RE = re.compile(
    r"\b(?:static\s+)?const\s+u32\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\[",
)
HEX_WORD_RE = re.compile(r"0x[0-9a-fA-F]{8}\b")
PALETTE_NAME_RE = re.compile(r"(?i)pal(?:ette)?\b|_pal\b|^pal_")
MIN_AUTHORED_HEX_WORDS = 16

DEBUG_SCOPE_RE = re.compile(r"(?i)debug|telemetry|telemetria|hitbox|overlay_dbg|_dbg|diag")

SKIP_DIR_PARTS = {
    "out",
    "build",
    "rascunho",
    ".git",
    "__pycache__",
    "node_modules",
    "boot",
    "res_generated",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except (OSError, UnicodeDecodeError):
            continue
    return ""


def walkable(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    if not root.is_dir():
        return found
    for path in root.rglob("*"):
        if path.suffix.lower() not in suffixes:
            continue
        if SKIP_DIR_PARTS & {part.lower() for part in path.relative_to(root).parts}:
            continue
        if path.is_file():
            found.append(path)
    return found


def parse_res_files(project_root: Path) -> list[dict[str, Any]]:
    """Collect every visual symbol declared across res/**/*.res."""
    symbols: list[dict[str, Any]] = []
    for res_file in sorted(walkable(project_root / "res", (".res",))):
        rel_res = res_file.relative_to(project_root).as_posix()
        for line_no, raw in enumerate(read_text(res_file).splitlines(), start=1):
            line = raw.split("//", 1)[0].strip()
            if not line:
                continue
            match = RES_ENTRY_RE.match(line)
            if not match:
                continue
            kind = match.group("kind").upper()
            if kind not in VISUAL_RES_KINDS:
                continue
            asset_path = (match.group("qpath") or match.group("upath") or "").strip()
            symbols.append(
                {
                    "res_symbol": match.group("symbol"),
                    "res_kind": kind,
                    "asset_path": asset_path,
                    "res_file": rel_res,
                    "res_line": line_no,
                }
            )
    return symbols


def collect_primitive_builders(
    project_root: Path, extra_roots: list[Path]
) -> list[dict[str, Any]]:
    """Find Python builders that draw with primitives rather than import art."""
    builders: list[dict[str, Any]] = []
    seen: set[Path] = set()
    for root in [project_root, *extra_roots]:
        for script in sorted(walkable(root, (".py",))):
            resolved = script.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            text = read_text(script)
            if not IMAGEDRAW_RE.search(text):
                continue
            calls = len(PRIMITIVE_CALL_RE.findall(text))
            if calls == 0:
                continue
            builders.append(
                {
                    "path": script.as_posix(),
                    "primitive_calls": calls,
                    "_text": text,
                    "traced_symbols": [],
                }
            )
    return builders


def trace_builders_to_symbols(
    symbols: list[dict[str, Any]], builders: list[dict[str, Any]]
) -> None:
    """Link a builder to a res symbol when the builder writes that exact file name.

    Basename matching is deliberate: it proves the producer without guessing
    from the asset file name, which is what the old quarantine audit did.
    """
    for symbol in symbols:
        basename = Path(symbol["asset_path"]).name
        stem = Path(basename).stem
        hits: list[str] = []
        for builder in builders:
            text = builder["_text"]
            if basename and basename in text:
                hits.append(builder["path"])
                builder["traced_symbols"].append(symbol["res_symbol"])
            elif stem and len(stem) >= 8 and stem in text:
                hits.append(builder["path"])
                builder["traced_symbols"].append(symbol["res_symbol"])
        symbol["primitive_builders"] = sorted(set(hits))


def scan_runtime_authored_tiles(project_root: Path) -> list[dict[str, Any]]:
    """Find tile pixel data authored as C literals and uploaded to VRAM.

    Two shapes count as authorship:
      - a const array holding many hex words that is passed to a tile upload API;
      - a const array holding many hex words that looks like a tile bank even
        when the upload is indirect.
    """
    hits: list[dict[str, Any]] = []
    for source in sorted(walkable(project_root / "src", (".c", ".h"))):
        rel = source.relative_to(project_root).as_posix()
        text = read_text(source)
        lines = text.splitlines()
        debug_file = bool(DEBUG_SCOPE_RE.search(rel))

        # Map every locally declared const array to its hex-literal density.
        authored_arrays: dict[str, dict[str, Any]] = {}
        for match in TILE_ARRAY_DECL_RE.finditer(text):
            name = match.group("name")
            if PALETTE_NAME_RE.search(name):
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            window = text[match.end() : match.end() + 4096]
            body = window.split(";", 1)[0]
            hex_words = len(HEX_WORD_RE.findall(body))
            if hex_words >= MIN_AUTHORED_HEX_WORDS:
                authored_arrays[name] = {"line": line_no, "hex_words": hex_words}

        uploaded: set[str] = set()
        for line_no, line in enumerate(lines, start=1):
            code = line.split("//", 1)[0]
            match = TILE_UPLOAD_RE.search(code)
            if not match:
                continue
            arg = match.group("arg")
            uploaded.add(arg)
            if arg in authored_arrays:
                hits.append(
                    {
                        "file": rel,
                        "api": "authored_tile_data_upload",
                        "line": line_no,
                        "symbol": arg,
                        "hex_words": authored_arrays[arg]["hex_words"],
                        "debug_scoped": debug_file or bool(DEBUG_SCOPE_RE.search(line)),
                    }
                )

        for name, info in authored_arrays.items():
            if name in uploaded:
                continue
            hits.append(
                {
                    "file": rel,
                    "api": "authored_tile_data_array",
                    "line": info["line"],
                    "symbol": name,
                    "hex_words": info["hex_words"],
                    "debug_scoped": debug_file,
                }
            )
    return hits


def load_context(project_root: Path) -> dict[str, Any]:
    data = read_json(project_root / "doc" / "project_context_manifest.json")
    if not isinstance(data, dict):
        return {}
    return data


def audit(project_root: Path, extra_roots: list[Path]) -> dict[str, Any]:
    context = load_context(project_root)
    context_type = str(context.get("context_type", "unknown"))

    manifest_path = project_root / "doc" / "asset_provenance_manifest.json"
    manifest = read_json(manifest_path)
    if manifest is None:
        manifest_status = "absent" if not manifest_path.exists() else "invalid"
        entries: list[dict[str, Any]] = []
    elif not isinstance(manifest, dict) or not isinstance(manifest.get("entries"), list):
        manifest_status = "invalid"
        entries = []
    else:
        manifest_status = "present"
        entries = [e for e in manifest["entries"] if isinstance(e, dict)]

    fixture_declared = bool(
        (isinstance(manifest, dict) and manifest.get("validator_fixture"))
        or context.get("validator_fixture")
    )

    symbols = parse_res_files(project_root)
    builders = collect_primitive_builders(project_root, extra_roots)
    trace_builders_to_symbols(symbols, builders)
    runtime_hits = scan_runtime_authored_tiles(project_root)

    by_symbol = {str(e.get("res_symbol")): e for e in entries}
    findings: list[dict[str, Any]] = []

    def add(code: str, severity: str, subject: str, message: str, evidence: str = "") -> None:
        findings.append(
            {
                "code": code,
                "severity": severity,
                "subject": subject,
                "message": message,
                "evidence": evidence,
            }
        )

    pixel_symbols = [s for s in symbols if s["res_kind"] in PIXEL_BEARING_KINDS]

    if not pixel_symbols and not fixture_declared:
        add(
            "resources_res_missing_for_visual_delivery",
            "blocking",
            "res/resources.res",
            "Nenhum simbolo visual externo declarado. Entrega [TECHDEMO]/[RELEASE] exige "
            "consumir sprite sheets e tilesets reais.",
            "res/",
        )

    if fixture_declared:
        ceiling = str(context.get("delivery_claim_ceiling", ""))
        if ceiling not in {"none", "concept", "lab", "exercise"}:
            add(
                "validator_fixture_claiming_visual_delivery",
                "blocking",
                "delivery_claim_ceiling",
                "Fixture de validador nao pode sustentar claim de entrega visual. "
                "delivery_claim_ceiling deve ser none, concept, lab ou exercise.",
                f"delivery_claim_ceiling={ceiling or 'undeclared'}",
            )
        if pixel_symbols:
            add(
                "validator_fixture_claiming_visual_delivery",
                "warning",
                "res/resources.res",
                "Fixture declarado mas ha simbolos visuais no .res. Se o projeto tem arte de "
                "verdade, ele nao e fixture: remova validator_fixture e cumpra o gate completo.",
                f"{len(pixel_symbols)} simbolos",
            )

    if manifest_status != "present" and pixel_symbols:
        add(
            "asset_provenance_manifest_absent"
            if manifest_status == "absent"
            else "asset_provenance_manifest_invalid",
            "blocking",
            "doc/asset_provenance_manifest.json",
            "Manifesto de proveniencia ausente ou invalido. Sem ele nenhum asset visual "
            "pode ser aceito como final.",
            manifest_path.as_posix(),
        )

    for symbol in symbols:
        entry = by_symbol.get(symbol["res_symbol"])
        pixel_bearing = symbol["res_kind"] in PIXEL_BEARING_KINDS
        primitive_builders = symbol.get("primitive_builders") or []

        if entry is None:
            symbol["provenance"] = "undeclared"
            if pixel_bearing and not fixture_declared:
                severity = "blocking"
                code = (
                    "procedural_asset_promoted_to_res"
                    if primitive_builders
                    else "asset_provenance_undeclared"
                )
                message = (
                    "Asset visual final produzido por builder de primitivas sem proveniencia "
                    "declarada."
                    if primitive_builders
                    else "Asset visual final sem proveniencia declarada."
                )
                add(
                    code,
                    severity,
                    symbol["res_symbol"],
                    message,
                    ", ".join(primitive_builders) or f"{symbol['res_file']}:{symbol['res_line']}",
                )
            continue

        source_kind = str(entry.get("source_kind", ""))
        acceptance = str(entry.get("acceptance_status", ""))

        if source_kind == "procedural_primitive" and acceptance == "final":
            symbol["provenance"] = "declared_procedural_primitive_final"
            add(
                "procedural_source_kind_declared_final",
                "blocking",
                symbol["res_symbol"],
                "source_kind=procedural_primitive nunca pode ter acceptance_status=final.",
                f"{symbol['res_file']}:{symbol['res_line']}",
            )
            continue

        if acceptance != "final":
            symbol["provenance"] = "declared_non_final"
            continue

        symbol["provenance"] = "declared_final_authored"

        if source_kind == "procedural_composed_from_authored" and not entry.get("authored_source"):
            add(
                "procedural_composed_without_authored_source",
                "blocking",
                symbol["res_symbol"],
                "Composicao procedural final sem authored_source persistida em data/source_art/.",
                f"{symbol['res_file']}:{symbol['res_line']}",
            )

        if primitive_builders and source_kind in {
            "hand_authored_pixel",
            "ai_generated",
            "photo_or_render_derived",
        }:
            add(
                "procedural_asset_promoted_to_res",
                "blocking",
                symbol["res_symbol"],
                f"Declarado {source_kind} mas o arquivo e escrito por builder de primitivas. "
                "Declare procedural_composed_from_authored com fonte autoral ou re-autore a arte.",
                ", ".join(primitive_builders),
            )

    for res_symbol in sorted(set(by_symbol) - {s["res_symbol"] for s in symbols}):
        add(
            "provenance_symbol_not_in_res",
            "warning",
            res_symbol,
            "Proveniencia declarada para simbolo que nao existe em nenhum .res.",
            "doc/asset_provenance_manifest.json",
        )

    undeclared_runtime = [h for h in runtime_hits if not h["debug_scoped"]]
    for hit in undeclared_runtime:
        add(
            "runtime_authored_tile_pixels_outside_debug",
            "blocking",
            hit["symbol"],
            "Pixels de tile escritos como literal em C fora de escopo de debug/telemetria. "
            "Grafico procedural e permitido apenas para debug visual ou elemento transitorio "
            "de interface.",
            f"{hit['file']}:{hit['line']} ({hit['hex_words']} hex words)",
        )

    blocking_statuses = sorted(
        {f["code"] for f in findings if f["severity"] == "blocking"}
    )

    for builder in builders:
        builder.pop("_text", None)
        builder["traced_symbols"] = sorted(set(builder["traced_symbols"]))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "project_root": project_root.as_posix(),
        "project_name": project_root.name,
        "validator_fixture": fixture_declared,
        "context_type": context_type,
        "manifest_status": manifest_status,
        "visual_symbols": symbols,
        "primitive_builders": builders,
        "runtime_authored_tiles": runtime_hits,
        "findings": findings,
        "summary": {
            "visual_symbols": len(symbols),
            "pixel_bearing_symbols": len(pixel_symbols),
            "declared_entries": len(entries),
            "primitive_builders": len(builders),
            "symbols_traced_to_primitive_builders": len(
                [s for s in symbols if s.get("primitive_builders")]
            ),
            "blocking_findings": len(
                [f for f in findings if f["severity"] == "blocking"]
            ),
            "warnings": len([f for f in findings if f["severity"] == "warning"]),
        },
        "blocking": bool(blocking_statuses),
        "blocking_statuses": blocking_statuses,
    }


def print_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    print(f"[asset-provenance] project: {report['project_name']}")
    print(
        "[asset-provenance] context_type={0} validator_fixture={1} manifest={2}".format(
            report["context_type"], report["validator_fixture"], report["manifest_status"]
        )
    )
    print(
        "[asset-provenance] visual_symbols={0} pixel_bearing={1} primitive_builders={2} "
        "traced={3}".format(
            summary["visual_symbols"],
            summary["pixel_bearing_symbols"],
            summary["primitive_builders"],
            summary["symbols_traced_to_primitive_builders"],
        )
    )
    for finding in report["findings"]:
        print(
            "[{0}] {1} :: {2} :: {3} :: {4}".format(
                finding["severity"].upper(),
                finding["code"],
                finding["subject"],
                finding["message"],
                finding["evidence"],
            )
        )
    verdict = "BLOCKED" if report["blocking"] else "OK"
    print(f"[asset-provenance] verdict={verdict} blocking={report['blocking_statuses']}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Audit procedural asset provenance against res/*.res."
    )
    parser.add_argument("--project-root", required=True)
    parser.add_argument(
        "--shared-builder-root",
        action="append",
        default=[],
        help="Extra builder tree to scan, e.g. tools/image-tools at workspace level.",
    )
    parser.add_argument("--output", default="")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.is_dir():
        print(f"[asset-provenance] ERROR: project root not found: {project_root}")
        return 2

    extra_roots = [Path(p).expanduser().resolve() for p in args.shared_builder_root]
    report = audit(project_root, [p for p in extra_roots if p.is_dir()])

    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else project_root / "out" / "logs" / "asset_provenance_audit_report.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    if not args.quiet:
        print_report(report)
        print(f"[asset-provenance] report: {output.as_posix()}")

    return 1 if report["blocking"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

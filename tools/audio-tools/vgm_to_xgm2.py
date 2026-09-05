#!/usr/bin/env python3
"""Convertedor VGM -> XGM2/XGC2 embutindo o `xgm2tool` oficial do SGDK.

A rota autoral de musica: compositor (Deflemask/Furnace/MML) -> VGM ->
`xgm2tool` -> `.xgm` (compressao XGM2) ou `.xgc` (packed, pronto ao Z80 driver).
O `.res` recebe `XGM2 name "file.vgm"` e o rescomp usa o mesmo conversor; este
script existe para converter explicitamente e auditar a saida (magic, versao,
blocos FM/PSG) antes de fechar o correto.

Localizacao do jar (por precedencia):
  1. env XGM2TOOL_JAR
  2. $SGDK_HOME/bin/xgm2tool.jar
  3. ./sdk/sgdk-2.11/bin/xgm2tool.jar
  4. out/host_tools/sgdk_wine_flatpak/sgdk-2.11/bin/xgm2tool.jar

Exemplo:
  python3 tools/audio-tools/vgm_to_xgm2.py --input track.vgm --out track.xgc --packed
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from audio_core import SCHEMA_VERSION, now_iso, sha256_file, vgm_info, xgm2_info

TOOL_NAME = "vgm_to_xgm2"
TOOL_VERSION = "1.0.0"

WORKSPACE = Path(__file__).resolve().parents[2]
CANDIDATE_JARS = [
    Path(os.environ["XGM2TOOL_JAR"]) if os.environ.get("XGM2TOOL_JAR") else None,
    Path(os.environ["SGDK_HOME"]) / "bin" / "xgm2tool.jar" if os.environ.get("SGDK_HOME") else None,
    WORKSPACE / "sdk" / "sgdk-2.11" / "bin" / "xgm2tool.jar",
    WORKSPACE / "out" / "host_tools" / "sgdk_wine_flatpak" / "sgdk-2.11" / "bin" / "xgm2tool.jar",
]


def find_tool() -> Path | None:
    for candidate in CANDIDATE_JARS:
        if candidate is not None and candidate.is_file():
            return candidate
    return None


def convert(vgm: Path, out: Path, packed: bool, timing: str,
            silent: bool) -> dict:
    tool = find_tool()
    if tool is None:
        raise FileNotFoundError(
            "xgm2tool.jar nao encontrado. Defina XGM2TOOL_JAR ou SGDK_HOME.")
    if not vgm.is_file():
        raise FileNotFoundError(f"entrada inexistente: {vgm}")
    if timing not in {"auto", "ntsc", "pal"}:
        raise ValueError(f"timing invalido: {timing}")
    source_info = vgm_info(vgm.read_bytes())
    suffix = ".xgc" if packed else ".xgm"
    target = out if out.suffix.lower() == suffix else out.with_suffix(suffix)
    target.parent.mkdir(parents=True, exist_ok=True)

    args = ["java", "-jar", str(tool), str(vgm), str(target)]
    if timing == "ntsc":
        args.append("-n")
    elif timing == "pal":
        args.append("-p")
    if silent:
        args.append("-s")
    result = subprocess.run(args, capture_output=True, text=True, timeout=120, check=False)
    if result.returncode != 0 or not target.is_file():
        raise RuntimeError(
            f"xgm2tool falhou (rc={result.returncode}): {result.stdout}{result.stderr}")

    data = target.read_bytes()
    if packed:
        # .xgc (compilado) remove o header XGM2; validamos tamanho e plausibilidade.
        info = {
            "magic": "(none/packed)",
            "note": "compilado XGM2: header XGM2 removido (xgm2.txt)",
            "size_bytes": len(data),
            "plausible": len(data) > 4,
        }
    else:
        info = xgm2_info(data)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "generated_at": now_iso(),
        "converter_jar": str(tool),
        "converter_jar_sha256": sha256_file(tool),
        "input": str(vgm),
        "input_sha256": sha256_file(vgm),
        "input_suffix": vgm.suffix.lower(),
        "input_vgm": source_info,
        "output": str(target),
        "output_sha256": sha256_file(target),
        "packed": packed,
        "timing": timing,
        "silent": silent,
        "xgm2": info,
    }


def _real_fixture_vgm() -> Path:
    """Retorna um VGM real para self-check, criado se necessario."""
    lab = WORKSPACE / "SGDK_projects" / (
        "Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]")
    fixture = lab / "res" / "audio" / "chase" / "chase_core_fm_psg.vgm"
    if fixture.is_file():
        return fixture
    # qualquer VGM dos templates do SGDK serve
    for pattern in ["out/host_tools/sgdk_wine_flatpak/sgdk-2.11/sample/**/*.vgm"]:
        found = list(WORKSPACE.glob(pattern))
        if found:
            return found[0]
    raise FileNotFoundError("nenhum VGM de teste encontrado para self-check")


def _positive_fixtures(tmpdir: Path) -> list[dict]:
    name = "vgm_to_xgm2_converts"
    fails = []
    try:
        vgm = _real_fixture_vgm()
        out = tmpdir / "converted.xgm"
        report = convert(vgm, out, packed=False, timing="ntsc", silent=True)
        if report["xgm2"]["magic"] != "XGM2":
            fails.append("saida sem magic XGM2")
        if not out.is_file() or out.stat().st_size == 0:
            fails.append("saida vazia")
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
    # entrada nao-VGM deve falhar
    bad_input = False
    bogus = tmpdir / "bogus.vgm"
    bogus.write_bytes(b"not a vgm at all")
    try:
        out = tmpdir / "bogus.xgm"
        convert(bogus, out, packed=False, timing="ntsc", silent=True)
    except (RuntimeError, FileNotFoundError, ValueError):
        bad_input = True
    fixtures.append({
        "fixture": "rejects_non_vgm_input",
        "kind": "negative",
        "passed": bad_input,
        "blocker": "audio_self_check_expected_blocker:rejects_non_vgm_input",
        "detail": [] if bad_input else ["xgm2tool aceitou um ficheiro nao-VGM"],
    })
    # sem jar deveria falhar com mensagem clara
    no_tool = False
    try:
        vgm = _real_fixture_vgm()
        # simula ausencia de jar temporariamente
        prev = list(CANDIDATE_JARS)
        try:
            CANDIDATE_JARS.clear()
            convert(vgm, tmpdir / "x.xgm", packed=False, timing="ntsc", silent=True)
        finally:
            CANDIDATE_JARS.extend(prev)
    except FileNotFoundError:
        no_tool = True
    fixtures.append({
        "fixture": "reports_missing_converter",
        "kind": "negative",
        "passed": no_tool,
        "blocker": "audio_self_check_expected_blocker:reports_missing_converter",
        "detail": [] if no_tool else ["nao reportou jar ausente"],
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
        "rule_ref": "Launcher.java (xgm2tool) + xgm2.txt",
        "exercised": "conversao real VGM->XGM2; rejeicao de nao-VGM; reporte de jar ausente.",
        "limitation": "Prova conversao/formato. Nao prova lei, qualidade nem loop.",
        "fixtures_total": len(fixtures),
        "fixtures_passed": len(fixtures) - len(failed),
        "fixtures": fixtures,
        "blocking": bool(failed),
        "blocking_statuses": sorted({f["blocker"] for f in failed if not f["passed"]}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=TOOL_NAME + " (VGM -> XGM2/XGC2).")
    parser.add_argument("--input", dest="vgm", metavar="VGM",
                        help="VGM de entrada.")
    parser.add_argument("--out", dest="out", metavar="XGM|XGC",
                        help="arquivo de saida.")
    parser.add_argument("--packed", action="store_true",
                        help="gera .xgc (compilado/packed) em vez de .xgm.")
    timing = parser.add_mutually_exclusive_group()
    timing.add_argument("--ntsc", action="store_true", help="forca timing NTSC")
    timing.add_argument("--pal", action="store_true", help="forca timing PAL")
    parser.add_argument("--silent", action="store_true",
                        help="modo silencioso do conversor.")
    parser.add_argument("--self-check", action="store_true",
                        help="Roda fixtures positivas e negativas e emite report JSON.")
    args = parser.parse_args(argv)

    if args.self_check:
        report = self_check()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1 if report["blocking"] else 0

    if not args.vgm or not args.out:
        parser.print_help()
        return 2
    try:
        selected_timing = "ntsc" if args.ntsc else ("pal" if args.pal else "auto")
        report = convert(Path(args.vgm), Path(args.out), args.packed,
                         selected_timing, args.silent)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

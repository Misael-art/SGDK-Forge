#!/usr/bin/env python3
"""Reproduz o handoff P11 em uma cópia mínima e descartável.

O projeto completo contém evidências e artefatos grandes demais para uma cópia
ingênua. Este runner copia somente os manuais e o contrato de StageDefinition,
injeta um stub mínimo de SGDK para compilação host e executa um probe de dados.
Ele não substitui o build SGDK nem uma ROM no emulador.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_TOKENS = {
    "doc/engine_quickstart.md": ("build_sgdk_wine_bridge.sh", "pending_visual_review"),
    "doc/engine_extension_guide.md": ("StageDefinition", "PLAYER_SET_SPRITE", "CombatEvent"),
    "doc/controls_and_options.md": ("SFX", "MUSIC", "STG2", "DEFAULTS"),
    # O inventário ativo acompanha o SHA da ROM vigente; manter um prefixo
    # histórico aqui faria a reprodução falhar mesmo com documentação correta.
    "doc/engine/release_inventory.json": ("2ba2aaf8", "required_runtime_sources", "pending_visual_review"),
}
DOCS = list(DOC_TOKENS)


def utc_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run() -> tuple[int, Path, dict]:
    out = ROOT / "out" / f"p11_isolated_reproduction_{utc_id()}"
    include = out / "include"
    inc = out / "inc"
    res = out / "res"
    src = out / "src"
    for rel in DOCS:
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)
    for rel, target_root in (("inc/stage.h", inc), ("res/gfx.h", res), ("src/stage.c", src)):
        target = target_root / Path(rel).name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)

    # Só o que StageDefinition usa; nenhuma API é inventada no runtime.
    write(include / "genesis.h", """\n#ifndef GENESIS_H\n#define GENESIS_H\n#include <stdint.h>\ntypedef uint8_t u8;\ntypedef uint16_t u16;\ntypedef int bool;\n#define TRUE 1\n#define FALSE 0\n#define BG_B 1\n#define PAL0 0\ntypedef struct Image { uint16_t w, h; } Image;\n#endif\n""")
    write(out / "gfx_stub.c", """\n#include \"genesis.h\"\nconst Image room_0_bga = {0, 0};\nconst Image room_0_bgb = {0, 0};\nconst Image gfx_bgb1 = {512, 256};\nconst Image gfx_bgb2 = {512, 256};\nconst Image gfx_showdown = {512, 256};\n""")
    write(out / "stage_probe.c", """\n#include <stdio.h>\n#include <string.h>\n#include \"stage.h\"\nint main(void) {\n    const StageDefinition *a = STAGE_getDefinition(1);\n    const StageDefinition *b = STAGE_getDefinition(2);\n    if (!a || !b || a->id != 1 || b->id != 2 || a->width != 512 || b->height != 256) return 2;\n    if (strcmp(a->name, \"SHOWDOWN\") != 0 || strcmp(b->name, \"BGB2\") != 0) return 3;\n    if (!STAGE_getImage(1) || !STAGE_getImage(2)) return 4;\n    puts(\"stage_definition_ok\");\n    return 0;\n}\n""")

    binary = out / "stage_probe"
    compile_cmd = [
        "gcc", "-std=c11", "-Wall", "-Wextra", "-Werror",
        "-I", str(include), "-I", str(inc), "-I", str(res),
        str(src / "stage.c"), str(out / "gfx_stub.c"), str(out / "stage_probe.c"),
        "-o", str(binary),
    ]
    compiled = subprocess.run(compile_cmd, capture_output=True, text=True)
    probe = None
    if compiled.returncode == 0:
        probe = subprocess.run([str(binary)], capture_output=True, text=True)

    doc_checks = {}
    for rel in DOCS:
        text = (out / rel).read_text(encoding="utf-8", errors="replace")
        doc_checks[rel] = {
            "exists": True,
            "tokens": {token: (token in text) for token in DOC_TOKENS[rel]},
        }
    docs_ok = all(all(v["tokens"].values()) for v in doc_checks.values())
    inventory = json.loads((out / "doc/engine/release_inventory.json").read_text(encoding="utf-8"))
    inventory_paths = inventory["required_runtime_sources"] + inventory["required_documentation"]
    inventory_missing = [rel for rel in inventory_paths if not (ROOT / rel).exists()]
    inventory_ok = inventory["status"] == "candidate_not_release" and not inventory_missing
    status = compiled.returncode == 0 and probe is not None and probe.returncode == 0 and docs_ok and inventory_ok
    report = {
        "schema_version": "1.0.0",
        "status": "pass" if status else "fail",
        "scope": "p11_isolated_manual_and_stage_extension",
        "copy_root": str(out),
        "docs": doc_checks,
        "compile": {"command": compile_cmd, "returncode": compiled.returncode, "stderr": compiled.stderr[-2000:]},
        "probe": None if probe is None else {"returncode": probe.returncode, "stdout": probe.stdout.strip(), "stderr": probe.stderr[-1000:]},
        "inventory": {"status": inventory.get("status"), "missing": inventory_missing, "ok": inventory_ok},
        "claim_limit": "host compilation/probe only; SGDK build, emulator, visual and audio remain separate gates",
    }
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return (0 if status else 1), out, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-check", action="store_true", help="executa a reprodução isolada")
    parser.parse_args()
    code, out, report = run()
    print(json.dumps({"session": str(out), "status": report["status"]}, ensure_ascii=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())

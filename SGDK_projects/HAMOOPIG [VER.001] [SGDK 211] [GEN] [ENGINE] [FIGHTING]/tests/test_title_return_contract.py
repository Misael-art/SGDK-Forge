#!/usr/bin/env python3
"""Contrato da rota SELECT/AFTER_MATCH -> TITLE usada por INTRO/FADE."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures = []
    select = (ROOT / "src" / "select.c").read_text(encoding="utf-8", errors="replace")
    main_c = (ROOT / "src" / "main.c").read_text(encoding="utf-8", errors="replace")
    title = (ROOT / "src" / "title.c").read_text(encoding="utf-8", errors="replace")
    if "select_return_to_title" not in select:
        failures.append("SELECT sem owner de retorno ao título")
    if "SCENE_request(gConfig.showOpening ? SCENE_OPENING : SCENE_TITLE)" not in select:
        failures.append("SELECT não respeita INTRO OFF/ON")
    if "SCENE_request(gConfig.showOpening ? SCENE_OPENING : SCENE_TITLE)" not in main_c:
        failures.append("AFTER_MATCH não respeita INTRO OFF/ON")
    for token in ('TITLE_OPTION_OPENING', 'TITLE_OPTION_FADE', '"INTRO ON"', '"FADE OFF"'):
        if token not in title:
            failures.append(f"menu sem {token}")
    evidence = sorted((ROOT / "out" / "emulator_evidence").glob("title_return_*/manifest.json"))
    if evidence:
        manifest = json.loads(evidence[-1].read_text(encoding="utf-8"))
        if manifest.get("scope") != "real_keyboard_title_intro_fade_return":
            failures.append("manifesto de retorno tem escopo incorreto")
        if len(manifest.get("captures", [])) < 5:
            failures.append("manifesto de retorno não contém as cinco capturas")
    if failures:
        print("FAIL:")
        for item in failures:
            print("  -", item)
        return 1
    print("PASS: INTRO/FADE possuem toggles, retorno real e evidência de emulador")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

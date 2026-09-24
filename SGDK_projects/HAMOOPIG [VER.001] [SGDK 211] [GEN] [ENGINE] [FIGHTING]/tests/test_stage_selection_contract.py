#!/usr/bin/env python3
"""Contrato estático da seleção de dois cenários."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    select = (ROOT / "src/select.c").read_text(encoding="utf-8")
    init = (ROOT / "src/init.c").read_text(encoding="utf-8")
    stage = (ROOT / "src/stage.c").read_text(encoding="utf-8")
    title = (ROOT / "src/title.c").read_text(encoding="utf-8")
    harness = (ROOT / "tests/capture_visual_ko.py").read_text(encoding="utf-8")
    config = (ROOT / "inc/config.h").read_text(encoding="utf-8")
    assert "gBG_Choice = (gBG_Choice == 1) ? 2 : 1" in select
    assert "gConfig.stage2Enabled" in select and "P[1].key_JOY_C_status" in select
    assert "STAGE_getDefinition(gBG_Choice)" in init and "STAGE_getImage(gBG_Choice)" in init
    assert "gfx_showdown" in stage and "gfx_bgb2" in stage
    assert "TITLE_OPTION_STAGE2" in title and "stage2Enabled" in config
    assert "--stage2" in harness and "00_stage2_selected" in harness
    assert "time.sleep(1.5)" in harness
    assert "Do not confirm A/X in a selection-only capture" in harness
    assert "scope': 'real_keyboard_playtest_selection_only'" in harness
    assert "--selection-confirmation" in harness
    assert "01_p1_confirmed" in harness and "02_desconfirmed_title" in harness
    assert "--confirm-both" in harness and "02_both_confirmed" in harness
    assert "'stage': 'SHOWDOWN' if '--showdown' in sys.argv else 'BGB2'" in harness
    assert "real_keyboard_playtest_probe_short" in harness and "manifest.json" in harness
    assert "--h240" in harness and "h240_requested" in harness
    assert "fighter_arg('--p1'" in harness and "fighter_arg('--p2fighter'" in harness
    assert "tests/blastem_qa.cfg" in harness
    print("PASS: stage2 selecionável por P1, ramo gfx_showdown/gfx_bgb2 e toggle")


if __name__ == "__main__":
    main()

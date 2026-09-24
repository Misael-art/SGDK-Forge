#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    header = (ROOT / "inc/stage.h").read_text()
    source = (ROOT / "src/stage.c").read_text()
    init = (ROOT / "src/init.c").read_text()
    select = (ROOT / "src/select.c").read_text()
    physics = (ROOT / "src/physics.c").read_text()
    for token in ("StageDefinition", "STAGE_getDefinition", "STAGE_getImage", "supports240"):
        assert token in header
    for token in ("kShowdown", "kStage2", ".width = 512", ".height = 256", "&gfx_showdown", "&gfx_bgb2"):
        assert token in source
    for token in ("STAGE_LOAD_RESIDENT", "tileBudget", "measuredUniqueTiles", "StageCameraContract", "provenance"):
        assert token in header or token in source
    assert "STAGE_getDefinition(gBG_Choice)" in init
    assert "STAGE_getImage(gBG_Choice)" in init
    assert "STAGE_getDefinition(gBG_Choice)->name" in select
    assert "gLimiteCenarioE" in physics and "gLimiteCenarioD" in physics
    assert "gBG_Width-30" not in physics
    print("PASS: StageDefinition centraliza dimensoes, limites, recurso e nome dos dois palcos")


if __name__ == "__main__":
    main()

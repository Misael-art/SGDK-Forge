#!/usr/bin/env python3
"""Static contract for grounded KO presentation.

The airborne knock-back state (550) may move horizontally, but the settle
state (551) must not keep translating the fighter.  Otherwise a loser can
leave the viewport before the terminal defeat pose (570) is shown.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    physics = (ROOT / "src/physics.c").read_text()
    table = (ROOT / "inc/player_musgo_table.h").read_text()
    graphics = (ROOT / "src/graphics.c").read_text()

    settle = physics.split("if(P[i].state==551){", 1)[1].split("//'551' >", 1)[0]
    assert "P[i].x-=2" not in settle and "P[i].x+=2" not in settle
    landing = physics.split("if(P[i].state==551 && P[i].y>gAlturaPiso)", 1)[1].split("//-----------------------------------------------------------------------------------------", 1)[0]
    assert "gLimiteCenarioE" in landing and "gLimiteCenarioD" in landing
    assert "case 570:" in table and "&spr_musgo_fall_v1" in table
    assert "defeat_v1 asset" in table
    assert "P[i].animFrame = P[i].animFrameTotal" in graphics
    musgo = (ROOT / "src/player_musgo.c").read_text()
    assert "State==550 || State==551 || State==570" in musgo
    assert "SPR_releaseSprite(P[Player].sprite)" in musgo
    main = (ROOT / "src/main.c").read_text()
    assert "koNeedsLanding" in main
    assert "P[1].state==550 || P[1].state==551" in main
    assert "P[2].state==550 || P[2].state==551" in main
    print("PASS: KO congela deslocamento no settle, limita posição e mantém pose terminal do Musgo")


if __name__ == "__main__":
    main()

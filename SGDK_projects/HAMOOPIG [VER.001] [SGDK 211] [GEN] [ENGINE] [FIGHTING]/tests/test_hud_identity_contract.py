#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    text = (ROOT / "src/hud.c").read_text(encoding="utf-8")
    required = (
        "hud_identity_update",
        "hud_fighter_name",
        "hud_draw_text(hud_fighter_name(P[1].id), 0, 4)",
        "hud_draw_text(hud_fighter_name(P[2].id), 34, 4)",
        "P[1].wins >= 1",
        "P[2].wins >= 1",
        "P[1].wins >= 2",
        "P[2].wins >= 2",
        "HUD_SPECIAL_ROW     27",
        "HUD_COMBO_ROW       13",
    )
    missing = [token for token in required if token not in text]
    assert not missing, "tokens ausentes: " + ", ".join(missing)
    assert text.count("hud_identity_update();") >= 2
    print("PASS: nomes e estrelas usam margens do HUD sem sprites adicionais")

if __name__ == "__main__":
    main()

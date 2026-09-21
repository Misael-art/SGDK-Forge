#!/usr/bin/env python3
"""Contrato estático do primeiro corte da barra de especial (P05).

Este teste prova a faixa, a ausência de sprites extras e a escrita no plano;
captura no emulador ainda é necessária para validar legibilidade e posição.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    hud = (ROOT / "src/hud.c").read_text(encoding="utf-8")
    player = (ROOT / "src/player.c").read_text(encoding="utf-8")
    fsm = (ROOT / "src/fsm.c").read_text(encoding="utf-8")
    config = (ROOT / "src/config.c").read_text(encoding="utf-8")
    assert "HUD_SPECIAL_ROW     27" in hud
    assert "hud_special_count" in hud
    assert "sHudSpecialEnabled" in hud
    assert "energy > 32 ? 32" in hud
    assert "(e * HUD_BAR_SEGMENTS + 31) / 32" in hud
    assert "VDP_setTileMapXY(HUD_PLANE" in hud
    assert "energiaSP" in player and "SPECIAL_METER_MAX" in player
    assert "FUNCAO_SPEND_SPECIAL" in player and "SPECIAL_METER_COST" in player
    assert "specialRules" in player and "hudSpecialBar" in hud and "hudHitCount" in hud
    assert "specialRules" in config
    assert "fsm_try_start_special" in fsm
    assert "fsm_try_start_special(player,730)" in fsm
    assert "fsm_try_start_special(player,700)" in fsm
    assert "FUNCAO_REGISTER_HIT" in fsm
    assert "FUNCAO_UPDATE_HIT_COMBOS" in (ROOT / "src/player.c").read_text()
    assert "HIT_COMBO_WINDOW_TICKS" in (ROOT / "inc/game_types.h").read_text()
    assert "HUD_COMBO_ROW       13" in hud
    assert "hud_combo_update" in hud
    assert "hud_draw_life_bar" in hud
    assert "spr_hud_energy_y" in hud
    assert "spr_hud_energy_y_p2" in hud
    # A barra de especial não pode reintroduzir o atlas legado de 16x2 sprites.
    assert "GE[6+i]" not in hud
    print("PASS: especial clamp 0..32, oito células BG_A, sem sprites extras")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Static guard for the NTSC DMA back-pressure policy."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_fighter_sprites_do_not_force_unbounded_frame_uploads():
    for name in ("player.c", "player_ken.c", "player_musgo.c"):
        text = (ROOT / "src" / name).read_text()
        assert "HAMOOPIG_DMA_LAB_DELAYED_FRAME" in text
        assert "#define HAMOOPIG_DMA_LAB_DELAYED_FRAME 1" in text
        assert "#define SPR_FLAG_DISABLE_DELAYED_FRAME_UPDATE 0" in text


def test_transient_hud_maps_stay_out_of_dma_queue():
    text = (ROOT / "src" / "hud.c").read_text()
    assert text.count("HUD_COMBO_ROW, 40, HUD_COMBO_ROWS, 40, CPU") == 2
    assert text.count("HUD_MESSAGE_ROW, 40, HUD_MESSAGE_ROWS, 40, CPU") == 2
    assert "HUD_COMBO_ROW, 40, 2, 40, DMA_QUEUE_COPY" not in text
    assert "HUD_MESSAGE_ROW, 40, HUD_MESSAGE_ROWS, 40, DMA_QUEUE_COPY" not in text


def test_hud_plane_owned_life_bar_invalidates_special_strip():
    text = (ROOT / "src" / "hud.c").read_text()
    assert "hud_sync_segment_tile" in text
    assert "sHudLifeBarP1" in text and "sHudLifeBarP2" in text
    assert "hud_draw_life_bar(0, P[1].energiaBase)" in text
    assert "hud_draw_life_bar(1, P[2].energiaBase)" in text
    assert "sHudSpecialCount[0] = -1" in text
    assert "sHudSpecialCount[1] = -1" in text


def test_fighter_keeps_stable_sprite_handle_and_round_reset_releases_hud():
    player = (ROOT / "src" / "player.c").read_text()
    init = (ROOT / "src" / "init.c").read_text()
    assert "HAMOOPIG_STABLE_PLAYER_SPRITE" in player
    assert "SPR_setDefinition(sprite, definition)" in player
    assert "PLAYER_SET_SPRITE(Player" in player
    assert "#if !HAMOOPIG_STABLE_PLAYER_SPRITE" in player
    assert "hud_window_off();" in init
    assert init.index("hud_window_off();") < init.index("hud_window_init();")
    assert init.count("SPR_releaseSprite(Rect1BB1_Q1)") == 1
    assert init.count("SPR_releaseSprite(Rect2HB1_Q4)") == 1


def test_visual_ko_harness_separates_life_and_special_rows():
    text = (ROOT / "tests" / "capture_visual_ko.py").read_text()
    assert "life row" in text
    assert text.count("int(32*scale)") >= 2
    assert "int(40*scale)" not in text


if __name__ == "__main__":
    test_fighter_sprites_do_not_force_unbounded_frame_uploads()
    test_transient_hud_maps_stay_out_of_dma_queue()
    test_hud_plane_owned_life_bar_invalidates_special_strip()
    test_fighter_keeps_stable_sprite_handle_and_round_reset_releases_hud()
    test_visual_ko_harness_separates_life_and_special_rows()
    print("PASS: fighter DMA back-pressure and transient HUD CPU writes")

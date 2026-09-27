"""Guard the HUD's one-VBlank deferral after queued BG_A stage-map restores."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / 'SGDK_projects/Mugenesis_Demo [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]'


def test_stage_restore_defers_hud_redraw_until_the_next_frame():
    hud = (PROJECT / 'src/scenes/fight_hud.c').read_text(encoding='utf-8')
    scene = (PROJECT / 'src/scenes/scene_demo.c').read_text(encoding='utf-8')
    update = hud.split('void FIGHT_HUD_update(void)', 1)[1].split('void FIGHT_HUD_invalidateBGA', 1)[0]
    restore_guard = update.index('if (sBgaRedrawDelay)')
    redraw = update.index('if (sHidden) { sHidden = 0; drawStatic(); }')
    assert restore_guard < redraw
    assert 'if (FIGHT_STAGE_takeHudInvalidation()) FIGHT_HUD_deferBGARebuild();' in scene
    assert 'if (FIGHT_STAGE_takeHudInvalidation()) FIGHT_HUD_invalidateBGA();' in scene
    assert 'sBgaRedrawDelay = 1;' in hud

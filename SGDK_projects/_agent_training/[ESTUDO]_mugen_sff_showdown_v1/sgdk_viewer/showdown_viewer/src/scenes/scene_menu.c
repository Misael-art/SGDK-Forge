#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/audio.h"
#include "system/input.h"

static void SCENE_menuDraw(void)
{
    VDP_clearPlane(BG_A, TRUE);

    VDP_drawTextFill("MUGEN SFF SHOWDOWN", 10, 4, 20);
    VDP_drawTextFill("Fixture: showdown.sff + showdown.def", 2, 8, 38);
    VDP_drawTextFill("Pipeline local: extract/rebuild/tilemap", 2, 10, 38);
    VDP_drawTextFill("Status: controlled training area", 2, 12, 38);
    VDP_drawTextFill("ready_for_aaa=false", 2, 14, 38);
    VDP_drawTextFill("A ou START: abrir viewer", 7, 19, 32);
    VDP_drawTextFill("B: tela de contexto", 10, 21, 30);
    VDP_drawTextFill("C: alternar HUD", 12, HUD_ROW_HINT_PRIMARY, 28);
}

void SCENE_menuEnter(void)
{
    /*
     * Canonical scene-enter pattern:
     *   1) SPR_reset + SPR_update => safety net in case we were re-entered via
     *      a code path that bypasses APP_changeScene.
     *   2) PAL3 = palette_grey with VDP_setTextPalette(PAL3) guarantees high-
     *      contrast overlay text regardless of the currently loaded BG palettes.
     */
    SPR_reset();
    SPR_update();

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x102410));
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);

    SCENE_menuDraw();
}

void SCENE_menuUpdate(void)
{
    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        APP_changeScene(APP_SCENE_DEMO);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        APP_changeScene(APP_SCENE_BOOT);
    }
}

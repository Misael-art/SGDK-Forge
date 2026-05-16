#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

static void SCENE_menuDraw(void)
{
    VDP_clearPlane(BG_A, TRUE);

    VDP_drawTextFill("NOVO ARARA GI FIGHTER V2", 7, 4, 26);
    VDP_drawTextFill("LAPA OPEN MAT - NOITE", 9, 8, 22);
    VDP_drawTextFill("CAIO ARARA  VS  DAVI ARARA", 6, 11, 28);
    VDP_drawTextFill("A ou START: LUTAR", 11, 18, 18);
    VDP_drawTextFill("B: VOLTAR AO BOOT", 11, 20, 18);
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
        APP_changeScene(APP_SCENE_DEMO);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_BOOT);
    }
}
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

void SCENE_bootEnter(void)
{
    gApp.showDebugHud = TRUE;
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x121224));
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    VDP_drawText("BLUE CIRCUIT", 14, 5);
    VDP_drawText("vertical slice SGDK 2.11", 8, 8);
    VDP_drawText("A ou START: title", 10, 12);
    VDP_drawText("C: ligar/desligar HUD", 8, 14);
    VDP_drawText("build exige BlastEm para fechar", 5, 18);
}

void SCENE_bootUpdate(void)
{
    if (gApp.sceneFrames > 180 || INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_MENU);
    }
}

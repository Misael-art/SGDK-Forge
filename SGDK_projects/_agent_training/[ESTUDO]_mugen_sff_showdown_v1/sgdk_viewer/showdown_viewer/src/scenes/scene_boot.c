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

    VDP_drawText("MUGEN SFF SHOWDOWN VIEWER", 6, 5);
    VDP_drawText("Fixture de treino SFF v1.01 -> SGDK", 2, 8);
    VDP_drawText("A ou START: ver stage", 8, 12);
    VDP_drawText("C: ligar/desligar HUD", 8, 14);
    VDP_drawText("Status: lab_not_delivery", 8, 18);
}

void SCENE_bootUpdate(void)
{
    if (gApp.sceneFrames > 180 || INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_DEMO);
    }
}

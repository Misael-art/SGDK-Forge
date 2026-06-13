#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

void SCENE_brandingEnter(void)
{
    gApp.showDebugHud = TRUE;
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101018));
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_drawText("MUGEN SFF SHOWDOWN", 10, 8);
    VDP_drawText("Template branding disabled", 8, 12);
    VDP_drawText("A ou START: viewer", 10, 16);
}

void SCENE_brandingUpdate(void)
{
    if (gApp.sceneFrames > 90 || INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_DEMO);
    }
}

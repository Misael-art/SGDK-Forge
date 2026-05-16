#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

void SCENE_bootEnter(void)
{
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x121224));
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    VDP_drawText("NOVO ARARA GI FIGHTER V2", 7, 5);
    VDP_drawText("Campeonato noturno de BJJ", 6, 8);
    VDP_drawText("Lapa Open Mat - Rio", 9, 11);
    VDP_drawText("A ou START: luta", 11, 16);
}

void SCENE_bootUpdate(void)
{
    if (gApp.sceneFrames > 60 || INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_DEMO);
    }
}
#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

void SCENE_bootEnter(void)
{
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x121224));
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    VDP_drawText("MODELO CANONICO SGDK", 7, 5);
    VDP_drawText("Base pedagogica do sgdk_wrapper", 4, 8);
    VDP_drawText("A ou START: entrar no menu", 6, 12);
    VDP_drawText("C: ligar/desligar HUD", 8, 14);
    VDP_drawText("Este projeto compila sem assets finais.", 2, 18);
}

void SCENE_bootUpdate(void)
{
    if (gApp.sceneFrames > 180 || INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_MENU);
    }
}

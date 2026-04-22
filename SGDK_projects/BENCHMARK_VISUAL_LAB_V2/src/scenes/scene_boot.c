#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

void SCENE_bootEnter(void)
{
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x121224));
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    VDP_drawTextFill("BENCHMARK VISUAL LAB V2", 8, 5, 24);
    VDP_drawTextFill("Framework vivo para benchmark visual em ROM.", 1, 8, 39);
    VDP_drawTextFill("Slice 1: menu + 3 cenas navegaveis.", 2, 10, 38);
    VDP_drawTextFill("A ou START: entrar no menu", 6, 14, 28);
    VDP_drawTextFill("Warmup READY via SRAM ocorre apos boot estavel.", 1, 18, 39);
    VDP_drawTextFill("C: HUD global   B: sem acao no boot", 3, 21, 34);
}

void SCENE_bootUpdate(void)
{
    if (gApp.sceneFrames > 120 || INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_MENU);
    }
}

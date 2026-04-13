#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/input.h"

static void SCENE_menuDraw(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);

    VDP_drawText("GAIRA FIGHTER LAB", 11, 3);
    VDP_drawText("Sprint 1 Runtime Proof", 9, 5);

    VDP_drawText("A: S1.1 SPRITE ANIMATION", 8, 10);
    VDP_drawText("B: S1.2 CHARACTER DESIGN", 8, 12);
    VDP_drawText("START: S1.3 MULTIPLANE", 9, 14);

    VDP_drawText("C: toggle debug HUD", 10, 20);
}

void SCENE_menuEnter(void)
{
    SPR_reset();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);

    PAL_setPalette(PAL0, palette_grey, DMA);
    VDP_setTextPalette(PAL0);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x102410));

    SCENE_menuDraw();
}

void SCENE_menuUpdate(void)
{
    if (INPUT_pressed(BUTTON_A)) {
        APP_changeScene(APP_SCENE_SPRITE_ANIM);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        APP_changeScene(APP_SCENE_CHAR_DESIGN);
        return;
    }

    if (INPUT_pressed(BUTTON_START)) {
        APP_changeScene(APP_SCENE_MULTIPLANE);
    }
}

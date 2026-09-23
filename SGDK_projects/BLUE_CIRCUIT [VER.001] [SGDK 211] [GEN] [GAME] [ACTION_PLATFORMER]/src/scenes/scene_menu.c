#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "resources.h"
#include "system/audio.h"
#include "system/input.h"

#define MENU_TILE_LOGO TILE_USER_INDEX

static void SCENE_menuDraw(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);

    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x000012));
    PAL_setPalette(PAL1, img_bc_title_logo.palette->data, CPU);
    PAL_setPalette(PAL3, palette_grey, CPU);
    VDP_setTextPalette(PAL3);

    VDP_drawImageEx(
        BG_A,
        &img_bc_title_logo,
        TILE_ATTR_FULL(PAL1, TRUE, FALSE, FALSE, MENU_TILE_LOGO),
        12,
        4,
        FALSE,
        FALSE
    );

    VDP_drawTextFill("BLUE_CIRCUIT", 14, 12, 14);
    VDP_drawTextFill("RESCUE MAINTENANCE ACTION", 7, 15, 28);
    VDP_drawTextFill("PRESS START", 14, 19, 14);
    VDP_drawTextFill("A: START   C: DEBUG HUD", 8, HUD_ROW_HINT_PRIMARY, 26);
}

void SCENE_menuEnter(void)
{
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
    gApp.paused = FALSE;
    SCENE_menuDraw();
}

void SCENE_menuUpdate(void)
{
    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        APP_changeScene(APP_SCENE_DEMO);
    }
}

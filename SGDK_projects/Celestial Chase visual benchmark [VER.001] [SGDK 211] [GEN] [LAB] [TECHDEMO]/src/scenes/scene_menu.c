#include <genesis.h>

#include "core/app.h"
#include "system/audio.h"
#include "system/input.h"

static void SCENE_menuDraw(void)
{
    VDP_clearTileMapRect(BG_A, 0, 0, 64, 32);
    VDP_clearTileMapRect(BG_B, 0, 0, 64, 32);

    VDP_drawText("CELESTIAL CHASE", 12, 5);
    VDP_drawText("FIRST PLAYABLE MISSION", 8, 8);
    VDP_drawText("SELECT MODE", 14, 12);

    VDP_drawText((gApp.chaseMode == CHASE_MODE_RUN) ? "> RUN (TIMED)" : "  RUN (TIMED)", 13, 14);
    VDP_drawText((gApp.chaseMode == CHASE_MODE_ENDLESS) ? "> ENDLESS" : "  ENDLESS", 13, 16);

    VDP_drawText("UP/DOWN: SELECT", 11, 20);
    VDP_drawText("A/START: BEGIN", 11, 22);
    VDP_drawText("B: BACK", 16, 24);
}

void SCENE_menuEnter(void)
{
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
    AUDIO_setMusicState(AUDIO_MUSIC_MENU);
    SCENE_cleanupLineScroll(BG_A);
    SCENE_cleanupLineScroll(BG_B);
    VDP_setWindowOff();
    VDP_setTextPlane(BG_A);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x080418));
    PAL_setPalette(PAL3, palette_grey, CPU);
    VDP_setTextPalette(PAL3);

    SCENE_menuDraw();
}

void SCENE_menuUpdate(void)
{
    if (INPUT_pressed(BUTTON_UP) || INPUT_pressed(BUTTON_DOWN)) {
        gApp.chaseMode = (gApp.chaseMode == CHASE_MODE_RUN) ? CHASE_MODE_ENDLESS : CHASE_MODE_RUN;
        AUDIO_playCue(AUDIO_CUE_MENU);
        SCENE_menuDraw();
        return;
    }

    if (INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        APP_changeScene(APP_SCENE_CHASE);
        return;
    }

    if (INPUT_pressed(BUTTON_B)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        APP_changeScene(APP_SCENE_BOOT);
    }
}

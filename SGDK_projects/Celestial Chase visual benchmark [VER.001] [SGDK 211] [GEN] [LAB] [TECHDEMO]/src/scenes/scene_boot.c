#include <genesis.h>

#include "core/app.h"
#include "game_vars.h"
#include "system/audio.h"
#include "system/input.h"

void SCENE_bootEnter(void)
{
    SPR_reset();
    SPR_update();
    AUDIO_stopAll();
    AUDIO_setMusicState(AUDIO_MUSIC_INTRO);
    SCENE_cleanupLineScroll(BG_A);
    SCENE_cleanupLineScroll(BG_B);
    VDP_setWindowOff();
    VDP_setTextPlane(BG_A);
    PAL_setPalette(PAL3, palette_grey, CPU);
    VDP_setTextPalette(PAL3);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x080418));
    VDP_clearTileMapRect(BG_A, 0, 0, 64, 32);
    VDP_clearTileMapRect(BG_B, 0, 0, 64, 32);

    VDP_drawText("CELESTIAL CHASE", 12, 8);
    VDP_drawText("A MYTHIC PURSUIT", 11, 11);
    VDP_drawText("PRESS A OR START", 11, 18);
}

void SCENE_bootUpdate(void)
{
    if (gApp.sceneFrames > 240 || INPUT_pressed(BUTTON_A) || INPUT_pressed(BUTTON_START)) {
        AUDIO_playCue(AUDIO_CUE_MENU);
        AUDIO_setMusicState(AUDIO_MUSIC_MENU);
        APP_changeScene(APP_SCENE_MENU);
    }
}

#include <genesis.h>

#include "core/app.h"
#include "system/audio.h"

void SCENE_brandingEnter(void)
{
    AUDIO_stopAll();
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x000012));
}

void SCENE_brandingUpdate(void)
{
    APP_changeScene(APP_SCENE_MENU);
}

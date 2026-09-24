#include <genesis.h>

#include "core/app.h"
#include "scenes/scene_branding.h"

/* Neutral fallback only. The reference ROM boots directly into DEMO. */
void SCENE_brandingEnter(void)
{
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    PAL_setPalette(PAL3, palette_grey, DMA);
    VDP_setTextPalette(PAL3);
    PAL_setColor(0, RGB24_TO_VDPCOLOR(0x101828));
    VDP_drawText("FORGE REFERENCE", 12, 12);
    VDP_drawText("NEUTRAL FIXTURE", 12, 14);
}

void SCENE_brandingUpdate(void)
{
    if (gApp.sceneFrames >= 60u) {
        APP_changeScene(APP_SCENE_DEMO);
    }
}

/**
 * camera.c — Dead-zone tracking camera + dual-layer parallax
 *
 * BGA (foreground map): scrolls at 1:1 with camera.
 * BGB (background map): scrolls at 1/8 horizontal, 1/32 vertical.
 * Sine-wave line scroll applied to BGB in VBlank for raster shimmer effect.
 *
 * Dead zone: camera only scrolls when player exits a central rectangle.
 * This is a classic Mega Drive technique (used in Sonic, Shinobi III).
 */

#include <genesis.h>

#include "camera.h"
#include "effects.h"
#include "game_config.h"

/* =========================================================================
 * State
 * ========================================================================= */
s16 camX = 0;
s16 camY = 0;

/* Sine wave scroll buffer (BGB line scroll) */
static s16 bgbLineScroll[224];
static u16 sinePhase = 0;

/* =========================================================================
 * Init
 * ========================================================================= */
void CAMERA_init(void) {
    camX = 0;
    camY = 0;
    sinePhase = 0;

    /* Set BGB to line-scroll mode so we can write per-line offsets in VBlank */
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);

    /* Pre-fill sine buffer to zero */
    for (u16 i = 0; i < 224; i++) bgbLineScroll[i] = 0;
}

/* =========================================================================
 * Center camera on world position (dead-zone follow)
 * ========================================================================= */
void CAMERA_centerOn(s16 worldX, s16 worldY) {
    s16 screenX = worldX - camX;
    s16 screenY = worldY - camY;

    s16 newCamX = camX;
    s16 newCamY = camY;

    /* Horizontal dead zone: follow when outside [40..240] */
    if (screenX > CAM_LEAD_X_RIGHT) newCamX = worldX - CAM_LEAD_X_RIGHT;
    else if (screenX < CAM_LEAD_X_LEFT) newCamX = worldX - CAM_LEAD_X_LEFT;

    /* Vertical dead zone: follow when outside [60..150] */
    if (screenY > CAM_LEAD_Y_DOWN) newCamY = worldY - CAM_LEAD_Y_DOWN;
    else if (screenY < CAM_LEAD_Y_UP) newCamY = worldY - CAM_LEAD_Y_UP;

    /* Clip to world bounds */
    if (newCamX < 0) newCamX = 0;
    if (newCamX > WORLD_WIDTH_PX - 320) newCamX = WORLD_WIDTH_PX - 320;
    if (newCamY < 0) newCamY = 0;
    if (newCamY > WORLD_HEIGHT_PX - 224) newCamY = WORLD_HEIGHT_PX - 224;

    camX = newCamX;
    camY = newCamY;
}

/* =========================================================================
 * VBlank callback — runs during blanking period for zero-tear raster effects
 *
 * BGB gets a sine-wave horizontal scroll applied per scanline.
 * This creates a subtle heat-shimmer / parallax depth effect on the background.
 * ========================================================================= */
void CAMERA_onVBlank(void) {
    s16 bgbBaseScroll = -(camX >> 3) + shakeOffsetX;

    /* Write sine-offset per scanline into BGB horizontal scroll table */
    for (u16 i = 0; i < 224; i++) {
        /* sinFix16 returns fix16 in range [-32768..32767]; >> 11 scales to ~-16..16 px */
        bgbLineScroll[i] = bgbBaseScroll
            + (sinFix16(((i * 3) + sinePhase) & 0xFF) >> 11);
    }

    VDP_setHorizontalScrollLine(BG_B, 0, bgbLineScroll, 224, DMA_QUEUE);

    sinePhase += 2;
    if (sinePhase >= 256) sinePhase = 0;
}

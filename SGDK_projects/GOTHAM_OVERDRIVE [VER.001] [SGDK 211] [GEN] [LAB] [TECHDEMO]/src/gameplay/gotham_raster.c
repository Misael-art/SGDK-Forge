#include "gameplay/gotham_raster.h"
#include "resources.h"

static s16 sBgALineScroll[GOTHAM_RASTER_LINES];
static s16 sBgBLineScroll[GOTHAM_RASTER_LINES];
static s16 sBgAColumnScroll[GOTHAM_RASTER_COLUMNS];
static s16 sBgBColumnScroll[GOTHAM_RASTER_COLUMNS];

static const u16 sBatSignalColors[8] = {
    0x0EEE, 0x0ECC, 0x0CAA, 0x0A88, 0x0866, 0x0A88, 0x0CAA, 0x0ECC
};

void GOTHAM_RASTER_init(u16 bgATileIndex, u16 bgBTileIndex)
{
    u16 i;
    (void)bgATileIndex;
    (void)bgBTileIndex;

    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_COLUMN);

    for (i = 0; i < GOTHAM_RASTER_LINES; i++) {
        sBgALineScroll[i] = 0;
        sBgBLineScroll[i] = 0;
    }
    for (i = 0; i < GOTHAM_RASTER_COLUMNS; i++) {
        sBgAColumnScroll[i] = 0;
        sBgBColumnScroll[i] = 0;
    }

    VDP_setHorizontalScrollLine(BG_A, 0, sBgALineScroll, GOTHAM_RASTER_LINES, CPU);
    VDP_setHorizontalScrollLine(BG_B, 0, sBgBLineScroll, GOTHAM_RASTER_LINES, CPU);
    VDP_setVerticalScrollTile(BG_A, 0, sBgAColumnScroll, GOTHAM_RASTER_COLUMNS, CPU);
    VDP_setVerticalScrollTile(BG_B, 0, sBgBColumnScroll, GOTHAM_RASTER_COLUMNS, CPU);
}

void GOTHAM_RASTER_triggerShake(GothamRasterFx* fx, u8 intensity, u8 frames)
{
    if (fx == NULL) return;
    fx->shakeX = (s16)intensity;
    fx->shakeY = (s16)(intensity >> 1);
    fx->shakeTimer = frames;
}

void GOTHAM_RASTER_triggerFlash(GothamRasterFx* fx, u8 frames)
{
    if (fx == NULL) return;
    fx->flashTimer = frames;
}

void GOTHAM_RASTER_update(GothamRasterFx* fx, bool advance)
{
    u16 line;
    u16 col;
    s16 curve;
    s16 roll;
    s32 bendNum = 0;
    s32 bendDelta;
    s32 streakNum = 0;
    s16 streakStep;
    s16 skyScroll;
    s16 roadSpeed;

    if (fx == NULL) return;

    if (advance) {
        fx->frameCount++;

        // Smooth curve easing
        if (fx->curveAngle < fx->targetCurve) {
            fx->curveAngle += 2;
            if (fx->curveAngle > fx->targetCurve) fx->curveAngle = fx->targetCurve;
        } else if (fx->curveAngle > fx->targetCurve) {
            fx->curveAngle -= 2;
            if (fx->curveAngle < fx->targetCurve) fx->curveAngle = fx->targetCurve;
        }

        // Screen shake decay
        if (fx->shakeTimer > 0) {
            fx->shakeTimer--;
            if (fx->shakeTimer == 0) {
                fx->shakeX = 0;
                fx->shakeY = 0;
            } else {
                fx->shakeX = (fx->shakeTimer & 1) ? (fx->shakeX > 0 ? -fx->shakeX : -fx->shakeX - 1) : (fx->shakeX >> 1);
                fx->shakeY = (fx->shakeTimer & 1) ? (fx->shakeY > 0 ? -fx->shakeY : -fx->shakeY - 1) : (fx->shakeY >> 1);
            }
        }

        // Screen flash decay
        if (fx->flashTimer > 0) {
            fx->flashTimer--;
            if (fx->flashTimer == 0) {
                // Restore palette
                PAL_setPalette(PAL0, img_gotham_skyline_bgb.palette->data, DMA_QUEUE);
                PAL_setPalette(PAL1, img_gotham_roadway_bga.palette->data, DMA_QUEUE);
            }
        }

        // Bat-Signal pulse
        fx->signalSweepPhase = (u8)((fx->frameCount >> 2) & 7u);
        PAL_setColor(13, sBatSignalColors[fx->signalSweepPhase]);
    }

    curve = fx->curveAngle;
    roll = fx->rollAngle;
    roadSpeed = fx->speed;
    skyScroll = (s16)(fx->frameCount >> 2);
    bendDelta = (s32)curve;
    streakStep = (s16)((fx->frameCount * roadSpeed) & 31u);

    // Scanline Scroll Engine (Multi-Axis Pseudo-3D)
    for (line = 0; line < GOTHAM_RASTER_LINES; line++) {
        if (line < GOTHAM_HORIZON_Y) {
            // Upper Zone: Gotham Dark Deco Skyline (BG_B) with multi-plane parallax
            s16 parallax;
            if (line < 25) {
                // Deep sky / Stars: slowest scroll
                parallax = skyScroll >> 2;
            } else if (line < 50) {
                // Moon / Upper Spires: mid scroll
                parallax = (skyScroll >> 1) + (s16)(sinFix16((fx->frameCount + line) << 2) >> 13);
            } else {
                // Gothic Towers / Cathedral Rooftops
                parallax = skyScroll + (curve >> 2);
            }
            sBgBLineScroll[line] = -parallax + fx->shakeX;
            sBgALineScroll[line] = fx->shakeX;
        } else {
            // Lower Zone: 3D Perspective Roadway (BG_A) and Distant Bridge Pillars (BG_B)
            s16 bend = (s16)(bendNum >> 11);
            s16 streak = (s16)(streakNum >> 6);

            sBgALineScroll[line] = bend - streak + fx->shakeX;
            sBgBLineScroll[line] = -(skyScroll + (curve >> 1)) + (bend >> 3) + fx->shakeX;

            bendNum += bendDelta;
            bendDelta += (curve >> 2);
            streakNum += streakStep;
        }
    }

    // Column Scroll Engine: Vertical tilt & banking
    for (col = 0; col < GOTHAM_RASTER_COLUMNS; col++) {
        s16 colOffset = (s16)(col - 10);
        s16 tiltY = (s16)((colOffset * roll) >> 2);

        sBgAColumnScroll[col] = tiltY + fx->shakeY;
        sBgBColumnScroll[col] = (tiltY >> 2) + fx->shakeY;
    }

    // Push scroll tables to VDP via DMA queue
    VDP_setHorizontalScrollLine(BG_A, 0, sBgALineScroll, GOTHAM_RASTER_LINES, DMA_QUEUE);
    VDP_setHorizontalScrollLine(BG_B, 0, sBgBLineScroll, GOTHAM_RASTER_LINES, DMA_QUEUE);
    VDP_setVerticalScrollTile(BG_A, 0, sBgAColumnScroll, GOTHAM_RASTER_COLUMNS, DMA_QUEUE);
    VDP_setVerticalScrollTile(BG_B, 0, sBgBColumnScroll, GOTHAM_RASTER_COLUMNS, DMA_QUEUE);
}

void GOTHAM_RASTER_reset(void)
{
    u16 i;
    for (i = 0; i < GOTHAM_RASTER_LINES; i++) {
        sBgALineScroll[i] = 0;
        sBgBLineScroll[i] = 0;
    }
    for (i = 0; i < GOTHAM_RASTER_COLUMNS; i++) {
        sBgAColumnScroll[i] = 0;
        sBgBColumnScroll[i] = 0;
    }
    VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);
}

#ifndef GAMEPLAY_GOTHAM_RASTER_H
#define GAMEPLAY_GOTHAM_RASTER_H

#include <genesis.h>

#define GOTHAM_RASTER_LINES 224
#define GOTHAM_RASTER_COLUMNS 20
#define GOTHAM_HORIZON_Y 80

typedef struct GothamRasterFx {
    s16 curveAngle;        // Current road curve (-64 to +64)
    s16 targetCurve;       // Target curve for smooth easing
    s16 rollAngle;         // Camera horizon roll tilt (-16 to +16)
    s16 speed;             // Road scrolling speed
    u32 frameCount;        // Frame counter
    s16 shakeX;            // Screen shake X
    s16 shakeY;            // Screen shake Y
    u8  shakeTimer;        // Shake duration in frames
    u8  flashTimer;        // Screen flash timer
    u8  signalSweepPhase;  // Bat-Signal sweep phase
} GothamRasterFx;

void GOTHAM_RASTER_init(u16 bgATileIndex, u16 bgBTileIndex);
void GOTHAM_RASTER_update(GothamRasterFx* fx, bool advance);
void GOTHAM_RASTER_triggerShake(GothamRasterFx* fx, u8 intensity, u8 frames);
void GOTHAM_RASTER_triggerFlash(GothamRasterFx* fx, u8 frames);
void GOTHAM_RASTER_reset(void);

#endif

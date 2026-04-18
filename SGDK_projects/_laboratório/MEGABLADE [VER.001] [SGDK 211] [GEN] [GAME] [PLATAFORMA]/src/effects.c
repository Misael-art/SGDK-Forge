/**
 * effects.c — Screen shake + palette flash effects
 *
 * Screen shake: applies a pixel offset to both scroll layers.
 *   Alternates direction each frame for a "vibration" feel.
 *   Applied in main.c to MAP_scrollTo calls.
 *
 * Palette flash: alternates player palette between normal and bright white
 *   for a few frames on hit — visual impact feedback.
 */

#include <genesis.h>

#include "effects.h"
#include "game_config.h"

/* =========================================================================
 * State
 * ========================================================================= */
s16 shakeOffsetX = 0;
s16 shakeOffsetY = 0;

static u16 shakeMagnitude = 0;
static u16 shakeDuration  = 0;

static u16 flashDuration  = 0;
static u16 flashPalette[16];
static u16 normalPalette[16];

/* =========================================================================
 * Init — build the flash palette (bright white-yellow)
 * ========================================================================= */
void EFFECTS_init(void) {
    shakeOffsetX   = 0;
    shakeOffsetY   = 0;
    shakeMagnitude = 0;
    shakeDuration  = 0;
    flashDuration  = 0;

    /* Flash palette: all entries set to near-white (RGB 15,15,15 = 0xEEE) */
    for (u16 i = 0; i < 16; i++) {
        flashPalette[i] = RGB24_TO_VDPCOLOR(0xEEEEEE);
    }
    flashPalette[0] = 0x0000; /* index 0 always transparent */
}

/* =========================================================================
 * Start shake
 * ========================================================================= */
void EFFECTS_startShake(u16 magnitude, u16 duration) {
    shakeMagnitude = magnitude;
    shakeDuration  = duration;
}

/* =========================================================================
 * Start palette flash on player palette (PAL2)
 * ========================================================================= */
void EFFECTS_startFlash(u16 duration) {
    flashDuration = duration;
    /* Capture current PAL2 for restoration */
    PAL_getColors(PAL2 * 16, normalPalette, 16);
}

/* =========================================================================
 * Update (call once per frame during gameplay)
 * ========================================================================= */
void EFFECTS_update(void) {

    /* --- Screen shake --- */
    if (shakeDuration > 0) {
        /* Alternate direction each frame for vibration effect */
        shakeOffsetX = (shakeDuration & 1) ?  (s16)shakeMagnitude
                                            : -(s16)shakeMagnitude;
        shakeOffsetY = (shakeDuration & 2) ?  (s16)(shakeMagnitude >> 1)
                                            : -(s16)(shakeMagnitude >> 1);
        shakeDuration--;
    } else {
        shakeOffsetX = 0;
        shakeOffsetY = 0;
    }

    /* --- Palette flash --- */
    if (flashDuration > 0) {
        if (flashDuration & 1)
            PAL_setPalette(PAL2, flashPalette, CPU);
        else
            PAL_setPalette(PAL2, normalPalette, CPU);
        flashDuration--;
    }
}

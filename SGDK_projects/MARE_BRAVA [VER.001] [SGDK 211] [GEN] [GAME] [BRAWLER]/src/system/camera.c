#include <genesis.h>

#include "system/camera.h"

#define CAMERA_VIEWPORT_WIDTH 320
#define CAMERA_VIEWPORT_CENTER (CAMERA_VIEWPORT_WIDTH / 2)
#define CAMERA_DEADZONE_LEFT 16
#define CAMERA_DEADZONE_RIGHT 16
#define CAMERA_LOOKAHEAD_X 32
#define CAMERA_MAX_STEP_PX 4

static fix32 sCameraX;
static s16 sMinX;
static s16 sMaxX;
static bool sInitialized;

static s16 cameraClamp(s16 value)
{
    if (value < sMinX) {
        return sMinX;
    }
    if (value > sMaxX) {
        return sMaxX;
    }
    return value;
}

void CAMERA_init(s16 minX, s16 maxX, s16 initialX)
{
    sMinX = minX;
    sMaxX = (maxX < minX) ? minX : maxX;
    sCameraX = FIX32(cameraClamp(initialX));
    sInitialized = TRUE;
}

void CAMERA_update(fix16 targetWorldX, bool facingRight)
{
    s16 currentX;
    s16 targetX;
    s16 targetScreenX;
    s16 lookahead;
    fix32 targetFix32;

    if (!sInitialized) {
        return;
    }

    currentX = F32_toInt(sCameraX);
    targetScreenX = F16_toInt(targetWorldX) - currentX;
    lookahead = facingRight ? CAMERA_LOOKAHEAD_X : -CAMERA_LOOKAHEAD_X;
    targetX = currentX;

    /* Keep the actor readable while the look-ahead exposes the risk side. */
    if (targetScreenX < CAMERA_VIEWPORT_CENTER - CAMERA_DEADZONE_LEFT) {
        targetX = F16_toInt(targetWorldX) -
                  (CAMERA_VIEWPORT_CENTER - CAMERA_DEADZONE_LEFT) + lookahead;
    } else if (targetScreenX > CAMERA_VIEWPORT_CENTER + CAMERA_DEADZONE_RIGHT) {
        targetX = F16_toInt(targetWorldX) -
                  (CAMERA_VIEWPORT_CENTER + CAMERA_DEADZONE_RIGHT) + lookahead;
    }

    targetX = cameraClamp(targetX);
    targetFix32 = FIX32(targetX);

    if (sCameraX < targetFix32) {
        sCameraX += FIX32(CAMERA_MAX_STEP_PX);
        if (sCameraX > targetFix32) {
            sCameraX = targetFix32;
        }
    } else if (sCameraX > targetFix32) {
        sCameraX -= FIX32(CAMERA_MAX_STEP_PX);
        if (sCameraX < targetFix32) {
            sCameraX = targetFix32;
        }
    }
}

void CAMERA_reset(void)
{
    sCameraX = 0;
    sMinX = 0;
    sMaxX = 0;
    sInitialized = FALSE;
}

s16 CAMERA_getX(void)
{
    if (!sInitialized) {
        return 0;
    }
    return cameraClamp((s16) F32_toInt(sCameraX));
}

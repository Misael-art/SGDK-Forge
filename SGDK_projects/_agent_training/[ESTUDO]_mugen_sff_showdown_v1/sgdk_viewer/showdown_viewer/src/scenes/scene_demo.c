#include <genesis.h>

#include "core/app.h"
#include "system/audio.h"
#include "system/input.h"
#include "resources.h"

#define WORLD_TILES_W 96
#define WORLD_TILES_H 60
#define VIEWPORT_W 320
#define VIEWPORT_H 224
#define WINDOW_TILES_W 42
#define WINDOW_TILES_H 30
#define FRAME_COUNT 4
#define GLOBAL_UNIQUE_TILES 2253
#define CACHE_TILE_CAPACITY 1151
#define MAP_TILE_ID_MASK 0x0FFF
#define MAP_HFLIP_FLAG 0x1000
#define MAP_VFLIP_FLAG 0x2000
#define MAP_PAL_SHIFT 14
#define EMPTY_SLOT 0xFFFF
#define CAMERA_DEFAULT_X 224
#define CAMERA_DEFAULT_Y 256
#define CAMERA_MAX_X 448
#define CAMERA_MAX_Y 256
#define CAMERA_AUTOPAN_HOLD_TICKS 1800
#define CAMERA_AUTOPAN_STEP_MASK 0x0003
#define FRAME_ANIMATION_ENABLED 0

static u16 sFrameIndex;
static u16 sTick;
static u16 sCameraX;
static u16 sCameraY;
static s16 sCameraDx;
static s16 sCameraDy;
static u16 sLastTileX;
static u16 sLastTileY;
static u16 sLastFrameIndex;
static u16 sCacheCount;
static u16 sCacheOverflow;
static u16 sGlobalToSlot[GLOBAL_UNIQUE_TILES];
static u16 sWindowMap[WINDOW_TILES_W * WINDOW_TILES_H];
static u32 sTileUploadBuffer[CACHE_TILE_CAPACITY * 8];

static const u16* getFrameMap(const u16* maps, u16 frame)
{
    return maps + (frame * WORLD_TILES_W * WORLD_TILES_H);
}

static void drawPause(void)
{
    VDP_drawTextFill("==== PAUSE ====", 12, 11, 16);
    VDP_drawTextFill("START: resume", 13, 13, 14);
}

static void resetTileCache(void)
{
    u16 i;

    for (i = 0; i < GLOBAL_UNIQUE_TILES; i++) {
        sGlobalToSlot[i] = EMPTY_SLOT;
    }
    sCacheCount = 0;
    sCacheOverflow = 0;
}

static u16 acquireTileSlot(u16 globalTileId)
{
    u16 slot;
    const u8* tileSource;

    if (globalTileId >= GLOBAL_UNIQUE_TILES) {
        sCacheOverflow = 1;
        return 0;
    }

    slot = sGlobalToSlot[globalTileId];
    if (slot != EMPTY_SLOT) {
        return slot;
    }

    if (sCacheCount >= CACHE_TILE_CAPACITY) {
        sCacheOverflow = 1;
        return 0;
    }

    slot = sCacheCount++;
    sGlobalToSlot[globalTileId] = slot;
    tileSource = ((const u8*)bin_showdown_tiles) + ((u32)globalTileId * 32UL);
    {
        u16 i;
        const u32* src = (const u32*)tileSource;
        u32* dst = &sTileUploadBuffer[slot * 8];

        for (i = 0; i < 8; i++) {
            dst[i] = src[i];
        }
    }
    return slot;
}

static void streamCameraWindow(void)
{
    const u16* maps = (const u16*)bin_showdown_maps;
    const u16* frameMap = getFrameMap(maps, sFrameIndex);
    const u16 tileX = sCameraX >> 3;
    const u16 tileY = sCameraY >> 3;
    u16 wy;
    u16 wx;

    resetTileCache();

    for (wy = 0; wy < WINDOW_TILES_H; wy++) {
        const u16 srcY = min(WORLD_TILES_H - 1, tileY + wy);
        for (wx = 0; wx < WINDOW_TILES_W; wx++) {
            const u16 srcX = min(WORLD_TILES_W - 1, tileX + wx);
            const u16 raw = frameMap[(srcY * WORLD_TILES_W) + srcX];
            const u16 globalTileId = raw & MAP_TILE_ID_MASK;
            const u16 slot = acquireTileSlot(globalTileId);
            u16 word = TILE_USER_INDEX + slot;

            if (raw & MAP_HFLIP_FLAG) {
                word |= TILE_ATTR_HFLIP_MASK;
            }
            if (raw & MAP_VFLIP_FLAG) {
                word |= TILE_ATTR_VFLIP_MASK;
            }
            word |= ((raw >> MAP_PAL_SHIFT) & 0x3) << 13;
            sWindowMap[(wy * WINDOW_TILES_W) + wx] = word;
        }
    }

    if (sCacheCount > 0) {
        VDP_loadTileData(sTileUploadBuffer, TILE_USER_INDEX, sCacheCount, CPU);
    }
    VDP_setTileMapDataRect(BG_A, sWindowMap, 0, 0, WINDOW_TILES_W, WINDOW_TILES_H, WINDOW_TILES_W, CPU);
    sLastTileX = tileX;
    sLastTileY = tileY;
    sLastFrameIndex = sFrameIndex;
}

static void applyCamera(void)
{
    const u16 tileX = sCameraX >> 3;
    const u16 tileY = sCameraY >> 3;

    if ((tileX != sLastTileX) || (tileY != sLastTileY) || (sFrameIndex != sLastFrameIndex)) {
        streamCameraWindow();
    }

    VDP_setHorizontalScroll(BG_A, -(s16)(sCameraX & 7));
    VDP_setVerticalScroll(BG_A, -(s16)(sCameraY & 7));
}

static void clampCamera(void)
{
    if (sCameraX > CAMERA_MAX_X) {
        sCameraX = CAMERA_MAX_X;
    }
    if (sCameraY > CAMERA_MAX_Y) {
        sCameraY = CAMERA_MAX_Y;
    }
}

static void autopanCamera(void)
{
    s16 nextX;
    s16 nextY;

    if ((sTick < CAMERA_AUTOPAN_HOLD_TICKS) || ((sTick & CAMERA_AUTOPAN_STEP_MASK) != 0)) {
        return;
    }

    nextX = (s16)sCameraX + sCameraDx;
    if (nextX < 0) {
        nextX = 0;
        sCameraDx = 1;
    } else if (nextX > CAMERA_MAX_X) {
        nextX = CAMERA_MAX_X;
        sCameraDx = -1;
    }

    nextY = (s16)sCameraY + sCameraDy;
    if (nextY < 0) {
        nextY = 0;
        sCameraDy = 1;
    } else if (nextY > CAMERA_MAX_Y) {
        nextY = CAMERA_MAX_Y;
        sCameraDy = -1;
    }

    sCameraX = (u16)nextX;
    sCameraY = (u16)nextY;
}

static void updateCamera(void)
{
    bool manual = FALSE;

    if (INPUT_held(BUTTON_LEFT)) {
        sCameraX = (sCameraX > 1) ? (sCameraX - 2) : 0;
        manual = TRUE;
    } else if (INPUT_held(BUTTON_RIGHT)) {
        sCameraX += 2;
        manual = TRUE;
    }

    if (INPUT_held(BUTTON_UP)) {
        sCameraY = (sCameraY > 1) ? (sCameraY - 2) : 0;
        manual = TRUE;
    } else if (INPUT_held(BUTTON_DOWN)) {
        sCameraY += 2;
        manual = TRUE;
    }

    if (!manual) {
        autopanCamera();
    }

    clampCamera();
}

void SCENE_demoEnter(void)
{
    VDP_setTextPlane(WINDOW);
    VDP_setEnable(FALSE);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_A, 0);

    const u16* pals = (const u16*)bin_showdown_palettes;
    PAL_setPalette(PAL0, pals + (0 * 16), DMA_QUEUE);
    PAL_setPalette(PAL1, pals + (1 * 16), DMA_QUEUE);
    PAL_setPalette(PAL2, pals + (2 * 16), DMA_QUEUE);
    PAL_setPalette(PAL3, pals + (3 * 16), DMA_QUEUE);

    sFrameIndex = 0;
    sTick = 0;
    sCameraX = CAMERA_DEFAULT_X;
    sCameraY = CAMERA_DEFAULT_Y;
    sCameraDx = 1;
    sCameraDy = -1;
    sLastTileX = EMPTY_SLOT;
    sLastTileY = EMPTY_SLOT;
    sLastFrameIndex = EMPTY_SLOT;
    streamCameraWindow();
    applyCamera();
    VDP_setEnable(TRUE);
}

void SCENE_demoUpdate(void)
{
    if (INPUT_pressed(BUTTON_START)) {
        gApp.paused = !gApp.paused;
        AUDIO_playCue(AUDIO_CUE_PAUSE);
        if (!gApp.paused) {
            VDP_clearTextArea(12, 11, 16, 3);
        }
        return;
    }

    if (gApp.paused) {
        drawPause();
        return;
    }

    if (INPUT_pressed(BUTTON_MODE)) {
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    sTick++;
    updateCamera();
#if FRAME_ANIMATION_ENABLED
    if ((sTick & 0x0F) == 0) {
        sFrameIndex = (u16)((sFrameIndex + 1) % FRAME_COUNT);
    }
#endif
    applyCamera();
}

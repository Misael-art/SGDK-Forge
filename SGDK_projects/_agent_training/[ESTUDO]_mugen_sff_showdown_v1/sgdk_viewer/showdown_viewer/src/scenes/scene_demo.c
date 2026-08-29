#include <genesis.h>

#include "core/app.h"
#include "system/audio.h"
#include "system/input.h"
#include "resources.h"

#define WORLD_TILES_W 96
#define WORLD_TILES_H 60
#define VIEWPORT_W 320
#define VIEWPORT_H 224
#define WINDOW_TILES_W 41
#define WINDOW_TILES_H 29
#define FRAME_COUNT 4
#define ROUTE_A_PLANE_COUNT 2
#define ROUTE_A_PLANE_BG_B 0
#define ROUTE_A_PLANE_BG_A 1
#define GLOBAL_UNIQUE_TILES 2870
#define CACHE_TILE_CAPACITY 1190
#define TILE_UPLOAD_BATCH_TILES 16
#define BLANK_GLOBAL_TILE_ID 1303
#define MAP_TILES_PER_FRAME (WORLD_TILES_W * WORLD_TILES_H)
#define MAP_WORDS_PER_FRAME (MAP_TILES_PER_FRAME * ROUTE_A_PLANE_COUNT)
#define MAP_TILE_ID_MASK 0x0FFF
#define MAP_HFLIP_FLAG 0x1000
#define MAP_VFLIP_FLAG 0x2000
#define MAP_PAL_SHIFT 14
#define EMPTY_SLOT 0xFFFF
#define MUGEN_ZOFFSET 215
#define CAMERA_DEFAULT_X 224
#define CAMERA_DEFAULT_Y 256
#define CAMERA_MAX_X 448
#define CAMERA_MAX_Y 256
#define FIGHT_FOCUS_WORLD_X (CAMERA_DEFAULT_X + (VIEWPORT_W / 2))
#define FLOOR_ANCHOR_WORLD_Y (CAMERA_DEFAULT_Y + MUGEN_ZOFFSET)
#define FRAME_ANIMATION_ENABLED 0
#define FRAME_ANIMATION_INTERVAL_FRAMES 45 /* P6b medido: incremental delta reduz DMA mas sem eviction a uniao estoura; ver p6_incremental_report */
#define CAMERA_EXPLORATORY_INPUT_ENABLED 0
#define CAMERA_FIGHT_INPUT_ENABLED 1
#define FIGHTER_START_OFFSET_X 70
#define FIGHTER_MIN_X 24
#define FIGHTER_MAX_X ((WORLD_TILES_W * 8) - 24)
#define FIGHTER_MAX_SEPARATION_X (VIEWPORT_W - 96)
#define CAMERA_VERTICAL_DEADZONE_PX 100
#define CAMERA_VERTICALFOLLOW_NUM 1
#define CAMERA_VERTICALFOLLOW_DEN 2
#define CAMERA_SMOOTH_STEP_X 6
#define CAMERA_SMOOTH_STEP_Y 8
#define SUPER_JUMP_TOTAL_TICKS 96
#define SUPER_JUMP_RISE_TICKS 48
#define SUPER_JUMP_SPEED_PX 6
#define DEMO_ENTER_INPUT_COOLDOWN_TICKS 12
#define PARALLAX_FAR_SCREEN_MAX_Y 72
#define PARALLAX_MID_SCREEN_MAX_Y 176
#define WATER_LINE_TOP 88
#define WATER_LINE_BOTTOM 176
#define BGA_TILEMAP_VRAM 0xC000
#define WINDOW_TILEMAP_VRAM 0xD000
#define BGB_TILEMAP_VRAM 0xE000
#define HSCROLL_TABLE_VRAM 0xF000
#define SPRITE_TABLE_VRAM 0xF800

static u16 sFrameIndex;
static u16 sTick;
static u16 sCameraX;
static u16 sCameraY;
static u16 sP1WorldX;
static u16 sP1WorldY;
static u16 sP2WorldX;
static u16 sP2WorldY;
static u16 sP1JumpTick;
static u16 sP2JumpTick;
static u16 sInputCooldownTicks;
static u16 sLastTileX;
static u16 sLastTileY;
static u16 sLastFrameIndex;
static u16 sLastBgBTileX;
static u16 sLastBgBTileY;
static u16 sLastRowTileX[WINDOW_TILES_H];
static u16 sLastRowTileY[WINDOW_TILES_H];
static u16 sCacheCount;
static u16 sCacheOverflow;
static u16 sTileUploadBatchStart;
static u16 sTileUploadBatchCount;
static u16 sGlobalToSlot[GLOBAL_UNIQUE_TILES];
static u8 sTileOpacityState[GLOBAL_UNIQUE_TILES];
static u8 sWindowAOpaque[WINDOW_TILES_W * WINDOW_TILES_H];
static u16 sWindowMapA[WINDOW_TILES_W * WINDOW_TILES_H];
static u16 sWindowMapB[WINDOW_TILES_W * WINDOW_TILES_H];
static u16 sWindowGlobalA[WINDOW_TILES_W * WINDOW_TILES_H];
static u16 sWindowGlobalB[WINDOW_TILES_W * WINDOW_TILES_H];
static u32 sTileUploadBatch[TILE_UPLOAD_BATCH_TILES * 8];
static s16 sLineScrollA[VIEWPORT_H];
static s16 sLineScrollB[VIEWPORT_H];

static u16 clampSignedToRange(s16 value, u16 minValue, u16 maxValue);

static const u16* getFramePlaneMap(const u16* maps, u16 frame, u16 plane)
{
    return maps + ((u32)frame * MAP_WORDS_PER_FRAME) + ((u32)plane * MAP_TILES_PER_FRAME);
}

static void drawPause(void)
{
    VDP_drawTextFill("==== PAUSE ====", 12, 11, 16);
    VDP_drawTextFill("START: resume", 13, 13, 14);
}

/* Telemetria de streaming (P2 do plano de continuidade).
   Lida pela probe via bloco TSTR na SRAM e pelo leitor Python local.
   [0]=tiles pedidos total [1]=tiles enviados via DMA total
   [2]=chamadas de upload [3]=eventos de overflow
   [4]=pico de residentes num unico passe [5]=capacidade do cache
   [6]=tiles globais unicos [7]=magic 0x54533130 ("TS10") */
u32 gTileStreamStats[8];
static u16 sStreamPassPeak;

/* Varredura P3: centro + 4 cantos do mundo, pico/requisicoes por parada.
   Arrays nao-static: a probe (runtime_probe.c) exporta via bloco TSTR. */
u16 sSweepPeakPerStop[5];
u16 sSweepReqPerStop[5];
u16 sSweepStopsDone;
static u16 sSweepActive;
static u16 sSweepStop;
static u16 sSweepReqMark;

static void statFlushBatch(u16 count)
{
    gTileStreamStats[1] += count;
    gTileStreamStats[2] += 1;
}

static void statEndStreamingPass(void)
{
    if (sStreamPassPeak > (u16) gTileStreamStats[4]) {
        gTileStreamStats[4] = sStreamPassPeak;
    }
    if (sSweepActive && (sSweepStop < 5)) {
        sSweepPeakPerStop[sSweepStop] = sStreamPassPeak;
        sSweepReqPerStop[sSweepStop] = (u16)(gTileStreamStats[0] - sSweepReqMark);
        sSweepStopsDone |= (u16)(1 << sSweepStop);
    }
    sStreamPassPeak = 0;
}

static void resetTileCache(void)
{
    u16 i;

    for (i = 0; i < GLOBAL_UNIQUE_TILES; i++) {
        sGlobalToSlot[i] = EMPTY_SLOT;
    }
    sCacheCount = 0;
    sCacheOverflow = 0;
    sTileUploadBatchStart = 0;
    sTileUploadBatchCount = 0;
}

static void resetTileOpacityCache(void)
{
    u16 i;

    for (i = 0; i < GLOBAL_UNIQUE_TILES; i++) {
        sTileOpacityState[i] = 0;
    }
}

static u16 acquireTileSlot(u16 globalTileId)
{
    u16 slot;
    const u8* tileSource;

    if (globalTileId >= GLOBAL_UNIQUE_TILES) {
        sCacheOverflow = 1;
        gTileStreamStats[3] += 1;
        return 0;
    }

    slot = sGlobalToSlot[globalTileId];
    if (slot != EMPTY_SLOT) {
        return slot;
    }

    if (sCacheCount >= CACHE_TILE_CAPACITY) {
        sCacheOverflow = 1;
        gTileStreamStats[3] += 1;
        return 0;
    }

    slot = sCacheCount++;
    gTileStreamStats[0] += 1;
    sStreamPassPeak = (sCacheCount > sStreamPassPeak) ? sCacheCount : sStreamPassPeak;
    sGlobalToSlot[globalTileId] = slot;
    tileSource = ((const u8*)bin_showdown_tiles) + ((u32)globalTileId * 32UL);
    if (
        (sTileUploadBatchCount >= TILE_UPLOAD_BATCH_TILES)
        || ((sTileUploadBatchCount > 0) && ((sTileUploadBatchStart + sTileUploadBatchCount) != slot))
    ) {
        VDP_loadTileData(sTileUploadBatch, TILE_USER_INDEX + sTileUploadBatchStart, sTileUploadBatchCount, CPU);
        statFlushBatch(sTileUploadBatchCount);
        sTileUploadBatchCount = 0;
    }
    if (sTileUploadBatchCount == 0) {
        sTileUploadBatchStart = slot;
    }
    {
        u16 i;
        const u32* src = (const u32*)tileSource;
        u32* dst = &sTileUploadBatch[sTileUploadBatchCount * 8];

        for (i = 0; i < 8; i++) {
            dst[i] = src[i];
        }
    }
    sTileUploadBatchCount++;
    return slot;
}

static void flushTileUploadBatch(void)
{
    if (sTileUploadBatchCount > 0) {
        VDP_loadTileData(sTileUploadBatch, TILE_USER_INDEX + sTileUploadBatchStart, sTileUploadBatchCount, CPU);
        statFlushBatch(sTileUploadBatchCount);
        sTileUploadBatchCount = 0;
    }
}

static u16 globalTileIsOpaqueForOverlay(u16 globalTileId)
{
    u16 i;
    const u8* tileSource;

    if (globalTileId >= GLOBAL_UNIQUE_TILES) {
        return FALSE;
    }
    if (sTileOpacityState[globalTileId] == 2) {
        return TRUE;
    }
    if (sTileOpacityState[globalTileId] == 1) {
        return FALSE;
    }

    tileSource = ((const u8*)bin_showdown_tiles) + ((u32)globalTileId * 32UL);
    for (i = 0; i < 32; i++) {
        const u8 packed = tileSource[i];
        if (((packed & 0xF0) == 0) || ((packed & 0x0F) == 0)) {
            sTileOpacityState[globalTileId] = 1;
            return FALSE;
        }
    }

    sTileOpacityState[globalTileId] = 2;
    return TRUE;
}

static u16 customMapWordToSgdkAttr(u16 raw, u16 slot)
{
    u16 word = TILE_USER_INDEX + slot;

    if (raw & MAP_HFLIP_FLAG) {
        word |= TILE_ATTR_HFLIP_MASK;
    }
    if (raw & MAP_VFLIP_FLAG) {
        word |= TILE_ATTR_VFLIP_MASK;
    }
    word |= ((raw >> MAP_PAL_SHIFT) & 0x3) << 13;
    return word;
}

static u16 scaledCameraFromDefault(u16 cameraValue, u16 defaultValue, s16 num, s16 den, u16 maxValue)
{
    const s16 delta = (s16)cameraValue - (s16)defaultValue;
    const s16 scaled = (s16)defaultValue + ((delta * num) / den);

    return clampSignedToRange(scaled, 0, maxValue);
}

static u16 layerCameraXForScreenY(u16 screenY)
{
    if (screenY < PARALLAX_FAR_SCREEN_MAX_Y) {
        return scaledCameraFromDefault(sCameraX, CAMERA_DEFAULT_X, 43, 100, CAMERA_MAX_X);
    }
    if (screenY < PARALLAX_MID_SCREEN_MAX_Y) {
        return scaledCameraFromDefault(sCameraX, CAMERA_DEFAULT_X, 71, 100, CAMERA_MAX_X);
    }
    return sCameraX;
}

static u16 layerCameraYForScreenY(u16 screenY)
{
    if (screenY < PARALLAX_FAR_SCREEN_MAX_Y) {
        return scaledCameraFromDefault(sCameraY, CAMERA_DEFAULT_Y, 285, 1000, CAMERA_MAX_Y);
    }
    if (screenY < PARALLAX_MID_SCREEN_MAX_Y) {
        return scaledCameraFromDefault(sCameraY, CAMERA_DEFAULT_Y, 635, 1000, CAMERA_MAX_Y);
    }
    return sCameraY;
}

static s16 waterLineExtra(u16 screenY)
{
    s16 cameraDelta;
    u16 depth;

    if ((screenY < WATER_LINE_TOP) || (screenY >= WATER_LINE_BOTTOM)) {
        return 0;
    }

    cameraDelta = (s16)sCameraX - (s16)CAMERA_DEFAULT_X;
    if (cameraDelta < 0) {
        cameraDelta = -cameraDelta;
    }
    depth = (screenY - WATER_LINE_TOP) + 1;
    return (s16)(((u16)cameraDelta * depth) / ((WATER_LINE_BOTTOM - WATER_LINE_TOP) * 10));
}

static void resetLastRowSources(void)
{
    u16 i;

    sLastBgBTileX = EMPTY_SLOT;
    sLastBgBTileY = EMPTY_SLOT;
    for (i = 0; i < WINDOW_TILES_H; i++) {
        sLastRowTileX[i] = EMPTY_SLOT;
        sLastRowTileY[i] = EMPTY_SLOT;
    }
}

static u16 windowSourceChanged(void)
{
    u16 wy;

    if (sFrameIndex != sLastFrameIndex) {
        return TRUE;
    }

    {
        const u16 bgBCameraX = scaledCameraFromDefault(sCameraX, CAMERA_DEFAULT_X, 43, 100, CAMERA_MAX_X);
        const u16 bgBCameraY = scaledCameraFromDefault(sCameraY, CAMERA_DEFAULT_Y, 285, 1000, CAMERA_MAX_Y);
        const u16 bgBTileX = bgBCameraX >> 3;
        const u16 bgBTileY = bgBCameraY >> 3;

        if ((bgBTileX != sLastBgBTileX) || (bgBTileY != sLastBgBTileY)) {
            return TRUE;
        }
    }

    for (wy = 0; wy < WINDOW_TILES_H; wy++) {
        const u16 screenY = wy << 3;
        const u16 rowCameraX = layerCameraXForScreenY(screenY);
        const u16 rowCameraY = layerCameraYForScreenY(screenY);
        const u16 tileX = rowCameraX >> 3;
        const u16 tileY = min(WORLD_TILES_H - 1, (rowCameraY >> 3) + wy);

        if ((tileX != sLastRowTileX[wy]) || (tileY != sLastRowTileY[wy])) {
            return TRUE;
        }
    }

    return FALSE;
}

static void streamCameraWindow(void)
{
    const u16* maps = (const u16*)bin_showdown_maps;
    const u16* frameMapB = getFramePlaneMap(maps, sFrameIndex, ROUTE_A_PLANE_BG_B);
    const u16* frameMapA = getFramePlaneMap(maps, sFrameIndex, ROUTE_A_PLANE_BG_A);
    const u16 bgBCameraX = scaledCameraFromDefault(sCameraX, CAMERA_DEFAULT_X, 43, 100, CAMERA_MAX_X);
    const u16 bgBCameraY = scaledCameraFromDefault(sCameraY, CAMERA_DEFAULT_Y, 285, 1000, CAMERA_MAX_Y);
    const u16 bgBTileX = bgBCameraX >> 3;
    const u16 bgBTileY = bgBCameraY >> 3;
    u16 blankSlot;
    u16 wy;
    u16 wx;
    u16 isFrameOnlyChange = 0;

    if ((sFrameIndex != sLastFrameIndex) && (sLastFrameIndex != EMPTY_SLOT) && (sLastTileX != EMPTY_SLOT)) {
        u16 cameraMoved = 0;
        if ((bgBTileX != sLastBgBTileX) || (bgBTileY != sLastBgBTileY)) {
            cameraMoved = 1;
        } else {
            for (wy = 0; wy < WINDOW_TILES_H; wy++) {
                const u16 screenY = wy << 3;
                const u16 rowCameraX = layerCameraXForScreenY(screenY);
                const u16 rowCameraY = layerCameraYForScreenY(screenY);
                const u16 tileX = rowCameraX >> 3;
                const u16 tileY = min(WORLD_TILES_H - 1, (rowCameraY >> 3) + wy);
                if ((tileX != sLastRowTileX[wy]) || (tileY != sLastRowTileY[wy])) {
                    cameraMoved = 1;
                    break;
                }
            }
        }
        if (!cameraMoved) {
            isFrameOnlyChange = 1;
        }
    }

    if (isFrameOnlyChange) {
        /* P6b incremental: delta entre frames, sem resetTileCache. */
        blankSlot = sGlobalToSlot[BLANK_GLOBAL_TILE_ID];
        if (blankSlot == EMPTY_SLOT) {
            blankSlot = acquireTileSlot(BLANK_GLOBAL_TILE_ID);
        }
        for (wy = 0; wy < WINDOW_TILES_H; wy++) {
            const u16 screenY = wy << 3;
            const u16 rowCameraX = layerCameraXForScreenY(screenY);
            const u16 rowCameraY = layerCameraYForScreenY(screenY);
            const u16 tileX = rowCameraX >> 3;
            const u16 srcY = min(WORLD_TILES_H - 1, (rowCameraY >> 3) + wy);
            for (wx = 0; wx < WINDOW_TILES_W; wx++) {
                const u16 srcX = min(WORLD_TILES_W - 1, tileX + wx);
                const u16 raw = frameMapA[(srcY * WORLD_TILES_W) + srcX];
                const u16 globalTileId = raw & MAP_TILE_ID_MASK;
                const u16 index = (wy * WINDOW_TILES_W) + wx;
                if (sWindowGlobalA[index] != globalTileId) {
                    const u16 slot = acquireTileSlot(globalTileId);
                    sWindowGlobalA[index] = globalTileId;
                    sWindowAOpaque[index] = globalTileIsOpaqueForOverlay(globalTileId);
                    sWindowMapA[index] = customMapWordToSgdkAttr(raw, slot);
                } else if (globalTileId != sWindowGlobalA[index]) {
                    sWindowAOpaque[index] = globalTileIsOpaqueForOverlay(globalTileId);
                }
            }
            sLastRowTileX[wy] = tileX;
            sLastRowTileY[wy] = srcY;
        }
        for (wy = 0; wy < WINDOW_TILES_H; wy++) {
            const u16 srcY = min(WORLD_TILES_H - 1, bgBTileY + wy);
            for (wx = 0; wx < WINDOW_TILES_W; wx++) {
                const u16 index = (wy * WINDOW_TILES_W) + wx;
                if (sWindowAOpaque[index]) {
                    sWindowMapB[index] = TILE_USER_INDEX + blankSlot;
                    sWindowGlobalB[index] = BLANK_GLOBAL_TILE_ID;
                } else {
                    const u16 srcX = min(WORLD_TILES_W - 1, bgBTileX + wx);
                    const u16 raw = frameMapB[(srcY * WORLD_TILES_W) + srcX];
                    const u16 globalTileId = raw & MAP_TILE_ID_MASK;
                    if (sWindowGlobalB[index] != globalTileId) {
                        const u16 slot = acquireTileSlot(globalTileId);
                        sWindowGlobalB[index] = globalTileId;
                        sWindowMapB[index] = customMapWordToSgdkAttr(raw, slot);
                    }
                }
            }
        }
        flushTileUploadBatch();
        VDP_setTileMapDataRect(BG_B, sWindowMapB, 0, 0, WINDOW_TILES_W, WINDOW_TILES_H, WINDOW_TILES_W, CPU);
        VDP_setTileMapDataRect(BG_A, sWindowMapA, 0, 0, WINDOW_TILES_W, WINDOW_TILES_H, WINDOW_TILES_W, CPU);
        statEndStreamingPass();
        sLastTileX = sCameraX >> 3;
        sLastTileY = sCameraY >> 3;
        sLastBgBTileX = bgBTileX;
        sLastBgBTileY = bgBTileY;
        sLastFrameIndex = sFrameIndex;
        return;
    }

    resetTileCache();
    blankSlot = acquireTileSlot(BLANK_GLOBAL_TILE_ID);

    /* Overlay first: it tells us which BG_B cells are fully hidden. */
    for (wy = 0; wy < WINDOW_TILES_H; wy++) {
        const u16 screenY = wy << 3;
        const u16 rowCameraX = layerCameraXForScreenY(screenY);
        const u16 rowCameraY = layerCameraYForScreenY(screenY);
        const u16 tileX = rowCameraX >> 3;
        const u16 srcY = min(WORLD_TILES_H - 1, (rowCameraY >> 3) + wy);

        for (wx = 0; wx < WINDOW_TILES_W; wx++) {
            const u16 srcX = min(WORLD_TILES_W - 1, tileX + wx);
            const u16 raw = frameMapA[(srcY * WORLD_TILES_W) + srcX];
            const u16 globalTileId = raw & MAP_TILE_ID_MASK;
            const u16 index = (wy * WINDOW_TILES_W) + wx;
            const u16 slot = acquireTileSlot(globalTileId);

            sWindowAOpaque[index] = globalTileIsOpaqueForOverlay(globalTileId);
            sWindowMapA[index] = customMapWordToSgdkAttr(raw, slot);
            sWindowGlobalA[index] = globalTileId;
        }
        sLastRowTileX[wy] = tileX;
        sLastRowTileY[wy] = srcY;
    }

    for (wy = 0; wy < WINDOW_TILES_H; wy++) {
        const u16 srcY = min(WORLD_TILES_H - 1, bgBTileY + wy);

        for (wx = 0; wx < WINDOW_TILES_W; wx++) {
            const u16 index = (wy * WINDOW_TILES_W) + wx;

            if (sWindowAOpaque[index]) {
                sWindowMapB[index] = TILE_USER_INDEX + blankSlot;
                sWindowGlobalB[index] = BLANK_GLOBAL_TILE_ID;
            } else {
                const u16 srcX = min(WORLD_TILES_W - 1, bgBTileX + wx);
                const u16 raw = frameMapB[(srcY * WORLD_TILES_W) + srcX];
                const u16 globalTileId = raw & MAP_TILE_ID_MASK;
                const u16 slot = acquireTileSlot(globalTileId);
                sWindowMapB[index] = customMapWordToSgdkAttr(raw, slot);
                sWindowGlobalB[index] = globalTileId;
            }
        }
    }

    flushTileUploadBatch();
    VDP_setTileMapDataRect(BG_B, sWindowMapB, 0, 0, WINDOW_TILES_W, WINDOW_TILES_H, WINDOW_TILES_W, CPU);
    VDP_setTileMapDataRect(BG_A, sWindowMapA, 0, 0, WINDOW_TILES_W, WINDOW_TILES_H, WINDOW_TILES_W, CPU);
    statEndStreamingPass();
    sLastTileX = sCameraX >> 3;
    sLastTileY = sCameraY >> 3;
    sLastBgBTileX = bgBTileX;
    sLastBgBTileY = bgBTileY;
    sLastFrameIndex = sFrameIndex;
}

static void applyCamera(void)
{
    const u16 bgBCameraX = scaledCameraFromDefault(sCameraX, CAMERA_DEFAULT_X, 43, 100, CAMERA_MAX_X);
    const u16 bgBCameraY = scaledCameraFromDefault(sCameraY, CAMERA_DEFAULT_Y, 285, 1000, CAMERA_MAX_Y);
    u16 line;

    if (windowSourceChanged()) {
        streamCameraWindow();
    }

    for (line = 0; line < VIEWPORT_H; line++) {
        const u16 rowCameraX = layerCameraXForScreenY(line);
        sLineScrollA[line] = -(s16)(rowCameraX & 7);
        sLineScrollA[line] += waterLineExtra(line);
        sLineScrollB[line] = -(s16)(bgBCameraX & 7);
    }

    VDP_setHorizontalScrollLine(BG_B, 0, sLineScrollB, VIEWPORT_H, DMA_QUEUE);
    VDP_setHorizontalScrollLine(BG_A, 0, sLineScrollA, VIEWPORT_H, DMA_QUEUE);
    VDP_setVerticalScroll(BG_B, -(s16)(bgBCameraY & 7));
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

static u16 clampSignedToRange(s16 value, u16 minValue, u16 maxValue)
{
    if (value < (s16)minValue) {
        return minValue;
    }
    if (value > (s16)maxValue) {
        return maxValue;
    }
    return (u16)value;
}

static u16 approachCameraAxis(u16 current, u16 target, u16 step)
{
    if (current < target) {
        const u16 delta = target - current;
        return (delta <= step) ? target : (u16)(current + step);
    }
    if (current > target) {
        const u16 delta = current - target;
        return (delta <= step) ? target : (u16)(current - step);
    }
    return current;
}

static void moveFighterX(u16* fighterX, u16 otherX, s16 delta)
{
    u16 clamped = clampSignedToRange((s16)(*fighterX) + delta, FIGHTER_MIN_X, FIGHTER_MAX_X);

    if (((s16)clamped - (s16)otherX) > (s16)FIGHTER_MAX_SEPARATION_X) {
        clamped = clampSignedToRange((s16)otherX + (s16)FIGHTER_MAX_SEPARATION_X, FIGHTER_MIN_X, FIGHTER_MAX_X);
    } else if (((s16)otherX - (s16)clamped) > (s16)FIGHTER_MAX_SEPARATION_X) {
        clamped = clampSignedToRange((s16)otherX - (s16)FIGHTER_MAX_SEPARATION_X, FIGHTER_MIN_X, FIGHTER_MAX_X);
    }

    *fighterX = clamped;
}

static void updateJumpState(u16* jumpTick, u16* worldY)
{
    if (*jumpTick == 0) {
        *worldY = FLOOR_ANCHOR_WORLD_Y;
        return;
    }

    {
        const u16 tick = *jumpTick;
        const u16 arcTick = (tick < SUPER_JUMP_RISE_TICKS) ? tick : (u16)(SUPER_JUMP_TOTAL_TICKS - tick);
        u16 height = arcTick * SUPER_JUMP_SPEED_PX;

        if (height > FLOOR_ANCHOR_WORLD_Y) {
            height = FLOOR_ANCHOR_WORLD_Y;
        }
        *worldY = FLOOR_ANCHOR_WORLD_Y - height;
    }

    (*jumpTick)++;
    if (*jumpTick >= SUPER_JUMP_TOTAL_TICKS) {
        *jumpTick = 0;
        *worldY = FLOOR_ANCHOR_WORLD_Y;
    }
}

static void updateFighterFixture(void)
{
#if CAMERA_FIGHT_INPUT_ENABLED
    if ((sInputCooldownTicks == 0) && INPUT_held(BUTTON_LEFT)) {
        if (INPUT_held(BUTTON_C)) {
            moveFighterX(&sP2WorldX, sP1WorldX, -2);
        } else {
            moveFighterX(&sP1WorldX, sP2WorldX, -2);
        }
    } else if ((sInputCooldownTicks == 0) && INPUT_held(BUTTON_RIGHT)) {
        if (INPUT_held(BUTTON_C)) {
            moveFighterX(&sP2WorldX, sP1WorldX, 2);
        } else {
            moveFighterX(&sP1WorldX, sP2WorldX, 2);
        }
    }

    if ((sInputCooldownTicks == 0) && INPUT_pressed(BUTTON_A) && (sP1JumpTick == 0)) {
        sP1JumpTick = 1;
    }
    if ((sInputCooldownTicks == 0) && INPUT_pressed(BUTTON_B) && (sP2JumpTick == 0)) {
        sP2JumpTick = 1;
    }
#endif

    updateJumpState(&sP1JumpTick, &sP1WorldY);
    updateJumpState(&sP2JumpTick, &sP2WorldY);
}

static void updateFightCameraFromFocus(void)
{
    const u16 focusX = (sP1WorldX + sP2WorldX) >> 1;
    const u16 highestY = (sP1WorldY < sP2WorldY) ? sP1WorldY : sP2WorldY;
    u16 targetX = clampSignedToRange((s16)focusX - (VIEWPORT_W / 2), 0, CAMERA_MAX_X);
    u16 targetY = CAMERA_DEFAULT_Y;

    if (highestY < FLOOR_ANCHOR_WORLD_Y) {
        const u16 airborneDelta = FLOOR_ANCHOR_WORLD_Y - highestY;
        if (airborneDelta > CAMERA_VERTICAL_DEADZONE_PX) {
            const u16 activeDelta = airborneDelta - CAMERA_VERTICAL_DEADZONE_PX;
            const u16 followedDelta = ((activeDelta * CAMERA_VERTICALFOLLOW_NUM) + (CAMERA_VERTICALFOLLOW_DEN - 1)) / CAMERA_VERTICALFOLLOW_DEN;
            targetY = (followedDelta > CAMERA_DEFAULT_Y) ? 0 : (u16)(CAMERA_DEFAULT_Y - followedDelta);
        }
    }

    if (targetY > CAMERA_MAX_Y) {
        targetY = CAMERA_MAX_Y;
    }

    sCameraX = approachCameraAxis(sCameraX, targetX, CAMERA_SMOOTH_STEP_X);
    sCameraY = approachCameraAxis(sCameraY, targetY, CAMERA_SMOOTH_STEP_Y);
}

static void updateCamera(void)
{
#if CAMERA_EXPLORATORY_INPUT_ENABLED
    if (INPUT_held(BUTTON_LEFT)) {
        sCameraX = (sCameraX > 1) ? (sCameraX - 2) : 0;
    } else if (INPUT_held(BUTTON_RIGHT)) {
        sCameraX += 2;
    }

    if (INPUT_held(BUTTON_UP)) {
        sCameraY = (sCameraY > 1) ? (sCameraY - 2) : 0;
    } else if (INPUT_held(BUTTON_DOWN)) {
        sCameraY += 2;
    }
#endif

    updateFighterFixture();
    updateFightCameraFromFocus();
    clampCamera();
}

void SCENE_demoEnter(void)
{
    gTileStreamStats[5] = CACHE_TILE_CAPACITY;
    gTileStreamStats[6] = GLOBAL_UNIQUE_TILES;
    gTileStreamStats[7] = 0x54533130UL; /* "TS10" */

    VDP_setTextPlane(WINDOW);
    VDP_setEnable(FALSE);
    VDP_setBGAAddress(BGA_TILEMAP_VRAM);
    VDP_setWindowAddress(WINDOW_TILEMAP_VRAM);
    VDP_setBGBAddress(BGB_TILEMAP_VRAM);
    VDP_setHScrollTableAddress(HSCROLL_TABLE_VRAM);
    VDP_setSpriteListAddress(SPRITE_TABLE_VRAM);
    VDP_clearPlane(BG_A, TRUE);
    VDP_clearPlane(BG_B, TRUE);
    VDP_setScrollingMode(HSCROLL_LINE, VSCROLL_PLANE);
    VDP_setHorizontalScroll(BG_A, 0);
    VDP_setHorizontalScroll(BG_B, 0);
    VDP_setVerticalScroll(BG_A, 0);
    VDP_setVerticalScroll(BG_B, 0);

    const u16* pals = (const u16*)bin_showdown_palettes;
    PAL_setPalette(PAL0, pals + (0 * 16), DMA_QUEUE);
    PAL_setPalette(PAL1, pals + (1 * 16), DMA_QUEUE);
    PAL_setPalette(PAL2, pals + (2 * 16), DMA_QUEUE);
    PAL_setPalette(PAL3, pals + (3 * 16), DMA_QUEUE);

    sFrameIndex = 0;
    sTick = 0;
    sCameraX = CAMERA_DEFAULT_X;
    sCameraY = CAMERA_DEFAULT_Y;
    sP1WorldX = FIGHT_FOCUS_WORLD_X - FIGHTER_START_OFFSET_X;
    sP2WorldX = FIGHT_FOCUS_WORLD_X + FIGHTER_START_OFFSET_X;
    sP1WorldY = FLOOR_ANCHOR_WORLD_Y;
    sP2WorldY = FLOOR_ANCHOR_WORLD_Y;
    sP1JumpTick = 0;
    sP2JumpTick = 0;
    sInputCooldownTicks = DEMO_ENTER_INPUT_COOLDOWN_TICKS;
    sLastTileX = EMPTY_SLOT;
    sLastTileY = EMPTY_SLOT;
    sLastFrameIndex = EMPTY_SLOT;
    resetTileOpacityCache();
    resetLastRowSources();
    streamCameraWindow();
    applyCamera();

    /* P3: varredura centro + 4 cantos do mundo (768x480, bounds 0..448 / 0..256).
       Cada parada = um passe completo de streaming com telemetria propria. */
    {
        static const u16 sweepX[5] = { 224, 0, 448, 0, 448 };
        static const u16 sweepY[5] = { 128, 0, 0, 256, 256 };
        u16 i;

        sSweepActive = 1;
        for (i = 0; i < 5; i++) {
            sSweepStop = i;
            sSweepReqMark = (u16) gTileStreamStats[0];
            sCameraX = sweepX[i];
            sCameraY = sweepY[i];
            streamCameraWindow();
            applyCamera();
        }
        sSweepActive = 0;

        /* restaura posicao padrao do stage */
        sCameraX = CAMERA_DEFAULT_X;
        sCameraY = CAMERA_DEFAULT_Y;
        streamCameraWindow();
        applyCamera();
    }

    VDP_setEnable(TRUE);
}

void SCENE_demoUpdate(void)
{
    if (sInputCooldownTicks > 0) {
        sInputCooldownTicks--;
    }

    if ((sInputCooldownTicks == 0) && INPUT_pressed(BUTTON_START)) {
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

    if ((sInputCooldownTicks == 0) && INPUT_pressed(BUTTON_MODE)) {
        VDP_setScrollingMode(HSCROLL_PLANE, VSCROLL_PLANE);
        VDP_setHorizontalScroll(BG_A, 0);
        VDP_setHorizontalScroll(BG_B, 0);
        VDP_setVerticalScroll(BG_A, 0);
        VDP_setVerticalScroll(BG_B, 0);
        APP_changeScene(APP_SCENE_MENU);
        return;
    }

    sTick++;
    updateCamera();
#if FRAME_ANIMATION_ENABLED
    if ((sTick % FRAME_ANIMATION_INTERVAL_FRAMES) == 0) {
        sFrameIndex = (u16)((sFrameIndex + 1) % FRAME_COUNT);
    }
#else
    (void)FRAME_ANIMATION_INTERVAL_FRAMES;
#endif
    applyCamera();
}

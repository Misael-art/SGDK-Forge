#include "sgdk_runtime_probe.h"

#include <sprite_eng_legacy.h>

volatile u16 g_mdRuntimeProbe[MD_RT_SAMPLE_DATA_OFFSET + MD_RT_MAX_SAMPLES];

static u8 s_scanlinePressure[256];
static u16 s_frameScanlinePeak;
static u16 s_activeFxCount;
static u32 s_fxMaskLow;
static u32 s_fxMaskHigh;

static void MD_RT_SetWord(u16 index, u16 value)
{
    g_mdRuntimeProbe[index] = value;
}

static u16 MD_RT_GetWord(u16 index)
{
    return g_mdRuntimeProbe[index];
}

static void MD_RT_AddToSum(u16 sample)
{
    u32 sum = ((u32) MD_RT_GetWord(MD_RT_WORD_CPU_LOAD_SUM_HI) << 16) | MD_RT_GetWord(MD_RT_WORD_CPU_LOAD_SUM_LO);
    sum += sample;
    MD_RT_SetWord(MD_RT_WORD_CPU_LOAD_SUM_HI, (u16) (sum >> 16));
    MD_RT_SetWord(MD_RT_WORD_CPU_LOAD_SUM_LO, (u16) sum);
}

static u16 MD_RT_GetSpriteHeight(const FrameVDPSprite* vdpSprite)
{
    return ((vdpSprite->size & 0x3) + 1) << 3;
}

static void MD_RT_RecordSpriteEngineState(void)
{
    Sprite* cursor = firstSprite;
    u16 activeCount = SPR_getNumActiveSprite();

    if (activeCount > MD_RT_GetWord(MD_RT_WORD_SPRITE_ENGINE_PEAK)) {
        MD_RT_SetWord(MD_RT_WORD_SPRITE_ENGINE_PEAK, activeCount);
    }

    while (cursor)
    {
        if (cursor->frame)
        {
            u16 index;
            u16 count = cursor->frame->numSprite & 0x7F;

            for (index = 0; index < count; index++)
            {
                const FrameVDPSprite* vdpSprite = &cursor->frame->frameVDPSprites[index];
                s16 spriteY = (cursor->y - 0x80) + (s16) vdpSprite->offsetY;
                MD_RT_RecordSpriteSpan(spriteY, MD_RT_GetSpriteHeight(vdpSprite));
            }
        }

        cursor = cursor->next;
    }
}

void MD_RT_Init(void)
{
    u16 index;

    for (index = 0; index < (MD_RT_SAMPLE_DATA_OFFSET + MD_RT_MAX_SAMPLES); index++) {
        g_mdRuntimeProbe[index] = 0;
    }

    for (index = 0; index < 256; index++) {
        s_scanlinePressure[index] = 0;
    }

    s_frameScanlinePeak = 0;
    s_activeFxCount = 0;
    s_fxMaskLow = 0;
    s_fxMaskHigh = 0;

    MD_RT_SetWord(MD_RT_WORD_MAGIC_HI, MD_RT_MAGIC_HI);
    MD_RT_SetWord(MD_RT_WORD_MAGIC_LO, MD_RT_MAGIC_LO);
    MD_RT_SetWord(MD_RT_WORD_VERSION, MD_RT_SCHEMA_VERSION);
    MD_RT_SetWord(MD_RT_WORD_TARGET_FPS, IS_PAL_SYSTEM ? 50 : 60);
    MD_RT_SetWord(MD_RT_WORD_FRAME_WINDOW_TARGET, MD_RT_MAX_SAMPLES);
    MD_RT_SetWord(MD_RT_WORD_SAMPLE_CAPACITY, MD_RT_MAX_SAMPLES);
    MD_RT_SetWord(MD_RT_WORD_BUDGET_THRESHOLD, 100);
}

void MD_RT_SetScene(u16 sceneId)
{
    MD_RT_SetWord(MD_RT_WORD_SCENE_ID, sceneId);
}

void MD_RT_FrameBegin(void)
{
    u16 index;

    for (index = 0; index < 256; index++) {
        s_scanlinePressure[index] = 0;
    }

    s_frameScanlinePeak = 0;
    MD_RT_SetWord(MD_RT_WORD_ACTIVE_FX, s_activeFxCount);
}

void MD_RT_RecordSpriteSpan(s16 y, u16 height)
{
    s16 start;
    s16 end;
    s16 line;

    if (!height) {
        return;
    }

    start = y;
    end = y + (s16) height;

    if (end <= 0 || start >= 256) {
        return;
    }

    if (start < 0) {
        start = 0;
    }

    if (end > 256) {
        end = 256;
    }

    for (line = start; line < end; line++)
    {
        if (s_scanlinePressure[line] < 0xFF) {
            s_scanlinePressure[line]++;
        }

        if (s_scanlinePressure[line] > s_frameScanlinePeak) {
            s_frameScanlinePeak = s_scanlinePressure[line];
        }
    }
}

void MD_RT_MarkFXStart(u16 fxId)
{
    if (fxId < 32)
    {
        u32 mask = (u32) 1 << fxId;
        if (!(s_fxMaskLow & mask))
        {
            s_fxMaskLow |= mask;
            s_activeFxCount++;
        }
    }
    else if (fxId < 64)
    {
        u32 mask = (u32) 1 << (fxId - 32);
        if (!(s_fxMaskHigh & mask))
        {
            s_fxMaskHigh |= mask;
            s_activeFxCount++;
        }
    }

    if (s_activeFxCount > MD_RT_GetWord(MD_RT_WORD_FX_PEAK_CONCURRENCY)) {
        MD_RT_SetWord(MD_RT_WORD_FX_PEAK_CONCURRENCY, s_activeFxCount);
    }

    MD_RT_SetWord(MD_RT_WORD_ACTIVE_FX, s_activeFxCount);
}

void MD_RT_MarkFXEnd(u16 fxId)
{
    if (fxId < 32)
    {
        u32 mask = (u32) 1 << fxId;
        if (s_fxMaskLow & mask)
        {
            s_fxMaskLow &= ~mask;
            if (s_activeFxCount) {
                s_activeFxCount--;
            }
        }
    }
    else if (fxId < 64)
    {
        u32 mask = (u32) 1 << (fxId - 32);
        if (s_fxMaskHigh & mask)
        {
            s_fxMaskHigh &= ~mask;
            if (s_activeFxCount) {
                s_activeFxCount--;
            }
        }
    }

    MD_RT_SetWord(MD_RT_WORD_ACTIVE_FX, s_activeFxCount);
}

void MD_RT_SetPerceptualScores(u16 fluidez, u16 leitura, u16 naturalidade, u16 impacto)
{
    MD_RT_SetWord(MD_RT_WORD_PERCEPTUAL_FLUIDEZ, fluidez);
    MD_RT_SetWord(MD_RT_WORD_PERCEPTUAL_LEITURA, leitura);
    MD_RT_SetWord(MD_RT_WORD_PERCEPTUAL_NATURALIDADE, naturalidade);
    MD_RT_SetWord(MD_RT_WORD_PERCEPTUAL_IMPACTO, impacto);
}

void MD_RT_ExportHeartbeat(u32 currentFrame)
{
    SRAM_enable();

    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 0, 'R');
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 1, 'E');
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 2, 'A');
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 3, 'D');
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 4, 'Y');

    /* bytes 5..7 reservados (zero) */
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 5, 0);
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 6, 0);
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 7, 0);

    /* frame atual em big-endian */
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 8,  (u8) ((currentFrame >> 24) & 0xFF));
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 9,  (u8) ((currentFrame >> 16) & 0xFF));
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 10, (u8) ((currentFrame >> 8)  & 0xFF));
    SRAM_writeByte(MD_RT_HEARTBEAT_SRAM_OFFSET + 11, (u8) (currentFrame         & 0xFF));

    SRAM_disable();
}

void MD_RT_FrameEnd(void)
{
    u16 samplesRecorded = MD_RT_GetWord(MD_RT_WORD_SAMPLES_RECORDED);
    u16 cpuLoad = SYS_getCPULoad();
    u16 previousLoad = MD_RT_GetWord(MD_RT_WORD_CPU_LOAD_PREV);
    u16 delta = (cpuLoad >= previousLoad) ? (cpuLoad - previousLoad) : (previousLoad - cpuLoad);

    MD_RT_RecordSpriteEngineState();

    MD_RT_SetWord(MD_RT_WORD_FRAMES_SEEN, MD_RT_GetWord(MD_RT_WORD_FRAMES_SEEN) + 1);

    if (samplesRecorded < MD_RT_MAX_SAMPLES)
    {
        MD_RT_SetWord(MD_RT_SAMPLE_DATA_OFFSET + samplesRecorded, cpuLoad);
        samplesRecorded++;
        MD_RT_SetWord(MD_RT_WORD_SAMPLES_RECORDED, samplesRecorded);
        if (samplesRecorded >= MD_RT_GetWord(MD_RT_WORD_FRAME_WINDOW_TARGET)) {
            MD_RT_SetWord(MD_RT_WORD_FRAME_WINDOW_COMPLETE, 1);
        }
    }

    MD_RT_AddToSum(cpuLoad);

    if (cpuLoad > MD_RT_GetWord(MD_RT_WORD_CPU_LOAD_MAX)) {
        MD_RT_SetWord(MD_RT_WORD_CPU_LOAD_MAX, cpuLoad);
    }

    if (delta > MD_RT_GetWord(MD_RT_WORD_CPU_LOAD_JITTER_MAX)) {
        MD_RT_SetWord(MD_RT_WORD_CPU_LOAD_JITTER_MAX, delta);
    }

    if (cpuLoad > MD_RT_GetWord(MD_RT_WORD_BUDGET_THRESHOLD)) {
        MD_RT_SetWord(MD_RT_WORD_OVER_BUDGET_FRAMES, MD_RT_GetWord(MD_RT_WORD_OVER_BUDGET_FRAMES) + 1);
    }

    if (s_frameScanlinePeak > MD_RT_GetWord(MD_RT_WORD_MAX_SCANLINE_SPRITES)) {
        MD_RT_SetWord(MD_RT_WORD_MAX_SCANLINE_SPRITES, s_frameScanlinePeak);
    }

    MD_RT_SetWord(MD_RT_WORD_CPU_LOAD_PREV, cpuLoad);
    MD_RT_SetWord(MD_RT_WORD_ACTIVE_FX, s_activeFxCount);
}

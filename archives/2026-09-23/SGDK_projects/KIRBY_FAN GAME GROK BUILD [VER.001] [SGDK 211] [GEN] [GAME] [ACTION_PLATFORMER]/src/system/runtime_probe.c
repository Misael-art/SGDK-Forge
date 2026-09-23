#include <genesis.h>
#include <sprite_eng.h>

#include "system/runtime_probe.h"

/*
 * Instrumentation only. No game header is included on purpose: the game pushes
 * its scene id in through PROBE_setSceneId(), the probe never pulls it out of
 * a scene manager. See system/runtime_probe.h for the SRAM contract.
 */

#define PROBE_MAGIC_HI 0x4D44u /* "MD" */
#define PROBE_MAGIC_LO 0x5254u /* "RT" */
#define PROBE_SCHEMA_VERSION 2u
#define PROBE_SRAM_SCHEMA_VERSION 1u
#define PROBE_VLAB_SCHEMA_VERSION 1u

#define PROBE_TARGET_FPS_NTSC 60u
#define PROBE_TARGET_FPS_PAL 50u
#define PROBE_CPU_BUDGET_THRESHOLD 100u
#define PROBE_SCENE_WARMUP_FRAMES 90u

#define PROBE_SCANLINE_COUNT 224u
#define PROBE_SCANLINE_SAMPLE_GROUPS 4u
#define PROBE_SCANLINE_GROUP_LENGTH \
    (PROBE_SCANLINE_COUNT / PROBE_SCANLINE_SAMPLE_GROUPS)

#define PROBE_VLAB_METRIC_WORDS 24u
#define PROBE_VLAB_PALETTE_WORDS 64u
#define PROBE_VLAB_TOTAL_BYTES \
    (8u + ((PROBE_VLAB_METRIC_WORDS + PROBE_VLAB_PALETTE_WORDS) * 2u))

/* Re-flush cadence so the sealed SRAM is close in time to the screenshot. */
#define PROBE_VLAB_EXPORT_PERIOD 30u
#define PROBE_MDRT_EXPORT_PERIOD 60u

/* SBIS host request block. */
#define PROBE_BOOTSTRAP_VERSION 1u
#define PROBE_BOOTSTRAP_LENGTH 12u
#define PROBE_BOOTSTRAP_CHECKSUM_SEED 0xA55Au

#define PROBE_RASTER_LINES_NTSC 262u
#define PROBE_RASTER_LINES_PAL 313u

volatile u16 g_mdRuntimeProbe[MD_RUNTIME_PROBE_WORD_COUNT];

static u16 s_sceneId;
static u16 s_prevCpuLoad;
static bool s_hasPrevSample;
static u16 s_sceneWarmupFrames;
static u16 s_scanlineCursor;
static u32 s_frameCounter;
static u32 s_heartbeatCounter;

static bool s_bootstrapApplied;
static u16 s_bootstrapScene;

static u16 s_rasterLines;
static u16 s_sectionStart[PROBE_SECTION_COUNT];
static u16 s_sectionAccum[PROBE_SECTION_COUNT];

static u16 s_vlabPalette[PROBE_VLAB_PALETTE_WORDS];

/* ------------------------------------------------------------------ */
/* SRAM primitives                                                     */
/* ------------------------------------------------------------------ */

static void sram_write_u16be(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFFu));
    SRAM_writeByte(offset + 1u, (u8)(value & 0xFFu));
}

static void sram_push_u16be(u32* offset, u16 value)
{
    sram_write_u16be(*offset, value);
    *offset += 2u;
}

static u16 sram_read_u16be(u32 offset)
{
    return (u16)(((u16) SRAM_readByte(offset) << 8) |
                 (u16) SRAM_readByte(offset + 1u));
}

/* ------------------------------------------------------------------ */
/* Sprite pressure sampling                                            */
/* ------------------------------------------------------------------ */

/*
 * Walks the SGDK sprite list and counts how many hardware sprites overlap each
 * of PROBE_SCANLINE_SAMPLE_GROUPS probe scanlines. The probe lines advance one
 * pixel per frame so over PROBE_SCANLINE_GROUP_LENGTH frames every scanline is
 * visited. This is a SAMPLE, not an exhaustive per-scanline census: a spike
 * that lives on a single scanline for a single frame can be missed.
 */
static u16 measure_max_scanline_sprites(void)
{
    Sprite* cursor = firstSprite;
    u16 sampleLines[PROBE_SCANLINE_SAMPLE_GROUPS];
    u8 pressure[PROBE_SCANLINE_SAMPLE_GROUPS] = { 0u, 0u, 0u, 0u };
    u16 sample;
    u16 peak = 0u;

    for (sample = 0u; sample < PROBE_SCANLINE_SAMPLE_GROUPS; sample++) {
        sampleLines[sample] =
            s_scanlineCursor + (sample * PROBE_SCANLINE_GROUP_LENGTH);
    }

    while (cursor != NULL) {
        if ((cursor->frame != NULL) && (cursor->visibility != HIDDEN)) {
            u16 index;
            const u16 count = cursor->frame->numSprite & 0x7Fu;

            for (index = 0u; index < count; index++) {
                const FrameVDPSprite* vdpSprite =
                    &cursor->frame->frameVDPSprites[index];
                const s16 start =
                    (cursor->y - 0x80) + (s16) vdpSprite->offsetY;
                const s16 end =
                    start + (s16)(((vdpSprite->size & 0x3u) + 1u) << 3);

                for (sample = 0u;
                     sample < PROBE_SCANLINE_SAMPLE_GROUPS;
                     sample++) {
                    const s16 scanline = (s16) sampleLines[sample];
                    if ((scanline >= start) && (scanline < end)) {
                        pressure[sample]++;
                        if (pressure[sample] > peak) {
                            peak = pressure[sample];
                        }
                    }
                }
            }
        }
        cursor = cursor->next;
    }

    s_scanlineCursor++;
    if (s_scanlineCursor >= PROBE_SCANLINE_GROUP_LENGTH) {
        s_scanlineCursor = 0u;
    }

    return peak;
}

/* ------------------------------------------------------------------ */
/* Section attribution                                                 */
/* ------------------------------------------------------------------ */

void PROBE_beginSection(u8 section)
{
    if (section >= PROBE_SECTION_COUNT) {
        return;
    }
    s_sectionStart[section] = (u16) GET_VCOUNTER;
}

void PROBE_endSection(u8 section)
{
    u16 now;
    u16 start;
    u16 delta;

    if (section >= PROBE_SECTION_COUNT) {
        return;
    }

    now = (u16) GET_VCOUNTER;
    start = s_sectionStart[section];

    /*
     * GET_VCOUNTER is a raster line index that wraps once per frame. A single
     * wrap is recovered here; a section longer than one full frame is
     * indistinguishable from a short one and will under-report.
     */
    if (now >= start) {
        delta = (u16)(now - start);
    } else {
        delta = (u16)((s_rasterLines - start) + now);
    }

    s_sectionAccum[section] = (u16)(s_sectionAccum[section] + delta);
}

/* ------------------------------------------------------------------ */
/* Scene / lifecycle                                                   */
/* ------------------------------------------------------------------ */

static void reset_scene_metrics(u16 sceneId, u16 cpuLoad)
{
    u16 index;

    g_mdRuntimeProbe[5] = sceneId;
    g_mdRuntimeProbe[6] = 0u;
    g_mdRuntimeProbe[8] = 0u;
    g_mdRuntimeProbe[9] = 0u;
    g_mdRuntimeProbe[10] = 0u;
    g_mdRuntimeProbe[11] = 0u;
    g_mdRuntimeProbe[12] = 0u;
    g_mdRuntimeProbe[13] = 0u;
    g_mdRuntimeProbe[14] = 0u;
    g_mdRuntimeProbe[15] = 0u;
    g_mdRuntimeProbe[16] = 0u;
    g_mdRuntimeProbe[17] = 0u;

    for (index = 0u; index < PROBE_SECTION_COUNT; index++) {
        g_mdRuntimeProbe[18u + index] = 0u;
        s_sectionAccum[index] = 0u;
        s_sectionStart[index] = 0u;
    }

    for (index = 0u; index < MD_RUNTIME_PROBE_MAX_SAMPLES; index++) {
        g_mdRuntimeProbe[MD_RUNTIME_PROBE_SAMPLE_OFFSET + index] = 0u;
    }

    s_frameCounter = 0u;
    s_prevCpuLoad = cpuLoad;
    s_hasPrevSample = FALSE;
    s_sceneWarmupFrames = PROBE_SCENE_WARMUP_FRAMES;
    s_scanlineCursor = 0u;
}

void PROBE_setSceneId(u16 sceneId)
{
    if (sceneId == s_sceneId) {
        return;
    }

    s_sceneId = sceneId;

    /*
     * Always restart the measurement window on a real scene change, even when
     * the host requested a specific boot scene. The probe reports the scene it
     * ACTUALLY measured in word 5 and the scene the host ASKED FOR in word 3;
     * masking a drifting scene behind the requested id would turn a real
     * capture failure into a silently wrong number.
     */
    reset_scene_metrics(sceneId, SYS_getCPULoad());
}

u16 PROBE_getSceneId(void)
{
    return s_sceneId;
}

bool PROBE_bootstrapWasApplied(void)
{
    return s_bootstrapApplied;
}

u16 PROBE_resolveBootScene(u16 fallbackScene, u16 sceneCount)
{
    const u32 offset = MD_RUNTIME_PROBE_BOOTSTRAP_OFFSET;
    u16 version;
    u16 length;
    u16 sceneId;
    u16 checksum;
    u16 expected;
    bool magicOk;

    s_bootstrapApplied = FALSE;
    s_bootstrapScene = 0xFFFFu;

    SRAM_enable();
    magicOk = ((SRAM_readByte(offset + 0u) == (u8) 'S') &&
               (SRAM_readByte(offset + 1u) == (u8) 'B') &&
               (SRAM_readByte(offset + 2u) == (u8) 'I') &&
               (SRAM_readByte(offset + 3u) == (u8) 'S'));

    if (!magicOk) {
        SRAM_disable();
        return fallbackScene;
    }

    version = sram_read_u16be(offset + 4u);
    length = sram_read_u16be(offset + 6u);
    sceneId = sram_read_u16be(offset + 8u);
    checksum = sram_read_u16be(offset + 10u);

    /* Consume the request so a warm reset does not replay it. */
    SRAM_writeByte(offset + 0u, 0u);
    SRAM_writeByte(offset + 1u, 0u);
    SRAM_writeByte(offset + 2u, 0u);
    SRAM_writeByte(offset + 3u, 0u);
    SRAM_disable();

    expected = (u16)(PROBE_BOOTSTRAP_CHECKSUM_SEED ^ version ^ length ^ sceneId);

    if ((version != PROBE_BOOTSTRAP_VERSION) ||
        (length != PROBE_BOOTSTRAP_LENGTH) ||
        (checksum != expected) ||
        (sceneId >= sceneCount)) {
        return fallbackScene;
    }

    s_bootstrapApplied = TRUE;
    s_bootstrapScene = sceneId;
    return sceneId;
}

/* ------------------------------------------------------------------ */
/* SRAM exporters                                                      */
/* ------------------------------------------------------------------ */

void PROBE_writeHeartbeat(void)
{
    const u32 offset = MD_RUNTIME_PROBE_HEARTBEAT_OFFSET;

    SRAM_enable();
    SRAM_writeByte(offset + 0u, (u8) 'R');
    SRAM_writeByte(offset + 1u, (u8) 'E');
    SRAM_writeByte(offset + 2u, (u8) 'A');
    SRAM_writeByte(offset + 3u, (u8) 'D');
    SRAM_writeByte(offset + 4u, (u8) 'Y');
    SRAM_writeByte(offset + 5u, (u8)((s_heartbeatCounter >> 16) & 0xFFu));
    SRAM_writeByte(offset + 6u, (u8)((s_heartbeatCounter >> 8) & 0xFFu));
    SRAM_writeByte(offset + 7u, (u8)(s_heartbeatCounter & 0xFFu));
    SRAM_disable();

    s_heartbeatCounter++;
}

void PROBE_exportMdrtToSram(void)
{
    const u16 wordCount = (u16) MD_RUNTIME_PROBE_WORD_COUNT;
    const u16 totalBytes = (u16)(10u + (wordCount * 2u));
    u32 offset = MD_RUNTIME_PROBE_SRAM_OFFSET;
    u16 index;

    SRAM_enable();
    SRAM_writeByte(offset + 0u, (u8) 'M');
    SRAM_writeByte(offset + 1u, (u8) 'D');
    SRAM_writeByte(offset + 2u, (u8) 'R');
    SRAM_writeByte(offset + 3u, (u8) 'T');
    sram_write_u16be(offset + 4u, PROBE_SRAM_SCHEMA_VERSION);
    sram_write_u16be(offset + 6u, totalBytes);
    sram_write_u16be(offset + 8u, wordCount);

    offset += 10u;
    for (index = 0u; index < wordCount; index++) {
        sram_write_u16be(offset, g_mdRuntimeProbe[index]);
        offset += 2u;
    }
    SRAM_disable();
}

void PROBE_exportVlabToSram(void)
{
    u32 offset = MD_RUNTIME_PROBE_VLAB_OFFSET;
    u16 index;

    /*
     * PAL_getColors reads real CRAM through the VDP data port, but SGDK masks
     * every entry with VDPPALETTE_COLORMASK (0x0EEE). Bits outside the RGB333
     * layout therefore cannot survive into this dump.
     */
    PAL_getColors(0u, s_vlabPalette, PROBE_VLAB_PALETTE_WORDS);

    SRAM_enable();
    SRAM_writeByte(offset + 0u, (u8) 'V');
    SRAM_writeByte(offset + 1u, (u8) 'L');
    SRAM_writeByte(offset + 2u, (u8) 'A');
    SRAM_writeByte(offset + 3u, (u8) 'B');
    sram_write_u16be(offset + 4u, PROBE_VLAB_SCHEMA_VERSION);
    sram_write_u16be(offset + 6u, PROBE_VLAB_TOTAL_BYTES);

    offset += 8u;
    sram_push_u16be(&offset, g_mdRuntimeProbe[5]);   /*  0 scene id       */
    sram_push_u16be(&offset, g_mdRuntimeProbe[6]);   /*  1 frame hi       */
    sram_push_u16be(&offset, g_mdRuntimeProbe[8]);   /*  2 frame lo       */
    sram_push_u16be(&offset, VDP_getScreenWidth());  /*  3               */
    sram_push_u16be(&offset, VDP_getScreenHeight()); /*  4               */
    sram_push_u16be(&offset, VDP_getPlaneWidth());   /*  5               */
    sram_push_u16be(&offset, VDP_getPlaneHeight());  /*  6               */
    sram_push_u16be(&offset, (u16) VDP_getHorizontalScrollingMode()); /* 7 */
    sram_push_u16be(&offset, (u16) VDP_getVerticalScrollingMode());   /* 8 */
    sram_push_u16be(&offset, VDP_getBGAAddress());         /*  9         */
    sram_push_u16be(&offset, VDP_getBGBAddress());         /* 10         */
    sram_push_u16be(&offset, VDP_getWindowAddress());      /* 11         */
    sram_push_u16be(&offset, VDP_getSpriteListAddress());  /* 12         */
    sram_push_u16be(&offset, VDP_getHScrollTableAddress());/* 13         */
    sram_push_u16be(&offset, (u16) VDP_getBackgroundColor()); /* 14      */
    sram_push_u16be(&offset, g_mdRuntimeProbe[8]);   /* 15 frame snapshot */
    sram_push_u16be(&offset, g_mdRuntimeProbe[9]);   /* 16 sample count   */
    sram_push_u16be(&offset, g_mdRuntimeProbe[10]);  /* 17 over budget    */
    sram_push_u16be(&offset, g_mdRuntimeProbe[11]);  /* 18 max cpu load   */
    sram_push_u16be(&offset, g_mdRuntimeProbe[13]);  /* 19 max jitter     */
    sram_push_u16be(&offset, g_mdRuntimeProbe[14]);  /* 20 scanline peak  */
    sram_push_u16be(&offset, g_mdRuntimeProbe[16]);  /* 21 vdp sprites    */
    sram_push_u16be(&offset, g_mdRuntimeProbe[17]);  /* 22 active sprites */
    sram_push_u16be(&offset, g_mdRuntimeProbe[4]);   /* 23 target fps     */

    for (index = 0u; index < PROBE_VLAB_PALETTE_WORDS; index++) {
        sram_push_u16be(&offset, s_vlabPalette[index]);
    }
    SRAM_disable();
}

/* ------------------------------------------------------------------ */
/* Init / tick                                                         */
/* ------------------------------------------------------------------ */

void PROBE_init(void)
{
    u16 index;

    for (index = 0u; index < MD_RUNTIME_PROBE_WORD_COUNT; index++) {
        g_mdRuntimeProbe[index] = 0u;
    }

    g_mdRuntimeProbe[0] = PROBE_MAGIC_HI;
    g_mdRuntimeProbe[1] = PROBE_MAGIC_LO;
    g_mdRuntimeProbe[2] = PROBE_SCHEMA_VERSION;
    g_mdRuntimeProbe[4] =
        SYS_isPAL() ? PROBE_TARGET_FPS_PAL : PROBE_TARGET_FPS_NTSC;
    g_mdRuntimeProbe[23] = PROBE_CPU_BUDGET_THRESHOLD;
    g_mdRuntimeProbe[24] = PROBE_SECTION_COUNT;
    g_mdRuntimeProbe[25] =
        s_bootstrapApplied ? PROBE_FLAG_BOOTSTRAP_APPLIED : 0u;
    /* word 3 = scene the HOST requested (0xFFFF when it requested nothing). */
    g_mdRuntimeProbe[3] = s_bootstrapApplied ? s_bootstrapScene : 0xFFFFu;

    s_rasterLines =
        SYS_isPAL() ? PROBE_RASTER_LINES_PAL : PROBE_RASTER_LINES_NTSC;
    s_heartbeatCounter = 0u;
    s_sceneId = s_bootstrapApplied ? s_bootstrapScene : 0u;

    reset_scene_metrics(s_sceneId, SYS_getCPULoad());
    PROBE_writeHeartbeat();
    PROBE_exportVlabToSram();
    PROBE_exportMdrtToSram();
}

void PROBE_tick(void)
{
    const u16 cpuLoad = SYS_getCPULoad();
    const s32 jitterDelta = (s32) cpuLoad - (s32) s_prevCpuLoad;
    const u16 jitter = (u16)((jitterDelta < 0) ? -jitterDelta : jitterDelta);
    u16 samplesRecorded = g_mdRuntimeProbe[9];
    u16 scanlineSprites;
    u16 usedVdpSprites;
    u16 index;

    s_frameCounter++;
    g_mdRuntimeProbe[5] = PROBE_getSceneId();
    g_mdRuntimeProbe[6] = (u16)((s_frameCounter >> 16) & 0xFFFFu);
    g_mdRuntimeProbe[8] = (u16)(s_frameCounter & 0xFFFFu);

    if ((s_frameCounter % MD_RUNTIME_PROBE_HEARTBEAT_PERIOD) == 0u) {
        PROBE_writeHeartbeat();
    }

    /* Fold this frame's section costs into the running peaks, then clear. */
    for (index = 0u; index < PROBE_SECTION_COUNT; index++) {
        if (s_sectionAccum[index] > g_mdRuntimeProbe[18u + index]) {
            g_mdRuntimeProbe[18u + index] = s_sectionAccum[index];
        }
        s_sectionAccum[index] = 0u;
    }

    if (s_sceneWarmupFrames > 0u) {
        s_sceneWarmupFrames--;
        s_prevCpuLoad = cpuLoad;
        s_hasPrevSample = FALSE;
        /* Peaks collected during warmup are not representative. */
        for (index = 0u; index < PROBE_SECTION_COUNT; index++) {
            g_mdRuntimeProbe[18u + index] = 0u;
        }
        return;
    }

    g_mdRuntimeProbe[12] = cpuLoad;

    if (cpuLoad > PROBE_CPU_BUDGET_THRESHOLD) {
        g_mdRuntimeProbe[10]++;
    }
    if (cpuLoad > g_mdRuntimeProbe[11]) {
        g_mdRuntimeProbe[11] = cpuLoad;
    }
    if (s_hasPrevSample && (jitter > g_mdRuntimeProbe[13])) {
        g_mdRuntimeProbe[13] = jitter;
    }

    scanlineSprites = measure_max_scanline_sprites();
    if (scanlineSprites > g_mdRuntimeProbe[14]) {
        g_mdRuntimeProbe[14] = scanlineSprites;
    }

    usedVdpSprites = SPR_getUsedVDPSprite();
    if (usedVdpSprites > g_mdRuntimeProbe[16]) {
        g_mdRuntimeProbe[16] = usedVdpSprites;
    }
    g_mdRuntimeProbe[17] = SPR_getNumActiveSprite();

    if (samplesRecorded < MD_RUNTIME_PROBE_MAX_SAMPLES) {
        g_mdRuntimeProbe[MD_RUNTIME_PROBE_SAMPLE_OFFSET + samplesRecorded] =
            cpuLoad;
        samplesRecorded++;
        g_mdRuntimeProbe[9] = samplesRecorded;
    }

    s_prevCpuLoad = cpuLoad;
    s_hasPrevSample = TRUE;

    /*
     * Re-flush on a fixed cadence instead of once. The host screenshots at an
     * arbitrary wall-clock moment, so a one-shot export would describe a VDP
     * state hundreds of frames older than the pixels it is compared against.
     */
    if ((s_frameCounter % PROBE_VLAB_EXPORT_PERIOD) == 0u) {
        PROBE_exportVlabToSram();
    }
    if ((s_frameCounter % PROBE_MDRT_EXPORT_PERIOD) == 0u) {
        PROBE_exportMdrtToSram();
    }
}

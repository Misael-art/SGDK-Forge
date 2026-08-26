#include <genesis.h>
#include <sprite_eng.h>

#include "game_vars.h"
#include "system/runtime_probe.h"

/*
 * Canonical ROM-side readiness probe. See system/runtime_probe.h for contract.
 * This module is deliberately small; projects copy it as-is, then tune the
 * warmup and period constants only if budget analysis justifies it.
 */

#define PROBE_MAGIC_HI 0x4D44 /* "MD" */
#define PROBE_MAGIC_LO 0x5254 /* "RT" */
#define PROBE_SCHEMA_VERSION 1
#define PROBE_SRAM_SCHEMA_VERSION 1
#define PROBE_TARGET_FPS_NTSC 60
#define PROBE_TARGET_FPS_PAL 50
#define PROBE_CPU_BUDGET_THRESHOLD 100

/* Bloco visual canonico (espelha seal_fresh_evidence_bundle.py):
   24 words de metrica + 64 words de paleta CRAM, magic "VLAB". */
#define PROBE_VLAB_OFFSET 0x200
#define PROBE_VLAB_SCHEMA_VERSION 1
#define PROBE_VLAB_METRIC_WORDS 24
#define PROBE_VLAB_PALETTE_WORDS 64
#define PROBE_VLAB_TOTAL_BYTES (8 + ((PROBE_VLAB_METRIC_WORDS + PROBE_VLAB_PALETTE_WORDS) * 2))

#define PROBE_SAMPLE_OFFSET 32
#define PROBE_SCENE_WARMUP_FRAMES 90
#define PROBE_SCANLINE_COUNT 224
#define PROBE_SCANLINE_SAMPLE_GROUPS 4
#define PROBE_SCANLINE_GROUP_LENGTH (PROBE_SCANLINE_COUNT / PROBE_SCANLINE_SAMPLE_GROUPS)

volatile u16 g_mdRuntimeProbe[MD_RUNTIME_PROBE_WORD_COUNT];

static u16 s_prevCpuLoad;
static bool s_hasPrevSample;
static u16 s_prevScene;
static u16 s_lastExportSamples;
static u32 s_lastExportFrame;
static u16 s_sceneWarmupFrames;
static u32 s_heartbeatCounter;
static u16 s_scanlineCursor;
static u16 s_vlabPalette[PROBE_VLAB_PALETTE_WORDS];

static u16 measure_max_scanline_sprites(void)
{
    Sprite* cursor = firstSprite;
    u16 sampleLines[PROBE_SCANLINE_SAMPLE_GROUPS];
    u8 pressure[PROBE_SCANLINE_SAMPLE_GROUPS] = { 0, 0, 0, 0 };
    u16 sample;
    u16 peak = 0;

    for (sample = 0; sample < PROBE_SCANLINE_SAMPLE_GROUPS; sample++) {
        sampleLines[sample] = s_scanlineCursor + (sample * PROBE_SCANLINE_GROUP_LENGTH);
    }

    while (cursor != NULL) {
        if (cursor->frame != NULL && cursor->visibility != HIDDEN) {
            u16 index;
            u16 count = cursor->frame->numSprite & 0x7F;

            for (index = 0; index < count; index++) {
                const FrameVDPSprite* vdpSprite = &cursor->frame->frameVDPSprites[index];
                s16 start = (cursor->y - 0x80) + (s16)vdpSprite->offsetY;
                s16 end = start + (s16)(((vdpSprite->size & 0x3) + 1) << 3);

                for (sample = 0; sample < PROBE_SCANLINE_SAMPLE_GROUPS; sample++) {
                    u16 scanline = sampleLines[sample];
                    if (scanline >= start && scanline < end) {
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
        s_scanlineCursor = 0;
    }

    return peak;
}

static void sram_write_u16be(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFF));
    SRAM_writeByte(offset + 1, (u8)(value & 0xFF));
}

static void sram_write_visual_word(u32* offset, u16 value)
{
    sram_write_u16be(*offset, value);
    *offset += 2;
}

static void reset_scene_metrics(u16 sceneId, u16 cpuLoad)
{
    u16 i;

    g_mdRuntimeProbe[5] = sceneId;
    g_mdRuntimeProbe[8] = 0;
    g_mdRuntimeProbe[9] = 0;
    g_mdRuntimeProbe[10] = 0;
    g_mdRuntimeProbe[11] = 0;
    g_mdRuntimeProbe[13] = 0;
    g_mdRuntimeProbe[14] = 0;
    g_mdRuntimeProbe[15] = 0;
    g_mdRuntimeProbe[16] = 0;
    g_mdRuntimeProbe[17] = 0;

    for (i = 0; i < MD_RUNTIME_PROBE_MAX_SAMPLES; i++) {
        g_mdRuntimeProbe[PROBE_SAMPLE_OFFSET + i] = 0;
    }

    s_prevCpuLoad = cpuLoad;
    s_hasPrevSample = FALSE;
    s_lastExportSamples = 0;
    s_lastExportFrame = 0;
    s_sceneWarmupFrames = PROBE_SCENE_WARMUP_FRAMES;
    s_scanlineCursor = 0;
}

static u16 clamp_u16(s32 value)
{
    if (value < 0) return 0;
    if (value > 0xFFFF) return 0xFFFF;
    return (u16) value;
}

void MDRuntimeProbe_writeHeartbeat(void)
{
    /*
     * Rolling READY heartbeat at SRAM[HEARTBEAT_OFFSET]:
     *   [0..4] 'R','E','A','D','Y'
     *   [5..7] 3-byte big-endian rolling counter (advances once per write)
     *
     * The wrapper only checks bytes 0..4 via Test-MDReadyHeartbeat; the
     * rolling counter exists so analytic tooling can confirm the heartbeat
     * is being re-asserted and distinguish live runs from a single stale
     * write that happened to survive a sandbox reset.
     */
    u32 offset = MD_RUNTIME_PROBE_HEARTBEAT_OFFSET;

    SRAM_enable();
    SRAM_writeByte(offset + 0, (u8) 'R');
    SRAM_writeByte(offset + 1, (u8) 'E');
    SRAM_writeByte(offset + 2, (u8) 'A');
    SRAM_writeByte(offset + 3, (u8) 'D');
    SRAM_writeByte(offset + 4, (u8) 'Y');
    SRAM_writeByte(offset + 5, (u8) ((s_heartbeatCounter >> 16) & 0xFF));
    SRAM_writeByte(offset + 6, (u8) ((s_heartbeatCounter >> 8) & 0xFF));
    SRAM_writeByte(offset + 7, (u8) (s_heartbeatCounter & 0xFF));
    SRAM_disable();

    s_heartbeatCounter++;
}

void MDRuntimeProbe_init(void)
{
    u16 i;

    for (i = 0; i < MD_RUNTIME_PROBE_WORD_COUNT; i++) {
        g_mdRuntimeProbe[i] = 0;
    }

    g_mdRuntimeProbe[0] = PROBE_MAGIC_HI;
    g_mdRuntimeProbe[1] = PROBE_MAGIC_LO;
    g_mdRuntimeProbe[2] = PROBE_SCHEMA_VERSION;
    g_mdRuntimeProbe[4] = SYS_isPAL() ? PROBE_TARGET_FPS_PAL : PROBE_TARGET_FPS_NTSC;
    g_mdRuntimeProbe[23] = PROBE_CPU_BUDGET_THRESHOLD;
    s_prevScene = (u16) gApp.currentScene;
    s_heartbeatCounter = 0;
    reset_scene_metrics(s_prevScene, SYS_getCPULoad());
}

void MDRuntimeProbe_exportToSRAM(void)
{
    const u16 wordCount = (u16) MD_RUNTIME_PROBE_WORD_COUNT;
    const u16 totalBytes = (u16)(8u + 2u + (wordCount * 2u));
    u32 offset = MD_RUNTIME_PROBE_SRAM_OFFSET;
    u16 i;

    SRAM_enable();

    SRAM_writeByte(offset + 0, 'M');
    SRAM_writeByte(offset + 1, 'D');
    SRAM_writeByte(offset + 2, 'R');
    SRAM_writeByte(offset + 3, 'T');
    sram_write_u16be(offset + 4, PROBE_SRAM_SCHEMA_VERSION);
    sram_write_u16be(offset + 6, totalBytes);
    sram_write_u16be(offset + 8, wordCount);

    offset += 10;
    for (i = 0; i < wordCount; i++) {
        sram_write_u16be(offset, g_mdRuntimeProbe[i]);
        offset += 2;
    }

    SRAM_disable();
}

static void export_visual_probe_to_sram(void)
{
    u32 offset = PROBE_VLAB_OFFSET;
    u32 frame = gApp.totalFrames;
    u16 i;

    PAL_getColors(0, s_vlabPalette, PROBE_VLAB_PALETTE_WORDS);

    SRAM_enable();

    SRAM_writeByte(offset + 0, 'V');
    SRAM_writeByte(offset + 1, 'L');
    SRAM_writeByte(offset + 2, 'A');
    SRAM_writeByte(offset + 3, 'B');
    sram_write_u16be(offset + 4, PROBE_VLAB_SCHEMA_VERSION);
    sram_write_u16be(offset + 6, PROBE_VLAB_TOTAL_BYTES);

    offset += 8;
    sram_write_visual_word(&offset, g_mdRuntimeProbe[5]);
    sram_write_visual_word(&offset, (u16)((frame >> 16) & 0xFFFF));
    sram_write_visual_word(&offset, (u16)(frame & 0xFFFF));
    sram_write_visual_word(&offset, VDP_getScreenWidth());
    sram_write_visual_word(&offset, VDP_getScreenHeight());
    sram_write_visual_word(&offset, VDP_getPlaneWidth());
    sram_write_visual_word(&offset, VDP_getPlaneHeight());
    sram_write_visual_word(&offset, VDP_getHorizontalScrollingMode());
    sram_write_visual_word(&offset, VDP_getVerticalScrollingMode());
    sram_write_visual_word(&offset, VDP_getBGAAddress());
    sram_write_visual_word(&offset, VDP_getBGBAddress());
    sram_write_visual_word(&offset, VDP_getWindowAddress());
    sram_write_visual_word(&offset, VDP_getSpriteListAddress());
    sram_write_visual_word(&offset, VDP_getHScrollTableAddress());
    sram_write_visual_word(&offset, VDP_getBackgroundColor());
    sram_write_visual_word(&offset, g_mdRuntimeProbe[8]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[9]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[10]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[11]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[13]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[14]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[16]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[17]);
    sram_write_visual_word(&offset, g_mdRuntimeProbe[4]);

    for (i = 0; i < PROBE_VLAB_PALETTE_WORDS; i++) {
        sram_write_visual_word(&offset, s_vlabPalette[i]);
    }

    SRAM_disable();
}

void MDRuntimeProbe_tick(void)
{
    u16 cpuLoad = SYS_getCPULoad();
    u16 sceneId = (u16) gApp.currentScene;
    u16 samplesRecorded = g_mdRuntimeProbe[9];
    u16 maxScanlineSprites;
    s32 jitterDelta = (s32) cpuLoad - (s32) s_prevCpuLoad;
    u16 jitter = (u16) ((jitterDelta < 0) ? -jitterDelta : jitterDelta);

    if (sceneId != s_prevScene) {
        s_prevScene = sceneId;
        reset_scene_metrics(sceneId, cpuLoad);
        samplesRecorded = g_mdRuntimeProbe[9];
        jitter = 0;
    }

    g_mdRuntimeProbe[5] = sceneId;
    g_mdRuntimeProbe[8]++;

    if (s_sceneWarmupFrames > 0) {
        s_sceneWarmupFrames--;
        s_prevCpuLoad = cpuLoad;
        s_hasPrevSample = FALSE;
        return;
    }

    /*
     * Rolling heartbeat: re-assert READY in SRAM at HEARTBEAT_OFFSET every
     * MD_RUNTIME_PROBE_HEARTBEAT_PERIOD frames post-warmup. A single missed
     * flush on the emulator side cannot starve the wrapper's detection loop
     * because the tag will be rewritten on the next period.
     */
    if ((g_mdRuntimeProbe[8] % MD_RUNTIME_PROBE_HEARTBEAT_PERIOD) == 0u) {
        MDRuntimeProbe_writeHeartbeat();
    }

    if (cpuLoad > PROBE_CPU_BUDGET_THRESHOLD) {
        g_mdRuntimeProbe[10]++;
    }
    if (cpuLoad > g_mdRuntimeProbe[11]) {
        g_mdRuntimeProbe[11] = cpuLoad;
    }
    if (s_hasPrevSample && jitter > g_mdRuntimeProbe[13]) {
        g_mdRuntimeProbe[13] = jitter;
    }

    maxScanlineSprites = measure_max_scanline_sprites();
    if (maxScanlineSprites > g_mdRuntimeProbe[14]) {
        g_mdRuntimeProbe[14] = maxScanlineSprites;
    }

    if (g_mdRuntimeProbe[15] < 1) g_mdRuntimeProbe[15] = 1;
    g_mdRuntimeProbe[16] = clamp_u16(SPR_getNumActiveSprite());
    g_mdRuntimeProbe[17] = 1;

    if (samplesRecorded < MD_RUNTIME_PROBE_MAX_SAMPLES) {
        g_mdRuntimeProbe[PROBE_SAMPLE_OFFSET + samplesRecorded] = cpuLoad;
        g_mdRuntimeProbe[9] = samplesRecorded + 1;
    }

    s_prevCpuLoad = cpuLoad;
    s_hasPrevSample = TRUE;

    samplesRecorded = g_mdRuntimeProbe[9];
    if (samplesRecorded > 0 && (samplesRecorded != s_lastExportSamples) && ((gApp.totalFrames - s_lastExportFrame) >= 60u)) {
        MDRuntimeProbe_exportToSRAM();
        export_visual_probe_to_sram();
        s_lastExportSamples = samplesRecorded;
        s_lastExportFrame = gApp.totalFrames;
    }
}

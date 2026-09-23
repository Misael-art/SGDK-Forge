#include <genesis.h>
#include <sprite_eng.h>

#include "input_abstraction.h"
#include "project_config.h"
#include "scene_manager.h"
#include "system/qa_bootstrap.h"
#include "system/runtime_probe.h"

#define PROBE_MAGIC_HI 0x4D44u
#define PROBE_MAGIC_LO 0x5254u
#define PROBE_SCHEMA_VERSION 1u
#define PROBE_SRAM_SCHEMA_VERSION 1u
#define PROBE_TARGET_FPS_NTSC 60u
#define PROBE_TARGET_FPS_PAL 50u
#define PROBE_CPU_BUDGET_THRESHOLD 100u
#define PROBE_SCENE_WARMUP_FRAMES 90u
#define PROBE_SCANLINE_COUNT 224u
#define PROBE_SCANLINE_SAMPLE_GROUPS 4u
#define PROBE_SCANLINE_GROUP_LENGTH \
    (PROBE_SCANLINE_COUNT / PROBE_SCANLINE_SAMPLE_GROUPS)
#define PROBE_VLAB_SCHEMA_VERSION 1u
#define PROBE_VLAB_METRIC_WORDS 24u
#define PROBE_VLAB_PALETTE_WORDS 64u
#define PROBE_VLAB_TOTAL_BYTES \
    (8u + ((PROBE_VLAB_METRIC_WORDS + PROBE_VLAB_PALETTE_WORDS) * 2u))

volatile u16 g_mdRuntimeProbe[MD_RUNTIME_PROBE_WORD_COUNT];

static u16 s_prev_cpu_load;
static bool s_has_prev_sample;
static SceneId s_prev_scene;
static u16 s_scene_warmup_frames;
static u32 s_heartbeat_counter;
static u16 s_scanline_cursor;
static bool s_target_locked;
static SceneId s_capture_target;
static bool s_mdrt_exported;
static bool s_vlab_exported;
static u16 s_vlab_palette[PROBE_VLAB_PALETTE_WORDS];

static void write_u16be(u32 offset, u16 value)
{
    SRAM_writeByte(offset, (u8)((value >> 8) & 0xFFu));
    SRAM_writeByte(offset + 1u, (u8)(value & 0xFFu));
}

static void write_visual_word(u32* offset, u16 value)
{
    write_u16be(*offset, value);
    *offset += 2u;
}

static u16 measure_max_scanline_sprites(void)
{
    Sprite* cursor = firstSprite;
    u16 sample_lines[PROBE_SCANLINE_SAMPLE_GROUPS];
    u8 pressure[PROBE_SCANLINE_SAMPLE_GROUPS] = { 0u, 0u, 0u, 0u };
    u16 sample;
    u16 peak = 0u;

    for (sample = 0u; sample < PROBE_SCANLINE_SAMPLE_GROUPS; sample++)
    {
        sample_lines[sample] =
            s_scanline_cursor + (sample * PROBE_SCANLINE_GROUP_LENGTH);
    }

    while (cursor != NULL)
    {
        if ((cursor->frame != NULL) && (cursor->visibility != HIDDEN))
        {
            u16 index;
            const u16 count = cursor->frame->numSprite & 0x7Fu;

            for (index = 0u; index < count; index++)
            {
                const FrameVDPSprite* vdp_sprite =
                    &cursor->frame->frameVDPSprites[index];
                const s16 start =
                    (cursor->y - 0x80) + (s16)vdp_sprite->offsetY;
                const s16 end =
                    start + (s16)(((vdp_sprite->size & 0x3u) + 1u) << 3);

                for (sample = 0u;
                     sample < PROBE_SCANLINE_SAMPLE_GROUPS;
                     sample++)
                {
                    const u16 scanline = sample_lines[sample];
                    if ((scanline >= start) && (scanline < end))
                    {
                        pressure[sample]++;
                        if (pressure[sample] > peak)
                        {
                            peak = pressure[sample];
                        }
                    }
                }
            }
        }
        cursor = cursor->next;
    }

    s_scanline_cursor++;
    if (s_scanline_cursor >= PROBE_SCANLINE_GROUP_LENGTH)
    {
        s_scanline_cursor = 0u;
    }

    return peak;
}

static void reset_scene_metrics(SceneId scene_id, u16 cpu_load)
{
    u16 index;

    g_mdRuntimeProbe[5] = (u16)scene_id;
    g_mdRuntimeProbe[8] = 0u;
    g_mdRuntimeProbe[9] = 0u;
    g_mdRuntimeProbe[10] = 0u;
    g_mdRuntimeProbe[11] = 0u;
    g_mdRuntimeProbe[13] = 0u;
    g_mdRuntimeProbe[14] = 0u;
    g_mdRuntimeProbe[15] = 0u;
    g_mdRuntimeProbe[16] = 0u;
    g_mdRuntimeProbe[17] = 0u;

    for (index = 0u; index < MD_RUNTIME_PROBE_MAX_SAMPLES; index++)
    {
        g_mdRuntimeProbe[MD_RUNTIME_PROBE_SAMPLE_OFFSET + index] = 0u;
    }

    s_prev_cpu_load = cpu_load;
    s_has_prev_sample = false;
    s_scene_warmup_frames = PROBE_SCENE_WARMUP_FRAMES;
    s_scanline_cursor = 0u;
    s_mdrt_exported = false;
    s_vlab_exported = false;
}

void MDRuntimeProbe_writeHeartbeat(void)
{
    const u32 ready_offset = MD_RUNTIME_PROBE_HEARTBEAT_OFFSET;
    const u32 scene_offset = PROJECT_SCENE_SRAM_OFFSET;
    const u32 input_offset = PROJECT_INPUT_SRAM_OFFSET;
    const SceneId scene_id = SM_getCurrentScene();
    const u16 raw_input = IO_getRawState();
    const u16 observed_input = IO_getObservedState();

    SRAM_enable();
    SRAM_writeByte(ready_offset + 0u, (u8)'R');
    SRAM_writeByte(ready_offset + 1u, (u8)'E');
    SRAM_writeByte(ready_offset + 2u, (u8)'A');
    SRAM_writeByte(ready_offset + 3u, (u8)'D');
    SRAM_writeByte(ready_offset + 4u, (u8)'Y');
    SRAM_writeByte(ready_offset + 5u,
                   (u8)((s_heartbeat_counter >> 16) & 0xFFu));
    SRAM_writeByte(ready_offset + 6u,
                   (u8)((s_heartbeat_counter >> 8) & 0xFFu));
    SRAM_writeByte(ready_offset + 7u,
                   (u8)(s_heartbeat_counter & 0xFFu));

    SRAM_writeByte(scene_offset + 0u, (u8)'S');
    SRAM_writeByte(scene_offset + 1u, (u8)'C');
    SRAM_writeByte(scene_offset + 2u, (u8)'N');
    SRAM_writeByte(scene_offset + 3u, (u8)scene_id);

    SRAM_writeByte(input_offset + 0u, (u8)'I');
    SRAM_writeByte(input_offset + 1u, (u8)'N');
    SRAM_writeByte(input_offset + 2u, (u8)'P');
    SRAM_writeByte(input_offset + 3u, (u8)((raw_input >> 8) & 0xFFu));
    SRAM_writeByte(input_offset + 4u, (u8)(raw_input & 0xFFu));
    SRAM_writeByte(input_offset + 5u,
                   (u8)((observed_input >> 8) & 0xFFu));
    SRAM_writeByte(input_offset + 6u, (u8)(observed_input & 0xFFu));
    SRAM_writeByte(input_offset + 7u, IO_isLocked() ? 1u : 0u);
    SRAM_disable();

    s_heartbeat_counter++;
}

void MDRuntimeProbe_exportToSRAM(void)
{
    const u16 word_count = (u16)MD_RUNTIME_PROBE_WORD_COUNT;
    const u16 total_bytes = (u16)(10u + (word_count * 2u));
    u32 offset = MD_RUNTIME_PROBE_SRAM_OFFSET;
    u16 index;

    SRAM_enable();
    SRAM_writeByte(offset + 0u, (u8)'M');
    SRAM_writeByte(offset + 1u, (u8)'D');
    SRAM_writeByte(offset + 2u, (u8)'R');
    SRAM_writeByte(offset + 3u, (u8)'T');
    write_u16be(offset + 4u, PROBE_SRAM_SCHEMA_VERSION);
    write_u16be(offset + 6u, total_bytes);
    write_u16be(offset + 8u, word_count);

    offset += 10u;
    for (index = 0u; index < word_count; index++)
    {
        write_u16be(offset, g_mdRuntimeProbe[index]);
        offset += 2u;
    }
    SRAM_disable();
}

static void export_visual_probe_to_sram(void)
{
    u32 offset = MD_RUNTIME_PROBE_VLAB_OFFSET;
    u16 index;

    PAL_getColors(0u, s_vlab_palette, PROBE_VLAB_PALETTE_WORDS);

    SRAM_enable();
    SRAM_writeByte(offset + 0u, (u8)'V');
    SRAM_writeByte(offset + 1u, (u8)'L');
    SRAM_writeByte(offset + 2u, (u8)'A');
    SRAM_writeByte(offset + 3u, (u8)'B');
    write_u16be(offset + 4u, PROBE_VLAB_SCHEMA_VERSION);
    write_u16be(offset + 6u, PROBE_VLAB_TOTAL_BYTES);

    offset += 8u;
    write_visual_word(&offset, g_mdRuntimeProbe[5]);
    write_visual_word(&offset, (u16)((g_mdRuntimeProbe[8] >> 16) & 0xFFFFu));
    write_visual_word(&offset, g_mdRuntimeProbe[8]);
    write_visual_word(&offset, VDP_getScreenWidth());
    write_visual_word(&offset, VDP_getScreenHeight());
    write_visual_word(&offset, VDP_getPlaneWidth());
    write_visual_word(&offset, VDP_getPlaneHeight());
    write_visual_word(&offset, VDP_getHorizontalScrollingMode());
    write_visual_word(&offset, VDP_getVerticalScrollingMode());
    write_visual_word(&offset, VDP_getBGAAddress());
    write_visual_word(&offset, VDP_getBGBAddress());
    write_visual_word(&offset, VDP_getWindowAddress());
    write_visual_word(&offset, VDP_getSpriteListAddress());
    write_visual_word(&offset, VDP_getHScrollTableAddress());
    write_visual_word(&offset, VDP_getBackgroundColor());
    write_visual_word(&offset, g_mdRuntimeProbe[8]);
    write_visual_word(&offset, g_mdRuntimeProbe[9]);
    write_visual_word(&offset, g_mdRuntimeProbe[10]);
    write_visual_word(&offset, g_mdRuntimeProbe[11]);
    write_visual_word(&offset, g_mdRuntimeProbe[13]);
    write_visual_word(&offset, g_mdRuntimeProbe[14]);
    write_visual_word(&offset, g_mdRuntimeProbe[16]);
    write_visual_word(&offset, g_mdRuntimeProbe[17]);
    write_visual_word(&offset, g_mdRuntimeProbe[4]);

    for (index = 0u; index < PROBE_VLAB_PALETTE_WORDS; index++)
    {
        write_visual_word(&offset, s_vlab_palette[index]);
    }
    SRAM_disable();
}

void MDRuntimeProbe_init(void)
{
    u16 index;

    for (index = 0u; index < MD_RUNTIME_PROBE_WORD_COUNT; index++)
    {
        g_mdRuntimeProbe[index] = 0u;
    }

    g_mdRuntimeProbe[0] = PROBE_MAGIC_HI;
    g_mdRuntimeProbe[1] = PROBE_MAGIC_LO;
    g_mdRuntimeProbe[2] = PROBE_SCHEMA_VERSION;
    g_mdRuntimeProbe[4] =
        SYS_isPAL() ? PROBE_TARGET_FPS_PAL : PROBE_TARGET_FPS_NTSC;
    g_mdRuntimeProbe[23] = PROBE_CPU_BUDGET_THRESHOLD;

    s_prev_scene = SM_getCurrentScene();
    s_target_locked = QA_bootstrapWasApplied();
    s_capture_target = s_target_locked
        ? QA_bootstrapGetTargetScene()
        : s_prev_scene;
    s_heartbeat_counter = 0u;
    reset_scene_metrics(s_capture_target, SYS_getCPULoad());
    MDRuntimeProbe_writeHeartbeat();
}

bool MDRuntimeProbe_shouldHoldScene(void)
{
    return QA_bootstrapWasApplied() &&
           ((QA_bootstrapGetFlags() & QA_BOOTSTRAP_FLAG_HOLD_SCENE) != 0u) &&
           (SM_getCurrentScene() == QA_bootstrapGetTargetScene()) &&
           (g_mdRuntimeProbe[8] >= QA_bootstrapGetHoldFrame());
}

void MDRuntimeProbe_tick(void)
{
    const u16 cpu_load = SYS_getCPULoad();
    const SceneId scene_id = SM_getCurrentScene();
    u16 samples_recorded = g_mdRuntimeProbe[9];
    const s32 jitter_delta =
        (s32)cpu_load - (s32)s_prev_cpu_load;
    const u16 jitter =
        (u16)((jitter_delta < 0) ? -jitter_delta : jitter_delta);
    u16 used_vdp_sprites;
    u16 scanline_sprites;

    if (!s_target_locked && (scene_id != s_prev_scene))
    {
        s_prev_scene = scene_id;
        s_capture_target = scene_id;
        reset_scene_metrics(scene_id, cpu_load);
        samples_recorded = 0u;
    }

    g_mdRuntimeProbe[5] = (u16)s_capture_target;
    g_mdRuntimeProbe[8]++;

    if ((g_mdRuntimeProbe[8] % MD_RUNTIME_PROBE_HEARTBEAT_PERIOD) == 0u)
    {
        MDRuntimeProbe_writeHeartbeat();
    }

    if (s_scene_warmup_frames > 0u)
    {
        s_scene_warmup_frames--;
        s_prev_cpu_load = cpu_load;
        s_has_prev_sample = false;
        return;
    }

    if (cpu_load > PROBE_CPU_BUDGET_THRESHOLD)
    {
        g_mdRuntimeProbe[10]++;
    }
    if (cpu_load > g_mdRuntimeProbe[11])
    {
        g_mdRuntimeProbe[11] = cpu_load;
    }
    if (s_has_prev_sample && (jitter > g_mdRuntimeProbe[13]))
    {
        g_mdRuntimeProbe[13] = jitter;
    }

    scanline_sprites = measure_max_scanline_sprites();
    if (scanline_sprites > g_mdRuntimeProbe[14])
    {
        g_mdRuntimeProbe[14] = scanline_sprites;
    }

    used_vdp_sprites = SPR_getUsedVDPSprite();
    if (used_vdp_sprites > g_mdRuntimeProbe[16])
    {
        g_mdRuntimeProbe[16] = used_vdp_sprites;
    }
    g_mdRuntimeProbe[17] = SPR_getNumActiveSprite();

    if (samples_recorded < MD_RUNTIME_PROBE_MAX_SAMPLES)
    {
        g_mdRuntimeProbe[MD_RUNTIME_PROBE_SAMPLE_OFFSET +
                         samples_recorded] = cpu_load;
        samples_recorded++;
        g_mdRuntimeProbe[9] = samples_recorded;
    }

    if (!s_vlab_exported &&
        (samples_recorded >= (MD_RUNTIME_PROBE_MAX_SAMPLES / 2u)))
    {
        export_visual_probe_to_sram();
        s_vlab_exported = true;
    }

    if (!s_mdrt_exported &&
        (samples_recorded >= MD_RUNTIME_PROBE_MAX_SAMPLES))
    {
        MDRuntimeProbe_exportToSRAM();
        s_mdrt_exported = true;
    }

    s_prev_cpu_load = cpu_load;
    s_has_prev_sample = true;
}
